---
title: templates (директива Caddyfile)
---

# templates

Выполняет response body как документ [template](/docs/modules/http.handlers.templates). Templates предоставляют функциональные primitives для создания простых dynamic pages. Возможности включают HTTP subrequests, HTML file includes, Markdown rendering, JSON parsing, базовые data structures, randomness, time и другое.

<aside class="tip">

Templates могут выполняться над response body из *любого* источника — будь то статический файл на диске или проксируемый веб-сервис. Разумно включать выполнение templates только для контента, которому вы доверяете, который контролируете и/или санитизируете! Неправильная настройка может привести к нарушениям безопасности. Например, если проксируемое приложение позволяет пользователям писать/публиковать контент, и этот контент содержит текст, похожий на template actions, это позволит произвольным пользователям выполнять templates и потенциально получить доступ к окружению, локальным файлам и сети. Не включайте templates для пользовательского контента (без санитизации).

</aside>


<a id="syntax"></a>
## Синтаксис

```caddy-d
templates [<matcher>] {
	mime    <types...>
	between <open_delim> <close_delim>
	root    <path>
	extensions {
		<name> {
			...
		}
	}
}
```

- **mime** — MIME types, на которые будет действовать templates middleware; любые responses без подходящего `Content-Type` не будут вычисляться как templates.

  По умолчанию: `text/html text/plain`.

- **between** — opening и closing delimiters для template actions. Их можно изменить, если они конфликтуют с остальным документом.

  По умолчанию: `{{printf "{{ }}"}}`.

- **root** — site root при использовании функций, обращающихся к файловой системе.

  По умолчанию берется site root, заданный директивой [`root`](root), или текущий рабочий каталог, если он не задан.

- **extensions** позволяет зарегистрировать custom template functions, предоставленные modules в namespace `http.handlers.templates.functions.*`.

  Каждая поддиректива внутри блока соответствует module name. Эти modules могут добавлять custom functions в template function map, обычно для реализации reusable components. Эта возможность в первую очередь предназначена для plugins.

Документацию по встроенным template functions можно найти в [templates module](/docs/modules/http.handlers.templates#docs).



<a id="examples"></a>
## Примеры

Полный пример site, использующего templates для обслуживания markdown, смотрите в source [этого сайта](https://github.com/caddyserver/website)! В частности, посмотрите [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile) и [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html).

Включить templates для static site:

```caddy
example.com {
	root /srv
	templates
	file_server
}
```

Чтобы отдать простой static response с помощью template, обязательно задайте `Content-Type`:

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `Current year is: {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

Использование template extension (plugin):

```caddy
example.com {
	root /srv
	templates {
		extensions {
			# Требуется plugin caddy-hitcounter:
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
```
