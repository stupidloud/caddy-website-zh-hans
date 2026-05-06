---
title: log_name (Caddyfile 指令)
---

<a id="log-name"></a>
# log_name

使用 [**log** 指令](log) 寫入存取記錄時，覆寫用於請求的記錄器名稱。

當你想根據某些條件（例如請求路徑或方法）將請求記錄到不同的檔案時，此指令非常有用。

可以指定多個記錄器名稱，這樣請求的記錄就會被推送到多個匹配的記錄器。

這通常與 **log** 指令的 [**no_hostname**](log#no_hostname) 選項配合使用，該選項可防止記錄器與站點區塊的任何主機名關聯，因此只有設置了 **log_name** 的請求才會將記錄推送到該記錄器。


<a id="syntax"></a>
## 語法

```caddy-d
log_name [<matcher>] <names...>
```


<a id="examples"></a>
## 範例

您可能想將請求記錄到不同的檔案，例如，您可能想將健康檢查與主存取記錄分開記錄。

在 **log** 中使用 **no_hostname** 可防止記錄器與站點區塊的任何主機名（即此處的 **localhost**）關聯，因此只有將 **log_name** 設置為該記錄器名稱的請求才會收到記錄。

```caddy
localhost {
	log {
		output file ./caddy.access.log
	}

	log health_check_log {
		output file ./caddy.access.health.log
		no_hostname
	}

	handle /healthz* {
		log_name health_check_log
		respond "Healthy"
	}

	handle {
		respond "Hello World"
	}
}
```
