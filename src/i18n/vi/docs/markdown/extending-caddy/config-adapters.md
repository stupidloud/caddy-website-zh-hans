---
title: "Viết Bộ điều hợp Cấu hình"
---

<a id="writing-config-adapters"></a>
# Viết Bộ điều hợp Cấu hình

Vì nhiều lý do khác nhau, bạn có thể muốn cấu hình Caddy bằng một định dạng không phải là [JSON](/docs/json/). Caddy hỗ trợ điều này một cách xuất sắc thông qua [bộ điều hợp cấu hình (config adapters)](/docs/config-adapters).

Nếu chưa có bộ điều hợp nào cho ngôn ngữ/cú pháp/định dạng mà bạn ưu tiên, bạn có thể tự viết một cái!

<a id="template"></a>
## Mẫu (Template)

Dưới đây là một mẫu mà bạn có thể bắt đầu:

```go
package myadapter

import (
	"fmt"

	"github.com/caddyserver/caddy/v2/caddyconfig"
)

func init() {
	caddyconfig.RegisterAdapter("adapter_name", MyAdapter{})
}

// MyAdapter adapts ____ to Caddy JSON.
type MyAdapter struct{
}

// Adapt adapts the body to Caddy JSON.
func (a MyAdapter) Adapt(body []byte, options map[string]interface{}) ([]byte, []caddyconfig.Warning, error) {
	// TODO: parse body and convert it to JSON
	return nil, nil, fmt.Errorf("not implemented")
}
```

- Xem godoc cho [`RegisterAdapter()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#RegisterAdapter)
- Xem godoc cho interface ['Adapter'](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#Adapter)

JSON được trả về **không** nên được thụt lề; nó phải luôn ở dạng nén (compact). Người gọi luôn có thể làm đẹp nó nếu họ muốn.

Lưu ý rằng mặc dù các bộ điều hợp cấu hình là các _plugin_ của Caddy, chúng không phải là các _module_ của Caddy vì chúng không tích hợp vào một phần của cấu hình (nhưng chúng sẽ hiển thị trong `list-modules` để thuận tiện). Do đó, chúng không có các phương thức `Provision()` hoặc `Validate()` hoặc tuân theo phần còn lại của vòng đời module. Chúng chỉ cần triển khai interface `Adapter` và được đăng ký như là các bộ điều hợp.

Khi điền vào các trường của cấu hình là các kiểu `json.RawMessage` (tức là các trường module), hãy sử dụng các hàm `JSON()` và `JSONModuleObject()`:

- [`caddyconfig.JSON()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSON) dùng để chuyển đổi (marshaling) các giá trị module mà không nhúng tên module vào. (Thường được sử dụng cho các trường ModuleMap nơi tên module là khóa bản đồ.)
- [`caddyconfig.JSONModuleObject()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig?tab=doc#JSONModuleObject) dùng để chuyển đổi các giá trị module với tên module được thêm vào đối tượng. (Được sử dụng ở hầu hết các nơi khác.)


<a id="caddyfile-server-types"></a>
## Các loại Server Caddyfile

Cũng có thể triển khai một định dạng Caddyfile tùy chỉnh. Bộ điều hợp Caddyfile là một triển khai bộ điều hợp duy nhất và "loại server" mặc định của nó là HTTP, nhưng nó hỗ trợ các "loại server" thay thế khi đăng ký. Ví dụ, HTTP Caddyfile được đăng ký như sau:

```go
func init() {
	caddyconfig.RegisterAdapter("caddyfile",  caddyfile.Adapter{ServerType: ServerType{}})
}
```

Bạn sẽ triển khai [interface `caddyfile.ServerType`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#ServerType) và đăng ký bộ điều hợp của riêng bạn cho phù hợp.
