---
title: "Primeros pasos"
---

# Primeros pasos

¡Bienvenido a Caddy! Este tutorial explora los conceptos básicos de uso de Caddy y te ayuda a familiarizarte con él a nivel general.

**Objetivos:**
- 🔲 Ejecutar el daemon
- 🔲 Probar la API
- 🔲 Asignar una configuración a Caddy
- 🔲 Probar la configuración
- 🔲 Crear un Caddyfile
- 🔲 Usar el config adapter
- 🔲 Iniciar con una configuración inicial
- 🔲 Comparar JSON y Caddyfile
- 🔲 Comparar API y archivos de configuración
- 🔲 Ejecutar en segundo plano
- 🔲 Recargar configuración sin downtime

**Requisitos previos:**
- Habilidades básicas de terminal / línea de comandos
- Habilidades básicas de editor de texto
- `caddy` y `curl` en tu PATH

---

**Si [instalaste Caddy](/docs/install) desde un gestor de paquetes, Caddy podría ya estar ejecutándose como servicio. Si es así, por favor detén el servicio antes de hacer este tutorial.**

Empecemos ejecutándolo:

<pre><code class="cmd bash">caddy</code></pre>

Vaya, sin subcomando, el comando `caddy` solo muestra la ayuda. Puedes usarlo en cualquier momento que olvides qué hacer.

Para iniciar Caddy como daemon, usa el subcomando `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Ejecutar el daemon</aside>

Esto se bloquea indefinidamente, pero ¿qué está haciendo? En este momento... nada. Por defecto, la configuración de Caddy ("config") está en blanco. Podemos verificarlo usando la [API de administración](/docs/api) en otra terminal:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

Esto **no** es tu sitio web: el endpoint de administración en localhost:2019 se usa para controlar Caddy y por defecto está restringido a localhost.

</aside>


<aside class="complete">Probar la API</aside>

Podemos hacer que Caddy sea útil dándole una configuración. Esto se puede hacer de muchas maneras, pero empezaremos enviando una solicitud POST al endpoint [/load](/docs/api#post-load) usando `curl` en la siguiente sección.



## Tu primera configuración

Para preparar nuestra solicitud, necesitamos crear una configuración. En esencia, la configuración de Caddy es simplemente un [documento JSON](/docs/json/).

Guárdala en un archivo JSON (por ejemplo, `caddy.json`):

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

<aside class="tip">

No estás obligado a usar archivos de configuración, pero en este tutorial sí lo haremos. La [API de administración](/docs/api) de Caddy está diseñada para uso por otros programas o scripts.

</aside>


Luego súbela:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Asignar configuración a Caddy</aside>

Podemos verificar que Caddy aplicó nuestra nueva configuración con otra solicitud GET:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Comprueba que funciona entrando a [localhost:2015](http://localhost:2015) en tu navegador o usando `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Si ves _Hello, world!_, entonces está funcionando. Siempre es buena idea comprobar que tu configuración funciona como esperas, especialmente antes de desplegar a producción.

<aside class="complete">Probar configuración</aside>


## Tu primer Caddyfile

Eso fue _bastante trabajo_ solo para un Hello World.

Otra forma de configurar Caddy es con el [**Caddyfile**](/docs/caddyfile). La misma configuración que escribimos en JSON antes se puede expresar simplemente como:

```caddy
:2015

respond "Hello, world!"
```


Guárdalo en un archivo llamado `Caddyfile` (sin extensión) en el directorio actual.

<aside class="complete">Crear un Caddyfile</aside>

Detén Caddy si ya está en ejecución (<kbd>Ctrl</kbd>+<kbd>C</kbd>), y luego ejecuta:

<pre><code class="cmd bash">caddy adapt</code></pre>

O si guardaste el Caddyfile en otro lugar o con nombre distinto de `Caddyfile`:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile</code></pre>

¡Verás salida JSON! ¿Qué pasó aquí?

Acabamos de usar un [_config adapter_](/docs/config-adapters) para convertir nuestro Caddyfile a la estructura JSON nativa de Caddy.

<aside class="complete">Usar el config adapter</aside>

Aunque podríamos tomar esa salida y hacer otra solicitud API, podemos saltar esos pasos porque el comando `caddy` puede hacerlo por nosotros. Si existe un archivo llamado Caddyfile en el directorio actual y no se especifica otra configuración, Caddy cargará el Caddyfile, lo adaptará para nosotros y lo ejecutará enseguida.

Ahora que hay un Caddyfile en la carpeta actual, hagamos `caddy run` de nuevo:

<pre><code class="cmd bash">caddy run</code></pre>

O si tu Caddyfile está en otra ruta:

<pre><code class="cmd bash">caddy run --config /path/to/Caddyfile</code></pre>

(Si se llama de otra forma y no empieza por "Caddyfile", necesitarás especificar `--adapter caddyfile`).

Ahora puedes volver a cargar tu sitio y verás que funciona.

<aside class="complete">Iniciar con configuración inicial</aside>

Como puedes ver, hay varias formas de iniciar Caddy con configuración inicial:

- Un archivo llamado Caddyfile en el directorio actual
- La opción `--config` (opcionalmente con la opción `--adapter`)
- La opción `--resume` (si previamente se cargó una configuración)


## JSON vs. Caddyfile

Ya sabes que el Caddyfile se convierte a JSON por ti.

El Caddyfile parece más fácil que JSON, pero ¿deberías usarlo siempre? Hay ventajas y desventajas en cada enfoque. La respuesta depende de tus requisitos y caso de uso.

JSON | Caddyfile
-----|----------
Fácil de generar | Fácil de redactar a mano
Fácilmente programable | Incómodo de automatizar
Extremadamente expresivo | Moderadamente expresivo
Rango completo de funcionalidades de Caddy | La mayor parte de funcionalidades de Caddy
Permite recorrer configuración | No permite recorrer dentro del Caddyfile
Cambios de configuración parciales | Solo cambios de configuración completa
Se puede exportar | No se puede exportar
Compatible con todos los endpoints de API | Compatible con algunos endpoints de API
Documentación generada automáticamente | Documentación escrita a mano
Universal | Nicho
Más eficiente | Más gasto computacional
Un poco aburrido | Un poco divertido
**Más información: [estructura JSON](/docs/json/)** | **Más información: [documentación Caddyfile](/docs/caddyfile)**

Tendrás que decidir qué es mejor para tu caso de uso.

Es importante señalar que tanto JSON como Caddyfile (y [cualquier otro config adapter soportado](/docs/config-adapters)) se pueden usar con la [API de Caddy](/docs/api). Sin embargo, para tener el rango completo de funcionalidades y de API de Caddy debes usar JSON. Si usas un config adapter, la única forma de cargar o cambiar la configuración con la API es el endpoint [/load](/docs/api#post-load).

<aside class="complete">Comparar JSON y Caddyfile</aside>


## API vs. archivos de configuración

<aside class="tip">

En la implementación, incluso los archivos de configuración pasan por los endpoints de la API de Caddy; el comando `caddy` solo envuelve esas llamadas a la API.

</aside>


También tendrás que decidir si tu flujo es basado en API o basado en CLI. (Puedes usar API y archivos de configuración en el mismo servidor, pero no lo recomendamos: lo mejor es tener una única fuente de verdad).

API | Archivos de configuración
----|-------------
Hacer cambios de configuración con solicitudes HTTP | Hacer cambios de configuración con comandos de shell
Escala fácilmente | Escala con dificultad
Difícil de gestionar manualmente | Fácil de gestionar manualmente
Realmente divertido | También divertido
**Más información: [tutorial de API](/docs/api-tutorial)** | **Más información: [tutorial de Caddyfile](/docs/caddyfile-tutorial)**

<aside class="tip">
	Gestionar manualmente la configuración de un servidor con la API es totalmente viable con herramientas adecuadas, por ejemplo cualquier aplicación cliente REST.
</aside>

La elección entre API y archivo de configuración es ortogonal al uso de adaptadores de configuración: puedes usar JSON pero guardarlo en un archivo y usar la interfaz de línea de comandos; de forma inversa, también puedes usar Caddyfile con la API.

Pero la mayoría de personas usa combinaciones JSON+API o Caddyfile+CLI.

Como puedes ver, Caddy se adapta bien a una gran variedad de casos de uso y despliegues.

<aside class="complete">Comparar API y archivos de configuración</aside>



## Iniciar, detener, ejecutar

Como Caddy es un servidor, se ejecuta indefinidamente. Eso significa que tu terminal no se libera al ejecutar `caddy run` hasta terminar el proceso (generalmente con <kbd>Ctrl</kbd>+<kbd>C</kbd>).

Aunque `caddy run` es la opción más común y suele recomendarse (especialmente al crear un servicio del sistema), también puedes usar `caddy start` para iniciar Caddy y dejarlo ejecutándose en segundo plano:

<pre><code class="cmd bash">caddy start</code></pre>

Así podrás seguir usando tu terminal, algo conveniente en ciertos entornos interactivos sin pantalla.

Entonces tendrás que detener el proceso tú mismo, porque <kbd>Ctrl</kbd>+<kbd>C</kbd> no lo detendrá:

<pre><code class="cmd bash">caddy stop</code></pre>

O usa [el endpoint /stop](/docs/api#post-stop) de la API.

<aside class="complete">Ejecutar en segundo plano</aside>


## Recargar configuración

Tu servidor puede hacer recargas/cambios de configuración sin downtime.

Todos los [endpoints API](/docs/api) que cargan o cambian configuración hacen cambios sin bloqueo ni downtime.

Sin embargo, con la CLI puede ser tentador usar <kbd>Ctrl</kbd>+<kbd>C</kbd> para detener el servidor y reiniciarlo para tomar una nueva configuración. No lo hagas: detener y arrancar el servidor es independiente de los cambios de configuración y producirá downtime.

<aside class="tip">
	Detener el servidor hará que el servicio se caiga.
</aside>

En su lugar, usa el comando [`caddy reload`](/docs/command-line#caddy-reload) para un cambio de configuración sin downtime:

<pre><code class="cmd bash">caddy reload</code></pre>

Esto realmente usa la API internamente. Cargará y, si es necesario, adaptará tu archivo de configuración a JSON, y luego reemplazará la configuración activa sin downtime.

Si hay errores al cargar la nueva configuración, Caddy vuelve a la última configuración que funcionaba.

<aside class="tip">
	Técnicamente, la nueva configuración se inicia antes de que se detenga la anterior, así que durante un breve tiempo se ejecutan ambas configuraciones. Si la nueva configuración falla, aborta con error y la anterior simplemente continúa.
</aside>

<aside class="complete">Recargar configuración sin downtime</aside>
