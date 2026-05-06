---
title: Guía rápida de Caddyfile
---

# Guía rápida de Caddyfile

Crea un archivo de texto nuevo llamado `Caddyfile` (sin extensión).

Lo primero que escribes en un Caddyfile es la dirección de tu sitio:

```caddy
localhost
```

<aside class="tip">

Si los puertos HTTP y HTTPS (80 y 443, respectivamente) son puertos privilegiados en tu sistema operativo, necesitarás ejecutar con permisos elevados o usar puertos más altos. Para obtener permisos, ejecuta como root con `sudo -E` o usa `sudo setcap cap_net_bind_service=+ep $(which caddy)`. Alternativamente, para usar puertos más altos, cambia la dirección a algo como `localhost:2080` y modifica el puerto HTTP usando la opción [`http_port`](/docs/caddyfile/options) del Caddyfile.

</aside>

Luego pulsa Enter y escribe lo que quieres que haga, de modo que quede así:

```caddy
localhost

respond "Hello, world!"
```

Guarda esto y ejecuta Caddy desde la misma carpeta que contiene tu Caddyfile:

<pre><code class="cmd bash">caddy start</code></pre>

Probablemente te pedirá la contraseña, porque Caddy sirve todos los sitios, incluso los locales, sobre HTTPS de forma predeterminada. (¡La solicitud de contraseña debería aparecer solo la primera vez!)

<aside class="tip">

Para HTTPS local, Caddy genera automáticamente certificados y claves privadas únicas. El certificado raíz se agrega al almacén de confianza del sistema, por eso es necesario el aviso de contraseña. Esto te permite desarrollar en local sobre HTTPS sin errores de certificado.

</aside>

(Si recibes errores de permisos, es posible que debas ejecutar con privilegios elevados o elegir un puerto superior a 1023.)

Abre tu navegador en [localhost](http://localhost) o haz `curl`:

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Hello, world!</code></pre>

Puedes definir múltiples sitios en un Caddyfile encerrándolos entre llaves `{ }`. Cambia tu Caddyfile para que sea:

```caddy
localhost {
	respond "Hello, world!"
}

localhost:2016 {
	respond "Goodbye, world!"
}
```

Puedes aplicar la configuración actualizada de Caddy de dos formas, bien directamente por la API:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

o con el comando de recarga, que realiza la misma solicitud API por ti:

<pre><code class="cmd bash">caddy reload</code></pre>

Prueba tu nuevo endpoint de "goodbye" [en tu navegador](https://localhost:2016) o con `curl` para verificar que funciona:

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Goodbye, world!</code></pre>

Cuando termines de usar Caddy, asegúrate de detenerlo:

<pre><code class="cmd bash">caddy stop</code></pre>

## Lectura adicional

- [Conceptos de Caddyfile](/docs/caddyfile/concepts)
- [Directivas](/docs/caddyfile/directives)
- [Patrones comunes](/docs/caddyfile/patterns)
