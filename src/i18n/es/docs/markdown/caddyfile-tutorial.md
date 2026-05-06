---
title: Tutorial de Caddyfile
---

# Tutorial de Caddyfile

Este tutorial te enseñará lo básico del [HTTP Caddyfile](/docs/caddyfile) para que puedas crear rápidamente configuraciones de sitio funcionales y con buen aspecto.

**Objetivos:**
- 🔲 Primer sitio
- 🔲 Servidor de archivos estáticos
- 🔲 Plantillas
- 🔲 Compresión
- 🔲 Varios sitios
- 🔲 Matchers
- 🔲 Variables de entorno
- 🔲 Comentarios

**Requisitos previos:**
- Habilidades básicas de terminal / línea de comandos
- Habilidades básicas de editor de texto
- `caddy` en tu PATH

---

Crea un archivo de texto nuevo llamado `Caddyfile` (sin extensión).

Lo primero que debes escribir es la [dirección](/docs/caddyfile/concepts#addresses) de tu sitio:

```caddy
localhost
```

<aside class="tip">

Si los puertos HTTP y HTTPS (80 y 443 respectivamente) son puertos privilegiados en tu sistema operativo, necesitarás ejecutar con privilegios elevados o usar un puerto más alto. Para usar un puerto alto, cambia la dirección a algo como `localhost:2015` y cambia el puerto HTTP usando la opción Caddyfile [http_port](/docs/caddyfile/options).

</aside>


Luego pulsa Enter y escribe lo que quieres que haga. Para este tutorial, haz que tu Caddyfile quede así:

```caddy
localhost

respond "Hello, world!"
```

Guárdalo y ejecuta Caddy (como es un tutorial de entrenamiento, usaremos el flag `--watch` para que los cambios en nuestro Caddyfile se apliquen automáticamente):

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

Si tienes errores de permisos, prueba usar un puerto más alto en la dirección (por ejemplo `localhost:2015`) y [cambiar el puerto HTTP](/docs/caddyfile/options), o ejecutar con privilegios elevados.

</aside>


La primera vez se te pedirá la contraseña. Esto es para que Caddy pueda servir tu sitio por HTTPS.

<aside class="tip">

Caddy sirve todos los sitios por HTTPS de forma predeterminada siempre que un host o IP forme parte de la dirección del sitio. [Automatic HTTPS](/docs/automatic-https) puede desactivarse prefijando explícitamente la dirección con `http://`.

</aside>


<aside class="complete">Primer sitio</aside>

Abre [localhost](https://localhost) en tu navegador y verás tu servidor web funcionando, ¡completo con HTTPS!

<aside class="tip">
	Es posible que tengas que reiniciar el navegador si te aparece un error de certificado la primera vez.
</aside>

Eso no es especialmente emocionante, así que cambiemos nuestra respuesta estática por un [servidor de archivos](/docs/caddyfile/directives/file_server) con listado de directorios habilitado:

```caddy
localhost

file_server browse
```

Guarda tu Caddyfile y actualiza la pestaña del navegador. Deberías ver una lista de archivos o una página HTML si existe un archivo de índice en el directorio actual.

<aside class="complete">Servidor de archivos estáticos</aside>

## Añadir funcionalidad

Hagamos algo interesante con nuestro servidor de archivos: servir una página con plantilla. Crea un archivo nuevo y pega esto:

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Tutorial de Caddy</title>
	</head>
	<body>
		Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

Guárdalo como `caddy.html` en el directorio actual y ábrelo en tu navegador: [https://localhost/caddy.html](https://localhost/caddy.html)

La salida es:

```
Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

Espera un momento. Deberíamos ver la fecha de hoy. ¿Por qué no funcionó? Porque el servidor aún no se configuró para evaluar plantillas. Es fácil de arreglar: solo añade una línea al Caddyfile para que quede así:

```caddy
localhost

templates
file_server browse
```

Guarda eso y recarga la pestaña del navegador. Deberías ver:

```
Page loaded at: {{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

Con el [módulo de templates](/docs/modules/http.handlers.templates) de Caddy puedes hacer muchas cosas útiles con archivos estáticos, como incluir otros archivos HTML, hacer subsolicitudes, establecer encabezados de respuesta, trabajar con estructuras de datos, ¡y más!

<aside class="complete">Plantillas</aside>

Es buena práctica comprimir respuestas con un algoritmo moderno y rápido. Habilitemos soporte para Gzip y Zstandard usando la directiva [`encode`](/docs/caddyfile/directives/encode):

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">Compresión</aside>

¡Este es el proceso básico para levantar un sitio semi-avanzado listo para producción!

Cuando estés listo para activar [Automatic HTTPS](/docs/automatic-https), simplemente reemplaza la dirección de tu sitio (`localhost` en este tutorial) por tu nombre de dominio. Consulta nuestra [guía rápida de HTTPS](/docs/quick-starts/https) para más información.

## Múltiples sitios

Con nuestro Caddyfile actual solo podemos tener una definición de sitio. Solo la primera línea puede ser la(s) dirección(es) del sitio, y todo el resto del archivo debe ser directivas para ese sitio.

Pero es fácil hacerlo para poder añadir más sitios.

Nuestro Caddyfile hasta ahora:

```caddy
localhost

encode
templates
file_server browse
```

es equivalente a este:

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

excepto que el segundo permite añadir más sitios.

Al encerrar nuestro bloque de sitio entre llaves `{ }` podemos definir múltiples sitios diferentes en el mismo Caddyfile.

Por ejemplo:

```caddy
:8080 {
	respond "I am 8080"
}

:8081 {
	respond "I am 8081"
}
```

Cuando envolvemos bloques de sitio entre llaves, solo aparecen [direcciones](/docs/caddyfile/concepts#addresses) fuera de las llaves y solo [directivas](/docs/caddyfile/directives) dentro.

Para múltiples sitios que comparten la misma configuración, puedes agregar más direcciones, por ejemplo:

```caddy
:8080, :8081 {
	...
}
```

Luego puedes definir tantos sitios como quieras, siempre que cada dirección sea única.

<aside class="complete">Múltiples sitios</aside>


## Matchers

Puede que queramos aplicar algunas directivas solo a ciertas solicitudes. Por ejemplo, supongamos que queremos tener un servidor de archivos y un reverse proxy, pero obviamente no podemos hacerlo para todas las solicitudes. O bien el file server escribirá una respuesta con un archivo estático, o el reverse proxy pasará la solicitud a un backend y devolverá su respuesta.

Esta configuración no funcionará como queremos (`reverse_proxy` tendrá prioridad por el [orden de directivas](/docs/caddyfile/directives#directive-order)):

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

En la práctica, puede que queramos usar el reverse proxy solo para solicitudes de API, por ejemplo solicitudes con ruta base `/api/`. Esto es fácil de hacer agregando un [token matcher](/docs/caddyfile/matchers#syntax):

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

Listo; ahora el reverse proxy tendrá prioridad para todas las solicitudes que empiecen por `/api/`.

La parte `/api/*` que acabamos de agregar se llama un **token matcher**. Puedes reconocerlo porque empieza con una barra `/` y aparece justo después de la directiva (aunque siempre puedes confirmar en la [documentación de la directiva](/docs/caddyfile/directives)).

Los matchers son muy potentes. Puedes declarar matchers con nombre y usarlos como `@name` para hacer coincidencias más allá de solo la ruta de solicitud. Dedica un momento a [aprender más sobre matchers](/docs/caddyfile/matchers) antes de continuar.

<aside class="complete">Matchers</aside>

## Variables de entorno

El adaptador de Caddyfile permite sustituir [variables de entorno](/docs/caddyfile/concepts#environment-variables) antes de analizar el Caddyfile.

Primero, define una variable de entorno (en el mismo shell donde ejecutas Caddy):

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

Luego puedes usarla así en el Caddyfile:

```caddy
{$SITE_ADDRESS}

file_server
```

Antes de que se analice el Caddyfile, se expandirá a:

```caddy
localhost:9055

file_server
```

Puedes usar variables de entorno en cualquier parte del Caddyfile y para cualquier número de tokens.

<aside class="complete">Variables de entorno</aside>


## Comentarios

Una última cosa que te será muy útil: si quieres anotar o destacar algo en tu Caddyfile, puedes usar comentarios, que comienzan con `#`:

```caddy
# esto inicia un comentario
```

<aside class="complete">Comentarios</aside>

## Para seguir leyendo

- [Conceptos de Caddyfile](/docs/caddyfile/concepts)
- [Directivas](/docs/caddyfile/directives)
- [Patrones comunes](/docs/caddyfile/patterns)
