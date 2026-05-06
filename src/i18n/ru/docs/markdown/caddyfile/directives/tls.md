---
title: tls (директива Caddyfile)
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# tls

Настраивает TLS для сайта.

**Настройки TLS по умолчанию в Caddy безопасны. Меняйте эти настройки только при наличии веской причины и понимании последствий.** Чаще всего эта директива используется, чтобы указать email-адрес учетной записи ACME, изменить endpoint ACME CA или предоставить собственные сертификаты.

Примечание о совместимости: поскольку TLS является чувствительным протоколом безопасности, в новых minor или patch релизах могут намеренно изменяться значения TLS по умолчанию. Старые или сломанные версии TLS, cipher, возможности и т. п. могут быть удалены в любой момент. Если ваше развертывание крайне чувствительно к изменениям, явно укажите значения, которые должны оставаться постоянными, и внимательно следите за обновлениями. Почти во всех случаях мы рекомендуем использовать настройки по умолчанию.


<a id="syntax"></a>
## Синтаксис

```caddy-d
tls [internal|force_automate|<email>] | [<cert_file> <key_file>] {
	protocols <min> [<max>]
	ciphers   <cipher_suites...>
	curves    <groups...>
	alpn      <values...>
	load      <paths...>
	ca        <ca_dir_url>
	ca_root   <pem_file>
	key_type  ed25519|p256|p384|rsa2048|rsa4096
	dns       <provider_name> [<params...>]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	eab       <key_id> <mac_key>
	on_demand
	reuse_private_keys
	client_auth {
		mode                   [request|require|verify_if_given|require_and_verify]
		trust_pool             <module>
		verifier 			   <module>
	}
	issuer          <issuer_name>  [<params...>]
	get_certificate <manager_name> [<params...>]
	insecure_secrets_log <log_file>
	renewal_window_ratio <ratio>
	force_automate
}
```

- **internal** означает использование внутреннего локально доверенного CA Caddy для выпуска сертификатов для этого сайта. Чтобы дополнительно настроить issuer [`internal`](#internal), используйте поддирективу [`issuer`](#issuer).

- **force_automate** заставляет Caddy автоматизировать сертификаты для сайта, даже если применяются другие managed certificates.

- **&lt;email&gt;** — email-адрес, используемый для учетной записи ACME, управляющей сертификатами сайта. Возможно, вам удобнее использовать [глобальную опцию `email`](/docs/caddyfile/options#email), чтобы настроить это сразу для всех сайтов.

<aside class="tip">

Помните, что Let's Encrypt может присылать письма о приближении срока истечения сертификата, но это может вводить в заблуждение, потому что Caddy при renewal мог выбрать другого issuer, например ZeroSSL. Проверьте журналы и/или сам сертификат, например в браузере, чтобы увидеть, какой issuer использовался и что срок действия все еще актуален; если это так, письмо от Let's Encrypt можно безопасно игнорировать.

</aside>

- **&lt;cert_file&gt;** и **&lt;key_file&gt;** — пути к PEM-файлам сертификата и приватного ключа. Указывать только один из них недопустимо.

- **protocols** <span id="protocols"/> задает минимальную и максимальную версии протокола. НЕ меняйте это, если точно не знаете, что делаете. Настраивать это редко необходимо, потому что Caddy всегда использует современные значения по умолчанию.
  
  Минимум по умолчанию: `tls1.2`, максимум по умолчанию: `tls1.3`

- **ciphers** <span id="ciphers"/> задает список имен cipher suite в порядке убывания предпочтения. НЕ меняйте это, если точно не знаете, что делаете. Обратите внимание, что cipher suites для TLS 1.3 не настраиваются; и не все cipher TLS 1.2 включены по умолчанию. Поддерживаемые имена, в порядке предпочтения Go stdlib:
	- `TLS_AES_128_GCM_SHA256`
	- `TLS_CHACHA20_POLY1305_SHA256`
	- `TLS_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA`

- **curves** <span id="curves"/> задает список EC groups для поддержки. Рекомендуется не менять значения по умолчанию. Поддерживаемые значения:
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> — список значений для объявления в [расширении ALPN <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Glossary/ALPN) TLS handshake.

- **load** <span id="load"/> задает список папок, из которых загружать PEM-файлы, являющиеся bundles сертификат+ключ.

- **ca** <span id="ca"/> изменяет endpoint ACME CA. Чаще всего это используется для задания [staging endpoint Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) при тестировании или внутреннего ACME server. Чтобы изменить это значение для всего Caddyfile, используйте вместо этого [глобальную опцию](/docs/caddyfile/options) `acme_ca`.

- **ca_root** <span id="ca_root"/> задает PEM-файл с доверенным корневым сертификатом для endpoint ACME CA, если его нет в системном trust store.

- **key_type** <span id="key_type"/> — тип ключа, используемый при генерации CSR. Задавайте это только при наличии конкретного требования.

- **dns** <span id="dns"/> включает [DNS challenge](/docs/automatic-https#dns-challenge) с указанным provider plugin, который должен быть подключен из одного из репозиториев [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). У каждого provider plugin может быть собственный синтаксис после имени; подробности см. в его документации. Поддержка каждого DNS provider является усилием сообщества. [Узнайте в нашей wiki, как включить DNS challenge для вашего provider.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> — [значение длительности](/docs/conventions#durations), задающее максимальное время ожидания появления DNS TXT records при использовании DNS challenge. Установите `-1`, чтобы отключить проверки propagation. По умолчанию 2 минуты.

- **propagation_delay** <span id="propagation_delay"/> — [значение длительности](/docs/conventions#durations), задающее, как долго ждать перед началом проверок propagation DNS TXT records при использовании DNS challenge. По умолчанию `0` (без ожидания).

- **dns_ttl** <span id="dns_ttl"/> — [значение длительности](/docs/conventions#durations), задающее TTL записи `TXT`, используемой для DNS challenge. Требуется редко.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> переопределяет домен для DNS challenge. Это нужно, чтобы делегировать challenge другому домену.

  Это может понадобиться, если DNS provider вашего основного домена не имеет доступного [DNS plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Вместо этого можно добавить запись `CNAME` с поддоменом `_acme-challenge` в основной домен, указывающую на вторичный домен, для которого у вас *есть* plugin. Эта опция *не* требует специальной поддержки от plugin.
  
  Когда ACME issuers пытаются решить DNS challenge для вашего основного домена, они затем последуют по `CNAME` к вашему вторичному домену, чтобы найти запись `TXT`.

  **Примечание:** указывайте здесь полное каноническое имя из CNAME record; поддомен `_acme-challenge` не будет добавлен автоматически.

- **resolvers** <span id="resolvers"/> настраивает DNS resolvers, используемые при выполнении DNS challenge; они имеют приоритет над системными resolvers и любыми значениями по умолчанию. Если они заданы здесь, resolvers будут переданы всем настроенным certificate issuers.

  Обычно это список IP-адресов. Например, чтобы использовать [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns):

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> настраивает ACME external account binding (EAB) для этого сайта, используя key ID и MAC key, предоставленные вашим CA.

- **on_demand** <span id="on_demand"/> включает [On-Demand TLS](/docs/automatic-https#on-demand-tls) для имен хостов, указанных в адресах блока сайта. **Предупреждение безопасности:** использовать это в production небезопасно, если вы также не настроили [глобальную опцию `on_demand_tls`](/docs/caddyfile/options#on-demand-tls) для защиты от злоупотреблений.

- **reuse_private_keys** <span id="reuse_private_keys"/> включает повторное использование приватных ключей при renewal сертификатов. По умолчанию для каждого нового сертификата создается новый ключ, чтобы снизить риски pinning и уменьшить область компрометации ключа. Key pinning противоречит лучшим практикам отрасли. Эта опция не рекомендуется, если у вас нет конкретной причины использовать ее; в будущей версии она может быть удалена.

- **client_auth** <span id="client_auth"/> включает и настраивает TLS client authentication:
  - **mode** <span id="mode"/> — режим аутентификации клиента. Разрешенные значения:

    | Режим | Описание |
    | --- | --- |
    | request | Запросить у клиентов сертификат, но разрешить даже если его нет; не проверять его |
    | require | Требовать от клиентов предъявить сертификат, но не проверять его |
    | verify_if_given | Запросить у клиентов сертификат; разрешить даже если его нет, но проверить, если он есть |
    | require_and_verify | Требовать от клиентов предъявить действительный сертификат, который проходит проверку |

    По умолчанию: `require_and_verify`, если предоставлен модуль `trust_pool`; иначе `require`.
	
  - **trust_pool** <span id="trust_pool"/> настраивает источник certificate authorities (CA), предоставляющих сертификаты, по которым проверяются клиентские сертификаты.
	
	Используемый certificate authority, предоставляющий pool доверенных сертификатов, и конфигурация внутри сегмента зависят от настроенного источника модуля trust pool. Стандартные модули, доступные в Caddy, [перечислены ниже](#trust-pool-providers). Полный список модулей, включая сторонние, приведен в [JSON-документации `trust_pool`](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool).

    Можно использовать несколько директив `trusted_*`, чтобы указать несколько CA или leaf certificates. Клиентские сертификаты, которые не перечислены как один из leaf certificates и не подписаны ни одним из указанных CA, будут отклонены согласно **mode**.

  - **verifier** <span id="verifier"/> включает использование пользовательского модуля verifier клиентских сертификатов. Такие модули могут выполнять пользовательские проверки client authentication, например проверять, что сертификат не отозван.

- **issuer** <span id="issuer"/> настраивает пользовательский certificate issuer или источник, из которого получать сертификаты.

  Какой issuer используется и какие опции следуют в этом сегменте, зависит от доступных [модулей issuer](#issuers). Некоторые другие поддирективы, например `ca` и `dns`, фактически являются сокращениями для настройки issuer `acme`, а эта поддиректива была добавлена позже; поэтому одновременное указание этой директивы и некоторых других запутывает и запрещено.
  
  Эту поддирективу можно указывать несколько раз, чтобы настроить несколько резервных issuers; если один не сможет выпустить cert, будет испробован следующий.

- **get_certificate** <span id="get_certificate"/> включает получение сертификатов из [модуля manager](#certificate-managers) во время handshake.

- **insecure_secrets_log** <span id="insecure_secrets_log"/> включает запись TLS secrets в файл. Это также известно как `SSLKEYLOGFILE`. Используется формат NSS key log, который затем может быть разобран Wireshark или другими инструментами. ⚠️ **Предупреждение безопасности:** это небезопасно, так как позволяет другим программам или инструментам расшифровывать TLS-соединения и поэтому полностью компрометирует безопасность. Однако эта возможность может быть полезна для отладки и troubleshooting.

- **renewal_window_ratio** <span id="renewal_window_ratio"/> — коэффициент между 0 и 1, определяющий, какой срок действия сертификата должен оставаться перед тем, как Caddy попытается renew сертификат. Например, если срок действия сертификата 90 дней, а этот коэффициент равен `0.3333` (значение по умолчанию), Caddy будет постоянно пытаться renew сертификат, когда до истечения останется 30 дней или меньше. Это также можно задать глобально с помощью [глобальной опции `renewal_window_ratio`](/docs/caddyfile/options#renewal_window_ratio).

  Менять это нужно редко, но это может быть полезно, чтобы renew происходил позже в сроке действия сертификата, если у вашего CA очень долгое время выпуска.

  Помните, что это рекомендация, поскольку ACME issuers могут реализовать [расширение ARI](https://datatracker.ietf.org/doc/rfc9773/). ARI задает окно, в котором ACME client, в данном случае Caddy, должен попытаться renewal, и это окно может не совпадать с этим коэффициентом.

- **force_automate** — то же самое, что указать inline, см. выше.

<a id="trust-pool-providers"></a>
### Trust Pool Providers

Это стандартные trust pool providers, которые можно использовать в поддирективе `trust_pool`:

<a id="inline"></a>
#### inline

Модуль `inline` разбирает доверенные root certificates, перечисленные прямо в Caddyfile, в формате base64 DER. Директиву `trust_der` можно повторять несколько раз.

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> — CA certificate в формате base64 DER, по которому проверяются клиентские сертификаты.

<a id="file"></a>
#### file

Модуль `file` читает доверенные root certificates из PEM-файлов на диске. Директива `pem_file` может принимать несколько путей к файлам в одной строке и повторяться несколько раз.

```caddy-d
... file [<pem_file>...] {
	pem_file <pem_file>...
}
```

- **pem_file** <span id="pem_file"/> — путь к PEM-файлу CA certificate, по которому проверяются клиентские сертификаты.

<a id="pki-root"></a>
#### pki_root

Модуль `pki_root` получает *root* и доверяет сертификатам от certificate authority, определенного в [PKI app](/docs/caddyfile/options#pki-options). Директива `authority` может принимать несколько authorities одновременно и повторяться несколько раз.

```caddy-d
... pki_root [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> — имя certificate authority, настроенного в PKI app.

<a id="pki-intermediate"></a>
#### pki_intermediate

Модуль `pki_intermediate` получает *intermediate* и доверяет сертификатам от certificate authority, определенного в [PKI app](/docs/caddyfile/options#pki-options). Директива `authority` может принимать несколько authorities одновременно и повторяться несколько раз.

```caddy-d
... pki_intermediate [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> — имя certificate authority, настроенного в PKI app.

<a id="storage"></a>
#### storage

Модуль `storage` извлекает trusted certificates root из [storage](/docs/caddyfile/options#storage) Caddy. Директива `authority` может принимать несколько authorities одновременно и повторяться несколько раз.

```caddy-d
... storage [<storage_keys>...] {
	storage <storage_module>
	keys    <storage_keys>...
}
```

- **storage** <span id="storage"/> — необязательный модуль storage для использования. Если не указан, будет использован модуль storage по умолчанию. Если указан, может быть указан только один раз.

- **keys** <span id="keys"/> — список storage keys, по которым хранятся PEM-файлы сертификатов. Директива принимает несколько значений в одной строке и может указываться несколько раз.

<a id="http"></a>
#### http

Модуль `http` получает доверенные сертификаты из HTTP endpoints. Директива `endpoints` может принимать несколько endpoints одновременно и повторяться несколько раз.

```caddy-d
... http [<endpoints...>] {
	endpoints   <endpoints...>
	tls         <tls_config>
}
```

- **endpoints** <span id="endpoints"/> — список HTTP endpoints, из которых получать сертификаты. Директива принимает несколько значений в одной строке и может указываться несколько раз.

- **tls** <span id="tls"/> — необязательная конфигурация TLS для подключения к HTTP endpoint. Разбор сегмента определен в [следующем разделе](#tls-1).

<a id="tls-1"></a>
##### TLS

```caddy-d
... {
	ca                    <ca_module>
	insecure_skip_verify
	handshake_timeout     <duration>
	server_name           <name>
	renegotiation         <never|once|freely>
}
```

- **ca** <span id="ca"/> — необязательная директива для определения provider trust pool. Конфигурация следует тому же поведению, что и [`trust_pool`](#trust_pool). Если указана, может быть указана только один раз.

- **insecure_skip_verify** <span id="insecure_skip_verify"/> отключает проверку TLS handshake, делая соединение небезопасным и уязвимым к атакам man-in-the-middle. *Не используйте в production.* Проверка выполняется по certificate authorities, которым доверяет система, или как определено директивой [`ca`](#ca).

- **handshake_timeout** <span id="handshake_timeout"/> — максимальная [длительность](/docs/conventions#durations) ожидания завершения TLS handshake. По умолчанию: без timeout..

- **server_name** <span id="server_name"/> задает имя сервера, используемое при проверке сертификата, полученного в TLS handshake. По умолчанию используется часть host из upstream address.

- **renegotiation** <span id="renegotiation"/> задает уровень TLS renegotiation. TLS renegotiation — это выполнение последующих handshakes после первого. Уровень может быть одним из:
  - `never` (по умолчанию) отключает renegotiation.
  - `once` позволяет удаленному серверу запросить renegotiation один раз на соединение.
  - `freely` позволяет удаленному серверу многократно запрашивать renegotiation.

<a id="verifiers"></a>
### Verifiers

Модули verifier клиентских сертификатов выполняются после проверки, что сертификаты выданы доверенным certificate authority, если настроен `trust_pool`. Единственный verifier, сейчас поставляемый в стандартном Caddy, — `leaf`.

<a id="leaf"></a>
#### Leaf

Verifier `leaf` проверяет, входит ли клиентский сертификат в заданный набор разрешенных сертификатов. Набор сертификатов загружается с помощью модулей [loader](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders).

<a id="loaders"></a>
##### Loaders

Стандартный дистрибутив Caddy включает 4 loader; 3 из них доступны в Caddyfile.

<a id="file-1"></a>
###### File

Loader `file` загружает набор сертификатов из указанных PEM-файлов.

```caddy-d
... file <pem_files...>
```

<a id="folder"></a>
###### Folder

Loader `folder` рекурсивно обходит именованные директории в поисках PEM-файлов, которые нужно загрузить как принимаемые клиентские сертификаты.

```caddy-d
... folder <folders...>
```

<a id="pem"></a>
###### PEM

Loader `pem` принимает сертификаты, встроенные в Caddyfile в формате PEM.

```caddy-d
... pem <pem_strings...>
```

<a id="issuers"></a>
### Issuers

Эти issuers входят в стандартную поставку директивы `tls`:

<a id="acme"></a>
#### acme

Получает сертификаты с использованием протокола ACME. Обратите внимание, что `acme` — issuer по умолчанию, использующий Let's Encrypt, поэтому явно настраивать его обычно не нужно.

```caddy-d
... acme [<directory_url>] {
	dir      <directory_url>
	test_dir <test_directory_url>
	email    <email>
	timeout  <duration>
	disable_http_challenge
	disable_tlsalpn_challenge
	alt_http_port    <port>
	alt_tlsalpn_port <port>
	eab <key_id> <mac_key>
	trusted_roots <pem_files...>
	dns [<provider_name> [<options>]]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}
	profile <name>
}
```

- **dir** <span id="dir"/> — URL directory ACME CA.
  
  По умолчанию: `https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> — необязательный fallback directory, используемый при повторе challenges; если все challenges не удались, этот endpoint будет использоваться во время retry. Полезно, если у CA есть staging endpoint, где вы хотите избежать rate limits production endpoint.

  По умолчанию: `https://acme-staging-v02.api.letsencrypt.org/directory`

- **email** <span id="email"/> — контактный email-адрес учетной записи ACME.

- **timeout** <span id="timeout"/> — [значение длительности](/docs/conventions#durations), задающее, как долго ждать перед timeout операции ACME.

- **disable_http_challenge** <span id="disable_http_challenge"/> отключает HTTP challenge.

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> отключает TLS-ALPN challenge.

- **alt_http_port** <span id="alt_http_port"/> — альтернативный порт для обслуживания HTTP challenge; он должен происходить на порту 80, поэтому пакеты нужно перенаправить на этот альтернативный порт.

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> — альтернативный порт для обслуживания TLS-ALPN challenge; он должен происходить на порту 443, поэтому пакеты нужно перенаправить на этот альтернативный порт.

- **eab** <span id="eab"/> задает External Account Binding, который может требоваться некоторыми ACME CA.

- **trusted_roots** <span id="trusted_roots"/> — один или несколько root certificates в виде PEM filenames, которым нужно доверять при подключении к ACME CA server.

- **dns** <span id="dns"/> настраивает DNS challenge. Здесь должен быть настроен provider, если только [глобальная опция `dns`](/docs/caddyfile/options#dns) не задает глобально применимый DNS provider module.

- **propagation_timeout** <span id="propagation_timeout"/> — [значение длительности](/docs/conventions#durations), задающее максимальное время ожидания появления DNS TXT records при использовании DNS challenge. Установите `-1`, чтобы отключить проверки propagation. По умолчанию 2 минуты.

- **propagation_delay** <span id="propagation_delay"/> — [значение длительности](/docs/conventions#durations), задающее, как долго ждать перед началом проверок propagation DNS TXT records при использовании DNS challenge. По умолчанию 0 (без ожидания).

- **dns_ttl** <span id="dns_ttl"/> — [значение длительности](/docs/conventions#durations), задающее TTL записи `TXT`, используемой для DNS challenge. Требуется редко.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> переопределяет домен для DNS challenge. Это нужно, чтобы делегировать challenge другому домену.

  Это может понадобиться, если DNS provider вашего основного домена не имеет доступного [DNS plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Вместо этого можно добавить запись `CNAME` с поддоменом `_acme-challenge` в основной домен, указывающую на вторичный домен, для которого у вас *есть* plugin. Эта опция *не* требует специальной поддержки от plugin.
  
  Когда ACME issuers пытаются решить DNS challenge для вашего основного домена, они затем последуют по `CNAME` к вашему вторичному домену, чтобы найти запись `TXT`.

  **Примечание:** указывайте здесь полное каноническое имя из CNAME record; поддомен `_acme-challenge` не будет добавлен автоматически.

- **resolvers** <span id="resolvers"/> настраивает DNS resolvers, используемые при выполнении DNS challenge; они имеют приоритет над системными resolvers и любыми значениями по умолчанию. Если они заданы здесь, resolvers будут переданы всем настроенным certificate issuers.

  Обычно это список IP-адресов. Например, чтобы использовать [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns):

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> задает, какие certificate chains Caddy должен предпочитать; полезно, если ваш CA предоставляет несколько chains. Используйте одну из следующих опций:
	- **smallest** <span id="smallest"/> указывает Caddy предпочитать chains с наименьшим числом байтов.

	- **root_common_name** <span id="root_common_name"/> — список из одного или нескольких common names; Caddy выберет первую chain, у которой root совпадает хотя бы с одним из указанных common names.

	- **any_common_name** <span id="any_common_name"/> — список из одного или нескольких common names; Caddy выберет первую chain, у которой issuer совпадает хотя бы с одним из указанных common names.

- **profile** — имя [ACME profile](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/), применяемого при заказе сертификатов. Если вы укажете его, все настроенные, явно или иначе, CA должны поддерживать этот profile. Сведения о доступных profiles см. в документации вашего CA; некоторые CA могут не поддерживать profiles. ЭКСПЕРИМЕНТАЛЬНО: спецификация ACME profile все еще находится в состоянии draft, поэтому эта возможность/функция может измениться или быть удалена.


<a id="zerossl"></a>
#### zerossl

Получает сертификаты с использованием [проприетарного API выпуска сертификатов ZeroSSL](https://zerossl.com/documentation/api/). Требуется API key, и в зависимости от вашего плана может также требоваться оплата. Обратите внимание, что этот issuer отличается от [ACME endpoint ZeroSSL](https://zerossl.com/documentation/acme/). Чтобы использовать ACME endpoint ZeroSSL, используйте описанный выше issuer `acme`, настроенный с ACME directory endpoint ZeroSSL.

```caddy-d
... zerossl <api_key> {
	validity_days <days>
	alt_http_port <port>
	dns <provider_name> ...
	propagation_delay <duration>
	propagation_timeout <duration>
	resolvers <list...>
	dns_ttl <duration>
}
```

- **validity_days** <span id="validity_days"/> определяет срок действия сертификата. Принимаются только некоторые значения; подробности см. в [документации ZeroSSL](https://zerossl.com/documentation/api/create-certificate/).
<!--   
  Default: `https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> — порт для выполнения HTTP validation ZeroSSL, если это не порт 80.
- **dns** <span id="zerossl_dns"/> включает метод CNAME validation с использованием указанного DNS provider и его конфигурации для автоматического создания записей. DNS provider plugin должен быть установлен из репозиториев [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). У каждого provider plugin может быть собственный синтаксис после имени; подробности см. в его документации. Поддержка каждого DNS provider является усилием сообщества.
- **propagation_delay** <span id="zerossl_propagation_delay"/> — как долго ждать перед проверкой propagation CNAME record.
- **propagation_timeout** <span id="zerossl_propagation_timeout"/> — как долго ждать propagation CNAME record перед отказом.
- **resolvers** <span id="zerossl_resolvers"/> задает пользовательские DNS resolvers для проверки propagation CNAME record.
- **dns_ttl** <span id="zerossl_dns_ttl"/> настраивает TTL для CNAME records, создаваемых как часть validation process.



<a id="internal"></a>
#### internal

Получает сертификаты от внутреннего certificate authority.

```caddy-d
... internal {
	ca       <name>
	lifetime <duration>
	sign_with_root
}
```

- **ca** <span id="ca"/> — имя внутреннего CA для использования. По умолчанию: `local`. См. [глобальные опции PKI app](/docs/caddyfile/options#pki-options), чтобы настроить CA `local` или создать альтернативные CA.

  По умолчанию root CA certificate имеет срок действия `3600d` (10 лет), а intermediate — `7d` (7 дней).

  Caddy попытается установить root CA certificate в системный trust store, но это может не удаться, если Caddy запущен от непривилегированного пользователя или внутри Docker container. В таком случае root CA certificate нужно установить вручную: либо командой [`caddy trust`](/docs/command-line#caddy-trust), либо [скопировав его из container](/docs/running#usage).

- **lifetime** <span id="lifetime"/> — [значение длительности](/docs/conventions#durations), задающее период действия internally issued leaf certificates. По умолчанию: `12h`. Менять это НЕ рекомендуется, если только это абсолютно не необходимо. Оно должно быть короче срока действия intermediate.

- **sign_with_root** <span id="sign_with_root"/> заставляет root быть issuer вместо intermediate. Это НЕ рекомендуется и должно использоваться только когда устройства/клиенты неправильно проверяют certificate chains, что очень нетипично.



<a id="certificate-managers"></a>
### Certificate Managers

Модули certificate manager отличаются от модулей issuer тем, что использование manager modules подразумевает, что внешний инструмент или сервис поддерживает сертификат обновленным, тогда как issuer module подразумевает, что Caddy сам управляет сертификатом. Модули issuer принимают Certificate Signing Request (CSR) на вход, а certificate manager modules принимают TLS ClientHello.

Эти manager modules входят в стандартную поставку директивы `tls`:

<a id="tailscale"></a>
#### tailscale

Получить сертификаты от локально запущенного экземпляра [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com). [HTTPS должен быть включен в вашей учетной записи Tailscale](https://tailscale.com/kb/1153/enabling-https/) или на вашем open source [Headscale server <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/juanfont/headscale); а процесс Caddy должен либо работать от root, либо вы должны настроить `tailscaled`, чтобы дать пользователю Caddy [разрешение на получение сертификатов](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).

_**ПРИМЕЧАНИЕ: Обычно это не нужно!** Caddy автоматически использует Tailscale для всех доменов `*.ts.net` без дополнительной конфигурации._

```caddy-d
get_certificate tailscale  # often unnecessary!
```


<a id="http-1"></a>
#### http

Получать сертификаты, выполняя HTTP(S)-запрос. Ответ должен иметь status code `200`, а тело должно содержать PEM chain, включающую полный сертификат с intermediates, а также приватный ключ.

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> — fully-qualified URL, к которому выполняется запрос. Настоятельно рекомендуется, чтобы это был локальный endpoint по причинам производительности. URL будет дополнен следующими query string parameters: 

  - `server_name`: значение SNI
  - `signature_schemes`: список hex ID алгоритмов signature, разделенный запятыми
  - `cipher_suites`: список hex IDS cipher suites, разделенный запятыми
  - `local_ip`: IP-адрес, к которому клиент сделал запрос



<a id="examples"></a>
## Примеры

Использовать пользовательский сертификат и ключ. Сертификат должен иметь [SANs](https://en.wikipedia.org/wiki/Subject_Alternative_Name), совпадающие с адресом сайта:

```caddy
example.com {
	tls cert.pem key.pem
}
```

Использовать [локально доверенные](/docs/automatic-https#local-https) сертификаты для всех hosts в текущем блоке сайта вместо публичных сертификатов через ACME / Let's Encrypt; полезно в dev-окружениях:

```caddy
example.com {
	tls internal
}
```

Использовать локально доверенные сертификаты, но управляемые [On-Demand](/docs/automatic-https#on-demand-tls), а не в фоне. Это позволяет направить любой домен на ваш экземпляр Caddy, и он автоматически подготовит для него сертификат. Это НЕ СЛЕДУЕТ использовать, если ваш экземпляр Caddy публично доступен, поскольку атакующий может использовать это для исчерпания ресурсов сервера:

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

Использовать пользовательские опции для внутреннего CA (нельзя использовать сокращение `tls internal`):

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

Указать email-адрес для учетной записи ACME; но если один email используется для всех сайтов, вместо этого рекомендуем [глобальную опцию](/docs/caddyfile/options) `email`:

```caddy
example.com {
	tls your@email.com
}
```

Включить DNS challenge для домена, управляемого в Cloudflare, с учетными данными аккаунта в переменной окружения. Это разблокирует поддержку wildcard certificates, для которой требуется DNS validation:

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

Получить certificate chain через HTTP вместо того, чтобы Caddy управлял ей. Обратите внимание, что [`get_certificate`](#certificate-managers) подразумевает включенный [`on_demand`](#on_demand), получая сертификаты через модуль вместо запуска ACME issuance:

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

Включить TLS Client Authentication и требовать от клиентов предъявлять действительный сертификат, который проверяется по всем предоставленным CA через provider `file` [`trust_pool`](#trust_pool):

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
