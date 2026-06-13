---
title: templates (Caddyfile directive)
---

# templates

Executa o corpo da resposta como um documento de [template](/docs/modules/http.handlers.templates). Templates fornecem primitivos funcionais para criar páginas dinâmicas simples. Os recursos incluem subrequisições HTTP, inclusão de arquivos HTML, renderização de Markdown, análise de JSON, estruturas de dados básicas, aleatoriedade, tempo e muito mais.

<aside class="tip">

Os templates podem ser executados sobre o corpo da resposta de *qualquer* origem, seja um arquivo estático em disco ou um serviço web atrás de um proxy. Seria sensato habilitar a avaliação de templates apenas para conteúdo em que você confia, que controla e/ou que sanitiza! Uma configuração incorreta pode resultar em falhas de segurança. Por exemplo, se um app atrás de um proxy permitir que usuários escrevam/publiquem conteúdo, e esse conteúdo contiver texto que se pareça com ações de template, isso permitiria que usuários arbitrários avaliassem templates e potencialmente acessassem o ambiente, os arquivos locais e a rede. Não habilite templates em conteúdo gerado por usuários (sem sanitizá-lo).

</aside>


<a id="syntax"></a>
## Sintaxe

```caddy-d
templates [<matcher>] {
	mime    <types...>
	between <open_delim> <close_delim>
	root    <path>
	extensions {
		<name> {
			...
		}
	}
}
```

- **mime** são os tipos MIME sobre os quais o middleware de templates atuará; qualquer resposta que não tenha um `Content-Type` qualificado não será avaliada como template.

  Padrão: `text/html text/plain`.

- **between** são os delimitadores de abertura e fechamento para as ações de template. Você pode alterá-los se eles interferirem com o restante do seu documento.

  Padrão: `{{printf "{{ }}"}}`.

- **root** é a raiz do site, usada quando se empregam funções que acessam o sistema de arquivos.

  O padrão é a raiz do site definida pela diretiva [`root`](root), ou o diretório de trabalho atual, se nada tiver sido definido.

- **extensions** permite registrar funções de template personalizadas fornecidas por módulos no namespace `http.handlers.templates.functions.*`.

  Cada subdiretiva dentro do bloco corresponde a um nome de módulo. Esses módulos podem adicionar funções personalizadas ao mapa de funções do template, normalmente usadas para implementar componentes reutilizáveis. Este recurso é voltado principalmente para plugins.

A documentação das funções de template embutidas pode ser encontrada no [módulo templates](/docs/modules/http.handlers.templates#docs).


<a id="examples"></a>
## Exemplos

Para um exemplo completo de um site usando templates para servir markdown, veja o código-fonte [deste próprio site](https://github.com/caddyserver/website)! Em particular, confira o [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile) e [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html).

Habilitar templates para um site estático:

```caddy
example.com {
	root /srv
	templates
	file_server
}
```

Para servir uma resposta estática simples usando um template, lembre-se de definir `Content-Type`:

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `Current year is: {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

Usando uma extensão de template (plugin):

```caddy
example.com {
	root /srv
	templates {
		extensions {
			# Requer o plugin caddy-hitcounter:
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
```
