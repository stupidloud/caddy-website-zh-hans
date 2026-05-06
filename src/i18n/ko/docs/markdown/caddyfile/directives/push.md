---
title: push (Caddyfile 지시어)
---

# push

HTTP/2 서버 푸시를 사용하여 클라이언트에 리소스를 선제적으로 전송하도록 서버를 구성합니다.

응답의 Link 헤더를 지정하여 서버 푸시용 리소스를 연결할 수 있습니다. 이 지시어는 다음 형식의 업스트림 Link 헤더에 기술된 리소스를 자동으로 푸시합니다:

- `<resource>; as=script`
- `<resource>; as=script,<resource>; as=style`
- `<resource>; nopush`
- `<resource>;<resource2>;...`

여기서 `<resource>`는 슬래시 `/`로 시작합니다(즉, 동일한 호스트의 URI 경로임). 동일한 호스트의 리소스만 푸시할 수 있습니다. 연결된 리소스가 외부 리소스이거나 `nopush` 속성이 있는 경우 푸시되지 않습니다.

기본적으로 푸시 요청에는 원래 요청에서 복사해도 안전하다고 판단되는 일부 헤더가 포함됩니다:

- Accept-Encoding
- Accept-Language
- Accept
- Cache-Control
- User-Agent

이러한 헤더가 없으면 많은 요청이 실패할 것으로 가정하기 때문이며, 수동으로 구성할 필요는 없습니다.

푸시 요청은 내부적으로 가상화되므로 매우 가볍습니다.


## 구문 <a id="syntax"></a>

```caddy-d
push [<matcher>] [<resource>] {
	[GET|HEAD] <resource>
	headers {
		[+]<field> [<value|regexp> [<replacement>]]
		-<field>
	}
}
```

- **&lt;resource&gt;** 는 푸시할 대상 URI 경로입니다. 블록 내에서 사용되는 경우 선택적으로 메서드(GET 또는 POST; 기본값은 GET)가 앞에 올 수 있습니다.
- **&lt;headers&gt;** 는 [`header` 지시어](/docs/caddyfile/directives/header)와 동일한 구문을 사용하여 푸시 요청의 헤더를 조작합니다. 일부 헤더는 기본적으로 전달되므로 명시적으로 구성할 필요가 없습니다(위 내용 참조).



## 예제 <a id="examples"></a>

응답의 `Link` 헤더에 기술된 모든 리소스를 푸시합니다:

```caddy-d
push
```

동일하지만 모든 요청에 대해 `/resources/style.css`도 푸시합니다:

```caddy-d
push * /resources/style.css
```

클라이언트가 `/foo.html`을 요청할 때만 `/foo.jpg`를 푸시합니다:

```caddy-d
push /foo.html /foo.jpg
```
