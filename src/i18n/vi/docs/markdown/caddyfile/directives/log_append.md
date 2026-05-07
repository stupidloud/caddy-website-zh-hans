---
title: log_append (Chỉ thị Caddyfile)
---

# log_append

Thêm một trường vào nhật ký truy cập (access log) cho yêu cầu hiện tại.

Chỉ thị này nên được sử dụng cùng với [chỉ thị `log`](log), vốn là yêu cầu bắt buộc để kích hoạt ghi nhật ký truy cập ngay từ đầu.

Giá trị có thể là một chuỗi tĩnh, hoặc một [trình giữ chỗ (placeholder)](/docs/caddyfile/concepts#placeholders) sẽ được thay thế bằng giá trị của trình giữ chỗ tại thời điểm yêu cầu.


<a id="syntax"></a>
## Cú pháp

```caddy-d
log_append [<matcher>] [<]<key> <value>
```

Theo mặc định, trường nhật ký được thêm vào trên đường quay trở lại chuỗi middleware (tức là "muộn"), sau khi tất cả các trình xử lý tiếp theo đã hoàn tất (ví dụ: sau các trình xử lý như [`reverse_proxy`](reverse_proxy), [`respond`](respond), hoặc [`file_server`](file_server), những trình xử lý này thực hiện ghi phản hồi), vì vậy nó nắm bắt được trạng thái cuối cùng của yêu cầu và phản hồi.

Nếu `<` được sử dụng làm tiền tố cho khóa (key), nó sẽ được đánh dấu là "sớm" (early), nghĩa là trường nhật ký sẽ được thêm vào nhật ký _trước khi_ gọi trình xử lý tiếp theo trong chuỗi, do đó yêu cầu có thể được đọc trước khi bị sửa đổi bởi các trình xử lý tiếp theo.

Chỉ dành cho mục đích gỡ lỗi (không sử dụng trong môi trường thực tế), trình xử lý có cách xử lý chuyên biệt khi giá trị là một trong các trình giữ chỗ sau: `{http.request.body}`, `{http.request.body_base64}`, `{http.response.body}`, hoặc `{http.response.body_base64}`. Nếu trình giữ chỗ thân yêu cầu (request body) được sử dụng, chế độ "sớm" (early) sẽ được kích hoạt ngầm định và thân yêu cầu sẽ được lưu đệm (buffer). Nếu trình giữ chỗ thân phản hồi (response body) được sử dụng, việc lưu đệm phản hồi sẽ được kích hoạt để nắm bắt thân phản hồi và trường này sẽ được thêm vào nhật ký "muộn" (late), khi phản hồi đang được ghi.


<a id="examples"></a>
## Ví dụ

Hiển thị trong nhật ký khu vực của trang web mà yêu cầu đang được phục vụ, là `static` (tĩnh) hoặc `dynamic` (động):

```caddy
example.com {
	log

	handle /static* {
		log_append area "static"
		respond "Static response!"
	}

	handle {
		log_append area "dynamic"
		reverse_proxy localhost:9000
	}
}
```

Hiển thị trong nhật ký, upstream proxy ngược nào đã thực sự được sử dụng (có thể là `node1`, `node2` hoặc `node3`) và thời gian thực hiện proxy đến upstream tính bằng mili giây, cũng như thời gian upstream proxy cần để ghi tiêu đề phản hồi (response header):

```caddy
example.com {
	log

	handle {
		reverse_proxy node1:80 node2:80 node3:80 {
			lb_policy random_choose 2 
		}
		log_append upstream_host {rp.upstream.host}
		log_append upstream_duration_ms {rp.upstream.duration_ms}
		log_append upstream_latency_ms {rp.upstream.latency_ms}
	}
}
```

Một trường có thể được thêm vào nhật ký "sớm" bằng cách thêm tiền tố `<` vào khóa. Điều này cho phép bạn nắm bắt trạng thái của yêu cầu trước khi nó bị sửa đổi bởi các trình xử lý tiếp theo. Ví dụ: để ghi lại đường dẫn yêu cầu ban đầu trước khi nó được viết lại (mặc dù đây chỉ là một ví dụ minh họa, vì đường dẫn yêu cầu ban đầu dù sao cũng đã được ghi lại, nhưng nó giúp làm rõ vấn đề):

```caddy
example.com {
	log
	log_append <original_path {http.request.uri.path}
	rewrite /new-base{uri}
	reverse_proxy localhost:9000
}
```

Vì mục đích gỡ lỗi, hãy thêm thân yêu cầu và thân phản hồi vào nhật ký (không sử dụng trong môi trường thực tế vì điều này gây hại cho hiệu suất và làm cho nhật ký rất nhiễu). Nếu bạn dự đoán phần thân là dữ liệu nhị phân với các ký tự không in được, bạn có thể sử dụng các biến thể base64 của trình giữ chỗ thay thế (ví dụ: `{http.request.body_base64}` và `{http.response.body_base64}`), chúng sẽ dễ dàng hơn để sao chép và kiểm tra:

```caddy
example.com {
	log
	log_append req_body {http.request.body}
	log_append resp_body {http.response.body}

	reverse_proxy localhost:9000
}
```
