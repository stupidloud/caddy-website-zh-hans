---
title: "API 快速入门"
---

# API 快速入门

**先决条件：**
- 基本的终端/命令行操作技能
- `caddy` 并 `curl` 在您的 PATH 环境变量中

---

首次启动 Caddy：

<pre><code class="cmd bash">caddy start</code></pre>

Caddy 目前处于空闲状态（配置为空）。请使用 `curl` 为其配置一个简单的 JSON，如下所示：

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

使用[Heredoc](https://en.wikipedia.org/wiki/Here_document#Unix_shells)传递 POST 请求正文可能会比较繁琐，因此如果您更倾向于使用文件，请将 JSON 保存到一个名为 `caddy.json` 的文件中，然后改用以下命令：

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

现在在浏览器中访问 [localhost:2015](http://localhost:2015) 或使用 `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

我们还可以使用此 JSON 在不同的接口上定义多个站点：

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

更新您的 JSON 文件，然后再次发送 API 请求。

[在浏览器中](http://localhost:2016)或使用 `curl` 来确保其正常运行：

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Goodbye, world!</code></pre>

使用完 Caddy 后，请务必将其停止：

<pre><code class="cmd bash">caddy stop</code></pre>

借助该 API，您还可以进行更多操作，包括导出配置以及对配置进行精细调整（而非更新整个配置）。请务必阅读[完整的 API 教程](/docs/api-tutorial)，了解具体操作方法！

## 延伸阅读

- [完整的 API 教程](/docs/api-tutorial)
- [API 文档](/docs/api)
