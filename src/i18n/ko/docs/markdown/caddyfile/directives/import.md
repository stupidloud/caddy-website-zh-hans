---
title: import (Caddyfile 지시어)
---

# import

[스니펫](/docs/caddyfile/concepts#snippets)이나 파일을 포함하며, 이 지시어를 해당 스니펫 또는 파일의 내용으로 대체합니다.

이 지시어는 특별한 사례입니다. 구조가 파싱되기 전에 평가되며, Caddyfile의 어느 위치에서나 나타날 수 있습니다.

## 구문

```caddy-d
import <pattern> [<args...>] [{block}]
```

- **&lt;pattern&gt;** 은 포함할 파일 이름, glob 패턴 또는 [스니펫](/docs/caddyfile/concepts#snippets)의 이름입니다. 해당 내용은 마치 그 파일의 내용이 처음부터 여기에 있었던 것처럼 이 라인을 대체합니다.

  특정 파일을 찾을 수 없으면 오류가 발생하지만, 비어 있는 glob 패턴은 오류가 아닙니다.

  특정 파일을 가져올 때 파일이 비어 있으면 경고가 발생합니다.

  패턴이 파일 이름이나 glob인 경우, 항상 `import`가 나타나는 파일을 기준으로 상대적인 경로를 가집니다.

  glob 패턴 `*`을 마지막 경로 세그먼트로 사용하는 경우, 숨김 파일(즉, `.`으로 시작하는 파일)은 무시됩니다. 숨김 파일을 가져오려면 `.*`을 마지막 세그먼트로 사용하세요.
- **&lt;args...&gt;** 는 가져온 토큰에 전달할 선택적 인자 목록입니다. 이 플레이스홀더는 특별한 사례로, 런타임이 아닌 Caddyfile 파싱 시점에 평가됩니다. [Go의 슬라이스 구문](https://gobyexample.com/slices)과 유사하게 다양한 형태로 사용할 수 있습니다:
  - `{args[n]}`: n번째(0부터 시작) 위치 인자
  - `{args[:]}`: 모든 인자가 삽입됨
  - `{args[:m]}`: m 이전의 모든 인자가 삽입됨
  - `{args[n:]}`: n부터 시작하는 모든 인자가 삽입됨
  - `{args[n:m]}`: n과 m 사이의 범위에 있는 인자가 삽입됨

  많은 토큰을 삽입하는 형태의 경우, 플레이스홀더는 그 자체로 하나의 [토큰](/docs/caddyfile/concepts#tokens-and-quotes)이어야 하며 다른 토큰의 일부가 될 수 없습니다. 다시 말해, 주변에 공백이 있어야 하며 따옴표 안에 있을 수 없습니다.

  v2.7.0 이전에는 구문이 `{args.N}`이었으나, 위의 더 유연한 구문을 위해 해당 형식은 더 이상 권장되지 않습니다(deprecated).

⚠️ *실험적 기능* <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** 은 가져온 토큰에 전달할 선택적 블록입니다. 이 플레이스홀더는 특별한 사례로, 런타임이 아닌 Caddyfile 파싱 시점에 재귀적으로 평가됩니다. 두 가지 형태로 사용할 수 있습니다:
  - `{block}`: 제공된 전체 블록의 내용이 플레이스홀더를 대체함
  - `{blocks.key}`: `key`는 제공된 블록 내 매개변수의 첫 번째 토큰임


## 예시

인접한 sites-enabled 폴더의 모든 파일 가져오기(숨김 파일 제외):

```caddy-d
import sites-enabled/*
```

가져오기 인자를 사용하여 CORS 헤더를 설정하는 스니펫 가져오기:

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

프록시 업스트림 목록을 인자로 받는 스니펫 가져오기:

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

첫 번째 인자로 접두사 재작성(rewrite) 규칙을 사용하는 프록시를 생성하는 스니펫 가져오기:

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ *실험적 기능* <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

설정 가능한 "hello world" 메시지와 content-type으로 응답하는 스니펫 가져오기:

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

역방향 프록시를 위한 확장 가능한 옵션을 제공하는 스니펫 가져오기:

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

모든 지시어 세트를 제공하지만 사전 로드된 미들웨어가 있는 스니펫 가져오기:

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
