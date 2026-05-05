---
title: forward_auth (Caddyfile directive)
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.innerText.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// Fix uri subdirective, gets parsed as matcher arg because of "uri" directive
	$$_('.k').forEach(item => {
		if (item.innerText.includes('uri') && item.nextElementSibling && item.nextElementSibling.classList.contains('nd')) {
			const next = item.nextElementSibling;
			next.classList.remove('nd');
			next.classList.add('s');
			next.textContent = next.textContent;
		}
	});
});
</script>

# forward_auth

認証 gateway にリクエストの複製を proxy する、意見を持った directive です。認証 gateway は処理を続行してよいか、または login page へ送る必要があるかを判断できます。

- [構文](#syntax)
- [展開形](#expanded-form)
- [例](#examples)
  - [Authelia](#authelia)
  - [Tailscale](#tailscale)

Caddy の [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) は外部サービスへの "pre-check requests" を実行できますが、この directive は認証用途に特化しています。実際には、この directive はより長く一般的な設定（下記）を使うための便利なショートカットです。

この directive は、設定された upstream に対して、`uri` を書き換えた `GET` リクエストを行います。
- upstream が `2xx` status code で応答した場合、アクセスが許可され、`copy_headers` 内の header fields が元のリクエストへコピーされ、処理が続行されます。
- それ以外で、upstream が他の status code で応答した場合、upstream のレスポンスがクライアントへコピーされます。このレスポンスでは通常、認証 gateway の login page への redirect が行われます。

この動作が求めるものと正確に一致しない場合は、下の[展開形](#expanded-form)を土台にして、必要に応じてカスタマイズできます。

[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) のすべての subdirective がサポートされ、下位の `reverse_proxy` handler に渡されます。


<a id="syntax"></a>
## 構文

```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <to>
	copy_headers <fields...> {
		<fields...>
	}
}
```

- **&lt;upstreams...&gt;** は、認証リクエストの送信先となる upstream（backend）のリストです。

- **uri** は、upstream へ送られるリクエストに設定する URI（path と query）です。通常は認証 gateway の検証エンドポイントです。

- **copy_headers** は、リクエストが成功 status code の場合に、レスポンスから元のリクエストへコピーする HTTP header fields のリストです。

  field は `>` の後に新しい名前を書くことで rename できます。例: `Before>After`。

  読みやすさを優先する場合は、block を使って field を 1 行に 1 つずつ列挙できます。

この directive は reverse proxy の上にある意見を持った wrapper なので、[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax) の任意の subdirective を使ってカスタマイズできます。


<a id="expanded-form"></a>
## 展開形

`forward_auth` directive は次の設定と同じです。[Authelia](https://www.authelia.com/) のような Auth gateway は、この preset と相性よく動作します。自分の gateway が合わない場合は、`forward_auth` ショートカットを使う代わりに、ここから必要な部分を借りてカスタマイズしてください。

```caddy-d
reverse_proxy <upstreams...> {
	# 常に GET にして、受信した
	# request body が消費されないようにする
	method GET

	# URI を auth gateway の
	# 検証エンドポイントへ変更する
	rewrite <to>

	# 元の method と URI を転送する。
	# 上で書き換えられるため必要です。これは
	# reverse_proxy によって既に設定される他の X-Forwarded-*
	# header に追加されます
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# 成功レスポンスでは response header をコピーする
	@good status 2xx
	handle_response @good {
		# たとえば、copy_headers field ごとに...
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


<a id="examples"></a>
## 例


### Authelia

reverse proxy でアプリを提供する前に、認証を [Authelia](https://www.authelia.com/) へ委任します。

```caddy
# authentication gateway 自体を提供する
auth.example.com {
	reverse_proxy authelia:9091
}

# アプリを提供する
app1.example.com {
	forward_auth authelia:9091 {
		uri /api/authz/forward-auth
		copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
	}

	reverse_proxy app1:8080
}
```

詳細は、Caddy と統合するための [Authelia's documentation](https://www.authelia.com/integration/proxies/caddy/) を参照してください。


### Tailscale

認証を [Tailscale](https://tailscale.com/)（現在の名前は [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/) ですが、Caddy でも動作します）へ委任し、`copy_headers` の代替構文を使ってコピーした header を *rename* します（各 header 内の `>` に注目してください）。

```caddy-d
forward_auth unix//run/tailscale.nginx-auth.sock {
	uri /auth
	header_up Remote-Addr {remote_host}
	header_up Remote-Port {remote_port}
	header_up Original-URI {uri}
	copy_headers {
		Tailscale-User>X-Webauth-User
		Tailscale-Name>X-Webauth-Name
		Tailscale-Login>X-Webauth-Login
		Tailscale-Tailnet>X-Webauth-Tailnet
		Tailscale-Profile-Picture>X-Webauth-Profile-Picture
	}
}
```
