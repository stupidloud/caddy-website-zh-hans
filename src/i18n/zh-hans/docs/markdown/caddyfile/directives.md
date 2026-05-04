---
title: "Caddyfile 指令"
---

<style>
#directive-table table {
	margin: 0 auto;
	overflow: hidden;
}

#directive-table tr:hover {
	background: rgba(109, 226, 255, 0.11);
}

#directive-table tr td:first-child {
	position: relative;
}

#directive-table a:before {
	content: '';
	position: absolute;
	left: 0;
	top: 0;
	bottom: 0;
	display: block;
	width: 100vw;
}
</style>

# Caddyfile 指令

指令是出现在站点[块](/docs/caddyfile/concepts#blocks)中的功能关键字。有时，它们可能会开启自己的代码块，这些代码块可以包含*子指令*，但除非另有说明，否则指令**不能**在其他指令内部使用。例如，你不能在 `file_server` 块内使用 `basic_auth`，因为 `file_server` 不具备身份验证功能。不过，你*可以*在 `handle` 和 `route` 这类特殊指令块中使用某些指令，因为这些块专门用于聚合 HTTP 处理程序指令。

- [语法](#syntax)
- [指令顺序](#directive-order)
- [排序算法](#sorting-algorithm)

以下指令是 Caddy 的标准配置，可在 HTTP Caddyfile 中使用：

<div id="directive-table">

指令 | 描述
----------|------------
**[abort](/docs/caddyfile/directives/abort)** | 中止 HTTP 请求
**[acme_server](/docs/caddyfile/directives/acme_server)** | 一个嵌入式 ACME 服务器
**[basic_auth](/docs/caddyfile/directives/basic_auth)** | 强制执行 HTTP 基本身份验证
**[bind](/docs/caddyfile/directives/bind)** | 自定义服务器的套接字地址
**[encode](/docs/caddyfile/directives/encode)** | 对响应进行编码（通常是压缩）
**[error](/docs/caddyfile/directives/error)** | 触发错误
**[file_server](/docs/caddyfile/directives/file_server)** | 从磁盘提供文件
**[forward_auth](/docs/caddyfile/directives/forward_auth)** | 将身份验证委托给外部服务
**[fs](/docs/caddyfile/directives/fs)** | 设置用于文件 I/O 的文件系统
**[handle](/docs/caddyfile/directives/handle)** | 一组互斥的指令
**[handle_errors](/docs/caddyfile/directives/handle_errors)** | 定义用于处理错误的路由
**[handle_path](/docs/caddyfile/directives/handle_path)** | 与 handle 类似，但会去除路径前缀
**[header](/docs/caddyfile/directives/header)** | 设置或移除响应头
**[import](/docs/caddyfile/directives/import)** | 包含代码片段或文件
**[intercept](/docs/caddyfile/directives/intercept)** | 拦截其他处理程序编写的响应
**[invoke](/docs/caddyfile/directives/invoke)** | 调用指定路由
**[log](/docs/caddyfile/directives/log)** | 启用访问/请求日志记录
**[log_append](/docs/caddyfile/directives/log_append)** | 将字段追加到访问日志中
**[log_skip](/docs/caddyfile/directives/log_skip)** | 跳过匹配请求的访问日志记录
**[log_name](/docs/caddyfile/directives/log_name)** | 覆盖要写入的日志器名称
**[map](/docs/caddyfile/directives/map)** | 将一个输入值映射到一个或多个输出
**[method](/docs/caddyfile/directives/method)** | 在内部更改 HTTP 方法
**[metrics](/docs/caddyfile/directives/metrics)** | 配置 Prometheus 指标发布端点
**[php_fastcgi](/docs/caddyfile/directives/php_fastcgi)** | 通过 FastCGI 提供 PHP 网站服务
**[push](/docs/caddyfile/directives/push)** | 使用 HTTP/2 服务器推送将内容推送至客户端
**[redir](/docs/caddyfile/directives/redir)** | 向客户端发送 HTTP 重定向
**[request_body](/docs/caddyfile/directives/request_body)** | 处理请求正文
**[request_header](/docs/caddyfile/directives/request_header)** | 操作请求头
**[respond](/docs/caddyfile/directives/respond)** | 向客户端发送一个硬编码的响应
**[reverse_proxy](/docs/caddyfile/directives/reverse_proxy)** | 一个功能强大且可扩展的反向代理
**[rewrite](/docs/caddyfile/directives/rewrite)** | 在内部重写请求
**[root](/docs/caddyfile/directives/root)** | 设置网站根目录的路径
**[route](/docs/caddyfile/directives/route)** | 一组被视为单一整体的指令
**[templates](/docs/caddyfile/directives/templates)** | 在响应中执行模板
**[tls](/docs/caddyfile/directives/tls)** | 自定义 TLS 设置
**[tracing](/docs/caddyfile/directives/tracing)** | 与 OpenTelemetry 追踪的集成
**[try_files](/docs/caddyfile/directives/try_files)** | 基于文件是否存在的重写规则
**[uri](/docs/caddyfile/directives/uri)** | 操作 URI
**[vars](/docs/caddyfile/directives/vars)** | 设置任意变量

</div>

## 语法
<a id="syntax"></a>
## 语法

每条指令的语法大致如下：

```caddy-d
directive [<matcher>] <args...> {
	subdirective [<args...>]
}
```

这些 `<carets>` 表示将被实际值替换的标记。

这些 `[brackets]` 表示可选参数。

省略号 `...` 表示后续内容，即一个或多个参数或行。

除非另有说明，子指令通常是可选的，即使它们未出现在 `[brackets]` 中也是如此。


### 匹配器

大多数（但并非全部）指令都支持[匹配器标记](/docs/caddyfile/matchers#syntax)，这些标记可用于过滤请求。匹配器标记通常是可选的。如果某条指令的语法中包含以下内容，则说明该指令支持匹配器：

```caddy-d
[<matcher>]
```

由于所有匹配器标记的工作原理相同，为避免重复，各页面将不再赘述匹配器标记的各种用法。有关语法的详细说明，请参阅[匹配器文档](/docs/caddyfile/matchers)。


<a id="directive-order"></a>
## 指令顺序

许多指令会操作 HTTP 处理程序链。这些指令的评估顺序至关重要，因此 Caddy 中硬编码了一个默认顺序。

您可以通过使用[全局选项](/docs/caddyfile/options#order) [`order`](/docs/caddyfile/options#order) 或[指令](/docs/caddyfile/directives/route) [`route`](/docs/caddyfile/directives/route) 来覆盖/自定义此排序顺序。

```caddy-d
tracing

map
vars
fs
root
log_append
log_skip
log_name

header
copy_response_headers # only in reverse_proxy's handle_response block
request_body

redir

# incoming request manipulation
method
rewrite
uri
try_files

# middleware handlers; some wrap responses
basic_auth
forward_auth
request_header
encode
push
intercept
templates

# special routing & dispatching directives
invoke
handle
handle_path
route

# handlers that typically respond to requests
abort
error
copy_response # only in reverse_proxy's handle_response block
respond
metrics
reverse_proxy
php_fastcgi
file_server
acme_server
```



<a id="sorting-algorithm"></a>
## 排序算法

为了便于使用，Caddyfile 适配器会根据以下规则对指令进行排序：

- 名称不同的指令会根据其在[默认顺序](#directive-order)中的位置进行排序。可以通过[全局选项 ](/docs/caddyfile/options)[`order`](/docs/caddyfile/options) 覆盖默认顺序。插件中的指令*没有*默认顺序，因此应使用全局选项 [`order`](/docs/caddyfile/options) 或指令 [`route`](/docs/caddyfile/directives/route) 来设置顺序。

- 同名的指令会根据其[匹配器](/docs/caddyfile/matchers#syntax)进行排序。

  - 优先级最高的是仅包含一个[路径匹配器的](/docs/caddyfile/matchers#path-matchers)指令。

    路径匹配器按特异性排序，从特异性最高到最低。
	
	通常，这是通过按路径匹配器的长度进行排序来实现的。有一种例外情况：如果路径以 `*` ，且两个匹配器的路径在其他方面完全相同，则不带 `*` 的匹配器被视为更具体，排序优先级更高。

    例如：
    - `/foobar` 比……更具体 `/foo`
    - `/foo` 比……更具体 `/foo*`
    - `/foo/*` 比……更具体 `/foo*`

  - 接下来按其在 Caddyfile 中的出现顺序，对包含其他匹配器的指令进行排序。

    这包括具有多个值的路径匹配器和[命名匹配器](/docs/caddyfile/matchers#named-matchers)。

  - 没有匹配器（即匹配所有请求）的指令会被排在最后。

- [`vars`](/docs/caddyfile/directives/vars) 指令的匹配器排序顺序被反转，因为它涉及设置可能相互覆盖的值，因此最具体的匹配器应最后进行评估。

- [`route`](/docs/caddyfile/directives/route) 指令的内容会忽略上述所有规则，并保留指令出现的顺序。
