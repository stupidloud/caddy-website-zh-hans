---
title: intercept (Chỉ thị Caddyfile)
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#response-matcher" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Response matchers
	const nameMatchers = Array.from($$_('pre.chroma .nd')).filter(item => item.innerText.includes('@name'));
	if (nameMatchers.length > 0) {
		const first = nameMatchers[0];
		const span = document.createElement('span');
		span.className = 'nd';
		first.parentNode.insertBefore(span, first);
		span.appendChild(first);
		span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;">@name</a>';
	}
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText === 'status') {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;">status</a>';
		}
	});
	
	const headerElements = $$_('pre.chroma .k');
	for (let item of headerElements) {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;">header</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# intercept

Một sự trừu tượng hóa khái quát của tính năng [chặn phản hồi (response interception)](reverse_proxy#intercepting-responses) từ [chỉ thị `reverse_proxy`](reverse_proxy). Chỉ thị này có thể được sử dụng với bất kỳ trình xử lý (handler) nào tạo ra phản hồi, bao gồm cả những trình xử lý từ các plugin như `php_server` của [FrankenPHP](https://frankenphp.dev/).

Chỉ thị này cho phép bạn [khớp các phản hồi](/docs/caddyfile/response-matchers), và luồng `handle_response` hoặc `replace_status` khớp đầu tiên sẽ được thực thi. Khi được thực thi, thân phản hồi (body) ban đầu sẽ được giữ lại, tạo cơ hội cho luồng đó ghi một thân phản hồi khác, với mã trạng thái mới hoặc với bất kỳ thao tác tiêu đề phản hồi (response header) cần thiết nào. Nếu luồng đó _không_ ghi thân phản hồi mới, thì thân phản hồi ban đầu sẽ được ghi thay thế.


<a id="syntax"></a>
## Cú pháp

```caddy-d
intercept [<matcher>] {
	@name {
		status <code...>
		header <field> [<value>]
	}

	replace_status [<response_matcher>] <code>

	handle_response [<response_matcher>] {
		<directives...>
	}
}
```

- **@name** là một khối [trình khớp phản hồi (response matcher)](/docs/caddyfile/response-matchers) được đặt tên. Miễn là mỗi trình khớp phản hồi có một tên duy nhất, nhiều trình khớp có thể được xác định. Một phản hồi có thể được khớp dựa trên mã trạng thái và sự hiện diện hoặc giá trị của một tiêu đề phản hồi.

- **replace_status** <span id="replace_status"/> chỉ đơn giản là thay đổi mã trạng thái của phản hồi khi khớp với trình khớp được đưa ra.

- **handle_response** <span id="handle_response"/> xác định luồng sẽ thực thi khi phản hồi ban đầu khớp với trình khớp phản hồi được đưa ra. Nếu trình khớp bị bỏ qua, tất cả các phản hồi đều bị chặn. Khi nhiều khối `handle_response` được xác định, khối khớp đầu tiên sẽ được áp dụng. Bên trong khối, tất cả các [chỉ thị (directives)](/docs/caddyfile/directives) khác đều có thể được sử dụng.

Trong các luồng `handle_response`, các trình giữ chỗ (placeholders) sau đây có sẵn để lấy thông tin từ phản hồi ban đầu:

- `{resp.status_code}` Mã trạng thái của phản hồi ban đầu.

- `{resp.header.*}` Các tiêu đề từ phản hồi ban đầu.


<a id="examples"></a>
## Ví dụ

Khi sử dụng `php_server` của [FrankenPHP](https://frankenphp.dev/), bạn có thể sử dụng `intercept` để triển khai hỗ trợ `X-Accel-Redirect`, phục vụ các tệp tĩnh theo yêu cầu của ứng dụng PHP:

```caddy
localhost {
	root /srv

	intercept {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {resp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}

	php_server
}
```
