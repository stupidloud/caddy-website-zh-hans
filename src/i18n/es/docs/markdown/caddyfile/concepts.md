---
title: Conceptos del Caddyfile
---

# Conceptos de Caddyfile

Este documento te ayuda a aprender en detalle el Caddyfile HTTP.

1. [Estructura](#structure)
	- [Bloques](#blocks)
	- [Directivas](#directives)
	- [Tokens y comillas](#tokens-and-quotes)
2. [Opciones globales](#global-options)
3. [Direcciones](#addresses)
4. [Matchers](#matchers)
5. [Placeholders](#placeholders)
6. [Snippets](#snippets)
7. [Rutas con nombre](#named-routes)
8. [Comentarios](#comments)
9. [Variables de entorno](#environment-variables)



## Structure

La estructura del Caddyfile se puede describir visualmente:

<style>
	:root {
		--struct-border-global: #e74c3c;
		--struct-border-snippet: #2ecc71;
		--struct-border-site: #3498db;
		--struct-border-matcher: #d453d4;
		--struct-bg-1: #edf5fd;
		--struct-bg-2: #f8fbfd;
		--struct-bg-end: 100%;
		--struct-fg: #254048;
		--struct-opt-name-bg: #ffd9dd;
		--struct-opt-name-fg: #7a2a39;
		--struct-opt-value-bg: #f4dec6;
		--struct-opt-value-fg: #5a3723;
		--struct-comment-bg: #d2d7d8;
		--struct-comment-fg: #495456;
		--struct-site-addr-bg: #cbe4f2;
		--struct-site-addr-fg: #1f6f9a;
		--struct-directive-bg: #c8f7d6;
		--struct-directive-fg: #14663a;
		--struct-matcher-token-bg: #ffd6ff;
		--struct-matcher-token-fg: #6f2070;
		--struct-arg-bg: #ded0ff;
		--struct-arg-fg: #4b2f7a;
		--struct-subdir-bg: #dbbca2;
		--struct-subdir-fg: #5b3a25;
	}
	html.dark {
		--struct-border-global: #e74c3c;
		--struct-border-snippet: #2ecc71;
		--struct-border-site: #3498db;
		--struct-border-matcher: #d453d4;
		--struct-bg-1: #0d313c;
		--struct-bg-2: transparent;
		--struct-bg-end: 120%;
		--struct-fg: #cbd6da;
		--struct-opt-name-bg: #6b2630;
		--struct-opt-name-fg: #ffd9dd;
		--struct-opt-value-bg: #68412b;
		--struct-opt-value-fg: #f4dec6;
		--struct-comment-bg: #2f424d;
		--struct-comment-fg: #e8eef0;
		--struct-site-addr-bg: #204d59;
		--struct-site-addr-fg: #d6f0ff;
		--struct-directive-bg: #1f4e36;
		--struct-directive-fg: #c8f7d6;
		--struct-matcher-token-bg: #65305a;
		--struct-matcher-token-fg: #ffd6ff;
		--struct-arg-bg: #3b2e46;
		--struct-arg-fg: #ded0ff;
		--struct-subdir-bg: #6a4a2e;
		--struct-subdir-fg: #ebc095;
	}
	/* color variables - easy to tweak */
	.struct-caddyfile-visual-repl {
		display: block;
		margin: 0;
		padding: 0;
	}
	/* default (light) visual background */
	.struct-caddyfile-visual-repl .struct-visual {
		box-sizing: border-box;
		margin: 0 0 1.25rem;
		padding: 14px;
		border-radius: 14px;
		background: linear-gradient(to bottom, var(--struct-bg-1) 0%, var(--struct-bg-2) var(--struct-bg-end));
		color: var(--struct-fg);
		font-family: Inter, 'Source Sans Pro', Arial, system-ui, sans-serif;
		line-height: 1.2;
	}
	/* layout */
	.struct-caddyfile-visual-repl .struct-panel {
		display: flex;
		gap: 18px;
		align-items: flex-start;
		flex-wrap: wrap;
	}
	.struct-caddyfile-visual-repl .struct-diagram {
		flex: 1;
		padding: 8px 8px;
	}
	.struct-caddyfile-visual-repl .struct-legend {
		width: 310px;
		padding: 12px 4px;
	}
	/* code-like box: use normal whitespace so HTML pretty-printing won't leak source indentation */
	.struct-caddyfile-visual-repl .struct-code-box {
		background: transparent;
		border-radius: 8px;
		padding: 6px 6px !important;
		font-family: var(--monospace-fonts);
		font-size: 90%;
		white-space: normal;
	}
	.struct-block {
		border-radius: 8px;
		padding: 10px;
		margin: 0 0 10px 0;
	}
	.struct-block.global {
		border: 4px solid var(--struct-border-global);
	}
	.struct-block.snippet {
		border: 4px solid var(--struct-border-snippet);
	}
	.struct-block.site {
		border: 4px solid var(--struct-border-site);
	}
	.struct-block.matcher {
		border: 4px solid var(--struct-border-matcher);
		margin: 8px 8px 10px 10px;
		padding: 8px;
		border-radius: 6px;
	}
	.struct-token, .struct-opt-name, .struct-opt-value, .struct-comment, .struct-site-addr, .struct-directive, .struct-matcher-token, .struct-arg, .struct-subdir {
		display: inline !important;
		padding: .03rem .18rem !important;
		border-radius: 6px;
		font-family: var(--monospace-fonts);
		font-size: 95%;
		vertical-align: middle;
	}
	.struct-opt-name {
		background: var(--struct-opt-name-bg);
		color: var(--struct-opt-name-fg);
	}
	.struct-opt-value {
		background: var(--struct-opt-value-bg);
		color: var(--struct-opt-value-fg);
	}
	.struct-comment {
		background: var(--struct-comment-bg);
		color: var(--struct-comment-fg);
	}
	.struct-site-addr {
		background: var(--struct-site-addr-bg);
		color: var(--struct-site-addr-fg);
	}
	.struct-directive {
		background: var(--struct-directive-bg);
		color: var(--struct-directive-fg);
	}
	.struct-matcher-token {
		background: var(--struct-matcher-token-bg);
		color: var(--struct-matcher-token-fg);
	}
	.struct-arg {
		background: var(--struct-arg-bg);
		color: var(--struct-arg-fg);
	}
	.struct-subdir {
		background: var(--struct-subdir-bg);
		color: var(--struct-subdir-fg);
	}
	.struct-legend .struct-legend-title {
		font-weight: 700;
		font-size: 1.6rem;
	}
	.struct-legend .struct-item {
		display: flex;
		align-items: center;
		gap: 10px;
		margin: 16px 0;
	}
	.struct-legend .struct-item-spacer {
		height: 8px;
	}
	/* swatch for border-based legend items (blocks) */
	.struct-legend .struct-swatch-border {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		border: 4px solid transparent;
		background: transparent;
	}
	/* swatch for filled legend items (text backgrounds) */
	.struct-legend .struct-swatch-fill {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		background: transparent;
	}
	.struct-legend .struct-label {
		font-size: 90%;
		color: inherit;
	}
	.struct-caddyfile-visual-repl .struct-visual, .struct-caddyfile-visual-repl .struct-panel, .struct-caddyfile-visual-repl .struct-diagram, .struct-caddyfile-visual-repl .struct-legend, .struct-caddyfile-visual-repl .struct-code-box {
		margin: 0;
	}
	/* force compact vertical rhythm and explicit indenting so global CSS can't leak in
		NOTE: use normal whitespace so server-side HTML formatting doesn't create visible gaps */
	.struct-line {
		display: block !important;
		margin: 0 !important;
		padding: 2px 0 !important;
		line-height: 1.2 !important;
		white-space: normal !important;
	}
	/* helper to visually indent lines (do not rely on source file whitespace)
		use an explicit spacer element so HTML formatting won't affect alignment */
	.struct-line.struct-indent {
		padding-left: 0 !important;
	}
	.struct-indent-spacer {
		display: inline-block;
		width: 1.2rem;
		height: 1px;
		margin-right: 0.18rem;
	}
	/* smaller spacer for sub-directive / nested lines */
	.struct-subindent-spacer {
		display: inline-block;
		width: 0.9rem;
		height: 1px;
		margin-right: 0.12rem;
	}
</style>

<div class="struct-caddyfile-visual-repl fullwidth">
	<div class="struct-visual">
		<div class="struct-panel">
			<div class="struct-diagram">
				<div class="struct-code-box">
					<div class="struct-block global">
						<div class="struct-line">{</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">email</span> <span class="struct-opt-value">you@yours.com</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">servers</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">trusted_proxies</span> <span class="struct-arg">static</span> <span class="struct-arg">private_ranges</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block snippet">
						<div class="struct-line">(snippet) {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-comment"># this is a reusable snippet</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">log</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">output</span> <span class="struct-arg">file</span> <span class="struct-arg">/var/log/access.log</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line"><span class="struct-site-addr">example.com</span> {</div>
						<div class="struct-block matcher">
							<div class="struct-line"><span class="struct-matcher-token">@post</span> {</div>
							<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-matcher-token">method</span> <span class="struct-arg">POST</span></div>
							<div class="struct-line">}</div>
						</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">reverse_proxy</span> <span class="struct-matcher-token">@post</span> <span class="struct-arg">localhost:9001</span> <span class="struct-arg">localhost:9002</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">lb_policy</span> <span class="struct-arg">first</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">file_server</span> <span class="struct-matcher-token">/static</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">import</span> <span class="struct-arg">snippet</span></div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line struct-indent"><span class="struct-site-addr">www.example.com</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">redir</span> <span class="struct-arg">https://example.com{uri}</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">import</span> <span class="struct-arg">snippet</span></div>
						<div class="struct-line">}</div>
					</div>
				</div>
			</div>
			<div class="struct-legend" aria-hidden="false">
				<div class="struct-legend-title">Legend</div>
				<div class="struct-legend-title">Leyenda</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">Global options block</div><div class="struct-label">Bloque de opciones globales</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">Snippet</div><div class="struct-label">Snippet</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">Site block</div><div class="struct-label">Bloque de sitio</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-matcher)"></div><div class="struct-label">Matcher definition</div><div class="struct-label">Definición de matcher</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">Option name</div><div class="struct-label">Nombre de opción</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">Option value</div><div class="struct-label">Valor de opción</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">Comment</div><div class="struct-label">Comentario</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">Site address</div><div class="struct-label">Dirección del sitio</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">Directive</div><div class="struct-label">Directiva</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">Matcher token</div><div class="struct-label">Token de matcher</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">Argument</div><div class="struct-label">Argumento</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">Subdirective</div><div class="struct-label">Subdirectiva</div></div>
			</div>
		</div>
	</div>
</div>

Puntos clave:

- Un [**bloque de opciones globales**](#global-options) puede ser lo primero en el archivo.

- [Snippets](#snippets) o [rutas con nombre](#named-routes) pueden aparecer opcionalmente a continuación.

- Si no hay snippets ni rutas con nombre, la primera línea del Caddyfile es **siempre** la(s) [dirección(es)](#addresses) del sitio a servir.

- Todos los [directivas](#directives) y [matchers](#matchers) deben ir dentro de un bloque de sitio. No hay alcance global ni herencia entre bloques de sitio.

- Si hay solo un bloque de sitio, sus llaves `{ }` son opcionales.

Un Caddyfile consta de al menos uno o más bloques de sitio, que siempre comienzan por una o más [direcciones](#addresses) del sitio. Cualquier directiva que aparezca antes de la dirección confundirá al parser.


### Blocks

Abrir y cerrar un **bloque** se hace con llaves:

```
... {
	...
}
```

- La llave de apertura `{` debe estar al final de la línea y precedida por un espacio.

- La llave de cierre `}` debe estar en su propia línea.

Si existe un solo bloque de sitio, las llaves (e indentación) son opcionales. Esto es para configurar rápidamente un sitio único, por ejemplo:

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

equivale a:

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

cuando solo tienes un bloque de sitio; es solo una cuestión de preferencia.

Para configurar múltiples sitios con el mismo Caddyfile, debes usar llaves alrededor de cada uno para separar sus configuraciones:

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

Si una solicitud coincide con varios bloques de sitio, se elige el bloque cuya dirección coincida de forma más específica. La solicitud no cascada a otros bloques.


### Directives

Las [**directivas**](/docs/caddyfile/directives) son palabras clave funcionales que personalizan cómo se sirve el sitio. Deben aparecer dentro de bloques de sitio. Por ejemplo, una configuración completa de servidor de archivos puede ser:

```caddy
localhost {
	file_server
}
```

O un proxy inverso:

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

En estos ejemplos, [`file_server`](/docs/caddyfile/directives/file_server) y [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) son directivas. Las directivas son la primera palabra en una línea dentro de un bloque de sitio.

En el segundo ejemplo, `localhost:9000` es un **argumento** porque aparece en la misma línea después de la directiva.

A veces las directivas abren sus propios bloques. Los **subdirectives** aparecen al inicio de cada línea dentro de esos bloques:

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

Aquí, `lb_policy` es un subdirectiva de [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) y define la estrategia de balanceo de carga entre backend.

**Salvo que se documente lo contrario, las directivas no pueden usarse dentro de otros bloques de directiva.** Por ejemplo, [`basic_auth`](/docs/caddyfile/directives/basic_auth) no puede ir dentro de [`file_server`](/docs/caddyfile/directives/file_server) porque file_server no puede autenticar; pero sí puedes usar directivas dentro de [`route`](/docs/caddyfile/directives/route)、[`handle`](/docs/caddyfile/directives/handle) y [`handle_path`](/docs/caddyfile/directives/handle_path), porque están diseñadas para agrupar directivas.

Ten en cuenta que cuando se adapta el HTTP Caddyfile, las directivas de manejador HTTP se ordenan según un [orden de directivas](/docs/caddyfile/directives#directive-order) por defecto, excepto en bloques [`route`](/docs/caddyfile/directives/route). Por eso, el orden en el archivo no importa salvo en `route`.


### Tokens and quotes

El Caddyfile se tokeniza antes de analizarse. El espacio en blanco es significativo, ya que los tokens se separan por él.

A menudo, las directivas esperan un número concreto de argumentos; si un argumento tiene espacios, se separaría en dos tokens:

```caddy-d
directive abc def
```

Esto puede causar errores o comportamiento inesperado.

Si `abc def` debe ser el valor de un único argumento, debe ir entre comillas:

```caddy-d
directive "abc def"
```

Las comillas también pueden escaparse si necesitas comillas dentro de un token citado:

```caddy-d
directive "\"abc def\""
```

Para evitar escapar comillas, puedes usar backticks <code>\` \`</code> para encerrar tokens:

```caddy-d
directive `{"foo": "bar"}`
```

Dentro de tokens entre comillas, todos los caracteres se tratan literalmente, incluyendo espacios, tabulaciones y saltos de línea. Por eso existen tokens multilínea:

```caddy-d
directive "primera línea
	segunda línea"
```

También se admiten heredocs <span id="heredocs"/>.

```caddy
example.com {
	respond <<HTML
		<html>
		  <head><title>Foo</title></head>
		  <body>Foo</body>
		</html>
		HTML 200
}
```

El marcador inicial debe comenzar con `<<` y cualquier texto (se recomiendan mayúsculas). El marcador de cierre debe ser el mismo texto (en el ejemplo, `HTML`). El marcador de apertura puede escaparse con `\<<` para evitar el parseo de heredoc.

El cierre puede tener sangría, lo que provoca eliminar esa cantidad de sangría de cada línea (inspirado por [PHP](https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc)). Esto mejora legibilidad dentro de [bloques](#blocks) y da control de espacios en el token. También se elimina el salto de línea final, salvo que añadas una línea en blanco extra antes del cierre.

Pueden aparecer tokens adicionales tras el marcador de cierre como argumentos de la directiva (como en el ejemplo, el código de estado `200`).


## Global options

Un Caddyfile puede comenzar opcionalmente con un bloque especial sin claves llamado [bloque de opciones globales](/docs/caddyfile/options):

```caddy
{
	...
}
```

Si existe, debe ser el primer bloque del Caddyfile.

Sirve para definir opciones de alcance global o no aplicables a un sitio en particular. Dentro, solo pueden ponerse opciones globales; no puedes usar directivas de sitio regulares.

Por ejemplo, para habilitar la opción global `debug`, que se usa frecuentemente para logs detallados de troubleshooting:

```caddy
{
	debug
}
```

**[Lee la página de opciones globales](/docs/caddyfile/options) para más detalles.**



## Addresses

La dirección siempre aparece al principio del bloque de sitio y suele ser lo primero del Caddyfile.

Ejemplos de direcciones válidas:

| Address              | Effect                            |
|----------------------|-----------------------------------|
| `example.com`        | HTTPS con certificado [de confianza pública gestionado](/docs/automatic-https#hostname-requirements) |
| `*.example.com`      | HTTPS con [certificado wildcard de confianza pública](/docs/caddyfile/patterns#wildcard-certificates) gestionado |
| `localhost`          | HTTPS con certificado [de confianza local](/docs/automatic-https#local-https) |
| `http://`            | HTTP catch-all, afectado por [`http_port`](/docs/caddyfile/options#http-port) |
| `https://`           | HTTPS catch-all, afectado por [`https_port`](/docs/caddyfile/options#http-port) |
| `http://example.com` | HTTP explícito, con matcher `Host` |
| `example.com:443`    | HTTPS por coincidencia con [`https_port`](/docs/caddyfile/options#http-port) predeterminado |
| `:443`               | HTTPS catch-all por coincidencia con [`https_port`](/docs/caddyfile/options#http-port) predeterminado |
| `:8080`              | HTTP en puerto no estándar, sin matcher `Host` |
| `localhost:8080`     | HTTPS en puerto no estándar por tener un dominio válido |
| `https://example.com:443` | HTTPS, pero con `https://` y `:443` se vuelve redundante |
| `127.0.0.1` | HTTPS con certificado IP de confianza local |
| `http://127.0.0.1` | HTTP con `Host` matcher de dirección IP (rechaza `localhost`) |


<aside class="tip">

[Automatic HTTPS](/docs/automatic-https) se habilita si la dirección del sitio contiene hostname o IP. Esta es una configuración implícita, por lo que no sobrescribe ninguna configuración explícita.

Por ejemplo, si la dirección del sitio es `http://example.com`, auto-HTTPS no se activará porque el esquema es explícitamente `http://`.

</aside>


Desde la dirección, Caddy puede inferir esquema, host y puerto del sitio. Si la dirección no tiene puerto, el Caddyfile elegirá el puerto correspondiente al esquema si está especificado, o se asumirá el puerto `443` por defecto.

Si especificas un hostname, solo se atenderán solicitudes con encabezado `Host` coincidente. En otras palabras, con dirección `localhost` Caddy no atenderá `127.0.0.1`.

Se pueden usar comodines (`*`), pero solo para una etiqueta concreta del hostname. Por ejemplo, `*.example.com` coincide con `foo.example.com` pero no `foo.bar.example.com`, y `*` coincide con `localhost` pero no con `example.com`. Consulta el ejemplo práctico de [wildcard certificates](/docs/caddyfile/patterns#wildcard-certificates).

Para capturar todos los hosts, omite la parte de host de la dirección, por ejemplo `https://`. Esto es útil con [On-Demand TLS](/docs/automatic-https#on-demand-tls) cuando no conoces los dominios de antemano.

Si varios sitios comparten la misma definición, puedes listarlos juntos separados por espacios o comas (al menos un espacio). Los siguientes ejemplos son equivalentes:

```caddy
# Direcciones separadas por comas
localhost:8080, example.com, www.example.com {
	...
}
```

o

```caddy
# Direcciones separadas por espacios
localhost:8080 example.com www.example.com {
	...
}
```

o

```caddy
# Direcciones por líneas y coma
localhost:8080,
example.com,
www.example.com {
	...
}
```

Una dirección debe ser única; no se puede repetir.

[Placeholders](#placeholders) **no** se pueden usar en direcciones, aunque sí puedes usar variables de entorno de Caddyfile:

```caddy
{$DOMAIN:localhost} {
	...
}
```

Por defecto, los sitios se enlazan en todas las interfaces de red. Si quieres sobreescribirlo, usa la directiva [`bind`](/docs/caddyfile/directives/bind) o la opción global [`default_bind` ](/docs/caddyfile/options#default-bind).


## Matchers

Los [directivas](/docs/caddyfile/directives) de HTTP handler se aplican a todas las solicitudes por defecto (salvo que se documente otra cosa).

Los [request matchers](/docs/caddyfile/matchers) clasifican solicitudes por criterios. Con ellos, puedes especificar exactamente a qué solicitudes se aplica una directiva.

Para directivas que soportan matchers, el primer argumento tras la directiva es el **matcher token**. Ejemplos:

```caddy-d
root *           /var/www  # matcher token: *
root /index.html /var/www  # matcher token: /index.html
root @post       /var/www  # matcher token: @post
```

El matcher token puede omitirse para que coincida con todas las solicitudes; por ejemplo, no hace falta usar `*` si el argumento siguiente no parece un matcher de ruta.

**[Lee la página de Request Matchers](/docs/caddyfile/matchers) para más información.**


## Placeholders

Los [Placeholders](/docs/conventions#placeholders) permiten inyectar valores dinámicos en configuraciones estáticas. Pueden usarse como argumentos de directivas y subdirectivas.

Los placeholders van entre llaves `{ }` y contienen un identificador, por ejemplo: `{foo.bar}`. La llave de apertura se puede escapar `\{like.this}` para evitar reemplazo. Los identificadores suelen estar namespaced con puntos para evitar colisiones entre módulos.

Qué placeholders están disponibles depende del contexto. No todos se soportan en todas partes. Por ejemplo, [el app HTTP define placeholders](/docs/json/apps/http/#docs) disponibles solo donde se maneja HTTP (por ejemplo, en [directivas de manejo HTTP](/docs/caddyfile/directives) y [matchers](/docs/caddyfile/matchers)), **no** en la [configuración `tls`](/docs/caddyfile/directives/tls). Algunas directivas o matchers también definen placeholders propios reutilizables por siguientes handlers. Algunos placeholders son [globales](/docs/conventions#placeholders).

Puedes usar placeholders sin convertir en Caddyfile con equivalencias de atajos:

| Caddyfile        | Reemplaza                            |
|------------------|-------------------------------------|
| `{cookie.*}`     | `{http.request.cookie.*}`           |
| `{client_ip}`    | `{http.vars.client_ip}`             |
| `{dir}`          | `{http.request.uri.path.dir}`       |
| `{err.*}`        | `{http.error.*}`                    |
| `{file_match.*}` | `{http.matchers.file.*}`            |
| `{file.base}`    | `{http.request.uri.path.file.base}` |
| `{file.ext}`     | `{http.request.uri.path.file.ext}`  |
| `{file}`         | `{http.request.uri.path.file}`      |
| `{header.*}`     | `{http.request.header.*}`           |
| `{host}`         | `{http.request.host}`               |
| `{hostport}`     | `{http.request.hostport}`           |
| `{labels.*}`     | `{http.request.host.labels.*}`      |
| `{method}`       | `{http.request.method}`             |
| `{orig_method}`  | `{http.request.orig_method}`        |
| `{orig_uri}`     | `{http.request.orig_uri}`           |
| `{orig_path}`    | `{http.request.orig_uri.path}`      |
| `{orig_dir}`     | `{http.request.orig_uri.path.dir}`  |
| `{orig_file}`    | `{http.request.orig_uri.path.file}` |
| `{orig_query}`   | `{http.request.orig_uri.query}`     |
| `{orig_?query}`  | `{http.request.orig_uri.prefixed_query}` |
| `{path.*}`       | `{http.request.uri.path.*}`         |
| `{path}`         | `{http.request.uri.path}`           |
| `{%path}`        | `{http.request.uri.path_escaped}`   |
| `{port}`         | `{http.request.port}`               |
| `{query.*}`      | `{http.request.uri.query.*}`        |
| `{query}`        | `{http.request.uri.query}`          |
| `{%query}`       | `{http.request.uri.query_escaped}`  |
| `{?query}`       | `{http.request.uri.prefixed_query}` |
| `{re.*}`         | `{http.regexp.*}`                   |
| `{remote_host}`  | `{http.request.remote.host}`        |
| `{remote_port}`  | `{http.request.remote.port}`        |
| `{remote}`       | `{http.request.remote}`             |
| `{rp.*}`         | `{http.reverse_proxy.*}`            |
| `{resp.*}`       | `{http.intercept.*}`                |
| `{scheme}`       | `{http.request.scheme}`             |
| `{tls_cipher}`   | `{http.request.tls.cipher_suite}`   |
| `{tls_client_certificate_der_base64}` | `{http.request.tls.client.certificate_der_base64}` |
| `{tls_client_certificate_pem}`        | `{http.request.tls.client.certificate_pem}` |
| `{tls_client_fingerprint}`            | `{http.request.tls.client.fingerprint}`     |
| `{tls_client_issuer}`                 | `{http.request.tls.client.issuer}`          |
| `{tls_client_serial}`                 | `{http.request.tls.client.serial}`          |
| `{tls_client_subject}`                | `{http.request.tls.client.subject}`         |
| `{tls_version}`       | `{http.request.tls.version}`             |
| `{upstream_hostport}` | `{http.reverse_proxy.upstream.hostport}` |
| `{uri}`               | `{http.request.uri}`                     |
| `{%uri}`              | `{http.request.uri_escaped}`             |
| `{vars.*}`            | `{http.vars.*}`                          |

No todos los campos de configuración aceptan placeholders, pero la mayoría sí donde esperas. El soporte debe estar implementado explícitamente. Los autores de plugins pueden [leer este artículo](/docs/extending-caddy/placeholders) para agregar soporte en sus módulos.


## Snippets

Puedes definir bloques especiales llamados snippets con un nombre entre paréntesis:

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

Y luego reutilizarlos donde necesites con la directiva [`import`](/docs/caddyfile/directives/import):

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

[`import`](/docs/caddyfile/directives/import) también puede incluir otros archivos en su lugar. Si el argumento no coincide con un snippet definido, lo trata como archivo. También soporta globs para importar varios archivos. Como caso especial, puede aparecer en cualquier parte del Caddyfile (excepto como argumento de otra directiva), incluso fuera de bloques de sitio:

```caddy
{
	email admin@example.com
}

import sites/*
```

Puedes pasar argumentos a snippets o archivos importados:

```caddy
(snippet) {
	respond "Yahaha! You found {args[0]}!"
}

a.example.com {
	import snippet "Example A"
}

b.example.com {
	import snippet "Example B"
}
```

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

También puedes pasar un bloque opcional a un snippet importado, y usarlo así:

```caddy
(snippet) {
	{block}
	respond "OK"
}

a.example.com {
	import snippet {
		header +foo bar
	}
}

b.example.com {
	import snippet {
		header +bar foo
	}
}
```

**[Lee la página de la directiva `import`](/docs/caddyfile/directives/import) para más detalles.**


## Named Routes

⚠️ <i>Experimental</i>

Las rutas con nombre usan una sintaxis similar a [snippets](#snippets). Son bloques especiales definidos fuera de bloques de sitio, prefijados con `&(` y cerrados con `)` con el nombre en medio.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

Luego puedes reutilizar la ruta con nombre dentro de cualquier sitio:

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

Esto es útil para reducir memoria cuando se necesita la misma ruta en muchos sitios, o distintos matchers para invocarla.

**[Lee la página de la directiva `invoke`](/docs/caddyfile/directives/invoke) para más detalles.**



## Comments

Los comentarios empiezan por `#` y van hasta el final de la línea:

```caddy-d
# Los comentarios pueden empezar una línea
directive  # o ir al final
```

El carácter `#` de un comentario no puede aparecer en mitad de un token (debe tener un espacio o estar al inicio de línea). Esto permite usar `#` en URIs o valores sin comillas.



## Environment variables

Si tu configuración depende de variables de entorno, puedes usarlas en Caddyfile:

```caddy
{$ENV}
```

Estas variables se sustituyen **antes** de que el Caddyfile empiece a parsearse, por eso pueden expandirse a valor vacío (`""`), tokens parciales, tokens completos o incluso múltiples líneas.

Por ejemplo, una variable `UPSTREAMS="app1:8080 app2:8080 app3:8080"` se expandiría en múltiples [tokens](#tokens-and-quotes):

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

Puedes definir un valor predeterminado si la variable no existe usando `:` como separador entre nombre y valor:

```caddy
{$DOMAIN:localhost} {

}
```

Si quieres **posponer la sustitución** de una variable al tiempo de ejecución, usa placeholders [`{env.*}` estándar](/docs/conventions#placeholders). No todos los parámetros soportan estos placeholders, ya que los desarrolladores de módulos deben añadir reemplazo explícito. Si no funciona, abre un issue para solicitar soporte.

Por ejemplo, si tienes instalado el plugin [`caddy-dns/cloudflare` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns/cloudflare) y quieres configurar el [DNS challenge](/docs/automatic-https#dns-challenge), puedes pasar tu variable `CLOUDFLARE_API_TOKEN` así:

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Si ejecutas Caddy como servicio `systemd`, consulta [estas instrucciones](/docs/running#overrides) para definir overrides con variables de entorno.
