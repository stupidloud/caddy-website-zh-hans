---
title: forward_auth (Chỉ thị Caddyfile)
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.innerText.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// Fix uri subdirective, gets parsed as matcher arg because of "uri" directive
	$$_('.k').forEach(item => {
		if (item.innerText.includes('uri') && item.nextElementSibling && item.nextElementSibling.classList.contains('nd')) {
			const next = item.nextElementSibling;
			next.classList.remove('nd');
			next.classList.add('s');
			next.textContent = next.textContent;
		}
	});
});
</script>

# forward_auth

Một chỉ thị theo quan điểm riêng có chức năng proxy một bản sao của yêu cầu đến một cổng xác thực (authentication gateway), nơi có thể quyết định xem việc xử lý có nên tiếp tục hay cần được chuyển đến trang đăng nhập.

- [Cú pháp](#syntax)
- [Dạng mở rộng](#expanded-form)
- [Ví dụ](#examples)
  - [Authelia](#authelia)
  - [Tailscale](#tailscale)

[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) của Caddy có khả năng thực hiện "các yêu cầu kiểm tra trước" (pre-check requests) đến một dịch vụ bên ngoài, nhưng chỉ thị này được thiết kế riêng đặc biệt cho trường hợp sử dụng xác thực. Chỉ thị này thực chất chỉ là một cách thuận tiện để sử dụng một cấu hình dài hơn, phổ biến hơn (bên dưới).

Chỉ thị này thực hiện một yêu cầu `GET` đến upstream đã cấu hình với `uri` được viết lại:
- Nếu upstream phản hồi với mã trạng thái `2xx`, quyền truy cập sẽ được cấp và các trường tiêu đề trong `copy_headers` sẽ được sao chép vào yêu cầu ban đầu, và việc xử lý tiếp tục.
- Ngược lại, nếu upstream phản hồi với bất kỳ mã trạng thái nào khác, phản hồi của upstream sẽ được sao chép ngược lại cho máy khách. Phản hồi này thường bao gồm một lệnh chuyển hướng đến trang đăng nhập của cổng xác thực.

Nếu hành vi này không chính xác như những gì bạn muốn, bạn có thể lấy [dạng mở rộng](#expanded-form) bên dưới làm cơ sở và tùy chỉnh nó theo nhu cầu của mình.

Tất cả các chỉ thị con của [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) đều được hỗ trợ và được chuyển đến trình xử lý `reverse_proxy` bên dưới.


<a id="syntax"></a>
## Cú pháp

```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <to>
	copy_headers <fields...> {
		<fields...>
	}
}
```

- **&lt;upstreams...&gt;** là danh sách các upstream (backend) để gửi các yêu cầu xác thực.

- **uri** là URI (đường dẫn và truy vấn) để đặt trên yêu cầu được gửi đến upstream. Đây thường sẽ là điểm cuối xác minh (verification endpoint) của cổng xác thực.

- **copy_headers** là danh sách các trường tiêu đề HTTP để sao chép từ phản hồi sang yêu cầu ban đầu, khi yêu cầu có mã trạng thái thành công.

  Trường có thể được đổi tên bằng cách sử dụng `>` theo sau là tên mới, ví dụ: `Before>After`.

  Một khối có thể được sử dụng để liệt kê tất cả các trường, mỗi trường một dòng, nếu bạn thích để dễ đọc hơn.

Vì chỉ thị này là một trình bao bọc theo quan điểm riêng dựa trên một reverse proxy, bạn có thể sử dụng bất kỳ chỉ thị con nào của [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax) để tùy chỉnh nó.


<a id="expanded-form"></a>
## Dạng mở rộng

Chỉ thị `forward_auth` giống với cấu hình sau đây. Các cổng xác thực như [Authelia](https://www.authelia.com/) hoạt động tốt với thiết lập sẵn này. Nếu của bạn không hoạt động, hãy thoải mái mượn từ cấu hình này và tùy chỉnh nó khi cần thiết thay vì sử dụng phím tắt `forward_auth`.

```caddy-d
reverse_proxy <upstreams...> {
	# Always GET, so that the incoming
	# request's body is not consumed
	method GET

	# Change the URI to the auth gateway's
	# verification endpoint
	rewrite <to>

	# Forward the original method and URI,
	# since they get rewritten above; this
	# is in addition to other X-Forwarded-*
	# headers already set by reverse_proxy
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# On a successful response, copy response headers
	@good status 2xx
	handle_response @good {
		# for example, for each copy_headers field...
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


<a id="examples"></a>
## Ví dụ


### Authelia

Ủy quyền xác thực cho [Authelia](https://www.authelia.com/), trước khi phục vụ ứng dụng của bạn qua một reverse proxy:

```caddy
# Serve the authentication gateway itself
auth.example.com {
	reverse_proxy authelia:9091
}

# Serve your app
app1.example.com {
	forward_auth authelia:9091 {
		uri /api/authz/forward-auth
		copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
	}

	reverse_proxy app1:8080
}
```

Để biết thêm thông tin, hãy xem [tài liệu của Authelia](https://www.authelia.com/integration/proxies/caddy/) để tích hợp với Caddy.


### Tailscale

Ủy quyền xác thực cho [Tailscale](https://tailscale.com/) (hiện tại có tên là [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/), nhưng nó vẫn hoạt động với Caddy) và sử dụng cú pháp thay thế cho `copy_headers` để đổi tên các tiêu đề được sao chép (lưu ý dấu `>` trong mỗi tiêu đề):

```caddy-d
forward_auth unix//run/tailscale.nginx-auth.sock {
	uri /auth
	header_up Remote-Addr {remote_host}
	header_up Remote-Port {remote_port}
	header_up Original-URI {uri}
	copy_headers {
		Tailscale-User>X-Webauth-User
		Tailscale-Name>X-Webauth-Name
		Tailscale-Login>X-Webauth-Login
		Tailscale-Tailnet>X-Webauth-Tailnet
		Tailscale-Profile-Picture>X-Webauth-Profile-Picture
	}
}
```
