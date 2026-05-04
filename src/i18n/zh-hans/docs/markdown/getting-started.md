---
title: "入门指南"
---

# 入门指南

欢迎使用 Caddy！本教程将带您了解 Caddy 的基本用法，并帮助您从宏观层面熟悉该工具。

**目标：**
- 🔲 运行守护进程
- 🔲 试用 API
- 🔲 为 Caddy 配置
- 🔲 测试配置
- 🔲 创建一个 Caddyfile
- 🔲 使用配置适配器
- 🔲 从初始配置开始
- 🔲 比较 JSON 和 Caddyfile
- 🔲 比较 API 和配置文件
- 🔲 在后台运行
- 🔲 零停机时间配置重载

**先决条件：**
- 基本的终端/命令行操作技能
- 基本的文本编辑技能
- `caddy` 以及 `curl` 并将其添加到 PATH 环境变量中

---

**如果您是通过包管理器[安装的 Caddy](/docs/install)，它可能已经作为服务在运行。如果是这样，请在开始本教程之前先停止该服务。**

我们先运行一下：

<pre><code class="cmd bash">caddy</code></pre>

哎呀；如果不指定子命令， `caddy` 命令只会显示帮助文本。当你忘记该怎么做时，随时可以使用它。

要以守护进程方式启动 Caddy，请使用 `run` 子命令：

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">运行守护进程</aside>

这会一直阻塞，但它到底在做什么？目前……什么也没做。默认情况下，Caddy 的配置（“config”）是空的。我们可以在另一个终端中使用[管理 API](/docs/api) 来验证这一点：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

这**不是**您的网站：位于 localhost:2019 的管理端点用于控制 Caddy，默认情况下仅限本地主机访问。

</aside>


<aside class="complete">试用 API</aside>

我们可以通过配置来让 Caddy 发挥作用。实现方法有很多种，但我们将从向 [/load](/docs/api#post-load) 端点发送一个 POST 请求开始，具体方法将在 `curl` 在下一节中。



## 您的首次配置

为了准备我们的请求，我们需要创建一个配置文件。从本质上讲，Caddy 的配置不过是一个 [JSON 文档](/docs/json/)。

将此内容保存为 JSON 文件（例如 `caddy.json`):

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

<aside class="tip">

您不必使用配置文件，但在本教程中我们会使用。Caddy 的[管理 API](/docs/api) 专为其他程序或脚本设计。

</aside>


然后上传：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">为 Caddy 配置</aside>

我们可以发送另一个 GET 请求来验证 Caddy 是否应用了我们的新配置：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

请在浏览器中访问 [localhost:2015](http://localhost:2015) 测试是否正常工作，或者使用 `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

如果你看到“*Hello, world!*”，那么恭喜——它运行正常了！确保配置符合预期总是明智之举，尤其是在部署到生产环境之前。

<aside class="complete">测试配置</aside>


## 你的第一个 Caddyfile

光是为了实现“Hello World”，这工作量*还真挺大的*。

配置 Caddy 的另一种方法是使用 [**Caddyfile**](/docs/caddyfile)。上面用 JSON 编写的配置可以简单地表示为：

```caddy
:2015

respond "Hello, world!"
```


将其保存为当前目录下名为 `Caddyfile` （无扩展名）的文件中。

<aside class="complete">创建一个 Caddyfile</aside>

如果 Caddy 正在运行，请先停止它（按 <kbd>Ctrl</kbd>+<kbd>C</kbd>），然后运行：

<pre><code class="cmd bash">caddy adapt</code></pre>

或者，如果您将 Caddyfile 保存在其他位置，或者将其命名为其他名称， `Caddyfile`:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile</code></pre>

你会看到 JSON 输出！这是怎么回事？

我们刚刚使用了一个 [*config 适配器*](/docs/config-adapters)，将我们的 Caddyfile 转换为 Caddy 的原生 JSON 结构。

<aside class="complete">使用配置适配器</aside>

虽然我们可以将该输出结果用于发起另一个 API 请求，但我们可以跳过所有这些步骤，因为 `caddy` 该命令可以代劳。如果当前目录下存在名为 Caddyfile 的文件，且未指定其他配置，Caddy 会加载该文件，自动进行适配，并立即运行。

既然当前文件夹中已经有一个 Caddyfile 文件，让我们再次执行 `caddy run` ：

<pre><code class="cmd bash">caddy run</code></pre>

或者，如果您的 Caddyfile 位于其他位置：

<pre><code class="cmd bash">caddy run --config /path/to/Caddyfile</code></pre>

（如果文件名不是以“Caddyfile”开头的其他名称，则需要指定 `--adapter caddyfile`.)

现在您可以尝试重新加载网站，您会发现它已经可以正常运行了！

<aside class="complete">从初始配置开始</aside>

如您所见，有几种方法可以使用初始配置启动 Caddy：

- 当前目录下有一个名为 Caddyfile 的文件
- `--config` flag（可选地配合 `--adapter` 标志）
- 该 `--resume` 标志（如果之前已加载过配置）


## JSON 与 Caddyfile

现在你已经知道，Caddyfile 只是被转换成了 JSON 格式。

Caddyfile 似乎比 JSON 更简单，但你应该总是使用它吗？这两种方法各有优缺点。答案取决于你的需求和使用场景。

JSON | Caddyfile
-----|----------
轻松生成 | 轻松手工制作
易于编程 | 难以自动化
极具表现力 | 具有一定表现力
Caddy 的全部功能 | Caddy 的大部分功能
允许配置文件遍历 | 无法在 Caddyfile 内进行遍历
仅修改部分配置 | 仅修改全部配置
可导出 | 不可导出
兼容所有 API 端点 | 兼容部分 API 端点
自动生成的文档 | 手动编写的文档
无处不在 | 小众
更高效 | 更强大的计算能力
有点无聊 | 有点好玩
**了解更多：[JSON 结构](/docs/json/)** | **了解更多：[Caddyfile 文档](/docs/caddyfile)**

您需要根据具体使用场景决定哪种方案最适合。

需要注意的是，JSON 和 Caddyfile（以及[任何其他受支持的配置适配器](/docs/config-adapters)）均可与 [Caddy 的 API](/docs/api) 配合使用。不过，若使用 JSON，您将能够充分利用 Caddy 的全部功能和 API 特性。如果使用配置适配器，通过 API 加载或修改配置的唯一方法是使用 [/load 端点](/docs/api#post-load)。

<aside class="complete">比较 JSON 和 Caddyfile</aside>


## API 与配置文件

<aside class="tip">

实际上，就连配置文件也会通过 Caddy 的 API 端点进行处理； `caddy` 该命令只是为你封装了这些 API 调用。

</aside>


您还需要决定工作流是基于 API 还是基于 CLI。（您*可以*在同一台服务器上同时使用 API 和配置文件，但我们不建议这样做：最好只保留一个权威数据源。）

API | 配置文件
----|-------------
通过 HTTP 请求修改配置 | 通过 shell 命令修改配置
易于扩展 | 难以扩展
手动操作困难 | 手动操作简单
真的很有趣 | 也很有趣
**了解更多：[API 教程](/docs/api-tutorial)** | **了解更多：[Caddyfile 教程](/docs/caddyfile-tutorial)**

<aside class="tip">
	只要使用合适的工具（例如任何 REST 客户端应用程序），完全可以通过 API 手动管理服务器的配置。
</aside>

选择 API 或配置文件工作流与配置适配器的使用互不冲突：您可以使用 JSON，但将其存储在文件中并使用命令行界面；反之，您也可以在 API 中使用 Caddyfile。

但大多数人会使用 JSON+API 或 Caddyfile+CLI 的组合。

如您所见，Caddy 非常适合各种使用场景和部署方式！

<aside class="complete">比较 API 和配置文件</aside>



## 开始、停止、运行

由于 Caddy 是一个服务器，它会无限期运行。这意味着在执行 `caddy run` ，终端将保持阻塞状态，直到该进程被终止（通常使用 <kbd>Ctrl</kbd>+<kbd>C</kbd>）。

虽然 `caddy run` 虽然这是最常见且通常推荐的做法（尤其是创建系统服务时！），但你也可以使用 `caddy start` 来启动 Caddy 并使其在后台运行：

<pre><code class="cmd bash">caddy start</code></pre>

这样您就可以再次使用终端了，这在某些交互式无显示器的环境中非常方便。

届时您需要手动停止该进程，因为 <kbd>Ctrl</kbd>+<kbd>C</kbd> 无法为您停止它：

<pre><code class="cmd bash">caddy stop</code></pre>

或者使用 API 的 [/stop 端点](/docs/api#post-stop)。

<aside class="complete">在后台运行</aside>


## 重新加载配置

您的服务器可以执行零停机时间的配置重新加载/更改。

所有用于加载或修改配置的 [API 端点](/docs/api)均能平滑过渡，且不会造成任何停机。

不过，在使用命令行时，您可能会想通过按下 <kbd>Ctrl</kbd>+<kbd>C</kbd> 来停止服务器，然后重新启动它以应用新配置。请不要这样做：停止和启动服务器与配置更改是相互独立的操作，这样做会导致服务中断。

<aside class="tip">
	停止服务器将导致服务器下线。
</aside>

相反，请使用 [`caddy reload`](/docs/command-line#caddy-reload) 命令来平滑地更改配置：

<pre><code class="cmd bash">caddy reload</code></pre>

实际上，这只是在后台调用 API。它会加载您的配置文件，并在必要时将其转换为 JSON 格式，然后在不造成服务中断的情况下平滑地替换当前的配置。

如果加载新配置时出现任何错误，Caddy 将回滚到上一个有效的配置。

<aside class="tip">
	从技术上讲，新配置是在旧配置停止之前启动的，因此有一小段时间，两个配置都会同时运行！如果新配置失败，它会因错误而中止，而旧配置则只是没有停止。
</aside>

<aside class="complete">零停机时间配置重载</aside>
