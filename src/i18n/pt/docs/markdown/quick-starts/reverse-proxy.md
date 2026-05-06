---
title: "Início rápido do reverse proxy"
---

# Início rápido do reverse proxy

Este guia vai mostrar como colocar rapidamente em funcionamento um reverse proxy pronto para produção, com ou sem HTTPS.

**Pré-requisitos:**
- Noções básicas de terminal / linha de comando
- `caddy` no seu `PATH`
- Um processo backend em execução para o qual fazer proxy

---

Este tutorial assume que você tem um serviço HTTP backend rodando em `127.0.0.1:9000`. Esses comandos são para Linux, mas os mesmos princípios se aplicam a outros sistemas operacionais.

Você pode iniciar um reverse proxy simples sem arquivo de configuração, ou usar um arquivo de configuração para ter mais flexibilidade e controle.

## Linha de comando

Para iniciar um proxy HTTP em texto puro da porta 2080 para a porta 9000 na sua máquina:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

Depois teste:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

O [`comando reverse-proxy`](/docs/command-line#reverse-proxy) é pensado para reverse proxies rápidos e fáceis. (Você pode usá-lo em produção se seus requisitos forem simples.)

## Caddyfile

No diretório de trabalho atual, crie um arquivo chamado `Caddyfile` com este conteúdo:

```caddy
:2080

reverse_proxy :9000
```

Esse arquivo de configuração é aproximadamente equivalente ao comando `caddy reverse-proxy` acima.

Depois, no mesmo diretório, execute:

<pre><code class="cmd bash">caddy run</code></pre>

Então teste seu proxy:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Se você mudar o Caddyfile, lembre-se de [recarregar](/docs/command-line#caddy-reload) o Caddy.

Esse foi um exemplo simples. Você pode fazer muito mais com a [`directiva reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

## HTTPS do cliente para o proxy

O Caddy servirá seu proxy sobre [HTTPS automaticamente e por padrão](/docs/automatic-https) se ele conhecer o hostname (nome de domínio). O comando `caddy reverse-proxy` usará `localhost` por padrão se você omitir a flag `--from`, ou você pode substituir a primeira linha do seu Caddyfile pelo nome de domínio do proxy.

- Se você usar `localhost` ou qualquer domínio que termine em `.localhost`, o Caddy usará um certificado autoassinado com renovação automática. Na primeira vez, talvez seja necessário digitar uma senha enquanto o Caddy tenta instalar o certificado raiz da CA no seu trust store.
- Se você usar qualquer outro nome de domínio, o Caddy tentará obter um certificado com confiança pública; certifique-se de que seus registros DNS apontam para a sua máquina e que as portas 80 e 443 estão abertas ao público e direcionadas para o Caddy.

Se você não especificar uma porta, o Caddy usa 443 para HTTPS. Nesse caso, você também precisará de permissão para vincular portas baixas. Algumas formas de fazer isso no Linux:

- Execute como root (por exemplo, `sudo -E`).
- Ou execute `sudo setcap cap_net_bind_service=+ep $(which caddy)` para dar ao Caddy essa capacidade específica.

A forma mais básica do comando `caddy reverse-proxy` que dá HTTPS é:

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

Depois teste:

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

Você pode personalizar o hostname usando a flag `--from`:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

Se você não tiver permissão para vincular portas baixas, pode fazer proxy a partir de uma porta mais alta:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

Se estiver usando um Caddyfile, basta alterar a primeira linha para o nome do seu domínio, por exemplo:

```caddy
example.com

reverse_proxy :9000
```

## HTTPS do proxy para o backend

O Caddy também pode fazer proxy usando HTTPS entre ele e o backend, se o backend suportar TLS. Basta usar `https://` no endereço do backend:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

Isso exige que o certificado do backend seja confiável pelo sistema em que o Caddy está rodando. (O Caddy não confia em certificados autoassinados, a menos que isso seja configurado explicitamente.)

Claro que você pode usar HTTPS nas duas pontas também:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

Isso serve HTTPS do cliente para o proxy e do proxy para o backend.

Se o hostname para o qual você está fazendo proxy for diferente daquele de onde você está fazendo proxy, será necessário usar a flag `--change-host-header`:

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

Por padrão, o Caddy passa todos os cabeçalhos HTTP inalterados, incluindo `Host`, e deriva o TLS ServerName do cabeçalho Host. `--change-host-header` redefine o cabeçalho Host para o do backend, para que o handshake TLS possa ser concluído com sucesso. No exemplo acima, ele seria alterado de `example.com` para `localhost:9000` (e `localhost` seria usado no handshake TLS).
