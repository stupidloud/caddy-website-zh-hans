---
title: 剖析 Caddy (Profiling Caddy)
---

<a id="profiling-caddy"></a>
剖析 Caddy
================

**程序剖析 (program profile)** 是程序在運行時資源使用情況的快照。剖析對於識別問題區域、排除錯誤和當機以及優化代碼非常有幫助。

Caddy 使用 Go 的工具來捕獲剖析，這被稱為 [pprof](https://github.com/google/pprof)，它內置於 `go` 命令中。

剖析報告 CPU 和內存的消耗者，顯示 goroutine 的堆棧追蹤，並幫助追蹤死鎖或高爭用的同步原語。

在報告 Caddy 中的某些錯誤時，我們可能會要求提供剖析文件。這篇文章可以提供幫助。它描述了如何通過 Caddy 獲取剖析，以及通常如何使用和解釋生成的 pprof 剖析。


在開始之前，有兩件事需要了解：

1. **Caddy 剖析不涉及安全敏感信息。** 它們包含的是無害的技術讀數，而不是內存內容。它們不會授予對系統的訪問權限。共享它們是安全的。
2. **剖析是輕量級的，可以在生產環境中收集。** 事實上，對於許多用戶來說，這是一個推薦的最佳實踐；請參閱本文後面的內容。

<a id="obtaining-profiles"></a>
## 獲取剖析 (Obtaining profiles)

剖析可通過 [管理接口](/docs/api) 的 `/debug/pprof/` 獲取。在運行 Caddy 的機器上，在瀏覽器中打開它：

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	預設情況下，管理 API 僅能從本地訪問。如果在遠端、虛擬機或容器中運行，請參閱下一節了解如何訪問此端點。
</aside>

你會注意到一個簡單的計數和連結表格，例如：

Count | Profile
----- | --------------------
79    | allocs
0     | block
0     | cmdline
22    | goroutine
79    | heap
0     | mutex
0     | profile
29    | threadcreate
0     | trace
|     | full goroutine stack dump

這些計數是快速識別洩漏的便捷方式。如果你懷疑有洩漏，請反覆刷新頁面，你會看到其中一個或多個計數不斷增加。如果 heap 計數增加，可能是內存洩漏；如果 goroutine 計數增加，可能是 goroutine 洩漏。

點擊剖析並查看它們的樣子。有些可能是空的，這在很多時候是正常的。最常用的是 <b>goroutine</b> (函數堆棧)、<b>heap</b> (內存) 和 <b>profile</b> (CPU)。其他剖析對於排除 mutex 爭用或死鎖非常有用。

在底部，有對每個剖析的簡單描述：

- **allocs:** 所有過去內存分配的採樣
- **block:** 導致同步原語阻塞的堆棧追蹤
- **cmdline:** 當前程序的命令行調用
- **goroutine:** 所有當前 goroutine 的堆棧追蹤。使用 debug=2 作為查詢參數，以與未恢復的 panic 相同的格式導出。
- **heap:** 活動對象內存分配的採樣。你可以指定 gc GET 參數在獲取堆採樣之前運行 GC。
- **mutex:** 爭用 mutex 持有者的堆棧追蹤
- **profile:** CPU 剖析。你可以在 seconds GET 參數中指定持續時間。獲取剖析文件後，使用 go tool pprof 命令調查剖析。
- **threadcreate:** 導致創建新操作系統線程的堆棧追蹤
- **trace:** 當前程序執行的追蹤。你可以在 seconds GET 參數中指定持續時間。獲取追蹤文件後，使用 go tool trace 命令調查追蹤。

<aside class="tip">

"goroutine" 和 "full goroutine stack dump" 之間的區別在於 `?debug=2` 參數：完整堆棧轉儲就像你在 panic 後看到的輸出；它更詳細，而且值得注意的是，它不會合併相同的 goroutine。

</aside>


<a id="downloading-profiles"></a>
### 下載剖析 (Downloading profiles)

點擊上面 pprof 索引頁面上的連結將為你提供文本格式的剖析。這對於調試很有用，也是我們 Caddy 團隊偏好的方式，因為我們可以掃描它以尋找明顯的線索，而無需額外的工具。

但二進制實際上是預設格式。HTML 連結附加了 `?debug=` 查詢字符串參數以將其格式化為文本，但 (CPU) "profile" 連結除外，它沒有文本表示。

以下是可以設置的查詢字符串參數 (來自 [Go 文檔](https://pkg.go.dev/net/http/pprof#hdr-Parameters)):

- **`debug=N` (除 cpu 外的所有剖析):** 響應格式：N = 0: 二進制 (預設)，N > 0: 純文本
- **`gc=N` (heap 剖析):** N > 0: 在剖析前運行垃圾回收週期
- **`seconds=N` (allocs, block, goroutine, heap, mutex, threadcreate 剖析):** 返回增量剖析
- **`seconds=N` (cpu, trace 剖析):** 給定持續時間的剖析

因為這些是 HTTP 端點，你也可以使用任何 HTTP 客戶端（如 curl 或 wget）來下載剖析。

下載剖析後，你可以將它們上傳到 GitHub issue 評論或使用 [pprof.me](https://pprof.me/) 之類的網站。專門針對 CPU 剖析，[flamegraph.com](https://flamegraph.com/) 是另一個選擇。


<a id="accessing-remotely"></a>
## 遠端訪問 (Accessing remotely)

*如果你已經能夠在本地訪問管理 API，請跳過本節。*

預設情況下，Caddy 的管理 API 只能通過迴環套接字 (loopback socket) 訪問。但是，至少有 3 種方式可以遠端訪問 Caddy 的 `/debug/pprof` 端點：

<a id="reverse-proxy-through-your-site"></a>
### 通過你的網站進行反向代理 (Reverse proxy through your site)

一個簡單的選擇是直接從你的網站反向代理到它：

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

當然，這將使剖析對能夠連接到你網站的人可用。如果這不是你想要的，你可以使用你選擇的 HTTP auth 模組添加一些身份驗證。

(不要忘記 `/debug/pprof/*` matcher，否則你將代理整個管理 API！)


<a id="ssh-tunnel"></a>
### SSH 隧道 (SSH tunnel)

另一種方式是使用 SSH 隧道。這是你的電腦和服務器之間使用 SSH 協議的加密連接。在你的電腦上運行如下命令：

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

這會將 `localhost:8123` (在你的本地機器上) 隧道化到 `example.com` 上的 `localhost:2019`。請確保根據需要替換 `username`、`example.com` 和端口。

<aside class="tip">

此命令將在前台運行。請記住，如果你嘗試使用 <kbd>Ctrl</kbd>+<kbd>Z</kbd> 將進程轉入後台，它會暫停隧道，使用該隧道的連接將無法連接。

</aside>

然後在另一個終端中，你可以像這樣運行 `curl`:

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

你可以通過在隧道的兩端都使用端口 `2019` 來避免需要 `-H "Host: ..."` (但這要求你的電腦上尚未佔用端口 `2019`，即本地未運行 Caddy)。

當隧道處於活動狀態時，你可以訪問任何及所有管理 API。在 `ssh` 命令上輸入 <kbd>Ctrl</kbd>+<kbd>C</kbd> 即可關閉隧道。

<a id="long-running-tunnel"></a>
#### 長期運行的隧道 (Long-running tunnel)

使用上述命令運行隧道需要你保持終端打開。如果你想在後台運行隧道，可以像這樣啟動隧道：

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

這將在後台啟動並在 `/tmp/caddy-tunnel.sock` 創建一個控制套接字。完成後，你可以使用該控制套接字關閉隧道：

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>


<a id="remote-admin-api"></a>
### 遠端管理 API (Remote admin API)

你還可以配置管理 API 以接受來自授權客戶端的遠端連接。

(待辦事項：撰寫關於此內容的文章。)



<a id="goroutine-profiles"></a>
## Goroutine 剖析 (Goroutine profiles)

goroutine 轉儲對於了解存在哪些 goroutine 以及它們的調用堆棧非常有用。換句話說，它讓我們了解當前正在執行或正在阻塞/等待的代碼。

如果你點擊 "goroutines" 或轉到 `/debug/pprof/goroutine?debug=1`，你將看到 goroutine 列表及其調用堆棧。例如：

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

第一行 `goroutine profile: total 88` 告訴我們正在查看什麼以及有多少個 goroutine。

接下來是 goroutine 列表。它們按調用堆棧的頻率降序排列。

goroutine 行的語法如下：`<count> @ <addresses...>`

該行以具有相關調用堆棧的 goroutine 計數開始。`@` 符號表示調用指令地址（即啟動 goroutine 的函數指針）的開始。每個指針都是一個函數調用或調用幀 (call frame)。

你可能會注意到，許多 goroutine 共享同一個第一調用地址。這是你的程序的主入口點 (main)。有些 goroutine 不會從那裡發起，因為程序有各種 `init()` 函數，而且 Go runtime 也可能派生 goroutine。

後面的行以 `#` 開頭，實際上只是為了方便讀者閱讀的註釋。它們包含 goroutine 當前的堆棧追蹤。頂部代表堆棧頂部，即當前正在執行的代碼行。底部代表堆棧底部，或 goroutine 最初開始運行的代碼。

堆棧追蹤的格式如下：

```
<address> <package/func>+<offset> <filename>:<line>
```

地址是函數指針，然後你會看到 Go package 和函數名稱 (如果是方法，則帶有相關的類型名稱)，以及函數內的指令偏移量。最後是可能最有用的信息：文件和行號。

<a id="full-goroutine-stack-dump"></a>
### 完整 goroutine 堆棧轉儲 (Full goroutine stack dump)

如果我們將查詢字符串參數更改為 `?debug=2`，我們將獲得完整轉儲。這包括每個 goroutine 的詳細堆棧追蹤，並且相同的 goroutine 不會被合併。在繁忙的服務器上，此輸出可能非常龐大，但它是很有趣的信息！

讓我們看一個與上面的第一個調用堆棧對應的例子 (已截斷)：

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

儘管非常冗長，但此轉儲唯一提供的最有用的信息是每個 goroutine 的第一行和最後一行。

第一行包含 goroutine 的編號 (61961905)、狀態 ("IO wait") 和持續時間 ("1 minutes")：

- **Goroutine 編號:** 是的，goroutine 有編號！但它們不向我們的代碼公開。然而，這些編號在堆棧追蹤中特別有用，因為我們可以看到哪個 goroutine 派生了這一個 (參見末尾："created by ... in goroutine 61961902")。下面顯示的工具有助於我們繪製其視覺圖表。

- **狀態:** 這告訴我們 goroutine 當前正在做什麼。以下是你可能會看到的一些可能狀態：
	- `running`: 正在執行代碼 - 太棒了！
	- `IO wait`: 等待網絡。不消耗操作系統線程，因為它停靠在非阻塞網絡輪詢器 (network poller) 上。
	- `sleep`: 我們都需要更多的睡眠。
	- `select`: 阻塞在 select 上；等待一個 case 可用。
	- `select (no cases):` 特別是阻塞在空的 `select {}` 上。Caddy 在其 main 中使用一個來保持運行，因為關機是從其他 goroutine 發起的。
	- `chan receive`: 阻塞在通道接收 (`<-ch`) 上。
	- `semacquire`: 等待獲取信號量 (semaphore，低級同步原語)。
	- `syscall`: 執行系統調用。消耗一個操作系統線程。

- **持續時間:** goroutine 已存在多長時間。對於查找 goroutine 洩漏等錯誤非常有用。例如，如果我們預期所有網絡連接在幾分鐘後關閉，那麼當我們發現很多活動了幾個小時的 netconn goroutine 時，這意味著什麼？

<a id="interpreting-goroutine-dumps"></a>
### 解釋 goroutine 轉儲 (Interpreting goroutine dumps)

不看代碼，我們能從上述 goroutine 中學到什麼？

它是在大約一分鐘前創建的，正在等待網絡套接字上的數據，並且它的 goroutine 編號非常大 (61961905)。

從第一個轉儲 (debug=1) 中，我們知道它的調用堆棧執行頻率相對較高，而且較大的 goroutine 編號結合較短的持續時間表明，已經存在數千萬個這種壽命相對較短的 goroutine。它處於名為 `pollWait` 的函數中，其調用歷史包括從使用 TLS 的加密網絡連接中讀取 HTTP/2 幀。

因此，我們可以推斷出這個 goroutine 正在處理一個 HTTP/2 請求！它正在等待來自客戶端的數據。更重要的是，我們知道派生它的 goroutine 不是進程的第一批 goroutine 之一，因為它也有一個很高的編號；在轉儲中找到該 goroutine 會發現它是在現有請求期間為處理新的 HTTP/2 流而派生的。相比之下，其他具有高編號的 goroutine 可能是由低編號的 goroutine (如 32) 派生的，這表示一個全新的連接剛從套接字的 `Accept()` 調用中產生。

每個程序都不同，但在調試 Caddy 時，這些模式往往是成立的。

<a id="memory-profiles"></a>
## 內存剖析 (Memory profiles)

內存 (或堆) 剖析追蹤堆分配，這是系統內存的主要消耗者。分配也是性能問題的常見嫌疑人，因為分配內存需要系統調用，這可能很慢。

堆剖析在幾乎所有方面看起來都與 goroutine 剖析相似，除了頂行的開頭。這是一個例子：

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

在上面的例子中，我們有一個由 `bufio.NewWriterSize()` 執行的單次分配，但目前沒有來自此調用堆棧的活動對象。

有趣的是，我們可以從該調用堆棧中推斷出 http2 包使用了一個池化的 4 KB 來向客戶端寫入 HTTP/2 幀。如果熱點路徑經過優化以重用分配，你經常會在 Go 內存剖析中看到池化對象。這減少了新的分配，堆剖析可以幫助你了解池是否被正確使用！

<a id="cpu-profiles"></a>
## CPU 剖析 (CPU profiles)

CPU 剖析可幫助你了解 Go 程序在處理器上的大部分預定時間花在了哪裡。

但是，這些剖析沒有純文本形式，因此在下一節中，我們將使用 `go tool pprof` 命令來幫助我們讀取它們。

要下載 CPU 剖析，請向 `/debug/pprof/profile?seconds=N` 發起請求，其中 N 是你想要收集剖析的秒數。在收集 CPU 剖析期間，程序性能可能會受到輕微影響。(其他剖析幾乎沒有性能影響。)

完成後，它應該會下載一個二進制文件，恰如其名地稱為 `profile`。然後我們需要檢查它。

<a id="go-tool-pprof"></a>
## `go tool pprof`

我們將以使用 Go 內置的剖析分析器讀取 CPU 剖析為例，但你可以將其用於任何類型的剖析。

運行此命令 (如果不同，請將 "profile" 替換為實際的文件路徑)，這將打開一個交互式提示：

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">

你可以使用此命令檢查任何類型的剖析，而不僅僅是 CPU 剖析。對於其他剖析，原理是相同的，概念也是共通的。

</aside>

這是你可以探索的內容。輸入 `help` 會為你提供命令列表，輸入 `o` 將顯示當前選項。如果你輸入 `help <command>`，你可以獲得有關特定命令的信息。

有很多命令，但一些常見的是：

- `top`: 顯示消耗 CPU 最多的部分。你可以附加一個數字（如 `top 20`）來查看更多內容，或使用正則表達式來 "focus" (關注) 或忽略某些項目。
- `web`: 在網絡瀏覽器中打開調用圖。這是直觀查看 CPU 使用情況的好方法。
- `svg`: 生成調用圖的 SVG 圖像。它與 `web` 相同，只是它不會打開你的網絡瀏覽器，並且 SVG 會保存在本地。
- `tree`: 調用堆棧的表格視圖。

讓我們從 `top` 開始。我們看到如下輸出：

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

CPU 的前 10 個消耗者都在 Go runtime 中 - 特別是大量的垃圾回收 (請記住系統調用用於釋放和分配內存)。這暗示我們可以通過減少分配來提高性能，堆剖析將是值得的。

好的，但如果我們想查看來自我們自己代碼的 CPU 利用率呢？我們可以像這樣忽略包含 "runtime" 的模式：

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

顯然，Prometheus 指標是另一個主要的消耗者，但你會注意到，累計起來，它們的量級比上面的 GC 小得多。這種鮮明的對比表明我們應該專注於減少 GC。

<aside class="tip">

重要的是要注意，CPU 剖析是從間歇性採樣中獲取測量值的，並且採樣捕獲的頻率絕不會高於採樣率（預設為 10ms）。這就是為什麼你不會看到任何小於 10ms 的累計持續時間 (它們可能更小，但被向上取整)。對於更具體的計時，你可以進行執行追蹤 (execution trace)，它不使用採樣閉。(待辦事項：添加關於追蹤的章節。)

</aside>

讓我們使用 `q` 退出此剖析，並在堆剖析上使用相同的命令：

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

賓果。近一半的內存分配嚴格用於我們使用 bufio 包時的讀寫緩衝區。因此，我們可以推斷，優化我們的代碼以減少緩衝將非常有益。(Caddy 中 [相關的補丁](https://github.com/caddyserver/caddy/pull/4978) 正是這樣做的)。

<a id="visualizations"></a>
### 可視化 (Visualizations)

如果我們改為運行 `svg` 或 `web` 命令，我們將獲得剖析的可視化圖表：

![CPU 剖析可視化](/old/resources/images/profile.png)

這是一個 CPU 剖析圖，但類似的圖表也可用於其他剖析類型。

要學習如何閱讀這些圖表，請閱讀 [pprof 文檔](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph)。


<a id="diffing-profiles"></a>
### 對比剖析 (Diffing profiles)

進行代碼更改後，你可以使用差異分析 ("diff") 比較前後情況。這是堆的差異對比：

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

如你所見，我們將內存分配減少了大約一半！

差異也可以可視化：

![CPU 剖析可視化](/old/resources/images/profile-diff.png)

這使得更改如何影響程序某些部分的性能變得非常明顯。

<a id="further-reading"></a>
## 延伸閱讀 (Further reading)

程序剖析有很多需要掌握的內容，我們僅僅觸及了皮毛。

要真正成為 "剖析" 專家，請考慮以下資源：

- [pprof 文檔](https://github.com/google/pprof/blob/main/doc/README.md)
- [Caddy 剖析的一個真實案例](https://github.com/caddyserver/caddy/pull/4978)
- [Go wiki 上的性能頁面](https://github.com/golang/go/wiki/Performance)
- [`net/http/pprof` 包](https://pkg.go.dev/net/http/pprof)
