---
title: abort (директива Caddyfile)
---

# abort

Предотвращает любой ответ клиенту, немедленно прерывая цепочку HTTP handler'ов и закрывая соединение. Любые параллельные активные HTTP streams в том же соединении прерываются.


<a id="syntax"></a>
## Синтаксис

```caddy-d
abort [<matcher>]
```

<a id="examples"></a>
## Примеры

Принудительно закрыть соединение, полученное для неизвестных доменов, при использовании wildcard-сертификата:

```caddy
*.example.com {
    @foo host foo.example.com
    handle @foo {
        respond "This is foo!" 200
    }

    handle {
		# Необработанные домены попадают сюда,
		# но мы не хотим принимать их запросы
        abort
    }
}
```
