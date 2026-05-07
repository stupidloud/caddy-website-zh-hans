---
title: handle_errors (chỉ thị Caddyfile)
---

# handle_errors

Thiết lập các trình xử lý lỗi.

Khi các trình xử lý yêu cầu HTTP thông thường trả về một lỗi, quá trình xử lý bình thường sẽ dừng lại và các trình xử lý lỗi sẽ được gọi. Các trình xử lý lỗi tạo thành một tuyến đường (route) giống như các tuyến đường thông thường và chúng có thể làm bất cứ điều gì mà các tuyến đường thông thường có thể làm. Điều này mang lại khả năng kiểm soát và linh hoạt tuyệt vời khi xử lý lỗi trong các yêu cầu HTTP. Ví dụ: bạn có thể phục vụ các trang lỗi tĩnh, các trang lỗi mẫu (template) hoặc reverse proxy sang một backend khác để xử lý lỗi.

Chỉ thị này có thể được lặp lại với các mã trạng thái khác nhau để xử lý các lỗi khác nhau theo những cách khác nhau. Nếu không có mã trạng thái nào được chỉ định, nó sẽ khớp với bất kỳ lỗi nào, đóng vai trò là phương án dự phòng nếu bất kỳ trình xử lý lỗi nào khác không khớp.

Ngữ cảnh của yêu cầu được mang vào các tuyến đường lỗi, vì vậy bất kỳ giá trị nào được đặt trên ngữ cảnh yêu cầu như [site root](root) hoặc [vars](vars) cũng sẽ được bảo toàn trong các trình xử lý lỗi. Ngoài ra, các [placeholders mới](#placeholders) cũng có sẵn khi xử lý lỗi.

Lưu ý rằng một số chỉ thị nhất định, ví dụ như [`reverse_proxy`](reverse_proxy) có thể viết một phản hồi với trạng thái HTTP được phân loại là lỗi, sẽ _không_ kích hoạt các tuyến đường lỗi.

Bạn có thể sử dụng chỉ thị [`error`](error) để kích hoạt lỗi một cách rõ ràng dựa trên các quyết định định tuyến của riêng bạn.


<a id="syntax"></a>
## Cú pháp

```caddy-d
handle_errors [<status_codes...>] {
	<directives...>
}
```

- **<status_codes...>** là một hoặc nhiều mã trạng thái HTTP để khớp với lỗi đang được xử lý. Các mã trạng thái có thể là số có 3 chữ số, hoặc trường hợp đặc biệt là `4xx` hoặc `5xx` khớp với tất cả các mã trạng thái trong phạm vi tương ứng từ 400-499 hoặc 500-599. Nếu không có mã trạng thái nào được chỉ định, nó sẽ khớp với bất kỳ lỗi nào, đóng vai trò là phương án dự phòng nếu bất kỳ trình xử lý lỗi nào khác không khớp.

- **<directives...>** là danh sách các [chỉ thị](/docs/caddyfile/directives) và [trình so khớp (matchers)](/docs/caddyfile/matchers) của trình xử lý HTTP, mỗi dòng một chỉ thị.


## Placeholders

Các placeholder sau đây có sẵn trong khi xử lý lỗi. Chúng là các [viết tắt Caddyfile](/docs/caddyfile/concepts#placeholders) cho các placeholder đầy đủ có thể được tìm thấy trong [tài liệu JSON cho các tuyến đường lỗi của máy chủ HTTP](/docs/json/apps/http/servers/errors/#routes).

| Placeholder | Mô tả |
|---|---|
| `{err.status_code}` | Mã trạng thái HTTP được đề xuất |
| `{err.status_text}` | Văn bản trạng thái được liên kết với mã trạng thái được đề xuất |
| `{err.message}` | Thông báo lỗi |
| `{err.trace}` | Nguồn gốc của lỗi |
| `{err.id}` | Một định danh cho lần xuất hiện lỗi này |


<a id="examples"></a>
## Ví dụ

Các trang lỗi tùy chỉnh dựa trên mã trạng thái (ví dụ: một trang có tên `404.html` cho các lỗi `404`). Lưu ý rằng [`file_server`](file_server) bảo toàn mã trạng thái HTTP của lỗi khi chạy trong `handle_errors` (giả sử bạn đã đặt một [site root](root) trong trang web của mình trước đó):

```caddy-d
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

Một trang lỗi duy nhất sử dụng [`templates`](templates) để viết thông báo lỗi tùy chỉnh:

```caddy-d
handle_errors {
	rewrite /error.html
	templates
	file_server
}
```

Nếu bạn chỉ muốn cung cấp các trang lỗi tùy chỉnh cho một số mã lỗi, bạn có thể kiểm tra sự tồn tại của các tệp lỗi tùy chỉnh trước đó bằng trình so khớp [`file`](/docs/caddyfile/matchers#file):

```caddy-d
handle_errors {
	@custom_err file /err-{err.status_code}.html /err.html
	handle @custom_err {
		rewrite {file_match.relative}
		file_server
	}
	respond "{err.status_code} {err.status_text}"
}
```

Reverse proxy đến một máy chủ chuyên nghiệp có trình độ cao trong việc xử lý các lỗi HTTP và giúp ngày của bạn tốt đẹp hơn 😸:

```caddy-d
handle_errors {
	rewrite /{err.status_code}
	reverse_proxy https://http.cat {
		replace_status {err.status_code}
	}
}
```

Đơn giản là sử dụng [`respond`](respond) để trả về mã lỗi và tên lỗi:

```caddy-d
handle_errors {
	respond "{err.status_code} {err.status_text}"
}
```

Để xử lý các mã lỗi cụ thể theo cách khác nhau:

```caddy-d
handle_errors 404 410 {
	respond "It's a 404 or 410 error!"
}

handle_errors 5xx {
	respond "It's a 5xx error."
}

handle_errors {
	respond "It's another error"
}
```

Đoạn mã trên hoạt động giống như đoạn mã dưới đây, sử dụng trình so khớp [`expression`](/docs/caddyfile/matchers#expression) đối với các mã trạng thái và sử dụng [`handle`](handle) để loại trừ lẫn nhau:

```caddy-d
handle_errors {
	@404-410 `{err.status_code} in [404, 410]`
	handle @404-410 {
		respond "It's a 404 or 410 error!"
	}

	@5xx `{err.status_code} >= 500 && {err.status_code} < 600`
	handle @5xx {
		respond "It's a 5xx error."
	}

	handle {
		respond "It's another error"
	}
}
```
