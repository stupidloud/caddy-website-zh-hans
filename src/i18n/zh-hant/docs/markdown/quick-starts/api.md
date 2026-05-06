---
title: API 快速入門
---

<a id="api-quick-start"></a>
# API 快速入門

**先決條件：** 
- 基礎終端機 / 命令列技能
- PATH 中包含 `caddy` 和 `curl`

---

首先啟動 Caddy：

<pre><code class="cmd bash">caddy start</code></pre>

Caddy 目前正處於閒置運行狀態（使用空白配置）。使用 `curl` 給它一個簡單的配置：

<pre><code class="cmd bash">curl localhost:2019/load \
    -H "Content-Type: application/json" \
    -d @- << EOF
    {
        "apps": {
            "http": {
                "servers": {
                    "hello": {
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
EOF</code></pre>

使用 [Heredoc](https://en.wikipedia.org/wiki/Here_document#Unix_shells) 提供 POST 主體可能很繁瑣，因此如果你更喜歡使用文件，請將 JSON 儲存到名為 `caddy.json` 的文件中，然後改用此命令：

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

現在在瀏覽器中載入 [localhost:2015](http://localhost:2015) 或使用 `curl`：

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

我們還可以使用此 JSON 在不同的介面上定義多個站點：

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				},
				"bye": {
					"listen": [":2016"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Goodbye, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

更新你的 JSON，然後再次執行 API 請求。

在瀏覽器中 [查看](http://localhost:2016) 或使用 `curl` 嘗試新的 "goodbye" 端點，以確保其正常運作：

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Goodbye, world!</code></pre>

當你使用完 Caddy 後，請確保將其停止：

<pre><code class="cmd bash">caddy stop</code></pre>

你還可以使用 API 執行更多操作，包括匯出配置和對配置進行細粒度的更改（而不是更新整個配置）。請務必閱讀 [完整的 API 教學](/docs/api-tutorial) 以了解如何操作！

<a id="further-reading"></a>
## 延伸閱讀

- [完整的 API 教學](/docs/api-tutorial)
- [API 文件](/docs/api)
