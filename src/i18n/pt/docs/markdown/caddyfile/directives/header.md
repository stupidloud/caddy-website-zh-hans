---
title: header (diretiva do Caddyfile)
---

# header

Manipula campos de cabeçalho de resposta HTTP. Pode definir, adicionar e apagar valores de cabeçalho, ou fazer substituições usando expressões regulares.

Por padrão, as operações de header são executadas imediatamente, a menos que algum dos cabeçalhos esteja sendo apagado (`-` prefixo) ou esteja sendo definido um valor padrão (`?` prefixo). Nesses casos, as operações de header são automaticamente adiadas até o momento em que estão sendo escritas para o cliente.

Para manipular cabeçalhos de requisição HTTP, você pode usar a diretiva [`request_header`](request_header).


## Sintaxe

```caddy-d
header [<matcher>] [[+|-|?|>]<field> [<value>|<find>] [<replace>]] {
	# Adicionar
	+<field> <value>

	# Definir
	<field> <value>

	# Definir com defer
	><field> <value>

	# Apagar
	-<field>

	# Substituir
	<field> <find> <replace>

	# Substituir com defer
	><field> <find> <replace>

	# Padrão
	?<field> <value>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;field&gt;** é o nome do campo de cabeçalho.

  Sem prefixo, o campo é definido (sobrescrito).

  Com o prefixo `+`, o campo é adicionado em vez de sobrescrito (definido) se ele já existir; campos de cabeçalho podem aparecer mais de uma vez em uma resposta.

  Com o prefixo `-`, o campo é apagado. O campo pode usar curingas `*` de prefixo ou sufixo para apagar todos os campos correspondentes.

  Com o prefixo `?`, é definido um valor padrão para o campo. O campo só é escrito se ainda não existir.

  Com o prefixo `>`, o campo é definido e o `defer` é habilitado, como atalho.

- **&lt;value&gt;** é o valor do campo de cabeçalho, ao adicionar ou definir um campo.

- **&lt;find&gt;** é a expressão regular a ser pesquisada. Placeholders podem ser usados para entrada dinâmica no padrão de busca. A linguagem de expressão regular usada é RE2, incluída no Go. Veja a [referência de sintaxe do RE2](https://github.com/google/re2/wiki/Syntax) e a [visão geral da sintaxe de regexp do Go](https://pkg.go.dev/regexp/syntax).

- **&lt;replace&gt;** é o valor de substituição; obrigatório se estiver fazendo busca e substituição. Use `$1` ou `$2` e assim por diante para referenciar grupos de captura do padrão de busca. Se o valor de substituição for `""`, o texto correspondente será removido do valor. Veja a [documentação do Go](https://golang.org/pkg/regexp/#Regexp.Expand) para detalhes.

- **defer** adia a execução das operações de header até a resposta ser enviada ao cliente. Essa opção é habilitada automaticamente nas seguintes condições:
	- Quando algum campo de cabeçalho é apagado usando `-`.
	- Quando um valor padrão é definido com `?`.
	- Quando o prefixo `>` é usado em uma operação de definir ou substituir.
	- Quando uma ou mais condições `match` estão presentes.

- **match** <span id="match"/> é um [matcher de resposta](/docs/caddyfile/response-matchers) inline. As operações de header são aplicadas somente às respostas que satisfazem as condições especificadas.

Para várias manipulações de cabeçalho, você pode abrir um bloco e especificar uma manipulação por linha, da mesma maneira.

Ao usar o prefixo `?` para definir um valor padrão de cabeçalho, ele é automaticamente separado em seu próprio handler `header`, se estiver em um bloco `header` com várias operações de cabeçalho. [Nos bastidores](/docs/modules/http.handlers.headers#response/require), usar `?` configura um [matcher de resposta](/docs/caddyfile/response-matchers) que se aplica a todo o handler da diretiva, que só aplica as operações de header (como `defer`), mas apenas se o campo ainda não tiver sido definido.


## Exemplos

Definir um campo de cabeçalho personalizado em todas as respostas:

```caddy-d
header Custom-Header "My value"
```

Remover o cabeçalho "Hidden":

```caddy-d
header -Hidden
```

Substituir `http://` por `https://` em qualquer cabeçalho Location:

```caddy-d
header Location http:// https://
```

Definir cabeçalhos de segurança e privacidade em todas as páginas: (**AVISO:** use apenas se você entender as implicações!)

```caddy-d
header {
	# desativa o rastreamento do FLoC
	Permissions-Policy interest-cohort=()

	# habilita HSTS
	Strict-Transport-Security max-age=31536000;

	# impede que clientes deduzam o tipo de mídia pelo conteúdo
	X-Content-Type-Options nosniff

	# proteção contra clickjacking
	X-Frame-Options DENY
}
```

Várias diretivas header que devem ser mutuamente exclusivas:

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

Definir uma expiração de cache padrão se o upstream não definir uma:

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

Marcar todas as respostas bem-sucedidas para requisições GET como cacheáveis por até uma hora:

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

Impedir o cache de respostas de erro em caso de exceção no servidor upstream:

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

Marcar respostas em modo claro como cacheáveis separadamente das respostas em modo escuro, se o servidor upstream suportar client hints:
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

Evitar cabeçalhos CORS permissivos demais substituindo valores curinga por um domínio específico:
```caddy-d
header >Access-Control-Allow-Origin "\*" "allowed-partner.com"
reverse_proxy upstream:443
```
**Observação**: em operações de substituição, o valor `<find>` é interpretado como uma expressão regular. Para corresponder ao caractere `*`, ele precisa ser escapado com uma barra invertida, como mostrado no exemplo acima.

Alternativamente, você pode usar um [matcher de resposta](/docs/caddyfile/response-matchers) para corresponder literalmente a um valor de cabeçalho:
```caddy-d
header Access-Control-Allow-Origin "allowed-partner.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

Para sobrescrever a expiração de cache que um upstream de proxy definiu para caminhos que começam com `/no-cache`; habilitar `defer` é necessário para garantir que o cabeçalho seja definido _depois_ que o proxy escrever seus cabeçalhos:

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

Para fazer uma atualização adiada de um cabeçalho `Set-Cookie` para adicionar `SameSite=None`; um capture de regexp é usado para recuperar o valor existente, e `$1` o reinsere no início com a opção adicional anexada:

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
