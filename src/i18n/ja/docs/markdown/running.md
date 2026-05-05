---
title: Caddy を継続実行する
---

<a id="keep-caddy-running"></a>
# Caddy を継続実行する

Caddy は[コマンドラインインターフェース](/docs/command-line)から直接実行できますが、サービスマネージャーを使って実行し続けることには多くの利点があります。たとえば、システム再起動時に自動起動させたり、stdout/stderr ログを取得したりできます。


- [Linux サービス](#linux-service)
  - [Unit ファイル](#unit-files)
  - [手動インストール](#manual-installation)
  - [サービスを使う](#using-the-service)
  - [ローカル HTTPS](#local-https-with-systemd)
  - [オーバーライド](#overrides)
	- [環境変数](#environment-variables)
	- [`run` と `reload` のオーバーライド](#run-and-reload-override)
	- [クラッシュ時の再起動](#restart-on-crash)
  - [SELinux に関する考慮事項](#selinux-considerations)
- [Windows service](#windows-service)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [セットアップ](#setup)
  - [使い方](#usage)
  - [ローカル HTTPS](#local-https-with-docker)


<a id="linux-service"></a>
## Linux サービス

systemd を使う Linux ディストリビューションで Caddy を実行する推奨方法は、公式の systemd unit ファイルを使うことです。


<a id="unit-files"></a>
### Unit ファイル

ユースケースに応じて選べる、2 種類の systemd unit ファイルを提供しています。

- [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service): [Caddyfile](/docs/caddyfile) で Caddy を設定する場合に使います。別の config adapter や JSON 設定ファイルを使いたい場合は、`ExecStart` と `ExecReload` コマンドを[オーバーライド](#overrides)できます。

- [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service): Caddy を [API](/docs/api) だけで設定する場合に使います。このサービスは [`--resume`](/docs/command-line#caddy-run) オプションを使い、既定で[永続化](/docs/json/admin/config/)される `autosave.json` を使って Caddy を起動します。

両者はよく似ていますが、ワークフローに合わせるために `ExecStart` と `ExecReload` コマンドが異なります。

サービスを切り替える必要がある場合は、新しいサービスを有効化して開始する前に、以前のサービスを無効化して停止してください。たとえば `caddy` サービスから `caddy-api` サービスへ切り替えるには、次のようにします。
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>


<a id="manual-installation"></a>
### 手動インストール

一部の[インストール方法](/docs/install)では、Caddy がサービスとして実行されるよう自動的にセットアップされます。そうでない方法を選んだ場合は、次の手順に従ってください。

**要件:**

- [ダウンロード](/download)または[ソースからビルド](/docs/build)した `caddy` バイナリ
- `systemctl --version` 232 以降
- `sudo` 権限

caddy バイナリを `$PATH` に移動します。例:
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

動作したことを確認します。
<pre><code class="cmd bash">caddy version</code></pre>

`caddy` という名前のグループを作成します。
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

書き込み可能なホームディレクトリを持つ `caddy` という名前のユーザーを作成します。
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

設定ファイルを使う場合は、作成した `caddy` ユーザーがそのファイルを読めるようにしてください。

次に、ユースケースに基づいて [systemd unit ファイルを選びます](#unit-files)。

**`ExecStart` と `ExecReload` ディレクティブを必ず再確認してください。** バイナリの場所とコマンドライン引数が、あなたのインストールに対して正しいことを確認してください。たとえば設定ファイルを使う場合、既定と異なるなら `--config` パスを変更します。

サービスファイルの通常の保存先は `/etc/systemd/system/caddy.service` です。

サービスファイルを保存したら、いつもの systemctl 手順で初回起動できます。

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

実行中であることを確認します。
<pre><code class="cmd bash">systemctl status caddy</code></pre>

これで[サービスを使う](#using-the-service)準備ができました。



<a id="using-the-service"></a>
### サービスを使う

Caddyfile を使う場合は、`nano`、`vi`、または好みのエディタで設定を編集できます。
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

静的サイトファイルは `/var/www/html` または `/srv` のどちらにも配置できます。`caddy` ユーザーにファイルを読む権限があることを確認してください。

サービスが実行中か確認するには:
<pre><code class="cmd bash">systemctl status caddy</code></pre>
status コマンドは、現在実行中のサービスファイルの場所も表示します。

公式サービスファイルで実行している場合、Caddy の出力は `journalctl` へリダイレクトされます。完全なログを読み、行が切り詰められるのを避けるには:
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

設定ファイルを使っている場合、変更後に Caddy を graceful にリロードできます。
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

サービスを停止するには:
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

Caddy の設定変更のためにサービスを停止しないでください。サーバーを停止するとダウンタイムが発生します。代わりに reload コマンドを使ってください。

</aside>

Caddy プロセスは `caddy` ユーザーとして実行され、その `$HOME` は `/var/lib/caddy` に設定されます。つまり、次のようになります。
- 既定の[データ保存場所](/docs/conventions#data-directory)（証明書やその他の状態情報）は `/var/lib/caddy/.local/share/caddy` になります。
- 既定の[設定保存場所](/docs/conventions#configuration-directory)（自動保存された JSON 設定。主に `caddy-api` サービスで有用）は `/var/lib/caddy/.config/caddy` になります。


<a id="local-https-with-systemd"></a>
### systemd でのローカル HTTPS

ローカル開発で Caddy を HTTPS と一緒に使う場合、`localhost` や `app.localhost` のような[ホスト名](/docs/caddyfile/concepts#addresses)を使うことがあります。これにより、Caddy のローカル CA が証明書を発行する [Local HTTPS](/docs/automatic-https#local-https) が有効になります。

サービスとして実行している場合、Caddy は `caddy` ユーザーとして動作するため、ルート CA 証明書をシステムの信頼ストアへインストールする権限がありません。これを行うには、[`sudo caddy trust`](/docs/command-line#caddy-trust) を実行してインストールします。

[`internal` issuer](/docs/caddyfile/directives/tls#internal) を使っているときに他のデバイスからサーバーへ接続させたい場合は、それらのデバイスにもルート CA 証明書をインストールする必要があります。ルート CA 証明書は `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt` にあります。現在、多くの Web ブラウザは独自の信頼ストアを使うため（システムの信頼ストアを無視するため）、ブラウザ側にも手動で証明書をインストールする必要があるかもしれません。


<a id="overrides"></a>
### オーバーライド

サービスファイルの一部をオーバーライドする最善の方法は、次のコマンドです。
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

これにより、既定のターミナルテキストエディタで空のファイルが開き、unit 定義に対してディレクティブをオーバーライドまたは追加できます。これは「drop-in」ファイルと呼ばれます。

<a id="environment-variables"></a>
#### 環境変数

設定内で使う環境変数を定義する必要がある場合は、次のようにできます。
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

同様に、環境変数を別ファイル（envfile）で管理したい場合は、[`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) ディレクティブを次のように使えます。
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

このとき `/etc/caddy/.env` ファイルは次のようになります（値を `"` 引用符で囲まないでください）。

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

<a id="run-and-reload-override"></a>
#### `run` と `reload` のオーバーライド

設定ファイルを既定の Caddyfile から JSON ファイルへ変更する必要がある場合は、次のようにします（新しい値を設定する前に、`Exec*` ディレクティブは[空文字列でリセットする必要があります](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=)）。
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

<a id="restart-on-crash"></a>
#### クラッシュ時の再起動

caddy が予期せずクラッシュした場合、5 秒後に自動再起動させたいなら:
```systemd
[Service]
# 終了コードが 1 の場合を除き、caddy がクラッシュしたら自動的に再起動する
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

その後、ファイルを保存してテキストエディタを終了し、反映のためにサービスを再起動します。
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>



<a id="selinux-considerations"></a>
### SELinux に関する考慮事項

SELinux が有効なシステムでは、2 つの選択肢があります。
1. [COPR repo](/docs/install#fedora-redhat-centos) を使って Caddy をインストールします。systemd ファイルと caddy バイナリはすでに正しく作成され、ラベル付けされています（そのためこのセクションは無視できます）。Caddy のカスタムビルドを使いたい場合は、下記のように実行ファイルへラベル付けする必要があります。

2. [このサイトから Caddy をダウンロード](/download)するか、[`xcaddy`](https://github.com/caddyserver/xcaddy) でコンパイルします。どちらの場合も、ファイルには自分でラベル付けする必要があります。

Systemd unit ファイルとその実行ファイルは、それぞれ `systemd_unit_file_t` と `bin_t` でラベル付けされていない限り実行されません。

`/etc/systemd/...` に作成されたファイルには `systemd_unit_file_t` ラベルが自動的に適用されるため、[手動インストール](#manual-installation)手順に従い、必ずそこに `caddy.service` ファイルを作成してください。

`caddy` バイナリにタグ付けするには、次のコマンドを使えます。
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

<a id="windows-service"></a>
## Windows service

Windows で Caddy をサービスとして実行する方法は 2 つあります。[sc.exe](#scexe) または [WinSW](#winsw) です。

### sc.exe

サービスを作成するには、次を実行します。

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "YOURPATH\caddy.exe run"</code></pre>

（`YOURPATH` を実際の `caddy.exe` のパスに置き換えてください）

起動するには:

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

停止するには:

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>


### WinSW

次の手順で、Windows に Caddy をサービスとしてインストールします。

**要件:**

- [ダウンロード](/download)または[ソースからビルド](/docs/build)した `caddy.exe` バイナリ
- [WinSW](https://github.com/winsw/winsw/releases/latest) サービスラッパーの最新リリースから任意の `.exe`（以下のサービス設定は v2.x リリース向けです）

すべてのファイルをサービスディレクトリへ配置します。以下の例では `C:\caddy` を使います。

`WinSW-x64.exe` ファイルの名前を `caddy-service.exe` に変更します。

同じディレクトリに `caddy-service.xml` を追加します。

```xml
<service>
  <id>caddy</id>
  <!-- Display name of the service -->
  <name>Caddy Web Server (powered by WinSW)</name>
  <!-- Service description -->
  <description>Caddy Web Server (https://caddyserver.com/)</description>
  <executable>%BASE%\caddy.exe</executable>
  <arguments>run</arguments>
  <log mode="roll-by-time">
    <pattern>yyyy-MM-dd</pattern>
  </log>
</service>
```

次のコマンドでサービスをインストールできます。
<pre><code class="cmd bash">caddy-service install</code></pre>

Windows Services Console を起動して、サービスが正しく実行されているか確認したくなるかもしれません。
<pre><code class="cmd bash">services.msc</code></pre>

Windows services はリロードできないため、caddy に直接リロードを指示する必要があります。
<pre><code class="cmd bash">caddy reload</code></pre>

再起動は通常の Windows サービスコマンドで可能です。たとえば Task Manager の "Services" タブから行えます。

サービスラッパーのカスタマイズについては、[WinSW documentation](https://github.com/winsw/winsw/tree/master#usage) を参照してください。


## Docker Compose

Docker で手早く起動する最も簡単な方法は Docker Compose を使うことです。公式 Caddy Docker イメージの追加詳細については、[Docker Hub](https://hub.docker.com/_/caddy) のドキュメントを参照してください。

<aside class="tip">

これは [Docker Compose V2](https://docs.docker.com/compose/reference/) を使っている前提です。V2 ではコマンドは V1 の `docker-compose`（ハイフン）ではなく、`docker compose`（スペース）です。

</aside>

<a id="setup"></a>
### セットアップ

まず `compose.yml` ファイルを作成します（または既存ファイルにこのサービスを追加します）。

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

image の `<version>` には最新のバージョン番号を入れてください。これは [Docker Hub](https://hub.docker.com/_/caddy) の "Tags" セクションで確認できます。

この設定が行うこと:

- `unless-stopped` 再起動ポリシーを使い、マシン再起動時に Caddy コンテナが自動的に再起動されるようにします。
- HTTP と HTTPS 用にそれぞれ `80` と `443`、さらに HTTP/3 用に `443/udp` へバインドします。
- Caddyfile 設定を含む `conf` ディレクトリを bind mount します。
- サイトの静的ファイルを `/srv` から配信するため、`site` ディレクトリを bind mount します。
- `/data` と `/config` には、[重要な情報を永続化](/docs/conventions#file-locations)するための named volume を使います。

次に、`conf` ディレクトリ内の唯一のファイルとして `Caddyfile` という名前のファイルを作成し、[Caddyfile](/docs/caddyfile/concepts) 設定を書きます。

配信する静的ファイルがある場合は、設定の隣に `site/` ディレクトリを置き、[`root`](/docs/caddyfile/directives/root) を `root /srv` で設定できます。ない場合は、`/srv` volume mount を削除して構いません。

<aside class="tip">

Caddy を使って別コンテナへ [reverse proxy](/docs/caddyfile/directives/reverse_proxy) する場合、Docker ネットワークでは `localhost` が「このマシン」ではなく「このコンテナ」を意味することを忘れないでください。たとえば `reverse_proxy localhost:8080` は使わず、代わりに `reverse_proxy other-container:8080` を使います。

</aside>

プラグイン入りの Caddy カスタムビルドが必要な場合は、[Docker build instructions](/docs/build#docker) に従ってカスタム Docker イメージを作成してください。`Dockerfile` を `compose.yml` の隣に作成し、`compose.yml` 内の `image:` 行を `build: .` に置き換えます。



<a id="usage"></a>
### 使い方

次に、コンテナを起動できます。
<pre><code class="cmd bash">docker compose up -d</code></pre>

Caddyfile の変更後に Caddy をリロードするには:
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

v2.11.0 以降では、Caddy が `caddy run` と設定ファイルで起動されている場合、`SIGUSR1` でリロードできます。
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

Caddy の直近 1000 件のログを表示し、新しいログをストリーミング表示するために `f`ollow するには:
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

<a id="local-https-with-docker"></a>
### Docker でのローカル HTTPS

ローカル開発で Docker と HTTPS を使う場合、`localhost` や `app.localhost` のような[ホスト名](/docs/caddyfile/concepts#addresses)を使うことがあります。これにより、Caddy のローカル CA が証明書を発行する [Local HTTPS](/docs/automatic-https#local-https) が有効になります。つまり、コンテナ外の HTTP クライアントは Caddy が提供する TLS 証明書を信頼しません。これを解決するには、Caddy のルート CA 証明書をホストマシンの信頼ストアへインストールできます。

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

現在、多くの Web ブラウザは独自の信頼ストアを使うため（システムの信頼ストアを無視するため）、上のコマンドでコンテナからコピーした `root.crt` ファイルを使って、ブラウザにも手動で証明書をインストールする必要があるかもしれません。

- Firefox では、Preferences > Privacy & Security > Certificates > View Certificates > Authorities > Import へ移動し、`root.crt` ファイルを選択します。

- Chrome では、Settings > Privacy and security > Security > Manage certificates > Authorities > Import へ移動し、`root.crt` ファイルを選択します。
