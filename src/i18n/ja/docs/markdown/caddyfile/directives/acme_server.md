---
title: acme_server (Caddyfile directive)
---

# acme_server

組み込みの [ACME protocol](https://tools.ietf.org/html/rfc8555) サーバーハンドラです。これにより、ある Caddy インスタンスが他の ACME 互換ソフトウェア（他の Caddy インスタンスを含む）向けに証明書を発行できます。

有効にすると、パス `/acme/*` に一致するリクエストは ACME サーバーによって処理されます。


<a id="client-configuration"></a>
## クライアント設定

ACME サーバーのデフォルトを使う場合、ACME クライアントは ACME エンドポイントとして `https://localhost/acme/local/directory` を使うように設定するだけで十分です。（`local` は Caddy のデフォルト CA の ID です。）


<a id="syntax"></a>
## 構文

```caddy-d
acme_server [<matcher>] {
	ca         <id>
	lifetime   <duration>
	resolvers  <resolvers...>
	challenges <challenges...>
	allow_wildcard_names
	allow {
		domains <domains...>
		ip_ranges <addresses...>
	}
	deny {
		domains <domains...>
		ip_ranges <addresses...>
	}
}
```

- **ca** は、証明書の署名に使う認証局の ID を指定します。デフォルトは `local` で、これは Caddy のデフォルト CA です。ローカルで使う自己署名証明書を想定しており、開発環境で最もよく使われます。より広い用途では、混乱を避けるため別の CA を指定することを推奨します。指定した ID の CA がまだ存在しない場合は作成されます。代替 CA の設定については [PKI app global options](/docs/caddyfile/options#pki-options) を参照してください。

- **lifetime**（デフォルト: `12h`）は、発行される証明書の有効期間を指定する [duration](/docs/conventions#durations) です。この値は署名に使う [intermediate certificate](/docs/caddyfile/options#intermediate-lifetime) の有効期間より短くなければなりません。どうしても必要な場合を除き、変更は推奨されません。

- **resolvers** は、ACME DNS チャレンジの解決に必要な TXT レコードを検索するときに使う DNS リゾルバのアドレスです。[network addresses](/docs/conventions#network-addresses) を受け付け、指定がなければ UDP とポート 53 がデフォルトです。ホストが IP アドレスの場合は、upstream サーバーを解決するために直接ダイヤルされます。ホストが IP アドレスでない場合は、Go 標準ライブラリの [name resolution convention](https://golang.org/pkg/net/#hdr-Name_Resolution) に従ってアドレスが解決されます。複数のリゾルバを指定した場合は、そのうち 1 つがランダムに選ばれます。

- **challenges** は、有効にするチャレンジ種別を設定します。未設定の場合、または値なしでこの directive を使った場合は、すべてのチャレンジ種別が有効になります。受け付ける値は `http-01`、`tls-alpn-01`、`dns-01` です。

- **allow_wildcard_names** は、ワイルドカード SAN（Subject Alternative Name）を持つ証明書の発行を有効にします。

- **allow**、**deny** は `acme_server` の運用ポリシーを設定します。ポリシー評価は Step-CA が[ここ](https://smallstep.com/docs/step-ca/policies/#policy-evaluation)で説明している基準に従います。

	- **domains** は、ポリシー評価基準に従って許可または拒否する subject domain name を設定します。

	- **ip_ranges** は、ポリシー評価基準に従って許可または拒否する subject IP range を設定します。

<a id="examples"></a>
## 例

[`pki` global option](/docs/caddyfile/options#pki-options) で CA をカスタマイズし、`internal` issuer を使って自身の証明書を発行しながら、ドメイン `acme.example.com` で ID `home` の ACME サーバーを提供します。

```caddy
{
	pki {
		ca home {
			name "My Home CA"
		}
	}
}

acme.example.com {
	tls {
		issuer internal {
			ca home
		}
	}
	acme_server {
		ca home
	}
}
```

別の Caddy サーバーがある場合は、上の ACME サーバーを使って自身の証明書を発行できます。

```caddy
{
	acme_ca https://acme.example.com/acme/home/directory
	acme_ca_root /path/to/home_ca_root.crt
}

example.com {
	respond "Hello, world!"
}
```
