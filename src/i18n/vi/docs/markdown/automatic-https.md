---
title: "HTTPS Tự động"
---

<a id="automatic-https"></a>
# HTTPS Tự động

**Caddy là máy chủ web đầu tiên sử dụng HTTPS tự động _và theo mặc định_.**

HTTPS tự động cung cấp chứng chỉ TLS cho tất cả các trang web của bạn và giữ cho chúng được gia hạn. Nó cũng tự động chuyển hướng HTTP sang HTTPS cho bạn! Caddy sử dụng các thiết lập mặc định an toàn và hiện đại -- không cần thời gian dừng hoạt động, cấu hình bổ sung hoặc công cụ riêng biệt.

<aside class="tip">
	Caddy đã đổi mới công nghệ HTTPS tự động; chúng tôi đã thực hiện việc này kể từ ngày đầu tiên nó khả thi vào năm 2015. Logic tự động hóa HTTPS của Caddy là trưởng thành và mạnh mẽ nhất thế giới.
</aside>

Dưới đây là một video dài 28 giây cho thấy cách nó hoạt động:

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**Menu:**

- [Tổng quan](#overview)
- [Kích hoạt](#activation)
- [Ảnh hưởng](#effects)
- [Yêu cầu về tên máy chủ](#hostname-requirements)
- [HTTPS cục bộ](#local-https)
- [Thử nghiệm](#testing)
- [Thử thách ACME](#acme-challenges)
- [TLS theo yêu cầu (On-Demand TLS)](#on-demand-tls)
- [Lỗi](#errors)
- [Lưu trữ](#storage)
- [Chứng chỉ Wildcard](#wildcard-certificates)
- [ClientHello được mã hóa (ECH)](#encrypted-clienthello-ech)



<a id="overview"></a>
## Tổng quan

**Theo mặc định, Caddy phục vụ tất cả các trang web qua HTTPS.**

- Caddy phục vụ các địa chỉ IP và tên máy chủ cục bộ/nội bộ qua HTTPS bằng cách sử dụng các chứng chỉ tự ký được tự động tin cậy cục bộ (nếu được phép).
	- Ví dụ: `localhost`, `127.0.0.1`
- Caddy phục vụ các tên DNS công khai qua HTTPS bằng cách sử dụng chứng chỉ từ một CA ACME công khai như [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) hoặc [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com).
	- Ví dụ: `example.com`, `sub.example.com`, `*.example.com`

Caddy giữ cho tất cả các chứng chỉ được quản lý được gia hạn và tự động chuyển hướng HTTP (cổng mặc định `80`) sang HTTPS (cổng mặc định `443`).

**Đối với HTTPS cục bộ:**

- Caddy có thể yêu cầu mật khẩu để cài đặt chứng chỉ gốc (root certificate) duy nhất của nó vào kho lưu trữ tin cậy của bạn. Việc này chỉ xảy ra một lần cho mỗi gốc; và bạn có thể xóa nó bất cứ lúc nào.
- Bất kỳ ứng dụng khách nào truy cập trang web mà không tin cậy chứng chỉ CA gốc của Caddy sẽ hiển thị lỗi bảo mật.

**Đối với tên miền công khai:**

<aside class="tip">

Đây là các yêu cầu chung cho bất kỳ trang web sản xuất cơ bản nào, không chỉ riêng Caddy. Sự khác biệt chính là thiết lập các bản ghi DNS của bạn một cách chính xác **trước khi** chạy Caddy để nó có thể cung cấp chứng chỉ.

</aside>


- Nếu các bản ghi A/AAAA của tên miền trỏ đến máy chủ của bạn,
- các cổng `80` và `443` được mở ra bên ngoài,
- Caddy có thể liên kết với các cổng đó (_hoặc_ các cổng đó được chuyển tiếp đến Caddy),
- [thư mục dữ liệu](/docs/conventions#data-directory) của bạn có thể ghi và bền vững,
- và tên miền của bạn xuất hiện ở đâu đó có liên quan trong cấu hình,

thì các trang web sẽ được phục vụ qua HTTPS một cách tự động. Bạn sẽ không phải làm gì khác về việc đó. Nó chỉ đơn giản là hoạt động!

Vì HTTPS sử dụng cơ sở hạ tầng công cộng, dùng chung, bạn với tư cách là quản trị viên máy chủ nên hiểu phần còn lại của thông tin trên trang này để có thể tránh các vấn đề không cần thiết, khắc phục sự cố khi chúng xảy ra và định cấu hình đúng cho các triển khai nâng cao.



<a id="activation"></a>
## Kích hoạt

Caddy kích hoạt HTTPS tự động một cách ngầm định khi nó biết tên miền (tức là tên máy chủ) hoặc địa chỉ IP mà nó đang phục vụ. Có nhiều cách khác nhau để thông báo cho Caddy về tên miền/IP của bạn, tùy thuộc vào cách bạn chạy hoặc định cấu hình Caddy:

- Một [địa chỉ trang web](/docs/caddyfile/concepts#addresses) trong [Caddyfile](/docs/caddyfile)
- Một [host matcher](/docs/json/apps/http/servers/routes/match/host/) ở cấp cao nhất trong [các tuyến JSON](/docs/modules/http#servers/routes)
- Các cờ dòng lệnh như [`--domain`](/docs/command-line#caddy-file-server) hoặc [`--from`](/docs/command-line#caddy-reverse-proxy)
- Trình tải chứng chỉ [automate](/docs/json/apps/tls/certificates/automate/)

Bất kỳ điều nào sau đây sẽ ngăn HTTPS tự động được kích hoạt, một phần hoặc toàn bộ:

- Vô hiệu hóa nó một cách rõ ràng [qua JSON](/docs/json/apps/http/servers/automatic_https/) hoặc [qua Caddyfile](/docs/caddyfile/options#auto-https)
- Không cung cấp bất kỳ tên máy chủ hoặc địa chỉ IP nào trong cấu hình
- Chỉ lắng nghe trên cổng HTTP
- Thêm tiền tố `http://` vào [địa chỉ trang web](/docs/caddyfile/concepts#addresses) trong Caddyfile
- Tải chứng chỉ theo cách thủ công (trừ khi [`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/) được thiết lập)

**Các trường hợp đặc biệt:**

- Các tên miền kết thúc bằng `.ts.net` sẽ không được quản lý bởi Caddy. Thay vào đó, Caddy sẽ tự động cố gắng lấy các chứng chỉ này tại thời điểm bắt tay (handshake-time) từ phiên bản [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) đang chạy cục bộ. Điều này yêu cầu [HTTPS phải được bật trong tài khoản Tailscale của bạn <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/) và tiến trình Caddy phải chạy dưới quyền root, hoặc bạn phải định cấu hình `tailscaled` để cấp cho người dùng Caddy của bạn [quyền lấy chứng chỉ](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).


<a id="effects"></a>
## Ảnh hưởng

Khi HTTPS tự động được kích hoạt, các điều sau sẽ xảy ra:

- Chứng chỉ được lấy và gia hạn cho [tất cả các tên miền đủ điều kiện](#hostname-requirements)
- HTTP được chuyển hướng sang HTTPS (việc này sử dụng [cổng HTTP](/docs/modules/http#http_port) `80`)

HTTPS tự động không bao giờ ghi đè lên cấu hình rõ ràng, nó chỉ bổ sung cho cấu hình đó.

Nếu bạn đã có một [máy chủ](/docs/json/apps/http/servers/) lắng nghe trên cổng HTTP, các tuyến chuyển hướng HTTP->HTTPS sẽ được chèn sau các tuyến của bạn bằng trình khớp máy chủ (host matcher), nhưng trước một tuyến bắt tất cả (catch-all) do người dùng xác định.

Bạn có thể [tùy chỉnh hoặc vô hiệu hóa HTTPS tự động](/docs/json/apps/http/servers/automatic_https/) nếu cần thiết; ví dụ: bạn có thể bỏ qua một số tên miền nhất định hoặc vô hiệu hóa chuyển hướng (đối với Caddyfile, hãy thực hiện việc này bằng [các tùy chọn toàn cục](/docs/caddyfile/options)).


<a id="hostname-requirements"></a>
## Yêu cầu về tên máy chủ

Tất cả các tên máy chủ (tên miền) đều đủ điều kiện nhận chứng chỉ được quản lý hoàn toàn nếu chúng:

- không trống
- chỉ bao gồm các ký tự chữ cái, chữ số, dấu gạch ngang, dấu chấm và ký tự đại diện (`*`)
- không bắt đầu hoặc kết thúc bằng dấu chấm ([RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5))

Ngoài ra, các tên máy chủ đủ điều kiện nhận chứng chỉ tin cậy công khai nếu chúng:

- không phải là localhost (bao gồm các TLD `.localhost`, `.local`, `.internal` và `.home.arpa`)
- không phải là địa chỉ IP
- chỉ có một ký tự đại diện duy nhất `*` là nhãn ngoài cùng bên trái


<a id="local-https"></a>
## HTTPS cục bộ

Caddy tự động sử dụng HTTPS cho tất cả các trang web có máy chủ (tên miền, IP hoặc tên máy chủ) được chỉ định, bao gồm các máy chủ nội bộ và cục bộ. Một số máy chủ không công khai (ví dụ: `127.0.0.1`, `localhost`) hoặc thường không đủ điều kiện nhận chứng chỉ tin cậy công khai (ví dụ: địa chỉ IP -- bạn có thể lấy chứng chỉ cho chúng, nhưng chỉ từ một số CA nhất định). Những trang này vẫn được phục vụ qua HTTPS trừ khi bị vô hiệu hóa.

Để phục vụ các trang web không công khai qua HTTPS, Caddy tạo cơ quan chứng thực (CA) của riêng mình và sử dụng nó để ký các chứng chỉ. Chuỗi tin cậy bao gồm một chứng chỉ gốc (root) và một chứng chỉ trung gian (intermediate). Các chứng chỉ lá (leaf) được ký bởi chứng chỉ trung gian. Chúng được lưu trữ trong [thư mục dữ liệu của Caddy](/docs/conventions#data-directory) tại `pki/authorities/local`.

CA cục bộ của Caddy được hỗ trợ bởi [các thư viện Smallstep <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/).

HTTPS cục bộ không sử dụng ACME cũng như không thực hiện bất kỳ xác thực DNS nào. Nó chỉ hoạt động trên máy chủ cục bộ và chỉ được tin cậy ở nơi chứng chỉ gốc của CA được cài đặt.

<a id="ca-root"></a>
### CA Gốc (Root)

Khóa riêng (private key) của chứng chỉ gốc được tạo duy nhất bằng nguồn giả ngẫu nhiên an toàn về mặt mật mã và được lưu trữ bền vững với các quyền hạn chế. Nó chỉ được tải vào bộ nhớ để thực hiện các tác vụ ký, sau đó nó sẽ nằm ngoài phạm vi để được thu gom rác (garbage-collected).

Mặc dù Caddy có thể được định cấu hình để ký trực tiếp với chứng chỉ gốc (để hỗ trợ các ứng dụng khách không tuân thủ), nhưng điều này bị vô hiệu hóa theo mặc định và khóa gốc chỉ được sử dụng để ký các chứng chỉ trung gian.

Lần đầu tiên khóa gốc được sử dụng, Caddy sẽ cố gắng cài đặt nó vào (các) kho lưu trữ tin cậy cục bộ của hệ thống. Nếu nó không có quyền làm như vậy, nó sẽ yêu cầu mật khẩu. Hành vi này có thể được vô hiệu hóa bằng [`skip_install_trust` trong Caddyfile](/docs/caddyfile/options#skip-install-trust) hoặc [`"install_trust": false` trong cấu hình JSON](/docs/json/apps/pki/certificate_authorities/install_trust/). Nếu việc này thất bại do chạy dưới quyền người dùng không có đặc quyền, bạn có thể chạy [`caddy trust`](/docs/command-line#caddy-trust) để thử lại việc cài đặt với tư cách là người dùng có đặc quyền.

<aside class="tip">
	Việc tin cậy chứng chỉ gốc của Caddy trên máy của bạn là an toàn miễn là máy tính của bạn không bị xâm nhập và khóa gốc duy nhất của bạn không bị rò rỉ.
</aside>

Sau khi CA gốc của Caddy được cài đặt, bạn sẽ thấy nó trong kho lưu trữ tin cậy cục bộ của mình với tên "Caddy Local Authority" (trừ khi bạn đã định cấu hình một tên khác). Bạn có thể gỡ cài đặt nó bất cứ lúc nào nếu muốn (lệnh [`caddy untrust`](/docs/command-line#caddy-untrust) giúp việc này trở nên dễ dàng).

Lưu ý rằng việc tự động cài đặt chứng chỉ vào các kho lưu trữ tin cậy cục bộ chỉ mang tính chất thuận tiện và không đảm bảo sẽ hoạt động, đặc biệt là nếu các vùng chứa (containers) đang được sử dụng hoặc nếu Caddy đang chạy dưới dạng một dịch vụ hệ thống không có đặc quyền. Cuối cùng, nếu bạn đang dựa vào PKI nội bộ, trách nhiệm của quản trị viên hệ thống là đảm bảo CA gốc của Caddy được thêm đúng cách vào các kho lưu trữ tin cậy cần thiết (điều này nằm ngoài phạm vi của máy chủ web).


<a id="ca-intermediates"></a>
### CA Trung gian (Intermediates)

Một chứng chỉ và khóa trung gian cũng sẽ được tạo ra, dùng để ký các chứng chỉ lá (từng trang web riêng lẻ).

Khác với chứng chỉ gốc, chứng chỉ trung gian có thời hạn ngắn hơn nhiều và sẽ tự động được gia hạn khi cần thiết.


<a id="testing"></a>
## Thử nghiệm

Để thử nghiệm hoặc thử nghiệm với cấu hình Caddy của bạn, hãy đảm bảo bạn [thay đổi điểm cuối ACME](/docs/modules/tls.issuance.acme#ca) thành một URL thử nghiệm hoặc phát triển, nếu không bạn có khả năng gặp giới hạn về tỷ lệ (rate limits) có thể chặn quyền truy cập của bạn vào HTTPS trong tối đa một tuần, tùy thuộc vào giới hạn tỷ lệ mà bạn gặp phải.

Một trong những CA mặc định của Caddy là [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/), có một [điểm cuối thử nghiệm <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) không phải chịu các [giới hạn về tỷ lệ <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/) tương tự:

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

<a id="acme-challenges"></a>
## Thử thách ACME

Việc lấy một chứng chỉ TLS tin cậy công khai yêu cầu xác thực từ một cơ quan bên thứ ba, tin cậy công khai. Ngày nay, quy trình xác thực này được tự động hóa bằng [giao thức ACME <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555) và có thể được thực hiện theo một trong ba cách ("loại thử thách"), được mô tả dưới đây.

Hai loại thử thách đầu tiên được bật theo mặc định. Nếu nhiều thử thách được bật, Caddy chọn ngẫu nhiên một thử thách để tránh sự phụ thuộc vô tình vào một thử thách cụ thể. Theo thời gian, nó sẽ học được loại thử thách nào thành công nhất và sẽ bắt đầu ưu tiên nó trước, nhưng sẽ quay lại các loại thử thách có sẵn khác nếu cần thiết.


<a id="http-challenge"></a>
### Thử thách HTTP

Thử thách HTTP thực hiện tra cứu DNS có thẩm quyền cho bản ghi A/AAAA của tên máy chủ ứng viên, sau đó yêu cầu một tài nguyên mật mã tạm thời qua cổng `80` bằng HTTP. Nếu CA nhìn thấy tài nguyên như mong đợi, chứng chỉ sẽ được cấp.

Thử thách này yêu cầu cổng `80` phải có thể truy cập được từ bên ngoài. Nếu Caddy không thể lắng nghe trên cổng 80, các gói tin từ cổng `80` phải được chuyển tiếp đến [cổng HTTP](/docs/json/apps/http/http_port/) của Caddy.

Thử thách này được bật theo mặc định và không yêu cầu cấu hình rõ ràng.


<a id="tls-alpn-challenge"></a>
### Thử thách TLS-ALPN

Thử thách TLS-ALPN thực hiện tra cứu DNS có thẩm quyền cho bản ghi A/AAAA của tên máy chủ ứng viên, sau đó yêu cầu một tài nguyên mật mã tạm thời qua cổng `443` bằng cách sử dụng bắt tay TLS chứa các giá trị ServerName và ALPN đặc biệt. Nếu CA nhìn thấy tài nguyên như mong đợi, chứng chỉ sẽ được cấp.

Thử thách này yêu cầu cổng `443` phải có thể truy cập được từ bên ngoài. Nếu Caddy không thể lắng nghe trên cổng 443, các gói tin từ cổng `443` phải được chuyển tiếp đến [cổng HTTPS](/docs/json/apps/http/https_port/) của Caddy.

Thử thách này được bật theo mặc định và không yêu cầu cấu hình rõ ràng.


<a id="dns-challenge"></a>
### Thử thách DNS

Thử thách DNS thực hiện tra cứu DNS có thẩm quyền cho các bản ghi `TXT` của tên máy chủ ứng viên và tìm kiếm một bản ghi `TXT` đặc biệt với một giá trị nhất định. Nếu CA nhìn thấy giá trị như mong đợi, chứng chỉ sẽ được cấp.

Thử thách này không yêu cầu bất kỳ cổng nào được mở và máy chủ yêu cầu chứng chỉ không cần phải truy cập được từ bên ngoài. Tuy nhiên, thử thách DNS yêu cầu phải cấu hình. Caddy cần biết thông tin xác thực để truy cập nhà cung cấp DNS của tên miền của bạn để nó có thể thiết lập (và xóa) các bản ghi `TXT` đặc biệt. Nếu thử thách DNS được bật, các thử thách khác sẽ bị vô hiệu hóa theo mặc định.

Vì các CA ACME tuân theo các tiêu chuẩn DNS khi tra cứu các bản ghi `TXT` để xác minh thử thách, bạn có thể sử dụng các bản ghi CNAME để ủy quyền trả lời thử thách cho các vùng DNS khác. Điều này có thể được sử dụng để ủy quyền miền phụ `_acme-challenge` cho [vùng khác](/docs/caddyfile/directives/tls#dns_challenge_override_domain). Điều này đặc biệt hữu ích nếu nhà cung cấp DNS của bạn không cung cấp API hoặc không được hỗ trợ bởi một trong các plugin DNS cho Caddy.

Hỗ trợ nhà cung cấp DNS là một nỗ lực của cộng đồng. [Tìm hiểu cách bật thử thách DNS cho nhà cung cấp của bạn tại wiki của chúng tôi.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


<a id="on-demand-tls"></a>
## TLS theo yêu cầu (On-Demand TLS)

Caddy đã tiên phong trong một công nghệ mới mà chúng tôi gọi là **TLS theo yêu cầu (On-Demand TLS)**, công nghệ này sẽ tự động lấy chứng chỉ mới trong lần bắt tay TLS đầu tiên yêu cầu nó, thay vì tại thời điểm tải cấu hình. Quan trọng là việc này **không** yêu cầu phải mã hóa cứng các tên miền trong cấu hình của bạn trước.

Nhiều doanh nghiệp tin dùng tính năng độc đáo này để mở rộng quy trình triển khai TLS của họ với chi phí thấp hơn và không gặp khó khăn trong vận hành khi phục vụ hàng chục nghìn trang web.

TLS theo yêu cầu hữu ích nếu:

- bạn không biết tất cả các tên miền khi bạn bắt đầu hoặc tải lại máy chủ của mình,
- tên miền có thể chưa được định cấu hình đúng ngay lập tức (các bản ghi DNS chưa được thiết lập),
- bạn không kiểm soát các tên miền (ví dụ: chúng là tên miền của khách hàng).

Khi TLS theo yêu cầu được bật, bạn không cần chỉ định tên miền trong cấu hình của mình để lấy chứng chỉ cho chúng. Thay vào đó, khi nhận được bắt tay TLS cho một tên máy chủ (SNI) mà Caddy chưa có chứng chỉ, bắt tay đó sẽ được giữ lại trong khi Caddy lấy chứng chỉ để sử dụng để hoàn tất quá trình bắt tay. Thời gian chờ thường chỉ mất vài giây và chỉ có lần bắt tay ban đầu đó là chậm. Tất cả các lần bắt tay trong tương lai đều nhanh vì chứng chỉ được lưu vào bộ nhớ đệm và được sử dụng lại, đồng thời việc gia hạn diễn ra trong nền. Các lần bắt tay trong tương lai có thể kích hoạt bảo trì cho chứng chỉ để giữ cho nó được gia hạn, nhưng việc bảo trì này diễn ra trong nền nếu chứng chỉ chưa hết hạn.

<a id="using-on-demand-tls"></a>
### Sử dụng TLS theo yêu cầu

**TLS theo yêu cầu phải được bật và hạn chế để ngăn chặn việc lạm dụng.**

Việc bật TLS theo yêu cầu diễn ra trong [các chính sách tự động hóa TLS](/docs/json/apps/tls/automation/policies/) nếu sử dụng cấu hình JSON, hoặc [trong các khối trang web với chỉ thị `tls`](/docs/caddyfile/directives/tls) nếu sử dụng Caddyfile.

Để ngăn chặn việc lạm dụng tính năng này, bạn phải cấu hình các hạn chế. Việc này được thực hiện trong [đối tượng `automation` của cấu hình JSON](/docs/json/apps/tls/automation/on_demand/), hoặc [tùy chọn toàn cục `on_demand_tls`](/docs/caddyfile/options#on-demand-tls) của Caddyfile. Các hạn chế là "toàn cục" và không thể cấu hình cho từng trang web hoặc từng tên miền. Hạn chế chính là một điểm cuối "ask" mà Caddy sẽ gửi một yêu cầu HTTP để hỏi xem nó có quyền lấy và quản lý chứng chỉ cho tên miền trong lần bắt tay đó hay không. Điều này có nghĩa là bạn sẽ cần một phần phụ trợ (backend) nội bộ có thể, ví dụ, truy vấn bảng tài khoản trong cơ sở dữ liệu của bạn và xem liệu khách hàng đã đăng ký với tên miền đó hay chưa.

Hãy lưu ý về tốc độ mà CA của bạn có thể cấp chứng chỉ. Nếu mất hơn vài giây, điều này sẽ ảnh hưởng tiêu cực đến trải nghiệm người dùng (chỉ đối với khách truy cập đầu tiên).

Do tính chất trì hoãn và cấu hình bổ sung cần thiết để ngăn chặn lạm dụng, chúng tôi khuyên bạn chỉ nên bật TLS theo yêu cầu khi trường hợp sử dụng thực tế của bạn được mô tả ở trên.

[Xem bài viết wiki của chúng tôi để biết thêm thông tin về cách sử dụng TLS theo yêu cầu một cách hiệu quả.](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)

<a id="errors"></a>
## Lỗi

Caddy cố gắng hết sức để tiếp tục nếu có lỗi xảy ra với việc quản lý chứng chỉ.

Theo mặc định, việc quản lý chứng chỉ được thực hiện trong nền. Điều này có nghĩa là nó sẽ không chặn quá trình khởi động hoặc làm chậm các trang web của bạn. Tuy nhiên, nó cũng có nghĩa là máy chủ sẽ chạy ngay cả trước khi tất cả các chứng chỉ có sẵn. Chạy trong nền cho phép Caddy thử lại với tính năng trì hoãn lũy thừa (exponential backoff) trong một thời gian dài.

Dưới đây là những gì sẽ xảy ra nếu có lỗi khi lấy hoặc gia hạn chứng chỉ:

1. Caddy thử lại một lần sau khi tạm dừng một lát để đề phòng trường hợp đó là sự cố ngẫu nhiên
2. Caddy tạm dừng một lát, sau đó chuyển sang loại thử thách được bật tiếp theo
3. Sau khi tất cả các loại thử thách được bật đã được thử, [nó sẽ thử nhà phát hành tiếp theo được cấu hình](#issuer-fallback)
	- Let's Encrypt
	- ZeroSSL
4. Sau khi tất cả các nhà phát hành đã được thử, nó sẽ trì hoãn lũy thừa
	- Tối đa 1 ngày giữa các lần thử
	- Trong tối đa 30 ngày

Trong các lần thử lại với Let's Encrypt, Caddy chuyển sang [môi trường thử nghiệm (staging) của họ <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) để tránh các vấn đề về giới hạn tỷ lệ. Đây không phải là một chiến lược hoàn hảo, nhưng nhìn chung nó có ích.

Các thử thách ACME mất ít nhất vài giây và giới hạn tỷ lệ nội bộ giúp giảm thiểu việc lạm dụng vô tình. Caddy sử dụng giới hạn tỷ lệ nội bộ bên cạnh những gì bạn hoặc CA định cấu hình để bạn có thể đưa cho Caddy một danh sách một triệu tên miền và nó sẽ dần dần -- nhưng nhanh nhất có thể -- lấy chứng chỉ cho tất cả chúng. Giới hạn tỷ lệ nội bộ của Caddy hiện là 10 lần thử cho mỗi tài khoản ACME sau mỗi 10 giây.

Để tránh rò rỉ tài nguyên, Caddy hủy các tác vụ đang thực hiện (bao gồm các giao dịch ACME) khi cấu hình bị thay đổi. Mặc dù Caddy có khả năng xử lý việc tải lại cấu hình thường xuyên, hãy lưu ý đến các cân nhắc vận hành như thế này và cân nhắc việc gom nhóm các thay đổi cấu hình để giảm bớt số lần tải lại và cho Caddy cơ hội thực sự hoàn thành việc lấy chứng chỉ trong nền.

<a id="issuer-fallback"></a>
### Cơ chế dự phòng nhà phát hành (Issuer fallback)

Caddy là máy chủ đầu tiên (và cho đến nay là duy nhất) hỗ trợ chuyển đổi dự phòng tự động, hoàn toàn dư thừa sang các CA khác trong trường hợp nó không thể lấy chứng chỉ thành công.

Theo mặc định, Caddy bật hai CA tương thích với ACME: [**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) và [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com). Nếu Caddy không thể lấy chứng chỉ từ Let's Encrypt, nó sẽ thử với ZeroSSL; nếu cả hai đều thất bại, nó sẽ trì hoãn và thử lại sau. Trong cấu hình của bạn, bạn có thể tùy chỉnh nhà phát hành nào Caddy sử dụng để lấy chứng chỉ, cho toàn bộ hệ thống hoặc cho các tên miền cụ thể.


<a id="storage"></a>
## Lưu trữ

Caddy sẽ lưu trữ các chứng chỉ công khai, khóa riêng và các tài nguyên khác trong [cơ sở lưu trữ được định cấu hình](/docs/json/storage/) (hoặc cơ sở lưu trữ mặc định, nếu không được định cấu hình -- xem liên kết để biết chi tiết).

**Điều chính bạn cần biết khi sử dụng cấu hình mặc định là thư mục `$HOME` phải có quyền ghi và bền vững.** Để giúp bạn khắc phục sự cố, Caddy in các biến môi trường của nó khi khởi động nếu cờ `--environ` được chỉ định.

Bất kỳ phiên bản Caddy nào được cấu hình để sử dụng cùng một bộ lưu trữ sẽ tự động chia sẻ các tài nguyên đó và điều phối việc quản lý chứng chỉ như một cụm (cluster).

Trước khi thực hiện bất kỳ giao dịch ACME nào, Caddy sẽ kiểm tra bộ lưu trữ được cấu hình để đảm bảo nó có thể ghi được và có đủ dung lượng. Điều này giúp giảm bớt sự tranh chấp khóa (lock contention) không cần thiết.


<a id="wildcard-certificates"></a>
## Chứng chỉ Wildcard

Caddy có thể lấy và quản lý chứng chỉ wildcard khi nó được cấu hình để phục vụ một trang web với tên wildcard đủ điều kiện. Một tên trang web đủ điều kiện cho wildcard nếu chỉ có nhãn tên miền ngoài cùng bên trái của nó là một ký tự đại diện. Ví dụ: `*.example.com` đủ điều kiện, nhưng những tên này thì không: `sub.*.example.com`, `foo*.example.com`, `*bar.example.com`, và `*.*.example.com`. (Đây là một hạn chế của WebPKI.)

Nếu sử dụng Caddyfile, Caddy lấy tên trang web theo đúng nghĩa đen đối với tên chủ thể chứng chỉ. Nói cách khác, một trang web được định nghĩa là `sub.example.com` sẽ khiến Caddy quản lý chứng chỉ cho `sub.example.com`, và một trang web được định nghĩa là `*.example.com` sẽ khiến Caddy quản lý chứng chỉ wildcard cho `*.example.com`. Bạn có thể thấy điều này được thể hiện trên trang [Các mẫu Caddyfile phổ biến](/docs/caddyfile/patterns#wildcard-certificates) của chúng tôi. Nếu bạn cần hành vi khác, [cấu hình JSON](/docs/json/) cung cấp cho bạn quyền kiểm soát chính xác hơn đối với các chủ thể chứng chỉ và tên trang web ("host matchers").

Kể từ Caddy 2.10, khi tự động hóa chứng chỉ wildcard, Caddy sẽ sử dụng chứng chỉ wildcard cho các miền phụ riêng lẻ trong cấu hình. Nó sẽ không lấy chứng chỉ cho các miền phụ riêng lẻ trừ khi được cấu hình rõ ràng để làm như vậy (ví dụ: với `force_automate`).

Chứng chỉ wildcard đại diện cho một mức độ thẩm quyền rộng và chỉ nên được sử dụng khi bạn có quá nhiều miền phụ đến mức việc quản lý chứng chỉ riêng lẻ cho chúng sẽ gây áp lực lên PKI hoặc khiến bạn gặp phải các giới hạn tỷ lệ do CA thực thi, hoặc nếu sự đánh đổi về quyền riêng tư xứng đáng với rủi ro để lộ phần lớn vùng DNS trong trường hợp khóa bị xâm nhập. Lưu ý rằng chỉ riêng chứng chỉ wildcard không cung cấp sự riêng tư trong việc che giấu các miền phụ cụ thể: chúng vẫn bị lộ trong các gói tin TLS ClientHello trừ khi ClientHello được mã hóa (ECH) được bật. (Xem bên dưới.)

**Lưu ý:** [Let's Encrypt yêu cầu <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) [thử thách DNS](#dns-challenge) để lấy chứng chỉ wildcard.


<a id="encrypted-clienthello-ech"></a>
## ClientHello được mã hóa (ECH)

Thông thường, các lần bắt tay TLS liên quan đến việc gửi ClientHello, bao gồm Chỉ báo tên máy chủ (Server Name Indicator - SNI; tên miền đang được kết nối tới), ở dạng văn bản thuần túy (plaintext). Đó là vì nó chứa các thông số cần thiết để mã hóa kết nối diễn ra sau khi bắt tay. Điều này, tất nhiên, để lộ tên miền, vốn là phần nhạy cảm nhất của ClientHello, cho bất kỳ ai có thể nghe lén các kết nối, ngay cả khi họ không ở gần bạn về mặt vật lý. Nó tiết lộ dịch vụ nào bạn đang kết nối tới khi IP đích có thể phục vụ nhiều trang web khác nhau và đó là cách một số chính phủ thực hiện kiểm duyệt Internet.

Với ClientHello được mã hóa, ứng dụng khách có thể bảo vệ tên miền bằng cách bọc ClientHello thực trong một ClientHello "bên ngoài" để thiết lập các thông số cho việc giải mã ClientHello "bên trong". Tuy nhiên, nhiều bộ phận chuyển động cần phải kết hợp hoàn hảo để điều này hoạt động và mang lại lợi ích riêng tư thực sự.

Đầu tiên, ứng dụng khách cần biết những thông số nào, hoặc cấu hình nào, để sử dụng nhằm mã hóa ClientHello. Thông tin này bao gồm một khóa công khai và tên miền "bên ngoài" (tên miền công khai - "public name"), cùng với những thông tin khác. Cấu hình này phải được công bố hoặc phân phối bằng cách nào đó một cách đáng tin cậy.

Về lý thuyết, bạn có thể viết nó ra một mảnh giấy và đưa cho mọi người, nhưng hầu hết các trình duyệt lớn đều hỗ trợ tra cứu các bản ghi DNS loại HTTPS chứa các thông số ECH khi kết nối tới một trang web. Do đó, bạn sẽ cần phải: (1) tạo một cấu hình ECH (cặp khóa công khai/riêng tư, cùng với các thông số khác), và sau đó (2) tạo một bản ghi DNS loại HTTPS chứa cấu hình ECH được mã hóa base64.

Hoặc... bạn có thể để Caddy làm tất cả những việc đó cho bạn. Caddy là máy chủ web đầu tiên và duy nhất có thể tự động tạo, công bố và phục vụ các cấu hình ECH.

Sau khi bản ghi HTTPS được công bố, các ứng dụng khách sẽ cần thực hiện tra cứu DNS cho bản ghi HTTPS khi kết nối tới trang web của bạn. Thông thường, các lần tra cứu DNS ở dạng văn bản thuần túy, điều này làm ảnh hưởng đến tính bảo mật của các lần bắt tay ECH kết quả, vì vậy các trình duyệt sẽ cần sử dụng một giao thức DNS an toàn như DNS-over-HTTPS (DoH) hoặc DNS-over-TLS (DoT). Tùy thuộc vào trình duyệt, việc này có thể cần phải được bật thủ công.

Sau khi ứng dụng khách đã tải xuống cấu hình ECH một cách an toàn, nó sử dụng khóa công khai được nhúng để mã hóa ClientHello và tiến hành kết nối tới trang web của bạn. Caddy sau đó giải mã ClientHello bên trong và tiến hành phục vụ trang web của bạn mà không có tên miền nào xuất hiện ở dạng văn bản thuần túy trên đường truyền.

<a id="deployment-considerations"></a>
### Các cân nhắc khi triển khai

ECH là một công nghệ sắc thái. Mặc dù Caddy tự động hóa hoàn toàn ECH, nhưng cần cân nhắc nhiều thứ để đạt được lợi ích riêng tư tối đa. Bạn cũng nên biết về các sự đánh đổi khác nhau. 

<a id="publication"></a>
#### Việc công bố

Caddy sẽ chỉ tạo bản ghi HTTPS cho một tên miền nếu đã có bản ghi cho tên miền đó. Điều này ngăn chặn việc làm hỏng các lần tra cứu DNS cho một miền phụ có thể được bao phủ bởi một wildcard. Đảm bảo rằng các trang web của bạn có ít nhất một bản ghi A/AAAA trỏ đến máy chủ của bạn. Nếu bạn chỉ sử dụng ký tự đại diện cho các bản ghi DNS, thì miền ký tự đại diện cũng sẽ cần xuất hiện trong cấu hình Caddy của bạn.

Caddy sẽ không công bố bản ghi HTTPS cho một tên miền có bản ghi CNAME.

#### ECH GREASE

Nếu bạn mở Wireshark và sau đó kết nối tới bất kỳ trang web nào (ngay cả trang không hỗ trợ ECH) trong một phiên bản trình duyệt lớn hiện đại như Firefox hoặc Chrome (ngay cả khi ECH bị vô hiệu hóa), bạn có thể nhận thấy quá trình bắt tay của nó bao gồm phần mở rộng `encrypted_client_hello`:

![ECH GREASE](/resources/images/ech-grease.png)

Mục đích của việc này là làm cho các lần bắt tay ECH thực thụ không thể phân biệt được với các lần bắt tay văn bản thuần túy. Nếu các lần bắt tay ECH trông khác với các lần bình thường, những người kiểm duyệt có thể dễ dàng chặn các lần bắt tay ECH với thiệt hại/tác động phụ tối thiểu. Nhưng nếu họ chặn bất kỳ lần bắt tay nào có phần mở rộng ECH khả thi, về cơ bản họ sẽ tắt phần lớn Internet. (Mục tiêu là tăng chi phí cho việc kiểm duyệt trên diện rộng.)

Đây chủ yếu là điều quan trọng cần biết khi khắc phục sự cố kết nối.

<a id="key-rotation"></a>
#### Việc xoay vòng khóa (Key rotation)

Giống như các khóa chứng chỉ, việc sử dụng cùng một khóa trong một thời gian dài là không tốt (và có thể cực kỳ mất an toàn). Vì vậy, các khóa ECH nên được xoay vòng định kỳ. Không giống như chứng chỉ, các cấu hình ECH không hết hạn một cách nghiêm ngặt. Nhưng dù vậy các máy chủ vẫn nên xoay vòng chúng.

Tuy nhiên, việc xoay vòng khóa rất phức tạp, bởi vì các ứng dụng khách cần biết về các khóa đã cập nhật. Nếu máy chủ chỉ đơn giản thay thế các khóa cũ bằng các khóa mới, tất cả các lần bắt tay ECH sẽ thất bại trừ khi các ứng dụng khách được thông báo ngay lập tức về các khóa mới. Nhưng việc chỉ công bố các khóa đã cập nhật là chưa đủ. Thực tế là, các bản ghi DNS có TTL và các trình giải quyết (resolvers) lưu trữ các phản hồi, v.v. Có thể mất vài phút, vài giờ hoặc thậm chí vài ngày để các ứng dụng khách truy vấn các bản ghi HTTPS đã cập nhật và bắt đầu sử dụng cấu hình ECH mới.

Vì lý do đó, các máy chủ nên tiếp tục hỗ trợ các cấu hình ECH cũ trong một khoảng thời gian. Không làm như vậy sẽ có nguy cơ để lộ tên máy chủ ở dạng văn bản thuần túy _trên diện rộng_. Caddy xoay vòng các khóa định kỳ và hỗ trợ các khóa đã xoay vòng trong một thời gian cho đến khi chúng cuối cùng bị loại bỏ.

Tuy nhiên, điều đó có thể là chưa đủ. Một số ứng dụng khách vẫn sẽ không nhận được các khóa đã cập nhật vì nhiều lý do khác nhau và bất cứ khi nào điều đó xảy ra, sẽ có nguy cơ để lộ tên máy chủ. Vì vậy, cần có một cách khác để cung cấp cho ứng dụng khách cấu hình đã cập nhật _ngay trong_ kết nối. Đó là mục đích của _tên bên ngoài_ (hoặc _tên công khai_).

<a id="public-name"></a>
#### Tên công khai (Public name)

ClientHello "bên ngoài" là một ClientHello bình thường với hai điểm khác biệt tinh tế mà chỉ máy chủ gốc mới biết:

1. Phần mở rộng SNI là giả
2. Phần mở rộng ECH là thật

Phần mở rộng SNI "bên ngoài" đó chứa tên công khai giúp bảo vệ các tên miền thực của bạn. Tên này có thể là bất kỳ thứ gì, nhưng **máy chủ của bạn phải có thẩm quyền đối với tên công khai đó** vì Caddy _will_ lấy một chứng chỉ cho nó.

Nếu một ứng dụng khách cố gắng thực hiện một kết nối ECH nhưng máy chủ không thể giải mã ClientHello bên trong, máy chủ thực sự có thể hoàn tất quá trình bắt tay bằng cách sử dụng ClientHello _bên ngoài_ với một chứng chỉ cho tên bên ngoài. Kết nối an toàn này được sử dụng một cách nghiêm ngặt _chỉ_ để gửi cho ứng dụng khách cấu hình ECH hiện tại; tức là nó là một kết nối TLS tạm thời cho mục đích duy nhất là hoàn tất kết nối TLS ban đầu. Không có dữ liệu ứng dụng nào được truyền đi: chỉ có khóa ECH. Khi ứng dụng khách đã có khóa đã cập nhật, nó có thể thiết lập kết nối TLS như mong muốn.

Theo cách này, tên máy chủ thực vẫn được bảo vệ và các ứng dụng khách không đồng bộ vẫn có thể kết nối, cả hai đều là các yếu tố quan trọng của bảo mật.

Tên bên ngoài có thể là một trong các tên miền trang web của bạn, một miền phụ hoặc bất kỳ tên miền nào khác trỏ tới máy chủ của bạn. Chúng tôi khuyên bạn nên chọn đúng một tên chung. Ví dụ, Cloudflare phục vụ hàng triệu trang web đằng sau `cloudflare-ech.com`. Điều này quan trọng để tăng quy mô cho tập hợp ẩn danh (anonymity set) của bạn.

Tên công khai không được để trống; tức là tên công khai phải được cấu hình để mọi thứ hoạt động. Caddy hiện không bắt buộc điều này (và có thể sẽ bắt buộc sau này), nhưng đặc tả ECH yêu cầu tên công khai phải dài ít nhất 1 byte. Một số phần mềm sẽ chấp nhận tên trống, số khác thì không. Điều này có thể dẫn đến các hành vi khó hiểu như trình duyệt sử dụng ECH nhưng máy chủ từ chối nó là không hợp lệ; hoặc trình duyệt không sử dụng ECH (vì nó không hợp lệ) ngay cả khi cấu hình đã có trong bản ghi DNS một cách chính xác. Trách nhiệm của chủ sở hữu trang web là đảm bảo cấu hình và công bố ECH đúng cách để đảm bảo quyền riêng tư.


<a id="anonymity-set"></a>
#### Tập hợp ẩn danh (Anonymity set)

Để tối đa hóa lợi ích riêng tư của ECH, hãy cố gắng tối đa hóa quy mô của _tập hợp ẩn danh_ của bạn. Về bản chất, tập hợp này bao gồm các máy chủ hướng tới ứng dụng khách có hành vi giống hệt nhau đối với những người quan sát. Ý tưởng là một người quan sát không thể dễ dàng thu hẹp/suy luận ra các trang web hoặc dịch vụ khả thi mà ứng dụng khách đang kết nối tới.

Trong thực tế, chúng tôi khuyên bạn chỉ nên có một tên công khai cho tất cả các trang web của mình. (Chỉ có 1 tên công khai cho mỗi cấu hình ECH, vì vậy điều này ngụ ý chỉ có 1 cấu hình ECH hoạt động tại bất kỳ thời điểm nào.) Nếu bạn vận hành Caddy trong một cụm, Caddy sẽ tự động chia sẻ và điều phối các cấu hình ECH với các phiên bản khác, giúp giải quyết việc này cho bạn.

Nếu đẩy tới mức cực đoan, điều này ngụ ý rằng mọi trang web trên Internet có thể hoặc nên nằm sau một địa chỉ IP duy nhất và một tên công khai duy nhất...


<a id="centralization"></a>
#### Sự tập trung hóa (Centralization)

... điều này dẫn chúng ta đến chủ đề tiếp theo: sự tập trung hóa. Một trong những lời chỉ trích đối với ECH là nó có xu hướng thúc đẩy sự tập trung hóa. Nó thực hiện điều này theo ít nhất hai cách: (1) bởi các ứng dụng khách ưu tiên DoH/DoT cho các lần tra cứu DNS, việc này gửi tất cả các lần tra cứu DNS qua một số ít các nhà cung cấp, và (2) bằng cách tối đa hóa quy mô của tập hợp ẩn danh trên diện rộng.

Khi DoH hoặc DoT được sử dụng, các lần tra cứu DNS đều đi qua nhà cung cấp DoH/DoT. Giữa ứng dụng khách và nhà cung cấp, dữ liệu DNS được mã hóa, nhưng giữa nhà cung cấp và máy chủ DNS, nó không được mã hóa. DoH/DoT toàn cầu về cơ bản sẽ tập trung tất cả các lưu lượng DNS dạng văn bản thuần túy béo bở vào một vài đường ống lớn chín muồi cho việc quan sát... hoặc thất bại.

Tương tự như vậy, nếu chúng ta thực sự tối đa hóa tập hợp ẩn danh trên diện rộng, tất cả các trang web sẽ được bảo vệ đằng sau một tên công khai duy nhất, như `cloudflare-ech.com`. Điều này tốt cho quyền riêng tư, nhưng khi đó toàn bộ Internet sẽ nằm dưới sự chi phối của Cloudflare và tên miền duy nhất đó. Bây giờ, việc tối đa hóa đến mức đó là không cần thiết hoặc không thực tế, nhưng những tác động về mặt lý thuyết vẫn có giá trị.

Chúng tôi khuyến nghị mỗi tổ chức hoặc cá nhân chọn một tên duy nhất cho tất cả các trang web của họ và sử dụng tên đó, và trong hầu hết các trường hợp, điều đó sẽ cung cấp đủ quyền riêng tư. Tuy nhiên, vui lòng tham khảo ý kiến các chuyên gia về các mô hình đe dọa riêng lẻ cho trường hợp cụ thể của bạn.


<a id="subdomain-privacy"></a>
#### Quyền riêng tư của miền phụ

Với ECH, giờ đây về lý thuyết có thể giữ các miền phụ bí mật/riêng tư khỏi các kênh phụ nếu được triển khai đúng cách.

Hầu hết các trang web không cần điều này, vì nói chung, miền phụ là thông tin công khai. Chúng tôi khuyên bạn không nên đưa thông tin nhạy cảm vào tên miền. Điều đó có nghĩa là...

Để tránh rò rỉ các miền phụ nhạy cảm vào các nhật ký Tính minh bạch của chứng chỉ (Certificate Transparency - CT), hãy sử dụng chứng chỉ wildcard thay thế. Nói cách khác, thay vì đưa `sub.example.com` vào cấu hình của bạn, hãy đưa `*.example.com`. (Xem [Chứng chỉ Wildcard](#wildcard-certificates) để biết thông tin quan trọng.)

Một nguồn rò rỉ khác là DNSSEC, mà hầu hết các máy chủ DNS có thẩm quyền sử dụng theo mặc định. Thông qua một quy trình có tên là "đi bộ vùng" (zone walking), việc liệt kê miền phụ là khả thi bằng cách nhìn vào các bản ghi NSEC, vốn được sử dụng để cung cấp thông tin xác thực về sự không tồn tại. Với mục đích này, chúng trỏ tới miền phụ có sẵn tiếp theo theo thứ tự bảng chữ cái, tạo thành một danh sách liên kết của tất cả các bản ghi. Đảm bảo tên miền của bạn đang sử dụng ít nhất là NSEC3 hoặc lý tưởng nhất là một bản ghi CNAME wildcard để giảm thiểu điều này.

Sau đó, bật ECH trong Caddy. Một chứng chỉ wildcard kết hợp với ECH và một bản ghi CNAME wildcard sẽ che giấu các miền phụ một cách thích hợp, miễn là mọi ứng dụng khách cố gắng kết nối tới nó đều sử dụng ECH và có một triển khai mạnh mẽ. (Bạn vẫn phải phụ thuộc vào các ứng dụng khách để giữ gìn quyền riêng tư.)


<a id="enabling-ech"></a>
### Bật ECH

Vì để ECH hoạt động cần phải công bố các cấu hình vào các bản ghi DNS, bạn sẽ cần một bản dựng Caddy có tích hợp [mô-đun caddy-dns](https://github.com/caddy-dns) cho nhà cung cấp DNS của bạn.

Sau đó, với một Caddyfile, hãy chỉ định cấu hình nhà cung cấp DNS của bạn trong các tùy chọn toàn cục, cũng như tên công khai ECH mà bạn muốn sử dụng:

```caddy
{
	dns <provider config...>
	ech example.com
}
```

Hãy nhớ rằng:

- Mô-đun nhà cung cấp DNS phải được tích hợp và bạn phải có cấu hình phù hợp cho nhà cung cấp/tài khoản của mình.
- Tên công khai ECH phải trỏ tới máy chủ của bạn. Caddy sẽ lấy một chứng chỉ cho nó. Nó không bắt buộc phải là một trong các tên miền trang web của bạn.

Nếu sử dụng JSON, hãy thêm các thuộc tính này vào ứng dụng `tls`:

```json
"encrypted_client_hello": {
	"configs": [
		{
			"public_name": "example.com"
		}
	]
},
"dns": {
	"name": "<provider name>",
	// cấu hình nhà cung cấp
}
```

Các cấu hình này sẽ bật ECH và công bố các cấu hình ECH cho tất cả các trang web của bạn. Cấu hình JSON cung cấp nhiều tính linh hoạt hơn nếu bạn cần tùy chỉnh hành vi hoặc có một thiết lập nâng cao.

<a id="verifying-ech"></a>
### Xác minh ECH

Hiện tại vẫn chưa có nhiều công cụ xoay quanh ECH, vì vậy tại thời điểm viết bài, cách tốt nhất và phổ biến nhất để xác minh rằng nó đang hoạt động là sử dụng Wireshark và tìm tên công khai của bạn trong trường ServerName.

Đầu tiên, hãy khởi động máy chủ của bạn và xem các nhật ký có đề cập điều gì đó như "published ECH configuration list" (đã công bố danh sách cấu hình ECH) cho các tên miền của bạn hay không. (Nếu bạn gặp bất kỳ lỗi nào với việc công bố, hãy đảm bảo mô-đun nhà cung cấp DNS của bạn hỗ trợ [libdns 1.0](https://github.com/libdns/libdns) và gửi một báo cáo lỗi lên kho lưu trữ của nhà cung cấp nếu bạn gặp vấn đề.) Caddy cũng sẽ lấy một chứng chỉ cho tên công khai.

Tiếp theo, hãy đảm bảo trình duyệt của bạn đã bật ECH; việc này có thể yêu cầu bật DoH/DoT. Bạn cũng nên xóa bộ nhớ đệm DNS của trình duyệt (hoặc của hệ thống), để đảm bảo nó sẽ nhận các bản ghi HTTPS mới được công bố. Chúng tôi cũng khuyên bạn nên đóng trình duyệt hoặc ít nhất là mở một tab ẩn danh mới để đảm bảo nó không sử dụng lại các kết nối hiện có.

Thế nên, hãy mở Wireshark và bắt đầu lắng nghe trên giao diện mạng thích hợp. Trong khi Wireshark đang thu thập các gói tin, hãy tải trang web của bạn trong trình duyệt. Sau đó, bạn có thể tạm dừng Wireshark. Tìm TLS ClientHello của bạn, và bạn sẽ thấy _tên công khai_ trong trường ServerName, thay vì tên miền thực tế mà bạn đã kết nối tới.

Hãy nhớ rằng: bạn vẫn có thể thấy một phần mở rộng `encrypted_client_hello` ngay cả khi ECH không được sử dụng. Chỉ báo chính là giá trị SNI. Bạn không bao giờ được thấy tên trang web thực ở dạng văn bản thuần túy với Wireshark nếu ECH đang hoạt động bình thường.

Nếu bạn gặp vấn đề khi triển khai với ECH, trước tiên hãy hỏi trong [diễn đàn](https://caddy.community) của chúng tôi. Nếu đó là lỗi, bạn có thể [gửi một báo cáo lỗi](https://github.com/caddyserver/caddy/issues) trên GitHub.


<a id="ech-in-storage"></a>
### ECH trong lưu trữ

Các cấu hình ECH được lưu trữ trong [thư mục dữ liệu](/docs/conventions#data-directory) trong mô-đun lưu trữ được định cấu hình (mặc định là hệ thống tệp) dưới thư mục `ech/configs`.

Thư mục tiếp theo là một ID cấu hình ECH, được tạo ngẫu nhiên và tương đối không quan trọng. Sự ngẫu nhiên được đặc tả khuyến nghị nhằm giúp giảm thiểu việc lấy dấu vân tay/theo dõi (fingerprinting/tracking).

Một tệp đính kèm siêu dữ liệu (metadata sidecar file) giúp Caddy theo dõi thời điểm việc công bố diễn ra lần cuối. Điều này ngăn chặn việc dồn dập gửi yêu cầu tới nhà cung cấp DNS của bạn tại mỗi lần tải lại cấu hình. Nếu bạn phải đặt lại trạng thái này, bạn có thể xóa tệp siêu dữ liệu một cách an toàn. Tuy nhiên, việc này cũng có thể đặt lại thời điểm mà khóa sẽ được xoay vòng. Bạn cũng có thể vào tệp và xóa chỉ thông tin về việc công bố.
