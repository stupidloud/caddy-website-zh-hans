---
title: basic_auth (direttiva del Caddyfile)
---

# basic_auth

Abilita l'autenticazione HTTP Basic, che può essere utilizzata per proteggere directory e file con un nome utente e una password sottoposta a hashing.

**Si noti che la basic auth non è sicura su HTTP in chiaro.** Usate discrezione quando decidete cosa proteggere con l'autenticazione HTTP Basic.

Quando un utente richiede una risorsa protetta, il browser chiederà all'utente un nome utente e una password se non ne ha già forniti. Se le credenziali corrette sono presenti nell'header `Authorization`, il server concederà l'accesso alla risorsa. Se l'header è mancante o le credenziali sono errate, il server risponderà con HTTP 401 Unauthorized.

La configurazione di Caddy non accetta password in chiaro; DOVETE eseguirne l'hashing prima di inserirle nella configurazione. Il comando [`caddy hash-password`](/docs/command-line#caddy-hash-password) può aiutarvi in questo.

Dopo un'autenticazione riuscita, sarà disponibile il placeholder `{http.auth.user.id}`, che contiene il nome utente autenticato.

Prima della v2.8.0, questa direttiva si chiamava `basicauth`, ma è stata rinominata per coerenza con le altre direttive.


## Sintassi

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<username> <hashed_password>
	...
}
```

- **&lt;hash_algorithm&gt;** specifica l'algoritmo di hashing della password (o funzione di derivazione della chiave) utilizzato per gli hash in questa configurazione. Le opzioni disponibili includono `argon2id`; il valore predefinito è `bcrypt`.

- **&lt;realm&gt;** è un nome di realm personalizzato.

- **&lt;username&gt;** è un nome utente o un ID utente.

- **&lt;hashed_password&gt;** è l'hash della password.


## Esempi

Richiede l'autenticazione per tutte le richieste a `example.com`:

```caddy
example.com {
	basic_auth {
		# Utente "Bob", password "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Benvenuto, {http.auth.user.id}" 200
}
```

Protegge i file in `/secret/` in modo che solo `Bob` possa accedervi (e chiunque possa vedere gli altri percorsi):

```caddy
example.com {
	root * /srv

	basic_auth /secret/* {
		# Utente "Bob", password "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

Esempio con `argon2id`

```caddy
example.com {
	root * /srv

	basic_auth /secret/* argon2id {
		# Utente "Bob", password "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
