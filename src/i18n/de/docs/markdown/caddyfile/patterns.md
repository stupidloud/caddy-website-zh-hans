---
title: Gängige Caddyfile-Muster
---

<a id="common-caddyfile-patterns"></a>
# Gängige Caddyfile-Muster

Diese Seite zeigt einige vollständige und minimale Caddyfile-Konfigurationen für gängige Anwendungsfälle. Sie können hilfreiche Ausgangspunkte für Ihre eigenen Caddyfile-Dokumente sein.

Dies sind keine fertigen Drop-in-Lösungen; Sie müssen Domainnamen, Ports/Sockets, Verzeichnispfade usw. anpassen. Sie sollen einige der häufigsten Konfigurationsmuster veranschaulichen.

- [Statischer Dateiserver](#static-file-server)
- [Reverse Proxy](#reverse-proxy)
- [PHP](#php)
- [`www.`-Subdomain umleiten](#redirect-www-subdomain)
- [Abschließende Slashes](#trailing-slashes)
- [Wildcard-Zertifikate](#wildcard-certificates)
- [Single-page apps (SPAs)](#single-page-apps-spas)
- [Caddy proxyt zu einem anderen Caddy](#caddy-proxying-to-another-caddy)


<a id="static-file-server"></a>
## Statischer Dateiserver

```caddy
example.com {
	root /var/www
	file_server
}
```

Wie üblich ist die erste Zeile die Site-Adresse. Die [`root`-Direktive](/docs/caddyfile/directives/root) gibt den Pfad zum Root der Site an (das `*` bedeutet, dass alle Requests gematcht werden, um es von einem [Path-Matcher](/docs/caddyfile/matchers#path-matchers) zu unterscheiden)&mdash;ändern Sie den Pfad zu Ihrer Site, falls es nicht das aktuelle Arbeitsverzeichnis ist. Schließlich aktivieren wir den [statischen Dateiserver](/docs/caddyfile/directives/file_server).



<a id="reverse-proxy"></a>
## Reverse Proxy

Alle Requests proxien:

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

Nur Requests proxien, deren Pfad mit `/api/` beginnt, und für alles andere statische Dateien ausliefern:

```caddy
example.com {
	root /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

Dies verwendet einen [Request-Matcher](/docs/caddyfile/matchers#syntax), um nur Requests zu matchen, die mit `/api/` beginnen, und sie an das Backend zu proxien. Alle anderen Requests werden vom Site-[`root`](/docs/caddyfile/directives/root) mit dem [statischen Dateiserver](/docs/caddyfile/directives/file_server) ausgeliefert. Das hängt außerdem davon ab, dass `reverse_proxy` in der [Direktivenreihenfolge](/docs/caddyfile/directives#directive-order) höher steht als `file_server`.

Es gibt [hier viele weitere `reverse_proxy`-Beispiele](/docs/caddyfile/directives/reverse_proxy#examples).



## PHP

### PHP-FPM

Wenn ein PHP-FastCGI-Dienst läuft, funktioniert für die meisten modernen PHP-Apps ungefähr Folgendes:

```caddy
example.com {
	root /srv/public
	encode
	php_fastcgi localhost:9000
	file_server
}
```

Passen Sie den Site-Root entsprechend an; dieses Beispiel nimmt an, dass der Webroot Ihrer PHP-App in einem Verzeichnis `public` liegt&mdash;Requests für Dateien, die auf der Festplatte existieren, werden mit [`file_server`](/docs/caddyfile/directives/file_server) ausgeliefert, und alles andere wird zur Verarbeitung durch die PHP-App an `index.php` geroutet.

Manchmal können Sie einen Unix-Socket verwenden, um sich mit PHP-FPM zu verbinden:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

Die Direktive [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi) ist tatsächlich nur eine Kurzform für [mehrere Konfigurationsstücke](/docs/caddyfile/directives/php_fastcgi#expanded-form).


### FrankenPHP

Alternativ können Sie [FrankenPHP](https://frankenphp.dev/) verwenden, eine Caddy-Distribution, die PHP direkt über CGO (Go-to-C-Bindings) aufruft. Das kann bis zu 4x schneller sein als mit PHP-FPM und noch besser, wenn Sie den Worker-Modus verwenden können.

```caddy
{
    frankenphp
    order php_server before file_server
}

example.com {
	root /srv/public
    encode zstd br gzip
    php_server
}
```


<a id="redirect-www-subdomain"></a>
## `www.`-Subdomain umleiten

Um die `www.`-Subdomain per HTTP-Redirect **hinzuzufügen**:

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


Um sie **zu entfernen**:

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


Um sie für **mehrere Domains** auf einmal zu entfernen; dies verwendet die Platzhalter `{labels.*}`, die die Teile des Hostnamens sind, `0`-indiziert von rechts (z. B. `0`=`com`, `1`=`example-one`, `2`=`www`):

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```



<a id="trailing-slashes"></a>
## Abschließende Slashes

Normalerweise müssen Sie dies nicht selbst konfigurieren; die Direktive [`file_server`](/docs/caddyfile/directives/file_server) fügt abschließende Slashes automatisch per HTTP-Redirect hinzu oder entfernt sie, je nachdem, ob die angeforderte Ressource ein Verzeichnis beziehungsweise eine Datei ist.

Falls nötig, können Sie abschließende Slashes dennoch mit Ihrer Konfiguration erzwingen. Es gibt zwei Wege: intern oder extern.

<a id="internal-enforcement"></a>
### Interne Erzwingung

Dies verwendet die Direktive [`rewrite`](/docs/caddyfile/directives/rewrite). Caddy schreibt die URI intern um, um den abschließenden Slash hinzuzufügen oder zu entfernen:

```caddy
example.com {
	rewrite /add     /add/
	rewrite /remove/ /remove
}
```

Mit einem Rewrite sind Requests mit und ohne abschließenden Slash gleich.


<a id="external-enforcement"></a>
### Externe Erzwingung

Dies verwendet die Direktive [`redir`](/docs/caddyfile/directives/redir). Caddy fordert den Browser auf, die URI zu ändern, um den abschließenden Slash hinzuzufügen oder zu entfernen:

```caddy
example.com {
	redir /add     /add/
	redir /remove/ /remove
}
```

Mit einem Redirect muss der Client den Request erneut senden; dadurch wird eine einzelne akzeptable URI für eine Ressource erzwungen.



<a id="wildcard-certificates"></a>
## Wildcard-Zertifikate

Für die meisten Issuer einschließlich Let's Encrypt müssen Sie die [ACME DNS Challenge](/docs/automatic-https#dns-challenge) aktivieren, damit Caddy Wildcard-Zertifikate automatisieren kann.

Mit aktivierter DNS Challenge bevorzugt Caddy ab Caddy 2.10 ein anwendbares Wildcard-Zertifikat, das bereits konfiguriert oder verwaltet wird, bevor ein separates Zertifikat für eine Subdomain verwaltet wird.



Wenn Sie mehrere Subdomains mit demselben Wildcard-Zertifikat ausliefern müssen, ist ein Caddyfile wie dieses die beste Art, sie zu behandeln. Es nutzt die Direktive [`handle`](/docs/caddyfile/directives/handle) und [`host`-Matcher](/docs/caddyfile/matchers#host):

```caddy
*.example.com {
	tls {
		dns <provider_name> [<params...>]
	}

	@foo host foo.example.com
	handle @foo {
		respond "Foo!"
	}

	@bar host bar.example.com
	handle @bar {
		respond "Bar!"
	}

	# Fallback für anderweitig nicht behandelte Domains
	handle {
		abort
	}
}
```

Sie müssen die [ACME DNS Challenge](/docs/automatic-https#dns-challenge) aktivieren, damit Caddy Wildcard-Zertifikate automatisch verwalten kann.



<a id="single-page-apps-spas"></a>
## Single-page apps (SPAs)

Wenn eine Webseite ihr eigenes Routing übernimmt, können Server viele Requests für Seiten erhalten, die serverseitig nicht existieren, clientseitig aber renderbar sind, solange stattdessen die einzelne Indexdatei ausgeliefert wird. So aufgebaute Webanwendungen heißen SPAs oder single-page apps.

Die Grundidee ist, dass der Server "try files" ausführt, um zu prüfen, ob die angeforderte Datei serverseitig existiert, und andernfalls auf eine Indexdatei zurückfällt, in der der Client das Routing übernimmt (normalerweise mit clientseitigem JavaScript).

Eine typische SPA-Konfiguration sieht meist ungefähr so aus:

```caddy
example.com {
	root /srv
	encode
	try_files {path} /index.html
	file_server
}
```

Wenn Ihre SPA mit einer API oder anderen ausschließlich serverseitigen Endpunkten gekoppelt ist, sollten Sie `handle`-Blöcke verwenden, um sie exklusiv zu behandeln:

```caddy
example.com {
	encode

	handle /api/* {
		reverse_proxy backend:8000
	}

	handle {
		root /srv
		try_files {path} /index.html
		file_server
	}
}
```

Wenn Ihre `index.html` Verweise auf JS-/CSS-Assets mit gehashten Dateinamen enthält, sollten Sie erwägen, einen `Cache-Control`-Header hinzuzufügen, um Clients anzuweisen, sie *nicht* zu cachen (damit Browser neue Assets abrufen, wenn sich die Assets ändern). Da der `try_files`-Rewrite verwendet wird, um Ihre `index.html` von jedem Pfad auszuliefern, der keiner anderen Datei auf der Festplatte entspricht, können Sie `try_files` mit einer `route` umschließen, sodass der `header`-Handler *nach* dem Rewrite läuft (normalerweise würde er wegen der [Direktivenreihenfolge](/docs/caddyfile/directives#directive-order) vorher laufen):

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```


<a id="caddy-proxying-to-another-caddy"></a>
## Caddy proxyt zu einem anderen Caddy

Wenn Sie eine öffentlich erreichbare Caddy-Instanz haben (nennen wir sie "front") und eine andere Caddy-Instanz in Ihrem privaten Netzwerk (nennen wir sie "back"), die Ihre eigentliche App ausliefert, können Sie die Direktive [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) verwenden, um Requests durchzureichen.

Front-Instanz:

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

Back-Instanz:

```caddy
{
	servers {
		trusted_proxies static private_ranges
	}
}

http://foo.example.com {
	reverse_proxy foo-app:8080
}

http://bar.example.com {
	reverse_proxy bar-app:9000
}
```

- Dieses Beispiel bedient zwei verschiedene Domains und proxyt beide zu derselben Back-Caddy-Instanz auf Port `80`. Ihre Back-Instanz bedient die zwei Domains unterschiedlich, deshalb ist sie mit zwei separaten Site-Blöcken konfiguriert.

- Auf der Back-Instanz wird [`http://`](/docs/caddyfile/concepts#addresses) verwendet, um HTTP auf Port `80` zu akzeptieren. Die Front-Instanz terminiert TLS, und der Traffic zwischen Front und Back läuft über ein privates Netzwerk, daher muss er nicht erneut verschlüsselt werden.

- Sie können auf der Back-Instanz einen anderen Port wie `8080` verwenden, falls nötig; hängen Sie einfach `:8080` an jede Site-Adresse in der Back-Konfiguration an ODER setzen Sie die globale Option [`http_port`](/docs/caddyfile/options#http_port) auf `8080`.

- Auf der Back-Instanz wird die globale Option [`trusted_proxies`](/docs/caddyfile/options#trusted_proxies) verwendet, um Caddy mitzuteilen, dass es der Front-Instanz als Proxy vertrauen soll. Dadurch bleibt die echte Client-IP erhalten.

- Weiterführend könnten Sie mehr als eine Back-Instanz haben und zwischen ihnen [Load Balancing](/docs/caddyfile/directives/reverse_proxy#load-balancing) durchführen. Sie könnten mTLS (mutual TLS) mit dem [`acme_server`](/docs/caddyfile/directives/acme_server) auf der Front-Instanz einrichten, sodass diese wie die CA für die Back-Instanz agiert (nützlich, wenn der Traffic zwischen Front und Back über nicht vertrauenswürdige Netzwerke läuft).
