---
title: root (Chỉ thị Caddyfile)
---

# root

Thiết lập đường dẫn gốc của trang web, được sử dụng bởi các trình khớp (matcher) và chỉ thị (directive) khác nhau khi truy cập hệ thống tệp. Nếu không được thiết lập, thư mục làm việc hiện tại sẽ là gốc của trang web mặc định.

Cụ thể, chỉ thị này thiết lập trình giữ chỗ (placeholder) `{http.vars.root}`. Nó loại trừ lẫn nhau với các chỉ thị `root` khác trong cùng một khối, vì vậy việc định nghĩa nhiều gốc với các trình khớp giao nhau là an toàn: chúng sẽ không xếp chồng và ghi đè lên nhau.

Chỉ thị này không tự động bật tính năng phục vụ các tệp tĩnh, vì vậy nó thường được sử dụng kết hợp với [chỉ thị `file_server`](file_server) hoặc [chỉ thị `php_fastcgi`](php_fastcgi).


<a id="syntax"></a>
## Cú pháp

```caddy-d
root [<matcher>] <path>
```

- **&lt;path&gt;** là đường dẫn được sử dụng làm gốc cho trang web.

Trước phiên bản v2.8.0, đối số `<path>` có thể bị bộ phân tích cú pháp nhầm lẫn với một [token trình khớp](/docs/caddyfile/matchers#syntax) nếu nó bắt đầu bằng `/`, vì vậy cần phải chỉ định một token trình khớp đại diện (wildcard matcher token) (`*`).


<a id="examples"></a>
## Ví dụ

Thiết lập gốc của trang web thành `/home/bob/public_html` (giả định Caddy đang chạy dưới quyền người dùng `bob`):

<aside class="tip">

Nếu bạn đang chạy Caddy dưới dạng dịch vụ systemd, việc đọc các tệp từ `/home` sẽ không hoạt động vì người dùng `caddy` không có quyền "thực thi" (executable) trên thư mục `/home` (cần thiết để duyệt qua). Bạn nên đặt các tệp của mình trong `/srv` hoặc `/var/www/html`.

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

Lưu ý rằng trước phiên bản v2.8.0, một [trình khớp đại diện](/docs/caddyfile/matchers#wildcard-matchers) được yêu cầu ở đây vì đối số đầu tiên dễ bị nhầm lẫn với một [trình khớp đường dẫn](/docs/caddyfile/matchers#path-matchers), ví dụ: `root * /srv`, nhưng hiện tại nó có thể được đơn giản hóa thành `root /srv`.

</aside>


Thiết lập gốc của trang web thành `public_html` (tương đối với thư mục làm việc hiện tại) cho tất cả các yêu cầu:

```caddy-d
root public_html
```

Chỉ thay đổi gốc của trang web cho các yêu cầu trong `/foo/*`:

```caddy-d
root /foo/* /home/user/public_html/foo
```

Chỉ thị `root` thường được kết hợp với [`file_server`](file_server) để phục vụ các tệp tĩnh và/hoặc với [`php_fastcgi`](php_fastcgi) để phục vụ một trang web PHP:

```caddy
example.com {
	root /srv
	file_server
}
```
