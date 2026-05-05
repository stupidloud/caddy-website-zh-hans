---
title: "ソースからビルド"
---

<a id="build-from-source"></a>
# ソースからビルド

カスタムビルド（例: プラグイン入り）が必要な場合、Caddy をビルドする方法はいくつかあります。
- [Git](#git): Git リポジトリからビルド
- [`xcaddy`](#xcaddy): `xcaddy` を使ってビルド
- [Docker](#docker): カスタム Docker イメージをビルド

要件:

- [Go](https://golang.org/doc/install) 1.20 以降

[Debian/Ubuntu/Raspbian 向けカスタムビルド用パッケージサポートファイル](#package-support-files-for-custom-builds-for-debianubunturaspbian) セクションには、Debian 派生システムで APT コマンドを使って Caddy をインストールしたものの、運用上カスタムビルドの実行ファイルが必要なユーザー向けの手順があります。



## Git

要件:

- Go がインストール済み（上記を参照）

リポジトリを clone します。

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

git がない場合は、[GitHub](https://github.com/caddyserver/caddy) からソースコードをアーカイブファイルとしてダウンロードできます。各 [release](https://github.com/caddyserver/caddy/releases) にもソーススナップショットがあります。

ビルド:

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>


<aside class="tip">

[Go のバグ](https://github.com/golang/go/issues/29228) により、これらの基本手順ではバージョン情報が埋め込まれません。バージョン（`caddy version`）が必要な場合は、Caddy を main module としてではなく依存関係としてコンパイルする必要があります。その手順は Caddy の [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) ファイルにあります。または、これを自動化する [`xcaddy`](#xcaddy) を使えます。

</aside>

Go プログラムは他のプラットフォーム向けにも簡単にコンパイルできます。異なる `GOOS`、`GOARCH`、または `GOARM` 環境変数を設定するだけです。（詳細は [Go documentation](https://golang.org/doc/install/source#environment) を参照してください。）

たとえば、Windows 以外の環境で Caddy を Windows 向けにコンパイルするには:

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

同様に、Linux ではない環境、または ARMv6 ではない環境で Linux ARMv6 向けにコンパイルするには:

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



## xcaddy

[`xcaddy` command](https://github.com/caddyserver/xcaddy) は、バージョン情報やプラグインを含めて Caddy をビルドする最も簡単な方法です。

要件:

- Go がインストール済み（上記を参照）
- [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) が `PATH` にあることを確認

Caddy のソースコードをダウンロードする必要は **ありません**（`xcaddy` が代わりに行います）。

その後、Caddy を（バージョン情報付きで）ビルドするのは次のように簡単です。

<pre><code class="cmd bash">xcaddy build</code></pre>

プラグイン付きでビルドするには、`--with` を使います。

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter
	--with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

見てのとおり、`@` 構文でプラグインのバージョンをカスタマイズできます。バージョンにはタグ名、commit SHA、またはブランチを指定できます。

`xcaddy` によるクロスプラットフォームコンパイルは、`go` コマンドの場合と同じです。たとえば、macOS 向けにクロスコンパイルするには:

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



## Docker

`:builder` イメージを使うと、カスタムモジュールを含む新しい Caddy バイナリのビルドを手早く行えます。

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

開始時には、`<version>` を Caddy の最新バージョンに置き換えてください。

2 つ目の `FROM` 命令に注意してください。これは、通常の `caddy` イメージの上に新しくビルドしたバイナリを重ねるだけなので、はるかに小さいイメージを生成します。

builder は、上で [説明した](#xcaddy) 流れと同様に、指定されたモジュールを含めて Caddy をビルドするために `xcaddy` を使います。`--mount=type=cache,target=/go/pkg/mod` と `--mount=type=cache,target=/root/.cache/go-build` オプションは、それぞれ Go module の依存関係とビルド成果物をキャッシュするために使われ、後続のビルドを高速化します。このフラグは [`xcaddy` ではなく Docker の機能](https://docs.docker.com/build/cache/optimize/#use-cache-mounts) です。

Docker Compose を使う場合は、推奨の [`compose.yml`](/docs/running#docker-compose) と使用手順を参照してください。



<a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>
## Debian/Ubuntu/Raspbian 向けカスタムビルド用パッケージサポートファイル

この手順は、`caddy` パッケージのサポートファイルを維持しながら、カスタム `caddy` バイナリを実行しやすくすることを目的としています。

この手順により、ユーザーは公式パッケージのデフォルト設定、systemd service ファイル、bash-completion を活用できます。

要件:
- [こちらの手順](/docs/install#debian-ubuntu-raspbian) に従って `caddy` パッケージをインストールする
- カスタム `caddy` バイナリをビルドする（上記セクションを参照）、またはカスタムビルドを [download](/download) する
- カスタム `caddy` バイナリは現在のディレクトリに置かれている必要があります

手順:
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

説明:

- `dpkg-divert` は `/usr/bin/caddy` バイナリを `/usr/bin/caddy.default` に移動し、パッケージがこの場所にファイルをインストールしようとした場合に備えて diversion を設定します。

- `update-alternatives` は、希望する caddy バイナリから `/usr/bin/caddy` への symlink を作成します。

- `systemctl restart caddy` は、Caddy サーバーのデフォルトバージョンを停止し、カスタム版を起動します。

以下を実行し、画面上の案内に従うことで、カスタム版とデフォルト版の `caddy` バイナリを切り替えられます。その後、Caddy service を再起動してください。

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

この後 Caddy をアップグレードするには、[`caddy upgrade`](/docs/command-line#caddy-upgrade) を実行できます。これは、現在のビルドと同じプラグインを含み、Caddy の最新バージョンを使ったビルドを [download](/download) し、現在のバイナリを新しいものに置き換えようとします。
