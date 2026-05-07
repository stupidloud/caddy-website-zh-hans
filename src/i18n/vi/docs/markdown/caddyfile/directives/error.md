---
title: error (Chỉ thị Caddyfile)
---

# error

Kích hoạt một lỗi trong chuỗi trình xử lý HTTP, với một thông báo tùy chọn và mã trạng thái HTTP được đề xuất. 

Trình xử lý này không viết phản hồi. Thay vào đó, nó được dùng để kết hợp với chỉ thị [`handle_errors`](handle_errors) để gọi logic xử lý lỗi tùy chỉnh của bạn.


<a id="syntax"></a>
## Cú pháp

```caddy-d
error [<matcher>] <status>|<message> [<status>] {
    message <text>
}
```

- **&lt;status&gt;** là mã trạng thái HTTP để ghi. Mặc định là `500`.
- **&lt;message&gt;** là thông báo lỗi. Mặc định là không có thông báo lỗi.
- **message** là một cách thay thế để cung cấp thông báo lỗi; thuận tiện nếu nó có nhiều dòng.

Để làm rõ, đối số không phải trình khớp (non-matcher) đầu tiên có thể là mã trạng thái gồm 3 chữ số hoặc chuỗi thông báo lỗi. Nếu đó là một thông báo lỗi, đối số tiếp theo có thể là mã trạng thái.


<a id="examples"></a>
## Ví dụ

Kích hoạt lỗi trên các đường dẫn yêu cầu nhất định và sử dụng [`handle_errors`](handle_errors) để viết phản hồi:

```caddy
example.com {
	root /srv

	# Kích hoạt lỗi cho các đường dẫn nhất định
    error /private* "Unauthorized" 403
	error /hidden* "Not found" 404

    # Xử lý lỗi bằng cách cung cấp một trang HTML 
    handle_errors {
        rewrite /{err.status_code}.html
		file_server
    }

	file_server
}
```
