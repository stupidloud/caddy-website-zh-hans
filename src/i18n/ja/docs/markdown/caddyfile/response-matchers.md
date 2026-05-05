---
title: "Response matchers (Caddyfile)"
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
# Response Matchers

**Response matchers** は、特定の条件でレスポンスを絞り込む（または分類する）ために使えます。

通常は、クライアントへレスポンスを書き出している最中に判断を行うため、特定の他のディレクティブ内の設定としてだけ現れます。

- [構文](#syntax)
- [Matchers](#matchers)
	- [status](#status)
	- [header](#header)

<a id="syntax"></a>
## 構文

ディレクティブが response matchers を受け付ける場合、構文ドキュメントでは `[<response_matcher>]` または `[<inline_response_matcher>]` として表されます。

- **<response_matcher>** token は、以前に宣言された named response matcher の名前です。例: `@name`。
- **<inline_response_matcher>** token は、事前宣言なしで直接書くレスポンス条件です。例: `status 200`。

<a id="named"></a>
### Named

```caddy-d
@name {
	status <code...>
	header <field> [<value>]
}
```
レスポンスの 1 つの側面だけがディレクティブに関係する場合は、名前と条件を同じ行に書けます。

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
## Matchers

<a id="status"></a>
### status

```caddy-d
status <code...>
```

HTTP status code で match します。

- **&lt;code...&gt;** は HTTP status code のリストです。特殊なケースとして `2xx` や `3xx` のような文字列があり、それぞれ `200`-`299`、`300`-`399` の範囲にあるすべての status code に match します。

#### 例:

```caddy-d
@success status 2xx
```



<a id="header"></a>
### header

```caddy-d
header <field> [<value>]
```

レスポンス header field で match します。

- `<field>` は確認する HTTP header field の名前です。
	- 先頭に `!` を付けた場合、その field が存在しないことが match 条件になります（value 引数は省略します）。
- `<value>` は match に必要な field の値です。
	- 先頭に `*` を付けると、高速な suffix match（末尾に現れる）を行います。
	- 末尾に `*` を付けると、高速な prefix match（先頭に現れる）を行います。
	- `*` で囲むと、高速な substring match（任意の位置に現れる）を行います。
	- それ以外の場合は、高速な exact match です。

同じ set 内の異なる header field は AND で結合されます。field ごとの複数 value は OR で結合されます。

header field は繰り返し出現し、異なる値を持つことがある点に注意してください。Backend アプリケーションは、header field の値が単一値ではなく配列であることを必ず考慮しなければなりません。Caddy はそのような曖昧な状況の意味を解釈しません。

#### 例:

`Foo` header に値 `bar` を含むレスポンスに match します。

```caddy-d
@upgrade header Foo *bar*
```

`Foo` header の値が `bar` または `baz` であるレスポンスに match します。

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

`Foo` header field をまったく持たないレスポンスに match します。

```caddy-d
@not_foo header !Foo
```
