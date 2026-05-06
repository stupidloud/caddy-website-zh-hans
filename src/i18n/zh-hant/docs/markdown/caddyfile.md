---
title: Caddyfile
---

<a id="the-caddyfile"></a>
# Caddyfile

**Caddyfile** 是專為人類設計的便利 Caddy 配置格式。它是大多數人最喜歡使用 Caddy 的方式，因為它易於編寫、易於理解，且對於大多數使用情境來說具有足夠的表達能力。

它看起來像這樣：

```caddy
example.com {
	root /var/www/wordpress
	encode
	php_fastcgi unix//run/php/php-version-fpm.sock
	file_server
}
```

（這是一個真實、可用於生產環境的 Caddyfile，它以全代管的 HTTPS 提供 WordPress 服務。）

基本概念是，你先輸入網站的位址，然後輸入網站需要的功能。 [查看更多常用模式。](/docs/caddyfile/patterns)

<a id="menu"></a>
## 選單

- #### [快速入門指南](/docs/quick-starts/caddyfile)
  開始熟悉 Caddyfile 的好地方。
- #### [完整的 Caddyfile 教學](/docs/caddyfile-tutorial)
  學習使用 Caddyfile 處理各種常見事務。
- #### [Caddyfile 概念](/docs/caddyfile/concepts)
  必讀內容！結構、網站位址、matcher、placeholder 等等。
- #### [指令](/docs/caddyfile/directives)
  行首的關鍵字，用於為你的網站啟用各項功能。
- #### [請求 matcher](/docs/caddyfile/matchers)
  透過在指令中使用 matcher 來過濾請求。
- #### [全域選項](/docs/caddyfile/options)
  適用於整個伺服器而非個別網站的設定。
- #### [常用模式](/docs/caddyfile/patterns)
  執行常見事務的簡單方法。
<!-- - #### [Caddyfile 規範](/docs/caddyfile/spec) TODO: 完成它 -->


<a id="note"></a>
## 注意

Caddyfile 只是 Caddy 的一個 [config adapter](/docs/config-adapters)。當手動撰寫配置時，通常會首選它，但它不如 Caddy 的 [原生 JSON 結構](/docs/json/) 那樣具有表達能力、靈活性或可程式化。如果你正在自動化你的 Caddy 配置/部署，你可能希望透過 [Caddy 的 API](/docs/api) 使用 JSON。（實際上你也可以在 API 中使用 Caddyfile，只是程度有限。）
