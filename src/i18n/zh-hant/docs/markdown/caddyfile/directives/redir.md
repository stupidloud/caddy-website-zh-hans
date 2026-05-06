---
title: redir (Caddyfile 指令)
---

<a id="redir"></a>
# redir

向用戶端發出 HTTP 重新導向。

此指令意味著匹配的請求將按原樣拒絕，並且用戶端應在不同的 URL 重試。因此，它的 [指令順序](/docs/caddyfile/directives#directive-order) 非常靠前。


<a id="syntax"></a>
## 語法

```caddy-d
redir [<matcher>] <to> [<code>]
```

- **&lt;to&gt;** 是目標位置。這將成為回應的 [`Location` 標頭 <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location)。

- **&lt;code&gt;** 是用於重新導向的 HTTP 狀態碼。可以是：

	- `3xx` 範圍內的正整數，或者是 `401`
	
	- `temporary` 用於臨時重新導向（`302`，這是預設值）
	
	- `permanent` 用於永久重新導向（`301`）
	
	- `html` 使用 HTML 文件執行重新導向（對於重新導向瀏覽器有用，但對 API 用戶端無效）
	
	- 包含狀態碼值的 placeholder



<a id="examples"></a>
## 範例

將所有請求重新導向到 `https://example.com`：

```caddy
www.example.com {
	redir https://example.com
}
```

同樣的操作，但透過附加 [`{uri}` placeholder](/docs/caddyfile/concepts#placeholders) 來保留現有的 URI：

```caddy
www.example.com {
	redir https://example.com{uri}
}
```

同樣的操作，但是是永久的：

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

將您的舊 `/about-us` 頁面重新導向到您的新 `/about` 頁面：

```caddy
example.com {
	redir /about-us /about
	reverse_proxy localhost:9000
}
```
