---
title: php_fastcgi (Caddyfile directive)
---

<script>
ready(function() {
	// Wir fügen Links zu allen Unterdirektiven hinzu, wenn ein passender Anker auf der Seite gefunden wird.
	addLinksToSubdirectives();
});
</script>

# php_fastcgi

Eine meinungsstarke Direktive, die Anfragen an einen PHP-FastCGI-Server wie php-fpm weiterleitet.

- [Syntax](#syntax)
- [Erweiterte Form](#expanded-form)
  - [Erklärung](#explanation)
- [Beispiele](#examples)

Caddys [`reverse_proxy`](reverse_proxy) kann jede FastCGI-Anwendung bedienen, diese Direktive ist jedoch speziell auf PHP-Apps zugeschnitten. Sie ist eine praktische Abkürzung, die eine [längere Konfiguration](#expanded-form) ersetzt.

Sie erwartet, dass jedes `index.php` im Site-Root als Router dient. Wenn das nicht gewünscht ist, konfigurieren Sie entweder die Unterdirektive [`try_files`](#try_files) neu, um das Standard-Rewrite-Verhalten zu ändern, oder verwenden Sie die [erweiterte Form](#expanded-form) als Grundlage und passen Sie sie an Ihre Anforderungen an.

Zusätzlich zu den unten aufgeführten Unterdirektiven unterstützt diese Direktive auch alle Unterdirektiven von [`reverse_proxy`](reverse_proxy#syntax). Sie können zum Beispiel Load Balancing und Health Checks aktivieren.

**Die meisten modernen PHP-Apps funktionieren ohne zusätzliche Unterdirektiven oder Anpassungen.** Unterdirektiven werden üblicherweise nur in bestimmten Randfällen oder mit alten PHP-Apps verwendet.

<a id="syntax"></a>
## Syntax

```caddy-d
php_fastcgi [<matcher>] <php-fpm_gateways...> {
	root <path>
	split <substrings...>
	index <filename>|off
	try_files <files...>
	env [<key> <value>]
	resolve_root_symlink
	capture_stderr
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>

	<any other reverse_proxy subdirectives...>
}
```

- **<php-fpm_gateways...>** sind die [Adressen](/docs/conventions#network-addresses) der FastCGI-Server. Typischerweise ist das entweder ein TCP-Socket oder eine Unix-Socket-Datei.

- **root** <span id="root"/> setzt den Root-Ordner der Site. Es wird empfohlen, immer die [`root`-Direktive](root) zusammen mit `php_fastcgi` zu verwenden. Diese Einstellung zu überschreiben kann aber nützlich sein, wenn Ihr PHP-FPM-Upstream ein anderes Root als Caddy verwendet (siehe [Beispiel](#docker)). Standard ist der Wert der [`root`-Direktive](root), falls verwendet, andernfalls Caddys aktuelles Arbeitsverzeichnis.

- **split** <span id="split"/> setzt die Teilstrings, mit denen die URI in zwei Teile getrennt wird. Der erste passende Teilstring wird verwendet, um die "path info" vom Pfad zu trennen. Das erste Stück erhält den passenden Teilstring als Suffix und wird als tatsächlicher Ressourcenname (CGI-Skript) angenommen. Das zweite Stück wird für das CGI-Skript als PATH_INFO gesetzt. Standard: `.php`

- **index** <span id="index"/> gibt den Dateinamen an, der als Directory-Index-Datei behandelt wird. Dies beeinflusst den File Matcher in der [erweiterten Form](#expanded-form). Standard: `index.php`. Kann auf `off` gesetzt werden, um den Rewrite-Fallback auf `index.php` zu deaktivieren, wenn keine passende Datei gefunden wird.

- **try_files** <span id="try_files"/> gibt einen Override für den standardmäßigen try-files-Rewrite an. Details finden Sie bei der Direktive [`try_files`](try_files). Standard: `{path} {path}/index.php index.php`.

- **env** <span id="env"/> setzt eine zusätzliche Umgebungsvariable auf den angegebenen Wert. Kann mehrfach für mehrere Umgebungsvariablen angegeben werden. Standardmäßig sind alle relevanten FastCGI-Umgebungsvariablen bereits gesetzt (einschließlich HTTP-Headern), aber Sie können Variablen nach Bedarf hinzufügen oder überschreiben.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> löst das Verzeichnis [`root`](#root) auf seinen tatsächlichen Wert auf, wenn es ein symbolischer Link (Symlink) ist. Das wird manchmal als Deployment-Strategie verwendet, indem einfach der Symlink auf eine neue Version in einem anderen Verzeichnis umgestellt wird. Standardmäßig deaktiviert, um wiederholte Systemaufrufe zu vermeiden.

- **capture_stderr** <span id="capture_stderr"/> aktiviert das Erfassen und Loggen aller Nachrichten, die der Upstream-FastCGI-Server auf `stderr` sendet. Standardmäßig wird auf Level `WARN` geloggt. Wenn die Antwort einen Status `4xx` oder `5xx` hat, wird stattdessen Level `ERROR` verwendet. Standardmäßig wird `stderr` ignoriert.

- **dial_timeout** <span id="dial_timeout"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie lange beim Verbinden mit dem Upstream-Socket gewartet wird. Standard: `3s`.

- **read_timeout** <span id="read_timeout"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie lange beim Lesen vom FastCGI-Upstream gewartet wird. Standard: kein Timeout.

- **write_timeout** <span id="write_timeout"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie lange beim Senden an den FastCGI-Upstream gewartet wird. Standard: kein Timeout.


Da diese Direktive ein meinungsstarker Wrapper über einen Reverse Proxy ist, können Sie jede Unterdirektive von [`reverse_proxy`](reverse_proxy#syntax) verwenden, um sie anzupassen.


<a id="expanded-form"></a>
## Erweiterte Form

Die Direktive `php_fastcgi` (ohne Unterdirektiven) entspricht der folgenden Konfiguration. Die meisten modernen PHP-Apps funktionieren gut mit dieser Voreinstellung. Wenn Ihre App das nicht tut, können Sie diese Konfiguration übernehmen und nach Bedarf anpassen, statt die Abkürzung `php_fastcgi` zu verwenden.

```caddy-d
route {
	# Abschließenden Slash für Verzeichnisanfragen hinzufügen
	# Diese Weiterleitung wird automatisch deaktiviert, wenn "{http.request.uri.path}/index.php"
	# nicht in der try_files-Liste vorkommt
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# Wenn die angeforderte Datei nicht existiert, Indexdateien versuchen und annehmen, dass index.php immer existiert
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# PHP-Dateien an den FastCGI-Responder weiterleiten
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```

<a id="explanation"></a>
### Erklärung

- Der erste Abschnitt kümmert sich um die Kanonisierung des Anfragepfads. Ziel ist sicherzustellen, dass Anfragen, die auf ein Verzeichnis auf der Festplatte zielen, tatsächlich den abschließenden Slash `/` im Anfragepfad haben, sodass nur eine einzige URL für Anfragen an dieses Verzeichnis gültig ist.

  Diese Kanonisierung erfolgt nur, wenn die Unterdirektive `try_files` `{path}/index.php` enthält (der Standard).

  Dies wird durch einen Request Matcher umgesetzt, der nur auf Anfragen passt, die *nicht* mit einem Slash enden und auf ein Verzeichnis auf der Festplatte abbilden, das eine Datei `index.php` enthält. Wenn er passt, wird ein HTTP-308-Redirect mit angehängtem Slash ausgeführt. Beispielsweise würde eine Anfrage mit Pfad `/foo` nach `/foo/` umgeleitet (Anhängen von `/`, um den Pfad zum Verzeichnis zu kanonisieren), wenn `/foo/index.php` auf der Festplatte existiert.

- Der nächste Abschnitt behandelt Pfad-Rewrites abhängig davon, ob eine passende Datei auf der Festplatte existiert. Außerdem merkt er sich den Teil des Pfads nach `.php` (wenn der Anfragepfad `.php` enthält). Das ist wichtig, damit Caddy die FastCGI-Umgebungsvariablen korrekt setzen kann.

  - Zuerst wird geprüft, ob `{path}` eine Datei ist, die auf der Festplatte existiert. Wenn ja, wird auf diesen Pfad umgeschrieben. Das bricht den Rest im Wesentlichen kurz ab und stellt sicher, dass Anfragen an Dateien, die auf der Festplatte *existieren*, nicht anderweitig umgeschrieben werden (siehe nächste Schritte unten). Wenn Sie also beispielsweise eine Datei `/js/app.js` auf der Festplatte haben, bleibt die Anfrage an diesen Pfad unverändert.

  - Zweitens wird geprüft, ob `{path}/index.php` eine Datei ist, die auf der Festplatte existiert. Wenn ja, wird auf diesen Pfad umgeschrieben. Bei Anfragen an ein Verzeichnis wie `/foo/` wird dann nach `/foo//index.php` gesucht (was zu `/foo/index.php` normalisiert wird), und die Anfrage wird auf diesen Pfad umgeschrieben, wenn er existiert. Dieses Verhalten ist manchmal nützlich, wenn Sie eine weitere PHP-App in einem Unterverzeichnis Ihres Webroots ausführen.

  - Zuletzt wird immer auf `index.php` umgeschrieben (bei modernen PHP-Apps existiert es fast immer). Dadurch kann Ihre PHP-App jede Anfrage für Pfade verarbeiten, die *nicht* auf Dateien auf der Festplatte abbilden, indem sie das Skript `index.php` als Entrypoint verwendet.

- Und schließlich ist der letzte Abschnitt derjenige, der die Anfrage tatsächlich an Ihren PHP-FastCGI- (oder PHP-FPM-)Dienst weiterleitet, damit Ihr PHP-Code ausgeführt wird. Der Request Matcher passt nur auf Anfragen, die auf `.php` enden. Jede Datei, die *kein* PHP-Skript ist und auf der Festplatte *existiert*, wird daher *nicht* von dieser Direktive behandelt und fällt durch.

Die Direktive `php_fastcgi` reicht für sich genommen normalerweise nicht aus. Sie sollte fast immer mit der [`root`-Direktive](root) kombiniert werden, um den Speicherort Ihrer Dateien auf der Festplatte festzulegen (bei modernen PHP-Apps kann dies `/var/www/html/public` sein, wobei das Verzeichnis `public` Ihre `index.php` enthält), sowie mit der [`file_server`-Direktive](file_server), um Ihre statischen Dateien (JS, CSS, Bilder usw.) auszuliefern, die nicht anderweitig von dieser Direktive behandelt werden und durchgefallen sind.



<a id="examples"></a>
## Beispiele

Alle PHP-Anfragen an einen FastCGI-Responder weiterleiten, der auf `127.0.0.1:9000` lauscht:

```caddy-d
php_fastcgi 127.0.0.1:9000
```

Dasselbe, aber nur für Anfragen unter `/blog/`:

```caddy-d
php_fastcgi /blog/* localhost:9000
```

Bei PHP-FPM, das über einen Unix-Socket lauscht:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

Die [`root`-Direktive](root) wird fast immer verwendet, um das Verzeichnis mit den PHP-Skripten anzugeben, und die [`file_server`-Direktive](file_server), um statische Dateien auszuliefern:

```caddy
example.com {
	root /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<span id="docker"/> Wenn mehrere PHP-Apps mit Caddy ausgeliefert werden, muss der Webroot für jede App unterschiedlich sein, damit Caddy Ihre statischen Dateien getrennt lesen und ausliefern und erkennen kann, ob PHP-Dateien existieren.

Wenn Sie Docker verwenden, haben Ihre PHP-FPM-Container die Dateien oft unter demselben Root gemountet. In diesem Fall besteht die Lösung darin, die Dateien in Ihrem Caddy-Container in unterschiedliche Verzeichnisse zu mounten und dann die Unterdirektive [`root`](#root) zu verwenden, um das Root für jeden Container zu setzen:

```caddy
app1.example.com {
	root /srv/app1/public
	php_fastcgi app1:9000 {
		root /var/www/html/public
	}
	file_server
}

app2.example.com {
	root /srv/app2/public
	php_fastcgi app2:9000 {
		root /var/www/html/public
	}
	file_server
}
```

Für eine PHP-Site, die `index.php` nicht als Entrypoint verwendet, können Sie stattdessen auf das Ausgeben eines `404`-Fehlers zurückfallen. Der Fehler kann mit der [`handle_errors`-Direktive](handle_errors) abgefangen und behandelt werden:

```caddy
example.com {
	php_fastcgi localhost:9000 {
		try_files {path} {path}/index.php =404
	}

	handle_errors {
		respond "{err.status_code} {err.status_text}"
	}
}
```
