---
title: abort (diretiva do Caddyfile)
---

# abort

Impede qualquer resposta ao cliente ao abortar imediatamente a cadeia de handlers HTTP e fechar a conexão. Quaisquer streams HTTP concorrentes e ativos na mesma conexão são interrompidos.


## Sintaxe

```caddy-d
abort [<matcher>]
```

## Exemplos

Feche à força uma conexão recebida para domínios desconhecidos ao usar um certificado curinga:

```caddy
*.example.com {
    @foo host foo.example.com
    handle @foo {
        respond "Este é o foo!" 200
    }

    handle {
		# Domínios não tratados caem aqui,
		# mas não queremos aceitar as requisições deles
        abort
    }
}
```
