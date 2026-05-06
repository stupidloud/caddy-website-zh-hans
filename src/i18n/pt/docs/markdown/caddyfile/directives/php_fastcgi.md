---
title: php_fastcgi (diretiva do Caddyfile)
---

<script>
ready(function() {
	// Vamos adicionar links a todas as subdiretivas se um anchor correspondente for encontrado na página.
	addLinksToSubdirectives();
});
</script>

# php_fastcgi

Uma diretiva opinativa que faz proxy de requisições para um servidor PHP FastCGI como php-fpm.

- [Sintaxe](#syntax)
- [Forma expandida](#expanded-form)
  - [Explicação](#explanation)
- [Exemplos](#examples)

O [`reverse_proxy`](reverse_proxy) do Caddy é capaz de servir qualquer aplicação FastCGI, mas esta diretiva é feita especificamente para apps PHP. Ela é um atalho conveniente, substituindo uma [configuração mais longa](#expanded-form).

Ela espera que qualquer `index.php` na raiz do site atue como roteador. Se isso não for desejável, reconfigure a [`subdiretiva try_files`](#try_files) para modificar o comportamento padrão de rewrite, ou use a [forma expandida](#expanded-form) como base e personalize conforme necessário.

Além das subdiretivas listadas abaixo, esta diretiva também suporta todas as subdiretivas de [`reverse_proxy`](reverse_proxy#syntax). Por exemplo, você pode habilitar balanceamento de carga e health checks.

**A maioria dos apps PHP modernos funciona bem sem subdiretivas extras ou personalizações.** As subdiretivas normalmente só são usadas em alguns casos de borda ou com apps PHP legados.

<a id="syntax"></a>
## Sintaxe

```caddy-d
php_fastcgi [<matcher>] <php-fpm_gateways...> {
	root <path>
	split <substrings...>
	index <filename>|off
	try_files <files...>
	env [<key> <value>]
	resolve_root_symlink
	capture_stderr
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>

	<any other reverse_proxy subdirectives...>
}
```

- **<php-fpm_gateways...>** são os [endereços](/docs/conventions#network-addresses) dos servidores FastCGI. Normalmente, um socket TCP ou um arquivo de unix socket.

- **root** <span id="root"/> define a pasta raiz do site. É recomendável sempre usar a [`diretiva root`](root) em conjunto com `php_fastcgi`, mas sobrescrevê-la pode ser útil quando seu upstream PHP-FPM usa uma raiz diferente da do Caddy (veja [um exemplo](#docker)). O padrão é o valor da [`diretiva root`](root), se ela for usada; caso contrário, o padrão é o diretório de trabalho atual do Caddy.

- **split** <span id="split"/> define as substrings para dividir a URI em duas partes. A primeira substring correspondente será usada para separar o "path info" do caminho. A primeira parte receberá o sufixo da substring correspondente e será assumida como o nome real do recurso (script CGI). A segunda parte será definida como PATH_INFO para o script CGI usar. Padrão: `.php`

- **index** <span id="index"/> especifica o nome de arquivo a tratar como o arquivo de índice do diretório. Isso afeta o matcher de arquivo na [forma expandida](#expanded-form). Padrão: `index.php`. Pode ser definido como `off` para desativar o fallback de rewrite para `index.php` quando um arquivo correspondente não for encontrado.

- **try_files** <span id="try_files"/> especifica uma substituição para o rewrite padrão de try-files. Veja a [`diretiva try_files`](try_files) para detalhes. Padrão: `{path} {path}/index.php index.php`.

- **env** <span id="env"/> define uma variável de ambiente extra com o valor fornecido. Pode ser especificada mais de uma vez para múltiplas variáveis de ambiente. Por padrão, todas as variáveis relevantes de ambiente FastCGI já são definidas (incluindo cabeçalhos HTTP), mas você pode adicionar ou sobrescrever variáveis conforme necessário.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> quando o diretório [`root`](#root) é um link simbólico (symlink), isso habilita resolvê-lo para seu valor real. Às vezes isso é usado como estratégia de implantação, simplesmente trocando o symlink para apontar para a nova versão em outro diretório. Desativado por padrão para evitar chamadas de sistema repetidas.

- **capture_stderr** <span id="capture_stderr"/> habilita capturar e registrar qualquer mensagem enviada pelo servidor fastcgi upstream em `stderr`. O logging é feito no nível `WARN` por padrão. Se a resposta tiver status `4xx` ou `5xx`, o nível `ERROR` será usado em vez disso. Por padrão, `stderr` é ignorado.

- **dial_timeout** <span id="dial_timeout"/> é um [valor de duração](/docs/conventions#durations) que define quanto tempo esperar ao conectar ao socket upstream. Padrão: `3s`.

- **read_timeout** <span id="read_timeout"/> é um [valor de duração](/docs/conventions#durations) que define quanto tempo esperar ao ler do upstream FastCGI. Padrão: sem timeout.

- **write_timeout** <span id="write_timeout"/> é um [valor de duração](/docs/conventions#durations) que define quanto tempo esperar ao enviar para o upstream FastCGI. Padrão: sem timeout.


Como essa diretiva é um wrapper opinativo sobre um reverse proxy, você pode usar quaisquer subdiretivas de [`reverse_proxy`](reverse_proxy#syntax) para personalizá-la.


<a id="expanded-form"></a>
## Forma expandida

A diretiva `php_fastcgi` (sem subdiretivas) é o mesmo que a seguinte configuração. A maioria dos apps PHP modernos funciona bem com esse preset. Se o seu não funcionar, sinta-se à vontade para se basear nisso e personalizar conforme necessário em vez de usar o atalho `php_fastcgi`.

```caddy-d
route {
	# Adiciona barra final para requisições de diretório
	# Esse redirecionamento é desativado automaticamente se "{http.request.uri.path}/index.php"
	# não aparecer na lista try_files
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# Se o arquivo solicitado não existir, tenta arquivos index e assume que index.php sempre existe
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# Faz proxy de arquivos PHP para o responder FastCGI
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```

<a id="explanation"></a>
### Explicação

- A primeira seção trata da canonicalização do caminho da requisição. O objetivo é garantir que requisições que apontam para um diretório no disco realmente tenham a barra final `/` adicionada ao caminho da requisição, de modo que apenas uma URL seja válida para aquele diretório.

  Essa canonicalização acontece somente se a subdiretiva `try_files` contiver `{path}/index.php` (o padrão).

  Isso é feito usando um matcher de requisição que corresponde apenas a requisições que _não_ terminam com uma barra, e que mapeiam para um diretório no disco que contém um arquivo `index.php`; se corresponder, ele executa um redirecionamento HTTP 308 com a barra final adicionada. Então, por exemplo, ele redirecionaria uma requisição com caminho `/foo` para `/foo/` (adicionando `/`, para canonicalizar o caminho do diretório), se `/foo/index.php` existir no disco.

- A próxima seção trata de realizar rewrites de caminho com base em se um arquivo correspondente existe no disco. Isso também tem o efeito colateral de lembrar a parte do caminho após `.php` (se o caminho da requisição tiver `.php` nele). Isso é importante para o Caddy definir corretamente as variáveis de ambiente FastCGI.

  - Primeiro, ele verifica se `{path}` é um arquivo existente no disco. Se for, ele reescreve para esse caminho. Isso essencialmente encerra o restante da lógica e garante que requisições para arquivos que _existem_ no disco não sejam reescritas de outra forma (veja os próximos passos abaixo). Então, por exemplo, se você tiver um arquivo `/js/app.js` no disco, a requisição para esse caminho será mantida igual.

  - Segundo, ele verifica se `{path}/index.php` é um arquivo existente no disco. Se for, ele reescreve para esse caminho. Para requisições para um diretório como `/foo/`, ele então procurará por `/foo//index.php` (que é normalizado para `/foo/index.php`) e reescreverá a requisição para esse caminho se ele existir. Esse comportamento às vezes é útil se você estiver executando outro app PHP em um subdiretório da sua webroot.

  - Por fim, ele sempre reescreve para `index.php` (ele quase sempre existe para apps PHP modernos). Isso permite que seu app PHP trate qualquer requisição para caminhos que _não_ mapeiem para arquivos no disco, usando o script `index.php` como ponto de entrada.

- E, por fim, a última seção é o que de fato faz proxy da requisição para o seu serviço PHP FastCGI (ou PHP-FPM) para executar seu código PHP. O matcher de requisição só corresponderá a requisições que terminem em `.php`, então qualquer arquivo que _não_ seja um script PHP e que _exista_ no disco não será tratado por esta diretiva, e cairá adiante.

A diretiva `php_fastcgi` geralmente não é suficiente sozinha. Ela quase sempre deve ser combinada com a [`diretiva root`](root) para definir a localização dos seus arquivos no disco (para apps PHP modernos, isso pode ser `/var/www/html/public`, onde o diretório `public` contém o `index.php`) e com a [`diretiva file_server`](file_server) para servir seus arquivos estáticos (JS, CSS, imagens etc.) que não forem tratados de outra forma por esta diretiva e que caíram adiante.



<a id="examples"></a>
## Exemplos

Faça proxy de todas as requisições PHP para um responder FastCGI ouvindo em `127.0.0.1:9000`:

```caddy-d
php_fastcgi 127.0.0.1:9000
```

O mesmo, mas apenas para requisições sob `/blog/`:

```caddy-d
php_fastcgi /blog/* localhost:9000
```

Quando usar PHP-FPM ouvindo via um unix socket:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

A [`diretiva root`](root) é quase sempre usada para especificar o diretório que contém os scripts PHP, e a [`diretiva file_server`](file_server) para servir arquivos estáticos:

```caddy
example.com {
	root /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<span id="docker"/> Ao servir vários apps PHP com Caddy, a webroot de cada app deve ser diferente para que o Caddy possa ler e servir os arquivos estáticos separadamente e detectar se arquivos PHP existem.

Se você estiver usando Docker, muitas vezes seus containers PHP-FPM terão os arquivos montados na mesma raiz. Nesse caso, a solução é montar os arquivos no seu container Caddy em diretórios diferentes e então usar a [`subdiretiva root`](#root) para definir a raiz de cada container:

```caddy
app1.example.com {
	root /srv/app1/public
	php_fastcgi app1:9000 {
		root /var/www/html/public
	}
	file_server
}

app2.example.com {
	root /srv/app2/public
	php_fastcgi app2:9000 {
		root /var/www/html/public
	}
	file_server
}
```

Para um site PHP que não usa `index.php` como ponto de entrada, você pode em vez disso cair para emitir um erro `404`. O erro pode ser capturado e tratado com a [`diretiva handle_errors`](handle_errors):

```caddy
example.com {
	php_fastcgi localhost:9000 {
		try_files {path} {path}/index.php =404
	}

	handle_errors {
		respond "{err.status_code} {err.status_text}"
	}
}
```
