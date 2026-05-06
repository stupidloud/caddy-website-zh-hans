---
title: 约定
---

<a id="conventions"></a>
# 约定

Caddy 生态遵循一组约定，以使整个平台的行为更一致、更直观。


- [网络地址](#network-addresses)
- [占位符](#placeholders)
- [文件位置](#file-locations)
  - [数据目录](#data-directory)
  - [配置目录](#configuration-directory)
- [时长](#durations)



<a id="network-addresses"></a>
## 网络地址

当你指定要拨号或绑定的网络地址时，Caddy 接受以下格式的字符串：

```
network/address
```

网络部分可选（默认 `tcp`），其取值可为 Go 的 [net.Dial 函数](https://pkg.go.dev/net#Dial)可识别的任意值。若指定了网络，网络与地址之间必须用单个斜杠 `/` 分隔。

网络可为以下任一类型；以 `4` 或 `6` 结尾的表示仅 IPv4 或仅 IPv6：

- TCP：`tcp`、`tcp4`、`tcp6`
- UDP：`udp`、`udp4`、`udp6`
- IP：`ip`、`ip4`、`ip6`
- Unix：`unix`、`unixgram`、`unixpacket`

地址部分可为以下形式：

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/path/to/unix/socket`
- `/path/to/unix/socket|0200`

主机名可以是任意主机名、可解析的域名或 IP 地址。

对于 IPv6 地址，需用方括号 `[]` 包裹地址。区段标识（以 `%` 开头）可选（通常用于链路本地地址）。

端口可以是单个值（`:8080`）或闭区间范围（`:8080-8085`）。端口范围会被展开为单个地址。并非所有配置字段都支持端口范围。特殊端口 `:0` 表示任意可用端口。

Unix socket 路径仅在使用 `unix*` 网络类型时才有效。用于分隔网络和地址的斜杠不算作路径的一部分。

当 Unix socket 用作 bind 地址时，可以在路径后用竖线 `|` 指定文件权限模式。默认值为 `0200`（八进制），即 `u=w,g=,o=`（符号表示法）。前导 `0` 可省略。

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

Caddy 的网络地址不是 URL。URL 会耦合 [OSI 模型 <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OSI_model#Layer_architecture) 的低层和高层，但 Caddy 常常将网络地址独立于具体应用使用，因此将两者混用会有问题。Caddy 的网络地址只精确指向可在 L3-L5 层拨号或绑定的资源，而 URL 会覆盖 L3-L7，范围过宽。网络地址要求 host+port 与 path 互斥，但 URL 不要求。网络地址有时支持端口范围，而 URL 不支持。

</aside>




<a id="placeholders"></a>
## 占位符

Caddy 的配置支持使用 *占位符*。通过占位符可以把动态值注入静态配置。

<aside class="tip">

占位符与其他软件中的变量概念类似。例如，[nginx 的变量 <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html) 有 `$uri` 和 `$document_root`，而 Caddy 的对应写法是 [`{http.request.uri}`](/docs/json/apps/http/#docs) 和 [`{http.vars.root}`](/docs/caddyfile/directives/root)。

</aside>


占位符使用一对花括号 `{ }` 包裹中间标识符，例如：`{foo.bar}`。起始花括号可通过 `\{like.this}` 转义，以防被替换。为避免模块间冲突，占位符标识符通常使用点号进行命名空间划分。

可用占位符取决于上下文，并非所有占位符都能在配置的每个位置使用。例如，[HTTP app 会设置占位符](/docs/json/apps/http/#docs)，这些占位符只在处理 HTTP 请求相关配置区域可见。当请求经过 [`reverse_proxy` 处理器](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs) 时，处理器会设置若干 proxy 专用占位符。这些占位符可在代理过程中以及之后（在 `handle_response`）使用，例如设置响应头或增强访问日志。

以下占位符始终可用（全局）：

Placeholder | Description
------------|-------------
`{env.*}` | 环境变量；示例：`{env.HOME}`
`{file.*}` | 文件内容；示例：`{file./path/to/secret.txt}`
`{system.hostname}` | 系统本地主机名
`{system.slash}` | 系统文件路径分隔符
`{system.os}` | 系统 OS
`{system.arch}` | 系统架构
`{system.wd}` | 当前工作目录
`{time.now}` | Go Time 结构表示的当前时间
`{time.now.http}` | 当前时间（采用 [HTTP headers <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified) 的格式）
`{time.now.unix}` | 当前时间，单位为秒的 Unix 时间戳
`{time.now.unix_ms}` | 当前时间，单位为毫秒的 Unix 时间戳
`{time.now.common_log}` | 当前时间，Common Log Format
`{time.now.year}` | 当前年份（YYYY 格式）

并非所有配置字段都支持占位符，但大多数在你预期的场景中都会支持。只有该字段明确增加了支持后才可使用。插件作者可阅读 [这篇文章](/docs/extending-caddy/placeholders) 了解如何在自己的模块中添加占位符支持。



<a id="file-locations"></a>
## 文件位置

本节说明各种文件的存放位置。这里列出的路径主要是默认值；部分路径可被覆盖。

### 你的配置文件

没有一个固定约定的单一位置用于放置配置文件。把它放在最适合你的位置即可。

<aside class="tip">

唯一一个例外可能是当前工作目录下名为 `Caddyfile` 的文件；如果未指定其他配置文件，caddy 命令会为方便自动尝试该文件。

</aside>


带有默认配置文件的发行版应该说明该配置文件位置，即使对打包/发行版维护者来说可能一眼可见。对于大多数 Linux 安装，Caddyfile 位于 `/etc/caddy/Caddyfile`。


<a id="data-directory"></a>
### 数据目录

Caddy 会把 TLS 证书和其他重要资产存入数据目录，该目录由 [已配置的存储模块](/docs/json/storage/) 提供支撑（默认是本地文件系统）。

若设置了 `XDG_DATA_HOME` 环境变量，则路径为 `$XDG_DATA_HOME/caddy`。

否则，路径随平台变化，遵循各 OS 约定：

OS | 数据目录路径
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy`（或 `/sdcard/caddy`）

其他所有操作系统使用 Linux/BSD 的目录路径。

**数据目录不应被当作缓存使用。** 其内容**不是**短暂数据，也不只是用于性能优化。Caddy 会将 TLS 证书、私钥、OCSP staples 及其他必要信息写入数据目录。未理解影响不要直接清理。

该目录必须持久化，并且 Caddy 必须有写权限。


<a id="configuration-directory"></a>
### 配置目录

这是 Caddy 可将部分配置持久写入磁盘的目录。最主要的用途是默认将最近一次活动配置保存到该目录，以便后续通过 [`caddy run --resume`](/docs/command-line#caddy-run) 快速恢复。

<aside class="tip">

配置目录**不是**放置[你的配置文件](#your-config-files)的地方（当然你也可以放）。

</aside>


如果设置了 `XDG_CONFIG_HOME` 环境变量，则为 `$XDG_CONFIG_HOME/caddy`。

否则，路径随平台变化，遵循 OS 约定：


OS | 配置目录路径
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

其他所有操作系统使用 Linux/BSD 的目录路径。

该目录必须持久化，并且 Caddy 必须有写权限。


<a id="durations"></a>
## 时长

Caddy 配置中常用时长字符串。其格式与 [Go 的 `time.ParseDuration` 语法](https://golang.org/pkg/time/#ParseDuration)一致，但还可使用 `d` 表示天（为了简化，约定 1 天 = 24 小时）。有效单位为：

- `ns`（纳秒）
- `us`/`µs`（微秒）
- `ms`（毫秒）
- `s`（秒）
- `m`（分钟）
- `h`（小时）
- `d`（天）

示例：

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

在 [JSON 配置](/docs/json/) 中，时长值也可以是表示纳秒的整数。
