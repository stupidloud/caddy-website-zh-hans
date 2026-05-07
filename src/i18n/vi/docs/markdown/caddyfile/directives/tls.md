---
title: tls (Chỉ thị Caddyfile)
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# tls

Cấu hình TLS cho trang web.

**Các cài đặt TLS mặc định của Caddy rất an toàn. Chỉ thay đổi các cài đặt này nếu bạn có lý do chính đáng và hiểu rõ các hệ quả.** Cách sử dụng phổ biến nhất của chỉ thị này là chỉ định địa chỉ email tài khoản ACME, thay đổi điểm cuối ACME CA hoặc cung cấp chứng chỉ của riêng bạn.

Ghi chú về tính tương thích: Do tính chất nhạy cảm như một giao thức bảo mật, các điều chỉnh có chủ đích đối với các giá trị mặc định của TLS có thể được thực hiện trong các bản phát hành phụ hoặc bản sửa lỗi mới. Các phiên bản TLS cũ hoặc bị lỗi, mã hóa, tính năng, v.v. có thể bị loại bỏ bất cứ lúc nào. Nếu việc triển khai của bạn cực kỳ nhạy cảm với các thay đổi, bạn nên chỉ định rõ ràng các giá trị phải giữ nguyên hằng số và cảnh giác với các bản nâng cấp. Trong hầu hết các trường hợp, chúng tôi khuyên bạn nên sử dụng các cài đặt mặc định.


<a id="syntax"></a>
## Cú pháp (Syntax)

```caddy-d
tls [internal|force_automate|<email>] | [<cert_file> <key_file>] {
	protocols <min> [<max>]
	ciphers   <cipher_suites...>
	curves    <groups...>
	alpn      <values...>
	load      <paths...>
	ca        <ca_dir_url>
	ca_root   <pem_file>
	key_type  ed25519|p256|p384|rsa2048|rsa4096
	dns       <provider_name> [<params...>]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	eab       <key_id> <mac_key>
	on_demand
	reuse_private_keys
	client_auth {
		mode                   [request|require|verify_if_given|require_and_verify]
		trust_pool             <module>
		verifier 			   <module>
	}
	issuer          <issuer_name>  [<params...>]
	get_certificate <manager_name> [<params...>]
	insecure_secrets_log <log_file>
	renewal_window_ratio <ratio>
	force_automate
}
```

- **internal** có nghĩa là sử dụng CA nội bộ, được tin cậy cục bộ của Caddy để tạo chứng chỉ cho trang web này. Để cấu hình thêm cho nhà phát hành [`internal`](#internal), hãy sử dụng chỉ thị con [`issuer`](#issuer).

- **force_automate** buộc Caddy tự động hóa chứng chỉ cho trang web, ngay cả khi các chứng chỉ được quản lý khác được áp dụng.

- **&lt;email&gt;** là địa chỉ email được sử dụng cho tài khoản ACME quản lý các chứng chỉ của trang web. Bạn có thể muốn sử dụng [tùy chọn toàn cục `email`](/docs/caddyfile/options#email) để thay thế, nhằm cấu hình điều này cho tất cả các trang web của bạn cùng một lúc.

<aside class="tip">

Lưu ý rằng Let's Encrypt có thể gửi cho bạn email về việc chứng chỉ của bạn sắp hết hạn, nhưng điều này có thể gây nhầm lẫn vì Caddy có thể đã chọn sử dụng một nhà phát hành khác (ví dụ: ZeroSSL) khi gia hạn. Hãy kiểm tra nhật ký của bạn và/hoặc chính chứng chỉ đó (ví dụ: trong trình duyệt của bạn) để xem nhà phát hành nào đã được sử dụng và ngày hết hạn của nó vẫn còn hiệu lực; nếu vậy, bạn có thể bỏ qua email từ Let's Encrypt một cách an toàn.

</aside>

- **&lt;cert_file&gt;** và **&lt;key_file&gt;** là các đường dẫn đến các tệp PEM chứng chỉ và khóa riêng. Việc chỉ chỉ định một trong hai là không hợp lệ.

- **protocols** <span id="protocols"/> chỉ định các phiên bản giao thức tối thiểu và tối đa. KHÔNG thay đổi các giá trị này trừ khi bạn biết mình đang làm gì. Việc cấu hình này hiếm khi cần thiết, vì Caddy sẽ luôn sử dụng các mặc định hiện đại.
  
  Mặc định tối thiểu (min): `tls1.2`, Mặc định tối đa (max): `tls1.3`

- **ciphers** <span id="ciphers"/> chỉ định danh sách các tên bộ mã hóa (cipher suite) theo thứ tự ưu tiên giảm dần. KHÔNG thay đổi các giá trị này trừ khi bạn biết mình đang làm gì. Lưu ý rằng các bộ mã hóa không thể tùy chỉnh cho TLS 1.3; và không phải tất cả các bộ mã hóa TLS 1.2 đều được bật theo mặc định. Các tên được hỗ trợ là (theo thứ tự ưu tiên của thư viện chuẩn Go):
	- `TLS_AES_128_GCM_SHA256`
	- `TLS_CHACHA20_POLY1305_SHA256`
	- `TLS_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA`

- **curves** <span id="curves"/> chỉ định danh sách các nhóm EC để hỗ trợ. Khuyên bạn không nên thay đổi các giá trị mặc định. Các giá trị được hỗ trợ là:
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> là danh sách các giá trị để quảng bá trong [phần mở rộng ALPN <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Glossary/ALPN) của quá trình bắt tay TLS.

- **load** <span id="load"/> chỉ định danh sách các thư mục để tải các tệp PEM là các gói chứng chỉ+khóa.

- **ca** <span id="ca"/> thay đổi điểm cuối ACME CA. Điều này thường được sử dụng nhất để thiết lập [điểm cuối thử nghiệm (staging) của Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) khi kiểm tra, hoặc một máy chủ ACME nội bộ. (Để thay đổi giá trị này cho toàn bộ Caddyfile, hãy sử dụng [tùy chọn toàn cục](/docs/caddyfile/options) `acme_ca` để thay thế.)

- **ca_root** <span id="ca_root"/> chỉ định một tệp PEM chứa chứng chỉ gốc (root certificate) đáng tin cậy cho điểm cuối ACME CA, nếu không có trong kho lưu trữ tin cậy của hệ thống.

- **key_type** <span id="key_type"/> là loại khóa được sử dụng khi tạo CSR. Chỉ thiết lập điều này nếu bạn có yêu cầu cụ thể.

- **dns** <span id="dns"/> bật [thử thách DNS (DNS challenge)](/docs/automatic-https#dns-challenge) bằng cách sử dụng plugin nhà cung cấp được chỉ định, plugin này phải được cắm từ một trong các kho lưu trữ [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Mỗi plugin nhà cung cấp có thể có cú pháp riêng theo sau tên của chúng; hãy tham khảo tài liệu của chúng để biết chi tiết. Việc duy trì hỗ trợ cho từng nhà cung cấp DNS là một nỗ lực của cộng đồng. [Tìm hiểu cách bật thử thách DNS cho nhà cung cấp của bạn tại wiki của chúng tôi.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập thời gian tối đa để chờ các bản ghi DNS TXT xuất hiện khi sử dụng thử thách DNS. Đặt thành `-1` để tắt kiểm tra lan truyền. Mặc định là 2 phút.

- **propagation_delay** <span id="propagation_delay"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập thời gian chờ trước khi bắt đầu kiểm tra lan truyền bản ghi DNS TXT khi sử dụng thử thách DNS. Mặc định là `0` (không chờ).

- **dns_ttl** <span id="dns_ttl"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập TTL của bản ghi `TXT` được sử dụng cho thử thách DNS. Hiếm khi cần thiết.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> ghi đè tên miền sẽ sử dụng cho thử thách DNS. Điều này dùng để ủy quyền thử thách cho một tên miền khác.

  Bạn có thể muốn sử dụng điều này nếu nhà cung cấp DNS của tên miền chính của bạn không có sẵn [plugin DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Thay vào đó, bạn có thể thêm bản ghi `CNAME` với tên miền phụ `_acme-challenge` vào tên miền chính của mình, trỏ đến một tên miền phụ mà bạn _có_ plugin. Tùy chọn này _không yêu cầu_ sự hỗ trợ đặc biệt từ plugin.
  
  Khi các nhà phát hành ACME cố gắng giải quyết thử thách DNS cho tên miền chính của bạn, họ sẽ đi theo `CNAME` đến tên miền phụ của bạn để tìm bản ghi `TXT`.

  **Lưu ý:** Sử dụng tên chuẩn đầy đủ từ bản ghi CNAME làm giá trị ở đây - tên miền phụ `_acme-challenge` sẽ không được thêm tự động phía trước.

- **resolvers** <span id="resolvers"/> tùy chỉnh các trình phân giải DNS (DNS resolvers) được sử dụng khi thực hiện thử thách DNS; các trình phân giải này được ưu tiên hơn các trình phân giải hệ thống hoặc bất kỳ trình phân giải mặc định nào. Nếu được đặt ở đây, các trình phân giải sẽ lan truyền đến tất cả các nhà phát hành chứng chỉ được cấu hình.

  Đây thường là một danh sách các địa chỉ IP. Ví dụ, để sử dụng [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns):

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> cấu hình liên kết tài khoản bên ngoài ACME (EAB) cho trang web này, sử dụng ID khóa và khóa MAC được cung cấp bởi CA của bạn.

- **on_demand** <span id="on_demand"/> bật [TLS theo yêu cầu (On-Demand TLS)](/docs/automatic-https#on-demand-tls) cho các tên máy chủ (hostname) được đưa ra trong (các) địa chỉ của khối trang web. **Cảnh báo bảo mật:** Việc làm này trong môi trường production là không an toàn trừ khi bạn cũng cấu hình [tùy chọn toàn cục `on_demand_tls`](/docs/caddyfile/options#on-demand-tls) để giảm thiểu sự lạm dụng.

- **reuse_private_keys** <span id="reuse_private_keys"/> cho phép sử dụng lại các khóa riêng khi gia hạn chứng chỉ. Theo mặc định, một khóa mới được tạo cho mỗi chứng chỉ mới để giảm thiểu việc ghim khóa (pinning) và giảm phạm vi xâm phạm khóa. Việc ghim khóa đi ngược lại với các phương pháp hay nhất trong ngành. Tùy chọn này không được khuyến khích trừ khi bạn có lý do cụ thể để sử dụng nó; điều này có thể bị loại bỏ trong phiên bản tương lai.

- **client_auth** <span id="client_auth"/> bật và cấu hình xác thực máy khách TLS:
  - **mode** <span id="mode"/> là chế độ để xác thực máy khách. Các giá trị được phép là:

    | Chế độ (Mode) | Mô tả |
    | --- | --- |
    | request | Yêu cầu khách hàng cung cấp chứng chỉ, nhưng vẫn cho phép ngay cả khi không có; không xác minh nó |
    | require | Yêu cầu khách hàng trình bày chứng chỉ, nhưng không xác minh nó |
    | verify_if_given | Yêu cầu khách hàng cung cấp chứng chỉ; cho phép ngay cả khi không có, nhưng xác minh nó nếu có |
    | require_and_verify | Yêu cầu khách hàng trình bày một chứng chỉ hợp lệ đã được xác minh |

    Mặc định: `require_and_verify` nếu mô-đun `trust_pool` được cung cấp; ngược lại là `require`.
	
  - **trust_pool** <span id="trust_pool"/> cấu hình nguồn của các cơ quan cấp chứng chỉ (CA) cung cấp các chứng chỉ dùng để xác thực chứng chỉ khách hàng.
	
	Cơ quan cấp chứng chỉ được sử dụng cung cấp nhóm các chứng chỉ đáng tin cậy và cấu hình trong phân đoạn này phụ thuộc vào mô-đun nguồn của nhóm tin cậy được cấu hình. Các mô-đun tiêu chuẩn có sẵn trong Caddy được [liệt kê bên dưới](#trust-pool-providers). Danh sách đầy đủ các mô-đun, bao gồm cả bên thứ 3, được liệt kê trong [tài liệu JSON `trust_pool`](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool).

    Nhiều chỉ thị `trusted_*` có thể được sử dụng để chỉ định nhiều CA hoặc chứng chỉ lá (leaf certificate). Các chứng chỉ khách hàng không được liệt kê là một trong các chứng chỉ lá hoặc không được ký bởi bất kỳ CA nào được chỉ định sẽ bị từ chối tùy theo **chế độ (mode)**.

  - **verifier** <span id="verifier"/> cho phép sử dụng mô-đun trình xác minh chứng chỉ máy khách tùy chỉnh. Các mô-đun này có thể thực hiện các kiểm tra xác thực máy khách tùy chỉnh, chẳng hạn như đảm bảo chứng chỉ không bị thu hồi.

- **issuer** <span id="issuer"/> cấu hình một nhà phát hành chứng chỉ tùy chỉnh, hoặc một nguồn để lấy chứng chỉ.

  Nhà phát hành nào được sử dụng và các tùy chọn theo sau trong phân đoạn này phụ thuộc vào các [mô-đun nhà phát hành](#issuers) có sẵn. Một số chỉ thị con khác như `ca` và `dns` thực chất là các phím tắt để cấu hình nhà phát hành `acme` (và chỉ thị con này đã được thêm vào sau), vì vậy việc chỉ định chỉ thị này cùng với một số chỉ thị khác gây nhầm lẫn và do đó bị cấm.
  
  Chỉ thị con này có thể được chỉ định nhiều lần để cấu hình nhiều nhà phát hành dự phòng; nếu một nhà phát hành không cấp được chứng chỉ, nhà phát hành tiếp theo sẽ được thử.

- **get_certificate** <span id="get_certificate"/> cho phép lấy chứng chỉ từ một [mô-đun trình quản lý](#certificate-managers) tại thời điểm bắt tay.

- **insecure_secrets_log** <span id="insecure_secrets_log"/> cho phép ghi lại các bí mật TLS vào một tệp. Điều này còn được gọi là `SSLKEYLOGFILE`. Sử dụng định dạng nhật ký khóa NSS, định dạng này sau đó có thể được phân tích bởi Wireshark hoặc các công cụ khác. ⚠️ **Cảnh báo bảo mật:** Việc này không an toàn vì nó cho phép các chương trình hoặc công cụ khác giải mã các kết nối TLS, và do đó làm ảnh hưởng hoàn toàn đến bảo mật. Tuy nhiên, khả năng này có thể hữu ích cho việc gỡ lỗi và khắc phục sự cố.

- **renewal_window_ratio** <span id="renewal_window_ratio"/> là một tỷ lệ giữa 0 và 1 xác định thời gian sống của chứng chỉ phải còn lại trước khi Caddy cố gắng gia hạn chứng chỉ. Ví dụ, nếu một chứng chỉ có thời gian sống là 90 ngày và tỷ lệ này là `0.3333` (giá trị mặc định), thì Caddy sẽ liên tục cố gắng gia hạn chứng chỉ khi nó còn lại 30 ngày hoặc ít hơn trước khi hết hạn. Cũng có thể được thiết lập toàn cục với [tùy chọn toàn cục `renewal_window_ratio`](/docs/caddyfile/options#renewal_window_ratio).

  Bạn hiếm khi cần phải thay đổi điều này, nhưng nó có thể hữu ích để gia hạn muộn hơn trong thời gian sống của chứng chỉ nếu CA của bạn có thời gian cấp rất dài.

  Lưu ý rằng đây là một gợi ý vì các nhà phát hành ACME có thể triển khai [phần mở rộng ARI](https://datatracker.ietf.org/doc/rfc9773/). ARI chỉ định một khoảng thời gian mà trong đó khách hàng ACME (trong trường hợp này là Caddy) nên cố gắng gia hạn, và khoảng thời gian đó có thể không phù hợp với tỷ lệ này.

- **force_automate** giống như việc chỉ định nội dòng (xem ở trên).

<a id="trust-pool-providers"></a>
### Nhà cung cấp nhóm tin cậy (Trust Pool Providers)

Đây là các nhà cung cấp nhóm tin cậy tiêu chuẩn có thể được sử dụng trong chỉ thị con `trust_pool`:

#### inline

Mô-đun `inline` phân tích các chứng chỉ gốc đáng tin cậy như được liệt kê trực tiếp trong Caddyfile ở định dạng DER-encoded base64. Chỉ thị `trust_der` có thể được lặp lại nhiều lần.

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> là chứng chỉ CA được mã hóa DER base64 dùng để xác thực chứng chỉ khách hàng.

#### file

Mô-đun `file` đọc các chứng chỉ gốc đáng tin cậy từ các tệp PEM trên đĩa. Chỉ thị `pem_file` có thể chấp nhận nhiều đường dẫn tệp trên cùng một dòng và có thể được lặp lại nhiều lần.

```caddy-d
... file [<pem_file>...] {
	pem_file <pem_file>...
}
```

- **pem_file** <span id="pem_file"/> là đường dẫn đến tệp chứng chỉ CA PEM dùng để xác thực chứng chỉ khách hàng.

#### pki_root

Mô-đun `pki_root` lấy chứng chỉ _root_ và các chứng chỉ tin cậy từ cơ quan cấp chứng chỉ được định nghĩa trong [ứng dụng PKI](/docs/caddyfile/options#pki-options). Chỉ thị `authority` có thể chấp nhận nhiều cơ quan cùng một lúc và có thể được lặp lại nhiều lần.

```caddy-d
... pki_root [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> là tên của cơ quan cấp chứng chỉ được cấu hình trong ứng dụng PKI.

#### pki_intermediate

Mô-đun `pki_intermediate` lấy chứng chỉ _trung gian (intermediate)_ và các chứng chỉ tin cậy từ cơ quan cấp chứng chỉ được định nghĩa trong [ứng dụng PKI](/docs/caddyfile/options#pki-options). Chỉ thị `authority` có thể chấp nhận nhiều cơ quan cùng một lúc và có thể được lặp lại nhiều lần.

```caddy-d
... pki_intermediate [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> là tên của cơ quan cấp chứng chỉ được cấu hình trong ứng dụng PKI.

#### storage

Mô-đun `storage` trích xuất gốc chứng chỉ đáng tin cậy từ [kho lưu trữ (storage)](/docs/caddyfile/options#storage) của Caddy. Chỉ thị `authority` có thể chấp nhận nhiều cơ quan cùng một lúc và có thể được lặp lại nhiều lần.

```caddy-d
... storage [<storage_keys>...] {
	storage <storage_module>
	keys    <storage_keys>...
}
```

- **storage** <span id="storage"/> là một mô-đun lưu trữ tùy chọn để sử dụng. Nếu không được chỉ định, mô-đun lưu trữ mặc định sẽ được sử dụng. Nếu được chỉ định, nó chỉ có thể được chỉ định một lần.

- **keys** <span id="keys"/> là danh sách các khóa lưu trữ mà tại đó các tệp PEM của chứng chỉ được lưu trữ. Chỉ thị này chấp nhận nhiều giá trị trên cùng một dòng và có thể được chỉ định nhiều lần.

#### http

Mô-đun `http` lấy các chứng chỉ đáng tin cậy từ các điểm cuối HTTP. Chỉ thị `endpoints` có thể chấp nhận nhiều điểm cuối cùng một lúc và có thể được lặp lại nhiều lần.

```caddy-d
... http [<endpoints...>] {
	endpoints   <endpoints...>
	tls         <tls_config>
}
```

- **endpoints** <span id="endpoints"/> là danh sách các điểm cuối HTTP để lấy chứng chỉ. Chỉ thị này chấp nhận nhiều giá trị trên cùng một dòng và có thể được chỉ định nhiều lần.

- **tls** <span id="tls"/> là cấu hình TLS tùy chọn để sử dụng khi kết nối với điểm cuối HTTP. Việc phân tích phân đoạn này được định nghĩa trong [phần tiếp theo](#tls-1).

##### TLS

```caddy-d
... {
	ca                    <ca_module>
	insecure_skip_verify
	handshake_timeout     <duration>
	server_name           <name>
	renegotiation         <never|once|freely>
}
```

- **ca** <span id="ca"/> là một chỉ thị tùy chọn để xác định nhà cung cấp nhóm tin cậy. Cấu hình tuân theo hành vi tương tự như [`trust_pool`](#trust_pool). Nếu được chỉ định, nó chỉ có thể được chỉ định một lần.

- **insecure_skip_verify** <span id="insecure_skip_verify"/> tắt xác minh bắt tay TLS, làm cho kết nối không an toàn và dễ bị tấn công man-in-the-middle. _Không sử dụng trong production._ Việc xác minh được thực hiện dựa trên các cơ quan cấp chứng chỉ được hệ thống tin cậy hoặc được xác định bởi chỉ thị [`ca`](#ca).

- **handshake_timeout** <span id="handshake_timeout"/> là [thời lượng](/docs/conventions#durations) tối đa để chờ quá trình bắt tay TLS hoàn tất. Mặc định: Không có thời gian chờ (No timeout).

- **server_name** <span id="server_name"/> thiết lập tên máy chủ được sử dụng khi xác minh chứng chỉ nhận được trong quá trình bắt tay TLS. Theo mặc định, điều này sẽ sử dụng phần host của địa chỉ upstream.

- **renegotiation** <span id="renegotiation"/> thiết lập mức độ tái đàm phán TLS. Tái đàm phán TLS là hành động thực hiện các quá trình bắt tay tiếp theo sau lần đầu tiên. Mức độ có thể là một trong số:
  - `never` (mặc định) vô hiệu hóa tái đàm phán.
  - `once` cho phép một máy chủ từ xa yêu cầu tái đàm phán một lần cho mỗi kết nối.
  - `freely` cho phép một máy chủ từ xa liên tục yêu cầu tái đàm phán.

<a id="verifiers"></a>
### Trình xác minh (Verifiers)

Các mô-đun trình xác minh chứng chỉ máy khách được thực hiện sau khi xác thực rằng chúng được cấp từ một cơ quan cấp chứng chỉ đáng tin cậy, nếu `trust_pool` được cấu hình. Trình xác minh duy nhất hiện được đi kèm trong Caddy tiêu chuẩn là `leaf`.

#### Leaf

Trình xác minh `leaf` kiểm tra xem chứng chỉ máy khách có phải là một trong một tập hợp các chứng chỉ được phép đã được định nghĩa hay không. Tập hợp chứng chỉ được tải bằng các mô-đun [loader](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders).

<a id="loaders"></a>
##### Trình tải (Loaders)

Bản phân phối Caddy tiêu chuẩn đi kèm với 4 trình tải, 3 trong số đó có sẵn trong Caddyfile.

###### File

Trình tải `file` tải tập hợp các chứng chỉ từ các tệp PEM được chỉ định.

```caddy-d
... file <pem_files...>
```

###### Folder

Trình tải `folder` duyệt đệ quy các thư mục được đặt tên để tìm kiếm các tệp PEM sẽ được tải làm chứng chỉ máy khách được chấp nhận.

```caddy-d
... folder <folders...>
```

###### PEM

Trình tải `pem` chấp nhận các chứng chỉ được đưa nội dòng vào Caddyfile ở định dạng PEM.

```caddy-d
... pem <pem_strings...>
```

<a id="issuers"></a>
### Nhà phát hành (Issuers)

Các nhà phát hành này đi kèm tiêu chuẩn với chỉ thị `tls`:

#### acme

Lấy chứng chỉ bằng giao thức ACME. Lưu ý rằng `acme` là nhà phát hành mặc định (sử dụng Let's Encrypt), vì vậy việc cấu hình nó một cách rõ ràng thường là không cần thiết.

```caddy-d
... acme [<directory_url>] {
	dir      <directory_url>
	test_dir <test_directory_url>
	email    <email>
	timeout  <duration>
	disable_http_challenge
	disable_tlsalpn_challenge
	alt_http_port    <port>
	alt_tlsalpn_port <port>
	eab <key_id> <mac_key>
	trusted_roots <pem_files...>
	dns [<provider_name> [<options>]]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}
	profile <name>
}
```

- **dir** <span id="dir"/> là URL dẫn đến thư mục của ACME CA.
  
  Mặc định: `https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> là thư mục dự phòng tùy chọn để sử dụng khi thử lại các thử thách; nếu tất cả các thử thách thất bại, điểm cuối này sẽ được sử dụng trong quá trình thử lại; hữu ích nếu một CA có điểm cuối thử nghiệm (staging) mà bạn muốn tránh giới hạn tốc độ trên điểm cuối production của họ.

  Mặc định: `https://acme-staging-v02.api.letsencrypt.org/directory`

- **email** <span id="email"/> là địa chỉ email liên hệ của tài khoản ACME.

- **timeout** <span id="timeout"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập thời gian chờ trước khi hết thời gian thực hiện một thao tác ACME.

- **disable_http_challenge** <span id="disable_http_challenge"/> sẽ vô hiệu hóa thử thách HTTP.

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> sẽ vô hiệu hóa thử thách TLS-ALPN.

- **alt_http_port** <span id="alt_http_port"/> là một cổng thay thế để phục vụ thử thách HTTP; nó phải diễn ra trên cổng 80 nên bạn phải chuyển tiếp các gói tin đến cổng thay thế này.

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> là một cổng thay thế để phục vụ thử thách TLS-ALPN; nó phải diễn ra trên cổng 443 nên bạn phải chuyển tiếp các gói tin đến cổng thay thế này.

- **eab** <span id="eab"/> chỉ định một Liên kết Tài khoản Bên ngoài (External Account Binding) có thể được yêu cầu với một số ACME CA.

- **trusted_roots** <span id="trusted_roots"/> là một hoặc nhiều chứng chỉ gốc (dưới dạng tên tệp PEM) để tin cậy khi kết nối với máy chủ ACME CA.

- **dns** <span id="dns"/> cấu hình thử thách DNS. Một nhà cung cấp phải được cấu hình ở đây, trừ khi [tùy chọn toàn cục `dns`](/docs/caddyfile/options#dns) chỉ định một mô-đun nhà cung cấp DNS áp dụng toàn cục.

- **propagation_timeout** <span id="propagation_timeout"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập thời gian tối đa để chờ các bản ghi DNS TXT xuất hiện khi sử dụng thử thách DNS. Đặt thành `-1` để tắt kiểm tra lan truyền. Mặc định là 2 phút.

- **propagation_delay** <span id="propagation_delay"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập thời gian chờ trước khi bắt đầu kiểm tra lan truyền bản ghi DNS TXT khi sử dụng thử thách DNS. Mặc định là 0 (không chờ).

- **dns_ttl** <span id="dns_ttl"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập TTL của bản ghi `TXT` được sử dụng cho thử thách DNS. Hiếm khi cần thiết.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> ghi đè tên miền sẽ sử dụng cho thử thách DNS. Điều này dùng để ủy quyền thử thách cho một tên miền khác.

  Bạn có thể muốn sử dụng điều này nếu nhà cung cấp DNS của tên miền chính của bạn không có sẵn [plugin DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Thay vào đó, bạn có thể thêm bản ghi `CNAME` với tên miền phụ `_acme-challenge` vào tên miền chính của mình, trỏ đến một tên miền phụ mà bạn _có_ plugin. Tùy chọn này _không yêu cầu_ sự hỗ trợ đặc biệt từ plugin.
  
  Khi các nhà phát hành ACME cố gắng giải quyết thử thách DNS cho tên miền chính của bạn, họ sẽ đi theo `CNAME` đến tên miền phụ của bạn để tìm bản ghi `TXT`.

  **Lưu ý:** Sử dụng tên chuẩn đầy đủ từ bản ghi CNAME làm giá trị ở đây - tên miền phụ `_acme-challenge` sẽ không được thêm tự động phía trước.

- **resolvers** <span id="resolvers"/> tùy chỉnh các trình phân giải DNS được sử dụng khi thực hiện thử thách DNS; các trình phân giải này được ưu tiên hơn các trình phân giải hệ thống hoặc bất kỳ trình phân giải mặc định nào. Nếu được đặt ở đây, các trình phân giải sẽ lan truyền đến tất cả các nhà phát hành chứng chỉ được cấu hình.

  Đây thường là một danh sách các địa chỉ IP. Ví dụ, để sử dụng [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns):

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> chỉ định chuỗi chứng chỉ nào Caddy nên ưu tiên; hữu ích nếu CA của bạn cung cấp nhiều chuỗi. Sử dụng một trong các tùy chọn sau:
	- **smallest** <span id="smallest"/> sẽ yêu cầu Caddy ưu tiên các chuỗi có ít byte nhất.

	- **root_common_name** <span id="root_common_name"/> là một danh sách gồm một hoặc nhiều tên phổ biến (common name); Caddy sẽ chọn chuỗi đầu tiên có chứng chỉ gốc khớp với ít nhất một trong các tên phổ biến được chỉ định.

	- **any_common_name** <span id="any_common_name"/> là một danh sách gồm một hoặc nhiều tên phổ biến; Caddy will sẽ chọn chuỗi đầu tiên có nhà phát hành khớp với ít nhất một trong các tên phổ biến được chỉ định.

- **profile** là tên của [hồ sơ ACME (ACME profile)](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/) sẽ áp dụng khi đặt hàng chứng chỉ. Nếu bạn chỉ định một hồ sơ, tất cả các CA được cấu hình (ngầm định hoặc cách khác) phải hỗ trợ hồ sơ này. Tham khảo tài liệu của CA của bạn để biết các hồ sơ có sẵn; một số CA có thể không hỗ trợ hồ sơ. THỬ NGHIỆM (EXPERIMENTAL): Đặc tả hồ sơ ACME vẫn đang ở trạng thái bản thảo, vì vậy tính năng/chức năng này có thể bị thay đổi hoặc loại bỏ.


#### zerossl

Lấy chứng chỉ bằng [API cấp chứng chỉ độc quyền của ZeroSSL](https://zerossl.com/documentation/api/). Cần có khóa API và cũng có thể yêu cầu thanh toán tùy thuộc vào gói của bạn. Lưu ý rằng vấn đề này khác với [điểm cuối ACME của ZeroSSL](https://zerossl.com/documentation/acme/). Để sử dụng điểm cuối ACME của ZeroSSL, hãy sử dụng nhà phát hành `acme` được mô tả ở trên được cấu hình với điểm cuối thư mục ACME của ZeroSSL.

```caddy-d
... zerossl <api_key> {
	validity_days <days>
	alt_http_port <port>
	dns <provider_name> ...
	propagation_delay <duration>
	propagation_timeout <duration>
	resolvers <list...>
	dns_ttl <duration>
}
```

- **validity_days** <span id="validity_days"/> xác định thời gian sống của chứng chỉ. Chỉ một số giá trị nhất định được chấp nhận; xem [tài liệu của ZeroSSL](https://zerossl.com/documentation/api/create-certificate/) để biết chi tiết.
<!--   
  Default: `https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> là cổng được sử dụng để hoàn tất việc xác thực HTTP của ZeroSSL, nếu không phải là cổng 80.
- **dns** <span id="zerossl_dns"/> bật phương pháp xác thực CNAME bằng cách sử dụng nhà cung cấp DNS được đặt tên với cấu hình đã cho để cung cấp bản ghi tự động. Plugin nhà cung cấp DNS phải được cài đặt từ các kho lưu trữ [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Mỗi plugin nhà cung cấp có thể có cú pháp riêng theo sau tên của chúng; hãy tham khảo tài liệu của chúng để biết chi tiết. Việc duy trì hỗ trợ cho từng nhà cung cấp DNS là một nỗ lực của cộng đồng.
- **propagation_delay** <span id="zerossl_propagation_delay"/> là thời gian chờ trước khi kiểm tra lan truyền bản ghi CNAME.
- **propagation_timeout** <span id="zerossl_propagation_timeout"/> là thời gian chờ lan truyền bản ghi CNAME trước khi bỏ cuộc.
- **resolvers** <span id="zerossl_resolvers"/> xác định các trình phân giải DNS tùy chỉnh để sử dụng khi kiểm tra lan truyền bản ghi CNAME.
- **dns_ttl** <span id="zerossl_dns_ttl"/> cấu hình TTL cho các bản ghi CNAME được tạo như một phần của quá trình xác thực.



#### internal

Lấy chứng chỉ từ một cơ quan cấp chứng chỉ nội bộ.

```caddy-d
... internal {
	ca       <name>
	lifetime <duration>
	sign_with_root
}
```

- **ca** <span id="ca"/> là tên của CA nội bộ sẽ sử dụng. Mặc định: `local`. Xem [tùy chọn toàn cục ứng dụng PKI](/docs/caddyfile/options#pki-options) để cấu hình CA `local`, hoặc để tạo các CA thay thế.

  Theo mặc định, chứng chỉ root CA có thời gian sống `3600d` (10 năm) và trung gian (intermediate) có thời gian sống `7d` (7 ngày).

  Caddy sẽ cố gắng cài đặt chứng chỉ root CA vào kho lưu trữ tin cậy của hệ thống, nhưng việc này có thể thất bại khi Caddy chạy dưới quyền người dùng không có đặc quyền, hoặc khi chạy trong container Docker. Trong trường hợp đó, chứng chỉ root CA sẽ cần được cài đặt thủ công, bằng cách sử dụng lệnh [`caddy trust`](/docs/command-line#caddy-trust), hoặc bằng cách [sao chép ra khỏi container](/docs/running#usage).

- **lifetime** <span id="lifetime"/> là một [giá trị thời lượng](/docs/conventions#durations) thiết lập thời hạn hiệu lực cho các chứng chỉ lá được cấp nội bộ. Mặc định: `12h`. KHÔNG nên thay đổi giá trị này, trừ khi thực sự cần thiết. Nó phải ngắn hơn thời gian sống của chứng chỉ trung gian.

- **sign_with_root** <span id="sign_with_root"/> buộc root là nhà phát hành thay vì trung gian. Điều này KHÔNG được khuyến khích và chỉ nên được sử dụng khi các thiết bị/khách hàng không xác thực chuỗi chứng chỉ một cách chính xác (rất hiếm khi xảy ra).



<a id="certificate-managers"></a>
### Trình quản lý chứng chỉ (Certificate Managers)

Các mô-đun trình quản lý chứng chỉ khác với các mô-đun nhà phát hành ở chỗ việc sử dụng các mô-đun trình quản lý ngụ ý rằng một công cụ hoặc dịch vụ bên ngoài đang duy trì việc gia hạn chứng chỉ, trong khi một mô-đun nhà phát hành ngụ ý rằng chính Caddy đang quản lý chứng chỉ. (Các mô-đun nhà phát hành lấy Yêu cầu ký chứng chỉ (CSR) làm đầu vào, nhưng các mô-đun trình quản lý chứng chỉ lấy TLS ClientHello làm đầu vào.)

Các mô-đun trình quản lý này đi kèm tiêu chuẩn với chỉ thị `tls`:

#### tailscale

Lấy chứng chỉ từ một phiên bản [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) đang chạy cục bộ. [HTTPS phải được bật trong tài khoản Tailscale của bạn](https://tailscale.com/kb/1153/enabling-https/) (hoặc máy chủ [Headscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/juanfont/headscale) mã nguồn mở của bạn); và tiến trình Caddy phải đang chạy dưới quyền root, hoặc bạn phải cấu hình `tailscaled` để cấp cho người dùng Caddy của bạn [quyền lấy chứng chỉ](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).

_**LƯU Ý: Điều này thường không cần thiết!** Caddy tự động sử dụng Tailscale cho tất cả các tên miền `*.ts.net` mà không cần thêm bất kỳ cấu hình nào._

```caddy-d
get_certificate tailscale  # thường không cần thiết!
```


#### http

Lấy chứng chỉ bằng cách thực hiện một yêu cầu HTTP(S). Phản hồi phải có mã trạng thái `200` và nội dung phải chứa một chuỗi PEM bao gồm chứng chỉ đầy đủ (với các trung gian) cũng như khóa riêng.

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> là URL đầy đủ để thực hiện yêu cầu. Khuyên bạn nên đặt đây là một điểm cuối cục bộ vì lý do hiệu suất. URL sẽ được tăng cường với các tham số chuữu truy vấn sau: 

  - `server_name`: giá trị SNI
  - `signature_schemes`: danh sách phân tách bằng dấu phẩy các ID thập lục phân của các thuật toán chữ ký
  - `cipher_suites`: danh sách phân tách bằng dấu phẩy các ID thập lục phân của các bộ mã hóa
  - `local_ip`: địa chỉ IP mà khách hàng đã thực hiện yêu cầu



<a id="examples"></a>
## Ví dụ (Examples)

Sử dụng chứng chỉ và khóa tùy chỉnh. Chứng chỉ nên có [SANs](https://en.wikipedia.org/wiki/Subject_Alternative_Name) khớp với địa chỉ trang web:

```caddy
example.com {
	tls cert.pem key.pem
}
```

Sử dụng chứng chỉ [được tin cậy cục bộ](/docs/automatic-https#local-https) cho tất cả các máy chủ trên khối trang web hiện tại, thay vì chứng chỉ công khai thông qua ACME / Let's Encrypt (hữu ích trong môi trường phát triển):

```caddy
example.com {
	tls internal
}
```

Sử dụng chứng chỉ được tin cậy cục bộ, nhưng được quản lý [Theo yêu cầu (On-Demand)](/docs/automatic-https#on-demand-tls) thay vì ở chế độ nền. Điều này cho phép bạn trỏ bất kỳ tên miền nào vào phiên bản Caddy của mình và nó sẽ tự động cấp chứng chỉ cho bạn. Điều này KHÔNG NÊN được sử dụng nếu phiên bản Caddy của bạn có thể truy cập công khai, vì kẻ tấn công có thể sử dụng nó để làm cạn kiệt tài nguyên máy chủ của bạn:

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

Chỉ định các tùy chọn tùy chỉnh cho CA nội bộ (không thể sử dụng phím tắt `tls internal`):

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

Chỉ định địa chỉ email cho tài khoản ACME của bạn (nhưng nếu chỉ có một email được sử dụng cho tất cả các trang web, chúng tôi khuyên bạn nên sử dụng [tùy chọn toàn cục](/docs/caddyfile/options) `email` để thay thế):

```caddy
example.com {
	tls your@email.com
}
```

Bật thử thách DNS cho một tên miền được quản lý trên Cloudflare với thông tin đăng nhập tài khoản trong một biến môi trường. Điều này mở khóa hỗ trợ chứng chỉ wildcard, yêu cầu xác thực DNS:

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

Lấy chuỗi chứng chỉ qua HTTP, thay vì để Caddy quản lý nó. Lưu ý rằng [`get_certificate`](#certificate-managers) ngụ ý rằng [`on_demand`](#on_demand) được bật, lấy chứng chỉ bằng một mô-đun thay vì kích hoạt việc cấp phát ACME:

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

Bật Xác thực máy khách TLS và yêu cầu máy khách trình bày một chứng chỉ hợp lệ đã được xác minh đối với tất cả các CA được cung cấp thông qua nhà cung cấp `file` của [`trust_pool`](#trust_pool):

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
