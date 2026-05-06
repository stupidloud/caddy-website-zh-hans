---
title: 保持 Caddy 運行
---

<a id="keep-caddy-running"></a>
# 保持 Caddy 運行

雖然 Caddy 可以透過其 [命令列介面](/docs/command-line) 直接執行，但使用服務管理器（service manager）來保持其運行有許多優點，例如確保系統重新啟動時自動啟動，以及擷取 stdout/stderr 日誌。


- [Linux 服務](#linux-service)
  - [單元檔案](#unit-files)
  - [手動安裝](#manual-installation)
  - [使用服務](#using-the-service)
  - [本地 HTTPS](#local-https-with-systemd)
  - [覆寫](#overrides)
	- [環境變數](#environment-variables)
	- [「run」與「reload」覆寫](#run-and-reload-override)
	- [崩潰後重啟](#restart-on-crash)
  - [SELinux 注意事項](#selinux-considerations)
- [Windows 服務](#windows-service)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [設定](#setup)
  - [使用方式](#usage)
  - [本地 HTTPS](#local-https-with-docker)


<a id="linux-service"></a>
## Linux 服務

在帶有 systemd 的 Linux 發行版上執行 Caddy 的推薦方式是使用我們官方的 systemd 單元檔案。


<a id="unit-files"></a>
### 單元檔案

我們提供兩個不同的 systemd 單元檔案供您選擇，具體取決於您的使用情境：

- [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service) 如果您使用 [Caddyfile](/docs/caddyfile) 設定 Caddy。如果您偏好使用不同的 config adapter 或 JSON 設定檔，您可以 [覆寫](#overrides) `ExecStart` 與 `ExecReload` 命令。

- [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service) 如果您僅透過 [API](/docs/api) 設定 Caddy。此服務使用 [`--resume`](/docs/command-line#caddy-run) 選項，這將使用預設情況下 [持久化](/docs/json/admin/config/) 的 `autosave.json` 來啟動 Caddy。

它們非常相似，但在 `ExecStart` 與 `ExecReload` 命令上有所不同，以適應不同的工作流程。

如果您需要在服務之間切換，應在啟用並啟動另一個服務之前，先停用並停止前一個服務。例如，要從 `caddy` 服務切換到 `caddy-api` 服務：
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>


<a id="manual-installation"></a>
### 手動安裝

某些 [安裝方法](/docs/install) 會自動將 Caddy 設定為以服務形式執行。如果您選擇的方法沒有這樣做，您可以按照以下說明進行操作：

**要求：**

- 您 [下載](/download) 或 [從原始碼構建](/docs/build) 的 `caddy` 二進位檔案
- `systemctl --version` 232 或更新版本
- `sudo` 權限

將 caddy 二進位檔案移動到您的 `$PATH` 中，例如：
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

測試是否成功：
<pre><code class="cmd bash">caddy version</code></pre>

建立一個名為 `caddy` 的群組：
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

建立一個名為 `caddy` 的使用者，並具有可寫入的主目錄：
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

如果使用設定檔，請確保它對您剛剛建立的 `caddy` 使用者是可讀的。

接著，根據您的使用情境 [選擇一個 systemd 單元檔案](#unit-files)。

**再次檢查 `ExecStart` 與 `ExecReload` 指令。** 確保二進位檔案的位置和命令列參數對您的安裝是正確的！例如：如果使用設定檔，且您的 `--config` 路徑與預設值不同，請進行更改。

儲存服務檔案的通常位置是：`/etc/systemd/system/caddy.service`

儲存服務檔案後，您可以使用常用的 systemctl 命令第一次啟動服務：

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

驗證它是否正在運行：
<pre><code class="cmd bash">systemctl status caddy</code></pre>

現在您已經準備好 [使用服務](#using-the-service) 了！



<a id="using-the-service"></a>
### 使用服務

如果使用 Caddyfile，您可以使用 `nano`、`vi` 或您偏好的編輯器編輯設定：
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

您可以將靜態網站檔案放在 `/var/www/html` 或 `/srv` 中。確保 `caddy` 使用者有權讀取這些檔案。

要驗證服務是否正在運行：
<pre><code class="cmd bash">systemctl status caddy</code></pre>
status 命令還會顯示目前運行的服務檔案的位置。

使用我們官方的服務檔案運行時，Caddy 的輸出將被重導向到 `journalctl`。要讀取完整的日誌並避免行被截斷：
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

如果使用設定檔，您可以在進行任何更改後平滑地重新載入 Caddy：
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

您可以使用以下命令停止服務：
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

請勿為了更改 Caddy 的設定而停止服務。停止伺服器會導致停機。請改用 reload 命令。

</aside>

Caddy 程序將以 `caddy` 使用者身份執行，其 `$HOME` 設置為 `/var/lib/caddy`。這意味著：
- 預設的 [資料儲存位置](/docs/conventions#data-directory)（用於證書和其他狀態資訊）將位於 `/var/lib/caddy/.local/share/caddy`。
- 預設的 [設定儲存位置](/docs/conventions#configuration-directory)（用於自動儲存的 JSON 設定，主要對 `caddy-api` 服務有用）將位於 `/var/lib/caddy/.config/caddy`。


<a id="local-https-with-systemd"></a>
### 本地 HTTPS

當使用 Caddy 進行帶有 HTTPS 的本地開發時，您可能會使用像 `localhost` 或 `app.localhost` 這樣的 [hostname](/docs/caddyfile/concepts#addresses)。這將啟用 [本地 HTTPS](/docs/automatic-https#local-https)，使用 Caddy 的本地 CA 來簽發證書。

由於 Caddy 在作為服務運行時是以 `caddy` 使用者身份執行的，因此它沒有權限將其根 CA 證書安裝到系統信任存放區中。要執行此操作，請執行 [`sudo caddy trust`](/docs/command-line#caddy-trust) 以進行安裝。

如果您希望其他裝置在使用 [`internal` 簽發者](/docs/caddyfile/directives/tls#internal) 時連線到您的伺服器，您也需要在這些裝置上安裝根 CA 證書。您可以在 `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt` 找到根 CA 證書。現在許多網頁瀏覽器使用自己的信任存放區（忽略系統的信任存放區），因此您可能也需要手動在那裡安裝證書。


<a id="overrides"></a>
### 覆寫

覆寫服務檔案各方面的最佳方式是使用此命令：
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

這將使用您的預設終端文本編輯器開啟一個空白檔案，您可以在其中覆寫或向單元定義添加指令。這被稱為「drop-in」檔案。

<a id="environment-variables"></a>
#### 環境變數

如果您需要定義用於設定的環境變數，可以這樣做：
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

同樣地，如果您偏好維護一個單獨的檔案來維護環境變數 (envfile)，您可以使用 [`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) 指令，如下所示：
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

然後您的 `/etc/caddy/.env` 檔案可能看起來像這樣（值周圍不要使用 `"` 引號）：

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

<a id="run-and-reload-override"></a>
#### 「run」與「reload」覆寫

如果您需要將預設的 Caddyfile 設定檔更改為使用 JSON 檔案（注意，在設定新值之前，`Exec*` 指令 [必須使用空字串重置](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=)）：
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

<a id="restart-on-crash"></a>
#### 崩潰後重啟

如果您希望 caddy 在意外崩潰後 5 秒後自動重啟：
```systemd
[Service]
# 如果 caddy 崩潰則自動重啟，除非退出碼為 1
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

然後，儲存檔案並退出文本編輯器，並重啟服務以使其生效：
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>



<a id="selinux-considerations"></a>
### SELinux 注意事項

在啟用了 SELinux 的系統上，您有兩個選擇：
1. 使用 [COPR 儲存庫](/docs/install#fedora-redhat-centos) 安裝 Caddy。您的 systemd 檔案和 caddy 二進位檔案將已經建立並標記正確（因此您可以忽略此部分）。如果您希望使用自定義構建的 Caddy，您需要按照下面的說明標記執行檔。

2. [從此網站下載 Caddy](/download) 或使用 [`xcaddy`](https://github.com/caddyserver/xcaddy) 編譯。在任何一種情況下，您都需要自己標記檔案。

除非分別標記為 `systemd_unit_file_t` 和 `bin_t`，否則 systemd 單元檔案及其執行檔將不會運行。

`systemd_unit_file_t` 標籤會自動套用於在 `/etc/systemd/...` 中建立的檔案，因此請確保按照 [手動安裝](#manual-installation) 說明在那裡建立您的 `caddy.service` 檔案。

要標記 `caddy` 二進位檔案，您可以使用以下命令：
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

<a id="windows-service"></a>
## Windows 服務

在 Windows 上有兩種將 Caddy 作為服務運行的路徑：[sc.exe](#scexe) 或 [WinSW](#winsw)。

<a id="scexe"></a>
### sc.exe

要建立服務，請執行：

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "YOURPATH\caddy.exe run"</code></pre>

（將 `YOURPATH` 替換為您的 `caddy.exe` 的實際路徑）

啟動：

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

停止：

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>


<a id="winsw"></a>
### WinSW

按照以下說明在 Windows 上將 Caddy 安裝為服務。

**要求：**

- 您 [下載](/download) 或 [從原始碼構建](/docs/build) 的 `caddy.exe` 二進位檔案
- 來自最新版本 [WinSW](https://github.com/winsw/winsw/releases/latest) 服務包裝器的任何 `.exe`（以下服務設定是為 v2.x 版本編寫的）

將所有檔案放入服務目錄中。在以下範例中，我們使用 `C:\caddy`。

將 `WinSW-x64.exe` 檔案重命名為 `caddy-service.exe`。

在同一目錄中添加一個 `caddy-service.xml`：

```xml
<service>
  <id>caddy</id>
  <!-- 服務的顯示名稱 -->
  <name>Caddy Web Server (powered by WinSW)</name>
  <!-- 服務描述 -->
  <description>Caddy Web Server (https://caddyserver.com/)</description>
  <executable>%BASE%\caddy.exe</executable>
  <arguments>run</arguments>
  <log mode="roll-by-time">
    <pattern>yyyy-MM-dd</pattern>
  </log>
</service>
```

您現在可以使用以下命令安裝服務：
<pre><code class="cmd bash">caddy-service install</code></pre>

您可能想啟動 Windows 服務主控台來查看服務是否正常運行：
<pre><code class="cmd bash">services.msc</code></pre>

請注意，Windows 服務無法重新載入，因此您必須直接告訴 caddy 重新載入：
<pre><code class="cmd bash">caddy reload</code></pre>

可以透過正常的 Windows 服務命令重新啟動，例如透過工作管理員的「服務」分頁。

有關自定義服務包裝器的資訊，請參閱 [WinSW 文件](https://github.com/winsw/winsw/tree/master#usage)


<a id="docker-compose"></a>
## Docker Compose

使用 Docker 啟動並運行的最簡單方法是使用 Docker Compose。有關官方 Caddy Docker 映像的更多其他詳細資訊，請參閱 [Docker Hub](https://hub.docker.com/_/caddy) 上的文件。

<aside class="tip">

這假設您使用的是 [Docker Compose V2](https://docs.docker.com/compose/reference/)，其中命令現在是 `docker compose`（空格），而不是 V1 的 `docker-compose`（連字號）。

</aside>

<a id="setup"></a>
### 設定

首先，建立一個檔案 `compose.yml`（或將此服務添加到您現有的檔案中）：

```yaml
services:
  caddy:
    image: caddy:<version>
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./conf:/etc/caddy
      - ./site:/srv
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

請確保在映像 `<version>` 中填寫最新的版本號，您可以在 [Docker Hub](https://hub.docker.com/_/caddy) 的「Tags」部分找到列出的版本。

這的作用是：

- 使用 `unless-stopped` 重啟策略，確保在機器重新啟動時自動重啟 Caddy 容器。
- 分別綁定到 HTTP 和 HTTPS 的連接埠 `80` 與 `443`，以及用於 HTTP/3 的 `443/udp`。
- 綁定掛載包含您的 Caddyfile 設定的 `conf` 目錄。
- 綁定掛載 `site` 目錄，以便從 `/srv` 提供網站的靜態檔案。
- 為 `/data` 和 `/config` 命名磁碟卷，以 [持久化重要資訊](/docs/conventions#file-locations)。

然後，建立一個名為 `Caddyfile` 的檔案，作為 `conf` 目錄中唯一的檔案，並編寫您的 [Caddyfile](/docs/caddyfile/concepts) 設定。

如果您有靜態檔案要提供，可以將它們放在設定旁邊的 `site/` 目錄中，然後使用 `root /srv` 設定 [`root`](/docs/caddyfile/directives/root)。如果您沒有，則可以移除 `/srv` 磁碟卷掛載。

<aside class="tip">

如果您使用 Caddy [反向代理](/docs/caddyfile/directives/reverse_proxy) 到另一個容器，請記住，在 Docker 網路中，`localhost` 意味著「這個容器」，而不是「這台機器」。因此，例如不要使用 `reverse_proxy localhost:8080`，而是使用 `reverse_proxy other-container:8080`

</aside>

如果您需要帶有外掛程式的自定義構建 Caddy，請按照 [Docker 構建說明](/docs/build#docker) 建立自定義 Docker 映像。在您的 `compose.yml` 旁邊建立 `Dockerfile`，然後將 `compose.yml` 中的 `image:` 行替換為 `build: .`。



<a id="usage"></a>
### 使用方式

接著，您可以啟動容器：
<pre><code class="cmd bash">docker compose up -d</code></pre>

更改 Caddyfile 後重新載入 Caddy：
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

自 v2.11.0 起，您可以使用 `SIGUSR1` 重新載入，前提是 Caddy 是使用 `caddy run` 和設定檔啟動的：
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

要查看 Caddy 最近的 1000 條日誌，並使用 `f`ollow 查看新日誌：
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

<a id="local-https-with-docker"></a>
### 本地 HTTPS

當使用 Docker 進行帶有 HTTPS 的本地開發時，您可能會使用像 `localhost` 或 `app.localhost` 這樣的 [hostname](/docs/caddyfile/concepts#addresses)。這將啟用 [本地 HTTPS](/docs/automatic-https#local-https)，使用 Caddy 的本地 CA 來簽發證書。這意味著容器外部的 HTTP 客戶端將不信任 Caddy 提供的 TLS 證書。要解決此問題，您可以在主機機器的信任存放區中安裝 Caddy 的根 CA 證書：

<div x-data="{ os: $persist(defaultOS(['linux', 'mac', 'windows'], 'linux')) }" class="tabs">
<div class="tab-buttons">
	<button x-on:click="os = 'linux'" x-bind:class="{ active: os === 'linux' }">Linux</button>
	<button x-on:click="os = 'mac'" x-bind:class="{ active: os === 'mac' }">Mac</button>
	<button x-on:click="os = 'windows'" x-bind:class="{ active: os === 'windows' }">Windows</button>
</div>

<div x-show="os === 'linux'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /usr/local/share/ca-certificates/root.crt \
  && sudo update-ca-certificates</code></pre>

</div>

<div x-show="os === 'mac'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /tmp/root.crt \
  && sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain /tmp/root.crt</code></pre>

</div>

<div x-show="os === 'windows'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    %TEMP%/root.crt \
  && certutil -addstore -f "ROOT" %TEMP%/root.crt</code></pre>

</div>
</div>

現在許多網頁瀏覽器使用自己的信任存放區（忽略系統的信任存放區），因此您可能也需要手動在那裡安裝證書，使用上述命令從容器中複製的 `root.crt` 檔案。

- 對於 Firefox，前往「偏好設定」>「隱私與安全性」>「憑證」>「檢視憑證」>「憑證機構」>「匯入」，然後選擇 `root.crt` 檔案。

- 對於 Chrome，前往「設定」>「隱私權和安全性」>「安全性」>「管理憑證」>「憑證機構」>「匯入」，然後選擇 `root.crt` 檔案。
