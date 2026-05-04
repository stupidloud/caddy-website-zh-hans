---
title: "API 教程"
---

# API 教程

本教程将向您展示如何使用 Caddy 的[管理 API](/docs/api)，该 [API](/docs/api) 支持通过编程方式实现自动化操作。

**目标：**
- 🔲 运行守护进程
- 🔲 为 Caddy 配置
- 🔲 测试配置
- 🔲 替换当前配置
- 🔲 Traverse 配置
- 🔲 使用 `@id` 标签

**先决条件：**
- 基本的终端/命令行操作技能
- 具备基本的 JSON 经验
- `caddy` 以及 `curl` 并将其添加到 PATH 环境变量中

---

要启动 Caddy 守护进程，请使用 `run` 子命令：

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">运行守护进程</aside>

这会一直阻塞，但它到底在做什么？目前……什么也没做。默认情况下，Caddy 的配置（“config”）是空的。我们可以在另一个终端中使用[管理 API](/docs/api) 来验证这一点：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

我们可以通过配置来让 Caddy 发挥作用。实现这一目标的一种方法是向 [/load](/docs/api#post-load) 端点发送一个 POST 请求。就像任何 HTTP 请求一样，实现方式多种多样，但在本教程中，我们将使用 `curl`.

## 您的首次配置

为了准备我们的请求，我们需要创建一个配置文件。Caddy 的配置文件只是一个 [JSON 文档](/docs/json/)（或[任何可以转换为 JSON 的格式](/docs/config-adapters)）。

<aside class="tip">
	无需配置文件。配置 API 始终支持不使用文件直接调用，这在自动化操作时非常方便。本教程使用文件，是因为手动编辑起来更方便。
</aside>

将此内容保存为 JSON 文件：

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

然后上传：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	请务必不要忘记在文件名前加上 @；这会告诉 curl 你要发送一个文件。
</aside>

<aside class="complete">为 Caddy 配置</aside>

我们可以通过另一个 GET 请求验证 Caddy 是否应用了我们的新配置：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

请在浏览器中访问 [localhost:2015](http://localhost:2015) 或使用 `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">测试配置</aside>

如果你看到“*Hello, world!*”，那么恭喜——它运行正常了！确保配置符合预期总是明智之举，尤其是在部署到生产环境之前。

让我们把欢迎信息从“Hello world!”改成更有激励作用的句子：“我能应对困难。”在配置文件中进行此修改，使处理程序对象现在看起来像这样：

```json
{
	"handler": "static_response",
	"body": "I can do hard things."
}
```

保存配置文件，然后再次执行相同的 POST 请求以更新 Caddy 的当前配置：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">替换当前配置</aside>

为了保险起见，请确认配置是否已更新：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

请在浏览器中刷新页面（或再次运行 `curl` ），你将看到一条鼓舞人心的信息！


## 配置遍历

与其为了一个微小的改动就上传整个配置文件，不如利用 Caddy API 的强大功能，在完全不触碰配置文件的情况下完成修改。

<aside class="tip">
	像上面那样通过替换整个配置文件来对生产服务器进行微调可能会很危险；这就像获得了文件系统的 root 权限一样。Caddy 的 API 允许您限制更改范围，以确保配置的其他部分不会被意外修改。
</aside>

利用请求 URI 的路径，我们可以遍历配置结构，并仅更新消息字符串（如果内容被截断，请务必向右滚动）：

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Work smarter, not harder."'
</code></pre>


<aside class="tip">

每次您通过 API 修改配置时，Caddy 都会保存一份新配置的副本，以便您[稍后](/docs/command-line#caddy-run)可以 [**--resume** 恢复它](/docs/command-line#caddy-run)！

</aside>


您可以通过一个类似的 GET 请求来验证是否成功，例如：

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

你应该看到：

```json
[{"handle":[{"body":"Work smarter, not harder.","handler":"static_response"}]}]
```


<aside class="tip">

您可以使用 <a href="https://stedolan.github.io/jq/">`jq` 命令 <img src="/old/resources/images/external-link.svg" class="external-link"></a> 来美化 JSON 输出：**`curl ... | jq`**

</aside>


<aside class="complete">Traverse 配置</aside>

**重要提示：** 这一点应该不言自明，但一旦您使用 API 进行了配置文件中原本不存在的更改，您的配置文件就会过时。有几种方法可以处理这种情况：

- 使用 `--resume` [caddy run](/docs/command-line#caddy-run) 命令的 -c 选项来使用上次活动的配置。
- 不要将配置文件的使用与通过 API 进行的更改混为一谈；应确保只有一个权威来源。
- 通过后续的 GET 请求[导出 Caddy 的新配置](/docs/api#get-configpath)（相比前两个选项，此方法不那么推荐）。



## 使用 `@id` 在 JSON 中

配置遍历确实很有用，但路径是不是有点长？

我们可以给处理程序对象添加一个[`@id`标签](/docs/api#using-id-in-json)，以便更方便地访问它：

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

这为我们的处理程序对象添加了一个属性： `"@id": "msg"`，因此现在看起来像这样：

```json
{
	"@id": "msg",
	"body": "Work smarter, not harder.",
	"handler": "static_response"
}
```


<aside class="tip">

**@id** 标签可以出现在任何对象中，并可以包含任何基本数据类型（通常是字符串）。[了解更多](/docs/api#using-id-in-json)

</aside>


然后我们就可以直接访问它：

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

现在，我们可以使用更短的路径来更改消息：

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Some shortcuts are good."'
</code></pre>

再检查一遍：

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete">使用 `@id` 标签</aside>
