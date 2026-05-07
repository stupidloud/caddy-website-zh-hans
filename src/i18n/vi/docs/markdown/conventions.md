---
title: Quy ước
---

<a id="conventions"></a>
# Quy ước

Hệ sinh thái Caddy tuân thủ một vài quy ước để làm cho mọi thứ nhất quán và trực quan trên toàn bộ nền tảng.


- [Địa chỉ mạng](#network-addresses)
- [Trình giữ chỗ](#placeholders)
- [Vị trí tệp](#file-locations)
  - [Thư mục dữ liệu](#data-directory)
  - [Thư mục cấu hình](#configuration-directory)
- [Thời lượng](#durations)



<a id="network-addresses"></a>
## Địa chỉ mạng

Khi chỉ định một địa chỉ mạng để kết nối (dial) hoặc liên kết (bind), Caddy chấp nhận một chuỗi theo định dạng sau:

```
network/address
```

Phần mạng (network) là tùy chọn (mặc định là `tcp`), và là bất cứ thứ gì mà [hàm `net.Dial` của Go](https://pkg.go.dev/net#Dial) nhận dạng được. Nếu một mạng được chỉ định, một dấu gạch chéo xuôi đơn `/` phải phân tách phần mạng và phần địa chỉ.

Mạng có thể là bất kỳ loại nào sau đây; những loại có hậu tố `4` hoặc `6` chỉ dành cho IPv4 hoặc IPv6 tương ứng:

- TCP: `tcp`, `tcp4`, `tcp6`
- UDP: `udp`, `udp4`, `udp6`
- IP: `ip`, `ip4`, `ip6`
- Unix: `unix`, `unixgram`, `unixpacket`

Phần địa chỉ có thể ở bất kỳ dạng nào sau đây:

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/path/to/unix/socket`
- `/path/to/unix/socket|0200`

Máy chủ (host) có thể là bất kỳ tên máy chủ, tên miền có thể phân giải hoặc địa chỉ IP nào.

Trong trường hợp địa chỉ IPv6, địa chỉ phải được đặt trong dấu ngoặc vuông `[]`. Mã nhận dạng vùng (bắt đầu bằng `%`) là tùy chọn (thường được sử dụng cho các địa chỉ link-local).

Cổng (port) có thể là một giá trị đơn lẻ (`:8080`) hoặc một dải bao gồm cả hai đầu (`:8080-8085`). Một dải cổng sẽ được nhân lên thành các địa chỉ riêng lẻ. Không phải tất cả các trường cấu hình đều chấp nhận dải cổng. Cổng đặc biệt `:0` có nghĩa là bất kỳ cổng nào có sẵn.

Đường dẫn unix socket chỉ có thể chấp nhận được khi sử dụng loại mạng `unix*`. Dấu gạch chéo xuôi phân tách mạng và địa chỉ không được coi là một phần của đường dẫn.

Khi một unix socket được sử dụng làm địa chỉ liên kết (bind address), bạn có thể tùy chọn chỉ định chế độ quyền tệp sau đường dẫn, được phân tách bằng dấu gạch đứng `|`. Mặc định là `0200` (hệ bát phân), tức là `u=w,g=,o=` (dạng ký hiệu). Số `0` ở đầu là tùy chọn.

Ví dụ hợp lệ:

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//path/to/socket
unix//path/to/socket|0200
```

<aside class="tip">

Địa chỉ mạng của Caddy không phải là URL. URL kết hợp các lớp thấp hơn và cao hơn của [mô hình OSI <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OSI_model#Layer_architecture), nhưng Caddy thường sử dụng địa chỉ mạng độc lập với một ứng dụng cụ thể, vì vậy việc kết hợp chúng sẽ gây rắc rắc. Trong Caddy, địa chỉ mạng đề cập chính xác đến các tài nguyên có thể được kết nối hoặc liên kết ở các lớp L3-L5, nhưng URL kết hợp L3-L7, điều này là quá nhiều. Một địa chỉ mạng yêu cầu host+port và đường dẫn phải loại trừ lẫn nhau, nhưng URL thì không. Địa chỉ mạng đôi khi hỗ trợ dải cổng, nhưng URL thì không.

</aside>




<a id="placeholders"></a>
## Trình giữ chỗ

Cấu hình của Caddy hỗ trợ việc sử dụng _trình giữ chỗ_ (placeholders). Sử dụng trình giữ chỗ là một cách đơn giản để chèn các giá trị động vào một cấu hình tĩnh.

<aside class="tip">

Trình giữ chỗ là một ý tưởng tương tự như các biến trong các phần mềm khác. Ví dụ, [nginx có các biến <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html) như `$uri` và `$document_root`, trong khi giá trị tương đương của Caddy sẽ là [`{http.request.uri}`](/docs/json/apps/http/#docs) và [`{http.vars.root}`](/docs/caddyfile/directives/root).

</aside>


Trình giữ chỗ được bao quanh hai bên bởi dấu ngoặc nhọn `{ }` và chứa mã định danh bên trong, ví dụ: `{foo.bar}`. Dấu ngoặc nhọn mở của trình giữ chỗ có thể được thoát bằng ký tự `\{like.this}` để ngăn chặn việc thay thế. Mã định danh trình giữ chỗ thường được phân tách theo không gian tên (namespace) bằng các dấu chấm để tránh xung đột giữa các mô-đun.

Các trình giữ chỗ nào có sẵn tùy thuộc vào ngữ cảnh. Không phải tất cả các trình giữ chỗ đều có sẵn trong tất cả các phần của cấu hình. Ví dụ, [ứng dụng HTTP thiết lập các trình giữ chỗ](/docs/json/apps/http/#docs) chỉ có sẵn trong các khu vực của cấu hình liên quan đến việc xử lý các yêu cầu HTTP. Khi một yêu cầu đi qua [trình xử lý `reverse_proxy`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs), trình xử lý sẽ thiết lập một số trình giữ chỗ dành riêng cho proxy. Các trình giữ chỗ này có thể được tham chiếu trong quá trình proxy cũng như sau đó (trong `handle_response`), ví dụ như khi thiết lập các tiêu đề phản hồi hoặc làm phong phú thêm nhật ký truy cập (access logs).

Các trình giữ chỗ sau đây luôn có sẵn (toàn cục):

Trình giữ chỗ | Mô tả
------------|-------------
`{env.*}` | Biến môi trường; ví dụ: `{env.HOME}`
`{file.*}` | Nội dung từ một tệp; ví dụ: `{file./path/to/secret.txt}`
`{system.hostname}` | Tên máy chủ cục bộ của hệ thống
`{system.slash}` | Dấu phân tách đường dẫn tệp của hệ thống
`{system.os}` | Hệ điều hành của hệ thống
`{system.arch}` | Kiến trúc của hệ thống
`{system.wd}` | Thư mục làm việc hiện tại
`{time.now}` | Thời gian hiện tại dưới dạng cấu trúc Go Time
`{time.now.http}` | Thời gian hiện tại theo định dạng được sử dụng trong các [tiêu đề HTTP <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified)
`{time.now.unix}` | Thời gian hiện tại dưới dạng dấu thời gian unix tính bằng giây
`{time.now.unix_ms}` | Thời gian hiện tại dưới dạng dấu thời gian unix tính bằng mili giây
`{time.now.common_log}` | Thời gian hiện tại theo Định dạng Nhật ký Chung (Common Log Format)
`{time.now.year}` | Năm hiện tại theo định dạng YYYY

Không phải tất cả các trường cấu hình đều hỗ trợ trình giữ chỗ, nhưng hầu hết đều hỗ trợ ở những nơi bạn mong đợi. Hỗ trợ cho các trình giữ chỗ cần phải được thêm một cách rõ ràng vào các trường đó. Các tác giả plugin có thể [đọc bài viết này](/docs/extending-caddy/placeholders) để tìm hiểu cách thêm hỗ trợ cho các trình giữ chỗ trong các mô-đun của riêng họ.




<a id="file-locations"></a>
## Vị trí tệp

Phần này chứa thông tin về nơi tìm thấy các tệp khác nhau. Các đường dẫn tệp và thư mục được mô tả ở đây tốt nhất chỉ là mặc định; một số có thể được ghi đè.

<a id="your-config-files"></a>
### Các tệp cấu hình của bạn

Không có một nơi duy nhất, theo quy ước để bạn đặt các tệp cấu hình của mình. Hãy đặt chúng ở bất cứ nơi nào bạn thấy hợp lý nhất.

<aside class="tip">

Ngoại lệ duy nhất cho điều này có thể là một tệp có tên `Caddyfile` trong thư mục làm việc hiện tại, tệp mà lệnh caddy sẽ thử tìm kiếm cho thuận tiện nếu không có tệp cấu hình nào khác được chỉ định.

</aside>


Các bản phân phối đi kèm với tệp cấu hình mặc định nên ghi lại tài liệu về vị trí của tệp cấu hình này, ngay cả khi điều đó có thể hiển nhiên đối với những người duy trì gói/bản phân phối. Đối với hầu hết các bản cài đặt Linux, Caddyfile sẽ được tìm thấy tại `/etc/caddy/Caddyfile`.


<a id="data-directory"></a>
### Thư mục dữ liệu

Caddy lưu trữ các chứng chỉ TLS và các tài sản quan trọng khác trong một thư mục dữ liệu, thư mục này được hỗ trợ bởi [mô-đun lưu trữ đã được cấu hình](/docs/json/storage/) (mặc định: hệ thống tệp cục bộ).

Nếu biến môi trường `XDG_DATA_HOME` được thiết lập, nó sẽ là `$XDG_DATA_HOME/caddy`.

Nếu không, đường dẫn của nó thay đổi theo nền tảng, tuân thủ các quy ước của hệ điều hành:

Hệ điều hành | Đường dẫn thư mục dữ liệu
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (hoặc `/sdcard/caddy`)

Tất cả các hệ điều hành khác sử dụng đường dẫn thư mục của Linux/BSD.

**Thư mục dữ liệu không được coi là một bộ nhớ đệm (cache).** Nội dung của nó **không** phải là tạm thời hoặc chỉ phục vụ cho mục đích hiệu suất. Caddy lưu trữ các chứng chỉ TLS, khóa riêng tư, OCSP staples và các thông tin cần thiết khác vào thư mục dữ liệu. Không nên xóa sạch nó mà không hiểu rõ các tác động.

Điều quan trọng là thư mục này phải có tính bền vững và Caddy có quyền ghi vào đó.


<a id="configuration-directory"></a>
### Thư mục cấu hình

Đây là nơi Caddy có thể lưu trữ một số cấu hình nhất định vào đĩa. Đáng chú ý nhất là nó lưu giữ cấu hình hoạt động cuối cùng (theo mặc định) vào thư mục này để dễ dàng khôi phục lại sau này bằng cách sử dụng [`caddy run --resume`](/docs/command-line#caddy-run).

<aside class="tip">

Thư mục cấu hình *không* phải là nơi bạn cần lưu trữ [các tệp cấu hình của mình](#your-config-files). (Mặc dù bạn được phép làm vậy.)

</aside>


Nếu biến môi trường `XDG_CONFIG_HOME` được thiết lập, nó sẽ là `$XDG_CONFIG_HOME/caddy`.

Nếu không, đường dẫn của nó thay đổi theo nền tảng, tuân thủ các quy ước của hệ điều hành:


Hệ điều hành | Đường dẫn thư mục cấu hình
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

Tất cả các hệ điều hành khác sử dụng đường dẫn thư mục của Linux/BSD.

Điều quan trọng là thư mục này phải có tính bền vững và Caddy có quyền ghi vào đó.


<a id="durations"></a>
## Thời lượng

Các chuỗi thời lượng (duration strings) thường được sử dụng trong suốt cấu hình của Caddy. Chúng có cùng định dạng với [cú pháp `time.ParseDuration` của Go](https://golang.org/pkg/time/#ParseDuration), ngoại trừ việc bạn cũng có thể sử dụng `d` cho ngày (chúng tôi giả định 1 ngày = 24 giờ cho đơn giản). Các đơn vị hợp lệ là:

- `ns` (nano giây)
- `us`/`µs` (vi giây)
- `ms` (mili giây)
- `s` (giây)
- `m` (phút)
- `h` (giờ)
- `d` (ngày)

Ví dụ:

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

Trong [cấu hình JSON](/docs/json/), các giá trị thời lượng cũng có thể là số nguyên đại diện cho số nano giây.
