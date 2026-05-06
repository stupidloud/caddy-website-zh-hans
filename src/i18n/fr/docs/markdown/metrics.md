---
title: Surveiller Caddy avec des métriques
---

# Surveiller Caddy avec des métriques

Que vous fassiez tourner des milliers d'instances Caddy dans le cloud ou un seul serveur Caddy sur un appareil embarqué, il est probable qu'à un moment donné vous souhaitiez avoir une vue d'ensemble de ce que fait Caddy et du temps que cela prend. En d'autres termes, vous allez vouloir *surveiller* Caddy.

## Activer les métriques

Vous devrez activer les métriques.

Si vous utilisez un Caddyfile, activez les métriques dans les [options globales](/docs/caddyfile/options#metrics) :

```caddy
{
	metrics
}
```

Si vous utilisez le format JSON, ajoutez `"metrics": {}` à votre [configuration `apps > http > servers`](/docs/json/apps/http/servers/).

Pour ajouter des métriques par hôte, vous pouvez insérer l'option `per_host`. Les métriques spécifiques aux hôtes auront désormais une balise (tag) Host.

```caddy
{
	metrics {
		per_host
	}
}
```

Cette configuration observera les hôtes configurés. Si un serveur HTTPS est configuré, l'hôte est observé, même s'il n'est pas explicitement configuré (par exemple avec une installation TLS à la demande). Si le HTTPS est désactivé, seuls les hôtes configurés sont activés en raison du risque potentiel de cardinalité infinie. Pour observer tous les hôtes dans une installation HTTP, même ceux non configurés, utilisez l'option `observe_catchall_hosts`.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

## Prometheus

[Prometheus](https://prometheus.io) est une plateforme de surveillance qui collecte les métriques de cibles surveillées en interrogeant (scraping) leurs points d'accès HTTP de métriques. En plus de vous aider à afficher des métriques avec un outil de tableau de bord comme [Grafana](https://grafana.com/docs/grafana/latest/introduction/), Prometheus est également utilisé pour l'[alerte](https://prometheus.io/docs/alerting/latest/overview/).

Comme Caddy, Prometheus est écrit en Go et distribué sous forme de binaire unique. Pour l'installer, consultez la [documentation d'installation de Prometheus](https://prometheus.io/docs/prometheus/latest/installation/), ou sur macOS, lancez simplement `brew install prometheus`.

Consultez la [documentation de Prometheus](https://prometheus.io/docs/introduction/first_steps/) si vous débutez avec Prometheus, sinon continuez votre lecture !

Pour configurer Prometheus afin qu'il interroge Caddy, vous aurez besoin d'un fichier de configuration YAML semblable à celui-ci :

```yaml
# prometheus.yaml
global:
  scrape_interval: 15s # par défaut : 1 minute

scrape_configs:
  - job_name: caddy
    static_configs:
      - targets: ['localhost:2019']
```

Vous pouvez ensuite lancer Prometheus comme ceci :

```console
$ prometheus --config.file=prometheus.yaml
```

## OpenTelemetry

Caddy peut également envoyer des métriques vers un point d'accès utilisant le protocole OpenTelemetry (OTLP). C'est utile pour les piles d'observabilité natives OTLP, telles qu'un collecteur OpenTelemetry, Grafana Alloy, Honeycomb, ou d'autres systèmes recevant directement des métriques OTLP.

Activez l'exportation des métriques OTLP avec l'option `otlp` :

```caddy
{
	metrics {
		otlp
	}
}
```

L'exportateur OTLP se configure avec les [variables d'environnement standards d'OpenTelemetry](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/), correspondant au style de configuration du [`tracing`](/docs/caddyfile/directives/tracing) de Caddy. Par exemple :

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Par défaut, l'exportateur utilise OTLP via HTTP/protobuf. Définissez `OTEL_EXPORTER_OTLP_PROTOCOL=grpc` pour utiliser gRPC à la place. Les en-têtes, points d'accès, protocoles, sélection d'exportateurs et intervalles de collecte sont contrôlés par des variables d'environnement telles que `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS` et `OTEL_METRIC_EXPORT_INTERVAL`.

Définissez `OTEL_METRICS_EXPORTER=none` pour désactiver l'exportation de métriques sans modifier le Caddyfile.

Lorsque l'exportation OTLP est activée, Caddy exporte les mêmes métriques que celles collectées pour le point d'accès Prometheus. Les métriques exportées incluent des attributs de ressource pour `web_engine.name` et `web_engine.version`.

## Les métriques de Caddy

Comme tout processus surveillé par Prometheus, Caddy expose un point d'accès HTTP qui répond au [format d'exposition de Prometheus](https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format). Le client Prometheus de Caddy est également configuré pour répondre au format d'exposition [OpenMetrics](https://pkg.go.dev/github.com/prometheus/client_golang@v1.7.1/prometheus/promhttp#HandlerOpts) si négocié (c'est-à-dire si l'en-tête `Accept` est défini sur `application/openmetrics-text; version=0.0.1`).

Par défaut, un point d'accès `/metrics` est disponible via l'[API d'administration](/docs/api) (ex: http://localhost:2019/metrics). Mais si l'API d'administration est désactivée ou si vous souhaitez écouter sur un autre port ou chemin, vous pouvez utiliser le [gestionnaire `metrics`](/docs/caddyfile/directives/metrics) pour configurer cela.

Vous pouvez consulter les métriques avec n'importe quel navigateur ou client HTTP comme `curl` :

```console
$ curl http://localhost:2019/metrics
# HELP caddy_admin_http_requests_total Counter of requests made to the Admin API's HTTP endpoints.
# TYPE caddy_admin_http_requests_total counter
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 2
# HELP caddy_http_request_duration_seconds Histogram of round-trip request durations.
# TYPE caddy_http_request_duration_seconds histogram
caddy_http_request_duration_seconds_bucket{code="308",handler="static_response",method="GET",server="remaining_auto_https_redirects",le="0.005"} 1
...
```

Vous verrez de nombreuses métriques, qui se répartissent globalement en 4 catégories :

- Métriques du runtime
- Métriques de l'API d'administration
- Métriques des middlewares HTTP
- Métriques du proxy inverse

### Métriques du runtime

Ces métriques couvrent les composants internes du processus Caddy et sont fournies automatiquement par le client Go de Prometheus. Elles sont préfixées par `go_*` et `process_*`.

Notez que les métriques `process_*` ne sont collectées que sur Linux et Windows.

Consultez la documentation pour le [collecteur Go](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewGoCollector), le [collecteur de processus](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewProcessCollector) et le [collecteur BuildInfo](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#NewBuildInfoCollector).

### Métriques de l'API d'administration

Il s'agit de métriques aidant à surveiller l'API d'administration de Caddy. Chacun des points d'accès d'administration est instrumenté pour suivre le nombre de requêtes et les erreurs.

Ces métriques sont préfixées par `caddy_admin_*`.

Par exemple :

```console
$ curl -s http://localhost:2019/metrics | grep ^caddy_admin
caddy_admin_http_requests_total{code="200",handler="admin",method="GET",path="/config/"} 1
caddy_admin_http_requests_total{code="200",handler="metrics",method="GET",path="/metrics"} 3
```

#### `caddy_admin_http_requests_total`

Un compteur du nombre de requêtes traitées par les points d'accès d'administration, incluant les modules dans l'espace de noms `admin.api.*`.

Label  | Description
-------|------------
`code` | Code d'état HTTP
`handler` | Le nom du gestionnaire ou du module
`method` | La méthode HTTP
`path` | Le chemin URL où le point d'accès administration est monté

#### `caddy_admin_http_request_errors_total`

Un compteur du nombre d'erreurs rencontrées dans les points d'accès d'administration, incluant les modules dans l'espace de noms `admin.api.*`.

Label  | Description
-------|------------
`handler` | Le nom du gestionnaire ou du module
`method` | La méthode HTTP
`path` | Le chemin URL où le point d'accès administration est monté

### Métriques des middlewares HTTP

Tous les gestionnaires de middleware HTTP de Caddy sont automatiquement instrumentés pour déterminer la latence des requêtes, le délai avant le premier octet (time-to-first-byte), les erreurs et les tailles des corps de requête/réponse.

<aside class="tip">
	Comme tous les gestionnaires de middleware sont instrumentés et que de nombreuses requêtes sont traitées par plusieurs gestionnaires, veillez à ne pas simplement additionner tous les compteurs.
</aside>

Pour les métriques d'histogramme ci-dessous, les tranches (buckets) ne sont actuellement pas configurables. Pour les durées, le jeu de tranches par défaut ([`prometheus.DefBuckets`](https://pkg.go.dev/github.com/prometheus/client_golang/prometheus#pkg-variables)) est utilisé (5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s, et 10s). Pour les tailles, les tranches sont 256o, 1kiB, 4kiB, 16kiB, 64kiB, 256kiB, 1MiB et 4MiB.

#### `caddy_http_requests_in_flight`

Une jauge du nombre de requêtes en cours de traitement par ce serveur.

Label  | Description
-------|------------
`server` | Le nom du serveur
`handler` | Le nom du gestionnaire ou du module

#### `caddy_http_request_errors_total`

Un compteur des erreurs de middleware rencontrées lors du traitement des requêtes.

Label  | Description
-------|------------
`server` | Le nom du serveur
`handler` | Le nom du gestionnaire ou du module

#### `caddy_http_requests_total`

Un compteur des requêtes HTTP(S) effectuées.

Label  | Description
-------|------------
`server` | Le nom du serveur
`handler` | Le nom du gestionnaire ou du module

#### `caddy_http_request_duration_seconds`

Un histogramme des durées des requêtes (aller-retour).

Label  | Description
-------|------------
`server` | Le nom du serveur
`handler` | Le nom du gestionnaire ou du module
`code` | Code d'état HTTP
`method` | La méthode HTTP

#### `caddy_http_request_size_bytes`

Un histogramme de la taille totale (estimée) de la requête. Inclut le corps.

Label  | Description
-------|------------
`server` | Le nom du serveur
`handler` | Le nom du gestionnaire ou du module
`code` | Code d'état HTTP
`method` | La méthode HTTP

#### `caddy_http_response_size_bytes`

Un histogramme de la taille du corps de la réponse renvoyée.

Label  | Description
-------|------------
`server` | Le nom du serveur
`handler` | Le nom du gestionnaire ou du module
`code` | Code d'état HTTP
`method` | La méthode HTTP

#### `caddy_http_response_duration_seconds`

Un histogramme du délai avant le premier octet (time-to-first-byte) pour les réponses.

Label  | Description
-------|------------
`server` | Le nom du serveur
`handler` | Le nom du gestionnaire ou du module
`code` | Code d'état HTTP
`method` | La méthode HTTP

### Métriques du proxy inverse

#### `caddy_reverse_proxy_upstreams_healthy`

Une jauge de l'état de santé des serveurs d'amont (upstreams) du proxy inverse.

La valeur `0` signifie que l'amont n'est pas sain, tandis que `1` signifie qu'il est sain.

Label  | Description
-------|------------
`upstream` | Adresse du serveur d'amont

## Exemples de requêtes

Une fois que Prometheus interroge les métriques de Caddy, vous pouvez commencer à voir des métriques intéressantes sur les performances de Caddy.

<aside class="tip">

Si vous avez lancé un serveur Prometheus pour interroger Caddy avec la configuration ci-dessus, essayez de coller ces requêtes dans l'interface Prometheus sur [http://localhost:9090/graph](http://localhost:9090/graph)

</aside>


Par exemple, pour voir le taux de requêtes par seconde, moyenné sur 5 minutes :

```
rate(caddy_http_requests_total{handler="file_server"}[5m])
```

Pour voir le taux auquel votre seuil de latence de 100ms est dépassé :

```
sum(rate(caddy_http_request_duration_seconds_count{server="srv0"}[5m])) by (handler)
-
sum(rate(caddy_http_request_duration_seconds_bucket{le="0.100", server="srv0"}[5m])) by (handler)
```

Pour trouver le 95e percentile de la durée des requêtes sur le gestionnaire `file_server`, vous pouvez utiliser une requête comme celle-ci :

```
histogram_quantile(0.95, sum(caddy_http_request_duration_seconds_bucket{handler="file_server"}) by (le))
```

Ou pour voir la taille médiane des réponses en octets pour les requêtes `GET` réussies sur le gestionnaire `file_server` :

```
histogram_quantile(0.5, caddy_http_response_size_bytes_bucket{method="GET", handler="file_server", code="200"})
```
