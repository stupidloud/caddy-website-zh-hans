---
title: log_skip (Caddyfile 지시어)
---

# log_skip

매칭된 요청에 대한 액세스 로깅을 건너뜁니다.

필요하지 않은 요청에 대한 로깅을 건너뛰려면 [`log` 지시어](log)와 함께 이 지시어를 사용해야 합니다.

v2.8.0 이전에는 이 지시어의 이름이 `skip_log`였으나, 다른 지시어들과의 일관성을 위해 이름이 변경되었습니다.


## 구문

```caddy-d
log_skip [<matcher>]
```


## 예시

하위 경로에 저장된 정적 파일에 대한 액세스 로깅 건너뛰기:

```caddy
example.com {
	root /srv

	log
	log_skip /static*

	file_server
}
```


패턴과 일치하는 요청에 대한 액세스 로깅 건너뛰기. 이 예시에서는 특정 확장자를 가진 파일에 대해 적용됩니다:

```caddy-d
@skip path_regexp \.(js|css|png|jpe?g|gif|ico|woff|otf|ttf|eot|svg|txt|pdf|docx?|xlsx?)$
log_skip @skip
```


이미 매처 내에 있는 경로 내에서 사용되는 경우 매처가 필요하지 않습니다. 예를 들어, 특정 하위 경로에 대한 파일 서버 핸들이 있는 경우:

```caddy-d
handle_path /static* {
	root /srv/static
	log_skip
	file_server
}
```
