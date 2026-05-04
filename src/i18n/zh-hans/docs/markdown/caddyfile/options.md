---
title: "全局选项 (Caddyfile)"
---

<script>
ready(function() {
	// We'll add links on the options in the code block at the top
	// to their associated anchor tags.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Add links on comments to their respective sections
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // the leading whitespace
			text = text.slice(text.indexOf('#')); // only the comment part
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Surgically fix a duplicate link; 'name' appears twice as a link
	// for two different sections, so we change the second to #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// Surgically fix `renewal_window_ratio` which appears twice as a link for two different sections, so we change the second to #renewal_window_ratio-1
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>


# 全局选项

Caddyfile 提供了一种指定全局选项的方法。某些选项作为默认值；另一些则用于自定义 HTTP 服务器，且不仅限于某个特定站点；还有一些则用于自定义 Caddyfile 适配器的行为。

Caddyfile 文件的最顶部可以是一个 **全局选项块**。这是一个没有键的块：

```caddy
{
	...
}
```

最多只能有一个，且必须是 Caddyfile 的第一个区块。

可选选项包括（点击每个选项可跳转至其文档）：

```caddy
{
	# 通用选项
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hosts...>
	order <dir1> first|last|[before|after <dir2>]
	storage <module_name> {
		<options...>
	}
	storage_clean_interval <duration>
	admin   off|<addr> {
		origins <origins...>
		enforce_origin
	}
	persist_config off
	log [name] {
		output  <writer_module> ...
		format  <encoder_module> ...
		level   <level>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <duration>
	shutdown_delay <duration>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# TLS Options
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <yours>
	default_sni <name>
	fallback_sni <name>
	local_certs
	skip_install_trust
	acme_ca <directory_url>
	acme_ca_root <pem_file>
	acme_eab {
		key_id <key_id>
		mac_key <mac_key>
	}
	acme_dns <provider> ...
	dns <provider> ...
	ech <public_names...> {
		dns <provider> ...
	}
	on_demand_tls {
		ask        <endpoint>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <name> ...
	renew_interval <duration>
	cert_lifetime  <duration>
	ocsp_interval  <duration>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# 服务器选项
	servers [<listener_address>] {
		name <name>
		listener_wrappers {
			<listener_wrappers...>
		}
		timeouts {
			read_body   <duration>
			read_header <duration>
			write       <duration>
			idle        <duration>
		}
		keepalive_interval <duration>
		keepalive_idle     <duration>
		keepalive_count	   <number>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <headers...>

		trace
		max_header_size <size>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# 文件系统
	filesystem <name> <module> {
		<options...>
	}

	# PKI Options
	pki {
		ca [<id>] {
			name                  <name>
			root_cn               <name>
			intermediate_cn       <name>
			intermediate_lifetime <duration>
			maintenance_interval  <duration>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <path>
				key    <path>
			}
			intermediate {
				format <format>
				cert   <path>
				key    <path>
			}
		}
	}

	# 事件选项
	events {
		on <event> <handler...>
	}
}
```

<a id="general-options"></a>
## 常规选项

##### `debug`
启用调试模式，将日志级别设置为 `DEBUG` 。这将显示更多细节，在故障排除时可能很有帮助（但在生产环境中会产生大量日志）。我们建议您在[社区论坛](https://caddy.community)寻求帮助之前先启用此功能。例如，如果您在 Caddyfile 的顶部没有其他全局选项，可以这样写：

```caddy
{
	debug
}
```


##### `http_port`
服务器用于处理HTTP请求的端口。

**仅限内部使用**；不会更改客户端的 HTTP 端口。通常在内部网络中，若需将端口转发 `80` （例如 `8080`），以便进行路由。

默认： `80`


##### `https_port`
服务器用于HTTPS的端口。

**仅限内部使用**；不会更改客户端的HTTPS端口。通常在内部网络中，若需将端口转发 `443` （例如 `8443`），以便进行路由。

默认： `443`


##### `default_bind`
如果站点中未使用[`bind`指令](/docs/caddyfile/directives/bind)，则此处指定的默认绑定地址将适用于所有站点。默认值为空，表示绑定到所有接口。

<aside class="tip">

请注意，此设置仅适用于由 Caddyfile 生成的服务器；这意味着由“自动 HTTPS”功能为 HTTP 到 HTTPS 重定向创建的 HTTP 服务器将不会继承这些绑定地址。要解决此问题，请确保声明一个 `http://` site（可以是空的，不包含任何指令），以便在调整 Caddyfile 时该 site 已存在，从而接收绑定地址。

</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



##### `order`
为 HTTP 处理程序指令指定执行顺序。由于 HTTP 处理程序以顺序链的方式执行，因此必须确保它们按正确顺序执行。标准指令具有[预定义的顺序](/docs/caddyfile/directives#directive-order)，但如果使用第三方 HTTP 处理程序模块，则需要通过使用此选项或将指令放置在 [`route`](/docs/caddyfile/directives/route) [块](/docs/caddyfile/directives/route)中来显式定义顺序。顺序可以采用绝对形式（`first` 或 `last`），也可采用相对顺序（`before` 或 `after`）来描述。

例如，若要使用[`replace-response`插件](https://github.com/caddyserver/replace-response)，请确保其指令位于 `encode` 之后，这样它才能在响应被编码之前执行替换操作（因为响应是沿着处理程序链向上流转，而不是向下）：

```caddy
{
	order replace after encode
}
```


##### `storage`
配置 Caddy 的存储机制。默认值为 [`file_system`](/docs/json/storage/file_system/)。还有许多其他可用的[存储模块](/docs/json/storage/)以插件形式提供。

例如，要更改文件系统的存储位置：

```caddy
{
	storage file_system /path/to/custom/location
}
```

在将 Caddy 的存储同步到多个 Caddy 实例时，通常需要自定义存储模块，以确保它们都使用相同的证书和密钥。更多详细信息，请参阅[存储部分中的“自动 HTTPS”章节](/docs/automatic-https#storage)。


##### `storage_clean_interval`
应以何种频率扫描存储单元以查找过时或已过期的资产并将其移除。此类扫描会对存储模块产生大量读取（及列表操作），因此对于大型部署，请选择较长的间隔时间。支持[持续时间参数](/docs/conventions#durations)。

每次进程首次启动时，都会对存储进行清理。随后，如果前一次清理耗时少于本次间隔时间的一半，则将在本次间隔开始后的该时间点启动新一轮清理（否则将跳过下次启动）。

默认： `24h`

```caddy
{
	storage_clean_interval 7d
}
```




##### `admin`
自定义[管理 API 端点](/docs/api)。支持占位符。接受[网络地址](/docs/conventions#network-addresses)。

默认： `localhost:2019`，除非 `CADDY_ADMIN` 环境变量已设置。

如果设置为 `off`，则管理员端点将被禁用。禁用后，**若不停止并重启服务器，将无法修改配置**，因为[`caddy reload`命令](/docs/command-line#caddy-reload)会通过管理员API将新配置推送至正在运行的服务器。

请记住，如果运行中服务器的地址已更改为非默认地址，请使用 `--address` CLI 参数配合兼容的[命令](/docs/command-line)，以指定当前的管理端点，如果运行中服务器的地址已从默认值更改。

还支持以下子选项：

- **origins** 用于配置允许连接到该端点的[源](https://developer.mozilla.org/en-US/docs/Glossary/Origin)列表。

  默认选项是经过精心挑选的：
  - 如果监听地址是回环地址（例如 `localhost` 或回环 IP，或 Unix 套接字），则允许的来源为 `localhost`, `::1` 和 `127.0.0.1`，并结合监听地址的端口（因此 `localhost:2019` 即为有效的源地址）。
  - 如果监听地址不是回环地址，则允许的来源地址与监听地址相同。

  如果监听地址的主机不是通配符接口（通配符包括：空字符串，或 `0.0.0.0`，或 `[::]`），则 `Host` 将执行报头强制检查。实际上，这意味着默认情况下， `Host` 会验证报头是否位于 `origins`，因为该接口是 `localhost`。但对于类似 `:2020` ，其接口为通配符接口， `Host` 则不会执行报头验证。

- **enforce_origin** 强制执行 `Origin` 请求头。当客户端发送 CORS 头时，或客户端显式使用 `Sec-Fetch-Mode: no-cors`。否则，当监听地址为通配符接口（因为 `Host` 不进行验证），且管理 API 面向公共互联网开放时，该选项最为有用。它启用 CORS 预检，并确保 `Origin` 头是否符合 `origins` 列表进行验证。仅当您在开发机上运行 Caddy 且需要通过网页浏览器访问管理 API 时才应使用此选项。

例如，要在所有接口上通过不同的端口暴露管理 API —— ⚠️ 该端口**不应对外公开**，否则任何人都可以控制您的服务器；如果需要对外公开，请考虑启用源站强制策略：

```caddy
{
	admin :2020
}
```

要关闭管理 API — ⚠️ 这将导致**无法重新加载配置**，除非停止并重启服务器：

```caddy
{
	admin off
}
```

若要使用 [Unix 套接字](/docs/conventions#network-addresses)作为管理 API，并通过文件权限实现访问控制：

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

仅允许请求包含匹配的 `Origin` 标头：

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```



##### `persist_config`

控制是否将当前的 JSON 配置持久化到[配置目录](/docs/conventions#configuration-directory)中，以避免丢失通过管理 API 进行的配置更改。目前，仅支持 `off` 选项。默认情况下，配置会被持久化。

```caddy
{
	persist_config off
}
```



##### `log`
配置命名日志记录器。

可以传入名称来指定要自定义其行为的特定日志记录器。如果未指定名称，则 `default` 日志器的行为。您可以阅读更多关于 `default` 日志器以及 [Caddy 中日志记录的工作](/docs/logging)原理。

可以通过多次使用 `log` 多次。

这与[`log`指令](/docs/caddyfile/directives/log)不同，后者仅用于配置HTTP请求日志（也称为访问日志）。 `log` global 选项与该指令具有相同的配置结构（ `include` 和 `exclude`除外），完整的文档可在该指令的页面上查阅。

- **output** 用于配置日志的写入位置。

  有关完整文档，请参阅[`log`指令](/docs/caddyfile/directives/log#output-modules)。

- **格式** 描述了日志的编码或格式化方式。

  有关完整文档，请参阅[`log`指令](/docs/caddyfile/directives/log#format-modules)。

- **级别** 是记录日志的最低级别。

  默认： `INFO`.

  可能的值： `DEBUG`, `INFO`, `WARN`, `ERROR`，以及极少见的， `PANIC`, `FATAL`.

- **include** 指定要包含在此日志器中的日志名称。

  默认情况下，此列表为空（即包含所有日志）。

  例如，若要仅包含由管理 API 生成的日志，请包含 `admin.api`.

- **exclude** 指定要从该日志器中排除的日志名称。

  默认情况下，此列表为空（即没有被排除的日志）。

  例如，若要仅排除 HTTP 访问日志，您需要排除 `http.log.access`.

日志记录器的名称 `include` 和 `exclude` 接受的日志记录器名称取决于所使用的模块，而查阅之前的日志是发现它们的最简单方法。

以下是一个示例，它将所有 HTTP 访问日志和管理日志以 JSON 格式记录到标准输出（stdout）：

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

##### `grace_period`
定义了关闭 HTTP 服务器的宽限期（即在配置更改期间或 Caddy 停止运行时）。

在宽限期内，系统不接受新的连接，会关闭空闲连接，并对活动连接进行不耐烦的等待，直至其请求完成。如果客户端未能在宽限期内完成请求，服务器将强制终止连接，以便完成重载并释放资源。支持设置[持续时间值](/docs/conventions#durations)。

默认情况下，宽限期是无限期的，这意味着连接永远不会被强制关闭。

```caddy
{
	grace_period 10s
}
```


##### `shutdown_delay`
定义一个[时长](/docs/conventions#durations)
在[宽限期](#grace_period)*之前*，即将停止运行的服务器仍会正常运行，但 `{http.shutting_down}` 占位符的求值结果为 `true` ，而 `{http.time_until_shutdown}` 返回宽限期开始前剩余的时间。

如果因配置变更而需要关闭任何服务器，这会导致延迟，并实际上将变更推迟到稍后执行。这有助于向该服务器的健康检查程序发出即将停机的通知，并为负载均衡器提供时间将其移出轮询列表；例如：

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Bye-bye in {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Hello, world!"
	}
}
```

<a id="tls-options"></a>
## TLS 选项

##### `auto_https`
配置[自动 HTTPS](/docs/automatic-https)，该功能可让 Caddy 自动管理证书，并为您的网站处理 HTTP 到 HTTPS 的重定向。

有几种模式可供选择：

- `off`: 禁用证书自动化和 HTTP 到 HTTPS 的重定向。

- `disable_redirects`：仅禁用 HTTP 到 HTTPS 的重定向。

- `disable_certs`：仅禁用证书自动化。

- `ignore_loaded_certs`: 即使对于出现在手动加载的证书中的名称，也能实现证书自动化管理。如果通过 [`tls` 指令](/docs/caddyfile/directives/tls)指定了包含某些名称（或通配符）的证书，而您希望这些名称由系统自动管理，此功能将非常有用。

<aside class="tip">

当网站地址包含有效的域名时，此选项不会影响 Caddy 的默认协议（即始终为 HTTPS）。这意味着 `auto_https off` 不会导致您的网站通过 HTTP 提供服务，它只会禁用自动证书管理和重定向。

这意味着，如果您希望通过 HTTP 提供网站服务，应将[网站地址](/docs/caddyfile/concepts#addresses)的前缀更改为 `http://` 或尾部添加 `:80` （或使用 [`http_port` 选项](#http_port)）。

</aside>

```caddy
{
	auto_https disable_redirects
}
```


##### `email`
您的电子邮件地址。该地址主要用于在您的证书颁发机构（CA）处创建 ACME 账户，并且强烈建议您提供该地址，以防证书出现问题。

<aside class="tip">

请注意，Let's Encrypt 可能会向您发送证书即将过期的邮件，但这可能会造成误导，因为 Caddy 在续期时可能选择了其他证书颁发机构（例如 ZeroSSL）。 请检查日志和/或证书本身（例如在浏览器中查看），以确认实际使用的证书颁发机构及其有效期是否仍在有效期内；如果有效，您可以放心忽略来自 Let's Encrypt 的邮件。

</aside>

```caddy
{
	email admin@example.com
}
```


##### `default_sni`
设置默认的 TLS ServerName，用于客户端在 ClientHello 中未使用 SNI 时。

```caddy
{
	default_sni example.com
}
```


##### `fallback_sni`
⚠️ *实验性*

如果进行了配置，当原始 ServerName 与缓存中的任何证书都不匹配时，备用值将作为 ClientHello 中的 TLS ServerName 使用。

此功能的用途非常小众；通常情况下，如果客户端是 CDN，且在下游握手过程中传递了 ServerName，但可以接受包含源服务器主机名的证书，那么您应将此处设置为源服务器的主机名。请注意，Caddy 必须为该名称管理一份证书。

```caddy
{
	fallback_sni example.com
}
```


##### `local_certs`
默认情况下，此设置将导致**所有**证书均由系统内部签发，而非通过 Let's Encrypt 等（公共）ACME 证书颁发机构（CA）签发。在开发环境中，此功能可作为快速切换选项使用。

```caddy
{
	local_certs
}
```


##### `skip_install_trust`
跳过将本地证书颁发机构（CA）的根证书安装到系统信任存储库、Java 信任存储库以及 Mozilla Firefox 信任存储库中的操作。

```caddy
{
	skip_install_trust
}
```


##### `acme_ca`
指定 ACME 证书颁发机构 (CA) 目录的 URL。强烈建议在测试或开发阶段将此项设置为 Let's Encrypt 的<a href="https://letsencrypt.org/docs/staging-environment/">预发布端点 <img src="/old/resources/images/external-link.svg" class="external-link"></a>。默认值：ZeroSSL 和 Let's Encrypt 的生产端点。

请注意，全局配置的 ACME 证书颁发机构（CA）可能并不适用于所有站点；请参阅使用默认 ACME 签发机构[的主机名要求](/docs/automatic-https#hostname-requirements)。

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

##### `acme_ca_root`
指定一个包含 ACME CA 端点受信任根证书的 PEM 文件（如果该证书未存储在系统受信任存储库中）。

```caddy
{
	acme_ca_root /path/to/ca/root.pem
}
```


##### `acme_eab`
指定用于所有 ACME 交易的外部账户绑定。

例如，使用模拟的 ZeroSSL 凭据：

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


##### `acme_dns`
配置用于所有 ACME 交易的 [ACME DNS 验证](/docs/automatic-https#dns-challenge)提供程序。

需要一个包含您 DNS 服务商插件的 Caddy 定制版本。

提供者名称后面的标记会以与在[`tls`指令的`acme`发行者](/docs/caddyfile/directives/tls#acme)中指定时完全相同的方式配置该提供者。

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


##### `dns`
配置一个默认的 DNS 提供商，当相关上下文中未在本地指定其他提供商时使用。例如，如果启用了 ACME DNS 验证但未配置 DNS 提供商，则将使用此全局默认值。此设置也适用于发布加密 ClientHello (ECH) 配置。

要使此功能正常工作，您的 Caddy 二进制文件必须使用指定的 DNS 提供商模块进行编译。

示例：使用环境变量中的凭据：

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

（需要 Caddy 2.10 beta 1 或更高版本。）


##### `ech`
通过在 TLS 握手过程中将指定的公共域名用作明文服务器名称 (SNI)，启用加密 ClientHello (ECH)。在满足适当条件的情况下，ECH 可在连接过程中帮助保护您网站域名的传输安全。Caddy 将针对每个指定的公共域名生成并发布一份 ECH 配置。 发布功能是兼容客户端（例如配置正确的现代浏览器）知晓应使用 ECH 访问您网站的途径。

为了正常工作，ECH 配置必须以客户端预期的方式发布。大多数浏览器（启用了 DNS-over-HTTPS 或 DNS-over-TLS 的浏览器）期望 ECH 配置发布到 HTTPS 类型的 DNS 记录中。Caddy 会自动进行此类发布，但您必须通过 `dns` 子选项，或通过全局[选项`dns`](#dns)进行配置，并且您的 Caddy 二进制文件必须使用指定的 DNS 提供商模块进行编译。（自定义构建版本可在我们的[下载页面](/download)获取。）

**隐私声明：**

- 通常建议**尽可能扩大您的[*匿名集*](https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction)的规模**。因此，我们通常建议大多数用户仅配置*一个*公共域名来保护所有网站。
- **您的服务器应是您指定的公共域名的权威服务器**（即这些域名应指向您的服务器），因为 Caddy 将为这些域名获取证书。 在某些情况下，这些证书对于帮助符合规范的客户端可靠且安全地连接到 ECH 至关重要。它们仅用于促进正确的 ECH 握手过程，不用于传输应用程序数据（您的网站——除非您定义了一个与您的公共域名相同的站点）。
- 每种情况可能各不相同。如果风险较高，我们建议咨询专家来**审查您的威胁模型**，因为 ECH 并非万能解决方案。

以下示例演示了如何使用环境变量中的凭据，将数据发布到托管在 Cloudflare 上的名称服务器：

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

这将导致兼容的客户端使用 `ech.example.net`，而非以明文形式暴露的各个网站名称。

要成功发布，您的网站域名必须托管在已配置的 DNS 服务商处，并且能够使用给定的凭据或服务商配置来修改相关记录。

（需要 Caddy 2.10 beta 1 或更高版本。）


##### `on_demand_tls`
在已启用[按需 TLS](/docs/automatic-https#on-demand-tls) 的情况下配置该功能，但不会启用它（若要启用，请使用[ `tls` 指令的](/docs/caddyfile/directives/tls#syntax) [`on_demand` 子指令](/docs/caddyfile/directives/tls#syntax)）。在生产环境中必须启用此功能，以防止滥用。

- **ask** 将导致 Caddy 向指定的 URL 发送 HTTP 请求，查询某个域名是否被允许签发证书。

  该请求的查询字符串为 `?domain=` 其中包含域名值。

  如果端点返回 `2xx` 状态码，Caddy 将被授权为该名称获取证书。任何其他状态码都将导致证书签发被取消，并使 TLS 握手失败。

<aside class="tip">

该请求端点应*尽可能快地*返回结果，理想情况下应在几毫秒内完成。通常，您的端点应在带有域名索引的数据库中进行常数时间查找；请避免使用循环。请避免进行 DNS 查询或其他网络请求。

</aside>

- **permission** 允许使用自定义模块来确定是否应为特定名称签发证书。该模块必须实现[`caddytls.OnDemandPermission`接口](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission)。 `http` 已包含一个权限模块，这是 `ask` 选项所使用的，并作为向后兼容的快捷方式保留下来。

- ⚠️ 虽然曾提供过 **间隔** 和 **突发** 速率限制选项，但不建议使用。如果您配置中仍保留这些选项，请将其移除。

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


##### `key_type`
指定为 TLS 证书生成的密钥类型；仅当您有特定需求需要进行自定义时，才应更改此设置。

可能的取值包括： `ed25519`, `p256`, `p384`, `rsa2048`, `rsa4096`.

```caddy
{
	key_type ed25519
}
```


##### `cert_issuer`
定义 TLS 证书的签发者（或来源）。

这使得可以全局配置签发者，而不是像使用[`tls`指令的`issuer`子指令](/docs/caddyfile/directives/tls#issuer)那样按站点进行配置。

如果您希望配置多个发行方进行尝试，可以重复此操作。系统将按照定义的顺序依次尝试这些发行方。

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


##### `renew_interval`
应以何种频率扫描所有已加载的受管证书以检查其有效期，并在证书过期时触发续期。

默认： `10m`

```caddy
{
	renew_interval 30m
}
```


##### `cert_lifetime`
向证书颁发机构申请签发证书的有效期。

该值用于计算 `notAfter` ACME订单的字段；因此系统必须具备合理同步的时钟。注意：并非所有CA都支持此功能。请查阅您CA的ACME文档，以确认是否允许此操作以及可使用的具体值。

默认： `0` （由CA决定有效期，通常为90天）

⚠️ 此为实验性功能。可能会进行更改或移除。

```caddy
{
	cert_lifetime 30d
}
```


##### `ocsp_interval`
应多久检查一次 <a href="https://en.wikipedia.org/wiki/OCSP_stapling">OCSP 锚点 <img src="/old/resources/images/external-link.svg" class="external-link"></a> 是否需要更新。

默认： `1h`

```caddy
{
	ocsp_interval 2h
}
```


##### `ocsp_stapling`
可设置为 `off` 以禁用 OCSP 钉合。在因防火墙导致响应服务器不可达的环境中，此设置非常有用。

```caddy
{
	ocsp_stapling off
}
```

##### `renewal_window_ratio`
Caddy 在尝试续期证书之前，证书剩余有效期必须达到的百分比（范围为 0 到 1）。例如，如果某证书的有效期为 90 天，且该百分比设置为 `0.3333` （默认值），则当证书剩余有效期为30天或更少时，Caddy将持续尝试续期。也可通过[`tls`指令的`renewal_window_ratio`子指令](/docs/caddyfile/directives/tls#renewal_window_ratio)按站点进行设置。

您通常无需更改此设置，但如果您的证书颁发机构（CA）的签发时间非常长，在证书有效期后期进行更新可能会很有用。

请注意，这仅供参考，因为 ACME 颁发机构可能会实现 [ARI 扩展](https://datatracker.ietf.org/doc/rfc9773/)，该扩展允许颁发机构指定 ACME 客户端（此处为 Caddy）尝试续期的时间窗口，而该时间窗口可能与该比例不一致。

```caddy
{
	renewal_window_ratio 0.1
}
```


##### `preferred_chains`
如果您的证书颁发机构（CA）提供了多个证书链，您可以使用此选项指定 Caddy 应优先使用哪个证书链。请设置以下选项之一：

- **smallest** 将指示 Caddy 优先选择字节数最少的链。

- **root_common_name** 是一个包含一个或多个通用名称的列表；Caddy 将选择根节点与所指定的通用名称中至少一个匹配的第一个链。

- **any_common_name** 是一个包含一个或多个通用名称的列表；Caddy 将选择首个其签发者与所指定的通用名称中至少一个相匹配的证书链。

请注意，如果将 `preferred_chains` 作为全局选项，若没有[覆盖](/docs/caddyfile/directives/tls#acme)该设置的[发布者级配置](/docs/caddyfile/directives/tls#acme)，则将影响所有发布者。

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```

<a id="server-options"></a>
## 服务器选项

用于自定义 [HTTP 服务器](/docs/json/apps/http/servers/)，其设置可能涉及多个站点，因此无法在站点块中正确配置。这些选项会影响监听器/套接字或 HTTP 层下的其他组件。

可以使用不同的 `listener_address` 值，以针对每台服务器配置不同的选项。例如， `servers :443` 仅适用于绑定到监听地址的服务器 `:443`。省略监听器地址时，这些选项将应用于其余所有服务器。

<aside class="tip">

使用[`caddy adapt`](/docs/command-line#caddy-adapt)命令查找 Caddyfile 中服务器的监听地址。

</aside>


例如，要为端口上的服务器配置不同的选项 `:80` 和 `:443`，您需要指定两个 `servers` 块：

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

使用 `servers` 时，它将**仅**适用于**实际出现在**您的 Caddyfile 中（即由 site 块生成的）的服务器。请注意，[自动 HTTPS](/docs/automatic-https) 会创建一个监听端口 `80`（或 [`http_port` 选项](#http_port)）上的服务器，用于处理 HTTP→HTTPS 重定向并解决 ACME HTTP 验证；这一过程发生在运行时，即在 Caddyfile 适配器应用 `servers` 之后。换言之，这意味着 `servers` **不会**应用于 `:80`，除非你显式声明了一个类似 `http://` 或 `:80` 的站点块。


<aside class="tip">

如果您使用了[`bind`指令](/docs/caddyfile/directives/bind)或[`default_bind`全局选项](/docs/caddyfile/options#default_bind)， `listener_address` *必须*与站点块的绑定地址和端口相匹配，否则设置将无法生效。例如：

```caddy
{
	# 这条配置不会匹配服务器，缺少绑定地址
	servers :8080 {
		name private
	}

	# 这条配置会生效，因为是精确匹配
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



##### `name`

分配给此服务器的自定义名称。通常有助于通过名称在日志和指标中识别服务器。如果未设置，Caddy 将使用 `srvX` 模式，其中 `X` 以 `0` ，并根据配置中的服务器数量递增。

请注意，只有配置文件中通过 site 块生成的服务器才会应用这些设置。[自动 HTTPS](/docs/automatic-https) 会在运行时创建一个 `:80` 服务器（或[`http_port`](#http_port)），因此若要重命名它，您至少需要一个空的 `http://` 站点块。

例如：

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```

</aside>



##### `listener_wrappers`

允许配置[监听器封装器](/docs/json/apps/http/servers/listener_wrappers/)，这些封装器可以修改套接字监听器的行为。它们将按给定的顺序应用。

###### `tls`

该 `tls` 监听器包装器是一个无操作的监听器包装器，用于标记 TLS 监听器在监听器包装器链中的位置。仅当必须在 TLS 握手之前放置另一个监听器包装器时，才应使用它。

###### `http_redirect`

[`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/) 通过检测前几个字节（以判断其并非 TLS 握手，而是 HTTP 请求），为通过 TLS 端口以 HTTP 请求形式建立的连接提供 HTTP 到 HTTPS 的重定向。当在非标准端口（除 `443`），因为除非明确指定协议方案，否则浏览器会尝试使用 HTTP。它必须放置在 `tls` 监听器包装器之前。示例如下：

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

###### `proxy_protocol`

[`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/)监听器封装器（在v2.7.0之前仅通过插件提供）支持解析[PROXY协议](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt)（该协议由HAProxy推广开来）。必须在 `tls` 监听器包装器之前，因为它会在连接开始时解析明文数据：

请注意，在评估匹配器或[`trusted_proxies`](/docs/caddyfile/options#trusted-proxies)之前，PROXY协议的元数据可能会应用于该连接。直接对等方的IP地址在后续评估中将不可用。

```caddy-d
proxy_protocol {
	timeout <duration>
	allow <cidrs...>
	deny <cidrs...>
	fallback_policy <policy>
}
```

- **timeout** 指定等待 PROXY 标头的最大时长。默认值为 `5s`.

- **allow** 是一个包含可接收 PROXY 头信息的受信任来源的 CIDR 范围列表。Unix 套接字默认被视为受信任，因此不包含在此选项中。

- **deny** 是一个包含受信任来源 CIDR 范围的列表，用于拒绝来自这些来源的 PROXY 标头。

- **fallback_policy** 指当 PROXY 头部来自既不在允许列表也不在拒绝列表中的地址时应采取的操作。默认的备用策略是 `ignore`。 `fallback_policy` 的有效值包括：
	- `ignore`: 来自 PROXY 标头的地址，但接受连接
	- `use`: PROXY 标头中的地址
	- `reject`：发送 PROXY 标头时的连接
	- `require`: 连接时需发送 PROXY 标头，若未包含则拒绝
	- `skip`: 接受不包含 PROXY 标头的连接。


例如，对于一个 HTTPS 服务器（需要 `tls` 监听器包装器），该服务器接受来自特定 IP 地址范围的 PROXY 头部，并拒绝来自其他 IP 地址范围的 PROXY 头部，超时时间为 2 秒：

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


##### `timeouts`

- **read_body** 是一个[时长值](/docs/conventions#durations)，用于设定允许从客户端上传数据中读取的时间长度。将其设置为较短的非零值可以缓解 Slowloris 攻击，但也可能影响那些确实速度较慢的客户端。默认不设置超时。

- **read_header** 是一个[时长值](/docs/conventions#durations)，用于设置允许从客户端请求头中读取数据的时间长度。默认不设置超时。

- **write** 是一个[时长值](/docs/conventions#durations)，用于设置允许客户端写入操作的时间长度。请注意，在传输大文件时若将此值设为过小，可能会对那些确实速度较慢的客户端产生负面影响。默认不设置超时。

- **idle** 是一个[时间值](/docs/conventions#durations)，用于设置在启用保持连接功能时等待下一个请求的最长时间。默认值为 5 分钟，以避免资源耗尽。

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


##### `keepalive_interval`

在没有传输其他数据时，为保持 TCP 层连接处于活动状态而发送 TCP 保持活动数据包的间隔。默认值为 `15s`.

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


##### `keepalive_idle`

在没有传输其他数据的情况下，连接处于空闲状态多长时间后，系统才会发送 TCP 保持活动数据包。默认值为 `15s`.

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


##### `keepalive_count`

在判定连接已断开之前，最多发送的 TCP keepalive 数据包数量。默认值为 `9`.

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


##### `0rtt`

默认情况下，QUIC 监听器（即 HTTP/3）启用了 0-RTT（早期数据）功能，允许客户端在 TLS 握手的第一轮往返中发送数据，这有助于提升重复连接的性能。

您可以将此项设置为 `off` 来禁用 QUIC 监听器的 0-RTT。禁用 0-RTT 的一个原因是使用了 [`remote_ip` 匹配器](/docs/caddyfile/matchers#remote-ip)，这会导致在 TLS 握手完成之前进行路由时，对远程地址的验证产生依赖。 这种情况下会返回 HTTP 425 响应，但某些客户端（如浏览器）可能行为异常而不会进行重试，因此禁用 0-RTT 可以确保用户不会看到 425 响应，代价是失去了 0-RTT 带来的性能优势。

```caddy
{
	servers {
		0rtt off
	}
}
```


##### `trusted_proxies`

允许配置应被信任的代理服务器的 IP 范围（CIDR）。默认情况下，不信任任何代理。

启用此选项后，系统会从 HTTP 头部解析可信请求的*真实*客户端 IP（默认情况下， `X-Forwarded-For`；请参阅 [`client_ip_headers`](#client-ip-headers) 以配置其他标头）。若请求被视为可信，客户端 IP 将被添加至[访问日志](/docs/caddyfile/directives/log)，可作为 `{client_ip}` [占位符](/docs/caddyfile/concepts#placeholders)，并支持使用 [`client_ip` 匹配器](/docs/caddyfile/matchers#client-ip)。若请求并非来自受信任的代理，则客户端 IP 将设置为直接传入连接的远程 IP 地址，或（若使用 [PROXY 协议](/docs/caddyfile/options#proxy-protocol)）由该协议设定的地址。默认情况下，标头中的 IP 地址按从左到右的顺序解析。如需更改此行为，请参阅 [`trusted_proxies_strict`](#trusted-proxies-strict)。

某些匹配器或处理程序可能会利用请求的信任状态来做出决策。例如，如果请求被视为可信，[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#defaults) 处理程序将代理并增强敏感 `X-Forwarded-*` 请求头。

目前，只有 `static` [IP 源模块](/docs/json/apps/http/servers/trusted_proxies/)，但可以通过插件进行[扩展](/docs/extending-caddy)，以维护一个动态的 IP 范围列表。


###### `static`

接受一个静态（不变）的IP范围（CIDR）列表作为受信任列表。

作为快捷方式， `private_ranges` 可用于匹配所有私有 IPv4 和 IPv6 地址范围。这相当于指定以下所有范围： `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`.

语法如下：

```caddy-d
trusted_proxies static [private_ranges] <ranges...>
```

以下是一个完整的示例，其中信任了一个示例 IPv4 地址范围和一个 IPv6 地址范围：

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

##### `trusted_proxies_strict`

启用 [`trusted_proxies`](#trusted-proxies) 时，默认情况下会从左到右解析标头中的 IP 地址（由 [`client_ip_headers`](#client-ip-headers) 配置）。找到的第一个不可信 IP 地址即被视为真实客户端地址。自 v2.8 起，您可以通过 `trusted_proxies_strict`。出于向后兼容性考虑，此选项默认处于禁用状态。

上游代理（如 HAProxy、CloudFlare、AWS ALB、CloudFront 等）会将每个新连接的远程地址追加到 `X-Forwarded-For`。建议在 `trusted_proxies_strict` ，因为最左侧的 IP 地址可能会被客户端伪造。

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">

特别是在 AWS ALB 的情况下，您肯定需要启用此选项。[根据其文档](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15)说明，只有将 XFF 模式设置为 `append`。该 IP 地址将附加在 `X-Forwarded-For` 右侧，且只能通过 `trusted_proxies_strict`.

</aside>

##### `trusted_proxies_unix`

该 `trusted_proxies_unix` 选项允许信任所有来自 Unix 套接字的连接，当 Caddy 位于反向代理（可能是另一个 Caddy 实例）之后，且该代理通过 Unix 套接字与其连接时（即 [`bind` 指令](/docs/caddyfile/directives/bind)设置为 Unix 套接字），此功能非常有用。此选项默认处于禁用状态。

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

##### `client_ip_headers`

配合使用[`trusted_proxies`](#trusted-proxies)，可配置用于确定客户端IP地址的头部字段。默认情况下，仅 `X-Forwarded-For` 。可以指定多个标头字段，此时将使用第一个非空的标头值。

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


##### `metrics`

启用指标收集；在抓取指标或通过 OTLP 推送指标之前，必须先启用此功能。请注意，在负载极高的服务器上，指标收集会降低性能。（我们的社区正在致力于改善这一情况。欢迎参与！）

```caddy
{
	metrics
}
```

您可以添加 `per_host` 选项，以主机名对指标进行标记。

```caddy
{
	metrics {
		per_host
	}
}
```

由于监控所有可能的主机可能导致无限基数，Caddy 仅会记录已配置主机的指标，而所有其他主机（例如 attacker.com）则会汇总到“_other”标签下。若需强制监控所有主机，且可接受潜在的无限基数风险，请添加 `observe_catchall_hosts`。请注意，添加 `observe_catchall_hosts` 不会启用 `per_host`。不过，此功能对 HTTPS 服务器会自动启用（因为证书能提供一定程度的保护以防范无限基数问题），但默认情况下对 HTTP 服务器处于禁用状态，以防止来自任意 Host 头部的基数攻击。

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

您可以添加 `otlp` 选项，将相同的指标推送到 OpenTelemetry 协议 (OTLP) 端点。该导出器通过标准的 OpenTelemetry `OTEL_*` 环境变量进行配置，例如 `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL` 和 `OTEL_METRICS_EXPORTER`.

```caddy
{
	metrics {
		otlp
	}
}
```

例如：

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

更多详情请参阅[《带指标的 Monitoring Caddy》](/docs/metrics)。

##### `trace`

记录每个被调用的处理程序。要求日志输出级别为 `DEBUG` 级别输出（可通过[全局选项`debug`](#debug)实现）。

注意：此操作可能会记录您的 HTTP 处理程序模块的配置；如果配置中包含敏感数据，请勿在不安全的环境中启用此功能。

⚠️ 此为实验性功能。可能会进行更改或移除。

```caddy
{
	servers {
		trace
	}
}
```


##### `max_header_size`

从客户端 HTTP 请求头中解析的最大大小。如果超过此限制，服务器将返回 HTTP 状态码 `431 Request Header Fields Too Large`。该参数支持 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支持的所有格式。默认情况下，限制为 `1MB`.

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


##### `enable_full_duplex`

为 HTTP/1 请求启用全双工通信。

对于 HTTP/1 请求，Go HTTP 服务器默认会在开始写入响应之前先读取请求正文中尚未读取的部分，从而阻止处理程序在写入响应的同时并行读取请求。启用此选项将禁用此行为，允许处理程序在写入响应的同时继续读取请求。

对于 HTTP/2+ 请求，Go HTTP 服务器始终允许并行读取和响应，因此此选项无效。

请使用您的 HTTP 客户端进行彻底测试，因为某些旧版客户端可能不支持全双工 HTTP/1，这可能会导致它们陷入死锁。更多信息请参阅 [golang/go#57786](https://github.com/golang/go/issues/57786)。

⚠️ 此为实验性功能。可能会进行更改或移除。

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


##### `log_credentials`

默认情况下，访问日志（通过[`log`](/docs/caddyfile/directives/log)指令启用）中包含可能涉及敏感信息的标头（`Cookie`, `Set-Cookie`, `Authorization` 和 `Proxy-Authorization`）将作为 `REDACTED`.

如果您希望*不*对这些标头进行屏蔽，可以启用 `log_credentials` 选项。

```caddy
{
	servers {
		log_credentials
	}
}
```



##### `protocols`

要支持的 HTTP 协议列表（以空格分隔）。

默认： `h1 h2 h3`

允许的值包括：
- `h1` 针对 HTTP/1.1
- `h2` 对于 HTTP/2
- `h2c` 用于明文传输的 HTTP/2
- `h3` 适用于 HTTP/3

目前，启用 HTTP/2（包括 H2C）必然意味着启用 HTTP/1.1，因为 Go 标准库不允许我们在使用其 HTTP 服务器时禁用 HTTP/1.1。不过，HTTP/1.1 和 HTTP/3 均可独立启用。

请注意，Go 标准库未实现 H2C（“明文 HTTP/2”或“TCP 上的 H2”）和 HTTP/3，因此某些功能或特性可能会受到限制。除非您的应用程序绝对需要，否则我们不建议启用 H2C。

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



##### `strict_sni_host`

要启用此功能，请求的 `Host` 标头与 `ServerName` ，这是使用 TLS 客户端身份验证时的一项必要安全措施。如果存在不匹配，HTTP 状态码 `421 Misdirected Request` 响应将发送给客户端。

如果配置了[客户端身份验证](/docs/caddyfile/directives/tls#client_auth)，此选项将自动启用。这将阻止 TLS 客户端身份验证绕过（域名前置）攻击——此类攻击通常通过在 TLS 握手过程中发送未加密的 SNI 值，然后在建立连接后在 Host 头中填入受保护的域名来实现。此行为是安全的默认设置，但您可以通过 `insecure_off`；例如在运行代理时，若需要使用域名前置且访问不受主机名限制，即可采用此方式。

```caddy
{
	servers {
		strict_sni_host on
	}
}
```


<a id="file-systems"></a>
## 文件系统

该 `filesystem` 全局选项允许声明一个或多个可用于文件 I/O 的文件系统。

这使您能够连接到云端运行的远程文件系统、具有文件式接口的数据库，甚至读取嵌入在 Caddy 二进制文件中的文件。

文件系统通过名称进行声明，以便对其进行标识。这意味着，如果需要，您可以连接多个同类型的文件系统。

默认情况下，Caddy 不包含任何文件系统模块，因此您需要根据要使用的文件系统，在构建 Caddy 时添加相应的插件。

#### 示例

假设使用一个 `custom` 文件系统模块，您可以声明两个文件系统：

```caddy
{
	filesystem foo custom {
		...
	}

	filesystem bar custom {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```


<a id="pki-options"></a>
## PKI 选项

PKI（公钥基础设施）应用是 Caddy [本地 HTTPS](/docs/automatic-https#local-https) 和 [ACME 服务器](/docs/caddyfile/directives/acme_server)功能的基础。该应用定义了能够对证书进行签名的证书颁发机构（CA）。

默认的 CA ID 是 `local`。如果在配置 `ca`时省略了 ID，则 `local` 将默认使用。

##### `name`
证书颁发机构的用户可见名称。

默认： `Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "My Local CA"
		}
	}
}
```

##### `root_cn`
要填入根证书“CommonName”字段中的名称。

默认： `{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "My Local CA - 2024 ECC Root"
		}
	}
}
```

##### `intermediate_cn`
要填入中间证书“CommonName”字段的名称。

默认： `{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "My Local CA - ECC Intermediate"
		}
	}
}
```

##### `intermediate_lifetime`
中间证书的有效[期](/docs/conventions#durations)。此值**必须**小于根证书的有效期（`3600d` 或 10 年）。

默认值： `7d`。除非绝对必要，否则*不建议*更改此设置。

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

##### `maintenance_interval`
检查中间证书（以及适用时根证书）是否需要续期的频率。

默认值： `10m`。除非绝对必要，否则*不建议*更改此设置。

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

##### `renewal_window_ratio`
Caddy 在尝试续期证书之前，证书剩余有效期必须达到的比率（范围为 0 到 1）。例如，如果某张证书的有效期为 1 年，且该比率为 `0.2` （默认值），则当证书剩余有效期为 73 天或更少时，Caddy 将持续尝试续期该证书。

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


##### `root`
用作 CA 根证书的密钥对（证书和私钥）。如果未指定，系统将自动生成并管理该密钥对。

- **格式** 指证书和私钥的提供格式。目前仅 `pem_file` 格式，这是默认选项，因此该字段为可选。
- **cert** 是指证书。当使用 `pem_file` 格式时，此处应为 PEM 文件的路径。
- **key** 是私钥。当使用 `pem_file` 格式时，此处应为 PEM 文件的路径。

##### `intermediate`
用于作为 CA 中间证书的密钥对（证书和私钥）。如果未指定，系统将自动生成并管理该密钥对。

- **格式** 指证书和私钥的提供格式。目前仅 `pem_file` ，这是默认格式，因此该字段为可选。
- **cert** 是指证书。当使用 `pem_file` 格式时，此处应为 PEM 文件的路径。
- **key** 是私钥。当使用 `pem_file` 格式时，此处应为 PEM 文件的路径。

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /path/to/root.pem
				key /path/to/root.key
			}
			intermediate {
				format pem_file
				cert /path/to/intermediate.pem
				key /path/to/intermediate.key
			}
		}
	}
}
```

<a id="event-options"></a>
## 事件选项

当发生（或即将发生）重要事件时，Caddy 模块会触发事件。

事件通常包含元数据负载。了解事件及其负载的最佳方式是查阅各模块的文档，但您也可以通过启用[`debug` 全局选项](#debug)并查看日志来查看事件及其数据负载。

##### `on`

将事件处理程序绑定到指定名称的事件。请指定事件处理程序模块的名称，并随后提供其配置。

例如，要在获取证书后执行一条命令（需要<a href="https://github.com/mholt/caddy-events-exec">第三方插件 <img src="/old/resources/images/external-link.svg" class="external-link"></a>），并通过占位符将事件负载的一部分传递给脚本：

```caddy
{
	events {
		on cert_obtained exec ./my-script.sh {event.data.certificate_path}
	}
}
```

<a id="events"></a>
### 事件

Caddy 会触发以下标准事件：

- <a href="https://github.com/caddyserver/certmagic#events">`tls` events <img src="/old/resources/images/external-link.svg" class="external-link"></a>
- [`reverse_proxy` 活动](/docs/caddyfile/directives/reverse_proxy#events)

插件也可能触发事件，因此请查阅其文档以获取详细信息。
