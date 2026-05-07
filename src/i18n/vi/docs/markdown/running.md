---
title: Duy trì Caddy chạy
---

<a id="keep-caddy-running"></a>
# Duy trì Caddy chạy

Mặc dù Caddy có thể được chạy trực tiếp bằng [giao diện dòng lệnh](/docs/command-line) của nó, nhưng có rất nhiều lợi thế khi sử dụng một trình quản lý dịch vụ để duy trì nó chạy, chẳng hạn như đảm bảo nó tự động khởi động khi hệ thống khởi động lại và để thu thập nhật ký stdout/stderr.


- [Dịch vụ Linux](#linux-service)
  - [Tệp Unit](#unit-files)
  - [Cài đặt thủ công](#manual-installation)
  - [Sử dụng dịch vụ](#using-the-service)
  - [HTTPS cục bộ](#local-https-with-systemd)
  - [Ghi đè](#overrides)
	- [Biến môi trường](#environment-variables)
	- [Ghi đè `run` và `reload`](#run-and-reload-override)
	- [Khởi động lại khi gặp sự cố](#restart-on-crash)
  - [Cân nhắc về SELinux](#selinux-considerations)
- [Dịch vụ Windows](#windows-service)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [Thiết lập](#setup)
  - [Sử dụng](#usage)
  - [HTTPS cục bộ](#local-https-with-docker)


<a id="linux-service"></a>
## Dịch vụ Linux

Cách được khuyến nghị để chạy Caddy trên các bản phân phối Linux sử dụng systemd là với các tệp unit systemd chính thức của chúng tôi.


<a id="unit-files"></a>
### Tệp Unit

Chúng tôi cung cấp hai tệp unit systemd khác nhau mà bạn có thể lựa chọn tùy theo trường hợp sử dụng của mình:

- [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service) nếu bạn cấu hình Caddy bằng [Caddyfile](/docs/caddyfile). Nếu bạn muốn sử dụng một config adapter khác hoặc tệp cấu hình JSON, bạn có thể [ghi đè](#overrides) các lệnh `ExecStart` và `ExecReload`.

- [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service) nếu bạn chỉ cấu hình Caddy thông qua [API](/docs/api). Dịch vụ này sử dụng tùy chọn [`--resume`](/docs/command-line#caddy-run) sẽ khởi động Caddy bằng `autosave.json` vốn được [lưu trữ lâu dài](/docs/json/admin/config/) theo mặc định.

Chúng rất giống nhau, nhưng khác nhau ở lệnh `ExecStart` và `ExecReload` để phù hợp với quy trình làm việc.

Nếu bạn cần chuyển đổi giữa các dịch vụ, bạn nên vô hiệu hóa và dừng dịch vụ trước đó trước khi kích hoạt và khởi động dịch vụ kia. Ví dụ: để chuyển từ dịch vụ `caddy` sang dịch vụ `caddy-api`:
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>


<a id="manual-installation"></a>
### Cài đặt thủ công

Một số [phương pháp cài đặt](/docs/install) tự động thiết lập Caddy để chạy như một dịch vụ. Nếu bạn chọn một phương pháp không làm như vậy, bạn có thể làm theo các hướng dẫn sau:

**Yêu cầu:**

- Tệp thực thi `caddy` mà bạn đã [tải xuống](/download) hoặc [xây dựng từ mã nguồn](/docs/build)
- `systemctl --version` 232 hoặc mới hơn
- Quyền `sudo`

Di chuyển tệp thực thi caddy vào `$PATH` của bạn, ví dụ:
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

Kiểm tra xem nó có hoạt động không:
<pre><code class="cmd bash">caddy version</code></pre>

Tạo một nhóm tên là `caddy`:
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

Tạo một người dùng tên là `caddy` với thư mục gốc (home directory) có thể ghi được:
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

Nếu sử dụng tệp cấu hình, hãy đảm bảo rằng người dùng `caddy` bạn vừa tạo có thể đọc được tệp đó.

Tiếp theo, [chọn một tệp unit systemd](#unit-files) dựa trên trường hợp sử dụng của bạn.

**Kiểm tra kỹ các chỉ thị `ExecStart` và `ExecReload`.** Đảm bảo vị trí của tệp thực thi và các đối số dòng lệnh là chính xác cho bản cài đặt của bạn! Ví dụ: nếu sử dụng tệp cấu hình, hãy thay đổi đường dẫn `--config` nếu nó khác với mặc định.

Vị trí thông thường để lưu tệp dịch vụ là: `/etc/systemd/system/caddy.service`

Sau khi lưu tệp dịch vụ, bạn có thể khởi động dịch vụ lần đầu tiên bằng các lệnh systemctl thông thường:

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

Xác minh rằng nó đang chạy:
<pre><code class="cmd bash">systemctl status caddy</code></pre>

Bây giờ bạn đã sẵn sàng để [sử dụng dịch vụ](#using-the-service)!



<a id="using-the-service"></a>
### Sử dụng dịch vụ

Nếu sử dụng Caddyfile, bạn có thể chỉnh sửa cấu hình của mình bằng `nano`, `vi` hoặc trình soạn thảo văn bản yêu thích của bạn:
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

Bạn có thể đặt các tệp trang web tĩnh của mình trong `/var/www/html` hoặc `/srv`. Đảm bảo người dùng `caddy` có quyền đọc các tệp này.

Để xác minh rằng dịch vụ đang chạy:
<pre><code class="cmd bash">systemctl status caddy</code></pre>
Lệnh status cũng sẽ hiển thị vị trí của tệp dịch vụ hiện đang chạy.

Khi chạy với tệp dịch vụ chính thức của chúng tôi, đầu ra của Caddy sẽ được chuyển hướng đến `journalctl`. Để đọc nhật ký đầy đủ và tránh các dòng bị cắt ngắn:
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

Nếu sử dụng tệp cấu hình, bạn có thể tải lại Caddy một cách an toàn sau khi thực hiện bất kỳ thay đổi nào:
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

Bạn có thể dừng dịch vụ bằng lệnh:
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

Không dừng dịch vụ để thay đổi cấu hình của Caddy. Việc dừng máy chủ sẽ gây ra thời gian chết (downtime). Hãy sử dụng lệnh reload thay thế.

</aside>

Tiến trình Caddy sẽ chạy dưới tên người dùng `caddy`, với `$HOME` được đặt thành `/var/lib/caddy`. Điều này có nghĩa là:
- [Vị trí lưu trữ dữ liệu](/docs/conventions#data-directory) mặc định (cho các chứng chỉ và thông tin trạng thái khác) sẽ nằm trong `/var/lib/caddy/.local/share/caddy`.
- [Vị trí lưu trữ cấu hình](/docs/conventions#configuration-directory) mặc định (cho cấu hình JSON tự động lưu, chủ yếu hữu ích cho dịch vụ `caddy-api`) sẽ nằm trong `/var/lib/caddy/.config/caddy`.


<a id="local-https-with-systemd"></a>
### HTTPS cục bộ với systemd

Khi sử dụng Caddy để phát triển cục bộ với HTTPS, bạn có thể sử dụng một [hostname](/docs/caddyfile/concepts#addresses) như `localhost` hoặc `app.localhost`. Điều này kích hoạt [HTTPS cục bộ](/docs/automatic-https#local-https) bằng cách sử dụng CA cục bộ của Caddy để cấp chứng chỉ. 

Vì Caddy chạy dưới tên người dùng `caddy` khi chạy như một dịch vụ, nó sẽ không có quyền cài đặt chứng chỉ root CA của mình vào kho lưu trữ tin cậy của hệ thống. Để làm điều này, hãy chạy [`sudo caddy trust`](/docs/command-line#caddy-trust) để thực hiện cài đặt.

Nếu bạn muốn các thiết bị khác kết nối với máy chủ của mình khi sử dụng [issuer `internal`](/docs/caddyfile/directives/tls#internal), bạn cũng sẽ cần cài đặt chứng chỉ root CA trên các thiết bị đó. Bạn có thể tìm thấy chứng chỉ root CA tại `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt`. Nhiều trình duyệt web hiện nay sử dụng kho lưu trữ tin cậy của riêng chúng (bỏ qua kho lưu trữ tin cậy của hệ thống), vì vậy bạn cũng có thể cần cài đặt chứng chỉ thủ công ở đó.


<a id="overrides"></a>
### Ghi đè

Cách tốt nhất để ghi đè các khía cạnh của tệp dịch vụ là sử dụng lệnh này:
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

Lệnh này sẽ mở một tệp trống bằng trình soạn thảo văn bản mặc định của bạn, nơi bạn có thể ghi đè hoặc thêm các chỉ thị vào định nghĩa unit. Đây được gọi là tệp "drop-in".

<a id="environment-variables"></a>
#### Biến môi trường

Nếu bạn cần định nghĩa các biến môi trường để sử dụng trong cấu hình của mình, bạn có thể làm như sau:
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

Tương tự, nếu bạn muốn duy trì một tệp riêng biệt để quản lý các biến môi trường (envfile), bạn có thể sử dụng chỉ thị [`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) như sau:
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

Khi đó, tệp `/etc/caddy/.env` của bạn có thể trông như thế này (không sử dụng dấu ngoặc kép `"` quanh các giá trị):

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

<a id="and-override"></a>
<a id="run-and-reload-override"></a>
#### Ghi đè `run` và `reload`

Nếu bạn cần thay đổi tệp cấu hình từ Caddyfile mặc định sang sử dụng tệp JSON (lưu ý rằng các chỉ thị `Exec*` [phải được đặt lại bằng các chuỗi trống](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=) trước khi đặt giá trị mới):
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

<a id="restart-on-crash"></a>
#### Khởi động lại khi gặp sự cố

Nếu bạn muốn caddy tự khởi động lại sau 5 giây nếu nó gặp sự cố bất ngờ:
```systemd
[Service]
<a id="automatically-restart-caddy-if-it-crashes-except-if-the-exit-code-was-1"></a>
# Tự động khởi động lại caddy nếu nó gặp sự cố ngoại trừ khi mã thoát là 1
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

Sau đó, lưu tệp và thoát trình soạn thảo văn bản, và khởi động lại dịch vụ để thay đổi có hiệu lực:
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>



<a id="selinux-considerations"></a>
### Cân nhắc về SELinux

Trên các hệ thống đã bật SELinux, bạn có hai lựa chọn:
1. Cài đặt Caddy bằng [kho lưu trữ COPR](/docs/install#fedora-redhat-centos). Tệp systemd và tệp thực thi caddy của bạn đã được tạo và gán nhãn chính xác (vì vậy bạn có thể bỏ qua phần này). Nếu bạn muốn sử dụng một bản dựng tùy chỉnh của Caddy, bạn sẽ cần gán nhãn cho tệp thực thi như mô tả bên dưới.

2. [Tải xuống Caddy từ trang web này](/download) hoặc biên dịch nó bằng [`xcaddy`](https://github.com/caddyserver/xcaddy). Trong cả hai trường hợp, bạn sẽ cần tự gán nhãn cho các tệp.

Các tệp unit systemd và các tệp thực thi của chúng sẽ không được chạy trừ khi được gán nhãn tương ứng là `systemd_unit_file_t` và `bin_t`.

Nhãn `systemd_unit_file_t` được tự động áp dụng cho các tệp được tạo trong `/etc/systemd/...`, vì vậy hãy đảm bảo tạo tệp `caddy.service` của bạn ở đó, theo hướng dẫn [cài đặt thủ công](#manual-installation).

Để gắn thẻ cho tệp thực thi `caddy`, bạn có thể sử dụng lệnh sau:
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

<a id="windows-service"></a>
## Dịch vụ Windows

Có hai cách để chạy Caddy dưới dạng dịch vụ trên Windows: [sc.exe](#scexe) hoặc [WinSW](#winsw).

### sc.exe

Để tạo dịch vụ, hãy chạy:

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "YOURPATH\caddy.exe run"</code></pre>

(thay thế `YOURPATH` bằng đường dẫn thực tế đến tệp `caddy.exe` của bạn)

Để khởi động:

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

Để dừng:

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>


### WinSW

Cài đặt Caddy như một dịch vụ trên Windows bằng các hướng dẫn sau.

**Yêu cầu:**

- Tệp thực thi `caddy.exe` mà bạn đã [tải xuống](/download) hoặc [xây dựng từ mã nguồn](/docs/build)
- Bất kỳ tệp `.exe` nào từ bản phát hành mới nhất của trình bao bọc dịch vụ [WinSW](https://github.com/winsw/winsw/releases/latest) (cấu hình dịch vụ bên dưới được viết cho các bản phát hành v2.x)

Đặt tất cả các tệp vào một thư mục dịch vụ. Trong các ví dụ sau, chúng tôi sử dụng `C:\caddy`.

Đổi tên tệp `WinSW-x64.exe` thành `caddy-service.exe`.

Thêm tệp `caddy-service.xml` vào cùng thư mục đó:

```xml
<service>
  <id>caddy</id>
  <!-- Tên hiển thị của dịch vụ -->
  <name>Caddy Web Server (powered by WinSW)</name>
  <!-- Mô tả dịch vụ -->
  <description>Caddy Web Server (https://caddyserver.com/)</description>
  <executable>%BASE%\caddy.exe</executable>
  <arguments>run</arguments>
  <log mode="roll-by-time">
    <pattern>yyyy-MM-dd</pattern>
  </log>
</service>
```

Bây giờ bạn có thể cài đặt dịch vụ bằng lệnh:
<pre><code class="cmd bash">caddy-service install</code></pre>

Bạn có thể muốn khởi động Windows Services Console để xem dịch vụ có chạy chính xác hay không:
<pre><code class="cmd bash">services.msc</code></pre>

Lưu ý rằng các dịch vụ Windows không thể được tải lại, vì vậy bạn phải yêu cầu caddy tải lại trực tiếp:
<pre><code class="cmd bash">caddy reload</code></pre>

Có thể khởi động lại thông qua các lệnh dịch vụ thông thường của Windows, ví dụ thông qua tab "Services" của Task Manager.

Để tùy chỉnh trình bao bọc dịch vụ, hãy xem [tài liệu WinSW](https://github.com/winsw/winsw/tree/master#usage)


## Docker Compose

Cách đơn giản nhất để bắt đầu và vận hành với Docker là sử dụng Docker Compose. Xem tài liệu trên [Docker Hub](https://hub.docker.com/_/caddy) để biết thêm các chi tiết bổ sung về hình ảnh Docker chính thức của Caddy.

<aside class="tip">

Điều này giả định rằng bạn đang sử dụng [Docker Compose V2](https://docs.docker.com/compose/reference/), nơi lệnh hiện nay là `docker compose` (có dấu cách) thay vì `docker-compose` (có dấu gạch ngang) của V1.

</aside>

<a id="setup"></a>
### Thiết lập

Đầu tiên, tạo một tệp `compose.yml` (hoặc thêm dịch vụ này vào tệp hiện có của bạn):

```yaml
services:
  caddy:
    image: caddy:<version>
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./conf:/etc/caddy
      - ./site:/srv
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

Đảm bảo điền hình ảnh `<version>` với số phiên bản mới nhất, bạn có thể tìm thấy trong phần "Tags" trên [Docker Hub](https://hub.docker.com/_/caddy).

Những gì thiết lập này thực hiện:

- Sử dụng chính sách khởi động lại `unless-stopped` để đảm bảo container Caddy tự động khởi động lại khi máy của bạn được khởi động lại.
- Liên kết với các cổng `80` và `443` tương ứng cho HTTP và HTTPS, cộng với `443/udp` cho HTTP/3.
- Gắn thư mục `conf` chứa cấu hình Caddyfile của bạn.
- Gắn thư mục `site` để phục vụ các tệp tĩnh của trang web từ `/srv`.
- Các volume được đặt tên cho `/data` và `/config` để [lưu trữ thông tin quan trọng](/docs/conventions#file-locations).

Sau đó, tạo một tệp tên là `Caddyfile` là tệp duy nhất trong thư mục `conf` và viết cấu hình [Caddyfile](/docs/caddyfile/concepts) của bạn.

Nếu bạn có các tệp tĩnh cần phục vụ, bạn có thể đặt chúng trong thư mục `site/` bên cạnh các cấu hình, sau đó đặt [`root`](/docs/caddyfile/directives/root) bằng lệnh `root /srv`. Nếu không, bạn có thể xóa phần gắn volume `/srv`.

<aside class="tip">

Nếu bạn đang sử dụng Caddy để làm [reverse proxy](/docs/caddyfile/directives/reverse_proxy) cho một container khác, hãy nhớ rằng trong mạng Docker, `localhost` có nghĩa là "container này", chứ không phải "máy này". Vì vậy, ví dụ, không sử dụng `reverse_proxy localhost:8080`, thay vào đó hãy sử dụng `reverse_proxy other-container:8080` 

</aside>

Nếu bạn cần một bản dựng Caddy tùy chỉnh với các plugin, hãy làm theo [hướng dẫn xây dựng Docker](/docs/build#docker) để tạo một hình ảnh Docker tùy chỉnh. Tạo `Dockerfile` bên cạnh `compose.yml` của bạn, sau đó thay thế dòng `image:` trong `compose.yml` bằng `build: .`.



<a id="usage"></a>
### Sử dụng

Sau đó, bạn có thể khởi động container:
<pre><code class="cmd bash">docker compose up -d</code></pre>

Để tải lại Caddy sau khi thực hiện các thay đổi đối với Caddyfile của bạn:
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

Kể từ v2.11.0, bạn có thể tải lại bằng cách sử dụng `SIGUSR1`, với điều kiện Caddy được khởi động bằng `caddy run` và một tệp cấu hình:
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

Để xem 1000 nhật ký gần đây nhất của Caddy và sử dụng `f` để xem các nhật ký mới đang truyền vào:
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

<a id="local-https-with-docker"></a>
### HTTPS cục bộ với Docker

Khi sử dụng Docker để phát triển cục bộ với HTTPS, bạn có thể sử dụng một [hostname](/docs/caddyfile/concepts#addresses) như `localhost` hoặc `app.localhost`. Điều này kích hoạt [HTTPS cục bộ](/docs/automatic-https#local-https) bằng cách sử dụng CA cục bộ của Caddy để cấp chứng chỉ. Điều này có nghĩa là các máy khách HTTP bên ngoài container sẽ không tin tưởng chứng chỉ TLS được phục vụ bởi Caddy. Để giải quyết vấn đề này, bạn có thể cài đặt chứng chỉ root CA của Caddy vào kho lưu trữ tin cậy của máy chủ vật lý:

<div x-data="{ os: $persist(defaultOS(['linux', 'mac', 'windows'], 'linux')) }" class="tabs">
<div class="tab-buttons">
	<button x-on:click="os = 'linux'" x-bind:class="{ active: os === 'linux' }">Linux</button>
	<button x-on:click="os = 'mac'" x-bind:class="{ active: os === 'mac' }">Mac</button>
	<button x-on:click="os = 'windows'" x-bind:class="{ active: os === 'windows' }">Windows</button>
</div>

<div x-show="os === 'linux'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /usr/local/share/ca-certificates/root.crt \
  && sudo update-ca-certificates</code></pre>

</div>

<div x-show="os === 'mac'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /tmp/root.crt \
  && sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain /tmp/root.crt</code></pre>

</div>

<div x-show="os === 'windows'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    %TEMP%/root.crt \
  && certutil -addstore -f "ROOT" %TEMP%/root.crt</code></pre>

</div>
</div>

Nhiều trình duyệt web hiện nay sử dụng kho lưu trữ tin cậy của riêng chúng (bỏ qua kho lưu trữ tin cậy của hệ thống), vì vậy bạn cũng có thể cần cài đặt chứng chỉ thủ công ở đó, bằng cách sử dụng tệp `root.crt` được sao chép từ container trong lệnh trên.

- Đối với Firefox, đi tới Preferences > Privacy & Security > Certificates > View Certificates > Authorities > Import, và chọn tệp `root.crt`.

- Đối với Chrome, đi tới Settings > Privacy and security > Security > Manage certificates > Authorities > Import, và chọn tệp `root.crt`.
