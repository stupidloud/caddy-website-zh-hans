---
title: log_skip (Chỉ thị Caddyfile)
---

# log_skip

Bỏ qua việc ghi nhật ký truy cập (access logging) cho các yêu cầu (requests) khớp với điều kiện.

Chỉ thị này nên được sử dụng cùng với [chỉ thị `log`](log) để bỏ qua việc ghi nhật ký cho các yêu cầu không cần thiết cho nhu cầu của bạn.

Trước phiên bản v2.8.0, chỉ thị này có tên là `skip_log`, nhưng đã được đổi tên để thống nhất với các chỉ thị khác.


<a id="syntax"></a>
## Cú pháp

```caddy-d
log_skip [<matcher>]
```


<a id="examples"></a>
## Ví dụ

Bỏ qua ghi nhật ký truy cập cho các tệp tĩnh được lưu trữ trong một đường dẫn con:

```caddy
example.com {
	root /srv

	log
	log_skip /static*

	file_server
}
```


Bỏ qua ghi nhật ký truy cập cho các yêu cầu khớp với một mẫu (pattern); trong trường hợp này là cho các tệp có phần mở rộng cụ thể:

```caddy-d
@skip path_regexp \.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```


Bộ khớp (matcher) là không cần thiết nếu nó nằm trong một tuyến đường (route) đã có bộ khớp. Ví dụ, với một handle cho máy chủ tệp cho một đường dẫn con cụ thể:

```caddy-d
handle_path /static* {
	root /srv/static
	log_skip
	file_server
}
```
