---
title: request_body (Caddyfile 지시어)
---

# request_body

들어오는 요청의 본문(body)을 조작하거나 제한을 설정합니다.

## 구문

```caddy-d
request_body [<matcher>] {
	max_size <value>
	set <body_content>
}
```

- **max_size**는 요청 본문에 허용되는 최대 크기(바이트)입니다. [go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants)에서 지원하는 모든 크기 값을 허용합니다. 이보다 많은 바이트를 읽으려고 하면 HTTP 상태 `413` 오류가 반환됩니다.

⚠️ *실험적 기능* <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set**은 요청 본문을 특정 내용으로 설정할 수 있게 해줍니다. 내용에는 동적으로 데이터를 삽입하기 위한 플레이스홀더가 포함될 수 있습니다.

## 예시

요청 본문 크기를 10메가바이트로 제한합니다:

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

SQL 쿼리를 포함하는 JSON 구조로 요청 본문을 설정합니다:

```caddy
example.com {
	handle /jazz {
		request_body {
			set `\{"statementText":"SELECT name, genre, debut_year FROM artists WHERE genre = 'Jazz'"}`
		}

		reverse_proxy localhost:8080 {
			header_up Content-Type application/json
			method POST
			rewrite /execute-sql
		}
	}
}
