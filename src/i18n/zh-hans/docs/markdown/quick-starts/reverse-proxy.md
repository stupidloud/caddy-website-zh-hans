---
title: "反向代理快速入门"
---

# 反向代理快速入门

本指南将向您展示如何快速搭建一个支持或不支持 HTTPS 的、可用于生产环境的反向代理。

**先决条件：**
- 基本的终端/命令行操作技能
- `caddy` 在您的 PATH 中
- 一个正在运行的后端进程，用于进行代理

---

本教程假设您有一个后端 HTTP 服务正在 `127.0.0.1:9000`。以下命令适用于 Linux 系统，但相同原理也适用于其他操作系统。

您可以不使用配置文件直接运行一个简单的反向代理，也可以使用配置文件以获得更大的灵活性和控制权。


## 命令行

要在您的机器上启动一个从端口 2080 到端口 9000 的明文 HTTP 代理：

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

那么试试看：

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

[`reverse-proxy`命令](/docs/command-line#reverse-proxy)旨在实现快速简便的反向代理。（如果您的需求简单，也可以在生产环境中使用它。）

## Caddyfile

在当前工作目录中，创建一个名为 `Caddyfile` ，内容如下：

```caddy
:2080

reverse_proxy :9000
```

该配置文件大致相当于上方的 `caddy reverse-proxy` 上述命令。

然后，在同一目录下运行：

<pre><code class="cmd bash">caddy run</code></pre>

然后试着使用你的代理：

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

如果修改了 Caddyfile，请务必[重新加载](/docs/command-line#caddy-reload) Caddy。

这是一个简单的示例。借助[`reverse_proxy`指令](/docs/caddyfile/directives/reverse_proxy)，您可以实现更多功能。

## 客户端到代理的HTTPS连接

如果 Caddy 知道主机名（域名），它将[默认自动](/docs/automatic-https)通过 [HTTPS](/docs/automatic-https) 提供代理服务。`caddy reverse-proxy` 命令在未指定 `--from` 参数时默认使用 `localhost`；如果您使用 Caddyfile，则可以将第一行替换为代理的域名。

- 如果您使用 `localhost` 或任何以 `.localhost` 结尾的域名，Caddy 将使用自动续期的自签名证书。首次操作时，您可能需要输入密码，因为 Caddy 会尝试将它的 CA 根证书安装到您的信任存储中。
- 如果您使用其他域名，Caddy 将尝试获取受公众信任的证书；请确保您的 DNS 记录指向您的机器，并且 80 和 443 端口对公众开放，且指向 Caddy。

如果您未指定端口，Caddy 会默认使用 443 端口进行 HTTPS 连接。在这种情况下，您还需要获得绑定到低端口的权限。在 Linux 系统上实现这一点有以下几种方法：

- 以 root 身份运行（例如： `sudo -E`).
- 或者运行 `sudo setcap cap_net_bind_service=+ep $(which caddy)` 以赋予 Caddy 这一特定功能。

以下是最基本的 `caddy reverse-proxy` 命令，可实现 HTTPS：

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

那么试试看：

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

您可以使用 `--from` 标志：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

如果您没有绑定低号端口的权限，可以从更高号端口进行代理：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

如果您使用的是 Caddyfile，只需将第一行修改为您自己的域名，例如：

```caddy
example.com

reverse_proxy :9000
```

## 从代理到后端的 HTTPS

如果后端支持 TLS，Caddy 还可以通过 HTTPS 在自身与后端之间进行代理。只需在后端地址中使用 `https://` ：

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

这要求后端的服务证书必须被 Caddy 运行的系统所信任。（除非明确配置，否则 Caddy 不信任自签名证书。）

当然，你也可以在两端都使用HTTPS：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

这实现了从客户端到代理，以及从代理到后端的HTTPS连接。

如果代理目标的主机名与代理源的主机名不同，则需要使用 `--change-host-header` 标志：

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

默认情况下，Caddy 会原样转发所有 HTTP 头，包括 `Host`，且 Caddy 会根据 Host 头部推导出 TLS ServerName。 `--change-host-header` 会将 Host 头部重置为后端服务器的值，以确保 TLS 握手能够成功完成。在上例中，它将从 `example.com` 更改为 `localhost:9000` （且 `localhost` 将用于 TLS 握手）。
