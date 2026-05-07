---
title: basic_auth (Chỉ thị Caddyfile)
---

# basic_auth

Kích hoạt Xác thực Cơ bản HTTP (HTTP Basic Authentication), có thể được sử dụng để bảo vệ các thư mục và tệp tin bằng tên người dùng và mật khẩu đã được băm.

**Lưu ý rằng xác thực cơ bản không an toàn qua HTTP thông thường.** Hãy thận trọng khi quyết định nội dung nào cần bảo vệ bằng Xác thực Cơ bản HTTP.

Khi người dùng yêu cầu một tài nguyên được bảo vệ, trình duyệt sẽ nhắc người dùng nhập tên đăng nhập và mật khẩu nếu họ chưa cung cấp. Nếu thông tin xác thực chính xác có trong tiêu đề Authorization, máy chủ sẽ cấp quyền truy cập vào tài nguyên. Nếu thiếu tiêu đề hoặc thông tin xác thực sai, máy chủ sẽ phản hồi bằng lỗi HTTP 401 Unauthorized.

Cấu hình Caddy không chấp nhận mật khẩu dạng văn bản thuần túy; bạn PHẢI băm chúng trước khi đưa vào cấu hình. Lệnh [`caddy hash-password`](/docs/command-line#caddy-hash-password) có thể giúp thực hiện việc này.

Sau khi xác thực thành công, biến thay thế `{http.auth.user.id}` sẽ khả dụng, chứa tên người dùng đã được xác thực.

Trước phiên bản v2.8.0, chỉ thị này có tên là `basicauth`, nhưng đã được đổi tên để thống nhất với các chỉ thị khác.


<a id="syntax"></a>
## Cú pháp

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<username> <hashed_password>
	...
}
```

- **&lt;hash_algorithm&gt;** chỉ định thuật toán băm mật khẩu (hoặc hàm dẫn xuất khóa) được sử dụng cho các bản băm trong cấu hình này. Các tùy chọn có sẵn bao gồm `argon2id`, mặc định là `bcrypt`.

- **&lt;realm&gt;** là tên vùng (realm) tùy chỉnh.

- **&lt;username&gt;** là tên người dùng hoặc ID người dùng.

- **&lt;hashed_password&gt;** là bản băm của mật khẩu.


<a id="examples"></a>
## Ví dụ

Yêu cầu xác thực cho tất cả các yêu cầu đến `example.com`:

```caddy
example.com {
	basic_auth {
		# Tên người dùng "Bob", mật khẩu "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Welcome, {http.auth.user.id}" 200
}
```

Bảo vệ các tệp trong `/secret/` để chỉ `Bob` mới có thể truy cập (và bất kỳ ai cũng có thể xem các đường dẫn khác):

```caddy
example.com {
	root /srv

	basic_auth /secret/* {
		# Tên người dùng "Bob", mật khẩu "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

Ví dụ `argon2id`

```caddy
example.com {
	root /srv

	basic_auth /secret/* argon2id {
		# Tên người dùng "Bob", mật khẩu "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
