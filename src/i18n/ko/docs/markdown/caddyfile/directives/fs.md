---
title: fs (Caddyfile 지시어)
---

# fs <a id="fs"></a>

파일 I/O를 수행하는 데 사용될 파일 시스템을 설정합니다.

이를 통해 클라우드에서 실행 중인 원격 파일 시스템, 파일과 같은 인터페이스를 가진 데이터베이스 또는 Caddy 바이너리 내에 포함된 파일에서 읽을 수 있도록 연결할 수 있습니다.

먼저 [`filesystem` 전역 옵션](/docs/caddyfile/options#filesystem)을 사용하여 파일 시스템 이름을 선언해야 하며, 그런 다음 이 지시어를 사용하여 사용할 파일 시스템을 지정할 수 있습니다.

이 지시어는 종종 정적 파일을 제공하기 위한 [`file_server` 지시어](file_server) 또는 파일 존재 여부에 따라 다시 쓰기를 수행하기 위한 [`try_files` 지시어](try_files)와 함께 사용됩니다. 일반적으로 파일 시스템 내의 루트 경로를 설정하기 위해 [`root` 지시어](root)와도 함께 사용됩니다.


## 구문 <a id="syntax"></a>

```caddy-d
fs [<matcher>] <filesystem>
```

## 예시 <a id="examples"></a>

인증이 필요할 수 있는 가상의 `custom` 모듈을 사용하는 `foo`라는 이름의 파일 시스템 사용 예시:

```caddy
{
	filesystem foo custom {
		api_key abc123
	}
}

example.com {
	fs foo
	root /srv
	file_server
}
```

`/images*` 경로에 대해서만 `foo` 파일 시스템에서 이미지를 제공하고, 나머지는 기본 파일 시스템에서 제공하는 예시:

```caddy
example.com {
	fs /images* foo
	root /srv
	file_server
}
```
