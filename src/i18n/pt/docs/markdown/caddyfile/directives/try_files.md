---
title: try_files (Caddyfile directive)
---

# try_files

Reescreve o caminho do URI da requisição para o primeiro dos arquivos listados que existir na raiz do site. Se nenhum arquivo corresponder, nenhuma reescrita é feita.


<a id="syntax"></a>
## Sintaxe

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **<files...>** é a lista de arquivos a tentar. O caminho do URI será reescrito para o primeiro que existir.

  Para corresponder a diretórios, acrescente uma barra `/` no final do caminho. Todos os caminhos de arquivo são relativos à [root](root) do site, e [padrões glob](https://pkg.go.dev/path/filepath#Match) serão expandidos.

  Cada argumento também pode conter uma query string; nesse caso, a query string também será alterada se corresponder àquele arquivo específico.

  Se `try_policy` for `first_exist` (o padrão), o último item da lista pode ser um número prefixado por `=` (por exemplo, `=404`), que servirá como fallback para emitir um erro com esse código; o erro pode ser capturado e tratado com [`handle_errors`](handle_errors).

- **policy** é a política para escolher o arquivo entre a lista de arquivos.

  Padrão: `first_exist`


<a id="expanded-form"></a>
## Forma expandida

A diretiva `try_files` é basicamente um atalho para:

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

Observe que esta diretiva não aceita um token de matcher. Se você precisar de uma lógica de correspondência mais complexa, use a forma expandida acima como base.

Veja o [matcher `file`](/docs/caddyfile/matchers#file) para mais detalhes.


<a id="examples"></a>
## Exemplos

Se a requisição não corresponder a nenhum arquivo estático, reescreva para o ponto de entrada de um índice/roteador PHP:

```caddy-d
try_files {path} /index.php
```

O mesmo, mas adicionando o caminho original à query string (necessário para alguns aplicativos PHP legados):

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

O mesmo, mas também correspondendo a diretórios:

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

Tente reescrever para um arquivo ou diretório, se ele existir, caso contrário emita um erro 404 (que pode ser capturado e tratado com [`handle_errors`](handle_errors)):

```caddy-d
try_files {path} {path}/ =404
```

Escolha a versão implantada mais recentemente de um arquivo estático (por exemplo, sirva `index.be331df.html` quando `index.html` for solicitado):

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
