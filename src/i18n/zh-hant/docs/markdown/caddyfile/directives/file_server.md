---
title: file_server (Caddyfile 指令)
---

<script>
ready(function() {
	// Fix inline browse arg
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

<a id="file-server"></a>
# file_server

一個支持真實和虛擬文件系統的靜態文件服務器。它通過將請求的 URI 路徑附加到 [站點根路徑](root) 來形成文件路徑。

默認情況下，它執行規範的 URI；這意味著對於不以斜槓結尾的目錄請求（以添加它），或者對於具有斜槓的文件請求（以刪除它），將發出 HTTP 重定向。但是，如果內部重寫修改了路徑的最後一個元素（文件名），則不會發出重定向。

通常，`file_server` 指令與 [`root`](root) 指令配對使用，為整個站點設置文件根目錄。此指令也有一個 `root` 子指令（見下文）僅為此處理程序設置根目錄（不推薦）。請注意，站點根目錄不帶有沙箱保證：文件服務器確實防止路徑組件的目錄遍歷，但根目錄內的符號鏈接仍然可以允許訪問根目錄之外的內容。

當發生錯誤時（例如找不到文件 `404`，權限被拒絕 `403`），將調用錯誤路由。使用 [`handle_errors`](handle_errors) 指令定義錯誤路由，並顯示自定義錯誤頁面。

使用 `browse` 時，默認輸出由 HTML 模板生成。客戶端可以分別使用 `Accept: application/json` 或 `Accept: text/plain` 標頭請求 JSON 或純文本形式的目錄列表。JSON 輸出對於腳本編寫很有用，而純文本輸出對於人類終端使用很有用。


<a id="syntax"></a>
## 語法

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <path>
	hide          <files...>
	index         <filenames...>
	browse        [<template_file>] {
		reveal_symlinks
		sort <sort_field> [<direction>]
		file_limit <number>
	}
	precompressed [<formats...>]
	status        <status>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> 指定要使用的替代（可能是虛擬）文件系統。任何在 `caddy.fs` 命名空間中的 Caddy 模塊都可以在這裡使用。任何根路徑/前綴仍然適用於替代文件系統模塊。默認情況下，使用本地磁盤。

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 引入了 [`--embed` 標誌](https://github.com/caddyserver/xcaddy#custom-builds) 以將文件系統樹嵌入到自定義 Caddy 構建中，並註冊了一個名為 `embedded` 的 `fs` 模塊，允許您的靜態站點作為 Caddy 可執行文件分發。

- **root** <span id="root"/> 設置站點根路徑。它與 [`root`](root) 指令類似，不同之處在於它僅適用於此文件服務器實例，並覆蓋可能已定義的任何其他站點根目錄。默認值：`{http.vars.root}` 或當前工作目錄。注意：此子指令僅更改此處理程序的根目錄。為了讓其他指令（如 [`try_files`](try_files) 或 [`templates`](templates)）知道相同的站點根目錄，請改用 [`root`](root) 指令。

- **hide** <span id="hide"/> 是要隱藏的文件或文件夾列表；如果被請求，文件服務器將假裝它們不存在。接受 placeholder 和通配符模式。請注意，這些是 *文件系統* 路徑，而不是請求路徑。換句話說，相對路徑使用當前工作目錄作為基礎，而不是站點根目錄；並且在比較之前，所有路徑都會轉換為其絕對形式（如果可能）。指定不帶路徑分隔符的文件名或模式將隱藏所有具有匹配名稱的文件，無論其位置如何；否則，將嘗試進行路徑前綴匹配，然後是通配符匹配。由於這是 Caddyfile 配置，默認情況下將添加活動配置文件。隱藏比較區分大小寫；在不區分大小寫的文件系統上，不同大小寫的請求路徑仍可能解析為磁盤上的相同路徑，因此 `hide` 不應被視為敏感路徑的安全邊界。

- **index** <span id="index"/> 是要作為索引文件查找的文件名列表。默認值：`index.html index.txt`

- **browse** <span id="browse"/> 為沒有索引文件的目錄請求啟用文件列表。

  - **<template_file>** <span id="template_file"/> 是用於目錄列表的可選自定義模板文件。默認為可以使用命令 `caddy file-server export-template` 提取的模板，該命令將默認模板打印到標準輸出。嵌入的模板也可以在 [源代碼中的這裡 ![外部鏈接](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html) 找到。Browse 模板也可以使用來自 [標準 templates 模塊](/docs/modules/http.handlers.templates#docs) 的動作。

  - **reveal_symlinks** <span id="reveal_symlinks"/> 在目錄列表中啟用顯示符號鏈接的目標。默認情況下，符號鏈接目標是隱藏的，僅顯示鏈接文件本身。

  - **sort** <span id="sort"/> 更改目錄列表的默認排序。第一個參數是要排序的字段/列：`name`、`namedirfirst`、`size` 或 `time`。第二個參數是可選的方向：`asc` 或 `desc`。例如，`sort name desc` 將按名稱降序排列。

  - **file_limit** <span id="file_limit"/> 設置要在目錄列表中顯示的最大文件數。默認值：`10000`。如果文件數量超過此限制，則僅顯示前 N 個文件，其中 N 是指定的限制。

- **precompressed** <span id="precompressed"/> 是要搜索預壓縮掛件文件的編碼格式列表。參數是要搜索預壓縮 [掛件文件](https://en.wikipedia.org/wiki/Sidecar_file) 的編碼格式有序列表。支持的格式有 `gzip` (`.gz`)、`zstd` (`.zst`) 和 `br` (`.br`)。如果省略格式，則默認為 `br zstd gzip`（按此順序）。

  所有文件查找都將首先查找未壓縮文件是否存在。一旦找到，Caddy 將查找具有每個啟用格式文件擴展名的掛件文件。如果找到了預壓縮掛件文件，Caddy 將響應預壓縮文件，並適當地設置 `Content-Encoding` 響應標頭。否則，Caddy 將照常響應未壓縮文件。如果啟用了 [`encode` 指令](encode)，則如果未預壓縮，它可能會實時壓縮響應。

- **status** <span id="status"/> 是編寫響應時要使用的可選狀態碼覆蓋。在響應帶有 [自定義錯誤頁面](handle_errors) 的請求時特別有用。可以是 3 位數字的狀態碼，例如：`404`。支持 placeholder。默認情況下，寫入的狀態碼通常為 `200`，或者是部分內容的 `206`。

- **disable_canonical_uris** <span id="disable_canonical_uris"/> 禁用重定向的默認行為（如果請求路徑是目錄則添加末尾斜槓，或者如果請求路徑是文件則刪除末尾斜槓）。請注意，默認情況下，如果請求路徑的最後一個元素（文件名）經歷了內部重寫，則不會發生規範化，以避免用隱含行為破壞顯式重寫。

- **pass_thru** <span id="pass_thru"/> 啟用透傳模式，如果請求的文件未找到，則繼續執行路由中的下一個 HTTP 處理程序，而不是觸發 `404` 錯誤（調用 [`handle_errors`](handle_errors) 路由）。實際上，這僅在包含其他 handler 指令跟隨 `file_server` 的 [`route`](route) 塊內有用，因為此指令實際上 [排序最後](/docs/caddyfile/directives#directive-order)。


<a id="examples"></a>
## 示例

當前目錄外的靜態文件服務器：

```caddy-d
file_server
```

啟用文件列表：

```caddy-d
file_server browse
```

僅服務 `/static` 文件夾中的靜態文件：

```caddy-d
file_server /static/*
```

`file_server` 指令通常與 [`root` 指令](root) 配對使用，以設置服務文件的根路徑：

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

如果您將 Caddy 作為 systemd 服務運行，從 `/home` 讀取文件將不起作用，因為 `caddy` 用戶在 `/home` 目錄上沒有 “執行” 權限（遍歷所必需的）。建議您將文件放在 `/srv` 或 `/var/www/html` 中。

</aside>


隱藏所有 `.git` 文件夾及其內容：

```caddy-d
file_server {
	hide .git
}
```

如果客戶端支持（`Accept-Encoding` 標頭），則檢查請求文件旁邊是否存在預壓縮文件。因此，如果請求 `/path/to/file`，它會按順序檢查 `/path/to/file.br`、`/path/to/file.zst` 和 `/path/to/file.gz`，並服務第一個可用的文件及其對應的 `Content-Encoding`：

```caddy-d
file_server {
	precompressed
}
```
