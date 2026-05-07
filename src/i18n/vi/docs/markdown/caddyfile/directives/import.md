---
title: import (chỉ thị Caddyfile)
---

# import

Bao gồm một [snippet](/docs/caddyfile/concepts#snippets) hoặc tệp, thay thế chỉ thị này bằng nội dung của snippet hoặc tệp đó.

Chỉ thị này là một trường hợp đặc biệt: nó được đánh giá trước khi cấu trúc được phân tích cú pháp và nó có thể xuất hiện ở bất kỳ đâu trong Caddyfile.

<a id="syntax"></a>
## Cú pháp

```caddy-d
import <pattern> [<args...>] [{block}]
```

- **&lt;pattern&gt;** là tên tệp, mẫu glob hoặc tên của [snippet](/docs/caddyfile/concepts#snippets) để bao gồm. Nội dung của nó sẽ thay thế dòng này giống như nội dung của tệp đó đã xuất hiện ở đây ngay từ đầu.

  Sẽ xảy ra lỗi nếu không tìm thấy một tệp cụ thể, nhưng một mẫu glob trống thì không phải là lỗi.

  Nếu nhập một tệp cụ thể, một cảnh báo sẽ được đưa ra nếu tệp đó trống.

  Nếu mẫu là một tên tệp hoặc glob, nó luôn luôn tương đối với tệp mà `import` xuất hiện.

  Nếu sử dụng mẫu glob `*` làm phân đoạn đường dẫn cuối cùng, các tệp ẩn (tức là các tệp bắt đầu bằng dấu `.`) sẽ bị bỏ qua. Để nhập các tệp ẩn, hãy sử dụng `.*` làm phân đoạn cuối cùng.
- **&lt;args...&gt;** là danh sách các đối số tùy chọn để truyền cho các token được nhập. Trình giữ chỗ này là một trường hợp đặc biệt và được đánh giá tại thời điểm phân tích cú pháp Caddyfile, chứ không phải tại thời điểm chạy. Chúng có thể được sử dụng ở nhiều dạng khác nhau, tương tự như [cú pháp slice của Go](https://gobyexample.com/slices):
  - `{args[n]}` trong đó `n` là chỉ số vị trí dựa trên 0 của tham số
  - `{args[:]}` trong đó tất cả các đối số được chèn vào
  - `{args[:m]}` trong đó các đối số trước `m` được chèn vào
  - `{args[n:]}` trong đó các đối số bắt đầu bằng `n` được chèn vào
  - `{args[n:m]}` trong đó các đối số trong phạm vi giữa `n` và `m` được chèn vào

  Đối với các dạng chèn nhiều token, trình giữ chỗ **phải** là một [token](/docs/caddyfile/concepts#tokens-and-quotes) riêng biệt, nó không thể là một phần của token khác. Nói cách khác, nó phải có khoảng trắng xung quanh và không thể nằm trong dấu ngoặc kép.

  Lưu ý rằng trước phiên bản v2.7.0, cú pháp là `{args.N}` nhưng dạng này đã bị loại bỏ để thay thế bằng cú pháp linh hoạt hơn ở trên.

⚠️ <i>Thử nghiệm</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>
- **{block}** là một khối tùy chọn để truyền cho các token được nhập. Trình giữ chỗ này là một trường hợp đặc biệt và được đánh giá đệ quy tại thời điểm phân tích cú pháp Caddyfile, chứ không phải tại thời điểm chạy. Chúng có thể được sử dụng ở hai dạng:
  - `{block}` trong đó nội dung của toàn bộ khối được cung cấp sẽ được thay thế cho trình giữ chỗ
  - `{blocks.key}` trong đó `key` là token đầu tiên của một tham số trong khối được cung cấp


<a id="examples"></a>
## Ví dụ

Nhập tất cả các tệp trong thư mục sites-enabled liền kề (ngoại trừ các tệp ẩn):

```caddy-d
import sites-enabled/*
```

Nhập một snippet thiết lập các tiêu đề CORS bằng cách sử dụng đối số import:

```caddy
(cors) {
	@origin header Origin {args[0]}
	header @origin Access-Control-Allow-Origin "{args[0]}"
	header @origin Access-Control-Allow-Methods "OPTIONS,HEAD,GET,POST,PUT,PATCH,DELETE"
}

example.com {
	import cors example.com
}
```

Nhập một snippet nhận danh sách các upstream proxy làm đối số:

```caddy
(https-proxy) {
	reverse_proxy {args[:]} {
		transport http {
			tls
		}
	}
}

example.com {
	import https-proxy 10.0.0.1 10.0.0.2 10.0.0.3
}
```

Nhập một snippet tạo một proxy với quy tắc ghi lại tiền tố làm đối số đầu tiên:

```caddy
(proxy-rewrite) {
	rewrite {args[0]}{uri}
	reverse_proxy {args[1:]}
}

example.com {
	import proxy-rewrite /api 10.0.0.1 10.0.0.2 10.0.0.3
}
```


⚠️ <i>Thử nghiệm</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Nhập một snippet phản hồi bằng thông báo "hello world" và content-type có thể định cấu hình:

```caddy
(hello-world) {
	header {
		Cache-Control max-age=3600
		X-Foo bar
		{blocks.content_type}
	}
	respond /hello-world 200 {
		{blocks.body}
	}
}

example.com {
	import hello-world {
		content_type {
			Content-Type text/html
		}
		body {
			body "<h1>hello world</h1>"
		}
	}
}
```

Nhập một snippet cung cấp các tùy chọn có thể mở rộng cho một reverse proxy:

```caddy
(extendable-proxy) {
	reverse_proxy {
		{blocks.proxy_target}
		{blocks.proxy_options}
	}
}

example.com {
	import extendable-proxy {
		proxy_target {
			to 10.0.0.1
		}
		proxy_options {
			transport http {
				tls
			}
		}
	}
}
```

Nhập một snippet phục vụ bất kỳ tập hợp chỉ thị nào, nhưng với một middleware được tải sẵn:

```caddy
(instrumented-route) {
	header {
		Alt-Svc `h3="0.0.0.0:443"; ma=2592000`
	}
	tracing {
		span args[0]
	}
	{block}
}

example.com {
	import instrumented-route example-com {
		respond "OK"
	}
}
```
