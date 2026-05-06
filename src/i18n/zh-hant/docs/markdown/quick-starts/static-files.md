---
title: 靜態檔案快速入門
---

<a id="static-files-quick-start"></a>
# 靜態檔案快速入門

本指南將向你展示如何快速建立並運行一個生產就緒的靜態檔案伺服器。

**Prerequisites:** 
- 基礎的終端機 / 命令列技能
- 在你的 PATH 中有 `caddy`
- 一個包含你的網站的資料夾

---

有兩種簡單的方法可以快速啟動檔案伺服器。

<a id="command-line"></a>
## 命令列

在你的終端機中，切換到網站的根目錄並執行：

<pre><code class="cmd bash">caddy file-server</code></pre>

如果你收到權限錯誤，這可能意味著你的作業系統不允許你綁定到低埠號 —— 因此請改用高埠號：

<pre><code class="cmd bash">caddy file-server --listen :2015</code></pre>

然後在瀏覽器中開啟 [localhost](http://localhost)（或 [localhost:2015](http://localhost:2015)）即可查看你的網站！

如果你沒有索引檔案（index file），但想顯示檔案列表，請使用 `--browse` 選項：

<pre><code class="cmd bash">caddy file-server --browse</code></pre>

你可以使用另一個資料夾作為網站根目錄：

<pre><code class="cmd bash">caddy file-server --root ~/mysite</code></pre>



<a id="caddyfile"></a>
## Caddyfile

在網站的根目錄中，建立一個名為 `Caddyfile` 的檔案，內容如下：

```caddy
localhost

file_server
```

如果你沒有權限綁定到低埠號，請將 `localhost` 替換為 `localhost:2015`（或其他高埠號）。

然後，在同一個目錄中執行：

<pre><code class="cmd bash">caddy run</code></pre>

接著你可以載入 [localhost](https://localhost)（或你的設定中的任何地址）來查看網站！

[`file_server` 指令](/docs/caddyfile/directives/file_server) 有更多選項供你自定義網站。當你更改 Caddyfile 時，請務必 [重新載入](/docs/command-line#caddy-reload) Caddy（或停止並重新啟動）！

如果你沒有索引檔案，但想顯示檔案列表，請使用 `browse` 參數：

```caddy
localhost

file_server browse
```

你也可以使用另一個資料夾作為網站根目錄：

```caddy
localhost

root /var/www/mysite
file_server
```
