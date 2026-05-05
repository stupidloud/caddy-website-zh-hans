---
title: Railway Quick-start
---

<a id="railway-quick-start"></a>
# Railway クイックスタート

Railway に Caddy をデプロイするのは、plugin を含むカスタム Caddy build を簡単にデプロイできる手軽な方法です。

**前提条件:**
- 無料の [Railway](https://railway.com) アカウント

<a id="deploy-caddy-on-railway"></a>
## Railway に Caddy をデプロイする

[Download page](/download) に移動して必要な plugin を選択し、上部の紫色の "Deploy on Railway" ボタンをクリックします。

<details>
	<summary>または、template を手動で設定する</summary>

Railway template を自分で設定したい場合は、次のように行います。

Railway 上の template に移動します。

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

そして "Configure" をクリックして、必要な plugin を追加します。

![Deploy screen](/resources/images/railway/deploy-screen.png)

次に、plugin をスペース区切りで `CADDY_PLUGINS` 変数に貼り付けます。

![Adding plugins](/resources/images/railway/deploy-config.png)

</details>

Deploy をクリックします。デプロイが完了したら、ここに表示されるリンクをクリックして試せます。

![Visit your deployment](/resources/images/railway/prod-link.png)

新しいサーバーが動作していることを示す welcome page が表示されるはずです。

次に、自分のサイトを提供したり、別の Railway service へ proxy したりするようにデプロイをカスタマイズできます。

<a id="customize-the-deployment"></a>
## デプロイをカスタマイズする

自分の web site を提供したり設定を変更したりするには、[our template](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic) を自分の repository に "eject" するだけです。

![Eject template](/resources/images/railway/eject.png)

自分の repository では、次のことができます。

- 自分のサイトを `www` folder に置く。
- Caddy の設定である [Caddyfile](/docs/caddyfile) を変更する。

変更を commit して push すれば、Railway で redeploy できます。

Caddy build に含める plugin を変更したい場合は、`CADDY_PLUGINS` 変数を編集して redeploy するだけです。

![Change plugins](/resources/images/railway/plugins-variable.png)

<a id="tips"></a>
## ヒント

Railway は TLS を終端してくれるため、Caddy の設定は proxy 先として動作しているものとして書く必要があります（実際にそうなっています）。したがって、Caddyfile の site address で host を使う場合は、global options で `auto_https off` を使ってください。この template では、Caddy は edge-facing ではありません。


<a id="variables"></a>
## Variables

この template が使う可能性のある、Railway project で設定できる環境変数:

Name | Description | Default | Example(s)
---- | ----------- | ------- | ----------
`CADDY_PLUGINS` | スペース区切りの Caddy plugins のリスト | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
