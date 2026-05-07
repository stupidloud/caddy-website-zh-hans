---
title: "Cài đặt"
---

<a id="install"></a>
# Cài đặt

Trang này mô tả các phương pháp khác nhau để cài đặt Caddy trên hệ thống của bạn.

**Chính thức:**

- [Binary tĩnh](#static-binaries)
- [Gói Debian, Ubuntu, Raspbian](#debian-ubuntu-raspbian)
- [Gói Fedora, RedHat, CentOS](#fedora-redhat-centos)
- [Gói Arch Linux, Manjaro, Parabola](#arch-linux-manjaro-parabola)
- [Hình ảnh Docker](#docker)
- [Mẫu Railway](#railway)

<aside class="tip">

Các [gói chính thức](https://github.com/caddyserver/dist) của chúng tôi chỉ đi kèm với các mô-đun tiêu chuẩn. Nếu bạn cần các plugin của bên thứ ba, hãy [xây dựng từ nguồn với `xcaddy`](/docs/build#xcaddy), sử dụng [trang tải xuống của chúng tôi](/download), hoặc [triển khai trên Railway](#railway).

</aside>


**Do cộng đồng duy trì:**

- [Gentoo](#gentoo)
- [Homebrew (Mac)](#homebrew-mac)
- [Chocolatey (Windows)](#chocolatey-windows)
- [Scoop (Windows)](#scoop-windows)
- [Webi](#webi)
- [Ansible](#ansible)
- [Termux](#termux)
- [Nix/Nixpkgs/NixOS](#nixnixpkgsnixos)
- [Unikraft](#unikraft)
- [OPNsense](#opnsense)
- [Mise](#mise)


<a id="static-binaries"></a>
## Binary tĩnh

**Nếu cài đặt lên một hệ thống thực tế (production), chúng tôi khuyên bạn nên sử dụng gói chính thức cho bản phân phối của mình nếu có sẵn bên dưới.**

1. Lấy file binary của Caddy:
	- [từ các bản phát hành trên GitHub](https://github.com/caddyserver/caddy/releases) (mở rộng phần "Assets")
		- Tham khảo [Xác minh chữ ký tài sản](/docs/signature-verification) để biết cách xác minh chữ ký tài sản
	- [từ trang tải xuống của chúng tôi](/download)
	- [bằng cách xây dựng từ nguồn](/docs/build) (bằng `go` hoặc `xcaddy`)
2. [Cài đặt Caddy như một dịch vụ hệ thống.](/docs/running#manual-installation) Điều này được khuyến khích mạnh mẽ, đặc biệt là đối với các máy chủ thực tế.

Đặt file binary vào một trong các thư mục nằm trong `$PATH` (hoặc `%PATH%` trên Windows) của bạn để bạn có thể chạy `caddy` mà không cần nhập đường dẫn đầy đủ của file thực thi. (Chạy `echo $PATH` để xem danh sách các thư mục đủ điều kiện.)

Bạn có thể nâng cấp các binary tĩnh bằng cách thay thế chúng bằng các phiên bản mới hơn và khởi động lại Caddy. [Lệnh `caddy upgrade`](/docs/command-line#caddy-upgrade) có thể giúp việc này trở nên dễ dàng.



## Debian, Ubuntu, Raspbian

Việc cài đặt gói này sẽ tự động khởi động và chạy Caddy dưới dạng một [dịch vụ systemd](/docs/running#linux-service) có tên là `caddy`. Nó cũng đi kèm với một dịch vụ `caddy-api` tùy chọn vốn *không* được bật theo mặc định, nhưng nên được sử dụng nếu bạn chủ yếu cấu hình Caddy thông qua API của nó thay vì các file cấu hình.

Sau khi cài đặt, vui lòng đọc [hướng dẫn sử dụng dịch vụ](/docs/running#using-the-service).

**Các bản phát hành ổn định (Stable):**

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-stable.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

**Các bản phát hành thử nghiệm (Testing)** (bao gồm các bản beta và bản ứng viên phát hành):

<pre><code class="cmd"><span class="bash">sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">curl -1sLf 'https://dl.cloudsmith.io/public/caddy/testing/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo chmod o+r /usr/share/keyrings/caddy-testing-archive-keyring.gpg</span>
<span class="bash">sudo chmod o+r /etc/apt/sources.list.d/caddy-testing.list</span>
<span class="bash">sudo apt update</span>
<span class="bash">sudo apt install caddy</span></code></pre>

[**Xem các kho lưu trữ Cloudsmith**](https://cloudsmith.io/~caddy/repos/)

Nếu bạn muốn sử dụng các file hỗ trợ được đóng gói (dịch vụ systemd, bash completion và cấu hình mặc định) với một bản xây dựng Caddy tùy chỉnh, bạn có thể [tìm thấy hướng dẫn tại đây](/docs/build#package-support-files-for-custom-builds-for-debianubunturaspbian).


## Fedora, RedHat, CentOS

Gói này đi kèm với cả hai file đơn vị [dịch vụ systemd](/docs/running#linux-service) của Caddy, nhưng không bật chúng theo mặc định. Việc sử dụng dịch vụ được khuyến khích. Nếu bạn làm vậy, vui lòng đọc [hướng dẫn sử dụng dịch vụ](/docs/running#using-the-service).

Fedora:

<pre><code class="cmd"><span class="bash">dnf install dnf5-plugins</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

CentOS/RHEL:

<pre><code class="cmd"><span class="bash">dnf install dnf-plugins-core</span>
<span class="bash">dnf copr enable @caddy/caddy</span>
<span class="bash">dnf install caddy</span></code></pre>

[**Xem Caddy COPR**](https://copr.fedorainfracloud.org/coprs/g/caddy/caddy/)


## Arch Linux, Manjaro, Parabola

Gói này đi kèm với các phiên bản đã được sửa đổi nhiều của cả hai file đơn vị [dịch vụ systemd](/docs/running#linux-service) của Caddy, nhưng không bật chúng theo mặc định.
Những sửa đổi đó bao gồm hành vi bắt đầu/dừng tùy chỉnh và các cờ sandboxing bổ sung được giải thích trong [tài liệu thực thi của systemd](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Sandboxing), điều này có thể dẫn đến việc một số thư mục máy chủ không khả dụng cho tiến trình Caddy. 

<pre><code class="cmd"><span class="bash">pacman -Syu caddy</span></code></pre>

[**Xem Caddy trong kho lưu trữ Arch Linux**](https://archlinux.org/packages/extra/x86_64/caddy/) và [**Arch Linux Wiki**](https://wiki.archlinux.org/title/Caddy)

## Docker

<pre><code class="cmd bash">docker pull caddy</code></pre>

[**Xem trên Docker Hub**](https://hub.docker.com/_/caddy)

Xem [cấu hình Docker Compose được khuyến nghị](/docs/running#docker-compose) và hướng dẫn sử dụng của chúng tôi.


## Railway

Thông qua sự tài trợ từ [Railway](https://railway.com), chúng tôi chính thức hỗ trợ mẫu này:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/caddy?referralCode=YOPtw9&utm_medium=integration&utm_source=template&utm_campaign=generic)


## Gentoo

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

<pre><code class="cmd">emerge www-servers/caddy</code></pre>

[**Xem gói Gentoo**](https://packages.gentoo.org/packages/www-servers/caddy)



## Homebrew (Mac)

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

<pre><code class="cmd bash">brew install caddy</code></pre>

[**Xem công thức Homebrew**](https://formulae.brew.sh/formula/caddy)



## Chocolatey (Windows)

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

<pre><code class="cmd">choco install caddy</code></pre>

[**Xem gói Chocolatey**](https://chocolatey.org/packages/caddy)



## Scoop (Windows)

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

<pre><code class="cmd">scoop install caddy</code></pre>

[**Xem bản kê khai Scoop**](https://github.com/ScoopInstaller/Main/blob/master/bucket/caddy.json)



## Webi

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

Linux và macOS:

<pre><code class="cmd bash">curl -sS https://webi.sh/caddy | sh</code></pre>

Windows:

<pre><code class="cmd">curl.exe https://webi.ms/caddy | powershell</code></pre>

Bạn có thể cần điều chỉnh các quy tắc tường lửa của Windows để cho phép các kết nối đến không phải từ localhost.

[**Xem trên Webi**](https://webinstall.dev/caddy)



## Ansible

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

<pre><code class="cmd bash">ansible-galaxy install nvjacobo.caddy</code></pre>

[**Xem kho lưu trữ vai trò Ansible**](https://github.com/nvjacobo/caddy)



## Termux

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

<pre><code class="cmd">pkg install caddy</code></pre>

[**Xem file build.sh của Termux**](https://github.com/termux/termux-packages/blob/master/packages/caddy/build.sh)



## Nix/Nixpkgs/NixOS

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

- Tên gói: [`caddy`](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy)
- Mô-đun NixOS: [`services.caddy`](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)

[**Xem Caddy trong tìm kiếm Nixpkgs](https://search.nixos.org/packages?channel=unstable&show=caddy&query=caddy) và [tìm kiếm các tùy chọn NixOS](https://search.nixos.org/options?channel=unstable&show=services.caddy.enable&query=services.caddy)**



## Unikraft

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

Trước tiên, hãy cài đặt công cụ đồng hành của Unikraft, [`kraft`](https://unikraft.org/docs/cli):

<pre><code class="cmd">curl --proto '=https' --tlsv1.2 -sSf https://get.kraftkit.sh | sh</code></pre>

Sau đó chạy Caddy với Unikraft bằng cách sử dụng:

<pre><code class="cmd">kraft run --rm -p 2015:2015 --plat qemu --arch x86_64 -M 256M caddy:2.7</code></pre>

Để cho phép các kết nối đến không phải từ localhost, bạn cần [kết nối phiên bản unikernel với mạng](https://unikraft.org/docs/cli/running#connecting-a-unikernel-instance-to-a-network).

[**Xem danh mục ứng dụng Unikraft](https://github.com/unikraft/catalog/tree/main/examples/caddy) và [các ví dụ về nền tảng KraftCloud (được cung cấp bởi Unikraft)](https://github.com/kraftcloud/examples/tree/main/caddy).**



## OPNsense

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

<pre><code class="cmd">pkg install os-caddy</code></pre>

[**Xem makefile caddy-custom của FreeBSD](https://github.com/opnsense/ports/blob/master/www/caddy-custom/Makefile) và [nguồn plugin os-caddy](https://github.com/opnsense/plugins/tree/master/www/caddy)**

## Mise

*Lưu ý: Đây là phương pháp cài đặt do cộng đồng duy trì.*

Nếu bạn đang sử dụng [mise](https://github.com/jdx/mise), trình quản lý phiên bản công cụ đa ngôn ngữ, bạn có thể sử dụng một lệnh như thế này để cài đặt phiên bản mới nhất:

<pre><code class="cmd">mise use -g caddy@latest</code></pre>
