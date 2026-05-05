---
title: API Quick-start
---

<a id="api-quick-start"></a>
# API Quick-start

**Voraussetzungen:**
- Grundkenntnisse im Terminal / in der Kommandozeile
- `caddy` und `curl` in deinem PATH

---

Starte zuerst Caddy:

<pre><code class="cmd bash">caddy start</code></pre>

Caddy läuft jetzt im Leerlauf mit leerer Konfiguration. Gib ihm mit `curl` eine einfache Konfiguration:

<pre><code class="cmd bash">curl localhost:2019/load \
    -H "Content-Type: application/json" \
    -d @- << EOF
    {
        "apps": {
            "http": {
                "servers": {
                    "hello": {
                        "listen": [":2015"],
                        "routes": [
                            {
                                "handle": [{
                                    "handler": "static_response",
                                    "body": "Hello, world!"
                                }]
                            }
                        ]
                    }
                }
            }
        }
    }
EOF</code></pre>

Einen POST-Body mit [Heredoc](https://en.wikipedia.org/wiki/Here_document#Unix_shells) anzugeben kann umständlich sein. Wenn du lieber Dateien verwendest, speichere das JSON in einer Datei namens `caddy.json` und verwende stattdessen diesen Befehl:

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

Lade nun [localhost:2015](http://localhost:2015) im Browser oder verwende `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Mit diesem JSON können wir auch mehrere Websites auf verschiedenen Interfaces definieren:

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				},
				"bye": {
					"listen": [":2016"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Goodbye, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

Aktualisiere dein JSON und führe den API-Request erneut aus.

Teste deinen neuen „goodbye“-Endpunkt [im Browser](http://localhost:2016) oder mit `curl`, um sicherzugehen, dass er funktioniert:

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Goodbye, world!</code></pre>

Wenn du mit Caddy fertig bist, stoppe ihn:

<pre><code class="cmd bash">caddy stop</code></pre>

Mit der API kannst du noch viel mehr tun, etwa Konfiguration exportieren oder feingranulare Änderungen an der Konfiguration vornehmen, statt immer alles komplett zu aktualisieren. Lies unbedingt das [vollständige API-Tutorial](/docs/api-tutorial), um zu lernen, wie das geht.

<a id="further-reading"></a>
## Weitere Lektüre

- [Vollständiges API-Tutorial](/docs/api-tutorial)
- [API-Dokumentation](/docs/api)
