---
title: acme_server (Chỉ thị Caddyfile)
---

# acme_server

Một trình xử lý máy chủ [giao thức ACME](https://tools.ietf.org/html/rfc8555) được tích hợp sẵn. Điều này cho phép một phiên bản Caddy cấp chứng chỉ cho bất kỳ phần mềm tương thích ACME nào khác (bao gồm cả các phiên bản Caddy khác).

Khi được bật, các yêu cầu khớp với đường dẫn `/acme/*` sẽ được xử lý bởi máy chủ ACME.


<a id="client-configuration"></a>
## Cấu hình máy khách

Sử dụng các giá trị mặc định của máy chủ ACME, các máy khách ACME chỉ cần được cấu hình để sử dụng `https://localhost/acme/local/directory` làm điểm cuối ACME của họ. (`local` là ID của CA mặc định của Caddy.)


<a id="syntax"></a>
## Cú pháp

```caddy-d
acme_server [<matcher>] {
	ca         <id>
	lifetime   <duration>
	resolvers  <resolvers...>
	challenges <challenges...>
	allow_wildcard_names
	allow {
		domains <domains...>
		ip_ranges <addresses...>
	}
	deny {
		domains <domains...>
		ip_ranges <addresses...>
	}
}
```

- **ca** chỉ định ID của tổ chức phát hành chứng chỉ (CA) dùng để ký các chứng chỉ. Mặc định là `local`, là CA mặc định của Caddy, dành cho các chứng chỉ tự ký sử dụng cục bộ, thường thấy nhất trong môi trường phát triển. Để sử dụng rộng rãi hơn, bạn nên chỉ định một CA khác để tránh nhầm lẫn. Nếu CA với ID đã cho chưa tồn tại, nó sẽ được tạo. Xem [tùy chọn toàn cục ứng dụng PKI](/docs/caddyfile/options#pki-options) để cấu hình các CA thay thế.

- **lifetime** (Mặc định: `12h`) là một [khoảng thời gian](/docs/conventions#durations) chỉ định thời hạn hiệu lực cho các chứng chỉ được cấp. Giá trị này phải nhỏ hơn thời hạn của [chứng chỉ trung gian](/docs/caddyfile/options#intermediate-lifetime) được sử dụng để ký. Không nên thay đổi giá trị này trừ khi thực sự cần thiết.

- **resolvers** là địa chỉ của các trình giải quyết DNS (DNS resolvers) để sử dụng khi tra cứu các bản ghi TXT nhằm giải quyết các thử thách ACME DNS. Chấp nhận [địa chỉ mạng](/docs/conventions#network-addresses), mặc định là UDP và cổng 53 trừ khi được chỉ định. Nếu máy chủ là một địa chỉ IP, nó sẽ được kết nối trực tiếp để giải quyết máy chủ thượng nguồn. Nếu máy chủ không phải là địa chỉ IP, các địa chỉ sẽ được giải quyết bằng [quy ước phân giải tên](https://golang.org/pkg/net/#hdr-Name_Resolution) của thư viện tiêu chuẩn Go. Nếu nhiều trình giải quyết được chỉ định, một trình sẽ được chọn ngẫu nhiên.

- **challenges** thiết lập các loại thử thách được bật. Nếu không được đặt hoặc chỉ thị được sử dụng mà không có giá trị, thì tất cả các loại thử thách đều được bật. Các giá trị được chấp nhận là: http-01, tls-alpn-01, dns-01.

- **allow_wildcard_names** cho phép cấp chứng chỉ với SAN (Tên thay thế chủ thể) ký tự đại diện (wildcard).

- **allow**, **deny** cấu hình chính sách hoạt động của `acme_server`. Việc đánh giá chính sách tuân theo các tiêu chí được mô tả bởi Step-CA [tại đây](https://smallstep.com/docs/step-ca/policies/#policy-evaluation).

	- **domains** thiết lập các tên miền chủ thể được phép hoặc bị từ chối theo tiêu chí đánh giá chính sách.

	- **ip_ranges** thiết lập các dải IP chủ thể được phép hoặc bị từ chối theo tiêu chí đánh giá chính sách.

<a id="examples"></a>
## Ví dụ

Để phục vụ một máy chủ ACME với ID `home` trên tên miền `acme.example.com`, với CA được tùy chỉnh thông qua [tùy chọn toàn cục `pki`](/docs/caddyfile/options#pki-options), và cấp chứng chỉ riêng của nó bằng trình phát hành `internal`:

```caddy
{
	pki {
		ca home {
			name "My Home CA"
		}
	}
}

acme.example.com {
	tls {
		issuer internal {
			ca home
		}
	}
	acme_server {
		ca home
	}
}
```

Nếu bạn có một máy chủ Caddy khác, nó có thể sử dụng máy chủ ACME ở trên để cấp chứng chỉ cho chính nó:

```caddy
{
	acme_ca https://acme.example.com/acme/home/directory
	acme_ca_root /path/to/home_ca_root.crt
}

example.com {
	respond "Hello, world!"
}
```
