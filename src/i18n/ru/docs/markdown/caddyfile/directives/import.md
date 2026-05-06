---
title: import (директива Caddyfile)
---

# import

Включает [snippet](/docs/caddyfile/concepts#snippets) или файл, заменяя эту директиву содержимым snippet или файла.

Эта директива является особым случаем: она вычисляется до разбора структуры и может появляться где угодно в Caddyfile.

<a id="syntax"></a>
## Синтаксис

```caddy-d
import <pattern> [<args...>] [{block}]
```

- **&lt;pattern&gt;** — имя файла, glob pattern или имя [snippet](/docs/caddyfile/concepts#snippets), который нужно включить. Его содержимое заменит эту строку так, как если бы содержимое файла изначально находилось здесь.

  Если конкретный файл не найден, это ошибка, но пустой glob pattern ошибкой не является.

  При импорте конкретного файла будет выдано предупреждение, если файл пуст.

  Если pattern является именем файла или glob, он всегда относится к файлу, в котором появляется `import`.

  Если используется glob pattern `*` как последний сегмент пути, hidden files (т. е. файлы, начинающиеся с `.`) игнорируются. Чтобы импортировать hidden files, используйте `.*` как последний сегмент.
- **&lt;args...&gt;** — необязательный список аргументов, передаваемых импортируемым tokens. Этот placeholder является особым случаем и вычисляется во время разбора Caddyfile, а не во время выполнения. Их можно использовать в разных формах, похожих на [slice syntax в Go](https://gobyexample.com/slices):
  - `{args[n]}`, где `n` — 0-based positional index параметра
  - `{args[:]}`, где вставляются все аргументы
  - `{args[:m]}`, где вставляются аргументы перед `m`
  - `{args[n:]}`, где вставляются аргументы, начиная с `n`
  - `{args[n:m]}`, где вставляются аргументы в диапазоне между `n` и `m`

  Для форм, вставляющих много tokens, placeholder **должен** быть отдельным [token](/docs/caddyfile/concepts#tokens-and-quotes); он не может быть частью другого token. Иными словами, вокруг него должны быть пробелы, и он не может находиться в кавычках.

  Обратите внимание, что до v2.7.0 синтаксис был `{args.N}`, но эта форма была deprecated в пользу более гибкого синтаксиса выше.

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** — необязательный блок, передаваемый импортируемым tokens. Этот placeholder является особым случаем и вычисляется рекурсивно во время разбора Caddyfile, а не во время выполнения. Его можно использовать в двух формах:
  - `{block}`, где содержимое всего переданного блока подставляется вместо placeholder
  - `{blocks.key}`, где `key` — первый token параметра внутри переданного блока


<a id="examples"></a>
## Примеры

Импортировать все файлы из соседней папки sites-enabled (кроме hidden files):

```caddy-d
import sites-enabled/*
```

Импортировать snippet, который устанавливает CORS headers с помощью аргумента import:

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

Импортировать snippet, который принимает список proxy upstreams как аргументы:

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

Импортировать snippet, который создает proxy с prefix rewrite rule в первом аргументе:

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Импортировать snippet, который отвечает настраиваемым сообщением "hello world" и content-type:

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

Импортировать snippet, который предоставляет расширяемые опции для reverse proxy:

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

Импортировать snippet, который обслуживает любой набор директив, но с предварительно загруженным middleware:

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
```
