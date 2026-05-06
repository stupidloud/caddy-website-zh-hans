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

“[软件包支持文件](#package-support-files-for-custom-builds-for-debianubunturaspbian)”一节说明了在 Debian 衍生系统上通过 APT 安装 Caddy 后，仍想使用自定义构建二进制文件的场景。



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

例如，如果您不在 Windows 系统上，要编译适用于 Windows 的 Caddy：

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

或者，在 Linux ARMv6 上编译时（且当前不在 Linux 或 ARMv6 环境时）：

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



<a id="xcaddy"></a>
## xcaddy

[`xcaddy` 命令](https://github.com/caddyserver/xcaddy)是构建包含版本信息和/或插件的 Caddy 最便捷的方式。

要求：

- 已安装 Go（参见上文）
- 请确保 [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) 位于您的 `PATH`

您**不必**下载 Caddy 的源代码，系统会代为下载。

构建 Caddy（包含版本信息）并不复杂：

<pre><code class="cmd bash">xcaddy build</code></pre>

要使用插件进行构建，请使用 `--with`:

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter
	--with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

如您所见，版本可通过 `@` 语法指定；版本可为标签名称、提交 SHA 或分支名。

使用 `xcaddy` 与 `go` 命令的效果相同。例如，要针对 macOS 进行交叉编译：

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



<a id="docker"></a>
## Docker

您可以使用 `:builder` 镜像作为构建包含自定义模块的新 Caddy 二进制文件的快捷方式：

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

请注意第二个 `FROM` 指令——它会将新构建的二进制文件叠加到常规 `caddy` 镜像上，从而生成体积更小的镜像。

构建过程使用 `xcaddy` 和所选模块构建 Caddy，流程与[上述说明](#xcaddy)一致。`--mount=type=cache,target=/go/pkg/mod` 与 `--mount=type=cache,target=/root/.cache/go-build` 选项分别用于缓存 Go 模块依赖和构建产物，从而加快后续构建。该标志是 [Docker 的功能](https://docs.docker.com/build/cache/optimize/#use-cache-mounts)，不是 `xcaddy` 的。

如需使用 Docker Compose，请参阅我们推荐的 [`compose.yml`](/docs/running#docker-compose) 和使用说明。



<a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>
## 适用于 Debian/Ubuntu/Raspbian 自定义构建的软件包支持文件

此流程旨在简化运行自定义 `caddy` 二进制文件，并保留 `caddy` 的 systemd 服务文件和 bash 补全等支持文件。

此操作可让您复用官方软件包中的默认配置、systemd 服务文件和 bash 补全功能。

要求：
- 按照[这些说明](/docs/install#debian-ubuntu-raspbian)安装 `caddy` 软件包
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

- `dpkg-divert` 将 `/usr/bin/caddy` 二进制文件移动到 `/usr/bin/caddy.default`，并创建重定向，以防有软件包尝试写入该路径。

- `update-alternatives` 会从目标的 `caddy` 二进制文件创建到 `/usr/bin/caddy` 的符号链接。

- `systemctl restart caddy` 将关闭 Caddy 服务器的默认版本，并启动自定义版本。

您可通过执行以下命令并按提示，在自定义与默认 `caddy` 二进制文件之间切换；随后重启 Caddy 服务。

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

若要在此之后升级 Caddy，您可以运行 [`caddy upgrade`](/docs/command-line#caddy-upgrade)。该命令会尝试[下载](/download)一个与您当前构建版本包含相同插件、但采用最新 Caddy 版本的构建包，然后用新二进制文件替换当前的二进制文件。
