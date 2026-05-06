---
title: O Caddyfile
---

<a id="the-caddyfile"></a>
# O Caddyfile

O **Caddyfile** é um formato conveniente de configuração do Caddy para humanos. É a forma favorita da maioria das pessoas para usar o Caddy porque é fácil de escrever, fácil de entender e expressivo o suficiente para a maioria dos casos de uso.

Ele se parece com isto:

```caddy
example.com {
	root /var/www/wordpress
	encode
	php_fastcgi unix//run/php/php-version-fpm.sock
	file_server
}
```

(Esse é um Caddyfile real, pronto para produção, que serve WordPress com HTTPS totalmente gerenciado.)

A ideia básica é primeiro digitar o endereço do seu site e, depois, os recursos ou funcionalidades que você quer que o site tenha. [Veja mais padrões comuns.](/docs/caddyfile/patterns)

<a id="menu"></a>
## Menu

- #### [Guia de início rápido](/docs/quick-starts/caddyfile)
  Um bom ponto de partida para começar a se familiarizar com o Caddyfile.
- #### [Tutorial completo do Caddyfile](/docs/caddyfile-tutorial)
  Aprenda a fazer várias coisas comuns com o Caddyfile.
- #### [Conceitos do Caddyfile](/docs/caddyfile/concepts)
  Leitura obrigatória. Estrutura, endereços de site, matchers, placeholders e mais.
- #### [Diretivas](/docs/caddyfile/directives)
  Palavras-chave no início das linhas que habilitam recursos para seus sites.
- #### [Matchers de requisição](/docs/caddyfile/matchers)
  Filtre requisições usando matchers com suas diretivas.
- #### [Opções globais](/docs/caddyfile/options)
  Configurações que se aplicam ao servidor inteiro, e não a sites individuais.
- #### [Padrões comuns](/docs/caddyfile/patterns)
  Formas simples de fazer coisas comuns.
<!-- - #### [Especificação do Caddyfile](/docs/caddyfile/spec) TODO: concluir -->


<a id="note"></a>
## Observação

O Caddyfile é apenas um [adaptador de configuração](/docs/config-adapters) para o Caddy. Ele costuma ser preferido quando você cria configurações manualmente, mas não é tão expressivo, flexível ou programável quanto a [estrutura JSON nativa](/docs/json/) do Caddy. Se você estiver automatizando as configurações/implantações do Caddy, talvez prefira usar JSON com a [API do Caddy](/docs/api). Na prática, você também pode usar o Caddyfile com a API, mas apenas de forma limitada.
