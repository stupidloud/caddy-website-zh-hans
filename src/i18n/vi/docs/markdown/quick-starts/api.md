---
title: Bắt đầu nhanh với API
---

<a id="api-quick-start"></a>
# Bắt đầu nhanh với API

**Điều kiện tiên quyết:**
- Kỹ năng cơ bản về terminal / dòng lệnh
- `caddy` và `curl` trong PATH của bạn

---

Đầu tiên, hãy khởi động Caddy:

<pre><code class="cmd bash">caddy start</code></pre>

Caddy hiện đang chạy ở chế độ chờ (với cấu hình trống). Hãy cung cấp cho nó một cấu hình đơn giản bằng `curl`:

<pre><code class="cmd bash">curl localhost:2019/load \
    -H "Content-Type: application/json" \
    -d @- << EOF
    {
        "apps": {
            "http": {
                "servers": {
                    "hello": {
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
EOF</code></pre>

Việc cung cấp nội dung POST bằng [Heredoc](https://en.wikipedia.org/wiki/Here_document#Unix_shells) có thể gây tẻ nhạt, vì vậy nếu bạn thích sử dụng tệp, hãy lưu JSON vào một tệp có tên `caddy.json` và sau đó sử dụng lệnh này thay thế:

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

Bây giờ hãy tải [localhost:2015](http://localhost:2015) trong trình duyệt của bạn hoặc sử dụng `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Chúng ta cũng có thể định nghĩa nhiều trang web trên các giao diện khác nhau với JSON này:

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				},
				"bye": {
					"listen": [":2016"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Goodbye, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

Cập nhật JSON của bạn sau đó thực hiện lại yêu cầu API.

Dùng thử endpoint "goodbye" mới của bạn [trong trình duyệt](http://localhost:2016) hoặc bằng `curl` để đảm bảo nó hoạt động:

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Goodbye, world!</code></pre>

Khi bạn hoàn tất với Caddy, hãy nhớ dừng nó:

<pre><code class="cmd bash">caddy stop</code></pre>

Còn rất nhiều điều bạn có thể làm với API, bao gồm cả việc xuất cấu hình và thực hiện các thay đổi chi tiết đối với cấu hình (thay vì cập nhật toàn bộ). Hãy nhớ đọc [hướng dẫn đầy đủ về API](/docs/api-tutorial) để tìm hiểu cách thực hiện!

<a id="further-reading"></a>
## Đọc thêm

- [Hướng dẫn đầy đủ về API](/docs/api-tutorial)
- [Tài liệu API](/docs/api)
