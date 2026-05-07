---
title: Kiến trúc
---

Kiến trúc
============

Caddy là một tệp thực thi duy nhất, độc lập, tĩnh và không có phụ thuộc bên ngoài vì nó được viết bằng Go. Những giá trị này tạo nên phần quan trọng trong tầm nhìn của dự án bởi vì chúng đơn giản hóa việc triển khai và giảm bớt các thao tác khắc phục sự cố tẻ nhạt trong môi trường sản xuất.

Nếu không có liên kết động (dynamic linking), vậy làm thế nào nó có thể được mở rộng? Caddy sở hữu một kiến trúc plugin mới lạ giúp mở rộng khả năng của nó vượt xa bất kỳ máy chủ web nào khác, ngay cả những máy chủ có phụ thuộc bên ngoài (liên kết động).

Triết lý "ít bộ phận chuyển động hơn" của chúng tôi cuối cùng dẫn đến các trang web đáng tin cậy hơn, dễ quản lý hơn và ít tốn kém hơn&mdash;đặc biệt là ở quy mô lớn. Tài liệu bán kỹ thuật này mô tả cách chúng tôi đạt được mục tiêu đó thông qua kỹ thuật phần mềm.


<a id="overview"></a>
## Tổng quan

Caddy bao gồm một lệnh (command), thư viện cốt lõi (core library) và các mô-đun (modules).

**Lệnh** cung cấp [giao diện dòng lệnh](/docs/command-line) mà hy vọng bạn đã quen thuộc. Đó là cách bạn khởi chạy tiến trình từ hệ điều hành của mình. Lượng mã và logic ở đây khá tối thiểu và chỉ có những gì cần thiết để khởi động phần cốt lõi theo cách người dùng mong muốn. Chúng tôi cố tình tránh sử dụng các cờ (flags) và biến môi trường cho cấu hình, ngoại trừ những gì liên quan đến việc khởi động cấu hình.


<aside class="tip">

Các mô-đun có thể thêm các lệnh con vào giao diện dòng lệnh! Ví dụ, đó là nguồn gốc của lệnh [`caddy file-server`](/docs/command-line#caddy-file-server) command. Các lệnh được thêm vào này có thể có bất kỳ cờ nào hoặc sử dụng bất kỳ biến môi trường nào chúng muốn, mặc dù các lệnh cốt lõi của Caddy hạn chế việc sử dụng chúng.

</aside>


**[Thư viện cốt lõi](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc)**, hoặc "phần cốt lõi" của Caddy, chủ yếu quản lý cấu hình. Nó có thể [`Run()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Run) một cấu hình mới hoặc [`Stop()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Stop) một cấu hình đang chạy. Nó cũng cung cấp các tiện ích, kiểu dữ liệu và giá trị khác nhau để các mô-đun sử dụng.

**Các mô-đun** thực hiện mọi việc khác. Nhiều mô-đun được tích hợp sẵn trong Caddy, được gọi là các _mô-đun tiêu chuẩn_. Đây là những mô-đun được xác định là hữu ích nhất cho hầu hết người dùng.


<aside class="tip">

Đôi khi các thuật ngữ *module*, *plugin*, và *extension* được sử dụng thay thế cho nhau và thường thì điều đó cũng ổn. Về mặt kỹ thuật, tất cả các mô-đun đều là plugin, nhưng không phải tất cả plugin đều là mô-đun. Mô-đun cụ thể là một loại plugin mở rộng [cấu trúc cấu hình](/docs/json/) của Caddy.

</aside>




<a id="caddy-core"></a>
## Cốt lõi của Caddy (Caddy core)

Ở phần cốt lõi, Caddy chỉ đơn thuần tải một cấu hình ban đầu ("config") hoặc, nếu không có cấu hình nào, nó sẽ mở một socket để chấp nhận cấu hình mới sau này.

Một [cấu hình Caddy](/docs/json/) là một tài liệu JSON, với một số trường ở cấp cao nhất:

```json
{
	"admin": {},
	"logging": {},
	"apps": {•••},
	...
}
```

Phần cốt lõi của Caddy biết cách làm việc with một số trường này một cách tự nhiên: 

- [`admin`](/docs/json/admin/) để nó có thể thiết lập [admin API](/docs/api) và quản lý tiến trình
- [`logging`](/docs/json/logging/) để nó có thể [xuất nhật ký](/docs/logging)

Nhưng các trường cấp cao nhất khác (như [`apps`](/docs/json/apps/)) là mờ đục (opaque) đối với phần cốt lõi của Caddy. Trên thực tế, tất cả những gì Caddy biết để làm với các byte trong `apps` là giải mã chúng thành một kiểu interface mà nó có thể gọi hai phương thức trên đó:

1. `Start()`
2. `Stop()`

... và chỉ vậy thôi. Nó gọi `Start()` trên mỗi ứng dụng (app) khi cấu hình được tải và `Stop()` trên mỗi ứng dụng khi cấu hình bị hủy tải.

Khi một mô-đun ứng dụng được khởi động, nó sẽ bắt đầu vòng đời mô-đun của ứng dụng đó.


<aside class="tip">

Nếu bạn là một lập trình viên đang xây dựng các mô-đun Caddy, bạn có thể tìm thấy thông tin tương tự trong hướng dẫn [Mở rộng Caddy](/docs/extending-caddy) guide của chúng tôi, nhưng tập trung nhiều hơn vào mã nguồn.

</aside>


<a id="module-lifecycle"></a>
## Vòng đời mô-đun (Module lifecycle)

Có hai loại mô-đun: _mô-đun máy chủ (host modules)_ và _mô-đun khách (guest modules)_.

**Mô-đun máy chủ** (hoặc mô-đun "cha") là những mô-đun tải các mô-đun khác.

**Mô-đun khách** (hoặc mô-đun "con") là những mô-đun được tải. Tất cả các mô-đun đều là mô-đun khách -- ngay cả các mô-đun ứng dụng.

Các mô-đun được tải, được cung cấp (provisioned) và xác thực, được sử dụng, sau đó được dọn dẹp, theo trình tự sau:

1. Được tải (Loaded)
2. Được cung cấp và xác thực (Provisioned and validated)
3. Được sử dụng (Used)
4. Được dọn dẹp (Cleaned up)

Caddy bắt đầu vòng đời mô-đun khi cấu hình được tải trước tiên bằng cách khởi tạo tất cả các mô-đun ứng dụng đã được cấu hình. Từ đó, nó tiếp tục theo cấp bậc (turtles all the way down) khi mỗi mô-đun ứng dụng thực hiện các bước còn lại.

<a id="load-phase"></a>
### Giai đoạn tải (Load phase)

Tải một mô-đun bao gồm việc giải mã các byte JSON của nó thành một giá trị có kiểu trong bộ nhớ. Đó... cơ bản là vậy. Nó chỉ là giải mã JSON thành một giá trị.

<a id="provision-phase"></a>
### Giai đoạn cung cấp (Provision phase)

Giai đoạn này là nơi hầu hết các công việc thiết lập diễn ra. Tất cả các mô-đun đều có cơ hội tự cung cấp sau khi được tải.

Vì bất kỳ thuộc tính nào từ mã hóa JSON sẽ được giải mã rồi, nên chỉ cần thực hiện thiết lập bổ sung ở đây. Nhiệm vụ phổ biến nhất trong quá trình cung cấp là thiết lập các mô-đun khách. Nói cách khác, việc cung cấp một mô-đun máy chủ cũng dẫn đến việc cung cấp các mô-đun khách của nó, cho đến hết các cấp.

Bạn có thể cảm nhận điều này bằng cách [duyệt qua cấu trúc JSON của Caddy trong tài liệu của chúng tôi](/docs/json/). Bất cứ nơi nào bạn thấy `{•••}` là nơi các mô-đun khách có thể được sử dụng; và khi bạn nhấp vào một cái, bạn có thể tiếp tục khám phá cho đến khi không còn mô-đun khách nào nữa.

Các nhiệm vụ cung cấp phổ biến khác là thiết lập các giá trị nội bộ sẽ được sử dụng trong vòng đời của mô-đun hoặc tiêu chuẩn hóa các đầu vào. Ví dụ, mô-đun [`http.matchers.remote_ip`](/docs/modules/http.matchers.remote_ip) sử dụng giai đoạn cung cấp để phân tích các giá trị CIDR từ các đầu vào chuỗi mà nó nhận được từ JSON. Bằng cách đó, nó không phải làm điều này trong mỗi yêu cầu HTTP và do đó hiệu quả hơn.

Việc xác thực cũng có thể diễn ra trong giai đoạn cung cấp. Nếu cấu hình kết quả của một mô-đun không hợp lệ, một lỗi có thể được trả về tại đây để hủy bỏ toàn bộ quá trình tải cấu hình.

<a id="use-phase"></a>
### Giai đoạn sử dụng (Use phase)

Khi một mô-đun khách được cung cấp và xác thực, nó có thể được sử dụng bởi mô-đun máy chủ của nó. Chính xác điều này có nghĩa là gì tùy thuộc vào từng mô-đun máy chủ.

Mỗi mô-đun có một ID, bao gồm một namespace (không gian tên) và một tên trong không gian tên đó. Ví dụ, [`http.handlers.reverse_proxy`](/docs/modules/http.handlers.reverse_proxy) là một trình xử lý HTTP vì nó nằm trong không gian tên `http.handlers` và tên của nó là `reverse_proxy`. Tất cả các mô-đun trong không gian tên `http.handlers` đều thỏa mãn cùng một interface mà mô-đun máy chủ đã biết. Do đó, ứng dụng `http` biết cách tải và sử dụng các loại mô-đun này.

<a id="cleanup-phase"></a>
### Giai đoạn dọn dẹp (Cleanup phase)

Khi đến lúc một cấu hình phải dừng lại, tất cả các mô-đun sẽ được hủy tải. Nếu một mô-đun đã phân bổ bất kỳ tài nguyên nào cần được giải phóng, nó có cơ hội để thực hiện việc đó trong giai đoạn dọn dẹp.


<a id="plugging-in"></a>
## Cắm vào (Plugging in)

Một mô-đun -- hoặc bất kỳ plugin Caddy nào -- được "cắm vào" Caddy bằng cách thêm một `import` cho gói (package) của mô-đun đó. Bằng cách nhập gói, [mô-đun sẽ tự đăng ký](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule) với cốt lõi Caddy, vì vậy khi tiến trình Caddy bắt đầu, nó sẽ biết từng mô-đun theo tên. Nó thậm chí có thể liên kết giữa các giá trị mô-đun và tên, và ngược lại.


<aside class="tip">

Các plugin có thể được thêm vào mà không cần sửa đổi mã nguồn Caddy. Có các hướng dẫn [trong tệp readme](https://github.com/caddyserver/caddy/#with-version-information-andor-plugins) để thực hiện việc này!

</aside>


<a id="managing-configuration"></a>
## Quản lý cấu hình

Thay đổi cấu hình đang hoạt động của một máy chủ đang chạy (thường được gọi là "reload") có thể rất phức tạp với mức độ đồng thời cao và hàng nghìn tham số mà các máy chủ yêu cầu. Caddy giải quyết vấn đề này một cách thanh lịch bằng cách sử dụng một thiết kế có nhiều lợi ích:

- Không gây gián đoạn cho các dịch vụ đang chạy
- Có thể thay đổi cấu hình ở mức độ chi tiết
- Chỉ yêu cầu một khóa (lock) (trong nền)
- Tất cả các lần nạp lại đều mang tính nguyên tử, nhất quán, cô lập và hầu hết là bền vững ("ACID")
- Trạng thái toàn cục tối thiểu

Bạn có thể [xem video về thiết kế của Caddy 2 tại đây](https://www.youtube.com/watch?v=EhJO8giOqQs).

Việc nạp lại cấu hình hoạt động bằng cách cung cấp các mô-đun mới và nếu tất cả thành công, các mô-đun cũ sẽ được dọn dẹp. Trong một khoảng thời gian ngắn, hai cấu hình sẽ hoạt động cùng một lúc.

Mỗi cấu hình được liên kết với một [ngữ cảnh (context)](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context) giữ tất cả trạng thái mô-đun, vì vậy hầu hết trạng thái không bao giờ thoát khỏi phạm vi của một cấu hình. Đây là tin tốt cho sự chính xác, hiệu suất và sự đơn giản!

Tuy nhiên, đôi khi trạng thái thực sự toàn cục là cần thiết. Ví dụ, reverse proxy có thể theo dõi tình trạng sức khỏe của các upstream của nó; vì chỉ có một trong mỗi upstream trên toàn cầu, sẽ thật tệ nếu nó quên mất chúng mỗi khi có một thay đổi cấu hình nhỏ được thực hiện. May mắn thay, Caddy [cung cấp các cơ sở](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#UsagePool) tương tự như bộ thu gom rác (garbage collector) của một ngôn ngữ lập trình để giữ cho trạng thái toàn cục được gọn gàng.

Một cách tiếp cận rõ ràng đối với các cập nhật cấu hình trực tuyến là đồng bộ hóa quyền truy cập vào từng tham số cấu hình đơn lẻ, ngay cả trong các đường dẫn quan trọng (hot paths). Điều này cực kỳ tệ về mặt hiệu suất và độ phức tạp&mdash;đặc biệt là ở quy mô lớn&mdash;vì vậy Caddy không sử dụng cách tiếp cận này.

Thay vào đó, các cấu hình được coi là các đơn vị nguyên tử, bất biến: hoặc toàn bộ được thay thế, hoặc không có gì được thay đổi. Các [điểm cuối API quản trị (admin API endpoints)](/docs/api)&mdash;cho phép các thay đổi chi tiết bằng cách duyệt vào cấu trúc&mdash;chỉ làm biến đổi một biểu diễn trong bộ nhớ của cấu hình, từ đó một tài liệu cấu hình hoàn toàn mới được tạo ra và tải lên. Cách tiếp cận này có lợi ích to lớn về mặt đơn giản, hiệu suất và tính nhất quán. Vì chỉ có một khóa, Caddy có thể dễ dàng xử lý các lần nạp lại nhanh chóng.
