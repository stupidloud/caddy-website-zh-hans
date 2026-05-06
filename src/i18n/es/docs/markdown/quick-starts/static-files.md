---
title: Guía rápida de archivos estáticos
---

# Inicio rápido de archivos estáticos

Esta guía muestra cómo poner en marcha rápidamente un servidor de archivos estáticos listo para producción.

**Prerrequisitos:**
- Conocimientos básicos de terminal / línea de comandos
- `caddy` en tu `PATH`
- Una carpeta que contenga tu sitio web

---

Hay dos formas sencillas de levantar un servidor de archivos rápidamente.

## Línea de comandos

En tu terminal, cambia al directorio raíz de tu sitio y ejecuta:

<pre><code class="cmd bash">caddy file-server</code></pre>

Si obtienes un error de permisos, probablemente significa que tu sistema operativo no te permite enlazar puertos bajos; usa un puerto alto:

<pre><code class="cmd bash">caddy file-server --listen :2015</code></pre>

Luego abre [localhost](http://localhost) (o [localhost:2015](http://localhost:2015)) en tu navegador para ver tu sitio.

Si no tienes un archivo `index` pero quieres mostrar un listado de archivos, usa la opción `--browse`:

<pre><code class="cmd bash">caddy file-server --browse</code></pre>

También puedes usar otra carpeta como raíz del sitio:

<pre><code class="cmd bash">caddy file-server --root ~/mysite</code></pre>



## Caddyfile

En la raíz de tu sitio, crea un archivo llamado `Caddyfile` con este contenido:

```caddy
localhost

file_server
```

Si no tienes permiso para enlazar puertos bajos, reemplaza `localhost` por `localhost:2015` (o cualquier otro puerto alto).

Luego, desde el mismo directorio, ejecuta:

<pre><code class="cmd bash">caddy run</code></pre>

Luego puedes abrir [localhost](https://localhost) (o la dirección que esté en tu configuración) para ver tu sitio.

La directiva [`file_server`](/docs/caddyfile/directives/file_server) tiene más opciones para personalizar tu sitio. Asegúrate de [recargar](/docs/command-line#caddy-reload) Caddy (o detenerlo y volver a iniciarlo) cuando cambies el Caddyfile.

Si no tienes un archivo `index` pero quieres mostrar un listado de archivos, usa el argumento `browse`:

```caddy
localhost

file_server browse
```

También puedes usar otra carpeta como raíz del sitio:

```caddy
localhost

root /var/www/mysite
file_server
```
