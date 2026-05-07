---
title: fs (Chỉ thị Caddyfile)
---

# fs

Thiết lập hệ thống tệp nào sẽ được sử dụng để thực hiện I/O tệp.

Điều này có thể cho phép bạn kết nối với một hệ thống tệp từ xa đang chạy trên đám mây, hoặc một cơ sở dữ liệu có giao diện giống tệp, hoặc thậm chí để đọc từ các tệp được nhúng bên trong tệp thực thi Caddy.

Trước tiên, bạn phải khai báo tên hệ thống tệp bằng cách sử dụng [tùy chọn toàn cục `filesystem`](/docs/caddyfile/options#filesystem), sau đó bạn có thể sử dụng chỉ thị này để chỉ định hệ thống tệp nào sẽ được sử dụng.

Chỉ thị này thường được sử dụng kết hợp với [chỉ thị `file_server`](file_server) để phục vụ các tệp tĩnh, hoặc [chỉ thị `try_files`](try_files) để thực hiện ghi lại (rewrites) dựa trên sự tồn tại của các tệp. Thường cũng được sử dụng với [chỉ thị `root`](root) để thiết lập đường dẫn gốc bên trong hệ thống tệp.


<a id="syntax"></a>
## Cú pháp

```caddy-d
fs [<matcher>] <filesystem>
```

<a id="examples"></a>
## Ví dụ

Sử dụng một hệ thống tệp có tên là `foo`, sử dụng một mô-đun giả tưởng có tên là `custom` có thể yêu cầu xác thực:

```caddy
{
	filesystem foo custom {
		api_key abc123
	}
}

example.com {
	fs foo
	root /srv
	file_server
}
```

Để chỉ phục vụ hình ảnh từ hệ thống tệp `foo`, và phần còn lại từ hệ thống tệp mặc định:

```caddy
example.com {
	fs /images* foo
	root /srv
	file_server
}
```
