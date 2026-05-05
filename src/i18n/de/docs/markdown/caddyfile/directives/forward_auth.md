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

Eine meinungsstarke Direktive, die eine Kopie des Requests an ein Authentifizierungs-Gateway proxyt. Dieses kann entscheiden, ob die Verarbeitung fortgesetzt werden soll oder ob der Client zu einer Login-Seite geschickt werden muss.

- [Syntax](#syntax)
- [Erweiterte Form](#expanded-form)
- [Beispiele](#examples)
  - [Authelia](#authelia)
  - [Tailscale](#tailscale)

Caddys [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) kann "Pre-check Requests" an einen externen Dienst ausführen, aber diese Direktive ist speziell auf den Authentifizierungsfall zugeschnitten. Tatsächlich ist diese Direktive nur eine bequeme Kurzform für eine längere, häufige Konfiguration (unten).

Diese Direktive sendet einen `GET`-Request an den konfigurierten Upstream, wobei `uri` umgeschrieben wird:
- Wenn der Upstream mit einem `2xx`-Statuscode antwortet, wird Zugriff gewährt, die Header-Felder in `copy_headers` werden in den ursprünglichen Request kopiert, und die Verarbeitung wird fortgesetzt.
- Andernfalls, wenn der Upstream mit einem anderen Statuscode antwortet, wird die Response des Upstreams an den Client zurückkopiert. Diese Response sollte typischerweise einen Redirect zur Login-Seite des Authentifizierungs-Gateways enthalten.

Wenn dieses Verhalten nicht genau das ist, was Sie möchten, können Sie die untenstehende [erweiterte Form](#expanded-form) als Grundlage nehmen und an Ihre Bedürfnisse anpassen.

Alle Subdirektiven von [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) werden unterstützt und an den zugrunde liegenden `reverse_proxy`-Handler weitergereicht.


<a id="syntax"></a>
## Syntax

```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <to>
	copy_headers <fields...> {
		<fields...>
	}
}
```

- **&lt;upstreams...&gt;** ist eine Liste von Upstreams (Backends), an die Auth-Requests gesendet werden.

- **uri** ist die URI (Pfad und Query), die auf dem an den Upstream gesendeten Request gesetzt wird. Dies ist normalerweise der Verifizierungs-Endpunkt des Authentifizierungs-Gateways.

- **copy_headers** ist eine Liste von HTTP-Header-Feldern, die bei erfolgreichem Statuscode vom Response in den ursprünglichen Request kopiert werden.

  Das Feld kann mit `>` gefolgt vom neuen Namen umbenannt werden, zum Beispiel `Before>After`.

  Für bessere Lesbarkeit kann ein Block verwendet werden, um alle Felder zeilenweise aufzulisten.

Da diese Direktive ein meinungsstarker Wrapper über einem Reverse Proxy ist, können Sie jede Subdirektive von [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax) verwenden, um sie anzupassen.


<a id="expanded-form"></a>
## Erweiterte Form

Die Direktive `forward_auth` entspricht der folgenden Konfiguration. Auth-Gateways wie [Authelia](https://www.authelia.com/) funktionieren gut mit diesem Preset. Falls Ihres das nicht tut, können Sie diese Form als Ausgangspunkt nehmen und nach Bedarf anpassen, statt die Kurzform `forward_auth` zu verwenden.

```caddy-d
reverse_proxy <upstreams...> {
	# Immer GET, damit der Body des
	# eingehenden Requests nicht verbraucht wird
	method GET

	# Die URI zum Verifizierungs-Endpunkt
	# des Auth-Gateways ändern
	rewrite <to>

	# Ursprüngliche Methode und URI weiterleiten,
	# da sie oben umgeschrieben werden; zusätzlich
	# zu anderen X-Forwarded-*-Headern, die bereits
	# von reverse_proxy gesetzt werden
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# Bei erfolgreicher Response Header kopieren
	@good status 2xx
	handle_response @good {
		# zum Beispiel für jedes copy_headers-Feld ...
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


<a id="examples"></a>
## Beispiele


### Authelia

Authentifizierung an [Authelia](https://www.authelia.com/) delegieren, bevor Ihre App über einen Reverse Proxy ausgeliefert wird:

```caddy
# Das Authentifizierungs-Gateway selbst ausliefern
auth.example.com {
	reverse_proxy authelia:9091
}

# Ihre App ausliefern
app1.example.com {
	forward_auth authelia:9091 {
		uri /api/authz/forward-auth
		copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
	}

	reverse_proxy app1:8080
}
```

Weitere Informationen finden Sie in [Authelias Dokumentation](https://www.authelia.com/integration/proxies/caddy/) zur Integration mit Caddy.


### Tailscale

Authentifizierung an [Tailscale](https://tailscale.com/) delegieren (derzeit [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/) genannt, funktioniert aber weiterhin mit Caddy) und die alternative Syntax für `copy_headers` verwenden, um die kopierten Header *umzubenennen* (beachten Sie das `>` in jedem Header):

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
