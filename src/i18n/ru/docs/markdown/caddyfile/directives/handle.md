---
title: handle (директива Caddyfile)
---

# handle

Выполняет группу директив взаимно исключительно относительно других блоков `handle` на том же уровне вложенности.

Иными словами, когда несколько директив `handle` идут последовательно, будет выполнен только первый *совпавший* блок `handle`. `handle` без matcher действует как *fallback* route.

Директивы `handle` сортируются по своим matchers согласно [алгоритму сортировки директив](/docs/caddyfile/directives#sorting-algorithm). Директива [`handle_path`](handle_path) — особый случай: она сортируется с тем же приоритетом, что и `handle` с path matcher.

Блоки handle при необходимости можно вкладывать друг в друга. Внутри блоков handle можно использовать только HTTP handler directives.

<a id="syntax"></a>
## Синтаксис

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **<directives...>** — список HTTP handler directives или блоков директив, по одному в строке, как если бы они использовались вне блока handle.



<a id="similar-directives"></a>
## Похожие директивы

Есть и другие директивы, которые могут оборачивать HTTP handler directives, но каждая используется в зависимости от поведения, которое вы хотите выразить:

- [`handle_path`](handle_path) делает то же, что и `handle`, но удаляет prefix из запроса перед запуском своих handlers.

- [`handle_errors`](handle_errors) похожа на `handle`, но вызывается только когда Caddy сталкивается с ошибкой во время обработки запроса.

- [`route`](route) оборачивает другие директивы, как и `handle`, но с двумя отличиями:
  1. блоки route не являются взаимно исключающими,
  2. директивы внутри route не [переупорядочиваются](/docs/caddyfile/directives#directive-order), что при необходимости дает больше контроля.



<a id="examples"></a>
## Примеры

Обрабатывать запросы в `/foo/` статическим файловым сервером, а остальные запросы — reverse proxy:

```caddy
example.com {
	handle /foo/* {
		file_server
	}

	handle {
		reverse_proxy 127.0.0.1:8080
	}
}
```

Можно смешивать `handle` и [`handle_path`](handle_path) в одном site, и они все равно будут взаимно исключающими:

```caddy
example.com {
	handle_path /foo/* {
		# Prefix "/foo" удаляется из path
	}

	handle /bar/* {
		# Path все еще сохраняет "/bar"
	}
}
```

Можно вкладывать блоки `handle`, чтобы создавать более сложную routing logic:

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# Этот блок совпадает только с paths внутри /foo/bar
		}

		handle {
			# Этот блок совпадает со всем остальным внутри /foo/
		}
	}

	handle {
		# Этот блок совпадает со всем остальным (работает как fallback)
	}
}
```
