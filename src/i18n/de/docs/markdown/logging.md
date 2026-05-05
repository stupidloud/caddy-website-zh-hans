---
title: Wie Logging funktioniert
---

Wie Logging funktioniert
========================

Caddy hat leistungsfähige und flexible Logging-Funktionen, die sich aber möglicherweise von dem unterscheiden, was du gewohnt bist, besonders wenn du aus älterem Shared Hosting oder von anderen Legacy-Webservern kommst.


<a id="overview"></a>
## Überblick

Logging hat zwei Hauptaspekte: Emission und Consumption.

**Emission** bedeutet, Meldungen zu erzeugen. Sie besteht aus drei Schritten:

1. Relevante Informationen sammeln (Kontext)
2. Eine nützliche Repräsentation aufbauen (Encoding)
3. Diese Repräsentation an ein Ziel senden (Writing)

Diese Funktionalität ist in Caddys Core eingebaut, sodass jeder Teil der Caddy-Codebasis und auch Module (Plugins) Logs ausgeben können.

**Consumption** ist die Aufnahme und Verarbeitung von Meldungen. Damit ausgegebene Logs nützlich sind, müssen sie konsumiert werden. Logs, die nur geschrieben, aber nie gelesen werden, haben keinen Wert. Logs zu konsumieren kann so einfach sein wie ein Administrator, der Konsolenausgabe liest, oder so fortgeschritten wie ein Log-Aggregation-Tool oder Cloud-Dienst, der Logmeldungen filtert, zählt und indexiert.

<a id="caddys-role"></a>
### Caddys Rolle

*Caddy ist ein Log-Emitter*. Caddy konsumiert Logs nicht, abgesehen von der minimalen Verarbeitung, die nötig ist, um Logs zu encoden und zu schreiben. Das ist wichtig, weil es Caddys Core einfacher hält, zu weniger Bugs und Randfällen führt und den Wartungsaufwand reduziert. Letztlich liegt Log-Verarbeitung außerhalb des Umfangs von Caddys Core.

Es besteht allerdings immer die Möglichkeit für ein Caddy-App-Modul, das Logs konsumiert. Soweit wir wissen, existiert so eines nur noch nicht.


<a id="structured-logs"></a>
## Strukturierte Logs

Wie bei den meisten modernen Anwendungen sind Caddys Logs *strukturiert*. Das bedeutet, dass die Informationen in einer Meldung nicht einfach ein undurchsichtiger String oder Byte-Slice sind. Stattdessen bleiben Daten stark typisiert und werden bis zum Encoden und Schreiben der Meldung über einzelne *Feldnamen* adressiert.

Vergleiche traditionelle unstrukturierte Logs&mdash;wie das archaische Common Log Format (CLF)&mdash;das häufig bei traditionellen HTTP-Servern verwendet wird:

```
127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.1" 200 2326
```

Dieses Format „hat Struktur“, ist aber nicht „strukturiert“: Es kann nur zum Loggen von HTTP-Requests verwendet werden. Es gibt keinen effizienten Weg, es anders zu encoden, weil es ein undurchsichtiger Byte-String ist. Außerdem fehlen viele Informationen. Es enthält nicht einmal den Host-Header des Requests. Dieses Logformat ist nur nützlich, wenn eine einzelne Site gehostet wird und nur grundlegendste Informationen über Requests benötigt werden.

<aside class="tip">
	Das Fehlen von Host-Informationen in CLF ist der Grund, warum diese Logs beim Hosten mehrerer Sites normalerweise in getrennte Dateien geschrieben werden müssen: Anders lässt sich der Host-Header des Requests nicht erkennen.
</aside>

Vergleiche nun eine gleichwertige strukturierte Logmeldung von Caddy, als JSON encoded und für die Anzeige schön formatiert:

```json
{
	"level": "info",
	"ts": 1646861401.5241024,
	"logger": "http.log.access",
	"msg": "handled request",
	"request": {
		"remote_ip": "127.0.0.1",
		"remote_port": "41342",
		"client_ip": "127.0.0.1",
		"proto": "HTTP/2.0",
		"method": "GET",
		"host": "localhost",
		"uri": "/",
		"headers": {
			"User-Agent": ["curl/7.82.0"],
			"Accept": ["*/*"],
			"Accept-Encoding": ["gzip, deflate, br"],
		},
		"tls": {
			"resumed": false,
			"version": 772,
			"cipher_suite": 4865,
			"proto": "h2",
			"server_name": "example.com"
		}
	},
	"bytes_read": 0,
	"user_id": "",
	"duration": 0.000929675,
	"size": 10900,
	"status": 200,
	"resp_headers": {
		"Server": ["Caddy"],
		"Content-Encoding": ["gzip"],
		"Content-Type": ["text/html; charset=utf-8"],
		"Vary": ["Accept-Encoding"]
	}
}
```

Du siehst, dass das strukturierte Log deutlich nützlicher ist und viel mehr Informationen enthält. Die Fülle an Informationen in dieser Logmeldung ist nicht nur nützlich, sie verursacht praktisch keinen Performance-Overhead: Caddys Logs sind zero-allocation. Strukturierte Logs haben keine Einschränkungen bei Datentypen oder Kontext: Sie können in jedem Codepfad verwendet werden und jede Art von Information enthalten.

Weil die Logs strukturiert und stark typisiert sind, können sie in jedes Format encoded werden. Wenn du also nicht mit JSON arbeiten möchtest, können Logs in eine andere Repräsentation encoded werden. Caddy unterstützt weitere Formate über [log encoder modules](/docs/json/logging/logs/encoder/), und noch mehr können hinzugefügt werden.

**Am wichtigsten** bei der Unterscheidung zwischen strukturierten Logs und Legacy-Formaten ist: Mit einem Performance-Aufwand kann ein strukturiertes Log [in das Legacy Common Log Format transformiert werden <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder), aber nicht umgekehrt. Von CLF zu strukturierten Formaten zu gelangen ist nicht trivial oder zumindest ineffizient, und wegen der fehlenden Informationen teilweise unmöglich.

Im Kern fördert effizientes, strukturiertes Logging im Allgemeinen diese Prinzipien:

- Zu viele Logs sind besser als zu wenige
- Filtern ist besser als Verwerfen
- Encoding aufschieben bringt mehr Flexibilität und Interoperabilität


<a id="emission"></a>
## Emission

Im Code sieht eine Log-Emission ungefähr so aus:

```go
logger.Debug("proxy roundtrip",
	zap.String("upstream", di.Upstream.String()),
	zap.Object("request", caddyhttp.LoggableHTTPRequest{Request: req}),
	zap.Object("headers", caddyhttp.LoggableHTTPHeader(res.Header)),
	zap.Duration("duration", duration),
	zap.Int("status", res.StatusCode),
)
```

<aside class="tip">
	Dies ist eine echte Codezeile aus Caddys Reverse Proxy. Diese Zeile ermöglicht dir, Requests zu konfigurierten upstreams zu untersuchen, wenn Debug-Logging aktiviert ist. Bei der Fehlerbehebung ist das ein unschätzbar wertvoller Datensatz.
</aside>

Du siehst, dass dieser eine Funktionsaufruf das Log-Level, eine Meldung und mehrere Datenfelder enthält. All dies ist stark typisiert, und Caddy verwendet eine zero-allocation Logging-Bibliothek, sodass Log-Emissionen schnell und effizient sind und fast keinen Overhead verursachen.

Die Variable `logger` ist ein `zap.Logger`, dem beliebig viel Kontext zugeordnet sein kann, einschließlich eines Namens und Datenfeldern. Dadurch können Logger sehr gut von Parent-Kontexten „erben“, was fortgeschrittenes Tracing und Metrics ermöglicht.

Von dort wird die Meldung durch eine hocheffiziente Verarbeitungspipeline geschickt, in der sie encoded und geschrieben wird.


<a id="logging-pipeline"></a>
## Logging-Pipeline

Wie du oben gesehen hast, werden Meldungen von **Loggern** ausgegeben. Die Meldungen werden dann zur Verarbeitung an **Logs** gesendet.

Caddy lässt dich [mehrere Logs konfigurieren](/docs/json/logging/logs/), die Meldungen verarbeiten können. Ein Log besteht aus einem Encoder, Writer, Mindest-Level, Sampling-Verhältnis und einer Liste von Loggern, die ein- oder ausgeschlossen werden. In Caddy gibt es immer ein Standard-Log namens `default`. Du kannst es anpassen, indem du in [diesem Objekt](/docs/json/logging/logs/) der Konfiguration ein Log mit dem Schlüssel `"default"` angibst.

<aside class="tip">

Jetzt ist ein guter Zeitpunkt, [Caddys Logging-Dokumentation zu erkunden](/docs/json/logging/), damit du mit der Struktur und den Parametern vertraut wirst, über die wir sprechen.

</aside>


- **Encoder:** Das Format des Logs. Wandelt die In-Memory-Datenrepräsentation in einen Byte-Slice um. Encoder haben Zugriff auf alle Felder einer Logmeldung.
- **Writer:** Die Log-Ausgabe. Kann jedes log writer module sein, zum Beispiel eine Datei oder ein Netzwerk-Socket. Es schreibt einfach Bytes.
- **Level:** Logs haben verschiedene Level, von DEBUG bis FATAL. Meldungen unterhalb des angegebenen Levels werden vom Log ignoriert.
- **Sampling:** Extrem heiße Pfade können mehr Logs ausgeben, als effektiv verarbeitet werden können; Sampling zu aktivieren ist eine Möglichkeit, die Last zu reduzieren und trotzdem eine repräsentative Stichprobe von Meldungen zu erhalten.
- **Include/exclude:** Jede Meldung wird von einem Logger ausgegeben, der einen Namen hat, meist abgeleitet von der Modul-ID. Logs können Meldungen bestimmter Logger einschließen oder ausschließen.

Wenn eine Logmeldung von Caddy ausgegeben wird:

- Der Name des ursprünglichen Loggers wird gegen die Include/Exclude-Liste jedes Logs geprüft; wenn er eingeschlossen ist oder nicht ausgeschlossen wird, wird er in dieses Log aufgenommen.
- Wenn Sampling aktiviert ist, bestimmt eine schnelle Berechnung, ob die Logmeldung behalten wird.
- Die Meldung wird mit dem konfigurierten Encoder des Logs encoded.
- Die encoded Bytes werden dann an den konfigurierten Writer des Logs geschrieben.

Standardmäßig gehen alle Meldungen an alle konfigurierten Logs. Das folgt den oben beschriebenen Werten des strukturierten Loggings. Du kannst begrenzen, welche Meldungen an welche Logs gehen, indem du Include/Exclude-Listen setzt, aber das ist hauptsächlich zum Filtern von Meldungen aus verschiedenen Modulen gedacht; es soll nicht wie ein Log-Aggregation-Dienst verwendet werden. Um Caddys Logging-Pipeline schlank und effizient zu halten, wird fortgeschrittene Verarbeitung von Logmeldungen der Consumption überlassen.

<a id="consumption"></a>
## Consumption

Nachdem Meldungen an eine Ausgabe gesendet wurden, liest ein Consumer sie ein, parst sie und behandelt sie entsprechend.

Das ist ein ganz anderer Problembereich als das Ausgeben von Logs, und Caddys Core übernimmt keine Consumption, auch wenn ein Caddy-App-Modul das durchaus könnte. Es gibt zahlreiche Tools, mit denen du Streams von JSON-Meldungen oder anderen Formaten verarbeiten und Logs anzeigen, filtern, indexieren und abfragen kannst. Du könntest sogar dein eigenes schreiben oder implementieren.

Wenn du zum Beispiel Legacy-Software betreibst, die CLF nach einem bestimmten Feld, etwa Hostname, in verschiedene Dateien getrennt benötigt, könntest du ein einfaches Tool verwenden oder schreiben, das JSON einliest, mit `sprintf()` einen CLF-String erstellt und ihn dann basierend auf dem Wert im Feld `request.host` in eine Datei schreibt.

Caddys Logging-Funktionen können auch zum Implementieren von Metrics und Tracing verwendet werden: Metrics zählen im Grunde Meldungen mit bestimmten Eigenschaften, und Tracing verknüpft mehrere Meldungen anhand gemeinsamer Merkmale.

Es gibt unzählige Möglichkeiten, was du durch das Konsumieren von Caddys Logs tun kannst.
