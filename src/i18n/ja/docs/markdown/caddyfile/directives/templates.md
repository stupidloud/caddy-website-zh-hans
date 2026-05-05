---
title: templates (Caddyfile directive)
---

# templates

レスポンス body を [template](/docs/modules/http.handlers.templates) ドキュメントとして実行します。Templates は、簡単な動的ページを作るための機能的な primitive を提供します。HTTP subrequest、HTML ファイル include、Markdown rendering、JSON parsing、基本的なデータ構造、乱数、時刻などの機能があります。


<a id="syntax"></a>
## 構文

```caddy-d
templates [<matcher>] {
	mime    <types...>
	between <open_delim> <close_delim>
	root    <path>
	extensions {
		<name> {
			...
		}
	}
}
```

- **mime** は templates middleware が処理する MIME type です。条件を満たす `Content-Type` を持たないレスポンスは、template として評価されません。

  デフォルト: `text/html text/plain`。

- **between** は template action の開始 delimiter と終了 delimiter です。ドキュメントの他の部分と干渉する場合は変更できます。

  デフォルト: `{{printf "{{ }}"}}`。

- **root** は、file system にアクセスする関数を使うときの site root です。

  [`root`](root) ディレクティブで設定された site root がデフォルトです。設定されていない場合は現在の working directory です。

- **extensions** は、`http.handlers.templates.functions.*` namespace の module が提供する custom template function を登録できます。

  ブロック内の各サブディレクティブは module 名に対応します。これらの module は template function map に custom function を追加でき、通常は再利用可能な component の実装に使われます。この機能は主に plugin 向けです。

組み込み template function のドキュメントは [templates module](/docs/modules/http.handlers.templates#docs) にあります。



<a id="examples"></a>
## 例

templates を使って markdown を配信する site の完全な例は、[この Web サイト自体](https://github.com/caddyserver/website)の source を見てください。特に [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile) と [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html) が参考になります。

静的 site で templates を有効にします。

```caddy
example.com {
	root /srv
	templates
	file_server
}
```

template を使って単純な静的レスポンスを配信するには、必ず `Content-Type` を設定してください。

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `Current year is: {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

template extension（plugin）を使います。

```caddy
example.com {
	root /srv
	templates {
		extensions {
			# caddy-hitcounter plugin が必要:
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
```
