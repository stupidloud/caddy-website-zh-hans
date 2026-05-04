---
title: "request_header（Caddyfile 指令）"
---

# 请求头

操作请求中的 HTTP 头字段。它可以设置、添加和删除头字段值，或使用正则表达式进行替换。

如果您打算为代理设置而修改请求头，请改用 `reverse_proxy` ，因为这些操作会自动考虑代理环境。

要操作 HTTP 响应头，您可以使用 [`header`](header) 指令。


## 语法

```caddy-d
request_header [<matcher>] [[+|-]<field> [<value>|<find>] [<replace>]]
```

- **&lt;field&gt;** 是该标头字段的名称。

  如果没有前缀，则设置（覆盖）该字段。

  在 `+` 前缀，以添加该字段，而非覆盖（设置）已存在的字段；请求中可以出现多个该字段。

  在字段名前添加 `-` 前缀来删除该字段。该字段可使用前缀或后缀 `*` 通配符来删除所有匹配的字段。

- **&lt;value&gt;** 是标头字段的值，若要添加或设置该字段。

- **&lt;find&gt;** 是要搜索的子字符串或正则表达式。

- **&lt;replace&gt;** 是替换内容；若进行查找和替换操作，此项为必填。


## 示例

从请求中移除 Referer 标头：

```caddy-d
request_header -Referer
```

从请求中删除所有包含下划线的标头：

```caddy-d
request_header -*_*
```
