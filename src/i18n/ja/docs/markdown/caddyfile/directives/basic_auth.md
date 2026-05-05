---
title: basic_auth (Caddyfile directive)
---

# basic_auth

HTTP Basic Authentication を有効にします。ユーザー名とハッシュ化されたパスワードで、ディレクトリやファイルを保護できます。

**plain HTTP 上の basic auth は安全ではないことに注意してください。** HTTP Basic Authentication で何を保護するかは慎重に判断してください。

ユーザーが保護されたリソースをリクエストし、まだ認証情報を送っていない場合、ブラウザはユーザー名とパスワードの入力を求めます。Authorization header に正しい認証情報が含まれていれば、サーバーはそのリソースへのアクセスを許可します。header がない、または認証情報が誤っている場合、サーバーは HTTP 401 Unauthorized で応答します。

Caddy 設定では平文パスワードを受け付けません。設定に入れる前に必ずハッシュ化する必要があります。[`caddy hash-password`](/docs/command-line#caddy-hash-password) コマンドが役立ちます。

認証に成功すると、認証済みユーザー名を含む `{http.auth.user.id}` placeholder が利用可能になります。

v2.8.0 より前は、この directive は `basicauth` という名前でしたが、他の directive との一貫性のために改名されました。


<a id="syntax"></a>
## 構文

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<username> <hashed_password>
	...
}
```

- **&lt;hash_algorithm&gt;** は、この設定内のハッシュに使うパスワードハッシュアルゴリズム（または鍵導出関数）を指定します。利用可能な選択肢には `argon2id` があり、デフォルトは `bcrypt` です。

- **&lt;realm&gt;** はカスタム realm 名です。

- **&lt;username&gt;** はユーザー名またはユーザー ID です。

- **&lt;hashed_password&gt;** はパスワードハッシュです。


<a id="examples"></a>
## 例

`example.com` へのすべてのリクエストに認証を要求します。

```caddy
example.com {
	basic_auth {
		# ユーザー名 "Bob"、パスワード "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Welcome, {http.auth.user.id}" 200
}
```

`/secret/` 内のファイルを保護し、`Bob` だけがアクセスできるようにします（他のパスは誰でも閲覧できます）。

```caddy
example.com {
	root /srv

	basic_auth /secret/* {
		# ユーザー名 "Bob"、パスワード "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

`argon2id` の例

```caddy
example.com {
	root /srv

	basic_auth /secret/* argon2id {
		# ユーザー名 "Bob"、パスワード "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
