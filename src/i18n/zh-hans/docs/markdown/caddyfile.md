---
title: "《Caddyfile》"
---

# Caddyfile

**Caddyfile** 是一种便于人类阅读的 Caddy 配置格式。这是大多数人最喜欢的 Caddy 使用方式，因为它易于编写、易于理解，并且足以满足大多数使用场景的需求。

看起来是这样的：

```caddy
example.com {
	root /var/www/wordpress
	encode
	php_fastcgi unix//run/php/php-version-fpm.sock
	file_server
}
```

（这是一个真正的、已准备好投入生产的 Caddyfile，它通过完全托管的 HTTPS 服务 WordPress。）

基本思路是：首先输入您网站的地址，然后输入您希望网站具备的特性或功能。[查看更多常见模式。](/docs/caddyfile/patterns)

## 菜单

- #### [快速入门指南](/docs/quick-starts/caddyfile)
  这是开始熟悉 Caddyfile 的一个好地方。
- #### [完整的 Caddyfile 教程](/docs/caddyfile-tutorial)
  学习如何使用 Caddyfile 完成各种常见操作。
- #### [Caddyfile 概念](/docs/caddyfile/concepts)
  必读！结构、站点地址、匹配器、占位符等。
- #### [指令](/docs/caddyfile/directives)
  行首的关键词可为您的网站启用相关功能。
- #### [请求匹配器](/docs/caddyfile/matchers)
  使用匹配器配合指令来过滤请求。
- #### [全局选项](/docs/caddyfile/options)
  适用于整个服务器而非单个网站的设置。
- #### [常见模式](/docs/caddyfile/patterns)
  简单完成日常事务的方法。
<!-- - #### [Caddyfile specification](/docs/caddyfile/spec) TODO: Finish this -->


## 注

Caddyfile 只是 Caddy 的一个[配置适配器](/docs/config-adapters)。在手动编写配置时通常更倾向于使用它，但它的表达能力、灵活性和可编程性都不如 Caddy [原生的 JSON 结构](/docs/json/)。如果您需要自动化 Caddy 的配置或部署，建议使用 JSON 配合 [Caddy 的 API](/docs/api)。（实际上，您也可以通过 API 使用 Caddyfile，只是功能有所限制。）
