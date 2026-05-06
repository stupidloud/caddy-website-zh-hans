---
title: log_skip (Caddyfile 指令)
---

<a id="log_skip"></a>
# log_skip

跳過符合條件請求的存取日誌。

這應該與 [`log` 指令](log) 配合使用，以跳過對您的需求不相關的請求日誌記錄。

在 v2.8.0 版本之前，此指令被命名為 `skip_log`，但為了與其他指令保持一致而重新命名。


<a id="syntax"></a>
## 語法

```caddy-d
log_skip [<matcher>]
```


<a id="examples"></a>
## 範例

跳過存儲在子路徑中的靜態文件的存取日誌記錄：

```caddy
example.com {
	root /srv

	log
	log_skip /static*

	file_server
}
```


跳過符合特定模式的請求存取日誌記錄；在這種情況下，是針對具有特定副檔名的文件：

```caddy-d
@skip path_regexp \.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```


如果在已經處於 matcher 中的 route 內，則不需要 matcher。例如，對於特定子路徑的文件伺服器使用 handle：

```caddy-d
handle_path /static* {
	root /srv/static
	log_skip
	file_server
}
```
