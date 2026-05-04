---
title: "保持 Caddy 运行"
---

<a id="keep-caddy-running"></a>
# 保持 Caddy 运行

虽然可以直接通过[命令行界面](/docs/command-line)运行 Caddy，但使用服务管理器来维持其运行具有诸多优势，例如确保系统重启时它能自动启动，以及捕获 stdout/stderr 日志。


- [Linux 服务](#linux-service)
  - [单元文件](#unit-files)
  - [手动安装](#manual-installation)
  - [使用本服务](#using-the-service)
  - [本地 HTTPS](#local-https-with-systemd)
  - [覆盖](#overrides)
	- [环境变量](#environment-variables)
	- [`run` 和 `reload` 覆盖](#run-and-reload-override)
	- [发生崩溃时重启](#restart-on-crash)
  - [SELinux 注意事项](#selinux-considerations)
- [Windows 服务](#windows-service)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [设置](#setup)
  - [用法](#usage)
  - [本地 HTTPS](#local-https-with-docker)


<a id="linux-service"></a>
## Linux 服务

在采用 systemd 的 Linux 发行版上运行 Caddy 的推荐方法是使用我们的官方 systemd 单元文件。


<a id="unit-files"></a>
### 单元文件

我们提供了两种不同的 systemd 单元文件，您可以根据具体使用场景进行选择：

- [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service)（若您使用 [Caddyfile](/docs/caddyfile) 配置 Caddy）。如果您希望使用其他配置适配器或 JSON 配置文件，可以[覆盖](#overrides) `ExecStart` 和 `ExecReload` 命令。

- [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service)，如果您仅通过 [API](/docs/api) 配置 Caddy。该服务使用 [`--resume`](/docs/command-line#caddy-run) 选项，这将使用 `autosave.json` （该配置默认会被[持久化](/docs/json/admin/config/)）。

它们非常相似，但在 `ExecStart` 和 `ExecReload` 命令有所不同，以适应不同的工作流程。

如果您需要在不同服务之间切换，应在启用并启动另一项服务之前，先禁用并停止前一项服务。例如，要从 `caddy` 服务切换到 `caddy-api` 服务：
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>


<a id="manual-installation"></a>
### 手动安装

某些[安装方法](/docs/install)会自动将 Caddy 配置为以服务形式运行。如果您选择的安装方法未进行此设置，请按照以下说明进行操作：

**要求：**

- `caddy` 您[下载](/download)或[从源代码编译](/docs/build)的二进制文件
- `systemctl --version` 232 或更新版本
- `sudo` 特权

将 caddy 二进制文件移动到您的 `$PATH`，例如：
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

验证是否成功：
<pre><code class="cmd bash">caddy version</code></pre>

创建一个名为 `caddy` 的组：
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

创建一个名为 `caddy` 的用户，并为其设置可写的主目录：
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

如果使用配置文件，请确保该文件可被 `caddy` 用户读取。

接下来，[请](#unit-files)根据您的具体情况[选择一个 systemd 单元文件](#unit-files)。

**请仔细检查 `ExecStart` 和 `ExecReload` 指令。** 请确保二进制文件的位置和命令行参数与您的安装环境相符！例如：如果使用配置文件，请修改您的 `--config` 路径。

通常保存服务文件的位置是： `/etc/systemd/system/caddy.service`

保存服务文件后，您可以使用常规的 systemctl 命令首次启动该服务：

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

请确认其正在运行：
<pre><code class="cmd bash">systemctl status caddy</code></pre>

现在您可以开始[使用该服务](#using-the-service)了！



<a id="using-the-service"></a>
### 使用本服务

如果使用 Caddyfile，您可以通过 `nano`、`vi` 或您喜欢的编辑器进行编辑：
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

您可以将静态网站文件放置在以下任一位置： `/var/www/html` 或 `/srv`。请确保 `caddy` 用户拥有读取这些文件的权限。

要验证服务是否正在运行：
<pre><code class="cmd bash">systemctl status caddy</code></pre>
status 命令还会显示当前正在运行的服务文件的位置。

使用我们的官方服务文件运行时，Caddy 的输出将被重定向到 `journalctl`。若要阅读完整的日志并避免行被截断：
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

如果使用配置文件，在进行任何更改后，您可以优雅地重新加载 Caddy：
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

您可以使用以下命令停止该服务：
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

请勿停止服务来更改 Caddy 的配置。停止服务器会导致服务中断。请改用 reload 命令。

</aside>

Caddy 进程将以 `caddy` 用户身份运行，该用户的 `$HOME` 设置为 `/var/lib/caddy`。这意味着：
- 默认[的数据存储位置](/docs/conventions#data-directory)（用于证书和其他状态信息）将位于 `/var/lib/caddy/.local/share/caddy`.
- 默认[配置存储位置](/docs/conventions#configuration-directory)（用于自动保存的 JSON 配置，主要适用于 `caddy-api` 服务）将位于 `/var/lib/caddy/.config/caddy`.


<a id="local-https-with-systemd"></a>
### 使用 systemd 配置本地 HTTPS

在本地开发中使用 Caddy 并启用 HTTPS 时，您可能会使用如下[主机名](/docs/caddyfile/concepts#addresses)： `localhost` 或 `app.localhost`。这将通过 Caddy 的本地 CA 签发证书来启用[本地 HTTPS](/docs/automatic-https#local-https)。

由于 Caddy 以 `caddy` 用户身份运行，因此无权将根 CA 证书安装到系统信任存储中。要执行此操作，请运行 [`sudo caddy trust`](/docs/command-line#caddy-trust) 进行安装。

如果您希望在使用[`internal`颁发者](/docs/caddyfile/directives/tls#internal)时，其他设备也能连接到您的服务器，则还需要在这些设备上安装根 CA 证书。您可以在 `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt` 找到该根 CA 证书。如今许多网页浏览器都使用自己的信任存储库（而非系统的信任存储库），因此您可能还需要手动将证书安装到这些浏览器的信任存储库中。


<a id="overrides"></a>
### 覆盖

覆盖服务文件中某些设置的最佳方法是使用以下命令：
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

这将使用您的默认终端文本编辑器打开一个空白文件，您可以在其中覆盖或向单元定义中添加指令。这种文件通常称为 drop-in 文件。

<a id="environment-variables"></a>
#### 环境变量

如果您需要在配置中定义环境变量，可以按以下方式操作：
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

同样地，如果您希望使用单独的文件来管理环境变量（envfile），可以使用[`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=)指令，如下所示：
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

那么你的 `/etc/caddy/.env` 文件可能如下所示（请勿在 `"` 引号）：

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

<a id="run-and-reload-override"></a>
#### `run` 以及 `reload` 覆盖

如果您需要将配置文件从默认的 Caddyfile 更改为使用 JSON 文件（请注意， `Exec*` 在设置新值之前[，必须将](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=)指令[重置为空字符串](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=)）：
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

<a id="restart-on-crash"></a>
#### 崩溃后重启

如果你希望 caddy 在意外崩溃后 5 秒自动重启：
```systemd
[Service]
# 除非退出码为 1，否则在崩溃后自动重启 caddy
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

然后，保存文件并退出文本编辑器，重启该服务以使更改生效：
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>



<a id="selinux-considerations"></a>
### SELinux 注意事项

在启用了 SELinux 的系统上，您有两种选择：
1. 使用 [COPR 仓库](/docs/install#fedora-redhat-centos)安装 Caddy。此时您的 systemd 配置文件和 Caddy 可执行文件已自动生成并正确标记（因此您可以跳过本节）。如果您希望使用自定义构建的 Caddy，则需要按照下文所述对可执行文件进行标记。

2. [从本网站下载 Caddy](/download)，或使用 [`xcaddy`](https://github.com/caddyserver/xcaddy) 进行编译。无论采用哪种方式，您都需要自行标记文件。

除非文件已标记为 `systemd_unit_file_t` 和 `bin_t`。

`systemd_unit_file_t` 标签会自动应用于 `/etc/systemd/...` 下创建的文件，因此请务必按照手动安装说明将 `caddy.service` 文件放在该位置。

要为 `caddy` 二进制文件打标签，您可以使用以下命令：
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

<a id="windows-service"></a>
## Windows 服务

在 Windows 上，有两种方法可以将 Caddy 作为服务运行：[sc.exe](#scexe) 或 [WinSW](#winsw)。

<a id="scexe"></a>
### sc.exe

要创建该服务，请运行：

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "YOURPATH\caddy.exe run"</code></pre>

（请将 `YOURPATH` 替换为您实际的 `caddy.exe` 路径）

首先：

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

要停止：

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>


<a id="winsw"></a>
### WinSW

请按照以下说明在 Windows 上将 Caddy 安装为服务。

**要求：**

- `caddy.exe` 您[下载的](/download)二进制文件或[从源代码编译的](/docs/build)二进制文件
- 任何 `.exe` 来自最新发布的
  [WinSW](https://github.com/winsw/winsw/releases/latest) 服务封装器（下方的服务配置适用于 v2.x 版本）

将所有文件放入服务目录中。在下面的示例中，我们使用 `C:\caddy`.

将 `WinSW-x64.exe` 重命名为 `caddy-service.exe`。

在同一目录下添加 `caddy-service.xml`：

```xml
<service>
  <id>caddy</id>
  <!-- Display name of the service -->
  <name>Caddy Web Server (powered by WinSW)</name>
  <!-- Service description -->
  <description>Caddy Web Server (https://caddyserver.com/)</description>
  <executable>%BASE%\caddy.exe</executable>
  <arguments>run</arguments>
  <log mode="roll-by-time">
    <pattern>yyyy-MM-dd</pattern>
  </log>
</service>
```

现在，您可以使用以下命令安装该服务：
<pre><code class="cmd bash">caddy-service install</code></pre>

您可以打开“Windows 服务控制台”，查看该服务是否运行正常：
<pre><code class="cmd bash">services.msc</code></pre>

请注意，Windows 服务无法自动重载，因此您必须直接指示 caddy 进行重载：
<pre><code class="cmd bash">caddy reload</code></pre>

可以通过常规的 Windows 服务命令重新启动，例如通过“任务管理器”中的“服务”选项卡。

有关自定义服务封装器的信息，请参阅 [WinSW 文档](https://github.com/winsw/winsw/tree/master#usage)


<a id="docker-compose"></a>
## Docker Compose

要快速入门 Docker，最简单的方法是使用 Docker Compose。有关官方 Caddy Docker 镜像的更多详细信息，请参阅 [Docker Hub](https://hub.docker.com/_/caddy) 上的文档。

<aside class="tip">

这假设您正在使用 [Docker Compose V2](https://docs.docker.com/compose/reference/)，此时该命令应为 `docker compose` (空格)。而非 V1 中的 `docker-compose` (连字符)。

</aside>

<a id="setup"></a>
### 设置

首先，创建一个文件 `compose.yml` （或将此服务添加到现有文件中）：

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

请务必填写镜像 `<version>` ，该版本号可在 [Docker Hub](https://hub.docker.com/_/caddy) 的“标签”部分找到。

此功能的作用：

- 使用 `unless-stopped` 重启策略，确保在您的机器重启时自动重启 Caddy 容器。
- 绑定到端口 `80` 以及 `443` 分别用于 HTTP 和 HTTPS，此外 `443/udp` 用于 HTTP/3。
- 挂载包含您的 Caddyfile 配置的 `conf` 目录。
- 挂载 `site` 目录，以便从该目录提供您网站的静态文件到 `/srv`。
- 命名卷用于 `/data` 以及 `/config` 以[持久化重要信息](/docs/conventions#file-locations)。

然后，在 `conf` 目录中创建一个名为 `Caddyfile` 的文件，并在其中编写您的 [Caddyfile](/docs/caddyfile/concepts) 配置。

如果您需要提供静态文件，可以将其放置在与配置文件并列的 `site/` 目录中，然后使用 `root /srv`。若无静态文件，则可移除 `/srv` 卷挂载。

<aside class="tip">

如果您正在使用 Caddy 作为[反向代理](/docs/caddyfile/directives/reverse_proxy)连接到另一个容器，请记住，在 Docker 网络中， `localhost` 表示“此容器”，而非“此机器”。因此，例如，请勿使用 `reverse_proxy localhost:8080`，而应使用 `reverse_proxy other-container:8080`。

</aside>

如果您需要带插件的定制版 Caddy，请按照 [Docker 构建说明](/docs/build#docker)创建自定义 Docker 镜像。将 `Dockerfile` 放在 `compose.yml` 同级目录中，然后把 `compose.yml` 里的 `image:` 行改为 `build: .`。



<a id="usage"></a>
### 使用方法

然后，您可以启动容器：
<pre><code class="cmd bash">docker compose up -d</code></pre>

在修改 Caddyfile 后，请按以下步骤重新加载 Caddy：
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

从 v2.11.0 版本开始，您可以使用 `SIGUSR1`，前提是 Caddy 是通过 `caddy run` 以及配置文件启动：
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

查看 Caddy 最近 1000 条日志，并使用 `-f` 查看实时更新的日志：
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

<a id="local-https-with-docker"></a>
### 使用 Docker 实现本地 HTTPS

在本地开发中使用 Docker 并启用 HTTPS 时，您可能会使用类似以下的[主机名](/docs/caddyfile/concepts#addresses)： `localhost` 或 `app.localhost`。这将通过 Caddy 的本地 CA 签发证书来启用[本地 HTTPS](/docs/automatic-https#local-https)。这意味着容器外的 HTTP 客户端将不信任 Caddy 提供的 TLS 证书。要解决此问题，您可以在主机的信任存储中安装 Caddy 的根 CA 证书：

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

现在许多网络浏览器都使用自己的信任库（忽略系统的信任库），因此您可能还需要将证书手动安装到该信任库中，使用 `root.crt` 上文命令中从容器中复制的文件。

- 在 Firefox 中，请依次进入“首选项” > “隐私与安全” > “证书” > “查看证书” > “颁发机构” > “导入”，然后选择该 `root.crt` 文件。

- 在 Chrome 中，请前往“设置” > “隐私和安全” > “安全” > “管理证书” > “证书颁发机构” > “导入”，然后选择该 `root.crt` 文件。
