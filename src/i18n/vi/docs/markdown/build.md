---
title: "Xây dựng từ mã nguồn"
---

<a id="build-from-source"></a>
# Xây dựng từ mã nguồn

Có nhiều tùy chọn để xây dựng Caddy, nếu bạn cần một bản dựng tùy chỉnh (ví dụ: với các plugin):
- [Git](#git): Xây dựng từ kho lưu trữ Git
- [`xcaddy`](#xcaddy): Xây dựng bằng `xcaddy`
- [Docker](#docker): Xây dựng một Docker image tùy chỉnh

Yêu cầu:

- [Go](https://golang.org/doc/install) 1.20 hoặc mới hơn

Phần [Các tệp hỗ trợ gói](#package-support-files-for-custom-builds-for-debianubunturaspbian) chứa hướng dẫn cho những người dùng đã cài đặt Caddy bằng lệnh APT trên hệ thống phái sinh từ Debian nhưng cần tệp thực thi bản dựng tùy chỉnh cho các hoạt động của họ.



## Git

Yêu cầu:

- Đã cài đặt Go (xem ở trên)

Sao chép kho lưu trữ:

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

Nếu bạn không có git, bạn có thể tải xuống mã nguồn dưới dạng tệp nén [từ GitHub](https://github.com/caddyserver/caddy). Mỗi [bản phát hành](https://github.com/caddyserver/caddy/releases) cũng có các bản chụp mã nguồn (snapshots).

Xây dựng:

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>


<aside class="tip">

Do [một lỗi trong Go](https://github.com/golang/go/issues/29228), các bước cơ bản này không nhúng thông tin phiên bản. Nếu bạn muốn có phiên bản (`caddy version`), bạn cần biên dịch Caddy như một phụ thuộc (dependency) thay vì là mô-đun chính. Hướng dẫn cho việc này có trong tệp [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) của Caddy. Hoặc, bạn có thể sử dụng [`xcaddy`](#xcaddy) để tự động hóa việc này.

</aside>

Các chương trình Go rất dễ biên dịch cho các nền tảng khác. Chỉ cần đặt các biến môi trường `GOOS`, `GOARCH`, và/hoặc `GOARM` khác nhau. ([Xem tài liệu Go để biết thêm chi tiết.](https://golang.org/doc/install/source#environment))

Ví dụ, để biên dịch Caddy cho Windows khi bạn không ở trên Windows:

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

Hoặc tương tự cho Linux ARMv6 khi bạn không ở trên Linux hoặc trên ARMv6:

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



## xcaddy

Lệnh [`xcaddy`](https://github.com/caddyserver/xcaddy) là cách dễ nhất để xây dựng Caddy với thông tin phiên bản và/hoặc các plugin.

Yêu cầu:

- Đã cài đặt Go (xem ở trên)
- Đảm bảo [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) nằm trong `PATH` của bạn

Bạn **không** cần tải xuống mã nguồn Caddy (nó sẽ thực hiện việc đó cho bạn).

Sau đó, việc xây dựng Caddy (với thông tin phiên bản) trở nên đơn giản như:

<pre><code class="cmd bash">xcaddy build</code></pre>

Để xây dựng với các plugin, hãy sử dụng `--with`:

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter
	--with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

Như bạn thấy, bạn có thể tùy chỉnh phiên bản của các plugin bằng cú pháp `@`. Phiên bản có thể là tên thẻ (tag), mã băm xác nhận (commit SHA), hoặc nhánh (branch).

Biên dịch đa nền tảng với `xcaddy` hoạt động tương tự như với lệnh `go`. Ví dụ, để biên dịch chéo cho macOS:

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



## Docker

Bạn có thể sử dụng image `:builder` như một cách nhanh chóng để xây dựng một tệp thực thi Caddy mới với các mô-đun tùy chỉnh:

```Dockerfile
FROM caddy:<version>-builder AS builder

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
    --with github.com/hairyhenderson/caddy-teapot-module@v0.0.3-0

FROM caddy:<version>

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

Đảm bảo thay thế `<version>` bằng phiên bản mới nhất của Caddy để bắt đầu.

Lưu ý chỉ thị `FROM` thứ hai — điều này tạo ra một image nhỏ hơn nhiều bằng cách chỉ đơn giản là đặt tệp thực thi mới được xây dựng lên trên image `caddy` thông thường.

Trình xây dựng sử dụng `xcaddy` để xây dựng Caddy với các mô-đun được cung cấp, tương tự như quy trình [được phác thảo ở trên](#xcaddy). Các tùy chọn `--mount=type=cache,target=/go/pkg/mod` và `--mount=type=cache,target=/root/.cache/go-build` được sử dụng để lưu vào bộ nhớ đệm (cache) các phụ thuộc mô-đun Go và các sản phẩm xây dựng tương ứng, giúp tăng tốc các lần xây dựng tiếp theo. Cờ này là [một tính năng của Docker](https://docs.docker.com/build/cache/optimize/#use-cache-mounts), không phải của `xcaddy`.

Để sử dụng Docker Compose, hãy xem [`compose.yml`](/docs/running#docker-compose) được khuyến nghị của chúng tôi và hướng dẫn sử dụng.



<a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>
## Các tệp hỗ trợ gói cho các bản dựng tùy chỉnh cho Debian/Ubuntu/Raspbian

Thủ tục này nhằm đơn giản hóa việc chạy các tệp thực thi `caddy` tùy chỉnh trong khi vẫn giữ lại các tệp hỗ trợ từ gói `caddy`.

Thủ tục này cho phép người dùng tận dụng cấu hình mặc định, các tệp dịch vụ systemd và tính năng tự động hoàn thành bash từ gói chính thức.

Yêu cầu:
- Cài đặt gói `caddy` theo [các hướng dẫn này](/docs/install#debian-ubuntu-raspbian)
- Xây dựng tệp thực thi `caddy` tùy chỉnh của bạn (xem các phần trên), hoặc [tải xuống](/download) một bản dựng tùy chỉnh
- Tệp thực thi `caddy` tùy chỉnh của bạn phải nằm trong thư mục hiện tại

Thủ tục:
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

Giải thích:

- `dpkg-divert` sẽ di chuyển tệp thực thi `/usr/bin/caddy` sang `/usr/bin/caddy.default` và đặt một sự chuyển hướng tại chỗ trong trường hợp có bất kỳ gói nào muốn cài đặt một tệp vào vị trí này.

- `update-alternatives` sẽ tạo một liên kết biểu tượng (symlink) từ tệp thực thi caddy mong muốn đến `/usr/bin/caddy`.

- `systemctl restart caddy` sẽ tắt phiên bản mặc định của máy chủ Caddy và khởi động phiên bản tùy chỉnh.

Bạn có thể thay đổi giữa các tệp thực thi `caddy` tùy chỉnh và mặc định bằng cách thực thi lệnh bên dưới và làm theo thông tin trên màn hình. Sau đó, khởi động lại dịch vụ Caddy.

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

Để nâng cấp Caddy sau thời điểm này, bạn có thể chạy [`caddy upgrade`](/docs/command-line#caddy-upgrade). Lệnh này sẽ cố gắng [tải xuống](/download) một bản dựng với các plugin tương tự như bản dựng hiện tại của bạn, với phiên bản mới nhất của Caddy, sau đó thay thế tệp thực thi hiện tại bằng tệp mới.
