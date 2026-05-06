---
title: "從源碼編譯"
---

<a id="build-from-source"></a>
# 從源碼編譯

如果您需要自訂編譯（例如添加插件），有多種編譯 Caddy 的選項：
- [Git](#git)：從 Git 存儲庫編譯
- [`xcaddy`](#xcaddy)：使用 `xcaddy` 編譯
- [Docker](#docker)：編譯自訂 Docker 映像

要求：

- [Go](https://golang.org/doc/install) 1.20 或更高版本

[針對 Debian/Ubuntu/Raspbian 自訂編譯的套件支援檔案](#package-support-files-for-custom-builds-for-debianubunturaspbian) 章節包含針對使用 APT 命令在 Debian 衍生系統上安裝了 Caddy，但需要自訂編譯的可執行檔案來進行操作的使用者說明。



<a id="git"></a>
## Git

要求：

- 已安裝 Go（見上文）

克隆存儲庫：

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

如果您沒有 git，可以 [從 GitHub](https://github.com/caddyserver/caddy) 下載原始碼存檔。每個 [release](https://github.com/caddyserver/caddy/releases) 也有原始碼快照。

編譯：

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>


<aside class="tip">

由於 [Go 中的一個 bug](https://github.com/golang/go/issues/29228)，這些基本步驟不會嵌入版本資訊。如果您需要版本資訊（`caddy version`），您需要將 Caddy 作為依賴項而不是主模組進行編譯。相關說明在 Caddy 的 [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) 檔案中。或者，您可以使用自動執行此操作的 [`xcaddy`](#xcaddy)。

</aside>

Go 程式很容易為其他平台編譯。只需設置不同的 `GOOS`、`GOARCH` 和/或 `GOARM` 環境變數即可。（[詳情請參閱 go 官方文檔](https://golang.org/doc/install/source#environment)）。

例如，要在非 Windows 系統上為 Windows 編譯 Caddy：

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

或者類似地，在非 Linux 或非 ARMv6 系統上為 Linux ARMv6 編譯：

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



<a id="xcaddy"></a>
## xcaddy

[`xcaddy` 命令](https://github.com/caddyserver/xcaddy) 是編譯帶有版本資訊和/或插件的 Caddy 最簡單的方法。

要求：

- 已安裝 Go（見上文）
- 確保 [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) 在您的 `PATH` 中

您 **不需要** 下載 Caddy 原始碼（它會為您完成此操作）。

然後編譯 Caddy（帶有版本資訊）就像這樣簡單：

<pre><code class="cmd bash">xcaddy build</code></pre>

要使用插件編譯，請使用 `--with`：

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
	--with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

如您所見，您可以使用 `@` 語法自訂插件的版本。版本可以是標籤名稱、提交 SHA 或分支。

使用 `xcaddy` 進行跨平台編譯與使用 `go` 命令相同。例如，為 macOS 進行跨平台編譯：

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



<a id="docker"></a>
## Docker

您可以使用 `:builder` 映像作為編譯帶有自訂模組的新 Caddy 二進位檔案的捷徑：

```Dockerfile
FROM caddy:<version>-builder AS builder

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
    --with github.com/hairyhenderson/caddy-teapot-module@v0.0.3-0

FROM caddy:<version>

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

請務必將 `&lt;version&gt;` 替換為最新的 Caddy 版本以開始。

注意第二個 `FROM` 指令 —— 這會透過簡單地將新編譯的二進位檔案疊加在常規 `caddy` 映像之上，從而產生一個小得多的映像。

編譯器使用 `xcaddy` 編譯帶有提供模組的 Caddy，類似於 [上文所述](#xcaddy) 的過程。`--mount=type=cache,target=/go/pkg/mod` 和 `--mount=type=cache,target=/root/.cache/go-build` 選項分別用於快取 Go 模組依賴項和編譯產物，從而加快後續編譯速度。該標記是 [Docker 的一項功能](https://docs.docker.com/build/cache/optimize/#use-cache-mounts)，而不是 `xcaddy` 的。

要使用 Docker Compose，請參閱我們推薦的 [`compose.yml`](/docs/running#docker-compose) 和使用說明。



<a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>
## 針對 Debian/Ubuntu/Raspbian 自訂編譯的套件支援檔案

此程序旨在簡化運行自訂 `caddy` 二進位檔案的過程，同時保留來自 `caddy` 套件的支援檔案。

此程序允許使用者利用官方套件中的默認配置、systemd 服務檔案和 bash-completion。

要求：
- 根據 [這些說明](/docs/install#debian-ubuntu-raspbian) 安裝 `caddy` 套件
- 編譯您的自訂 `caddy` 二進位檔案（參見上述章節），或 [下載](/download) 自訂編譯版本
- 您的自訂 `caddy` 二進位檔案應位於當前目錄中

程序：
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

說明：

- `dpkg-divert` 將把 `/usr/bin/caddy` 二進位檔案移動到 `/usr/bin/caddy.default`，並在原處設置一個轉向（diversion），以防有任何套件想要將檔案安裝到此位置。

- `update-alternatives` 將創建從所需的 caddy 二進位檔案到 `/usr/bin/caddy` 的軟連結。

- `systemctl restart caddy` 將關閉默認版本的 Caddy 伺服器並啟動自訂版本。

您可以透過執行以下命令並按照螢幕上的資訊，在自訂和默認 `caddy` 二進位檔案之間進行切換。然後，重新啟動 Caddy 服務。

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

在此之後要升級 Caddy，您可以執行 [`caddy upgrade`](/docs/command-line#caddy-upgrade)。這會嘗試 [下載](/download) 一個與您當前編譯版本具有相同插件且為最新 Caddy 版本的編譯版本，然後將當前二進位檔案替換為新版本。
