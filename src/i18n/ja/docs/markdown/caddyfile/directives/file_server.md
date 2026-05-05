---
title: file_server (Caddyfile directive)
---

<script>
ready(function() {
	// Fix inline browse arg
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# file_server

実ファイルシステムと仮想ファイルシステムをサポートする静的ファイルサーバーです。リクエストの URI path を [site's root path](root) に追加して、ファイルパスを組み立てます。

デフォルトでは canonical URI を強制します。つまり、末尾のスラッシュがないディレクトリへのリクエストにはスラッシュを追加するための HTTP redirect が発行され、末尾にスラッシュがあるファイルへのリクエストにはスラッシュを削除するための HTTP redirect が発行されます。ただし、内部 rewrite によってパスの最後の要素（ファイル名）が変更された場合、redirect は発行されません。

ほとんどの場合、`file_server` directive は [`root`](root) directive と組み合わせて、サイト全体のファイル root を設定します。この directive にも `root` subdirective（下記参照）があり、このハンドラだけの root を設定できます（非推奨）。site root は sandbox 保証を持たない点に注意してください。file server はパスコンポーネントによる directory traversal を防ぎますが、root 内の symbolic link によって root 外へのアクセスが可能になる場合があります。

エラーが発生した場合（例: file not found `404`、permission denied `403`）、error route が呼び出されます。[`handle_errors`](handle_errors) directive を使って error route を定義し、カスタムエラーページを表示してください。

`browse` を使う場合、デフォルト出力は HTML template によって生成されます。クライアントは `Accept: application/json` または `Accept: text/plain` header を使うことで、ディレクトリ一覧を JSON または plaintext としてリクエストできます。JSON 出力はスクリプト用途に便利で、plaintext 出力は人がターミナルで読む用途に便利です。


<a id="syntax"></a>
## 構文

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <path>
	hide          <files...>
	index         <filenames...>
	browse        [<template_file>] {
		reveal_symlinks
		sort <sort_field> [<direction>]
		file_limit <number>
	}
	precompressed [<formats...>]
	status        <status>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> は、使用する代替の（場合によっては仮想の）ファイルシステムを指定します。`caddy.fs` namespace の任意の Caddy module をここで使用できます。root path/prefix は代替ファイルシステムモジュールにも引き続き適用されます。デフォルトではローカルディスクが使われます。

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 では、ファイルシステムツリーをカスタム Caddy build に埋め込む [`--embed` flag](https://github.com/caddyserver/xcaddy#custom-builds) が導入され、`embedded` という名前の `fs` module が登録されます。これにより、静的サイトを Caddy 実行ファイルとして配布できます。

- **root** <span id="root"/> は site root へのパスを設定します。[`root`](root) directive と似ていますが、この file server インスタンスにのみ適用され、定義済みの他の site root を上書きします。デフォルト: `{http.vars.root}` または現在の作業ディレクトリ。注意: この subdirective はこのハンドラの root だけを変更します。他の directive（[`try_files`](try_files) や [`templates`](templates) など）が同じ site root を知る必要がある場合は、代わりに [`root`](root) directive を使ってください。

- **hide** <span id="hide"/> は隠すファイルまたはフォルダのリストです。リクエストされた場合、file server はそれらが存在しないものとして扱います。placeholder と glob pattern を受け付けます。これらは request path ではなく、*file system* path である点に注意してください。言い換えると、相対パスは site root ではなく現在の作業ディレクトリを基準にし、すべてのパスは（可能であれば）比較前に絶対形式へ変換されます。パス区切りを含まないファイル名または pattern を指定すると、場所に関係なく一致する名前のすべてのファイルが隠されます。それ以外の場合は path prefix match が試され、その後 globular match が試されます。これは Caddyfile 設定であるため、アクティブな設定ファイルはデフォルトで追加されます。hide の比較は case-sensitive です。case-insensitive なファイルシステムでは、大文字小文字が異なる request path が同じオンディスク path に解決される可能性があるため、`hide` を機密パスの security boundary として扱うべきではありません。

- **index** <span id="index"/> は index file として探すファイル名のリストです。デフォルト: `index.html index.txt`

- **browse** <span id="browse"/> は、index file がないディレクトリへのリクエストでファイル一覧を有効にします。

  - **<template_file>** <span id="template_file"/> は、ディレクトリ一覧に使う任意のカスタム template file です。デフォルトは `caddy file-server export-template` コマンドで抽出できる template で、このコマンドはデフォルト template を stdout に出力します。埋め込み template は[ソースコード内のここ ![external link](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html)にもあります。Browse template では [standard templates module](/docs/modules/http.handlers.templates#docs) の actions も使用できます。

  - **reveal_symlinks** <span id="reveal_symlinks"/> は、ディレクトリ一覧で symbolic link の target を表示するようにします。デフォルトでは symlink target は隠され、link file 自体だけが表示されます。

  - **sort** <span id="sort"/> は、ディレクトリ一覧のデフォルト sort を変更します。最初のパラメータは sort 対象の field/column です: `name`、`namedirfirst`、`size`、`time`。2 つ目の引数は任意の方向です: `asc` または `desc`。たとえば、`sort name desc` は名前で降順に sort します。

  - **file_limit** <span id="file_limit"/> は、ディレクトリ一覧に表示するファイル数の最大値を設定します。デフォルト: `10000`。ファイル数がこの上限を超える場合、最初の N 個のファイルだけが表示されます。N は指定した上限値です。

- **precompressed** <span id="precompressed"/> は、事前圧縮された sidecar file を探す encoding format のリストです。引数は、事前圧縮された [sidecar files](https://en.wikipedia.org/wiki/Sidecar_file) を検索する encoding format の順序付きリストです。サポートされる format は `gzip`（`.gz`）、`zstd`（`.zst`）、`br`（`.br`）です。format を省略した場合、デフォルトは `br zstd gzip`（この順）です。

  すべてのファイル検索では、まず非圧縮ファイルの存在を確認します。見つかると、Caddy は有効な各 format のファイル拡張子を持つ sidecar file を探します。事前圧縮された sidecar file が見つかった場合、Caddy は `Content-Encoding` response header を適切に設定して、その事前圧縮ファイルで応答します。そうでない場合、Caddy は通常どおり非圧縮ファイルで応答します。[`encode` directive](encode) が有効な場合、事前圧縮されていなければレスポンスをオンザフライで圧縮することがあります。

- **status** <span id="status"/> は、レスポンスを書き込むときに使う任意の status code override です。[custom error page](handle_errors) でリクエストに応答するときに特に便利です。3 桁の status code を指定できます。例: `404`。placeholder をサポートします。デフォルトでは、書き込まれる status code は通常 `200`、partial content の場合は `206` です。

- **disable_canonical_uris** <span id="disable_canonical_uris"/> は、デフォルトの redirect 動作を無効にします（request path がディレクトリなら末尾のスラッシュを追加し、request path がファイルなら末尾のスラッシュを削除します）。デフォルトでは、明示的な rewrite を暗黙的な動作で上書きしないように、request path の最後の要素（ファイル名）が内部 rewrite された場合は canonicalization が行われない点に注意してください。

- **pass_thru** <span id="pass_thru"/> は pass-thru mode を有効にします。リクエストされたファイルが見つからない場合に `404` エラーを発生させる（[`handle_errors`](handle_errors) route を呼び出す）のではなく、route 内の次の HTTP handler へ処理を続行します。実際には、この directive は実質的に [ordered last](/docs/caddyfile/directives#directive-order) されるため、`file_server` の後に他の handler directive が続く [`route`](route) block 内でのみ有用です。


<a id="examples"></a>
## 例

現在のディレクトリを提供する静的ファイルサーバー:

```caddy-d
file_server
```

ファイル一覧を有効にする:

```caddy-d
file_server browse
```

`/static` フォルダ内の静的ファイルだけを提供する:

```caddy-d
file_server /static/*
```

`file_server` directive は通常、ファイルを提供する root path を設定するために [`root` directive](root) と組み合わせます。

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

Caddy を systemd service として実行している場合、`/home` からファイルを読み取ることはできません。`caddy` user が `/home` directory に対する "executable" permission（traversal に必要）を持っていないためです。代わりに、ファイルは `/srv` または `/var/www/html` に置くことを推奨します。

</aside>


すべての `.git` folder とその内容を隠します。

```caddy-d
file_server {
	hide .git
}
```

クライアントがサポートしている場合（`Accept-Encoding` header）、リクエストされたファイルの横にある事前圧縮ファイルの存在を確認します。たとえば `/path/to/file` がリクエストされた場合、`/path/to/file.br`、`/path/to/file.zst`、`/path/to/file.gz` の順に確認し、対応する `Content-Encoding` を付けて最初に利用可能なファイルを提供します。

```caddy-d
file_server {
	precompressed
}
```
