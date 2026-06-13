---
title: templates (Caddyfile 指令)
---

<a id="templates"></a>
# templates

將回應主體作為 [template](/docs/modules/http.handlers.templates) 檔案執行。Templates 提供了一些功能原語，用於製作簡單的動態頁面。功能包括 HTTP 子請求、HTML 檔案包含、Markdown 渲染、JSON 解析、基本資料結構、隨機性、時間等。

<aside class="tip">

模板可能會在來自*任何*來源的回應主體上執行，無論它是磁碟上的靜態檔案，還是被代理的 Web 服務。明智的做法是只對你信任、可控和/或已淨化的內容啟用模板求值！設定不當可能導致安全漏洞。例如，如果一個被代理的應用允許使用者撰寫/發佈內容，而這些內容包含看起來像模板操作的文字，就會讓任意使用者得以執行模板，並可能藉此存取環境變數、本機檔案和網路。不要在使用者生成的內容上啟用模板（除非已先淨化）。

</aside>


<a id="syntax"></a>
## 語法

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

- **mime** 是 templates 中間件將作用的 MIME 類型；任何不具有合格 `Content-Type` 的回應都不會被作為 templates 評估。

  預設值：`text/html text/plain`。

- **between** 是 template 動作的開頭和結尾分隔符。如果它們與文件中的其他部分衝突，你可以更改它們。

  預設值：`{{printf "{{ }}"}}`。

- **root** 是存取檔案系統的功能時使用的站點根目錄。

  預設為 [`root`](root) 指令設置的站點根目錄，如果未設置，則為當前工作目錄。

- **extensions** 允許你註冊由 `http.handlers.templates.functions.*` 命名空間中的模組提供的自定義 template 函式。

  區塊內的每個子指令對應一個模組名稱。這些模組可以向 template 函式映射添加自定義函式，通常用於實現可重用的元件。此功能主要用於外掛。

內建 template 函式的文檔可以在 [templates 模組](/docs/modules/http.handlers.templates#docs) 中找到。



<a id="examples"></a>
## 範例

有關使用 templates 提供 markdown 的完整站點範例，請查看 [本網站](https://github.com/caddyserver/website) 的原始碼！具體來說，請查看 [`Caddyfile`](https://github.com/caddyserver/website/blob/master/Caddyfile) 和 [`src/docs/index.html`](https://github.com/caddyserver/website/blob/master/src/docs/index.html)。

為靜態站點啟用 templates：

```caddy
example.com {
	root /srv
	templates
	file_server
}
```

要使用 template 提供簡單的靜態回應，請務必設置 `Content-Type`：

```caddy
example.com {
	header Content-Type text/plain
	templates
	respond `Current year is: {{printf "{{"}}now | date "2006"{{printf "}}"}}`
}
```

使用 template 擴充（外掛）：

```caddy
example.com {
	root /srv
	templates {
		extensions {
			# 需要 caddy-hitcounter 外掛：
			# https://github.com/mholt/caddy-hitcounter
			hitCounter {
				style bright_green
				pad_digits 6
			}
		}
	}
	file_server
}
