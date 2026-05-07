---
title: reverse_proxy (chỉ thị Caddyfile)
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
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Fix matcher placeholder
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@name')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">@name</a>';
			break;
		}
	}
	
	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}
	
	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# reverse_proxy

Proxy các yêu cầu đến một hoặc nhiều backend với các tùy chọn cấu hình về vận chuyển (transport), cân bằng tải (load balancing), kiểm tra sức khỏe (health checking), thao tác yêu cầu (request manipulation) và bộ đệm (buffering).

- [Cú pháp](#syntax)
- [Upstream](#upstreams)
  - [Địa chỉ upstream](#upstream-addresses)
  - [Upstream động](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
	- [Multi](#multi)
- [Cân bằng tải](#load-balancing)
  - [Kiểm tra sức khỏe chủ động](#active-health-checks)
  - [Kiểm tra sức khỏe thụ động](#passive-health-checks)
  - [Sự kiện](#events)
- [Streaming](#streaming)
- [Header](#headers)
- [Rewrite](#rewrites)
- [Vận chuyển (Transport)](#transports)
  - [Vận chuyển `http`](#the-http-transport)
  - [Vận chuyển `fastcgi`](#the-fastcgi-transport)
- [Chặn phản hồi](#intercepting-responses)
- [Ví dụ](#examples)



<a id="syntax"></a>
## Cú pháp

```caddy-d
reverse_proxy [<matcher>] [<upstreams...>] {
	# backends
	to      <upstreams...>
	dynamic <module> ...

	# cân bằng tải
	lb_policy       <name> [<options...>]
	lb_retries      <retries>
	lb_try_duration <duration>
	lb_try_interval <interval>
	lb_retry_match  <request-matcher>

	# kiểm tra sức khỏe chủ động (active health checking)
	health_uri          <uri>
	health_upstream     <ip:port>
	health_port         <port>
	health_interval     <interval>
	health_passes       <num>
	health_fails	    <num>
	health_timeout      <duration>
	health_method       <method>
	health_status       <status>
	health_request_body <body>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<field> [<values...>]
	}

	# kiểm tra sức khỏe thụ động (passive health checking)
	fail_duration     <duration>
	max_fails         <num>
	unhealthy_status  <status>
	unhealthy_latency <duration>
	unhealthy_request_count <num>

	# streaming
	flush_interval     <duration>
	request_buffers    <size>
	response_buffers   <size>
	stream_timeout     <duration>
	stream_close_delay <duration>

	# thao tác request/header
	trusted_proxies [private_ranges] <ranges...>
	header_up   [+|-]<field> [<value|regexp> [<replacement>]]
	header_down [+|-]<field> [<value|regexp> [<replacement>]]
	method <method>
	rewrite <to>

	# round trip
	transport <name> {
		...
	}

	# tùy chọn chặn phản hồi từ upstream
	@name {
		status <code...>
		header <field> [<value>]
	}
	replace_status [<matcher>] <status_code>
	handle_response [<matcher>] {
		<directives...>

		# các chỉ thị đặc biệt chỉ có sẵn trong handle_response
		copy_response [<matcher>] [<status>] {
			status <status>
		}
		copy_response_headers [<matcher>] {
			include <fields...>
			exclude <fields...>
		}
	}
}
```



<a id="upstreams"></a>
## Upstream

- **&lt;upstreams...&gt;** là danh sách các upstream (backend) để proxy tới.
- **to** <span id="to"/> là một cách thay thế để chỉ định danh sách các upstream, một (hoặc nhiều) trên mỗi dòng.
- **dynamic** <span id="dynamic"/> cấu hình một module _dynamic upstreams_. Điều này cho phép lấy danh sách các upstream một cách động cho mỗi yêu cầu. Xem phần [upstream động](#dynamic-upstreams) bên dưới để biết mô tả về các module upstream động tiêu chuẩn. Các upstream động được truy xuất tại mỗi vòng lặp proxy (nghĩa là có thể nhiều lần cho mỗi yêu cầu nếu thử lại cân bằng tải được bật) và sẽ được ưu tiên hơn các upstream tĩnh. Nếu xảy ra lỗi, proxy sẽ quay lại sử dụng bất kỳ upstream nào được cấu hình tĩnh.


<a id="upstream-addresses"></a>
### Địa chỉ upstream

Địa chỉ upstream tĩnh có thể ở dạng URL chỉ chứa scheme và host/port, hoặc một [địa chỉ mạng Caddy](/docs/conventions#network-addresses) thông thường. Các ví dụ hợp lệ:

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

Theo mặc định, các kết nối đến upstream được thực hiện qua HTTP văn bản thuần túy. Khi sử dụng dạng URL, một scheme có thể được sử dụng để thiết lập một số mặc định cho [`transport`](#transports) như một cách viết tắt.
- Sử dụng `https://` làm scheme sẽ sử dụng [`http` transport](#the-http-transport) với [`tls`](#tls) được bật.

  Ngoài ra, bạn có thể cần ghi đè header `Host` để nó khớp với giá trị TLS SNI, giá trị này được máy chủ sử dụng để định tuyến và chọn chứng chỉ. Xem phần [HTTPS](#https) bên dưới để biết thêm chi tiết.

- Sử dụng `h2c://` làm scheme sẽ sử dụng [`http` transport](#the-http-transport) với [phiên bản HTTP](#versions) được thiết lập để cho phép kết nối HTTP/2 văn bản thuần túy (cleartext).

- Sử dụng `http://` làm scheme giống hệt như việc bỏ qua scheme, vì HTTP đã là mặc định. Cú pháp này được bao gồm để đồng bộ với các phím tắt scheme khác.

Các scheme không thể được trộn lẫn, vì chúng sửa đổi cấu hình vận chuyển chung (một transport được bật TLS không thể mang cả HTTPS và HTTP văn bản thuần túy). Bất kỳ cấu hình transport rõ ràng nào cũng sẽ không bị ghi đè, và việc bỏ qua các scheme hoặc sử dụng các cổng khác sẽ không giả định một transport cụ thể nào.

Khi sử dụng IPv6 với một zone (ví dụ: địa chỉ link-local với một giao diện mạng cụ thể), một scheme **không thể** được sử dụng làm phím tắt vì ký tự `%` sẽ dẫn đến lỗi phân tích cú pháp URL; hãy cấu hình transport một cách rõ ràng thay thế.

Khi sử dụng dạng [địa chỉ mạng](/docs/conventions#network-addresses), loại mạng được chỉ định dưới dạng tiền tố cho địa chỉ upstream. Điều này không thể kết hợp với một URL scheme. Trong trường hợp đặc biệt, `unix+h2c/` được hỗ trợ như một phím tắt cho mạng `unix/` cộng với các hiệu ứng tương tự như scheme `h2c://`. Các dải cổng (port ranges) được hỗ trợ như một phím tắt, mở rộng thành nhiều upstream với cùng một host.

Địa chỉ upstream **không được** chứa đường dẫn (path) hoặc chuỗi truy vấn (query string), vì điều đó ngụ ý việc ghi lại yêu cầu đồng thời trong khi proxy, hành vi này không được xác định hoặc hỗ trợ. Bạn có thể sử dụng chỉ thị [`rewrite`](/docs/caddyfile/directives/rewrite) nếu bạn cần điều này.

Nếu địa chỉ không phải là URL (nghĩa là không có scheme), thì có thể sử dụng [các trình giữ chỗ (placeholders)](/docs/caddyfile/concepts#placeholders), nhưng điều này làm cho upstream trở thành _tĩnh một cách động_ (dynamically static), có nghĩa là nhiều backend khác nhau có thể đóng vai trò như một upstream tĩnh duy nhất xét về mặt kiểm tra sức khỏe và cân bằng tải. Chúng tôi khuyên bạn nên sử dụng module [upstream động](#dynamic-upstreams) nếu có thể. Khi sử dụng các trình giữ chỗ, một cổng **phải** được bao gồm (hoặc bởi trình giữ chỗ thay thế, hoặc dưới dạng hậu tố tĩnh cho địa chỉ).


<a id="dynamic-upstreams"></a>
### Upstream động

Proxy ngược của Caddy đi kèm tiêu chuẩn với một số module upstream động. Lưu ý rằng việc sử dụng các upstream động có ảnh hưởng đến việc cân bằng tải và kiểm tra sức khỏe, tùy thuộc vào cấu hình chính sách cụ thể: kiểm tra sức khỏe chủ động không chạy cho các upstream động; và cân bằng tải cũng như kiểm tra sức khỏe thụ động sẽ phục vụ tốt nhất nếu danh sách các upstream tương đối ổn định và nhất quán (đặc biệt là với round-robin). Lý tưởng nhất là các module upstream động chỉ trả về các backend khỏe mạnh, có thể sử dụng được.


#### SRV

Truy xuất các upstream từ các bản ghi DNS SRV.

```caddy-d
	dynamic srv [<full_name>] {
		service   <service>
		proto     <proto>
		name      <name>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
	}
```

- **&lt;full_name&gt;** là tên miền đầy đủ của bản ghi cần tra cứu (ví dụ: `_service._proto.name`).
- **service** là thành phần dịch vụ của tên đầy đủ.
- **proto** là thành phần giao thức của tên đầy đủ. Hoặc `tcp` hoặc `udp`.
- **name** là thành phần tên. Hoặc, nếu `service` và `proto` trống, thì đó là tên miền đầy đủ để truy vấn.
- **refresh** là tần suất làm mới các kết quả đã lưu trong bộ nhớ cache. Mặc định: `1m`
- **resolvers** là danh sách các trình phân giải DNS để ghi đè các trình phân giải của hệ thống.
- **dial_timeout** là thời gian chờ để quay số truy vấn.
- **dial_fallback_delay** là thời gian chờ trước khi tạo kết nối RFC 6555 Fast Fallback. Mặc định: `300ms`



#### A/AAAA

Truy xuất các upstream từ các bản ghi DNS A/AAAA.

```caddy-d
	dynamic a [<name> <port>] {
		name      <name>
		port      <port>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
		versions ipv4|ipv6
	}
```

- **name** là tên miền để truy vấn.
- **port** là cổng để sử dụng cho backend.
- **refresh** là tần suất làm mới các kết quả đã lưu trong bộ nhớ cache. Mặc định: `1m`
- **resolvers** là danh sách các trình phân giải DNS để ghi đè các trình phân giải của hệ thống.
- **dial_timeout** là thời gian chờ để quay số truy vấn.
- **dial_fallback_delay** là thời gian chờ trước khi tạo kết nối RFC 6555 Fast Fallback. Mặc định: `300ms`
- **versions** là danh sách các phiên bản IP để phân giải. Mặc định: `ipv4 ipv6` tương ứng với cả bản ghi A và AAAA tương ứng.


#### Multi

Nối kết quả của nhiều module upstream động. Hữu ích nếu bạn muốn có các nguồn upstream dự phòng, ví dụ: một cụm SRV chính được sao lưu bởi một cụm SRV phụ.

```caddy-d
	dynamic multi {
		<source> [...]
	}
```

- **&lt;source&gt;** là tên của module cho các upstream động, theo sau là cấu hình của nó. Có thể chỉ định nhiều hơn một.




<a id="load-balancing"></a>
## Cân bằng tải

Cân bằng tải thường được sử dụng để phân chia lưu lượng giữa nhiều upstream. Bằng cách bật thử lại (retries), nó cũng có thể được sử dụng với một hoặc nhiều upstream, để giữ các yêu cầu cho đến khi có thể chọn được một upstream khỏe mạnh (ví dụ: để chờ và giảm thiểu lỗi trong khi khởi động lại hoặc triển khai lại một upstream).

Tính năng này được bật theo mặc định, với chính sách `random`. Các lần thử lại bị tắt theo mặc định.

- **lb_policy** <span id="lb_policy"/> là tên của chính sách cân bằng tải, cùng với bất kỳ tùy chọn nào. Mặc định: `random`.

  Đối với các chính sách liên quan đến băm (hashing), thuật toán [highest-random-weight (HRW)](https://en.wikipedia.org/wiki/Rendezvous_hashing) được sử dụng để đảm bảo rằng một khách hàng hoặc yêu cầu có cùng mã băm (hash key) được ánh chiếu đến cùng một upstream, ngay cả khi danh sách các upstream thay đổi.

  Một số chính sách hỗ trợ dự phòng (fallback) như một tùy chọn, nếu được ghi chú, trong trường hợp đó chúng nhận một [khối (block)](/docs/caddyfile/concepts#blocks) với `fallback <policy>` nhận một chính sách cân bằng tải khác. Đối với các chính sách đó, dự phòng mặc định là `random`. Cấu hình dự phòng cho phép sử dụng một chính sách phụ nếu chính sách chính không chọn được cái nào, cho phép các kết hợp mạnh mẽ. Dự phòng có thể được lồng nhau nhiều lần nếu muốn.
  
  Ví dụ, `header` có thể được sử dụng làm chính sách chính để cho phép các nhà phát triển chọn một upstream cụ thể, với dự phòng là `first` cho tất cả các kết nối khác để thực hiện chuyển đổi dự phòng chính/phụ (primary/secondary failover).
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` chọn ngẫu nhiên một upstream

	- `random_choose <n>` chọn ngẫu nhiên hai hoặc nhiều upstream, sau đó chọn một cái có tải ít nhất (`n` thường là 2)

	- `first` chọn upstream có sẵn đầu tiên, theo thứ tự chúng được định nghĩa trong cấu hình, cho phép chuyển đổi dự phòng chính/phụ; hãy nhớ bật kiểm tra sức khỏe cùng với cái này, nếu không việc chuyển đổi dự phòng sẽ không xảy ra

	- `round_robin` lặp qua từng upstream lần lượt

	- `weighted_round_robin <weights...>` lặp qua từng upstream lần lượt, tôn trọng các trọng số được cung cấp. Số lượng đối số trọng số phải khớp với số lượng upstream được cấu hình. Trọng số phải là các số nguyên không âm. Ví dụ với hai upstream và trọng số `5 1`, upstream đầu tiên sẽ được chọn 5 lần liên tiếp trước khi upstream thứ hai được chọn một lần, sau đó chu kỳ lặp lại. Nếu số không được sử dụng làm trọng số, điều này sẽ tắt việc chọn upstream đó cho các yêu cầu mới.

	- `least_conn` chọn upstream có số lượng yêu cầu hiện tại ít nhất; nếu có nhiều hơn một host có số lượng yêu cầu ít nhất, thì một trong những host đó được chọn ngẫu nhiên

	- `ip_hash` ánh chiếu IP từ xa (remote IP - peer trực tiếp) tới một upstream cố định (sticky upstream)

	- `client_ip_hash` ánh chiếu IP của khách hàng (client IP) tới một upstream cố định; điều này tốt nhất nên kết hợp với [tùy chọn toàn cục `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) cho phép phân tích cú pháp IP khách thực, nếu không nó sẽ hoạt động giống như `ip_hash`

	- `uri_hash` ánh chiếu URI yêu cầu (đường dẫn và truy vấn) tới một upstream cố định

	- `query [key]` ánh chiếu một truy vấn yêu cầu tới một upstream cố định, bằng cách băm giá trị truy vấn; nếu khóa được chỉ định không hiện diện, chính sách dự phòng sẽ được sử dụng để chọn một upstream (mặc định là `random`)

	- `header [field]` ánh chiếu một header yêu cầu tới một upstream cố định, bằng cách băm giá trị header; nếu trường header được chỉ định không hiện diện, chính sách dự phòng sẽ được sử dụng để chọn một upstream (mặc định là `random`)

	- `cookie [<name> [<secret>]]` trong yêu cầu đầu tiên từ khách hàng (khi chưa có cookie), chính sách dự phòng sẽ được sử dụng để chọn một upstream (mặc định là `random`), và một header `Set-Cookie` được thêm vào phản hồi (tên cookie mặc định là `lb` nếu không được chỉ định). Giá trị cookie là địa chỉ quay số của upstream được chọn, được băm bằng HMAC-SHA256 (sử dụng `<secret>` làm bí mật dùng chung, chuỗi trống nếu không được chỉ định).
	
	  Trong các yêu cầu tiếp theo khi có cookie, giá trị cookie sẽ được ánh chiếu tới cùng một upstream nếu nó có sẵn; nếu không có sẵn hoặc không tìm thấy, một upstream mới được chọn bằng chính sách dự phòng, và cookie được thêm vào phản hồi.

	  Nếu bạn muốn sử dụng một upstream cụ thể cho mục đích gỡ lỗi, bạn có thể băm địa chỉ upstream với bí mật và thiết lập cookie trong trình duyệt HTTP của mình (trình duyệt hoặc cách khác). Ví dụ, với PHP, bạn có thể chạy đoạn mã sau để tính toán giá trị cookie, trong đó `10.1.0.10:8080` là địa chỉ của một trong các upstream của bạn và `secret` là bí mật đã cấu hình.
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```
	
	  Bạn có thể thiết lập cookie trong trình duyệt của mình qua bảng điều khiển Javascript, ví dụ để thiết lập cookie có tên `lb`:
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries** <span id="lb_retries"/> là số lần thử lại việc chọn các backend có sẵn cho mỗi yêu cầu nếu host có sẵn tiếp theo bị hỏng. Theo mặc định, các lần thử lại bị tắt (bằng không).

  Nếu [`lb_try_duration`](#lb_try_duration) cũng được cấu hình, thì các lần thử lại có thể dừng sớm nếu đạt đến thời lượng đó. Nói cách khác, thời lượng thử lại được ưu tiên hơn số lần thử lại.

- **lb_try_duration** <span id="lb_try_duration"/> là một [giá trị thời lượng](/docs/conventions#durations) xác định thời gian cố gắng chọn các backend có sẵn cho mỗi yêu cầu nếu host có sẵn tiếp theo bị hỏng. Theo mặc định, các lần thử lại bị tắt (thời lượng bằng không).

  Khách hàng sẽ đợi tối đa thời gian này trong khi trình cân bằng tải cố gắng tìm một host upstream có sẵn. Một điểm bắt đầu hợp lý có thể là `5s` vì thời gian chờ quay số mặc định của vận chuyển HTTP là `3s`, do đó điều này cho phép ít nhất một lần thử lại nếu upstream được chọn đầu tiên không thể kết nối; nhưng hãy thoải mái thử nghiệm để tìm ra sự cân bằng phù hợp cho trường hợp sử dụng của bạn.

- **lb_try_interval** <span id="lb_try_interval"/> là một [giá trị thời lượng](/docs/conventions#durations) xác định thời gian chờ giữa việc chọn host tiếp theo từ nhóm. Mặc định là `250ms`. Chỉ có ý nghĩa khi một yêu cầu đến một host upstream thất bại. Hãy lưu ý rằng việc đặt giá trị này thành `0` với một `lb_try_duration` khác không có thể khiến CPU hoạt động quá mức nếu tất cả các backend đều hỏng và độ trễ rất thấp.

- **lb_retry_match** <span id="lb_retry_match"/> hạn chế những yêu cầu nào được phép thử lại. Một yêu cầu phải khớp với điều kiện này để được thử lại nếu kết nối đến upstream thành công nhưng vòng lặp (round-trip) tiếp theo thất bại. Nếu kết nối đến upstream thất bại, một lần thử lại luôn được phép. Theo mặc định, chỉ các yêu cầu `GET` mới được thử lại.

  Cú pháp cho tùy chọn này giống với [các trình khớp yêu cầu có tên (named request matchers)](/docs/caddyfile/matchers#named-matchers), nhưng không có `@name`. Nếu bạn chỉ cần một trình khớp duy nhất, bạn có thể cấu hình nó trên cùng một dòng. Đối với nhiều trình khớp, một khối là cần thiết.



<a id="active-health-checks"></a>
### Kiểm tra sức khỏe chủ động (Active health checks)

Kiểm tra sức khỏe chủ động thực hiện việc kiểm tra sức khỏe trong nền theo một bộ hẹn giờ. Để bật tính năng này, yêu cầu phải có `health_uri` hoặc `health_port`.

- **health_uri** <span id="health_uri"/> là đường dẫn URI (và truy vấn tùy chọn) để kiểm tra sức khỏe chủ động.

- **health_upstream** <span id="health_upstream"/> là ip:port để sử dụng cho các cuộc kiểm tra sức khỏe chủ động, nếu khác với upstream. Điều này nên được sử dụng song song với `health_header` và `{http.reverse_proxy.active.target_upstream}`.

- **health_port** <span id="health_port"/> là cổng để sử dụng cho các cuộc kiểm tra sức khỏe chủ động, nếu khác với cổng của upstream. Bị bỏ qua nếu `health_upstream` được sử dụng.

- **health_interval** <span id="health_interval"/> là một [giá trị thời lượng](/docs/conventions#durations) xác định tần suất thực hiện các cuộc kiểm tra sức khỏe chủ động. Mặc định: `30s`.

- **health_passes** <span id="health_passes"/> là số lần kiểm tra sức khỏe thành công liên tiếp cần thiết trước khi đánh dấu backend là khỏe mạnh trở lại. Mặc định: `1`.

- **health_fails** <span id="health_fails"/> là số lần kiểm tra sức khỏe thất bại liên tiếp cần thiết trước khi đánh dấu backend là không khỏe mạnh. Mặc định: `1`.

- **health_timeout** <span id="health_timeout"/> là một [giá trị thời lượng](/docs/conventions#durations) xác định thời gian chờ phản hồi trước khi đánh dấu backend là hỏng. Mặc định: `5s`.

- **health_method** <span id="health_method"/> là phương thức HTTP để sử dụng cho cuộc kiểm tra sức khỏe chủ động. Mặc định: `GET`.

- **health_status** <span id="health_status"/> là mã trạng thái HTTP mong đợi từ một backend khỏe mạnh. Có thể là mã trạng thái 3 chữ số, hoặc một lớp mã trạng thái kết thúc bằng `xx`. Ví dụ: `200` (là mặc định), hoặc `2xx`.

- **health_request_body** <span id="health_request_body"/> là một chuỗi đại diện cho thân yêu cầu (request body) được gửi cùng với cuộc kiểm tra sức khỏe chủ động.

- **health_body** <span id="health_body"/> là một chuỗi con hoặc biểu thức chính quy (regular expression) để khớp với thân phản hồi của một cuộc kiểm tra sức khỏe chủ động. Nếu backend không trả về thân phản hồi khớp, nó sẽ bị đánh dấu là hỏng.

- **health_follow_redirects** <span id="health_follow_redirects"/> sẽ khiến việc kiểm tra sức khỏe tuân theo các chuyển hướng (redirects) được cung cấp bởi upstream. Theo mặc định, một phản hồi chuyển hướng sẽ khiến cuộc kiểm tra sức khỏe được tính là thất bại.

- **health_headers** <span id="health_headers"/> cho phép chỉ định các header để thiết lập trên các yêu cầu kiểm tra sức khỏe chủ động. Điều này hữu ích nếu bạn cần thay đổi header `Host`, hoặc nếu bạn cần cung cấp một số xác thực cho backend của mình như một phần của các cuộc kiểm tra sức khỏe.



<a id="passive-health-checks"></a>
### Kiểm tra sức khỏe thụ động (Passive health checks)

Kiểm tra sức khỏe thụ động xảy ra trực tiếp với các yêu cầu thực tế được proxy. Để bật tính năng này, yêu cầu phải có `fail_duration`.

- **fail_duration** <span id="fail_duration"/> là một [giá trị thời lượng](/docs/conventions#durations) xác định thời gian ghi nhớ một yêu cầu bị lỗi. Một thời lượng > `0` bật tính năng kiểm tra sức khỏe thụ động; mặc định là `0` (tắt). Một điểm bắt đầu hợp lý có thể là `30s` để cân bằng tỷ lệ lỗi với khả năng phản hồi khi đưa một upstream không khỏe mạnh hoạt động trở lại; nhưng hãy thoải mái thử nghiệm để tìm ra sự cân bằng phù hợp cho trường hợp sử dụng của bạn.

- **max_fails** <span id="max_fails"/> là số lượng yêu cầu thất bại tối đa trong `fail_duration` cần thiết trước khi coi một backend là hỏng; phải >= `1`; mặc định là `1`.

- **unhealthy_status** <span id="unhealthy_status"/> tính một yêu cầu là thất bại nếu phản hồi trả về với một trong các mã trạng thái này. Có thể là mã trạng thái 3 chữ số hoặc một lớp mã trạng thái kết thúc bằng `xx`, ví dụ: `404` hoặc `5xx`.

- **unhealthy_latency** <span id="unhealthy_latency"/> là một [giá trị thời lượng](/docs/conventions#durations) tính một yêu cầu là thất bại nếu nó mất thời gian lâu như thế này để nhận được phản hồi.

- **unhealthy_request_count** <span id="unhealthy_request_count"/> là số lượng yêu cầu đồng thời được phép đến một backend trước khi đánh dấu nó là hỏng. Nói cách khác, nếu một backend cụ thể hiện đang xử lý số lượng yêu cầu này, thì nó được coi là "quá tải" và các backend khác sẽ được ưu tiên thay thế.

  Đây nên là một con số tương đối lớn; cấu hình này có nghĩa là proxy sẽ có giới hạn tổng cộng `unhealthy_request_count × upstreams_count` yêu cầu đồng thời, và bất kỳ yêu cầu nào sau thời điểm đó sẽ dẫn đến lỗi do không có upstream nào khả dụng.


<a id="events"></a>
## Sự kiện (Events)

Khi một upstream chuyển trạng thái từ khỏe mạnh sang không khỏe mạnh hoặc ngược lại, [một sự kiện](/docs/caddyfile/options#event-options) sẽ được phát ra. Các sự kiện này có thể được sử dụng để kích hoạt các hành động khác, chẳng hạn như gửi thông báo hoặc ghi nhật ký. Các sự kiện như sau:

- `healthy` được phát ra khi một upstream được đánh dấu là khỏe mạnh trong khi trước đó nó không khỏe mạnh
- `unhealthy` được phát ra khi một upstream được đánh dấu là không khỏe mạnh trong khi trước đó nó khỏe mạnh

Trong cả hai trường hợp, `host` được bao gồm dưới dạng siêu dữ liệu trong sự kiện để xác định upstream đã thay đổi trạng thái. Nó có thể được sử dụng như một trình giữ chỗ với `{event.data.host}` với trình xử lý sự kiện `exec`, ví dụ.



## Streaming

Theo mặc định, proxy đệm một phần phản hồi để đạt hiệu quả truyền tải.

Proxy cũng hỗ trợ các kết nối WebSocket, thực hiện yêu cầu nâng cấp HTTP sau đó chuyển kết nối sang một đường hầm hai chiều.

<aside class="tip">

Theo mặc định, các kết nối WebSocket bị buộc phải đóng (với một thông báo điều khiển Close được gửi đến cả khách hàng và upstream) khi cấu hình được tải lại. Mỗi yêu cầu giữ một tham chiếu đến cấu hình, vì vậy việc đóng các kết nối cũ là cần thiết để kiểm soát việc sử dụng bộ nhớ. Hành vi đóng này có thể được tùy chỉnh với các tùy chọn [`stream_timeout`](#stream_timeout) và [`stream_close_delay`](#stream_close_delay).

</aside>

- **flush_interval** <span id="flush_interval"/> là một [giá trị thời lượng](/docs/conventions#durations) điều chỉnh tần suất Caddy nên xả (flush) bộ đệm phản hồi cho khách hàng. Theo mặc định, không có việc xả định kỳ. Một giá trị âm (thường là -1) gợi ý "chế độ độ trễ thấp" (low-latency mode) giúp tắt hoàn toàn việc đệm phản hồi và xả ngay lập tức sau mỗi lần ghi cho khách hàng, và không hủy yêu cầu đến backend ngay cả khi khách hàng ngắt kết nối sớm. Tùy chọn này bị bỏ qua và các phản hồi được xả ngay lập tức cho khách hàng nếu một trong những điều sau áp dụng từ phản hồi:
	- `Content-Type: text/event-stream`
	- `Content-Length` không xác định
	- HTTP/2 ở cả hai phía của proxy, `Content-Length` không xác định và `Accept-Encoding` hoặc không được thiết lập hoặc là "identity"

- **request_buffers** <span id="request_buffers"/> sẽ khiến proxy đọc tới lượng byte `<size>` từ thân yêu cầu vào một bộ đệm trước khi gửi nó lên upstream. Điều này rất không hiệu quả và chỉ nên được thực hiện nếu upstream yêu cầu đọc thân yêu cầu mà không có độ trễ (đây là điều mà ứng dụng upstream nên khắc phục). Chỉ thị này chấp nhận tất cả các định dạng kích thước được hỗ trợ bởi [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **response_buffers** <span id="response_buffers"/> sẽ khiến proxy đọc tới lượng byte `<size>` từ thân phản hồi vào một bộ đệm trước khi được trả về cho khách hàng. Điều này nên được tránh nếu có thể vì lý do hiệu suất, nhưng có thể hữu ích nếu backend có các hạn chế về bộ nhớ chặt chẽ hơn. Chỉ thị này chấp nhận tất cả các định dạng kích thước được hỗ trợ bởi [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **stream_timeout** <span id="stream_timeout"/> là một [giá trị thời lượng](/docs/conventions#durations) mà sau đó các yêu cầu phát trực tuyến (streaming) như WebSocket sẽ bị buộc đóng khi kết thúc thời gian chờ. Điều này về cơ bản sẽ hủy các kết nối nếu chúng mở quá lâu. Một điểm bắt đầu hợp lý có thể là `24h` để loại bỏ các kết nối cũ hơn một ngày. Mặc định: không có thời gian chờ.

- **stream_close_delay** <span id="stream_close_delay"/> là một [giá trị thời lượng](/docs/conventions#durations) trì hoãn các yêu cầu phát trực tuyến như WebSocket không bị buộc đóng khi cấu hình được dỡ bỏ; thay vào đó, luồng sẽ vẫn mở cho đến khi hoàn tất việc trì hoãn. Nói cách khác, việc bật tính năng này ngăn các luồng đóng ngay lập tức khi cấu hình của Caddy được tải lại. Bật tính năng này có thể là một ý tưởng hay để tránh tình trạng hàng loạt khách hàng kết nối lại cùng lúc do kết nối của họ bị đóng bởi việc đóng cấu hình trước đó. Một điểm bắt đầu hợp lý có thể là một cái gì đó như `5m` để cho phép người dùng có 5 phút rời khỏi trang một cách tự nhiên sau khi tải lại cấu hình. Mặc định: không trì hoãn.



<a id="headers"></a>
## Header

Proxy có thể **thao tác các header** giữa chính nó và backend:

- **header_up** <span id="header_up"/> thiết lập, thêm (với tiền tố `+`), xóa (với tiền tố `-`), hoặc thực hiện thay thế (bằng cách sử dụng hai đối số, tìm kiếm và thay thế) trong một header yêu cầu đi lên upstream tới backend.

- **header_down** <span id="header_down"/> thiết lập, thêm (với tiền tố `+`), xóa (với tiền tố `-`), hoặc thực hiện thay thế (bằng cách sử dụng hai đối số, tìm kiếm và thay thế) trong một header phản hồi đi xuống từ backend.

Ví dụ, để thiết lập một header yêu cầu, ghi đè lên bất kỳ giá trị hiện có nào:

```caddy-d
header_up Some-Header "the value"
```

Để thêm một header phản hồi; lưu ý rằng có thể có nhiều giá trị cho một trường header:

```caddy-d
header_down +Some-Header "first value"
header_down +Some-Header "second value"
```

Để xóa một header yêu cầu, ngăn nó đến được backend:

```caddy-d
header_up -Some-Header
```

Để xóa tất cả các header yêu cầu khớp, sử dụng khớp hậu tố:

```caddy-d
header_up -Some-*
```

Để xóa _tất cả_ các header yêu cầu, để có thể thêm riêng lẻ những cái bạn muốn (không được khuyến khích):

```caddy-d
header_up -*
```

Để thực hiện thay thế bằng biểu thức chính quy trên một header yêu cầu:

```caddy-d
header_up Some-Header "^prefix-([A-Za-z0-9]*)$" "replaced-$1-suffix"
```

Ngôn ngữ biểu thức chính quy được sử dụng là RE2, được bao gồm trong Go. Xem [tham khảo cú pháp RE2](https://github.com/google/re2/wiki/Syntax) và [tổng quan cú pháp regexp của Go](https://pkg.go.dev/regexp/syntax). Chuỗi thay thế được [mở rộng](https://pkg.go.dev/regexp#Regexp.Expand), cho phép sử dụng các giá trị đã bắt được (captured values), ví dụ `$1` là nhóm bắt đầu tiên.


<a id="defaults"></a>
### Mặc định

Theo mặc định, Caddy chuyển các header đến&mdash;bao gồm cả `Host`&mdash;tới backend mà không sửa đổi, với ba ngoại lệ:

- Nó thiết lập hoặc tăng cường trường header [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For).
- Nó thiết lập trường header [`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto).
- Nó thiết lập trường header [`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host).

<span id="trusted_proxies"/> Đối với các header `X-Forwarded-*` này, theo mặc định, proxy sẽ bỏ qua giá trị của chúng từ các yêu cầu đến, để ngăn chặn giả mạo (spoofing).

Nếu Caddy không phải là máy chủ đầu tiên được kết nối bởi các khách hàng của bạn (ví dụ: khi có CDN đứng trước Caddy), bạn có thể cấu hình `trusted_proxies` với danh sách các dải IP (CIDR) mà từ đó các yêu cầu đến được tin cậy là đã gửi các giá trị tốt cho các header này.

Khuyến khích mạnh mẽ rằng bạn nên cấu hình điều này qua [tùy chọn toàn cục `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) thay vì trong proxy, để điều này áp dụng cho tất cả các trình xử lý proxy trong máy chủ của bạn, và điều này có lợi ích là bật tính năng phân tích cú pháp IP khách hàng.

<aside class="tip">

Nếu bạn đang sử dụng Cloudflare trước Caddy, hãy lưu ý rằng bạn có thể dễ bị giả mạo header `X-Forwarded-For`. Những người bạn của chúng tôi tại [Authelia](https://www.authelia.com) đã ghi lại một [giải pháp khắc phục](https://www.authelia.com/integration/proxies/forwarded-headers/) để cấu hình Cloudflare bỏ qua các giá trị đến cho header này.

</aside>

Ngoài ra, khi sử dụng [`http` transport](#the-http-transport), header `Accept-Encoding: gzip` sẽ được thiết lập, nếu nó thiếu trong yêu cầu từ khách hàng. Điều này cho phép upstream phục vụ nội dung nén nếu nó có thể. Hành vi này có thể bị tắt với [`compression off`](#compression) trên transport.


### HTTPS

Vì (hầu hết) các header giữ nguyên giá trị ban đầu của chúng khi được proxy, nên thường cần phải ghi đè header `Host` bằng địa chỉ upstream đã cấu hình khi proxy tới HTTPS, sao cho header `Host` khớp với giá trị TLS ServerName:

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

Kể từ Caddy v2.11.0, việc này được thực hiện tự động, vì vậy không còn cần thiết phải ghi đè rõ ràng header `Host` khi proxy tới HTTPS nữa. Nếu bạn muốn từ chối hành vi này, bạn có thể đặt header `Host` về giá trị ban đầu của nó (nhưng điều này hiếm khi có ý nghĩa):

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

Header `X-Forwarded-Host` vẫn được chuyển qua [theo mặc định](#defaults), vì vậy upstream vẫn có thể sử dụng nó nếu cần biết giá trị header `Host` ban đầu.

Điều tương tự cũng áp dụng khi kết thúc TLS trong Caddy và proxy qua HTTP, cho dù là đến một cổng hay một unix socket. Thực tế, chính Caddy phải nhận được Host chính xác, khi nó là mục tiêu của `reverse_proxy`. Trong trường hợp unix socket, `upstream_hostport` sẽ là đường dẫn socket và Host phải được thiết lập rõ ràng.



<a id="rewrites"></a>
## Rewrite

Theo mặc định, Caddy thực hiện yêu cầu upstream với cùng một phương thức HTTP và URI như yêu cầu đến, trừ khi việc ghi lại (rewrite) được thực hiện trong chuỗi middleware trước khi nó đến `reverse_proxy`.

Trước khi proxy nó, yêu cầu được nhân bản (cloned); điều này đảm bảo rằng bất kỳ sửa đổi nào được thực hiện đối với yêu cầu trong trình xử lý không bị rò rỉ sang các trình xử lý khác. Điều này hữu ích trong các tình huống mà việc xử lý cần tiếp tục sau proxy.

Ngoài việc [thao tác header](#headers), phương thức và URI của yêu cầu có thể được thay đổi trước khi nó được gửi đến upstream:

- **method** <span id="method"/> thay đổi phương thức HTTP của yêu cầu đã nhân bản. Nếu phương thức được thay đổi thành `GET` hoặc `HEAD`, thì thân yêu cầu đến sẽ _không_ được gửi lên upstream bởi trình xử lý này. Điều này hữu ích nếu bạn muốn cho phép một trình xử lý khác tiêu thụ thân yêu cầu.
- **rewrite** <span id="rewrite"/> thay đổi URI (đường dẫn và truy vấn) của yêu cầu đã nhân bản. Điều này tương tự như chỉ thị [`rewrite`](/docs/caddyfile/directives/rewrite), ngoại trừ việc nó không duy trì việc ghi lại quá phạm vi của trình xử lý này.

Các bản ghi lại này thường hữu ích cho một mô hình như "yêu cầu kiểm tra trước" (pre-check requests), nơi một yêu cầu được gửi đến một máy chủ khác để giúp đưa ra quyết định về cách tiếp tục xử lý yêu cầu hiện tại.

Ví dụ, yêu cầu có thể được gửi đến một cổng xác thực để quyết định xem yêu cầu đó có phải từ một người dùng đã xác thực hay không (ví dụ: yêu cầu có cookie phiên) và nên tiếp tục, hay thay vào đó nên được chuyển hướng đến trang đăng nhập. Đối với mô hình này, Caddy cung cấp một chỉ thị phím tắt [`forward_auth`](/docs/caddyfile/directives/forward_auth) để bỏ qua hầu hết các cấu hình rườm rà.




<a id="transports"></a>
## Transport

**Transport** của proxy Caddy có thể cắm được (pluggable):

- **transport** <span id="transport"/> xác định cách giao tiếp với backend. Mặc định là `http`.


<a id="the-transport"></a>
<a id="the-http-transport"></a>
### Vận chuyển `http`

```caddy-d
transport http {
	read_buffer             <size>
	write_buffer            <size>
	max_response_header     <size>
	proxy_protocol          v1|v2
	dial_timeout            <duration>
	dial_fallback_delay     <duration>
	response_header_timeout <duration>
	expect_continue_timeout <duration>
	resolvers <ip...>
	tls
	tls_client_auth <automate_name> | <cert_file> <key_file>
	tls_insecure_skip_verify
	tls_curves <curves...>
	tls_timeout <duration>
	tls_trust_pool <module>
	tls_server_name <server_name>
	tls_renegotiation <level>
	tls_except_ports <ports...>
	keepalive [off|<duration>]
	keepalive_interval <interval>
	keepalive_idle_conns <max_count>
	keepalive_idle_conns_per_host <count>
	versions <versions...>
	compression off
	max_conns_per_host <count>
	network_proxy <module>
}
```

- **read_buffer** <span id="read_buffer"/> là kích thước của bộ đệm đọc tính bằng byte. Nó chấp nhận tất cả các định dạng được hỗ trợ bởi [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Mặc định: `4KiB`.

- **write_buffer** <span id="write_buffer"/> là kích thước của bộ đệm ghi tính bằng byte. Nó chấp nhận tất cả các định dạng được hỗ trợ bởi [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Mặc định: `4KiB`.

- **max_response_header** <span id="max_response_header"/> là lượng byte tối đa để đọc từ các header phản hồi. Nó chấp nhận tất cả các định dạng được hỗ trợ bởi [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Mặc định: `10MiB`.

- **proxy_protocol** <span id="proxy_protocol"/> bật [giao thức PROXY](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (được phổ biến bởi HAProxy) trên kết nối tới upstream, thêm dữ liệu IP khách thực vào phía trước. Điều này tốt nhất nên kết hợp với [tùy chọn toàn cục `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) nếu Caddy đứng sau một proxy khác. Phiên bản `v1` và `v2` được hỗ trợ. Điều này chỉ nên được sử dụng nếu bạn biết máy chủ upstream có thể phân tích cú pháp giao thức PROXY. Theo mặc định, tính năng này bị tắt.

- **dial_timeout** <span id="dial_timeout"/> là [thời lượng](/docs/conventions#durations) tối đa để đợi khi kết nối tới socket upstream. Mặc định: `3s`.

- **dial_fallback_delay** <span id="dial_fallback_delay"/> là [thời lượng](/docs/conventions#durations) tối đa để đợi trước khi tạo kết nối RFC 6555 Fast Fallback. Một giá trị âm sẽ tắt tính năng này. Mặc định: `300ms`.

- **response_header_timeout** <span id="response_header_timeout"/> là [thời lượng](/docs/conventions#durations) tối đa để đợi việc đọc các header phản hồi từ upstream. Mặc định: Không có thời gian chờ.

- **expect_continue_timeout** <span id="expect_continue_timeout"/> là [thời lượng](/docs/conventions#durations) tối đa để đợi các header phản hồi đầu tiên của upstream sau khi đã ghi hoàn toàn các header yêu cầu nếu yêu cầu có header `Expect: 100-continue`. Mặc định: Không có thời gian chờ.

- **read_timeout** <span id="read_timeout"/> là [thời lượng](/docs/conventions#durations) tối đa để đợi cho lần đọc tiếp theo từ backend. Mặc định: Không có thời gian chờ.

- **write_timeout** <span id="write_timeout"/> là [thời lượng](/docs/conventions#durations) tối đa để đợi cho các lần ghi tiếp theo tới backend. Mặc định: Không có thời gian chờ.

- **resolvers** <span id="resolvers"/> là danh sách các trình phân giải DNS để ghi đè các trình phân giải của hệ thống.

- **tls** <span id="tls"/> sử dụng HTTPS với backend. Điều này sẽ được bật tự động nếu bạn chỉ định backend bằng scheme `https://`, hoặc nếu bất kỳ tùy chọn `tls_*` nào bên dưới được cấu hình.

- **tls_client_auth** <span id="tls_client_auth"/> bật xác thực khách hàng TLS theo một trong hai cách: (1) bằng cách chỉ định một tên miền mà Caddy nên lấy chứng chỉ và duy trì việc gia hạn, hoặc (2) bằng cách chỉ định một tệp chứng chỉ và khóa để xuất trình cho xác thực khách hàng TLS với backend.

- **tls_insecure_skip_verify** <span id="tls_insecure_skip_verify"/> tắt tính năng xác minh bắt tay TLS, làm cho kết nối trở nên không an toàn và dễ bị tấn công xen giữa (man-in-the-middle). _Không sử dụng trong môi trường thực tế (production)._

- **tls_curves** <span id="tls_curves"/> là danh sách các đường cong elliptic được hỗ trợ cho kết nối upstream. Các mặc định của Caddy là hiện đại và an toàn, vì vậy bạn chỉ cần cấu hình điều này nếu bạn có các yêu cầu cụ thể.

- **tls_timeout** <span id="tls_timeout"/> là [thời lượng](/docs/conventions#durations) tối đa để đợi quá trình bắt tay TLS hoàn tất. Mặc định: Không có thời gian chờ.

- **tls_trust_pool** <span id="tls_trust_pool"/> cấu hình nguồn của các cơ quan cấp chứng chỉ (CA) đáng tin cậy tương tự như [chỉ thị phụ `trust_pool`](/docs/caddyfile/directives/tls#trust_pool) được mô tả trong tài liệu chỉ thị `tls`. Danh sách các nguồn trust pool có sẵn trong cài đặt Caddy tiêu chuẩn có sẵn [tại đây](/docs/caddyfile/directives/tls#trust-pool-providers).

- **tls_server_name** <span id="tls_server_name"/> thiết lập tên máy chủ được sử dụng khi xác minh chứng chỉ nhận được trong quá trình bắt tay TLS. Theo mặc định, điều này sẽ sử dụng phần máy chủ của địa chỉ upstream.

  Bạn chỉ cần ghi đè điều này nếu địa chỉ upstream của bạn không khớp với chứng chỉ mà upstream có khả năng sử dụng. Ví dụ: nếu địa chỉ upstream là một địa chỉ IP, thì bạn sẽ cần cấu hình điều này thành tên máy chủ đang được máy chủ upstream phục vụ.

  Có thể sử dụng trình giữ chỗ yêu cầu, trong trường hợp đó một bản sao của cấu hình vận chuyển HTTP sẽ được sử dụng cho mỗi yêu cầu, điều này có thể gây giảm hiệu suất.

- **tls_renegotiation** <span id="tls_renegotiation"/> thiết lập cấp độ thương lượng lại TLS (TLS renegotiation). Thương lượng lại TLS là hành động thực hiện các lần bắt tay tiếp theo sau lần bắt tay đầu tiên. Cấp độ có thể là một trong số:
  - `never` (mặc định) tắt tính năng thương lượng lại.
  - `once` cho phép máy chủ từ xa yêu cầu thương lượng lại một lần trên mỗi kết nối.
  - `freely` cho phép máy chủ từ xa yêu cầu thương lượng lại liên tục.

- **tls_except_ports** <span id="tls_except_ports"/> khi TLS được bật, nếu mục tiêu upstream sử dụng một trong các cổng đã cho, TLS sẽ bị tắt cho các kết nối đó. Điều này có thể hữu ích khi cấu hình các upstream động, nơi một số upstream mong đợi HTTP và những cái khác mong đợi yêu cầu HTTPS.

- **keepalive** <span id="keepalive"/> là `off` hoặc một [giá trị thời lượng](/docs/conventions#durations) chỉ định thời gian duy trì các kết nối mở (thời gian chờ). Mặc định: `2m`.

  ⚠️ Các yêu cầu tới các upstream HTTP/1.1 có thể thất bại do lỗi "connection reset by peer" nếu thời lượng keepalive vượt quá thời gian chờ keepalive của máy chủ upstream. Các yêu cầu lũy đẳng (idempotent requests) sẽ được thử lại bởi vận chuyển HTTP của Go, nhưng Caddy sẽ phản hồi với mã trạng thái 502 trong các trường hợp khác.

- **keepalive_interval** <span id="keepalive_interval"/> là [thời lượng](/docs/conventions#durations) giữa các lần kiểm tra độ hoạt động (liveness probes). Mặc định: `30s`.

- **keepalive_idle_conns** <span id="keepalive_idle_conns"/> xác định số lượng kết nối tối đa được duy trì. Mặc định: Không giới hạn.

- **keepalive_idle_conns_per_host** <span id="keepalive_idle_conns_per_host"/> nếu khác không, sẽ kiểm soát số lượng kết nối rảnh (keep-alive) tối đa được duy trì cho mỗi host. Mặc định: `32`.

- **versions** <span id="versions"/> cho phép tùy chỉnh các phiên bản HTTP nào được hỗ trợ.
  
  Các tùy chọn hợp lệ là: `1.1`, `2`, `h2c`, `3`. 

  Mặc định: `1.1 2`, hoặc nếu [scheme của upstream](#upstream-addresses) là `h2c://`, thì mặc định là `h2c 2`.

  `h2c` cho phép kết nối HTTP/2 văn bản thuần túy (cleartext) tới upstream. Đây là một tính năng không tiêu chuẩn không sử dụng vận chuyển HTTP mặc định của Go, vì vậy nó loại trừ các tính năng khác.

  `3` cho phép kết nối HTTP/3 tới upstream. ⚠️ Đây là một tính năng thử nghiệm và có thể thay đổi.

- **compression** <span id="compression"/> có thể được sử dụng để tắt nén tới backend bằng cách đặt nó thành `off`.

- **max_conns_per_host** <span id="max_conns_per_host"/> tùy chọn giới hạn tổng số kết nối trên mỗi host, bao gồm các kết nối ở trạng thái quay số (dialing), đang hoạt động (active) và rảnh (idle). Mặc định: Không giới hạn.

- **network_proxy** <span id="network_proxy"/> chỉ định tên của một module proxy mạng để sử dụng cho các yêu cầu tới máy chủ upstream. Nếu không được cấu hình rõ ràng, Caddy tôn trọng proxy được cấu hình qua các biến môi trường theo [thư viện tiêu chuẩn Go](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment), ví dụ: `HTTP_PROXY`, `HTTPS_PROXY`, và `NO_PROXY`. Khi một giá trị được cung cấp cho tham số này, các yêu cầu sẽ chảy qua proxy ngược theo thứ tự sau: Khách hàng (người dùng) → `reverse_proxy` → `network_proxy` → upstream. Các module tích hợp sẵn là:
	- `none`, được sử dụng để bỏ qua các cài đặt môi trường của `HTTP_PROXY`, `HTTPS_PROXY`, và `NO_PROXY`.
	- `url <url>`, được sử dụng để chỉ định một URL duy nhất ghi đè cấu hình môi trường.

<a id="the-transport"></a>
<a id="the-fastcgi-transport"></a>
<a id="the-fastcgi-transport"></a>
### Vận chuyển `fastcgi`

```caddy-d
transport fastcgi {
	root  <path>
	split <at>
	env   <key> <value>
	resolve_root_symlink
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>
	capture_stderr
}
```

- **root** <span id="root"/> là gốc (root) của trang web. Mặc định: `{http.vars.root}` hoặc thư mục làm việc hiện tại.

- **split** <span id="split"/> là nơi để chia đường dẫn nhằm lấy PATH_INFO ở cuối URI.

- **env** <span id="env"/> thiết lập một biến môi trường bổ sung cho giá trị đã cho. Có thể được chỉ định nhiều lần cho nhiều biến môi trường.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> cho phép phân giải thư mục `root` thành giá trị thực tế của nó bằng cách đánh giá một liên kết tượng trưng (symbolic link), nếu có.

- **dial_timeout** <span id="dial_timeout"/> là thời gian chờ khi kết nối tới socket upstream. Chấp nhận [giá trị thời lượng](/docs/conventions#durations). Mặc định: `3s`.

- **read_timeout** <span id="read_timeout"/> là thời gian chờ khi đọc từ máy chủ FastCGI. Chấp nhận [giá trị thời lượng](/docs/conventions#durations). Mặc định: không có thời gian chờ.

- **write_timeout** <span id="write_timeout"/> là thời gian chờ khi gửi tới máy chủ FastCGI. Chấp nhận [giá trị thời lượng](/docs/conventions#durations). Mặc định: không có thời gian chờ.

- **capture_stderr** <span id="capture_stderr"/> cho phép thu thập và ghi nhật ký bất kỳ thông báo nào được gửi bởi máy chủ fastcgi upstream trên `stderr`. Nhật ký được thực hiện ở cấp độ `WARN` theo mặc định. Nếu phản hồi có trạng thái `4xx` hoặc `5xx`, thì cấp độ `ERROR` sẽ được sử dụng thay thế. Theo mặc định, `stderr` bị bỏ qua.

<aside class="tip">

Nếu bạn đang cố gắng phục vụ một ứng dụng PHP hiện đại, bạn có thể đang tìm kiếm [chỉ thị `php_fastcgi`](/docs/caddyfile/directives/php_fastcgi), đây là một phím tắt cho một proxy sử dụng chỉ thị `fastcgi`, với các bản ghi lại cần thiết để sử dụng `index.php` làm điểm vào định tuyến (routing entrypoint).

</aside>



<a id="intercepting-responses"></a>
## Chặn phản hồi (Intercepting responses)

Proxy ngược có thể được cấu hình để chặn các phản hồi từ backend. Để tạo điều kiện thuận lợi cho việc này, [các trình khớp phản hồi (response matchers)](/docs/caddyfile/response-matchers) có thể được xác định (tương tự như cú pháp của trình khớp yêu cầu) và tuyến đường `handle_response` đầu tiên khớp sẽ được gọi.

Khi một trình xử lý phản hồi được gọi, phản hồi từ backend sẽ không được ghi cho khách hàng, và tuyến đường `handle_response` được cấu hình sẽ được thực thi thay thế, và tuyến đường đó có nhiệm vụ ghi phản hồi. Nếu tuyến đường _không_ ghi phản hồi, thì việc xử lý yêu cầu sẽ tiếp tục với bất kỳ trình xử lý nào được [sắp xếp sau](/docs/caddyfile/directives#directive-order) `reverse_proxy` này.

- **@name** là tên của một [trình khớp phản hồi](/docs/caddyfile/response-matchers). Miễn là mỗi trình khớp phản hồi có một tên duy nhất, có thể xác định nhiều trình khớp. Một phản hồi có thể được khớp dựa trên mã trạng thái và sự hiện diện hoặc giá trị của một header phản hồi.

- **replace_status** <span id="replace_status"/> chỉ đơn giản là thay đổi mã trạng thái của phản hồi khi khớp bởi trình khớp đã cho.

- **handle_response** <span id="handle_response"/> xác định tuyến đường để thực thi khi khớp bởi trình khớp đã cho (hoặc, nếu bỏ qua trình khớp, cho tất cả các phản hồi). Khối khớp đầu tiên sẽ được áp dụng. Bên trong một khối `handle_response`, bất kỳ [chỉ thị](/docs/caddyfile/directives) nào khác cũng có thể được sử dụng.

Ngoài ra, bên trong `handle_response`, hai chỉ thị trình xử lý đặc biệt có thể được sử dụng:

- **copy_response** <span id="copy_response"/> sao chép thân phản hồi nhận được từ backend trả về cho khách hàng. Tùy chọn cho phép thay đổi mã trạng thái của phản hồi trong khi thực hiện việc đó. Chỉ thị này được [sắp xếp trước `respond`](/docs/caddyfile/directives#directive-order).

- **copy_response_headers** <span id="copy_response_headers"/> sao chép các header phản hồi từ backend cho khách hàng, tùy chọn bao gồm _HOẶC_ loại trừ một danh sách các trường header (không thể chỉ định cả `include` và `exclude`). Chỉ thị này được [sắp xếp sau `header`](/docs/caddyfile/directives#directive-order).

Ba trình giữ chỗ sẽ có sẵn trong các tuyến đường `handle_response`:

- `{rp.status_code}` Mã trạng thái từ phản hồi của backend.

- `{rp.status_text}` Văn bản trạng thái từ phản hồi của backend.

- `{rp.header.*}` Các header từ phản hồi của backend.

Mặc dù trình xử lý phản hồi proxy ngược có thể sao chép phản hồi mới nhận được từ proxy ngược cho khách hàng, nó không thể chuyển phản hồi mới đó cho một proxy ngược tiếp theo. Mỗi lần sử dụng `reverse_proxy` đều nhận được thân từ yêu cầu gốc (hoặc đã được sửa đổi với một module khác).




<a id="examples"></a>
## Ví dụ

Proxy ngược tất cả các yêu cầu tới một backend cục bộ:

```caddy
example.com {
	reverse_proxy localhost:9005
}
```


[Cân bằng tải](#load-balancing) tất cả các yêu cầu [giữa 3 backend](#upstreams):

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```


Tương tự, nhưng chỉ các yêu cầu trong `/api`, và cố định bằng cách sử dụng [chính sách `cookie`](#lb_policy):

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```


Sử dụng [kiểm tra sức khỏe chủ động](#active-health-checks) để xác định backend nào khỏe mạnh, và bật [thử lại](#lb_try_duration) cho các kết nối thất bại, giữ yêu cầu cho đến khi tìm thấy một backend khỏe mạnh:

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```


Cấu hình một số [tùy chọn vận chuyển (transport options)](#transports):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```


Proxy ngược tới một [upstream HTTPS](#https) (kể từ v2.11.0, Caddy sẽ tự động thiết lập header `Host` khớp với máy chủ của upstream, vì vậy không còn cần thiết phải thực hiện thủ công):

```caddy
example.com {
	reverse_proxy https://example.com
}
```


Proxy ngược tới một upstream HTTPS, nhưng [⚠️ tắt xác minh TLS](#tls_insecure_skip_verify). Điều này KHÔNG ĐƯỢC KHUYẾN KHÍCH, vì nó tắt tất cả các kiểm tra bảo mật mà HTTPS cung cấp; việc proxy qua HTTP trong mạng nội bộ được ưu tiên hơn nếu có thể, vì nó tránh được cảm giác bảo mật giả tạo:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```


Thay vào đó, bạn có thể thiết lập sự tin cậy với upstream bằng cách [tin tưởng rõ ràng vào chứng chỉ của upstream](#tls_trust_pool), và (tùy chọn) thiết lập TLS-SNI khớp với tên máy chủ trong chứng chỉ của upstream:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /path/to/cert.pem
			tls_server_name app.example.com
		}
	}
}
```



[Loại bỏ tiền tố đường dẫn](handle_path) trước khi proxy; nhưng hãy lưu ý về [vấn đề thư mục con (subfolder problem) <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575):

```caddy
example.com {
	handle_path /prefix/* {
		reverse_proxy localhost:9000
	}
}
```


Thay thế tiền tố đường dẫn trước khi proxy, sử dụng một [`rewrite`](/docs/caddyfile/directives/rewrite):

```caddy
example.com {
	handle_path /old-prefix/* {
		rewrite /new-prefix{path}
		reverse_proxy localhost:9000
	}
}
```


Hỗ trợ `X-Accel-Redirect`, tức là phục vụ các tệp tĩnh theo yêu cầu, bằng cách [chặn phản hồi](#intercepting-responses):

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {rp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```


Trang lỗi tùy chỉnh cho các lỗi từ upstream, bằng cách [chặn các phản hồi lỗi](#intercepting-responses) theo mã trạng thái:

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root /path/to/error/pages
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```


Lấy backend [một cách động](#dynamic-upstreams) từ các truy vấn DNS [bản ghi `A`/`AAAA`](#aaaaa):

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```


Lấy backend [một cách động](#dynamic-upstreams) từ các truy vấn DNS [bản ghi `SRV`](#srv):

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```


Sử dụng [kiểm tra sức khỏe chủ động](#active-health-checks) và `health_upstream` có thể hữu ích khi tạo một dịch vụ trung gian để thực hiện kiểm tra sức khỏe kỹ lưỡng hơn. `{http.reverse_proxy.active.target_upstream}` sau đó có thể được sử dụng như một header để cung cấp upstream ban đầu cho dịch vụ kiểm tra sức khỏe.

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
