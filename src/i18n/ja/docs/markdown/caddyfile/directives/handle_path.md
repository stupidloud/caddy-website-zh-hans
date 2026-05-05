---
title: handle_path (Caddyfile directive)
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

[`handle` directive](handle) と同じように動作しますが、一致した path prefix を strip するために暗黙的に [`uri strip_prefix`](uri) を使います。

特定の path に一致するリクエストを処理しながら、その path を request URI から strip することは十分によくあるユースケースなので、利便性のために専用の directive があります。


<a id="syntax"></a>
## 構文

```caddy-d
handle_path <path_matcher> {
	<directives...>
}
```

- **<directives...>** は HTTP handler directive または directive block のリストです。`handle_path` block の外で使う場合と同じく、1 行に 1 つずつ書きます。

受け付けるのは単一の [path matcher](/docs/caddyfile/matchers#path-matchers) のみで、必須です。`handle_path` では named matcher を使えません。

<a id="examples"></a>
## 例

この設定:

```caddy-d
handle_path /prefix/* {
	...
}
```

👆 は実質的に次と同じですが 👇、`handle_path` 形式 👆 の方が少し簡潔です。

```caddy-d
handle /prefix/* {
	uri strip_prefix /prefix
	...
}
```

`handle_path` と `handle` が相互排他的である完全な Caddyfile の例です。ただし、[subfolder problem <img src="/old/resources/images/external-link.svg" class="external-link">](https://caddy.community/t/the-subfolder-problem-or-why-cant-i-reverse-proxy-my-app-into-a-subfolder/8575) には注意してください。

```caddy
example.com {
	# /api prefix を strip して API を提供する
	handle_path /api/* {
		reverse_proxy localhost:9000
	}

	# 静的サイトを提供する
	handle {
		root /srv
		file_server
	}
}
```
