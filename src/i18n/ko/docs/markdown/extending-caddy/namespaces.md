---
title: "Module Namespaces"
---

# 모듈 네임스페이스

Caddy 게스트 모듈은 제네릭하게(generically) `interface{}` 또는 `any` 타입으로 로드됩니다. 호스트 모듈이 이들을 사용하려면 로드된 게스트 모듈이 일반적으로 먼저 알려진 타입으로 타입 단언(type-asserted)되어야 합니다. 이 페이지는 모든 표준 모듈에 대한 모듈 네임스페이스에서 Go 타입으로의 매핑(mapping)을 설명합니다.

비표준 모듈 네임스페이스에 대한 문서는 해당 네임스페이스를 정의하는 호스트 모듈의 문서에서 찾을 수 있습니다.

<aside class="tip">
	이 표를 읽는 한 가지 방법은 "내 모듈이 &lt;namespace&gt;에 있다면, &lt;type&gt;으로 컴파일되어야 한다"는 것입니다.
</aside>

<style>
.table-wrapper {
	padding-left: 0 !important;
	padding-right: 0 !important;
}
</style>

Namespace | Expected Interface Type | Description | Notes
--------- | ------------- | ----------- | ----------
|         | [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#App) | Caddy 앱 (Caddy app)
admin.api | [`caddy.AdminRouter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#AdminRouter)<br><br>[`caddy.AdminHandler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#AdminHandler) | 관리자용 HTTP 경로 등록<br><br>HTTP 핸들러 미들웨어 |
caddy.config_loaders | [`caddy.ConfigLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#ConfigLoader) | 설정 로드 | <i>⚠️&nbsp;실험적(Experimental)</i>
caddy.fs  | [`fs.FS`](https://pkg.go.dev/io/fs#FS) | 가상 파일 시스템 |  <i>⚠️&nbsp;실험적(Experimental)</i>
caddy.listeners | [`caddy.ListenerWrapper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#ListenerWrapper) | 네트워크 리스너 래핑(Wrap)
caddy.logging.encoders | [`zapcore.Encoder`](https://pkg.go.dev/go.uber.org/zap/zapcore#Encoder) | 로그 항목(entry) 인코더
caddy.logging.encoders.filter | [`logging.LogFieldFilter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/logging#LogFieldFilter) | 로그 필드 필터
caddy.logging.writers | [`caddy.WriterOpener`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#WriterOpener) | 로그 작성기(writers)
caddy.storage | [`caddy.StorageConverter`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#StorageConverter) | 스토리지 백엔드
dns.providers | [`certmagic.DNSProvider`](https://pkg.go.dev/github.com/caddyserver/certmagic#DNSProvider) | DNS 챌린지 해결기(solver)
events.handlers | [`caddyevents.Handler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyevents#Handler) | 이벤트 핸들러 | <i>⚠️&nbsp;실험적(Experimental)</i>
http.authentication.hashes | [`caddyauth.Comparer`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Comparer)<br><br>[`caddyauth.Hasher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Hasher) | 비밀번호 비교기(comparers)<br><br>비밀번호 해시 생성기(hashers)
http.authentication.providers | [`caddyauth.Authenticator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/caddyauth#Authenticator) | HTTP 인증(authentication) 제공자
http.encoders | [`encode.Encoding`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Encoding)<br><br>[`encode.Encoder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Encoder) | 인코더(압축) 생성<br><br>데이터 스트림 인코딩
http.handlers | [`caddyhttp.MiddlewareHandler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#MiddlewareHandler) | HTTP 핸들러
http.ip_sources | [`caddyhttp.IPRangeSource`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#IPRangeSource) | 신뢰할 수 있는 프록시의 IP 대역
http.matchers | [`caddyhttp.RequestMatcher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#RequestMatcher)<br><br>[`caddyhttp.RequestMatcherWithError`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#RequestMatcherWithError)<br><br>[`caddyhttp.CELLibraryProducer`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp#CELLibraryProducer) | 요청 매처 (대신 WithError 사용 권장)<br><br>오류 숏서킷(short-circuit)이 있는 요청 매처<br><br>CEL 표현식 지원 | <i>⚠️&nbsp;사용 안 함(Deprecated)</i><br><br><br><br><i>(선택적)</i>
http.precompressed | [`encode.Precompressed`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/encode#Precompressed) | 지원되는 사전 압축(precompress) 매핑
http.reverse_proxy.circuit_breakers | [`reverseproxy.CircuitBreaker`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#CircuitBreaker) | 리버스 프록시 서킷 브레이커
http.reverse_proxy.selection_policies | [`reverseproxy.Selector`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#Selector) | 로드 밸런싱 선택 정책
http.reverse_proxy.transport | [`http.RoundTripper`](https://pkg.go.dev/net/http#RoundTripper) | HTTP 리버스 프록시 전송(transports)
http.reverse_proxy.upstreams | [`reverseproxy.UpstreamSource`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy#UpstreamSource) | 동적 업스트림 소스 | <i>⚠️&nbsp;실험적(Experimental)</i>
tls.ca_pool.source | [`caddytls.CA`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#CA) | 신뢰할 수 있는 루트 인증서 소스
tls.certificates | [`caddytls.CertificateLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#CertificateLoader) | TLS 인증서 소스
tls.client_auth | [`caddytls.ClientCertificateVerifier`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ClientCertificateVerifier) | 클라이언트 인증서 확인
tls.ech.publishers | [`caddytls.ECHPublisher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ECHPublisher) | 암호화된 ClientHello(ECH) 구성 게시 | <i>⚠️&nbsp;실험적(Experimental)</i>
tls.get_certificate | [`certmagic.Manager`](https://pkg.go.dev/github.com/caddyserver/certmagic#Manager) | TLS 인증서 관리자 | <i>⚠️&nbsp;실험적(Experimental)</i>
tls.handshake_match | [`caddytls.ConnectionMatcher`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#ConnectionMatcher) | TLS 연결 매처
tls.issuance | [`certmagic.Issuer`](https://pkg.go.dev/github.com/caddyserver/certmagic#Issuer) | TLS 인증서 발급자
tls.leaf_cert_loader | [`caddytls.LeafCertificateLoader`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#LeafCertificateLoader) | 신뢰할 수 있는 말단(leaf) 인증서 로드
tls.permission | [`caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission) | 도메인에 대한 인증서 획득 여부 | <i>⚠️&nbsp;실험적(Experimental)</i>
tls.stek | [`caddytls.STEKProvider`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#STEKProvider) | TLS 세션 티켓 키 소스
tls.context | [`caddytls.HandshakeContext`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#HandshakeContext) | GetCertificate 컨텍스트 가로채기(Intercept) | <i>⚠️&nbsp;실험적(Experimental)</i>

"실험적(Experimental)"으로 표시된 네임스페이스는 변경될 수 있습니다. (인터페이스를 확정할 수 있도록 이들을 사용하여 개발해 주세요!)
