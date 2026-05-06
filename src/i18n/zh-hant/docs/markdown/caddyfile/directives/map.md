---
title: map (Caddyfile 指令)
---

<a id="map"></a>
# map

根據輸入值切換並設定自定義 placeholder 的值。

它將源值 (source value) 與 map 的輸入端進行比較，對於匹配的項，它將輸出值應用於每個目標 (destination)。目標會成為 placeholder 名稱。也可以為每個目標指定預設輸出值。

對應的 placeholder 在被使用之前不會進行評估，因此即使是處理非常龐大的對應表，此指令也非常高效。

<a id="syntax"></a>
## 語法

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<input> <outputs...>
	default    <defaults...>
}
```

- **&lt;source&gt;** 是用於切換的輸入值。通常是一個 placeholder。

- **&lt;destinations...&gt;** 是要建立的用於存放輸出值的 placeholder。

- **&lt;input&gt;** 是要匹配的輸入值。如果帶有 `~` 前綴，則被視為正規表示式 (regular expression)。

- **&lt;outputs...&gt;** 是一個或多個要存儲在相關 placeholder 中的輸出值。第一個輸出寫入第一個目標，第二個輸出寫入第二個目標，依此類推。
  
  作為特殊情況，Caddyfile 解析器將字面量連字號 (`-`) 的輸出視為 null/nil 值。如果您想在給定輸入的情況下對該特定輸出回退到預設值，但又想對其他輸出使用非預設值，這非常有用。

  如果可能，輸出將進行類型轉換；`true` 和 `false` 將轉換為布林 (boolean) 類型，數值將相應地轉換為整數 (integer) 或浮點數 (float)。為了避免這種轉換，您可以用 [引號](/docs/caddyfile/concepts#tokens-and-quotes) 包裹輸出，它們將保持為字串。

  每個映射的輸出數量不得超過目標數量；但是，為了方便起見，輸出的數量可以少於目標數量，任何缺失的輸出都將隱式填補。
  
  如果使用正規表示式作為輸入，則可以使用 `${group}` 引用擷取群組 (capture groups)，其中 `group` 是表達式中擷取群組的名稱或編號。擷取群組 `0` 是整個正規表示式匹配項，`1` 是第一個擷取群組，`2` 是第二個擷取群組，依此類推。

- **&lt;default&gt;** 指定在沒有輸入匹配時要存儲的輸出值。


<a id="examples"></a>
## 範例

以下範例演示了此指令的大部分方面：

```caddy-d
map {host}                {my_placeholder}  {magic_number} {
	example.com           "some value"      3
	foo.example.com       "another value"
	~(.*)\.example\.com$  "${1} subdomain"  5

	~.*\.net$             -                 7
	~.*\.xyz$             -                 15

	default               "unknown domain"  42
}
```

此指令根據 `{host}` 的值進行切換，即請求的網域名稱。

- 如果請求是針對 `example.com`，則將 `{my_placeholder}` 設定為 `some value`，並將 `{magic_number}` 設定為 `3`。
- 否則，如果請求是針對 `foo.example.com`，則將 `{my_placeholder}` 設定為 `another value`，並讓 `{magic_number}` 預設為 `42`。
- 否則，如果請求是針對 `example.com` 的任何子網域，則將 `{my_placeholder}` 設定為包含第一個正規表示式擷取群組值的字串，即整個子網域，並將 `{magic_number}` 設定為 `5`。
- 否則，如果請求是針對任何以 `.net` 或 `.xyz` 結尾的主機，則分別僅將 `{magic_number}` 設定為 `7` 或 `15`。保持 `{my_placeholder}` 未設定。
- 否則（對於所有其他主機），將應用預設值：`{my_placeholder}` 將被設定為 `unknown domain`，而 `{magic_number}` 將被設定為 `42`。
