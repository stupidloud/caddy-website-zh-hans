---
title: Globale Optionen (Caddyfile)
---

<script>
ready(function() {
	// Wir fügen Links auf die Optionen im Codeblock oben hinzu,
	// die auf die zugehörigen Anker verweisen.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Kommentare mit ihren jeweiligen Abschnitten verlinken
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // führender Leerraum
			text = text.slice(text.indexOf('#')); // nur der Kommentarteil
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Einen doppelten Link gezielt korrigieren; 'name' erscheint zweimal als Link
	// für zwei verschiedene Abschnitte, deshalb ändern wir den zweiten zu #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// `renewal_window_ratio` gezielt korrigieren, da es zweimal als Link für zwei verschiedene Abschnitte erscheint; deshalb ändern wir den zweiten zu #renewal_window_ratio-1
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>


<a id="global-options"></a>
# Globale Optionen

Das Caddyfile bietet eine Möglichkeit, Optionen anzugeben, die global gelten. Einige Optionen dienen als Standardwerte, andere passen HTTP-Server an und gelten nicht nur für eine bestimmte Site; wieder andere passen das Verhalten des Caddyfile-[Adapters](/docs/config-adapters) an.

Ganz oben in deinem Caddyfile kann ein **globaler Optionsblock** stehen. Das ist ein Block ohne Schlüssel:

```caddy
{
	...
}
```

Es kann höchstens einen geben, und er muss der erste Block des Caddyfile sein.

Mögliche Optionen sind (klicke auf eine Option, um zu ihrer Dokumentation zu springen):

```caddy
{
	# Allgemeine Optionen
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hosts...>
	order <dir1> first|last|[before|after <dir2>]
	storage <module_name> {
		<options...>
	}
	storage_clean_interval <duration>
	admin   off|<addr> {
		origins <origins...>
		enforce_origin
	}
	persist_config off
	log [name] {
		output  <writer_module> ...
		format  <encoder_module> ...
		level   <level>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <duration>
	shutdown_delay <duration>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# TLS-Optionen
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <yours>
	default_sni <name>
	fallback_sni <name>
	local_certs
	skip_install_trust
	acme_ca <directory_url>
	acme_ca_root <pem_file>
	acme_eab {
		key_id <key_id>
		mac_key <mac_key>
	}
	acme_dns <provider> ...
	dns <provider> ...
	ech <public_names...> {
		dns <provider> ...
	}
	on_demand_tls {
		ask        <endpoint>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <name> ...
	renew_interval <duration>
	cert_lifetime  <duration>
	ocsp_interval  <duration>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# Server-Optionen
	servers [<listener_address>] {
		name <name>
		listener_wrappers {
			<listener_wrappers...>
		}
		timeouts {
			read_body   <duration>
			read_header <duration>
			write       <duration>
			idle        <duration>
		}
		keepalive_interval <duration>
		keepalive_idle     <duration>
		keepalive_count	   <number>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <headers...>

		trace
		max_header_size <size>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# Dateisysteme
	filesystem <name> <module> {
		<options...>
	}

	# PKI-Optionen
	pki {
		ca [<id>] {
			name                  <name>
			root_cn               <name>
			intermediate_cn       <name>
			intermediate_lifetime <duration>
			maintenance_interval  <duration>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <path>
				key    <path>
			}
			intermediate {
				format <format>
				cert   <path>
				key    <path>
			}
		}
	}

	# Event-Optionen
	events {
		on <event> <handler...>
	}
}
```


<a id="general-options"></a>
## Allgemeine Optionen

##### `debug`
Aktiviert den Debug-Modus, der das Log-Level für den [Standard-Logger](#log) auf `DEBUG` setzt. Dadurch werden mehr Details sichtbar, die bei der Fehlersuche nützlich sein können (und in Produktion sehr ausführlich sind). Wir bitten dich, dies zu aktivieren, bevor du in den [Community-Foren](https://caddy.community) um Hilfe bittest. Zum Beispiel oben in deinem Caddyfile, wenn du keine anderen globalen Optionen hast:

```caddy
{
	debug
}
```


##### `http_port`
Der Port, den der Server für HTTP verwenden soll.

**Nur für interne Verwendung**; ändert den HTTP-Port für Clients nicht. Dies wird typischerweise verwendet, wenn du innerhalb deines internen Netzwerks Port `80` aus Routing-Gründen an einen anderen Port (z. B. `8080`) weiterleiten musst, bevor die Anfrage Caddy erreicht.

Standard: `80`


##### `https_port`
Der Port, den der Server für HTTPS verwenden soll.

**Nur für interne Verwendung**; ändert den HTTPS-Port für Clients nicht. Dies wird typischerweise verwendet, wenn du innerhalb deines internen Netzwerks Port `443` aus Routing-Gründen an einen anderen Port (z. B. `8443`) weiterleiten musst, bevor die Anfrage Caddy erreicht.

Standard: `443`


##### `default_bind`
Die standardmäßige(n) Bind-Adresse(n), die für alle Sites verwendet werden, wenn die [`bind`-Direktive](/docs/caddyfile/directives/bind) in der Site nicht verwendet wird. Standard: leer, wodurch an alle Schnittstellen gebunden wird.

<aside class="tip">

Beachte, dass dies nur für Server gilt, die vom Caddyfile erzeugt werden. Das bedeutet, dass der von [Automatic HTTPS](/docs/automatic-https) für HTTP-zu-HTTPS-Weiterleitungen erstellte HTTP-Server diese Bind-Adressen nicht erbt. Um das zu umgehen, deklariere eine `http://`-Site (sie kann leer sein, ohne Direktiven), damit sie beim Adaptieren des Caddyfile existiert und die Bind-Adressen erhält.

</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



##### `order`
Weist HTTP-handler-Direktiven eine Reihenfolge zu. Da HTTP-Handler in einer sequenziellen Kette ausgeführt werden, müssen sie in der richtigen Reihenfolge laufen. Standarddirektiven haben eine [vordefinierte Reihenfolge](/docs/caddyfile/directives#directive-order), aber bei HTTP-handler-Modulen von Drittanbietern musst du die Reihenfolge explizit festlegen, entweder mit dieser Option oder indem du die Direktive in einen [`route`-Block](/docs/caddyfile/directives/route) setzt. Die Reihenfolge kann absolut (`first` oder `last`) oder relativ (`before` oder `after`) zu einer anderen Direktive beschrieben werden.

Wenn du zum Beispiel das Plugin [`replace-response`](https://github.com/caddyserver/replace-response) verwendest, solltest du sicherstellen, dass seine Direktive nach `encode` einsortiert wird, damit es Ersetzungen durchführen kann, bevor die Antwort codiert wird (denn Antworten laufen in der Handler-Kette nach oben, nicht nach unten):

```caddy
{
	order replace after encode
}
```


##### `storage`
Konfiguriert Caddys Storage-Mechanismus. Standard ist [`file_system`](/docs/json/storage/file_system/). Es gibt viele weitere verfügbare [Storage-Module](/docs/json/storage/), die als Plugins bereitgestellt werden.

Zum Beispiel, um den Speicherort des Dateisystems zu ändern:

```caddy
{
	storage file_system /path/to/custom/location
}
```

Das Anpassen des Storage-Moduls ist typischerweise nötig, wenn Caddys Storage über mehrere Caddy-Instanzen hinweg synchronisiert wird, damit alle dieselben Zertifikate und Schlüssel verwenden. Weitere Details findest du im Abschnitt [Automatic HTTPS zu Storage](/docs/automatic-https#storage).


##### `storage_clean_interval`
Wie oft Storage-Einheiten nach alten oder abgelaufenen Assets durchsucht und diese entfernt werden. Diese Scans verursachen viele Lesezugriffe (und Listenoperationen) auf dem Storage-Modul; wähle für große Deployments daher ein längeres Intervall. Akzeptiert [Dauerwerte](/docs/conventions#durations).

Beim ersten Start des Prozesses wird Storage immer bereinigt. Danach wird eine neue Bereinigung diese Dauer nach Beginn der vorherigen Bereinigung gestartet, wenn die vorherige Bereinigung in weniger als der Hälfte dieses Intervalls abgeschlossen wurde (andernfalls wird der nächste Start übersprungen).

Standard: `24h`

```caddy
{
	storage_clean_interval 7d
}
```




##### `admin`
Passt den [Admin-API-Endpunkt](/docs/api) an. Akzeptiert Platzhalter. Verwendet [Netzwerkadressen](/docs/conventions#network-addresses).

Standard: `localhost:2019`, sofern die Umgebungsvariable `CADDY_ADMIN` nicht gesetzt ist.

Wenn auf `off` gesetzt, wird der Admin-Endpunkt deaktiviert. Wenn er deaktiviert ist, sind **Konfigurationsänderungen unmöglich**, ohne den Server zu stoppen und neu zu starten, da der Befehl [`caddy reload`](/docs/command-line#caddy-reload) die Admin-API verwendet, um die neue Konfiguration an den laufenden Server zu übertragen.

Denk daran, bei kompatiblen [Befehlen](/docs/command-line) das CLI-Flag `--address` zu verwenden, um den aktuellen Admin-Endpunkt anzugeben, wenn die Adresse des laufenden Servers vom Standard abweicht.

Unterstützt außerdem diese Unteroptionen:

- **origins** konfiguriert die Liste der [Origins](https://developer.mozilla.org/en-US/docs/Glossary/Origin), die sich mit dem Endpunkt verbinden dürfen.

  Ein Standard wird intelligent gewählt:
  - Wenn die Listen-Adresse loopback ist (z. B. `localhost`, eine Loopback-IP oder ein Unix-Socket), dann sind die erlaubten Origins `localhost`, `::1` und `127.0.0.1`, jeweils mit dem Port der Listen-Adresse kombiniert (also ist `localhost:2019` eine gültige Origin).
  - Wenn die Listen-Adresse nicht loopback ist, entspricht die erlaubte Origin der Listen-Adresse.

  Wenn der Host der Listen-Adresse keine Wildcard-Schnittstelle ist (Wildcards sind: leerer String, `0.0.0.0` oder `[::]`), wird der `Host`-Header erzwungen. Praktisch bedeutet das, dass der `Host`-Header standardmäßig gegen `origins` geprüft wird, da die Schnittstelle `localhost` ist. Bei einer Adresse wie `:2020` mit Wildcard-Schnittstelle wird der `Host`-Header jedoch nicht geprüft.

- **enforce_origin** erzwingt die Prüfung des `Origin`-Request-Headers. Das geschieht implizit, wenn der Client CORS-Header sendet oder wenn der Client CORS ausdrücklich mit `Sec-Fetch-Mode: no-cors` deaktiviert. Ansonsten ist diese Option am nützlichsten, wenn die Listen-Adresse eine Wildcard-Schnittstelle ist (weil `Host` nicht geprüft wird) und die Admin-API dem öffentlichen Internet ausgesetzt ist. Sie aktiviert CORS-Preflight-Prüfungen und stellt sicher, dass der `Origin`-Header gegen die `origins`-Liste geprüft wird. Verwende dies nur, wenn du Caddy auf deiner Entwicklungsmaschine betreibst und aus einem Webbrowser auf die Admin-API zugreifen musst.

Zum Beispiel, um die Admin-API auf einem anderen Port auf allen Schnittstellen bereitzustellen: ⚠️ Dieser Port **sollte nicht öffentlich erreichbar sein**, sonst kann jeder deinen Server steuern. Wenn er öffentlich sein muss, solltest du Origin-Erzwingung aktivieren:

```caddy
{
	admin :2020
}
```

Um die Admin-API auszuschalten: ⚠️ Dadurch werden **Konfigurations-Reloads unmöglich**, ohne den Server zu stoppen und neu zu starten:

```caddy
{
	admin off
}
```

Um einen [Unix-Socket](/docs/conventions#network-addresses) für die Admin-API zu verwenden, wodurch Zugriffskontrolle über Dateiberechtigungen möglich wird:

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

Um nur Anfragen mit passendem `Origin`-Header zu erlauben:

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```



##### `persist_config`

Steuert, ob die aktuelle JSON-Konfiguration im [Konfigurationsverzeichnis](/docs/conventions#configuration-directory) persistiert werden soll, um zu vermeiden, dass über die Admin-API vorgenommene Konfigurationsänderungen verloren gehen. Derzeit wird nur die Option `off` unterstützt. Standardmäßig wird die Konfiguration persistiert.

```caddy
{
	persist_config off
}
```



##### `log`
Konfiguriert benannte Logger.

Der Name kann übergeben werden, um einen bestimmten Logger anzugeben, dessen Verhalten angepasst werden soll. Wenn kein Name angegeben ist, wird das Verhalten des `default`-Loggers geändert. Mehr über den `default`-Logger und eine Erklärung, [wie Logging in Caddy funktioniert](/docs/logging), findest du in der Logging-Dokumentation.

Mehrere Logger mit unterschiedlichen Namen können konfiguriert werden, indem `log` mehrfach verwendet wird.

Dies unterscheidet sich von der [`log`-Direktive](/docs/caddyfile/directives/log), die nur HTTP-Request-Logging konfiguriert (auch als Access-Logs bekannt). Die globale Option `log` teilt ihre Konfigurationsstruktur mit der Direktive (außer `include` und `exclude`); die vollständige Dokumentation findest du auf der Seite der Direktive.

- **output** konfiguriert, wohin die Logs geschrieben werden.

  Die vollständige Dokumentation findest du bei der [`log`-Direktive](/docs/caddyfile/directives/log#output-modules).

- **format** beschreibt, wie die Logs codiert bzw. formatiert werden.

  Die vollständige Dokumentation findest du bei der [`log`-Direktive](/docs/caddyfile/directives/log#format-modules).

- **level** ist das minimale Entry-Level, das geloggt wird.

  Standard: `INFO`.

  Mögliche Werte: `DEBUG`, `INFO`, `WARN`, `ERROR` und sehr selten `PANIC`, `FATAL`.

- **include** gibt die Log-Namen an, die in diesen Logger aufgenommen werden.

  Standardmäßig ist diese Liste leer (d. h. alle Logs werden eingeschlossen).

  Um zum Beispiel nur Logs einzuschließen, die von der Admin-API ausgegeben werden, würdest du `admin.api` einschließen.

- **exclude** gibt die Log-Namen an, die von diesem Logger ausgeschlossen werden.

  Standardmäßig ist diese Liste leer (d. h. keine Logs werden ausgeschlossen).

  Um zum Beispiel nur HTTP-Access-Logs auszuschließen, würdest du `http.log.access` ausschließen.

Welche Logger-Namen `include` und `exclude` akzeptieren, hängt von den verwendeten Modulen ab; am einfachsten findest du sie in früheren Logs.

Hier ist ein Beispiel, das alle HTTP-Access-Logs und Admin-Logs als JSON nach stdout loggt:

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

##### `grace_period`
Definiert die grace period zum Herunterfahren von HTTP-Servern (d. h. während Konfigurationsänderungen oder wenn Caddy stoppt).

Während der grace period werden keine neuen Verbindungen angenommen, inaktive Verbindungen werden geschlossen, und bei aktiven Verbindungen wird nur kurz darauf gewartet, dass sie ihre Anfragen abschließen. Wenn Clients ihre Anfragen innerhalb der grace period nicht beenden, wird der Server zwangsweise beendet, damit der Reload abgeschlossen und Ressourcen freigegeben werden können. Akzeptiert [Dauerwerte](/docs/conventions#durations).

Standardmäßig ist die grace period unbegrenzt, was bedeutet, dass Verbindungen niemals zwangsweise geschlossen werden.

```caddy
{
	grace_period 10s
}
```


##### `shutdown_delay`
Definiert eine [Dauer](/docs/conventions#durations)
*vor* der [grace period](#grace_period), während der ein Server, der gestoppt werden soll, normal weiterläuft, außer dass der Platzhalter `{http.shutting_down}` zu `true` ausgewertet wird und `{http.time_until_shutdown}` die Zeit bis zum Beginn der grace period angibt.

Dies verursacht eine Verzögerung, wenn ein Server im Rahmen einer Konfigurationsänderung heruntergefahren wird, und plant die Änderung praktisch für einen späteren Zeitpunkt. Das ist nützlich, um Health-Checkern das bevorstehende Herunterfahren dieses Servers anzukündigen und einem Load Balancer Zeit zu geben, ihn aus der Rotation zu nehmen; zum Beispiel:

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Bye-bye in {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Hello, world!"
	}
}
```


<a id="tls-options"></a>
## TLS-Optionen

##### `auto_https`
Konfiguriert [Automatic HTTPS](/docs/automatic-https), die Funktion, mit der Caddy Zertifikatsverwaltung und HTTP-zu-HTTPS-Weiterleitungen für deine Sites automatisiert.

Es stehen mehrere Modi zur Auswahl:

- `off`: Deaktiviert sowohl Zertifikatsautomatisierung als auch HTTP-zu-HTTPS-Weiterleitungen.

- `disable_redirects`: Deaktiviert nur HTTP-zu-HTTPS-Weiterleitungen.

- `disable_certs`: Deaktiviert nur die Zertifikatsautomatisierung.

- `ignore_loaded_certs`: Automatisiert Zertifikate auch für Namen, die auf manuell geladenen Zertifikaten vorkommen. Nützlich, wenn du mit der [`tls`-Direktive](/docs/caddyfile/directives/tls) ein Zertifikat angegeben hast, das Namen (oder Wildcards) enthält, die stattdessen automatisch verwaltet werden sollen.

<aside class="tip">

Diese Option beeinflusst Caddys Standardprotokoll nicht; bei einer Site-Adresse mit gültigem Domainnamen ist es immer HTTPS. Das bedeutet, dass `auto_https off` nicht dazu führt, dass deine Site über HTTP ausgeliefert wird; es deaktiviert nur automatische Zertifikatsverwaltung und Weiterleitungen.

Wenn du deine Site über HTTP ausliefern möchtest, solltest du daher deine [Site-Adresse](/docs/caddyfile/concepts#addresses) so ändern, dass sie mit `http://` beginnt oder mit `:80` endet (oder die Option [`http_port`](#http_port) verwenden).

</aside>

```caddy
{
	auto_https disable_redirects
}
```


##### `email`
Deine E-Mail-Adresse. Wird hauptsächlich beim Erstellen eines ACME-Kontos bei deiner CA verwendet und ist dringend empfohlen, falls es Probleme mit deinen Zertifikaten gibt.

<aside class="tip">

Beachte, dass Let's Encrypt dir möglicherweise E-Mails schickt, wenn sich dein Zertifikat dem Ablaufdatum nähert. Das kann aber irreführend sein, weil Caddy bei der Erneuerung möglicherweise einen anderen Issuer (z. B. ZeroSSL) gewählt hat. Prüfe deine Logs und/oder das Zertifikat selbst (zum Beispiel im Browser), um zu sehen, welcher Issuer verwendet wurde und ob dessen Ablaufdatum noch gültig ist. Falls ja, kannst du die E-Mail von Let's Encrypt gefahrlos ignorieren.

</aside>

```caddy
{
	email admin@example.com
}
```


##### `default_sni`
Setzt einen standardmäßigen TLS-ServerName für den Fall, dass Clients in ihrem ClientHello kein SNI verwenden.

```caddy
{
	default_sni example.com
}
```


##### `fallback_sni`
⚠️ <i>Experimentell</i>

Wenn konfiguriert, wird der Fallback zum TLS-ServerName im ClientHello, falls der ursprüngliche ServerName zu keinem Zertifikat im Cache passt.

Die Anwendungsfälle dafür sind sehr speziell. Typischerweise würdest du dies auf den Hostnamen deines Origins setzen, wenn ein Client ein CDN ist und den ServerName des nachgelagerten Handshakes durchreicht, aber stattdessen ein Zertifikat mit dem Hostnamen des Origins akzeptieren kann. Beachte, dass Caddy für diesen Namen ein Zertifikat verwalten muss.

```caddy
{
	fallback_sni example.com
}
```


##### `local_certs`
Bewirkt, dass **alle** Zertifikate standardmäßig intern ausgestellt werden, statt über eine (öffentliche) ACME-CA wie Let's Encrypt. Das ist als schneller Schalter in Entwicklungsumgebungen nützlich.

```caddy
{
	local_certs
}
```


##### `skip_install_trust`
Überspringt die Versuche, die Root der lokalen CA in den Trust Store des Systems sowie in die Trust Stores von Java und Mozilla Firefox zu installieren.

```caddy
{
	skip_install_trust
}
```


##### `acme_ca`
Gibt die URL zum Verzeichnis der ACME-CA an. Für Tests oder Entwicklung wird dringend empfohlen, dies auf den [Staging-Endpunkt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) von Let's Encrypt zu setzen. Standard: die Produktionsendpunkte von ZeroSSL und Let's Encrypt.

Beachte, dass eine global konfigurierte ACME-CA möglicherweise nicht für alle Sites gilt. Siehe die [Hostname-Anforderungen](/docs/automatic-https#hostname-requirements) zur Verwendung der standardmäßigen ACME-Issuer.

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

##### `acme_ca_root`
Gibt eine PEM-Datei an, die ein vertrauenswürdiges Root-Zertifikat für ACME-CA-Endpunkte enthält, falls es nicht im Trust Store des Systems liegt.

```caddy
{
	acme_ca_root /path/to/ca/root.pem
}
```


##### `acme_eab`
Gibt ein External Account Binding an, das für alle ACME-Transaktionen verwendet wird.

Zum Beispiel mit simulierten ZeroSSL-Zugangsdaten:

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


##### `acme_dns`
Konfiguriert den Provider für die [ACME-DNS-Challenge](/docs/automatic-https#dns-challenge), der für alle ACME-Transaktionen verwendet wird.

Erfordert einen eigenen Caddy-Build mit einem Plugin für deinen DNS-Provider.

Die Tokens nach dem Namen des Providers richten den Provider genauso ein, als wäre er im `acme`-Issuer der [`tls`-Direktive](/docs/caddyfile/directives/tls#acme) angegeben.

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


##### `dns`
Konfiguriert einen standardmäßigen DNS-Provider, der verwendet wird, wenn lokal in einem relevanten Kontext kein anderer angegeben ist. Wenn zum Beispiel die ACME-DNS-Challenge aktiviert ist, aber kein DNS-Provider konfiguriert wurde, wird dieser globale Standard verwendet. Er wird auch zum Veröffentlichen von Encrypted ClientHello (ECH)-Konfigurationen angewendet.

Damit dies funktioniert, muss dein Caddy-Binary mit dem angegebenen DNS-Provider-Modul kompiliert sein.

Beispiel mit Zugangsdaten aus einer Umgebungsvariable:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

(Erfordert Caddy 2.10 beta 1 oder neuer.)


##### `ech`
Aktiviert Encrypted ClientHello (ECH), indem die angegebenen öffentlichen Domainnamen als Klartext-Servername (SNI) in TLS-Handshakes verwendet werden. Unter den richtigen Bedingungen kann ECH helfen, die Domainnamen deiner Sites während Verbindungen auf der Leitung zu schützen. Caddy generiert und veröffentlicht für jeden angegebenen öffentlichen Namen eine ECH-Konfiguration. Durch diese Veröffentlichung wissen kompatible Clients (wie korrekt konfigurierte moderne Browser), dass sie ECH verwenden sollen, um auf deine Sites zuzugreifen.

Damit dies korrekt funktioniert, müssen die ECH-Konfigurationen so veröffentlicht werden, wie Clients es erwarten. Die meisten Browser (mit aktiviertem DNS-over-HTTPS oder DNS-over-TLS) erwarten, dass ECH-Konfigurationen in DNS-Records des Typs HTTPS veröffentlicht werden. Caddy führt diese Art der Veröffentlichung automatisch durch, aber du musst entweder mit der Unteroption `dns` oder global mit der globalen Option [`dns`](#dns) einen DNS-Provider angeben, und dein Caddy-Binary muss mit dem angegebenen DNS-Provider-Modul gebaut sein. (Custom Builds sind auf unserer [Download-Seite](/download) verfügbar.)

**Datenschutzhinweise:**

- Es ist im Allgemeinen ratsam, **die Größe deines [*Anonymity Set*](https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction) zu maximieren**. Deshalb empfehlen wir den meisten Benutzern typischerweise, *nur einen* öffentlichen Domainnamen zu konfigurieren, um alle Sites zu schützen.
- **Dein Server sollte für die angegebenen öffentlichen Domainnamen autoritativ sein** (d. h. sie sollten auf deinen Server zeigen), weil Caddy dafür ein Zertifikat beziehen wird. Diese Zertifikate sind in manchen Fällen entscheidend, damit spezifikationskonforme Clients zuverlässig und sicher mit ECH verbinden können. Sie werden nur verwendet, um einen korrekten ECH-Handshake zu ermöglichen, nicht für Anwendungsdaten (deine Sites, außer du definierst eine Site, die deinem öffentlichen Domainnamen entspricht).
- Jede Situation kann anders sein. Wenn viel auf dem Spiel steht, empfehlen wir, Experten hinzuzuziehen, um **dein Bedrohungsmodell zu prüfen**, da ECH keine Universallösung ist.

Beispiel mit Zugangsdaten aus einer Umgebungsvariable für die Veröffentlichung auf Nameservern, die bei Cloudflare liegen:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

Dies sollte dazu führen, dass kompatible Clients alle deine Sites mit `ech.example.net` laden, statt die einzelnen Site-Namen im Klartext offenzulegen.

Eine erfolgreiche Veröffentlichung setzt voraus, dass die Domains deiner Site beim konfigurierten DNS-Provider liegen und die Records mit den angegebenen Zugangsdaten bzw. der Provider-Konfiguration geändert werden können.

(Erfordert Caddy 2.10 beta 1 oder neuer.)


##### `on_demand_tls`
Konfiguriert [On-Demand TLS](/docs/automatic-https#on-demand-tls) dort, wo es aktiviert ist, aktiviert es aber nicht selbst (zum Aktivieren verwende die Unterdirektive [`on_demand` der `tls`-Direktive](/docs/caddyfile/directives/tls#syntax)). Für den Einsatz in Produktionsumgebungen erforderlich, um Missbrauch zu verhindern.

- **ask** veranlasst Caddy, eine HTTP-Anfrage an die angegebene URL zu stellen und zu fragen, ob für eine Domain ein Zertifikat ausgestellt werden darf.

  Die Anfrage hat einen Query-String `?domain=`, der den Wert des Domainnamens enthält.

  Wenn der Endpunkt einen `2xx`-Statuscode zurückgibt, ist Caddy autorisiert, ein Zertifikat für diesen Namen zu beziehen. Jeder andere Statuscode führt dazu, dass die Ausstellung des Zertifikats abgebrochen wird und der TLS-Handshake mit einem Fehler endet.

<aside class="tip">

Der ask-Endpunkt sollte *so schnell wie möglich* antworten, idealerweise innerhalb weniger Millisekunden. Typischerweise sollte dein Endpunkt eine konstante Lookup-Operation in einer Datenbank mit Index nach Domainname ausführen; vermeide Schleifen. Vermeide DNS-Abfragen oder andere Netzwerkanfragen.

</aside>

- **permission** erlaubt die Verwendung eigener Module, um zu bestimmen, ob für einen bestimmten Namen ein Zertifikat ausgestellt werden soll. Das Modul muss das Interface [`caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission) implementieren. Ein `http`-Permission-Modul ist enthalten; dieses wird von der Option `ask` verwendet und bleibt als Kurzform aus Gründen der Abwärtskompatibilität erhalten.

- ⚠️ Die Rate-Limiting-Optionen **interval** und **burst** waren verfügbar, werden aber NICHT empfohlen. Entferne sie aus deiner Konfiguration, falls du sie noch hast.

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


##### `key_type`
Gibt den Schlüsseltyp an, der für TLS-Zertifikate generiert werden soll. Ändere dies nur, wenn du einen konkreten Bedarf zur Anpassung hast.

Mögliche Werte sind: `ed25519`, `p256`, `p384`, `rsa2048`, `rsa4096`.

```caddy
{
	key_type ed25519
}
```


##### `cert_issuer`
Definiert den Issuer (oder die Quelle) von TLS-Zertifikaten.

Damit können Issuer global konfiguriert werden, statt pro Site wie mit der Unterdirektive [`issuer` der `tls`-Direktive](/docs/caddyfile/directives/tls#issuer).

Kann wiederholt werden, wenn du mehrere Issuer konfigurieren möchtest, die ausprobiert werden sollen. Sie werden in der Reihenfolge versucht, in der sie definiert sind.

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


##### `renew_interval`
Wie oft alle geladenen, verwalteten Zertifikate auf Ablauf geprüft werden und bei Ablauf eine Erneuerung ausgelöst wird.

Standard: `10m`

```caddy
{
	renew_interval 30m
}
```


##### `cert_lifetime`
Die Gültigkeitsdauer, für die die CA gebeten wird, ein Zertifikat auszustellen.

Dieser Wert wird verwendet, um das Feld `notAfter` der ACME-Order zu berechnen; daher muss die Systemuhr ausreichend synchronisiert sein. HINWEIS: Nicht alle CAs unterstützen dies. Prüfe in der ACME-Dokumentation deiner CA, ob dies erlaubt ist und welche Werte verwendet werden dürfen.

Standard: `0` (die CA wählt die Laufzeit, normalerweise 90 Tage)

⚠️ Dies ist eine experimentelle Funktion. Sie kann geändert oder entfernt werden.

```caddy
{
	cert_lifetime 30d
}
```


##### `ocsp_interval`
Wie oft geprüft wird, ob [OCSP-Staples <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OCSP_stapling) aktualisiert werden müssen.

Standard: `1h`

```caddy
{
	ocsp_interval 2h
}
```


##### `ocsp_stapling`
Kann auf `off` gesetzt werden, um OCSP-Stapling zu deaktivieren. Nützlich in Umgebungen, in denen Responder wegen Firewalls nicht erreichbar sind.

```caddy
{
	ocsp_stapling off
}
```

##### `renewal_window_ratio`
Das Verhältnis (zwischen 0 und 1) der Zertifikatslaufzeit, das noch verbleiben muss, bevor Caddy versucht, das Zertifikat zu erneuern. Wenn ein Zertifikat zum Beispiel eine Laufzeit von 90 Tagen hat und dieses Verhältnis `0.3333` ist (der Standardwert), versucht Caddy fortlaufend, das Zertifikat zu erneuern, sobald es 30 Tage oder weniger bis zum Ablauf hat. Kann auch pro Site mit der Unterdirektive [`renewal_window_ratio` der `tls`-Direktive](/docs/caddyfile/directives/tls#renewal_window_ratio) gesetzt werden.

Du solltest dies nur selten ändern müssen, aber es kann nützlich sein, später in der Laufzeit des Zertifikats zu erneuern, wenn deine CA sehr lange für die Ausstellung braucht.

Beachte, dass dies ein Vorschlag ist, da ACME-Issuer die [ARI-Erweiterung](https://datatracker.ietf.org/doc/rfc9773/) implementieren können. Dabei gibt der Issuer ein Zeitfenster vor, in dem der ACME-Client (in diesem Fall Caddy) die Erneuerung versuchen soll, und dieses Fenster muss nicht mit diesem Verhältnis übereinstimmen.

```caddy
{
	renewal_window_ratio 0.1
}
```


##### `preferred_chains`
Wenn deine CA mehrere Zertifikatsketten bereitstellt, kannst du mit dieser Option angeben, welche Kette Caddy bevorzugen soll. Setze eine der folgenden Optionen:

- **smallest** weist Caddy an, Ketten mit der geringsten Byte-Anzahl zu bevorzugen.

- **root_common_name** ist eine Liste aus einem oder mehreren Common Names; Caddy wählt die erste Kette, deren Root mit mindestens einem der angegebenen Common Names übereinstimmt.

- **any_common_name** ist eine Liste aus einem oder mehreren Common Names; Caddy wählt die erste Kette, deren Issuer mit mindestens einem der angegebenen Common Names übereinstimmt.

Beachte, dass `preferred_chains` als globale Option alle Issuer beeinflusst, wenn keine [überschreibende Konfiguration auf Issuer-Ebene](/docs/caddyfile/directives/tls#acme) vorhanden ist.

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```


<a id="server-options"></a>
## Server-Optionen

Passt [HTTP-Server](/docs/json/apps/http/servers/) mit Einstellungen an, die sich potenziell über mehrere Sites erstrecken und daher nicht sinnvoll in Site-Blöcken konfiguriert werden können. Diese Optionen betreffen den Listener/Socket oder andere Einrichtungen unterhalb der HTTP-Schicht.

Kann mehrfach mit unterschiedlichen `listener_address`-Werten angegeben werden, um verschiedene Optionen pro Server zu konfigurieren. Zum Beispiel gilt `servers :443` nur für den Server, der an die Listener-Adresse `:443` gebunden ist. Wenn die Listener-Adresse weggelassen wird, gelten die Optionen für alle verbleibenden Server.

<aside class="tip">

Verwende den Befehl [`caddy adapt`](/docs/command-line#caddy-adapt), um die Listen-Adresse der Server in deinem Caddyfile zu finden.

</aside>


Um zum Beispiel unterschiedliche Optionen für die Server auf den Ports `:80` und `:443` zu konfigurieren, würdest du zwei `servers`-Blöcke angeben:

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

Bei Verwendung von `servers` gilt dies **nur** für Server, die **tatsächlich** in deinem Caddyfile erscheinen (d. h. durch einen Site-Block erzeugt werden). Denk daran: [Automatic HTTPS](/docs/automatic-https) erstellt zur Laufzeit einen Server, der auf Port `80` (oder der Option [`http_port`](#http_port)) lauscht, um HTTP->HTTPS-Weiterleitungen auszuliefern und die ACME-HTTP-Challenge zu lösen; das geschieht zur Laufzeit, also *nachdem* der Caddyfile-Adapter `servers` angewendet hat. Anders gesagt: `servers` gilt **nicht** für `:80`, sofern du nicht ausdrücklich einen Site-Block wie `http://` oder `:80` deklarierst.


<aside class="tip">

Wenn du die [`bind`-Direktive](/docs/caddyfile/directives/bind) oder die globale Option [`default_bind`](/docs/caddyfile/options#default_bind) verwendest, *MUSS* die `listener_address` der Bind-Adresse kombiniert mit dem Port des Site-Blocks entsprechen, sonst werden die Einstellungen nicht angewendet. Zum Beispiel:

```caddy
{
	# Dies matcht den Server NICHT, Bind-Adresse fehlt
	servers :8080 {
		name private
	}

	# Dies funktioniert, weil es ein exakter Match ist
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



##### `name`

Ein benutzerdefinierter Name, der diesem Server zugewiesen wird. Das ist normalerweise hilfreich, um einen Server in Logs und Metriken anhand seines Namens zu identifizieren. Wenn nicht gesetzt, definiert Caddy ihn dynamisch nach dem Muster `srvX`, wobei `X` bei `0` beginnt und basierend auf der Anzahl der Server in der Konfiguration hochgezählt wird.

Beachte, dass Einstellungen nur auf Server angewendet werden, die durch Site-Blöcke in deiner Konfiguration erzeugt werden. [Automatic HTTPS](/docs/automatic-https) erstellt zur Laufzeit einen `:80`-Server (oder [`http_port`](#http_port)); wenn du ihn umbenennen möchtest, brauchst du mindestens einen leeren `http://`-Site-Block.

Zum Beispiel:

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```

</aside>



##### `listener_wrappers`

Erlaubt die Konfiguration von [Listener-Wrappers](/docs/json/apps/http/servers/listener_wrappers/), die das Verhalten des Socket-Listeners ändern können. Sie werden in der angegebenen Reihenfolge angewendet.

###### `tls`

Der `tls`-Listener-Wrapper ist ein No-op-Listener-Wrapper, der markiert, wo der TLS-Listener in einer Kette von Listener-Wrappers stehen soll. Er sollte nur verwendet werden, wenn ein anderer Listener-Wrapper vor dem TLS-Handshake platziert werden muss.

###### `http_redirect`

[`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/) stellt HTTP->HTTPS-Weiterleitungen für Verbindungen bereit, die auf dem TLS-Port als HTTP-Anfrage ankommen, indem anhand der ersten Bytes erkannt wird, dass es kein TLS-Handshake, sondern eine HTTP-Anfrage ist. Das ist am nützlichsten, wenn HTTPS auf einem nicht standardmäßigen Port (anders als `443`) bereitgestellt wird, da Browser HTTP versuchen, sofern das Schema nicht angegeben ist. Er muss *vor* dem `tls`-Listener-Wrapper platziert werden. Hier ist ein Beispiel:

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

###### `proxy_protocol`

Der [`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/)-Listener-Wrapper (vor v2.7.0 nur über ein Plugin verfügbar) aktiviert das Parsen des [PROXY-Protokolls](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (bekannt gemacht durch HAProxy). Er muss *vor* dem `tls`-Listener-Wrapper verwendet werden, da er Klartextdaten am Anfang der Verbindung parst:

Beachte, dass Metadaten aus dem PROXY-Protokoll auf die Verbindung angewendet werden können, bevor Matcher oder [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) ausgewertet werden. Die IP-Adresse des direkten Peers geht für weitere Auswertungen verloren.

```caddy-d
proxy_protocol {
	timeout <duration>
	allow <cidrs...>
	deny <cidrs...>
	fallback_policy <policy>
}
```

- **timeout** gibt die maximale Dauer an, die auf den PROXY-Header gewartet wird. Standard: `5s`.

- **allow** ist eine Liste von CIDR-Bereichen vertrauenswürdiger Quellen, von denen PROXY-Header angenommen werden. Unix-Sockets sind standardmäßig vertrauenswürdig und nicht Teil dieser Option.

- **deny** ist eine Liste von CIDR-Bereichen vertrauenswürdiger Quellen, von denen PROXY-Header abgelehnt werden.

- **fallback_policy** ist die Aktion, die ausgeführt wird, wenn der PROXY-Header von einer Adresse kommt, die weder in der allow- noch in der deny-Liste steht. Die Standard-Fallback-Policy ist `ignore`. Akzeptierte Werte für `fallback_policy` sind:
	- `ignore`: Adresse aus dem PROXY-Header, Verbindung aber akzeptieren
	- `use`: Adresse aus dem PROXY-Header
	- `reject`: Verbindung ablehnen, wenn ein PROXY-Header gesendet wird
	- `require`: Verbindung muss einen PROXY-Header senden, andernfalls ablehnen
	- `skip`: akzeptiert eine Verbindung, ohne den PROXY-Header zu verlangen.


Zum Beispiel für einen HTTPS-Server (der den `tls`-Listener-Wrapper benötigt), der PROXY-Header aus einem bestimmten IP-Adressbereich annimmt und PROXY-Header aus einem anderen Bereich ablehnt, mit einem Timeout von 2 Sekunden:

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


##### `timeouts`

- **read_body** ist ein [Dauerwert](/docs/conventions#durations), der festlegt, wie lange ein Lesevorgang aus dem Upload eines Clients erlaubt ist. Ein kurzer, von null verschiedener Wert kann Slowloris-Angriffe abschwächen, aber auch legitime langsame Clients beeinträchtigen. Standardmäßig kein Timeout.

- **read_header** ist ein [Dauerwert](/docs/conventions#durations), der festlegt, wie lange ein Lesevorgang aus den Request-Headern eines Clients erlaubt ist. Standardmäßig kein Timeout.

- **write** ist ein [Dauerwert](/docs/conventions#durations), der festlegt, wie lange ein Schreibvorgang zu einem Client erlaubt ist. Beachte, dass ein kleiner Wert beim Ausliefern großer Dateien legitime langsame Clients negativ beeinflussen kann. Standardmäßig kein Timeout.

- **idle** ist ein [Dauerwert](/docs/conventions#durations), der die maximale Wartezeit auf die nächste Anfrage festlegt, wenn Keep-Alives aktiviert sind. Standard: 5 Minuten, um Ressourcenerschöpfung zu vermeiden.

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


##### `keepalive_interval`

Das Intervall, in dem TCP-Keepalive-Pakete gesendet werden, um die Verbindung auf TCP-Ebene aktiv zu halten, wenn keine anderen Daten übertragen werden. Standard: `15s`.

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


##### `keepalive_idle`

Die Dauer, die eine Verbindung inaktiv sein muss, bevor TCP-Keepalive-Pakete gesendet werden, wenn keine anderen Daten übertragen werden. Standard: `15s`.

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


##### `keepalive_count`

Die maximale Anzahl von TCP-Keepalive-Paketen, die gesendet werden, bevor die Verbindung als tot betrachtet wird. Standard: `9`.

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


##### `0rtt`

Standardmäßig ist 0-RTT (Early Data) für QUIC-Listener (d. h. HTTP/3) aktiviert, damit Clients Daten bereits im ersten Roundtrip des TLS-Handshakes senden können. Das kann die Performance bei wiederholten Verbindungen verbessern.

Du kannst dies auf `off` setzen, um 0-RTT für QUIC-Listener zu deaktivieren. Ein Grund, 0-RTT zu deaktivieren, ist die Verwendung eines [`remote_ip`-Matchers](/docs/caddyfile/matchers#remote-ip), wodurch eine Abhängigkeit davon entsteht, dass die Remote-Adresse verifiziert wurde, wenn Routing stattfindet, bevor der TLS-Handshake abgeschlossen ist. In diesem Fall wird eine HTTP-425-Antwort geschrieben, aber manche Clients (Browser) können sich fehlerhaft verhalten und keinen Retry durchführen. Das Deaktivieren von 0-RTT kann daher sicherstellen, dass Benutzer keine 425-Antworten sehen, allerdings auf Kosten der Performance-Vorteile von 0-RTT.

```caddy
{
	servers {
		0rtt off
	}
}
```


##### `trusted_proxies`

Erlaubt die Konfiguration von IP-Bereichen (CIDRs) von Proxy-Servern, deren Anfragen vertraut werden soll. Standardmäßig wird keinen Proxies vertraut.

Wenn dies aktiviert ist, wird bei vertrauenswürdigen Anfragen die *echte* Client-IP aus HTTP-Headern geparst (standardmäßig `X-Forwarded-For`; siehe [`client_ip_headers`](#client-ip-headers), um andere Header zu konfigurieren). Bei vertrauenswürdigen Anfragen wird die Client-IP zu [Access-Logs](/docs/caddyfile/directives/log) hinzugefügt, ist als `{client_ip}`-[Platzhalter](/docs/caddyfile/concepts#placeholders) verfügbar und erlaubt die Verwendung des [`client_ip`-Matchers](/docs/caddyfile/matchers#client-ip). Wenn die Anfrage nicht von einem vertrauenswürdigen Proxy stammt, wird die Client-IP auf die Remote-IP-Adresse der direkt eingehenden Verbindung gesetzt oder, falls verwendet, auf die durch das [PROXY-Protokoll](/docs/caddyfile/options#proxy-protocol) gesetzte Adresse. Standardmäßig werden IPs in Headern von links nach rechts geparst. Siehe [`trusted_proxies_strict`](#trusted-proxies-strict), um dieses Verhalten zu ändern.

Einige Matcher oder Handler können den Vertrauensstatus der Anfrage für Entscheidungen verwenden. Wenn sie zum Beispiel vertrauenswürdig ist, proxyt und ergänzt der [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#defaults)-Handler die sensiblen `X-Forwarded-*`-Request-Header.

Derzeit ist nur das [IP-Quellmodul](/docs/json/apps/http/servers/trusted_proxies/) `static` in der Standarddistribution von Caddy enthalten, aber dies kann mit Plugins [erweitert](/docs/extending-caddy) werden, um eine dynamische Liste von IP-Bereichen zu pflegen.


###### `static`

Nimmt eine statische (unveränderliche) Liste vertrauenswürdiger IP-Bereiche (CIDRs) entgegen.

Als Kurzform kann `private_ranges` verwendet werden, um alle privaten IPv4- und IPv6-Bereiche zu matchen. Das entspricht der Angabe all dieser Bereiche: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`.

Die Syntax ist wie folgt:

```caddy-d
trusted_proxies static [private_ranges] <ranges...>
```

Hier ist ein vollständiges Beispiel, das einem beispielhaften IPv4-Bereich und einem IPv6-Bereich vertraut:

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

##### `trusted_proxies_strict`

Wenn [`trusted_proxies`](#trusted-proxies) aktiviert ist, werden die IPs in den Headern (konfiguriert durch [`client_ip_headers`](#client-ip-headers)) standardmäßig von links nach rechts geparst. Die erste gefundene nicht vertrauenswürdige IP-Adresse wird zur echten Client-Adresse. Seit v2.8 kannst du mit `trusted_proxies_strict` das Parsen dieser Header von rechts nach links aktivieren. Aus Gründen der Abwärtskompatibilität ist diese Option standardmäßig deaktiviert.

Upstream-Proxies wie HAProxy, CloudFlare, AWS ALB, CloudFront usw. hängen jede neu verbindende Remote-Adresse rechts an `X-Forwarded-For` an. Bei der Arbeit mit solchen Proxies wird empfohlen, `trusted_proxies_strict` zu aktivieren, da die ganz linke IP-Adresse vom Client gefälscht sein kann.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">

Insbesondere bei AWS ALB willst du diese Option mit Sicherheit aktivieren. [Laut deren Dokumentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15) kannst du die echte Client-IP nur identifizieren, indem du den XFF-Modus auf `append` setzt. Diese IP wird rechts an `X-Forwarded-For` angehängt und kann nur über `trusted_proxies_strict` sicher extrahiert werden.

</aside>

##### `trusted_proxies_unix`

Die Option `trusted_proxies_unix` erlaubt es, allen Verbindungen zu vertrauen, die von Unix-Sockets kommen. Das ist nützlich, wenn Caddy hinter einem Reverse Proxy steht (möglicherweise einer anderen Caddy-Instanz), der über einen Unix-Socket verbindet (d. h. die [`bind`-Direktive](/docs/caddyfile/directives/bind) ist auf einen Unix-Socket gesetzt). Standardmäßig ist dies deaktiviert.

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

##### `client_ip_headers`

In Kombination mit [`trusted_proxies`](#trusted-proxies) kann konfiguriert werden, welche Header zur Bestimmung der IP-Adresse des Clients verwendet werden. Standardmäßig wird nur `X-Forwarded-For` berücksichtigt. Mehrere Header-Felder können angegeben werden; in diesem Fall wird der erste nicht leere Header-Wert verwendet.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


##### `metrics`

Aktiviert die Metrikerfassung; erforderlich, bevor Metriken gescrapt oder mit OTLP gepusht werden. Beachte, dass Metriken die Performance auf sehr stark ausgelasteten Servern reduzieren. (Unsere Community arbeitet daran, dies zu verbessern. Bitte beteilige dich!)

```caddy
{
	metrics
}
```

Du kannst die Option `per_host` hinzufügen, um Metriken mit dem Hostnamen der Metrik zu labeln.

```caddy
{
	metrics {
		per_host
	}
}
```

Da das Beobachten aller möglichen Hosts, die Clients senden können, potenziell unendliche Kardinalität erzeugt, zeichnet Caddy nur Metriken für konfigurierte Hosts auf, während alle anderen Hosts (z. B. attacker.com) unter dem Label "_other" aggregiert werden. Um die Beobachtung aller Hosts zu erzwingen, wenn potenziell unendliche Kardinalität ein akzeptables Risiko ist, fügst du `observe_catchall_hosts` hinzu. Beachte, dass `observe_catchall_hosts` `per_host` nicht aktiviert. Für HTTPS-Server ist dies jedoch automatisch aktiviert (da Zertifikate einen gewissen Schutz vor unbegrenzter Kardinalität bieten), für HTTP-Server aber standardmäßig deaktiviert, um Kardinalitätsangriffe über beliebige Host-Header zu verhindern.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

Du kannst die Option `otlp` hinzufügen, um dieselben Metriken an einen OpenTelemetry Protocol (OTLP)-Endpunkt zu pushen. Der Exporter wird über standardmäßige OpenTelemetry-Umgebungsvariablen `OTEL_*` konfiguriert, etwa `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL` und `OTEL_METRICS_EXPORTER`.

```caddy
{
	metrics {
		otlp
	}
}
```

Zum Beispiel:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Weitere Details findest du unter [Caddy mit Metriken überwachen](/docs/metrics).

##### `trace`

Loggt jeden einzelnen Handler, der aufgerufen wird. Erfordert, dass das Log auf `DEBUG`-Level ausgibt (das kannst du mit der globalen Option [`debug`](#debug) tun).

HINWEIS: Dies kann die Konfiguration deiner HTTP-handler-Module loggen. Aktiviere dies nicht in unsicheren Kontexten, wenn die Konfiguration sensible Daten enthält.

⚠️ Dies ist eine experimentelle Funktion. Sie kann geändert oder entfernt werden.

```caddy
{
	servers {
		trace
	}
}
```


##### `max_header_size`

Die maximale Größe, die aus den HTTP-Request-Headern eines Clients geparst wird. Wenn das Limit überschritten wird, antwortet der Server mit HTTP-Status `431 Request Header Fields Too Large`. Akzeptiert alle von [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) unterstützten Formate. Standardmäßig beträgt das Limit `1MB`.

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


##### `enable_full_duplex`

Aktiviert Full-Duplex-Kommunikation für HTTP/1-Anfragen.

Bei HTTP/1-Anfragen verbraucht der Go-HTTP-Server standardmäßig jeden ungelesenen Teil des Request-Bodys, bevor er mit dem Schreiben der Antwort beginnt. Dadurch werden Handler daran gehindert, gleichzeitig aus der Anfrage zu lesen und die Antwort zu schreiben. Das Aktivieren dieser Option deaktiviert dieses Verhalten und erlaubt Handlern, weiter aus der Anfrage zu lesen, während sie gleichzeitig die Antwort schreiben.

Bei HTTP/2+-Anfragen erlaubt der Go-HTTP-Server immer gleichzeitiges Lesen und Antworten, daher hat diese Option keine Wirkung.

Teste gründlich mit deinen HTTP-Clients, da einige ältere Clients Full-Duplex-HTTP/1 möglicherweise nicht unterstützen, was zu Deadlocks führen kann. Weitere Informationen findest du unter [golang/go#57786](https://github.com/golang/go/issues/57786).

⚠️ Dies ist eine experimentelle Funktion. Sie kann geändert oder entfernt werden.

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


##### `log_credentials`

Standardmäßig werden Access-Logs (aktiviert mit der [`log`-Direktive](/docs/caddyfile/directives/log)) mit Headern, die potenziell sensible Informationen enthalten (`Cookie`, `Set-Cookie`, `Authorization` und `Proxy-Authorization`), als `REDACTED` geloggt.

Wenn diese Header *nicht* redigiert werden sollen, kannst du die Option `log_credentials` aktivieren.

```caddy
{
	servers {
		log_credentials
	}
}
```



##### `protocols`

Die durch Leerzeichen getrennte Liste der zu unterstützenden HTTP-Protokolle.

Standard: `h1 h2 h3`

Akzeptierte Werte sind:
- `h1` für HTTP/1.1
- `h2` für HTTP/2
- `h2c` für HTTP/2 über Klartext
- `h3` für HTTP/3

Derzeit bedeutet das Aktivieren von HTTP/2 (einschließlich H2C) zwangsläufig auch das Aktivieren von HTTP/1.1, weil die Go-Standardbibliothek es bei Verwendung ihres HTTP-Servers nicht erlaubt, HTTP/1.1 zu deaktivieren. HTTP/1.1 oder HTTP/3 können jedoch jeweils unabhängig aktiviert werden.

Beachte, dass H2C ("Cleartext HTTP/2" oder "H2 over TCP") und HTTP/3 nicht von der Go-Standardbibliothek implementiert werden, sodass einige Funktionalitäten oder Features eingeschränkt sein können. Wir raten davon ab, H2C zu aktivieren, außer es ist für deine Anwendung absolut notwendig.

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



##### `strict_sni_host`

Wenn dies aktiviert ist, muss der `Host`-Header einer Anfrage mit dem Wert von `ServerName` übereinstimmen, den das TLS-ClientHello des Clients sendet. Das ist eine notwendige Schutzmaßnahme bei Verwendung von TLS-Client-Authentifizierung. Bei einer Abweichung wird eine HTTP-Antwort mit Status `421 Misdirected Request` an den Client geschrieben.

Diese Option wird automatisch aktiviert, wenn [Client-Authentifizierung](/docs/caddyfile/directives/tls#client_auth) konfiguriert ist. Dadurch wird ein Bypass der TLS-Client-Authentifizierung (Domain Fronting) verhindert, der andernfalls ausgenutzt werden könnte, indem während eines TLS-Handshakes ein ungeschützter SNI-Wert gesendet und nach dem Verbindungsaufbau eine geschützte Domain in den Host-Header gesetzt wird. Dieses Verhalten ist ein sicherer Standard, aber du kannst es mit `insecure_off` ausdrücklich abschalten; zum Beispiel beim Betrieb eines Proxys, bei dem Domain Fronting gewünscht ist und der Zugriff nicht anhand des Hostnamens beschränkt wird.

```caddy
{
	servers {
		strict_sni_host on
	}
}
```



<a id="file-systems"></a>
## Dateisysteme

Die globale Option `filesystem` erlaubt das Deklarieren eines oder mehrerer Dateisysteme, die für Datei-I/O verwendet werden können.

Damit kannst du dich etwa mit einem entfernten Dateisystem in der Cloud verbinden, mit einer Datenbank mit dateiähnlicher Schnittstelle oder sogar Dateien lesen, die im Caddy-Binary eingebettet sind.

Dateisysteme werden mit einem Namen deklariert, um sie zu identifizieren. Das bedeutet, dass du dich bei Bedarf mit mehr als einem Dateisystem desselben Typs verbinden kannst.

Standardmäßig hat Caddy keine Dateisystemmodule, daher musst du Caddy mit einem Plugin für das Dateisystem bauen, das du verwenden möchtest.

#### Beispiel

Mit einem fiktiven `custom`-Dateisystemmodul könntest du zwei Dateisysteme deklarieren:

```caddy
{
	filesystem foo custom {
		...
	}

	filesystem bar custom {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```



<a id="pki-options"></a>
## PKI-Optionen

Die PKI-App (Public Key Infrastructure) ist die Grundlage für Caddys Funktionen [Local HTTPS](/docs/automatic-https#local-https) und [ACME server](/docs/caddyfile/directives/acme_server). Die App definiert Certificate Authorities (CAs), die Zertifikate signieren können.

Die standardmäßige CA-ID ist `local`. Wenn die ID beim Konfigurieren von `ca` weggelassen wird, wird `local` angenommen.

##### `name`
Der benutzerseitig sichtbare Name der Certificate Authority.

Standard: `Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "My Local CA"
		}
	}
}
```

##### `root_cn`
Der Name, der in das CommonName-Feld des Root-Zertifikats eingetragen wird.

Standard: `{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "My Local CA - 2024 ECC Root"
		}
	}
}
```

##### `intermediate_cn`
Der Name, der in das CommonName-Feld der Intermediate-Zertifikate eingetragen wird.

Standard: `{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "My Local CA - ECC Intermediate"
		}
	}
}
```

##### `intermediate_lifetime`
Die [Dauer](/docs/conventions#durations), für die Intermediate-Zertifikate gültig sind. Dieser Wert **muss** kleiner sein als die Laufzeit des Root-Zertifikats (`3600d` oder 10 Jahre).

Standard: `7d`. Es wird *nicht empfohlen*, dies zu ändern, außer es ist absolut notwendig.

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

##### `maintenance_interval`
Die [Dauer](/docs/conventions#durations), wie oft geprüft wird, ob Intermediate-Zertifikate (und, falls zutreffend, Root-Zertifikate) erneuert werden müssen.

Standard: `10m`. Es wird *nicht empfohlen*, dies zu ändern, außer es ist absolut notwendig.

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

##### `renewal_window_ratio`
Das Verhältnis (zwischen 0 und 1) der Zertifikatslaufzeit, das noch verbleiben muss, bevor Caddy versucht, Zertifikate zu erneuern. Wenn ein Zertifikat zum Beispiel eine Laufzeit von 1 Jahr hat und dieses Verhältnis `0.2` ist (der Standardwert), versucht Caddy fortlaufend, das Zertifikat zu erneuern, sobald es 73 Tage oder weniger bis zum Ablauf hat.

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


##### `root`
Ein Schlüsselpaar (Zertifikat und privater Schlüssel), das als Root für die CA verwendet wird. Wenn nicht angegeben, wird eines automatisch generiert und verwaltet.

- **format** ist das Format, in dem Zertifikat und privater Schlüssel bereitgestellt werden. Derzeit wird nur `pem_file` unterstützt; das ist der Standard, daher ist dieses Feld optional.
- **cert** ist das Zertifikat. Bei Verwendung des Formats `pem_file` sollte dies der Pfad zu einer PEM-Datei sein.
- **key** ist der private Schlüssel. Bei Verwendung des Formats `pem_file` sollte dies der Pfad zu einer PEM-Datei sein.

##### `intermediate`
Ein Schlüsselpaar (Zertifikat und privater Schlüssel), das als Intermediate für die CA verwendet wird. Wenn nicht angegeben, wird eines automatisch generiert und verwaltet.

- **format** ist das Format, in dem Zertifikat und privater Schlüssel bereitgestellt werden. Derzeit wird nur `pem_file` unterstützt; das ist der Standard, daher ist dieses Feld optional.
- **cert** ist das Zertifikat. Bei Verwendung des Formats `pem_file` sollte dies der Pfad zu einer PEM-Datei sein.
- **key** ist der private Schlüssel. Bei Verwendung des Formats `pem_file` sollte dies der Pfad zu einer PEM-Datei sein.

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /path/to/root.pem
				key /path/to/root.key
			}
			intermediate {
				format pem_file
				cert /path/to/intermediate.pem
				key /path/to/intermediate.key
			}
		}
	}
}
```


<a id="event-options"></a>
## Event-Optionen

Caddy-Module geben Events aus, wenn interessante Dinge passieren (oder kurz davor sind).

Events enthalten typischerweise eine Metadata-Payload. Am besten erfährst du in der Dokumentation des jeweiligen Moduls etwas über Events und ihre Payloads; du kannst die Events und ihre Daten-Payloads aber auch sehen, indem du die globale Option [`debug`](#debug) aktivierst und die Logs liest.

##### `on`

Bindet einen Event-Handler an das benannte Event. Gib den Namen des Event-Handler-Moduls an, gefolgt von seiner Konfiguration.

Zum Beispiel, um nach dem Bezug eines Zertifikats einen Befehl auszuführen ([Drittanbieter-Plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/mholt/caddy-events-exec) erforderlich), wobei ein Teil der Event-Payload per Platzhalter an das Skript übergeben wird:

```caddy
{
	events {
		on cert_obtained exec ./my-script.sh {event.data.certificate_path}
	}
}
```

### Events

Diese Standard-Events werden von Caddy ausgegeben:

- [`tls` events <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/certmagic#events)
- [`reverse_proxy` events](/docs/caddyfile/directives/reverse_proxy#events)

Plugins können ebenfalls Events ausgeben; Details findest du in ihrer Dokumentation.
