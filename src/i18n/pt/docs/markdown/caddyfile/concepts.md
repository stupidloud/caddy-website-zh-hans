---
title: Conceitos do Caddyfile
---

<a id="caddyfile-concepts"></a>
# Conceitos do Caddyfile

Este documento vai ajudar você a aprender os detalhes do Caddyfile HTTP.

1. [Estrutura](#structure)
	- [Blocos](#blocks)
	- [Diretivas](#directives)
	- [Tokens e aspas](#tokens-and-quotes)
2. [Opções globais](#global-options)
3. [Endereços](#addresses)
4. [Matchers](#matchers)
5. [Placeholders](#placeholders)
6. [Snippets](#snippets)
7. [Rotas nomeadas](#named-routes)
8. [Comentários](#comments)
9. [Variáveis de ambiente](#environment-variables)



<a id="structure"></a>
## Estrutura

A estrutura do Caddyfile pode ser descrita visualmente:

<style>
	:root {
		--struct-border-global: #e74c3c;
		--struct-border-snippet: #2ecc71;
		--struct-border-site: #3498db;
		--struct-border-matcher: #d453d4;
		--struct-bg-1: #edf5fd;
		--struct-bg-2: #f8fbfd;
		--struct-bg-end: 100%;
		--struct-fg: #254048;
		--struct-opt-name-bg: #ffd9dd;
		--struct-opt-name-fg: #7a2a39;
		--struct-opt-value-bg: #f4dec6;
		--struct-opt-value-fg: #5a3723;
		--struct-comment-bg: #d2d7d8;
		--struct-comment-fg: #495456;
		--struct-site-addr-bg: #cbe4f2;
		--struct-site-addr-fg: #1f6f9a;
		--struct-directive-bg: #c8f7d6;
		--struct-directive-fg: #14663a;
		--struct-matcher-token-bg: #ffd6ff;
		--struct-matcher-token-fg: #6f2070;
		--struct-arg-bg: #ded0ff;
		--struct-arg-fg: #4b2f7a;
		--struct-subdir-bg: #dbbca2;
		--struct-subdir-fg: #5b3a25;
	}
	html.dark {
		--struct-border-global: #e74c3c;
		--struct-border-snippet: #2ecc71;
		--struct-border-site: #3498db;
		--struct-border-matcher: #d453d4;
		--struct-bg-1: #0d313c;
		--struct-bg-2: transparent;
		--struct-bg-end: 120%;
		--struct-fg: #cbd6da;
		--struct-opt-name-bg: #6b2630;
		--struct-opt-name-fg: #ffd9dd;
		--struct-opt-value-bg: #68412b;
		--struct-opt-value-fg: #f4dec6;
		--struct-comment-bg: #2f424d;
		--struct-comment-fg: #e8eef0;
		--struct-site-addr-bg: #204d59;
		--struct-site-addr-fg: #d6f0ff;
		--struct-directive-bg: #1f4e36;
		--struct-directive-fg: #c8f7d6;
		--struct-matcher-token-bg: #65305a;
		--struct-matcher-token-fg: #ffd6ff;
		--struct-arg-bg: #3b2e46;
		--struct-arg-fg: #ded0ff;
		--struct-subdir-bg: #6a4a2e;
		--struct-subdir-fg: #ebc095;
	}
	/* color variables - easy to tweak */
	.struct-caddyfile-visual-repl {
		display: block;
		margin: 0;
		padding: 0;
	}
	/* default (light) visual background */
	.struct-caddyfile-visual-repl .struct-visual {
		box-sizing: border-box;
		margin: 0 0 1.25rem;
		padding: 14px;
		border-radius: 14px;
		background: linear-gradient(to bottom, var(--struct-bg-1) 0%, var(--struct-bg-2) var(--struct-bg-end));
		color: var(--struct-fg);
		font-family: Inter, 'Source Sans Pro', Arial, system-ui, sans-serif;
		line-height: 1.2;
	}
	/* layout */
	.struct-caddyfile-visual-repl .struct-panel {
		display: flex;
		gap: 18px;
		align-items: flex-start;
		flex-wrap: wrap;
	}
	.struct-caddyfile-visual-repl .struct-diagram {
		flex: 1;
		padding: 8px 8px;
	}
	.struct-caddyfile-visual-repl .struct-legend {
		width: 310px;
		padding: 12px 4px;
	}
	/* code-like box: use normal whitespace so HTML pretty-printing won't leak source indentation */
	.struct-caddyfile-visual-repl .struct-code-box {
		background: transparent;
		border-radius: 8px;
		padding: 6px 6px !important;
		font-family: var(--monospace-fonts);
		font-size: 90%;
		white-space: normal;
	}
	.struct-block {
		border-radius: 8px;
		padding: 10px;
		margin: 0 0 10px 0;
	}
	.struct-block.global {
		border: 4px solid var(--struct-border-global);
	}
	.struct-block.snippet {
		border: 4px solid var(--struct-border-snippet);
	}
	.struct-block.site {
		border: 4px solid var(--struct-border-site);
	}
	.struct-block.matcher {
		border: 4px solid var(--struct-border-matcher);
		margin: 8px 8px 10px 10px;
		padding: 8px;
		border-radius: 6px;
	}
	.struct-token, .struct-opt-name, .struct-opt-value, .struct-comment, .struct-site-addr, .struct-directive, .struct-matcher-token, .struct-arg, .struct-subdir {
		display: inline !important;
		padding: .03rem .18rem !important;
		border-radius: 6px;
		font-family: var(--monospace-fonts);
		font-size: 95%;
		vertical-align: middle;
	}
	.struct-opt-name {
		background: var(--struct-opt-name-bg);
		color: var(--struct-opt-name-fg);
	}
	.struct-opt-value {
		background: var(--struct-opt-value-bg);
		color: var(--struct-opt-value-fg);
	}
	.struct-comment {
		background: var(--struct-comment-bg);
		color: var(--struct-comment-fg);
	}
	.struct-site-addr {
		background: var(--struct-site-addr-bg);
		color: var(--struct-site-addr-fg);
	}
	.struct-directive {
		background: var(--struct-directive-bg);
		color: var(--struct-directive-fg);
	}
	.struct-matcher-token {
		background: var(--struct-matcher-token-bg);
		color: var(--struct-matcher-token-fg);
	}
	.struct-arg {
		background: var(--struct-arg-bg);
		color: var(--struct-arg-fg);
	}
	.struct-subdir {
		background: var(--struct-subdir-bg);
		color: var(--struct-subdir-fg);
	}
	.struct-legend .struct-legend-title {
		font-weight: 700;
		font-size: 1.6rem;
	}
	.struct-legend .struct-item {
		display: flex;
		align-items: center;
		gap: 10px;
		margin: 16px 0;
	}
	.struct-legend .struct-item-spacer {
		height: 8px;
	}
	/* swatch for border-based legend items (blocks) */
	.struct-legend .struct-swatch-border {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		border: 4px solid transparent;
		background: transparent;
	}
	/* swatch for filled legend items (text backgrounds) */
	.struct-legend .struct-swatch-fill {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		background: transparent;
	}
	.struct-legend .struct-label {
		font-size: 90%;
		color: inherit;
	}
	.struct-caddyfile-visual-repl .struct-visual, .struct-caddyfile-visual-repl .struct-panel, .struct-caddyfile-visual-repl .struct-diagram, .struct-caddyfile-visual-repl .struct-legend, .struct-caddyfile-visual-repl .struct-code-box {
		margin: 0;
	}
	/* force compact vertical rhythm and explicit indenting so global CSS can't leak in
		NOTE: use normal whitespace so server-side HTML formatting doesn't create visible gaps */
	.struct-line {
		display: block !important;
		margin: 0 !important;
		padding: 2px 0 !important;
		line-height: 1.2 !important;
		white-space: normal !important;
	}
	/* helper to visually indent lines (do not rely on source file whitespace)
		use an explicit spacer element so HTML formatting won't affect alignment */
	.struct-line.struct-indent {
		padding-left: 0 !important;
	}
	.struct-indent-spacer {
		display: inline-block;
		width: 1.2rem;
		height: 1px;
		margin-right: 0.18rem;
	}
	/* smaller spacer for sub-directive / nested lines */
	.struct-subindent-spacer {
		display: inline-block;
		width: 0.9rem;
		height: 1px;
		margin-right: 0.12rem;
	}
</style>

<div class="struct-caddyfile-visual-repl fullwidth">
	<div class="struct-visual">
		<div class="struct-panel">
			<div class="struct-diagram">
				<div class="struct-code-box">
					<div class="struct-block global">
						<div class="struct-line">{</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">email</span> <span class="struct-opt-value">you@yours.com</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">servers</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">trusted_proxies</span> <span class="struct-arg">static</span> <span class="struct-arg">private_ranges</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block snippet">
						<div class="struct-line">(snippet) {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-comment"># este é um snippet reutilizável</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">log</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">output</span> <span class="struct-arg">file</span> <span class="struct-arg">/var/log/access.log</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line"><span class="struct-site-addr">example.com</span> {</div>
						<div class="struct-block matcher">
							<div class="struct-line"><span class="struct-matcher-token">@post</span> {</div>
							<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-matcher-token">method</span> <span class="struct-arg">POST</span></div>
							<div class="struct-line">}</div>
						</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">reverse_proxy</span> <span class="struct-matcher-token">@post</span> <span class="struct-arg">localhost:9001</span> <span class="struct-arg">localhost:9002</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">lb_policy</span> <span class="struct-arg">first</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">file_server</span> <span class="struct-matcher-token">/static</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">import</span> <span class="struct-arg">snippet</span></div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line struct-indent"><span class="struct-site-addr">www.example.com</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">redir</span> <span class="struct-arg">https://example.com{uri}</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">import</span> <span class="struct-arg">snippet</span></div>
						<div class="struct-line">}</div>
					</div>
				</div>
			</div>
			<div class="struct-legend" aria-hidden="false">
				<div class="struct-legend-title">Legenda</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">Bloco de opções globais</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">Snippet</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">Bloco de site</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-matcher)"></div><div class="struct-label">Definição de matcher</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">Nome da opção</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">Valor da opção</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">Comentário</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">Endereço do site</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">Diretiva</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">Token de matcher</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">Argumento</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">Subdiretiva</div></div>
			</div>
		</div>
	</div>
</div>

Pontos-chave:

- Um [**bloco de opções globais**](#global-options) opcional pode ser a primeira coisa do arquivo.

- [Snippets](#snippets) ou [rotas nomeadas](#named-routes) podem aparecer em seguida, de forma opcional.

- Caso contrário, a primeira linha do Caddyfile é **sempre** o(s) [endereço(s)](#addresses) do site a servir.

- Todas as [diretivas](#directives) e [matchers](#matchers) **devem** ficar dentro de um bloco de site. Não existe escopo global nem herança entre blocos de site.

- Se houver apenas um bloco de site, as chaves `{ }` são opcionais.

Um Caddyfile consiste em pelo menos um bloco de site, que sempre começa com um ou mais [endereços](#addresses) do site. Qualquer diretiva que apareça antes do endereço vai confundir o parser.


<a id="blocks"></a>
### Blocos

Abrir e fechar um **bloco** é feito com chaves:

```caddy
... {
	...
}
```

- A chave de abertura `{` deve ficar no fim da linha e ser precedida por um espaço.

- A chave de fechamento `}` deve ficar em uma linha própria.

Quando há apenas um bloco de site, as chaves (e a indentação) são opcionais. Isso serve para facilitar a definição rápida de um único site. Por exemplo, isto:

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

é equivalente a:

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

quando você tem apenas um bloco de site; é uma questão de preferência.

Para configurar vários sites com o mesmo Caddyfile, você **deve** usar chaves em torno de cada um para separar as configurações:

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

Se uma requisição corresponder a vários blocos de site, será escolhido o bloco com o endereço correspondente mais específico. As requisições não continuam para outros blocos de site.


<a id="directives"></a>
### Diretivas

[**Diretivas**](/docs/caddyfile/directives) são palavras-chave funcionais que personalizam como o site é servido. Elas **devem** aparecer dentro de blocos de site. Por exemplo, uma configuração completa de file server pode ser assim:

```caddy
localhost {
	file_server
}
```

Ou um reverse proxy:

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

Nesses exemplos, [`file_server`](/docs/caddyfile/directives/file_server) e [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) são diretivas. Diretivas são a primeira palavra de uma linha dentro de um bloco de site.

No segundo exemplo, `localhost:9000` é um **argumento** porque aparece na mesma linha depois da diretiva.

Às vezes as diretivas podem abrir seus próprios blocos. **Subdiretivas** aparecem no início de cada linha dentro de blocos de diretiva:

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

Aqui, `lb_policy` é uma subdiretiva de [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) (ela define a política de balanceamento de carga usada entre os backends).

**A menos que a documentação diga o contrário, diretivas não podem ser usadas dentro de outros blocos de diretiva.** Por exemplo, [`basic_auth`](/docs/caddyfile/directives/basic_auth) não pode ser usado dentro de [`file_server`](/docs/caddyfile/directives/file_server) porque o file server não sabe fazer autenticação; mas você pode usar diretivas dentro de blocos [`route`](/docs/caddyfile/directives/route), [`handle`](/docs/caddyfile/directives/handle) e [`handle_path`](/docs/caddyfile/directives/handle_path), porque eles foram projetados especificamente para agrupar diretivas.

Observe que, quando o Caddyfile HTTP é adaptado, as diretivas de handler HTTP são ordenadas segundo uma [ordem padrão de diretivas](/docs/caddyfile/directives#directive-order) específica, a menos que estejam em um bloco [`route`](/docs/caddyfile/directives/route). Portanto, a ordem em que as diretivas aparecem não importa, exceto em blocos `route`.


<a id="tokens-and-quotes"></a>
### Tokens e aspas

O Caddyfile é transformado em tokens antes de ser analisado. Espaços em branco são significativos no Caddyfile, porque os tokens são separados por espaços.

Muitas vezes, as diretivas esperam uma certa quantidade de argumentos; se um único argumento tiver um valor com espaços, ele será transformado em dois tokens separados:

```caddy-d
directive abc def
```

Isso pode ser problemático e gerar erros ou comportamento inesperado.

Se `abc def` for o valor de um único argumento, ele precisa estar entre aspas:

```caddy-d
directive "abc def"
```

As aspas podem ser escapadas se você também precisar usar aspas dentro de tokens entre aspas:

```caddy-d
directive "\"abc def\""
```

Para evitar escapar aspas, você pode usar crases <code>\` \`</code> para delimitar tokens; por exemplo:

```caddy-d
directive `{"foo": "bar"}`
```

Dentro de tokens entre aspas, todos os outros caracteres são tratados literalmente, incluindo espaços, tabs e quebras de linha. Portanto, tokens multilinha são possíveis:

```caddy-d
directive "first line
	second line"
```

Heredocs <span id="heredocs"/> também são suportados:

```caddy
example.com {
	respond <<HTML
		<html>
		  <head><title>Foo</title></head>
		  <body>Foo</body>
		</html>
		HTML 200
}
```

O marcador inicial do heredoc deve começar com `<<`, seguido por qualquer texto (recomendam-se letras maiúsculas). O marcador final do heredoc deve ter o mesmo texto (no exemplo acima, `HTML`). O marcador inicial pode ser escapado com `\<<` para impedir o parsing de heredoc, se necessário.

O marcador final pode ser indentado, o que faz com que cada linha de texto tenha essa mesma indentação removida (inspirado no [PHP](https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc)), o que é útil para legibilidade dentro de [blocos](#blocks) e dá bastante controle sobre os espaços em branco no texto do token. A quebra de linha final também é removida, mas pode ser mantida adicionando uma linha em branco extra antes do marcador final.

Tokens adicionais podem seguir o marcador final como argumentos da diretiva (como no exemplo acima, o código de status `200`).


<a id="global-options"></a>
## Opções globais

Um Caddyfile pode começar opcionalmente com um bloco especial sem chaves, chamado de [bloco de opções globais](/docs/caddyfile/options):

```caddy
{
	...
}
```

Se estiver presente, ele deve ser o primeiro bloco da configuração.

Ele é usado para definir opções que se aplicam globalmente, ou que não se aplicam a nenhum site em particular. No interior desse bloco, só podem ser definidas opções globais; não é possível usar diretivas normais de site.

Por exemplo, para habilitar a opção global `debug`, que é comumente usada para gerar logs verbosos para depuração:

```caddy
{
	debug
}
```

**[Leia a página de Opções Globais](/docs/caddyfile/options) para saber mais.**



<a id="addresses"></a>
## Endereços

Um endereço sempre aparece no topo do bloco de site e geralmente é a primeira coisa no Caddyfile.

Estes são exemplos de endereços válidos:

| Endereço              | Efeito                            |
|----------------------|-----------------------------------|
| `example.com`        | HTTPS com [certificado público confiável](/docs/automatic-https#hostname-requirements) gerenciado |
| `*.example.com`      | HTTPS com [certificado curinga público confiável](/docs/caddyfile/patterns#wildcard-certificates) gerenciado |
| `localhost`          | HTTPS com [certificado confiável localmente](/docs/automatic-https#local-https) gerenciado |
| `http://`            | HTTP para todos, afetado por [`http_port`](/docs/caddyfile/options#http-port) |
| `https://`           | HTTPS para todos, afetado por [`https_port`](/docs/caddyfile/options#http-port) |
| `http://example.com` | HTTP explicitamente, com um matcher `Host` |
| `example.com:443`    | HTTPS por corresponder ao padrão de [`https_port`](/docs/caddyfile/options#http-port) |
| `:443`               | HTTPS para todos por corresponder ao padrão de [`https_port`](/docs/caddyfile/options#http-port) |
| `:8080`              | HTTP em porta não padrão, sem matcher `Host` |
| `localhost:8080`     | HTTPS em porta não padrão, por ter um domínio válido |
| `https://example.com:443` | HTTPS, mas usar `https://` e `:443` ao mesmo tempo é redundante |
| `127.0.0.1` | HTTPS, com um certificado de IP confiável localmente |
| `http://127.0.0.1` | HTTP, com um matcher `Host` baseado em endereço IP (rejeita `localhost`) |

<aside class="tip">

[Automatic HTTPS](/docs/automatic-https) é ativado se o endereço do seu site contiver um hostname ou endereço IP. Esse comportamento, porém, é puramente implícito, então ele nunca substitui nenhuma configuração explícita.

Por exemplo, se o endereço do site for `http://example.com`, o auto-HTTPS não será ativado porque o esquema foi explicitamente definido como `http://`.

</aside>


A partir do endereço, o Caddy pode inferir potencialmente o esquema, o host e a porta do seu site. Se o endereço não tiver porta, o Caddyfile escolherá a porta correspondente ao esquema, se ele estiver especificado, ou assumirá a porta padrão 443.

Se você especificar um hostname, somente requisições com um cabeçalho `Host` correspondente serão aceitas. Em outras palavras, se o endereço do site for `localhost`, o Caddy não corresponderá a requisições para `127.0.0.1`.

Wildcards (`*`) podem ser usados, mas apenas para representar exatamente um rótulo do hostname. Por exemplo, `*.example.com` corresponde a `foo.example.com`, mas não a `foo.bar.example.com`, e `*` corresponde a `localhost`, mas não a `example.com`. Veja o [padrão de certificados curinga](/docs/caddyfile/patterns#wildcard-certificates) para um exemplo prático.

Para aceitar todos os hosts, omita a parte do host do endereço, por exemplo, simplesmente `https://`. Isso é útil ao usar [TLS sob demanda](/docs/automatic-https#on-demand-tls), quando você ainda não sabe os domínios.

Se vários sites compartilharem a mesma definição, você pode listá-los juntos, separados por espaços e vírgulas (é necessário pelo menos um espaço). Os três exemplos a seguir são equivalentes:

```caddy
# Endereços de site separados por vírgulas
localhost:8080, example.com, www.example.com {
	...
}
```

ou

```caddy
# Endereços de site separados por espaços
localhost:8080 example.com www.example.com {
	...
}
```

ou

```caddy
# Endereços de site separados por vírgulas e novas linhas
localhost:8080,
example.com,
www.example.com {
	...
}
```

Um endereço precisa ser único; você não pode especificar o mesmo endereço mais de uma vez.

[Placeholders](#placeholders) **não** podem ser usados em endereços, mas você pode usar [variáveis de ambiente no estilo do Caddyfile](#environment-variables) neles:

```caddy
{$DOMAIN:localhost} {
	...
}
```

Por padrão, os sites fazem bind em todas as interfaces de rede. Se quiser sobrescrever isso, use a [`diretiva bind`](/docs/caddyfile/directives/bind) ou a [`opção global default_bind`](/docs/caddyfile/options#default-bind).



<a id="matchers"></a>
## Matchers

As [diretivas](#directives) de handler HTTP se aplicam a todas as requisições por padrão (a menos que a documentação diga o contrário).

[Matchers de requisição](/docs/caddyfile/matchers) podem ser usados para classificar requisições por um critério específico. Com matchers, você pode especificar exatamente a quais requisições uma determinada diretiva se aplica.

Para diretivas que suportam matchers, o primeiro argumento depois da diretiva é o **token de matcher**. Aqui estão alguns exemplos:

```caddy-d
root *           /var/www  # token de matcher: *
root /index.html /var/www  # token de matcher: /index.html
root @post       /var/www  # token de matcher: @post
```

Os tokens de matcher podem ser omitidos por completo para corresponder a todas as requisições; por exemplo, `*` não precisa ser fornecido se o próximo argumento não parecer um matcher de caminho.

**[Leia a página de Matchers de Requisição](/docs/caddyfile/matchers) para saber mais.**




<a id="placeholders"></a>
## Placeholders

[Placeholders](/docs/conventions#placeholders) são uma forma simples de inserir valores dinâmicos na sua configuração estática. Eles podem ser usados como argumentos de diretivas e subdiretivas.

Placeholders são delimitados por chaves `{ }` e contêm o identificador no interior, por exemplo: `{foo.bar}`. A chave de abertura do placeholder pode ser escapada com `\{like.this}` para impedir a substituição. Os identificadores de placeholder normalmente usam namespaces com pontos para evitar colisões entre módulos.

Quais placeholders estão disponíveis depende do contexto. Nem todos os placeholders estão disponíveis em todas as partes da configuração. Por exemplo, [o app HTTP define placeholders](/docs/json/apps/http/#docs) que só ficam disponíveis em áreas da configuração relacionadas ao tratamento de requisições HTTP (isto é, em [diretivas](#directives) e [matchers](#matchers) de handler HTTP, mas _não_ em [configuração `tls`](/docs/caddyfile/directives/tls)). Algumas diretivas ou matchers também podem definir seus próprios placeholders, que podem ser usados por qualquer coisa que venha depois. Alguns placeholders [estão disponíveis globalmente](/docs/conventions#placeholders).

Você pode usar qualquer placeholder no Caddyfile, mas, por conveniência, também pode usar alguns destes atalhos equivalentes, que são expandidos quando o Caddyfile é analisado:

| Caddyfile        | Substitui                            |
|------------------|--------------------------------------|
| `{cookie.*}`     | `{http.request.cookie.*}`           |
| `{client_ip}`    | `{http.vars.client_ip}`             |
| `{dir}`          | `{http.request.uri.path.dir}`       |
| `{err.*}`        | `{http.error.*}`                    |
| `{file_match.*}` | `{http.matchers.file.*}`            |
| `{file.base}`    | `{http.request.uri.path.file.base}` |
| `{file.ext}`     | `{http.request.uri.path.file.ext}`  |
| `{file}`         | `{http.request.uri.path.file}`      |
| `{header.*}`     | `{http.request.header.*}`           |
| `{host}`         | `{http.request.host}`               |
| `{hostport}`     | `{http.request.hostport}`           |
| `{labels.*}`     | `{http.request.host.labels.*}`      |
| `{method}`       | `{http.request.method}`             |
| `{orig_method}`  | `{http.request.orig_method}`        |
| `{orig_uri}`     | `{http.request.orig_uri}`           |
| `{orig_path}`    | `{http.request.orig_uri.path}`      |
| `{orig_dir}`     | `{http.request.orig_uri.path.dir}`  |
| `{orig_file}`    | `{http.request.orig_uri.path.file}` |
| `{orig_query}`   | `{http.request.orig_uri.query}`     |
| `{orig_?query}`  | `{http.request.orig_uri.prefixed_query}` |
| `{path.*}`       | `{http.request.uri.path.*}`         |
| `{path}`         | `{http.request.uri.path}`           |
| `{%path}`        | `{http.request.uri.path_escaped}`   |
| `{port}`         | `{http.request.port}`               |
| `{query.*}`      | `{http.request.uri.query.*}`        |
| `{query}`        | `{http.request.uri.query}`          |
| `{%query}`       | `{http.request.uri.query_escaped}`  |
| `{?query}`       | `{http.request.uri.prefixed_query}` |
| `{re.*}`         | `{http.regexp.*}`                   |
| `{remote_host}`  | `{http.request.remote.host}`        |
| `{remote_port}`  | `{http.request.remote.port}`        |
| `{remote}`       | `{http.request.remote}`             |
| `{rp.*}`         | `{http.reverse_proxy.*}`            |
| `{resp.*}`       | `{http.intercept.*}`                |
| `{scheme}`       | `{http.request.scheme}`             |
| `{tls_cipher}`   | `{http.request.tls.cipher_suite}`   |
| `{tls_client_certificate_der_base64}` | `{http.request.tls.client.certificate_der_base64}` |
| `{tls_client_certificate_pem}`        | `{http.request.tls.client.certificate_pem}` |
| `{tls_client_fingerprint}`            | `{http.request.tls.client.fingerprint}`     |
| `{tls_client_issuer}`                 | `{http.request.tls.client.issuer}`          |
| `{tls_client_serial}`                 | `{http.request.tls.client.serial}`          |
| `{tls_client_subject}`                | `{http.request.tls.client.subject}`         |
| `{tls_version}`       | `{http.request.tls.version}`             |
| `{upstream_hostport}` | `{http.reverse_proxy.upstream.hostport}` |
| `{uri}`               | `{http.request.uri}`                     |
| `{%uri}`              | `{http.request.uri_escaped}`             |
| `{vars.*}`            | `{http.vars.*}`                          |

Nem todos os campos da configuração suportam placeholders, mas a maioria suporta onde você esperaria isso. O suporte a placeholders precisa ter sido adicionado explicitamente a esses campos. Os autores de plugins podem [ler este artigo](/docs/extending-caddy/placeholders) para aprender a adicionar suporte a placeholders em seus próprios módulos.




<a id="snippets"></a>
## Snippets

Você pode definir blocos especiais chamados snippets dando a eles um nome cercado por parênteses:

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

Depois, você pode reutilizá-los em qualquer lugar onde precisar, usando a diretiva especial [`import`](/docs/caddyfile/directives/import):

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

A diretiva [`import`](/docs/caddyfile/directives/import) também pode ser usada para incluir outros arquivos no lugar dela. Se o argumento não corresponder a um snippet definido, ele será tratado como arquivo. Ela também aceita globs para importar vários arquivos. Como caso especial, ela pode aparecer em qualquer lugar do Caddyfile (exceto como argumento de outra diretiva), inclusive fora de blocos de site:

```caddy
{
	email admin@example.com
}

import sites/*
```

Você pode passar argumentos para uma configuração importada (snippets ou arquivos) e usá-los assim:

```caddy
(snippet) {
	respond "Yahaha! You found {args[0]}!"
}

a.example.com {
	import snippet "Example A"
}

b.example.com {
	import snippet "Example B"
}
```

⚠️ <i>Experimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Você também pode passar um bloco opcional a um snippet importado e usá-lo da seguinte forma.

```caddy
(snippet) {
	{block}
	respond "OK"
}

a.example.com {
	import snippet {
		header +foo bar
	}
}

b.example.com {
	import snippet {
		header +bar foo
	}
}
```

**[Leia a página da diretiva `import`](/docs/caddyfile/directives/import) para saber mais.**


<a id="named-routes"></a>
## Rotas nomeadas

⚠️ <i>Experimental</i>

Rotas nomeadas usam uma sintaxe parecida com [snippets](#snippets); elas são blocos especiais definidos fora de blocos de site, prefixados com `&(` e terminados em `)` com o nome no meio.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

Depois, você pode reutilizar essa rota nomeada em qualquer site:

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

Isso é especialmente útil para reduzir o uso de memória se a mesma rota for necessária em muitos sites diferentes, ou se forem necessárias várias condições de matcher diferentes para invocar a mesma rota.

**[Leia a página da diretiva `invoke`](/docs/caddyfile/directives/invoke) para saber mais.**



<a id="comments"></a>
## Comentários

Comentários começam com `#` e vão até o fim da linha:

```caddy-d
# Comentários podem começar uma linha
directive  # ou ir no final
```

O caractere de hash `#` de um comentário não pode aparecer no meio de um token (isto é, ele precisa ser precedido por um espaço ou aparecer no início de uma linha). Isso permite usar hashes em URIs ou outros valores sem precisar de aspas.



<a id="environment-variables"></a>
## Variáveis de ambiente

Se a sua configuração depender de variáveis de ambiente, você pode usá-las no Caddyfile:

```caddy
{$ENV}
```

Variáveis de ambiente nesse formato são substituídas **antes do início do parsing do Caddyfile**, então elas podem expandir para valores vazios (isto é, `""`), tokens parciais, tokens completos ou até vários tokens e linhas.

Por exemplo, uma variável de ambiente `UPSTREAMS="app1:8080 app2:8080 app3:8080"` se expandiria para vários [tokens](#tokens-and-quotes):

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

Um valor padrão pode ser especificado para quando a variável de ambiente não for encontrada, usando `:` como delimitador entre o nome da variável e o valor padrão:

```caddy
{$DOMAIN:localhost} {

}
```

Se você quiser **adiar a substituição** de uma variável de ambiente até o tempo de execução, pode usar os [placeholders padrão `{env.*}`](/docs/conventions#placeholders). Observe, porém, que nem todos os parâmetros de configuração suportam esses placeholders, já que os desenvolvedores de módulos precisam adicionar uma linha de código para fazer a substituição. Se não parecer funcionar, abra uma issue para solicitar suporte.

Por exemplo, se você tiver o [plugin `caddy-dns/cloudflare` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns/cloudflare) instalado e quiser configurar o [desafio DNS](/docs/automatic-https#dns-challenge), você pode passar a variável de ambiente `CLOUDFLARE_API_TOKEN` para o plugin assim:

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Se você estiver executando o Caddy como um serviço systemd, veja [estas instruções](/docs/running#overrides) para definir overrides do serviço e declarar suas variáveis de ambiente.
