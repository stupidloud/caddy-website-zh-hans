---
title: "命令列"
---

<a id="command-line"></a>
# 命令列

Caddy 具有標準的類 Unix 命令列介面。基本用法是：

```
caddy <command> [<args...>]
```

`<尖括號>` 表示將被您的輸入替換的參數。

`[方括號]` 表示可選參數。`(圓括號)` 表示必需參數。

省略號 `...` 表示延續，即一個或多個參數。

`--flags` 可能具有單字母快捷方式，例如 `-f`。

**快速開始：`caddy`、`caddy help` 或 `man caddy`（如果已安裝）**

---

- **[caddy adapt](#caddy-adapt)**
  將配置檔案適配為原生 JSON

- **[caddy build-info](#caddy-build-info)**
  列印構建資訊

- **[caddy completion](#caddy-completion)**
  生成 shell 補全指令碼

- **[caddy environ](#caddy-environ)**
  列印環境變數

- **[caddy file-server](#caddy-file-server)**
  一個簡單但可用於生產環境的檔案伺服器

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  檔案伺服器的輔助命令，用於匯出預設的檔案瀏覽器模板

- **[caddy fmt](#caddy-fmt)**
  格式化 Caddyfile

- **[caddy hash-password](#caddy-hash-password)**
  對密碼進行雜湊處理並輸出 base64

- **[caddy help](#caddy-help)**
  查看 Caddy 命令的說明

- **[caddy list-modules](#caddy-list-modules)**
  列出已安裝的 Caddy 模組

- **[caddy manpage](#caddy-manpage)**
  生成說明手冊頁（manpages）

- **[caddy reload](#caddy-reload)**
  更改正在運行的 Caddy 程序配置

- **[caddy respond](#caddy-respond)**
  一個快速且簡潔的硬編碼 HTTP 伺服器，用於開發和測試

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  一個簡單但可用於生產環境的 HTTP(S) reverse_proxy

- **[caddy run](#caddy-run)**
  在前臺啟動 Caddy 程序

- **[caddy start](#caddy-start)**
  在後臺啟動 Caddy 程序

- **[caddy stop](#caddy-stop)**
  停止正在運行的 Caddy 程序

- **[caddy storage export](#caddy-storage)**
  將配置的存儲內容匯出到 tar 封裝檔

- **[caddy storage import](#caddy-storage)**
  將以前匯出的 tar 封裝檔匯入到配置的存儲中

- **[caddy trust](#caddy-trust)**
  將證書安裝到本地信任存儲中

- **[caddy untrust](#caddy-untrust)**
  從本地信任存儲中移除對證書的信任

- **[caddy upgrade](#caddy-upgrade)**
  將 Caddy 升級到最新版本

- **[caddy add-package](#caddy-add-package)**
  將 Caddy 升級到最新版本，並添加額外套件

- **[caddy remove-package](#caddy-remove-package)**
  將 Caddy 升級到最新版本，並移除部分套件

- **[caddy validate](#caddy-validate)**
  測試配置檔案是否有效

- **[caddy version](#caddy-version)**
  列印版本資訊

- **[Signals](#signals)**
  Caddy 如何處理訊號

- **[Exit codes](#exit-codes)**
  Caddy 程序退出時發出的代碼

<a id="subcommands"></a>
## 子命令


<a id="caddy-adapt"></a>
### `caddy adapt`

<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

將配置適配為 Caddy 的原生 JSON 配置結構，並將輸出寫入 stdout，同時將任何警告寫入 stderr，然後退出。

`--config` 是配置檔案的路徑。如果省略，則假定當前目錄中存在 `Caddyfile`；否則，此標誌是必需的。如果您希望使用 stdin 而不是常規檔案，請使用 - 作為路徑。

`--adapter` 指定要使用的配置適配器；預設為 `caddyfile`。

`--pretty` 將使用縮排格式化輸出，以便於人類閱讀。

`--validate` 將載入並配置（provision）適配後的配置以檢查其有效性（但不會實際開始運行該配置）。

請注意，成功適配的配置可能仍會驗證失敗。有關此範例，請使用此 Caddyfile：

```caddy
localhost

tls cert_notexist.pem key_notexist.pem
```

嘗試適配它：

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

它成功完成且沒有錯誤。然後嘗試：

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_notexist.pem: no such file or directory
</code></pre>

儘管該 Caddyfile 可以無錯誤地適配為 JSON，但實際的證書和/或金鑰檔案並不存在，因此驗證失敗，因為該錯誤發生在配置（provisioning）階段。因此，驗證是比適配更強大的錯誤檢查。

#### 範例

將 Caddyfile 適配為您可以輕鬆手動閱讀和調整的 JSON：

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile --pretty</code></pre>



<a id="caddy-build-info"></a>
### `caddy build-info`

<pre><code class="cmd bash">caddy build-info</code></pre>

列印由 Go 提供的有關構建的資訊（主模組路徑、套件版本、模組替換）。




<a id="caddy-completion"></a>
### `caddy completion`

<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

生成 shell 補全指令碼。這使您在輸入 `caddy` 命令時可以獲得標籤補全或自動補全（或類似功能，取決於您的 shell）。

要獲取將此指令碼安裝到特定 shell 的說明，請執行 `caddy help completion` 或 `caddy completion -h`。



<a id="caddy-environ"></a>
### `caddy environ`

<pre><code class="cmd bash">caddy environ</code></pre>

列印 Caddy 看到的環境變數，然後退出。在除錯初始化系統或程序管理器單元（如 systemd）時很有用。




<a id="caddy-file-server"></a>
### `caddy file-server`

<pre><code class="cmd bash">caddy file-server
	[-r, --root &lt;path&gt;]
	[--listen &lt;addr&gt;]
	[-d, --domain &lt;example.com&gt;]
	[-b, --browse]
	[--reveal-symlinks]
	[-t, --templates]
	[--access-log]
	[-v, --debug]
	[-f, --file-limit &lt;number&gt;]
	[--no-compress]
	[-p, --precompressed]</code></pre>

啟動一個簡單但可用於生產環境的靜態檔案伺服器。

`--root` 指定根檔案路徑。預設為當前工作目錄。

`--listen` 接受一個監聽地址。預設為 `:80`，除非使用了 `--domain`，否則 `:443` 將是預設值。

`--domain` 將僅透過該主機名提供檔案，並且 Caddy 將嘗試透過 HTTPS 提供服務，因此如果是公共域名，請確保先正確配置任何公共 DNS。預設連接埠將更改為 443。

`--browse` 如果請求了沒有索引檔案的目錄，將啟用目錄列表。

`--reveal-symlinks` 當啟用 `--browse` 時，將在目錄列表中顯示符號連結的目標。

`--templates` 將啟用模板渲染。

`--access-log` 啟用請求/存取日誌。

`--debug` 啟用詳細日誌記錄。

`--file-limit` 設定在目錄列表中顯示的最大檔案數量。預設值：`10000`。如果檔案數量超過此限制，則僅顯示前 N 個檔案，其中 N 是指定的限制。

`--no-compress` 禁用壓縮。預設情況下，啟用了 Zstandard 和 Gzip 壓縮。

`--precompressed` 指定要搜索預壓縮旁載檔案（sidecar files）的編碼格式。可以重複使用多種格式。有關更多資訊，請參見 [file_server 指令](/docs/caddyfile/directives/file_server#precompressed)。

此命令禁用了管理 API，從而更容易在本地開發機器上運行多個實例。


<a id="caddy-file-server-export-template"></a>
#### `caddy file-server export-template`

<pre><code class="cmd bash">caddy file-server export-template</code></pre>

將預設的檔案瀏覽模板匯出到 stdout

<a id="caddy-fmt"></a>
### `caddy fmt`

<pre><code class="cmd bash">caddy fmt [&lt;path&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

格式化或美化 Caddyfile，然後退出。除非使用 `--overwrite`，否則結果將列印到 stdout，如果存在任何差異，將以代碼 `1` 退出。

`&lt;path&gt;` 指定 Caddyfile 的路徑。如果是 `-`，則從 stdin 讀取輸入。如果省略，則假定當前目錄中名為 Caddyfile 的檔案。

`--overwrite` 導致將結果寫入輸入檔案，而不是列印到終端。如果輸入不是常規檔案，則此標誌無效。

`--diff` 導致將輸出與輸入進行比較，並且在不同的行前會加上 `-` 和 `+`。請注意，未更改的行前會加上兩個空格以進行對齊，並且這不是有效的補丁（patch）格式；它僅作為視覺工具。


<a id="caddy-hash-password"></a>
### `caddy hash-password`

<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;password&gt;]
	[-a, --algorithm &lt;name&gt;]</code></pre>
	[--bcrypt-cost &lt;cost&gt;]</code></pre>

對純文字密碼進行雜湊處理的便捷方法。產生的雜湊值將寫入 stdout，其格式可直接在您的 Caddy 配置中使用。

`--plaintext`
    要雜湊的密碼。如果省略，它將從 stdin 讀取。
    如果 Caddy 連接到控制 TTY，輸入將不會回顯。

`--algorithm`
    選擇雜湊演算法。有效選項包括：
      * `argon2id`（推薦用於現代安全性）
      * `bcrypt` （舊版，較慢，可配置成本，預設成本為 `14`）

bcrypt 特定參數：

`--bcrypt-cost`
    設定 bcrypt 雜湊難度。較高的值透過使雜湊計算變慢且更耗費 CPU 來提高安全性。
    必須在有效範圍 [bcrypt.MinCost, bcrypt.MaxCost] 內。
    如果省略或無效，則使用預設成本。

Argon2id 特定參數：

`--argon2id-time`
    要執行的迭代次數。增加此值會使雜湊變慢，並增強對暴力攻擊的抵抗力。

`--argon2id-memory`
    雜湊期間使用的記憶體量。
    較大的值會增加對 GPU/ASIC 攻擊的抵抗力。

`--argon2id-threads`
    要使用的 CPU 執行緒數。增加此值可在多核系統上加快雜湊速度。

`--argon2id-keylen`
    產生的雜湊值的長度（以位元組為單位）。較長的金鑰會增加安全性，但會稍微增加存儲大小。


<a id="caddy-help"></a>
### `caddy help`

<pre><code class="cmd bash">caddy help [&lt;command&gt;]</code></pre>

列印 CLI 說明文字（可選特定子命令），然後退出。



<a id="caddy-list-modules"></a>
### `caddy list-modules`

<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

列印已安裝的 Caddy 模組，可選包含來自其關聯 Go 模組的套件和/或版本資訊，然後退出。

在某些腳本編寫情況下，列印所有標準模組可能是多餘的，因此您可以使用 `--skip-standard` 從輸出中省略這些模組。

`--json` 以 JSON 格式輸出模組資訊，這對於程式化處理很有用。

注意：由於 [Go 中的一個錯誤](https://github.com/golang/go/issues/29228)，僅當 Caddy 作為依賴項而不是主模組構建時，版本資訊才可用。使用 [xcaddy](/docs/build#xcaddy) 使其更容易。



<a id="caddy-manpage"></a>
### `caddy manpage`

<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;path&gt;)</code></pre>

為 Caddy 命令生成手冊/文件頁，並將其寫入指定路徑的目錄。此命令的輸出可以由 `man` 命令讀取。

`--directory`（必需）是寫入手冊頁的目錄路徑。如果不存在，它將被創建。

生成後，手冊頁通常需要安裝。此程序因平台而異，但在典型的 Linux 系統上，通常如下所示：

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

然後您可以執行 `man caddy`（或對子命令執行 `man caddy-*`）在您的終端機中閱讀文件。

手冊頁與我們網站上的文件是分開的文件。我們的網站有更全面且經常更新的文件。




<a id="caddy-reload"></a>
### `caddy reload`

<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

為正在運行的 Caddy 實例提供新配置。這與將文件 POST 到 [/load 端點](/docs/api#post-load) 具有相同的效果，但此命令對於圍繞配置檔案的簡單工作流程非常方便。與 `stop`、`start` 和 `run` 命令相比，此單一命令是更改/重新載入正在運行的配置的正確且語義化的方式。

因為此命令使用 API，所以管理端點不得被禁用。

`--config` 是要套用的配置檔案。如果是 `-`，則從 stdin 讀取配置。如果未指定，它將嘗試在當前工作目錄中尋找名為 `Caddyfile` 的檔案，如果存在，它將使用 `caddyfile` 配置適配器進行適配；否則，如果沒有要載入的配置檔案，則會報錯。

`--adapter` 指定要使用的配置適配器（如果有）。如果 `--config` 檔名以 `Caddyfile` 開頭或以 `.caddyfile` 結尾，則不需此標誌，因為預設會使用 `caddyfile` 適配器。否則，如果提供的配置檔案不是 Caddy 的原生 JSON 格式，則此標誌是必需的。任何警告都將列印到日誌中，但請注意，任何沒有錯誤的適配都將立即使用，即使有警告。如果您想先檢查適配結果，請使用 [`caddy adapt`](#caddy-adapt) 子命令。

`--address` 如果管理端點未在預設位址上監聽，且與提供配置檔案中的位址不同，則需要使用此標誌。

`--force` 將導致即使指定的配置與 Caddy 已經運行的配置相同也進行重新載入。這對於強制 Caddy 重新配置（reprovision）其模組非常有用，這可能會產生副作用，例如：重新載入手動載入的 TLS 證書。




<a id="caddy-respond"></a>
### `caddy respond`

<pre><code class="cmd bash">caddy respond
	[-s, --status &lt;code&gt;]
	[-H, --header "&lt;Field&gt;: &lt;value&gt;"]
	[-b, --body &lt;content&gt;]
	[-l, --listen &lt;addr&gt;]
	[-v, --debug]
	[--access-log]
	[&lt;status|body&gt;]</code></pre>


啟動一個或多個簡單的、硬編碼的 HTTP 伺服器，這對於開發、預演和某些生產案例非常有用。它對於驗證或除錯 HTTP 客戶端、指令碼甚至負載平衡器很有幫助。

`--status` 是要回傳的 HTTP 狀態碼。

`--header` 添加一個 HTTP 標頭；預期格式為 `Field: value`。此標誌可以多次使用。

`--body` 指定回應主體。或者，可以從 stdin 透過管道傳輸主體。

`--listen` 是監聽地址，可以是 Caddy 識別的任何 [網路地址](/docs/conventions#network-addresses)，並且可以包含啟動多個伺服器的連接埠範圍。

`--debug` 啟用詳細偵錯日誌記錄。

`--access-log` 啟用存取/請求日誌記錄。

在未指定任何選項的情況下，此命令在隨機可用連接埠上進行監聽，並以空的 200 回應回答 HTTP 請求。可以使用 `--listen` 標誌自定義監聽位址，該位址將始終列印到 stdout。如果監聽地址包含連接埠範圍，則將啟動多個伺服器。

如果給出了最後一個未命名的參數，則如果是 3 位數字，它將被視為狀態碼（與 `--status` 標誌相同）。否則，它將用作回應主體（與 `--body` 標誌相同）。`--status` 和 `--body` 標誌將始終覆蓋此參數。

可以透過 3 種方式給出主體：標誌、命令的最後一個（且未命名）參數，或者（如果未設定標誌和參數）透過管道傳輸到 stdin。主體支援有限的 [模板評估](https://pkg.go.dev/text/template)，包含以下變數：

變數 | 描述
---------|-------------
`.N`       | 伺服器編號
`.Port`    | 監聽連接埠
`.Address` | 監聽地址


#### 範例

隨機連接埠上的空 200 回應：
<pre><code class="cmd bash">caddy respond</code></pre>

帶有主體的 HTTP 回應：
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

多個伺服器和模板：
<pre><code class="cmd"><b>$ caddy respond --listen :2000-2004 "{{printf "I'm server {{.N}} on port {{.Port}}"}}"</b>

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

<b>$ curl 127.0.0.1:2002</b>
I'm server 2 on port 2002</code></pre>

透過管道傳入維護頁面：
<pre><code class="cmd bash">cat maintenance.html | caddy respond \
	--listen :80 \
	--status 503 \
	--header "Content-Type: text/html"</code></pre>




<a id="caddy-reverse-proxy"></a>
### `caddy reverse-proxy`

<pre><code class="cmd bash">caddy reverse-proxy
	[-f, --from &lt;addr&gt;]
	(-t, --to &lt;addr&gt;)
	[-H, --header-up "&lt;Field&gt;: &lt;value&gt;"]
	[-d, --header-down "&lt;Field&gt;: &lt;value&gt;"]
	[-c, --change-host-header]
	[-r, --disable-redirects]
	[-i, --internal-certs]
	[-v, --debug]
	[--access-log]
	[--insecure]</code></pre>

一個簡單但可用於生產環境的 reverse_proxy。適用於快速部署、演示和開發。

簡單地將 HTTP(S) 流量從 `--from` 地址傳送到 `--to` 地址。可以透過重複標誌來指定多個 `--to` 地址。至少需要一個 `--to` 地址。`--to` 地址可以有一個連接埠範圍，作為擴展到多個上游的快捷方式。

除非在位址中另有說明，否則如果給出了主機名，則 `--from` 地址將被假定為 HTTPS，而 `--to` 地址將被假定為 HTTP。

如果 `--from` 地址具有主機或 IP，Caddy 將嘗試使用證書透過 HTTPS 提供服務（除非被 HTTP 方案或連接埠覆蓋）。

如果提供 HTTPS 服務：
  - `--disable-redirects` 可用於避免綁定到 HTTP 連接埠。

  - `--internal-certs` 可用於強制使用內部 CA 發行證書，而不是嘗試發行公共證書。

對於代理：
  - `--header-up` 可用於設定要發送到上游的請求標頭。
  
  - `--header-down` 可用於設定要發送回客戶端的回應標頭。
  
  - `--change-host-header` 將請求上的 Host 標頭設定為上游的位址，而不是預設為傳入的 Host 標頭。

    這是 `--header-up "Host: {http.reverse_proxy.upstream.hostport}"` 的快捷方式。
  
  - `--insecure` 禁用與上游的 TLS 驗證。警告：這會因不驗證上游證書而導致安全性喪失。
  
  - `--debug` 啟用詳細日誌記錄。

此命令禁用了管理 API，因此更容易在本地開發機器上運行多個實例。



<a id="caddy-run"></a>
### `caddy run`

<pre><code class="cmd bash">caddy run
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--pidfile &lt;file&gt;]
	[-e, --environ]
	[--envfile &lt;file&gt;]
	[-r, --resume]
	[-w, --watch]</code></pre>

運行 Caddy 並無限期阻塞；即「守護程序（daemon）」模式。

`--config` 指定要立即載入並使用的初始配置檔案。如果是 `-`，則從 stdin 讀取配置。如果未指定配置，Caddy 將以空白配置運行，並為 [管理 API 端點](/docs/api) 使用預設設定，該端點可用於向其提供新配置。作為一種特殊情況，如果當前工作目錄有一個名為「Caddyfile」的檔案並且插入了 `caddyfile` 配置適配器（預設），則即使沒有任何命令列標誌，該檔案也會被載入並用於配置 Caddy。

`--adapter` 是載入初始配置時要使用的配置適配器的名稱（如果有）。如果 `--config` 檔名以 `Caddyfile` 開頭或以 `.caddyfile` 結尾，則不需此標誌，因為預設會使用 `caddyfile` 適配器。否則，如果提供的配置檔案不是 Caddy 的原生 JSON 格式，則此標誌是必需的。任何警告都將列印到日誌中，但請注意，任何沒有錯誤的適配都將立即使用，即使有警告。如果您想先查看適配結果，請使用 [`caddy adapt`](#caddy-adapt) 子命令。

`--pidfile` 將 PID 寫入指定的檔案。

`--environ` 在啟動前列印出環境變數。這與 `caddy environ` 命令相同，但列印後不會退出。

`--envfile` 從指定的檔案中以 `KEY=VALUE` 格式載入環境變數。支援以 `#` 開頭的註解；金鑰可能以 `export` 為字首；值可以用雙引號括起來（內部的雙引號可以轉義）；支援多行值。

`--resume` 使用上次自動儲存的載入配置，覆蓋 `--config` 標誌（如果存在）。使用此標誌可確保配置在機器重新啟動或程序重啟後具有持久性。它在以 [API](/docs/api) 為中心的部署中最為有用。

`--watch` 將監視配置檔案並在更改後自動重新載入。 ⚠️ 此功能僅適用於本地開發環境！

<aside class="advice">

在生產環境中運行時，請勿停止伺服器來更改配置！這將導致停機。（這應該是顯而易見的，但您會驚訝於我們收到了多少關於它的投訴。）請改用 [`caddy reload`](#caddy-reload) 命令，或者向程序發送 `SIGUSR1` 訊號，這與對當前載入的配置執行 `caddy reload` 具有相同的效果。

</aside>



<a id="caddy-start"></a>
### `caddy start`

<pre><code class="cmd bash">caddy start
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]
	[--pidfile &lt;file&gt;]
	[-w, --watch]</code></code></pre>

與 [`caddy run`](#caddy-run) 相同，但在後臺運行。此命令僅在後臺程序成功運行（或運行失敗）之前阻塞，然後回傳。

注意：標誌 `--config` *不* 支援 `-` 來從 stdin 讀取配置。

不鼓勵在系統服務或 Windows 上使用此命令。在 Windows 上，子程序將保持連接到終端，因此關閉窗口將強制停止 Caddy，這並不明顯。請考慮將 Caddy [作為服務](/docs/running) 運行。

啟動後，您可以使用 [`caddy stop`](#caddy-stop) 或 [`POST /stop`](/docs/api#post-stop) API 端點來退出後臺程序。



<a id="caddy-stop"></a>
### `caddy stop`

<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

<aside class="tip">

停止（和重新啟動）伺服器與配置更改是無關的。 **除非您想要停機，否則請勿使用 stop 命令在生產環境中更改配置。** 請改用 [`caddy reload`](#caddy-reload) 命令。

</aside>


優雅地停止正在運行的 Caddy 程序（停止命令本身的程序除外）並使其退出。它使用管理 API 的 [`POST /stop`](/docs/api#post-stop) 端點來執行優雅停機。

如果正在運行的實例的管理 API 未使用預設監聽位址，則可以使用 `--address` 標誌或從給定的 `--config` 自定義此請求的位址。

如果您想停止當前配置但不退出程序，請使用帶有空白配置的 [`caddy reload`](#caddy-reload)，或 [`DELETE /config/`](/docs/api#delete-configpath) 端點。


<a id="caddy-storage"></a>
### `caddy storage`

*⚠️ 實驗性功能*

允許匯出和匯入 Caddy 配置的數據存儲內容。

這在需要從一個 [存儲模組](/docs/json/storage/) 轉換到另一個存儲模組時非常有用，方法是從舊模組匯出，更新配置，然後匯入到新模組。

以下命令可用於一鍵在不同模組之間複製存儲，使用舊配置和新配置，將匯出命令的輸出透過管道傳輸到匯入命令中。

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">

請注意，當使用 [檔案系統存儲](/docs/conventions#data-directory) 時，您必須以與 Caddy 平常運行時相同的用戶身份執行匯出命令，否則可能會使用錯誤的存儲位置。

例如，當以 [systemd 服務](/docs/running#linux-service) 運行 Caddy 時，它將以 `caddy` 用戶身份運行，因此您應該以該用戶身份執行匯出或匯入命令。這通常可以透過 `sudo -u caddy <command>` 來完成。

</aside>


<a id="caddy-storage-export"></a>
#### `caddy storage export`

<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;path&gt;
	[-o, --output &lt;path&gt;]</code></pre>

`--config` 是要載入的配置檔案。這是必需的，以便連接到正確的存儲模組。

`--output` 是寫入 tar 封裝檔的檔名。如果是 `-`，則將輸出寫入 stdout。



<a id="caddy-storage-import"></a>
#### `caddy storage import`

<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;path&gt;
	-i, --input &lt;path&gt;</code></pre>

`--config` 是要載入的配置檔案。這是必需的，以便連接到正確的存儲模組。

`--input` 是要讀取的 tar 封裝檔的檔名。如果是 `-`，則從 stdin 讀取輸入。


<a id="caddy-trust"></a>
### `caddy trust`

<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

將 Caddy 的 [PKI app](/docs/json/apps/pki/) 管理的 CA 的根證書安裝到本地信任存儲中。

Caddy 會在首次生成根證書時嘗試自動將其安裝到本地信任存儲中，但如果 Caddy 沒有適當的權限寫入信任存儲，則可能會失敗。如果伺服器程序以非特權用戶（例如透過 systemd）運行，則在安裝證書之前必須執行此命令。您可能需要在 Unix 系統上使用 `sudo` 執行此命令。

預設情況下，此命令安裝 Caddy 預設 CA（即「local」）的根證書。您可以使用 `--ca` 標誌指定另一個 CA 的 ID。

此命令將嘗試連接到 Caddy 的 [管理 API](/docs/api) 以獲取根證書，使用 [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates) 端點。如果正在運行的實例的管理 API 未使用預設監聽地址，您可以明確指定 `--address`，或使用 `--config` 標誌從配置中載入管理位址。

如果管理 API 可供其他機器存取，您還可以使用帶有此命令的 `caddy` 二進位檔案在網路中的其他機器上安裝證書——執行此操作時請小心，不要將管理 API 暴露給不受信任的客戶端。


<a id="caddy-untrust"></a>
### `caddy untrust`

<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;path&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

從本地信任存儲中取消對根證書的信任。

此命令解除信任；它不一定會從信任存儲中完全刪除根證書。因此，重複信任和取消對新證書的信任可能會填滿信任資料庫。

此命令不會從 Caddy 配置的存儲中刪除或修改證書檔案。

此命令可以透過以下兩種方式之一使用：
- 透過使用 `--cert` 標誌指定要取消信任的根證書的直接路徑。
- 透過使用 [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates) 端點從 [管理 API](/docs/api) 獲取根證書。如果沒有給出標誌，這是預設行為。

如果使用管理 API，則 CA ID 預設為「local」。您可以使用 `--ca` 標誌指定另一個 CA 的 ID。如果正在運行的實例的管理 API 未使用預設監聽地址，您可以明確指定 `--address`，或使用 `--config` 標誌從配置中載入管理地址。


<a id="caddy-upgrade"></a>
### `caddy upgrade`

*⚠️ 實驗性功能*

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

將當前的 Caddy 二進位檔案替換為 [我們的下載頁面](/download) 中的最新版本，並安裝相同的模組，包括在 Caddy 網站上註冊的所有第三方外掛。

升級不會中斷正在運行的伺服器；目前，該命令僅替換磁碟上的二進位檔案。如果我們能找到一個好的方法，這在未來可能會改變。

升級過程具有容錯性；當前的二進位檔案首先被備份（複製到當前檔案旁邊），如果出現任何問題，會自動恢復。如果您希望在升級過程完成後保留備份，可以使用 `--keep-backup` 選項。

如果您的用戶沒有寫入可執行檔案的權限，此命令可能需要較高的權限。



<a id="caddy-add-package"></a>
### `caddy add-package`

*⚠️ 實驗性功能*

<pre><code class="cmd bash">caddy add-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

與 `caddy upgrade` 類似，將當前的 Caddy 二進位檔案替換為安裝了相同模組的最新版本，*並* 包含作為參數列出的套件。從 [我們的下載頁面](/download) 中找到您可以安裝的套件列表。每個參數應該是完整的套件名稱。

例如：

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>



<a id="caddy-remove-package"></a>
### `caddy remove-package`

*⚠️ 實驗性功能*

<pre><code class="cmd bash">caddy remove-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

與 `caddy upgrade` 類似，將當前的 Caddy 二進位檔案替換為安裝了相同模組的最新版本，但 *不* 包含作為參數列出的套件（如果當前二進位檔案中存在這些套件）。執行 `caddy list-modules --packages` 以查看當前二進位檔案中包含的非標準模組的套件名稱列表。



<a id="caddy-validate"></a>
### `caddy validate`

<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]</code></pre>

驗證配置檔案，然後退出。此命令將配置反序列化，然後載入並配置（provision）其所有模組，就像啟動配置一樣，但配置實際上並未啟動。這暴露了在載入或配置階段產生的配置錯誤，並且是比僅將配置序列化為 JSON 更強大的錯誤檢查。

`--config` 是要驗證的配置檔案。如果是 `-`，則從 stdin 讀取配置。預設是當前目錄中的 `Caddyfile`（如果有）。

`--adapter` 是要使用的配置適配器的名稱。如果 `--config` 檔名以 `Caddyfile` 開頭或以 `.caddyfile` 結尾，則不需此標誌，因為預設會使用 `caddyfile` 適配器。否則，如果提供的配置檔案不是 Caddy 的原生 JSON 格式，則此標誌是必需的。

`--envfile` 從指定的檔案中以 `KEY=VALUE` 格式載入環境變數。支援以 `#` 開頭的註解；金鑰可能以 `export` 為字首；值可以用雙引號括起來（內部的雙引號可以轉義）；支援多行值。



<a id="caddy-version"></a>
### `caddy version`
<pre><code class="cmd bash">caddy version</code></pre>

列印版本並退出。



<a id="signals"></a>
## 訊號

Caddy 會捕捉某些訊號並忽略其他訊號。訊號可以啟動特定的程序行為。

訊號 | 行為
-------|----------
`SIGINT` | 優雅退出。再次發送訊號以立即強制退出。
`SIGQUIT` | 立即退出 Caddy，但仍會清理存儲中的鎖（lock），因為這很重要。
`SIGTERM` | 優雅退出。
`SIGUSR1` | 重新載入配置檔案，但僅當使用 `caddy run`（不帶 `--resume`）啟動且未透過 [API](/docs/api)（包括 [`caddy reload`]#caddy-reload）對配置進行任何更改時才有效。
`SIGUSR2` | 忽略。
`SIGHUP` | 忽略。

優雅退出意味著不再接受新連接，現有連接將在通訊端（socket）關閉之前排空。可能會套用寬限期（且是可配置的）。寬限期過後，連接將被強制終止。存儲中的鎖（lock）以及各個模組需要釋放的其他資源會在優雅停機期間被清理。

當收到重新載入配置的訊號（`SIGUSR1`）時，它的行為就像強制配置重新載入（即即使配置文字未更改也重新載入），這可能會從磁碟重新載入 TLS 證書等依賴檔案。

僅當 Caddy 使用配置檔案以 `caddy run` 啟動時，才啟用基於訊號的配置重新載入。如果 Caddy 以 `--resume` 啟動（因為它暗示了 API 工作流程），或者如果透過管理 API 接收到任何配置更改，或者如果以與最初啟動時 *不同* 的檔名或配置適配器執行 `caddy reload`，則它們將被禁用（忽略訊號，並帶有日誌警告）。這是為了避免重新載入方法之間的衝突。



<a id="exit-codes"></a>
## 退出碼

Caddy 在程序退出時回傳一個代碼：

代碼 | 含義
-----|---------
`0` | 正常退出。
`1` | 啟動失敗。 **請勿自動重啟程序；除非進行更改，否則它可能會再次出錯。**
`2` | 強制退出。Caddy 被強制退出而未清理資源。
`3` | 退出失敗。Caddy 在清理期間帶有一些錯誤退出。

在 bash 中，您可以使用 `echo $?` 獲取上一個命令的退出碼。
