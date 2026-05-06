---
title: uri (Caddyfile 指令)
---

# uri

操作請求的 URI。它可以移除路徑前綴/後綴，或者替換整個 URI 中的子字串。

此指令與 [`rewrite`](rewrite) 的不同之處在於 `uri` *差異化地* 更改 URI，而不是像 `rewrite` 那樣將其重置為完全不同的內容。雖然 `rewrite` 被視為內部重新導向的特殊處理，但 `uri` 只是另一個 middleware。

<a id="syntax"></a>
## 語法

支援多種不同的操作：

```caddy-d
uri [<matcher>] strip_prefix <target>
uri [<matcher>] strip_suffix <target>
uri [<matcher>] replace      <target> <replacement> [<limit>]
uri [<matcher>] path_regexp  <target> <replacement>
uri [<matcher>] query        [-|+]<param> [<value>]
uri [<matcher>] query {
	<param> [<value>] [<replacement>]
	...
}
```

第一個（非 matcher）參數指定操作：

- **strip_prefix** 從路徑中移除前綴。

- **strip_suffix** 從路徑中移除後綴。

- **replace** 在整個 URI 中執行子字串替換。

	- **&lt;target&gt;** 是前綴、後綴，或是搜尋字串/正規表示式。如果是前綴，可以省略開頭的正斜線，因為路徑始終以正斜線開頭。

	- **&lt;replacement&gt;** 是替換字串。支援使用 `$name` 或 `${name}` 語法，或是使用索引數字（如 `$1`）來使用擷取群組。詳細資訊請參閱 [Go 文件](https://golang.org/pkg/regexp/#Regexp.Expand)。如果替換值是 `""`，則匹配的文字將從值中移除。

	- **&lt;limit&gt;** 是選用的，用於限制最大替換次數。

- **path_regexp** 在 URI 的路徑部分執行正規表示式替換。

	- **&lt;target&gt;** 是前綴、後綴，或是搜尋字串/正規表示式。如果是前綴，可以省略開頭的正斜線，因為路徑始終以正斜線開頭。

	- **&lt;replacement&gt;** 是替換字串。支援使用 `$name` 或 `${name}` 語法，或是使用索引數字（如 `$1`）來使用擷取群組。詳細資訊請參閱 [Go 文件](https://golang.org/pkg/regexp/#Regexp.Expand)。如果替換值是 `""`，則匹配的文字將從值中移除。

- **query** 對 URI 查詢參數進行操作，模式取決於參數名稱的前綴或參數的數量。可以使用區塊來一次指定多個操作，並按此順序分組執行：rename 🡒 set 🡒 append 🡒 replace 🡒 delete。

	- 如果沒有前綴，則在查詢中設置給定值的參數。
	
	  例如，`uri query foo bar` 將 `foo` 參數的值設置為 `bar`。

	- 前綴帶 `-` 表示從查詢中移除該參數。
	
	  例如，`uri query -foo` 將從查詢中刪除 `foo` 參數。

	- 前綴帶 `+` 表示向查詢中追加一個參數，並賦予給定值。這 *不會* 覆蓋現有的同名參數（省略 `+` 則會覆蓋）。
	
	  例如，`uri query +foo bar` 將向查詢追加 `foo=bar`。

	- 中間帶有 `>` 的參數名會將參數重新命名為 `>` 之後的值。
	
	  例如，`uri query foo>bar` 會將 `foo` 參數重新命名為 `bar`。

	- 如果有三個參數，則執行查詢值的正規表示式替換，其中第一個參數是查詢參數名，第二個是搜尋值，第三個是替換值。第一個參數（參數名）可以是 `*`，以便對所有查詢參數執行替換。
	
	  支援使用 `$name` 或 `${name}` 語法，或是使用索引數字（如 `$1`）來使用擷取群組。詳細資訊請參閱 [Go 文件](https://golang.org/pkg/regexp/#Regexp.Expand)。如果替換值是 `""`，則匹配的文字將從值中移除。
	
	  例如，`uri query foo ^(ba)r $1z` 會替換 `foo` 參數的值，如果值以 `bar` 開頭，則結果值變為 `baz`。

URI 變更發生在規範化或未轉義形式的 URI 上。但是，在路徑前綴或後綴模式中可以使用轉義序列，以僅匹配請求路徑中對應位置的那些字面轉義。例如，`uri strip_prefix /a/b` 會將 `/a/b/c` 和 `/a%2Fb/c` 都重寫為 `/c`；而 `uri strip_prefix /a%2Fb` 則會將 `/a%2Fb/c` 重寫為 `/c`，但不會匹配 `/a/b/c`。

在修改之前，URI 路徑會清除目錄遍歷點。此外，除非 `<target>` 也包含多個斜線，否則多個斜線（如 `//`）會被合併。

<a id="similar-directives"></a>
## 類似的指令

其他一些指令也可以操作請求 URI。

- [`rewrite`](rewrite) 更改整個路徑和查詢為新值，而不是部分更改。

- [`handle_path`](handle_path) 與 [`handle`](handle) 作用相同，但在運行其 handler 之前會從請求中剝離前綴。在許多情況下可以用它來代替 `uri strip_prefix`，從而減少一行配置。


<a id="examples"></a>
## 範例

從所有請求路徑的開頭移除 `/api`：

```caddy-d
uri strip_prefix /api
```

從所有請求路徑的末尾移除 `.php`：

```caddy-d
uri strip_suffix .php
```

在任何請求 URI 中將 "/docs/" 替換為 "/v1/docs/"：

```caddy-d
uri replace /docs/ /v1/docs/
```

將請求路徑中所有重複的斜線（但不包括請求查詢部分）合併為單個斜線：

```caddy-d
uri path_regexp /{2,} /
```

將 `foo` 查詢參數的值設置為 `bar`：

```caddy-d
uri query foo bar
```

從查詢中移除 `foo` 參數：

```caddy-d
uri query -foo
```

將 `foo` 查詢參數重新命名為 `bar`：

```caddy-d
uri query foo>bar
```

向查詢中追加 `bar` 參數：

```caddy-d
uri query +foo bar
```

將 `foo` 查詢參數中以 `bar` 開頭的值替換為 `baz`：

```caddy-d
uri query foo ^(ba)r $1z
```

一次執行多個查詢操作：

```caddy-d
uri query {
	+foo bar
	-baz
	qux test
	renamethis>renamed
}
```
