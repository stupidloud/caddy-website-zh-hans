---
title: Hướng dẫn nhanh về reverse proxy
---

<a id="reverse-proxy-quick-start"></a>
# Hướng dẫn nhanh về reverse proxy

Hướng dẫn này sẽ cho bạn thấy cách khởi chạy nhanh chóng một reverse proxy sẵn sàng cho môi trường production, có hoặc không có HTTPS.

**Điều kiện tiên quyết:**
- Kỹ năng cơ bản về terminal / dòng lệnh
- Có `caddy` trong PATH của bạn
- Một tiến trình backend đang chạy để proxy tới

---

Hướng dẫn này giả định rằng bạn có một dịch vụ HTTP backend đang chạy tại `127.0.0.1:9000`. Các lệnh này dành cho Linux, nhưng các nguyên tắc tương tự cũng áp dụng cho các hệ điều hành khác.

Bạn có thể chạy một reverse proxy đơn giản mà không cần file cấu hình, hoặc bạn có thể sử dụng file cấu hình để linh hoạt và kiểm soát tốt hơn.


<a id="command-line"></a>
## Dòng lệnh

Để bắt đầu một proxy HTTP văn bản thuần (plaintext) từ cổng 2080 đến cổng 9000 trên máy của bạn:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

Sau đó hãy thử nó:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Lệnh [`reverse-proxy`](/docs/command-line#reverse-proxy) được thiết kế cho các reverse proxy nhanh chóng và dễ dàng. (Bạn có thể sử dụng nó trong môi trường production nếu các yêu cầu của bạn đơn giản.)

## Caddyfile

Trong thư mục làm việc hiện tại, hãy tạo một file có tên là `Caddyfile` với nội dung sau:

```caddy
:2080

reverse_proxy :9000
```

File cấu hình đó tương đương với lệnh `caddy reverse-proxy` ở trên.

Sau đó, từ cùng thư mục đó, hãy chạy:

<pre><code class="cmd bash">caddy run</code></pre>

Sau đó hãy thử proxy của bạn:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Nếu bạn thay đổi Caddyfile, hãy đảm bảo [reload](/docs/command-line#caddy-reload) Caddy.

Đây là một ví dụ đơn giản. Bạn có thể làm được nhiều hơn thế với [chỉ thị `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

<a id="https-from-client-to-proxy"></a>
## HTTPS từ client đến proxy

Caddy sẽ cung cấp proxy của bạn qua [HTTPS tự động và theo mặc định](/docs/automatic-https) nếu nó biết tên máy chủ (tên miền). Lệnh `caddy reverse-proxy` sẽ mặc định là `localhost` nếu bạn bỏ qua cờ `--from`, hoặc bạn có thể thay thế dòng đầu tiên của Caddyfile bằng tên miền của proxy.

- Nếu bạn sử dụng `localhost` hoặc bất kỳ tên miền nào kết thúc bằng `.localhost`, Caddy sẽ sử dụng chứng chỉ tự ký tự động gia hạn. Lần đầu tiên bạn làm điều này, bạn có thể cần nhập mật khẩu khi Caddy cố gắng cài đặt chứng chỉ gốc của CA vào kho lưu trữ tin cậy của bạn.
- Nếu bạn sử dụng bất kỳ tên miền nào khác, Caddy sẽ cố gắng lấy chứng chỉ được tin cậy công khai; hãy đảm bảo hồ sơ DNS của bạn trỏ đến máy của bạn và các cổng 80 và 443 được mở công khai và hướng về phía Caddy.

Nếu bạn không chỉ định cổng, Caddy mặc định là 443 cho HTTPS. Trong trường hợp đó, bạn cũng sẽ cần quyền để liên kết với các cổng thấp. Một vài cách để thực hiện việc này trên Linux:

- Chạy với quyền root (ví dụ: `sudo -E`).
- Hoặc chạy `sudo setcap cap_net_bind_service=+ep $(which caddy)` để cấp cho Caddy khả năng cụ thể này.

Dưới đây là lệnh `caddy reverse-proxy` cơ bản nhất cung cấp cho bạn HTTPS:

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

Sau đó hãy thử nó:

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

Bạn có thể tùy chỉnh tên máy chủ bằng cờ `--from`:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

Nếu bạn không có quyền liên kết với các cổng thấp, bạn có thể proxy từ một cổng cao hơn:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

Nếu bạn đang sử dụng Caddyfile, chỉ cần thay đổi dòng đầu tiên thành tên miền của bạn, ví dụ:

```caddy
example.com

reverse_proxy :9000
```

<a id="https-from-proxy-to-backend"></a>
## HTTPS từ proxy đến backend

Caddy cũng có thể proxy bằng HTTPS giữa nó và backend nếu backend hỗ trợ TLS. Chỉ cần sử dụng `https://` trong địa chỉ backend của bạn:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

Điều này yêu cầu chứng chỉ của backend phải được tin cậy bởi hệ thống mà Caddy đang chạy. (Caddy không tin cậy các chứng chỉ tự ký trừ khi được cấu hình rõ ràng để làm như vậy.)

Tất nhiên, bạn cũng có thể thực hiện HTTPS trên cả hai đầu:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

Lệnh này phục vụ HTTPS từ client đến proxy, và từ proxy đến backend.

Nếu tên máy chủ bạn đang proxy đến khác với tên máy chủ bạn đang proxy từ đó, bạn sẽ cần sử dụng cờ `--change-host-header`:

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

Theo mặc định, Caddy chuyển tất cả các HTTP header nguyên vẹn, bao gồm cả `Host`, và Caddy lấy TLS ServerName từ header Host. Cờ `--change-host-header` đặt lại header Host thành tên miền của backend để quá trình bắt tay TLS có thể hoàn tất thành công. Trong ví dụ trên, nó sẽ được thay đổi từ `example.com` thành `localhost:9000` (và `localhost` sẽ được sử dụng trong quá trình bắt tay TLS).
