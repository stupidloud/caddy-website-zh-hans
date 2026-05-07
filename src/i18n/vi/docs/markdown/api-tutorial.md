---
title: "Hướng dẫn sử dụng API"
---

<a id="api-tutorial"></a>
# Hướng dẫn sử dụng API

Hướng dẫn này sẽ cho bạn thấy cách sử dụng [admin API](/docs/api) của Caddy, giúp bạn có thể tự động hóa theo cách lập trình được.

**Mục tiêu:**
- 🔲 Chạy daemon
- 🔲 Cung cấp cấu hình cho Caddy
- 🔲 Kiểm tra cấu hình
- 🔲 Thay thế cấu hình đang hoạt động
- 🔲 Duyệt cấu hình
- 🔲 Sử dụng thẻ `@id`

**Điều kiện tiên quyết:**
- Kỹ năng sử dụng terminal / dòng lệnh cơ bản
- Kinh nghiệm cơ bản về JSON
- `caddy` và `curl` đã được thêm vào PATH của bạn

---

Để bắt đầu Caddy daemon, hãy sử dụng lệnh con `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Chạy daemon</aside>

Lệnh này sẽ chặn (block) mãi mãi, nhưng nó đang làm gì? Hiện tại... không làm gì cả. Theo mặc định, cấu hình ("config") của Caddy là trống. Chúng ta có thể xác minh điều này bằng cách sử dụng [admin API](/docs/api) trong một terminal khác:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Chúng ta có thể làm cho Caddy trở nên hữu ích bằng cách cung cấp cho nó một cấu hình. Một cách để thực hiện việc này là tạo một yêu cầu POST đến endpoint [/load](/docs/api#post-load). Giống như bất kỳ yêu cầu HTTP nào, có nhiều cách để thực hiện việc này, nhưng trong hướng dẫn này, chúng ta sẽ sử dụng `curl`.

<a id="your-first-config"></a>
## Cấu hình đầu tiên của bạn

Để chuẩn bị yêu cầu, chúng ta cần tạo một cấu hình. Cấu hình của Caddy chỉ đơn giản là một [tài liệu JSON](/docs/json/) (hoặc [bất cứ thứ gì có thể chuyển đổi sang JSON](/docs/config-adapters)).

<aside class="tip">
	Các tệp cấu hình không bắt buộc. API cấu hình luôn có thể được sử dụng mà không cần tệp, điều này rất tiện lợi khi tự động hóa mọi thứ. Hướng dẫn này sử dụng một tệp vì nó thuận tiện hơn cho việc chỉnh sửa thủ công.
</aside>

Lưu nội dung sau vào một tệp JSON:

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

Sau đó tải nó lên:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	Đảm bảo bạn không quên ký tự @ trước tên tệp của mình; điều này thông báo cho curl rằng bạn đang gửi một tệp.
</aside>

<aside class="complete">Cung cấp cấu hình cho Caddy</aside>

Chúng ta có thể xác minh rằng Caddy đã áp dụng cấu hình mới của chúng ta bằng một yêu cầu GET khác:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Kiểm tra xem nó có hoạt động hay không bằng cách truy cập [localhost:2015](http://localhost:2015) trong trình duyệt của bạn hoặc sử dụng `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">Kiểm tra cấu hình</aside>

Nếu bạn thấy _Hello, world!_, thì xin chúc mừng -- nó đang hoạt động! Luôn là một ý tưởng tốt để đảm bảo cấu hình của bạn hoạt động như mong đợi, đặc biệt là trước khi triển khai vào môi trường production.

Hãy thay đổi thông điệp chào mừng từ "Hello world!" thành một điều gì đó truyền cảm hứng hơn một chút: "I can do hard things." Thực hiện thay đổi này trong tệp cấu hình của bạn, để đối tượng handler bây giờ trông như thế này:

```json
{
	"handler": "static_response",
	"body": "I can do hard things."
}
```

Lưu tệp cấu hình, sau đó cập nhật cấu hình đang hoạt động của Caddy bằng cách chạy lại chính yêu cầu POST đó:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Thay thế cấu hình đang hoạt động</aside>

Để chắc chắn, hãy xác minh rằng cấu hình đã được cập nhật:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Kiểm tra nó bằng cách làm mới trang trong trình duyệt của bạn (hoặc chạy lại `curl`), và bạn sẽ thấy một thông điệp đầy cảm hứng!


<a id="config-traversal"></a>
## Duyệt cấu hình

Thay vì tải lên toàn bộ tệp cấu hình cho một thay đổi nhỏ, hãy sử dụng một tính năng mạnh mẽ của API Caddy để thực hiện thay đổi mà không cần chạm vào tệp cấu hình của chúng ta.

<aside class="tip">
	Việc thực hiện những thay đổi nhỏ trên các máy chủ production bằng cách thay thế toàn bộ cấu hình như chúng ta đã làm ở trên có thể gây nguy hiểm; nó giống như việc có quyền truy cập root vào hệ thống tệp. API của Caddy cho phép bạn giới hạn phạm vi thay đổi để đảm bảo rằng các phần khác trong cấu hình của bạn không bị thay đổi ngoài ý muốn.
</aside>

Sử dụng đường dẫn của URI yêu cầu, chúng ta có thể duyệt sâu vào cấu trúc cấu hình và chỉ cập nhật chuỗi thông điệp (hãy nhớ cuộn sang phải nếu bị che khuất):

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Work smarter, not harder."'
</code></pre>


<aside class="tip">

Mỗi khi bạn thay đổi cấu hình bằng API, Caddy sẽ lưu một bản sao của cấu hình mới để bạn có thể [**tiếp tục (--resume)** nó sau này](/docs/command-line#caddy-run)!

</aside>


Bạn có thể xác minh rằng nó đã hoạt động bằng một yêu cầu GET tương tự, ví dụ:

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

Bạn sẽ thấy:

```json
[{"handle":[{"body":"Work smarter, not harder.","handler":"static_response"}]}]
```


<aside class="tip">

Bạn có thể sử dụng [lệnh `jq` <img src="/old/resources/images/external-link.svg" class="external-link">](https://stedolan.github.io/jq/) để làm đẹp đầu ra JSON: **`curl ... | jq`**

</aside>


<aside class="complete">Duyệt cấu hình</aside>

**Lưu ý quan trọng:** Điều này có vẻ hiển nhiên, nhưng một khi bạn sử dụng API để thực hiện một thay đổi không có trong tệp cấu hình gốc của mình, tệp cấu hình đó sẽ trở nên lỗi thời. Có một vài cách để xử lý vấn đề này:

- Sử dụng tùy chọn `--resume` của lệnh [caddy run](/docs/command-line#caddy-run) để sử dụng cấu hình hoạt động cuối cùng.
- Đừng trộn lẫn việc sử dụng các tệp cấu hình với các thay đổi thông qua API; hãy chỉ có một nguồn sự thật duy nhất.
- [Xuất cấu hình mới của Caddy](/docs/api#get-configpath) bằng một yêu cầu GET tiếp theo (ít được khuyến khích hơn hai tùy chọn đầu tiên).



<a id="using-in-json"></a>
<a id="using-id-in-json"></a>
## Sử dụng `@id` trong JSON

Duyệt cấu hình chắc chắn là hữu ích, nhưng các đường dẫn hơi dài, bạn có nghĩ vậy không?

Chúng ta có thể đặt cho đối tượng handler của mình một [thẻ `@id`](/docs/api#using-id-in-json) để giúp truy cập dễ dàng hơn:

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

Thao tác này sẽ thêm một thuộc tính vào đối tượng handler của chúng ta: `"@id": "msg"`, vì vậy bây giờ nó trông như thế này:

```json
{
	"@id": "msg",
	"body": "Work smarter, not harder.",
	"handler": "static_response"
}
```


<aside class="tip">

Các thẻ **@id** có thể được đặt trong bất kỳ đối tượng nào và có thể có bất kỳ giá trị nguyên thủy nào (thường là một chuỗi). [Tìm hiểu thêm](/docs/api#using-id-in-json)

</aside>


Sau đó, chúng ta có thể truy cập trực tiếp vào nó:

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

Và bây giờ chúng ta có thể thay đổi thông điệp với một đường dẫn ngắn hơn:

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Some shortcuts are good."'
</code></pre>

Và kiểm tra lại lần nữa:

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete">Sử dụng thẻ <code>@id</code></aside>
