---
title: "abort（Caddyfile 指令）"
---

# 中止

通过立即终止 HTTP 处理程序链并关闭连接，阻止向客户端发送任何响应。同一连接上所有并发且处于活动状态的 HTTP 流均会被中断。


## 语法

```caddy-d
abort [<matcher>]
```

## 示例

在使用通配符证书时，强制关闭针对未知域名的连接：

```caddy
*.example.com {
    @foo host foo.example.com
    handle @foo {
        respond "This is foo!" 200
    }

    handle {
		# 未处理的域名会跑到这里，
		# 但我们不接受它们的请求
        abort
    }
}
```
