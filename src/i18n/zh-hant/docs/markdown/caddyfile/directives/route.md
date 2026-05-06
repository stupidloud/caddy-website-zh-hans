---
title: route (Caddyfile 指令)
---

<a id="route"></a>
# route

按照字面意思將一組指令作為一個單元進行評估。

包含在 `route` 塊中的指令不會在 [內部重新排序](/docs/caddyfile/directives#directive-order)。只有 HTTP handler 指令（向鏈中添加 handler 或 middleware 的指令）可以在 `route` 塊中使用。

此指令是一個特例，其子指令也是常規指令。


<a id="syntax"></a>
## 語法

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **<directives...>** 是一組指令或指令塊，每行一個，就像在 `route` 塊之外一樣；不同之處在於這些指令不會被重新排序。只有 HTTP handler 指令可以使用。



<a id="utility"></a>
## 用途

`route` 指令在某些進階使用場景或邊緣情況下非常有用，可以用來絕對控制 HTTP handler 鏈的部分內容。

由於 HTTP middleware 的評估順序非常重要，Caddyfile 通常會在解析後重新排序指令，以便讓 Caddyfile 更易於使用；你不需要擔心輸入的順序。

雖然 [內置順序](/docs/caddyfile/directives#directive-order) 適用於大多數網站，但有時你需要手動控制順序，無論是針對整個網站還是其中的一部分。這就是 `route` 指令的作用。

為了說明這一點，考慮兩個終端 handler 的情況：[`redir`](redir) 和 [`file_server`](file_server)。兩者都會向客戶端寫入響應，並且不會調用鏈中的下一個 handler，因此對於某個請求，只有其中一個會被執行。那麼哪一個先執行呢？通常情況下，`redir` 會在 `file_server` 之前執行，因為通常你只想在特定情況下發出重定向，而在一般情況下提供文件服務。

然而，有時第一個指令（`file_server`）可能比第二個指令（`redir`）具有更具體的 matcher。換句話說，你希望在一般情況下進行重定向，而只提供特定文件的服務。

因此，你可能會嘗試像這樣的 Caddyfile（但這不會按預期工作！）：

```caddy
example.com {
	file_server /specific.html
	redir https://anothersite.com{uri}
}
```

問題在於，在 [指令排序](/docs/caddyfile/directives#sorting-algorithm) 之後，`redir` 會排在 `file_server` 之前。

但在這種情況下，`redir` 的 matcher（一個隱式的 [`*`](/docs/caddyfile/matchers#wildcard-matchers)）是 `file_server` matcher（`*` 是 `/specific.html` 的超集）的超集。

幸運的是，解決方案很簡單：只需將這兩個指令包裝在 `route` 塊中，以確保 `file_server` 在 `redir` 之前執行：

```caddy
example.com {
	route {
		file_server /specific.html
		redir https://anothersite.com{uri}
	}
}
```

<aside class="tip">

另一種方法是使這兩個 matcher 互斥，但如果有兩個以上的條件，這會很快變得複雜。使用 `route` 指令，這兩個 handler 的互斥性是隱式的，因為它們都是終端 handler。

</aside>

現在 `file_server` 將排在 `redir` 之前，因為順序是按字面意思採用的。



<a id="similar-directives"></a>
## 類似指令

還有其他指令可以包裝 HTTP handler 指令，但每種指令都有其用途，具體取決於你想要傳達的行為：

- [`handle`](handle) 像 `route` 一樣包裝其他指令，但有兩個區別：1) handle 塊彼此互斥，2) handle 內的指令會正常 [重新排序](/docs/caddyfile/directives#directive-order)。

- [`handle_path`](handle_path) 的作用與 `handle` 相同，但在運行其 handler 之前會從請求中剝離前綴。

- [`handle_errors`](handle_errors) 與 `handle` 類似，但僅在 Caddy 在請求處理過程中遇到錯誤時才被調用。



<a id="examples"></a>
## 範例

將 `/api` 的請求原樣代理，並根據其他所有請求是否匹配磁碟上的文件進行重寫，否則重寫為 `/index.html`。然後提供該文件。

由於 [`try_files`](try_files) 的指令優先級高於 [`reverse_proxy`](reverse_proxy)，通常會被排在更高位置並首先運行；這會導致 API 請求全部被重寫為 `/index.html` 且無法匹配 `/api*`，因此它們都不會被代理，而是會從 [`file_server`](file_server) 得到 `404` 錯誤。將其全部包裝在 `route` 中可確保 `reverse_proxy` 始終在請求被重寫之前首先運行。

```caddy
example.com {
	root /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

這不是此問題的唯一解決方案。你還可以使用一對 [`handle`](handle) 塊，第一個匹配 `/api*` 到 `reverse_proxy`，第二個作為備選並提供文件。請參閱 SPA 的 [此範例](/docs/caddyfile/patterns#single-page-apps-spas)。

</aside>
