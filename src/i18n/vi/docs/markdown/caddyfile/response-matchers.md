---
title: Trình khớp phản hồi (Caddyfile)
---

<script>
ready(function() {
	// Response matchers
	$$_('pre.chroma .nd').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#syntax" style="color: inherit;">${text}</a>`;
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="#status" style="color: inherit;">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="#header" style="color: inherit;">header</a>';
		}
	});

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

<a id="response-matchers"></a>
# Trình khớp phản hồi

**Trình khớp phản hồi** có thể được sử dụng để lọc (hoặc phân loại) các phản hồi theo các tiêu chí cụ thể.

Các trình khớp này thường chỉ xuất hiện dưới dạng cấu hình bên trong một số chỉ thị khác, để đưa ra quyết định về phản hồi khi nó đang được gửi đi cho khách hàng.

- [Cú pháp](#syntax)
- [Trình khớp](#matchers)
	- [status](#status)
	- [header](#header)

<a id="syntax"></a>
## Cú pháp

Nếu một chỉ thị chấp nhận các trình khớp phản hồi, cách sử dụng sẽ được biểu diễn dưới dạng `[<response_matcher>]` hoặc `[<inline_response_matcher>]` trong tài liệu hướng dẫn cú pháp.

- Token **<response_matcher>** có thể là tên của một trình khớp phản hồi có tên đã được khai báo trước đó. Ví dụ: `@name`.
- Token **<inline_response_matcher>** có thể là chính các tiêu chí phản hồi mà không cần khai báo trước. Ví dụ: `status 200`.

<a id="named"></a>
### Có tên (Named)

```caddy-d
@name {
	status <code...>
	header <field> [<value>]
}
```
Nếu chỉ có một khía cạnh của phản hồi liên quan đến chỉ thị, bạn có thể đặt tên và tiêu chí trên cùng một dòng:

```caddy-d
@name status <code...>
```

<a id="inline"></a>
### Nội dòng (Inline)

```caddy-d
... {
	status <code...>
	header <field> [<value>]
}
```
```caddy-d
... status <code...>
```
```caddy-d
... header <field> [<value>]
```

<a id="matchers"></a>
## Trình khớp

### status

```caddy-d
status <code...>
```

Theo mã trạng thái HTTP.

- **&lt;code...&gt;** là một danh sách các mã trạng thái HTTP. Các trường hợp đặc biệt là các chuỗi như `2xx` và `3xx`, khớp với tất cả các mã trạng thái trong phạm vi lần lượt là `200`-`299` và `300`-`399`.

<a id="example"></a>
#### Ví dụ:

```caddy-d
@success status 2xx
```



### header

```caddy-d
header <field> [<value>]
```

Theo các trường tiêu đề (header) phản hồi.

- `<field>` là tên của trường tiêu đề HTTP cần kiểm tra.
	- Nếu có tiền tố `!`, trường đó phải không tồn tại để khớp (bỏ qua tham số value).
- `<value>` là giá trị mà trường đó phải có để khớp.
	- Nếu có tiền tố `*`, nó thực hiện khớp hậu tố nhanh (xuất hiện ở cuối).
	- Nếu có hậu tố `*`, nó thực hiện khớp tiền tố nhanh (xuất hiện ở đầu).
	- Nếu được bao quanh bởi `*`, nó thực hiện khớp chuỗi con nhanh (xuất hiện ở bất cứ đâu).
	- Nếu không, đó là một khớp chính xác nhanh.

Các trường tiêu đề khác nhau trong cùng một tập hợp được kết hợp bằng toán tử AND. Nhiều giá trị cho mỗi trường được kết hợp bằng toán tử OR.

Lưu ý rằng các trường tiêu đề có thể được lặp lại và có các giá trị khác nhau. Các ứng dụng backend PHẢI xem xét rằng các giá trị trường tiêu đề là các mảng, không phải các giá trị đơn lẻ, và Caddy không diễn giải ý nghĩa trong các tình huống như vậy.

<a id="example"></a>
#### Ví dụ:

Khớp các phản hồi có tiêu đề `Foo` chứa giá trị `bar`:

```caddy-d
@upgrade header Foo *bar*
```

Khớp các phản hồi có tiêu đề `Foo` có giá trị `bar` HOẶC `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Khớp các phản hồi hoàn toàn không có trường tiêu đề `Foo`:

```caddy-d
@not_foo header !Foo
```
