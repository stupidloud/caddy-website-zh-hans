---
title: Bộ chuyển đổi cấu hình
---

<a id="config-adapters"></a>
# Bộ chuyển đổi cấu hình

Ngôn ngữ cấu hình gốc của Caddy là [JSON](https://www.json.org/json-en.html), nhưng việc viết JSON thủ công có thể tẻ nhạt và dễ xảy ra sai sót. Đó là lý do tại sao Caddy hỗ trợ cấu hình bằng các ngôn ngữ khác thông qua các **bộ chuyển đổi cấu hình** (config adapters). Chúng là các plugin của Caddy giúp bạn có thể sử dụng cấu hình theo định dạng ưa thích của mình bằng cách xuất ra [Caddy JSON](/docs/json/) cho bạn.

Ví dụ: một bộ chuyển đổi cấu hình có thể [chuyển đổi cấu hình NGINX của bạn thành Caddy JSON](https://github.com/caddyserver/nginx-adapter).

<a id="known-config-adapters"></a>
## Các bộ chuyển đổi cấu hình đã biết

Các bộ chuyển đổi cấu hình sau hiện đang có sẵn (một số là dự án của bên thứ ba):

- [**caddyfile**](/docs/caddyfile) (tiêu chuẩn)
- [**nginx**](https://github.com/caddyserver/nginx-adapter)
- [**jsonc**](https://github.com/caddyserver/jsonc-adapter)
- [**json5**](https://github.com/caddyserver/json5-adapter)
- [**yaml**](https://github.com/abiosoft/caddy-yaml)
- [**cue**](https://github.com/caddyserver/cue-adapter)
- [**toml**](https://github.com/awoodbeck/caddy-toml-adapter)
- [**hcl**](https://github.com/francislavoie/caddy-hcl)
- [**dhall**](https://github.com/mholt/dhall-adapter)
- [**mysql**](https://github.com/zhangjiayin/caddy-mysql-adapter)

<a id="using-config-adapters"></a>
## Sử dụng các bộ chuyển đổi cấu hình

Bạn có thể sử dụng một bộ chuyển đổi cấu hình bằng cách chỉ định nó trên dòng lệnh bằng cách sử dụng cờ `--adapter` trên hầu hết các lệnh con nhận cấu hình:

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

Hoặc thông qua API tại [điểm cuối `/load`](/docs/api#post-load):

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

Nếu bạn chỉ muốn lấy kết quả JSON đầu ra mà không chạy nó, bạn có thể sử dụng lệnh [`caddy adapt`](/docs/command-line#caddy-adapt):

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

<a id="caveats"></a>
## Những điều cần lưu ý

Không phải tất cả các ngôn ngữ cấu hình đều tương thích 100% với Caddy; một số tính năng hoặc hành vi đơn giản là không được chuyển đổi tốt hoặc chưa được lập trình vào bộ chuyển đổi hoặc chính Caddy.

Một số bộ chuyển đổi thực hiện chuyển đổi 1-1, như YAML->JSON hoặc TOML->JSON. Những bộ khác được thiết kế riêng cho Caddy, như Caddyfile. Nhìn chung, các bộ chuyển đổi này sẽ luôn hoạt động.

Tuy nhiên, không phải tất cả các bộ chuyển đổi đều hoạt động mọi lúc. Các bộ chuyển đổi cấu hình cố gắng hết sức để chuyển đổi đầu vào của bạn sang Caddy JSON với độ trung thực và chính xác cao nhất. Vì quá trình chuyển đổi này không đảm bảo luôn hoàn chỉnh và chính xác, chúng tôi không gọi chúng là "bộ chuyển đổi" (converters) hay "bộ dịch" (translators). Chúng là "bộ chuyển đổi" (adapters) vì ít nhất chúng sẽ cung cấp cho bạn một điểm khởi đầu tốt để hoàn thiện cấu hình JSON cuối cùng của mình.

Các bộ chuyển đổi cấu hình có thể xuất ra kết quả JSON, cảnh báo và lỗi. Kết quả JSON sẽ được tạo ra nếu không có lỗi nào xảy ra. Lỗi xảy ra khi có vấn đề với đầu vào (ví dụ: lỗi cú pháp). Cảnh báo được phát ra khi có vấn đề với quá trình chuyển đổi nhưng không nhất thiết là nghiêm trọng (ví dụ: tính năng không được hỗ trợ). Nên thận trọng nếu sử dụng các cấu hình đã được chuyển đổi kèm theo cảnh báo.
