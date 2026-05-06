---
title: "Writing Config Adapters"
---

# 설정 어댑터 작성

다양한 이유로, [JSON](/docs/json/)이 아닌 형식을 사용하여 Caddy를 설정하고 싶을 수 있습니다. Caddy는 [설정 어댑터(config adapters)](/docs/config-adapters)를 통해 이에 대한 일급 지원(first-class support)을 제공합니다.

선호하는 언어/구문/형식에 대한 어댑터가 아직 존재하지 않는 경우, 직접 작성할 수 있습니다!

## 템플릿

시작할 수 있는 템플릿은 다음과 같습니다:

```go
package myadapter

import (
	"fmt"

	"github.com/caddyserver/caddy/v2/caddyconfig"
)

func init() {
	caddyconfig.RegisterAdapter("adapter_name", MyAdapter{})
}

// MyAdapter는 ____를 Caddy JSON에 적용합니다(adapts).
type MyAdapter struct{
}

// Adapt는 본문(body)을 Caddy JSON에 적용합니다.
func (a MyAdapter) Adapt(body []byte, options map[string]interface{}) ([]byte, []caddyconfig.Warning, error) {
	// TODO: 본문을 파싱하고 JSON으로 변환
	return nil, nil, fmt.Errorf("not implemented")
}
```

- [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter)에 대한 godoc을 참조하세요
- ['Adapter'](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter) 인터페이스에 대한 godoc을 참조하세요

반환되는 JSON은 들여쓰기(indented)되어서는 **안 되며**, 항상 간결해야(compact) 합니다. 호출자가 원할 경우 언제든지 보기 좋게 꾸밀(prettify) 수 있습니다.

설정 어댑터는 Caddy _플러그인(plugins)_ 이지만 설정의 일부에 통합되지 않으므로 Caddy _모듈(modules)_ 은 아닙니다 (하지만 편의상 `list-modules`에는 표시됩니다). 따라서 어댑터는 `Provision()`이나 `Validate()` 메서드가 필요하지 않으며 나머지 모듈 수명 주기(lifecycle)를 따르지 않습니다. 어댑터는 `Adapter` 인터페이스만 구현하고 어댑터로 등록되면 됩니다.

`json.RawMessage` 타입인 설정의 필드(즉, 모듈 필드)를 채울 때는 `JSON()` 및 `JSONModuleObject()` 함수를 사용하세요:

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON)은 모듈 이름이 포함되지 않은 모듈 값을 마샬링(marshaling)하기 위한 것입니다. (종종 모듈 이름이 맵 키(map key)인 ModuleMap 필드에 사용됩니다.)
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject)는 모듈 이름이 객체(object)에 추가된 상태로 모듈 값을 마샬링하기 위한 것입니다. (그 외의 거의 모든 곳에서 사용됩니다.)

## Caddyfile 서버 타입 (Caddyfile Server Types)

커스텀 Caddyfile 형식을 구현하는 것도 가능합니다. Caddyfile 어댑터는 단일 어댑터 구현이며 기본 "서버 타입(server type)"은 HTTP이지만, 등록 시 대체 "서버 타입"을 지원합니다. 예를 들어, HTTP Caddyfile은 다음과 같이 등록됩니다:

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

[`caddyfile.ServerType` 인터페이스](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType)를 구현하고 그에 따라 자체 어댑터를 등록하면 됩니다.
