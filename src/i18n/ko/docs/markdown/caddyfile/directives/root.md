---
title: root (Caddyfile 지시어)
---

# root

사이트의 루트 경로를 설정합니다. 파일 시스템에 액세스하는 다양한 매처와 지시어에서 사용됩니다. 설정하지 않으면 기본 사이트 루트는 현재 작업 디렉토리입니다.

구체적으로, 이 지시어는 `{http.vars.root}` 플레이스홀더를 설정합니다. 동일한 블록 내의 다른 `root` 지시어와 상호 배타적이므로, 일치하는 부분이 있는 여러 개의 루트를 정의해도 안전합니다. 서로 중첩되어 덮어쓰지 않습니다.

이 지시어는 정적 파일 서비스를 자동으로 활성화하지 않으므로, 흔히 [`file_server` 지시어](file_server) 또는 [`php_fastcgi` 지시어](php_fastcgi)와 함께 사용됩니다.


## 구문 <a id="syntax"></a>

```caddy-d
root [<matcher>] <path>
```

- **&lt;path&gt;** 는 사이트 루트로 사용할 경로입니다.

v2.8.0 이전에는 `<path>` 인자가 `/`로 시작하는 경우 파서가 [매처 토큰](/docs/caddyfile/matchers#syntax)으로 혼동할 수 있었기 때문에, 와일드카드 매처 토큰(`*`)을 지정해야 했습니다.


## 예시 <a id="examples"></a>

사이트 루트를 `/home/bob/public_html`로 설정합니다(Caddy가 `bob` 사용자로 실행 중이라고 가정):

<aside class="tip">

Caddy를 systemd 서비스로 실행하는 경우, `caddy` 사용자가 `/home` 디렉토리에 대해 "실행(executable)" 권한(디렉토리 이동에 필요함)을 가지고 있지 않기 때문에 `/home`에서 파일을 읽는 것이 작동하지 않습니다. 대신 파일을 `/srv` 또는 `/var/www/html`에 두는 것이 좋습니다.

</aside>


```caddy-d
root /home/bob/public_html
```


<aside class="tip">

v2.8.0 이전에는 첫 번째 인자가 [경로 매처](/docs/caddyfile/matchers#path-matchers)와 모호했기 때문에(예: `root * /srv`) [와일드카드 매처](/docs/caddyfile/matchers#wildcard-matchers)가 필요했지만, 이제는 `root /srv`로 단순화할 수 있습니다.

</aside>


모든 요청에 대해 사이트 루트를 `public_html`(현재 작업 디렉토리에 대한 상대 경로)로 설정합니다:

```caddy-d
root public_html
```

`/foo/*` 요청에 대해서만 사이트 루트를 변경합니다:

```caddy-d
root /foo/* /home/user/public_html/foo
```

`root` 지시어는 정적 파일을 서비스하기 위해 [`file_server`](file_server)와 함께 사용되거나, PHP 사이트를 서비스하기 위해 [`php_fastcgi`](php_fastcgi)와 함께 사용되는 경우가 많습니다:

```caddy
example.com {
	root /srv
	file_server
}
```
