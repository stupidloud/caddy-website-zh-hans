---
title: "从源代码编译"
---

<a id="build-from-source"></a>
# 从源代码编译

构建 Caddy 有多种选项，如果您需要自定义构建（例如包含插件）：
- [Git](#git)：从 Git 仓库构建
- [`xcaddy`](#xcaddy)：使用 `xcaddy`
- [Docker](#docker)：构建自定义 Docker 镜像

要求：

- [Go](https://golang.org/doc/install) 1.20 或更高版本

“[软件包支持文件](#package-support-files-for-custom-builds-for-debianubunturaspbian)”部分提供了相关说明，适用于在Debian衍生系统上使用APT命令安装Caddy，但仍需使用自定义构建的可执行文件进行操作的用户。



<a id="git"></a>
## Git

要求：

- 已安装 Go（参见上文）

克隆仓库：

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

如果您没有安装 Git，可以[从 GitHub](https://github.com/caddyserver/caddy) 下载源代码压缩包。每个[版本](https://github.com/caddyserver/caddy/releases)还提供源代码快照。

构建：

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>


<aside class="tip">

由于 [Go 语言中存在一个漏洞](https://github.com/golang/go/issues/29228)，这些基本步骤不会嵌入版本信息。如果您需要版本号（`caddy version`)，则需将 Caddy 作为依赖项而非主模块进行编译。具体操作指南详见 Caddy 的 [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) 文件。或者，您可以使用 [`xcaddy`](#xcaddy) 来实现自动化操作。

</aside>

Go 程序很容易编译到其他平台上。只需设置 `GOOS`, `GOARCH`和/或 `GOARM` 环境变量即可。（[详情请参阅 Go 文档。](https://golang.org/doc/install/source#environment)）

例如，当您不在 Windows 系统上时，要编译适用于 Windows 的 Caddy：

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

或者，对于 Linux ARMv6，当你不在 Linux 系统上或不在 ARMv6 架构上时：

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



<a id="xcaddy"></a>
## xcaddy

[`xcaddy` 命令](https://github.com/caddyserver/xcaddy)是构建包含版本信息和/或插件的 Caddy 的最简单方法。

要求：

- 已安装 Go（参见上文）
- 请确保 [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) 位于您的 `PATH`

您**无需**下载 Caddy 的源代码（系统会自动为您完成）。

那么，构建 Caddy（包含版本信息）就变得非常简单：

<pre><code class="cmd bash">xcaddy build</code></pre>

要使用插件进行构建，请使用 `--with`:

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter
	--with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

如您所见，您可以使用 `@` 语法。版本可以是标签名称、提交 SHA 或分支。

使用 `xcaddy` 与 `go` 命令的效果相同。例如，要针对 macOS 进行交叉编译：

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



<a id="docker"></a>
## Docker

您可以使用 `:builder` 该图像作为构建包含自定义模块的新 Caddy 二进制文件的快捷方式：

```Dockerfile
FROM caddy:<version>-builder AS builder

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
    --with github.com/hairyhenderson/caddy-teapot-module@v0.0.3-0

FROM caddy:<version>

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

请务必将 `<version>` 替换为最新版本的 Caddy 才能开始。

请注意第二个 `FROM` 指令——这通过将新构建的二进制文件简单地叠加在常规 `caddy` 图像上，便能生成一张体积小得多的图像。

构建程序使用 `xcaddy` 来使用提供的模块构建 Caddy，其流程与[上述概述的](#xcaddy)类似。该 `--mount=type=cache,target=/go/pkg/mod` 和 `--mount=type=cache,target=/root/.cache/go-build` 选项分别用于缓存 Go 模块依赖项和构建产物，从而加快后续构建的速度。该标志是 [Docker 的功能](https://docs.docker.com/build/cache/optimize/#use-cache-mounts)，而非 `xcaddy`.

如需使用 Docker Compose，请参阅我们推荐的《[`compose.yml`](/docs/running#docker-compose)》及使用指南。



<a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>
## 适用于 Debian/Ubuntu/Raspbian 自定义构建的软件包支持文件

此流程旨在简化运行自定义 `caddy` 二进制文件，同时保留 `caddy` 。

此操作可让用户利用官方软件包中的默认配置、systemd 服务文件以及 bash 补全功能。

要求：
- 请按照以下说明安装 `caddy` 按照[这些说明](/docs/install#debian-ubuntu-raspbian)安装该软件包
- 构建您的自定义 `caddy` 二进制文件（参见前文），或[下载](/download)自定义构建版本
- 您的自定义 `caddy` 二进制文件应位于当前目录中

步骤：
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

说明：

- `dpkg-divert` 将移动 `/usr/bin/caddy` 二进制文件至 `/usr/bin/caddy.default` ，并设置重定向，以防有软件包需要将文件安装到此位置。

- `update-alternatives` 将从目标 caddy 二进制文件创建一个符号链接到 `/usr/bin/caddy`

- `systemctl restart caddy` 将关闭 Caddy 服务器的默认版本，并启动自定义版本。

您可以通过执行以下命令并按照屏幕上的提示操作，在自定义和默认 `caddy` 二进制文件，请执行以下操作并按照屏幕上的提示进行。随后，请重启 Caddy 服务。

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

若要在此之后升级 Caddy，您可以运行 [`caddy upgrade`](/docs/command-line#caddy-upgrade)。该命令会尝试[下载](/download)一个与您当前构建版本包含相同插件、但采用最新 Caddy 版本的构建包，然后用新二进制文件替换当前的二进制文件。
