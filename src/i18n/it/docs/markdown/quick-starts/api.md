---
title: Avvio rapido all'API
---

# Avvio rapido all'API

**Prerequisiti:**
- Competenze di base del terminale / riga di comando
- `caddy` e `curl` nel vostro PATH

---

Per prima cosa, avviate Caddy:

<pre><code class="cmd bash">caddy start</code></pre>

Caddy è attualmente in esecuzione a riposo (con una configurazione vuota). Fornitegli una semplice configurazione con `curl`:

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
                                    "body": "Ciao, mondo!"
                                }]
                            }
                        ]
                    }
                }
            }
        }
    }
EOF</code></pre>

Fornire un corpo POST con un [Heredoc](https://it.wikipedia.org/wiki/Heredoc) può essere noioso, quindi se preferite usare i file, salvate il JSON in un file chiamato `caddy.json` e poi usate invece questo comando:

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

Ora caricate [localhost:2015](http://localhost:2015) nel vostro browser o usate `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Ciao, mondo!</code></pre>

Possiamo anche definire più siti su interfacce diverse con questo JSON:

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
								"body": "Ciao, mondo!"
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
								"body": "Arrivederci, mondo!"
							}]
						}
					]
				}
			}
		}
	}
}
```

Aggiornate il vostro JSON e poi eseguite nuovamente la richiesta API.

Provate il vostro nuovo endpoint "arrivederci" [nel vostro browser](http://localhost:2016) o con `curl` per assicurarvi che funzioni:

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Arrivederci, mondo!</code></pre>

Quando avrete finito con Caddy, assicuratevi di fermarlo:

<pre><code class="cmd bash">caddy stop</code></pre>

C'è molto altro che potete fare con l'API, inclusa l'esportazione della configurazione e l'apporto di modifiche granulari alla configurazione (anziché aggiornare l'intero documento). Assicuratevi di leggere il [tutorial completo sull'API](/docs/api-tutorial) per imparare come fare!

## Letture consigliate

- [Tutorial completo sull'API](/docs/api-tutorial)
- [Documentazione dell'API](/docs/api)
