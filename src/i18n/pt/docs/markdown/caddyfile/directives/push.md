---
title: push (diretiva do Caddyfile)
---

# push

Configura o servidor para enviar recursos de forma proativa ao cliente usando HTTP/2 server push.

Recursos podem ser vinculados para server push especificando os cabeçalhos Link da resposta. Esta diretiva enviará automaticamente os recursos descritos por cabeçalhos Link do upstream nestes formatos:

- `<resource>; as=script`
- `<resource>; as=script,<resource>; as=style`
- `<resource>; nopush`
- `<resource>;<resource2>;...`

onde `<resource>` começa com uma barra `/` (isto é, é um caminho de URI no mesmo host). Apenas recursos do mesmo host podem ser enviados. Se um recurso vinculado for externo ou tiver o atributo `nopush`, ele não será enviado.

Por padrão, as requisições de push incluirão alguns cabeçalhos considerados seguros para copiar da requisição original:

- Accept-Encoding
- Accept-Language
- Accept
- Cache-Control
- User-Agent

como se assume que muitas requisições falhariam sem esses cabeçalhos; eles não precisam ser configurados manualmente.

As requisições de push são virtualizadas internamente, então são muito leves.


## Sintaxe

```caddy-d
push [<matcher>] [<resource>] {
	[GET|HEAD] <resource>
	headers {
		[+]<field> [<value|regexp> [<replacement>]]
		-<field>
	}
}
```

- **&lt;resource&gt;** é o caminho de URI de destino a ser enviado. Se usado dentro do bloco, pode ser precedido opcionalmente pelo método (GET ou POST; GET é o padrão).
- **&lt;headers&gt;** manipula os cabeçalhos da requisição de push usando a mesma sintaxe da [`diretiva header`](/docs/caddyfile/directives/header). Alguns cabeçalhos são carregados por padrão e não precisam ser configurados explicitamente (veja acima).



## Exemplos

Envia qualquer recurso descrito por cabeçalhos `Link` na resposta:

```caddy-d
push
```

O mesmo, mas também envia `/resources/style.css` para todas as requisições:

```caddy-d
push * /resources/style.css
```

Envia `/foo.jpg` apenas quando `/foo.html` for solicitado pelo cliente:

```caddy-d
push /foo.html /foo.jpg
```
