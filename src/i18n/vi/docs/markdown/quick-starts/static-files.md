---
title: Hướng dẫn nhanh về tệp tĩnh
---

<a id="static-files-quick-start"></a>
# Hướng dẫn nhanh về tệp tĩnh

Hướng dẫn này sẽ chỉ cho bạn cách thiết lập và chạy một máy chủ tệp tĩnh sẵn sàng cho môi trường thực tế (production) một cách nhanh chóng.

**Điều kiện tiên quyết:**
- Kỹ năng cơ bản về terminal / dòng lệnh
- `caddy` trong PATH của bạn
- Một thư mục chứa trang web của bạn

---

Có hai cách dễ dàng để thiết lập và chạy một máy chủ tệp nhanh chóng.

<a id="command-line"></a>
## Dòng lệnh

Trong terminal của bạn, hãy chuyển đến thư mục gốc của trang web và chạy:

<pre><code class="cmd bash">caddy file-server</code></pre>

Nếu bạn gặp lỗi quyền truy cập, điều đó có thể có nghĩa là hệ điều hành của bạn không cho phép bạn liên kết với các cổng thấp -- vì vậy hãy sử dụng cổng cao để thay thế:

<pre><code class="cmd bash">caddy file-server --listen :2015</code></pre>

Sau đó mở [localhost](http://localhost) (hoặc [localhost:2015](http://localhost:2015)) trong trình duyệt của bạn để xem trang web!

Nếu bạn không có tệp index nhưng muốn hiển thị danh sách tệp, hãy sử dụng tùy chọn `--browse`:

<pre><code class="cmd bash">caddy file-server --browse</code></pre>

Bạn có thể sử dụng một thư mục khác làm gốc trang web:

<pre><code class="cmd bash">caddy file-server --root ~/mysite</code></pre>



## Caddyfile

Trong thư mục gốc của trang web, hãy tạo một tệp có tên là `Caddyfile` với nội dung sau:

```caddy
localhost

file_server
```

Nếu bạn không có quyền liên kết với các cổng thấp, hãy thay thế `localhost` bằng `localhost:2015` (hoặc một cổng cao khác).

Sau đó, từ cùng một thư mục đó, hãy chạy:

<pre><code class="cmd bash">caddy run</code></pre>

Sau đó, bạn có thể tải [localhost](https://localhost) (hoặc bất kỳ địa chỉ nào trong cấu hình của bạn) để xem trang web!

[Chỉ thị `file_server`](/docs/caddyfile/directives/file_server) có nhiều tùy chọn hơn để bạn tùy chỉnh trang web của mình. Hãy đảm bảo [tải lại (reload)](/docs/command-line#caddy-reload) Caddy (hoặc dừng và khởi động lại) khi bạn thay đổi Caddyfile!

Nếu bạn không có tệp index nhưng muốn hiển thị danh sách tệp, hãy sử dụng đối số `browse`:

```caddy
localhost

file_server browse
```

Bạn cũng có thể sử dụng một thư mục khác làm gốc trang web:

```caddy
localhost

root /var/www/mysite
file_server
```
