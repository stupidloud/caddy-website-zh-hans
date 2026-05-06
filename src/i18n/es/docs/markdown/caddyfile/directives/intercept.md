---
title: intercept (Directiva de Caddyfile)
---

<script>
ready(function() {
	// Corrige los matchers de respuesta para que se rendericen con el color correcto
	// y enlaza con la sección de matchers de respuesta
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#response-matcher" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Matchers de respuesta
	const nameMatchers = Array.from($$_('pre.chroma .nd')).filter(item => item.innerText.includes('@name'));
	if (nameMatchers.length > 0) {
		const first = nameMatchers[0];
		const span = document.createElement('span');
		span.className = 'nd';
		first.parentNode.insertBefore(span, first);
		span.appendChild(first);
		span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;">@name</a>';
	}
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText === 'status') {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;">status</a>';
		}
	});
	
	const headerElements = $$_('pre.chroma .k');
	for (let item of headerElements) {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;">header</a>';
			break;
		}
	}

	// Agregaremos enlaces a todas las subdirectivas si se encuentra una etiqueta anchor coincidente en la página.
	addLinksToSubdirectives();
});
</script>

# intercept

Una abstracción generalizada de la característica de [intercepción de respuestas](reverse_proxy#intercepting-responses) de la directiva [`reverse_proxy`](reverse_proxy). Puede usarse con cualquier handler que genere respuestas, incluyendo los de plugins como `php_server` de [FrankenPHP](https://frankenphp.dev/).

Esta directiva te permite [coincidir respuestas](/docs/caddyfile/response-matchers), y se invocará la primera ruta `handle_response` coincidente o `replace_status`. Cuando se invoca, el cuerpo de respuesta original se retiene, dando a esa ruta la oportunidad de escribir un cuerpo de respuesta diferente, con un nuevo código de estado o con cualquier manipulación necesaria de encabezados de respuesta. Si la ruta no escribe un nuevo cuerpo de respuesta, se vuelve a escribir el cuerpo de respuesta original.


## Sintaxis

```caddy-d
intercept [<matcher>] {
	@name {
		status <code...>
		header <field> [<value>]
	}

	replace_status [<response_matcher>] <code>

	handle_response [<response_matcher>] {
		<directives...>
	}
}
```

- **@name** es un bloque de [response matcher](/docs/caddyfile/response-matchers) con nombre. Mientras cada response matcher tenga un nombre único, se pueden definir múltiples matchers. Una respuesta puede coincidir por código de estado y por la presencia o valor de un encabezado de respuesta.

- **replace_status** <span id="replace_status"/> simplemente cambia el código de estado de la respuesta cuando coincide con el matcher indicado.

- **handle_response** <span id="handle_response"/> define la ruta que se ejecutará cuando la respuesta original coincida con el response matcher indicado. Si se omite un matcher, se interceptan todas las respuestas. Cuando se definen varios bloques `handle_response`, se aplicará el primer bloque coincidente. Dentro del bloque se pueden usar todas las demás [directivas](/docs/caddyfile/directives).

Dentro de rutas `handle_response`, están disponibles los siguientes placeholders para extraer información de la respuesta original:

- `{resp.status_code}` es el código de estado de la respuesta original.

- `{resp.header.*}` son los encabezados de la respuesta original.


## Ejemplos

Cuando se usa `php_server` de [FrankenPHP](https://frankenphp.dev/), puedes usar `intercept` para implementar soporte de `X-Accel-Redirect`, sirviendo archivos estáticos según lo solicitado por la app PHP:

```caddy
localhost {
	root /srv

	intercept {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {resp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}

	php_server
}
```
