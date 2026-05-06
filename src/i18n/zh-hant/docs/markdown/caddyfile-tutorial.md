---
title: Caddyfile 教程
---

<a id="caddyfile-tutorial"></a>
# Caddyfile 教程

本教程將教你 [HTTP Caddyfile](/docs/caddyfile) 的基礎知識，以便你快速輕鬆地生成美觀且功能齊全的網站配置。

**目標：**
- 🔲 第一個網站
- 🔲 靜態檔案伺服器
- 🔲 模板
- 🔲 壓縮
- 🔲 多個網站
- 🔲 Matchers
- 🔲 環境變數
- 🔲 註解

**先決條件：**
- 基礎終端機 / 命令列技能
- 基礎文字編輯器技能
- `caddy` 已加入你的 PATH

---

創建一個名為 `Caddyfile` 的新文字檔案（不含副檔名）。

你首先應該輸入的是網站的 [地址](/docs/caddyfile/concepts#addresses)：

```caddy
localhost
```

<aside class="tip">

如果 HTTP 和 HTTPS 埠（分別為 80 和 443）在你的作業系統上是特權埠，你將需要以提升的權限執行或使用較高的埠。要使用較高的埠，只需將地址更改為類似 `localhost:2015` 的形式，並使用 [http_port](/docs/caddyfile/options) Caddyfile 選項更改 HTTP 埠。

</aside>


接著按下 Enter 並輸入你想要執行的操作。在本教程中，請讓你的 Caddyfile 看起來像這樣：

```caddy
localhost

respond "Hello, world!"
```

保存檔案並執行 Caddy（由於這是教學課程，我們將使用 `--watch` 旗標，以便自動套用 Caddyfile 的更改）：

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

如果你遇到權限錯誤，請嘗試在地址中使用較高的埠（例如 `localhost:2015`）並 [更改 HTTP 埠](/docs/caddyfile/options)，或者使用提升的權限執行。

</aside>


第一次執行時，系統會詢問你的密碼。這是為了讓 Caddy 能透過 HTTPS 提供服務。

<aside class="tip">

只要主機名或 IP 是網站地址的一部分， Caddy 預設會透過 HTTPS 提供所有網站。可以透過在地址前明確加上 `http://` 來停用 [自動 HTTPS](/docs/automatic-https)。

</aside>


<aside class="complete">第一個網站</aside>

在瀏覽器中打開 [localhost](https://localhost)，查看你的網頁伺服器是否正常運作，且包含 HTTPS！

<aside class="tip">
	如果第一次遇到憑證錯誤，你可能需要重啟瀏覽器。
</aside>

這並不是特別令人興奮，所以讓我們將靜態回應更改為啟用目錄列表功能的 [file_server](/docs/caddyfile/directives/file_server)：

```caddy
localhost

file_server browse
```

保存你的 Caddyfile，然後重新整理瀏覽器標籤頁。你應該會看到檔案列表，或者如果當前目錄中存在 index 檔案，則會看到 HTML 頁面。

<aside class="complete">靜態檔案伺服器</aside>

<a id="adding-functionality"></a>
## 添加功能

讓我們對 file_server 做一些有趣的事情：提供模板化頁面。創建一個新檔案並貼入以下內容：

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Caddy tutorial</title>
	</head>
	<body>
		頁面載入時間：{{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

將其保存為當前目錄下的 `caddy.html`，並在瀏覽器中加載它：[https://localhost/caddy.html](https://localhost/caddy.html)

輸出結果為：

```
頁面載入時間：{{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

等一下。我們應該看到今天的日期。為什麼它不起作用？這是因為伺服器尚未配置為處理模板！修復起來很簡單，只需在 Caddyfile 中添加一行，如下所示：

```caddy
localhost

templates
file_server browse
```

保存後重新整理瀏覽器標籤頁。你應該會看到：

```
頁面載入時間：{{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

透過 Caddy 的 [templates 模組](/docs/modules/http.handlers.templates)，你可以對靜態檔案執行許多有用的操作，例如包含其他 HTML 檔案、發起子請求、設置回應 標頭、處理資料結構等等！

<aside class="complete">模板</aside>

使用快速且現代的壓縮演算法來壓縮回應是良好的做法。讓我們使用 [`encode`](/docs/caddyfile/directives/encode) 指令來啟用 Gzip 和 Zstandard 支援：

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">壓縮</aside>

這就是建立一個半進階、準備好用於生產環境的網站的基本流程！

當你準備好開啟 [自動 HTTPS](/docs/automatic-https) 時，只需將網站地址（在本教程中為 `localhost`）替換為你的網域名稱。更多資訊請參閱我們的 [HTTPS 快速入門指南](/docs/quick-starts/https)。

<a id="multiple-sites"></a>
## 多個網站

使用目前的 Caddyfile，我們只能有一個網站定義！只有第一行可以是網站的地址，檔案的其餘部分都必須是該網站的指令。

但要增加更多網站其實很容易！

我們目前的 Caddyfile：

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

等同於這一個：

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

除了第二個允許我們增加更多網站。

透過將網站區塊包裹在大括號 `{ }` 中，我們就能在同一個 Caddyfile 中定義多個不同的網站。

例如：

```caddy
:8080 {
	respond "I am 8080"
}

:8081 {
	respond "I am 8081"
}
```

將網站區塊包裹在大括號中時，只有 [地址](/docs/caddyfile/concepts#addresses) 出現在大括號外部，且只有 [指令](/docs/caddyfile/directives) 出現在大括號內部。

對於共享相同配置的多個網站，你可以添加更多地址，例如：

```caddy
:8080, :8081 {
	...
}
```

只要每個地址是唯一的，你就可以定義任意數量的不同網站。

<aside class="complete">多個網站</aside>


## Matchers

我們可能希望僅對某些請求套用某些指令。例如，假設我們想要同時擁有檔案伺服器和反向代理，但顯然我們不能對每個請求都執行這兩者！檔案伺服器會寫入靜態檔案的回應，或者反向代理會將請求傳遞給後端並寫回其回應。

此配置將無法按我們預期的方式運作（由於 [指令順序](/docs/caddyfile/directives#directive-order)，`reverse_proxy` 將具有優先權）：

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

在實務中，我們可能只想為 API 請求使用反向代理，即基本路徑為 `/api/` 的請求。這可以透過添加 [matcher token](/docs/caddyfile/matchers#syntax) 輕鬆實現：

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

好了；現在反向代理將優先處理所有以 `/api/` 開頭的請求。

我們剛剛添加的 `/api/*` 部分稱為 **matcher token** 。你可以判斷它是 matcher token，因為它以正斜線 `/` 開頭，且出現在指令的正後方（但你隨時可以在 [指令文檔](/docs/caddyfile/directives) 中查閱以確定）。

Matchers 非常強大。你可以聲明具名 matchers 並像 `@name` 這樣使用它們，以匹配請求路徑以外的更多內容！在繼續之前，請花點時間 [深入了解 matchers](/docs/caddyfile/matchers)！

<aside class="complete">Matchers</aside>

<a id="environment-variables"></a>
## 環境變數

Caddyfile 適配器允許在解析 Caddyfile 之前替換 [環境變數](/docs/caddyfile/concepts#environment-variables)。

首先，設置一個環境變數（在執行 Caddy 的同一個 shell 中）：

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

然後你可以在 Caddyfile 中像這樣使用它：

```caddy
{$SITE_ADDRESS}

file_server
```

在解析 Caddyfile 之前，它將被展開為：

```caddy
localhost:9055

file_server
```

你可以在 Caddyfile 的任何位置使用環境變數，用於任意數量的 token。

<aside class="complete">環境變數</aside>


<a id="comments"></a>
## 註解

最後一件對你非常有幫助的事情：如果你想在 Caddyfile 中標註或記錄任何內容，可以使用以 `#` 開頭的註解：

```caddy
# 這是一條註解
```

<aside class="complete">註解</aside>

<a id="further-reading"></a>
## 進階閱讀

- [Caddyfile 概念](/docs/caddyfile/concepts)
- [指令 (Directives)](/docs/caddyfile/directives)
- [常用模式](/docs/caddyfile/patterns)
