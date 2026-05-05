---
title: log_append (Caddyfile directive)
---

# log_append

Hängt für den aktuellen Request ein Feld an das Access-Log an.

Dies sollte zusammen mit der Direktive [`log`](log) verwendet werden, die erforderlich ist, um Access Logging überhaupt zu aktivieren.

Der Wert kann ein statischer String sein oder ein [Platzhalter](/docs/caddyfile/concepts#placeholders), der zum Zeitpunkt des Requests durch den Wert des Platzhalters ersetzt wird.


<a id="syntax"></a>
## Syntax

```caddy-d
log_append [<matcher>] [<]<key> <value>
```

Standardmäßig wird das Log-Feld auf dem Rückweg durch die Middleware-Kette hinzugefügt (d. h. "late"), nachdem alle nachfolgenden Handler abgeschlossen sind (z. B. nach Handlern wie [`reverse_proxy`](reverse_proxy), [`respond`](respond) oder [`file_server`](file_server), die eine Response schreiben). So erfasst es den endgültigen Zustand von Request und Response.

Wenn `<` als Präfix des Schlüssels verwendet wird, wird er als "early" markiert. Das bedeutet, dass das Log-Feld *vor* dem Aufruf des nächsten Handlers in der Kette zu den Logs hinzugefügt wird, sodass der Request gelesen werden kann, bevor er von nachfolgenden Handlern verändert wird.

Nur für Debugging-Zwecke (nicht für Produktion) hat der Handler spezielles Verhalten, wenn der Wert einer dieser Platzhalter ist: `{http.request.body}`, `{http.request.body_base64}`, `{http.response.body}` oder `{http.response.body_base64}`. Wenn ein Request-Body-Platzhalter verwendet wird, wird der "early"-Modus implizit aktiviert und der Request-Body gepuffert. Wenn ein Response-Body-Platzhalter verwendet wird, wird Response-Buffering aktiviert, um den Response-Body zu erfassen, und das Feld wird "late" zum Log hinzugefügt, während die Response geschrieben wird.


<a id="examples"></a>
## Beispiele

In den Logs den Bereich der Site anzeigen, aus dem der Request bedient wird, entweder `static` oder `dynamic`:

```caddy
example.com {
	log

	handle /static* {
		log_append area "static"
		respond "Static response!"
	}

	handle {
		log_append area "dynamic"
		reverse_proxy localhost:9000
	}
}
```

In den Logs anzeigen, welcher Reverse-Proxy-Upstream effektiv verwendet wurde (entweder `node1`, `node2` oder `node3`) sowie die Zeit, die beim Proxying zum Upstream in Millisekunden verbracht wurde, und wie lange der Proxy-Upstream gebraucht hat, um den Response-Header zu schreiben:

```caddy
example.com {
	log

	handle {
		reverse_proxy node1:80 node2:80 node3:80 {
			lb_policy random_choose 2 
		}
		log_append upstream_host {rp.upstream.host}
		log_append upstream_duration_ms {rp.upstream.duration_ms}
		log_append upstream_latency_ms {rp.upstream.latency_ms}
	}
}
```

Ein Feld kann den Logs "early" hinzugefügt werden, indem dem Schlüssel `<` vorangestellt wird. So können Sie den Zustand des Requests erfassen, bevor er von nachfolgenden Handlern verändert wird. Zum Beispiel, um den ursprünglichen Request-Pfad zu loggen, bevor er umgeschrieben wird (auch wenn dies ein konstruiertes Beispiel ist, da der ursprüngliche Request-Pfad ohnehin bereits geloggt wird; es veranschaulicht nur den Punkt):

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /new-base{uri}
	reverse_proxy localhost:9000
}
```

Für Debugging-Zwecke Request- und Response-Bodies zu den Logs hinzufügen (nicht für Produktion, da dies die Performance beeinträchtigt und die Logs sehr laut macht). Wenn Sie erwarten, dass die Bodies Binärdaten mit nicht druckbaren Zeichen sind, können Sie stattdessen die Base64-Varianten der Platzhalter verwenden (z. B. `{http.request.body_base64}` und `{http.response.body_base64}`), die leichter zu kopieren und zu prüfen sind:

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
