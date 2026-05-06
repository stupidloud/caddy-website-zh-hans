---
title: handle_path (директива Caddyfile)
---

<script>
ready(function() {
	// Add a link to [<path_matcher>] as a special case for this directive.
	// The matcher text includes <> characters which are parsed as HTML,
	// so we must use text() to change the link text.
	$$_('pre.chroma .s').forEach(item => {
		if (item.innerText.includes('<path_matcher>')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			item.innerHTML = `<a href="/docs/caddyfile/matchers#path-matchers" style="color: inherit;" title="Matcher token">${text}</a>`;
			item.classList.remove('s');
			item.classList.add('nd');
		}
	});
});
</script>

# handle_path

Работает так же, как [директива `handle`](handle), но неявно использует [`uri strip_prefix`](uri), чтобы удалить совпавший path prefix.

Обработка запроса, совпадающего с определенным path (с удалением этого path из request URI), достаточно распространенный сценарий, поэтому для удобства у него есть отдельная директива.


<a id="syntax"></a>
## Синтаксис

```caddy-d
handle_path <path_matcher> {
	<directives...>
}
```

- **<directives...>** — список HTTP handler directives или блоков директив, по одному в строке, как если бы они использовались вне блока `handle_path`.

Принимается и обязателен только один [path matcher](/docs/caddyfile/matchers#path-matchers); использовать named matchers с `handle_path` нельзя.

<a id="examples"></a>
## Примеры

Эта конфигурация:

```caddy-d
handle_path /prefix/* {
	...
}
```

👆 фактически эквивалентна этой 👇, но форма `handle_path` 👆 немного короче

```caddy-d
handle /prefix/* {
	uri strip_prefix /prefix
	...
}
```

Полный пример Caddyfile, где `handle_path` и `handle` взаимно исключают друг друга; но помните о [проблеме subfolder <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575)

```caddy
example.com {
	# Обслуживать API, удаляя prefix /api
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# Обслуживать статический сайт
	handle {
		root /srv
		file_server
	}
}
```
