---
title: import (Caddyfile 指令)
---

<a id="import"></a>
# import

包含一個 [snippet](/docs/caddyfile/concepts#snippets) 或檔案，並將此指令替換為該 snippet 或檔案的內容。

此指令是一個特殊情況：它在解析結構之前就會被評估，且可以出現在 Caddyfile 的任何位置。

<a id="syntax"></a>
## 語法

```caddy-d
import <pattern> [<args...>] [{block}]
```

- **&lt;pattern&gt;** 是要包含的檔案名稱、glob pattern 或 [snippet](/docs/caddyfile/concepts#snippets) 的名稱。其內容將替換此行，就像該檔案的內容最初就出現在這裡一樣。

  如果找不到特定的檔案，則會報錯，但空的 glob pattern 則不視為錯誤。

  如果匯入的是特定檔案，且該檔案為空，則會發出警告。

  如果 pattern 是檔案名稱或 glob，它總是相對於 `import` 出現的檔案路徑。

  如果使用 glob pattern `*` 作為最後一個路徑段，隱藏檔案（即以 `.` 開頭的檔案）將被忽略。要匯入隱藏檔案，請使用 `.*` 作為最後一個段。
- **&lt;args...&gt;** 是要傳遞給匯入 tokens 的選擇性參數列表。此 placeholder 是一個特殊情況，它在 Caddyfile 解析時（Caddyfile-parse-time）而非執行時（run-time）進行評估。它們可以以多種形式使用，類似於 [Go 的 slice 語法](https://gobyexample.com/slices)：
  - `{args[n]}` 其中 `n` 是參數從 0 開始的索引位置
  - `{args[:]}` 插入所有參數
  - `{args[:m]}` 插入 `m` 之前的參數
  - `{args[n:]}` 插入從 `n` 開始的參數
  - `{args[n:m]}` 插入 `n` 到 `m` 範圍內的參數

  對於插入多個 tokens 的形式，placeholder **必須** 是一個獨立的 [token](/docs/caddyfile/concepts#tokens-and-quotes)，不能是另一個 token 的一部分。換句話說，它的前後必須有空格，且不能包含在引號中。

  請注意，在 v2.7.0 之前，語法為 `{args.N}`，但此形式已被棄用，轉而使用上述更靈活的語法。

⚠️ <i>實驗性功能</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** 是要傳遞給匯入 tokens 的選擇性區塊（block）。此 placeholder 是一個特殊情況，它在 Caddyfile 解析時遞迴評估，而非執行時。它們可以以兩種形式使用：
  - `{block}` 整個提供的區塊內容將替換該 placeholder
  - `{blocks.key}` 其中 `key` 是所提供區塊內參數的第一個 token


<a id="examples"></a>
## 範例

匯入相鄰 sites-enabled 資料夾中的所有檔案（隱藏檔案除外）：

```caddy-d
import sites-enabled/*
```

使用匯入參數來匯入設定 CORS 標頭的 snippet：

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

匯入一個將代理 upstream 列表作為參數的 snippet：

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

匯入一個建立代理的 snippet，其中第一個參數為路徑前綴重寫規則：

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ <i>實驗性功能</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

匯入一個使用可設定的 "hello world" 訊息和 content-type 進行回應的 snippet：

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

匯入一個為 reverse_proxy 提供可擴展選項的 snippet：

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

匯入一個可以提供任何指令集，但帶有預先載入 middleware 的 snippet：

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
```
