---
title: "方法（Caddyfile 指令）"
---

# 方法

更改请求的 HTTP 方法。


## 语法

```caddy-d
method [<matcher>] <method>
```

- **&lt;method&gt;** 是要将请求更改为的 HTTP 方法。


## 示例

更改以下路径下所有请求的方法： `/api` 为 `POST`:

```caddy-d
method /api* POST
```
