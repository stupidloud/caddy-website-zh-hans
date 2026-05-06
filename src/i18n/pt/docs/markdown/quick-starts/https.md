---
title: "Início rápido de HTTPS"
---

# Início rápido de HTTPS

Este guia vai mostrar como colocar em funcionamento rapidamente o [HTTPS totalmente gerenciado](/docs/automatic-https).

<aside class="tip">
	O Caddy usa HTTPS para todos os sites por padrão, desde que um nome de host seja fornecido na configuração. Este tutorial assume que você quer colocar um site com certificado de confiança pública (ou seja, não "localhost") no ar via HTTPS, então usaremos um nome de domínio público e portas externas.
</aside>

**Pré-requisitos:**
- Noções básicas de terminal / linha de comando
- Entendimento básico de DNS
- Um nome de domínio público registrado
- Acesso externo às portas 80 e 443
- `caddy` e `curl` no seu `PATH`

---

Neste tutorial, substitua `example.com` pelo seu nome de domínio real.

Defina os registros A/AAAA do seu domínio apontando para o seu servidor. Você pode fazer isso entrando no seu provedor de DNS e gerenciando o nome de domínio.

Antes de continuar, verifique os registros corretos com uma consulta autoritativa. Substitua `example.com` pelo seu domínio e, se estiver usando IPv6, substitua `type=A` por `type=AAAA`:

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=example.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

Também verifique se o seu servidor está acessível externamente nas portas 80 e 443 a partir de uma interface pública.

<aside class="tip">
	Se você estiver em casa ou em outra rede restrita, talvez precise encaminhar portas ou ajustar as configurações de firewall.
</aside>

Tudo o que precisamos fazer é iniciar o Caddy com seu nome de domínio na configuração. Há várias maneiras de fazer isso.

## Caddyfile

Esta é a forma mais comum de obter HTTPS.

Crie um arquivo chamado `Caddyfile` (sem extensão) em que a primeira linha seja o nome do seu domínio, por exemplo:

```caddy
example.com

respond "Hello, privacy!"
```

Depois, no mesmo diretório, execute:

<pre><code class="cmd bash">caddy run</code></pre>

Você verá o Caddy provisionar um certificado TLS e servir seu site via HTTPS. Isso foi possível porque o endereço do seu site no Caddyfile continha um nome de domínio.

## O comando `file-server`

Se tudo o que você precisa é servir arquivos estáticos via HTTPS, execute este comando (substituindo seu nome de domínio):

<pre><code class="cmd bash">caddy file-server --domain example.com</code></pre>

Você verá o Caddy provisionar um certificado TLS e servir seu site via HTTPS.

## O comando `reverse-proxy`

Se tudo o que você precisa é de um reverse proxy simples via HTTPS (como terminador TLS), execute este comando (substituindo seu nome de domínio e o endereço real do backend):

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to localhost:9000</code></pre>

Você verá o Caddy provisionar um certificado TLS e servir seu site via HTTPS.

## Configuração JSON

A regra geral é que qualquer [host matcher](/docs/json/apps/http/servers/routes/match/host/) vai acionar o Automatic HTTPS.

Assim, uma configuração JSON como a seguinte vai ativar o [Automatic HTTPS](/docs/automatic-https) pronta para produção:

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["example.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Hello, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
