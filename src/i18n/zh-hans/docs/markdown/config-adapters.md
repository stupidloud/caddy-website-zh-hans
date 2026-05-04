---
title: "配置适配器"
---

# 配置适配器

Caddy 的默认配置语言是 [JSON](https://www.json.org/json-en.html)，但手动编写 JSON 既费时又容易出错。因此，Caddy 支持通过 **配置适配器** 使用其他语言进行配置。这些适配器是 Caddy 插件，它们会自动将配置转换为 [Caddy JSON](/docs/json/) 格式，从而让你能够使用自己喜欢的格式进行配置。

例如，一个配置适配器可以将[您的 NGINX 配置转换为 Caddy JSON](https://github.com/caddyserver/nginx-adapter) 格式。

## 已知的配置适配器

目前提供以下配置适配器（其中部分为第三方项目）：

- [**caddyfile**](/docs/caddyfile)（标准）
- [**nginx**](https://github.com/caddyserver/nginx-adapter)
- [**jsonc**](https://github.com/caddyserver/jsonc-adapter)
- [**json5**](https://github.com/caddyserver/json5-adapter)
- [**yaml**](https://github.com/abiosoft/caddy-yaml)
- [**提示**](https://github.com/caddyserver/cue-adapter)
- [**toml**](https://github.com/awoodbeck/caddy-toml-adapter)
- [**hcl**](https://github.com/francislavoie/caddy-hcl)
- [**dhall**](https://github.com/mholt/dhall-adapter)
- [**mysql**](https://github.com/zhangjiayin/caddy-mysql-adapter)

## 使用配置适配器

您可以通过在命令行中使用 `--adapter` 标志，在支持配置的大多数子命令中进行指定：

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

或者通过 API 的 [`/load` 端点](/docs/api#post-load)：

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

如果你只想获取输出 JSON 而不执行该命令，可以使用 [`caddy adapt`](/docs/command-line#caddy-adapt) 命令：

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

## 注意事项

并非所有配置语言都与 Caddy 100% 兼容；某些功能或行为可能无法很好地转换，或者尚未被编程到适配器或 Caddy 本身中。

有些适配器支持一对一转换，例如 YAML→JSON 或 TOML→JSON。还有些则是专门为 Caddy 设计的，例如 Caddyfile。通常情况下，这些适配器都能正常工作。

不过，并非所有适配器都能始终正常工作。配置适配器会竭尽全力，以最高保真度和准确性将您的输入转换为 Caddy JSON。由于无法保证该转换过程始终完整且正确，因此我们不称其为“转换器”或“翻译器”。它们被称为“适配器”，因为它们至少能为您提供一个良好的起点，供您最终完善 JSON 配置。

配置适配器可以输出处理后的 JSON 结果、警告和错误。如果未发生错误，则输出 JSON 结果。当输入存在问题时（例如语法错误），会触发错误。当适配过程中出现问题但并非致命错误时（例如不支持某项功能），会发出警告。如果使用的是在适配过程中出现过警告的配置，请谨慎操作。
