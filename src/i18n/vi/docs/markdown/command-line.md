---
title: "Dòng lệnh"
---

<a id="command-line"></a>
# Dòng lệnh

Caddy có giao diện dòng lệnh chuẩn kiểu unix. Cách sử dụng cơ bản là:

```
caddy <command> [<args...>]
```

Các dấu `<ngoặc nhọn>` chỉ các tham số sẽ được thay thế bằng đầu vào của bạn.

Các dấu `[ngoặc vuông]` chỉ các tham số tùy chọn. Các dấu `(ngoặc đơn)` chỉ các tham số bắt buộc.

Dấu ba chấm `...` chỉ sự tiếp nối, tức là một hoặc nhiều tham số.

Các `--flags` (cờ) có thể có phím tắt một chữ cái như `-f`.

**Bắt đầu nhanh: `caddy`, `caddy help`, hoặc `man caddy` (nếu đã cài đặt)**

---

- **[caddy adapt](#caddy-adapt)**
  Chuyển đổi một tài liệu cấu hình sang JSON bản địa

- **[caddy build-info](#caddy-build-info)**
  In thông tin bản dựng

- **[caddy completion](#caddy-completion)**
  Tạo tập lệnh hoàn thành trình bao (shell completion script)

- **[caddy environ](#caddy-environ)**
  In các biến môi trường

- **[caddy file-server](#caddy-file-server)**
  Một máy chủ tệp đơn giản nhưng sẵn sàng cho sản xuất

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  Lệnh bổ trợ cho máy chủ tệp để xuất mẫu trình duyệt tệp mặc định

- **[caddy fmt](#caddy-fmt)**
  Định dạng một Caddyfile

- **[caddy hash-password](#caddy-hash-password)**
  Băm mật khẩu và xuất ra base64

- **[caddy help](#caddy-help)**
  Xem trợ giúp cho các lệnh caddy

- **[caddy list-modules](#caddy-list-modules)**
  Liệt kê các mô-đun Caddy đã cài đặt

- **[caddy manpage](#caddy-manpage)**
  Tạo các trang hướng dẫn (manpages)

- **[caddy reload](#caddy-reload)**
  Thay đổi cấu hình của tiến trình Caddy đang chạy

- **[caddy respond](#caddy-respond)**
  Một máy chủ HTTP được mã hóa cứng nhanh chóng và sạch sẽ cho việc phát triển và thử nghiệm

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  Một proxy ngược HTTP(S) đơn giản nhưng sẵn sàng cho sản xuất

- **[caddy run](#caddy-run)**
  Bắt đầu tiến trình Caddy ở chế độ nền trước (foreground)

- **[caddy start](#caddy-start)**
  Bắt đầu tiến trình Caddy ở chế độ chạy ngầm (background)

- **[caddy stop](#caddy-stop)**
  Dừng tiến trình Caddy đang chạy

- **[caddy storage export](#caddy-storage)**
  Xuất nội dung của bộ lưu trữ đã cấu hình sang tệp tarball

- **[caddy storage import](#caddy-storage)**
  Nhập một tệp tarball đã xuất trước đó vào bộ lưu trữ đã cấu hình

- **[caddy trust](#caddy-trust)**
  Cài đặt một chứng chỉ vào (các) kho lưu trữ tin cậy cục bộ

- **[caddy untrust](#caddy-untrust)**
  Gỡ bỏ sự tin cậy của một chứng chỉ khỏi (các) kho lưu trữ tin cậy cục bộ

- **[caddy upgrade](#caddy-upgrade)**
  Nâng cấp Caddy lên phiên bản mới nhất

- **[caddy add-package](#caddy-add-package)**
  Nâng cấp Caddy lên phiên bản mới nhất, với các plugin bổ sung được thêm vào

- **[caddy remove-package](#caddy-remove-package)**
  Nâng cấp Caddy lên phiên bản mới nhất, với một số plugin bị gỡ bỏ

- **[caddy validate](#caddy-validate)**
  Kiểm tra xem tệp cấu hình có hợp lệ hay không

- **[caddy version](#caddy-version)**
  In ra phiên bản

- **[Tín hiệu (Signals)](#signals)**
  Cách Caddy xử lý các tín hiệu

- **[Mã thoát (Exit codes)](#exit-codes)**
  Được phát ra khi tiến trình Caddy thoát

<a id="subcommands"></a>
## Các lệnh con


<a id="caddy-adapt"></a>
### `caddy adapt`

<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

Chuyển đổi một cấu hình sang cấu trúc cấu hình JSON bản địa của Caddy và ghi đầu ra vào stdout, cùng với bất kỳ cảnh báo nào vào stderr, sau đó thoát.

`--config` là đường dẫn đến tệp cấu hình. Nếu bị bỏ qua, giả định là `Caddyfile` trong thư mục hiện tại nếu nó tồn tại; nếu không, cờ này là bắt buộc. Nếu bạn muốn sử dụng stdin thay vì một tệp thông thường, hãy sử dụng - làm đường dẫn.

`--adapter` chỉ định bộ chuyển đổi cấu hình (config adapter) để sử dụng; mặc định là `caddyfile`.

`--pretty` sẽ định dạng đầu ra với các khoảng thụt đầu dòng để con người dễ đọc hơn.

`--validate` sẽ tải và cung cấp cấu hình đã chuyển đổi để kiểm tra tính hợp lệ (nhưng nó sẽ không thực sự bắt đầu chạy cấu hình).

Lưu ý rằng một cấu hình được chuyển đổi thành công vẫn có thể thất bại khi xác thực. Ví dụ về điều này, hãy sử dụng Caddyfile sau:

```caddy
localhost

tls cert_notexist.pem key_notexist.pem
```

Hãy thử chuyển đổi nó:

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

Nó thành công mà không có lỗi. Sau đó hãy thử:

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_notexist.pem: no such file or directory
</code></pre>

Mặc dù Caddyfile đó có thể được chuyển đổi sang JSON mà không có lỗi, nhưng chứng chỉ thực tế và/hoặc các tệp khóa không tồn tại, vì vậy việc xác thực thất bại vì lỗi đó phát sinh trong giai đoạn cung cấp (provisioning). Do đó, xác thực là một bước kiểm tra lỗi mạnh hơn so với việc chuyển đổi.

<a id="example"></a>
#### Ví dụ

Để chuyển đổi một Caddyfile sang JSON mà bạn có thể dễ dàng đọc và tinh chỉnh thủ công:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile --pretty</code></pre>



<a id="caddy-build-info"></a>
### `caddy build-info`

<pre><code class="cmd bash">caddy build-info</code></pre>

In thông tin do Go cung cấp về bản dựng (đường dẫn mô-đun chính, phiên bản gói, thay thế mô-đun).




<a id="caddy-completion"></a>
### `caddy completion`

<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

Tạo các tập lệnh hoàn thành trình bao (shell completion scripts). Điều này cho phép bạn sử dụng tab-complete hoặc auto-complete (hoặc tương tự, tùy thuộc vào trình bao của bạn) khi nhập các lệnh `caddy`.

Để biết hướng dẫn cài đặt tập lệnh này vào trình bao cụ thể của bạn, hãy chạy `caddy help completion` hoặc `caddy completion -h`.



<a id="caddy-environ"></a>
### `caddy environ`

<pre><code class="cmd bash">caddy environ</code></pre>

In môi trường như Caddy thấy, sau đó thoát. Có thể hữu ích khi gỡ lỗi các hệ thống khởi tạo (init systems) hoặc các đơn vị quản lý tiến trình như systemd.




<a id="caddy-file-server"></a>
### `caddy file-server`

<pre><code class="cmd bash">caddy file-server
	[-r, --root &lt;path&gt;]
	[--listen &lt;addr&gt;]
	[-d, --domain &lt;example.com&gt;]
	[-b, --browse]
	[--reveal-symlinks]
	[-t, --templates]
	[--access-log]
	[-v, --debug]
	[-f, --file-limit &lt;number&gt;]
	[--no-compress]
	[-p, --precompressed]</code></pre>

Khởi động một máy chủ tệp tĩnh đơn giản nhưng sẵn sàng cho sản xuất.

`--root` chỉ định đường dẫn tệp gốc. Mặc định là thư mục làm việc hiện tại.

`--listen` chấp nhận một địa chỉ lắng nghe. Mặc định là `:80`, trừ khi `--domain` được sử dụng, khi đó `:443` sẽ là mặc định.

`--domain` sẽ chỉ phục vụ các tệp thông qua tên máy chủ đó, và Caddy sẽ cố gắng phục vụ nó qua HTTPS, vì vậy hãy đảm bảo mọi DNS công cộng được cấu hình đúng trước nếu đó là một tên miền công cộng. Cổng mặc định sẽ được thay đổi thành 443.

`--browse` sẽ bật liệt kê thư mục nếu một thư mục không có tệp chỉ mục được yêu cầu.

`--reveal-symlinks` sẽ hiển thị đích của các liên kết tượng trưng (symbolic links) trong danh sách thư mục, khi `--browse` được bật.

`--templates` sẽ bật kết xuất mẫu (template rendering).

`--access-log` bật nhật ký yêu cầu/truy cập (request/access log).

`--debug` bật nhật ký chi tiết (verbose logging).

`--file-limit` đặt số lượng tệp tối đa để hiển thị trong danh sách thư mục. Mặc định: `10000`. Nếu số lượng tệp vượt quá giới hạn này, chỉ có N tệp đầu tiên sẽ được hiển thị, trong đó N là giới hạn đã chỉ định.

`--no-compress` tắt nén. Theo mặc định, nén Zstandard và Gzip được bật.

`--precompressed` chỉ định các định dạng mã hóa để tìm kiếm các tệp nén sẵn (precompressed sidecar files). Có thể lặp lại cho nhiều định dạng. Xem [chỉ thị file_server](/docs/caddyfile/directives/file_server#precompressed) để biết thêm thông tin.

Lệnh này vô hiệu hóa API quản trị (admin API), giúp chạy nhiều phiên bản trên máy phát triển cục bộ dễ dàng hơn.


<a id="caddy-file-server-export-template"></a>
#### `caddy file-server export-template`

<pre><code class="cmd bash">caddy file-server export-template</code></pre>

Xuất mẫu duyệt tệp mặc định ra stdout

<a id="caddy-fmt"></a>
### `caddy fmt`

<pre><code class="cmd bash">caddy fmt [&lt;path&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

Định dạng hoặc làm đẹp một Caddyfile, sau đó thoát. Kết quả được in ra stdout trừ khi `--overwrite` được sử dụng, và sẽ thoát với mã `1` nếu có bất kỳ sự khác biệt nào.

`<path>` chỉ định đường dẫn đến Caddyfile. Nếu `-`, đầu vào được đọc từ stdin. Nếu bị bỏ qua, một tệp có tên Caddyfile trong thư mục hiện tại sẽ được giả định.

`--overwrite` khiến kết quả được ghi vào tệp đầu vào thay vì được in ra thiết bị đầu cuối. Nếu đầu vào không phải là một tệp thông thường, cờ này không có tác dụng.

`--diff` khiến đầu ra được so sánh với đầu vào, và các dòng sẽ được bắt đầu bằng dấu `-` và `+` ở nơi chúng khác nhau. Lưu ý rằng các dòng không thay đổi được bắt đầu bằng hai khoảng trắng để căn lề, và đây không phải là định dạng bản vá (patch format) hợp lệ; nó chỉ được coi như một công cụ trực quan.


<a id="caddy-hash-password"></a>
### `caddy hash-password`

<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;password&gt;]
	[-a, --algorithm &lt;name&gt;]</code></pre>
	[--bcrypt-cost &lt;cost&gt;]</code></pre>

Cách thuận tiện để băm một mật khẩu văn bản thuần túy. Mã băm kết quả được ghi vào stdout dưới dạng định dạng có thể sử dụng trực tiếp trong cấu hình Caddy của bạn.

`--plaintext`
    Mật khẩu cần băm. Nếu bị bỏ qua, nó sẽ được đọc từ stdin.
    Nếu Caddy được gắn vào một TTY điều khiển, đầu vào sẽ không được phản hồi (echo).

`--algorithm`
    Chọn thuật toán băm. Các tùy chọn hợp lệ là:
      * `argon2id` (được khuyến nghị cho bảo mật hiện đại)
      * `bcrypt` (cũ hơn, chậm hơn, chi phí có thể cấu hình, chi phí mặc định là `14`)

Các tham số cụ thể cho bcrypt:

`--bcrypt-cost`
    Đặt độ khó băm bcrypt. Các giá trị cao hơn tăng cường bảo mật bằng cách
    làm cho việc tính toán mã băm chậm hơn và tốn nhiều tài nguyên CPU hơn.
    Phải nằm trong phạm vi hợp lệ [bcrypt.MinCost, bcrypt.MaxCost].
    Nếu bị bỏ qua hoặc không hợp lệ, chi phí mặc định sẽ được sử dụng.

Các tham số cụ thể cho Argon2id:

`--argon2id-time`
    Số lần lặp lại cần thực hiện. Tăng số này làm cho việc băm
    chậm hơn và có khả năng chống lại các cuộc tấn công brute-force tốt hơn.

`--argon2id-memory`
    Lượng bộ nhớ cần sử dụng trong khi băm.
    Các giá trị lớn hơn tăng khả năng chống lại các cuộc tấn công bằng GPU/ASIC.

`--argon2id-threads`
    Số luồng CPU cần sử dụng. Tăng số này để băm nhanh hơn
    trên các hệ thống đa lõi.

`--argon2id-keylen`
    Độ dài của mã băm kết quả tính bằng byte. Các khóa dài hơn tăng cường
    bảo mật nhưng làm tăng nhẹ kích thước lưu trữ.


<a id="caddy-help"></a>
### `caddy help`

<pre><code class="cmd bash">caddy help [&lt;command&gt;]</code></pre>

In văn bản trợ giúp CLI, tùy chọn cho một lệnh con cụ thể, sau đó thoát.



<a id="caddy-list-modules"></a>
### `caddy list-modules`

<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

In các mô-đun Caddy đã được cài đặt, tùy chọn kèm theo thông tin gói và/hoặc phiên bản từ các mô-đun Go liên quan, sau đó thoát.

Trong một số tình huống viết tập lệnh, việc in tất cả các mô-đun tiêu chuẩn có thể bị thừa, vì vậy bạn có thể sử dụng `--skip-standard` để loại bỏ chúng khỏi đầu ra.

`--json` xuất thông tin mô-đun ở định dạng JSON, có thể hữu ích cho việc xử lý theo chương trình.

LƯU Ý: Do [một lỗi trong Go](https://github.com/golang/go/issues/29228), thông tin phiên bản chỉ có sẵn nếu Caddy được xây dựng dưới dạng một phụ thuộc chứ không phải là mô-đun chính. Sử dụng [xcaddy](/docs/build#xcaddy) để thực hiện việc này dễ dàng hơn.



<a id="caddy-manpage"></a>
### `caddy manpage`

<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;path&gt;)</code></pre>

Tạo các trang hướng dẫn/tài liệu cho các lệnh Caddy và ghi chúng vào thư mục tại đường dẫn đã chỉ định. Đầu ra của lệnh này có thể được đọc bởi lệnh `man`.

`--directory` (bắt buộc) là đường dẫn đến thư mục nơi sẽ ghi các trang man. Nó sẽ được tạo nếu chưa tồn tại.

Sau khi được tạo, các trang hướng dẫn thường cần được cài đặt. Quy trình này thay đổi tùy theo nền tảng, nhưng trên các hệ thống Linux điển hình, nó sẽ giống như thế này:

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

Sau đó, bạn có thể chạy `man caddy` (hoặc `man caddy-*` cho các lệnh con) để đọc tài liệu trong thiết bị đầu cuối của mình.

Các trang hướng dẫn là tài liệu riêng biệt với những gì có trên trang web của chúng tôi. Trang web của chúng tôi có tài liệu toàn diện hơn và được cập nhật thường xuyên.




<a id="caddy-reload"></a>
### `caddy reload`

<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

Cung cấp cho phiên bản Caddy đang chạy một cấu hình mới. Điều này có tác dụng tương tự như việc gửi một tài liệu POST đến điểm cuối [/load](/docs/api#post-load), nhưng lệnh này thuận tiện cho các quy trình làm việc đơn giản xoay quanh các tệp cấu hình. So với các lệnh `stop`, `start` và `run`, lệnh duy nhất này là cách chính xác, mang tính ngữ nghĩa để thay đổi/tải lại cấu hình đang chạy.

Vì lệnh này sử dụng API, điểm cuối quản trị (admin endpoint) không được bị vô hiệu hóa.

`--config` là tệp cấu hình cần áp dụng. Nếu `-`, cấu hình được đọc từ stdin. Nếu không được chỉ định, nó sẽ thử một tệp có tên `Caddyfile` trong thư mục làm việc hiện tại và nếu tệp đó tồn tại, nó sẽ chuyển đổi tệp đó bằng bộ chuyển đổi cấu hình `caddyfile`; nếu không, sẽ là một lỗi nếu không có tệp cấu hình nào để tải.

`--adapter` chỉ định một bộ chuyển đổi cấu hình để sử dụng, nếu có. Cờ này không cần thiết nếu tên tệp `--config` bắt đầu bằng `Caddyfile` hoặc kết thúc bằng `.caddyfile`, điều này giả định bộ chuyển đổi `caddyfile`. Nếu không, cờ này là bắt buộc nếu tệp cấu hình được cung cấp không ở định dạng JSON bản địa của Caddy.

`--address` cần được sử dụng nếu điểm cuối quản trị không lắng nghe trên địa chỉ mặc định và nếu nó khác với địa chỉ trong tệp cấu hình được cung cấp.

`--force` sẽ khiến việc tải lại xảy ra ngay cả khi cấu hình được chỉ định giống với cấu hình Caddy đang chạy. Có thể hữu ích để buộc Caddy cung cấp lại các mô-đun của mình, điều này có thể gây ra các tác dụng phụ, ví dụ: tải lại các chứng chỉ TLS được tải thủ công.




<a id="caddy-respond"></a>
### `caddy respond`

<pre><code class="cmd bash">caddy respond
	[-s, --status &lt;code&gt;]
	[-H, --header "&lt;Field&gt;: &lt;value&gt;"]
	[-b, --body &lt;content&gt;]
	[-l, --listen &lt;addr&gt;]
	[-v, --debug]
	[--access-log]
	[&lt;status|body&gt;]</code></pre>


Bắt đầu một hoặc nhiều máy chủ HTTP đơn giản, được mã hóa cứng, hữu ích cho việc phát triển, dàn dựng và một số trường hợp sử dụng trong sản xuất. Nó có thể hữu ích để xác minh hoặc gỡ lỗi các máy khách HTTP, các tập lệnh hoặc thậm chí các bộ cân bằng tải.

`--status` là mã trạng thái HTTP cần trả về.

`--header` thêm một tiêu đề HTTP; định dạng `Field: value` được mong đợi. Cờ này có thể được sử dụng nhiều lần.

`--body` chỉ định nội dung phản hồi. Ngoài ra, nội dung có thể được dẫn từ stdin.

`--listen` là địa chỉ lắng nghe, có thể là bất kỳ [địa chỉ mạng](/docs/conventions#network-addresses) nào được Caddy công nhận, và có thể bao gồm một dải cổng để khởi động nhiều máy chủ.

`--debug` bật nhật ký gỡ lỗi chi tiết (verbose debug logging).

`--access-log` bật nhật ký truy cập/yêu cầu (access/request logging).

Nếu không có tùy chọn nào được chỉ định, lệnh này sẽ lắng nghe trên một cổng khả dụng ngẫu nhiên và trả lời các yêu cầu HTTP bằng một phản hồi 200 trống. Địa chỉ lắng nghe có thể được tùy chỉnh bằng cờ `--listen` và sẽ luôn được in ra stdout. Nếu địa chỉ lắng nghe bao gồm một dải cổng, nhiều máy chủ sẽ được khởi động.

Nếu một đối số cuối cùng, không tên được đưa ra, nó sẽ được xử lý như một mã trạng thái (giống như cờ `--status`) nếu nó là một số có 3 chữ số. Nếu không, nó được sử dụng làm nội dung phản hồi (giống như cờ `--body`). Các cờ `--status` và `--body` sẽ luôn ghi đè lên đối số này.

Nội dung phản hồi có thể được đưa ra theo 3 cách: một cờ, một đối số cuối cùng (và không tên) cho lệnh, hoặc được dẫn đến stdin (nếu cờ và đối số không được đặt). [Đánh giá mẫu](https://pkg.go.dev/text/template) có giới hạn được hỗ trợ trên nội dung phản hồi, với các biến sau:

Biến | Mô tả
---------|-------------
`.N`       | Số thứ tự máy chủ
`.Port`    | Cổng lắng nghe
`.Address` | Địa chỉ lắng nghe


<a id="examples"></a>
#### Ví dụ

Phản hồi 200 trống trên một cổng ngẫu nhiên:
<pre><code class="cmd bash">caddy respond</code></pre>

Phản hồi HTTP với một nội dung:
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

Nhiều máy chủ và các mẫu:
<pre><code class="cmd"><b>$ caddy respond --listen :2000-2004 "{{printf "I'm server {{.N}} on port {{.Port}}"}}"</b>

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

<b>$ curl 127.0.0.1:2002</b>
I'm server 2 on port 2002</code></pre>

Dẫn vào một trang bảo trì:
<pre><code class="cmd bash">cat maintenance.html | caddy respond \
	--listen :80 \
	--status 503 \
	--header "Content-Type: text/html"</code></pre>




<a id="caddy-reverse-proxy"></a>
### `caddy reverse-proxy`

<pre><code class="cmd bash">caddy reverse-proxy
	[-f, --from &lt;addr&gt;]
	(-t, --to &lt;addr&gt;)
	[-H, --header-up "&lt;Field&gt;: &lt;value&gt;"]
	[-d, --header-down "&lt;Field&gt;: &lt;value&gt;"]
	[-c, --change-host-header]
	[-r, --disable-redirects]
	[-i, --internal-certs]
	[-v, --debug]
	[--access-log]
	[--insecure]</code></pre>

Một proxy ngược đơn giản nhưng sẵn sàng cho sản xuất. Hữu ích cho các triển khai nhanh, trình diễn và phát triển.

Chỉ đơn giản là chuyển lưu lượng HTTP(S) từ địa chỉ `--from` đến địa chỉ `--to`. Có thể chỉ định nhiều địa chỉ `--to` bằng cách lặp lại cờ. Cần ít nhất một địa chỉ `--to`. Địa chỉ `--to` có thể có dải cổng như một phím tắt để mở rộng thành nhiều máy chủ thượng nguồn (upstreams).

Trừ khi được chỉ định khác trong các địa chỉ, địa chỉ `--from` sẽ được giả định là HTTPS nếu tên máy chủ được đưa ra, và địa chỉ `--to` sẽ được giả định là HTTP.

Nếu địa chỉ `--from` có máy chủ hoặc IP, Caddy sẽ cố gắng phục vụ proxy qua HTTPS bằng một chứng chỉ (trừ khi bị ghi đè bởi lược đồ HTTP hoặc cổng).

Nếu phục vụ HTTPS: 
  - `--disable-redirects` có thể được sử dụng để tránh liên kết với cổng HTTP.

  - `--internal-certs` có thể được sử dụng để buộc cấp các chứng chỉ sử dụng CA nội bộ thay vì cố gắng cấp một chứng chỉ công cộng.

Để ủy quyền (proxying):
  - `--header-up` có thể được sử dụng để đặt một tiêu đề yêu cầu gửi đến thượng nguồn.
  
  - `--header-down` có thể được sử dụng để đặt một tiêu đề phản hồi gửi ngược lại cho khách hàng.
  
  - `--change-host-header` đặt tiêu đề Host trên yêu cầu thành địa chỉ của thượng nguồn, thay vì mặc định là tiêu đề Host đến.

    Đây là phím tắt cho `--header-up "Host: {http.reverse_proxy.upstream.hostport}"`
  
  - `--insecure` tắt xác thực TLS với thượng nguồn. CẢNH BÁO: ĐIỀU NÀY VÔ HIỆU HÓA BẢO MẬT VÌ KHÔNG XÁC THỰC CHỨNG CHỈ CỦA THƯỢNG NGUỒN.
  
  - `--debug` bật nhật ký chi tiết.

Lệnh này vô hiệu hóa API quản trị để chạy nhiều phiên bản trên máy phát triển cục bộ dễ dàng hơn.



<a id="caddy-run"></a>
### `caddy run`

<pre><code class="cmd bash">caddy run
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--pidfile &lt;file&gt;]
	[-e, --environ]
	[--envfile &lt;file&gt;]
	[-r, --resume]
	[-w, --watch]</code></pre>

Chạy Caddy và chặn vô thời hạn; tức là chế độ "daemon".

`--config` chỉ định tệp cấu hình ban đầu để tải và sử dụng ngay lập tức. Nếu `-`, cấu hình được đọc từ stdin. Nếu không có cấu hình nào được chỉ định, Caddy sẽ chạy với một cấu hình trống và sử dụng các cài đặt mặc định cho [điểm cuối API quản trị](/docs/api), có thể được sử dụng để nạp cấu hình mới cho nó. Trong trường hợp đặc biệt, nếu thư mục làm việc hiện tại có một tệp mang tên "Caddyfile" và bộ chuyển đổi cấu hình `caddyfile` đã được cắm vào (mặc định), thì tệp đó sẽ được tải và sử dụng để cấu hình Caddy, ngay cả khi không có bất kỳ cờ dòng lệnh nào.

`--adapter` là tên của bộ chuyển đổi cấu hình sẽ sử dụng khi tải cấu hình ban đầu, nếu có. Cờ này không cần thiết nếu tên tệp `--config` bắt đầu bằng `Caddyfile` hoặc kết thúc bằng `.caddyfile`, điều này giả định bộ chuyển đổi `caddyfile`. Nếu không, cờ này là bắt buộc nếu tệp cấu hình được cung cấp không ở định dạng JSON bản địa của Caddy. Mọi cảnh báo sẽ được in vào nhật ký, nhưng hãy lưu ý rằng bất kỳ sự chuyển đổi nào không có lỗi sẽ được sử dụng ngay lập tức, ngay cả khi có cảnh báo. Nếu bạn muốn xem xét kết quả của việc chuyển đổi trước, hãy sử dụng lệnh con [`caddy adapt`](#caddy-adapt).

`--pidfile` ghi PID vào tệp đã chỉ định.

`--environ` in ra môi trường trước khi bắt đầu. Điều này giống như lệnh `caddy environ`, nhưng không thoát sau khi in.

`--envfile` tải các biến môi trường từ tệp đã chỉ định, theo định dạng `KEY=VALUE`. Các nhận xét bắt đầu bằng `#` được hỗ trợ; các khóa có thể được tiền tố bằng `export`; các giá trị có thể được đặt trong dấu ngoặc kép (dấu ngoặc kép bên trong có thể được thoát); các giá trị nhiều dòng được hỗ trợ.

`--resume` sử dụng cấu hình cuối cùng được tải đã được tự động lưu, ghi đè lên cờ `--config` (nếu có). Sử dụng cờ này đảm bảo tính bền vững của cấu hình thông qua việc khởi động lại máy hoặc khởi động lại tiến trình. Nó hữu ích nhất trong các triển khai tập trung vào [API](/docs/api).

`--watch` sẽ theo dõi tệp cấu hình và tự động tải lại sau khi nó thay đổi. ⚠️ Tính năng này chỉ dành cho mục đích sử dụng trong các môi trường phát triển cục bộ!

<aside class="advice">

Không dừng máy chủ để thay đổi cấu hình khi đang chạy trong sản xuất! Điều đó sẽ dẫn đến thời gian chết (downtime). (Điều này có vẻ hiển nhiên nhưng bạn sẽ ngạc nhiên về việc có bao nhiêu lời phàn nàn chúng tôi nhận được về nó.) Hãy sử dụng lệnh [`caddy reload`](#caddy-reload) để thay thế, hoặc gửi tín hiệu `SIGUSR1` cho tiến trình, điều này có tác dụng tương tự như `caddy reload` với cấu hình hiện đang tải.

</aside>



<a id="caddy-start"></a>
### `caddy start`

<pre><code class="cmd bash">caddy start
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]
	[--pidfile &lt;file&gt;]
	[-w, --watch]</code></code></pre>

Giống như [`caddy run`](#caddy-run), nhưng chạy ngầm (background). Lệnh này chỉ chặn cho đến khi tiến trình chạy ngầm bắt đầu thành công (hoặc thất bại), sau đó trả về.

Lưu ý: cờ `--config` *không* hỗ trợ `-` để đọc cấu hình từ stdin.

Việc sử dụng lệnh này không được khuyến nghị với các dịch vụ hệ thống hoặc trên Windows. Trên Windows, tiến trình con sẽ vẫn gắn liền với thiết bị đầu cuối, vì vậy việc đóng cửa sổ sẽ buộc Caddy dừng lại, điều này không rõ ràng. Thay vào đó, hãy xem xét việc chạy Caddy [như một dịch vụ](/docs/running).

Sau khi đã bắt đầu, bạn có thể sử dụng [`caddy stop`](#caddy-stop) hoặc điểm cuối API [`POST /stop`](/docs/api#post-stop) để thoát khỏi tiến trình chạy ngầm.



<a id="caddy-stop"></a>
### `caddy stop`

<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

<aside class="tip">

Dừng (và khởi động lại) máy chủ là độc lập với các thay đổi cấu hình. **Không sử dụng lệnh dừng để thay đổi cấu hình trong sản xuất, trừ khi bạn muốn thời gian chết.** Hãy sử dụng lệnh [`caddy reload`](#caddy-reload) để thay thế.

</aside>


Dừng tiến trình Caddy đang chạy một cách an toàn (ngoại trừ tiến trình của chính lệnh stop) và khiến nó thoát. Nó sử dụng điểm cuối [`POST /stop`](/docs/api#post-stop) của API quản trị để thực hiện việc tắt máy an toàn.

Địa chỉ của yêu cầu này có thể được tùy chỉnh bằng cờ `--address`, hoặc từ `--config` đã cho, nếu API quản trị của phiên bản đang chạy không sử dụng địa chỉ lắng nghe mặc định.

Nếu bạn muốn dừng cấu hình hiện tại nhưng không muốn thoát tiến trình, hãy sử dụng [`caddy reload`](#caddy-reload) với một cấu hình trống, hoặc điểm cuối [`DELETE /config/`](/docs/api#delete-configpath).


<a id="caddy-storage"></a>
### `caddy storage`

<i>⚠️ Thực nghiệm</i>

Cho phép xuất và nhập nội dung của bộ lưu trữ dữ liệu đã cấu hình của Caddy.

Điều này hữu ích khi cần chuyển đổi từ một [mô-đun lưu trữ](/docs/json/storage/) này sang mô-đun lưu trữ khác, bằng cách xuất từ mô-đun cũ, cập nhật cấu hình của bạn, sau đó nhập vào mô-đun mới.

Lệnh sau có thể được sử dụng để sao chép bộ lưu trữ giữa các mô-đun khác nhau chỉ trong một lần, sử dụng các cấu hình cũ và mới, dẫn đầu ra của lệnh xuất vào lệnh nhập.

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">

Xin lưu ý rằng khi sử dụng [lưu trữ hệ thống tệp](/docs/conventions#data-directory), bạn phải chạy lệnh xuất với cùng người dùng mà Caddy thường chạy dưới danh nghĩa, nếu không vị trí lưu trữ sai có thể được sử dụng.

Ví dụ, khi chạy Caddy như một [dịch vụ systemd](/docs/running#linux-service), nó sẽ chạy dưới danh nghĩa người dùng `caddy`, vì vậy bạn nên chạy lệnh xuất hoặc nhập với người dùng đó. Điều này thường có thể được thực hiện bằng `sudo -u caddy <command>`.

</aside>


<a id="caddy-storage-export"></a>
#### `caddy storage export`

<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;path&gt;
	[-o, --output &lt;path&gt;]</code></pre>

`--config` là tệp cấu hình để tải. Đây là bắt buộc, để mô-đun lưu trữ chính xác được kết nối.

`--output` là tên tệp để ghi tarball. Nếu `-`, đầu ra được ghi vào stdout.



<a id="caddy-storage-import"></a>
#### `caddy storage import`

<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;path&gt;
	-i, --input &lt;path&gt;</code></pre>

`--config` là tệp cấu hình để tải. Đây là bắt buộc, để mô-đun lưu trữ chính xác được kết nối.

`--input` là tên tệp của tarball để đọc. Nếu `-`, đầu vào được đọc từ stdin.


<a id="caddy-trust"></a>
### `caddy trust`

<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Cài đặt chứng chỉ gốc cho một CA do [ứng dụng PKI](/docs/json/apps/pki/) của Caddy quản lý vào các kho lưu trữ tin cậy cục bộ. 

Caddy sẽ cố gắng cài đặt các chứng chỉ gốc của mình vào các kho lưu trữ tin cậy cục bộ một cách tự động khi chúng được tạo lần đầu, nhưng nó có thể thất bại nếu Caddy không có các quyền thích hợp để ghi vào kho lưu trữ tin cậy. Lệnh này là cần thiết để cài đặt trước các chứng chỉ trước khi sử dụng chúng, nếu tiến trình máy chủ chạy dưới danh nghĩa một người dùng không có đặc quyền (chẳng hạn như thông qua systemd). Bạn có thể cần chạy lệnh này với `sudo` trên các hệ thống unix.

Theo mặc định, lệnh này cài đặt chứng chỉ gốc cho CA mặc định của Caddy (tức là "local"). Bạn có thể chỉ định ID của một CA khác bằng cờ `--ca`.

Lệnh này sẽ cố gắng kết nối với [API quản trị](/docs/api) của Caddy để lấy chứng chỉ gốc, sử dụng điểm cuối [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates). Bạn có thể chỉ định rõ ràng `--address`, hoặc sử dụng cờ `--config` để tải địa chỉ quản trị từ cấu hình của bạn, nếu API quản trị của phiên bản đang chạy không sử dụng địa chỉ lắng nghe mặc định.

Bạn cũng có thể sử dụng nhị phân `caddy` với lệnh này để cài đặt chứng chỉ trên các máy khác trong mạng của mình, nếu API quản trị được cung cấp cho các máy khác -- hãy cẩn thận khi thực hiện việc này, để không để lộ API quản trị cho các khách hàng không đáng tin cậy.


<a id="caddy-untrust"></a>
### `caddy untrust`

<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;path&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Gỡ bỏ sự tin cậy của một chứng chỉ gốc khỏi (các) kho lưu trữ tin cậy cục bộ.

Lệnh này gỡ bỏ cài đặt sự tin cậy; nó không nhất thiết xóa hoàn toàn chứng chỉ gốc khỏi các kho lưu trữ tin cậy. Do đó, việc lặp lại việc tin tưởng và gỡ bỏ sự tin cậy các chứng chỉ mới có thể làm đầy các cơ sở dữ liệu tin cậy.

Lệnh này không xóa hoặc sửa đổi các tệp chứng chỉ từ bộ lưu trữ đã cấu hình của Caddy.

Lệnh này có thể được sử dụng theo một trong hai cách:
- Bằng cách chỉ định đường dẫn trực tiếp đến chứng chỉ gốc cần gỡ bỏ sự tin cậy bằng cờ `--cert`.
- Bằng cách lấy chứng chỉ gốc từ [API quản trị](/docs/api) bằng điểm cuối [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates). Đây là hành vi mặc định nếu không có cờ nào được đưa ra.

Nếu API quản trị được sử dụng, thì CA ID mặc định là "local". Bạn có thể chỉ định ID của một CA khác bằng cờ `--ca`. Bạn có thể chỉ định rõ ràng `--address`, hoặc sử dụng cờ `--config` để tải địa chỉ quản trị từ cấu hình của bạn, nếu API quản trị của phiên bản đang chạy không sử dụng địa chỉ lắng nghe mặc định.


<a id="caddy-upgrade"></a>
### `caddy upgrade`

<i>⚠️ Thực nghiệm</i>

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

Thay thế tệp nhị phân Caddy hiện tại bằng phiên bản mới nhất từ [trang tải xuống của chúng tôi](/download) với cùng các mô-đun được cài đặt, bao gồm tất cả các plugin bên thứ ba đã được đăng ký trên trang web Caddy.

Việc nâng cấp không làm gián đoạn các máy chủ đang chạy; hiện tại, lệnh chỉ thay thế tệp nhị phân trên đĩa. Điều này có thể thay đổi trong tương lai nếu chúng tôi có thể tìm ra cách tốt để thực hiện nó.

Quá trình nâng cấp có khả năng chịu lỗi; tệp nhị phân hiện tại được sao lưu trước (được sao chép bên cạnh tệp hiện tại) và tự động được khôi phục nếu có bất kỳ sự cố nào xảy ra. Nếu bạn muốn giữ bản sao lưu sau khi quá trình nâng cấp hoàn tất, bạn có thể sử dụng tùy chọn `--keep-backup`.

Lệnh này có thể yêu cầu các đặc quyền nâng cao nếu người dùng của bạn không có quyền ghi vào tệp thực thi.



<a id="caddy-add-package"></a>
### `caddy add-package`

<i>⚠️ Thực nghiệm</i>

<pre><code class="cmd bash">caddy add-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

Tương tự như `caddy upgrade`, thay thế tệp nhị phân Caddy hiện tại bằng phiên bản mới nhất với cùng các mô-đun được cài đặt, _cộng thêm_ các gói được liệt kê làm đối số có trong tệp nhị phân mới. Tìm danh sách các gói bạn có thể cài đặt từ [trang tải xuống của chúng tôi](/download). Mỗi đối số phải là tên gói đầy đủ.

Ví dụ:

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>



<a id="caddy-remove-package"></a>
### `caddy remove-package`

<i>⚠️ Thực nghiệm</i>

<pre><code class="cmd bash">caddy remove-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

Tương tự như `caddy upgrade`, thay thế tệp nhị phân Caddy hiện tại bằng phiên bản mới nhất với cùng các mô-đun được cài đặt, nhưng _không có_ các gói được liệt kê làm đối số, nếu chúng tồn tại trong tệp nhị phân hiện tại. Chạy `caddy list-modules --packages` để xem danh sách tên gói của các mô-đun không tiêu chuẩn có trong tệp nhị phân hiện tại.



<a id="caddy-validate"></a>
### `caddy validate`

<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]</code></pre>

Xác thực một tệp cấu hình, sau đó thoát. Lệnh này khử tuần tự hóa cấu hình, sau đó tải và cung cấp tất cả các mô-đun của nó như thể để bắt đầu cấu hình, nhưng cấu hình không thực sự được bắt đầu. Điều này bộc lộ các lỗi trong một cấu hình phát sinh trong giai đoạn tải hoặc cung cấp và là một bước kiểm tra lỗi mạnh hơn so với việc chỉ đơn thuần tuần tự hóa một cấu hình dưới dạng JSON.

`--config` là tệp cấu hình cần xác thực. Nếu `-`, cấu hình được đọc từ stdin. Mặc định là `Caddyfile` trong thư mục hiện tại, nếu có.

`--adapter` là tên của bộ chuyển đổi cấu hình cần sử dụng. Cờ này không cần thiết nếu tên tệp `--config` bắt đầu bằng `Caddyfile` hoặc kết thúc bằng `.caddyfile`, điều này giả định bộ chuyển đổi `caddyfile`. Nếu không, cờ này là bắt buộc nếu tệp cấu hình được cung cấp không ở định dạng JSON bản địa của Caddy.

`--envfile` tải các biến môi trường từ tệp đã chỉ định, theo định dạng `KEY=VALUE`. Các nhận xét bắt đầu bằng `#` được hỗ trợ; các khóa có thể được tiền tố bằng `export`; các giá trị có thể được đặt trong dấu ngoặc kép (dấu ngoặc kép bên trong có thể được thoát); các giá trị nhiều dòng được hỗ trợ.



<a id="caddy-version"></a>
### `caddy version`
<pre><code class="cmd bash">caddy version</code></pre>

In phiên bản và thoát.



<a id="signals"></a>
## Tín hiệu (Signals)

Caddy bẫy một số tín hiệu nhất định và bỏ qua những tín hiệu khác. Các tín hiệu có thể bắt đầu các hành vi tiến trình cụ thể.

Tín hiệu | Hành vi
-------|----------
`SIGINT` | Thoát an toàn. Gửi lại tín hiệu để buộc thoát ngay lập tức.
`SIGQUIT` | Thoát Caddy ngay lập tức, nhưng vẫn dọn dẹp các khóa (locks) trong bộ lưu trữ vì nó quan trọng.
`SIGTERM` | Thoát an toàn.
`SIGUSR1` | Tải lại tệp cấu hình, nhưng chỉ khi được khởi động bằng `caddy run` (không có `--resume`) và không có thay đổi nào đối với cấu hình được thực hiện thông qua [API](/docs/api) (bao gồm [`caddy reload`]#caddy-reload)).
`SIGUSR2` | Bị bỏ qua.
`SIGHUP` | Bị bỏ qua.

Một lối thoát an toàn (graceful exit) có nghĩa là các kết nối mới không còn được chấp nhận và các kết nối hiện có sẽ được rút sạch (drained) trước khi ổ cắm (socket) bị đóng. Một khoảng thời gian ân hạn có thể được áp dụng (và có thể cấu hình được). Sau khi hết thời gian ân hạn, các kết nối sẽ bị chấm dứt một cách cưỡng ép. Các khóa trong bộ lưu trữ và các tài nguyên khác mà các mô-đun riêng lẻ cần giải phóng sẽ được dọn dẹp trong quá trình tắt máy an toàn.

Khi nhận được một tín hiệu tải lại cấu hình (`SIGUSR1`), nó hoạt động giống như một việc tải lại cấu hình bắt buộc (tức là vẫn tải lại ngay cả khi văn bản cấu hình không thay đổi), điều này có thể tải lại các tệp phụ thuộc như chứng chỉ TLS từ đĩa. 

Việc tải lại cấu hình dựa trên tín hiệu chỉ được bật nếu Caddy được khởi động bằng `caddy run` với một tệp cấu hình. Chúng sẽ bị vô hiệu hóa (tín hiệu bị bỏ qua, kèm theo cảnh báo trong nhật ký) nếu Caddy được khởi động bằng `--resume` (vì nó ngụ ý một quy trình làm việc API), hoặc nếu có bất kỳ thay đổi cấu hình nào nhận được qua API quản trị, hoặc nếu `caddy reload` được chạy với một tên tệp hoặc bộ chuyển đổi cấu hình _khác_ so với lúc khởi động ban đầu. Điều này là để tránh xung đột giữa các phương pháp tải lại.



<a id="exit-codes"></a>
## Mã thoát (Exit codes)

Caddy trả về một mã khi tiến trình thoát:

Mã | Ý nghĩa
-----|---------
`0` | Thoát bình thường.
`1` | Khởi động thất bại. **Không tự động khởi động lại tiến trình; nó có khả năng sẽ lại lỗi trừ khi có các thay đổi được thực hiện.**
`2` | Buộc thoát. Caddy bị buộc thoát mà không dọn dẹp tài nguyên.
`3` | Thoát thất bại. Caddy thoát với một số lỗi trong quá trình dọn dẹp.

Trong bash, bạn có thể lấy mã thoát của lệnh cuối cùng bằng `echo $?`.
