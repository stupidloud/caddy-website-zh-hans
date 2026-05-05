---
title: request_header (Caddyfile directive)
---

# request_header

リクエストの HTTP header フィールドを操作します。header 値の設定、追加、削除、または正規表現による置換ができます。

proxy 用に header を操作したい場合は、代わりに `reverse_proxy` の [`header_up` サブディレクティブ](/docs/caddyfile/directives/reverse_proxy#header_up) を使用してください。こちらは proxy の処理を考慮して動作します。

HTTP レスポンス header を操作するには、[`header`](header) ディレクティブを使用できます。


<a id="syntax"></a>
## 構文

```caddy-d
request_header [<matcher>] [[+|-]<field> [<value>|<find>] [<replace>]]
```

- **&lt;field&gt;** は header フィールド名です。

  prefix がない場合、フィールドは設定されます（上書きされます）。

  `+` を prefix に付けると、既存のフィールドを上書き（設定）するのではなく追加します。header フィールドは 1 つのリクエスト内に複数回現れることがあります。

  `-` を prefix に付けると、フィールドを削除します。フィールド名には prefix または suffix の `*` ワイルドカードを使い、一致するすべてのフィールドを削除できます。

- **&lt;value&gt;** は、フィールドを追加または設定する場合の header フィールド値です。

- **&lt;find&gt;** は、検索する部分文字列または正規表現です。

- **&lt;replace&gt;** は置換後の値です。検索置換を行う場合は必須です。


<a id="examples"></a>
## 例

リクエストから Referer header を削除します。

```caddy-d
request_header -Referer
```

リクエストからアンダースコアを含むすべての header を削除します。

```caddy-d
request_header -*_*
```
