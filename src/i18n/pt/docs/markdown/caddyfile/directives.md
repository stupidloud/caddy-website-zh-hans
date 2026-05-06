---
title: Diretivas do Caddyfile
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

# Diretivas do Caddyfile

Diretivas são palavras-chave funcionais que aparecem dentro de [blocos](/docs/caddyfile/concepts#blocks) de site. Às vezes, elas podem abrir seus próprios blocos, que podem conter _subdiretivas_, mas diretivas **não podem** ser usadas dentro de outras diretivas, a menos que seja indicado. Por exemplo, você não pode usar `basic_auth` dentro de um bloco `file_server`, porque `file_server` não sabe fazer autenticação. No entanto, você _pode_ usar algumas diretivas dentro de blocos especiais como `handle` e `route`, porque eles foram projetados especificamente para agrupar diretivas de handler HTTP.

- [Sintaxe](#syntax)
- [Ordem das diretivas](#directive-order)
- [Algoritmo de ordenação](#sorting-algorithm)

As diretivas a seguir vêm por padrão com o Caddy e podem ser usadas no Caddyfile HTTP:

<div id="directive-table">

Directive | Description
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | Interrompe a requisição HTTP
**[acme_server](/docs/caddyfile/directives/acme_server)** | Um servidor ACME embutido
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | Impõe autenticação HTTP Basic
**[bind](/docs/caddyfile/directives/bind)** | Personaliza o endereço de socket do servidor
**[encode](/docs/caddyfile/directives/encode)** | Codifica as respostas (normalmente compactando-as)
**[error](/docs/caddyfile/directives/error)** | Dispara um erro
**[file_server](/docs/caddyfile/directives/file_server)** | Serve arquivos do disco
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | Delega a autenticação a um serviço externo
**[fs](/docs/caddyfile/directives/fs)** | Define o sistema de arquivos usado para E/S de arquivos
**[handle](/docs/caddyfile/directives/handle)** | Um grupo mutuamente exclusivo de diretivas
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | Define rotas para tratar erros
**[handle_path](/docs/caddyfile/directives/handle_path)** | Como `handle`, mas remove o prefixo do caminho
**[header](/docs/caddyfile/directives/header)** | Define ou remove cabeçalhos de resposta
**[import](/docs/caddyfile/directives/import)** | Inclui snippets ou arquivos
**[intercept](/docs/caddyfile/directives/intercept)** | Intercepta respostas escritas por outros handlers
**[invoke](/docs/caddyfile/directives/invoke)** | Invoca uma rota nomeada
**[log](/docs/caddyfile/directives/log)** | Ativa o registro de acesso/requisição
**[log_append](/docs/caddyfile/directives/log_append)** | Adiciona um campo ao log de acesso
**[log_skip](/docs/caddyfile/directives/log_skip)** | Ignora o logging de acesso para requisições correspondentes
**[log_name](/docs/caddyfile/directives/log_name)** | Substitui o(s) nome(s) do logger usado(s) para escrever
**[map](/docs/caddyfile/directives/map)** | Mapeia um valor de entrada para uma ou mais saídas
**[method](/docs/caddyfile/directives/method)** | Altera internamente o método HTTP
**[metrics](/docs/caddyfile/directives/metrics)** | Configura o endpoint de exposição de métricas do Prometheus
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | Serve sites PHP sobre FastCGI
**[push](/docs/caddyfile/directives/push)** | Envia conteúdo ao cliente usando HTTP/2 server push
**[redir](/docs/caddyfile/directives/redir)** | Emite um redirecionamento HTTP para o cliente
**[request_body](/docs/caddyfile/directives/request_body)** | Manipula o corpo da requisição
**[request_header](/docs/caddyfile/directives/request_header)** | Manipula os cabeçalhos da requisição
**[respond](/docs/caddyfile/directives/respond)** | Escreve uma resposta codificada diretamente para o cliente
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | Um reverse proxy poderoso e extensível
**[rewrite](/docs/caddyfile/directives/rewrite)** | Reescreve a requisição internamente
**[root](/docs/caddyfile/directives/root)** | Define o caminho da raiz do site
**[route](/docs/caddyfile/directives/route)** | Um grupo de diretivas tratado literalmente como uma única unidade
**[templates](/docs/caddyfile/directives/templates)** | Executa templates na resposta
**[tls](/docs/caddyfile/directives/tls)** | Personaliza as configurações de TLS
**[tracing](/docs/caddyfile/directives/tracing)** | Integração com tracing do OpenTelemetry
**[try_files](/docs/caddyfile/directives/try_files)** | Reescrita que depende da existência do arquivo
**[uri](/docs/caddyfile/directives/uri)** | Manipula a URI
**[vars](/docs/caddyfile/directives/vars)** | Define variáveis arbitrárias

</div>

<a id="syntax"></a>
## Sintaxe

A sintaxe de cada diretiva será algo parecido com isto:

```caddy-d
directive [<matcher>] <args...> {
	subdirective [<args...>]
}
```

Os `<carets>` indicam tokens que serão substituídos por valores reais.

Os `[colchetes]` indicam parâmetros opcionais.

As reticências `...` indicam continuação, isto é, um ou mais parâmetros ou linhas.

Subdiretivas normalmente são opcionais, a menos que a documentação diga o contrário, mesmo que não apareçam entre `[colchetes]`.


### Matchers

A maioria das diretivas, mas não todas, aceita [tokens de matcher](/docs/caddyfile/matchers#syntax), que permitem filtrar requisições. Tokens de matcher geralmente são opcionais. As diretivas suportam matchers se você vir isto na sintaxe da diretiva:

```caddy-d
[<matcher>]
```

Como todos os tokens de matcher funcionam da mesma forma, as várias possibilidades para o token de matcher não serão descritas em cada página, para evitar repetição. Em vez disso, consulte a [documentação de matchers](/docs/caddyfile/matchers) para uma explicação detalhada da sintaxe.


<a id="directive-order"></a>
## Ordem das diretivas

Muitas diretivas manipulam a cadeia de handlers HTTP. A ordem em que essas diretivas são avaliadas importa, então uma ordem padrão é embutida no Caddy.

Você pode substituir/personalizar essa ordem usando a [opção global `order`](/docs/caddyfile/options#order) ou a [`diretiva route`](/docs/caddyfile/directives/route).

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # apenas no bloco handle_response de reverse_proxy
request_body

redir

# manipulação da requisição de entrada
method
rewrite
uri
try_files

# handlers de middleware; alguns encapsulam respostas
basic_auth
forward_auth
request_header
encode
push
intercept
templates

# diretivas especiais de roteamento e despacho
invoke
handle
handle_path
route

# handlers que normalmente respondem às requisições
abort
error
copy_response # apenas no bloco handle_response de reverse_proxy
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



<a id="sorting-algorithm"></a>
## Algoritmo de ordenação

Para facilitar o uso, o adaptador do Caddyfile ordena as diretivas de acordo com as seguintes regras:

- Diretivas com nomes diferentes são ordenadas conforme a posição delas na [ordem padrão](#directive-order). A ordem padrão pode ser substituída com a [opção global `order`](/docs/caddyfile/options). Diretivas de plugins _não_ têm uma ordem, então a [opção global `order`](/docs/caddyfile/options) ou a [`diretiva route`](/docs/caddyfile/directives/route) deve ser usada para definir uma.

- Diretivas com o mesmo nome são ordenadas de acordo com seus [matchers](/docs/caddyfile/matchers#syntax).

  - A maior prioridade é uma diretiva com um único [matcher de caminho](/docs/caddyfile/matchers#path-matchers).

    Matchers de caminho são ordenados por especificidade, do mais específico ao menos específico.
	
    Em geral, isso é feito ordenando pelo comprimento do matcher de caminho. Há uma exceção: se o caminho termina em `*` e os caminhos dos dois matchers forem, de resto, iguais, o matcher sem `*` é considerado mais específico e fica acima.

    Por exemplo:
    - `/foobar` é mais específico que `/foo`
    - `/foo` é mais específico que `/foo*`
    - `/foo/*` é mais específico que `/foo*`

  - Uma diretiva com qualquer outro matcher é ordenada em seguida, na ordem em que aparece no Caddyfile.

    Isso inclui matchers de caminho com vários valores e [matchers nomeados](/docs/caddyfile/matchers#named-matchers).

  - Uma diretiva sem matcher (isto é, que corresponde a todas as requisições) é ordenada por último.

- A diretiva [`vars`](/docs/caddyfile/directives/vars) tem sua ordenação por matcher invertida, porque ela envolve definir valores que podem sobrescrever uns aos outros; portanto, o matcher mais específico deve ser avaliado por último.

- O conteúdo da [`diretiva route`](/docs/caddyfile/directives/route) ignora todas as regras acima e preserva a ordem em que as diretivas aparecem.
