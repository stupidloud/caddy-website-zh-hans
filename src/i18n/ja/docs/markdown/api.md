---
title: "API"
---

# API

Caddy は、HTTP から [REST <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Representational_state_transfer) API でアクセスできる管理エンドポイントを通じて設定します。このエンドポイントは Caddy の設定で[設定できます](/docs/json/admin/)。

**デフォルトのアドレス: `localhost:2019`**

デフォルトのアドレスは、`CADDY_ADMIN` 環境変数を設定することで変更できます。インストール方法によっては、別の値に設定されている場合があります。Caddy の設定内のアドレスは、常にデフォルトより優先されます。

<aside class="tip">
	信頼できないコードをサーバー上で実行している場合（うわあ 😬）、プロセスを分離し、脆弱なプログラムにパッチを当て、権限付き unix socket に bind するようエンドポイントを設定して、admin endpoint を必ず保護してください。
</aside>

変更後の最新の設定は、[無効化](/docs/json/admin/config/)されていない限りディスクに保存されます。再起動後は [`caddy run --resume`](/docs/command-line#caddy-run) で直近の動作していた設定を再開できます。これにより、電源断などが起きても設定の永続性が保証されます。

API を使い始めるには、[API tutorial](/docs/api-tutorial) を試してください。時間が 1 分しかない場合は、[API quick-start guide](/docs/quick-starts/api) を参照してください。

---

- **[POST /load](#post-load)**
  有効な設定をセットまたは置き換える

- **[POST /stop](#post-stop)**
  有効な設定を停止し、プロセスを終了する

- **[GET /config/[path]](#get-configpath)**
  指定した path の設定をエクスポートする

- **[POST /config/[path]](#post-configpath)**
  オブジェクトをセットまたは置き換え、配列には追加する

- **[PUT /config/[path]](#put-configpath)**
  新しいオブジェクトを作成し、配列には挿入する

- **[PATCH /config/[path]](#patch-configpath)**
  既存のオブジェクトまたは配列要素を置き換える

- **[DELETE /config/[path]](#delete-configpath)**
  指定した path の値を削除する

- **[`@id` を JSON で使う](#using-id-in-json)**
  設定構造内を簡単にたどれるようにする

- **[設定変更の並行実行](#concurrent-config-changes)**
  同期されていない設定変更での衝突を避ける

- **[POST /adapt](#post-adapt)**
  設定を実行せずに JSON へ変換する

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  特定の [PKI app](/docs/json/apps/pki/) CA に関する情報を返す

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  特定の [PKI app](/docs/json/apps/pki/) CA の証明書チェーンを返す

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  設定済み proxy upstream の現在の状態を返す


## POST /load

Caddy の設定をセットし、以前の設定を上書きします。リロードが完了または失敗するまでブロックします。設定変更は軽量で効率的であり、ダウンタイムは発生しません。新しい設定が何らかの理由で失敗した場合、古い設定がダウンタイムなしで元に戻されます。

このエンドポイントは、config adapter を使って複数の設定形式に対応します。リクエストの Content-Type header は、リクエストボディで使われている設定形式を示します。通常は、Caddy のネイティブ設定形式を表す `application/json` を使います。別の設定形式では、スラッシュ `/` の後の値が使用する config adapter 名になるよう、適切な Content-Type を指定してください。たとえば Caddyfile を送信する場合は `text/caddyfile` のような値を使います。JSON 5 の場合は `application/json5` などを使います。

新しい設定が現在の設定と同じ場合、リロードは行われません。強制的にリロードするには、リクエスト header に `Cache-Control: must-revalidate` を設定します。

<a id="examples"></a>
### 例

新しい有効な設定をセットする:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

注: curl の `-d` フラグは改行を削除するため、設定形式が改行に依存する場合（例: Caddyfile）は、代わりに `--data-binary` を使ってください。

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## POST /stop

サーバーを正常にシャットダウンし、プロセスを終了します。プロセスを終了せずに実行中の設定だけを停止するには、[DELETE /config/](#delete-configpath) を使います。

<a id="example"></a>
### 例

プロセスを停止する:

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


## GET /config/[path]

指定した path にある Caddy の現在の設定をエクスポートします。JSON ボディを返します。

<a id="examples-1"></a>
### 例

設定全体をエクスポートし、整形して表示する:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					]
				}
			}
		}
	}
}</code></pre>

listener address だけをエクスポートする:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[":443"]</code></pre>



## POST /config/[path]

指定した path にある Caddy の設定を、リクエストの JSON ボディに変更します。宛先の値が配列なら POST は追加し、オブジェクトなら作成または置き換えます。

特別なケースとして、次の条件を満たす場合は配列へ複数の項目を追加できます。

1. path が `/...` で終わる
2. `/...` の前の path 要素が配列を参照している
3. payload が配列である

この場合、payload の配列内の要素が展開され、それぞれが宛先の配列へ追加されます。Go で表すと、次と同じ効果になります。

```go
baseSlice = append(baseSlice, newElems...)
```

<a id="examples-2"></a>
### 例

listener address を追加する:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

複数の listener address を追加する:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

## PUT /config/[path]

指定した path にある Caddy の設定を、リクエストの JSON ボディに変更します。宛先の値が配列内の位置（index）なら PUT は挿入し、オブジェクトなら厳密に新しい値を作成します。

<a id="example-1"></a>
### 例

最初の slot に listener address を追加する:

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


## PATCH /config/[path]

指定した path にある Caddy の設定を、リクエストの JSON ボディに変更します。PATCH は既存の値または配列要素だけを置き換えます。

<a id="example-2"></a>
### 例

listener address を置き換える:

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>



## DELETE /config/[path]

指定した path にある Caddy の設定を削除します。DELETE は対象の値を削除します。

<a id="examples-3"></a>
### 例

現在の設定全体をアンロードし、プロセスは実行したままにする:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

HTTP server の 1 つだけを停止する:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


<a id="using-id-in-json"></a>
## `@id` を JSON で使う

JSON ドキュメント内に ID を埋め込むと、JSON のその部分へ直接アクセスしやすくなります。

単に `"@id"` というフィールドをオブジェクトに追加し、一意の名前を付けます。たとえば、頻繁にアクセスしたい reverse proxy handler がある場合は次のようにします。

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

使用するには、対応する `/config/` endpoint と同じように `/id/` API endpoint へリクエストします。ただし、path 全体は不要です。ID によって、その設定の scope へ直接移動できます。

たとえば、ID なしで reverse proxy の upstreams にアクセスする場合、path は次のようになります。

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

しかし ID を使うと、path は次のようになります。

```
/id/my_proxy/upstreams
```

こちらの方が覚えやすく、手で書きやすくなります。

<a id="concurrent-config-changes"></a>
## 設定変更の並行実行

<aside class="tip">

このセクションはすべての `/config/` endpoint が対象です。これは実験的であり、変更される可能性があります。

</aside>


Caddy の config API は、個々のリクエストに対して [ACID guarantees <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/ACID) を提供します。しかし、複数のリクエストにまたがる変更は、適切に同期しないと衝突やデータ損失が起こる可能性があります。

たとえば、2 つの client が同時に `GET /config/foo` を実行し、その scope（config path）内で編集してから、同時に `POST|PUT|PATCH|DELETE /config/foo/...` を呼び出して変更を適用すると、衝突が起きます。どちらか一方が他方を上書きするか、2 番目の変更が、準備時とは異なる設定バージョンに適用されて意図しない状態になる可能性があります。これは、それぞれの変更が互いを認識していないためです。

Caddy の API は、複数リクエストにまたがる transaction をサポートしておらず、HTTP は stateless protocol です。ただし、`Etag` と `If-Match` header を使えば、あらゆる変更について楽観的 concurrency control の一種として衝突を検出し、防止できます。これは、Caddy の `/config/...` endpoint を同期なしで並行利用する可能性がある場合に有用です。`GET /config/...` リクエストへのすべてのレスポンスには、`Etag` という HTTP header があり、その scope 内の path と内容の hash が含まれます（例: `Etag: "/config/apps/http/servers 65760b8e"`）。変更系リクエストでは、以前の `GET` リクエストから得た Etag header の値を `If-Match` header に設定するだけです。

基本的なアルゴリズムは次のとおりです。

1. 設定内の任意の scope `S` へ `GET` リクエストを実行します。レスポンスの `Etag` header を保持します。
2. 返された設定に目的の変更を加えます。
3. scope `S` 内で `POST|PUT|PATCH|DELETE` リクエストを実行し、保存しておいた `Etag` 値を `If-Match` リクエスト header に設定します。
4. レスポンスが HTTP 412 (Precondition Failed) の場合は、手順 1 からやり直すか、試行回数が多すぎる場合は諦めます。

このアルゴリズムにより、明示的な同期を行わなくても、Caddy の設定に対する複数の重なり合う変更を安全に扱えます。設定の異なる部分への同時変更では retry が不要になるよう設計されています。衝突を起こし得る、つまり retry が必要になり得るのは、同じ設定 scope に重なる変更だけです。


## POST /adapt

設定を読み込んだり実行したりせずに、Caddy JSON へ変換します。成功すると、結果の JSON ドキュメントがレスポンスボディで返されます。

Content-Type header は、[/load](#post-load) と同じ方法で設定形式を指定するために使われます。たとえば Caddyfile を変換するには、`Content-Type: text/caddyfile` を設定します。

このエンドポイントは、関連する [config adapter](/docs/config-adapters) が Caddy build に組み込まれていれば、どの設定形式でも変換できます。

<a id="examples-4"></a>
### 例

Caddyfile を JSON へ変換する:

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## GET /pki/ca/&lt;id&gt;

特定の [PKI app](/docs/json/apps/pki/) CA について、その ID による情報を返します。リクエストされた CA ID がデフォルト（`local`）の場合、CA がまだ provision されていなければ provision されます。他の CA ID は、以前に provision されていない場合は error を返します。

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


## GET /pki/ca/&lt;id&gt;/certificates

特定の [PKI app](/docs/json/apps/pki/) CA の証明書チェーンを、その ID によって返します。リクエストされた CA ID がデフォルト（`local`）の場合、CA がまだ provision されていなければ provision されます。他の CA ID は、以前に provision されていない場合は error を返します。

このエンドポイントは、CA の root certificate を system の trust store にインストールできるよう、[`caddy trust`](/docs/command-line#caddy-trust) コマンドによって内部的に使われます。

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


## GET /reverse_proxy/upstreams

設定済み reverse proxy upstream（backend）の現在の状態を JSON ドキュメントとして返します。

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

JSON 配列の各 entry は、global upstream pool に保存されている設定済みの [upstream](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/) です。

- **address** は upstream の dial address です。
- **num_requests** は、その upstream が現在処理している active request の数です。
- **fails** は、passive health check の設定に従って記憶されている、現在の失敗リクエスト数です。

目的が backend の可用性を判断することなら、使用している handler 設定と照らし合わせて、upstream の関連プロパティを確認する必要があります。たとえば proxy で [passive health checks](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/) を有効化している場合、upstream が利用可能と見なされるかを判断するには、`fails` と `num_requests` の値も考慮する必要があります。`fails` が proxy に設定した最大失敗数（つまり [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/)）未満であること、また `num_requests` が upstream あたりの最大リクエスト数（proxy 全体では [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/)、個別 upstream では [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/)）以下であることを確認してください。
