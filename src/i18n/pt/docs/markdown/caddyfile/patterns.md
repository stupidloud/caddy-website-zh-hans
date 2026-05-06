---
title: Padrões comuns do Caddyfile
---

<a id="common-caddyfile-patterns"></a>
# Padrões comuns do Caddyfile

Esta página demonstra algumas configurações completas e mínimas de Caddyfile para casos de uso comuns. Elas podem servir como bons pontos de partida para os seus próprios documentos Caddyfile.

Essas não são soluções prontas para uso; você terá que personalizar seu nome de domínio, portas/sockets, caminhos de diretório etc. Elas têm o objetivo de ilustrar alguns dos padrões de configuração mais comuns.

- [Servidor de arquivos estáticos](#static-file-server)
- [Reverse proxy](#reverse-proxy)
- [PHP](#php)
- [Redirecionar subdomínio `www.`](#redirect-www-subdomain)
- [Barras finais](#trailing-slashes)
- [Certificados curinga](#wildcard-certificates)
- [SPAs (single-page apps)](#single-page-apps-spas)
- [Caddy fazendo proxy para outro Caddy](#caddy-proxying-to-another-caddy)


<a id="static-file-server"></a>
## Servidor de arquivos estáticos

```caddy
example.com {
	root /var/www
	file_server
}
```

Como de costume, a primeira linha é o endereço do site. A [`diretiva root`](/docs/caddyfile/directives/root) especifica o caminho da raiz do site (o `*` significa corresponder a todas as requisições, para desambiguar de um [matcher de caminho](/docs/caddyfile/matchers#path-matchers))&mdash;altere o caminho para o do seu site se ele não for o diretório de trabalho atual. Por fim, habilitamos o [servidor de arquivos estáticos](/docs/caddyfile/directives/file_server).



<a id="reverse-proxy"></a>
## Reverse proxy

Proxy para todas as requisições:

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

Proxy apenas para requisições cujo caminho começa com `/api/` e servir arquivos estáticos para todo o resto:

```caddy
example.com {
	root /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

Isso usa um [matcher de requisição](/docs/caddyfile/matchers#syntax) para corresponder apenas às requisições que começam com `/api/` e enviá-las ao backend. Todas as outras requisições serão servidas a partir da [`raiz`](/docs/caddyfile/directives/root) do site com o [servidor de arquivos estáticos](/docs/caddyfile/directives/file_server). Isso também depende do fato de que `reverse_proxy` está acima de `file_server` na [ordem de diretivas](/docs/caddyfile/directives#directive-order).

Há muitos mais [exemplos de `reverse_proxy` aqui](/docs/caddyfile/directives/reverse_proxy#examples).



<a id="php"></a>
## PHP

### PHP-FPM

Com um serviço PHP FastCGI em execução, algo assim funciona para a maioria dos apps PHP modernos:

```caddy
example.com {
	root /srv/public
	encode
	php_fastcgi localhost:9000
	file_server
}
```

Personalize a raiz do site de acordo; este exemplo assume que o webroot do seu app PHP está dentro de um diretório `public`&mdash;requisições por arquivos existentes no disco serão servidas com [`file_server`](/docs/caddyfile/directives/file_server), e qualquer outra coisa será roteada para `index.php` para tratamento pelo app PHP.

Às vezes você pode usar um unix socket para se conectar ao PHP-FPM:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

A [`diretiva php_fastcgi`](/docs/caddyfile/directives/php_fastcgi) é na verdade apenas um atalho para [várias peças de configuração](/docs/caddyfile/directives/php_fastcgi#expanded-form).


### FrankenPHP

Como alternativa, você pode usar o [FrankenPHP](https://frankenphp.dev/), que é uma distribuição do Caddy que chama PHP diretamente usando CGO (Go to C bindings). Isso pode ser até 4x mais rápido do que com PHP-FPM, e ainda melhor se você puder usar o modo worker.

```caddy
{
    frankenphp
    order php_server before file_server
}

example.com {
	root /srv/public
    encode zstd br gzip
    php_server
}
```


<a id="redirect-www-subdomain"></a>
## Redirecionar subdomínio `www.`

Para **adicionar** o subdomínio `www.` com um redirecionamento HTTP:

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


Para **removê-lo**:

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


Para removê-lo de **vários domínios** de uma vez; isso usa os placeholders `{labels.*}`, que são as partes do hostname, indexadas a partir da direita com base 0 (por exemplo `0`=`com`, `1`=`example-one`, `2`=`www`):

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```



<a id="trailing-slashes"></a>
## Barras finais

Normalmente você não precisará configurar isso manualmente; a [`diretiva file_server`](/docs/caddyfile/directives/file_server) adicionará ou removerá barras finais das requisições automaticamente por meio de redirecionamentos HTTP, dependendo de o recurso solicitado ser um diretório ou um arquivo, respectivamente.

No entanto, se precisar, você ainda pode impor barras finais na sua configuração. Há duas formas de fazer isso: internamente ou externamente.

### Imposição interna

Isso usa a [`diretiva rewrite`](/docs/caddyfile/directives/rewrite). O Caddy reescreve a URI internamente para adicionar ou remover a barra final:

```caddy
example.com {
	rewrite /add     /add/
	rewrite /remove/ /remove
}
```

Usando um rewrite, requisições com e sem a barra final serão tratadas da mesma forma.


### Imposição externa

Isso usa a [`diretiva redir`](/docs/caddyfile/directives/redir). O Caddy pede ao navegador que altere a URI para adicionar ou remover a barra final:

```caddy
example.com {
	redir /add     /add/
	redir /remove/ /remove
}
```

Usando um redirect, o cliente terá que reenviar a requisição, impondo uma única URI aceitável para o recurso.



<a id="wildcard-certificates"></a>
## Certificados curinga

Para a maioria dos emissores, incluindo Let's Encrypt, você precisa habilitar o [desafio ACME DNS](/docs/automatic-https#dns-challenge) para o Caddy automatizar certificados curinga.

Com o desafio DNS habilitado, a partir do Caddy 2.10, o Caddy vai preferir um certificado curinga aplicável que já esteja configurado ou gerenciado antes de gerar um certificado separado para um subdomínio.



Se você precisar servir vários subdomínios com o mesmo certificado curinga, a melhor forma de lidar com isso é com um Caddyfile como este, usando a [`diretiva handle`](/docs/caddyfile/directives/handle) e matchers [`host`](/docs/caddyfile/matchers#host):

```caddy
*.example.com {
	tls {
		dns <provider_name> [<params...>]
	}

	@foo host foo.example.com
	handle @foo {
		respond "Foo!"
	}

	@bar host bar.example.com
	handle @bar {
		respond "Bar!"
	}

	# Fallback para domínios que não forem tratados de outra forma
	handle {
		abort
	}
}
```

Você precisa habilitar o [desafio ACME DNS](/docs/automatic-https#dns-challenge) para o Caddy gerenciar automaticamente certificados curinga.



<a id="single-page-apps-spas"></a>
## SPAs (single-page apps)

Quando uma página web faz seu próprio roteamento, os servidores podem receber muitas requisições para páginas que não existem no lado do servidor, mas que podem ser renderizadas no lado do cliente desde que o arquivo index singular seja servido em seu lugar. Aplicações web arquitetadas assim são conhecidas como SPAs, ou single-page apps.

A ideia principal é fazer o servidor "testar arquivos" para ver se o arquivo solicitado existe no lado do servidor e, se não existir, cair para um arquivo index onde o cliente faz o roteamento (normalmente com JavaScript no lado do cliente).

Uma configuração típica de SPA normalmente parece algo assim:

```caddy
example.com {
	root /srv
	encode
	try_files {path} /index.html
	file_server
}
```

Se sua SPA estiver acoplada a uma API ou a outros endpoints que só existem no lado do servidor, você vai querer usar blocos `handle` para tratá-los de forma exclusiva:

```caddy
example.com {
	encode

	handle /api/* {
		reverse_proxy backend:8000
	}

	handle {
		root /srv
		try_files {path} /index.html
		file_server
	}
}
```

Se o seu `index.html` contiver referências aos seus assets JS/CSS com nomes de arquivo hashados, talvez valha considerar adicionar um cabeçalho `Cache-Control` para instruir os clientes a _não_ fazer cache dele (assim, se os assets mudarem, os navegadores buscarão os novos). Como o rewrite `try_files` é usado para servir seu `index.html` a partir de qualquer caminho que não corresponda a outro arquivo no disco, você pode envolver `try_files` com um `route` para que o handler `header` execute _depois_ do rewrite (normalmente ele executaria antes por causa da [ordem de diretivas](/docs/caddyfile/directives#directive-order)):

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```


<a id="caddy-proxying-to-another-caddy"></a>
## Caddy fazendo proxy para outro Caddy

Se você tiver uma instância do Caddy acessível publicamente (vamos chamá-la de "front") e outra instância do Caddy na sua rede privada (vamos chamá-la de "back") servindo sua aplicação real, você pode usar a [`diretiva reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) para encaminhar as requisições.

Instância front:

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

Instância back:

```caddy
{
	servers {
		trusted_proxies static private_ranges
	}
}

http://foo.example.com {
	reverse_proxy foo-app:8080
}

http://bar.example.com {
	reverse_proxy bar-app:9000
}
```

- Este exemplo serve dois domínios diferentes, fazendo proxy de ambos para a mesma instância back do Caddy, na porta `80`. Sua instância back está servindo os dois domínios de maneiras diferentes, então ela é configurada com dois blocos de site separados.

- No back, [`http://`](/docs/caddyfile/concepts#addresses) é usado para aceitar HTTP na porta `80`. A instância front encerra o TLS, e o tráfego entre front e back ocorre em uma rede privada, então não há necessidade de criptografá-lo novamente.

- Você pode usar uma porta diferente, como `8080`, no back se precisar; basta adicionar `:8080` a cada endereço de site na configuração do back, OU definir a [`opção global http_port`](/docs/caddyfile/options#http_port) como `8080`.

- No back, a [`opção global trusted_proxies`](/docs/caddyfile/options#trusted_proxies) é usada para dizer ao Caddy que a instância front deve ser confiável como proxy. Isso garante que o IP real do cliente seja preservado.

- Indo além, você poderia ter mais de uma instância back entre as quais fazer [load balance](/docs/caddyfile/directives/reverse_proxy#load-balancing). Você poderia configurar mTLS (mutual TLS) usando o [`acme_server`](/docs/caddyfile/directives/acme_server) na instância front, de modo que ela atuasse como a CA para a instância back (útil se o tráfego entre front e back atravessar redes não confiáveis).
