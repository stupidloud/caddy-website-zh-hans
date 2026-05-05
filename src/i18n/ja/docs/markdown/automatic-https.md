---
title: "Automatic HTTPS"
---

<a id="automatic-https"></a>
# Automatic HTTPS

**Caddy は、HTTPS を自動的に、しかも *デフォルトで* 使用した最初の Web サーバーです。**

Automatic HTTPS は、すべてのサイトに TLS 証明書を用意し、更新し続けます。HTTP から HTTPS へのリダイレクトも自動で行います。Caddy は安全で現代的なデフォルトを使います。ダウンタイム、追加設定、別ツールは不要です。

<aside class="tip">
	Caddy は Automatic HTTPS 技術を切り開きました。2015 年にそれが現実的になった最初の日から、この仕組みに取り組んできました。Caddy の HTTPS 自動化ロジックは、世界で最も成熟し堅牢なものです。
</aside>

動作を示す 28 秒の動画です。

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**メニュー:**

- [概要](#overview)
- [有効化](#activation)
- [効果](#effects)
- [ホスト名の要件](#hostname-requirements)
- [ローカル HTTPS](#local-https)
- [テスト](#testing)
- [ACME Challenges](#acme-challenges)
- [On-Demand TLS](#on-demand-tls)
- [エラー](#errors)
- [ストレージ](#storage)
- [ワイルドカード証明書](#wildcard-certificates)
- [Encrypted ClientHello (ECH)](#encrypted-clienthello-ech)



<a id="overview"></a>
## 概要

**デフォルトでは、Caddy はすべてのサイトを HTTPS で提供します。**

- Caddy は、ローカルで自動的に信頼される（許可されている場合）自己署名証明書を使って、IP アドレスとローカル/内部ホスト名を HTTPS で提供します。
	- 例: `localhost`, `127.0.0.1`
- Caddy は、[Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) や [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com) などの public ACME CA からの証明書を使って、public DNS names を HTTPS で提供します。
	- 例: `example.com`, `sub.example.com`, `*.example.com`

Caddy は、管理対象のすべての証明書を更新し続け、HTTP（デフォルトポート `80`）を HTTPS（デフォルトポート `443`）へ自動的にリダイレクトします。

**ローカル HTTPS の場合:**

- Caddy は、固有の root certificate を trust store にインストールするため、パスワードを求めることがあります。これは root ごとに一度だけ起こり、いつでも削除できます。
- Caddy の root CA certificate を信頼していないクライアントがサイトへアクセスすると、セキュリティエラーが表示されます。

**public domain names の場合:**

<aside class="tip">

これらは Caddy に限らず、基本的な本番 Web サイトに共通する要件です。主な違いは、Caddy が証明書を用意できるように、Caddy を実行する **前に** DNS records を正しく設定しておくことです。

</aside>


- ドメインの A/AAAA records がサーバーを指していて、
- ports `80` と `443` が外部から開いていて、
- Caddy がそれらの ports に bind できる（*または* それらの ports が Caddy に転送されている）、
- [data directory](/docs/conventions#data-directory) が書き込み可能で永続的であり、
- ドメイン名が設定内の関連する場所に現れている、

なら、サイトは自動的に HTTPS で提供されます。それ以上何もする必要はありません。そのまま動きます。

HTTPS は共有された public infrastructure を利用するため、サーバー管理者はこのページの残りの情報を理解しておくべきです。そうすることで、不要な問題を避け、問題が起きたときにトラブルシュートし、高度なデプロイを正しく設定できます。



<a id="activation"></a>
## 有効化

Caddy は、提供する domain name（つまり hostname）または IP address を知ると、Automatic HTTPS を暗黙的に有効化します。Caddy の実行方法や設定方法に応じて、ドメイン/IP を Caddy に伝える方法はいくつかあります。

- [Caddyfile](/docs/caddyfile) の [site address](/docs/caddyfile/concepts#addresses)
- [JSON routes](/docs/modules/http#servers/routes) のトップレベルにある [host matcher](/docs/json/apps/http/servers/routes/match/host/)
- [`--domain`](/docs/command-line#caddy-file-server) や [`--from`](/docs/command-line#caddy-reverse-proxy) などの command line flags
- [automate](/docs/json/apps/tls/certificates/automate/) certificate loader

次のいずれかに該当すると、Automatic HTTPS は全体または一部で有効化されません。

- [JSON 経由](/docs/json/apps/http/servers/automatic_https/) または [Caddyfile 経由](/docs/caddyfile/options#auto-https) で明示的に無効化している
- 設定に hostname や IP address をまったく指定していない
- HTTP port だけを listen している
- Caddyfile で [site address](/docs/caddyfile/concepts#addresses) に `http://` を付けている
- 証明書を手動で読み込んでいる（[`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/) が設定されている場合を除く）

**特別なケース:**

- `.ts.net` で終わるドメインは Caddy によって管理されません。代わりに、Caddy は handshake-time に、ローカルで実行中の [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) instance からこれらの証明書を取得しようとします。これには、[Tailscale account で HTTPS が有効化されている <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/) ことが必要です。また、Caddy process が root として実行されているか、`tailscaled` に Caddy user が [証明書を取得する権限](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348) を与えるよう設定されている必要があります。


<a id="effects"></a>
## 効果

Automatic HTTPS が有効化されると、次のことが起こります。

- [条件を満たすすべての domain names](#hostname-requirements) について証明書が取得され、更新されます
- HTTP が HTTPS にリダイレクトされます（これは [HTTP port](/docs/modules/http#http_port) `80` を使います）

Automatic HTTPS は明示的な設定を上書きすることはなく、あくまで補完するだけです。

HTTP port で listen している [server](/docs/json/apps/http/servers/) がすでにある場合、HTTP->HTTPS redirect routes は host matcher を持つあなたの routes の後、ただし user-defined catch-all route の前に挿入されます。

必要に応じて [Automatic HTTPS をカスタマイズまたは無効化](/docs/json/apps/http/servers/automatic_https/) できます。たとえば、特定の domain names を除外したり、redirects を無効にしたりできます（Caddyfile では [global options](/docs/caddyfile/options) で行います）。


<a id="hostname-requirements"></a>
## ホスト名の要件

すべての hostnames（domain names）は、次を満たす場合に fully-managed certificates の対象になります。

- 空でない
- 英数字、hyphens、dots、wildcard（`*`）だけで構成されている
- dot で始まらず、dot で終わらない（[RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5)）

さらに、次を満たす hostnames は publicly-trusted certificates の対象になります。

- localhost ではない（`.localhost`、`.local`、`.internal`、`.home.arpa` TLDs を含む）
- IP address ではない
- 左端の label として単一の wildcard `*` だけを持つ


<a id="local-https"></a>
## ローカル HTTPS

Caddy は、host（domain、IP、hostname）が指定されたすべてのサイトで、内部ホストやローカルホストを含めて自動的に HTTPS を使います。一部の host は public ではない（例: `127.0.0.1`, `localhost`）か、一般には publicly-trusted certificates の対象になりません（例: IP addresses -- 一部の CAs からは取得できます）。それでも、無効化されていない限り HTTPS で提供されます。

非 public site を HTTPS で提供するため、Caddy は独自の certificate authority（CA）を生成し、それを使って証明書に署名します。trust chain は root certificate と intermediate certificate で構成されます。Leaf certificates は intermediate によって署名されます。これらは [Caddy の data directory](/docs/conventions#data-directory) の `pki/authorities/local` に保存されます。

Caddy の local CA は [Smallstep libraries <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/) によって動作しています。

Local HTTPS は ACME を使わず、DNS validation も行いません。これはローカルマシン上でのみ動作し、CA の root certificate がインストールされている場所でのみ信頼されます。

<a id="ca-root"></a>
### CA Root

root の private key は、暗号学的に安全な疑似乱数源を使って一意に生成され、制限された権限で storage に永続化されます。署名タスクを実行するときだけメモリに読み込まれ、その後スコープを離れて garbage-collected されます。

Caddy は（非準拠クライアントをサポートするために）root で直接署名するよう設定できますが、これはデフォルトでは無効です。root key は intermediates に署名するためだけに使われます。

root key が初めて使われるとき、Caddy はそれをシステムの local trust store(s) にインストールしようとします。その権限がない場合は、パスワードを求めます。この挙動は、[`skip_install_trust` in a caddyfile](/docs/caddyfile/options#skip-install-trust) または [`"install_trust": false` in a json config](/docs/json/apps/pki/certificate_authorities/install_trust/) で無効化できます。権限のないユーザーとして実行しているために失敗する場合は、[`caddy trust`](/docs/command-line#caddy-trust) を実行して、権限のあるユーザーとしてインストールを再試行できます。

<aside class="tip">
	自分のコンピューターが侵害されておらず、固有の root key が漏洩していない限り、自分のマシンで Caddy の root certificate を信頼しても安全です。
</aside>

Caddy の root CA がインストールされると、local trust store に "Caddy Local Authority" として表示されます（別の名前を設定していない場合）。必要ならいつでもアンインストールできます（[`caddy untrust`](/docs/command-line#caddy-untrust) コマンドを使うと簡単です）。

証明書を local trust stores に自動インストールすることは利便性のためだけであり、特に containers を使っている場合や、Caddy が権限のない system service として実行されている場合には、動作が保証されるものではありません。最終的に、internal PKI に依存するなら、Caddy の root CA が必要な trust stores に正しく追加されていることを保証するのはシステム管理者の責任です（これは Web サーバーの範囲外です）。


<a id="ca-intermediates"></a>
### CA Intermediates

intermediate certificate と key も生成され、leaf（個別サイト）証明書の署名に使われます。

root certificate と異なり、intermediate certificates の有効期間はかなり短く、必要に応じて自動的に更新されます。


<a id="testing"></a>
## テスト

Caddy 設定をテストまたは実験するには、必ず [ACME endpoint を変更](/docs/modules/tls.issuance.acme#ca) して staging または development URL を使ってください。そうしないと rate limits に達し、どの rate limit に当たったかによっては、最大 1 週間 HTTPS へのアクセスがブロックされる可能性があります。

Caddy のデフォルト CAs の 1 つである [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/) には、同じ [rate limits <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/) の対象ではない [staging endpoint <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) があります。

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

<a id="acme-challenges"></a>
## ACME challenges

publicly-trusted TLS certificate を取得するには、publicly-trusted な第三者機関による validation が必要です。現在、この validation process は [ACME protocol <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555) で自動化されており、以下で説明する 3 つの方法（"challenge types"）のいずれかで実行できます。

最初の 2 つの challenge types はデフォルトで有効です。複数の challenges が有効な場合、Caddy は特定の challenge への偶発的な依存を避けるため、ランダムに 1 つを選びます。時間が経つにつれて、どの challenge type が最も成功しやすいかを学習し、それを先に優先するようになりますが、必要に応じて他の利用可能な challenge types にフォールバックします。


<a id="http-challenge"></a>
### HTTP challenge

HTTP challenge は、候補 hostname の A/AAAA record について authoritative DNS lookup を行い、その後 HTTP を使って port `80` 経由で一時的な暗号リソースをリクエストします。CA が期待されるリソースを確認できれば、証明書が発行されます。

この challenge には、port `80` が外部からアクセス可能であることが必要です。Caddy が port 80 で listen できない場合、port `80` からの packets は Caddy の [HTTP port](/docs/json/apps/http/http_port/) に転送される必要があります。

この challenge はデフォルトで有効で、明示的な設定は不要です。


<a id="tls-alpn-challenge"></a>
### TLS-ALPN challenge

TLS-ALPN challenge は、候補 hostname の A/AAAA record について authoritative DNS lookup を行い、その後、特別な ServerName と ALPN 値を含む TLS handshake を使って port `443` 経由で一時的な暗号リソースをリクエストします。CA が期待されるリソースを確認できれば、証明書が発行されます。

この challenge には、port `443` が外部からアクセス可能であることが必要です。Caddy が port 443 で listen できない場合、port `443` からの packets は Caddy の [HTTPS port](/docs/json/apps/http/https_port/) に転送される必要があります。

この challenge はデフォルトで有効で、明示的な設定は不要です。


<a id="dns-challenge"></a>
### DNS challenge

DNS challenge は、候補 hostname の `TXT` records について authoritative DNS lookup を行い、特定の値を持つ特別な `TXT` record を探します。CA が期待される値を確認できれば、証明書が発行されます。

この challenge は開いている port を必要とせず、証明書をリクエストするサーバーが外部からアクセス可能である必要もありません。ただし、DNS challenge には設定が必要です。Caddy は、特別な `TXT` records を設定（および削除）できるように、あなたの domain の DNS provider へアクセスする credentials を知る必要があります。DNS challenge が有効な場合、他の challenges はデフォルトで無効になります。

ACME CAs は challenge verification のために `TXT` records を lookup するとき DNS 標準に従うため、CNAME records を使って challenge への応答を他の DNS zones に委任できます。これにより、`_acme-challenge` subdomain を [別の zone](/docs/caddyfile/directives/tls#dns_challenge_override_domain) に委任できます。これは、DNS provider が API を提供していない場合や、Caddy の DNS plugins のいずれにも対応していない場合に特に便利です。

DNS provider support は community effort です。[あなたの provider で DNS challenge を有効化する方法は wiki を参照してください。](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


<a id="on-demand-tls"></a>
## On-Demand TLS

Caddy は **On-Demand TLS** と呼ぶ新しい技術を先駆けて実装しました。これは、設定読み込み時ではなく、それを必要とする最初の TLS handshake 中に新しい証明書を動的に取得します。重要なのは、domain names を事前に設定へ hard-code する必要が **ない** ことです。

多くの企業は、数万のサイトを提供するときに、この独自機能を使って TLS deployment を低コストかつ運用上の悩みなしにスケールさせています。

On-demand TLS は次の場合に便利です。

- サーバーの起動時または reload 時に、すべての domain names が分からない
- domain names がすぐには正しく設定されていない可能性がある（DNS records がまだ設定されていない）
- domain names を自分で管理していない（例: それらが customer domains である）

on-demand TLS が有効な場合、証明書を取得するために設定内で domain names を指定する必要はありません。代わりに、Caddy がまだ証明書を持っていない server name（SNI）に対する TLS handshake を受け取ると、Caddy が handshake を完了するために使う証明書を取得するまで、その handshake は待たされます。遅延は通常数秒だけで、遅いのは最初の handshake だけです。証明書はキャッシュされ再利用され、更新はバックグラウンドで行われるため、それ以降の handshakes は高速です。将来の handshakes は、証明書を更新し続けるための maintenance を起動することがありますが、証明書がまだ期限切れでなければ、この maintenance はバックグラウンドで行われます。

<a id="using-on-demand-tls"></a>
### On-Demand TLS の使用

**On-demand TLS は、乱用を防ぐために有効化と制限の両方が必要です。**

on-demand TLS の有効化は、JSON config を使う場合は [TLS automation policies](/docs/json/apps/tls/automation/policies/) で、Caddyfile を使う場合は [`tls` directive を持つ site blocks](/docs/caddyfile/directives/tls) で行います。

この機能の乱用を防ぐには、制限を設定する必要があります。これは [JSON config の `automation` object](/docs/json/apps/tls/automation/on_demand/) または Caddyfile の [`on_demand_tls` global option](/docs/caddyfile/options#on-demand-tls) で行います。制限は "global" であり、site ごと、domain ごとには設定できません。主な制限は "ask" endpoint です。Caddy は handshake 内の domain について、証明書を取得・管理する許可があるかを尋ねる HTTP request をこの endpoint に送ります。つまり、たとえば database の accounts table を query し、その customer がその domain name で登録しているか確認できる内部 backend が必要になります。

CA がどれだけ速く証明書を発行できるかに注意してください。数秒を超える場合、（最初の client だけとはいえ）ユーザー体験に悪影響があります。

遅延実行という性質と、乱用防止のために追加設定が必要なことから、上記のユースケースに実際に当てはまる場合にのみ on-demand TLS を有効化することを推奨します。

[on-demand TLS を効果的に使う方法の詳細は wiki article を参照してください。](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)

<a id="errors"></a>
## エラー

Caddy は、証明書管理でエラーが発生しても、可能な限り継続しようとします。

デフォルトでは、証明書管理はバックグラウンドで実行されます。つまり、起動をブロックしたり、サイトを遅くしたりしません。ただし、すべての証明書が利用可能になる前にサーバーが動作している可能性もあります。バックグラウンドで実行することで、Caddy は長期間にわたって exponential backoff で再試行できます。

証明書の取得または更新でエラーが発生した場合は、次のようになります。

1. Caddy は、偶発的な失敗に備えて短い pause の後に 1 回再試行します
2. Caddy は少し pause し、次に有効化された challenge type へ切り替えます
3. 有効化されたすべての challenge types を試した後、[次に設定された issuer](#issuer-fallback) を試します
	- Let's Encrypt
	- ZeroSSL
4. すべての issuers を試した後、exponential backoff します
	- 試行間隔は最大 1 日
	- 最大 30 日間

Let's Encrypt での再試行中、Caddy は rate limit の懸念を避けるため、[staging environment <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) に切り替えます。完璧な戦略ではありませんが、一般には役に立ちます。

ACME challenges には少なくとも数秒かかり、内部 rate limiting は偶発的な乱用の軽減に役立ちます。Caddy は、あなたや CA が設定するものに加えて内部 rate limiting を使うため、100 万個の domain names を Caddy に渡しても、Caddy は徐々に、ただし可能な限り速く、すべての証明書を取得します。Caddy の内部 rate limit は現在、ACME account ごとに 10 秒あたり 10 回の試行です。

リソース漏れを避けるため、Caddy は設定が変更されると進行中のタスク（ACME transactions を含む）を中止します。Caddy は頻繁な config reloads を処理できますが、このような運用上の考慮事項に注意し、reload を減らして Caddy がバックグラウンドで証明書取得を実際に完了できるように、設定変更をまとめることを検討してください。

<a id="issuer-fallback"></a>
### Issuer fallback

Caddy は、証明書を正常に取得できない場合に、他の CAs へ完全に冗長化された自動 failover をサポートした最初の（そして今のところ唯一の）サーバーです。

デフォルトでは、Caddy は 2 つの ACME-compatible CAs を有効化します。[**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) と [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com) です。Caddy が Let's Encrypt から証明書を取得できない場合、ZeroSSL を試します。両方とも失敗した場合は backoff し、後で再試行します。設定では、Caddy が証明書取得に使う issuers を、全体または特定の names 向けにカスタマイズできます。


<a id="storage"></a>
## ストレージ

Caddy は public certificates、private keys、その他の assets を [configured storage facility](/docs/json/storage/)（設定されていない場合はデフォルト。詳細はリンク先を参照）に保存します。

**デフォルト設定を使うときに知っておくべき最も重要なことは、`$HOME` folder が書き込み可能で永続的でなければならないということです。** トラブルシュートを助けるため、`--environ` flag が指定されている場合、Caddy は起動時に環境変数を出力します。

同じ storage を使うように設定された Caddy instances は、その resources を自動的に共有し、cluster として証明書管理を調整します。

ACME transactions を試みる前に、Caddy は設定された storage をテストし、書き込み可能で十分な容量があることを確認します。これにより、不要な lock contention を減らせます。


<a id="wildcard-certificates"></a>
## ワイルドカード証明書

Caddy は、条件を満たす wildcard name を持つサイトを提供するよう設定されている場合、wildcard certificates を取得し管理できます。site name は、左端の domain label だけが wildcard である場合に wildcard の対象になります。たとえば、`*.example.com` は対象ですが、次は対象外です: `sub.*.example.com`, `foo*.example.com`, `*bar.example.com`, `*.*.example.com`。（これは WebPKI の制約です。）

Caddyfile を使う場合、Caddy は certificate subject names に関して site names を文字どおりに扱います。つまり、`sub.example.com` と定義された site は Caddy に `sub.example.com` の証明書を管理させ、`*.example.com` と定義された site は Caddy に `*.example.com` の wildcard certificate を管理させます。これは [Common Caddyfile Patterns](/docs/caddyfile/patterns#wildcard-certificates) ページで確認できます。異なる挙動が必要な場合、[JSON config](/docs/json/) により certificate subjects と site names（"host matchers"）をより正確に制御できます。

Caddy 2.10 以降、wildcard certificate を自動化する場合、Caddy は設定内の個別 subdomains に対して wildcard certificate を使います。明示的にそう設定されていない限り（例: `force_automate`）、個別 subdomains の証明書は取得しません。

Wildcard certificates は広い権限を表すため、多数の subdomains があり、それらの個別証明書を管理すると PKI に負荷がかかったり CA-enforced rate limits に達したりする場合、または key compromise 時に DNS zone の多くを露出するリスクに見合う privacy tradeoff がある場合にのみ使うべきです。wildcard certificates だけでは、特定 subdomains を隠す privacy は提供しない点に注意してください。Encrypted ClientHello（ECH）が有効でない限り、それらは TLS ClientHello packets にまだ露出します。（下記参照。）

**注:** [Let's Encrypt requires <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) wildcard certificates の取得には [DNS challenge](#dns-challenge) が必要です。


<a id="encrypted-clienthello-ech"></a>
## Encrypted ClientHello (ECH)

通常、TLS handshakes では、Server Name Indicator（SNI、接続先の domain）を含む ClientHello が plaintext で送られます。これは、handshake の後に続く接続を暗号化するために必要なパラメーターを含んでいるからです。当然ながら、これは ClientHello の中で最も機密性の高い domain name を、接続を盗聴できる誰に対しても公開します。相手があなたのすぐ近くにいる必要はありません。宛先 IP が多数の異なるサイトを提供している場合、あなたがどの service に接続しているかを明かし、一部の政府が Internet を検閲する手段にもなります。

Encrypted ClientHello では、client は true ClientHello を "outer" ClientHello で包むことで domain name を保護できます。この "outer" ClientHello は "inner" ClientHello を復号するためのパラメーターを確立します。ただし、これが実際の privacy benefits をもたらすには、多くの要素が完全にかみ合う必要があります。

まず、client は ClientHello を暗号化するために使う parameters、つまり configuration を知る必要があります。この情報には public key と "outer" domain（"public name"）などが含まれます。この configuration は、何らかの信頼できる方法で公開または配布されなければなりません。

理論上はそれを紙に書いて全員に配ることもできますが、主要ブラウザーの多くは、サイトに接続するときに ECH parameters を含む HTTPS-type DNS records を lookup することをサポートしています。したがって、(1) ECH configuration（public/private key pair などの parameters）を生成し、(2) base64-encoded ECH configuration を含む HTTPS-type DNS record を作成する必要があります。

あるいは... それらすべてを Caddy に任せることもできます。Caddy は、ECH configurations を自動的に生成、公開、提供できる最初で唯一の Web サーバーです。

HTTPS record が公開されると、clients はあなたのサイトに接続するときに HTTPS record の DNS lookup を行う必要があります。通常、DNS lookups は plaintext であり、結果として得られる ECH handshakes のセキュリティを損ないます。そのため、ブラウザーは DNS-over-HTTPS（DoH）や DNS-over-TLS（DoT）のような安全な DNS protocol を使う必要があります。ブラウザーによっては、これを手動で有効にする必要があります。

client が ECH config を安全にダウンロードすると、埋め込まれた public key を使って ClientHello を暗号化し、あなたのサイトへの接続を進めます。その後 Caddy は inner ClientHello を復号し、domain name が wire 上で plaintext として現れることなくサイトを提供します。

<a id="deployment-considerations"></a>
### デプロイ時の考慮事項

ECH は繊細な技術です。Caddy は ECH を完全に自動化しますが、最大限の privacy benefits を得るには多くのことを考慮する必要があります。さまざまな trade-offs も理解しておくべきです。

<a id="publication"></a>
#### 公開

Caddy は、domain にすでに record が存在する場合にのみ、その domain の HTTPS record を作成します。これにより、wildcard でカバーされる可能性がある subdomain の DNS lookups を壊すことを防ぎます。サイトには、少なくともサーバーを指す A/AAAA record があることを確認してください。DNS records に wildcard だけを使っている場合は、その wildcard domain も Caddy config に現れる必要があります。

Caddy は、CNAME record を持つ domain には HTTPS record を公開しません。

<a id="ech-grease"></a>
#### ECH GREASE

Wireshark を開いて、主要ブラウザーの最近のバージョン（Firefox や Chrome など）で任意のサイト（ECH をサポートしていないサイトでも）に接続すると、ECH が無効でも、その handshake に `encrypted_client_hello` extension が含まれていることに気づくかもしれません。

![ECH GREASE](/resources/images/ech-grease.png)

これは、true ECH handshakes を plaintext のものと区別できないようにするためです。ECH handshakes が通常のものと異なって見えるなら、検閲者は最小限の副作用/巻き添え被害で ECH handshakes だけをブロックできます。しかし、もっともらしい ECH extension を持つ handshake をすべてブロックすると、実質的に Internet の大部分を停止させることになります。（目的は、広範な検閲のコストを上げることです。）

これは主に接続をトラブルシュートするときに知っておくべきことです。

<a id="key-rotation"></a>
#### Key rotation

証明書の keys と同様に、同じ key を長期間使い続けることは良い習慣ではなく、明らかに安全でない場合もあります。そのため、ECH keys は定期的に rotate すべきです。証明書と異なり、ECH configs は厳密には expire しません。それでも servers は rotate すべきです。

ただし key rotation は難しいです。clients が更新された keys を知る必要があるからです。server が単に古い keys を新しいものに置き換えた場合、clients が新しい keys についてすぐ通知されない限り、すべての ECH handshakes が失敗します。しかし、更新された keys を公開するだけでは十分ではありません。現実には、DNS records には TTL があり、resolvers は responses を cache します。clients が更新された HTTPS records を query し、新しい ECH config を使い始めるまで、数分、数時間、あるいは数日かかることがあります。

そのため、servers は一定期間、古い ECH configs のサポートを続けるべきです。そうしないと、server names が plaintext で *大規模に* 露出するリスクがあります。Caddy は時々 keys を rotate し、最終的に削除されるまでの一定期間、rotated keys をサポートします。

しかし、それだけでは十分でない可能性があります。一部の clients はさまざまな理由で更新された keys を取得できず、そのたびに server name が露出するリスクがあります。そのため、接続の *in band* で clients に更新された config を渡す別の方法が必要です。それが *outer name*（または *public name*）の役割です。

<a id="public-name"></a>
#### Public name

"outer" ClientHello は通常の ClientHello ですが、origin server だけが知っている 2 つの微妙な違いがあります。

1. SNI extension は偽物です
2. ECH extension は本物です

その "outer" SNI extension には、あなたの real domains を保護する public name が含まれます。この名前は何でも構いませんが、Caddy はその証明書を取得するため、**あなたのサーバーは public name に対して authoritative でなければなりません**。

client が ECH connection を試みたものの server が inner ClientHello を復号できない場合、server は outer name の証明書を使って *outer* ClientHello による handshake を実際に完了できます。この安全な接続は、現在の ECH config を client に送るため *だけ* に使われます。つまり、最初の TLS connection を完了するという唯一の目的のための一時的な TLS connection です。application data は送信されません。送られるのは ECH key だけです。client が更新された key を得ると、意図した TLS connection を確立できます。

このようにして、true server name は保護され、同期がずれた clients も接続できるままになります。どちらもセキュリティ上重要な要素です。

outer name は、サイトの domains の 1 つ、subdomain、またはサーバーを指す任意の domain name で構いません。汎用的な名前をちょうど 1 つ選ぶことを推奨します。たとえば、Cloudflare は `cloudflare-ech.com` の背後で数百万のサイトを提供しています。これは anonymity set のサイズを増やすために重要です。

Public names は空であるべきではありません。つまり、動作させるには public name を設定する必要があります。Caddy は現在これを強制していません（将来強制する可能性があります）が、ECH specification は public name が少なくとも 1 byte 以上であることを要求しています。空の名前を受け入れる software もあれば、受け入れないものもあります。これにより、ブラウザーは ECH を使っているが servers が無効として拒否する、または config が DNS record に正しく入っているのにブラウザーが ECH を使わない（無効だから）といった混乱する挙動につながることがあります。privacy を確保するために適切な ECH configuration と publication を保証するのは site owner の責任です。


<a id="anonymity-set"></a>
#### Anonymity set

ECH の privacy benefits を最大化するには、*anonymity set* のサイズを最大化するよう努めてください。本質的に、この set は、観測者から見て同じ挙動をする client-facing servers で構成されます。考え方は、観測者が clients の接続先としてあり得る sites や services を簡単に絞り込んだり推測したりできないようにすることです。

実際には、すべてのサイトに対して public name は 1 つだけにすることを推奨します。（ECH config ごとに public name は 1 つだけなので、これは任意の時点で active ECH config が 1 つだけであることを意味します。）Caddy を cluster で運用している場合、Caddy は他の instances と ECH configs を自動的に共有・調整するため、これを自動で処理します。

極端に考えると、Internet 上のすべてのサイトは単一の IP address と 1 つの public name の背後にあるべき、またはあり得る、ということになります...


<a id="centralization"></a>
#### 中央集権化

... ここで次の話題である中央集権化につながります。ECH への批判の 1 つは、中央集権化を促しがちだという点です。少なくとも 2 つの方法でそうなります。(1) clients が DNS lookups に DoH/DoT を優先し、すべての DNS lookups が少数の providers を通るようになること、(2) anonymity set のサイズを大規模に最大化することです。

DoH または DoT が使われると、DNS lookups はすべて DoH/DoT provider を通ります。client と provider の間では DNS data は暗号化されますが、provider と DNS server の間では暗号化されません。global DoH/DoT は、観測や障害にさらされやすい少数の大きなパイプへ、価値の高い plaintext DNS traffic を効果的に集約します。

同様に、anonymity set を大規模に本当に最大化するなら、すべてのサイトは `cloudflare-ech.com` のような単一の public name の背後で保護されることになります。これは privacy には良いですが、Internet 全体が Cloudflare とその 1 つの domain name に依存することにもなります。そこまで最大化することは必要でも実用的でもありませんが、理論的な含意は有効です。

各組織または個人が、すべてのサイトに対して単一の名前を選んで使うことを推奨します。多くの場合、それで十分な privacy が得られるはずです。ただし、あなたの具体的なケースについては、個別の threat models に基づき専門家に相談してください。


<a id="subdomain-privacy"></a>
#### Subdomain privacy

ECH により、正しくデプロイされていれば、side channels から subdomains を secret/private に保つことが理論上可能になりました。

一般的に subdomains は public information なので、ほとんどのサイトではこれは不要です。domain names に機密情報を入れることは推奨しません。とはいえ...

Certificate Transparency（CT）logs に sensitive subdomains が漏れるのを避けるには、代わりに wildcard certificate を使ってください。言い換えると、設定に `sub.example.com` を入れる代わりに、`*.example.com` を入れます。（重要な情報については [Wildcard certificates](#wildcard-certificates) を参照してください。）

もう 1 つの漏洩源は DNSSEC です。これは多くの authoritative DNS servers がデフォルトで使っています。"zone walking" と呼ばれる手法により、存在しないことの認証に使われる NSEC records を見ることで subdomain enumeration が可能です。このため、NSEC records はアルファベット順で次に利用可能な subdomain を指し、すべての records の linked list を形成します。これを軽減するため、domain が少なくとも NSEC3、理想的には wildcard CNAME record を使っていることを確認してください。

その後、Caddy で ECH を有効にします。wildcard certificate と ECH、そして wildcard CNAME record を組み合わせれば、接続しようとするすべての client が ECH を使い、強い実装を持つ限り、subdomains を適切に隠せるはずです。（privacy を保つには、依然として clients に依存します。）


<a id="enabling-ech"></a>
### ECH の有効化

機能する ECH には configs を DNS records に公開する必要があるため、DNS provider 向けの [caddy-dns module](https://github.com/caddy-dns) が組み込まれた Caddy build が必要です。

次に、Caddyfile では global options に DNS provider config と、使いたい ECH public name を指定します。

```caddy
{
	dns <provider config...>
	ech example.com
}
```

覚えておいてください。

- DNS provider module が組み込まれており、provider/account に合った正しい設定が必要です。
- ECH public name はサーバーを指しているべきです。Caddy はその証明書を取得します。これはあなたの site の domains の 1 つである必要はありません。

JSON を使う場合は、`tls` app に次の properties を追加します。

```json
"encrypted_client_hello": {
	"configs": [
		{
			"public_name": "example.com"
		}
	]
},
"dns": {
	"name": "<provider name>",
	// provider configuration
}
```

これらの設定は ECH を有効にし、すべてのサイトについて ECH configs を公開します。JSON config は、挙動をカスタマイズしたい場合や高度な setup がある場合に、より高い柔軟性を提供します。

<a id="verifying-ech"></a>
### ECH の検証

ECH 周辺の tooling はまだ多くないため、執筆時点では、動作していることを検証する最善かつ最も汎用的な方法は、Wireshark を使い、ServerName field に public name があるかを見ることです。

まず、サーバーを起動し、logs にあなたの domains について "published ECH configuration list" のような内容が出ていることを確認します。（publication でエラーが出る場合は、DNS provider module が [libdns 1.0](https://github.com/libdns/libdns) をサポートしていることを確認し、問題があれば provider の repository に issue を作成してください。）Caddy は public name の証明書も取得するはずです。

次に、ブラウザーで ECH が有効になっていることを確認します。これには DoH/DoT の有効化が必要な場合があります。新しく公開された HTTPS records を確実に拾うため、ブラウザー（またはシステム）の DNS cache をクリアするのも良い考えです。また、既存の接続を再利用しないよう、ブラウザーを閉じるか、少なくとも新しい private tab を開くことを推奨します。

その後、Wireshark を開き、適切な network interface で listen を開始します。Wireshark が packets を収集している間に、ブラウザーでサイトを読み込みます。その後 Wireshark を pause できます。TLS ClientHello を見つけると、接続した実際の domain name ではなく、ServerName field に *public name* が表示されているはずです。

覚えておいてください。ECH が使われていなくても、`encrypted_client_hello` extension が表示されることがあります。重要な指標は SNI value です。ECH が正しく動作している場合、Wireshark で true site name が plaintext で表示されることは決してないはずです。

ECH のデプロイで問題に遭遇した場合は、まず [forum](https://caddy.community) で質問してください。bug であれば、GitHub で [issue を作成](https://github.com/caddyserver/caddy/issues) できます。


<a id="ech-in-storage"></a>
### ECH in storage

ECH configurations は、設定された storage module（デフォルトは file system）の [data directory](/docs/conventions#data-directory) 内、`ech/configs` folder に保存されます。

次の folder は ECH config ID で、これはランダムに生成され、比較的重要ではありません。この randomness は fingerprinting/tracking の軽減に役立つため、spec で推奨されています。

metadata sidecar file は、Caddy が publications が最後に行われた時刻を追跡するのに役立ちます。これにより、config reload のたびに DNS provider へ大量の request を送ることを防ぎます。この状態を reset する必要がある場合は、metadata file を安全に削除できます。ただし、key が rotate される時刻も reset される可能性があります。file に入り、publication に関する情報だけを消すこともできます。
