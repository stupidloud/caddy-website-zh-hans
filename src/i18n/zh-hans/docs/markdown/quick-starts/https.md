---
title: "HTTPS 快速入门"
---

# HTTPS 快速入门

本指南将向您展示如何快速部署并启用[全托管 HTTPS](/docs/automatic-https)。

<aside class="tip">
	只要配置文件中提供了主机名，Caddy 默认会为所有站点启用 HTTPS。本教程假设您希望通过 HTTPS 部署一个受公众信任的网站（即非“localhost”），因此我们将使用公共域名和外部端口。
</aside>

**先决条件：**
- 基本的终端/命令行操作技能
- 对 DNS 有基本了解
- 一个已注册的域名
- 允许外部访问80和443端口
- `caddy` 并 `curl` 并将其添加到 PATH 环境变量中

---

在本教程中，请将 `example.com` 替换为您的实际域名。

请将您的域名的 A/AAAA 记录指向您的服务器。您可以通过登录您的 DNS 服务商并管理您的域名来完成此操作。

继续操作前，请通过权威服务器查询验证记录是否正确。请将 `example.com` 替换为您的域名，若使用 IPv6，请将 `type=A` 替换为 `type=AAAA`:

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=example.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

此外，请确保您的服务器通过公共接口在 80 和 443 端口上对外可访问。

<aside class="tip">
	如果您正在使用家庭网络或其他受限网络，可能需要进行端口转发或调整防火墙设置。
</aside>

我们只需在配置中使用您的域名启动 Caddy 即可。实现方法有多种。

## Caddyfile

这是获取 HTTPS 的最常见方法。

创建一个名为 `Caddyfile` （无扩展名），其第一行是您的域名，例如：

```caddy
example.com

respond "Hello, privacy!"
```

然后在同一目录下运行：

<pre><code class="cmd bash">caddy run</code></pre>

您会看到 Caddy 生成一个 TLS 证书，并通过 HTTPS 提供您的网站服务。之所以能实现这一点，是因为 Caddyfile 中您网站的地址包含了一个域名。


## `file-server` 命令

如果你只需要通过 HTTPS 提供静态文件，请运行以下命令（将域名替换为你的域名）：

<pre><code class="cmd bash">caddy file-server --domain example.com</code></pre>

您将看到 Caddy 生成一个 TLS 证书，并通过 HTTPS 提供您的网站服务。


## `reverse-proxy` 命令

如果您只需要一个简单的 HTTPS 反向代理（作为 TLS 终结点），请运行以下命令（请替换为您自己的域名和实际后端地址）：

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to localhost:9000</code></pre>

您将看到 Caddy 生成一个 TLS 证书，并通过 HTTPS 提供您的网站服务。


## JSON 配置

一般而言，任何[主机匹配器](/docs/json/apps/http/servers/routes/match/host/)都会触发自动HTTPS。

因此，如下所示的 JSON 配置将启用适用于生产环境的[自动 HTTPS](/docs/automatic-https)：

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["example.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Hello, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
