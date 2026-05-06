---
title: Monitorando o Caddy com métricas
---

# Monitorando o Caddy com métricas

Quer você esteja rodando milhares de instâncias do Caddy na nuvem, ou um único servidor Caddy em um dispositivo embarcado, é provável que em algum momento você queira ter uma visão geral de alto nível do que o Caddy está fazendo e de quanto tempo isso está levando. Em outras palavras, você vai querer conseguir _monitorar_ o Caddy.

## Habilitando métricas

Você precisará ligar as métricas.

Se estiver usando um Caddyfile, habilite métricas [nas opções globais](/docs/caddyfile/options#metrics):

```caddy
{
	metrics
}
```

Se estiver usando JSON, adicione `"metrics": {}` à sua [configuração `apps > http > servers`](/docs/json/apps/http/servers/).

Para adicionar métricas por host, você pode inserir a opção `per_host`. As métricas específicas de host agora terão uma tag Host.

```caddy
{
	metrics {
		per_host
	}
}
```

Essa configuração observará os hosts configurados. Se um servidor HTTPS estiver configurado, o host será observado, mesmo que não esteja explicitamente configurado, por exemplo, em uma configuração on-demand TLS. Se HTTPS estiver desabilitado, apenas os hosts configurados serão habilitados devido ao risco potencial de cardinalidade infinita. Para observar todos os hosts em uma configuração HTTP, inclusive os não configurados, use a opção `observe_catchall_hosts`.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

## Prometheus

[Prometheus](https://prometheus.io) é uma plataforma de monitoramento que coleta métricas de alvos monitorados fazendo scrape de endpoints HTTP de métricas nesses alvos. Além de ajudar você a exibir métricas com uma ferramenta de dashboards como o [Grafana](https://grafana.com/docs/grafana/latest/introduction/), o Prometheus também é usado para [alerting](https://prometheus.io/docs/alerting/latest/overview/).

Assim como o Caddy, o Prometheus é escrito em Go e distribuído como um único binário. Para instalá-lo, veja a [documentação de instalação do Prometheus](https://prometheus.io/docs/prometheus/latest/installation/), ou no MacOS basta executar `brew install prometheus`.

Leia a [documentação do Prometheus](https://prometheus.io/docs/introduction/first_steps/) se você está começando agora com Prometheus; caso contrário, continue lendo!

Para configurar o Prometheus para fazer scrape do Caddy, você precisará de um arquivo de configuração YAML parecido com este:

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # padrão é 1 minuto

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

Então você pode iniciar o Prometheus assim:

```console
$ prometheus --config.file=prometheus.yaml
```

## OpenTelemetry

O Caddy também pode enviar métricas para um endpoint do OpenTelemetry Protocol (OTLP). Isso é útil para stacks de observabilidade nativas de OTLP, como um OpenTelemetry Collector, Grafana Alloy, Honeycomb ou outros sistemas que recebem métricas OTLP diretamente.

Habilite a exportação de métricas OTLP com a opção `otlp`:

```caddy
{
	metrics {
		otlp
	}
}
```

O exporter OTLP é configurado com as variáveis de ambiente padrão do [OpenTelemetry](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/), seguindo o estilo de configuração da diretiva [`tracing`](/docs/caddyfile/directives/tracing) do Caddy. Por exemplo:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Por padrão, o exporter usa OTLP sobre HTTP/protobuf. Defina `OTEL_EXPORTER_OTLP_PROTOCOL=grpc` para usar gRPC em vez disso. Headers, endpoints, protocolos, seleção de exporter e intervalos de coleta são controlados por variáveis de ambiente como `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS` e `OTEL_METRIC_EXPORT_INTERVAL`.

Defina `OTEL_METRICS_EXPORTER=none` para desabilitar a exportação de métricas sem alterar o Caddyfile.

Quando a exportação OTLP está habilitada, o Caddy exporta as mesmas métricas coletadas para o endpoint Prometheus. As métricas exportadas incluem atributos de recurso para `web_engine.name` e `web_engine.version`.

## Métricas do Caddy

Como qualquer processo monitorado com Prometheus, o Caddy expõe um endpoint HTTP que responde no [formato de exposição do Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format). O client Prometheus do Caddy também é configurado para responder no [formato de exposição OpenMetrics](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts) se isso for negociado (isto é, se o cabeçalho `Accept` estiver definido como `application/openmetrics-text; version=0.0.1`).

Por padrão, há um endpoint `/metrics` disponível na [admin API](/docs/api) (ou seja, http://localhost:2019/metrics). Mas se a admin API estiver desabilitada ou você quiser escutar em uma porta ou path diferente, pode usar o [handler `metrics`](/docs/caddyfile/directives/metrics) para configurar isso.

Você pode ver as métricas com qualquer navegador ou cliente HTTP como `curl`:

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

Há várias métricas que você verá, e elas se enquadram amplamente em 4 categorias:

- Métricas de runtime
- Métricas da Admin API
- Métricas do middleware HTTP
- Métricas do reverse proxy

### Métricas de runtime

Essas métricas cobrem os mecanismos internos do processo Caddy e são fornecidas automaticamente pelo Prometheus Go Client. Elas são prefixadas com `go_*` e `process_*`.

Observe que as métricas `process_*` só são coletadas em Linux e Windows.

Veja a documentação do [Go Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector),
[Process Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector)
e [BuildInfo Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector).

### Métricas da Admin API

Essas são métricas que ajudam a monitorar a Admin API do Caddy. Cada um dos endpoints de administração é instrumentado para acompanhar contagens de requisições e erros.

Essas métricas são prefixadas com `caddy_admin_*`.

Por exemplo:

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/"} 2
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/cmdline"} 1
caddy_admin_http_requests_total{code="200",handler="load",method="POST",path="/load"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

#### `caddy_admin_http_requests_total`

Uma contagem do número de requisições tratadas pelos endpoints de administração, incluindo módulos no namespace `admin.api.*`.

Label  | Descrição
-------|------------
`code` | Código de status HTTP
`handler` | O handler ou nome do módulo
`method` | O método HTTP
`path` | O path URL onde o endpoint de administração foi montado

#### `caddy_admin_http_request_errors_total`

Uma contagem do número de erros encontrados nos endpoints de administração, incluindo módulos no namespace `admin.api.*`.

Label  | Descrição
-------|------------
`handler` | O handler ou nome do módulo
`method` | O método HTTP
`path` | O path URL onde o endpoint de administração foi montado

### Métricas do middleware HTTP

Todos os handlers de middleware HTTP do Caddy são instrumentados automaticamente para determinar latência da requisição, time-to-first-byte, erros e tamanhos de corpo da requisição/resposta.

<aside class="tip">
	Como todos os handlers de middleware são instrumentados, e muitas requisições são tratadas por vários handlers, certifique-se de não simplesmente somar todos os contadores.
</aside>

Para as métricas histogramadas abaixo, os buckets atualmente não são configuráveis.
Para durações, é usado o conjunto padrão de buckets ([`prometheus.DefBuckets`](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#pkg-variables)) (5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s e 10s).
Para tamanhos, os buckets são 256b, 1kiB, 4kiB, 16kiB, 64kiB, 256kiB, 1MiB e 4MiB.

#### `caddy_http_requests_in_flight`

Um gauge do número de requisições atualmente sendo tratadas por este servidor.

Label  | Descrição
-------|------------
`server` | O nome do servidor
`handler` | O handler ou nome do módulo

#### `caddy_http_request_errors_total`

Uma contagem de erros de middleware encontrados ao tratar requisições.

Label  | Descrição
-------|------------
`server` | O nome do servidor
`handler` | O handler ou nome do módulo

#### `caddy_http_requests_total`

Uma contagem de requisições HTTP(S) feitas.

Label  | Descrição
-------|------------
`server` | O nome do servidor
`handler` | O handler ou nome do módulo

#### `caddy_http_request_duration_seconds`

Um histograma das durações de round-trip da requisição.

Label  | Descrição
-------|------------
`server` | O nome do servidor
`handler` | O handler ou nome do módulo
`code` | Código de status HTTP
`method` | O método HTTP

#### `caddy_http_request_size_bytes`

Um histograma do tamanho total (estimado) da requisição. Inclui o corpo.

Label  | Descrição
-------|------------
`server` | O nome do servidor
`handler` | O handler ou nome do módulo
`code` | Código de status HTTP
`method` | O método HTTP

#### `caddy_http_response_size_bytes`

Um histograma do tamanho do corpo da resposta retornada.

Label  | Descrição
-------|------------
`server` | O nome do servidor
`handler` | O handler ou nome do módulo
`code` | Código de status HTTP
`method` | O método HTTP

#### `caddy_http_response_duration_seconds`

Um histograma do time-to-first-byte das respostas.

Label  | Descrição
-------|------------
`server` | O nome do servidor
`handler` | O handler ou nome do módulo
`code` | Código de status HTTP
`method` | O método HTTP

### Métricas do reverse proxy

#### `caddy_reverse_proxy_upstreams_healthy`

Um gauge da saúde dos upstreams do reverse proxy.

Valor `0` significa que o upstream está doente, enquanto `1` significa que o upstream está saudável.

Label  | Descrição
-------|------------
`upstream` | Endereço do upstream

## Consultas de exemplo

Depois que você estiver fazendo o Prometheus fazer scrape das métricas do Caddy, pode começar a ver algumas métricas interessantes sobre como o Caddy está performando.

<aside class="tip">

Se você iniciou um servidor Prometheus para fazer scrape do Caddy com a configuração acima, tente colar estas consultas na UI do Prometheus em [http://localhost:9090/graph](http://localhost:9090/graph)

</aside>

Por exemplo, para ver a taxa de requisições por segundo, média ao longo de 5 minutos:

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

Para ver a taxa na qual o seu limite de latência de 100ms está sendo excedido:

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

Para encontrar o percentil 95 da duração de requisição no handler `file_server`, você pode usar uma consulta como esta:

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

Ou, para ver o tamanho mediano da resposta em bytes para requisições `GET` bem-sucedidas no handler `file_server`:

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
