---
title: try_files (Chỉ thị Caddyfile)
---

# try_files

Viết lại đường dẫn URI của yêu cầu thành tệp đầu tiên trong danh sách tồn tại trong gốc trang web. Nếu không có tệp nào khớp, việc viết lại sẽ không được thực hiện.


<a id="syntax"></a>
## Cú pháp

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **<files...>** là danh sách các tệp cần thử. Đường dẫn URI sẽ được viết lại thành tệp đầu tiên tồn tại.

  Để khớp với các thư mục, hãy thêm dấu gạch chéo xuôi `/` vào cuối đường dẫn. Tất cả các đường dẫn tệp đều tương đối so với [gốc](root) trang web và các [mẫu glob](https://pkg.go.dev/path/filepath#Match) sẽ được mở rộng.

  Mỗi đối số cũng có thể chứa một chuỗi truy vấn (query string), trong trường hợp đó chuỗi truy vấn cũng sẽ được thay đổi nếu nó khớp với tệp cụ thể đó.

  Nếu `try_policy` là `first_exist` (mặc định), thì mục cuối cùng trong danh sách có thể là một số được bắt đầu bằng dấu `=` (ví dụ: `=404`), đóng vai trò như một phương án dự phòng, sẽ phát ra lỗi với mã đó; lỗi có thể được bắt và xử lý bằng [`handle_errors`](handle_errors).

- **policy** là chính sách để chọn tệp trong danh sách các tệp.

  Mặc định: `first_exist`



<a id="expanded-form"></a>
## Dạng mở rộng

Chỉ thị `try_files` về cơ bản là một lối tắt cho:

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

Lưu ý rằng chỉ thị này không chấp nhận mã thông báo bộ khớp (matcher token). Nếu bạn cần logic khớp phức tạp hơn, hãy sử dụng dạng mở rộng ở trên làm cơ sở.

Xem [bộ khớp `file`](/docs/caddyfile/matchers#file) để biết thêm chi tiết.



<a id="examples"></a>
## Ví dụ

Nếu yêu cầu không khớp với bất kỳ tệp tĩnh nào, hãy viết lại thành điểm vào index/router PHP của bạn:

```caddy-d
try_files {path} /index.php
```

Tương tự, nhưng thêm đường dẫn gốc vào chuỗi truy vấn (yêu cầu bởi một số ứng dụng PHP cũ):

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

Tương tự, nhưng cũng khớp với các thư mục:

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

Cố gắng viết lại thành một tệp hoặc thư mục nếu nó tồn tại, nếu không sẽ phát ra lỗi 404 (có thể được bắt và xử lý bằng [`handle_errors`](handle_errors)):

```caddy-d
try_files {path} {path}/ =404
```

Chọn phiên bản tệp tĩnh được triển khai gần đây nhất (ví dụ: phục vụ `index.be331df.html` khi `index.html` được yêu cầu):

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
