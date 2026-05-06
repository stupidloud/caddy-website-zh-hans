---
title: log_name (директива Caddyfile)
---

# log_name

Переопределяет имя logger, используемое для запроса при записи access logs с помощью [директивы `log`](log).

Эта директива полезна, когда нужно записывать requests в разные файлы на основе некоторого условия, например request path или method.

Можно указать больше одного имени logger, чтобы log запроса отправлялся более чем в один совпадающий logger.

Часто используется вместе с опцией [`no_hostname`](log#no_hostname) директивы `log`, которая не дает logger связываться с каким-либо hostname из site block, так что только requests, которые устанавливают `log_name`, будут отправлять logs в этот logger.


<a id="syntax"></a>
## Синтаксис

```caddy-d
log_name [<matcher>] <names...>
```


<a id="examples"></a>
## Примеры

Может потребоваться записывать requests в разные файлы; например, health checks можно записывать в отдельный файл, отличный от основных access logs.

Использование `no_hostname` в `log` не дает logger связываться с каким-либо hostname из site block (т. е. здесь `localhost`), так что logs получат только requests, у которых `log_name` установлен в имя этого logger.

```caddy
localhost {
	log {
		output file ./caddy.access.log
	}

	log health_check_log {
		output file ./caddy.access.health.log
		no_hostname
	}

	handle /healthz* {
		log_name health_check_log
		respond "Healthy"
	}

	handle {
		respond "Hello World"
	}
}
```
