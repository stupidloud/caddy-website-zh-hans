---
title: request_header (Chỉ thị Caddyfile)
---

# request_header

Thao tác các trường tiêu đề HTTP trên yêu cầu. Nó có thể thiết lập, thêm và xóa các giá trị tiêu đề, hoặc thực hiện thay thế bằng biểu thức chính quy (regular expressions).

Nếu bạn có ý định thao tác các tiêu đề để chuyển tiếp (proxying), hãy sử dụng [chỉ thị phụ `header_up`](/docs/caddyfile/directives/reverse_proxy#header_up) của `reverse_proxy` thay thế, vì những thao tác đó có nhận thức về proxy.

Để thao tác các tiêu đề phản hồi HTTP, bạn có thể sử dụng chỉ thị [`header`](header).


<a id="syntax"></a>
## Cú pháp

```caddy-d
request_header [<matcher>] [[+|-]<field> [<value>|<find>] [<replace>]]
```

- **&lt;field&gt;** là tên của trường tiêu đề.

  Nếu không có tiền tố, trường sẽ được thiết lập (ghi đè).

  Thêm tiền tố `+` để thêm trường thay vì ghi đè (thiết lập) nếu trường đã tồn tại; các trường tiêu đề có thể xuất hiện nhiều lần trong một yêu cầu.

  Thêm tiền tố `-` để xóa trường. Trường có thể sử dụng các ký tự đại diện `*` ở tiền tố hoặc hậu tố để xóa tất cả các trường phù hợp.

- **&lt;value&gt;** là giá trị của trường tiêu đề, nếu thêm hoặc thiết lập một trường.

- **&lt;find&gt;** là chuỗi con hoặc biểu thức chính quy để tìm kiếm.

- **&lt;replace&gt;** là giá trị thay thế; bắt buộc nếu thực hiện tìm kiếm và thay thế.


<a id="examples"></a>
## Ví dụ

Xóa tiêu đề Referer khỏi yêu cầu:

```caddy-d
request_header -Referer
```

Xóa tất cả các tiêu đề có chứa dấu gạch dưới khỏi yêu cầu:

```caddy-d
request_header -*_*
```
