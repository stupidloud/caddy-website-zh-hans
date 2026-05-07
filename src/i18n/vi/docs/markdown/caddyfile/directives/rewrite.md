---
title: rewrite (chỉ thị Caddyfile)
---

# rewrite

Ghi lại URI yêu cầu một cách nội bộ.

Việc ghi lại (rewrite) sẽ thay đổi một phần hoặc toàn bộ URI yêu cầu. Lưu ý rằng URI không bao gồm scheme hoặc authority (host & port), và khách hàng thường không gửi các fragment. Do đó, chỉ thị này chủ yếu được sử dụng để thao tác trên chuỗi **đường dẫn (path)** và **truy vấn (query)**.

Chỉ thị `rewrite` ngụ ý ý định chấp nhận yêu cầu, nhưng với các sửa đổi.

Nó loại trừ lẫn nhau với các chỉ thị `rewrite` khác trong cùng một khối, vì vậy an toàn khi xác định các rewrite mà nếu không sẽ chồng chéo lên nhau vì chỉ lần khớp đầu tiên mới được thực hiện.

Một [request matcher](/docs/caddyfile/matchers) khớp với một yêu cầu trước khi `rewrite` có thể không khớp với chính yêu cầu đó sau khi `rewrite`. Nếu bạn muốn `rewrite` của mình chia sẻ một tuyến đường với các trình xử lý khác, hãy sử dụng chỉ thị [`route`](route) hoặc [`handle`](handle).


<a id="syntax"></a>
## Cú pháp

```caddy-d
rewrite [<matcher>] <to>
```

- **&lt;to&gt;** là URI để ghi lại yêu cầu tới đó. Chỉ các thành phần của URI (đường dẫn hoặc chuỗi truy vấn) được chỉ định trong rewrite mới được thao tác. Đường dẫn URI là bất kỳ chuỗi con nào đứng trước `?`. Nếu `?` bị bỏ qua, thì toàn bộ token được coi là đường dẫn.

Trước phiên bản v2.8.0, đối số `<to>` có thể gây nhầm lẫn cho bộ phân tích cú pháp với một [matcher token](/docs/caddyfile/matchers#syntax) nếu nó bắt đầu bằng `/`, vì vậy cần phải chỉ định một ký tự đại diện wildcard (`*`).


<a id="similar-directives"></a>
## Các chỉ thị tương tự

Có các chỉ thị khác thực hiện việc ghi lại, nhưng ngụ ý ý định khác hoặc thực hiện việc ghi lại mà không thay thế hoàn toàn URI:

- [`uri`](uri) thao tác trên URI (loại bỏ tiền tố, hậu tố hoặc thay thế chuỗi con).

- [`try_files`](try_files) ghi lại yêu cầu dựa trên sự tồn tại của các tệp.



<a id="examples"></a>
## Ví dụ

Ghi lại tất cả các yêu cầu thành `index.html`, giữ nguyên bất kỳ chuỗi truy vấn nào:

```caddy
example.com {
	rewrite /index.html
}
```

<aside class="tip">

Lưu ý rằng trước phiên bản v2.8.0, một [wildcard matcher](/docs/caddyfile/matchers#wildcard-matchers) được yêu cầu ở đây vì đối số đầu tiên dễ gây nhầm lẫn với một [path matcher](/docs/caddyfile/matchers#path-matchers), ví dụ: `rewrite * /foo`, nhưng giờ đây nó có thể được đơn giản hóa thành `rewrite /foo`.

</aside>

Thêm tiền tố `/api` cho tất cả các yêu cầu, giữ nguyên phần còn lại của URI, sau đó chuyển tiếp proxy (reverse proxy) đến một ứng dụng:

```caddy
api.example.com {
	rewrite /api{uri}
	reverse_proxy localhost:8080
}
```

Thay thế chuỗi truy vấn trên các yêu cầu API bằng `a=b`, giữ nguyên đường dẫn:

```caddy
example.com {
	rewrite ?a=b
}
```

Chỉ đối với các yêu cầu tới `/api/`, hãy giữ nguyên chuỗi truy vấn hiện có và thêm một cặp khóa-giá trị:

```caddy
example.com {
	rewrite /api/* ?{query}&a=b
}
```

Thay đổi cả đường dẫn và chuỗi truy vấn, giữ nguyên chuỗi truy vấn ban đầu đồng thời thêm đường dẫn ban đầu làm tham số `p`:

```caddy
example.com {
	rewrite /index.php?{query}&p={path}
}
