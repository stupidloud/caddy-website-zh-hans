---
title: rewrite (diretiva do Caddyfile)
---

# rewrite

Reescreve internamente a URI da requisição.

Um rewrite altera parte ou toda a URI da requisição. Observe que a URI não inclui esquema nem autoridade (host e porta), e os clientes normalmente não enviam fragmentos. Portanto, esta diretiva é usada principalmente para manipulação de **path** e string de **query**.

A diretiva `rewrite` implica a intenção de aceitar a requisição, mas com modificações.

Ela é mutuamente exclusiva com outras diretivas `rewrite` no mesmo bloco, então é seguro definir rewrites que, de outra forma, cascariam uns nos outros, porque apenas o primeiro rewrite correspondente será executado.

Um [matcher de requisição](/docs/caddyfile/matchers) que corresponda a uma requisição antes do `rewrite` pode não corresponder à mesma requisição depois do `rewrite`. Se você quiser que seu `rewrite` compartilhe uma rota com outros handlers, use as diretivas [`route`](route) ou [`handle`](handle).


## Sintaxe

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** é a URI para a qual a requisição será reescrita. Apenas os componentes da URI (path ou query string) especificados no rewrite serão operados. O caminho da URI é qualquer substring antes de `?`. Se `?` for omitido, então todo o token é considerado o path.

Antes da v2.8.0, o argumento `<to>` podia ser confundido pelo parser com um [token de matcher](/docs/caddyfile/matchers#syntax) se começasse com `/`, então era necessário especificar um token de matcher curinga (`*`).


## Diretivas semelhantes

Há outras diretivas que realizam rewrites, mas implicam uma intenção diferente ou fazem o rewrite sem substituir a URI por completo:

- [`uri`](uri) manipula uma URI (remove prefixo, sufixo ou faz substituição de substring).

- [`try_files`](try_files) reescreve a requisição com base na existência de arquivos.



## Exemplos

Reescreve todas as requisições para `index.html`, deixando qualquer query string inalterada:

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

Observe que, antes da v2.8.0, um [matcher curinga](/docs/caddyfile/matchers#wildcard-matchers) era necessário aqui porque o primeiro argumento é ambíguo com um [matcher de caminho](/docs/caddyfile/matchers#path-matchers), ou seja, `rewrite * /foo`, mas agora pode ser simplificado para `rewrite /foo`.

</aside>

Prefixar todas as requisições com `/api`, preservando o restante da URI, e depois fazer reverse proxy para um app:

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

Substituir a query string em requisições da API por `a=b`, deixando o path inalterado:

```caddy
example.com {
	rewrite ?a=b
}
```

Somente para requisições em `/api/`, preservar a query string existente e adicionar um par chave-valor:

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

Alterar tanto o path quanto a query string, preservando a query original enquanto adiciona o path original como o parâmetro `p`:

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
```
