---
title: templates (chỉ thị Caddyfile)
---

# templates

Thực thi phần thân phản hồi dưới dạng tài liệu [template](/docs/modules/http.handlers.templates). Các template cung cấp các thành phần chức năng để tạo các trang động đơn giản. Các tính năng bao gồm các yêu cầu con HTTP, bao gồm tệp HTML, kết xuất Markdown, phân tích cú pháp JSON, cấu trúc dữ liệu cơ bản, tính ngẫu nhiên, thời gian và nhiều tính năng khác.


<a id="syntax"></a>
## Cú pháp

```caddy-d
templates [<matcher>] {
	mime    <types...>
	between <open_delim> <close_delim>
	root    <path>
	extensions {
		<name> {
			...
		}
	}
}
```

- **mime** là các loại MIME mà middleware templates sẽ tác động; bất kỳ phản hồi nào không có `Content-Type` đủ điều kiện sẽ không được đánh giá là template.

  Mặc định: `text/html text/plain`.

- **between** là các dấu phân cách mở và đóng cho các hành động template. Bạn có thể thay đổi chúng nếu chúng gây xung đột với phần còn lại của tài liệu.

  Mặc định: `{{printf "{{ }}"}}`.

- **root** là gốc của trang web, khi sử dụng các hàm truy cập hệ thống tệp.

  Mặc định là gốc của trang web được đặt bởi chỉ thị [`root`](root), hoặc thư mục làm việc hiện tại nếu chưa được đặt.

- **extensions** cho phép bạn đăng ký các hàm template tùy chỉnh được cung cấp bởi các mô-đun trong không gian tên `http.handlers.templates.functions.*`.

  Mỗi chỉ thị con bên trong khối tương ứng với một tên mô-đun. Các mô-đun này có thể thêm các hàm tùy chỉnh vào bản đồ hàm template, thường được sử dụng để triển khai các thành phần có thể tái sử dụng. Tính năng này chủ yếu dành cho các plugin.

Tài liệu cho các hàm template tích hợp có thể được tìm thấy trong [mô-đun templates](/docs/modules/http.handlers.templates#docs).



<a id="examples"></a>
## Ví dụ

Để xem một ví dụ đầy đủ về một trang web sử dụng template để phục vụ markdown, hãy xem mã nguồn của [chính trang web này](https://github.com/caddyserver/website)! Cụ thể, hãy xem [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile) và [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html).

Bật templates cho một trang tĩnh:

```caddy
example.com {
	root /srv
	templates
	file_server
}
```

Để cung cấp một phản hồi tĩnh đơn giản bằng cách sử dụng template, hãy đảm bảo đặt `Content-Type`:

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `Current year is: {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

Sử dụng một phần mở rộng template (plugin):

```caddy
example.com {
	root /srv
	templates {
		extensions {
			# Requires the caddy-hitcounter plugin:
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
```
