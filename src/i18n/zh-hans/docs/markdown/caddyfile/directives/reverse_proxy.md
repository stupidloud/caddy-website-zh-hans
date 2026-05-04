---
title: "reverse_proxy（Caddyfile 指令）"
---

<script>
ready(function() {
	// Fix response matchers to render with the right color,
	// and link to response matchers section
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">${text}</a>`;
		}
	});

	// Fix matcher placeholder
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@name')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">@name</a>';
			break;
		}
	}
	
	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}
	
	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Response matcher">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# 反向代理

将请求代理到一个或多个后端，并支持可配置的传输、负载均衡、健康检查、请求处理和缓冲选项。

- [语法](#syntax)
- [上游](#upstreams)
  - [上游地址](#upstream-addresses)
  - [动态上游](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
    - [多路合并](#multi)
- [负载均衡](#load-balancing)
  - [主动健康检查](#active-health-checks)
  - [被动健康检查](#passive-health-checks)
  - [活动](#events)
- [流媒体](#streaming)
- [标头](#headers)
- [改写](#rewrites)
- [运输](#transports)
  - [ `http` 传输](#the-http-transport)
  - [ `fastcgi` 传输](#the-fastcgi-transport)
- [拦截响应](#intercepting-responses)
- [示例](#examples)



<a id="syntax"></a>
## 语法

```caddy-d
reverse_proxy [<matcher>] [<upstreams...>] {
	# backends
	to      <upstreams...>
	dynamic <module> ...

	# load balancing
	lb_policy       <name> [<options...>]
	lb_retries      <retries>
	lb_try_duration <duration>
	lb_try_interval <interval>
	lb_retry_match  <request-matcher>

	# active health checking
	health_uri          <uri>
	health_upstream     <ip:port>
	health_port         <port>
	health_interval     <interval>
	health_passes       <num>
	health_fails	    <num>
	health_timeout      <duration>
	health_method       <method>
	health_status       <status>
	health_request_body <body>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<field> [<values...>]
	}

	# passive health checking
	fail_duration     <duration>
	max_fails         <num>
	unhealthy_status  <status>
	unhealthy_latency <duration>
	unhealthy_request_count <num>

	# streaming
	flush_interval     <duration>
	request_buffers    <size>
	response_buffers   <size>
	stream_timeout     <duration>
	stream_close_delay <duration>

	# request/header manipulation
	trusted_proxies [private_ranges] <ranges...>
	header_up   [+|-]<field> [<value|regexp> [<replacement>]]
	header_down [+|-]<field> [<value|regexp> [<replacement>]]
	method <method>
	rewrite <to>

	# round trip
	transport <name> {
		...
	}

	# optionally intercept responses from upstream
	@name {
		status <code...>
		header <field> [<value>]
	}
	replace_status [<matcher>] <status_code>
	handle_response [<matcher>] {
		<directives...>

		# special directives only available in handle_response
		copy_response [<matcher>] [<status>] {
			status <status>
		}
		copy_response_headers [<matcher>] {
			include <fields...>
			exclude <fields...>
		}
	}
}
```



<a id="upstreams"></a>
## 上游

- **&lt;upstreams...&gt;** 是要进行代理的上游（后端）列表。
- **to**  是指定上游列表的另一种方式，每行一个（或多个）。
- **dynamic**  用于配置 *动态上游* 模块。这允许在每次请求时动态获取上游列表。请参阅下文的[动态上游部分](#dynamic-upstreams)，了解标准动态上游模块的说明。动态上游会在每次代理循环迭代时检索（即如果启用了负载均衡重试，则每个请求可能检索多次），并且优先于静态上游。如果发生错误，代理将回退到使用任何静态配置的上游。


<a id="upstream-addresses"></a>
### 上游地址

静态上游地址可以是仅包含协议和主机/端口信息的 URL，也可以是常规的 [Caddy 网络地址](/docs/conventions#network-addresses)。有效示例：

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

默认情况下，与上游的连接是通过明文 HTTP 建立的。在使用 URL 表单时，可以使用协议方案作为简写来设置某些 [`transport`](#transports) 的默认值。
- 使用 `https://` 作为方案将使用[`http`传输](#the-http-transport)协议，并启用[`tls`](#tls)。

  此外，您可能需要覆盖 `Host` 标头，使其与 TLS SNI 值相匹配，服务器会利用该值进行路由和证书选择。更多详情请参阅下文的 [HTTPS](#https) 部分。

- 使用 `h2c://` 作为方案时，将使用[`http`传输](#the-http-transport)协议，并设置[HTTP版本](#versions)以允许明文HTTP/2连接。

- 使用 `http://` 作为方案等同于省略方案，因为 HTTP 已经是默认值。此语法是为了与其他方案快捷方式保持一致而包含的。

方案不能混合使用，因为它们会修改通用的传输配置（启用了 TLS 的传输无法同时承载 HTTPS 和明文 HTTP）。任何显式的传输配置都不会被覆盖，且省略方案或使用其他端口时，系统不会默认采用特定的传输方式。

在区域中使用 IPv6 时（例如，特定网络接口上的链路本地地址），**不能**使用方案作为快捷方式，因为 `%` 将导致 URL 解析错误；请显式配置传输协议。

使用[网络地址](/docs/conventions#network-addresses)格式时，网络类型应作为上游地址的前缀进行指定。此格式不能与 URL 方案结合使用。作为特例， `unix+h2c/` 作为 `unix/` 网络方案，并具有与 `h2c://` 方案。端口范围可作为快捷方式使用，展开后将生成多个具有相同主机的上游地址。

上游地址**不能**包含路径或查询字符串，因为这将意味着在代理过程中同时重写请求，而这种行为既未定义也不受支持。如果您需要此功能，可以使用[`rewrite`](/docs/caddyfile/directives/rewrite)指令。

如果地址不是 URL（即没有协议），则可以使用[占位符](/docs/caddyfile/concepts#placeholders)，但这会使上游变得“动态固定”，也就是说，在健康检查和负载均衡方面，许多不同的后端可能会被视为一个单一的静态上游。我们建议在可能的情况下改用[动态上游](#dynamic-upstreams)模块。使用占位符时，**必须**包含端口号（可通过占位符替换实现，或作为地址的静态后缀添加）。


<a id="dynamic-upstreams"></a>
### 动态上游

Caddy 的反向代理默认包含一些动态上游模块。请注意，使用动态上游会对负载均衡和健康检查产生影响，具体取决于具体的策略配置：动态上游不会执行主动健康检查；而如果上游列表相对稳定且一致（尤其是采用轮询算法时），负载均衡和被动健康检查的效果会更好。理想情况下，动态上游模块应仅返回健康且可用的后端。


<a id="srv"></a>
#### SRV

从 SRV DNS 记录中检索上游服务器。

```caddy-d
	dynamic srv [<full_name>] {
		service   <service>
		proto     <proto>
		name      <name>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
	}
```

- **&lt;full_name&gt;** 是要查询的记录的完整域名（即 `_service._proto.name`).
- **service** 是全称中的服务组件。
- **proto** 是全称中的协议组件。可以是 `tcp` 或 `udp`.
- **name** 是名称组件。或者，如果 `service` 且 `proto` 为空，则查询完整的域名。
- **refresh** 表示刷新缓存结果的频率。默认值： `1m`
- **解析器** 是用于覆盖系统解析器的 DNS 解析器列表。
- **dial_timeout** 是拨号查询的超时时间。
- **dial_fallback_delay** 指在建立 RFC 6555 快速回退连接之前需要等待的时间。默认值： `300ms`



<a id="aaaaa"></a>
#### A/AAAA

从 A/AAAA DNS 记录中检索上游服务器。

```caddy-d
	dynamic a [<name> <port>] {
		name      <name>
		port      <port>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
		versions ipv4|ipv6
	}
```

- **name** 是要查询的域名。
- **端口** 是后端使用的端口。
- **refresh** 表示刷新缓存结果的频率。默认值： `1m`
- **解析器** 是用于覆盖系统解析器的 DNS 解析器列表。
- **dial_timeout** 是拨号查询的超时时间。
- **dial_fallback_delay** 指在建立 RFC 6555 快速回退连接之前需要等待的时间。默认值： `300ms`
- **versions** 是要解析的 IP 版本列表。默认值： `ipv4 ipv6` 分别对应 A 记录和 AAAA 记录。


<a id="multi"></a>
#### 多路合并

合并多个动态上游模块的结果。如果需要冗余的上游来源，此功能非常有用，例如：由一个备用 SRV 集群作为后备的主 SRV 集群。

```caddy-d
	dynamic multi {
		<source> [...]
	}
```

- **&lt;source&gt;** 是动态上游模块的名称，后跟其配置。可以指定多个。




<a id="load-balancing"></a>
## 负载均衡

负载均衡通常用于将流量分配到多个上游服务器。通过启用重试功能，它也可与一个或多个上游服务器配合使用，在选定可用的上游服务器之前暂存请求（例如，在重启或重新部署上游服务器时等待并缓解错误）。

此功能默认处于启用状态， `random` 策略。重试功能默认处于禁用状态。

- **lb_policy**  是负载均衡策略的名称，以及任何相关选项。默认值： `random`.

  对于涉及哈希的策略，会使用[最高随机权重（HRW）](https://en.wikipedia.org/wiki/Rendezvous_hashing)算法，以确保具有相同哈希键的客户端或请求会被映射到相同的上游服务器，即使上游服务器列表发生变化也是如此。

  某些策略支持将“回退”作为选项（如有注明），在这种情况下，它们会接受一个包含 `fallback <policy>` ，该策略又会采用另一项负载均衡策略。对于此类策略，默认的后备策略是 `random`。配置回退机制可在主策略未选定目标时启用次要策略，从而实现强大的组合效果。若需，回退机制可进行多层嵌套。
  
  例如， `header` 可作为主节点，以便开发人员选择特定的上游，并设置 `first` 作为所有其他连接的备用，从而实现主/备故障转移。
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` 随机选择一个上游

	- `random_choose <n>` 随机选择两个或多个上游节点，然后选择负载最小的那个（`n` 通常为2）

	- `first` 根据配置中定义的顺序，选择第一个可用的上游，从而支持主/备故障转移；请务必同时启用健康检查，否则不会触发故障转移

	- `round_robin` 依次遍历每个上游

	- `weighted_round_robin <weights...>` 依次遍历每个上游服务器，并遵循所提供的权重。权重参数的数量应与配置的上游服务器数量相匹配。权重应为非负整数。例如，如果有两个上游服务器且权重分别为 `5 1`，则第一个上游将被连续选中 5 次，随后第二个上游被选中 1 次，然后循环重复。如果将 0 作为权重，则该上游将不再被选中以处理新请求。

	- `least_conn` 选择当前请求数量最少的上游；如果有多个主机的请求数量最少，则随机选择其中一个

	- `ip_hash` 将远程 IP（直接对等方）映射到一个粘性上游

	- `client_ip_hash` 将客户端 IP 映射到一个粘性上游；建议与启用真实客户端 IP 解析的 [`servers > trusted_proxies` 全局选项](/docs/caddyfile/options#trusted-proxies)配合使用，否则其行为与 `ip_hash` 相同

	- `uri_hash` 将请求 URI（路径和查询字符串）映射到一个粘性上游服务器

	- `query [key]` 通过对查询值进行哈希运算，将请求查询映射到一个粘性上游；如果指定的键不存在，则将使用备用策略来选择上游（`random` 默认情况下）

	- `header [field]` 通过对请求头值进行哈希运算，将请求头映射到一个粘性上游；如果指定的请求头字段不存在，则将使用备用策略来选择上游（`random` 默认情况下）

	- `cookie [<name> [<secret>]]` 在收到客户端的首次请求时（即没有 Cookie 的情况下），系统将使用备用策略来选择上游服务器（默认是 `random`），并在响应中添加一个 `Set-Cookie` 标头（如果未指定，则默认 Cookie 名称为 `lb`）。Cookie 的值是所选上游服务器的拨号地址，经 HMAC-SHA256 哈希处理（使用 `<secret>` 作为共享密钥；如果未指定，则使用空字符串）。
	
	  在后续请求中，如果存在该 Cookie，且上游服务器可用，则该 Cookie 的值将映射到该上游服务器；如果上游服务器不可用或未找到，则根据备用策略选择新的上游服务器，并将该 Cookie 添加到响应中。

	  如果您希望为调试目的使用特定的上游服务器，可以将上游地址与密钥进行哈希运算，并在您的 HTTP 客户端（浏览器或其他）中设置该 Cookie。例如，在 PHP 中，您可以运行以下代码来计算 Cookie 值，其中 `10.1.0.10:8080` 是您的某个上游服务器的地址，而 `secret` 是您配置的密钥。
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```
	
	  您可以通过浏览器的 JavaScript 控制台设置 Cookie，例如设置名为 `lb`:
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries**  表示当下一个可用主机不可用时，针对每个请求尝试选择可用后端的重试次数。默认情况下，重试功能处于禁用状态（值为零）。

  如果还配置了[`lb_try_duration`](#lb_try_duration)，则当达到该时长时，重试可能会提前停止。换句话说，重试时长优先于重试次数。

- **lb_try_duration**  是一个[时长值](/docs/conventions#durations)，用于定义当下一个可用主机不可用时，针对每个请求尝试选择可用后端的时间长度。默认情况下，重试功能处于禁用状态（时长为零）。

  在负载均衡器尝试查找可用上游主机期间，客户端最多会等待这么长时间。一个合理的起始值可能是 `5s` ，因为 HTTP 传输的默认拨号超时时间为 `3s`，这样如果首次选定的上游主机无法连接，至少还能进行一次重试；但请根据您的具体使用场景自由调整，以找到最佳平衡点。

- **lb_try_interval**  是一个[时间间隔值](/docs/conventions#durations)，用于定义从主机池中选择下一个主机时，两次尝试之间的等待时长。默认值为 `250ms`。仅在上游主机请求失败时生效。请注意，若将其设置为 `0`，并且 `lb_try_duration` 非零，可能会导致当所有后端都不可用且延迟极低时 CPU 陷入空转状态。

- **lb_retry_match**  用于限制允许重试的请求类型。如果与上游服务器的连接成功，但随后的往返请求失败，则请求必须满足此条件才能被重试。如果与上游服务器的连接失败，则始终允许重试。默认情况下，仅 `GET` 请求会被重试。

  此选项的语法与[命名请求匹配器](/docs/caddyfile/matchers#named-matchers)相同，但不包含 `@name`。若仅需一个匹配器，可将其配置在同一行。若需多个匹配器，则必须使用代码块。



<a id="active-health-checks"></a>
### 主动健康检查

主动健康检查会根据定时器在后台执行健康检查。要启用此功能， `health_uri` 或 `health_port` 是必需的。

- **health_uri**  是用于主动健康检查的 URI 路径（以及可选的查询字符串）。

- **health_upstream**  是用于主动健康检查的 IP:端口，若与上游地址不同。此设置应与 `health_headers` 以及 `{http.reverse_proxy.active.target_upstream}` 一起使用。

- **health_port**  是用于主动健康检查的端口，如果与上游服务器的端口不同。若指定了 `health_upstream`，则会忽略此项。

- **health_interval**  是一个[时间间隔值](/docs/conventions#durations)，用于定义主动健康检查的执行频率。默认值： `30s`.

- **health_passes**  表示在将后端标记为健康状态之前，所需的连续健康检查次数。默认值： `1`.

- **health_fails**  表示在将后端标记为“不健康”之前所需的连续健康检查次数。默认值： `1`.

- **health_timeout**  是一个[时间值](/docs/conventions#durations)，用于定义在将后端标记为不可用之前等待响应的时间长度。默认值： `5s`.

- **health_method**  是用于主动健康检查的 HTTP 方法。默认值： `GET`.

- **health_status**  是来自健康后端时应返回的 HTTP 状态码。可以是三位数的状态码，也可以是以 `xx` 结尾的状态码类别。例如： `200`（这是默认值），或 `2xx`。

- **health_request_body**  是一个字符串，表示要随主动健康检查一起发送的请求正文。

- **health_body**  是一个子字符串或正则表达式，用于匹配正在进行的健康检查的响应正文。如果后端未返回匹配的正文，则该后端将被标记为不可用。

- **health_follow_redirects**  将导致健康检查跟随上游提供的重定向。默认情况下，重定向响应会导致健康检查被判定为失败。

- **health_headers**  允许指定要在活动健康检查请求中设置的头部信息。如果您需要更改 `Host` ，或者作为健康检查的一部分向后端提供身份验证时，此功能非常有用。



<a id="passive-health-checks"></a>
### 被动健康检查

被动健康检查会随实际的代理请求同步进行。要启用此功能， `fail_duration` 是必需的。

- **fail_duration**  是一个[时长值](/docs/conventions#durations)，用于定义系统应记住失败请求多长时间。当该时长大于 `0` 时将启用被动健康检查；默认值为 `0`（关闭）。一个合理的起始值可能是 `30s`，用于在将异常上游恢复在线时平衡错误率和响应速度；但请根据您的具体用例自由尝试，以找到最合适的平衡点。

- **max_fails**  是指在 `fail_duration` 内，达到该次数后才将后端视为已下线；必须 >= `1`；默认值为 `1`。

- **unhealthy_status**  若响应包含以下任一状态码，则将该请求视为失败。可以是三位数的状态码，也可以是以 `xx` 结尾的状态码类别，例如： `404` 或 `5xx`。

- **unhealthy_latency**  是一个[时长值](/docs/conventions#durations)，如果请求在该时长内未收到响应，则被视为失败。

- **unhealthy_request_count**  是指在将后端标记为不可用之前，允许其处理的并发请求数量。换句话说，如果某个后端当前正在处理此数量的请求，则会被视为“过载”，系统将优先使用其他后端。

  这个数值应该相当大；配置此参数意味着代理将限制 `unhealthy_request_count × upstreams_count` 总并发请求数，超过该限额的任何请求都将因上游服务器不可用而导致错误。


<a id="events"></a>
## 活动

当上游状态从健康变为不健康，或反之，系统会触发[一个事件](/docs/caddyfile/options#event-options)。这些事件可用于触发其他操作，例如发送通知或记录日志。具体事件如下：

- `healthy` 当上游节点此前处于非健康状态，但随后被标记为健康时，会发出此信号
- `unhealthy` 当上游节点此前处于健康状态，但随后被标记为不健康时，会触发此事件

在这两种情况下， `host` 作为元数据包含在事件中，用于标识状态发生变化的上游。它可作为占位符， `{event.data.host}` 配合 `exec` 事件处理程序中作为占位符使用。



<a id="streaming"></a>
## 流媒体

默认情况下，代理会部分缓存响应，以提高网络传输效率。

该代理还支持 WebSocket 连接，会先执行 HTTP 升级请求，然后将连接转换为双向隧道。

<aside class="tip">

默认情况下，当配置被重新加载时，WebSocket 连接会被强制关闭（同时向客户端和上游发送 Close 控制消息）。由于每个请求都持有对配置的引用，因此关闭旧连接对于控制内存使用至关重要。可以通过 [`stream_timeout`](#stream_timeout) 和 [`stream_close_delay`](#stream_close_delay) 选项自定义此关闭行为。

</aside>

- **flush_interval**  是一个[时间间隔值](/docs/conventions#durations)，用于调整 Caddy 向客户端刷新响应缓冲区的频率。默认情况下，不会进行周期性刷新。 负值（通常为 -1）表示“低延迟模式”，该模式会完全禁用响应缓冲，并在每次向客户端写入数据后立即刷新，即使客户端提前断开连接，也不会取消对后端的请求。如果响应满足以下任一条件，则该选项将被忽略，响应将立即刷新至客户端：
	- `Content-Type: text/event-stream`
	- `Content-Length` 未知
	- 代理两端的 HTTP/2 支持情况， `Content-Length` 未知，且 `Accept-Encoding` 要么未设置，要么为“identity”

	- **request_buffers**  会导致代理在将请求体发送给上游之前，先将其中最多 `<size>` 字节的请求正文读入缓冲区，然后再将其发送给上游。这种做法效率极低，仅当上游要求无延迟读取请求正文时才应使用（这本应由上游应用程序自行解决）。该参数支持 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支持的所有大小格式。

	- **response_buffers**  将导致代理先从响应正文中读取最多 `<size>` 字节到缓冲区，然后再返回给客户端。出于性能考虑，应尽可能避免使用此功能，但如果后端内存限制较严格，则可能有用。此参数支持 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支持的所有大小格式。

	- **stream_timeout**  是一个[时间值](/docs/conventions#durations)，超时结束后，WebSockets 等流式请求将被强制关闭。这本质上是在连接保持打开状态过久时将其断开。一个合理的起始值可能是 `24h`，用于清除超过一天的连接。默认：无超时。

	- **stream_close_delay**  是一个[时间值](/docs/conventions#durations)，用于延迟在配置卸载时强制关闭 WebSockets 等流请求；相反，流将保持打开状态，直到延迟时间结束。换言之，启用此选项可防止在 Caddy 配置重新加载时流立即关闭。启用此选项有助于避免因前一配置关闭导致连接被断开的客户端蜂拥重连的情况。一个合理的起始值可以是 `5m`，这样可在配置重新加载后给予用户 5 分钟时间自然离开页面。默认：不延迟。



<a id="headers"></a>
## 标头

代理可以在自身与后端之间**修改请求头**：

- **header_up**  设置、添加（使用 `+` 前缀）、删除（使用 `-` 前缀），或对发往后端的请求头执行替换操作（通过两个参数：搜索值和替换值）。

- **header_down**  设置、添加（使用 `+` 前缀）、删除（使用 `-` 前缀），或对来自后端的响应头执行替换（通过使用两个参数：搜索和替换）。

例如，要设置请求头并覆盖现有值：

```caddy-d
header_up Some-Header "the value"
```

要添加响应头；请注意，一个头字段可以包含多个值：

```caddy-d
header_down +Some-Header "first value"
header_down +Some-Header "second value"
```

要删除请求头，以防止其到达后端：

```caddy-d
header_up -Some-Header
```

要删除所有匹配的请求头，请使用后缀匹配：

```caddy-d
header_up -Some-*
```

要删除所有请求头，以便能够单独添加所需的请求头（不建议这样做）：

```caddy-d
header_up -*
```

要在请求头中执行正则表达式替换：

```caddy-d
header_up Some-Header "^prefix-([A-Za-z0-9]*)$" "replaced-$1-suffix"
```

所使用的正则表达式语言是 RE2，Go 语言中已包含该语言。请参阅 [RE2 语法参考](https://github.com/google/re2/wiki/Syntax)和 [Go 正则表达式语法概述](https://pkg.go.dev/regexp/syntax)。替换字符串会进行[展开](https://pkg.go.dev/regexp#Regexp.Expand)，从而允许使用捕获的值，例如 `$1` 表示第一个捕获组。



### 默认设置

默认情况下，Caddy 会将传入的头部信息（包括 `Host`——原样传递给后端，但有三种例外情况：

- 它用于设置或扩展[`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For)标头字段。
- 它设置了[`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto)标头字段。
- 它设置了[`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host)标头字段。

 对于这些 `X-Forwarded-*` 标头，默认情况下，代理会忽略来自传入请求的这些值，以防止欺骗。

如果 Caddy 不是客户端连接到的第一个服务器（例如，当 CDN 位于 Caddy 之前时），您可以配置 `trusted_proxies` 一组 IP 范围（CIDR）列表，来自这些范围的传入请求被视为已正确设置了这些标头的值。

强烈建议您通过[全局选项 `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) 进行配置，而非在代理中配置，这样该设置将适用于服务器中的所有代理处理程序，并且还能启用客户端 IP 解析功能。

<aside class="tip">

如果您在 Caddy 前端使用了 Cloudflare，请注意，您可能面临 `X-Forwarded-For` 。我们的合作伙伴 [Authelia](https://www.authelia.com) 已记录了一种[解决方法](https://www.authelia.com/integration/proxies/forwarded-headers/)，可用于配置 Cloudflare 忽略此标头的传入值。

</aside>

此外，在使用 [`http` 传输](#the-http-transport)协议时， `Accept-Encoding: gzip` 如果客户端请求中缺少该标头，则会自动设置该标头。这使得上游服务器在条件允许时能够提供压缩内容。通过在传输层设置[`compression off`](#compression)，可以禁用此行为。



### HTTPS

由于（大多数）标头在代理过程中会保留其原始值，因此在代理到 HTTPS 时，通常需要覆盖 `Host` 标头，将其替换为配置的上游地址，从而确保 `Host` 标头与 TLS ServerName 的值相匹配：

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

从 Caddy v2.11.0 开始，此操作已自动完成，因此在代理到 HTTPS 时，不再需要显式覆盖 `Host` 。若希望禁用此行为，可将 `Host` 标头设置为原始值（但这样做通常没有意义）：

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

该 `X-Forwarded-Host` 该标头[默认](#defaults)仍会被传递，因此上游服务若需了解原始 `Host` 标头值。

当在 Caddy 中终止 TLS 并通过 HTTP 进行代理时（无论是代理到端口还是 Unix 套接字），情况也是如此。事实上，当 Caddy 本身是目标时，它必须接收正确的 Host 字段 `reverse_proxy`。在 Unix 套接字的情况下， `upstream_hostport` 将表示套接字路径，且必须显式设置 Host。



<a id="rewrites"></a>
## 改写

默认情况下，Caddy 会使用与传入请求相同的 HTTP 方法和 URI 来执行上游请求，除非在请求到达之前，中间件链中已执行重写。 `reverse_proxy`.

在通过代理处理之前，会先克隆该请求；这样可以确保在处理程序中对请求所做的任何修改都不会影响其他处理程序。当需要在代理处理之后继续进行处理时，此机制非常有用。

除了对[请求头进行操作](#headers)外，在将请求发送给上游服务器之前，还可以修改请求的方法和 URI：

- **method**  用于更改克隆请求的 HTTP 方法。如果将方法更改为 `GET` 或 `HEAD`，则该处理程序将*不会*将传入请求的正文发送给上游。若您希望让另一个处理程序处理该请求正文，此功能将非常有用。
- **rewrite**  会更改克隆请求的 URI（路径和查询字符串）。这与 [`rewrite` 指令](/docs/caddyfile/directives/rewrite)类似，不同之处在于它不会将重写规则保留到该处理程序的作用域之外。

此类重写通常适用于“预检请求”这类场景，即向另一台服务器发送请求，以协助决定如何继续处理当前请求。

例如，该请求可以被发送到身份验证网关，由其判断该请求是否来自经过身份验证的用户（例如，请求中包含会话 Cookie），从而决定是继续处理该请求，还是将其重定向到登录页面。针对这种模式，Caddy 提供了一个快捷指令 [`forward_auth`](/docs/caddyfile/directives/forward_auth)，用于跳过大部分冗余的配置代码。




<a id="transports"></a>
## 运输

Caddy 的代理 **传输** 支持插件：

- **transport**  定义了与后端的通信方式。默认值为 `http`.


<a id="the-http-transport"></a>
### `http` 传输

```caddy-d
transport http {
	read_buffer             <size>
	write_buffer            <size>
	max_response_header     <size>
	proxy_protocol          v1|v2
	dial_timeout            <duration>
	dial_fallback_delay     <duration>
	response_header_timeout <duration>
	expect_continue_timeout <duration>
	resolvers <ip...>
	tls
	tls_client_auth <automate_name> | <cert_file> <key_file>
	tls_insecure_skip_verify
	tls_curves <curves...>
	tls_timeout <duration>
	tls_trust_pool <module>
	tls_server_name <server_name>
	tls_renegotiation <level>
	tls_except_ports <ports...>
	keepalive [off|<duration>]
	keepalive_interval <interval>
	keepalive_idle_conns <max_count>
	keepalive_idle_conns_per_host <count>
	versions <versions...>
	compression off
	max_conns_per_host <count>
	network_proxy <module>
}
```

- **read_buffer**  表示读取缓冲区的大小（单位为字节）。它支持 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支持的所有格式。默认值： `4KiB`.

- **write_buffer**  表示写缓冲区的大小（单位为字节）。它支持 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支持的所有格式。默认值： `4KiB`.

- **max_response_header**  表示从响应头中读取的最大字节数。它支持 [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go) 支持的所有格式。默认值： `10MiB`.

- **proxy_protocol**  在与上游服务器的连接中启用 [PROXY 协议](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt)（由 HAProxy 推广），并在请求前添加真实的客户端 IP 数据。如果 Caddy 位于另一个代理之后，建议配合使用[全局选项 ](/docs/caddyfile/options#trusted-proxies)[`servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies)。支持 `v1` 和 `v2`。仅当您确定上游服务器能够解析 PROXY 协议时才应使用此功能。默认情况下，此功能处于禁用状态。

- **dial_timeout**  是连接上游套接字时的最大等待[时长](/docs/conventions#durations)。默认值： `3s`.

- **dial_fallback_delay**  是建立 RFC 6555 快速回退连接前的最大等待[时长](/docs/conventions#durations)。负值将禁用此功能。默认值： `300ms`.

- **response_header_timeout**  是等待从上游读取响应头信息的最大[时长](/docs/conventions#durations)。默认值：无超时。

- **expect_continue_timeout**  是请求包含该标头时，在请求头写入完成后等待上游服务器返回首个响应头所允许的最长[时长](/docs/conventions#durations) `Expect: 100-continue`。默认：无超时。

- **read_timeout**  是等待后端进行下一次读取的最长[时长](/docs/conventions#durations)。默认值：无超时。

- **write_timeout**  是等待向后端进行下一次写入操作的最长[时长](/docs/conventions#durations)。默认值：无超时。

- **解析器**  是一组用于覆盖系统解析器的 DNS 解析器列表。

- **tls**  与后端使用 HTTPS 通信。如果您使用 `https://` 方案指定后端，或者配置了以下任何 `tls_*` 选项中的任意一项。

- **tls_client_auth**  通过以下两种方式之一启用 TLS 客户端身份验证：(1) 指定一个域名，Caddy 将为此域名获取证书并保持其有效；或 (2) 指定一个证书和密钥文件，用于向后端提供 TLS 客户端身份验证。

- **tls_insecure_skip_verify**  会关闭 TLS 握手验证，导致连接不安全，并容易受到中间人攻击。*请勿在生产环境中使用。*

- **tls_curves**  是一个用于上游连接的椭圆曲线列表。Caddy 的默认设置既现代又安全，因此您只需在有特殊需求时才需要配置此项。

- **tls_timeout**  是等待 TLS 握手完成的最长[时长](/docs/conventions#durations)。默认值：无超时。

- **tls_trust_pool**  用于配置受信任的证书颁发机构来源，其作用类似于 `tls` 指令文档中所述的 `trust_pool` 子指令。标准 Caddy 安装中可用的信任池来源列表可[在此处](/docs/caddyfile/directives/tls#trust-pool-providers)查看。

- **tls_server_name**  用于设置在验证 TLS 握手过程中接收到的证书时所使用的服务器名称。默认情况下，该字段将使用上游地址的主机部分。

  只有当您的上游地址与上游服务器可能使用的证书不匹配时，才需要重写此设置。例如，如果上游地址是一个 IP 地址，则您需要将其配置为上游服务器所提供的主机名。

  可以使用请求占位符，在这种情况下，每次请求都会使用 HTTP 传输配置的副本，这可能会导致性能下降。

- **tls_renegotiation**  用于设置 TLS 重协商级别。TLS 重协商是指在首次握手之后再次进行握手操作。该级别可以是以下选项之一：
  - `never` （默认）禁用重新协商。
  - `once` 允许远程服务器在每次连接中请求一次重新协商。
  - `freely` 允许远程服务器反复请求重新协商。

- **tls_except_ports**  当启用 TLS 时，如果上游目标使用给定端口中的某个端口，则这些连接的 TLS 将被禁用。在配置动态上游时，这可能很有用，因为有些上游期望接收 HTTP 请求，而另一些则期望接收 HTTPS 请求。

- **keepalive**  可以是 `off` 或一个[时长值](/docs/conventions#durations)，用于指定保持连接打开的时间（超时）。默认值： `2m`.

  ⚠️ 如果 keepalive 时长超过上游服务器的 keepalive 超时设置，发往 HTTP/1.1 上游服务器的请求可能会因“连接被对端重置”错误而失败。对于幂等请求，Go 的 HTTP 传输层会自动重试；但在其他情况下，Caddy 将返回 502 状态码。

- **keepalive_interval**  是两次存活探测之间的间隔[时间](/docs/conventions#durations)。默认值： `30s`.

- **keepalive_idle_conns**  定义了要保持活动的最大连接数。默认值：无限制。

- **keepalive_idle_conns_per_host**  若非零值，则控制每个主机上保留的最大空闲（保持活动）连接数。默认值： `32`.

- **版本**  允许自定义支持的 HTTP 版本。
  
  有效的选项包括： `1.1`, `2`, `h2c`, `3`.

  默认： `1.1 2`，或者如果[上游的方案](#upstream-addresses)是 `h2c://`，则默认值为 `h2c 2`.

  `h2c` 启用与上游服务器之间的明文 HTTP/2 连接。这是一项非标准功能，不使用 Go 的默认 HTTP 传输协议，因此与其他功能互斥。

  `3` 启用与上游服务器的 HTTP/3 连接。⚠️ 此为实验性功能，可能会有变动。

- **压缩**  可通过将其设置为 `off` 来禁用对后端的压缩。

- **max_conns_per_host**  可选地限制每个主机的总连接数，包括处于拨号、活动和空闲状态的连接。默认：无限制。

- **network_proxy**  指定用于向上游服务器发送请求的网络代理模块名称。如果未显式配置，Caddy 将遵循 [Go 标准库](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment)的规范，使用通过环境变量配置的代理，即 `HTTP_PROXY`, `HTTPS_PROXY`，以及 `NO_PROXY`。当为该参数提供值时，请求将按以下顺序流经反向代理：客户端（用户）→ `reverse_proxy` → `network_proxy` → 上游服务器。内置模块包括：
	- `none`，用于忽略 `HTTP_PROXY`, `HTTPS_PROXY`，以及 `NO_PROXY`.
	- `url <url>`，用于指定一个单一的 URL 以覆盖环境配置。

<a id="the-fastcgi-transport"></a>
### `fastcgi` 传输

```caddy-d
transport fastcgi {
	root  <path>
	split <at>
	env   <key> <value>
	resolve_root_symlink
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>
	capture_stderr
}
```

- **root**  是网站的根目录。默认值： `{http.vars.root}` 或当前工作目录。

- **split**  是用于分割路径的位置，以便在 URI 末尾获取 PATH_INFO。

- **env**  将指定值设置为额外的环境变量。可多次指定以设置多个环境变量。

- **resolve_root_symlink**  启用通过解析符号链接（若存在）将 `root` 目录解析为实际值，方法是评估符号链接（如果存在的话）。

- **dial_timeout**  表示连接上游套接字时等待的时间长度。接受[时长值](/docs/conventions#durations)。默认值： `3s`.

- **read_timeout**  表示从 FastCGI 服务器读取数据时等待的时间长度。接受[时间值](/docs/conventions#durations)。默认：无超时。

- **write_timeout**  表示向 FastCGI 服务器发送数据时等待的时间长度。支持[时间值](/docs/conventions#durations)。默认：不超时。

- **capture_stderr**  用于捕获并记录上游 FastCGI 服务器发送的任何消息 `stderr`。日志记录默认在 `WARN` 级别。如果响应包含 `4xx` 或 `5xx` 状态，则将改用 `ERROR` 级别。默认情况下， `stderr` 将被忽略。

<aside class="tip">

如果您想托管一个现代 PHP 应用程序，您可能正在寻找 [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi) 指令，它是一个使用 `fastcgi` 指令的快捷方式，并包含将 `index.php` 用作路由入口点所需的重写规则。

</aside>



<a id="intercepting-responses"></a>
## 拦截响应

可以配置反向代理以拦截来自后端的响应。为此，可以定义[响应匹配器](/docs/caddyfile/response-matchers)（语法与请求匹配器类似），然后执行第一个匹配的 `handle_response` 路由。

当响应处理程序被调用时，来自后端的响应不会写入客户端，而是会执行配置的 `handle_response` 路由，由该路由负责写入响应。如果该路由未写入响应，则请求处理将按[顺序](/docs/caddyfile/directives#directive-order)继续执行该 `reverse_proxy` 之后的处理程序。

- **@name** 是[响应](/docs/caddyfile/response-matchers)匹配器的名称。只要每个响应匹配器都有一个唯一的名称，就可以定义多个匹配器。可以通过状态码以及响应头是否存在或其值来匹配响应。

- **replace_status**  仅在匹配到指定的匹配器时，更改响应的状态码。

- **handle_response**  定义了当与给定的匹配器匹配时（或如果省略了匹配器，则为所有响应）应执行的路由。将应用第一个匹配的代码块。在 `handle_response` 块内，可以使用任何其他[指令](/docs/caddyfile/directives)。

此外，在 `handle_response`，可以使用两个特殊的处理程序指令：

- **copy_response**  将从后端接收到的响应正文复制回客户端。可选地，允许在此过程中更改响应的状态码。该指令的[执行顺序](/docs/caddyfile/directives#directive-order)应[位于`respond`之前](/docs/caddyfile/directives#directive-order)。

- **copy_response_headers**  将后端响应头复制到客户端，可选择性地包含或排除一组响应头字段（不可同时指定两者 `include` 和 `exclude`）。该指令的[执行顺序](/docs/caddyfile/directives#directive-order)位于[`header`之后](/docs/caddyfile/directives#directive-order)。

在 `handle_response` 路由中：

- `{rp.status_code}` 后端响应的状态码。

- `{rp.status_text}` 后端响应中的状态文本。

- `{rp.header.*}` 后端响应中的头部信息。

虽然反向代理响应处理程序可以将从代理接收到的新响应复制回客户端，但它无法将该新响应传递给后续的反向代理。每次调用 `reverse_proxy` 都会接收来自原始请求的正文（或经其他模块修改后的正文）。




<a id="examples"></a>
## 示例

将所有请求反向代理到本地后端：

```caddy
example.com {
	reverse_proxy localhost:9005
}
```


[在 3 个后端之间对](#upstreams)所有请求[进行负载均衡](#load-balancing)：

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```


同上，但仅限 `/api`，并通过[`cookie`策略](#lb_policy)实现粘性分发：

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```


使用[主动健康检查](#active-health-checks)来确定哪些后端处于正常状态，并在连接失败时启用[重试](#lb_try_duration)，将请求保留直至找到正常的后端：

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```


配置一些[传输选项](#transports)：

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```


反向代理到 [HTTPS 上游](#https)服务器（自 v2.11.0 起，Caddy 会自动将 `Host` 头部以匹配上游的主机，因此不再需要手动设置）：

```caddy
example.com {
	reverse_proxy https://example.com
}
```


将反向代理指向 HTTPS 上游服务器，但 [⚠️ 请禁用 TLS 验证](#tls_insecure_skip_verify)。不建议这样做，因为这会禁用 HTTPS 提供的所有安全检查；如果可能，建议在私有网络中通过 HTTP 进行代理，这样可以避免产生虚假的安全感：

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```


相反，您可以通过显式[信任上游服务器的证书](#tls_trust_pool)来与上游建立信任关系，并（可选）将 TLS-SNI 设置为与上游证书中的主机名匹配：

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /path/to/cert.pem
			tls_server_name app.example.com
		}
	}
}
```



在进行代理之前，[应去除路径前缀](handle_path)；但需注意<a href="https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575">子文件夹的问题 <img src="/old/resources/images/external-link.svg" class="external-link"></a>：

```caddy
example.com {
	handle_path /prefix/* {
		reverse_proxy localhost:9000
	}
}
```


在代理之前替换路径前缀，使用[`rewrite`](/docs/caddyfile/directives/rewrite)：

```caddy
example.com {
	handle_path /old-prefix/* {
		rewrite /new-prefix{path}
		reverse_proxy localhost:9000
	}
}
```


`X-Accel-Redirect` 通过[拦截响应](#intercepting-responses)来提供支持，即按请求提供静态文件：

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {rp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```


通过[拦截](#intercepting-responses)特定状态码的[错误响应](#intercepting-responses)，为上游产生的错误设置自定义错误页面：

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root /path/to/error/pages
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```


从 [`A` / `AAAA` 记录的](#aaaaa) DNS 查询中[动态](#dynamic-upstreams)获取后端：

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```


通过 [`SRV` 记录的](#srv) DNS 查询[动态](#dynamic-upstreams)获取后端：

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```


使用[主动健康检查](#active-health-checks)以及 `health_upstream` 在创建中间服务以进行更全面的健康检查时，这会很有帮助。 `{http.reverse_proxy.active.target_upstream}` 随后可将其作为请求头，向健康检查服务提供原始上游服务的信息。

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
