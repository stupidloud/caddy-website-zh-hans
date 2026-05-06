---
title: route (директива Caddyfile)
---

# route

Выполняет группу директив буквально и как единый блок.

Директивы внутри блока route не будут [внутренне переупорядочены](/docs/caddyfile/directives#directive-order). В блоке route можно использовать только HTTP handler directives (директивы, которые добавляют handlers или middleware в chain).

Эта директива является особым случаем, потому что ее поддирективы также являются обычными директивами.


<a id="syntax"></a>
## Синтаксис

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **<directives...>** — список directives или блоков директив, по одному в строке, как и вне блока route; но эти директивы не будут переупорядочены. Можно использовать только HTTP handler directives.



<a id="utility"></a>
## Назначение

Директива `route` полезна в некоторых advanced use cases или edge cases, когда нужно получить полный контроль над частями HTTP handler chain.

Поскольку порядок выполнения HTTP middleware важен, Caddyfile обычно переупорядочивает directives после разбора, чтобы Caddyfile было проще использовать; не нужно беспокоиться о порядке, в котором вы их пишете.

Хотя [встроенный порядок](/docs/caddyfile/directives#directive-order) совместим с большинством sites, иногда нужно вручную управлять порядком — для всего site или только для его части. Именно для этого нужна директива `route`.

Для примера рассмотрим два terminating handlers: [`redir`](redir) и [`file_server`](file_server). Оба записывают ответ клиенту и не вызывают следующий handler в chain, поэтому для конкретного запроса выполнится только один из них. Какой должен быть первым? Обычно `redir` выполняется перед `file_server`, потому что redirect обычно нужен только в отдельных случаях, а files обслуживаются в общем случае.

Однако могут быть ситуации, когда первая директива (`file_server`) имеет более конкретный matcher, чем вторая (`redir`). Иными словами, нужно выполнять redirect в общем случае, а обслуживать только конкретный файл.

Можно попробовать такой Caddyfile (но он не будет работать как ожидается!):

```caddy
example.com {
	file_server /specific.html
	redir https://anothersite.com{uri}
}
```

Проблема в том, что после [сортировки directives](/docs/caddyfile/directives#sorting-algorithm) `redir` окажется перед `file_server`.

Но в этом случае matcher для `redir` (неявный [`*`](/docs/caddyfile/matchers#wildcard-matchers)) является superset matcher для `file_server` (`*` является superset для `/specific.html`).

К счастью, решение простое: оберните эти две директивы в блок `route`, чтобы гарантировать выполнение `file_server` перед `redir`:

```caddy
example.com {
	route {
		file_server /specific.html
		redir https://anothersite.com{uri}
	}
}
```

<aside class="tip">

Другой способ — сделать два matchers взаимно исключающими, но это быстро усложняется, если условий больше одного-двух. С директивой `route` взаимное исключение двух handlers неявно, потому что оба являются terminal handlers.

</aside>

Теперь `file_server` будет включен в chain перед `redir`, потому что порядок воспринимается буквально.



<a id="similar-directives"></a>
## Похожие директивы

Есть и другие директивы, которые могут оборачивать HTTP handler directives, но каждая используется в зависимости от поведения, которое вы хотите выразить:

- [`handle`](handle) оборачивает другие директивы, как и `route`, но с двумя отличиями: 1) блоки handle взаимно исключают друг друга, и 2) директивы внутри handle обычно [переупорядочиваются](/docs/caddyfile/directives#directive-order).

- [`handle_path`](handle_path) делает то же, что и `handle`, но удаляет prefix из запроса перед запуском своих handlers.

- [`handle_errors`](handle_errors) похожа на `handle`, но вызывается только когда Caddy сталкивается с ошибкой во время обработки запроса.



<a id="examples"></a>
## Примеры

Проксировать requests к `/api` как есть, а все остальные requests переписывать в зависимости от того, совпадают ли они с файлом на диске, иначе в `/index.html`. Затем этот файл обслуживается.

Поскольку [`try_files`](try_files) имеет более высокий directive order, чем [`reverse_proxy`](reverse_proxy), обычно он был бы отсортирован выше и выполнился первым; из-за этого все API requests были бы переписаны в `/index.html` и перестали бы совпадать с `/api*`, поэтому ни один из них не был бы проксирован и вместо этого завершился бы `404` от [`file_server`](file_server). Оборачивание всего в `route` гарантирует, что `reverse_proxy` всегда выполняется первым, до переписывания запроса.

```caddy
example.com {
	root /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

Это не единственное решение этой проблемы. Можно также использовать пару блоков [`handle`](handle): первый совпадает с `/api*` и выполняет `reverse_proxy`, а второй работает как fallback и обслуживает files. См. [этот пример](/docs/caddyfile/patterns#single-page-apps-spas) SPA.

</aside>
