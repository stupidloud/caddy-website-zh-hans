---
title: 全域選項 (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the options in the code block at the top
	// to their associated anchor tags.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Add links on comments to their respective sections
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // the leading whitespace
			text = text.slice(text.indexOf('#')); // only the comment part
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Surgically fix a duplicate link; 'name' appears twice as a link
	// for two different sections, so we change the second to #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// Surgically fix `renewal_window_ratio` which appears twice as a link for two different sections, so we change the second to #renewal_window_ratio-1
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>

<a id="global-options"></a>
# 全域選項

Caddyfile 提供了一種方式供您指定全域應用的選項。有些選項作為預設值；有些用於自訂 HTTP 伺服器，且不只應用於某個特定站點；而另一些則用於自訂 Caddyfile [轉接器 (adapter)](/docs/config-adapters) 的行為。

Caddyfile 的最頂部可以是一個 **全域選項塊 (global options block)** 。這是一個沒有鍵 (key) 的區塊：

```caddy
{
	...
}
```

最多只能有一個，且必須是 Caddyfile 的第一個區塊。

可用的選項如下（點擊每個選項跳轉到其文件）：

```caddy
{
	# 一般選項 (General Options)
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hosts...>
	order <dir1> first|last|[before|after <dir2>]
	storage <module_name> {
		<options...>
	}
	storage_clean_interval <duration>
	admin   off|<addr> {
		origins <origins...>
		enforce_origin
	}
	persist_config off
	log [name] {
		output  <writer_module> ...
		format  <encoder_module> ...
		level   <level>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <duration>
	shutdown_delay <duration>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# TLS 選項 (TLS Options)
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <yours>
	default_sni <name>
	fallback_sni <name>
	local_certs
	skip_install_trust
	acme_ca <directory_url>
	acme_ca_root <pem_file>
	acme_eab {
		key_id <key_id>
		mac_key <mac_key>
	}
	acme_dns <provider> ...
	dns <provider> ...
	ech <public_names...> {
		dns <provider> ...
	}
	on_demand_tls {
		ask        <endpoint>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <name> ...
	renew_interval <duration>
	cert_lifetime  <duration>
	ocsp_interval  <duration>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# 伺服器選項 (Server Options)
	servers [<listener_address>] {
		name <name>
		listener_wrappers {
			<listener_wrappers...>
		}
		timeouts {
			read_body   <duration>
			read_header <duration>
			write       <duration>
			idle        <duration>
		}
		keepalive_interval <duration>
		keepalive_idle     <duration>
		keepalive_count	   <number>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <headers...>

		trace
		max_header_size <size>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# 檔案系統 (File Systems)
	filesystem <name> <module> {
		<options...>
	}

	# PKI 選項 (PKI Options)
	pki {
		ca [<id>] {
			name                  <name>
			root_cn               <name>
			intermediate_cn       <name>
			intermediate_lifetime <duration>
			maintenance_interval  <duration>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <path>
				key    <path>
			}
			intermediate {
				format <format>
				cert   <path>
				key    <path>
			}
		}
	}

	# 事件選項 (Event options)
	events {
		on <event> <handler...>
	}
}
```


<a id="general-options"></a>
## 一般選項 (General Options)

<a id="debug"></a>
##### `debug`
啟用除錯模式，這會將 [預設記錄器 (#log)](#log) 的記錄層級設定為 `DEBUG`。這會揭露更多在故障排除時非常有用的細節（在正式環境中會非常冗長）。我們建議您在 [社群論壇](https://caddy.community) 尋求幫助之前先啟用此功能。例如，在您的 Caddyfile 頂部，如果您沒有其他全域選項：

```caddy
{
	debug
}
```


<a id="http-port"></a>
##### `http_port`
伺服器用於 HTTP 的連接埠。

**僅供內部使用** ；不會更改客戶端的 HTTP 連接埠。這通常用於您的內部網路中，如果您出於路由目的需要在請求到達 Caddy 之前將 `80` 轉發到不同的連接埠（例如 `8080`）。

預設值：`80`


<a id="https-port"></a>
##### `https_port`
伺服器用於 HTTPS 的連接埠。

**僅供內部使用** ；不會更改客戶端的 HTTPS 連接埠。這通常用於您的內部網路中，如果您出於路由目的需要在請求到達 Caddy 之前將 `443` 轉發到不同的連接埠（例如 `8443`）。

預設值：`443`


<a id="default-bind"></a>
##### `default_bind`
如果站點中未使用 [`bind` 指令](/docs/caddyfile/directives/bind)，則用於所有站點的預設綁定位址。預設值：空，即綁定到所有介面。

<aside class="tip">

請記住，這僅適用於由 Caddyfile 生成的伺服器；這意味著由 [自動 HTTPS (Automatic HTTPS)](/docs/automatic-https) 建立的用於 HTTP 到 HTTPS 重新導向的 HTTP 伺服器將不會繼承這些綁定位址。要解決此問題，請確保聲明一個 `http://` 站點（可以是空的，沒有指令），以便在轉接 Caddyfile 時它存在，以接收綁定位址。

</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



<a id="order"></a>
##### `order`
為 HTTP handler 指令分配順序。由於 HTTP handler 在順序鏈中執行，因此 handler 以正確的順序執行是必要的。標準指令具有 [預定義的順序](/docs/caddyfile/directives#directive-order)，但如果使用第三方 HTTP handler 模組，您需要透過使用此選項或將指令放在 [`route` 區塊](/docs/caddyfile/directives/route) 中來顯式定義順序。順序可以相對於另一個指令進行絕對描述（`first` 或 `last`）或相對描述（`before` 或 `after`）。

例如，要使用 [`replace-response` 外掛](https://github.com/caddyserver/replace-response)，您需要確保其指令順序在 `encode` 之後，以便它可以在回應被編碼之前執行替換（因為回應是沿著 handler 鏈向上流動，而不是向下）：

```caddy
{
	order replace after encode
}
```


<a id="storage"></a>
##### `storage`
設定 Caddy 的儲存機制。預設值為 [`file_system`](/docs/json/storage/file_system/)。還有許多其他可用的 [儲存模組](/docs/json/storage/) 作為外掛提供。

例如，更改檔案系統的儲存位置：

```caddy
{
	storage file_system /path/to/custom/location
}
```

自訂儲存模組通常在多個 Caddy 實例之間同步 Caddy 儲存時需要，以確保它們都使用相同的憑證和金鑰。有關更多詳細資訊，請參閱 [自動 HTTPS 關於儲存的部分](/docs/automatic-https#storage)。


<a id="storage-clean-interval"></a>
##### `storage_clean_interval`
掃描儲存單元以尋找舊的或過期的資產並將其移除的頻率。這些掃描會對儲存模組執行大量讀取（和列表操作），因此對於大型部署請選擇較長的間隔。接受 [持續時間值](/docs/conventions#durations)。

當程序首次啟動時，將始終清理儲存。然後，如果上一次清理在少於此間隔一半的時間內完成，則在上一次清理開始後的此持續時間後將開始新的清理（否則將跳過下一次啟動）。

預設值：`24h`

```caddy
{
	storage_clean_interval 7d
}
```




<a id="admin"></a>
##### `admin`
自訂 [admin API 端點](/docs/api)。接受 placeholder 。接受 [網路位址](/docs/conventions#network-addresses)。

預設值：`localhost:2019`，除非設定了 `CADDY_ADMIN` 環境變數。

如果設定為 `off`，則 admin 端點將被停用。停用後，如果不停止並啟動伺服器，**將無法進行設定變更** ，因為 [`caddy reload` 命令](/docs/command-line#caddy-reload) 使用 admin API 將新設定推送到正在運行的伺服器。

請記住，如果正在運行的伺服器的位址已從預設值更改，請將 `--address` CLI 旗標與相容的 [命令](/docs/command-line) 一起使用以指定當前的 admin 端點。

還支援以下子選項：

- **origins** 設定允許連接到端點的 [來源 (origins)](https://developer.mozilla.org/en-US/docs/Glossary/Origin) 列表。

  會智慧地選擇一個預設值：
  - 如果監聽位址是 loopback（例如 `localhost` 或 loopback IP，或 unix socket），則允許的來源是 `localhost`、`::1` 和 `127.0.0.1`，並結合監聽位址連接埠（因此 `localhost:2019` 是一個有效的來源）。
  - 如果監聽位址不是 loopback，則允許的來源與監聽位址相同。

  如果監聽位址主機不是通配符介面（通配符包括：空字串、或 `0.0.0.0`、或 `[::]`），則執行 `Host` 標頭強制執行。實際上，這意味著預設情況下，由於介面是 `localhost`，因此 `Host` 標頭會被驗證是否在 `origins` 中。但對於像 `:2020` 這樣具有通配符介面的位址，則不執行 `Host` 標頭驗證。

- **enforce_origin** 強制執行 `Origin` 請求標頭。每當客戶端發送 CORS 標頭或客戶端使用 `Sec-Fetch-Mode: no-cors` 顯式停用 CORS 時，這都會隱式完成。否則，當監聽位址是通配符介面（因為不驗證 `Host`）且 admin API 暴露於公共網路時，此選項最有用。它啟用 CORS 預檢檢查並確保根據 `origins` 列表驗證 `Origin` 標頭。僅當您在開發機器上執行 Caddy 且需要從網頁瀏覽器存取 admin API 時才使用此選項。

例如，在所有介面上的不同連接埠上公開 admin API —— ⚠️ 此連接埠 **不應公開公開** ，否則任何人都可以控制您的伺服器；如果您需要公開，請考慮啟用來源強制執行：

```caddy
{
	admin :2020
}
```

關閉 admin API —— ⚠️ 這使得 **設定重新載入變為不可能** ，除非停止並啟動伺服器：

```caddy
{
	admin off
}
```

要為 admin API 使用 [unix socket](/docs/conventions#network-addresses)，允許透過檔案權限進行存取控制：

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

僅允許具有匹配 `Origin` 標頭的請求：

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```



<a id="persist-config"></a>
##### `persist_config`

控制是否應將當前的 JSON 設定持久化到 [設定目錄](/docs/conventions#configuration-directory)，以避免丟失透過 admin API 執行的設定變更。目前僅支援 `off` 選項。預設情況下，設定會被持久化。

```caddy
{
	persist_config off
}
```



<a id="log"></a>
##### `log`
設定命名記錄器。

可以傳遞名稱以指示要自訂其行為的特定記錄器。如果未指定名稱，則修改 `default` 記錄器的行為。您可以閱讀有關 `default` 記錄器的更多資訊以及對 [Caddy 記錄運作方式](/docs/logging) 的說明。

可以透過多次使用 `log` 來設定具有不同名稱的多個記錄器。

這與 [`log` 指令](/docs/caddyfile/directives/log) 不同，後者僅設定 HTTP 請求記錄（也稱為存取日誌）。`log` 全域選項與該指令共享其設定結構（`include` 和 `exclude` 除外），完整的內容可以在指令的頁面上找到。

- **output** 設定將日誌寫入何處。

  請參閱 [`log` 指令](/docs/caddyfile/directives/log#output-modules) 以獲取完整的內容。

- **format** 描述如何編碼或格式化日誌。

  請參閱 [`log` 指令](/docs/caddyfile/directives/log#format-modules) 以獲取完整的內容。

- **level** 是要記錄的最低輸入層級。

  預設值：`INFO`。

  可能的值：`DEBUG`、`INFO`、`WARN`、`ERROR`，以及極少見的 `PANIC`、`FATAL`。

- **include** 指定要包含在此記錄器中的日誌名稱。

  預設情況下，此列表為空（即包含所有日誌）。

  例如，要僅包含由 admin API 發出的日誌，您可以包含 `admin.api`。

- **exclude** 指定要從此記錄器中排除的日誌名稱。

  預設情況下，此列表為空（即不排除任何日誌）。

  例如，要僅排除 HTTP 存取日誌，您可以排除 `http.log.access`。

`include` 和 `exclude` 接受的記錄器名稱取決於所使用的模組，發現它們的最簡單方法是從先前的日誌中查找。

這是一個將所有 http 存取日誌和 admin 日誌作為 json 記錄到 stdout 的範例：

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

<a id="grace-period"></a>
##### `grace_period`
定義關閉 HTTP 伺服器的寬限期（即在設定變更期間或 Caddy 停止時）。

在寬限期內，不接受新連接，關閉空閒連接，並焦急地等待活動連接完成其請求。如果客戶端在寬限期內未完成其請求，伺服器將被強制終止以允許重新載入完成並釋放資源。接受 [持續時間值](/docs/conventions#durations)。

預設情況下，寬限期是永恆的，這意味著永遠不會強制關閉連接。

```caddy
{
	grace_period 10s
}
```


<a id="shutdown-delay"></a>
##### `shutdown_delay`
在 [寬限期 (#grace_period)](#grace_period) *before* 定義一個 [持續時間](/docs/conventions#durations) ，在此期間即將停止的伺服器繼續正常運行，除了 `{http.shutting_down}` placeholder 求值為 `true` 且 `{http.time_until_shutdown}` 給出到寬限期開始為止的時間。

如果任何伺服器作為設定變更的一部分而被關閉，這會導致延遲，並有效地將變更安排在稍後的時間。這對於向此伺服器即將滅亡的健康檢查員宣佈以及為負載平衡器將其從輪換中移除提供時間非常有用；例如：

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Bye-bye in {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Hello, world!"
	}
}
```


<a id="tls-options"></a>
## TLS 選項 (TLS Options)

<a id="auto-https"></a>
##### `auto_https`
設定 [自動 HTTPS (Automatic HTTPS)](/docs/automatic-https)，這是使 Caddy 能夠為您的站點自動執行憑證管理和 HTTP 到 HTTPS 重新導向的功能。

有幾種模式可供選擇：

- `off`：停用憑證自動化和 HTTP 到 HTTPS 重新導向。

- `disable_redirects`：僅停用 HTTP 到 HTTPS 重新導向。

- `disable_certs`：僅停用憑證自動化。

- `ignore_loaded_certs`：即使名稱出現在手動載入的憑證上，也要自動執行憑證。如果您使用 [`tls` 指令](/docs/caddyfile/directives/tls) 指定了一個包含您希望改為自動管理的名稱（或通配符）的憑證，則這非常有用。

<aside class="tip">

當站點位址具有有效的域名時，此選項不會影響 Caddy 的預設通訊協定，該通訊協定始終是 HTTPS。這意味著 `auto_https off` 不會導致您的站點透過 HTTP 提供服務，它只會停用自動憑證管理和重新導向。

這意味著如果您希望透過 HTTP 提供站點服務，則應將 [站點位址](/docs/caddyfile/concepts#addresses) 更改為以 `http://` 為前綴或以 `:80` 為後綴（或 [`http_port` 選項](#http_port)）。

</aside>

```caddy
{
	auto_https disable_redirects
}
```


<a id="email"></a>
##### `email`
您的電子郵件位址。主要用於向您的 CA 建立 ACME 帳戶，強烈建議在您的憑證出現問題時提供此資訊。

<aside class="tip">

請記住，Let's Encrypt 可能會向您發送有關您的憑證即將過期的電子郵件，但這可能會引起誤解，因為 Caddy 在續訂時可能已選擇使用不同的發行者（例如 ZeroSSL）。請檢查您的日誌和/或憑證本身（例如在瀏覽器中）以查看使用了哪個發行者，並且其到期日期仍然有效；如果是這樣，您可以放心地忽略來自 Let's Encrypt 的電子郵件。

</aside>

```caddy
{
	email admin@example.com
}
```


<a id="default-sni"></a>
##### `default_sni`
當客戶端在其 ClientHello 中不使用 SNI 時，設定預設的 TLS ServerName。

```caddy
{
	default_sni example.com
}
```


<a id="fallback-sni"></a>
##### `fallback_sni`
⚠️ *實驗性功能* 

如果設定了此項，則如果原始 ServerName 與快取中的任何憑證都不匹配，則 fallback 將成為 ClientHello 中的 TLS ServerName。

此功能的用途非常小眾；通常，如果客戶端是 CDN 並傳遞下游握手的 ServerName，但可以改為接受具有原始主機名稱的憑證，則您可以將此設定為原始主機名稱。請注意，Caddy 必須正在管理此名稱的憑證。

```caddy
{
	fallback_sni example.com
}
```


<a id="local-certs"></a>
##### `local_certs`
導致預設情況下 **所有** 憑證都由內部簽發，而不是透過（公共）ACME CA（如 Let's Encrypt）。這在開發環境中作為快速切換非常有用。

```caddy
{
	local_certs
}
```


<a id="skip-install-trust"></a>
##### `skip_install_trust`
跳過嘗試將本地 CA 的根安裝到系統信任庫以及 Java 和 Mozilla Firefox 信任庫的嘗試。

```caddy
{
	skip_install_trust
}
```


<a id="acme-ca"></a>
##### `acme_ca`
指定 ACME CA 目錄的 URL。強烈建議將此設定為 Let's Encrypt 的 [測試端點 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) 用於測試或開發。預設值：ZeroSSL 和 Let's Encrypt 的生產端點。

請注意，全域設定的 ACME CA 可能不適用於所有站點；請參閱使用預設 ACME 發行者的 [主機名稱要求](/docs/automatic-https#hostname-requirements)。

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

<a id="acme-ca-root"></a>
##### `acme_ca_root`
指定一個 PEM 檔案，該檔案包含 ACME CA 端點的受信任根憑證（如果不在系統信任庫中）。

```caddy
{
	acme_ca_root /path/to/ca/root.pem
}
```


<a id="acme-eab"></a>
##### `acme_eab`
指定用於所有 ACME 交易的外部帳戶綁定 (External Account Binding)。

例如，使用模擬的 ZeroSSL 憑據：

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


<a id="acme-dns"></a>
##### `acme_dns`
設定用於所有 ACME 交易的 [ACME DNS 驗證](/docs/automatic-https#dns-challenge) 提供者。

需要使用具有適用於您的 DNS 提供者的外掛的 Caddy 自訂版本。

提供者名稱之後的權杖設定提供者，其方式與在 [`tls` 指令的 `acme` 發行者](/docs/caddyfile/directives/tls#acme) 中指定的方式相同。

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


<a id="dns"></a>
##### `dns`
設定當在相關上下文中未本地指定其他 DNS 提供者時使用的預設 DNS 提供者。例如，如果啟用了 ACME DNS 驗證但未設定 DNS 提供者，則將使用此全域預設值。它也應用於發佈加密客戶端 Hello (ECH) 設定。

您的 Caddy 二進位檔案必須使用指定的 DNS 提供者模組編譯，此功能才能運作。

範例，使用來自環境變數的憑據：

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

（需要 Caddy 2.10 beta 1 或更高版本。）


<a id="ech"></a>
##### `ech`
透過使用指定的公共域名作為 TLS 握手中的純文字伺服器名稱 (SNI) 來啟用加密客戶端 Hello (ECH)。在合適的條件下，ECH 可以幫助保護連接期間站點的域名在網路上不被窺探。Caddy 將為指定的每個公共名稱生成並發佈一個 ECH 設定。發佈是讓相容客戶端（例如設定正確的現代瀏覽器）知道使用 ECH 存取您的站點的方式。

為了正常運作，ECH 設定必須以客戶端期望的方式發佈。大多數瀏覽器（啟用了 DNS-over-HTTPS 或 DNS-over-TLS）期望將 ECH 設定發佈到 HTTPS 類型的 DNS 記錄。Caddy 會自動執行此類發佈，但您必須使用 `dns` 子選項或使用 [`dns` 全域選項](#dns) 全域指定 DNS 提供者，並且您的 Caddy 二進位檔案必須使用指定的 DNS 提供者模組構建。（我們的 [下載頁面](/download) 提供自訂構建。）

**隱私聲明：**

- 通常建議 **最大化您的 [*匿名集 (anonymity set)*](https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction) 的大小** 。因此，我們通常建議大多數使用者僅設定 *一個* 公共域名來保護您的所有站點。
- **您的伺服器應該對您指定的公共域名具有權威性** （即它們應該指向您的伺服器），因為 Caddy 將為它們獲取憑證。這些憑證對於幫助符合規範的客戶端在某些情況下透過 ECH 可靠且安全地連接至關重要。它們僅用於促進正確的 ECH 握手，不用於應用程式數據（您的站點 —— 除非您定義了一個與您的公共域名相同的站點）。
- 每個情況可能都不同。如果利害關係重大，我們建議諮詢專家以 **審查您的威脅模型** ，因為 ECH 不是一成不變的解決方案。

使用來自環境變數的憑據發佈到停放在 Cloudflare 的名稱伺服器的範例：

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

這應該會導致相容客戶端使用 `ech.example.net` 載入您的所有站點，而不是以純文字形式暴露的單個站點名稱。

成功發佈要求您的站點域名停放在設定的 DNS 提供者處，並且可以使用給定的憑據 / 提供者設定修改記錄。

（需要 Caddy 2.10 beta 1 或更高版本。）


<a id="on-demand-tls"></a>
##### `on_demand_tls`
設定啟用了 [隨選 TLS (On-Demand TLS)](/docs/automatic-https#on-demand-tls) 的地方，但不會啟用它（要啟用它，請使用 [`tls` 指令的 `on_demand` 子指令](/docs/caddyfile/directives/tls#syntax)）。在生產環境中使用是必需的，以防止濫用。

- **ask** 將導致 Caddy 向給定的 URL 發送 HTTP 請求，詢問是否允許域名簽發憑證。

  請求具有包含域名值的查詢字串 `?domain=`。

如果端點回傳 `2xx` 狀態碼，則 Caddy 將被授權獲取該名稱的憑證。任何其他狀態碼都將導致取消憑證簽發並使 TLS 握手出錯。

<aside class="tip">

ask 端點應 *儘快* 回傳，最好在幾毫秒內。通常，您的端點應在具有按域名索引的資料庫中執行常數時間查找；避免循環。避免進行 DNS 查詢或其他網路請求。

</aside>

- **permission** 允許使用自訂模組來確定是否應為特定名稱簽發憑證。該模組必須實作 [`caddytls.OnDemandPermission` 介面](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission)。包含一個 `http` 權限模組，這就是 `ask` 選項所使用的模組，並且作為向後相容的快捷方式保留。

- ⚠️ **interval** 和 **burst** 速率限制選項曾可用，但 **不建議** 使用。如果您仍有這些選項，請將其從設定中移除。

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


<a id="key-type"></a>
##### `key_type`
指定為 TLS 憑證生成的金鑰類型；僅當您有自訂它的特定需求時才更改此項。

可能的值為：`ed25519`、`p256`、`p384`、`rsa2048`、`rsa4096`。

```caddy
{
	key_type ed25519
}
```


<a id="cert-issuer"></a>
##### `cert_issuer`
定義 TLS 憑證的發行者（或來源）。

這允許全域設定發行者，而不是像使用 [`tls` 指令的 `issuer` 子指令](/docs/caddyfile/directives/tls#issuer) 那樣按站點進行設定。

如果您希望設定多個發行者進行嘗試，可以重複此操作。它們將按定義順序進行嘗試。

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


<a id="renew-interval"></a>
##### `renew_interval`
掃描所有已載入、受管理的憑證以查找過期情況並在過期時觸發續訂的頻率。

預設值：`10m`

```caddy
{
	renew_interval 30m
}
```


<a id="cert-lifetime"></a>
##### `cert_lifetime`
要求 CA 簽發憑證的有效期。

此值用於計算 ACME 訂單的 `notAfter` 欄位；因此系統必須具有合理同步的時鐘。注意：並非所有 CA 都支援此功能。請查看您的 CA 的 ACME 文件，以了解是否允許此操作以及可以使用哪些值。

預設值：`0`（CA 選擇有效期，通常為 90 天）

⚠️ 這是一個實驗性功能。可能會發生更改或移除。

```caddy
{
	cert_lifetime 30d
}
```


<a id="ocsp-interval"></a>
##### `ocsp_interval`
檢查 [OCSP stapling <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OCSP_stapling) 是否需要更新的頻率。

預設值：`1h`

```caddy
{
	ocsp_interval 2h
}
```


<a id="ocsp-stapling"></a>
##### `ocsp_stapling`
可以設定為 `off` 以停用 OCSP stapling。在由於防火牆而無法存取回應器的環境中非常有用。

```caddy
{
	ocsp_stapling off
}
```

<a id="renewal-window-ratio"></a>
##### `renewal_window_ratio`
在 Caddy 嘗試續訂憑證之前必須剩餘的憑證有效期的比例（介於 0 和 1 之間）。例如，如果憑證的有效期為 90 天，且此比例為 `0.3333`（預設值），則當憑證剩餘 30 天或更短時間到期時，Caddy 將持續嘗試續訂憑證。也可以使用 [`tls` 指令的 `renewal_window_ratio` 子指令](/docs/caddyfile/directives/tls#renewal_window_ratio) 按站點進行設定。

您極少需要更改此項，但如果您的 CA 簽發時間非常長，則在憑證有效期的後期進行續訂傾斜可能會很有用。

請記住，這只是一個建議，因為 ACME 發行者可能會實作 [ARI 擴充功能 (ARI extension)](https://datatracker.ietf.org/doc/rfc9773/) ，該擴充功能讓發行者指示 ACME 客戶端（在本例中為 Caddy）應嘗試續訂的時間視窗，且該視窗可能與此比例不一致。

```caddy
{
	renewal_window_ratio 0.1
}
```


<a id="preferred-chains"></a>
##### `preferred_chains`
如果您的 CA 提供多個憑證鏈，您可以使用此選項指定 Caddy 應偏好哪個鏈。設定以下選項之一：

- **smallest** 將告訴 Caddy 偏好位元組數最少的鏈。

- **root_common_name** 是一個或多個通用名稱 (common names) 的列表；Caddy 將選擇第一個具有與至少一個指定通用名稱相匹配的根的鏈。

- **any_common_name** 是一個或多個通用名稱 (common names) 的列表；Caddy 將選擇第一個具有與至少一個指定通用名稱相匹配的發行者的鏈。

請注意，如果沒有任何 [覆蓋發行者層級設定](/docs/caddyfile/directives/tls#acme) ，將 `preferred_chains` 指定為全域選項將影響所有發行者。

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```


<a id="server-options"></a>
## 伺服器選項 (Server Options)

使用可能跨越多個站點的設定來自訂 [HTTP 伺服器](/docs/json/apps/http/servers/) ，因此無法在站點區塊中正確設定。這些選項會影響接聽程式/通訊端或 HTTP 層之下的其他設施。

可以使用不同的 `listener_address` 值多次指定，以為每個伺服器設定不同的選項。例如，`servers :443` 將僅適用於綁定到接聽程式位址 `:443` 的伺服器。省略接聽程式位址將把選項應用於任何剩餘的伺服器。

<aside class="tip">

使用 [`caddy adapt`](/docs/command-line#caddy-adapt) 命令尋找 Caddyfile 中伺服器的接聽位址。

</aside>


例如，要為連接埠 `:80` 和 `:443` 上的伺服器設定不同的選項，您可以指定兩個 `servers` 區塊：

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

當使用 `servers` 時，它將 **僅** 適用於 **實際出現在** 您 Caddyfile 中的伺服器（即由站點區塊生成的伺服器）。請記住， [自動 HTTPS (Automatic HTTPS)](/docs/automatic-https) 將建立一個監聽連接埠 `80`（或 [`http_port` 選項](#http_port)）的伺服器，以提供 HTTP->HTTPS 重新導向並解決 ACME HTTP 驗證；這發生在執行時，即在 Caddyfile 轉接器應用 `servers` *之後* 。換句話說，這意味著 `servers` **將不** 應用於 `:80`，除非您顯式聲明一個站點區塊，例如 `http://` 或 `:80`。


<aside class="tip">

如果您使用的是 [`bind` 指令](/docs/caddyfile/directives/bind) 或 [`default_bind` 全域選項](/docs/caddyfile/options#default_bind) ，則 `listener_address` *必須* 與綁定位址結合站點區塊的連接埠相匹配，否則將不應用設定。例如：

```caddy
{
	# 這將不會匹配伺服器，缺少綁定位址
	servers :8080 {
		name private
	}

	# 這將起作用，因為它是精確匹配
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



<a id="name"></a>
##### `name`

要分配給此伺服器的自訂名稱。通常有助於在日誌和指標中按其名稱識別伺服器。如果未設定，Caddy 將使用 `srvX` 模式動態定義它，其中 `X` 從 `0` 開始並根據設定中的伺服器數量遞增。

請記住，僅您的設定中由站點區塊產生的伺服器才會應用設定。 [自動 HTTPS (Automatic HTTPS)](/docs/automatic-https) 在執行時建立 `:80` 伺服器（或 [`http_port`](#http_port)），因此如果您想重命名它，您至少需要一個空的 `http://` 站點區塊。

例如：

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```

</aside>



<a id="listener-wrappers"></a>
##### `listener_wrappers`

允許設定 [接聽程式包裝器 (listener wrappers)](/docs/json/apps/http/servers/listener_wrappers/) ，它可以修改通訊端接聽程式的行為。它們按給定的順序應用。

<a id="tls"></a>
###### `tls`

`tls` 接聽程式包裝器是一個空操作接聽程式包裝器，用於標記 TLS 接聽程式應在接聽程式包裝器鏈中的位置。僅當另一個接聽程式包裝器必須放在 TLS 握手之前時才應使用它。

<a id="http-redirect"></a>
###### `http_redirect`

[`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/) 為以 HTTP 請求形式進入 TLS 連接埠的連接提供 HTTP->HTTPS 重新導向，透過使用前幾個位元組檢測它不是 TLS 握手而是 HTTP 請求。這在非標準連接埠（非 `443`）上提供 HTTPS 服務時最有用，因為除非指定了 schema，否則瀏覽器會嘗試 HTTP。它必須放在 `tls` 接聽程式包裝器 *before* 。這是一個範例：

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

<a id="proxy-protocol"></a>
###### `proxy_protocol`

[`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/) 接聽程式包裝器（在 v2.7.0 之前僅透過外掛可用）啟用了 [PROXY 通訊協定 (PROXY protocol)](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) 解析（由 HAProxy 普及）。這必須在 `tls` 接聽程式包裝器 *before* 使用，因為它在連接開始時解析純文字數據：

請注意，在評估 matcher 或 [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) 之前，來自 PROXY 通訊協定的元數據可能會應用於連接。直接對等體的 IP 位址將丟失以供進一步評估。

```caddy-d
proxy_protocol {
	timeout <duration>
	allow <cidrs...>
	deny <cidrs...>
	fallback_policy <policy>
}
```

- **timeout** 指定等待 PROXY 標頭的最大持續時間。預設為 `5s`。

- **allow** 是受信任來源接收 PROXY 標頭的 CIDR 範圍列表。Unix socket 預設是受信任的，不屬於此選項的一部分。

- **deny** 是要拒絕來自其的 PROXY 標頭的受信任來源的 CIDR 範圍列表。

- **fallback_policy** 是如果 PROXY 標頭來自不在允許/拒絕列表中位址時要採取的行動。預設回退策略為 `ignore`。`fallback_policy` 的公認值為：
	- `ignore`：來自 PROXY 標頭的位址，但接受連接
	- `use`：使用來自 PROXY 標頭的位址
	- `reject`：發送 PROXY 標頭時拒絕連接
	- `require`：連接必須發送 PROXY 標頭，如果不存在則拒絕
	- `skip`：接受不要求 PROXY 標頭的連接。


例如，對於一個 HTTPS 伺服器（需要 `tls` 接聽程式包裝器），它接受來自特定 IP 位址範圍的 PROXY 標頭，並拒絕來自不同範圍的 PROXY 標頭，超時時間為 2 秒：

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


<a id="timeouts"></a>
##### `timeouts`

- **read_body** 是一個 [持續時間值](/docs/conventions#durations) ，設定允許從客戶端上傳讀取多長時間。將此設定為一個較短的非零值可以減輕 slowloris 攻擊，但也可能影響合法的慢速客戶端。預設無超時。

- **read_header** 是一個 [持續時間值](/docs/conventions#durations) ，設定允許從客戶端請求標頭讀取多長時間。預設無超時。

- **write** 是一個 [持續時間值](/docs/conventions#durations) ，設定允許向客戶端寫入多長時間。請注意，在提供大型檔案時將此設定為較小的值可能會對合法的慢速客戶端產生負面影響。預設無超時。

- **idle** 是一個 [持續時間值](/docs/conventions#durations) ，設定啟用了 keep-alives 時等待下一個請求的最大時間。預設為 5 分鐘，以幫助避免資源耗盡。

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


<a id="keepalive-interval"></a>
##### `keepalive_interval`
在沒有傳輸其他數據時，在 TCP 層發送 TCP keepalive 封包以保持連接活動的間隔。預設為 `15s`。

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


<a id="keepalive-idle"></a>
##### `keepalive_idle`
在沒有傳輸其他數據時，在發送 TCP keepalive 封包之前連接必須處於空閒狀態的持續時間。預設為 `15s`。

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


<a id="keepalive-count"></a>
##### `keepalive_count`
在認為連接已死之前要發送的 TCP keepalive 封包的最大數量。預設為 `9`。

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


<a id="0rtt"></a>
##### `0rtt`

預設情況下，QUIC 接聽程式（即 HTTP/3）啟用了 0-RTT（早期數據），以允許客戶端在 TLS 握手的第一次往返中發送數據，這可以提高重複連接的效能。

您可以將此設定為 `off` 以停用 QUIC 接聽程式的 0-RTT。停用 0-RTT 的一個原因是如果使用了 [`remote_ip` 匹配器 (matcher)](/docs/caddyfile/matchers#remote-ip) ，如果路由發生在 TLS 握手完成之前，則會引入對被驗證的遠端位址的依賴。在這種情況下，會寫入一個 HTTP 425 回應，但某些客戶端（瀏覽器）可能會表現異常且不執行重試，因此停用 0-RTT 可以確保使用者看不到 425 回應，代價是失去 0-RTT 的效能優勢。

```caddy
{
	servers {
		0rtt off
	}
}
```


<a id="trusted-proxies"></a>
##### `trusted_proxies`

允許設定應信任其請求的代理伺服器的 IP 範圍 (CIDRs)。預設情況下，不信任任何代理。

啟用此功能會導致受信任的請求從 HTTP 標頭中解析 *real* 客戶端 IP（預設為 `X-Forwarded-For`；請參閱 [`client_ip_headers`](#client-ip-headers) 以設定其他標頭）。如果受信任，客戶端 IP 將添加到 [存取日誌](/docs/caddyfile/directives/log) 中，可作為 `{client_ip}` [placeholder](/docs/caddyfile/concepts#placeholders) 使用，並允許使用 [`client_ip` 匹配器 (matcher)](/docs/caddyfile/matchers#client-ip)。如果請求不是來自受信任的代理，則客戶端 IP 將設定為直接傳入連接的遠端 IP 位址，或如果使用了 [PROXY 通訊協定 (PROXY protocol)](/docs/caddyfile/options#proxy-protocol) ，則設定為其設定的位址。預設情況下，標頭中的 IP 是從左到右解析的。請參閱 [`trusted_proxies_strict`](#trusted-proxies-strict) 以更改此行為。

一些匹配器 (matcher) 或 handler 可能會使用請求的信任狀態來做出決定。例如，如果受信任，[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#defaults) handler 將代理並擴充敏感的 `X-Forwarded-*` 請求標頭。

目前，Caddy 的標準發行版中僅包含 `static` [IP 來源模組](/docs/json/apps/http/servers/trusted_proxies/) ，但可以使用外掛進行 [擴充](/docs/extending-caddy) 以維護 IP 範圍的動態列表。


<a id="static"></a>
###### `static`

獲取要信任的靜態（不變的）IP 範圍 (CIDRs) 列表。

作為快捷方式，`private_ranges` 可用於匹配所有私有 IPv4 和 IPv6 範圍。這與指定所有這些範圍相同：`192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`。

語法如下：

```caddy-d
trusted_proxies static [private_ranges] <ranges...>
```

這是一個完整的範例，信任範例 IPv4 範圍和 IPv6 範圍：

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

<a id="trusted-proxies-strict"></a>
##### `trusted_proxies_strict`

啟用 [`trusted_proxies`](#trusted-proxies) 後，標頭（由 [`client_ip_headers`](#client-ip-headers) 設定）中的 IP 預設從左到右解析。找到的第一個不受信任的 IP 位址將成為真實的客戶端位址。從 v2.8 開始，您可以使用 `trusted_proxies_strict` 選擇對這些標頭進行從右到左的解析。預設情況下，為了向後相容，此選項是停用的。

上述代理（如 HAProxy、CloudFlare、AWS ALB、CloudFront 等）會將每個新的連接遠端位址附加到 `X-Forwarded-For` 的右側。建議在使用這些代理時啟用 `trusted_proxies_strict` ，因為最左側的 IP 位址可能被客戶端偽造。

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">

特別是在 AWS ALB 的情況下，您肯定會想要啟用此選項。 [根據其文件](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15) ，您只能透過將 XFF 模式設定為 `append` 來識別真正的客戶端 IP。此 IP 將被附加到 `X-Forwarded-For` 的右側，並且只能透過 `trusted_proxies_strict` 安全地提取。

</aside>

<a id="trusted-proxies-unix"></a>
##### `trusted_proxies_unix`

`trusted_proxies_unix` 選項允許信任來自 Unix socket 的所有連接，這在 Caddy 位於透過 Unix socket 連接到它的反向代理（可能是另一個 Caddy 實例）之後時非常有用（即 [`bind` 指令](/docs/caddyfile/directives/bind) 設定為 unix socket）。此功能預設停用。

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

<a id="client-ip-headers"></a>
##### `client_ip_headers`

與 [`trusted_proxies`](#trusted-proxies) 配合使用，允許設定使用哪些標頭來確定客戶端的 IP 位址。預設情況下，僅考慮 `X-Forwarded-For`。可以指定多個標頭欄位，在這種情況下，使用第一個非空標頭值。

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


<a id="metrics"></a>
##### `metrics`

啟用指標收集；在抓取指標或使用 OTLP 推送指標之前是必要的。請注意，指標會降低非常繁忙的伺服器上的效能。（我們的社群正在努力改進這一點。請參與進來！）

```caddy
{
	metrics
}
```

您可以添加 `per_host` 選項以使用指標的主機名稱標記指標。

```caddy
{
	metrics {
		per_host
	}
}
```

由於觀察客戶端可能發送的所有可能主機具有無限基數的潛力，Caddy 僅記錄已設定主機的指標，而所有其他主機（例如 attacker.com）則彙總在 "_other" 標籤下。要強制觀察所有主機，且潛在的無限基數是可接受的風險，您可以添加 `observe_catchall_hosts`。請注意，添加 `observe_catchall_hosts` 不會啟用 `per_host`。然而，對於 HTTPS 伺服器（因為憑證提供了一些防止無限基數的保護），這會自動啟用，但對於 HTTP 伺服器，預設情況下停用，以防止來自任意 Host 標頭的基數攻擊。

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

您可以添加 `otlp` 選項將相同的指標推送到 OpenTelemetry 通訊協定 (OTLP) 端點。匯出器由標準的 OpenTelemetry `OTEL_*` 環境變數設定，例如 `OTEL_EXPORTER_OTLP_ENDPOINT`、`OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`、`OTEL_EXPORTER_OTLP_PROTOCOL`、`OTEL_EXPORTER_OTLP_HEADERS`、`OTEL_METRIC_EXPORT_INTERVAL` 和 `OTEL_METRICS_EXPORTER`。

```caddy
{
	metrics {
		otlp
	}
}
```

例如：

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

有關更多詳細資訊，請參閱 [使用指標監控 Caddy](/docs/metrics)。

<a id="trace"></a>
##### `trace`

記錄呼叫的每個單個 handler 。要求日誌以 `DEBUG` 層級發出（ 您可以使用 [`debug` 全域選項](#debug) 執行此操作）。

注意：這可能會記錄您的 HTTP handler 模組的設定；當設定中有敏感數據時，請勿在不安全的上下文中啟用此功能。

⚠️ 這是一個實驗性功能。可能會發生更改或移除。

```caddy
{
	servers {
		trace
	}
}
```


<a id="max-header-size"></a>
##### `max_header_size`

從客戶端 HTTP 請求標頭中解析的最大大小。如果超過限制，伺服器將以 HTTP 狀態 `431 Request Header Fields Too Large` 進行回應。它接受 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支援的所有格式。預設情況下，限制為 `1MB`。

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


<a id="enable-full-duplex"></a>
##### `enable_full_duplex`

為 HTTP/1 請求啟用全雙工通訊。

對於 HTTP/1 請求，Go HTTP 伺服器預設在開始寫入回應之前消耗請求體中任何未讀取的部分，防止 handler 同時從請求中讀取並寫入回應。啟用此選項會停用此行為，並允許 handler 在同時寫入回應的同時繼續從請求中讀取。

對於 HTTP/2+ 請求，Go HTTP 伺服器始終允許並發讀取和回應，因此此選項無效。

請對您的 HTTP 客戶端進行徹底測試，因為一些較舊的客戶端可能不支援全雙工 HTTP/1，這可能導致它們死結。有關更多資訊，請參閱 [golang/go#57786](https://github.com/golang/go/issues/57786)。

⚠️ 這是一個實驗性功能。可能會發生更改或移除。

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


<a id="log-credentials"></a>
##### `log_credentials`

預設情況下，具有可能包含敏感資訊的標頭（`Cookie`、`Set-Cookie`、`Authorization` 和 `Proxy-Authorization`）的存取日誌（使用 [`log` 指令](/docs/caddyfile/directives/log) 啟用）將被記錄為 `REDACTED`。

如果您希望 *不* 脫敏這些標頭，則可以啟用 `log_credentials` 選項。

```caddy
{
	servers {
		log_credentials
	}
}
```



<a id="protocols"></a>
##### `protocols`

要支援的以空格分隔的 HTTP 通訊協定列表。

預設值：`h1 h2 h3`

公認的值為：
- `h1` 代表 HTTP/1.1
- `h2` 代表 HTTP/2
- `h2c` 代表明文 HTTP/2
- `h3` 代表 HTTP/3

目前，啟用 HTTP/2（包括 H2C）必然意味著啟用 HTTP/1.1，因為 Go 標準庫在使用其 HTTP 伺服器時不允許我們停用 HTTP/1.1。但是，HTTP/1.1 或 HTTP/3 都可以獨立啟用。

請注意，H2C（"明文 HTTP/2" 或 "TCP 上的 H2"）和 HTTP/3 並非由 Go 標準庫實作，因此某些功能或特性可能受限。除非您的應用程式絕對必要，否則我們不建議啟用 H2C。

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



<a id="strict-sni-host"></a>
##### `strict_sni_host`

啟用此項要求請求的 `Host` 標頭與客戶端 TLS ClientHello 發送的 `ServerName` 值相匹配，這是使用 TLS 客戶端身份驗證時的必要保護措施。如果不匹配，則向客戶端寫入 HTTP 狀態 `421 Misdirected Request` 回應。

如果設定了 [客戶端身份驗證](/docs/caddyfile/directives/tls#client_auth) ，則此選項將自動開啟。這禁止了 TLS 客戶端身份驗證繞過（域名強置，domain fronting），否則可以透過在 TLS 握手期間發送不受保護的 SNI 值，然後在建立連接後將受保護的域名放在 Host 標頭中來利用這一點。此行為是一個安全的預設值，但您可以使用 `insecure_off` 顯式將其關閉；例如，在運行反向代理且需要域名強置且不根據主機名稱限制存取的情況下。

```caddy
{
	servers {
		strict_sni_host on
	}
}
```



<a id="file-systems"></a>
## 檔案系統 (File Systems)

`filesystem` 全域選項允許聲明一個或多個可用於檔案 I/O 的檔案系統。

這可以讓您連接到在雲端運行的遠端檔案系統，或具有類檔案介面的資料庫，甚至讀取嵌入在 Caddy 二進位檔案中的檔案。

檔案系統使用名稱聲明以識別它們。這意味著如果需要，您可以連接到多個相同類型的檔案系統。

預設情況下，Caddy 沒有任何檔案系統模組，因此您需要使用適用於您要使用的檔案系統的外掛構建 Caddy。

<a id="example"></a>
#### 範例 (Example)

使用虛構的 `custom` 檔案系統模組，您可以聲明兩個檔案系統：

```caddy
{
	filesystem foo custom {
		...
	}

	filesystem bar custom {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```



<a id="pki-options"></a>
## PKI 選項 (PKI Options)

PKI (Public Key Infrastructure) app 是 Caddy 的 [本地 HTTPS (Local HTTPS)](/docs/automatic-https#local-https) 和 [ACME 伺服器](/docs/caddyfile/directives/acme_server) 功能的基礎。此 app 定義了能夠簽署憑證的憑證頒發機構 (CAs)。

預設的 CA ID 是 `local`。如果在設定 `ca` 時省略了 ID，則假定為 `local`。

<a id="name-1"></a>
##### `name`
憑證頒發機構的使用者導向名稱。

預設值：`Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "My Local CA"
		}
	}
}
```

<a id="root-cn"></a>
##### `root_cn`
放在根憑證的 CommonName 欄位中的名稱。

預設值：`{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "My Local CA - 2024 ECC Root"
		}
	}
}
```

<a id="intermediate-cn"></a>
##### `intermediate_cn`
放在中間憑證的 CommonName 欄位中的名稱。

預設值：`{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "My Local CA - ECC Intermediate"
		}
	}
}
```

<a id="intermediate-lifetime"></a>
##### `intermediate_lifetime`
中間憑證有效的 [持續時間](/docs/conventions#durations)。此值 **必須** 小於根憑證的有效期（`3600d` 或 10 年）。

預設值：`7d`。除非絕對必要，否則 *不建議* 更改此項。

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

<a id="maintenance-interval"></a>
##### `maintenance_interval`
檢查中間憑證（以及根憑證，如果適用）是否需要續訂的頻率 [持續時間](/docs/conventions#durations)。

預設值：`10m`。除非絕對必要，否則 *不建議* 更改此項。

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

<a id="renewal-window-ratio-1"></a>
##### `renewal_window_ratio`
在 Caddy 嘗試續訂憑證之前必須剩餘的憑證有效期的比例（介於 0 和 1 之間）。例如，如果憑證的有效期為 1 年，且此比例為 `0.2`（預設值），則當憑證剩餘 73 天或更短時間到期時，Caddy 將持續嘗試續訂憑證。

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


<a id="root"></a>
##### `root`
用作 CA 根的金鑰對（憑證和私密金鑰）。如果未指定，將自動生成並管理一個。

- **format** 是提供憑證和私密金鑰的格式。目前僅支援 `pem_file`，這是預設值，因此此欄位是可選的。
- **cert** 是憑證。使用 `pem_file` 格式時，這應該是 PEM 檔案的路徑。
- **key** 是私密金鑰。使用 `pem_file` 格式時，這應該是 PEM 檔案的路徑。

<a id="intermediate"></a>
##### `intermediate`
用作 CA 中間體的金鑰對（憑證和私密金鑰）。如果未指定，將自動生成並管理一個。

- **format** 是提供憑證和私密金鑰的格式。目前僅支援 `pem_file`，這是預設值，因此此欄位是可選的。
- **cert** 是憑證。使用 `pem_file` 格式時，這應該是 PEM 檔案的路徑。
- **key** 是私密金鑰。使用 `pem_file` 格式時，這應該是 PEM 檔案的路徑。

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /path/to/root.pem
				key /path/to/root.key
			}
			intermediate {
				format pem_file
				cert /path/to/intermediate.pem
				key /path/to/intermediate.key
			}
		}
	}
}
```


<a id="event-options"></a>
## 事件選項 (Event Options)

Caddy 模組在發生（或即將發生）有趣的事情時發出事件。

事件通常包含元數據負載。了解事件及其負載的最佳方法是查閱每個模組的文件，但您也可以透過啟用 [`debug` 全域選項](#debug) 並讀取日誌來查看事件及其數據負載。

<a id="on"></a>
##### `on`

將事件 handler 綁定到具名事件。指定事件 handler 模組的名稱，後跟其設定。

例如，在獲取憑證後運行命令（需要 [第三方外掛 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/mholt/caddy-events-exec)），使用 placeholder 將事件負載的一部分傳遞給腳本：

```caddy
{
	events {
		on cert_obtained exec ./my-script.sh {event.data.certificate_path}
	}
}
```

<a id="events"></a>
### 事件 (Events)

這些標準事件由 Caddy 發出：

- [`tls` 事件 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/certmagic#events)
- [`reverse_proxy` 事件](/docs/caddyfile/directives/reverse_proxy#events)

外掛也可能發出事件，因此請查看其文件以獲取詳細資訊。
