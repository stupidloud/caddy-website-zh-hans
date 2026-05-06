---
title: "Caddyfile Support"
---

# Caddyfile 지원

Caddy 모듈은 [등록(registered)](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule)될 때 네임스페이스(namespace)에 의해 [기본 JSON 설정](/docs/json/)에 자동으로 추가되어 사용 가능해지고 문서화됩니다. 이로 인해 Caddyfile 지원은 전적으로 선택 사항이지만, Caddyfile을 선호하는 사용자들이 자주 요청합니다.

## 언마샬러 (Unmarshaler)

모듈에 Caddyfile 지원을 추가하려면 간단히 [`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler) 인터페이스를 구현하면 됩니다. 토큰을 구문 분석(parse)하는 방식에 따라 모듈이 가질 Caddyfile 구문(syntax)을 선택할 수 있습니다.

언마샬러의 역할은 자신에게 전달된 [`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser)를 사용하여, 예를 들어 필드를 채우는 등의 방식으로 모듈의 타입을 설정하는 것뿐입니다. 예를 들어 이름이 `Gizmo`인 모듈 타입은 다음과 같은 메서드를 가질 수 있습니다:

```go
// UnmarshalCaddyfile은 caddyfile.Unmarshaler를 구현합니다. 구문:
//
// gizmo <name> [<option>]
//
func (g *Gizmo) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // 지시어 이름(directive name) 소비

	if !d.Args(&g.Name) {
		// 인수가 충분하지 않음
		return d.ArgErr()
	}
	if d.NextArg() {
		// 선택적(optional) 인수
		g.Option = d.Val()
	}
	if d.NextArg() {
		// 인수가 너무 많음
		return d.ArgErr()
	}

	return nil
}
```

메서드에 대한 godoc 주석에 구문을 문서화하는 것이 좋습니다. Caddyfile 구문 분석에 대한 자세한 내용은 [`caddyfile` 패키지에 대한 godoc](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc)을 참조하세요.

지시어 이름 토큰은 간단한 `d.Next()` 호출로 소비하거나 건너뛸 수 있습니다.

`d.NextArg()` 또는 `d.RemainingArgs()`를 사용하여 누락되었거나 남는 인수가 있는지 확인하세요. 간단한 "유효하지 않은 사례(invalid case)" 메시지의 경우 `d.ArgErr()`를 사용하고, 문제에 대한 설명(이상적으로는 제안하는 해결책 포함)이 있는 유용한 오류 메시지를 작성하려면 `d.Errf("some message")`를 사용하세요.

또한 인터페이스가 제대로 충족되는지 확인하기 위해 [인터페이스 가드(interface guard)](/docs/extending-caddy#interface-guards)를 추가해야 합니다:

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

### 블록 (Blocks)

한 줄에 담을 수 있는 것보다 더 많은 설정을 받으려면 하위 지시어가 있는 블록을 허용할 수 있습니다. 이는 `d.NextBlock()`을 사용하고 원래의 중첩 수준(nesting level)으로 돌아올 때까지 반복(iterating)하여 수행할 수 있습니다:

```go
for nesting := d.Nesting(); d.NextBlock(nesting); {
	switch d.Val() {
		case "sub_directive_1":
		// ...
		case "sub_directive_2":
		// ...
	}
}
```

루프의 각 반복이 전체 세그먼트(줄 또는 블록)를 소비하는 한, 이는 블록을 처리하는 우아한 방법입니다.

## HTTP 지시어

HTTP Caddyfile은 Caddy의 기본 Caddyfile 어댑터 구문(또는 "서버 타입")입니다. 이는 확장 가능하므로, 모듈에 대한 고유한 "최상위(top-level)" 지시어를 [등록](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterDirective)할 수 있습니다:

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

지시어가 (일반적인 경우처럼) 단일 HTTP 핸들러만 반환하는 경우 [`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective)를 사용하는 것이 더 쉬울 수 있습니다:

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

기본적인 아이디어는 지시어와 연결하는 [구문 분석 함수](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc)가 하나 이상의 [`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue) 값을 반환한다는 것입니다. (또는 `RegisterHandlerDirective`를 사용하는 경우 채워진 `caddyhttp.MiddlewareHandler` 값을 직접 반환합니다.) 각 설정 값은 HTTP Caddyfile 어댑터가 최종 JSON 설정의 어떤 부분에 사용될 수 있는지 알 수 있도록 도와주는 ["클래스(class)"](#classes)와 연결됩니다. 모든 설정 값은 어댑터가 최종 JSON 설정을 구성할 때 가져올 수 있도록 한데 모아집니다.

이러한 설계를 통해 지시어는 인식되는 모든 클래스에 대한 설정 값을 반환할 수 있습니다. 즉, HTTP Caddyfile 어댑터가 지정된 클래스를 가지고 있는 설정의 어떤 부분에도 영향을 미칠 수 있습니다.

이미 `UnmarshalCaddyfile()` 메서드를 구현했다면, 구문 분석 함수는 다음과 같이 간단해질 수 있습니다:

```go
// parseCaddyfileHandler는 h의 토큰을 언마샬링하여 새로운 미들웨어 핸들러 값으로 만듭니다.
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

`httpcaddyfile.Helper` 타입을 사용하는 방법에 대한 자세한 내용은 [`httpcaddyfile` 패키지 godoc](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc)을 참조하세요.

### 핸들러 순서 (Handler order)

HTTP 미들웨어/핸들러 값을 반환하는 모든 지시어는 올바른 순서로 평가되어야 합니다. 예를 들어, 사이트의 루트 디렉토리를 설정하는 핸들러는 루트 디렉토리에 접근하는 핸들러보다 먼저 와야 디렉토리 경로가 무엇인지 알 수 있습니다.

HTTP Caddyfile은 [표준 지시어에 대해 하드코딩된 순서를 가지고 있습니다](/docs/caddyfile/directives#directive-order). 이렇게 하면 사용자가 웹 서버의 가장 일반적인 기능에 대한 구현 세부 사항을 알 필요가 없고, 올바른 설정을 작성하기가 더 쉬워집니다. 단일 하드코딩된 목록은 Caddyfile의 확장 가능한 특성을 고려할 때 비결정성(nondeterminism)을 방지하기도 합니다.

**새로운 핸들러 지시어를 등록할 때는 (`route` 블록 외부에서) 사용되기 전에 해당 목록에 추가해야 합니다.** 이 작업은 다음 세 가지 방법 중 하나를 사용하여 수행됩니다:

- (권장) 플러그인 작성자는 지시어를 등록한 후 `init()`에서 [`httpcaddyfile.RegisterDirectiveOrder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile#RegisterDirectiveOrder)를 호출하여 다른 [표준 지시어](/docs/caddyfile/directives#directive-order)에 상대적인 순서로 지시어를 삽입할 수 있습니다. 이렇게 하면 사용자는 추가 설정 없이 사이트에서 지시어를 직접 사용할 수 있습니다. 예를 들어, `gizmo` 지시어가 `header` 핸들러 다음에 평가되도록 삽입하려면:

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- 사용자는 Caddyfile의 표준 순서를 수정하기 위해 [`order` 전역 옵션](/docs/caddyfile/options)을 추가할 수 있습니다. 예: `order gizmo before respond`는 `respond` 핸들러보다 먼저 평가되도록 새로운 지시어 `gizmo`를 삽입합니다. 그런 다음 지시어를 정상적으로 사용할 수 있습니다.

- 사용자는 지시어를 [`route` 블록](/docs/caddyfile/directives/route) 안에 배치할 수 있습니다. 경로 블록 안의 지시어는 재정렬되지 않으므로, 경로 블록 안에서 사용되는 지시어는 목록에 나타날 필요가 없습니다.

처음 두 가지가 아닌 마지막 두 가지 옵션 중 하나를 선택하는 경우, 사용자가 제대로 사용할 수 있도록 지시어가 순서 목록 내의 어느 위치에 있어야 하는지에 대한 권장 사항을 문서화해 주세요.

### 클래스 (Classes)

이 표는 HTTP Caddyfile 어댑터가 인식하는 내보내진(exported) 타입이 있는 각 클래스를 설명합니다:

Class name | Expected type | Description
---------- | ------------- | -----------
bind | `[]string` | 서버 리스너 바인딩 주소
route | `caddyhttp.Route` | HTTP 핸들러 경로
error_route | `*caddyhttp.Subroute` | HTTP 오류 처리 경로
tls.connection_policy | `*caddytls.ConnectionPolicy` | TLS 연결 정책
tls.cert_issuer | `certmagic.Issuer` | TLS 인증서 발급자
tls.cert_loader | `caddytls.CertificateLoader` | TLS 인증서 로더

## 서버 타입 (Server Types)

구조적으로 Caddyfile은 단순한 형식이므로, 다양한 필요에 맞게 다양한 유형의 Caddyfile 형식(때로는 "서버 타입"이라고도 함)이 있을 수 있습니다.

기본 Caddyfile 형식은 아마도 가장 익숙하실 HTTP Caddyfile입니다. 이 형식은 주로 [`http` 앱](/docs/modules/http)을 설정하면서 잠재적으로 Caddy 설정 구조의 다른 부분(예: 인증서를 로드하고 자동화하는 `tls` 앱)에 일부 설정을 흩뿌립니다(sprinkling).

HTTP 이외의 앱을 설정하려면 [자신만의 서버 타입](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter)을 사용하는 자체 설정 어댑터(config adapter)를 구현하고 싶을 수 있습니다. Caddyfile 어댑터는 실제로 입력을 구문 분석하여 서버 블록 및 옵션 목록을 제공하며, 해당 구조를 이해하고 JSON 설정으로 변환하는 것은 어댑터에 달려 있습니다.
