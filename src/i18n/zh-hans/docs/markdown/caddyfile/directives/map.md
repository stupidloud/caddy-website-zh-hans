---
title: "map（Caddyfile 指令）"
---

# 地图

根据输入值设置已启用的自定义占位符的值。

它将源值与映射表的输入侧进行比对，对于匹配的项，将输出值应用到每个目标上。目标将作为占位符名称。还可以为每个目标指定默认输出值。

映射占位符在被使用之前不会被求值，因此即使面对非常庞大的映射，该指令也相当高效。

## 语法

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<input> <outputs...>
	default    <defaults...>
}
```

- **&lt;source&gt;** 是用于触发开关的输入值。通常是一个占位符。

- **&lt;destinations...&gt;** 是用于存储输出值的占位符。

- **&lt;input&gt;** 是待匹配的输入值。如果前面加上 `~`，则将其视为正则表达式。

- **&lt;outputs...&gt;** 表示一个或多个要存储在相关占位符中的输出值。第一个输出将写入第一个目标，第二个输出写入第二个目标，依此类推。
  
  作为一种特例，Caddyfile 解析器会将字面上的连字符 (`-`）视为空值。如果希望在给定输入的情况下，针对该特定输出使用默认值，但对其他输出使用非默认值，此特性将非常有用。

  如果可能，输出的类型将进行转换； `true` 并且 `false` 将转换为布尔类型，数值将根据情况转换为整数或浮点数。若要避免此类转换，可将输出用[引号](/docs/caddyfile/concepts#tokens-and-quotes)包裹，此时它们将保持为字符串。

  每个映射的输出数量不得超过目标数量；不过，出于方便起见，输出数量可以少于目标数量，任何缺失的输出都将被隐式补全。
  
  如果输入的是正则表达式，则可以通过 `${group}` ，其中 `group` 表示表达式中捕获组的名称或编号。捕获组 `0` 表示完整的正则表达式匹配结果， `1` 是第一个捕获组， `2` 表示第二个捕获组，以此类推。

- **&lt;default&gt;** 指定在没有匹配的输入时应存储的输出值。


## 示例

以下示例演示了该指令的大部分功能：

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

此指令启用 `{host}`，即请求的域名。

- 如果请求的是 `example.com`，请设置 `{my_placeholder}` 为 `some value`，并将 `{magic_number}` 为 `3`.
- 否则，如果请求的是 `foo.example.com`，则设置 `{my_placeholder}` 为 `another value`，并让 `{magic_number}` 默认值为 `42`.
- 否则，如果请求指向 `example.com`，则将 `{my_placeholder}` 为包含第一个正则表达式捕获组值的字符串，即整个子域名，并将 `{magic_number}` 设为 5。
- 否则，如果请求的目标是任何以 `.net` 或 `.xyz`，则仅设置 `{magic_number}` 为 `7` 或 `15`。将 `{my_placeholder}` 保持未设置。
- 否则（对于所有其他主机），将应用默认值： `{my_placeholder}` 将设置为 `unknown domain` 并将 `{magic_number}` 将设置为 `42`.
