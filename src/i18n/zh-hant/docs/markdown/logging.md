---
title: 記錄功能的工作原理
---

<a id="how-logging-works"></a>
# 記錄功能的工作原理

Caddy 擁有強大且靈活的記錄（logging）設施，但它們可能與您習慣的有所不同，特別是如果您來自更陳舊的共享主機或其他傳統 Web 伺服器。


<a id="overview"></a>
## 總覽

記錄有兩個主要方面：發射（emission）和消耗（consumption）。

**發射** 意味著產生訊息。它包含三個步驟：

1. 收集相關資訊（context）
2. 構建有用的表示形式（encoding）
3. 將該表示形式發送到輸出（writing）

此功能內建於 Caddy 的核心，使 Caddy 代碼庫或模組（plugins）的任何部分都能發射日誌（logs）。

**消耗** 是訊息的接收和處理。為了發揮作用，發射的日誌必須被消耗。僅僅被寫入但從未被讀取的日誌沒有價值。消耗日誌可以像管理員閱讀控制台輸出那樣簡單，也可以像連接日誌聚合工具或雲端服務來過濾、計數和索引日誌訊息那樣高級。

<a id="caddys-role"></a>
### Caddy 的角色

*Caddy 是一個日誌發射器*。它不消耗日誌，除了編碼和寫入日誌所需的最低限度處理。這很重要，因為它保持了 Caddy 核心的簡潔，減少了錯誤和邊緣情況，同時降低了維護負擔。最終，日誌處理超出了 Caddy 核心的範疇。

然而，始終存在消耗日誌的 Caddy app 模組的可能性。（據我們所知，它目前還不存在。）


<a id="structured-logs"></a>
## 結構化日誌

與大多數現代應用程式一樣，Caddy 的日誌是 *結構化* 的。這意味著訊息中的資訊不僅僅是一個不透明的字串或位元組切片。相反，數據保持強型別，並由單個 *欄位名稱* 引導，直到需要對訊息進行編碼並寫出為止。

比較傳統的非結構化日誌&mdash;例如傳統 HTTP 伺服器常用的陳舊 Common Log Format (CLF)：

```
127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.1" 200 2326
```

這種格式「具有結構」但不是「結構化」的：它只能用於記錄 HTTP 請求。沒有（有效的）方法可以用不同的方式對其進行編碼，因為它是一個不透明的位元組串。它也缺少很多資訊。它甚至不包含請求的 Host 標頭！這種日誌格式僅在託管單個網站以及獲取有關請求的最基本資訊時才有用。

<aside class="tip">
	CLF 中缺少主機資訊是為什麼在託管多個網站時通常需要將這些日誌寫入單獨文件的原因：否則無法從請求中得知 Host 標頭！
</aside>

現在比較一下 Caddy 的等效結構化日誌訊息，以 JSON 編碼並為顯示而進行了精美格式化：

```json
{
	"level": "info",
	"ts": 1646861401.5241024,
	"logger": "http.log.access",
	"msg": "handled request",
	"request": {
		"remote_ip": "127.0.0.1",
		"remote_port": "41342",
		"client_ip": "127.0.0.1",
		"proto": "HTTP/2.0",
		"method": "GET",
		"host": "localhost",
		"uri": "/",
		"headers": {
			"User-Agent": ["curl/7.82.0"],
			"Accept": ["*/*"],
			"Accept-Encoding": ["gzip, deflate, br"],
		},
		"tls": {
			"resumed": false,
			"version": 772,
			"cipher_suite": 4865,
			"proto": "h2",
			"server_name": "example.com"
		}
	},
	"bytes_read": 0,
	"user_id": "",
	"duration": 0.000929675,
	"size": 10900,
	"status": 200,
	"resp_headers": {
		"Server": ["Caddy"],
		"Content-Encoding": ["gzip"],
		"Content-Type": ["text/html; charset=utf-8"],
		"Vary": ["Accept-Encoding"]
	}
}
```

您可以看到結構化日誌如何更加有用並包含更多資訊。此日誌訊息中的豐富資訊不僅有用，而且幾乎沒有效能開銷：Caddy 的日誌是零分配（zero-allocation）的。結構化日誌對數據類型或 context 沒有限制：它們可以用於任何代碼路徑並包含任何類型的資訊。

因為日誌是結構化且強型別的，所以它們可以被編碼成任何格式。因此，如果您不想使用 JSON，日誌可以被編碼成任何其他表示形式。Caddy 通過 [log encoder 模組](/docs/json/logging/logs/encoder/) 支援其他格式，甚至可以添加更多格式。

**最重要的是** 在結構化日誌和傳統格式之間的區別中，以效能為代價，結構化日誌 [可以轉換為傳統的 Common Log Format <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder)，但反之則不行。從 CLF 轉向結構化格式是非常困難（或者至少是低效）的，而且考慮到資訊的缺失，這是不可能的。

本質上，高效的結構化記錄通常提倡以下理念：

- 日誌過多總比過少好
- 過濾勝於丟棄
- 延遲編碼以獲得更大的靈活性和互操作性
 

<a id="emission"></a>
## 發射

在代碼中，日誌發射類似於以下內容：

```go
logger.Debug("proxy roundtrip",
	zap.String("upstream", di.Upstream.String()),
	zap.Object("request", caddyhttp.LoggableHTTPRequest{Request: req}),
	zap.Object("headers", caddyhttp.LoggableHTTPHeader(res.Header)),
	zap.Duration("duration", duration),
	zap.Int("status", res.StatusCode),
)
```

<aside class="tip">
	這是 Caddy 反向代理中實際的一行代碼。當您啟用 debug 記錄時，這一行讓您可以檢查對配置的 upstream 的請求。這是在排查問題時非常寶貴的數據！
</aside>

您可以看到這一個函式調用包含了日誌級別、一條訊息和幾個數據欄位。所有這些都是強型別的，並且 Caddy 使用一個零分配的記錄庫，因此日誌發射快速高效，幾乎沒有開銷。

`logger` 變數是一個 `zap.Logger`，它可能具有任何數量的與之關聯的 context，其中包括名稱和數據欄位。這使得 logger 可以很好地從父級 context 中「繼承」，從而實現高級追蹤和指標（metrics）。

從那裡，訊息被發送到一個高效的處理管道，在那裡它被編碼和寫入。


<a id="logging-pipeline"></a>
## 記錄管道

如上所述，訊息是由 **loggers** 發射的。然後訊息被發送到 **logs** 進行處理。

Caddy 讓您 [配置多個 logs](/docs/json/logging/logs/)，它們可以處理訊息。一個 log 由 encoder、writer、最小級別、取樣率以及要包含或排除的 logger 列表組成。在 Caddy 中，始終有一個名為 `default` 的默認 log。您可以通過在設定中的 [此對象](/docs/json/logging/logs/) 中指定鍵名為 `"default"` 的 log 來自定義它。

<aside class="tip">

現在是 [探索 Caddy 記錄文件](/docs/json/logging/) 以熟悉我們正在討論的結構和參數的好時機。

</aside>


- **Encoder：** 日誌的格式。將記憶體中的數據表示形式轉換為位元組切片。Encoder 可以訪問日誌訊息的所有欄位。
- **Writer：** 日誌輸出。可以是任何 log writer 模組，例如寫入文件或網路套接字。它只是寫入位元組。
- **Level：** 日誌有多個級別，從 DEBUG 到 FATAL。低於指定級別的訊息將被日誌忽略。
- **Sampling：** 極端繁重的路徑可能會發射比能被有效處理的更多的日誌；啟用取樣是一種減輕負擔的方法，同時仍能產生具代表性的訊息樣本。
- **Include/exclude：** 每條訊息都由一個 logger 發射，該 logger 有一個名稱（通常源自模組 ID）。Logs 可以包含或排除來自某些 logger 的訊息。

當從 Caddy 發射日誌訊息時：

- 根據每個 log 的包含/排除列表檢查原始 logger 的名稱；如果包含（或未排除），則將其接納到該 log 中。
- 如果啟用了取樣，則會進行快速計算以確定是否保留該日誌訊息。
- 使用 log 配置的 encoder 對訊息進行編碼。
- 然後將編碼後的位元組寫入 log 配置的 writer。

默認情況下，所有訊息都發送到所有配置的 logs。這符合上述結構化記錄的價值觀。您可以通過設置它們的包含/排除列表來限制哪些訊息發送到哪些 logs，但這主要是為了過濾來自不同模組的訊息；它並不打算像日誌聚合服務那樣使用。為了保持 Caddy 記錄管道的簡潔和高效，日誌訊息的高級處理被延遲到消耗階段。

<a id="consumption"></a>
## 消耗

在訊息發送到輸出之後，消費者將讀入它們、解析它們並相應地處理它們。

這與發射日誌是一個非常不同的問題領域，Caddy 的核心不處理消耗（儘管 Caddy app 模組當然可以）。有許多工具可以用於處理 JSON 訊息流（或其他格式）以及查看、過濾、索引和查詢日誌。您甚至可以編寫或實現自己的工具。

例如，如果您運行的舊軟體需要根據特定欄位（例如主機名）將 CLF 分隔到不同的文件中，您可以使用或編寫一個簡單的工具，該工具讀入 JSON，調用 `sprintf()` 來建立 CLF 字串，然後根據 `request.host` 欄位中的值將其寫入文件。

Caddy 的記錄設施也可以用來實現指標和追蹤：指標基本上是對具有某些特徵的訊息進行計數，而追蹤則根據它們之間的共同點將多個訊息連結在一起。

通過消耗 Caddy 的日誌，您可以做的事情有無限多種可能性！
