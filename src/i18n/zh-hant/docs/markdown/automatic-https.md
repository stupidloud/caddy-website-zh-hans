---
title: "自動 HTTPS"
---

# 自動 HTTPS

**Caddy 是第一個自動 *且預設* 使用 HTTPS 的網頁伺服器。**

自動 HTTPS 為您的所有網站提供 TLS 憑證並保持其更新。它還會為您將 HTTP 重新導向到 HTTPS！Caddy 使用安全且現代的預設值 —— 不需要停機、額外設定或單獨的工具。

<aside class="tip">
	Caddy 創新了自動 HTTPS 技術；自 2015 年可行第一天起，我們就一直在做這件事。Caddy 的 HTTPS 自動化邏輯是世界上最成熟且最強健的。
</aside>

這是一個展示其運作方式的 28 秒影片：

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**選單：**

- [概覽](#overview)
- [啟用](#activation)
- [效果](#effects)
- [主機名要求](#hostname-requirements)
- [本地 HTTPS](#local-https)
- [測試](#testing)
- [ACME 挑戰](#acme-challenges)
- [隨選 TLS](#on-demand-tls)
- [錯誤](#errors)
- [儲存](#storage)
- [萬用字元憑證](#wildcard-certificates)
- [加密用戶端 Hello (ECH)](#encrypted-clienthello-ech)


<a id="overview"></a>
## 概覽

**預設情況下，Caddy 透過 HTTPS 提供所有網站。**

- Caddy 透過 HTTPS 提供 IP 位址和本地/內部主機名，使用在本地自動受信任的自簽名憑證（如果允許）。
	- 範例：`localhost`, `127.0.0.1`
- Caddy 透過 HTTPS 提供公共 DNS 名稱，使用來自公共 ACME CA 的憑證，例如 [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) 或 [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com)。
	- 範例：`example.com`, `sub.example.com`, `*.example.com`

Caddy 自動保持所有受管憑證的更新，並將 HTTP（預設埠 `80`）重新導向到 HTTPS（預設埠 `443`）。

**對於本地 HTTPS：**

- Caddy 可能會提示輸入密碼，以便將其唯一的根憑證安裝到您的信任存放區中。這在每個根憑證只會發生一次；您可以隨時將其移除。
- 任何在不信任 Caddy 根 CA 憑證的情況下存取該網站的用戶端都會顯示安全性錯誤。

**對於公共網域名稱：**

<aside class="tip">

這些是任何基本生產網站的共同要求，而不僅僅是 Caddy。主要的區別在於在執行 Caddy **之前** 正確設定您的 DNS 紀錄，以便它可以提供憑證。

</aside>


- 如果您網域的 A/AAAA 紀錄指向您的伺服器，
- 埠 `80` 和 `443` 在外部是開啟的，
- Caddy 可以綁定到這些埠（*或* 這些埠被轉發到 Caddy），
- 您的 [資料目錄](/docs/conventions#data-directory) 是可寫入且持久的，
- 且您的網域名稱出現在設定檔中相關的位置，

那麼網站將自動透過 HTTPS 提供。您不需要對此做任何其他事情。它就是能用！

因為 HTTPS 利用了共享的公共基礎設施，作為伺服器管理員，您應該了解本頁面上的其餘資訊，以便避免不必要的技術問題，在發生問題時進行疑難排解，並正確設定進階部署。


<a id="activation"></a>
## 啟用

當 Caddy 知道它正在提供的網域名稱（即主機名）或 IP 位址時，它會隱含地啟動自動 HTTPS。根據您執行或設定 Caddy 的方式，有多種方法可以告訴 Caddy 您的網域/IP：

- [Caddyfile](/docs/caddyfile) 中的 [網站位址](/docs/caddyfile/concepts#addresses)
- [JSON routes](/docs/modules/http#servers/routes) 最上層的 [host matcher](/docs/json/apps/http/servers/routes/match/host/)
- 命令列旗標，例如 [`--domain`](/docs/command-line#caddy-file-server) 或 [`--from`](/docs/command-line#caddy-reverse-proxy)
- [automate](/docs/json/apps/tls/certificates/automate/) 憑證載入器

以下任何情況都將全部或部分阻止自動 HTTPS 的啟動：

- [透過 JSON](/docs/json/apps/http/servers/automatic_https/) 或 [透過 Caddyfile](/docs/caddyfile/options#auto-https) 明確停用它
- 未在設定中提供任何主機名或 IP 位址
- 僅在 HTTP 埠監聽
- 在 Caddyfile 中的 [網站位址](/docs/caddyfile/concepts#addresses) 前加上 `http://`
- 手動載入憑證（除非設定了 [`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/)）

**特殊情況：**

- 以 `.ts.net` 結尾的網域將不受到 Caddy 管理。相反，Caddy 會在交握時自動嘗試從本地執行的 [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) 實例獲取這些憑證。這要求 [在您的 Tailscale 帳戶中啟用了 HTTPS <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/)，且 Caddy 程序必須以 root 身分執行，或者您必須設定 `tailscaled` 以授予您的 Caddy 使用者 [獲取憑證的權限](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348)。


<a id="effects"></a>
## 效果

當自動 HTTPS 啟動時，會發生以下情況：

- 為 [所有符合條件的網域名稱](#hostname-requirements) 獲取並更新憑證
- 將 HTTP 重新導向到 HTTPS（這使用 [HTTP 埠](/docs/modules/http#http_port) `80`）

自動 HTTPS 永遠不會覆寫明確的設定，它只會擴充它。

如果您已經有一個監聽在 HTTP 埠的 [伺服器](/docs/json/apps/http/servers/)，HTTP->HTTPS 重新導向 route 將插入在具有 host matcher 的 route 之後，但在使用者定義的 catch-all route 之前。

如果需要，您可以 [自訂或停用自動 HTTPS](/docs/json/apps/http/servers/automatic_https/)；例如，您可以跳過某些網域名稱或停用重新導向（對於 Caddyfile，請使用 [全域選項](/docs/caddyfile/options) 進行此操作）。


<a id="hostname-requirements"></a>
## 主機名要求

如果滿足以下條件，所有主機名（網域名稱）都符合完全管理憑證的資格：

- 非空
- 僅由字母數字、連字號、點和萬用字元 (`*`) 組成
- 不以點開頭或結尾 ([RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5))

此外，如果滿足以下條件，主機名符合公共受信任憑證的資格：

- 不是 localhost（包括 `.localhost`, `.local`, `.internal` 和 `.home.arpa` TLDs）
- 不是 IP 位址
- 只有一個萬用字元 `*` 作為最左邊的標籤


<a id="local-https"></a>
## 本地 HTTPS

Caddy 對所有指定了主機（網域、IP 或主機名）的網站自動使用 HTTPS，包括內部和本地主機。某些主機要麼不是公共的（例如 `127.0.0.1`, `localhost`），要麼通常不符合公共受信任憑證的資格（例如 IP 位址 —— 您可以為它們獲取憑證，但僅限於某些 CA）。除非停用，否則這些網站仍會透過 HTTPS 提供。

為了透過 HTTPS 提供非公共網站，Caddy 會生成自己的憑證授權單位 (CA) 並使用它來簽署憑證。信任鏈由根憑證和中間憑證組成。分葉憑證由中間憑證簽署。它們儲存在 [Caddy 的資料目錄](/docs/conventions#data-directory) 中的 `pki/authorities/local`。

Caddy 的本地 CA 由 [Smallstep 函式庫 <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/) 提供支援。

本地 HTTPS 不使用 ACME，也不執行任何 DNS 驗證。它僅在本地機器上運作，並且僅在安裝了 CA 根憑證的地方受信任。

<a id="ca-root"></a>
### CA 根

根金鑰的私鑰是使用加密安全的偽隨機來源唯一生成的，並以受限權限持久化到儲存中。它僅在執行簽署任務時載入到記憶體中，之後它會離開範疇以進行垃圾回收。

雖然可以將 Caddy 設定為直接使用根金鑰進行簽署（以支援不符合規範的用戶端），但這在預設情況下是停用的，且根金鑰僅用於簽署中間金鑰。

第一次使用根金鑰時，Caddy 會嘗試將其安裝到系統的本地信任存放區中。如果它沒有權限這樣做，它會提示輸入密碼。此行為可以透過 [Caddyfile 中的 `skip_install_trust`](/docs/caddyfile/options#skip-install-trust) 或 [JSON 設定中的 `"install_trust": false`](/docs/json/apps/pki/certificate_authorities/install_trust/) 來停用。如果由於以非特權使用者身分執行而失敗，您可以執行 [`caddy trust`](/docs/command-line#caddy-trust) 以特權使用者身分重試安裝。

<aside class="tip">
	只要您的電腦沒有受到侵害且您唯一的根金鑰沒有洩漏，在您自己的機器上信任 Caddy 的根憑證是安全的。
</aside>

安裝 Caddy 的根 CA 後，您將在本地信任存放區中看到它為 "Caddy Local Authority"（除非您設定了不同的名稱）。如果您願意，可以隨時解除安裝它（[`caddy untrust`](/docs/command-line#caddy-untrust) 命令讓這變得很簡單）。

請注意，自動將憑證安裝到本地信任存放區僅是為了方便，並不保證一定有效，特別是如果使用了容器或者 Caddy 是以非特權系統服務執行。最終，如果您依賴內部 PKI，系統管理員有責任確保 Caddy 的根 CA 已正確添加到必要的信任存放區（這超出了網頁伺服器的範疇）。


<a id="ca-intermediates"></a>
### CA 中間體

還會生成一個中間憑證和金鑰，這將用於簽署分葉（各個網站）憑證。

與根憑證不同，中間憑證的壽命要短得多，並且會根據需要自動更新。


<a id="testing"></a>
## 測試

要測試或實驗您的 Caddy 設定，請確保將 [ACME 端點](/docs/modules/tls.issuance.acme#ca) 更改為預備 (staging) 或開發 URL，否則您可能會達到速率限制，這可能會阻礙您存取 HTTPS 長達一週，具體取決於您達到的速率限制。

Caddy 的預設 CA 之一是 [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/)，它有一個 [預備端點 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/)，不受相同的 [速率限制 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/) 限制：

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

<a id="acme-challenges"></a>
## ACME 挑戰

獲取公共受信任的 TLS 憑證需要來自公共受信任的第三方機構的驗證。如今，此驗證程序已透過 [ACME 協定 <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555) 自動化，並且可以透過以下三種方式（"挑戰類型"）之一執行。

預設情況下啟用前兩種類型的挑戰。如果啟用了多個挑戰，Caddy 會隨機選擇一個，以避免意外依賴特定挑戰。隨著時間的推移，它會了解哪種挑戰類型最成功，並開始優先考慮它，但在必要時會回退到其他可用的挑戰類型。


<a id="http-challenge"></a>
### HTTP 挑戰

HTTP 挑戰對候選主機名的 A/AAAA 紀錄執行權威 DNS 查詢，然後透過埠 `80` 使用 HTTP 請求臨時加密資源。如果 CA 看到預期的資源，則簽發憑證。

此挑戰要求埠 `80` 可從外部存取。如果 Caddy 無法在埠 80 上監聽，則必須將來自埠 `80` 的封包轉發到 Caddy 的 [HTTP 埠](/docs/json/apps/http/http_port/)。

此挑戰預設啟用，不需要明確設定。


<a id="tls-alpn-challenge"></a>
### TLS-ALPN 挑戰

TLS-ALPN 挑戰對候選主機名的 A/AAAA 紀錄執行權威 DNS 查詢，然後透過埠 `443` 使用包含特殊 ServerName 和 ALPN 值的 TLS 交握請求臨時加密資源。如果 CA 看到預期的資源，則簽發憑證。

此挑戰要求埠 `443` 可從外部存取。如果 Caddy 無法在埠 443 上監聽，則必須將來自埠 `443` 的封包轉發到 Caddy 的 [HTTPS 埠](/docs/json/apps/http/https_port/)。

此挑戰預設啟用，不需要明確設定。


<a id="dns-challenge"></a>
### DNS 挑戰

DNS 挑戰對候選主機名的 `TXT` 紀錄執行權威 DNS 查詢，並尋找具有特定值的特殊 `TXT` 紀錄。如果 CA 看到預期的值，則簽發憑證。

此挑戰不需要任何開放埠，且請求憑證的伺服器不需要可從外部存取。但是，DNS 挑戰需要設定。Caddy 需要知道存取您網域 DNS 提供者的憑據，以便它可以設定（並清除）特殊的 `TXT` 紀錄。如果啟用了 DNS 挑戰，預設情況下會停用其他挑戰。

由於 ACME CA 在查詢挑戰驗證的 `TXT` 紀錄時遵循 DNS 標準，因此您可以使用 CNAME 紀錄將回答挑戰的任務委派給其他 DNS 區域。這可用於將 `_acme-challenge` 子網域委派給 [另一個區域](/docs/caddyfile/directives/tls#dns_challenge_override_domain)。如果您您的 DNS 提供者不提供 API，或者不受 Caddy 的 DNS 外掛程式之一支援，這特別有用。

DNS 提供者支援是一項社群努力。[在我們的 wiki 上了解如何為您的提供者啟用 DNS 挑戰。](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


<a id="on-demand-tls"></a>
## 隨選 TLS

Caddy 開創了一項我們稱為 **隨選 TLS** (On-Demand TLS) 的新技術，它會在需要它的第一次 TLS 交握期間動態獲取新憑證，而不是在設定載入時。至關重要的是，這 **不** 需要提前在您的設定中硬編碼網域名稱。

許多企業依賴這項獨特的功能，在提供數以萬計的網站時，以更低的成本和更少的營運煩惱來擴展其 TLS 部署。

隨選 TLS 在以下情況很有用：

- 您在啟動或重新載入伺服器時不知道所有的網域名稱，
- 網域名稱可能不會立即正確設定（DNS 紀錄尚未設定），
- 您無法控制網域名稱（例如它們是客戶網域）。

啟用隨選 TLS 後，您不需要在設定中指定網域名稱即可為其獲取憑證。相反，當收到 Caddy 尚未擁有憑證的伺服器名稱 (SNI) 的 TLS 交握時，交握會被保留，同時 Caddy 獲取憑證以用於完成交握。延遲通常只有幾秒鐘，而且只有最初的交握很慢。所有未來的交握都很快，因為憑證已快取並重複使用，且更新發生在背景。未來的交握可能會觸發憑證的維護以保持其更新，但如果憑證尚未過期，則此維護會在背景進行。

<a id="using-on-demand-tls"></a>
### 使用隨選 TLS

**必須同時啟用和限制隨選 TLS 以防止濫用。**

如果使用 JSON 設定，啟用隨選 TLS 發生在 [TLS automation policies](/docs/json/apps/tls/automation/policies/) 中，或者如果使用 Caddyfile，發生在 [具有 `tls` 指令的網站區塊](/docs/caddyfile/directives/tls) 中。

為了防止濫用此功能，您必須設定限制。這在 JSON 設定的 [`automation` 物件](/docs/json/apps/tls/automation/on_demand/)中完成，或在 Caddyfile 的 [`on_demand_tls` 全域選項](/docs/caddyfile/options#on-demand-tls)中完成。限制是 "全域" 的，不能按網站或按網域設定。主要的限制是一個 "ask" 端點，Caddy 將向其發送 HTTP 請求，以詢問是否有權獲取並管理交握中網域的憑證。這意味著您將需要一些內部後端，例如，它可以查詢資料庫的帳戶表，並查看是否有客戶使用該網域名稱註冊。

請注意您的 CA 簽發憑證的速度。如果超過幾秒鐘，這將對使用者體驗產生負面影響（僅對第一個用戶端）。

由於其延遲性質和防止濫用所需的額外設定，我們建議僅在您的實際使用案例符合上述描述時才啟用隨選 TLS。

[有關有效使用隨選 TLS 的更多資訊，請參見我們的 wiki 文章。](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)


<a id="errors"></a>
## 錯誤

如果憑證管理發生錯誤，Caddy 會盡力繼續運作。

預設情況下，憑證管理在背景執行。這意味著它不會阻塞啟動或降低您的網站速度。然而，這也意味著伺服器甚至在所有憑證可用之前就已經在執行。在背景執行允許 Caddy 在較長一段時間內使用指數退避重試。

如果獲取或更新憑證時發生錯誤，會發生以下情況：

1. Caddy 在短暫停頓後重試一次，以防萬一只是偶然
2. Caddy 短暫停頓，然後切換到下一個啟用的挑戰類型
3. 嘗試了所有啟用的挑戰類型後，[它會嘗試下一個設定的簽發者](#issuer-fallback)
	- Let's Encrypt
	- ZeroSSL
4. 嘗試了所有簽發者後，它會指數級退避
	- 每次嘗試之間最長 1 天
	- 最多持續 30 天

在與 Let's Encrypt 重試期間，Caddy 會切換到他們的 [預備環境 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/)，以避免速率限制疑慮。這不是一個完美的策略，但通常很有幫助。

ACME 挑戰至少需要幾秒鐘，且內部速率限制有助於減輕意外濫用。除了您或 CA 設定的限制外，Caddy 還使用內部速率限制，因此您可以交給 Caddy 一盤包含一百萬個網域名稱的清單，它會逐漸 —— 但儘快 —— 為所有網域名稱獲取憑證。Caddy 的內部速率限制目前為每 10 秒每個 ACME 帳戶 10 次嘗試。

為了避免資源洩漏，當設定更改時，Caddy 會中止執行中的任務（包括 ACME 交易）。雖然 Caddy 能夠處理頻繁的設定重新載入，但請注意此類營運考量，並考慮批次處理設定更改以減少重新載入，並讓 Caddy 有機會實際在背景完成獲取憑證。

<a id="issuer-fallback"></a>
### 簽發者回退

Caddy 是第一個（也是目前唯一一個）在無法成功獲取憑證時支援完全冗餘、自動故障轉移到其他 CA 的伺服器。

預設情況下，Caddy 啟用兩個相容 ACME 的 CA：[**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) 和 [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com)。如果 Caddy 無法從 Let's Encrypt 獲取憑證，它將嘗試使用 ZeroSSL；如果兩者都失敗，它將退避並在稍後再次重試。在您的設定中，您可以自訂 Caddy 用於獲取憑證的簽發者，無論是通用的還是針對特定名稱的。


<a id="storage"></a>
## 儲存

Caddy 將公共憑證、私鑰和其他資產儲存在其 [設定的儲存設施](/docs/json/storage/)中（如果未設定，則為預設儲存設施 —— 請參見連結以獲取詳細資訊）。

**使用預設設定時，您需要知道的主要事情是 `$HOME` 資料夾必須是可寫入且持久的。** 為了幫助您疑難排解，如果指定了 `--environ` 旗標，Caddy 會在啟動時列印其環境變數。

任何設定為使用相同儲存的 Caddy 實例都將自動共享這些資源，並協調憑證管理作為一個叢集。

在嘗試任何 ACME 交易之前，Caddy 將測試設定的儲存，以確保它是可寫入的且具有足夠的容量。這有助於減少不必要的鎖定爭用。


<a id="wildcard-certificates"></a>
## 萬用字元憑證

當 Caddy 設定為提供具有符合條件的萬用字元名稱的網站時，它可以獲取並管理萬用字元憑證。如果網站名稱僅其最左邊的網域標籤是萬用字元，則該網站名稱符合萬用字元資格。例如，`*.example.com` 符合條件，但以下不符合：`sub.*.example.com`, `foo*.example.com`, `*bar.example.com`, 以及 `*.*.example.com`。（這是 WebPKI 的限制。）

如果使用 Caddyfile， Caddy 在憑證主體名稱方面會逐字採用網站名稱。換句話說，定義為 `sub.example.com` 的網站將導致 Caddy 管理 `sub.example.com` 的憑證，而定義為 `*.example.com` 的網站將導致 Caddy 管理 `*.example.com` 的萬用字元憑證。您可以在我們的 [通用 Caddyfile 模式](/docs/caddyfile/patterns#wildcard-certificates) 頁面上看到此展示。如果您需要不同的行為，[JSON 設定](/docs/json/)可以讓您更精確地控制憑證主體和網站名稱（"host matchers"）。

從 Caddy 2.10 開始，在自動化萬用字元憑證時，Caddy 將對設定中的各個子網域使用萬用字元憑證。除非明確設定為這樣做（例如使用 `force_automate`），否則它不會為各個子網域獲取憑證。

萬用字元憑證代表了廣泛的授權，僅當您擁有如此多的子網域，以至於為它們管理個別憑證會使 PKI 緊張或導致您達到 CA 強制執行的速率限制時，或者如果隱私權衡值得在金鑰洩露的情況下暴露如此多的 DNS 區域的風險時，才應使用它們。請注意，僅靠萬用字元憑證無法提供隱藏特定子網域的隱私：除非啟用了加密用戶端 Hello (ECH)，否則它們仍會在 TLS ClientHello 封包中暴露。（見下文。）

**注意：** [Let's Encrypt 要求 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) 使用 [DNS 挑戰](#dns-challenge) 才能獲取萬用字元憑證。


<a id="encrypted-clienthello-ech"></a>
## 加密用戶端 Hello (ECH)

通常，TLS 交握涉及以明文發送 ClientHello，包括伺服器名稱指示（SNI；正在連線的網域）。這是因為它包含交握後加密連線所需的參數。這當然會向任何可以竊聽連線的人暴露網域名稱（這是 ClientHello 中最敏感的部分），即使他們不在您的直接物理鄰近區域內。當目標 IP 可能提供許多不同的網站時，它會揭示您正在連線到哪個服務，這也是一些政府審查網路的方式。

透過加密用戶端 Hello，用戶端可以透過將真正的 ClientHello 包裝在一個 "外部" ClientHello 中來保護網域名稱，該外部 ClientHello 建立了用於解密 "內部" ClientHello 的參數。然而，許多移動部件需要完美地結合在一起，這才能發揮作用並提供實際的隱私效益。

首先，用戶端需要知道使用什麼參數或設定來加密 ClientHello。此資訊包括公鑰和 "外部" 網域（"公共名稱"）等。此設定必須以某種可靠的方式發佈或分發。

理論上，您可以將其寫在一張紙上並分發給每個人，但大多數主要瀏覽器支援在連線到網站時查詢包含 ECH 參數的 HTTPS 類型 DNS 紀錄。因此，您需要：(1) 生成 ECH 設定（公鑰/私鑰對，以及其他參數），然後 (2) 建立一個包含 base64 編碼的 ECH 設定的 HTTPS 類型 DNS 紀錄。

或者... 您可以讓 Caddy 為您完成所有這些工作。Caddy 是第一個也是唯一一個可以自動生成、發佈和提供 ECH 設定的網頁伺服器。

一旦發佈了 HTTPS 紀錄，用戶端在連線到您的網站時將需要對 HTTPS 紀錄執行 DNS 查詢。通常，DNS 查詢是明文的，這會損害生成的 ECH 交握的安全性，因此瀏覽器將需要使用安全的 DNS 協定，例如 DNS-over-HTTPS (DoH) 或 DNS-over-TLS (DoT)。根據瀏覽器的不同，這可能需要手動啟用。

一旦用戶端安全地下載了 ECH 設定，它就會使用嵌入的公鑰來加密 ClientHello，並繼續連線到您的網站。然後 Caddy 解密內部 ClientHello 並繼續為您的網站提供服務，而網域名稱永遠不會以明文形式出現在線路上。

<a id="deployment-considerations"></a>
### 部署考量

ECH 是一項細微的技術。儘管 Caddy 完全自動化了 ECH，但為了獲得最大的隱私效益，仍需要考慮許多事項。您還應該意識到各種權衡。

<a id="publication"></a>
#### 發佈

Caddy 只有在該網域已經有紀錄的情況下才會為其建立 HTTPS 紀錄。這可以防止破壞可能被萬用字元覆蓋的子網域的 DNS 查詢。確保您的網站至少有一個指向您伺服器的 A/AAAA 紀錄。如果您僅對 DNS 紀錄使用萬用字元，那麼該萬用字元網域也需要出現在您的 Caddy 設定中。

Caddy 不會為具有 CNAME 紀錄的網域發佈 HTTPS 紀錄。

<a id="ech-grease"></a>
#### ECH GREASE

如果您開啟 Wireshark，然後在現代版本的 Firefox 或 Chrome 等主要瀏覽器（即使停用了 ECH）中連線到任何網站（甚至是其不支援 ECH 的網站），您可能會注意到其交握包含 `encrypted_client_hello` 擴充：

![ECH GREASE](/resources/images/ech-grease.png)

這樣做的目的是使真正的 ECH 交握與明文交握無法區分。如果 ECH 交握看起來與普通交握不同，審查員就可以用最小的後果/附帶損害來阻止 ECH 交握。但如果他們阻止了任何具有似是而非的 ECH 擴充的交握，他們基本上就會關閉大部分的網際網路。（目標是增加大規模審查的成本。）

這主要在對連線進行疑難排解時需要了解。

<a id="key-rotation"></a>
#### 金鑰輪轉

與憑證金鑰一樣，長時間使用同一個金鑰不是好的做法（而且可能非常不安全）。因此，ECH 金鑰應定期輪轉。與憑證不同，ECH 設定不會嚴格過期。但伺服器仍應輪轉它們。

然而，金鑰輪轉很棘手，因為用戶端需要知道更新後的金鑰。如果伺服器只是簡單地將舊金鑰替換為新金鑰，除非立即通知用戶端新金鑰，否則所有 ECH 交握都會失敗。但僅僅發佈更新後的金鑰是不夠的。事實上，DNS 紀錄有 TTL，解析器會快取回應等。用戶端可能需要幾分鐘、幾小時甚至幾天才能查詢到更新後的 HTTPS 紀錄並開始使用新的 ECH 設定。

出於這個原因，伺服器應在一段時間內繼續支援舊的 ECH 設定。如果不這樣做，就有在大規模範圍內暴露明文伺服器名稱的風險。Caddy 會不時輪轉金鑰，並支援已輪轉的金鑰一段時間，直到最終將其捨棄。

然而，這可能還不夠。出於各種原因，某些用戶端仍無法獲得更新後的金鑰，每當發生這種情況時，就有暴露伺服器名稱的風險。因此，需要有另一種方式在連線中（in-band）為用戶端提供更新後的設定。這就是 *外部名稱* (outer name)（或 *公共名稱* (public name)）的作用。

<a id="public-name"></a>
#### 公共名稱

"外部" ClientHello 是一個普通的 ClientHello，但有兩個只有原始伺服器知道的細微差別：

1. SNI 擴充是假的
2. ECH 擴充是真的

該 "外部" SNI 擴充包含保護您真實網域的公共名稱。此名稱可以是任何名稱，但 **您的伺服器必須對公共名稱具有權威性**，因為 Caddy *會* 為其獲取憑證。

如果用戶端嘗試進行 ECH 連線，但伺服器無法解密內部 ClientHello，它實際上可以使用帶有外部名稱憑證的 *外部* ClientHello 完成交握。此安全連線嚴格地 *僅* 用於向用戶端發送當前的 ECH 設定；即它是為了完成初始 TLS 連線而建立的臨時 TLS 連線。不傳輸應用程式資料：僅傳輸 ECH 金鑰。一旦用戶端獲得了更新後的金鑰，它就可以按預期建立 TLS 連線。

透過這種方式，真實的伺服器名稱保持受到保護，且不同步的用戶端仍能連線，這兩者都是安全性的重要元素。

公共名稱可以是您的網站網域之一、子網域或指向您伺服器的任何其他網域名稱。我們建議僅選擇一個通用的名稱。例如，Cloudflare 在 `cloudflare-ech.com` 背後提供數百萬個網站。這對於增加您的匿名集的大小非常重要。

公共名稱不應為空；即必須設定公共名稱才能正常運作。Caddy 目前不強制執行此操作（以後可能會），但 ECH 規範要求公共名稱至少為 1 位元組長。有些軟體會接受空名稱，有些則不會。這可能導致令人困惑的行為，例如瀏覽器使用 ECH 但伺服器將其拒絕為無效；或者瀏覽器不使用 ECH（因為它無效），即使設定已正確位於 DNS 紀錄中。網站擁有者有責任確保正確的 ECH 設定和發佈，以確保隱私。


<a id="anonymity-set"></a>
#### 匿名集

為了最大化 ECH 的隱私效益，請努力最大化您的 *匿名集* (anonymity set) 的大小。從本質上講，這個集由對觀察者俱有相同行為的面對用戶端伺服器組成。其理念是觀察者無法輕易地縮減/推斷用戶端正在連線的可能網站或服務。

在實踐中，我們建議為您的所有網站僅設定一個公共名稱。（每個 ECH 設定只有 1 個公共名稱，因此這意味著在任何給定時間只有 1 個活動的 ECH 設定。）如果您在叢集中執行 Caddy，Caddy 會自動與其他實例共享並協調 ECH 設定，這會為您處理好這件事。

推向極端，這意味著網際網路上的每個網站都可以或應該位於單一 IP 位址和一個公共名稱背後...


<a id="centralization"></a>
#### 中心化

... 這帶我們到了下一個話題：中心化。對 ECH 的批評之一是它傾向於激發中心化。它至少以兩種方式做到這一點：(1) 透過用戶端偏好 DoH/DoT 進行 DNS 查詢，這會透過少數幾個提供者發送所有 DNS 查詢；(2) 透過在大規模範圍內最大化匿名集的大小。

當使用 DoH 或 DoT 時，DNS 查詢都會通過 DoH/DoT 提供者。在用戶端和提供者之間，DNS 資料是加密的，但在提供者和 DNS 伺服器之間，它是不加密的。全球 DoH/DoT 有效地將所有有趣的明文 DNS 流量匯集到幾個大管道中，這些管道已經成熟，可以被觀察... 或失敗。

同樣地，如果我們真正在大規模範圍內最大化匿名集，所有網站都將受到單一公共名稱（如 `cloudflare-ech.com`）的保護。這對隱私有好處，但整個網際網路就受制於 Cloudflare 和那個網域名稱。現在，最大限度地最大化到那種程度是不必要也不切實際的，但理論上的影響仍然有效。

我們建議每個組織或個人為其所有網站選擇一個名稱並使用它，在大多數情況下這應該提供足夠的隱私。然而，請針對您的特定情況諮詢具有個人威脅模型的專家。


<a id="subdomain-privacy"></a>
#### 子網域隱私

有了 ECH，如果部署正確，現在理論上可以使子網域對側向通道保持秘密/私密。

大多數網站不需要這個，因為一般來說，子網域是公共資訊。我們建議不要在網域名稱中放入敏感資訊。話雖如此...

為了避免敏感子網域洩漏到憑證透明度 (CT) 紀錄中，請改用萬用字元憑證。換句話說，與其在您的設定中放入 `sub.example.com`，不如放入 `*.example.com`。（請參閱 [萬用字元憑證](#wildcard-certificates) 以獲取重要資訊。）

另一個洩漏來源是 DNSSEC，大多數權威 DNS 伺服器預設使用它。透過一種稱為 "區域漫步" (zone walking) 的實踐，可以透過查看 NSEC 紀錄來列舉子網域，NSEC 紀錄用於提供經過身份驗證的存在否認。為此，它們按字母順序指向下一個可用的子網域，形成所有紀錄的鏈結清單。確保您的網域至少使用 NSEC3，或者理想情況下使用萬用字元 CNAME 紀錄來減輕這種情況。

然後，在 Caddy 中啟用 ECH。萬用字元憑證結合 ECH 和萬用字元 CNAME 紀錄應能妥善隱藏子網域，只要每個嘗試連線到它的用戶端都使用 ECH 且具有強健的實作。（您仍受制於用戶端以維護隱私。）


<a id="enabling-ech"></a>
### 啟用 ECH

由於正常運作的 ECH 需要將設定發佈到 DNS 紀錄，因此您需要一個外掛了適用於您的 DNS 提供者的 [caddy-dns 模組](https://github.com/caddy-dns) 的 Caddy 組建。

然後，使用 Caddyfile，在全域選項中指定您的 DNS 提供者設定，以及您要使用的 ECH 公共名稱：

```caddy
{
	dns <provider config...>
	ech example.com
}
```

記住：

- DNS 提供者模組必須已外掛，且您必須為您的提供者/帳戶進行正確的設定。
- ECH 公共名稱應指向您的伺服器。Caddy 會為其獲取憑證。它不一定要是您網站的網域之一。

如果使用 JSON，請將這些屬性添加到 `tls` 應用程式：

```json
"encrypted_client_hello": {
	"configs": [
		{
			"public_name": "example.com"
		}
	]
},
"dns": {
	"name": "<provider name>",
	// provider configuration
}
```

這些設定將為您的所有網站啟用 ECH 並發佈 ECH 設定。如果您需要自訂行為或具有進階設置，JSON 設定提供了更大的靈活性。


<a id="verifying-ech"></a>
### 驗證 ECH

目前圍繞 ECH 的工具還不多，因此在撰寫本文時，驗證它是否正常運作的最佳且最通用的方法是使用 Wireshark 並在 ServerName 欄位中尋找您的公共名稱。

首先，啟動您的伺服器，並查看紀錄中是否提到您的網域類似於 "published ECH configuration list" 的內容。（如果您在發佈時遇到任何錯誤，請確保您的 DNS 提供者模組支援 [libdns 1.0](https://github.com/libdns/libdns)，如果遇到問題，請向您的提供者儲存庫提交問題。）Caddy 還應獲取公共名稱的憑證。

接下來，確保您的瀏覽器已啟用 ECH；這可能需要啟用 DoH/DoT。清除瀏覽器（或系統）的 DNS 快取也是一個好主意，以確保它會取得新發佈的 HTTPS 紀錄。我們還建議關閉瀏覽器或至少開啟一個新的私密分頁，以確保它不會重複使用現有連線。

然後，開啟 Wireshark 並開始在適當的網路介面上監聽。當 Wireshark 正在收集封包時，在瀏覽器中載入您的網站。然後您可以暫停 Wireshark。找到您的 TLS ClientHello，您應該在 ServerName 欄位中看到 *公共名稱*，而不是您連線到的實際網域名稱。

記住：即使未使用 ECH，您仍可能看到 `encrypted_client_hello` 擴充。關鍵指標是 SNI 值。如果 ECH 運作正常，您不應該在 Wireshark 中看到明文的真實網站名稱。

如果您在部署 ECH 時遇到問題，請先在我們的 [論壇](https://caddy.community) 中詢問。如果是錯誤，您可以在 GitHub 上 [提交問題](https://github.com/caddyserver/caddy/issues)。


<a id="ech-in-storage"></a>
### 儲存中的 ECH

ECH 設定儲存在 [資料目錄](/docs/conventions#data-directory) 中設定的儲存模組（預設為檔案系統）下的 `ech/configs` 資料夾中。

下一個資料夾是 ECH 設定 ID，它是隨機生成的且相對不重要。規格建議採用隨機性，以幫助減輕指紋識別/追蹤。

元資料邊車檔案可幫助 Caddy 追蹤上次發佈發生的時間。這可以防止在每次設定重新載入時都向您的 DNS 提供者發起大量請求。如果您必須重設此狀態，可以安全地刪除該元資料檔案。但是，這也可能會重設金鑰輪轉的時間。您也可以進入檔案並僅清除有關發佈的資訊。
