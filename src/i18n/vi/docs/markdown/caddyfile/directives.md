---
title: Chỉ thị Caddyfile
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

<a id="caddyfile-directives"></a>
# Chỉ thị Caddyfile

Chỉ thị (Directives) là các từ khóa chức năng xuất hiện bên trong các [khối (blocks)](/docs/caddyfile/concepts#blocks) trang web. Đôi khi, chúng có thể mở các khối riêng chứa các _chỉ thị con (subdirectives)_, nhưng các chỉ thị **không thể** được sử dụng bên trong các chỉ thị khác trừ khi được ghi chú. Ví dụ: bạn không thể sử dụng `basic_auth` bên trong một khối `file_server`, vì `file_server` không biết cách thực hiện xác thực. Tuy nhiên, bạn _có thể_ sử dụng một số chỉ thị bên trong các khối chỉ thị đặc biệt như `handle` và `route` vì chúng được thiết kế cụ thể để nhóm các chỉ thị xử lý HTTP.

- [Cú pháp](#syntax)
- [Thứ tự chỉ thị](#directive-order)
- [Thuật toán sắp xếp](#sorting-algorithm)

Các chỉ thị sau đây được đi kèm tiêu chuẩn với Caddy và có thể được sử dụng trong HTTP Caddyfile:

<div id="directive-table">

Chỉ thị | Mô tả
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | Hủy yêu cầu HTTP
**[acme_server](/docs/caddyfile/directives/acme_server)** | Một máy chủ ACME tích hợp
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | Thực thi xác thực HTTP Basic
**[bind](/docs/caddyfile/directives/bind)** | Tùy chỉnh địa chỉ socket của máy chủ
**[encode](/docs/caddyfile/directives/encode)** | Mã hóa (thường là nén) các phản hồi
**[error](/docs/caddyfile/directives/error)** | Kích hoạt một lỗi
**[file_server](/docs/caddyfile/directives/file_server)** | Phục vụ các tệp từ đĩa
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | Ủy thác xác thực cho một dịch vụ bên ngoài
**[fs](/docs/caddyfile/directives/fs)** | Thiết lập hệ thống tệp để sử dụng cho I/O tệp
**[handle](/docs/caddyfile/directives/handle)** | Một nhóm các chỉ thị loại trừ lẫn nhau
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | Xác định các tuyến đường để xử lý lỗi
**[handle_path](/docs/caddyfile/directives/handle_path)** | Giống như handle, nhưng loại bỏ tiền tố đường dẫn
**[header](/docs/caddyfile/directives/header)** | Thiết lập hoặc loại bỏ các tiêu đề phản hồi
**[import](/docs/caddyfile/directives/import)** | Bao gồm các đoạn mã (snippets) hoặc tệp
**[intercept](/docs/caddyfile/directives/intercept)** | Chặn các phản hồi được viết bởi các trình xử lý khác
**[invoke](/docs/caddyfile/directives/invoke)** | Gọi một tuyến đường được đặt tên
**[log](/docs/caddyfile/directives/log)** | Bật ghi nhật ký truy cập/yêu cầu
**[log_append](/docs/caddyfile/directives/log_append)** | Thêm một trường vào nhật ký truy cập
**[log_skip](/docs/caddyfile/directives/log_skip)** | Bỏ qua ghi nhật ký truy cập cho các yêu cầu khớp
**[log_name](/docs/caddyfile/directives/log_name)** | Ghi đè (các) tên logger để ghi vào
**[map](/docs/caddyfile/directives/map)** | Ánh xạ một giá trị đầu vào thành một hoặc nhiều đầu ra
**[method](/docs/caddyfile/directives/method)** | Thay đổi phương thức HTTP nội bộ
**[metrics](/docs/caddyfile/directives/metrics)** | Cấu hình điểm cuối hiển thị các chỉ số Prometheus
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | Phục vụ các trang web PHP qua FastCGI
**[push](/docs/caddyfile/directives/push)** | Đẩy nội dung đến máy khách bằng HTTP/2 server push
**[redir](/docs/caddyfile/directives/redir)** | Phát hành một chuyển hướng HTTP cho máy khách
**[request_body](/docs/caddyfile/directives/request_body)** | Thao tác với thân yêu cầu
**[request_header](/docs/caddyfile/directives/request_header)** | Thao tác với các tiêu đề yêu cầu
**[respond](/docs/caddyfile/directives/respond)** | Viết một phản hồi được mã hóa cứng cho máy khách
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | Một reverse proxy mạnh mẽ và có thể mở rộng
**[rewrite](/docs/caddyfile/directives/rewrite)** | Viết lại yêu cầu nội bộ
**[root](/docs/caddyfile/directives/root)** | Thiết lập đường dẫn đến thư mục gốc của trang web
**[route](/docs/caddyfile/directives/route)** | Một nhóm các chỉ thị được xử lý theo nghĩa đen như một đơn vị duy nhất
**[templates](/docs/caddyfile/directives/templates)** | Thực thi các mẫu (templates) trên phản hồi
**[tls](/docs/caddyfile/directives/tls)** | Tùy chỉnh các thiết lập TLS
**[tracing](/docs/caddyfile/directives/tracing)** | Tích hợp với tính năng theo dõi OpenTelemetry
**[try_files](/docs/caddyfile/directives/try_files)** | Viết lại dựa trên sự tồn tại của tệp
**[uri](/docs/caddyfile/directives/uri)** | Thao tác với URI
**[vars](/docs/caddyfile/directives/vars)** | Thiết lập các biến tùy ý

</div>

<a id="syntax"></a>
## Cú pháp

Cú pháp của mỗi chỉ thị sẽ trông giống như sau:

```caddy-d
directive [<matcher>] <args...> {
	subdirective [<args...>]
}
```

Các dấu `<ngoặc nhọn>` chỉ ra các token sẽ được thay thế bằng các giá trị thực tế.

Các dấu `[ngoặc vuông]` chỉ ra các tham số tùy chọn.

Dấu ba chấm `...` chỉ ra sự tiếp tục, nghĩa là một hoặc nhiều tham số hoặc dòng.

Các chỉ thị con thường là tùy chọn trừ khi được tài liệu hóa khác, mặc dù chúng không xuất hiện trong `[ngoặc vuông]`.


<a id="matchers"></a>
### Trình so khớp (Matchers)

Hầu hết—nhưng không phải tất cả—các chỉ thị đều chấp nhận [các token so khớp](/docs/caddyfile/matchers#syntax), cho phép bạn lọc các yêu cầu. Các token so khớp thường là tùy chọn. Các chỉ thị hỗ trợ trình so khớp nếu bạn thấy điều này trong cú pháp của một chỉ thị:

```caddy-d
[<matcher>]
```

Bởi vì các token so khớp đều hoạt động giống nhau, các khả năng khác nhau cho token so khớp sẽ không được mô tả trên mỗi trang để giảm sự trùng lặp. Thay vào đó, hãy tham khảo [tài liệu trình so khớp](/docs/caddyfile/matchers) cho phần giải thích chi tiết về cú pháp.


<a id="directive-order"></a>
## Thứ tự chỉ thị

Nhiều chỉ thị thao tác với chuỗi trình xử lý HTTP. Thứ tự mà các chỉ thị đó được đánh giá là quan trọng, vì vậy một thứ tự mặc định đã được mã hóa cứng vào Caddy.

Bạn có thể ghi đè/tùy chỉnh thứ tự này bằng cách sử dụng [tùy chọn toàn cục `order`](/docs/caddyfile/options#order) hoặc [chỉ thị `route`](/docs/caddyfile/directives/route).

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # chỉ trong khối handle_response của reverse_proxy
request_body

redir

<a id="incoming-request-manipulation"></a>
# thao tác yêu cầu đến
method
rewrite
uri
try_files

<a id="middleware-handlers-some-wrap-responses"></a>
# các trình xử lý middleware; một số bao bọc các phản hồi
basic_auth
forward_auth
request_header
encode
push
intercept
templates

<a id="special-routing-dispatching-directives"></a>
<a id="special-routing--dispatching-directives"></a>
# các chỉ thị định tuyến & điều phối đặc biệt
invoke
handle
handle_path
route

<a id="handlers-that-typically-respond-to-requests"></a>
# các trình xử lý thường phản hồi các yêu cầu
abort
error
copy_response # chỉ trong khối handle_response của reverse_proxy
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



<a id="sorting-algorithm"></a>
## Thuật toán sắp xếp

Để dễ sử dụng, bộ chuyển đổi Caddyfile sắp xếp các chỉ thị theo các quy tắc sau:

- Các chỉ thị có tên khác nhau được sắp xếp theo vị trí của chúng trong [thứ tự mặc định](#directive-order). Thứ tự mặc định có thể được ghi đè bằng [tùy chọn toàn cục `order`](/docs/caddyfile/options). Các chỉ thị từ các plugin _không_ có thứ tự, vì vậy nên sử dụng tùy chọn toàn cục [`order`](/docs/caddyfile/options) hoặc chỉ thị [`route`](/docs/caddyfile/directives/route) để thiết lập một thứ tự.

- Các chỉ thị có cùng tên được sắp xếp theo [trình so khớp](/docs/caddyfile/matchers#syntax) của chúng.

  - Ưu tiên cao nhất là chỉ thị có một [trình so khớp đường dẫn (path matcher)](/docs/caddyfile/matchers#path-matchers) duy nhất.

    Các trình so khớp đường dẫn được sắp xếp theo độ cụ thể, từ cụ thể nhất đến ít cụ thể nhất.
	
	Nói chung, điều này được thực hiện bằng cách sắp xếp theo độ dài của trình so khớp đường dẫn. Có một ngoại lệ là nếu đường dẫn kết thúc bằng dấu `*` và đường dẫn của hai trình so khớp giống nhau, thì trình so khớp không có dấu `*` được coi là cụ thể hơn và được xếp hạng cao hơn.

    Ví dụ:
    - `/foobar` cụ thể hơn `/foo`
    - `/foo` cụ thể hơn `/foo*`
    - `/foo/*` cụ thể hơn `/foo*`

  - Một chỉ thị với bất kỳ trình so khớp nào khác sẽ được sắp xếp tiếp theo, theo thứ tự nó xuất hiện trong Caddyfile.

    Điều này bao gồm các trình so khớp đường dẫn có nhiều giá trị và [trình so khớp được đặt tên (named matchers)](/docs/caddyfile/matchers#named-matchers).

  - Một chỉ thị không có trình so khớp (nghĩa là khớp với tất cả các yêu cầu) được sắp xếp cuối cùng.

- Chỉ thị [`vars`](/docs/caddyfile/directives/vars) có thứ tự theo trình so khớp bị đảo ngược, bởi vì nó liên quan đến việc thiết lập các giá trị có thể ghi đè lẫn nhau, do đó trình so khớp cụ thể nhất nên được đánh giá sau cùng.

- Nội dung của chỉ thị [`route`](/docs/caddyfile/directives/route) bỏ qua tất cả các quy tắc trên và giữ nguyên thứ tự các chỉ thị xuất hiện bên trong.
