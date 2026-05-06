---
title: php_fastcgi (Caddyfile 지시어)
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# php_fastcgi

php-fpm과 같은 PHP FastCGI 서버에 요청을 프록시하는 독창적인(opinionated) 지시어입니다.

- [구문](#syntax)
- [확장된 형태](#expanded-form)
  - [설명](#explanation)
- [예제](#examples)

Caddy의 [`reverse_proxy`](reverse_proxy)는 모든 FastCGI 애플리케이션을 제공할 수 있지만, 이 지시어는 PHP 앱에 특별히 맞춰져 있습니다. 이 지시어는 [더 긴 구성](#expanded-form)을 대체하는 편리한 단축키입니다.

사이트 루트에 있는 모든 `index.php`가 라우터 역할을 할 것으로 예상합니다. 그것이 바람직하지 않은 경우, [`try_files` 하위 지시어](#try_files)를 재구성하여 기본 리라이트(rewrite) 동작을 수정하거나, [확장된 형태](#expanded-form)를 기반으로 필요에 맞게 커스텀하십시오.

아래 나열된 하위 지시어 외에도 이 지시어는 [`reverse_proxy`](reverse_proxy#syntax)의 모든 하위 지시어를 지원합니다. 예를 들어, 부하 분산(load balancing) 및 헬스 체크(health checks)를 활성화할 수 있습니다.

**대부분의 현대적인 PHP 앱은 추가적인 하위 지시어나 커스텀 없이도 잘 작동합니다.** 하위 지시어는 보통 특정 엣지 케이스나 레거시 PHP 앱에서만 사용됩니다.

## 구문 <a id="syntax"></a>

```caddy-d
php_fastcgi [<matcher>] <php-fpm_gateways...> {
	root <path>
	split <substrings...>
	index <filename>|off
	try_files <files...>
	env [<key> <value>]
	resolve_root_symlink
	capture_stderr
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>

	<any other reverse_proxy subdirectives...>
}
```

- **<php-fpm_gateways...>** 는 FastCGI 서버의 [주소](/docs/conventions#network-addresses)입니다. 일반적으로 TCP 소켓 또는 unix 소켓 파일입니다.

- **root** <span id="root"/>는 사이트의 루트 폴더를 설정합니다. 항상 `php_fastcgi`와 함께 [`root` 지시어](root)를 사용하는 것이 좋지만, PHP-FPM 업스트림이 Caddy와 다른 루트를 사용하는 경우 이를 덮어쓰는 것이 유용할 수 있습니다([예제](#docker) 참조). 사용된 경우 [`root` 지시어](root)의 값으로 기본 설정되며, 그렇지 않으면 Caddy의 현재 작업 디렉토리로 기본 설정됩니다.

- **split** <span id="split"/>는 URI를 두 부분으로 나누기 위한 하위 문자열을 설정합니다. 첫 번째로 일치하는 하위 문자열은 경로에서 "경로 정보(path info)"를 분할하는 데 사용됩니다. 첫 번째 조각은 일치하는 하위 문자열이 접미사로 붙고 실제 리소스(CGI 스크립트) 이름으로 간주됩니다. 두 번째 조각은 CGI 스크립트가 사용할 PATH_INFO로 설정됩니다. 기본값: `.php`

- **index** <span id="index"/>는 디렉토리 인덱스 파일로 취급할 파일 이름을 지정합니다. 이는 [확장된 형태](#expanded-form)의 파일 매처에 영향을 미칩니다. 기본값: `index.php`. 일치하는 파일을 찾지 못했을 때 `index.php`로의 리라이트 폴백을 비활성화하려면 `off`로 설정할 수 있습니다.

- **try_files** <span id="try_files"/>는 기본 try-files 리라이트에 대한 오버라이드를 지정합니다. 자세한 내용은 [`try_files` 지시어](try_files)를 참조하십시오. 기본값: `{path} {path}/index.php index.php`.

- **env** <span id="env"/>는 지정된 값으로 추가 환경 변수를 설정합니다. 여러 환경 변수에 대해 두 번 이상 지정할 수 있습니다. 기본적으로 모든 관련 FastCGI 환경 변수는 이미 설정되어 있지만(HTTP 헤더 포함), 필요한 경우 변수를 추가하거나 덮어쓸 수 있습니다.

- **resolve_root_symlink** <span id="resolve_root_symlink"/> [`root`](#root) 디렉토리가 심볼릭 링크(symlink)인 경우, 이를 실제 값으로 확인(resolve)하도록 합니다. 이는 단순히 심볼릭 링크를 다른 디렉토리의 새 버전을 가리키도록 교체함으로써 배포 전략으로 사용되기도 합니다. 반복적인 시스템 호출을 피하기 위해 기본적으로 비활성화되어 있습니다.

- **capture_stderr** <span id="capture_stderr"/>는 업스트림 fastcgi 서버가 `stderr`로 보낸 모든 메시지를 캡처하고 로깅하도록 합니다. 로깅은 기본적으로 `WARN` 레벨에서 수행됩니다. 응답에 `4xx` 또는 `5xx` 상태가 있는 경우 대신 `ERROR` 레벨이 사용됩니다. 기본적으로 `stderr`은 무시됩니다.

- **dial_timeout** <span id="dial_timeout"/>은 업스트림 소켓에 연결할 때 대기할 시간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 기본값: `3s`.

- **read_timeout** <span id="read_timeout"/>은 FastCGI 업스트림에서 읽을 때 대기할 시간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 기본값: 타임아웃 없음.

- **write_timeout** <span id="write_timeout"/>은 FastCGI 업스트림으로 보낼 때 대기할 시간을 설정하는 [기간 값](/docs/conventions#durations)입니다. 기본값: 타임아웃 없음.


이 지시어는 리버스 프록시를 둘러싼 독창적인 래퍼이므로, [`reverse_proxy`](reverse_proxy#syntax)의 모든 하위 지시어를 사용하여 커스텀할 수 있습니다.


## 확장된 형태 <a id="expanded-form"></a>

`php_fastcgi` 지시어(하위 지시어 없음)는 다음과 같은 구성과 동일합니다. 대부분의 현대적인 PHP 앱은 이 프리셋으로 잘 작동합니다. 그렇지 않은 경우, `php_fastcgi` 단축키를 사용하는 대신 이를 빌려와 필요에 따라 커스텀하여 사용하십시오.

```caddy-d
route {
	# 디렉토리 요청에 대해 트레일링 슬래시 추가
	# 이 리다이렉션은 "{http.request.uri.path}/index.php"가
	# try_files 목록에 나타나지 않으면 자동으로 비활성화됩니다.
	@canonicalPath {
		file {path}/index.php
		not path */
	}
	redir @canonicalPath {http.request.orig_uri.path}/ 308

	# 요청된 파일이 존재하지 않으면 인덱스 파일을 시도하고 index.php가 항상 존재한다고 가정합니다.
	@indexFiles file {
		try_files {path} {path}/index.php index.php
		try_policy first_exist_fallback
		split_path .php
	}
	rewrite @indexFiles {file_match.relative}

	# PHP 파일을 FastCGI 응답기로 프록시
	@phpFiles path *.php
	reverse_proxy @phpFiles <php-fpm_gateway> {
		transport fastcgi {
			split .php
		}
	}
}
```

### 설명 <a id="explanation"></a>

- 첫 번째 섹션은 요청 경로를 정규화(canonicalizing)하는 것과 관련이 있습니다. 목표는 디스크의 디렉토리를 대상으로 하는 요청에 실제로 트레일링 슬래시 `/`가 추가되도록 하여, 해당 디렉토리에 대한 요청에 대해 하나의 URL만 유효하도록 보장하는 것입니다.

  이 정규화는 `try_files` 하위 지시어에 `{path}/index.php`가 포함된 경우에만 발생합니다(기본값).

  이것은 슬래시로 끝나지 *않고*, `index.php` 파일을 포함하는 디스크의 디렉토리와 매핑되는 요청만 일치시키는 요청 매처를 사용하고, 일치하는 경우 트레일링 슬래시가 추가된 HTTP 308 리다이렉트를 수행함으로써 이루어집니다. 예를 들어, 디스크에 `/foo/index.php`가 존재하는 경우 경로가 `/foo`인 요청을 `/foo/`로 리다이렉트합니다(디렉토리에 대한 경로를 정규화하기 위해 `/`를 추가함).

- 다음 섹션은 일치하는 파일이 디스크에 존재하는지 여부에 따라 경로 리라이트를 수행하는 것과 관련이 있습니다. 이것은 또한 `.php` 뒤의 경로 부분(요청 경로에 `.php`가 포함된 경우)을 기억하는 부수 효과가 있습니다. 이는 Caddy가 FastCGI 환경 변수를 올바르게 설정하는 데 중요합니다.

  - 먼저, `{path}`가 디스크에 존재하는 파일인지 확인합니다. 그렇다면 해당 경로로 리라이트합니다. 이것은 기본적으로 나머지를 단락(short-circuits)시키고, 디스크에 *실제로 존재하는* 파일에 대한 요청이 다른 방식으로 리라이트되지 않도록 보장합니다(아래의 다음 단계 참조). 따라서 예를 들어 디스크에 `/js/app.js` 파일이 있는 경우 해당 경로에 대한 요청은 그대로 유지됩니다.

  - 둘째, `{path}/index.php`가 디스크에 존재하는 파일인지 확인합니다. 그렇다면 해당 경로로 리라이트합니다. `/foo/`와 같은 디렉토리에 대한 요청의 경우 `/foo//index.php`(이는 `/foo/index.php`로 정규화됨)를 찾고, 존재하는 경우 해당 경로로 요청을 리라이트합니다. 이 동작은 웹 루트의 하위 디렉토리에서 다른 PHP 앱을 실행하는 경우에 가끔 유용합니다.

  - 마지막으로, 항상 `index.php`로 리라이트합니다(현대적인 PHP 앱에서는 거의 항상 존재합니다). 이를 통해 PHP 앱은 `index.php` 스크립트를 진입점으로 사용하여 디스크의 파일로 매핑되지 *않는* 경로에 대한 모든 요청을 처리할 수 있습니다.

- 마지막 섹션은 실제로 PHP 코드를 실행하기 위해 요청을 PHP FastCGI(또는 PHP-FPM) 서비스로 프록시하는 부분입니다. 요청 매처는 `.php`로 끝나는 요청만 일치시키므로, PHP 스크립트가 *아니고* 디스크에 *존재하는* 모든 파일은 이 지시어에 의해 처리되지 않고 통과됩니다.

`php_fastcgi` 지시어만으로는 보통 충분하지 않습니다. 디스크에 있는 파일의 위치를 설정하기 위해 [`root` 지시어](root)와 거의 항상 함께 사용해야 하며(현대적인 PHP 앱의 경우 `index.php`가 포함된 `public` 디렉토리인 `/var/www/html/public`일 수 있음), 이 지시어에 의해 처리되지 않고 통과된 정적 파일(JS, CSS, 이미지 등)을 제공하기 위해 [`file_server` 지시어](file_server)와 함께 사용해야 합니다.



## 예제 <a id="examples"></a>

`127.0.0.1:9000`에서 수신 대기 중인 FastCGI 응답기로 모든 PHP 요청을 프록시합니다:

```caddy-d
php_fastcgi 127.0.0.1:9000
```

동일하지만 `/blog/` 아래의 요청에 대해서만 해당됩니다:

```caddy-d
php_fastcgi /blog/* localhost:9000
```

unix 소켓을 통해 수신 대기 중인 PHP-FPM을 사용하는 경우:

```caddy-d
php_fastcgi unix//run/php/php8.2-fpm.sock
```

[`root` 지시어](root)는 거의 항상 PHP 스크립트가 포함된 디렉토리를 지정하는 데 사용되며, 정적 파일을 제공하기 위해 [`file_server` 지시어](file_server)가 사용됩니다:

```caddy
example.com {
	root /var/www/html/public
	php_fastcgi 127.0.0.1:9000
	file_server
}
```

<span id="docker"/> Caddy로 여러 PHP 앱을 제공할 때, Caddy가 정적 파일을 별도로 읽고 제공하며 PHP 파일이 존재하는지 감지할 수 있도록 각 앱의 웹 루트가 달라야 합니다.

Docker를 사용하는 경우, 종종 PHP-FPM 컨테이너가 동일한 루트에 파일이 마운트되어 있습니다. 이 경우 해결책은 Caddy 컨테이너의 다른 디렉토리에 파일을 마운트한 다음, [`root` 하위 지시어](#root)를 사용하여 각 컨테이너의 루트를 설정하는 것입니다:

```caddy
app1.example.com {
	root /srv/app1/public
	php_fastcgi app1:9000 {
		root /var/www/html/public
	}
	file_server
}

app2.example.com {
	root /srv/app2/public
	php_fastcgi app2:9000 {
		root /var/www/html/public
	}
	file_server
}
```

`index.php`를 진입점으로 사용하지 않는 PHP 사이트의 경우, 대신 `404` 오류를 발생시키도록 폴백할 수 있습니다. 오류는 [`handle_errors` 지시어](handle_errors)를 사용하여 포착하고 처리할 수 있습니다:

```caddy
example.com {
	php_fastcgi localhost:9000 {
		try_files {path} {path}/index.php =404
	}

	handle_errors {
		respond "{err.status_code} {err.status_text}"
	}
}
```
