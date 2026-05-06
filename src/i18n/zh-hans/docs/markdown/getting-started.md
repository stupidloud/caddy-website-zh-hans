---
title: "入门指南"
---

# 入门指南

欢迎使用 Caddy！本教程将带您快速了解 Caddy 的基本用法，并从全局层面熟悉它的工作方式。

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

如果不指定子命令，`caddy` 只会显示帮助文本。如果您偶尔忘记命令，可随时运行此命令回看。

要以守护进程方式启动 Caddy，请使用 `run` 子命令：

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">运行守护进程</aside>

这会一直阻塞，但此时并未立即对外提供服务。默认情况下，Caddy 的配置（“config”）是空的。我们可以在另一终端中使用[管理 API](/docs/api) 验证这一点：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

这**不是**您的网站：位于 localhost:2019 的管理端点用于控制 Caddy，默认情况下仅限本地主机访问。

</aside>


<aside class="complete">试用 API</aside>

我们可以通过配置让 Caddy 发挥作用。实现方法有很多种，本节我们从下一步用 `curl` 向 [/load](/docs/api#post-load) 端点发送 POST 请求开始。



## 您的首次配置

为了准备我们的请求，我们需要创建一个配置文件。从本质上讲，Caddy 的配置不过是一个 [JSON 文档](/docs/json/)。

将以下内容保存为 JSON 文件（例如 `caddy.json`）：

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

您可以不使用配置文件，但本教程中将使用配置文件说明。Caddy 的[管理 API](/docs/api) 专为其他程序或脚本设计。

</aside>


然后上传：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">为 Caddy 配置</aside>

我们可以发送另一个 GET 请求来验证 Caddy 是否应用了我们的新配置：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

请在浏览器中访问 [localhost:2015](http://localhost:2015) 测试是否正常工作，或者使用 `curl`：

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

如果您看到“*Hello, world!*”，就说明运行正常。确保配置符合预期总是有必要的，尤其是在部署到生产环境之前。

<aside class="complete">测试配置</aside>


## 您的第一个 Caddyfile

仅为了输出“Hello World”，这套步骤*还真不短*。

配置 Caddy 的另一种方法是使用 [**Caddyfile**](/docs/caddyfile)。上面用 JSON 编写的配置可以简单地表示为：

```caddy
:2015

respond "Hello, world!"
```


将其保存为当前目录下名为 `Caddyfile`（无扩展名）的文件中。

<aside class="complete">创建一个 Caddyfile</aside>

如果 Caddy 正在运行，请先停止它（按 <kbd>Ctrl</kbd>+<kbd>C</kbd>），然后运行：

<pre><code class="cmd bash">caddy adapt</code></pre>

或者，如果您将 Caddyfile 保存在其他位置，或者将其命名为其他名称， `Caddyfile`:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile</code></pre>

您会看到 JSON 输出。发生了什么变化？

我们刚刚使用了一个 [*config 适配器*](/docs/config-adapters)，将我们的 Caddyfile 转换为 Caddy 的原生 JSON 结构。

<aside class="complete">使用配置适配器</aside>

我们本可以拿该输出再发起一次 API 请求，但可以跳过这一步，因为 `caddy` 命令会替我们完成。只要当前目录存在 `Caddyfile` 且未手动指定其他配置，Caddy 会加载该文件自动适配并立即运行。

既然当前文件夹中已有 `Caddyfile` 文件，请再执行一次：

<pre><code class="cmd bash">caddy run</code></pre>

或者，如果您的 Caddyfile 位于其他位置：

<pre><code class="cmd bash">caddy run --config /path/to/Caddyfile</code></pre>

（如果文件名不是以 `Caddyfile` 开头的其他名称，请使用 `--adapter caddyfile`。）

现在您可以再次访问站点，确认服务已经恢复正常。

<aside class="complete">从初始配置开始</aside>

如您所见，有几种方法可以使用初始配置启动 Caddy：

- 当前目录下有一个名为 Caddyfile 的文件
- `--config` 选项（可选配合 `--adapter`）
- `--resume` 选项（如果先前已加载过配置）


## JSON 与 Caddyfile

您已经看到，Caddyfile 会被转换为 JSON 格式。

Caddyfile 看起来可能更易使用，但是否总用它取决于您的需求和场景。两种方式都有优缺点。

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
更高效 | 更高计算开销
有点无聊 | 有点好玩
**了解更多：[JSON 结构](/docs/json/)** | **了解更多：[Caddyfile 文档](/docs/caddyfile)**

您需要根据具体使用场景决定哪种方案最适合。

需要注意的是，JSON 和 Caddyfile（以及[任意其他受支持的配置适配器](/docs/config-adapters)）都可与 [Caddy 的 API](/docs/api) 一起使用。若要完整使用 Caddy 的全部功能与 API 特性，请使用 JSON；使用配置适配器时，若要通过 API 加载或修改配置，唯一方式是调用 [/load 端点](/docs/api#post-load)。

<aside class="complete">比较 JSON 和 Caddyfile</aside>


## API 与配置文件

<aside class="tip">

实际上，就连配置文件也会经过 Caddy 的 API 端点处理；`caddy` 命令只是在底层替您包装这些 API 调用。

</aside>


您还需要决定工作流是基于 API 还是基于 CLI（您*可以*在同一台服务器上同时使用两者，但不建议这样做：建议只保留一个可信来源）。

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

API 与配置文件工作流与配置适配器并不冲突。您可以使用 JSON 并存放在文件中，借助命令行加载；也可以在 API 中使用 Caddyfile。

但大多数人会使用 JSON+API 或 Caddyfile+CLI 的组合。

如您所见，Caddy 非常适合各种使用场景和部署方式！

<aside class="complete">比较 API 和配置文件</aside>



## 开始、停止、运行

由于 Caddy 是服务进程，它会持续运行。这意味着执行 `caddy run` 后终端将阻塞，直到进程被终止（通常按 <kbd>Ctrl</kbd>+<kbd>C</kbd>）。

虽然 `caddy run` 是最常见且通常推荐的用法（尤其用于创建系统服务时），您也可以使用 `caddy start` 在后台启动 Caddy：

<pre><code class="cmd bash">caddy start</code></pre>

这样您就可以再次使用终端了，这在某些交互式无显示器的环境中非常方便。

届时您需要手动停止该进程，因为 <kbd>Ctrl</kbd>+<kbd>C</kbd> 无法为您停止它：

<pre><code class="cmd bash">caddy stop</code></pre>

或者使用 API 的 [/stop 端点](/docs/api#post-stop)。

<aside class="complete">在后台运行</aside>


## 重新加载配置

您的服务器可以执行零停机时间的配置重载和更改。

所有用于加载或修改配置的 [API 端点](/docs/api)都支持平滑切换，不会造成服务中断。

不过，在命令行环境下，您可能会想按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 停止服务器后再重启以应用新配置。请避免这样做：停止/启动服务与配置变更是两件事，直接重启会产生中断。

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
