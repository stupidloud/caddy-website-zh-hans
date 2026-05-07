---
title: map (Chỉ thị Caddyfile)
---

# map

Thiết lập giá trị của các placeholder tùy chỉnh dựa trên một giá trị đầu vào.

Nó so sánh giá trị nguồn với phía đầu vào của bản đồ, và đối với giá trị khớp, nó áp dụng (các) giá trị đầu ra cho mỗi đích. Các đích trở thành tên của placeholder. Giá trị đầu ra mặc định cũng có thể được chỉ định cho mỗi đích.

Các placeholder được ánh xạ không được đánh giá cho đến khi chúng được sử dụng, vì vậy ngay cả đối với các ánh xạ rất lớn, chỉ thị này vẫn khá hiệu quả.

<a id="syntax"></a>
## Cú pháp

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<input> <outputs...>
	default    <defaults...>
}
```

- **&lt;source&gt;** là giá trị đầu vào để chuyển đổi. Thường là một placeholder.

- **&lt;destinations...&gt;** là các placeholder được tạo ra để giữ các giá trị đầu ra.

- **&lt;input&gt;** là giá trị đầu vào để khớp. Nếu có tiền tố `~`, nó được coi là một biểu thức chính quy (regular expression).

- **&lt;outputs...&gt;** là một hoặc nhiều giá trị đầu ra để lưu trữ trong placeholder liên quan. Đầu ra đầu tiên được ghi vào đích đầu tiên, đầu ra thứ hai vào đích thứ hai, v.v.
  
  Trường hợp đặc biệt, trình phân tích cú pháp Caddyfile coi các đầu ra là một dấu gạch ngang (`-`) là các giá trị null/nil. Điều này hữu ích nếu bạn muốn quay lại giá trị mặc định cho một đầu ra cụ thể trong trường hợp đầu vào đã cho, nhưng muốn sử dụng các giá trị không mặc định cho các đầu ra khác.

  Các đầu ra sẽ được chuyển đổi kiểu nếu có thể; `true` và `false` sẽ được chuyển đổi sang kiểu boolean, và các giá trị số sẽ được chuyển đổi sang số nguyên hoặc số thực tương ứng. Để tránh việc chuyển đổi này, bạn có thể bao quanh đầu ra bằng [dấu ngoặc kép](/docs/caddyfile/concepts#tokens-and-quotes) và chúng sẽ vẫn là chuỗi.

  Số lượng đầu ra cho mỗi ánh xạ không được vượt quá số lượng đích; tuy nhiên, để thuận tiện, có thể có ít đầu ra hơn đích, và bất kỳ đầu ra nào bị thiếu sẽ được điền vào một cách ngầm định.
  
  Nếu một biểu thức chính quy được sử dụng làm đầu vào, thì các nhóm bắt giữ (capture groups) có thể được tham chiếu bằng `${group}` trong đó `group` là tên hoặc số của nhóm bắt giữ trong biểu thức. Nhóm bắt giữ `0` là toàn bộ kết quả khớp regexp, `1` là nhóm bắt giữ đầu tiên, `2` là nhóm bắt giữ thứ hai, v.v.

- **&lt;default&gt;** chỉ định các giá trị đầu ra để lưu trữ nếu không có đầu vào nào khớp.


<a id="examples"></a>
## Ví dụ

Ví dụ sau đây trình bày hầu hết các khía cạnh của chỉ thị này:

```caddy-d
map {host}                {my_placeholder}  {magic_number} {
	example.com           "some value"      3
	foo.example.com       "another value"
	~(.*)\.example\.com$  "${1} subdomain"  5

	~.*\.net$             -                 7
	~.*\.xyz$             -                 15

	default               "unknown domain"  42
}
```

Chỉ thị này chuyển đổi dựa trên giá trị của `{host}`, tức là tên miền của yêu cầu.

- Nếu yêu cầu dành cho `example.com`, hãy đặt `{my_placeholder}` thành `some value`, và `{magic_number}` thành `3`.
- Ngược lại, nếu yêu cầu dành cho `foo.example.com`, hãy đặt `{my_placeholder}` thành `another value`, và để `{magic_number}` mặc định thành `42`.
- Ngược lại, nếu yêu cầu dành cho bất kỳ tên miền phụ nào của `example.com`, hãy đặt `{my_placeholder}` thành một chuỗi chứa giá trị của nhóm bắt giữ regexp đầu tiên, tức là toàn bộ tên miền phụ, và đặt `{magic_number}` thành 5.
- Ngược lại, nếu yêu cầu dành cho bất kỳ máy chủ nào kết thúc bằng `.net` hoặc `.xyz`, hãy chỉ đặt `{magic_number}` thành tương ứng `7` hoặc `15`. Để trống `{my_placeholder}`.
- Ngược lại (đối với tất cả các máy chủ khác), các giá trị mặc định sẽ được áp dụng: `{my_placeholder}` sẽ được đặt thành `unknown domain` và `{magic_number}` sẽ được đặt thành `42`.
