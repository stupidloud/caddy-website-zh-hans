---
title: "API"
---

<a id="api"></a>
# API

Caddy 透過管理端點進行設定，該端點可以使用 HTTP 透過 [REST <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Representational_state_transfer) API 存取。您可以在 Caddy 設定中 [設定此端點](/docs/json/admin/)。

**預設位址：`localhost:2019`**

預設位址可以透過設定 `CADDY_ADMIN` 環境變數來更改。某些安裝方法可能會將此設定為不同的值。Caddy 設定中的位址始終優先於預設值。

<aside class="tip">
	如果您在伺服器上執行不受信任的程式碼（哎呀 😬），請確保透過隔離程序、修補有漏洞的程式以及將端點設定為綁定到有權限的 unix socket 來保護您的管理端點。
</aside>

任何更改後，最新的設定都將儲存到磁碟中（除非 [已停用](/docs/json/admin/config/)）。您可以在重啟後使用 [`caddy run --resume`](/docs/command-line#caddy-run) 恢復上次工作的設定，這保證了在電源循環或類似情況下的設定持久性。

要開始使用 API，請嘗試我們的 [API 教程](/docs/api-tutorial) 或者，如果您只有一分鐘時間，請閱讀我們的 [API 快速入門指南](/docs/quick-starts/api)。

---

- **[POST /load](#post-load)**
  設定或替換活動設定

- **[POST /stop](#post-stop)**
  停止活動設定並退出程序

- **[GET /config/[path]](#get-configpath)**
  匯出指定路徑的設定

- **[POST /config/[path]](#post-configpath)**
  設定或替換對象；追加到陣列
  
- **[PUT /config/[path]](#put-configpath)**
  建立新對象；插入到陣列

- **[PATCH /config/[path]](#patch-configpath)**
  替換現有的對象或陣列元素

- **[DELETE /config/[path]](#delete-configpath)**
  刪除指定路徑的值

- **[在 JSON 中使用 @id](#using-id-in-json)**
  輕鬆遍歷到設定結構中

- **[並行設定更改](#concurrent-config-changes)**
  避免在對設定進行不同步的更改時發生衝突

- **[POST /adapt](#post-adapt)**
  將設定轉換為 JSON 而不執行它

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  返回有關特定 [PKI app](/docs/json/apps/pki/) CA 的資訊

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  返回特定 [PKI app](/docs/json/apps/pki/) CA 的證書鏈

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  返回已設定的 proxy upstreams 的當前狀態


## POST /load

設定 Caddy 的設定，覆蓋任何先前的設定。它會阻塞直到重新載入完成或失敗。設定更改是輕量、高效且零停機的。如果新設定由於任何原因失敗，舊設定將回滾到位而不會停機。

此端點支援使用設定轉接器 (config adapters) 的不同設定格式。請求的 Content-Type 標頭指示請求正文中使用的設定格式。通常，這應該是 `application/json`，它代表 Caddy 的原生設定格式。對於另一種設定格式，請指定適當的 Content-Type，以便正斜槓 / 之後的值是要使用的設定轉接器的名稱。例如，在提交 Caddyfile 時，使用類似 `text/caddyfile` 的值；或者對於 JSON 5，使用諸如 `application/json5` 的值；等等。

如果新設定與當前設定相同，則不會發生重新載入。要強制重新載入，請在請求標頭中設定 `Cache-Control: must-revalidate`。

<a id="examples"></a>
### 範例

設定新的活動設定：

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

注意：curl 的 `-d` 標記會移除換行符，因此如果您的設定格式對換行符敏感（例如 Caddyfile），請改用 `--data-binary`：

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## POST /stop

優雅地關閉伺服器並退出程序。要僅停止正在執行的設定而不退出程序，請使用 [DELETE /config/](#delete-configpath)。

<a id="examples"></a>
### 範例

停止程序：

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


## GET /config/[path]

匯出指定路徑處的 Caddy 當前設定。返回一個 JSON 正文。

<a id="examples"></a>
### 範例

匯出整個設定並美化輸出：

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					]
				}
			}
		}
	}
}</code></pre>

僅匯出監聽器位址：

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[":443"]</code></pre>



## POST /config/[path]

將指定路徑處的 Caddy 設定更改為請求的 JSON 正文。如果目標值是陣列，POST 會追加；如果是對象，它會建立或替換。

作為一種特殊情況，如果滿足以下條件，可以將多個項目添加到陣列中：

1. 路徑以 `/...` 結尾
2. `/...` 之前的路徑元素指向一個陣列
3. 負載是一個陣列

在這種情況下，負載陣列中的元素將被展開，並且每個元素都將被追加到目標陣列。用 Go 的話來說，這與以下程式碼具有相同的效果：

```go
baseSlice = append(baseSlice, newElems...)
```

<a id="examples"></a>
### 範例

添加一個監聽器位址：

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

添加多個監聽器位址：

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

## PUT /config/[path]

將指定路徑處的 Caddy 設定更改為請求的 JSON 正文。如果目標值是陣列中的位置（索引），PUT 會插入；如果是對象，它會嚴格地建立一個新值。

<a id="examples"></a>
### 範例

在第一個槽位添加一個監聽器位址：

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


## PATCH /config/[path]

將指定路徑處的 Caddy 設定更改為請求的 JSON 正文。PATCH 嚴格地替換現有值或陣列元素。

<a id="examples"></a>
### 範例

替換監聽器位址：

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>



## DELETE /config/[path]

移除指定路徑處的 Caddy 設定。DELETE 刪除目標值。

<a id="examples"></a>
### 範例

卸載整個當前設定但保持程序執行：

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

僅停止您的一個 HTTP 伺服器：

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


<a id="using-id-in-json"></a>
## 在 JSON 中使用 @id

您可以在 JSON 文件中嵌入 ID，以便更輕鬆地直接存取 JSON 的那些部分。

只需在對象中添加一個名為 `"@id"` 的欄位並給它一個唯一的名稱。例如，如果您有一個想要頻繁存取的 reverse proxy handler：

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

要使用它，只需向 `/id/` API 端點發出請求，方式與向相應的 `/config/` 端點發出請求相同，但不需要完整路徑。ID 會直接將請求帶入該設定範圍。

例如，要在沒有 ID 的情況下存取 reverse proxy 的 upstreams，路徑將類似於

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

但有了 ID，路徑變為

```
/id/my_proxy/upstreams
```

這更容易記住和手動編寫。

<a id="concurrent-config-changes"></a>
## 並行設定更改

<aside class="tip">

本節適用於所有 `/config/` 端點。它是實驗性的，可能會發生變化。

</aside>


Caddy 的設定 API 為單個請求提供 [ACID 保證 <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/ACID)，但如果不進行適當的同步，涉及多個請求的更改可能會發生衝突或資料丟失。

例如，兩個用戶端可能同時 `GET /config/foo`，在該範圍（設定路徑）內進行編輯，然後同時呼叫 `POST|PUT|PATCH|DELETE /config/foo/...` 來應用他們的更改，從而導致衝突：要麼一個會覆蓋另一個，要麼第二個可能會使設定處於非預期狀態，因為它是應用於與其準備時不同的設定版本。這是因為更改彼此不知情。

Caddy 的 API 不支援跨越多個請求的事務，並且 HTTP 是一種無狀態協議。但是，您可以使用 `Etag` 和 `If-Match` 標頭來檢測並防止任何和所有更改的衝突，作為一種樂觀並行控制。如果您有可能在不同步的情況下同時使用 Caddy 的 `/config/...` 端點，這很有用。所有對 `GET /config/...` 請求的響應都有一個名為 `Etag` 的 HTTP 標頭，其中包含路徑和該範圍內內容的哈希值（例如 `Etag: "/config/apps/http/servers 65760b8e"`）。只需在變更請求上將 `If-Match` 標頭設定為來自先前 `GET` 請求的 Etag 標頭的值。

此操作的基本算法如下：

1. 對設定內的任何範圍 `S` 執行 `GET` 請求。保留響應的 `Etag` 標頭。
2. 在返回的設定上進行您想要的更改。
3. 在範圍 `S` 內執行 `POST|PUT|PATCH|DELETE` 請求，將 `If-Match` 請求標頭設定為儲存的 `Etag` 值。
4. 如果響應是 HTTP 412 (Precondition Failed)，則從步驟 1 重試，或在嘗試次數過多後放棄。

此算法安全地允許對 Caddy 的設定進行多個重疊的更改，而無需顯式同步。它的設計使得對設定不同部分的同時更改不需要重試：只有重疊在設定相同範圍的更改才可能導致衝突，從而需要重試。


## POST /adapt

將設定轉換為 Caddy JSON 而不載入或執行它。如果成功，生成的 JSON 文件將在響應正文中返回。

Content-Type 標頭用於以與 [/load](#post-load) 相同的方式指定設定格式。例如，要轉換 Caddyfile，請設定 `Content-Type: text/caddyfile`。

只要您的 Caddy 版本中插入了關聯的 [設定轉接器 (config adapter)](/docs/config-adapters)，此端點將轉換任何設定格式。

<a id="examples"></a>
### 範例

將 Caddyfile 轉換為 JSON：

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## GET /pki/ca/&lt;id&gt;

透過 ID 返回有關特定 [PKI app](/docs/json/apps/pki/) CA 的資訊。如果請求的 CA ID 是預設值 (`local`)，則如果尚未配置該 CA，則將配置該 CA。如果先前未配置其他 CA ID，則將返回錯誤。

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


## GET /pki/ca/&lt;id&gt;/certificates

透過 ID 返回特定 [PKI app](/docs/json/apps/pki/) CA 的證書鏈。如果請求的 CA ID 是預設值 (`local`)，則如果尚未配置該 CA，則將配置該 CA。如果先前未配置其他 CA ID，則將返回錯誤。

此端點由 [`caddy trust`](/docs/command-line#caddy-trust) 命令在內部使用，以允許將 CA 的根證書安裝到系統的信任存儲中。

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


<a id="get-reverse-proxyupstreams"></a>
## GET /reverse_proxy/upstreams

以 JSON 文件形式返回已設定的 reverse proxy upstreams（後端）的當前狀態。

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

JSON 陣列中的每個條目都是儲存在全域 upstream 池中已設定的 [upstream](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/)。

- **address** 是 upstream 的撥號位址。
- **num_requests** 是 upstream 當前正在處理的活動請求數量。
- **fails** 是根據被動健康檢查設定，目前記住的失敗請求數量。

如果您的目標是確定後端的可用性，您需要根據您正在使用的 handler 設定交叉檢查 upstream 的相關屬性。例如，如果您為您的 proxy 啟用了 [被動健康檢查](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/)，那麼您還需要考慮 `fails` 和 `num_requests` 的值來確定一個 upstream 是否被認為是可用的：檢查 `fails` 數量是否小於您為 proxy 設定的最大失敗次數（即 [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/)），以及 `num_requests` 是否小於或等於您設定的每個 upstream 最大請求數量（即對於整個 proxy 的 [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/)，或對於單個 upstream 的 [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/)）。
