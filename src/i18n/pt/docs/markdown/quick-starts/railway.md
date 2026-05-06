---
title: "Início rápido do Railway"
---

# Início rápido do Railway

Implantar o Caddy no Railway é uma forma fácil e sem complicação de implantar uma build personalizada do Caddy com plugins.

**Pré-requisitos:**
- Uma conta gratuita no [Railway](https://railway.com)

## Implantar o Caddy no Railway

Vá para nossa [página de download](/download) e selecione os plugins de que precisar, depois clique no botão roxo "Deploy on Railway" no topo.

<details>
	<summary>Ou configure o template manualmente</summary>

Alternativamente, se você quiser configurar o template do Railway por conta própria, veja como fazer.

Vá para o template no Railway:

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

e adicione os plugins de que precisar clicando em "Configure":

![Deploy screen](/resources/images/railway/deploy-screen.png)

Depois cole os plugins na variável `CADDY_PLUGINS`, separados por espaços:

![Adding plugins](/resources/images/railway/deploy-config.png)

</details>

Clique em Deploy e, após a implantação terminar, você pode testá-la clicando no link aqui:

![Visit your deployment](/resources/images/railway/prod-link.png)

Você deverá ver uma página de boas-vindas indicando que seu novo servidor está funcionando!

Em seguida, você pode personalizar a implantação para servir seu próprio site ou fazer proxy para outro serviço Railway.

## Personalizar a implantação

Para servir seu próprio site, ou mudar a configuração, basta "ejetar" [nosso template](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic) para o seu próprio repositório:

![Eject template](/resources/images/railway/eject.png)

A partir do seu próprio repositório, você pode:

- Colocar seu próprio site na pasta `www`.
- Modificar a configuração do Caddy, que é o [Caddyfile](/docs/caddyfile).

Simplesmente faça commit das mudanças e envie, e então você pode fazer redeploy no Railway.

Se quiser alterar os plugins na sua build do Caddy, tudo o que você precisa fazer é editar a variável `CADDY_PLUGINS` e redeployar:

![Change plugins](/resources/images/railway/plugins-variable.png)

## Dicas

O Railway termina o TLS para você, então você deve escrever a configuração do Caddy como se ele estivesse sendo proxied to (porque está). Portanto, se você usar hosts nos endereços do site do seu Caddyfile, deve usar `auto_https off` nas opções globais. O Caddy não fica voltado diretamente para a borda com o nosso template.

## Variáveis

Variáveis de ambiente que você pode definir no seu projeto Railway e que este template pode usar:

Nome | Descrição | Padrão | Exemplo(s)
---- | ----------- | ------- | ----------
`CADDY_PLUGINS` | Lista de plugins do Caddy separada por espaços | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
