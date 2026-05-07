---
title: Các mẫu Caddyfile phổ biến
---

<a id="common-caddyfile-patterns"></a>
# Các mẫu Caddyfile phổ biến

Trang này trình bày một vài cấu hình Caddyfile hoàn chỉnh và tối giản cho các trường hợp sử dụng phổ biến. Đây có thể là những điểm bắt đầu hữu ích cho các tài liệu Caddyfile của riêng bạn.

Đây không phải là các giải pháp lắp-là-chạy (drop-in); bạn sẽ phải tùy chỉnh tên miền, cổng/socket, đường dẫn thư mục, v.v. Chúng nhằm mục đích minh họa một số mẫu cấu hình phổ biến nhất.

- [Máy chủ tệp tĩnh](#static-file-server)
- [Proxy ngược](#reverse-proxy)
- [PHP](#php)
- [Chuyển hướng miền phụ `www.`](#redirect-www-subdomain)
- [Dấu gạch chéo ở cuối](#trailing-slashes)
- [Chứng chỉ Wildcard](#wildcard-certificates)
- [Ứng dụng đơn trang (SPAs)](#single-page-apps-spas)
- [Caddy làm proxy cho một Caddy khác](#caddy-proxying-to-another-caddy)


<a id="static-file-server"></a>
## Máy chủ tệp tĩnh

```caddy
example.com {
	root /var/www
	file_server
}
```

Như thường lệ, dòng đầu tiên là địa chỉ trang web. [Chỉ thị `root`](/docs/caddyfile/directives/root) chỉ định đường dẫn đến thư mục gốc của trang web (`*` có nghĩa là khớp với tất cả các yêu cầu, để phân biệt với một [trình khớp đường dẫn](/docs/caddyfile/matchers#path-matchers))&mdash;hãy thay đổi đường dẫn đến trang web của bạn nếu nó không phải là thư mục làm việc hiện tại. Cuối cùng, chúng ta bật [máy chủ tệp tĩnh](/docs/caddyfile/directives/file_server).



<a id="reverse-proxy"></a>
## Proxy ngược

Proxy tất cả các yêu cầu:

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

Chỉ proxy các yêu cầu có đường dẫn bắt đầu bằng `/api/` và phục vụ tệp tĩnh cho mọi thứ khác:

```caddy
example.com {
	root /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

Cấu hình này sử dụng một [trình khớp yêu cầu](/docs/caddyfile/matchers#syntax) để chỉ khớp các yêu cầu bắt đầu bằng `/api/` và proxy chúng đến backend. Tất cả các yêu cầu khác sẽ được phục vụ từ thư mục [`root`](/docs/caddyfile/directives/root) của trang web bằng [máy chủ tệp tĩnh](/docs/caddyfile/directives/file_server). Điều này cũng phụ thuộc vào thực tế là `reverse_proxy` có [thứ tự chỉ thị](/docs/caddyfile/directives#directive-order) cao hơn `file_server`.

Có nhiều [ví dụ về `reverse_proxy` khác tại đây](/docs/caddyfile/directives/reverse_proxy#examples).



## PHP

### PHP-FPM

Với dịch vụ PHP FastCGI đang chạy, cấu hình như thế này sẽ hoạt động cho hầu hết các ứng dụng PHP hiện đại:

```caddy
example.com {
	root /srv/public
	encode
	php_fastcgi localhost:9000
	file_server
}
```

Tùy chỉnh thư mục gốc của trang web cho phù hợp; ví dụ này giả định rằng thư mục gốc web của ứng dụng PHP của bạn nằm trong thư mục `public`&mdash;các yêu cầu cho các tệp tồn tại trên đĩa sẽ được phục vụ bằng [`file_server`](/docs/caddyfile/directives/file_server), và bất kỳ thứ gì khác sẽ được định tuyến đến `index.php` để ứng dụng PHP xử lý.

Đôi khi bạn có thể sử dụng unix socket để kết nối với PHP-FPM:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[Chỉ thị `php_fastcgi`](/docs/caddyfile/directives/php_fastcgi) thực chất chỉ là một lối tắt cho [nhiều phần cấu hình](/docs/caddyfile/directives/php_fastcgi#expanded-form).


### FrankenPHP

Ngoài ra, bạn có thể sử dụng [FrankenPHP](https://frankenphp.dev/), một bản phân phối của Caddy gọi PHP trực tiếp bằng CGO (Go to C bindings). Nó có thể nhanh hơn tới 4 lần so với PHP-FPM, và thậm chí còn tốt hơn nếu bạn có thể sử dụng chế độ worker.

```caddy
{
    frankenphp
    order php_server before file_server
}

example.com {
	root /srv/public
    encode zstd br gzip
    php_server
}
```


<a id="redirect-subdomain"></a>
<a id="redirect-www-subdomain"></a>
## Chuyển hướng miền phụ `www.`

Để **thêm** miền phụ `www.` bằng chuyển hướng HTTP:

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


Để **loại bỏ** nó:

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


Để loại bỏ nó cho **nhiều tên miền** cùng lúc; cấu hình này sử dụng các trình giữ chỗ `{labels.*}` là các phần của tên máy chủ, được đánh chỉ mục từ `0` tính từ bên phải (ví dụ: `0`=`com`, `1`=`example-one`, `2`=`www`):

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```



<a id="trailing-slashes"></a>
## Dấu gạch chéo ở cuối

Thông thường bạn sẽ không cần phải tự cấu hình việc này; [chỉ thị `file_server`](/docs/caddyfile/directives/file_server) sẽ tự động thêm hoặc loại bỏ các dấu gạch chéo ở cuối từ các yêu cầu thông qua chuyển hướng HTTP, tùy thuộc vào việc tài nguyên được yêu cầu tương ứng là một thư mục hay một tệp.

Tuy nhiên, nếu cần thiết, bạn vẫn có thể bắt buộc sử dụng dấu gạch chéo ở cuối với cấu hình của mình. Có hai cách để thực hiện: nội bộ hoặc bên ngoài.

<a id="internal-enforcement"></a>
### Bắt buộc nội bộ

Cách này sử dụng chỉ thị [`rewrite`](/docs/caddyfile/directives/rewrite). Caddy sẽ viết lại URI nội bộ để thêm hoặc loại bỏ dấu gạch chéo ở cuối:

```caddy
example.com {
	rewrite /add     /add/
	rewrite /remove/ /remove
}
```

Sử dụng việc viết lại, các yêu cầu có và không có dấu gạch chéo ở cuối sẽ như nhau.


<a id="external-enforcement"></a>
### Bắt buộc bên ngoài

Cách này sử dụng chỉ thị [`redir`](/docs/caddyfile/directives/redir). Caddy sẽ yêu cầu trình duyệt thay đổi URI để thêm hoặc loại bỏ dấu gạch chéo ở cuối:

```caddy
example.com {
	redir /add     /add/
	redir /remove/ /remove
}
```

Sử dụng chuyển hướng, máy khách sẽ phải gửi lại yêu cầu, bắt buộc một URI duy nhất được chấp nhận cho một tài nguyên.



<a id="wildcard-certificates"></a>
## Chứng chỉ Wildcard

Đối với hầu hết các nhà cấp phát bao gồm Let's Encrypt, bạn phải bật [thử thách ACME DNS](/docs/automatic-https#dns-challenge) để Caddy tự động hóa các chứng chỉ wildcard.

Với thử thách DNS được bật, kể từ Caddy 2.10, Caddy sẽ ưu tiên một chứng chỉ wildcard áp dụng được đã được cấu hình hoặc quản lý trước khi quản lý một chứng chỉ riêng biệt cho một miền phụ.



Nếu bạn cần phục vụ nhiều miền phụ với cùng một chứng chỉ wildcard, cách tốt nhất để xử lý chúng là sử dụng Caddyfile như thế này, tận dụng [chỉ thị `handle`](/docs/caddyfile/directives/handle) và [trình khớp `host`](/docs/caddyfile/matchers#host):

```caddy
*.example.com {
	tls {
		dns <provider_name> [<params...>]
	}

	@foo host foo.example.com
	handle @foo {
		respond "Foo!"
	}

	@bar host bar.example.com
	handle @bar {
		respond "Bar!"
	}

	# Phương án dự phòng cho các tên miền chưa được xử lý khác
	handle {
		abort
	}
}
```

Bạn phải bật [thử thách ACME DNS](/docs/automatic-https#dns-challenge) để Caddy tự động quản lý các chứng chỉ wildcard.



<a id="single-page-apps-spas"></a>
## Ứng dụng đơn trang (SPAs)

Khi một trang web tự thực hiện việc định tuyến, máy chủ có thể nhận được rất nhiều yêu cầu cho các trang không tồn tại phía máy chủ, nhưng có thể hiển thị phía máy khách miễn là tệp chỉ mục duy nhất được phục vụ thay thế. Các ứng dụng web được kiến trúc theo cách này được gọi là SPAs, hoặc các ứng dụng đơn trang.

Ý tưởng chính là để máy chủ "thử các tệp" (try files) xem tệp được yêu cầu có tồn tại phía máy chủ hay không, và nếu không, sẽ quay lại tệp chỉ mục nơi máy khách thực hiện việc định tuyến (thường bằng JavaScript phía máy khách).

Một cấu hình SPA điển hình thường trông như thế này:

```caddy
example.com {
	root /srv
	encode
	try_files {path} /index.html
	file_server
}
```

Nếu SPA của bạn đi kèm với API hoặc các điểm cuối chỉ dành cho máy chủ khác, bạn sẽ muốn sử dụng các khối `handle` để xử lý chúng một cách riêng biệt:

```caddy
example.com {
	encode

	handle /api/* {
		reverse_proxy backend:8000
	}

	handle {
		root /srv
		try_files {path} /index.html
		file_server
	}
}
```

Nếu tệp `index.html` của bạn chứa các tham chiếu đến các tài sản JS/CSS với tên tệp đã được băm, bạn có thể cân nhắc thêm tiêu đề `Cache-Control` để hướng dẫn máy khách *không* lưu nó vào bộ nhớ đệm (để nếu tài sản thay đổi, trình duyệt sẽ tải những tài sản mới). Vì việc viết lại `try_files` được sử dụng để phục vụ `index.html` của bạn từ bất kỳ đường dẫn nào không khớp với một tệp khác trên đĩa, bạn có thể bao bọc `try_files` bằng một `route` để trình xử lý `header` chạy *sau* khi viết lại (thông thường nó sẽ chạy trước do [thứ tự chỉ thị](/docs/caddyfile/directives#directive-order)):

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```


<a id="caddy-proxying-to-another-caddy"></a>
## Caddy làm proxy cho một Caddy khác

Nếu bạn có một thực thể Caddy có thể truy cập công khai (hãy gọi nó là "front"), và một thực thể Caddy khác trong mạng nội bộ của bạn (hãy gọi nó là "back") phục vụ ứng dụng thực tế của bạn, bạn có thể sử dụng [chỉ thị `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) để chuyển tiếp các yêu cầu qua đó.

Thực thể Front:

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

Thực thể Back:

```caddy
{
	servers {
		trusted_proxies static private_ranges
	}
}

http://foo.example.com {
	reverse_proxy foo-app:8080
}

http://bar.example.com {
	reverse_proxy bar-app:9000
}
```

- Ví dụ này phục vụ hai tên miền khác nhau, proxy cả hai đến cùng một thực thể Caddy back, trên cổng `80`. Thực thể back của bạn đang phục vụ hai tên miền theo các cách khác nhau, vì vậy nó được cấu hình với hai khối trang web riêng biệt.

- Ở phía back, [`http://`](/docs/caddyfile/concepts#addresses) được sử dụng để chấp nhận HTTP trên cổng `80`. Thực thể front kết thúc TLS, và lưu lượng giữa front và back nằm trên một mạng nội bộ, vì vậy không cần phải mã hóa lại nó.

- Bạn có thể sử dụng một cổng khác như `8080` trên thực thể back nếu cần; chỉ cần thêm `:8080` vào mỗi địa chỉ trang web trên cấu hình của back, HOẶC đặt [tùy chọn toàn cục `http_port`](/docs/caddyfile/options#http_port) thành `8080`.

- Ở phía back, [tùy chọn toàn cục `trusted_proxies`](/docs/caddyfile/options#trusted_proxies) được sử dụng để thông báo cho Caddy tin tưởng thực thể front như một proxy. Điều này đảm bảo IP thực của máy khách được bảo toàn.

- Đi xa hơn nữa, bạn có thể có nhiều hơn một thực thể back để thực hiện [cân bằng tải](/docs/caddyfile/balancing) giữa chúng. Bạn có thể thiết lập mTLS (mutual TLS) bằng cách sử dụng [`acme_server`](/docs/caddyfile/directives/acme_server) trên thực thể front sao cho nó hoạt động như một CA cho thực thể back (hữu ích nếu lưu lượng giữa front và back đi qua các mạng không tin cậy).
