---
title: "Inicio rápido de la API"
---

# Inicio rápido de la API

**Prerrequisitos:**
- Conocimientos básicos de terminal / línea de comandos
- `caddy` y `curl` en tu `PATH`

---

Primero inicia Caddy:

<pre><code class="cmd bash">caddy start</code></pre>

Caddy está ejecutándose ahora en estado inactivo (con una configuración en blanco). Dale una configuración simple con `curl`:

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

Crear un cuerpo POST con [Heredoc](https://en.wikipedia.org/wiki/Here_document#Unix_shells) puede ser tedioso, así que si prefieres usar archivos, guarda el JSON en un archivo llamado `caddy.json` y usa este comando en su lugar:

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

Ahora carga [localhost:2015](http://localhost:2015) en tu navegador o usa `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

También podemos definir múltiples sitios en diferentes interfaces con este JSON:

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

Actualiza tu JSON y realiza la solicitud de API otra vez.

Prueba tu nuevo endpoint "goodbye" [en tu navegador](http://localhost:2016) o con `curl` para comprobar que funciona:

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Goodbye, world!</code></pre>

Cuando termines de usar Caddy, asegúrate de detenerlo:

<pre><code class="cmd bash">caddy stop</code></pre>

Puedes hacer mucho más con la API, incluida la exportación de la configuración y realizar cambios granulares en ella (en lugar de actualizarla por completo). Lee el [tutorial completo de la API](/docs/api-tutorial) para aprenderlo.

## Lectura adicional

- [Tutorial completo de la API](/docs/api-tutorial)
- [Documentación de la API](/docs/api)
