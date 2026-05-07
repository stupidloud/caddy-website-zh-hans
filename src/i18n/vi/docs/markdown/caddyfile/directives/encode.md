---
title: encode (chỉ thị Caddyfile)
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();

	// Response matchers
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#status" style="color: inherit;" title="Response matcher">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers#header" style="color: inherit;" title="Response matcher">header</a>';
		}
	});
});
</script>

# encode

Mã hóa các phản hồi bằng cách sử dụng (các) kiểu mã hóa đã định cấu hình. Một cách sử dụng điển hình cho mã hóa là nén.

<a id="syntax"></a>
## Cú pháp

```caddy-d
encode [<matcher>] [<formats...>] {
	# encoding formats
	gzip [<level>]
	zstd [<level>]
	
	minimum_length <length>

	match <inline_response_matcher>
}
```

- **&lt;formats...&gt;** là danh sách các định dạng mã hóa để kích hoạt. Nếu nhiều kiểu mã hóa được kích hoạt, kiểu mã hóa sẽ được chọn dựa trên tiêu đề Accept-Encoding của yêu cầu; nếu máy khách không có sự ưu tiên mạnh mẽ (q-factor), thì kiểu mã hóa được hỗ trợ đầu tiên sẽ được sử dụng. Nếu bị bỏ qua, `zstd` (được ưu tiên) và `gzip` được bật theo mặc định.

- **gzip** <span id="gzip"/> kích hoạt nén Gzip, tùy chọn ở một mức độ cụ thể.

- **zstd** <span id="zstd"/> kích hoạt nén Zstandard, tùy chọn ở một mức độ cụ thể (các giá trị có thể = default, fastest, better, best). Mức nén mặc định tương đương với chế độ Zstandard mặc định (cấp độ 3). 

- **minimum_length** <span id="minimum_length"/> số byte tối thiểu mà một phản hồi phải có để được mã hóa (mặc định: 512).

- **match** <span id="match"/> là một [trình khớp phản hồi (response matcher)](/docs/caddyfile/response-matchers). Chỉ các phản hồi khớp mới được mã hóa. Mặc định trông như thế này:

  ```caddy-d
  match {
  	header Content-Type application/atom+xml*
  	header Content-Type application/eot*
  	header Content-Type application/font*
  	header Content-Type application/geo+json*
  	header Content-Type application/graphql+json*
  	header Content-Type application/javascript*
  	header Content-Type application/json*
  	header Content-Type application/ld+json*
  	header Content-Type application/manifest+json*
  	header Content-Type application/opentype*
  	header Content-Type application/otf*
  	header Content-Type application/rss+xml*
  	header Content-Type application/truetype*
  	header Content-Type application/ttf*
  	header Content-Type application/vnd.api+json*
  	header Content-Type application/vnd.ms-fontobject*
  	header Content-Type application/wasm*
  	header Content-Type application/x-httpd-cgi*
  	header Content-Type application/x-javascript*
  	header Content-Type application/x-opentype*
  	header Content-Type application/x-otf*
  	header Content-Type application/x-perl*
  	header Content-Type application/x-protobuf*
  	header Content-Type application/x-ttf*
  	header Content-Type application/xhtml+xml*
  	header Content-Type application/xml*
  	header Content-Type font/*
  	header Content-Type image/svg+xml*
  	header Content-Type image/vnd.microsoft.icon*
  	header Content-Type image/x-icon*
  	header Content-Type multipart/bag*
  	header Content-Type multipart/mixed*
  	header Content-Type text/*
  }
  ```


<a id="examples"></a>
## Ví dụ

Kích hoạt nén Gzip:

```caddy-d
encode gzip
```

Kích hoạt nén Zstandard và Gzip (với Zstandard được ưu tiên ngầm định, vì nó đứng trước):

```caddy-d
encode zstd gzip
```

Vì đây là giá trị mặc định, cấu hình trước đó hoàn toàn tương đương với:

```caddy-d
encode
```

Và trong một trang web đầy đủ, nén các tệp tĩnh được phục vụ bởi [`file_server`](file_server):

```caddy
example.com {
	root /srv
	encode
	file_server
}
```
