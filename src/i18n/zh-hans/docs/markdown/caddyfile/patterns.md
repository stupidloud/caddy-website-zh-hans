---
title: "常见的 Caddyfile 模式"
---

# 常见的 Caddyfile 模式

本页面展示了适用于常见使用场景的几个完整且精简的 Caddyfile 配置示例。这些示例可作为您编写 Caddyfile 文档时的有用起点。

这些并非开箱即用的解决方案；您需要自定义域名、端口/套接字、目录路径等。它们旨在说明一些最常见的配置模式。

- [静态文件服务器](#static-file-server)
- [反向代理](#reverse-proxy)
- [PHP](#php)
- [将 `www.` 子域名重定向](#redirect-www-subdomain)
- [尾随斜杠](#trailing-slashes)
- [通配符证书](#wildcard-certificates)
- [单页应用程序（SPAs）](#single-page-apps-spas)
- [Caddy 作为代理连接到另一个 Caddy](#caddy-proxying-to-another-caddy)

<a id="static-file-server"></a>
## 静态文件服务器

```caddy
example.com {
	root /var/www
	file_server
}
```

与往常一样，第一行是网站地址。[`root`指令](/docs/caddyfile/directives/root)指定了网站根目录的路径（该 `*` 表示匹配所有请求，以此与[路径匹配器](/docs/caddyfile/matchers#path-matchers)区分开来）——如果当前工作目录不是您的网站路径，请将其更改为您的网站路径。最后，我们启用[静态文件服务器](/docs/caddyfile/directives/file_server)。


<a id="reverse-proxy"></a>
## 反向代理

将所有请求通过代理：

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

仅代理路径以 `/api/` ，其余情况均返回静态文件：

```caddy
example.com {
	root /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

这使用了一个[请求匹配器](/docs/caddyfile/matchers#syntax)，仅匹配以 `/api/` 开头的请求，并将它们代理到后端。所有其他请求将由[静态文件服务器](/docs/caddyfile/directives/file_server)通过 [`root`](/docs/caddyfile/directives/root) 网站提供服务。这也取决于 `reverse_proxy` 在[指令顺序](/docs/caddyfile/directives#directive-order)中优先级高于 `file_server`。

还有更多 [`reverse_proxy` 示例](/docs/caddyfile/directives/reverse_proxy#examples)。


<a id="php"></a>
## PHP

<a id="php-fpm"></a>
### PHP-FPM

在运行 PHP FastCGI 服务的情况下，对于大多数现代 PHP 应用程序，如下所示的配置是可行的：

```caddy
example.com {
	root /srv/public
	encode
	php_fastcgi localhost:9000
	file_server
}
```

请根据实际情况自定义网站根目录；本示例假设您的 PHP 应用程序的 Web 根目录位于 `public` 目录中——针对磁盘上已存在文件的请求将通过 [`file_server`](/docs/caddyfile/directives/file_server) 处理，其余所有请求都将路由至 `index.php` 由 PHP 应用程序处理。

有时您可以使用 Unix 套接字连接到 PHP-FPM：

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[`php_fastcgi` 指令](/docs/caddyfile/directives/php_fastcgi)实际上只是对[几项配置的](/docs/caddyfile/directives/php_fastcgi#expanded-form)简写。


<a id="frankenphp"></a>
### FrankenPHP

此外，您还可以使用 [FrankenPHP](https://frankenphp.dev/)，这是一个基于 Caddy 的发行版，它通过 CGO（Go 到 C 绑定）直接调用 PHP。其运行速度最高可达 PHP-FPM 的 4 倍，若能启用 worker 模式，性能表现将更为出色。

```caddy
{
    frankenphp
    order php_server before file_server
}

example.com {
	root /srv/public
    encode zstd br gzip
    php_server
}
```

<a id="redirect-www-subdomain"></a>
## 重定向 `www.` 子域名

要**添加** `www.` 子域名并设置 HTTP 重定向：

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


要**删除**它：

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


若要一次性为**多个域名**移除该部分，需使用 `{labels.*}` 占位符，即主机名的各部分，`0` 从右向左索引（例如 `0`=`com`，`1`=`example-one`，`2`=`www`）：

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```


<a id="trailing-slashes"></a>
## 尾随斜杠

通常您无需手动配置此项；[`file_server`指令](/docs/caddyfile/directives/file_server)会通过HTTP重定向自动在请求中添加或移除尾部斜杠，具体取决于所请求的资源是目录还是文件。

不过，如果确实有必要，你仍然可以通过配置强制使用尾部斜杠。实现方法有两种：内部实现或外部实现。

<a id="internal-enforcement"></a>
### 内部执行

这使用了[`rewrite`](/docs/caddyfile/directives/rewrite)指令。Caddy会在内部重写URI，以添加或移除尾部斜杠：

```caddy
example.com {
	rewrite /add     /add/
	rewrite /remove/ /remove
}
```

通过重写规则，无论请求中是否包含尾部斜杠，都会被视为相同的请求。


<a id="external-enforcement"></a>
### 外部执行

此处使用了[`redir`](/docs/caddyfile/directives/redir)指令。Caddy会要求浏览器修改URI，以添加或移除末尾的斜杠：

```caddy
example.com {
	redir /add     /add/
	redir /remove/ /remove
}
```

通过重定向，客户端将不得不重新发送请求，从而确保资源仅有一个可接受的 URI。


<a id="wildcard-certificates"></a>
## 通配符证书

对于包括 Let's Encrypt 在内的绝大多数证书颁发机构，您必须启用 [ACME DNS 验证](/docs/automatic-https#dns-challenge)，才能让 Caddy 自动生成通配符证书。

从 Caddy 2.10 版本开始，启用 DNS 验证后，Caddy 会优先使用已配置或管理的适用通配符证书，而非为子域名单独管理证书。



如果您需要使用同一张通配符证书来托管多个子域名，最佳做法是编写如下所示的 Caddyfile，利用 [`handle`](/docs/caddyfile/directives/handle)指令和 [`host` 匹配器](/docs/caddyfile/matchers#host)：

```caddy
*.example.com {
	tls {
		dns <provider_name> [<params...>]
	}

	@foo host foo.example.com
	handle @foo {
		respond "Foo!"
	}

	@bar host bar.example.com
	handle @bar {
		respond "Bar!"
	}

	# 其他未处理的域名会走到这里，作为兜底
	handle {
		abort
	}
}
```

您必须启用 [ACME DNS 验证](/docs/automatic-https#dns-challenge)，才能让 Caddy 自动管理通配符证书。


<a id="single-page-apps-spas"></a>
## 单页应用程序（SPAs）

当网页自行处理路由时，服务器可能会收到大量针对服务器端不存在的页面的请求，但只要返回单一的索引文件，这些页面在客户端仍可渲染。采用这种架构的 Web 应用程序被称为 SPA（单页应用程序）。

其核心思想是让服务器“尝试加载文件”，以检查请求的文件是否存在于服务器端；如果不存在，则回退到一个索引文件，由客户端进行路由处理（通常使用客户端 JavaScript）。

典型的 SPA 配置通常如下所示：

```caddy
example.com {
	root /srv
	encode
	try_files {path} /index.html
	file_server
}
```

如果您的 SPA 与 API 或其他仅限服务端的端点相关联，您可能需要使用 `handle` 块来专门处理它们：

```caddy
example.com {
	encode

	handle /api/* {
		reverse_proxy backend:8000
	}

	handle {
		root /srv
		try_files {path} /index.html
		file_server
	}
}
```

如果您的 `index.html` 包含对文件名经过哈希处理的 JS/CSS 资源的引用，建议考虑添加一个 `Cache-Control` 标头，以指示客户端*不要*缓存该文件（这样当资源发生变化时，浏览器会获取新文件）。由于 `try_files` 重写规则用于从 `index.html` ，使其能够从任何不匹配磁盘上其他文件的路径进行服务，因此您可以将 `try_files` 包裹 `route` ，以便 `header` 处理程序在重写之后运行（通常由于[指令顺序](/docs/caddyfile/directives#directive-order)，它会在重写之前运行）：

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```

<a id="caddy-proxying-to-another-caddy"></a>
## Caddy 作为代理连接到另一个 Caddy

如果你有一个可公开访问的 Caddy 实例（我们称之为“前端”），以及另一个位于私有网络中的 Caddy 实例（我们称之为“后端”）来托管你的实际应用，你可以使用 [`reverse_proxy` 指令](/docs/caddyfile/directives/reverse_proxy)将请求转发过去。

示例：

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

后端实例：

```caddy
{
	servers {
		trusted_proxies static private_ranges
	}
}

http://foo.example.com {
	reverse_proxy foo-app:8080
}

http://bar.example.com {
	reverse_proxy bar-app:9000
}
```

- 此示例为两个不同的域名提供服务，并将两者都代理到同一后端 Caddy 实例，端口为 `80`。您的后端实例以不同的方式为这两个域名提供服务，因此配置了两个独立的站点块。

- 在后端，[`http://`](/docs/caddyfile/concepts#addresses) 用于在端口 `80`。前端实例负责终止 TLS 连接，且前端与后端之间的流量在私有网络内传输，因此无需重新加密。

- 如有需要，您可以使用其他端口，例如 `8080` ；只需在后端实例的配置中，将 `:8080` ，或者将[全局选项`http_port`](/docs/caddyfile/options#http_port)设置为 `8080`.

- 在服务器端，通过使用[全局选项](/docs/caddyfile/options#trusted_proxies) [`trusted_proxies`](/docs/caddyfile/options#trusted_proxies)，可指示 Caddy 信任前端实例作为代理。这确保了真实客户端 IP 地址得以保留。

- 进一步而言，您可以部署多个后端实例，并在它们之间进行[负载均衡](/docs/caddyfile/directives/reverse_proxy#load-balancing)。您可以在前端实例上配置[`acme_server`](/docs/caddyfile/directives/acme_server)来设置mTLS（双向TLS），使其充当后端实例的CA（如果前端与后端之间的流量需要穿越不可信网络，此配置将非常有用）。
