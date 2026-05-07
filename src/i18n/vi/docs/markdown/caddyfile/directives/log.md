---
title: log (Chỉ thị Caddyfile)
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.textContent.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# log

Bật và cấu hình ghi nhật ký yêu cầu HTTP (còn được gọi là nhật ký truy cập).

<aside class="tip">

Để cấu hình nhật ký thời gian chạy của Caddy, hãy xem [tùy chọn toàn cục `log`](/docs/caddyfile/options#log) thay thế.

</aside>


Chỉ thị `log` áp dụng cho các hostname của site block mà nó xuất hiện, trừ khi bị ghi đè bởi chỉ thị con `hostnames`.

Khi được cấu hình, theo mặc định, tất cả các yêu cầu đến trang web sẽ được ghi nhật ký. Để bỏ qua việc ghi nhật ký một số yêu cầu theo điều kiện, hãy sử dụng [chỉ thị `log_skip`](log_skip).

Để thêm các trường tùy chỉnh vào các mục nhật ký, hãy sử dụng [chỉ thị `log_append`](log_append).


- [Cú pháp](#syntax)
- [Các mô-đun đầu ra](#output-modules)
  - [stderr](#stderr)
  - [stdout](#stdout)
  - [discard](#discard)
  - [file](#file)
  - [net](#net)
- [Các mô-đun định dạng](#format-modules)
  - [console](#console)
  - [json](#json)
  - [filter](#filter)
    - [delete](#delete)
	- [rename](#rename)
	- [replace](#replace)
	- [ip_mask](#ip-mask)
	- [query](#query)
	- [cookie](#cookie)
	- [regexp](#regexp)
	- [hash](#hash)
  - [append](#append)
- [Ví dụ](#examples)

Theo mặc định, các tiêu đề có thông tin nhạy cảm tiềm ẩn (`Cookie`, `Set-Cookie`, `Authorization` và `Proxy-Authorization`) sẽ được ghi nhật ký là `REDACTED` trong nhật ký truy cập. Hành vi này có thể bị vô hiệu hóa bằng tùy chọn máy chủ toàn cục [`log_credentials`](/docs/caddyfile/options#log-credentials).


<a id="syntax"></a>
## Cú pháp

```caddy-d
log [<logger_name>] {
	hostnames <hostnames...>
	no_hostname
	output <writer_module> ...
	format <encoder_module> ...
	level  <level>
	sampling {
		interval   <duration>
		first      <number>
		thereafter <number>
	}
}
```

- **logger_name** <span id="logger_name"/> là một ghi đè tùy chọn của tên logger cho trang web này.

  Theo mặc định, tên logger được tạo tự động, ví dụ: `log0`, `log1`, v.v. tùy thuộc vào thứ tự của các trang web trong Caddyfile. Điều này chỉ hữu ích nếu bạn muốn tham chiếu một cách đáng tin cậy đến đầu ra của logger này từ một logger khác được định nghĩa trong các tùy chọn toàn cục. Xem [một ví dụ](#multiple-outputs) bên dưới.

- **hostnames** <span id="hostnames"/> là một ghi đè tùy chọn của các hostname mà logger này áp dụng cho.

  Theo mặc định, logger áp dụng cho các hostname của site block mà nó xuất hiện, tức là các địa chỉ trang web. Điều này hữu ích nếu bạn muốn xác định các logger khác nhau cho mỗi tên miền phụ trong một [site block ký tự đại diện](/docs/caddyfile/patterns#wildcard-certificates). Xem [một ví dụ](#wildcard-logs) bên dưới.

- **no_hostname** <span id="no_hostname"/> ngăn logger được liên kết với bất kỳ hostname nào của site block. Theo mặc định, logger được liên kết với [địa chỉ trang web](/docs/caddyfile/concepts#addresses) mà chỉ thị `log` xuất hiện.

  Điều này hữu ích khi bạn muốn ghi nhật ký các yêu cầu vào các tệp khác nhau dựa trên một số điều kiện, chẳng hạn như đường dẫn hoặc phương thức yêu cầu, sử dụng [chỉ thị `log_name`](/docs/caddyfile/directives/log_name).

- **output** <span id="output"/> cấu hình nơi viết nhật ký. Xem [các mô-đun `output`](#output-modules) bên dưới.

  Mặc định: `stderr`.

- **format** <span id="format"/> mô tả cách mã hóa, hoặc định dạng, nhật ký. Xem [các mô-đun `format`](#format-modules) bên dưới.

  Mặc định: `console` nếu `stderr` được phát hiện là một terminal, ngược lại là `json`.

- **level** <span id="level"/> là mức đầu vào tối thiểu để ghi nhật ký. Mặc định: `INFO`.

  Lưu ý rằng nhật ký truy cập hiện chỉ phát ra nhật ký mức `INFO` và `ERROR`.

- **sampling** <span id="sampling"/> cấu hình lấy mẫu nhật ký để giảm dung lượng nhật ký. Nếu lấy mẫu được chỉ định, thì nó được bật, với các giá trị mặc định bên dưới có hiệu lực. Bỏ qua điều này sẽ vô hiệu hóa lấy mẫu.

  - **interval** là [cửa sổ thời gian](/docs/conventions#durations) để tiến hành lấy mẫu. Mặc định: `1s` (vô hiệu hóa).

  - **first** là số lượng nhật ký cần giữ trong một mức và thông báo nhất định cho mỗi khoảng thời gian. Mặc định: `100`.

  - **thereafter** là số lượng nhật ký cần bỏ qua trong mỗi khoảng thời gian sau những nhật ký đầu tiên được giữ lại. Mặc định: `100`.

  Ví dụ, với `interval 1s`, `first 5`, và `thereafter 10`, trong mỗi khoảng thời gian 10 giây, 5 mục nhật ký đầu tiên sẽ được giữ lại, sau đó nó sẽ cho phép qua mỗi mục nhật ký thứ 10 có cùng mức và thông báo trong giây đó.


<a id="output-modules"></a>
### Các mô-đun đầu ra

Chỉ thị con **output** cho phép bạn tùy chỉnh nơi nhật ký được viết.

#### stderr

Lỗi tiêu chuẩn (console, là mặc định).

```caddy-d
output stderr
```

#### stdout

Đầu ra tiêu chuẩn (console).

```caddy-d
output stdout
```

#### discard

Không có đầu ra.

```caddy-d
output discard
```

#### file

Một tệp. Theo mặc định, các tệp nhật ký được xoay vòng ("rolled") dựa trên kích thước để ngăn chặn việc cạn kiệt dung lượng đĩa.

Việc xoay vòng nhật ký được cung cấp bởi [timberjack <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/DeRuina/timberjack)

<aside class="tip">

**Lưu ý về việc tải lại các tùy chọn tệp nhật ký:** Cần khởi động lại máy chủ để áp dụng các thay đổi cấu hình cho một tệp đầu ra nhất định.
Các thay đổi sẽ không được áp dụng tại thời điểm tải lại máy chủ, trừ khi bạn thêm một tên tệp nhật ký mới.

</aside>

```caddy-d
output file <filename> {
	mode          <mode>
	roll_disabled
	roll_size     <size>
	roll_interval <duration>
	roll_minutes  <minutes...>
	roll_at	      <times...>
	roll_uncompressed
	roll_local_time
	roll_keep     <num>
	roll_keep_for <days>
	backup_time_format <format>
}
```

- **&lt;filename&gt;** là đường dẫn đến tệp nhật ký.

  Khi được xoay vòng, các tệp được đổi tên bằng mẫu `<name>-<timestamp>-<reason>.log`. Dấu thời gian được định dạng theo tùy chọn [`backup_time_format`](#backup_time_format). Lý do là `size` hoặc `time`, tùy thuộc vào lý do nào đã kích hoạt việc xoay vòng. Nếu tệp được nén, `.gz` sẽ được thêm vào tên tệp.

   Ví dụ, nếu tên tệp là `access.log`, một tệp được xoay vòng có thể được đặt tên là `access-2026-01-30T22-15-42.123-size.log` nếu nó được xoay do kích thước, hoặc `access-2025-01-30T00-00-00.000-time.log` nếu nó được xoay do thời gian.

- **mode** <span id="mode"/> là chế độ/quyền tệp Unix để sử dụng cho tệp nhật ký. Chế độ bao gồm từ 1 đến 4 chữ số bát phân (giống như định dạng số được chấp nhận bởi lệnh Unix [chmod <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Chmod), ngoại trừ chế độ toàn số không được hiểu là chế độ mặc định `600`).

  Ví dụ: `0600` sẽ đặt chế độ thành `rw-,---,---` (quyền đọc/ghi cho chủ sở hữu tệp nhật ký và không có quyền truy cập cho bất kỳ ai khác); `0640` sẽ đặt chế độ thành `rw-,r--,---` (quyền đọc/ghi cho chủ sở hữu tệp, chỉ có quyền đọc cho nhóm); `644` đặt chế độ thành `rw-,r--,r--` cung cấp quyền đọc/ghi cho chủ sở hữu tệp nhật ký, nhưng chỉ có quyền đọc cho chủ sở hữu nhóm và những người dùng khác.

- **roll_disabled** <span id="roll_disabled"/> vô hiệu hóa việc xoay vòng nhật ký. Điều này có thể dẫn đến cạn kiệt dung lượng đĩa, vì vậy chỉ sử dụng điều này nếu các tệp nhật ký của bạn được duy trì theo cách khác.

- **roll_size** <span id="roll_size"/> là kích thước để xoay vòng tệp nhật ký. Việc triển khai hiện tại hỗ trợ độ phân giải megabyte; các giá trị phân số được làm tròn lên megabyte nguyên tiếp theo. Ví dụ: `1.1MiB` được làm tròn lên `2MiB`.

  Điều này luôn được bật. Nếu một lần ghi vào nhật ký khiến tệp vượt quá kích thước được chỉ định, nhật ký sẽ được xoay vòng ngay lập tức. Tên tệp sao lưu sẽ bao gồm `size` là lý do.

  Mặc định: `100MiB`

- **roll_interval** <span id="roll_interval"/> là thời gian tối đa giữa các lần xoay vòng nhật ký. Giá trị là một [chuỗi thời gian](/docs/conventions#durations) sau đó để xoay vòng tệp nhật ký.

  Khi được bật, tệp sẽ được xoay vòng vào lần ghi nhật ký tiếp theo sau khi khoảng thời gian này đã trôi qua kể từ lần xoay vòng cuối cùng. Tên tệp sao lưu sẽ bao gồm `time` là lý do.

  Lưu ý rằng nếu được đặt thành `24h`, nó không nhất thiết phải xoay vòng vào nửa đêm, mà đúng hơn là tại mốc 24 giờ kể từ lần xoay vòng cuối cùng. Nếu việc xoay vòng xảy ra do kích thước, thì thời gian của lần xoay vòng tiếp theo sẽ bị lệch so với lần xoay vòng trước đó. Bạn có thể sử dụng các tùy chọn `roll_at` hoặc `roll_minutes` để xoay vòng vào các thời điểm cụ thể thay thế.

  Mặc định: vô hiệu hóa

- **roll_minutes** <span id="roll_minutes"/> là danh sách các giá trị phút (0-59) để xoay vòng tệp nhật ký. Ví dụ: `10 40` sẽ xoay vòng tệp nhật ký sau mỗi 30 phút tại phút thứ `10` và `40` của mỗi giờ. Việc xoay vòng được căn chỉnh theo kim phút của đồng hồ (giây 0).

  Bật tính năng này sẽ tạo ra một bộ hẹn giờ goroutine kích hoạt việc xoay vòng nhật ký tại các giá trị phút được chỉ định (tức là giới thiệu một lượng nhỏ xử lý nền). Điều này hoạt động bổ sung cho `roll_interval` và `roll_size`. Tên tệp sao lưu sẽ bao gồm `time` là lý do.

  Mặc định: vô hiệu hóa

- **roll_at** <span id="roll_at"/> là danh sách các giá trị thời gian (theo định dạng 24 giờ) để xoay vòng tệp nhật ký. Ví dụ: `00:00 12:00` sẽ xoay vòng tệp nhật ký hai lần mỗi ngày vào nửa đêm và buổi trưa. Việc xoay vòng được căn chỉnh theo kim phút của đồng hồ (giây 0).

  Bật tính năng này sẽ tạo ra một bộ hẹn giờ goroutine kích hoạt việc xoay vòng nhật ký tại các thời điểm được chỉ định (tức là giới thiệu một lượng nhỏ xử lý nền). Điều này hoạt động bổ sung cho `roll_interval` và `roll_size`. Tên tệp sao lưu sẽ bao gồm `time` là lý do.

  Mặc định: vô hiệu hóa

- **roll_uncompressed** <span id="roll_uncompressed"/> tắt tính năng nén nhật ký gzip.

  Mặc định: Nén `gzip` được bật.

- **roll_local_time** <span id="roll_local_time"/> đặt việc xoay vòng sử dụng dấu thời gian địa phương trong tên tệp.
  Mặc định: sử dụng thời gian UTC.

- **roll_keep** <span id="roll_keep"/> là số lượng tệp nhật ký cần giữ lại trước khi xóa những tệp cũ nhất. Kích hoạt khi một tệp nhật ký mới được tạo.

  Mặc định: `10`

- **roll_keep_for** <span id="roll_keep_for"/> là thời gian giữ các tệp đã xoay dưới dạng [chuỗi thời gian](/docs/conventions#durations). Kích hoạt khi một tệp nhật ký mới được tạo.
  Việc triển khai hiện tại hỗ trợ độ phân giải ngày; các giá trị phân số được làm tròn lên ngày nguyên tiếp theo. Ví dụ: `36h` (1,5 ngày) được làm tròn lên `48h` (2 ngày).
  
  Mặc định: `2160h` (90 ngày)

- **backup_time_format** <span id="backup_time_format"/> là định dạng thời gian để sử dụng trong tên tệp sao lưu. Phải là một chuỗi bố cục thời gian hợp lệ; xem [tài liệu Go](https://pkg.go.dev/time#pkg-constants) để biết chi tiết đầy đủ.

  Mặc định: `2006-01-02T15-04-05`


#### net

Một socket mạng. Nếu socket bị ngắt, nó sẽ đổ nhật ký ra stderr trong khi cố gắng kết nối lại.

```caddy-d
output net <address> {
	dial_timeout <duration>
	soft_start
}
```

- **&lt;address&gt;** là [địa chỉ](/docs/conventions#network-addresses) để viết nhật ký vào.

- **dial_timeout** <span id="dial_timeout"/> là thời gian chờ kết nối thành công đến socket nhật ký. Việc phát nhật ký có thể bị chặn trong khoảng thời gian này nếu socket bị ngắt.

- **soft_start** <span id="soft_start"/> sẽ bỏ qua các lỗi khi kết nối với socket, cho phép bạn tải cấu hình của mình ngay cả khi dịch vụ nhật ký từ xa bị ngắt. Nhật ký sẽ được phát ra stderr thay thế.


<a id="format-modules"></a>
### Các mô-đun định dạng

Chỉ thị con **format** cho phép bạn tùy chỉnh cách nhật ký được mã hóa (định dạng). Nó xuất hiện bên trong một khối `log`.

<aside class="tip">

**Lưu ý về Định dạng Nhật ký Chung (CLF):** CLF xung đột với nhật ký có cấu trúc hiện đại. Để chuyển đổi nhật ký truy cập của bạn sang Định dạng Nhật ký Chung đã lỗi thời, vui lòng sử dụng [plugin `transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder).

</aside>


Ngoài cú pháp cho từng bộ mã hóa riêng lẻ, các thuộc tính chung này có thể được đặt trên hầu hết các bộ mã hóa:

```caddy-d
format <encoder_module> {
	message_key     <key>
	level_key       <key>
	time_key        <key>
	name_key        <key>
	caller_key      <key>
	stacktrace_key  <key>
	line_ending     <char>
	time_format     <format>
	time_local
	duration_format <format>
	level_format    <format>
}
```

- **message_key** <span id="message_key"/> Khóa cho trường thông báo của mục nhật ký. Mặc định: `msg`

- **level_key** <span id="level_key"/> Khóa cho trường mức của mục nhật ký. Mặc định: `level`

- **time_key** <span id="time_key"/> Khóa cho trường thời gian của mục nhật ký. Mặc định: `ts`
- **name_key** <span id="name_key"/> Khóa cho trường tên của mục nhật ký. Mặc định: `name`

- **caller_key** <span id="caller_key"/> Khóa cho trường người gọi của mục nhật ký.

- **stacktrace_key** <span id="stacktrace_key"/> Khóa cho trường stacktrace của mục nhật ký.

- **line_ending** <span id="line_ending"/> Các kết thúc dòng để sử dụng.

- **time_format** <span id="time_format"/> Định dạng cho dấu thời gian.
  Mặc định: `wall_milli` nếu định dạng mặc định là `console`, ngược lại là `unix_seconds_float`.
  
  Có thể là một trong:
  - `unix_seconds_float` Số giây dấu phẩy động kể từ kỷ nguyên Unix.
  - `unix_milli_float` Số mili giây dấu phẩy động kể từ kỷ nguyên Unix.
  - `unix_nano` Số nguyên nano giây kể từ kỷ nguyên Unix.
  - `iso8601` Ví dụ: `2006-01-02T15:04:05.000Z0700`
  - `rfc3339` Ví dụ: `2006-01-02T15:04:05Z07:00`
  - `rfc3339_nano` Ví dụ: `2006-01-02T15:04:05.999999999Z07:00`
  - `wall` Ví dụ: `2006/01/02 15:04:05`
  - `wall_milli` Ví dụ: `2006/01/02 15:04:05.000`
  - `wall_nano` Ví dụ: `2006/01/02 15:04:05.000000000`
  - `common_log` Ví dụ: `02/Jan/2006:15:04:05 -0700`
  - Hoặc, bất kỳ chuỗi bố cục thời gian tương thích nào; xem [tài liệu Go](https://pkg.go.dev/time#pkg-constants) để biết chi tiết đầy đủ.
  
  Lưu ý rằng các phần của chuỗi định dạng là các hằng số đặc biệt cho bố cục; vì vậy `2006` là năm, `01` là tháng, `Jan` là tháng dưới dạng chuỗi, `02` là ngày. Không sử dụng các số ngày hiện tại thực tế trong chuỗi định dạng.

- **time_local** <span id="time_local"/> Nhật ký với thời gian hệ thống địa phương thay vì thời gian UTC mặc định.

- **duration_format** <span id="duration_format"/> Định dạng cho khoảng thời gian.

  Mặc định: `seconds`.
  
  Có thể là một trong:
  - `s`, `second` hoặc `seconds` Số giây dấu phẩy động đã trôi qua.
  - `ms`, `milli` hoặc `millis` Số mili giây dấu phẩy động đã trôi qua.
  - `ns`, `nano` hoặc `nanos` Số nguyên nano giây đã trôi qua.
  - `string` Sử dụng định dạng chuỗi tích hợp của Go, ví dụ `1m32.05s` hoặc `6.31ms`.

- **level_format** <span id="level_format"/> Định dạng cho các mức.

  Mặc định: `color` nếu định dạng mặc định là `console`, ngược lại là `lower`.
  
  Có thể là một trong:
  - `lower` Chữ thường.
  - `upper` Chữ hoa.
  - `color` Chữ hoa, với màu sắc ANSI.
  

#### console

Bộ mã hóa console định dạng mục nhật ký để con người có thể đọc được trong khi vẫn bảo toàn một số cấu trúc.

```caddy-d
format console
```

#### json

Định dạng mỗi mục nhật ký dưới dạng một đối tượng JSON.

```caddy-d
format json
```


#### filter

Cho phép lọc theo từng trường.

```caddy-d
format filter {
	fields {
		<field> <filter> ...
	}
	<field> <filter> ...
	wrap <encode_module> ...
}
```

Các trường lồng nhau có thể được tham chiếu bằng cách biểu thị một lớp lồng nhau bằng `>`. Nói cách khác, đối với một đối tượng như `{"a":{"b":0}}`, trường bên trong có thể được tham chiếu là `a>b`.

Các trường sau đây là cơ bản đối với nhật ký và không thể được lọc vì chúng được thêm vào bởi thư viện ghi nhật ký cơ bản dưới dạng các trường hợp đặc biệt: `ts`, `level`, `logger`, và `msg`.

Chỉ định `wrap` là tùy chọn; nếu bỏ qua, một giá trị mặc định sẽ được chọn tùy thuộc vào việc mô-đun đầu ra hiện tại là [`stderr`](#stderr) hay [`stdout`](#stdout), và là một terminal tương tác, trong trường hợp đó [`console`](#console) được chọn, nếu không thì [`json`](#json) được chọn.

Như một lối tắt, khối `fields` có thể được bỏ qua và các bộ lọc có thể được chỉ định trực tiếp trong khối `filter`.


Đây là các bộ lọc có sẵn:

##### delete

Đánh dấu một trường cần bỏ qua khi mã hóa.

```caddy-d
<field> delete
```


##### rename

Đổi tên khóa của một trường nhật ký.

```caddy-d
<field> rename <key>
```


##### replace

Đánh dấu một trường cần được thay thế bằng chuỗi được cung cấp tại thời điểm mã hóa.

```caddy-d
<field> replace <replacement>
```


##<a id="ip-mask"></a>
<a id="ip-mask"></a>
##### ip_mask

Ẩn các địa chỉ IP trong trường bằng mặt nạ CIDR, tức là số lượng bit từ IP cần giữ lại, bắt đầu từ phía bên trái. Nếu trường là một mảng các chuỗi (ví dụ: các tiêu đề HTTP), mỗi giá trị trong mảng sẽ được ẩn. Giá trị có thể là một chuỗi các địa chỉ IP được phân tách bằng dấu phẩy.

Có cấu hình riêng cho địa chỉ IPv4 và IPv6, vì chúng có tổng số bit khác nhau.

Thông thường nhất, các trường cần lọc sẽ là:
- `request>remote_ip` cho máy khách kết nối trực tiếp
- `request>client_ip` cho "máy khách thực" được phân tích cú pháp khi [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) được cấu hình
- `request>headers>X-Forwarded-For` nếu đứng sau một reverse proxy

```caddy-d
<field> ip_mask [<ipv4> [<ipv6>]] {
	ipv4 <cidr>
	ipv6 <cidr>
}
```


##### query

Đánh dấu một trường để thực hiện một hoặc nhiều hành động, nhằm thao tác phần query của một trường URL. Thông thường nhất, trường cần lọc sẽ là `request>uri`.

```caddy-d
<field> query {
	delete  <key>
	replace <key> <replacement>
	hash    <key>
}
```

Các hành động có sẵn là:

- **delete** loại bỏ khóa đã cho khỏi query.

- **replace** thay thế giá trị của khóa query đã cho bằng **replacement**. Hữu ích để chèn một trình giữ chỗ biên tập; bạn sẽ thấy rằng khóa query đã có trong URL, nhưng giá trị bị ẩn.

- **hash** thay thế giá trị của khóa query đã cho bằng 4 byte đầu tiên của mã băm SHA-256 của giá trị, dưới dạng thập lục phân chữ thường. Hữu ích để che giấu giá trị nếu nó nhạy cảm, đồng thời có thể nhận thấy liệu mỗi yêu cầu có một giá trị khác nhau hay không.


##### cookie

Đánh dấu một trường để thực hiện một hoặc nhiều hành động, nhằm thao tác giá trị của tiêu đề HTTP `Cookie`. Thông thường nhất, trường cần lọc sẽ là `request>headers>Cookie`.

```caddy-d
<field> cookie {
	delete  <name>
	replace <name> <replacement>
	hash    <name>
}
```

Các hành động có sẵn là:

- **delete** loại bỏ cookie đã cho theo tên khỏi tiêu đề.

- **replace** thay thế giá trị của cookie đã cho bằng **replacement**. Hữu ích để chèn một trình giữ chỗ biên tập; bạn sẽ thấy rằng cookie đã có trong tiêu đề, nhưng giá trị bị ẩn.

- **hash** thay thế giá trị của cookie đã cho bằng 4 byte đầu tiên của mã băm SHA-256 của giá trị, dưới dạng thập lục phân chữ thường. Hữu ích để che giấu giá trị nếu nó nhạy cảm, đồng thời có thể nhận thấy liệu mỗi yêu cầu có một giá trị khác nhau hay không.

Nếu nhiều hành động được xác định cho cùng một tên cookie, chỉ hành động đầu tiên sẽ được áp dụng.


##### regexp

Đánh dấu một trường cần được áp dụng thay thế biểu thức chính quy tại thời điểm mã hóa. Nếu trường là một mảng các chuỗi (ví dụ: các tiêu đề HTTP), mỗi giá trị trong mảng sẽ được áp dụng thay thế.

```caddy-d
<field> regexp <pattern> <replacement>
```

Ngôn ngữ biểu thức chính quy được sử dụng là RE2, được bao gồm trong Go. Xem [tham chiếu cú pháp RE2](https://github.com/google/re2/wiki/Syntax) và [tổng quan cú pháp regexp của Go](https://pkg.go.dev/regexp/syntax).

Trong chuỗi thay thế, các nhóm thu giữ có thể được tham chiếu bằng `${group}` trong đó `group` là tên hoặc số của nhóm thu giữ trong biểu thức. Nhóm thu giữ `0` là toàn bộ kết quả khớp regexp, `1` là nhóm thu giữ đầu tiên, `2` là nhóm thu giữ thứ hai, v.v.


##### hash

Đánh dấu một trường cần được thay thế bằng 4 byte đầu tiên (8 ký tự hex) của mã băm SHA-256 của giá trị tại thời điểm mã hóa. Nếu trường là một mảng chuỗi (ví dụ: các tiêu đề HTTP), mỗi giá trị trong mảng sẽ được băm.

Hữu ích để che giấu giá trị nếu nó nhạy cảm, đồng thời có thể nhận thấy liệu mỗi yêu cầu có một giá trị khác nhau hay không.

```caddy-d
<field> hash
```

#### append

Thêm (các) trường vào tất cả các mục nhật ký.

```caddy-d
format append {
	fields {
		<field> <value>
	}
	<field> <value>
	wrap <encode_module> ...
}
```

Nó hữu ích nhất để thêm thông tin về phiên bản Caddy đang tạo ra các mục nhật ký, có thể thông qua một biến môi trường. Các giá trị trường có thể là các trình giữ chỗ toàn cục (ví dụ: `{env.*}`), nhưng *không phải* là các trình giữ chỗ theo từng yêu cầu do nhật ký được viết bên ngoài ngữ cảnh yêu cầu HTTP.

Chỉ định `wrap` là tùy chọn; nếu bỏ qua, một giá trị mặc định sẽ được chọn tùy thuộc vào việc mô-đun đầu ra hiện tại là [`stderr`](#stderr) hay [`stdout`](#stdout), và là một terminal tương tác, trong trường hợp đó [`console`](#console) được chọn, nếu không thì [`json`](#json) được chọn.

Khối `fields` có thể được bỏ qua và các trường có thể được chỉ định trực tiếp trong khối `append`.



<a id="examples"></a>
## Ví dụ

Bật ghi nhật ký truy cập vào logger mặc định.

Nói cách khác, theo mặc định, điều này ghi nhật ký vào `stderr`, nhưng điều này có thể được thay đổi bằng cách cấu hình lại logger `default` với [tùy chọn toàn cục `log`](/docs/caddyfile/options#log):

```caddy
example.com {
	log
}
```


Ghi nhật ký vào một tệp (với tính năng xoay vòng nhật ký, được bật theo mặc định):

```caddy
example.com {
	log {
		output file /var/log/access.log
	}
}
```


Tùy chỉnh xoay vòng nhật ký, xoay vòng hàng ngày vào nửa đêm hoặc khi tệp nhật ký đạt 1 GB (tùy điều kiện nào đến trước), và giữ lại 5 tệp đã xoay hoặc 30 ngày nhật ký:

```caddy
example.com {
	log {
		output file /var/log/access.log {
			roll_at 00:00
			roll_size 1gb
			roll_keep 5
			roll_keep_for 720h
		}
	}
}
```


Xóa tiêu đề yêu cầu `User-Agent` khỏi nhật ký:

```caddy
example.com {
	log {
		format filter {
			request>headers>User-Agent delete
		}
	}
}
```


Biên tập nhiều cookie nhạy cảm. (Lưu ý rằng một số tiêu đề nhạy cảm được ghi nhật ký với giá trị trống theo mặc định; xem [tùy chọn toàn cục `log_credentials`](/docs/caddyfile/options#log-credentials) để bật ghi nhật ký các giá trị tiêu đề `Cookie`):

```caddy
example.com {
	log {
		format filter {
			request>headers>Cookie cookie {
				replace session REDACTED
				delete secret
			}
		}
	}
}
```


Ẩn địa chỉ từ xa khỏi yêu cầu, giữ lại 16 bit đầu tiên (tức là 255.255.0.0) cho địa chỉ IPv4, và 32 bit đầu tiên cho địa chỉ IPv6.

Lưu ý rằng kể từ Caddy v2.7, cả `remote_ip` và `client_ip` đều được ghi nhật ký, trong đó `client_ip` là "IP thực" khi [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) được cấu hình:

```caddy
example.com {
	log {
		format filter {
			request>remote_ip ip_mask 16 32
			request>client_ip ip_mask 16 32
		}
	}
}
```


Để thêm ID máy chủ từ một biến môi trường vào tất cả các mục nhật ký và chuỗi nó với một `filter` để xóa một tiêu đề:

```caddy
example.com {
	log {
		format append {
			server_id {env.SERVER_ID}
			wrap filter {
				request>headers>Cookie delete
			}
		}
	}
}
```


<span id="wildcard-logs" /> Để viết các tệp nhật ký riêng biệt cho mỗi tên miền phụ trong một [site block ký tự đại diện](/docs/caddyfile/patterns#wildcard-certificates), bằng cách ghi đè `hostnames` cho mỗi logger. Điều này sử dụng một [snippet](/docs/caddyfile/concepts#snippets) để tránh lặp lại:

```caddy
(subdomain-log) {
	log {
		hostnames {args[0]}
		output file /var/log/{args[0]}.log
	}
}

*.example.com {
	import subdomain-log foo.example.com
	@foo host foo.example.com
	handle @foo {
		respond "foo"
	}

	import subdomain-log bar.example.com
	@bar host bar.example.com
	handle @bar {
		respond "bar"
	}
}
```

<span id="multiple-outputs" /> Để viết nhật ký truy cập cho một tên miền phụ cụ thể vào hai tệp khác nhau, với các định dạng khác nhau (một với [plugin `transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder) và cái còn lại với [`json`](#json)).

Điều này hoạt động bằng cách ghi đè tên logger thành `foo` trong site block, sau đó bao gồm các nhật ký truy cập được tạo bởi logger đó trong hai logger trong các tùy chọn toàn cục với `include http.log.access.foo`:

```caddy
{
	log access-formatted {
		include http.log.access.foo
		output file /var/log/access-foo.log
		format transform "{common_log}"
	}

	log access-json {
		include http.log.access.foo
		output file /var/log/access-foo.json
		format json
	}
}

foo.example.com {
	log foo
}
```

<span id="sampling-example" /> Để giảm dung lượng nhật ký bằng cách lấy mẫu, ví dụ để giữ lại 5 yêu cầu đầu tiên mỗi giây, sau đó cứ 10 yêu cầu thì giữ lại 1 yêu cầu sau đó:

```caddy
example.com {
	log {
		sampling {
			interval   1s
			first      5
			thereafter 10
		}
	}
}
```
