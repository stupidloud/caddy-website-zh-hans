---
title: respond (Chỉ thị Caddyfile)
---

# respond

Viết một phản hồi mã hóa cứng/tĩnh cho máy khách.

Nếu phần thân không trống, chỉ thị này sẽ thiết lập tiêu đề `Content-Type` nếu nó chưa được thiết lập. Giá trị mặc định là `text/plain; utf-8` trừ khi phần thân là một đối tượng hoặc mảng JSON hợp lệ, trong trường hợp đó nó được thiết lập thành `application/json`. Đối với tất cả các loại nội dung khác, hãy thiết lập Content-Type thích hợp một cách rõ ràng bằng cách sử dụng [chỉ thị `header`](/docs/caddyfile/directives/header).


<a id="syntax"></a>
## Cú pháp

```caddy-d
respond [<matcher>] <status>|<body> [<status>] {
	body <text>
	close
}
```

- **&lt;status&gt;** là mã trạng thái HTTP để viết.

  Nếu `103` (Early Hints), phản hồi sẽ được viết mà không có phần thân và chuỗi trình xử lý sẽ tiếp tục. (Các phản hồi HTTP `1xx` là thông tin, không phải là cuối cùng.)
  
  Mặc định: `200`

- **&lt;body&gt;** là phần thân phản hồi để viết.

- **body** là một cách thay thế để cung cấp phần thân; thuận tiện nếu nó có nhiều dòng.

- **close** sẽ đóng kết nối của máy khách với máy chủ sau khi viết phản hồi.

Để làm rõ, đối số không phải trình khớp đầu tiên có thể là mã trạng thái 3 chữ số hoặc chuỗi phần thân phản hồi. Nếu nó là một phần thân, đối số tiếp theo có thể là mã trạng thái.

<aside class="tip">

Phản hồi bằng mã trạng thái lỗi khác với việc trả về một lỗi trong chuỗi trình xử lý, vốn sẽ gọi các trình xử lý lỗi nội bộ.

</aside>


<a id="examples"></a>
## Ví dụ

Viết mã trạng thái 200 trống với phần thân trống cho tất cả các kiểm tra sức khỏe, và một phần thân phản hồi đơn giản cho tất cả các yêu cầu khác:

```caddy
example.com {
	respond /health-check 200
	respond "Hello, world!"
}
```

Viết một phản hồi lỗi và đóng kết nối:

<aside class="tip">

Bạn có thể thích sử dụng [chỉ thị `error`](error) thay thế, chỉ thị này sẽ kích hoạt một lỗi có thể được xử lý bằng [chỉ thị `handle_errors`](handle_errors).

</aside>

```caddy
example.com {
	respond /secret/* "Access denied" 403 {
		close
	}
}
```

Viết một phản hồi HTML, sử dụng [cú pháp heredoc](/docs/caddyfile/concepts#heredocs) để kiểm soát khoảng trắng, và cũng thiết lập tiêu đề `Content-Type` để khớp với phần thân phản hồi:

```caddy
example.com {
	header Content-Type text/html
	respond <<HTML
		<html>
			<head><title>Foo</title></head>
			<body>Foo</body>
		</html>
		HTML 200
}
```
