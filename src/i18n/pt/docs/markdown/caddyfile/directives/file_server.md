---
title: file_server (Caddyfile directive)
---

<script>
ready(function() {
	// Corrige o argumento inline browse
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// Vamos adicionar links a todas as subdiretivas se houver uma tag de âncora correspondente na página.
	addLinksToSubdirectives();
});
</script>

# file_server

Um servidor de arquivos estáticos que suporta sistemas de arquivos reais e virtuais. Ele forma os caminhos dos arquivos anexando o caminho URI da requisição ao [caminho raiz do site](root).

Por padrão, ele impõe URIs canônicas; isto é, redirecionamentos HTTP serão emitidos para requisições de diretórios que não terminam com uma barra final (para adicioná-la), ou para requisições de arquivos que terminam com uma barra (para removê-la). Porém, redirecionamentos não são emitidos se uma reescrita interna modificar o último elemento do caminho (o nome do arquivo).

Na maioria das vezes, a diretiva `file_server` é combinada com a diretiva [`root`](root) para definir a raiz de arquivos de todo o site. Esta diretiva também tem uma subdiretiva `root` (veja abaixo) para definir a raiz apenas para este handler (não recomendado). Observe que a raiz do site não oferece garantias de sandbox: o servidor de arquivos impede a travessia de diretórios a partir dos componentes do caminho, mas links simbólicos dentro da raiz ainda podem permitir acessos fora dela.

Quando ocorrem erros (por exemplo, arquivo não encontrado `404`, permissão negada `403`), as rotas de erro serão acionadas. Use a diretiva [`handle_errors`](handle_errors) para definir rotas de erro e exibir páginas de erro personalizadas.

Ao usar `browse`, a saída padrão é produzida pelo modelo HTML. Os clientes podem solicitar a listagem de diretório em JSON ou texto puro usando, respectivamente, os cabeçalhos `Accept: application/json` ou `Accept: text/plain`. A saída em JSON pode ser útil para automação, e a saída em texto puro pode ser útil para uso humano no terminal.


<a id="syntax"></a>
## Sintaxe

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <path>
	hide          <files...>
	index         <filenames...>
	browse        [<template_file>] {
		reveal_symlinks
		sort <sort_field> [<direction>]
		file_limit <number>
	}
	precompressed [<formats...>]
	status        <status>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> especifica um sistema de arquivos alternativo (talvez virtual) a ser usado. Qualquer módulo Caddy no namespace `caddy.fs` pode ser usado aqui. Qualquer raiz/prefixo ainda se aplica aos módulos alternativos do sistema de arquivos. Por padrão, é usado o disco local.

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 introduz a flag [`--embed`](https://github.com/caddyserver/xcaddy#custom-builds) para incorporar uma árvore de arquivos na compilação personalizada do Caddy, e registra um módulo `fs` chamado `embedded`, que permite distribuir seu site estático como um executável do Caddy.

- **root** <span id="root"/> define o caminho da raiz do site. É parecido com a diretiva [`root`](root), exceto que se aplica apenas a esta instância do servidor de arquivos e substitui qualquer outra raiz de site que possa ter sido definida. Padrão: `{http.vars.root}` ou o diretório de trabalho atual. Observação: esta subdiretiva só altera a raiz para este handler. Para que outras diretivas (como [`try_files`](try_files) ou [`templates`](templates)) conheçam a mesma raiz do site, use a diretiva [`root`](root) em vez disso.

- **hide** <span id="hide"/> é uma lista de arquivos ou pastas a ocultar; se forem solicitados, o servidor de arquivos fingirá que eles não existem. Aceita placeholders e padrões glob. Observe que estes são caminhos do _sistema de arquivos_, e NÃO caminhos de requisição. Em outras palavras, caminhos relativos usam o diretório de trabalho atual como base, e NÃO a raiz do site; e todos os caminhos são convertidos para a forma absoluta antes das comparações (se possível). Especificar um nome de arquivo ou padrão sem separador de caminho ocultará todos os arquivos com nome correspondente, independentemente da localização; caso contrário, primeiro será tentada uma correspondência por prefixo de caminho e depois uma correspondência globular. Como esta é uma configuração de Caddyfile, os arquivos de configuração ativos serão adicionados por padrão. As comparações de `hide` diferenciam maiúsculas de minúsculas; em sistemas de arquivos sem distinção de maiúsculas, um caminho solicitado com outra capitalização ainda pode resolver para o mesmo caminho em disco, então `hide` não deve ser tratado como uma fronteira de segurança para caminhos sensíveis.

- **index** <span id="index"/> é uma lista de nomes de arquivo a procurar como arquivos de índice. Padrão: `index.html index.txt`

- **browse** <span id="browse"/> habilita listagens de arquivos para requisições a diretórios que não têm um arquivo de índice.

  - **<template_file>** <span id="template_file"/> é um arquivo de modelo personalizado opcional para usar nas listagens de diretório. O padrão é o modelo que pode ser extraído com o comando `caddy file-server export-template`, que imprimirá o modelo padrão no stdout. O modelo embutido também pode ser encontrado [aqui no código-fonte ![external link](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html). Modelos de browse também podem usar ações do [módulo templates padrão](/docs/modules/http.handlers.templates#docs).

  - **reveal_symlinks** <span id="reveal_symlinks"/> habilita revelar os destinos de links simbólicos nas listagens de diretório. Por padrão, os destinos dos links simbólicos ficam ocultos, e apenas o próprio arquivo de link é mostrado.

  - **sort** <span id="sort"/> altera a ordenação padrão das listagens de diretório. O primeiro parâmetro é o campo/coluna por qual ordenar: `name`, `namedirfirst`, `size` ou `time`. O segundo argumento é uma direção opcional: `asc` ou `desc`. Por exemplo, `sort name desc` ordenará por nome em ordem decrescente.

  - **file_limit** <span id="file_limit"/> define o número máximo de arquivos a mostrar nas listagens de diretório. Padrão: `10000`. Se o número de arquivos exceder esse limite, apenas os primeiros N arquivos serão mostrados, onde N é o limite especificado.

- **precompressed** <span id="precompressed"/> é a lista de formatos de codificação a procurar em arquivos lado a lado pré-comprimidos. Os argumentos são uma lista ordenada de formatos de codificação para procurar [sidecar files](https://en.wikipedia.org/wiki/Sidecar_file) pré-comprimidos. Os formatos suportados são `gzip` (`.gz`), `zstd` (`.zst`) e `br` (`.br`). Se os formatos forem omitidos, o padrão será `br zstd gzip` (nessa ordem).

  Todas as buscas de arquivo verificarão primeiro a existência do arquivo não comprimido. Uma vez encontrado, o Caddy procurará arquivos lado a lado com a extensão de cada formato habilitado. Se um arquivo lado a lado pré-comprimido for encontrado, o Caddy responderá com o arquivo pré-comprimido, com o cabeçalho de resposta `Content-Encoding` definido apropriadamente. Caso contrário, o Caddy responderá normalmente com o arquivo não comprimido. Se a diretiva [`encode`](encode) estiver habilitada, ela poderá compactar a resposta em tempo real se ela não estiver pré-comprimida.

- **status** <span id="status"/> é um código de status opcional a ser usado ao escrever a resposta. Especialmente útil ao responder a uma requisição com uma [página de erro personalizada](handle_errors). Pode ser um código de status de 3 dígitos, por exemplo: `404`. Placeholders são suportados. Por padrão, o código de status escrito normalmente será `200`, ou `206` para conteúdo parcial.

- **disable_canonical_uris** <span id="disable_canonical_uris"/> desabilita o comportamento padrão de redirecionar (para adicionar uma barra final se o caminho da requisição for um diretório, ou remover a barra final se o caminho da requisição for um arquivo). Observe que, por padrão, a canonização não ocorrerá se o último elemento do caminho da requisição (o nome do arquivo) tiver passado por uma reescrita interna, para evitar sobrescrever uma reescrita explícita com comportamento implícito.

- **pass_thru** <span id="pass_thru"/> habilita o modo pass-through, que continua para o próximo handler HTTP na rota se o arquivo solicitado não for encontrado, em vez de disparar um erro `404` (invocando rotas de [`handle_errors`](handle_errors)). Na prática, isso só é útil dentro de um bloco [`route`](route) com outras diretivas de handler após `file_server`, porque esta diretiva é efetivamente [ordenada por último](/docs/caddyfile/directives#directive-order).


<a id="examples"></a>
## Exemplos

Um servidor de arquivos estáticos a partir do diretório atual:

```caddy-d
file_server
```

Com listagens de arquivos habilitadas:

```caddy-d
file_server browse
```

Servir apenas arquivos estáticos dentro da pasta `/static`:

```caddy-d
file_server /static/*
```

A diretiva `file_server` normalmente é combinada com a [diretiva `root`](root) para definir o caminho raiz a partir do qual servir os arquivos:

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

Se você estiver executando o Caddy como serviço systemd, ler arquivos de `/home` não funcionará, porque o usuário `caddy` não tem permissão de "execução" no diretório `/home` (necessária para atravessá-lo). É recomendável colocar seus arquivos em `/srv` ou `/var/www/html` em vez disso.

</aside>


Ocultar todas as pastas `.git` e seus conteúdos:

```caddy-d
file_server {
	hide .git
}
```

Se for suportado pelo cliente (cabeçalho `Accept-Encoding`), verifica a existência de arquivos pré-comprimidos ao lado do arquivo solicitado. Assim, se `/path/to/file` for solicitado, ele verifica `/path/to/file.br`, `/path/to/file.zst` e `/path/to/file.gz` nessa ordem e serve o primeiro arquivo disponível com o `Content-Encoding` correspondente:

```caddy-d
file_server {
	precompressed
}
```
