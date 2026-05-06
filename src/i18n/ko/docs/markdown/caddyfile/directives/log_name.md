---
title: log_name (Caddyfile 지시어)
---

# log_name

[`log` 지시어](log)를 사용하여 액세스 로그를 작성할 때 요청에 사용할 로거 이름을 재정의합니다.

이 지시어는 요청 경로 또는 메서드와 같은 특정 조건에 따라 서로 다른 파일에 요청을 로깅하고 싶을 때 유용합니다.

둘 이상의 로거 이름을 지정할 수 있으며, 이 경우 요청의 로그가 일치하는 여러 로거로 전달됩니다.

이는 종종 `log` 지시어의 [`no_hostname`](log#no_hostname) 옵션과 함께 사용됩니다. 이 옵션은 로거가 사이트 블록의 호스트 이름과 연결되는 것을 방지하여, `log_name`이 설정된 요청만 해당 로거로 로그를 전달하도록 합니다.


## 구문

```caddy-d
log_name [<matcher>] <names...>
```


## 예시

요청을 서로 다른 파일에 로깅하고 싶을 수 있습니다. 예를 들어, 메인 액세스 로그와 별도의 파일에 헬스 체크(health check)를 로깅하고 싶을 수 있습니다.

`log`에서 `no_hostname`을 사용하면 로거가 사이트 블록의 호스트 이름(여기서는 `localhost`)과 연결되는 것을 방지하므로, `log_name`이 해당 로거의 이름으로 설정된 요청만 로그를 받게 됩니다.

```caddy
localhost {
	log {
		output file ./caddy.access.log
	}

	log health_check_log {
		output file ./caddy.access.health.log
		no_hostname
	}

	handle /healthz* {
		log_name health_check_log
		respond "Healthy"
	}

	handle {
		respond "Hello World"
	}
}
```
