---
title: Hướng dẫn nhanh về Caddyfile
---

<a id="caddyfile-quick-start"></a>
# Hướng dẫn nhanh về Caddyfile

Tạo một tệp văn bản mới có tên là `Caddyfile` (không có phần mở rộng).

Điều đầu tiên cần nhập vào Caddyfile là địa chỉ trang web của bạn:

```caddy
localhost
```

<aside class="tip">

Nếu các cổng HTTP và HTTPS (lần lượt là 80 và 443) là các cổng đặc quyền trên hệ điều hành của bạn, bạn sẽ cần chạy với quyền nâng cao hoặc sử dụng các cổng cao hơn. Để được cấp quyền, hãy chạy với tư cách root bằng `sudo -E` hoặc sử dụng `sudo setcap cap_net_bind_service=+ep $(which caddy)`. Ngoài ra, để sử dụng các cổng cao hơn, chỉ cần thay đổi địa chỉ thành một địa chỉ như `localhost:2080` và thay đổi cổng HTTP bằng tùy chọn Caddyfile [`http_port`](/docs/caddyfile/options).

</aside>

Sau đó nhấn enter và nhập những gì bạn muốn nó thực hiện, để nó trông như thế này:

```caddy
localhost

respond "Hello, world!"
```

Lưu tệp này và chạy Caddy từ cùng một thư mục chứa tệp Caddyfile của bạn:

<pre><code class="cmd bash">caddy start</code></pre>

Bạn có thể sẽ được yêu cầu nhập mật khẩu, vì Caddy cung cấp tất cả các trang web -- ngay cả các trang cục bộ -- qua HTTPS theo mặc định. (Yêu cầu mật khẩu chỉ xảy ra lần đầu tiên!)

<aside class="tip">

Đối với HTTPS cục bộ, Caddy tự động tạo chứng chỉ và khóa riêng duy nhất cho bạn. Chứng chỉ gốc được thêm vào kho lưu trữ tin cậy của hệ thống, đó là lý do tại sao yêu cầu mật khẩu là cần thiết. Nó cho phép bạn phát triển cục bộ qua HTTPS mà không gặp lỗi chứng chỉ.

</aside>

(Nếu bạn gặp lỗi về quyền, bạn có thể cần chạy với quyền nâng cao hoặc chọn một cổng cao hơn 1023.)

Hãy mở trình duyệt của bạn tới [localhost](http://localhost) hoặc sử dụng `curl`:

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Hello, world!</code></pre>

Bạn có thể định nghĩa nhiều trang web trong một Caddyfile bằng cách bao quanh chúng trong dấu ngoặc nhọn `{ }`. Thay đổi Caddyfile của bạn thành:

```caddy
localhost {
	respond "Hello, world!"
}

localhost:2016 {
	respond "Goodbye, world!"
}
```

Bạn có thể cung cấp cho Caddy cấu hình đã cập nhật theo hai cách, bằng API trực tiếp:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

hoặc bằng lệnh reload, lệnh này sẽ thực hiện cùng một yêu cầu API cho bạn:

<pre><code class="cmd bash">caddy reload</code></pre>

Hãy thử điểm cuối "goodbye" mới của bạn [trong trình duyệt](https://localhost:2016) hoặc bằng `curl` để đảm bảo nó hoạt động:

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Goodbye, world!</code></pre>

Khi bạn hoàn tất với Caddy, hãy đảm bảo dừng nó:

<pre><code class="cmd bash">caddy stop</code></pre>

<a id="further-reading"></a>
## Đọc thêm

- [Các khái niệm Caddyfile](/docs/caddyfile/concepts)
- [Các chỉ thị](/docs/caddyfile/directives)
- [Các mẫu phổ biến](/docs/caddyfile/patterns)
