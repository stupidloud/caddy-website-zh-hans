---
title: "入門指南"
---

# 入門指南

歡迎使用 Caddy！本教學將探索使用 Caddy 的基礎知識，並幫助您在宏觀層面熟悉它。

**目標：**
- 🔲 執行守護程序 (daemon)
- 🔲 嘗試 API
- 🔲 為 Caddy 提供設定
- 🔲 測試設定
- 🔲 編寫 Caddyfile
- 🔲 使用設定適配器 (config adapter)
- 🔲 從初始設定開始
- 🔲 比較 JSON 與 Caddyfile
- 🔲 比較 API 與設定檔
- 🔲 在背景執行
- 🔲 零停機設定重新載入

**前置條件：**
- 基礎終端機 / 命令列操作技能
- 基礎文字編輯器操作技能
- 您的 PATH 中已有 `caddy` 和 `curl`

---

**如果您是從軟體包管理器 [安裝 Caddy](/docs/install) 的，Caddy 可能已經作為服務正在執行。如果是這樣，請在進行本教學之前停止該服務。**

讓我們從執行它開始：

<pre><code class="cmd bash">caddy</code></pre>

哎呀；如果沒有子命令，`caddy` 命令只會顯示說明文字。每當您忘記該怎麼做時，都可以使用它。

要將 Caddy 作為守護程序啟動，請使用 `run` 子命令：

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">執行守護程序</aside>

這會一直阻塞，但它在做什麼呢？目前... 什麼也沒做。預設情況下，Caddy 的設定（"config"）是空白的。我們可以在另一個終端機使用 [管理 API](/docs/api) 來驗證這一點：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

這**不是**您的網站：位於 localhost:2019 的管理端點用於控制 Caddy，且預設情況下僅限本機 (localhost) 存取。

</aside>


<aside class="complete">嘗試 API</aside>

我們可以透過給 Caddy 一個設定來讓它發揮作用。這可以透過多種方式實現，但在下一節中，我們將從使用 `curl` 向 [/load](/docs/api#post-load) 端點發送 POST 請求開始。



## 您的第一個設定

為了準備請求，我們需要建立一個設定。從核心上講，Caddy 的設定只是一個 [JSON 文件](/docs/json/)。

將其儲存到 JSON 檔案（例如 `caddy.json`）：

```json
{
	"apps": {
		"http": {
			"servers": {
				"example": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

<aside class="tip">

您不必使用設定檔，但在本教學中我們會使用。Caddy 的 [管理 API](/docs/api) 設計用於其他程式或指令碼。

</aside>


然後上傳它：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">為 Caddy 提供設定</aside>

我們可以透過另一個 GET 請求來驗證 Caddy 是否套用了我們的新設定：

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

在瀏覽器中造訪 [localhost:2015](http://localhost:2015) 或使用 `curl` 來測試它是否正常運作：

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

如果您看到 _Hello, world!_，那麼恭喜——它正在運作！確保您的設定如預期般運作總是一個好主意，特別是在部署到生產環境之前。

<aside class="complete">測試設定</aside>


## 您的第一個 Caddyfile

僅僅為了 Hello World，那感覺有點麻煩。

另一種設定 Caddy 的方式是使用 [**Caddyfile**](/docs/caddyfile)。上面我們用 JSON 編寫的相同設定可以簡單地表示為：

```caddy
:2015

respond "Hello, world!"
```


將其儲存到目前目錄下名為 `Caddyfile`（無副檔名）的檔案中。

<aside class="complete">編寫 Caddyfile</aside>

如果 Caddy 已經在執行，請停止它（<kbd>Ctrl</kbd>+<kbd>C</kbd>），然後執行：

<pre><code class="cmd bash">caddy adapt</code></pre>

或者，如果您將 Caddyfile 儲存在其他地方或將其命名為 `Caddyfile` 以外的其他名稱：

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile</code></pre>

您將看到 JSON 輸出！這裡發生了什麼？

我們剛剛使用了一個 [ _設定適配器 (config adapter)_ ](/docs/config-adapters) 將我們的 Caddyfile 轉換為 Caddy 的原生 JSON 結構。

<aside class="complete">使用設定適配器</aside>

雖然我們可以獲取該輸出並發出另一個 API 請求，但我們可以跳過所有這些步驟，因為 `caddy` 命令可以為我們完成。如果目前目錄下有一個名為 Caddyfile 的檔案，且沒有指定其他設定，Caddy 將載入該 Caddyfile，為我們進行適配，並立即執行。

現在目前資料夾中有一個 Caddyfile，讓我們再次執行 `caddy run`：

<pre><code class="cmd bash">caddy run</code></pre>

或者如果您的 Caddyfile 在其他地方：

<pre><code class="cmd bash">caddy run --config /path/to/Caddyfile</code></pre>

（如果它的名稱不是以 "Caddyfile" 開頭，您需要指定 `--adapter caddyfile`。）

現在您可以嘗試再次載入您的網站，您將看到它正在運作！

<aside class="complete">從初始設定開始</aside>

如您所見，有幾種方法可以使用初始設定啟動 Caddy：

- 目前目錄下名為 Caddyfile 的檔案
- `--config` 標誌（可選配合 `--adapter` 標誌）
- `--resume` 標誌（如果之前載入過設定）


## JSON vs. Caddyfile

現在您知道 Caddyfile 只是為您轉換成了 JSON。

Caddyfile 看起來比 JSON 更簡單，但您應該總是使用它嗎？每種方法都有利有弊。答案取決於您的需求和使用場景。

JSON | Caddyfile
-----|----------
易於生成 | 易於手工編寫
易於程式化 | 難以自動化
極具表現力 | 表現力適中
涵蓋 Caddy 的全部功能 | 涵蓋 Caddy 的大部分功能
允許設定遍歷 | 無法在 Caddyfile 內部遍歷
支援局部設定更改 | 僅限整體設定更改
可以匯出 | 無法匯出
相容所有 API 端點 | 相容部分 API 端點
文件自動生成 | 文件是手工編寫的
無處不在 | 較小眾
更高效 | 計算開銷稍大
有點無聊 | 挺有趣的
**了解更多：[JSON 結構](/docs/json/)** | **了解更多：[Caddyfile 文件](/docs/caddyfile)**

您需要決定哪種最適合您的使用場景。

重要的是要注意，JSON 和 Caddyfile（以及 [任何其他受支援的設定適配器](/docs/config-adapters)）都可以與 [Caddy 的 API](/docs/api) 配合使用。但是，如果您使用 JSON，則可以獲得 Caddy 的全部功能和 API 特性。如果使用設定適配器，透過 API 載入或更改設定的唯一方法是使用 [/load 端點](/docs/api#post-load)。

<aside class="complete">比較 JSON 與 Caddyfile</aside>


## API vs. 設定檔

<aside class="tip">

在底層，即使是設定檔也會透過 Caddy 的 API 端點；`caddy` 命令只是為您包裝了這些 API 呼叫。

</aside>


您還需要決定您的工作流程是基於 API 的還是基於 CLI 的。（您 _可以_ 在同一台伺服器上同時使用 API 和設定檔，但我們不建議這樣做：最好只有一個真理來源。）

API | 設定檔
----|-------------
透過 HTTP 請求更改設定 | 透過 shell 命令更改設定
易於擴充 | 難以擴充
難以手動管理 | 易於手動管理
非常有趣 | 同樣有趣
**了解更多：[API 教學](/docs/api-tutorial)** | **了解更多：[Caddyfile 教學](/docs/caddyfile-tutorial)**

<aside class="tip">
	使用適當的工具（例如任何 REST 客戶端應用程式）手動透過 API 管理伺服器設定是完全可行的。
</aside>

選擇 API 還是設定檔工作流程與設定適配器的使用是相互獨立的：您可以使用 JSON 但將其儲存在檔案中並使用命令列介面；反之，您也可以將 Caddyfile 與 API 配合使用。

但大多數人會使用 JSON+API 或 Caddyfile+CLI 的組合。

如您所見，Caddy 非常適合各種使用場景和部署環境！

<aside class="complete">比較 API 與設定檔</aside>



## 啟動、停止、執行

由於 Caddy 是伺服器，它會無限期執行。這意味著在執行 `caddy run` 後，您的終端機將一直處於阻塞狀態，直到程序被終止（通常使用 <kbd>Ctrl</kbd>+<kbd>C</kbd>）。

雖然 `caddy run` 是最常用的，也是通常推薦的做法（特別是在建立系統服務時！），您也可以選擇使用 `caddy start` 來啟動 Caddy 並讓它在背景執行：

<pre><code class="cmd bash">caddy start</code></pre>

這將讓您可以再次使用終端機，這在某些互動式無頭環境中非常方便。

然後您必須自己停止該程序，因為 <kbd>Ctrl</kbd>+<kbd>C</kbd> 不會為您停止它：

<pre><code class="cmd bash">caddy stop</code></pre>

或者使用 API 的 [/stop 端點](/docs/api#post-stop)。

<aside class="complete">在背景執行</aside>


## 重新載入設定

您的伺服器可以執行零停機設定重新載入/更改。

所有載入或更改設定的 [API 端點](/docs/api) 都是平順的且零停機。

然而，在使用命令列時，可能很想使用 <kbd>Ctrl</kbd>+<kbd>C</kbd> 来停止伺服器，然後再次重新啟動以載入新設定。請不要這樣做：停止和啟動伺服器與設定更改是相互獨立的，並且會導致停機。

<aside class="tip">
	停止伺服器將導致服務中斷。
</aside>

相反，請使用 [`caddy reload`](/docs/command-line#caddy-reload) 命令進行平順的設定更改：

<pre><code class="cmd bash">caddy reload</code></pre>

這實際上只是在底層使用了 API。它將載入設定，並在必要时將您的設定檔適配為 JSON，然後平順地替換活動設定，而無需停機。

如果在載入新設定時出現任何錯誤，Caddy 會回退到上一個有效設定。

<aside class="tip">
	從技術上講，新設定在舊設定停止之前就已經啟動，因此在極短的時間內，兩個設定都在執行！如果新設定失敗，它會因錯誤而中止，而舊設定則不會停止。
</aside>

<aside class="complete">零停機設定重新載入</aside>
