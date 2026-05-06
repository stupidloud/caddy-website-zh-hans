---
title: "Primeiros passos"
---

<a id="getting-started"></a>
# Primeiros passos

Bem-vindo ao Caddy! Este tutorial vai explorar os fundamentos do uso do Caddy e ajudar você a se familiarizar com ele em alto nível.

**Objetivos:**
- 🔲 Executar o daemon
- 🔲 Experimentar a API
- 🔲 Dar uma configuração ao Caddy
- 🔲 Testar a configuração
- 🔲 Criar um Caddyfile
- 🔲 Usar o config adapter
- 🔲 Começar com uma configuração inicial
- 🔲 Comparar JSON e Caddyfile
- 🔲 Comparar API e arquivos de configuração
- 🔲 Executar em segundo plano
- 🔲 Reload de configuração sem downtime

**Pré-requisitos:**
- Noções básicas de terminal / linha de comando
- Noções básicas de editor de texto
- `caddy` e `curl` no seu `PATH`

---

**Se você [instalou o Caddy](/docs/install) por meio de um gerenciador de pacotes, ele talvez já esteja rodando como serviço. Se estiver, pare o serviço antes de fazer este tutorial.**

Vamos começar executando-o:

<pre><code class="cmd bash">caddy</code></pre>

Ops; sem um subcomando, o comando `caddy` apenas exibe o texto de ajuda. Você pode usar isso sempre que esquecer o que fazer.

Para iniciar o Caddy como daemon, use o subcomando `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Executar o daemon</aside>

Isso fica bloqueado para sempre, mas o que ele está fazendo? No momento... nada. Por padrão, a configuração ("config") do Caddy está vazia. Podemos verificar isso usando a [admin API](/docs/api) em outro terminal:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

Isto **não** é o seu site: o endpoint de administração em localhost:2019 é usado para controlar o Caddy e fica restrito a localhost por padrão.

</aside>


<aside class="complete">Experimentar a API</aside>

Podemos tornar o Caddy útil dando a ele uma configuração. Isso pode ser feito de muitas formas, mas vamos começar enviando uma requisição POST para o endpoint [/load](/docs/api#post-load) usando `curl` na próxima seção.

## Sua primeira configuração

Para preparar nossa requisição, precisamos criar uma configuração. No fundo, a configuração do Caddy é simplesmente um [documento JSON](/docs/json/).

Salve isto em um arquivo JSON (por exemplo, `caddy.json`):

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

<aside class="tip">

Você não precisa usar arquivos de configuração, mas vamos usá-los neste tutorial. A [admin API](/docs/api) do Caddy foi projetada para uso por outros programas ou scripts.

</aside>


Depois envie o arquivo:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Dar uma configuração ao Caddy</aside>

Podemos verificar se o Caddy aplicou a nova configuração com outra requisição GET:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Teste isso acessando [localhost:2015](http://localhost:2015) no navegador ou usando `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Se você vir _Hello, world!_, parabéns -- está funcionando! É sempre uma boa ideia garantir que a configuração funcione como você espera, especialmente antes de implantar em produção.

<aside class="complete">Testar a configuração</aside>

## Seu primeiro Caddyfile

Isso deu _um trabalho razoável_ só para um Hello World.

Outra forma de configurar o Caddy é com o [**Caddyfile**](/docs/caddyfile). A mesma configuração que escrevemos em JSON acima pode ser expressa simplesmente como:

```caddy
:2015

respond "Hello, world!"
```

Salve isso em um arquivo chamado `Caddyfile` (sem extensão) no diretório atual.

<aside class="complete">Criar um Caddyfile</aside>

Pare o Caddy se ele já estiver em execução (<kbd>Ctrl</kbd>+<kbd>C</kbd>), e então execute:

<pre><code class="cmd bash">caddy adapt</code></pre>

Ou, se você armazenou o Caddyfile em outro lugar ou deu a ele um nome diferente de `Caddyfile`:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile</code></pre>

Você verá saída JSON! O que aconteceu aqui?

Acabamos de usar um [_config adapter_](/docs/config-adapters) para converter nosso Caddyfile para a estrutura JSON nativa do Caddy.

<aside class="complete">Usar o config adapter</aside>

Embora pudéssemos pegar essa saída e fazer outra requisição à API, podemos pular tudo isso porque o comando `caddy` pode fazer isso por nós. Se houver um arquivo chamado Caddyfile no diretório atual e nenhuma outra configuração for especificada, o Caddy vai carregar o Caddyfile, adaptá-lo para nós e executá-lo imediatamente.

Agora que há um Caddyfile na pasta atual, vamos executar `caddy run` novamente:

<pre><code class="cmd bash">caddy run</code></pre>

Ou, se o seu Caddyfile estiver em outro lugar:

<pre><code class="cmd bash">caddy run --config /path/to/Caddyfile</code></pre>

(Se ele tiver outro nome que não comece com "Caddyfile", você precisará especificar `--adapter caddyfile`.)

Agora você pode tentar carregar seu site novamente e verá que ele está funcionando!

<aside class="complete">Começar com uma configuração inicial</aside>

Como você pode ver, há várias maneiras de iniciar o Caddy com uma configuração inicial:

- Um arquivo chamado Caddyfile no diretório atual
- A flag `--config` (opcionalmente com a flag `--adapter`)
- A flag `--resume` (se uma configuração tiver sido carregada anteriormente)

## JSON vs. Caddyfile

Agora você sabe que o Caddyfile simplesmente é convertido para JSON para você.

O Caddyfile parece mais fácil que JSON, mas será que você deve sempre usá-lo? Há prós e contras em cada abordagem. A resposta depende dos seus requisitos e do seu caso de uso.

JSON | Caddyfile
-----|----------
Fácil de gerar | Fácil de escrever à mão
Facilmente programável | Desajeitado para automatizar
Extremamente expressivo | Moderadamente expressivo
Toda a funcionalidade do Caddy | A maior parte da funcionalidade do Caddy
Permite navegação na configuração | Não permite navegação dentro do Caddyfile
Alterações parciais de configuração | Apenas alterações na configuração inteira
Pode ser exportado | Não pode ser exportado
Compatível com todos os endpoints da API | Compatível com alguns endpoints da API
Documentação gerada automaticamente | Documentação escrita manualmente
Ubiquidade | Nicho
Mais eficiente | Mais computacional
Meio sem graça | Meio divertido
**Saiba mais: [estrutura JSON](/docs/json/)** | **Saiba mais: [docs do Caddyfile](/docs/caddyfile)**

Você precisará decidir qual é o melhor para o seu caso de uso.

É importante notar que tanto JSON quanto o Caddyfile (e [qualquer outro config adapter suportado](/docs/config-adapters)) podem ser usados com a [API do Caddy](/docs/api). No entanto, você obtém toda a gama de funcionalidades e recursos da API do Caddy se usar JSON. Ao usar um config adapter, a única forma de carregar ou alterar a configuração com a API é pelo endpoint [/load](/docs/api#post-load).

<aside class="complete">Comparar JSON e Caddyfile</aside>

## API vs. arquivos de configuração

<aside class="tip">

Nos bastidores, até os arquivos de configuração passam pelos endpoints da API do Caddy; o comando `caddy` apenas embrulha essas chamadas de API para você.

</aside>


Você também vai querer decidir se o seu fluxo de trabalho será baseado em API ou em CLI. (Você _pode_ usar tanto a API quanto arquivos de configuração no mesmo servidor, mas não recomendamos isso: o melhor é ter uma única fonte de verdade.)

API | Arquivos de configuração
----|-------------
Fazer alterações de configuração com requisições HTTP | Fazer alterações de configuração com comandos de shell
Fácil de escalar | Difícil de escalar
Difícil de gerenciar manualmente | Fácil de gerenciar manualmente
Muito divertido | Também divertido
**Saiba mais: [tutorial da API](/docs/api-tutorial)** | **Saiba mais: [tutorial do Caddyfile](/docs/caddyfile-tutorial)**

<aside class="tip">
	Gerenciar manualmente a configuração de um servidor pela API é totalmente viável com as ferramentas certas, por exemplo: qualquer aplicativo cliente REST.
</aside>

A escolha entre fluxo baseado em API ou em arquivo de configuração é independente do uso de config adapters: você pode usar JSON mas armazená-lo em um arquivo e usar a interface de linha de comando; por outro lado, também pode usar o Caddyfile com a API.

Mas a maioria das pessoas usará combinações JSON+API ou Caddyfile+CLI.

Como você pode ver, o Caddy é adequado para uma ampla variedade de casos de uso e implantações!

<aside class="complete">Comparar API e arquivos de configuração</aside>

## Iniciar, parar, executar

Como o Caddy é um servidor, ele roda indefinidamente. Isso significa que seu terminal não vai liberar depois de você executar `caddy run` até que o processo seja encerrado (geralmente com <kbd>Ctrl</kbd>+<kbd>C</kbd>).

Embora `caddy run` seja o mais comum e geralmente o recomendado (especialmente ao criar um serviço de sistema!), você pode usar `caddy start` para iniciar o Caddy e deixá-lo rodando em segundo plano:

<pre><code class="cmd bash">caddy start</code></pre>

Isso permitirá que você use o terminal novamente, o que é conveniente em alguns ambientes headless interativos.

Depois, você terá que parar o processo manualmente, já que <kbd>Ctrl</kbd>+<kbd>C</kbd> não o interromperá:

<pre><code class="cmd bash">caddy stop</code></pre>

Ou use o [endpoint /stop](/docs/api#post-stop) da API.

<aside class="complete">Executar em segundo plano</aside>

## Recarregando a configuração

Seu servidor pode realizar reloads/alterações de configuração sem downtime.

Todos os [endpoints da API](/docs/api) que carregam ou alteram configuração são tolerantes e feitos sem downtime.

Ao usar a linha de comando, porém, pode ser tentador usar <kbd>Ctrl</kbd>+<kbd>C</kbd> para parar o servidor e iniciá-lo novamente para carregar a nova configuração. Não faça isso: parar e iniciar o servidor é algo separado das mudanças de configuração e resultará em downtime.

<aside class="tip">
	Parar seu servidor vai fazer o servidor cair.
</aside>

Em vez disso, use o comando [`caddy reload`](/docs/command-line#caddy-reload) para uma mudança graciosa de configuração:

<pre><code class="cmd bash">caddy reload</code></pre>

Isso, na prática, apenas usa a API por baixo dos panos. Ele vai carregar e, se necessário, adaptar seu arquivo de configuração para JSON, e então substituir graciosamente a configuração ativa sem downtime.

Se houver erros ao carregar a nova configuração, o Caddy reverte para a última configuração funcional.

<aside class="tip">
	Tecnicamente, a nova configuração é iniciada antes de a antiga ser parada, então por um breve período as duas configurações ficam em execução! Se a nova falhar, ela é abortada com erro, enquanto a antiga simplesmente não é parada.
</aside>

<aside class="complete">Reload de configuração sem downtime</aside>
