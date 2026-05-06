---
title: handle_path (Caddyfile 指令)
---

<script>
ready(function() {
	// 為此指令添加 [<path_matcher>] 連結作為特殊情況。
	// matcher 文本包含被解析為 HTML 的 <> 字符，
	// 因此我們必須使用 text() 來更改連結文本。
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

<a id="handle-path"></a>
# handle_path

運作方式與 [`handle` 指令](handle) 相同，但會隱式使用 [`uri strip_prefix`](uri) 來剝離匹配的路徑前綴。

處理匹配特定路徑的請求（同時從請求 URI 中剝離該路徑）是一個非常常見的用例，因此為了方便起見，它有自己的指令。


<a id="syntax"></a>
## Syntax

```caddy-d
handle_path <path_matcher> {
	<directives...>
}
```

- **<directives...>** 是 HTTP 處理程序指令或指令塊的列表，每行一個，就像在 `handle_path` 塊之外使用一樣。

僅接受單個 [path matcher](/docs/caddyfile/matchers#path-matchers) 且是必填項；您不能在 `handle_path` 中使用命名的 matcher。

<a id="examples"></a>
## Examples

此配置：

```caddy-d
handle_path /prefix/* {
	...
}
```

👆 實際上與下面這個 👇 相同，但 `handle_path` 形式 👆 稍微簡潔一些

```caddy-d
handle /prefix/* {
	uri strip_prefix /prefix
	...
}
```

一個完整的 Caddyfile 示例，其中 `handle_path` 和 `handle` 是互斥的；但是，請注意 [子文件夾問題 <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575)

```caddy
example.com {
	# 提供您的 API，並剝離 /api 前綴
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# 提供您的靜態網站
	handle {
		root /srv
		file_server
	}
}
```
