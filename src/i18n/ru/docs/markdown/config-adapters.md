---
title: Config Adapters
---

<a id="config-adapters"></a>
# Config Adapters

Нативный язык config в Caddy — [JSON](https://www.json.org/json-en.html), но писать JSON вручную может быть утомительно и чревато ошибками. Поэтому Caddy поддерживает конфигурацию на других языках через **config adapters**. Это Caddy plugins, которые позволяют использовать config в предпочитаемом формате, выводя для вас [Caddy JSON](/docs/json/).

Например, config adapter может [преобразовать вашу NGINX config в Caddy JSON](https://github.com/caddyserver/nginx-adapter).

<a id="known-config-adapters"></a>
## Известные config adapters

Сейчас доступны следующие config adapters (некоторые являются third-party projects):

- [**caddyfile**](/docs/caddyfile) (standard)
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
## Использование config adapters

Можно использовать config adapter, указав его в command line через flag `--adapter` в большинстве subcommands, принимающих config:

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

Или через API на endpoint [`/load`](/docs/api#post-load):

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

Если нужно только получить output JSON без запуска, можно использовать команду [`caddy adapt`](/docs/command-line#caddy-adapt):

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

<a id="caveats"></a>
## Предостережения

Не все config languages на 100% совместимы с Caddy; некоторые features или behaviors просто плохо переводятся или еще не реализованы в adapter или самом Caddy.

Некоторые adapters выполняют 1-1 translation, например YAML->JSON или TOML->JSON. Другие специально разработаны для Caddy, например Caddyfile. В целом такие adapters будут работать всегда.

Однако не все adapters работают во всех случаях. Config adapters делают все возможное, чтобы преобразовать ваш input в Caddy JSON с максимальной fidelity и correctness. Поскольку этот conversion process не гарантированно всегда полный и корректный, мы не называем их "converters" или "translators". Это "adapters", потому что они как минимум дают хорошую отправную точку для завершения вашей итоговой JSON config.

Config adapters могут выводить итоговый JSON, warnings и errors. JSON получается, если errors не возникли. Errors возникают, когда с input что-то не так (например, syntax errors). Warnings выдаются, когда с adaptation что-то не так, но это не обязательно fatal (например, feature not supported). Рекомендуется осторожность при использовании configs, которые были adapted с warnings.
