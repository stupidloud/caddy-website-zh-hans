---
title: Hướng dẫn nhanh về Railway
---

<a id="railway-quick-start"></a>
# Hướng dẫn nhanh về Railway

Triển khai Caddy trên Railway là một cách dễ dàng và không rắc rối để triển khai bản build Caddy tùy chỉnh kèm theo các plugin.

**Điều kiện tiên quyết:**
- Một tài khoản [Railway](https://railway.com) miễn phí

<a id="deploy-caddy-on-railway"></a>
## Triển khai Caddy trên Railway

Truy cập [trang Tải xuống](/download) của chúng tôi và chọn bất kỳ plugin nào bạn cần, sau đó nhấp vào nút "Deploy on Railway" màu tím ở trên cùng.

<details>
	<summary>Hoặc cấu hình template theo cách thủ công</summary>

Ngoài ra, nếu bạn muốn tự cấu hình template Railway, đây là cách thực hiện.

Truy cập template trên Railway:

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

và thêm bất kỳ plugin nào bạn cần bằng cách nhấp vào "Configure":

![Màn hình triển khai](/resources/images/railway/deploy-screen.png)

Sau đó dán các plugin vào biến `CADDY_PLUGINS`, cách nhau bằng dấu cách:

![Thêm plugin](/resources/images/railway/deploy-config.png)

</details>

Nhấp vào Deploy, sau đó sau khi quá trình triển khai hoàn tất, bạn có thể dùng thử bằng cách nhấp vào liên kết tại đây:

![Truy cập bản triển khai của bạn](/resources/images/railway/prod-link.png)

Bạn sẽ thấy một trang chào mừng cho biết máy chủ mới của bạn đang hoạt động!

Tiếp theo, bạn có thể tùy chỉnh bản triển khai của mình để phục vụ trang web của riêng bạn hoặc làm proxy cho một dịch vụ Railway khác.

<a id="customize-the-deployment"></a>
## Tùy chỉnh bản triển khai

Để phục vụ trang web của riêng bạn hoặc để thay đổi cấu hình, chỉ cần "eject" (tách) [template của chúng tôi](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic) vào kho lưu trữ (repository) của riêng bạn:

![Eject template](/resources/images/railway/eject.png)

Từ kho lưu trữ của riêng bạn, bạn có thể:

- Đưa trang web của riêng bạn vào thư mục `www`.
- Sửa đổi cấu hình của Caddy, chính là [Caddyfile](/docs/caddyfile).

Chỉ cần commit các thay đổi và push, sau đó bạn có thể triển khai lại trên Railway.

Nếu bạn muốn thay đổi các plugin trong bản build Caddy của mình, tất cả những gì bạn cần làm là chỉnh sửa biến `CADDY_PLUGINS` và triển khai lại:

![Thay đổi plugin](/resources/images/railway/plugins-variable.png)

<a id="tips"></a>
## Mẹo

Railway xử lý chấm dứt TLS cho bạn, vì vậy bạn nên viết cấu hình Caddy của mình như thể nó đang được chuyển tiếp proxy (vì thực tế là như vậy). Do đó, nếu bạn sử dụng host trong các địa chỉ trang web Caddyfile của mình, bạn nên sử dụng `auto_https off` trong các tùy chọn toàn cục (global options). Caddy không đóng vai trò trực tiếp đối mặt với internet (edge-facing) với template của chúng tôi.


<a id="variables"></a>
## Các biến

Các biến môi trường mà bạn có thể thiết lập trong dự án Railway của mình mà template này có thể sử dụng:

Tên | Mô tả | Mặc định | Ví dụ
---- | ----------- | ------- | ----------
`CADDY_PLUGINS` | Danh sách các plugin Caddy cách nhau bởi dấu cách | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
