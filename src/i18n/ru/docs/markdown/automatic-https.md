---
title: "Автоматический HTTPS"
---

<a id="automatic-https"></a>
# Автоматический HTTPS

**Caddy был первым веб-сервером, который использовал HTTPS автоматически *и по умолчанию*.**

Automatic HTTPS получает TLS certificates для всех ваших сайтов и поддерживает их обновленными. Он также перенаправляет HTTP на HTTPS за вас! Caddy использует безопасные и современные значения по умолчанию: не требуется downtime, дополнительная конфигурация или отдельные инструменты.

<aside class="tip">
	Caddy первым внедрил технологию automatic HTTPS; мы делаем это с первого дня, когда это стало практически возможно в 2015 году. Логика HTTPS automation в Caddy — самая зрелая и надежная в мире.
</aside>

Вот 28-секундное видео, показывающее, как это работает:

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**Меню:**

- [Обзор](#overview)
- [Активация](#activation)
- [Эффекты](#effects)
- [Требования к hostname](#hostname-requirements)
- [Локальный HTTPS](#local-https)
- [Тестирование](#testing)
- [ACME challenges](#acme-challenges)
- [On-Demand TLS](#on-demand-tls)
- [Ошибки](#errors)
- [Storage](#storage)
- [Wildcard certificates](#wildcard-certificates)
- [Encrypted ClientHello (ECH)](#encrypted-clienthello-ech)



<a id="overview"></a>
## Обзор

**По умолчанию Caddy обслуживает все сайты по HTTPS.**

- Caddy обслуживает IP addresses и локальные/внутренние hostnames по HTTPS, используя self-signed certificates, которым локально автоматически доверяют (если разрешено).
	- Примеры: `localhost`, `127.0.0.1`
- Caddy обслуживает публичные DNS names по HTTPS, используя certificates от публичного ACME CA, например [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) или [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com).
	- Примеры: `example.com`, `sub.example.com`, `*.example.com`

Caddy автоматически поддерживает обновление всех managed certificates и перенаправляет HTTP (порт по умолчанию `80`) на HTTPS (порт по умолчанию `443`).

**Для локального HTTPS:**

- Caddy может запросить пароль, чтобы установить свой уникальный root certificate в ваше trust store. Это происходит только один раз для каждого root; удалить его можно в любой момент.
- Любой client, который обращается к сайту без доверия к root CA certificate Caddy, покажет security errors.

**Для публичных доменных имен:**

<aside class="tip">

Это обычные требования для любого базового production-сайта, не только для Caddy. Главное отличие — нужно правильно настроить DNS records **до** запуска Caddy, чтобы он мог provision certificates.

</aside>


- Если A/AAAA records вашего домена указывают на ваш сервер,
- порты `80` и `443` открыты извне,
- Caddy может bind к этим портам (*или* эти порты forwarded к Caddy),
- ваш [data directory](/docs/conventions#data-directory) доступен для записи и persistent,
- и ваше доменное имя появляется в релевантном месте config,

то сайты будут обслуживаться по HTTPS автоматически. Больше ничего делать не нужно. Оно просто работает!

Поскольку HTTPS использует общую публичную инфраструктуру, вам как администратору сервера следует понимать остальную информацию на этой странице, чтобы избегать лишних проблем, устранять их при возникновении и правильно настраивать advanced deployments.



<a id="activation"></a>
## Активация

Caddy неявно активирует automatic HTTPS, когда знает domain name (то есть hostname) или IP address, который он обслуживает. Есть разные способы сообщить Caddy ваш domain/IP, в зависимости от того, как вы запускаете или настраиваете Caddy:

- [Site address](/docs/caddyfile/concepts#addresses) в [Caddyfile](/docs/caddyfile)
- [Host matcher](/docs/json/apps/http/servers/routes/match/host/) на верхнем уровне в [JSON routes](/docs/modules/http#servers/routes)
- Флаги командной строки вроде [`--domain`](/docs/command-line#caddy-file-server) или [`--from`](/docs/command-line#caddy-reverse-proxy)
- Certificate loader [automate](/docs/json/apps/tls/certificates/automate/)

Любое из следующего предотвратит активацию automatic HTTPS полностью или частично:

- Явное отключение [через JSON](/docs/json/apps/http/servers/automatic_https/) или [через Caddyfile](/docs/caddyfile/options#auto-https)
- Отсутствие hostnames или IP addresses в config
- Прослушивание исключительно HTTP-порта
- Префикс [site address](/docs/caddyfile/concepts#addresses) `http://` в Caddyfile
- Ручная загрузка certificates (если не задан [`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/))

**Особые случаи:**

- Domains, заканчивающиеся на `.ts.net`, не будут managed by Caddy. Вместо этого Caddy автоматически попытается получить эти certificates во время handshake от локально запущенного экземпляра [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com). Для этого [HTTPS должен быть включен в вашей учетной записи Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/), а процесс Caddy должен либо работать от root, либо нужно настроить `tailscaled`, чтобы дать пользователю Caddy [разрешение получать certificates](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).


<a id="effects"></a>
## Эффекты

Когда automatic HTTPS активирован, происходит следующее:

- Certificates получаются и обновляются для [всех подходящих доменных имен](#hostname-requirements)
- HTTP перенаправляется на HTTPS (для этого используется [HTTP port](/docs/modules/http#http_port) `80`)

Automatic HTTPS никогда не переопределяет явную конфигурацию, а только дополняет ее.

Если у вас уже есть [server](/docs/json/apps/http/servers/), слушающий HTTP port, routes перенаправления HTTP->HTTPS будут вставлены после ваших routes с host matcher, но до user-defined catch-all route.

При необходимости можно [настроить или отключить automatic HTTPS](/docs/json/apps/http/servers/automatic_https/); например, можно пропустить некоторые доменные имена или отключить redirects (в Caddyfile это делается через [global options](/docs/caddyfile/options)).


<a id="hostname-requirements"></a>
## Требования к hostname

Все hostnames (domain names) подходят для fully-managed certificates, если они:

- не пустые
- состоят только из alphanumerics, hyphens, dots и wildcard (`*`)
- не начинаются и не заканчиваются точкой ([RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5))

Кроме того, hostnames подходят для publicly-trusted certificates, если они:

- не являются localhost (включая TLD `.localhost`, `.local`, `.internal` и `.home.arpa`)
- не являются IP address
- имеют только один wildcard `*` как самый левый label


<a id="local-https"></a>
## Локальный HTTPS

Caddy автоматически использует HTTPS для всех сайтов с указанным host (domain, IP или hostname), включая internal и local hosts. Некоторые hosts либо не публичны (например, `127.0.0.1`, `localhost`), либо обычно не подходят для publicly-trusted certificates (например, IP addresses — certificates для них получить можно, но только у некоторых CAs). Они все равно обслуживаются по HTTPS, если это не отключено.

Чтобы обслуживать непубличные сайты по HTTPS, Caddy генерирует собственный certificate authority (CA) и использует его для подписи certificates. Trust chain состоит из root и intermediate certificate. Leaf certificates подписываются intermediate. Они хранятся в [data directory Caddy](/docs/conventions#data-directory) по пути `pki/authorities/local`.

Локальный CA Caddy работает на [библиотеках Smallstep <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/).

Local HTTPS не использует ACME и не выполняет DNS validation. Он работает только на локальной машине и считается доверенным только там, где установлен root certificate этого CA.

<a id="ca-root"></a>
### CA Root

Private key root уникально генерируется с помощью cryptographically-secure pseudorandom source и сохраняется в storage с ограниченными permissions. Он загружается в memory только для signing tasks, после чего выходит из scope и может быть garbage-collected.

Хотя Caddy можно настроить на подпись напрямую root (для поддержки non-compliant clients), по умолчанию это отключено, и root key используется только для подписи intermediates.

При первом использовании root key Caddy попытается установить его в локальные trust store(s) системы. Если у него нет разрешения на это, он запросит пароль. Это поведение можно отключить через [`skip_install_trust` в caddyfile](/docs/caddyfile/options#skip-install-trust) или [`"install_trust": false` в json config](/docs/json/apps/pki/certificate_authorities/install_trust/). Если это не сработало из-за запуска от непривилегированного пользователя, можно выполнить [`caddy trust`](/docs/command-line#caddy-trust), чтобы повторить установку от privileged user.

<aside class="tip">
	Доверять root certificate Caddy на собственной машине безопасно, пока ваш компьютер не скомпрометирован и ваш уникальный root key не утек.
</aside>

После установки root CA Caddy вы увидите его в локальном trust store как "Caddy Local Authority" (если вы не настроили другое имя). При желании его можно удалить в любой момент (команда [`caddy untrust`](/docs/command-line#caddy-untrust) упрощает это).

Обратите внимание, что автоматическая установка certificate в локальные trust stores существует только для удобства и не гарантируется, особенно при использовании containers или запуске Caddy как непривилегированного system service. В конечном счете, если вы полагаетесь на internal PKI, ответственность за правильное добавление root CA Caddy в нужные trust stores лежит на системном администраторе (это вне scope веб-сервера).


<a id="ca-intermediates"></a>
### CA Intermediates

Intermediate certificate и key также будут сгенерированы и будут использоваться для подписи leaf (individual site) certificates.

В отличие от root certificate, intermediate certificates имеют гораздо более короткий срок жизни и автоматически обновляются по мере необходимости.


<a id="testing"></a>
## Тестирование

Чтобы тестировать или экспериментировать с конфигурацией Caddy, обязательно [измените ACME endpoint](/docs/modules/tls.issuance.acme#ca) на staging или development URL, иначе вы, скорее всего, попадете в rate limits, которые могут заблокировать доступ к HTTPS на срок до недели, в зависимости от конкретного limit.

Один из default CAs Caddy — [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/), у которого есть [staging endpoint <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/), не подверженный тем же [rate limits <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/):

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

<a id="acme-challenges"></a>
## ACME challenges

Получение publicly-trusted TLS certificate требует проверки от publicly-trusted стороннего authority. В наши дни этот validation process автоматизирован с помощью [ACME protocol <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555) и может выполняться одним из трех способов ("challenge types"), описанных ниже.

Первые два challenge types включены по умолчанию. Если включено несколько challenges, Caddy выбирает один случайно, чтобы избежать случайной зависимости от конкретного challenge. Со временем он узнает, какой challenge type наиболее успешен, и начнет предпочитать его первым, но при необходимости будет fall back к другим доступным challenge types.


<a id="http-challenge"></a>
### HTTP challenge

HTTP challenge выполняет authoritative DNS lookup A/AAAA record для candidate hostname, затем запрашивает временный cryptographic resource через порт `80` с помощью HTTP. Если CA видит ожидаемый resource, выдается certificate.

Этот challenge требует, чтобы порт `80` был доступен извне. Если Caddy не может listen на port 80, packets с порта `80` должны быть forwarded на [HTTP port](/docs/json/apps/http/http_port/) Caddy.

Этот challenge включен по умолчанию и не требует явной configuration.


<a id="tls-alpn-challenge"></a>
### TLS-ALPN challenge

TLS-ALPN challenge выполняет authoritative DNS lookup A/AAAA record для candidate hostname, затем запрашивает временный cryptographic resource через порт `443` с помощью TLS handshake, содержащего специальные значения ServerName и ALPN. Если CA видит ожидаемый resource, выдается certificate.

Этот challenge требует, чтобы порт `443` был доступен извне. Если Caddy не может listen на port 443, packets с порта `443` должны быть forwarded на [HTTPS port](/docs/json/apps/http/https_port/) Caddy.

Этот challenge включен по умолчанию и не требует явной configuration.


<a id="dns-challenge"></a>
### DNS challenge

DNS challenge выполняет authoritative DNS lookup `TXT` records для candidate hostname и ищет специальную `TXT` record с определенным value. Если CA видит ожидаемое value, выдается certificate.

Этот challenge не требует открытых портов, и сервер, запрашивающий certificate, не обязан быть доступен извне. Однако DNS challenge требует configuration. Caddy должен знать credentials для доступа к DNS provider вашего домена, чтобы задавать (и удалять) специальные `TXT` records. Если DNS challenge включен, другие challenges по умолчанию отключены.

Поскольку ACME CAs следуют DNS standards при lookup `TXT` records для challenge verification, можно использовать CNAME records, чтобы делегировать ответ на challenge другим DNS zones. Это можно использовать для делегирования subdomain `_acme-challenge` [другой zone](/docs/caddyfile/directives/tls#dns_challenge_override_domain). Это особенно полезно, если ваш DNS provider не предоставляет API или не поддерживается одним из DNS plugins для Caddy.

Поддержка DNS providers — усилие сообщества. [Узнайте в нашей wiki, как включить DNS challenge для вашего provider.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


<a id="on-demand-tls"></a>
## On-Demand TLS

Caddy pioneered новую технологию, которую мы называем **On-Demand TLS**: она динамически получает новый certificate во время первого TLS handshake, которому он нужен, а не при загрузке config. Ключевой момент: это **не** требует заранее hard-code доменные имена в вашей configuration.

Многие бизнесы полагаются на эту уникальную возможность, чтобы масштабировать свои TLS deployments с меньшими затратами и без operational headaches при обслуживании десятков тысяч сайтов.

On-demand TLS полезен, если:

- вы не знаете все доменные имена при запуске или reload сервера,
- доменные имена могут быть не настроены сразу должным образом (DNS records еще не заданы),
- вы не контролируете доменные имена (например, это customer domains).

Когда on-demand TLS включен, вам не нужно указывать доменные имена в config, чтобы получить для них certificates. Вместо этого, когда приходит TLS handshake для server name (SNI), для которого у Caddy еще нет certificate, handshake удерживается, пока Caddy получает certificate для завершения handshake. Задержка обычно всего несколько секунд, и медленным является только начальный handshake. Все будущие handshakes быстрые, потому что certificates cached и reused, а renewals выполняются в фоне. Будущие handshakes могут trigger maintenance для certificate, чтобы поддерживать его renewed, но эта maintenance выполняется в фоне, если certificate еще не expired.

<a id="using-on-demand-tls"></a>
### Using On-Demand TLS

**On-demand TLS должен быть одновременно включен и ограничен, чтобы предотвратить abuse.**

Включение on-demand TLS выполняется в [TLS automation policies](/docs/json/apps/tls/automation/policies/) при использовании JSON config или [в site blocks с директивой `tls`](/docs/caddyfile/directives/tls) при использовании Caddyfile.

Чтобы предотвратить abuse этой функции, нужно настроить restrictions. Это делается в [object `automation` JSON config](/docs/json/apps/tls/automation/on_demand/) или в global option [`on_demand_tls`](/docs/caddyfile/options#on-demand-tls) Caddyfile. Restrictions являются "global" и не настраиваются per-site или per-domain. Основное ограничение — endpoint "ask", которому Caddy отправит HTTP request, чтобы спросить, имеет ли он разрешение получить и manage certificate для домена в handshake. Это означает, что вам понадобится внутренний backend, который может, например, запросить таблицу accounts в вашей database и проверить, зарегистрировался ли customer с этим domain name.

Учитывайте, как быстро ваш CA способен выдавать certificates. Если это занимает больше нескольких секунд, это ухудшит user experience (только для первого client).

Из-за deferred nature и дополнительной configuration, необходимой для предотвращения abuse, мы рекомендуем включать on-demand TLS только когда ваш реальный use case описан выше.

[Дополнительную информацию об эффективном использовании on-demand TLS смотрите в нашей wiki статье.](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)

<a id="errors"></a>
## Ошибки

Caddy делает все возможное, чтобы продолжить работу при errors в certificate management.

По умолчанию certificate management выполняется в фоне. Это означает, что он не блокирует startup и не замедляет ваши sites. Однако это также означает, что server будет работать еще до того, как все certificates станут доступны. Работа в фоне позволяет Caddy повторять попытки с exponential backoff в течение длительного времени.

Вот что происходит при error получения или renewal certificate:

1. Caddy повторяет попытку один раз после короткой паузы на случай случайного сбоя
2. Caddy делает короткую паузу, затем переключается на следующий включенный challenge type
3. После попытки всех включенных challenge types [он пробует следующий настроенный issuer](#issuer-fallback)
	- Let's Encrypt
	- ZeroSSL
4. После попытки всех issuers он делает exponential backoff
	- Максимум 1 день между попытками
	- До 30 дней

Во время retries с Let's Encrypt Caddy переключается на их [staging environment <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/), чтобы избежать проблем с rate limit. Это не идеальная strategy, но в целом она помогает.

ACME challenges занимают как минимум несколько секунд, а internal rate limiting помогает снизить случайный abuse. Caddy использует internal rate limiting в дополнение к тому, что настраиваете вы или CA, так что можно дать Caddy platter с миллионом domain names, и он постепенно — но настолько быстро, насколько сможет — получит certificates для всех. Текущий internal rate limit Caddy — 10 attempts на ACME account за 10 seconds.

Чтобы избежать утечки resources, Caddy aborts in-flight tasks (включая ACME transactions) при изменении config. Хотя Caddy способен обрабатывать частые config reloads, учитывайте такие operational considerations и рассмотрите batching config changes, чтобы уменьшить reloads и дать Caddy шанс фактически завершить получение certificates в фоне.

<a id="issuer-fallback"></a>
### Issuer fallback

Caddy — первый (и пока единственный) server, поддерживающий fully-redundant automatic failover к другим CAs, если ему не удается успешно получить certificate.

По умолчанию Caddy включает два ACME-compatible CAs: [**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) и [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com). Если Caddy не может получить certificate от Let's Encrypt, он попробует ZeroSSL; если оба не сработают, он сделает backoff и повторит попытку позже. В config можно настроить, какие issuers Caddy использует для получения certificates, универсально или для конкретных names.


<a id="storage"></a>
## Storage

Caddy будет хранить public certificates, private keys и другие assets в своем [configured storage facility](/docs/json/storage/) (или в default one, если не настроено; подробности по ссылке).

**Главное, что нужно знать при использовании default config: папка `$HOME` должна быть writeable и persistent.** Чтобы помочь с troubleshooting, Caddy выводит свои environment variables при startup, если указан флаг `--environ`.

Любые экземпляры Caddy, настроенные на использование одного и того же storage, будут автоматически sharing этих resources и coordinating certificate management как cluster.

Перед попыткой любых ACME transactions Caddy проверит configured storage, чтобы убедиться, что он writeable и имеет достаточную capacity. Это помогает уменьшить unnecessary lock contention.


<a id="wildcard-certificates"></a>
## Wildcard certificates

Caddy может получать и manage wildcard certificates, когда он настроен обслуживать site с подходящим wildcard name. Site name подходит для wildcard, если только самый левый domain label является wildcard. Например, `*.example.com` подходит, а такие — нет: `sub.*.example.com`, `foo*.example.com`, `*bar.example.com` и `*.*.example.com`. (Это restriction WebPKI.)

При использовании Caddyfile Caddy воспринимает site names буквально относительно certificate subject names. Иными словами, site, определенный как `sub.example.com`, заставит Caddy manage certificate для `sub.example.com`, а site, определенный как `*.example.com`, заставит Caddy manage wildcard certificate для `*.example.com`. Это показано на странице [Common Caddyfile Patterns](/docs/caddyfile/patterns#wildcard-certificates). Если нужно другое поведение, [JSON config](/docs/json/) дает более точный контроль над certificate subjects и site names ("host matchers").

Начиная с Caddy 2.10, при автоматизации wildcard certificate Caddy будет использовать wildcard certificate для individual subdomains в configuration. Он не будет получать certificates для individual subdomains, если это явно не настроено (например, через `force_automate`).

Wildcard certificates представляют широкий уровень authority и должны использоваться только если у вас так много subdomains, что управление individual certificates для них перегрузило бы PKI или привело бы к CA-enforced rate limits, либо если privacy tradeoff стоит риска раскрытия такой большой части DNS zone при key compromise. Обратите внимание, что сами по себе wildcard certificates не скрывают specific subdomains: они все равно раскрываются в TLS ClientHello packets, если не включен Encrypted ClientHello (ECH). (См. ниже.)

**Примечание:** [Let's Encrypt требует <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) [DNS challenge](#dns-challenge) для получения wildcard certificates.


<a id="encrypted-clienthello-ech"></a>
## Encrypted ClientHello (ECH)

Обычно TLS handshakes включают отправку ClientHello, включая Server Name Indicator (SNI; домен, к которому подключаются), в plaintext. Это потому, что он содержит параметры, необходимые для шифрования соединения после handshake. Разумеется, это раскрывает domain name — самую чувствительную часть ClientHello — любому, кто может eavesdrop connections, даже если он не находится рядом физически. Это показывает, к какому service вы подключаетесь, когда destination IP может обслуживать много разных sites, и именно так некоторые governments censor the Internet.

С Encrypted ClientHello client может защитить domain name, обернув настоящий ClientHello во "внешний" ClientHello, который задает параметры для расшифровки "внутреннего" ClientHello. Однако для реальной privacy нужно, чтобы много moving parts идеально совпали.

Сначала client должен знать, какие параметры, или configuration, использовать для шифрования ClientHello. Эта информация включает public key и "outer" domain ("public name"), среди прочего. Эту configuration нужно надежно опубликовать или распространить.

Теоретически можно записать ее на бумаге и раздать всем, но большинство основных browsers поддерживают lookup HTTPS-type DNS records, содержащих ECH parameters, при подключении к site. Поэтому вам нужно: (1) сгенерировать ECH configuration (public/private key pair и другие параметры), а затем (2) создать HTTPS-type DNS record, содержащую base64-encoded ECH configuration.

Или... можно позволить Caddy сделать все это за вас. Caddy — первый и единственный web server, который может автоматически генерировать, публиковать и обслуживать ECH configurations.

После публикации HTTPS record clients должны выполнить DNS lookup для HTTPS record при подключении к вашему site. Обычно DNS lookups идут в plaintext, что компрометирует security итоговых ECH handshakes, поэтому browsers должны использовать secure DNS protocol вроде DNS-over-HTTPS (DoH) или DNS-over-TLS (DoT). В зависимости от browser это может потребовать ручного включения.

После безопасной загрузки ECH config client использует embedded public key для шифрования ClientHello и продолжает подключение к вашему site. Затем Caddy расшифровывает inner ClientHello и обслуживает ваш site, при этом domain name никогда не появляется в plaintext on the wire.

<a id="deployment-considerations"></a>
### Deployment considerations

ECH — nuanced technology. Хотя Caddy полностью автоматизирует ECH, для максимальной privacy benefits нужно учитывать множество вещей. Также следует понимать разные trade-offs. 

<a id="publication"></a>
#### Publication

Caddy создаст HTTPS record для domain только если для этого domain уже есть record. Это предотвращает поломку DNS lookups для subdomain, который может быть покрыт wildcard. Убедитесь, что у ваших sites есть как минимум A/AAAA record, указывающая на ваш server. Если для DNS records вы используете только wildcard, wildcard domain тоже должен появиться в config Caddy.

Caddy не будет публиковать HTTPS record для domain, у которого есть CNAME record.

<a id="ech-grease"></a>
#### ECH GREASE

Если открыть Wireshark и подключиться к любому site (даже тому, который не поддерживает ECH) в современной версии крупного browser вроде Firefox или Chrome (даже с отключенным ECH), можно заметить, что его handshake включает extension `encrypted_client_hello`:

![ECH GREASE](/resources/images/ech-grease.png)

Цель этого — сделать настоящие ECH handshakes неотличимыми от plaintext handshakes. Если бы ECH handshakes выглядели иначе, censors могли бы просто блокировать ECH handshakes с минимальным fallout/collateral damage. Но если они заблокируют любой handshake с правдоподобным ECH extension, они фактически отключат большую часть Internet. (Цель — повысить стоимость widespread censorship.)

Это в основном важно знать при troubleshooting connections.

<a id="key-rotation"></a>
#### Key rotation

Как и certificate keys, один и тот же key не следует использовать долго; это плохая практика и может быть прямо небезопасно. Поэтому ECH keys следует регулярно rotate. В отличие от certificates, ECH configs не имеют строгого expiration. Но servers все равно должны их rotate.

Key rotation сложна, потому что clients должны узнать об updated keys. Если server просто заменит old keys на new ones, все ECH handshakes будут fail, если clients не будут немедленно уведомлены о новых keys. Но просто опубликовать updated keys недостаточно. В реальности DNS records имеют TTLs, resolvers cache responses и т. д. Клиентам могут потребоваться минуты, часы или даже дни, чтобы запросить updated HTTPS records и начать использовать новый ECH config.

По этой причине servers должны некоторое время поддерживать old ECH configs. Иначе есть риск раскрыть server names в plaintext *at scale*. Caddy время от времени rotates keys и поддерживает rotated keys некоторое время, пока они в итоге не удаляются.

Однако этого может быть недостаточно. Некоторые clients по разным причинам все равно не получат updated keys, и каждый такой случай создает риск раскрытия server name. Поэтому нужен другой способ передать clients updated config *in band* вместе с connection. Для этого и нужен *outer name* (или *public name*).

<a id="public-name"></a>
#### Public name

"Outer" ClientHello — это обычный ClientHello с двумя тонкими отличиями, которые известны только origin server:

1. Extension SNI является fake
2. Extension ECH является real

Этот "outer" SNI extension содержит public name, защищающий ваши реальные domains. Это name может быть любым, но **ваш server должен быть authoritative для public name**, потому что Caddy *получит* certificate для него.

Если client пытается установить ECH connection, но server не может расшифровать inner ClientHello, он фактически может завершить handshake, используя *outer* ClientHello с certificate для outer name. Это secure connection строго используется *только* для отправки client текущего ECH config; то есть это временное TLS connection исключительно для завершения начального TLS connection. Application data не передается: только ECH key. После получения updated key client может установить TLS connection как задумано.

Таким образом, настоящий server name остается защищенным, а out-of-sync clients сохраняют возможность подключаться; оба элемента важны для security.

Outer name может быть одним из domains вашего site, subdomain или любым другим domain name, указывающим на ваш server. Мы рекомендуем выбрать ровно одно generic name. Например, Cloudflare обслуживает миллионы sites за `cloudflare-ech.com`. Это важно для увеличения размера вашего anonymity set.

Public names не должны быть пустыми; то есть public name должен быть настроен, чтобы все работало. Caddy сейчас это не enforce (но может позже), однако ECH specification требует, чтобы public name был длиной минимум 1 byte. Некоторые software принимают empty names, другие нет. Это может приводить к confusing behaviors: browsers используют ECH, но servers reject его как invalid; или browsers не используют ECH (потому что он invalid), хотя config корректно находится в DNS record. Ответственность за правильную ECH configuration и publication для обеспечения privacy лежит на владельце site.


<a id="anonymity-set"></a>
#### Anonymity set

Чтобы максимизировать privacy benefits ECH, стремитесь максимизировать размер вашего *anonymity set*. По сути, этот set состоит из client-facing servers с identical behavior для observers. Идея в том, что observer не может легко сузить/вывести возможные sites или services, к которым подключаются clients.

На практике мы рекомендуем иметь только одно public name для всех ваших sites. (На каждый ECH config приходится только 1 public name, поэтому это подразумевает только 1 active ECH config в любой момент времени.) Если вы запускаете Caddy в cluster, Caddy автоматически shares и coordinates ECH configs с другими instances, что решает это за вас.

В пределе это означает, что каждый site в Internet мог бы или должен был бы находиться за одним IP address и одним public name...


<a id="centralization"></a>
#### Centralization

... что приводит нас к следующей теме: centralization. Одна из критик ECH состоит в том, что он склонен мотивировать centralization. Он делает это как минимум двумя способами: (1) clients предпочитают DoH/DoT для DNS lookups, что отправляет все DNS lookups через небольшую группу providers, и (2) максимизируется размер anonymity set at scale.

Когда используется DoH или DoT, все DNS lookups проходят через DoH/DoT provider. Между client и provider DNS data encrypted, но между provider и DNS server — нет. Global DoH/DoT фактически направляет весь ценный plaintext DNS traffic в несколько больших каналов, удобных для observation... или failure.

Аналогично, если действительно максимизировать anonymity set at scale, все sites были бы защищены за одним public name, например `cloudflare-ech.com`. Это хорошо для privacy, но тогда весь Internet зависит от Cloudflare и этого одного domain name. Максимизация до такой степени не нужна и непрактична, но теоретические последствия остаются valid.

Мы рекомендуем каждой organization или individual выбрать одно name для всех своих sites и использовать его; в большинстве случаев это должно дать достаточную privacy. Однако для вашего конкретного case консультируйтесь с experts по вашим individual threat models.


<a id="subdomain-privacy"></a>
#### Subdomain privacy

С ECH теперь теоретически возможно скрывать subdomains от side channels, если все развернуто правильно.

Большинству sites это не нужно, поскольку в общем случае subdomains являются публичной информацией. Мы не советуем помещать sensitive information в domain names. Тем не менее...

Чтобы избежать утечки sensitive subdomains в Certificate Transparency (CT) logs, используйте вместо этого wildcard certificate. Иными словами, вместо `sub.example.com` в config укажите `*.example.com`. (См. [Wildcard certificates](#wildcard-certificates) для важной информации.)

Другой источник leaks — DNSSEC, который большинство authoritative DNS servers использует по умолчанию. Через практику под названием "zone walking" возможна enumeration subdomains путем просмотра NSEC records, которые используются для authenticated denial of existence. Для этого они указывают на следующий доступный subdomain в алфавитном порядке, формируя linked list всех records. Убедитесь, что ваш domain использует как минимум NSEC3 или, в идеале, wildcard CNAME record, чтобы снизить этот риск.

Затем включите ECH в Caddy. Wildcard certificate в сочетании с ECH и wildcard CNAME record должен правильно скрывать subdomains, если каждый client, который пытается к нему подключиться, использует ECH и имеет сильную implementation. (Вы все равно зависите от clients в сохранении privacy.)


<a id="enabling-ech"></a>
### Включение ECH

Поскольку работающий ECH требует публикации configs в DNS records, вам понадобится сборка Caddy с подключенным [caddy-dns module](https://github.com/caddy-dns) для вашего DNS provider.

Затем в Caddyfile укажите config вашего DNS provider в global options, а также ECH public name, которое хотите использовать:

```caddy
{
	dns <provider config...>
	ech example.com
}
```

Помните:

- DNS provider module должен быть подключен, и у вас должна быть правильная configuration для вашего provider/account.
- ECH public name должно указывать на ваш server. Caddy получит для него certificate. Оно не обязано быть одним из domains вашего site.

Если используется JSON, добавьте эти properties в app `tls`:

```json
"encrypted_client_hello": {
	"configs": [
		{
			"public_name": "example.com"
		}
	]
},
"dns": {
	"name": "<provider name>",
	// provider configuration
}
```

Эти configurations включат ECH и опубликуют ECH configs для всех ваших sites. JSON config дает больше flexibility, если нужно customize behavior или у вас advanced setup.

<a id="verifying-ech"></a>
### Проверка ECH

Инструментов вокруг ECH пока немного, поэтому на момент написания лучший и самый универсальный способ проверить работу — использовать Wireshark и искать ваше public name в поле ServerName.

Сначала запустите server и проверьте, что logs упоминают что-то вроде "published ECH configuration list" для ваших domains. (Если при publication возникают errors, убедитесь, что ваш DNS provider module поддерживает [libdns 1.0](https://github.com/libdns/libdns), и откройте issue в repository вашего provider, если столкнетесь с проблемами.) Caddy также должен получить certificate для public name.

Далее убедитесь, что в browser включен ECH; для этого может потребоваться включить DoH/DoT. Также полезно очистить DNS cache browser (или system), чтобы он забрал newly published HTTPS records. Мы также рекомендуем закрыть browser или как минимум открыть новую private tab, чтобы он не reused existing connections.

Затем откройте Wireshark и начните listen на подходящем network interface. Пока Wireshark собирает packets, загрузите ваш site в browser. Затем можно pause Wireshark. Найдите ваш TLS ClientHello: в поле ServerName вы должны увидеть *public name*, а не фактическое domain name, к которому подключались.

Помните: extension `encrypted_client_hello` может быть виден даже если ECH не используется. Ключевой индикатор — значение SNI. Если ECH работает правильно, в Wireshark вы никогда не должны видеть true site name в plaintext.

Если при deployment ECH возникают проблемы, сначала спросите на нашем [форуме](https://caddy.community). Если это bug, можно [создать issue](https://github.com/caddyserver/caddy/issues) на GitHub.


<a id="ech-in-storage"></a>
### ECH in storage

ECH configurations хранятся в [data directory](/docs/conventions#data-directory) в configured storage module (по умолчанию file system) в папке `ech/configs`.

Следующая папка — ECH config ID, который генерируется случайно и относительно неважен. Randomness рекомендована specification, чтобы помочь снизить fingerprinting/tracking.

Metadata sidecar file помогает Caddy отслеживать, когда в последний раз происходили publications. Это предотвращает hammering вашего DNS provider при каждом config reload. Если нужно reset это state, можно безопасно удалить metadata file. Однако это также может reset время, когда key будет rotated. Можно также зайти в file и очистить только информацию о publication.
