---
title: "Railway 快速入门"
---

# Railway 快速入门

在 Railway 上部署 Caddy 是一种简单、省心的方法，可用于部署包含插件的自定义 Caddy 构建版本。

**先决条件：**
- 一个免费的[Railway](https://railway.com)账户

## 在 Railway 上部署 Caddy

请访问我们的 [下载页面](/download)，选择您需要的插件，然后点击顶部的紫色“在 Railway 上部署”按钮。

<details>
	<summary>或者，手动配置该模板</summary>

或者，如果您想自行配置 Railway 模板，请按照以下步骤操作。

前往 Railway 模板：

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

并点击“配置”以添加所需的插件：

![部署界面](/resources/images/railway/deploy-screen.png)

然后将插件粘贴到 `CADDY_PLUGINS` 变量中，各插件之间用空格分隔：

![添加插件](/resources/images/railway/deploy-config.png)

</details>

点击“部署”，待部署完成后，您可以通过点击此处的链接进行试用：

![访问您的部署](/resources/images/railway/prod-link.png)

您应该会看到一个欢迎页面，显示您的新服务器正在运行！

接下来，您可以自定义部署配置，以托管您自己的网站，或作为代理连接到另一个 Railway 服务。

## 自定义部署

若要部署到您自己的网站，或修改配置，只需将[我们的模板](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic)“提取”到您自己的仓库中：

![弹出模板](/resources/images/railway/eject.png)

在您自己的仓库中，您可以：

- 将您的网站放入 `www` 文件夹中。
- 修改 Caddy 的配置文件，即 [Caddyfile](/docs/caddyfile)。

只需提交更改并推送，然后即可在 Railway 上重新部署。

如果您想更改 Caddy 构建中的插件，只需编辑 `CADDY_PLUGINS` 变量并重新部署：

![更改插件](/resources/images/railway/plugins-variable.png)

## 提示

Railway 会为您终止 TLS 连接，因此您应将 Caddy 配置写成仿佛其正被代理至某处（因为实际上确实如此）。因此，如果您在 Caddyfile 的站点地址中使用了主机名，则应在全局选项中使用 `auto_https off` 。使用我们的模板时，Caddy 不会直接面向互联网。


## 变量

您可以在 Railway 项目中设置以下环境变量，本模板可能会使用这些变量：

名称 | 描述 | 默认值 | 示例
---- | ----------- | ------- | ----------
`CADDY_PLUGINS` | 以空格分隔的 Caddy 插件列表 | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
