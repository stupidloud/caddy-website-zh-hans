---
title: bind (Chỉ thị Caddyfile)
---

# bind

Ghi đè giao diện (interface) mà socket của máy chủ sẽ liên kết (bind).

Thông thường, trình lắng nghe (listener) sẽ liên kết với giao diện trống (wildcard). Tuy nhiên, bạn có thể buộc trình lắng nghe liên kết với một tên miền (hostname) hoặc địa chỉ IP khác. Chỉ thị này chỉ chấp nhận máy chủ (host), không bao gồm cổng (port). Cổng được xác định bởi [địa chỉ trang web](/docs/caddyfile/concepts#addresses) (mặc định là `443`).

Lưu ý rằng việc liên kết các trang web không nhất quán có thể dẫn đến những hậu quả không mong muốn. Ví dụ: nếu hai trang web trên cùng một cổng cùng trỏ về `127.0.0.1` và chỉ một trong số đó được cấu hình with `bind 127.0.0.1`, thì chỉ trang web đó mới có thể truy cập được vì trang còn lại sẽ liên kết với cổng mà không có máy chủ cụ thể; hệ điều hành sẽ chọn socket khớp cụ thể hơn. (Máy chủ ảo - Virtual hosts không được chia sẻ giữa các trình lắng nghe khác nhau.)

`bind` chấp nhận [địa chỉ mạng](/docs/conventions#network-addresses), nhưng không được bao gồm cổng.


<a id="syntax"></a>
## Cú pháp

```caddy-d
bind <hosts...>
```

- **&lt;hosts...&gt;** là danh sách các giao diện máy chủ để liên kết với trình lắng nghe.


<a id="examples"></a>
## Ví dụ

Để làm cho một socket chỉ có thể truy cập được trên máy hiện tại, hãy liên kết với giao diện loopback (localhost):

```caddy
example.com {
	bind 127.0.0.1
}
```

Để bao gồm IPv6:

```caddy
example.com {
	bind 127.0.0.1 [::1]
}
```

Để liên kết với `10.0.0.1:8080`:

```caddy
example.com:8080 {
	bind 10.0.0.1
}
```

Để liên kết với Unix domain socket tại `/run/caddy`:

```caddy
example.com {
	bind unix//run/caddy
}
```

Để thay đổi quyền truy cập tệp thành có thể ghi bởi tất cả người dùng ([mặc định](/docs/conventions#network-addresses) là `0200`, chỉ chủ sở hữu mới có quyền ghi):

```caddy
example.com {
	bind unix//run/caddy|0222
}
```

Để liên kết một tên miền với hai giao diện khác nhau, với các phản hồi khác nhau:

```caddy
example.com {
	bind 10.0.0.1
	respond "One"
}

example.com {
	bind 10.0.0.2
	respond "Two"
}
```
