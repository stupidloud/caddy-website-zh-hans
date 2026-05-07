---
title: Nâng cấp lên Caddy 2
---

Hướng dẫn Nâng cấp
==================

Caddy 2 là một cơ sở mã hoàn toàn mới, được viết lại từ đầu để cải thiện Caddy 1. Caddy 2 không tương thích ngược với Caddy 1. Nhưng đừng lo lắng, đối với hầu hết các thiết lập cơ bản, không có nhiều sự khác biệt. Hướng dẫn này sẽ giúp bạn chuyển đổi dễ dàng nhất có thể.

Hướng dẫn này sẽ không đi sâu vào các tính năng mới có sẵn -- những tính năng này thực sự rất tuyệt vời, nhân tiện, bạn nên [tìm hiểu chúng](/docs/getting-started) -- mục tiêu ở đây chỉ là giúp bạn khởi chạy Caddy 2 một cách nhanh chóng.

- [Các điểm chính](#high-order-bits)
- [Các bước thực hiện](#steps)
- [HTTPS và cổng (ports)](#https-and-ports)
- [Dòng lệnh (Command line)](#command-line)
- [Caddyfile](#caddyfile)
	- [Các thay đổi chính](#primary-changes)
	- [basicauth](#basicauth)
	- [browse](#browse)
	- [errors](#errors)
	- [ext](#ext)
	- [fastcgi](#fastcgi)
	- [gzip](#gzip)
	- [header](#header)
	- [log](#log)
	- [proxy](#proxy)
	- [redir](#redir)
	- [rewrite](#rewrite)
	- [root](#root)
	- [status](#status)
	- [templates](#templates)
	- [tls](#tls)
- [Tệp dịch vụ (Service files)](#service-files)
- [Plugin](#plugins)
- [Nhận sự trợ giúp](#getting-help)



<a id="high-order-bits"></a>
## Các điểm chính

- "Caddy 2" vẫn chỉ được gọi là `caddy`. Chúng tôi có thể sử dụng "Caddy 2" để làm rõ phiên bản nào nhằm giúp quá trình chuyển đổi bớt nhầm lẫn hơn.
- Hầu hết người dùng sẽ chỉ cần thay thế tệp thực thi `caddy` và cấu hình `Caddyfile` đã cập nhật của họ (sau khi kiểm tra xem nó có hoạt động hay không).
- Tốt nhất là nên tiếp cận Caddy 2 mà không mang theo bất kỳ giả định nào từ Caddy 1.
- Bạn có thể không sao chép hoàn hảo cấu hình v1 đặc thù của mình sang v2. Thông thường, có một lý do chính đáng cho điều đó.
- Dòng lệnh không còn được sử dụng để cấu hình máy chủ.
- Các biến môi trường không còn cần thiết để cấu hình.
- Cách chính để cung cấp cấu hình cho Caddy 2 là thông qua [API](/docs/api) của nó, nhưng lệnh [`caddy`](/docs/command-line) cũng có thể được sử dụng.
- Bạn nên biết rằng ngôn ngữ cấu hình gốc của Caddy 2 là [JSON](/docs/json/), và Caddyfile chỉ là một [adapter cấu hình](/docs/config-adapters) khác chuyển đổi sang JSON cho bạn. Các trường hợp sử dụng cực kỳ tùy chỉnh/nâng cao có thể yêu cầu JSON, vì không phải mọi cấu hình khả thi đều có thể được biểu diễn bằng Caddyfile.
- Caddyfile hầu như giống nhau, nhưng cũng mạnh mẽ hơn nhiều; các chỉ thị (directives) đã thay đổi.



<a id="steps"></a>
## Các bước thực hiện

1. Làm quen với Caddy 2 bằng cách thực hiện hướng dẫn [Bắt đầu](/docs/getting-started) của chúng tôi.
2. Thực hiện bước 1 nếu bạn chưa làm. Nghiêm túc mà nói -- chúng tôi không thể nhấn mạnh tầm quan trọng của việc ít nhất là biết cách sử dụng Caddy 2. (Nó thú vị hơn!)
3. Sử dụng hướng dẫn bên dưới để chuyển đổi (các) lệnh `caddy` của bạn.
4. Sử dụng hướng dẫn bên dưới để chuyển đổi Caddyfile của bạn.
5. Kiểm tra cấu hình mới của bạn cục bộ hoặc trong môi trường thử nghiệm (staging).
6. Kiểm tra, kiểm tra, và kiểm tra lại.
7. Triển khai và tận hưởng!



<a id="https-and-ports"></a>
## HTTPS và cổng

Cổng mặc định của Caddy không còn là `:2015`. Cổng mặc định của Caddy 2 là `:443` hoặc, nếu không biết hostname/IP, là cổng `:80`. Bạn luôn có thể tùy chỉnh các cổng trong cấu hình của mình.

Giao thức mặc định của Caddy 2 là [_luôn luôn_ HTTPS nếu biết hostname hoặc IP](/docs/automatic-https#overview). Điều này khác với Caddy 1, nơi chỉ các tên miền công khai mới sử dụng HTTPS theo mặc định. Giờ đây, _mọi_ trang web đều sử dụng HTTPS (trừ khi bạn tắt nó bằng cách chỉ định rõ ràng cổng `:80` hoặc `http://`).

Các địa chỉ IP và tên miền localhost sẽ được cấp chứng chỉ từ một [CA nhúng, được tin cậy cục bộ](/docs/automatic-https#local-https). Tất cả các tên miền khác sẽ sử dụng ZeroSSL hoặc Let's Encrypt. (Tất cả những điều này đều có thể cấu hình được.)

Cấu trúc lưu trữ các chứng chỉ và tài nguyên ACME đã thay đổi. Caddy 2 có thể sẽ lấy các chứng chỉ mới cho các trang web của bạn; nhưng nếu bạn có nhiều chứng chỉ, bạn có thể di chuyển chúng thủ công nếu nó không tự động thực hiện cho bạn. Xem các vấn đề [#2955](https://github.com/caddyserver/caddy/issues/2955) và [#3124](https://github.com/caddyserver/caddy/issues/3124) để biết thêm chi tiết.



<a id="command-line"></a>
## Dòng lệnh

Lệnh `caddy` hiện là `caddy run`.

Tất cả các cờ dòng lệnh (flags) đều khác nhau. Hãy xóa chúng; tất cả cấu hình máy chủ hiện nằm trong tài liệu cấu hình thực tế (thường là Caddyfile hoặc JSON). Bạn có thể sẽ tìm thấy những gì mình cần trong [cấu trúc JSON](/docs/json/) hoặc trong [các tùy chọn toàn cục của Caddyfile](/docs/caddyfile/options) để thay thế hầu hết các cờ dòng lệnh từ v1.

Một lệnh như `caddy -conf ../Caddyfile` sẽ trở thành `caddy run --config ../Caddyfile`.

Như trước đây, nếu Caddyfile của bạn nằm trong thư mục hiện tại, Caddy sẽ tự động tìm và sử dụng nó; bạn không cần sử dụng cờ `--config` trong trường hợp đó.

Các tín hiệu (Signals) hầu như giống nhau, ngoại trừ USR1 và USR2 không còn được hỗ trợ. Sử dụng lệnh [`caddy reload`](/docs/command-line#caddy-reload) hoặc [API](/docs/api) thay thế để tải cấu hình mới.

Chạy `caddy` mà không có bất kỳ cấu hình nào từng là chạy một máy chủ tệp đơn giản. Tương đương trong Caddy 2 là [`caddy file-server`](/docs/command-line#caddy-file-server).

Các biến môi trường không còn liên quan, ngoại trừ `HOME` (và tùy chọn, bất kỳ biến `XDG_*` nào bạn đặt). `CADDYPATH` được [thay thế bằng các quy ước của hệ điều hành](/docs/conventions#file-locations).



## Caddyfile

[Caddyfile v2](/docs/caddyfile/concepts) rất giống với những gì bạn đã quen thuộc. Điều chính bạn cần làm là thay đổi các chỉ thị của mình.

⚠️ **Hãy đảm bảo đọc kỹ các chỉ thị mới!** Đặc biệt nếu cấu hình của bạn nâng cao hơn, có nhiều sắc thái cần xem xét. Những mẹo này sẽ giúp bạn chuyển đổi hầu hết khá nhanh chóng, nhưng vui lòng đọc tài liệu đầy đủ cho từng chỉ thị để bạn có thể hiểu rõ ý nghĩa của việc nâng cấp. Và tất nhiên, luôn kiểm tra kỹ các cấu hình của bạn trước khi đưa vào sản xuất.


<a id="primary-changes"></a>
### Các thay đổi chính

- Nếu bạn đang phục vụ các tệp tĩnh, bạn sẽ cần thêm [chỉ thị `file_server`](/docs/caddyfile/directives/file_server), vì Caddy 2 không mặc định giả định điều này. Caddy 2 cũng không tự động nhận diện MIME theo mặc định vì lý do bảo mật; nếu thiếu Content-Type, bạn có thể cần tự đặt tiêu đề bằng chỉ thị [header](/docs/caddyfile/directives/header).

- Trong v1, bạn chỉ có thể lọc (hoặc "khớp") các chỉ thị theo đường dẫn yêu cầu. Trong v2, [khớp yêu cầu (request matching)](/docs/caddyfile/matchers) mạnh mẽ hơn nhiều. Bất kỳ chỉ thị v2 nào thêm middleware vào chuỗi trình xử lý HTTP hoặc thao tác yêu cầu/phản hồi HTTP theo bất kỳ cách nào đều tận dụng chức năng khớp mới này. [Đọc thêm về bộ khớp yêu cầu v2.](/docs/caddyfile/matchers) Bạn cần biết về chúng để hiểu Caddyfile v2.

- Mặc dù nhiều [placeholders](/docs/conventions#placeholders) vẫn giống nhau, nhiều thứ đã thay đổi và hiện có [nhiều cái mới](/docs/modules/http#docs), bao gồm cả [các lối tắt cho Caddyfile](/docs/caddyfile/concepts#placeholders).

- Các bản ghi log của Caddy 2 đều có cấu trúc, và định dạng mặc định là JSON. Tất cả các cấp độ log có thể đơn giản đi vào cùng một log để xử lý (nhưng bạn có thể tùy chỉnh điều này nếu cần).

- Ở những nơi bạn khớp yêu cầu theo tiền tố đường dẫn trong Caddy 1, việc khớp đường dẫn hiện là khớp chính xác theo mặc định trong Caddy 2. Nếu bạn muốn khớp một tiền tố như `/foo/`, bạn sẽ cần `/foo/*` trong Caddy 2.

Chúng tôi sẽ liệt kê một số chỉ thị v1 phổ biến nhất ở đây và mô tả cách chuyển đổi chúng để sử dụng trong Caddyfile v2.

⚠️ **Việc một chỉ thị v1 bị thiếu trong trang này không có nghĩa là v2 không thể làm được!** Một số chỉ thị v1 không còn cần thiết, không được chuyển đổi tốt hoặc được đáp ứng theo những cách khác trong v2. Đối với một số tùy chỉnh nâng cao, bạn có thể cần chuyển xuống JSON để đạt được những gì mình muốn. Khám phá [tài liệu của chúng tôi](/docs/caddyfile) để tìm thấy những gì bạn cần!


### basicauth

Xác thực HTTP Basic vẫn được cấu hình bằng chỉ thị [`basic_auth`](/docs/caddyfile/directives/basic_auth). Tuy nhiên, cấu hình Caddy 2 không chấp nhận mật khẩu văn bản thuần túy. Bạn phải băm (hash) chúng, lệnh [`caddy hash-password`](/docs/command-line#caddy-hash-password) có thể trợ giúp việc này.

- **v1:**
```
basicauth /secret/ Bob hiccup
```

- **v2:**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```


### browse

Duyệt tệp hiện được bật thông qua chỉ thị [`file_server`](/docs/caddyfile/directives/file_server).

- **v1:**
```
browse /subfolder/
```
- **v2:**
```caddy-d
file_server /subfolder/* browse
```


### errors

Các trang lỗi tùy chỉnh có thể được thực hiện bằng [`handle_errors`](/docs/caddyfile/directives/handle_errors).


- **v1:**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2:**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

### ext

Phần mở rộng tệp ngầm định có thể được thực hiện bằng [`try_files`](/docs/caddyfile/directives/try_files).

- **v1:** `ext .html`
- **v2:** `try_files {path}.html {path}`


### fastcgi

Giả sử bạn đang phục vụ PHP, tương đương v2 là [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi).

- **v1:**
```
fastcgi / localhost:9005 php
```
- **v2:**
```caddy-d
php_fastcgi localhost:9005
```

Lưu ý rằng chỉ thị `fastcgi` từ v1 đã làm rất nhiều việc ngầm bên dưới, bao gồm thử các tệp trên đĩa, viết lại yêu cầu và thậm chí là chuyển hướng. Chỉ thị `php_fastcgi` của v2 cũng thực hiện những việc này cho bạn, nhưng tài liệu cung cấp [biểu mẫu mở rộng](/docs/caddyfile/directives/php_fastcgi#expanded-form) của nó mà bạn có thể sửa đổi nếu yêu cầu của bạn khác đi.

Không cần cài đặt trước (preset) `php` trong v2, vì chỉ thị `php_fastcgi` giả định PHP theo mặc định. Một dòng như `php_fastcgi 127.0.0.1:9000 php` sẽ khiến reverse proxy nghĩ rằng có một backend thứ hai tên là `php`, dẫn đến lỗi kết nối.

Các chỉ thị con (subdirectives) khác nhau trong v2 -- bạn có lẽ sẽ không cần bất kỳ chỉ thị nào cho PHP.


### gzip

Một chỉ thị duy nhất [`encode`](/docs/caddyfile/directives/encode) hiện được sử dụng cho tất cả các mã hóa phản hồi, bao gồm nhiều định dạng nén.

- **v1:**
```
gzip
```
- **v2:**
```caddy-d
encode gzip
```

Sự thật thú vị: Caddy 2 cũng hỗ trợ `zstd` (nhưng chưa có trình duyệt nào hỗ trợ).


### header

[Hầu như không thay đổi](/docs/caddyfile/directives/header), nhưng giờ đây mạnh mẽ hơn nhiều vì nó có thể thực hiện thay thế chuỗi con trong v2.

- **v1:**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2:**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```


### log

Bật ghi nhật ký truy cập; chỉ thị [`log`](/docs/caddyfile/directives/log) vẫn có thể được sử dụng trong v2, nhưng tất cả các bản ghi nhật ký đều có cấu trúc, được mã hóa dưới dạng JSON theo mặc định.

Cách được đề xuất để bật ghi nhật ký truy cập đơn giản là:

```caddy-d
log
```

phát ra các bản ghi có cấu trúc tới stderr. (Bạn cũng có thể phát ra một tệp hoặc socket mạng; xem tài liệu chỉ thị [`log`](/docs/caddyfile/directives/log).)

Theo mặc định, nhật ký sẽ ở định dạng JSON [có cấu trúc](/docs/logging). Nếu bạn vẫn cần nhật ký ở định dạng Common Log Format (CLF) vì lý do kế thừa, bạn có thể sử dụng plugin [`transform-encoder`](https://github.com/caddyserver/transform-encoder).


### proxy

Tương đương v2 là [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

Các thay đổi chỉ thị con đáng chú ý là `header_upstream` và `header_downstream` đã lần lượt trở thành `header_up` và `header_down`; và các chỉ thị con liên quan đến cân bằng tải được thêm tiền tố `lb_`.

Một sự khác biệt đáng kể khác là proxy v2 chuyển tiếp tất cả các tiêu đề đến theo mặc định (bao gồm cả tiêu đề `Host`) và đặt tiêu đề `X-Forwarded-For`. Nói cách khác, chế độ "transparent" của v1 về cơ bản là mặc định trong v2 (nhưng nếu bạn cần các tiêu đề khác như X-Real-IP, bạn phải tự đặt chúng). Bạn vẫn có thể ghi đè/tùy chỉnh tiêu đề `Host` bằng chỉ thị con `header_up`.

Proxy Websocket "chỉ việc hoạt động" trong v2; không cần phải "bật" websockets như trong v1.

Chỉ thị con `without` đã bị xóa vì các [mẹo viết lại (rewrite hacks)](#rewrite) không còn cần thiết trong v2 nhờ hỗ trợ bộ khớp được cải thiện.

- **v1:**
```
proxy / localhost:9005
```
- **v2:**
```caddy-d
reverse_proxy localhost:9005
```


### redir

[Không thay đổi](/docs/caddyfile/directives/redir), ngoại trừ một vài chi tiết về đối số mã trạng thái tùy chọn. Hầu hết các cấu hình sẽ không cần thực hiện bất kỳ thay đổi nào.

- **v1:** `redir https://example.com{uri}`
- **v2:** `redir https://example.com{uri}`


### rewrite

Ngữ nghĩa của việc viết lại yêu cầu ("internal redirecting") đã thay đổi một chút. Nếu bạn đã sử dụng cái gọi là "mẹo viết lại" trong v1 như một cách để khớp các yêu cầu trên một thứ khác ngoài tiền tố đường dẫn đơn giản, thì điều đó hoàn toàn không cần thiết trong v2.

[Chỉ thị `rewrite` mới](/docs/caddyfile/directives/rewrite) rất đơn giản nhưng rất mạnh mẽ, vì hầu hết sự phức tạp của nó được xử lý bởi [các bộ khớp (matchers)](/docs/caddyfile/matchers) trong v2:

- **v1:**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2:**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

Lưu ý cách chúng tôi chỉ đơn giản sử dụng [các token bộ khớp](/docs/caddyfile/matchers) thông thường của Caddy 2; nó không còn là một trường hợp đặc biệt cho chỉ thị này.

Bắt đầu bằng cách xóa tất cả các mẹo viết lại; thay vào đó hãy chuyển chúng thành [các bộ khớp có tên (named matchers)](/docs/caddyfile/concepts#named-matchers). Đánh giá từng `rewrite` v1 để xem nó có thực sự cần thiết trong v2 hay không. Gợi ý: Một Caddyfile v1 sử dụng `rewrite` để thêm tiền tố đường dẫn và sau đó là `proxy` với `without` để xóa cùng tiền tố đó là một mẹo viết lại và có thể được loại bỏ.

Bạn có thể thấy các chỉ thị [`route`](/docs/caddyfile/directives/route) và [`handle`](/docs/caddyfile/directives/handle) mới hữu ích để có quyền kiểm soát lớn hơn đối với logic định tuyến nâng cao.


### root

[Không thay đổi](/docs/caddyfile/directives/root).

Hãy nhớ thêm [chỉ thị `file_server`](/docs/caddyfile/directives/file_server) nếu phục vụ các tệp tĩnh, vì Caddy 2 không mặc định giả định điều này, trong khi v1 luôn bật nó.


### status

Tương đương v2 là [`respond`](/docs/caddyfile/directives/respond), cũng có thể viết một thân phản hồi.

- **v1:**
```
status 404 /secrets/
```
- **v2:**
```caddy-d
respond /secrets/* 404
```


### templates

Cú pháp tổng thể của chỉ thị [`templates`](/docs/caddyfile/directives/templates) không thay đổi, nhưng các hành động/hàm template thực tế đã khác và được cải thiện nhiều. Ví dụ: các template có khả năng bao gồm các tệp, hiển thị markdown, thực hiện các yêu cầu phụ nội bộ, phân tích cú pháp front matter, v.v.!

[Xem tài liệu](/docs/modules/http.handlers.templates) để biết chi tiết về các hàm mới.

- **v1:** `templates`
- **v2:** `templates`


### tls

Các nguyên tắc cơ bản của chỉ thị [`tls`](/docs/caddyfile/directives/tls) không thay đổi, ví dụ: chỉ định chứng chỉ và khóa của riêng bạn:

- **v1:** `tls cert.pem key.pem`
- **v2:** `tls cert.pem key.pem`

Nhưng [logic tự động HTTPS](/docs/automatic-https) của Caddy _đã_ thay đổi, vì vậy hãy lưu ý điều đó!

Tên của các bộ mã hóa (cipher suite) cũng đã thay đổi.

Một cấu hình phổ biến trong Caddy 2 là sử dụng `tls internal` để nó phục vụ một chứng chỉ được tin cậy cục bộ cho một hostname phát triển không phải là `localhost` hoặc địa chỉ IP.

Hầu hết các trang web sẽ không cần chỉ thị này chút nào.


<a id="service-files"></a>
## Tệp dịch vụ

Chúng tôi khuyên bạn nên sử dụng [một trong các tệp dịch vụ systemd chính thức của chúng tôi](/docs/running#linux-service) để triển khai Caddy.

Nếu bạn cần một tệp dịch vụ tùy chỉnh, hãy dựa trên tệp của chúng tôi. Chúng đã được tinh chỉnh cẩn thận vì những lý do chính đáng! Hãy đảm bảo tùy chỉnh tệp của bạn nếu cần thiết.


<a id="plugins"></a>
## Plugin

Các plugin được viết cho v1 không tự động tương thích với v2. Nhiều plugin v1 thậm chí không cần thiết trong v2. Mặt khác, v2 dễ dàng mở rộng và linh hoạt hơn nhiều so với v1!

Nếu bạn muốn viết một plugin cho Caddy 2, hãy [tìm hiểu cách viết một module Caddy](/docs/extending-caddy).


<a id="building-caddy-2-with-plugins"></a>
### Xây dựng Caddy 2 với các plugin

Caddy 2 có thể được tải xuống cùng các plugin tại [trang tải xuống tương tác](/download). Ngoài ra, bạn có thể [tự xây dựng Caddy](/docs/build) bằng `xcaddy` và chọn các plugin để bao gồm. `xcaddy` tự động hóa các hướng dẫn trong tệp [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) của Caddy.


<a id="getting-help"></a>
## Nhận sự trợ giúp

Nếu bạn đang gặp khó khăn trong việc vận hành Caddy, vui lòng xem qua trang web của chúng tôi để biết tài liệu trước. Hãy dành thời gian để thử những điều mới và hiểu những gì đang diễn ra - v2 rất khác so với v1 ở nhiều khía cạnh (nhưng nó cũng rất quen thuộc)!

Nếu bạn vẫn cần hỗ trợ, vui lòng trở thành một phần của [cộng đồng của chúng tôi](https://caddy.community)! Bạn có thể thấy rằng việc giúp đỡ người khác cũng là cách tốt nhất để giúp chính mình.
