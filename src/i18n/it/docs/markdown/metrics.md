---
title: Monitoraggio di Caddy con le metriche
---

# Monitoraggio di Caddy con le metriche

Sia che eseguiate migliaia di istanze di Caddy nel cloud, sia che abbiate un singolo server Caddy su un dispositivo embedded, è probabile che a un certo punto desideriate avere una panoramica di alto livello di ciò che Caddy sta facendo e di quanto tempo impiega. In altre parole, vorrete essere in grado di *monitorare* Caddy.

## Abilitare le metriche

Dovrete attivare le metriche.

Se utilizzate un Caddyfile, abilitate le metriche [nelle opzioni globali](/docs/caddyfile/options#metrics):

```caddy
{
	metrics
}
```

Se utilizzate il JSON, aggiungete `"metrics": {}` alla vostra [configurazione `apps > http > servers`](/docs/json/apps/http/servers/).

Per aggiungere metriche per ciascun host, potete inserire l'opzione `per_host`. Le metriche specifiche per l'host avranno ora un tag `Host`.

```caddy
{
	metrics {
		per_host
	}
}
```

Questa configurazione osserverà gli host configurati. Se è configurato un server HTTPS, l'host viene osservato anche se non esplicitamente configurato, ad esempio in una configurazione TLS on-demand. Se l'HTTPS è disabilitato, vengono abilitati solo gli host configurati a causa del rischio potenziale di cardinalità infinita. Per osservare tutti gli host in una configurazione HTTP, anche quelli non configurati, utilizzate l'opzione `observe_catchall_hosts`.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

## Prometheus

[Prometheus](https://prometheus.io) è una piattaforma di monitoraggio che raccoglie metriche dai target monitorati effettuando lo "scraping" degli endpoint HTTP delle metriche su tali target. Oltre ad aiutarvi a visualizzare le metriche con uno strumento di dashboarding come [Grafana](https://grafana.com/docs/grafana/latest/introduction/), Prometheus viene utilizzato anche per l'[alerting](https://prometheus.io/docs/alerting/latest/overview/).

Come Caddy, Prometheus è scritto in Go e distribuito come un singolo binario. Per installarlo, consultate la [documentazione di installazione di Prometheus](https://prometheus.io/docs/prometheus/latest/installation/), oppure su macOS eseguite semplicemente `brew install prometheus`.

Leggete la [documentazione di Prometheus](https://prometheus.io/docs/introduction/first_steps/) se siete alle prime armi, altrimenti continuate a leggere!

Per configurare Prometheus per lo scraping da Caddy, avrete bisogno di un file di configurazione YAML simile a questo:

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # il valore predefinito è 1 minuto

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

Potete quindi avviare Prometheus in questo modo:

```console
$ prometheus --config.file=prometheus.yaml
```

## OpenTelemetry

Caddy può anche inviare le metriche a un endpoint OpenTelemetry Protocol (OTLP). Questo è utile per stack di osservabilità nativi OTLP, come un OpenTelemetry Collector, Grafana Alloy, Honeycomb o altri sistemi che ricevono direttamente metriche OTLP.

Abilitate l'esportazione delle metriche OTLP con l'opzione `otlp`:

```caddy
{
	metrics {
		otlp
	}
}
```

L'esportatore OTLP viene configurato con le standard [variabili d'ambiente OpenTelemetry](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/), seguendo lo stile di configurazione del [`tracing`](/docs/caddyfile/directives/tracing) di Caddy. Ad esempio:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Per impostazione predefinita, l'esportatore utilizza OTLP su HTTP/protobuf. Impostate `OTEL_EXPORTER_OTLP_PROTOCOL=grpc` per utilizzare invece gRPC. Header, endpoint, protocolli, selezione dell'esportatore e intervalli di raccolta sono controllati da variabili d'ambiente come `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS` e `OTEL_METRIC_EXPORT_INTERVAL`.

Impostate `OTEL_METRICS_EXPORTER=none` per disabilitare l'esportazione delle metriche senza modificare il Caddyfile.

Quando l'esportazione OTLP è abilitata, Caddy esporta le stesse metriche raccolte per l'endpoint Prometheus. Le metriche esportate includono gli attributi risorsa per `web_engine.name` e `web_engine.version`.

## Le metriche di Caddy

Come ogni processo monitorato con Prometheus, Caddy espone un endpoint HTTP che risponde nel [formato di esposizione di Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format). Il client Prometheus di Caddy è configurato anche per rispondere con il [formato di esposizione OpenMetrics](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts) se negoziato (cioè se l'header `Accept` è impostato su `application/openmetrics-text; version=0.0.1`).

Per impostazione predefinita, è disponibile un endpoint `/metrics` presso l'[API di amministrazione](/docs/api) (es. http://localhost:2019/metrics). Tuttavia, se l'API di amministrazione è disabilitata o se desiderate ascoltare su una porta o un percorso diverso, potete usare l'[handler `metrics`](/docs/caddyfile/directives/metrics) per configurarlo.

Potete vedere le metriche con qualsiasi browser o client HTTP come `curl`:

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

Vedrete una serie di metriche che ricadono generalmente in 4 categorie:

- Metriche di runtime
- Metriche dell'API di amministrazione
- Metriche del middleware HTTP
- Metriche del reverse proxy

### Metriche di runtime

Queste metriche riguardano gli aspetti interni del processo Caddy e sono fornite automaticamente dal client Go di Prometheus. Hanno il prefisso `go_*` e `process_*`.

Notate che le metriche `process_*` sono raccolte solo su Linux e Windows.

Consultate la documentazione per il [Go Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector), il [Process Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector) e il [BuildInfo Collector](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector).

### Metriche dell'API di amministrazione

Queste sono metriche che aiutano a monitorare l'API di amministrazione di Caddy. Ognuno degli endpoint di amministrazione è strumentato per tracciare il numero di richieste ed errori.

Queste metriche hanno il prefisso `caddy_admin_*`.

Per esempio:

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/"} 2
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/debug/pprof/cmdline"} 1
caddy_admin_http_requests_total{code="200",handler="load",method="POST",path="/load"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

#### `caddy_admin_http_requests_total`

Un contatore del numero di richieste gestite dagli endpoint di amministrazione, inclusi i moduli nel namespace `admin.api.*`.

Label  | Descrizione
-------|------------
`code` | Codice di stato HTTP
`handler` | Il nome dell'handler o del modulo
`method` | Il metodo HTTP
`path` | Il percorso URL su cui è stato montato l'endpoint di amministrazione

#### `caddy_admin_http_request_errors_total`

Un contatore del numero di errori riscontrati negli endpoint di amministrazione, inclusi i moduli nel namespace `admin.api.*`.

Label  | Descrizione
-------|------------
`handler` | Il nome dell'handler o del modulo
`method` | Il metodo HTTP
`path` | Il percorso URL su cui è stato montato l'endpoint di amministrazione

### Metriche del middleware HTTP

Tutti gli handler del middleware HTTP di Caddy sono strumentati automaticamente per determinare la latenza della richiesta, il tempo per il primo byte (time-to-first-byte), gli errori e le dimensioni dei corpi di richiesta/risposta.

<aside class="tip">
	Poiché tutti gli handler del middleware sono strumentati e molte richieste sono gestite da più handler, assicuratevi di non sommare semplicemente tutti i contatori insieme.
</aside>

Per le metriche istogramma riportate di seguito, i bucket non sono attualmente configurabili. Per le durate, viene utilizzato il set predefinito di bucket [`prometheus.DefBuckets`](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#pkg-variables) (5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s e 10s). Per le dimensioni, i bucket sono 256b, 1kiB, 4kiB, 16kiB, 64kiB, 256kiB, 1MiB e 4MiB.

#### `caddy_http_requests_in_flight`

Un indicatore (gauge) del numero di richieste attualmente gestite da questo server.

Label  | Descrizione
-------|------------
`server` | Il nome del server
`handler` | Il nome dell'handler o del modulo

#### `caddy_http_request_errors_total`

Un contatore degli errori del middleware riscontrati durante la gestione delle richieste.

Label  | Descrizione
-------|------------
`server` | Il nome del server
`handler` | Il nome dell'handler o del modulo

#### `caddy_http_requests_total`

Un contatore delle richieste HTTP(S) effettuate.

Label  | Descrizione
-------|------------
`server` | Il nome del server
`handler` | Il nome dell'handler o del modulo

#### `caddy_http_request_duration_seconds`

Un istogramma delle durate delle richieste (round-trip).

Label  | Descrizione
-------|------------
`server` | Il nome del server
`handler` | Il nome dell'handler o del modulo
`code` | Codice di stato HTTP
`method` | Il metodo HTTP

#### `caddy_http_request_size_bytes`

Un istogramma della dimensione totale (stimata) della richiesta. Include il corpo.

Label  | Descrizione
-------|------------
`server` | Il nome del server
`handler` | Il nome dell'handler o del modulo
`code` | Codice di stato HTTP
`method` | Il metodo HTTP

#### `caddy_http_response_size_bytes`

Un istogramma della dimensione del corpo della risposta restituita.

Label  | Descrizione
-------|------------
`server` | Il nome del server
`handler` | Il nome dell'handler o del modulo
`code` | Codice di stato HTTP
`method` | Il metodo HTTP

#### `caddy_http_response_duration_seconds`

Un istogramma del tempo per il primo byte (time-to-first-byte) delle risposte.

Label  | Descrizione
-------|------------
`server` | Il nome del server
`handler` | Il nome dell'handler o del modulo
`code` | Codice di stato HTTP
`method` | Il metodo HTTP

### Metriche del reverse proxy

#### `caddy_reverse_proxy_upstreams_healthy`

Un indicatore (gauge) dello stato di salute degli upstream del reverse proxy.

Il valore `0` significa che l'upstream non è in salute, mentre `1` significa che l'upstream è in salute.

Label  | Descrizione
-------|------------
`upstream` | Indirizzo dell'upstream

## Esempi di query

Una volta che Prometheus effettua lo scraping delle metriche di Caddy, potete iniziare a vedere alcune metriche interessanti sulle prestazioni di Caddy.

<aside class="tip">
	Se avete avviato un server Prometheus per lo scraping di Caddy con la configurazione sopra riportata, provate a incollare queste query nell'interfaccia utente di Prometheus all'indirizzo [http://localhost:9090/graph](http://localhost:9090/graph)
</aside>


Ad esempio, per vedere il tasso di richieste al secondo, mediato su 5 minuti:

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

Per vedere il tasso con cui viene superata la vostra soglia di latenza di 100ms:

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

Per trovare il 95° percentile della durata della richiesta sull'handler `file_server`, potete usare una query come questa:

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

O per vedere la dimensione mediana della risposta in byte per le richieste `GET` andate a buon fine sull'handler `file_server`:

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
