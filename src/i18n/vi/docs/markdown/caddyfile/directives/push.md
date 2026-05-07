---
title: push (Chỉ thị Caddyfile)
---

# push

Cấu hình máy chủ để chủ động gửi tài nguyên đến máy khách bằng HTTP/2 server push.

Các tài nguyên có thể được liên kết để server push bằng cách chỉ định (các) tiêu đề Link của phản hồi. Chỉ thị này sẽ tự động push các tài nguyên được mô tả bởi các tiêu đề Link ở thượng nguồn (upstream) theo các định dạng sau:

- `<resource>; as=script`
- `<resource>; as=script,<resource>; as=style`
- `<resource>; nopush`
- `<resource>;<resource2>;...`

trong đó `<resource>` bắt đầu bằng dấu gạch chéo `/` (tức là một đường dẫn URI với cùng máy chủ). Chỉ các tài nguyên cùng máy chủ mới có thể được push. Nếu tài nguyên được liên kết là bên ngoài hoặc nếu nó có thuộc tính `nopush`, nó sẽ không được push.

Theo mặc định, các yêu cầu push sẽ bao gồm một số tiêu đề được coi là an toàn để sao chép từ yêu cầu ban đầu:

- Accept-Encoding
- Accept-Language
- Accept
- Cache-Control
- User-Agent

vì người ta giả định rằng nhiều yêu cầu sẽ thất bại nếu thiếu các tiêu đề này; chúng không cần phải được cấu hình thủ công.

Các yêu cầu push được ảo hóa nội bộ, vì vậy chúng rất nhẹ.


<a id="syntax"></a>
## Cú pháp

```caddy-d
push [<matcher>] [<resource>] {
	[GET|HEAD] <resource>
	headers {
		[+]<field> [<value|regexp> [<replacement>]]
		-<field>
	}
}
```

- **&lt;resource&gt;** là đường dẫn URI đích để push. Nếu được sử dụng trong khối, có thể tùy chọn tiền tố là phương thức (GET hoặc POST; mặc định là GET).
- **&lt;headers&gt;** thao tác các tiêu đề của yêu cầu push bằng cùng một cú pháp như [chỉ thị `header`](/docs/caddyfile/directives/header). Một số tiêu đề được mang theo theo mặc định và không cần phải được cấu hình rõ ràng (xem ở trên).



<a id="examples"></a>
## Ví dụ

Push bất kỳ tài nguyên nào được mô tả bởi các tiêu đề `Link` trong phản hồi:

```caddy-d
push
```

Tương tự, nhưng cũng push `/resources/style.css` cho tất cả các yêu cầu:

```caddy-d
push * /resources/style.css
```

Chỉ push `/foo.jpg` khi `/foo.html` được yêu cầu bởi máy khách:

```caddy-d
push /foo.html /foo.jpg
```
