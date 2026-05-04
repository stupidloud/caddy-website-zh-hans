---
title: "Caddy 性能剖析"
---

Caddy 性能剖析
================

**程序剖析**是程序在运行时资源使用情况的快照。剖析结果对于识别问题区域、排查错误和崩溃，以及优化代码都大有裨益。

Caddy 使用 Go 语言的性能分析工具 [pprof](https://github.com/google/pprof)，该工具已内置于 `go` 命令中。

性能分析报告会展示 CPU 和内存的使用情况，呈现 goroutine 的堆栈跟踪，并有助于排查死锁或高竞争率的同步原语。

在报告 Caddy 中的某些错误时，我们可能会要求您提供性能分析报告。本文可为您提供帮助。它既介绍了如何使用 Caddy 获取性能分析报告，也概述了如何使用和解读生成的 pprof 性能分析报告。


开始之前，有两点需要注意：

1. **Caddy 的剖析报告不涉及安全敏感信息。** 它们包含无害的技术读数，而非内存内容。它们不会授予系统访问权限。因此，分享这些文件是安全的。
2. **性能分析数据体积小，可在生产环境中收集。** 事实上，这对许多用户来说是一项推荐的最佳实践；详见本文后文。

## 获取剖析报告

您可通过[管理界面](/docs/api)访问剖析页面： `/debug/pprof/`。在运行 Caddy 的机器上，请通过浏览器打开：

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	默认情况下，管理 API 仅可在本地访问。若在远程环境、虚拟机或容器中运行，请参阅下一节了解如何访问此端点。
</aside>

你会看到一个包含统计数字和链接的简单表格，例如：

计数 | 剖析项
----- | --------------------
79    | 分配
0     | 阻塞
0     | 命令行
22    | 协程
79    | 堆
0     | 互斥锁
0     | CPU 剖析
29    | 创建线程
0     | 跟踪
|     | 完整的 goroutine 堆栈转储

这些计数器是快速识别内存泄漏的便捷工具。如果您怀疑存在泄漏，请反复刷新页面，您会发现其中一个或多个计数器在持续增加。如果堆计数增加，则可能是内存泄漏；如果协程计数增加，则可能是协程泄漏。

点击各个剖析项查看它们的具体内容。有些项可能为空，这在很多情况下都很正常。最常用的项目包括 **goroutine**（协程栈）、**heap**（内存）和 **profile**（CPU）。其他项目则有助于排查互斥锁争用或死锁问题。

底部对每个剖析项进行了简要说明：

- **allocs：** 所有历史内存分配的样本
- **block：** 导致在同步原语上阻塞的堆栈跟踪
- **cmdline：** 当前程序的命令行调用
- **goroutine：** 所有当前 goroutine 的堆栈跟踪。使用 `debug=2` 作为查询参数，即可按与未恢复 panic 相同的格式导出。
- **heap：** 活跃对象的内存分配样本。您可以指定 `gc` GET 参数，在采集堆样本之前运行垃圾回收。
- **mutex：** 竞争互斥锁持有者的堆栈跟踪
- **profile：** CPU 剖析文件。您可以在 `seconds` GET 参数中指定持续时间（单位为秒）。获取剖析文件后，请使用 `go tool pprof` 命令分析该文件。
- **threadcreate：** 导致创建新操作系统线程的堆栈跟踪
- **trace：** 当前程序的执行跟踪记录。您可以在 `seconds` GET 参数中指定持续时间（以秒为单位）。获取跟踪文件后，请使用 `go tool trace` 命令分析该跟踪记录。

<aside class="tip">

“goroutine”与“完整 goroutine 堆栈转储”之间的区别在于 `?debug=2` 参数：完整堆栈转储类似于 panic 后的输出；它更详细，而且不会合并相同的 goroutine。

</aside>


### 下载剖析报告

点击上方 pprof 索引页上的链接，即可获取文本格式的分析报告。这对于调试非常有用，也是我们 Caddy 团队更倾向于采用的方式，因为我们可以直接浏览报告寻找明显的线索，而无需借助额外的工具。

但二进制格式实际上才是默认格式。HTML 链接会附加 `?debug=` 查询字符串参数，以便将其格式化为文本，但（CPU）“profile”链接除外，因为它没有文本表示形式。

以下是您可以设置的查询字符串参数（摘自 [Go 文档](https://pkg.go.dev/net/http/pprof#hdr-Parameters)）：

- **`debug=N`（除 CPU 以外的所有剖析项）：** 响应格式：N = 0：二进制（默认），N > 0：明文
- **`gc=N`（堆剖析）：** N > 0：在进行分析前先执行一次垃圾回收
- **`seconds=N`（allocs、block、goroutine、heap、mutex、threadcreate 剖析）：** 返回一个增量剖析结果
- **`seconds=N`（CPU、跟踪剖析）：** 针对指定时间段的分析

由于这些是 HTTP 端点，您也可以使用任何 HTTP 客户端（如 curl 或 wget）来下载剖析报告。

下载剖析报告后，您可以将其上传至 GitHub 问题评论中，或使用 [pprof.me](https://pprof.me/) 之类的网站。若仅涉及 CPU 剖析，[flamegraph.com](https://flamegraph.com/) 也是一个不错的选择。


## 远程访问

*如果您已经可以在本地访问管理 API，请跳过本节。*

默认情况下，Caddy 的管理 API 仅可通过回环套接字访问。不过，您至少可以通过 3 种方式远程访问 Caddy 的 `/debug/pprof` 端点：

### 通过您的网站设置反向代理

一个简单的方法是直接从您的网站对其进行反向代理：

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

当然，这将使这些剖析项对所有能够连接到您网站的人可见。如果您不希望这样，可以使用您选择的 HTTP 身份验证模块来添加身份验证功能。

（别忘了 `/debug/pprof/*` 匹配器，否则你会代理整个管理 API！)


### SSH 隧道

另一种方法是使用 SSH 隧道。这是一种通过 SSH 协议在您的计算机与服务器之间建立的加密连接。请在您的计算机上运行如下命令：

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

这会建立一条隧道 `localhost:8123` （在您的本地机器上）转发到 `localhost:2019` 到 `example.com`。请务必根据需要替换 `username`, `example.com`，并根据需要调整端口。

<aside class="tip">

该命令将在前台运行。请注意，如果您尝试使用 <kbd>Ctrl</kbd>+<kbd>Z</kbd> 将进程置于后台，隧道将会暂停，且通过该隧道建立的连接将无法成功。

</aside>

然后在另一个终端中，你可以运行 `curl` 如下所示：

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

您可以避免需要 `-H "Host: ..."` 通过在隧道两端使用端口 `2019` （但这要求该端口 `2019` 在您的计算机上尚未被占用，即本地未运行 Caddy）。

在隧道处于活动状态时，您可以访问所有管理 API。在 `ssh` 命令行中输入 <kbd>Ctrl</kbd>+<kbd>C</kbd> 以关闭隧道。

#### 长期运行的隧道

使用上述命令运行隧道时，必须保持终端窗口打开。若要在后台运行隧道，可以按以下方式启动：

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

该进程将在后台启动，并在 `/tmp/caddy-tunnel.sock`。完成操作后，您可以使用该控制套接字关闭隧道：

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>


### 远程管理 API

您还可以配置管理 API，使其接受来自授权客户端的远程连接。

（待办事项：撰写一篇关于此内容的文章。）



## Goroutine 剖析

goroutine 转储有助于了解当前存在哪些 goroutine 以及它们的调用堆栈。换句话说，它能让我们了解哪些代码正在执行，哪些处于阻塞或等待状态。

如果你点击“goroutines”或访问 `/debug/pprof/goroutine?debug=1`，你会看到一个 goroutine 及其调用栈的列表。例如：

```
goroutine profile: total 88
23 @ 0x43e50e 0x436d37 0x46bda5 0x4e1327 0x4e261a 0x4e2608 0x545a65 0x5590c5 0x6b2e9b 0x50ddb8 0x6b307e 0x6b0650 0x6b6918 0x6b6921 0x4b8570 0xb11a05 0xb119d4 0xb12145 0xb1d087 0x4719c1
#	0x46bda4	internal/poll.runtime_pollWait+0x84			runtime/netpoll.go:343
#	0x4e1326	internal/poll.(*pollDesc).wait+0x26			internal/poll/fd_poll_runtime.go:84
#	0x4e2619	internal/poll.(*pollDesc).waitRead+0x279		internal/poll/fd_poll_runtime.go:89
#	0x4e2607	internal/poll.(*FD).Read+0x267				internal/poll/fd_unix.go:164
#	0x545a64	net.(*netFD).Read+0x24					net/fd_posix.go:55
#	0x5590c4	net.(*conn).Read+0x44					net/net.go:179
#	0x6b2e9a	crypto/tls.(*atLeastReader).Read+0x3a			crypto/tls/conn.go:805
#	0x50ddb7	bytes.(*Buffer).ReadFrom+0x97				bytes/buffer.go:211
#	0x6b307d	crypto/tls.(*Conn).readFromUntil+0xdd			crypto/tls/conn.go:827
#	0x6b064f	crypto/tls.(*Conn).readRecordOrCCS+0x24f		crypto/tls/conn.go:625
#	0x6b6917	crypto/tls.(*Conn).readRecord+0x157			crypto/tls/conn.go:587
#	0x6b6920	crypto/tls.(*Conn).Read+0x160				crypto/tls/conn.go:1369
#	0x4b856f	io.ReadAtLeast+0x8f					io/io.go:335
#	0xb11a04	io.ReadFull+0x64					io/io.go:354
#	0xb119d3	golang.org/x/net/http2.readFrameHeader+0x33		golang.org/x/net@v0.14.0/http2/frame.go:237
#	0xb12144	golang.org/x/net/http2.(*Framer).ReadFrame+0x84		golang.org/x/net@v0.14.0/http2/frame.go:498
#	0xb1d086	golang.org/x/net/http2.(*serverConn).readFrames+0x86	golang.org/x/net@v0.14.0/http2/server.go:818

1 @ 0x43e50e 0x44e286 0xafeeb3 0xb0af86 0x5c29fc 0x5c3225 0xb0365b 0xb03650 0x15cb6af 0x43e09b 0x4719c1
#	0xafeeb2	github.com/caddyserver/caddy/v2/cmd.cmdRun+0xcd2					github.com/caddyserver/caddy/v2@v2.7.4/cmd/commandfuncs.go:277
#	0xb0af85	github.com/caddyserver/caddy/v2/cmd.init.1.func2.WrapCommandFuncForCobra.func1+0x25	github.com/caddyserver/caddy/v2@v2.7.4/cmd/cobra.go:126
#	0x5c29fb	github.com/spf13/cobra.(*Command).execute+0x87b						github.com/spf13/cobra@v1.7.0/command.go:940
#	0x5c3224	github.com/spf13/cobra.(*Command).ExecuteC+0x3a4					github.com/spf13/cobra@v1.7.0/command.go:1068
#	0xb0365a	github.com/spf13/cobra.(*Command).Execute+0x5a						github.com/spf13/cobra@v1.7.0/command.go:992
#	0xb0364f	github.com/caddyserver/caddy/v2/cmd.Main+0x4f						github.com/caddyserver/caddy/v2@v2.7.4/cmd/main.go:65
#	0x15cb6ae	main.main+0xe										caddy/main.go:11
#	0x43e09a	runtime.main+0x2ba									runtime/proc.go:267

1 @ 0x43e50e 0x44e9c5 0x8ec085 0x4719c1
#	0x8ec084	github.com/caddyserver/certmagic.(*Cache).maintainAssets+0x304	github.com/caddyserver/certmagic@v0.19.2/maintain.go:67

...
```

第一行， `goroutine profile: total 88`，告诉我们当前正在查看的内容以及 goroutine 的数量。

以下是 goroutine 的列表。它们按调用栈按频率从高到低进行分组。

goroutine 语句的语法如下： `<count> @ <addresses...>`

该行以拥有相关调用栈的 goroutine 数量开头。 `@` 符号表示调用指令地址的起始位置，即引发该 goroutine 的函数指针。每个指针代表一次函数调用，或称调用帧。

您可能会注意到，许多 goroutine 共享相同的首次调用地址。这就是您程序的主函数，也就是入口点。有些 goroutine 并非由此发起，因为程序包含各种 `init()` 函数，而且 Go 运行时也可能自行创建 goroutine。

以下以 `#` ，实际上只是为了方便读者阅读而添加的注释。这些内容包含该 goroutine 的当前堆栈跟踪。顶部代表堆栈顶部，即当前正在执行的代码行。底部代表堆栈底部，即该 goroutine 最初开始运行的代码。

堆栈跟踪的格式如下：

```
<address> <package/func>+<offset> <filename>:<line>
```

地址是函数指针，接着你会看到 Go 包名和函数名（如果是方法，还会显示相关的类型名），以及该函数内的指令偏移量。最后是可能最有用的信息——文件名和行号。

### 完整的 goroutine 堆栈转储

如果我们将查询字符串参数改为 `?debug=2`，我们将获得完整的转储。其中包含每个 goroutine 的详细堆栈跟踪，且相同的 goroutine 不会被合并。在繁忙的服务器上，该输出可能非常庞大，但这些信息非常有价值！

我们来看一个与上文第一个调用堆栈（已截断）相对应的示例：

```
goroutine 61961905 [IO wait, 1 minutes]:
internal/poll.runtime_pollWait(0x7f9a9a059eb0, 0x72)
	runtime/netpoll.go:343 +0x85
...
golang.org/x/net/http2.(*serverConn).readFrames(0xc001756f00)
	golang.org/x/net@v0.14.0/http2/server.go:818 +0x87
created by golang.org/x/net/http2.(*serverConn).serve in goroutine 61961902
	golang.org/x/net@v0.14.0/http2/server.go:930 +0x56a
```

尽管输出内容冗长，但该转储文件所提供的最有价值的信息，正是每个 goroutine 的首行和末行。

第一行包含该 goroutine 的编号（61961905）、状态（“IO wait”）和持续时间（“1 分钟”）：

- **Goroutine 编号：** 是的，Goroutine 是有编号的！但这些编号不会在我们的代码中直接显示。不过，这些编号在堆栈跟踪中特别有用，因为我们可以据此查看是哪一个 Goroutine 创建了当前这个 Goroutine（参见末尾的提示：“由……在 Goroutine 61961902 中创建”）。下文介绍的工具可帮助我们绘制相关可视化图表。

- **状态：** 这告诉我们该 goroutine 当前正在执行什么操作。以下是一些你可能会看到的状态：
	- `running`: 执行代码——太棒了！
	- `IO wait`: 正在等待网络响应。由于该操作挂载在非阻塞网络轮询器上，因此不会占用操作系统线程。
	- `sleep`: 我们都需要更多这样的东西。
	- `select`: 在执行 SELECT 语句时被阻塞；正在等待一个处理槽位可用。
	- `select (no cases):` 因空的 select 语句而阻塞 `select {}` 具体来说，Caddy 在其主函数中使用了一个 select 来保持运行，因为关闭操作是由其他 goroutine 发起的。
	- `chan receive`: 通道接收受阻 (`<-ch`).
	- `semacquire`: 正在等待获取信号量（低级同步原语）。
	- `syscall`: 执行系统调用。占用一个操作系统线程。

- **持续时间：** 指 goroutine 存在的时间长度。这对于排查诸如 goroutine 泄漏之类的错误非常有用。例如，如果我们预期所有网络连接在几分钟后都会关闭，那么发现大量 netconn goroutine 持续存活数小时又意味着什么？

### 解析 goroutine 转储

不看代码的话，我们能从上面的 goroutine 中了解到什么？

它大约一分钟前才创建，正在通过网络套接字等待数据，且其 goroutine 数量相当大（61961905）。

从第一个转储（`debug=1`）中，我们得知其调用栈被执行的频率相对较高，而庞大的 goroutine 数量加上较短的持续时间表明，曾有数千万个这类短生命周期 goroutine 被创建。它位于名为 `pollWait` 的函数中，其调用历史包含从使用 TLS 的加密网络连接中读取 HTTP/2 帧的操作。

因此，我们可以推断出这个 goroutine 正在处理一个 HTTP/2 请求！它正在等待客户端发送的数据。此外，我们知道创建它的 goroutine 并非该进程最早的几个 goroutine 之一，因为它的编号也很大；在转储中找到该 goroutine 后会发现，它是为了在现有请求期间处理一个新的 HTTP/2 流而创建的。相比之下，编号较高的其他 goroutine 可能是由编号较低的 goroutine（例如 32）创建的，这表明这是一个刚从套接字建立的新连接，而不是由 `Accept()` 调用直接建立的连接。

虽然每个程序都不尽相同，但在调试 Caddy 时，这些模式通常都成立。

## 内存剖析

内存（或堆）分析会追踪堆内存的分配情况，而堆内存是系统中主要的内存消耗源。内存分配通常也是性能问题的常见诱因，因为分配内存需要调用系统调用，而系统调用的执行可能比较耗时。

堆内存剖析图在几乎所有方面都与 goroutine 剖析图相似，唯一不同之处在于第一行的开头。以下是一个示例：

```
0: 0 [1: 4096] @ 0xb1fc05 0xb1fc4d 0x48d8d1 0xb1fce6 0xb184c7 0xb1bc8e 0xb41653 0xb4105c 0xb4151d 0xb23b14 0x4719c1
#	0xb1fc04	bufio.NewWriterSize+0x24					bufio/bufio.go:599
#	0xb1fc4c	golang.org/x/net/http2.glob..func8+0x6c				golang.org/x/net@v0.17.0/http2/http2.go:263
#	0x48d8d0	sync.(*Pool).Get+0xb0						sync/pool.go:151
#	0xb1fce5	golang.org/x/net/http2.(*bufferedWriter).Write+0x45		golang.org/x/net@v0.17.0/http2/http2.go:276
#	0xb184c6	golang.org/x/net/http2.(*Framer).endWrite+0xc6			golang.org/x/net@v0.17.0/http2/frame.go:371
#	0xb1bc8d	golang.org/x/net/http2.(*Framer).WriteHeaders+0x48d		golang.org/x/net@v0.17.0/http2/frame.go:1131
#	0xb41652	golang.org/x/net/http2.(*writeResHeaders).writeHeaderBlock+0xd2	golang.org/x/net@v0.17.0/http2/write.go:239
#	0xb4105b	golang.org/x/net/http2.splitHeaderBlock+0xbb			golang.org/x/net@v0.17.0/http2/write.go:169
#	0xb4151c	golang.org/x/net/http2.(*writeResHeaders).writeFrame+0x1dc	golang.org/x/net@v0.17.0/http2/write.go:234
#	0xb23b13	golang.org/x/net/http2.(*serverConn).writeFrameAsync+0x73	golang.org/x/net@v0.17.0/http2/server.go:851
```

第一行的格式如下：

```
<live objects> <live memory> [<allocations>: <allocation memory>] @ <addresses...>
```

在上例中，我们有一个由 `bufio.NewWriterSize()` ，但当前该调用栈中没有活跃的对象。

有趣的是，我们可以从该调用堆栈中推断出，http2 包使用了一个 4 KB 的对象池来向客户端写入 HTTP/2 帧。如果在热路径中已优化为复用内存分配，那么在 Go 内存剖析中经常会看到这类池化对象。这可以减少新的内存分配，而堆剖析有助于您判断该池是否被正确使用。

## CPU 剖析

CPU 剖析有助于您了解 Go 程序在处理器上被调度的时间主要花在了哪些地方。

不过，这些数据没有明文形式，因此在下节中，我们将使用 `go tool pprof` 命令来帮助我们读取它们。

要下载 CPU 剖析文件，请访问 `/debug/pprof/profile?seconds=N`，其中 N 表示您希望收集剖析的时间（以秒为单位）。在收集 CPU 剖析期间，程序性能可能会受到轻微影响。（其他剖析几乎不会对性能产生影响。）

完成后，系统应下载一个二进制文件，其名称恰如其分地命名为 `profile`。然后我们需要对其进行检查。

## `go tool pprof`

我们将以读取 CPU 剖析数据为例，使用 Go 内置的剖析工具，但您也可以将其用于任何类型的剖析数据。

运行以下命令（如果“profile”的实际路径不同，请将其替换为正确的路径），这将打开一个交互式提示符：

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">

您可以使用此命令查看任何类型的剖析报告，而不仅仅是 CPU 剖析报告。对于其他类型的剖析报告，其原理相同，相关概念也同样适用。

</aside>

你可以尝试一下。输入 `help` 将显示命令列表，而 `o` 将显示当前的选项。如果你输入 `help <command>` ，即可获取特定命令的相关信息。

命令有很多，但一些常用的包括：

- `top`: 显示哪些条目占用了最多的 CPU。您可以添加一个数字，例如 `top 20` 来查看更多内容，或者使用正则表达式来“聚焦”或忽略某些项目。
- `web`: 在网页浏览器中打开调用图。这是直观查看 CPU 使用情况的绝佳方式。
- `svg`: 生成调用图的 SVG 图片。这与 `web` 类似，只是不会打开您的网页浏览器，且 SVG 文件将保存在本地。
- `tree`: 调用堆栈的表格视图。

我们先从 `top`。我们会看到如下输出：

```
(pprof) top
Showing nodes accounting for 38.36s, 54.71% of 70.11s total
Dropped 785 nodes (cum <= 0.35s)
Showing top 10 nodes out of 196
      flat  flat%   sum%        cum   cum%
    10.97s 15.65% 15.65%     10.97s 15.65%  runtime/internal/syscall.Syscall6
     6.59s  9.40% 25.05%     36.65s 52.27%  runtime.gcDrain
     5.03s  7.17% 32.22%      5.34s  7.62%  runtime.(*lfstack).pop (inline)
     3.69s  5.26% 37.48%     11.02s 15.72%  runtime.scanobject
     2.42s  3.45% 40.94%      2.42s  3.45%  runtime.(*lfstack).push
     2.26s  3.22% 44.16%      2.30s  3.28%  runtime.pageIndexOf (inline)
     2.11s  3.01% 47.17%      2.56s  3.65%  runtime.findObject
     2.03s  2.90% 50.06%      2.03s  2.90%  runtime.markBits.isMarked (inline)
     1.69s  2.41% 52.47%      1.69s  2.41%  runtime.memclrNoHeapPointers
     1.57s  2.24% 54.71%      1.57s  2.24%  runtime.epollwait
```

CPU 资源消耗排名前十的条目均位于 Go 运行时中——尤其是大量垃圾回收操作（请记住，系统调用用于释放和分配内存）。这表明我们可以通过减少内存分配来提升性能，因此进行堆剖析是值得的。

好的，但如果我们想查看自己代码中的 CPU 使用率呢？我们可以像这样忽略包含 “runtime” 的模式：

```
(pprof) top -runtime  
Active filters:
   ignore=runtime
Showing nodes accounting for 0.92s, 1.31% of 70.11s total
Dropped 160 nodes (cum <= 0.35s)
Showing top 10 nodes out of 243
      flat  flat%   sum%        cum   cum%
     0.17s  0.24%  0.24%      0.28s   0.4%  sync.(*Pool).getSlow
     0.11s  0.16%   0.4%      0.11s  0.16%  github.com/prometheus/client_golang/prometheus.(*histogram).observe (inline)
     0.10s  0.14%  0.54%      0.23s  0.33%  github.com/prometheus/client_golang/prometheus.(*MetricVec).hashLabels
     0.10s  0.14%  0.68%      0.12s  0.17%  net/textproto.CanonicalMIMEHeaderKey
     0.10s  0.14%  0.83%      0.10s  0.14%  sync.(*poolChain).popTail
     0.08s  0.11%  0.94%      0.26s  0.37%  github.com/prometheus/client_golang/prometheus.(*histogram).Observe
     0.07s   0.1%  1.04%      0.07s   0.1%  internal/poll.(*fdMutex).rwlock
     0.07s   0.1%  1.14%      0.10s  0.14%  path/filepath.Clean
     0.06s 0.086%  1.23%      0.06s 0.086%  context.value
     0.06s 0.086%  1.31%      0.06s 0.086%  go.uber.org/zap/buffer.(*Buffer).AppendByte
```

显然，Prometheus 的指标也是一个主要的资源消耗源，但您会发现，其累计消耗量比上文提到的垃圾回收（GC）要少几个数量级。这种显著的差异表明，我们应重点关注减少 GC 的消耗。

<aside class="tip">

需要注意的是，CPU 剖析报告中的测量数据来自间歇性采样，且采样频率绝不会高于默认的 10 毫秒。这就是为什么您不会看到任何小于 10 毫秒的累计时间（实际时间可能更短，但会被向上取整）。 若需获取更精确的时间数据，可执行执行跟踪（execution trace），该操作不依赖采样机制。（待办事项：添加关于执行跟踪的章节。）

</aside>

让我们使用 `q` 退出此剖析视图，并在堆剖析上使用相同的命令：

```
(pprof) top
Showing nodes accounting for 22259.07kB, 81.30% of 27380.04kB total
Showing top 10 nodes out of 102
      flat  flat%   sum%        cum   cum%
   12300kB 44.92% 44.92%    12300kB 44.92%  runtime.allocm
 2570.01kB  9.39% 54.31%  2570.01kB  9.39%  bufio.NewReaderSize
 2048.81kB  7.48% 61.79%  2048.81kB  7.48%  runtime.malg
 1542.01kB  5.63% 67.42%  1542.01kB  5.63%  bufio.NewWriterSize
 ...
 ```

说得对。由于我们使用了bufio包，近一半的内存被专门分配给了读写缓冲区。因此，我们可以推断，通过优化代码来减少缓冲将大有裨益。（[Caddy中的相关补丁](https://github.com/caddyserver/caddy/pull/4978)正是为此而设计的）。

### 可视化

如果我们改运行 `svg` 或 `web` 命令，我们将获得性能分析图：

![CPU 剖析可视化](/old/resources/images/profile.png)

这是一份 CPU 性能分析报告，但其他类型的性能分析报告也包含类似的图表。

要了解如何阅读这些图表，请参阅 [pprof 文档](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph)。


### 剖析比较

修改代码后，您可以使用差异分析（“diff”）来比较修改前后的内容。以下是堆的差异分析结果：

<pre><code class="cmd bash">go tool pprof -diff_base=before.prof after.prof
File: caddy
Type: inuse_space
Time: Aug 29, 2022 at 1:21am (MDT)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) top
Showing nodes accounting for -26.97MB, 49.32% of 54.68MB total
Dropped 10 nodes (cum <= 0.27MB)
Showing top 10 nodes out of 137
      flat  flat%   sum%        cum   cum%
  -27.04MB 49.45% 49.45%   -27.04MB 49.45%  bufio.NewWriterSize
      -2MB  3.66% 53.11%       -2MB  3.66%  runtime.allocm
    1.06MB  1.93% 51.18%     1.06MB  1.93%  github.com/yuin/goldmark/util.init
    1.03MB  1.89% 49.29%     1.03MB  1.89%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.glob..func2
       1MB  1.84% 47.46%        1MB  1.84%  bufio.NewReaderSize
      -1MB  1.83% 49.29%       -1MB  1.83%  runtime.malg
       1MB  1.83% 47.46%        1MB  1.83%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.cloneRequest
      -1MB  1.83% 49.29%       -1MB  1.83%  net/http.(*Server).newConn
   -0.55MB  1.00% 50.29%    -0.55MB  1.00%  html.populateMaps
    0.53MB  0.97% 49.32%     0.53MB  0.97%  github.com/alecthomas/chroma.TypeRemappingLexer</code></pre>

如您所见，我们把内存分配量减少了一半左右！

差异也可以可视化：

![CPU 性能分析可视化](/old/resources/images/profile-diff.png)

这清楚地表明了这些更改如何影响了程序某些部分的性能。

## 延伸阅读

程序剖析涉及的内容非常广泛，而我们目前仅是略知皮毛。

要想真正把“专业”二字体现在“性能剖析”上，不妨参考以下资源：

- [pprof 文档](https://github.com/google/pprof/blob/main/doc/README.md)
- [Caddy 中的剖析实践](https://github.com/caddyserver/caddy/pull/4978)
- [“移动性能”维基](https://github.com/golang/go/wiki/Performance)
- [`net/http/pprof` 包](https://pkg.go.dev/net/http/pprof)
