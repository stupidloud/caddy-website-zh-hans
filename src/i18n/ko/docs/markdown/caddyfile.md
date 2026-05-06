---
title: Caddyfile
---

# Caddyfile

**Caddyfile**은 사람을 위한 편리한 Caddy 구성 형식입니다. 쓰기 쉽고, 이해하기 쉬우며, 대부분의 사용 사례에 대해 충분히 표현력이 뛰어나기 때문에 대부분의 사람들이 Caddy를 사용할 때 가장 선호하는 방법입니다.

다음과 같이 생겼습니다:

```caddy
example.com {
	root /var/www/wordpress
	encode
	php_fastcgi unix//run/php/php-version-fpm.sock
	file_server
}
```

(이것은 완전히 관리되는 HTTPS로 WordPress를 서비스하는 실제 프로덕션 준비가 완료된 Caddyfile입니다.)

기본적인 아이디어는 먼저 사이트의 주소를 입력한 다음, 사이트에 필요한 기능이나 특징을 입력하는 것입니다. [더 일반적인 패턴을 확인하세요.](/docs/caddyfile/patterns)

## <a id="menu"></a>메뉴

- #### [빠른 시작 가이드](/docs/quick-starts/caddyfile)
  Caddyfile에 익숙해지기 시작하기 좋은 곳입니다.
- #### [전체 Caddyfile 튜토리얼](/docs/caddyfile-tutorial)
  Caddyfile로 다양하고 일반적인 작업을 수행하는 방법을 배웁니다.
- #### [Caddyfile 개념](/docs/caddyfile/concepts)
  필독! 구조, 사이트 주소, 매처(matchers), 자리 표시자(placeholders) 등.
- #### [지시문](/docs/caddyfile/directives)
  사이트의 기능을 활성화하는 줄의 시작 부분에 있는 키워드.
- #### [요청 매처](/docs/caddyfile/matchers)
  지시문과 함께 매처를 사용하여 요청을 필터링합니다.
- #### [전역 옵션](/docs/caddyfile/options)
  개별 사이트가 아닌 전체 서버에 적용되는 설정.
- #### [일반적인 패턴](/docs/caddyfile/patterns)
  일반적인 작업을 수행하는 간단한 방법.
<!-- - #### [Caddyfile specification](/docs/caddyfile/spec) TODO: Finish this -->


## <a id="note"></a>참고

Caddyfile은 단지 Caddy를 위한 [구성 어댑터(config adapter)](/docs/config-adapters)일 뿐입니다. 일반적으로 손으로 직접 구성을 작성할 때 선호되지만, Caddy의 [기본 JSON 구조](/docs/json/)만큼 표현력이 뛰어나거나 유연하거나 프로그래밍하기 쉽지는 않습니다. Caddy 구성/배포를 자동화하는 경우 [Caddy의 API](/docs/api)와 함께 JSON을 사용하는 것이 좋습니다. (제한적이지만 API와 함께 Caddyfile을 사용할 수도 있습니다.)