---
title: "API"
---

<a id="api"></a>
# API

Caddy 通过一个管理端点进行配置，该端点可通过 HTTP 并使用 <a href="https://en.wikipedia.org/wiki/Representational_state_transfer">REST <img src="/old/resources/images/external-link.svg" class="external-link"></a> API 访问。您可以在 Caddy 的配置文件中[配置此端点](/docs/json/admin/)。

**默认地址： `localhost:2019`**

可以通过设置 `CADDY_ADMIN` 环境变量进行修改。某些安装方式可能会将其设置为其他值。Caddy 配置文件中的地址始终优先于默认地址。

<aside class="tip">
	如果您在服务器上运行不可信代码（天哪 😬），请务必通过隔离进程、修补存在漏洞的程序，并将端点配置为绑定到受限的 Unix 套接字，来保护您的管理端点。
</aside>

进行任何更改后，最新配置都会保存到磁盘（除非[已禁用此功能](/docs/json/admin/config/)）。重启后，您可以通过执行 [`caddy run --resume`](/docs/command-line#caddy-run) 恢复上次运行的配置，这可确保在断电或类似情况下配置的持久性。

若要开始使用该 API，请尝试我们的 [API 教程](/docs/api-tutorial)；如果时间有限，也可以参考我们的 [API 快速入门指南](/docs/quick-starts/api)。

---

- **[POST /load](#post-load)**
  设置或替换当前配置

- **[POST /stop](#post-stop)**
  停止当前配置并退出进程

- **[GET /config/[path]](#get-configpath)**
  将配置导出到指定路径

- **[POST /config/[path]](#post-configpath)**
  设置或替换对象；向数组追加元素
  
- **[PUT /config/[path]](#put-configpath)**
  创建新对象；将其插入数组

- **[PATCH /config/[path]](#patch-configpath)**
  替换现有对象或数组元素

- **[DELETE /config/[path]](#delete-configpath)**
  删除指定路径下的值

- **[在 JSON 中使用 `@id`](#using-id-in-json)**
  轻松浏览配置结构

- **[并行配置更改](#concurrent-config-changes)**
  在对配置进行非同步修改时，请避免发生冲突

- **[POST /adapt](#post-adapt)**
  将配置转换为 JSON 格式，但不执行该配置

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  返回有关特定 [PKI 应用程序](/docs/json/apps/pki/) CA 的信息

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  返回特定 [PKI 应用程序](/docs/json/apps/pki/) CA 的证书链

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  返回已配置代理上游的当前状态


<a id="post-load"></a>
## POST /load

设置 Caddy 的配置，并覆盖任何之前的配置。该操作将阻塞程序，直到重新加载完成或失败。配置更改操作轻量、高效，且不会造成任何停机。如果新配置因任何原因失败，旧配置将无缝回滚，不会造成停机。

该端点通过配置适配器支持多种配置格式。请求的 Content-Type 头字段指定了请求正文中使用的配置格式。通常，该值应为 `application/json` ，这代表 Caddy 的原生配置格式。若要使用其他配置格式，请指定相应的 Content-Type，确保斜杠 / 后的值是所需配置适配器的名称。例如，提交 Caddyfile 时，请使用类似 `text/caddyfile`；若使用 JSON 5，则使用类似 `application/json5`；等等。

如果新配置与当前配置相同，则不会重新加载。若要强制重新加载，请在请求头中设置 `Cache-Control: must-revalidate` 。

### 示例

设置新的活动配置：

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

注意：curl 的 `-d` 参数会移除换行符，因此如果您的配置格式对换行符敏感（例如 Caddyfile），请改用 `--data-binary` 代替：

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


<a id="post-stop"></a>
## POST /stop

优雅地关闭服务器并退出进程。若仅需停止当前配置而不退出进程，请使用 [DELETE /config/。](#delete-configpath)

### 示例

停止该进程：

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


<a id="get-configpath"></a>
## GET /config/[path]

将 Caddy 的当前配置导出到指定路径。返回一个 JSON 主体。

### 示例

导出整个配置并以美观格式显示：

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					]
				}
			}
		}
	}
}</code></pre>

仅导出监听器地址：

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[":443"]</code></pre>



<a id="post-configpath"></a>
## POST /config/[path]

将 Caddy 在指定路径下的配置更改为请求 JSON 主体中的内容。如果目标值是一个数组，POST 操作会追加内容；如果是对象，则会创建或替换该对象。

作为一种特例，如果满足以下条件，可以将多个元素添加到数组中：

1. 路径以...结尾 `/...`
2. 路径中位于 `/...` 指代一个数组
3. 有效载荷是一个数组

在这种情况下，有效载荷数组中的元素将被展开，并分别追加到目标数组中。用 Go 语言的术语来说，这与以下代码效果相同：

```go
baseSlice = append(baseSlice, newElems...)
```

### 示例

添加监听地址：

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

添加多个监听地址：

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

<a id="put-configpath"></a>
## PUT /config/[path]

将指定路径下的 Caddy 配置更改为请求 JSON 正文中的内容。如果目标值是数组中的一个位置（索引），PUT 操作将插入该值；如果是对象，则严格创建一个新值。

### 示例

在第一个插槽中添加一个监听地址：

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


<a id="patch-configpath"></a>
## PATCH /config/[path]

将指定路径下的 Caddy 配置更改为请求 JSON 主体中的内容。PATCH 请求会严格替换现有的值或数组元素。

### 示例

替换监听器地址：

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>



<a id="delete-configpath"></a>
## DELETE /config/[path]

删除指定路径下的 Caddy 配置。DELETE 命令将删除目标值。

### 示例

要卸载当前的全部配置，但让进程继续运行：

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

若要仅停止其中一台 HTTP 服务器：

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


<a id="using-id-in-json"></a>
## 使用 `@id` 在 JSON 中

您可以在 JSON 文档中嵌入 ID，以便更方便地直接访问 JSON 中的相应部分。

只需为某个对象添加一个名为 `"@id"` 字段，并为其指定一个唯一名称。例如，如果你有一个需要频繁访问的反向代理处理程序：

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

要使用它，只需像调用相应的 `/id/` API 端点发送请求，方法与访问对应的 `/config/` 端点的方式向该API 端点发送请求，但无需包含完整的路径。ID 会自动将请求定向到配置中的相应范围。

例如，若要在不提供 ID 的情况下访问反向代理的上游服务器，路径大致如下：

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

但如果使用 ID，路径则变为

```
/id/my_proxy/upstreams
```

这样更容易记住，也更方便手写。

<a id="concurrent-config-changes"></a>
## 并发配置更改

<aside class="tip">

本节适用于所有 `/config/` 端点。此功能尚处于实验阶段，可能会随时变更。

</aside>


Caddy 的配置 API 为单个请求提供了 <a href="https://en.wikipedia.org/wiki/ACID">ACID 保证 <img src="/old/resources/images/external-link.svg" class="external-link"></a>，但如果涉及多个请求的更改未得到妥善同步，则可能会发生冲突或导致数据丢失。

例如，两个客户端可能 `GET /config/foo` 在同一时间，在该范围（配置路径）内进行编辑，然后调用 `POST|PUT|PATCH|DELETE /config/foo/...` ，导致冲突：要么一方覆盖另一方，要么第二个操作会将配置应用到与准备时不同的版本上，从而导致配置处于非预期状态。这是因为这些更改彼此之间并不知道对方的存在。

Caddy 的 API 不支持跨多个请求的事务，而且 HTTP 是一种无状态协议。不过，您可以使用 `Etag` 和 `If-Match` 头部来检测并防止更改冲突，作为一种乐观并发控制机制。如果有多个客户端同时对 Caddy 的 `/config/...` 端点进行未同步修改，这种方法会很有帮助。所有 `GET /config/...` 响应都会包含一个名为 `Etag` 的头部，其值由路径以及该范围内内容的哈希组成（例如 `Etag: "/config/apps/http/servers 65760b8e"`）。只需在后续可变请求中将 `If-Match` 头部设为上一次 `GET` 返回的 `Etag` 即可。

其基本算法如下：

1. 对配置中的任一作用域 `S` 执行 `GET`，并保留响应中的 `Etag` 头部。
2. 根据需要修改返回的配置。
3. 对 `S` 执行 `POST|PUT|PATCH|DELETE`，并将 `If-Match` 请求头设为保存的 `Etag` 值。
4. 如果响应为 HTTP 412（先决条件失败），请从步骤 1 重新开始，或者在重试次数过多后放弃。

该算法允许对 Caddy 的配置进行多次重叠修改，且无需显式同步。其设计确保了对配置不同部分的并行修改无需重试：只有那些涉及配置相同范围的修改才可能导致冲突，从而需要重试。


<a id="post-adapt"></a>
## POST /adapt

将配置转换为 Caddy JSON 格式，而无需加载或运行该配置。如果操作成功，生成的 JSON 文档将作为响应正文返回。

Content-Type 标头用于指定配置格式，其工作原理与 [/load](#post-load) 类似。例如，要适配一个 Caddyfile，请设置 `Content-Type: text/caddyfile`.

只要相应的[配置适配器](/docs/config-adapters)已集成到您的 Caddy 构建中，该端点就能适配任何配置格式。

### 示例

将 Caddyfile 转换为 JSON：

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


<a id="get-pkicaltidgt"></a>
## GET /pki/ca/&lt;id&gt;

根据其 ID 返回有关特定 [PKI 应用程序](/docs/json/apps/pki/) CA 的信息。如果请求的 CA ID 是默认值（`local`），且该 CA 尚未配置，则会对其进行初始化。其他 CA ID 若此前未配置，则会返回错误。

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


<a id="get-pkicaltidgtcertificates"></a>
## GET /pki/ca/&lt;id&gt;/certificates

根据其 ID 返回特定 [PKI 应用程序](/docs/json/apps/pki/) CA 的证书链。如果请求的 CA ID 是默认值（`local`），则该 CA 若尚未配置，将进行初始化。其他 CA ID 若此前未配置，则会返回错误。

该端点由[`caddy trust`](/docs/command-line#caddy-trust)命令在内部使用，用于将证书颁发机构（CA）的根证书安装到系统的信任存储中。

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


<a id="get-reverse-proxyupstreams"></a>
## GET /reverse_proxy/upstreams

返回已配置的反向代理上游（后端）的当前状态，格式为 JSON 文档。

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

JSON 数组中的每一项都是存储在全局上游池中的一个已配置[上游](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/)。

- **地址** 是上游服务器的拨号地址。
- **num_requests** 表示上游服务器当前正在处理的活动请求数量。
- **失败**：当前记录的失败请求数量，由被动健康检查配置决定。

如果您希望判断后端的可用性，则需要将上游的相关属性与您所使用的处理程序配置进行交叉核对。例如，如果您已为代理启用了[被动健康检查](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/)，那么还需考虑 `fails` 和 `num_requests` 的值来判断上游是否被视为可用：检查 `fails` 是否小于您为代理配置的最大失败次数（即 [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/)），并且 `num_requests` 是否小于或等于您为每个上游配置的最大请求数（即整个代理的 [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/)，或单个上游的 [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/)）。
