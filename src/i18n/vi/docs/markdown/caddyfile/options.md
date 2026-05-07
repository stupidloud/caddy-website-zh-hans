---
title: Các tùy chọn toàn cục (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the options in the code block at the top
	// to their associated anchor tags.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Add links on comments to their respective sections
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // the leading whitespace
			text = text.slice(text.indexOf('#')); // only the comment part
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Surgically fix a duplicate link; 'name' appears twice as a link
	// for two different sections, so we change the second to #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// Surgically fix `renewal_window_ratio` which appears twice as a link for two different sections, so we change the second to #renewal_window_ratio-1
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>


<a id="global-options"></a>
# Các tùy chọn toàn cục

Caddyfile cung cấp một cách để bạn chỉ định các tùy chọn áp dụng trên toàn cục. Một số tùy chọn hoạt động như các giá trị mặc định; số khác tùy chỉnh các máy chủ HTTP và không chỉ áp dụng cho một trang web cụ thể; trong khi những tùy chọn khác tùy chỉnh hành vi của [adapter](/docs/config-adapters) Caddyfile.

Phần trên cùng của Caddyfile có thể là một **khối tùy chọn toàn cục (global options block)**. Đây là một khối không có khóa:

```caddy
{
	...
}
```

Chỉ có thể có tối đa một khối như vậy và nó phải là khối đầu tiên của Caddyfile.

Các tùy chọn khả thi là (nhấp vào từng tùy chọn để chuyển đến tài liệu tương ứng):

```caddy
{
	# General Options
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hosts...>
	order <dir1> first|last|[before|after <dir2>]
	storage <module_name> {
		<options...>
	}
	storage_clean_interval <duration>
	admin   off|<addr> {
		origins <origins...>
		enforce_origin
	}
	persist_config off
	log [name] {
		output  <writer_module> ...
		format  <encoder_module> ...
		level   <level>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <duration>
	shutdown_delay <duration>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# TLS Options
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <yours>
	default_sni <name>
	fallback_sni <name>
	local_certs
	skip_install_trust
	acme_ca <directory_url>
	acme_ca_root <pem_file>
	acme_eab {
		key_id <key_id>
		mac_key <mac_key>
	}
	acme_dns <provider> ...
	dns <provider> ...
	ech <public_names...> {
		dns <provider> ...
	}
	on_demand_tls {
		ask        <endpoint>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <name> ...
	renew_interval <duration>
	cert_lifetime  <duration>
	ocsp_interval  <duration>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# Server Options
	servers [<listener_address>] {
		name <name>
		listener_wrappers {
			<listener_wrappers...>
		}
		timeouts {
			read_body   <duration>
			read_header <duration>
			write       <duration>
			idle        <duration>
		}
		keepalive_interval <duration>
		keepalive_idle     <duration>
		keepalive_count	   <number>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <headers...>

		trace
		max_header_size <size>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# File Systems
	filesystem <name> <module> {
		<options...>
	}

	# PKI Options
	pki {
		ca [<id>] {
			name                  <name>
			root_cn               <name>
			intermediate_cn       <name>
			intermediate_lifetime <duration>
			maintenance_interval  <duration>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <path>
				key    <path>
			}
			intermediate {
				format <format>
				cert   <path>
				key    <path>
			}
		}
	}

	# Event options
	events {
		on <event> <handler...>
	}
}
```


<a id="general-options"></a>
## Các tùy chọn chung

<a id="debug"></a>
##### `debug`
Kích hoạt chế độ gỡ lỗi (debug mode), thiết lập mức nhật ký (log level) thành `DEBUG` cho [trình ghi nhật ký mặc định (default logger)](#log). Điều này giúp hiển thị nhiều chi tiết hơn, hữu ích khi khắc phục sự cố (và sẽ rất chi tiết trong môi trường sản xuất). Chúng tôi khuyến nghị bạn kích hoạt tùy chọn này trước khi yêu cầu hỗ trợ trên [diễn đàn cộng đồng](https://caddy.community). Ví dụ, ở đầu Caddyfile của bạn, nếu bạn không có tùy chọn toàn cục nào khác:

```caddy
{
	debug
}
```


<a id="httpport"></a>
##### `http_port`
Cổng để máy chủ sử dụng cho HTTP.

**Chỉ dành cho sử dụng nội bộ**; không thay đổi cổng HTTP đối với khách truy cập (clients). Điều này thường được sử dụng nếu trong mạng nội bộ của bạn, bạn cần chuyển tiếp cổng (port forward) `80` sang một cổng khác (ví dụ: `8080`) trước khi nó đến Caddy, vì mục đích định tuyến.

Mặc định: `80`


<a id="httpsport"></a>
##### `https_port`
Cổng để máy chủ sử dụng cho HTTPS.

**Chỉ dành cho sử dụng nội bộ**; không thay đổi cổng HTTPS đối với khách truy cập. Điều này thường được sử dụng nếu trong mạng nội bộ của bạn, bạn cần chuyển tiếp cổng `443` sang một cổng khác (ví dụ: `8443`) trước khi nó đến Caddy, vì mục đích định tuyến.

Mặc định: `443`


<a id="defaultbind"></a>
##### `default_bind`
(Các) địa chỉ ràng buộc (bind address) mặc định được sử dụng cho tất cả các trang web, nếu chỉ thị [`bind`](/docs/caddyfile/directives/bind) không được sử dụng trong trang web đó. Mặc định: để trống, sẽ ràng buộc với tất cả các giao diện mạng.

<aside class="tip">

Hãy lưu ý rằng điều này sẽ chỉ áp dụng cho các máy chủ được tạo ra bởi Caddyfile; điều này có nghĩa là máy chủ HTTP được tạo bởi [HTTPS tự động (Automatic HTTPS)](/docs/automatic-https) để chuyển hướng HTTP sang HTTPS sẽ không kế thừa các địa chỉ ràng buộc này. Để giải quyết vấn đề này, hãy đảm bảo khai báo một trang web `http://` (nó có thể để trống, không có chỉ thị nào) để nó tồn tại khi Caddyfile được chuyển đổi (adapted), nhằm nhận các địa chỉ ràng buộc.

</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



<a id="order"></a>
##### `order`
Gán thứ tự cho (các) chỉ thị trình xử lý (handler) HTTP. Vì các trình xử lý HTTP thực thi trong một chuỗi tuần tự, nên cần phải thực thi các trình xử lý theo đúng thứ tự. Các chỉ thị tiêu chuẩn có [thứ tự được xác định trước](/docs/caddyfile/directives#directive-order), nhưng nếu sử dụng các mô-đun trình xử lý HTTP của bên thứ ba, bạn sẽ cần xác định thứ tự rõ ràng bằng cách sử dụng tùy chọn này hoặc đặt chỉ thị trong một [khối `route`](/docs/caddyfile/directives/route). Thứ tự có thể được mô tả tuyệt đối (`first` hoặc `last`), hoặc tương đối (`before` hoặc `after`) so với một chỉ thị khác.

Ví dụ, để sử dụng [plugin `replace-response`](https://github.com/caddyserver/replace-response), bạn sẽ muốn đảm bảo chỉ thị của nó được sắp xếp sau `encode` để nó có thể thực hiện thay thế trước khi phản hồi được mã hóa (bởi vì các phản hồi luân chuyển ngược lên chuỗi trình xử lý, chứ không phải xuôi xuống):

```caddy
{
	order replace after encode
}
```


<a id="storage"></a>
##### `storage`
Cấu hình cơ chế lưu trữ của Caddy. Mặc định là [`file_system`](/docs/json/storage/file_system/). Có nhiều [mô-đun lưu trữ](/docs/json/storage/) khác có sẵn dưới dạng plugin.

Ví dụ, để thay đổi vị trí lưu trữ của hệ thống tệp:

```caddy
{
	storage file_system /path/to/custom/location
}
```

Việc tùy chỉnh mô-đun lưu trữ thường cần thiết khi đồng bộ hóa lưu trữ của Caddy trên nhiều phiên bản Caddy để đảm bảo tất cả chúng đều sử dụng cùng các chứng chỉ và khóa. Xem [phần HTTPS tự động về lưu trữ](/docs/automatic-https#storage) để biết thêm chi tiết.


<a id="storagecleaninterval"></a>
##### `storage_clean_interval`
Tần suất quét các đơn vị lưu trữ để tìm các tài sản cũ hoặc đã hết hạn và xóa chúng. Các lần quét này tốn nhiều thao tác đọc (và liệt kê) trên mô-đun lưu trữ, vì vậy hãy chọn khoảng thời gian dài hơn cho các triển khai lớn. Chấp nhận các [giá trị khoảng thời gian (duration)](/docs/conventions#durations).

Lưu trữ sẽ luôn được dọn dẹp khi tiến trình khởi động lần đầu. Sau đó, một lần dọn dẹp mới sẽ được bắt đầu sau khoảng thời gian này kể từ khi lần dọn dẹp trước đó bắt đầu, nếu lần dọn dẹp trước đó kết thúc trong ít hơn một nửa thời gian của khoảng thời gian này (nếu không lần khởi động tiếp theo sẽ bị bỏ qua).

Mặc định: `24h`

```caddy
{
	storage_clean_interval 7d
}
```




<a id="admin"></a>
##### `admin`
Tùy chỉnh [điểm cuối API quản trị (admin API endpoint)](/docs/api). Chấp nhận các trình giữ chỗ (placeholders). Nhận [địa chỉ mạng](/docs/conventions#network-addresses).

Mặc định: `localhost:2019`, trừ khi biến môi trường `CADDY_ADMIN` được thiết lập.

Nếu được đặt thành `off`, điểm cuối quản trị sẽ bị vô hiệu hóa. Khi bị vô hiệu hóa, **việc thay đổi cấu hình sẽ là không thể** nếu không dừng và khởi động lại máy chủ, vì [lệnh `caddy reload`](/docs/command-line#caddy-reload) sử dụng API quản trị để đẩy cấu hình mới vào máy chủ đang chạy.

Hãy nhớ sử dụng cờ CLI `--address` với các [lệnh](/docs/command-line) tương thích để chỉ định điểm cuối quản trị hiện tại, nếu địa chỉ của máy chủ đang chạy đã được thay đổi so với mặc định.

Cũng hỗ trợ các tùy chọn phụ sau:

- **origins** cấu hình danh sách các [nguồn gốc (origins)](https://developer.mozilla.org/en-US/docs/Glossary/Origin) được phép kết nối với điểm cuối.

  Mặc định được chọn một cách thông minh:
  - nếu địa chỉ lắng nghe là loopback (ví dụ: `localhost` hoặc IP loopback, hoặc socket unix) thì các nguồn gốc được phép là `localhost`, `::1` và `127.0.0.1`, kết hợp với cổng của địa chỉ lắng nghe (vì vậy `localhost:2019` là một nguồn gốc hợp lệ).
  - nếu địa chỉ lắng nghe không phải là loopback, thì nguồn gốc được phép giống như địa chỉ lắng nghe.

  Nếu máy chủ của địa chỉ lắng nghe không phải là một giao diện đại diện (wildcard interface - bao gồm: chuỗi trống, hoặc `0.0.0.0`, hoặc `[::]`), thì việc thực thi tiêu đề `Host` sẽ được thực hiện. Thực tế, điều này có nghĩa là theo mặc định, tiêu đề `Host` được xác thực là nằm trong `origins`, vì giao diện là `localhost`. Nhưng đối với một địa chỉ như `:2020` có giao diện đại diện, việc xác thực tiêu đề `Host` sẽ không được thực hiện.

- **enforce_origin** bắt buộc thực thi tiêu đề yêu cầu `Origin`. Điều này được thực hiện ngầm định bất cứ khi nào các tiêu đề CORS được gửi bởi khách truy cập hoặc nếu khách truy cập vô hiệu hóa CORS rõ ràng với `Sec-Fetch-Mode: no-cors`. Nếu không, tùy chọn này hữu ích nhất khi địa chỉ lắng nghe là một giao diện đại diện (vì `Host` không được xác thực) và API quản trị được tiếp xúc với internet công cộng. Nó cho phép kiểm tra trước (preflight) CORS và đảm bảo tiêu đề `Origin` được xác thực so với danh sách `origins`. Chỉ sử dụng tùy chọn này nếu bạn đang chạy Caddy trên máy phát triển của mình và cần truy cập API quản trị từ trình duyệt web.

Ví dụ, để tiếp xúc API quản trị trên một cổng khác, trên tất cả các giao diện — ⚠️ cổng này **không nên được tiếp xúc công khai**, nếu không bất kỳ ai cũng có thể điều khiển máy chủ của bạn; cân nhắc việc bật thực thi nguồn gốc nếu bạn cần nó công khai:

```caddy
{
	admin :2020
}
```

Để tắt API quản trị — ⚠️ điều này khiến **việc tải lại cấu hình là không thể** nếu không dừng và khởi động lại máy chủ:

```caddy
{
	admin off
}
```

Để sử dụng một [socket unix](/docs/conventions#network-addresses) cho API quản trị, cho phép kiểm soát truy cập thông qua quyền tệp:

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

Để chỉ cho phép các yêu cầu có tiêu đề `Origin` khớp:

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```



<a id="persistconfig"></a>
##### `persist_config`

Kiểm soát việc cấu hình JSON hiện tại có nên được lưu giữ lâu dài vào [thư mục cấu hình](/docs/conventions#configuration-directory) hay không, để tránh mất các thay đổi cấu hình được thực hiện thông qua API quản trị. Hiện tại, chỉ hỗ trợ tùy chọn `off`. Theo mặc định, cấu hình được lưu giữ lâu dài.

```caddy
{
	persist_config off
}
```



<a id="log"></a>
##### `log`
Cấu hình các trình ghi nhật ký (loggers) có tên.

Tên có thể được truyền vào để chỉ định một trình ghi nhật ký cụ thể để tùy chỉnh hành vi. Nếu không có tên nào được chỉ định, hành vi của trình ghi nhật ký `default` sẽ được sửa đổi. Bạn có thể đọc thêm về trình ghi nhật ký `default` và giải thích về [cách hoạt động của việc ghi nhật ký trong Caddy](/docs/logging).

Nhiều trình ghi nhật ký với tên khác nhau có thể được cấu hình bằng cách sử dụng `log` nhiều lần.

Điều này khác với chỉ thị [`log`](/docs/caddyfile/directives/log), chỉ cấu hình ghi nhật ký yêu cầu HTTP (còn được gọi là nhật ký truy cập - access logs). Tùy chọn toàn cục `log` chia sẻ cấu trúc cấu hình của nó với chỉ thị này (ngoại trừ `include` và `exclude`), và tài liệu đầy đủ có thể được tìm thấy trên trang của chỉ thị.

- **output** cấu hình nơi ghi nhật ký.

  Xem chỉ thị [`log`](/docs/caddyfile/directives/log#output-modules) để biết tài liệu đầy đủ.

- **format** mô tả cách mã hóa hoặc định dạng nhật ký.

  Xem chỉ thị [`log`](/docs/caddyfile/directives/log#format-modules) để biết tài liệu đầy đủ.

- **level** là mức độ tối thiểu để ghi nhật ký.

  Mặc định: `INFO`.

  Các giá trị khả thi: `DEBUG`, `INFO`, `WARN`, `ERROR`, và rất hiếm khi là `PANIC`, `FATAL`.

- **include** chỉ định các tên nhật ký được bao gồm trong trình ghi nhật ký này.

  Theo mặc định, danh sách này để trống (tức là tất cả các nhật ký đều được bao gồm).

  Ví dụ, để chỉ bao gồm các nhật ký được phát ra bởi API quản trị, bạn sẽ bao gồm `admin.api`.

- **exclude** chỉ định các tên nhật ký được loại trừ khỏi trình ghi nhật ký này.

  Theo mặc định, danh sách này để trống (tức là không có nhật ký nào bị loại trừ).

  Ví dụ, để chỉ loại trừ nhật ký truy cập HTTP, bạn sẽ loại trừ `http.log.access`.

Các tên trình ghi nhật ký mà `include` và `exclude` chấp nhận phụ thuộc vào các mô-đun được sử dụng, và cách dễ nhất để khám phá chúng là từ các nhật ký trước đó.

Dưới đây là một ví dụ về việc ghi nhật ký dưới dạng json tất cả các nhật ký truy cập http và nhật ký quản trị vào stdout:

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

<a id="graceperiod"></a>
##### `grace_period`
Xác định thời gian ân hạn (grace period) để tắt các máy chủ HTTP (ví dụ: trong quá trình thay đổi cấu hình hoặc khi Caddy đang dừng).

Trong thời gian ân hạn, không có kết nối mới nào được chấp nhận, các kết nối nhàn rỗi (idle) bị đóng và các kết nối đang hoạt động được chờ đợi một cách thiếu kiên nhẫn để hoàn thành các yêu cầu của chúng. Nếu khách truy cập không hoàn thành các yêu cầu của họ trong thời gian ân hạn, máy chủ sẽ bị buộc chấm dứt để cho phép việc tải lại hoàn tất và giải phóng tài nguyên. Chấp nhận các [giá trị khoảng thời gian](/docs/conventions#durations).

Theo mặc định, thời gian ân hạn là vĩnh viễn, có nghĩa là các kết nối không bao giờ bị buộc đóng.

```caddy
{
	grace_period 10s
}
```


<a id="shutdowndelay"></a>
##### `shutdown_delay`
Xác định một [khoảng thời gian](/docs/conventions#durations)
_trước khi_ [thời gian ân hạn](#grace_period) bắt đầu, trong đó một máy chủ sắp bị dừng vẫn tiếp tục hoạt động bình thường, ngoại trừ trình giữ chỗ `{http.shutting_down}` trả về giá trị `true` và `{http.time_until_shutdown}` cho biết thời gian cho đến khi thời gian ân hạn bắt đầu.

Điều này gây ra sự chậm trễ nếu bất kỳ máy chủ nào bị tắt như một phần của thay đổi cấu hình và thực tế là lên lịch cho sự thay đổi vào một thời điểm muộn hơn. Nó hữu ích cho việc thông báo cho các bộ kiểm tra sức khỏe (health checkers) về sự kết thúc sắp tới của máy chủ này và để dành thời gian cho bộ cân bằng tải (load balancer) đưa nó ra khỏi vòng quay; ví dụ:

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Bye-bye in {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Hello, world!"
	}
}
```


<a id="tls-options"></a>
## Các tùy chọn TLS

<a id="autohttps"></a>
##### `auto_https`
Cấu hình [HTTPS tự động (Automatic HTTPS)](/docs/automatic-https), là tính năng cho phép Caddy tự động quản lý chứng chỉ và chuyển hướng HTTP sang HTTPS cho các trang web của bạn.

Có một vài chế độ để lựa chọn:

- `off`: Vô hiệu hóa cả việc tự động hóa chứng chỉ và chuyển hướng HTTP sang HTTPS.

- `disable_redirects`: Chỉ vô hiệu hóa chuyển hướng HTTP sang HTTPS.

- `disable_certs`: Chỉ vô hiệu hóa việc tự động hóa chứng chỉ.

- `ignore_loaded_certs`: Tự động hóa chứng chỉ ngay cả đối với các tên xuất hiện trên các chứng chỉ được tải thủ công. Hữu ích nếu bạn đã chỉ định một chứng chỉ bằng chỉ thị [`tls`](/docs/caddyfile/directives/tls) chứa các tên (hoặc ký tự đại diện) mà bạn muốn được quản lý tự động thay thế.

<aside class="tip">

Tùy chọn này không ảnh hưởng đến giao thức mặc định của Caddy, luôn là HTTPS, khi địa chỉ trang web có tên miền hợp lệ. Điều này có nghĩa là `auto_https off` sẽ không khiến trang web của bạn được phục vụ qua HTTP, nó sẽ chỉ vô hiệu hóa việc quản lý chứng chỉ tự động và chuyển hướng.

Điều này có nghĩa là nếu bạn muốn phục vụ trang web của mình qua HTTP, bạn nên thay đổi [địa chỉ trang web](/docs/caddyfile/concepts#addresses) của mình để được bắt đầu bằng `http://` hoặc kết thúc bằng `:80` (hoặc tùy chọn [`http_port`](#http_port)).

</aside>

```caddy
{
	auto_https disable_redirects
}
```


<a id="email"></a>
##### `email`
Địa chỉ email của bạn. Chủ yếu được sử dụng khi tạo tài khoản ACME với CA của bạn và rất được khuyến khích trong trường hợp có vấn đề với chứng chỉ của bạn.

<aside class="tip">

Hãy lưu ý rằng Let's Encrypt có thể gửi cho bạn các email về việc chứng chỉ của bạn sắp hết hạn, nhưng điều này có thể gây hiểu lầm vì Caddy có thể đã chọn sử dụng một nhà phát hành khác (ví dụ: ZeroSSL) khi gia hạn. Hãy kiểm tra nhật ký của bạn và/hoặc chính chứng chỉ đó (trong trình duyệt của bạn chẳng hạn) để xem nhà phát hành nào đã được sử dụng và ngày hết hạn của nó vẫn còn hiệu lực; nếu vậy, bạn có thể an tâm bỏ qua email từ Let's Encrypt.

</aside>

```caddy
{
	email admin@example.com
}
```


<a id="defaultsni"></a>
##### `default_sni`
Thiết lập một TLS ServerName mặc định cho trường hợp khách truy cập không sử dụng SNI trong ClientHello của họ.

```caddy
{
	default_sni example.com
}
```


<a id="fallbacksni"></a>
##### `fallback_sni`
⚠️ <i>Thử nghiệm</i>

Nếu được cấu hình, giá trị dự phòng (fallback) sẽ trở thành TLS ServerName trong ClientHello nếu ServerName ban đầu không khớp với bất kỳ chứng chỉ nào trong bộ nhớ đệm (cache).

Các trường hợp sử dụng cho việc này rất hạn chế; thường là nếu khách truy cập là một CDN và truyền qua ServerName của cái bắt tay hạ nguồn (downstream handshake) nhưng có thể chấp nhận một chứng chỉ với tên máy chủ của nguồn (origin) thay thế, thì bạn sẽ đặt đây là tên máy chủ của nguồn của mình. Lưu ý rằng Caddy phải đang quản lý một chứng chỉ cho tên này.

```caddy
{
	fallback_sni example.com
}
```


<a id="localcerts"></a>
##### `local_certs`
Khiến **tất cả** các chứng chỉ được phát hành nội bộ theo mặc định, thay vì thông qua một ACME CA (công khai) như Let's Encrypt. Điều này hữu ích như một công tắc nhanh trong môi trường phát triển.

```caddy
{
	local_certs
}
```


<a id="skipinstalltrust"></a>
##### `skip_install_trust`
Bỏ qua các nỗ lực cài đặt chứng chỉ gốc của CA nội bộ vào kho lưu trữ tin cậy của hệ thống, cũng như vào kho lưu trữ tin cậy của Java và Mozilla Firefox.

```caddy
{
	skip_install_trust
}
```


<a id="acmeca"></a>
##### `acme_ca`
Chỉ định URL đến thư mục của ACME CA. Rất khuyến khích đặt giá trị này thành [điểm cuối thử nghiệm (staging endpoint) của Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) để kiểm tra hoặc phát triển. Mặc định: các điểm cuối sản xuất của ZeroSSL và Let's Encrypt.

Lưu ý rằng một ACME CA được cấu hình toàn cục có thể không áp dụng cho tất cả các trang web; xem [các yêu cầu về tên máy chủ](/docs/automatic-https#hostname-requirements) để sử dụng (các) nhà phát hành ACME mặc định.

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

<a id="acmecaroot"></a>
##### `acme_ca_root`
Chỉ định một tệp PEM chứa chứng chỉ gốc (root) tin cậy cho các điểm cuối ACME CA, nếu không có trong kho lưu trữ tin cậy của hệ thống.

```caddy
{
	acme_ca_root /path/to/ca/root.pem
}
```


<a id="acmeeab"></a>
##### `acme_eab`
Chỉ định một Ràng buộc Tài khoản Bên ngoài (External Account Binding - EAB) để sử dụng cho tất cả các giao dịch ACME.

Ví dụ, với thông tin xác thực ZeroSSL giả định:

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


<a id="acmedns"></a>
##### `acme_dns`
Cấu hình nhà cung cấp [ACME DNS challenge](/docs/automatic-https#dns-challenge) để sử dụng cho tất cả các giao dịch ACME.

Yêu cầu một bản dựng tùy chỉnh của Caddy với plugin cho nhà cung cấp DNS của bạn.

Các mã thông báo (tokens) theo sau tên của nhà cung cấp sẽ thiết lập nhà cung cấp giống như khi được chỉ định trong [nhà phát hành `acme` của chỉ thị `tls`](/docs/caddyfile/directives/tls#acme).

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


<a id="dns"></a>
##### `dns`
Cấu hình một nhà cung cấp DNS mặc định để sử dụng khi không có nhà cung cấp nào khác được chỉ định cục bộ trong một ngữ cảnh liên quan. Ví dụ: nếu ACME DNS challenge được kích hoạt nhưng không có nhà cung cấp DNS nào được cấu hình, thì giá trị mặc định toàn cục này sẽ được sử dụng. Nó cũng được áp dụng để xuất bản cấu hình Encrypted ClientHello (ECH).

Tệp thực thi Caddy của bạn phải được biên dịch với mô-đun nhà cung cấp DNS được chỉ định để tính năng này hoạt động.

Ví dụ, sử dụng thông tin xác thực từ một biến môi trường:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

(Yêu cầu Caddy 2.10 beta 1 hoặc mới hơn.)


<a id="ech"></a>
##### `ech`
Kích hoạt Encrypted ClientHello (ECH) bằng cách sử dụng (các) tên miền công cộng được chỉ định làm tên máy chủ dạng văn bản thuần túy (SNI) trong các lần bắt tay TLS. Trong các điều kiện thích hợp, ECH có thể giúp bảo vệ tên miền của các trang web của bạn trên đường truyền trong quá trình kết nối. Caddy sẽ tạo và xuất bản một cấu hình ECH cho mỗi tên công cộng được chỉ định. Xuất bản là cách các khách truy cập tương thích (chẳng hạn như các trình duyệt hiện đại được cấu hình đúng cách) biết để sử dụng ECH nhằm truy cập các trang web của bạn.

Để hoạt động bình thường, (các) cấu hình ECH phải được xuất bản theo cách mà khách truy cập mong đợi. Hầu hết các trình duyệt (đã bật DNS-over-HTTPS hoặc DNS-over-TLS) mong đợi các cấu hình ECH được xuất bản lên các bản ghi DNS loại HTTPS. Caddy thực hiện kiểu xuất bản này một cách tự động, nhưng bạn phải chỉ định một nhà cung cấp DNS bằng tùy chọn phụ `dns`, hoặc toàn cục với [tùy chọn toàn cục `dns`](#dns), và tệp thực thi Caddy của bạn phải được xây dựng với mô-đun nhà cung cấp DNS được chỉ định. (Các bản dựng tùy chỉnh có sẵn trên [trang tải xuống](/download) của chúng tôi.)

**Thông báo về quyền riêng tư:**

- Thông thường, bạn nên **tối đa hóa quy mô của [_tập hợp ẩn danh_ (anonymity set)](https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction) của mình**. Do đó, chúng tôi thường khuyên hầu hết người dùng _chỉ cấu hình một_ tên miền công cộng để bảo vệ tất cả các trang web của bạn.
- **Máy chủ của bạn nên có thẩm quyền đối với (các) tên miền công cộng mà bạn chỉ định** (tức là chúng nên trỏ đến máy chủ của bạn) vì Caddy sẽ lấy chứng chỉ cho chúng. Các chứng chỉ này cực kỳ quan trọng để giúp các khách truy cập tuân thủ đặc tả kết nối một cách đáng tin cậy và an toàn với ECH trong một số trường hợp. Chúng chỉ được sử dụng để tạo điều kiện thuận lợi cho việc bắt tay ECH đúng cách, không được sử dụng cho dữ liệu ứng dụng (các trang web của bạn -- trừ khi bạn xác định một trang web trùng với tên miền công cộng của mình).
- Mọi trường hợp có thể khác nhau. Chúng tôi khuyên bạn nên tham khảo ý kiến chuyên gia để **xem xét mô hình đe dọa (threat model) của mình** nếu rủi ro cao, vì ECH không phải là một giải pháp phù hợp cho tất cả.

Ví dụ sử dụng thông tin xác thực từ một biến môi trường để xuất bản lên các máy chủ tên được đặt tại Cloudflare:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

Điều này sẽ khiến các khách truy cập tương thích tải tất cả các trang web của bạn với `ech.example.net`, thay vì các tên trang web riêng lẻ bị lộ dưới dạng văn bản thuần túy.

Việc xuất bản thành công yêu cầu các tên miền của trang web của bạn phải được đặt tại nhà cung cấp DNS được cấu hình và các bản ghi có thể được sửa đổi bằng thông tin xác thực / cấu hình nhà cung cấp đã cho.

(Yêu cầu Caddy 2.10 beta 1 hoặc mới hơn.)


<a id="ondemandtls"></a>
##### `on_demand_tls`
Cấu hình [TLS theo yêu cầu (On-Demand TLS)](/docs/automatic-https#on-demand-tls) nơi nó được kích hoạt, nhưng bản thân nó không kích hoạt tính năng này (để kích hoạt, hãy sử dụng [chỉ thị phụ `on_demand` của chỉ thị `tls`](/docs/caddyfile/directives/tls#syntax)). Yêu cầu sử dụng trong môi trường sản xuất để ngăn chặn việc lạm dụng.

- **ask** sẽ khiến Caddy thực hiện một yêu cầu HTTP đến URL đã cho, hỏi xem một tên miền có được phép cấp chứng chỉ hay không.

  Yêu cầu có một chuỗi truy vấn (query string) là `?domain=` chứa giá trị của tên miền.

  Nếu điểm cuối trả về mã trạng thái `2xx`, Caddy sẽ được ủy quyền để lấy chứng chỉ cho tên đó. Bất kỳ mã trạng thái nào khác sẽ dẫn đến việc hủy bỏ việc cấp chứng chỉ và báo lỗi bắt tay TLS.

<aside class="tip">

Điểm cuối ask nên trả về _càng nhanh càng tốt_, lý tưởng là trong vài mili giây. Thông thường, điểm cuối của bạn nên thực hiện tra cứu theo thời gian không đổi (constant-time lookup) trong một cơ sở dữ liệu có chỉ mục theo tên miền; tránh các vòng lặp. Tránh thực hiện các truy vấn DNS hoặc các yêu cầu mạng khác.

</aside>

- **permission** cho phép sử dụng các mô-đun tùy chỉnh để xác định xem một chứng chỉ có nên được cấp cho một tên cụ thể hay không. Mô-đun phải triển khai [giao diện `caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission). Một mô-đun quyền `http` đã được bao gồm, chính là cái mà tùy chọn `ask` sử dụng, và vẫn tồn tại như một phím tắt để tương thích ngược.

- ⚠️ Các tùy chọn giới hạn tốc độ **interval** và **burst** từng khả dụng, nhưng KHÔNG được khuyến khích. Hãy xóa chúng khỏi cấu hình của bạn nếu bạn vẫn còn giữ chúng.

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


<a id="keytype"></a>
##### `key_type`
Chỉ định loại khóa sẽ tạo cho chứng chỉ TLS; chỉ thay đổi điều này nếu bạn có nhu cầu cụ thể để tùy chỉnh nó.

Các giá trị khả thi là: `ed25519`, `p256`, `p384`, `rsa2048`, `rsa4096`.

```caddy
{
	key_type ed25519
}
```


<a id="certissuer"></a>
##### `cert_issuer`
Xác định nhà phát hành (hoặc nguồn) của chứng chỉ TLS.

Điều này cho phép cấu hình các nhà phát hành trên toàn cục, thay vì cho từng trang web như cách bạn làm với [chỉ thị phụ `issuer` của chỉ thị `tls`](/docs/caddyfile/directives/tls#issuer).

Có thể được lặp lại nếu bạn muốn cấu hình nhiều hơn một nhà phát hành để thử nghiệm. Chúng sẽ được thử theo thứ tự mà chúng được xác định.

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


<a id="renewinterval"></a>
##### `renew_interval`
Tần suất quét tất cả các chứng chỉ đã tải và được quản lý để tìm các chứng chỉ hết hạn và kích hoạt việc gia hạn nếu đã hết hạn.

Mặc định: `10m`

```caddy
{
	renew_interval 30m
}
```


<a id="certlifetime"></a>
##### `cert_lifetime`
Thời hạn hiệu lực yêu cầu CA cấp chứng chỉ.

Giá trị này được sử dụng để tính toán trường `notAfter` của đơn hàng ACME; do đó hệ thống phải có đồng hồ được đồng bộ hóa hợp lý. LƯU Ý: Không phải tất cả các CA đều hỗ trợ điều này. Hãy kiểm tra tài liệu ACME của CA của bạn để xem điều này có được phép không và những giá trị nào có thể được sử dụng.

Mặc định: `0` (CA tự chọn thời hạn, thường là 90 ngày)

⚠️ Đây là một tính năng thử nghiệm. Có thể bị thay đổi hoặc loại bỏ.

```caddy
{
	cert_lifetime 30d
}
```


<a id="ocspinterval"></a>
##### `ocsp_interval`
Tần suất kiểm tra xem [OCSP staples <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OCSP_stapling) có cần cập nhật hay không.

Mặc định: `1h`

```caddy
{
	ocsp_interval 2h
}
```


<a id="ocspstapling"></a>
##### `ocsp_stapling`
Có thể được đặt thành `off` để vô hiệu hóa OCSP stapling. Hữu ích trong các môi trường mà các bộ phản hồi (responders) không thể truy cập được do tường lửa.

```caddy
{
	ocsp_stapling off
}
```

<a id="renewalwindowratio"></a>
##### `renewal_window_ratio`
Tỷ lệ (từ 0 đến 1) của thời hạn hiệu lực chứng chỉ phải còn lại trước khi Caddy cố gắng gia hạn chứng chỉ. Ví dụ: nếu một chứng chỉ có thời hạn 90 ngày và tỷ lệ này là `0.3333` (giá trị mặc định), thì Caddy sẽ liên tục cố gắng gia hạn chứng chỉ khi nó còn lại 30 ngày hoặc ít hơn trước khi hết hạn. Cũng có thể được thiết lập cho từng trang web bằng [chỉ thị phụ `renewal_window_ratio` của chỉ thị `tls`](/docs/caddyfile/directives/tls#renewal_window_ratio).

Bạn hiếm khi cần thay đổi điều này, nhưng nó có thể hữu ích để gia hạn muộn hơn trong vòng đời của chứng chỉ nếu CA của bạn có thời gian cấp rất dài.

Hãy lưu ý rằng đây chỉ là một gợi ý, vì các nhà phát hành ACME có thể triển khai [tiện ích mở rộng ARI](https://datatracker.ietf.org/doc/rfc9773/) trong đó nhà phát hành ra lệnh về một khung thời gian mà khách truy cập ACME (Caddy trong trường hợp này) nên thử gia hạn, và khung thời gian đó có thể không phù hợp với tỷ lệ này.

```caddy
{
	renewal_window_ratio 0.1
}
```


<a id="preferredchains"></a>
##### `preferred_chains`
Nếu CA của bạn cung cấp nhiều chuỗi chứng chỉ, bạn có thể sử dụng tùy chọn này để chỉ định chuỗi nào Caddy nên ưu tiên. Thiết lập một trong các tùy chọn sau:

- **smallest** sẽ yêu cầu Caddy ưu tiên các chuỗi có ít byte nhất.

- **root_common_name** là danh sách một hoặc nhiều tên chung (common names); Caddy sẽ chọn chuỗi đầu tiên có chứng chỉ gốc khớp với ít nhất một trong các tên chung được chỉ định.

- **any_common_name** là danh sách một hoặc nhiều tên chung; Caddy sẽ chọn chuỗi đầu tiên có nhà phát hành khớp với ít nhất một trong các tên chung được chỉ định.

Lưu ý rằng việc chỉ định `preferred_chains` dưới dạng tùy chọn toàn cục sẽ ảnh hưởng đến tất cả các nhà phát hành nếu không có bất kỳ [cấu hình cấp độ nhà phát hành nào ghi đè lên](/docs/caddyfile/directives/tls#acme).

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```


<a id="server-options"></a>
## Các tùy chọn máy chủ

Tùy chỉnh các [máy chủ HTTP](/docs/json/apps/http/servers/) với các cài đặt có khả năng trải rộng trên nhiều trang web, và do đó không thể được cấu hình đúng cách trong các khối trang web. Các tùy chọn này ảnh hưởng đến bộ lắng nghe (listener)/socket hoặc các phương tiện khác bên dưới lớp HTTP.

Có thể được chỉ định nhiều lần với các giá trị `listener_address` khác nhau để cấu hình các tùy chọn khác nhau cho mỗi máy chủ. Ví dụ: `servers :443` sẽ chỉ áp dụng cho máy chủ được ràng buộc với địa chỉ lắng nghe `:443`. Việc bỏ qua địa chỉ lắng nghe sẽ áp dụng các tùy chọn cho bất kỳ máy chủ còn lại nào.

<aside class="tip">

Sử dụng lệnh [`caddy adapt`](/docs/command-line#caddy-adapt) để tìm địa chỉ lắng nghe của các máy chủ trong Caddyfile của bạn.

</aside>


Ví dụ, để cấu hình các tùy chọn khác nhau cho các máy chủ trên các cổng `:80` và `:443`, bạn sẽ chỉ định hai khối `servers`:

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

Khi sử dụng `servers`, nó sẽ **chỉ** áp dụng cho các máy chủ **thực sự xuất hiện** trong Caddyfile của bạn (tức là được tạo ra bởi một khối trang web). Hãy nhớ rằng, [HTTPS tự động](/docs/automatic-https) sẽ tạo một máy chủ lắng nghe trên cổng `80` (hoặc tùy chọn [`http_port`](#http_port)), để phục vụ các chuyển hướng HTTP->HTTPS và để giải quyết ACME HTTP challenge; điều này xảy ra lúc thực thi (runtime), tức là _sau khi_ bộ chuyển đổi Caddyfile áp dụng `servers`. Vì vậy, nói cách khác, điều này có nghĩa là `servers` **sẽ không** áp dụng cho `:80` trừ khi bạn khai báo rõ ràng một khối trang web như `http://` hoặc `:80`.


<aside class="tip">

Nếu bạn đang sử dụng chỉ thị [`bind`](/docs/caddyfile/directives/bind) hoặc [tùy chọn toàn cục `default_bind`](/docs/caddyfile/options#default_bind), `listener_address` *PHẢI* khớp với địa chỉ ràng buộc kết hợp với cổng của khối trang web, nếu không các cài đặt sẽ không được áp dụng. Ví dụ:

```caddy
{
	# Điều này sẽ KHÔNG khớp với máy chủ, thiếu địa chỉ ràng buộc
	servers :8080 {
		name private
	}

	# Điều này sẽ hoạt động vì nó là một sự khớp chính xác
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



<a id="name"></a>
##### `name`

Một tên tùy chỉnh để gán cho máy chủ này. Thường hữu ích để nhận dạng một máy chủ qua tên của nó trong nhật ký và các chỉ số (metrics). Nếu không được thiết lập, Caddy sẽ tự động xác định tên đó bằng mẫu `srvX`, trong đó `X` bắt đầu bằng `0` và tăng dần dựa trên số lượng máy chủ trong cấu hình.

Hãy lưu ý rằng chỉ các máy chủ được tạo bởi các khối trang web trong cấu hình của bạn mới được áp dụng các cài đặt. [HTTPS tự động](/docs/automatic-https) tạo một máy chủ `:80` (hoặc [`http_port`](#http_port)) lúc thực thi, vì vậy nếu bạn muốn đổi tên nó, bạn sẽ cần ít nhất một khối trang web `http://` trống.

Ví dụ:

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```

</aside>



<a id="listenerwrappers"></a>
##### `listener_wrappers`

Cho phép cấu hình các [vỏ bọc bộ lắng nghe (listener wrappers)](/docs/json/apps/http/servers/listener_wrappers/), có thể sửa đổi hành vi của bộ lắng nghe socket. Chúng được áp dụng theo thứ tự đã cho.

<a id="tls"></a>
###### `tls`

Vỏ bọc bộ lắng nghe `tls` là một vỏ bọc bộ lắng nghe không thực hiện hành động nào (no-op), đánh dấu nơi bộ lắng nghe TLS nên nằm trong một chuỗi các vỏ bọc bộ lắng nghe. Nó chỉ nên được sử dụng nếu một vỏ bọc bộ lắng nghe khác phải được đặt trước cái bắt tay TLS.

<a id="httpredirect"></a>
###### `http_redirect`

[`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/) cung cấp các chuyển hướng HTTP->HTTPS cho các kết nối đến cổng TLS dưới dạng yêu cầu HTTP, bằng cách phát hiện thông qua vài byte đầu tiên rằng đó không phải là một cái bắt tay TLS, mà thay vào đó là một yêu cầu HTTP. Điều này hữu ích nhất khi phục vụ HTTPS trên một cổng không tiêu chuẩn (khác với `443`), vì các trình duyệt sẽ thử HTTP trừ khi giao thức được chỉ định. Nó phải được đặt _trước_ vỏ bọc bộ lắng nghe `tls`. Đây là một ví dụ:

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

<a id="proxyprotocol"></a>
###### `proxy_protocol`

Vỏ bọc bộ lắng nghe [`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/) (trước phiên bản v2.7.0 nó chỉ có sẵn qua plugin) cho phép phân tích cú pháp [giao thức PROXY](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (được phổ biến bởi HAProxy). Điều này phải được sử dụng _trước_ vỏ bọc bộ lắng nghe `tls` vì nó phân tích cú pháp dữ liệu văn bản thuần túy khi bắt đầu kết nối:

Hãy lưu ý rằng siêu dữ liệu từ giao thức PROXY có thể được áp dụng cho kết nối trước khi đánh giá các bộ khớp hoặc [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies). Địa chỉ IP của nút mạng (peer) trực tiếp sẽ bị mất cho quá trình đánh giá tiếp theo.

```caddy-d
proxy_protocol {
	timeout <duration>
	allow <cidrs...>
	deny <cidrs...>
	fallback_policy <policy>
}
```

- **timeout** chỉ định khoảng thời gian tối đa để chờ tiêu đề PROXY. Mặc định là `5s`.

- **allow** là danh sách các dải CIDR của các nguồn tin cậy để nhận tiêu đề PROXY. Socket unix được tin cậy theo mặc định và không phải là một phần của tùy chọn này.

- **deny** là danh sách các dải CIDR của các nguồn tin cậy để từ chối tiêu đề PROXY.

- **fallback_policy** là hành động cần thực hiện nếu tiêu đề PROXY đến từ một địa chỉ không nằm trong một trong hai danh sách cho phép/từ chối. Chính sách dự phòng mặc định là `ignore`. Các giá trị được chấp nhận của `fallback_policy` là:
	- `ignore`: lấy địa chỉ từ tiêu đề PROXY, nhưng vẫn chấp nhận kết nối
	- `use`: sử dụng địa chỉ từ tiêu đề PROXY
	- `reject`: từ chối kết nối khi tiêu đề PROXY được gửi
	- `require`: bắt buộc kết nối phải gửi tiêu đề PROXY, từ chối nếu không có
	- `skip`: chấp nhận một kết nối mà không yêu cầu tiêu đề PROXY.


Ví dụ, đối với một máy chủ HTTPS (cần vỏ bọc bộ lắng nghe `tls`) chấp nhận các tiêu đề PROXY từ một dải địa chỉ IP cụ thể và từ chối các tiêu đề PROXY từ một dải khác, với thời gian chờ là 2 giây:

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


<a id="timeouts"></a>
##### `timeouts`

- **read_body** là một [giá trị khoảng thời gian](/docs/conventions#durations) thiết lập thời gian tối đa được phép đọc từ dữ liệu tải lên của khách truy cập. Việc đặt giá trị này thành một giá trị ngắn, khác không có thể giảm thiểu các cuộc tấn công slowloris, nhưng cũng có thể ảnh hưởng đến các khách truy cập thực sự chậm. Mặc định là không có thời gian chờ.

- **read_header** là một [giá trị khoảng thời gian](/docs/conventions#durations) thiết lập thời gian tối đa được phép đọc từ các tiêu đề yêu cầu của khách truy cập. Mặc định là không có thời gian chờ.

- **write** là một [giá trị khoảng thời gian](/docs/conventions#durations) thiết lập thời gian tối đa được phép ghi cho khách truy cập. Lưu ý rằng việc đặt giá trị này thành một giá trị nhỏ khi phục vụ các tệp lớn có thể ảnh hưởng tiêu cực đến các khách truy cập thực sự chậm. Mặc định là không có thời gian chờ.

- **idle** là một [giá trị khoảng thời gian](/docs/conventions#durations) thiết lập thời gian tối đa để chờ yêu cầu tiếp theo khi các tính năng duy trì kết nối (keep-alives) được bật. Mặc định là 5 phút để giúp tránh cạn kiệt tài nguyên.

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


<a id="keepaliveinterval"></a>
##### `keepalive_interval`

Khoảng thời gian mà các gói TCP keepalive được gửi để duy trì kết nối ở lớp TCP khi không có dữ liệu nào khác được truyền đi. Mặc định là `15s`.

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


<a id="keepaliveidle"></a>
##### `keepalive_idle`

Thời gian một kết nối phải nhàn rỗi trước khi các gói TCP keepalive được gửi khi không có dữ liệu nào khác được truyền đi. Mặc định là `15s`.

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


<a id="keepalivecount"></a>
##### `keepalive_count`

Số lượng gói TCP keepalive tối đa được gửi trước khi coi kết nối đã chết. Mặc định là `9`.

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


<a id="0rtt"></a>
##### `0rtt`

Theo mặc định, 0-RTT (dữ liệu sớm) được kích hoạt cho các bộ lắng nghe QUIC (tức là HTTP/3) để cho phép khách truy cập gửi dữ liệu trong vòng khứ hồi đầu tiên của cái bắt tay TLS, điều này có thể cải thiện hiệu suất cho các kết nối lặp lại.

Bạn có thể đặt giá trị này thành `off` để vô hiệu hóa 0-RTT cho các bộ lắng nghe QUIC. Một lý do để vô hiệu hóa 0-RTT là nếu một [bộ khớp `remote_ip`](/docs/caddyfile/matchers#remote-ip) được sử dụng, điều này tạo ra một sự phụ thuộc vào việc địa chỉ từ xa được xác thực nếu việc định tuyến diễn ra trước khi cái bắt tay TLS hoàn tất. Một phản hồi HTTP 425 sẽ được ghi trong trường hợp đó, nhưng một số khách truy cập (trình duyệt) có thể hoạt động không đúng và không thực hiện thử lại, vì vậy việc vô hiệu hóa 0-RTT có thể đảm bảo rằng người dùng không thấy phản hồi 425, với cái giá là mất đi lợi ích hiệu suất của 0-RTT.

```caddy
{
	servers {
		0rtt off
	}
}
```


<a id="trustedproxies"></a>
##### `trusted_proxies`

Cho phép cấu hình các dải IP (CIDR) của các máy chủ proxy mà từ đó các yêu cầu nên được tin cậy. Theo mặc định, không có proxy nào được tin cậy.

Việc kích hoạt tính năng này khiến các yêu cầu tin cậy có địa chỉ IP của khách truy cập _thực_ được phân tích cú pháp từ các tiêu đề HTTP (theo mặc định là `X-Forwarded-For`; xem [`client_ip_headers`](#client-ip-headers) để cấu hình các tiêu đề khác). Nếu được tin cậy, IP của khách truy cập sẽ được thêm vào [nhật ký truy cập](/docs/caddyfile/directives/log), có sẵn dưới dạng trình giữ chỗ `{client_ip}` [placeholder](/docs/caddyfile/concepts#placeholders), và cho phép sử dụng [bộ khớp `client_ip`](/docs/caddyfile/matchers#client-ip). Nếu yêu cầu không đến từ một proxy tin cậy, thì IP của khách truy cập được đặt thành địa chỉ IP từ xa của kết nối trực tiếp đến hoặc địa chỉ được đặt bởi [giao thức PROXY](/docs/caddyfile/options#proxy-protocol) nếu được sử dụng. Theo mặc định, các IP trong tiêu đề được phân tích cú pháp từ trái sang phải. Xem [`trusted_proxies_strict`](#trusted-proxies-strict) để thay đổi hành vi này.

Một số bộ khớp hoặc trình xử lý có thể sử dụng trạng thái tin cậy của yêu cầu để đưa ra quyết định. Ví dụ, nếu được tin cậy, trình xử lý [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#defaults) sẽ proxy và tăng cường các tiêu đề yêu cầu `X-Forwarded-*` nhạy cảm.

Hiện tại, chỉ có [mô-đun nguồn IP](/docs/json/apps/http/servers/trusted_proxies/) `static` được bao gồm trong bản phân phối tiêu chuẩn của Caddy, nhưng điều này có thể được [mở rộng](/docs/extending-caddy) bằng các plugin để duy trì một danh sách động các dải IP.


<a id="static"></a>
###### `static`

Nhận một danh sách tĩnh (không thay đổi) các dải IP (CIDR) để tin cậy.

Như một phím tắt, `private_ranges` có thể được sử dụng để khớp với tất cả các dải IPv4 và IPv6 riêng tư. Nó giống như việc chỉ định tất cả các dải sau: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`.

Cú pháp như sau:

```caddy-d
trusted_proxies static [private_ranges] <ranges...>
```

Dưới đây là một ví dụ đầy đủ, tin cậy một dải IPv4 ví dụ và một dải IPv6:

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

<a id="trustedproxiesstrict"></a>
##### `trusted_proxies_strict`

Khi [`trusted_proxies`](#trusted-proxies) được bật, các IP trong các tiêu đề (được cấu hình bởi [`client_ip_headers`](#client-ip-headers)) được phân tích cú pháp từ trái sang phải theo mặc định. Địa chỉ IP không tin cậy đầu tiên được tìm thấy sẽ trở thành địa chỉ khách truy cập thực. Kể từ v2.8, bạn có thể chọn phân tích cú pháp từ phải sang trái của các tiêu đề này với `trusted_proxies_strict`. Theo mặc định, tùy chọn này bị vô hiệu hóa để tương thích ngược.

Các proxy ngược dòng như HAProxy, CloudFlare, AWS ALB, CloudFront, v.v. sẽ nối thêm mỗi địa chỉ từ xa kết nối mới vào bên phải của `X-Forwarded-For`. Bạn nên bật `trusted_proxies_strict` khi làm việc với các hệ thống này, vì địa chỉ IP ngoài cùng bên trái có thể bị khách truy cập giả mạo.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">

Đặc biệt trong trường hợp của AWS ALB, bạn chắc chắn sẽ muốn bật tùy chọn này. [Theo tài liệu của họ](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15), bạn chỉ có thể xác định IP của khách truy cập thực bằng cách đặt chế độ XFF thành `append`. IP này sẽ được nối vào bên phải của `X-Forwarded-For` và chỉ có thể được trích xuất an toàn thông qua `trusted_proxies_strict`.

</aside>

<a id="trustedproxiesunix"></a>
##### `trusted_proxies_unix`

Tùy chọn `trusted_proxies_unix` cho phép tin cậy tất cả các kết nối đến từ socket Unix, điều này hữu ích khi Caddy đứng sau một proxy ngược (có thể là một phiên bản Caddy khác) kết nối với nó thông qua một socket Unix (tức là chỉ thị [`bind`](/docs/caddyfile/directives/bind) được đặt thành một socket unix). Tùy chọn này bị vô hiệu hóa theo mặc định.

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

<a id="clientipheaders"></a>
##### `client_ip_headers`

Kết hợp với [`trusted_proxies`](#trusted-proxies), cho phép cấu hình tiêu đề nào sẽ được sử dụng để xác định địa chỉ IP của khách truy cập. Theo mặc định, chỉ có `X-Forwarded-For` được xem xét. Nhiều trường tiêu đề có thể được chỉ định, trong đó giá trị tiêu đề không trống đầu tiên sẽ được sử dụng.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


<a id="metrics"></a>
##### `metrics`

Kích hoạt việc thu thập các chỉ số (metrics); cần thiết trước khi lấy các chỉ số hoặc đẩy chúng bằng OTLP. Lưu ý rằng các chỉ số làm giảm hiệu suất trên các máy chủ thực sự bận rộn. (Cộng đồng của chúng tôi đang nỗ lực cải thiện điều này. Hãy tham gia cùng chúng tôi!)

```caddy
{
	metrics
}
```

Bạn có thể thêm tùy chọn `per_host` để gắn nhãn các chỉ số với tên máy chủ của chỉ số đó.

```caddy
{
	metrics {
		per_host
	}
}
```

Do tiềm năng về số lượng quan hệ (cardinality) vô hạn trong việc quan sát tất cả các máy chủ có thể được gửi bởi khách truy cập, Caddy sẽ chỉ ghi lại các chỉ số cho các máy chủ đã cấu hình, trong khi tất cả các máy chủ khác (ví dụ: attacker.com) được tổng hợp dưới nhãn "_other". Để buộc quan sát tất cả các máy chủ, và nơi mà tiềm năng về cardinality vô hạn là một rủi ro có thể chấp nhận được, bạn thêm `observe_catchall_hosts`. Lưu ý rằng việc thêm `observe_catchall_hosts` sẽ không bật `per_host`. Tuy nhiên, tính năng này tự động được bật cho các máy chủ HTTPS (vì các chứng chỉ cung cấp một số bảo vệ chống lại cardinality không giới hạn), nhưng bị vô hiệu hóa cho các máy chủ HTTP theo mặc định để ngăn chặn các cuộc tấn công cardinality từ các tiêu đề Host tùy ý.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

Bạn có thể thêm tùy chọn `otlp` để đẩy cùng một bộ các chỉ số đến một điểm cuối Giao thức OpenTelemetry (OTLP). Bộ xuất (exporter) được cấu hình bởi các biến môi trường `OTEL_*` tiêu chuẩn của OpenTelemetry, chẳng hạn như `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL` và `OTEL_METRICS_EXPORTER`.

```caddy
{
	metrics {
		otlp
	}
}
```

Ví dụ:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Xem [Giám sát Caddy với các chỉ số](/docs/metrics) để biết thêm chi tiết.

<a id="trace"></a>
##### `trace`

Ghi nhật ký từng trình xử lý riêng lẻ được gọi. Yêu cầu nhật ký phải được phát ra ở mức `DEBUG` (Bạn có thể thực hiện việc này với [tùy chọn toàn cục `debug`](#debug)).

LƯU Ý: Điều này có thể ghi nhật ký cấu hình của các mô-đun trình xử lý HTTP của bạn; không bật tính năng này trong các ngữ cảnh không an toàn khi có dữ liệu nhạy cảm trong cấu hình.

⚠️ Đây là một tính năng thử nghiệm. Có thể bị thay đổi hoặc loại bỏ.

```caddy
{
	servers {
		trace
	}
}
```


<a id="maxheadersize"></a>
##### `max_header_size`

Kích thước tối đa để phân tích cú pháp từ các tiêu đề yêu cầu HTTP của khách truy cập. Nếu vượt quá giới hạn, máy chủ sẽ phản hồi với trạng thái HTTP `431 Request Header Fields Too Large`. Nó chấp nhận tất cả các định dạng được hỗ trợ bởi [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Theo mặc định, giới hạn là `1MB`.

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


<a id="enablefullduplex"></a>
##### `enable_full_duplex`

Kích hoạt giao tiếp song công toàn phần (full-duplex) cho các yêu cầu HTTP/1.

Đối với các yêu cầu HTTP/1, máy chủ HTTP của Go theo mặc định sẽ tiêu thụ bất kỳ phần nào chưa đọc của thân yêu cầu (request body) trước khi bắt đầu ghi phản hồi, ngăn cản các trình xử lý đồng thời đọc từ yêu cầu và ghi phản hồi. Việc bật tùy chọn này sẽ vô hiệu hóa hành vi này và cho phép các trình xử lý tiếp tục đọc từ yêu cầu trong khi đồng thời ghi phản hồi.

Đối với các yêu cầu HTTP/2+, máy chủ HTTP của Go luôn cho phép đọc và phản hồi đồng thời, vì vậy tùy chọn này không có tác dụng.

Kiểm tra kỹ lưỡng với các khách truy cập HTTP của bạn, vì một số khách truy cập cũ hơn có thể không hỗ trợ HTTP/1 song công toàn phần, điều này có thể khiến chúng bị treo (deadlock). Xem [golang/go#57786](https://github.com/golang/go/issues/57786) để biết thêm thông tin.

⚠️ Đây là một tính năng thử nghiệm. Có thể bị thay đổi hoặc loại bỏ.

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


<a id="logcredentials"></a>
##### `log_credentials`

Theo mặc định, nhật ký truy cập (được bật với chỉ thị [`log`](/docs/caddyfile/directives/log)) với các tiêu đề chứa thông tin nhạy cảm tiềm ẩn (`Cookie`, `Set-Cookie`, `Authorization` và `Proxy-Authorization`) sẽ được ghi nhật ký là `REDACTED`.

Nếu bạn muốn các tiêu đề này _không_ bị ẩn đi, bạn có thể bật tùy chọn `log_credentials`.

```caddy
{
	servers {
		log_credentials
	}
}
```



<a id="protocols"></a>
##### `protocols`

Danh sách các giao thức HTTP được hỗ trợ, cách nhau bởi dấu cách.

Mặc định: `h1 h2 h3`

Các giá trị được chấp nhận là:
- `h1` cho HTTP/1.1
- `h2` cho HTTP/2
- `h2c` cho HTTP/2 qua văn bản thuần túy (cleartext)
- `h3` cho HTTP/3

Hiện tại, việc bật HTTP/2 (bao gồm cả H2C) nhất thiết phải bao gồm việc bật HTTP/1.1 vì thư viện tiêu chuẩn của Go không cho phép chúng tôi vô hiệu hóa HTTP/1.1 khi sử dụng máy chủ HTTP của nó. Tuy nhiên, HTTP/1.1 hoặc HTTP/3 đều có thể được bật độc lập.

Lưu ý rằng H2C ("Cleartext HTTP/2" hoặc "H2 qua TCP") và HTTP/3 không được triển khai bởi thư viện tiêu chuẩn của Go, vì vậy một số chức năng hoặc tính năng có thể bị hạn chế. Chúng tôi khuyên không nên bật H2C trừ khi nó thực sự cần thiết cho ứng dụng của bạn.

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



<a id="strictsnihost"></a>
##### `strict_sni_host`

Việc bật tính năng này yêu cầu tiêu đề `Host` của một yêu cầu phải khớp với giá trị của `ServerName` được gửi bởi ClientHello TLS của khách truy cập, một biện pháp bảo vệ cần thiết khi sử dụng xác thực khách truy cập bằng TLS. Nếu có sự không khớp, phản hồi trạng thái HTTP `421 Misdirected Request` sẽ được ghi lại cho khách truy cập.

Tùy chọn này sẽ tự động được bật nếu [xác thực khách truy cập](/docs/caddyfile/directives/tls#client_auth) được cấu hình. Điều này không cho phép bỏ qua xác thực khách truy cập TLS (domain fronting), vốn có thể bị khai thác bằng cách gửi một giá trị SNI không được bảo vệ trong quá trình bắt tay TLS, sau đó đặt một tên miền được bảo vệ trong tiêu đề Host sau khi thiết lập kết nối. Hành vi này là một mặc định an toàn, nhưng bạn có thể tắt nó một cách rõ ràng bằng `insecure_off`; ví dụ trong trường hợp chạy một proxy mà domain fronting được mong muốn và quyền truy cập không bị hạn chế dựa trên tên máy chủ.

```caddy
{
	servers {
		strict_sni_host on
	}
}
```



<a id="file-systems"></a>
## Hệ thống tệp

Tùy chọn toàn cục `filesystem` cho phép khai báo một hoặc nhiều hệ thống tệp có thể được sử dụng cho I/O tệp.

Điều này có thể cho phép bạn kết nối với một hệ thống tệp từ xa đang chạy trên đám mây, hoặc một cơ sở dữ liệu với giao diện giống như tệp, hoặc thậm chí để đọc từ các tệp được nhúng trong tệp thực thi Caddy.

Các hệ thống tệp được khai báo với một tên để nhận dạng chúng. Điều này có nghĩa là bạn có thể kết nối với nhiều hệ thống tệp cùng loại, nếu cần.

Theo mặc định, Caddy không có bất kỳ mô-đun hệ thống tệp nào, vì vậy bạn sẽ cần xây dựng Caddy với một plugin cho hệ thống tệp mà bạn muốn sử dụng.

<a id="example"></a>
#### Ví dụ

Sử dụng một mô-đun hệ thống tệp giả định là `custom`, bạn có thể khai báo hai hệ thống tệp:

```caddy
{
	filesystem foo custom {
		...
	}

	filesystem bar custom {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```



<a id="pki-options"></a>
## Các tùy chọn PKI

Ứng dụng PKI (Cơ sở hạ tầng khóa công khai - Public Key Infrastructure) là nền tảng cho các tính năng [HTTPS cục bộ](/docs/automatic-https#local-https) và [ACME server](/docs/caddyfile/directives/acme_server) của Caddy. Ứng dụng này xác định các cơ quan cấp chứng chỉ (CA) có khả năng ký chứng chỉ.

ID của CA mặc định là `local`. Nếu ID bị bỏ qua khi cấu hình `ca`, thì `local` được giả định.

<a id="name"></a>
##### `name`
Tên dành cho người dùng của cơ quan cấp chứng chỉ.

Mặc định: `Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "My Local CA"
		}
	}
}
```

<a id="rootcn"></a>
##### `root_cn`
Tên được đặt trong trường CommonName của chứng chỉ gốc.

Mặc định: `{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "My Local CA - 2024 ECC Root"
		}
	}
}
```

<a id="intermediatecn"></a>
##### `intermediate_cn`
Tên được đặt trong trường CommonName của các chứng chỉ trung gian.

Mặc định: `{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "My Local CA - ECC Intermediate"
		}
	}
}
```

<a id="intermediatelifetime"></a>
##### `intermediate_lifetime`
[Khoảng thời gian](/docs/conventions#durations) mà các chứng chỉ trung gian có hiệu lực. Giá trị này **phải** nhỏ hơn thời hạn hiệu lực của chứng chỉ gốc (`3600d` hoặc 10 năm).

Mặc định: `7d`. Không khuyến khích thay đổi giá trị này, trừ khi thực sự cần thiết.

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

<a id="maintenanceinterval"></a>
##### `maintenance_interval`
[Khoảng thời gian](/docs/conventions#durations) về tần suất kiểm tra xem các chứng chỉ trung gian (và chứng chỉ gốc, khi có thể) có cần gia hạn hay không.

Mặc định: `10m`. Không khuyến khích thay đổi giá trị này, trừ khi thực sự cần thiết.

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

<a id="renewalwindowratio"></a>
##### `renewal_window_ratio`
Tỷ lệ (từ 0 đến 1) của thời hạn hiệu lực chứng chỉ phải còn lại trước khi Caddy cố gắng gia hạn chứng chỉ. Ví dụ: nếu một chứng chỉ có thời hạn hiệu lực 1 năm và tỷ lệ này là `0.2` (giá trị mặc định), thì Caddy sẽ liên tục cố gắng gia hạn chứng chỉ khi nó còn lại 73 ngày hoặc ít hơn trước khi hết hạn.

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


<a id="root"></a>
##### `root`
Một cặp khóa (chứng chỉ và khóa riêng) được sử dụng làm gốc (root) cho CA. Nếu không được chỉ định, một cặp khóa sẽ được tạo và quản lý tự động.

- **format** là định dạng cung cấp chứng chỉ và khóa riêng. Hiện tại, chỉ hỗ trợ `pem_file`, đây cũng là giá trị mặc định, vì vậy trường này là tùy chọn.
- **cert** là chứng chỉ. Đây nên là đường dẫn đến một tệp PEM khi sử dụng định dạng `pem_file`.
- **key** là khóa riêng. Đây nên là đường dẫn đến một tệp PEM khi sử dụng định dạng `pem_file`.

<a id="intermediate"></a>
##### `intermediate`
Một cặp khóa (chứng chỉ và khóa riêng) được sử dụng làm trung gian cho CA. Nếu không được chỉ định, một cặp khóa sẽ được tạo và quản lý tự động.

- **format** là định dạng cung cấp chứng chỉ và khóa riêng. Hiện tại, chỉ hỗ trợ `pem_file`, đây cũng là giá trị mặc định, vì vậy trường này là tùy chọn.
- **cert** là chứng chỉ. Đây nên là đường dẫn đến một tệp PEM khi sử dụng định dạng `pem_file`.
- **key** là khóa riêng. Đây nên là đường dẫn đến một tệp PEM khi sử dụng định dạng `pem_file`.

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /path/to/root.pem
				key /path/to/root.key
			}
			intermediate {
				format pem_file
				cert /path/to/intermediate.pem
				key /path/to/intermediate.key
			}
		}
	}
}
```


<a id="event-options"></a>
## Các tùy chọn sự kiện

Các mô-đun Caddy phát ra các sự kiện khi những điều thú vị xảy ra (hoặc sắp xảy ra).

Các sự kiện thường bao gồm một tải dữ liệu (payload) siêu dữ liệu. Cách tốt nhất để tìm hiểu về các sự kiện và tải dữ liệu của chúng là từ tài liệu của mỗi mô-đun, nhưng bạn cũng có thể xem các sự kiện và tải dữ liệu của chúng bằng cách bật [tùy chọn toàn cục `debug`](#debug) và đọc nhật ký.

<a id="on"></a>
##### `on`

Liên kết một trình xử lý sự kiện (event handler) với sự kiện đã đặt tên. Chỉ định tên của mô-đun trình xử lý sự kiện, theo sau là cấu hình của nó.

Ví dụ, để chạy một lệnh sau khi lấy được chứng chỉ (yêu cầu [plugin của bên thứ ba <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/mholt/caddy-events-exec)), với một phần của tải dữ liệu sự kiện được truyền cho tập lệnh bằng cách sử dụng một trình giữ chỗ:

```caddy
{
	events {
		on cert_obtained exec ./my-script.sh {event.data.certificate_path}
	}
}
```

<a id="events"></a>
### Các sự kiện

Các sự kiện tiêu chuẩn này được phát ra bởi Caddy:

- [Các sự kiện `tls` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/certmagic#events)
- [Các sự kiện `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#events)

Các plugin cũng có thể phát ra sự kiện, vì vậy hãy kiểm tra tài liệu của chúng để biết chi tiết.
