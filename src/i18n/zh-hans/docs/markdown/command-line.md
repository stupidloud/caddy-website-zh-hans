---
title: "命令行"
---

# 命令行

Caddy 具有标准的类 Unix 命令行界面。基本用法如下：

```
caddy <command> [<args...>]
```

这些 `<尖括号>` 表示会被您的输入替换的参数。

`[brackets]` 表示可选参数。`(brackets)` 表示必填参数。

省略号 `...` 表示后续内容，即一个或多个参数。

`--flags` 可能有一个单字母快捷键，例如 `-f`。

**快速入门： `caddy`, `caddy help`，或 `man caddy` （若已安装）**

---

- **[caddy adapt](#caddy-adapt)**
  将配置文档转换为原生 JSON

- **[caddy build-info](#caddy-build-info)**
  打印构建信息

- **[caddy completion](#caddy-completion)**
  生成 shell 补全脚本

- **[caddy environ](#caddy-environ)**
  打印环境

- **[caddy file-server](#caddy-file-server)**
  一个简单但已准备好投入生产的文件服务器

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  文件服务器用于导出默认文件浏览器模板的辅助命令

- **[caddy fmt](#caddy-fmt)**
  格式化一个 Caddyfile

- **[caddy hash-password](#caddy-hash-password)**
  对密码进行哈希处理并输出 Base64

- **[caddy help](#caddy-help)**
  查看 caddy 命令的帮助

- **[caddy list-modules](#caddy-list-modules)**
  列出已安装的 Caddy 模块

- **[caddy manpage](#caddy-manpage)**
  生成手册页

- **[caddy reload](#caddy-reload)**
  修改正在运行的 Caddy 进程的配置

- **[caddy respond](#caddy-respond)**
  一个用于开发和测试的快速、简洁且硬编码的 HTTP 服务器

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  一个简单但已准备好投入生产的 HTTP(S) 反向代理

- **[caddy run](#caddy-run)**
  在前台启动 Caddy 进程

- **[caddy start](#caddy-start)**
  在后台启动 Caddy 进程

- **[caddy stop](#caddy-stop)**
  停止正在运行的 Caddy 进程

- **[caddy storage export](#caddy-storage)**
  将已配置存储中的内容导出为 tar 压缩包

- **[caddy storage import](#caddy-storage)**
  将先前导出的 tarball 导入到配置的存储中

- **[caddy trust](#caddy-trust)**
  将证书安装到本地受信任存储区中

- **[caddy untrust](#caddy-untrust)**
  不信任来自本地信任存储库的证书

- **[caddy upgrade](#caddy-upgrade)**
  将 Caddy 升级至最新版本

- **[caddy add-package](#caddy-add-package)**
  将 Caddy 升级至最新版本，并添加了额外插件

- **[caddy remove-package](#caddy-remove-package)**
  将 Caddy 升级至最新版本，并移除了部分插件

- **[caddy validate](#caddy-validate)**
  检查配置文件是否有效

- **[caddy version](#caddy-version)**
  打印版本

- **[信号](#signals)**
  Caddy 如何处理信号

- **[退出代码](#exit-codes)**
  当 Caddy 进程退出时触发

<a id="subcommands"></a>
## 子命令


<a id="caddy-adapt"></a>
### `caddy adapt`

<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

将配置转换为 Caddy 的原生 JSON 配置结构，并将输出写入标准输出（stdout），同时将任何警告写入标准错误（stderr），然后退出。

`--config` 是配置文件的路径。如果省略，则会假定当前目录中存在 `Caddyfile`；否则，此标志是必需的。若希望使用标准输入（stdin）而不是普通文件，请将路径设为 `-`。

`--adapter` 指定要使用的配置适配器；默认值为 `caddyfile`。

`--pretty` 将对输出内容进行缩进格式化，以便于阅读。

`--validate` 将加载并提供该适配后的配置以验证其有效性（但不会真正启动该配置）。

请注意，即使配置已成功适配，仍可能无法通过验证。以下是一个示例 Caddyfile：

```caddy
localhost

tls cert_notexist.pem key_notexist.pem
```

试着改写一下：

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

操作成功，没有错误。然后请尝试：

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_notexist.pem: no such file or directory
</code></pre>

尽管该 Caddyfile 可以无误地转换为 JSON 格式，但实际的证书和/或密钥文件并不存在，因此验证会失败，因为该错误是在配置阶段出现的。因此，验证比转换更能有效地检测错误。

#### 示例

要将 Caddyfile 转换为 JSON 格式，以便您能轻松阅读并手动调整：

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile --pretty</code></pre>



<a id="caddy-build-info"></a>
### `caddy build-info`

<pre><code class="cmd bash">caddy build-info</code></pre>

打印 Go 提供的有关构建的信息（主模块路径、包版本、模块替换）。




<a id="caddy-completion"></a>
### `caddy completion`

<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

生成 shell 补全脚本。这使您在输入 `caddy` 命令时，可获得 Tab 键补全或自动补全（或类似功能，具体取决于您的 shell）。

要获取将此脚本安装到您特定 shell 中的说明，请运行 `caddy help completion` 或 `caddy completion -h`.



<a id="caddy-environ"></a>
### `caddy environ`

<pre><code class="cmd bash">caddy environ</code></pre>

打印 caddy 所看到的运行环境，然后退出。在调试初始化系统或 systemd 等进程管理器单元时，此功能可能很有用。




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

启动一个简单但已准备好投入生产的静态文件服务器。

`--root` 指定根文件路径。默认值为当前工作目录。

`--listen` 接受监听器地址。默认值为 `:80`，除非 `--domain` 被使用，则 `:443` 将成为默认值。

`--domain` 将仅通过该主机名提供文件，且 Caddy 会尝试通过 HTTPS 提供服务，因此如果是公共域名，请先确保公共 DNS 已正确配置。默认端口将更改为 443。

`--browse` 如果请求的目录没有索引文件，则启用目录列表功能。

`--reveal-symlinks` 当 `--browse` 启用时。

`--templates` 将启用模板渲染。

`--access-log` 启用请求/访问日志。

`--debug` 启用详细日志记录。

`--file-limit` 设置目录列表中显示的文件最大数量。默认值： `10000`。如果文件数量超过此限制，则仅显示前 N 个文件，其中 N 为指定的限制值。

`--no-compress` 禁用压缩。默认情况下，Zstandard 和 Gzip 压缩处于启用状态。

`--precompressed` 指定用于搜索预压缩 sidecar 文件的编码格式。可重复使用以支持多种格式。更多信息请参阅 [`file_server` 指令](/docs/caddyfile/directives/file_server#precompressed)。

此命令将禁用管理 API，从而更方便在本地开发机器上运行多个实例。


<a id="caddy-file-server-export-template"></a>
#### `caddy file-server export-template`

<pre><code class="cmd bash">caddy file-server export-template</code></pre>

将默认文件浏览模板导出到标准输出

<a id="caddy-fmt"></a>
### `caddy fmt`

<pre><code class="cmd bash">caddy fmt [&lt;path&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

对 Caddyfile 进行格式化或美化处理，然后退出。除非使用 `--overwrite`，否则该命令将以 `1` 退出。

`<path>` 指定 Caddyfile 的路径。如果 `-`，则从标准输入读取数据。若省略，则默认在当前目录中查找名为 Caddyfile 的文件。

`--overwrite` 会导致结果写入输入文件，而不是输出到终端。如果输入不是普通文件，此标志将不起作用。

`--diff` 会将输出与输入进行比较，并在不同之处以 `-` 和 `+` 为行添加前缀。请注意，未更改的行会以前导两个空格对齐，且这并非有效的补丁格式；它只是一个可视化工具。


<a id="caddy-hash-password"></a>
### `caddy hash-password`

<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;password&gt;]
	[-a, --algorithm &lt;name&gt;]
	[--bcrypt-cost &lt;cost&gt;]</code></pre>

一种便捷的明文密码哈希处理方式。生成的哈希值将以可直接用于 Caddy 配置的格式写入标准输出。

`--plaintext`
    待哈希的密码。如果省略，将从标准输入读取。
    如果 Caddy 连接到一个控制终端，则不会回显输入内容。

`--algorithm`
    选择哈希算法。有效选项包括：
      * `argon2id` （推荐用于现代安全）
      * `bcrypt`  （旧版，速度较慢，支持自定义成本，默认成本为 `14`）

bcrypt 特定参数：

`--bcrypt-cost`
    设置 bcrypt 哈希的难度。数值越高，安全性就越高。
    这会导致哈希计算变慢，并对 CPU 资源消耗更大。
    必须在有效范围 [bcrypt.MinCost, bcrypt.MaxCost] 之内。
    如果未填写或填写内容无效，将使用默认成本。

Argon2id 特定参数：

`--argon2id-time`
    要执行的迭代次数。增加此数值会使
    哈希运算更慢，但更能抵御暴力破解攻击。

`--argon2id-memory`
    哈希运算过程中使用的内存量。
    数值越大，对 GPU/ASIC 攻击的抵抗力越强。

`--argon2id-threads`
    要使用的 CPU 线程数。增加该数值可加快哈希运算速度
    在多核系统上。

`--argon2id-keylen`
    生成的哈希值长度（以字节为单位）。长度越大，
    安全性越高，但存储空间会略有增加。


<a id="caddy-help"></a>
### `caddy help`

<pre><code class="cmd bash">caddy help [&lt;command&gt;]</code></pre>

显示 CLI 帮助文本（可选指定特定子命令），然后退出。



<a id="caddy-list-modules"></a>
### `caddy list-modules`

<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

打印已安装的 Caddy 模块，可选地显示其关联的 Go 模块的包和/或版本信息，然后退出。

在某些脚本场景中，同时打印所有标准模块可能显得多余，因此您可以使用 `--skip-standard` 来将它们从输出中省略。

`--json` 以 JSON 格式输出模块信息，这对于程序化处理非常有用。

注意：由于 [Go 语言中](https://github.com/golang/go/issues/29228)存在[一个漏洞](https://github.com/golang/go/issues/29228)，只有当 Caddy 作为依赖项而非主模块进行构建时，才能获取版本信息。建议使用 [xcaddy](/docs/build#xcaddy) 来简化此操作。



<a id="caddy-manpage"></a>
### `caddy manpage`

<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;path&gt;)</code></pre>

为 Caddy 命令生成手册/文档页面，并将其写入指定路径下的目录。该命令的输出可通过 `man` 命令读取。

`--directory` （必填）是用于存储手册页的目录路径。如果该目录不存在，系统会自动创建。

生成后，通常需要安装手册页。具体操作因平台而异，但在典型的 Linux 系统上，步骤大致如下：

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

然后你可以运行 `man caddy` (或 `man caddy-*` 用于子命令) 在终端中阅读文档。

手册页面与我们网站上的文档是分开的。我们的网站提供了更全面的文档，并且会经常更新。




<a id="caddy-reload"></a>
### `caddy reload`

<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

为正在运行的 Caddy 实例提供新的配置。这与向 [/load 端点](/docs/api#post-load)发送 POST 请求的效果相同，但对于围绕配置文件展开的简单工作流而言，此命令更为便捷。相比之下，`stop`、`start` 和 `run` 命令相比，这个单独的命令才是修改/重新加载运行中配置的正确且语义明确的方式。

由于此命令使用了 API，因此不得禁用管理端点。

`--config` 是要应用的配置文件。如果是 `-`，则从标准输入读取配置。若未指定，系统将尝试在当前工作目录中查找名为 `Caddyfile` 的文件，并使用 `caddyfile` 配置适配器进行适配；否则，如果没有可加载的配置文件，就会报错。

`--adapter` 指定要使用的配置适配器（如有）。如果 `--config` 文件名以 `Caddyfile` 开头或以 `.caddyfile` 结尾，则默认使用 `caddyfile` 适配器。否则，如果提供的配置文件不是 Caddy 的原生 JSON 格式，则必须使用此标志。

`--address` 如果管理端点未监听默认地址，且该地址与提供的配置文件中的地址不同，则需使用此地址。

`--force` 即使指定的配置与 Caddy 当前运行的配置相同，此操作仍会触发重新加载。这在需要强制 Caddy 重新配置其模块时可能很有用，但可能会产生副作用，例如：重新加载手动加载的 TLS 证书。




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


启动一个或多个简单的、硬编码的 HTTP 服务器，适用于开发、预发布环境以及某些生产场景。它可用于验证或调试 HTTP 客户端、脚本，甚至负载均衡器。

`--status` 是要返回的 HTTP 状态码。

`--header` 添加一个 HTTP 头部；需要 `Field: value` 形式。此标志可以多次使用。

`--body` 指定响应正文。或者，正文也可以通过标准输入管道传入。

`--listen` 是监听地址，可以是 Caddy 识别的任何[网络地址](/docs/conventions#network-addresses)，并可包含端口范围以启动多个服务器。

`--debug` 启用详细调试日志记录。

`--access-log` 启用访问/请求日志记录。

如果未指定任何选项，该命令将在一个随机的可用端口上监听，并以空的 200 响应来应答 HTTP 请求。监听地址可以通过 `--listen` 参数进行自定义，并始终输出到标准输出。如果监听地址包含端口范围，则会启动多个服务器。

如果提供了最后一个未命名的参数，它将被视为状态码（与 `--status` 标志）。否则，它将用作响应正文（与 `--body` 标志）。 `--status` 和 `--body` 标志将始终覆盖此参数。

响应正文可以通过以下三种方式提供：标志、命令的最后一个（且未命名的）参数，或者通过标准输入管道传入（如果标志和参数均未设置）。响应正文支持有限的[模板求值](https://pkg.go.dev/text/template)，可使用以下变量：

变量 | 描述
---------|-------------
`.N`       | 服务器编号
`.Port`    | 监听端口
`.Address` | 监听器地址


#### 示例

在随机端口上发送空的 200 响应：
<pre><code class="cmd bash">caddy respond</code></pre>

包含正文的 HTTP 响应：
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

多服务器与模板：
<pre><code class="cmd bash">$ caddy respond --listen :2000-2004 "{{printf "I'm server {{.N}} on port {{.Port}}"}}"

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

$ curl 127.0.0.1:2002
I'm server 2 on port 2002</code></pre>

在维护页面中插入：
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

一个简单但已准备好投入生产的反向代理。适用于快速部署、演示和开发。

只需将 HTTP(S) 流量从 `--from` 地址转发到 `--to` 地址即可。可以重复指定多个 `--to` 地址。`--to` 地址还可以包含端口范围，作为扩展为多个上游的快捷方式。

除非地址中另有说明，否则如果提供了主机名，`--from` 地址将被视为 HTTPS；`--to` 地址将被视为 HTTP。

如果 `--from` 地址包含主机名或 IP，Caddy 将尝试通过 HTTPS 并使用证书提供代理服务（除非被 HTTP scheme 或端口覆盖）。

如果使用 HTTPS：
  - `--disable-redirects` 可用于避免绑定 HTTP 端口。
  - `--internal-certs` 可用于强制使用内部 CA 签发证书，而不是尝试获取公开证书。

对于代理转发：
  - `--header-up` 可用于设置要发送给上游的请求头。
  - `--header-down` 可用于设置要发回给客户端的响应头。
  - `--change-host-header` 会将请求中的 `Host` 头设置为上游地址，而不是默认使用传入的 `Host` 头。

    这相当于 `--header-up "Host: {http.reverse_proxy.upstream.hostport}"`。

  - `--insecure` 会禁用与上游服务器的 TLS 验证。警告：这会因为不验证上游证书而降低安全性。
  - `--debug` 启用详细日志记录。

此命令会禁用管理 API，以便在本地开发机器上更轻松地运行多个实例。



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

运行 Caddy 并无限期阻塞；即“守护进程”模式。

`--config` 指定一个初始配置文件，以便立即加载并使用。如果是 `-`，则从标准输入（stdin）读取配置。若未指定配置文件，Caddy 将以空配置运行，并为[管理 API 端点](/docs/api)使用默认设置，这些端点可用于向其提供新的配置。作为特例，如果当前工作目录中存在名为 “Caddyfile” 的文件，且已加载 `caddyfile` 配置适配器（默认），则该文件将被加载并用于配置 Caddy，即使未提供任何命令行参数。

`--adapter` 是加载初始配置时要使用的配置适配器的名称（如有）。如果 `--config` 文件名以 `Caddyfile` 开头或以 `.caddyfile` 结尾，则默认使用 `caddyfile` 适配器。否则，如果提供的配置文件不是 Caddy 的原生 JSON 格式，则必须使用此标志。任何警告都会输出到日志中，但请注意，即使存在警告，只要适配过程没有报错，系统就会立即采用该配置。如果您想先查看适配结果，请使用[`caddy adapt`](#caddy-adapt)子命令。

`--pidfile` 将 PID 写入指定的文件。

`--environ` 在开始前打印出环境信息。这与 `caddy environ` 命令相同，但不会在输出后退出。

`--envfile` 从指定文件中加载环境变量，格式为 `KEY=VALUE`。支持以 `#` 开头的注释；键前可添加 `export` 前缀；值可用双引号括起（引号内部的双引号可进行转义）；也支持多行值。

`--resume` 使用上次加载并自动保存的配置，覆盖 `--config` 标志（如果存在）。使用此标志可确保配置在机器重启或进程重启后仍然有效。这在以 [API](/docs/api) 为中心的部署中最有用。

`--watch` 将监视配置文件，并在文件发生更改后自动重新加载。⚠️ 此功能仅适用于本地开发环境！

<aside class="advice">

在生产环境中运行时，切勿停止服务器来更改配置！这会导致系统停机。（这本应是显而易见的，但你会惊讶于我们收到多少关于此问题的投诉。）请改用[`caddy reload`](#caddy-reload)命令，或者向进程发送 `SIGUSR1` 信号，其效果等同于 `caddy reload` 使用当前加载的配置。

</aside>



<a id="caddy-start"></a>
### `caddy start`

<pre><code class="cmd bash">caddy start
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]
	[--pidfile &lt;file&gt;]
	[-w, --watch]</code></pre>

与[`caddy run`](#caddy-run)相同，但会在后台运行。该命令仅在后台进程成功启动（或启动失败）之前保持阻塞状态，随后返回。

注意：该标志 `--config` 不支持 `-` 从标准输入读取配置。

不建议在系统服务或 Windows 环境中使用此命令。在 Windows 系统中，子进程将保持与终端的连接，因此关闭窗口会强制停止 Caddy，这一点并不明显。建议改用[服务方式](/docs/running)运行 Caddy。

启动后，您可以使用 [`caddy stop`](#caddy-stop) 或 [`POST /stop`](/docs/api#post-stop) API 端点来退出后台进程。



<a id="caddy-stop"></a>
### `caddy stop`

<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

<aside class="tip">

停止（和重启）服务器与配置更改是相互独立的。**在生产环境中，请勿使用 stop 命令来更改配置，除非您希望系统出现停机。** 请改用 [`caddy reload`](#caddy-reload) 命令。

</aside>


优雅地停止正在运行的 Caddy 进程（不包括 stop 命令触发的进程），并使其退出。它使用 admin API 的 [`POST /stop`](/docs/api#post-stop) 端点来执行优雅关机。

可以使用 `--address` 标志，或通过给定的 `--config`，前提是运行中的实例的管理 API 未使用默认监听地址。

如果您想停止当前配置但不想退出该进程，请使用[`caddy reload`](#caddy-reload)并提供空配置，或调用[`DELETE /config/`](/docs/api#delete-configpath)端点。


<a id="caddy-storage"></a>
### `caddy storage`

*⚠️ 实验性功能*

支持导出和导入 Caddy 已配置的数据存储中的内容。

当需要从一个[存储模块](/docs/json/storage/)切换到另一个[存储模块](/docs/json/storage/)时，这种方法非常有用：先从旧模块导出数据，更新配置，然后导入到新模块中。

可以使用以下命令，利用旧配置和新配置，将存储内容一次性复制到不同模块之间，方法是将 export 命令的输出通过管道传递给 import 命令。

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">

请注意，在使用[文件系统存储](/docs/conventions#data-directory)时，必须以 Caddy 通常运行的用户身份执行 export 命令，否则可能会使用错误的存储位置。

例如，当以 [systemd 服务的](/docs/running#linux-service)形式运行 Caddy 时，它将以 `caddy` 用户身份运行，因此您应以该用户身份执行 export 或 import 命令。通常可通过以下方式实现： `sudo -u caddy <command>`.

</aside>


<a id="caddy-storage-export"></a>
#### `caddy storage export`

<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;path&gt;
	[-o, --output &lt;path&gt;]</code></pre>

`--config` 是用于加载配置的文件。这是必需的，以便连接到正确的存储模块。

`--output` 是用于写入压缩包的文件名。如果 `-`，则输出将写入标准输出。



<a id="caddy-storage-import"></a>
#### `caddy storage import`

<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;path&gt;
	-i, --input &lt;path&gt;</code></pre>

`--config` 是用于加载配置的文件。这是必需的，以便连接到正确的存储模块。

`--input` 是要读取的 tar 压缩包的文件名。如果 `-`，则从标准输入读取数据。


<a id="caddy-trust"></a>
### `caddy trust`

<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

将由 Caddy 的 [PKI 应用](/docs/json/apps/pki/)管理的 CA 的根证书安装到本地信任存储中。

Caddy 会在生成根证书时尝试将其自动安装到本地信任存储中，但如果 Caddy 没有写入信任存储的相应权限，此操作可能会失败。如果服务器进程以无特权用户身份运行（例如通过 systemd），则必须在使用证书之前执行此命令进行预安装。您可能需要在 Unix 系统上通过 `sudo` 运行此命令。

默认情况下，此命令会安装 Caddy 默认 CA（即“local”）的根证书。您可以使用 `--ca` 参数指定其他 CA 的 ID。

该命令将尝试连接到 Caddy [的管理 API](/docs/api) 以获取根证书，使用 [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates) 端点。您可以显式指定 `--address`，或使用 `--config` 标志从配置中加载管理地址，前提是正在运行的实例的管理 API 未使用默认监听地址。

您还可以使用 `caddy` 二进制文件配合此命令，将证书安装到网络中的其他机器上（前提是已向其他机器开放管理 API）——执行此操作时请务必谨慎，切勿将管理 API 暴露给不可信的客户端。


<a id="caddy-untrust"></a>
### `caddy untrust`

<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;path&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

将本地信任存储库中的某个根证书标记为不受信任。

此命令仅取消信任；它并不一定会完全从信任存储中删除根证书。因此，反复对新证书进行信任和取消信任操作可能会导致信任数据库空间不足。

此命令不会删除或修改 Caddy 配置存储中的证书文件。

该命令有两种使用方式：
- 通过使用 `--cert` 标志。
- 通过使用 [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates) 端点从[管理 API](/docs/api) 获取根证书。如果未指定任何标志，则这是默认行为。

如果使用管理 API，则 CA ID 默认为“local”。您可以使用 `--ca` 标志指定其他 CA 的 ID。您可以显式指定 `--address`，或使用 `--config` 标志从配置中加载管理地址。


<a id="caddy-upgrade"></a>
### `caddy upgrade`

*⚠️ 实验性功能*

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

将当前的 Caddy 二进制文件替换为[下载页面](/download)上的最新版本，并安装相同的模块，包括已在 Caddy 网站上注册的所有第三方插件。

升级操作不会中断正在运行的服务器；目前，该命令仅会替换磁盘上的二进制文件。如果将来我们能找到更好的实现方法，这一机制可能会有所调整。

升级过程具有容错性；系统会先备份当前的二进制文件（将其复制到当前文件旁边），并在出现任何问题时自动恢复。如果您希望在升级完成后保留备份，可以使用 `--keep-backup` 选项。

如果您的用户没有对可执行文件进行写入的权限，则执行此命令可能需要提升权限。



<a id="caddy-add-package"></a>
### `caddy add-package`

*⚠️ 实验性功能*

<pre><code class="cmd bash">caddy add-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

与 `caddy upgrade` 类似，该命令将当前的 Caddy 二进制文件替换为最新版本，其中安装相同的模块，并额外包含作为参数列出的软件包。您可以在[我们的下载页面](/download)上查看可安装的软件包列表。每个参数应为完整的软件包名称。

例如：

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>



<a id="caddy-remove-package"></a>
### `caddy remove-package`

*⚠️ 实验性功能*

<pre><code class="cmd bash">caddy remove-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

与 `caddy upgrade` 类似，该命令会用最新版本的 Caddy 二进制文件替换当前版本，并安装相同的模块，但如果当前二进制文件中包含作为参数列出的软件包，则不会安装这些软件包。运行 `caddy list-modules --packages` 可查看当前二进制文件中包含的非标准模块的包名列表。



<a id="caddy-validate"></a>
### `caddy validate`

<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]</code></pre>

验证配置文件，然后退出。该命令会反序列化配置文件，随后加载并配置其中的所有模块，其操作过程如同启动该配置一般，但配置文件实际上并未被启动。此操作可揭示配置文件在加载或配置阶段出现的错误，其错误检查能力比单纯将配置文件序列化为 JSON 格式更为强大。

`--config` 是要验证的配置文件。如果 `-`，则从标准输入读取配置。默认情况下读取 `Caddyfile` （若存在）。

`--adapter` 是要使用的配置适配器的名称。如果 `--config` 文件名以 `Caddyfile` 或以 `.caddyfile` ，则默认使用 `caddyfile` 适配器。否则，如果提供的配置文件不是 Caddy 的原生 JSON 格式，则必须使用此标志。

`--envfile` 从指定文件中加载环境变量，采用 `KEY=VALUE` 格式。以 `#` 开头的注释；键值前可添加前缀 `export`；值可用双引号括起（内部的双引号可进行转义）；支持多行值。



<a id="caddy-version"></a>
### `caddy version`
<pre><code class="cmd bash">caddy version</code></pre>

打印版本号并退出。



<a id="signals"></a>
## 信号

Caddy 会拦截某些信号，而忽略其他信号。信号可以触发特定的进程行为。

信号 | 行为
-------|----------
`SIGINT` | 正常退出。再次发送信号以强制立即退出。
`SIGQUIT` | 立即退出 Caddy，但仍会清理存储中的锁，因为这很重要。
`SIGTERM` | 体面地退出。
`SIGUSR1` | 重新加载配置文件，但仅当以 `caddy run`（不带 `--resume`）且未通过 [API](/docs/api) 对配置进行修改（包括 [`caddy reload`](#caddy-reload)）时才会生效。
`SIGUSR2` | 已忽略。
`SIGHUP` | 已忽略。

“优雅退出”意味着不再接受新的连接，且在关闭套接字之前，现有连接将被逐步释放。此过程可能设有宽限期（且该宽限期可配置）。宽限期结束后，连接将被强制终止。在优雅关闭过程中，存储中的锁以及各模块需要释放的其他资源将被清理。

当接收到重新加载配置的信号（`SIGUSR1`）时，其行为类似于强制配置重载（即即使配置文本未更改，仍会执行重载），这可能会从磁盘重新加载相关文件（如 TLS 证书）。

只有当 Caddy 通过 `caddy run` 并指定配置文件时才启用。若 Caddy 通过 `--resume`（因为这暗示了 API 工作流），或者通过管理 API 接收任何配置更改，或者 `caddy reload` 以与初始启动时不同的文件名或配置适配器运行，则不会启用。此设计旨在避免不同加载方式之间的冲突。



<a id="exit-codes"></a>
## 退出代码

当进程退出时，Caddy 会返回一个代码：

代码 | 含义
-----|---------
`0` | 正常退出。
`1` | 启动失败。**请勿自动重启该进程；除非进行修改，否则很可能再次出现错误。**
`2` | 强制退出。Caddy 在未清理资源的情况下被强制退出。
`3` | 退出失败。Caddy 在清理过程中因出现错误而退出。

在 Bash 中，你可以通过以下方式获取上一个命令的退出代码： `echo $?`.
