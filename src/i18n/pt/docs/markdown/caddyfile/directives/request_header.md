---
title: request_header (diretiva do Caddyfile)
---

# request_header

Manipula campos de cabeçalho HTTP na requisição. Pode definir, adicionar e apagar valores de cabeçalho, ou fazer substituições usando expressões regulares.

Se sua intenção for manipular cabeçalhos para proxy, use em vez disso a [`subdiretiva header_up`](/docs/caddyfile/directives/reverse_proxy#header_up) de `reverse_proxy`, já que essas manipulações são cientes de proxy.

Para manipular cabeçalhos de resposta HTTP, você pode usar a diretiva [`header`](header).


## Sintaxe

```caddy-d
request_header [<matcher>] [[+|-]<field> [<value>|<find>] [<replace>]]
```

- **&lt;field&gt;** é o nome do campo de cabeçalho.

  Sem prefixo, o campo é definido (sobrescrito).

  Com o prefixo `+`, o campo é adicionado em vez de sobrescrito (definido) se ele já existir; campos de cabeçalho podem aparecer mais de uma vez em uma requisição.

  Com o prefixo `-`, o campo é apagado. O campo pode usar curingas `*` de prefixo ou sufixo para apagar todos os campos correspondentes.

- **&lt;value&gt;** é o valor do campo de cabeçalho, se estiver adicionando ou definindo um campo.

- **&lt;find&gt;** é a substring ou expressão regular a ser pesquisada.

- **&lt;replace&gt;** é o valor de substituição; obrigatório se estiver fazendo busca e substituição.


## Exemplos

Remover o cabeçalho Referer da requisição:

```caddy-d
request_header -Referer
```

Apagar todos os cabeçalhos que contenham um underscore da requisição:

```caddy-d
request_header -*_*
```
