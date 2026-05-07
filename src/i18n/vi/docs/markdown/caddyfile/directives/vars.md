---
title: vars (chỉ thị Caddyfile)
---

# vars

Thiết lập một hoặc nhiều biến cho một giá trị cụ thể, để sử dụng sau này trong chuỗi xử lý yêu cầu.

Cách chính để truy cập các biến là sử dụng các trình giữ chỗ (placeholders), có dạng `{vars.variable_name}`, hoặc với các trình so khớp yêu cầu [`vars`](/docs/caddyfile/matchers#vars) và [`vars_regexp`](/docs/caddyfile/matchers#vars_regexp).

Bạn có thể sử dụng các biến với chỉ thị [`templates`](templates) bằng cách sử dụng hàm `placeholder`, ví dụ: `{{ "{{placeholder \"http.vars.variable_name\"}}" }}`

Trong một trường hợp đặc biệt, có thể ghi đè biến có tên `http.auth.user.id`, được lưu trữ trong trình thay thế (replacer), để cập nhật trường `user_id` trong [nhật ký truy cập](log).


<a id="syntax"></a>
## Cú pháp

```caddy-d
vars [<matcher>] [<name> <value>] {
    <name> <value>
    ...
}
```

- **&lt;name&gt;** là tên biến cần thiết lập.

- **&lt;value&gt;** là giá trị của biến.

  Giá trị sẽ được chuyển đổi kiểu dữ liệu nếu có thể; `true` và `false` sẽ được chuyển đổi thành kiểu boolean, và các giá trị số sẽ được chuyển đổi thành số nguyên hoặc số thực tương ứng. Để tránh việc chuyển đổi này và giữ chúng dưới dạng chuỗi, bạn có thể bao quanh chúng bằng [dấu ngoặc kép](/docs/caddyfile/concepts#tokens-and-quotes).

<a id="examples"></a>
## Ví dụ

Để thiết lập một biến duy nhất, với giá trị có điều kiện dựa trên đường dẫn yêu cầu, sau đó phản hồi với giá trị đó:

```caddy
example.com {
	vars /foo* isFoo "yep"
	vars isFoo "nope"

	respond {vars.isFoo}
}
```

Để thiết lập nhiều biến, mỗi biến được chuyển đổi sang kiểu vô hướng thích hợp:

```caddy-d
vars {
	# boolean
	abc true

	# integer
	def 1

	# float
	ghi 2.3

	# string
	jkl "example"
}
```
