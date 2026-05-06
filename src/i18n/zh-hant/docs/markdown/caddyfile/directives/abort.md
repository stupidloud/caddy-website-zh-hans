---
title: abort (Caddyfile 指令)
---

<a id="abort"></a>
# abort

透過立即中止 HTTP handler chain 並關閉連線，防止向用戶端發送任何回應。同一連線上的任何併發、活動中的 HTTP 資料流都將被中斷。

<a id="syntax"></a>
## Syntax

```caddy-d
abort [<matcher>]
```

<a id="examples"></a>
## Examples

當使用萬用字元憑證時，強制關閉接收自未知網域的連線：

```caddy
*.example.com {
    @foo host foo.example.com
    handle @foo {
        respond "This is foo!" 200
    }

    handle {
		# 未處理的網域會流轉到這裡，
		# 但我們不想接受這些請求
        abort
    }
}
```
