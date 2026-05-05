---
title: tls (Caddyfile directive)
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# tls

site の TLS を設定します。

**Caddy のデフォルト TLS 設定は安全です。十分な理由があり、その影響を理解している場合にのみ、これらの設定を変更してください。** このディレクティブの最も一般的な用途は、ACME account email address の指定、ACME CA endpoint の変更、または独自の certificate の提供です。

互換性に関する注意: TLS は security protocol として機密性が高いため、新しい minor release や patch release で TLS default が意図的に調整されることがあります。古い、または壊れた TLS version、cipher、feature などはいつでも削除される可能性があります。deployment が変更に対して非常に敏感な場合は、一定に保つ必要がある値を明示的に指定し、upgrade に注意してください。ほとんどすべての場合、デフォルト設定の使用を推奨します。


<a id="syntax"></a>
## 構文

```caddy-d
tls [internal|force_automate|<email>] | [<cert_file> <key_file>] {
	protocols <min> [<max>]
	ciphers   <cipher_suites...>
	curves    <groups...>
	alpn      <values...>
	load      <paths...>
	ca        <ca_dir_url>
	ca_root   <pem_file>
	key_type  ed25519|p256|p384|rsa2048|rsa4096
	dns       <provider_name> [<params...>]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	eab       <key_id> <mac_key>
	on_demand
	reuse_private_keys
	client_auth {
		mode                   [request|require|verify_if_given|require_and_verify]
		trust_pool             <module>
		verifier 			   <module>
	}
	issuer          <issuer_name>  [<params...>]
	get_certificate <manager_name> [<params...>]
	insecure_secrets_log <log_file>
	renewal_window_ratio <ratio>
	force_automate
}
```

- **internal** は、この site の certificate を生成するために、Caddy の internal な locally-trusted CA を使うことを意味します。[`internal`](#internal) issuer をさらに設定するには、[`issuer`](#issuer) サブディレクティブを使います。

- **force_automate** は、他の managed certificate が適用される場合でも、Caddy に site の certificate automation を強制します。

- **&lt;email&gt;** は、site の certificate を管理する ACME account に使う email address です。すべての site に一括で設定するには、代わりに [`email` global option](/docs/caddyfile/options#email) を使う方がよい場合があります。

<aside class="tip">

Let's Encrypt は certificate の期限が近いことを email で知らせる場合がありますが、Caddy が renewal 時に別の issuer（例: ZeroSSL）を選んでいる場合、その email は誤解を招くことがあります。log や certificate 自体（たとえば browser 内）を確認し、どの issuer が使われたか、また有効期限がまだ有効かを確認してください。有効であれば、Let's Encrypt からの email は安全に無視できます。

</aside>

- **&lt;cert_file&gt;** と **&lt;key_file&gt;** は certificate と private key の PEM file への path です。片方だけを指定するのは無効です。

- **protocols** <span id="protocols"/> は最小および最大 protocol version を指定します。自分が何をしているか分かっている場合を除き、変更しないでください。Caddy は常に modern default を使うため、これを設定する必要はほとんどありません。
  
  デフォルト min: `tls1.2`, デフォルト max: `tls1.3`

- **ciphers** <span id="ciphers"/> は cipher suite 名の一覧を、優先度の高い順に指定します。自分が何をしているか分かっている場合を除き、変更しないでください。TLS 1.3 では cipher suite は custom できないこと、また TLS 1.2 のすべての cipher がデフォルトで有効なわけではないことに注意してください。サポートされる名前は次のとおりです（Go stdlib の優先順）。
	- `TLS_AES_128_GCM_SHA256`
	- `TLS_CHACHA20_POLY1305_SHA256`
	- `TLS_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA`

- **curves** <span id="curves"/> はサポートする EC group の一覧を指定します。デフォルトを変更しないことを推奨します。サポートされる値:
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> は、TLS handshake の [ALPN extension <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Glossary/ALPN) で advertise する値の一覧です。

- **load** <span id="load"/> は、certificate+key bundle である PEM file を読み込む folder の一覧を指定します。

- **ca** <span id="ca"/> は ACME CA endpoint を変更します。これは testing 時に [Let's Encrypt の staging endpoint <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) を設定する場合、または internal ACME server を使う場合に最もよく使われます。（Caddyfile 全体でこの値を変更するには、代わりに `acme_ca` [global option](/docs/caddyfile/options) を使ってください。）

- **ca_root** <span id="ca_root"/> は、system trust store にない場合に、ACME CA endpoint 用の trusted root certificate を含む PEM file を指定します。

- **key_type** <span id="key_type"/> は CSR 生成時に使う key の種類です。特定の要件がある場合にのみ設定してください。

- **dns** <span id="dns"/> は、指定された provider plugin を使って [DNS challenge](/docs/automatic-https#dns-challenge) を有効にします。この plugin は [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) repository のいずれかから組み込む必要があります。各 provider plugin は名前の後に独自の構文を持つ場合があります。詳細はそれぞれの docs を参照してください。各 DNS provider の support 維持は community effort です。[provider で DNS challenge を有効にする方法は wiki を参照してください。](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> は、DNS challenge 使用時に DNS TXT record が現れるまで待つ最大時間を設定する [duration value](/docs/conventions#durations) です。propagation check を無効化するには `-1` に設定します。デフォルトは 2 分です。

- **propagation_delay** <span id="propagation_delay"/> は、DNS challenge 使用時に DNS TXT record propagation check を開始する前に待つ時間を設定する [duration value](/docs/conventions#durations) です。デフォルトは `0`（待機なし）です。

- **dns_ttl** <span id="dns_ttl"/> は、DNS challenge で使う `TXT` record の TTL を設定する [duration value](/docs/conventions#durations) です。必要になることはまれです。

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> は、DNS challenge に使う domain を上書きします。これは challenge を別 domain に delegate するためのものです。

  primary domain の DNS provider に利用可能な [DNS plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) がない場合に使うとよいでしょう。代わりに、primary domain に `_acme-challenge` subdomain の `CNAME` record を追加し、plugin を*持っている* secondary domain を指すようにできます。この option は plugin からの特別な support を*必要としません*。
  
  ACME issuer が primary domain の DNS challenge を解決しようとすると、`CNAME` を辿って secondary domain にある `TXT` record を探します。

  **Note:** ここでは CNAME record からの完全な canonical name を値として使ってください。`_acme-challenge` subdomain は自動的には前置されません。

- **resolvers** <span id="resolvers"/> は、DNS challenge 実行時に使う DNS resolver を custom します。これは system resolver や任意の default resolver より優先されます。ここで設定すると、resolver は設定済みのすべての certificate issuer に伝播します。

  通常これは IP address の一覧です。たとえば [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns) を使う場合:

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> は、この site に対して、CA から提供された key ID と MAC key を使って ACME external account binding（EAB）を設定します。

- **on_demand** <span id="on_demand"/> は、site block の address に含まれる hostname に対して [On-Demand TLS](/docs/automatic-https#on-demand-tls) を有効にします。**Security warning:** production でこれを行うのは、abuse を緩和するために [`on_demand_tls` global option](/docs/caddyfile/options#on-demand-tls) も設定していない限り insecure です。

- **reuse_private_keys** <span id="reuse_private_keys"/> は、certificate renewal 時の private key 再利用を有効にします。デフォルトでは、pinning を緩和し key compromise の scope を小さくするため、新しい certificate ごとに新しい key が作成されます。Key pinning は業界の best practice に反します。この option は特定の理由がない限り推奨されません。将来の version で削除される可能性があります。

- **client_auth** <span id="client_auth"/> は TLS client authentication を有効化し設定します。
  - **mode** <span id="mode"/> は client を認証する mode です。許可される値:

    | Mode | Description |
    | --- | --- |
    | request | client に certificate を求めますが、なくても許可します。検証はしません |
    | require | client に certificate の提示を要求しますが、検証はしません |
    | verify_if_given | client に certificate を求めます。なくても許可しますが、あれば検証します |
    | require_and_verify | 検証済みの有効な certificate を client が提示することを要求します |

    デフォルト: `trust_pool` module が提供されている場合は `require_and_verify`、それ以外は `require`。
	
  - **trust_pool** <span id="trust_pool"/> は、client certificate の検証対象となる certificate を提供する certificate authority（CA）の source を設定します。
	
	trusted certificate の pool を提供する certificate authority と、その segment 内の設定は、設定された trust pool module の source によって異なります。Caddy で利用できる標準 module は [下に一覧](#trust-pool-providers) があります。3rd-party を含む module の完全な一覧は [`trust_pool` JSON documentation](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool) にあります。

    複数の CA または leaf certificate を指定するために、複数の `trusted_*` ディレクティブを使えます。leaf certificate の 1 つとして listed されておらず、指定された CA のいずれにも署名されていない client certificate は、**mode** に従って拒否されます。

  - **verifier** <span id="verifier"/> は custom client certificate verifier module の使用を有効にします。これらは、certificate が revoked されていないことを確認するなど、custom client authentication check を実行できます。

- **issuer** <span id="issuer"/> は custom certificate issuer、または certificate を取得する source を設定します。

  どの issuer が使われるか、およびこの segment に続く option は、利用可能な [issuer modules](#issuers) によって異なります。`ca` や `dns` など一部の他のサブディレクティブは、実際には `acme` issuer を設定する shortcut です（このサブディレクティブは後から追加されました）。そのため、このディレクティブとそれらのいくつかを同時に指定すると混乱を招くため、禁止されています。
  
  このサブディレクティブは複数回指定して、複数の冗長 issuer を設定できます。ある issuer が certificate の発行に失敗した場合、次の issuer が試されます。

- **get_certificate** <span id="get_certificate"/> は、handshake-time に [manager module](#certificate-managers) から certificate を取得することを有効にします。

- **insecure_secrets_log** <span id="insecure_secrets_log"/> は TLS secret を file へ logging することを有効にします。これは `SSLKEYLOGFILE` としても知られています。NSS key log format を使い、Wireshark などの tool で parse できます。⚠️ **Security Warning:** これは他の program や tool に TLS connection の decrypt を可能にし、security を完全に損なうため insecure です。ただし、この機能は debugging や troubleshooting には役立つ場合があります。

- **renewal_window_ratio** <span id="renewal_window_ratio"/> は、Caddy が certificate renewal を試みる前に残っている必要がある certificate lifetime を決める、0 から 1 の ratio です。たとえば certificate の lifetime が 90 日で、この ratio が `0.3333`（デフォルト値）の場合、Caddy は expiration まで 30 日以下になると継続的に certificate renewal を試みます。[`renewal_window_ratio` global option](/docs/caddyfile/options#renewal_window_ratio) で global に設定することもできます。

  これを変更する必要はほとんどありませんが、CA の issuance time が非常に長い場合に、certificate lifetime の後半で renewal するために役立つことがあります。

  ACME issuer は [ARI extension](https://datatracker.ietf.org/doc/rfc9773/) を実装している場合があるため、これは suggestion であることを覚えておいてください。ARI は ACME client（この場合は Caddy）が renewal を試みるべき window を指定し、その window はこの ratio と一致しないことがあります。

- **force_automate** は inline で指定する場合と同じです（上記参照）。

<a id="trust-pool-providers"></a>
### Trust Pool Providers

これらは `trust_pool` サブディレクティブで使える標準 trust pool provider です。

<a id="inline"></a>
#### inline

`inline` module は、Caddyfile に直接 listed された trusted root certificate を base64 DER-encoded format として parse します。`trust_der` ディレクティブは複数回繰り返せます。

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> は、client certificate の検証対象となる base64 DER-encoded CA certificate です。

<a id="file"></a>
#### file

`file` module は、disk 上の PEM file から trusted root certificate を読み取ります。`pem_file` ディレクティブは同じ行で複数の file path を受け付けられ、複数回繰り返せます。

```caddy-d
... file [<pem_file>...] {
	pem_file <pem_file>...
}
```

- **pem_file** <span id="pem_file"/> は、client certificate の検証対象となる PEM CA certificate file への path です。

<a id="pki_root"></a>
#### pki_root

`pki_root` module は、[PKI app](/docs/caddyfile/options#pki-options) で定義された certificate authority から *root* certificate を取得し、それを trust します。`authority` ディレクティブは複数の authority を同時に受け付けられ、複数回繰り返せます。

```caddy-d
... pki_root [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> は PKI app で設定された certificate authority の名前です。

<a id="pki_intermediate"></a>
#### pki_intermediate

`pki_intermediate` module は、[PKI app](/docs/caddyfile/options#pki-options) で定義された certificate authority から *intermediate* certificate を取得し、それを trust します。`authority` ディレクティブは複数の authority を同時に受け付けられ、複数回繰り返せます。

```caddy-d
... pki_intermediate [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> は PKI app で設定された certificate authority の名前です。

<a id="storage"></a>
#### storage

`storage` module は、Caddy [storage](/docs/caddyfile/options#storage) から trusted certificate root を抽出します。`authority` ディレクティブは複数の authority を同時に受け付けられ、複数回繰り返せます。

```caddy-d
... storage [<storage_keys>...] {
	storage <storage_module>
	keys    <storage_keys>...
}
```

- **storage** <span id="storage"/> は使用する任意の storage module です。指定しない場合、デフォルト storage module が使われます。指定する場合は 1 回だけ指定できます。

- **keys** <span id="keys"/> は certificate の PEM file が保存されている storage key の一覧です。このディレクティブは同じ行で複数の値を受け付けられ、複数回指定できます。

<a id="http"></a>
#### http

`http` module は HTTP endpoint から trusted certificate を取得します。`endpoints` ディレクティブは複数の endpoint を同時に受け付けられ、複数回繰り返せます。

```caddy-d
... http [<endpoints...>] {
	endpoints   <endpoints...>
	tls         <tls_config>
}
```

- **endpoints** <span id="endpoints"/> は certificate を取得する HTTP endpoint の一覧です。このディレクティブは同じ行で複数の値を受け付けられ、複数回指定できます。

- **tls** <span id="tls"/> は、HTTP endpoint へ接続するときに使う任意の TLS 設定です。segment parsing は [次のセクション](#tls-1) で定義されています。

<a id="tls-1"></a>
##### TLS

```caddy-d
... {
	ca                    <ca_module>
	insecure_skip_verify
	handshake_timeout     <duration>
	server_name           <name>
	renegotiation         <never|once|freely>
}
```

- **ca** <span id="ca"/> は trust pool provider を定義する任意のディレクティブです。設定は [`trust_pool`](#trust_pool) と同じ挙動に従います。指定する場合は 1 回だけ指定できます。

- **insecure_skip_verify** <span id="insecure_skip_verify"/> は TLS handshake verification を無効にし、connection を insecure にして man-in-the-middle attack に脆弱にします。*production では使用しないでください。* 検証は system が信頼する certificate authority、または [`ca`](#ca) ディレクティブで決まる authority に対して行われます。

- **handshake_timeout** <span id="handshake_timeout"/> は TLS handshake 完了を待つ最大 [duration](/docs/conventions#durations) です。デフォルト: timeout なし。

- **server_name** <span id="server_name"/> は、TLS handshake で受け取った certificate を検証するときに使う server name を設定します。デフォルトでは upstream address の host 部分を使います。

- **renegotiation** <span id="renegotiation"/> は TLS renegotiation level を設定します。TLS renegotiation とは、最初の handshake 後に追加の handshake を実行することです。level は次のいずれかです。
  - `never`（デフォルト）は renegotiation を無効にします。
  - `once` は remote server が connection ごとに 1 回 renegotiation を要求することを許可します。
  - `freely` は remote server が renegotiation を繰り返し要求することを許可します。

<a id="verifiers"></a>
### Verifiers

Client certificate verifier module は、`trust_pool` が設定されている場合、trusted certificate authority から発行されていることを検証した後に実行されます。現在、標準の Caddy に含まれている verifier は `leaf` です。

<a id="leaf"></a>
#### Leaf

`leaf` verifier は、client certificate が定義済みの許可 certificate set の 1 つかどうかを確認します。certificate set は [loader](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders) module を使って読み込まれます。

<a id="loaders"></a>
##### Loaders

標準の Caddy distribution は 4 つの loader を bundle しており、そのうち 3 つが Caddyfile で利用できます。

<a id="file-1"></a>
###### File

`file` loader は、指定された PEM file から certificate set を読み込みます。

```caddy-d
... file <pem_files...>
```

<a id="folder"></a>
###### Folder

`folder` loader は、指定された directory を再帰的に traverse し、accepted client certificate として読み込む PEM file を探します。

```caddy-d
... folder <folders...>
```

<a id="pem"></a>
###### PEM

`pem` loader は、Caddyfile に PEM format で inline された certificate を受け付けます。

```caddy-d
... pem <pem_strings...>
```

<a id="issuers"></a>
### Issuers

これらの issuer は `tls` ディレクティブに標準で含まれています。

<a id="acme"></a>
#### acme

ACME protocol を使って certificate を取得します。`acme` はデフォルト issuer（Let's Encrypt を使用）であるため、通常は明示的に設定する必要はありません。

```caddy-d
... acme [<directory_url>] {
	dir      <directory_url>
	test_dir <test_directory_url>
	email    <email>
	timeout  <duration>
	disable_http_challenge
	disable_tlsalpn_challenge
	alt_http_port    <port>
	alt_tlsalpn_port <port>
	eab <key_id> <mac_key>
	trusted_roots <pem_files...>
	dns [<provider_name> [<options>]]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}
	profile <name>
}
```

- **dir** <span id="dir"/> は ACME CA の directory URL です。
  
  デフォルト: `https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> は challenge retry 時に使う任意の fallback directory です。すべての challenge が失敗した場合、retry 中にこの endpoint が使われます。production endpoint の rate limit を避けたい staging endpoint を CA が持っている場合に便利です。

  デフォルト: `https://acme-staging-v02.api.letsencrypt.org/directory`

- **email** <span id="email"/> は ACME account contact email address です。

- **timeout** <span id="timeout"/> は ACME operation が timeout するまで待つ時間を設定する [duration value](/docs/conventions#durations) です。

- **disable_http_challenge** <span id="disable_http_challenge"/> は HTTP challenge を無効にします。

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> は TLS-ALPN challenge を無効にします。

- **alt_http_port** <span id="alt_http_port"/> は HTTP challenge を提供する代替 port です。challenge は port 80 で発生する必要があるため、この代替 port へ packet を forward する必要があります。

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> は TLS-ALPN challenge を提供する代替 port です。challenge は port 443 で発生する必要があるため、この代替 port へ packet を forward する必要があります。

- **eab** <span id="eab"/> は、一部の ACME CA で必要になる場合がある External Account Binding を指定します。

- **trusted_roots** <span id="trusted_roots"/> は、ACME CA server への接続時に trust する 1 つ以上の root certificate（PEM filename）です。

- **dns** <span id="dns"/> は DNS challenge を設定します。[`dns` global option](/docs/caddyfile/options#dns) が global に適用される DNS provider module を指定していない限り、ここで provider を設定する必要があります。

- **propagation_timeout** <span id="propagation_timeout"/> は、DNS challenge 使用時に DNS TXT record が現れるまで待つ最大時間を設定する [duration value](/docs/conventions#durations) です。propagation check を無効化するには `-1` に設定します。デフォルトは 2 分です。

- **propagation_delay** <span id="propagation_delay"/> は、DNS challenge 使用時に DNS TXT record propagation check を開始する前に待つ時間を設定する [duration value](/docs/conventions#durations) です。デフォルトは 0（待機なし）です。

- **dns_ttl** <span id="dns_ttl"/> は、DNS challenge で使う `TXT` record の TTL を設定する [duration value](/docs/conventions#durations) です。必要になることはまれです。

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> は、DNS challenge に使う domain を上書きします。これは challenge を別 domain に delegate するためのものです。

  primary domain の DNS provider に利用可能な [DNS plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) がない場合に使うとよいでしょう。代わりに、primary domain に `_acme-challenge` subdomain の `CNAME` record を追加し、plugin を*持っている* secondary domain を指すようにできます。この option は plugin からの特別な support を*必要としません*。
  
  ACME issuer が primary domain の DNS challenge を解決しようとすると、`CNAME` を辿って secondary domain にある `TXT` record を探します。

  **Note:** ここでは CNAME record からの完全な canonical name を値として使ってください。`_acme-challenge` subdomain は自動的には前置されません。

- **resolvers** <span id="resolvers"/> は、DNS challenge 実行時に使う DNS resolver を custom します。これは system resolver や任意の default resolver より優先されます。ここで設定すると、resolver は設定済みのすべての certificate issuer に伝播します。

  通常これは IP address の一覧です。たとえば [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns) を使う場合:

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> は Caddy が優先すべき certificate chain を指定します。CA が複数の chain を提供する場合に便利です。次の option のいずれかを使います。
	- **smallest** <span id="smallest"/> は、bytes 数が最も少ない chain を優先するよう Caddy に指示します。

	- **root_common_name** <span id="root_common_name"/> は 1 つ以上の common name の一覧です。Caddy は、指定された common name の少なくとも 1 つと一致する root を持つ最初の chain を選びます。

	- **any_common_name** <span id="any_common_name"/> は 1 つ以上の common name の一覧です。Caddy は、指定された common name の少なくとも 1 つと一致する issuer を持つ最初の chain を選びます。

- **profile** は、certificate ordering 時に適用する [ACME profile](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/) の名前です。指定する場合、設定済み（implicit かどうかに関係なく）のすべての CA がこの profile をサポートしている必要があります。利用可能な profile については CA の documentation を参照してください。一部の CA は profile をサポートしない場合があります。EXPERIMENTAL: ACME profile specification はまだ draft 状態であるため、この feature/function は変更または削除される可能性があります。


<a id="zerossl"></a>
#### zerossl

[ZeroSSL の proprietary certificate issuance API](https://zerossl.com/documentation/api/) を使って certificate を取得します。API key が必要で、plan によっては支払いも必要です。これは [ZeroSSL の ACME endpoint](https://zerossl.com/documentation/acme/) とは別物であることに注意してください。ZeroSSL の ACME endpoint を使うには、上で説明した `acme` issuer を ZeroSSL の ACME directory endpoint で設定してください。

```caddy-d
... zerossl <api_key> {
	validity_days <days>
	alt_http_port <port>
	dns <provider_name> ...
	propagation_delay <duration>
	propagation_timeout <duration>
	resolvers <list...>
	dns_ttl <duration>
}
```

- **validity_days** <span id="validity_days"/> は certificate lifetime を定義します。受け付けられる値は限られています。詳細は [ZeroSSL's docs](https://zerossl.com/documentation/api/create-certificate/) を参照してください。
<!--   
  Default: `https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> は、port 80 でない場合に ZeroSSL の HTTP validation を完了するために使う port です。
- **dns** <span id="zerossl_dns"/> は、named DNS provider と指定された設定を使って automatic record provisioning による CNAME validation method を有効にします。DNS provider plugin は [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) repository から install する必要があります。各 provider plugin は名前の後に独自の構文を持つ場合があります。詳細はそれぞれの docs を参照してください。各 DNS provider の support 維持は community effort です。
- **propagation_delay** <span id="zerossl_propagation_delay"/> は CNAME record propagation を確認する前に待つ時間です。
- **propagation_timeout** <span id="zerossl_propagation_timeout"/> は諦める前に CNAME record propagation を待つ時間です。
- **resolvers** <span id="zerossl_resolvers"/> は CNAME record propagation の確認時に使う custom DNS resolver を定義します。
- **dns_ttl** <span id="zerossl_dns_ttl"/> は validation process の一部として作成される CNAME record の TTL を設定します。



<a id="internal"></a>
#### internal

internal certificate authority から certificate を取得します。

```caddy-d
... internal {
	ca       <name>
	lifetime <duration>
	sign_with_root
}
```

- **ca** <span id="ca"/> は使用する internal CA の名前です。デフォルト: `local`。`local` CA を設定する、または代替 CA を作成するには、[PKI app global options](/docs/caddyfile/options#pki-options) を参照してください。

  デフォルトでは、root CA certificate の lifetime は `3600d`（10 年）、intermediate は `7d`（7 日）です。

  Caddy は root CA certificate を system trust store に install しようとしますが、Caddy が unprivileged user として実行されている場合、または Docker container 内で実行されている場合は失敗することがあります。その場合、[`caddy trust`](/docs/command-line#caddy-trust) command を使うか、[container から copy](/docs/running#usage) することで、root CA certificate を手動で install する必要があります。

- **lifetime** <span id="lifetime"/> は、internal に発行される leaf certificate の validity period を設定する [duration value](/docs/conventions#durations) です。デフォルト: `12h`。絶対に必要でない限り、これを変更することは推奨されません。intermediate の lifetime より短くする必要があります。

- **sign_with_root** <span id="sign_with_root"/> は、intermediate ではなく root を issuer にすることを強制します。これは推奨されず、device/client が certificate chain を適切に検証しない場合にのみ使うべきです（非常にまれです）。



<a id="certificate-managers"></a>
### Certificate Managers

Certificate manager module は issuer module とは異なります。manager module の使用は、external tool または service が certificate を更新し続けることを意味する一方、issuer module は Caddy 自身が certificate を管理することを意味します。（issuer module は Certificate Signing Request (CSR) を input としますが、certificate manager module は TLS ClientHello を input とします。）

これらの manager module は `tls` ディレクティブに標準で含まれています。

<a id="tailscale"></a>
#### tailscale

local で実行されている [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) instance から certificate を取得します。[Tailscale account で HTTPS を有効にする必要があります](https://tailscale.com/kb/1153/enabling-https/)（または open source の [Headscale server <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/juanfont/headscale)）。また、Caddy process は root として実行されているか、`tailscaled` に Caddy user が [certificate を取得する permission](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348) を持つよう設定する必要があります。

**NOTE: これは通常不要です。** Caddy は追加設定なしで、すべての `*.ts.net` domain に対して自動的に Tailscale を使います。

```caddy-d
get_certificate tailscale  # 多くの場合不要です!
```


<a id="http-1"></a>
#### http

HTTP(S) request を行って certificate を取得します。response は `200` status code を持ち、body には full certificate（intermediate を含む）と private key を含む PEM chain が含まれている必要があります。

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> は request を行う fully-qualified URL です。performance 上の理由から、local endpoint にすることを強く推奨します。URL には次の query string parameter が追加されます。

  - `server_name`: SNI value
  - `signature_schemes`: signature algorithm の hex ID の comma-separated list
  - `cipher_suites`: cipher suite の hex ID の comma-separated list
  - `local_ip`: client が request を行った IP address



<a id="examples"></a>
## 例

custom certificate と key を使います。certificate は site address と一致する [SANs](https://en.wikipedia.org/wiki/Subject_Alternative_Name) を持っている必要があります。

```caddy
example.com {
	tls cert.pem key.pem
}
```

ACME / Let's Encrypt 経由の public certificate ではなく、現在の site block のすべての host に [locally-trusted](/docs/automatic-https#local-https) certificate を使います（dev environment で便利です）。

```caddy
example.com {
	tls internal
}
```

locally-trusted certificate を使いますが、background ではなく managed [On-Demand](/docs/automatic-https#on-demand-tls) にします。これにより、任意の domain を Caddy instance に向けるだけで、自動的に certificate を provision できます。Caddy instance が public にアクセス可能な場合は、attacker が server resource を使い尽くす可能性があるため、使用すべきではありません。

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

internal CA に custom option を使います（`tls internal` shortcut は使えません）。

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

ACME account の email address を指定します（ただし、すべての site で email が 1 つだけなら、代わりに `email` [global option](/docs/caddyfile/options) を推奨します）。

```caddy
example.com {
	tls your@email.com
}
```

environment variable 内の account credential を使い、Cloudflare で管理されている domain に DNS challenge を有効にします。これにより wildcard certificate support が使えるようになります。wildcard には DNS validation が必要です。

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

Caddy に管理させる代わりに、HTTP 経由で certificate chain を取得します。[`get_certificate`](#certificate-managers) は [`on_demand`](#on_demand) が有効であることを意味し、ACME issuance を trigger する代わりに module を使って certificate を取得する点に注意してください。

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

TLS Client Authentication を有効にし、[`trust_pool`](#trust_pool) の `file` provider を通じて、提供されたすべての CA に対して検証される有効な certificate の提示を client に要求します。

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
