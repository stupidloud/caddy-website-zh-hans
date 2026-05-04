---
title: "Caddyfile 教程"
---

# Caddyfile 教程

本教程将向您介绍 [HTTP Caddyfile](/docs/caddyfile) 的基础知识，帮助您快速轻松地创建美观且功能完善的站点配置。

**目标：**
- 🔲 首个网站
- 🔲 静态文件服务器
- 🔲 模板
- 🔲 压缩
- 🔲 多个站点
- 🔲 匹配器
- 🔲 环境变量
- 🔲 注释

**先决条件：**
- 基本的终端/命令行操作技能
- 基本的文本编辑技能
- `caddy` 在您的 PATH 环境变量中

---

创建一个名为 `Caddyfile` （无扩展名）。

首先，您应输入您网站的[地址](/docs/caddyfile/concepts#addresses)：

```caddy
localhost
```

<aside class="tip">

如果 HTTP 和 HTTPS 端口（分别是 80 和 443）在您的操作系统上属于受限端口，您需要以提升权限的方式运行，或者使用更高的端口。要使用更高的端口，只需将地址修改为类似 `localhost:2015` 这样的形式，并通过 Caddyfile 中的 [http_port](/docs/caddyfile/options) 选项修改 HTTP 端口。

</aside>


然后按回车键，输入你希望它执行的操作。在本教程中，请将你的 Caddyfile 设置为如下所示：

```caddy
localhost

respond "Hello, world!"
```

保存该文件并运行 Caddy（由于这是个培训教程，我们将使用 `--watch` 参数，这样对 Caddyfile 的修改会自动应用）：

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

如果遇到权限错误，请尝试在地址中使用更高的端口（例如 `localhost:2015`）并[更改 HTTP 端口](/docs/caddyfile/options)，或者以管理员权限运行。

</aside>


第一次使用时，系统会要求您输入密码。这是为了让 Caddy 能通过 HTTPS 提供您的网站服务。

<aside class="tip">

只要主机名或 IP 地址是网站地址的一部分，Caddy 默认会通过 HTTPS 提供所有网站的服务。若要显式禁用自动 HTTPS，只需在地址前加上 `http://`。

</aside>


<aside class="complete">第一个网站</aside>

在浏览器中打开 [localhost](https://localhost)，查看您的 Web 服务器是否正常运行，并已启用 HTTPS！

<aside class="tip">
	如果第一次出现证书错误，您可能需要重启浏览器。
</aside>

这没什么特别的，所以让我们把静态响应改为启用了目录列表功能的[文件服务器](/docs/caddyfile/directives/file_server)：

```caddy
localhost

file_server browse
```

保存您的 Caddyfile，然后刷新浏览器标签页。此时您应该会看到文件列表，或者如果当前目录中存在索引文件，则会看到一个 HTML 页面。

<aside class="complete">静态文件服务器</aside>

<a id="adding-functionality"></a>
## 添加功能

让我们用文件服务器做点有趣的事：提供一个模板页面。创建一个新文件，并将以下内容粘贴进去：

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Caddy tutorial</title>
	</head>
	<body>
		Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

将此文件保存为 `caddy.html`，放在当前目录中，并在浏览器中加载：[https://localhost/caddy.html](https://localhost/caddy.html)

输出结果是：

```
Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

等一下。我们应该能看到今天的日期。为什么没成功？那是因为服务器尚未配置好以解析模板！解决起来很简单，只需在 Caddyfile 中添加一行，使其看起来像这样：

```caddy
localhost

templates
file_server browse
```

保存后，重新加载浏览器标签页。您应该会看到：

```
Page loaded at: {{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

借助 Caddy 的[模板模块](/docs/modules/http.handlers.templates)，您可以对静态文件进行许多有用的操作，例如包含其他 HTML 文件、发起子请求、设置响应头、处理数据结构等等！

<aside class="complete">模板</aside>

使用快速且现代的压缩算法对响应进行压缩是一种良好的实践。让我们通过[`encode`](/docs/caddyfile/directives/encode)指令启用Gzip和Zstandard支持：

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">压缩</aside>

这就是搭建一个功能较为完善、可投入生产的网站的基本流程！

当您准备好启用[自动 HTTPS](/docs/automatic-https) 时，只需将教程中的网站地址（`localhost` 在我们的教程中）替换为您的域名。更多信息请参阅我们的 [HTTPS 快速入门指南](/docs/quick-starts/https)。

<a id="multiple-sites"></a>
## 多个站点

在当前的 Caddyfile 中，我们只能定义一个站点！只有第一行可以是该站点的地址，而文件中的其余部分必须都是针对该站点的指令。

但这很容易实现，这样我们就能添加更多网站了！

迄今为止的 Caddyfile：

```caddy
localhost

encode
templates
file_server browse
```

等同于这个：

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

不过第二个方案允许我们添加更多站点。

通过将站点块用大括号包裹 `{ }` ，我们便可以在同一个 Caddyfile 中定义多个不同的站点。

例如：

```caddy
:8080 {
	respond "I am 8080"
}

:8081 {
	respond "I am 8081"
}
```

将站点块用大括号包围时，大括号外部仅显示[地址](/docs/caddyfile/concepts#addresses)，内部仅显示[指令](/docs/caddyfile/directives)。

对于使用相同配置的多个站点，您可以添加更多地址，例如：

```caddy
:8080, :8081 {
	...
}
```

然后，您可以定义任意数量的不同站点，只要每个地址都是唯一的即可。

<aside class="complete">多个站点</aside>


<a id="matchers"></a>
## 匹配器

我们可能希望仅对某些请求应用某些指令。例如，假设我们既想部署文件服务器，又想部署反向代理，但显然不可能对每个请求都同时执行这两项操作！要么由文件服务器返回静态文件，要么由反向代理将请求转发给后端服务器，并返回其响应。

此配置无法按预期工作（`reverse_proxy` 由于[指令](/docs/caddyfile/directives#directive-order)的[顺序](/docs/caddyfile/directives#directive-order)，将具有更高优先级）：

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

实际上，我们可能只想对 API 请求使用反向代理，即基础路径为 `/api/`的请求。通过添加一个[匹配器令牌](/docs/caddyfile/matchers#syntax)即可轻松实现：

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

好了，现在反向代理将优先处理所有以 `/api/` 开头的请求。

刚刚添加的 `/api/*` 部分被称为**匹配器标记**。你可以通过它判断其是否以正斜杠 `/` 开头，并且紧跟在指令之后（但为了确认，你也可以随时查阅该指令[的文档](/docs/caddyfile/directives)）。

匹配器非常强大。您可以声明命名匹配器，并像这样使用它们 `@name` ，从而匹配的不仅仅是请求路径！在继续之前，请花一点时间[进一步了解匹配器](/docs/caddyfile/matchers)！

<aside class="complete">匹配器</aside>

<a id="environment-variables"></a>
## 环境变量

Caddyfile 适配器允许在解析 Caddyfile 之前替换[环境变量](/docs/caddyfile/concepts#environment-variables)。

首先，设置一个环境变量（在运行 Caddy 的同一终端中）：

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

然后你可以在 Caddyfile 中这样使用它：

```caddy
{$SITE_ADDRESS}

file_server
```

在解析 Caddyfile 之前，它将被展开为：

```caddy
localhost:9055

file_server
```

您可以在 Caddyfile 的任何位置使用环境变量，且令牌数量不限。

<aside class="complete">环境变量</aside>


<a id="comments"></a>
## 注释

最后还有一点，相信你会觉得非常有用：如果你想在 Caddyfile 中添加注释或备注，可以使用以 `#`:

```caddy
# this starts a comment
```

<aside class="complete">注释</aside>

<a id="further-reading"></a>
## 延伸阅读

- [Caddyfile 概念](/docs/caddyfile/concepts)
- [指令](/docs/caddyfile/directives)
- [常见模式](/docs/caddyfile/patterns)
