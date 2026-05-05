---
title: Response-Matcher (Caddyfile)
---

<script>
ready(function() {
	// Response matchers
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

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

<a id="response-matchers"></a>
# Response-Matcher

**Response-Matcher** können verwendet werden, um Responses nach bestimmten Kriterien zu filtern (oder zu klassifizieren).

Sie erscheinen typischerweise nur als Konfiguration innerhalb bestimmter anderer Direktiven, um Entscheidungen über die Response zu treffen, während sie an den Client geschrieben wird.

- [Syntax](#syntax)
- [Matcher](#matchers)
	- [status](#status)
	- [header](#header)

<a id="syntax"></a>
## Syntax

Wenn eine Direktive Response-Matcher akzeptiert, wird die Verwendung in der Syntaxdokumentation entweder als `[<response_matcher>]` oder als `[<inline_response_matcher>]` dargestellt.

- Das Token **<response_matcher>** kann der Name eines zuvor deklarierten benannten Response-Matchers sein. Zum Beispiel: `@name`.
- Das Token **<inline_response_matcher>** kann das Response-Kriterium selbst sein, ohne vorherige Deklaration. Zum Beispiel: `status 200`.

### Benannt

```caddy-d
@name {
	status <code...>
	header <field> [<value>]
}
```
Wenn nur ein Aspekt der Response für die Direktive relevant ist, können Sie den Namen und das Kriterium in dieselbe Zeile setzen:

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

<a id="matchers"></a>
## Matcher

### status

```caddy-d
status <code...>
```

Nach HTTP-Statuscode.

- **&lt;code...&gt;** ist eine Liste von HTTP-Statuscodes. Sonderfälle sind Strings wie `2xx` und `3xx`, die auf alle Statuscodes im Bereich `200`-`299` beziehungsweise `300`-`399` matchen.

#### Beispiel:

```caddy-d
@success status 2xx
```



### header

```caddy-d
header <field> [<value>]
```

Nach Response-Header-Feldern.

- `<field>` ist der Name des zu prüfenden HTTP-Header-Felds.
	- Wenn `!` vorangestellt ist, darf das Feld nicht existieren, damit es matcht (value-Argument weglassen).
- `<value>` ist der Wert, den das Feld haben muss, um zu matchen.
	- Wenn `*` vorangestellt ist, wird ein schneller Suffix-Match ausgeführt (erscheint am Ende).
	- Wenn `*` angehängt ist, wird ein schneller Prefix-Match ausgeführt (erscheint am Anfang).
	- Wenn es von `*` eingeschlossen ist, wird ein schneller Substring-Match ausgeführt (erscheint irgendwo).
	- Andernfalls ist es ein schneller exakter Match.

Verschiedene Header-Felder innerhalb derselben Menge werden mit UND verknüpft. Mehrere Werte pro Feld werden mit ODER verknüpft.

Beachten Sie, dass Header-Felder wiederholt werden und unterschiedliche Werte haben können. Backend-Anwendungen MÜSSEN berücksichtigen, dass Header-Feldwerte Arrays sind, keine einzelnen Werte, und Caddy interpretiert in solchen Zweideutigkeiten keine Bedeutung.

#### Beispiel:

Responses matchen, deren Header `Foo` den Wert `bar` enthält:

```caddy-d
@upgrade header Foo *bar*
```

Responses matchen, deren Header `Foo` den Wert `bar` ODER `baz` hat:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Responses matchen, die überhaupt kein Header-Feld `Foo` haben:

```caddy-d
@not_foo header !Foo
```
