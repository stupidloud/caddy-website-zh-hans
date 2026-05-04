---
title: "log_name（Caddyfile 指令）"
---

# 日志名称

使用[`log`指令](log)写入访问日志时，覆盖请求所使用的日志器名称。

当您希望根据某些条件（例如请求路径或方法）将请求记录到不同的文件时，此指令非常有用。

可以指定多个日志记录器名称，这样请求的日志就会被推送到多个匹配的日志记录器中。

这通常与 `log` 指令的[`no_hostname`](log#no_hostname)选项配合使用，该选项可防止日志器与任何站点块的主机名相关联，从而确保只有设置了 `log_name` 的请求才会将日志推送到该日志器。


## 语法

```caddy-d
log_name [<matcher>] <names...>
```


## 示例

您可能希望将请求记录到不同的文件中，例如，您可能希望将健康检查日志记录到与主访问日志不同的文件中。

使用 `no_hostname` 在 `log` 可防止日志器与任何站点块的主机名相关联（即 `localhost` 此处），从而确保只有将 `log_name` 设置为该日志器名称的请求才会收到日志。

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
