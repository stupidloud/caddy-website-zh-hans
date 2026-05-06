---
title: basic_auth (директива Caddyfile)
---

# basic_auth

Включает HTTP Basic Authentication, которую можно использовать для защиты каталогов и файлов с помощью имени пользователя и хешированного пароля.

**Обратите внимание, что basic auth небезопасна поверх обычного HTTP.** Обдуманно выбирайте, что защищать с помощью HTTP Basic Authentication.

Когда пользователь запрашивает защищенный ресурс, браузер запросит у него имя пользователя и пароль, если они еще не были предоставлены. Если в header Authorization присутствуют правильные учетные данные, сервер предоставит доступ к ресурсу. Если header отсутствует или учетные данные неверны, сервер ответит HTTP 401 Unauthorized.

Конфигурация Caddy не принимает пароли в открытом виде; вы ДОЛЖНЫ хешировать их перед добавлением в конфигурацию. В этом может помочь команда [`caddy hash-password`](/docs/command-line#caddy-hash-password).

После успешной аутентификации будет доступен placeholder `{http.auth.user.id}`, содержащий имя аутентифицированного пользователя.

До v2.8.0 эта директива называлась `basicauth`, но была переименована для согласованности с другими директивами.


<a id="syntax"></a>
## Синтаксис

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<username> <hashed_password>
	...
}
```

- **&lt;hash_algorithm&gt;** задает алгоритм хеширования пароля (или key derivation function), используемый для хешей в этой конфигурации. Доступные варианты включают `argon2id`; значение по умолчанию — `bcrypt`.

- **&lt;realm&gt;** — пользовательское имя realm.

- **&lt;username&gt;** — имя пользователя или user ID.

- **&lt;hashed_password&gt;** — хеш пароля.


<a id="examples"></a>
## Примеры

Требовать аутентификацию для всех запросов к `example.com`:

```caddy
example.com {
	basic_auth {
		# Username "Bob", password "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Welcome, {http.auth.user.id}" 200
}
```

Защитить файлы в `/secret/`, чтобы доступ к ним был только у `Bob` (а остальные пути могли видеть все):

```caddy
example.com {
	root /srv

	basic_auth /secret/* {
		# Username "Bob", password "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

Пример `argon2id`

```caddy
example.com {
	root /srv

	basic_auth /secret/* argon2id {
		# Username "Bob", password "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
