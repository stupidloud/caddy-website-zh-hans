---
title: log_skip (diretiva do Caddyfile)
---

# log_skip

Pula o access logging para requisições correspondentes.

Isso deve ser usado junto com a [`diretiva log`](log) para pular o logging de requisições que não sejam relevantes para suas necessidades.

Antes da v2.8.0, esta diretiva se chamava `skip_log`, mas foi renomeada para consistência com outras diretivas.


## Sintaxe

```caddy-d
log_skip [<matcher>]
```


## Exemplos

Pular o access logging de arquivos estáticos armazenados em um subcaminho:

```caddy
example.com {
	root /srv

	log
	log_skip /static*

	file_server
}
```


Pular o access logging de requisições que correspondem a um padrão; neste caso, para arquivos com extensões específicas:

```caddy-d
@skip path_regexp \.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```


O matcher não é necessário se ele estiver dentro de uma rota que já esteja dentro de um matcher. Por exemplo, com um handle para um file server para um subcaminho específico:

```caddy-d
handle_path /static* {
	root /srv/static
	log_skip
	file_server
}
```
