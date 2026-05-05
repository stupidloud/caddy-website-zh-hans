---
title: Caddy をプロファイリングする
---

<a id="profiling-caddy"></a>
プロファイリング Caddy
================

**プログラムプロファイル** は、実行時にプログラムが使っているリソースのスナップショットです。プロファイルは、問題箇所の特定、バグやクラッシュのトラブルシューティング、コードの最適化に非常に役立ちます。

Caddy はプロファイルの取得に Go のツールを使います。これは [pprof](https://github.com/google/pprof) と呼ばれ、`go` コマンドに組み込まれています。

プロファイルは CPU やメモリの消費元を報告し、goroutine の stack trace を表示し、デッドロックや競合の激しい同期プリミティブの追跡に役立ちます。

Caddy の特定のバグを報告するとき、私たちはプロファイルの提供をお願いすることがあります。この記事はその助けになります。Caddy でプロファイルを取得する方法と、生成された pprof プロファイルを一般にどう使い、どう解釈するかの両方を説明します。


始める前に知っておくべきことが 2 つあります。

1. **Caddy のプロファイルはセキュリティ上機密ではありません。** メモリの内容ではなく、無害な技術的読み取り値を含むだけです。システムへのアクセス権を与えるものではありません。共有しても安全です。
2. **プロファイルは軽量で、本番環境でも収集できます。** 実際、多くのユーザーに推奨されるベストプラクティスです。この記事の後半を参照してください。

<a id="obtaining-profiles"></a>
## プロファイルを取得する

プロファイルは [admin interface](/docs/api) の `/debug/pprof/` から利用できます。Caddy が動いているマシンで、ブラウザから開きます。

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	既定では admin API はローカルからしかアクセスできません。リモート、VM、コンテナで実行している場合、このエンドポイントへアクセスする方法は次のセクションを参照してください。
</aside>

次のような、件数とリンクの簡単な表が表示されます。

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

件数は、リークを素早く特定するのに便利です。リークを疑う場合は、ページを繰り返し更新してください。これらの件数のうち 1 つ以上が継続的に増え続けるのが見えるでしょう。heap 件数が増えるならメモリリークの可能性があり、goroutine 件数が増えるなら goroutine リークの可能性があります。

各プロファイルのリンクを開き、どのように見えるか確認してください。一部が空でも、多くの場合それは正常です。最もよく使われるのは <b>goroutine</b>（関数 stack）、<b>heap</b>（メモリ）、<b>profile</b>（CPU）です。他のプロファイルは mutex 競合やデッドロックのトラブルシューティングに役立ちます。

下部には、各プロファイルの簡単な説明があります。

- **allocs:** 過去のすべてのメモリアロケーションのサンプリング
- **block:** 同期プリミティブでブロックする原因になった stack trace
- **cmdline:** 現在のプログラムのコマンドライン呼び出し
- **goroutine:** 現在のすべての goroutine の stack trace。復旧されなかった panic と同じ形式でエクスポートするには、クエリパラメータとして debug=2 を使います。
- **heap:** 生存オブジェクトのメモリアロケーションのサンプリング。heap サンプル取得前に GC を実行するには、gc GET パラメータを指定できます。
- **mutex:** 競合した mutex を保持していた側の stack trace
- **profile:** CPU プロファイル。seconds GET パラメータで秒数を指定できます。プロファイルファイルを取得した後、go tool pprof コマンドで調査します。
- **threadcreate:** 新しい OS thread の作成につながった stack trace
- **trace:** 現在のプログラムの実行 trace。seconds GET パラメータで秒数を指定できます。trace ファイルを取得した後、go tool trace コマンドで調査します。

<aside class="tip">

"goroutine" と "full goroutine stack dump" の違いは `?debug=2` パラメータです。full stack dump は panic 後に見える出力に似ており、より冗長で、特に同一の goroutine を畳み込みません。

</aside>


<a id="downloading-profiles"></a>
### プロファイルをダウンロードする

上の pprof インデックスページのリンクをクリックすると、テキスト形式のプロファイルが得られます。これはデバッグに便利で、Caddy チームとしても好んで使う形式です。追加ツールなしで明らかな手がかりを探せるからです。

ただし、実際の既定形式はバイナリです。HTML リンクは、(CPU) "profile" リンクを除き、テキスト形式にするため `?debug=` クエリ文字列パラメータを付けています。CPU profile にはテキスト表現がありません。

設定できるクエリ文字列パラメータは次の通りです（[Go docs](https://pkg.go.dev/net/http/pprof#hdr-Parameters) より）。

- **`debug=N`（cpu を除くすべてのプロファイル）:** レスポンス形式: N = 0 はバイナリ（既定）、N > 0 はプレーンテキスト
- **`gc=N`（heap profile）:** N > 0 なら、プロファイリング前に garbage collection cycle を実行
- **`seconds=N`（allocs、block、goroutine、heap、mutex、threadcreate profiles）:** delta profile を返す
- **`seconds=N`（cpu、trace profiles）:** 指定された期間だけプロファイルする

これらは HTTP エンドポイントなので、curl や wget のような任意の HTTP クライアントでもプロファイルをダウンロードできます。

プロファイルをダウンロードしたら、GitHub issue のコメントへアップロードしたり、[pprof.me](https://pprof.me/) のようなサイトを使ったりできます。CPU profile については、[flamegraph.com](https://flamegraph.com/) も選択肢です。


<a id="accessing-remotely"></a>
## リモートからアクセスする

*すでに admin API へローカルでアクセスできる場合は、このセクションをスキップしてください。*

既定では、Caddy の admin API は loopback socket 経由でしかアクセスできません。ただし、Caddy の `/debug/pprof` エンドポイントへリモートからアクセスする方法は少なくとも 3 つあります。

<a id="reverse-proxy-through-your-site"></a>
### サイト経由で reverse proxy する

簡単な選択肢の 1 つは、サイトから単純に reverse proxy することです。

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

当然ながら、これによりサイトへ接続できる人はプロファイルを利用できるようになります。それが望ましくない場合は、任意の HTTP auth モジュールを使って認証を追加できます。

（`/debug/pprof/*` matcher を忘れないでください。そうしないと admin API 全体をプロキシしてしまいます。）


<a id="ssh-tunnel"></a>
### SSH tunnel

別の方法は SSH tunnel を使うことです。これはあなたのコンピュータとサーバーの間で SSH プロトコルを使う暗号化接続です。あなたのコンピュータで次のようなコマンドを実行します。

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

これは（ローカルマシン上の）`localhost:8123` を `example.com` 上の `localhost:2019` へトンネルします。必要に応じて `username`、`example.com`、ポートを置き換えてください。

<aside class="tip">

このコマンドはフォアグラウンドで実行されます。<kbd>Ctrl</kbd>+<kbd>Z</kbd> でプロセスをバックグラウンド化しようとすると、トンネルが一時停止し、そのトンネルを使う接続は失敗する点に注意してください。

</aside>

その後、別のターミナルで次のように `curl` を実行できます。

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

トンネルの両側でポート `2019` を使えば、`-H "Host: ..."` を不要にできます（ただし、あなたのコンピュータでポート `2019` がすでに使われていないこと、つまりローカルで Caddy が動いていないことが必要です）。

トンネルが有効な間は、admin API の任意の部分へアクセスできます。トンネルを閉じるには、`ssh` コマンドで <kbd>Ctrl</kbd>+<kbd>C</kbd> を入力します。

<a id="long-running-tunnel"></a>
#### 長時間実行する tunnel

上のコマンドで tunnel を実行するには、ターミナルを開いたままにする必要があります。バックグラウンドで tunnel を実行したい場合は、次のように開始できます。

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

これはバックグラウンドで起動し、`/tmp/caddy-tunnel.sock` に control socket を作成します。作業が終わったら、この control socket を使って tunnel を閉じられます。

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>


<a id="remote-admin-api"></a>
### Remote admin API

認可されたクライアントからのリモート接続を受け入れるよう、admin API を設定することもできます。

（TODO: これについての記事を書く。）



<a id="goroutine-profiles"></a>
## Goroutine profiles

goroutine dump は、どの goroutine が存在し、それぞれの call stack が何かを知るのに役立ちます。言い換えると、現在実行中、またはブロック/待機中のコードの見当を付けられます。

"goroutines" をクリックするか `/debug/pprof/goroutine?debug=1` へアクセスすると、goroutine とその call stack の一覧が表示されます。例:

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

最初の行 `goroutine profile: total 88` は、何を見ているかと goroutine の数を示しています。

その後に goroutine の一覧が続きます。call stack ごとに、頻度の高い順でグループ化されています。

goroutine 行の構文は `<count> @ <addresses...>` です。

行は、関連する call stack を持つ goroutine の数から始まります。`@` 記号は、その goroutine の発生元となった呼び出し命令アドレス、つまり関数ポインタの開始を示します。各ポインタは関数呼び出し、または call frame です。

多くの goroutine が同じ最初の呼び出しアドレスを共有していることに気付くかもしれません。これはプログラムの main、つまり entry point です。一部の goroutine はそこから発生しません。プログラムにはさまざまな `init()` 関数があり、Go runtime も goroutine を生成することがあるためです。

続く `#` で始まる行は、実際には読み手のためのコメントです。そこには goroutine の現在の stack trace が含まれています。上部は stack の先頭、つまり現在実行中のコード行を表します。下部は stack の底、つまり goroutine が最初に実行し始めたコードを表します。

stack trace の形式は次の通りです。

```
<address> <package/func>+<offset> <filename>:<line>
```

address は関数ポインタです。その後に Go package と関数名（メソッドなら関連する型名も含む）、関数内の命令 offset が続きます。最後に、最も有用な情報であるファイル名と行番号があります。

<a id="full-goroutine-stack-dump"></a>
### Full goroutine stack dump

クエリ文字列パラメータを `?debug=2` に変更すると、full dump が得られます。これにはすべての goroutine の詳細な stack trace が含まれ、同一の goroutine は畳み込まれません。ビジーなサーバーではこの出力は非常に大きくなることがありますが、興味深い情報です。

上の最初の call stack に対応するものを見てみましょう（省略あり）。

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

冗長ではありますが、この dump が一意に提供する最も有用な情報は、各 goroutine の最初と最後の行です。

最初の行には goroutine の番号（61961905）、状態（"IO wait"）、期間（"1 minutes"）が含まれます。

- **Goroutine 番号:** はい、goroutine には番号があります。ただし、私たちのコードからは公開されていません。それでも stack trace では非常に役立ちます。どの goroutine がこれを生成したかが分かるからです（末尾の "created by ... in goroutine 61961902" を参照）。下で示すツールは、これを視覚的なグラフとして描く助けになります。

- **状態:** goroutine が現在何をしているかを示します。表示される可能性のある状態には次のようなものがあります。
	- `running`: コードを実行中。すばらしい。
	- `IO wait`: ネットワーク待ち。非ブロッキングネットワーク poller で待機しているため、OS thread は消費しません。
	- `sleep`: 私たちにももっと必要なものです。
	- `select`: select でブロック中。case が利用可能になるのを待っています。
	- `select (no cases):` 空の select `select {}` でブロック中。Caddy は、shutdown が他の goroutine から開始されるため、実行を継続するために main でこれを使います。
	- `chan receive`: channel receive（`<-ch`）でブロック中。
	- `semacquire`: semaphore（低レベル同期プリミティブ）の取得待ち。
	- `syscall`: system call を実行中。OS thread を消費します。

- **期間:** goroutine が存在している時間。goroutine リークのようなバグを見つけるのに役立ちます。たとえば、すべてのネットワーク接続が数分後に閉じると期待しているのに、多数の netconn goroutine が何時間も生存している場合、それは何を意味するでしょうか。

<a id="interpreting-goroutine-dumps"></a>
### goroutine dump を解釈する

コードを見ずに、上の goroutine から何が分かるでしょうか。

これは約 1 分前に作成され、ネットワークソケット越しのデータを待っており、goroutine 番号はかなり大きい（61961905）です。

最初の dump（debug=1）から、この call stack は比較的頻繁に実行されていることが分かります。また、大きな goroutine 番号と短い期間を組み合わせると、このような比較的短命な goroutine が数千万個作られてきたことが示唆されます。これは `pollWait` という関数内にあり、呼び出し履歴には TLS を使う暗号化ネットワーク接続から HTTP/2 frame を読み取る処理が含まれます。

したがって、この goroutine は HTTP/2 リクエストを処理していると推測できます。クライアントからのデータを待っています。さらに、それを生成した goroutine も大きな番号を持っているため、プロセス初期の goroutine ではないことが分かります。dump 内でその goroutine を探すと、既存リクエスト中に新しい HTTP/2 stream を処理するために生成されたことが分かります。対照的に、大きな番号を持つ他の goroutine が、32 のような小さい番号の goroutine から生成されている場合は、socket の `Accept()` 呼び出し直後の新しい接続を示します。

プログラムごとに違いはありますが、Caddy をデバッグするとき、これらのパターンはたいてい当てはまります。

<a id="memory-profiles"></a>
## Memory profiles

Memory（または heap）profiles は heap allocation を追跡します。heap allocation はシステム上のメモリの主な消費元です。アロケーションは、メモリ確保に system call が必要で遅くなり得るため、性能問題のよくある容疑者でもあります。

heap profile は、先頭行の始まりを除き、ほぼすべての点で goroutine profile に似ています。例:

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

最初の行の形式は次の通りです。

```
<live objects> <live memory> [<allocations>: <allocation memory>] @ <addresses...>
```

上の例では、`bufio.NewWriterSize()` によって 1 回の allocation が行われていますが、この call stack から現在生存している object はありません。

興味深いことに、この call stack から、http2 package が client へ HTTP/2 frame を書き込むために pooled 4 KB を使ったと推測できます。Go の memory profile では、hot path が allocation を再利用するよう最適化されている場合、pooled object をよく見かけます。これにより新しい allocation が減り、heap profile は pool が適切に使われているかを知る助けになります。

<a id="cpu-profiles"></a>
## CPU profiles

CPU profiles は、Go プログラムがプロセッサ上でスケジュールされた時間を主にどこで使っているかを理解するのに役立ちます。

ただし、これらにはプレーンテキスト形式がないため、次のセクションでは `go tool pprof` コマンドを使って読み取ります。

CPU profile をダウンロードするには、`/debug/pprof/profile?seconds=N` へリクエストします。N はプロファイルを収集する秒数です。CPU profile の収集中は、プログラム性能に軽い影響が出ることがあります。（他のプロファイルは実質的に性能影響がありません。）

完了すると、適切にも `profile` という名前のバイナリファイルがダウンロードされます。次に、それを調べる必要があります。

## `go tool pprof`

例として CPU profile を読むために Go 組み込みの profile analyzer を使いますが、どの種類の profile にも使えます。

次のコマンドを実行します（"profile" は実際のファイルパスが異なる場合は置き換えてください）。interactive prompt が開きます。

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">

このコマンドは CPU profiles だけでなく、どの種類の profile の調査にも使えます。原則は他の profile でも同じで、概念も引き継がれます。

</aside>

これは自分で探索できます。`help` を入力するとコマンド一覧が表示され、`o` は現在のオプションを表示します。`help <command>` と入力すれば、特定のコマンドについての情報を得られます。

コマンドは多数ありますが、よく使うものは次の通りです。

- `top`: CPU を最も使ったものを表示します。`top 20` のように数値を追加して多く表示したり、regex を指定して特定項目へ「focus」したり無視したりできます。
- `web`: call graph を Web ブラウザで開きます。CPU 使用量を視覚的に見るのに優れた方法です。
- `svg`: call graph の SVG 画像を生成します。Web ブラウザを開かず、SVG がローカルへ保存される点を除き `web` と同じです。
- `tree`: call stack の表形式ビューです。

`top` から始めましょう。次のような出力が見えます。

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

CPU の上位 10 消費元はすべて Go runtime 内でした。特に garbage collection が多くあります（syscall はメモリの解放と確保に使われることを思い出してください）。これは、allocation を減らせば性能を改善できる可能性があり、heap profile を見る価値があるという手がかりです。

では、自分たちのコードによる CPU 使用率を見たい場合はどうでしょうか。次のように "runtime" を含むパターンを無視できます。

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

Prometheus metrics も上位の消費元であることは明らかですが、累積しても上の GC より桁違いに小さいことに気付くでしょう。この大きな差は、GC の削減に集中すべきことを示唆しています。

<aside class="tip">

CPU profiles は断続的なサンプリングから測定値を得るため、サンプルはサンプリングレートより頻繁には取得されません。既定では 10ms です。そのため、10ms 未満の累積時間は表示されません（実際にはそれより短い可能性がありますが、切り上げられます）。より具体的なタイミングには execution trace を使えます。これはサンプリングを使いません。（TODO: tracing についてのセクションを追加する。）

</aside>

`q` でこの profile を終了し、heap profile に同じコマンドを使ってみましょう。

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

その通りです。メモリのほぼ半分が、bufio package の使用による read/write buffers のためだけに割り当てられています。したがって、buffering を減らすようコードを最適化することは非常に有益だと推測できます。（Caddy の[関連 patch](https://github.com/caddyserver/caddy/pull/4978) はまさにそれを行っています。）

<a id="visualizations"></a>
### 可視化

代わりに `svg` または `web` コマンドを実行すると、profile の可視化が得られます。

![CPU profile visualization](/old/resources/images/profile.png)

これは CPU profile ですが、他の profile type でも同様のグラフを利用できます。

これらのグラフの読み方を学ぶには、[pprof documentation](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph) を読んでください。


<a id="diffing-profiles"></a>
### profile の差分を取る

コード変更後、差分解析（"diff"）を使って変更前後を比較できます。heap の diff の例です。

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

見ての通り、メモリアロケーションを約半分削減できました。

diff も可視化できます。

![CPU profile visualization](/old/resources/images/profile-diff.png)

これにより、変更がプログラムの特定部分の性能にどう影響したかが非常に分かりやすくなります。

<a id="further-reading"></a>
## 参考資料

プログラムプロファイリングには習得すべきことが多く、ここでは表面に触れただけです。

"profiling" の "pro" になるには、次の資料を検討してください。

- [pprof Documentation](https://github.com/google/pprof/blob/main/doc/README.md)
- [A real-world use of profiles with Caddy](https://github.com/caddyserver/caddy/pull/4978)
- [Performance on the Go wiki](https://github.com/golang/go/wiki/Performance)
- [The `net/http/pprof` package](https://pkg.go.dev/net/http/pprof)
