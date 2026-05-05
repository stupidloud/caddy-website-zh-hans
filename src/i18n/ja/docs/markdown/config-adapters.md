---
title: Config Adapters
---

<a id="config-adapters"></a>
# Config Adapters

Caddy のネイティブ設定言語は [JSON](https://www.json.org/json-en.html) ですが、JSON を手で書くのは退屈で、ミスも起きやすいものです。そのため Caddy は、**config adapters** を通じて他の言語での設定に対応しています。config adapter は Caddy plugin であり、[Caddy JSON](/docs/json/) を出力することで、好みの形式の設定を使えるようにします。

たとえば、config adapter は [NGINX config を Caddy JSON に変換](https://github.com/caddyserver/nginx-adapter)できます。

<a id="known-config-adapters"></a>
## 既知の config adapter

現在、次の config adapter が利用できます（一部は third-party project です）。

- [**caddyfile**](/docs/caddyfile) (standard)
- [**nginx**](https://github.com/caddyserver/nginx-adapter)
- [**jsonc**](https://github.com/caddyserver/jsonc-adapter)
- [**json5**](https://github.com/caddyserver/json5-adapter)
- [**yaml**](https://github.com/abiosoft/caddy-yaml)
- [**cue**](https://github.com/caddyserver/cue-adapter)
- [**toml**](https://github.com/awoodbeck/caddy-toml-adapter)
- [**hcl**](https://github.com/francislavoie/caddy-hcl)
- [**dhall**](https://github.com/mholt/dhall-adapter)
- [**mysql**](https://github.com/zhangjiayin/caddy-mysql-adapter)

<a id="using-config-adapters"></a>
## config adapter を使う

設定を受け取る多くのサブコマンドでは、command line で `--adapter` フラグを指定して config adapter を使えます。

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

または、API の [`/load` endpoint](/docs/api#post-load) から使えます。

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

実行せずに出力 JSON だけを得たい場合は、[`caddy adapt`](/docs/command-line#caddy-adapt) コマンドを使えます。

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

<a id="caveats"></a>
## 注意点

すべての設定言語が Caddy と 100% 互換というわけではありません。一部の機能や挙動は、うまく変換できなかったり、adapter や Caddy 自体にまだ実装されていなかったりします。

YAML->JSON や TOML->JSON のように 1 対 1 で変換する adapter もあります。Caddyfile のように、Caddy 専用に設計されたものもあります。一般的に、これらの adapter は常に動作します。

しかし、すべての adapter が常に完全に動作するわけではありません。config adapter は、入力を Caddy JSON へできるだけ高い忠実度と正確さで変換しようとします。この変換処理は常に完全かつ正確であるとは保証されないため、私たちはこれらを "converter" や "translator" とは呼びません。少なくとも最終的な JSON 設定を仕上げるための良い出発点を提供するものなので、"adapter" と呼んでいます。

config adapter は、結果の JSON、warning、error を出力できます。error が発生しなければ JSON が出力されます。入力に問題がある場合（たとえば syntax error）には error が発生します。変換に問題があるものの必ずしも致命的ではない場合（たとえば feature not supported）には warning が出力されます。warning 付きで変換された設定を使う場合は注意してください。
