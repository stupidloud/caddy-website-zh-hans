---
title: abort (chỉ thị Caddyfile)
---

# abort

Ngăn chặn bất kỳ phản hồi nào cho client bằng cách hủy bỏ chuỗi xử lý HTTP ngay lập tức và đóng kết nối. Bất kỳ luồng HTTP hiện thời, đang hoạt động nào trên cùng một kết nối đều bị gián đoạn.


<a id="syntax"></a>
## Cú pháp

```caddy-d
abort [<matcher>]
```

<a id="examples"></a>
## Ví dụ

Đóng kết nối một cách cưỡng bức khi nhận được yêu cầu từ các tên miền không xác định khi sử dụng chứng chỉ wildcard:

```caddy
*.example.com {
    @foo host foo.example.com
    handle @foo {
        respond "This is foo!" 200
    }

    handle {
		# Các tên miền không được xử lý rơi xuống đây,
		# nhưng chúng ta không muốn chấp nhận các yêu cầu của chúng
        abort
    }
}
```