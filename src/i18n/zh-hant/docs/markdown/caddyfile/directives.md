---
title: Caddyfile 指令
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

<a id="caddyfile-directives"></a>
# Caddyfile 指令

指令（Directives）是出現在網站 [blocks](/docs/caddyfile/concepts#blocks) 中具有功能性的關鍵字。有時，它們可能會開啟自己的區塊，其中可以包含 *subdirectives*，但除非另有說明，否則指令 **cannot** 在其他指令中使用。例如，你不能在 `file_server` 區塊中使用 `basic_auth`，因為 `file_server` 不知道如何執行身份驗證。但是，你 *may* 在 `handle` 和 `route` 等特殊指令區塊中使用某些指令，因為它們是專門為 HTTP handler 指令分組而設計的。

- [語法](#syntax)
- [指令順序](#directive-order)
- [排序演算法](#sorting-algorithm)

以下指令是 Caddy 標配，可用於 HTTP Caddyfile：

<div id="directive-table">

指令 | 描述
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | 中止 HTTP 請求
**[acme_server](/docs/caddyfile/directives/acme_server)** | 嵌入式 ACME 伺服器
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | 強制執行 HTTP 基本身份驗證
**[bind](/docs/caddyfile/directives/bind)** | 自定義伺服器的通訊端位址 (socket address)
**[encode](/docs/caddyfile/directives/encode)** | 編碼（通常是壓縮）回應
**[error](/docs/caddyfile/directives/error)** | 觸發錯誤
**[file_server](/docs/caddyfile/directives/file_server)** | 從磁碟提供檔案服務
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | 將身份驗證委派給外部服務
**[fs](/docs/caddyfile/directives/fs)** | 設置用於檔案 I/O 的檔案系統
**[handle](/docs/caddyfile/directives/handle)** | 一組互斥的指令
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | 定義處理錯誤的路由
**[handle_path](/docs/caddyfile/directives/handle_path)** | 類似 handle，但會剝離路徑前綴
**[header](/docs/caddyfile/directives/header)** | 設置或移除回應標頭
**[import](/docs/caddyfile/directives/import)** | 包含程式碼片段或檔案
**[intercept](/docs/caddyfile/directives/intercept)** | 攔截其他 handler 寫入的回應
**[invoke](/docs/caddyfile/directives/invoke)** | 調用具名路由
**[log](/docs/caddyfile/directives/log)** | 啟用存取/請求日誌
**[log_append](/docs/caddyfile/directives/log_append)** | 向存取日誌追加欄位
**[log_skip](/docs/caddyfile/directives/log_skip)** | 對匹配的請求跳過存取日誌
**[log_name](/docs/caddyfile/directives/log_name)** | 覆蓋要寫入的日誌名稱
**[map](/docs/caddyfile/directives/map)** | 將輸入值映射到一個或多個輸出
**[method](/docs/caddyfile/directives/method)** | 在內部更改 HTTP 方法
**[metrics](/docs/caddyfile/directives/metrics)** | 配置 Prometheus 指標呈現端點
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | 通過 FastCGI 提供 PHP 網站服務
**[push](/docs/caddyfile/directives/push)** | 使用 HTTP/2 伺服器推播向用戶端推送內容
**[redir](/docs/caddyfile/directives/redir)** | 向用戶端發出 HTTP 重定向
**[request_body](/docs/caddyfile/directives/request_body)** | 操作請求主體
**[request_header](/docs/caddyfile/directives/request_header)** | 操作請求標頭
**[respond](/docs/caddyfile/directives/respond)** | 向用戶端寫入硬編碼的回應
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | 功能強大且可擴展的反向代理
**[rewrite](/docs/caddyfile/directives/rewrite)** | 在內部重寫請求
**[root](/docs/caddyfile/directives/root)** | 設置網站根目錄的路徑
**[route](/docs/caddyfile/directives/route)** | 一組被視為單一單位的指令
**[templates](/docs/caddyfile/directives/templates)** | 在回應上執行模板
**[tls](/docs/caddyfile/directives/tls)** | 自定義 TLS 設置
**[tracing](/docs/caddyfile/directives/tracing)** | 與 OpenTelemetry 追蹤集成
**[try_files](/docs/caddyfile/directives/try_files)** | 取決於檔案是否存在的重寫
**[uri](/docs/caddyfile/directives/uri)** | 操作 URI
**[vars](/docs/caddyfile/directives/vars)** | 設置任意變數

</div>

<a id="syntax"></a>
## 語法

每個指令的語法看起來像這樣：

```caddy-d
directive [<matcher>] <args...> {
	subdirective [<args...>]
}
```

`<尖括號>` 表示要替換為實際值的權杖。

`[方括號]` 表示選擇性參數。

省略號 `...` 表示延續，即一個或多個參數或行。

除非另有說明，否則 *subdirectives* 通常是可選的，即使它們沒有出現在 `[方括號]` 中。


<a id="matchers"></a>
### Matcher

大多數（但不是全部）指令都接受 [matcher 權杖](/docs/caddyfile/matchers#syntax)，這讓你能夠過濾請求。Matcher 權杖通常是可選的。如果你在指令的語法中看到以下內容，則該指令支援 matcher：

```caddy-d
[<matcher>]
```

因為 matcher 權杖的工作方式都相同，為了減少重複，每頁都不會描述 matcher 權杖的各種可能性。請參閱 [matcher 文檔](/docs/caddyfile/matchers) 以獲取語法的詳細說明。


<a id="directive-order"></a>
## 指令順序

許多指令會操作 HTTP handler 鏈。評估這些指令的順序非常重要，因此 Caddy 內建了默認排序。

你可以通過使用 [`order` 全域選項](/docs/caddyfile/options#order) 或 [`route` 指令](/docs/caddyfile/directives/route) 來覆蓋/自定義此順序。

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # 僅在 reverse_proxy 的 handle_response 區塊中有效
request_body

redir

# 傳入請求操作
method
rewrite
uri
try_files

# 中間件 handler；有些會封裝回應
basic_auth
forward_auth
request_header
encode
push
intercept
templates

# 特殊的路由與分派指令
invoke
handle
handle_path
route

# 通常用於回應請求的 handler
abort
error
copy_response # 僅在 reverse_proxy 的 handle_response 區塊中有效
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



<a id="sorting-algorithm"></a>
## 排序演算法

為了便於使用，Caddyfile 配接器根據以下規則對指令進行排序：

- 不同名稱的指令根據它們在 [預設順序](#directive-order) 中的位置進行排序。預設順序可以通過 [`order` 全域選項](/docs/caddyfile/options) 進行覆蓋。來自外掛程式的指令 *do not* 具有順序，因此應使用 [`order`](/docs/caddyfile/options) 全域選項或 [`route`](/docs/caddyfile/directives/route) 指令來設置一個。

- 同名的指令根據其 [matchers](/docs/caddyfile/matchers#syntax) 進行排序。

  - 最高優先級是具有單個 [路徑 matcher](/docs/caddyfile/matchers#path-matchers) 的指令。

    路徑 matcher 按特異性（specificity）排序，從最精確到最不精確。
	
	通常，這是通過路徑 matcher 的長度進行排序來執行的。有一個例外：如果路徑以 `*` 結尾，而兩個 matcher 的路徑在其他方面相同，則不帶 `*` 的 matcher 被視為更精確且排序更高。

    例如：
    - `/foobar` 比 `/foo` 更精確
    - `/foo` 比 `/foo*` 更精確
    - `/foo/*` 比 `/foo*` 更精確

  - 具有任何其他 matcher 的指令排在後面，按其在 Caddyfile 中出現的順序排列。

    這包括具有多個值的路徑 matcher 以及 [具名 matcher](/docs/caddyfile/matchers#named-matchers)。

  - 沒有 matcher 的指令（即匹配所有請求）排在最後。

- [`vars`](/docs/caddyfile/directives/vars) 指令的 matcher 排序相反，因為它涉及設置可能互相覆蓋的值，因此評估順序應為最精確的 matcher 最後評估。

- [`route`](/docs/caddyfile/directives/route) 指令的內容忽略上述所有規則，並保留指令在其中出現的順序。
