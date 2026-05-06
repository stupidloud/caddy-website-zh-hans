---
title: 架構
---

架構
====

Caddy 是一個單一、自包含的靜態二進位檔案，由於它是用 Go 編寫的，因此完全沒有外部依賴。這些價值觀構成了專案願景的重要組成部分，因為它們簡化了部署並減少了生產環境中繁瑣的疑難排解。

如果沒有動態連結，那該如何擴充呢？Caddy 擁有一種新穎的插件架構，使其功能遠遠超出了任何其他 Web 伺服器，甚至是那些具有外部（動態連結）依賴的伺服器。

我們「更少的移動部件」之哲學最終帶來了更可靠、更易於管理且成本更低的網站&mdash;特別是在大規模情況下。這份半技術性文件描述了我們如何透過軟體工程實現這一目標。


<a id="overview"></a>
## 概覽

Caddy 由 command、core 函式庫和 modules 組成。

**command** 提供了你可能已經熟悉的 [命令列介面](/docs/command-line)。這就是你從作業系統啟動程序的方式。這裡的程式碼和邏輯量相當少，僅包含以使用者想要的方式引導 core 所需的內容。我們刻意避免使用 flag 和環境變數進行配置，除非它們與引導配置有關。


<aside class="tip">

Modules 可以向命令列介面添加子命令！例如，[`caddy file-server`](/docs/command-line#caddy-file-server) 命令就是由此而來的。這些新增的命令可以擁有任何 flag 或使用任何它們想要的環境變數，儘管 Caddy 的核心命令盡量減少了它們的使用。

</aside>


**[core 函式庫](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc)**，或稱 Caddy 的「core」，主要管理配置。它可以 [`Run()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Run) 一個新的配置或 [`Stop()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Stop) 一個正在運行的配置。它還為 modules 提供了各種實用工具、類型和值。

**Modules** 負責其餘的一切。許多 modules 內建於 Caddy 中，稱為 *標準 modules*。 這些被認為是對大多數使用者最有用的。


<aside class="tip">

有時 *module*、*plugin* 和 *extension* 這些術語會互換使用，通常這沒問題。技術上來說，所有的 modules 都是 plugins，但並非所有的 plugins 都是 modules。Modules 特指一種擴充 Caddy [配置結構](/docs/json/) 的 plugin。

</aside>




<a id="caddy-core"></a>
## Caddy core

在核心層面，Caddy 僅僅是載入初始配置（「config」），或者如果沒有初始配置，則開啟一個通訊端以便稍後接受新配置。

一個 [Caddy 配置](/docs/json/) 是一個 JSON 文件，其頂層有一些欄位：

```json
{
	"admin": {},
	"logging": {},
	"apps": {•••},
	...
}
```

Caddy 的核心知道如何原生處理其中一些欄位：

- [`admin`](/docs/json/admin/) 這樣它就可以設置 [admin API](/docs/api) 並管理程序
- [`logging`](/docs/json/logging/) 這樣它就可以 [發出日誌](/docs/logging)

但其他的頂層欄位（例如 [`apps`](/docs/json/apps/)）對 Caddy 核心來說是不透明的。事實上，Caddy 對於 `apps` 中的位元組所知道的唯一操作，就是將它們反序列化為一個可以調用兩個方法的介面類型：

1. `Start()`
2. `Stop()`

... 僅此而已。當配置載入時，它會對每個 app 調用 `Start()`，當配置卸載時，則對每個 app 調用 `Stop()`。

當一個 app module 啟動時，它會啟始該 app 的 module 生命週期。


<aside class="tip">

如果你是正在開發 Caddy modules 的程式設計師，你可以在我們的 [擴充 Caddy](/docs/extending-caddy) 指南中找到類似的資訊，但會更側重於程式碼。

</aside>


<a id="module-lifecycle"></a>
## Module lifecycle

有兩種 modules：*host modules* 和 *guest modules*。

**Host modules**（或「父」modules）是那些載入其他 modules 的模組。

**Guest modules**（或「子」modules）是那些被載入的模組。所有的 modules 都是 guest modules -- 甚至是 app modules。

Modules 被載入、配置（provisioned）和驗證、使用，然後被清理，遵循以下順序：

1. 載入 (Loaded)
2. 配置與驗證 (Provisioned and validated)
3. 使用 (Used)
4. 清理 (Cleaned up)

當配置載入時，Caddy 首先透過初始化所有已配置的 app modules 來啟動 module 生命週期。從那裡開始，就像「烏龜背著烏龜」一樣，每個 app module 會繼續完成剩下的部分。

<a id="load-phase"></a>
### Load phase

載入一個 module 涉及將其 JSON 位元組反序列化為記憶體中的類型值。基本上... 就是這樣。這只是將 JSON 解碼為一個值。

<a id="provision-phase"></a>
### Provision phase

這個階段是大多數設置工作進行的地方。所有 modules 在載入後都有機會進行自我配置。

由於來自 JSON 編碼的任何屬性都已經被解碼，這裡只需要進行額外的設置。在配置過程中最常見的任務是設置 guest modules。換句話說，配置一個 host module 也會導致其 guest modules 的配置，依此類推。

你可以透過 [在我們的文件中查看 Caddy 的 JSON 結構](/docs/json/) 來了解這一點。任何你看到 `{•••}` 的地方就是可以使用 guest modules 的地方；當你點擊進去時，你可以繼續探索下去，直到沒有更多的 guest modules 為止。

其他常見的配置任務是設置在 module 生命周期內將使用的內部值，或將輸入標準化。例如，[`http.matchers.remote_ip`](/docs/modules/http.matchers.remote_ip) module 使用配置階段從它從 JSON 接收到的字串輸入中解析 CIDR 值。這樣，它就不必在每次 HTTP 請求期間執行此操作，因此效率更高。

驗證也可以在配置階段進行。如果 module 最終的配置無效，則可以在此處返回錯誤，從而中止整個配置載入過程。

<a id="use-phase"></a>
### Use phase

一旦 guest module 經過配置和驗證，它就可以被其 host module 使用。這具體意味著什麼取決於每個 host module。

每個 module 都有一個 ID，由一個命名空間和該命名空間中的一個名稱組成。例如，[`http.handlers.reverse_proxy`](/docs/modules/http.handlers.reverse_proxy) 是一個 HTTP handler，因為它在 `http.handlers` 命名空間中，其名稱為 `reverse_proxy`。`http.handlers` 命名空間中的所有 modules 都滿足 host module 所知的相同介面。因此，`http` app 知道如何載入和使用這些類型的 modules。

<a id="cleanup-phase"></a>
### Cleanup phase

當需要停止配置時，所有的 modules 都會被卸載。如果 module 分配了任何應釋放的資源，它有機會在清理階段執行此操作。


<a id="plugging-in"></a>
## Plugging in

一個 module -- 或任何 Caddy plugin -- 透過為 module 的套件添加一個 `import` 來「插入」到 Caddy 中。透過導入套件，[該 module 會向 Caddy 核心註冊自己](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule)，因此當 Caddy 程序啟動時，它知道每個 module 的名稱。它甚至可以在 module 值和名稱之間建立關聯，反之亦然。


<aside class="tip">

插件可以在完全不修改 Caddy 程式碼庫的情況下添加。在 [讀我文件 (readme)](https://github.com/caddyserver/caddy/#with-version-information-andor-plugins) 中有相關說明！

</aside>


<a id="managing-configuration"></a>
## 管理配置

對於伺服器所需的高層級併發和數千個參數，更改正在運行的伺服器之活動配置（通常稱為「重載 (reload)」）可能會很棘手。Caddy 使用一種具有許多優點的設計優雅地解決了這個問題：

- 不中斷正在運行的服務
- 可以進行細粒度的配置更改
- 只需要一個鎖（在背景中）
- 所有的重載都是原子性 (atomic)、一致性 (consistent)、隔離性 (isolated) 且大部分持久的 (durable)（「ACID」）
- 極少的全域狀態

你可以 [在這裡觀看關於 Caddy 2 設計的影片](https://www.youtube.com/watch?v=EhJO8giOqQs)。

配置重載的工作原理是配置新的 modules，如果全部成功，則清理舊的 modules。在短暫的時間內，兩個配置會同時運作。

每個配置都與一個 [context](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context) 相關聯，該 context 保存了所有的 module 狀態，因此大多數狀態永遠不會超出配置的範圍。這對於正確性、效能和簡潔性來說是個好消息！

然而，有時真正全域的狀態是必要的。例如，reverse_proxy 可能會追蹤其 upstreams 的健康狀況；由於全域每個 upstream 只有一個，如果每次進行微小的配置更改時都忘記它們，那將是很糟糕的。幸運的是，Caddy [提供了類似於](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#UsagePool) 語言運行時垃圾回收機制的設施，以保持全域狀態整潔。

線上配置更新的一個顯而易見的方法是同步存取每個配置參數，即使在熱路徑 (hot paths) 中也是如此。就效能和複雜性而言，這簡直是糟糕透頂&mdash;特別是在大規模情況下&mdash;因此 Caddy 不使用這種方法。

相反，配置被視為不可變的原子單元：要麼整個更換，要麼什麼都不更改。[admin API 端點](/docs/api)&mdash;允許透過遍歷結構進行細粒度更改&mdash;僅修改配置的記憶體表示，並由此生成並載入一個全新的配置文件。這種方法在簡潔性、效能和一致性方面具有巨大的優勢。由於只有一個鎖，Caddy 很容易處理快速重載。
