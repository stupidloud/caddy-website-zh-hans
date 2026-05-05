---
title: bind (Caddyfile directive)
---

# bind

サーバーのソケットが bind するインターフェイスを上書きします。

通常、listener は空の（ワイルドカード）インターフェイスに bind します。ただし、listener を別のホスト名または IP に強制的に bind できます。この directive が受け付けるのはホストのみで、ポートは受け付けません。ポートは [site address](/docs/caddyfile/concepts#addresses) によって決まります（デフォルトは `443`）。

サイト間で一貫性なく bind すると、意図しない結果になる場合があります。たとえば、同じポート上の 2 つのサイトがどちらも `127.0.0.1` に解決され、そのうち一方だけが `bind 127.0.0.1` で設定されている場合、アクセスできるサイトは 1 つだけになります。もう一方は特定のホストなしでそのポートに bind し、OS はより具体的に一致するソケットを選ぶためです。（Virtual host は異なる listener 間では共有されません。）

`bind` は [network addresses](/docs/conventions#network-addresses) を受け付けますが、ポートを含めることはできません。


<a id="syntax"></a>
## 構文

```caddy-d
bind <hosts...>
```

- **&lt;hosts...&gt;** は、listener を bind するホストインターフェイスのリストです。


<a id="examples"></a>
## 例

ソケットを現在のマシン上でのみアクセス可能にするには、ループバックインターフェイス（localhost）に bind します。

```caddy
example.com {
	bind 127.0.0.1
}
```

IPv6 も含めるには:

```caddy
example.com {
	bind 127.0.0.1 [::1]
}
```

`10.0.0.1:8080` に bind するには:

```caddy
example.com:8080 {
	bind 10.0.0.1
}
```

`/run/caddy` の Unix domain socket に bind するには:

```caddy
example.com {
	bind unix//run/caddy
}
```

ファイル権限をすべてのユーザーが書き込み可能に変更するには（[デフォルト](/docs/conventions#network-addresses)は `0200` で、所有者だけが書き込み可能です）:

```caddy
example.com {
	bind unix//run/caddy|0222
}
```

1 つのドメインを 2 つの異なるインターフェイスに bind し、それぞれ異なるレスポンスを返すには:

```caddy
example.com {
	bind 10.0.0.1
	respond "One"
}

example.com {
	bind 10.0.0.2
	respond "Two"
}
```
