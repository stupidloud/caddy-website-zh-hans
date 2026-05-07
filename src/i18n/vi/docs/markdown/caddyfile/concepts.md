---
title: Các khái niệm Caddyfile
---

<a id="caddyfile-concepts"></a>
# Các khái niệm Caddyfile

Tài liệu này sẽ giúp bạn tìm hiểu chi tiết về HTTP Caddyfile.

1. [Cấu trúc](#structure)
	- [Các khối (Blocks)](#blocks)
	- [Các chỉ thị (Directives)](#directives)
	- [Token và dấu ngoặc kép](#tokens-and-quotes)
2. [Các tùy chọn toàn cục](#global-options)
3. [Địa chỉ](#addresses)
4. [Các bộ khớp (Matchers)](#matchers)
5. [Các trình giữ chỗ (Placeholders)](#placeholders)
6. [Các đoạn mã (Snippets)](#snippets)
7. [Các tuyến đường có tên (Named Routes)](#named-routes)
8. [Chú thích](#comments)
9. [Các biến môi trường](#environment-variables)



<a id="structure"></a>
## Cấu trúc

Cấu trúc của Caddyfile có thể được mô tả trực quan:

<style>
	:root {
		--struct-border-global: #e74c3c;
		--struct-border-snippet: #2ecc71;
		--struct-border-site: #3498db;
		--struct-border-matcher: #d453d4;
		--struct-bg-1: #edf5fd;
		--struct-bg-2: #f8fbfd;
		--struct-bg-end: 100%;
		--struct-fg: #254048;
		--struct-opt-name-bg: #ffd9dd;
		--struct-opt-name-fg: #7a2a39;
		--struct-opt-value-bg: #f4dec6;
		--struct-opt-value-fg: #5a3723;
		--struct-comment-bg: #d2d7d8;
		--struct-comment-fg: #495456;
		--struct-site-addr-bg: #cbe4f2;
		--struct-site-addr-fg: #1f6f9a;
		--struct-directive-bg: #c8f7d6;
		--struct-directive-fg: #14663a;
		--struct-matcher-token-bg: #ffd6ff;
		--struct-matcher-token-fg: #6f2070;
		--struct-arg-bg: #ded0ff;
		--struct-arg-fg: #4b2f7a;
		--struct-subdir-bg: #dbbca2;
		--struct-subdir-fg: #5b3a25;
	}
	html.dark {
		--struct-border-global: #e74c3c;
		--struct-border-snippet: #2ecc71;
		--struct-border-site: #3498db;
		--struct-border-matcher: #d453d4;
		--struct-bg-1: #0d313c;
		--struct-bg-2: transparent;
		--struct-bg-end: 120%;
		--struct-fg: #cbd6da;
		--struct-opt-name-bg: #6b2630;
		--struct-opt-name-fg: #ffd9dd;
		--struct-opt-value-bg: #68412b;
		--struct-opt-value-fg: #f4dec6;
		--struct-comment-bg: #2f424d;
		--struct-comment-fg: #e8eef0;
		--struct-site-addr-bg: #204d59;
		--struct-site-addr-fg: #d6f0ff;
		--struct-directive-bg: #1f4e36;
		--struct-directive-fg: #c8f7d6;
		--struct-matcher-token-bg: #65305a;
		--struct-matcher-token-fg: #ffd6ff;
		--struct-arg-bg: #3b2e46;
		--struct-arg-fg: #ded0ff;
		--struct-subdir-bg: #6a4a2e;
		--struct-subdir-fg: #ebc095;
	}
	/* color variables - easy to tweak */
	.struct-caddyfile-visual-repl {
		display: block;
		margin: 0;
		padding: 0;
	}
	/* default (light) visual background */
	.struct-caddyfile-visual-repl .struct-visual {
		box-sizing: border-box;
		margin: 0 0 1.25rem;
		padding: 14px;
		border-radius: 14px;
		background: linear-gradient(to bottom, var(--struct-bg-1) 0%, var(--struct-bg-2) var(--struct-bg-end));
		color: var(--struct-fg);
		font-family: Inter, 'Source Sans Pro', Arial, system-ui, sans-serif;
		line-height: 1.2;
	}
	/* layout */
	.struct-caddyfile-visual-repl .struct-panel {
		display: flex;
		gap: 18px;
		align-items: flex-start;
		flex-wrap: wrap;
	}
	.struct-caddyfile-visual-repl .struct-diagram {
		flex: 1;
		padding: 8px 8px;
	}
	.struct-caddyfile-visual-repl .struct-legend {
		width: 310px;
		padding: 12px 4px;
	}
	/* code-like box: use normal whitespace so HTML pretty-printing won't leak source indentation */
	.struct-caddyfile-visual-repl .struct-code-box {
		background: transparent;
		border-radius: 8px;
		padding: 6px 6px !important;
		font-family: var(--monospace-fonts);
		font-size: 90%;
		white-space: normal;
	}
	.struct-block {
		border-radius: 8px;
		padding: 10px;
		margin: 0 0 10px 0;
	}
	.struct-block.global {
		border: 4px solid var(--struct-border-global);
	}
	.struct-block.snippet {
		border: 4px solid var(--struct-border-snippet);
	}
	.struct-block.site {
		border: 4px solid var(--struct-border-site);
	}
	.struct-block.matcher {
		border: 4px solid var(--struct-border-matcher);
		margin: 8px 8px 10px 10px;
		padding: 8px;
		border-radius: 6px;
	}
	.struct-token, .struct-opt-name, .struct-opt-value, .struct-comment, .struct-site-addr, .struct-directive, .struct-matcher-token, .struct-arg, .struct-subdir {
		display: inline !important;
		padding: .03rem .18rem !important;
		border-radius: 6px;
		font-family: var(--monospace-fonts);
		font-size: 95%;
		vertical-align: middle;
	}
	.struct-opt-name {
		background: var(--struct-opt-name-bg);
		color: var(--struct-opt-name-fg);
	}
	.struct-opt-value {
		background: var(--struct-opt-value-bg);
		color: var(--struct-opt-value-fg);
	}
	.struct-comment {
		background: var(--struct-comment-bg);
		color: var(--struct-comment-fg);
	}
	.struct-site-addr {
		background: var(--struct-site-addr-bg);
		color: var(--struct-site-addr-fg);
	}
	.struct-directive {
		background: var(--struct-directive-bg);
		color: var(--struct-directive-fg);
	}
	.struct-matcher-token {
		background: var(--struct-matcher-token-bg);
		color: var(--struct-matcher-token-fg);
	}
	.struct-arg {
		background: var(--struct-arg-bg);
		color: var(--struct-arg-fg);
	}
	.struct-subdir {
		background: var(--struct-subdir-bg);
		color: var(--struct-subdir-fg);
	}
	.struct-legend .struct-legend-title {
		font-weight: 700;
		font-size: 1.6rem;
	}
	.struct-legend .struct-item {
		display: flex;
		align-items: center;
		gap: 10px;
		margin: 16px 0;
	}
	.struct-legend .struct-item-spacer {
		height: 8px;
	}
	/* swatch for border-based legend items (blocks) */
	.struct-legend .struct-swatch-border {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		border: 4px solid transparent;
		background: transparent;
	}
	/* swatch for filled legend items (text backgrounds) */
	.struct-legend .struct-swatch-fill {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		background: transparent;
	}
	.struct-legend .struct-label {
		font-size: 90%;
		color: inherit;
	}
	.struct-caddyfile-visual-repl .struct-visual, .struct-caddyfile-visual-repl .struct-panel, .struct-caddyfile-visual-repl .struct-diagram, .struct-caddyfile-visual-repl .struct-legend, .struct-caddyfile-visual-repl .struct-code-box {
		margin: 0;
	}
	/* force compact vertical rhythm and explicit indenting so global CSS can't leak in
		NOTE: use normal whitespace so server-side HTML formatting doesn't create visible gaps */
	.struct-line {
		display: block !important;
		margin: 0 !important;
		padding: 2px 0 !important;
		line-height: 1.2 !important;
		white-space: normal !important;
	}
	/* helper to visually indent lines (do not rely on source file whitespace)
		use an explicit spacer element so HTML formatting won't affect alignment */
	.struct-line.struct-indent {
		padding-left: 0 !important;
	}
	.struct-indent-spacer {
		display: inline-block;
		width: 1.2rem;
		height: 1px;
		margin-right: 0.18rem;
	}
	/* smaller spacer for sub-directive / nested lines */
	.struct-subindent-spacer {
		display: inline-block;
		width: 0.9rem;
		height: 1px;
		margin-right: 0.12rem;
	}
</style>

<div class="struct-caddyfile-visual-repl fullwidth">
	<div class="struct-visual">
		<div class="struct-panel">
			<div class="struct-diagram">
				<div class="struct-code-box">
					<div class="struct-block global">
						<div class="struct-line">{</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">email</span> <span class="struct-opt-value">you@yours.com</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">servers</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">trusted_proxies</span> <span class="struct-arg">static</span> <span class="struct-arg">private_ranges</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block snippet">
						<div class="struct-line">(snippet) {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-comment"># this is a reusable snippet</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">log</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">output</span> <span class="struct-arg">file</span> <span class="struct-arg">/var/log/access.log</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line"><span class="struct-site-addr">example.com</span> {</div>
						<div class="struct-block matcher">
							<div class="struct-line"><span class="struct-matcher-token">@post</span> {</div>
							<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-matcher-token">method</span> <span class="struct-arg">POST</span></div>
							<div class="struct-line">}</div>
						</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">reverse_proxy</span> <span class="struct-matcher-token">@post</span> <span class="struct-arg">localhost:9001</span> <span class="struct-arg">localhost:9002</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">lb_policy</span> <span class="struct-arg">first</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">file_server</span> <span class="struct-matcher-token">/static</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">import</span> <span class="struct-arg">snippet</span></div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line struct-indent"><span class="struct-site-addr">www.example.com</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">redir</span> <span class="struct-arg">https://example.com{uri}</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">import</span> <span class="struct-arg">snippet</span></div>
						<div class="struct-line">}</div>
					</div>
				</div>
			</div>
			<div class="struct-legend" aria-hidden="false">
				<div class="struct-legend-title">Chú giải</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">Khối tùy chọn toàn cục</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">Đoạn mã (Snippet)</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">Khối trang web</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">Định nghĩa bộ khớp</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">Tên tùy chọn</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">Giá trị tùy chọn</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">Chú thích</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">Địa chỉ trang web</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">Chỉ thị</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">Token bộ khớp</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">Đối số</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">Chỉ thị con</div></div>
			</div>
		</div>
	</div>
</div>

Các điểm chính:

- Một [**khối tùy chọn toàn cục**](#global-options) tùy chọn có thể là phần đầu tiên trong tệp.

- [Các đoạn mã (Snippets)](#snippets) hoặc [các tuyến đường có tên (named routes)](#named-routes) có thể xuất hiện tiếp theo tùy chọn.

- Nếu không, dòng đầu tiên của Caddyfile **luôn luôn** là [địa chỉ](#addresses) của trang web cần phục vụ.

- Tất cả các [chỉ thị (directives)](#directives) và [bộ khớp (matchers)](#matchers) **phải** nằm trong một khối trang web. Không có phạm vi toàn cục hoặc tính kế thừa giữa các khối trang web.

- Nếu chỉ có một khối trang web, các dấu ngoặc nhọn `{ }` của nó là tùy chọn.

Một Caddyfile bao gồm ít nhất một hoặc nhiều khối trang web, luôn bắt đầu bằng một hoặc nhiều [địa chỉ](#addresses) cho trang web. Bất kỳ chỉ thị nào xuất hiện trước địa chỉ sẽ gây nhầm lẫn cho trình phân tích cú pháp.


<a id="blocks"></a>
### Các khối (Blocks)

Việc mở và đóng một **khối** được thực hiện bằng các dấu ngoặc nhọn:

```
... {
	...
}
```

- Dấu ngoặc nhọn mở `{` phải ở cuối dòng và phía trước là một khoảng trắng.

- Dấu ngoặc nhọn đóng `}` phải nằm trên dòng riêng của nó.

Khi chỉ có một khối trang web, các dấu ngoặc nhọn (và thụt đầu dòng) là tùy chọn. Điều này nhằm mang lại sự tiện lợi để nhanh chóng định nghĩa một trang web duy nhất, ví dụ, điều này:

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

tương đương với:

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

khi bạn chỉ có một khối trang web duy nhất; đó là vấn đề sở thích.

Để cấu hình nhiều trang web với cùng một Caddyfile, bạn **phải** sử dụng dấu ngoặc nhọn xung quanh mỗi khối để tách biệt cấu hình của chúng:

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

Nếu một yêu cầu khớp với nhiều khối trang web, khối trang web có địa chỉ khớp cụ thể nhất sẽ được chọn. Các yêu cầu không đổ xuống (cascade) các khối trang web khác.


<a id="directives"></a>
### Các chỉ thị (Directives)

[**Các chỉ thị (Directives)**](/docs/caddyfile/directives) là các từ khóa chức năng giúp tùy chỉnh cách trang web được phục vụ. Chúng **phải** xuất hiện bên trong các khối trang web. Ví dụ, một cấu hình máy chủ tệp hoàn chỉnh có thể trông như thế này:

```caddy
localhost {
	file_server
}
```

Hoặc một proxy ngược (reverse proxy):

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

Trong các ví dụ này, [`file_server`](/docs/caddyfile/directives/file_server) và [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) là các chỉ thị. Chỉ thị là từ đầu tiên trên một dòng trong khối trang web.

Trong ví dụ thứ hai, `localhost:9000` là một **đối số (argument)** vì nó xuất hiện trên cùng một dòng sau chỉ thị.

Đôi khi các chỉ thị có thể mở các khối của riêng chúng. **Các chỉ thị con (Subdirectives)** xuất hiện ở đầu mỗi dòng trong các khối chỉ thị:

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

Ở đây, `lb_policy` là một chỉ thị con của [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) (nó thiết lập chính sách cân bằng tải để sử dụng giữa các backend).

**Trừ khi có tài liệu hướng dẫn khác, các chỉ thị không thể được sử dụng bên trong các khối chỉ thị khác.** Ví dụ, [`basic_auth`](/docs/caddyfile/directives/basic_auth) không thể được sử dụng bên trong [`file_server`](/docs/caddyfile/directives/file_server) vì máy chủ tệp không biết cách thực hiện xác thực; nhưng bạn có thể sử dụng các chỉ thị bên trong các khối [`route`](/docs/caddyfile/directives/route), [`handle`](/docs/caddyfile/directives/handle), và [`handle_path`](/docs/caddyfile/directives/handle_path) vì chúng được thiết kế đặc biệt để nhóm các chỉ thị lại với nhau.

Lưu ý rằng khi HTTP Caddyfile được chuyển đổi (adapted), các chỉ thị trình xử lý HTTP được sắp xếp theo một [thứ tự chỉ thị](/docs/caddyfile/directives#directive-order) mặc định cụ thể trừ khi nằm trong khối [`route`](/docs/caddyfile/directives/route), vì vậy thứ tự xuất hiện của các chỉ thị không quan trọng ngoại trừ trong các khối `route`.


<a id="tokens-and-quotes"></a>
### Token và dấu ngoặc kép

Caddyfile được phân tích thành các token trước khi được phân tích cú pháp. Khoảng trắng rất quan trọng trong Caddyfile, vì các token được phân tách bằng khoảng trắng.

Thông thường, các chỉ thị yêu cầu một số lượng đối số nhất định; nếu một đối số duy nhất có giá trị chứa khoảng trắng, nó sẽ được phân tích thành hai token riêng biệt:

```caddy-d
directive abc def
```

Điều này có thể gây rắc rối và dẫn đến lỗi hoặc hành vi không mong muốn.

Nếu `abc def` được coi là giá trị của một đối số duy nhất, nó cần được đặt trong dấu ngoặc kép:

```caddy-d
directive "abc def"
```

Dấu ngoặc kép cũng có thể được thoát (escaped) nếu bạn cần sử dụng dấu ngoặc kép bên trong các token được trích dẫn:

```caddy-d
directive "\"abc def\""
```

Để tránh việc thoát dấu ngoặc kép, thay vào đó bạn có thể sử dụng các dấu phẩy ngược (backticks) <code>\` \`</code> để bao quanh các token; ví dụ:

```caddy-d
directive `{"foo": "bar"}`
```

Bên trong các token được trích dẫn, tất cả các ký tự khác đều được xử lý theo nghĩa đen, bao gồm cả khoảng trắng, tab và xuống dòng. Do đó, các token nhiều dòng là hoàn toàn khả thi:

```caddy-d
directive "first line
	second line"
```

Heredocs <span id="heredocs"/> cũng được hỗ trợ:

```caddy
example.com {
	respond <<HTML
		<html>
		  <head><title>Foo</title></head>
		  <body>Foo</body>
		</html>
		HTML 200
}
```

Dấu đánh dấu heredoc mở đầu phải bắt đầu bằng `<<`, theo sau là bất kỳ văn bản nào (khuyên dùng các chữ cái viết hoa). Dấu đánh dấu heredoc kết thúc phải là cùng một văn bản đó (trong ví dụ trên là `HTML`). Dấu đánh dấu mở đầu có thể được thoát bằng `\<<` để ngăn chặn việc phân tích cú pháp heredoc nếu cần thiết.

Dấu đánh dấu kết thúc có thể được thụt đầu dòng, điều này làm cho mỗi dòng văn bản bị loại bỏ bấy nhiêu khoảng thụt đầu dòng (lấy cảm hứng từ [PHP](https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc)), giúp tăng khả năng đọc bên trong các [khối](#blocks) trong khi vẫn cho phép kiểm soát tốt khoảng trắng trong văn bản token. Dòng mới ở cuối cũng bị loại bỏ, nhưng có thể được giữ lại bằng cách thêm một dòng trống bổ sung trước dấu đánh dấu kết thúc.

Các token bổ sung có thể theo sau dấu đánh dấu kết thúc như là các đối số cho chỉ thị (chẳng hạn như trong ví dụ trên là mã trạng thái `200`).


<a id="global-options"></a>
## Các tùy chọn toàn cục

Một Caddyfile có thể tùy chọn bắt đầu bằng một khối đặc biệt không có khóa, được gọi là [khối tùy chọn toàn cục](/docs/caddyfile/options):

```caddy
{
	...
}
```

Nếu có, nó phải là khối đầu tiên trong cấu hình.

Nó được sử dụng để thiết lập các tùy chọn áp dụng trên toàn cục, hoặc không cụ thể cho bất kỳ trang web nào. Bên trong, chỉ các tùy chọn toàn cục mới có thể được thiết lập; bạn không thể sử dụng các chỉ thị trang web thông thường trong đó.

Ví dụ, để bật tùy chọn toàn cục `debug`, vốn thường được sử dụng để tạo ra nhật ký chi tiết nhằm khắc phục sự cố:

```caddy
{
	debug
}
```

**[Đọc trang Các tùy chọn toàn cục](/docs/caddyfile/options) để tìm hiểu thêm.**



<a id="addresses"></a>
## Địa chỉ

Một địa chỉ luôn xuất hiện ở đầu khối trang web, và thường là phần đầu tiên trong Caddyfile.

Dưới đây là các ví dụ về các địa chỉ hợp lệ:

| Địa chỉ              | Hiệu quả                            |
|----------------------|-----------------------------------|
| `example.com`        | HTTPS với [chứng chỉ tin cậy công khai](/docs/automatic-https#hostname-requirements) được quản lý |
| `*.example.com`      | HTTPS với [chứng chỉ tin cậy công khai đại diện (wildcard)](/docs/caddyfile/patterns#wildcard-certificates) được quản lý |
| `localhost`          | HTTPS với [chứng chỉ tin cậy cục bộ](/docs/automatic-https#local-https) được quản lý |
| `http://`            | HTTP bắt tất cả (catch-all), bị ảnh hưởng bởi [`http_port`](/docs/caddyfile/options#http-port) |
| `https://`           | HTTPS bắt tất cả (catch-all), bị ảnh hưởng bởi [`https_port`](/docs/caddyfile/options#http-port) |
| `http://example.com` | HTTP rõ ràng, với một bộ khớp `Host` |
| `example.com:443`    | HTTPS do khớp với mặc định của [`https_port`](/docs/caddyfile/options#http-port) |
| `:443`               | HTTPS bắt tất cả do khớp với mặc định của [`https_port`](/docs/caddyfile/options#http-port) |
| `:8080`              | HTTP trên cổng không tiêu chuẩn, không có bộ khớp `Host` |
| `localhost:8080`     | HTTPS trên cổng không tiêu chuẩn, do có một tên miền hợp lệ |
| `https://example.com:443` | HTTPS, nhưng việc có cả `https://` và `:443` là dư thừa |
| `127.0.0.1` | HTTPS, với chứng chỉ IP tin cậy cục bộ |
| `http://127.0.0.1` | HTTP, với bộ khớp `Host` là một địa chỉ IP (từ chối `localhost`) |


<aside class="tip">

[HTTPS tự động](/docs/automatic-https) được bật nếu địa chỉ trang web của bạn chứa tên máy chủ (hostname) hoặc địa chỉ IP. Tuy nhiên, hành vi này hoàn toàn là ngầm định, vì vậy nó không bao giờ ghi đè lên bất kỳ cấu hình rõ ràng nào.

Ví dụ, nếu địa chỉ của trang web là `http://example.com`, HTTPS tự động sẽ không kích hoạt vì giao thức (scheme) được chỉ định rõ ràng là `http://`.

</aside>


Từ địa chỉ, Caddy có thể suy luận ra giao thức, máy chủ và cổng của trang web của bạn. Nếu địa chỉ không có cổng, Caddyfile sẽ chọn cổng khớp với giao thức nếu được chỉ định, hoặc mặc định sẽ là cổng 443.

Nếu bạn chỉ định một tên máy chủ, chỉ các yêu cầu có tiêu đề `Host` khớp mới được chấp nhận. Nói cách khác, nếu địa chỉ trang web là `localhost`, thì Caddy sẽ không khớp các yêu cầu đến `127.0.0.1`.

Các ký tự đại diện (`*`) có thể được sử dụng, nhưng chỉ để đại diện cho đúng một nhãn của tên máy chủ. Ví dụ, `*.example.com` khớp với `foo.example.com` nhưng không khớp với `foo.bar.example.com`, và `*` khớp với `localhost` nhưng không khớp với `example.com`. Xem [mô hình chứng chỉ đại diện (wildcard)](/docs/caddyfile/patterns#wildcard-certificates) để biết ví dụ thực tế.

Để bắt tất cả các máy chủ, hãy bỏ qua phần máy chủ của địa chỉ, ví dụ, chỉ đơn giản là `https://`. Điều này hữu ích khi sử dụng [TLS theo yêu cầu (On-Demand TLS)](/docs/automatic-https#on-demand-tls), khi bạn không biết trước các tên miền.

Nếu nhiều trang web có cùng định nghĩa, bạn có thể liệt kê tất cả chúng cùng nhau, phân tách bằng dấu cách và dấu phẩy (cần ít nhất một dấu cách). Ba ví dụ sau đây là tương đương:

```caddy
<a id="comma-separated-site-addresses"></a>
# Các địa chỉ trang web được phân tách bằng dấu phẩy
localhost:8080, example.com, www.example.com {
	...
}
```

hoặc

```caddy
<a id="space-separated-site-addresses"></a>
# Các địa chỉ trang web được phân tách bằng dấu cách
localhost:8080 example.com www.example.com {
	...
}
```

hoặc

```caddy
<a id="comma-and-new-line-separated-site-addresses"></a>
# Các địa chỉ trang web được phân tách bằng dấu phẩy và dòng mới
localhost:8080,
example.com,
www.example.com {
	...
}
```

Một địa chỉ phải là duy nhất; bạn không thể chỉ định cùng một địa chỉ nhiều hơn một lần.

[Các trình giữ chỗ (Placeholders)](#placeholders) **không thể** được sử dụng trong địa chỉ, nhưng bạn có thể sử dụng các [biến môi trường](#environment-variables) theo kiểu Caddyfile trong đó:

```caddy
{$DOMAIN:localhost} {
	...
}
```

Theo mặc định, các trang web liên kết (bind) trên tất cả các giao diện mạng. Nếu bạn muốn ghi đè điều này, hãy sử dụng [chỉ thị `bind`](/docs/caddyfile/directives/bind) hoặc [tùy chọn toàn cục `default_bind`](/docs/caddyfile/options#default-bind).



<a id="matchers"></a>
## Các bộ khớp (Matchers)

Các [chỉ thị (directives)](#directives) trình xử lý HTTP áp dụng cho tất cả các yêu cầu theo mặc định (trừ khi có tài liệu hướng dẫn khác).

[Các bộ khớp yêu cầu (Request matchers)](/docs/caddyfile/matchers) có thể được sử dụng để phân loại các yêu cầu theo một tiêu chí nhất định. Với các bộ khớp, bạn có thể chỉ định chính xác các yêu cầu nào mà một chỉ thị nhất định áp dụng cho.

Đối với các chỉ thị hỗ trợ bộ khớp, đối số đầu tiên sau chỉ thị là **token bộ khớp (matcher token)**. Dưới đây là một số ví dụ:

```caddy-d
root *           /var/www  # token bộ khớp: *
root /index.html /var/www  # token bộ khớp: /index.html
root @post       /var/www  # token bộ khớp: @post
```

Token bộ khớp có thể được bỏ qua hoàn toàn để khớp với tất cả các yêu cầu; ví dụ, không cần cung cấp `*` nếu đối số tiếp theo không giống một bộ khớp đường dẫn (path matcher).

**[Đọc trang Các bộ khớp yêu cầu](/docs/caddyfile/matchers) để tìm hiểu thêm.**




<a id="placeholders"></a>
## Các trình giữ chỗ (Placeholders)

[Các trình giữ chỗ (Placeholders)](/docs/conventions#placeholders) là một cách đơn giản để đưa các giá trị động vào cấu hình tĩnh của bạn. Chúng có thể được sử dụng làm đối số cho các chỉ thị và chỉ thị con.

Các trình giữ chỗ được giới hạn ở cả hai đầu bằng các dấu ngoặc nhọn `{ }` và chứa mã định danh bên trong, ví dụ: `{foo.bar}`. Dấu ngoặc nhọn mở của trình giữ chỗ có thể được thoát `\{like.this}` để ngăn chặn việc thay thế. Các mã định danh trình giữ chỗ thường được đặt trong không gian tên bằng dấu chấm để tránh xung đột giữa các mô-đun.

Các trình giữ chỗ nào có sẵn tùy thuộc vào ngữ cảnh. Không phải tất cả các trình giữ chỗ đều có sẵn trong tất cả các phần của cấu hình. Ví dụ, [ứng dụng HTTP thiết lập các trình giữ chỗ](/docs/json/apps/http/#docs) chỉ khả dụng trong các khu vực của cấu hình liên quan đến việc xử lý các yêu cầu HTTP (tức là trong các [chỉ thị (directives)](#directives) và [bộ khớp (matchers)](#matchers) trình xử lý HTTP, nhưng _không_ có trong [cấu hình `tls`](/docs/caddyfile/directives/tls)). Một số chỉ thị hoặc bộ khớp cũng có thể thiết lập các trình giữ chỗ của riêng chúng, có thể được sử dụng bởi bất kỳ thứ gì theo sau chúng. Một số trình giữ chỗ [có sẵn trên toàn cầu](/docs/conventions#placeholders).

Bạn có thể sử dụng bất kỳ trình giữ chỗ nào trong Caddyfile, nhưng để thuận tiện, bạn cũng có thể sử dụng một số từ viết tắt tương đương sau đây vốn sẽ được mở rộng khi Caddyfile được phân tích cú pháp:

| Caddyfile        | Thay thế cho                            |
|------------------|-------------------------------------|
| `{cookie.*}`     | `{http.request.cookie.*}`           |
| `{client_ip}`    | `{http.vars.client_ip}`             |
| `{dir}`          | `{http.request.uri.path.dir}`       |
| `{err.*}`        | `{http.error.*}`                    |
| `{file_match.*}` | `{http.matchers.file.*}`            |
| `{file.base}`    | `{http.request.uri.path.file.base}` |
| `{file.ext}`     | `{http.request.uri.path.file.ext}`  |
| `{file}`         | `{http.request.uri.path.file}`      |
| `{header.*}`     | `{http.request.header.*}`           |
| `{host}`         | `{http.request.host}`               |
| `{hostport}`     | `{http.request.hostport}`           |
| `{labels.*}`     | `{http.request.host.labels.*}`      |
| `{method}`       | `{http.request.method}`             |
| `{orig_method}`  | `{http.request.orig_method}`        |
| `{orig_uri}`     | `{http.request.orig_uri}`           |
| `{orig_path}`    | `{http.request.orig_uri.path}`      |
| `{orig_dir}`     | `{http.request.orig_uri.path.dir}`  |
| `{orig_file}`    | `{http.request.orig_uri.path.file}` |
| `{orig_query}`   | `{http.request.orig_uri.query}`     |
| `{orig_?query}`  | `{http.request.orig_uri.prefixed_query}` |
| `{path.*}`       | `{http.request.uri.path.*}`         |
| `{path}`         | `{http.request.uri.path}`           |
| `{%path}`        | `{http.request.uri.path_escaped}`   |
| `{port}`         | `{http.request.port}`               |
| `{query.*}`      | `{http.request.uri.query.*}`        |
| `{query}`        | `{http.request.uri.query}`          |
| `{%query}`       | `{http.request.uri.query_escaped}`  |
| `{?query}`       | `{http.request.uri.prefixed_query}` |
| `{re.*}`         | `{http.regexp.*}`                   |
| `{remote_host}`  | `{http.request.remote.host}`        |
| `{remote_port}`  | `{http.request.remote.port}`        |
| `{remote}`       | `{http.request.remote}`             |
| `{rp.*}`         | `{http.reverse_proxy.*}`            |
| `{resp.*}`       | `{http.intercept.*}`                |
| `{scheme}`       | `{http.request.scheme}`             |
| `{tls_cipher}`   | `{http.request.tls.cipher_suite}`   |
| `{tls_client_certificate_der_base64}` | `{http.request.tls.client.certificate_der_base64}` |
| `{tls_client_certificate_pem}`        | `{http.request.tls.client.certificate_pem}` |
| `{tls_client_fingerprint}`            | `{http.request.tls.client.fingerprint}`     |
| `{tls_client_issuer}`                 | `{http.request.tls.client.issuer}`          |
| `{tls_client_serial}`                 | `{http.request.tls.client.serial}`          |
| `{tls_client_subject}`                | `{http.request.tls.client.subject}`         |
| `{tls_version}`       | `{http.request.tls.version}`             |
| `{upstream_hostport}` | `{http.reverse_proxy.upstream.hostport}` |
| `{uri}`               | `{http.request.uri}`                     |
| `{%uri}`              | `{http.request.uri_escaped}`             |
| `{vars.*}`            | `{http.vars.*}`                          |

Không phải tất cả các trường cấu hình đều hỗ trợ các trình giữ chỗ, nhưng hầu hết đều hỗ trợ ở những nơi bạn mong đợi. Việc hỗ trợ các trình giữ chỗ cần được thêm vào các trường đó một cách rõ ràng. Các tác giả plugin có thể [đọc bài viết này](/docs/extending-caddy/placeholders) để tìm hiểu cách thêm hỗ trợ trình giữ chỗ trong các mô-đun của riêng họ.




<a id="snippets"></a>
## Các đoạn mã (Snippets)

Bạn có thể định nghĩa các khối đặc biệt được gọi là các đoạn mã (snippets) bằng cách đặt tên cho chúng bên trong dấu ngoặc đơn:

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

Và sau đó bạn có thể tái sử dụng điều này ở bất cứ đâu bạn cần, bằng cách sử dụng chỉ thị đặc biệt [`import`](/docs/caddyfile/directives/import):

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

Chỉ thị [`import`](/docs/caddyfile/directives/import) cũng có thể được sử dụng để chèn các tệp khác vào vị trí của nó. Nếu đối số không khớp với một đoạn mã đã được định nghĩa, nó sẽ được thử như một tệp. Nó cũng hỗ trợ các ký tự đại diện (globs) để nhập nhiều tệp. Trong một trường hợp đặc biệt, nó có thể xuất hiện ở bất kỳ đâu trong Caddyfile (ngoại trừ làm đối số cho một chỉ thị khác), bao gồm cả bên ngoài các khối trang web:

```caddy
{
	email admin@example.com
}

import sites/*
```

Bạn có thể truyền các đối số cho một cấu hình được nhập (các đoạn mã hoặc tệp) và sử dụng chúng như sau:

```caddy
(snippet) {
	respond "Yahaha! Bạn đã tìm thấy {args[0]}!"
}

a.example.com {
	import snippet "Example A"
}

b.example.com {
	import snippet "Example B"
}
```

⚠️ <i>Thử nghiệm</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Bạn cũng có thể truyền một khối tùy chọn cho một đoạn mã được nhập và sử dụng chúng như sau.

```caddy
(snippet) {
	{block}
	respond "OK"
}

a.example.com {
	import snippet {
		header +foo bar
	}
}

b.example.com {
	import snippet {
		header +bar foo
	}
}
```

**[Đọc trang chỉ thị `import`](/docs/caddyfile/directives/import) để tìm hiểu thêm.**


<a id="named-routes"></a>
## Các tuyến đường có tên (Named Routes)

⚠️ <i>Thử nghiệm</i>

Các tuyến đường có tên (Named routes) sử dụng cú pháp tương tự như [các đoạn mã (snippets)](#snippets); chúng là một khối đặc biệt được định nghĩa bên ngoài các khối trang web, bắt đầu bằng `&(` và kết thúc bằng `)` với tên ở giữa.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

Và sau đó bạn có thể tái sử dụng tuyến đường có tên này bên trong bất kỳ trang web nào:

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

Điều này đặc biệt hữu ích để giảm mức sử dụng bộ nhớ nếu cùng một tuyến đường cần thiết trong nhiều trang web khác nhau, hoặc nếu cần nhiều điều kiện bộ khớp khác nhau để gọi cùng một tuyến đường.

**[Đọc trang chỉ thị `invoke`](/docs/caddyfile/directives/invoke) để tìm hiểu thêm.**



<a id="comments"></a>
## Chú thích

Các chú thích bắt đầu bằng `#` và kéo dài cho đến hết dòng:

```caddy-d
<a id="comments-can-start-a-line"></a>
# Các chú thích có thể bắt đầu một dòng
directive  # hoặc nằm ở cuối
```

Ký tự thăng `#` cho một chú thích không thể xuất hiện ở giữa một token (tức là nó phải được bắt đầu bằng một khoảng trắng hoặc xuất hiện ở đầu dòng). Điều này cho phép sử dụng các dấu thăng bên trong URI hoặc các giá trị khác mà không cần trích dẫn.



<a id="environment-variables"></a>
## Các biến môi trường

Nếu cấu hình của bạn dựa trên các biến môi trường, bạn có thể sử dụng chúng trong Caddyfile:

```caddy
{$ENV}
```

Các biến môi trường ở dạng này được thay thế **trước khi quá trình phân tích cú pháp Caddyfile bắt đầu**, vì vậy chúng có thể mở rộng thành các giá trị trống (tức là `""`), các token một phần, các token hoàn chỉnh, hoặc thậm chí là nhiều token và nhiều dòng.

Ví dụ, một biến môi trường `UPSTREAMS="app1:8080 app2:8080 app3:8080"` sẽ mở rộng thành nhiều [token](#tokens-and-quotes):

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

Một giá trị mặc định có thể được chỉ định cho trường hợp không tìm thấy biến môi trường, bằng cách sử dụng `:` làm dấu phân cách giữa tên biến và giá trị mặc định:

```caddy
{$DOMAIN:localhost} {

}
```

Nếu bạn muốn **trì hoãn việc thay thế** một biến môi trường cho đến khi chạy (runtime), bạn có thể sử dụng các [trình giữ chỗ `{env.*}` tiêu chuẩn](/docs/conventions#placeholders). Lưu ý rằng không phải tất cả các tham số cấu hình đều hỗ trợ các trình giữ chỗ này, vì các nhà phát triển mô-đun cần thêm một dòng mã để thực hiện việc thay thế. Nếu nó có vẻ không hoạt động, vui lòng gửi một issue để yêu cầu hỗ trợ.

Ví dụ, nếu bạn đã cài đặt [plugin `caddy-dns/cloudflare` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns/cloudflare) cài đặt và muốn cấu hình [thách thức DNS (DNS challenge)](/docs/automatic-https#dns-challenge), bạn có thể truyền biến môi trường `CLOUDFLARE_API_TOKEN` của mình cho plugin như sau:

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Nếu bạn đang chạy Caddy dưới dạng dịch vụ systemd, hãy xem [các hướng dẫn này](/docs/running#overrides) để thiết lập ghi đè dịch vụ nhằm định nghĩa các biến môi trường của bạn.
