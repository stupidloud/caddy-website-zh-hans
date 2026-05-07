---
title: uri (chỉ thị Caddyfile)
---

# uri

Thao tác URI của yêu cầu. Nó có thể loại bỏ tiền tố/hậu tố đường dẫn hoặc thay thế các chuỗi con trên toàn bộ URI.

Chỉ thị này khác với [`rewrite`](rewrite) ở chỗ `uri` thay đổi URI một cách _khác biệt_, thay vì đặt lại nó thành một thứ hoàn toàn khác như `rewrite` làm. Trong khi `rewrite` được xử lý đặc biệt như một chuyển hướng nội bộ, `uri` chỉ là một middleware thông thường.


<a id="syntax"></a>
## Cú pháp

Nhiều thao tác khác nhau được hỗ trợ:

```caddy-d
uri [<matcher>] strip_prefix <target>
uri [<matcher>] strip_suffix <target>
uri [<matcher>] replace      <target> <replacement> [<limit>]
uri [<matcher>] path_regexp  <target> <replacement>
uri [<matcher>] query        [-|+]<param> [<value>]
uri [<matcher>] query {
	<param> [<value>] [<replacement>]
	...
}
```

Đối số đầu tiên (không phải bộ khớp) chỉ định thao tác:

- **strip_prefix** loại bỏ tiền tố khỏi đường dẫn.

- **strip_suffix** loại bỏ hậu tố khỏi đường dẫn.

- **replace** thực hiện thay thế chuỗi con trên toàn bộ URI.

	- **&lt;target&gt;** là tiền tố, hậu tố, hoặc chuỗi tìm kiếm/biểu thức chính quy. Nếu là tiền tố, dấu gạch chéo đứng đầu có thể được bỏ qua, vì các đường dẫn luôn bắt đầu bằng dấu gạch chéo.

	- **&lt;replacement&gt;** là chuỗi thay thế. Hỗ trợ sử dụng các nhóm thu thập (capture groups) với cú pháp `$name` hoặc `${name}`, hoặc với một số cho chỉ mục, chẳng hạn như `$1`. Xem [tài liệu Go](https://golang.org/pkg/regexp/#Regexp.Expand) để biết chi tiết. Nếu giá trị thay thế là `""`, thì văn bản khớp sẽ bị xóa khỏi giá trị.

	- **&lt;limit&gt;** là giới hạn tùy chọn cho số lần thay thế tối đa.

- **path_regexp** thực hiện thay thế biểu thức chính quy trên phần đường dẫn của URI.

	- **&lt;target&gt;** là tiền tố, hậu tố, hoặc chuỗi tìm kiếm/biểu thức chính quy. Nếu là tiền tố, dấu gạch chéo đứng đầu có thể được bỏ qua, vì các đường dẫn luôn bắt đầu bằng dấu gạch chéo.

	- **&lt;replacement&gt;** là chuỗi thay thế. Hỗ trợ sử dụng các nhóm thu thập (capture groups) với cú pháp `$name` hoặc `${name}`, hoặc với một số cho chỉ mục, chẳng hạn như `$1`. Xem [tài liệu Go](https://golang.org/pkg/regexp/#Regexp.Expand) để biết chi tiết. Nếu giá trị thay thế là `""`, thì văn bản khớp sẽ bị xóa khỏi giá trị.

- **query** thực hiện các thao tác trên truy vấn (query) URI, với chế độ tùy thuộc vào tiền tố của tên tham số hoặc số lượng đối số. Một khối có thể được sử dụng để chỉ định nhiều thao tác cùng lúc, được nhóm và thực hiện theo thứ tự này: đổi tên (rename) 🡒 đặt (set) 🡒 thêm vào (append) 🡒 thay thế (replace) 🡒 xóa (delete).

	- Nếu không có tiền tố, tham số sẽ được đặt với giá trị đã cho trong truy vấn.
	
	  Ví dụ, `uri query foo bar` sẽ đặt giá trị của tham số `foo` thành `bar`.

	- Tiền tố với `-` để xóa tham số khỏi truy vấn.
	
	  Ví dụ, `uri query -foo` sẽ xóa tham số `foo` khỏi truy vấn.

	- Tiền tố với `+` để thêm một tham số vào truy vấn, với giá trị đã cho. Điều này sẽ _không_ ghi đè lên một tham số hiện có cùng tên (bỏ qua dấu `+` để ghi đè).
	
	  Ví dụ, `uri query +foo bar` sẽ thêm `foo=bar` vào truy vấn.

	- Một tham số với `>` làm trung tố (infix) sẽ đổi tên tham số thành giá trị sau dấu `>`. 
	
	  Ví dụ, `uri query foo>bar` sẽ đổi tên tham số `foo` thành `bar`.

	- Với ba đối số, việc thay thế biểu thức chính quy cho giá trị truy vấn được thực hiện, trong đó đối số đầu tiên là tên tham số truy vấn, đối số thứ hai là giá trị tìm kiếm, và đối số thứ ba là chuỗi thay thế. Đối số đầu tiên (tên tham số) có thể là `*` để thực hiện thay thế trên tất cả các tham số truy vấn.
	
	  Hỗ trợ sử dụng các nhóm thu thập với cú pháp `$name` hoặc `${name}`, hoặc với một số cho chỉ mục, chẳng hạn như `$1`. Xem [tài liệu Go](https://golang.org/pkg/regexp/#Regexp.Expand) để biết chi tiết. Nếu giá trị thay thế là `""`, thì văn bản khớp sẽ bị xóa khỏi giá trị.
	
	  Ví dụ, `uri query foo ^(ba)r $1z` sẽ thay thế giá trị của tham số `foo`, trong đó giá trị bắt đầu bằng `bar` dẫn đến giá trị trở thành `baz`.

Các thay đổi URI xảy ra trên dạng đã chuẩn hóa (normalized) hoặc chưa thoát (unescaped) của URI. Tuy nhiên, các chuỗi thoát (escape sequences) có thể được sử dụng trong các mẫu tiền tố hoặc hậu tố để chỉ khớp với các chuỗi thoát theo nghĩa đen tại các vị trí đó trong đường dẫn yêu cầu. Ví dụ, `uri strip_prefix /a/b` sẽ viết lại cả `/a/b/c` và `/a%2Fb/c` thành `/c`; và `uri strip_prefix /a%2Fb` sẽ viết lại `/a%2Fb/c` thành `/c`, nhưng sẽ không khớp với `/a/b/c`.

Đường dẫn URI được làm sạch các dấu chấm di chuyển thư mục (directory traversal dots) trước khi sửa đổi. Ngoài ra, nhiều dấu gạch chéo (chẳng hạn như `//`) được hợp nhất trừ khi `<target>` cũng chứa nhiều dấu gạch chéo.

<a id="similar-directives"></a>
## Các chỉ thị tương tự

Một số chỉ thị khác cũng có thể thao tác URI yêu cầu.

- [`rewrite`](rewrite) thay đổi toàn bộ đường dẫn và truy vấn thành một giá trị mới thay vì thay đổi một phần giá trị.

- [`handle_path`](handle_path) thực hiện tương tự như [`handle`](handle), nhưng nó loại bỏ một tiền tố khỏi yêu cầu trước khi chạy các trình xử lý (handlers) của nó. Có thể được sử dụng thay cho `uri strip_prefix` để loại bỏ một dòng cấu hình bổ sung trong nhiều trường hợp.


<a id="examples"></a>
## Ví dụ

Loại bỏ `/api` khỏi đầu tất cả các đường dẫn yêu cầu:

```caddy-d
uri strip_prefix /api
```

Loại bỏ `.php` khỏi cuối tất cả các đường dẫn yêu cầu:

```caddy-d
uri strip_suffix .php
```

Thay thế "/docs/" bằng "/v1/docs/" trong bất kỳ URI yêu cầu nào:

```caddy-d
uri replace /docs/ /v1/docs/
```

Thu gọn tất cả các dấu gạch chéo lặp lại trong đường dẫn yêu cầu (nhưng không phải trong truy vấn yêu cầu) thành một dấu gạch chéo duy nhất:

```caddy-d
uri path_regexp /{2,} /
```

Đặt giá trị của tham số truy vấn `foo` thành `bar`:

```caddy-d
uri query foo bar
```

Xóa tham số `foo` khỏi truy vấn:

```caddy-d
uri query -foo
```

Đổi tên tham số truy vấn `foo` thành `bar`:

```caddy-d
uri query foo>bar
```

Thêm tham số `bar` vào truy vấn:

```caddy-d
uri query +foo bar
```

Thay thế giá trị của tham số truy vấn `foo` trong đó giá trị bắt đầu bằng `bar` bằng `baz`:

```caddy-d
uri query foo ^(ba)r $1z
```

Thực hiện nhiều thao tác truy vấn cùng lúc:

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	renamethis>renamed
}
```
