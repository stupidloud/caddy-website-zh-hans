---
title: "Espacios de nombres de módulos"
---

# Espacios de nombres de módulos

Los módulos invitado de Caddy se cargan de forma genérica como tipos `interface{}` o `any`. Para que los módulos anfitriones puedan utilizarlos, normalmente se hace una aserción de tipo de los módulos invitado a un tipo conocido primero. Esta página describe el mapeo de espacios de nombres de módulos a tipos de Go para todos los módulos estándar.

La documentación de los espacios de nombres de módulos no estándar se puede encontrar en la documentación del módulo anfitrión que los define.

<aside class="tip">
	Una forma de leer esta tabla es: "Si tu módulo está en &lt;namespace&gt;, entonces debería compilar como &lt;type&gt;."
</aside>

<style>
.table-wrapper {
	padding-left: 0 !important;
	padding-right: 0 !important;
}
</style>

Espacio de nombres | Tipo de interfaz esperado | Descripción | Notas
--------- | ------------- | ----------- | ----------
|         | [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#App) | Aplicación de Caddy
admin.api | [`caddy.AdminRouter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#AdminRouter)<br><br>[`caddy.AdminHandler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#AdminHandler) | Registra rutas HTTP para administración<br><br>Middleware de manejador HTTP |
caddy.config_loaders | [`caddy.ConfigLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#ConfigLoader) | Carga una configuración | <i>⚠️&nbsp;Experimental</i>
caddy.fs  | [`fs.FS`](https://pkg.go.dev/io/fs#FS) | Sistema de archivos virtual |  <i>⚠️&nbsp;Experimental</i>
caddy.listeners | [`caddy.ListenerWrapper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#ListenerWrapper) | Envuelve listeners de red
caddy.logging.encoders | [`zapcore.Encoder`](https://pkg.go.dev/go.uber.org/zap/zapcore#Encoder) | Codificador de entradas de registro
caddy.logging.encoders.filter | [`logging.LogFieldFilter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/logging#LogFieldFilter) | Filtro de campos de registro
caddy.logging.writers | [`caddy.WriterOpener`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#WriterOpener) | Escritores de registro
caddy.storage | [`caddy.StorageConverter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#StorageConverter) | Backends de almacenamiento
dns.providers | [`certmagic.DNSProvider`](https://pkg.go.dev/github.com/caddyserver/certmagic#DNSProvider) | Solucionador de desafío DNS
events.handlers | [`caddyevents.Handler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyevents#Handler) | Manejadores de eventos | <i>⚠️&nbsp;Experimental</i>
http.authentication.hashes | [`caddyauth.Comparer`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Comparer)<br><br>[`caddyauth.Hasher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Hasher) | Comparadores de contraseña<br><br>Hashers de contraseña
http.authentication.providers | [`caddyauth.Authenticator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Authenticator) | Proveedores de autenticación HTTP
http.encoders | [`encode.Encoding`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Encoding)<br><br>[`encode.Encoder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Encoder) | Crea un codificador (compresión)<br><br>Codifica un flujo de datos
http.handlers | [`caddyhttp.MiddlewareHandler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#MiddlewareHandler) | Manejadores HTTP
http.ip_sources | [`caddyhttp.IPRangeSource`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#IPRangeSource) | Rangos IP para proxies de confianza
http.matchers | [`caddyhttp.RequestMatcher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#RequestMatcher)<br><br>[`caddyhttp.RequestMatcherWithError`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#RequestMatcherWithError)<br><br>[`caddyhttp.CELLibraryProducer`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#CELLibraryProducer) | Request matcher (usa WithError en su lugar)<br><br>Request matcher con salida por error anticipado<br><br>Compatibilidad con expresiones CEL | <i>⚠️&nbsp;Obsoleto</i><br><br><br><br><i>(Opcional)</i>
http.precompressed | [`encode.Precompressed`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Precompressed) | Mapeos de precompresión soportados
http.reverse_proxy.circuit_breakers | [`reverseproxy.CircuitBreaker`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#CircuitBreaker) | Breakers de circuito de reverse proxy
http.reverse_proxy.selection_policies | [`reverseproxy.Selector`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#Selector) | Políticas de selección de balanceo de carga
http.reverse_proxy.transport | [`http.RoundTripper`](https://pkg.go.dev/net/http#RoundTripper) | Transportes de reverse proxy HTTP
http.reverse_proxy.upstreams | [`reverseproxy.UpstreamSource`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#UpstreamSource) | Fuente de upstream dinámica | <i>⚠️&nbsp;Experimental</i>
tls.ca_pool.source | [`caddytls.CA`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#CA) | Fuente de certificados raíz confiables
tls.certificates | [`caddytls.CertificateLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#CertificateLoader) | Fuente de certificados TLS
tls.client_auth | [`caddytls.ClientCertificateVerifier`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ClientCertificateVerifier) | Verifica certificados de cliente
tls.ech.publishers | [`caddytls.ECHPublisher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ECHPublisher) | Publica configuraciones de Encrypted ClientHello (ECH) | <i>⚠️&nbsp;Experimental</i>
tls.get_certificate | [`certmagic.Manager`](https://pkg.go.dev/github.com/caddyserver/certmagic#Manager) | Gestor de certificados TLS | <i>⚠️&nbsp;Experimental</i>
tls.handshake_match | [`caddytls.ConnectionMatcher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ConnectionMatcher) | Matcher de conexión TLS
tls.issuance | [`certmagic.Issuer`](https://pkg.go.dev/github.com/caddyserver/certmagic#Issuer) | Emisor de certificados TLS
tls.leaf_cert_loader | [`caddytls.LeafCertificateLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#LeafCertificateLoader) | Carga certificados leaf de confianza
tls.permission | [`caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission) | Si obtener un certificado para un dominio | <i>⚠️&nbsp;Experimental</i>
tls.stek | [`caddytls.STEKProvider`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#STEKProvider) | Fuente de clave de tickets de sesión TLS
tls.context | [`caddytls.HandshakeContext`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#HandshakeContext) | Intercepta contexto de GetCertificate | <i>⚠️&nbsp;Experimental</i>

Los espacios de nombres marcados como "Experimental" pueden cambiar. (Por favor, úsalo para que podamos finalizar sus interfaces.)
