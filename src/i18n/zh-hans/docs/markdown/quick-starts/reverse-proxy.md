---
title: "反向代理快速入门"
---

# 反向代理快速入门

本指南将帮助您快速搭建一个可用于生产环境的反向代理（支持或不支持 HTTPS）。

**先决条件：**
- 基础终端 / 命令行操作能力
- `caddy` 在 `PATH` 中
- 一个可供代理的后端进程正在运行

---

本教程假设您有一个后端 HTTP 服务运行在 `127.0.0.1:9000`。以下命令以 Linux 为例，但同样适用于其他操作系统。

您可以在不使用配置文件的情况下快速运行一个反向代理，也可以使用配置文件获得更高的灵活性和可控性。


## 命令行

要在本机将明文 HTTP 代理从 `2080` 端口代理到 `9000` 端口：

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

然后测试：

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

[`reverse-proxy` 命令](/docs/command-line#reverse-proxy)适用于快速、简洁的反向代理场景。（如果需求较简单，也可直接用于生产环境。）


## Caddyfile

在当前工作目录创建一个名为 `Caddyfile` 的文件，内容如下：

```caddy
:2080

reverse_proxy :9000
```

该配置文件与上文的 `caddy reverse-proxy` 命令大致等价。

然后在同一目录执行：

<pre><code class="cmd bash">caddy run</code></pre>

再测试您的代理：

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

如果修改了 Caddyfile，请务必进行[重载](/docs/command-line#caddy-reload)。

这是一个非常基础的示例。借助 [`reverse_proxy` 指令](/docs/caddyfile/directives/reverse_proxy)，您可以构建更复杂的配置。


## 客户端到代理的 HTTPS

如果 Caddy 能识别主机名（域名），会默认自动通过 [HTTPS](/docs/automatic-https) 提供代理服务。`caddy reverse-proxy` 命令如果省略 `--from` 参数，默认使用 `localhost`；或者您也可以把 Caddyfile 的首行替换为代理的域名。

- 如果使用 `localhost` 或任何以 `.localhost` 结尾的域名，Caddy 会使用一个自动续期的自签名证书。您第一次这样做时，可能需要输入密码，因为 Caddy 会尝试将其 CA 根证书写入信任库。
- 如果使用其他域名，Caddy 会尝试获取公信任证书；请确保 DNS 记录指向您的机器，并且 80 与 443 端口对外开放且流量指向 Caddy。

如果不指定端口，Caddy 默认使用 HTTPS 443。此时还需要有权绑定低位端口。在 Linux 可通过以下方式实现：

- 使用 root 身份运行（例如 `sudo -E`）
- 或运行 `sudo setcap cap_net_bind_service=+ep $(which caddy)` 赋予 Caddy 该能力

以下是最基础的、启用 HTTPS 的 `caddy reverse-proxy` 命令：

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

然后测试：

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

您可以使用 `--from` 参数自定义主机名：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

如果您没有权限绑定低位端口，可以改为从更高端口代理：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

若使用 Caddyfile，请直接将首行改为您的域名，例如：

```caddy
example.com

reverse_proxy :9000
```

## 代理到后端的 HTTPS

如果后端支持 TLS，Caddy 也可以在 Caddy 与后端之间使用 HTTPS。只需在后端地址中使用 `https://`：

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

这要求后端证书受 Caddy 运行环境信任（除非明确配置，否则 Caddy 不会信任自签名证书）。

当然，您也可以在两端都使用 HTTPS：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

这会同时在客户端与代理之间、代理与后端之间使用 HTTPS。

如果代理目标主机名与来源主机名不同，您需要使用 `--change-host-header` 参数：

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

默认情况下，Caddy 会透传所有 HTTP 标头（包括 `Host`）而不做更改，并从 `Host` 标头推导 TLS 的 `ServerName`。`--change-host-header` 会将 `Host` 标头重置为后端标头，以保证 TLS 握手成功完成。在上例中，`Host` 将从 `example.com` 改为 `localhost:9000`（TLS 握手时使用 `localhost`）。
