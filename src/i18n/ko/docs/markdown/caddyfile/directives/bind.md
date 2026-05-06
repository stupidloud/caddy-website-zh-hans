---
title: bind (Caddyfile 지시어)
---

# bind

서버 소켓이 바인딩되어야 할 인터페이스를 오버라이드합니다.

보통 리스너는 빈(와일드카드) 인터페이스에 바인딩됩니다. 하지만 리스너가 다른 호스트 이름이나 IP에 바인딩되도록 강제할 수 있습니다. 이 지시어는 포트가 아닌 호스트만 허용합니다. 포트는 [사이트 주소](/docs/caddyfile/concepts#addresses)에 의해 결정됩니다 (기본값은 `443`).

사이트 바인딩을 일관성 없게 설정하면 의도치 않은 결과가 발생할 수 있습니다. 예를 들어, 동일한 포트의 두 사이트가 `127.0.0.1`로 확인되는데 그중 하나만 `bind 127.0.0.1`로 설정된 경우, 특정 호스트 없이 포트에 바인딩된 다른 사이트 때문에 하나의 사이트만 접근 가능하게 될 수 있습니다. 운영체제는 더 구체적으로 일치하는 소켓을 선택하기 때문입니다. (가상 호스트는 서로 다른 리스너 간에 공유되지 않습니다.)

`bind`는 [네트워크 주소](/docs/conventions#network-addresses)를 허용하지만 포트를 포함할 수는 없습니다.


## 구문

```caddy-d
bind <hosts...>
```

- **&lt;hosts...&gt;** 는 리스너를 바인딩할 호스트 인터페이스의 목록입니다.


## 예시

소켓을 현재 머신에서만 접근 가능하게 하려면 루프백 인터페이스(localhost)에 바인딩합니다:

```caddy
example.com {
	bind 127.0.0.1
}
```

IPv6를 포함하려면:

```caddy
example.com {
	bind 127.0.0.1 [::1]
}
```

`10.0.0.1:8080`에 바인딩하려면:

```caddy
example.com:8080 {
	bind 10.0.0.1
}
```

`/run/caddy`의 유닉스 도메인 소켓에 바인딩하려면:

```caddy
example.com {
	bind unix//run/caddy
}
```

모든 사용자가 쓸 수 있도록 파일 권한을 변경하려면 ([기본값](/docs/conventions#network-addresses)은 소유자만 쓸 수 있는 `0200`입니다):

```caddy
example.com {
	bind unix//run/caddy|0222
}
```

하나의 도메인을 두 개의 서로 다른 인터페이스에 바인딩하고 서로 다른 응답을 하도록 설정하려면:

```caddy
example.com {
	bind 10.0.0.1
	respond "One"
}

example.com {
	bind 10.0.0.2
	respond "Two"
}
```
