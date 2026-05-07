---
title: "Hỗ trợ Caddyfile"
---

<a id="caddyfile-support"></a>
# Hỗ trợ Caddyfile

Các module Caddy được tự động thêm vào [cấu hình JSON gốc](/docs/json/) nhờ vào namespace của chúng khi được [đăng ký](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule), giúp chúng vừa có thể sử dụng vừa được ghi chép tài liệu. Điều này làm cho việc hỗ trợ Caddyfile là hoàn toàn tùy chọn, nhưng nó thường được yêu cầu bởi những người dùng thích Caddyfile.

## Unmarshaler

Để thêm hỗ trợ Caddyfile cho module của bạn, chỉ cần triển khai interface [`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler). Bạn có quyền chọn cú pháp Caddyfile mà module của bạn có bằng cách bạn phân tích các token.

Công việc của một unmarshaler chỉ đơn giản là thiết lập kiểu module của bạn, ví dụ: bằng cách điền các trường của nó, sử dụng [`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser) được truyền cho nó. Ví dụ, một kiểu module tên là `Gizmo` có thể có phương thức này:

```go
// UnmarshalCaddyfile triển khai caddyfile.Unmarshaler. Cú pháp:
//
// gizmo <name> [<option>]
//
func (g *Gizmo) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // tiêu thụ tên chỉ thị

	if !d.Args(&g.Name) {
		// không đủ đối số
		return d.ArgErr()
	}
	if d.NextArg() {
		// đối số tùy chọn
		g.Option = d.Val()
	}
	if d.NextArg() {
		// quá nhiều đối số
		return d.ArgErr()
	}

	return nil
}
```

Nên ghi lại cú pháp trong comment godoc cho phương thức. Xem [godoc cho package `caddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc) để biết thêm thông tin về việc phân tích Caddyfile.

Token tên chỉ thị (directive) có thể được tiêu thụ/bỏ qua bằng một lệnh gọi `d.Next()` đơn giản.

Hãy đảm bảo kiểm tra các đối số bị thiếu và/hoặc dư thừa bằng `d.NextArg()` hoặc `d.RemainingArgs()`. Sử dụng `d.ArgErr()` cho một thông báo "trường hợp không hợp lệ" đơn giản, hoặc sử dụng `d.Errf("some message")` để tạo một thông báo lỗi hữu ích kèm theo giải thích về vấn đề (và lý tưởng nhất là một giải pháp gợi ý).

Bạn cũng nên thêm một [interface guard](/docs/extending-caddy#interface-guards) để đảm bảo interface được thỏa mãn đúng cách:

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

<a id="blocks"></a>
### Khối (Blocks)

Để chấp nhận nhiều cấu hình hơn mức có thể chứa trên một dòng, bạn có thể muốn cho phép một khối với các chỉ thị con (subdirectives). Điều này có thể được thực hiện bằng cách sử dụng `d.NextBlock()` và lặp lại cho đến khi bạn quay trở lại mức lồng nhau ban đầu:

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

Miễn là mỗi lần lặp của vòng lặp tiêu thụ toàn bộ phân đoạn (dòng hoặc khối), thì đây là một cách trang nhã để xử lý các khối.

<a id="http-directives"></a>
## Các chỉ thị HTTP

HTTP Caddyfile là cú pháp bộ điều hợp Caddyfile mặc định của Caddy (hoặc "kiểu máy chủ"). Nó có thể mở rộng, nghĩa là bạn có thể [đăng ký](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterDirective) các chỉ thị "cấp cao nhất" của riêng bạn cho module của bạn:

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

Nếu chỉ thị của bạn chỉ trả về một trình xử lý HTTP duy nhất (như thường thấy), bạn có thể thấy [`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective) dễ dàng hơn:

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

Ý tưởng cơ bản là [hàm phân tích](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc) mà bạn liên kết với chỉ thị của mình sẽ trả về một hoặc nhiều giá trị [`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue). (Hoặc, nếu sử dụng `RegisterHandlerDirective`, nó chỉ đơn giản trả về trực tiếp giá trị `caddyhttp.MiddlewareHandler` đã được điền.) Mỗi giá trị cấu hình được liên kết với một ["lớp" (class)](#classes) giúp bộ điều hợp HTTP Caddyfile biết nó có thể được sử dụng trong (các) phần nào của cấu hình JSON cuối cùng. Tất cả các giá trị cấu hình được đổ vào một đống mà từ đó bộ điều hợp rút ra khi xây dựng cấu hình JSON cuối cùng.

Thiết kế này cho phép chỉ thị của bạn trả về bất kỳ giá trị cấu hình nào cho bất kỳ lớp nào được công nhận, điều đó có nghĩa là nó có thể ảnh hưởng đến bất kỳ phần nào của cấu hình mà bộ điều hợp HTTP Caddyfile có một lớp được chỉ định.

Nếu bạn đã triển khai phương thức `UnmarshalCaddyfile()`, thì hàm phân tích của bạn có thể đơn giản như:

```go
// parseCaddyfileHandler giải mã các token từ h thành một giá trị middleware handler mới.
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

Xem [godoc của package `httpcaddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc) để biết thêm thông tin về cách sử dụng kiểu `httpcaddyfile.Helper`.

<a id="handler-order"></a>
### Thứ tự trình xử lý

Tất cả các chỉ thị trả về các giá trị middleware/trình xử lý HTTP cần được đánh giá theo đúng thứ tự. Ví dụ, một trình xử lý thiết lập thư mục gốc của trang web phải đứng trước một trình xử lý truy cập thư mục gốc, để nó biết đường dẫn thư mục là gì.

HTTP Caddyfile [có thứ tự được mã hóa cứng cho các chỉ thị tiêu chuẩn](/docs/caddyfile/directives#directive-order). Điều này đảm bảo rằng người dùng không cần biết chi tiết triển khai của các chức năng phổ biến nhất của máy chủ web của họ và giúp họ viết các cấu hình chính xác dễ dàng hơn. Một danh sách duy nhất, được mã hóa cứng cũng ngăn chặn tính không xác định do tính chất có thể mở rộng của Caddyfile.

**Khi bạn đăng ký một chỉ thị trình xử lý mới, nó phải được thêm vào danh sách đó trước khi có thể được sử dụng (bên ngoài một khối `route`).** Điều này được thực hiện bằng một trong ba phương pháp:

- (Khuyến nghị) Tác giả plugin có thể gọi [`httpcaddyfile.RegisterDirectiveOrder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile#RegisterDirectiveOrder) trong `init()` sau khi đăng ký chỉ thị, để chèn chỉ thị vào thứ tự so với một [chỉ thị tiêu chuẩn](/docs/caddyfile/directives#directive-order) khác. Làm như vậy, người dùng có thể sử dụng chỉ thị trực tiếp trong các trang web của họ mà không cần thiết lập thêm. Ví dụ, để chèn chỉ thị `gizmo` của bạn để được đánh giá sau trình xử lý `header`:

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- Người dùng có thể thêm [tùy chọn toàn cục `order`](/docs/caddyfile/options) để sửa đổi thứ tự tiêu chuẩn cho Caddyfile của họ. Ví dụ: `order gizmo before respond` sẽ chèn một chỉ thị `gizmo` mới để được đánh giá trước trình xử lý `respond`. Sau đó, chỉ thị có thể được sử dụng bình thường.

- Người dùng có thể đặt chỉ thị trong một [khối `route`](/docs/caddyfile/directives/route). Vì các chỉ thị trong một khối route không được sắp xếp lại, các chỉ thị được sử dụng trong một khối route không cần phải xuất hiện trong danh sách.

Nếu bạn chọn một trong hai tùy chọn sau, vui lòng ghi lại khuyến nghị cho người dùng của bạn về vị trí thích hợp trong danh sách để chỉ thị của bạn được sắp xếp, để họ có thể sử dụng nó một cách chính xác.

<a id="classes"></a>
### Các lớp (Classes)

Bảng này mô tả từng lớp với các kiểu được export mà bộ điều hợp HTTP Caddyfile công nhận:

Tên lớp | Kiểu mong đợi | Mô tả
---------- | ------------- | -----------
bind | `[]string` | Địa chỉ liên kết trình lắng nghe máy chủ
route | `caddyhttp.Route` | Tuyến đường trình xử lý HTTP
error_route | `*caddyhttp.Subroute` | Tuyến đường xử lý lỗi HTTP
tls.connection_policy | `*caddytls.ConnectionPolicy` | Chính sách kết nối TLS
tls.cert_issuer | `certmagic.Issuer` | Nhà phát hành chứng chỉ TLS
tls.cert_loader | `caddytls.CertificateLoader` | Trình tải chứng chỉ TLS

<a id="server-types"></a>
## Các kiểu máy chủ

Về mặt cấu trúc, Caddyfile là một định dạng đơn giản, vì vậy có thể có các loại định dạng Caddyfile khác nhau (đôi khi được gọi là "kiểu máy chủ") để phù hợp với các nhu cầu khác nhau.

Định dạng Caddyfile mặc định là HTTP Caddyfile, có lẽ bạn đã quen thuộc. Định dạng này chủ yếu cấu hình [app `http`](/docs/modules/http) trong khi chỉ có thể rắc một số cấu hình ở các phần khác của cấu trúc cấu hình Caddy (ví dụ: app `tls` để tải và tự động hóa chứng chỉ).

Để cấu hình các app khác ngoài HTTP, bạn có thể muốn triển khai bộ điều hợp cấu hình của riêng mình bằng cách sử dụng [kiểu máy chủ của riêng bạn](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter). Bộ điều hợp Caddyfile thực sự sẽ phân tích đầu vào cho bạn và cung cấp cho bạn danh sách các khối máy chủ, và các tùy chọn, và việc bộ điều hợp của bạn có ý nghĩa gì đối với cấu trúc đó và biến nó thành cấu hình JSON là tùy thuộc vào bạn.
