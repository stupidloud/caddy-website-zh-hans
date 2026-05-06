---
title: bind (diretiva do Caddyfile)
---

# bind

Substitui a interface à qual o socket do servidor deve fazer bind.

Normalmente, o listener faz bind na interface vazia (curinga). No entanto, você pode forçar o listener a fazer bind em outro hostname ou IP. Esta diretiva aceita apenas um host, não uma porta. A porta é determinada pelo [endereço do site](/docs/caddyfile/concepts#addresses) (com padrão `443`).

Observe que fazer bind em sites de forma inconsistente pode resultar em consequências indesejadas. Por exemplo, se dois sites na mesma porta resolvem para `127.0.0.1` e apenas um deles é configurado com `bind 127.0.0.1`, então apenas um site ficará acessível, já que o outro fará bind na porta sem um host específico; o sistema operacional escolherá o socket correspondente mais específico. (Virtual hosts não são compartilhados entre listeners diferentes.)

`bind` aceita [endereços de rede](/docs/conventions#network-addresses), mas não pode incluir uma porta.


## Sintaxe

```caddy-d
bind <hosts...>
```

- **&lt;hosts...&gt;** é a lista de interfaces de host nas quais o listener fará bind.


## Exemplos

Para tornar um socket acessível apenas na máquina atual, faça bind na interface loopback (localhost):

```caddy
example.com {
	bind 127.0.0.1
}
```

Para incluir IPv6:

```caddy
example.com {
	bind 127.0.0.1 [::1]
}
```

Para fazer bind em `10.0.0.1:8080`:

```caddy
example.com:8080 {
	bind 10.0.0.1
}
```

Para fazer bind em um unix domain socket em `/run/caddy`:

```caddy
example.com {
	bind unix//run/caddy
}
```

Para mudar a permissão do arquivo para que possa ser escrita por todos os usuários ([padrão](/docs/conventions#network-addresses) `0200`, que só é gravável pelo proprietário):

```caddy
example.com {
	bind unix//run/caddy|0222
}
```

Para fazer bind de um domínio em duas interfaces diferentes, com respostas diferentes:

```caddy
example.com {
	bind 10.0.0.1
	respond "Um"
}

example.com {
	bind 10.0.0.2
	respond "Dois"
}
```
