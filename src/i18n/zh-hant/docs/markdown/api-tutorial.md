---
title: "API 教學"
---

<a id="api-tutorial"></a>
# API 教學

本教學將向你展示如何使用 Caddy 的 [admin API](/docs/api)，這使得以程式化方式實現自動化成為可能。

**目標：**
- 🔲 執行 daemon
- 🔲 為 Caddy 提供 config
- 🔲 測試 config
- 🔲 替換啟動中的 config
- 🔲 遍歷 config
- 🔲 使用 `@id` 標籤

**必備條件：**
- 基礎的終端機 / 命令列技能
- 基礎的 JSON 經驗
- 你的 PATH 中有 `caddy` 和 `curl`

---

要啟動 Caddy daemon，請使用 `run` 子指令：

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">執行 daemon</aside>

這會永久阻塞，但它在做什麼呢？目前... 什麼都沒做。預設情況下，Caddy 的配置（"config"）是空白的。我們可以在另一個終端機中使用 [admin API](/docs/api) 來驗證這一點：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

我們可以透過給予 Caddy 一個 config 來使其發揮作用。其中一種方法是向 [/load](/docs/api#post-load) 端點發送 POST 請求。就像任何 HTTP 請求一樣，有很多方法可以做到這一點，但在本教學中我們將使用 `curl`。

<a id="your-first-config"></a>
## 你的第一個 config

為了準備我們的請求，我們需要建立一個 config。Caddy 的配置只是一個 [JSON 文件](/docs/json/)（或 [任何可以轉換為 JSON 的東西](/docs/config-adapters)）。

<aside class="tip">
	不強制要求使用 config 檔案。配置 API 始終可以在不使用檔案的情況下使用，這在自動化時非常方便。本教學使用檔案是因為手動編輯更為方便。
</aside>

將此內容儲存到 JSON 檔案中：

```json
{
	"apps": {
		"http": {
			"servers": {
				"example": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

然後上傳它：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	請確保不要忘記檔名前面的 @；這會告訴 curl 你正在傳送一個檔案。
</aside>

<aside class="complete">為 Caddy 提供 config</aside>

我們可以用另一個 GET 請求來驗證 Caddy 是否套用了我們的新 config：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

在瀏覽器中前往 [localhost:2015](http://localhost:2015) 或使用 `curl` 來測試它是否正常工作：

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">測試 config</aside>

如果你看到 *Hello, world!*，那麼恭喜你 —— 它正在工作！確保你的 config 按預期工作總是一個好主意，特別是在部署到生產環境之前。

讓我們將歡迎訊息從 "Hello world!" 更改為更具激勵性的內容："I can do hard things." 在你的 config 檔案中進行此更改，使 handler 物件現在看起來像這樣：

```json
{
	"handler": "static_response",
	"body": "I can do hard things."
}
```

儲存 config 檔案，然後再次執行相同的 POST 請求來更新 Caddy 的啟動配置：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">替換啟動中的 config</aside>

為了慎重起見，請驗證 config 已更新：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

透過重新整理瀏覽器頁面（或再次執行 `curl`）來測試它，你將看到一條勵志訊息！

<a id="config-traversal"></a>
## Config 遍歷

我們可以使用 Caddy API 的強大功能來進行更改，而無需觸及我們的 config 檔案，而不是為了小小的更改而上傳整個 config 檔案。

<aside class="tip">
	像我們上面那樣透過替換整個 config 來對生產伺服器進行微小更改可能是危險的；這就像擁有檔案系統的 root 存取權限。Caddy 的 API 允許你限制更改的範圍，以保證 config 的其他部分不會被意外更改。
</aside>

使用請求 URI 的路徑，我們可以遍歷 config 結構並僅更新訊息字串（如果被裁剪，請務必向右滾動）：

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Work smarter, not harder."'
</code></pre>


<aside class="tip">

每次使用 API 更改 config 時，Caddy 都會保留新 config 的副本，以便你以後可以 [**--resume** 它](/docs/command-line#caddy-run)！

</aside>


你可以使用類似的 GET 請求來驗證它是否成功，例如：

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

你應該會看到：

```json
[{"handle":[{"body":"Work smarter, not harder.","handler":"static_response"}]}]
```


<aside class="tip">

你可以使用 [`jq` 指令 <img src="/old/resources/images/external-link.svg" class="external-link">](https://stedolan.github.io/jq/) 來美化 JSON 輸出： **`curl ... | jq`**

</aside>


<aside class="complete">遍歷 config</aside>

**重要提示：** 這應該很明顯，但是一旦你使用 API 進行了不在原始 config 檔案中的更改，你的 config 檔案就會變得過時。有幾種方法可以處理這個問題：

- 使用 [caddy run](/docs/command-line#caddy-run) 指令的 `--resume` 來使用最後一個啟動的 config。
- 不要混合使用 config 檔案與透過 API 進行的更改；保持單一事實來源。
- 透過隨後的 GET 請求 [匯出 Caddy 的新配置](/docs/api#get-configpath)（與前兩個選項相比，不推薦此選項）。

<a id="using-id-in-json"></a>
## 在 JSON 中使用 `@id`

Config 遍歷當然很有用，但路徑有點長，你不覺得嗎？

我們可以給我們的 handler 物件一個 [`@id` 標籤](/docs/api#using-id-in-json) 來使其更容易存取：

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

這會為我們的 handler 物件增加一個屬性：`"@id": "msg"`，所以它現在看起來像這樣：

```json
{
	"@id": "msg",
	"body": "Work smarter, not harder.",
	"handler": "static_response"
}
```


<aside class="tip">

**@id** 標籤可以放在任何物件中，並且可以具有任何原始值（通常是字串）。 [了解更多](/docs/api#using-id-in-json)

</aside>


然後我們可以直接存取它：

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

現在我們可以用更短的路徑來更改訊息：

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Some shortcuts are good."'
</code></pre>

然後再次檢查：

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete">使用 <code>@id</code> 標籤</aside>
