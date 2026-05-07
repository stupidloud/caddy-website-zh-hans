---
title: "API"
---

# API

Caddy được cấu hình thông qua một điểm cuối quản trị (administration endpoint), có thể truy cập qua HTTP bằng [API REST <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Representational_state_transfer). Bạn có thể [cấu hình điểm cuối này](/docs/json/admin/) trong cấu hình Caddy của mình.

**Địa chỉ mặc định: `localhost:2019`**

Địa chỉ mặc định có thể được thay đổi bằng cách thiết lập biến môi trường `CADDY_ADMIN`. Một số phương pháp cài đặt có thể thiết lập giá trị này khác đi. Địa chỉ trong cấu hình Caddy luôn có mức ưu tiên cao hơn giá trị mặc định.

<aside class="tip">
	Nếu bạn đang chạy mã không đáng tin cậy trên máy chủ của mình (eo ơi 😬), hãy đảm bảo bạn bảo vệ điểm cuối quản trị bằng cách cô lập các tiến trình, vá các chương trình có lỗ hổng và cấu hình điểm cuối để liên kết với một socket unix được phân quyền.
</aside>

Cấu hình mới nhất sẽ được lưu vào đĩa sau bất kỳ thay đổi nào (trừ khi [bị vô hiệu hóa](/docs/json/admin/config/)). Bạn có thể khôi phục cấu hình hoạt động cuối cùng sau khi khởi động lại bằng lệnh [`caddy run --resume`](/docs/command-line#caddy-run), điều này đảm bảo tính bền vững của cấu hình trong trường hợp mất điện hoặc sự cố tương tự.

Để bắt đầu với API, hãy thử [hướng dẫn API](/docs/api-tutorial) của chúng tôi hoặc nếu bạn chỉ có một phút, hãy xem [hướng dẫn bắt đầu nhanh API](/docs/quick-starts/api) của chúng tôi.

---

- **[POST /load](#post-load)**
  Thiết lập hoặc thay thế cấu hình hiện tại

- **[POST /stop](#post-stop)**
  Dừng cấu hình hiện tại và thoát tiến trình

- **[GET /config/[path]](#get-configpath)**
  Xuất cấu hình tại đường dẫn đã chỉ định

- **[POST /config/[path]](#post-configpath)**
  Thiết lập hoặc thay thế đối tượng; thêm vào mảng
  
- **[PUT /config/[path]](#put-configpath)**
  Tạo đối tượng mới; chèn vào mảng

- **[PATCH /config/[path]](#patch-configpath)**
  Thay thế một đối tượng hoặc phần tử mảng hiện có

- **[DELETE /config/[path]](#delete-configpath)**
  Xóa giá trị tại đường dẫn đã chỉ định

- **[Sử dụng `@id` trong JSON](#using-id-in-json)**
  Dễ dàng điều hướng vào cấu hình

- **[Thay đổi cấu hình đồng thời](#concurrent-config-changes)**
  Tránh xung đột khi thực hiện các thay đổi cấu hình không đồng bộ

- **[POST /adapt](#post-adapt)**
  Chuyển đổi cấu hình sang JSON mà không chạy nó

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  Trả về thông tin về một CA [ứng dụng PKI](/docs/json/apps/pki/) cụ thể

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  Trả về chuỗi chứng chỉ của một CA [ứng dụng PKI](/docs/json/apps/pki/) cụ thể

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  Trả về trạng thái hiện tại của các proxy upstream đã được cấu hình


## POST /load

Thiết lập cấu hình của Caddy, ghi đè lên bất kỳ cấu hình nào trước đó. Nó sẽ chặn cho đến khi việc tải lại hoàn tất hoặc thất bại. Các thay đổi cấu hình rất nhẹ nhàng, hiệu quả và không gây ra thời gian chết (zero downtime). Nếu cấu hình mới thất bại vì bất kỳ lý do gì, cấu hình cũ sẽ được khôi phục lại mà không gây gián đoạn.

Điểm cuối này hỗ trợ các định dạng cấu hình khác nhau bằng cách sử dụng các bộ chuyển đổi cấu hình (config adapters). Tiêu đề Content-Type của yêu cầu cho biết định dạng cấu hình được sử dụng trong thân yêu cầu. Thông thường, giá trị này nên là `application/json`, đại diện cho định dạng cấu hình gốc của Caddy. Đối với định dạng cấu hình khác, hãy chỉ định Content-Type thích hợp sao cho giá trị sau dấu gạch chéo / là tên của bộ chuyển đổi cấu hình sẽ sử dụng. Ví dụ: khi gửi một Caddyfile, hãy sử dụng giá trị như `text/caddyfile`; hoặc đối với JSON 5, sử dụng giá trị như `application/json5`; v.v.

Nếu cấu hình mới giống với cấu hình hiện tại, việc tải lại sẽ không xảy ra. Để buộc tải lại, hãy thiết lập `Cache-Control: must-revalidate` trong các tiêu đề yêu cầu.

<a id="examples"></a>
### Ví dụ

Thiết lập một cấu hình hoạt động mới:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

Lưu ý: cờ `-d` của curl loại bỏ các ký tự xuống dòng, vì vậy nếu định dạng cấu hình của bạn nhạy cảm với việc ngắt dòng (ví dụ: Caddyfile), hãy sử dụng `--data-binary` thay thế:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## POST /stop

Dừng máy chủ một cách an toàn và thoát khỏi tiến trình. Để chỉ dừng cấu hình đang chạy mà không thoát tiến trình, hãy sử dụng [DELETE /config/](#delete-configpath).

<a id="example"></a>
### Ví dụ

Dừng tiến trình:

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


## GET /config/[path]

Xuất cấu hình hiện tại của Caddy tại đường dẫn đã chỉ định. Trả về một thân JSON.

<a id="examples"></a>
### Ví dụ

Xuất toàn bộ cấu hình và in đẹp (pretty-print):

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					]
				}
			}
		}
	}
}</code></pre>

Chỉ xuất các địa chỉ listener:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[":443"]</code></pre>



## POST /config/[path]

Thay đổi cấu hình của Caddy tại đường dẫn đã chỉ định thành thân JSON của yêu cầu. Nếu giá trị đích là một mảng, POST sẽ thêm vào cuối (append); nếu là một đối tượng, nó sẽ tạo mới hoặc thay thế.

Trong trường hợp đặc biệt, nhiều mục có thể được thêm vào một mảng nếu:

1. đường dẫn kết thúc bằng `/...`
2. phần tử của đường dẫn trước `/...` tham chiếu đến một mảng
3. dữ liệu tải lên (payload) là một mảng

Trong trường hợp này, các phần tử trong mảng của payload sẽ được mở rộng và mỗi phần tử sẽ được thêm vào mảng đích. Theo thuật ngữ Go, điều này sẽ có tác dụng tương đương với:

```go
baseSlice = append(baseSlice, newElems...)
```

<a id="examples"></a>
### Ví dụ

Thêm một địa chỉ listener:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

Thêm nhiều địa chỉ listener:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

## PUT /config/[path]

Thay đổi cấu hình của Caddy tại đường dẫn đã chỉ định thành thân JSON của yêu cầu. Nếu giá trị đích là một vị trí (chỉ số) trong một mảng, PUT sẽ chèn vào (insert); nếu là một đối tượng, nó sẽ chỉ tạo một giá trị mới.

<a id="example"></a>
### Ví dụ

Thêm một địa chỉ listener vào vị trí đầu tiên:

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


## PATCH /config/[path]

Thay đổi cấu hình của Caddy tại đường dẫn đã chỉ định thành thân JSON của yêu cầu. PATCH thay thế hoàn toàn một giá trị hoặc phần tử mảng hiện có.

<a id="example"></a>
### Ví dụ

Thay thế các địa chỉ listener:

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>



## DELETE /config/[path]

Loại bỏ cấu hình của Caddy tại đường dẫn đã chỉ định. DELETE xóa giá trị mục tiêu.

<a id="examples"></a>
### Ví dụ

Để hủy tải toàn bộ cấu hình hiện tại nhưng vẫn giữ cho tiến trình chạy:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

Để chỉ dừng một trong các máy chủ HTTP của bạn:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


<a id="using-in-json"></a>
<a id="using-id-in-json"></a>
<a id="using-id-in-json"></a>
## Sử dụng `@id` trong JSON

Bạn có thể nhúng các ID vào tài liệu JSON của mình để truy cập trực tiếp dễ dàng hơn vào các phần đó của JSON.

Chỉ cần thêm một trường tên là `"@id"` vào một đối tượng và đặt cho nó một cái tên duy nhất. Ví dụ, nếu bạn có một trình xử lý reverse proxy mà bạn muốn truy cập thường xuyên:

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

Để sử dụng nó, chỉ cần thực hiện một yêu cầu tới điểm cuối API `/id/` theo cùng cách bạn làm với điểm cuối `/config/` tương ứng, nhưng không cần toàn bộ đường dẫn. ID sẽ đưa yêu cầu trực tiếp vào phạm vi cấu hình đó cho bạn.

Ví dụ, để truy cập các upstream của reverse proxy mà không có ID, đường dẫn sẽ như sau:

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

nhưng với một ID, đường dẫn trở thành:

```
/id/my_proxy/upstreams
```

điều này dễ nhớ và viết tay hơn nhiều.

<a id="concurrent-config-changes"></a>
## Thay đổi cấu hình đồng thời

<aside class="tip">

Phần này dành cho tất cả các điểm cuối `/config/`. Đây là tính năng thử nghiệm và có thể thay đổi.

</aside>


API cấu hình của Caddy cung cấp [đảm bảo ACID <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/ACID) cho từng yêu cầu riêng lẻ, nhưng các thay đổi liên quan đến nhiều hơn một yêu cầu có thể gặp phải xung đột hoặc mất dữ liệu nếu không được đồng bộ hóa đúng cách.

Ví dụ, hai máy khách có thể `GET /config/foo` cùng một lúc, thực hiện chỉnh sửa trong phạm vi đó (đường dẫn cấu hình), sau đó gọi `POST|PUT|PATCH|DELETE /config/foo/...` cùng một lúc để áp dụng các thay đổi của họ, dẫn đến xung đột: hoặc một người sẽ ghi đè lên người kia, hoặc người thứ hai có thể để cấu hình ở trạng thái không mong muốn vì nó được áp dụng cho một phiên bản cấu hình khác với phiên bản mà nó được chuẩn bị. Điều này là do các thay đổi không nhận biết được nhau.

API của Caddy không hỗ trợ các giao dịch kéo dài qua nhiều yêu cầu và HTTP là một giao thức phi trạng thái. Tuy nhiên, bạn có thể sử dụng các tiêu đề `Etag` và `If-Match` để phát hiện và ngăn chặn xung đột cho bất kỳ và tất cả các thay đổi như một loại kiểm soát đồng thời lạc quan (optimistic concurrency control). Điều này hữu ích nếu có bất kỳ khả năng nào bạn đang sử dụng các điểm cuối `/config/...` của Caddy đồng thời mà không có sự đồng bộ hóa. Tất cả các phản hồi cho yêu cầu `GET /config/...` đều có một tiêu đề HTTP gọi là `Etag` chứa đường dẫn và một mã băm của nội dung trong phạm vi đó (ví dụ: `Etag: "/config/apps/http/servers 65760b8e"`). Chỉ cần thiết lập tiêu đề `If-Match` trên một yêu cầu thay đổi (mutative request) thành giá trị của tiêu đề Etag từ một yêu cầu `GET` trước đó.

Thuật toán cơ bản cho việc này như sau:

1. Thực hiện một yêu cầu `GET` tới bất kỳ phạm vi `S` nào trong cấu hình. Lưu giữ tiêu đề `Etag` của phản hồi.
2. Thực hiện thay đổi mong muốn của bạn trên cấu hình được trả về.
3. Thực hiện một yêu cầu `POST|PUT|PATCH|DELETE` trong phạm vi `S`, thiết lập tiêu đề yêu cầu `If-Match` thành giá trị `Etag` đã lưu.
4. Nếu phản hồi là HTTP 412 (Precondition Failed), hãy lặp lại từ bước 1 hoặc bỏ cuộc sau quá nhiều lần thử.

Thuật toán này cho phép thực hiện một cách an toàn nhiều thay đổi chồng chéo lên cấu hình của Caddy mà không cần đồng bộ hóa rõ ràng. Nó được thiết kế để các thay đổi đồng thời đối với các phần khác nhau của cấu hình không yêu cầu thử lại: chỉ các thay đổi chồng chéo trong cùng một phạm vi của cấu hình mới có thể gây ra xung đột và do đó yêu cầu thử lại.


## POST /adapt

Chuyển đổi một cấu hình sang JSON của Caddy mà không tải hoặc chạy nó. Nếu thành công, tài liệu JSON kết quả sẽ được trả về trong thân phản hồi.

Tiêu đề Content-Type được sử dụng để chỉ định định dạng cấu hình giống như cách thức hoạt động của [/load](#post-load). Ví dụ, để chuyển đổi một Caddyfile, hãy thiết lập `Content-Type: text/caddyfile`.

Điểm cuối này sẽ chuyển đổi bất kỳ định dạng cấu hình nào miễn là [bộ chuyển đổi cấu hình](/docs/config-adapters) tương ứng được tích hợp vào bản build Caddy của bạn.

<a id="examples"></a>
### Ví dụ

Chuyển đổi một Caddyfile sang JSON:

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## GET /pki/ca/&lt;id&gt;

Trả về thông tin về một CA [ứng dụng PKI](/docs/json/apps/pki/) cụ thể theo ID của nó. Nếu ID CA được yêu cầu là mặc định (`local`), thì CA sẽ được cung cấp nếu nó chưa được cung cấp. Các ID CA khác sẽ trả về lỗi nếu chúng chưa được cung cấp trước đó.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


## GET /pki/ca/&lt;id&gt;/certificates

Trả về chuỗi chứng chỉ của một CA [ứng dụng PKI](/docs/json/apps/pki/) cụ thể theo ID của nó. Nếu ID CA được yêu cầu là mặc định (`local`), thì CA sẽ được cung cấp nếu nó chưa được cung cấp. Các ID CA khác sẽ trả về lỗi nếu chúng chưa được cung cấp trước đó.

Điểm cuối này được sử dụng nội bộ bởi lệnh [`caddy trust`](/docs/command-line#caddy-trust) để cho phép cài đặt chứng chỉ gốc của CA vào kho lưu trữ tin cậy của hệ thống.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


<a id="get-reverse-proxyupstreams"></a>
## GET /reverse_proxy/upstreams

Trả về trạng thái hiện tại của các reverse proxy upstream (backend) đã cấu hình dưới dạng tài liệu JSON.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

Mỗi mục trong mảng JSON là một [upstream](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/) đã cấu hình được lưu trữ trong nhóm upstream toàn cục.

- **address** là địa chỉ kết nối của upstream.
- **num_requests** là số lượng yêu cầu đang hoạt động hiện đang được xử lý bởi upstream.
- **fails** là số lượng yêu cầu thất bại hiện tại được ghi nhớ, theo cấu hình kiểm tra sức khỏe thụ động (passive health checks).

Nếu mục tiêu của bạn là xác định tính khả dụng của một backend, bạn sẽ cần kiểm tra chéo các thuộc tính liên quan của upstream với cấu hình trình xử lý mà bạn đang sử dụng. Ví dụ, nếu bạn đã bật [kiểm tra sức khỏe thụ động](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/) cho các proxy của mình, thì bạn cũng cần xem xét các giá trị `fails` và `num_requests` để xác định xem một upstream có được coi là khả dụng hay không: hãy kiểm tra xem số lượng `fails` có ít hơn số lượng thất bại tối đa đã cấu hình cho proxy của bạn hay không (tức là [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/)), và `num_requests` có nhỏ hơn hoặc bằng số lượng yêu cầu tối đa đã cấu hình cho mỗi upstream hay không (tức là [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/) cho toàn bộ proxy, hoặc [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/) cho từng upstream riêng lẻ).
ng lẻ).
