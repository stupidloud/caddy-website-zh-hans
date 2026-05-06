---
title: root (diretiva do Caddyfile)
---

# root

Define o caminho raiz do site, usado por vários matchers e diretivas que acessam o sistema de arquivos. Se não for definido, a raiz padrão do site é o diretório de trabalho atual.

Especificamente, esta diretiva define o placeholder `{http.vars.root}`. Ela é mutuamente exclusiva de outras diretivas `root` no mesmo bloco, então é seguro definir várias raízes com matchers que se intersectam: elas não cascatarão nem se sobrescreverão.

Esta diretiva não habilita automaticamente a servir arquivos estáticos, então ela é frequentemente usada em conjunto com a [`diretiva file_server`](file_server) ou com a [`diretiva php_fastcgi`](php_fastcgi).


## Sintaxe

```caddy-d
root [<matcher>] <path>
```

- **&lt;path&gt;** é o caminho a usar como raiz do site.

Antes da v2.8.0, o argumento `<path>` podia ser confundido pelo parser com um [token de matcher](/docs/caddyfile/matchers#syntax) se começasse com `/`, então era necessário especificar um token de matcher curinga (`*`).


## Exemplos

Define a raiz do site como `/home/bob/public_html` (assumindo que o Caddy está rodando como o usuário `bob`):

<aside class="tip">

Se você estiver executando o Caddy como um serviço systemd, ler arquivos de `/home` não funcionará, porque o usuário `caddy` não tem permissão "execute" no diretório `/home` (necessária para atravessar o caminho). É recomendado colocar seus arquivos em `/srv` ou `/var/www/html` em vez disso.

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

Observe que, antes da v2.8.0, um [matcher curinga](/docs/caddyfile/matchers#wildcard-matchers) era necessário aqui porque o primeiro argumento é ambíguo com um [matcher de caminho](/docs/caddyfile/matchers#path-matchers), ou seja, `root * /srv`, mas agora pode ser simplificado para `root /srv`.

</aside>


Define a raiz do site como `public_html` (relativa ao diretório de trabalho atual) para todas as requisições:

```caddy-d
root public_html
```

Altera a raiz do site apenas para requisições em `/foo/*`:

```caddy-d
root /foo/* /home/user/public_html/foo
```

A diretiva `root` é comumente combinada com [`file_server`](file_server) para servir arquivos estáticos e/ou com [`php_fastcgi`](php_fastcgi) para servir um site PHP:

```caddy
example.com {
	root /srv
	file_server
}
```
