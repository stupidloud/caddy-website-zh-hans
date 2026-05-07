---
title: Caddyfile
---

<a id="the-caddyfile"></a>
# Caddyfile

**Caddyfile** là một định dạng cấu hình Caddy tiện lợi dành cho con người. Đây là cách được hầu hết mọi người ưa chuộng để sử dụng Caddy vì nó dễ viết, dễ hiểu và đủ linh hoạt cho phần lớn các trường hợp sử dụng.

Nó trông như thế này:

```caddy
example.com {
	root /var/www/wordpress
	encode
	php_fastcgi unix//run/php/php-version-fpm.sock
	file_server
}
```

(Đó là một Caddyfile thực tế, sẵn sàng cho môi trường sản xuất để phục vụ WordPress với HTTPS được quản lý hoàn toàn.)

Ý tưởng cơ bản là trước tiên bạn nhập địa chỉ trang web của mình, sau đó là các tính năng hoặc chức năng mà bạn cần trang web của mình có. [Xem thêm các mẫu phổ biến.](/docs/caddyfile/patterns)

<a id="menu"></a>
## Danh mục

- #### [Hướng dẫn bắt đầu nhanh](/docs/quick-starts/caddyfile)
  Một nơi tốt để bắt đầu làm quen với Caddyfile.
- #### [Hướng dẫn Caddyfile đầy đủ](/docs/caddyfile-tutorial)
  Học cách thực hiện nhiều công việc phổ biến với Caddyfile.
- #### [Các khái niệm Caddyfile](/docs/caddyfile/concepts)
  Bắt buộc phải đọc! Cấu trúc, địa chỉ trang web, trình so khớp (matchers), trình giữ chỗ (placeholders), và nhiều hơn nữa.
- #### [Chỉ thị (Directives)](/docs/caddyfile/directives)
  Các từ khóa ở đầu dòng giúp kích hoạt các tính năng cho trang web của bạn.
- #### [Trình so khớp yêu cầu (Request matchers)](/docs/caddyfile/matchers)
  Lọc các yêu cầu bằng cách sử dụng các trình so khớp với các chỉ thị của bạn.
- #### [Tùy chọn toàn cục (Global options)](/docs/caddyfile/options)
  Các cài đặt áp dụng cho toàn bộ máy chủ thay vì từng trang web riêng lẻ.
- #### [Các mẫu phổ biến](/docs/caddyfile/patterns)
  Những cách đơn giản để thực hiện các công việc thường gặp.
<!-- - #### [Thông số kỹ thuật Caddyfile](/docs/caddyfile/spec) TODO: Hoàn thành phần này -->


<a id="note"></a>
## Lưu ý

Caddyfile chỉ là một [config adapter](/docs/config-adapters) cho Caddy. Nó thường được ưu tiên khi soạn thảo cấu hình thủ công bằng tay, nhưng không linh hoạt, mạnh mẽ hoặc có khả năng lập trình bằng [cấu trúc JSON gốc](/docs/json/) của Caddy. Nếu bạn đang tự động hóa các cấu hình/triển khai Caddy của mình, bạn có thể muốn sử dụng JSON với [API của Caddy](/docs/api). (Thực tế bạn cũng có thể sử dụng Caddyfile với API, nhưng chỉ ở một mức độ hạn chế.)
