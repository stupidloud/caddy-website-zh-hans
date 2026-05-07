---
title: header (Chỉ thị Caddyfile)
---

# header

Thao tác các trường header của phản hồi HTTP. Nó có thể thiết lập (set), thêm (add) và xóa (delete) các giá trị header, hoặc thực hiện thay thế bằng biểu thức chính quy (regular expressions).

Theo mặc định, các thao tác header được thực hiện ngay lập tức trừ khi có bất kỳ header nào đang bị xóa (tiền tố `-`) hoặc đang thiết lập một giá trị mặc định (tiền tố `?`). Trong những trường hợp đó, các thao tác header sẽ tự động được trì hoãn (deferred) cho đến khi chúng được ghi vào máy khách.

Để thao tác các header của yêu cầu (request headers) HTTP, bạn có thể sử dụng chỉ thị [`request_header`](request_header).


<a id="syntax"></a>
## Cú pháp

```caddy-d
header [<matcher>] [[+|-|?|>]<field> [<value>|<find>] [<replace>]] {
	# Add
	+<field> <value>

	# Set
	<field> <value>

	# Set with defer
	><field> <value>

	# Delete
	-<field>

	# Replace
	<field> <find> <replace>

	# Replace with defer
	><field> <find> <replace>

	# Default
	?<field> <value>

	[defer]

	match <inline_response_matcher>
}
```

- **&lt;field&gt;** là tên của trường header.

  Nếu không có tiền tố, trường sẽ được thiết lập (ghi đè).

  Sử dụng tiền tố `+` để thêm trường thay vì ghi đè (thiết lập) trường nếu nó đã tồn tại; các trường header có thể xuất hiện nhiều lần trong một phản hồi.

  Sử dụng tiền tố `-` để xóa trường. Trường có thể sử dụng các ký tự đại diện `*` ở tiền tố hoặc hậu tố để xóa tất cả các trường khớp.

  Sử dụng tiền tố `?` để thiết lập một giá trị mặc định cho trường. Trường chỉ được ghi nếu nó chưa tồn tại.

  Sử dụng tiền tố `>` để thiết lập trường và bật `defer`, như một phím tắt.

- **&lt;value&gt;** là giá trị của trường header, khi thêm hoặc thiết lập một trường.

- **&lt;find&gt;** là biểu thức chính quy cần tìm kiếm. Các trình giữ chỗ (placeholders) có thể được sử dụng cho đầu vào động vào mẫu tìm kiếm. Ngôn ngữ biểu thức chính quy được sử dụng là RE2, được bao gồm trong Go. Xem [tài liệu tham khảo cú pháp RE2](https://github.com/google/re2/wiki/Syntax) và [tổng quan cú pháp regexp của Go](https://pkg.go.dev/regexp/syntax).

- **&lt;replace&gt;** là giá trị thay thế; bắt buộc nếu thực hiện tìm kiếm và thay thế. Sử dụng `$1` hoặc `$2`, v.v. để tham chiếu các nhóm thu thập (capture groups) từ mẫu tìm kiếm. Nếu giá trị thay thế là `""`, thì văn bản khớp sẽ bị xóa khỏi giá trị. Xem [tài liệu Go](https://golang.org/pkg/regexp/#Regexp.Expand) để biết thêm chi tiết.

- **defer** trì hoãn việc thực thi các thao tác header cho đến khi phản hồi được gửi đến máy khách. Tùy chọn này được tự động bật trong các điều kiện sau:
	- Khi bất kỳ trường header nào bị xóa bằng `-`.
	- Khi thiết lập giá trị mặc định bằng `?`.
	- Khi sử dụng tiền tố `>` cho một thao tác thiết lập hoặc thay thế.
	- Khi có một hoặc nhiều điều kiện `match` hiện diện.

- **match** <span id="match"/> là một trình khớp phản hồi (response matcher) [nội dòng](/docs/caddyfile/response-matchers). Các thao tác header chỉ được áp dụng cho các phản hồi thỏa mãn các điều kiện được chỉ định.

Đối với nhiều thao tác header, bạn có thể mở một khối và chỉ định mỗi thao tác trên một dòng theo cùng một cách.

Khi sử dụng tiền tố `?` để thiết lập giá trị header mặc định, nó sẽ tự động được tách thành bộ xử lý `header` riêng, nếu nó nằm trong một khối `header` có nhiều thao tác header. [Bên dưới](/docs/modules/http.handlers.headers#response/require), việc sử dụng `?` sẽ cấu hình một [trình khớp phản hồi](/docs/caddyfile/response-matchers) áp dụng cho toàn bộ bộ xử lý của chỉ thị, chỉ áp dụng các thao tác header (như `defer`), nhưng chỉ khi trường đó chưa được thiết lập.


<a id="examples"></a>
## Ví dụ

Thiết lập một trường header tùy chỉnh trên tất cả các phản hồi:

```caddy-d
header Custom-Header "My value"
```

Loại bỏ trường header "Hidden":

```caddy-d
header -Hidden
```

Thay thế `http://` bằng `https://` trong bất kỳ header Location nào:

```caddy-d
header Location http:// https://
```

Thiết lập các header bảo mật và quyền riêng tư trên tất cả các trang: (**CẢNH BÁO:** chỉ sử dụng nếu bạn hiểu rõ các tác động!)

```caddy-d
header {
	# vô hiệu hóa theo dõi FLoC
	Permissions-Policy interest-cohort=()

	# bật HSTS
	Strict-Transport-Security max-age=31536000;

	# vô hiệu hóa việc máy khách tự ý đoán kiểu media
	X-Content-Type-Options nosniff

	# bảo vệ chống clickjacking
	X-Frame-Options DENY
}
```

Nhiều chỉ thị header được dự định loại trừ lẫn nhau:

```caddy-d
route {
	header           Cache-Control max-age=3600
	header /static/* Cache-Control max-age=31536000
}
```

Thiết lập thời gian hết hạn bộ nhớ đệm mặc định nếu máy chủ thượng nguồn không xác định:

```caddy-d
header ?Cache-Control "max-age=3600"
reverse_proxy upstream:443
```

Đánh dấu tất cả các phản hồi thành công cho yêu cầu GET là có thể lưu vào bộ nhớ đệm lên đến một giờ:

```caddy-d
@GET method GET
header @GET Cache-Control "max-age=3600" {
	match status 2xx
}
reverse_proxy upstream:443
```

Ngăn chặn lưu bộ nhớ đệm các phản hồi lỗi trong trường hợp có ngoại lệ ở máy chủ thượng nguồn:

```caddy-d
header {
	-Cache-Control
	-CDN-Cache-Control
	match status 500
}
reverse_proxy upstream:443
```

Đánh dấu các phản hồi chế độ sáng (light mode) có thể lưu vào bộ nhớ đệm riêng biệt với các phản hồi chế độ tối (dark mode) nếu máy chủ thượng nguồn hỗ trợ gợi ý của máy khách (client hints):
```caddy-d
header {
	Cache-Control "max-age=3600"
	Vary "Sec-CH-Prefers-Color-Scheme"
	match {
		header Accept-CH "*Sec-CH-Prefers-Color-Scheme*"
		header Critical-CH "Sec-CH-Prefers-Color-Scheme"
	}
}
reverse_proxy upstream:443
```

Ngăn chặn các header CORS quá lỏng lẻo bằng cách thay thế các giá trị ký tự đại diện bằng một tên miền cụ thể:
```caddy-d
header >Access-Control-Allow-Origin "\*" "allowed-partner.com"
reverse_proxy upstream:443
```
**Lưu ý**: Trong các thao tác thay thế, giá trị `<find>` được hiểu là một biểu thức chính quy. Để khớp với ký tự `*`, nó phải được thoát bằng dấu gạch chéo ngược như được trình bày trong ví dụ trên.

Ngoài ra, bạn có thể sử dụng [trình khớp phản hồi](/docs/caddyfile/response-matchers) để khớp chính xác giá trị header:
```caddy-d
header Access-Control-Allow-Origin "allowed-partner.com" {
	match header Access-Control-Allow-Origin *
}
reverse_proxy upstream:443
```

Để ghi đè thời gian hết hạn bộ nhớ đệm mà máy chủ thượng nguồn proxy đã thiết lập cho các đường dẫn bắt đầu bằng `/no-cache`; việc bật `defer` là cần thiết để đảm bảo header được thiết lập _sau khi_ proxy ghi các header của nó:

```caddy-d
header /no-cache* >Cache-Control no-cache
reverse_proxy upstream:443
```

Để thực hiện cập nhật trì hoãn của header `Set-Cookie` nhằm thêm `SameSite=None`; một biểu thức chính quy thu thập được sử dụng để lấy giá trị hiện có, và `$1` chèn lại nó vào đầu với tùy chọn bổ sung được thêm vào sau:

```caddy-d
header >Set-Cookie (.*) "$1; SameSite=None;"
```
