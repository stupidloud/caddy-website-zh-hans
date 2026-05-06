---
title: HTTPS 快速入門
---

# <a id="https-quick-start"></a>HTTPS 快速入門

本指南將向你展示如何立即啟動並執行 [全自動管理 HTTPS](/docs/automatic-https)。

<aside class="tip">
	只要在配置中提供了主機名稱，Caddy 默認對所有網站使用 HTTPS。本教程假設你想透過 HTTPS 建立一個公開信任的網站（即不是 "localhost"），因此我們將使用公共域名和外部端口。
</aside>

**先決條件：**
- 基礎終端機 / 命令行操作技能
- 對 DNS 有基本瞭解
- 一個已註冊的公共域名
- 外部可訪問 80 和 443 端口
- `caddy` 和 `curl` 在你的 PATH 中

---

在本教程中，請將 `example.com` 替換為你的實際域名。

將你的域名的 A/AAAA 記錄指向你的伺服器。你可以透過登錄你的 DNS 提供商並管理你的域名來完成此操作。

在繼續之前，請透過權威查詢驗證記錄是否正確。將 `example.com` 替換為你的域名，如果你使用的是 IPv6，請將 `type=A` 替換為 `type=AAAA`：

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=example.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

同時確保你的伺服器可以從公共介面透過 80 和 443 端口從外部訪問。

<aside class="tip">
	如果你位於家庭或其他受限網絡中，可能需要進行端口轉發或調整防火牆設置。
</aside>

我們所要做的就是啟動 Caddy，並在配置中包含你的域名。有幾種方法可以做到這一點。

## <a id="caddyfile"></a>Caddyfile

這是獲得 HTTPS 最常用的方式。

在一個名為 `Caddyfile`（無擴展名）的文件中，第一行寫上你的域名，例如：

```caddy
example.com

respond "Hello, privacy!"
```

然後在同一目錄下執行：

<pre><code class="cmd bash">caddy run</code></pre>

你會看到 Caddy 配置 TLS 證書並透過 HTTPS 提供你的網站服務。這之所以可行，是因為你在 Caddyfile 中的網站地址包含了一個域名。


## <a id="the-file-server-command"></a>`file-server` 命令

如果你只需要透過 HTTPS 提供靜態文件服務，請執行此命令（替換你的域名）：

<pre><code class="cmd bash">caddy file-server --domain example.com</code></pre>

你會看到 Caddy 配置 TLS 證書並透過 HTTPS 提供你的網站服務。


## <a id="the-reverse-proxy-command"></a>`reverse-proxy` 命令

如果你只需要一個簡單的 HTTPS 反向代理（作為 TLS 終端），請執行此命令（替換你的域名和實際後端地址）：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to localhost:9000</code></pre>

你會看到 Caddy 配置 TLS 證書並透過 HTTPS 提供你的網站服務。


## <a id="json-config"></a>JSON 配置

一般的經驗法則是，任何 [host matcher](/docs/json/apps/http/servers/routes/match/host/) 都會觸發自動 HTTPS。

因此，如下所示的 JSON 配置將啟用準備好用於生產環境的 [自動 HTTPS](/docs/automatic-https)：

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["example.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Hello, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
