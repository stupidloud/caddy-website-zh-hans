---
title: fs (diretiva do Caddyfile)
---

# fs

Define qual sistema de arquivos deve ser usado para realizar E/S de arquivos.

Isso pode permitir conectar-se a um filesystem remoto executando na nuvem, ou a um banco de dados com interface semelhante a arquivo, ou até mesmo ler arquivos embutidos dentro do binário do Caddy.

Primeiro, você deve declarar um nome de sistema de arquivos usando a [opção global `filesystem`](/docs/caddyfile/options#filesystem); depois, pode usar esta diretiva para especificar qual sistema de arquivos usar.

Essa diretiva é frequentemente usada em conjunto com a [`diretiva file_server`](file_server) para servir arquivos estáticos, ou com a [`diretiva try_files`](try_files) para realizar rewrites com base na existência de arquivos. Normalmente também é usada com a [`diretiva root`](root) para definir o caminho raiz dentro do sistema de arquivos.


## Sintaxe

```caddy-d
fs [<matcher>] <filesystem>
```

## Exemplos

Usando um sistema de arquivos chamado `foo`, com um módulo imaginário chamado `custom` que pode exigir autenticação:

```caddy
{
	filesystem foo custom {
		api_key abc123
	}
}

example.com {
	fs foo
	root /srv
	file_server
}
```

Para servir apenas imagens do sistema de arquivos `foo`, e o restante do sistema de arquivos padrão:

```caddy
example.com {
	fs /images* foo
	root /srv
	file_server
}
```
