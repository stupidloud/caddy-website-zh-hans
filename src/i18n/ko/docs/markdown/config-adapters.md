---
title: 구성 어댑터
---

# 구성 어댑터

Caddy의 네이티브 구성 언어는 [JSON](https://www.json.org/json-en.html)이지만, JSON을 직접 작성하는 것은 번거롭고 실수가 발생하기 쉽습니다. 그래서 Caddy는 **구성 어댑터(config adapters)** 를 통해 다른 언어로 구성하는 것을 지원합니다. 구성 어댑터는 사용자가 선호하는 형식의 구성을 [Caddy JSON](/docs/json/)으로 출력하여 사용할 수 있게 해주는 Caddy 플러그인입니다.

예를 들어, 구성 어댑터를 사용하여 [NGINX 구성을 Caddy JSON으로 변환](https://github.com/caddyserver/nginx-adapter)할 수 있습니다.

## 알려진 구성 어댑터 {#known-config-adapters}

현재 다음과 같은 구성 어댑터를 사용할 수 있습니다 (일부는 제3자 프로젝트입니다):

- [**caddyfile**](/docs/caddyfile) (표준)
- [**nginx**](https://github.com/caddyserver/nginx-adapter)
- [**jsonc**](https://github.com/caddyserver/jsonc-adapter)
- [**json5**](https://github.com/caddyserver/json5-adapter)
- [**yaml**](https://github.com/abiosoft/caddy-yaml)
- [**cue**](https://github.com/caddyserver/cue-adapter)
- [**toml**](https://github.com/awoodbeck/caddy-toml-adapter)
- [**hcl**](https://github.com/francislavoie/caddy-hcl)
- [**dhall**](https://github.com/mholt/dhall-adapter)
- [**mysql**](https://github.com/zhangjiayin/caddy-mysql-adapter)

## 구성 어댑터 사용하기 {#using-config-adapters}

구성을 사용하는 대부분의 서브커맨드에서 `--adapter` 플래그를 사용하여 명령줄에서 구성 어댑터를 지정할 수 있습니다:

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

또는 [`/load` 엔드포인트](/docs/api#post-load)의 API를 통해서도 가능합니다:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

실행하지 않고 출력 JSON만 얻으려면 [`caddy adapt`](/docs/command-line#caddy-adapt) 명령을 사용할 수 있습니다:

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

## 주의 사항 {#caveats}

모든 구성 언어가 Caddy와 100% 호환되는 것은 아닙니다. 일부 기능이나 동작은 변환이 잘 되지 않거나, 아직 어댑터나 Caddy 자체에 프로그래밍되지 않았을 수 있습니다.

YAML->JSON이나 TOML->JSON처럼 1대1 변환을 수행하는 어댑터도 있습니다. Caddyfile처럼 Caddy를 위해 특별히 설계된 어댑터도 있습니다. 일반적으로 이러한 어댑터는 항상 잘 작동합니다.

그러나 모든 어댑터가 항상 완벽하게 작동하는 것은 아닙니다. 구성 어댑터는 사용자의 입력을 최대한 정확하고 올바르게 Caddy JSON으로 변환하려고 최선을 다합니다. 이 변환 프로세스가 항상 완벽하거나 정확하다고 보장할 수 없기 때문에, 우리는 이를 "변환기(converters)"나 "번역기(translators)"라고 부르지 않습니다. 대신 최소한 최종 JSON 구성을 완성하기 위한 좋은 시작점을 제공한다는 의미에서 "어댑터(adapters)"라고 부릅니다.

구성 어댑터는 결과 JSON, 경고 및 오류를 출력할 수 있습니다. 오류가 발생하지 않으면 JSON 결과가 나옵니다. 입력에 문제가 있는 경우(예: 구문 오류) 오류가 발생합니다. 변환에 문제가 있지만 반드시 치명적이지는 않은 경우(예: 지원되지 않는 기능) 경고가 발생합니다. 경고와 함께 변환된 구성을 사용할 때는 주의가 필요합니다.
