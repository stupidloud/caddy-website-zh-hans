---
title: Caddyfile 快速入門
---

<a id="caddyfile-quick-start"></a>
# Caddyfile 快速入門

建立一個名為 `Caddyfile`（無副檔名）的新文字檔。

在 Caddyfile 中要輸入的第一件事是您網站的位址：

```caddy
localhost
```

<aside class="tip">

如果 HTTP 和 HTTPS 連接埠（分別為 80 和 443）在您的 OS 上是受限埠，您將需要以提升的權限運行或使用更高的連接埠。若要獲得權限，請使用 `sudo -E` 以 root 身分運行，或使用 `sudo setcap cap_net_bind_service=+ep $(which caddy)`。或者，若要使用更高的連接埠，只需將位址更改為類似 `localhost:2080` 的內容，並使用 [`http_port`](/docs/caddyfile/options) Caddyfile 選項更改 HTTP 連接埠。

</aside>

然後按 Enter 並輸入您希望它執行的操作，使其看起來像這樣：

```caddy
localhost

respond "Hello, world!"
```

儲存此檔案並在包含您的 Caddyfile 的同一個資料夾中運行 Caddy：

<pre><code class="cmd bash">caddy start</code></pre>

系統可能會要求您輸入密碼，因為 Caddy 預設會透過 HTTPS 提供所有網站服務 —— 即使是本地網站。（密碼提示應該只在第一次出現！）

<aside class="tip">

對於本地 HTTPS，Caddy 會自動為您生成憑證和唯一的私鑰。根憑證會被添加到您系統的信任存放區，這就是為什麼密碼提示是必要的。它允許您在本地透過 HTTPS 進行開發而不會出現憑證錯誤。

</aside>

（如果您遇到權限錯誤，您可能需要以提升的權限運行或選擇高於 1023 的連接埠。）

您可以直接在瀏覽器中開啟 [localhost](http://localhost) 或使用 `curl`：

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Hello, world!</code></pre>

您可以透過將多個網站包裹在大括號 `{ }` 中，在一個 Caddyfile 中定義它們。將您的 Caddyfile 更改為：

```caddy
localhost {
	respond "Hello, world!"
}

localhost:2016 {
	respond "Goodbye, world!"
}
```

您可以透過兩種方式為 Caddy 提供更新後的配置，一種是直接使用 API：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

或是使用 `reload` 命令，它會為您執行相同的 API 請求：

<pre><code class="cmd bash">caddy reload</code></pre>

在 [瀏覽器中](https://localhost:2016) 或使用 `curl` 測試您的新「goodbye」端點，以確保其正常運作：

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Goodbye, world!</code></pre>

當您完成 Caddy 的使用後，請務必將其停止：

<pre><code class="cmd bash">caddy stop</code></pre>

<a id="further-reading"></a>
## 進一步閱讀

- [Caddyfile 概念](/docs/caddyfile/concepts)
- [指令](/docs/caddyfile/directives)
- [常見模式](/docs/caddyfile/patterns)
