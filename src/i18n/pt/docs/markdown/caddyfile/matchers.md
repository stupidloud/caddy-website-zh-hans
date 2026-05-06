---
title: Matchers de requisição (Caddyfile)
---

<script>
ready(function() {
	// Vamos adicionar links nos matchers nos blocos de código
	// para seus respectivos anchors.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Vincula tokens de matcher com base no conteúdo deles à seção de sintaxe
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Token de matcher">${text}</a>`;
	});
});
</script>

<a id="request-matchers"></a>
# Matchers de requisição

**Matchers de requisição** podem ser usados para filtrar (ou classificar) requisições por vários critérios.

- [Sintaxe](#syntax)
	- [Exemplos](#examples)
	- [Matchers curinga](#wildcard-matchers)
	- [Matchers de caminho](#path-matchers)
	- [Matchers nomeados](#named-matchers)
- [Matchers padrão](#standard-matchers)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)


<a id="syntax"></a>
## Sintaxe

No Caddyfile, um **token de matcher** imediatamente depois da diretiva pode limitar o escopo dessa diretiva. O token de matcher pode ter uma destas formas:

1. [**`*`**](#wildcard-matchers) para corresponder a todas as requisições (curinga; padrão).
2. [**`/path`**](#path-matchers) começa com uma barra `/` para corresponder a um caminho de requisição.
3. [**`@name`**](#named-matchers) para especificar um _matcher nomeado_.

Se uma diretiva suportar matchers, isso aparecerá como `[<matcher>]` na documentação da sintaxe. Tokens de matcher são [geralmente opcionais](/docs/caddyfile/directives#syntax), indicados por `[ ]`. Se o token de matcher for omitido, é o mesmo que um matcher curinga (`*`).


<a id="examples"></a>
#### Exemplos

Esta diretiva se aplica a requisições HTTP de [todas](#wildcard-matchers):

```caddy-d
reverse_proxy localhost:9000
```

E isto é o mesmo (`*` é desnecessário aqui):

```caddy-d
reverse_proxy * localhost:9000
```

Mas esta diretiva se aplica apenas a requisições que têm um [caminho](#path-matchers) começando com `/api/`:

```caddy-d
reverse_proxy /api/* localhost:9000
```

Para corresponder a qualquer coisa que não seja um caminho, defina um [matcher nomeado](#named-matchers) e referencie-o usando `@name`:

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```




<a id="wildcard-matchers"></a>
### Matchers curinga

O matcher curinga, ou "catch-all", `*` corresponde a todas as requisições e só é necessário se um token de matcher for exigido. Por exemplo, se o primeiro argumento que você quiser passar para uma diretiva também for um caminho, ele pareceria exatamente um matcher de caminho! Então você pode usar um matcher curinga para desambiguar, por exemplo:

```caddy-d
root * /home/www/mysite
```

Caso contrário, esse matcher não é usado com tanta frequência. Em geral, recomendamos omití-lo se a sintaxe não exigir.


<a id="path-matchers"></a>
### Matchers de caminho

Corresponder pelo caminho da URI é a forma mais comum de corresponder requisições, então o matcher pode ser inline, assim:

```caddy-d
redir /old.html /new.html
```

Tokens de matcher de caminho devem começar com uma barra `/`.

**[A correspondência de caminho](#path) é, por padrão, uma correspondência exata, não uma correspondência de prefixo.** Você deve adicionar um `*` para fazer uma correspondência rápida de prefixo. Observe que `/foo*` vai corresponder a `/foo` e `/foo/`, assim como a `/foobar`; talvez você queira usar `/foo/*` em vez disso.


<a id="named-matchers"></a>
### Matchers nomeados

Todos os matchers que não são de caminho nem curinga devem ser matchers nomeados. Este é um matcher definido fora de uma diretiva específica e que pode ser reutilizado.

Definir um matcher com um nome único lhe dá mais flexibilidade, permitindo combinar [qualquer matcher disponível](#standard-matchers) em um conjunto:

```caddy-d
@name {
	...
}
```

ou, se houver apenas um matcher no conjunto, você pode colocá-lo na mesma linha:

```caddy-d
@name ...
```

Depois, você pode usar o matcher assim, especificando-o como o primeiro argumento de uma diretiva:

```caddy-d
directive @name
```

Por exemplo, isto encaminha requisições websocket HTTP/1.1 para `localhost:6001`, e outras requisições para `localhost:8080`. Ele corresponde a requisições que têm um cabeçalho `Connection` _contendo_ `Upgrade`, **e** outro cabeçalho `Upgrade` com o valor exato `websocket`:

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

Se o conjunto de matchers contiver apenas um matcher, a sintaxe em uma única linha também funciona:

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

Como caso especial, o matcher [`expression`](#expression) pode ser usado sem especificar o nome, desde que um argumento [entre aspas](/docs/caddyfile/concepts#tokens-and-quotes) (a própria expressão CEL) venha depois do nome do matcher:

```caddy-d
@not-found `{err.status_code} == 404`
```

Assim como as diretivas, as definições de matchers nomeados devem ficar dentro dos [blocos de site](/docs/caddyfile/concepts#structure) que os usam.

Uma definição de matcher nomeado constitui um _conjunto de matchers_. Matchers em um conjunto são combinados com AND; isto é, todos devem corresponder. Por exemplo, se você tiver um matcher [`header`](#header) e um matcher [`path`](#path) no conjunto, ambos precisam corresponder.

Vários matchers do mesmo tipo podem ser combinados (por exemplo, vários matchers [`path`](#path) no mesmo conjunto) usando álgebra booleana (AND/OR), como descrito nas respectivas seções abaixo.

Para lógicas booleanas mais complexas, é recomendado usar o matcher [`expression`](#expression) para escrever uma expressão CEL, que suporta **and** `&&`, **or** `||` e **parênteses** `( )`.




<a id="standard-matchers"></a>
## Matchers padrão

A documentação completa dos matchers pode ser encontrada [na documentação de cada módulo de matcher respectivo](/docs/json/apps/http/servers/routes/match/).

As requisições podem ser correspondidas das seguintes formas:



<a id="client-ip"></a>
### client_ip

```caddy-d
client_ip <ranges...>

expression client_ip('<ranges...>')
```

Pelo endereço IP do cliente. Aceita IPs exatos ou intervalos CIDR. Zonas IPv6 são suportadas.

Esse matcher é melhor usado quando a opção global [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) está configurada; caso contrário, ele se comporta exatamente como o matcher [`remote_ip`](#remote-ip). Somente requisições vindas de proxies confiáveis terão seu IP do cliente analisado no início da requisição; requisições não confiáveis usarão o IP remoto do peer imediato ou o endereço definido via [PROXY protocol](/docs/caddyfile/options#proxy-protocol).

Como atalho, `private_ranges` pode ser usado para corresponder a todos os intervalos privados IPv4 e IPv6. É o mesmo que especificar todos estes intervalos: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Pode haver vários matchers `client_ip` por matcher nomeado, e seus intervalos serão combinados e unidos com OR.

#### Exemplo:

Corresponde a requisições vindas de endereços IPv4 privados:

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Esse matcher é comumente combinado com o matcher [`not`](#not) para inverter a correspondência. Por exemplo, para abortar todas as conexões vindas de endereços IPv4 e IPv6 _públicos_ (que é o inverso de todos os intervalos privados):

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "Olá, você precisa vir de uma rede privada!"
}
```

Em uma [expressão CEL](#expression), ficaria assim:

```caddy-d
@my-friends `client_ip('12.23.34.45', '23.34.45.56')`
```



<a id="expression"></a>
### expression

```caddy-d
expression <cel...>
```

Por qualquer expressão [CEL (Common Expression Language)](https://github.com/google/cel-spec) que retorne `true` ou `false`.

A maioria dos outros matchers de requisição também pode ser usada em expressões como funções, o que dá mais flexibilidade para lógica booleana do que fora de expressões. Veja a documentação de cada matcher para a sintaxe suportada dentro de expressões CEL.

Os [placeholders](/docs/conventions#placeholders) do Caddy (ou os [atalhos do Caddyfile](/docs/caddyfile/concepts#placeholders)) podem ser usados nessas expressões CEL, porque eles são pré-processados e convertidos em chamadas normais de função CEL antes de serem interpretados pelo ambiente CEL. Se um placeholder precisar ser passado como argumento de string para uma função matcher, então a chave inicial `{` deve ser escapada com uma barra invertida `\` para que ela não seja pré-processada, por exemplo `file('\{path}.md')`.

Por conveniência, o nome do matcher pode ser omitido se você estiver definindo um matcher nomeado que consista apenas em uma expressão CEL. A expressão CEL deve estar [entre aspas](/docs/caddyfile/concepts#tokens-and-quotes) (recomendam-se crases ou heredocs). Isso fica bem legível:

```caddy-d
@mutable `{method}.startsWith("P")`
```

Nesse caso, assume-se o matcher CEL.

#### Exemplos:

Corresponde a requisições cujos métodos começam com `P`, por exemplo `PUT` ou `POST`:

```caddy-d
@methods expression {method}.startsWith("P")
```

Corresponde a requisições em que o handler retornou o código de erro `404`, o que seria usado em conjunto com a [`diretiva handle_errors`](/docs/caddyfile/directives/handle_errors):

```caddy-d
@404 expression {err.status_code} == 404
```

Corresponde a requisições em que o caminho corresponde a uma de duas expressões regulares diferentes; isso só é possível escrever usando uma expressão, porque o matcher [`path_regexp`](#path-regexp) normalmente só pode existir uma vez por matcher nomeado:

```caddy-d
@user expression path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')
```

Ou o mesmo, omitindo o nome do matcher e envolvendo em [crases](/docs/caddyfile/concepts#tokens-and-quotes) para que seja interpretado como um único token:

```caddy-d
@user `path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')`
```

Você pode usar a sintaxe de [heredoc](/docs/caddyfile/concepts#heredocs) para escrever expressões CEL multilinha:

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Olá, API!"
```


---
<a id="file"></a>
### file

```caddy-d
file {
	root       <path>
	try_files  <files...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delims...>
}
file <files...>

expression `file({
	'root': '<path>',
	'try_files': ['<files...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delims...>']
})`
expression file('<files...>')
```

Por arquivos.

- `root` define o diretório no qual os arquivos serão procurados. O padrão é o diretório de trabalho atual, ou a [variável](/docs/modules/http.handlers.vars) `root` (`{http.vars.root}`) se ela estiver definida (o que pode ser feito pela [`diretiva root`](/docs/caddyfile/directives/root)).

- `try_files` verifica os arquivos da lista que correspondem ao try_policy.

  Para corresponder a diretórios, adicione uma barra `/` ao final do caminho. Todos os caminhos de arquivo são relativos à [raiz](/docs/caddyfile/directives/root) do site, e [padrões glob](https://pkg.go.dev/path/filepath#Match) serão expandidos.

  Se `try_policy` for `first_exist` (o padrão), então o último item da lista pode ser um número prefixado por `=` (por exemplo `=404`), que, como fallback, emitirá um erro com esse código; o erro pode ser capturado e tratado com [`handle_errors`](/docs/caddyfile/directives/handle_errors).



- `try_policy` especifica como escolher um arquivo. O padrão é `first_exist`.

	- `first_exist` verifica a existência do arquivo. O primeiro arquivo que existir é selecionado.

	- `first_exist_fallback` é semelhante a `first_exist`, mas assume que o último elemento da lista sempre existe para evitar acesso ao disco.

	- `smallest_size` escolhe o arquivo com o menor tamanho.

	- `largest_size` escolhe o arquivo com o maior tamanho.

	- `most_recently_modified` escolhe o arquivo modificado mais recentemente.

- `split_path` faz o caminho ser dividido no primeiro delimitador da lista encontrado em cada filepath a ser testado. Para cada valor de divisão, a parte esquerda da divisão, incluindo o próprio delimitador, será o filepath testado. Por exemplo, `/remote.php/dav/` usando um delimitador `.php` tentaria o arquivo `/remote.php`. Cada delimitador deve aparecer no fim de um componente do caminho da URI para poder ser usado como delimitador de divisão. Esse é um ajuste de nicho e é usado principalmente ao servir sites PHP.

Como `try_files` com a política `first_exist` é tão comum, existe um atalho de uma linha para isso:

```caddy-d
file <files...>
```

Um matcher `file` vazio (sem arquivos listados depois dele) verificará se o arquivo solicitado - exatamente como vem da URI, relativo à [raiz do site](/docs/caddyfile/directives/root) - existe. Isso é, na prática, o mesmo que `file {path}`.


<aside class="tip">

Como reescrever com base na existência de um arquivo em disco é tão comum, também existe uma [`diretiva try_files`](/docs/caddyfile/directives/try_files), que é um atalho para o matcher `file` e um [handler `rewrite`](/docs/caddyfile/directives/rewrite).

</aside>


Ao corresponder, quatro novos placeholders ficarão disponíveis:

- `{file_match.relative}` O caminho relativo à raiz do arquivo. Isso costuma ser útil ao reescrever requisições.
- `{file_match.absolute}` O caminho absoluto do arquivo correspondente, incluindo a raiz.
- `{file_match.type}` O tipo de arquivo, `file` ou `directory`.
- `{file_match.remainder}` A parte restante após dividir o caminho do arquivo (se `split_path` estiver configurado)


#### Exemplos:

Corresponde a requisições em que o caminho é um arquivo existente:

```caddy-d
@file file
```

Corresponde a requisições em que o caminho seguido de `.html` é um arquivo existente, ou, se não for, em que o caminho em si é um arquivo existente:

```caddy-d
@html file {
	try_files {path}.html {path} 
}
```

O mesmo de cima, mas usando o atalho de uma linha e caindo para emitir um erro 404 se o arquivo não for encontrado:

```caddy-d
@html-or-error file {path}.html {path} =404
```

Mais alguns exemplos usando [expressões CEL](#expression). Tenha em mente que os placeholders são pré-processados e convertidos em chamadas normais de função CEL antes de serem interpretados pelo ambiente CEL, então a concatenação é usada aqui. Além disso, o formato longo precisa ser usado ao concatenar com placeholders por causa das limitações atuais de parsing:

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---
<a id="header"></a>
### header

```caddy-d
header <field> [<value> ...]

expression header({'<field>': '<value>'})
```

Por campos de cabeçalho da requisição.

- `<field>` é o nome do campo de cabeçalho HTTP a verificar.
	- Se for prefixado com `!`, o campo não deve existir para corresponder (omita o argumento de valor).
- `<value>` é o valor que o campo deve ter para corresponder. Um ou mais podem ser especificados.
	- Se for prefixado com `*`, faz uma correspondência rápida de sufixo (aparece no final).
	- Se for suffixado com `*`, faz uma correspondência rápida de prefixo (aparece no início).
	- Se estiver entre `*`, faz uma correspondência rápida de substring (aparece em qualquer lugar).
	- Caso contrário, é uma correspondência exata rápida.

Campos diferentes dentro do mesmo conjunto são combinados com AND. Vários valores por campo são combinados com OR.

Observe que campos de cabeçalho podem ser repetidos e ter valores diferentes. Aplicações de backend DEVEM considerar que os valores dos campos de cabeçalho são arrays, não valores singulares, e o Caddy não interpreta nenhum significado especial nesses casos.

#### Exemplo:

Corresponde a requisições com o cabeçalho `Connection` contendo `Upgrade`:

```caddy-d
@upgrade header Connection *Upgrade*
```

Corresponde a requisições com o cabeçalho `Foo` contendo `bar` OU `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Corresponde a requisições que não têm o cabeçalho `Foo`:

```caddy-d
@not_foo header !Foo
```

Usando uma [expressão CEL](#expression), corresponda a requisições WebSocket verificando se o cabeçalho `Connection` contém `Upgrade` e o cabeçalho `Upgrade` é igual a `websocket` (HTTP/2 usa o cabeçalho `:protocol` para isso):

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---
<a id="header-regexp"></a>
### header_regexp

```caddy-d
header_regexp [<name>] <field> <regexp>

expression header_regexp('<name>', '<field>', '<regexp>')
expression header_regexp('<field>', '<regexp>')
```

Como [`header`](#header), mas com suporte a expressões regulares.

A linguagem de expressão regular usada é RE2, incluída no Go. Veja a [referência de sintaxe do RE2](https://github.com/google/re2/wiki/Syntax) e a [visão geral da sintaxe de regexp do Go](https://pkg.go.dev/regexp/syntax).

Desde v2.8.0, se `name` _não_ for fornecido, o nome será tirado do nome do matcher nomeado. Por exemplo, um matcher nomeado `@foo` fará com que este matcher receba o nome `foo`. A principal vantagem de especificar um nome é quando mais de um matcher de regexp (por exemplo `header_regexp` e [`path_regexp`](#path-regexp), ou vários campos de cabeçalho diferentes) é usado no mesmo matcher nomeado.

Grupos de captura podem ser acessados via [placeholder](/docs/caddyfile/concepts#placeholders) em diretivas depois da correspondência:
- `{re.<name>.<capture_group>}` onde:
  - `<name>` é o nome da expressão regular,
  - `<capture_group>` é o nome ou número do grupo de captura na expressão.

- `{re.<capture_group>}` sem nome também é preenchido por conveniência. A ressalva é que, se vários matchers de regexp forem usados em sequência, os valores do placeholder serão sobrescritos pelo matcher seguinte.

O grupo de captura `0` é a correspondência completa da regexp, `1` é o primeiro grupo de captura, `2` é o segundo, e assim por diante. Então `{re.foo.1}` ou `{re.1}` conterão o valor do primeiro grupo de captura.

Apenas uma expressão regular é suportada por campo de cabeçalho, já que padrões regexp não podem ser combinados; se você precisar de mais, considere usar um matcher [`expression`](#expression). Correspondências contra vários campos de cabeçalho diferentes serão combinadas com AND.

#### Exemplo:

Corresponde a requisições em que o cabeçalho Cookie contém `login_` seguido por uma string hex, com um grupo de captura que pode ser acessado via `{re.login.1}` ou `{re.1}`.

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

Isso pode ser simplificado omitindo o nome, que será inferido do matcher nomeado:

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

Ou o mesmo, usando uma [expressão CEL](#expression):

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```


---
<a id="host"></a>
### host

```caddy-d
host <hosts...>

expression host('<hosts...>')
```

Corresponde à requisição pelo campo de cabeçalho `Host`.

Como a maioria dos blocos de site já indica hosts no endereço do site, esse matcher é mais comumente usado em blocos de site que usam um hostname curinga (veja o [padrão de certificados curinga](/docs/caddyfile/patterns#wildcard-certificates)), mas em que há lógica específica por hostname.

Vários matchers `host` serão combinados com OR.

#### Exemplo:

Correspondendo a um subdomínio:

```caddy-d
@sub host sub.example.com
```

Correspondendo ao domínio apex e a um subdomínio:

```caddy-d
@site host example.com www.example.com
```

Vários subdomínios usando uma [expressão CEL](#expression):

```caddy-d
@app `host('app1.example.com', 'app2.example.com')`
```


---
<a id="method"></a>
### method

```caddy-d
method <verbs...>

expression method('<verbs...>')
```

Pelo método (verbo) da requisição HTTP. Os verbos devem estar em maiúsculas, como `POST`. Pode corresponder a um ou vários métodos.

Vários matchers `method` serão combinados com OR.

#### Exemplos:

Corresponde a requisições com o método `GET`:

```caddy-d
@get method GET
```

Corresponde a requisições com os métodos `PUT` ou `DELETE`:

```caddy-d
@put-delete method PUT DELETE
```

Corresponde a métodos apenas de leitura usando uma [expressão CEL](#expression):

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```


---
<a id="not"></a>
### not

```caddy-d
not <matcher>
```

ou, para negar vários matchers que são combinados com AND, abra um bloco:

```caddy-d
not {
	<matchers...>
}
```

Os resultados dos matchers contidos serão negados.

#### Exemplos:

Corresponde a requisições com caminhos que NÃO começam com `/css/` OU `/js/`.

```caddy-d
@not-assets {
	not path /css/* /js/*
}
```

Corresponde a requisições SEM NENHUM DOS DOIS:
- um prefixo de caminho `/api/`, NEM
- o método de requisição `POST`

isto é, não deve ter nenhum desses para corresponder:

```caddy-d
@with-neither {
	not path /api/*
	not method POST
}
```

Corresponde a requisições SEM AMBOS:
- um prefixo de caminho `/api/`, E
- o método de requisição `POST`

isto é, deve não ter nenhum ou apenas um deles para corresponder:

```caddy-d
@without-both {
	not {
		path /api/*
		method POST
	}
}
```

Não existe uma [expressão CEL](#expression) para esse matcher, porque você pode usar o operador `!` para negação em vez disso. Por exemplo:

```caddy-d
@without-both `!path('/api*') && !method('POST')`
```

Que é o mesmo que isto, usando parênteses:

```caddy-d
@without-both `!(path('/api*') || method('POST'))`
```




---
<a id="path"></a>
### path

```caddy-d
path <paths...>

expression path('<paths...>')
```

Pelo caminho da requisição (o componente de caminho da URI da requisição). As correspondências de caminho são exatas, mas não diferenciam maiúsculas de minúsculas. Wildcards `*` podem ser usados:

- No final apenas, para uma correspondência de prefixo (`/prefix/*`)
- No início apenas, para uma correspondência de sufixo (`*.suffix`)
- Dos dois lados apenas, para uma correspondência de substring (`*/contains/*`)
- No meio apenas, para uma correspondência em estilo glob (`/accounts/*/info`)

As barras importam. Por exemplo, `/foo*` vai corresponder a `/foo`, `/foobar`, `/foo/` e `/foo/bar`, mas `/foo/*` não vai corresponder a `/foo` nem a `/foobar`.

Os caminhos da requisição são limpos para resolver pontos de travessia de diretório antes da correspondência. Além disso, várias barras são mescladas, a menos que o padrão de correspondência tenha várias barras. Em outras palavras, `/foo` vai corresponder a `/foo` e `//foo`, mas `//foo` só vai corresponder a `//foo`.

Como há várias formas escapadas de uma dada URI, o caminho da requisição é normalizado (URL-decoded, unescaped), exceto para aquelas sequências de escape em posições em que as sequências de escape também estão presentes no padrão de correspondência. Por exemplo, `/foo/bar` corresponde tanto a `/foo/bar` quanto a `/foo%2Fbar`, mas `/foo%2Fbar` vai corresponder somente a `/foo%2Fbar`, porque a sequência de escape foi explicitamente fornecida na configuração.

A sequência especial `%*` também pode ser usada no lugar de `*` para manter o trecho correspondente escapado. Por exemplo, `/bands/*/*` não vai corresponder a `/bands/AC%2FDC/T.N.T` porque o caminho será comparado no espaço normalizado, em que ele parece `/bands/AC/DC/T.N.T`, o que não corresponde ao padrão; porém, `/bands/%*/*` vai corresponder a `/bands/AC%2FDC/T.N.T` porque o trecho representado por `%*` será comparado sem decodificar as sequências de escape.

Vários caminhos serão combinados com OR.

#### Exemplos:

Corresponde a vários diretórios e seus conteúdos:

```caddy-d
@assets path /js/* /css/* /images/*
```

Corresponde a um arquivo específico:

```caddy-d
@favicon path /favicon.ico
```

Corresponde a extensões de arquivo:

```caddy-d
@extensions path *.js *.css
```

Com uma [expressão CEL](#expression):

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```


---
<a id="path-regexp"></a>
### path_regexp

```caddy-d
path_regexp [<name>] <regexp>

expression path_regexp('<name>', '<regexp>')
expression path_regexp('<regexp>')
```

Como [`path`](#path), mas com suporte a expressões regulares. Executa sobre o caminho decodificado/desescapado da URI.

A linguagem de expressão regular usada é RE2, incluída no Go. Veja a [referência de sintaxe do RE2](https://github.com/google/re2/wiki/Syntax) e a [visão geral da sintaxe de regexp do Go](https://pkg.go.dev/regexp/syntax).

Desde v2.8.0, se `name` _não_ for fornecido, o nome será tirado do nome do matcher nomeado. Por exemplo, um matcher nomeado `@foo` fará com que este matcher receba o nome `foo`. A principal vantagem de especificar um nome é quando mais de um matcher de regexp (por exemplo `path_regexp` e [`header_regexp`](#header-regexp)) é usado no mesmo matcher nomeado.

Grupos de captura podem ser acessados via [placeholder](/docs/caddyfile/concepts#placeholders) em diretivas depois da correspondência:
- `{re.<name>.<capture_group>}` onde:
  - `<name>` é o nome da expressão regular,
  - `<capture_group>` é o nome ou número do grupo de captura na expressão.

- `{re.<capture_group>}` sem nome também é preenchido por conveniência. A ressalva é que, se vários matchers de regexp forem usados em sequência, os valores do placeholder serão sobrescritos pelo matcher seguinte.

O grupo de captura `0` é a correspondência completa da regexp, `1` é o primeiro grupo de captura, `2` é o segundo, e assim por diante. Então `{re.foo.1}` ou `{re.1}` conterão o valor do primeiro grupo de captura.

Só pode haver um padrão `path_regexp` por matcher nomeado, já que esse matcher não pode ser combinado consigo mesmo; se você precisar de mais, considere usar um matcher [`expression`](#expression).

#### Exemplo:

Corresponde a requisições em que o caminho termina com uma string hex de 6 caracteres seguida por `.css` ou `.js` como extensão do arquivo, com grupos de captura (partes entre `( )`), que podem ser acessados respectivamente por `{re.static.1}` e `{re.static.2}` (ou `{re.1}` e `{re.2}`):

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

Isso pode ser simplificado omitindo o nome, que será inferido do matcher nomeado:

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

Ou o mesmo, usando uma [expressão CEL](#expression), também validando que o [`file`](#file) existe no disco:

```caddy-d
@static `path_regexp('\.([a-f0-9]{6})\.(css|js)$') && file()`
```


---
<a id="protocol"></a>
### protocol

```caddy-d
protocol http|https|grpc|http/<version>[+]

expression protocol('http|https|grpc|http/<version>[+]')
```

Pelo protocolo da requisição. Pode ser usado um nome amplo de protocolo como `http`, `https` ou `grpc`; ou versões HTTP específicas ou mínimas como `http/1.1` ou `http/2+`.

Só pode haver um matcher `protocol` por matcher nomeado.

#### Exemplo:

Corresponde a requisições usando HTTP/2:

```caddy-d
@http2 protocol http/2+
```

Com uma [expressão CEL](#expression):

```caddy-d
@http2 `protocol('http/2+')`
```


---
<a id="query"></a>
### query

```caddy-d
query <key>=<val>...
query ""

expression query({'<key>': '<val>'})
expression query({'<key>': ['<vals...>']})
```

Por parâmetros da query string. Deve ser uma sequência de pares `key=value`, ou uma string vazia `""`. As chaves são correspondidas exatamente (com distinção de maiúsculas/minúsculas), mas também suportam `*` para corresponder a qualquer valor. Os valores podem usar placeholders. Uma string vazia corresponde a requisições HTTP sem parâmetros de query.

Pode haver vários matchers `query` por matcher nomeado, e pares com as mesmas chaves serão combinados com OR. Chaves diferentes serão combinadas com AND. Assim, todas as chaves no matcher precisam ter pelo menos um valor correspondente.

Strings de query inválidas (sintaxe ruim, ponto e vírgula sem escape, etc.) falharão no parsing e, portanto, não corresponderão.

**OBSERVAÇÃO:** Parâmetros da query string são arrays, não valores singulares. Isso acontece porque chaves repetidas são válidas em query strings, e cada uma pode ter um valor diferente. Esse matcher vai corresponder a uma chave se qualquer um dos valores configurados for atribuído na query string. Aplicações backend que usam query strings DEVEM levar em consideração que os valores da query string são arrays e podem ter vários valores.

#### Exemplo:

Corresponde a um parâmetro de query `q` com qualquer valor:

```caddy-d
@search query q=*
```

Corresponde a um parâmetro de query `sort` com o valor `asc` ou `desc`:

```caddy-d
@sorted query sort=asc sort=desc
```

Correspondendo a `q` e `sort`, com uma [expressão CEL](#expression):

```caddy-d
@search-sort `query({'sort': ['asc', 'desc'], 'q': '*'})`
```


---
<a id="remote-ip"></a>
### remote_ip

```caddy-d
remote_ip <ranges...>

expression remote_ip('<ranges...>')
```

Pelo endereço IP remoto (isto é, o IP do peer imediato ou o endereço definido via [PROXY protocol](/docs/caddyfile/options#proxy-protocol)). Aceita IPs exatos ou intervalos CIDR. Zonas IPv6 são suportadas.

Como atalho, `private_ranges` pode ser usado para corresponder a todos os intervalos privados IPv4 e IPv6. É o mesmo que especificar todos estes intervalos: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

se você quiser corresponder ao "IP real" do cliente, conforme analisado dos cabeçalhos HTTP, use o matcher [`client_ip`](#client-ip) em vez disso.

Pode haver vários matchers `remote_ip` por matcher nomeado, e seus intervalos serão combinados e unidos com OR.

#### Exemplo:

Corresponde a requisições vindas de endereços IPv4 privados:

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Esse matcher é comumente combinado com o matcher [`not`](#not) para inverter a correspondência. Por exemplo, para abortar todas as conexões vindas de endereços IPv4 e IPv6 _públicos_ (que é o inverso de todos os intervalos privados):

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "Olá, você precisa vir de uma rede privada!"
}
```

Em uma [expressão CEL](#expression), ficaria assim:

```caddy-d
@my-friends `remote_ip('12.23.34.45', '23.34.45.56')`
```


---
<a id="vars"></a>
### vars

```caddy-d
vars <variable> <values...>

expression vars({'<variable>': '<value>'})
expression vars({'<variable>': ['<values...>']})
```

Pelo valor de uma variável no contexto da requisição, ou pelo valor de um placeholder. Vários valores podem ser especificados para corresponder a qualquer um desses valores possíveis (com OR).

O argumento **&lt;variable&gt;** pode ser um nome de variável ou um placeholder entre chaves `{ }`. (Placeholders não são expandidos no primeiro parâmetro.)

Esse matcher é mais útil quando combinado com a [`diretiva map`](/docs/caddyfile/directives/map), que define saídas, com a [`diretiva vars`](/docs/caddyfile/directives/vars) dentro das suas rotas, ou com plugins que definem alguma informação no contexto da requisição.

#### Exemplo:

Corresponde a uma saída da [`diretiva map`](/docs/caddyfile/directives/map) chamada `magic_number` para os valores `3` ou `5`:

```caddy-d
vars {magic_number} 3 5
```

Corresponde ao valor de um placeholder arbitrário, por exemplo o ID do usuário autenticado, seja `Bob` ou `Alice`:

```caddy-d
vars {http.auth.user.id} Bob Alice
```

Um exemplo completo usando a [`diretiva vars`](/docs/caddyfile/directives/vars) para definir uma variável e depois correspondê-la com o matcher [`vars`](#vars). Aqui combinamos dois cabeçalhos de requisição em uma variável e correspondemos com base nela:

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "Você enviou Foo=123 e Bar=456!"
	}
	handle {
		respond "Foo e Bar não eram especiais."
	}
}
```

Em uma [expressão CEL](#expression), ficaria assim:

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---
<a id="vars-regexp"></a>
### vars_regexp

```caddy-d
vars_regexp [<name>] <variable> <regexp>

expression vars_regexp('<name>', '<variable>', '<regexp>')
expression vars_regexp('<variable>', '<regexp>')
```

Como [`vars`](#vars), mas com suporte a expressões regulares.

A linguagem de expressão regular usada é RE2, incluída no Go. Veja a [referência de sintaxe do RE2](https://github.com/google/re2/wiki/Syntax) e a [visão geral da sintaxe de regexp do Go](https://pkg.go.dev/regexp/syntax).

Desde v2.8.0, se `name` _não_ for fornecido, o nome será tirado do nome do matcher nomeado. Por exemplo, um matcher nomeado `@foo` fará com que este matcher receba o nome `foo`. A principal vantagem de especificar um nome é quando mais de um matcher de regexp (por exemplo `vars_regexp` e [`header_regexp`](#header-regexp)) é usado no mesmo matcher nomeado.

Grupos de captura podem ser acessados via [placeholder](/docs/caddyfile/concepts#placeholders) em diretivas depois da correspondência:
- `{re.<name>.<capture_group>}` onde:
  - `<name>` é o nome da expressão regular,
  - `<capture_group>` é o nome ou número do grupo de captura na expressão.

- `{re.<capture_group>}` sem nome também é preenchido por conveniência. A ressalva é que, se vários matchers de regexp forem usados em sequência, os valores do placeholder serão sobrescritos pelo matcher seguinte.

O grupo de captura `0` é a correspondência completa da regexp, `1` é o primeiro grupo de captura, `2` é o segundo, e assim por diante. Então `{re.foo.1}` ou `{re.1}` conterão o valor do primeiro grupo de captura.

Só pode haver uma expressão regular por nome de variável, já que padrões regexp não podem ser combinados; se você precisar de mais, considere usar um matcher [`expression`](#expression). Correspondências contra várias variáveis diferentes serão combinadas com AND.

#### Exemplo:

Corresponde a uma saída da [`diretiva map`](/docs/caddyfile/directives/map) chamada `magic_number` para um valor que começa com `4`, capturando o valor em um grupo de captura que pode ser acessado via `{re.magic.1}` ou `{re.1}`:

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

Isso pode ser simplificado omitindo o nome, que será inferido do matcher nomeado:

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

Em uma [expressão CEL](#expression), ficaria assim:

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
```
