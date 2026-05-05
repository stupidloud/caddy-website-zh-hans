---
title: グローバルオプション (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the options in the code block at the top
	// to their associated anchor tags.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Add links on comments to their respective sections
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // the leading whitespace
			text = text.slice(text.indexOf('#')); // only the comment part
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Surgically fix a duplicate link; 'name' appears twice as a link
	// for two different sections, so we change the second to #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// Surgically fix `renewal_window_ratio` which appears twice as a link for two different sections, so we change the second to #renewal_window_ratio-1
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>


<a id="global-options"></a>
# グローバルオプション

Caddyfile には、全体に適用されるオプションを指定する仕組みがあります。一部のオプションはデフォルト値として働きます。別のものは HTTP サーバーをカスタマイズし、特定の 1 つの site だけに適用されるものではありません。さらに別のものは Caddyfile [adapter](/docs/config-adapters) の挙動をカスタマイズします。

Caddyfile の最上部には **グローバルオプションブロック**を置けます。これはキーを持たないブロックです。

```caddy
{
	...
}
```

置けるのは最大 1 つだけで、Caddyfile の最初のブロックでなければなりません。

指定できるオプションは次のとおりです（各オプションをクリックすると、その説明へ移動します）。

```caddy
{
	# General Options
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hosts...>
	order <dir1> first|last|[before|after <dir2>]
	storage <module_name> {
		<options...>
	}
	storage_clean_interval <duration>
	admin   off|<addr> {
		origins <origins...>
		enforce_origin
	}
	persist_config off
	log [name] {
		output  <writer_module> ...
		format  <encoder_module> ...
		level   <level>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <duration>
	shutdown_delay <duration>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# TLS Options
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <yours>
	default_sni <name>
	fallback_sni <name>
	local_certs
	skip_install_trust
	acme_ca <directory_url>
	acme_ca_root <pem_file>
	acme_eab {
		key_id <key_id>
		mac_key <mac_key>
	}
	acme_dns <provider> ...
	dns <provider> ...
	ech <public_names...> {
		dns <provider> ...
	}
	on_demand_tls {
		ask        <endpoint>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <name> ...
	renew_interval <duration>
	cert_lifetime  <duration>
	ocsp_interval  <duration>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# Server Options
	servers [<listener_address>] {
		name <name>
		listener_wrappers {
			<listener_wrappers...>
		}
		timeouts {
			read_body   <duration>
			read_header <duration>
			write       <duration>
			idle        <duration>
		}
		keepalive_interval <duration>
		keepalive_idle     <duration>
		keepalive_count	   <number>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <headers...>

		trace
		max_header_size <size>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# File Systems
	filesystem <name> <module> {
		<options...>
	}

	# PKI Options
	pki {
		ca [<id>] {
			name                  <name>
			root_cn               <name>
			intermediate_cn       <name>
			intermediate_lifetime <duration>
			maintenance_interval  <duration>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <path>
				key    <path>
			}
			intermediate {
				format <format>
				cert   <path>
				key    <path>
			}
		}
	}

	# Event options
	events {
		on <event> <handler...>
	}
}
```


<a id="general-options"></a>
## 一般オプション

##### `debug`
debug モードを有効にします。これにより、[default logger](#log) の log level が `DEBUG` に設定されます。トラブルシューティングに役立つ詳細情報が出力されます（本番環境では非常に冗長です）。[community forums](https://caddy.community) で助けを求める前に、このオプションを有効にしていただくようお願いしています。たとえば、他にグローバルオプションがない場合は、Caddyfile の先頭に次のように書きます。

```caddy
{
	debug
}
```


##### `http_port`
サーバーが HTTP に使用する port です。

**内部利用専用**です。client 向けの HTTP port は変更しません。通常は、内部ネットワーク内で Caddy に到達する前に、ルーティング目的で `80` を別の port（例: `8080`）へ port forward する必要がある場合に使います。

デフォルト: `80`


##### `https_port`
サーバーが HTTPS に使用する port です。

**内部利用専用**です。client 向けの HTTPS port は変更しません。通常は、内部ネットワーク内で Caddy に到達する前に、ルーティング目的で `443` を別の port（例: `8443`）へ port forward する必要がある場合に使います。

デフォルト: `443`


##### `default_bind`
site で [`bind` directive](/docs/caddyfile/directives/bind) が使われていない場合に、すべての site で使われるデフォルトの bind address です。デフォルトは空で、すべての interface に bind します。

<aside class="tip">

これは Caddyfile から生成されるサーバーにのみ適用される点に注意してください。つまり、HTTP から HTTPS への redirect のために [Automatic HTTPS](/docs/automatic-https) が作成する HTTP サーバーは、これらの bind address を継承しません。回避するには、Caddyfile の adapt 時点でそのサーバーが存在し、bind address を受け取れるように、`http://` site（directive なしの空でも可）を宣言してください。

</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



##### `order`
HTTP handler directive に順序を割り当てます。HTTP handler は逐次的な chain として実行されるため、handler が正しい順序で実行される必要があります。標準 directive には[事前定義された順序](/docs/caddyfile/directives#directive-order)がありますが、サードパーティの HTTP handler module を使う場合は、このオプションを使うか、directive を [`route` block](/docs/caddyfile/directives/route) 内に置いて、順序を明示的に定義する必要があります。順序は絶対指定（`first` または `last`）でも、別の directive に対する相対指定（`before` または `after`）でも表せます。

たとえば [`replace-response` plugin](https://github.com/caddyserver/replace-response) を使う場合、レスポンスは handler chain を下るのではなく上へ戻るため、レスポンスが encode される前に置換できるよう、この directive を `encode` の後に並べる必要があります。

```caddy
{
	order replace after encode
}
```


##### `storage`
Caddy の storage 機構を設定します。デフォルトは [`file_system`](/docs/json/storage/file_system/) です。plugin として提供される他の [storage modules](/docs/json/storage/) も多数あります。

たとえば、file system の storage location を変更するには次のようにします。

```caddy
{
	storage file_system /path/to/custom/location
}
```

storage module のカスタマイズは、通常、複数の Caddy instance 間で Caddy の storage を同期し、すべてが同じ certificate と key を使うようにする場合に必要です。詳しくは [Automatic HTTPS の storage セクション](/docs/automatic-https#storage)を参照してください。


##### `storage_clean_interval`
storage unit をスキャンして古い asset や期限切れの asset を削除する頻度です。このスキャンは storage module に多くの read（および list 操作）を発生させるため、大規模 deployment では長めの interval を選んでください。[duration values](/docs/conventions#durations) を受け付けます。

process が最初に起動するとき、storage は必ず clean されます。その後、前回の clean がこの interval の半分未満の時間で完了した場合、前回の clean 開始からこの duration 後に新しい clean が開始されます（そうでない場合、次回開始は skip されます）。

デフォルト: `24h`

```caddy
{
	storage_clean_interval 7d
}
```




##### `admin`
[admin API endpoint](/docs/api) をカスタマイズします。placeholder を受け付けます。[network addresses](/docs/conventions#network-addresses) を取ります。

デフォルト: `localhost:2019`。ただし `CADDY_ADMIN` environment variable が設定されている場合を除きます。

`off` に設定すると、admin endpoint は無効化されます。無効化すると、[`caddy reload` command](/docs/command-line#caddy-reload) は admin API を使って実行中のサーバーへ新しい config を push するため、サーバーを停止して起動し直さない限り **config の変更は不可能**になります。

実行中サーバーの address をデフォルトから変更した場合は、互換性のある [commands](/docs/command-line) で現在の admin endpoint を指定するために、`--address` CLI flag を使うことを忘れないでください。

次の sub-option もサポートします。

- **origins** は、endpoint への接続を許可する [origins](https://developer.mozilla.org/en-US/docs/Glossary/Origin) の一覧を設定します。

  デフォルトは賢く選ばれます。
  - listen address が loopback（例: `localhost`、loopback IP、または unix socket）の場合、許可される origins は `localhost`、`::1`、`127.0.0.1` に listen address の port を結合したものです（したがって `localhost:2019` は有効な origin です）。
  - listen address が loopback でない場合、許可される origin は listen address と同じです。

  listen address の host が wildcard interface（wildcard には空文字列、`0.0.0.0`、`[::]` を含みます）でない場合、`Host` header の強制チェックが行われます。実質的には、interface が `localhost` であるため、デフォルトでは `Host` header が `origins` 内にあるか検証されます。一方、`:2020` のように wildcard interface を持つ address では、`Host` header の検証は行われません。

- **enforce_origin** は `Origin` request header の強制チェックを行います。これは client が CORS header を送信した場合、または client が `Sec-Fetch-Mode: no-cors` で明示的に CORS を無効化した場合に暗黙的に行われます。それ以外では、このオプションは listen address が wildcard interface（`Host` が検証されないため）で、admin API が public internet に公開されている場合に特に有用です。CORS preflight checks を有効化し、`Origin` header が `origins` list に対して検証されるようにします。開発マシン上で Caddy を実行していて、web browser から admin API にアクセスする必要がある場合にのみ使ってください。

たとえば、admin API を別の port で全 interface に公開するには次のようにします。⚠️ この port は **public に公開すべきではありません**。公開すると、誰でもあなたのサーバーを制御できてしまいます。public にする必要がある場合は origin enforcement の有効化を検討してください。

```caddy
{
	admin :2020
}
```

admin API を無効化するには次のようにします。⚠️ これにより、サーバーを停止して起動し直さない限り **config reload は不可能**になります。

```caddy
{
	admin off
}
```

admin API に [unix socket](/docs/conventions#network-addresses) を使い、file permission による access control を可能にするには次のようにします。

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

一致する `Origin` header を持つ request だけを許可するには次のようにします。

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```



##### `persist_config`

現在の JSON config を [configuration directory](/docs/conventions#configuration-directory) に永続化するかどうかを制御します。admin API 経由で行われた config 変更が失われるのを避けるためです。現在サポートされているのは `off` オプションのみです。デフォルトでは config は永続化されます。

```caddy
{
	persist_config off
}
```



##### `log`
名前付き logger を設定します。

name を渡すと、挙動をカスタマイズする対象の特定 logger を示せます。name を指定しない場合、`default` logger の挙動が変更されます。`default` logger と [Caddy における logging の仕組み](/docs/logging)について、さらに読むことができます。

異なる name を持つ複数の logger は、`log` を複数回使って設定できます。

これは [`log` directive](/docs/caddyfile/directives/log) とは異なります。directive の方は HTTP request logging（access logs とも呼ばれます）だけを設定します。`log` グローバルオプションは、その directive と同じ設定構造を共有します（`include` と `exclude` を除く）。完全なドキュメントは directive のページにあります。

- **output** は log の書き込み先を設定します。

  完全なドキュメントは [`log` directive](/docs/caddyfile/directives/log#output-modules) を参照してください。

- **format** は log をどのように encode、または format するかを記述します。

  完全なドキュメントは [`log` directive](/docs/caddyfile/directives/log#format-modules) を参照してください。

- **level** は log に出力する最小 entry level です。

  デフォルト: `INFO`

  指定できる値: `DEBUG`、`INFO`、`WARN`、`ERROR`。ごくまれに `PANIC`、`FATAL`。

- **include** はこの logger に含める log name を指定します。

  デフォルトでは、この list は空です（つまり、すべての log が含まれます）。

  たとえば、admin API から出力された log だけを含めるには、`admin.api` を含めます。

- **exclude** はこの logger から除外する log name を指定します。

  デフォルトでは、この list は空です（つまり、除外される log はありません）。

  たとえば、HTTP access log だけを除外するには、`http.log.access` を除外します。

`include` と `exclude` が受け付ける logger name は使用する module に依存し、それらを見つける最も簡単な方法は過去の log を見ることです。

次は、すべての http access log と admin log を json として stdout に出力する例です。

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

##### `grace_period`
HTTP サーバーを shutdown する際の grace period を定義します（つまり config 変更中、または Caddy の停止時）。

grace period 中は、新しい connection は受け付けられず、idle connection は閉じられ、active connection については request が完了するのを待ちます。client が grace period 内に request を完了しない場合、reload を完了して resource を解放できるよう、サーバーは強制終了されます。[duration values](/docs/conventions#durations) を受け付けます。

デフォルトでは grace period は無期限です。つまり connection が強制的に閉じられることはありません。

```caddy
{
	grace_period 10s
}
```


##### `shutdown_delay`
停止予定のサーバーが通常どおり動作し続ける、[grace period](#grace_period) の*前*の [duration](/docs/conventions#durations) を定義します。ただしその間、`{http.shutting_down}` placeholder は `true` と評価され、`{http.time_until_shutdown}` は grace period が始まるまでの時間を返します。

config 変更の一部としていずれかのサーバーが shutdown される場合、この設定により delay が発生し、実質的に変更が後の時刻にスケジュールされます。これは、このサーバーがまもなく停止することを health checker に知らせ、load balancer が rotation から外す時間を与えるのに便利です。例:

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Bye-bye in {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Hello, world!"
	}
}
```


<a id="tls-options"></a>
## TLS オプション

##### `auto_https`
[Automatic HTTPS](/docs/automatic-https) を設定します。これは、site の certificate management と HTTP から HTTPS への redirect を Caddy が自動化できるようにする機能です。

選べる mode はいくつかあります。

- `off`: certificate automation と HTTP から HTTPS への redirect の両方を無効にします。

- `disable_redirects`: HTTP から HTTPS への redirect のみを無効にします。

- `disable_certs`: certificate automation のみを無効にします。

- `ignore_loaded_certs`: 手動で読み込まれた certificate に含まれる name に対しても certificate を自動化します。[`tls` directive](/docs/caddyfile/directives/tls) で指定した certificate に、代わりに自動管理したい name（または wildcard）が含まれる場合に便利です。

<aside class="tip">

site address に有効な domain name がある場合、このオプションは Caddy のデフォルト protocol には影響しません。デフォルト protocol は常に HTTPS です。つまり `auto_https off` にしても site が HTTP で提供されるわけではなく、自動 certificate management と redirect だけが無効になります。

site を HTTP で提供したい場合は、[site address](/docs/caddyfile/concepts#addresses) に `http://` prefix を付けるか、`:80`（または [`http_port` option](#http_port)）suffix を付けてください。

</aside>

```caddy
{
	auto_https disable_redirects
}
```


##### `email`
あなたの email address です。主に CA で ACME account を作成するときに使われ、certificate に問題がある場合に備えて強く推奨されます。

<aside class="tip">

Let's Encrypt は certificate の期限が近づいたことを email で通知することがありますが、これは誤解を招く場合があります。Caddy が renewal 時に別の issuer（例: ZeroSSL）を使うことを選んでいる可能性があるためです。log や certificate 自体（たとえば browser 内）を確認して、どの issuer が使われたか、そして有効期限がまだ有効かを確認してください。有効であれば、Let's Encrypt からの email は安全に無視できます。

</aside>

```caddy
{
	email admin@example.com
}
```


##### `default_sni`
client が ClientHello で SNI を使わない場合の、デフォルト TLS ServerName を設定します。

```caddy
{
	default_sni example.com
}
```


##### `fallback_sni`
⚠️ <i>Experimental</i>

設定されている場合、元の ServerName が cache 内のどの certificate にも一致しないとき、fallback が ClientHello 内の TLS ServerName になります。

この用途は非常に限定的です。通常、client が CDN で、下流 handshake の ServerName を通過させる一方、origin の hostname を持つ certificate を受け入れられる場合に、これを origin の hostname として設定します。この name の certificate を Caddy が管理している必要がある点に注意してください。

```caddy
{
	fallback_sni example.com
}
```


##### `local_certs`
Let's Encrypt などの（public）ACME CA 経由ではなく、デフォルトで **すべての** certificate を内部発行させます。開発環境で素早く切り替えるために便利です。

```caddy
{
	local_certs
}
```


##### `skip_install_trust`
local CA の root を system trust store、Java trust store、Mozilla Firefox trust store へ install する試みを skip します。

```caddy
{
	skip_install_trust
}
```


##### `acme_ca`
ACME CA の directory URL を指定します。testing や development では、Let's Encrypt の [staging endpoint <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) に設定することを強く推奨します。デフォルト: ZeroSSL と Let's Encrypt の production endpoint。

グローバルに設定した ACME CA がすべての site に適用されるとは限りません。デフォルト ACME issuer を使うための [hostname requirements](/docs/automatic-https#hostname-requirements) を参照してください。

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

##### `acme_ca_root`
system trust store にない場合、ACME CA endpoint の trusted root certificate を含む PEM file を指定します。

```caddy
{
	acme_ca_root /path/to/ca/root.pem
}
```


##### `acme_eab`
すべての ACME transaction で使用する External Account Binding を指定します。

たとえば、mock の ZeroSSL credential を使う場合:

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


##### `acme_dns`
すべての ACME transaction で使う [ACME DNS challenge](/docs/automatic-https#dns-challenge) provider を設定します。

DNS provider 用 plugin を含む Caddy の custom build が必要です。

provider 名に続く token は、[`tls` directive の `acme` issuer](/docs/caddyfile/directives/tls#acme) で指定した場合と同じように provider を設定します。

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


##### `dns`
関連する context で local に他の provider が指定されていない場合に使う、デフォルト DNS provider を設定します。たとえば ACME DNS challenge が有効だが DNS provider が設定されていない場合、このグローバルデフォルトが使われます。Encrypted ClientHello (ECH) config の公開にも適用されます。

これを機能させるには、指定した DNS provider module を含めて Caddy binary が compile されている必要があります。

environment variable から credential を使う例:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

（Caddy 2.10 beta 1 以降が必要です。）


##### `ech`
指定した public domain name を TLS handshake 内の plaintext server name（SNI）として使い、Encrypted ClientHello (ECH) を有効にします。条件がそろえば、ECH は connection 時に wire 上で site の domain name を保護する助けになります。Caddy は指定された public name ごとに 1 つの ECH config を生成して公開します。公開により、互換 client（適切に設定された modern browser など）は、あなたの site へアクセスするときに ECH を使うべきことを知ります。

正しく動作するには、ECH config が client の期待する方法で公開されている必要があります。多くの browser（DNS-over-HTTPS または DNS-over-TLS が有効な場合）は、ECH config が HTTPS-type DNS record に公開されることを期待します。Caddy はこの種の公開を自動で行いますが、`dns` sub-option、またはグローバルの [`dns` global option](#dns) で DNS provider を指定する必要があり、Caddy binary は指定された DNS provider module を含めて build されている必要があります。（Custom build は [download page](/download) で利用できます。）

**プライバシー上の注意:**

- 一般には、**[_anonymity set_](https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction) の大きさを最大化する**ことが望ましいです。そのため、通常は、すべての site を保護する public domain name を *1 つだけ*設定することをほとんどの user に推奨しています。
- **指定する public domain name について、あなたのサーバーが authoritative であるべきです**（つまり、それらはあなたのサーバーを指しているべきです）。Caddy がそれらの certificate を取得するためです。これらの certificate は、一部の場合に、仕様準拠 client が ECH で確実かつ安全に接続するために重要です。これらは適切な ECH handshake を実現するためだけに使われ、application data には使われません（あなたの site には使われません。ただし、public domain name と同じ site を定義した場合を除きます）。
- 状況はそれぞれ異なります。利害が大きい場合、ECH は万能の解決策ではないため、専門家に相談して**脅威モデルを review**することを推奨します。

Cloudflare に parked された nameserver へ公開するため、environment variable から credential を使う例:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

これにより、互換 client は plaintext で個別の site name を露出する代わりに、`ech.example.net` であなたのすべての site を load するようになります。

公開に成功するには、site の domain が設定済み DNS provider に parked されており、与えられた credential / provider configuration で record を変更できる必要があります。

（Caddy 2.10 beta 1 以降が必要です。）


##### `on_demand_tls`
[On-Demand TLS](/docs/automatic-https#on-demand-tls) が有効になっている場所でそれを設定しますが、これ自体は有効化しません（有効化するには [`tls` directive の `on_demand` subdirective](/docs/caddyfile/directives/tls#syntax) を使います）。production environment で abuse を防ぐために必須です。

- **ask** は、指定された URL に対して Caddy に HTTP request を行わせ、domain に certificate を発行してよいかを問い合わせます。

  request には domain name の値を含む `?domain=` query string が付きます。

  endpoint が `2xx` status code を返した場合、Caddy はその name の certificate を取得することを許可されます。それ以外の status code は certificate 発行のキャンセルと TLS handshake の error につながります。

<aside class="tip">

ask endpoint は、理想的には数 millisecond で、*できるだけ速く*返すべきです。通常、endpoint は domain name で index された database に対して constant-time lookup を行うべきです。loop は避けてください。DNS query や他の network request も避けてください。

</aside>

- **permission** は、特定の name について certificate を発行すべきかどうかを判断するために custom module を使えるようにします。この module は [`caddytls.OnDemandPermission` interface](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission) を実装している必要があります。`http` permission module が含まれており、これは `ask` option が使うものです。また、後方互換性のための shortcut として残っています。

- ⚠️ **interval** と **burst** の rate limiting option は利用可能でしたが、推奨されません。まだ config に残っている場合は削除してください。

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


##### `key_type`
TLS certificate 用に生成する key の type を指定します。これを変更するのは、カスタマイズする明確な必要がある場合だけにしてください。

指定できる値: `ed25519`、`p256`、`p384`、`rsa2048`、`rsa4096`

```caddy
{
	key_type ed25519
}
```


##### `cert_issuer`
TLS certificate の issuer（または source）を定義します。

[`tls` directive の `issuer` subdirective](/docs/caddyfile/directives/tls#issuer) で site ごとに設定する代わりに、issuer をグローバルに設定できます。

試行したい issuer が複数ある場合は、繰り返し指定できます。定義された順序で試行されます。

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


##### `renew_interval`
読み込まれて管理されているすべての certificate の expiration をスキャンし、期限切れであれば renewal を trigger する頻度です。

デフォルト: `10m`

```caddy
{
	renew_interval 30m
}
```


##### `cert_lifetime`
CA に発行を求める certificate の validity period です。

この値は ACME order の `notAfter` field を計算するために使われます。そのため、system clock は十分に同期されている必要があります。注意: すべての CA がこれをサポートしているわけではありません。許可されているか、どの値が使えるかは、CA の ACME documentation で確認してください。

デフォルト: `0`（CA が lifetime を選びます。通常は 90 日）

⚠️ これは experimental feature です。変更または削除される可能性があります。

```caddy
{
	cert_lifetime 30d
}
```


##### `ocsp_interval`
[OCSP staples <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OCSP_stapling) の更新が必要かどうかを確認する頻度です。

デフォルト: `1h`

```caddy
{
	ocsp_interval 2h
}
```


##### `ocsp_stapling`
`off` に設定すると OCSP stapling を無効にできます。firewall のため responder に到達できない環境で便利です。

```caddy
{
	ocsp_stapling off
}
```

##### `renewal_window_ratio`
Caddy が certificate の renewal を試みる前に残っている必要がある、certificate lifetime の割合（0 から 1）です。たとえば certificate の lifetime が 90 日で、この ratio が `0.3333`（デフォルト値）の場合、Caddy は expiration まで 30 日以下になると、certificate の renewal を継続的に試みます。[`tls` directive の `renewal_window_ratio` subdirective](/docs/caddyfile/directives/tls#renewal_window_ratio) で site ごとにも設定できます。

これを変更する必要はほとんどありませんが、CA の発行時間が非常に長い場合、certificate lifetime の後半で renew するために役立つことがあります。

これは suggestion である点に注意してください。ACME issuer は [ARI extension](https://datatracker.ietf.org/doc/rfc9773/) を実装している場合があり、その場合 issuer が ACME client（この場合は Caddy）が renewal を試みるべき window を指示します。その window はこの ratio と一致しない可能性があります。

```caddy
{
	renewal_window_ratio 0.1
}
```


##### `preferred_chains`
CA が複数の certificate chain を提供する場合、このオプションで Caddy が優先すべき chain を指定できます。次のいずれかのオプションを設定します。

- **smallest** は、byte 数が最も少ない chain を優先するよう Caddy に指示します。

- **root_common_name** は 1 つ以上の common name の list です。Caddy は、指定された common name の少なくとも 1 つに一致する root を持つ最初の chain を選びます。

- **any_common_name** は 1 つ以上の common name の list です。Caddy は、指定された common name の少なくとも 1 つに一致する issuer を持つ最初の chain を選びます。

`preferred_chains` をグローバルオプションとして指定すると、[issuer level config の override](/docs/caddyfile/directives/tls#acme) がない限り、すべての issuer に影響する点に注意してください。

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```


<a id="server-options"></a>
## Server オプション

複数の site にまたがる可能性があるため site block 内では適切に設定できない設定で、[HTTP servers](/docs/json/apps/http/servers/) をカスタマイズします。これらのオプションは、HTTP layer の下にある listener/socket やその他の機能に影響します。

異なる `listener_address` 値で複数回指定し、server ごとに異なる option を設定できます。たとえば `servers :443` は、listener address `:443` に bind されている server にだけ適用されます。listener address を省略すると、残りのすべての server に option が適用されます。

<aside class="tip">

Caddyfile 内の server の listen address を調べるには、[`caddy adapt`](/docs/command-line#caddy-adapt) command を使ってください。

</aside>


たとえば、port `:80` と `:443` の server に別々の option を設定するには、2 つの `servers` block を指定します。

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

`servers` を使う場合、これは Caddyfile 内に **実際に現れる** server（つまり site block から生成される server）に**のみ**適用されます。[Automatic HTTPS](/docs/automatic-https) は HTTP->HTTPS redirect の提供と ACME HTTP challenge の解決のために、port `80`（または [`http_port` option](#http_port)）で listen する server を作成します。これは runtime、つまり Caddyfile adapter が `servers` を適用した*後*に起こります。言い換えると、`http://` や `:80` のような site block を明示的に宣言しない限り、`servers` は `:80` には適用されません。


<aside class="tip">

[`bind` directive](/docs/caddyfile/directives/bind) または [`default_bind` global option](/docs/caddyfile/options#default_bind) を使っている場合、`listener_address` は bind address と site block の port を組み合わせたものに*一致しなければなりません*。そうでないと設定は適用されません。例:

```caddy
{
	# これは server に一致しません。bind address がありません
	servers :8080 {
		name private
	}

	# 完全一致なのでこれは動作します
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



##### `name`

この server に割り当てる custom name です。通常、log や metrics で server を名前で識別するのに役立ちます。設定されていない場合、Caddy は `srvX` pattern を使って動的に定義します。ここで `X` は `0` から始まり、config 内の server 数に応じて増加します。

設定が適用されるのは config 内の site block から生成された server だけである点に注意してください。[Automatic HTTPS](/docs/automatic-https) は runtime に `:80` server（または [`http_port`](#http_port)）を作成するため、それを rename したい場合は少なくとも空の `http://` site block が必要です。

例:

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```

</aside>



##### `listener_wrappers`

[listener wrappers](/docs/json/apps/http/servers/listener_wrappers/) を設定できます。これは socket listener の挙動を変更できます。指定された順序で適用されます。

###### `tls`

`tls` listener wrapper は、listener wrapper の chain 内で TLS listener があるべき位置を示す no-op listener wrapper です。別の listener wrapper を TLS handshake の前に置く必要がある場合にのみ使うべきです。

###### `http_redirect`

[`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/) は、TLS port に HTTP request として来た connection に対して HTTP->HTTPS redirect を提供します。最初の数 byte を使って、それが TLS handshake ではなく HTTP request であることを検出します。これは、標準でない port（`443` 以外）で HTTPS を提供する場合に特に有用です。scheme が指定されていないと browser は HTTP を試すためです。これは `tls` listener wrapper の*前*に置かなければなりません。例:

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

###### `proxy_protocol`

[`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/) listener wrapper（v2.7.0 より前は plugin 経由でのみ利用可能でした）は、[PROXY protocol](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) parsing（HAProxy によって普及）を有効にします。これは connection の先頭にある plaintext data を parse するため、`tls` listener wrapper の*前*に使う必要があります。

PROXY protocol からの metadata は、matcher や [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) の評価より前に connection に適用される可能性がある点に注意してください。直近 peer の IP address は、その後の評価では失われます。

```caddy-d
proxy_protocol {
	timeout <duration>
	allow <cidrs...>
	deny <cidrs...>
	fallback_policy <policy>
}
```

- **timeout** は PROXY header を待つ最大 duration を指定します。デフォルトは `5s` です。

- **allow** は、PROXY header を受け取る trusted source の CIDR range list です。Unix socket はデフォルトで trusted であり、この option には含まれません。

- **deny** は、PROXY header を拒否する trusted source の CIDR range list です。

- **fallback_policy** は、PROXY header が allow/deny のどちらの list にも含まれない address から来た場合に取る action です。デフォルトの fallback policy は `ignore` です。`fallback_policy` で受け付ける値は次のとおりです。
	- `ignore`: PROXY header からの address は無視するが、connection は受け入れる
	- `use`: PROXY header からの address を使う
	- `reject`: PROXY header が送信された場合、connection を拒否する
	- `require`: connection に PROXY header の送信を要求し、存在しない場合は拒否する
	- `skip`: PROXY header を要求せずに connection を受け入れる


たとえば、特定の IP address range からの PROXY header を受け入れ、別の range からの PROXY header を拒否し、timeout を 2 秒にする HTTPS server（`tls` listener wrapper が必要）の例です。

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


##### `timeouts`

- **read_body** は、client upload からの read をどれだけ許可するかを設定する [duration value](/docs/conventions#durations) です。短い非ゼロ値に設定すると slowloris attack を緩和できますが、正当に遅い client にも影響する可能性があります。デフォルトでは timeout なしです。

- **read_header** は、client の request headers からの read をどれだけ許可するかを設定する [duration value](/docs/conventions#durations) です。デフォルトでは timeout なしです。

- **write** は、client への write をどれだけ許可するかを設定する [duration value](/docs/conventions#durations) です。大きな file を提供するときに小さい値を設定すると、正当に遅い client に悪影響を与える可能性がある点に注意してください。デフォルトでは timeout なしです。

- **idle** は、keep-alive が有効な場合に次の request を待つ最大時間を設定する [duration value](/docs/conventions#durations) です。resource exhaustion を避けるため、デフォルトは 5 分です。

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


##### `keepalive_interval`

他の data が送信されていないときに、connection を TCP layer で維持するため TCP keepalive packet を送信する interval です。デフォルトは `15s` です。

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


##### `keepalive_idle`

他の data が送信されていないときに TCP keepalive packet を送信し始めるまで、connection が idle でなければならない duration です。デフォルトは `15s` です。

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


##### `keepalive_count`

connection が dead とみなされる前に送信する TCP keepalive packet の最大数です。デフォルトは `9` です。

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


##### `0rtt`

デフォルトでは、QUIC listener（つまり HTTP/3）で 0-RTT（early data）が有効です。これにより、client は TLS handshake の最初の round trip で data を送信でき、repeat connection の性能が向上する可能性があります。

QUIC listener の 0-RTT を無効にするには、これを `off` に設定できます。0-RTT を無効にする理由の 1 つは、[`remote_ip` matcher](/docs/caddyfile/matchers#remote-ip) が使われている場合です。これは、TLS handshake が完了する前に routing が発生すると、remote address が検証済みであることへの依存を導入します。その場合 HTTP 425 response が書き込まれますが、一部の client（browser）は誤動作して retry を行わないことがあります。そのため、0-RTT を無効にすると、0-RTT の性能上の利点を失う代わりに、user が 425 response を目にしないようにできます。

```caddy
{
	servers {
		0rtt off
	}
}
```


##### `trusted_proxies`

request を trusted とみなす proxy server の IP range（CIDR）を設定できます。デフォルトでは、trusted proxy はありません。

これを有効にすると、trusted request では HTTP header（デフォルトでは `X-Forwarded-For`。他の header を設定するには [`client_ip_headers`](#client-ip-headers) を参照）から*実際の* client IP が parse されます。trusted の場合、client IP は [access logs](/docs/caddyfile/directives/log) に追加され、`{client_ip}` [placeholder](/docs/caddyfile/concepts#placeholders) として利用でき、[`client_ip` matcher](/docs/caddyfile/matchers#client-ip) を使えるようになります。request が trusted proxy からのものでない場合、client IP は直接入ってきた connection の remote IP address、または [PROXY protocol](/docs/caddyfile/options#proxy-protocol) を使っている場合はそれによって設定された address になります。デフォルトでは、header 内の IP は左から右に parse されます。この挙動を変更するには [`trusted_proxies_strict`](#trusted-proxies-strict) を参照してください。

一部の matcher や handler は、request の trust status を使って判断する場合があります。たとえば trusted の場合、[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#defaults) handler は sensitive な `X-Forwarded-*` request header を proxy し、拡張します。

現在、Caddy の標準 distribution に含まれるのは `static` [IP source module](/docs/json/apps/http/servers/trusted_proxies/) のみですが、dynamic な IP range list を維持する plugin で[拡張](/docs/extending-caddy)できます。


###### `static`

trusted とする static（変化しない）IP range（CIDR）の list を取ります。

shortcut として、`private_ranges` を使うと private IPv4 および IPv6 range すべてに一致させられます。これは次の range をすべて指定するのと同じです: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

構文は次のとおりです。

```caddy-d
trusted_proxies static [private_ranges] <ranges...>
```

example IPv4 range と IPv6 range を trusted とする完全な例です。

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

##### `trusted_proxies_strict`

[`trusted_proxies`](#trusted-proxies) が有効な場合、header（[`client_ip_headers`](#client-ip-headers) で設定）内の IP はデフォルトでは左から右に parse されます。最初に見つかった untrusted IP address が実際の client address になります。v2.8 以降では、`trusted_proxies_strict` により、これらの header を右から左に parse する方式へ opt-in できます。後方互換性のため、この option はデフォルトで無効です。

HAProxy、CloudFlare、AWS ALB、CloudFront などの upstream proxy は、新しく接続した各 remote address を `X-Forwarded-For` の右側へ append します。左端の IP address は client によって spoof される可能性があるため、これらを使う場合は `trusted_proxies_strict` を有効にすることを推奨します。

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">

特に AWS ALB の場合、この option はほぼ確実に有効にしたいはずです。[documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15) によると、実際の client IP を識別するには XFF mode を `append` に設定するしかありません。この IP は `X-Forwarded-For` の右側に append され、`trusted_proxies_strict` 経由でのみ安全に抽出できます。

</aside>

##### `trusted_proxies_unix`

`trusted_proxies_unix` option は、Unix socket から来るすべての connection を trusted にできます。これは、Caddy が Unix socket 経由で接続する reverse proxy（別の Caddy instance である可能性もあります）の背後にある場合に便利です（つまり [`bind` directive](/docs/caddyfile/directives/bind) が unix socket に設定されている場合）。デフォルトでは無効です。

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

##### `client_ip_headers`

[`trusted_proxies`](#trusted-proxies) と組み合わせて、client の IP address を判断するために使う header を設定できます。デフォルトでは `X-Forwarded-For` のみが考慮されます。複数の header field を指定でき、その場合は最初の空でない header value が使われます。

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


##### `metrics`

metrics collection を有効にします。metrics を scrape したり OTLP で push したりする前に必要です。metrics は非常に高負荷な server では性能を低下させる点に注意してください。（community はこれを改善するために取り組んでいます。ぜひ参加してください！）

```caddy
{
	metrics
}
```

metric の host name で metrics に label を付けるには、`per_host` option を追加できます。

```caddy
{
	metrics {
		per_host
	}
}
```

client から送られる可能性のあるすべての host を観測すると cardinality が無限になり得るため、Caddy は設定済み host の metrics だけを記録し、その他すべての host（例: attacker.com）は "_other" label の下に集約します。すべての host の観測を強制し、潜在的な無限 cardinality が許容できる risk である場合は、`observe_catchall_hosts` を追加します。`observe_catchall_hosts` を追加しても `per_host` は有効にならない点に注意してください。ただし、HTTPS server ではこれは自動的に有効になります（certificate が無制限の cardinality に対して一定の保護を提供するため）。HTTP server では任意の Host header による cardinality attack を防ぐため、デフォルトで無効です。

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

同じ metrics を OpenTelemetry Protocol (OTLP) endpoint に push するには、`otlp` option を追加できます。exporter は `OTEL_EXPORTER_OTLP_ENDPOINT`、`OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`、`OTEL_EXPORTER_OTLP_PROTOCOL`、`OTEL_EXPORTER_OTLP_HEADERS`、`OTEL_METRIC_EXPORT_INTERVAL`、`OTEL_METRICS_EXPORTER` などの標準 OpenTelemetry `OTEL_*` environment variable で設定されます。

```caddy
{
	metrics {
		otlp
	}
}
```

例:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

詳しくは [Monitoring Caddy with metrics](/docs/metrics) を参照してください。

##### `trace`

呼び出された個々の handler を log に出力します。log が `DEBUG` level で emit される必要があります（[`debug` global option](#debug) で設定できます）。

注意: これは HTTP handler module の configuration を log に出力する可能性があります。configuration に sensitive data が含まれる場合、安全でない context では有効にしないでください。

⚠️ これは experimental feature です。変更または削除される可能性があります。

```caddy
{
	servers {
		trace
	}
}
```


##### `max_header_size`

client の HTTP request headers から parse する最大 size です。limit を超えると、server は HTTP status `431 Request Header Fields Too Large` で応答します。[go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) がサポートするすべての format を受け付けます。デフォルトの limit は `1MB` です。

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


##### `enable_full_duplex`

HTTP/1 request の full-duplex communication を有効にします。

HTTP/1 request では、Go HTTP server はデフォルトで response の書き込みを始める前に request body の未読部分を消費します。これにより handler が request から読みながら同時に response を書き込むことができなくなります。この option を有効にすると、この挙動が無効になり、handler は request から読み続けながら同時に response を書き込めます。

HTTP/2+ request では、Go HTTP server は常に concurrent read と response を許可するため、この option は効果がありません。

古い client の中には full-duplex HTTP/1 をサポートせず、deadlock を起こす可能性があるため、HTTP client で十分に test してください。詳しくは [golang/go#57786](https://github.com/golang/go/issues/57786) を参照してください。

⚠️ これは experimental feature です。変更または削除される可能性があります。

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


##### `log_credentials`

デフォルトでは、[`log` directive](/docs/caddyfile/directives/log) で有効化された access log では、潜在的に sensitive な情報を含む header（`Cookie`、`Set-Cookie`、`Authorization`、`Proxy-Authorization`）は `REDACTED` として log に記録されます。

これらの header を redact したくない場合は、`log_credentials` option を有効にできます。

```caddy
{
	servers {
		log_credentials
	}
}
```



##### `protocols`

サポートする HTTP protocol の space-separated list です。

デフォルト: `h1 h2 h3`

受け付ける値:
- `h1`: HTTP/1.1
- `h2`: HTTP/2
- `h2c`: cleartext 上の HTTP/2
- `h3`: HTTP/3

現在、HTTP/2（H2C を含む）を有効にすると、必然的に HTTP/1.1 も有効になります。Go standard library は、その HTTP server を使うときに HTTP/1.1 を無効にできないためです。ただし、HTTP/1.1 または HTTP/3 はそれぞれ独立して有効にできます。

H2C（"Cleartext HTTP/2" または "H2 over TCP"）と HTTP/3 は Go standard library によって実装されていないため、一部の functionality や feature が制限される可能性がある点に注意してください。application にとって絶対に必要でない限り、H2C を有効にすることは推奨しません。

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



##### `strict_sni_host`

これを有効にすると、request の `Host` header が client の TLS ClientHello で送信された `ServerName` の値と一致することが要求されます。これは TLS client authentication を使う場合に必要な safeguard です。不一致がある場合、HTTP status `421 Misdirected Request` response が client に書き込まれます。

[client authentication](/docs/caddyfile/directives/tls#client_auth) が設定されている場合、この option は自動的に有効になります。これにより、保護されていない SNI value を TLS handshake 中に送信し、connection 確立後に Host header に保護対象 domain を入れることで悪用できる TLS client auth bypass（domain fronting）を禁止します。この挙動は安全なデフォルトですが、`insecure_off` で明示的に無効にできます。たとえば、domain fronting が望まれていて、hostname に基づいて access が制限されない proxy を実行する場合です。

```caddy
{
	servers {
		strict_sni_host on
	}
}
```



<a id="file-systems"></a>
## File System

`filesystem` global option は、file I/O に使用できる 1 つ以上の file system を宣言できます。

これにより、cloud で実行されている remote filesystem、file-like interface を持つ database、あるいは Caddy binary に embedded された file からの読み取りに接続できる可能性があります。

file system は、それを識別する name とともに宣言されます。つまり、必要であれば同じ type の file system に複数接続できます。

デフォルトでは、Caddy は file system module を持っていないため、使いたい file system の plugin を含めて Caddy を build する必要があります。

<a id="example"></a>
#### 例

架空の `custom` file system module を使う場合、2 つの file system を宣言できます。

```caddy
{
	filesystem foo custom {
		...
	}

	filesystem bar custom {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```



<a id="pki-options"></a>
## PKI オプション

PKI (Public Key Infrastructure) app は、Caddy の [Local HTTPS](/docs/automatic-https#local-https) と [ACME server](/docs/caddyfile/directives/acme_server) feature の基盤です。この app は、certificate に署名できる certificate authority (CA) を定義します。

デフォルト CA ID は `local` です。`ca` を設定するときに ID を省略すると、`local` とみなされます。

##### `name`
certificate authority の user-facing name です。

デフォルト: `Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "My Local CA"
		}
	}
}
```

##### `root_cn`
root certificate の CommonName field に入れる name です。

デフォルト: `{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "My Local CA - 2024 ECC Root"
		}
	}
}
```

##### `intermediate_cn`
intermediate certificate の CommonName field に入れる name です。

デフォルト: `{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "My Local CA - ECC Intermediate"
		}
	}
}
```

##### `intermediate_lifetime`
intermediate certificate が有効な [duration](/docs/conventions#durations) です。この値は root cert の lifetime（`3600d` または 10 年）より**短くなければなりません**。

デフォルト: `7d`。絶対に必要でない限り、これを変更することは*推奨されません*。

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

##### `maintenance_interval`
intermediate（および該当する場合は root）certificate の renewal が必要かどうかを確認する頻度を表す [duration](/docs/conventions#durations) です。

デフォルト: `10m`。絶対に必要でない限り、これを変更することは*推奨されません*。

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

##### `renewal_window_ratio`
Caddy が certificate の renewal を試みる前に残っている必要がある、certificate lifetime の割合（0 から 1）です。たとえば certificate の lifetime が 1 年で、この ratio が `0.2`（デフォルト値）の場合、Caddy は expiration まで 73 日以下になると、certificate の renewal を継続的に試みます。

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


##### `root`
CA の root として使う key pair（certificate と private key）です。指定しない場合は自動的に生成、管理されます。

- **format** は certificate と private key が提供される format です。現在サポートされているのは `pem_file` のみで、これがデフォルトであるため、この field は optional です。
- **cert** は certificate です。`pem_file` format を使う場合、これは PEM file への path であるべきです。
- **key** は private key です。`pem_file` format を使う場合、これは PEM file への path であるべきです。

##### `intermediate`
CA の intermediate として使う key pair（certificate と private key）です。指定しない場合は自動的に生成、管理されます。

- **format** は certificate と private key が提供される format です。現在サポートされているのは `pem_file` のみで、これがデフォルトであるため、この field は optional です。
- **cert** は certificate です。`pem_file` format を使う場合、これは PEM file への path であるべきです。
- **key** は private key です。`pem_file` format を使う場合、これは PEM file への path であるべきです。

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /path/to/root.pem
				key /path/to/root.key
			}
			intermediate {
				format pem_file
				cert /path/to/intermediate.pem
				key /path/to/intermediate.key
			}
		}
	}
}
```


<a id="event-options"></a>
## Event オプション

Caddy module は、興味深いことが起きたとき（または起きようとしているとき）に event を emit します。

event には通常 metadata payload が含まれます。event とその payload について知る最良の方法は各 module の documentation ですが、[`debug` global option](#debug) を有効にして log を読むことで、event とその data payload を確認することもできます。

##### `on`

名前付き event に event handler を bind します。event handler module の name を指定し、その後に configuration を続けます。

たとえば、certificate が取得された後に command を実行するには（[third-party plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/mholt/caddy-events-exec) が必要）、event payload の一部を placeholder で script に渡します。

```caddy
{
	events {
		on cert_obtained exec ./my-script.sh {event.data.certificate_path}
	}
}
```

<a id="events"></a>
### Events

これらの標準 event は Caddy によって emit されます。

- [`tls` events <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/certmagic#events)
- [`reverse_proxy` events](/docs/caddyfile/directives/reverse_proxy#events)

plugin も event を emit する場合があるため、詳しくはそれぞれの documentation を確認してください。
