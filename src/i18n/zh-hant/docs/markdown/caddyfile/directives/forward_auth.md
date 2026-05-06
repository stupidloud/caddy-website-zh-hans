---
title: forward_auth (Caddyfile 指令)
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

<a id="forward-auth"></a>
# forward_auth

一個固執的指令，它將請求的克隆代理到身份驗證網關 (authentication gateway)，該網關可以決定是否應繼續處理，或者需要發送到登錄頁面。

- [語法](#syntax)
- [展開形式](#expanded-form)
- [範例](#examples)
  - [Authelia](#authelia)
  - [Tailscale](#tailscale)

Caddy 的 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) 能夠向外部服務執行「預檢請求」，但此指令是專門為身份驗證用例量身定制的。這個指令實際上只是使用更長、更常見配置（如下所示）的一種便捷方式。

此指令向配置的 upstream 發送 `GET` 請求，並重寫 `uri`：
- 如果 upstream 以 `2xx` 狀態碼響應，則授予訪問權限，並將 `copy_headers` 中的標頭欄位複製到原始請求中，然後繼續處理。
- 否則，如果 upstream 以任何其他狀態碼響應，則將 upstream 的響應複製回客戶端。此響應通常應涉及重定向到身份驗證網關的登錄頁面。

如果此行為不完全是您想要的，您可以將下面的 [展開形式](#expanded-form) 作為基礎，並根據您的需求進行自定義。

支持 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) 的所有子指令，並傳遞到基礎的 `reverse_proxy` handler。


<a id="syntax"></a>
## 語法

```caddy-d
forward_auth [<matcher>] [<upstreams...>] {
	uri          <to>
	copy_headers <fields...> {
		<fields...>
	}
}
```

- **&lt;upstreams...&gt;** 是一組發送身份驗證請求的 upstream（後端）列表。

- **uri** 是要在發送到 upstream 的請求上設置的 URI（路徑和查詢）。這通常是身份驗證網關的驗證端點。

- **copy_headers** 是當請求具有成功狀態碼時，從響應複製到原始請求的 HTTP 標頭欄位列表。

  可以通過使用 `>` 後跟新名稱來重命名欄位，例如 `Before>After`。

  如果您為了可讀性而偏好，可以使用一個區塊來列出所有欄位，每行一個。

由於此指令是反向代理的一個固執封裝，您可以使用 [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#syntax) 的任何子指令來對其進行自定義。


<a id="expanded-form"></a>
## 展開形式

`forward_auth` 指令與以下配置相同。像 [Authelia](https://www.authelia.com/) 這樣的身份驗證網關與此預設配合良好。如果您的網關不是，請隨意參考此內容並根據需要進行自定義，而不是使用 `forward_auth` 快捷方式。

```caddy-d
reverse_proxy <upstreams...> {
	# 始終使用 GET，以便不消耗
	# 傳入請求的正文
	method GET

	# 將 URI 更改為身份驗證網關的
	# 驗證端點
	rewrite <to>

	# 轉發原始方法和 URI，
	# 因為它們在上面被重寫了；這
	# 是除了 reverse_proxy 已經設置的其他 X-Forwarded-*
	# 標頭之外的補充
	header_up X-Forwarded-Method {method}
	header_up X-Forwarded-Uri {uri}

	# 在響應成功時，複製響應標頭
	@good status 2xx
	handle_response @good {
		# 例如，對於每個 copy_headers 欄位...
		request_header Remote-User {rp.header.Remote-User}
		request_header Remote-Email {rp.header.Remote-Email}
	}
}
```


<a id="examples"></a>
## 範例


<a id="authelia"></a>
### Authelia

在通過反向代理提供應用程式服務之前，將身份驗證委派給 [Authelia](https://www.authelia.com/)：

```caddy
# 提供身份驗證網關本身
auth.example.com {
	reverse_proxy authelia:9091
}

# 提供您的應用程式
app1.example.com {
	forward_auth authelia:9091 {
		uri /api/authz/forward-auth
		copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
	}

	reverse_proxy app1:8080
}
```

有關更多資訊，請參閱 [Authelia 的文檔](https://www.authelia.com/integration/proxies/caddy/) 以與 Caddy 集成。


<a id="tailscale"></a>
### Tailscale

將身份驗證委派給 [Tailscale](https://tailscale.com/)（目前名為 [`nginx-auth`](https://tailscale.com/blog/tailscale-auth-nginx/)，但它仍然適用於 Caddy），並使用 `copy_headers` 的替代語法來 *重命名* 複製的標頭（請注意每個標頭中的 `>`）：

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
