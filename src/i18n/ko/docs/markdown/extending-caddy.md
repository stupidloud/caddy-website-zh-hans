---
title: "Caddy 확장"
---

# Caddy 확장

Caddy는 모듈식 아키텍처 덕분에 확장하기 쉽습니다. 대부분의 Caddy 확장(또는 플러그인)이 Caddy의 구성 구조를 확장하거나 플러그인하는 경우 *모듈(modules)* 이라고 합니다. 명확히 하자면, Caddy 모듈은 [Go 모듈](https://github.com/golang/go/wiki/Modules)과 구별됩니다(물론 Go 모듈이기도 합니다).

**전제 조건:**
- [Caddy의 아키텍처](/docs/architecture)에 대한 기본적 이해
- Go 언어 능숙도
- [`go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://golang.org/doc/install)
- [`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/xcaddy)


## 빠른 시작

Caddy 모듈은 패키지를 가져올 때 자신을 Caddy 모듈로 등록하는 명명된 유형입니다. 결정적으로 모듈은 이름과 생성자 함수를 제공하는 [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module) 인터페이스를 항상 구현합니다.

새로운 Go 모듈의 Go 파일에 다음 템플릿을 붙여넣고 패키지 이름, 유형 이름 및 Caddy 모듈 ID를 사용자 정의합니다.

```go
package mymodule

import "github.com/caddyserver/caddy/v2"

func init() {
	caddy.RegisterModule(Gizmo{})
}

// Gizmo는 예제입니다. 여기에 사용자 정의 유형을 입력하세요.
type Gizmo struct {
}

// CaddyModule은 Caddy 모듈 정보를 반환합니다.
func (Gizmo) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "foo.gizmo",
		New: func() caddy.Module { return new(Gizmo) },
	}
}
```

그런 다음 프로젝트 디렉터리에서 이 명령을 실행하면 목록에 모듈이 나타나는 것을 볼 수 있습니다.

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">

[`xcaddy` 명령](https://github.com/caddyserver/xcaddy)은 모든 모듈 개발자의 워크플로에서 중요한 부분입니다. 플러그인과 함께 Caddy를 컴파일한 다음 지정된 인수를 사용하여 실행합니다. 매번 임시 바이너리를 삭제합니다(`go run`과 유사함).

</aside>


축하합니다! 모듈이 Caddy에 등록되었으며, 동일한 네임스페이스에서 모듈을 사용하는 위치라면 어디든 [Caddy의 구성 문서](/docs/json/)에서 사용할 수 있습니다.

내부적으로 `xcaddy`는 Caddy와 플러그인 모두를 요구하는 새로운 Go 모듈을 생성하고(로컬 개발 버전을 사용하도록 적절한 `replace`를 적용) 컴파일 시 포함되도록 가져오기(import)를 추가합니다.

```go
import _ "github.com/example/mymodule"
```


## 모듈 기초

Caddy 모듈은:

1. `caddy.Module` 인터페이스를 구현하여 ID와 생성자를 제공합니다.
2. 적절한 네임스페이스 내에서 고유한 이름을 갖습니다.
3. 보통 해당 네임스페이스에 대해 호스트 모듈에게 의미 있는 하나 이상의 인터페이스를 만족합니다.

**호스트 모듈** (또는 *부모 모듈*)은 다른 모듈을 로드/초기화하는 모듈입니다. 일반적으로 게스트 모듈을 위한 네임스페이스를 정의합니다.

**게스트 모듈** (또는 *자식 모듈*)은 로드되거나 초기화되는 모듈입니다. 모든 모듈은 게스트 모듈입니다.


## 모듈 ID

각 Caddy 모듈은 네임스페이스와 이름으로 구성된 고유한 ID를 갖습니다:

- 완전한 ID는 `foo.bar.module_name`과 같습니다.
- 네임스페이스는 `foo.bar`가 됩니다.
- 이름은 `module_name`이며, 해당 네임스페이스 내에서 고유해야 합니다.

모듈 ID는 `snake_case` 규칙을 사용해야 합니다.

### 네임스페이스

네임스페이스는 클래스와 같습니다. 즉, 네임스페이스는 그 안에 있는 모든 모듈 간에 공통된 기능을 정의합니다. 예를 들어, `http.handlers` 네임스페이스 내의 모든 모듈이 HTTP 핸들러라고 기대할 수 있습니다. 따라서 호스트 모듈은 해당 네임스페이스의 게스트 모듈을 `interface{}` 유형에서 `caddyhttp.MiddlewareHandler`와 같이 구체적이고 유용한 유형으로 타입 단언(type-assert)할 수 있습니다.

호스트 모듈이 원하는 기능을 제공하기 위해 특정 네임스페이스 내의 모듈을 Caddy에 요청하기 때문에, 게스트 모듈이 호스트 모듈에 의해 인식되려면 적절한 네임스페이스에 위치해야 합니다. 예를 들어, `gizmo`라는 HTTP 핸들러 모듈을 작성한다면 `http` 앱은 `http.handlers` 네임스페이스에서 핸들러를 찾기 때문에 모듈의 이름은 `http.handlers.gizmo`가 됩니다.

달리 말하면, Caddy 모듈은 모듈 네임스페이스에 따라 [특정 인터페이스](/docs/extending-caddy/namespaces)를 구현해야 합니다. 이 규칙 덕분에 모듈 개발자는 "`http.handlers` 네임스페이스의 모든 모듈은 HTTP 핸들러입니다"와 같이 직관적으로 말할 수 있습니다. 보다 기술적으로는, 보통 "`http.handlers` 네임스페이스의 모든 모듈은 `caddyhttp.MiddlewareHandler` 인터페이스를 구현합니다"라는 뜻입니다. 메서드 세트가 알려져 있기 때문에 더 구체적인 유형을 단언하여 사용할 수 있습니다.

**[모든 표준 Caddy 네임스페이스를 해당 Go 유형에 매핑하는 표 보기](/docs/extending-caddy/namespaces)**

`caddy`와 `admin` 네임스페이스는 예약되어 있으며 앱 이름이 될 수 없습니다.

타사 호스트 모듈에 플러그인되는 모듈을 작성하려면, 해당 모듈의 네임스페이스 문서를 참조하세요.

### 이름

네임스페이스 내의 이름은 중요하고 사용자에게 잘 노출되지만, 고유하고 간결하며 그 기능을 이해할 수 있는 한 특정 형식이 크게 중요하지는 않습니다.


## 앱 모듈

앱은 빈 네임스페이스를 가지며, 관례적으로 자체 최상위 네임스페이스가 되는 모듈입니다. 앱 모듈은 [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App) 인터페이스를 구현합니다.

이 모듈들은 Caddy 구성의 최상위 [`"apps"`](/docs/json/#apps) 속성에 나타납니다:

```json
{
	"apps": {}
}
```

예시 [앱](/docs/json/apps/)으로는 `http`와 `tls`가 있습니다. 이들은 빈 네임스페이스를 갖습니다.

이 앱들을 위해 작성된 게스트 모듈은 앱 이름에서 파생된 네임스페이스에 있어야 합니다. 예를 들어, HTTP 핸들러는 `http.handlers` 네임스페이스를 사용하고 TLS 인증서 로더는 `tls.certificates` 네임스페이스를 사용합니다.

## 모듈 구현

모듈은 거의 모든 유형이 될 수 있지만, 사용자 구성을 보유할 수 있기 때문에 구조체(struct)가 가장 일반적입니다.


### 구성

대부분의 모듈은 약간의 구성이 필요합니다. 유형이 JSON과 호환되는 한 Caddy는 이를 자동으로 처리합니다. 따라서 모듈이 구조체 유형인 경우 필드에 구조체 태그가 필요하며, Caddy 규칙에 따라 `snake_casing`을 사용해야 합니다.

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

구조체 태그에 `omitempty` 옵션을 사용하면 필드의 값이 해당 유형의 제로 값일 경우 JSON 출력에서 제외됩니다. 이는 마샬링할 때(예: Caddyfile을 JSON으로 조정할 때) JSON 구성을 깨끗하고 간결하게 유지하는 데 유용합니다.

모듈이 초기화될 때 그 구성은 이미 채워져 있습니다. 모듈이 초기화된 후 추가 [프로비저닝](#provisioning) 및 [유효성 검사](#validating) 단계를 수행하는 것도 가능합니다.


### 모듈 수명 주기

모듈의 수명은 호스트 모듈에 의해 로드될 때 시작됩니다. 다음과 같은 일이 발생합니다:

1. 모듈 값의 인스턴스를 가져오기 위해 [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New)가 호출됩니다.
2. 모듈의 구성이 해당 인스턴스로 언마샬링됩니다.
3. 모듈이 [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner)인 경우, `Provision()` 메서드가 호출됩니다.
4. 모듈이 [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator)인 경우, `Validate()` 메서드가 호출됩니다.
5. 이 시점에서 호스트 모듈에는 로드된 게스트 모듈이 `interface{}` 값으로 제공되므로, 호스트 모듈은 일반적으로 게스트 모듈을 더 유용한 유형으로 타입 단언합니다. 해당 네임스페이스의 게스트 모듈에 무엇이 필요한지(예: 구현해야 하는 메서드가 무엇인지) 알아보려면 호스트 모듈의 문서를 확인하세요.
6. 모듈이 더 이상 필요하지 않고 [`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#CleanerUpper)인 경우, `Cleanup()` 메서드가 호출됩니다.

특정 시간에 로드된 여러 모듈 인스턴스가 중첩될 수 있음에 유의하세요! 구성 변경 중에 새 모듈은 이전 모듈이 중지되기 전에 시작됩니다. 전역 상태를 신중하게 사용해야 합니다. 모듈 로드 전반에 걸쳐 전역 상태를 관리하는 데 도움이 필요하면 [`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool) 유형을 사용하세요. 모듈이 소켓에서 수신 대기하는 경우, `caddy.Listen*()`을 사용하여 중첩 사용을 지원하는 소켓을 얻으세요.

### 프로비저닝

모듈의 구성은 해당 값으로 자동 언마샬링됩니다(JSON 구성을 로드할 때). 즉, 예를 들어 구조체 필드는 자동으로 채워집니다.

그러나 모듈에 추가 프로비저닝 단계가 필요한 경우 (선택적) [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner) 인터페이스를 구현할 수 있습니다.

```go
// Provision은 모듈을 설정합니다.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO: 모듈 설정
	return nil
}
```

이곳은 사용자가 제공하지 않은 필드(제로 값이 아닌 필드)에 대한 기본값을 설정해야 하는 곳입니다. 필수 필드가 설정되지 않은 경우 오류를 반환할 수 있습니다. 제로 값이 의미를 갖는 숫자 필드(예: 일부 시간 제한)의 경우 `0`이 아닌 `-1`을 사용하여 "끄기"를 지원하고자 할 수 있으므로, 사용자가 구성하지 않은 경우 기본값을 설정할 수 있습니다.

또한 이 단계는 일반적으로 호스트 모듈이 게스트/자식 모듈을 로드하는 곳입니다.

모듈은 `ctx.App()`을 호출하여 다른 앱에 액세스할 수 있지만, 모듈에는 순환 종속성이 없어야 합니다. 즉, `tls` 앱에 의해 로드된 모듈이 `http` 앱에 종속되는 경우, `http` 앱에 의해 로드된 모듈은 `tls` 앱에 종속될 수 없습니다. (Go에서 가져오기 순환을 금지하는 규칙과 매우 유사합니다.)

또한 구성이 유효성 검증만 될 때도 프로비저닝이 수행되므로, `Provision`에서 비용이 많이 드는 작업을 수행하지 않도록 해야 합니다. 프로비저닝 단계에 있을 때는 모듈이 실제로 사용될 것이라고 예상하지 마세요.

#### 로그

Caddy에서 [로깅이 작동하는 방식](/docs/logging)을 확인하세요. 모듈에 로깅이 필요한 경우 Go 표준 라이브러리의 `log.Print*()`를 사용하지 마세요. 즉, **Go의 전역 로거를 사용하지 마세요**. Caddy는 [zap](https://github.com/uber-go/zap)과 함께 고성능, 매우 유연한 구조화된 로깅을 사용합니다.

로그를 내보내려면 모듈의 Provision 메서드에서 로거를 가져오세요:

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger는 *zap.Logger입니다.
}
```

그런 다음 `g.logger`를 사용하여 구조화된 수준의 로그를 내보낼 수 있습니다. 자세한 내용은 [zap의 godoc](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger)을 참조하세요.


### 유효성 검사

자신의 구성을 유효성 검사하려는 모듈은 (선택적) [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator) 인터페이스를 만족함으로써 이를 수행할 수 있습니다.

```go
// Validate는 모듈에 사용 가능한 구성이 있는지 유효성 검사합니다.
func (g Gizmo) Validate() error {
	// TODO: 모듈 설정 유효성 검사
	return nil
}
```

Validate는 읽기 전용 함수여야 합니다. `Provision()` 메서드 후에 실행됩니다.


### 인터페이스 가드

Caddy 모듈의 동작은 Go 인터페이스가 암시적으로 만족되기 때문에 암시적입니다. 단순히 모듈의 유형에 올바른 메서드를 추가하기만 하면 모듈의 올바름이 결정되거나 깨질 수 있습니다. 따라서 오타를 내거나 메서드 서명을 잘못 입력하면 예기치 않은 (또는 누락된) 동작이 발생할 수 있습니다.

다행히 올바른 메서드를 추가했는지 확인하기 위해 코드에 추가할 수 있는 쉽고 오버헤드가 없는 컴파일 시간 검사가 있습니다. 이를 인터페이스 가드(interface guards)라고 합니다.

```go
var _ InterfaceName = (*YourType)(nil)
```

`InterfaceName`을 만족하려는 인터페이스로, `YourType`을 모듈의 유형 이름으로 바꾸세요.

예를 들어, 정적 파일 서버와 같은 HTTP 핸들러는 여러 인터페이스를 만족할 수 있습니다.

```go
// 인터페이스 가드
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

이는 `*FileServer`가 해당 인터페이스를 만족하지 못하는 경우 프로그램이 컴파일되는 것을 방지합니다.

인터페이스 가드가 없으면 혼란스러운 버그가 발생할 수 있습니다. 예를 들어, 모듈이 사용되기 전에 자신을 프로비저닝해야 하는데 `Provision()` 메서드에 실수가 있는 경우(예: 맞춤법 오류 또는 잘못된 서명) 프로비저닝이 발생하지 않아 원인을 찾기 힘듭니다. 인터페이스 가드는 매우 쉽고 이를 방지할 수 있습니다. 보통 파일의 맨 아래에 작성됩니다.


## 호스트 모듈

모듈은 자신의 게스트 모듈을 로드할 때 호스트 모듈이 됩니다. 모듈 기능의 일부가 다른 방식으로 구현될 수 있는 경우 유용합니다.

호스트 모듈은 거의 항상 구조체입니다. 일반적으로 게스트 모듈을 지원하려면 원시 JSON을 보관하는 필드와 디코딩된 값을 보관하는 필드의 두 가지 구조체 필드가 필요합니다.

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

첫 번째 필드(이 예에서는 `GadgetRaw`)는 게스트 모듈의 원시적인 프로비저닝되지 않은 JSON 형식을 찾을 수 있는 곳입니다.

두 번째 필드(`Gadget`)는 최종적으로 프로비저닝된 값이 저장되는 위치입니다. 두 번째 필드는 사용자를 대면하지 않기 때문에 구조체 태그로 JSON에서 제외합니다. (다른 패키지에서 필요하지 않은 경우 내보내지 않을 수도 있으며, 이 경우 구조체 태그가 필요하지 않습니다.)

### Caddy 구조체 태그

원시 모듈 필드의 `caddy` 구조체 태그는 Caddy가 로드할 모듈의 네임스페이스와 이름(전체 ID로 구성됨)을 아는 데 도움이 됩니다. 또한 문서를 생성하는 데에도 사용됩니다.

구조체 태그는 `key1=val1 key2=val2 ...`와 같은 매우 간단한 형식을 갖습니다.

모듈 필드의 경우 구조체 태그는 다음과 같습니다.

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

`namespace=` 부분은 필수입니다. 모듈을 찾을 네임스페이스를 정의합니다.

`inline_key=` 부분은 모듈의 이름이 모듈 자체와 함께 *인라인(inline)* 으로 발견되는 경우에만 사용됩니다. 이것은 값이 인라인 키 중 하나를 갖는 객체이고, 그 값이 모듈의 이름임을 의미합니다. 생략하는 경우 필드 유형은 맵 키가 모듈 이름인 [`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap) 또는 `[]caddy.ModuleMap`이어야 합니다.


### 게스트 모듈 로딩

게스트 모듈을 로드하려면 프로비저닝 단계에서 [`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule)을 호출하세요.

```go
// Provision은 g를 설정하고 gadget을 로드합니다.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	if g.GadgetRaw != nil {
		val, err := ctx.LoadModule(g, "GadgetRaw")
		if err != nil {
			return fmt.Errorf("loading gadget module: %v", err)
		}
		g.Gadget = val.(Gadgeter)
	}
	return nil
}
```

`LoadModule()` 호출은 구조체에 대한 포인터와 필드 이름을 문자열로 취합니다. 이상하죠? 왜 구조체 필드를 직접 전달하지 않을까요? 구성의 레이아웃에 따라 모듈을 로드하는 몇 가지 다른 방법이 있기 때문입니다. 이 메서드 서명을 통해 Caddy는 리플렉션을 사용하여 모듈을 로드하는 가장 좋은 방법을 파악하고 무엇보다도 구조체 태그를 읽을 수 있습니다.

게스트 모듈을 사용자가 명시적으로 설정해야 하는 경우, 로드하기 전에 Raw 필드가 nil이거나 비어 있으면 오류를 반환해야 합니다.

로드된 모듈이 어떻게 타입 단언되는지 확인하세요: `g.Gadget = val.(Gadgeter)` - 반환된 `val`이 별로 유용하지 않은 `interface{}` 유형이기 때문입니다. 그러나 선언된 네임스페이스(예제의 구조체 태그에 있는 `foo.gizmo.gadgets`)의 모든 모듈이 `Gadgeter` 인터페이스를 구현할 것으로 기대하므로 이 타입 단언은 안전하며, 그 후 사용할 수 있습니다!

호스트 모듈이 새로운 네임스페이스를 정의하는 경우 [여기에서 수행한 것처럼](/docs/extending-caddy/namespaces) 개발자를 위해 해당 네임스페이스와 해당 Go 유형(들)을 모두 문서화해야 합니다.

## 모듈 문서화

새로운 Caddy 모듈이 모듈 문서에 나타나고 http://caddyserver.com/download 에서 사용 가능하게 하려면 모듈을 등록하세요. 등록은 http://caddyserver.com/account 에서 가능합니다. 아직 계정이 없다면 새 계정을 만들고 "Register package"를 클릭하세요.

## 전체 예제

HTTP 핸들러 모듈을 작성하고 싶다고 가정해 봅시다. 이것은 데모 목적으로 만들어진 인위적인 미들웨어로, 모든 HTTP 요청에 대해 스트림에 방문자의 IP 주소를 출력합니다.

대부분의 사람들은 비자동화된 상황에서 Caddyfile 사용을 선호하기 때문에 Caddyfile을 통해 구성할 수 있도록 하려고 합니다. 우리는 HTTP 라우트에 핸들러를 추가할 수 있는 일종의 지시문인 Caddyfile 핸들러 지시문을 등록하여 이를 수행합니다. 또한 `caddyfile.Unmarshaler` 인터페이스도 구현합니다. 이 몇 줄의 코드를 추가하면 이 모듈을 Caddyfile로 구성할 수 있습니다! 예: `visitor_ip stdout`.

다음은 설명 주석이 포함된 모듈의 코드입니다.

```go
package visitorip

import (
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/caddyserver/caddy/v2"
	"github.com/caddyserver/caddy/v2/caddyconfig/caddyfile"
	"github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile"
	"github.com/caddyserver/caddy/v2/modules/caddyhttp"
)

func init() {
	caddy.RegisterModule(Middleware{})
	httpcaddyfile.RegisterHandlerDirective("visitor_ip", parseCaddyfile)
}

// Middleware는 방문자의 IP 주소를 파일이나 스트림에 쓰는 
// HTTP 핸들러를 구현합니다.
type Middleware struct {
	// 쓸 파일 또는 스트림입니다. "stdout" 또는 
	// "stderr"일 수 있습니다.
	Output string `json:"output,omitempty"`

	w io.Writer
}

// CaddyModule은 Caddy 모듈 정보를 반환합니다.
func (Middleware) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "http.handlers.visitor_ip",
		New: func() caddy.Module { return new(Middleware) },
	}
}

// Provision은 caddy.Provisioner를 구현합니다.
func (m *Middleware) Provision(ctx caddy.Context) error {
	switch m.Output {
	case "stdout":
		m.w = os.Stdout
	case "stderr":
		m.w = os.Stderr
	default:
		return fmt.Errorf("an output stream is required")
	}
	return nil
}

// Validate는 caddy.Validator를 구현합니다.
func (m *Middleware) Validate() error {
	if m.w == nil {
		return fmt.Errorf("no writer")
	}
	return nil
}

// ServeHTTP는 caddyhttp.MiddlewareHandler를 구현합니다.
func (m Middleware) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	m.w.Write([]byte(r.RemoteAddr))
	return next.ServeHTTP(w, r)
}

// UnmarshalCaddyfile은 caddyfile.Unmarshaler를 구현합니다.
func (m *Middleware) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // 지시문 이름 소비

	// 인수가 필요함
	if !d.NextArg() {
		return d.ArgErr()
	}

	// 인수를 저장
	m.Output = d.Val()
	return nil
}

// parseCaddyfile은 h에서 토큰을 언마샬링하여 새로운 Middleware로 만듭니다.
func parseCaddyfile(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var m Middleware
	err := m.UnmarshalCaddyfile(h.Dispenser)
	return m, err
}

// 인터페이스 가드
var (
	_ caddy.Provisioner           = (*Middleware)(nil)
	_ caddy.Validator             = (*Middleware)(nil)
	_ caddyhttp.MiddlewareHandler = (*Middleware)(nil)
	_ caddyfile.Unmarshaler       = (*Middleware)(nil)
)
```
