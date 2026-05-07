---
title: "Bắt đầu"
---

<a id="getting-started"></a>
# Bắt đầu

Chào mừng bạn đến với Caddy! Hướng dẫn này sẽ khám phá những kiến thức cơ bản về cách sử dụng Caddy và giúp bạn làm quen với nó ở mức độ tổng quát.

**Mục tiêu:**
- 🔲 Chạy daemon
- 🔲 Thử nghiệm API
- 🔲 Cung cấp cấu hình cho Caddy
- 🔲 Kiểm tra cấu hình
- 🔲 Tạo một Caddyfile
- 🔲 Sử dụng bộ chuyển đổi cấu hình (config adapter)
- 🔲 Bắt đầu với một cấu hình ban đầu
- 🔲 So sánh JSON và Caddyfile
- 🔲 So sánh API và các tệp cấu hình
- 🔲 Chạy dưới nền
- 🔲 Tải lại cấu hình không gây gián đoạn (zero-downtime)

**Điều kiện tiên quyết:**
- Kỹ năng sử dụng terminal / dòng lệnh cơ bản
- Kỹ năng sử dụng trình soạn thảo văn bản cơ bản
- `caddy` và `curl` trong PATH của bạn

---

**Nếu bạn [đã cài đặt Caddy](/docs/install) từ một trình quản lý gói, Caddy có thể đã đang chạy như một dịch vụ. Nếu vậy, vui lòng dừng dịch vụ trước khi thực hiện hướng dẫn này.**

Hãy bắt đầu bằng cách chạy nó:

<pre><code class="cmd bash">caddy</code></pre>

Rất tiếc; nếu không có lệnh con, lệnh `caddy` chỉ hiển thị văn bản trợ giúp. Bạn có thể sử dụng lệnh này bất cứ khi nào bạn quên việc cần làm.

Để bắt đầu Caddy như một daemon, hãy sử dụng lệnh con `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Chạy daemon</aside>

Lệnh này sẽ chặn terminal mãi mãi, nhưng nó đang làm gì? Hiện tại... không có gì cả. Theo mặc định, cấu hình của Caddy ("config") là trống. Chúng ta có thể xác minh điều này bằng cách sử dụng [admin API](/docs/api) trong một terminal khác:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

Đây **không phải** là trang web của bạn: điểm cuối quản trị (administration endpoint) tại localhost:2019 được sử dụng để điều khiển Caddy và bị giới hạn ở localhost theo mặc định.

</aside>


<aside class="complete">Thử nghiệm API</aside>

Chúng ta có thể làm cho Caddy trở nên hữu ích bằng cách cung cấp cho nó một cấu hình. Điều này có thể được thực hiện theo nhiều cách, nhưng chúng ta sẽ bắt đầu bằng cách thực hiện một yêu cầu POST tới điểm cuối [/load](/docs/api#post-load) bằng `curl` trong phần tiếp theo.



<a id="your-first-config"></a>
## Cấu hình đầu tiên của bạn

Để chuẩn bị yêu cầu, chúng ta cần tạo một cấu hình. Về cốt lõi, cấu hình của Caddy chỉ đơn giản là một [tài liệu JSON](/docs/json/).

Lưu nội dung này vào một tệp JSON (ví dụ: `caddy.json`):

```json
{
	"apps": {
		"http": {
			"servers": {
				"example": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

<aside class="tip">

Bạn không nhất thiết phải sử dụng các tệp cấu hình, nhưng chúng ta sẽ sử dụng chúng trong hướng dẫn này. [Admin API](/docs/api) của Caddy được thiết kế để sử dụng bởi các chương trình hoặc tập lệnh khác.

</aside>


Sau đó tải nó lên:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Cung cấp cấu hình cho Caddy</aside>

Chúng ta có thể xác minh rằng Caddy đã áp dụng cấu hình mới bằng một yêu cầu GET khác:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Kiểm tra xem nó có hoạt động không bằng cách truy cập [localhost:2015](http://localhost:2015) trong trình duyệt của bạn hoặc sử dụng `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Nếu bạn thấy _Hello, world!_, thì chúc mừng -- nó đang hoạt động! Luôn luôn là một ý hay khi đảm bảo cấu hình của bạn hoạt động như mong đợi, đặc biệt là trước khi triển khai vào môi trường thực tế (production).

<aside class="complete">Kiểm tra cấu hình</aside>


<a id="your-first-caddyfile"></a>
## Caddyfile đầu tiên của bạn

Đó là _một khối lượng công việc kha khá_ chỉ để có Hello World.

Một cách khác để cấu hình Caddy là sử dụng [**Caddyfile**](/docs/caddyfile). Cùng một cấu hình mà chúng ta đã viết bằng JSON ở trên có thể được diễn đạt đơn giản như sau:

```caddy
:2015

respond "Hello, world!"
```


Lưu nội dung đó vào một tệp có tên `Caddyfile` (không có phần mở rộng) trong thư mục hiện tại.

<aside class="complete">Tạo một Caddyfile</aside>

Dừng Caddy nếu nó đang chạy (<kbd>Ctrl</kbd>+<kbd>C</kbd>), sau đó chạy:

<pre><code class="cmd bash">caddy adapt</code></pre>

Or if you stored the Caddyfile somewhere else or named it something other than `Caddyfile`:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile</code></pre>

Bạn sẽ thấy đầu ra JSON! Điều gì đã xảy ra ở đây?

Chúng ta vừa sử dụng một [_bộ chuyển đổi cấu hình_](/docs/config-adapters) để chuyển đổi Caddyfile của mình sang cấu trúc JSON gốc của Caddy.

<aside class="complete">Sử dụng bộ chuyển đổi cấu hình (config adapter)</aside>

Mặc dù chúng ta có thể lấy đầu ra đó và thực hiện một yêu cầu API khác, chúng ta có thể bỏ qua tất cả các bước đó vì lệnh `caddy` có thể làm điều đó cho chúng ta. Nếu có một tệp mang tên Caddyfile trong thư mục hiện tại và không có cấu hình nào khác được chỉ định, Caddy sẽ tải Caddyfile đó, chuyển đổi nó cho chúng ta và chạy nó ngay lập tức.

Bây giờ đã có một Caddyfile trong thư mục hiện tại, hãy thực hiện lại lệnh `caddy run`:

<pre><code class="cmd bash">caddy run</code></pre>

Hoặc nếu Caddyfile của bạn ở một nơi khác:

<pre><code class="cmd bash">caddy run --config /path/to/Caddyfile</code></pre>

(Nếu nó được đặt tên là một thứ gì đó khác không bắt đầu bằng \"Caddyfile\", bạn sẽ cần chỉ định `--adapter caddyfile`.)

Bây giờ bạn có thể thử tải lại trang web của mình và bạn sẽ thấy nó đang hoạt động!

<aside class="complete">Bắt đầu với một cấu hình ban đầu</aside>

Như bạn có thể thấy, có một số cách bạn có thể bắt đầu Caddy với một cấu hình ban đầu:

- Một tệp có tên Caddyfile trong thư mục hiện tại
- Cờ `--config` (tùy chọn với cờ `--adapter`)
- Cờ `--resume` (nếu một cấu hình đã được tải trước đó)


<a id="json-vs-caddyfile"></a>
## JSON so với Caddyfile

Bây giờ bạn đã biết rằng Caddyfile chỉ được chuyển đổi sang JSON cho bạn.

Caddyfile có vẻ dễ dàng hơn JSON, nhưng bạn có nên luôn luôn sử dụng nó không? Có những ưu và nhược điểm đối với mỗi cách tiếp cận. Câu trả lời phụ thuộc vào yêu cầu và trường hợp sử dụng của bạn.

JSON | Caddyfile
-----|----------
Dễ dàng tạo ra | Dễ dàng viết thủ công
Dễ dàng lập trình | Khó tự động hóa
Khả năng diễn đạt cực cao | Khả năng diễn đạt vừa phải
Đầy đủ các chức năng của Caddy | Hầu hết các chức năng của Caddy
Cho phép duyệt cấu hình | Không thể duyệt trong Caddyfile
Thay đổi cấu hình từng phần | Chỉ thay đổi toàn bộ cấu hình
Có thể được xuất ra | Không thể được xuất ra
Tương thích với tất cả các điểm cuối API | Tương thích với một số điểm cuối API
Tài liệu được tạo tự động | Tài liệu được viết tay
Phổ biến | Chuyên biệt
Hiệu quả hơn | Tính toán nhiều hơn
Hơi nhàm chán | Hơi thú vị
**Tìm hiểu thêm: [Cấu trúc JSON](/docs/json/)** | **Tìm hiểu thêm: [Tài liệu Caddyfile](/docs/caddyfile)**

Bạn sẽ cần quyết định cái nào là tốt nhất cho trường hợp sử dụng của mình.

Điều quan trọng cần lưu ý là cả JSON và Caddyfile (và [bất kỳ bộ chuyển đổi cấu hình nào khác được hỗ trợ](/docs/config-adapters)) đều có thể được sử dụng với [API của Caddy](/docs/api). Tuy nhiên, bạn sẽ có được đầy đủ các chức năng và tính năng API của Caddy nếu bạn sử dụng JSON. Nếu sử dụng bộ chuyển đổi cấu hình, cách duy nhất để tải hoặc thay đổi cấu hình bằng API là điểm cuối [/load](/docs/api#post-load).

<aside class="complete">So sánh JSON và Caddyfile</aside>


<a id="api-vs-config-files"></a>
## API so với các tệp cấu hình

<aside class="tip">

Bên dưới lớp vỏ, ngay cả các tệp cấu hình cũng đi qua các điểm cuối API của Caddy; lệnh `caddy` chỉ bao bọc các cuộc gọi API đó cho bạn.

</aside>


Bạn cũng sẽ muốn quyết định xem quy trình làm việc của mình dựa trên API hay CLI. (Bạn _có thể_ sử dụng cả API và các tệp cấu hình trên cùng một máy chủ, nhưng chúng tôi không khuyến nghị điều đó: tốt nhất là nên có một nguồn sự thật duy nhất.)

API | Các tệp cấu hình
----|-------------
Thay đổi cấu hình bằng các yêu cầu HTTP | Thay đổi cấu hình bằng các lệnh shell
Dễ dàng mở rộng | Khó mở rộng
Khó quản lý thủ công | Dễ dàng quản lý thủ công
Thực sự thú vị | Cũng thú vị
**Tìm hiểu thêm: [Hướng dẫn API](/docs/api-tutorial)** | **Tìm hiểu thêm: [Hướng dẫn Caddyfile](/docs/caddyfile-tutorial)**

<aside class="tip">
	Việc quản lý thủ công cấu hình của máy chủ bằng API là hoàn toàn có thể thực hiện được với các công cụ phù hợp, ví dụ: bất kỳ ứng dụng REST client nào.
</aside>

Việc lựa chọn quy trình làm việc API hay tệp cấu hình là độc lập với việc sử dụng các bộ chuyển đổi cấu hình: bạn có thể sử dụng JSON nhưng lưu trữ nó trong một tệp và sử dụng giao diện dòng lệnh; ngược lại, bạn cũng có thể sử dụng Caddyfile với API.

Nhưng hầu hết mọi người sẽ sử dụng kết hợp JSON+API hoặc Caddyfile+CLI.

Như bạn có thể thấy, Caddy phù hợp với rất nhiều trường hợp sử dụng và triển khai khác nhau!

<aside class="complete">So sánh API và các tệp cấu hình</aside>



<a id="start-stop-run"></a>
## Bắt đầu, dừng, chạy

Vì Caddy là một máy chủ, nó chạy vô thời hạn. Điều đó có nghĩa là terminal của bạn sẽ không được giải phóng sau khi bạn thực hiện lệnh `caddy run` cho đến khi tiến trình bị chấm dứt (thường là bằng <kbd>Ctrl</kbd>+<kbd>C</kbd>).

Mặc dù `caddy run` là phổ biến nhất và thường được khuyến nghị (đặc biệt là khi tạo một dịch vụ hệ thống!), bạn có thể thay thế bằng cách sử dụng `caddy start` để bắt đầu Caddy và cho nó chạy dưới nền:

<pre><code class="cmd bash">caddy start</code></pre>

Điều này sẽ cho phép bạn sử dụng lại terminal của mình, điều này thuận tiện trong một số môi trường headless tương tác.

Sau đó, bạn sẽ phải tự mình dừng tiến trình, vì <kbd>Ctrl</kbd>+<kbd>C</kbd> sẽ không dừng nó cho bạn:

<pre><code class="cmd bash">caddy stop</code></pre>

Hoặc sử dụng [điểm cuối /stop](/docs/api#post-stop) của API.

<aside class="complete">Chạy dưới nền</aside>


<a id="reloading-config"></a>
## Tải lại cấu hình

Máy chủ của bạn có thể thực hiện việc tải lại/thay đổi cấu hình không gây gián đoạn (zero-downtime).

Tất cả các [điểm cuối API](/docs/api) thực hiện tải hoặc thay đổi cấu hình đều diễn ra êm đẹp mà không gây gián đoạn.

Tuy nhiên, khi sử dụng dòng lệnh, bạn có thể muốn sử dụng <kbd>Ctrl</kbd>+<kbd>C</kbd> để dừng máy chủ và sau đó khởi động lại nó để áp dụng cấu hình mới. Đừng làm điều này: việc dừng và khởi động máy chủ là độc lập với việc thay đổi cấu hình, và sẽ dẫn đến thời gian chết (downtime).

<aside class="tip">
	Dừng máy chủ của bạn sẽ khiến máy chủ ngừng hoạt động.
</aside>

Thay đổi cấu hình một cách êm đẹp bằng cách sử dụng lệnh [`caddy reload`](/docs/command-line#caddy-reload):

<pre><code class="cmd bash">caddy reload</code></pre>

Lệnh này thực sự chỉ sử dụng API bên dưới. Nó sẽ tải và nếu cần thiết, chuyển đổi tệp cấu hình của bạn sang JSON, sau đó thay thế cấu hình đang hoạt động một cách êm đẹp mà không gây gián đoạn.

Nếu có bất kỳ lỗi nào khi tải cấu hình mới, Caddy sẽ khôi phục lại cấu hình hoạt động gần nhất.

<aside class="tip">
	Về mặt kỹ thuật, cấu hình mới được khởi động trước khi cấu hình cũ bị dừng, vì vậy trong một thời gian ngắn, cả hai cấu hình đều đang chạy! Nếu cấu hình mới thất bại, nó sẽ hủy bỏ với một lỗi, trong khi cấu hình cũ đơn giản là không bị dừng.
</aside>

<aside class="complete">Tải lại cấu hình không gây gián đoạn (zero-downtime)</aside>
