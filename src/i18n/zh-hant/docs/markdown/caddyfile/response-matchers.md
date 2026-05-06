---
title: Response matcher (Caddyfile)
---

<script>
ready(function() {
	// Response matchers
	$$_('pre.chroma .nd').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#syntax" style="color: inherit;">${text}</a>`;
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="#status" style="color: inherit;">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="#header" style="color: inherit;">header</a>';
		}
	});

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

<a id="response-matchers"></a>
# Response matcher

**Response matcher** 可以根據特定標準來過濾（或分類）回應。

這些通常僅作為某些其他指令內部的設定出現，以便在回應正被寫出到客戶端時做出決策。

- [Syntax](#syntax)
- [Matcher](#matchers)
	- [status](#status)
	- [header](#header)

<a id="syntax"></a>
## Syntax

如果某個指令接受 Response matcher，則在語法文件中其用法表示為 `[<response_matcher>]` 或 `[<inline_response_matcher>]`。

- **<response_matcher>** 標記可以是先前宣告的具名 Response matcher 的名稱。例如：`@name`。
- **<inline_response_matcher>** 標記可以是回應標準本身，不需要事先宣告。例如：`status 200`。

<a id="named"></a>
### Named

```caddy-d
@name {
	status <code...>
	header <field> [<value>]
}
```
如果只有回應的一個面向與該指令相關，您可以將名稱和標準放在同一行：

```caddy-d
@name status <code...>
```

<a id="inline"></a>
### Inline

```caddy-d
... {
	status <code...>
	header <field> [<value>]
}
```
```caddy-d
... status <code...>
```
```caddy-d
... header <field> [<value>]
```

<a id="matchers"></a>
## Matcher

<a id="status"></a>
### status

```caddy-d
status <code...>
```

根據 HTTP 狀態碼。

- **&lt;code...&gt;** 是 HTTP 狀態碼清單。特殊情況是像 `2xx` 和 `3xx` 這樣的字串，它們分別比對 `200`-`299` 和 `300`-`399` 範圍內的所有狀態碼。

<a id="example"></a>
#### 範例：

```caddy-d
@success status 2xx
```



<a id="header"></a>
### header

```caddy-d
header <field> [<value>]
```

根據回應標頭欄位。

- `<field>` 是要檢查的 HTTP 標頭欄位名稱。
	- 如果前綴為 `!`，則該欄位必須不存在才能比對（省略值參數）。
- `<value>` 是該欄位必須具備的值才能比對。
	- 如果前綴為 `*`，它將執行快速後綴比對（出現在末尾）。
	- 如果後綴為 `*`，它將執行快速前綴比對（出現在開頭）。
	- 如果被 `*` 包圍，它將執行快速子字串比對（出現在任何位置）。
	- 否則，它是快速精確比對。

同一組中的不同標頭欄位之間是「且」(AND) 關係。每個欄位的多個值之間是「或」(OR) 關係。

請注意，標頭欄位可能會重複並具有不同的值。後端應用程式「必須」考慮到標頭欄位值是陣列，而不是單一值，且 Caddy 不會解釋此類困境中的含義。

<a id="example-1"></a>
#### 範例：

比對 `Foo` 標頭包含 `bar` 值的回應：

```caddy-d
@upgrade header Foo *bar*
```

比對 `Foo` 標頭具有 `bar` 或 `baz` 值的回應：

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

比對完全不具備 `Foo` 標頭欄位的回應：

```caddy-d
@not_foo header !Foo
```
