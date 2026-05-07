---
title: handle (Chỉ thị Caddyfile)
---

# handle

Thực thi một nhóm các chỉ thị loại trừ lẫn nhau với các khối `handle` khác ở cùng một mức độ lồng nhau.

Nói cách khác, khi nhiều chỉ thị `handle` xuất hiện theo trình tự, chỉ khối `handle` *khớp* đầu tiên mới được thực thi. Một handle không có bộ khớp (matcher) hoạt động giống như một tuyến đường *dự phòng* (fallback).

Các chỉ thị `handle` được sắp xếp theo [thuật toán sắp xếp chỉ thị](/docs/caddyfile/directives#sorting-algorithm) dựa trên các bộ khớp của chúng. Chỉ thị [`handle_path`](handle_path) là một trường hợp đặc biệt được sắp xếp cùng mức ưu tiên với một `handle` có bộ khớp đường dẫn.

Các khối Handle có thể lồng vào nhau nếu cần thiết. Chỉ các chỉ thị trình xử lý HTTP (HTTP handler directives) mới có thể được sử dụng bên trong các khối handle.

<a id="syntax"></a>
## Cú pháp

```caddy-d
handle [<matcher>] {
	<directives...>
}
```

- **<directives...>** là một danh sách các chỉ thị trình xử lý HTTP hoặc các khối chỉ thị, mỗi dòng một chỉ thị, giống như cách sử dụng bên ngoài khối handle.



<a id="similar-directives"></a>
## Các chỉ thị tương tự

Có các chỉ thị khác có thể bao bọc các chỉ thị trình xử lý HTTP, nhưng mỗi loại có mục đích sử dụng tùy thuộc vào hành vi bạn muốn truyền đạt:

- [`handle_path`](handle_path) thực hiện tương tự như `handle`, nhưng nó loại bỏ một tiền tố khỏi yêu cầu trước khi chạy các trình xử lý của nó.

- [`handle_errors`](handle_errors) giống như `handle`, nhưng chỉ được gọi khi Caddy gặp lỗi trong quá trình xử lý yêu cầu.

- [`route`](route) bao bọc các chỉ thị khác giống như `handle`, nhưng có hai điểm khác biệt:
  1. Các khối route không loại trừ lẫn nhau,
  2. Các chỉ thị bên trong một route không được [sắp xếp lại](/docs/caddyfile/directives#directive-order), giúp bạn kiểm soát nhiều hơn nếu cần.



<a id="examples"></a>
## Ví dụ

Xử lý các yêu cầu trong `/foo/` với máy chủ tệp tĩnh và các yêu cầu khác với proxy ngược:

```caddy
example.com {
	handle /foo/* {
		file_server
	}

	handle {
		reverse_proxy 127.0.0.1:8080
	}
}
```

Bạn có thể kết hợp `handle` và [`handle_path`](handle_path) trong cùng một trang web, và chúng vẫn sẽ loại trừ lẫn nhau:

```caddy
example.com {
	handle_path /foo/* {
		# Đường dẫn đã được loại bỏ tiền tố "/foo"
	}

	handle /bar/* {
		# Đường dẫn vẫn giữ lại "/bar"
	}
}
```

Bạn có thể lồng các khối `handle` để tạo logic định tuyến phức tạp hơn:

```caddy
example.com {
	handle /foo* {
		handle /foo/bar* {
			# Khối này chỉ khớp với các đường dẫn dưới /foo/bar
		}

		handle {
			# Khối này khớp với mọi thứ khác dưới /foo/
		}
	}

	handle {
		# Khối này khớp với mọi thứ khác (hoạt động như một dự phòng)
	}
}
