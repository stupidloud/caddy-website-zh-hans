---
title: Phân tích hiệu năng Caddy (Profiling Caddy)
---

Phân tích hiệu năng Caddy
================

Một **program profile** (hồ sơ chương trình) là một bản chụp nhanh về việc sử dụng tài nguyên của một chương trình tại thời điểm thực thi. Các hồ sơ này có thể cực kỳ hữu ích để xác định các khu vực có vấn đề, khắc phục lỗi và sự cố treo máy, cũng như tối ưu hóa mã nguồn.

Caddy sử dụng các công cụ của Go để thu thập hồ sơ, được gọi là [pprof](https://github.com/google/pprof), và nó được tích hợp sẵn trong lệnh `go`.

Các hồ sơ báo cáo về những đối tượng tiêu thụ CPU và bộ nhớ, hiển thị dấu vết ngăn xếp (stack traces) của các goroutine, và giúp theo dõi các lỗi bế tắc (deadlocks) hoặc các cơ chế đồng bộ hóa tranh chấp cao (high-contention synchronization primitives).

Khi báo cáo một số lỗi nhất định trong Caddy, chúng tôi có thể yêu cầu cung cấp một hồ sơ. Bài viết này có thể giúp ích. Nó mô tả cả cách lấy hồ sơ với Caddy và cách sử dụng cũng như diễn giải các hồ sơ pprof kết quả nói chung.


Hai điều cần biết trước khi bắt đầu:

1. **Các hồ sơ Caddy KHÔNG nhạy cảm về bảo mật.** Chúng chứa các thông số kỹ thuật lành tính, không phải nội dung của bộ nhớ. Chúng không cấp quyền truy cập vào hệ thống. Việc chia sẻ chúng là an toàn.
2. **Các hồ sơ rất nhẹ và có thể được thu thập trong môi trường thực tế (production).** Trên thực tế, đây là một phương pháp hay được khuyến nghị cho nhiều người dùng; xem thêm ở phần sau của bài viết này.

<a id="obtaining-profiles"></a>
## Thu thập hồ sơ

Các hồ sơ có sẵn thông qua [giao diện quản trị (admin interface)](/docs/api) tại `/debug/pprof/`. Trên máy đang chạy Caddy, hãy mở nó trong trình duyệt của bạn:

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	Theo mặc định, API quản trị chỉ có thể truy cập được từ máy cục bộ. Nếu chạy từ xa, trong máy ảo (VM) hoặc trong container, hãy xem phần tiếp theo để biết cách truy cập điểm cuối (endpoint) này.
</aside>

Bạn sẽ nhận thấy một bảng đơn giản gồm các số lượng và liên kết, chẳng hạn như:

Số lượng (Count) | Hồ sơ (Profile)
----- | --------------------
79    | allocs
0     | block
0     | cmdline
22    | goroutine
79    | heap
0     | mutex
0     | profile
29    | threadcreate
0     | trace
|     | full goroutine stack dump

Các con số này là một cách thuận tiện để nhanh chóng xác định rò rỉ. Nếu bạn nghi ngờ có rò rỉ, hãy làm mới trang liên tục và bạn sẽ thấy một hoặc nhiều con số đó không ngừng tăng lên. Nếu số lượng heap tăng, đó có thể là rò rỉ bộ nhớ; nếu số lượng goroutine tăng, đó có thể là rò rỉ goroutine.

Nhấp qua các hồ sơ và xem chúng trông như thế nào. Một số hồ sơ có thể trống và điều đó là bình thường trong nhiều trường hợp. Những hồ sơ được sử dụng phổ biến nhất là <b>goroutine</b> (ngăn xếp hàm), <b>heap</b> (bộ nhớ), và <b>profile</b> (CPU). Các hồ sơ khác hữu ích để khắc phục tranh chấp mutex hoặc lỗi bế tắc (deadlocks).

Ở phía dưới, có một mô tả đơn giản về từng hồ sơ:

- **allocs:** Lấy mẫu tất cả các lần cấp phát bộ nhớ trong quá khứ
- **block:** Dấu vết ngăn xếp dẫn đến việc bị chặn (blocking) trên các cơ chế đồng bộ hóa
- **cmdline:** Lời gọi dòng lệnh của chương trình hiện tại
- **goroutine:** Dấu vết ngăn xếp của tất cả các goroutine hiện tại. Sử dụng debug=2 làm tham số truy vấn để xuất theo cùng định dạng với một lỗi panic chưa được khôi phục.
- **heap:** Lấy mẫu các lần cấp phát bộ nhớ của các đối tượng còn sống. Bạn có thể chỉ định tham số GET `gc` để chạy trình thu gom rác (GC) trước khi lấy mẫu heap.
- **mutex:** Dấu vết ngăn xếp của những đối tượng giữ các mutex đang bị tranh chấp
- **profile:** Hồ sơ CPU. Bạn có thể chỉ định thời gian tính bằng giây trong tham số GET `seconds`. Sau khi bạn nhận được tệp hồ sơ, hãy sử dụng lệnh `go tool pprof` để kiểm tra hồ sơ.
- **threadcreate:** Dấu vết ngăn xếp dẫn đến việc tạo các luồng Hệ điều hành mới
- **trace:** Một dấu vết thực thi của chương trình hiện tại. Bạn có thể chỉ định thời gian tính bằng giây trong tham số GET `seconds`. Sau khi bạn nhận được tệp trace, hãy sử dụng lệnh `go tool trace` để kiểm tra dấu vết.

<aside class="tip">

Sự khác biệt giữa "goroutine" và "full goroutine stack dump" nằm ở tham số `?debug=2`: bản kết xuất ngăn xếp đầy đủ giống như kết quả bạn thấy sau một lỗi panic; nó chi tiết hơn và đáng chú ý là nó không gộp các goroutine giống hệt nhau.

</aside>


<a id="downloading-profiles"></a>
### Tải xuống các hồ sơ

Nhấp vào các liên kết trên trang chỉ mục pprof ở trên sẽ cung cấp cho bạn các hồ sơ ở định dạng văn bản. Điều này hữu ích cho việc gỡ lỗi và đó là những gì đội ngũ Caddy ưu tiên vì chúng tôi có thể quét nó để tìm các manh mối rõ ràng mà không cần thêm công cụ.

Nhưng định dạng mặc định thực tế là nhị phân. Các liên kết HTML sẽ thêm tham số truy vấn `?debug=` để định dạng chúng dưới dạng văn bản, ngoại trừ liên kết "profile" (CPU) không có biểu diễn văn bản.

Đây là các tham số truy vấn bạn có thể đặt (từ [tài liệu Go](https://pkg.go.dev/net/http/pprof#hdr-Parameters)):

- **`debug=N` (tất cả các hồ sơ ngoại trừ cpu):** định dạng phản hồi: N = 0: nhị phân (mặc định), N > 0: văn bản thuần túy
- **`gc=N` (hồ sơ heap):** N > 0: chạy một chu kỳ thu gom rác trước khi phân tích hồ sơ
- **`seconds=N` (các hồ sơ allocs, block, goroutine, heap, mutex, threadcreate):** trả về một hồ sơ delta (sự thay đổi)
- **`seconds=N` (các hồ sơ cpu, trace):** phân tích hồ sơ trong khoảng thời gian đã cho

Vì đây là các điểm cuối HTTP, bạn cũng có thể sử dụng bất kỳ ứng dụng khách HTTP nào như curl hoặc wget để tải xuống các hồ sơ.

Sau khi các hồ sơ của bạn được tải xuống, bạn có thể tải chúng lên nhận xét về một vấn đề (issue) trên GitHub hoặc sử dụng một trang web như [pprof.me](https://pprof.me/). Riêng đối với hồ sơ CPU, [flamegraph.com](https://flamegraph.com/) là một lựa chọn khác.


<a id="accessing-remotely"></a>
## Truy cập từ xa

_Nếu bạn đã có thể truy cập API quản trị tại địa phương, hãy bỏ qua phần này._

Theo mặc định, API quản trị của Caddy chỉ có thể truy cập được qua socket loopback. Tuy nhiên, có ít nhất 3 cách để bạn có thể truy cập điểm cuối `/debug/pprof` của Caddy từ xa:

<a id="reverse-proxy-through-your-site"></a>
### Reverse proxy thông qua trang web của bạn

Một lựa chọn dễ dàng là chỉ cần thiết lập proxy ngược (reverse proxy) tới nó từ trang web của bạn:

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

Tất nhiên, điều này sẽ làm cho các hồ sơ có sẵn cho bất kỳ ai có thể kết nối với trang web của bạn. Nếu không muốn điều đó, bạn có thể thêm một số xác thực bằng cách sử dụng mô-đun xác thực HTTP tùy chọn của bạn.

(Đừng quên trình khớp (matcher) `/debug/pprof/*`, nếu không bạn sẽ chuyển tiếp toàn bộ API quản trị!)


### SSH tunnel

Một cách khác là sử dụng SSH tunnel. Đây là một kết nối được mã hóa sử dụng giao thức SSH giữa máy tính của bạn và máy chủ của bạn. Chạy một lệnh như thế này trên máy tính của bạn:

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

Lệnh này tạo một tunnel từ `localhost:8123` (trên máy tính cục bộ của bạn) tới `localhost:2019` trên `example.com`. Hãy đảm bảo thay thế `username`, `example.com`, và các cổng nếu cần thiết.

<aside class="tip">

Lệnh này sẽ chạy ở chế độ nền trước (foreground). Hãy lưu ý rằng nếu bạn cố gắng đưa tiến trình này vào chế độ nền bằng <kbd>Ctrl</kbd>+<kbd>Z</kbd>, nó sẽ tạm dừng tunnel và các kết nối sử dụng tunnel sẽ không thể kết nối được.

</aside>

Sau đó, trong một thiết bị đầu cuối (terminal) khác, bạn có thể chạy `curl` như sau:

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

Bạn có thể tránh việc cần sử dụng `-H "Host: ..."` bằng cách sử dụng cổng `2019` ở cả hai đầu của tunnel (nhưng điều này yêu cầu cổng `2019` chưa được sử dụng trên máy tính của chính bạn, tức là không có Caddy đang chạy cục bộ).

Khi tunnel đang hoạt động, bạn có thể truy cập vào bất kỳ và tất cả API quản trị nào. Nhấn <kbd>Ctrl</kbd>+<kbd>C</kbd> trên lệnh `ssh` để đóng tunnel.

<a id="long-running-tunnel"></a>
#### Tunnel chạy lâu dài

Chạy một tunnel với lệnh trên yêu cầu bạn phải giữ terminal luôn mở. Nếu bạn muốn chạy tunnel ở chế độ nền, bạn có thể bắt đầu tunnel như sau:

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

Lệnh này sẽ bắt đầu ở chế độ nền và tạo một socket điều khiển tại `/tmp/caddy-tunnel.sock`. Sau đó, bạn có thể sử dụng socket điều khiển này để đóng tunnel khi hoàn tất:

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>


<a id="remote-admin-api"></a>
### API quản trị từ xa

Bạn cũng có thể cấu hình API quản trị để chấp nhận các kết nối từ xa đến các ứng dụng khách được ủy quyền.

(CẦN LÀM: Viết bài về vấn đề này.)



<a id="goroutine-profiles"></a>
## Hồ sơ Goroutine

Bản kết xuất (dump) goroutine hữu ích để biết những goroutine nào đang tồn tại và ngăn xếp lệnh gọi của chúng là gì. Nói cách khác, nó cung cấp cho chúng ta ý tưởng về mã hiện đang thực thi hoặc đang bị chặn/chờ đợi.

Nếu bạn nhấp vào "goroutines" hoặc truy cập `/debug/pprof/goroutine?debug=1`, bạn sẽ thấy danh sách các goroutine và ngăn xếp lệnh gọi của chúng. Ví dụ:

```
goroutine profile: total 88
23 @ 0x43e50e 0x436d37 0x46bda5 0x4e1327 0x4e261a 0x4e2608 0x545a65 0x5590c5 0x6b2e9b 0x50ddb8 0x6b307e 0x6b0650 0x6b6918 0x6b6921 0x4b8570 0xb11a05 0xb119d4 0xb12145 0xb1d087 0x4719c1
#	0x46bda4	internal/poll.runtime_pollWait+0x84			runtime/netpoll.go:343
#	0x4e1326	internal/poll.(*pollDesc).wait+0x26			internal/poll/fd_poll_runtime.go:84
#	0x4e2619	internal/poll.(*pollDesc).waitRead+0x279		internal/poll/fd_poll_runtime.go:89
#	0x4e2607	internal/poll.(*FD).Read+0x267				internal/poll/fd_unix.go:164
#	0x545a64	net.(*netFD).Read+0x24					net/fd_posix.go:55
#	0x5590c4	net.(*conn).Read+0x44					net/net.go:179
#	0x6b2e9a	crypto/tls.(*atLeastReader).Read+0x3a			crypto/tls/conn.go:805
#	0x50ddb7	bytes.(*Buffer).ReadFrom+0x97				bytes/buffer.go:211
#	0x6b307d	crypto/tls.(*Conn).readFromUntil+0xdd			crypto/tls/conn.go:827
#	0x6b064f	crypto/tls.(*Conn).readRecordOrCCS+0x24f		crypto/tls/conn.go:625
#	0x6b6917	crypto/tls.(*Conn).readRecord+0x157			crypto/tls/conn.go:587
#	0x6b6920	crypto/tls.(*Conn).Read+0x160				crypto/tls/conn.go:1369
#	0x4b856f	io.ReadAtLeast+0x8f					io/io.go:335
#	0xb11a04	io.ReadFull+0x64					io/io.go:354
#	0xb119d3	golang.org/x/net/http2.readFrameHeader+0x33		golang.org/x/net@v0.14.0/http2/frame.go:237
#	0xb12144	golang.org/x/net/http2.(*Framer).ReadFrame+0x84		golang.org/x/net@v0.14.0/http2/frame.go:498
#	0xb1d086	golang.org/x/net/http2.(*serverConn).readFrames+0x86	golang.org/x/net@v0.14.0/http2/server.go:818

1 @ 0x43e50e 0x44e286 0xafeeb3 0xb0af86 0x5c29fc 0x5c3225 0xb0365b 0xb03650 0x15cb6af 0x43e09b 0x4719c1
#	0xafeeb2	github.com/caddyserver/caddy/v2/cmd.cmdRun+0xcd2					github.com/caddyserver/caddy/v2@v2.7.4/cmd/commandfuncs.go:277
#	0xb0af85	github.com/caddyserver/caddy/v2/cmd.init.1.func2.WrapCommandFuncForCobra.func1+0x25	github.com/caddyserver/caddy/v2@v2.7.4/cmd/cobra.go:126
#	0x5c29fb	github.com/spf13/cobra.(*Command).execute+0x87b						github.com/spf13/cobra@v1.7.0/command.go:940
#	0x5c3224	github.com/spf13/cobra.(*Command).ExecuteC+0x3a4					github.com/spf13/cobra@v1.7.0/command.go:1068
#	0xb0365a	github.com/spf13/cobra.(*Command).Execute+0x5a						github.com/spf13/cobra@v1.7.0/command.go:992
#	0xb0364f	github.com/caddyserver/caddy/v2/cmd.Main+0x4f						github.com/caddyserver/caddy/v2@v2.7.4/cmd/main.go:65
#	0x15cb6ae	main.main+0xe										caddy/main.go:11
#	0x43e09a	runtime.main+0x2ba									runtime/proc.go:267

1 @ 0x43e50e 0x44e9c5 0x8ec085 0x4719c1
#	0x8ec084	github.com/caddyserver/certmagic.(*Cache).maintainAssets+0x304	github.com/caddyserver/certmagic@v0.19.2/maintain.go:67

...
```

Dòng đầu tiên, `goroutine profile: total 88`, cho chúng ta biết những gì chúng ta đang xem và có bao nhiêu goroutine.

Danh sách các goroutine tiếp theo. Chúng được nhóm theo ngăn xếp lệnh gọi của chúng theo thứ tự giảm dần của tần suất.

Một dòng goroutine có cú pháp sau: `<số lượng> @ <các địa chỉ...>`

Dòng bắt đầu bằng số lượng các goroutine có cùng ngăn xếp lệnh gọi được liên kết. Ký hiệu `@` chỉ ra sự bắt đầu của các địa chỉ lệnh gọi hàm, tức là các con trỏ hàm, nơi bắt nguồn goroutine. Mỗi con trỏ là một lệnh gọi hàm, hoặc một khung lệnh gọi (call frame).

Bạn có thể nhận thấy rằng nhiều goroutine của bạn có chung địa chỉ lệnh gọi đầu tiên. Đây là điểm vào hoặc hàm main của chương trình của bạn. Một số goroutine sẽ không bắt nguồn từ đó vì các chương trình có các hàm `init()` khác nhau và thời gian chạy Go cũng có thể tạo ra các goroutine.

Các dòng tiếp theo bắt đầu bằng `#` thực chất chỉ là các nhận xét giúp người đọc dễ hiểu hơn. Chúng chứa dấu vết ngăn xếp (stack trace) hiện tại của goroutine. Phần trên cùng đại diện cho đỉnh của ngăn xếp, tức là dòng mã hiện đang được thực thi. Phần dưới cùng đại diện cho đáy của ngăn xếp, hoặc đoạn mã mà goroutine ban đầu bắt đầu chạy.

Dấu vết ngăn xếp có định dạng sau:

```
<địa chỉ> <gói/hàm>+<offset> <tên tệp>:<dòng>
```

Địa chỉ là con trỏ hàm, sau đó bạn sẽ thấy gói Go và tên hàm (cùng với tên kiểu liên quan nếu đó là một phương thức) và offset lệnh trong hàm. Sau đó, có lẽ là thông tin hữu ích nhất, tên tệp và số dòng, nằm ở cuối cùng.

<a id="full-goroutine-stack-dump"></a>
### Bản kết xuất ngăn xếp goroutine đầy đủ

Nếu chúng ta thay đổi tham số truy vấn thành `?debug=2`, chúng ta sẽ nhận được một bản kết xuất đầy đủ. Điều này bao gồm dấu vết ngăn xếp chi tiết của mọi goroutine và các goroutine giống hệt nhau không bị gộp lại. Kết quả này có thể rất lớn trên các máy chủ bận rộn, nhưng nó là thông tin thú vị!

Hãy xem một cái tương ứng với ngăn xếp lệnh gọi đầu tiên ở trên (đã lược bớt):

```
goroutine 61961905 [IO wait, 1 minutes]:
internal/poll.runtime_pollWait(0x7f9a9a059eb0, 0x72)
	runtime/netpoll.go:343 +0x85
...
golang.org/x/net/http2.(*serverConn).readFrames(0xc001756f00)
	golang.org/x/net@v0.14.0/http2/server.go:818 +0x87
created by golang.org/x/net/http2.(*serverConn).serve in goroutine 61961902
	golang.org/x/net@v0.14.0/http2/server.go:930 +0x56a
```

Mặc dù chi tiết, thông tin hữu ích nhất được cung cấp duy nhất bởi bản kết xuất này là dòng đầu tiên và dòng cuối cùng cho mỗi goroutine.

Dòng đầu tiên chứa số của goroutine (61961905), trạng thái ("IO wait") và thời gian tồn tại ("1 minutes"):

- **Số Goroutine:** Đúng vậy, các goroutine có số hiệu! Nhưng chúng không được tiết lộ trong mã nguồn của chúng ta. Tuy nhiên, những con số này đặc biệt hữu ích trong dấu vết ngăn xếp vì chúng ta có thể thấy goroutine nào đã tạo ra goroutine này (xem ở cuối: "created by ... in goroutine 61961902"). Công cụ hiển thị bên dưới giúp chúng ta vẽ biểu đồ trực quan về điều này.

- **Trạng thái:** Điều này cho chúng ta biết goroutine hiện đang làm gì. Dưới đây là một số trạng thái có thể bạn sẽ thấy:
	- `running`: Đang thực thi mã - tuyệt vời!
	- `IO wait`: Đang đợi mạng. Không tiêu thụ luồng Hệ điều hành vì nó được đặt trên một trình thăm dò mạng không bị chặn (non-blocking network poller).
	- `sleep`: Tất cả chúng ta đều cần ngủ nhiều hơn.
	- `select`: Bị chặn trên một lệnh select; đang chờ một trường hợp (case) có sẵn.
	- `select (no cases):` Bị chặn cụ thể trên một lệnh select trống `select {}`. Caddy sử dụng một cái trong hàm main của nó để duy trì hoạt động vì việc tắt máy được khởi tạo từ các goroutine khác.
	- `chan receive`: Bị chặn khi nhận dữ liệu từ channel (`<-ch`).
	- `semacquire`: Đang đợi để nhận một semaphore (cơ chế đồng bộ hóa cấp thấp).
	- `syscall`: Đang thực thi một lệnh gọi hệ thống. Tiêu thụ một luồng Hệ điều hành.

- **Thời gian tồn tại:** Goroutine đã tồn tại được bao lâu. Hữu ích để tìm các lỗi như rò rỉ goroutine. Ví dụ: nếu chúng ta mong đợi tất cả các kết nối mạng sẽ đóng sau vài phút, điều đó có nghĩa là gì khi chúng ta thấy rất nhiều goroutine netconn tồn tại trong nhiều giờ?

<a id="interpreting-goroutine-dumps"></a>
### Giải thích các bản kết xuất goroutine

Nếu không nhìn vào mã nguồn, chúng ta có thể biết được điều gì về goroutine ở trên?

Nó được tạo ra chỉ khoảng một phút trước, đang chờ dữ liệu qua một socket mạng và số hiệu goroutine của nó khá lớn (61961905).

Từ bản kết xuất đầu tiên (debug=1), chúng ta biết ngăn xếp lệnh gọi của nó được thực thi tương đối thường xuyên và số lượng goroutine lớn kết hợp với thời gian ngắn cho thấy đã có hàng chục triệu goroutine tồn tại trong thời gian tương đối ngắn này. Nó nằm trong một hàm gọi là `pollWait` và lịch sử lệnh gọi của nó bao gồm việc đọc các khung hình (frames) HTTP/2 từ một kết nối mạng được mã hóa sử dụng TLS.

Vì vậy, chúng ta có thể suy luận rằng goroutine này đang phục vụ một yêu cầu HTTP/2! Nó đang chờ dữ liệu từ khách hàng. Hơn nữa, chúng ta biết rằng goroutine đã tạo ra nó không phải là một trong những goroutine đầu tiên của tiến trình vì nó cũng có số hiệu cao; việc tìm thấy goroutine đó trong bản kết xuất cho thấy nó được tạo ra để xử lý một luồng (stream) HTTP/2 mới trong một yêu cầu hiện có. Ngược lại, các goroutine khác có số hiệu cao có thể được tạo ra bởi một goroutine có số hiệu thấp (chẳng hạn như 32), cho thấy một kết nối hoàn toàn mới vừa được thực hiện từ lệnh gọi `Accept()` từ socket.

Mỗi chương trình đều khác nhau, nhưng khi gỡ lỗi Caddy, những quy luật này thường đúng.

<a id="memory-profiles"></a>
## Hồ sơ Bộ nhớ (Memory profiles)

Các hồ sơ bộ nhớ (hoặc heap) theo dõi các lần cấp phát heap, vốn là những đối tượng tiêu thụ bộ nhớ chính trên hệ thống. Các lần cấp phát cũng thường là nguyên nhân gây ra các vấn đề về hiệu suất vì việc cấp phát bộ nhớ yêu cầu các lệnh gọi hệ thống, vốn có thể diễn ra chậm.

Các hồ sơ heap trông tương tự như các hồ sơ goroutine về mọi mặt, ngoại trừ phần đầu của dòng đầu tiên. Đây là một ví dụ:

```
0: 0 [1: 4096] @ 0xb1fc05 0xb1fc4d 0x48d8d1 0xb1fce6 0xb184c7 0xb1bc8e 0xb41653 0xb4105c 0xb4151d 0xb23b14 0x4719c1
#	0xb1fc04	bufio.NewWriterSize+0x24					bufio/bufio.go:599
#	0xb1fc4c	golang.org/x/net/http2.glob..func8+0x6c				golang.org/x/net@v0.17.0/http2/http2.go:263
#	0x48d8d0	sync.(*Pool).Get+0xb0						sync/pool.go:151
#	0xb1fce5	golang.org/x/net/http2.(*bufferedWriter).Write+0x45		golang.org/x/net@v0.17.0/http2/http2.go:276
#	0xb184c6	golang.org/x/net/http2.(*Framer).endWrite+0xc6			golang.org/x/net@v0.17.0/http2/frame.go:371
#	0xb1bc8d	golang.org/x/net/http2.(*Framer).WriteHeaders+0x48d		golang.org/x/net@v0.17.0/http2/frame.go:1131
#	0xb41652	golang.org/x/net/http2.(*writeResHeaders).writeHeaderBlock+0xd2	golang.org/x/net@v0.17.0/http2/write.go:239
#	0xb4105b	golang.org/x/net/http2.splitHeaderBlock+0xbb			golang.org/x/net@v0.17.0/http2/write.go:169
#	0xb4151c	golang.org/x/net/http2.(*writeResHeaders).writeFrame+0x1dc	golang.org/x/net@v0.17.0/http2/write.go:234
<a id="0xb23b13golangorgxnethttp2serverconnwriteframeasync0x73golangorgxnetv0170http2servergo851"></a>
#	0xb23b13	golang.org/x/net/http2.(*serverConn).writeFrameAsync+0x73	golang.org/x/net@v0.14.0/http2/server.go:851
```

Định dạng dòng đầu tiên như sau:

```
<đối tượng còn sống> <bộ nhớ còn sống> [<lần cấp phát>: <bộ nhớ cấp phát>] @ <các địa chỉ...>
```

Trong ví dụ trên, chúng ta có một lần cấp phát duy nhất được thực hiện bởi `bufio.NewWriterSize()` nhưng hiện tại không có đối tượng nào còn sống từ ngăn xếp lệnh gọi này.

Điều thú vị là chúng ta có thể suy luận từ ngăn xếp lệnh gọi đó rằng gói http2 đã sử dụng một vùng đệm (pool) 4 KB để ghi (các) khung HTTP/2 cho khách hàng. Bạn sẽ thường thấy các đối tượng được đưa vào vùng đệm (pooled objects) trong các hồ sơ bộ nhớ Go nếu các đường dẫn quan trọng (hot paths) đã được tối ưu hóa để tái sử dụng các lần cấp phát. Điều này giúp giảm bớt các lần cấp phát mới và hồ sơ heap có thể giúp bạn biết liệu vùng đệm đó có đang được sử dụng đúng cách hay không!

<a id="cpu-profiles"></a>
## Hồ sơ CPU (CPU profiles)

Hồ sơ CPU giúp bạn hiểu chương trình Go đang dành phần lớn thời gian đã lên lịch ở đâu trên bộ vi xử lý.

Tuy nhiên, không có dạng văn bản thuần túy cho những hồ sơ này, vì vậy trong phần tiếp theo, chúng ta sẽ sử dụng các lệnh `go tool pprof` để giúp đọc chúng.

Để tải xuống hồ sơ CPU, hãy gửi yêu cầu tới `/debug/pprof/profile?seconds=N`, trong đó N là số giây bạn muốn thu thập hồ sơ. Trong quá trình thu thập hồ sơ CPU, hiệu suất chương trình có thể bị ảnh hưởng nhẹ. (Các hồ sơ khác hầu như không ảnh hưởng đến hiệu suất.)

Khi hoàn tất, nó sẽ tải xuống một tệp nhị phân, được đặt tên phù hợp là `profile`. Sau đó, chúng ta cần kiểm tra nó.

<a id="go-tool-pprof"></a>
## `go tool pprof`

Chúng ta sẽ sử dụng trình phân tích hồ sơ tích hợp sẵn của Go để đọc hồ sơ CPU làm ví dụ, nhưng bạn có thể sử dụng nó với bất kỳ loại hồ sơ nào.

Chạy lệnh này (thay thế "profile" bằng đường dẫn tệp thực tế nếu khác), lệnh này sẽ mở một dấu nhắc tương tác:

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">

Bạn có thể sử dụng lệnh này để kiểm tra bất kỳ loại hồ sơ nào, không chỉ hồ sơ CPU. Các nguyên tắc là tương tự cho các hồ sơ khác và các khái niệm cũng tương đồng.

</aside>

Đây là điều mà bạn có thể khám phá. Nhập `help` để nhận danh sách các lệnh và `o` sẽ hiển thị cho bạn các tùy chọn hiện tại. Và nếu bạn nhập `help <lệnh>`, bạn có thể nhận được thông tin về một lệnh cụ thể.

Có rất nhiều lệnh, nhưng một số lệnh phổ biến là:

- `top`: Hiển thị những gì tiêu thụ CPU nhiều nhất. Bạn có thể thêm một con số như `top 20` để xem nhiều hơn, hoặc một regex để "tập trung" (focus) vào hoặc bỏ qua một số mục nhất định.
- `web`: Mở biểu đồ lệnh gọi trong trình duyệt web của bạn. Đây là một cách tuyệt vời để xem trực quan việc sử dụng CPU.
- `svg`: Tạo hình ảnh SVG của biểu đồ lệnh gọi. Nó giống như lệnh `web` ngoại trừ việc nó không mở trình duyệt web của bạn và tệp SVG được lưu cục bộ.
- `tree`: Một chế độ xem dạng bảng của ngăn xếp lệnh gọi.

Hãy bắt đầu với `top`. Chúng ta thấy kết quả như sau:

```
(pprof) top
Showing nodes accounting for 38.36s, 54.71% of 70.11s total
Dropped 785 nodes (cum <= 0.35s)
Showing top 10 nodes out of 196
      flat  flat%   sum%        cum   cum%
    10.97s 15.65% 15.65%     10.97s 15.65%  runtime/internal/syscall.Syscall6
     6.59s  9.40% 25.05%     36.65s 52.27%  runtime.gcDrain
     5.03s  7.17% 32.22%      5.34s  7.62%  runtime.(*lfstack).pop (inline)
     3.69s  5.26% 37.48%     11.02s 15.72%  runtime.scanobject
     2.42s  3.45% 40.94%      2.42s  3.45%  runtime.(*lfstack).push
     2.26s  3.22% 44.16%      2.30s  3.28%  runtime.pageIndexOf (inline)
     2.11s  3.01% 47.17%      2.56s  3.65%  runtime.findObject
     2.03s  2.90% 50.06%      2.03s  2.90%  runtime.markBits.isMarked (inline)
     1.69s  2.41% 52.47%      1.69s  2.41%  runtime.memclrNoHeapPointers
     1.57s  2.24% 54.71%      1.57s  2.24%  runtime.epollwait
```

10 đối tượng tiêu thụ CPU hàng đầu đều nằm trong Go runtime -- cụ thể là rất nhiều hoạt động thu gom rác (hãy nhớ rằng các lệnh gọi hệ thống được sử dụng để giải phóng và cấp phát bộ nhớ). Đây là một gợi ý rằng chúng ta có thể giảm bớt các lần cấp phát để cải thiện hiệu suất và một hồ sơ heap sẽ rất đáng giá.

Được rồi, nhưng nếu chúng ta muốn xem mức sử dụng CPU từ mã nguồn của chính mình thì sao? Chúng ta có thể bỏ qua các mẫu chứa "runtime" như thế này:

```
(pprof) top -runtime  
Active filters:
   ignore=runtime
Showing nodes accounting for 0.92s, 1.31% of 70.11s total
Dropped 160 nodes (cum <= 0.35s)
Showing top 10 nodes out of 243
      flat  flat%   sum%        cum   cum%
     0.17s  0.24%  0.24%      0.28s   0.4%  sync.(*Pool).getSlow
     0.11s  0.16%   0.4%      0.11s  0.16%  github.com/prometheus/client_golang/prometheus.(*histogram).observe (inline)
     0.10s  0.14%  0.54%      0.23s  0.33%  github.com/prometheus/client_golang/prometheus.(*MetricVec).hashLabels
     0.10s  0.14%  0.68%      0.12s  0.17%  net/textproto.CanonicalMIMEHeaderKey
     0.10s  0.14%  0.83%      0.10s  0.14%  sync.(*poolChain).popTail
     0.08s  0.11%  0.94%      0.26s  0.37%  github.com/prometheus/client_golang/prometheus.(*histogram).Observe
     0.07s   0.1%  1.04%      0.07s   0.1%  internal/poll.(*fdMutex).rwlock
     0.07s   0.1%  1.14%      0.10s  0.14%  path/filepath.Clean
     0.06s 0.086%  1.23%      0.06s 0.086%  context.value
     0.06s 0.086%  1.31%      0.06s 0.086%  go.uber.org/zap/buffer.(*Buffer).AppendByte
```

Rõ ràng là các số liệu (metrics) Prometheus là một đối tượng tiêu thụ hàng đầu khác, nhưng bạn sẽ nhận thấy rằng về tổng thể, chúng ít hơn nhiều bậc so với hoạt động GC ở trên. Sự khác biệt rõ rệt gợi ý rằng chúng ta nên tập trung vào việc giảm bớt GC.

<aside class="tip">

Điều quan trọng cần lưu ý là các hồ sơ CPU lấy các phép đo từ việc lấy mẫu gián đoạn và các mẫu sẽ không bao giờ được thu thập thường xuyên hơn tỷ lệ lấy mẫu, theo mặc định là 10ms. Đó là lý do tại sao bạn sẽ không thấy bất kỳ thời gian tích lũy nào ngắn hơn 10ms (chúng có thể ngắn hơn, nhưng được làm tròn lên). Để có thời gian cụ thể hơn, bạn có thể thực hiện trace thực thi (execution trace), vốn không sử dụng lấy mẫu. (CẦN LÀM: Thêm phần về tracing.)

</aside>

Hãy sử dụng lệnh `q` để thoát hồ sơ này và sử dụng cùng lệnh đó trên hồ sơ heap:

```
(pprof) top
Showing nodes accounting for 22259.07kB, 81.30% of 27380.04kB total
Showing top 10 nodes out of 102
      flat  flat%   sum%        cum   cum%
   12300kB 44.92% 44.92%    12300kB 44.92%  runtime.allocm
 2570.01kB  9.39% 54.31%  2570.01kB  9.39%  bufio.NewReaderSize
 2048.81kB  7.48% 61.79%  2048.81kB  7.48%  runtime.malg
 1542.01kB  5.63% 67.42%  1542.01kB  5.63%  bufio.NewWriterSize
 ...
 ```

Đúng rồi. Gần một nửa bộ nhớ được cấp phát nghiêm ngặt cho các bộ đệm đọc và ghi từ việc chúng ta sử dụng gói bufio. Do đó, chúng ta có thể suy luận rằng việc tối ưu hóa mã của chúng ta để giảm bớt việc đệm dữ liệu sẽ rất có lợi. ([Bản vá liên quan trong Caddy](https://github.com/caddyserver/caddy/pull/4978) đã thực hiện chính xác điều đó).

<a id="visualizations"></a>
### Trực quan hóa

Nếu thay vào đó chúng ta chạy các lệnh `svg` hoặc `web`, chúng ta sẽ nhận được một hình ảnh trực quan của hồ sơ:

![CPU profile visualization](/old/resources/images/profile.png)

Đây là một hồ sơ CPU nhưng các biểu đồ tương tự cũng có sẵn cho các loại hồ sơ khác.

To learn how to read these graphs, read [the pprof documentation](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph).


<a id="diffing-profiles"></a>
### So sánh sự khác biệt (Diffing profiles)

Sau khi bạn thực hiện thay đổi mã, bạn có thể so sánh trạng thái trước và sau bằng cách sử dụng phân tích sự khác biệt ("diff"). Đây là một bản diff của heap:

<pre><code class="cmd bash">go tool pprof -diff_base=before.prof after.prof
File: caddy
Type: inuse_space
Time: Aug 29, 2022 at 1:21am (MDT)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) top
Showing nodes accounting for -26.97MB, 49.32% of 54.68MB total
Dropped 10 nodes (cum <= 0.27MB)
Showing top 10 nodes out of 137
      flat  flat%   sum%        cum   cum%
  -27.04MB 49.45% 49.45%   -27.04MB 49.45%  bufio.NewWriterSize
      -2MB  3.66% 53.11%       -2MB  3.66%  runtime.allocm
    1.06MB  1.93% 51.18%     1.06MB  1.93%  github.com/yuin/goldmark/util.init
    1.03MB  1.89% 49.29%     1.03MB  1.89%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.glob..func2
       1MB  1.84% 47.46%        1MB  1.84%  bufio.NewReaderSize
      -1MB  1.83% 49.29%       -1MB  1.83%  runtime.malg
       1MB  1.83% 47.46%        1MB  1.83%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.cloneRequest
      -1MB  1.83% 49.29%       -1MB  1.83%  net/http.(*Server).newConn
   -0.55MB  1.00% 50.29%    -0.55MB  1.00%  html.populateMaps
    0.53MB  0.97% 49.32%     0.53MB  0.97%  github.com/alecthomas/chroma.TypeRemappingLexer</code></pre>

Như bạn có thể thấy, chúng ta đã giảm cấp phát bộ nhớ xuống còn khoảng một nửa!

Các bản diff cũng có thể được trực quan hóa:

![CPU profile visualization](/old/resources/images/profile-diff.png)

Điều này giúp thấy rõ cách thức các thay đổi ảnh hưởng đến hiệu suất của một số phần nhất định của chương trình.

<a id="further-reading"></a>
## Tìm hiểu thêm

Có rất nhiều điều cần nắm vững về phân tích hiệu năng chương trình, và chúng ta mới chỉ lướt qua bề mặt.

Để thực sự trở thành một chuyên gia trong việc "phân tích hiệu năng", hãy cân nhắc các tài nguyên sau:

- [Tài liệu pprof](https://github.com/google/pprof/blob/main/doc/README.md)
- [Một trường hợp sử dụng thực tế của hồ sơ với Caddy](https://github.com/caddyserver/caddy/pull/4978)
- [Hiệu suất trên Go wiki](https://github.com/golang/go/wiki/Performance)
- [Gói `net/http/pprof`](https://pkg.go.dev/net/http/pprof)
