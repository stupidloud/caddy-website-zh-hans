---
title: "Início rápido de arquivos estáticos"
---

# Início rápido de arquivos estáticos

Este guia vai mostrar como colocar rapidamente em funcionamento um servidor de arquivos estáticos pronto para produção.

**Pré-requisitos:**
- Noções básicas de terminal / linha de comando
- `caddy` no seu `PATH`
- Uma pasta contendo seu site

---

Há duas formas fáceis de colocar rapidamente um servidor de arquivos em funcionamento.

## Linha de comando

No terminal, vá para o diretório raiz do seu site e execute:

<pre><code class="cmd bash">caddy file-server</code></pre>

Se você receber um erro de permissão, provavelmente significa que seu sistema operacional não permite vincular portas baixas -- então use uma porta alta:

<pre><code class="cmd bash">caddy file-server --listen :2015</code></pre>

Depois abra [localhost](http://localhost) (ou [localhost:2015](http://localhost:2015)) no navegador para ver seu site!

Se você não tiver um arquivo index, mas quiser exibir uma listagem de arquivos, use a opção `--browse`:

<pre><code class="cmd bash">caddy file-server --browse</code></pre>

Você pode usar outra pasta como raiz do site:

<pre><code class="cmd bash">caddy file-server --root ~/mysite</code></pre>

## Caddyfile

Na raiz do seu site, crie um arquivo chamado `Caddyfile` com este conteúdo:

```caddy
localhost

file_server
```

Se você não tiver permissão para vincular portas baixas, substitua `localhost` por `localhost:2015` (ou alguma outra porta alta).

Depois, no mesmo diretório, execute:

<pre><code class="cmd bash">caddy run</code></pre>

Você pode então abrir [localhost](https://localhost) (ou o endereço que estiver na sua configuração) para ver seu site!

A [`diretiva file_server`](/docs/caddyfile/directives/file_server) tem mais opções para você personalizar seu site. Lembre-se de [recarregar](/docs/command-line#caddy-reload) o Caddy (ou pará-lo e iniciá-lo novamente) quando mudar o Caddyfile!

Se você não tiver um arquivo index, mas quiser exibir uma listagem de arquivos, use o argumento `browse`:

```caddy
localhost

file_server browse
```

Você também pode usar outra pasta como raiz do site:

```caddy
localhost

root /var/www/mysite
file_server
```
