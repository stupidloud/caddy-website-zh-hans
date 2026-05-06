---
title: "Tutorial do Caddyfile"
---

# Tutorial do Caddyfile

Este tutorial vai ensinar os fundamentos do [Caddyfile HTTP](/docs/caddyfile) para que você consiga produzir rapidamente configurações de site funcionais e com boa aparência.

**Objetivos:**
- 🔲 Primeiro site
- 🔲 Servidor de arquivos estáticos
- 🔲 Templates
- 🔲 Compressão
- 🔲 Vários sites
- 🔲 Matchers
- 🔲 Variáveis de ambiente
- 🔲 Comentários

**Pré-requisitos:**
- Noções básicas de terminal / linha de comando
- Noções básicas de editor de texto
- `caddy` no seu `PATH`

---

Crie um novo arquivo de texto chamado `Caddyfile` (sem extensão).

A primeira coisa que você deve digitar é o [endereço](/docs/caddyfile/concepts#addresses) do seu site:

```caddy
localhost
```

<aside class="tip">

Se as portas HTTP e HTTPS (80 e 443, respectivamente) forem portas privilegiadas no seu sistema operacional, você precisará executar com privilégios elevados ou usar uma porta mais alta. Para usar uma porta mais alta, basta mudar o endereço para algo como `localhost:2015` e alterar a porta HTTP usando a opção [http_port](/docs/caddyfile/options) do Caddyfile.

</aside>


Depois pressione Enter e digite o que você quer que ele faça. Para este tutorial, faça seu Caddyfile ficar assim:

```caddy
localhost

respond "Hello, world!"
```

Salve isso e execute o Caddy (como este é um tutorial de treinamento, usaremos a flag `--watch` para que as mudanças no Caddyfile sejam aplicadas automaticamente):

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

Se aparecerem erros de permissão, tente usar uma porta mais alta no seu endereço (como `localhost:2015`) e [mude a porta HTTP](/docs/caddyfile/options), ou execute com privilégios elevados.

</aside>


Na primeira vez, você será solicitado a informar sua senha. Isso é para que o Caddy possa servir seu site via HTTPS.

<aside class="tip">

O Caddy serve todos os sites via HTTPS por padrão, desde que um host ou IP faça parte do endereço do site. O [Automatic HTTPS](/docs/automatic-https) pode ser desativado prefixando explicitamente o endereço com `http://`.

</aside>


<aside class="complete">Primeiro site</aside>

Abra [localhost](https://localhost) no navegador e veja seu servidor web funcionando, com HTTPS incluso!

<aside class="tip">
	Talvez você precise reiniciar o navegador se aparecer um erro de certificado na primeira vez.
</aside>

Isso não é particularmente empolgante, então vamos mudar nossa resposta estática para um [servidor de arquivos](/docs/caddyfile/directives/file_server) com listagem de diretório habilitada:

```caddy
localhost

file_server browse
```

Salve o Caddyfile e, em seguida, recarregue a aba do navegador. Você deverá ver uma lista de arquivos ou uma página HTML, se houver um arquivo index no diretório atual.

<aside class="complete">Servidor de arquivos estáticos</aside>

## Adicionando funcionalidade

Vamos fazer algo interessante com nosso servidor de arquivos: servir uma página com template. Crie um novo arquivo e cole isto nele:

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Caddy tutorial</title>
	</head>
	<body>
		Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

Salve isso como `caddy.html` no diretório atual e abra no navegador: [https://localhost/caddy.html](https://localhost/caddy.html)

A saída é:

```
Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

Espere um pouco. Deveríamos ver a data de hoje. Por que não funcionou? Porque o servidor ainda não foi configurado para avaliar templates! É fácil corrigir: basta adicionar uma linha ao Caddyfile para que ele fique assim:

```caddy
localhost

templates
file_server browse
```

Salve isso e recarregue a aba do navegador. Você deverá ver:

```
Page loaded at: {{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

Com o [módulo templates](/docs/modules/http.handlers.templates) do Caddy, você pode fazer várias coisas úteis com arquivos estáticos, como incluir outros arquivos HTML, fazer sub-requisições, definir cabeçalhos de resposta, trabalhar com estruturas de dados e muito mais!

<aside class="complete">Templates</aside>

É uma boa prática comprimir respostas com um algoritmo rápido e moderno. Vamos habilitar suporte a Gzip e Zstandard usando a diretiva [`encode`](/docs/caddyfile/directives/encode):

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">Compressão</aside>

Esse é o processo básico para colocar um site semiavançado e pronto para produção em funcionamento!

Quando estiver pronto para ativar o [Automatic HTTPS](/docs/automatic-https), basta substituir o endereço do site (`localhost` no nosso tutorial) pelo seu nome de domínio. Veja nosso [guia rápido de HTTPS](/docs/quick-starts/https) para mais informações.

## Vários sites

Com o Caddyfile atual, só podemos ter uma definição de site! Apenas a primeira linha pode ser o(s) endereço(s) do site, e todo o restante do arquivo precisa ser diretiva para aquele site.

Mas é fácil mudar isso para que possamos adicionar mais sites!

Nosso Caddyfile até agora:

```caddy
localhost

encode
templates
file_server browse
```

é equivalente a isto:

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

exceto que a segunda versão permite adicionar mais sites.

Ao envolver o bloco do site com chaves `{ }`, conseguimos definir vários sites diferentes no mesmo Caddyfile.

Por exemplo:

```caddy
:8080 {
	respond "I am 8080"
}

:8081 {
	respond "I am 8081"
}
```

Ao envolver blocos de site com chaves, apenas [endereços](/docs/caddyfile/concepts#addresses) aparecem fora das chaves e apenas [diretivas](/docs/caddyfile/directives) aparecem dentro delas.

Para vários sites que compartilham a mesma configuração, você pode adicionar mais endereços, por exemplo:

```caddy
:8080, :8081 {
	...
}
```

Você pode então definir quantos sites diferentes quiser, desde que cada endereço seja único.

<aside class="complete">Vários sites</aside>

## Matchers

Talvez queiramos aplicar algumas diretivas apenas a determinadas requisições. Por exemplo, suponha que queremos ter ao mesmo tempo um servidor de arquivos e um reverse proxy, mas obviamente não podemos fazer os dois em todas as requisições! Ou o servidor de arquivos escreverá uma resposta com um arquivo estático, ou o reverse proxy enviará a requisição para um backend e devolverá a resposta dele.

Essa configuração não vai funcionar como queremos (`reverse_proxy` terá precedência por causa da [ordem das diretivas](/docs/caddyfile/directives#directive-order)):

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

Na prática, talvez queiramos usar o reverse proxy apenas para requisições de API, ou seja, requisições com um path base de `/api/`. Isso é fácil de fazer adicionando um [token de matcher](/docs/caddyfile/matchers#syntax):

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

Aí está; agora o reverse proxy terá prioridade para todas as requisições que comecem com `/api/`.

A parte `/api/*` que acabamos de adicionar é chamada de **token de matcher**. Você pode perceber que é um token de matcher porque ele começa com uma barra `/` e aparece logo depois da diretiva (mas você sempre pode conferir na [documentação da diretiva](/docs/caddyfile/directives) para ter certeza).

Matchers são realmente poderosos. Você pode declarar matchers nomeados e usá-los como `@name` para combinar mais coisas além do path da requisição! Reserve um momento para [aprender mais sobre matchers](/docs/caddyfile/matchers) antes de continuar!

<aside class="complete">Matchers</aside>

## Variáveis de ambiente

O adaptador do Caddyfile permite substituir [variáveis de ambiente](/docs/caddyfile/concepts#environment-variables) antes de o Caddyfile ser analisado.

Primeiro, defina uma variável de ambiente (no mesmo shell que executa o Caddy):

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

Então você pode usá-la assim no Caddyfile:

```caddy
{$SITE_ADDRESS}

file_server
```

Antes de o Caddyfile ser analisado, isso será expandido para:

```caddy
localhost:9055

file_server
```

Você pode usar variáveis de ambiente em qualquer lugar do Caddyfile, para qualquer quantidade de tokens.

<aside class="complete">Variáveis de ambiente</aside>

## Comentários

Mais uma coisa que pode ser muito útil: se você quiser fazer uma observação ou anotação no seu Caddyfile, pode usar comentários, começando com `#`:

```caddy
# this starts a comment
```

<aside class="complete">Comentários</aside>

## Leitura adicional

- [Conceitos do Caddyfile](/docs/caddyfile/concepts)
- [Diretivas](/docs/caddyfile/directives)
- [Padrões comuns](/docs/caddyfile/patterns)
