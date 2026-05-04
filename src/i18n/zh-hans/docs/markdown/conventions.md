---
title: "惯例"
---

<a id="conventions"></a>
# 惯例

Caddy 生态系统遵循一些约定，以确保整个平台体验的一致性和直观性。
- [网络地址](#network-addresses)
- [占位符](#placeholders)
- [文件位置](#file-locations)
  - [数据目录](#data-directory)
  - [配置目录](#configuration-directory)
- [时长](#durations)



<a id="network-addresses"></a>
## 网络地址

在指定要拨号或绑定的网络地址时，Caddy 接受以下格式的字符串：

```
network/address
```

网络部分是可选的（默认为 `tcp`），其格式须为 [Go 语言的](https://pkg.go.dev/net#Dial) [`net.Dial`](https://pkg.go.dev/net#Dial) [函数](https://pkg.go.dev/net#Dial)所识别的任何形式。若指定了网络部分，则必须使用单个正斜杠 `/` 必须将网络部分与地址部分分隔开。

该网络可以是以下任何一种；后缀为 `4` 或 `6` 分别仅支持 IPv4 或 IPv6：

- TCP： `tcp`, `tcp4`, `tcp6`
- UDP： `udp`, `udp4`, `udp6`
- IP： `ip`, `ip4`, `ip6`
- Unix： `unix`, `unixgram`, `unixpacket`

地址部分可以采用以下任何一种形式：

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/path/to/unix/socket`
- `/path/to/unix/socket|0200`

主机可以是任何主机名、可解析的域名或 IP 地址。

对于 IPv6 地址，该地址必须用方括号括起来 `[]`。区域标识符（以 `%`）是可选的（通常用于链路本地地址）。

端口可以是一个单一值（`:8080`）或包含起止点的范围（`:8080-8085`）。端口范围将被转换为单个地址。并非所有配置字段都支持端口范围。特殊端口 `:0` 表示任何可用端口。

只有在使用 `unix*` 网络类型时才被接受。用于分隔网络和地址的正斜杠不被视为路径的一部分。

当将 Unix 套接字用作绑定地址时，您可以在路径后可选地指定文件权限模式，并用竖线分隔 `|`。默认值为 `0200` （八进制），即 `u=w,g=,o=` (符号模式)。开头的 `0` 是可选的。

有效示例：

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//path/to/socket
unix//path/to/socket|0200
```

<aside class="tip">

Caddy 的网络地址并非 URL。URL 将 [OSI 模型](https://en.wikipedia.org/wiki/OSI_model#Layer_architecture)的底层和高层结合在一起 <a href="https://en.wikipedia.org/wiki/OSI_model#Layer_architecture"><img src="/old/resources/images/external-link.svg" class="external-link"></a>，但 Caddy 通常会独立于特定应用程序使用网络地址，因此将两者结合会带来问题。 在 Caddy 中，网络地址精确指代可在 L3-L5 层进行连接或绑定的资源，而 URL 则涵盖 L3-L7 层，范围过于广泛。网络地址要求主机名、端口和路径相互独立，但 URL 则无此限制。网络地址有时支持端口范围，而 URL 则不支持。

</aside>




<a id="placeholders"></a>
## 占位符

Caddy 的配置支持使用 *占位符*。使用占位符是一种将动态值注入静态配置的简便方法。

<aside class="tip">

占位符的概念与其他软件中的变量类似。例如，<a href="https://nginx.org/en/docs/varindex.html">nginx 中的变量 <img src="/old/resources/images/external-link.svg" class="external-link"></a> 类似于 `$uri` 以及 `$document_root`，而 Caddy 的对应形式则是 [`{http.request.uri}`](/docs/json/apps/http/#docs) 和 [`{http.vars.root}`](/docs/caddyfile/directives/root)。

</aside>


占位符两侧由大括号包围 `{ }` ，并在其中包含标识符，例如： `{foo.bar}`。可以通过转义开头的占位符大括号 `\{like.this}` 以防止被替换。占位符标识符通常使用点分隔符进行命名空间划分，以避免跨模块冲突。

可用的占位符取决于上下文。并非所有占位符在配置的各个部分都可用。例如，[HTTP 应用程序设置的占位符](/docs/json/apps/http/#docs)仅在配置中与处理 HTTP 请求相关的区域中可用。当请求通过 [`reverse_proxy` 处理程序](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs)时，该处理程序会设置几个代理特有的占位符。这些占位符既可在代理过程中引用，也可在之后引用（例如在 `handle_response`），例如在设置响应头或丰富访问日志时。

以下占位符始终可用（全局）：

占位符 | 描述
------------|-------------
`{env.*}` | 环境变量；示例： `{env.HOME}`
`{file.*}` | 文件中的内容；示例： `{file./path/to/secret.txt}`
`{system.hostname}` | 系统的本地主机名
`{system.slash}` | 系统的文件路径分隔符
`{system.os}` | 系统的操作系统
`{system.arch}` | 系统架构
`{system.wd}` | 当前工作目录
`{time.now}` | 当前时间，以 Go Time 结构体表示
`{time.now.http}` | 当前时间，采用 [HTTP ](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified)头中使用的格式 <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified"><img src="/old/resources/images/external-link.svg" class="external-link"></a>
`{time.now.unix}` | 当前时间（以秒为单位的 Unix 时间戳）
`{time.now.unix_ms}` | 当前时间（以毫秒为单位的 Unix 时间戳）
`{time.now.common_log}` | 当前时间（通用日志格式）
`{time.now.year}` | 当前年份（YYYY格式）

并非所有配置字段都支持占位符，但在大多数情况下，您预期的字段都会支持。这些字段必须已明确添加了对占位符的支持。插件作者可以[阅读本文](/docs/extending-caddy/placeholders)，了解如何在自己的模块中添加对占位符的支持。




<a id="file-locations"></a>
## 文件位置

本节介绍了各种文件的位置。此处描述的文件和目录路径仅为默认设置；部分路径可以被覆盖。

<a id="your-config-files"></a>
### 您的配置文件

并没有一个固定的、常规的位置来存放您的配置文件。请将它们放在您认为最合适的地方。

<aside class="tip">

唯一的例外可能是当前工作目录下名为 `Caddyfile` ，如果未指定其他配置文件，`caddy` 命令会出于方便而尝试读取该文件。

</aside>


随发行版附带默认配置文件的软件包，应说明该配置文件的位置，即使这对软件包或发行版的维护者来说显而易见。对于大多数 Linux 系统，Caddyfile 通常位于 `/etc/caddy/Caddyfile`.


<a id="data-directory"></a>
### 数据目录

Caddy 将 TLS 证书和其他重要资产存储在一个数据目录中，该目录由[配置的存储模块](/docs/json/storage/)提供支持（默认：本地文件系统）。

如果 `XDG_DATA_HOME` 环境变量已设置，则 `$XDG_DATA_HOME/caddy`.

否则，其路径会因平台而异，并遵循操作系统的规范：

操作系统 | 数据目录路径
---|---------------------
**Linux、BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (或 `/sdcard/caddy`)

所有其他操作系统均采用 Linux/BSD 目录路径。

**数据目录绝不能被视为缓存。** 其内容 **并非** 临时数据，也并非仅为提升性能而存在。Caddy 会将 TLS 证书、私钥、OCSP 固定项及其他必要信息存储在数据目录中。在未充分了解其影响之前，不应清空该目录。

该目录必须是持久的，并且Caddy能够对其进行写入。


<a id="configuration-directory"></a>
### 配置目录

Caddy 可能会将某些配置存储在此处。最值得注意的是，它会将最后一个活跃配置（默认情况下）持久化到此文件夹，以便日后通过 [`caddy run --resume`](/docs/command-line#caddy-run) 命令轻松恢复。

<aside class="tip">

配置目录*并非*您存放[配置文件](#your-config-files)的地方。（不过，您也可以将文件存放在那里。）

</aside>


如果 `XDG_CONFIG_HOME` 环境变量已设置，则 `$XDG_CONFIG_HOME/caddy`.

否则，其路径会因平台而异，并遵循操作系统的规范：


操作系统 | 配置目录路径
---|---------------------
**Linux、BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

所有其他操作系统均采用 Linux/BSD 目录路径。

该目录必须是持久的，并且Caddy能够对其进行写入。


<a id="durations"></a>
## 时长

时长字符串在 Caddy 的配置中被广泛使用。它们采用与 [Go 语言中 `time.ParseDuration` 语法](https://golang.org/pkg/time/#ParseDuration)相同的格式，只不过还可以使用 `d` 表示天（为简化起见，我们假设1天=24小时）。有效的单位包括：

- `ns` (纳秒)
- `us`/`µs` (微秒)
- `ms` (毫秒)
- `s` （第二）
- `m` (分钟)
- `h` (小时)
- `d` (天)

示例：

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

在 [JSON 配置](/docs/json/)中，时长值也可以是表示纳秒的整数。
