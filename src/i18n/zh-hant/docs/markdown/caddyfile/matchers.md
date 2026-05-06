---
title: 請求 matcher (Caddyfile)
---

<script>
ready(function() {
	// We'll add links on the matchers in the code blocks
	// to their associated anchor tags.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Link matcher tokens based on their contents to the syntax section
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Matcher token">${text}</a>`;
	});
});
</script>

<a id="request-matchers"></a>
# 請求 matcher

**Request matcher** 可以用於根據各種標準過濾（或分類）請求。

- [語法](#syntax)
	- [範例](#examples)
	- [通配符 matcher](#wildcard-matchers)
	- [路徑 matcher](#path-matchers)
	- [命名 matcher](#named-matchers)
- [標準 matcher](#standard-matchers)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)


<a id="syntax"></a>
## 語法

在 Caddyfile 中，緊接在指令後的 **matcher token** 可以限制該指令的範圍。matcher token 可以是以下形式之一：

1. [**`*`**](#wildcard-matchers) 匹配所有請求（通配符；預設值）。
2. [**`/path`**](#path-matchers) 以正斜槓開頭以匹配請求路徑。
3. [**`@name`**](#named-matchers) 指定一個 *命名 matcher*。

如果一個指令支持 matcher，它將在語法文檔中顯示為 `[<matcher>]`。matcher token [通常是可選的](/docs/caddyfile/directives#syntax)，由 `[ ]` 表示。如果省略 matcher token，則與通配符 matcher (`*`) 相同。


<a id="examples"></a>
#### 範例

此指令適用於 [所有](#wildcard-matchers) HTTP 請求：

```caddy-d
reverse_proxy localhost:9000
```

這也是一樣的（這裡不需要 `*`）：

```caddy-d
reverse_proxy * localhost:9000
```

但此指令僅適用於 [路徑](#path-matchers) 以 `/api/` 開頭的請求：

```caddy-d
reverse_proxy /api/* localhost:9000
```

要匹配路徑以外的任何內容，請定義一個 [命名 matcher](#named-matchers) 並使用 `@name` 引用它：

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```




<a id="wildcard-matchers"></a>
### 通配符 matcher

通配符（或「全匹配」）matcher `*` 匹配所有請求，並且僅在需要 matcher token 時才需要。例如，如果您想給指令的第一個參數恰好也是一個路徑，它看起來就像一個路徑 matcher！因此您可以使用通配符 matcher 來消除歧義，例如：

```caddy-d
root * /home/www/mysite
```

否則，此 matcher 不常用。如果語法不需要，我們通常建議省略它。


<a id="path-matchers"></a>
### 路徑 matcher

按 URI 路徑匹配是匹配請求最常用的方式，因此 matcher 可以內聯，如下所示：

```caddy-d
redir /old.html /new.html
```

路徑 matcher token 必須以正斜槓 `/` 開頭。

**[路徑匹配](#path) 預設是精確匹配，而不是前綴匹配。** 您必須附加 `*` 以進行快速前綴匹配。請注意，`/foo*` 將匹配 `/foo` 和 `/foo/` 以及 `/foobar`；您實際上可能想要 `/foo/*`。


<a id="named-matchers"></a>
### 命名 matcher

所有非路徑或通配符 matcher 的 matcher 必須是命名 matcher。這是在任何特定指令之外定義的 matcher，可以重複使用。

定義一個具有唯一名稱的 matcher 可以為您提供更大的靈活性，允許您將 [任何可用的 matcher](#standard-matchers) 組合成一個集合：

```caddy-d
@name {
	...
}
```

或者，如果集合中只有一個 matcher，您可以將其放在同一行：

```caddy-d
@name ...
```

然後您可以像這樣使用 matcher，將其指定為指令的第一個參數：

```caddy-d
directive @name
```

例如，這將 HTTP/1.1 websocket 請求代理到 `localhost:6001`，將其他請求代理到 `localhost:8080`。它匹配具有名為 `Connection` 且 *包含* `Upgrade` 的標頭欄位的請求，**以及** 另一個名為 `Upgrade` 且精確為 `websocket` 的欄位：

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

如果 matcher 集合僅由一個 matcher 組成，則單行語法也適用：

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

作為一種特殊情況，[`expression` matcher](#expression) 可以在不指定其名稱的情況下使用，只要一個 [被引用](/docs/caddyfile/concepts#tokens-and-quotes) 的參數（CEL 表達式本身）緊跟在 matcher 名稱之後：

```caddy-d
@not-found `{err.status_code} == 404`
```

與指令一樣，命名 matcher 定義必須放在使用它們的 [site block](/docs/caddyfile/concepts#structure) 內。

命名 matcher 定義構成一個 *matcher set*。集合中的 matcher 是「與 (AND)」關係；即所有 matcher 都必須匹配。例如，如果您在集合中同時擁有 [`header`](#header) 和 [`path`](#path) matcher，則兩者都必須匹配。

相同類型的多個 matcher 可以使用布林代數 (AND/OR) 進行合併（例如同一個集合中的多個 [`path`](#path) matcher），如其下方相應章節所述。

對於更複雜的布林匹配邏輯，建議使用 [`expression` matcher](#expression) 編寫 CEL 表達式，它支持 **與 (and)** `&&`、**或 (or)** `||` 和 **括號** `( )`。





<a id="standard-matchers"></a>
## 標準 matcher

完整的 matcher 文檔可以在 [各自的 matcher 模組文檔中](/docs/json/apps/http/servers/routes/match/) 找到。

可以通過以下方式匹配請求：



<a id="client-ip"></a>
### client_ip

```caddy-d
client_ip <ranges...>

expression client_ip('<ranges...>')
```

按客戶端 IP 地址。接受精確的 IP 或 CIDR 範圍。支持 IPv6 區域。

當配置了 [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) 全域選項時，最好使用此 matcher，否則它的行為與 [`remote_ip`](#remote-ip) matcher 完全相同。只有來自受信任代理的請求才會在請求開始時解析其客戶端 IP；不受信任的請求將使用直接對等端的遠端 IP 地址或通過 [PROXY 協議](/docs/caddyfile/options#proxy-protocol) 設置的地址。

作為快捷方式，`private_ranges` 可用於匹配所有私有 IPv4 和 IPv6 範圍。這與指定所有這些範圍相同：`192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

每個命名 matcher 可以有多個 `client_ip` matcher，它們的範圍將被合併並進行「或 (OR)」運算。

#### 範例：

匹配來自私有 IPv4 地址的請求：

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

此 matcher 通常與 [`not`](#not) matcher 配合使用以反轉匹配。例如，要中止來自 *公共* IPv4 和 IPv6 地址的所有連接（這是所有私有範圍的反向）：

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

在 [CEL 表達式](#expression) 中，它看起來像這樣：

```caddy-d
@my-friends `client_ip('12.23.34.45', '23.34.45.56')`
```



<a id="expression"></a>
### expression

```caddy-d
expression <cel...>
```

通過任何返回 `true` 或 `false` 的 [CEL (Common Expression Language)](https://github.com/google/cel-spec) 表達式。

大多數其他請求 matcher 也可以在表達式中作為函數使用，這比外部表達式提供了更大的布林邏輯靈活性。有關 CEL 表達式中支持的語法，請參閱每個 matcher 的文檔。

Caddy [placeholder](/docs/conventions#placeholders)（或 [Caddyfile 簡寫](/docs/caddyfile/concepts#placeholders)）可以用在這些 CEL 表達式中，因為它們在被 CEL 環境解釋之前會被預處理並轉換為常規的 CEL 函數調用。如果 placeholder 應該作為字串參數傳遞給 matcher 函數，則開頭的 `{` 應該使用反斜槓 `\` 轉義，以便不被預處理，例如 `file('\{path}.md')`。

為了方便起見，如果定義的命名 matcher 僅由 CEL 表達式組成，則可以省略 matcher 名稱。CEL 表達式必須 [被引用](/docs/caddyfile/concepts#tokens-and-quotes)（建議使用反引號或 heredoc）。這讀起來非常不錯：

```caddy-d
@mutable `{method}.startsWith("P")`
```

在這種情況下，假定使用 CEL matcher。

#### 範例：

匹配方法以 `P` 開頭的請求，例如 `PUT` 或 `POST`：

```caddy-d
@methods expression {method}.startsWith("P")
```

匹配處理程序返回錯誤狀態碼 `404` 的請求，將與 [`handle_errors` 指令](/docs/caddyfile/directives/handle_errors) 結合使用：

```caddy-d
@404 expression {err.status_code} == 404
```

匹配路徑符合兩個不同正則表達式之一的請求；這只能使用表達式編寫，因為 [`path_regexp`](#path-regexp) matcher 通常每個命名 matcher 只能存在一次：

```caddy-d
@user expression path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')
```

或者相同，省略 matcher 名稱，並包裹在 [反引號](/docs/caddyfile/concepts#tokens-and-quotes) 中，以便將其解析為單個 token：

```caddy-d
@user `path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')`
```

您可以使用 [heredoc 語法](/docs/caddyfile/concepts#heredocs) 編寫多行 CEL 表達式：

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Hello, API!"
```


---

<a id="file"></a>
### file

```caddy-d
file {
	root       <path>
	try_files  <files...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delims...>
}
file <files...>

expression `file({
	'root': '<path>',
	'try_files': ['<files...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delims...>']
})`
expression file('<files...>')
```

按文件。

- `root` 定義查找文件的目錄。預設是當前工作目錄，或者如果設置了 `root` [變數](/docs/modules/http.handlers.vars) (`{http.vars.root}`)（可以通過 [`root` 指令](/docs/caddyfile/directives/root) 設置）。

- `try_files` 檢查其清單中符合 try_policy 的文件。

  要匹配目錄，請在路徑後附加一個正斜槓 `/`。所有文件路徑都是相對於站點 [root](/docs/caddyfile/directives/root) 的，並且 [glob 模式](https://pkg.go.dev/path/filepath#Match) 將被展開。

  如果 `try_policy` 是 `first_exist`（預設值），則清單中的最後一項可以是以 `=` 開頭的數字（例如 `=404`），作為備用方案，這將發出具有該代碼的錯誤；可以使用 [`handle_errors`](/docs/caddyfile/directives/handle_errors) 捕获並處理該錯誤。



- `try_policy` 指定如何選擇文件。預設為 `first_exist`。

	- `first_exist` 檢查文件是否存在。選擇第一個存在的文件。

	- `first_exist_fallback` 與 `first_exist` 類似，但假設清單中的最後一個元素始終存在以防止磁盤訪問。

	- `smallest_size` 選擇尺寸最小的文件。

	- `largest_size` 選擇尺寸最大的文件。

	- `most_recently_modified` 選擇最近修改的文件。

- `split_path` 將導致路徑在清單中找到的第一個分隔符處拆分，以便在每個要嘗試的文件路徑中查找。對於每個拆分值，拆分的左側（包括分隔符本身）將是嘗試的文件路徑。例如，對於 `/remote.php/dav/`，使用 `.php` 的分隔符將嘗試文件 `/remote.php`。每個分隔符必須出現在 URI 路徑組件的末尾，才能用作拆分分隔符。這是一個小眾設置，主要在服務 PHP 站點時使用。

因為具有 `first_exist` 策略的 `try_files` 非常常見，所以有一個單行快捷方式：

```caddy-d
file <files...>
```

空的 `file` matcher（後面沒有列出文件）將查看請求的文件&mdash;逐字來自 URI，相對於 [站點 root](/docs/caddyfile/directives/root)&mdash;是否存在。這實際上與 `file {path}` 相同。


<aside class="tip">

由於根據磁盤上是否存在文件進行重寫非常常見，因此還有一個 [`try_files` 指令](/docs/caddyfile/directives/try_files)，它是 `file` matcher 和 [`rewrite` 處理程序](/docs/caddyfile/directives/rewrite) 的快捷方式。

</aside>


匹配後，將提供四個新的 placeholder：

- `{file_match.relative}` 文件的根相對路徑。這在重寫請求時通常很有用。
- `{file_match.absolute}` 匹配文件的絕對路徑，包括 root。
- `{file_match.type}` 文件類型，`file` 或 `directory`。
- `{file_match.remainder}` 拆分文件路徑後剩餘的部分（如果配置了 `split_path`）


#### 範例：

匹配路徑是存在的文件請求：

```caddy-d
@file file
```

匹配路徑後跟 `.html` 是存在的文件請求，如果不是，則匹配路徑是存在的文件請求：

```caddy-d
@html file {
	try_files {path}.html {path} 
}
```

與上述相同，除了使用單行快捷方式，如果未找到文件則回退到發出 404 錯誤：

```caddy-d
@html-or-error file {path}.html {path} =404
```

一些使用 [CEL 表達式](#expression) 的更多範例。請記住，placeholder 在被 CEL 環境解釋之前會被預處理並轉換為常規的 CEL 函數調用，因此這裡使用了連接。此外，由於當前的解析限制，如果與 placeholder 連接，則必须使用長格式：

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---

<a id="header"></a>
### header

```caddy-d
header <field> [<value> ...]

expression header({'<field>': '<value>'})
```

按請求標頭欄位。

- `<field>` 是要檢查的 HTTP 標頭欄位的名稱。
	- 如果帶有前綴 `!`，則欄位必須不存在才能匹配（省略 value 參數）。
- `<value>` 是欄位必須具有的值才能匹配。可以指定一個或多個。
	- 如果帶有前缀 `*`，它將執行快速後綴匹配（出現在末尾）。
	- 如果帶有後綴 `*`，它將執行快速前綴匹配（出現在開頭）。
	- 如果被 `*` 包裹，它將執行快速子字串匹配（出現在任何位置）。
	- 否則，它是快速精確匹配。

同一集合中的不同標頭欄位是「與 (AND)」關係。每個欄位的多個值是「或 (OR)」關係。

請注意，標頭欄位可能會重複並具有不同的值。後端應用程式必須考慮標頭欄位值是陣列，而不是單個值，Caddy 不會解釋此類難題中的含義。

#### 範例：

匹配 `Connection` 標頭包含 `Upgrade` 的請求：

```caddy-d
@upgrade header Connection *Upgrade*
```

匹配 `Foo` 標頭包含 `bar` 或 `baz` 的請求：

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

匹配完全沒有 `Foo` 標頭欄位的請求：

```caddy-d
@not_foo header !Foo
```

使用 [CEL 表達式](#expression)，通過檢查 `Connection` 標頭包含 `Upgrade` 且 `Upgrade` 標頭等於 `websocket`（HTTP/2 有用於此的 `:protocol` 標頭）來匹配 WebSocket 請求：

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---

<a id="header-regexp"></a>
### header_regexp

```caddy-d
header_regexp [<name>] <field> <regexp>

expression header_regexp('<name>', '<field>', '<regexp>')
expression header_regexp('<field>', '<regexp>')
```

類似於 [`header`](#header)，但支持正則表達式。

使用的正則表達式語言是 RE2，包含在 Go 中。請參閱 [RE2 語法參考](https://github.com/google/re2/wiki/Syntax) 和 [Go 正則語法概述](https://pkg.go.dev/regexp/syntax)。

自 v2.8.0 起，如果 *未* 提供 `name`，則名稱將取自命名 matcher 的名稱。例如，命名 matcher `@foo` 將使此 matcher 命名為 `foo`。指定名稱的主要優點是在同一個命名 matcher 中使用多個正則 matcher（例如 `header_regexp` 和 [`path_regexp`](#path-regexp)，或多個不同的標頭欄位）。

匹配後，可以通過指令中的 [placeholder](/docs/caddyfile/concepts#placeholders) 訪問捕獲組：
- `{re.<name>.<capture_group>}` 其中：
  - `<name>` 是正則表達式的名稱，
  - `<capture_group>` 是表達式中捕获組的名稱或編號。

- 為了方便起見，還填充了不帶名稱的 `{re.<capture_group>}`。缺點是如果按順序使用多個正則 matcher，則 placeholder 值將被下一個 matcher 覆蓋。

捕獲組 `0` 是完整的正則匹配，`1` 是第一個捕獲組，`2` 是第二個捕獲組，依此類推。因此 `{re.foo.1}` 或 `{re.1}` 都將保存第一個捕獲組的值。

每個標頭欄位僅支持一個正則表達式，因為正則模式無法合併；如果您需要更多，請考慮使用 [`expression` matcher](#expression)。與多個不同標頭欄位的匹配將進行「與 (AND)」運算。

#### 範例：

匹配 `Cookie` 標頭包含 `login_` 後跟十六進位字串的請求，其中包含一個捕獲組，可以通過 `{re.login.1}` 或 `{re.1}` 訪問。

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

可以通過省略名稱來簡化這點，名稱將從命名 matcher 中推斷出來：

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

或者相同，使用 [CEL 表達式](#expression)：

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```



---

<a id="host"></a>
### host

```caddy-d
host <hosts...>

expression host('<hosts...>')
```

通過請求的 `Host` 標頭欄位匹配請求。

由於大多數 site block 已經在站點的地址中指明了主機，因此此 matcher 更常用於使用通配符主機名的 site block（參見 [通配符證書模式](/docs/caddyfile/patterns#wildcard-certificates)），但需要特定於主機名的邏輯。

多個 `host` matcher 將被「或 (OR)」在一起。

#### 範例：

匹配一個子域名：

```caddy-d
@sub host sub.example.com
```

匹配頂級域名和子域名：

```caddy-d
@site host example.com www.example.com
```

使用 [CEL 表達式](#expression) 的多個子域名：

```caddy-d
@app `host('app1.example.com', 'app2.example.com')`
```



---

<a id="method"></a>
### method

```caddy-d
method <verbs...>

expression method('<verbs...>')
```

按 HTTP 請求的方法（動詞）。動詞應為大寫，如 `POST`。可以匹配一個或多個方法。

多個 `method` matcher 將被「或 (OR)」在一起。

#### 範例：

匹配使用 `GET` 方法的請求：

```caddy-d
@get method GET
```

匹配使用 `PUT` 或 `DELETE` 方法的請求：

```caddy-d
@put-delete method PUT DELETE
```

使用 [CEL 表達式](#expression) 匹配唯讀方法：

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```



---

<a id="not"></a>
### not

```caddy-d
not <matcher>
```

或者，要否定多個進行「與 (AND)」運算的 matcher，請開啟一個區塊：

```caddy-d
not {
	<matchers...>
}
```

包含的 matcher 的結果將被反轉。

#### 範例：

匹配路徑 *不* 以 `/css/` 或 `/js/` 開頭的請求。

```caddy-d
@not-assets {
	not path /css/* /js/*
}
```

匹配 **兩者皆無** 的請求：
- `/api/` 路徑前綴，**且無**
- `POST` 請求方法

即必須兩者皆不具備才能匹配：

```caddy-d
@with-neither {
	not path /api/*
	not method POST
}
```

匹配 **非兩者同時具備** 的請求：
- `/api/` 路徑前綴，**以及**
- `POST` 請求方法

即只要不具備其中之一或兩者皆不具備即可匹配：

```caddy-d
@without-both {
	not {
		path /api/*
		method POST
	}
}
```

此 matcher 沒有 [CEL 表達式](#expression)，因為您可以使用 `!` 運算子進行否定。例如：

```caddy-d
@without-both `!path('/api*') && !method('POST')`
```

與使用括號的這點相同：

```caddy-d
@without-both `!(path('/api*') || method('POST'))`
```




---

<a id="path"></a>
### path

```caddy-d
path <paths...>

expression path('<paths...>')
```

按請求路徑（請求 URI 的路徑部分）。路徑匹配是精確的，但不區分大小寫。可以使用通配符 `*`：

- 僅在末尾，用於前綴匹配 (`/prefix/*`)
- 僅在開頭，用於後綴匹配 (`*.suffix`)
- 僅在兩側，用於子字串匹配 (`*/contains/*`)
- 僅在中間，用於全域匹配 (`/accounts/*/info`)

斜槓是有意義的。例如，`/foo*` 將匹配 `/foo`、`/foobar`、`/foo/` 和 `/foo/bar`，但 `/foo/*` 將 *不* 匹配 `/foo` 或 `/foobar`。

請求路徑在匹配前會經過清理以解析目錄遍歷點。此外，除非匹配模式有多個斜槓，否則多個斜槓將被合併。換句話說，`/foo` 將匹配 `/foo` 和 `//foo`，但 `//foo` 將僅匹配 `//foo`。

由於任何給定 URI 都有多種轉義形式，請求路徑將被規範化（URL 解碼、取消轉義），但在匹配模式中也存在轉義序列的位置除外。例如，`/foo/bar` 同時匹配 `/foo/bar` 和 `/foo%2Fbar`，但 `/foo%2Fbar` 將僅匹配 `/foo%2Fbar`，因為轉義序列在配置中明確給出。

特殊的通配符轉義 `%*` 也可以用來代替 `*` 以使其匹配跨度保持轉義。例如，`/bands/*/*` 將不匹配 `/bands/AC%2FDC/T.N.T`，因為路徑將在規範化空間中進行比較，在那裡它看起來像 `/bands/AC/DC/T.N.T`，這與模式不匹配；但是，`/bands/%*/*` 將匹配 `/bands/AC%2FDC/T.N.T`，因為由 `%*` 表示的跨度將在不解碼轉義序列的情況下進行比較。

多個路徑將被「或 (OR)」在一起。

#### 範例：

匹配多個目錄及其內容：

```caddy-d
@assets path /js/* /css/* /images/*
```

匹配特定文件：

```caddy-d
@favicon path /favicon.ico
```

匹配文件擴展名：

```caddy-d
@extensions path *.js *.css
```

使用 [CEL 表達式](#expression) ：

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```



---

<a id="path-regexp"></a>
### path_regexp

```caddy-d
path_regexp [<name>] <regexp>

expression path_regexp('<name>', '<regexp>')
expression path_regexp('<regexp>')
```

類似於 [`path`](#path)，但支持正則表達式。針對經過 URI 解碼/取消轉義的路徑運行。

使用的正則表達式語言是 RE2，包含在 Go 中。請參閱 [RE2 語法參考](https://github.com/google/re2/wiki/Syntax) 和 [Go 正則語法概述](https://pkg.go.dev/regexp/syntax)。

自 v2.8.0 起，如果 *未* 提供 `name`，則名稱將取自命名 matcher 的名稱。例如，命名 matcher `@foo` 將使此 matcher 命名為 `foo`。指定名稱的主要優點是在同一個命名 matcher 中使用多個正則 matcher（例如 `path_regexp` 和 [`header_regexp`](#header-regexp)）。

匹配後，可以通過指令中的 [placeholder](/docs/caddyfile/concepts#placeholders) 訪問捕獲組：
- `{re.<name>.<capture_group>}` 其中：
  - `<name>` 是正則表達式的名稱，
  - `<capture_group>` 是表達式中捕获組的名稱或編號。

- 為了方便起見，還填充了不帶名稱的 `{re.<capture_group>}`。缺點是如果按順序使用多個正則 matcher，則 placeholder 值將被下一個 matcher 覆蓋。

捕獲組 `0` 是完整的正則匹配，`1` 是第一個捕獲組，`2` 是第二個捕獲組，依此類推。因此 `{re.foo.1}` 或 `{re.1}` 都將保存第一個捕獲組的值。

每個命名 matcher 只能有一個 `path_regexp` 模式，因為此 matcher 無法與自身合併；如果您需要更多，請考慮使用 [`expression` matcher](#expression)。

#### 範例：

匹配路徑以 6 個字元的十六進位字串結尾且後跟 `.css` 或 `.js` 作為文件擴展名的請求，具有捕獲組（括在 `( )` 中的部分），可以分別通過 `{re.static.1}` 和 `{re.static.2}`（或 `{re.1}` 和 `{re.2}`）訪問：

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

可以通過省略名稱來簡化這點，名稱將從命名 matcher 中推斷出來：

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

或者相同，使用 [CEL 表達式](#expression)，同時驗證磁盤上是否存在 [`file`](#file)：

```caddy-d
@static `path_regexp('\.([a-f0-9]{6})\.(css|js)$') && file()`
```



---

<a id="protocol"></a>
### protocol

```caddy-d
protocol http|https|grpc|http/<version>[+]

expression protocol('http|https|grpc|http/<version>[+]')
```

按請求協議。可以使用廣泛的協議名稱，如 `http`、`https` 或 `grpc`；或特定或最低 HTTP 版本，如 `http/1.1` 或 `http/2+`。

每個命名 matcher 只能有一個 `protocol` matcher。

#### 範例：

匹配使用 HTTP/2 的請求：

```caddy-d
@http2 protocol http/2+
```

使用 [CEL 表達式](#expression)：

```caddy-d
@http2 `protocol('http/2+')`
```



---

<a id="query"></a>
### query

```caddy-d
query <key>=<val>...
query ""

expression query({'<key>': '<val>'})
expression query({'<key>': ['<vals...>']})
```

按查詢字串參數。應為 `key=value` 對序列，或空字串 ""。鍵是精確匹配的（區分大小寫），但也支持 `*` 來匹配任何值。值可以使用 placeholder。空字串匹配沒有查詢參數的 HTTP 請求。

每個命名 matcher 可以有多個 `query` matcher，具有相同鍵的對將被「或 (OR)」在一起。不同的鍵將被「與 (AND)」在一起。因此，matcher 中的所有鍵必須至少有一個匹配值。

非法查詢字串（語法錯誤、未轉义的分號等）將無法解析，因此不會匹配。

**注意：** 查詢字串參數是陣列，而不是單個值。這是因為在查詢字串中重複鍵是有效的，並且每個鍵可能具有不同的值。如果查詢字串中分配了任何一個配置的值，此 matcher 將匹配該鍵。使用查詢字串的後端應用程式必須考慮查詢字串值是陣列且可以具有多個值。

#### 範例：

匹配具有任何值的 `q` 查詢參數：

```caddy-d
@search query q=*
```

匹配值為 `asc` 或 `desc` 的 `sort` 查詢參數：

```caddy-d
@sorted query sort=asc sort=desc
```

使用 [CEL 表達式](#expression) 同時匹配 `q` 和 `sort`：

```caddy-d
@search-sort `query({'sort': ['asc', 'desc'], 'q': '*'})`
```


---

<a id="remote-ip"></a>
### remote_ip

```caddy-d
remote_ip <ranges...>

expression remote_ip('<ranges...>')
```

按遠端 IP 地址（即直接對等端的 IP 地址或通過 [PROXY 協議](/docs/caddyfile/options#proxy-protocol) 設置的地址）。接受精確的 IP 或 CIDR 範圍。支持 IPv6 區域。

作為快捷方式，`private_ranges` 可用於匹配所有私有 IPv4 和 IPv6 範圍。這與指定所有這些範圍相同：`192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

如果您希望匹配從 HTTP 標头解析的客戶端「真實 IP」，請改用 [`client_ip`](#client-ip) matcher。

每個命名 matcher 可以有多個 `remote_ip` matcher，它們的範圍將被合併並進行「或 (OR)」運算。

#### 範例：

匹配來自私有 IPv4 地址的請求：

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

此 matcher 通常與 [`not`](#not) matcher 配合使用以反轉匹配。例如，要中止來自 *公共* IPv4 和 IPv6 地址的所有連接（這是所有私有範圍的反向）：

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

在 [CEL 表達式](#expression) 中，它看起來像这样：

```caddy-d
@my-friends `remote_ip('12.23.34.45', '23.34.45.56')`
```


---

<a id="vars"></a>
### vars

```caddy-d
vars <variable> <values...>

expression vars({'<variable>': '<value>'})
expression vars({'<variable>': ['<values...>']})
```

按請求上下文中變數的值或 placeholder 的值。可以指定多個值以匹配任何可能的內容（「或 (OR)」關係）。

**&lt;variable&gt;** 參數可以是變數名稱或大括號 `{ }` 中的 placeholder。（第一個參數中不展開 placeholder。）

當與設置輸出的 [`map` 指令](/docs/caddyfile/directives/map)、路由中的 [`vars` 指令](/docs/caddyfile/directives/vars) 或在請求上下文中設置某些資訊的插件配合使用時，此 matcher 最有用。

#### 範例：

匹配名為 `magic_number` 的 [`map` 指令](/docs/caddyfile/directives/map) 的輸出值 `3` 或 `5`：

```caddy-d
vars {magic_number} 3 5
```

匹配任意 placeholder 的值，即認證用戶의 ID，`Bob` 或 `Alice`：

```caddy-d
vars {http.auth.user.id} Bob Alice
```

一個完整的範例，使用 [`vars` 指令](/docs/caddyfile/directives/vars) 設置變數，然後使用 [`vars` matcher](#vars) 進行匹配。在這裡，我們將兩個請求標頭組合成一個變數，並匹配該變數：

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "You sent Foo=123 and Bar=456!"
	}
	handle {
		respond "Foo and Bar were not special."
	}
}
```

在 [CEL 表達式](#expression) 中，它看起來像这样：

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---

<a id="vars-regexp"></a>
### vars_regexp

```caddy-d
vars_regexp [<name>] <variable> <regexp>

expression vars_regexp('<name>', '<variable>', '<regexp>')
expression vars_regexp('<variable>', '<regexp>')
```

類似於 [`vars`](#vars)，但支持正則表達式。

使用的正則表達式語言是 RE2，包含在 Go 中。請參閱 [RE2 語法參考](https://github.com/google/re2/wiki/Syntax) 和 [Go 正則語法概述](https://pkg.go.dev/regexp/syntax)。

自 v2.8.0 起，如果 *未* 提供 `name`，則名稱將取自命名 matcher 的名稱。例如，命名 matcher `@foo` 將使此 matcher 命名為 `foo`。指定名稱的主要優點是在同一個命名 matcher 中使用多個正則 matcher（例如 `vars_regexp` 和 [`header_regexp`](#header-regexp)）。

匹配後，可以通過指令中的 [placeholder](/docs/caddyfile/concepts#placeholders) 訪問捕獲組：
- `{re.<name>.<capture_group>}` 其中：
  - `<name>` 是正則表達式的名稱，
  - `<capture_group>` 是表達式中捕获組的名稱或編號。

- 為了方便起見，還填充了不帶名稱的 `{re.<capture_group>}`。缺點是如果按順序使用多個正則 matcher，則 placeholder 值將被下一個 matcher 覆蓋。

捕獲組 `0` 是完整的正則匹配，`1` 是第一個捕獲組，`2` 是第二個捕獲組，依此類推。因此 `{re.foo.1}` 或 `{re.1}` 都將保存第一個捕獲組的值。

每個變數名稱僅支持一個正則表達式，因為正則模式無法合併；如果您需要更多，請考慮使用 [`expression` matcher](#expression)。與多個不同變數的匹配將進行「與 (AND)」運算。

#### 範例：

匹配名為 `magic_number` 的 [`map` 指令](/docs/caddyfile/directives/map) 的輸出值以 `4` 開頭，將值捕獲在可以通過 `{re.magic.1}` 或 `{re.1}` 訪問的捕獲組中：

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

可以通過省略名稱來簡化這點，名稱將從命名 matcher 中推斷出來：

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

在 [CEL 表達式](#expression) 中，它看起來像这样：

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
