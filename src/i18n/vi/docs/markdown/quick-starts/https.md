---
title: Bắt đầu nhanh với HTTPS
---

<a id="https-quick-start"></a>
# Bắt đầu nhanh với HTTPS

Hướng dẫn này sẽ chỉ cho bạn cách thiết lập và chạy [HTTPS được quản lý hoàn toàn](/docs/automatic-https) trong thời gian ngắn.

<aside class="tip">
	Caddy sử dụng HTTPS cho tất cả các trang web theo mặc định, miễn là tên máy chủ được cung cấp trong cấu hình. Hướng dẫn này giả định rằng bạn muốn đưa một trang web được tin cậy công khai (nghĩa là không phải "localhost") lên qua HTTPS, vì vậy chúng tôi sẽ sử dụng tên miền công khai và các cổng bên ngoài.
</aside>

**Điều kiện tiên quyết:**
- Kỹ năng sử dụng terminal / dòng lệnh cơ bản
- Hiểu biết cơ bản về DNS
- Một tên miền công khai đã đăng ký
- Quyền truy cập bên ngoài vào các cổng 80 và 443
- `caddy` và `curl` trong PATH của bạn

---

Trong hướng dẫn này, hãy thay thế `example.com` bằng tên miền thực của bạn.

Đặt bản ghi A/AAAA của miền của bạn trỏ đến máy chủ của bạn. Bạn có thể thực hiện việc này bằng cách đăng nhập vào nhà cung cấp DNS và quản lý tên miền của mình.

Trước khi tiếp tục, hãy xác minh các bản ghi chính xác bằng một tra cứu có thẩm quyền. Thay thế `example.com` bằng tên miền của bạn và nếu bạn đang sử dụng IPv6, hãy thay thế `type=A` bằng `type=AAAA`:

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=example.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

Đồng thời đảm bảo máy chủ của bạn có thể truy cập được từ bên ngoài trên các cổng 80 và 443 từ một giao diện công khai.

<aside class="tip">
	Nếu bạn đang ở mạng gia đình hoặc mạng bị hạn chế khác, bạn có thể cần chuyển tiếp cổng hoặc điều chỉnh cài đặt tường lửa.
</aside>

Tất cả những gì chúng ta phải làm là khởi động Caddy với tên miền của bạn trong cấu hình. Có một vài cách để làm việc này.

## Caddyfile

Đây là cách phổ biến nhất để có HTTPS.

Tạo một tệp có tên là `Caddyfile` (không có phần mở rộng) trong đó dòng đầu tiên là tên miền của bạn, ví dụ:

```caddy
example.com

respond "Hello, privacy!"
```

Sau đó, từ cùng một thư mục, chạy:

<pre><code class="cmd bash">caddy run</code></pre>

Bạn sẽ thấy Caddy cung cấp chứng chỉ TLS và phục vụ trang web của bạn qua HTTPS. Điều này khả thi vì địa chỉ trang web của bạn trong Caddyfile có chứa một tên miền.


<a id="the-command"></a>
<a id="the-file-server-command"></a>
## Lệnh `file-server`

Nếu tất cả những gì bạn cần là phục vụ các tệp tĩnh qua HTTPS, hãy chạy lệnh này (thay thế tên miền của bạn):

<pre><code class="cmd bash">caddy file-server --domain example.com</code></pre>

Bạn sẽ thấy Caddy cung cấp chứng chỉ TLS và phục vụ trang web của bạn qua HTTPS.


<a id="the-command"></a>
<a id="the-reverse-proxy-command"></a>
## Lệnh `reverse-proxy`

Nếu tất cả những gì bạn cần là một bản proxy ngược đơn giản qua HTTPS (dưới dạng bộ kết thúc TLS), hãy chạy lệnh này (thay thế tên miền của bạn và địa chỉ backend thực tế):

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to localhost:9000</code></pre>

Bạn sẽ thấy Caddy cung cấp chứng chỉ TLS và phục vụ trang web của bạn qua HTTPS.


<a id="json-config"></a>
## Cấu hình JSON

Quy tắc chung là bất kỳ [trình khớp máy chủ (host matcher)](/docs/json/apps/http/servers/routes/match/host/) nào cũng sẽ kích hoạt HTTPS tự động.

Do đó, một cấu hình JSON như sau sẽ bật [HTTPS tự động](/docs/automatic-https) sẵn sàng cho môi trường thực tế:

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["example.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Hello, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
