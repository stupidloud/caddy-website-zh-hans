---
title: Inicio rápido de HTTPS
---

# Inicio rápido de HTTPS

Esta guía mostrará cómo empezar a usar [HTTPS con gestión completa](/docs/automatic-https) en muy poco tiempo.

<aside class="tip">
	Caddy usa HTTPS para todos los sitios de forma predeterminada, siempre que en la configuración se especifique un nombre de host. Este tutorial asume que quieres poner en marcha un sitio confiable públicamente (es decir, no "localhost") con HTTPS, así que utilizaremos un dominio público y puertos externos.
</aside>

**Prerrequisitos:**
- Conocimientos básicos de terminal / línea de comandos
- Conocimientos básicos de DNS
- Un nombre de dominio público registrado
- Acceso externo a los puertos 80 y 443
- `caddy` y `curl` en tu `PATH`

---

En este tutorial, reemplaza `example.com` por tu nombre de dominio real.

Configura los registros A/AAAA de tu dominio para que apunten a tu servidor. Puedes hacerlo entrando al panel de tu proveedor de DNS y gestionando tu dominio.

Antes de continuar, verifica que los registros sean correctos con una consulta autoritativa. Reemplaza `example.com` por tu dominio, y si usas IPv6 cambia `type=A` por `type=AAAA`:

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=example.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

También asegúrate de que tu servidor sea accesible externamente en los puertos 80 y 443 desde una interfaz pública.

<aside class="tip">
	Si estás en casa o en otra red restringida, puede que necesites redirigir puertos o ajustar la configuración del firewall.
</aside>

Solo necesitamos iniciar Caddy con tu dominio en la configuración. Hay varias formas de hacerlo.

## Caddyfile

Esta es la forma más común de usar HTTPS.

Crea un archivo llamado `Caddyfile` (sin extensión) cuyo primer campo sea tu nombre de dominio, por ejemplo:

```caddy
example.com

respond "¡Hola, privacidad!"
```

Luego, desde el mismo directorio, ejecuta:

<pre><code class="cmd bash">caddy run</code></pre>

Verás que Caddy provisiona un certificado TLS y sirve tu sitio por HTTPS. Esto fue posible porque la dirección de tu sitio en el Caddyfile incluía un nombre de dominio.


## El comando `file-server`

Si solo necesitas servir archivos estáticos con HTTPS, ejecuta este comando (reemplazando `example.com` por tu dominio):

<pre><code class="cmd bash">caddy file-server --domain example.com</code></pre>

Verás que Caddy provisiona un certificado TLS y sirve tu sitio por HTTPS.


## El comando `reverse-proxy`

Si solo necesitas un reverse proxy simple sobre HTTPS (como terminador TLS), ejecuta este comando (reemplazando `example.com` y la dirección real del backend):

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to localhost:9000</code></pre>

Verás que Caddy provisiona un certificado TLS y sirve tu sitio por HTTPS.


## Configuración JSON

La regla general es que cualquier [host matcher](/docs/json/apps/http/servers/routes/match/host/) activará HTTPS automática.

Por ello, una configuración JSON como la siguiente habilitará [HTTPS automático](/docs/automatic-https) apto para producción:

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["example.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Hello, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
