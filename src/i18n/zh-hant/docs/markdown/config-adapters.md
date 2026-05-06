---
title: 配置適配器 (Config Adapters)
---

<a id="config-adapters"></a>
# 配置適配器 (Config Adapters)

Caddy 原生的配置語言是 [JSON](https://www.json.org/json-en.html)，但手寫 JSON 可能會很繁瑣且容易出錯。這就是為什麼 Caddy 支援透過 **配置適配器 (config adapters)** 使用其他語言進行配置的原因。它們是 Caddy 插件，透過為你輸出 [Caddy JSON](/docs/json/)，讓你可以使用自己偏好的格式。

例如，配置適配器可以 [將你的 NGINX 配置轉換為 Caddy JSON](https://github.com/caddyserver/nginx-adapter)。

<a id="known-config-adapters"></a>
## 已知的配置適配器 (Known config adapters)

目前可用的配置適配器如下（部分為第三方項目）：

- [**caddyfile**](/docs/caddyfile) (標準)
- [**nginx**](https://github.com/caddyserver/nginx-adapter)
- [**jsonc**](https://github.com/caddyserver/jsonc-adapter)
- [**json5**](https://github.com/caddyserver/json5-adapter)
- [**yaml**](https://github.com/abiosoft/caddy-yaml)
- [**cue**](https://github.com/caddyserver/cue-adapter)
- [**toml**](https://github.com/awoodbeck/caddy-toml-adapter)
- [**hcl**](https://github.com/francislavoie/caddy-hcl)
- [**dhall**](https://github.com/mholt/dhall-adapter)
- [**mysql**](https://github.com/zhangjiayin/caddy-mysql-adapter)

<a id="using-config-adapters"></a>
## 使用配置適配器 (Using config adapters)

你可以在大多數接受配置的子命令中使用 `--adapter` 標記來指定配置適配器：

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

或者透過 API 的 [`/load` 端點](/docs/api#post-load)：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

如果你只想獲取輸出的 JSON 而不運行它，可以使用 [`caddy adapt`](/docs/command-line#caddy-adapt) 命令：

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

<a id="caveats"></a>
## 注意事項 (Caveats)

並非所有配置語言都與 Caddy 100% 兼容；某些功能或行為根本無法很好地轉換，或者尚未編程到適配器或 Caddy 本身中。

某些適配器執行 1-1 的轉換，例如 YAML->JSON 或 TOML->JSON。其他的則是專門為 Caddy 設計的，例如 Caddyfile。通常，這些適配器總能正常工作。

然而，並非所有適配器在任何時候都能正常工作。配置適配器會盡力以最高保真度和正確性將你的輸入轉換為 Caddy JSON。由於這個轉換過程不能保證始終完整且正確，我們不稱它們為「轉換器 (converters)」或「翻譯器 (translators)」。它們是「適配器 (adapters)」，因為它們至少會為你提供一個很好的起點，以便完成最終 JSON 配置的製作。

配置適配器可以輸出生成的 JSON、警告和錯誤。如果沒有發生錯誤，則會生成 JSON 結果。當輸入出現問題（例如語法錯誤）時，會發生錯誤。當轉換出現問題但並非致命（例如功能不受支援）時，會發出警告。如果使用帶有警告適配的配置，建議謹慎行事。
