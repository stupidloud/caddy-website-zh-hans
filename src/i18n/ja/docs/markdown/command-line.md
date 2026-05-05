---
title: "Command Line"
---

<a id="command-line"></a>
# Command Line

Caddy には標準的な unix-like command line interface があります。基本的な使い方は次のとおりです。

```
caddy <command> [<args...>]
```

`<carets>` は、あなたの入力で置き換えられるパラメーターを示します。

`[brackets]` は任意のパラメーターを示します。`(brackets)` は必須のパラメーターを示します。

省略記号 `...` は継続、つまり 1 つ以上のパラメーターを示します。

`--flags` には `-f` のような 1 文字の shortcut がある場合があります。

**Quick start: `caddy`, `caddy help`, または `man caddy`（インストール済みの場合）**

---

- **[caddy adapt](#caddy-adapt)**
  config document を native JSON に変換します

- **[caddy build-info](#caddy-build-info)**
  build information を出力します

- **[caddy completion](#caddy-completion)**
  shell completion script を生成します

- **[caddy environ](#caddy-environ)**
  environment を出力します

- **[caddy file-server](#caddy-file-server)**
  シンプルですが本番利用に対応した file server です

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  file server が default file browser template を出力するための補助コマンドです

- **[caddy fmt](#caddy-fmt)**
  Caddyfile を整形します

- **[caddy hash-password](#caddy-hash-password)**
  password を hash し、base64 を出力します

- **[caddy help](#caddy-help)**
  caddy commands の help を表示します

- **[caddy list-modules](#caddy-list-modules)**
  インストール済みの Caddy modules を一覧表示します

- **[caddy manpage](#caddy-manpage)**
  manpages を生成します

- **[caddy reload](#caddy-reload)**
  実行中の Caddy process の config を変更します

- **[caddy respond](#caddy-respond)**
  開発とテスト向けの、手早く使える hard-coded HTTP server です

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  シンプルですが本番利用に対応した HTTP(S) reverse proxy です

- **[caddy run](#caddy-run)**
  Caddy process を foreground で起動します

- **[caddy start](#caddy-start)**
  Caddy process を background で起動します

- **[caddy stop](#caddy-stop)**
  実行中の Caddy process を停止します

- **[caddy storage export](#caddy-storage)**
  設定された storage の内容を tarball に export します

- **[caddy storage import](#caddy-storage)**
  以前 export した tarball を設定された storage に import します

- **[caddy trust](#caddy-trust)**
  certificate を local trust store(s) にインストールします

- **[caddy untrust](#caddy-untrust)**
  certificate を local trust store(s) から信頼解除します

- **[caddy upgrade](#caddy-upgrade)**
  Caddy を latest release にアップグレードします

- **[caddy add-package](#caddy-add-package)**
  追加 plugins を加えたうえで、Caddy を latest release にアップグレードします

- **[caddy remove-package](#caddy-remove-package)**
  一部 plugins を削除したうえで、Caddy を latest release にアップグレードします

- **[caddy validate](#caddy-validate)**
  config file が有効かをテストします

- **[caddy version](#caddy-version)**
  version を出力します

- **[Signals](#signals)**
  Caddy が signals をどう扱うか

- **[Exit codes](#exit-codes)**
  Caddy process の終了時に返される code

<a id="subcommands"></a>
## Subcommands


### `caddy adapt`

<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

configuration を Caddy の native JSON config structure に変換し、出力を stdout に、warnings を stderr に書き出して終了します。

`--config` は config file への path です。省略した場合、現在のディレクトリに `Caddyfile` が存在すればそれを想定します。存在しなければ、この flag は必須です。通常の file の代わりに stdin を使いたい場合は、path として - を使います。

`--adapter` は使用する config adapter を指定します。デフォルトは `caddyfile` です。

`--pretty` は、人が読みやすいように indentation 付きで出力を整形します。

`--validate` は、変換後の configuration を読み込み、provision して有効性を確認します（ただし、実際に config の実行を開始することはありません）。

正常に adapt できた config でも validation に失敗する可能性がある点に注意してください。たとえば、次の Caddyfile を使います。

```caddy
localhost

tls cert_notexist.pem key_notexist.pem
```

adapt してみます。

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

これはエラーなく成功します。次に試します。

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_notexist.pem: no such file or directory
</code></pre>

その Caddyfile はエラーなく JSON に adapt できますが、実際の certificate や key file が存在しないため、provisioning phase でそのエラーが発生し validation は失敗します。したがって、validation は adaptation より強いエラーチェックです。

#### Example

手で読みやすく調整もしやすい JSON へ Caddyfile を adapt するには:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile --pretty</code></pre>



### `caddy build-info`

<pre><code class="cmd bash">caddy build-info</code></pre>

build について Go が提供する情報（main module path、package versions、module replacements）を出力します。




### `caddy completion`

<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

shell completion scripts を生成します。これにより、`caddy` commands を入力するときに tab-complete や auto-complete（または shell に応じた類似機能）を使えるようになります。

この script を特定の shell にインストールする手順を確認するには、`caddy help completion` または `caddy completion -h` を実行してください。



### `caddy environ`

<pre><code class="cmd bash">caddy environ</code></pre>

caddy から見える environment を出力して終了します。systemd のような init systems や process manager units をデバッグするときに役立ちます。




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

シンプルですが本番利用に対応した static file server を起動します。

`--root` は root file path を指定します。デフォルトは現在の working directory です。

`--listen` は listener address を受け付けます。デフォルトは `:80` ですが、`--domain` が使われた場合は `:443` がデフォルトになります。

`--domain` はその hostname 経由でのみ files を提供し、Caddy はそれを HTTPS で提供しようとします。public domain name の場合は、先に public DNS が正しく設定されていることを確認してください。デフォルト port は 443 に変わります。

`--browse` は、index file のない directory がリクエストされた場合に directory listings を有効にします。

`--reveal-symlinks` は、`--browse` が有効なとき、directory listings に symbolic links の target を表示します。

`--templates` は template rendering を有効にします。

`--access-log` は request/access log を有効にします。

`--debug` は verbose logging を有効にします。

`--file-limit` は directory listings に表示する files の最大数を設定します。デフォルトは `10000` です。files の数がこの上限を超える場合、最初の N files だけが表示されます。N は指定した上限です。

`--no-compress` は compression を無効にします。デフォルトでは Zstandard と Gzip compression が有効です。

`--precompressed` は、precompressed sidecar files を探す encoding formats を指定します。複数 formats に対して繰り返し指定できます。詳細は [file_server directive](/docs/caddyfile/directives/file_server#precompressed) を参照してください。

この command は admin API を無効にするため、ローカル開発マシン上で複数 instances を実行しやすくなります。


#### `caddy file-server export-template`

<pre><code class="cmd bash">caddy file-server export-template</code></pre>

default file browsing template を stdout に export します

### `caddy fmt`

<pre><code class="cmd bash">caddy fmt [&lt;path&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

Caddyfile を format または prettify して終了します。`--overwrite` が使われない限り、結果は stdout に出力され、差分がある場合は exit code `1` で終了します。

`<path>` は Caddyfile への path を指定します。`-` の場合、input は stdin から読み込まれます。省略した場合、現在のディレクトリにある Caddyfile という名前の file が想定されます。

`--overwrite` は、結果を terminal に出力する代わりに input file へ書き込みます。input が regular file でない場合、この flag は効果がありません。

`--diff` は、output を input と比較し、異なる行に `-` と `+` の prefix を付けます。変更されていない行には alignment のため 2 つの spaces が prefix される点に注意してください。また、これは有効な patch format ではなく、視覚的なツールとして意図されています。


### `caddy hash-password`

<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;password&gt;]
	[-a, --algorithm &lt;name&gt;]</code></pre>
	[--bcrypt-cost &lt;cost&gt;]</code></pre>

plaintext password を hash する便利な方法です。結果の hash は、Caddy config で直接使える format として stdout に書き出されます。

`--plaintext`
    hash する password です。省略した場合、stdin から読み込まれます。
    Caddy が controlling TTY に接続されている場合、input は echo されません。

`--algorithm`
    hashing algorithm を選択します。有効な options:
      * `argon2id`（現代的な security では推奨）
      * `bcrypt`  （legacy、より遅い、cost を設定可能、default cost は `14`）

bcrypt-specific parameters:

`--bcrypt-cost`
    bcrypt hashing difficulty を設定します。値を大きくすると hash computation が遅くなり CPU-intensive になるため、security が上がります。
    有効範囲 [bcrypt.MinCost, bcrypt.MaxCost] 内でなければなりません。
    省略された場合、または無効な場合は default cost が使われます。

Argon2id-specific parameters:

`--argon2id-time`
    実行する iterations の数です。増やすと hashing が遅くなり、brute-force attacks への耐性が上がります。

`--argon2id-memory`
    hashing 中に使う memory の量です。
    値を大きくすると GPU/ASIC attacks への耐性が上がります。

`--argon2id-threads`
    使用する CPU threads の数です。multi-core systems では増やすと hashing が速くなります。

`--argon2id-keylen`
    resulting hash の byte 長です。長い keys は security を高めますが、storage size もわずかに増えます。


### `caddy help`

<pre><code class="cmd bash">caddy help [&lt;command&gt;]</code></pre>

CLI help text を出力します。必要に応じて特定の subcommand の help を出力し、その後終了します。



### `caddy list-modules`

<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

インストールされている Caddy modules を出力します。必要に応じて、関連する Go modules からの package や version 情報も含めて出力し、その後終了します。

script された状況によっては、standard modules もすべて出力するのは冗長な場合があります。そのため、`--skip-standard` を使ってそれらを省略できます。

`--json` は module information を JSON format で出力します。programmatic processing に便利です。

NOTE: [Go のバグ](https://github.com/golang/go/issues/29228) により、version information は Caddy が main module ではなく dependency としてビルドされた場合にのみ利用できます。これを簡単にするには [xcaddy](/docs/build#xcaddy) を使ってください。



### `caddy manpage`

<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;path&gt;)</code></pre>

Caddy commands の manual/documentation pages を生成し、指定された path の directory に書き込みます。この command の output は `man` command で読めます。

`--directory`（必須）は man pages を書き込む directory への path です。存在しない場合は作成されます。

生成後、manual pages は通常インストールする必要があります。この手順は platform によって異なりますが、一般的な Linux systems では、おおよそ次のようになります。

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

その後、`man caddy`（または subcommands なら `man caddy-*`）を実行して、terminal で documentation を読めます。

Manual pages は、私たちの website 上のものとは別の documentation です。website には、より包括的で頻繁に更新される documentation があります。




### `caddy reload`

<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

実行中の Caddy instance に新しい configuration を渡します。これは [/load endpoint](/docs/api#post-load) に document を POST するのと同じ効果がありますが、この command は config files を中心にした単純な workflow で便利です。`stop`、`start`、`run` commands と比べ、この単一 command が、実行中の configuration を変更/reload する正しい semantic な方法です。

この command は API を使うため、admin endpoint は無効化されていてはいけません。

`--config` は適用する config file です。`-` の場合、config は stdin から読み込まれます。指定しない場合、現在の working directory にある `Caddyfile` という file を試し、存在すれば `caddyfile` config adapter を使って adapt します。存在しない場合、読み込む config file がないためエラーになります。

`--adapter` は、使用する config adapter があれば指定します。`--config` filename が `Caddyfile` で始まる、または `.caddyfile` で終わる場合は `caddyfile` adapter が想定されるため、この flag は不要です。それ以外で、提供された config file が Caddy の native JSON format でない場合、この flag は必須です。

`--address` は、admin endpoint が default address で listen しておらず、提供された config file 内の address とも異なる場合に使う必要があります。

`--force` は、指定した config が Caddy がすでに実行しているものと同じでも reload を発生させます。Caddy に modules を reprovision させるために便利な場合があります。たとえば、手動で読み込まれた TLS certificates の reload などです。




### `caddy respond`

<pre><code class="cmd bash">caddy respond
	[-s, --status &lt;code&gt;]
	[-H, --header "&lt;Field&gt;: &lt;value&gt;"]
	[-b, --body &lt;content&gt;]
	[-l, --listen &lt;addr&gt;]
	[-v, --debug]
	[--access-log]
	[&lt;status|body&gt;]</code></pre>


開発、staging、一部の本番 use cases に役立つ、1 つ以上のシンプルな hard-coded HTTP servers を起動します。HTTP clients、scripts、load balancers の検証やデバッグに便利です。

`--status` は返す HTTP status code です。

`--header` は HTTP header を追加します。`Field: value` format が期待されます。この flag は複数回使えます。

`--body` は response body を指定します。代わりに、body を stdin から pipe できます。

`--listen` は listener address です。Caddy が認識する任意の [network address](/docs/conventions#network-addresses) を指定でき、複数 servers を開始するための port range も含められます。

`--debug` は verbose debug logging を有効にします。

`--access-log` は access/request logging を有効にします。

options が指定されていない場合、この command は利用可能なランダム port で listen し、空の 200 response で HTTP requests に応答します。listen address は `--listen` flag でカスタマイズでき、常に stdout に出力されます。listen address に port range が含まれる場合、複数 servers が開始されます。

最後の unnamed argument が与えられた場合、それが 3 桁の数字なら status code（`--status` flag と同じ）として扱われます。それ以外の場合は response body（`--body` flag と同じ）として使われます。`--status` と `--body` flags は常にこの argument を上書きします。

body は 3 つの方法で指定できます。flag、command の最後の（unnamed）argument、または flag と argument が未設定の場合に stdin から pipe する方法です。body では限定的な [template evaluation](https://pkg.go.dev/text/template) がサポートされ、次の variables を使えます。

Variable | Description
---------|-------------
`.N`       | Server number
`.Port`    | Listener port
`.Address` | Listener address


#### Examples

ランダム port で空の 200 response:
<pre><code class="cmd bash">caddy respond</code></pre>

body 付き HTTP response:
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

複数 servers と templates:
<pre><code class="cmd"><b>$ caddy respond --listen :2000-2004 "{{printf "I'm server {{.N}} on port {{.Port}}"}}"</b>

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

<b>$ curl 127.0.0.1:2002</b>
I'm server 2 on port 2002</code></pre>

maintenance page を pipe する:
<pre><code class="cmd bash">cat maintenance.html | caddy respond \
	--listen :80 \
	--status 503 \
	--header "Content-Type: text/html"</code></pre>




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

シンプルですが本番利用に対応した reverse proxy です。quick deployments、demos、development に便利です。

HTTP(S) traffic を `--from` address から `--to` address へ単純に中継します。`--to` addresses は flag を繰り返すことで複数指定できます。少なくとも 1 つの `--to` address が必須です。`--to` address は、複数 upstreams に展開する shortcut として port range を含めることができます。

addresses で別途指定されていない限り、hostname が与えられた場合の `--from` address は HTTPS と想定され、`--to` address は HTTP と想定されます。

`--from` address に host または IP がある場合、Caddy は（HTTP scheme または port で上書きされていない限り）certificate を使って proxy を HTTPS で提供しようとします。

HTTPS を提供する場合:
  - `--disable-redirects` は HTTP port への bind を避けるために使えます。

  - `--internal-certs` は public certificate の発行を試みる代わりに、internal CA を使って certs の発行を強制するために使えます。

proxying の場合:
  - `--header-up` は upstream へ送る request header を設定するために使えます。
  
  - `--header-down` は client へ返す response header を設定するために使えます。
  
  - `--change-host-header` は request 上の Host header を、incoming Host header のデフォルトではなく upstream の address に設定します。

    これは `--header-up "Host: {http.reverse_proxy.upstream.hostport}"` の shortcut です
  
  - `--insecure` は upstream との TLS verification を無効にします。WARNING: THIS DISABLES SECURITY BY NOT VERIFYING THE UPSTREAM'S CERTIFICATE.
  
  - `--debug` は verbose logging を有効にします。

この command は admin API を無効にするため、ローカル開発マシン上で複数 instances を実行しやすくなります。



### `caddy run`

<pre><code class="cmd bash">caddy run
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--pidfile &lt;file&gt;]
	[-e, --environ]
	[--envfile &lt;file&gt;]
	[-r, --resume]
	[-w, --watch]</code></pre>

Caddy を実行し、無期限に block します。つまり "daemon" mode です。

`--config` は、すぐに読み込んで使用する initial config file を指定します。`-` の場合、config は stdin から読み込まれます。config が指定されない場合、Caddy は blank configuration で実行され、[admin API endpoints](/docs/api) の default settings を使います。これを使って新しい configuration を渡せます。特別なケースとして、現在の working directory に "Caddyfile" という file があり、`caddyfile` config adapter が組み込まれている（デフォルト）場合、command line flags がなくても、その file が読み込まれて Caddy の設定に使われます。

`--adapter` は、initial config を読み込むときに使う config adapter の名前です。`--config` filename が `Caddyfile` で始まる、または `.caddyfile` で終わる場合は `caddyfile` adapter が想定されるため、この flag は不要です。それ以外で、提供された config file が Caddy の native JSON format でない場合、この flag は必須です。warnings は log に出力されますが、errors のない adaptation は、warnings があってもすぐに使用される点に注意してください。adaptation の結果を先に確認したい場合は、[`caddy adapt`](#caddy-adapt) subcommand を使ってください。

`--pidfile` は PID を指定した file に書き込みます。

`--environ` は起動前に environment を出力します。これは `caddy environ` command と同じですが、出力後に終了しません。

`--envfile` は、指定された file から `KEY=VALUE` format の environment variables を読み込みます。`#` で始まる comments がサポートされます。keys には `export` を prefix できます。values は double-quoted にできます（内部の double-quotes は escape できます）。multi-line values もサポートされます。

`--resume` は、最後に読み込まれて autosaved された configuration を使い、`--config` flag（存在する場合）を上書きします。この flag を使うと、machine reboot や process restart をまたいだ config durability が保証されます。[API](/docs/api)-centric deployments で最も役立ちます。

`--watch` は config file を監視し、変更後に自動で reload します。⚠️ この機能は local development environments でのみ使うことを意図しています。

<aside class="advice">

本番環境で設定を変更するために server を停止しないでください。downtime が発生します。（これは明らかなはずですが、驚くほど多くの苦情が寄せられます。）代わりに [`caddy reload`](#caddy-reload) command を使うか、process に `SIGUSR1` signal を送ってください。これは現在読み込まれている config で `caddy reload` と同じ効果があります。

</aside>



### `caddy start`

<pre><code class="cmd bash">caddy start
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]
	[--pidfile &lt;file&gt;]
	[-w, --watch]</code></code></pre>

[`caddy run`](#caddy-run) と同じですが、background で実行します。この command は background process が正常に実行される（または実行に失敗する）までだけ block し、その後 return します。

注: `--config` flag は、stdin から config を読み込むための `-` をサポートしません。

この command は system services や Windows での使用は推奨されません。Windows では child process が terminal に接続されたままになるため、window を閉じると Caddy が強制停止されますが、これは分かりにくい挙動です。代わりに Caddy を [service として](/docs/running) 実行することを検討してください。

起動後は、[`caddy stop`](#caddy-stop) または [`POST /stop`](/docs/api#post-stop) API endpoint を使って background process を終了できます。



### `caddy stop`

<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

<aside class="tip">

server の停止（および再起動）は config changes とは直交しています。**downtime を望むのでない限り、本番環境で configuration を変更するために stop command を使わないでください。** 代わりに [`caddy reload`](#caddy-reload) command を使ってください。

</aside>


実行中の Caddy process（stop command 自身の process を除く）を graceful に停止し、終了させます。これは graceful shutdown を行うために admin API の [`POST /stop`](/docs/api#post-stop) endpoint を使います。

running instance の admin API が default listen address を使っていない場合、この request の address は `--address` flag、または指定された `--config` からカスタマイズできます。

process を終了せずに現在の configuration だけを停止したい場合は、blank config で [`caddy reload`](#caddy-reload) を使うか、[`DELETE /config/`](/docs/api#delete-configpath) endpoint を使ってください。


### `caddy storage`

<i>⚠️ Experimental</i>

Caddy の configured data storage の内容を export および import できます。

これは、ある [storage module](/docs/json/storage/) から別のものへ移行する必要があるときに便利です。古い storage から export し、config を更新し、新しい storage に import します。

次の command は、古い config と新しい config を使い、export command の output を import command に pipe することで、異なる modules 間で storage を一度にコピーできます。

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">

[filesystem storage](/docs/conventions#data-directory) を使う場合、export command は Caddy が通常実行されるのと同じ user として実行する必要があります。そうしないと、間違った storage location が使われる可能性があります。

たとえば、Caddy を [systemd service](/docs/running#linux-service) として実行している場合、`caddy` user として実行されます。そのため、export または import commands もその user として実行するべきです。通常これは `sudo -u caddy <command>` で行えます。

</aside>


#### `caddy storage export`

<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;path&gt;
	[-o, --output &lt;path&gt;]</code></pre>

`--config` は読み込む config file です。正しい storage module に接続するため、これは必須です。

`--output` は tarball を書き込む filename です。`-` の場合、output は stdout に書き込まれます。



#### `caddy storage import`

<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;path&gt;
	-i, --input &lt;path&gt;</code></pre>

`--config` は読み込む config file です。正しい storage module に接続するため、これは必須です。

`--input` は読み込む tarball の filename です。`-` の場合、input は stdin から読み込まれます。


### `caddy trust`

<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Caddy の [PKI app](/docs/json/apps/pki/) が管理する CA の root certificate を local trust stores にインストールします。

Caddy は root certificates が初めて生成されるとき、local trust stores へ自動的にインストールしようとしますが、trust store へ書き込む適切な権限がない場合は失敗することがあります。server process が権限のない user として実行される場合（systemd 経由など）、証明書を使う前に事前インストールするため、この command が必要です。unix systems では、この command を `sudo` 付きで実行する必要があるかもしれません。

デフォルトでは、この command は Caddy の default CA（つまり "local"）の root certificate をインストールします。`--ca` flag で別の CA の ID を指定できます。

この command は、[`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates) endpoint を使って root certificate を取得するため、Caddy の [admin API](/docs/api) に接続しようとします。running instance の admin API が default listen address を使っていない場合は、`--address` を明示的に指定するか、`--config` flag を使って config から admin address を読み込めます。

admin API が他の machines からアクセスできるようにされている場合、この command と `caddy` binary を使って network 内の他の machines に certificates をインストールすることもできます。ただし、この場合は admin API を untrusted clients に公開しないよう注意してください。


### `caddy untrust`

<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;path&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

root certificate を local trust store(s) から信頼解除します。

この command は trust をアンインストールしますが、root certificate を trust stores から完全に削除するとは限りません。そのため、新しい certificates を何度も trust/untrust すると、trust databases が増えていくことがあります。

この command は、Caddy の configured storage から certificate files を削除または変更しません。

この command は次の 2 つの方法のいずれかで使えます。
- `--cert` flag で、信頼解除する root certificate への直接 path を指定する。
- [admin API](/docs/api) から [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates) endpoint を使って root certificate を取得する。flags が指定されていない場合、これが default behaviour です。

admin API が使われる場合、CA ID のデフォルトは "local" です。`--ca` flag で別の CA の ID を指定できます。running instance の admin API が default listen address を使っていない場合は、`--address` を明示的に指定するか、`--config` flag を使って config から admin address を読み込めます。


### `caddy upgrade`

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

現在の Caddy binary を、インストール済みの同じ modules（Caddy website に登録されているすべての third-party plugins を含む）を持つ [download page](/download) の latest version に置き換えます。

Upgrades は実行中の servers を中断しません。現在、この command は disk 上の binary を置き換えるだけです。将来、良い方法が見つかれば変わる可能性があります。

upgrade process は fault tolerant です。現在の binary は先に backup され（現在のものの隣にコピーされ）、何か問題があれば自動的に復元されます。upgrade process 完了後も backup を保持したい場合は、`--keep-backup` option を使えます。

この command は、あなたの user が executable file へ書き込む権限を持っていない場合、elevated privileges を必要とすることがあります。



### `caddy add-package`

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy add-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

`caddy upgrade` と同様に、現在の Caddy binary を、同じ modules に加えて arguments として listed された packages を含む latest version に置き換えます。インストールできる packages の一覧は [download page](/download) で確認できます。各 argument は full package name である必要があります。

例:

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>



### `caddy remove-package`

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy remove-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

`caddy upgrade` と同様に、現在の Caddy binary を、同じ modules を持つ latest version に置き換えますが、arguments として listed された packages が現在の binary に存在していれば、それらを含めません。現在の binary に含まれる non-standard modules の package names の一覧を見るには、`caddy list-modules --packages` を実行してください。



### `caddy validate`

<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]</code></pre>

configuration file を validate して終了します。この command は config を deserialize し、config を開始するかのようにすべての modules を読み込んで provision しますが、config は実際には開始されません。これにより、loading または provisioning phases 中に発生する configuration のエラーを明らかにできます。単に config を JSON として serialize するだけよりも強いエラーチェックです。

`--config` は validate する config file です。`-` の場合、config は stdin から読み込まれます。デフォルトは、存在する場合、現在の directory の `Caddyfile` です。

`--adapter` は使用する config adapter の名前です。`--config` filename が `Caddyfile` で始まる、または `.caddyfile` で終わる場合は `caddyfile` adapter が想定されるため、この flag は不要です。それ以外で、提供された config file が Caddy の native JSON format でない場合、この flag は必須です。

`--envfile` は、指定された file から `KEY=VALUE` format の environment variables を読み込みます。`#` で始まる comments がサポートされます。keys には `export` を prefix できます。values は double-quoted にできます（内部の double-quotes は escape できます）。multi-line values もサポートされます。



### `caddy version`
<pre><code class="cmd bash">caddy version</code></pre>

version を出力して終了します。



<a id="signals"></a>
## Signals

Caddy は特定の signals を捕捉し、その他を無視します。Signals は特定の process behavior を開始できます。

Signal | Behavior
-------|----------
`SIGINT` | Graceful exit。signal を再度送ると即座に強制終了します。
`SIGQUIT` | Caddy を即座に終了しますが、重要なため storage 内の locks は cleanup します。
`SIGTERM` | Graceful exit。
`SIGUSR1` | config file を reload します。ただし、`caddy run`（`--resume` なし）で起動され、[the API](/docs/api)（[`caddy reload`]#caddy-reload) を含む）経由で config に変更が加えられていない場合に限ります。
`SIGUSR2` | 無視されます。
`SIGHUP` | 無視されます。

Graceful exit では、新しい connections は受け付けられなくなり、既存の connections は socket が閉じられる前に drain されます。grace period が適用される場合があります（設定可能です）。grace period が過ぎると、connections は強制終了されます。storage 内の locks や、個々の modules が解放する必要のあるその他 resources は、graceful shutdown 中に cleanup されます。

config reload の signal（`SIGUSR1`）を受け取ると、forced config reload のように動作します（つまり、config text が変わっていなくても reload します）。これにより、TLS certificates などの dependent files が disk から reload される場合があります。

Signal-based config reloads は、Caddy が config file 付きの `caddy run` で起動された場合にのみ有効です。Caddy が `--resume` で起動された場合（API workflow を意味するため）、admin API 経由で config change が受信された場合、または `caddy reload` が最初に起動したときと *異なる* filename や config adapter で実行された場合、これは無効になります（signals は無視され、log warning が出ます）。これは reload の方法同士の conflict を避けるためです。



<a id="exit-codes"></a>
## Exit codes

Caddy は process が終了するときに code を返します。

Code | Meaning
-----|---------
`0` | Normal exit。
`1` | Failed startup。**process を自動的に再起動しないでください。変更が加えられない限り、再び error になる可能性が高いです。**
`2` | Forced quit。Caddy は resources を cleanup せずに強制終了されました。
`3` | Failed quit。Caddy は cleanup 中にいくつかの errors を出して終了しました。

bash では、最後の command の exit code を `echo $?` で取得できます。
