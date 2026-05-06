---
title: 反向代理快速入門
---

<a id="reverse-proxy-quick-start"></a>
# 反向代理快速入門

本指南將向您展示如何快速啟動一個準備好用於生產環境的反向代理（無論是否帶有 HTTPS）。

**先決條件：**
- 基本的終端機 / 命令列技能
- `caddy` 已在您的 PATH 中
- 一個正在運行的後端程序供代理使用

---

本教學假設您有一個運行在 `127.0.0.1:9000` 的後端 HTTP 服務。這些命令適用於 Linux，但同樣的原則也適用於其他作業系統。

您可以在沒有設定檔的情況下運行一個簡單的反向代理，也可以使用設定檔來獲得更多的靈活性和控制。

<a id="command-line"></a>
## 命令列

要啟動一個從您機器的 2080 連接埠到 9000 連接埠的明文 HTTP 代理：

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

然後嘗試：

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

[`reverse-proxy` 命令](/docs/command-line#reverse-proxy) 旨在用於快速簡便的反向代理。（如果您的需求很簡單，您可以在生產環境中使用它。）

<a id="caddyfile"></a>
## Caddyfile

在當前工作目錄中，創建一個名為 `Caddyfile` 的文件，內容如下：

```caddy
:2080

reverse_proxy :9000
```

該設定檔大致相當於上面的 `caddy reverse-proxy` 命令。

然後，在同一個目錄下運行：

<pre><code class="cmd bash">caddy run</code></pre>

然後測試您的代理：

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

如果您更改了 Caddyfile，請確保 [重新載入](/docs/command-line#caddy-reload) Caddy。

這是一個簡單的例子。您可以使用 [`reverse_proxy` 指令](/docs/caddyfile/directives/reverse_proxy) 執行更多操作。

<a id="https-from-client-to-proxy"></a>
## 從用戶端到代理的 HTTPS

如果 Caddy 知道主機名（網域名稱），它將 [自動且預設地通過 HTTPS](/docs/automatic-https) 提供代理服務。如果您省略 `--from` 標誌，`caddy reverse-proxy` 命令將預設為 `localhost`，或者您可以用代理的網域名稱替換 Caddyfile 的第一行。

- 如果您使用 `localhost` 或任何以 `.localhost` 結尾的網域，Caddy 將使用自動更新的自簽名證書。第一次執行此操作時，由於 Caddy 嘗試將其 CA 的根證書安裝到您的信任存放區中，您可能需要輸入密碼。
- 如果您使用任何其他網域名稱，Caddy 將嘗試獲取受大眾信任的證書；請確保您的 DNS 記錄指向您的機器，並且 80 和 443 連接埠已對外開放並導向 Caddy。

如果您不指定連接埠，Caddy 在 HTTPS 情況下預設為 443。在這種情況下，您還需要綁定低階連接埠的權限。在 Linux 上有幾種方法可以做到這一點：

- 以 root 身份運行（例如 `sudo -E`）。
- 或運行 `sudo setcap cap_net_bind_service=+ep $(which caddy)` 以授予 Caddy 這一特定能力。

這是最基本的 `caddy reverse-proxy` 命令，可為您提供 HTTPS：

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

然後嘗試：

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

您可以使用 `--from` 標誌自定義主機名：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

如果您沒有綁定低階連接埠的權限，您可以從較高階的連接埠進行代理：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

如果您正在使用 Caddyfile，只需將第一行更改為您的網域名稱，例如：

```caddy
example.com

reverse_proxy :9000
```

<a id="https-from-proxy-to-backend"></a>
## 從代理到後端的 HTTPS

如果後端支持 TLS，Caddy 也可以在其自身與後端之間使用 HTTPS 進行代理。只需在您的後端地址中使用 `https://`：

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

這要求後端的證書被運行 Caddy 的系統所信任。（除非經過明確配置，否則 Caddy 不會信任自簽名證書。）

當然，您也可以在兩端都使用 HTTPS：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

這會在用戶端到代理、以及代理到後端都提供 HTTPS。

如果您代理到的主機名與您代理的主機名不同，您將需要使用 `--change-host-header` 標誌：

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

預設情況下，Caddy 會原封不動地傳遞所有 HTTP 標頭，包括 `Host`，並且 Caddy 從 Host 標頭派生 TLS ServerName。`--change-host-header` 會將 Host 標頭重置為後端的標頭，以便 TLS 握手可以成功完成。在上面的示例中，它將從 `example.com` 更改為 `localhost:9000`（並且在 TLS 握手中將使用 `localhost`）。
