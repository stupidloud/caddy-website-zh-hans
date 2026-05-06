---
title: forward_auth (direttiva del Caddyfile)
---

<script>
ready(function() {
	// Corregge > nei blocchi di codice
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Salta se termina con >
			if (item.textContent.trim().endsWith('>')) return;
			// Sostituisce > con <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// Corregge la sottodirettiva uri, viene analizzata come argomento del matcher a causa della direttiva "uri"
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

Una direttiva opinionata che effettua il proxy di un clone della richiesta verso un gateway di autenticazione, il quale può decidere se la gestione debba continuare o se la richiesta debba essere inviata a una pagina di login.

- [Sintassi](#syntax)
- [Forma estesa](#expanded-form)
- [Esempi](#examples)
  - [Authelia](#authelia)
  - [Tailscale](#tailscale)

Il [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) di Caddy è in grado di eseguire "richieste di pre-controllo" verso un servizio esterno, ma questa direttiva è studiata specificamente per il caso d'uso dell'autenticazione. Questa direttiva è in realtà solo un modo comodo per utilizzare una configurazione più lunga e comune (descritta di seguito).

Questa direttiva effettua una richiesta `GET` verso l'upstream configurato con l'uri riscritto:
- Se l'upstream risponde con un codice di stato `2xx`, l'accesso viene concesso e i campi header specificati in `copy_headers` vengono copiati nella richiesta originale, e la gestione prosegue.
- Altrimenti, se l'upstream risponde con qualsiasi altro codice di stato, la risposta dell'upstream viene copiata verso il client. Questa risposta tipicamente comporterà un reindirizzamento alla pagina di login del gateway di autenticazione.

Se questo comportamento non è esattamente quello desiderato, potete prendere la [forma estesa](#expanded-form) sottostante come base e personalizzatela secondo le vostre necessità.

Tutte le sottodirettive di [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) sono supportate e passate all'handler `reverse_proxy` sottostante.


## Sintassi

<a id="syntax"></a>
```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <to>
	copy_headers <fields...> {
		<fields...>
	}
}
```

- **&lt;upstreams...&gt;** è un elenco di upstream (backend) verso cui inviare le richieste di autenticazione.

- **uri** è l'URI (percorso e query) da impostare sulla richiesta inviata all'upstream. Solitamente si tratta dell'endpoint di verifica del gateway di autenticazione.

- **copy_headers** è un elenco di campi header HTTP da copiare dalla risposta alla richiesta originale, quando la richiesta ha un codice di stato di successo.

  Il campo può essere rinominato usando `>` seguito dal nuovo nome, ad esempio `Prima>Dopo`.

  Può essere usato un blocco per elencare tutti i campi, uno per riga, se preferito per leggibilità.

Poiché questa direttiva è un wrapper opinionato attorno a un reverse proxy, potete usare qualsiasi sottodirettiva di [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax) per personalizzarla.


## Forma estesa

<a id="expanded-form"></a>
La direttiva `forward_auth` è equivalente alla seguente configurazione. I gateway di autenticazione come [Authelia](https://www.authelia.com/) funzionano bene con questo preset. Se il vostro non lo fa, sentitevi liberi di prendere spunto da qui e personalizzarlo secondo necessità anziché usare la scorciatoia `forward_auth`.

```caddy-d
reverse_proxy <upstreams...> {
	# Sempre GET, in modo che il corpo della richiesta
	# in entrata non venga consumato
	method GET

	# Cambia l'URI verso l'endpoint di verifica
	# del gateway di autenticazione
	rewrite <to>

	# Inoltra il metodo e l'URI originali,
	# dato che vengono riscritti sopra; questo
	# si aggiunge agli altri header X-Forwarded-*
	# già impostati da reverse_proxy
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# In caso di risposta positiva, copia gli header di risposta
	@good status 2xx
	handle_response @good {
		# ad esempio, per ogni campo copy_headers...
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


## Esempi

<a id="examples"></a>


### Authelia

<a id="authelia"></a>
Delegare l'autenticazione ad [Authelia](https://www.authelia.com/), prima di servire la vostra app tramite un reverse proxy:

```caddy
# Serve il gateway di autenticazione stesso
auth.example.com {
	reverse_proxy authelia:9091
}

# Serve la vostra app
app1.example.com {
	forward_auth authelia:9091 {
		uri /api/authz/forward-auth
		copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
	}

	reverse_proxy app1:8080
}
```

Per maggiori informazioni, consultate la [documentazione di Authelia](https://www.authelia.com/integration/proxies/caddy/) per l'integrazione con Caddy.


### Tailscale

<a id="tailscale"></a>
Delegare l'autenticazione a [Tailscale](https://tailscale.com/) (attualmente chiamato [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/), ma funziona ancora con Caddy), e usare la sintassi alternativa per `copy_headers` per *rinominare* gli header copiati (notate il simbolo `>` in ogni header):

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
