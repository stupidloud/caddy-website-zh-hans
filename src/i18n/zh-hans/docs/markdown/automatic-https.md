---
title: "自动 HTTPS"
---

<a id="automatic-https"></a>
# 自动 HTTPS

**Caddy 是第一个*自动且默认*启用 HTTPS 的 Web 服务器。**

Automatic HTTPS 会为所有网站配置 TLS 证书并保持续期。它还会自动将 HTTP 重定向到 HTTPS。Caddy 采用安全且现代的默认配置，避免停机，也不需要额外配置或外部工具。

<aside class="tip">
	Caddy 率先提出了 Automatic HTTPS 的技术方案；自 2015 年该技术首次可用起我们就持续在做这件事。Caddy 的 HTTPS 自动化逻辑是当前世界上最成熟、最稳健的实现之一。
</aside>

这是一个展示工作原理的 28 秒视频：

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**菜单：**

- [概览](#overview)
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
- [加密 ClientHello (ECH)](#encrypted-clienthello-ech)



<a id="overview"></a>
## 概览

**默认情况下，Caddy 会通过 HTTPS 服务所有站点。**

- Caddy 使用本地自动受信任（如果允许）的自签名证书，为 IP 地址和本地/内部主机名提供 HTTPS。
	- 例如：`localhost`、`127.0.0.1`
- Caddy 使用公共 ACME 证书颁发机构（例如 [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) 或 [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com)）签发的证书为公共 DNS 名称提供 HTTPS。
	- 例如：`example.com`、`sub.example.com`、`*.example.com`

Caddy 会自动保持所有受管理证书的续期，并自动将 HTTP（默认端口 `80`）重定向到 HTTPS（默认端口 `443`）。

**本地 HTTPS 情况下：**

- Caddy 可能会提示输入密码，把它的唯一根证书安装到信任库。该操作每个根证书仅需一次，您可随时移除。
- 任何未信任 Caddy 根 CA 证书的客户端访问站点时，都会看到安全错误。

**公共域名情况：**

<aside class="tip">

这也是所有基础生产网站的常见要求，不只针对 Caddy。关键差别在于在运行 Caddy 之前，先把 DNS 记录配置好，从而让 Caddy 能完成证书申请。

</aside>


- 您的域名 A/AAAA 记录已指向服务器，
- `80` 和 `443` 端口对外可达，
- Caddy 可以绑定这些端口（或这些端口转发到了 Caddy），
- 您的[数据目录](/docs/conventions#data-directory)可写且持久化，
- 并且域名已在配置中合适的位置出现。

满足上述条件后，站点会自动通过 HTTPS 提供，不需要额外操作，开箱即用。

HTTPS 使用的是共享的公共基础设施。作为服务器管理员，您应理解本页其他内容，避免常见问题、在故障时快速排查，并正确配置高级部署。



<a id="activation"></a>
## 激活

当 Caddy 已知其正在服务的域名（即主机名）或 IP 地址时，会自动启用 Automatic HTTPS。根据运行和配置方式不同，可通过多种方式让 Caddy 知道您的域名/IP：

- 在 [Caddyfile](/docs/caddyfile) 中设置 [站点地址](/docs/caddyfile/concepts#addresses)
- 在 [JSON routes](/docs/modules/http#servers/routes) 的顶层设置 [host matcher](/docs/json/apps/http/servers/routes/match/host/)
- 通过命令行参数，例如 [`--domain`](/docs/command-line#caddy-file-server) 或 [`--from`](/docs/command-line#caddy-reverse-proxy)
- 使用 [automate](/docs/json/apps/tls/certificates/automate/) 证书加载器

以下任一情况都会导致 Automatic HTTPS 未被启用，或仅部分生效：

- 通过 [JSON](/docs/json/apps/http/servers/automatic_https/) 或 [Caddyfile](/docs/caddyfile/options#auto-https) 显式禁用
- 配置里未提供任何主机名或 IP 地址
- 只监听 HTTP 端口
- 在 Caddyfile 中给[站点地址](/docs/caddyfile/concepts#addresses)加上 `http://` 前缀
- 手动加载证书（除非设置了 [`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/)）

**特殊情况：**

- 以 `.ts.net` 结尾的域名不会由 Caddy 管理。Caddy 会在握手阶段自动尝试从本地运行的 [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) 实例获取这些证书。这要求您的 [Tailscale 账号已启用 HTTPS <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/)，并且 Caddy 进程要么以 root 运行，要么配置 `tailscaled`，给 Caddy 用户授予[获取证书的权限](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348)。


<a id="effects"></a>
## 效果

当 Automatic HTTPS 启用后，会发生以下内容：

- 会为所有[符合条件的域名](#hostname-requirements)申请并续期证书
- 将 HTTP 重定向到 HTTPS（使用 [HTTP 端口](/docs/modules/http#http_port) `80`）

Automatic HTTPS 从不覆盖显式配置，只会补充。

如果已有[服务器](/docs/json/apps/http/servers/)在 HTTP 端口监听，那么 HTTP 到 HTTPS 的重定向路由将插入到带有 host matcher 的自定义路由之后、用户定义的 catch-all 路由之前。

您可以按需[自定义或禁用 Automatic HTTPS](/docs/json/apps/http/servers/automatic_https/)；例如跳过部分域名或禁用重定向（在 Caddyfile 中通过[全局选项](/docs/caddyfile/options)）。


<a id="hostname-requirements"></a>
## 主机名要求

所有主机名（域名）满足以下条件则可申请全托管证书：

- 非空
- 只包含字母数字、连字符、点和通配符（`*`）
- 不以点开始或结束（[RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5)）

此外，以下主机名可申请公开受信任证书：

- 不是 localhost（包括 `.localhost`、`.local`、`.internal` 及 `.home.arpa` 顶级域名）
- 不是 IP 地址
- 左侧仅有一个通配符 `*`


<a id="local-https"></a>
## 本地 HTTPS

Caddy 自动为所有指定了主机（域名、IP 或主机名）的站点启用 HTTPS，包括内部和本地主机。一些主机要么不是公开地址（如 `127.0.0.1`、`localhost`），要么通常不满足公开受信任证书条件（例如 IP 地址——可从部分 CA 获取）。这类站点除非禁用，否则仍然走 HTTPS。

对于非公开站点的 HTTPS 服务，Caddy 会生成自身的证书颁发机构（CA）并用于签名证书。信任链包括根证书与中间证书，站点证书由中间证书签发。它们存储在 [Caddy 数据目录](/docs/conventions#data-directory)下的 `pki/authorities/local`。

Caddy 的本地 CA 由 [Smallstep 库 <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/) 提供能力支持。

本地 HTTPS 不使用 ACME，也不做 DNS 验证。它仅在本机生效，并且只要 CA 根证书已安装就会被信任。

<a id="ca-root"></a>
### CA 根证书

根私钥使用加密安全的伪随机源唯一生成，并以受限权限持久化到存储中。根私钥仅在执行签名时载入内存，任务结束后即可被垃圾回收。

虽然可将 Caddy 配置为直接用根证书签名（用于支持非规范客户端），但此项默认关闭；根密钥仅用于签发中间证书。

第一次使用根密钥时，Caddy 会尝试将其安装到系统本地信任库。如果无权限，会提示输入密码。可通过 Caddyfile 中的 [`skip_install_trust`](/docs/caddyfile/options#skip-install-trust) 或 JSON 配置中的 [`"install_trust": false`](/docs/json/apps/pki/certificate_authorities/install_trust/) 禁用该行为。如果因为以非特权用户运行而安装失败，您可使用 [`caddy trust`](/docs/command-line#caddy-trust) 以特权用户权限重试安装。

<aside class="tip">
	只要您的主机未被入侵且根密钥未泄露，在自己的机器上信任 Caddy 根证书是安全的。
</aside>

根 CA 安装后，您会在本地信任库中看到名称为“Caddy Local Authority”（除非您配置了其他名称）。如有需要，可随时移除（`caddy untrust` 命令可简化操作）。

请注意，将证书自动安装到本地信任库仅为便捷性考虑，不能保证必定成功，尤其是在容器环境或 Caddy 以无特权系统服务运行时。若您依赖内部 PKI，确保将 Caddy 根 CA 添加到所需信任库仍是系统管理员职责（这已超出 Web 服务器职责范围）。


<a id="ca-intermediates"></a>
### CA 中间证书

系统还会生成一个中间证书和密钥，用于签署 leaf（单站点）证书。

与根证书不同，中间证书有效期更短，会在需要时自动续期。


<a id="testing"></a>
## 测试

如果您在测试或实验 Caddy 配置，请先把 [ACME 端点](/docs/modules/tls.issuance.acme#ca)切换为预发布或开发环境 URL，否则很容易触发限流规则，影响 HTTPS 可用性，最长可能持续一周，具体取决于触发的限制。

Caddy 的默认 CA 之一是 [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/)，它提供一个[预发布端点 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/)，该端点不受同一组 [速率限制 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/)。

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

<a id="acme-challenges"></a>
## ACME 挑战

公开受信任 TLS 证书申请需要经公开受信任的第三方机构校验。如今该流程通常通过 [ACME 协议 <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555) 自动完成，可采用以下三种“挑战类型”（challenge types）之一。

默认启用前两种挑战。若启用多个挑战，Caddy 会随机选择一种，避免过度依赖某一类型。系统会逐渐学习哪种挑战成功率更高，并优先使用，但在必要时会回退到其他可用类型。


<a id="http-challenge"></a>
### HTTP 挑战

HTTP 挑战会对候选主机名的 A/AAAA 记录做权威 DNS 查询，然后通过端口 `80` 的 HTTP 请求一个临时加密资源。如果 CA 收到预期资源，即发放证书。

此挑战要求端口 `80` 可公开访问。如果 Caddy 无法监听 80 端口，需将来自该端口的流量转发到 Caddy 的 [HTTP 端口](/docs/json/apps/http/http_port/)。

此挑战默认启用，无需显式配置。


<a id="tls-alpn-challenge"></a>
### TLS-ALPN 挑战

TLS-ALPN 挑战先对候选主机名的 A/AAAA 记录做权威 DNS 查询，再通过端口 `443` 发起包含特殊 ServerName 与 ALPN 值的 TLS 握手请求临时资源。如果 CA 识别到预期资源，证书即被颁发。

此挑战要求端口 `443` 可公开访问。如果 Caddy 无法监听 443 端口，需将来自该端口的数据包转发到 Caddy 的 [HTTPS 端口](/docs/json/apps/http/https_port/)。

此挑战默认启用，无需显式配置。


<a id="dns-challenge"></a>
### DNS 挑战

DNS 挑战会对候选主机名的 `TXT` 记录进行权威 DNS 查询，并查找具有特定值的特殊 `TXT` 记录。CA 若看到预期值，则会签发证书。

DNS 挑战无需打开任何端口，且请求证书的服务器也不必对外可达。不过它需要配置：Caddy 需要有权限访问您的域名 DNS 提供商，以便创建/清除特殊的 `TXT` 记录。如果启用 DNS 挑战，其他挑战默认会被禁用。

由于 ACME CA 在做 `TXT` 记录校验时遵循 DNS 标准，您可以使用 CNAME 记录把挑战响应委托给其他 DNS 区域。这可用于将 `_acme-challenge` 子域委派到[其他区域](/docs/caddyfile/directives/tls#dns_challenge_override_domain)。若您的 DNS 提供商不提供 API，或不被 Caddy 的 DNS 插件支持，此方式尤其有用。

DNS 提供商支持由社区共同维护。[查看 wiki 了解如何在您的提供商上开启 DNS 挑战。](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


<a id="on-demand-tls"></a>
## 按需 TLS

Caddy 提出并实现了一个新技术，称为 **按需 TLS**。它会在第一次需要证书的 TLS 握手时动态申请证书，而不是在配置加载时申请。关键点是：无需在配置里提前硬编码域名。

很多企业依赖该特性，在服务数万站点时，以更低成本、更低运维负担扩展 TLS 部署。

按需 TLS 适用于以下场景：

- 启动或重载服务器时，您并不知道全部域名；
- 域名可能尚未及时配置（DNS 记录尚未下发）；
- 您不直接管理这些域名（例如客户域名）。

启用按需 TLS 后，您无需在配置里指定域名即可获取证书。具体是：当收到一个服务器名（SNI）对应的 TLS 握手，而 Caddy 尚无该域名证书时，Caddy 会先持有该握手并获取证书后再完成握手。延迟通常只有几秒，且只有第一次握手会变慢；后续握手会很快，因为证书会被缓存复用，续期也在后台进行。后续握手可能触发续期维护，但只要证书尚未过期，这类维护仍在后台完成。

<a id="using-on-demand-tls"></a>
### 使用按需 TLS

**按需 TLS 必须同时启用并加上限制，才能防止滥用。**

若使用 JSON 配置，在 [TLS 自动化策略](/docs/json/apps/tls/automation/policies/)中启用；若使用 Caddyfile，则在站点块通过 [`tls`](/docs/caddyfile/directives/tls) 指令启用。

要防止滥用，必须配置限制。这可通过 JSON 配置里的 [`automation`](/docs/json/apps/tls/automation/on_demand/) 对象，或 Caddyfile 的 [`on_demand_tls`](/docs/caddyfile/options#on-demand-tls) 全局选项完成。限制为全局级别，不支持按站点/域名单独配置。主要限制是“ask”端点：Caddy 会向该端点发送 HTTP 请求，确认是否有权限为握手中的域名申请并管理证书。换言之，您需要一个内部后端，例如可查询数据库账户表、判断客户是否已绑定该域名。

也要关注 CA 的签发速度。若超过几秒，只有首次客户端会感知到明显延迟。

考虑到其延迟特征和防滥用所需额外配置，我们只建议在上述场景确有需求时开启按需 TLS。

[查看 wiki 文章了解按需 TLS 的正确使用方法。](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)


<a id="errors"></a>
## 错误

Caddy 会尽量在证书管理发生错误时继续提供服务。

默认情况下，证书管理在后台进行，故不会阻塞启动或拖慢站点；但也意味着部分证书未就绪时服务可能已启动。后台机制结合指数退避，可在较长时间内持续重试。

证书申请或续期失败时的流程如下：

1. Caddy 在短暂暂停后重试一次，以应对偶发问题
2. Caddy 稍后暂停并切换到下一个已启用的挑战类型
3. 尝试完所有启用的挑战类型后，[会尝试下一个已配置的签发机构](#issuer-fallback)
	- Let's Encrypt
	- ZeroSSL
4. 尝试全部签发机构后，进入指数退避
	- 尝试间隔最大为 1 天
	- 最多持续 30 天

针对 Let's Encrypt 重试时，Caddy 会切换到其[测试环境 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/)，以规避限流问题。这不是完美方案，但通常有效。

ACME 挑战至少需要几秒。内部速率限制能进一步减轻误用影响。除了您或 CA 配置的限制外，Caddy 还会有内部速率限制，默认每个 ACME 账户每 10 秒 10 次。也就是说，您可以一次给 Caddy 上百万域名，它会逐步但尽可能快地完成证书获取。

为了减少资源浪费，配置变更时 Caddy 会中止正在进行中的任务（包括 ACME 事务）。虽然 Caddy 可处理频繁重载配置，但请注意运维影响，建议按批量更新配置，减少重载次数，让证书在后台有机会完整完成。

<a id="issuer-fallback"></a>
### 签发机构回退

Caddy 是目前首个（也仍是少数）在证书获取失败时实现完全冗余自动故障转移到其他 CA 的服务器。

默认情况下，Caddy 启用两个 ACME 兼容 CA：[**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) 和 [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com)。如果从 Let's Encrypt 获取失败，会尝试使用 ZeroSSL；如果两者都失败，稍后退避后重试。配置中可按需自定义 Caddy 使用的签发机构（全局或按名称）。


<a id="storage"></a>
## 存储

Caddy 会将公钥证书、私钥及其他资源写入其[配置的存储介质](/docs/json/storage/)（若未配置，则使用默认存储，可见链接说明）。

**使用默认配置时，最关键的是 `$HOME` 目录必须可写且持久。** 为便于排查，启动时若设置 `--environ`，Caddy 会打印环境变量。

所有使用同一存储配置的 Caddy 实例会自动共享资源，并以集群方式协同证书管理。

在任何 ACME 事务前，Caddy 会先检测目标存储是否可写且容量充足，以减少不必要的锁竞争。


<a id="wildcard-certificates"></a>
## 通配符证书

当站点名为符合条件的通配符名称时，Caddy 可以申请和管理通配符证书。站点名若只在最左侧标签使用通配符 `*`，则具备通配符资格。例如，`*.example.com` 合法；以下不合法：`sub.*.example.com`、`foo*.example.com`、`*bar.example.com`、`*.*.example.com`。这是 WebPKI 的限制。

若使用 Caddyfile，Caddy 会按 site 名字字面处理证书主题名。也就是说，`sub.example.com` 会让 Caddy 管理 `sub.example.com` 的证书，而 `*.example.com` 会让 Caddy 管理 `*.example.com` 的通配符证书。可在 [Caddyfile 常见模式](/docs/caddyfile/patterns#wildcard-certificates)页面查看示例。若您需要不同行为，可在 JSON 配置里更精确地控制证书主题与站点名（“host matchers”）。

自 Caddy 2.10 起，自动化通配符证书时，Caddy 会为配置中的各个子域名使用该通配符证书。除非显式设置（如 `force_automate`），否则不会单独申请每个子域名证书。

通配符证书赋予较高的权限，应仅在子域名数量巨大、若为每个子域单独管理证书会过度消耗 PKI 或触发 CA 速率限制时使用。若因密钥泄露而暴露大量 DNS 区域信息且您认为可接受隐私权衡，也可考虑使用。注意，仅有通配符证书并不能隐藏具体子域名：如果未启用 Encrypted ClientHello（ECH），这些子域名仍会在 TLS ClientHello 包中暴露（见下文）。

**注意：** [Let's Encrypt 要求 <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) 使用 [DNS 挑战](#dns-challenge)才能申请通配符证书。


<a id="encrypted-clienthello-ech"></a>
## 加密 ClientHello (ECH)

通常 TLS 握手会以明文发送 ClientHello，其中包含 SNI（Server Name Indicator，即目标域名）。这是因为该报文承载握手后加密连接所需参数，因而会把域名（ClientHello 中最敏感的信息之一）暴露给任何可以监听连接的人，即便对方不在您身边。当目标 IP 托管多个站点时，这能被用来判断您正在访问的服务，也是部分政府审查互联网的依据之一。

使用 ECH 时，客户端可将真实 ClientHello 封装在“外层”ClientHello 中，由该外层报文协商解密“内层”ClientHello 的参数。然而，要真正发挥隐私收益，需要多个环节正确协同。

首先，客户端必须知道加密 ClientHello 所用参数或配置，包括公钥和“外层”域名（即“公共名”）等。该配置必须通过可靠方式发布和分发。

理论上您可以把配置写在纸上发给每个人，但大多数主流浏览器在连接网站时会查询包含 ECH 参数的 HTTPS 资源记录。实际流程是：先生成 ECH 配置（公私钥对及其他参数），再在 DNS 中创建一条 HTTPS 记录并写入 base64 编码的 ECH 配置。

或者，交给 Caddy 全权处理。Caddy 是首个并且目前唯一一款可自动生成、发布并提供 ECH 配置的 Web 服务器。

HTTPS 记录发布后，客户端在连接站点时会查询该记录；DNS 通常是明文查询，会影响后续 ECH 握手安全，因此浏览器需使用 DNS-over-HTTPS（DoH）或 DNS-over-TLS（DoT）等安全 DNS 协议，部分浏览器可能需手动开启。

客户端安全下载 ECH 配置后，会用其中的公钥加密 ClientHello，随后连接站点。Caddy 解密内层 ClientHello 并提供服务，域名不会以明文在链路上传输。

<a id="deployment-considerations"></a>
### 部署注意事项

ECH 的技术细节较复杂。尽管 Caddy 完全集成自动化 ECH，要达成最佳隐私仍需综合考虑，并理解若干权衡。

<a id="publication"></a>
#### 发布

只有当域名已有记录时，Caddy 才会创建该域名的 HTTPS 记录。这样可避免影响可能被通配符覆盖的子域 DNS 查询。请确保站点至少有一条指向您的服务器的 A/AAAA 记录；若您仅使用通配符 DNS 记录，则通配符域名也需出现在 Caddy 配置中。

对于已有 CNAME 记录的域名，Caddy 不会发布 HTTPS 记录。

<a id="ech-grease"></a>
#### ECH GREASE

在 Firefox、Chrome 等主流浏览器上，连接任意站点（即便是未支持 ECH 的站点，即便 ECH 关闭）并抓包（如 Wireshark）时，您可能会看到握手里带有 `encrypted_client_hello` 扩展：

![ECH GREASE](/resources/images/ech-grease.png)

目的是让真实的 ECH 握手与明文握手难以区分。若 ECH 握手看起来与普通握手不同，审查方可仅凭这个特征拦截 ECH 流量而副作用较小；但若连带拦截所有带可疑 ECH 扩展的握手，则会导致大范围服务中断。目标是提高广域审查的成本。

在排障阶段，这一点尤其重要。

<a id="key-rotation"></a>
#### 密钥轮换

与证书密钥类似，长期使用同一密钥并不安全，ECH 密钥也应定期轮换。与证书不同，ECH 配置没有严格过期，但仍应按期替换。

密钥轮换的难点在于客户端必须获知新密钥。若服务端直接用新密钥替换旧密钥，且未及时通知客户端，所有 ECH 握手都会失败。并且 DNS 记录有 TTL，递归解析器也会缓存结果，客户端可能需要数分钟甚至数小时、几天才会查询到新 HTTPS 记录并使用新 ECH 配置。

因此服务器应在一段时间内继续支持旧 ECH 配置。否则可能在更大范围内以明文泄露服务器名。Caddy 会定期轮换密钥，并在一段时间内保留旧密钥，直到过期后丢弃。

但这仍可能不够。部分客户端可能出于各种原因未及时拿到新密钥，此时仍有泄露风险。因此还需要一种在“带内”传递配置的方式，也就是 *outer name*（或 *public name*）。

<a id="public-name"></a>
#### Public name

“外层” ClientHello 是一个普通 ClientHello，但有两个只对源站可见的差异：

1. SNI 扩展是伪造的
2. ECH 扩展是真实有效的

该“外层”SNI 扩展携带用于保护真实域名的 public name。该名称可任取，但 **您的服务器必须对该 public name 有权威性**，因为 Caddy 会为它申请证书。

如果客户端尝试 ECH 连接但服务端不能解密内层 ClientHello，服务端仍可用外层 ClientHello 和外层域名证书完成握手。该安全连接仅用于向客户端发送当前 ECH 配置，属于一次性 TLS 连接，仅为完成初始 TLS 连接而存在，不传输应用数据，只发送 ECH key。客户端拿到新密钥后，即可按预期完成 TLS 连接。

这样，真实服务器名仍受保护，而状态不同步的客户端也可继续连接，兼顾安全与可用性。

outer name 可是您站点的任一域名、子域名或任何指向本服务器的域名。建议选择一个通用名称。例如 Cloudflare 在 `cloudflare-ech.com` 背后托管数百万站点，这可放大匿名集合规模。

public name 不应为空；换言之，必须配置该值，流程才能正常工作。Caddy 目前未强制该项（将来可能会调整），但 ECH 规范要求 public name 至少 1 字节。部分软件可接受空名，部分不接受。可能导致的问题包括：浏览器启用 ECH 时显示无效，或虽然 DNS 记录发布正确，但浏览器仍不使用 ECH。确保 ECH 配置与发布正确，是站点所有者的责任。

<a id="anonymity-set"></a>
#### 匿名集

为最大化 ECH 的隐私收益，请尽量扩大 *anonymity set*。本质上，该集合由对外可见但行为一致的客户端面向服务器组成。思路是让观察者难以缩小或推断客户端可能访问的站点/服务。

实践中我们建议所有站点共用一个 public name（每个 ECH 配置只能有一个 public name，也意味着任意时刻仅有一个活动的 ECH 配置）。若您以集群运行 Caddy，实例之间会自动共享并协调 ECH 配置，您无需手工维护。

如果极端放大，这意味着互联网上所有站点都可共享一个 IP 与一个 public name...


<a id="centralization"></a>
#### 集中化

这就引出下一个话题：集中化。对 ECH 的一个常见批评是它可能促使集中化，主要有两方面：(1) 客户端更倾向于 DoH/DoT 查询，导致所有 DNS 请求都集中到少数提供商；(2) 在大规模下最大化匿名集合。

使用 DoH/DoT 时，所有 DNS 查询都经过 DoH/DoT 提供商。客户端到提供商路径上数据是加密的，但提供商到 DNS 服务器路径未必加密。全局 DoH/DoT 实际上会把大量明文 DNS 流量集中到少数通道，既易于观测也增加故障耦合。

同理，如果我们在大规模上最大化匿名集合，所有站点都可能被放在一个 public name 下，如 `cloudflare-ech.com`。这对隐私有利，但也意味着整个互联网会受单一域名和其运营方限制。这种极端化不现实，也不必要，但理论影响成立。

我们建议每个组织或个人为所有站点选择一个统一名称并使用它。多数场景下这已足够，具体隐私模型请结合威胁模型咨询安全专家。

<a id="subdomain-privacy"></a>
#### 子域隐私

ECH 在正确部署时，理论上可从旁路信道角度更好地隐藏子域。

多数站点通常不需要此项，因为子域往往本身就是公开信息。避免把敏感信息直接写进域名。尽量避免将敏感子域泄露到 Certificate Transparency（CT）日志，可改用通配符证书，即用 `*.example.com` 代替 `sub.example.com`（详见 [通配符证书](#wildcard-certificates)）。

另一个泄露来源是 DNSSEC。大多数权威 DNS 服务器默认支持 “zone walking” 风险：可通过 NSEC 记录（用于返回不存在性证明）按字母顺序遍历并枚举子域。为降低风险，请至少使用 NSEC3，或使用通配符 CNAME。

然后在 Caddy 中启用 ECH。通配符证书结合 ECH 与通配符 CNAME 可更好隐藏子域，但前提是所有尝试连接的客户端都启用并正确实现 ECH；隐私保障仍然受客户端实现能力影响。

<a id="enabling-ech"></a>
### 启用 ECH

ECH 需要把配置发布到 DNS，因此您需要一个包含对应 DNS 提供商 [caddy-dns module](https://github.com/caddy-dns) 的 Caddy 构建。

使用 Caddyfile 时，在全局选项里配置 DNS 提供商和 ECH public name，例如：

```caddy
{
	dns <provider config...>
	ech example.com
}
```

注意：

- 必须加载 DNS 提供商模块，并且需要为目标提供商配置正确凭据；
- ECH public name 应指向您的服务器，Caddy 会为其申请证书。该域名不必是站点本身的域名。

若使用 JSON 配置，需在 `tls` app 中添加：

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

以上配置会启用 ECH，并为全部站点发布 ECH 配置。JSON 配置在需要高级定制时更灵活。

<a id="verifying-ech"></a>
### 验证 ECH

目前与 ECH 相关的工具并不多，实践上验证其是否生效最通用的方法是抓包（Wireshark），并在 ServerName 字段观察 public name。

先启动服务器，确认日志出现如“published ECH configuration list”字样（如果发布报错，请确认 DNS 模块支持 [libdns 1.0](https://github.com/libdns/libdns)，并在遇到问题时在供应商仓库提交 issue）。Caddy 还应能申请到 public name 的证书。

然后确认浏览器已开启 ECH（可能需要开启 DoH/DoT）。建议清理浏览器或系统 DNS 缓存，确保新发布的 HTTPS 记录被及时获取；同时可关闭浏览器并重新用隐私标签页打开，避免复用旧连接。

接着打开 Wireshark，监听合适网卡；在抓包过程中打开站点。暂停抓包后找到 TLS ClientHello，应看到 ServerName 字段是 *public name*，而不是您实际访问的域名。

注意：未启用 ECH 时也可能看到 `encrypted_client_hello` 扩展。关键指标仍是 SNI 值。若 ECH 正常工作，Wireshark 不应看到明文形式的真实站点名。

如遇 ECH 部署问题，请先在 [forum](https://caddy.community) 讨论；若确认是 Bug，可在 GitHub [提交 issue](https://github.com/caddyserver/caddy/issues)。

<a id="ech-in-storage"></a>
### ECH 在存储中的存放

ECH 配置保存在[数据目录](/docs/conventions#data-directory)下配置的 storage 模块（默认是文件系统）内 `ech/configs` 目录。

下一层目录是 ECH 配置 ID，由随机字符串组成，按规约建议使用随机化以降低指纹追踪风险。

一份 metadata sidecar 文件用于记录最近一次发布时间，防止每次配置重载都向 DNS 提供商频繁请求。若必须重置该状态，可安全删除 metadata 文件；但这样也会重置密钥轮换时间。您也可以手动编辑文件，仅清理发布相关字段。
