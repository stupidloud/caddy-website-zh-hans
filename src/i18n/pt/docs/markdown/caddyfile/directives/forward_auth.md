---
title: forward_auth (diretiva do Caddyfile)
---

<script>
ready(function() {
	// Corrige > em blocos de código
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Pula se terminar com >
			if (item.innerText.trim().endsWith('>')) return;
			// Substitui > por <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// Corrige a subdiretiva uri, que é parseada como argumento de matcher por causa da diretiva "uri"
	$$_('.k').forEach(item => {
		if (item.innerText.includes('uri') && item.nextElementSibling && item.nextElementSibling.classList.contains('nd')) {
			const next = item.nextElementSibling;
			next.classList.remove('nd');
			next.classList.add('s');
			next.textContent = next.textContent;
		}
	});
});
</script>

# forward_auth

Uma diretiva opinativa que faz proxy de uma cópia da requisição para um gateway de autenticação, que pode decidir se o processamento deve continuar ou se a requisição precisa ser enviada para uma página de login.

- [Sintaxe](#syntax)
- [Forma expandida](#expanded-form)
- [Exemplos](#examples)
  - [Authelia](#authelia)
  - [Tailscale](#tailscale)

O [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) do Caddy é capaz de fazer "pre-check requests" para um serviço externo, mas esta diretiva é feita especificamente para o caso de autenticação. Na prática, ela é apenas uma forma conveniente de usar uma configuração mais longa e comum (abaixo).

Esta diretiva faz uma requisição `GET` para o upstream configurado com a `uri` reescrita:
- Se o upstream responder com um status `2xx`, o acesso é concedido, os campos de cabeçalho em `copy_headers` são copiados para a requisição original e o processamento continua.
- Caso contrário, se o upstream responder com qualquer outro código de status, a resposta do upstream é copiada de volta para o cliente. Essa resposta normalmente envolve um redirecionamento para a página de login do gateway de autenticação.

Se esse comportamento não for exatamente o que você quer, você pode usar a [forma expandida](#expanded-form) abaixo como base e personalizá-la conforme necessário.

Todas as subdiretivas de [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) são suportadas e repassadas para o handler `reverse_proxy` subjacente.


<a id="syntax"></a>
## Sintaxe

```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <to>
	copy_headers <fields...> {
		<fields...>
	}
}
```

- **&lt;upstreams...&gt;** é uma lista de upstreams (backends) para os quais as requisições de autenticação serão enviadas.

- **uri** é a URI (path e query) a definir na requisição enviada ao upstream. Normalmente, essa será o endpoint de verificação do gateway de autenticação.

- **copy_headers** é uma lista de campos de cabeçalho HTTP a copiar da resposta para a requisição original, quando a requisição tiver um status de sucesso.

  O campo pode ser renomeado usando `>` seguido do novo nome; por exemplo, `Before>After`.

  Um bloco pode ser usado para listar todos os campos, um por linha, se você preferir por legibilidade.

Como essa diretiva é um wrapper opinativo sobre um reverse proxy, você pode usar quaisquer subdiretivas de [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax) para personalizá-la.


<a id="expanded-form"></a>
## Forma expandida

A diretiva `forward_auth` é o mesmo que a seguinte configuração. Gateways de autenticação como [Authelia](https://www.authelia.com/) funcionam bem com esse preset. Se o seu não funcionar, sinta-se à vontade para se basear nisso e personalizar conforme necessário, em vez de usar o atalho `forward_auth`.

```caddy-d
reverse_proxy <upstreams...> {
	# Sempre usa GET, para que o corpo da
	# requisição de entrada não seja consumido
	method GET

	# Altera a URI para o endpoint de
	# verificação do gateway de autenticação
	rewrite <to>

	# Encaminha o método e a URI originais,
	# já que eles são reescritos acima; isso
	# é além dos outros cabeçalhos X-Forwarded-*
	# já definidos por reverse_proxy
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# Em uma resposta bem-sucedida, copia os cabeçalhos da resposta
	@good status 2xx
	handle_response @good {
		# por exemplo, para cada campo de copy_headers...
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


<a id="examples"></a>
## Exemplos


### Authelia

Delegando autenticação ao [Authelia](https://www.authelia.com/), antes de servir seu app via reverse proxy:

```caddy
# Serve o próprio gateway de autenticação
auth.example.com {
	reverse_proxy authelia:9091
}

# Serve sua aplicação
app1.example.com {
	forward_auth authelia:9091 {
		uri /api/authz/forward-auth
		copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
	}

	reverse_proxy app1:8080
}
```

Para mais informações, veja a [documentação do Authelia](https://www.authelia.com/integration/proxies/caddy/) sobre integração com o Caddy.


### Tailscale

Delegando autenticação ao [Tailscale](https://tailscale.com/) (atualmente chamado [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/), mas ainda funciona com o Caddy), e usando a sintaxe alternativa para `copy_headers` para *renomear* os cabeçalhos copiados (observe o `>` em cada cabeçalho):

```caddy-d
forward_auth unix//run/tailscale.nginx-auth.sock {
	uri /auth
	header_up Remote-Addr {remote_host}
	header_up Remote-Port {remote_port}
	header_up Original-URI {uri}
	copy_headers {
		Tailscale-User>X-Webauth-User
		Tailscale-Name>X-Webauth-Name
		Tailscale-Login>X-Webauth-Login
		Tailscale-Tailnet>X-Webauth-Tailnet
		Tailscale-Profile-Picture>X-Webauth-Profile-Picture
	}
}
```
