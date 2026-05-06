---
title: fs (Caddyfile 指令)
---

<a id="fs"></a>
# fs

設定用於執行檔案 I/O 的檔案系統。

這可以讓您連接到在雲端運行的遠端檔案系統、具有類檔案介面的資料庫，甚至是從嵌入在 Caddy 二進位檔案中的檔案讀取。

首先，您必須使用 [`filesystem` 全域選項](/docs/caddyfile/options#filesystem) 聲明一個檔案系統名稱，然後您可以使用此指令指定要使用的檔案系統。

此指令通常與 [`file_server` 指令](file_server) 配合使用以提供靜態檔案，或與 [`try_files` 指令](try_files) 配合使用以根據檔案是否存在執行重寫。通常也與 [`root` 指令](root) 配合使用以在檔案系統中設定根路徑。


<a id="syntax"></a>
## Syntax

```caddy-d
fs [<matcher>] <filesystem>
```

<a id="examples"></a>
## Examples

使用一個名為 `foo` 的檔案系統，並使用一個名為 `custom` 的虛構模組，該模組可能需要身份驗證：

```caddy
{
	filesystem foo custom {
		api_key abc123
	}
}

example.com {
	fs foo
	root /srv
	file_server
}
```

僅從 `foo` 檔案系統提供圖像，其餘部分從預設檔案系統提供：

```caddy
example.com {
	fs /images* foo
	root /srv
	file_server
}
```
