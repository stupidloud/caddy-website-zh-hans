---
title: forward_auth (Caddyfile directive)
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
});
</script>

# forward_auth

Una directiva con comportamientos predefinidos que hace un clon de la solicitud y lo envía a una puerta de autenticación, la cual decide si la gestión debe continuar o si hay que redirigir a una página de inicio de sesión.

- [Syntax](#syntax)
- [Expanded Form](#expanded-form)
- [Examples](#examples)
  - [Authelia](#authelia)
  - [Tailscale](#tailscale)

Caddy [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) puede realizar "solicitudes previas" a un servicio externo, pero esta directiva está diseñada específicamente para casos de autenticación. En realidad, esta directiva es solo una forma conveniente de usar una configuración más larga y común (más abajo).

Esta directiva realiza una solicitud `GET` al upstream configurado con el `uri` reescrito:
- Si el upstream responde con un código de estado `2xx`, se concede el acceso, se copian los campos de encabezado en `copy_headers` a la solicitud original y continúa el manejo.
- De lo contrario, si el upstream responde con cualquier otro código, se copia de vuelta al cliente la respuesta del upstream. Normalmente esta respuesta incluye una redirección hacia la página de inicio de sesión de la puerta de autenticación.

Si este comportamiento no es exactamente lo que necesitas, puedes tomar la [forma expandida](#expanded-form) más abajo como base y personalizarla.

Se admiten y se pasan al handler `reverse_proxy` subyacente todos los subdirectorios de [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).


## Syntax

```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <to>
	copy_headers <fields...> {
		<fields...>
	}
}
```

- **&lt;upstreams...&gt;** es una lista de upstreams (backends) a los que enviar las solicitudes de autenticación.

- **uri** es el URI (ruta y query) que se asigna a la solicitud enviada al upstream. Normalmente será el endpoint de verificación de la pasarela de autenticación.

- **copy_headers** es la lista de campos de encabezado HTTP que se copiarán desde la respuesta a la solicitud original cuando ésta tenga código de éxito.

  El campo puede renombrarse usando `>` seguido del nuevo nombre, por ejemplo `Antes>Después`.

  Si quieres más legibilidad, también puedes usar un bloque para listar todos los campos, uno por línea.

Como esta directiva es una envoltura de conveniencia sobre un proxy inverso, puedes usar cualquiera de los subdirectores de [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax) para personalizarla.


## Expanded form

La directiva `forward_auth` es equivalente a la configuración siguiente. Pasarelas de autenticación como [Authelia](https://www.authelia.com/) funcionan bien con este preset. Si la tuya no encaja, puedes tomar esta configuración como base y adaptarla en lugar de usar el atajo `forward_auth`.

```caddy-d
reverse_proxy <upstreams...> {
	# Always GET, so that the incoming
	# request's body is not consumed
	method GET

	# Change the URI to the auth gateway's
	# verification endpoint
	rewrite <to>

	# Forward the original method and URI,
	# since they get rewritten above; this
	# is in addition to other X-Forwarded-*
	# headers already set by reverse_proxy
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# On a successful response, copy response headers
	@good status 2xx
	handle_response @good {
		# for example, for each copy_headers field...
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


## Examples


### Authelia

Delegar la autenticación en [Authelia](https://www.authelia.com/), antes de servir tu app mediante un reverse proxy:

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

Para más información, consulta la [documentación de Authelia](https://www.authelia.com/integration/proxies/caddy/) para la integración con Caddy.


### Tailscale

Delegar la autenticación en [Tailscale](https://tailscale.com/) (actualmente llamado [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/), pero sigue funcionando con Caddy), y usar la sintaxis alternativa de `copy_headers` para *renombrar* los encabezados copiados (observa el `>` en cada encabezado):

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
