---
title: invoke (Chỉ thị Caddyfile)
---

# invoke

<i>⚠️ Thử nghiệm</i>

Kích hoạt một [tuyến đường được đặt tên (named route)](/docs/caddyfile/concepts#named-routes).

Điều này hữu ích khi kết hợp với các chỉ thị trình xử lý HTTP có trạng thái trong bộ nhớ riêng, hoặc nếu chúng tiêu tốn nhiều tài nguyên khi khởi tạo. Nếu bạn có hàng trăm trang web hoặc nhiều hơn, việc kích hoạt một tuyến đường được đặt tên có thể giúp giảm mức sử dụng bộ nhớ.

<aside class="tip">
	
Không giống như [`import`](/docs/caddyfile/directives/import), `invoke` không hỗ trợ các đối số, nhưng bạn có thể sử dụng [`vars`](/docs/caddyfile/directives/vars) để xác định các biến có thể được sử dụng trong tuyến đường được đặt tên.

</aside>

<a id="syntax"></a>
## Cú pháp

```caddy-d
invoke [<matcher>] <route-name>
```

- **&lt;route-name&gt;** là tên của tuyến đường đã được định nghĩa trước đó cần được kích hoạt. Nếu không tìm thấy tuyến đường, một lỗi sẽ được kích hoạt.


<a id="examples"></a>
## Ví dụ

Định nghĩa một [tuyến đường được đặt tên (named route)](/docs/caddyfile/concepts#named-routes) với một [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) có thể được tái sử dụng trong nhiều trang web, với cùng một trạng thái cân bằng tải trong bộ nhớ được tái sử dụng cho mọi trang web.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

<a id="apex-domain-allows-accessing-the-app-via-an-app-subpath"></a>
# Tên miền chính cho phép truy cập ứng dụng qua đường dẫn con /app
<a id="and-the-main-site-otherwise"></a>
# và trang web chính trong trường hợp ngược lại.
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root /srv
		file_server
	}
}

<a id="the-app-is-also-accessible-via-a-subdomain"></a>
# Ứng dụng cũng có thể truy cập được qua một tên miền phụ.
app.example.com {
	invoke app-proxy
}
