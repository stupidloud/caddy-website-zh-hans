---
title: "handle_path（Caddyfile 指令）"
---

<script>
ready(function() {
	// Add a link to [<path_matcher>] as a special case for this directive.
	// The matcher text includes <> characters which are parsed as HTML,
	// so we must use text() to change the link text.
	$$_('pre.chroma .s').forEach(item => {
		if (item.innerText.includes('<path_matcher>')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			item.innerHTML = `<a href="/docs/caddyfile/matchers#path-matchers" style="color: inherit;" title="Matcher token">${text}</a>`;
			item.classList.remove('s');
			item.classList.add('nd');
		}
	});
});
</script>

# handle_path

其工作原理与[`handle`指令](handle)相同，但会隐式使用[`uri strip_prefix`](uri)来移除匹配到的路径前缀。

处理与特定路径匹配的请求（同时从请求 URI 中移除该路径）是一种相当常见的用例，因此为了方便起见，为此专门提供了一个指令。


## 语法

```caddy-d
handle_path <path_matcher> {
	<directives...>
}
```

- **<directives...>** 是一组 HTTP 处理程序指令或指令块，每行一个，其格式与 `handle_path` 块之外的情况一样。

仅接受且必须使用一个[路径匹配器](/docs/caddyfile/matchers#path-matchers)；您不能在 `handle_path`.

## 示例

此配置：

```caddy-d
handle_path /prefix/* {
	...
}
```

👆 实际上与这个 👇 相同，但 `handle_path` 👆这种形式则稍显简洁

```caddy-d
handle /prefix/* {
	uri strip_prefix /prefix
	...
}
```

一个完整的 Caddyfile 示例，其中 `handle_path` 和 `handle` 是互斥的；但请注意<a href="https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575">子文件夹问题 <img src="/old/resources/images/external-link.svg" class="external-link"></a>

```caddy
example.com {
	# 提供 API 服务，并去掉 /api 前缀
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# 提供静态站点服务
	handle {
		root /srv
		file_server
	}
}
```
