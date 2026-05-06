---
title: basic_auth (Caddyfile 지시어)
---

# basic_auth

HTTP 기본 인증(Basic Authentication)을 활성화하여 사용자 이름과 해시된 비밀번호로 디렉토리 및 파일을 보호할 수 있습니다.

**기본 인증은 암호화되지 않은 HTTP 환경에서 안전하지 않다는 점에 유의하세요.** HTTP 기본 인증으로 무엇을 보호할지 결정할 때 신중을 기해야 합니다.

사용자가 보호된 리소스를 요청할 때, 아직 자격 증명을 제공하지 않았다면 브라우저가 사용자 이름과 비밀번호를 입력하라는 메시지를 표시합니다. Authorization 헤더에 올바른 자격 증명이 포함되어 있으면 서버는 리소스에 대한 액세스를 허용합니다. 헤더가 없거나 자격 증명이 올바르지 않으면 서버는 HTTP 401 Unauthorized로 응답합니다.

Caddy 설정은 평문 비밀번호를 허용하지 않습니다. 설정에 넣기 전에 반드시 비밀번호를 해싱해야 합니다. [`caddy hash-password`](/docs/command-line#caddy-hash-password) 명령어가 이를 도와줄 수 있습니다.

인증에 성공하면 인증된 사용자 이름을 포함하는 `{http.auth.user.id}` 플레이스홀더를 사용할 수 있습니다.

v2.8.0 이전에는 이 지시어의 이름이 `basicauth`였으나, 다른 지시어들과의 일관성을 위해 이름이 변경되었습니다.


## 구문

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<username> <hashed_password>
	...
}
```

- **&lt;hash_algorithm&gt;** 은 이 설정의 해시에 사용된 비밀번호 해싱 알고리즘(또는 키 유도 함수)을 지정합니다. 사용 가능한 옵션에는 `argon2id`가 포함되며, 기본값은 `bcrypt`입니다.

- **&lt;realm&gt;** 은 사용자 정의 영역(realm) 이름입니다.

- **&lt;username&gt;** 은 사용자 이름 또는 사용자 ID입니다.

- **&lt;hashed_password&gt;** 는 해시된 비밀번호입니다.


## 예시

`example.com`에 대한 모든 요청에 인증을 요구합니다:

```caddy
example.com {
	basic_auth {
		# 사용자 이름 "Bob", 비밀번호 "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Welcome, {http.auth.user.id}" 200
}
```

`/secret/` 안의 파일을 보호하여 `Bob`만 접근할 수 있게 합니다 (그 외 경로는 누구나 볼 수 있음):

```caddy
example.com {
	root /srv

	basic_auth /secret/* {
		# 사용자 이름 "Bob", 비밀번호 "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

`argon2id` 예시

```caddy
example.com {
	root /srv

	basic_auth /secret/* argon2id {
		# 사용자 이름 "Bob", 비밀번호 "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
