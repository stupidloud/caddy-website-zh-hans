---
title: Request matchers (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the matchers in the code blocks
	// to their associated anchor tags.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Link matcher tokens based on their contents to the syntax section
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Matcher token">${text}</a>`;
	});
});
</script>

# Request Matchers

Los **matchers de solicitud** se pueden usar para filtrar (o clasificar) solicitudes mediante distintos criterios.

- [Syntax](#syntax)
	- [Examples](#examples)
	- [Wildcard matchers](#wildcard-matchers)
	- [Path matchers](#path-matchers)
	- [Named matchers](#named-matchers)
- [Standard matchers](#standard-matchers)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)


## Syntax

En el Caddyfile, un **matcher token** inmediatamente después de la directiva puede limitar el alcance de esa directiva. El token matcher puede tener una de estas formas:

1. [**`*`**](#wildcard-matchers) para hacer match de todas las solicitudes (wildcard; valor predeterminado).
2. [**`/path`**](#path-matchers) inicia con slash para hacer match de la ruta de la solicitud.
3. [**`@name`**](#named-matchers) para especificar un _named matcher_.

Si una directiva admite matchers, aparecerá como `[<matcher>]` en su documentación de sintaxis. Los matcher tokens son [generalmente opcionales](/docs/caddyfile/directives#syntax), indicados por `[ ]`. Si se omite el matcher token, es equivalente a usar el matcher wildcard (`*`).


#### Examples

Esta directiva aplica a todas ([all](#wildcard-matchers)) las solicitudes HTTP:

```caddy-d
reverse_proxy localhost:9000
```

Y esto es equivalente (`*` no es necesario aquí):

```caddy-d
reverse_proxy * localhost:9000
```

Pero esta directiva solo aplica a solicitudes que tengan una [ruta](#path-matchers) que empiece por `/api/`:

```caddy-d
reverse_proxy /api/* localhost:9000
```

Para hacer match con algo distinto a una ruta, define un [named matcher](#named-matchers) y haz referencia a él con `@name`:

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```



### Wildcard matchers

El matcher wildcard (o "catch-all") `*` hace match de todas las solicitudes y solo es necesario si se requiere un matcher token. Por ejemplo, si el primer argumento que quieras pasar a una directiva también resulta parecer una ruta, tendrá exactamente el mismo aspecto que un path matcher. Por eso puedes usar wildcard matcher para desambiguar:

```caddy-d
root * /home/www/mysite
```

Fuera de eso, este matcher no se usa con frecuencia. En general recomendamos omitirlo si la sintaxis no lo requiere.


### Path matchers

Hacer match por la ruta URI es la forma más común de filtrar solicitudes, así que el matcher puede ir en línea, así:

```caddy-d
redir /old.html /new.html
```

Los tokens de path matcher deben comenzar con una barra diagonal `/`.

**El [match de path](#path) por defecto es una coincidencia exacta, no por prefijo.** Debes añadir `*` para un prefijo rápido. Ten en cuenta que `/foo*` hará match con `/foo` y `/foo/` además de `/foobar`; quizá realmente quieras `/foo/*` en su lugar.


### Named matchers

Todos los matchers que no sean path o wildcard son named matchers. Esto es un matcher que se define fuera de cualquier directiva en concreto y puede reutilizarse.

Definir un matcher con un nombre único te da más flexibilidad, ya que te permite combinar [cualquier matcher disponible](#standard-matchers) en un mismo set:

```caddy-d
@name {
	...
}
```

o, si solo hay un matcher en el set, puedes ponerlo en la misma línea:

```caddy-d
@name ...
```

Entonces puedes usar el matcher así, especificándolo como primer argumento de una directiva:

```caddy-d
directive @name
```

Por ejemplo, esto hace proxy de solicitudes websocket HTTP/1.1 a `localhost:6001`, y otras solicitudes a `localhost:8080`. Hace match de solicitudes que tengan un campo de cabecera llamado `Connection` _que contenga_ `Upgrade`, **y** otro campo llamado `Upgrade` con exactamente `websocket`:

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

Si el set de matcher consiste en un solo matcher, también funciona la sintaxis en una línea:

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

Como caso especial, el [`expression matcher`](#expression) puede usarse sin especificar su nombre siempre que un argumento entre [comillas](/docs/caddyfile/concepts#tokens-and-quotes) (la propia expresión CEL) siga al nombre del matcher:

```caddy-d
@not-found `{err.status_code} == 404`
```

Al igual que con las directivas, las definiciones de named matcher deben ir dentro de los [site blocks](/docs/caddyfile/concepts#structure) que los usan.

Una definición de named matcher constituye un _matcher set_. Los matchers de un set se combinan con AND; es decir, todos deben coincidir. Por ejemplo, si tienes tanto un matcher [`header`](#header) como [`path`](#path) en el set, ambos deben coincidir.

Se pueden fusionar múltiples matchers del mismo tipo (por ejemplo, varios matchers [`path`](#path) en el mismo set) usando álgebra booleana (AND/OR), como se describe en sus secciones más abajo.

Para lógicas booleanas más complejas, se recomienda el [`expression matcher`](#expression) para escribir una expresión CEL, que soporta **and** `&&`, **or** `||`, y **parentheses** `( )`.



## Standard matchers

La documentación completa de cada matcher se encuentra [en los docs de cada módulo de matcher respectivo](/docs/json/apps/http/servers/routes/match/).

Las solicitudes se pueden hacer match de las siguientes formas:



<a id="client-ip"></a>
### client_ip

```caddy-d
client_ip <ranges...>

expression client_ip('<ranges...>')
```

Por dirección IP de cliente. Acepta IPs exactas o rangos CIDR. Se soportan zonas IPv6.

Este matcher se usa mejor cuando la opción global [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) está configurada; de lo contrario actúa de forma idéntica al matcher [`remote_ip`](#remote-ip). Solo las solicitudes de proxys confiables tendrán su IP de cliente analizada al inicio de la petición; las solicitudes no confiables usarán la IP remota del par inmediato o la dirección establecida vía [PROXY protocol](/docs/caddyfile/options#proxy-protocol).

Como atajo, se puede usar `private_ranges` para hacer match de todos los rangos IPv4 e IPv6 privados. Es lo mismo que especificar todos estos rangos: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Puede haber múltiples matchers `client_ip` por named matcher, y sus rangos se combinarán con OR.

#### Example:

Hacer match de solicitudes desde direcciones IPv4 privadas:

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Este matcher se combina frecuentemente con [`not`](#not) para invertir el match. Por ejemplo, para abortar todas las conexiones desde direcciones IPv4 y IPv6 _públicas_ (lo opuesto a todos los rangos privados):

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

En una [expresión CEL](#expression), sería así:

```caddy-d
@my-friends `client_ip('12.23.34.45', '23.34.45.56')`
```



### expression

```caddy-d
expression <cel...>
```

Por cualquier expresión [CEL (Common Expression Language)](https://github.com/google/cel-spec) que devuelva `true` o `false`.

La mayoría de otros matchers también pueden usarse en expresiones como funciones, lo que permite más flexibilidad de lógica booleana fuera de expresiones. Consulta la documentación de cada matcher para la sintaxis admitida dentro de expresiones CEL.

Los [placeholders](/docs/conventions#placeholders) de Caddy (o [atajos de Caddyfile](/docs/caddyfile/concepts#placeholders)) se pueden usar en estas expresiones CEL, ya que se preprocesan y convierten a llamadas normales de funciones CEL antes de interpretarlas en el entorno CEL. Si un placeholder debe pasarse como argumento de cadena a una función matcher, el `{` inicial debe escaparse con una barra invertida `\` para que no se preprocese, por ejemplo `file('\{path}.md')`.

Por conveniencia, el nombre del matcher puede omitirse si defines un named matcher que consista únicamente en una expresión CEL. La expresión CEL debe ir entre [comillas](/docs/caddyfile/concepts#tokens-and-quotes) (se recomiendan backticks o heredocs). Esto se lee de forma muy limpia:

```caddy-d
@mutable `{method}.startsWith("P")`
```

En este caso se asume el expression matcher.

#### Examples:

Hacer match de solicitudes cuyos métodos empiecen por `P`, por ejemplo `PUT` o `POST`:

```caddy-d
@methods expression {method}.startsWith("P")
```

Hacer match de solicitudes donde el handler devolvió estado `404`, se usa junto con la directiva [`handle_errors`](/docs/caddyfile/directives/handle_errors):

```caddy-d
@404 expression {err.status_code} == 404
```

Hacer match de solicitudes donde la ruta coincide con dos expresiones regulares diferentes; esto solo es posible usando una expresión porque el matcher [`path_regexp`](#path-regexp) normalmente solo puede existir una vez por named matcher:

```caddy-d
@user expression path_regexp('^/user/(\\w*)') || path_regexp('^(\\w*)')
```

O lo mismo, omitiendo el nombre del matcher y envolviendo en [backticks](/docs/caddyfile/concepts#tokens-and-quotes) para que se analice como un solo token:

```caddy-d
@user `path_regexp('^/user/(\\w*)') || path_regexp('^(\\w*)')`
```

Puedes usar [heredoc syntax](/docs/caddyfile/concepts#heredocs) para escribir expresiones CEL multlínea:

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Hello, API!"
```


---
### file

```caddy-d
file {
	root       <path>
	try_files  <files...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delims...>
}
file <files...>

expression `file({
	'root': '<path>',
	'try_files': ['<files...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delims...>']
})`
expression file('<files...>')
```

Por archivos.

- `root` define el directorio donde buscar archivos. El valor predeterminado es el directorio de trabajo actual o la [variable](/docs/modules/http.handlers.vars) `root` (`{http.vars.root}`) si está definida (se puede definir con la directiva [`root`](/docs/caddyfile/directives/root)).

- `try_files` comprueba los archivos de su lista que cumplen con `try_policy`.

  Para hacer match con directorios, añade una barra diagonal final `/` a la ruta. Todas las rutas de archivo son relativas al [site root](/docs/caddyfile/directives/root), y los [patrones glob](https://pkg.go.dev/path/filepath#Match) se expandirán.

  Si `try_policy` es `first_exist` (valor predeterminado), el último elemento de la lista puede ser un número prefijado por `=` (por ejemplo `=404`), que como respaldo emitirá un error con ese código; ese error se puede capturar y manejar con [`handle_errors`](/docs/caddyfile/directives/handle_errors).



- `try_policy` especifica cómo elegir un archivo. El valor predeterminado es `first_exist`.

	- `first_exist` comprueba la existencia de archivos. Selecciona el primer archivo que exista.

	- `first_exist_fallback` es similar a `first_exist`, pero asume que el último elemento de la lista siempre existe para evitar un acceso a disco.

	- `smallest_size` elige el archivo de menor tamaño.

	- `largest_size` elige el archivo de mayor tamaño.

	- `most_recently_modified` elige el archivo modificado más recientemente.

- `split_path` hará que la ruta se separe en el primer delimitador de la lista que se encuentre en cada ruta de archivo que se pruebe. Para cada valor de split, el lado izquierdo del split, incluyendo el propio delimitador, será la ruta de archivo que se probará. Por ejemplo, `/remote.php/dav/` con un delimitador `.php` probaría el archivo `/remote.php`. Cada delimitador debe aparecer al final de un componente del path URI para poder usarse como split delimiter. Esta es una opción de nicho y se usa principalmente al servir sitios PHP.

Debido a que `try_files` con `first_exist` es tan común, existe un atajo de una sola línea para ese caso:

```caddy-d
file <files...>
```

Un matcher `file` vacío (sin archivos tras él) comprobará si el archivo solicitado&mdash;literalmente desde la URI, relativo al [site root](/docs/caddyfile/directives/root)&mdash;existe. Esto es efectivamente lo mismo que `file {path}`.


<aside class="tip">

Como el reescritura basada en la existencia de un archivo en disco es tan común, también existe la directiva [`try_files`](/docs/caddyfile/directives/try_files), que es un atajo del matcher `file` y un [handler]`rewrite`]
</aside>


Al hacer match, se exponen cuatro placeholders nuevos:

- `{file_match.relative}` La ruta del archivo relativa a la raíz. Esto suele ser útil al reescribir solicitudes.
- `{file_match.absolute}` La ruta absoluta del archivo que hizo match, incluyendo la raíz.
- `{file_match.type}` El tipo de archivo, `file` o `directory`.
- `{file_match.remainder}` La parte que queda tras dividir la ruta del archivo (si está configurado `split_path`).


#### Examples:

Hacer match de solicitudes donde la ruta es un archivo que existe:

```caddy-d
@file file
```

Hacer match de solicitudes donde la ruta seguida por `.html` es un archivo existente, o si no, donde la ruta es un archivo existente:

```caddy-d
@html file {
	try_files {path}.html {path} 
}
```

Igual que antes, excepto usando el atajo en una línea, y con respaldo de error 404 si no se encuentra archivo:

```caddy-d
@html-or-error file {path}.html {path} =404
```

Más ejemplos usando [expresiones CEL](#expression). Recuerda que los placeholders se preprocesan y convierten a llamadas de función CEL antes de interpretarse, así que aquí se usa concatenación. Además, se debe usar la forma larga si concatenas con placeholders por limitaciones actuales del parser:

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---
### header

```caddy-d
header <field> [<value> ...]

expression header({'<field>': '<value>'})
```

Por campos de cabecera de la solicitud.

- `<field>` es el nombre del campo de cabecera HTTP a comprobar.
	- Si está prefijado con `!`, el campo no debe existir para hacer match (omite el argumento de valor).
- `<value>` es el valor que debe tener el campo para hacer match. Se puede indicar uno o más.
	- Si está prefijado por `*`, realiza una coincidencia de sufijo rápido (aparece al final).
	- Si está sufijado con `*`, realiza una coincidencia de prefijo rápido (aparece al inicio).
	- Si está encerrado entre `*`, realiza una coincidencia de subcadena rápida (aparece en cualquier parte).
	- En otro caso es una coincidencia exacta rápida.

Campos de cabecera distintos dentro del mismo set se combinan con AND. Varios valores por campo se combinan con OR.

Ten en cuenta que los campos de cabecera pueden repetirse y tener valores distintos. Las aplicaciones backend DEBEN considerar que los valores de campos de cabecera son arrays, no valores únicos, y Caddy no interpreta significado en esas ambigüedades.

#### Example:

Hacer match de solicitudes con la cabecera `Connection` que contenga `Upgrade`:

```caddy-d
@upgrade header Connection *Upgrade*
```

Hacer match de solicitudes con la cabecera `Foo` que contenga `bar` o `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Hacer match de solicitudes que no tengan en absoluto el campo de cabecera `Foo`:

```caddy-d
@not_foo header !Foo
```

Usando una [expresión CEL](#expression), haz match de WebSocket verificando que `Connection` contenga `Upgrade` y que `Upgrade` sea exactamente `websocket` (HTTP/2 usa la cabecera `:protocol` para esto):

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---
<a id="header-regexp"></a>
### header_regexp

```caddy-d
header_regexp [<name>] <field> <regexp>

expression header_regexp('<name>', '<field>', '<regexp>')
expression header_regexp('<field>', '<regexp>')
```

Como [`header`](#header), pero soporta expresiones regulares.

El lenguaje de expresiones usado es RE2, incluido en Go. Consulta la [referencia de sintaxis RE2](https://github.com/google/re2/wiki/Syntax) y la [visión general de sintaxis regexp de Go](https://pkg.go.dev/regexp/syntax).

Desde v2.8.0, si no se proporciona `name`, el nombre se tomará del nombre del named matcher. Por ejemplo, un named matcher `@foo` hará que este matcher se nombre `foo`. La principal ventaja de especificar un nombre es cuando se usan más de un matcher regexp en el mismo named matcher (por ejemplo, `header_regexp` y [`path_regexp`](#path-regexp), o múltiples campos de cabecera diferentes).

Los grupos de captura pueden obtenerse mediante un [placeholder](/docs/caddyfile/concepts#placeholders) en directivas después del match:
- `{re.<name>.<capture_group>}` donde:
  - `<name>` es el nombre de la expresión regular,
  - `<capture_group>` es el nombre o número del grupo de captura en la expresión.

- `{re.<capture_group>}` sin nombre también se rellena por conveniencia. El detalle es que si se usan varios matchers regexp en secuencia, los valores del placeholder serán sobrescritos por el siguiente matcher.

El grupo `0` es la coincidencia completa de la regexp, `1` el primer grupo de captura, `2` el segundo y así sucesivamente. Así que `{re.foo.1}` o `{re.1}` contendrán ambos el valor del primer grupo de captura.

Solo se admite una expresión regular por campo de cabecera, ya que los patrones regexp no se pueden combinar; si necesitas más, considera usar un [`expression matcher`](#expression). Los matches contra varios campos diferentes de cabecera se combinarán con AND.

#### Example:

Hacer match de solicitudes donde la cabecera Cookie contenga `login_` seguido de una cadena hex, con un grupo de captura al que se accede con `{re.login.1}` o `{re.1}`.

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

Esto puede simplificarse omitiendo el nombre, que se deducirá del named matcher:

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

O lo mismo, usando una [expresión CEL](#expression):

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```



---
### host

```caddy-d
host <hosts...>

expression host('<hosts...>')
```

Hace match por el campo `Host` de la solicitud.

Como la mayoría de los site blocks ya indican hosts en la dirección del site, este matcher se usa más comúnmente en site blocks con hostname wildcard (ver [wildcard certificates pattern](/docs/caddyfile/patterns#wildcard-certificates)), pero donde se requiere lógica específica de hostname.

Múltiples matchers `host` se combinan con OR.

#### Example:

Haciendo match de un subdominio:

```caddy-d
@sub host sub.example.com
```

Haciendo match del dominio apex y un subdominio:

```caddy-d
@site host example.com www.example.com
```

Múltiples subdominios usando una [expresión CEL](#expression):

```caddy-d
@app `host('app1.example.com', 'app2.example.com')`
```


---
### method

```caddy-d
method <verbs...>

expression method('<verbs...>')
```

Por el método (verbo) de la solicitud HTTP. Los verbos deben ir en mayúsculas, como `POST`. Puede coincidir con uno o muchos métodos.

Múltiples matchers `method` se combinan con OR.

#### Examples:

Hacer match de solicitudes con método `GET`:

```caddy-d
@get method GET
```

Hacer match de solicitudes con método `PUT` o `DELETE`:

```caddy-d
@put-delete method PUT DELETE
```

Hacer match de métodos de solo lectura usando una [expresión CEL](#expression):

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```


---
### not

```caddy-d
not <matcher>
```

or, para negar varios matchers que se combinan con AND, abre un bloque:

```caddy-d
not {
	<matchers...>
}
```

Los resultados de los matchers contenidos se negarán.

#### Examples:

Hacer match de solicitudes con rutas que NO comiencen por `/css/` o `/js/`.

```caddy-d
@not-assets {
	not path /css/* /js/*
}
```

Hacer match de solicitudes SIN AMBAS:
- un prefijo de ruta `/api/`, NI
- el método HTTP `POST`

es decir, debe cumplirse ninguno de estos para hacer match:

```caddy-d
@with-neither {
	not path /api/*
	not method POST
}
```

Hacer match de solicitudes SIN AMBAS:
- un prefijo de ruta `/api/`, Y
- el método HTTP `POST`

es decir, debe cumplirse ninguna o ambas para hacer match:

```caddy-d
@without-both {
	not {
		path /api/*
		method POST
	}
}
```

No hay [expresión CEL](#expression) para este matcher, porque puedes usar el operador `!` para la negación. Por ejemplo:

```caddy-d
@without-both `!path('/api*') && !method('POST')`
```

Lo mismo que esto, usando paréntesis:

```caddy-d
@without-both `!(path('/api*') || method('POST'))`
```



---
### path

```caddy-d
path <paths...>

expression path('<paths...>')
```

Por la ruta solicitada (la parte de la ruta del URI de la solicitud). Los matches de path son exactos e insensibles a mayúsculas. Se pueden usar wildcards `*`:

- Solo al final, para coincidencia de prefijo (`/prefix/*`)
- Solo al inicio, para coincidencia de sufijo (`*.suffix`)
- En ambos lados, para coincidencia de subcadena (`*/contains/*`)
- En el medio, para coincidencia globular (`/accounts/*/info`)

Las barras diagonales son significativas. Por ejemplo, `/foo*` hará match con `/foo`, `/foobar`, `/foo/` y `/foo/bar`, pero `/foo/*` **no** hará match con `/foo` o `/foobar`.

Las rutas de las solicitudes se limpian para resolver puntos de directorio antes del match. Además, se combinan múltiples barras diagonales salvo que el patrón de match también tenga múltiples slashes. Es decir, `/foo` hará match con `/foo` y `//foo`, pero `//foo` solo hará match con `//foo`.

Debido a que hay varias formas escapadas de cualquier URI, la ruta de la solicitud se normaliza (se decodifica URL) salvo esas secuencias de escape presentes también en el patrón de match. Por ejemplo, `/foo/bar` hace match con ambos `/foo/bar` y `/foo%2Fbar`, pero `/foo%2Fbar` solo hará match con `/foo%2Fbar`, porque la secuencia de escape está explícitamente dada en la configuración.

El wildcard escape especial `%*` también puede usarse en lugar de `*` para dejar su rango de coincidencia escapado. Por ejemplo, `/bands/*/*` no hará match con `/bands/AC%2FDC/T.N.T` porque la ruta se comparará en espacio normalizado como `/bands/AC/DC/T.N.T`, que no coincide con el patrón; sin embargo, `/bands/%*/*` sí hará match con `/bands/AC%2FDC/T.N.T` porque el span representado por `%*` se comparará sin decodificar secuencias de escape.

Múltiples paths se combinan con OR.

#### Examples:

Hacer match de varios directorios y su contenido:

```caddy-d
@assets path /js/* /css/* /images/*
```

Hacer match de un archivo específico:

```caddy-d
@favicon path /favicon.ico
```

Hacer match de extensiones de archivo:

```caddy-d
@extensions path *.js *.css
```

Con una [expresión CEL](#expression):

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```


---
<a id="path-regexp"></a>
### path_regexp

```caddy-d
path_regexp [<name>] <regexp>

expression path_regexp('<name>', '<regexp>')
expression path_regexp('<regexp>')
```

Como [`path`](#path), pero soporta expresiones regulares. Se ejecuta contra la ruta URI decodificada/sin escapes.

El lenguaje de expresiones usado es RE2, incluido en Go. Consulta la [referencia de sintaxis RE2](https://github.com/google/re2/wiki/Syntax) y la [visión general de sintaxis regexp de Go](https://pkg.go.dev/regexp/syntax).

Desde v2.8.0, si no se proporciona `name`, el nombre se tomará del nombre del named matcher. Por ejemplo, un named matcher `@foo` hará que este matcher se nombre `foo`. La principal ventaja de especificar un nombre es cuando se usan más de un matcher regexp en el mismo named matcher (por ejemplo `path_regexp` y [`header_regexp`](#header-regexp)).

Los grupos de captura se pueden acceder mediante un [placeholder](/docs/caddyfile/concepts#placeholders) en las directivas después del match:
- `{re.<name>.<capture_group>}` donde:
  - `<name>` es el nombre de la expresión regular,
  - `<capture_group>` es el nombre o número del grupo de captura en la expresión.

- `{re.<capture_group>}` sin nombre también se rellena por conveniencia. El detalle es que si se usan varios regex en secuencia, los valores de placeholder se sobrescribirán con el siguiente matcher.

El grupo `0` es la coincidencia completa de la regexp, `1` el primer capture group, `2` el segundo y así sucesivamente. Así que `{re.foo.1}` o `{re.1}` contienen el valor del primer grupo.

Solo puede haber un patrón `path_regexp` por named matcher, ya que este matcher no se puede fusionar consigo mismo; si necesitas más, considera usar un [`expression matcher`](#expression).

#### Example:

Hacer match de solicitudes donde la ruta termine con una cadena hexadecimal de 6 caracteres seguida de `.css` o `.js` como extensión, con grupos de captura (partes entre `( )`) que se pueden acceder con `{re.static.1}` y `{re.static.2}` (o `{re.1}` y `{re.2}`):

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

Esto puede simplificarse omitiendo el nombre, que se deducirá del named matcher:

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

O lo mismo, usando una [expresión CEL](#expression), validando también que [`file`](#file) exista en disco:

```caddy-d
@static `path_regexp('\\.([a-f0-9]{6})\\.(css|js)$') && file()`
```


---
### protocol

```caddy-d
protocol http|https|grpc|http/<version>[+]

expression protocol('http|https|grpc|http/<version>[+]')
```

Por protocolo de la solicitud. Se puede usar un nombre amplio como `http`, `https` o `grpc`; o versiones específicas o mínimas de HTTP como `http/1.1` o `http/2+`.

Solo puede haber un matcher `protocol` por named matcher.

#### Example:

Hacer match de solicitudes que usen HTTP/2:

```caddy-d
@http2 protocol http/2+
```

Con una [expresión CEL](#expression):

```caddy-d
@http2 `protocol('http/2+')`
```


---
### query

```caddy-d
query <key>=<val>...
query ""

expression query({'<key>': '<val>'})
expression query({'<key>': ['<vals...>']})
```

Por parámetros de cadena de consulta. Debe ser una secuencia de pares `key=value`, o una cadena vacía "". Las claves se comparan exactas (sensible a mayúsculas/minúsculas), pero también admiten `*` para hacer match con cualquier valor. Los valores pueden usar placeholders. Una cadena vacía hace match con solicitudes sin parámetros de query.

Puede haber múltiples matchers `query` por named matcher, y los pares con claves iguales se combinarán con OR. Claves distintas se combinan con AND. Así, todas las claves del matcher deben tener al menos un valor coincidente.

Las cadenas de consulta ilegales (sintaxis inválida, punto y coma no escapado, etc.) fallarán al parsear y por eso no harán match.

**NOTA:** Los parámetros de query son arrays, no valores singulares. Esto ocurre porque las claves repetidas son válidas en query strings y cada una puede tener un valor distinto. Este matcher hará match para una clave si cualquiera de sus valores configurados aparece asignado en la query. Las aplicaciones backend usando query strings DEBEN considerar que los valores de query son arrays y pueden tener múltiples valores.

#### Example:

Hacer match de un parámetro `q` con cualquier valor:

```caddy-d
@search query q=*
```

Hacer match de un parámetro `sort` con el valor `asc` o `desc`:

```caddy-d
@sorted query sort=asc sort=desc
```

Hacer match de ambos `q` y `sort`, con una [expresión CEL](#expression):

```caddy-d
@search-sort `query({'sort': ['asc', 'desc'], 'q': '*'})`
```


---
<a id="remote-ip"></a>
### remote_ip

```caddy-d
remote_ip <ranges...>

expression remote_ip('<ranges...>')
```

Por la dirección IP remota (es decir, la IP del peer inmediato o la dirección establecida vía [PROXY protocol](/docs/caddyfile/options#proxy-protocol)). Acepta IPs exactas o rangos CIDR. Se soportan zonas IPv6.

Como atajo, `private_ranges` puede usarse para hacer match de todos los rangos privados IPv4 e IPv6. Es lo mismo que especificar todos estos rangos: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Si deseas hacer match con la "real IP" del cliente, analizada desde cabeceras HTTP, usa el matcher [`client_ip`](#client-ip).

Puede haber múltiples matchers `remote_ip` por named matcher, y sus rangos se combinarán con OR.

#### Example:

Hacer match de solicitudes desde direcciones IPv4 privadas:

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Este matcher se combina frecuentemente con [`not`](#not) para invertir el match. Por ejemplo, para abortar todas las conexiones desde direcciones IPv4 y IPv6 _públicas_ (lo opuesto a todos los rangos privados):

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

En una [expresión CEL](#expression), se vería así:

```caddy-d
@my-friends `remote_ip('12.23.34.45', '23.34.45.56')`
```


---
### vars

```caddy-d
vars <variable> <values...>

expression vars({'<variable>': '<value>'})
expression vars({'<variable>': ['<values...>']})
```

Por el valor de una variable en el contexto de la solicitud o el valor de un placeholder. Se pueden indicar múltiples valores para hacer match con cualquiera de esos valores (OR).

El argumento **&lt;variable&gt;** puede ser el nombre de una variable o un placeholder entre llaves `{ }`. (Los placeholders no se expanden en el primer parámetro.)

Este matcher es más útil cuando se combina con la directiva [`map`](/docs/caddyfile/directives/map) que genera valores, con la directiva [`vars`](/docs/caddyfile/directives/vars`) dentro de tus rutas, o con plugins que establecen información en el contexto de la solicitud.

#### Example:

Hacer match de una salida de la directiva [`map`](/docs/caddyfile/directives/map) llamada `magic_number` para los valores `3` o `5`:

```caddy-d
vars {magic_number} 3 5
```

Hacer match del valor de un placeholder arbitrario, por ejemplo el ID de usuario autenticado, ya sea `Bob` o `Alice`:

```caddy-d
vars {http.auth.user.id} Bob Alice
```

Un ejemplo completo usando la directiva [`vars`](/docs/caddyfile/directives/vars) para establecer una variable y luego hacer match sobre ella con [`vars matcher`](#vars). Aquí combinamos dos cabeceras de solicitud en una variable y hacemos match con esa variable:

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "You sent Foo=123 and Bar=456!"
	}
	handle {
		respond "Foo and Bar were not special."
	}
}
```

En una [expresión CEL](#expression), sería así:

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---
<a id="vars-regexp"></a>
### vars_regexp

```caddy-d
vars_regexp [<name>] <variable> <regexp>

expression vars_regexp('<name>', '<variable>', '<regexp>')
expression vars_regexp('<variable>', '<regexp>')
```

Como [`vars`](#vars), pero soporta expresiones regulares.

El lenguaje de expresiones usado es RE2, incluido en Go. Consulta la [referencia de sintaxis RE2](https://github.com/google/re2/wiki/Syntax) y la [visión general de sintaxis regexp de Go](https://pkg.go.dev/regexp/syntax).

Desde v2.8.0, si no se proporciona `name`, el nombre se tomará del named matcher. Por ejemplo, un named matcher `@foo` hará que este matcher se llame `foo`. La principal ventaja de especificar un nombre es cuando se usan más de un matcher regexp en el mismo named matcher (por ejemplo, `vars_regexp` y [`header_regexp`](#header-regexp)).

Los grupos de captura se pueden acceder mediante un [placeholder](/docs/caddyfile/concepts#placeholders) en directivas después del match:
- `{re.<name>.<capture_group>}` donde:
  - `<name>` es el nombre de la expresión regular,
  - `<capture_group>` es el nombre o número del grupo de captura en la expresión.

- `{re.<capture_group>}` sin nombre también se rellena por conveniencia. El detalle es que si se usan varios regex en secuencia, los valores del placeholder se sobrescribirán por el siguiente matcher.

El grupo `0` es la coincidencia completa de la regexp, `1` el primer capture group, `2` el segundo y así sucesivamente. Por lo tanto, `{re.foo.1}` o `{re.1}` contendrán ambos el valor del primer grupo.

Solo se admite una expresión regular por nombre de variable, ya que los patrones regexp no se pueden combinar; si necesitas más, considera usar un [`expression matcher`](#expression). Los matches sobre variables distintas se combinan con AND.

#### Example:

Hacer match de la salida de [`map`](/docs/caddyfile/directives/map) llamada `magic_number` para un valor que empiece por `4`, capturando el valor en un capture group al que se puede acceder con `{re.magic.1}` o `{re.1}`:

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

Esto puede simplificarse omitiendo el nombre, que se deducirá del named matcher:

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

En una [expresión CEL](#expression), sería así:

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
```
