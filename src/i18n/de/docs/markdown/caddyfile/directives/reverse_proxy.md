---
title: reverse_proxy (Caddyfile directive)
---

<script>
ready(function() {
	// Response Matcher mit der richtigen Farbe rendern
	// und zum Abschnitt response matchers verlinken
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Matcher-Platzhalter korrigieren
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@name')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">@name</a>';
			break;
		}
	}

	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// Wir fügen Links zu allen Unterdirektiven hinzu, wenn ein passender Anker auf der Seite gefunden wird.
	addLinksToSubdirectives();
});
</script>

# reverse_proxy

Leitet Anfragen an ein oder mehrere Backends weiter, mit konfigurierbaren Optionen für Transport, Load Balancing, Health Checks, Anfrage-Manipulation und Buffering.

- [Syntax](#syntax)
- [Upstreams](#upstreams)
  - [Upstream-Adressen](#upstream-addresses)
  - [Dynamische Upstreams](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
	- [Multi](#multi)
- [Load Balancing](#load-balancing)
  - [Aktive Health Checks](#active-health-checks)
  - [Passive Health Checks](#passive-health-checks)
  - [Events](#events)
- [Streaming](#streaming)
- [Header](#headers)
- [Rewrites](#rewrites)
- [Transports](#transports)
  - [Der `http`-Transport](#the-http-transport)
  - [Der `fastcgi`-Transport](#the-fastcgi-transport)
- [Antworten abfangen](#intercepting-responses)
- [Beispiele](#examples)



<a id="syntax"></a>
## Syntax

```caddy-d
reverse_proxy [<matcher>] [<upstreams...>] {
	# Backends
	to      <upstreams...>
	dynamic <module> ...

	# Load Balancing
	lb_policy       <name> [<options...>]
	lb_retries      <retries>
	lb_try_duration <duration>
	lb_try_interval <interval>
	lb_retry_match  <request-matcher>

	# aktive Health Checks
	health_uri          <uri>
	health_upstream     <ip:port>
	health_port         <port>
	health_interval     <interval>
	health_passes       <num>
	health_fails	    <num>
	health_timeout      <duration>
	health_method       <method>
	health_status       <status>
	health_request_body <body>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<field> [<values...>]
	}

	# passive Health Checks
	fail_duration     <duration>
	max_fails         <num>
	unhealthy_status  <status>
	unhealthy_latency <duration>
	unhealthy_request_count <num>

	# Streaming
	flush_interval     <duration>
	request_buffers    <size>
	response_buffers   <size>
	stream_timeout     <duration>
	stream_close_delay <duration>

	# Anfrage-/Header-Manipulation
	trusted_proxies [private_ranges] <ranges...>
	header_up   [+|-]<field> [<value|regexp> [<replacement>]]
	header_down [+|-]<field> [<value|regexp> [<replacement>]]
	method <method>
	rewrite <to>

	# Round Trip
	transport <name> {
		...
	}

	# optional Antworten vom Upstream abfangen
	@name {
		status <code...>
		header <field> [<value>]
	}
	replace_status [<matcher>] <status_code>
	handle_response [<matcher>] {
		<directives...>

		# spezielle Direktiven, die nur in handle_response verfügbar sind
		copy_response [<matcher>] [<status>] {
			status <status>
		}
		copy_response_headers [<matcher>] {
			include <fields...>
			exclude <fields...>
		}
	}
}
```



<a id="upstreams"></a>
## Upstreams

- **&lt;upstreams...&gt;** ist eine Liste von Upstreams (Backends), an die per Proxy weitergeleitet wird.
- **to** <span id="to"/> ist eine alternative Schreibweise, um die Liste der Upstreams anzugeben, einen (oder mehrere) pro Zeile.
- **dynamic** <span id="dynamic"/> konfiguriert ein Modul für *dynamische Upstreams*. Dadurch kann die Liste der Upstreams für jede Anfrage dynamisch ermittelt werden. Eine Beschreibung der standardmäßigen dynamischen Upstream-Module finden Sie unten unter [dynamische Upstreams](#dynamic-upstreams). Dynamische Upstreams werden in jeder Iteration der Proxy-Schleife abgerufen (also potenziell mehrfach pro Anfrage, wenn Load-Balancing-Retries aktiviert sind) und gegenüber statischen Upstreams bevorzugt. Tritt ein Fehler auf, fällt der Proxy auf statisch konfigurierte Upstreams zurück.


<a id="upstream-addresses"></a>
### Upstream-Adressen

Statische Upstream-Adressen können die Form einer URL haben, die nur Schema und Host/Port enthält, oder einer konventionellen [Caddy-Netzwerkadresse](/docs/conventions#network-addresses). Gültige Beispiele:

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

Standardmäßig werden Verbindungen zum Upstream über Plaintext-HTTP hergestellt. Bei Verwendung der URL-Form kann ein Schema als Abkürzung verwendet werden, um einige [`transport`](#transports)-Standardwerte zu setzen.
- Das Schema `https://` verwendet den [`http`-Transport](#the-http-transport) mit aktiviertem [`tls`](#tls).

  Zusätzlich müssen Sie möglicherweise den `Host`-Header überschreiben, sodass er dem TLS-SNI-Wert entspricht, den Server für Routing und Zertifikatsauswahl verwenden. Details finden Sie unten im Abschnitt [HTTPS](#https).

- Das Schema `h2c://` verwendet den [`http`-Transport](#the-http-transport), wobei die [HTTP-Versionen](#versions) Cleartext-HTTP/2-Verbindungen erlauben.

- Das Schema `http://` ist identisch damit, das Schema wegzulassen, da HTTP bereits der Standard ist. Diese Syntax ist aus Symmetrie zu den anderen Schema-Abkürzungen enthalten.

Schemata können nicht gemischt werden, da sie die gemeinsame Transportkonfiguration ändern (ein TLS-aktivierter Transport kann nicht zugleich HTTPS und Plaintext-HTTP transportieren). Eine explizite Transportkonfiguration wird nicht überschrieben; ausgelassene Schemata oder andere Ports lassen keinen bestimmten Transport annehmen.

Bei IPv6 mit Zone (z. B. link-local-Adressen mit bestimmtem Netzwerkinterface) kann ein Schema **nicht** als Abkürzung verwendet werden, weil `%` einen URL-Parse-Fehler auslöst; konfigurieren Sie stattdessen den Transport explizit.

Bei Verwendung der Form [Netzwerkadresse](/docs/conventions#network-addresses) wird der Netzwerktyp als Präfix der Upstream-Adresse angegeben. Das kann nicht mit einem URL-Schema kombiniert werden. Als Sonderfall wird `unix+h2c/` als Abkürzung für das Netzwerk `unix/` plus dieselben Effekte wie das Schema `h2c://` unterstützt. Portbereiche werden als Abkürzung unterstützt und zu mehreren Upstreams mit demselben Host expandiert.

Upstream-Adressen **dürfen** keine Pfade oder Query Strings enthalten, weil das ein gleichzeitiges Umschreiben der Anfrage während des Proxyings bedeuten würde; dieses Verhalten ist nicht definiert und wird nicht unterstützt. Verwenden Sie die Direktive [`rewrite`](/docs/caddyfile/directives/rewrite), wenn Sie das benötigen.

Wenn die Adresse keine URL ist (also kein Schema hat), können [Platzhalter](/docs/caddyfile/concepts#placeholders) verwendet werden. Dadurch wird der Upstream aber *dynamisch statisch*: potenziell viele unterschiedliche Backends werden für Health Checks und Load Balancing als ein einzelner statischer Upstream behandelt. Wir empfehlen, wenn möglich stattdessen ein Modul für [dynamische Upstreams](#dynamic-upstreams) zu verwenden. Bei Platzhaltern **muss** ein Port enthalten sein (entweder durch die Platzhalterersetzung oder als statisches Suffix der Adresse).


<a id="dynamic-upstreams"></a>
### Dynamische Upstreams

Caddys Reverse Proxy bringt standardmäßig einige dynamische Upstream-Module mit. Beachten Sie, dass dynamische Upstreams Auswirkungen auf Load Balancing und Health Checks haben, abhängig von der konkreten Policy-Konfiguration: Aktive Health Checks laufen nicht für dynamische Upstreams; Load Balancing und passive Health Checks funktionieren am besten, wenn die Liste der Upstreams relativ stabil und konsistent ist (besonders bei Round-Robin). Idealerweise geben dynamische Upstream-Module nur gesunde, verwendbare Backends zurück.


<a id="srv"></a>
#### SRV

Ruft Upstreams aus SRV-DNS-Records ab.

```caddy-d
	dynamic srv [<full_name>] {
		service   <service>
		proto     <proto>
		name      <name>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
	}
```

- **&lt;full_name&gt;** ist der vollständige Domainname des abzufragenden Records (also `_service._proto.name`).
- **service** ist die Service-Komponente des vollständigen Namens.
- **proto** ist die Protokollkomponente des vollständigen Namens. Entweder `tcp` oder `udp`.
- **name** ist die Namenskomponente. Oder, wenn `service` und `proto` leer sind, der vollständig abzufragende Domainname.
- **refresh** gibt an, wie oft gecachte Ergebnisse aktualisiert werden. Standard: `1m`
- **resolvers** ist die Liste von DNS-Resolvern, welche die Systemresolver überschreiben.
- **dial_timeout** ist das Timeout für das Wählen der Abfrage.
- **dial_fallback_delay** gibt an, wie lange gewartet wird, bevor eine RFC-6555-Fast-Fallback-Verbindung gestartet wird. Standard: `300ms`



<a id="aaaaa"></a>
#### A/AAAA

Ruft Upstreams aus A/AAAA-DNS-Records ab.

```caddy-d
	dynamic a [<name> <port>] {
		name      <name>
		port      <port>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
		versions ipv4|ipv6
	}
```

- **name** ist der abzufragende Domainname.
- **port** ist der für das Backend zu verwendende Port.
- **refresh** gibt an, wie oft gecachte Ergebnisse aktualisiert werden. Standard: `1m`
- **resolvers** ist die Liste von DNS-Resolvern, welche die Systemresolver überschreiben.
- **dial_timeout** ist das Timeout für das Wählen der Abfrage.
- **dial_fallback_delay** gibt an, wie lange gewartet wird, bevor eine RFC-6555-Fast-Fallback-Verbindung gestartet wird. Standard: `300ms`
- **versions** ist die Liste der aufzulösenden IP-Versionen. Standard: `ipv4 ipv6`, entsprechend A- und AAAA-Records.


<a id="multi"></a>
#### Multi

Hängt die Ergebnisse mehrerer dynamischer Upstream-Module aneinander. Nützlich, wenn Sie redundante Upstream-Quellen möchten, zum Beispiel einen primären SRV-Cluster mit einem sekundären SRV-Cluster als Backup.

```caddy-d
	dynamic multi {
		<source> [...]
	}
```

- **&lt;source&gt;** ist der Name des Moduls für dynamische Upstreams, gefolgt von seiner Konfiguration. Mehrere können angegeben werden.




<a id="load-balancing"></a>
## Load Balancing

Load Balancing wird typischerweise verwendet, um Traffic auf mehrere Upstreams zu verteilen. Durch Aktivieren von Retries kann es auch mit einem oder mehreren Upstreams verwendet werden, um Anfragen zu halten, bis ein gesunder Upstream gewählt werden kann (z. B. um Fehler während eines Neustarts oder Redeployments eines Upstreams abzufedern).

Dies ist standardmäßig mit der Policy `random` aktiviert. Retries sind standardmäßig deaktiviert.

- **lb_policy** <span id="lb_policy"/> ist der Name der Load-Balancing-Policy samt Optionen. Standard: `random`.

  Für Policies mit Hashing wird der Algorithmus [highest-random-weight (HRW)](https://en.wikipedia.org/wiki/Rendezvous_hashing) verwendet, um sicherzustellen, dass ein Client oder eine Anfrage mit demselben Hash-Key demselben Upstream zugeordnet wird, selbst wenn sich die Liste der Upstreams ändert.

  Einige Policies unterstützen optional einen Fallback. Wenn dies angegeben ist, nehmen sie einen [Block](/docs/caddyfile/concepts#blocks) mit `fallback <policy>`, der eine weitere Load-Balancing-Policy angibt. Für diese Policies ist der Standard-Fallback `random`. Ein Fallback erlaubt, eine sekundäre Policy zu verwenden, falls die primäre keine auswählt, was leistungsfähige Kombinationen ermöglicht. Fallbacks können bei Bedarf mehrfach verschachtelt werden.

  Zum Beispiel kann `header` als primäre Policy verwendet werden, damit Entwickler einen bestimmten Upstream auswählen können, mit `first` als Fallback für alle anderen Verbindungen, um Primary/Secondary-Failover umzusetzen.
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` wählt zufällig einen Upstream.

	- `random_choose <n>` wählt zwei oder mehr Upstreams zufällig aus und nimmt dann den mit der geringsten Last (`n` ist üblicherweise 2).

	- `first` wählt den ersten verfügbaren Upstream in der Reihenfolge, in der sie in der Konfiguration definiert sind, und erlaubt so Primary/Secondary-Failover; aktivieren Sie dazu Health Checks, sonst findet kein Failover statt.

	- `round_robin` iteriert der Reihe nach über jeden Upstream.

	- `weighted_round_robin <weights...>` iteriert der Reihe nach über jeden Upstream und berücksichtigt die angegebenen Gewichte. Die Anzahl der Gewichtsargumente muss der Anzahl der konfigurierten Upstreams entsprechen. Gewichte müssen nicht-negative Ganzzahlen sein. Bei zwei Upstreams und den Gewichten `5 1` würde der erste Upstream fünfmal hintereinander ausgewählt, bevor der zweite einmal ausgewählt wird; dann wiederholt sich der Zyklus. Ein Gewicht von null deaktiviert die Auswahl des Upstreams für neue Anfragen.

	- `least_conn` wählt den Upstream mit der geringsten Anzahl aktueller Anfragen; wenn mehrere Hosts die geringste Anzahl haben, wird einer davon zufällig gewählt.

	- `ip_hash` ordnet die Remote-IP (den unmittelbaren Peer) einem sticky Upstream zu.

	- `client_ip_hash` ordnet die Client-IP einem sticky Upstream zu; dies passt am besten zur globalen Option [`servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies), die echtes Client-IP-Parsing aktiviert, andernfalls verhält es sich wie `ip_hash`.

	- `uri_hash` ordnet die Anfrage-URI (Pfad und Query) einem sticky Upstream zu.

	- `query [key]` ordnet eine Anfrage-Query einem sticky Upstream zu, indem der Query-Wert gehasht wird; wenn der angegebene Key nicht vorhanden ist, wird die Fallback-Policy zur Auswahl eines Upstreams verwendet (standardmäßig `random`).

	- `header [field]` ordnet einen Anfrageheader einem sticky Upstream zu, indem der Headerwert gehasht wird; wenn das angegebene Headerfeld nicht vorhanden ist, wird die Fallback-Policy zur Auswahl eines Upstreams verwendet (standardmäßig `random`).

	- `cookie [<name> [<secret>]]`: Bei der ersten Anfrage eines Clients (wenn kein Cookie vorhanden ist) wird die Fallback-Policy zur Auswahl eines Upstreams verwendet (standardmäßig `random`), und der Antwort wird ein `Set-Cookie`-Header hinzugefügt (Standard-Cookiename ist `lb`, wenn nicht angegeben). Der Cookie-Wert ist die Dial-Adresse des gewählten Upstreams, gehasht mit HMAC-SHA256 (mit `<secret>` als gemeinsamem Secret, leerer String wenn nicht angegeben).

	  Bei nachfolgenden Anfragen mit vorhandenem Cookie wird der Cookie-Wert demselben Upstream zugeordnet, sofern er verfügbar ist; wenn er nicht verfügbar oder nicht gefunden ist, wird mit der Fallback-Policy ein neuer Upstream ausgewählt und das Cookie der Antwort hinzugefügt.

	  Wenn Sie zu Debugging-Zwecken einen bestimmten Upstream verwenden möchten, können Sie die Upstream-Adresse mit dem Secret hashen und das Cookie in Ihrem HTTP-Client (Browser oder anders) setzen. Zum Beispiel könnten Sie mit PHP Folgendes ausführen, um den Cookie-Wert zu berechnen, wobei `10.1.0.10:8080` die Adresse eines Ihrer Upstreams und `secret` Ihr konfiguriertes Secret ist.
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```

	  Sie können das Cookie beispielsweise über die Javascript-Konsole in Ihrem Browser setzen, hier für ein Cookie namens `lb`:
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries** <span id="lb_retries"/> gibt an, wie oft für jede Anfrage erneut versucht wird, verfügbare Backends auszuwählen, wenn der nächste verfügbare Host down ist. Standardmäßig sind Retries deaktiviert (null).

  Wenn auch [`lb_try_duration`](#lb_try_duration) konfiguriert ist, können Retries vorzeitig enden, wenn die Dauer erreicht ist. Anders gesagt: Die Retry-Dauer hat Vorrang vor der Retry-Anzahl.

- **lb_try_duration** <span id="lb_try_duration"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie lange für jede Anfrage versucht wird, verfügbare Backends auszuwählen, wenn der nächste verfügbare Host down ist. Standardmäßig sind Retries deaktiviert (Dauer null).

  Clients warten bis zu dieser Dauer, während der Load Balancer versucht, einen verfügbaren Upstream-Host zu finden. Ein sinnvoller Startwert könnte `5s` sein, da das Standard-Dial-Timeout des HTTP-Transports `3s` beträgt und so mindestens ein Retry möglich sein sollte, wenn der zuerst ausgewählte Upstream nicht erreichbar ist; experimentieren Sie aber gern, um die richtige Balance für Ihren Anwendungsfall zu finden.

- **lb_try_interval** <span id="lb_try_interval"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie lange zwischen der Auswahl des nächsten Hosts aus dem Pool gewartet wird. Standard ist `250ms`. Nur relevant, wenn eine Anfrage an einen Upstream-Host fehlschlägt. Beachten Sie, dass `0` zusammen mit einer nicht-null `lb_try_duration` CPU-Spinning verursachen kann, wenn alle Backends down sind und die Latenz sehr niedrig ist.

- **lb_retry_match** <span id="lb_retry_match"/> beschränkt, für welche Anfragen Retries erlaubt sind. Eine Anfrage muss diese Bedingung erfüllen, damit sie erneut versucht wird, wenn die Verbindung zum Upstream erfolgreich war, aber der anschließende Round Trip fehlgeschlagen ist. Wenn die Verbindung zum Upstream fehlgeschlagen ist, ist ein Retry immer erlaubt. Standardmäßig werden nur `GET`-Anfragen erneut versucht.

  Die Syntax dieser Option entspricht [benannten Request Matchern](/docs/caddyfile/matchers#named-matchers), aber ohne `@name`. Wenn Sie nur einen einzelnen Matcher benötigen, können Sie ihn in derselben Zeile konfigurieren. Für mehrere Matcher ist ein Block erforderlich.



<a id="active-health-checks"></a>
### Aktive Health Checks

Aktive Health Checks prüfen die Gesundheit im Hintergrund nach Zeitplan. Zum Aktivieren ist `health_uri` oder `health_port` erforderlich.

- **health_uri** <span id="health_uri"/> ist der URI-Pfad (und optional Query) für aktive Health Checks.

- **health_upstream** <span id="health_upstream"/> ist ip:port für aktive Health Checks, wenn abweichend vom Upstream. Dies sollte zusammen mit `health_header` und `{http.reverse_proxy.active.target_upstream}` verwendet werden.

- **health_port** <span id="health_port"/> ist der Port für aktive Health Checks, wenn abweichend vom Port des Upstreams. Wird ignoriert, wenn `health_upstream` verwendet wird.

- **health_interval** <span id="health_interval"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie oft aktive Health Checks durchgeführt werden. Standard: `30s`.

- **health_passes** <span id="health_passes"/> ist die Anzahl aufeinanderfolgender erfolgreicher Health Checks, die erforderlich sind, bevor das Backend wieder als gesund markiert wird. Standard: `1`.

- **health_fails** <span id="health_fails"/> ist die Anzahl aufeinanderfolgender fehlgeschlagener Health Checks, die erforderlich sind, bevor das Backend als ungesund markiert wird. Standard: `1`.

- **health_timeout** <span id="health_timeout"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie lange auf eine Antwort gewartet wird, bevor das Backend als down markiert wird. Standard: `5s`.

- **health_method** <span id="health_method"/> ist die HTTP-Methode für den aktiven Health Check. Standard: `GET`.

- **health_status** <span id="health_status"/> ist der HTTP-Statuscode, der von einem gesunden Backend erwartet wird. Kann ein dreistelliger Statuscode sein oder eine Statuscode-Klasse, die auf `xx` endet. Zum Beispiel: `200` (der Standard) oder `2xx`.

- **health_request_body** <span id="health_request_body"/> ist ein String, der den mit dem aktiven Health Check zu sendenden Anfragebody darstellt.

- **health_body** <span id="health_body"/> ist ein Teilstring oder regulärer Ausdruck, der auf den Antwortbody eines aktiven Health Checks passen muss. Gibt das Backend keinen passenden Body zurück, wird es als down markiert.

- **health_follow_redirects** <span id="health_follow_redirects"/> bewirkt, dass der Health Check Redirects des Upstreams folgt. Standardmäßig würde eine Redirect-Antwort den Health Check als fehlgeschlagen zählen lassen.

- **health_headers** <span id="health_headers"/> erlaubt, Header für aktive Health-Check-Anfragen anzugeben. Das ist nützlich, wenn Sie den `Host`-Header ändern oder Ihrem Backend im Rahmen der Health Checks Authentifizierung bereitstellen müssen.



<a id="passive-health-checks"></a>
### Passive Health Checks

Passive Health Checks laufen inline mit tatsächlichen Proxy-Anfragen. Zum Aktivieren ist `fail_duration` erforderlich.

- **fail_duration** <span id="fail_duration"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie lange eine fehlgeschlagene Anfrage gemerkt wird. Eine Dauer > `0` aktiviert passive Health Checks; Standard ist `0` (aus). Ein sinnvoller Startwert könnte `30s` sein, um Fehlerraten und Reaktionsfähigkeit beim Wiederherstellen eines ungesunden Upstreams auszubalancieren; experimentieren Sie aber gern, um die richtige Balance für Ihren Anwendungsfall zu finden.

- **max_fails** <span id="max_fails"/> ist die maximale Anzahl fehlgeschlagener Anfragen innerhalb von `fail_duration`, die nötig ist, bevor ein Backend als down gilt; muss >= `1` sein; Standard ist `1`.

- **unhealthy_status** <span id="unhealthy_status"/> zählt eine Anfrage als fehlgeschlagen, wenn die Antwort mit einem dieser Statuscodes zurückkommt. Kann ein dreistelliger Statuscode sein oder eine Statuscode-Klasse, die auf `xx` endet, zum Beispiel `404` oder `5xx`.

- **unhealthy_latency** <span id="unhealthy_latency"/> ist ein [duration-Wert](/docs/conventions#durations), der eine Anfrage als fehlgeschlagen zählt, wenn es so lange dauert, eine Antwort zu erhalten.

- **unhealthy_request_count** <span id="unhealthy_request_count"/> ist die zulässige Anzahl gleichzeitiger Anfragen an ein Backend, bevor es als down markiert wird. Anders gesagt: Wenn ein bestimmtes Backend gerade so viele Anfragen bearbeitet, gilt es als "überlastet" und andere Backends werden bevorzugt.

  Dies sollte eine angemessen große Zahl sein; die Konfiguration bedeutet, dass der Proxy ein Limit von `unhealthy_request_count × upstreams_count` gleichzeitigen Gesamtanfragen hat, und alle Anfragen danach mit einem Fehler enden, weil keine Upstreams verfügbar sind.


<a id="events"></a>
## Events

Wenn ein Upstream von gesund zu ungesund oder umgekehrt wechselt, wird [ein Event](/docs/caddyfile/options#event-options) ausgelöst. Diese Events können andere Aktionen auslösen, etwa eine Benachrichtigung senden oder eine Meldung loggen. Die Events sind:

- `healthy` wird ausgelöst, wenn ein Upstream als gesund markiert wird, nachdem er zuvor ungesund war.
- `unhealthy` wird ausgelöst, wenn ein Upstream als ungesund markiert wird, nachdem er zuvor gesund war.

In beiden Fällen ist `host` als Metadatum im Event enthalten, um den Upstream zu identifizieren, dessen Zustand sich geändert hat. Es kann zum Beispiel mit dem `exec`-Event-Handler als Platzhalter `{event.data.host}` verwendet werden.



<a id="streaming"></a>
## Streaming

Standardmäßig buffert der Proxy die Antwort teilweise, um die Effizienz auf der Leitung zu verbessern.

Der Proxy unterstützt außerdem WebSocket-Verbindungen: Er führt die HTTP-Upgrade-Anfrage aus und überführt die Verbindung dann in einen bidirektionalen Tunnel.

<aside class="tip">

Standardmäßig werden WebSocket-Verbindungen zwangsweise geschlossen (mit einer Close-Control-Message an Client und Upstream), wenn die Konfiguration neu geladen wird. Jede Anfrage hält eine Referenz auf die Konfiguration; das Schließen alter Verbindungen ist daher nötig, um den Speicherverbrauch unter Kontrolle zu halten. Dieses Schließverhalten kann mit den Optionen [`stream_timeout`](#stream_timeout) und [`stream_close_delay`](#stream_close_delay) angepasst werden.

</aside>

- **flush_interval** <span id="flush_interval"/> ist ein [duration-Wert](/docs/conventions#durations), der anpasst, wie oft Caddy den Antwortbuffer zum Client flushen soll. Standardmäßig erfolgt kein periodisches Flushen. Ein negativer Wert (typischerweise -1) signalisiert "Low-Latency-Modus"; dieser deaktiviert Antwort-Buffering vollständig, flusht nach jedem Schreibvorgang sofort zum Client und bricht die Anfrage zum Backend nicht ab, selbst wenn der Client früh trennt. Diese Option wird ignoriert und Antworten werden sofort zum Client geflusht, wenn eine der folgenden Bedingungen auf die Antwort zutrifft:
	- `Content-Type: text/event-stream`
	- `Content-Length` ist unbekannt
	- HTTP/2 auf beiden Seiten des Proxys, `Content-Length` ist unbekannt, und `Accept-Encoding` ist entweder nicht gesetzt oder ist "identity"

- **request_buffers** <span id="request_buffers"/> veranlasst den Proxy, bis zu `<size>` Bytes aus dem Anfragebody in einen Buffer zu lesen, bevor er ihn upstream sendet. Das ist sehr ineffizient und sollte nur erfolgen, wenn der Upstream das verzögerungsfreie Lesen von Anfragebodys erfordert (was die Upstream-Anwendung beheben sollte). Akzeptiert werden alle Größenformate, die von [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) unterstützt werden.

- **response_buffers** <span id="response_buffers"/> veranlasst den Proxy, bis zu `<size>` Bytes aus dem Antwortbody in einen Buffer zu lesen, bevor sie an den Client zurückgegeben werden. Das sollte aus Performance-Gründen möglichst vermieden werden, kann aber nützlich sein, wenn das Backend engere Speichergrenzen hat. Akzeptiert werden alle Größenformate, die von [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) unterstützt werden.

- **stream_timeout** <span id="stream_timeout"/> ist ein [duration-Wert](/docs/conventions#durations), nach dem Streaming-Anfragen wie WebSockets am Ende des Timeouts zwangsweise geschlossen werden. Im Wesentlichen werden Verbindungen abgebrochen, wenn sie zu lange offen bleiben. Ein sinnvoller Startwert könnte `24h` sein, um Verbindungen zu entfernen, die älter als ein Tag sind. Standard: kein Timeout.

- **stream_close_delay** <span id="stream_close_delay"/> ist ein [duration-Wert](/docs/conventions#durations), der das zwangsweise Schließen von Streaming-Anfragen wie WebSockets verzögert, wenn die Konfiguration entladen wird; stattdessen bleibt der Stream offen, bis die Verzögerung abgelaufen ist. Anders gesagt verhindert dies, dass Streams sofort schließen, wenn Caddys Konfiguration neu geladen wird. Das kann sinnvoll sein, um eine Verbindungswelle von Clients zu vermeiden, deren Verbindungen durch das Schließen der vorherigen Konfiguration beendet wurden. Ein sinnvoller Startwert könnte `5m` sein, um Benutzern nach einem Konfigurations-Reload 5 Minuten zu geben, die Seite natürlich zu verlassen. Standard: keine Verzögerung.



<a id="headers"></a>
## Header

Der Proxy kann **Header manipulieren** zwischen sich selbst und dem Backend:

- **header_up** <span id="header_up"/> setzt, fügt hinzu (mit Präfix `+`), löscht (mit Präfix `-`) oder führt eine Ersetzung durch (mit zwei Argumenten, Suche und Ersatz) in einem Anfrageheader, der upstream zum Backend geht.

- **header_down** <span id="header_down"/> setzt, fügt hinzu (mit Präfix `+`), löscht (mit Präfix `-`) oder führt eine Ersetzung durch (mit zwei Argumenten, Suche und Ersatz) in einem Antwortheader, der downstream vom Backend kommt.

Zum Beispiel einen Anfrageheader setzen und vorhandene Werte überschreiben:

```caddy-d
header_up Some-Header "the value"
```

Einen Antwortheader hinzufügen; beachten Sie, dass ein Headerfeld mehrere Werte haben kann:

```caddy-d
header_down +Some-Header "first value"
header_down +Some-Header "second value"
```

Einen Anfrageheader löschen, damit er das Backend nicht erreicht:

```caddy-d
header_up -Some-Header
```

Alle passenden Anfrageheader mit einem Suffix-Match löschen:

```caddy-d
header_up -Some-*
```

*Alle* Anfrageheader löschen, um die gewünschten einzeln hinzuzufügen (nicht empfohlen):

```caddy-d
header_up -*
```

Eine Ersetzung per regulärem Ausdruck auf einem Anfrageheader durchführen:

```caddy-d
header_up Some-Header "^prefix-([A-Za-z0-9]*)$" "replaced-$1-suffix"
```

Die verwendete Sprache für reguläre Ausdrücke ist RE2, enthalten in Go. Siehe die [RE2-Syntaxreferenz](https://github.com/google/re2/wiki/Syntax) und den [Überblick zur Go-regexp-Syntax](https://pkg.go.dev/regexp/syntax). Der Ersatzstring wird [expandiert](https://pkg.go.dev/regexp#Regexp.Expand), sodass erfasste Werte verwendet werden können, zum Beispiel `$1` für die erste Capture Group.


<a id="defaults"></a>
### Defaults

Standardmäßig leitet Caddy eingehende Header einschließlich `Host` unverändert an das Backend weiter, mit drei Ausnahmen:

- Es setzt oder erweitert das Headerfeld [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For).
- Es setzt das Headerfeld [`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto).
- Es setzt das Headerfeld [`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host).

<span id="trusted_proxies"/> Für diese `X-Forwarded-*`-Header ignoriert der Proxy standardmäßig ihre Werte aus eingehenden Anfragen, um Spoofing zu verhindern.

Wenn Caddy nicht der erste Server ist, mit dem sich Ihre Clients verbinden (zum Beispiel wenn ein CDN vor Caddy steht), können Sie `trusted_proxies` mit einer Liste von IP-Bereichen (CIDRs) konfigurieren, von denen eingehenden Anfragen vertraut wird, korrekte Werte für diese Header gesendet zu haben.

Es wird dringend empfohlen, dies über die globale Option [`servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) statt im Proxy zu konfigurieren. Dann gilt es für alle Proxy-Handler in Ihrem Server und aktiviert zusätzlich Client-IP-Parsing.

<aside class="tip">

Wenn Sie Cloudflare vor Caddy verwenden, beachten Sie, dass Sie anfällig für Spoofing des Headers `X-Forwarded-For` sein können. Unsere Freunde bei [Authelia](https://www.authelia.com) haben einen [Workaround](https://www.authelia.com/integration/proxies/forwarded-headers/) dokumentiert, um Cloudflare so zu konfigurieren, dass eingehende Werte für diesen Header ignoriert werden.

</aside>

Zusätzlich setzt der [`http`-Transport](#the-http-transport) den Header `Accept-Encoding: gzip`, wenn er in der Anfrage des Clients fehlt. Dadurch kann der Upstream komprimierte Inhalte ausliefern, wenn er kann. Dieses Verhalten kann mit [`compression off`](#compression) im Transport deaktiviert werden.


<a id="https"></a>
### HTTPS

Da die meisten Header beim Proxying ihren ursprünglichen Wert behalten, ist es beim Proxying zu HTTPS oft nötig, den `Host`-Header mit der konfigurierten Upstream-Adresse zu überschreiben, sodass der `Host`-Header dem TLS-ServerName-Wert entspricht:

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

Seit Caddy v2.11.0 geschieht dies automatisch; es ist also nicht mehr nötig, den `Host`-Header beim Proxying zu HTTPS ausdrücklich zu überschreiben. Wenn Sie dieses Verhalten deaktivieren möchten, können Sie den `Host`-Header auf seinen ursprünglichen Wert setzen (was allerdings selten sinnvoll ist):

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

Der Header `X-Forwarded-Host` wird weiterhin [standardmäßig](#defaults) weitergegeben, sodass der Upstream ihn verwenden kann, wenn er den ursprünglichen `Host`-Headerwert kennen muss.

Dasselbe gilt, wenn TLS in Caddy terminiert und per HTTP weitergeleitet wird, ob zu einem Port oder einem Unix-Socket. Tatsächlich muss Caddy selbst den korrekten Host erhalten, wenn es Ziel von `reverse_proxy` ist. Im Unix-Socket-Fall ist `upstream_hostport` der Socket-Pfad, und der Host muss explizit gesetzt werden.



<a id="rewrites"></a>
## Rewrites

Standardmäßig führt Caddy die Upstream-Anfrage mit derselben HTTP-Methode und URI wie die eingehende Anfrage aus, sofern zuvor in der Middleware-Kette kein Rewrite durchgeführt wurde, bevor sie `reverse_proxy` erreicht.

Vor dem Proxying wird die Anfrage geklont; dadurch wird sichergestellt, dass Änderungen an der Anfrage während des Handlers nicht zu anderen Handlern durchsickern. Das ist nützlich, wenn die Verarbeitung nach dem Proxy fortgesetzt werden muss.

Zusätzlich zu [Header-Manipulationen](#headers) können Methode und URI der Anfrage geändert werden, bevor sie an den Upstream gesendet wird:

- **method** <span id="method"/> ändert die HTTP-Methode der geklonten Anfrage. Wenn die Methode auf `GET` oder `HEAD` geändert wird, wird der Body der eingehenden Anfrage von diesem Handler *nicht* upstream gesendet. Das ist nützlich, wenn ein anderer Handler den Anfragebody verbrauchen soll.
- **rewrite** <span id="rewrite"/> ändert die URI (Pfad und Query) der geklonten Anfrage. Das ähnelt der Direktive [`rewrite`](/docs/caddyfile/directives/rewrite), außer dass der Rewrite nicht über den Scope dieses Handlers hinaus bestehen bleibt.

Diese Rewrites sind oft für Muster wie "Pre-Check-Anfragen" nützlich, bei denen eine Anfrage an einen anderen Server gesendet wird, um zu entscheiden, wie die aktuelle Anfrage weiterbehandelt wird.

Zum Beispiel könnte die Anfrage an ein Authentifizierungs-Gateway gesendet werden, das entscheidet, ob die Anfrage von einem authentifizierten Benutzer stammt (z. B. eine Session-Cookie enthält) und fortgesetzt werden soll, oder ob sie stattdessen zu einer Login-Seite umgeleitet werden soll. Für dieses Muster stellt Caddy die Abkürzungsdirektive [`forward_auth`](/docs/caddyfile/directives/forward_auth) bereit, um den größten Teil der Konfigurationsvorlage zu überspringen.




<a id="transports"></a>
## Transports

Caddys Proxy-**Transport** ist austauschbar:

- **transport** <span id="transport"/> definiert, wie mit dem Backend kommuniziert wird. Standard ist `http`.


<a id="the-http-transport"></a>
### Der `http`-Transport

```caddy-d
transport http {
	read_buffer             <size>
	write_buffer            <size>
	max_response_header     <size>
	proxy_protocol          v1|v2
	dial_timeout            <duration>
	dial_fallback_delay     <duration>
	response_header_timeout <duration>
	expect_continue_timeout <duration>
	resolvers <ip...>
	tls
	tls_client_auth <automate_name> | <cert_file> <key_file>
	tls_insecure_skip_verify
	tls_curves <curves...>
	tls_timeout <duration>
	tls_trust_pool <module>
	tls_server_name <server_name>
	tls_renegotiation <level>
	tls_except_ports <ports...>
	keepalive [off|<duration>]
	keepalive_interval <interval>
	keepalive_idle_conns <max_count>
	keepalive_idle_conns_per_host <count>
	versions <versions...>
	compression off
	max_conns_per_host <count>
	network_proxy <module>
}
```

- **read_buffer** <span id="read_buffer"/> ist die Größe des Lesebuffers in Bytes. Akzeptiert werden alle Formate, die [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) unterstützt. Standard: `4KiB`.

- **write_buffer** <span id="write_buffer"/> ist die Größe des Schreibbuffers in Bytes. Akzeptiert werden alle Formate, die [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) unterstützt. Standard: `4KiB`.

- **max_response_header** <span id="max_response_header"/> ist die maximale Anzahl Bytes, die aus Antwortheadern gelesen wird. Akzeptiert werden alle Formate, die [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) unterstützt. Standard: `10MiB`.

- **proxy_protocol** <span id="proxy_protocol"/> aktiviert das [PROXY protocol](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (popularisiert durch HAProxy) auf der Verbindung zum Upstream und stellt die echten Client-IP-Daten voran. Das passt am besten zur globalen Option [`servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies), wenn Caddy hinter einem weiteren Proxy steht. Die Versionen `v1` und `v2` werden unterstützt. Verwenden Sie dies nur, wenn Sie wissen, dass der Upstream-Server das PROXY protocol parsen kann. Standardmäßig deaktiviert.

- **dial_timeout** <span id="dial_timeout"/> ist die maximale [Dauer](/docs/conventions#durations), die beim Verbinden mit dem Upstream-Socket gewartet wird. Standard: `3s`.

- **dial_fallback_delay** <span id="dial_fallback_delay"/> ist die maximale [Dauer](/docs/conventions#durations), die gewartet wird, bevor eine RFC-6555-Fast-Fallback-Verbindung gestartet wird. Ein negativer Wert deaktiviert dies. Standard: `300ms`.

- **response_header_timeout** <span id="response_header_timeout"/> ist die maximale [Dauer](/docs/conventions#durations), die auf das Lesen der Antwortheader vom Upstream gewartet wird. Standard: kein Timeout.

- **expect_continue_timeout** <span id="expect_continue_timeout"/> ist die maximale [Dauer](/docs/conventions#durations), die nach vollständigem Schreiben der Anfrageheader auf die ersten Antwortheader des Upstreams gewartet wird, wenn die Anfrage den Header `Expect: 100-continue` hat. Standard: kein Timeout.

- **read_timeout** <span id="read_timeout"/> ist die maximale [Dauer](/docs/conventions#durations), die auf den nächsten Lesevorgang vom Backend gewartet wird. Standard: kein Timeout.

- **write_timeout** <span id="write_timeout"/> ist die maximale [Dauer](/docs/conventions#durations), die auf die nächsten Schreibvorgänge zum Backend gewartet wird. Standard: kein Timeout.

- **resolvers** <span id="resolvers"/> ist eine Liste von DNS-Resolvern, welche die Systemresolver überschreiben.

- **tls** <span id="tls"/> verwendet HTTPS mit dem Backend. Dies wird automatisch aktiviert, wenn Backends mit dem Schema `https://` angegeben werden oder wenn eine der unten stehenden `tls_*`-Optionen konfiguriert ist.

- **tls_client_auth** <span id="tls_client_auth"/> aktiviert TLS-Clientauthentifizierung auf eine von zwei Arten: (1) durch Angabe eines Domainnamens, für den Caddy ein Zertifikat beziehen und erneuern soll, oder (2) durch Angabe einer Zertifikats- und Schlüsseldatei, die für TLS-Clientauthentifizierung beim Backend präsentiert wird.

- **tls_insecure_skip_verify** <span id="tls_insecure_skip_verify"/> schaltet die TLS-Handshake-Verifikation ab, wodurch die Verbindung unsicher und anfällig für Man-in-the-Middle-Angriffe wird. *Nicht in Produktion verwenden.*

- **tls_curves** <span id="tls_curves"/> ist eine Liste elliptischer Kurven, die für die Upstream-Verbindung unterstützt werden. Caddys Standardwerte sind modern und sicher; konfigurieren Sie dies nur bei spezifischen Anforderungen.

- **tls_timeout** <span id="tls_timeout"/> ist die maximale [Dauer](/docs/conventions#durations), die auf Abschluss des TLS-Handshakes gewartet wird. Standard: kein Timeout.

- **tls_trust_pool** <span id="tls_trust_pool"/> konfiguriert die Quelle vertrauenswürdiger Certificate Authorities, ähnlich der Unterdirektive [`trust_pool`](/docs/caddyfile/directives/tls#trust_pool), die in der Dokumentation der `tls`-Direktive beschrieben ist. Die Liste der Trust-Pool-Quellen, die in einer Standard-Caddy-Installation verfügbar sind, finden Sie [hier](/docs/caddyfile/directives/tls#trust-pool-providers).

- **tls_server_name** <span id="tls_server_name"/> setzt den Servernamen, der beim Verifizieren des im TLS-Handshake empfangenen Zertifikats verwendet wird. Standardmäßig wird der Host-Teil der Upstream-Adresse verwendet.

  Sie müssen dies nur überschreiben, wenn Ihre Upstream-Adresse nicht zu dem Zertifikat passt, das der Upstream wahrscheinlich verwendet. Wenn die Upstream-Adresse zum Beispiel eine IP-Adresse ist, müssen Sie hier den Hostnamen konfigurieren, den der Upstream-Server bedient.

  Ein Anfrage-Platzhalter kann verwendet werden; in diesem Fall wird für jede Anfrage ein Klon der HTTP-Transportkonfiguration verwendet, was Performance kosten kann.

- **tls_renegotiation** <span id="tls_renegotiation"/> setzt das TLS-Renegotiation-Level. TLS-Renegotiation bedeutet, nach dem ersten weitere Handshakes auszuführen. Das Level kann eines der folgenden sein:
  - `never` (Standard) deaktiviert Renegotiation.
  - `once` erlaubt einem Remote-Server, einmal pro Verbindung Renegotiation anzufordern.
  - `freely` erlaubt einem Remote-Server, wiederholt Renegotiation anzufordern.

- **tls_except_ports** <span id="tls_except_ports"/> deaktiviert TLS für Verbindungen zu Upstream-Zielen, die einen der angegebenen Ports verwenden, wenn TLS aktiviert ist. Das kann bei dynamischen Upstreams nützlich sein, wenn manche Upstreams HTTP- und andere HTTPS-Anfragen erwarten.

- **keepalive** <span id="keepalive"/> ist entweder `off` oder ein [duration-Wert](/docs/conventions#durations), der angibt, wie lange Verbindungen offen gehalten werden (Timeout). Standard: `2m`.

  ⚠️ Anfragen an HTTP/1.1-Upstreams können wegen "connection reset by peer"-Fehlern fehlschlagen, wenn die Keepalive-Dauer das Keepalive-Timeout des Upstream-Servers überschreitet. Idempotente Anfragen werden vom Go-HTTP-Transport erneut versucht, aber in anderen Fällen antwortet Caddy mit Statuscode 502.

- **keepalive_interval** <span id="keepalive_interval"/> ist die [Dauer](/docs/conventions#durations) zwischen Liveness-Probes. Standard: `30s`.

- **keepalive_idle_conns** <span id="keepalive_idle_conns"/> definiert die maximale Anzahl Verbindungen, die am Leben gehalten werden. Standard: kein Limit.

- **keepalive_idle_conns_per_host** <span id="keepalive_idle_conns_per_host"/> steuert, wenn nicht null, die maximale Anzahl inaktiver (keep-alive) Verbindungen pro Host. Standard: `32`.

- **versions** <span id="versions"/> erlaubt anzupassen, welche HTTP-Versionen unterstützt werden.

  Gültige Optionen sind: `1.1`, `2`, `h2c`, `3`.

  Standard: `1.1 2`; wenn das [Upstream-Schema](#upstream-addresses) `h2c://` ist, ist der Standard `h2c 2`.

  `h2c` aktiviert Cleartext-HTTP/2-Verbindungen zum Upstream. Dies ist eine nicht standardisierte Funktion, die nicht Gos Standard-HTTP-Transport verwendet und daher andere Funktionen ausschließt.

  `3` aktiviert HTTP/3-Verbindungen zum Upstream. ⚠️ Dies ist eine experimentelle Funktion und kann sich ändern.

- **compression** <span id="compression"/> kann verwendet werden, um Kompression zum Backend durch Setzen auf `off` zu deaktivieren.

- **max_conns_per_host** <span id="max_conns_per_host"/> begrenzt optional die Gesamtzahl der Verbindungen pro Host, einschließlich Verbindungen in Dialing-, aktiven und Idle-Zuständen. Standard: kein Limit.

- **network_proxy** <span id="network_proxy"/> gibt den Namen eines Netzwerk-Proxy-Moduls an, das für Anfragen an den Upstream-Server verwendet wird. Wenn nicht ausdrücklich konfiguriert, respektiert Caddy Proxy-Einstellungen aus Umgebungsvariablen gemäß der [Go stdlib](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment), also `HTTP_PROXY`, `HTTPS_PROXY` und `NO_PROXY`. Wenn für diesen Parameter ein Wert angegeben ist, fließen Anfragen in folgender Reihenfolge durch den Reverse Proxy: Client (Benutzer) -> `reverse_proxy` -> `network_proxy` -> Upstream. Eingebaute Module sind:
	- `none`, um die Umgebungseinstellungen von `HTTP_PROXY`, `HTTPS_PROXY` und `NO_PROXY` zu ignorieren.
	- `url <url>`, um eine einzelne URL anzugeben, welche die Umgebungskonfiguration überschreibt.

<a id="the-fastcgi-transport"></a>
### Der `fastcgi`-Transport

```caddy-d
transport fastcgi {
	root  <path>
	split <at>
	env   <key> <value>
	resolve_root_symlink
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>
	capture_stderr
}
```

- **root** <span id="root"/> ist das Root der Site. Standard: `{http.vars.root}` oder aktuelles Arbeitsverzeichnis.

- **split** <span id="split"/> ist die Stelle, an der der Pfad getrennt wird, um PATH_INFO am Ende der URI zu erhalten.

- **env** <span id="env"/> setzt eine zusätzliche Umgebungsvariable auf den angegebenen Wert. Kann mehrfach für mehrere Umgebungsvariablen angegeben werden.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> aktiviert das Auflösen des Verzeichnisses `root` auf seinen tatsächlichen Wert, indem ein symbolischer Link ausgewertet wird, falls einer existiert.

- **dial_timeout** <span id="dial_timeout"/> gibt an, wie lange beim Verbinden mit dem Upstream-Socket gewartet wird. Akzeptiert [duration-Werte](/docs/conventions#durations). Standard: `3s`.

- **read_timeout** <span id="read_timeout"/> gibt an, wie lange beim Lesen vom FastCGI-Server gewartet wird. Akzeptiert [duration-Werte](/docs/conventions#durations). Standard: kein Timeout.

- **write_timeout** <span id="write_timeout"/> gibt an, wie lange beim Senden an den FastCGI-Server gewartet wird. Akzeptiert [duration-Werte](/docs/conventions#durations). Standard: kein Timeout.

- **capture_stderr** <span id="capture_stderr"/> aktiviert das Erfassen und Loggen aller Nachrichten, die der Upstream-FastCGI-Server auf `stderr` sendet. Standardmäßig wird auf Level `WARN` geloggt. Wenn die Antwort einen Status `4xx` oder `5xx` hat, wird stattdessen Level `ERROR` verwendet. Standardmäßig wird `stderr` ignoriert.

<aside class="tip">

Wenn Sie eine moderne PHP-Anwendung ausliefern möchten, suchen Sie möglicherweise nach der Direktive [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi). Sie ist eine Abkürzung für einen Proxy mit der Direktive `fastcgi` samt den nötigen Rewrites, um `index.php` als Routing-Entrypoint zu verwenden.

</aside>



<a id="intercepting-responses"></a>
## Antworten abfangen

Der Reverse Proxy kann so konfiguriert werden, dass er Antworten vom Backend abfängt. Dazu können [Response Matcher](/docs/caddyfile/response-matchers) definiert werden (ähnlich der Syntax für Request Matcher), und die erste passende `handle_response`-Route wird aufgerufen.

Wenn ein Response Handler aufgerufen wird, wird die Antwort vom Backend nicht an den Client geschrieben. Stattdessen wird die konfigurierte `handle_response`-Route ausgeführt, und diese Route ist dafür verantwortlich, eine Antwort zu schreiben. Wenn die Route *keine* Antwort schreibt, wird die Anfrageverarbeitung mit allen Handlern fortgesetzt, die [nach](/docs/caddyfile/directives#directive-order) diesem `reverse_proxy` einsortiert sind.

- **@name** ist der Name eines [Response Matchers](/docs/caddyfile/response-matchers). Solange jeder Response Matcher einen eindeutigen Namen hat, können mehrere Matcher definiert werden. Eine Antwort kann anhand des Statuscodes sowie anhand des Vorhandenseins oder Werts eines Antwortheaders gematcht werden.

- **replace_status** <span id="replace_status"/> ändert bei passendem Matcher einfach den Statuscode der Antwort.

- **handle_response** <span id="handle_response"/> definiert die Route, die bei passendem Matcher ausgeführt wird (oder, wenn kein Matcher angegeben ist, für alle Antworten). Der erste passende Block wird angewendet. Innerhalb eines `handle_response`-Blocks können beliebige andere [Direktiven](/docs/caddyfile/directives) verwendet werden.

Zusätzlich können innerhalb von `handle_response` zwei spezielle Handler-Direktiven verwendet werden:

- **copy_response** <span id="copy_response"/> kopiert den vom Backend empfangenen Antwortbody zurück an den Client. Optional kann dabei der Statuscode der Antwort geändert werden. Diese Direktive ist [vor `respond` einsortiert](/docs/caddyfile/directives#directive-order).

- **copy_response_headers** <span id="copy_response_headers"/> kopiert die Antwortheader vom Backend zum Client, optional mit Einschluss *ODER* Ausschluss einer Liste von Headerfeldern (`include` und `exclude` können nicht beide angegeben werden). Diese Direktive ist [nach `header` einsortiert](/docs/caddyfile/directives#directive-order).

Drei Platzhalter werden innerhalb von `handle_response`-Routen verfügbar gemacht:

- `{rp.status_code}` Der Statuscode aus der Antwort des Backends.

- `{rp.status_text}` Der Statustext aus der Antwort des Backends.

- `{rp.header.*}` Die Header aus der Antwort des Backends.

Der Response Handler des Reverse Proxys kann die neue vom Proxy empfangene Antwort zurück an den Client kopieren, sie aber nicht an einen nachfolgenden Reverse Proxy weitergeben. Jede Verwendung von `reverse_proxy` erhält den Body der ursprünglichen Anfrage (oder den durch ein anderes Modul modifizierten Body).




<a id="examples"></a>
## Beispiele

Alle Anfragen per Reverse Proxy an ein lokales Backend weiterleiten:

```caddy
example.com {
	reverse_proxy localhost:9005
}
```


Alle Anfragen per [Load Balancing](#load-balancing) [zwischen 3 Backends](#upstreams) verteilen:

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```


Dasselbe, aber nur Anfragen innerhalb von `/api`, und sticky durch Verwendung der [`cookie`-Policy](#lb_policy):

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```


[Aktive Health Checks](#active-health-checks) verwenden, um festzustellen, welche Backends gesund sind, und [Retries](#lb_try_duration) bei fehlgeschlagenen Verbindungen aktivieren, sodass die Anfrage gehalten wird, bis ein gesundes Backend gefunden wurde:

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```


Einige [Transportoptionen](#transports) konfigurieren:

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```


Reverse Proxy zu einem [HTTPS-Upstream](#https) (seit v2.11.0 setzt Caddy den `Host`-Header automatisch passend zum Host des Upstreams, sodass dies nicht mehr manuell nötig ist):

```caddy
example.com {
	reverse_proxy https://example.com
}
```


Reverse Proxy zu einem HTTPS-Upstream, aber [⚠️ TLS-Verifikation deaktivieren](#tls_insecure_skip_verify). Dies wird NICHT EMPFOHLEN, weil es alle Sicherheitsprüfungen deaktiviert, die HTTPS bietet; Proxying über HTTP in privaten Netzwerken ist nach Möglichkeit vorzuziehen, weil es ein falsches Sicherheitsgefühl vermeidet:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```


Stattdessen können Sie Vertrauen zum Upstream herstellen, indem Sie dem [Zertifikat des Upstreams explizit vertrauen](#tls_trust_pool) und (optional) TLS-SNI passend zum Hostnamen im Upstream-Zertifikat setzen:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /path/to/cert.pem
			tls_server_name app.example.com
		}
	}
}
```



Vor dem Proxying ein [Pfadpräfix entfernen](handle_path); beachten Sie aber das [Subfolder-Problem <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575):

```caddy
example.com {
	handle_path /prefix/* {
		reverse_proxy localhost:9000
	}
}
```


Ein Pfadpräfix vor dem Proxying mit einem [`rewrite`](/docs/caddyfile/directives/rewrite) ersetzen:

```caddy
example.com {
	handle_path /old-prefix/* {
		rewrite /new-prefix{path}
		reverse_proxy localhost:9000
	}
}
```


Unterstützung für `X-Accel-Redirect`, also statische Dateien wie angefordert ausliefern, durch [Abfangen der Antwort](#intercepting-responses):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {rp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```


Benutzerdefinierte Fehlerseite für Upstream-Fehler, durch [Abfangen von Fehlerantworten](#intercepting-responses) anhand des Statuscodes:

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root /path/to/error/pages
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```


Backends [dynamisch](#dynamic-upstreams) aus DNS-Abfragen von [`A`/`AAAA`-Records](#aaaaa) beziehen:

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```


Backends [dynamisch](#dynamic-upstreams) aus DNS-Abfragen von [`SRV`-Records](#srv) beziehen:

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```


Die Verwendung von [aktiven Health Checks](#active-health-checks) und `health_upstream` kann hilfreich sein, wenn ein zwischengeschalteter Dienst erstellt wird, der einen gründlicheren Health Check durchführt. `{http.reverse_proxy.active.target_upstream}` kann dann als Header verwendet werden, um dem Health-Check-Dienst den ursprünglichen Upstream bereitzustellen.

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
