---
title: "Compilar a partir do código-fonte"
---

# Compilar a partir do código-fonte

Há várias opções para compilar o Caddy, caso você precise de uma build personalizada (por exemplo, com plugins):
- [Git](#git): compilar a partir do repositório Git
- [`xcaddy`](#xcaddy): compilar usando `xcaddy`
- [Docker](#docker): compilar uma imagem Docker personalizada

Requisitos:

- [Go](https://golang.org/doc/install) 1.20 ou mais recente

A seção [Package Support Files](#package-support-files-for-custom-builds-for-debianubunturaspbian) contém instruções para usuários que instalaram o Caddy usando o comando APT em sistemas derivados de Debian, mas ainda precisam do executável de build personalizada para as suas operações.

## Git

Requisitos:

- Go instalado (veja acima)

Clone o repositório:

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

Se você não tiver git, pode baixar o código-fonte como um arquivo compactado [do GitHub](https://github.com/caddyserver/caddy). Cada [release](https://github.com/caddyserver/caddy/releases) também possui snapshots do código-fonte.

Compile:

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>

<aside class="tip">

Devido a [um bug no Go](https://github.com/golang/go/issues/29228), esses passos básicos não incorporam informações de versão. Se você quiser a versão (`caddy version`), precisa compilar o Caddy como dependência, e não como módulo principal. As instruções para isso estão no arquivo [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) do Caddy. Ou você pode usar [`xcaddy`](#xcaddy), que automatiza isso.

</aside>

Programas Go são fáceis de compilar para outras plataformas. Basta definir as variáveis de ambiente `GOOS`, `GOARCH` e/ou `GOARM` diferentes. ([Veja a documentação do Go para detalhes.](https://golang.org/doc/install/source#environment))

Por exemplo, para compilar o Caddy para Windows quando você não está no Windows:

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

Ou, de forma semelhante, para Linux ARMv6 quando você não está no Linux ou em ARMv6:

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>

## xcaddy

O comando [`xcaddy`](https://github.com/caddyserver/xcaddy) é a forma mais fácil de compilar o Caddy com informações de versão e/ou plugins.

Requisitos:

- Go instalado (veja acima)
- Certifique-se de que [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) esteja no seu `PATH`

Você **não** precisa baixar o código-fonte do Caddy (ele fará isso para você).

Então compilar o Caddy (com informações de versão) é tão fácil quanto:

<pre><code class="cmd bash">xcaddy build</code></pre>

Para compilar com plugins, use `--with`:

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter
	--with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

Como você pode ver, é possível personalizar as versões dos plugins com a sintaxe `@`. As versões podem ser um tag, um SHA de commit ou um branch.

A compilação multiplataforma com `xcaddy` funciona da mesma forma que com o comando `go`. Por exemplo, para cross-compilar para macOS:

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>

## Docker

Você pode usar a imagem `:builder` como atalho para compilar um novo binário do Caddy com módulos personalizados:

```Dockerfile
FROM caddy:<version>-builder AS builder

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
    --with github.com/hairyhenderson/caddy-teapot-module@v0.0.3-0

FROM caddy:<version>

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

Lembre-se de substituir `<version>` pela versão mais recente do Caddy para começar.

Observe a segunda instrução `FROM` - isso produz uma imagem muito menor, simplesmente sobrepondo o binário recém-compilado em cima da imagem normal do `caddy`.

O builder usa `xcaddy` para compilar o Caddy com os módulos fornecidos, de forma semelhante ao processo [descrito acima](#xcaddy). As opções `--mount=type=cache,target=/go/pkg/mod` e `--mount=type=cache,target=/root/.cache/go-build` são usadas para armazenar em cache as dependências dos módulos Go e os artefatos de compilação, respectivamente, o que acelera compilações subsequentes. A flag é [um recurso do Docker](https://docs.docker.com/build/cache/optimize/#use-cache-mounts), não do `xcaddy`.

Para usar Docker Compose, veja nosso [`compose.yml`](/docs/running#docker-compose) recomendado e as instruções de uso.

<a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>
## Arquivos de suporte de pacote para builds personalizadas para Debian/Ubuntu/Raspbian

Este procedimento tem como objetivo simplificar a execução de binários personalizados do `caddy` mantendo os arquivos de suporte do pacote `caddy`.

Ele permite que os usuários aproveitem a configuração padrão, os arquivos de serviço do systemd e o bash-completion do pacote oficial.

Requisitos:
- Instale o pacote `caddy` de acordo com [estas instruções](/docs/install#debian-ubuntu-raspbian)
- Compile seu binário personalizado do `caddy` (veja as seções acima) ou [faça o download](/download) de uma build personalizada
- Seu binário personalizado do `caddy` deve estar no diretório atual

Procedimento:
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

Explicação:

- `dpkg-divert` vai mover o binário `/usr/bin/caddy` para `/usr/bin/caddy.default` e deixar uma diversificação em vigor caso algum pacote tente instalar um arquivo nesse local.

- `update-alternatives` vai criar um symlink do binário `caddy` desejado para `/usr/bin/caddy`

- `systemctl restart caddy` vai desligar a versão padrão do servidor Caddy e iniciar a personalizada.

Você pode alternar entre os binários `caddy` personalizados e padrão executando o comando abaixo e seguindo as instruções na tela. Depois, reinicie o serviço do Caddy.

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

Para atualizar o Caddy depois disso, você pode executar [`caddy upgrade`](/docs/command-line#caddy-upgrade). Isso tenta [baixar](/download) uma build com os mesmos plugins da sua build atual, na versão mais recente do Caddy, e então substituir o binário atual pelo novo.
