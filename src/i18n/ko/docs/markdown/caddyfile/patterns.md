---
title: 일반적인 Caddyfile 패턴
---

# 일반적인 Caddyfile 패턴 <a id="common-caddyfile-patterns"></a>

이 페이지는 일반적인 사용 사례에 대한 몇 가지 완전하고 최소한의 Caddyfile 구성을 보여줍니다. 이는 여러분의 Caddyfile 문서를 작성하기 위한 유용한 시작점이 될 수 있습니다.

이들은 바로 가져다 쓸 수 있는 솔루션이 아니며, 도메인 이름, 포트/소켓, 디렉토리 경로 등을 직접 커스텀해야 합니다. 가장 일반적인 구성 패턴 중 일부를 설명하기 위한 목적으로 작성되었습니다.

- [정적 파일 서버](#static-file-server)
- [리버스 프록시](#reverse-proxy)
- [PHP](#php)
- [`www.` 서브도메인 리다이렉트](#redirect-www-subdomain)
- [트레일링 슬래시](#trailing-slashes)
- [와일드카드 인증서](#wildcard-certificates)
- [싱글 페이지 애플리케이션 (SPA)](#single-page-apps-spas)
- [Caddy에서 다른 Caddy로 프록시하기](#caddy-proxying-to-another-caddy)


## 정적 파일 서버 <a id="static-file-server"></a>

```caddy
example.com {
	root /var/www
	file_server
}
```

평소와 같이 첫 번째 줄은 사이트 주소입니다. [`root` 지시어](/docs/caddyfile/directives/root)는 사이트 루트의 경로를 지정합니다 (`*`은 [경로 매처](/docs/caddyfile/matchers#path-matchers)와 구별하기 위해 모든 요청을 매칭한다는 의미입니다). 현재 작업 디렉토리가 아니라면 경로를 사이트에 맞게 변경하세요. 마지막으로 [정적 파일 서버](/docs/caddyfile/directives/file_server)를 활성화합니다.



## 리버스 프록시 <a id="reverse-proxy"></a>

모든 요청 프록시:

```caddy
example.com {
	reverse_proxy localhost:5000
}
```

경로가 `/api/`로 시작하는 요청만 프록시하고 나머지는 정적 파일을 제공:

```caddy
example.com {
	root /var/www
	reverse_proxy /api/* localhost:5000
	file_server
}
```

이는 [요청 매처](/docs/caddyfile/matchers#syntax)를 사용하여 `/api/`로 시작하는 요청만 일치시키고 백엔드로 프록시합니다. 다른 모든 요청은 사이트 [`root`](/docs/caddyfile/directives/root)에서 [정적 파일 서버](/docs/caddyfile/directives/file_server)를 통해 제공됩니다. 이는 `reverse_proxy`가 `file_server`보다 [지시어 순서](/docs/caddyfile/directives#directive-order)에서 더 높다는 점을 이용한 것입니다.

여기에 더 많은 [`reverse_proxy` 예시](/docs/caddyfile/directives/reverse_proxy#examples)가 있습니다.



## PHP <a id="php"></a>

### PHP-FPM

PHP FastCGI 서비스가 실행 중인 경우, 대부분의 현대적인 PHP 앱에서 다음과 같이 작동합니다:

```caddy
example.com {
	root /srv/public
	encode
	php_fastcgi localhost:9000
	file_server
}
```

사이트 루트를 상황에 맞게 커스텀하세요. 이 예시는 PHP 앱의 웹 루트가 `public` 디렉토리 내에 있다고 가정합니다. 디스크에 존재하는 파일에 대한 요청은 [`file_server`](/docs/caddyfile/directives/file_server)를 통해 제공되고, 그 외의 모든 요청은 PHP 앱이 처리하도록 `index.php`로 라우팅됩니다.

때로는 유닉스 소켓을 사용하여 PHP-FPM에 연결할 수도 있습니다:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[`php_fastcgi` 지시어](/docs/caddyfile/directives/php_fastcgi)는 실제로 [여러 구성 조각](/docs/caddyfile/directives/php_fastcgi#expanded-form)에 대한 지름길입니다.


### FrankenPHP

또는 CGO(Go에서 C 바인딩)를 사용하여 PHP를 직접 호출하는 Caddy 배포판인 [FrankenPHP](https://frankenphp.dev/)를 사용할 수 있습니다. 이는 PHP-FPM을 사용하는 것보다 최대 4배 더 빠를 수 있으며, 워커 모드를 사용할 수 있다면 더욱 좋습니다.

```caddy
{
    frankenphp
    order php_server before file_server
}

example.com {
	root /srv/public
    encode zstd br gzip
    php_server
}
```


## `www.` 서브도메인 리다이렉트 <a id="redirect-www-subdomain"></a>

HTTP 리다이렉트를 통해 `www.` 서브도메인을 **추가**하려면:

```caddy
example.com {
	redir https://www.{host}{uri}
}

www.example.com {
}
```


이를 **제거**하려면:

```caddy
www.example.com {
	redir https://example.com{uri}
}

example.com {
}
```


**여러 도메인**을 동시에 제거하려면 오른쪽에서부터 `0`부터 인덱싱된 호스트명의 일부인 `{labels.*}` 플레이스홀더를 사용합니다 (예: `0`=`com`, `1`=`example-one`, `2`=`www`):

```caddy
www.example-one.com, www.example-two.com {
	redir https://{labels.1}.{labels.0}{uri}
}

example-one.com, example-two.com {
}
```



## 트레일링 슬래시 <a id="trailing-slashes"></a>

보통은 이를 직접 구성할 필요가 없습니다. [`file_server` 지시어](/docs/caddyfile/directives/file_server)는 요청된 리소스가 디렉토리인지 파일인지에 따라 HTTP 리다이렉트를 통해 요청에서 트레일링 슬래시를 자동으로 추가하거나 제거합니다.

하지만 필요한 경우 설정에서 트레일링 슬래시를 강제할 수 있습니다. 내부적으로 또는 외부적으로 처리하는 두 가지 방법이 있습니다.

### 내부 강제 (Internal enforcement)

이는 [`rewrite`](/docs/caddyfile/directives/rewrite) 지시어를 사용합니다. Caddy는 내부적으로 URI를 다시 작성하여 트레일링 슬래시를 추가하거나 제거합니다:

```caddy
example.com {
	rewrite /add     /add/
	rewrite /remove/ /remove
}
```

다시 쓰기를 사용하면 트레일링 슬래시가 있는 요청과 없는 요청이 동일하게 처리됩니다.


### 외부 강제 (External enforcement)

이는 [`redir`](/docs/caddyfile/directives/redir) 지시어를 사용합니다. Caddy는 브라우저에 URI를 변경하여 트레일링 슬래시를 추가하거나 제거하도록 요청합니다:

```caddy
example.com {
	redir /add     /add/
	redir /remove/ /remove
}
```

리다이렉트를 사용하면 클라이언트가 요청을 다시 보내야 하므로 리소스에 대해 허용 가능한 단일 URI를 강제할 수 있습니다.



## 와일드카드 인증서 <a id="wildcard-certificates"></a>

Let's Encrypt를 포함한 대부분의 발급자의 경우, Caddy가 와일드카드 인증서를 자동화하도록 하려면 [ACME DNS 챌린지](/docs/automatic-https#dns-challenge)를 활성화해야 합니다.

Caddy 2.10부터 DNS 챌린지가 활성화되면, Caddy는 서브도메인에 대해 별도의 인증서를 관리하기 전에 이미 구성되었거나 관리 중인 적용 가능한 와일드카드 인증서를 선언적으로 선호합니다.



동일한 와일드카드 인증서로 여러 서브도메인을 서비스해야 하는 경우, [`handle` 지시어](/docs/caddyfile/directives/handle)와 [`host` 매처](/docs/caddyfile/matchers#host)를 활용하여 다음과 같은 Caddyfile로 처리하는 것이 가장 좋습니다:

```caddy
*.example.com {
	tls {
		dns <provider_name> [<params...>]
	}

	@foo host foo.example.com
	handle @foo {
		respond "Foo!"
	}

	@bar host bar.example.com
	handle @bar {
		respond "Bar!"
	}

	# 그 외 처리되지 않은 도메인에 대한 폴백
	handle {
		abort
	}
}
```

Caddy가 와일드카드 인증서를 자동으로 관리하게 하려면 [ACME DNS 챌린지](/docs/automatic-https#dns-challenge)를 활성화해야 합니다.



## 싱글 페이지 애플리케이션 (SPA) <a id="single-page-apps-spas"></a>

웹 페이지가 자체적으로 라우팅을 수행할 때, 서버는 서버 측에 존재하지 않지만 단일 인덱스 파일이 제공되는 한 클라이언트 측에서 렌더링 가능한 페이지에 대한 요청을 많이 받을 수 있습니다. 이렇게 설계된 웹 애플리케이션을 SPA 또는 싱글 페이지 애플리케이션이라고 합니다.

핵심 아이디어는 서버가 요청된 파일이 서버 측에 존재하는지 확인하기 위해 "파일을 시도(try files)"하게 하고, 존재하지 않으면 클라이언트가 라우팅을 수행하는 인덱스 파일(보통 클라이언트 측 JavaScript 사용)로 폴백하는 것입니다.

일반적인 SPA 구성은 다음과 같습니다:

```caddy
example.com {
	root /srv
	encode
	try_files {path} /index.html
	file_server
}
```

SPA가 API 또는 다른 서버 측 전용 엔드포인트와 결합된 경우, `handle` 블록을 사용하여 독점적으로 처리하는 것이 좋습니다:

```caddy
example.com {
	encode

	handle /api/* {
		reverse_proxy backend:8000
	}

	handle {
		root /srv
		try_files {path} /index.html
		file_server
	}
}
```

`index.html`에 해시된 파일명을 가진 JS/CSS 자산에 대한 참조가 포함되어 있는 경우, 클라이언트에게 이를 캐시하지 않도록 지시하는 `Cache-Control` 헤더를 추가하는 것을 고려할 수 있습니다 (자산이 변경되면 브라우저가 새 자산을 가져오도록 하기 위해). `try_files` 다시 쓰기는 디스크의 다른 파일과 일치하지 않는 모든 경로에서 `index.html`을 제공하는 데 사용되므로, `try_files`를 `route`로 감싸서 `header` 핸들러가 다시 쓰기 *후에* 실행되도록 할 수 있습니다 (보통 [지시어 순서](/docs/caddyfile/directives#directive-order) 때문에 이전에 실행됩니다):

```caddy-d
route {
	try_files {path} /index.html
	header /index.html Cache-Control "public, max-age=0, must-revalidate"
}
```


## Caddy에서 다른 Caddy로 프록시하기 <a id="caddy-proxying-to-another-caddy"></a>

공개적으로 액세스 가능한 Caddy 인스턴스("front"라고 부름)가 있고, 실제 앱을 제공하는 프라이빗 네트워크에 다른 Caddy 인스턴스("back"이라고 부름)가 있는 경우, [`reverse_proxy` 지시어](/docs/caddyfile/directives/reverse_proxy)를 사용하여 요청을 전달할 수 있습니다.

Front 인스턴스:

```caddy
foo.example.com, bar.example.com {
	reverse_proxy 10.0.0.1:80
}
```

Back 인스턴스:

```caddy
{
	servers {
		trusted_proxies static private_ranges
	}
}

http://foo.example.com {
	reverse_proxy foo-app:8080
}

http://bar.example.com {
	reverse_proxy bar-app:9000
}
```

- 이 예시는 두 개의 서로 다른 도메인을 서비스하며, 두 도메인을 모두 `80` 포트의 동일한 back Caddy 인스턴스로 프록시합니다. back 인스턴스는 두 도메인을 서로 다른 방식으로 서비스하므로 두 개의 별도 사이트 블록으로 구성됩니다.

- back에서는 `80` 포트에서 HTTP를 수락하기 위해 [`http://`](/docs/caddyfile/concepts#addresses)가 사용됩니다. front 인스턴스가 TLS를 종료하고 front와 back 사이의 트래픽은 프라이빗 네트워크에 있으므로 다시 암호화할 필요가 없습니다.

- 필요한 경우 back 인스턴스에서 `8080`과 같은 다른 포트를 사용할 수 있습니다. back 구성의 각 사이트 주소 뒤에 `:8080`을 붙이거나 [`http_port` 전역 옵션](/docs/caddyfile/options#http_port)을 `8080`으로 설정하면 됩니다.

- back에서는 [`trusted_proxies` 전역 옵션](/docs/caddyfile/options#trusted_proxies)을 사용하여 front 인스턴스를 프록시로 신뢰하도록 Caddy에 지시합니다. 이를 통해 실제 클라이언트 IP가 유지됩니다.

- 더 나아가, [부하 분산(load balance)](/docs/caddyfile/directives/reverse_proxy#load-balancing)을 수행하는 두 개 이상의 back 인스턴스를 둘 수 있습니다. front 인스턴스에서 [`acme_server`](/docs/caddyfile/directives/acme_server)를 사용하여 mTLS(상호 TLS)를 설정하여 back 인스턴스의 CA 역할을 하도록 할 수 있습니다 (front와 back 사이의 트래픽이 신뢰할 수 없는 네트워크를 통과하는 경우 유용함).
