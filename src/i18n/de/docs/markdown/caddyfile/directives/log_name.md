---
title: log_name (Caddyfile directive)
---

# log_name

Überschreibt den Logger-Namen, der für einen Request beim Schreiben von Access Logs mit der Direktive [`log`](log) verwendet wird.

Diese Direktive ist nützlich, wenn Sie Requests abhängig von einer Bedingung, etwa Request-Pfad oder Methode, in verschiedene Dateien loggen möchten.

Es kann mehr als ein Logger-Name angegeben werden, sodass das Log des Requests an mehr als einen passenden Logger gesendet wird.

Dies wird häufig mit der Option [`no_hostname`](log#no_hostname) der Direktive `log` kombiniert. Sie verhindert, dass der Logger mit einem der Hostnamen des Site-Blocks verknüpft wird, sodass nur Requests, die `log_name` setzen, Logs an diesen Logger senden.


<a id="syntax"></a>
## Syntax

```caddy-d
log_name [<matcher>] <names...>
```


<a id="examples"></a>
## Beispiele

Möglicherweise möchten Sie Requests in verschiedene Dateien loggen; zum Beispiel Health Checks getrennt von den Haupt-Access-Logs.

Die Verwendung von `no_hostname` in einem `log` verhindert, dass der Logger mit einem der Hostnamen des Site-Blocks (hier also `localhost`) verknüpft wird. So erhalten nur Requests Logs, bei denen `log_name` auf den Namen dieses Loggers gesetzt ist.

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
