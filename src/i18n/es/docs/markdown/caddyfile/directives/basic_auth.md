---
title: basic_auth (directiva de Caddyfile)
---

# basic_auth

Habilita la autenticación HTTP Basic, que se puede usar para proteger directorios y archivos con un nombre de usuario y una contraseña hash.

**Ten en cuenta que la autenticación básica no es segura sobre HTTP en texto plano.** Usa tu criterio al decidir qué proteger con HTTP Basic Authentication.

Cuando un usuario solicita un recurso protegido, el navegador pedirá nombre de usuario y contraseña si aún no los ha enviado. Si las credenciales correctas están presentes en la cabecera Authorization, el servidor concederá acceso al recurso. Si falta la cabecera o las credenciales son incorrectas, el servidor responderá con HTTP 401 Unauthorized.

La configuración de Caddy no acepta contraseñas en texto plano; DEBES hashearlas antes de ponerlas en la configuración. El comando [`caddy hash-password`](/docs/command-line#caddy-hash-password) puede ayudarte con eso.

Tras una autenticación exitosa, estará disponible el placeholder `{http.auth.user.id}`, que contiene el nombre de usuario autenticado.

Antes de v2.8.0, esta directiva se llamaba `basicauth`, pero se renombró por coherencia con otras directivas.


## Sintaxis

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<username> <hashed_password>
	...
}
```

- **&lt;hash_algorithm&gt;** especifica el algoritmo de hash de contraseñas (o función de derivación de claves) usado para los hashes en esta configuración. Las opciones disponibles incluyen `argon2id`, y el valor por defecto es `bcrypt`.

- **&lt;realm&gt;** es un nombre de realm personalizado.

- **&lt;username&gt;** es un nombre de usuario o ID de usuario.

- **&lt;hashed_password&gt;** es el hash de contraseña.


## Ejemplos

Requerir autenticación para todas las solicitudes a `example.com`:

```caddy
example.com {
	basic_auth {
		# Usuario "Bob", contraseña "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Welcome, {http.auth.user.id}" 200
}
```

Proteger archivos en `/secret/` para que solo `Bob` pueda acceder (y cualquier persona pueda ver otros paths):

```caddy
example.com {
	root /srv

	basic_auth /secret/* {
		# Usuario "Bob", contraseña "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

Ejemplo de `argon2id`

```caddy
example.com {
	root /srv

	basic_auth /secret/* argon2id {
		# Usuario "Bob", contraseña "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
