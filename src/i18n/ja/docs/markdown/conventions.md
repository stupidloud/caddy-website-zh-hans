---
title: 規約
---

<a id="conventions"></a>
# 規約

Caddy エコシステムでは、プラットフォーム全体で一貫性があり直感的に使えるよう、いくつかの規約に従っています。


- [ネットワークアドレス](#network-addresses)
- [Placeholder](#placeholders)
- [ファイルの場所](#file-locations)
  - [データディレクトリ](#data-directory)
  - [設定ディレクトリ](#configuration-directory)
- [Duration](#durations)



<a id="network-addresses"></a>
## ネットワークアドレス

dial または bind するネットワークアドレスを指定するとき、Caddy は次の形式の文字列を受け付けます。

```
network/address
```

network 部分は省略可能で、デフォルトは `tcp` です。[Go の `net.Dial` 関数](https://pkg.go.dev/net#Dial)が認識する任意の値を指定できます。network を指定する場合は、network 部分と address 部分を単一のスラッシュ `/` で区切る必要があります。

network には次のいずれかを指定できます。末尾に `4` または `6` が付くものは、それぞれ IPv4 専用、IPv6 専用です。

- TCP: `tcp`, `tcp4`, `tcp6`
- UDP: `udp`, `udp4`, `udp6`
- IP: `ip`, `ip4`, `ip6`
- Unix: `unix`, `unixgram`, `unixpacket`

address 部分は、次のいずれかの形式にできます。

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/path/to/unix/socket`
- `/path/to/unix/socket|0200`

host には、任意の hostname、解決可能な domain name、または IP address を指定できます。

IPv6 address の場合、address は角括弧 `[]` で囲む必要があります。zone identifier（`%` で始まる）は省略可能です（link-local address でよく使われます）。

port は単一の値（`:8080`）または範囲（`:8080-8085`、両端を含む）にできます。port 範囲は個別の address に展開されます。すべての config field が port 範囲を受け付けるわけではありません。特殊な port `:0` は、利用可能な任意の port を意味します。

unix socket path は、`unix*` network type を使う場合にのみ有効です。network と address を区切るスラッシュは、path の一部とは見なされません。

unix socket を bind address として使う場合、path の後に pipe `|` で区切って file permission mode を任意で指定できます。デフォルトは `0200`（octal）、つまり `u=w,g=,o=`（symbolic）です。先頭の `0` は省略できます。

有効な例:

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//path/to/socket
unix//path/to/socket|0200
```

<aside class="tip">

Caddy のネットワークアドレスは URL ではありません。URL は [OSI model <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OSI_model#Layer_architecture) の低レイヤーと高レイヤーを結び付けますが、Caddy は特定のアプリケーションとは独立してネットワークアドレスを使うことが多いため、それらを結合すると問題になります。Caddy では、ネットワークアドレスは L3-L5 で dial または bind できるリソースを正確に指します。一方、URL は L3-L7 を組み合わせるため、含む範囲が広すぎます。ネットワークアドレスでは host+port と path は相互排他的である必要がありますが、URL ではそうではありません。ネットワークアドレスは port 範囲をサポートする場合がありますが、URL はサポートしません。

</aside>




<a id="placeholders"></a>
## Placeholder

Caddy の設定は *placeholder* の使用をサポートしています。placeholder を使うと、静的な設定に動的な値を簡単に注入できます。

<aside class="tip">

Placeholder は、他のソフトウェアにおける変数に近い考え方です。たとえば、[nginx には variables <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html) として `$uri` や `$document_root` がありますが、Caddy で対応するものは [`{http.request.uri}`](/docs/json/apps/http/#docs) や [`{http.vars.root}`](/docs/caddyfile/directives/root) です。

</aside>


Placeholder は両側を波括弧 `{ }` で囲み、内部に identifier を含めます。例: `{foo.bar}`。placeholder の開始波括弧は `\{like.this}` のように escape でき、置換を防げます。placeholder identifier は通常、module 間の衝突を避けるため dot で名前空間化されます。

利用できる placeholder は context に依存します。すべての placeholder が設定のすべての部分で使えるわけではありません。たとえば、[HTTP app が設定する placeholder](/docs/json/apps/http/#docs) は、HTTP リクエスト処理に関連する設定領域でのみ利用できます。リクエストが [`reverse_proxy` handler](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs) を通過すると、その handler は proxy 固有の placeholder をいくつか設定します。これらの placeholder は、proxy 中だけでなく、その後（`handle_response` 内）にも参照できます。たとえば、レスポンス header の設定やアクセスログの拡充に使えます。

次の placeholder は常に利用できます（global）。

Placeholder | Description
------------|-------------
`{env.*}` | 環境変数。例: `{env.HOME}`
`{file.*}` | ファイルからの内容。例: `{file./path/to/secret.txt}`
`{system.hostname}` | システムの local hostname
`{system.slash}` | システムの filepath separator
`{system.os}` | システムの OS
`{system.arch}` | システムの architecture
`{system.wd}` | 現在の working directory
`{time.now}` | Go Time struct としての現在時刻
`{time.now.http}` | [HTTP headers <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified) で使われる形式の現在時刻
`{time.now.unix}` | 秒単位の unix timestamp としての現在時刻
`{time.now.unix_ms}` | ミリ秒単位の unix timestamp としての現在時刻
`{time.now.common_log}` | Common Log Format の現在時刻
`{time.now.year}` | YYYY 形式の現在年

すべての config field が placeholder をサポートしているわけではありませんが、期待される場所の多くではサポートされています。placeholder のサポートは、それらの field に明示的に追加されている必要があります。plugin 作者は、自分の module に placeholder サポートを追加する方法を知るために、[この記事](/docs/extending-caddy/placeholders)を読めます。




<a id="file-locations"></a>
## ファイルの場所

このセクションでは、さまざまなファイルがどこにあるかを説明します。ここで説明する file path や directory path は、あくまでデフォルトです。一部は上書きできます。

<a id="your-config-files"></a>
### 設定ファイル

設定ファイルを置くための単一の慣例的な場所はありません。自分にとって最も自然な場所に置いてください。

<aside class="tip">

唯一の例外になり得るのは、現在の working directory にある `Caddyfile` という名前のファイルです。他の config file が指定されていない場合、caddy command は利便性のためにこのファイルを探します。

</aside>


デフォルト config file を同梱する distribution は、その config file がどこにあるかをドキュメント化すべきです。package/distro maintainers にとって明らかに見える場合でも同様です。ほとんどの Linux インストールでは、Caddyfile は `/etc/caddy/Caddyfile` にあります。


<a id="data-directory"></a>
### データディレクトリ

Caddy は TLS certificate やその他の重要な asset を data directory に保存します。この directory は [設定された storage module](/docs/json/storage/)（デフォルト: local file system）によって支えられます。

`XDG_DATA_HOME` 環境変数が設定されている場合は、`$XDG_DATA_HOME/caddy` です。

それ以外の場合、path は OS の慣例に従って platform ごとに異なります。

OS | Data directory path
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (または `/sdcard/caddy`)

その他すべての OS では Linux/BSD の directory path を使います。

**data directory を cache として扱ってはいけません。** その内容は**一時的なものでも、単なる性能目的のものでもありません**。Caddy は TLS certificate、private key、OCSP staple、その他必要な情報を data directory に保存します。影響を理解せずに削除すべきではありません。

この directory が永続的で、Caddy から書き込み可能であることは非常に重要です。


<a id="configuration-directory"></a>
### 設定ディレクトリ

ここは、Caddy が特定の設定をディスクへ保存する場所です。特に、最後に active だった設定を（デフォルトで）この folder に永続化し、後で [`caddy run --resume`](/docs/command-line#caddy-run) を使って簡単に再開できるようにします。

<aside class="tip">

configuration directory は、[あなたの config file](#your-config-files) を保存する必要がある場所ではありません。（ただし、保存しても構いません。）

</aside>


`XDG_CONFIG_HOME` 環境変数が設定されている場合は、`$XDG_CONFIG_HOME/caddy` です。

それ以外の場合、path は OS の慣例に従って platform ごとに異なります。


OS | Config directory path
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

その他すべての OS では Linux/BSD の directory path を使います。

この directory が永続的で、Caddy から書き込み可能であることは非常に重要です。


<a id="durations"></a>
## Duration

duration 文字列は、Caddy の設定全体でよく使われます。形式は [Go の `time.ParseDuration` 構文](https://golang.org/pkg/time/#ParseDuration) と同じですが、day を表す `d` も使用できます（簡単のため、1 day = 24 hours と仮定します）。有効な単位は次のとおりです。

- `ns` (nanosecond)
- `us`/`µs` (microsecond)
- `ms` (millisecond)
- `s` (second)
- `m` (minute)
- `h` (hour)
- `d` (day)

例:

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

[JSON config](/docs/json/) では、duration value を nanosecond を表す integer として指定することもできます。
