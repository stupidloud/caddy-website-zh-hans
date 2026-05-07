---
title: Hướng dẫn Caddyfile
---

<a id="caddyfile-tutorial"></a>
# Hướng dẫn Caddyfile

Hướng dẫn này sẽ dạy bạn những điều cơ bản về [HTTP Caddyfile](/docs/caddyfile) để bạn có thể nhanh chóng và dễ dàng tạo các cấu hình trang web đẹp mắt và đầy đủ chức năng.

**Mục tiêu:**
- 🔲 Trang web đầu tiên
- 🔲 Máy chủ tệp tĩnh
- 🔲 Mẫu (Templates)
- 🔲 Nén (Compression)
- 🔲 Nhiều trang web
- 🔲 Trình khớp (Matchers)
- 🔲 Biến môi trường
- 🔲 Chú thích

**Điều kiện tiên quyết:**
- Kỹ năng sử dụng terminal / dòng lệnh cơ bản
- Kỹ năng sử dụng trình chỉnh sửa văn bản cơ bản
- `caddy` trong PATH của bạn

---

Tạo một tệp văn bản mới có tên là `Caddyfile` (không có phần mở rộng).

Điều đầu tiên bạn nên nhập là [địa chỉ](/docs/caddyfile/concepts#addresses) trang web của bạn:

```caddy
localhost
```

<aside class="tip">

Nếu các cổng HTTP và HTTPS (lần lượt là 80 và 443) là các cổng đặc quyền trên hệ điều hành của bạn, bạn sẽ cần chạy với quyền nâng cao hoặc sử dụng cổng cao hơn. Để sử dụng cổng cao hơn, chỉ cần thay đổi địa chỉ thành một địa chỉ như `localhost:2015` và thay đổi cổng HTTP bằng tùy chọn [http_port](/docs/caddyfile/options) trong Caddyfile.

</aside>


Sau đó nhấn enter và nhập những gì bạn muốn nó thực hiện. Đối với hướng dẫn này, hãy làm cho Caddyfile của bạn trông như thế này:

```caddy
localhost

respond "Hello, world!"
```

Lưu tệp đó và chạy Caddy (vì đây là một hướng dẫn đào tạo, chúng ta sẽ sử dụng cờ `--watch` để các thay đổi đối với Caddyfile của chúng ta được áp dụng tự động):

<pre><code class="cmd bash">caddy run --watch</code></pre>

<aside class="tip">

Nếu bạn gặp lỗi quyền truy cập, hãy thử sử dụng cổng cao hơn trong địa chỉ của bạn (như `localhost:2015`) và [thay đổi cổng HTTP](/docs/caddyfile/options), hoặc chạy với quyền nâng cao.

</aside>


Lần đầu tiên, bạn sẽ được yêu cầu nhập mật khẩu. Điều này là để Caddy có thể phục vụ trang web của bạn qua HTTPS.

<aside class="tip">

Caddy phục vụ tất cả các trang web qua HTTPS theo mặc định miễn là một máy chủ hoặc IP là một phần của địa chỉ trang web. [HTTPS tự động](/docs/automatic-https) can be disabled by prefixing the address with `http://` explicitly.

</aside>


<aside class="complete">Trang web đầu tiên</aside>

Mở [localhost](https://localhost) trong trình duyệt của bạn và xem máy chủ web của bạn đang hoạt động, hoàn chỉnh với HTTPS!

<aside class="tip">
	Bạn có thể cần khởi động lại trình duyệt nếu bạn gặp lỗi chứng chỉ trong lần đầu tiên.
</aside>

Điều đó không đặc biệt thú vị, vì vậy hãy thay đổi phản hồi tĩnh của chúng ta thành một [máy chủ tệp](/docs/caddyfile/directives/file_server) với tính năng liệt kê danh mục được bật:

```caddy
localhost

file_server browse
```

Lưu Caddyfile của bạn, sau đó làm mới tab trình duyệt. Bạn sẽ thấy một danh sách các tệp hoặc một trang HTML nếu có tệp index trong thư mục hiện tại.

<aside class="complete">Máy chủ tệp tĩnh</aside>

<a id="adding-functionality"></a>
## Thêm chức năng

Hãy làm điều gì đó thú vị với máy chủ tệp của chúng ta: phục vụ một trang có mẫu (templated page). Tạo một tệp mới và dán nội dung này vào đó:

```html
<!DOCTYPE html>
<html>
	<head>
		<title>Caddy tutorial</title>
	</head>
	<body>
		Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
	</body>
</html>
```

Lưu tệp này dưới tên `caddy.html` trong thư mục hiện tại và tải nó trong trình duyệt của bạn: [https://localhost/caddy.html](https://localhost/caddy.html)

Đầu ra là:

```
Page loaded at: {{`{{`}}now | date "Mon Jan 2 15:04:05 MST 2006"{{`}}`}}
```

Chờ một chút. Chúng ta sẽ thấy ngày hôm nay. Tại sao nó không hoạt động? Đó là bởi vì máy chủ vẫn chưa được cấu hình để đánh giá các mẫu! Dễ dàng sửa chữa, chỉ cần thêm một dòng vào Caddyfile để nó trông như thế này:

```caddy
localhost

templates
file_server browse
```

Lưu tệp đó, sau đó tải lại tab trình duyệt. Bạn sẽ thấy:

```
Page loaded at: {{now | date "Mon Jan 2 15:04:05 MST 2006"}}
```

Với [mô-đun mẫu (templates module)](/docs/modules/http.handlers.templates) của Caddy, bạn có thể làm được nhiều điều hữu ích với các tệp tĩnh, chẳng hạn như bao gồm các tệp HTML khác, tạo các yêu cầu con (sub-requests), thiết lập các tiêu đề phản hồi, làm việc với các cấu trúc dữ liệu, và nhiều hơn nữa!

<aside class="complete">Mẫu (Templates)</aside>

Nén các phản hồi bằng một thuật toán nén nhanh và hiện đại là một thói quen tốt. Hãy bật hỗ trợ Gzip và Zstandard bằng cách sử dụng chỉ thị [`encode`](/docs/caddyfile/directives/encode):

```caddy
localhost

encode
templates
file_server browse
```

<aside class="complete">Nén (Compression)</aside>

Đó là quy trình cơ bản để thiết lập một trang web nâng cao vừa phải, sẵn sàng cho sản xuất và hoạt động!

Khi bạn đã sẵn sàng bật [HTTPS tự động](/docs/automatic-https), chỉ cần thay thế địa chỉ trang web của bạn (`localhost` trong hướng dẫn của chúng ta) bằng tên miền của bạn. Xem [hướng dẫn bắt đầu nhanh về HTTPS](/docs/quick-starts/https) của chúng ta để biết thêm thông tin.

<a id="multiple-sites"></a>
## Nhiều trang web

Với Caddyfile hiện tại của chúng ta, chúng ta chỉ có thể có một định nghĩa trang web! Chỉ dòng đầu tiên có thể là (các) địa chỉ của trang web, và sau đó tất cả phần còn lại của tệp phải là các chỉ thị cho trang web đó.

Nhưng thật dễ dàng để chúng ta có thể thêm nhiều trang web hơn!

Caddyfile của chúng ta cho đến nay:

```caddy
localhost

encode
templates
file_server browse
```

tương đương với tệp này:

```caddy
localhost {
	encode
	templates
	file_server browse
}
```

ngoại trừ việc tệp thứ hai cho phép chúng ta thêm nhiều trang web hơn.

Bằng cách bọc khối trang web của chúng ta trong dấu ngoặc nhọn `{ }`, chúng ta có thể định nghĩa nhiều trang web khác nhau trong cùng một Caddyfile.

Ví dụ:

```caddy
:8080 {
	respond "I am 8080"
}

:8081 {
	respond "I am 8081"
}
```

Khi bọc các khối trang web trong dấu ngoặc nhọn, chỉ các [địa chỉ](/docs/caddyfile/concepts#addresses) xuất hiện bên ngoài dấu ngoặc nhọn và chỉ các [chỉ thị](/docs/caddyfile/directives) xuất hiện bên trong chúng.

Đối với nhiều trang web chia sẻ cùng một cấu hình, bạn có thể thêm nhiều địa chỉ, ví dụ:

```caddy
:8080, :8081 {
	...
}
```

Sau đó, bạn có thể định nghĩa bao nhiêu trang web khác nhau tùy thích, miễn là mỗi địa chỉ là duy nhất.

<aside class="complete">Nhiều trang web</aside>


<a id="matchers"></a>
## Trình khớp (Matchers)

Chúng ta có thể muốn chỉ áp dụng một số chỉ thị cho một số yêu cầu nhất định. Ví dụ, giả sử chúng ta muốn có cả máy chủ tệp và proxy ngược, nhưng rõ ràng chúng ta không thể thực hiện cả hai trên mọi yêu cầu! Hoặc máy chủ tệp sẽ viết phản hồi với một tệp tĩnh, hoặc proxy ngược sẽ chuyển yêu cầu đến một backend và viết lại phản hồi của nó.

Cấu hình này sẽ không hoạt động như chúng ta muốn (`reverse_proxy` sẽ được ưu tiên do [thứ tự chỉ thị](/docs/caddyfile/directives#directive-order)):

```caddy
localhost

file_server
reverse_proxy 127.0.0.1:9005
```

Trong thực tế, chúng ta có thể chỉ muốn sử dụng proxy ngược cho các yêu cầu API, tức là các yêu cầu có đường dẫn gốc là `/api/`. Điều này dễ dàng thực hiện bằng cách thêm một [token trình khớp](/docs/caddyfile/matchers#syntax):

```caddy
localhost

reverse_proxy /api/* 127.0.0.1:9005
file_server
```

Xong; bây giờ proxy ngược sẽ được ưu tiên cho tất cả các yêu cầu bắt đầu bằng `/api/`.

Phần `/api/*` chúng ta vừa thêm được gọi là một **token trình khớp**. Bạn có thể nhận biết đó là một token trình khớp vì nó bắt đầu bằng một dấu gạch chéo xuôi `/` và nó xuất hiện ngay sau chỉ thị (nhưng bạn luôn có thể tra cứu nó trong [tài liệu của chỉ thị](/docs/caddyfile/directives) để chắc chắn).

Các trình khớp thực sự mạnh mẽ. Bạn có thể khai báo các trình khớp có tên và sử dụng chúng như `@name` để khớp trên nhiều thứ hơn là chỉ đường dẫn yêu cầu! Hãy dành một chút thời gian để [tìm hiểu thêm về các trình khớp](/docs/caddyfile/matchers) trước khi tiếp tục!

<aside class="complete">Trình khớp (Matchers)</aside>

<a id="environment-variables"></a>
## Biến môi trường

Bộ điều hợp Caddyfile cho phép thay thế các [biến môi trường](/docs/caddyfile/concepts#environment-variables) trước khi Caddyfile được phân tích cú pháp.

Đầu tiên, hãy đặt một biến môi trường (trong cùng một shell chạy Caddy):

<pre><code class="cmd bash">export SITE_ADDRESS=localhost:9055</code></pre>

Sau đó, bạn có thể sử dụng nó như thế này trong Caddyfile:

```caddy
{$SITE_ADDRESS}

file_server
```

Trước khi Caddyfile được phân tích cú pháp, nó sẽ được mở rộng thành:

```caddy
localhost:9055

file_server
```

Bạn có thể sử dụng các biến môi trường ở bất kỳ đâu trong Caddyfile, cho bất kỳ số lượng token nào.

<aside class="complete">Biến môi trường</aside>


<a id="comments"></a>
## Chú thích

Một điều cuối cùng mà bạn sẽ thấy hữu ích nhất: nếu bạn muốn nhận xét hoặc ghi chú bất cứ điều gì trong Caddyfile của mình, bạn có thể sử dụng các chú thích, bắt đầu bằng `#`:

```caddy
<a id="this-starts-a-comment"></a>
# dòng này bắt đầu một chú thích
```

<aside class="complete">Chú thích</aside>

<a id="further-reading"></a>
## Đọc thêm

- [Các khái niệm Caddyfile](/docs/caddyfile/concepts)
- [Các chỉ thị](/docs/caddyfile/directives)
- [Các mẫu phổ biến](/docs/caddyfile/patterns)
