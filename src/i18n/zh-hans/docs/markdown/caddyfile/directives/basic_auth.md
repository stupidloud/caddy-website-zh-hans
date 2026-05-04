---
title: "basic_auth（Caddyfile 指令）"
---

# 基本认证

启用 HTTP 基本身份验证，可用于通过用户名和哈希密码来保护目录和文件。

**请注意，基本认证在普通 HTTP 协议下并不安全。** 在决定使用 HTTP 基本认证保护哪些内容时，请谨慎行事。

当用户请求受保护的资源时，如果尚未提供用户名和密码，浏览器会提示用户输入。如果“Authorization”头中包含正确的凭据，服务器将授予对该资源的访问权限。如果该头缺失或凭据不正确，服务器将返回 HTTP 401 未授权状态码。

Caddy 配置不接受明文密码；您必须在将其写入配置前对其进行哈希处理。[`caddy hash-password`](/docs/command-line#caddy-hash-password) 命令可协助完成此操作。

身份验证成功后， `{http.auth.user.id}` 占位符将可用，其中包含已验证的用户名。

在 v2.8.0 之前，该指令名为 `basicauth`，但为了与其他指令保持一致，现已更名。


## 语法

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<username> <hashed_password>
	...
}
```

- **&lt;hash_algorithm&gt;** 指定了本配置中用于生成哈希值的密码哈希算法（或密钥派生函数）。可用选项包括 `argon2id`，默认值为 `bcrypt`.

- **&lt;realm&gt;** 是一个自定义的服名。

- **&lt;username&gt;** 是用户名或用户 ID。

- **&lt;hashed_password&gt;** 是密码哈希值。


## 示例

要求对所有发往 `example.com`:

```caddy
example.com {
	basic_auth {
		# 用户名 "Bob"，密码 "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Welcome, {http.auth.user.id}" 200
}
```

保护文件 `/secret/` ，因此只有 `Bob` 才能访问它们（其他人可以查看其他路径）：

```caddy
example.com {
	root /srv

	basic_auth /secret/* {
		# 用户名 "Bob"，密码 "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

`argon2id` 示例

```caddy
example.com {
	root /srv

	basic_auth /secret/* argon2id {
		# 用户名 "Bob"，密码 "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
