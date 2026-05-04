---
title: "log_skip（Caddyfile 指令）"
---

# log_skip

跳过匹配请求的访问日志记录。

应与[`log`指令](log)配合使用，以跳过对您而言无关的请求日志记录。

在 v2.8.0 之前，该指令名为 `skip_log`，但为了与其他指令保持一致，现已更名。


## 语法

```caddy-d
log_skip [<matcher>]
```


## 示例

跳过对存储在子路径中的静态文件的访问日志记录：

```caddy
example.com {
	root /srv

	log
	log_skip /static*

	file_server
}
```


跳过对符合特定模式的请求进行访问日志记录；在此情况下，即跳过对具有特定扩展名的文件的日志记录：

```caddy-d
@skip path_regexp \.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```


如果匹配器位于一个已包含匹配器的路由内，则无需该匹配器。例如，针对文件服务器某个子路径的句柄：

```caddy-d
handle_path /static* {
	root /srv/static
	log_skip
	file_server
}
```
