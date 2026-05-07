---
title: handle_path (chỉ thị Caddyfile)
---

<script>
ready(function() {
	// Add a link to [<path_matcher>] as a special case for this directive.
	// The matcher text includes <> characters which are parsed as HTML,
	// so we must use text() to change the link text.
	$$_('pre.chroma .s').forEach(item => {
		if (item.innerText.includes('<path_matcher>')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			item.innerHTML = `<a href="/docs/caddyfile/matchers#path-matchers" style="color: inherit;" title="Matcher token">${text}</a>`;
			item.classList.remove('s');
			item.classList.add('nd');
		}
	});
});
</script>

# handle_path

Hoạt động giống như [chỉ thị `handle`](handle), nhưng ngầm sử dụng [`uri strip_prefix`](uri) để loại bỏ tiền tố đường dẫn khớp.

Xử lý một yêu cầu khớp với một đường dẫn nhất định (trong khi loại bỏ đường dẫn đó khỏi URI yêu cầu) là một trường hợp sử dụng phổ biến đến mức nó có chỉ thị riêng để thuận tiện.


<a id="syntax"></a>
## Cú pháp

```caddy-d
handle_path <path_matcher> {
	<directives...>
}
```

- **<directives...>** là danh sách các chỉ thị xử lý HTTP hoặc các khối chỉ thị, mỗi dòng một chỉ thị, giống như cách sử dụng bên ngoài khối `handle_path`.

Chỉ chấp nhận một [trình khớp đường dẫn (path matcher)](/docs/caddyfile/matchers#path-matchers) duy nhất và là bắt buộc; bạn không thể sử dụng các trình khớp đã đặt tên (named matchers) với `handle_path`.

<a id="examples"></a>
## Ví dụ

Cấu hình này:

```caddy-d
handle_path /prefix/* {
	...
}
```

👆 về cơ bản giống với cái này 👇, nhưng dạng `handle_path` 👆 ngắn gọn hơn một chút

```caddy-d
handle /prefix/* {
	uri strip_prefix /prefix
	...
}
```

Một ví dụ Caddyfile đầy đủ, trong đó `handle_path` và `handle` loại trừ lẫn nhau; nhưng, hãy lưu ý về [vấn đề thư mục con <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575)

```caddy
example.com {
	# Phục vụ API của bạn, loại bỏ tiền tố /api
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# Phục vụ trang web tĩnh của bạn
	handle {
		root /srv
		file_server
	}
}
```
