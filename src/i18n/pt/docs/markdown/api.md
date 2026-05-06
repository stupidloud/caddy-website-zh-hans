---
title: "API"
---

# API

O Caddy é configurado por meio de um endpoint de administração que pode ser acessado via HTTP usando uma API [REST <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Representational_state_transfer). Você pode [configurar esse endpoint](/docs/json/admin/) na configuração do Caddy.

**Endereço padrão: `localhost:2019`**

O endereço padrão pode ser alterado definindo a variável de ambiente `CADDY_ADMIN`. Alguns métodos de instalação podem definir isso para algo diferente. O endereço na configuração do Caddy sempre tem precedência sobre o padrão.

<aside class="tip">
	Se você estiver executando código não confiável no seu servidor (péssima ideia 😬), proteja seu endpoint de administração isolando processos, corrigindo programas vulneráveis e configurando o endpoint para vincular-se a um unix socket com permissões apropriadas.
</aside>

A configuração mais recente será salva em disco depois de qualquer alteração (a menos que isso esteja [desativado](/docs/json/admin/config/)). Você pode retomar a última configuração funcional após uma reinicialização com [`caddy run --resume`](/docs/command-line#caddy-run), o que garante durabilidade da configuração em caso de falta de energia ou evento semelhante.

Para começar a usar a API, experimente nosso [tutorial da API](/docs/api-tutorial) ou, se você tiver apenas um minuto, nosso [guia rápido da API](/docs/quick-starts/api).

---

- **[POST /load](#post-load)**
  Define ou substitui a configuração ativa

- **[POST /stop](#post-stop)**
  Para a configuração ativa e encerra o processo

- **[GET /config/[path]](#get-configpath)**
  Exporta a configuração no caminho indicado

- **[POST /config/[path]](#post-configpath)**
  Define ou substitui um objeto; acrescenta em arrays
  
- **[PUT /config/[path]](#put-configpath)**
  Cria um novo objeto; insere em arrays

- **[PATCH /config/[path]](#patch-configpath)**
  Substitui um objeto existente ou um elemento de array

- **[DELETE /config/[path]](#delete-configpath)**
  Remove o valor no caminho indicado

- **[Usando `@id` em JSON](#using-id-in-json)**
  Navega facilmente pela estrutura da configuração

- **[Alterações concorrentes na configuração](#concurrent-config-changes)**
  Evita colisões quando alterações não sincronizadas são feitas na configuração

- **[POST /adapt](#post-adapt)**
  Adapta uma configuração para JSON sem executá-la

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  Retorna informações sobre uma CA específica do [app PKI](/docs/json/apps/pki/)

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  Retorna a cadeia de certificados de uma CA específica do [app PKI](/docs/json/apps/pki/)

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  Retorna o status atual dos upstreams configurados do proxy


<a id="post-load"></a>
## POST /load

Define a configuração do Caddy, substituindo qualquer configuração anterior. Isso bloqueia até o reload concluir ou falhar. As mudanças de configuração são leves, eficientes e não causam downtime. Se a nova configuração falhar por qualquer motivo, a configuração antiga é restaurada sem interrupção.

Este endpoint suporta diferentes formatos de configuração usando adaptadores de configuração. O cabeçalho `Content-Type` da requisição indica o formato da configuração no corpo. Normalmente, isso deve ser `application/json`, que representa o formato nativo de configuração do Caddy. Para outro formato, especifique o `Content-Type` apropriado, de modo que a parte depois da barra `/` seja o nome do adaptador de configuração a ser usado. Por exemplo, ao enviar um Caddyfile, use algo como `text/caddyfile`; para JSON 5, use algo como `application/json5`; e assim por diante.

Se a nova configuração for igual à atual, nenhum reload ocorrerá. Para forçar um reload, defina `Cache-Control: must-revalidate` nos cabeçalhos da requisição.

### Exemplos

Defina uma nova configuração ativa:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

Observação: a flag `-d` do curl remove quebras de linha; se o seu formato de configuração for sensível a quebras de linha (por exemplo, o Caddyfile), use `--data-binary` em vez disso:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


<a id="post-stop"></a>
## POST /stop

Desliga o servidor de forma graciosa e encerra o processo. Para parar apenas a configuração em execução sem encerrar o processo, use [DELETE /config/](#delete-configpath).

### Exemplo

Parar o processo:

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


<a id="get-configpath"></a>
## GET /config/[path]

Exporta a configuração atual do Caddy no caminho indicado. Retorna um corpo JSON.

### Exemplos

Exportar a configuração inteira e formatar para leitura:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					]
				}
			}
		}
	}
}</code></pre>

Exportar apenas os endereços de escuta:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[":443"]</code></pre>


<a id="post-configpath"></a>
## POST /config/[path]

Altera a configuração do Caddy no caminho indicado para o corpo JSON da requisição. Se o valor de destino for um array, POST acrescenta; se for um objeto, cria ou substitui.

Como caso especial, vários itens podem ser adicionados a um array se:

1. o caminho termina em `/...`
2. o elemento do caminho antes de `/...` referencia um array
3. o payload é um array

Nesse caso, os elementos do array do payload serão expandidos e cada um será acrescentado ao array de destino. Em termos de Go, isso teria o mesmo efeito que:

```go
baseSlice = append(baseSlice, newElems...)
```

### Exemplos

Adicionar um endereço de escuta:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

Adicionar vários endereços de escuta:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

<a id="put-configpath"></a>
## PUT /config/[path]

Altera a configuração do Caddy no caminho indicado para o corpo JSON da requisição. Se o valor de destino for uma posição (índice) em um array, PUT insere; se for um objeto, ele cria estritamente um novo valor.

### Exemplo

Adicionar um endereço de escuta na primeira posição:

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


<a id="patch-configpath"></a>
## PATCH /config/[path]

Altera a configuração do Caddy no caminho indicado para o corpo JSON da requisição. PATCH substitui estritamente um valor existente ou um elemento de array.

### Exemplo

Substituir os endereços de escuta:

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>


<a id="delete-configpath"></a>
## DELETE /config/[path]

Remove a configuração do Caddy no caminho indicado. DELETE apaga o valor de destino.

### Exemplos

Para descarregar toda a configuração atual, mas manter o processo em execução:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

Para parar apenas um dos seus servidores HTTP:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


<a id="using-id-in-json"></a>
## Usando `@id` em JSON

Você pode incorporar IDs no seu documento JSON para acessar diretamente essas partes com mais facilidade.

Basta adicionar um campo chamado `"@id"` a um objeto e dar a ele um nome exclusivo. Por exemplo, se você tivesse um handler de reverse proxy que quisesse acessar com frequência:

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

Para usá-lo, faça uma requisição ao endpoint `/id/` da API da mesma forma que faria com o endpoint `/config/` correspondente, mas sem o caminho inteiro. O ID leva a requisição diretamente para aquele escopo da configuração.

Por exemplo, para acessar os upstreams do reverse proxy sem um ID, o caminho seria algo como

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

mas com um ID, o caminho se torna

```
/id/my_proxy/upstreams
```

o que é muito mais fácil de lembrar e escrever manualmente.

<a id="concurrent-config-changes"></a>
## Alterações concorrentes na configuração

<aside class="tip">

Esta seção vale para todos os endpoints `/config/`. Ela é experimental e pode mudar.

</aside>


A API de configuração do Caddy fornece garantias [ACID <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/ACID) para requisições individuais, mas alterações que envolvem mais de uma requisição estão sujeitas a colisões ou perda de dados se não forem sincronizadas corretamente.

Por exemplo, dois clientes podem fazer `GET /config/foo` ao mesmo tempo, editar dentro daquele escopo (caminho da configuração) e então chamar `POST|PUT|PATCH|DELETE /config/foo/...` ao mesmo tempo para aplicar suas mudanças, resultando em uma colisão: um sobrescreverá o outro, ou o segundo pode deixar a configuração em um estado indesejado porque foi aplicada a uma versão diferente da configuração daquela com a qual ele foi preparado. Isso acontece porque as mudanças não têm conhecimento uma da outra.

A API do Caddy não oferece suporte a transações que atravessem várias requisições, e HTTP é um protocolo sem estado. No entanto, você pode usar os cabeçalhos `Etag` e `If-Match` para detectar e evitar colisões em qualquer alteração, como uma forma de controle otimista de concorrência. Isso é útil se houver qualquer chance de você estar usando os endpoints `/config/...` do Caddy de forma concorrente e sem sincronização. Todas as respostas a requisições `GET /config/...` têm um cabeçalho HTTP chamado `Etag` que contém o caminho e um hash do conteúdo naquele escopo (por exemplo, `Etag: "/config/apps/http/servers 65760b8e"`). Basta definir o cabeçalho `If-Match` em uma requisição de mutação com o valor de `Etag` de uma requisição `GET` anterior.

O algoritmo básico é o seguinte:

1. Faça uma requisição `GET` para qualquer escopo `S` dentro da configuração. Guarde o cabeçalho `Etag` da resposta.
2. Faça a alteração desejada na configuração retornada.
3. Faça uma requisição `POST|PUT|PATCH|DELETE` dentro do escopo `S`, definindo o cabeçalho `If-Match` com o valor armazenado de `Etag`.
4. Se a resposta for HTTP 412 (Precondition Failed), repita a partir do passo 1, ou desista depois de muitas tentativas.

Esse algoritmo permite fazer várias alterações sobrepostas à configuração do Caddy com segurança, sem sincronização explícita. Ele foi projetado para que alterações simultâneas em partes diferentes da configuração não exijam nova tentativa: apenas alterações que se sobrepõem ao mesmo escopo da configuração podem causar colisão e, portanto, exigir retry.


<a id="post-adapt"></a>
## POST /adapt

Adapta uma configuração para JSON do Caddy sem carregá-la ou executá-la. Se for bem-sucedido, o documento JSON resultante será retornado no corpo da resposta.

O cabeçalho `Content-Type` é usado para especificar o formato da configuração da mesma forma que [em `/load`](#post-load). Por exemplo, para adaptar um Caddyfile, defina `Content-Type: text/caddyfile`.

Esse endpoint adaptará qualquer formato de configuração, desde que o [adaptador de configuração](/docs/config-adapters) associado esteja incorporado ao seu build do Caddy.

### Exemplos

Adaptar um Caddyfile para JSON:

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


<a id="get-pkicaltidgt"></a>
## GET /pki/ca/&lt;id&gt;

Retorna informações sobre uma CA específica do [app PKI](/docs/json/apps/pki/) pelo seu ID. Se o ID da CA solicitado for o padrão (`local`), a CA será provisionada se ainda não tiver sido. Outros IDs de CA retornarão erro se ainda não tiverem sido provisionados anteriormente.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


<a id="get-pkicaltidgtcertificates"></a>
## GET /pki/ca/&lt;id&gt;/certificates

Retorna a cadeia de certificados de uma CA específica do [app PKI](/docs/json/apps/pki/) pelo seu ID. Se o ID da CA solicitado for o padrão (`local`), a CA será provisionada se ainda não tiver sido. Outros IDs de CA retornarão erro se ainda não tiverem sido provisionados anteriormente.

Este endpoint é usado internamente pelo comando [`caddy trust`](/docs/command-line#caddy-trust) para permitir a instalação do certificado raiz da CA no trust store do seu sistema.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


<a id="get-reverse-proxyupstreams"></a>
## GET /reverse_proxy/upstreams

Retorna o status atual dos upstreams (backends) configurados do reverse proxy como um documento JSON.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

Cada entrada no array JSON é um [upstream](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/) configurado e armazenado no pool global de upstreams.

- **address** é o endereço de conexão do upstream.
- **num_requests** é a quantidade de requisições ativas que o upstream está tratando no momento.
- **fails** é o número atual de requisições com falha lembradas, conforme configurado pelos health checks passivos.

Se seu objetivo for determinar a disponibilidade de um backend, você precisará cruzar as propriedades relevantes do upstream com a configuração do handler que está usando. Por exemplo, se você habilitou [health checks passivos](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/) para seus proxies, então também precisa levar em conta os valores `fails` e `num_requests` para determinar se um upstream é considerado disponível: verifique se `fails` é menor que o número máximo de falhas configurado para seu proxy (ou seja, [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/)), e se `num_requests` é menor ou igual à quantidade configurada de requisições máximas por upstream (ou seja, [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/) para o proxy inteiro, ou [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/) para upstreams individuais).
