---
title: メトリクスで Caddy を監視する
---

<a id="monitoring-caddy-with-metrics"></a>
# メトリクスで Caddy を監視する

クラウドで何千もの Caddy インスタンスを実行している場合でも、組み込みデバイスで単一の Caddy サーバーを実行している場合でも、いずれ Caddy が何をしていて、どれくらい時間がかかっているのかを高いレベルで把握したくなるでしょう。言い換えると、Caddy を *監視* できるようにしたくなります。

<a id="enabling-metrics"></a>
## メトリクスを有効にする

メトリクスを有効にする必要があります。

Caddyfile を使っている場合は、[グローバルオプション](/docs/caddyfile/options#metrics)で metrics を有効にします。

```caddy
{
	metrics
}
```

JSON を使っている場合は、[`apps > http > servers` 設定](/docs/json/apps/http/servers/)に `"metrics": {}` を追加します。

ホスト単位のメトリクスを追加するには、`per_host` オプションを挿入できます。ホスト固有のメトリクスには Host タグが付くようになります。

```caddy
{
	metrics {
		per_host
	}
}
```

この設定は、設定済みホストを監視します。HTTPS サーバーが設定されている場合、明示的に設定されていなくてもホストは監視されます。たとえば on-demand TLS のセットアップが該当します。HTTPS が無効な場合は、無限カーディナリティのリスクがあるため、設定済みホストのみが有効になります。HTTP セットアップで、未設定のものも含めてすべてのホストを監視するには、`observe_catchall_hosts` オプションを使います。

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

<a id="prometheus"></a>
## Prometheus

[Prometheus](https://prometheus.io) は監視プラットフォームで、監視対象のメトリクス HTTP エンドポイントをスクレイプしてメトリクスを収集します。[Grafana](https://grafana.com/docs/grafana/latest/introduction/) のようなダッシュボードツールでメトリクスを表示するのに役立つだけでなく、Prometheus は[アラート](https://prometheus.io/docs/alerting/latest/overview/)にも使われます。

Caddy と同じく、Prometheus は Go で書かれており、単一バイナリとして配布されています。インストール方法は [Prometheus Installation docs](https://prometheus.io/docs/prometheus/latest/installation/) を参照してください。MacOS なら `brew install prometheus` を実行するだけでも構いません。

Prometheus が初めてなら [Prometheus docs](https://prometheus.io/docs/introduction/first_steps/) を読んでください。そうでなければ、このまま読み進めてください。

Caddy からスクレイプするよう Prometheus を設定するには、次のような YAML 設定ファイルが必要です。

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # default is 1 minute

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

次のように Prometheus を起動できます。

```console
$ prometheus --config.file=prometheus.yaml
```

<a id="opentelemetry"></a>
## OpenTelemetry

Caddy は OpenTelemetry Protocol（OTLP）エンドポイントへメトリクスをプッシュすることもできます。これは、OpenTelemetry Collector、Grafana Alloy、Honeycomb、または OTLP メトリクスを直接受け取る他のシステムなど、OTLP ネイティブなオブザーバビリティスタックで便利です。

`otlp` オプションで OTLP メトリクスのエクスポートを有効にします。

```caddy
{
	metrics {
		otlp
	}
}
```

OTLP エクスポーターは標準の [OpenTelemetry 環境変数](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/)で設定され、Caddy の [`tracing`](/docs/caddyfile/directives/tracing) 設定スタイルと一致します。例:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

既定では、エクスポーターは HTTP/protobuf 上の OTLP を使います。代わりに gRPC を使うには `OTEL_EXPORTER_OTLP_PROTOCOL=grpc` を設定します。ヘッダー、エンドポイント、プロトコル、エクスポーター選択、収集間隔は、`OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`、`OTEL_EXPORTER_OTLP_HEADERS`、`OTEL_METRIC_EXPORT_INTERVAL` などの環境変数で制御されます。

Caddyfile を変更せずにメトリクスエクスポートを無効化するには、`OTEL_METRICS_EXPORTER=none` を設定します。

OTLP エクスポートが有効な場合、Caddy は Prometheus エンドポイント用に収集したものと同じメトリクスをエクスポートします。エクスポートされるメトリクスには、`web_engine.name` と `web_engine.version` のリソース属性が含まれます。

<a id="caddys-metrics"></a>
## Caddy のメトリクス

Prometheus で監視されるあらゆるプロセスと同様に、Caddy は [Prometheus exposition format](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format) で応答する HTTP エンドポイントを公開します。Caddy の Prometheus クライアントは、ネゴシエーションされた場合（つまり `Accept` header が `application/openmetrics-text; version=0.0.1` に設定されている場合）に [OpenMetrics exposition format](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts) で応答するようにも設定されています。

既定では、[admin API](/docs/api) に `/metrics` エンドポイントがあります（つまり http://localhost:2019/metrics）。ただし admin API が無効な場合や、別のポートまたはパスで待ち受けたい場合は、[`metrics` handler](/docs/caddyfile/directives/metrics) を使って設定できます。

任意のブラウザや `curl` のような HTTP クライアントでメトリクスを確認できます。

```console
$ curl http://localhost:2019/metrics
# HELP caddy_admin_http_requests_total Counter of requests made to the Admin API's HTTP endpoints.
# TYPE caddy_admin_http_requests_total counter
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 2
# HELP caddy_http_request_duration_seconds Histogram of round-trip request durations.
# TYPE caddy_http_request_duration_seconds histogram
caddy_http_request_duration_seconds_bucket{code="308",handler="static_response",method="GET",server="remaining_auto_https_redirects",le="0.005"} 1
caddy_http_request_duration_seconds_bucket{code="308",handler="static_response",method="GET",server="remaining_auto_https_redirects",le="0.01"} 1
caddy_http_request_duration_seconds_bucket{code="308",handler="static_response",method="GET",server="remaining_auto_https_redirects",le="0.025"} 1
...
```

表示されるメトリクスはいくつかあり、大きく 4 つのカテゴリに分けられます。

- Runtime metrics
- Admin API metrics
- HTTP Middleware metrics
- Reverse proxy metrics

<a id="runtime-metrics"></a>
### Runtime metrics

これらのメトリクスは Caddy プロセスの内部を対象とし、Prometheus Go Client によって自動的に提供されます。`go_*` と `process_*` のプレフィックスが付きます。

`process_*` メトリクスは Linux と Windows でのみ収集される点に注意してください。

[Go Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector)、[Process Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector)、[BuildInfo Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector) のドキュメントを参照してください。

<a id="admin-api-metrics"></a>
### Admin API metrics

これらは Caddy admin API の監視に役立つメトリクスです。各 admin エンドポイントには、リクエスト数とエラーを追跡するための計装が入っています。

これらのメトリクスには `caddy_admin_*` のプレフィックスが付きます。

例:

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/"} 2
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/cmdline"} 1
caddy_admin_http_requests_total{code="200",handler="load",method="POST",path="/load"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

#### `caddy_admin_http_requests_total`

`admin.api.*` 名前空間のモジュールを含む、admin エンドポイントで処理されたリクエスト数のカウンターです。

Label  | Description
-------|------------
`code` | HTTP ステータスコード
`handler` | handler またはモジュール名
`method` | HTTP メソッド
`path` | admin エンドポイントがマウントされた URL パス

#### `caddy_admin_http_request_errors_total`

`admin.api.*` 名前空間のモジュールを含む、admin エンドポイントで発生したエラー数のカウンターです。

Label  | Description
-------|------------
`handler` | handler またはモジュール名
`method` | HTTP メソッド
`path` | admin エンドポイントがマウントされた URL パス

<a id="http-middleware-metrics"></a>
### HTTP Middleware metrics

すべての Caddy HTTP middleware handler は、リクエストレイテンシ、time-to-first-byte、エラー、リクエスト/レスポンス body サイズを測定するために自動的に計装されます。

<aside class="tip">
	すべての middleware handler が計装され、多くのリクエストは複数の handler によって処理されるため、すべてのカウンターを単純に合計しないようにしてください。
</aside>

以下のヒストグラムメトリクスでは、現時点でバケットは設定できません。期間については、既定の [`prometheus.DefBuckets`](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#pkg-variables) バケットセット（5ms、10ms、25ms、50ms、100ms、250ms、500ms、1s、2.5s、5s、10s）が使われます。サイズについては、256b、1kiB、4kiB、16kiB、64kiB、256kiB、1MiB、4MiB のバケットです。

#### `caddy_http_requests_in_flight`

このサーバーで現在処理中のリクエスト数のゲージです。

Label  | Description
-------|------------
`server` | サーバー名
`handler` | handler またはモジュール名

#### `caddy_http_request_errors_total`

リクエスト処理中に発生した middleware エラー数のカウンターです。

Label  | Description
-------|------------
`server` | サーバー名
`handler` | handler またはモジュール名

#### `caddy_http_requests_total`

行われた HTTP(S) リクエスト数のカウンターです。

Label  | Description
-------|------------
`server` | サーバー名
`handler` | handler またはモジュール名

#### `caddy_http_request_duration_seconds`

往復リクエスト時間のヒストグラムです。

Label  | Description
-------|------------
`server` | サーバー名
`handler` | handler またはモジュール名
`code` | HTTP ステータスコード
`method` | HTTP メソッド

#### `caddy_http_request_size_bytes`

リクエストの合計（推定）サイズのヒストグラムです。body を含みます。

Label  | Description
-------|------------
`server` | サーバー名
`handler` | handler またはモジュール名
`code` | HTTP ステータスコード
`method` | HTTP メソッド

#### `caddy_http_response_size_bytes`

返されたレスポンス body のサイズのヒストグラムです。

Label  | Description
-------|------------
`server` | サーバー名
`handler` | handler またはモジュール名
`code` | HTTP ステータスコード
`method` | HTTP メソッド

#### `caddy_http_response_duration_seconds`

レスポンスの time-to-first-byte のヒストグラムです。

Label  | Description
-------|------------
`server` | サーバー名
`handler` | handler またはモジュール名
`code` | HTTP ステータスコード
`method` | HTTP メソッド

<a id="reverse-proxy-metrics"></a>
### Reverse proxy metrics

#### `caddy_reverse_proxy_upstreams_healthy`

reverse proxy upstream の健全性を表すゲージです。

値 `0` は upstream が異常であることを意味し、`1` は upstream が正常であることを意味します。

Label  | Description
-------|------------
`upstream` | upstream のアドレス

<a id="sample-queries"></a>
## クエリ例

Prometheus が Caddy のメトリクスをスクレイプするようになると、Caddy の動作について興味深いメトリクスを確認できるようになります。

<aside class="tip">

上の設定で Caddy をスクレイプする Prometheus サーバーを起動している場合は、これらのクエリを [http://localhost:9090/graph](http://localhost:9090/graph) の Prometheus UI に貼り付けてみてください。

</aside>


たとえば、5 分間で平均した 1 秒あたりのリクエストレートを見るには、次のようにします。

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

100ms のレイテンシしきい値を超えている割合を見るには、次のようにします。

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

`file_server` handler でのリクエスト時間の 95 パーセンタイルを求めるには、次のようなクエリを使えます。

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

または、`file_server` handler で成功した `GET` リクエストのレスポンスサイズ中央値（バイト単位）を見るには、次のようにします。

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
