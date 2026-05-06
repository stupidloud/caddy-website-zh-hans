---
title: basic_auth (Caddyfile 指令)
---

<a id="basic-auth"></a>
# basic_auth

啟用 HTTP 基本認證（Basic Authentication），可用於透過使用者名稱和雜湊處理過的密碼來保護目錄和檔案。

**請注意，基本認證在明文 HTTP 上並不安全。** 在決定要使用 HTTP 基本認證保護哪些內容時，請謹慎考量。

當使用者請求受保護的資源時，如果尚未提供使用者名稱和密碼，瀏覽器會提示使用者輸入。如果 Authorization 標頭中包含正確的憑據，伺服器將授權存取該資源。如果標頭缺失或憑據不正確，伺服器將回應 HTTP 401 Unauthorized。

Caddy 設定不接受明文密碼；你 **必須** 在將密碼放入設定之前對其進行雜湊處理。[`caddy hash-password`](/docs/command-line#caddy-hash-password) 命令可以提供幫助。

驗證成功後，`{http.auth.user.id}` placeholder 將可用，其中包含已驗證的使用者名稱。

在 v2.8.0 之前，此指令名為 `basicauth`，但為了與其他指令保持一致而重新命名。


<a id="syntax"></a>
## 語法

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<username> <hashed_password>
	...
}
```

- **&lt;hash_algorithm&gt;** 指定此設定中雜湊值所使用的密碼雜湊演算法（或金鑰衍生函數）。可用的選項包括 `argon2id`，預設值為 `bcrypt`。

- **&lt;realm&gt;** 是自定義的領域（realm）名稱。

- **&lt;username&gt;** 是使用者名稱或使用者 ID。

- **&lt;hashed_password&gt;** 是密碼雜湊值。


<a id="examples"></a>
## 範例

對 `example.com` 的所有請求要求驗證：

```caddy
example.com {
	basic_auth {
		# 使用者名稱 "Bob"，密碼 "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Welcome, {http.auth.user.id}" 200
}
```

保護 `/secret/` 中的檔案，以便只有 `Bob` 可以存取（其他人可以看到其他路徑）：

```caddy
example.com {
	root /srv

	basic_auth /secret/* {
		# 使用者名稱 "Bob"，密碼 "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

`argon2id` 範例：

```caddy
example.com {
	root /srv

	basic_auth /secret/* argon2id {
		# 使用者名稱 "Bob"，密碼 "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
