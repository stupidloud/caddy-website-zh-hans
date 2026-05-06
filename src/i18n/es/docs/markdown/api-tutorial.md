---
title: "Tutorial de la API"
---

# API Tutorial

Este tutorial te mostrará cómo usar la [API de administración](/docs/api) de Caddy, que permite automatizar mediante programación.

**Objetivos:**
- 🔲 Ejecutar el daemon
- 🔲 Dar una configuración a Caddy
- 🔲 Probar la configuración
- 🔲 Reemplazar la configuración activa
- 🔲 Recorrer la configuración
- 🔲 Usar etiquetas `@id`

**Requisitos previos:**
- Habilidades básicas de terminal / línea de comandos
- Experiencia básica con JSON
- `caddy` y `curl` en tu PATH

---

Para iniciar el daemon de Caddy, usa el subcomando `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Ejecutar el daemon</aside>

Esto se bloquea para siempre, pero ¿qué está haciendo? En este momento... nada. Por defecto, la configuración de Caddy ("config") está vacía. Podemos verificarlo usando la [API de administración](/docs/api) desde otra terminal:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Podemos hacer que Caddy sea útil dándole una configuración. Una forma de hacerlo es haciendo una solicitud POST al endpoint [/load](/docs/api#post-load). Al igual que con cualquier solicitud HTTP, hay varias formas de hacerlo, pero en este tutorial usaremos `curl`.

## Tu primera configuración

Para preparar nuestra solicitud, necesitamos crear una configuración. La configuración de Caddy es simplemente un [documento JSON](/docs/json/) (o [cualquier cosa que se convierta en JSON](/docs/config-adapters)).

<aside class="tip">
	Los archivos de configuración no son obligatorios. La API de configuración siempre se puede usar sin archivos, lo que resulta práctico para automatizar. Este tutorial usa un archivo porque es más cómodo para editar a mano.
</aside>

Guarda esto en un archivo JSON:

```json
{
	"apps": {
		"http": {
			"servers": {
				"example": {
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
```

Después, súbelo:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	Asegúrate de no olvidar el `@` delante del nombre de archivo; esto le indica a curl que estás enviando un archivo.
</aside>

<aside class="complete">Dar una configuración a Caddy</aside>

Podemos verificar que Caddy aplicó nuestra nueva configuración con otra solicitud GET:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Comprueba que funciona yendo a [localhost:2015](http://localhost:2015) en el navegador o usando `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">Probar configuración</aside>

Si ves *Hello, world!*, entonces felicidades — está funcionando. Siempre es buena idea verificar que tu configuración funciona como esperas, especialmente antes de desplegar a producción.

Cambiemos nuestro mensaje de bienvenida de "Hello world!" a algo un poco más motivador: "I can do hard things." Haz este cambio en tu archivo de configuración, de modo que el objeto handler quede así:

```json
{
	"handler": "static_response",
	"body": "I can do hard things."
}
```

Guarda el archivo de configuración y luego actualiza la configuración activa de Caddy ejecutando otra vez la misma solicitud POST:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Reemplazar configuración activa</aside>

Por si acaso, verifica que la configuración se haya actualizado:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Pruébalo actualizando la página en el navegador (o ejecutando `curl` otra vez), y verás un mensaje inspirador.


## Recorrer la configuración

En lugar de cargar todo el archivo de configuración para un cambio pequeño, usemos una función potente de la API de Caddy para hacer el cambio sin tocar el archivo de configuración.

<aside class="tip">
	Hacer cambios pequeños en servidores de producción reemplazando toda la configuración como hicimos arriba puede ser peligroso; es como tener acceso root a un sistema de archivos. La API de Caddy te permite limitar el alcance de tus cambios para garantizar que otras partes de tu configuración no se modifiquen accidentalmente.
</aside>

Usando la ruta del URI de la solicitud, podemos recorrer la estructura de configuración y actualizar solo la cadena del mensaje (desplázate a la derecha si está recortado):

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Work smarter, not harder."'
</code></pre>


<aside class="tip">

Cada vez que cambias la configuración usando la API, Caddy conserva una copia de la nueva configuración para que puedas hacer [**--resume** más tarde](/docs/command-line#caddy-run).

</aside>


Puedes verificar que funcionó con una solicitud GET similar, por ejemplo:

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

Deberías ver:

```json
[{"handle":[{"body":"Work smarter, not harder.","handler":"static_response"}]}]
```


<aside class="tip">

Puedes usar el [comando `jq` <img src="/old/resources/images/external-link.svg" class="external-link">](https://stedolan.github.io/jq/) para formatear la salida JSON: **`curl ... | jq`**

</aside>


<aside class="complete">Recorrer configuración</aside>

**Nota importante:** esto parece obvio, pero una vez que usas la API para hacer un cambio que no está en el archivo de configuración original, ese archivo queda obsoleto. Hay algunas formas de manejar esto:

- Usa `--resume` del comando [caddy run](/docs/command-line#caddy-run) para usar la última configuración activa.
- No mezcles el uso de archivos de configuración con cambios mediante la API; mantén una sola fuente de verdad.
- [Exporta la nueva configuración de Caddy](/docs/api#get-configpath) con una solicitud GET posterior (menos recomendado que las dos primeras opciones).



## Usar `@id` en JSON

Recorrer la configuración es útil, pero las rutas son un poco largas, ¿no crees?

Podemos asignar a nuestro objeto handler un [etiqueta `@id`](/docs/api#using-id-in-json) para facilitar el acceso:

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

Esto agrega una propiedad a nuestro objeto handler: `"@id": "msg"`, y ahora se verá así:

```json
{
	"@id": "msg",
	"body": "Work smarter, not harder.",
	"handler": "static_response"
}
```


<aside class="tip">

Las etiquetas **@id** se pueden poner en cualquier objeto y pueden tener cualquier valor primitivo (normalmente una cadena). [Más información](/docs/api#using-id-in-json)

</aside>


Luego podemos acceder directamente:

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

Y ahora podemos cambiar el mensaje con una ruta más corta:

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Some shortcuts are good."'
</code></pre>

Y compruébalo de nuevo:

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete">Usar etiquetas <code>@id</code></aside>
