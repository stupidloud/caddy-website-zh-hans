---
title: Konfigurationsadapter
---

# Konfigurationsadapter

Die native Konfigurationssprache von Caddy ist [JSON](https://www.json.org/json-en.html), aber das manuelle Schreiben von JSON kann mühsam und anfällig für error sein. Aus diesem Grund unterstützt Caddy die Konfiguration mit anderen Sprachen über **Konfigurationsadapter**. Dabei handelt es sich um Caddy-Plugins, die es ermöglichen, die Konfiguration in Ihrem bevorzugten Format zu verwenden, indem sie [Caddy JSON](/docs/json/) für Sie ausgeben.

Beispielsweise könnte ein Konfigurationsadapter [Ihre NGINX-Konfiguration in Caddy JSON umwandeln](https://github.com/caddyserver/nginx-adapter).

## Bekannte Konfigurationsadapter

Die folgenden Konfigurationsadapter sind derzeit verfügbar (einige sind Projekte von Drittanbietern):

- [**caddyfile**](/docs/caddyfile) (Standard)
- [**nginx**](https://github.com/caddyserver/nginx-adapter)
- [**jsonc**](https://github.com/caddyserver/jsonc-adapter)
- [**json5**](https://github.com/caddyserver/json5-adapter)
- [**yaml**](https://github.com/abiosoft/caddy-yaml)
- [**Stichwort**](https://github.com/caddyserver/cue-adapter)
- [**toml**](https://github.com/awoodbeck/caddy-toml-adapter)
- [**hcl**](https://github.com/francislavoie/caddy-hcl)
- [**dhall**](https://github.com/mholt/dhall-adapter)
- [**MySQL**](https://github.com/zhangjiayin/caddy-mysql-adapter)

## Verwendung von Konfigurationsadaptern

Sie können einen Konfigurationsadapter verwenden, indem Sie ihn in der Befehlszeile angeben, indem Sie bei den meisten Unterbefehlen, die eine Konfiguration annehmen, das Flag `--adapter` verwenden:

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

Or via the API at the [`/load` endpoint](/docs/api#post-load):

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

Wenn Sie nur die Ausgabe JSON erhalten möchten, ohne sie auszuführen, können Sie den Befehl [`caddy adapt`](/docs/command-line#caddy-adapt) verwenden:

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

## Vorbehalte

Not all config languages are 100% compatible with Caddy; some features or behaviors simply don't translate well or are not yet programmed into the adapter or Caddy itself.

Some adapters do a 1-1 translation, like YAML->JSON or TOML->JSON. Others are designed specifically for Caddy, like the Caddyfile. Generally, these adapters will always work.

However, not all adapters work all of the time. Config adapters do their best to translate your input to Caddy JSON with the highest fidelity and correctness. Because this conversion process is not guaranteed to be complete and correct all the time, we don't call them "converters" or "translators". They are "adapters" since they will at least give you a good starting point to finish crafting your final JSON config.

Config adapters can output the resulting JSON, warnings, and errors. JSON results if no errors occur. Errors occur when something is wrong with the input (for example, syntax errors). Warnings are emitted when something is wrong with the adaptation but which is not necessarily fatal (for example, feature not supported). Caution is advised if using configs that were adapted with warnings.
