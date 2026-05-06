---
title: "Namespace dei moduli"
---

# Namespace dei moduli

I moduli guest di Caddy sono caricati genericamente come tipi `interface{}` o `any`. Affinché i moduli host possano utilizzarli, i moduli guest caricati vengono solitamente sottoposti a type-assertion verso un tipo noto. Questa pagina descrive la mappatura dai namespace dei moduli ai tipi Go per tutti i moduli standard.

La documentazione per i namespace dei moduli non standard può essere trovata con la documentazione del modulo host che li definisce.

<aside class="tip">
	Un modo per leggere questa tabella è: "Se il vostro modulo si trova nel &lt;namespace&gt;, allora dovrebbe compilare come &lt;tipo&gt;."
</aside>

<style>
.table-wrapper {
	padding-left: 0 !important;
	padding-right: 0 !important;
}
</style>

Namespace | Tipo interfaccia atteso | Descrizione | Note
--------- | ------------- | ----------- | ----------
|         | [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#App) | App Caddy
admin.api | [`caddy.AdminRouter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#AdminRouter)<br><br>[`caddy.AdminHandler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#AdminHandler) | Registra rotte HTTP per admin<br><br>Middleware handler HTTP |
caddy.config_loaders | [`caddy.ConfigLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#ConfigLoader) | Carica una configurazione | <i>⚠️&nbsp;Sperimentale</i>
caddy.fs  | [`fs.FS`](https://pkg.go.dev/io/fs#FS) | File system virtuale |  <i>⚠️&nbsp;Sperimentale</i>
caddy.listeners | [`caddy.ListenerWrapper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#ListenerWrapper) | Avvolge i listener di rete
caddy.logging.encoders | [`zapcore.Encoder`](https://pkg.go.dev/go.uber.org/zap/zapcore#Encoder) | Encoder voci di log
caddy.logging.encoders.filter | [`logging.LogFieldFilter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/logging#LogFieldFilter) | Filtro campi di log
caddy.logging.writers | [`caddy.WriterOpener`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#WriterOpener) | Writer di log
caddy.storage | [`caddy.StorageConverter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#StorageConverter) | Backend di storage
dns.providers | [`certmagic.DNSProvider`](https://pkg.go.dev/github.com/caddyserver/certmagic#DNSProvider) | Solutore sfida DNS
events.handlers | [`caddyevents.Handler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyevents#Handler) | Handler di eventi | <i>⚠️&nbsp;Sperimentale</i>
http.authentication.hashes | [`caddyauth.Comparer`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Comparer)<br><br>[`caddyauth.Hasher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Hasher) | Comparatori password<br><br>Hasher password
http.authentication.providers | [`caddyauth.Authenticator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Authenticator) | Provider autenticazione HTTP
http.encoders | [`encode.Encoding`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Encoding)<br><br>[`encode.Encoder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Encoder) | Crea un encoder (compressione)<br><br>Codifica un flusso di dati
http.handlers | [`caddyhttp.MiddlewareHandler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#MiddlewareHandler) | Handler HTTP
http.ip_sources | [`caddyhttp.IPRangeSource`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#IPRangeSource) | Intervalli IP per proxy fidati
http.matchers | [`caddyhttp.RequestMatcher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#RequestMatcher)<br><br>[`caddyhttp.RequestMatcherWithError`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#RequestMatcherWithError)<br><br>[`caddyhttp.CELLibraryProducer`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#CELLibraryProducer) | Matcher di richiesta (usa WithError al suo posto)<br><br>Matcher di richiesta con errore short-circuit<br><br>Supporto per espressioni CEL | <i>⚠️&nbsp;Deprecato</i><br><br><br><br><i>(Opzionale)</i>
http.precompressed | [`encode.Precompressed`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Precompressed) | Mappature precompresse supportate
http.reverse_proxy.circuit_breakers | [`reverseproxy.CircuitBreaker`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#CircuitBreaker) | Circuit breaker reverse proxy
http.reverse_proxy.selection_policies | [`reverseproxy.Selector`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#Selector) | Policy di selezione bilanciamento del carico
http.reverse_proxy.transport | [`http.RoundTripper`](https://pkg.go.dev/net/http#RoundTripper) | Trasporti reverse proxy HTTP
http.reverse_proxy.upstreams | [`reverseproxy.UpstreamSource`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#UpstreamSource) | Sorgente upstream dinamica | <i>⚠️&nbsp;Sperimentale</i>
tls.ca_pool.source | [`caddytls.CA`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#CA) | Sorgente di certificati root fidati
tls.certificates | [`caddytls.CertificateLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#CertificateLoader) | Sorgente certificati TLS
tls.client_auth | [`caddytls.ClientCertificateVerifier`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ClientCertificateVerifier) | Verifica certificati client
tls.ech.publishers | [`caddytls.ECHPublisher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ECHPublisher) | Pubblica configurazioni Encrypted ClientHello (ECH) | <i>⚠️&nbsp;Sperimentale</i>
tls.get_certificate | [`certmagic.Manager`](https://pkg.go.dev/github.com/caddyserver/certmagic#Manager) | Gestore certificati TLS | <i>⚠️&nbsp;Sperimentale</i>
tls.handshake_match | [`caddytls.ConnectionMatcher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ConnectionMatcher) | Matcher connessione TLS
tls.issuance | [`certmagic.Issuer`](https://pkg.go.dev/github.com/caddyserver/certmagic#Issuer) | Emittente certificati TLS
tls.leaf_cert_loader | [`caddytls.LeafCertificateLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#LeafCertificateLoader) | Carica certificati foglia fidati
tls.permission | [`caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission) | Se ottenere un certificato per un dominio | <i>⚠️&nbsp;Sperimentale</i>
tls.stek | [`caddytls.STEKProvider`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#STEKProvider) | Sorgente chiave session ticket TLS
tls.context | [`caddytls.HandshakeContext`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#HandshakeContext) | Intercetta contesto GetCertificate | <i>⚠️&nbsp;Sperimentale</i>

I namespace contrassegnati come "Sperimentale" sono soggetti a modifiche. (Sviluppate con essi così da poterne finalizzare le interfacce!)
