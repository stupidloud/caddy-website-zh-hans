---
title: forward_auth (директива Caddyfile)
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.innerText.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// Fix uri subdirective, gets parsed as matcher arg because of "uri" directive
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

Опинионированная директива, которая проксирует клон запроса в authentication gateway, который может решить, должно ли выполнение продолжаться или нужно отправить пользователя на страницу входа.

- [Синтаксис](#syntax)
- [Развернутая форма](#expanded-form)
- [Примеры](#examples)
  - [Authelia](#authelia)
  - [Tailscale](#tailscale)

[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) в Caddy способен выполнять "pre-check requests" к внешнему сервису, но эта директива специально адаптирована под сценарий аутентификации. Фактически это просто удобный способ использовать более длинную и распространенную конфигурацию (ниже).

Эта директива выполняет `GET` request к настроенному upstream с переписанным `uri`:
- Если upstream отвечает status code `2xx`, доступ разрешается, header fields из `copy_headers` копируются в исходный запрос, и обработка продолжается.
- Иначе, если upstream отвечает любым другим status code, ответ upstream копируется обратно клиенту. Обычно такой ответ должен включать redirect на страницу входа authentication gateway.

Если это поведение не совсем то, что нужно, можно взять [развернутую форму](#expanded-form) ниже за основу и настроить ее под свои требования.

Поддерживаются все поддирективы [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy), которые передаются нижележащему handler `reverse_proxy`.


<a id="syntax"></a>
## Синтаксис

```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <to>
	copy_headers <fields...> {
		<fields...>
	}
}
```

- **&lt;upstreams...&gt;** — список upstreams (backends), куда нужно отправлять auth requests.

- **uri** — URI (path и query), который нужно установить в запросе, отправляемом upstream. Обычно это verification endpoint authentication gateway.

- **copy_headers** — список HTTP header fields, которые нужно копировать из ответа в исходный запрос, когда запрос получил успешный status code.

  Поле можно переименовать, используя `>` и затем новое имя, например `Before>After`.

  Для читаемости можно использовать блок, чтобы перечислить все поля по одному в строке.

Поскольку эта директива является опинионированной оберткой над reverse proxy, можно использовать любые поддирективы [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax), чтобы настроить ее.


<a id="expanded-form"></a>
## Развернутая форма

Директива `forward_auth` эквивалентна следующей конфигурации. Auth gateways вроде [Authelia](https://www.authelia.com/) хорошо работают с этим preset. Если ваш gateway работает иначе, можно заимствовать эту конфигурацию и настроить ее как нужно вместо использования сокращения `forward_auth`.

```caddy-d
reverse_proxy <upstreams...> {
	# Всегда GET, чтобы тело входящего
	# запроса не было прочитано
	method GET

	# Изменить URI на verification endpoint
	# auth gateway
	rewrite <to>

	# Передать исходный method и URI,
	# поскольку выше они переписываются; это
	# дополняет другие headers X-Forwarded-*,
	# уже установленные reverse_proxy
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# При успешном ответе скопировать response headers
	@good status 2xx
	handle_response @good {
		# например, для каждого поля copy_headers...
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


<a id="examples"></a>
## Примеры


### Authelia

Делегирование аутентификации [Authelia](https://www.authelia.com/) перед обслуживанием приложения через reverse proxy:

```caddy
# Serve the authentication gateway itself
auth.example.com {
	reverse_proxy authelia:9091
}

# Serve your app
app1.example.com {
	forward_auth authelia:9091 {
		uri /api/authz/forward-auth
		copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
	}

	reverse_proxy app1:8080
}
```

Подробнее см. [документацию Authelia](https://www.authelia.com/integration/proxies/caddy/) по интеграции с Caddy.


### Tailscale

Делегирование аутентификации [Tailscale](https://tailscale.com/) (сейчас называется [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/), но по-прежнему работает с Caddy) и использование альтернативного синтаксиса `copy_headers` для *переименования* копируемых headers (обратите внимание на `>` в каждом header):

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
