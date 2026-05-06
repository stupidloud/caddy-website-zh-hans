---
title: "Placeholder Support"
---

# 자리 표시자

Caddy에서 자리 표시자(placeholders)는 필요에 따라 각 개별 플러그인에 의해 처리되며, 모든 곳에서 자동으로 작동하지는 않습니다.

즉, 플러그인에서 자리 표시자를 지원하려면 플러그인에 명시적으로 지원을 추가해야 합니다.

자리 표시자에 아직 익숙하지 않다면, [여기](/docs/conventions#placeholders)에서부터 읽어보세요!

## 자리 표시자 개요

[자리 표시자](/docs/conventions#placeholders)는 동적 설정 값으로 사용되는 `{foo.bar}` 형식의 문자열이며 런타임에 나중에 평가됩니다.

`{$FOO}`와 같이 달러 기호로 시작하는 Caddyfile [환경 변수 대체(environment variables substitutions)](/docs/caddyfile/concepts#environment-variables)는 Caddyfile 구문 분석 시간에 평가되므로 플러그인에서 처리할 필요가 없습니다. 동일한 `{ }` 구문을 공유함에도 불구하고 이들은 자리 표시자가 *아닙니다*.

따라서 `{env.HOST}` ([전역 자리 표시자](/docs/conventions#placeholders))가 `{$HOST}` (Caddyfile 환경 변수 대체)와 근본적으로 다르다는 것을 이해하는 것이 중요합니다.

예를 들어 다음 Caddyfile을 살펴보세요:
```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

이 Caddyfile을 `HOST=example caddy adapt`를 사용하여 JSON으로 변환하면(adapt) 다음을 얻게 됩니다:

```json
{
  "apps": {
    "http": {
      "servers": {
        "srv0": {
          "listen": [":8080"],
          "routes": [
            {
              "handle": [
                {
                  "body": "example",
                  "handler": "static_response",
                  "status_code": 200
                }
              ]
            }
          ]
        },
        "srv1": {
          "listen": [":8081"],
          "routes": [
            {
              "handle": [
                {
                  "body": "{env.HOST}",
                  "handler": "static_response",
                  "status_code": 200
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```

특히 `srv0`과 `srv1` 모두에 있는 `"body"` 필드를 살펴보세요.

`srv0`은 `{$HOST}`(Caddyfile 환경 변수 대체)를 사용했기 때문에, JSON 설정을 생성할 때 Caddyfile 구문 분석 시간 동안 처리되어 값이 `example`이 되었습니다.

`srv1`은 `{env.HOST}`(전역 자리 표시자)를 사용했기 때문에 JSON으로 변환할 때 그대로 유지됩니다.

즉, (Caddyfile을 사용하지 않고) JSON 설정을 작성하는 사용자는 `{$ENV}` 구문을 사용할 수 없습니다. 이러한 이유로 플러그인 작성자가 설정이 프로비저닝될 때 자리 표시자를 교체할 수 있도록 지원을 구현하는 것이 중요합니다. 이에 대해서는 아래에 설명되어 있습니다.


## 자리 표시자 지원 구현하기

[`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile)에서 자리 표시자를 처리해서는 안 됩니다. 대신 자리 표시자는 `caddy.Replacer`를 사용하여 나중에 [`Provision()`](/docs/extending-caddy#provisioning) 단계에서 교체되거나 모듈이 실행되는 동안(예: HTTP 핸들러의 경우 `ServeHTTP()`, 매처의 경우 `Match()` 등) 교체되어야 합니다.


### 예시

여기서는 자리 표시자를 처리하기 위해 새로 생성된 교체기(replacer)를 사용하고 있습니다. 프로비저닝은 요청 도중이 아니라 설정이 로드될 때 발생하기 때문에 `{env.HOST}`와 같은 [전역 자리 표시자](/docs/conventions#placeholders)에는 접근할 수 있지만 `{http.request.uri}`와 같은 HTTP 자리 표시자에는 접근할 수 **없습니다**.

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

여기서는 `ServeHTTP` 도중 요청 컨텍스트 `r.Context()`에서 교체기를 가져옵니다. 이 교체기는 전역 자리 표시자 _와_ `{http.request.uri}`와 같은 요청당 HTTP 자리 표시자 모두에 접근할 수 있습니다.

```go
func (g *Gizmo) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	repl := r.Context().Value(caddy.ReplacerCtxKey).(*caddy.Replacer)
	_, err := w.Write([]byte(repl.ReplaceAll(g.Name,"")))
	if err != nil {
		return err
	}
	return next.ServeHTTP(w, r)
}
```
