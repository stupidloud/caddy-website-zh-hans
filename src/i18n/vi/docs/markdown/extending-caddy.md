---
title: "Mở rộng Caddy"
---

<a id="extending-caddy"></a>
# Mở rộng Caddy

Caddy rất dễ mở rộng nhờ kiến trúc dạng mô-đun (modular architecture). Hầu hết các loại phần mở rộng (hoặc plugin) của Caddy được gọi là các *module* nếu chúng mở rộng hoặc cắm vào cấu trúc cấu hình của Caddy. Để làm rõ, các module của Caddy khác biệt với [Go modules](https://github.com/golang/go/wiki/Modules) (nhưng chúng cũng là các Go module).

**Điều kiện tiên quyết:**
- Hiểu biết cơ bản về [kiến trúc của Caddy](/docs/architecture)
- Thành thạo ngôn ngữ Go
- [`go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://golang.org/doc/install)
- [`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/xcaddy)


<a id="quick-start"></a>
## Bắt đầu nhanh

Một module Caddy là bất kỳ kiểu dữ liệu có tên nào tự đăng ký là một module Caddy khi gói (package) của nó được nhập (import). Quan trọng là, một module luôn triển khai interface [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module), interface này cung cấp tên của nó và một hàm khởi tạo (constructor).

Trong một Go module mới, hãy dán mẫu sau vào một tệp Go và tùy chỉnh tên package, tên kiểu dữ liệu và ID module Caddy của bạn:

```go
package mymodule

import "github.com/caddyserver/caddy/v2"

func init() {
	caddy.RegisterModule(Gizmo{})
}

// Gizmo là một ví dụ; hãy đặt kiểu dữ liệu của riêng bạn ở đây.
type Gizmo struct {
}

// CaddyModule trả về thông tin module Caddy.
func (Gizmo) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "foo.gizmo",
		New: func() caddy.Module { return new(Gizmo) },
	}
}
```

Sau đó, chạy lệnh này từ thư mục dự án của bạn và bạn sẽ thấy module của mình trong danh sách:

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">

[Lệnh `xcaddy`](https://github.com/caddyserver/xcaddy) là một phần quan trọng trong quy trình làm việc của mọi nhà phát triển module. Nó biên dịch Caddy cùng với plugin của bạn, sau đó chạy nó với các đối số được cung cấp. Nó sẽ loại bỏ tệp thực thi tạm thời mỗi lần (tương tự như `go run`).

</aside>


Chúc mừng, module của bạn đã đăng ký với Caddy và có thể được sử dụng trong [tài liệu cấu hình của Caddy](/docs/json/) ở bất kỳ nơi nào sử dụng module trong cùng một namespace.

Về cơ bản, `xcaddy` chỉ đơn giản là tạo ra một Go module mới yêu cầu cả Caddy và plugin của bạn (với một lệnh `replace` phù hợp để sử dụng phiên bản phát triển cục bộ của bạn), sau đó thêm một lệnh import để đảm bảo nó được biên dịch vào:

```go
import _ "github.com/example/mymodule"
```


<a id="module-basics"></a>
## Cơ bản về Module

Các module Caddy:

1. Triển khai interface `caddy.Module` để cung cấp ID và hàm khởi tạo
2. Có tên duy nhất trong namespace thích hợp
3. Thường thỏa mãn một số interface có ý nghĩa đối với module máy chủ (host module) cho namespace đó

**Host modules** (hoặc *parent modules*) là các module tải/khởi tạo các module khác. Chúng thường định nghĩa các namespace cho các module khách (guest modules).

**Guest modules** (hoặc *child modules*) là các module được tải hoặc khởi tạo. Tất cả các module đều là module khách.


<a id="module-ids"></a>
## ID của Module

Mỗi module Caddy có một ID duy nhất, bao gồm một namespace và một tên:

- Một ID đầy đủ trông giống như `foo.bar.module_name`
- Namespace sẽ là `foo.bar`
- Tên sẽ là `module_name`, tên này phải là duy nhất trong namespace của nó

ID Module phải sử dụng quy ước `snake_case`.

<a id="namespaces"></a>
### Namespace

Namespace giống như các lớp (classes), nghĩa là một namespace định nghĩa một số chức năng chung cho tất cả các module bên trong nó. Ví dụ, chúng ta có thể mong đợi rằng tất cả các module trong namespace `http.handlers` đều là các trình xử lý HTTP (HTTP handlers). Từ đó, một module máy chủ có thể ép kiểu (type-assert) các module khách trong namespace đó từ kiểu `interface{}` sang một kiểu cụ thể, hữu ích hơn như `caddyhttp.MiddlewareHandler`.

Một module khách phải được đặt trong namespace đúng cách để được module máy chủ nhận diện, vì các module máy chủ sẽ yêu cầu Caddy cung cấp các module trong một namespace nhất định để cung cấp chức năng mà module máy chủ mong muốn. Ví dụ: nếu bạn viết một module trình xử lý HTTP có tên là `gizmo`, tên module của bạn sẽ là `http.handlers.gizmo`, vì ứng dụng `http` sẽ tìm kiếm các trình xử lý trong namespace `http.handlers`.

Nói cách khác, các module Caddy được mong đợi sẽ triển khai [các interface nhất định](/docs/extending-caddy/namespaces) tùy thuộc vào namespace của module đó. Với quy ước này, các nhà phát triển module có thể nói những điều trực quan như: "Tất cả các module trong namespace `http.handlers` đều là các trình xử lý HTTP." Về mặt kỹ thuật hơn, điều này thường có nghĩa là: "Tất cả các module trong namespace `http.handlers` đều triển khai interface `caddyhttp.MiddlewareHandler`." Bởi vì tập hợp các phương thức đó đã được biết trước, kiểu cụ thể hơn có thể được khẳng định và sử dụng.

**[Xem bảng ánh xạ tất cả các namespace tiêu chuẩn của Caddy sang các kiểu Go của chúng.](/docs/extending-caddy/namespaces)**

Các namespace `caddy` và `admin` được dự phòng và không thể là tên ứng dụng.

Để viết các module cắm vào các module máy chủ của bên thứ ba, hãy tham khảo tài liệu về namespace của các module đó.

<a id="names"></a>
### Tên

Tên trong một namespace có ý nghĩa quan trọng và hiển thị rõ ràng với người dùng, nhưng không đặc biệt quan trọng, miễn là nó duy nhất, súc tích và có ý nghĩa đối với những gì nó thực hiện.


<a id="app-modules"></a>
## Module Ứng dụng (App Modules)

Ứng dụng là các module có namespace trống, và theo quy ước sẽ trở thành namespace cấp cao nhất của riêng chúng. Các module ứng dụng triển khai interface [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App).

Các module này xuất hiện trong thuộc tính [`"apps"`](/docs/json/#apps) ở cấp cao nhất của cấu hình Caddy:

```json
{
	"apps": {}
}
```

Ví dụ về các [ứng dụng](/docs/json/apps/) là `http` và `tls`. Namespace của chúng là trống.

Các module khách được viết cho các ứng dụng này nên nằm trong một namespace được dẫn xuất từ tên ứng dụng. Ví dụ: trình xử lý HTTP sử dụng namespace `http.handlers` và trình tải chứng chỉ TLS sử dụng namespace `tls.certificates`.

<a id="module-implementation"></a>
## Triển khai Module

Một module hầu như có thể là bất kỳ kiểu dữ liệu nào, nhưng struct là phổ biến nhất vì chúng có thể chứa cấu hình của người dùng.


<a id="configuration"></a>
### Cấu hình

Hầu hết các module yêu cầu một số cấu hình. Caddy tự động xử lý việc này, miễn là kiểu dữ liệu của bạn tương thích với JSON. Do đó, nếu một module là kiểu struct, nó sẽ cần các thẻ struct (struct tags) trên các trường của nó, các thẻ này nên sử dụng `snake_casing` theo quy ước của Caddy:

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

Sử dụng tùy chọn `omitempty` trong thẻ struct sẽ loại bỏ trường đó khỏi đầu ra JSON nếu nó là giá trị mặc định (zero value) cho kiểu dữ liệu của nó. Điều này hữu ích để giữ cho cấu hình JSON sạch sẽ và súc tích khi được tuần tự hóa (ví dụ: chuyển đổi từ Caddyfile sang JSON).

Khi một module được khởi tạo, nó sẽ được điền sẵn cấu hình. Cũng có thể thực hiện các bước [cung cấp (provisioning)](#provisioning) và [xác thực (validating)](#validating) bổ sung sau khi module được khởi tạo.


<a id="module-lifecycle"></a>
### Vòng đời của Module

Cuộc đời của một module bắt đầu khi nó được tải bởi một module máy chủ. Những việc sau đây sẽ xảy ra:

1. [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New) được gọi để lấy một phiên bản (instance) giá trị của module.
2. Cấu hình của module được giải tuần tự hóa (unmarshaled) vào phiên bản đó.
3. Nếu module là một [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner), phương thức `Provision()` sẽ được gọi.
4. Nếu module là một [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator), phương thức `Validate()` sẽ được gọi.
5. Tại thời điểm này, module máy chủ được cung cấp module khách đã tải dưới dạng giá trị `interface{}`, vì vậy module máy chủ thường sẽ ép kiểu module khách sang một kiểu hữu ích hơn. Kiểm tra tài liệu cho module máy chủ để biết module khách trong namespace của nó yêu cầu những gì, ví dụ: những phương thức nào cần được triển khai.
6. Khi một module không còn cần thiết nữa, và nếu nó là một [`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#CleanerUpper), phương thức `Cleanup()` sẽ được gọi.

Lưu ý rằng nhiều phiên bản đã tải của module có thể chồng chéo nhau tại một thời điểm nhất định! Trong quá trình thay đổi cấu hình, các module mới được khởi động trước khi các module cũ bị dừng. Hãy chắc chắn sử dụng trạng thái toàn cục (global state) một cách cẩn thận. Sử dụng kiểu [`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool) để giúp quản lý trạng thái toàn cục giữa các lần tải module. Nếu module của bạn lắng nghe trên một socket, hãy sử dụng `caddy.Listen*()` để lấy một socket hỗ trợ việc sử dụng chồng chéo.

<a id="provisioning"></a>
### Cung cấp (Provisioning)

Cấu hình của một module sẽ tự động được giải tuần tự hóa vào giá trị của nó (khi tải cấu hình JSON). Điều này có nghĩa là, ví dụ, các trường struct sẽ được điền sẵn cho bạn.

Tuy nhiên, nếu module của bạn yêu cầu các bước cung cấp bổ sung, bạn có thể triển khai interface (tùy chọn) [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner):

```go
// Provision thiết lập module.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO: thiết lập module
	return nil
}
```

Đây là nơi bạn nên đặt giá trị mặc định cho các trường không được người dùng cung cấp (các trường không phải là giá trị mặc định của chúng). Nếu một trường là bắt buộc, bạn có thể trả về lỗi nếu nó không được thiết lập. Đối với các trường số mà giá trị 0 có ý nghĩa (ví dụ: một khoảng thời gian timeout), bạn có thể muốn hỗ trợ `-1` để có nghĩa là "tắt" thay vì `0`, vì vậy bạn có thể đặt giá trị mặc định nếu người dùng không cấu hình nó.

Đây cũng thường là nơi các module máy chủ sẽ tải các module khách/con của chúng.

Một module có thể truy cập các ứng dụng khác bằng cách gọi `ctx.App()`, nhưng các module không được có sự phụ thuộc vòng. Nói cách khác, một module được tải bởi ứng dụng `http` không thể phụ thuộc vào ứng dụng `tls` nếu một module được tải bởi ứng dụng `tls` phụ thuộc vào ứng dụng `http`. (Rất giống với các quy tắc cấm nhập vòng trong Go.)

Ngoài ra, bạn nên tránh thực hiện các thao tác tốn kém trong `Provision`, vì việc cung cấp được thực hiện ngay cả khi cấu hình chỉ đang được xác thực. Khi đang ở giai đoạn cung cấp, đừng kỳ vọng rằng module thực sự sẽ được sử dụng.

<a id="logs"></a>
#### Nhật ký (Logs)

Xem [cách ghi nhật ký hoạt động](/docs/logging) trong Caddy. Nếu module của bạn cần ghi nhật ký, đừng sử dụng `log.Print*()` từ thư viện tiêu chuẩn của Go. Nói cách khác, **không sử dụng logger toàn cục của Go**. Caddy sử dụng tính năng ghi nhật ký có cấu trúc, hiệu suất cao, linh hoạt cao với [zap](https://github.com/uber-go/zap).

Để xuất nhật ký, hãy lấy một logger trong phương thức Provision của module:

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger là một *zap.Logger
}
```

Sau đó, bạn có thể xuất các nhật ký có cấu trúc, phân cấp bằng cách sử dụng `g.logger`. Xem [tài liệu zap](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger) để biết thêm chi tiết.


<a id="validating"></a>
### Xác thực (Validating)

Các module muốn xác thực cấu hình của mình có thể làm như vậy bằng cách thỏa mãn interface (tùy chọn) [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator):

```go
// Validate xác thực rằng module có cấu hình có thể sử dụng được.
func (g Gizmo) Validate() error {
	// TODO: xác thực thiết lập của module
	return nil
}
```

Validate nên là một hàm chỉ đọc. Nó được chạy sau phương thức `Provision()`.


<a id="interface-guards"></a>
### Bảo vệ interface (Interface guards)

Hành vi của module Caddy là ngầm định vì các interface trong Go được thỏa mãn một cách ngầm định. Việc chỉ cần thêm các phương thức phù hợp vào kiểu dữ liệu của module là tất cả những gì cần thiết để tạo nên hoặc phá vỡ tính đúng đắn của module. Do đó, việc viết sai chính tả hoặc sai chữ ký phương thức có thể dẫn đến hành vi không mong muốn (hoặc thiếu sót).

May mắn thay, có một cách kiểm tra thời gian biên dịch dễ dàng, không tốn tài nguyên mà bạn có thể thêm vào mã của mình để đảm bảo bạn đã thêm các phương thức chính xác. Chúng được gọi là bảo vệ interface (interface guards):

```go
var _ InterfaceName = (*YourType)(nil)
```

Thay thế `InterfaceName` bằng interface bạn dự định thỏa mãn và `YourType` bằng tên kiểu dữ liệu module của bạn.

Ví dụ: một trình xử lý HTTP chẳng hạn như máy chủ tệp tĩnh có thể thỏa mãn nhiều interface:

```go
// Interface guards
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

Điều này ngăn chương trình biên dịch nếu `*FileServer` không thỏa mãn các interface đó.

Nếu không có bảo vệ interface, các lỗi khó hiểu có thể lọt vào. Ví dụ, nếu module của bạn phải tự cung cấp trước khi được sử dụng nhưng phương thức `Provision()` của bạn có lỗi (ví dụ: viết sai tên hoặc sai chữ ký), việc cung cấp sẽ không bao giờ xảy ra, dẫn đến khó hiểu. Bảo vệ interface cực kỳ dễ dàng và có thể ngăn chặn điều đó. Chúng thường được đặt ở cuối tệp.


<a id="host-modules"></a>
## Module máy chủ (Host Modules)

Một module trở thành module máy chủ khi nó tải các module khách của riêng mình. Điều này hữu ích nếu một phần chức năng của module có thể được triển khai theo nhiều cách khác nhau.

Một module máy chủ hầu như luôn luôn là một struct. Thông thường, việc hỗ trợ một module khách yêu cầu hai trường struct: một trường để chứa JSON thô của nó và một trường khác để chứa giá trị đã giải mã của nó:

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

Trường đầu tiên (`GadgetRaw` trong ví dụ này) là nơi có thể tìm thấy dạng JSON thô, chưa được cung cấp của module khách.

Trường thứ hai (`Gadget`) là nơi lưu trữ giá trị cuối cùng đã được cung cấp. Vì trường thứ hai không hướng tới người dùng, chúng tôi loại trừ nó khỏi JSON bằng một thẻ struct. (Bạn cũng có thể không xuất nó nếu các gói khác không cần nó, và sau đó không cần thẻ struct.)

<a id="caddy-struct-tags"></a>
### Thẻ struct Caddy (Caddy struct tags)

Thẻ struct `caddy` trên trường module thô giúp Caddy biết namespace và tên (tạo nên ID đầy đủ) của module cần tải. Nó cũng được sử dụng để tạo tài liệu.

Thẻ struct có định dạng rất đơn giản: `key1=val1 key2=val2 ...`

Đối với các trường module, thẻ struct sẽ trông giống như:

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

Phần `namespace=` là bắt buộc. Nó định nghĩa namespace để tìm kiếm module.

Phần `inline_key=` chỉ được sử dụng nếu tên của module sẽ được tìm thấy *cùng hàng* (inline) với chính module đó; điều này ngụ ý rằng giá trị là một đối tượng trong đó một trong các khóa là *khóa cùng hàng*, và giá trị của nó là tên của module. Nếu bỏ qua, thì kiểu dữ liệu của trường phải là một [`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap) hoặc `[]caddy.ModuleMap`, trong đó khóa bản đồ là tên module.


<a id="loading-guest-modules"></a>
### Tải các module khách

Để tải một module khách, hãy gọi [`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule) trong giai đoạn cung cấp:

```go
// Provision thiết lập g và tải gadget của nó.
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

Lưu ý rằng lệnh gọi `LoadModule()` nhận một con trỏ tới struct và tên trường dưới dạng một chuỗi. Kỳ lạ phải không? Tại sao không truyền trực tiếp trường struct? Đó là bởi vì có một vài cách khác nhau để tải các module tùy thuộc vào bố cục của cấu hình. Chữ ký phương thức này cho phép Caddy sử dụng kỹ thuật phản chiếu (reflection) để tìm ra cách tốt nhất để tải module và quan trọng nhất là đọc các thẻ struct của nó.

If a guest module must explicitly be set by the user, you should return an error if the Raw field is nil or empty before trying to load it.

Lưu ý cách module đã tải được ép kiểu: `g.Gadget = val.(Gadgeter)` - điều này là do `val` được trả về là kiểu `interface{}`, kiểu này không hữu ích lắm. Tuy nhiên, chúng tôi hy vọng rằng tất cả các module trong namespace đã khai báo (`foo.gizmo.gadgets` từ thẻ struct trong ví dụ của chúng tôi) đều triển khai interface `Gadgeter`, vì vậy việc ép kiểu này là an toàn, và sau đó chúng ta có thể sử dụng nó!

Nếu module máy chủ của bạn định nghĩa một namespace mới, hãy chắc chắn cung cấp tài liệu cho cả namespace đó và (các) kiểu Go của nó cho các nhà phát triển [như chúng tôi đã làm ở đây](/docs/extending-caddy/namespaces).

<a id="module-documentation"></a>
## Tài liệu về Module

Đăng ký module để module Caddy mới hiển thị trong tài liệu về module và có sẵn tại http://caddyserver.com/download. Việc đăng ký có sẵn tại http://caddyserver.com/account. Tạo một tài khoản mới nếu bạn chưa có và nhấp vào "Register package".

<a id="complete-example"></a>
## Ví dụ hoàn chỉnh

Giả sử chúng ta muốn viết một module trình xử lý HTTP. Đây sẽ là một middleware mô phỏng phục vụ mục đích trình diễn, in địa chỉ IP của khách truy cập vào một luồng trên mỗi yêu cầu HTTP.

Chúng tôi cũng muốn nó có thể định cấu hình thông qua Caddyfile, vì hầu hết mọi người thích sử dụng Caddyfile trong các tình huống không tự động hóa. Chúng tôi thực hiện việc này bằng cách đăng ký một chỉ thị trình xử lý Caddyfile (Caddyfile handler directive), đây là một loại chỉ thị có thể thêm trình xử lý vào lộ trình HTTP. Chúng tôi cũng triển khai interface `caddyfile.Unmarshaler`. Bằng cách thêm vài dòng mã này, module này có thể được cấu hình bằng Caddyfile! Ví dụ: `visitor_ip stdout`.

Dưới đây là mã cho một module như vậy, với các bình luận giải thích:

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

// Middleware triển khai một trình xử lý HTTP ghi lại
// địa chỉ IP của khách truy cập vào một tệp hoặc luồng.
type Middleware struct {
	// Tệp hoặc luồng để ghi vào. Có thể là "stdout"
	// hoặc "stderr".
	Output string `json:"output,omitempty"`

	w io.Writer
}

// CaddyModule trả về thông tin module Caddy.
func (Middleware) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "http.handlers.visitor_ip",
		New: func() caddy.Module { return new(Middleware) },
	}
}

// Provision triển khai caddy.Provisioner.
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

// Validate triển khai caddy.Validator.
func (m *Middleware) Validate() error {
	if m.w == nil {
		return fmt.Errorf("no writer")
	}
	return nil
}

// ServeHTTP triển khai caddyhttp.MiddlewareHandler.
func (m Middleware) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	m.w.Write([]byte(r.RemoteAddr))
	return next.ServeHTTP(w, r)
}

// UnmarshalCaddyfile triển khai caddyfile.Unmarshaler.
func (m *Middleware) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // tiêu thụ tên chỉ thị

	// yêu cầu một đối số
	if !d.NextArg() {
		return d.ArgErr()
	}

	// lưu trữ đối số
	m.Output = d.Val()
	return nil
}

// parseCaddyfile giải tuần tự hóa các token từ h vào một Middleware mới.
func parseCaddyfile(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var m Middleware
	err := m.UnmarshalCaddyfile(h.Dispenser)
	return m, err
}

// Interface guards
var (
	_ caddy.Provisioner           = (*Middleware)(nil)
	_ caddy.Validator             = (*Middleware)(nil)
	_ caddyhttp.MiddlewareHandler = (*Middleware)(nil)
	_ caddyfile.Unmarshaler       = (*Middleware)(nil)
)
```
