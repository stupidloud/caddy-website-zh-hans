---
title: "Caddyfile"
---

<a id="the-caddyfile"></a>
# Caddyfile

**Caddyfile** は、人が読み書きしやすい Caddy の設定形式です。書きやすく、理解しやすく、多くのユースケースを十分に表現できるため、多くのユーザーにとって Caddy を使う最も好まれる方法です。

見た目は次のようになります。

```caddy
example.com {
	root /var/www/wordpress
	encode
	php_fastcgi unix//run/php/php-version-fpm.sock
	file_server
}
```

（これは、完全に管理された HTTPS で WordPress を配信する、本番投入可能な実際の Caddyfile です。）

基本的な考え方は、まずサイトのアドレスを書き、次にそのサイトに必要な機能を書いていく、というものです。[よく使われるパターンをさらに見る。](/docs/caddyfile/patterns)

<a id="menu"></a>
## メニュー

- #### [クイックスタートガイド](/docs/quick-starts/caddyfile)
  Caddyfile に慣れる最初の入口として適しています。
- #### [完全な Caddyfile チュートリアル](/docs/caddyfile-tutorial)
  Caddyfile でよく行うさまざまな操作を学びます。
- #### [Caddyfile の概念](/docs/caddyfile/concepts)
  必読です。構造、サイトアドレス、matcher、placeholder などを説明します。
- #### [ディレクティブ](/docs/caddyfile/directives)
  行頭に置くキーワードで、サイトに機能を有効化します。
- #### [リクエスト matcher](/docs/caddyfile/matchers)
  ディレクティブと matcher を組み合わせてリクエストを絞り込みます。
- #### [グローバルオプション](/docs/caddyfile/options)
  個別サイトではなく、サーバー全体に適用される設定です。
- #### [よく使われるパターン](/docs/caddyfile/patterns)
  よくあることをシンプルに実現する方法です。
<!-- - #### [Caddyfile specification](/docs/caddyfile/spec) TODO: Finish this -->


<a id="note"></a>
## 注記

Caddyfile は Caddy の [config adapter](/docs/config-adapters) の 1 つにすぎません。手作業で設定を書く場合にはよく選ばれますが、Caddy の[ネイティブ JSON 構造](/docs/json/)ほど表現力、柔軟性、プログラム可能性は高くありません。Caddy の設定やデプロイを自動化する場合は、[Caddy の API](/docs/api) と JSON を使う方がよいことがあります。（実際には API でも Caddyfile を使えますが、できることは限られます。）
