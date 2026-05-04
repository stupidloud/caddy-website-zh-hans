---
title: "升级至 Caddy 2"
---

升级指南
=============

Caddy 2 是一个全新的代码库，是从头开始编写，旨在改进 Caddy 1。Caddy 2 与 Caddy 1 不向后兼容。但请放心，对于大多数基本配置而言，两者差异不大。本指南将帮助您尽可能轻松地完成过渡。

本指南不会深入探讨可用的新功能——顺便说一句，这些功能真的很棒，你应该[去了解一下](/docs/getting-started)——这里的目的是让你快速上手 Caddy 2。

- [要点](#high-order-bits)
- [步骤](#steps)
- [HTTPS 和端口](#https-and-ports)
- [命令行](#command-line)
- [Caddyfile](#caddyfile)
	- [主要变更](#primary-changes)
	- [基本认证](#basicauth)
	- [浏览](#browse)
	- [错误](#errors)
	- [扩展](#ext)
	- [FastCGI](#fastcgi)
	- [gzip](#gzip)
	- [标头](#header)
	- [日志](#log)
	- [代理](#proxy)
	- [重定向](#redir)
	- [重写](#rewrite)
	- [root](#root)
	- [状态](#status)
	- [模板](#templates)
	- [tls](#tls)
- [服务文件](#service-files)
- [插件](#plugins)
- [寻求帮助](#getting-help)



<a id="high-order-bits"></a>
## 要点

- “Caddy 2”目前仍仅称为 `caddy`。我们可能会使用“Caddy 2”来明确版本，以便过渡时避免混淆。
- 大多数用户只需替换他们的 `caddy` 二进制文件及其更新后的 `Caddyfile` 配置文件（在测试确认其正常工作后）。
- 最好在开始使用 Caddy 2 时，不要带着 Caddy 1 的任何先入之见。
- 您可能无法在 v2 中完全复制您在 v1 中的特定配置。通常，这背后是有充分理由的。
- 服务器配置不再使用命令行。
- 配置时不再需要环境变量。
- 配置 Caddy 2 的主要方式是通过其 [API](/docs/api)，但也可以使用 [`caddy` 命令](/docs/command-line)。
- 您需要知道，Caddy 2 的原生配置语言是 [JSON](/docs/json/)，而 Caddyfile 只是另一个[配置适配器](/docs/config-adapters)，它会为您将配置转换为 JSON。在极度定制化或高级的用例中，可能需要使用 JSON，因为并非所有可能的配置都能通过 Caddyfile 来表达。
- Caddyfile 基本保持不变，但功能更强大；指令已发生变化。



<a id="steps"></a>
## 步骤

1. 请通过我们的[入门](/docs/getting-started)教程熟悉 Caddy 2。
2. 如果你还没做过第 1 步，请先完成它。说真的——我们无法强调掌握 Caddy 2 的基本操作有多么重要。（这样会更有趣！）
3. 请参考以下指南，迁移您的 `caddy` 命令行参数。
4. 请参考以下指南来转换您的 Caddyfile。
5. 在本地或预发布环境中测试新配置。
6. 测试、测试、再测试
7. 部署并尽情享受吧！



<a id="https-and-ports"></a>
## HTTPS 和端口

Caddy 的默认端口不再是 `:2015`。Caddy 2 的默认端口是 `:443` ，或者，如果未指定主机名/IP，则为端口 `:80`。您始终可以在配置文件中自定义端口。

[如果已知主机名或 IP 地址](/docs/automatic-https#overview)，Caddy 2 的默认协议 [*始终*](/docs/automatic-https#overview) 为 [HTTPS](/docs/automatic-https#overview)。这与 Caddy 1 不同，后者默认仅对看起来像公共域名的站点使用 HTTPS。现在，*所有* 站点都使用 HTTPS（除非您显式指定 `:80` 或 `http://`）。

IP 地址和 localhost 域名将由[本地受信任的嵌入式证书颁发机构 (CA)](/docs/automatic-https#local-https) 签发证书。所有其他域名将使用 ZeroSSL 或 Let's Encrypt。（这些设置均可配置。）

证书和 ACME 资源的存储结构已发生变更。Caddy 2 可能会为您的站点自动获取新证书；但如果您拥有大量证书，且系统未自动处理，您可以手动进行迁移。详情请参阅问题 [#2955](https://github.com/caddyserver/caddy/issues/2955) 和 [#3124](https://github.com/caddyserver/caddy/issues/3124)。



<a id="command-line"></a>
## 命令行

现在 `caddy` 命令就是 `caddy run`。

所有命令行参数均已更改。请移除这些参数；现在，所有服务器配置都包含在实际的配置文件中（通常是 Caddyfile 或 JSON）。您可以在 [JSON 结构](/docs/json/)或 [Caddyfile 全局选项](/docs/caddyfile/options)中找到所需内容，以替换 v1 版本中的大部分命令行参数。

例如，`caddy -conf ../Caddyfile` 会变成 `caddy run --config ../Caddyfile`。

与之前一样，如果您的 Caddyfile 位于当前文件夹中，Caddy 会自动找到并使用它；这种情况下，您无需使用 `--config` 标志。

信号设置基本保持不变，但不再支持 USR1 和 USR2。请改用[`caddy reload`](/docs/command-line#caddy-reload)命令或 [API](/docs/api) 来加载新配置。

运行 `caddy` 无需任何配置即可运行一个简单的文件服务器。在 Caddy 2 中，其等效配置为 [`caddy file-server`](/docs/command-line#caddy-file-server)。

环境变量已不再相关，但以下情况除外 `HOME` （以及您可能设置的任何 `XDG_*` 您设置的变量）。 `CADDYPATH` 已被[操作系统约定所取代](/docs/conventions#file-locations)。



<a id="caddyfile"></a>
## Caddyfile

[v2](/docs/caddyfile/concepts) 版 Caddyfile 与您已经熟悉的版本非常相似。您主要需要做的就是修改相关指令。

⚠️ **请务必仔细阅读新指令！** 特别是如果您的配置较为复杂，需要考虑的细节很多。这些提示能帮助您快速完成大部分迁移工作，但请务必阅读每条指令的完整文档，以便您了解升级带来的影响。当然，在将配置投入生产环境之前，请务必对其进行彻底测试。


<a id="primary-changes"></a>
### 主要变更

- 如果您要提供静态文件，则需要添加一个 [`file_server`](/docs/caddyfile/directives/file_server) [指令](/docs/caddyfile/directives/file_server)，因为 Caddy 2 默认不会自动处理此类情况。出于安全考虑，Caddy 2 默认也不会检测 MIME 类型；如果缺少 `Content-Type` 头部，您可能需要使用 [header](/docs/caddyfile/directives/header) 指令手动设置该头部。

- 在 v1 中，您只能根据请求路径过滤（或“匹配”）指令。而在 v2 中，[请求匹配](/docs/caddyfile/matchers)功能变得更加强大。任何向 HTTP 处理程序链添加中间件，或以任何方式操作 HTTP 请求/响应的 v2 指令，都会利用这一新的匹配功能。[了解更多关于 v2 请求匹配器的信息。](/docs/caddyfile/matchers)您需要了解这些内容，才能理解 v2 版的 Caddyfile。

- 虽然许多[占位符](/docs/conventions#placeholders)保持不变，但也有不少发生了变化，现在还[新增了许多占位符](/docs/modules/http#docs)，其中包括 [Caddyfile 的简写形式](/docs/caddyfile/concepts#placeholders)。

- Caddy 2 的日志均采用结构化格式，默认格式为 JSON。所有日志级别均可直接写入同一日志文件进行处理（如有需要，您也可以自定义此设置）。

- 在 Caddy 1 中，您曾通过路径前缀来匹配请求；而在 Caddy 2 中，路径匹配默认采用精确匹配。如果您想匹配类似 `/foo/` 的前缀，则需要使用 `/foo/*`。

我们将在这里列出一些最常见的 v1 指令，并说明如何将其转换为可在 v2 Caddyfile 中使用的形式。

⚠️ **即使本页面缺少某个 v1 指令，也不代表 v2 无法实现该功能！** 某些 v1 指令在 v2 中已不再需要、难以转换，或已通过其他方式实现。对于某些高级自定义功能，您可能需要查看 JSON 代码才能实现预期效果。请查阅[我们的文档](/docs/caddyfile)，找到您所需的内容！


<a id="basicauth"></a>
### 基本认证

HTTP 基本身份验证仍需通过 [`basic_auth`](/docs/caddyfile/directives/basic_auth) 指令进行配置。不过，Caddy 2 的配置不接受明文密码。您必须对密码进行哈希处理，此时 [`caddy hash-password`](/docs/command-line#caddy-hash-password) 可以提供帮助。

- **v1:**
```
basicauth /secret/ Bob hiccup
```

- **v2:**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```


<a id="browse"></a>
### 浏览

现在可以通过[`file_server`](/docs/caddyfile/directives/file_server)指令启用文件浏览功能。

- **v1:**
```
browse /subfolder/
```
- **v2:**
```caddy-d
file_server /subfolder/* browse
```


<a id="errors"></a>
### 错误

可以通过 [`handle_errors`](/docs/caddyfile/directives/handle_errors) 实现自定义错误页面。


- **v1:**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2:**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

<a id="ext"></a>
### 扩展

可以使用 [`try_files`](/docs/caddyfile/directives/try_files) 实现隐含文件扩展名。

- **v1:** `ext .html`
- **v2:** `try_files {path}.html {path}`


<a id="fastcgi"></a>
### FastCGI

假设您使用的是 PHP 服务器，那么 v2 版本的对应地址是 [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi)。

- **v1:**
```
fastcgi / localhost:9005 php
```
- **v2:**
```caddy-d
php_fastcgi localhost:9005
```

请注意， `fastcgi` v1 版本的该指令在后台执行了大量操作，包括尝试读取磁盘上的文件、重写请求，甚至进行重定向。v2 版本的 `php_fastcgi` 指令同样能为你完成这些操作，但文档中给出了其[扩展形式](/docs/caddyfile/directives/php_fastcgi#expanded-form)，如果你有不同的需求，可以对其进行修改。

在 v2 中不需要 `php` 预设，因为 `php_fastcgi` 指令默认使用 PHP。类似于 `php_fastcgi 127.0.0.1:9000 php` 会导致反向代理误以为存在一个名为 `php` 的第二个后端，从而导致连接错误。

v2 中的子指令有所不同——对于 PHP，您可能不需要使用任何子指令。


<a id="gzip"></a>
### gzip

现在，所有响应编码（包括多种压缩格式）均使用单个指令[`encode`](/docs/caddyfile/directives/encode)。

- **v1:**
```
gzip
```
- **v2:**
```caddy-d
encode gzip
```

趣闻：Caddy 2 还支持 `zstd` （但目前尚无浏览器支持）。


<a id="header"></a>
### 标头

[基本保持不变](/docs/caddyfile/directives/header)，但现在功能更强大了，因为在 v2 中它支持子字符串替换。

- **v1:**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2:**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```


<a id="log"></a>
### 日志

启用访问日志记录；在 v2 中仍可使用 [`log`](/docs/caddyfile/directives/log) 指令，但默认情况下所有日志均采用结构化格式并以 JSON 编码。

启用访问日志记录的推荐方法非常简单：

```caddy-d
log
```

该功能会将结构化日志输出到标准错误输出（stderr）。（您也可以将日志输出到文件或网络套接字；请参阅[`log`](/docs/caddyfile/directives/log)指令的文档。）

默认情况下，日志将采用[结构化](/docs/logging) JSON 格式。如果您因兼容旧版系统的原因仍需使用通用日志格式 (CLF)，可以使用 [`transform-encoder`](https://github.com/caddyserver/transform-encoder) 插件。


<a id="proxy"></a>
### 代理

v2 版本的对应地址是 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)。

值得注意的子指令变更包括 `header_upstream` 以及 `header_downstream` 已变为 `header_up` 和 `header_down`；与负载均衡相关的子指令则以 `lb_` 为前缀。

另一个显著区别在于，v2 代理默认会转发所有传入的头部信息（包括 `Host` 标头），并设置 `X-Forwarded-For` 标头。换言之，v1 的“透明”模式基本上是 v2 的默认设置（但如果您需要其他标头，如 `X-Real-IP`，则必须自行设置）。您仍然可以使用 `header_up` 子指令来覆盖或自定义 `Host` 标头。

在 v2 中，WebSocket 代理功能“开箱即用”；无需像 v1 那样“启用” WebSocket。

该 `without` 子指令已被移除，因为得益于改进的匹配器支持，在 v2 中已不再需要[重写技巧](#rewrite)。

- **v1:**
```
proxy / localhost:9005
```
- **v2:**
```caddy-d
reverse_proxy localhost:9005
```


<a id="redir"></a>
### 重定向

除关于可选状态码参数的少量细节外，[其余内容保持不变](/docs/caddyfile/directives/redir)。大多数配置无需进行任何更改。

- **v1:** `redir https://example.com{uri}`
- **v2:** `redir https://example.com{uri}`


<a id="rewrite"></a>
### 重写

请求重写（“内部重定向”）的语义已略有变化。如果您在 v1 中曾使用所谓的“重写技巧”来匹配除简单路径前缀以外的内容，那么在 v2 中这已完全没有必要。

[新的](/docs/caddyfile/directives/rewrite) [`rewrite` 指令](/docs/caddyfile/directives/rewrite)非常简单却又非常强大，因为其大部分复杂性都由 v2 中的[匹配器](/docs/caddyfile/matchers)来处理：

- **v1:**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2:**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

请注意，我们只需使用 Caddy 2 惯用的[匹配器标记](/docs/caddyfile/matchers)；对于该指令而言，这已不再是特例。

首先移除所有重写技巧；将其替换为[命名匹配器](/docs/caddyfile/concepts#named-matchers)。评估每个 v1 `rewrite` 进行评估，以确定其在 v2 中是否真的必要。提示：一个使用 `rewrite` 来添加路径前缀，随后再使用 `proxy` 使用 `without` 来移除该前缀，这属于重写技巧，可以予以删除。

您可能会发现新的 [`route`](/docs/caddyfile/directives/route) 和 [`handle`](/docs/caddyfile/directives/handle) 指令非常有用，它们能让您更好地控制高级路由逻辑。


<a id="root"></a>
### root

[保持不变](/docs/caddyfile/directives/root)。

如果需要提供静态文件，请记得添加[`file_server`指令](/docs/caddyfile/directives/file_server)，因为 Caddy 2 默认不会启用此功能，而 v1 版本则始终默认启用。


<a id="status"></a>
### 状态

v2 版本的对应方法是 [`respond`](/docs/caddyfile/directives/respond)，它也可以写入响应正文。

- **v1:**
```
status 404 /secrets/
```
- **v2:**
```caddy-d
respond /secrets/* 404
```


<a id="templates"></a>
### 模板

[`templates`](/docs/caddyfile/directives/templates) 指令的整体语法保持不变，但具体的模板操作/函数已有所不同，且得到了显著改进。例如，模板现在能够包含文件、渲染 Markdown、发起内部子请求、解析前置信息等等！

有关新功能的详细信息，[请参阅文档](/docs/modules/http.handlers.templates)。

- **v1:** `templates`
- **v2:** `templates`


<a id="tls"></a>
### TLS

[`tls`](/docs/caddyfile/directives/tls) 指令的基本原理并未改变，例如指定您自己的证书和密钥：

- **v1:** `tls cert.pem key.pem`
- **v2:** `tls cert.pem key.pem`

但 Caddy 的[自动 HTTPS 逻辑](/docs/automatic-https)确实已经发生了变化，请务必注意这一点！

密码套件的名称也发生了变化。

Caddy 2 中的一种常见配置是使用 `tls internal` 来为一个非 `localhost` 或 IP 地址的开发主机名提供本地受信任的证书。

大多数网站根本不需要这个指令。


<a id="service-files"></a>
## 服务文件

我们建议在部署 Caddy 时使用[我们的官方 systemd 服务文件之一](/docs/running#linux-service)。

如果您需要自定义服务文件，请以我们的文件为基础。这些文件经过精心调校，其设置均有充分的理由！如有需要，请务必根据实际情况进行调整。


<a id="plugins"></a>
## 插件

为 v1 编写的插件并不自动兼容 v2。许多 v1 插件在 v2 中甚至已不再需要。另一方面，v2 的可扩展性和灵活性远胜于 v1！

如果你想为 Caddy 2 编写插件，[请学习如何编写 Caddy 模块](/docs/extending-caddy)。


### 使用插件构建 Caddy 2

您可以在[交互式下载页面](/download)下载包含插件的 Caddy 2。或者，您也可以使用 `xcaddy` 并选择要包含的插件。 `xcaddy` 该工具会自动执行 Caddy 的 [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) 文件中的指令。


<a id="getting-help"></a>
## 获取帮助

如果您在配置 Caddy 时遇到困难，请先浏览我们网站上的文档。请花点时间尝试新功能并了解其工作原理——v2 在许多方面与 v1 截然不同（但使用起来也依然非常熟悉）！

如果您仍然需要帮助，欢迎加入[我们的社区](https://caddy.community)！您会发现，帮助他人也是帮助自己的最佳方式。
