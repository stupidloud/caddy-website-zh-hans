---
title: "Không gian tên Module"
---

<a id="module-namespaces"></a>
# Không gian tên Module

Các module khách của Caddy được tải một cách chung chung dưới dạng kiểu `interface{}` hoặc `any`. Để các module chủ có thể sử dụng chúng, các module khách được tải thường được xác nhận kiểu (type-assertion) sang một kiểu đã biết trước. Trang này mô tả ánh xạ từ các không gian tên module sang các kiểu Go cho tất cả các module tiêu chuẩn.

Tài liệu cho các không gian tên module không tiêu chuẩn có thể được tìm thấy cùng với tài liệu của module chủ đã định nghĩa chúng.

<aside class="tip">
	Một cách để đọc bảng này là, "Nếu module của bạn nằm trong &lt;namespace&gt;, thì nó nên được biên dịch dưới dạng &lt;type&gt;."
</aside>

<style>
.table-wrapper {
	padding-left: 0 !important;
	padding-right: 0 !important;
}
</style>

Namespace | Kiểu Interface Dự kiến | Mô tả | Ghi chú
--------- | ------------- | ----------- | ----------
|         | [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#App) | Ứng dụng Caddy
admin.api | [`caddy.AdminRouter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#AdminRouter)<br><br>[`caddy.AdminHandler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#AdminHandler) | Đăng ký các định tuyến HTTP cho quản trị<br><br>Middleware trình xử lý HTTP |
caddy.config_loaders | [`caddy.ConfigLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#ConfigLoader) | Tải một cấu hình | <i>⚠️&nbsp;Thử nghiệm</i>
caddy.fs  | [`fs.FS`](https://pkg.go.dev/io/fs#FS) | Hệ thống tệp ảo |  <i>⚠️&nbsp;Thử nghiệm</i>
caddy.listeners | [`caddy.ListenerWrapper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#ListenerWrapper) | Bọc các bộ lắng nghe mạng (network listeners)
caddy.logging.encoders | [`zapcore.Encoder`](https://pkg.go.dev/go.uber.org/zap/zapcore#Encoder) | Bộ mã hóa mục nhập nhật ký (log entry encoder)
caddy.logging.encoders.filter | [`logging.LogFieldFilter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/logging#LogFieldFilter) | Bộ lọc trường nhật ký
caddy.logging.writers | [`caddy.WriterOpener`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#WriterOpener) | Trình ghi nhật ký
caddy.storage | [`caddy.StorageConverter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#StorageConverter) | Hậu phương lưu trữ (storage backends)
dns.providers | [`certmagic.DNSProvider`](https://pkg.go.dev/github.com/caddyserver/certmagic#DNSProvider) | Trình giải quyết thử thách DNS
events.handlers | [`caddyevents.Handler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyevents#Handler) | Trình xử lý sự kiện | <i>⚠️&nbsp;Thử nghiệm</i>
http.authentication.hashes | [`caddyauth.Comparer`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Comparer)<br><br>[`caddyauth.Hasher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Hasher) | Trình so sánh mật khẩu<br><br>Trình băm mật khẩu
http.authentication.providers | [`caddyauth.Authenticator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Authenticator) | Trình cung cấp xác thực HTTP
http.encoders | [`encode.Encoding`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Encoding)<br><br>[`encode.Encoder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Encoder) | Tạo một bộ mã hóa (nén)<br><br>Mã hóa một luồng dữ liệu
http.handlers | [`caddyhttp.MiddlewareHandler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#MiddlewareHandler) | Trình xử lý HTTP
http.ip_sources | [`caddyhttp.IPRangeSource`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#IPRangeSource) | Dải IP cho các proxy đáng tin cậy
http.matchers | [`caddyhttp.RequestMatcher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#RequestMatcher)<br><br>[`caddyhttp.RequestMatcherWithError`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#RequestMatcherWithError)<br><br>[`caddyhttp.CELLibraryProducer`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#CELLibraryProducer) | Trình khớp yêu cầu (hãy sử dụng WithError thay thế)<br><br>Trình khớp yêu cầu với ngắt mạch lỗi<br><br>Hỗ trợ cho các biểu thức CEL | <i>⚠️&nbsp;Đã lỗi thời</i><br><br><br><br><i>(Tùy chọn)</i>
http.precompressed | [`encode.Precompressed`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Precompressed) | Các ánh xạ nén trước được hỗ trợ
http.reverse_proxy.circuit_breakers | [`reverseproxy.CircuitBreaker`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#CircuitBreaker) | Bộ ngắt mạch (circuit breakers) cho proxy ngược
http.reverse_proxy.selection_policies | [`reverseproxy.Selector`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#Selector) | Chính sách lựa chọn cân bằng tải
http.reverse_proxy.transport | [`http.RoundTripper`](https://pkg.go.dev/net/http#RoundTripper) | Trình vận chuyển proxy ngược HTTP
http.reverse_proxy.upstreams | [`reverseproxy.UpstreamSource`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#UpstreamSource) | Nguồn upstream động | <i>⚠️&nbsp;Thử nghiệm</i>
tls.ca_pool.source | [`caddytls.CA`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#CA) | Nguồn của các chứng chỉ gốc đáng tin cậy
tls.certificates | [`caddytls.CertificateLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#CertificateLoader) | Nguồn chứng chỉ TLS
tls.client_auth | [`caddytls.ClientCertificateVerifier`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ClientCertificateVerifier) | Xác minh chứng chỉ máy khách
tls.ech.publishers | [`caddytls.ECHPublisher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ECHPublisher) | Công bố các cấu hình Encrypted ClientHello (ECH) | <i>⚠️&nbsp;Thử nghiệm</i>
tls.get_certificate | [`certmagic.Manager`](https://pkg.go.dev/github.com/caddyserver/certmagic#Manager) | Trình quản lý chứng chỉ TLS | <i>⚠️&nbsp;Thử nghiệm</i>
tls.handshake_match | [`caddytls.ConnectionMatcher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ConnectionMatcher) | Trình khớp kết nối TLS
tls.issuance | [`certmagic.Issuer`](https://pkg.go.dev/github.com/caddyserver/certmagic#Issuer) | Trình cấp phát chứng chỉ TLS
tls.leaf_cert_loader | [`caddytls.LeafCertificateLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#LeafCertificateLoader) | Tải các chứng chỉ lá đáng tin cậy
tls.permission | [`caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission) | Liệu có nên lấy chứng chỉ cho một tên miền hay không | <i>⚠️&nbsp;Thử nghiệm</i>
tls.stek | [`caddytls.STEKProvider`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#STEKProvider) | Nguồn khóa vé phiên (session ticket key) TLS
tls.context | [`caddytls.HandshakeContext`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#HandshakeContext) | Chặn ngữ cảnh GetCertificate | <i>⚠️&nbsp;Thử nghiệm</i>

Các không gian tên được đánh dấu là "Thử nghiệm" có thể thay đổi. (Vui lòng phát triển với chúng để chúng tôi có thể hoàn thiện các giao diện của chúng!)
