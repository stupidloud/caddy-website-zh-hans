---
title: try_files (Caddyfile 指令)
---

<a id="try-files"></a>
# try_files

將請求的 URI 路徑重寫為站點 root 中存在的第一個列出的檔案。如果沒有相符的檔案，則不執行重寫。


<a id="syntax"></a>
## 語法

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **<files...>** 是要嘗試的檔案列表。URI 路徑將被重寫為第一個存在的檔案。

  要相符目錄，請在路徑末尾添加斜線 `/`。所有檔案路徑都是相對於站點 [root](root) 的，並且將展開 [glob 模式](https://pkg.go.dev/path/filepath#Match)。

  每個參數也可以包含查詢字串，在這種情況下，如果相符該特定檔案，查詢字串也將被更改。

  如果 `try_policy` 是 `first_exist`（預設值），則列表中的最後一項可以是一個以 `=` 開頭的數字（例如 `=404`），作為回退方案，它將發出具有該代碼的錯誤；該錯誤可以由 [`handle_errors`](handle_errors) 捕獲並處理。

- **policy** 是從檔案列表中選擇檔案的策略。

  預設值：`first_exist`



<a id="expanded-form"></a>
## 擴展形式

`try_files` 指令基本上是以下內容的捷徑：

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

請注意，此指令不接受 matcher 標記。如果您需要更複雜的匹配邏輯，請以上述擴展形式為基礎。

有關更多詳細資訊，請參閱 [`file` matcher](/docs/caddyfile/matchers#file)。



<a id="examples"></a>
## 範例

如果請求不相符任何靜態檔案，則重寫到您的 PHP index/router 進入點：

```caddy-d
try_files {path} /index.php
```

同上，但將原始路徑添加到查詢字串（某些舊版 PHP 應用程式需要）：

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

同上，但也相符目錄：

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

如果存在，嘗試重寫到檔案或目錄，否則發出 404 錯誤（可以由 [`handle_errors`](handle_errors) 捕獲並處理）：

```caddy-d
try_files {path} {path}/ =404
```

選擇最近部署的靜態檔案版本（例如在請求 `index.html` 時提供 `index.be331df.html`）：

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
