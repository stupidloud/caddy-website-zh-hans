---
title: 常見 Caddyfile 模式
---

<a id="common-caddyfile-patterns"></a>
# 常見 Caddyfile 模式

本頁面展示了一些常見用例的完整且最小的 Caddyfile 配置。這些可以作為你自己的 Caddyfile 文檔的一個很好的起點。

這些並非即插即用的解決方案；你必須自定義你的域名、連接埠/通訊端、目錄路徑等。它們旨在說明一些最常見的配置模式。

- [靜態文件伺服器](#static-file-server)
- [反向代理](#reverse-proxy)
- [PHP](#php)
- [重定向 `www.` 子域名](#redirect-www-subdomain)
- [尾部斜線](#trailing-slashes)
- [泛域名證書](#wildcard-certificates)
- [單頁應用 (SPAs)](#single-page-apps-spas)
- [Caddy 代理到另一個 Caddy](#caddy-proxying-to-another-caddy)


<a id="static-file-server"></a>
## 靜態文件伺服器

```caddy
example.com {
	root /var/www
	file_server
}
```

通常，第一行是站點地址。[`root` 指令](/docs/caddyfile/directives/root) 指定了站點根目錄的路徑（`*` 表示匹配所有請求，以便與 [path matcher](/docs/caddyfile/matchers#path-matchers) 區分）&mdash; 如果不是當前工作目錄，請將路徑更改為你的站點路徑。最後，我們啟用 [static file server](/docs/caddyfile/directives/file_server)。



<a id="reverse-proxy"></a>
## 反向代理

代理所有請求：

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

僅代理路徑以 `/api/` 開頭的請求，並為其他所有請求提供靜態文件：

```caddy
example.com {
	root /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

這使用了一個 [request matcher](/docs/caddyfile/matchers#syntax) 來僅匹配以 `/api/` 開頭的請求，並將它們代理到後端。所有其他請求將由 [static file server](/docs/caddyfile/directives/file_server) 從站點 [`root`](/docs/caddyfile/directives/root) 提供服務。這也取決於 `reverse_proxy` 在 [指令順序](/docs/caddyfile/directives#directive-order) 中高於 `file_server` 的事實。

這裡還有更多 [`reverse_proxy` 示例](/docs/caddyfile/directives/reverse_proxy#examples)。



<a id="php"></a>
## PHP

<a id="php-fpm"></a>
### PHP-FPM

在運行 PHP FastCGI 服務的情況下，以下配置適用於大多數現代 PHP 應用：

```caddy
example.com {
	root /srv/public
	encode
	php_fastcgi localhost:9000
	file_server
}
```

相應地自定義站點根目錄；此示例假設你的 PHP 應用的網頁根目錄位於 `public` 目錄中 &mdash; 對磁碟上存在的文件請求將由 [`file_server`](/docs/caddyfile/directives/file_server) 提供服務，其他任何內容都將路由到 `index.php` 由 PHP 應用處理。

有時你可能會使用 unix socket 連接到 PHP-FPM：

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[`php_fastcgi` 指令](/docs/caddyfile/directives/php_fastcgi) 實際上只是 [幾部分配置](/docs/caddyfile/directives/php_fastcgi#expanded-form) 的快捷方式。


<a id="frankenphp"></a>
### FrankenPHP

或者，你可以使用 [FrankenPHP](https://frankenphp.dev/)，它是 Caddy 的一個發行版，使用 CGO（Go 到 C 的綁定）直接調用 PHP。這可能比使用 PHP-FPM 快 4 倍，如果你可以使用 worker 模式，效果會更好。

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

要通過 HTTP 重定向 **添加** `www.` 子域名：

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


要 **移除** 它：

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


要一次性為 **多個域名** 移除它；這使用了 `{labels.*}` placeholders，它們是主機名的部分，從右側開始以 `0` 為索引（例如 `0`=`com`, `1`=`example-one`, `2`=`www`）：

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```



<a id="trailing-slashes"></a>
## 尾部斜線

通常你不需要自己配置這個；[`file_server` 指令](/docs/caddyfile/directives/file_server) 會根據請求的資源分別是目錄還是文件，通過 HTTP 重定向自動添加或移除請求中的尾部斜線。

但是，如果需要，你仍然可以在配置中強制執行尾部斜線。有兩種方法可以做到：內部或外部。

<a id="internal-enforcement"></a>
### 內部強制

這使用了 [`rewrite`](/docs/caddyfile/directives/rewrite) 指令。Caddy 將在內部重寫 URI 以添加或移除尾部斜線：

```caddy
example.com {
	rewrite /add     /add/
	rewrite /remove/ /remove
}
```

使用 rewrite，帶有和不帶有尾部斜線的請求將是相同的。


<a id="external-enforcement"></a>
### 外部強制

這使用了 [`redir`](/docs/caddyfile/directives/redir) 指令。Caddy 將要求瀏覽器更改 URI 以添加或移除尾部斜線：

```caddy
example.com {
	redir /add     /add/
	redir /remove/ /remove
}
```

使用重定向，客戶端將不得不重新發出請求，從而為資源強制執行單個可接受的 URI。



<a id="wildcard-certificates"></a>
## 泛域名證書

對於包括 Let's Encrypt 在內的大多數簽發者，你必須啟用 [ACME DNS 挑戰](/docs/automatic-https#dns-challenge) 才能讓 Caddy 自動化泛域名證書。

啟用 DNS 挑戰後，從 Caddy 2.10 開始，Caddy 會優先選擇已配置或管理的適用泛域名證書，然後再為子域名管理單獨的證書。



如果你需要使用相同的泛域名證書為多個子域名提供服務，處理它們的最佳方法是使用像這樣的 Caddyfile，利用 [`handle` 指令](/docs/caddyfile/directives/handle) 和 [`host` matchers](/docs/caddyfile/matchers#host)：

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

	# 對於其他未處理域名的備用方案
	handle {
		abort
	}
}
```

你必須啟用 [ACME DNS 挑戰](/docs/automatic-https#dns-challenge) 才能讓 Caddy 自動管理泛域名證書。



<a id="single-page-apps-spas"></a>
## 單頁應用 (SPAs)

當網頁執行自己的路由時，伺服器可能會收到大量伺服器端不存在但客戶端可以渲染的頁面請求，前提是提供單個索引文件。以這種方式構建的 Web 應用程序稱為 SPA，即單頁應用。

其核心思想是讓伺服器「嘗試文件」(try files) 以查看請求的文件在伺服器端是否存在，如果不存在，則回退到客戶端執行路由的索引文件（通常使用客戶端 JavaScript）。

一個典型的 SPA 配置通常如下所示：

```caddy
example.com {
	root /srv
	encode
	try_files {path} /index.html
	file_server
}
```

如果你的 SPA 與 API 或其他僅限伺服器端的端點耦合，你將需要使用 `handle` 塊來專門處理它們：

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

如果你的 `index.html` 包含對帶有哈希文件名的 JS/CSS 資產的引用，你可能需要考慮添加一個 `Cache-Control` 標頭來指示客戶端 *不要* 快取它（以便在資產更改時，瀏覽器獲取新的資產）。由於 `try_files` 重寫用於從任何與磁碟上其他文件不匹配的路徑提供 `index.html` 服務，因此你可以使用 `route` 包裝 `try_files`，以便 `header` 處理程序在重寫 *之後* 運行（由於 [指令順序](/docs/caddyfile/directives#directive-order)，它通常會在重寫之前運行）：

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```


<a id="caddy-proxying-to-another-caddy"></a>
## Caddy 代理到另一個 Caddy

如果你有一個可公開訪問的 Caddy 實例（我們稱之為「front」），以及另一個在你的私有網絡中為你的實際應用提供服務的 Caddy 實例（我們稱之為「back」），你可以使用 [`reverse_proxy` 指令](/docs/caddyfile/directives/reverse_proxy) 來傳遞請求。

Front 實例：

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

Back 實例：

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

- 本示例提供兩個不同的域名服務，將兩者都代理到同一個後端 Caddy 實例的 `80` 連接埠。你的後端實例以不同的方式提供這兩個域名的服務，因此它配置了兩個獨立的站點塊。

- 在後端，[`http://`](/docs/caddyfile/concepts#addresses) 用於接收 `80` 連接埠上的 HTTP 請求。前端實例終止 TLS，並且前端和後端之間的流量在私有網絡上，因此無需重新加密。

- 如果需要，你可以在後端實例上使用不同的連接埠（如 `8080`）；只需在後端配置的每個站點地址後附加 `:8080`，或者將 [`http_port` 全域選項](/docs/caddyfile/options#http_port) 設置為 `8080`。

- 在後端，[`trusted_proxies` 全域選項](/docs/caddyfile/options#trusted_proxies) 用於告訴 Caddy 信任前端實例作為代理。這確保了真實的客戶端 IP 得到保留。

- 更進一步，你可以擁有多個後端實例並在它們之間進行 [負載平衡](/docs/caddyfile/directives/reverse_proxy#load-balancing)。你可以在前端實例上使用 [`acme_server`](/docs/caddyfile/directives/acme_server) 設置 mTLS（相互 TLS），使其充當後端實例的 CA（如果前端和後端之間的流量跨越不受信任的網絡，這很有用）。
