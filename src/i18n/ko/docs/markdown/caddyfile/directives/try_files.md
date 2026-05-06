---
title: try_files (Caddyfile 지시어)
---

# try_files

요청 URI 경로를 사이트 루트에 존재하는 나열된 파일 중 첫 번째 파일로 재작성합니다. 일치하는 파일이 없으면 재작성이 수행되지 않습니다.

## 구문 <a id="syntax"></a>

```caddy-d
try_files <files...> {
	policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
}
```

- **&lt;files...&gt;** 는 시도할 파일 목록입니다. URI 경로는 존재하는 첫 번째 파일로 재작성됩니다.

  디렉토리를 일치시키려면 경로 끝에 슬래시 `/` 를 추가하십시오. 모든 파일 경로는 사이트 [루트(root)](root)에 대한 상대 경로이며, [글로브 패턴(glob patterns)](https://pkg.go.dev/path/filepath#Match)이 확장됩니다.

  각 인자에는 쿼리 문자열이 포함될 수 있으며, 이 경우 해당 특정 파일과 일치하면 쿼리 문자열도 변경됩니다.

  `try_policy` 가 `first_exist` (기본값)인 경우, 목록의 마지막 항목은 `=` 로 시작하는 숫자(예: `=404`)일 수 있으며, 이는 폴백으로서 해당 코드로 오류를 발생시킵니다. 이 오류는 [`handle_errors`](handle_errors) 로 포착하여 처리할 수 있습니다.

- **policy** 는 파일 목록 중에서 파일을 선택하는 정책입니다.

  기본값: `first_exist`

## 확장된 형태 <a id="expanded-form"></a>

`try_files` 지시어는 기본적으로 다음의 축약형입니다:

```caddy-d
@try_files file <files...>
rewrite @try_files {file_match.relative}
```

이 지시어는 매처 토큰을 허용하지 않습니다. 더 복잡한 매칭 로직이 필요한 경우 위의 확장된 형태를 기초로 사용하십시오.

자세한 내용은 [`file` 매처](/docs/caddyfile/matchers#file) 를 참조하십시오.

## 예제 <a id="examples"></a>

요청이 정적 파일과 일치하지 않는 경우, PHP 인덱스/라우터 엔트리포인트로 재작성합니다:

```caddy-d
try_files {path} /index.php
```

동일하지만 쿼리 문자열에 원래 경로를 추가합니다 (일부 레거시 PHP 앱에서 필요함):

```caddy-d
try_files {path} /index.php?{query}&p={path}
```

동일하지만 디렉토리도 일치시킵니다:

```caddy-d
try_files {path} {path}/ /index.php?{query}&p={path}
```

파일이나 디렉토리가 존재하면 재작성을 시도하고, 그렇지 않으면 404 오류를 발생시킵니다 (이는 [`handle_errors`](handle_errors) 로 포착하여 처리할 수 있음):

```caddy-d
try_files {path} {path}/ =404
```

정적 파일의 가장 최근에 배포된 버전을 선택합니다 (예: `index.html` 이 요청될 때 `index.be331df.html` 을 서비스함):

```caddy-d
try_files {file.base}.*.{file.ext} {
	policy most_recently_modified
}
```
