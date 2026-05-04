---
title: "log（Caddyfile 指令）"
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.textContent.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# 日志

启用并配置 HTTP 请求日志记录（也称为访问日志）。

<aside class="tip">

要配置 Caddy 的运行时日志，请参阅 [`log` 全局选项](/docs/caddyfile/options#log)。

</aside>


该 `log` 指令适用于其所在的站点块中的主机名，除非被 `hostnames` 子指令进行覆盖。

配置完成后，默认情况下所有针对该站点的请求都会被记录。若要根据条件跳过某些请求的记录，请使用[`log_skip`指令](log_skip)。

若要在日志条目中添加自定义字段，请使用[`log_append`指令](log_append)。


- [语法](#syntax)
- [输出模块](#output-modules)
  - [stderr](#stderr)
  - [标准输出](#stdout)
  - [丢弃](#discard)
  - [文件](#file)
  - [网络](#net)
- [格式化模块](#format-modules)
  - [控制台](#console)
  - [json](#json)
  - [筛选](#filter)
    - [删除](#delete)
	- [重命名](#rename)
	- [替换](#replace)
	- [子网掩码](#ip-mask)
	- [查询](#query)
	- [cookie](#cookie)
	- [正则表达式](#regexp)
	- [哈希](#hash)
  - [追加](#append)
- [示例](#examples)

默认情况下，包含潜在敏感信息的标头（`Cookie`, `Set-Cookie`, `Authorization` 和 `Proxy-Authorization`）将作为 `REDACTED` 的形式记录在访问日志中。可通过全局服务器选项[`log_credentials`](/docs/caddyfile/options#log-credentials)禁用此行为。


<a id="syntax"></a>
## 语法

```caddy-d
log [<logger_name>] {
	hostnames <hostnames...>
	no_hostname
	output <writer_module> ...
	format <encoder_module> ...
	level  <level>
	sampling {
		interval   <duration>
		first      <number>
		thereafter <number>
	}
}
```

- **logger_name** <span id="logger_name"/> 是对本网站日志器名称的可选覆盖设置。

  默认情况下，日志记录器的名称会自动生成，例如 `log0`, `log1`，依此类推，具体取决于 Caddyfile 中站点的顺序。此功能仅在您希望从全局选项中定义的另一个日志器可靠地引用该日志器的输出时才有用。请参见下面的[示例](#multiple-outputs)。

- **主机名** <span id="hostnames"/> 是对该日志器所适用的主机名的可选覆盖设置。

  默认情况下，日志记录器适用于其所在站点块的主机名，即站点地址。如果您希望在[通配符站点块](/docs/caddyfile/patterns#wildcard-certificates)中为每个子域名定义不同的日志记录器，此功能非常有用。请参见下面的[示例](#wildcard-logs)。

- **no_hostname** <span id="no_hostname"/> 可防止日志记录器与任何站点块的主机名相关联。默认情况下，日志记录器会与包含 `log` 指令所在的站点地址相关联。

  当您希望根据某些条件（例如请求路径或方法）使用[`log_name`指令](/docs/caddyfile/directives/log_name)将请求记录到不同的文件时，此功能非常有用。

- **输出** <span id="output"/> 用于配置日志的写入位置。请参阅下文的 [`output` 模块](#output-modules)。

  默认： `stderr`.

- **格式** <span id="format"/> 描述了日志的编码或格式化方式。请参阅下文的 [`format` 模块](#format-modules)。

  默认： `console` 如果 `stderr` 被检测为终端， `json` 否则。

- **级别** <span id="level"/> 是日志记录的最低级别。默认值： `INFO`.

  请注意，访问日志目前仅输出 `INFO` 和 `ERROR` 级别的日志。

- **采样** <span id="sampling"/> 用于配置日志采样以减少日志量。如果指定了采样，则表示已启用该功能，并采用下述默认设置。省略此项将禁用采样。

  - **间隔**是指进行采样的[时间窗口](/docs/conventions#durations)。默认值： `1s` （禁用）。

  - **first** 表示在每个时间间隔内，针对特定级别和消息应保留多少条日志。默认值： `100`.

  - **thereafter** 表示在保留首批日志后，每个时间段内应跳过多少条日志。默认值： `100`.

  例如，使用 `interval 1s`、`first 5` 和 `thereafter 10` 时，在每个 1 秒的时间间隔内，将保留前 5 条日志条目，然后在该秒内，每第 10 条具有相同级别和消息的日志条目将被允许通过。


<a id="output-modules"></a>
### 输出模块

**output** 子指令允许您自定义日志的写入位置。

<a id="stderr"></a>
#### stderr

标准误差（控制台，默认）。

```caddy-d
output stderr
```

<a id="stdout"></a>
#### 标准输出

标准输出（控制台）。

```caddy-d
output stdout
```

<a id="discard"></a>
#### 丢弃

无输出。

```caddy-d
output discard
```

<a id="file"></a>
#### 文件

一个文件。默认情况下，日志文件会根据大小进行轮换（“滚动”），以防止磁盘空间耗尽。

日志轮换由 [Timberjack](https://github.com/DeRuina/timberjack) 提供 <a href="https://github.com/DeRuina/timberjack"><img src="/old/resources/images/external-link.svg" class="external-link"></a>

<aside class="tip">

**关于重新加载日志文件选项的说明：** 需重启服务器才能将配置更改应用到指定的输出文件中。
除非您添加了新的日志文件名，否则这些更改在服务器重启时不会生效。

</aside>

```caddy-d
output file <filename> {
	mode          <mode>
	roll_disabled
	roll_size     <size>
	roll_interval <duration>
	roll_minutes  <minutes...>
	roll_at	      <times...>
	roll_uncompressed
	roll_local_time
	roll_keep     <num>
	roll_keep_for <days>
	backup_time_format <format>
}
```

- **&lt;filename&gt;** 是日志文件的路径。

  进行文件滚动时，会使用模板 `<name>-<timestamp>-<reason>.log`。时间戳的格式由[`backup_time_format`](#backup_time_format)选项决定。原因可能是 `size` 或 `time`，具体取决于触发轮换的原因。如果文件被压缩， `.gz` 则会在文件名后附加。

   例如，如果文件名为 `access.log`，则滚动后的文件可能命名为 `access-2026-01-30T22-15-42.123-size.log`（若因文件大小而滚动），或者命名为 `access-2025-01-30T00-00-00.000-time.log`（若因时间原因进行滚动）。

- **模式** <span id="mode"/> 指日志文件应采用的 Unix 文件模式/权限。 该模式由 1 到 4 个八进制数字组成（与 Unix <a href="https://en.wikipedia.org/wiki/Chmod">chmod <img src="/old/resources/images/external-link.svg" class="external-link"></a> 命令接受的数字格式相同，但全零模式将被解释为默认模式 `600`).

  例如： `0600` 将模式设置为 `rw-,---,---` （日志文件的所有者具有读写权限，其他人则无权限）； `0640` 将模式设置为 `rw-,r--,---` （文件所有者具有读写权限，组成员仅具有读取权限）； `644` 将权限设置为 `rw-,r--,r--` 为日志文件的所有者提供读写权限，但仅向组所有者及其他用户提供读取权限。

- **roll_disabled** <span id="roll_disabled"/> 禁用日志轮换。这可能会导致磁盘空间耗尽，因此仅当您的日志文件通过其他方式进行管理时才应使用此选项。

- **roll_size** <span id="roll_size"/> 表示日志文件滚动时使用的大小。当前实现支持兆字节级精度；小数值将向上舍入至下一个整兆字节。例如， `1.1MiB` 将被四舍五入为 `2MiB`.

  此选项始终处于启用状态。如果向日志写入数据导致文件大小超过指定值，日志将立即进行轮换。备份文件名中将包含 `size` 作为原因。

  默认： `100MiB`

- **roll_interval** <span id="roll_interval"/> 是日志轮换之间的最大间隔时间。该值为一个[时间字符串](/docs/conventions#durations)，表示达到该时间后将对日志文件进行轮换。

  启用此功能后，当距离上次轮换已过此时间间隔，系统将在下次向日志写入数据时对文件进行轮换。备份文件名将包含 `time` 作为原因。

  请注意，如果设置为 `24h`，系统并不一定会在午夜进行轮换，而是在上次轮换后的第24小时进行。如果因数据量过大而触发轮换，则下次轮换的时间将与上次轮换的时间存在偏差。您可以使用 `roll_at` 或 `roll_minutes` 选项，以在特定时间进行轮换。

  默认：禁用

- **roll_minutes** <span id="roll_minutes"/> 是一组用于滚动日志文件的分钟值（0-59）。例如， `10 40` 将使日志文件每 30 分钟在 `xx:10` 和 `xx:40` 整点进行滚动。滚动时间以整点（第0秒）为基准。

  启用此功能将生成一个 goroutine 定时器，该定时器会在指定的分钟数时触发日志轮换（即引入少量后台处理）。此功能是在 `roll_interval` 和 `roll_size`。备份文件名将包含 `time` 作为原因。

  默认：禁用

- **roll_at** <span id="roll_at"/> 是一个时间值列表（采用24小时制），用于指定滚动日志文件的时间点。例如， `00:00 12:00` 将使日志文件每天在午夜和中午各滚动一次。滚动操作以整点（第 0 秒）为基准。

  启用此功能将生成一个 goroutine 定时器，该定时器会在指定时间触发日志轮换（即引入少量后台处理）。此功能是在 `roll_interval` 和 `roll_size`。备份文件名将包含 `time` 作为原因。

  默认：已禁用

- **roll_uncompressed** <span id="roll_uncompressed"/> 关闭日志的 gzip 压缩。

  默认：启用 `gzip` 压缩。

- **roll_local_time** <span id="roll_local_time"/> 设置滚动命名规则，使文件名中使用本地时间戳。 
  默认：使用协调世界时（UTC）。

- **roll_keep** <span id="roll_keep"/> 表示在删除最旧的日志文件之前，应保留多少个日志文件。当创建新的日志文件时触发。

  默认： `10`

- **roll_keep_for** <span id="roll_keep_for"/> 表示保留已轮转文件的时长，以[时间字符串](/docs/conventions#durations)形式表示。当创建新的日志文件时触发。
  当前的实现支持按天为单位；小数部分将向上舍入至下一个整日。例如， `36h` (1.5 天) 会被向上舍入为 `48h` (2天)。
  
  默认： `2160h` (90天)

- **backup_time_format** <span id="backup_time_format"/> 是备份文件名中使用的时间格式。必须是有效的日期时间格式字符串；详情请参阅 [Go ](https://pkg.go.dev/time#pkg-constants)语言[文档](https://pkg.go.dev/time#pkg-constants)。

  默认： `2006-01-02T15-04-05`


<a id="net"></a>
#### 网络套接字

一个网络套接字。如果套接字断开连接，它将在尝试重新连接的同时将日志输出到 stderr。

```caddy-d
output net <address> {
	dial_timeout <duration>
	soft_start
}
```

- **&lt;address&gt;** 是用于写入日志的[地址](/docs/conventions#network-addresses)。

- **dial_timeout** <span id="dial_timeout"/> 表示等待成功连接日志套接字的时间长度。如果套接字断开，日志输出可能会被阻塞，最长持续此时间。

- **soft_start** <span id="soft_start"/> 在连接套接字时会忽略错误，即使远程日志服务不可用，也能加载配置。此时日志将重定向至 stderr。


<a id="format-modules"></a>
### 格式模块

**format** 子指令允许您自定义日志的编码（格式）方式。它出现在 `log` 块中。

<aside class="tip">

**关于通用日志格式 (CLF) 的说明：** CLF 与现代结构化日志格式存在冲突。若要将访问日志转换为已弃用的通用日志格式，请使用 <a href="https://github.com/caddyserver/transform-encoder">`transform-encoder` 插件 <img src="/old/resources/images/external-link.svg" class="external-link"></a>。

</aside>


除了各编码器的特定语法外，以下通用属性可在大多数编码器上进行设置：

```caddy-d
format <encoder_module> {
	message_key     <key>
	level_key       <key>
	time_key        <key>
	name_key        <key>
	caller_key      <key>
	stacktrace_key  <key>
	line_ending     <char>
	time_format     <format>
	time_local
	duration_format <format>
	level_format    <format>
}
```

- **message_key** <span id="message_key"/> 日志条目中“message”字段的键。默认值： `msg`

- **level_key** <span id="level_key"/> 日志条目中“level”字段的键。默认值： `level`

- **time_key** <span id="time_key"/> 日志条目中时间字段的键。默认值： `ts`
- **name_key** <span id="name_key"/> 日志条目中“name”字段的键。默认值： `name`

- **caller_key** <span id="caller_key"/> 日志条目中“caller”字段的键。

- **stacktrace_key** <span id="stacktrace_key"/> 日志条目中 stacktrace 字段的键。

- **line_ending** <span id="line_ending"/> 要使用的换行符。

- **time_format** <span id="time_format"/> 时间戳的格式。
  默认： `wall_milli` 如果格式默认设置为 `console`, `unix_seconds_float` 否则。
  
  可能是以下之一：
  - `unix_seconds_float` 自 Unix 纪元以来的秒数（浮点数）。
  - `unix_milli_float` 自 Unix 纪元以来的毫秒数（浮点数）。
  - `unix_nano` 自 Unix 纪元以来的纳秒数（整数）。
  - `iso8601` 示例： `2006-01-02T15:04:05.000Z0700`
  - `rfc3339` 示例： `2006-01-02T15:04:05Z07:00`
  - `rfc3339_nano` 示例： `2006-01-02T15:04:05.999999999Z07:00`
  - `wall` 示例： `2006/01/02 15:04:05`
  - `wall_milli` 示例： `2006/01/02 15:04:05.000`
  - `wall_nano` 示例： `2006/01/02 15:04:05.000000000`
  - `common_log` 示例： `02/Jan/2006:15:04:05 -0700`
  - 或者，任何兼容的时间格式字符串；详情请参阅 [Go ](https://pkg.go.dev/time#pkg-constants)语言[文档](https://pkg.go.dev/time#pkg-constants)。
  
  请注意，格式字符串中的各个部分是布局的特殊常量；因此 `2006` 是年份， `01` 是月份， `Jan` 表示月份的字符串形式， `02` 表示日期。请勿在格式字符串中使用实际的当前日期数字。

- **time_local** <span id="time_local"/> 使用本地系统时间而非默认的UTC时间进行日志记录。

- **duration_format** <span id="duration_format"/> 时长的格式。

  默认： `seconds`.
  
  可能是以下之一：
  - `s`, `second` 或 `seconds` 已过去的秒数（浮点数）。
  - `ms`, `milli` 或 `millis` 已过去的毫秒数（浮点数）。
  - `ns`, `nano` 或 `nanos` 已过去的纳秒数（整数）。
  - `string` 例如，使用 Go 的内置字符串格式 `1m32.05s` 或者 `6.31ms`.

- **level_format** <span id="level_format"/> 级别格式。

  默认： `color` 如果格式默认设置为 `console`, `lower` 否则。
  
  可能是以下之一：
  - `lower` 小写。
  - `upper` 大写。
  - `color` 大写，并使用 ANSI 颜色。
  

<a id="console"></a>
#### 控制台

控制台编码器在保留部分结构的同时，对日志条目进行了格式化处理，以便于人工阅读。

```caddy-d
format console
```

<span id="json"/>
#### json

将每个日志条目格式化为 JSON 对象。

```caddy-d
format json
```


<a id="filter"></a>
#### 筛选

支持按字段过滤。

```caddy-d
format filter {
	fields {
		<field> <filter> ...
	}
	<field> <filter> ...
	wrap <encode_module> ...
}
```

可以通过使用 `>`表示。换言之，对于类似 `{"a":{"b":0}}`，其内部字段可通过以下方式引用： `a>b`.

以下字段对日志至关重要，且无法进行过滤，因为它们是由底层日志库作为特殊情况添加的： `ts`, `level`, `logger`，以及 `msg`.

指定 `wrap` 是可选的；若省略，将根据当前输出模块是[`stderr`](#stderr)还是[`stdout`](#stdout)，以及是否为交互式终端来选择默认值，如果是交互式终端，则选择[`console`](#console)，否则选择[`json`](#json)。

作为一种快捷方式， `fields` 块可以省略，并直接在 `filter` 块内直接指定过滤器。


以下是可用的筛选条件：

<a id="delete"></a>
##### 删除

标记该字段为跳过编码。

```caddy-d
<field> delete
```


<a id="rename"></a>
##### 重命名

重命名日志字段的键。

```caddy-d
<field> rename <key>
```


<a id="replace"></a>
##### 替换

标记该字段，以便在编码时将其替换为提供的字符串。

```caddy-d
<field> replace <replacement>
```


<a id="ip-mask"></a>
##### 子网掩码

使用 CIDR 掩码对字段中的 IP 地址进行掩码处理，即从左侧开始保留 IP 地址中的位数。如果该字段是一个字符串数组（例如 HTTP 头部），则数组中的每个值都会被掩码处理。该值可以是逗号分隔的 IP 地址字符串。

由于 IPv4 和 IPv6 地址的总位数不同，因此它们的配置是分开的。

最常见的筛选字段通常包括：
- `request>remote_ip` 对于直接连接的客户端
- `request>client_ip` 当配置了[`trusted_proxies`](/docs/caddyfile/options#trusted-proxies)时，针对已解析的“真实客户端”
- `request>headers>X-Forwarded-For` 如果位于反向代理之后

```caddy-d
<field> ip_mask [<ipv4> [<ipv6>]] {
	ipv4 <cidr>
	ipv6 <cidr>
}
```


<a id="query"></a>
##### 查询

用于标记一个字段，以便对其执行一项或多项操作，从而修改 URL 字段中的查询部分。通常情况下，需要进行筛选的字段是 `request>uri`.

```caddy-d
<field> query {
	delete  <key>
	replace <key> <replacement>
	hash    <key>
}
```

可执行的操作包括：

- **delete** 将指定的键从查询中移除。

- **replace** 将给定查询键的值替换为 **replacement**。此功能适用于插入信息遮蔽占位符；你会发现该查询键虽然出现在 URL 中，但其值已被隐藏。

- **hash** 将给定查询键的值替换为该值 SHA-256 哈希值的前 4 个字节（小写十六进制）。此功能可用于对敏感值进行模糊处理，同时仍能识别出每次请求的值是否不同。


<a id="cookie"></a>
##### cookie

标记一个字段以执行一项或多项操作，用于操作 `Cookie` HTTP 头部的值。最常见的情况是，需要过滤的字段是 `request>headers>Cookie`.

```caddy-d
<field> cookie {
	delete  <name>
	replace <name> <replacement>
	hash    <name>
}
```

可执行的操作包括：

- **delete** 会根据名称从请求头中删除指定的 Cookie。

- **replace** 将指定 Cookie 的值替换为 **replacement**。此功能可用于插入遮蔽占位符；您会发现该 Cookie 仍存在于请求头中，但其值已被隐藏。

- **hash** 将指定 Cookie 的值替换为该值 SHA-256 哈希值的前 4 个字节（小写十六进制）。此功能有助于对敏感值进行混淆处理，同时仍能判断每次请求的值是否不同。

如果为同一个 Cookie 名称定义了多个操作，则仅应用第一个操作。


<a id="regexp"></a>
##### 正则表达式

标记该字段，以便在编码时对其应用正则表达式替换。如果该字段是一个字符串数组（例如 HTTP 头部），则数组中的每个值都会应用替换操作。

```caddy-d
<field> regexp <pattern> <replacement>
```

所使用的正则表达式语言是 RE2，该语言已包含在 Go 语言中。请参阅 [RE2 语法参考](https://github.com/google/re2/wiki/Syntax)和 [Go 正则表达式语法概述](https://pkg.go.dev/regexp/syntax)。

在替换字符串中，可以通过 `${group}` 其中 `group` 表示表达式中捕获组的名称或编号。捕获组 `0` 表示完整的正则表达式匹配结果， `1` 是第一个捕获组， `2` 表示第二个捕获组，以此类推。


<a id="hash"></a>
##### 哈希

标记该字段，使其在编码时被该值的 SHA-256 哈希值的前 4 个字节（8 个十六进制字符）所替换。如果该字段是一个字符串数组（例如 HTTP 头部），则数组中的每个值都会被哈希处理。

如果该值属于敏感信息，此方法有助于对其进行遮蔽，同时又能察觉到每次请求的值是否不同。

```caddy-d
<field> hash
```

<a id="append"></a>
#### 追加

将字段追加到所有日志条目中。

```caddy-d
format append {
	fields {
		<field> <value>
	}
	<field> <value>
	wrap <encode_module> ...
}
```

该字段最适用于添加有关生成日志条目的 Caddy 实例的信息，通常可通过环境变量实现。字段值可以是全局占位符（例如 `{env.*}`），但*不*应是按请求生成的占位符，因为日志是在 HTTP 请求上下文之外写入的。

指定 `wrap` 是可选的；若省略，将根据当前输出模块是[`stderr`](#stderr)还是[`stdout`](#stdout)，以及是否为交互式终端来选择默认值，如果是交互式终端，则选择[`console`](#console)，否则选择[`json`](#json)。

该 `fields` 块可以省略，字段可直接在 `append` 块内直接指定字段。



<a id="examples"></a>
## 示例

启用对默认日志记录器的访问日志记录。

换句话说，默认情况下日志会记录到 `stderr`，但可以通过重新配置 `default` logger，使用[`log`全局选项](/docs/caddyfile/options#log)：

```caddy
example.com {
	log
}
```


将日志写入文件（并启用日志轮换功能，该功能默认已启用）：

```caddy
example.com {
	log {
		output file /var/log/access.log
	}
}
```


自定义日志轮换，设置为每天午夜轮换，或在日志文件达到 1 GB 时轮换（以先发生者为准），并保留 5 个轮换后的文件或 30 天的日志：

```caddy
example.com {
	log {
		output file /var/log/access.log {
			roll_at 00:00
			roll_size 1gb
			roll_keep 5
			roll_keep_for 720h
		}
	}
}
```


从日志中删除 `User-Agent` 日志中的请求头：

```caddy
example.com {
	log {
		format filter {
			request>headers>User-Agent delete
		}
	}
}
```


屏蔽多个敏感的 Cookie。（请注意，某些敏感标头默认会以空值进行记录；请参阅[全局选项](/docs/caddyfile/options#log-credentials) [`log_credentials`](/docs/caddyfile/options#log-credentials) 以启用 `Cookie` 标头值）：

```caddy
example.com {
	log {
		format filter {
			request>headers>Cookie cookie {
				replace session REDACTED
				delete secret
			}
		}
	}
}
```


将请求中的远程地址进行掩码处理，对于 IPv4 地址保留前 16 位（即 255.255.0.0），对于 IPv6 地址保留前 32 位。

请注意，从 Caddy v2.7 开始， `remote_ip` 和 `client_ip` 都会被记录，其中 `client_ip` 是配置了[`trusted_proxies`](/docs/caddyfile/options#trusted-proxies)时的“真实IP”：

```caddy
example.com {
	log {
		format filter {
			request>remote_ip ip_mask 16 32
			request>client_ip ip_mask 16 32
		}
	}
}
```


要在所有日志条目末尾追加来自环境变量的服务器 ID，并将其与 `filter` 来删除一个头部：

```caddy
example.com {
	log {
		format append {
			server_id {env.SERVER_ID}
			wrap filter {
				request>headers>Cookie delete
			}
		}
	}
}
```


<span id="wildcard-logs" /> 要为[通配符站点块](/docs/caddyfile/patterns#wildcard-certificates)中的每个子域名生成独立的日志文件，需为每个日志器覆盖 `hostnames` 。此方法使用代码[片段](/docs/caddyfile/concepts#snippets)来避免重复：

```caddy
(subdomain-log) {
	log {
		hostnames {args[0]}
		output file /var/log/{args[0]}.log
	}
}

*.example.com {
	import subdomain-log foo.example.com
	@foo host foo.example.com
	handle @foo {
		respond "foo"
	}

	import subdomain-log bar.example.com
	@bar host bar.example.com
	handle @bar {
		respond "bar"
	}
}
```

<span id="multiple-outputs" /> 若要将某个子域名的访问日志分别写入两个格式不同的文件（一个使用 <a href="https://github.com/caddyserver/transform-encoder">`transform-encoder` 插件 <img src="/old/resources/images/external-link.svg" class="external-link"></a>，另一个使用 [`json`](#json)）。

其工作原理是在 `foo` ，随后通过 `include http.log.access.foo`:

```caddy
{
	log access-formatted {
		include http.log.access.foo
		output file /var/log/access-foo.log
		format transform "{common_log}"
	}

	log access-json {
		include http.log.access.foo
		output file /var/log/access-foo.json
		format json
	}
}

foo.example.com {
	log foo
}
```

<span id="sampling-example" /> 若要通过采样来减少日志量，例如保留每秒的前 5 个请求，之后每 10 个请求中保留 1 个：

```caddy
example.com {
	log {
		sampling {
			interval   1s
			first      5
			thereafter 10
		}
	}
}
```
