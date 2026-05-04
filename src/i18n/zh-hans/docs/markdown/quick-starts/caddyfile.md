---
title: "Caddyfile 快速入门"
---

# Caddyfile 快速入门

创建一个名为 `Caddyfile` （无扩展名）。

在 Caddyfile 中输入的第一项是您网站的地址：

```caddy
localhost
```

<aside class="tip">

如果 HTTP 和 HTTPS 端口（分别是 80 和 443）在您的操作系统上属于受限端口，您需要以提升的权限运行，或者使用更高的端口。要获得权限，请以 root 身份运行 `sudo -E` ，或使用 `sudo setcap cap_net_bind_service=+ep $(which caddy)`。或者，若要使用更高端口，只需将地址修改为类似 `localhost:2080` ，并通过 Caddyfile 选项 [`http_port`](/docs/caddyfile/options) 修改 HTTP 端口。

</aside>

然后按回车键，输入你想让它执行的操作，这样看起来就像这样：

```caddy
localhost

respond "Hello, world!"
```

将此文件保存下来，然后在包含 Caddyfile 的同一文件夹中运行 Caddy：

<pre><code class="cmd bash">caddy start</code></pre>

系统可能会要求您输入密码，因为 Caddy 默认通过 HTTPS 提供所有网站（包括本地网站）的访问服务。（通常只有第一次才会出现密码提示！）

<aside class="tip">

对于本地 HTTPS，Caddy 会自动为您生成证书和唯一的私钥。根证书会被添加到系统的受信任存储中，因此需要输入密码。这样您就可以在本地通过 HTTPS 进行开发，而不会遇到证书错误。

</aside>

（如果遇到权限错误，您可能需要以管理员身份运行，或者选择大于1023的端口。）

请在浏览器中输入 [localhost](http://localhost) 或 `curl` 它：

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Hello, world!</code></pre>

您可以在 Caddyfile 中通过将多个站点用大括号包起来来定义它们 `{ }`。将您的 Caddyfile 修改为：

```caddy
localhost {
	respond "Hello, world!"
}

localhost:2016 {
	respond "Goodbye, world!"
}
```

您可以通过两种方式向 Caddy 提供更新后的配置，一种是直接通过 API：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

或者使用 reload 命令，它会为你执行相同的 API 请求：

<pre><code class="cmd bash">caddy reload</code></pre>

[在浏览器中](https://localhost:2016)或使用 `curl` 来确保其正常运行：

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Goodbye, world!</code></pre>

使用完 Caddy 后，请务必将其停止：

<pre><code class="cmd bash">caddy stop</code></pre>

## 延伸阅读

- [Caddyfile 概念](/docs/caddyfile/concepts)
- [指令](/docs/caddyfile/directives)
- [常见模式](/docs/caddyfile/patterns)
