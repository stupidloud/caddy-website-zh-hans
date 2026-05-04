---
title: "php_fastcgi（Caddyfile 指令）"
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# php_fastcgi

一个具有特定配置的指令，用于将请求代理到 PHP FastCGI 服务器（如 php-fpm）。

- [语法](#syntax)
- [展开形式](#expanded-form)
  - [说明](#explanation)
- [示例](#examples)

Caddy 的 [`reverse_proxy`](reverse_proxy) 指令能够托管任何 FastCGI 应用程序，但该指令是专门为 PHP 应用程序设计的。该指令提供了一种便捷的快捷方式，可以替代[冗长的配置](#expanded-form)。

它默认将位于站点根目录下的任何 `index.php` 位于站点根目录下的文件将充当路由器。如果不需要这种行为，请重新配置[`try_files`子指令](#try_files)以修改默认的重写行为，或者以[扩展形式](#expanded-form)为基础并根据您的需求进行自定义。

除了下面列出的子指令外，该指令还支持 [`reverse_proxy`](reverse_proxy#syntax) 中的所有子指令。例如，您可以启用负载均衡和健康检查。

**大多数现代 PHP 应用程序无需额外的子指令或自定义设置即可正常运行。** 子指令通常仅在某些特殊情况下或处理旧版 PHP 应用程序时才会用到。

<a id="syntax"></a>
<span id="syntax"/>
## 语法

```caddy-d
php_fastcgi [<matcher>] <php-fpm_gateways...> {
	root <path>
	split <substrings...>
	index <filename>|off
	try_files <files...>
	env [<key> <value>]
	resolve_root_symlink
	capture_stderr
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>

	<any other reverse_proxy subdirectives...>
}
```

- **<php-fpm_gateways...>** 是 FastCGI 服务器的[地址](/docs/conventions#network-addresses)。通常为 TCP 套接字或 Unix 套接字文件。

- **root** <span id="root"/> 将根目录设置为该网站。建议始终将 [`root` 指令](root)与 `php_fastcgi` 一起使用，但当您的 PHP-FPM 上游服务器使用的根目录与 Caddy 不同时，覆盖此设置可能会很有用（参见[示例](#docker)）。若已使用 [`root` 指令](root)，则默认采用其值；否则默认使用 Caddy 的当前工作目录。

- **split** <span id="split"/> 用于设置将 URI 分割为两部分的子字符串。第一个匹配的子字符串将用于从路径中分离出“路径信息”。第一部分的末尾将附加该匹配的子字符串，并被视为实际资源（CGI 脚本）的名称。第二部分将被设置为 PATH_INFO，供 CGI 脚本使用。默认值： `.php`

- **index** <span id="index"/> 指定要作为目录索引文件的文件名。这会影响[展开形式](#expanded-form)中的文件匹配器。默认值： `index.php`。可设置为 `off` 以禁用重写回退到 `index.php` 。

- <a id="try_files"></a>**try_files** <span id="try_files"/> 用于覆盖默认的 try-files 重写规则。详情请参阅 [`try_files` 指令](try_files)。默认值： `{path} {path}/index.php index.php`.

- **env** <span id="env"/> 将指定的值设置为额外的环境变量。可多次指定以设置多个环境变量。默认情况下，所有相关的 FastCGI 环境变量（包括 HTTP 头部）均已设置，但您可以根据需要添加或覆盖这些变量。 

- **resolve_root_symlink** <span id="resolve_root_symlink"/> 当[`root`](#root)目录是一个符号链接（symlink）时，此选项可将其解析为实际路径。这有时会被用作部署策略，只需将符号链接指向另一个目录中的新版本即可。默认情况下此选项处于禁用状态，以避免重复的系统调用。

- **capture_stderr** <span id="capture_stderr"/> 用于捕获并记录上游 FastCGI 服务器发送的任何消息 `stderr`。日志记录默认在 `WARN` 级别。如果响应包含 `4xx` 或 `5xx` 状态，则将改用 `ERROR` 级别。默认情况下， `stderr` 会被忽略。

- **dial_timeout** <span id="dial_timeout"/> 是一个[时间值](/docs/conventions#durations)，用于设置连接上游套接字时的等待时长。默认值： `3s`.

- **read_timeout** <span id="read_timeout"/> 是一个[时间值](/docs/conventions#durations)，用于设置从 FastCGI 上游读取数据时的等待时长。默认：无超时。

- **write_timeout** <span id="write_timeout"/> 是一个[时间值](/docs/conventions#durations)，用于设置向 FastCGI 上游发送数据时的等待时长。默认：无超时。


由于该指令是反向代理的一个具有特定实现方式的封装，您可以使用[`reverse_proxy`](reverse_proxy#syntax)中的任何子指令对其进行自定义。


<a id="expanded-form"></a>
<span id="expanded-form"/>
## 展开形式

该 `php_fastcgi` 指令（不含子指令）与以下配置效果相同。大多数现代 PHP 应用程序都能很好地适配此预设。如果您的应用程序无法适配，请随意参考此配置并根据需要进行自定义，而无需使用 `php_fastcgi` 快捷方式。

```caddy-d
route {
	# 为目录请求添加尾部斜杠
	# 如果 try_files 列表中不包含 "{http.request.uri.path}/index.php"，则自动禁用此重定向
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# 如果请求的文件不存在，尝试 index 文件，并假设 index.php 始终存在
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# 将 PHP 文件代理到 FastCGI 处理程序
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```

<a id="explanation"></a>
<span id="explanation"/>
### 说明

- 第一部分讨论请求路径的规范化。其目的是确保指向磁盘上某个目录的请求，其请求路径末尾确实包含斜杠 `/` ，从而确保针对该目录的请求仅有一个有效的 URL。

  只有当 `try_files` 子指令包含 `{path}/index.php` （默认情况）。

  这是通过使用一个请求匹配器来实现的，该匹配器仅匹配那些*不*以斜杠结尾的请求，并将这些请求映射到磁盘上一个包含 `index.php` 文件，若匹配成功，则执行 HTTP 308 重定向并添加尾部斜杠。例如，它会将路径为 `/foo` 重定向至 `/foo/` （在路径末尾添加 `/`，以将路径规范化为目录路径），前提是 `/foo/index.php` 文件存在于磁盘上。

- 下一节将介绍如何根据磁盘上是否存在匹配文件来执行路径重写。这还会产生一个副作用，即记住路径中 `.php` （如果请求路径中包含 `.php` ）。这对 Caddy 正确设置 FastCGI 环境变量至关重要。

  - 首先，它会检查 `{path}` 是否为磁盘上已存在的文件。如果是，则重写到该路径。这实际上会跳过后续步骤，并确保针对磁盘上*确实存在*的文件的请求不会被重写（参见下文后续步骤）。因此，例如，如果你有一个 `/js/app.js` 文件，那么针对该路径的请求将保持不变。

  - 其次，它会检查 `{path}/index.php` 是否为磁盘上已存在的文件。如果是，则重写到该路径。对于指向目录的请求，例如 `/foo/` ，系统将查找 `/foo//index.php` （该路径会被规范化为 `/foo/index.php`），并重写请求至该路径（若其存在）。若您在 Web 根目录的子目录中运行了另一个 PHP 应用程序，这种行为有时会派上用场。

  - 最后，它会始终重写为 `index.php` （对于现代 PHP 应用而言，该文件几乎总是存在的）。这使得您的 PHP 应用能够通过使用 `index.php` 脚本作为入口点。

- 最后，这一节负责将请求代理到您的 PHP FastCGI（或 PHP-FPM）服务，从而实际运行您的 PHP 代码。请求匹配器仅会匹配以 `.php`，因此，任何*不是* PHP 脚本且*确实*存在于磁盘上的文件，都不会由该指令处理，而是会直接被忽略。

仅使用 `php_fastcgi` 指令通常仅靠它本身是不够的。它几乎总是应与[`root`指令](root)配合使用，以设置文件在磁盘上的位置（对于现代 PHP 应用程序，这可能是 `/var/www/html/public`，其中 `public` 目录即存放您的 `index.php`），并配合[`file_server`指令](file_server)来提供静态文件（如JS、CSS、图片等），这些文件若未被该指令处理，则会由后者负责。



<a id="examples"></a>
<span id="examples"/>
## 示例

将所有 PHP 请求代理到监听在 `127.0.0.1:9000`:

```caddy-d
php_fastcgi 127.0.0.1:9000
```

同上，但仅适用于 `/blog/`:

```caddy-d
php_fastcgi /blog/* localhost:9000
```

当使用通过 Unix 套接字监听的 PHP-FPM 时：

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[`root`指令](root)几乎总是用于指定包含PHP脚本的目录，而[`file_server`指令](file_server)则用于提供静态文件：

```caddy
example.com {
	root /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<span id="docker"/> 使用 Caddy 托管多个 PHP 应用时，每个应用的 Web 根目录必须不同，这样 Caddy 才能分别读取和提供静态文件，并检测 PHP 文件是否存在。

如果您使用的是 Docker，通常您的 PHP-FPM 容器会将文件挂载到同一个根目录下。在这种情况下，解决方案是将文件挂载到 Caddy 容器的不同目录中，然后使用 [`root`](#root) [子指令](#root)为每个容器设置根目录：

```caddy
app1.example.com {
	root /srv/app1/public
	php_fastcgi app1:9000 {
		root /var/www/html/public
	}
	file_server
}

app2.example.com {
	root /srv/app2/public
	php_fastcgi app2:9000 {
		root /var/www/html/public
	}
	file_server
}
```

对于不使用 `index.php` 作为入口点的 PHP 网站，您可以改用抛出 `404` 错误。该错误可通过[`handle_errors`指令](handle_errors)进行捕获和处理：

```caddy
example.com {
	php_fastcgi localhost:9000 {
		try_files {path} {path}/index.php =404
	}

	handle_errors {
		respond "{err.status_code} {err.status_text}"
	}
}
```
