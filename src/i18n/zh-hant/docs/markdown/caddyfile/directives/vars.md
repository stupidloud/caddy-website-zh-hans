---
title: vars (Caddyfile 指令)
---

<a id="vars"></a>
# vars

設置一個或多個變量為特定值，以便稍後在請求處理鏈中使用。

訪問變量的主要方式是使用 placeholder，其形式為 `{vars.variable_name}`，或者使用 [`vars`](/docs/caddyfile/matchers#vars) 和 [`vars_regexp`](/docs/caddyfile/matchers#vars_regexp) 請求 matcher。

您可以在 [`templates`](templates) 指令中使用 `placeholder` 函數來使用變量，例如：`{{ "{{placeholder \"http.vars.variable_name\"}}" }}`

作為特殊情況，可以覆蓋存儲在 replacer 中的名為 `http.auth.user.id` 的變量，以更新 [access logs](log) 中的 `user_id` 字段。


<a id="syntax"></a>
## 語法

```caddy-d
vars [<matcher>] [<name> <value>] {
    <name> <value>
    ...
}
```

- **&lt;name&gt;** 是要設置的變量名稱。

- **&lt;value&gt;** 是變量的值。

  如果可能，該值將進行類型轉換；`true` 和 `false` 將轉換為布爾類型，數值將相應轉換為整數或浮點數。要避免這種轉換並將其保留為字符串，您可以用 [quotes](/docs/caddyfile/concepts#tokens-and-quotes) 將其括起來。

<a id="examples"></a>
## 範例

設置單個變量，其值根據請求路徑而定，然後返回該值：

```caddy
example.com {
	vars /foo* isFoo "yep"
	vars isFoo "nope"

	respond {vars.isFoo}
}
```

設置多個變量，每個變量都轉換為適當的標量類型：

```caddy-d
vars {
	# 布爾值
	abc true

	# 整數
	def 1

	# 浮點數
	ghi 2.3

	# 字符串
	jkl "example"
}
```
