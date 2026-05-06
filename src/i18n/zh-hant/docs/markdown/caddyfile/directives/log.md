---
title: log (Caddyfile 指令)
---

<script>
ready(function() {
	// 修復代碼塊中的 >
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// 如果以 > 結尾則跳過
			if (item.textContent.trim().endsWith('>')) return;
			// 將 > 替換為 <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// 如果在頁面上找到匹配的錨點標籤，我們將添加指向所有子指令的連結。
	addLinksToSubdirectives();
});
</script>

<a id="log"></a>
# log

啟用並配置 HTTP 請求日誌（也稱為存取日誌）。

<aside class="tip">

要配置 Caddy 的運行時日誌，請參閱 [`log` 全域選項](/docs/caddyfile/options#log)。

</aside>


除非使用 `hostnames` 子指令覆蓋，否則 `log` 指令適用於其出現的站點塊的主機名。

配置後，預設情況下站點的所有請求都將被記錄。要根據條件跳過某些請求的記錄，請使用 [`log_skip` 指令](log_skip)。

要向日誌條目添加自定義欄位，請使用 [`log_append` 指令](log_append)。


- [語法](#syntax)
- [輸出模組](#output-modules)
  - [stderr](#stderr)
  - [stdout](#stdout)
  - [discard](#discard)
  - [file](#file)
  - [net](#net)
- [格式模組](#format-modules)
  - [console](#console)
  - [json](#json)
  - [filter](#filter)
    - [delete](#delete)
	- [rename](#rename)
	- [replace](#replace)
	- [ip_mask](#ip-mask)
	- [query](#query)
	- [cookie](#cookie)
	- [regexp](#regexp)
	- [hash](#hash)
  - [append](#append)
- [範例](#examples)

預設情況下，包含潛在敏感資訊的標頭（`Cookie`、`Set-Cookie`、`Authorization` 和 `Proxy-Authorization`）在存取日誌中將被記錄為 `REDACTED`。可以使用 [`log_credentials`](/docs/caddyfile/options#log-credentials) 全域伺服器選項禁用此行為。


<a id="syntax"></a>
## 語法

```caddy-d
log [<logger_name>] {
	hostnames <hostnames...>
	no_hostname
	output <writer_module> ...
	format <encoder_module> ...
	level  <level>
	sampling {
		interval   <duration>
		first      <number>
		thereafter <number>
	}
}
```

- **logger_name** <span id="logger_name"/> 是此站點日誌記錄器名稱的可選覆蓋。

  預設情況下，會自動產生一個日誌記錄器名稱，例如 `log0`、`log1` 等，具體取決於 Caddyfile 中站點的順序。這僅在您希望從全域選項中定義的另一個日誌記錄器可靠地引用此日誌記錄器的輸出時才有用。請參閱下面的 [範例](#multiple-outputs)。

- **hostnames** <span id="hostnames"/> 是此日誌記錄器適用的主機名的可選覆蓋。

  預設情況下，日誌記錄器適用於其出現的站點塊的主機名，即站點位址。如果您希望在 [萬用字元站點塊](/docs/caddyfile/patterns#wildcard-certificates) 中為每個子網域定義不同的日誌記錄器，這很有用。請參閱下面的 [範例](#wildcard-logs)。

- **no_hostname** <span id="no_hostname"/> 防止日誌記錄器與站點塊的任何主機名關聯。預設情況下，日誌記錄器與 `log` 指令出現的 [站點位址](/docs/caddyfile/concepts#addresses) 相關聯。

  當您想要使用 [`log_name` 指令](/docs/caddyfile/directives/log_name) 根據某些條件（例如請求路徑或方法）將請求記錄到不同的檔案時，這很有用。

- **output** <span id="output"/> 配置日誌的寫入位置。請參閱下面的 [`output` 模組](#output-modules)。

  預設值：`stderr`。

- **format** <span id="format"/> 描述如何編碼或格式化日誌。請參閱下面的 [`format` 模組](#format-modules)。

  預設值：如果檢測到 `stderr` 是終端，則為 `console`，否則為 `json`。

- **level** <span id="level"/> 是要記錄的最小條目級別。預設值：`INFO`。

  請注意，存取日誌目前僅發出 `INFO` 和 `ERROR` 級別的日誌。

- **sampling** <span id="sampling"/> 配置日誌採樣以減少日誌量。如果指定了採樣，則會啟用採樣，並採用以下預設值。省略此項將禁用採樣。

  - **interval** 是進行採樣的 [持續時間窗口](/docs/conventions#durations)。預設值：`1s`（禁用）。

  - **first** 是在每個間隔內為給定級別和訊息保留多少日誌。預設值：`100`。

  - **thereafter** 是在保留第一批日誌後，每個間隔中要跳過多少日誌。預設值：`100`。

  例如，使用 `interval 1s`、`first 5` 和 `thereafter 10`，在每 10 秒的間隔內，將保留前 5 個日誌條目，然後在該秒內允許每隔 10 個具有相同級別和訊息的日誌條目通過。


<a id="output-modules"></a>
### 輸出模組

**output** 子指令讓您自定義日誌寫入的位置。

<a id="stderr"></a>
#### stderr

標準錯誤（主控台，這是預設值）。

```caddy-d
output stderr
```

<a id="stdout"></a>
#### stdout

標準輸出（主控台）。

```caddy-d
output stdout
```

<a id="discard"></a>
#### discard

不輸出。

```caddy-d
output discard
```

<a id="file"></a>
#### file

檔案。預設情況下，日誌檔案會根據大小進行輪轉（"rolled"），以防止磁碟空間耗盡。

日誌輪轉由 [timberjack <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/DeRuina/timberjack) 提供。

<aside class="tip">

**關於重新載入日誌檔案選項的說明：** 需要重新啟動伺服器才能將配置更改應用於給定的輸出檔案。更改不會在伺服器重新載入時應用，除非您添加新的日誌檔案名。

</aside>

```caddy-d
output file <filename> {
	mode          <mode>
	roll_disabled
	roll_size     <size>
	roll_interval <duration>
	roll_minutes  <minutes...>
	roll_at	      <times...>
	roll_uncompressed
	roll_local_time
	roll_keep     <num>
	roll_keep_for <days>
	backup_time_format <format>
}
```

- **&lt;filename&gt;** 是日誌檔案的路徑。

  輪轉時，檔案會使用模板 `<name>-<timestamp>-<reason>.log` 重新命名。時間戳根據 [`backup_time_format`](#backup_time_format) 選項進行格式化。原因是 `size` 或 `time`，具體取決於觸發輪轉的原因。如果檔案被壓縮，`.gz` 會附加到檔案名後。

   例如，如果檔案名是 `access.log`，由於大小輪轉的檔案可能命名為 `access-2026-01-30T22-15-42.123-size.log`，由於時間輪轉的檔案可能命名為 `access-2025-01-30T00-00-00.000-time.log`。

- **mode** <span id="mode"/> 是用於日誌檔案的 Unix 檔案模式/權限。該模式由 1 到 4 個八進制數字組成（與 Unix [chmod <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Chmod) 命令接受的數字格式相同，除了全零模式被解釋為預設模式 `600`）。

  例如：`0600` 將模式設置為 `rw-,---,---`（日誌檔案所有者具有讀/寫權限，其他人無權限）；`0640` 將模式設置為 `rw-,r--,---`（檔案所有者具有讀/寫權限，群組僅具有讀取權限）；`644` 將模式設置為 `rw-,r--,r--`，日誌檔案所有者具有讀/寫權限，但群組所有者和其他使用者僅具有讀取權限。

- **roll_disabled** <span id="roll_disabled"/> 禁用日誌輪轉。這可能導致磁碟空間耗盡，因此僅在以其他方式維護日誌檔案時才使用此項。

- **roll_size** <span id="roll_size"/> 是輪轉日誌檔案的大小。目前的實現支援千位元組（MB）解析度；小數值會無條件進位到下一個整數 MB。例如，`1.1MiB` 會無條件進位到 `2MiB`。

  此項始終啟用。如果對日誌的寫入導致檔案超過指定大小，日誌將立即輪轉。備份檔案名將包含 `size` 作為原因。

  預設值：`100MiB`

- **roll_interval** <span id="roll_interval"/> 是日誌輪轉之間的最大持續時間。該值是輪轉日誌檔案後的 [持續時間字串](/docs/conventions#durations)。

  啟用後，在上次輪轉後經過此持續時間後，下次寫入日誌時將輪轉檔案。備份檔案名將包含 `time` 作為原因。

  請注意，如果設置為 `24h`，它不一定在午夜輪轉，而是在自上次輪轉後的 24 小時標記處輪轉。如果由於大小發生輪轉，則下次輪轉的時間將與上次輪轉的時間偏移。您可以使用 `roll_at` 或 `roll_minutes` 選項在特定時間輪轉。

  預設值：禁用

- **roll_minutes** <span id="roll_minutes"/> 是輪轉日誌檔案的分鐘值列表（0-59）。例如，`10 40` 將在每小時的 `xx:10` 和 `xx:40` 每 30 分鐘輪轉一次日誌檔案。輪轉與時鐘分鐘對齊（第 0 秒）。

  啟用此項會啟動一個 goroutine 定時器，在指定的分鐘值觸發日誌輪轉（即引入少量後台處理）。這是在 `roll_interval` 和 `roll_size` 之外運行的。備份檔案名將包含 `time` 作為原因。

  預設值：禁用

- **roll_at** <span id="roll_at"/> 是輪轉日誌檔案的時間值列表（24 小時格式）。例如，`00:00 12:00` 將在每天午夜和中午輪轉兩次日誌檔案。輪轉與時鐘分鐘對齊（第 0 秒）。

  啟用此項會啟動一個 goroutine 定時器，在指定的時間觸發日誌輪轉（即引入少量後台處理）。這是在 `roll_interval` 和 `roll_size` 之外運行的。備份檔案名將包含 `time` 作為原因。

  預設值：禁用

- **roll_uncompressed** <span id="roll_uncompressed"/> 關閉 gzip 日誌壓縮。

  預設值：啟用 `gzip` 壓縮。

- **roll_local_time** <span id="roll_local_time"/> 設置輪轉在檔案名中使用本地時間戳。
  預設值：使用 UTC 時間。

- **roll_keep** <span id="roll_keep"/> 是在刪除最舊的檔案之前要保留多少個日誌檔案。在建立新日誌檔案時觸發。

  預設值：`10`

- **roll_keep_for** <span id="roll_keep_for"/> 是將輪轉後的檔案保留多久的 [持續時間字串](/docs/conventions#durations)。在建立新日誌檔案時觸發。
  目前的實現支援天解析度；小數值會無條件進位到下一個整天。例如，`36h`（1.5 天）會無條件進位到 `48h`（2 天）。
  
  預設值：`2160h`（90 天）

- **backup_time_format** <span id="backup_time_format"/> 是備份檔案名中使用的時間格式。必須是有效的時間佈局字串；有關詳細資訊，請參閱 [Go 文本](https://pkg.go.dev/time#pkg-constants)。

  預設值：`2006-01-02T15-04-05`


<a id="net"></a>
#### net

網絡套接字（Network socket）。如果套接字關閉，它將在嘗試重新連接時將日誌傾倒（dump）到 stderr。

```caddy-d
output net <address> {
	dial_timeout <duration>
	soft_start
}
```

- **&lt;address&gt;** 是寫入日誌的 [位址](/docs/conventions#network-addresses)。

- **dial_timeout** <span id="dial_timeout"/> 是等待成功連接到日誌套接字的時間。如果套接字關閉，日誌發送可能會被阻塞長達此時間。

- **soft_start** <span id="soft_start"/> 將在連接套接字時忽略錯誤，即使遠端日誌服務關閉，也可以載入您的配置。日誌將發送到 stderr。


<a id="format-modules"></a>
### 格式模組

**format** 子指令讓您自定義日誌的編碼（格式化）方式。它出現在 `log` 塊中。

<aside class="tip">

**關於通用日誌格式 (CLF) 的說明：** CLF 與現代結構化日誌衝突。要將您的存取日誌轉換為已棄用的通用日誌格式，請使用 [`transform-encoder` 插件 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder)。

</aside>


除了每個單獨編碼器的語法之外，大多數編碼器都可以設置以下通用屬性：

```caddy-d
format <encoder_module> {
	message_key     <key>
	level_key       <key>
	time_key        <key>
	name_key        <key>
	caller_key      <key>
	stacktrace_key  <key>
	line_ending     <char>
	time_format     <format>
	time_local
	duration_format <format>
	level_format    <format>
}
```

- **message_key** <span id="message_key"/> 日誌條目訊息欄位的鍵（Key）。預設值：`msg`

- **level_key** <span id="level_key"/> 日誌條目級別欄位的鍵。預設值：`level`

- **time_key** <span id="time_key"/> 日誌條目時間欄位的鍵。預設值：`ts`
- **name_key** <span id="name_key"/> 日誌條目名稱欄位的鍵。預設值：`name`

- **caller_key** <span id="caller_key"/> 日誌條目呼叫者（caller）欄位的鍵。

- **stacktrace_key** <span id="stacktrace_key"/> 日誌條目堆疊追蹤欄位的鍵。

- **line_ending** <span id="line_ending"/> 要使用的行尾。

- **time_format** <span id="time_format"/> 時間戳的格式。
  預設值：如果格式預設為 `console`，則為 `wall_milli`，否則為 `unix_seconds_float`。
  
  可以是以下之一：
  - `unix_seconds_float` 自 Unix 紀元以來的浮點秒數。
  - `unix_milli_float` 自 Unix 紀元以來的浮點毫秒數。
  - `unix_nano` 自 Unix 紀元以來的整數納秒數。
  - `iso8601` 範例：`2006-01-02T15:04:05.000Z0700`
  - `rfc3339` 範例：`2006-01-02T15:04:05Z07:00`
  - `rfc3339_nano` 範例：`2006-01-02T15:04:05.999999999Z07:00`
  - `wall` 範例：`2006/01/02 15:04:05`
  - `wall_milli` 範例：`2006/01/02 15:04:05.000`
  - `wall_nano` 範例：`2006/01/02 15:04:05.000000000`
  - `common_log` 範例：`02/Jan/2006:15:04:05 -0700`
  - 或者，任何相容的時間佈局字串；有關詳細資訊，請參閱 [Go 文本](https://pkg.go.dev/time#pkg-constants)。
  
  請注意，格式字串的部分是佈局的特殊常量；因此 `2006` 是年份，`01` 是月份，`Jan` 是作為字串的月份，`02` 是日期。請勿在格式字串中使用實際的目前日期數字。

- **time_local** <span id="time_local"/> 使用本地系統時間而不是預設的 UTC 時間進行記錄。

- **duration_format** <span id="duration_format"/> 持續時間的格式。

  預設值：`seconds`。
  
  可以是以下之一：
  - `s`, `second` 或 `seconds` 經過的浮點秒數。
  - `ms`, `milli` 或 `millis` 經過的浮點毫秒數。
  - `ns`, `nano` 或 `nanos` 經過的整數納秒數。
  - `string` 使用 Go 的內置字串格式，例如 `1m32.05s` 或 `6.31ms`。

- **level_format** <span id="level_format"/> 級別的格式。

  預設值：如果格式預設為 `console`，則為 `color`，否則為 `lower`。
  
  可以是以下之一：
  - `lower` 小寫。
  - `upper` 大寫。
  - `color` 大寫，帶有 ANSI 顏色。
  

<a id="console"></a>
#### console

console 編碼器將日誌條目格式化為人類可讀，同時保留一些結構。

```caddy-d
format console
```

<a id="json"></a>
#### json

將每個日誌條目格式化為 JSON 對象。

```caddy-d
format json
```


<a id="filter"></a>
#### filter

允許按欄位過濾。

```caddy-d
format filter {
	fields {
		<field> <filter> ...
	}
	<field> <filter> ...
	wrap <encode_module> ...
}
```

嵌套欄位可以通過用 `>` 表示嵌套層來引用。換句話說，對於像 `{"a":{"b":0}}` 這樣的對象，內部欄位可以引用為 `a>b`。

以下欄位是日誌的基礎欄位，不能被過濾，因為它們是由底層日誌庫作為特殊情況添加的：`ts`、`level`、`logger` 和 `msg`。

指定 `wrap` 是可選的；如果省略，則根據當前輸出模組是 [`stderr`](#stderr) 還是 [`stdout`](#stdout) 且是否為互動式終端來選擇預設值，如果是，則選擇 [`console`](#console)，否則選擇 [`json`](#json)。

作為捷徑，可以省略 `fields` 塊，直接在 `filter` 塊內指定過濾器。


以下是可用的過濾器：

<a id="delete"></a>
##### delete

標記一個欄位在編碼時被跳過。

```caddy-d
<field> delete
```


<a id="rename"></a>
##### rename

重命名日誌欄位的鍵。

```caddy-d
<field> rename <key>
```


<a id="replace"></a>
##### replace

標記一個欄位在編碼時被替換為提供的字串。

```caddy-d
<field> replace <replacement>
```


<a id="ip-mask"></a>
##### ip_mask

使用 CIDR 遮罩遮罩欄位中的 IP 位址，即從左側開始要保留的 IP 位元數。如果欄位是字串數組（例如 HTTP 標頭），則數組中的每個值都會被遮罩。該值可以是逗號分隔的 IP 位址字串。

IPv4 和 IPv6 位址有單獨的配置，因為它們的位元總數不同。

最常見的過濾欄位是：
- `request>remote_ip` 用於直接連接的客戶端
- `request>client_ip` 用於配置了 [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) 時解析的 "真實客戶端"
- `request>headers>X-Forwarded-For` 如果在反向代理後面

```caddy-d
<field> ip_mask [<ipv4> [<ipv6>]] {
	ipv4 <cidr>
	ipv6 <cidr>
}
```


<a id="query"></a>
##### query

標記一個欄位執行一個或多個操作，以操作 URL 欄位的查詢部分。最常見的過濾欄位是 `request>uri`。

```caddy-d
<field> query {
	delete  <key>
	replace <key> <replacement>
	hash    <key>
}
```

可用的操作有：

- **delete** 從查詢中刪除給定的鍵。

- **replace** 將給定查詢鍵的值替換為 **replacement**。用於插入遮蔽佔位符；您會看到查詢鍵在 URL 中，但值被隱藏了。

- **hash** 將給定查詢鍵的值替換為該值 SHA-256 哈希值的前 4 個位元組（小寫十六進制）。如果值是敏感的，這對於模糊值很有用，同時能夠注意到每個請求是否具有不同的值。


<a id="cookie"></a>
##### cookie

標記一個欄位執行一個或多個操作，以操作 `Cookie` HTTP 標頭的值。最常見的過濾欄位是 `request>headers>Cookie`。

```caddy-d
<field> cookie {
	delete  <name>
	replace <name> <replacement>
	hash    <name>
}
```

可用的操作有：

- **delete** 按名稱從標頭中刪除給定的 Cookie。

- **replace** 將給定 Cookie 的值替換為 **replacement**。用於插入遮蔽佔位符；您會看到 Cookie 在標頭中，但值被隱藏了。

- **hash** 將給定 Cookie 的值替換為該值 SHA-256 哈希值的前 4 個位元組（小寫十六進制）。如果值是敏感的，這對於模糊值很有用，同時能夠注意到每個請求是否具有不同的值。

如果為同一個 Cookie 名稱定義了多個操作，則僅應用第一個操作。


<a id="regexp"></a>
##### regexp

標記一個欄位在編碼時應用正規表達式替換。如果欄位是字串數組（例如 HTTP 標頭），則數組中的每個值都會應用替換。

```caddy-d
<field> regexp <pattern> <replacement>
```

使用的正規表達式語言是 Go 中包含的 RE2。請參閱 [RE2 語法參考](https://github.com/google/re2/wiki/Syntax) 和 [Go regexp 語法概述](https://pkg.go.dev/regexp/syntax)。

在替換字串中，可以使用 `${group}` 引用擷取群組，其中 `group` 是表達式中擷取群組的名稱或編號。擷取群組 `0` 是完整的正規表達式匹配，`1` 是第一個擷取群組，`2` 是第二個擷取群組，依此類推。


<a id="hash"></a>
##### hash

標記一個欄位在編碼時被替換為該值 SHA-256 哈希值的前 4 個位元組（8 個十六進制字元）。如果欄位是字串數組（例如 HTTP 標頭），則數組中的每個值都會被哈希。

如果值是敏感的，這對於模糊值很有用，同時能夠注意到每個請求是否具有不同的值。

```caddy-d
<field> hash
```

<a id="append"></a>
#### append

將欄位附加到所有日誌條目。

```caddy-d
format append {
	fields {
		<field> <value>
	}
	<field> <value>
	wrap <encode_module> ...
}
```

這對於添加有關產生日誌條目的 Caddy 實例的資訊最有用，可能通過環境變數。欄位值可以是全域佔位符（例如 `{env.*}`），但 *不能* 是每個請求的佔位符，因為日誌是在 HTTP 請求上下文之外寫入的。

指定 `wrap` 是可選的；如果省略，則根據當前輸出模組是 [`stderr`](#stderr) 還是 [`stdout`](#stdout) 且是否為互動式終端來選擇預設值，如果是，則選擇 [`console`](#console)，否則選擇 [`json`](#json)。

可以省略 `fields` 塊，直接在 `append` 塊內指定欄位。



<a id="examples"></a>
## 範例

啟用對預設日誌記錄器的存取日誌記錄。

換句話說，預設情況下，這會記錄到 `stderr`，但可以透過使用 [`log` 全域選項](/docs/caddyfile/options#log) 重新配置 `default` 日誌記錄器來更改此設定：

```caddy
example.com {
	log
}
```


將日誌寫入檔案（使用預設啟用的日誌輪轉）：

```caddy
example.com {
	log {
		output file /var/log/access.log
	}
}
```


自定義日誌輪轉，每天午夜或日誌檔案達到 1 GB 時輪轉（以先到者為準），並保留 5 個輪轉後的檔案或 30 天的日誌：

```caddy
example.com {
	log {
		output file /var/log/access.log {
			roll_at 00:00
			roll_size 1gb
			roll_keep 5
			roll_keep_for 720h
		}
	}
}
```


從日誌中刪除 `User-Agent` 請求標頭：

```caddy
example.com {
	log {
		format filter {
			request>headers>User-Agent delete
		}
	}
}
```


遮蔽多個敏感 Cookie。（請注意，預設情況下某些敏感標頭會以空值記錄；請參閱 [`log_credentials` 全域選項](/docs/caddyfile/options#log-credentials) 以啟用 `Cookie` 標頭值的記錄）：

```caddy
example.com {
	log {
		format filter {
			request>headers>Cookie cookie {
				replace session REDACTED
				delete secret
			}
		}
	}
}
```


遮罩請求中的遠端位址，IPv4 位址保留前 16 位元（即 255.255.0.0），IPv6 位址保留前 32 位元。

請注意，從 Caddy v2.7 開始，`remote_ip` 和 `client_ip` 都會被記錄，其中 `client_ip` 是配置了 [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) 時的 "真實 IP"：

```caddy
example.com {
	log {
		format filter {
			request>remote_ip ip_mask 16 32
			request>client_ip ip_mask 16 32
		}
	}
}
```


要將環境變數中的伺服器 ID 附加到所有日誌條目，並將其與 `filter` 連結以刪除標頭：

```caddy
example.com {
	log {
		format append {
			server_id {env.SERVER_ID}
			wrap filter {
				request>headers>Cookie delete
			}
		}
	}
}
```


<span id="wildcard-logs" /> 通過為每個日誌記錄器覆蓋 `hostnames`，為 [萬用字元站點塊](/docs/caddyfile/patterns#wildcard-certificates) 中的每個子網域寫入單獨的日誌檔案。這使用 [片段 (snippet)](/docs/caddyfile/concepts#snippets) 來避免重複：

```caddy
(subdomain-log) {
	log {
		hostnames {args[0]}
		output file /var/log/{args[0]}.log
	}
}

*.example.com {
	import subdomain-log foo.example.com
	@foo host foo.example.com
	handle @foo {
		respond "foo"
	}

	import subdomain-log bar.example.com
	@bar host bar.example.com
	handle @bar {
		respond "bar"
	}
}
```

<span id="multiple-outputs" /> 將特定子網域的存取日誌寫入兩個不同的檔案，具有不同的格式（一個使用 [`transform-encoder` 插件 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder)，另一個使用 [`json`](#json)）。

這透過在站點塊中將日誌記錄器名稱覆蓋為 `foo` 來實現，然後在全域選項中使用 `include http.log.access.foo` 將該日誌記錄器產生的存取日誌包含在兩個日誌記錄器中：

```caddy
{
	log access-formatted {
		include http.log.access.foo
		output file /var/log/access-foo.log
		format transform "{common_log}"
	}

	log access-json {
		include http.log.access.foo
		output file /var/log/access-foo.json
		format json
	}
}

foo.example.com {
	log foo
}
```

<span id="sampling-example" /> 使用採樣減少日誌量，例如每秒保留前 5 個請求，然後在此之後每 10 個請求中保留 1 個：

```caddy
example.com {
	log {
		sampling {
			interval   1s
			first      5
			thereafter 10
		}
	}
}
```
