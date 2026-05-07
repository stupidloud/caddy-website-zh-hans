---
title: redir (Chỉ thị Caddyfile)
---

# redir

Thực hiện chuyển hướng HTTP (redirect) đến máy khách (client).

Chỉ thị này ngụ ý rằng một yêu cầu khớp sẽ bị từ chối như hiện tại, và máy khách nên thử lại tại một URL khác. Vì lý do đó, [thứ tự chỉ thị](/docs/caddyfile/directives#directive-order) của nó được đặt rất sớm.


<a id="syntax"></a>
## Cú pháp

```caddy-d
redir [<matcher>] <to> [<code>]
```

- **&lt;to&gt;** là vị trí đích. Trở thành [tiêu đề `Location` <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Location) của phản hồi.

- **&lt;code&gt;** là mã trạng thái HTTP sẽ sử dụng để chuyển hướng. Có thể là:

	- Một số nguyên dương trong dải `3xx`, hoặc `401`
	
	- `temporary` cho chuyển hướng tạm thời (`302`, đây là mặc định)
	
	- `permanent` cho chuyển hướng vĩnh viễn (`301`)
	
	- `html` để sử dụng tài liệu HTML thực hiện chuyển hướng (hữu ích để chuyển hướng trình duyệt nhưng không phải máy khách API)
	
	- Một placeholder với giá trị mã trạng thái



<a id="examples"></a>
## Ví dụ

Chuyển hướng tất cả yêu cầu đến `https://example.com`:

```caddy
www.example.com {
	redir https://example.com
}
```

Tương tự, nhưng vẫn giữ nguyên URI hiện tại bằng cách thêm [placeholder `{uri}`](/docs/caddyfile/concepts#placeholders):

```caddy
www.example.com {
	redir https://example.com{uri}
}
```

Tương tự, nhưng là chuyển hướng vĩnh viễn:

```caddy
www.example.com {
	redir https://example.com{uri} permanent
}
```

Chuyển hướng trang `/about-us` cũ của bạn sang trang `/about` mới:

```caddy
example.com {
	redir /about-us /about
	reverse_proxy localhost:9000
}
```
