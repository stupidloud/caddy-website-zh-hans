---
title: log (Caddyfile directive)
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.textContent.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# log

HTTP request logging（access log とも呼ばれます）を有効化し、設定します。

<aside class="tip">

Caddy の runtime log を設定するには、代わりに [`log` global option](/docs/caddyfile/options#log) を参照してください。

</aside>


`log` ディレクティブは、`hostnames` subdirective で上書きしない限り、それが書かれている site block の hostnames に適用されます。

設定すると、デフォルトでは site へのすべてのリクエストが log に記録されます。一部のリクエストだけを条件付きで logging から除外するには、[`log_skip` ディレクティブ](log_skip)を使います。

log entry にカスタムフィールドを追加するには、[`log_append` ディレクティブ](log_append)を使います。


- [構文](#syntax)
- [出力モジュール](#output-modules)
  - [stderr](#stderr)
  - [stdout](#stdout)
  - [discard](#discard)
  - [file](#file)
  - [net](#net)
- [形式モジュール](#format-modules)
  - [console](#console)
  - [json](#json)
  - [filter](#filter)
    - [delete](#delete)
	- [rename](#rename)
	- [replace](#replace)
	- [ip_mask](#ip-mask)
	- [query](#query)
	- [cookie](#cookie)
	- [regexp](#regexp)
	- [hash](#hash)
  - [append](#append)
- [例](#examples)

デフォルトでは、潜在的に機密性の高い情報を含む header（`Cookie`、`Set-Cookie`、`Authorization`、`Proxy-Authorization`）は access log では `REDACTED` として記録されます。この動作は [`log_credentials`](/docs/caddyfile/options#log-credentials) global server option で無効化できます。


<a id="syntax"></a>
## 構文

```caddy-d
log [<logger_name>] {
	hostnames <hostnames...>
	no_hostname
	output <writer_module> ...
	format <encoder_module> ...
	level  <level>
	sampling {
		interval   <duration>
		first      <number>
		thereafter <number>
	}
}
```

- **logger_name** <span id="logger_name"/> は、この site の logger name を任意で上書きします。

  デフォルトでは、Caddyfile 内の site の順序に応じて `log0`、`log1` のような logger name が自動生成されます。これは、global options で定義された別の logger から、この logger の output を確実に参照したい場合にだけ有用です。下の[例](#multiple-outputs)を参照してください。

- **hostnames** <span id="hostnames"/> は、この logger が適用される hostnames を任意で上書きします。

  デフォルトでは、logger はそれが書かれている site block の hostnames、つまり site addresses に適用されます。これは [wildcard site block](/docs/caddyfile/patterns#wildcard-certificates) 内で subdomain ごとに異なる logger を定義したい場合に便利です。下の[例](#wildcard-logs)を参照してください。

- **no_hostname** <span id="no_hostname"/> は、logger が site block のどの hostname にも関連付けられないようにします。デフォルトでは、logger は `log` ディレクティブが書かれている [site address](/docs/caddyfile/concepts#addresses) に関連付けられます。

  これは、[`log_name` ディレクティブ](/docs/caddyfile/directives/log_name)を使って、リクエストパスやメソッドなどの条件に基づいてリクエストを別々のファイルに記録したい場合に便利です。

- **output** <span id="output"/> は、log の書き込み先を設定します。下の [`output` modules](#output-modules) を参照してください。

  デフォルト: `stderr`。

- **format** <span id="format"/> は、log をどのように encode、または format するかを指定します。下の [`format` modules](#format-modules) を参照してください。

  デフォルト: `stderr` が terminal として検出された場合は `console`、それ以外は `json`。

- **level** <span id="level"/> は、記録する最小 entry level です。デフォルト: `INFO`。

  access log は現在、`INFO` と `ERROR` level の log だけを出力します。

- **sampling** <span id="sampling"/> は、log volume を減らすための log sampling を設定します。`sampling` を指定すると有効になり、下のデフォルト値が適用されます。省略すると sampling は無効です。

  - **interval** は sampling を行う [duration window](/docs/conventions#durations) です。デフォルト: `1s`（無効）。

  - **first** は、各 interval 内で同じ level と message について保持する log 数です。デフォルト: `100`。

  - **thereafter** は、最初に保持された log の後、各 interval でいくつ log をスキップするかです。デフォルト: `100`。

  たとえば `interval 1s`、`first 5`、`thereafter 10` の場合、各 10 秒 interval 内で最初の 5 件の log entry を保持し、その後はその秒の同じ level と message を持つ log entry の 10 件ごとに 1 件を通します。


<a id="output-modules"></a>
### 出力モジュール

**output** subdirective では、log の書き込み先をカスタマイズできます。

#### stderr

標準エラー（console、デフォルト）。

```caddy-d
output stderr
```

#### stdout

標準出力（console）。

```caddy-d
output stdout
```

#### discard

出力しません。

```caddy-d
output discard
```

#### file

ファイルです。デフォルトでは、log file はディスク容量の枯渇を防ぐため、サイズに基づいて rotation（"roll"）されます。

Log rolling は [timberjack <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/DeRuina/timberjack) によって提供されます。

<aside class="tip">

**log file options の reload について:** 指定された output file への設定変更を適用するには、server restart が必要です。
新しい log filename を追加しない限り、server reload 時には変更は適用されません。

</aside>

```caddy-d
output file <filename> {
	mode          <mode>
	roll_disabled
	roll_size     <size>
	roll_interval <duration>
	roll_minutes  <minutes...>
	roll_at	      <times...>
	roll_uncompressed
	roll_local_time
	roll_keep     <num>
	roll_keep_for <days>
	backup_time_format <format>
}
```

- **&lt;filename&gt;** は log file への path です。

  roll された場合、ファイルは `<name>-<timestamp>-<reason>.log` という template を使って rename されます。timestamp は [`backup_time_format`](#backup_time_format) option に従って format されます。reason は rotation を発生させた条件に応じて `size` または `time` です。ファイルが圧縮される場合は、filename に `.gz` が追加されます。

   たとえば filename が `access.log` の場合、サイズによって roll されたファイルは `access-2026-01-30T22-15-42.123-size.log`、時間によって roll されたファイルは `access-2025-01-30T00-00-00.000-time.log` のような名前になります。

- **mode** <span id="mode"/> は log file に使う Unix file mode/permissions です。mode は 1 から 4 桁の 8 進数で構成されます（Unix の [chmod <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Chmod) command が受け付ける数値形式と同じですが、すべて 0 の mode はデフォルト mode `600` と解釈されます）。

  例: `0600` は mode を `rw-,---,---`（log file の owner には read/write access、他の誰にも access なし）に設定します。`0640` は `rw-,r--,---`（file owner には read/write access、group には read access のみ）に設定します。`644` は `rw-,r--,r--` に設定し、log file owner には read/write access、group owner と other users には read access のみを提供します。

- **roll_disabled** <span id="roll_disabled"/> は log rolling を無効にします。これはディスク容量の枯渇につながる可能性があるため、log file を別の方法で管理している場合にのみ使ってください。

- **roll_size** <span id="roll_size"/> は log file を roll するサイズです。現在の実装は megabyte 単位の解像度をサポートしており、小数値は次の整数 megabyte に切り上げられます。たとえば `1.1MiB` は `2MiB` に切り上げられます。

  これは常に有効です。log への書き込みによってファイルが指定サイズを超えると、log は直ちに rotate されます。backup filename には reason として `size` が含まれます。

  デフォルト: `100MiB`

- **roll_interval** <span id="roll_interval"/> は log rotation 間の最大 duration です。値は、この duration が経過した後に log file を roll する [duration string](/docs/conventions#durations) です。

  有効にすると、最後の rotation からこの duration が経過した後、次に log へ書き込まれるタイミングでファイルが rotate されます。backup filename には reason として `time` が含まれます。

  `24h` に設定しても、必ずしも真夜中に roll されるわけではなく、最後の rotation から 24 時間後に roll されます。サイズによって rolling が発生した場合、次の rotation 時刻は前回の rotation からずれます。特定の時刻に roll したい場合は、代わりに `roll_at` または `roll_minutes` option を使えます。

  デフォルト: disabled

- **roll_minutes** <span id="roll_minutes"/> は、log file を roll する minute values（0-59）のリストです。たとえば `10 40` は、毎時 `xx:10` と `xx:40`、つまり 30 分ごとに log file を roll します。rotation は時計の分（second 0）に揃えられます。

  これを有効にすると、指定した minute values で log rotation を起動する goroutine timer が生成されます（つまり少量の background processing が導入されます）。これは `roll_interval` と `roll_size` に加えて動作します。backup filename には reason として `time` が含まれます。

  デフォルト: disabled

- **roll_at** <span id="roll_at"/> は、log file を roll する time values（24-hour format）のリストです。たとえば `00:00 12:00` は、毎日 midnight と noon の 2 回 log file を roll します。rotation は時計の分（second 0）に揃えられます。

  これを有効にすると、指定した時刻で log rotation を起動する goroutine timer が生成されます（つまり少量の background processing が導入されます）。これは `roll_interval` と `roll_size` に加えて動作します。backup filename には reason として `time` が含まれます。

  デフォルト: disabled

- **roll_uncompressed** <span id="roll_uncompressed"/> は gzip log compression を無効にします。

  デフォルト: `gzip` compression は有効です。

- **roll_local_time** <span id="roll_local_time"/> は、rolling で filename に local timestamp を使うよう設定します。
  デフォルト: UTC time を使います。

- **roll_keep** <span id="roll_keep"/> は、最も古いファイルを削除する前に保持する log file 数です。新しい log file が作成されたときにトリガーされます。

  デフォルト: `10`

- **roll_keep_for** <span id="roll_keep_for"/> は、roll されたファイルを保持する期間を [duration string](/docs/conventions#durations) で指定します。新しい log file が作成されたときにトリガーされます。
  現在の実装は day 単位の解像度をサポートしており、小数値は次の整数日に切り上げられます。たとえば `36h`（1.5 days）は `48h`（2 days）に切り上げられます。
  
  デフォルト: `2160h`（90 days）

- **backup_time_format** <span id="backup_time_format"/> は backup filename で使う time format です。有効な time layout string である必要があります。詳細は [Go documentation](https://pkg.go.dev/time#pkg-constants) を参照してください。

  デフォルト: `2006-01-02T15-04-05`


#### net

Network socket です。socket が停止すると、再接続を試みている間は log を stderr に dump します。

```caddy-d
output net <address> {
	dial_timeout <duration>
	soft_start
}
```

- **&lt;address&gt;** は log の書き込み先となる [address](/docs/conventions#network-addresses) です。

- **dial_timeout** <span id="dial_timeout"/> は log socket への接続成功を待つ時間です。socket が停止した場合、log emission は最大でこの時間だけ block される可能性があります。

- **soft_start** <span id="soft_start"/> は socket への接続エラーを無視し、remote log service が停止していても config をロードできるようにします。代わりに log は stderr へ出力されます。


<a id="format-modules"></a>
### 形式モジュール

**format** subdirective では、log をどのように encode（format）するかをカスタマイズできます。これは `log` block 内に記述します。

<aside class="tip">

**Common Log Format（CLF）について:** CLF は現代的な structured log とは相性がよくありません。access log を非推奨の Common Log Format へ変換するには、[`transform-encoder` plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder) を使ってください。

</aside>

各 encoder 固有の構文に加えて、ほとんどの encoder では次の共通プロパティを設定できます。

```caddy-d
format <encoder_module> {
	message_key     <key>
	level_key       <key>
	time_key        <key>
	name_key        <key>
	caller_key      <key>
	stacktrace_key  <key>
	line_ending     <char>
	time_format     <format>
	time_local
	duration_format <format>
	level_format    <format>
}
```

- **message_key** <span id="message_key"/> log entry の message field の key です。デフォルト: `msg`

- **level_key** <span id="level_key"/> log entry の level field の key です。デフォルト: `level`

- **time_key** <span id="time_key"/> log entry の time field の key です。デフォルト: `ts`
- **name_key** <span id="name_key"/> log entry の name field の key です。デフォルト: `name`

- **caller_key** <span id="caller_key"/> log entry の caller field の key です。

- **stacktrace_key** <span id="stacktrace_key"/> log entry の stacktrace field の key です。

- **line_ending** <span id="line_ending"/> 使用する line ending です。

- **time_format** <span id="time_format"/> timestamp の format です。
  デフォルト: format が `console` にデフォルト設定された場合は `wall_milli`、それ以外は `unix_seconds_float`。
  
  次のいずれかを指定できます。
  - `unix_seconds_float` Unix epoch からの秒数を floating-point number で表します。
  - `unix_milli_float` Unix epoch からのミリ秒数を floating-point number で表します。
  - `unix_nano` Unix epoch からのナノ秒数を integer number で表します。
  - `iso8601` 例: `2006-01-02T15:04:05.000Z0700`
  - `rfc3339` 例: `2006-01-02T15:04:05Z07:00`
  - `rfc3339_nano` 例: `2006-01-02T15:04:05.999999999Z07:00`
  - `wall` 例: `2006/01/02 15:04:05`
  - `wall_milli` 例: `2006/01/02 15:04:05.000`
  - `wall_nano` 例: `2006/01/02 15:04:05.000000000`
  - `common_log` 例: `02/Jan/2006:15:04:05 -0700`
  - または、互換性のある任意の time layout string。詳細は [Go documentation](https://pkg.go.dev/time#pkg-constants) を参照してください。
  
  format string の各部分は layout 用の特別な定数です。つまり、`2006` は年、`01` は月、`Jan` は文字列としての月、`02` は日を表します。format string には実際の現在日付の数字を使わないでください。

- **time_local** <span id="time_local"/> デフォルトの UTC time ではなく、local system time で log を記録します。

- **duration_format** <span id="duration_format"/> duration の format です。

  デフォルト: `seconds`。
  
  次のいずれかを指定できます。
  - `s`、`second`、`seconds` 経過秒数を floating-point number で表します。
  - `ms`、`milli`、`millis` 経過ミリ秒数を floating-point number で表します。
  - `ns`、`nano`、`nanos` 経過ナノ秒数を integer number で表します。
  - `string` Go 組み込みの string format を使います。例: `1m32.05s` または `6.31ms`。

- **level_format** <span id="level_format"/> level の format です。

  デフォルト: format が `console` にデフォルト設定された場合は `color`、それ以外は `lower`。
  
  次のいずれかを指定できます。
  - `lower` lowercase。
  - `upper` uppercase。
  - `color` uppercase、ANSI colors 付き。
  

#### console

console encoder は、一定の構造を保持しながら、人間が読みやすい形に log entry を format します。

```caddy-d
format console
```

#### json

各 log entry を JSON object として format します。

```caddy-d
format json
```


#### filter

field ごとの filtering を可能にします。

```caddy-d
format filter {
	fields {
		<field> <filter> ...
	}
	<field> <filter> ...
	wrap <encode_module> ...
}
```

nested field は、ネストの階層を `>` で表して参照できます。つまり `{"a":{"b":0}}` のような object では、内側の field を `a>b` として参照できます。

次の field は log の基本要素であり、基盤の logging library によって特別扱いで追加されるため filter できません: `ts`、`level`、`logger`、`msg`。

`wrap` の指定は任意です。省略した場合は、現在の output module が [`stderr`](#stderr) または [`stdout`](#stdout) で、かつ interactive terminal の場合は [`console`](#console) が選ばれ、それ以外の場合は [`json`](#json) が選ばれます。

ショートカットとして、`fields` block を省略し、filter を `filter` block 内に直接指定できます。


利用可能な filter は次のとおりです。

##### delete

field を encode から除外するよう mark します。

```caddy-d
<field> delete
```


##### rename

log field の key を rename します。

```caddy-d
<field> rename <key>
```


##### replace

encode 時に、field を指定された文字列で置き換えるよう mark します。

```caddy-d
<field> replace <replacement>
```


##### ip_mask

CIDR mask を使って field 内の IP address を mask します。つまり、左側から保持する IP の bit 数を指定します。field が文字列の array（例: HTTP headers）の場合、array 内の各値が mask されます。値には、comma separated string の IP address を指定できます。

IPv4 address と IPv6 address では総 bit 数が異なるため、別々の設定があります。

filter 対象として最も一般的な field は次のとおりです。
- `request>remote_ip` 直接接続している client
- `request>client_ip` [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) が設定されている場合に解析された "real client"
- `request>headers>X-Forwarded-For` reverse proxy の背後にある場合

```caddy-d
<field> ip_mask [<ipv4> [<ipv6>]] {
	ipv4 <cidr>
	ipv6 <cidr>
}
```


##### query

URL field の query 部分を操作するため、field に 1 つ以上の action を実行するよう mark します。filter 対象として最も一般的な field は `request>uri` です。

```caddy-d
<field> query {
	delete  <key>
	replace <key> <replacement>
	hash    <key>
}
```

利用可能な action は次のとおりです。

- **delete** は、指定された key を query から削除します。

- **replace** は、指定された query key の値を **replacement** に置き換えます。redaction placeholder を挿入するのに便利です。query key が URL に存在したことは分かりますが、値は隠されます。

- **hash** は、指定された query key の値を、その値の SHA-256 hash の先頭 4 bytes の lowercase hexadecimal に置き換えます。値が機密である場合に隠しながら、各リクエストで異なる値だったかどうかを確認できるので便利です。


##### cookie

`Cookie` HTTP header の値を操作するため、field に 1 つ以上の action を実行するよう mark します。filter 対象として最も一般的な field は `request>headers>Cookie` です。

```caddy-d
<field> cookie {
	delete  <name>
	replace <name> <replacement>
	hash    <name>
}
```

利用可能な action は次のとおりです。

- **delete** は、指定された名前の cookie を header から削除します。

- **replace** は、指定された cookie の値を **replacement** に置き換えます。redaction placeholder を挿入するのに便利です。cookie が header に存在したことは分かりますが、値は隠されます。

- **hash** は、指定された cookie の値を、その値の SHA-256 hash の先頭 4 bytes の lowercase hexadecimal に置き換えます。値が機密である場合に隠しながら、各リクエストで異なる値だったかどうかを確認できるので便利です。

同じ cookie name に対して複数の action が定義されている場合、最初の action だけが適用されます。


##### regexp

encode 時に、field へ regular expression replacement を適用するよう mark します。field が文字列の array（例: HTTP headers）の場合、array 内の各値に replacement が適用されます。

```caddy-d
<field> regexp <pattern> <replacement>
```

使用される regular expression language は Go に含まれる RE2 です。[RE2 syntax reference](https://github.com/google/re2/wiki/Syntax) と [Go regexp syntax overview](https://pkg.go.dev/regexp/syntax) を参照してください。

replacement string では、capture group を `${group}` で参照できます。`group` には、式内の capture group の名前または番号を指定します。capture group `0` は正規表現全体のマッチ、`1` は最初の capture group、`2` は 2 番目の capture group、という形です。


##### hash

encode 時に、field をその値の SHA-256 hash の先頭 4 bytes（8 hex characters）で置き換えるよう mark します。field が文字列 array（例: HTTP headers）の場合、array 内の各値が hash されます。

値が機密である場合に隠しながら、各リクエストで異なる値だったかどうかを確認できるので便利です。

```caddy-d
<field> hash
```

#### append

すべての log entry に field を追加します。

```caddy-d
format append {
	fields {
		<field> <value>
	}
	<field> <value>
	wrap <encode_module> ...
}
```

これは、log entry を生成している Caddy instance に関する情報を追加する用途に最も便利です。環境変数経由で追加することもできます。field value には global placeholder（例: `{env.*}`）を使えますが、log は HTTP request context の外側で書き込まれるため、per-request placeholder は使え*ません*。

`wrap` の指定は任意です。省略した場合は、現在の output module が [`stderr`](#stderr) または [`stdout`](#stdout) で、かつ interactive terminal の場合は [`console`](#console) が選ばれ、それ以外の場合は [`json`](#json) が選ばれます。

`fields` block は省略でき、field を `append` block 内に直接指定できます。



<a id="examples"></a>
## 例

デフォルト logger への access logging を有効にします。

つまり、デフォルトでは `stderr` に log しますが、[`log` global option](/docs/caddyfile/options#log) で `default` logger を再設定すれば変更できます。

```caddy
example.com {
	log
}
```


log をファイルへ書き込みます（log rolling はデフォルトで有効です）。

```caddy
example.com {
	log {
		output file /var/log/access.log
	}
}
```


log rolling をカスタマイズし、毎日 midnight または log file が 1 GB に達したとき（どちらか早い方）に roll し、roll 済みファイル 5 個または 30 日分の log を保持します。

```caddy
example.com {
	log {
		output file /var/log/access.log {
			roll_at 00:00
			roll_size 1gb
			roll_keep 5
			roll_keep_for 720h
		}
	}
}
```


log から `User-Agent` request header を削除します。

```caddy
example.com {
	log {
		format filter {
			request>headers>User-Agent delete
		}
	}
}
```


複数の機密 cookie を redact します。（一部の機密 header はデフォルトで空の値として log に記録される点に注意してください。`Cookie` header の値を logging するには [`log_credentials` global option](/docs/caddyfile/options#log-credentials) を参照してください。）

```caddy
example.com {
	log {
		format filter {
			request>headers>Cookie cookie {
				replace session REDACTED
				delete secret
			}
		}
	}
}
```


リクエストの remote address を mask し、IPv4 address では最初の 16 bits（つまり 255.255.0.0）、IPv6 address では最初の 32 bits を保持します。

Caddy v2.7 以降では、`remote_ip` と `client_ip` の両方が log に記録されます。`client_ip` は [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) が設定されている場合の "real IP" です。

```caddy
example.com {
	log {
		format filter {
			request>remote_ip ip_mask 16 32
			request>client_ip ip_mask 16 32
		}
	}
}
```


環境変数から server ID をすべての log entry に追加し、それを `filter` と chain して header を削除します。

```caddy
example.com {
	log {
		format append {
			server_id {env.SERVER_ID}
			wrap filter {
				request>headers>Cookie delete
			}
		}
	}
}
```


<span id="wildcard-logs" /> [wildcard site block](/docs/caddyfile/patterns#wildcard-certificates) 内で subdomain ごとに別々の log file へ書き込むには、各 logger の `hostnames` を上書きします。重複を避けるため、この例では [snippet](/docs/caddyfile/concepts#snippets) を使います。

```caddy
(subdomain-log) {
	log {
		hostnames {args[0]}
		output file /var/log/{args[0]}.log
	}
}

*.example.com {
	import subdomain-log foo.example.com
	@foo host foo.example.com
	handle @foo {
		respond "foo"
	}

	import subdomain-log bar.example.com
	@bar host bar.example.com
	handle @bar {
		respond "bar"
	}
}
```

<span id="multiple-outputs" /> 特定の subdomain の access log を、異なる format の 2 つのファイルへ書き込む例です（片方は [`transform-encoder` plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder)、もう片方は [`json`](#json)）。

これは、site block 内で logger name を `foo` として上書きし、その logger が生成した access log を、global options の 2 つの logger で `include http.log.access.foo` によって取り込むことで動作します。

```caddy
{
	log access-formatted {
		include http.log.access.foo
		output file /var/log/access-foo.log
		format transform "{common_log}"
	}

	log access-json {
		include http.log.access.foo
		output file /var/log/access-foo.json
		format json
	}
}

foo.example.com {
	log foo
}
```

<span id="sampling-example" /> sampling で log volume を減らす例です。たとえば、毎秒最初の 5 リクエストを保持し、その後は 10 リクエストごとに 1 件だけ保持します。

```caddy
example.com {
	log {
		sampling {
			interval   1s
			first      5
			thereafter 10
		}
	}
}
```
