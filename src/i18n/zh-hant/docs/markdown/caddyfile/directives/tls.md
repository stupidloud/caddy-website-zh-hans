---
title: tls (Caddyfile 指令)
---

<script>
ready(function() {
	// 如果在頁面中找到匹配的錨標記，我們將添加指向所有子指令的連結。
	addLinksToSubdirectives();
});
</script>

<a id="tls"></a>
# tls

為站點配置 TLS。

**Caddy 的默認 TLS 設置是安全的。只有在你有充分理由並了解其影響的情況下才更改這些設置。** 該指令最常見的用法是指定 ACME 帳戶電子郵件地址、更改 ACME CA 端點或提供你自己的證書。

相容性說明：由於其作為安全協議的敏感性，可能會在新的次要版本或補丁版本中對 TLS 默認值進行蓄意調整。舊的或損壞的 TLS 版本、密碼、功能等可能隨時被移除。如果你的部署對更改極其敏感，你應該明確指定那些必須保持不變的值，並對升級保持警惕。在幾乎所有情況下，我們都建議轉用默認設置。


<a id="syntax"></a>
## 語法

```caddy-d
tls [internal|force_automate|<email>] | [<cert_file> <key_file>] {
	protocols <min> [<max>]
	ciphers   <cipher_suites...>
	curves    <groups...>
	alpn      <values...>
	load      <paths...>
	ca        <ca_dir_url>
	ca_root   <pem_file>
	key_type  ed25519|p256|p384|rsa2048|rsa4096
	dns       <provider_name> [<params...>]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	eab       <key_id> <mac_key>
	on_demand
	reuse_private_keys
	client_auth {
		mode                   [request|require|verify_if_given|require_and_verify]
		trust_pool             <module>
		verifier 			   <module>
	}
	issuer          <issuer_name>  [<params...>]
	get_certificate <manager_name> [<params...>]
	insecure_secrets_log <log_file>
	renewal_window_ratio <ratio>
	force_automate
}
```

- **internal** 表示使用 Caddy 內部的、本地信任的 CA 為此站點生成證書。要進一步配置 [`internal`](#internal) 發行者，請使用 [`issuer`](#issuer) 子指令。

- **force_automate** 強制 Caddy 為站點自動化證書，即使有其他託管證書適用。

- **&lt;email&gt;** 是用於管理站點證書的 ACME 帳戶的電子郵件地址。你可能更願意使用 [`email` 全域選項](/docs/caddyfile/options#email) 來一次性為所有站點配置此項。

<aside class="tip">

請記住，Let's Encrypt 可能會向你發送有關證書即將過期的電子郵件，但這可能具有誤導性，因為 Caddy 在續訂時可能已選擇使用不同的發行者（例如 ZeroSSL）。請檢查你的日誌和/或證書本身（例如在瀏覽器中）以查看使用了哪個發行者，以及其到期日期是否仍然有效；如果是，你可以放心地忽略來自 Let's Encrypt 的電子郵件。

</aside>

- **&lt;cert_file&gt;** 和 **&lt;key_file&gt;** 是證書和私鑰 PEM 文件的路徑。僅指定其中之一是無效的。

- **protocols** <span id="protocols"/> 指定最小和最大協議版本。除非你知道自己在做什麼，否則 *不要* 更改這些設置。通常不需要配置此項，因為 Caddy 將始終使用現代默認值。
  
  默認最小值：`tls1.2`，默認最大值：`tls1.3`

- **ciphers** <span id="ciphers"/> 按降序優先順序指定密碼套件名稱列表。除非你知道自己在做什麼，否則 *不要* 更改這些設置。請注意，TLS 1.3 的密碼套件是不可自定義的；並且並非所有 TLS 1.2 密碼都默認啟用。支持的名稱（按 Go 標準庫的優先順序排序）為：
	- `TLS_AES_128_GCM_SHA256`
	- `TLS_CHACHA20_POLY1305_SHA256`
	- `TLS_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA`

- **curves** <span id="curves"/> 指定要支持的 EC 組列表。建議不要更改默認值。支持的值為：
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> 是要在 TLS 握手的 [ALPN 擴展 <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Glossary/ALPN) 中宣佈的值列表。

- **load** <span id="load"/> 指定要從中加載作為證書+私鑰捆綁包的 PEM 文件的文件夾列表。

- **ca** <span id="ca"/> 更改 ACME CA 端點。這最常用於在測試時設置 [Let's Encrypt 的測試 (staging) 端點 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) 或內部 ACME 服務器。（要為整個 Caddyfile 更改此值，請改用 `acme_ca` [全域選項](/docs/caddyfile/options) 。）

- **ca_root** <span id="ca_root"/> 指定一個 PEM 文件，其中包含 ACME CA 端點的受信任根證書（如果不在系統信任庫中）。

- **key_type** <span id="key_type"/> 是生成 CSR 時要使用的密鑰類型。僅在你係特定要求時才設置此項。

- **dns** <span id="dns"/> 使用指定的提供者插件啟用 [DNS 驗證 (challenge)](/docs/automatic-https#dns-challenge) ，該插件必須從 [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) 存儲庫之一插入。每個提供者插件在名稱後可能有自己的語法；詳情請參閱其文檔。維護對每個 DNS 提供者的支持是社區的努力。 [在我們的 wiki 上了解如何為你的提供者啟用 DNS 驗證。](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> 是一個 [持續時間值](/docs/conventions#durations) ，設置在使用 DNS 驗證時等待 DNS TXT 記錄出現的最長時間。設置為 `-1` 可禁用傳播檢查。默認 2 分鐘。

- **propagation_delay** <span id="propagation_delay"/> 是一個 [持續時間值](/docs/conventions#durations) ，設置在使用 DNS 驗證時開始 DNS TXT 記錄傳播檢查之前等待多長時間。默認 `0` （不等待）。

- **dns_ttl** <span id="dns_ttl"/> 是一個 [持續時間值](/docs/conventions#durations) ，設置用於 DNS 驗證的 `TXT` 記錄的 TTL。極少需要。

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> 覆蓋用於 DNS 驗證的網域。這是為了將驗證委託給不同的網域。

  如果你的主網域的 DNS 提供者沒有可用的 [DNS 插件 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) ，你可能想要使用此項。你可以改為在主網域中添加一個帶有子網域 `_acme-challenge` 的 `CNAME` 記錄，指向你 *確實* 擁有插件的次要網域。此選項 *不需要* 插件的特殊支持。
  
  當 ACME 發行者嘗試解決主網域的 DNS 驗證時，他們隨後將跟隨 `CNAME` 到你的次要網域以查找 `TXT` 記錄。

  **注意：** 此處請使用 CNAME 記錄中的完整規範名稱 - `_acme-challenge` 子網域不會自動附加在前面。

- **resolvers** <span id="resolvers"/> 自定義執行 DNS 驗證時使用的 DNS 解析器；這些優先於系統解析器或任何默認解析器。如果在此處設置，解析器將傳播到所有配置的證書發行者。

  這通常是一個 IP 地址列表。例如，要使用 [Google 公共 DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns) ：

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> 使用 CA 提供的密鑰 ID 和 MAC 密鑰為此站點配置 ACME 外部帳戶綁定 (EAB)。

- **on_demand** <span id="on_demand"/> 為站點塊位址中給出的主機名啟用 [隨需 TLS (On-Demand TLS)](/docs/automatic-https#on-demand-tls) 。 **安全警告：** 在生產環境中這樣做是不安全的，除非你也配置了 [`on_demand_tls` 全域選項](/docs/caddyfile/options#on-demand-tls) 來減輕濫用。

- **reuse_private_keys** <span id="reuse_private_keys"/> 在續訂證書時啟用私鑰重用。默認情況下，會為每個新證書創建一個新密鑰，以減輕釘選 (pinning) 風險並縮小密鑰洩露的影響。密鑰釘選違反行業最佳實踐。除非你有特定原因，否則不建議使用此選項；這可能會在未來版本中移除。

- **client_auth** <span id="client_auth"/> 啟用並配置 TLS 客戶端身份驗證：
  - **mode** <span id="mode"/> 是身份驗證客戶端的模式。允許的值為：

    | 模式 | 描述 |
    | --- | --- |
    | request | 向客戶端請求證書，但即使沒有證書也允許；不進行驗證 |
    | require | 要求客戶端出示證書，但不進行驗證 |
    | verify_if_given | 向客戶端請求證書；即使沒有證書也允許，但如果有證書則進行驗證 |
    | require_and_verify | 要求客戶端出示有效的證書並進行驗證 |

    默認值：如果提供了 `trust_pool` 模塊，則為 `require_and_verify` ；否則為 `require` 。
	
  - **trust_pool** <span id="trust_pool"/> 配置證書頒發機構 (CA) 的來源，提供用於驗證客戶端證書的證書。
	
	用於提供受信任證書池的證書頒發機構以及該細分內的配置取決於配置的信任池模塊來源。 Caddy 中可用的標準模塊 [列在下方](#trust-pool-providers) 。完整模塊列表（包括第三方模塊）列在 [`trust_pool` JSON 文檔](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool) 中。

    可以使用多個 `trusted_*` 指令來指定多個 CA 或分葉 (leaf) 證書。未列為分葉證書之一或未由任何指定 CA 簽名的客戶端證書將根據 **mode** 被拒絕。

  - **verifier** <span id="verifier"/> 啟用自定義客戶端證書驗證器模塊。這些可以執行自定義客戶端身份驗證檢查，例如確保證書未被撤銷。

- **issuer** <span id="issuer"/> 配置自定義證書發行者或獲取證書的來源。

  使用哪個發行者以及此細分中隨後的選項取決於可用的 [發行者模塊](#issuers) 。其他一些子指令（如 `ca` 和 `dns`）實際上是配置 `acme` 發行者的快捷方式（此子指令是後來添加的），因此同時指定此指令和其他一些指令會引起混淆，因此是被禁止的。
  
  可以多次指定此子指令以配置多個冗餘發行者；如果一個發行者未能簽發證書，將嘗試下一個。

- **get_certificate** <span id="get_certificate"/> 允許在握手時從 [管理員模塊](#certificate-managers) 獲取證書。

- **insecure_secrets_log** <span id="insecure_secrets_log"/> 啟用將 TLS 密鑰記錄到文件中。這也稱為 `SSLKEYLOGFILE` 。使用 NSS 密鑰日誌格式，隨後可由 Wireshark 或其他工具解析。 ⚠️ **安全警告：** 這是不安全的，因為它允許其他程序或工具解密 TLS 連接，因此會完全損害安全性。然而，此功能對於調試和排障很有用。

- **renewal_window_ratio** <span id="renewal_window_ratio"/> 是 0 到 1 之間的比率，決定了在 Caddy 嘗試續訂證書之前必須剩餘的證書壽命。例如，如果證書的壽命為 90 天，且此比率為 `0.3333` （默認值），那麼當證書剩餘壽命不超過 30 天時，Caddy 將不斷嘗試續訂證書。也可以通過 [`renewal_window_ratio` 全域選項](/docs/caddyfile/options#renewal_window_ratio) 進行全域設置。

  你極少需要更改此項，但如果你的 CA 簽發時間非常長，在證書壽命後期續訂可能會很有用。

  請記住，這只是一個建議，因為 ACME 發行者可能會實現 [ARI 擴展](https://datatracker.ietf.org/doc/rfc9773/) 。 ARI 規定了 ACME 客戶端（在本例中為 Caddy）應嘗試續訂的時間窗口，而該窗口可能與此比率不一致。

- **force_automate** 與內聯指定相同（見上文）。

<a id="trust-pool-providers"></a>
### 信任池提供者 (Trust Pool Providers)

以下是可在 `trust_pool` 子指令中使用的標準信任池提供者：

<a id="inline"></a>
#### inline

`inline` 模塊直接解析 Caddyfile 中列出的 Base64 DER 編碼格式的受信任根證書。 `trust_der` 指令可以重複多次。

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> 是用於驗證客戶端證書的 Base64 DER 編碼的 CA 證書。

<a id="file"></a>
#### file

`file` 模塊從磁碟上的 PEM 文件讀取受信任的根證書。 `pem_file` 指令可以在同一行接受多個文件路徑，並且可以重複多次。

```caddy-d
... file [<pem_file>...] {
	pem_file <pem_file>...
}
```

- **pem_file** <span id="pem_file"/> 是用於驗證客戶端證書的 PEM CA 證書文件的路徑。

<a id="pki_root"></a>
#### pki_root

`pki_root` 模塊從 [PKI 應用](/docs/caddyfile/options#pki-options) 中定義的證書頒發機構獲取 *根 (root)* 並信任該證書。 `authority` 指令可以同時接受多個頒發機構，並且可以重複多次。

```caddy-d
... pki_root [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> 是在 PKI 應用中配置的證書頒發機構的名稱。

<a id="pki_intermediate"></a>
#### pki_intermediate

`pki_intermediate` 模塊從 [PKI 應用](/docs/caddyfile/options#pki-options) 中定義的證書頒發機構獲取 *中間 (intermediate)* 並信任該證書。 `authority` 指令可以同時接受多個頒發機構，並且可以重複多次。

```caddy-d
... pki_intermediate [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> 是在 PKI 應用中配置的證書頒發機構的名稱。

<a id="storage"></a>
#### storage

`storage` 模塊從 Caddy [存儲 (storage)](/docs/caddyfile/options#storage) 中提取受信任的證書根。 `authority` 指令可以同時接受多個頒發機構，並且可以重複多次。

```caddy-d
... storage [<storage_keys>...] {
	storage <storage_module>
	keys    <storage_keys>...
}
```

- **storage** <span id="storage"/> 是要使用的可選存儲模塊。如果未指定，將使用默認存儲模塊。如果指定，則只能指定一次。

- **keys** <span id="keys"/> 是存儲 PEM 證書文件的存儲密鑰列表。該指令在同一行接受多個值，並且可以指定多次。

<a id="http"></a>
#### http

`http` 模塊從 HTTP 端點獲取受信任的證書。 `endpoints` 指令可以同時接受多個端點，並且可以重複多次。

```caddy-d
... http [<endpoints...>] {
	endpoints   <endpoints...>
	tls         <tls_config>
}
```

- **endpoints** <span id="endpoints"/> 是獲取證書的 HTTP 端點列表。該指令在同一行接受多個值，並且可以指定多次。

- **tls** <span id="tls"/> 是連接到 HTTP 端點時要使用的可選 TLS 配置。細分解析定義在 [下一節](#tls-1) 中。

<a id="tls-1"></a>
##### TLS

```caddy-d
... {
	ca                    <ca_module>
	insecure_skip_verify
	handshake_timeout     <duration>
	server_name           <name>
	renegotiation         <never|once|freely>
}
```

- **ca** <span id="ca"/> 是定義信任池提供者的可選指令。其配置遵循 [`trust_pool`](#trust_pool) 的相同行為。如果指定，則只能指定一次。

- **insecure_skip_verify** <span id="insecure_skip_verify"/> 關閉 TLS 握手驗證，使連接不安全且容易受到中間人攻擊。 *不要在生產環境中使用。* 驗證是針對系統信任的證書頒發機構或由 [`ca`](#ca) 指令確定的頒發機構進行的。

- **handshake_timeout** <span id="handshake_timeout"/> 是等待 TLS 握手完成的最大 [持續時間](/docs/conventions#durations) 。默認值：無超時。

- **server_name** <span id="server_name"/> 設置驗證在 TLS 握手中收到的證書時使用的服務器名稱。默認情況下，這將使用上游地址的主機部分。

- **renegotiation** <span id="renegotiation"/> 設置 TLS 重新協商級別。 TLS 重新協商是在第一次握手之後執行後續握手的行為。級別可以是以下之一：
  - `never` (默認值) 禁用重新協商。
  - `once` 允許遠程服務器在每次連接中請求一次重新協商。
  - `freely` 允許遠程服務器重複請求重新協商。

<a id="verifiers"></a>
### 驗證器 (Verifiers)

如果配置了 `trust_pool` ，客戶端證書驗證器模塊將在驗證其由受信任證書頒發機構簽發後執行。目前 Caddy 標準分發中附帶的一個驗證器是 `leaf` 。

<a id="leaf"></a>
#### Leaf

`leaf` 驗證器檢查客戶端證書是否為一組定義的允許證書之一。證書集使用 [加載器 (loader)](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders) 模塊加載。

<a id="loaders"></a>
##### 加載器 (Loaders)

標準 Caddy 分發捆綁了 4 個加載器，其中 3 個在 Caddyfile 中可用。

<a id="file-1"></a>
###### File

`file` 加載器從指定的 PEM 文件加載證書集。

```caddy-d
... file <pem_files...>
```

<a id="folder"></a>
###### Folder

`folder` 加載器遞歸遍歷命名的目錄，搜索要加載為接受的客戶端證書的 PEM 文件。

```caddy-d
... folder <folders...>
```

<a id="pem"></a>
###### PEM

`pem` 加載器接受直接在 Caddyfile 中以 PEM 格式內聯的證書。

```caddy-d
... pem <pem_strings...>
```

<a id="issuers"></a>
### 發行者 (Issuers)

這些發行者隨 `tls` 指令標準提供：

<a id="acme"></a>
#### acme

使用 ACME 協議獲取證書。請注意，`acme` 是默認發行者（使用 Let's Encrypt），因此通常不需要顯式配置它。

```caddy-d
... acme [<directory_url>] {
	dir      <directory_url>
	test_dir <test_directory_url>
	email    <email>
	timeout  <duration>
	disable_http_challenge
	disable_tlsalpn_challenge
	alt_http_port    <port>
	alt_tlsalpn_port <port>
	eab <key_id> <mac_key>
	trusted_roots <pem_files...>
	dns [<provider_name> [<options>]]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}
	profile <name>
}
```

- **dir** <span id="dir"/> 是 ACME CA 目錄的 URL。
  
  默認值：`https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> 是重試驗證時要使用的可選備用目錄；如果所有驗證均失敗，則在重試期間將使用此端點；如果 CA 有測試端點，且你希望避免在其生產端點上受到速率限制，則此項很有用。

  默認值：`https://acme-staging-v02.api.letsencrypt.org/directory`

- **email** <span id="email"/> 是 ACME 帳戶聯絡電子郵件地址。

- **timeout** <span id="timeout"/> 是一個 [持續時間值](/docs/conventions#durations) ，設置 ACME 操作超時前的等待時間。

- **disable_http_challenge** <span id="disable_http_challenge"/> 將禁用 HTTP 驗證。

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> 將禁用 TLS-ALPN 驗證。

- **alt_http_port** <span id="alt_http_port"/> 是服務 HTTP 驗證的備用端口；它必須發生在 80 端口，因此你必須將數據包轉發到此備用端口。

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> 是服務 TLS-ALPN 驗證的備用端口；它必須發生在 443 端口，因此你必須將數據包轉發到此備用端口。

- **eab** <span id="eab"/> 指定某些 ACME CA 可能要求的外部帳戶綁定。

- **trusted_roots** <span id="trusted_roots"/> 是連接到 ACME CA 服務器時信任的一個或多個根證書（作為 PEM 文件名）。

- **dns** <span id="dns"/> 配置 DNS 驗證。除非 [`dns` 全域選項](/docs/caddyfile/options#dns) 指定了全域適用的 DNS 提供者模塊，否則必須在此處配置提供者。

- **propagation_timeout** <span id="propagation_timeout"/> 是一個 [持續時間值](/docs/conventions#durations) ，設置在使用 DNS 驗證時等待 DNS TXT 記錄出現的最長時間。設置為 `-1` 可禁用傳播檢查。默認 2 分鐘。

- **propagation_delay** <span id="propagation_delay"/> 是一個 [持續時間值](/docs/conventions#durations) ，設置在使用 DNS 驗證時開始 DNS TXT 記錄傳播檢查之前等待多長時間。默認 0 （不等待）。

- **dns_ttl** <span id="dns_ttl"/> 是一個 [持續時間值](/docs/conventions#durations) ，設置用於 DNS 驗證的 `TXT` 記錄的 TTL。極少需要。

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> 覆蓋用於 DNS 驗證的網域。這是為了將驗證委託給不同的網域。

  如果你的主網域的 DNS 提供者沒有可用的 [DNS 插件 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) ，你可能想要使用此項。你可以改為在主網域中添加一個帶有子網域 `_acme-challenge` 的 `CNAME` 記錄，指向你 *確實* 擁有插件的次要網域。此選項 *不需要* 插件的特殊支持。
  
  當 ACME 發行者嘗試解決主網域的 DNS 驗證時，他們隨後將跟隨 `CNAME` 到你的次要網域以查找 `TXT` 記錄。

  **注意：** 此處請使用 CNAME 記錄中的完整規範名稱 - `_acme-challenge` 子網域不會自動附加在前面。

- **resolvers** <span id="resolvers"/> 自定義執行 DNS 驗證時使用的 DNS 解析器；這些優先於系統解析器或任何默認解析器。如果在此處設置，解析器將傳播到所有配置的證書發行者。

  這學常是一個 IP 地址列表。例如，要使用 [Google 公共 DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns) ：

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> 指定 Caddy 應首選哪些證書鏈；如果你的 CA 提供多個鏈，則很有用。使用以下選項之一：
	- **smallest** <span id="smallest"/> 將告訴 Caddy 首選字節數最少的鏈。

	- **root_common_name** <span id="root_common_name"/> 是一個或多個通用名稱 (Common Names) 的列表； Caddy 將選擇第一個根證書與至少一個指定通用名稱匹配的鏈。

	- **any_common_name** <span id="any_common_name"/> 是一個或多個通用名稱的列表； Caddy 將選擇第一個發行者與至少一個指定通用名稱匹配的鏈。

- **profile** 是申請證書時要應用的 [ACME 配置檔案 (ACME profile)](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/) 的名稱。如果你指定了一個，所有配置的（隱式或以其他方式） CA 必須支持此配置檔案。請參閱你的 CA 文檔以了解可用的配置檔案；某些 CA 可能不支持配置檔案。 實驗性：ACME 配置檔案規範仍處於草案狀態，因此此特性/功能可能會發生更改或移除。


<a id="zerossl"></a>
#### zerossl

使用 [ZeroSSL 的專有證書簽發 API](https://zerossl.com/documentation/api/) 獲取證書。需要 API 密鑰，且根據你的方案可能還需要付費。請注意，此簽發方式與 [ZeroSSL 的 ACME 端點](https://zerossl.com/documentation/acme/) 不同。要使用 ZeroSSL 的 ACME 端點，請使用上面描述的配置了 ZeroSSL ACME 目錄端點的 `acme` 發行者。

```caddy-d
... zerossl <api_key> {
	validity_days <days>
	alt_http_port <port>
	dns <provider_name> ...
	propagation_delay <duration>
	propagation_timeout <duration>
	resolvers <list...>
	dns_ttl <duration>
}
```

- **validity_days** <span id="validity_days"/> 定義證書壽命。僅接受某些值；詳情請參閱 [ZeroSSL 文檔](https://zerossl.com/documentation/api/create-certificate/) 。
<!--   
  默認值：`https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> 是用於完成 ZeroSSL HTTP 驗證的端口（如果不是 80 端口）。
- **dns** <span id="zerossl_dns"/> 使用命名的 DNS 提供者啟用 CNAME 驗證方法，並使用給定配置進行自動記錄配置。 DNS 提供者插件必須從 [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) 存儲庫安裝。每個提供者插件在名稱後可能有自己的語法；詳情請參閱其文檔。維護對每個 DNS 提供者的支持是社區的努力。
- **propagation_delay** <span id="zerossl_propagation_delay"/> 是在檢查 CNAME 記錄傳播之前等待多長時間。
- **propagation_timeout** <span id="zerossl_propagation_timeout"/> 是在放棄之前等待 CNAME 記錄傳播多長時間。
- **resolvers** <span id="zerossl_resolvers"/> 定義檢查 CNAME 記錄傳播時使用的自定義 DNS 解析器。
- **dns_ttl** <span id="zerossl_dns_ttl"/> 配置作為驗證過程一部分創建的 CNAME 記錄的 TTL。



<a id="internal"></a>
#### internal

從內部證書頒發機構獲取證書。

```caddy-d
... internal {
	ca       <name>
	lifetime <duration>
	sign_with_root
}
```

- **ca** <span id="ca"/> 是要使用的內部 CA 的名稱。默認值：`local` 。參見 [PKI 應用全域選項](/docs/caddyfile/options#pki-options) 來配置 `local` CA 或創建替代 CA。

  默認情況下，根 CA 證書具有 `3600d` 的壽命（10 年），中間證書具有 `7d` 的壽命（7 天）。

  Caddy 將嘗試將根 CA 證書安裝到系統信任庫，但當 Caddy 以非特權用戶身份運行或在 Docker 容器中運行時，這可能會失敗。在這種情況下，需要手動安裝根 CA 證書，方法是使用 [`caddy trust`](/docs/command-line#caddy-trust) 命令，或 [從容器中複製出來](/docs/running#usage) 。

- **lifetime** <span id="lifetime"/> 是一個 [持續時間值](/docs/conventions#durations) ，設置內部簽發的分葉證書的有效期。默認值：`12h` 。除非絕對必要，否則 *不建議* 更改此項。它必須短於中間證書的壽命。

- **sign_with_root** <span id="sign_with_root"/> 強制將根證書作為發行者而不是中間證書。 *不建議* 這樣做，並且僅應在設備/客戶端無法正確驗證證書鏈時使用（非常罕見）。



<a id="certificate-managers"></a>
### 證書管理員 (Certificate Managers)

證書管理員模塊與發行者模塊不同，使用管理員模塊意味著外部工具或服務正在保持證書續訂，而發行者模塊則意味著 Caddy 本身正在管理證書。 （發行者模塊將證書簽署請求 (CSR) 作為輸入，但證書管理員模塊將 TLS ClientHello 作為輸入。）

這些管理員模塊隨 `tls` 指令標準提供：

<a id="tailscale"></a>
#### tailscale

從本地運行的 [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) 實例獲取證書。 [必須在你的 Tailscale 帳戶中啟用 HTTPS](https://tailscale.com/kb/1153/enabling-https/) (或你的開源 [Headscale 服務器 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/juanfont/headscale)) ；並且 Caddy 進程必須以 root 身份運行，或者你必須配置 `tailscaled` 以向你的 Caddy 用戶授予 [獲取證書的權限](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348) 。

***注意：這通常是不需要的！*** Caddy 會自動為所有 `*.ts.net` 網域使用 Tailscale，無需任何額外配置。

```caddy-d
get_certificate tailscale  # 通常不需要！
```


<a id="http-1"></a>
#### http

通過發送 HTTP(S) 請求來獲取證書。響應必須具有 `200` 狀態碼，且正文必須包含一個 PEM 鏈，包括完整證書（含中間證書）以及私鑰。

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> 是發送請求的完整規範 URL。出於性能原因，強烈建議這是一個本地端點。 URL 將增加以下查詢字符串參數： 

  - `server_name`: SNI 值
  - `signature_schemes`: 以逗號分隔的簽名算法十六進制 ID 列表
  - `cipher_suites`: 以逗號分隔的密碼套件十六進制 ID 列表
  - `local_ip`: 客戶端發送請求的 IP 地址



<a id="examples"></a>
## 範例

使用自定義證書和私鑰。證書應具有與站點位址匹配的 [SANs](https://en.wikipedia.org/wiki/Subject_Alternative_Name) ：

```caddy
example.com {
	tls cert.pem key.pem
}
```

在當前站點塊中為所有主機使用 [本地受信任](/docs/automatic-https#local-https) 的證書，而不是通過 ACME / Let's Encrypt 獲取公共證書（在開發環境中很有用）：

```caddy
example.com {
	tls internal
}
```

使用本地受信任的證書，但通過 [隨需 (On-Demand)](/docs/automatic-https#on-demand-tls) 進行管理，而不是在後台管理。這允許你將任何網域指向你的 Caddy 實例，並讓它自動為你配置證書。如果你的 Caddy 實例可以公開存取，則 *不應* 使用此功能，因為攻擊者可能會利用它來耗盡服務器的資源：

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

為內部 CA 指定自定義選項（不能使用 `tls internal` 快捷方式）：

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

為你的 ACME 帳戶指定電子郵件地址（但如果所有站點都使用同一個電子郵件，我們建議改用 `email` [全域選項](/docs/caddyfile/options) ）：

```caddy
example.com {
	tls your@email.com
}
```

為在 Cloudflare 上管理的網域啟用 DNS 驗證，帳戶憑據存儲在環境變量中。這將解鎖通配符證書支持，這需要 DNS 驗證：

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

通過 HTTP 獲取證書鏈，而不是讓 Caddy 管理它。請注意，[`get_certificate`](#certificate-managers) 暗示啟用了 [`on_demand`](#on_demand) ，即使用模塊獲取證書而不是觸發 ACME 簽發：

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

啟用 TLS 客戶端身份驗證，並要求客戶端出示有效的證書，該證書將通過 [`trust_pool`](#trust_pool) `file` 提供者針對所有提供的 CA 進行驗證：

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
