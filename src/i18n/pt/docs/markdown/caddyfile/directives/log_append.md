---
title: log_append (diretiva do Caddyfile)
---

# log_append

Acrescenta um campo ao access log da requisição atual.

Isso deve ser usado junto com a [`diretiva log`](log), que é necessária para habilitar access logging desde o início.

O valor pode ser uma string estática ou um [placeholder](/docs/caddyfile/concepts#placeholders), que será substituído pelo valor do placeholder no momento da requisição.


## Sintaxe

```caddy-d
log_append [<matcher>] [<]<key> <value>
```

Por padrão, o campo de log é adicionado na volta pela cadeia de middleware (isto é, "tardiamente"), depois que todos os handlers subsequentes tiverem sido concluídos (por exemplo, depois de handlers como [`reverse_proxy`](reverse_proxy), [`respond`](respond) ou [`file_server`](file_server), que escrevem uma resposta), então ele captura o estado final da requisição e da resposta.

Se `<` for usado como prefixo da chave, ela é marcada como "early", o que significa que o campo de log será adicionado aos logs _antes_ de chamar o próximo handler na cadeia, para que a requisição possa ser lida antes de ser modificada pelos handlers subsequentes.

Apenas para fins de depuração (não para uso em produção), o handler tem tratamento especializado quando o valor é um destes placeholders: `{http.request.body}`, `{http.request.body_base64}`, `{http.response.body}` ou `{http.response.body_base64}`. Se um placeholder de corpo de requisição for usado, o modo "early" é habilitado implicitamente, e o corpo da requisição será bufferizado. Se um placeholder de corpo de resposta for usado, o buffering da resposta é habilitado para capturar o corpo da resposta e o campo é adicionado ao log "late", enquanto a resposta é escrita.


## Exemplos

Exibe nos logs a área do site de onde a requisição está sendo servida, seja `static` ou `dynamic`:

```caddy
example.com {
	log

	handle /static* {
		log_append area "static"
		respond "Static response!"
	}

	handle {
		log_append area "dynamic"
		reverse_proxy localhost:9000
	}
}
```

Exibe nos logs qual upstream do reverse proxy foi efetivamente usado (seja `node1`, `node2` ou `node3`) e o tempo gasto fazendo proxy para o upstream em milissegundos, além de quanto tempo o upstream levou para escrever o cabeçalho da resposta:

```caddy
example.com {
	log

	handle {
		reverse_proxy node1:80 node2:80 node3:80 {
			lb_policy random_choose 2 
		}
		log_append upstream_host {rp.upstream.host}
		log_append upstream_duration_ms {rp.upstream.duration_ms}
		log_append upstream_latency_ms {rp.upstream.latency_ms}
	}
}
```

Um campo pode ser adicionado aos logs "early" prefixando a chave com `<`. Isso permite capturar o estado da requisição antes que ela seja modificada por handlers subsequentes. Por exemplo, para registrar o caminho original da requisição antes de ele ser reescrito (embora este seja um exemplo artificial, já que o caminho original da requisição já é registrado de qualquer forma, mas ajuda a ilustrar o ponto):

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /new-base{uri}
	reverse_proxy localhost:9000
}
```

Para fins de depuração, adicione os corpos da requisição e da resposta aos logs (não para uso em produção, já que isso prejudica o desempenho e deixa os logs muito verbosos). Se você espera que os corpos sejam dados binários com caracteres não imprimíveis, pode usar as variantes base64 dos placeholders em vez disso (por exemplo, `{http.request.body_base64}` e `{http.response.body_base64}`), que serão mais fáceis de copiar e inspecionar:

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
