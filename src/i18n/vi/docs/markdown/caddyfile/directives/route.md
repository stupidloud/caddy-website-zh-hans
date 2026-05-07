---
title: route (Chỉ thị Caddyfile)
---

# route

Đánh giá một nhóm các chỉ thị theo đúng nghĩa đen và như một đơn vị duy nhất.

Các chỉ thị nằm trong một khối route sẽ không bị [sắp xếp lại nội bộ](/docs/caddyfile/directives#directive-order). Chỉ các chỉ thị xử lý HTTP (các chỉ thị thêm trình xử lý hoặc middleware vào chuỗi) mới có thể được sử dụng trong một khối route.

Chỉ thị này là một trường hợp đặc biệt ở chỗ các chỉ thị con của nó cũng là các chỉ thị thông thường.


<a id="syntax"></a>
## Cú pháp

```caddy-d
route [<matcher>] {
	<directives...>
}
```

- **<directives...>** là một danh sách các chỉ thị hoặc các khối chỉ thị, mỗi chỉ thị trên một dòng, giống như bên ngoài một khối route; ngoại trừ việc các chỉ thị này sẽ không bị sắp xếp lại. Chỉ có các chỉ thị xử lý HTTP mới có thể được sử dụng.



<a id="utility"></a>
## Tiện ích

Chỉ thị `route` hữu ích trong một số trường hợp sử dụng nâng cao hoặc các trường hợp đặc biệt để kiểm soát tuyệt đối các phần của chuỗi trình xử lý HTTP.

Bởi vì thứ tự đánh giá middleware HTTP là quan trọng, Caddyfile thông thường sẽ sắp xếp lại các chỉ thị sau khi phân tích cú pháp để giúp Caddyfile dễ sử dụng hơn; bạn không phải lo lắng về việc mình nhập các thứ theo thứ tự nào.

Mặc dù [thứ tự tích hợp sẵn](/docs/caddyfile/directives#directive-order) tương thích với hầu hết các trang web, đôi khi bạn cần kiểm soát thủ công thứ tự, cho toàn bộ trang web hoặc chỉ một phần của nó. Đó là lý do chỉ thị `route` tồn tại.

Để minh họa, hãy xem xét trường hợp của hai trình xử lý kết thúc: [`redir`](redir) và [`file_server`](file_server). Cả hai đều viết phản hồi cho client và không gọi trình xử lý tiếp theo trong chuỗi, vì vậy chỉ một trong số chúng sẽ được thực thi cho một yêu cầu nhất định. Vậy cái nào đến trước? Thông thường, `redir` được thực thi trước `file_server` vì thông thường bạn chỉ muốn phát hành một lệnh chuyển hướng trong các trường hợp cụ thể và phục vụ các tệp trong trường hợp chung.

Tuy nhiên, có thể có những trường hợp chỉ thị đầu tiên (`file_server`) có bộ khớp cụ thể hơn chỉ thị thứ hai (`redir`). Nói cách khác, bạn muốn chuyển hướng trong trường hợp chung và chỉ phục vụ một tệp cụ thể.

Vì vậy, bạn có thể thử một Caddyfile như thế này (nhưng điều này sẽ không hoạt động như mong đợi!):

```caddy
example.com {
	file_server /specific.html
	redir https://anothersite.com{uri}
}
```

Vấn đề là sau khi [các chỉ thị được sắp xếp](/docs/caddyfile/directives#sorting-algorithm), `redir` sẽ đứng trước `file_server`.

Nhưng trong trường hợp này, bộ khớp cho `redir` (một [`*`](/docs/caddyfile/matchers#wildcard-matchers) ngầm định) là một tập siêu (superset) của bộ khớp cho `file_server` (`*` là tập siêu của `/specific.html`).

May mắn thay, giải pháp rất dễ dàng: chỉ cần bọc hai chỉ thị đó trong một khối `route`, để đảm bảo rằng `file_server` được thực thi trước `redir`:

```caddy
example.com {
	route {
		file_server /specific.html
		redir https://anothersite.com{uri}
	}
}
```

<aside class="tip">

Một cách khác để thực hiện việc này là làm cho hai bộ khớp loại trừ lẫn nhau, nhưng điều này có thể nhanh chóng trở nên phức tạp nếu có nhiều hơn một hoặc hai điều kiện. Với chỉ thị `route`, tính loại trừ lẫn nhau của hai trình xử lý là ngầm định vì cả hai đều là các trình xử lý kết thúc.

</aside>

Và bây giờ `file_server` sẽ được liên kết trước `redir` vì thứ tự được lấy theo đúng nghĩa đen.



<a id="similar-directives"></a>
## Các chỉ thị tương tự

Có các chỉ thị khác có thể bọc các chỉ thị xử lý HTTP, nhưng mỗi chỉ thị có cách sử dụng tùy thuộc vào hành vi bạn muốn truyền đạt:

- [`handle`](handle) bọc các chỉ thị khác giống như `route`, nhưng có hai điểm khác biệt: 1) các khối handle loại trừ lẫn nhau, và 2) các chỉ thị trong một handle được [sắp xếp lại](/docs/caddyfile/directives#directive-order) bình thường.

- [`handle_path`](handle_path) thực hiện tương tự như `handle`, but nó loại bỏ một tiền tố khỏi yêu cầu trước khi chạy các trình xử lý của nó.

- [`handle_errors`](handle_errors) giống như `handle`, nhưng chỉ được gọi khi Caddy gặp lỗi trong quá trình xử lý yêu cầu.



<a id="examples"></a>
## Ví dụ

Proxy các yêu cầu đến `/api` nguyên trạng và viết lại tất cả các yêu cầu khác dựa trên việc chúng có khớp với một tệp trên đĩa hay không, nếu không thì là `/index.html`. Sau đó, tệp đó được phục vụ.

Vì [`try_files`](try_files) có thứ tự chỉ thị cao hơn [`reverse_proxy`](reverse_proxy), nên thông thường nó sẽ được sắp xếp cao hơn và chạy trước; điều này sẽ khiến tất cả các yêu cầu API bị viết lại thành `/index.html` và không khớp với `/api*`, vì vậy không có yêu cầu nào trong số chúng được proxy và thay vào đó sẽ dẫn đến lỗi `404` từ [`file_server`](file_server). Việc bọc tất cả trong một `route` đảm bảo rằng `reverse_proxy` luôn chạy trước, trước khi yêu cầu bị viết lại.

```caddy
example.com {
	root /srv
	route {
		reverse_proxy /api* localhost:9000

		try_files {path} /index.html
		file_server
	}
}
```

<aside class="tip">

Đây không phải là giải pháp duy nhất cho vấn đề này. Bạn cũng có thể sử dụng một cặp khối [`handle`](handle), với khối đầu tiên khớp `/api*` cho `reverse_proxy`, và khối thứ hai đóng vai trò dự phòng và phục vụ các tệp. Xem [ví dụ này](/docs/caddyfile/patterns#single-page-apps-spas) về một SPA.

</aside>
