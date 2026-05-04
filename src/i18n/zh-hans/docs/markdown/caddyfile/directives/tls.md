---
title: "tls（Caddyfile 指令）"
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# tls

为该网站配置 TLS。

**Caddy 的默认 TLS 设置是安全的。除非有充分理由且清楚了解其影响，否则请勿更改这些设置。** 此指令最常见的用途是指定 ACME 账户的电子邮件地址、更改 ACME CA 端点，或提供您自己的证书。

兼容性说明：鉴于 TLS 作为安全协议的敏感性，在新发布的次要版本或补丁版本中，可能会对 TLS 的默认设置进行有意的调整。过时或已废弃的 TLS 版本、加密套件、功能等可能会随时被移除。如果您的部署环境对变更极为敏感，您应明确指定必须保持不变的值，并密切关注版本升级。在绝大多数情况下，我们建议使用默认设置。


<span id="syntax"/>
## 语法

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

- **internal** 表示使用 Caddy 的内部、本地受信任的证书颁发机构 (CA) 为该站点生成证书。若要进一步配置 [`internal`](#internal) 签发者，请使用 [`issuer`](#issuer) 子指令。

- **force_automate** 强制 Caddy 为该站点自动生成证书，即使存在其他受管理的证书。

- **&lt;email&gt;** 是用于管理该网站证书的 ACME 账户的电子邮件地址。您也可以选择使用[全局选项](/docs/caddyfile/options#email) [`email`](/docs/caddyfile/options#email)，以便一次性为所有网站配置此设置。

<aside class="tip">

请注意，Let's Encrypt 可能会向您发送证书即将过期的邮件，但这可能会造成误导，因为 Caddy 在续期时可能选择了其他证书颁发机构（例如 ZeroSSL）。 请检查日志和/或证书本身（例如在浏览器中查看），以确认实际使用的证书颁发机构及其有效期是否仍在有效期内；如果有效，您可以放心忽略来自 Let's Encrypt 的邮件。

</aside>

- **&lt;cert_file&gt;** 和 **&lt;key_file&gt;** 分别是证书和私钥 PEM 文件的路径。若仅指定其中一个，则视为无效。

- **协议** <span id="protocols"/> 指定了协议版本的最小值和最大值。除非您清楚自己在做什么，否则请勿更改这些设置。通常无需配置此项，因为 Caddy 始终会使用现代默认设置。
  
  默认最小值： `tls1.2`, 默认最大值： `tls1.3`

- **加密套件** <span id="ciphers"/> 指定按优先级从高到低排序的加密套件名称列表。除非您清楚自己在做什么，否则请勿修改这些设置。请注意，TLS 1.3 不支持自定义加密套件；且并非所有 TLS 1.2 加密套件默认都已启用。支持的名称如下（按 Go 标准库的优先级排序）：
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

- **curves** <span id="curves"/> 指定要支持的 EC 组列表。建议不要更改默认设置。支持的值包括：
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> 是 TLS 握手过程中 <a href="https://developer.mozilla.org/en-US/docs/Glossary/ALPN">ALPN 扩展 <img src="/old/resources/images/external-link.svg" class="external-link"></a> 中要发布的值列表。

- **load** <span id="load"/> 指定用于加载证书+密钥捆绑包（PEM 文件）的文件夹列表。

- **ca** <span id="ca"/> 用于更改 ACME CA 端点。此选项最常用于在测试时设置 <a href="https://letsencrypt.org/docs/staging-environment/">Let's Encrypt 的预发布端点 <img src="/old/resources/images/external-link.svg" class="external-link"></a>，或内部 ACME 服务器。（若要更改整个 Caddyfile 中的此值，请改用 `acme_ca` [global 选项](/docs/caddyfile/options)。）

- **ca_root** <span id="ca_root"/> 指定一个 PEM 文件，该文件包含 ACME CA 端点的受信任根证书（如果该证书未存储在系统受信任存储库中）。

- **key_type** <span id="key_type"/> 是生成 CSR 时使用的密钥类型。仅在有特定要求时才需设置此项。

- **dns** <span id="dns"/> 启用 [DNS 验证](/docs/automatic-https#dns-challenge)，使用指定的提供商插件，该插件必须从 <a href="https://github.com/caddy-dns">`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link"></a> 中的某个仓库安装。每个提供商插件可能在其名称后带有各自的语法；详情请参阅其文档。 对各 DNS 提供商的支持由社区共同维护。[请访问我们的维基了解如何为您的提供商启用 DNS 验证。](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> 是一个[时间值](/docs/conventions#durations)，用于设置在使用 DNS 验证时，等待 DNS TXT 记录生效的最长时长。将其设置为 `-1` 可禁用传播检查。默认值为 2 分钟。

- **propagation_delay** <span id="propagation_delay"/> 是一个[时间值](/docs/conventions#durations)，用于设置在使用 DNS 验证时，开始检查 DNS TXT 记录传播前需要等待多长时间。默认值 `0` （不等待）。

- **dns_ttl** <span id="dns_ttl"/> 是一个[时长值](/docs/conventions#durations)，用于设置 `TXT` 记录的 TTL。很少需要。

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> 用于覆盖 DNS 验证所使用的域名。此设置旨在将验证任务委派给另一个域名。

  如果您的主域名的 DNS 提供商未提供 <a href="https://github.com/caddy-dns">DNS 插件 <img src="/old/resources/images/external-link.svg" class="external-link"></a>，您可以使用此方法。您也可以为 `_acme-challenge` 添加一个 `CNAME` 记录，将其指向您确实拥有插件的辅助域名。此方案无需插件提供特殊支持。
  
  当 ACME 签发机构尝试解决您主域名的 DNS 验证时，它们会通过 `CNAME` 指向您的辅助域名，以查找 `TXT` 记录。

  **注意：** 此处请使用 CNAME 记录中的完整规范名称作为值—— `_acme-challenge` 子域名不会自动添加在前面。

- **解析器** <span id="resolvers"/> 可自定义执行 DNS 验证时使用的 DNS 解析器；这些解析器优先于系统解析器或任何默认解析器。若在此处设置，这些解析器将应用于所有已配置的证书签发机构。

  这通常是一组 IP 地址。例如，要使用 <a href="https://developers.google.com/speed/public-dns">Google 公共 DNS <img src="/old/resources/images/external-link.svg" class="external-link"></a>：

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> 用于为该网站配置 ACME 外部账户绑定（EAB），使用您的证书颁发机构（CA）提供的密钥 ID 和 MAC 密钥。

- **on_demand** <span id="on_demand"/> 会为站点块中 address(es) 字段指定的主机名启用[按需 TLS](/docs/automatic-https#on-demand-tls)。**安全警告：** 除非您同时配置了 [`on_demand_tls` 全局选项](/docs/caddyfile/options#on-demand-tls)以防范滥用，否则在生产环境中执行此操作是不安全的。

- **reuse_private_keys** <span id="reuse_private_keys"/> 启用在续签证书时重复使用私钥的功能。默认情况下，每份新证书都会生成一个新密钥，以缓解密钥固定问题并缩小密钥泄露的影响范围。密钥固定违反了行业最佳实践。除非有特殊原因，否则不建议使用此选项；该选项可能会在未来版本中被移除。

- **client_auth** <span id="client_auth"/> 用于启用并配置 TLS 客户端身份验证：
  - **mode** <span id="mode"/> 是用于验证客户端的模式。允许的值包括：

    | 模式 | 描述 |
    | --- | --- |
    | 请求 | 向客户端请求证书，但即使没有证书也允许连接；不进行验证 |
    | 要求 | 要求客户端出示证书，但不进行验证 |
    | verify_if_given | 向客户端请求证书；即使没有证书也允许连接，但若有证书则进行验证 |
    | require_and_verify | 要求客户端出示经过验证的有效证书 |

    默认： `require_and_verify` 如果 `trust_pool` 提供了模块；否则， `require`.
	
  - **trust_pool** <span id="trust_pool"/> 用于配置证书颁发机构（CA）的来源，这些机构提供的证书将用于验证客户端证书。
	
  该段中使用的证书颁发机构（CA）以及可信证书池的配置，取决于所配置的信任池模块来源。Caddy 中提供的标准模块[如下所示](#trust-pool-providers)。完整的模块列表（包括第三方模块）请参见 [`trust_pool` 的 JSON 文档](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool)。

    多个 `trusted_*` 指令可用于指定多个 CA 或终端证书。未被列为终端证书之一，或未由任何指定 CA 签名的客户端证书，将根据 **mode** 被拒绝。

  - **验证器** <span id="verifier"/> 支持使用自定义客户端证书验证模块。这些模块可执行自定义的客户端身份验证检查，例如确保证书未被吊销。

- **签发者** <span id="issuer"/> 用于配置自定义证书签发者，或指定获取证书的来源。

  本段中使用的发行者以及随后的选项取决于可用的[发行者模块](#issuers)。其他一些子指令，例如 `ca` 和 `dns` 实际上是配置 `acme` （且该子指令是后期添加的），因此同时指定此指令与其他某些指令会造成混淆，故被禁止。
  
  可以多次指定此子指令来配置多个冗余签发机构；如果其中一个无法签发证书，系统将尝试使用下一个。

- **get_certificate** <span id="get_certificate"/> 允许在握手阶段从[管理模块](#certificate-managers)获取证书。

- **insecure_secrets_log** <span id="insecure_secrets_log"/> 启用将 TLS 密钥记录到文件的功能。这也被称为 `SSLKEYLOGFILE`。采用 NSS 密钥日志格式，可由 Wireshark 或其他工具进行解析。⚠️ **安全警告：** 此功能存在安全隐患，因为它允许其他程序或工具解密 TLS 连接，从而彻底破坏安全性。不过，此功能对于调试和故障排除可能很有用。

- **renewal_window_ratio** <span id="renewal_window_ratio"/> 是一个介于 0 和 1 之间的比率，用于确定在 Caddy 尝试续期证书之前，证书必须剩余的有效期。例如，如果某证书的有效期为 90 天，且该比率为 `0.3333` （默认值），则当证书剩余有效期为 30 天或更少时，Caddy 将持续尝试续期该证书。也可通过[全局选项](/docs/caddyfile/options#renewal_window_ratio) [`renewal_window_ratio`](/docs/caddyfile/options#renewal_window_ratio) 进行全局设置。

  您通常无需更改此设置，但如果您的证书颁发机构（CA）的签发时间非常长，在证书有效期后期进行更新可能会很有帮助。

  请注意，这仅供参考，因为 ACME 颁发机构可能会实现 [ARI 扩展](https://datatracker.ietf.org/doc/rfc9773/)。ARI 规定了 ACME 客户端（此处为 Caddy）应尝试续期的时间窗口，而该时间窗口可能与该比率不一致。

- **force_automate** 与指定 inline 相同（参见上文）。

<span id="trust-pool-providers"/>
### 信任池提供商

以下是可在 `trust_pool` 子指令中使用的标准信任池提供商：

#### 内联

  `inline` 模块会直接解析 Caddyfile 中列出的受信任根证书，这些证书采用 base64 DER 编码格式。`trust_der` 指令可以重复多次。

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> 是一个采用 Base64 DER 编码的 CA 证书，用于验证客户端证书。

#### 文件

该 `file` 模块从磁盘上的 PEM 文件中读取受信任的根证书。该 `pem_file` 指令可以在同一行上接受多个文件路径，并且可以重复多次。

```caddy-d
... file [<pem_file>...] {
	pem_file <pem_file>...
}
```

- **pem_file** <span id="pem_file"/> 是用于验证客户端证书的 PEM 格式 CA 证书文件的路径。

#### pki_root

  `pki_root` 模块从 [PKI 应用](/docs/caddyfile/options#pki-options)中定义的证书颁发机构获取 *root* 证书和受信任证书。`authority` 指令可同时接受多个证书颁发机构，且可以重复多次。

```caddy-d
... pki_root [<ca_name>...] {
	authority <ca_name>...
}
```

- **证书颁发机构** <span id="authority"/> 是 PKI 应用中配置的证书颁发机构的名称。

#### pki_intermediate

  `pki_intermediate` 模块从 [PKI 应用程序](/docs/caddyfile/options#pki-options)中定义的证书颁发机构获取 *intermediate* 证书和受信任证书。`authority` 指令可同时接受多个证书颁发机构，且可以重复多次。

```caddy-d
... pki_intermediate [<ca_name>...] {
	authority <ca_name>...
}
```

- **证书颁发机构** <span id="authority"/> 是 PKI 应用中配置的证书颁发机构的名称。

#### 存储

  `storage` 模块从 Caddy [存储中](/docs/caddyfile/options#storage)提取受信任的证书根。`authority` 指令可同时接受多个证书颁发机构，且可以重复多次。

```caddy-d
... storage [<storage_keys>...] {
	storage <storage_module>
	keys    <storage_keys>...
}
```

- **存储** <span id="storage"/> 是一个可选的存储模块。如果未指定，将使用默认的存储模块。如果指定了，则只能指定一次。

- **keys** <span id="keys"/> 是证书的PEM文件所存储的存储密钥列表。该指令支持在同一行中指定多个值，并且可以多次出现。

#### http

该 `http` 模块从 HTTP 端点获取受信任的证书。该 `endpoints` 指令可同时接受多个端点，且可以多次重复使用。

```caddy-d
... http [<endpoints...>] {
	endpoints   <endpoints...>
	tls         <tls_config>
}
```

- **endpoints** <span id="endpoints"/> 是用于获取证书的 HTTP 端点列表。该指令支持在同一行中指定多个值，且可以多次出现。

- **tls** <span id="tls"/> 是在连接到 HTTP 端点时可选的 TLS 配置。该段的解析规则在[下一节](#tls-1)中定义。

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

- **ca** <span id="ca"/> 是一个可选指令，用于定义信任池的提供者。其配置行为与 [`trust_pool`](#trust_pool) 相同。如果指定，则只能指定一次。

- **insecure_skip_verify** <span id="insecure_skip_verify"/> 会关闭 TLS 握手验证，导致连接不安全，并容易受到中间人攻击。*请勿在生产环境中使用。* 验证是针对系统信任的证书颁发机构（CA）进行的，或者根据 [`ca`](#ca) 指令确定的证书颁发机构进行的。

- **handshake_timeout** <span id="handshake_timeout"/> 是等待 TLS 握手完成的最长[时长](/docs/conventions#durations)。默认值：无超时。

- **server_name** <span id="server_name"/> 用于设置在验证 TLS 握手过程中接收到的证书时所使用的服务器名称。默认情况下，此处将使用上游地址的主机部分。

- **重新协商** <span id="renegotiation"/> 用于设置 TLS 重新协商级别。TLS 重新协商是指在首次握手之后再次进行握手操作。该级别可以是以下之一：
  - `never` （默认）禁用重新协商。
  - `once` 允许远程服务器在每次连接中请求一次重新协商。
  - `freely` 允许远程服务器反复请求重新协商。

<span id="verifiers"/>
### 验证器

在验证客户端证书确实由受信任的证书颁发机构签发后，客户端证书验证模块才会被执行，前提是 `trust_pool` 已进行配置。目前，标准版 Caddy 中内置的验证器是 `leaf`.

#### 叶

该 `leaf` 验证器会检查客户端证书是否属于预定义的允许证书集。该证书集通过[加载器](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders)模块进行加载。

##### 加载器

标准 Caddy 发行版包含 4 个加载器，其中 3 个可在 Caddyfile 中获取。

###### 文件

该 `file` 加载器从指定的 PEM 文件中加载证书集。

```caddy-d
... file <pem_files...>
```

###### 文件夹

该 `folder` 加载器会递归遍历指定的目录，查找可加载为受信任客户端证书的 PEM 文件。

```caddy-d
... folder <folders...>
```

###### PEM

该 `pem` 加载器支持在 Caddyfile 中内联 PEM 格式的证书。

```caddy-d
... pem <pem_strings...>
```

<span id="issuers"/>
### 发行人

这些发行者默认包含 `tls` 指令：

#### acme

使用 ACME 协议获取证书。请注意， `acme` 是默认的证书颁发机构（使用 Let's Encrypt），因此通常无需显式配置。

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

- **dir** <span id="dir"/> 是 ACME 证书颁发机构 (CA) 目录的 URL。
  
  默认： `https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> 是一个可选的备用目录，用于在重试验证时使用；如果所有验证均失败，重试过程中将使用此端点；当证书颁发机构（CA）拥有一个预发布端点，而您希望避免其生产端点的速率限制时，此功能非常有用。

  默认： `https://acme-staging-v02.api.letsencrypt.org/directory`

- **电子邮件** <span id="email"/> 是 ACME 账户的联系电子邮件地址。

- **timeout** <span id="timeout"/> 是一个[时长值](/docs/conventions#durations)，用于设置 ACME 操作超时前的等待时间。

- **disable_http_challenge** <span id="disable_http_challenge"/> 将禁用 HTTP 验证。

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> 将禁用 TLS-ALPN 挑战。

- **alt_http_port** <span id="alt_http_port"/> 是用于提供 HTTP 验证码的备用端口；由于该操作必须在 80 端口上进行，因此您必须将数据包转发至此备用端口。

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> 是用于处理 TLS-ALPN 挑战的备用端口；该操作必须在 443 端口上进行，因此您必须将数据包转发至此备用端口。

- **eab** <span id="eab"/> 指定了一个外部账户绑定，某些 ACME 证书颁发机构（CA）可能需要此项。

- **trusted_roots** <span id="trusted_roots"/> 表示连接到 ACME CA 服务器时应信任的一个或多个根证书（以 PEM 文件名形式）。

- **dns** <span id="dns"/> 用于配置 DNS 验证。除非[全局选项](/docs/caddyfile/options#dns) [`dns`](/docs/caddyfile/options#dns) 指定了一个全局适用的 DNS 提供程序模块，否则必须在此处配置一个提供程序。

- **propagation_timeout** <span id="propagation_timeout"/> 是一个[时间值](/docs/conventions#durations)，用于设置在使用 DNS 验证时，等待 DNS TXT 记录生效的最长时限。将其设置为 `-1` 可禁用传播检查。默认值为 2 分钟。

- **propagation_delay** <span id="propagation_delay"/> 是一个[时间值](/docs/conventions#durations)，用于设置在使用 DNS 验证时，开始检查 DNS TXT 记录传播前需要等待多长时间。默认值为 0（不等待）。

- **dns_ttl** <span id="dns_ttl"/> 是一个[时长值](/docs/conventions#durations)，用于设置 `TXT` 记录的 TTL。很少需要。

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> 用于覆盖 DNS 验证所使用的域名。此操作旨在将验证任务委派给另一个域名。

  如果您的主域名的 DNS 服务商未提供 <a href="https://github.com/caddy-dns">DNS 插件 <img src="/old/resources/images/external-link.svg" class="external-link"></a>，您可以使用此方法。您也可以为 `_acme-challenge` 添加一个 `CNAME` 记录，并将其指向一个您确实拥有插件的辅助域名。此方案无需插件提供特殊支持。
  
  当 ACME 签发机构尝试解决您主域名的 DNS 验证时，它们会通过 `CNAME` 指向您的辅助域名，以查找 `TXT` 记录。

  **注意：** 此处的值应使用 CNAME 记录中的完整规范名称—— `_acme-challenge` 子域名不会自动添加在前面。

- **解析器** <span id="resolvers"/> 可自定义执行 DNS 验证时使用的 DNS 解析器；这些解析器优先于系统解析器或任何默认解析器。若在此处设置，这些解析器将应用于所有已配置的证书签发机构。

  这通常是一组 IP 地址。例如，要使用 <a href="https://developers.google.com/speed/public-dns">Google 公共 DNS <img src="/old/resources/images/external-link.svg" class="external-link"></a>：

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> 用于指定 Caddy 应优先使用的证书链；当您的 CA 提供多条证书链时，此选项非常有用。请使用以下选项之一：
	- **smallest** <span id="smallest"/> 将指示 Caddy 优先选择字节数最少的链。

	- **root_common_name** <span id="root_common_name"/> 是一个包含一个或多个通用名称的列表；Caddy 将选择根节点与所指定的通用名称中至少一个相匹配的第一个证书链。

	- **any_common_name** <span id="any_common_name"/> 是一组一个或多个通用名称；Caddy 将选择第一个其签发者与所指定的通用名称中至少一个相匹配的链。

- **profile** 是申请证书时要应用的 [ACME 配置文件](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/)名称。如果您指定了该配置文件，则所有已配置（无论是隐式还是显式）的 CA 都必须支持此配置文件。有关可用配置文件的信息，请参阅您的 CA 文档；部分 CA 可能不支持配置文件。实验性功能：ACME 配置文件规范仍处于草案阶段，因此此功能可能会发生变更或被移除。


#### zerossl

使用 [ZeroSSL 的专有证书签发 API](https://zerossl.com/documentation/api/) 获取证书。此操作需要 API 密钥，且根据您的套餐不同，可能还需要支付费用。请注意，此功能与 [ZeroSSL 的 ACME 端点](https://zerossl.com/documentation/acme/)不同。若要使用 ZeroSSL 的 ACME 端点，请使用 `acme` 上述已配置为 ZeroSSL ACME 目录端点的 issuer。

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

- **validity_days** <span id="validity_days"/> 用于定义证书的有效期。仅接受特定值；详情请参阅 [ZeroSSL 的文档](https://zerossl.com/documentation/api/create-certificate/)。
<!--   
  默认： `https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> 是用于完成 ZeroSSL HTTP 验证的端口，若非 80 端口。
- **dns** <span id="zerossl_dns"/> 启用 CNAME 验证方法，使用指定的 DNS 提供商及给定配置进行自动记录管理。必须从 <a href="https://github.com/caddy-dns">`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link"></a> 仓库安装 DNS 提供商插件。每个提供商插件可能有其自身的语法，具体取决于其名称；详情请参阅相关文档。对每个 DNS 提供商的支持维护是社区共同努力的结果。
- **propagation_delay** <span id="zerossl_propagation_delay"/> 指在检查 CNAME 记录传播前需要等待的时间。
- **propagation_timeout** <span id="zerossl_propagation_timeout"/> 指在放弃之前等待 CNAME 记录传播的时间长度。
- **解析器** <span id="zerossl_resolvers"/> 用于定义在检查 CNAME 记录传播时使用的自定义 DNS 解析器。
- **dns_ttl** <span id="zerossl_dns_ttl"/> 用于配置在验证过程中创建的 CNAME 记录的 TTL。



#### 内部

从内部证书颁发机构获取证书。

```caddy-d
... internal {
	ca       <name>
	lifetime <duration>
	sign_with_root
}
```

- **ca** <span id="ca"/> 是要使用的内部证书颁发机构（CA）的名称。默认值： `local`。请参阅 [PKI 应用程序的全局选项](/docs/caddyfile/options#pki-options)来配置 `local` CA，或创建备用CA。

  默认情况下，根 CA 证书的有效期为 `3600d`（10 年），而中间证书的有效期为 `7d`（7 天）。

  Caddy 将尝试将根 CA 证书安装到系统信任存储中，但如果 Caddy 以无特权用户身份运行，或在 Docker 容器中运行，此操作可能会失败。在这种情况下，需要手动安装根 CA 证书，方法是使用 [`caddy trust`](/docs/command-line#caddy-trust) 命令，或者[从容器中复制](/docs/running#usage)该证书。

- **有效期** <span id="lifetime"/> 是一个[时长值](/docs/conventions#durations)，用于设定内部签发的叶证书的有效期。默认值： `12h`。除非绝对必要，否则不建议更改此值。其有效期必须短于中间证书的有效期。

- **sign_with_root** <span id="sign_with_root"/> 强制将根证书设为签发者，而非中间证书。不建议使用此方法，仅当设备/客户端无法正确验证证书链时才应使用（这种情况非常罕见）。



<span id="certificate-managers"/>
### 证书管理器

证书管理器模块与签发器模块的区别在于：使用管理器模块意味着由外部工具或服务负责证书的续期，而使用签发器模块则意味着由 Caddy 自身管理证书。（签发器模块以证书签名请求（CSR）作为输入，而证书管理器模块则以 TLS ClientHello 作为输入。）

这些管理器模块默认包含 `tls` 指令：

#### tailscale

从本地运行的 <a href="https://tailscale.com">Tailscale <img src="/old/resources/images/external-link.svg" class="external-link"></a> 实例中获取证书。[您的 Tailscale 账户](https://tailscale.com/kb/1153/enabling-https/)（或开源 <a href="https://github.com/juanfont/headscale">Headscale 服务器 <img src="/old/resources/images/external-link.svg" class="external-link"></a>）中必须已启用 HTTPS；并且 Caddy 进程必须以 root 身份运行，或者您必须配置 `tailscaled`，以授予您的 Caddy 用户[获取证书的权限](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348)。

_**注意：通常无需此操作！** Caddy 会自动为所有 `*.ts.net` 域名，无需任何额外配置。_

```caddy-d
get_certificate tailscale  # often unnecessary!
```


#### http

通过发送 HTTP(S) 请求获取证书。响应必须包含 `200` 状态码，且正文必须包含一个 PEM 证书链，其中应包含完整的证书（含中间证书）以及私钥。

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> 是用于发起请求的完全限定 URL。出于性能考虑，强烈建议将其设置为本地端点。该 URL 将附加以下查询字符串参数： 

  - `server_name`: SNI 值
  - `signature_schemes`：以逗号分隔的签名算法十六进制标识符列表
  - `cipher_suites`: 加密套件十六进制ID的逗号分隔列表
  - `local_ip`: 客户端发送请求的 IP 地址



<span id="examples"/>
## 示例

使用自定义证书和密钥。该证书[的SAN](https://en.wikipedia.org/wiki/Subject_Alternative_Name)（主机名别名）应与网站地址一致：

```caddy
example.com {
	tls cert.pem key.pem
}
```

对当前站点块中的所有主机使用[本地受信任的](/docs/automatic-https#local-https)证书，而非通过 ACME / Let's Encrypt 获取的公共证书（在开发环境中很有用）：

```caddy
example.com {
	tls internal
}
```

使用本地受信任的证书，但通过 [On-Demand](/docs/automatic-https#on-demand-tls) 进行管理，而非在后台处理。这样，您可以将任意域名指向您的 Caddy 实例，并让其自动为您生成证书。如果您的 Caddy 实例对公众开放，则不应使用此功能，因为攻击者可能会利用此功能耗尽您服务器的资源：

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

对内部证书颁发机构（CA）使用自定义选项（不能使用 `tls internal` 快捷方式）：

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

请为您的 ACME 账户指定一个电子邮件地址（但如果所有站点共用一个电子邮件地址，我们建议使用 `email` [全局选项](/docs/caddyfile/options)）：

```caddy
example.com {
	tls your@email.com
}
```

在环境变量中使用账户凭据，为在 Cloudflare 上管理的域名启用 DNS 验证。这将解锁通配符证书支持，该功能需要进行 DNS 验证：

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

通过 HTTP 获取证书链，而不是由 Caddy 进行管理。请注意，[`get_certificate`](#certificate-managers) 意味着已启用 [`on_demand`](#on_demand)，即通过模块获取证书，而非触发 ACME 签发：

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

启用 TLS 客户端身份验证，并要求客户端出示有效的证书，该证书需通过 [`trust_pool`](#trust_pool) 验证是否符合所有提供的 CA 要求 `file` 提供程序进行验证：

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
