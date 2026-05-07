---
title: php_fastcgi (chỉ thị Caddyfile)
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# php_fastcgi

Một chỉ thị mang tính định hướng (opinionated) giúp chuyển tiếp các yêu cầu (proxy) đến máy chủ PHP FastCGI như php-fpm.

- [Cú pháp](#syntax)
- [Dạng mở rộng](#expanded-form)
  - [Giải thích](#explanation)
- [Ví dụ](#examples)

Chỉ thị [`reverse_proxy`](reverse_proxy) của Caddy có khả năng phục vụ bất kỳ ứng dụng FastCGI nào, nhưng chỉ thị này được thiết kế dành riêng cho các ứng dụng PHP. Chỉ thị này là một phím tắt tiện lợi, thay thế cho một [cấu hình dài hơn](#expanded-form).

Nó giả định rằng bất kỳ tệp `index.php` nào tại thư mục gốc của trang web đều đóng vai trò là một bộ định tuyến (router). Nếu điều đó không mong muốn, hãy định cấu hình lại [chỉ thị con `try_files`](#try_files) để sửa đổi hành vi viết lại (rewrite) mặc định, hoặc sử dụng [dạng mở rộng](#expanded-form) làm cơ sở và tùy chỉnh theo nhu cầu của bạn.

Ngoài các chỉ thị con được liệt kê dưới đây, chỉ thị này cũng hỗ trợ tất cả các chỉ thị con của [`reverse_proxy`](reverse_proxy#syntax). Ví dụ, bạn có thể bật cân bằng tải và kiểm tra tình trạng (health checks).

**Hầu hết các ứng dụng PHP hiện đại hoạt động tốt mà không cần thêm chỉ thị con hoặc tùy chỉnh.** Các chỉ thị con thường chỉ được sử dụng trong một số trường hợp đặc biệt hoặc với các ứng dụng PHP cũ.

<a id="syntax"></a>
## Cú pháp

```caddy-d
php_fastcgi [<matcher>] <php-fpm_gateways...> {
	root <path>
	split <substrings...>
	index <filename>|off
	try_files <files...>
	env [<key> <value>]
	resolve_root_symlink
	capture_stderr
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>

	<any other reverse_proxy subdirectives...>
}
```

- **<php-fpm_gateways...>** là các [địa chỉ mạng](/docs/conventions#network-addresses) của máy chủ FastCGI. Thông thường là một TCP socket hoặc một tệp unix socket.

- **root** <span id="root"/> đặt thư mục gốc cho trang web. Khuyến nghị luôn sử dụng [chỉ thị `root`](root) kết hợp với `php_fastcgi`, nhưng việc ghi đè điều này có thể hữu ích khi thượng nguồn (upstream) PHP-FPM của bạn đang sử dụng một thư mục gốc khác với Caddy (xem [ví dụ](#docker)). Mặc định là giá trị của [chỉ thị `root`](root) nếu được sử dụng, nếu không sẽ mặc định là thư mục làm việc hiện tại của Caddy.

- **split** <span id="split"/> đặt các chuỗi con để chia URI thành hai phần. Chuỗi con khớp đầu tiên sẽ được sử dụng để tách "path info" khỏi đường dẫn. Phần đầu tiên được gắn hậu tố là chuỗi con khớp và sẽ được giả định là tên tài nguyên thực tế (CGI script). Phần thứ hai sẽ được đặt thành PATH_INFO để tập lệnh CGI sử dụng. Mặc định: `.php`

- **index** <span id="index"/> chỉ định tên tệp để coi là tệp chỉ mục thư mục. Điều này ảnh hưởng đến trình khớp tệp (file matcher) trong [dạng mở rộng](#expanded-form). Mặc định: `index.php`. Có thể đặt thành `off` để tắt tính năng viết lại dự phòng (rewrite fallback) về `index.php` khi không tìm thấy tệp khớp.

- **try_files** <span id="try_files"/> chỉ định ghi đè cho việc viết lại try-files mặc định. Xem [chỉ thị `try_files`](try_files) để biết chi tiết. Mặc định: `{path} {path}/index.php index.php`.

- **env** <span id="env"/> đặt thêm một biến môi trường với giá trị đã cho. Có thể được chỉ định nhiều lần cho nhiều biến môi trường. Theo mặc định, tất cả các biến môi trường FastCGI liên quan đã được thiết lập (bao gồm cả các tiêu đề HTTP) nhưng bạn có thể thêm hoặc ghi đè các biến nếu cần.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> khi thư mục [`root`](#root) là một liên kết biểu tượng (symlink), tùy chọn này cho phép phân giải nó thành giá trị thực tế của nó. Điều này đôi khi được sử dụng như một chiến lược triển khai, bằng cách chỉ cần hoán đổi symlink để trỏ đến phiên bản mới trong một thư mục khác. Bị tắt theo mặc định để tránh các lệnh gọi hệ thống lặp đi lặp lại.

- **capture_stderr** <span id="capture_stderr"/> cho phép ghi lại và ghi nhật ký bất kỳ thông báo nào được gửi bởi máy chủ fastcgi thượng nguồn trên `stderr`. Việc ghi nhật ký được thực hiện ở mức `WARN` theo mặc định. Nếu phản hồi có trạng thái `4xx` hoặc `5xx`, thì mức `ERROR` sẽ được sử dụng thay thế. Theo mặc định, `stderr` bị bỏ qua.

- **dial_timeout** <span id="dial_timeout"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập thời gian chờ khi kết nối với socket thượng nguồn. Mặc định: `3s`.

- **read_timeout** <span id="read_timeout"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập thời gian chờ khi đọc từ FastCGI thượng nguồn. Mặc định: không có thời gian chờ.

- **write_timeout** <span id="write_timeout"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập thời gian chờ khi gửi đến FastCGI thượng nguồn. Mặc định: không có thời gian chờ.


Vì chỉ thị này là một trình bao bọc (wrapper) mang tính định hướng dựa trên reverse proxy, bạn có thể sử dụng bất kỳ chỉ thị con nào của [`reverse_proxy`](reverse_proxy#syntax) để tùy chỉnh nó.


<a id="expanded-form"></a>
## Dạng mở rộng

Chỉ thị `php_fastcgi` (không có các chỉ thị con) tương đương với cấu hình sau. Hầu hết các ứng dụng PHP hiện đại hoạt động tốt với thiết lập sẵn này. Nếu ứng dụng của bạn không như vậy, hãy thoải mái mượn từ cấu hình này và tùy chỉnh nó khi cần thiết thay vì sử dụng phím tắt `php_fastcgi`.

```caddy-d
route {
	# Thêm dấu gạch chéo cuối cho các yêu cầu thư mục
	# Việc chuyển hướng này sẽ tự động bị tắt nếu "{http.request.uri.path}/index.php"
	# không xuất hiện trong danh sách try_files
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# Nếu tệp được yêu cầu không tồn tại, hãy thử các tệp chỉ mục và giả định index.php luôn tồn tại
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# Chuyển tiếp các tệp PHP tới bộ phản hồi FastCGI
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```

<a id="explanation"></a>
### Giải thích

- Phần đầu tiên xử lý việc chuẩn hóa đường dẫn yêu cầu. Mục tiêu là đảm bảo rằng các yêu cầu hướng tới một thư mục trên đĩa thực sự có dấu gạch chéo cuối `/` được thêm vào đường dẫn yêu cầu, sao cho chỉ có một URL duy nhất là hợp lệ cho các yêu cầu tới thư mục đó.

  Việc chuẩn hóa này chỉ xảy ra nếu chỉ thị con `try_files` chứa `{path}/index.php` (mặc định).

  Điều này được thực hiện bằng cách sử dụng một trình khớp yêu cầu chỉ khớp với các yêu cầu _không_ kết thúc bằng dấu gạch chéo và trỏ đến một thư mục trên đĩa có chứa tệp `index.php`, và nếu nó khớp, sẽ thực hiện chuyển hướng HTTP 308 với dấu gạch chéo cuối được thêm vào. Ví dụ, nó sẽ chuyển hướng một yêu cầu với đường dẫn `/foo` sang `/foo/` (thêm một dấu `/`, để chuẩn hóa đường dẫn đến thư mục), nếu `/foo/index.php` tồn tại trên đĩa.

- Phần tiếp theo xử lý việc thực hiện viết lại đường dẫn dựa trên việc liệu một tệp khớp có tồn tại trên đĩa hay không. Điều này cũng có tác dụng phụ là ghi nhớ phần đường dẫn sau `.php` (nếu đường dẫn yêu cầu có chứa `.php`). Điều này quan trọng để Caddy thiết lập chính xác các biến môi trường FastCGI.

  - Đầu tiên, nó kiểm tra xem `{path}` có phải là một tệp tồn tại trên đĩa hay không. Nếu có, nó sẽ viết lại sang đường dẫn đó. Điều này về cơ bản sẽ ngắt các bước còn lại và đảm bảo rằng các yêu cầu tới các tệp _thực sự tồn tại_ trên đĩa không bị viết lại theo cách khác (xem các bước tiếp theo bên dưới). Vì vậy, ví dụ nếu bạn có tệp `/js/app.js` trên đĩa, thì yêu cầu tới đường dẫn đó sẽ được giữ nguyên.

  - Thứ hai, nó kiểm tra xem `{path}/index.php` có phải là một tệp tồn tại trên đĩa hay không. Nếu có, nó sẽ viết lại sang đường dẫn đó. Đối với các yêu cầu tới một thư mục như `/foo/`, nó sẽ tìm kiếm `/foo//index.php` (được chuẩn hóa thành `/foo/index.php`) và viết lại yêu cầu sang đường dẫn đó nếu nó tồn tại. Hành vi này đôi khi hữu ích nếu bạn đang chạy một ứng dụng PHP khác trong một thư mục con của webroot.

  - Cuối cùng, nó sẽ luôn viết lại thành `index.php` (tệp này hầu như luôn tồn tại đối với các ứng dụng PHP hiện đại). Điều này cho phép ứng dụng PHP của bạn xử lý bất kỳ yêu cầu nào cho các đường dẫn _không_ trỏ đến các tệp trên đĩa, bằng cách sử dụng tập lệnh `index.php` làm điểm truy cập (entrypoint) của nó.

- Và cuối cùng, phần cuối cùng là những gì thực sự chuyển tiếp yêu cầu đến dịch vụ PHP FastCGI (hoặc PHP-FPM) của bạn để thực sự chạy mã PHP của bạn. Trình khớp yêu cầu sẽ chỉ khớp với các yêu cầu kết thúc bằng `.php`, vì vậy, bất kỳ tệp nào _không phải_ là tập lệnh PHP và _có_ tồn tại trên đĩa, sẽ _không_ được xử lý bởi chỉ thị này và sẽ được bỏ qua.

Chỉ thị `php_fastcgi` thường không đủ nếu đứng một mình. Nó hầu như luôn phải được kết hợp với [chỉ thị `root`](root) để thiết lập vị trí các tệp của bạn trên đĩa (đối với các ứng dụng PHP hiện đại, đây có thể là `/var/www/html/public`, trong đó thư mục `public` là nơi chứa `index.php` của bạn) và [chỉ thị `file_server`](file_server) để phục vụ các tệp tĩnh của bạn (JS, CSS, hình ảnh, v.v.) mà không được xử lý bởi chỉ thị này.



<a id="examples"></a>
## Ví dụ

Chuyển tiếp tất cả các yêu cầu PHP tới bộ phản hồi FastCGI đang lắng nghe tại `127.0.0.1:9000`:

```caddy-d
php_fastcgi 127.0.0.1:9000
```

Tương tự, nhưng chỉ đối với các yêu cầu dưới `/blog/`:

```caddy-d
php_fastcgi /blog/* localhost:9000
```

Khi sử dụng PHP-FPM lắng nghe qua một unix socket:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[Chỉ thị `root`](root) hầu như luôn được sử dụng để chỉ định thư mục chứa các tập lệnh PHP và [chỉ thị `file_server`](file_server) để phục vụ các tệp tĩnh:

```caddy
example.com {
	root /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<span id="docker"/> Khi phục vụ nhiều ứng dụng PHP với Caddy, webroot của bạn cho mỗi ứng dụng phải khác nhau để Caddy có thể đọc và phục vụ các tệp tĩnh của bạn một cách riêng biệt và phát hiện xem các tệp PHP có tồn tại hay không.

Nếu bạn đang sử dụng Docker, thông thường các container PHP-FPM của bạn sẽ có các tệp được gắn kết tại cùng một thư mục gốc. Trong trường hợp đó, giải pháp là gắn kết các tệp vào container Caddy của bạn trong các thư mục khác nhau, sau đó sử dụng [chỉ thị con `root`](#root) để thiết lập thư mục gốc cho mỗi container:

```caddy
app1.example.com {
	root /srv/app1/public
	php_fastcgi app1:9000 {
		root /var/www/html/public
	}
	file_server
}

app2.example.com {
	root /srv/app2/public
	php_fastcgi app2:9000 {
		root /var/www/html/public
	}
	file_server
}
```

Đối với một trang web PHP không sử dụng `index.php` làm điểm truy cập, bạn có thể thiết lập dự phòng để phát ra lỗi `404`. Lỗi này có thể được bắt và xử lý bằng [chỉ thị `handle_errors`](handle_errors):

```caddy
example.com {
	php_fastcgi localhost:9000 {
		try_files {path} {path}/index.php =404
	}

	handle_errors {
		respond "{err.status_code} {err.status_text}"
	}
}
