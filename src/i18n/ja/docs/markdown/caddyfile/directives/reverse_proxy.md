---
title: reverse_proxy (Caddyfile directive)
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Fix matcher placeholder
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@name')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">@name</a>';
			break;
		}
	}
	
	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}
	
	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# reverse_proxy

設定可能な transport、load balancing、health checking、request 操作、buffering option を使って、リクエストを 1 つ以上の backend に proxy します。

- [構文](#syntax)
- [Upstream](#upstreams)
  - [Upstream address](#upstream-addresses)
  - [Dynamic upstream](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
	- [Multi](#multi)
- [Load balancing](#load-balancing)
  - [Active health checks](#active-health-checks)
  - [Passive health checks](#passive-health-checks)
  - [Events](#events)
- [Streaming](#streaming)
- [Headers](#headers)
- [Rewrites](#rewrites)
- [Transports](#transports)
  - [`http` transport](#the-http-transport)
  - [`fastcgi` transport](#the-fastcgi-transport)
- [レスポンスの intercept](#intercepting-responses)
- [例](#examples)



<a id="syntax"></a>
## 構文

```caddy-d
reverse_proxy [<matcher>] [<upstreams...>] {
	# backend
	to      <upstreams...>
	dynamic <module> ...

	# load balancing
	lb_policy       <name> [<options...>]
	lb_retries      <retries>
	lb_try_duration <duration>
	lb_try_interval <interval>
	lb_retry_match  <request-matcher>

	# active health checking
	health_uri          <uri>
	health_upstream     <ip:port>
	health_port         <port>
	health_interval     <interval>
	health_passes       <num>
	health_fails	    <num>
	health_timeout      <duration>
	health_method       <method>
	health_status       <status>
	health_request_body <body>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<field> [<values...>]
	}

	# passive health checking
	fail_duration     <duration>
	max_fails         <num>
	unhealthy_status  <status>
	unhealthy_latency <duration>
	unhealthy_request_count <num>

	# streaming
	flush_interval     <duration>
	request_buffers    <size>
	response_buffers   <size>
	stream_timeout     <duration>
	stream_close_delay <duration>

	# request/header 操作
	trusted_proxies [private_ranges] <ranges...>
	header_up   [+|-]<field> [<value|regexp> [<replacement>]]
	header_down [+|-]<field> [<value|regexp> [<replacement>]]
	method <method>
	rewrite <to>

	# round trip
	transport <name> {
		...
	}

	# 必要に応じて upstream からのレスポンスを intercept
	@name {
		status <code...>
		header <field> [<value>]
	}
	replace_status [<matcher>] <status_code>
	handle_response [<matcher>] {
		<directives...>

		# handle_response 内でのみ使える特別なディレクティブ
		copy_response [<matcher>] [<status>] {
			status <status>
		}
		copy_response_headers [<matcher>] {
			include <fields...>
			exclude <fields...>
		}
	}
}
```



<a id="upstreams"></a>
## Upstream

- **&lt;upstreams...&gt;** は、proxy 先の upstream（backend）の一覧です。
- **to** <span id="to"/> は upstream の一覧を指定する別の方法で、1 行に 1 つ（または複数）指定します。
- **dynamic** <span id="dynamic"/> は *dynamic upstreams* module を設定します。これにより、リクエストごとに upstream 一覧を動的に取得できます。標準の dynamic upstream module については、下の [dynamic upstream](#dynamic-upstreams) を参照してください。Dynamic upstream は proxy loop の各 iteration で取得されます（つまり load balancing の retry が有効な場合、1 リクエスト中に複数回取得される可能性があります）。また static upstream より優先されます。エラーが発生した場合、proxy は静的に設定された upstream があればそれに fallback します。


<a id="upstream-addresses"></a>
### Upstream address

Static upstream address は、scheme と host/port だけを含む URL、または通常の [Caddy network address](/docs/conventions#network-addresses) の形式を取れます。有効な例:

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

デフォルトでは、upstream への接続は plaintext HTTP で行われます。URL 形式を使う場合、scheme を shorthand として使い、いくつかの [`transport`](#transports) のデフォルトを設定できます。
- scheme に `https://` を使うと、[`tls`](#tls) が有効な [`http` transport](#the-http-transport) が使われます。

  さらに、`Host` header を TLS SNI 値と一致するように上書きする必要がある場合があります。これは server が routing と証明書選択に使う値です。詳細は下の [HTTPS](#https) セクションを参照してください。

- scheme に `h2c://` を使うと、cleartext HTTP/2 接続を許可する [HTTP versions](#versions) を設定した [`http` transport](#the-http-transport) が使われます。

- scheme に `http://` を使うことは、scheme を省略した場合と同じです。HTTP はすでにデフォルトだからです。この構文は他の scheme shortcut と対称にするために含まれています。

scheme は混在できません。共通の transport 設定を変更するためです（TLS-enabled transport は HTTPS と plaintext HTTP の両方を運べません）。明示的な transport 設定は上書きされず、scheme を省略したり他の port を使ったりしても、特定の transport は仮定されません。

zone 付き IPv6（例: 特定の network interface を持つ link-local address）を使う場合、`%` により URL parse error が発生するため、scheme を shortcut として使うことは**できません**。代わりに transport を明示的に設定してください。

[network address](/docs/conventions#network-addresses) 形式を使う場合、network type は upstream address の prefix として指定します。これは URL scheme と組み合わせられません。特殊なケースとして、`unix+h2c/` は `unix/` network に `h2c://` scheme と同じ効果を加える shortcut としてサポートされています。Port range は shortcut としてサポートされ、同じ host を持つ複数の upstream に展開されます。

Upstream address には path や query 文字列を含めることは**できません**。それは proxy と同時にリクエストを書き換えることを意味し、その挙動は定義もサポートもされていないためです。必要な場合は [`rewrite`](/docs/caddyfile/directives/rewrite) ディレクティブを使ってください。

address が URL でない（つまり scheme を持たない）場合、[placeholders](/docs/caddyfile/concepts#placeholders) を使えます。ただし、これは upstream を *dynamically static* にします。つまり、health check と load balancing の観点では、潜在的に多数の異なる backend が単一の static upstream として扱われます。可能であれば、代わりに [dynamic upstream](#dynamic-upstreams) module を使うことを推奨します。placeholder を使う場合、port は**必ず**含める必要があります（placeholder の置換結果、または address の静的 suffix のどちらでもかまいません）。


<a id="dynamic-upstreams"></a>
### Dynamic upstream

Caddy の reverse proxy には、いくつかの dynamic upstream module が標準で含まれています。dynamic upstream を使うと、特定の policy 設定によって load balancing と health check に影響があることに注意してください。active health check は dynamic upstream には実行されません。また、load balancing と passive health check は、upstream 一覧が比較的安定して一貫している場合に最もうまく機能します（特に round-robin）。理想的には、dynamic upstream module は healthy で利用可能な backend だけを返すべきです。


<a id="srv"></a>
#### SRV

SRV DNS record から upstream を取得します。

```caddy-d
	dynamic srv [<full_name>] {
		service   <service>
		proto     <proto>
		name      <name>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
	}
```

- **&lt;full_name&gt;** は lookup する record の完全な domain name（つまり `_service._proto.name`）です。
- **service** は full name の service component です。
- **proto** は full name の protocol component です。`tcp` または `udp` です。
- **name** は name component です。または `service` と `proto` が空の場合、query する完全な domain name です。
- **refresh** は cached result を更新する頻度です。デフォルト: `1m`
- **resolvers** は system resolver を上書きする DNS resolver の一覧です。
- **dial_timeout** は query の dial timeout です。
- **dial_fallback_delay** は RFC 6555 Fast Fallback connection を起動するまで待つ時間です。デフォルト: `300ms`



<a id="aaaaa"></a>
#### A/AAAA

A/AAAA DNS record から upstream を取得します。

```caddy-d
	dynamic a [<name> <port>] {
		name      <name>
		port      <port>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
		versions ipv4|ipv6
	}
```

- **name** は query する domain name です。
- **port** は backend に使う port です。
- **refresh** は cached result を更新する頻度です。デフォルト: `1m`
- **resolvers** は system resolver を上書きする DNS resolver の一覧です。
- **dial_timeout** は query の dial timeout です。
- **dial_fallback_delay** は RFC 6555 Fast Fallback connection を起動するまで待つ時間です。デフォルト: `300ms`
- **versions** は解決する IP version の一覧です。デフォルトは `ipv4 ipv6` で、それぞれ A record と AAAA record に対応します。


<a id="multi"></a>
#### Multi

複数の dynamic upstream module の結果を追加します。たとえば、primary SRV cluster を secondary SRV cluster でバックアップするなど、upstream source を冗長化したい場合に便利です。

```caddy-d
	dynamic multi {
		<source> [...]
	}
```

- **&lt;source&gt;** は dynamic upstream 用 module の名前と、その設定です。複数指定できます。




<a id="load-balancing"></a>
## Load balancing

Load balancing は通常、複数の upstream 間で traffic を分散するために使います。retry を有効にすると、1 つ以上の upstream に対しても、healthy な upstream を選べるまでリクエストを保持する目的で使えます（例: upstream の reboot や redeploy 中に待機して error を緩和する）。

これは `random` policy でデフォルト有効です。retry はデフォルト無効です。

- **lb_policy** <span id="lb_policy"/> は load balancing policy の名前と任意の option です。デフォルト: `random`。

  hashing を伴う policy では、[highest-random-weight (HRW)](https://en.wikipedia.org/wiki/Rendezvous_hashing) algorithm を使い、upstream 一覧が変わっても、同じ hash key を持つ client または request が同じ upstream に map されるようにします。

  一部の policy は、明記されている場合、option として fallback をサポートします。その場合、`fallback <policy>` を含む [block](/docs/caddyfile/concepts#blocks) を取り、別の load balancing policy を指定します。これらの policy では、デフォルト fallback は `random` です。fallback を設定すると、primary が選択できない場合に secondary policy を使えるため、強力な組み合わせを作れます。必要であれば fallback は複数段 nest できます。
  
  たとえば、`header` を primary として使い、developer が特定 upstream を選べるようにし、他のすべての connection では `first` fallback によって primary/secondary failover を実装できます。
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` は upstream をランダムに選びます

	- `random_choose <n>` は 2 つ以上の upstream をランダムに選び、その中で負荷が最も小さい 1 つを選びます（`n` は通常 2）

	- `first` は設定で定義された順に、最初に利用可能な upstream を選びます。primary/secondary failover に使えます。これと一緒に health check を有効にすることを忘れないでください。そうしないと failover は発生しません

	- `round_robin` は各 upstream を順番に反復します

	- `weighted_round_robin <weights...>` は、指定された weight を尊重しながら各 upstream を順番に反復します。weight 引数の数は、設定された upstream の数と一致する必要があります。weight は非負の integer である必要があります。たとえば 2 つの upstream と weight `5 1` の場合、最初の upstream が 5 回連続で選ばれ、その後 2 番目の upstream が 1 回選ばれ、その cycle が繰り返されます。weight に 0 を使うと、その upstream は新しいリクエストで選ばれなくなります

	- `least_conn` は現在のリクエスト数が最も少ない upstream を選びます。最少リクエスト数の host が複数ある場合、その中からランダムに 1 つが選ばれます

	- `ip_hash` は remote IP（直接の peer）を sticky upstream に map します

	- `client_ip_hash` は client IP を sticky upstream に map します。これは実 client IP parsing を有効にする [`servers > trusted_proxies` global option](/docs/caddyfile/options#trusted-proxies) と組み合わせるのが最適です。そうしない場合、`ip_hash` と同じ挙動になります

	- `uri_hash` は request URI（path と query）を sticky upstream に map します

	- `query [key]` は、query value を hash することで request query を sticky upstream に map します。指定した key が存在しない場合、fallback policy によって upstream が選択されます（デフォルトは `random`）

	- `header [field]` は、header value を hash することで request header を sticky upstream に map します。指定した header field が存在しない場合、fallback policy によって upstream が選択されます（デフォルトは `random`）

	- `cookie [<name> [<secret>]]` は、client からの最初のリクエスト（cookie がない場合）では、fallback policy によって upstream を選択します（デフォルトは `random`）。また、レスポンスに `Set-Cookie` header が追加されます（cookie 名が指定されない場合のデフォルトは `lb`）。cookie value は、選択された upstream の dial address を HMAC-SHA256 で hash したものです（`<secret>` を shared secret として使用し、未指定なら空文字列）。
	
	  cookie が存在する後続リクエストでは、利用可能であれば cookie value は同じ upstream に map されます。利用不可または見つからない場合は、fallback policy で新しい upstream が選択され、cookie がレスポンスに追加されます。

	  debug 目的で特定の upstream を使いたい場合は、secret で upstream address を hash し、その cookie を HTTP client（browser など）に設定できます。たとえば PHP では、`10.1.0.10:8080` が upstream の 1 つの address で、`secret` が設定済み secret である場合、次のように cookie value を計算できます。
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```
	
	  たとえば `lb` という名前の cookie を設定するには、browser の Javascript console から次のように設定できます。
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries** <span id="lb_retries"/> は、次に利用可能な host が down している場合に、各リクエストで利用可能な backend を選択し直す retry 回数です。デフォルトでは retry は無効（zero）です。

  [`lb_try_duration`](#lb_try_duration) も設定されている場合、その duration に到達すると retry は早期に停止することがあります。言い換えると、retry duration は retry count より優先されます。

- **lb_try_duration** <span id="lb_try_duration"/> は、次に利用可能な host が down している場合に、各リクエストで利用可能な backend を選択しようとする時間を定義する [duration value](/docs/conventions#durations) です。デフォルトでは retry は無効（zero duration）です。

  load balancer が利用可能な upstream host を探している間、client は最大でこの時間まで待ちます。HTTP transport のデフォルト dial timeout は `3s` なので、最初に選ばれた upstream に到達できない場合でも少なくとも 1 回 retry できるよう、妥当な開始点は `5s` かもしれません。ただし、ユースケースに合う balance を見つけるために自由に試してください。

- **lb_try_interval** <span id="lb_try_interval"/> は、pool から次の host を選択するまでの待ち時間を定義する [duration value](/docs/conventions#durations) です。デフォルトは `250ms` です。upstream host へのリクエストが失敗した場合にのみ関係します。非ゼロの `lb_try_duration` とともにこれを `0` に設定すると、すべての backend が down していて latency が非常に低い場合に CPU が spin する可能性があることに注意してください。

- **lb_retry_match** <span id="lb_retry_match"/> は、retry が許可される request を制限します。upstream への接続は成功したが、その後の round-trip が失敗した場合、retry されるには request がこの条件に一致する必要があります。upstream への接続自体が失敗した場合、retry は常に許可されます。デフォルトでは `GET` request だけが retry されます。

  この option の構文は [named request matchers](/docs/caddyfile/matchers#named-matchers) と同じですが、`@name` は使いません。単一の matcher だけが必要な場合、同じ行で設定できます。複数の matcher には block が必要です。



<a id="active-health-checks"></a>
### Active health checks

Active health check は timer によって background で health checking を実行します。これを有効にするには、`health_uri` または `health_port` が必要です。

- **health_uri** <span id="health_uri"/> は active health check 用の URI path（および任意の query）です。

- **health_upstream** <span id="health_upstream"/> は、upstream と異なる場合に active health check に使う ip:port です。これは `health_header` と `{http.reverse_proxy.active.target_upstream}` と組み合わせて使うべきです。

- **health_port** <span id="health_port"/> は、upstream の port と異なる場合に active health check に使う port です。`health_upstream` が使われている場合は無視されます。

- **health_interval** <span id="health_interval"/> は、active health check を実行する頻度を定義する [duration value](/docs/conventions#durations) です。デフォルト: `30s`。

- **health_passes** <span id="health_passes"/> は、backend を再び healthy と mark する前に必要な連続成功 health check 数です。デフォルト: `1`。

- **health_fails** <span id="health_fails"/> は、backend を unhealthy と mark する前に必要な連続失敗 health check 数です。デフォルト: `1`。

- **health_timeout** <span id="health_timeout"/> は、backend を down と mark する前に reply を待つ時間を定義する [duration value](/docs/conventions#durations) です。デフォルト: `5s`。

- **health_method** <span id="health_method"/> は、active health check に使う HTTP method です。デフォルト: `GET`。

- **health_status** <span id="health_status"/> は、healthy な backend から期待する HTTP status code です。3 桁の status code、または `xx` で終わる status code class を指定できます。例: `200`（デフォルト）、または `2xx`。

- **health_request_body** <span id="health_request_body"/> は、active health check で送信する request body を表す string です。

- **health_body** <span id="health_body"/> は、active health check の response body に一致させる substring または regular expression です。backend が一致する body を返さない場合、down と mark されます。

- **health_follow_redirects** <span id="health_follow_redirects"/> は、health check が upstream から提供された redirect を follow するようにします。デフォルトでは、redirect response は health check の fail として数えられます。

- **health_headers** <span id="health_headers"/> は、active health check request に設定する header を指定できます。`Host` header を変更する必要がある場合や、health check の一部として backend に authentication を提供する必要がある場合に便利です。



<a id="passive-health-checks"></a>
### Passive health checks

Passive health check は、実際に proxy された request の inline で発生します。これを有効にするには、`fail_duration` が必要です。

- **fail_duration** <span id="fail_duration"/> は、失敗した request を記憶する時間を定義する [duration value](/docs/conventions#durations) です。duration > `0` で passive health checking が有効になります。デフォルトは `0`（off）です。unhealthy な upstream を online に戻す際、error rate と responsiveness の balance を取る妥当な開始点は `30s` かもしれません。ただし、ユースケースに合う balance を見つけるために自由に試してください。

- **max_fails** <span id="max_fails"/> は、backend を down とみなす前に `fail_duration` 内で必要な failed request の最大数です。`>= 1` である必要があります。デフォルトは `1` です。

- **unhealthy_status** <span id="unhealthy_status"/> は、response がこれらの status code のいずれかで返ってきた場合、その request を failed と数えます。3 桁の status code、または `xx` で終わる status code class を指定できます。例: `404` または `5xx`。

- **unhealthy_latency** <span id="unhealthy_latency"/> は、response を得るまでにこの時間がかかった場合、その request を failed と数える [duration value](/docs/conventions#durations) です。

- **unhealthy_request_count** <span id="unhealthy_request_count"/> は、backend を down と mark する前に許容される同時 request 数です。言い換えると、特定の backend が現在この数の request を処理している場合、それは「overloaded」とみなされ、代わりに他の backend が優先されます。

  これは十分に大きな数であるべきです。これを設定すると、proxy には `unhealthy_request_count × upstreams_count` の合計同時 request 数の上限ができ、それを超えた request は利用可能な upstream がないため error になります。


<a id="events"></a>
## Events

upstream が healthy から unhealthy、またはその逆に遷移すると、[event](/docs/caddyfile/options#event-options) が発行されます。これらの event は、notification の送信や message の logging など、他の action を trigger するために使えます。event は次のとおりです。

- `healthy` は、以前 unhealthy だった upstream が healthy と mark されたときに発行されます
- `unhealthy` は、以前 healthy だった upstream が unhealthy と mark されたときに発行されます

どちらの場合も、状態が変わった upstream を識別するために、`host` が event の metadata として含まれます。たとえば `exec` event handler では `{event.data.host}` placeholder として使えます。



<a id="streaming"></a>
## Streaming

デフォルトでは、proxy は wire efficiency のために response を部分的に buffer します。

proxy は WebSocket connection もサポートします。HTTP upgrade request を実行し、その後 connection を bidirectional tunnel に移行します。

<aside class="tip">

デフォルトでは、config が reload されると WebSocket connection は強制的に閉じられます（Close control message が client と upstream の両方に送信されます）。各 request は config への reference を保持するため、memory usage を抑えるには古い connection を閉じる必要があります。この close behavior は [`stream_timeout`](#stream_timeout) と [`stream_close_delay`](#stream_close_delay) option で custom できます。

</aside>

- **flush_interval** <span id="flush_interval"/> は、Caddy が response buffer を client へ flush する頻度を調整する [duration value](/docs/conventions#durations) です。デフォルトでは periodic flushing は行われません。負の値（通常は -1）は「low-latency mode」を示し、response buffering を完全に無効化して client への各 write 後すぐに flush します。また、client が早期に disconnect しても backend への request を cancel しません。response が次のいずれかに該当する場合、この option は無視され、response はすぐに client へ flush されます。
	- `Content-Type: text/event-stream`
	- `Content-Length` が不明
	- proxy の両側が HTTP/2、`Content-Length` が不明、かつ `Accept-Encoding` が未設定または "identity"

- **request_buffers** <span id="request_buffers"/> は、upstream へ送信する前に request body から最大 `<size>` bytes を buffer に読み取るよう proxy に指示します。これは非常に非効率であり、upstream が遅延なく request body を読む必要がある場合にのみ行うべきです（本来は upstream application が修正すべきです）。[go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) がサポートするすべての size format を受け付けます。

- **response_buffers** <span id="response_buffers"/> は、client へ返す前に response body から最大 `<size>` bytes を buffer に読み取るよう proxy に指示します。performance 上の理由から可能な限り避けるべきですが、backend の memory 制約が厳しい場合には役立つことがあります。[go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) がサポートするすべての size format を受け付けます。

- **stream_timeout** <span id="stream_timeout"/> は、WebSocket などの streaming request が timeout 終了時に強制的に閉じられるまでの [duration value](/docs/conventions#durations) です。これは、connection が長く開いたままの場合に実質的に cancel します。1 日より古い connection を取り除くために、妥当な開始点は `24h` かもしれません。デフォルト: timeout なし。

- **stream_close_delay** <span id="stream_close_delay"/> は、config が unload されたときに WebSocket などの streaming request が強制的に閉じられるのを遅らせる [duration value](/docs/conventions#durations) です。代わりに、delay が完了するまで stream は開いたままになります。言い換えると、これを有効にすると Caddy の config reload 時に stream が即座に閉じられるのを防げます。以前の config によって connection を閉じられた client が一斉に reconnect する thundering herd を避けるため、有効にするとよい場合があります。妥当な開始点は、config reload 後に user が自然にページを離れるまで 5 分待てるように `5m` などかもしれません。デフォルト: delay なし。



<a id="headers"></a>
## Headers

proxy は自身と backend の間で **header を操作**できます。

- **header_up** <span id="header_up"/> は、backend へ向かう request header に対して、設定、追加（`+` prefix）、削除（`-` prefix）、または置換（検索と置換の 2 引数を使う）を行います。

- **header_down** <span id="header_down"/> は、backend から downstream へ来る response header に対して、設定、追加（`+` prefix）、削除（`-` prefix）、または置換（検索と置換の 2 引数を使う）を行います。

たとえば、既存の値を上書きして request header を設定します。

```caddy-d
header_up Some-Header "the value"
```

response header を追加します。header field には複数の値が存在し得ることに注意してください。

```caddy-d
header_down +Some-Header "first value"
header_down +Some-Header "second value"
```

request header を削除し、backend に到達しないようにします。

```caddy-d
header_up -Some-Header
```

suffix match を使って、一致するすべての request header を削除します。

```caddy-d
header_up -Some-*
```

必要なものだけを個別に追加できるよう、request header を*すべて*削除します（非推奨）。

```caddy-d
header_up -*
```

request header に対して正規表現置換を行います。

```caddy-d
header_up Some-Header "^prefix-([A-Za-z0-9]*)$" "replaced-$1-suffix"
```

使われる正規表現言語は Go に含まれる RE2 です。[RE2 syntax reference](https://github.com/google/re2/wiki/Syntax) と [Go regexp syntax overview](https://pkg.go.dev/regexp/syntax) を参照してください。置換文字列は [expanded](https://pkg.go.dev/regexp#Regexp.Expand) されるため、たとえば `$1` を最初の capture group として、captured value を使えます。


<a id="defaults"></a>
### Defaults

デフォルトでは、Caddy は `Host` を含む incoming header を変更せずに backend へ渡します。ただし、3 つの例外があります。

- [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For) header field を設定または拡張します。
- [`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto) header field を設定します。
- [`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host) header field を設定します。

<span id="trusted_proxies"/> これらの `X-Forwarded-*` header について、proxy はデフォルトで incoming request の値を無視し、spoofing を防ぎます。

Caddy が client から接続される最初の server ではない場合（たとえば Caddy の前に CDN がある場合）、これらの header について正しい値を送信したと信頼する incoming request の IP range（CIDR）一覧を `trusted_proxies` に設定できます。

proxy 内ではなく [`servers > trusted_proxies` global option](/docs/caddyfile/options#trusted-proxies) で設定することを強く推奨します。そうすれば server 内のすべての proxy handler に適用され、client IP parsing が有効になる利点もあります。

<aside class="tip">

Caddy の前で Cloudflare を使っている場合、`X-Forwarded-For` header の spoofing に対して脆弱になる可能性があることに注意してください。[Authelia](https://www.authelia.com) の友人たちが、Cloudflare にこの header の incoming value を無視させるための [workaround](https://www.authelia.com/integration/proxies/forwarded-headers/) を文書化しています。

</aside>

さらに、[`http` transport](#the-http-transport) を使う場合、client からの request に `Accept-Encoding: gzip` header がない場合は設定されます。これにより、upstream は可能であれば compressed content を返せます。この挙動は transport の [`compression off`](#compression) で無効化できます。


<a id="https"></a>
### HTTPS

proxy 時に（ほとんどの）header は元の値を保持するため、HTTPS へ proxy する場合、`Host` header が TLS ServerName value と一致するよう、設定された upstream address で `Host` header を上書きする必要があることがよくあります。

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

Caddy v2.11.0 以降、これは自動的に行われるため、HTTPS へ proxy するときに `Host` header を明示的に上書きする必要はなくなりました。この挙動を無効にしたい場合は、`Host` header を元の値に設定できます（ただし、そうする意味があることはほとんどありません）。

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

`X-Forwarded-Host` header は依然として [デフォルト](#defaults) で渡されるため、upstream が元の `Host` header value を知る必要がある場合はそれを使えます。

Caddy で TLS を終端し、HTTP 経由で port または unix socket へ proxy する場合も同じです。実際、`reverse_proxy` の target が caddy 自身である場合、caddy 自身が正しい Host を受け取る必要があります。unix socket の場合、`upstream_hostport` は socket path になるため、Host は明示的に設定する必要があります。



<a id="rewrites"></a>
## Rewrites

デフォルトでは、Caddy は `reverse_proxy` に到達する前の middleware chain で rewrite が行われていない限り、incoming request と同じ HTTP method と URI で upstream request を実行します。

proxy する前に request は clone されます。これにより、handler 中に request へ加えた変更が他の handler に漏れないことが保証されます。これは proxy 後も handling を継続する必要がある状況で便利です。

[header 操作](#headers)に加えて、upstream へ送信する前に request の method と URI を変更できます。

- **method** <span id="method"/> は clone された request の HTTP method を変更します。method が `GET` または `HEAD` に変更された場合、この handler は incoming request の body を upstream へ送信*しません*。別の handler に request body を消費させたい場合に便利です。
- **rewrite** <span id="rewrite"/> は clone された request の URI（path と query）を変更します。これは [`rewrite` ディレクティブ](/docs/caddyfile/directives/rewrite)に似ていますが、この handler の scope を超えて rewrite が維持されることはありません。

これらの rewrite は、「pre-check request」のような pattern でよく役立ちます。現在の request の処理をどう継続するか判断するため、別の server に request を送る pattern です。

たとえば、request を authentication gateway に送信し、その request が認証済み user からのものか（例: session cookie を持つ）を判断し、処理を継続するか、代わりに login page へ redirect するかを決められます。この pattern について、Caddy は設定 boilerplate の大半を省く shortcut ディレクティブ [`forward_auth`](/docs/caddyfile/directives/forward_auth) を提供します。




<a id="transports"></a>
## Transports

Caddy の proxy **transport** は pluggable です。

- **transport** <span id="transport"/> は backend との通信方法を定義します。デフォルトは `http` です。


<a id="the-http-transport"></a>
### `http` transport

```caddy-d
transport http {
	read_buffer             <size>
	write_buffer            <size>
	max_response_header     <size>
	proxy_protocol          v1|v2
	dial_timeout            <duration>
	dial_fallback_delay     <duration>
	response_header_timeout <duration>
	expect_continue_timeout <duration>
	resolvers <ip...>
	tls
	tls_client_auth <automate_name> | <cert_file> <key_file>
	tls_insecure_skip_verify
	tls_curves <curves...>
	tls_timeout <duration>
	tls_trust_pool <module>
	tls_server_name <server_name>
	tls_renegotiation <level>
	tls_except_ports <ports...>
	keepalive [off|<duration>]
	keepalive_interval <interval>
	keepalive_idle_conns <max_count>
	keepalive_idle_conns_per_host <count>
	versions <versions...>
	compression off
	max_conns_per_host <count>
	network_proxy <module>
}
```

- **read_buffer** <span id="read_buffer"/> は read buffer のサイズを bytes 単位で指定します。[go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) がサポートするすべての形式を受け付けます。デフォルト: `4KiB`。

- **write_buffer** <span id="write_buffer"/> は write buffer のサイズを bytes 単位で指定します。[go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) がサポートするすべての形式を受け付けます。デフォルト: `4KiB`。

- **max_response_header** <span id="max_response_header"/> は response header から読み取る最大 bytes 数です。[go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) がサポートするすべての形式を受け付けます。デフォルト: `10MiB`。

- **proxy_protocol** <span id="proxy_protocol"/> は upstream への connection で [PROXY protocol](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt)（HAProxy によって普及）を有効にし、real client IP data を先頭に付加します。Caddy が別の proxy の背後にある場合は、[`servers > trusted_proxies` global option](/docs/caddyfile/options#trusted-proxies) と組み合わせるのが最適です。version `v1` と `v2` がサポートされています。upstream server が PROXY protocol を parse できることが分かっている場合にのみ使ってください。デフォルトでは無効です。

- **dial_timeout** <span id="dial_timeout"/> は upstream socket への接続時に待つ最大 [duration](/docs/conventions#durations) です。デフォルト: `3s`。

- **dial_fallback_delay** <span id="dial_fallback_delay"/> は RFC 6555 Fast Fallback connection を起動するまで待つ最大 [duration](/docs/conventions#durations) です。負の値はこれを無効にします。デフォルト: `300ms`。

- **response_header_timeout** <span id="response_header_timeout"/> は upstream から response header を読むまで待つ最大 [duration](/docs/conventions#durations) です。デフォルト: timeout なし。

- **expect_continue_timeout** <span id="expect_continue_timeout"/> は、request に `Expect: 100-continue` header がある場合、request header を完全に書き込んだ後に upstream の最初の response header を待つ最大 [duration](/docs/conventions#durations) です。デフォルト: timeout なし。

- **read_timeout** <span id="read_timeout"/> は backend からの次の read を待つ最大 [duration](/docs/conventions#durations) です。デフォルト: timeout なし。

- **write_timeout** <span id="write_timeout"/> は backend への次の write を待つ最大 [duration](/docs/conventions#durations) です。デフォルト: timeout なし。

- **resolvers** <span id="resolvers"/> は system resolver を上書きする DNS resolver の一覧です。

- **tls** <span id="tls"/> は backend との通信に HTTPS を使います。`https://` scheme で backend を指定した場合、または下記の `tls_*` option のいずれかが設定された場合、自動的に有効になります。

- **tls_client_auth** <span id="tls_client_auth"/> は、2 つの方法のいずれかで TLS client authentication を有効にします。(1) Caddy が証明書を取得し更新し続ける domain name を指定する、または (2) backend との TLS client authentication で提示する certificate file と key file を指定する方法です。

- **tls_insecure_skip_verify** <span id="tls_insecure_skip_verify"/> は TLS handshake verification を無効にし、connection を insecure にして man-in-the-middle attack に脆弱にします。*production では使用しないでください。*

- **tls_curves** <span id="tls_curves"/> は upstream connection でサポートする elliptic curve の一覧です。Caddy のデフォルトは modern で secure なので、特定の要件がある場合にのみ設定が必要です。

- **tls_timeout** <span id="tls_timeout"/> は TLS handshake 完了を待つ最大 [duration](/docs/conventions#durations) です。デフォルト: timeout なし。

- **tls_trust_pool** <span id="tls_trust_pool"/> は、`tls` ディレクティブのドキュメントで説明されている [`trust_pool` サブディレクティブ](/docs/caddyfile/directives/tls#trust_pool) と同様に、信頼する certificate authority の source を設定します。標準の Caddy installation で利用できる trust pool source の一覧は [こちら](/docs/caddyfile/directives/tls#trust-pool-providers) です。

- **tls_server_name** <span id="tls_server_name"/> は、TLS handshake で受け取った certificate を検証するときに使う server name を設定します。デフォルトでは upstream address の host 部分を使います。

  upstream address が upstream の使う certificate と一致しない場合にのみ、これを上書きする必要があります。たとえば upstream address が IP address の場合、upstream server が提供する hostname に設定する必要があります。

  request placeholder を使えます。その場合、HTTP transport config の clone が各 request で使われるため、performance penalty が発生する可能性があります。

- **tls_renegotiation** <span id="tls_renegotiation"/> は TLS renegotiation level を設定します。TLS renegotiation とは、最初の handshake 後に追加の handshake を実行することです。level は次のいずれかです。
  - `never`（デフォルト）は renegotiation を無効にします。
  - `once` は remote server が connection ごとに 1 回 renegotiation を要求することを許可します。
  - `freely` は remote server が renegotiation を繰り返し要求することを許可します。

- **tls_except_ports** <span id="tls_except_ports"/> は、TLS が有効なとき、upstream target が指定された port のいずれかを使う場合、その connection では TLS を無効にします。一部の upstream は HTTP を期待し、他の upstream は HTTPS request を期待するような dynamic upstream 設定で役立つことがあります。

- **keepalive** <span id="keepalive"/> は `off`、または connection を開いたままにする時間（timeout）を指定する [duration value](/docs/conventions#durations) です。デフォルト: `2m`。

  ⚠️ keepalive duration が upstream server の keepalive timeout を超える場合、HTTP/1.1 upstream への request は "connection reset by peer" error により失敗することがあります。冪等な request は Go の HTTP transport により retry されますが、それ以外の場合 Caddy は status code 502 で応答します。

- **keepalive_interval** <span id="keepalive_interval"/> は liveness probe 間の [duration](/docs/conventions#durations) です。デフォルト: `30s`。

- **keepalive_idle_conns** <span id="keepalive_idle_conns"/> は alive に保持する connection の最大数を定義します。デフォルト: 制限なし。

- **keepalive_idle_conns_per_host** <span id="keepalive_idle_conns_per_host"/> は非ゼロの場合、host ごとに保持する idle（keep-alive）connection の最大数を制御します。デフォルト: `32`。

- **versions** <span id="versions"/> は、サポートする HTTP version を custom できます。
  
  有効な option: `1.1`, `2`, `h2c`, `3`。

  デフォルト: `1.1 2`。または [upstream scheme](#upstream-addresses) が `h2c://` の場合、デフォルトは `h2c 2` です。

  `h2c` は upstream への cleartext HTTP/2 connection を有効にします。これは Go のデフォルト HTTP transport を使わない非標準機能であるため、他の機能とは排他的です。

  `3` は upstream への HTTP/3 connection を有効にします。⚠️ これは experimental feature であり、変更される可能性があります。

- **compression** <span id="compression"/> は、`off` に設定することで backend への compression を無効化できます。

- **max_conns_per_host** <span id="max_conns_per_host"/> は、dialing、active、idle 状態の connection を含む、host ごとの total connection 数を任意で制限します。デフォルト: 制限なし。

- **network_proxy** <span id="network_proxy"/> は、upstream server への request に使う network proxy module の名前を指定します。明示的に設定されていない場合、Caddy は [Go stdlib](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment) に従い、環境変数で設定された proxy、つまり `HTTP_PROXY`、`HTTPS_PROXY`、`NO_PROXY` を尊重します。この parameter に値が指定された場合、request は次の順に reverse proxy を通過します: Client（users）→ `reverse_proxy` → `network_proxy` → upstream。組み込み module は次のとおりです。
	- `none` は、`HTTP_PROXY`、`HTTPS_PROXY`、`NO_PROXY` の環境設定を無視するために使います。
	- `url <url>` は、環境設定を上書きする単一 URL を指定するために使います。

<a id="the-fastcgi-transport"></a>
### `fastcgi` transport

```caddy-d
transport fastcgi {
	root  <path>
	split <at>
	env   <key> <value>
	resolve_root_symlink
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>
	capture_stderr
}
```

- **root** <span id="root"/> は site の root です。デフォルト: `{http.vars.root}` または現在の working directory。

- **split** <span id="split"/> は、URI の末尾で PATH_INFO を得るために path を分割する位置です。

- **env** <span id="env"/> は、追加の environment variable を指定値に設定します。複数の environment variable に対して複数回指定できます。

- **resolve_root_symlink** <span id="resolve_root_symlink"/> は、`root` directory に symbolic link が存在する場合、それを評価して実際の値へ解決することを有効にします。

- **dial_timeout** <span id="dial_timeout"/> は upstream socket への接続時に待つ時間です。[duration values](/docs/conventions#durations) を受け付けます。デフォルト: `3s`。

- **read_timeout** <span id="read_timeout"/> は FastCGI server から読み取るときに待つ時間です。[duration values](/docs/conventions#durations) を受け付けます。デフォルト: timeout なし。

- **write_timeout** <span id="write_timeout"/> は FastCGI server へ送信するときに待つ時間です。[duration values](/docs/conventions#durations) を受け付けます。デフォルト: timeout なし。

- **capture_stderr** <span id="capture_stderr"/> は upstream fastcgi server が `stderr` に送った message の capture と logging を有効にします。logging はデフォルトで `WARN` level で行われます。response が `4xx` または `5xx` status の場合は、代わりに `ERROR` level が使われます。デフォルトでは `stderr` は無視されます。

<aside class="tip">

modern PHP application を配信しようとしている場合、探しているのは [`php_fastcgi` ディレクティブ](/docs/caddyfile/directives/php_fastcgi) かもしれません。これは、`index.php` を routing entrypoint として使うために必要な rewrite を含む、`fastcgi` ディレクティブを使った proxy の shortcut です。

</aside>



<a id="intercepting-responses"></a>
## レスポンスの intercept

reverse proxy は backend からの response を intercept するよう設定できます。これを可能にするため、[response matcher](/docs/caddyfile/response-matchers) を定義できます（request matcher の構文に似ています）。最初に一致した `handle_response` route が呼び出されます。

response handler が呼び出されると、backend からの response は client に書き込まれず、設定された `handle_response` route が代わりに実行されます。その route が response を書き込む責任を持ちます。route が response を書き込ま*ない*場合、request handling はこの `reverse_proxy` の [後に並べられた](/docs/caddyfile/directives#directive-order) handler で継続します。

- **@name** は [response matcher](/docs/caddyfile/response-matchers) の名前です。各 response matcher が一意の名前を持つ限り、複数の matcher を定義できます。response は status code と response header の有無または値で match できます。

- **replace_status** <span id="replace_status"/> は、指定された matcher に一致したとき、response の status code を単に変更します。

- **handle_response** <span id="handle_response"/> は、指定された matcher に一致したとき（または matcher が省略された場合はすべての response で）実行する route を定義します。最初に一致した block が適用されます。`handle_response` block の中では、他の任意の [directives](/docs/caddyfile/directives) を使用できます。

さらに、`handle_response` 内では 2 つの特別な handler directive を使用できます。

- **copy_response** <span id="copy_response"/> は、backend から受け取った response body を client へ copy します。その際、任意で response の status code を変更できます。このディレクティブは [`respond` より前に並べられます](/docs/caddyfile/directives#directive-order)。

- **copy_response_headers** <span id="copy_response_headers"/> は、backend からの response header を client へ copy します。任意で header field の一覧を include *または* exclude できます（`include` と `exclude` の両方は指定できません）。このディレクティブは [`header` より後に並べられます](/docs/caddyfile/directives#directive-order)。

`handle_response` route 内では、3 つの placeholder が利用可能になります。

- `{rp.status_code}` backend response の status code。

- `{rp.status_text}` backend response の status text。

- `{rp.header.*}` backend response の header。

reverse proxy response handler は、proxy から受け取った新しい response を client へ copy できますが、その新しい response を後続の reverse proxy に渡すことはできません。`reverse_proxy` の各使用は、original request の body（または別の module によって変更された body）を受け取ります。




<a id="examples"></a>
## 例

すべての request を local backend に reverse proxy します。

```caddy
example.com {
	reverse_proxy localhost:9005
}
```


すべての request を [3 つの backend 間](#upstreams)で [load-balance](#load-balancing) します。

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```


同じですが、`/api` 内の request だけを対象にし、[`cookie` policy](#lb_policy) を使って sticky にします。

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```


[active health check](#active-health-checks) を使って healthy な backend を判定し、failed connection では [retry](#lb_try_duration) を有効にして、healthy な backend が見つかるまで request を保持します。

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```


いくつかの [transport option](#transports) を設定します。

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```


[HTTPS upstream](#https) へ reverse proxy します（v2.11.0 以降、Caddy は `Host` header を upstream の host と一致するよう自動設定するため、手動で行う必要はなくなりました）。

```caddy
example.com {
	reverse_proxy https://example.com
}
```


HTTPS upstream へ reverse proxy しますが、[⚠️ TLS verification を無効化](#tls_insecure_skip_verify)します。これは推奨されません。HTTPS が提供するすべての security check を無効にするためです。可能であれば private network では HTTP で proxy する方が望ましいです。security の錯覚を避けられるからです。

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```


代わりに、upstream の certificate を明示的に [trust](#tls_trust_pool) し、（任意で）TLS-SNI を upstream certificate 内の hostname と一致するよう設定することで、upstream との信頼を確立できます。

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /path/to/cert.pem
			tls_server_name app.example.com
		}
	}
}
```



proxy 前に [path prefix を strip](handle_path) します。ただし [subfolder problem <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575) に注意してください。

```caddy
example.com {
	handle_path /prefix/* {
		reverse_proxy localhost:9000
	}
}
```


[`rewrite`](/docs/caddyfile/directives/rewrite) を使って、proxy 前に path prefix を置換します。

```caddy
example.com {
	handle_path /old-prefix/* {
		rewrite /new-prefix{path}
		reverse_proxy localhost:9000
	}
}
```


`X-Accel-Redirect` support、つまり [response を intercept](#intercepting-responses) して、要求された静的ファイルを配信します。

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {rp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```


upstream からの error について、status code によって [error response を intercept](#intercepting-responses) し、custom error page を返します。

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root /path/to/error/pages
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```


[`A`/`AAAA` record](#aaaaa) DNS query から [動的に](#dynamic-upstreams) backend を取得します。

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```


[`SRV` record](#srv) DNS query から [動的に](#dynamic-upstreams) backend を取得します。

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```


[active health check](#active-health-checks) と `health_upstream` は、より詳細な health check を行う intermediate service を作る場合に役立ちます。その場合、`{http.reverse_proxy.active.target_upstream}` を header として使い、health check service に original upstream を提供できます。

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
