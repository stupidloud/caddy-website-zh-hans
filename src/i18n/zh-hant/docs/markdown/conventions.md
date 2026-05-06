---
title: 慣例 (Conventions)
---

<a id="conventions"></a>
# 慣例 (Conventions)

Caddy 生態系統遵循一些慣例，以確保整個平台的一致性與直觀性。


- [網路位址](#network-addresses)
- [Placeholders](#placeholders)
- [檔案位置](#file-locations)
  - [資料目錄](#data-directory)
  - [設定目錄](#configuration-directory)
- [時長 (Durations)](#durations)



<a id="network-addresses"></a>
## 網路位址 (Network addresses)

當指定要撥號 (dial) 或綁定 (bind) 的網路位址時，Caddy 接受以下格式的字串：

```
network/address
```

網路 (network) 部分是可選的（預設為 `tcp`），並且是 [Go 的 `net.Dial` 函式](https://pkg.go.dev/net#Dial) 所能辨識的任何內容。如果指定了網路，則必須使用單個正斜槓 `/` 分隔網路和位址部分。

網路可以是以下任何一種；後綴為 `4` 或 `6` 的分別僅限 IPv4 或 IPv6：

- TCP: `tcp`, `tcp4`, `tcp6`
- UDP: `udp`, `udp4`, `udp6`
- IP: `ip`, `ip4`, `ip6`
- Unix: `unix`, `unixgram`, `unixpacket`

位址 (address) 部分可以是以下任何形式：

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/path/to/unix/socket`
- `/path/to/unix/socket|0200`

主機 (host) 可以是任何主機名稱、可解析的網域名稱或 IP 位址。

對於 IPv6 位址，位址必須包含在方括號 `[]` 中。區域識別碼 (zone identifier)（以 `%` 開頭）是可選的（通常用於鏈路本地位址）。

連接埠 (port) 可以是單個值 (`:8080`) 或包含端點的範圍 (`:8080-8085`)。連接埠範圍將會被展開為多個單個位址。並非所有設定欄位都接受連接埠範圍。特殊的連接埠 `:0` 表示任何可用的連接埠。

Unix socket 路徑僅在選用 `unix*` 網路類型時才可接受。分隔網路和位址的正斜槓不被視為路徑的一部分。

當 Unix socket 用作綁定位址時，您可以選擇在路徑後指定檔案權限模式，並以管道符號 `|` 分隔。預設為 `0200`（八進位），即 `u=w,g=,o=`（符號式）。開頭的 `0` 是可選的。

有效範例：

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//path/to/socket
unix//path/to/socket|0200
```

<aside class="tip">

Caddy 網路位址不是 URL。URL 將 [OSI 模型 <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OSI_model#Layer_architecture) 的較低層與較高層耦合在一起，但 Caddy 經常獨立於特定應用程式使用網路位址，因此將它們結合起來會產生問題。在 Caddy 中，網路位址精確地指的是可以在 L3-L5 撥號或綁定的資源，但 URL 結合了 L3-L7，這涵蓋得太多了。網路位址要求 host+port 與路徑互斥，但 URL 則不然。網路位址有時支援連接埠範圍，但 URL 不支援。

</aside>




<a id="placeholders"></a>
## Placeholders

Caddy 的設定支援使用 *placeholders*。使用 placeholders 是一種將動態值注入靜態設定的簡單方法。

<aside class="tip">

Placeholders 的概念類似於其他軟體中的變數。例如，[nginx 有變數 <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html) 如 `$uri` 和 `$document_root`，而 Caddy 的對應項則是 [`{http.request.uri}`](/docs/json/apps/http/#docs) 和 [`{http.vars.root}`](/docs/caddyfile/directives/root)。

</aside>


Placeholders 由兩側的花括號 `{ }` 包圍，內部包含識別碼，例如：`{foo.bar}`。開頭的花括號可以被轉義 `\{like.this}` 以防止被替換。Placeholder 識別碼通常使用點號分隔命名空間，以避免跨模組衝突。

哪些 placeholders 可用取決於上下文。並非所有 placeholders 在設定的所有部分都可用。例如，[HTTP 應用程式設定的 placeholders](/docs/json/apps/http/#docs) 僅在設定中與處理 HTTP 請求相關的部分可用。當請求通過 [`reverse_proxy` 處理程式 (handler)](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs) 時，該處理程式會設定幾個 proxy 特定的 placeholders。這些 placeholders 可以在代理過程中以及之後（在 `handle_response` 中）被引用，例如在設定回應標頭或豐富存取日誌時。

以下 placeholders 始終可用（全域）：

Placeholder | 描述
------------|-------------
`{env.*}` | 環境變數；例如：`{env.HOME}`
`{file.*}` | 檔案內容；例如：`{file./path/to/secret.txt}`
`{system.hostname}` | 系統的本地主機名稱
`{system.slash}` | 系統的檔案路徑分隔符號
`{system.os}` | 系統的作業系統 (OS)
`{system.arch}` | 系統的架構
`{system.wd}` | 目前工作目錄
`{time.now}` | 目前時間，以 Go Time 結構表示
`{time.now.http}` | 目前時間，採用 [HTTP 標頭 <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified) 中使用的格式
`{time.now.unix}` | 目前時間，以 Unix 時間戳記（秒）表示
`{time.now.unix_ms}` | 目前時間，以 Unix 時間戳記（毫秒）表示
`{time.now.common_log}` | 目前時間，採用通用日誌格式 (Common Log Format)
`{time.now.year}` | 目前年份，採用 YYYY 格式

並非所有設定欄位都支援 placeholders，但大多數在您預期的地方都支援。對 placeholders 的支援需要明確地添加到這些欄位中。外掛作者可以 [閱讀這篇文章](/docs/extending-caddy/placeholders) 了解如何在他們自己的模組中加入對 placeholders 的支援。




<a id="file-locations"></a>
## 檔案位置 (File locations)

本節包含有關在哪裡可以找到各種檔案的資訊。這裡描述的檔案和目錄路徑充其量只是預設值；有些可以被覆蓋。

<a id="your-config-files"></a>
### 您的設定檔 (Your config files)

放置設定檔並沒有單一且慣用的位置。請將它們放在對您最有意義的地方。

<aside class="tip">

唯一的例外可能是當前工作目錄下名為 `Caddyfile` 的檔案，如果未指定其他設定檔，caddy 命令會為了方便而嘗試使用該檔案。

</aside>


隨附預設設定檔的發行版應說明該設定檔的位置，即使這對套件/發行版維護者來說可能顯而易見。對於大多數 Linux 安裝，Caddyfile 會位於 `/etc/caddy/Caddyfile`。


<a id="data-directory"></a>
### 資料目錄 (Data directory)

Caddy 將 TLS 憑證和其他重要資產儲存在資料目錄中，該目錄由 [設定的儲存模組](/docs/json/storage/)（預設：本地檔案系統）提供備份。

如果設定了 `XDG_DATA_HOME` 環境變數，則為 `$XDG_DATA_HOME/caddy`。

否則，其路徑因平台而異，並遵循作業系統慣例：

作業系統 | 資料目錄路徑
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (或 `/sdcard/caddy`)

所有其他作業系統使用 Linux/BSD 的目錄路徑。

**資料目錄絕對不能被視為快取。** 其內容 **不是** 臨時的，也不僅僅是為了效能。Caddy 在資料目錄中儲存 TLS 憑證、私鑰、OCSP staples 以及其他必要的資訊。在未了解影響的情況下，不應清除該目錄。

此目錄對於 Caddy 來說必須是持久化且可寫入的，這至關重要。


<a id="configuration-directory"></a>
### 設定目錄 (Configuration directory)

這是 Caddy 可能將某些設定儲存到磁碟的地方。最值得注意的是，它（預設情況下）會將最後一個活動設定持久化到此資料夾，以便稍後使用 [`caddy run --resume`](/docs/command-line#caddy-run) 輕鬆恢復。

<aside class="tip">

設定目錄 *不是* 您需要儲存 [您的設定檔](#your-config-files) 的地方。（雖然，您也可以這樣做。）

</aside>


如果設定了 `XDG_CONFIG_HOME` 環境變數，則為 `$XDG_CONFIG_HOME/caddy`。

否則，其路徑因平台而異，並遵循作業系統慣例：


作業系統 | 設定目錄路徑
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

所有其他作業系統使用 Linux/BSD 的目錄路徑。

此目錄對於 Caddy 來說必須是持久化且可寫入的，這至關重要。


<a id="durations"></a>
## 時長 (Durations)

時長字串在 Caddy 的設定中很常用。它們採用與 [Go 的 `time.ParseDuration` 語法](https://golang.org/pkg/time/#ParseDuration) 相同的格式，除了您還可以使用 `d` 表示天（為了簡單起見，我們假設 1 天 = 24 小時為簡單起見）。有效的單位有：

- `ns` (奈秒)
- `us`/`µs` (微秒)
- `ms` (毫秒)
- `s` (秒)
- `m` (分鐘)
- `h` (小時)
- `d` (天)

範例：

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

在 [JSON 設定](/docs/json/) 中，時長值也可以是表示奈秒的整數。
