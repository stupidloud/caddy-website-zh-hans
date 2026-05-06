---
title: 升級至 Caddy 2
---

<a id="upgrade-guide"></a>
升級指南
========

Caddy 2 是一個全新的代碼庫，從頭開始編寫，旨在對 Caddy 1 進行改進。Caddy 2 與 Caddy 1 不向下兼容。但請放心，對於大多數基礎設置，差異並不大。本指南將幫助您盡可能輕鬆地完成過渡。

本指南不會深入探討可用的新功能——順便說一下，這些功能真的很酷，您應該[學習它們](/docs/getting-started)——這裡的目標只是讓您快速上手並運行 Caddy 2。

- [重點摘要](#high-order-bits)
- [步驟](#steps)
- [HTTPS 和端口](#https-and-ports)
- [命令行](#command-line)
- [Caddyfile](#caddyfile)
	- [主要變化](#primary-changes)
	- [basicauth](#basicauth)
	- [browse](#browse)
	- [errors](#errors)
	- [ext](#ext)
	- [fastcgi](#fastcgi)
	- [gzip](#gzip)
	- [header](#header)
	- [log](#log)
	- [proxy](#proxy)
	- [redir](#redir)
	- [rewrite](#rewrite)
	- [root](#root)
	- [status](#status)
	- [templates](#templates)
	- [tls](#tls)
- [服務文件](#service-files)
- [插件](#plugins)
- [尋求幫助](#getting-help)



<a id="high-order-bits"></a>
## 重點摘要

- "Caddy 2" 仍然簡稱為 `caddy`。我們可能會使用 "Caddy 2" 來明確版本，以減少過渡時的困惑。
- 大多數用戶只需更換他們的 `caddy` 二進制文件和更新後的 `Caddyfile` 配置（在測試其正常工作後）。
- 最好在沒有 Caddy 1 假設的情況下進入 Caddy 2。
- 您可能無法在 v2 中完美地複製您在 v1 中的特殊配置。通常，這是有充分理由的。
- 命令行不再用於服務器配置。
- 配置不再需要環境變量。
- 為 Caddy 2 提供配置的主要方式是通過其 [API](/docs/api)，但也可以使用 [`caddy` 命令](/docs/command-line)。
- 您應該知道 Caddy 2 的原生配置語言是 [JSON](/docs/json/)，而 Caddyfile 只是另一個為您轉換為 JSON 的 [config adapter](/docs/config-adapters)。極其自定義/高級的使用場景可能需要 JSON，因為並非所有可能的配置都能通過 Caddyfile 表達。
- Caddyfile 大部分相同，但也功能更強大；指令（directives）已發生變化。



<a id="steps"></a>
## 步驟

1. 通過我們的[入門指南](/docs/getting-started)教程熟悉 Caddy 2。
2. 如果您還沒有執行第 1 步，請務必執行。說認真的——我們再怎麼強調至少知道如何使用 Caddy 2 有多重要都不為過。（這更有趣！）
3. 使用下面的指南過渡您的 `caddy` 命令。
4. 使用下面的指南過渡您的 Caddyfile。
5. 在本地或預發布環境中測試您的新配置。
6. 測試，測試，再測試
7. 部署並享受樂趣！



<a id="https-and-ports"></a>
## HTTPS 和端口

Caddy 的默認端口不再是 `:2015`。Caddy 2 的默認端口是 `:443`，或者如果不知道主機名/IP，則為端口 `:80`。您始終可以在配置中自定義端口。

Caddy 2 的默認協議是[*始終*為 HTTPS，如果已知主機名或 IP](/docs/automatic-https#overview)。這與 Caddy 1 不同，在 Caddy 1 中，默認情況下只有看起來像公共域名的域名才使用 HTTPS。現在，*每個* 站點都使用 HTTPS（除非您通過顯式指定端口 `:80` 或 `http://` 來禁用它）。

IP 地址和 localhost 域名將從[本地信任的內嵌 CA](/docs/automatic-https#local-https)獲取證書。所有其他域名將使用 ZeroSSL 或 Let's Encrypt。（這都是可配置的。）

證書和 ACME 資源的存儲結構已發生變化。Caddy 2 可能會為您的站點獲取新證書；但如果您有大量證書，如果它沒有自動為您完成，您可以手動遷移它們。有關詳細信息，請參閱 Issue [#2955](https://github.com/caddyserver/caddy/issues/2955) 和 [#3124](https://github.com/caddyserver/caddy/issues/3124)。



<a id="command-line"></a>
## 命令行

`caddy` 命令現在是 `caddy run`。

所有命令行標誌都不同。請移除它們；所有服務器配置現在都存在於實際的配置文檔中（通常是 Caddyfile 或 JSON）。您可能會在 [JSON structure](/docs/json/) 或 [Caddyfile global options](/docs/caddyfile/options) 中找到您需要的內容，以替換 v1 中的大部分命令行標誌。

像 `caddy -conf ../Caddyfile` 這樣的命令將變為 `caddy run --config ../Caddyfile`。

與以前一樣，如果您的 Caddyfile 在當前文件夾中， Caddy 將自動找到並使用它；在這種情況下，您不需要使用 `--config` 標誌。

信號（Signals）基本相同，但不再支持 USR1 和 USR2。請改用 [`caddy reload`](/docs/command-line#caddy-reload) 命令或 [API](/docs/api) 來加載新配置。

在沒有任何配置的情況下運行 `caddy` 過去是運行一個簡單的文件服務器。Caddy 2 中的等效命令是 [`caddy file-server`](/docs/command-line#caddy-file-server)。

環境變量不再相關，除了 `HOME`（以及可選的您設置的任何 `XDG_*` 變量）。`CADDYPATH` 已被 [OS 慣例](/docs/conventions#file-locations)取代。



<a id="caddyfile"></a>
## Caddyfile

[v2 Caddyfile](/docs/caddyfile/concepts) 與您已經熟悉的非常相似。您主要需要做的是更改您的指令。

⚠️ **務必閱讀新指令！** 特別是如果您的配置比較高級，有很多細節需要考慮。這些技巧將使您的大部分配置快速切換，但請閱讀每個指令的完整文檔，以便了解升級的影響。當然，在投入生產環境之前，請務必徹底測試您的配置。


<a id="primary-changes"></a>
### 主要變化

- 如果您正在提供靜態文件，則需要添加 [`file_server` 指令](/docs/caddyfile/directives/file_server)，因為 Caddy 2 默認不假定這一點。出於安全原因，Caddy 2 默認也不會探測 MIME；如果缺少 Content-Type，您可能需要使用 [header](/docs/caddyfile/directives/header) 指令自己設置標頭。

- 在 v1 中，您只能通過請求路徑過濾（或 "匹配"）指令。在 v2 中，[request matching](/docs/caddyfile/matchers) 功能要強大得多。任何在 HTTP 處理器鏈中添加中間件或以任何方式操作 HTTP 請求/響應的 v2 指令，都可以利用這種新的匹配功能。[閱讀更多關於 v2 request matchers 的信息。](/docs/caddyfile/matchers) 您需要了解它們才能理解 v2 Caddyfile。

- 雖然許多 [placeholders](/docs/conventions#placeholders) 相同，但也有許多已發生變化，現在有[許多新的 placeholders](/docs/modules/http#docs)，包括 [Caddyfile 的簡寫](/docs/caddyfile/concepts#placeholders)。

- Caddy 2 日誌都是結構化的，默認格式為 JSON。所有日誌級別都可以簡單地進入同一個日誌進行處理（但如果需要，您可以自定義）。

- 在 Caddy 1 中您按路徑前綴匹配請求的地方，Caddy 2 中的路徑匹配現在默認是精確匹配。如果您想匹配像 `/foo/` 這樣的前綴，您在 Caddy 2 中需要 `/foo/*`。

我們將在此處列出一些最常見 v1 指令，並說明如何將其轉換為在 v2 Caddyfile 中使用。

⚠️ **僅僅因為本頁面缺少 v1 指令並不意味著 v2 做不到！** 一些 v1 指令不再需要，或者轉換效果不佳，亦或是通過 v2 的其他方式實現。對於一些高級自定義，您可能需要深入到 JSON 才能獲得所需的內容。瀏覽[我們的文檔](/docs/caddyfile)以找到您需要的內容！


<a id="basicauth"></a>
### basicauth

HTTP Basic 認證仍然使用 [`basic_auth`](/docs/caddyfile/directives/basic_auth) 指令配置。然而，Caddy 2 配置不接受純文本密碼。您必須對它們進行哈希處理，[`caddy hash-password`](/docs/command-line#caddy-hash-password) 可以提供幫助。

- **v1:**
```
basicauth /secret/ Bob hiccup
```

- **v2:**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```


<a id="browse"></a>
### browse

現在通過 [`file_server`](/docs/caddyfile/directives/file_server) 指令啟用文件瀏覽。

- **v1:**
```
browse /subfolder/
```
- **v2:**
```caddy-d
file_server /subfolder/* browse
```


<a id="errors"></a>
### errors

自定義錯誤頁面可以通過 [`handle_errors`](/docs/caddyfile/directives/handle_errors) 實現。


- **v1:**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2:**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

<a id="ext"></a>
### ext

隱含的文件擴展名可以通過 [`try_files`](/docs/caddyfile/directives/try_files) 實現。

- **v1:** `ext .html`
- **v2:** `try_files {path}.html {path}`


<a id="fastcgi"></a>
### fastcgi

假設您正在提供 PHP 服務，v2 中的等效指令是 [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi)。

- **v1:**
```
fastcgi / localhost:9005 php
```
- **v2:**
```caddy-d
php_fastcgi localhost:9005
```

請注意，v1 中的 `fastcgi` 指令在幕後做了很多工作，包括嘗試磁盤上的文件、重寫請求，甚至重定向。v2 的 `php_fastcgi` 指令也會為您做這些事情，但文檔提供了它的[展開形式](/docs/caddyfile/directives/php_fastcgi#expanded-form)，如果您的需求不同，可以對其進行修改。

v2 中不需要 `php` 預設，因為 `php_fastcgi` 指令默認假定為 PHP。像 `php_fastcgi 127.0.0.1:9000 php` 這樣的行會導致反向代理認為存在一個名為 `php` 的第二個後端，從而導致連接錯誤。

子指令在 v2 中有所不同——對於 PHP，您可能不需要任何子指令。


<a id="gzip"></a>
### gzip

現在使用單個指令 [`encode`](/docs/caddyfile/directives/encode) 進行所有響應編碼，包括多種壓縮格式。

- **v1:**
```
gzip
```
- **v2:**
```caddy-d
encode gzip
```

有趣的事實：Caddy 2 還支持 `zstd`（但目前還沒有瀏覽器支持）。


<a id="header"></a>
### header

[基本沒變](/docs/caddyfile/directives/header)，但在 v2 中功能強大得多，因為它可以進行子字符串替換。

- **v1:**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2:**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```


<a id="log"></a>
### log

啟用訪問日誌；[`log`](/docs/caddyfile/directives/log) 指令在 v2 中仍然可以使用，但默認情況下所有日誌都是結構化的，並以 JSON 編碼。

建議啟用訪問日誌的方式如下：

```caddy-d
log
```

這會將結構化日誌發送到 stderr。（您也可以發送到文件或網絡套接字；請參閱 [`log`](/docs/caddyfile/directives/log) 指令文檔。）

默認情況下，日誌將採用[結構化](/docs/logging) JSON 格式。如果您出於歷史原因仍需要通用日誌格式 (CLF) 的日誌，可以使用 [`transform-encoder`](https://github.com/caddyserver/transform-encoder) 插件。


<a id="proxy"></a>
### proxy

v2 中的等效指令是 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)。

值得注意的子指令變化是 `header_upstream` 和 `header_downstream` 分別變成了 `header_up` 和 `header_down`；負載均衡相關的子指令現在以前綴 `lb_` 開頭。

另一個顯著區別是 v2 代理默認傳遞所有傳入的標頭（包括 `Host` 標頭）並設置 `X-Forwarded-For` 標頭。換句話說，v1 的 "transparent" 模式在 v2 中基本上是默認設置（但如果您需要其他標頭如 X-Real-IP，則必須自己設置）。您仍然可以使用 `header_up` 子指令覆蓋/自定義 `Host` 標頭。

Websocket 代理在 v2 中 "直接可用"；不需要像在 v1 中那樣 "啟用" websockets。

`without` 子指令已被移除，因為由於改進了 matcher 支持，v2 中不再需要 [rewrite hacks](#rewrite)。

- **v1:**
```
proxy / localhost:9005
```
- **v2:**
```caddy-d
reverse_proxy localhost:9005
```


<a id="redir"></a>
### redir

[沒變](/docs/caddyfile/directives/redir)，除了關於可選狀態碼參數的一些細節。大多數配置不需要進行任何更改。

- **v1:** `redir https://example.com{uri}`
- **v2:** `redir https://example.com{uri}`


<a id="rewrite"></a>
### rewrite

請求重寫（"內部重定向"）的語義略有變化。如果您在 v1 中使用所謂的 "rewrite hack" 作為匹配簡單路徑前綴以外的請求的一種方式，這在 v2 中完全沒有必要。

[新的 `rewrite` 指令](/docs/caddyfile/directives/rewrite)非常簡單但非常強大，因為它的大部分複雜性在 v2 中都由 [matchers](/docs/caddyfile/matchers) 處理：

- **v1:**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2:**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

請注意我們如何簡單地使用 Caddy 2 常用的 [matcher tokens](/docs/caddyfile/matchers)；對於此指令來說，這不再是一個特例。

首先移除所有 rewrite hacks；將它們轉換為 [named matchers](/docs/caddyfile/concepts#named-matchers)。評估每個 v1 `rewrite` 以查看在 v2 中是否真的需要。提示：使用 `rewrite` 添加路徑前綴然後使用帶有 `without` 的 `proxy` 移除該相同前綴的 v1 Caddyfile 就是一個 rewrite hack，可以被消除。

您可能會發現新的 [`route`](/docs/caddyfile/directives/route) 和 [`handle`](/docs/caddyfile/directives/handle) 指令對於更好地控制高級路由邏輯非常有用。


<a id="root"></a>
### root

[沒變](/docs/caddyfile/directives/root)。

請記住，如果提供靜態文件，請添加 [`file_server` 指令](/docs/caddyfile/directives/file_server)，因為 Caddy 2 默認不假定這一點，而 v1 始終啟用了它。


<a id="status"></a>
### status

v2 中的等效指令是 [`respond`](/docs/caddyfile/directives/respond)，它也可以寫入響應體。

- **v1:**
```
status 404 /secrets/
```
- **v2:**
```caddy-d
respond /secrets/* 404
```


<a id="templates"></a>
### templates

[`templates`](/docs/caddyfile/directives/templates) 指令的整體語法沒變，但實際的模板操作/函數有所不同且改進了很多。例如，模板能夠包含文件、渲染 markdown、發起內部子請求、解析 front matter 等等！

有關新功能的詳細信息，請[參閱文檔](/docs/modules/http.handlers.templates)。

- **v1:** `templates`
- **v2:** `templates`


<a id="tls"></a>
### tls

[`tls`](/docs/caddyfile/directives/tls) 指令的基本原理沒有改變，例如指定您自己的證書和密鑰：

- **v1:** `tls cert.pem key.pem`
- **v2:** `tls cert.pem key.pem`

但 Caddy 的 [auto-HTTPS logic](/docs/automatic-https) **確實** 發生了變化，所以請注意這一點！

加密套件名稱也發生了變化。

Caddy 2 中的一種常見配置是使用 `tls internal`，使其為非 `localhost` 或 IP 地址的開發主機名提供本地信任的證書。

大多數站點根本不需要此指令。


<a id="service-files"></a>
## 服務文件

對於 Caddy 部署，我們建議使用[我們官方的 systemd 服務文件之一](/docs/running#linux-service)。

如果您需要自定義服務文件，請以我們的為基礎。出於充分的理由，它們已經針對其用途進行了精心調整！如果需要，請務必自定義您的服務文件。


<a id="plugins"></a>
## 插件

為 v1 編寫的插件不自動兼容 v2。許多 v1 插件在 v2 中甚至不再需要。另一方面，v2 比 v1 更容易擴展且更靈活！

如果您想為 Caddy 2 編寫插件，請[學習如何編寫 Caddy 模塊](/docs/extending-caddy)。


<a id="building-caddy-2-with-plugins"></a>
### 使用插件構建 Caddy 2

Caddy 2 可以在[交互式下載頁面](/download)隨插件一起下載。或者，您可以使用 `xcaddy` [自己構建 Caddy](/docs/build) 並選擇要包含的插件。 `xcaddy` 自動執行 Caddy [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) 文件中的指令。


<a id="getting-help"></a>
## 尋求幫助

如果您在使 Caddy 工作時遇到困難，請首先瀏覽我們網站上的文檔。花點時間嘗試新事物並了解發生了什麼——v2 在很多方面與 v1 非常不同（但它也非常相似）！

如果您仍需要幫助，請成為[我們社區](https://caddy.community)的一員！您可能會發現，幫助他人也是幫助自己的最佳方式。
