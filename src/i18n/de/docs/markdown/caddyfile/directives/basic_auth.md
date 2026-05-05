---
title: basic_auth (Caddyfile directive)
---

# basic_auth

Aktiviert HTTP Basic Authentication, mit der Verzeichnisse und Dateien durch einen Benutzernamen und ein gehashtes Passwort geschützt werden können.

**Beachten Sie, dass Basic Auth über reines HTTP nicht sicher ist.** Entscheiden Sie sorgfältig, was Sie mit HTTP Basic Authentication schützen.

Wenn ein Benutzer eine geschützte Ressource anfordert, fragt der Browser nach Benutzername und Passwort, falls diese noch nicht übermittelt wurden. Wenn die richtigen Zugangsdaten im Authorization-Header vorhanden sind, gewährt der Server Zugriff auf die Ressource. Wenn der Header fehlt oder die Zugangsdaten falsch sind, antwortet der Server mit HTTP 401 Unauthorized.

Caddy-Konfiguration akzeptiert keine Klartextpasswörter; Sie MÜSSEN sie hashen, bevor Sie sie in die Konfiguration eintragen. Der Befehl [`caddy hash-password`](/docs/command-line#caddy-hash-password) kann dabei helfen.

Nach erfolgreicher Authentifizierung ist der Platzhalter `{http.auth.user.id}` verfügbar; er enthält den authentifizierten Benutzernamen.

Vor v2.8.0 hieß diese Direktive `basicauth`, wurde aber zur Konsistenz mit anderen Direktiven umbenannt.


<a id="syntax"></a>
## Syntax

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<username> <hashed_password>
	...
}
```

- **&lt;hash_algorithm&gt;** gibt den Passwort-Hashing-Algorithmus (oder die Key-Derivation-Funktion) an, der für die Hashes in dieser Konfiguration verwendet wird. Verfügbare Optionen umfassen `argon2id`; Standard ist `bcrypt`.

- **&lt;realm&gt;** ist ein eigener Realm-Name.

- **&lt;username&gt;** ist ein Benutzername oder eine Benutzer-ID.

- **&lt;hashed_password&gt;** ist der Passwort-Hash.


<a id="examples"></a>
## Beispiele

Authentifizierung für alle Requests an `example.com` verlangen:

```caddy
example.com {
	basic_auth {
		# Benutzername "Bob", Passwort "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Welcome, {http.auth.user.id}" 200
}
```

Dateien in `/secret/` schützen, sodass nur `Bob` darauf zugreifen kann (und alle anderen Pfade für jeden sichtbar bleiben):

```caddy
example.com {
	root /srv

	basic_auth /secret/* {
		# Benutzername "Bob", Passwort "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

`argon2id`-Beispiel

```caddy
example.com {
	root /srv

	basic_auth /secret/* argon2id {
		# Benutzername "Bob", Passwort "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
