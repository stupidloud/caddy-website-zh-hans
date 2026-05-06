---
title: templates (Caddyfile 지시어)
---

# templates

응답 본문을 [템플릿(template)](/docs/modules/http.handlers.templates) 문서로 실행합니다. 템플릿은 간단한 동적 페이지를 만들기 위한 기능적 프리미티브(primitives)를 제공합니다. HTTP 하위 요청, HTML 파일 포함(include), 마크다운 렌더링, JSON 파싱, 기본 데이터 구조, 무작위성(randomness), 시간 등의 기능이 포함됩니다.


## 구문 <a id="syntax"></a>

```caddy-d
templates [<matcher>] {
	mime    <types...>
	between <open_delim> <close_delim>
	root    <path>
	extensions {
		<name> {
			...
		}
	}
}
```

- **mime** 은 템플릿 미들웨어가 작동할 MIME 유형입니다. 적격한 `Content-Type`이 없는 응답은 템플릿으로 평가되지 않습니다.

  기본값: `text/html text/plain`.

- **between** 은 템플릿 동작에 대한 여는 구분 기호와 닫는 구분 기호입니다. 문서의 나머지 부분과 충돌하는 경우 이를 변경할 수 있습니다.

  기본값: `{{printf "{{ }}"}}`.

- **root** 는 파일 시스템에 접근하는 기능을 사용할 때 사이트 루트입니다.

  [`root`](root) 지시어로 설정된 사이트 루트가 기본값이며, 설정되지 않은 경우 현재 작업 디렉토리가 사용됩니다.

- **extensions** 를 사용하면 `http.handlers.templates.functions.*` 네임스페이스의 모듈에서 제공하는 사용자 정의 템플릿 함수를 등록할 수 있습니다.

  블록 내부의 각 하위 지시어는 모듈 이름에 해당합니다. 이러한 모듈은 템플릿 함수 맵에 사용자 정의 함수를 추가할 수 있으며, 일반적으로 재사용 가능한 구성 요소를 구현하는 데 사용됩니다. 이 기능은 주로 플러그인을 위한 것입니다.

내장된 템플릿 함수에 대한 문서는 [templates 모듈](/docs/modules/http.handlers.templates#docs)에서 찾을 수 있습니다.



## 예시 <a id="examples"></a>

마크다운을 제공하기 위해 템플릿을 사용하는 사이트의 전체 예시는 [이 웹사이트](https://github.com/caddyserver/website)의 소스 코드를 확인하세요! 특히 [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile)과 [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html)을 살펴보세요.

정적 사이트에 템플릿 활성화:

```caddy
example.com {
	root /srv
	templates
	file_server
}
```

템플릿을 사용하여 간단한 정적 응답을 제공하려면 `Content-Type`을 설정해야 합니다:

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `Current year is: {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

템플릿 확장(플러그인) 사용:

```caddy
example.com {
	root /srv
	templates {
		extensions {
			# caddy-hitcounter 플러그인이 필요합니다:
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
```
