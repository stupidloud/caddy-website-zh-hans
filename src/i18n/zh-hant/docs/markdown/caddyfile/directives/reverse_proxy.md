---
title: reverse_proxy (Caddyfile 指令)
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Fix matcher placeholder
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@name')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">@name</a>';
			break;
		}
	}
	
	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}
	
	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

<a id="reverse-proxy"></a>
# reverse_proxy

將請求轉發至一個或多個後端，並提供可配置的傳輸（transport）、負載平衡、健康檢查、請求處理及緩衝選項。

- [語法](#syntax)
- [上遊 (Upstreams)](#upstreams)
  - [上游地址](#upstream-addresses)
  - [動態上游](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
	- [Multi](#multi)
- [負載平衡](#load-balancing)
  - [主動健康檢查](#active-health-checks)
  - [被動健康檢查](#passive-health-checks)
  - [事件 (Events)](#events)
- [串流 (Streaming)](#streaming)
- [標頭 (Headers)](#headers)
- [重寫 (Rewrites)](#rewrites)
- [傳輸 (Transports)](#transports)
  - [`http` 傳輸](#the-http-transport)
  - [`fastcgi` 傳輸](#the-fastcgi-transport)
- [攔截響應](#intercepting-responses)
- [範例](#examples)


<a id="syntax"></a>
## 語法

```caddy-d
reverse_proxy [<matcher>] [<upstreams...>] {
	# 後端
	to      <upstreams...>
	dynamic <module> ...

	# 負載平衡
	lb_policy       <name> [<options...>]
	lb_retries      <retries>
	lb_try_duration <duration>
	lb_try_interval <interval>
	lb_retry_match  <request-matcher>

	# 主動健康檢查
	health_uri          <uri>
	health_upstream     <ip:port>
	health_port         <port>
	health_interval     <interval>
	health_passes       <num>
	health_fails	    <num>
	health_timeout      <duration>
	health_method       <method>
	health_status       <status>
	health_request_body <body>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<field> [<values...>]
	}

	# 被動健康檢查
	fail_duration     <duration>
	max_fails         <num>
	unhealthy_status  <status>
	unhealthy_latency <duration>
	unhealthy_request_count <num>

	# 串流
	flush_interval     <duration>
	request_buffers    <size>
	response_buffers   <size>
	stream_timeout     <duration>
	stream_close_delay <duration>

	# 請求/標頭處理
	trusted_proxies [private_ranges] <ranges...>
	header_up   [+|-]<field> [<value|regexp> [<replacement>]]
	header_down [+|-]<field> [<value|regexp> [<replacement>]]
	method <method>
	rewrite <to>

	# 輪詢傳輸
	transport <name> {
		...
	}

	# (可選) 攔截來自上游的響應
	@name {
		status <code...>
		header <field> [<value>]
	}
	replace_status [<matcher>] <status_code>
	handle_response [<matcher>] {
		<directives...>

		# 僅在 handle_response 中可用的特殊指令
		copy_response [<matcher>] [<status>] {
			status <status>
		}
		copy_response_headers [<matcher>] {
			include <fields...>
			exclude <fields...>
		}
	}
}
```


<a id="upstreams"></a>
## 上游

- **&lt;upstreams...&gt;** 是要代理到的上游（後端）列表。
- **to** <span id="to"/> 是指定上游列表的另一種方式，每行一個（或多個）。
- **dynamic** <span id="dynamic"/> 配置一個 *dynamic upstreams* 模組。這允許為每個請求動態獲取上游列表。有關標準動態上游模組的說明，請參見下文的 [動態上游](#dynamic-upstreams)。動態上游在每次代理循環迭代時獲取（即，如果啟用了負載平衡重試，每個請求可能會獲取多次），並且將優先於靜態上游。如果發生錯誤，代理將回退到使用任何靜態配置的上游。


<a id="upstream-addresses"></a>
### 上游地址

靜態上游地址可以採用僅包含協議 (scheme) 和主機/端口的 URL 形式，或傳統的 [Caddy 網路地址](/docs/conventions#network-addresses)。有效的範例：

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

預設情況下，連線是通過純文字 HTTP 與上游建立的。使用 URL 形式時，可以使用協議作為縮寫來設置一些 [`transport`](#transports) 預設值。
- 使用 `https://` 作為協議將使用啟用了 [`tls`](#tls) 的 [`http` 傳輸](#the-http-transport)。

  此外，您可能需要覆蓋 `Host` 標頭，使其與 TLS SNI 值匹配，服務器使用該值進行路由和證書選擇。有關更多詳細信息，請參見下文的 [HTTPS](#https) 部分。

- 使用 `h2c://` 作為協議將使用 [`http` 傳輸](#the-http-transport)，並將 [HTTP 版本](#versions) 設置為允許純文字 HTTP/2 連線。

- 使用 `http://` 作為協議與省略協議完全相同，因為 HTTP 已經是預設設置。包含此語法是為了與其他協議快捷方式對稱。

協議不能混用，因為它們會修改公共傳輸配置（啟用 TLS 的傳輸不能同時承載 HTTPS 和純文字 HTTP）。任何顯式的傳輸配置都不會被覆寫，省略協議或使用其他端口不會假定特定的傳輸。

當使用帶有區域（zone）的 IPv6（例如，具有特定網路接口的連結本地地址）時，**不能** 使用協議作為快捷方式，因為 `%` 會導致 URL 解析錯誤；請改為顯式配置傳輸。

當使用 [網路地址](/docs/conventions#network-addresses) 形式時，網路類型被指定為上游地址的前綴。這不能與 URL 協議結合使用。作為特殊情況，支援 `unix+h2c/` 作為 `unix/` 網路的快捷方式，並具有與 `h2c://` 協議相同的效果。支援端口範圍作為快捷方式，它會展開為具有相同主機的多個上游。

上游地址 **不能** 包含路徑或查詢字串，因為這意味著在代理的同時重寫請求，這種行為尚未定義或受支援。如果您需要此功能，可以使用 [`rewrite`](/docs/caddyfile/directives/rewrite) 指令。

如果地址不是 URL（即沒有協議），則可以使用 [placeholders](/docs/caddyfile/concepts#placeholders)，但這會使上游變成 *動態靜態* 的，這意味著在健康檢查和負載平衡方面，許多不同的後端可能充當單個靜態上游。如果可能，我們建議改用 [動態上游](#dynamic-upstreams) 模組。使用 placeholders 時，**必須** 包含端口（可以通過 placeholder 替換提供，也可以作為地址的靜態後綴）。


<a id="dynamic-upstreams"></a>
### 動態上游

Caddy 的 reverse_proxy 標配了一些動態上游模組。請注意，使用動態上游對負載平衡和健康檢查有影響，具體取決於具體的策略配置：主動健康檢查不適用於動態上游；如果上游列表相對穩定且一致（特別是使用輪詢策略），負載平衡和被動健康檢查的效果最好。理想情況下，動態上游模組僅回傳健康、可用的後端。


<a id="srv"></a>
#### SRV

從 SRV DNS 記錄獲取上游。

```caddy-d
	dynamic srv [<full_name>] {
		service   <service>
		proto     <proto>
		name      <name>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
	}
```

- **&lt;full_name&gt;** 是要查詢的記錄的完整域名（即 `_service._proto.name`）。
- **service** 是完整域名的服務部分。
- **proto** 是完整域名的協議部分。`tcp` 或 `udp`。
- **name** 是名稱部分。或者，如果 `service` 和 `proto` 為空，則是要查詢的完整域名。
- **refresh** 是刷新快取結果的頻率。預設：`1m`
- **resolvers** 是用於覆寫系統解析器的 DNS 解析器列表。
- **dial_timeout** 是撥號查詢的逾時時間。
- **dial_fallback_delay** 是在啟動 RFC 6555 快速回退連線之前等待的時間。預設：`300ms`


<a id="aaaaa"></a>
#### A/AAAA

從 A/AAAA DNS 記錄獲取上游。

```caddy-d
	dynamic a [<name> <port>] {
		name      <name>
		port      <port>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
		versions ipv4|ipv6
	}
```

- **name** 是要查詢的域名。
- **port** 是後端使用的端口。
- **refresh** 是刷新快取結果的頻率。預設：`1m`
- **resolvers** 是用於覆寫系統解析器的 DNS 解析器列表。
- **dial_timeout** 是撥號查詢的逾時時間。
- **dial_fallback_delay** 是在啟動 RFC 6555 快速回退連線之前等待的時間。預設：`300ms`
- **versions** 是要解析的 IP 版本列表。預設：`ipv4 ipv6`，分別對應 A 和 AAAA 記錄。


<a id="multi"></a>
#### Multi

追加多個動態上游模組的結果。如果您想要冗餘的上游來源，這很有用，例如：由第二組 SRV 備份的主 SRV 叢集。

```caddy-d
	dynamic multi {
		<source> [...]
	}
```

- **&lt;source&gt;** 是動態上游模組的名稱，後跟其配置。可以指定多個。


<a id="load-balancing"></a>
## 負載平衡

負載平衡通常用於在多個上游之間分配流量。通過啟用重試，它也可以用於一個或多個上游，以保留請求直到可以選擇健康的上游（例如，在重啟或重新部署上游時等待並減輕錯誤）。

這在預設情況下是啟用的，使用 `random` 策略。重試預設情況下是禁用的。

- **lb_policy** <span id="lb_policy"/> 是負載平衡策略的名稱，以及任何選項。預設：`random`。

  對於涉及哈希處理的策略，使用 [最高隨機權重 (HRW)](https://en.wikipedia.org/wiki/Rendezvous_hashing) 算法來確保具有相同哈希鍵的客戶端或請求被映射到同一個上游，即使上游列表發生變化也是如此。

  如果註明，某些策略支援將回退 (fallback) 作為選項，在這種情況下，它們接受一個帶有 `fallback <policy>` 的 [區塊](/docs/caddyfile/concepts#blocks)，該區塊接受另一個負載平衡策略。對於這些策略，預設回退是 `random`。配置回退允許在主要策略未選擇上游時使用次要策略，從而實現強大的組合。如果需要，回退可以嵌套多次。
  
  例如，`header` 可以用作主要策略以允許開發者選擇特定的上游，並將 `first` 作為所有其他連線的回退，以實現主/備故障轉移。
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` 隨機選擇一個上游

	- `random_choose <n>` 隨機選擇兩個或更多上游，然後選擇負載最小的一個（`n` 通常為 2）

	- `first` 按照配置中定義的順序選擇第一個可用的上游，允許主/備故障轉移；請記得同時啟用健康檢查，否則不會發生故障轉移

	- `round_robin` 依次輪詢每個上游

	- `weighted_round_robin <weights...>` 按順序輪詢每個上游，並遵循提供的權重。權重參數的數量應與配置的上游數量相匹配。權重應為非負整數。例如，如果有兩個上游且權重為 `5 1`，則第一個上游將連續被選中 5 次，然後第二個上游被選中一次，循環往復。如果權重使用零，將禁用為新請求選中該上游。

	- `least_conn` 選擇當前請求數最少的上游；如果多個主機的請求數最少，則隨機選擇其中一個

	- `ip_hash` 將遠端 IP（直接對等體）映射到一個固定的上游

	- `client_ip_hash` 將客戶端 IP 映射到一個固定的上游；這最好與 [`servers > trusted_proxies` 全域選項](/docs/caddyfile/options#trusted-proxies) 配合使用，後者啟用了真實客戶端 IP 解析，否則其行為與 `ip_hash` 相同

	- `uri_hash` 將請求 URI（路徑和查詢）映射到一個固定的上游

	- `query [key]` 通過對查詢值進行哈希處理，將請求查詢映射到一個固定的上游；如果指定的鍵不存在，將使用回退策略來選擇上游（預設為 `random`）

	- `header [field]` 通過對標頭值進行哈希處理，將請求標頭映射到一個固定的上游；如果指定的標頭欄位不存在，將使用回退策略來選擇上游（預設為 `random`）

	- `cookie [<name> [<secret>]]` 在來自客戶端的第一個請求（沒有 cookie 時）中，將使用回退策略選擇一個上游（預設為 `random`），並在響應中添加一個 `Set-Cookie` 標頭（如果未指定，預設 cookie 名稱為 `lb`）。Cookie 的值是所選上游的上游撥號地址，使用 HMAC-SHA256 進行哈希處理（使用 `<secret>` 作為共享密鑰，如果未指定則為空字串）。
	
	  在隨後帶有 cookie 的請求中，如果該上游可用，則 cookie 值將映射到同一個上游；如果不可用或未找到，則使用回退策略選擇一個新的上游，並將 cookie 添加到響應中。

	  如果您希望出於偵錯目的使用特定的上游，可以使用密鑰對上游地址進行哈希處理，並在您的 HTTP 客戶端（瀏覽器或其他工具）中設置 cookie。例如，使用 PHP，您可以運行以下代碼來計算 cookie 值，其中 `10.1.0.10:8080` 是您其中一個上游的地址，而 `secret` 是您配置的密鑰。
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```
	
	  您可以通過 Javascript 控制台在瀏覽器中設置 cookie，例如設置名為 `lb` 的 cookie：
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries** <span id="lb_retries"/> 是如果下一個可用主機宕機，為每個請求重試選擇可用後端的次數。預設情況下，禁用重試（零）。

  如果還配置了 [`lb_try_duration`](#lb_try_duration)，則如果達到持續時間，重試可能會提前停止。換句話說，重試持續時間優先於重試次數。

- **lb_try_duration** <span id="lb_try_duration"/> 是一個 [持續時間值](/docs/conventions#durations)，定義了如果下一個可用主機宕機，為每個請求嘗試選擇可用後端的時間。預設情況下，禁用重試（零持續時間）。

  當負載平衡器嘗試查找可用的上游主機時，客戶端將等待長達此時間。一個合理的起點可能是 `5s`，因為 HTTP 傳輸的預設撥號逾時是 `3s`，這應該允許在無法聯繫到第一個選定的上游時至少進行一次重試；但請隨意嘗試，為您的用例找到合適的平衡。

- **lb_try_interval** <span id="lb_try_interval"/> 是一個 [持續時間值](/docs/conventions#durations)，定義了從連線池中選擇下一個主機之間的等待時間。預設為 `250ms`。僅在對上游主機的請求失敗時相關。請注意，如果所有後端都宕機且延遲非常低，將此項設置為 `0` 並配合非零的 `lb_try_duration` 可能會導致 CPU 佔用過高。

- **lb_retry_match** <span id="lb_retry_match"/> 限制允許重試的請求。如果與上游的連線成功但隨後的輪詢失敗，則請求必須符合此條件才能重試。如果與上游的連線失敗，則始終允許重試。預設情況下，僅重試 `GET` 請求。

  此選項的語法與 [具名請求匹配器](/docs/caddyfile/matchers#named-matchers) 相同，但沒有 `@name`。如果您只需要單個匹配器，可以在同一行配置。對於多個匹配器，則需要一個區塊。


<a id="active-health-checks"></a>
### 主動健康檢查

主動健康檢查在後台按定時器執行。要啟用此功能，需要 `health_uri` 或 `health_port`。

- **health_uri** <span id="health_uri"/> 是主動健康檢查的 URI 路徑（以及可選的查詢）。

- **health_upstream** <span id="health_upstream"/> 是用於主動健康檢查的 ip:port（如果與上游不同）。這應與 `health_header` 和 `{http.reverse_proxy.active.target_upstream}` 配合使用。

- **health_port** <span id="health_port"/> 是用於主動健康檢查的端口（如果與上游的端口不同）。如果使用了 `health_upstream`，則忽略此項。

- **health_interval** <span id="health_interval"/> 是一個 [持續時間值](/docs/conventions#durations)，定義了執行主動健康檢查的頻率。預設：`30s`。

- **health_passes** <span id="health_passes"/> 是在將後端重新標記為健康之前所需的連續健康檢查成功次數。預設：`1`。

- **health_fails** <span id="health_fails"/> 是在將後端標記為不健康之前所需的連續健康檢查失敗次數。預設：`1`。

- **health_timeout** <span id="health_timeout"/> 是一個 [持續時間值](/docs/conventions#durations)，定義了在將後端標記為宕機之前等待回覆的時間。預設：`5s`。

- **health_method** <span id="health_method"/> 是用於主動健康檢查的 HTTP 方法。預設：`GET`。

- **health_status** <span id="health_status"/> 是健康後端預期的 HTTP 狀態碼。可以是 3 位數字的狀態碼，也可以是以 `xx` 結尾的狀態碼類別。例如：`200`（預設值）或 `2xx`。

- **health_request_body** <span id="health_request_body"/> 是一個字串，表示隨主動健康檢查發送的請求正文。

- **health_body** <span id="health_body"/> 是一個子字串或正規表達式，用於匹配主動健康檢查的響應正文。如果後端未回傳匹配的正文，它將被標記為宕機。

- **health_follow_redirects** <span id="health_follow_redirects"/> 將使健康檢查遵循上游提供的重定向。預設情況下，重定向響應會導致健康檢查被視為失敗。

- **health_headers** <span id="health_headers"/> 允許指定要在主動健康檢查請求上設置的標頭。如果您需要更改 `Host` 標頭，或者如果您需要作為健康檢查的一部分向後端提供某些身份驗證，這很有用。


<a id="passive-health-checks"></a>
### 被動健康檢查

被動健康檢查與實際的代理請求同時發生。要啟用此功能，需要 `fail_duration`。

- **fail_duration** <span id="fail_duration"/> 是一個 [持續時間值](/docs/conventions#durations)，定義了記住失敗請求的時間。持續時間 > `0` 可啟用被動健康檢查；預設為 `0`（關閉）。一個合理的起點可能是 `30s`，以便在將不健康的上游重新上線時平衡錯誤率與響應能力；但請隨意嘗試，為您的用例找到合適的平衡。

- **max_fails** <span id="max_fails"/> 是在將後端視為宕機之前，在 `fail_duration` 內所需的最高失敗請求數；必須 >= `1`；預設為 `1`。

- **unhealthy_status** <span id="unhealthy_status"/> 如果響應回傳這些狀態碼之一，則將請求計為失敗。可以是 3 位數字的狀態碼或以 `xx` 結尾的狀態碼類別，例如：`404` 或 `5xx`。

- **unhealthy_latency** <span id="unhealthy_latency"/> 是一個 [持續時間值](/docs/conventions#durations)，如果獲取響應花費了這麼長時間，則將請求計為失敗。

- **unhealthy_request_count** <span id="unhealthy_request_count"/> 是在將後端標記為宕機之前，允許同時向後端發送的請求數量。換句話說，如果某個特定後端目前正在處理這麼多請求，則認為它「超載」，將優先選擇其他後端。

  這應該是一個相當大的數字；配置此項意味著代理將具有 `unhealthy_request_count × upstreams_count` 的總同時請求限制，之後的任何請求都將由於沒有可用的上游而導致錯誤。


<a id="events"></a>
## 事件 (Events)

當上游從健康轉換為不健康或反之亦然時，會發出 [一個事件](/docs/caddyfile/options#event-options)。這些事件可用於觸發其他操作，例如發送通知或記錄訊息。事件如下：

- `healthy` 當上游之前不健康現在被標記為健康時發出
- `unhealthy` 當上游之前健康現在被標記為不健康時發出

在兩者中，`host` 都作為元數據包含在事件中，以識別更改狀態的上游。例如，它可以與 `exec` 事件處理程序配合使用，作為具備 `{event.data.host}` 的 placeholder。


<a id="streaming"></a>
## 串流 (Streaming)

預設情況下，代理會緩衝部分響應以提高傳輸效率。

代理還支援 WebSocket 連線，執行 HTTP 升級請求，然後將連線轉換為雙向隧道。

<aside class="tip">

預設情況下，當重新載入配置時，WebSocket 連線會被強制關閉（向客戶端和上游發送關閉控制訊息）。每個請求都持有對配置的引用，因此必須關閉舊連線以保持記憶體佔用。可以使用 [`stream_timeout`](#stream_timeout) 和 [`stream_close_delay`](#stream_close_delay) 選項自定義此關閉行為。

</aside>

- **flush_interval** <span id="flush_interval"/> 是一個 [持續時間值](/docs/conventions#durations)，用於調整 Caddy 將響應緩衝區刷新到客戶端的頻率。預設情況下，不進行定期刷新。負值（通常為 -1）表示「低延遲模式」，它完全禁用響應緩衝，並在每次寫入客戶端後立即刷新，並且即使客戶端提前斷開連線，也不會取消對後端的請求。如果響應中符合以下情況之一，則忽略此選項並立即將響應刷新到客戶端：
	- `Content-Type: text/event-stream`
	- `Content-Length` 未知
	- 代理兩側均為 HTTP/2，`Content-Length` 未知，且 `Accept-Encoding` 未設置或為 "identity"

- **request_buffers** <span id="request_buffers"/> 將導致代理在將請求正文發送到上游之前，將高達 `<size>` 的字節量讀入緩衝區。這非常低效，僅應在後端要求無延遲讀取請求正文時才執行此操作（這是後端應用程序應修復的問題）。這接受 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支援的所有大小格式。

- **response_buffers** <span id="response_buffers"/> 將導致代理在將響應正文回傳給客戶端之前，將高達 `<size>` 的字節量讀入緩衝區。出於效能原因，應儘可能避免這種做法，但如果後端記憶體限制較嚴，則可能會很有用。這接受 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支援的所有大小格式。

- **stream_timeout** <span id="stream_timeout"/> 是一個 [持續時間值](/docs/conventions#durations)，超時結束時，WebSocket 等串流請求將被強制關閉。這實際上是在連線保持開啟時間過長時將其取消。一個合理的起點可能是 `24h` 以清除早於一天的連線。預設：無逾時。

- **stream_close_delay** <span id="stream_close_delay"/> 是一個 [持續時間值](/docs/conventions#durations)，當卸載配置時，它會延遲 WebSocket 等串流請求被強制關閉；相反，串流將保持開啟直到延遲結束。換句話說，啟用此項可防止在重新載入 Caddy 配置時立即關閉串流。啟用此項可能是個好主意，可以避免因之前的配置關閉而導致連線關閉的客戶端大量重新連線。一個合理的起點可能是 `5m` 之類的時間，以便允許使用者在配置重新載入後 5 分鐘內自然地離開頁面。預設：無延遲。


<a id="headers"></a>
## 標頭 (Headers)

代理可以在其自身與後端之間 **操作標頭**：

- **header_up** <span id="header_up"/> 在發往後端的上游請求標頭中設置、添加（使用 `+` 前綴）、刪除（使用 `-` 前綴）或執行替換（通過使用兩個參數：搜索和替換）。

- **header_down** <span id="header_down"/> 在來自後端的下游響應標頭中設置、添加（使用 `+` 前綴）、刪除（使用 `-` 前綴）或執行替換（通過使用兩個參數：搜索和替換）。

例如，要設置請求標頭，覆寫任何現有值：

```caddy-d
header_up Some-Header "the value"
```

要添加響應標頭；請注意，一個標頭欄位可以有多個值：

```caddy-d
header_down +Some-Header "first value"
header_down +Some-Header "second value"
```

要刪除請求標頭，防止其到達後端：

```caddy-d
header_up -Some-Header
```

要使用後綴匹配刪除所有匹配的請求標頭：

```caddy-d
header_up -Some-*
```

要刪除 *所有* 請求標頭，以便能夠個別添加您想要的標頭（不推薦）：

```caddy-d
header_up -*
```

要在請求標頭上執行正規表達式替換：

```caddy-d
header_up Some-Header "^prefix-([A-Za-z0-9]*)$" "replaced-$1-suffix"
```

使用的正規表達式語言是 Go 中包含的 RE2。請參見 [RE2 語法參考](https://github.com/google/re2/wiki/Syntax) 和 [Go 正規表達式語法概述](https://pkg.go.dev/regexp/syntax)。替換字串被 [展開 (expanded)](https://pkg.go.dev/regexp#Regexp.Expand)，允許使用擷取到的值，例如 `$1` 為第一個擷取群組。


<a id="defaults"></a>
### 預設值

預設情況下，Caddy 將傳入的標頭（包括 `Host`）傳遞到後端而不進行修改，但有三個例外：

- 它設置或增強了 [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For) 標頭欄位。
- 它設置了 [`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto) 標頭欄位。
- 它設置了 [`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host) 標頭欄位。

<span id="trusted_proxies"/> 對於這些 `X-Forwarded-*` 標頭，預設情況下，代理將忽略傳入請求中的值，以防止偽造。

如果 Caddy 不是客戶端連線的第一台服務器（例如，Caddy 前面有 CDN），您可以為 `trusted_proxies` 配置一個 IP 範圍 (CIDR) 列表，從中傳入的請求被信任為這些標頭發送了正確的值。

強烈建議您通過 [`servers > trusted_proxies` 全域選項](/docs/caddyfile/options#trusted-proxies) 而不是在代理中配置此項，以便這適用於服務器中的所有代理處理程序，並且這有利於啟用客戶端 IP 解析。

<aside class="tip">

如果您在 Caddy 前面使用 Cloudflare，請注意您可能容易受到 `X-Forwarded-For` 標頭偽造的影響。我們在 [Authelia](https://www.authelia.com) 的朋友記錄了一種 [解決方法](https://www.authelia.com/integration/proxies/forwarded-headers/)，用於配置 Cloudflare 以忽略此標頭的傳入值。

</aside>

此外，當使用 [`http` 傳輸](#the-http-transport) 時，如果客戶端的請求中缺少 `Accept-Encoding: gzip` 標頭，則會設置該標頭。這允許上游在可能的情況下提供壓縮內容。可以使用傳輸上的 [`compression off`](#compression) 禁用此行為。


<a id="https"></a>
### HTTPS

由於（大多數）標頭在被代理時保留其原始值，因此在代理到 HTTPS 時，通常需要使用配置的上游地址覆寫 `Host` 標頭，以便 `Host` 標頭與 TLS ServerName 值相匹配：

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

自 Caddy v2.11.0 起，這是自動完成的，因此在代理到 HTTPS 時不再需要顯式覆寫 `Host` 標頭。如果您希望退出此行為，可以將 `Host` 標頭設置為其原始值（但這樣做很少有意義）：

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

`X-Forwarded-Host` 標頭仍會 [按預設情況](#defaults) 傳遞，因此如果上游需要知道原始 `Host` 標頭值，仍可以使用該標頭。

當在 Caddy 中終止 TLS 並通過 HTTP 代理時，無論是到端口還是 unix 套接字，同樣適用。事實上，當 Caddy 是 `reverse_proxy` 的目標時，它本身必須接收正確的 Host。在 unix 套接字的情況下，`upstream_hostport` 將是套接字路徑，並且必須顯式設置 Host。


<a id="rewrites"></a>
## 重寫 (Rewrites)

預設情況下，Caddy 使用與傳入請求相同的 HTTP 方法和 URI 執行上游請求，除非在到達 `reverse_proxy` 之前的中介軟體鏈中執行了重寫。

在代理之前，請求被複製；這確保了處理程序期間對請求所做的任何修改都不會洩漏到其他處理程序。這在處理需要在代理之後繼續的情況下很有用。

除了 [標頭操作](#headers) 之外，請求的方法和 URI 可以在發送到上游之前進行更改：

- **method** <span id="method"/> 更改克隆請求的 HTTP 方法。如果將方法更改為 `GET` 或 `HEAD`，則此處理程序將 *不會* 將傳入請求的正文發送到上游。如果您希望允許不同的處理程序使用請求正文，這很有用。
- **rewrite** <span id="rewrite"/> 更改克隆請求的 URI（路徑和查詢）。這與 [`rewrite` 指令](/docs/caddyfile/directives/rewrite) 類似，不同之處在於它不會在該處理程序的範圍之外保留重寫。

這些重寫對於「預檢查請求」之類的模式通常很有用，在這種模式下，請求被發送到另一台服務器以幫助決定如何繼續處理當前請求。

例如，請求可以發送到身份驗證閘道，以決定請求是否來自經過身份驗證的使用者（例如，請求具有會話 cookie）並應繼續，或者是否應重定向到登入頁面。對於這種模式，Caddy 提供了一個快捷指令 [`forward_auth`](/docs/caddyfile/directives/forward_auth) 以跳過大部分配置樣板。


<a id="transports"></a>
## 傳輸 (Transports)

Caddy 的代理 **傳輸 (transport)** 是可插拔的：

- **transport** <span id="transport"/> 定義了如何與後端通訊。預設為 `http`。


<a id="the-http-transport"></a>
### `http` 傳輸

```caddy-d
transport http {
	read_buffer             <size>
	write_buffer            <size>
	max_response_header     <size>
	proxy_protocol          v1|v2
	dial_timeout            <duration>
	dial_fallback_delay     <duration>
	response_header_timeout <duration>
	expect_continue_timeout <duration>
	resolvers <ip...>
	tls
	tls_client_auth <automate_name> | <cert_file> <key_file>
	tls_insecure_skip_verify
	tls_curves <curves...>
	tls_timeout <duration>
	tls_trust_pool <module>
	tls_server_name <server_name>
	tls_renegotiation <level>
	tls_except_ports <ports...>
	keepalive [off|<duration>]
	keepalive_interval <interval>
	keepalive_idle_conns <max_count>
	keepalive_idle_conns_per_host <count>
	versions <versions...>
	compression off
	max_conns_per_host <count>
	network_proxy <module>
}
```

- **read_buffer** <span id="read_buffer"/> 是讀取緩衝區的大小（以字節為單位）。它接受 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支援的所有格式。預設：`4KiB`。

- **write_buffer** <span id="write_buffer"/> 是寫入緩衝區的大小（以字節為單位）。它接受 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支援的所有格式。預設：`4KiB`。

- **max_response_header** <span id="max_response_header"/> 是從響應標頭中讀取的最大字節量。它接受 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支援的所有格式。預設：`10MiB`。

- **proxy_protocol** <span id="proxy_protocol"/> 在與上游的連線上啟用 [PROXY 協議](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt)（由 HAProxy 普及），並在前面加上真實的客戶端 IP 數據。如果 Caddy 位於另一個代理之後，這最好與 [`servers > trusted_proxies` 全域選項](/docs/caddyfile/options#trusted-proxies) 配合使用。支援版本 `v1` 和 `v2`。僅當您知道上游服務器能夠解析 PROXY 協議時才應使用此功能。預設情況下，此功能被禁用。

- **dial_timeout** <span id="dial_timeout"/> 是連線到上游套接字時等待的最大 [持續時間](/docs/conventions#durations)。預設：`3s`。

- **dial_fallback_delay** <span id="dial_fallback_delay"/> 是在啟動 RFC 6555 快速回退連線之前等待的最大 [持續時間](/docs/conventions#durations)。負值會禁用此功能。預設：`300ms`。

- **response_header_timeout** <span id="response_header_timeout"/> 是從上游讀取響應標頭時等待的最大 [持續時間](/docs/conventions#durations)。預設：無逾時。

- **expect_continue_timeout** <span id="expect_continue_timeout"/> 如果請求具有標頭 `Expect: 100-continue`，則在完整寫入請求標頭後，等待上游第一個響應標頭的最大 [持續時間](/docs/conventions#durations)。預設：無逾時。

- **read_timeout** <span id="read_timeout"/> 是等待從後端進行下一次讀取的最大 [持續時間](/docs/conventions#durations)。預設：無逾時。

- **write_timeout** <span id="write_timeout"/> 是等待向下一次寫入後端的最大 [持續時間](/docs/conventions#durations)。預設：無逾時。

- **resolvers** <span id="resolvers"/> 是用於覆寫系統解析器的 DNS 解析器列表。

- **tls** <span id="tls"/> 對後端使用 HTTPS。如果您使用 `https://` 協議指定後端，或者配置了以下任何 `tls_*` 選項，則會自動啟用此功能。

- **tls_client_auth** <span id="tls_client_auth"/> 通過以下兩種方式之一啟用 TLS 客戶端身份驗證：(1) 通過指定一個域名，Caddy 應為該域名獲取證書並保持其更新，或 (2) 通過指定證書和金鑰文件，以在與後端進行 TLS 客戶端身份驗證時出示。

- **tls_insecure_skip_verify** <span id="tls_insecure_skip_verify"/> 關閉 TLS 交握驗證，使連線變得不安全且容易受到中間人攻擊。*請勿在生產環境中使用。*

- **tls_curves** <span id="tls_curves"/> 是上游連線支援的橢圓曲線列表。Caddy 的預設設置是現代且安全的，因此只有在您有特定要求時才需要配置此項。

- **tls_timeout** <span id="tls_timeout"/> 是等待 TLS 交握完成的最大 [持續時間](/docs/conventions#durations)。預設：無逾時。

- **tls_trust_pool** <span id="tls_trust_pool"/> 配置受信任證書頒發機構的來源，類似於 `tls` 指令文件中描述的 [`trust_pool` 子指令](/docs/caddyfile/directives/tls#trust_pool)。標準 Caddy 安裝中可用的信任池來源列表 [點擊此處](/docs/caddyfile/directives/tls#trust-pool-providers)。

- **tls_server_name** <span id="tls_server_name"/> 設置在驗證 TLS 交握中接收到的證書時使用的服務器名稱。預設情況下，這將使用上游地址的主機部分。

  您僅在您的上游地址與上游可能使用的證書不匹配時才需要覆寫此項。例如，如果上游地址是 IP 地址，那麼您需要將其配置為上游服務器提供服務的主機名。

  可以使用請求 placeholder，在這種情況下，每次請求都將使用 HTTP 傳輸配置的克隆，這可能會導致效能損失。

- **tls_renegotiation** <span id="tls_renegotiation"/> 設置 TLS 重新協商級別。TLS 重新協商是在第一次交握之後執行隨後的交握。級別可以是以下之一：
  - `never`（預設值）禁用重新協商。
  - `once` 允許遠端服務器在每個連線中請求一次重新協商。
  - `freely` 允許遠端服務器重複請求重新協商。

- **tls_except_ports** <span id="tls_except_ports"/> 啟用 TLS 時，如果上游目標使用給定端口之一，則將對這些連線禁用 TLS。在配置動態上游時這可能很有用，其中一些上游預期 HTTP，而另一些預期 HTTPS 請求。

- **keepalive** <span id="keepalive"/> 是 `off` 或指定保持連線開啟時間（逾時）的 [持續時間值](/docs/conventions#durations)。預設：`2m`。

  ⚠️ 如果 keepalive 持續時間超過上游服務器的 keepalive 逾時，對 HTTP/1.1 上游的請求可能會由於「連線被對等方重置 (connection reset by peer)」錯誤而失敗。冪等請求將由 Go 的 HTTP 傳輸重試，但在其他情況下 Caddy 將以狀態碼 502 響應。

- **keepalive_interval** <span id="keepalive_interval"/> 是存活探測之間的 [持續時間](/docs/conventions#durations)。預設：`30s`。

- **keepalive_idle_conns** <span id="keepalive_idle_conns"/> 定義要保持存活的最大連線數。預設：無限制。

- **keepalive_idle_conns_per_host** <span id="keepalive_idle_conns_per_host"/> 如果非零，則控制每個主機保持的最大空閒 (keep-alive) 連線數。預設：`32`。

- **versions** <span id="versions"/> 允許自定義要支援的 HTTP 版本。
  
  有效選項包括：`1.1`、`2`、`h2c`、`3`。 

  預設值：`1.1 2`；或者，如果 [上游協議](#upstream-addresses) 為 `h2c://`，則預設值為 `h2c 2`。

  `h2c` 啟用與上游的純文字 HTTP/2 連線。這是一項非標準功能，不使用 Go 的預設 HTTP 傳輸，因此與其他功能互斥。

  `3` 啟用與上游的 HTTP/3 連線。⚠️ 這是一項實驗性功能，可能會發生變化。

- **compression** <span id="compression"/> 可用於通過設置為 `off` 來禁用對後端的壓縮。

- **max_conns_per_host** <span id="max_conns_per_host"/> 可選地限制每個主機的總連線數，包括處於撥號、活動和空閒狀態的連線。預設：無限制。

- **network_proxy** <span id="network_proxy"/> 指定發往上游服務器的請求所使用的網路代理模組名稱。如果未顯式配置，Caddy 會遵循通過環境變量配置的代理，如 [Go stdlib](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment) 所述，即 `HTTP_PROXY`、`HTTPS_PROXY` 和 `NO_PROXY`。當為此參數提供值時，請求將按以下順序流經反向代理：客戶端（使用者）→ `reverse_proxy` → `network_proxy` → 上游。內建模組包括：
	- `none`：用於忽略 `HTTP_PROXY`、`HTTPS_PROXY` 和 `NO_PROXY` 的環境設置。
	- `url <url>`：用於指定覆寫環境配置的單個 URL。


<a id="the-fastcgi-transport"></a>
### `fastcgi` 傳輸

```caddy-d
transport fastcgi {
	root  <path>
	split <at>
	env   <key> <value>
	resolve_root_symlink
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>
	capture_stderr
}
```

- **root** <span id="root"/> 是網站的根目錄。預設：`{http.vars.root}` 或當前工作目錄。

- **split** <span id="split"/> 是在哪裡拆分路徑以在 URI 末尾獲取 PATH_INFO。

- **env** <span id="env"/> 將額外的環境變量設置為給定值。可以為多個環境變量指定多次。

- **resolve_root_symlink** <span id="resolve_root_symlink"/> 通過評估符號連結（如果存在）來啟用將 `root` 目錄解析為其預定值。

- **dial_timeout** <span id="dial_timeout"/> 是連線到上游套接字時等待的時間。接受 [持續時間值](/docs/conventions#durations)。預設：`3s`。

- **read_timeout** <span id="read_timeout"/> 是從 FastCGI 服務器讀取時等待的時間。接受 [持續時間值](/docs/conventions#durations)。預設：無逾時。

- **write_timeout** <span id="write_timeout"/> 是向 FastCGI 服務器發送時等待的時間。接受 [持續時間值](/docs/conventions#durations)。預設：無逾時。

- **capture_stderr** <span id="capture_stderr"/> 啟用擷取並記錄上游 fastcgi 服務器在 `stderr` 上發送的任何訊息。預設情況下，記錄是在 `WARN` 級別完成的。如果響應具有 `4xx` 或 `5xx` 狀態，則將使用 `ERROR` 級別。預設情況下，忽略 `stderr`。

<aside class="tip">

如果您嘗試提供現代 PHP 應用程序，您可能正在尋找 [`php_fastcgi` 指令](/docs/caddyfile/directives/php_fastcgi)，它是使用 `fastcgi` 指令的代理快捷方式，具有使用 `index.php` 作為路由入口點所需的重寫。

</aside>


<a id="intercepting-responses"></a>
## 攔截響應

反向代理可以配置為攔截來自後端的響應。為了實現這一點，可以定義 [響應匹配器 (response matchers)](/docs/caddyfile/response-matchers)（語法類似於請求匹配器），並將調用第一個匹配的 `handle_response` 路由。

當調用響應處理程序時，來自後端的響應不會寫入客戶端，而是執行配置的 `handle_response` 路由，並由該路由負責寫入響應。如果該路由 *沒有* 寫入響應，則請求處理將繼續執行此 `reverse_proxy` 之後 [排序](/docs/caddyfile/directives#directive-order) 的任何處理程序。

- **@name** 是 [響應匹配器 (response matcher)](/docs/caddyfile/response-matchers) 的名稱。只要每個響應匹配器具有唯一的名稱，就可以定義多個匹配器。可以根據狀態碼以及響應標頭的存在或值來匹配響應。

- **replace_status** <span id="replace_status"/> 當被給定匹配器匹配時，僅僅更改響應的狀態碼。

- **handle_response** <span id="handle_response"/> 定義了當被給定匹配器匹配時要執行的路由（或者，如果省略匹配器，則匹配所有響應）。將應用第一個匹配的區塊。在 `handle_response` 區塊內，可以使用任何其他 [指令](/docs/caddyfile/directives)。

此外，在 `handle_response` 內部，可以使用兩個特殊的處理程序指令：

- **copy_response** <span id="copy_response"/> 將從後端接收到的響應正文複製回客戶端。可以選擇在執行此操作時更改響應的狀態碼。此指令 [排序在 `respond` 之前](/docs/caddyfile/directives#directive-order)。

- **copy_response_headers** <span id="copy_response_headers"/> 將響應標頭從後端複製到客戶端，可以選擇包含 *或* 排除標頭欄位列表（不能同時指定 `include` 和 `exclude`）。此指令 [排序在 `header` 之後](/docs/caddyfile/directives#directive-order)。

在 `handle_response` 路由中將提供三個 placeholders：

- `{rp.status_code}` 來自後端響應的狀態碼。

- `{rp.status_text}` 來自後端響應的狀態說明文字。

- `{rp.header.*}` 來自後端響應的標頭。

雖然反向代理響應處理程序可以將從代理接收到的新響應複製回客戶端，但它不能將該新響應傳遞給隨後的反向代理。`reverse_proxy` 的每次使用都會接收來自原始請求（或使用不同模組修改後的請求）的正文。


<a id="examples"></a>
## 範例

將所有請求反向代理到本地後端：

```caddy
example.com {
	reverse_proxy localhost:9005
}
```


在 [3 個後端之間](#upstreams) [負載平衡](#load-balancing) 所有請求：

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```


相同，但僅限 `/api` 內的請求，並通過使用 [`cookie` 策略](#lb_policy) 實現固定 (sticky)：

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```


使用 [主動健康檢查](#active-health-checks) 來確定哪些後端是健康的，並在連線失敗時啟用 [重試](#lb_try_duration)，保留請求直到找到健康的後端：

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```


配置一些 [傳輸選項](#transports)：

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```


反向代理到 [HTTPS 上游](#https)（自 v2.11.0 起，Caddy 將自動設置 `Host` 標頭以匹配上游的主機，因此不再需要手動設置）：

```caddy
example.com {
	reverse_proxy https://example.com
}
```


反向代理到 HTTPS 上游，但 [⚠️ 禁用 TLS 驗證](#tls_insecure_skip_verify)。不建議這樣做，因為它禁用了 HTTPS 提供的所有安全檢查；如果可能，最好在私有網路中通過 HTTP 進行代理，因為這可以避免虛假的安全感：

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```


相反，您可以通過顯式 [信任上游證書](#tls_trust_pool) 來建立與上游的信任，並且（可選）將 TLS-SNI 設置為與上游證書中的主機名相匹配：

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /path/to/cert.pem
			tls_server_name app.example.com
		}
	}
}
```



在代理之前 [去除路徑前綴](handle_path)；但請注意 [子文件夾問題 <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575)：

```caddy
example.com {
	handle_path /prefix/* {
		reverse_proxy localhost:9000
	}
}
```


在代理之前替換路徑前綴，使用 [`rewrite`](/docs/caddyfile/directives/rewrite)：

```caddy
example.com {
	handle_path /old-prefix/* {
		rewrite /new-prefix{path}
		reverse_proxy localhost:9000
	}
}
```


`X-Accel-Redirect` 支援，即根據請求提供靜態文件，通過 [攔截響應](#intercepting-responses)：

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {rp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```


上游錯誤的自定義錯誤頁面，通過狀態碼 [攔截錯誤響應](#intercepting-responses)：

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root /path/to/error/pages
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```


從 [`A`/`AAAA` 記錄](#aaaaa) DNS 查詢中 [動態](#dynamic-upstreams) 獲取後端：

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```


從 [`SRV` 記錄](#srv) DNS 查詢中 [動態](#dynamic-upstreams) 獲取後端：

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```


在創建中間服務以進行更徹底的健康檢查時，使用 [主動健康檢查](#active-health-checks) 和 `health_upstream` 可能會很有幫助。`{http.reverse_proxy.active.target_upstream}` 隨後可用作標頭，將原始上游提供給健康檢查服務。

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
