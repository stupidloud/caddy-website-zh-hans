---
title: "自动HTTPS"
---

# 自动启用 HTTPS

**Caddy 是首个自动且默认使用 HTTPS 的 Web 服务器。**

自动 HTTPS 会为您的所有网站配置 TLS 证书并自动续期。它还会为您将 HTTP 重定向到 HTTPS！Caddy 采用安全且现代的默认设置——无需停机、额外配置或单独的工具。

<aside class="tip">
	Caddy 率先推出了自动 HTTPS 技术；自 2015 年该技术首次可行以来，我们便一直致力于此。Caddy 的 HTTPS 自动化逻辑是全球最成熟、最可靠的。
</aside>

这是一段28秒的视频，展示了它的运作原理：

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**菜单：**

- [概述](#overview)
- [激活](#activation)
- [效果](#effects)
- [主机名要求](#hostname-requirements)
- [本地 HTTPS](#local-https)
- [测试](#testing)
- [ACME 挑战](#acme-challenges)
- [按需 TLS](#on-demand-tls)
- [错误](#errors)
- [存储](#storage)
- [通配符证书](#wildcard-certificates)
- [加密的 ClientHello (ECH)](#encrypted-clienthello-ech)



<a id="overview"></a>
## 概述

**默认情况下，Caddy 通过 HTTPS 提供所有网站的访问服务。**

- Caddy 通过 HTTPS 提供 IP 地址和本地/内部主机名，使用的是在本地自动被信任（如果允许的话）的自签名证书。
	- 示例： `localhost`, `127.0.0.1`
- Caddy 通过 HTTPS 提供公共 DNS 域名服务，并使用来自公共 ACME 证书颁发机构（如 <a href="https://letsencrypt.org">Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link"></a> 或 <a href="https://zerossl.com">ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link"></a>）签发的证书。
	- 示例： `example.com`, `sub.example.com`, `*.example.com`

Caddy 会自动续期所有受管理的证书，并将 HTTP（默认端口 `80`）自动重定向至 HTTPS（默认端口 `443`）。

**关于本地 HTTPS：**

- Caddy 可能会提示您输入密码，以便将其唯一的根证书安装到您的受信任存储中。此操作针对每个根证书仅需执行一次；您随时可以将其移除。
- 任何未信任 Caddy 根 CA 证书的客户端访问该网站时，都会显示安全错误。

**关于公共域名：**

<aside class="tip">

这些是任何基础生产环境的网站都必须满足的常见要求，而不仅仅是 Caddy。主要区别在于，必须在运行 Caddy **之前**正确设置 DNS 记录，以便它能够配置证书。

</aside>


- 如果您的域名的 A/AAAA 记录指向您的服务器，
- 端口 `80` 且 `443` 对外开放，
- Caddy 可以绑定到这些端口（或这些端口被转发到 Caddy），
- 您的[数据目录](/docs/conventions#data-directory)具有可写性和持久性，
- 且您的域名出现在配置中的相应位置，

届时网站将自动通过 HTTPS 提供服务。您无需进行任何额外操作。一切都会自动运行！

由于 HTTPS 采用的是共享的公共基础设施，作为服务器管理员，您应了解本页面上的其余信息，以便避免不必要的麻烦，在问题发生时进行排查，并正确配置高级部署。



<a id="activation"></a>
## 激活

当 Caddy 识别到其所服务的域名（即主机名）或 IP 地址时，会自动启用 HTTPS。根据您运行或配置 Caddy 的方式不同，有多种方法可以向 Caddy 指定您的域名/IP：

- [Caddyfile](/docs/caddyfile) 中的[站点地址](/docs/caddyfile/concepts#addresses)
- [JSON 路由](/docs/modules/http#servers/routes)顶层中的[主机匹配器](/docs/json/apps/http/servers/routes/match/host/)
- 命令行参数，例如 [`--domain`](/docs/command-line#caddy-file-server) 或 [`--from`](/docs/command-line#caddy-reverse-proxy)
- [自动](/docs/json/apps/tls/certificates/automate/)证书加载器

以下任何一种情况都会导致自动启用 HTTPS 功能无法生效，无论是全部还是部分：

- [通过 JSON](/docs/json/apps/http/servers/automatic_https/) 或 [Caddyfile](/docs/caddyfile/options#auto-https) 显式禁用该功能
- 配置中未提供任何主机名或 IP 地址
- 仅监听 HTTP 端口
- 在[网站](/docs/caddyfile/concepts#addresses)地址前添加 `http://` 在 Caddyfile 中
- 手动加载证书（除非已设置[`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/)）

**特殊情况：**

- 以 `.ts.net` 结尾的域名将不会由 Caddy 管理。相反，Caddy 会在握手阶段自动尝试从本地运行的 <a href="https://tailscale.com">Tailscale <img src="/old/resources/images/external-link.svg" class="external-link"></a> 实例获取这些证书。这要求 <a href="https://tailscale.com/kb/1153/enabling-https/">您的 Tailscale 账户 <img src="/old/resources/images/external-link.svg" class="external-link"> 已启用 HTTPS</a>，且 Caddy 进程必须以 root 身份运行，或者您必须配置 `tailscaled`，以授予您的 Caddy 用户[获取证书的权限](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348)。


<a id="effects"></a>
## 效果

启用自动 HTTPS 后，将发生以下情况：

- 已为[所有符合条件的域名](#hostname-requirements)申请并续期证书
- HTTP 被重定向到 HTTPS（这使用 [HTTP 端口](/docs/modules/http#http_port) `80`)

自动 HTTPS 功能绝不会覆盖显式配置，它仅是对显式配置的补充。

如果已有[服务器](/docs/json/apps/http/servers/)正在监听 HTTP 端口，则 HTTP 到 HTTPS 的重定向路由将插入到包含主机匹配器的路由之后，但位于用户自定义的通配路由之前。

如有必要，您可以[自定义或禁用自动 HTTPS](/docs/json/apps/http/servers/automatic_https/)；例如，您可以跳过某些域名或禁用重定向（对于 Caddyfile，请通过[全局选项](/docs/caddyfile/options)进行设置）。


<a id="hostname-requirements"></a>
## 主机名要求

只要满足以下条件，所有主机名（域名）均可申请全托管证书：

- 不是空集
- 仅包含字母、数字、连字符、句点和通配符 (`*`)
- 名称不得以点开头或结尾（[RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5)）

此外，如果主机名满足以下条件，则有资格获得受公众信任的证书：

- 不是 localhost（包括 `.localhost`, `.local`, `.internal` 且 `.home.arpa` 顶级域名)
- 不是 IP 地址
- 仅包含一个通配符 `*` 作为最左侧的标签


<a id="local-https"></a>
## 本地 HTTPS

对于所有指定了主机（域名、IP 地址或主机名）的网站，包括内部和本地主机，Caddy 都会自动使用 HTTPS。某些主机要么不对外公开（例如 `127.0.0.1`, `localhost`) 或通常不符合公开受信任证书的资格（例如 IP 地址——虽然可以为其获取证书，但仅限于某些 CA 签发）。除非被禁用，否则这些站点仍将通过 HTTPS 提供服务。

为了通过 HTTPS 提供非公开站点的服务，Caddy 会生成自己的证书颁发机构 (CA)，并使用它来签署证书。信任链由根证书和中间证书组成。叶证书由中间证书签署。它们存储在 [Caddy 的数据目录](/docs/conventions#data-directory)中，路径为 `pki/authorities/local`.

Caddy 的本地证书授权机构（CA）由 [Smallstep 库](https://smallstep.com/certificates/)提供支持 <a href="https://smallstep.com/certificates/"><img src="/old/resources/images/external-link.svg" class="external-link"></a>。

本地 HTTPS 不使用 ACME，也不进行任何 DNS 验证。它仅在本地机器上运行，且仅在安装了该 CA 的根证书时才被视为可信。

<a id="ca-root"></a>
### CA 根证书

根证书的私钥是通过加密安全的伪随机源唯一生成的，并存储在权限受限的存储区域中。该私钥仅在执行签名任务时加载到内存中，任务完成后即退出作用域，随后被垃圾回收机制回收。

虽然可以配置 Caddy 直接使用根证书进行签名（以支持不符合规范的客户端），但此功能默认处于禁用状态，根证书仅用于对中间证书进行签名。

首次使用根密钥时，Caddy 会尝试将其安装到系统的本地信任存储中。如果它没有相应的权限，则会提示输入密码。可以通过[在 caddyfile](/docs/caddyfile/options#skip-install-trust) 中设置 [`skip_install_trust`](/docs/caddyfile/options#skip-install-trust) 或[在 JSON 配置中](/docs/json/apps/pki/certificate_authorities/install_trust/)设置 [`"install_trust": false`](/docs/json/apps/pki/certificate_authorities/install_trust/) 来禁用此行为。如果因以无特权用户身份运行而导致安装失败，您可以运行 [`caddy trust`](/docs/command-line#caddy-trust) 以特权用户身份重试安装。

<aside class="tip">
	只要您的计算机未被入侵，且您的唯一根密钥未被泄露，在您自己的设备上信任 Caddy 的根证书是安全的。
</aside>

安装 Caddy 的根证书颁发机构 (CA) 后，您将在本地信任存储中看到它，名称为“Caddy Local Authority”（除非您配置了其他名称）。如果您愿意，可以随时将其卸载（使用 [`caddy untrust`](/docs/command-line#caddy-untrust) 命令即可轻松完成）。

请注意，将证书自动安装到本地信任存储库中仅是为了方便，并不保证一定能成功，尤其是在使用容器或将 Caddy 作为无特权系统服务运行时。最终，如果您依赖内部 PKI，则应由系统管理员负责确保将 Caddy 的根 CA 正确添加到必要的信任存储库中（这超出了 Web 服务器的范围）。


<a id="ca-intermediates"></a>
### CA 中间证书

系统还将生成一个中间证书和密钥，用于对叶证书（单个站点证书）进行签名。

与根证书不同，中间证书的有效期要短得多，并且会根据需要自动续期。


<a id="testing"></a>
## 测试

若要测试或调试您的 Caddy 配置，请务必将[ ACME 端点更改](/docs/modules/tls.issuance.acme#ca)为预发布或开发 URL，否则您可能会触发速率限制，这可能会导致您无法访问 HTTPS，持续时间最长可达一周，具体取决于您触发的速率限制类型。

Caddy 的默认证书颁发机构之一是 <a href="https://letsencrypt.org/">Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link"></a>，它有一个<a href="https://letsencrypt.org/docs/staging-environment/">测试端点 <img src="/old/resources/images/external-link.svg" class="external-link"></a>，该端点不受相同的<a href="https://letsencrypt.org/docs/rate-limits/">速率限制 <img src="/old/resources/images/external-link.svg" class="external-link"></a>：

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

<a id="acme-challenges"></a>
## ACME 挑战

要获取受公众信任的 TLS 证书，需要经过受公众信任的第三方证书颁发机构（CA）的验证。如今，该验证过程已通过 <a href="https://tools.ietf.org/html/rfc8555">ACME 协议 <img src="/old/resources/images/external-link.svg" class="external-link"></a> 实现自动化，并可通过以下三种方式（“验证类型”）之一进行。

前两种验证类型默认处于启用状态。如果启用了多种验证类型，Caddy 会随机选择其中一种，以避免意外依赖特定的验证类型。随着时间的推移，它会学习哪种验证类型最有效，并开始优先使用该类型，但在必要时仍会回退到其他可用的验证类型。


<a id="http-challenge"></a>
### HTTP 挑战

HTTP 验证会针对候选主机名的 A/AAAA 记录执行权威 DNS 查询，然后通过端口 `80` 使用 HTTP 请求临时获取资源。如果 CA 检测到预期的资源，则签发证书。

此挑战要求端口 `80` 对外部开放。如果 Caddy 无法监听 80 端口，则来自该端口的数据包必须转发至 Caddy 的 [HTTP 端口](/docs/json/apps/http/http_port/)。

此功能默认已启用，无需进行显式配置。


<a id="tls-alpn-challenge"></a>
### TLS-ALPN 挑战

TLS-ALPN 挑战会针对候选主机名的 A/AAAA 记录执行权威 DNS 查询，然后通过端口 `443` 发送包含特殊 ServerName 和 ALPN 值的 TLS 握手请求临时资源。若证书颁发机构（CA）检测到预期资源，则签发证书。

此挑战要求端口 `443` 对外开放。如果 Caddy 无法监听 443 端口，则来自该端口的数据包必须转发至 Caddy 的 [HTTPS 端口](/docs/json/apps/http/https_port/)。

此功能默认已启用，无需进行显式配置。


<a id="dns-challenge"></a>
### DNS 挑战

DNS 验证会针对候选主机名的 `TXT` 记录查找一个具有特定值的特殊 `TXT` 记录。如果证书颁发机构（CA）检测到预期值，则签发证书。

此验证机制无需开放任何端口，且请求证书的服务器也不必对外部开放。不过，DNS 验证需要进行配置。Caddy 需要知道访问您域名 DNS 提供商的凭据，以便设置（和清除）特殊的 `TXT` 记录。如果启用了 DNS 验证，其他验证方式将默认被禁用。

由于 ACME 证书颁发机构在查询 `TXT` 记录时遵循 DNS 标准，因此您可以使用 CNAME 记录将响应挑战的任务委托给其他 DNS 区域。这可用于将 `_acme-challenge` 子域名委派给其他 DNS 区域。如果您的 DNS 提供商未提供 API，或者 Caddy 的 DNS 插件不支持该提供商，此方法将特别有用。

DNS 服务商的支持工作是社区共同努力的结果。[请访问我们的维基页面，了解如何为您的服务商启用 DNS 验证。](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


<a id="on-demand-tls"></a>
## 按需 TLS

Caddy 开创了一项名为 **按需 TLS** 的新技术，该技术会在首次需要证书的 TLS 握手过程中动态获取新证书，而非在加载配置时获取。关键在于，这 **无需** 提前在配置中硬编码域名。

许多企业正是借助这一独特功能，在为数万个网站提供服务时，能够以更低的成本扩展 TLS 部署，且无需担心运营上的麻烦。

在以下情况下，按需 TLS 非常有用：

- 在启动或重启服务器时，您并不了解所有域名，
- 域名可能无法立即正确配置（DNS 记录尚未设置），
- 您无法控制这些域名（例如，它们是客户的域名）。

启用按需 TLS 后，您无需在配置中指定域名即可为其获取证书。相反，当收到针对某个服务器名称（SNI）的 TLS 握手请求，而 Caddy 尚未为此拥有证书时，该握手请求会被暂缓，同时 Caddy 会获取证书以完成握手。 此延迟通常仅需几秒钟，且仅首次握手会变慢。后续所有握手都将很快，因为证书会被缓存并重复使用，且证书续期会在后台进行。后续握手可能会触发证书维护以保持其有效，但如果证书尚未过期，此维护操作将在后台进行。

<a id="using-on-demand-tls"></a>
### 使用按需 TLS

**必须同时启用并限制按需 TLS，以防止滥用。**

如果使用 JSON 配置，则在 [TLS 自动化策略](/docs/json/apps/tls/automation/policies/)中启用按需 TLS；如果使用 Caddyfile，则[在站点块中通过 `tls` 指令](/docs/caddyfile/directives/tls)启用。

为防止此功能被滥用，您必须配置限制。这可以通过 [JSON 配置中的](/docs/json/apps/tls/automation/on_demand/) [`automation`](/docs/json/apps/tls/automation/on_demand/) [对象](/docs/json/apps/tls/automation/on_demand/)，或 Caddyfile 中的 [`on_demand_tls`](/docs/caddyfile/options#on-demand-tls) 全局选项来实现。这些限制是“全局”的，无法针对每个站点或每个域名单独配置。 主要限制机制是一个“查询”端点，Caddy 会向该端点发送 HTTP 请求，以确认其是否有权限为握手过程中的该域名获取并管理证书。这意味着您需要一个内部后端，例如，该后端可以查询数据库中的账户表，以确认客户是否已使用该域名注册。

请注意您的证书颁发机构（CA）签发证书的速度。如果耗时超过几秒钟，将会对用户体验造成负面影响（仅限首个客户端）。

鉴于其延迟的特性以及为防止滥用所需的额外配置，我们建议仅在您的实际使用场景符合上述描述时，才启用按需 TLS。

[有关如何有效使用按需 TLS 的更多信息，请参阅我们的维基文章。](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)

<a id="errors"></a>
## 错误

如果证书管理出现错误，Caddy 会尽力继续运行。

默认情况下，证书管理在后台进行。这意味着它不会阻碍启动过程，也不会拖慢您的网站速度。不过，这也意味着在所有证书都准备就绪之前，服务器就已经开始运行了。后台运行使 Caddy 能够在较长一段时间内采用指数退避策略进行重试。

如果在获取或续期证书时发生错误，将会出现以下情况：

1. Caddy 会在短暂暂停后重试一次，以防是偶然情况
2. Caddy 短暂停顿片刻，然后切换到下一个已启用的挑战类型
3. 在尝试了所有已启用的验证类型后，[系统将尝试下一个已配置的证书颁发机构](#issuer-fallback)
	- Let's Encrypt
	- ZeroSSL
4. 在所有发行方均经过审理后，其规模呈指数级缩减
	- 每次尝试之间间隔最多1天
	- 最长30天

在使用 Let's Encrypt 进行重试时，Caddy 会切换到其<a href="https://letsencrypt.org/docs/staging-environment/">测试环境 <img src="/old/resources/images/external-link.svg" class="external-link"></a>，以避免速率限制问题。虽然这不是一个完美的策略，但总体来说还是很有帮助的。

ACME 请求至少需要几秒钟时间，而内部速率限制有助于防止意外滥用。Caddy 除了您或证书颁发机构（CA）配置的速率限制外，还会使用内部速率限制，因此您可以向 Caddy 提供包含一百万个域名的列表，它将逐步——但以尽可能快的速度——为所有域名获取证书。Caddy 的内部速率限制目前为每个 ACME 账户每 10 秒 10 次尝试。

为避免资源泄漏，当配置发生变更时，Caddy 会中止正在执行的任务（包括 ACME 事务）。虽然 Caddy 能够处理频繁的配置重新加载，但请注意此类运维考量，并考虑将配置更改批量处理，以减少重新加载的次数，并让 Caddy 有机会在后台实际完成证书的获取。

<a id="issuer-fallback"></a>
### 发行方备用方案

Caddy 是首个（也是迄今为止唯一一个）支持完全冗余的服务器，当无法成功获取证书时，它会自动切换到其他证书颁发机构（CA）。

默认情况下，Caddy 启用了两个兼容 ACME 的证书颁发机构：<a href="https://letsencrypt.org">**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link"></a> 和 <a href="https://zerossl.com">**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link"></a>。 如果 Caddy 无法从 Let's Encrypt 获取证书，它将尝试使用 ZeroSSL；如果两者均失败，它将暂停并稍后重试。在配置中，您可以自定义 Caddy 用于获取证书的证书颁发机构，既可以是全局设置，也可以针对特定域名进行设置。


<a id="storage"></a>
## 存储

Caddy 会将其[配置的存储位置](/docs/json/storage/)（若未配置，则使用默认位置——详情请参阅链接）用于存储公钥证书、私钥及其他资产。

**使用默认配置时，您需要了解的关键点是 `$HOME` 文件夹必须具有写入权限且位置固定。** 为帮助您排查故障，如果 `--environ` 参数。

任何配置为使用同一存储的 Caddy 实例都会自动共享这些资源，并作为集群协同管理证书。

在尝试任何 ACME 交易之前，Caddy 会测试已配置的存储，以确保其可写入且具有足够的容量。这有助于减少不必要的锁竞争。


<a id="wildcard-certificates"></a>
## 通配符证书

当 Caddy 被配置为托管具有符合条件的通配符名称的站点时，它可以获取和管理通配符证书。只有当站点名称最左侧的域名标签是通配符时，该站点名称才符合通配符条件。例如， `*.example.com` 符合条件，但以下情况不符合： `sub.*.example.com`, `foo*.example.com`, `*bar.example.com`，以及 `*.*.example.com`。（这是 WebPKI 的限制。）

如果使用 Caddyfile，Caddy 会将站点名称作为证书主题名称的字面值进行处理。换句话说，如果将站点定义为 `sub.example.com` 将导致 Caddy 为 `sub.example.com`，而定义为 `*.example.com` 则会导致 Caddy 为 `*.example.com`。您可以在我们的《[常见 Caddyfile 模式](/docs/caddyfile/patterns#wildcard-certificates)》页面上查看演示。如果您需要不同的行为，[JSON 配置](/docs/json/)可让您更精确地控制证书主题和站点名称（“主机匹配器”）。

从 Caddy 2.10 开始，在为通配符证书设置自动化时，Caddy 会将该通配符证书应用于配置中的各个子域名。除非明确配置（例如使用 `force_automate`).

通配符证书具有广泛的授权范围，仅应在以下情况下使用：当您拥有大量子域名，以至于为每个子域名单独管理证书会给 PKI 系统带来负担，或导致触及 CA 设定的速率限制；或者，在密钥遭到泄露的情况下，隐私权与风险之间的权衡表明，暴露如此大规模的 DNS 区域是值得的。 请注意，仅凭通配符证书无法实现隐藏特定子域名的隐私保护：除非启用了加密客户端问候（ECH），否则这些子域名仍会在 TLS ClientHello 数据包中暴露。（详见下文。）

**注意：** <a href="https://letsencrypt.org/docs/challenge-types/">Let's Encrypt 要求 <img src="/old/resources/images/external-link.svg" class="external-link"></a> 通过 [DNS 验证](#dns-challenge)才能获取通配符证书。


<a id="encrypted-clienthello-ech"></a>
## 加密的 ClientHello (ECH)

通常，TLS 握手过程会以明文形式发送 ClientHello，其中包括服务器名称指示符（SNI；即正在连接的域名）。这是因为该报文包含握手完成后加密连接所需的参数。这当然会将域名（即 ClientHello 中最敏感的部分）暴露给任何能够窃听连接的人，即使他们并不在您身旁。当目标 IP 可能托管多个不同网站时，这会暴露您正在连接的服务，而这也是某些政府审查互联网的方式。

借助加密的 ClientHello，客户端可以通过将真正的 ClientHello 封装在一个“外层”ClientHello 中来保护域名，该“外层”ClientHello 会设定用于解密“内层”ClientHello 的参数。然而，要使该机制正常运作并真正带来隐私保护效益，许多环节必须完美配合。

首先，客户端需要知道应使用哪些参数或配置来加密 ClientHello。这些信息包括公钥和“外部”域名（即“公用名称”）等。该配置必须通过某种可靠的方式发布或分发。

理论上，你可以将其写在一张纸上分发给每个人，但大多数主流浏览器在连接网站时都支持查询包含 ECH 参数的 HTTPS 类型 DNS 记录。因此，你需要：(1) 生成 ECH 配置（包括公钥/私钥对及其他参数），然后 (2) 创建一个包含 base64 编码的 ECH 配置的 HTTPS 类型 DNS 记录。

或者……你可以让 Caddy 帮你完成这一切。Caddy 是首个也是唯一一个能够自动生成、发布和提供 ECH 配置的 Web 服务器。

HTTPS 记录发布后，客户端在连接您的网站时需要对该 HTTPS 记录进行 DNS 查询。通常，DNS 查询是以明文形式进行的，这会危及后续 ECH 握手的安全性，因此浏览器需要使用安全的 DNS 协议，例如 DNS-over-HTTPS（DoH）或 DNS-over-TLS（DoT）。根据浏览器的不同，可能需要手动启用此功能。

客户端安全下载 ECH 配置后，会使用嵌入的公钥对 ClientHello 进行加密，并继续连接到您的网站。随后，Caddy 会解密内部的 ClientHello 并开始提供您的网站服务，在此过程中，域名从未以明文形式出现在网络传输中。

<a id="deployment-considerations"></a>
### 部署注意事项

ECH 是一项技术细节繁多的技术。尽管 Caddy 已实现 ECH 的完全自动化，但为了获得最大的隐私保护效益，仍需考虑诸多因素。您还应了解其中的各种权衡取舍。 

#### 发布

只有当某个域名已有记录时，Caddy 才会为其创建 HTTPS 记录。这样可以避免破坏可能由通配符覆盖的子域名的 DNS 查询。请确保您的网站至少有一个指向您服务器的 A/AAAA 记录。如果您仅使用通配符作为 DNS 记录，则该通配符域名也需要出现在您的 Caddy 配置中。

如果某个域名已存在 CNAME 记录，Caddy 将不会为其发布 HTTPS 记录。

#### ECH GREASE

如果你打开 Wireshark，然后使用 Firefox 或 Chrome 等主流浏览器的最新版本（即使已禁用 ECH）访问任何网站（即使是不支持 ECH 的网站），你可能会注意到其握手过程中包含 `encrypted_client_hello` 扩展：

![ECH GREASE](/resources/images/ech-grease.png)

这样做的目的是让真正的 ECH 握手过程与明文握手过程无法区分。如果 ECH 握手过程看起来与普通握手过程不同，审查者只需封锁 ECH 握手过程，就能将副作用和附带损害降至最低。但如果他们封锁了任何带有合理 ECH 扩展的握手过程，实际上就会让互联网的大部分服务瘫痪。（其目的是提高大规模审查的成本。）

这一点在排查连接问题时尤为重要。

#### 密钥轮换

与证书密钥一样，长期使用同一把密钥并非良策（甚至可能极不安全）。因此，应定期轮换 ECH 密钥。与证书不同，ECH 配置并没有严格的过期时间。但服务器仍应定期轮换这些配置。

不过，密钥轮换颇具挑战性，因为客户端需要知道密钥已更新。如果服务器只是简单地用新密钥替换旧密钥，那么除非立即通知客户端新密钥，否则所有 ECH 握手都会失败。但仅仅发布更新后的密钥是不够的。 现实情况是，DNS 记录具有 TTL（生存时间），且解析器会缓存响应等。客户端查询到更新的 HTTPS 记录并开始使用新的 ECH 配置，可能需要数分钟、数小时，甚至数天的时间。

因此，服务器应继续支持旧版 ECH 配置一段时间。否则，可能会导致服务器名称以明文形式大规模泄露。Caddy 会定期轮换密钥，并在轮换后继续支持这些密钥一段时间，直到最终将其弃用。

然而，这可能还不够。由于各种原因，部分客户端仍无法获取更新后的密钥，而每当这种情况发生时，都存在泄露服务器名称的风险。因此，需要另一种方法，通过连接本身（即“带内”）向客户端提供更新的配置。这就是“外部名称”（或“公共名称”）的作用所在。

#### 公共名称

“外部”ClientHello 是一个普通的 ClientHello，但有两个细微的区别，只有源服务器才知道：

1. SNI 扩展名是伪造的
2. ECH 扩展是真实存在的

该“外部”SNI 扩展中包含用于保护您真实域名的公共名称。该名称可以是任意内容，但**您的服务器必须是该公共名称的权威服务器**，因为 Caddy 一定会为此名称获取证书。

如果客户端尝试建立 ECH 连接，但服务器无法解密内部的 ClientHello，它实际上可以使用包含外部名称证书的 _外部_ ClientHello 来完成握手。此安全连接严格 _仅_ 用于向客户端发送当前的 ECH 配置；也就是说，这是一个仅用于完成初始 TLS 连接的临时 TLS 连接。 不会传输任何应用数据：仅传输 ECH 密钥。一旦客户端获得更新后的密钥，即可按预期建立 TLS 连接。

通过这种方式，真实服务器名称得以保护，同时未同步的客户端仍能连接，这两者都是安全性的关键要素。

外部名称可以是您网站的域名、子域名，或是指向您服务器的任何其他域名。我们建议您仅选择一个通用名称。例如，Cloudflare 通过 `cloudflare-ech.com`。这对扩大您的匿名集规模至关重要。

公共名称不应为空；也就是说，必须配置一个公共名称才能使系统正常运行。Caddy 目前并未强制执行此要求（但未来可能会强制），但 ECH 规范要求公共名称的长度至少为 1 字节。 部分软件会接受空名称，而另一些则不会。这可能导致令人困惑的行为，例如浏览器使用 ECH 时，服务器却将其视为无效而拒绝；或者即使 DNS 记录中配置正确，浏览器也因 ECH 无效而未使用它。网站所有者有责任确保 ECH 的正确配置和发布，以保障隐私安全。


#### 匿名集

为了最大限度地发挥 ECH 的隐私保护优势，应努力扩大您的“匿名集”规模。本质上，该集合由面向客户端的服务器组成，这些服务器的行为与观察者完全一致。其核心思想在于，观察者无法轻易缩小或推断出客户端可能连接的站点或服务范围。

实际上，我们建议所有站点仅使用一个公共名称。（每个 ECH 配置仅对应一个公共名称，这意味着在任何给定时间点，只能有一个活跃的 ECH 配置。）如果您以集群模式运行 Caddy，Caddy 会自动与其他实例共享并协调 ECH 配置，从而为您自动处理此事。

如果将这一观点推向极端，就意味着互联网上的每个网站都可能或应该由一个IP地址和一个公共域名来表示……


#### 集中化

……这便引出了我们的下一个话题：集中化。针对 ECH 的批评之一在于，它往往会助长集中化趋势。其作用机制至少体现在两个方面：(1) 客户端倾向于使用 DoH/DoT 进行 DNS 查询，这导致所有 DNS 查询都通过少数几家提供商进行；(2) 在大规模部署时，为了最大化匿名集的规模。

当使用 DoH 或 DoT 时，所有 DNS 查询都会通过 DoH/DoT 提供商进行。在客户端与提供商之间，DNS 数据是加密的，但在提供商与 DNS 服务器之间，数据则未加密。全局 DoH/DoT 实际上将所有敏感的明文 DNS 流量都汇入少数几条宽带管道中，这些管道极易遭到监视……或发生故障。

同样地，如果我们真正地在大规模上将匿名集最大化，所有网站都将隐藏在单一的公共域名之后，例如 `cloudflare-ech.com`。这对隐私保护有利，但整个互联网将完全受制于 Cloudflare 和那个单一域名。当然，达到这种程度的最大化既非必要也不现实，但其理论意义依然成立。

我们建议每个组织或个人为其所有网站选择一个统一的名称并加以使用，在大多数情况下，这应能提供足够的隐私保护。不过，请根据您的具体情况，结合自身威胁模型咨询专家。


#### 子域隐私

如果部署得当，借助 ECH，理论上现在可以防止子域名被侧信道攻击泄露。

大多数网站并不需要这样做，因为通常来说，子域名属于公开信息。我们建议不要在域名中包含敏感信息。话虽如此……

为避免将敏感子域名泄露到证书透明度（CT）日志中，请改用通配符证书。换句话说，在配置中，请不要使用 `sub.example.com`，请改用 `*.example.com`。（有关重要信息，请参阅[“通配符证书”](#wildcard-certificates)。）

另一个信息泄露源是DNSSEC，大多数权威DNS服务器默认都会使用该协议。通过一种名为“区域漫游”（zone walking）的技术，攻击者可以查看用于提供经过认证的不存在响应的NSEC记录，从而枚举子域名。 为此，这些记录会指向按字母顺序排列的下一个可用子域名，从而形成包含所有记录的链表。请确保您的域名至少使用 NSEC3，或最好使用通配符 CNAME 记录来缓解此风险。

然后，在 Caddy 中启用 ECH。只要尝试连接的每个客户端都使用 ECH 且具备可靠的实现，结合 ECH 和通配符 CNAME 记录的通配符证书就能有效隐藏子域名。（不过，隐私保护仍取决于客户端的配合。）


<a id="enabling-ech"></a>
### 启用 ECH

由于 ECH 要正常运行需要将配置发布到 DNS 记录中，因此您需要构建一个集成了 [caddy-dns 模块](https://github.com/caddy-dns)的 Caddy 版本，以适配您的 DNS 服务商。

然后，在 Caddyfile 中，通过全局选项指定您的 DNS 提供商配置，以及您想要使用的 ECH 公共名称：

```caddy
{
	dns <provider config...>
	ech example.com
}
```

请记住：

- 必须已安装 DNS 提供商模块，并且必须为您的提供商/账户配置了正确的设置。
- ECH 公共名称应指向您的服务器。Caddy 会为其获取证书。该名称不必是您网站的域名之一。

如果使用 JSON，请将这些属性添加到 `tls` app 中：

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

这些配置将启用 ECH 并为您的所有站点发布 ECH 配置。如果您需要自定义行为或进行高级设置，JSON 配置将提供更大的灵活性。

<a id="verifying-ech"></a>
### 验证 ECH

目前围绕 ECH 的工具还不多，因此截至本文撰写之时，验证其是否正常运行的最佳且最通用方法是使用 Wireshark，并在 ServerName 字段中查找您的公钥名称。

首先，启动服务器，并确认日志中显示了类似“已发布 ECH 配置列表”的记录（针对您的域名）。（如果发布过程中出现任何错误，请确保您的 DNS 提供商模块支持 [libdns 1.0](https://github.com/libdns/libdns)；若遇到问题，请向提供商的代码库提交问题报告。）Caddy 还应为公共域名获取证书。

接下来，请确保您的浏览器已启用 ECH；这可能需要启用 DoH/DoT。此外，建议清除浏览器（或系统）的 DNS 缓存，以确保其能获取新发布的 HTTPS 记录。我们还建议关闭浏览器，或者至少打开一个新的无痕标签页，以确保其不会复用现有连接。

然后，打开 Wireshark 并开始监听相应的网络接口。在 Wireshark 收集数据包的同时，在浏览器中加载您的网站。随后您可以暂停 Wireshark。找到您的 TLS ClientHello 数据包，您应该会在 ServerName 字段中看到“_public name_”，而不是您实际连接的域名。

请注意：即使未启用 ECH，您仍可能看到 `encrypted_client_hello` 扩展名。关键指标是 SNI 值。如果 ECH 运行正常，你绝不会在 Wireshark 中看到以明文形式显示的真实网站名称。

如果您在使用 ECH 时遇到部署问题，请先在我们的[论坛](https://caddy.community)中提问。如果是 bug，您可以在 GitHub 上[提交问题](https://github.com/caddyserver/caddy/issues)。


<a id="ech-in-storage"></a>
### 仓库中的 ECH

ECH 配置存储在已配置存储模块（默认是文件系统）的[数据目录](/docs/conventions#data-directory)下的 `ech/configs` 文件夹下。

下一个文件夹是一个 ECH 配置 ID，这些 ID 是随机生成的，且相对不重要。规范建议采用随机生成的方式，以帮助减轻指纹识别和追踪的风险。

元数据旁路文件有助于 Caddy 记录发布操作的最后发生时间。这可以避免在每次重新加载配置时频繁向您的 DNS 提供商发送请求。如果您需要重置此状态，可以安全地删除该元数据文件。不过，这可能会重置密钥轮换的时间。您也可以直接编辑该文件，仅清除其中与发布相关的信息。
