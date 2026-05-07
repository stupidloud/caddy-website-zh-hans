---
title: request_body (chỉ thị Caddyfile)
---

# request_body

Thao tác hoặc thiết lập các hạn chế đối với nội dung (body) của các yêu cầu đến.

<a id="syntax"></a>
## Cú pháp

```caddy-d
request_body [<matcher>] {
	max_size <value>
	set <body_content>
}
```

- **max_size** là kích thước tối đa tính bằng byte được phép cho nội dung yêu cầu. Nó chấp nhận tất cả các giá trị kích thước được hỗ trợ bởi [go-humanize](https://pkg.go.dev/github.com/dustin/go-humanize#pkg-constants). Việc đọc nhiều byte hơn sẽ trả về lỗi với trạng thái HTTP `413`.

⚠️ <i>Thử nghiệm</i> <span style='white-space: pre;'> | </span> <span>v2.10.0+</span>
- **set** cho phép thiết lập nội dung yêu cầu thành nội dung cụ thể. Nội dung có thể bao gồm các trình giữ chỗ (placeholders) để chèn dữ liệu động.

<a id="examples"></a>
## Ví dụ

Giới hạn kích thước nội dung yêu cầu ở mức 10 megabytes:

```caddy
example.com {
	request_body {
		max_size 10MB
	}
	reverse_proxy localhost:8080
}
```

Thiết lập nội dung yêu cầu với cấu trúc JSON chứa truy vấn SQL:

```caddy
example.com {
	handle /jazz {
		request_body {
			set `\{"statementText":"SELECT name, genre, debut_year FROM artists WHERE genre = 'Jazz'"}`
		}

		reverse_proxy localhost:8080 {
			header_up Content-Type application/json
			method POST
			rewrite /execute-sql
		}
	}
}
