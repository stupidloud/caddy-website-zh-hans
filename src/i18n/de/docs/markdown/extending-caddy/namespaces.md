---
title: "Module Namespaces"
---

<a id="module-namespaces"></a>
# Module Namespaces

Caddy guest modules werden generisch als Typen `interface{}` oder `any` geladen. Damit host modules sie verwenden können, werden die geladenen guest modules normalerweise zuerst per type assertion in einen bekannten Typ umgewandelt. Diese Seite beschreibt die Zuordnung von module namespaces zu Go-Typen für alle Standardmodule.

Dokumentation zu nicht standardmäßigen module namespaces findest du in der Dokumentation des host module, das sie definiert.

<aside class="tip">
	Eine Art, diese Tabelle zu lesen, ist: "Wenn dein Modul in &lt;namespace&gt; liegt, sollte es als &lt;type&gt; kompilieren."
</aside>

<style>
.table-wrapper {
	padding-left: 0 !important;
	padding-right: 0 !important;
}
</style>

Namespace | Erwarteter Interface-Typ | Beschreibung | Hinweise
--------- | ------------- | ----------- | ----------
|         | [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#App) | Caddy app
admin.api | [`caddy.AdminRouter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#AdminRouter)<br><br>[`caddy.AdminHandler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#AdminHandler) | Registriert HTTP-Routen für admin<br><br>HTTP handler middleware |
caddy.config_loaders | [`caddy.ConfigLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#ConfigLoader) | Lädt eine Konfiguration | <i>⚠️&nbsp;Experimentell</i>
caddy.fs  | [`fs.FS`](https://pkg.go.dev/io/fs#FS) | Virtuelles Dateisystem |  <i>⚠️&nbsp;Experimentell</i>
caddy.listeners | [`caddy.ListenerWrapper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#ListenerWrapper) | Umschließt network listeners
caddy.logging.encoders | [`zapcore.Encoder`](https://pkg.go.dev/go.uber.org/zap/zapcore#Encoder) | Encoder für Logeinträge
caddy.logging.encoders.filter | [`logging.LogFieldFilter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/logging#LogFieldFilter) | Filter für Logfelder
caddy.logging.writers | [`caddy.WriterOpener`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#WriterOpener) | Log writers
caddy.storage | [`caddy.StorageConverter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#StorageConverter) | Storage backends
dns.providers | [`certmagic.DNSProvider`](https://pkg.go.dev/github.com/caddyserver/certmagic#DNSProvider) | Löser für DNS challenge
events.handlers | [`caddyevents.Handler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyevents#Handler) | Event handlers | <i>⚠️&nbsp;Experimentell</i>
http.authentication.hashes | [`caddyauth.Comparer`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Comparer)<br><br>[`caddyauth.Hasher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Hasher) | Password comparers<br><br>Password hashers
http.authentication.providers | [`caddyauth.Authenticator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Authenticator) | HTTP authentication providers
http.encoders | [`encode.Encoding`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Encoding)<br><br>[`encode.Encoder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Encoder) | Erstellt einen Encoder (Kompression)<br><br>Codiert einen Datenstrom
http.handlers | [`caddyhttp.MiddlewareHandler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#MiddlewareHandler) | HTTP handlers
http.ip_sources | [`caddyhttp.IPRangeSource`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#IPRangeSource) | IP-Bereiche für trusted proxies
http.matchers | [`caddyhttp.RequestMatcher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#RequestMatcher)<br><br>[`caddyhttp.RequestMatcherWithError`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#RequestMatcherWithError)<br><br>[`caddyhttp.CELLibraryProducer`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#CELLibraryProducer) | Request matcher (stattdessen WithError verwenden)<br><br>Request matcher mit error short-circuit<br><br>Unterstützung für CEL-Ausdrücke | <i>⚠️&nbsp;Veraltet</i><br><br><br><br><i>(Optional)</i>
http.precompressed | [`encode.Precompressed`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Precompressed) | Unterstützte precompress mappings
http.reverse_proxy.circuit_breakers | [`reverseproxy.CircuitBreaker`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#CircuitBreaker) | Reverse proxy circuit breakers
http.reverse_proxy.selection_policies | [`reverseproxy.Selector`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#Selector) | Load balancing selection policies
http.reverse_proxy.transport | [`http.RoundTripper`](https://pkg.go.dev/net/http#RoundTripper) | HTTP reverse proxy transports
http.reverse_proxy.upstreams | [`reverseproxy.UpstreamSource`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#UpstreamSource) | Dynamische upstream source | <i>⚠️&nbsp;Experimentell</i>
tls.ca_pool.source | [`caddytls.CA`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#CA) | Quelle vertrauenswürdiger root certs
tls.certificates | [`caddytls.CertificateLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#CertificateLoader) | TLS certificate source
tls.client_auth | [`caddytls.ClientCertificateVerifier`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ClientCertificateVerifier) | Verifiziert Client-Zertifikate
tls.ech.publishers | [`caddytls.ECHPublisher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ECHPublisher) | Veröffentlicht Encrypted ClientHello (ECH)-Konfigurationen | <i>⚠️&nbsp;Experimentell</i>
tls.get_certificate | [`certmagic.Manager`](https://pkg.go.dev/github.com/caddyserver/certmagic#Manager) | TLS certificate manager | <i>⚠️&nbsp;Experimentell</i>
tls.handshake_match | [`caddytls.ConnectionMatcher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ConnectionMatcher) | TLS connection matcher
tls.issuance | [`certmagic.Issuer`](https://pkg.go.dev/github.com/caddyserver/certmagic#Issuer) | TLS certificate issuer
tls.leaf_cert_loader | [`caddytls.LeafCertificateLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#LeafCertificateLoader) | Lädt vertrauenswürdige leaf certs
tls.permission | [`caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission) | Ob ein Zertifikat für eine Domain bezogen werden soll | <i>⚠️&nbsp;Experimentell</i>
tls.stek | [`caddytls.STEKProvider`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#STEKProvider) | TLS session ticket key source
tls.context | [`caddytls.HandshakeContext`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#HandshakeContext) | Intercept GetCertificate context | <i>⚠️&nbsp;Experimentell</i>

Namespaces, die als "Experimentell" markiert sind, können sich ändern. (Bitte entwickle mit ihnen, damit wir ihre Interfaces finalisieren können!)
