---
title: php_fastcgi (Caddyfile 指令)
---

<script>
ready(function() {
	// 如果在頁面中找到匹配的錨點標籤，我們將添加指向所有子指令的鏈接。
	addLinksToSubdirectives();
});
</script>

<a id="php-fastcgi"></a>
# php_fastcgi

一個具有特定見解的指令，用於將請求代理到 PHP FastCGI 伺服器，例如 php-fpm。

- [語法](#syntax)
- [展開形式](#expanded-form)
  - [詳細說明](#explanation)
- [範例](#examples)

Caddy 的 [`reverse_proxy`](reverse_proxy) 能夠為任何 FastCGI 應用程序提供服務，但此指令是專門為 PHP 應用程序量身定制的。此指令是一個方便的捷徑，取代了 [較長的配置](#expanded-form)。

它預期站點根目錄下的任何 `index.php` 都充當路由。如果不希望這樣，請重新配置 [`try_files` 子指令](#try_files) 以修改默認的重寫行為，或者以 [展開形式](#expanded-form) 為基礎並根據您的需求進行自定義。

除了下面列出的子指令外，此指令還支持 [`reverse_proxy`](reverse_proxy#syntax) 的所有子指令。例如，您可以啟用負載平衡和健康檢查。

**大多數現代 PHP 應用程序在沒有額外子指令或自定義的情況下都能正常工作。** 子指令通常僅用於某些邊緣情況或舊版 PHP 應用程序。

<a id="syntax"></a>
## 語法

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

- **<php-fpm_gateways...>** 是 FastCGI 伺服器的 [地址](/docs/conventions#network-addresses)。通常是 TCP 套接字或 unix 套接字文件。

- **root** <span id="root"/> 設置站點的根文件夾。建議始終將 [`root` 指令](root) 與 `php_fastcgi` 結合使用，但當您的 PHP-FPM 上游使用與 Caddy 不同的根目錄時，覆蓋此設置會很有用（參見 [範例](#docker)）。如果已使用 [`root` 指令](root)，則默認為其值，否則默認為 Caddy 的當前工作目錄。

- **split** <span id="split"/> 設置用於將 URI 分割為兩部分的子字符串。第一個匹配的子字符串將用於從路徑中分割 "path info"。第一部分以匹配的子字符串為後綴，並將被視為實際資源（CGI 腳本）名稱。第二部分將設置為 PATH_INFO 供 CGI 腳本使用。默認值：`.php`

- **index** <span id="index"/> 指定要視為目錄索引文件的文件名。這會影響 [展開形式](#expanded-form) 中的文件 matcher。默認值：`index.php`。可以設置為 `off` 以在找不到匹配文件時禁用重寫回退到 `index.php`。

- **try_files** <span id="try_files"/> 指定對默認 try-files 重寫的覆蓋。有關詳細信息，請參見 [`try_files` 指令](try_files)。默認值：`{path} {path}/index.php index.php`。

- **env** <span id="env"/> 將額外的環境變量設置為給定值。可以多次指定以設置多個環境變量。默認情況下，所有相關的 FastCGI 環境變量都已設置（包括 HTTP 標頭），但您可以根據需要添加或覆蓋變量。

- **resolve_root_symlink** <span id="resolve_root_symlink"/> 當 [`root`](#root) 目錄是符號鏈接（symlink）時，啟用將其解析為其實際值。這有時被用作一種部署策略，通過簡單地交換符號鏈接以指向另一個目錄中的新版本。默認情況下禁用以避免重複的系統調用。

- **capture_stderr** <span id="capture_stderr"/> 啟用捕獲並記錄上游 fastcgi 伺服器在 `stderr` 上發送的任何消息。默認情況下在 `WARN` 級別進行記錄。如果響應具有 `4xx` 或 `5xx` 狀態，則將改用 `ERROR` 級別。默認情況下忽略 `stderr`。

- **dial_timeout** <span id="dial_timeout"/> 是一個 [持續時間值](/docs/conventions#durations)，設置連接到上游套接字時等待多長時間。默認值：`3s`。

- **read_timeout** <span id="read_timeout"/> 是一個 [持續時間值](/docs/conventions#durations)，設置從 FastCGI 上游讀取時等待多長時間。默認值：無超時。

- **write_timeout** <span id="write_timeout"/> 是一個 [持續時間值](/docs/conventions#durations)，設置向 FastCGI 上游發送時等待多長時間。默認值：無超時。

由於此指令是反向代理的一個具有特定見解的封裝，因此您可以使用 [`reverse_proxy`](reverse_proxy#syntax) 的任何子指令來對其進行自定義。

<a id="expanded-form"></a>
## 展開形式

`php_fastcgi` 指令（不帶子指令）與以下配置相同。大多數現代 PHP 應用程序在此預設下運行良好。如果您的應用程序不是這樣，請隨意參考此配置並根據需要進行自定義，而不是使用 `php_fastcgi` 捷徑。

```caddy-d
route {
	# 為目錄請求添加尾隨斜槓
	# 如果 "{http.request.uri.path}/index.php" 不在 try_files 列表中，則此重定向將自動禁用
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# 如果請求的文件不存在，嘗試索引文件並假設 index.php 始終存在
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# 將 PHP 文件代理到 FastCGI 響應器
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```

<a id="explanation"></a>
### 詳細說明

- 第一部分處理請求路徑的規範化。目標是確保針對磁盤上目錄的請求實際上在請求路徑中添加了尾隨斜槓 `/`，以便該目錄的請求僅有一個有效的 URL。

  僅當 `try_files` 子指令包含 `{path}/index.php`（默認值）時，才會進行此規範化。

  這是通過使用一個請求 matcher 來執行的，該 matcher 僅匹配 *不* 以斜槓結尾的請求，並且這些請求映射到磁盤上包含 `index.php` 文件的目錄，如果匹配，則執行附加了尾隨斜槓的 HTTP 308 重定向。因此，例如，如果磁盤上存在 `/foo/index.php`，它會將路徑為 `/foo` 的請求重定向到 `/foo/`（附加一個 `/`，以使路徑規範化為目錄）。

- 下一部分處理基於磁盤上是否存在匹配文件來執行路徑重寫。這還有一個副作用，即記住 `.php` 之後的路徑部分（如果請求路徑中包含 `.php`）。這對於 Caddy 正確設置 FastCGI 環境變量非常重要。

  - 首先，它檢查 `{path}` 是否是磁盤上存在的文件。如果是，它會重寫到該路徑。這實際上使剩餘部分短路，並確保對磁盤上 *確實存在* 的文件的請求不會被重寫（參見下面的後續步驟）。因此，例如，如果您在磁盤上有一個 `/js/app.js` 文件，那麼對該路徑的請求將保持不變。

  - 其次，它檢查 `{path}/index.php` 是否是磁盤上存在的文件。如果是，它會重寫到該路徑。對於對 `/foo/` 等目錄的請求，它隨後將查找 `/foo//index.php`（被規範化為 `/foo/index.php`），如果存在則將請求重寫到該路徑。如果您在網站根目錄的子目錄中運行另一個 PHP 應用程序，這種行為有時會很有用。

  - 最後，它將始終重寫為 `index.php`（對於現代 PHP 應用程序，它幾乎總是存在）。這允許您的 PHP 應用程序通過使用 `index.php` 腳本作為其入口點來處理 *不* 映射到磁盤上文件的任何路徑請求。

- 最後，最後一部分是實際將請求代理到您的 PHP FastCGI（或 PHP-FPM）服務以實際運行您的 PHP 代碼的部分。請求 matcher 將僅匹配以 `.php` 結尾的請求，因此，任何 *不是* PHP 腳本且在磁盤上 *確實存在* 的文件都將 *不* 由此指令處理，並會穿透。

`php_fastcgi` 指令本身通常是不夠的。它幾乎總是應該與 [`root` 指令](root) 配對以設置文件在磁盤上的位置（對於現代 PHP 應用程序，這可能是 `/var/www/html/public`，其中 `public` 目錄是包含您的 `index.php` 的目錄），以及 [`file_server` 指令](file_server) 來提供您的靜態文件（您的 JS、CSS、圖像等），這些文件未由此指令處理並已穿透。

<a id="examples"></a>
## 範例

將所有 PHP 請求代理到在 `127.0.0.1:9000` 監聽的 FastCGI 響應器：

```caddy-d
php_fastcgi 127.0.0.1:9000
```

同上，但僅針對 `/blog/` 下的請求：

```caddy-d
php_fastcgi /blog/* localhost:9000
```

當使用通過 unix 套接字監聽的 PHP-FPM 時：

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[`root` 指令](root) 幾乎總是用於指定包含 PHP 腳本的目錄，以及 [`file_server` 指令](file_server) 用於提供靜態文件：

```caddy
example.com {
	root /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<a id="docker"></a> <span id="docker"/> 使用 Caddy 提供多個 PHP 應用程序時，每個應用程序的網站根目錄必須不同，以便 Caddy 可以分別讀取和提供您的靜態文件並檢測 PHP 文件是否存在。

如果您使用 Docker，通常您的 PHP-FPM 容器會將文件掛載在相同的根目錄。在這種情況下，解決方案是將文件掛載到 Caddy 容器的不同目錄中，然後使用 [`root` 子指令](#root) 為每個容器設置根目錄：

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

對於不使用 `index.php` 作為入口點的 PHP 站點，您可以改為回退到發出 `404` 錯誤。可以使用 [`handle_errors` 指令](handle_errors) 捕獲並處理該錯誤：

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
