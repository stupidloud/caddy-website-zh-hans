---
title: push (директива Caddyfile)
---

# push

Настраивает server на упреждающую отправку resources клиенту с помощью HTTP/2 server push.

Resources можно связать для server push, указав Link header(s) ответа. Эта директива автоматически push resources, описанные upstream Link headers в таких форматах:

- `<resource>; as=script`
- `<resource>; as=script,<resource>; as=style`
- `<resource>; nopush`
- `<resource>;<resource2>;...`

где `<resource>` начинается с forward slash `/` (т. е. является URI path с тем же host). Push возможен только для resources на том же host. Если связанный resource внешний или имеет атрибут `nopush`, он не будет push.

По умолчанию push requests включают некоторые headers, которые считаются безопасными для копирования из исходного запроса:

- Accept-Encoding
- Accept-Language
- Accept
- Cache-Control
- User-Agent

поскольку предполагается, что многие requests без этих headers завершились бы ошибкой; их не нужно настраивать вручную.

Push requests виртуализируются внутри, поэтому они очень легковесные.


<a id="syntax"></a>
## Синтаксис

```caddy-d
push [<matcher>] [<resource>] {
	[GET|HEAD] <resource>
	headers {
		[+]<field> [<value|regexp> [<replacement>]]
		-<field>
	}
}
```

- **&lt;resource&gt;** — target URI path для push. При использовании внутри блока перед ним опционально может быть method (GET или POST; по умолчанию GET).
- **&lt;headers&gt;** изменяет headers push request с тем же синтаксисом, что и [директива `header`](/docs/caddyfile/directives/header). Некоторые headers переносятся по умолчанию и не требуют явной настройки (см. выше).



<a id="examples"></a>
## Примеры

Push любых resources, описанных headers `Link` в ответе:

```caddy-d
push
```

То же самое, но также push `/resources/style.css` для всех requests:

```caddy-d
push * /resources/style.css
```

Push `/foo.jpg` только когда клиент запрашивает `/foo.html`:

```caddy-d
push /foo.html /foo.jpg
```
