---
title: Bộ so khớp yêu cầu (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the matchers in the code blocks
	// to their associated anchor tags.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Link matcher tokens based on their contents to the syntax section
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Matcher token">${text}</a>`;
	});
});
</script>

<a id="request-matchers"></a>
# Bộ so khớp yêu cầu (Request Matchers)

**Bộ so khớp yêu cầu** có thể được sử dụng để lọc (hoặc phân loại) các yêu cầu theo các tiêu chí khác nhau.

- [Cú pháp](#syntax)
	- [Ví dụ](#examples)
	- [Bộ so khớp Wildcard](#wildcard-matchers)
	- [Bộ so khớp đường dẫn](#path-matchers)
	- [Bộ so khớp có tên](#named-matchers)
- [Bộ so khớp tiêu chuẩn](#standard-matchers)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)


<a id="syntax"></a>
## Cú pháp

Trong Caddyfile, một **token so khớp** đứng ngay sau chỉ thị có thể giới hạn phạm vi của chỉ thị đó. Token so khớp có thể là một trong các dạng sau:

1. [**`*`**](#wildcard-matchers) để khớp với tất cả các yêu cầu (wildcard; mặc định).
2. [**`/path`**](#path-matchers) bắt đầu bằng dấu gạch chéo để khớp với đường dẫn yêu cầu.
3. [**`@name`**](#named-matchers) để chỉ định một *bộ so khớp có tên*.

Nếu một chỉ thị hỗ trợ bộ so khớp, nó sẽ xuất hiện dưới dạng `[<matcher>]` trong tài liệu cú pháp của nó. Các token so khớp [thường là tùy chọn](/docs/caddyfile/directives#syntax), được biểu thị bằng `[ ]`. Nếu token so khớp bị bỏ qua, nó tương đương với bộ so khớp wildcard (`*`).


<a id="examples"></a>
#### Ví dụ

Chỉ thị này áp dụng cho [tất cả](#wildcard-matchers) yêu cầu HTTP:

```caddy-d
reverse_proxy localhost:9000
```

Và kết quả là tương đương (`*` là không cần thiết ở đây):

```caddy-d
reverse_proxy * localhost:9000
```

Nhưng chỉ thị này chỉ áp dụng cho các yêu cầu có [đường dẫn](#path-matchers) bắt đầu bằng `/api/`:

```caddy-d
reverse_proxy /api/* localhost:9000
```

Để so khớp với bất kỳ thứ gì khác ngoài đường dẫn, hãy định nghĩa một [bộ so khớp có tên](#named-matchers) và tham chiếu đến nó bằng `@name`:

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```




<a id="wildcard-matchers"></a>
### Bộ so khớp Wildcard

Bộ so khớp wildcard (hoặc "bắt-tất-cả") `*` khớp với mọi yêu cầu và chỉ cần thiết nếu token so khớp bắt buộc phải có. Ví dụ, nếu đối số đầu tiên bạn muốn truyền cho một chỉ thị tình cờ cũng là một đường dẫn, nó sẽ trông giống hệt một bộ so khớp đường dẫn! Vì vậy, bạn có thể sử dụng bộ so khớp wildcard để phân biệt, ví dụ:

```caddy-d
root * /home/www/mysite
```

Nếu không, bộ so khớp này thường không được sử dụng. Chúng tôi khuyên bạn nên bỏ qua nó nếu cú pháp không yêu cầu.


<a id="path-matchers"></a>
### Bộ so khớp đường dẫn

So khớp theo đường dẫn URI là cách phổ biến nhất để so khớp các yêu cầu, vì vậy bộ so khớp có thể được viết trực tiếp (inline), như sau:

```caddy-d
redir /old.html /new.html
```

Các token so khớp đường dẫn phải bắt đầu bằng dấu gạch chéo `/`.

**[So khớp đường dẫn](#path) là so khớp chính xác theo mặc định, không phải so khớp tiền tố.** Bạn phải thêm một dấu `*` để so khớp tiền tố nhanh. Lưu ý rằng `/foo*` sẽ khớp với `/foo` và `/foo/` cũng như `/foobar`; bạn có thể thực sự muốn `/foo/*` thay thế.


<a id="named-matchers"></a>
### Bộ so khớp có tên

Tất cả các bộ so khớp không phải là bộ so khớp đường dẫn hoặc wildcard phải là bộ so khớp có tên. Đây là bộ so khớp được định nghĩa bên ngoài bất kỳ chỉ thị cụ thể nào và có thể được tái sử dụng.

Định nghĩa một bộ so khớp với một tên duy nhất mang lại cho bạn sự linh hoạt hơn, cho phép bạn kết hợp [bất kỳ bộ so khớp có sẵn nào](#standard-matchers) thành một tập hợp:

```caddy-d
@name {
	...
}
```

hoặc, nếu chỉ có một bộ so khớp trong tập hợp, bạn có thể đặt nó trên cùng một dòng:

```caddy-d
@name ...
```

Sau đó, bạn có thể sử dụng bộ so khớp như sau, bằng cách chỉ định nó làm đối số đầu tiên cho một chỉ thị:

```caddy-d
directive @name
```

Ví dụ, cấu hình này sẽ chuyển tiếp các yêu cầu websocket HTTP/1.1 đến `localhost:6001`, và các yêu cầu khác đến `localhost:8080`. Nó so khớp các yêu cầu có trường header tên là `Connection` *chứa* `Upgrade`, **và** một trường khác tên là `Upgrade` chính xác là `websocket`:

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

Nếu tập hợp bộ so khớp chỉ gồm một bộ so khớp duy nhất, cú pháp một dòng cũng hoạt động:

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

Trong một trường hợp đặc biệt, bộ so khớp [`expression`](#expression) có thể được sử dụng mà không cần chỉ định tên của nó miễn là có một đối số được [đặt trong dấu ngoặc kép](/docs/caddyfile/concepts#tokens-and-quotes) (chính là biểu thức CEL) đứng sau tên bộ so khớp:

```caddy-d
@not-found `{err.status_code} == 404`
```

Giống như các chỉ thị, các định nghĩa bộ so khớp có tên phải nằm bên trong các [khối trang (site blocks)](/docs/caddyfile/concepts#structure) sử dụng chúng.

Một định nghĩa bộ so khớp có tên cấu thành một *tập hợp bộ so khớp*. Các bộ so khớp trong một tập hợp được liên kết với nhau bằng toán tử AND; nghĩa là tất cả phải khớp. Ví dụ, nếu bạn có cả bộ so khớp [`header`](#header) và [`path`](#path) trong tập hợp, cả hai phải khớp.

Nhiều bộ so khớp cùng loại có thể được hợp nhất (ví dụ: nhiều bộ so khớp [`path`](#path) trong cùng một tập hợp) bằng đại số boolean (AND/OR), như được mô tả trong các phần tương ứng bên dưới.

Đối với logic so khớp boolean phức tạp hơn, bạn nên sử dụng bộ so khớp [`expression`](#expression) để viết biểu thức CEL, hỗ trợ **and** `&&`, **or** `||`, và **dấu ngoặc đơn** `( )`.





<a id="standard-matchers"></a>
## Bộ so khớp tiêu chuẩn

Tài liệu đầy đủ về bộ so khớp có thể được tìm thấy [trong tài liệu của từng module bộ so khớp tương ứng](/docs/json/apps/http/servers/routes/match/).

Các yêu cầu có thể được so khớp theo những cách sau:



<a id="client-ip"></a>
### client_ip

```caddy-d
client_ip <ranges...>

expression client_ip('<ranges...>')
```

Theo địa chỉ IP của máy khách. Chấp nhận các IP chính xác hoặc dải CIDR. Hỗ trợ các vùng IPv6.

Bộ so khớp này được sử dụng tốt nhất khi tùy chọn toàn cục [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) được cấu hình, nếu không nó hoạt động giống hệt bộ so khớp [`remote_ip`](#remote-ip). Chỉ các yêu cầu từ các proxy đáng tin cậy mới được phân tích IP máy khách khi bắt đầu yêu cầu; các yêu cầu không đáng tin cậy sẽ sử dụng địa chỉ IP từ xa của thiết bị kết nối trực tiếp hoặc địa chỉ được đặt qua [giao thức PROXY](/docs/caddyfile/options#proxy-protocol).

Như một lối tắt, `private_ranges` có thể được sử dụng để khớp với tất cả các dải IPv4 và IPv6 riêng tư. Nó tương đương với việc chỉ định tất cả các dải này: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Có thể có nhiều bộ so khớp `client_ip` trên mỗi bộ so khớp có tên, và các dải của chúng sẽ được hợp nhất và liên kết bằng toán tử OR.

<a id="example"></a>
#### Ví dụ:

Khớp các yêu cầu từ địa chỉ IPv4 riêng tư:

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Bộ so khớp này thường được kết hợp với bộ so khớp [`not`](#not) để đảo ngược kết quả so khớp. Ví dụ, để hủy tất cả các kết nối từ địa chỉ IPv4 và IPv6 *công cộng* (là nghịch đảo của tất cả các dải riêng tư):

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "Xin chào, bạn phải đến từ một mạng riêng tư!"
}
```

Trong một [biểu thức CEL](#expression), nó sẽ trông như thế này:

```caddy-d
@my-friends `client_ip('12.23.34.45', '23.34.45.56')`
```



### expression

```caddy-d
expression <cel...>
```

Theo bất kỳ biểu thức [CEL (Common Expression Language)](https://github.com/google/cel-spec) nào trả về `true` hoặc `false`.

Hầu hết các bộ so khớp yêu cầu khác cũng có thể được sử dụng trong các biểu thức dưới dạng hàm, cho phép linh hoạt hơn cho logic boolean so với bên ngoài biểu thức. Xem tài liệu cho từng bộ so khớp để biết cú pháp được hỗ trợ trong các biểu thức CEL.

Caddy [placeholders](/docs/conventions#placeholders) (hoặc [lối tắt Caddyfile](/docs/caddyfile/concepts#placeholders)) có thể được sử dụng trong các biểu thức CEL này, vì chúng được xử lý trước và chuyển đổi thành các lệnh gọi hàm CEL thông thường trước khi được môi trường CEL thông dịch. Nếu một trình giữ chỗ nên được truyền dưới dạng đối số chuỗi cho một hàm so khớp, thì ký tự `{` ở đầu nên được thoát bằng dấu gạch chéo ngược `\` để nó không bị xử lý trước, ví dụ `file('\{path}.md')`.

Để thuận tiện, tên bộ so khớp có thể được bỏ qua nếu định nghĩa một bộ so khớp có tên chỉ bao gồm một biểu thức CEL. Biểu thức CEL phải được [đặt trong dấu ngoặc kép](/docs/caddyfile/concepts#tokens-and-quotes) (khuyên dùng dấu huyền hoặc heredocs). Điều này trông khá gọn gàng:

```caddy-d
@mutable `{method}.startsWith("P")`
```

Trong trường hợp này, bộ so khớp CEL được giả định.

<a id="examples"></a>
#### Ví dụ:

Khớp các yêu cầu có phương thức bắt đầu bằng `P`, ví dụ: `PUT` hoặc `POST`:

```caddy-d
@methods expression {method}.startsWith("P")
```

Khớp các yêu cầu mà trình xử lý trả về mã trạng thái lỗi `404`, sẽ được sử dụng kết hợp với [chỉ thị `handle_errors`](/docs/caddyfile/directives/handle_errors):

```caddy-d
@404 expression {err.status_code} == 404
```

Khớp các yêu cầu mà đường dẫn khớp với một trong hai biểu thức chính quy khác nhau; điều này chỉ có thể viết bằng một biểu thức, vì bộ so khớp [`path_regexp`](#path-regexp) thông thường chỉ có thể tồn tại một lần cho mỗi bộ so khớp có tên:

```caddy-d
@user expression path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')
```

Hoặc tương tự, bỏ qua tên bộ so khớp và bọc trong [dấu huyền](/docs/caddyfile/concepts#tokens-and-quotes) để nó được phân tích cú pháp thành một token duy nhất:

```caddy-d
@user `path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')`
```

Bạn có thể sử dụng [cú pháp heredoc](/docs/caddyfile/concepts#heredocs) để viết các biểu thức CEL trên nhiều dòng:

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Xin chào, API!"
```


---
### file

```caddy-d
file {
	root       <path>
	try_files  <files...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delims...>
}
file <files...>

expression `file({
	'root': '<path>',
	'try_files': ['<files...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delims...>']
})`
expression file('<files...>')
```

Theo các tệp tin.

- `root` xác định thư mục để tìm kiếm tệp. Mặc định là thư mục làm việc hiện tại, hoặc [biến](/docs/modules/http.handlers.vars) `root` (`{http.vars.root}`) nếu được đặt (có thể được đặt qua [chỉ thị `root`](/docs/caddyfile/directives/root)).

- `try_files` kiểm tra các tệp trong danh sách của nó khớp với chính sách try_policy.

  Để khớp với các thư mục, hãy thêm dấu gạch chéo `/` vào sau đường dẫn. Tất cả các đường dẫn tệp đều tương đối với [gốc (root)](/docs/caddyfile/directives/root) của trang web và các [mẫu glob](https://pkg.go.dev/path/filepath#Match) sẽ được mở rộng.

  Nếu `try_policy` là `first_exist` (mặc định), thì mục cuối cùng trong danh sách có thể là một con số bắt đầu bằng dấu `=` (ví dụ `=404`), đóng vai trò như một giải pháp dự phòng, sẽ tạo ra lỗi với mã đó; lỗi có thể được bắt và xử lý bằng [`handle_errors`](/docs/caddyfile/directives/handle_errors).



- `try_policy` chỉ định cách chọn một tệp. Mặc định là `first_exist`.

	- `first_exist` kiểm tra sự tồn tại của tệp. Tệp đầu tiên tồn tại sẽ được chọn.

	- `first_exist_fallback` tương tự như `first_exist`, nhưng giả định rằng phần tử cuối cùng trong danh sách luôn tồn tại để ngăn chặn việc truy cập đĩa.

	- `smallest_size` chọn tệp có kích thước nhỏ nhất.

	- `largest_size` chọn tệp có kích thước lớn nhất.

	- `most_recently_modified` chọn tệp được sửa đổi gần đây nhất.

- `split_path` sẽ khiến đường dẫn bị chia tại dấu phân cách đầu tiên trong danh sách được tìm thấy trong mỗi đường dẫn tệp để thử. Đối với mỗi giá trị bị chia, phía bên trái của phần chia bao gồm cả chính dấu phân cách sẽ là đường dẫn tệp được thử. Ví dụ, `/remote.php/dav/` sử dụng dấu phân cách `.php` sẽ thử tệp `/remote.php`. Mỗi dấu phân cách phải xuất hiện ở cuối một thành phần đường dẫn URI để được sử dụng làm dấu phân cách chia. Đây là một cài đặt chuyên biệt và chủ yếu được sử dụng khi phục vụ các trang web PHP.

Vì `try_files` với chính sách `first_exist` rất phổ biến, nên có một lối tắt một dòng cho việc đó:

```caddy-d
file <files...>
```

Một bộ so khớp `file` trống (không có tệp nào được liệt kê sau nó) sẽ xem tệp được yêu cầu&mdash;nguyên văn từ URI, tương đối với [gốc trang web](/docs/caddyfile/directives/root)&mdash;có tồn tại hay không. Điều này thực tế giống như `file {path}`.


<aside class="tip">

Vì việc viết lại dựa trên sự tồn tại của một tệp trên đĩa là rất phổ biến, nên cũng có [chỉ thị `try_files`](/docs/caddyfile/directives/try_files) là lối tắt của bộ so khớp `file` và một [trình xử lý `rewrite`](/docs/caddyfile/directives/rewrite).

</aside>


Khi khớp, bốn trình giữ chỗ mới sẽ khả dụng:

- `{file_match.relative}` Đường dẫn tương đối với gốc của tệp. Điều này thường hữu ích khi viết lại yêu cầu.
- `{file_match.absolute}` Đường dẫn tuyệt đối của tệp khớp, bao gồm cả gốc.
- `{file_match.type}` Loại tệp, `file` hoặc `directory`.
- `{file_match.remainder}` Phần còn lại sau khi chia đường dẫn tệp (nếu `split_path` được cấu hình)


<a id="examples"></a>
#### Ví dụ:

Khớp các yêu cầu mà đường dẫn là một tệp tồn tại:

```caddy-d
@file file
```

Khớp các yêu cầu mà đường dẫn theo sau là `.html` là một tệp tồn tại, hoặc nếu không, mà đường dẫn là một tệp tồn tại:

```caddy-d
@html file {
	try_files {path}.html {path} 
}
```

Tương tự như trên, ngoại trừ việc sử dụng lối tắt một dòng và quay về tạo lỗi 404 nếu không tìm thấy tệp:

```caddy-d
@html-or-error file {path}.html {path} =404
```

Thêm một vài ví dụ sử dụng [biểu thức CEL](#expression). Hãy nhớ rằng các trình giữ chỗ được xử lý trước và chuyển đổi thành các lệnh gọi hàm CEL thông thường trước khi được môi trường CEL thông dịch, vì vậy phép nối được sử dụng ở đây. Ngoài ra, dạng dài phải được sử dụng nếu nối với các trình giữ chỗ do những hạn chế về phân tích cú pháp hiện tại:

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---
### header

```caddy-d
header <field> [<value> ...]

expression header({'<field>': '<value>'})
```

Theo các trường header yêu cầu.

- `<field>` là tên của trường header HTTP cần kiểm tra.
	- Nếu bắt đầu bằng `!`, trường đó không được tồn tại để khớp (bỏ qua đối số giá trị).
- `<value>` là giá trị mà trường phải có để khớp. Có thể chỉ định một hoặc nhiều giá trị.
	- Nếu bắt đầu bằng `*`, nó thực hiện so khớp hậu tố nhanh (xuất hiện ở cuối).
	- Nếu kết thúc bằng `*`, nó thực hiện so khớp tiền tố nhanh (xuất hiện ở đầu).
	- Nếu được bao quanh bởi `*`, nó thực hiện so khớp chuỗi con nhanh (xuất hiện ở bất cứ đâu).
	- Nếu không, đó là một so khớp chính xác nhanh.

Các trường header khác nhau trong cùng một tập hợp được liên kết bằng AND. Nhiều giá trị cho mỗi trường được liên kết bằng OR.

Lưu ý rằng các trường header có thể được lặp lại và có các giá trị khác nhau. Các ứng dụng phụ trợ (backend) PHẢI xem xét rằng các giá trị trường header là mảng, không phải giá trị đơn lẻ, và Caddy không thông dịch ý nghĩa trong các tình huống khó xử như vậy.

<a id="example"></a>
#### Ví dụ:

Khớp các yêu cầu có header `Connection` chứa `Upgrade`:

```caddy-d
@upgrade header Connection *Upgrade*
```

Khớp các yêu cầu có header `Foo` chứa `bar` HOẶC `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Khớp các yêu cầu hoàn toàn không có trường header `Foo`:

```caddy-d
@not_foo header !Foo
```

Sử dụng một [biểu thức CEL](#expression), khớp các yêu cầu WebSocket bằng cách kiểm tra header `Connection` chứa `Upgrade` và header `Upgrade` bằng `websocket` (HTTP/2 có header `:protocol` cho việc này):

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---
<a id="header-regexp"></a>
<a id="header-regexp"></a>
### header_regexp

```caddy-d
header_regexp [<name>] <field> <regexp>

expression header_regexp('<name>', '<field>', '<regexp>')
expression header_regexp('<field>', '<regexp>')
```

Giống như [`header`](#header), nhưng hỗ trợ biểu thức chính quy (regular expressions).

Ngôn ngữ biểu thức chính quy được sử dụng là RE2, có trong Go. Xem [tham chiếu cú pháp RE2](https://github.com/google/re2/wiki/Syntax) và [tổng quan cú pháp biểu thức chính quy của Go](https://pkg.go.dev/regexp/syntax).

Kể từ v2.8.0, nếu `name` *không* được cung cấp, tên sẽ được lấy từ tên của bộ so khớp có tên. Ví dụ: một bộ so khớp có tên `@foo` sẽ khiến bộ so khớp này có tên là `foo`. Ưu điểm chính của việc chỉ định một tên là nếu có nhiều hơn một bộ so khớp biểu thức chính quy (ví dụ: `header_regexp` và [`path_regexp`](#path-regexp), hoặc nhiều trường header khác nhau) được sử dụng trong cùng một bộ so khớp có tên.

Các nhóm chụp (capture groups) có thể được truy cập thông qua [trình giữ chỗ](/docs/caddyfile/concepts#placeholders) trong các chỉ thị sau khi khớp:
- `{re.<name>.<capture_group>}` trong đó:
  - `<name>` là tên của biểu thức chính quy,
  - `<capture_group>` là tên hoặc số thứ tự của nhóm chụp trong biểu thức.

- `{re.<capture_group>}` không có tên, cũng được điền sẵn để thuận tiện. Tuy nhiên, nếu nhiều bộ so khớp biểu thức chính quy được sử dụng tuần tự, thì các giá trị trình giữ chỗ sẽ bị ghi đè bởi bộ so khớp tiếp theo.

Nhóm chụp `0` là kết quả khớp đầy đủ của biểu thức chính quy, `1` là nhóm chụp đầu tiên, `2` là nhóm chụp thứ hai, v.v. Vì vậy, cả `{re.foo.1}` hoặc `{re.1}` đều sẽ giữ giá trị của nhóm chụp đầu tiên.

Chỉ hỗ trợ một biểu thức chính quy cho mỗi trường header, vì các mẫu biểu thức chính quy không thể được hợp nhất; nếu bạn cần nhiều hơn, hãy cân nhắc sử dụng bộ so khớp [`expression`](#expression). Các kết quả khớp với nhiều trường header khác nhau sẽ được liên kết bằng toán tử AND.

<a id="example"></a>
#### Ví dụ:

Khớp các yêu cầu trong đó header Cookie chứa `login_` theo sau bởi một chuỗi hex, với một nhóm chụp có thể truy cập bằng `{re.login.1}` hoặc `{re.1}`.

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

Điều này có thể được đơn giản hóa bằng cách bỏ qua tên, tên này sẽ được suy ra từ bộ so khớp có tên:

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

Hoặc tương tự, sử dụng một [biểu thức CEL](#expression):

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```



---
### host

```caddy-d
host <hosts...>

expression host('<hosts...>')
```

So khớp yêu cầu theo trường header `Host` của yêu cầu.

Vì hầu hết các khối trang đã chỉ ra máy chủ (host) trong địa chỉ của trang web, bộ so khớp này thường được sử dụng trong các khối trang sử dụng tên máy chủ wildcard (xem [mẫu chứng chỉ wildcard](/docs/caddyfile/patterns#wildcard-certificates)), nhưng yêu cầu logic cụ thể cho từng tên máy chủ.

Nhiều bộ so khớp `host` sẽ được liên kết với nhau bằng toán tử OR.

<a id="example"></a>
#### Ví dụ:

So khớp một tên miền phụ (subdomain):

```caddy-d
@sub host sub.example.com
```

So khớp tên miền chính (apex domain) và một tên miền phụ:

```caddy-d
@site host example.com www.example.com
```

Nhiều tên miền phụ sử dụng một [biểu thức CEL](#expression):

```caddy-d
@app `host('app1.example.com', 'app2.example.com')`
```



---
### method

```caddy-d
method <verbs...>

expression method('<verbs...>')
```

Theo phương thức (động từ) của yêu cầu HTTP. Các động từ nên được viết hoa, như `POST`. Có thể khớp một hoặc nhiều phương thức.

Nhiều bộ so khớp `method` sẽ được liên kết với nhau bằng toán tử OR.

<a id="examples"></a>
#### Ví dụ:

Khớp các yêu cầu với phương thức `GET`:

```caddy-d
@get method GET
```

Khớp các yêu cầu với phương thức `PUT` hoặc `DELETE`:

```caddy-d
@put-delete method PUT DELETE
```

Khớp các phương thức chỉ đọc sử dụng một [biểu thức CEL](#expression):

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```



---
### not

```caddy-d
not <matcher>
```

hoặc, để phủ định nhiều bộ so khớp vốn được liên kết bằng AND, hãy mở một khối:

```caddy-d
not {
	<matchers...>
}
```

Kết quả của các bộ so khớp đi kèm sẽ bị phủ định.

<a id="examples"></a>
#### Ví dụ:

Khớp các yêu cầu có đường dẫn KHÔNG bắt đầu bằng `/css/` HOẶC `/js/`.

```caddy-d
@not-assets {
	not path /css/* /js/*
}
```

Khớp các yêu cầu MÀ KHÔNG CÓ CẢ HAI:
- một tiền tố đường dẫn `/api/`, VÀ CŨNG KHÔNG CÓ
- phương thức yêu cầu `POST`

nghĩa là không được có bất kỳ thứ gì trong số này để khớp:

```caddy-d
@with-neither {
	not path /api/*
	not method POST
}
```

Khớp các yêu cầu KHÔNG CÓ CÙNG LÚC CẢ HAI:
- một tiền tố đường dẫn `/api/`, VÀ
- phương thức yêu cầu `POST`

nghĩa là không được có cả hai hoặc có một trong hai thứ này để khớp:

```caddy-d
@without-both {
	not {
		path /api/*
		method POST
	}
}
```

Không có [biểu thức CEL](#expression) cho bộ so khớp này, vì bạn có thể sử dụng toán tử `!` để phủ định. Ví dụ:

```caddy-d
@without-both `!path('/api*') && !method('POST')`
```

Kết quả tương tự như thế này, sử dụng dấu ngoặc đơn:

```caddy-d
@without-both `!(path('/api*') || method('POST'))`
```




---
### path

```caddy-d
path <paths...>

expression path('<paths...>')
```

Theo đường dẫn yêu cầu (thành phần đường dẫn của URI yêu cầu). So khớp đường dẫn là chính xác nhưng không phân biệt chữ hoa chữ thường. Các ký tự wildcard `*` có thể được sử dụng:

- Chỉ ở cuối, để so khớp tiền tố (`/prefix/*`)
- Chỉ ở đầu, để so khớp hậu tố (`*.suffix`)
- Chỉ ở cả hai bên, để so khớp chuỗi con (`*/contains/*`)
- Chỉ ở giữa, để so khớp dạng glob (`/accounts/*/info`)

Dấu gạch chéo rất quan trọng. Ví dụ, `/foo*` sẽ khớp với `/foo`, `/foobar`, `/foo/`, và `/foo/bar`, nhưng `/foo/*` sẽ *không* khớp với `/foo` hoặc `/foobar`.

Đường dẫn yêu cầu được làm sạch để giải quyết các dấu chấm điều hướng thư mục trước khi so khớp. Ngoài ra, nhiều dấu gạch chéo được hợp nhất trừ khi mẫu so khớp có nhiều dấu gạch chéo. Nói cách khác, `/foo` sẽ khớp với `/foo` và `//foo`, nhưng `//foo` sẽ chỉ khớp với `//foo`.

Vì có nhiều dạng thoát (escaped) cho bất kỳ URI nào được cung cấp, đường dẫn yêu cầu được chuẩn hóa (URL-decoded, unescaped) ngoại trừ những chuỗi thoát tại các vị trí mà chuỗi thoát cũng có mặt trong mẫu so khớp. Ví dụ, `/foo/bar` khớp với cả `/foo/bar` và `/foo%2Fbar`, nhưng `/foo%2Fbar` sẽ chỉ khớp với `/foo%2Fbar`, vì chuỗi thoát được đưa ra rõ ràng trong cấu hình.

Chuỗi thoát wildcard đặc biệt `%*` cũng có thể được sử dụng thay vì `*` để để nguyên phạm vi so khớp của nó ở dạng thoát. Ví dụ, `/bands/*/*` sẽ không khớp với `/bands/AC%2FDC/T.N.T` vì đường dẫn sẽ được so sánh trong không gian chuẩn hóa nơi nó trông giống như `/bands/AC/DC/T.N.T`, không khớp với mẫu; tuy nhiên, `/bands/%*/*` sẽ khớp với `/bands/AC%2FDC/T.N.T` vì phạm vi được đại diện bởi `%*` sẽ được so sánh mà không giải mã các chuỗi thoát.

Nhiều đường dẫn sẽ được liên kết với nhau bằng toán tử OR.

<a id="examples"></a>
#### Ví dụ:

Khớp nhiều thư mục và nội dung của chúng:

```caddy-d
@assets path /js/* /css/* /images/*
```

Khớp một tệp cụ thể:

```caddy-d
@favicon path /favicon.ico
```

Khớp các phần mở rộng tệp:

```caddy-d
@extensions path *.js *.css
```

Với một [biểu thức CEL](#expression):

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```



---
<a id="path-regexp"></a>
### path_regexp

```caddy-d
path_regexp [<name>] <regexp>

expression path_regexp('<name>', '<regexp>')
expression path_regexp('<regexp>')
```

Giống như [`path`](#path), nhưng hỗ trợ biểu thức chính quy. Chạy trên đường dẫn đã giải mã URI/không thoát.

Ngôn ngữ biểu thức chính quy được sử dụng là RE2, có trong Go. Xem [tham chiếu cú pháp RE2](https://github.com/google/re2/wiki/Syntax) và [tổng quan cú pháp biểu thức chính quy của Go](https://pkg.go.dev/regexp/syntax).

Kể từ v2.8.0, nếu `name` *không* được cung cấp, tên sẽ được lấy từ tên của bộ so khớp có tên. Ví dụ: một bộ so khớp có tên `@foo` sẽ khiến bộ so khớp này có tên là `foo`. Ưu điểm chính của việc chỉ định một tên là nếu có nhiều hơn một bộ so khớp biểu thức chính quy (ví dụ: `path_regexp` và [`header_regexp`](#header-regexp)) được sử dụng trong cùng một bộ so khớp có tên.

Các nhóm chụp có thể được truy cập thông qua [trình giữ chỗ](/docs/caddyfile/concepts#placeholders) trong các chỉ thị sau khi khớp:
- `{re.<name>.<capture_group>}` trong đó:
  - `<name>` là tên của biểu thức chính quy,
  - `<capture_group>` là tên hoặc số thứ tự của nhóm chụp trong biểu thức.

- `{re.<capture_group>}` không có tên, cũng được điền sẵn để thuận tiện. Tuy nhiên, nếu nhiều bộ so khớp biểu thức chính quy được sử dụng tuần tự, thì các giá trị trình giữ chỗ sẽ bị ghi đè bởi bộ so khớp tiếp theo.

Nhóm chụp `0` là kết quả khớp đầy đủ của biểu thức chính quy, `1` là nhóm chụp đầu tiên, `2` là nhóm chụp thứ hai, v.v. Vì vậy, cả `{re.foo.1}` hoặc `{re.1}` đều sẽ giữ giá trị của nhóm chụp đầu tiên.

Chỉ có thể có một mẫu `path_regexp` cho mỗi bộ so khớp có tên, vì bộ so khớp này không thể tự hợp nhất với chính nó; nếu bạn cần nhiều hơn, hãy cân nhắc sử dụng bộ so khớp [`expression`](#expression).

<a id="example"></a>
#### Ví dụ:

Khớp các yêu cầu mà đường dẫn kết thúc bằng chuỗi hex 6 ký tự theo sau là `.css` hoặc `.js` dưới dạng phần mở rộng tệp, với các nhóm chụp (các phần nằm trong `( )`), có thể được truy cập lần lượt bằng `{re.static.1}` và `{re.static.2}` (hoặc `{re.1}` và `{re.2}`):

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

Điều này có thể được đơn giản hóa bằng cách bỏ qua tên, tên này sẽ được suy ra từ bộ so khớp có tên:

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

Hoặc tương tự, sử dụng một [biểu thức CEL](#expression), cũng đồng thời xác thực rằng [`file`](#file) có tồn tại trên đĩa:

```caddy-d
@static `path_regexp('\.([a-f0-9]{6})\.(css|js)$') && file()`
```



---
### protocol

```caddy-d
protocol http|https|grpc|http/<version>[+]

expression protocol('http|https|grpc|http/<version>[+]')
```

Theo giao thức yêu cầu. Có thể sử dụng tên giao thức rộng như `http`, `https`, hoặc `grpc`; hoặc các phiên bản HTTP cụ thể hoặc tối thiểu như `http/1.1` hoặc `http/2+`.

Chỉ có thể có một bộ so khớp `protocol` cho mỗi bộ so khớp có tên.

<a id="example"></a>
#### Ví dụ:

Khớp các yêu cầu sử dụng HTTP/2:

```caddy-d
@http2 protocol http/2+
```

Với một [biểu thức CEL](#expression):

```caddy-d
@http2 `protocol('http/2+')`
```



---
### query

```caddy-d
query <key>=<val>...
query ""

expression query({'<key>': '<val>'})
expression query({'<key>': ['<vals...>']})
```

Theo các tham số chuỗi truy vấn (query string parameters). Nên là một chuỗi các cặp `key=value`, hoặc một chuỗi rỗng "". Các khóa (keys) được so khớp chính xác (phân biệt chữ hoa chữ thường) nhưng cũng hỗ trợ `*` để khớp với bất kỳ giá trị nào. Các giá trị (values) có thể sử dụng trình giữ chỗ. Chuỗi rỗng khớp với các yêu cầu HTTP không có tham số truy vấn.

Có thể có nhiều bộ so khớp `query` trên mỗi bộ so khớp có tên, và các cặp có cùng khóa sẽ được liên kết bằng OR. Các khóa khác nhau sẽ được liên kết bằng AND. Vì vậy, tất cả các khóa trong bộ so khớp phải có ít nhất một giá trị khớp.

Các chuỗi truy vấn không hợp lệ (sai cú pháp, dấu chấm phẩy không thoát, v.v.) sẽ không thể phân tích cú pháp và do đó sẽ không khớp.

**LƯU Ý:** Tham số chuỗi truy vấn là mảng, không phải giá trị đơn lẻ. Điều này là do các khóa lặp lại là hợp lệ trong các chuỗi truy vấn và mỗi khóa có thể có một giá trị khác nhau. Bộ so khớp này sẽ khớp cho một khóa nếu bất kỳ một trong các giá trị được định cấu hình của nó được gán trong chuỗi truy vấn. Các ứng dụng phụ trợ sử dụng chuỗi truy vấn PHẢI xem xét rằng giá trị chuỗi truy vấn là mảng và có thể có nhiều giá trị.

<a id="example"></a>
#### Ví dụ:

Khớp tham số truy vấn `q` với bất kỳ giá trị nào:

```caddy-d
@search query q=*
```

Khớp tham số truy vấn `sort` với giá trị `asc` hoặc `desc`:

```caddy-d
@sorted query sort=asc sort=desc
```

So khớp cả `q` và `sort`, với một [biểu thức CEL](#expression):

```caddy-d
@search-sort `query({'sort': ['asc', 'desc'], 'q': '*'})`
```



---
<a id="remote-ip"></a>
### remote_ip

```caddy-d
remote_ip <ranges...>

expression remote_ip('<ranges...>')
```

Theo địa chỉ IP từ xa (nghĩa là địa chỉ IP của thiết bị kết nối trực tiếp hoặc địa chỉ được đặt qua [giao thức PROXY](/docs/caddyfile/options#proxy-protocol)). Chấp nhận các IP chính xác hoặc dải CIDR. Hỗ trợ các vùng IPv6.

Như một lối tắt, `private_ranges` có thể được sử dụng để khớp với tất cả các dải IPv4 và IPv6 riêng tư. Nó tương đương với việc chỉ định tất cả các dải này: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Nếu bạn muốn so khớp "IP thực" của khách hàng, được phân tích từ các header HTTP, hãy sử dụng bộ so khớp [`client_ip`](#client-ip) thay thế.

Có thể có nhiều bộ so khớp `remote_ip` trên mỗi bộ so khớp có tên, và các dải của chúng sẽ được hợp nhất và liên kết bằng toán tử OR.

<a id="example"></a>
#### Ví dụ:

Khớp các yêu cầu từ địa chỉ IPv4 riêng tư:

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Bộ so khớp này thường được kết hợp với bộ so khớp [`not`](#not) để đảo ngược kết quả so khớp. Ví dụ, để hủy tất cả các kết nối từ địa chỉ IPv4 và IPv6 *công cộng* (là nghịch đảo của tất cả các dải riêng tư):

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "Xin chào, bạn phải đến từ một mạng riêng tư!"
}
```

Trong một [biểu thức CEL](#expression), nó sẽ trông như thế này:

```caddy-d
@my-friends `remote_ip('12.23.34.45', '23.34.45.56')`
```



---
### vars

```caddy-d
vars <variable> <values...>

expression vars({'<variable>': '<value>'})
expression vars({'<variable>': ['<values...>']})
```

Theo giá trị của một biến trong ngữ cảnh yêu cầu, hoặc giá trị của một trình giữ chỗ. Nhiều giá trị có thể được chỉ định để khớp với bất kỳ giá trị khả thi nào (liên kết bằng OR).

Đối số **&lt;variable&gt;** có thể là tên biến hoặc trình giữ chỗ trong dấu ngoặc nhọn `{ }`. (Trình giữ chỗ không được mở rộng trong tham số đầu tiên.)

Bộ so khớp này hữu ích nhất khi kết hợp với [chỉ thị `map`](/docs/caddyfile/directives/map) dùng để đặt các đầu ra, với [chỉ thị `vars`](/docs/caddyfile/directives/vars) bên trong các tuyến đường của bạn, hoặc với các plugin dùng để đặt một số thông tin trong ngữ cảnh yêu cầu.

<a id="example"></a>
#### Ví dụ:

So khớp một đầu ra của [chỉ thị `map`](/docs/caddyfile/directives/map) tên là `magic_number` cho các giá trị `3` hoặc `5`:

```caddy-d
vars {magic_number} 3 5
```

So khớp giá trị của một trình giữ chỗ tùy ý, ví dụ: ID của người dùng đã xác thực, là `Bob` hoặc `Alice`:

```caddy-d
vars {http.auth.user.id} Bob Alice
```

Một ví dụ đầy đủ sử dụng [chỉ thị `vars`](/docs/caddyfile/directives/vars) để đặt một biến, sau đó so khớp biến đó với [bộ so khớp `vars`](#vars). Ở đây chúng tôi kết hợp hai header yêu cầu thành một biến và so khớp biến đó:

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "Bạn đã gửi Foo=123 và Bar=456!"
	}
	handle {
		respond "Foo và Bar không có gì đặc biệt."
	}
}
```

Trong một [biểu thức CEL](#expression), nó sẽ trông như thế này:

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---
<a id="vars-regexp"></a>
<a id="vars-regexp"></a>
### vars_regexp

```caddy-d
vars_regexp [<name>] <variable> <regexp>

expression vars_regexp('<name>', '<variable>', '<regexp>')
expression vars_regexp('<variable>', '<regexp>')
```

Giống như [`vars`](#vars), nhưng hỗ trợ biểu thức chính quy.

Ngôn ngữ biểu thức chính quy được sử dụng là RE2, có trong Go. Xem [tham chiếu cú pháp RE2](https://github.com/google/re2/wiki/Syntax) và [tổng quan cú pháp biểu thức chính quy của Go](https://pkg.go.dev/regexp/syntax).

Kể từ v2.8.0, nếu `name` *không* được cung cấp, tên sẽ được lấy từ tên của bộ so khớp có tên. Ví dụ: một bộ so khớp có tên `@foo` sẽ khiến bộ so khớp này có tên là `foo`. Ưu điểm chính của việc chỉ định một tên là nếu có nhiều hơn một bộ so khớp biểu thức chính quy (ví dụ: `vars_regexp` và [`header_regexp`](#header-regexp)) được sử dụng trong cùng một bộ so khớp có tên.

Các nhóm chụp có thể được truy cập thông qua [trình giữ chỗ](/docs/caddyfile/concepts#placeholders) trong các chỉ thị sau khi khớp:
- `{re.<name>.<capture_group>}` trong đó:
  - `<name>` là tên của biểu thức chính quy,
  - `<capture_group>` là tên hoặc số thứ tự của nhóm chụp trong biểu thức.

- `{re.<capture_group>}` không có tên, cũng được điền sẵn để thuận tiện. Tuy nhiên, nếu nhiều bộ so khớp biểu thức chính quy được sử dụng tuần tự, thì các giá trị trình giữ chỗ sẽ bị ghi đè bởi bộ so khớp tiếp theo.

Nhóm chụp `0` là kết quả khớp đầy đủ của biểu thức chính quy, `1` là nhóm chụp đầu tiên, `2` là nhóm chụp thứ hai, v.v. Vì vậy, cả `{re.foo.1}` hoặc `{re.1}` đều sẽ giữ giá trị của nhóm chụp đầu tiên.

Chỉ hỗ trợ một biểu thức chính quy cho mỗi tên biến, vì các mẫu biểu thức chính quy không thể được hợp nhất; nếu bạn cần nhiều hơn, hãy cân nhắc sử dụng bộ so khớp [`expression`](#expression). Các kết quả khớp với nhiều biến khác nhau sẽ được liên kết bằng toán tử AND.

<a id="example"></a>
#### Ví dụ:

So khớp một đầu ra của [chỉ thị `map`](/docs/caddyfile/directives/map) tên là `magic_number` cho một giá trị bắt đầu bằng `4`, chụp giá trị trong một nhóm chụp có thể truy cập bằng `{re.magic.1}` hoặc `{re.1}`:

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

Điều này có thể được đơn giản hóa bằng cách bỏ qua tên, tên này sẽ được suy ra từ bộ so khớp có tên:

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

Trong một [biểu thức CEL](#expression), nó sẽ trông như thế này:

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
```
`
