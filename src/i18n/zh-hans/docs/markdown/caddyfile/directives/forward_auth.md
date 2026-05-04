---
title: "forward_auth（Caddyfile 指令）"
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.innerText.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// Fix uri subdirective, gets parsed as matcher arg because of "uri" directive
	$$_('.k').forEach(item => {
		if (item.innerText.includes('uri') && item.nextElementSibling && item.nextElementSibling.classList.contains('nd')) {
			const next = item.nextElementSibling;
			next.classList.remove('nd');
			next.classList.add('s');
			next.textContent = next.textContent;
		}
	});
});
</script>

# forward_auth

一个具有特定行为的指令，它将请求的副本代理到身份验证网关，该网关可决定是否继续处理请求，或将其重定向至登录页面。

- [语法](#syntax)
- [展开形式](#expanded-form)
- [示例](#examples)
  - [奥塞莉亚](#authelia)
  - [Tailscale](#tailscale)

Caddy 的 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) 指令能够向外部服务发送“预检请求”，但该指令是专门为身份验证场景设计的。实际上，该指令只是为了方便使用下面这种更长、更常见的配置而提供的一种简便方式。

该指令会向 `GET` 向配置的上游服务器发送请求，并使用 `uri` rewritten:
- 如果上游服务器返回 `2xx` 状态码，则访问被允许，且 `copy_headers` 中的标头字段将复制到原始请求中，并继续处理。
- 否则，如果上游返回其他状态码，则将上游的响应原样转发给客户端。该响应通常应包含重定向至身份验证网关登录页面的操作。

如果这种行为并非您想要的，您可以以下面的[扩展形式](#expanded-form)为基础，根据需要进行自定义。

支持[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy)的所有子指令，并将它们传递给底层的 `reverse_proxy` 处理程序。


<a id="syntax"></a>
<span id="syntax"/>
## 语法

```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <to>
	copy_headers <fields...> {
		<fields...>
	}
}
```

- **&lt;upstreams...&gt;** 是要向其发送认证请求的上游（后端）列表。

- **uri** 是发送给上游请求中要设置的 URI（路径和查询字符串）。这通常是身份验证网关的验证端点。

- **copy_headers** 是一个 HTTP 头字段列表，用于在请求返回成功状态码时，将响应中的这些字段复制到原始请求中。

  可以通过使用 `>` 后跟新名称，例如 `Before>After`.

  为了便于阅读，您可以使用代码块将所有字段按每行一个的方式列出。

由于该指令是反向代理的一个具有特定实现方式的封装，您可以使用[`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax)中的任何子指令对其进行自定义。


<a id="expanded-form"></a>
<span id="expanded-form"/>
## 展开形式

该 `forward_auth` 指令与以下配置效果相同。[Authelia](https://www.authelia.com/) 等身份验证网关与此预设配合良好。如果您的网关无法正常工作，请随意参考此配置并根据需要进行自定义，而非使用 `forward_auth` 快捷方式。

```caddy-d
reverse_proxy <upstreams...> {
	# 始终使用 GET，避免消耗
	# 原始请求的请求体
	method GET

	# 将 URI 改写为认证网关的
	# 验证端点
	rewrite <to>

	# 转发原始方法和 URI（因为它们在上方被改写）；
	# 这是对 reverse_proxy 已设置的
	# 其他 X-Forwarded-* 头部的补充
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# 响应成功时，复制响应头部
	@good status 2xx
	handle_response @good {
		# 例如，对每个 copy_headers 字段执行……
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


<a id="examples"></a>
<span id="examples"/>
## 示例


<a id="authelia"></a>
<span id="authelia"/>
### 奥塞莉亚

在通过反向代理提供应用程序之前，将身份验证委托给 [Authelia](https://www.authelia.com/)：

```caddy
# 提供身份验证网关服务
auth.example.com {
	reverse_proxy authelia:9091
}

# 提供应用服务
app1.example.com {
	forward_auth authelia:9091 {
		uri /api/authz/forward-auth
		copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
	}

	reverse_proxy app1:8080
}
```

如需了解更多信息，请参阅 [Authelia](https://www.authelia.com/integration/proxies/caddy/) 关于与 Caddy 集成的[文档](https://www.authelia.com/integration/proxies/caddy/)。


<a id="tailscale"></a>
<span id="tailscale"/>
### Tailscale

将身份验证委托给 [Tailscale](https://tailscale.com/)（目前名为 [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/)，但仍可与 Caddy 配合使用），并使用替代语法来 `copy_headers` 来*重命名*复制的头部（请注意每个头部中的 `>` ）：

```caddy-d
forward_auth unix//run/tailscale.nginx-auth.sock {
	uri /auth
	header_up Remote-Addr {remote_host}
	header_up Remote-Port {remote_port}
	header_up Original-URI {uri}
	copy_headers {
		Tailscale-User>X-Webauth-User
		Tailscale-Name>X-Webauth-Name
		Tailscale-Login>X-Webauth-Login
		Tailscale-Tailnet>X-Webauth-Tailnet
		Tailscale-Profile-Picture>X-Webauth-Profile-Picture
	}
}
```
