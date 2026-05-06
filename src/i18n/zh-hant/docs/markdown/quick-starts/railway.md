---
title: Railway 快速入門
---

<a id="railway-quick-start"></a>
# Railway 快速入門

在 Railway 上部署 Caddy 是一種簡單、輕鬆的方式，可以用來部署帶有外掛程式的自訂 Caddy 版本。

**先決條件：** 
- 一個免費的 [Railway](https://railway.com) 帳戶

<a id="deploy-caddy-on-railway"></a>
## 在 Railway 上部署 Caddy

前往我們的 [下載頁面](/download) 並選擇您需要的任何外掛程式，然後點擊頂部的紫色「Deploy on Railway」按鈕。

<details>
	<summary>或者，手動設定範本</summary>

或者，如果您想自行設定 Railway 範本，以下是操作方法。

前往 Railway 上的範本：

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

並透過點擊「Configure」添加您需要的任何外掛程式：

![部署畫面](/resources/images/railway/deploy-screen.png)

然後將外掛程式貼入 `CADDY_PLUGINS` 變數中，以空格分隔：

![添加外掛程式](/resources/images/railway/deploy-config.png)

</details>

點擊 Deploy，部署完成後，您可以透過點擊此處的連結來進行嘗試：

![訪問您的部署](/resources/images/railway/prod-link.png)

您應該會看到一個歡迎頁面，顯示您的新伺服器正在運行！

接下來，您可以自訂您的部署，以提供您自己的網站服務或反向代理到另一個 Railway 服務。

<a id="customize-the-deployment"></a>
## 自訂部署

要提供您自己的網站，或更改設定，只需將 [我們的範本](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic) 「退出 (eject)」到您自己的儲存庫中：

![退出範本](/resources/images/railway/eject.png)

在您自己的儲存庫中，您可以：

- 將您自己的網站放入 `www` 資料夾中。
- 修改 Caddy 的設定，即 [Caddyfile](/docs/caddyfile)。

只需提交更改並推送，然後您就可以在 Railway 上重新部署。

如果您想更改 Caddy 版本中的外掛程式，您只需編輯 `CADDY_PLUGINS` 變數並重新部署：

![更改外掛程式](/resources/images/railway/plugins-variable.png)

<a id="tips"></a>
## 提示

Railway 會為您終止 TLS，因此您應該像被代理一樣編寫 Caddy 設定（事實也確實如此）。因此，如果您在 Caddyfile 網站位址中使用主機名，則應在全域選項中使用 `auto_https off`。在我們的範本中，Caddy 並非直接面向邊緣 (edge-facing)。


<a id="variables"></a>
## 變數

您可以在 Railway 專案中設置此範本可能使用的環境變數：

名稱 | 描述 | 預設值 | 範例
---- | ----------- | ------- | ----------
`CADDY_PLUGINS` | 以空格分隔的 Caddy 外掛程式列表 | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
