---
title: Guía rápida de proxy inverso
---

# Guía rápida de proxy inverso

Esta guía muestra cómo poner en marcha un proxy inverso listo para producción con o sin HTTPS rápidamente.

**Requisitos previos:**
- Conocimientos básicos de terminal / línea de comandos
- `caddy` en tu PATH
- Un proceso backend en ejecución al que hacer proxy

---

Este tutorial asume que tienes un servicio HTTP backend ejecutándose en `127.0.0.1:9000`. Estos comandos son para Linux, pero los mismos principios se aplican a otros sistemas operativos.

Puedes iniciar un proxy inverso simple sin archivo de configuración, o usar un archivo de configuración para mayor flexibilidad y control.


## Línea de comandos

Para iniciar un proxy HTTP sin cifrado desde el puerto 2080 al puerto 9000 en tu máquina:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

Luego pruébalo:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

El comando [`reverse-proxy`](/docs/command-line#reverse-proxy) está pensado para proxys inversos rápidos y simples. (Puedes usarlo en producción si tus requisitos son sencillos.)

## Caddyfile

En el directorio de trabajo actual, crea un archivo llamado `Caddyfile` con este contenido:

```caddy
:2080

reverse_proxy :9000
```

Ese archivo de configuración es aproximadamente equivalente al comando `caddy reverse-proxy` anterior.

Luego, desde el mismo directorio, ejecuta:

<pre><code class="cmd bash">caddy run</code></pre>

Después prueba tu proxy:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Si cambias el Caddyfile, asegúrate de [recargar](/docs/command-line#caddy-reload) Caddy.

Este era un ejemplo simple. Puedes hacer mucho más con la [directiva `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

## HTTPS desde el cliente al proxy

Caddy servirá tu proxy sobre [HTTPS automáticamente y por defecto](/docs/automatic-https) si conoce el nombre de host (dominio). El comando `caddy reverse-proxy` usará `localhost` de forma predeterminada si omites la marca `--from`, o puedes reemplazar la primera línea de tu Caddyfile con el nombre de dominio del proxy.

- Si usas `localhost` o cualquier dominio que termine en `.localhost`, Caddy usará un certificado auto-firmado de renovación automática. La primera vez que hagas esto, es posible que debas introducir una contraseña porque Caddy intenta instalar el certificado raíz de su CA en tu almacén de confianza.
- Si usas cualquier otro nombre de dominio, Caddy intentará obtener un certificado de confianza pública; asegúrate de que tus registros DNS apunten a tu máquina y de que los puertos 80 y 443 estén abiertos públicamente y dirigidos a Caddy.

Si no especificas un puerto, Caddy usa 443 para HTTPS por defecto. En ese caso también necesitarás permiso para enlazar puertos bajos. Algunas formas de hacerlo en Linux:

- Ejecutar como root (por ejemplo, `sudo -E`).
- O ejecutar `sudo setcap cap_net_bind_service=+ep $(which caddy)` para darle a Caddy esta capacidad específica.

Este es el comando `caddy reverse-proxy` más básico que te da HTTPS:

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

Luego pruébalo:

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

Puedes personalizar el nombre de host usando la marca `--from`:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

Si no tienes permiso para enlazar puertos bajos, puedes hacer proxy desde un puerto más alto:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

Si estás usando un Caddyfile, simplemente cambia la primera línea por tu nombre de dominio, por ejemplo:

```caddy
example.com

reverse_proxy :9000
```

## HTTPS del proxy al backend

Caddy también puede hacer proxy usando HTTPS entre él y el backend si este soporta TLS. Solo usa `https://` en la dirección del backend:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

Esto requiere que el certificado del backend sea de confianza para el sistema donde se ejecuta Caddy. (Caddy no confía en certificados auto-firmados a menos que se configure explícitamente para hacerlo.)

Por supuesto, también puedes usar HTTPS en ambos extremos:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

Esto sirve HTTPS desde el cliente al proxy y del proxy al backend.

Si el nombre de host al que haces proxy es distinto del que haces proxy de entrada, deberás usar la marca `--change-host-header`:

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

Por defecto, Caddy reenvía todas las cabeceras HTTP sin cambios, incluido `Host`, y Caddy obtiene el `ServerName` de TLS a partir del encabezado Host. La opción `--change-host-header` restablece el encabezado Host al del backend para que el handshake TLS pueda completarse correctamente. En el ejemplo anterior, se cambiaría de `example.com` a `localhost:9000` (y se usaría `localhost` en el handshake TLS).
