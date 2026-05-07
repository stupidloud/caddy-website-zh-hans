---
title: Cách Logging hoạt động
---

Cách Logging hoạt động
=================

Caddy có các cơ sở ghi nhật ký (logging) mạnh mẽ và linh hoạt, nhưng chúng có thể khác với những gì bạn đã quen thuộc, đặc biệt nếu bạn đến từ các dịch vụ lưu trữ (hosting) chia sẻ lỗi thời hoặc các máy chủ web cũ khác.


<a id="overview"></a>
## Tổng quan

Có hai khía cạnh chính của việc ghi nhật ký: emission (ghi/phát hành) và consumption (đọc/tiêu thụ).

**Emission** nghĩa là tạo ra các thông báo. Nó bao gồm ba bước:

1. Thu thập thông tin liên quan (context - ngữ cảnh)
2. Xây dựng một biểu diễn hữu ích (encoding - mã hóa)
3. Gửi biểu diễn đó đến một đầu ra (writing - ghi)

Chức năng này được tích hợp vào lõi của Caddy, cho phép bất kỳ phần nào của mã nguồn Caddy hoặc các mô-đun (plugin) đều có thể ghi nhật ký.

**Consumption** là việc tiếp nhận &amp; xử lý các thông báo. Để có ích, các nhật ký đã ghi phải được tiêu thụ. Những nhật ký chỉ được ghi ra mà không bao giờ được đọc thì không mang lại giá trị nào. Việc tiêu thụ nhật ký có thể đơn giản như một quản trị viên đọc đầu ra bảng điều khiển (console), hoặc nâng cao như việc gắn một công cụ tổng hợp nhật ký hoặc dịch vụ đám mây để lọc, đếm và lập chỉ mục các thông báo nhật ký.

<a id="caddys-role"></a>
### Vai trò của Caddy

_Caddy là một trình ghi nhật ký (log emitter)_. Nó không tiêu thụ nhật ký, ngoại trừ việc xử lý tối thiểu cần thiết để mã hóa và ghi nhật ký. Điều này quan trọng vì nó giữ cho lõi của Caddy đơn giản hơn, dẫn đến ít lỗi và các trường hợp biên hơn, đồng thời giảm gánh nặng bảo trì. Cuối cùng, việc xử lý nhật ký nằm ngoài phạm vi của lõi Caddy.

Tuy nhiên, luôn có khả năng cho một mô-đun ứng dụng Caddy tiêu thụ nhật ký. (Nó chỉ là chưa tồn tại, theo hiểu biết của chúng tôi.)


<a id="structured-logs"></a>
## Nhật ký có cấu trúc (Structured logs)

Giống như hầu hết các ứng dụng hiện đại, nhật ký của Caddy có _cấu trúc_. Điều này có nghĩa là thông tin trong một thông báo không chỉ đơn thuần là một chuỗi ký tự hoặc một lát cắt byte không rõ ràng. Thay vào đó, dữ liệu vẫn được định kiểu mạnh và được xác định bởi các _tên trường_ (field names) riêng lẻ cho đến khi đến lúc mã hóa thông báo và ghi nó ra.

So sánh với nhật ký không cấu trúc truyền thống&mdash;như Định dạng Nhật ký Chung (Common Log Format - CLF) lỗi thời&mdash;thường được sử dụng với các máy chủ HTTP truyền thống:

```
127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.1" 200 2326
```

Định dạng này "có cấu trúc" nhưng không phải là "nhật ký có cấu trúc": nó chỉ có thể được sử dụng để ghi lại các yêu cầu HTTP. Không có cách nào (hiệu quả) để mã hóa nó theo cách khác, vì nó là một chuỗi byte không rõ ràng. Nó cũng thiếu rất nhiều thông tin. Nó thậm chí không bao gồm tiêu đề Host của yêu cầu! Định dạng nhật ký này chỉ hữu ích khi lưu trữ một trang web duy nhất và để có được những thông tin cơ bản nhất về các yêu cầu.

<aside class="tip">
	Việc thiếu thông tin host trong CLF là lý do tại sao các nhật ký này thường cần được ghi vào các tệp riêng biệt khi lưu trữ nhiều hơn một trang web: không có cách nào khác để biết tiêu đề Host từ yêu cầu!
</aside>

Bây giờ hãy so sánh một thông báo nhật ký có cấu trúc tương đương từ Caddy, được mã hóa dưới dạng JSON và được định dạng đẹp mắt để hiển thị:

```json
{
	"level": "info",
	"ts": 1646861401.5241024,
	"logger": "http.log.access",
	"msg": "handled request",
	"request": {
		"remote_ip": "127.0.0.1",
		"remote_port": "41342",
		"client_ip": "127.0.0.1",
		"proto": "HTTP/2.0",
		"method": "GET",
		"host": "localhost",
		"uri": "/",
		"headers": {
			"User-Agent": ["curl/7.82.0"],
			"Accept": ["*/*"],
			"Accept-Encoding": ["gzip, deflate, br"],
		},
		"tls": {
			"resumed": false,
			"version": 772,
			"cipher_suite": 4865,
			"proto": "h2",
			"server_name": "example.com"
		}
	},
	"bytes_read": 0,
	"user_id": "",
	"duration": 0.000929675,
	"size": 10900,
	"status": 200,
	"resp_headers": {
		"Server": ["Caddy"],
		"Content-Encoding": ["gzip"],
		"Content-Type": ["text/html; charset=utf-8"],
		"Vary": ["Accept-Encoding"]
	}
}
```

Bạn có thể thấy nhật ký có cấu trúc hữu ích hơn nhiều và chứa nhiều thông tin hơn như thế nào. Sự phong phú của thông tin trong thông báo nhật ký này không chỉ hữu ích mà còn hầu như không gây tốn kém về hiệu suất: nhật ký của Caddy không cấp phát bộ nhớ (zero-allocation). Nhật ký có cấu trúc không có hạn chế về kiểu dữ liệu hoặc ngữ cảnh: chúng có thể được sử dụng trong bất kỳ lộ trình mã nào và bao gồm bất kỳ loại thông tin nào.

Vì nhật ký có cấu trúc và được định kiểu mạnh, chúng có thể được mã hóa thành bất kỳ định dạng nào. Vì vậy, nếu bạn không muốn làm việc với JSON, nhật ký có thể được mã hóa thành bất kỳ biểu diễn nào khác. Caddy hỗ trợ các định dạng khác thông qua [các mô-đun mã hóa nhật ký (log encoder modules)](/docs/json/logging/logs/encoder/), và thậm chí có thể thêm nhiều hơn nữa.

**Quan trọng nhất** trong sự phân biệt giữa nhật ký có cấu trúc và các định dạng cũ, với một chút đánh đổi về hiệu suất, một nhật ký có cấu trúc [có thể được chuyển đổi thành Định dạng Nhật ký Chung cũ <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder), nhưng không thể làm ngược lại. Việc đi từ CLF sang các định dạng có cấu trúc là không hề đơn giản (hoặc ít nhất là không hiệu quả), và là bất khả thi nếu xét đến việc thiếu thông tin.

Về bản chất, việc ghi nhật ký có cấu trúc, hiệu quả thường thúc đẩy các triết lý sau:

- Quá nhiều nhật ký vẫn tốt hơn là quá ít
- Lọc tốt hơn là loại bỏ
- Trì hoãn việc mã hóa để linh hoạt hơn và có khả năng tương tác tốt hơn
 

<a id="emission"></a>
## Emission (Ghi nhật ký)

Trong mã nguồn, một lần ghi nhật ký giống như sau:

```go
logger.Debug("proxy roundtrip",
	zap.String("upstream", di.Upstream.String()),
	zap.Object("request", caddyhttp.LoggableHTTPRequest{Request: req}),
	zap.Object("headers", caddyhttp.LoggableHTTPHeader(res.Header)),
	zap.Duration("duration", duration),
	zap.Int("status", res.StatusCode),
)
```

<aside class="tip">
	Đây là một dòng mã thực tế từ reverse proxy của Caddy. Dòng này cho phép bạn kiểm tra các yêu cầu đến các máy chủ thượng nguồn (upstreams) đã định cấu hình khi bạn bật chế độ ghi nhật ký gỡ lỗi (debug logging). Nó là một mẩu dữ liệu vô giá khi khắc phục sự cố!
</aside>

Bạn có thể thấy rằng một lời gọi hàm này chứa mức độ nhật ký (log level), một thông báo và một vài trường dữ liệu. Tất cả chúng đều được định kiểu mạnh, và Caddy sử dụng thư viện ghi nhật ký không cấp phát bộ nhớ (zero-allocation logging library) nên việc ghi nhật ký diễn ra nhanh chóng và hiệu quả, hầu như không tốn kém tài nguyên.

Biến `logger` là một `zap.Logger` có thể có bất kỳ lượng ngữ cảnh nào được liên kết với nó, bao gồm cả tên và các trường dữ liệu. Điều này cho phép các trình ghi nhật ký "kế thừa" từ các ngữ cảnh cha một cách khá tốt, hỗ trợ việc truy vết (tracing) và đo lường (metrics) nâng cao.

Từ đó, thông báo được gửi qua một đường ống xử lý (processing pipeline) hiệu quả cao, nơi nó được mã hóa và ghi lại.


<a id="logging-pipeline"></a>
## Đường ống ghi nhật ký (Logging pipeline)

Như bạn đã thấy ở trên, các thông báo được tạo ra bởi **loggers**. Các thông báo sau đó được gửi đến **logs** để xử lý.

Caddy cho phép bạn [cấu hình nhiều logs](/docs/json/logging/logs/) để xử lý các thông báo. Một log bao gồm một trình mã hóa (encoder), trình ghi (writer), mức độ tối thiểu (minimum level), tỷ lệ lấy mẫu (sampling ratio) và một danh sách các loggers để bao gồm hoặc loại trừ. Trong Caddy, luôn có một log mặc định tên là `default`. Bạn có thể tùy chỉnh nó bằng cách chỉ định một log có khóa là `"default"` trong [đối tượng này](/docs/json/logging/logs/) trong cấu hình.

<aside class="tip">

Bây giờ là lúc thích hợp để [khám phá tài liệu ghi nhật ký của Caddy](/docs/json/logging/) để bạn có thể làm quen với cấu trúc và các tham số mà chúng ta đang nói đến.

</aside>


- **Encoder (Trình mã hóa):** Định dạng cho nhật ký. Chuyển đổi biểu diễn dữ liệu trong bộ nhớ thành một lát cắt byte. Các trình mã hóa có quyền truy cập vào tất cả các trường của một thông báo nhật ký.
- **Writer (Trình ghi):** Đầu ra của nhật ký. Có thể là bất kỳ mô-đun trình ghi nhật ký nào, chẳng hạn như ghi vào tệp hoặc ổ cắm mạng (network socket). Nó chỉ đơn giản là ghi các byte.
- **Level (Mức độ):** Nhật ký có các mức độ khác nhau, từ DEBUG đến FATAL. Các thông báo thấp hơn mức độ được chỉ định sẽ bị log bỏ qua.
- **Sampling (Lấy mẫu):** Các lộ trình cực kỳ "nóng" có thể tạo ra nhiều nhật ký hơn mức có thể xử lý hiệu quả; việc bật lấy mẫu là một cách để giảm tải trong khi vẫn mang lại một mẫu thông báo đại diện.
- **Include/exclude (Bao gồm/loại trừ):** Mỗi thông báo được tạo ra bởi một logger, logger này có tên (thường bắt nguồn từ ID mô-đun). Logs có thể bao gồm hoặc loại trừ các thông báo từ các loggers nhất định.

Khi một thông báo nhật ký được tạo ra từ Caddy:

- Tên của trình ghi nhật ký nguồn được kiểm tra đối với danh sách bao gồm/loại trừ của mỗi log; nếu được bao gồm (hoặc không bị loại trừ), nó sẽ được nhận vào log đó.
- Nếu lấy mẫu được bật, một phép tính nhanh sẽ xác định xem có giữ lại thông báo nhật ký hay không.
- Thông báo được mã hóa bằng trình mã hóa đã cấu hình của log.
- Các byte đã mã hóa sau đó được ghi vào trình ghi đã cấu hình của log.

Theo mặc định, tất cả các thông báo đều đi đến tất cả các logs đã cấu hình. Điều này tuân thủ các giá trị của việc ghi nhật ký có cấu trúc được mô tả ở trên. Bạn có thể giới hạn thông báo nào đi đến log nào bằng cách thiết lập danh sách bao gồm/loại trừ của chúng, nhưng điều này chủ yếu là để lọc các thông báo từ các mô-đun khác nhau; nó không nhằm mục đích sử dụng như một dịch vụ tổng hợp nhật ký. Để giữ cho đường ống ghi nhật ký của Caddy tinh gọn và hiệu quả, việc xử lý nâng cao các thông báo nhật ký được trì hoãn cho đến khi tiêu thụ.

<a id="consumption"></a>
## Consumption (Tiêu thụ/Đọc nhật ký)

Sau khi các thông báo được gửi đến một đầu ra, một trình tiêu thụ (consumer) sẽ đọc chúng vào, phân tích chúng và xử lý chúng một cách phù hợp.

Đây là một lĩnh vực vấn đề rất khác so với việc ghi nhật ký, và lõi của Caddy không xử lý việc tiêu thụ (mặc dù một mô-đun ứng dụng Caddy chắc chắn có thể làm được). Có rất nhiều công cụ bạn có thể sử dụng để xử lý các luồng thông báo JSON (hoặc các định dạng khác) và xem, lọc, lập chỉ mục và truy vấn nhật ký. Bạn thậm chí có thể viết hoặc triển khai công cụ của riêng mình.

Ví dụ: nếu bạn chạy phần mềm cũ yêu cầu CLF được tách thành các tệp khác nhau dựa trên một trường cụ thể (ví dụ: tên máy chủ), bạn có thể sử dụng hoặc viết một công cụ đơn giản để đọc JSON, gọi `sprintf()` để tạo chuỗi CLF, sau đó ghi nó vào tệp dựa trên giá trị trong trường `request.host`.

Các cơ sở ghi nhật ký của Caddy cũng có thể được sử dụng để triển khai đo lường (metrics) và truy vết (tracing): đo lường về cơ bản là đếm các thông báo với các đặc điểm nhất định, và truy vết liên kết nhiều thông báo lại với nhau dựa trên những điểm chung giữa chúng.

Có vô số khả năng cho những gì bạn có thể làm bằng cách tiêu thụ nhật ký của Caddy!
