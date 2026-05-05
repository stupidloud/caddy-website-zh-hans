---
title: log_skip (Caddyfile directive)
---

# log_skip

マッチしたリクエストの access logging をスキップします。

これは [`log` ディレクティブ](log) と一緒に使い、不要なリクエストの logging を省きます。

v2.8.0 より前は、このディレクティブは `skip_log` という名前でした。他のディレクティブとの一貫性のために名前が変更されました。


<a id="syntax"></a>
## 構文

```caddy-d
log_skip [<matcher>]
```


<a id="examples"></a>
## 例

サブパスに保存された静的ファイルの access logging をスキップします。

```caddy
example.com {
	root /srv

	log
	log_skip /static*

	file_server
}
```


パターンにマッチするリクエストの access logging をスキップします。この例では、特定の拡張子を持つファイルが対象です。

```caddy-d
@skip path_regexp \.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```


すでに matcher 内の route にある場合、matcher は不要です。たとえば、特定のサブパス用の file server を handle する場合は次のように書けます。

```caddy-d
handle_path /static* {
	root /srv/static
	log_skip
	file_server
}
```
