---
title: file_server (chỉ thị Caddyfile)
---

<script>
ready(function() {
	// Fix inline browse arg
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# file_server

Một máy chủ tệp tĩnh hỗ trợ cả hệ thống tệp thực và ảo. Nó tạo đường dẫn tệp bằng cách thêm đường dẫn URI của yêu cầu vào [đường dẫn gốc của trang web](root).

Theo mặc định, nó thực thi các URI chuẩn; nghĩa là các chuyển hướng HTTP sẽ được phát hành cho các yêu cầu đến các thư mục không kết thúc bằng dấu gạch chéo ngược (để thêm nó) hoặc các yêu cầu đến các tệp có dấu gạch chéo ngược (để xóa nó). Tuy nhiên, các chuyển hướng sẽ không được phát hành nếu một ghi lại nội bộ sửa đổi phần tử cuối cùng của đường dẫn (tên tệp).

Thông thường nhất, chỉ thị `file_server` được ghép nối với chỉ thị [`root`](root) để đặt gốc tệp cho toàn bộ trang web. Chỉ thị này cũng có một chỉ thị con `root` (xem bên dưới) để chỉ đặt gốc cho trình xử lý này (không được khuyến nghị). Lưu ý rằng gốc trang web không mang lại sự đảm bảo về sandbox: máy chủ tệp ngăn chặn việc duyệt thư mục từ các thành phần đường dẫn, nhưng các liên kết tượng trưng (symbolic links) bên trong gốc vẫn có thể cho phép truy cập ra ngoài gốc.

Khi có lỗi xảy ra (ví dụ: không tìm thấy tệp `404`, bị từ chối quyền truy cập `403`), các tuyến đường lỗi sẽ được gọi. Sử dụng chỉ thị [`handle_errors`](handle_errors) để xác định các tuyến đường lỗi và hiển thị các trang lỗi tùy chỉnh.

Khi sử dụng `browse`, đầu ra mặc định được tạo bởi mẫu HTML. Các máy khách có thể yêu cầu danh sách thư mục dưới dạng JSON hoặc văn bản thuần túy, bằng cách sử dụng các tiêu đề `Accept: application/json` hoặc `Accept: text/plain` tương ứng. Đầu ra JSON có thể hữu ích cho việc lập trình và đầu ra văn bản thuần túy có thể hữu ích cho việc sử dụng dòng lệnh của con người.


<a id="syntax"></a>
## Cú pháp

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <path>
	hide          <files...>
	index         <filenames...>
	browse        [<template_file>] {
		reveal_symlinks
		sort <sort_field> [<direction>]
		file_limit <number>
	}
	precompressed [<formats...>]
	status        <status>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> chỉ định một hệ thống tệp thay thế (có thể là ảo) để sử dụng. Bất kỳ mô-đun Caddy nào trong không gian tên `caddy.fs` đều có thể được sử dụng ở đây. Bất kỳ đường dẫn/tiền tố gốc nào vẫn sẽ áp dụng cho các mô-đun hệ thống tệp thay thế. Theo mặc định, đĩa cục bộ được sử dụng.

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 giới thiệu [cờ `--embed`](https://github.com/caddyserver/xcaddy#custom-builds) để nhúng một cây hệ thống tệp vào bản dựng Caddy tùy chỉnh và đăng ký một mô-đun `fs` tên là `embedded` cho phép trang web tĩnh của bạn được phân phối dưới dạng tệp thực thi Caddy.

- **root** <span id="root"/> đặt đường dẫn đến gốc của trang web. Nó tương tự như chỉ thị [`root`](root) ngoại trừ việc nó chỉ áp dụng cho phiên bản máy chủ tệp này và ghi đè lên bất kỳ gốc trang web nào khác có thể đã được xác định. Mặc định: `{http.vars.root}` hoặc thư mục làm việc hiện tại. Lưu ý: Chỉ thị con này chỉ thay đổi gốc cho trình xử lý này. Để các chỉ thị khác (như [`try_files`](try_files) hoặc [`templates`](templates)) biết cùng một gốc trang web, hãy sử dụng chỉ thị [`root`](root) thay thế.

- **hide** <span id="hide"/> là một danh sách các tệp hoặc thư mục cần ẩn; nếu được yêu cầu, máy chủ tệp sẽ giả vờ như chúng không tồn tại. Chấp nhận các trình giữ chỗ (placeholders) và các mẫu glob. Lưu ý rằng đây là các đường dẫn _hệ thống tệp_, KHÔNG phải đường dẫn yêu cầu. Nói cách khác, các đường dẫn tương đối sử dụng thư mục làm việc hiện tại làm cơ sở, KHÔNG phải gốc trang web; và tất cả các đường dẫn được chuyển đổi sang dạng tuyệt đối trước khi so sánh (nếu có thể). Chỉ định một tên tệp hoặc mẫu không có dấu phân cách đường dẫn sẽ ẩn tất cả các tệp có tên khớp bất kể vị trí của nó; nếu không, một so sánh tiền tố đường dẫn sẽ được thực hiện, sau đó là một so sánh hình cầu (globular). Vì đây là cấu hình Caddyfile, (các) tệp cấu hình đang hoạt động sẽ được thêm vào theo mặc định. Các so sánh ẩn có phân biệt chữ hoa chữ thường; trên các hệ thống tệp không phân biệt chữ hoa chữ thường, một đường dẫn yêu cầu có chữ hoa chữ thường khác nhau vẫn có thể phân giải thành cùng một đường dẫn trên đĩa, vì vậy `hide` không nên được coi là một ranh giới bảo mật cho các đường dẫn nhạy cảm.

- **index** <span id="index"/> là danh sách các tên tệp cần tìm kiếm làm tệp chỉ mục. Mặc định: `index.html index.txt`

- **browse** <span id="browse"/> cho phép liệt kê tệp cho các yêu cầu đến các thư mục không có tệp chỉ mục.

  - **<template_file>** <span id="template_file"/> là một tệp mẫu tùy chỉnh tùy chọn để sử dụng cho việc liệt kê thư mục. Mặc định là mẫu có thể được trích xuất bằng lệnh `caddy file-server export-template`, lệnh này sẽ in mẫu mặc định ra stdout. Mẫu được nhúng cũng có thể được tìm thấy [tại đây trong mã nguồn ![external link](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html). Các mẫu duyệt có thể sử dụng các hành động từ [mô-đun mẫu tiêu chuẩn](/docs/modules/http.handlers.templates#docs).

  - **reveal_symlinks** <span id="reveal_symlinks"/> cho phép hiển thị các mục tiêu của các liên kết tượng trưng trong danh sách thư mục. Theo mặc định, các mục tiêu liên kết tượng trưng được ẩn và chỉ bản thân tệp liên kết được hiển thị.

  - **sort** <span id="sort"/> thay đổi sắp xếp mặc định cho danh sách thư mục. Tham số đầu tiên là trường/cột để sắp xếp theo: `name`, `namedirfirst`, `size`, hoặc `time`. Đối số thứ hai là một hướng tùy chọn: `asc` hoặc `desc`. Ví dụ, `sort name desc` sẽ sắp xếp theo tên theo thứ tự giảm dần.

  - **file_limit** <span id="file_limit"/> đặt số lượng tệp tối đa để hiển thị trong danh sách thư mục. Mặc định: `10000`. Nếu số lượng tệp vượt quá giới hạn này, chỉ N tệp đầu tiên sẽ được hiển thị, trong đó N là giới hạn được chỉ định.

- **precompressed** <span id="precompressed"/> là danh sách các định dạng mã hóa để tìm kiếm các tệp sidecar được nén trước. Các đối số là một danh sách có thứ tự các định dạng mã hóa để tìm kiếm các [tệp sidecar](https://en.wikipedia.org/wiki/Sidecar_file) được nén trước. Các định dạng được hỗ trợ là `gzip` (`.gz`), `zstd` (`.zst`) và `br` (`.br`). Nếu các định dạng bị bỏ qua, chúng sẽ mặc định là `br zstd gzip` (theo thứ tự đó).

  Tất cả các tra cứu tệp sẽ tìm kiếm sự tồn tại của tệp chưa nén trước. Sau khi được tìm thấy, Caddy sẽ tìm kiếm các tệp sidecar với phần mở rộng tệp của từng định dạng được bật. Nếu tìm thấy tệp sidecar được nén trước, Caddy sẽ phản hồi bằng tệp được nén trước, với tiêu đề phản hồi `Content-Encoding` được đặt thích hợp. Nếu không, Caddy sẽ phản hồi bằng tệp chưa nén như bình thường. Nếu [chỉ thị `encode`](encode) được bật, thì nó có thể nén phản hồi ngay lập tức nếu không được nén trước.

- **status** <span id="status"/> là một ghi đè mã trạng thái tùy chọn được sử dụng khi viết phản hồi. Đặc biệt hữu ích khi phản hồi một yêu cầu bằng một [trang lỗi tùy chỉnh](handle_errors). Có thể là mã trạng thái gồm 3 chữ số, Ví dụ: `404`. Các trình giữ chỗ được hỗ trợ. Theo mặc định, mã trạng thái được viết thường sẽ là `200`, hoặc `206` cho nội dung một phần.

- **disable_canonical_uris** <span id="disable_canonical_uris"/> vô hiệu hóa hành vi mặc định của việc chuyển hướng (để thêm dấu gạch chéo ngược nếu đường dẫn yêu cầu là thư mục hoặc xóa dấu gạch chéo ngược nếu đường dẫn yêu cầu là tệp). Lưu ý rằng theo mặc định, việc chuẩn hóa sẽ không xảy ra nếu phần tử cuối cùng của đường dẫn yêu cầu (tên tệp) đã trải qua một ghi lại nội bộ, để tránh làm hỏng một ghi lại rõ ràng với hành vi ngầm định.

- **pass_thru** <span id="pass_thru"/> bật chế độ chuyển qua (pass-thru), tiếp tục đến trình xử lý HTTP tiếp theo trong tuyến đường nếu không tìm thấy tệp được yêu cầu, thay vì kích hoạt lỗi `404` (gọi các tuyến đường [`handle_errors`](handle_errors)). Thực tế, điều này chỉ hữu ích bên trong một khối [`route`](route) với các chỉ thị trình xử lý khác sau `file_server`, vì chỉ thị này có hiệu quả [được sắp xếp cuối cùng](/docs/caddyfile/directives#directive-order).


<a id="examples"></a>
## Ví dụ

Một máy chủ tệp tĩnh từ thư mục hiện tại:

```caddy-d
file_server
```

Với danh sách tệp được bật:

```caddy-d
file_server browse
```

Chỉ phục vụ các tệp tĩnh trong thư mục `/static`:

```caddy-d
file_server /static/*
```

Chỉ thị `file_server` thường được ghép nối với [chỉ thị `root`](root) để đặt đường dẫn gốc từ đó phục vụ các tệp:

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

Nếu bạn đang chạy Caddy như một dịch vụ systemd, việc đọc các tệp từ `/home` sẽ không hoạt động, vì người dùng `caddy` không có quyền "thực thi" trên thư mục `/home` (cần thiết cho việc duyệt). Bạn nên đặt các tệp của mình trong `/srv` hoặc `/var/www/html` thay thế.

</aside>


Ẩn tất cả các thư mục `.git` và nội dung của chúng:

```caddy-d
file_server {
	hide .git
}
```

Nếu được máy khách hỗ trợ (tiêu đề `Accept-Encoding`) kiểm tra sự tồn tại của các tệp được nén trước cùng với tệp được yêu cầu. Vì vậy, nếu `/path/to/file` được yêu cầu, nó sẽ kiểm tra `/path/to/file.br`, `/path/to/file.zst` và `/path/to/file.gz` theo thứ tự đó và phục vụ tệp có sẵn đầu tiên với `Content-Encoding` tương ứng:

```caddy-d
file_server {
	precompressed
}
```
