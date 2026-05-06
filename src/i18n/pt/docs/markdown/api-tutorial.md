---
title: "Tutorial da API"
---

# Tutorial da API

Este tutorial vai mostrar como usar a [admin API](/docs/api) do Caddy, que permite automatizar tudo de forma programável.

**Objetivos:**
- 🔲 Executar o daemon
- 🔲 Dar uma configuração ao Caddy
- 🔲 Testar a configuração
- 🔲 Substituir a configuração ativa
- 🔲 Navegar pela configuração
- 🔲 Usar tags `@id`

**Pré-requisitos:**
- Noções básicas de terminal / linha de comando
- Experiência básica com JSON
- `caddy` e `curl` no seu `PATH`

---

Para iniciar o daemon do Caddy, use o subcomando `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Executar o daemon</aside>

Isso fica bloqueado para sempre, mas o que ele está fazendo? Neste momento... nada. Por padrão, a configuração do Caddy ("config") está vazia. Podemos verificar isso usando a [admin API](/docs/api) em outro terminal:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Podemos tornar o Caddy útil dando a ele uma configuração. Uma forma de fazer isso é enviar uma requisição POST para o endpoint [/load](/docs/api#post-load). Como em qualquer requisição HTTP, há muitas formas de fazer isso, mas neste tutorial usaremos `curl`.

## Sua primeira configuração

Para preparar a requisição, precisamos criar uma configuração. A configuração do Caddy é simplesmente um [documento JSON](/docs/json/) (ou [qualquer coisa que possa ser convertida em JSON](/docs/config-adapters)).

<aside class="tip">
	Arquivos de configuração não são obrigatórios. A API de configuração sempre pode ser usada sem arquivos, o que é útil quando se automatiza algo. Este tutorial usa um arquivo porque é mais conveniente para editar manualmente.
</aside>

Salve isto em um arquivo JSON:

```json
{
	"apps": {
		"http": {
			"servers": {
				"example": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

Depois faça o upload:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	Não se esqueça do @ antes do nome do arquivo; isso diz ao curl que você está enviando um arquivo.
</aside>

<aside class="complete">Dar uma configuração ao Caddy</aside>

Podemos verificar se o Caddy aplicou a nova configuração com outra requisição GET:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Teste isso acessando [localhost:2015](http://localhost:2015) no navegador ou usando `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">Testar a configuração</aside>

Se você vir _Hello, world!_, então parabéns -- está funcionando! É sempre uma boa ideia garantir que a configuração está fazendo o que você espera, especialmente antes de colocar em produção.

Vamos mudar nossa mensagem de boas-vindas de "Hello world!" para algo um pouco mais motivador: "I can do hard things." Faça essa alteração no arquivo de configuração, de modo que o objeto handler fique assim:

```json
{
	"handler": "static_response",
	"body": "I can do hard things."
}
```

Salve o arquivo de configuração e, em seguida, atualize a configuração ativa do Caddy executando a mesma requisição POST novamente:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Substituir a configuração ativa</aside>

Por garantia, verifique se a configuração foi atualizada:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Teste isso recarregando a página no navegador (ou executando `curl` novamente), e você verá uma mensagem inspiradora!

## Navegação pela configuração

Em vez de enviar o arquivo de configuração inteiro para uma pequena alteração, vamos usar um recurso poderoso da API do Caddy para fazer a mudança sem tocar no arquivo de configuração.

<aside class="tip">
	Fazer pequenas alterações em servidores de produção substituindo a configuração inteira, como fizemos acima, pode ser perigoso; é como ter acesso root a um sistema de arquivos. A API do Caddy permite limitar o escopo das alterações para garantir que outras partes da configuração não sejam modificadas por acidente.
</aside>

Usando o caminho da URI da requisição, podemos navegar pela estrutura da configuração e atualizar apenas a string da mensagem (deslize para a direita se o conteúdo estiver cortado):

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Work smarter, not harder."'
</code></pre>


<aside class="tip">

Sempre que você altera a configuração usando a API, o Caddy mantém uma cópia persistida da nova configuração para que você possa [**--resume**](/docs/command-line#caddy-run) mais tarde!

</aside>


Você pode verificar se funcionou com uma requisição GET semelhante, por exemplo:

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

Você deverá ver:

```json
[{"handle":[{"body":"Work smarter, not harder.","handler":"static_response"}]}]
```


<aside class="tip">

Você pode usar o [`jq` <img src="/old/resources/images/external-link.svg" class="external-link">](https://stedolan.github.io/jq/) para embelezar a saída JSON: **`curl ... | jq`**

</aside>


<aside class="complete">Navegar pela configuração</aside>

**Observação importante:** isso deveria ser óbvio, mas, depois que você usa a API para fazer uma alteração que não está no arquivo de configuração original, o arquivo de configuração passa a ficar obsoleto. Há algumas formas de lidar com isso:

- Use o `--resume` do comando [caddy run](/docs/command-line#caddy-run) para usar a última configuração ativa.
- Não misture o uso de arquivos de configuração com alterações via API; tenha uma única fonte de verdade.
- [Exporte a nova configuração do Caddy](/docs/api#get-configpath) com uma requisição GET subsequente (menos recomendado que as duas opções anteriores).

## Usando `@id` em JSON

A navegação pela configuração certamente é útil, mas os caminhos ficam um pouco longos, não acha?

Podemos dar ao nosso objeto handler uma tag [`@id`](/docs/api#using-id-in-json) para facilitar o acesso:

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

Isso adiciona uma propriedade ao nosso objeto handler: `"@id": "msg"`, então agora ele fica assim:

```json
{
	"@id": "msg",
	"body": "Work smarter, not harder.",
	"handler": "static_response"
}
```


<aside class="tip">

Tags **@id** podem ser colocadas em qualquer objeto e podem ter qualquer valor primitivo (normalmente uma string). [Saiba mais](/docs/api#using-id-in-json)

</aside>


Podemos então acessá-lo diretamente:

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

E agora podemos alterar a mensagem com um caminho mais curto:

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Some shortcuts are good."'
</code></pre>

E verificar novamente:

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete">Usar tags <code>@id</code></aside>
