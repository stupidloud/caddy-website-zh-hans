---
title: Matchers de respuesta (Caddyfile)
---

<script>
ready(function() {
	// Matchers de respuesta
	$$_('pre.chroma .nd').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#syntax" style="color: inherit;">${text}</a>`;
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="#status" style="color: inherit;">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="#header" style="color: inherit;">header</a>';
		}
	});

	// Añadiremos enlaces a todos los subdirectores si existe ancla coincidente.
	addLinksToSubdirectives();
});
</script>

# Matchers de respuesta

Los **response matchers** se pueden usar para filtrar (o clasificar) respuestas por criterios concretos.

Normalmente solo aparecen dentro de ciertas directivas, para tomar decisiones sobre la respuesta mientras se escribe al cliente.

- [Sintaxis](#syntax)
- [Matchers](#matchers)
	- [status](#status)
	- [header](#header)

## Sintaxis
<a id="syntax"></a>

Si una directiva acepta response matchers, su sintaxis se representa como `[<response_matcher>]` o `[<inline_response_matcher>]`.

- El token **<response_matcher>** puede ser el nombre de un response matcher previamente definido. Por ejemplo: `@name`.
- El token **<inline_response_matcher>** puede ser el propio criterio de respuesta, sin declaración previa. Por ejemplo: `status 200`.

### Named

```caddy-d
@name {
	status <code...>
	header <field> [<value>]
}
```
Si solo un aspecto de la respuesta es relevante para la directiva, puedes poner nombre y criterio en la misma línea:

```caddy-d
@name status <code...>
```

### Inline

```caddy-d
... {
	status <code...>
	header <field> [<value>]
}
```
```caddy-d
... status <code...>
```
```caddy-d
... header <field> [<value>]
```

## Matchers

### status

```caddy-d
status <code...>
```

Por código de estado HTTP.

- **&lt;code...&gt;** es una lista de códigos de estado HTTP. Casos especiales son cadenas como `2xx` y `3xx`, que coinciden con todo el rango `200`-`299` y `300`-`399`, respectivamente.

#### Ejemplo:

```caddy-d
@success status 2xx
```



### header

```caddy-d
header <field> [<value>]
```

Por campos del encabezado de respuesta.

- `<field>` es el nombre del campo de encabezado HTTP a comprobar.
	- Si se antepone `!`, el campo no debe existir para que coincida (omite `value`).
- `<value>` es el valor que debe tener el campo para coincidir.
	- Si se antepone `*`, realiza coincidencia rápida por sufijo (al final).
	- Si se añade `*` al final, realiza coincidencia rápida por prefijo (al inicio).
	- Si se encierra entre `*`, realiza coincidencia rápida por subcadena (en cualquier parte).
	- En otros casos, es coincidencia exacta.

Los campos de encabezado distintos del mismo conjunto se combinan con AND. Valores múltiples por campo se combinan con OR.

Nota: los campos de encabezado pueden repetirse con distintos valores. Las aplicaciones de backend DEBEN considerar que los valores de campo de encabezado son arrays, no valores únicos, y Caddy no interpreta significados ambiguos.

#### Ejemplo:

Coincidir respuestas con encabezado `Foo` que contenga `bar`:

```caddy-d
@upgrade header Foo *bar*
```

Coincidir respuestas con encabezado `Foo` que tenga valor `bar` o `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Coincidir respuestas que no tengan en absoluto el campo `Foo`:

```caddy-d
@not_foo header !Foo
```
