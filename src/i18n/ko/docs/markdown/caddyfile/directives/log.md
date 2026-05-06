---
title: log (Caddyfile 지시어)
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.textContent.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# log

HTTP 요청 로깅(액세스 로그라고도 함)을 활성화하고 구성합니다.

<aside class="tip">

Caddy의 런타임 로그를 구성하려면 대신 [`log` 전역 옵션](/docs/caddyfile/options#log)을 참조하세요.

</aside>


`log` 지시어는 `hostnames` 하위 지시어로 재정의되지 않는 한, 해당 지시어가 나타나는 사이트 블록의 호스트 이름에 적용됩니다.

구성되면 기본적으로 사이트에 대한 모든 요청이 로깅됩니다. 일부 요청을 로깅에서 조건부로 제외하려면 [`log_skip` 지시어](log_skip)를 사용하세요.

로그 항목에 커스텀 필드를 추가하려면 [`log_append` 지시어](log_append)를 사용하세요.


- [구문](#syntax)
- [출력 모듈](#output-modules)
  - [stderr](#stderr)
  - [stdout](#stdout)
  - [discard](#discard)
  - [file](#file)
  - [net](#net)
- [형식 모듈](#format-modules)
  - [console](#console)
  - [json](#json)
  - [filter](#filter)
    - [delete](#delete)
	- [rename](#rename)
	- [replace](#replace)
	- [ip_mask](#ip-mask)
	- [query](#query)
	- [cookie](#cookie)
	- [regexp](#regexp)
	- [hash](#hash)
  - [append](#append)
- [예제](#examples)

기본적으로 민감한 정보가 포함될 수 있는 헤더(`Cookie`, `Set-Cookie`, `Authorization` 및 `Proxy-Authorization`)는 액세스 로그에 `REDACTED`로 로깅됩니다. 이 동작은 [`log_credentials`](/docs/caddyfile/options#log-credentials) 전역 서버 옵션으로 비활성화할 수 있습니다.


## 구문 <a id="syntax"></a>

```caddy-d
log [<logger_name>] {
	hostnames <hostnames...>
	no_hostname
	output <writer_module> ...
	format <encoder_module> ...
	level  <level>
	sampling {
		interval   <duration>
		first      <number>
		thereafter <number>
	}
}
```

- **logger_name** 는 이 사이트에 대한 로거 이름의 선택적 재정의입니다.

  기본적으로 로거 이름은 Caddyfile의 사이트 순서에 따라 `log0`, `log1` 등과 같이 자동으로 생성됩니다. 이는 전역 옵션에서 정의된 다른 로거로부터 이 로거의 출력을 안정적으로 참조하려는 경우에만 유용합니다. 아래 [예제](#multiple-outputs)를 참조하세요.

- **hostnames** 는 이 로거가 적용되는 호스트 이름의 선택적 재정의입니다.

  기본적으로 로거는 로거가 나타나는 사이트 블록의 호스트 이름(즉, 사이트 주소)에 적용됩니다. 이는 [와일드카드 사이트 블록](/docs/caddyfile/patterns#wildcard-certificates)에서 서브도메인별로 다른 로거를 정의하려는 경우에 유용합니다. 아래 [예제](#wildcard-logs)를 참조하세요.

- **no_hostname** 은 로거가 사이트 블록의 호스트 이름과 연결되지 않도록 합니다. 기본적으로 로거는 `log` 지시어가 나타나는 [사이트 주소](/docs/caddyfile/concepts#addresses)와 연결됩니다.

  이는 [`log_name` 지시어](/docs/caddyfile/directives/log_name)를 사용하여 요청 경로나 메서드와 같은 특정 조건에 따라 요청을 다른 파일로 로깅하려는 경우에 유용합니다.

- **output** 은 로그를 기록할 위치를 구성합니다. 아래 [`output` 모듈](#output-modules)을 참조하세요.

  기본값: `stderr`.

- **format** 은 로그를 인코딩하거나 형식을 지정하는 방법을 설명합니다. 아래 [`format` 모듈](#format-modules)을 참조하세요.

  기본값: `stderr`이 터미널로 감지되면 `console`, 그렇지 않으면 `json`.

- **level** 은 로깅할 최소 항목 수준입니다. 기본값: `INFO`.

  액세스 로그는 현재 `INFO` 및 `ERROR` 수준 로그만 내보냅니다.

- **sampling** 은 로그 볼륨을 줄이기 위해 로그 샘플링을 구성합니다. 샘플링이 지정되면 아래 기본값이 적용되어 활성화됩니다. 이를 생략하면 샘플링이 비활성화됩니다.

  - **interval** 은 샘플링을 수행할 [지속 시간 창(duration window)](/docs/conventions#durations)입니다. 기본값: `1s` (비활성화).

  - **first** 는 각 간격 동안 지정된 수준 및 메시지에 대해 유지할 로그 수입니다. 기본값: `100`.

  - **thereafter** 는 첫 번째 유지된 로그 이후 각 간격에서 건너뛸 로그 수입니다. 기본값: `100`.

  예를 들어, `interval 1s`, `first 5`, `thereafter 10`으로 설정하면, 각 10초 간격에서 처음 5개의 로그 항목이 유지되고, 그 후 해당 초 내에서 동일한 수준과 메시지를 가진 매 10번째 로그 항목만 허용됩니다.


### 출력 모듈 <a id="output-modules"></a>

**output** 하위 지시어를 사용하여 로그가 기록되는 위치를 커스터마이징할 수 있습니다.

#### stderr <a id="stderr"></a>

표준 오류 (콘솔, 기본값).

```caddy-d
output stderr
```

#### stdout <a id="stdout"></a>

표준 출력 (콘솔).

```caddy-d
output stdout
```

#### discard <a id="discard"></a>

출력 없음.

```caddy-d
output discard
```

#### file <a id="file"></a>

파일입니다. 기본적으로 로그 파일은 디스크 공간 소모를 방지하기 위해 크기에 따라 순환("롤링")됩니다.

로그 롤링은 [timberjack <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/DeRuina/timberjack)에 의해 제공됩니다.

<aside class="tip">

**로그 파일 옵션 다시 로드에 대한 참고 사항:** 지정된 출력 파일에 구성 변경 사항을 적용하려면 서버 재시작이 필요합니다.
새 로그 파일 이름을 추가하지 않는 한, 서버 다시 로드(reload) 시에는 변경 사항이 적용되지 않습니다.

</aside>

```caddy-d
output file <filename> {
	mode          <mode>
	roll_disabled
	roll_size     <size>
	roll_interval <duration>
	roll_minutes  <minutes...>
	roll_at	      <times...>
	roll_uncompressed
	roll_local_time
	roll_keep     <num>
	roll_keep_for <days>
	backup_time_format <format>
}
```

- **&lt;filename&gt;** 은 로그 파일의 경로입니다.

  롤링될 때, 파일은 `<name>-<timestamp>-<reason>.log` 템플릿을 사용하여 이름이 변경됩니다. 타임스탬프는 [`backup_time_format`](#backup_time_format) 옵션에 따라 형식이 지정됩니다. 이유는 회전을 트리거한 항목에 따라 `size` 또는 `time` 중 하나가 됩니다. 파일이 압축되면 파일 이름에 `.gz`가 추가됩니다.

   예를 들어, 파일 이름이 `access.log`인 경우, 크기로 인해 롤링되었다면 `access-2026-01-30T22-15-42.123-size.log`, 시간으로 인해 롤링되었다면 `access-2025-01-30T00-00-00.000-time.log`와 같이 이름이 지정될 수 있습니다.

- **mode** 는 로그 파일에 사용할 Unix 파일 모드/권한입니다. 모드는 1개에서 4개의 8진수 숫자로 구성됩니다(Unix [chmod <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Chmod) 명령에서 허용하는 숫자 형식과 동일하며, 단 0으로만 구성된 모드는 기본 모드인 `600`으로 해석됩니다).

  예를 들어: `0600`은 모드를 `rw-,---,---`로 설정합니다(로그 파일 소유자에게 읽기/쓰기 권한 부여, 다른 사람에게는 권한 없음). `0640`은 모드를 `rw-,r--,---`로 설정합니다(소유자에게 읽기/쓰기 권한, 그룹에게 읽기 권한만 부여). `644`는 모드를 `rw-,r--,r--`로 설정하여 소유자에게 읽기/쓰기 권한을 부여하고 그룹 소유자 및 다른 사용자에게는 읽기 권한만 부여합니다.

- **roll_disabled** 는 로그 롤링을 비활성화합니다. 이로 인해 디스크 공간이 고갈될 수 있으므로 로그 파일이 다른 방식으로 유지 관리되는 경우에만 사용하세요.

- **roll_size** 는 로그 파일을 롤링할 크기입니다. 현재 구현은 메가바이트 해상도를 지원하며, 소수점 값은 다음 전체 메가바이트로 올림됩니다. 예를 들어, `1.1MiB`는 `2MiB`로 올림됩니다.

  이 기능은 항상 활성화되어 있습니다. 로그 기록으로 인해 파일이 지정된 크기를 초과하면 로그가 즉시 회전됩니다. 백업 파일 이름에는 이유로 `size`가 포함됩니다.

  기본값: `100MiB`

- **roll_interval** 은 로그 회전 사이의 최대 기간입니다. 값은 로그 파일을 롤링할 [지속 시간 문자열](/docs/conventions#durations)입니다.

  활성화되면, 마지막 회전 이후 이 기간이 지난 후 로그에 다음 기록이 발생할 때 파일이 회전됩니다. 백업 파일 이름에는 이유로 `time`가 포함됩니다.

  `24h`로 설정하더라도 반드시 자정에 롤링되는 것은 아니며, 마지막 회전으로부터 24시간이 지난 시점에 롤링됩니다. 크기로 인해 롤링이 발생하는 경우 다음 회전 시간은 이전 회전과 비교하여 오프셋됩니다. 대신 특정 시간에 롤링하려면 `roll_at` 또는 `roll_minutes` 옵션을 사용할 수 있습니다.

  기본값: 비활성화

- **roll_minutes** 는 로그 파일을 롤링할 분 값 목록(0-59)입니다. 예를 들어, `10 40`은 매시간 `xx:10` 및 `xx:40`에 30분마다 로그 파일을 롤링합니다. 회전은 시계 분(0초)에 맞춰 정렬됩니다.

  이를 활성화하면 지정된 분 값에 로그 회전을 트리거하는 고루틴 타이머가 생성됩니다(즉, 약간의 백그라운드 처리가 도입됨). 이는 `roll_interval` 및 `roll_size` 외에도 작동합니다. 백업 파일 이름에는 이유로 `time`가 포함됩니다.

  기본값: 비활성화

- **roll_at** 은 로그 파일을 롤링할 시간 값 목록(24시간 형식)입니다. 예를 들어, `00:00 12:00`은 매일 자정과 정오에 두 번 로그 파일을 롤링합니다. 회전은 시계 분(0초)에 맞춰 정렬됩니다.

  이를 활성화하면 지정된 시간에 로그 회전을 트리거하는 고루틴 타이머가 생성됩니다(즉, 약간의 백그라운드 처리가 도입됨). 이는 `roll_interval` 및 `roll_size` 외에도 작동합니다. 백업 파일 이름에는 이유로 `time`가 포함됩니다.

  기본값: 비활성화

- **roll_uncompressed** 는 gzip 로그 압축을 끕니다.

  기본값: `gzip` 압축이 활성화됩니다.

- **roll_local_time** 은 롤링 시 파일 이름에 로컬 타임스탬프를 사용하도록 설정합니다.
  기본값: UTC 시간을 사용합니다.

- **roll_keep** 은 가장 오래된 파일을 삭제하기 전에 유지할 로그 파일 수입니다. 새 로그 파일이 생성될 때 트리거됩니다.

  기본값: `10`

- **roll_keep_for** 는 롤링된 파일을 유지할 기간을 [지속 시간 문자열](/docs/conventions#durations)로 나타냅니다. 새 로그 파일이 생성될 때 트리거됩니다.
  현재 구현은 일(day) 해상도를 지원하며, 소수점 값은 다음 전체 일로 올림됩니다. 예를 들어, `36h` (1.5일)는 `48h` (2일)로 올림됩니다.
  
  기본값: `2160h` (90일)

- **backup_time_format** 은 백업 파일 이름에 사용할 시간 형식입니다. 유효한 시간 레이아웃 문자열이어야 합니다. 자세한 내용은 [Go 문서](https://pkg.go.dev/time#pkg-constants)를 참조하세요.

  기본값: `2006-01-02T15-04-05`


#### net <a id="net"></a>

네트워크 소켓입니다. 소켓이 다운되면 다시 연결을 시도하는 동안 로그를 stderr에 덤프합니다.

```caddy-d
output net <address> {
	dial_timeout <duration>
	soft_start
}
```

- **&lt;address&gt;** 는 로그를 기록할 [주소](/docs/conventions#network-addresses)입니다.

- **dial_timeout** 은 로그 소켓에 성공적으로 연결될 때까지 대기하는 시간입니다. 소켓이 다운되면 로그 방출이 이 시간 동안 차단될 수 있습니다.

- **soft_start** 는 소켓 연결 시 오류를 무시하여 원격 로그 서비스가 다운된 경우에도 구성을 로드할 수 있도록 합니다. 대신 로그가 stderr로 방출됩니다.


### 형식 모듈 <a id="format-modules"></a>

**format** 하위 지시어를 사용하여 로그가 인코딩(형식화)되는 방식을 커스터마이징할 수 있습니다. `log` 블록 내에 나타납니다.

<aside class="tip">

**Common Log Format (CLF)에 대한 참고 사항:** CLF는 현대적인 구조화된 로그와 충돌합니다. 액세스 로그를 권장되지 않는 Common Log Format으로 변환하려면 [`transform-encoder` 플러그인 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder)을 사용하세요.

</aside>


각 개별 인코더에 대한 구문 외에도 대부분의 인코더에서 다음 공통 속성을 설정할 수 있습니다.

```caddy-d
format <encoder_module> {
	message_key     <key>
	level_key       <key>
	time_key        <key>
	name_key        <key>
	caller_key      <key>
	stacktrace_key  <key>
	line_ending     <char>
	time_format     <format>
	time_local
	duration_format <format>
	level_format    <format>
}
```

- **message_key** 로그 항목의 메시지 필드에 대한 키입니다. 기본값: `msg`

- **level_key** 로그 항목의 수준 필드에 대한 키입니다. 기본값: `level`

- **time_key** 로그 항목의 시간 필드에 대한 키입니다. 기본값: `ts`
- **name_key** 로그 항목의 이름 필드에 대한 키입니다. 기본값: `name`

- **caller_key** 로그 항목의 호출자 필드에 대한 키입니다.

- **stacktrace_key** 로그 항목의 스택 추적 필드에 대한 키입니다.

- **line_ending** 사용할 라인 엔딩입니다.

- **time_format** 타임스탬프 형식입니다.
  기본값: 형식이 기본적으로 `console`인 경우 `wall_milli`, 그렇지 않으면 `unix_seconds_float`.
  
  다음 중 하나일 수 있습니다:
  - `unix_seconds_float` Unix epoch 이후의 부동 소수점 초 수.
  - `unix_milli_float` Unix epoch 이후의 부동 소수점 밀리초 수.
  - `unix_nano` Unix epoch 이후의 정수 나노초 수.
  - `iso8601` 예: `2006-01-02T15:04:05.000Z0700`
  - `rfc3339` 예: `2006-01-02T15:04:05Z07:00`
  - `rfc3339_nano` 예: `2006-01-02T15:04:05.999999999Z07:00`
  - `wall` 예: `2006/01/02 15:04:05`
  - `wall_milli` 예: `2006/01/02 15:04:05.000`
  - `wall_nano` 예: `2006/01/02 15:04:05.000000000`
  - `common_log` 예: `02/Jan/2006:15:04:05 -0700`
  - 또는 모든 호환 가능한 시간 레이아웃 문자열. 자세한 내용은 [Go 문서](https://pkg.go.dev/time#pkg-constants)를 참조하세요.
  
  형식 문자열의 부분은 레이아웃에 대한 특수 상수입니다. 따라서 `2006`은 연도, `01`은 월, `Jan`은 문자열 형태의 월, `02`는 일입니다. 형식 문자열에 실제 현재 날짜 숫자를 사용하지 마세요.

- **time_local** 기본값인 UTC 시간 대신 로컬 시스템 시간으로 로깅합니다.

- **duration_format** 지속 시간의 형식입니다.

  기본값: `seconds`.
  
  다음 중 하나일 수 있습니다:
  - `s`, `second` 또는 `seconds` 경과된 부동 소수점 초 수.
  - `ms`, `milli` 또는 `millis` 경과된 부동 소수점 밀리초 수.
  - `ns`, `nano` 또는 `nanos` 경과된 정수 나노초 수.
  - `string` Go의 내장 문자열 형식을 사용합니다(예: `1m32.05s` 또는 `6.31ms`).

- **level_format** 수준의 형식입니다.

  기본값: 형식이 기본적으로 `console`인 경우 `color`, 그렇지 않으면 `lower`.
  
  다음 중 하나일 수 있습니다:
  - `lower` 소문자.
  - `upper` 대문자.
  - `color` ANSI 색상이 포함된 대문자.
  

#### console <a id="console"></a>

콘솔 인코더는 일부 구조를 유지하면서 사람이 읽기 쉬운 형식으로 로그 항목의 형식을 지정합니다.

```caddy-d
format console
```

#### json <a id="json"></a>

각 로그 항목을 JSON 객체로 형식화합니다.

```caddy-d
format json
```


#### filter <a id="filter"></a>

필드별 필터링을 허용합니다.

```caddy-d
format filter {
	fields {
		<field> <filter> ...
	}
	<field> <filter> ...
	wrap <encode_module> ...
}
```

중첩된 필드는 `>`를 사용하여 중첩 레이어를 나타냄으로써 참조할 수 있습니다. 즉, `{"a":{"b":0}}`과 같은 객체의 경우 내부 필드는 `a>b`로 참조할 수 있습니다.

다음 필드는 로그의 기본 필드이며 기본 로깅 라이브러리에 의해 특수 사례로 추가되기 때문에 필터링할 수 없습니다: `ts`, `level`, `logger` 및 `msg`.

`wrap` 지정은 선택 사항입니다. 생략하면 현재 출력 모듈이 [`stderr`](#stderr) 또는 [`stdout`](#stdout)인지, 그리고 인터랙티브 터미널인지에 따라 기본값이 선택됩니다. 이 경우 [`console`](#console)이 선택되고, 그렇지 않으면 [`json`](#json)이 선택됩니다.

단축형으로 `fields` 블록을 생략하고 `filter` 블록 내에 직접 필터를 지정할 수 있습니다.


사용 가능한 필터는 다음과 같습니다:

##### delete <a id="delete"></a>

필드가 인코딩에서 제외되도록 표시합니다.

```caddy-d
<field> delete
```


##### rename <a id="rename"></a>

로그 필드의 키 이름을 변경합니다.

```caddy-d
<field> rename <key>
```


##### replace <a id="replace"></a>

인코딩 시 필드를 제공된 문자열로 교체하도록 표시합니다.

```caddy-d
<field> replace <replacement>
```


##### ip_mask <a id="ip-mask"></a>

CIDR 마스크(즉, 왼쪽부터 유지할 IP 비트 수)를 사용하여 필드의 IP 주소를 마스킹합니다. 필드가 문자열 배열(예: HTTP 헤더)인 경우 배열의 각 값이 마스킹됩니다. 값은 쉼표로 구분된 IP 주소 문자열일 수 있습니다.

IPv4와 IPv6 주소는 총 비트 수가 다르기 때문에 별도의 구성이 있습니다.

가장 일반적으로 필터링할 필드는 다음과 같습니다:
- 직접 연결하는 클라이언트의 경우 `request>remote_ip`
- [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies)가 구성된 경우 파싱된 "실제 클라이언트"에 대한 `request>client_ip`
- 리버스 프록시 뒤에 있는 경우 `request>headers>X-Forwarded-For`

```caddy-d
<field> ip_mask [<ipv4> [<ipv6>]] {
	ipv4 <cidr>
	ipv6 <cidr>
}
```


##### query <a id="query"></a>

URL 필드의 쿼리 부분을 조작하기 위해 하나 이상의 작업을 수행하도록 필드를 표시합니다. 가장 일반적으로 필터링할 필드는 `request>uri`입니다.

```caddy-d
<field> query {
	delete  <key>
	replace <key> <replacement>
	hash    <key>
}
```

사용 가능한 작업은 다음과 같습니다:

- **delete** 쿼리에서 지정된 키를 제거합니다.

- **replace** 지정된 쿼리 키의 값을 **replacement**로 교체합니다. 편집 플레이스홀더를 삽입하는 데 유용합니다. URL에 쿼리 키는 있었지만 값은 숨겨졌음을 알 수 있습니다.

- **hash** 지정된 쿼리 키의 값을 값의 SHA-256 해시의 처음 4바이트(소문자 16진수)로 교체합니다. 민감한 경우 값을 가리면서 각 요청이 다른 값을 가졌는지 확인하는 데 유용합니다.


##### cookie <a id="cookie"></a>

`Cookie` HTTP 헤더 값을 조작하기 위해 하나 이상의 작업을 수행하도록 필드를 표시합니다. 가장 일반적으로 필터링할 필드는 `request>headers>Cookie`입니다.

```caddy-d
<field> cookie {
	delete  <name>
	replace <name> <replacement>
	hash    <name>
}
```

사용 가능한 작업은 다음과 같습니다:

- **delete** 헤더에서 이름으로 지정된 쿠키를 제거합니다.

- **replace** 지정된 쿠키의 값을 **replacement**로 교체합니다. 편집 플레이스홀더를 삽입하는 데 유용합니다. 헤더에 쿠키는 있었지만 값은 숨겨졌음을 알 수 있습니다.

- **hash** 지정된 쿠키의 값을 값의 SHA-256 해시의 처음 4바이트(소문자 16진수)로 교체합니다. 민감한 경우 값을 가리면서 각 요청이 다른 값을 가졌는지 확인하는 데 유용합니다.

동일한 쿠키 이름에 대해 여러 작업이 정의된 경우 첫 번째 작업만 적용됩니다.


##### regexp <a id="regexp"></a>

인코딩 시 정규 표현식 교체를 적용하도록 필드를 표시합니다. 필드가 문자열 배열(예: HTTP 헤더)인 경우 배열의 각 값에 교체가 적용됩니다.

```caddy-d
<field> regexp <pattern> <replacement>
```

사용되는 정규 표현식 언어는 Go에 포함된 RE2입니다. [RE2 구문 참조](https://github.com/google/re2/wiki/Syntax) 및 [Go 정규식 구문 개요](https://pkg.go.dev/regexp/syntax)를 확인하세요.

교체 문자열에서 캡처 그룹은 `${group}`으로 참조할 수 있습니다. 여기서 `group`은 표현식의 캡처 그룹 이름 또는 번호입니다. 캡처 그룹 `0`은 전체 정규식 매치, `1`은 첫 번째 캡처 그룹, `2`는 두 번째 캡처 그룹 등입니다.


##### hash <a id="hash"></a>

인코딩 시 필드를 값의 SHA-256 해시의 처음 4바이트(8개 16진수 문자)로 교체하도록 표시합니다. 필드가 문자열 배열(예: HTTP 헤더)인 경우 배열의 각 값이 해싱됩니다.

민감한 경우 값을 가리면서 각 요청이 다른 값을 가졌는지 확인하는 데 유용합니다.

```caddy-d
<field> hash
```

#### append <a id="append"></a>

모든 로그 항목에 필드를 추가합니다.

```caddy-d
format append {
	fields {
		<field> <value>
	}
	<field> <value>
	wrap <encode_module> ...
}
```

로그 항목을 생성하는 Caddy 인스턴스에 대한 정보(가능하면 환경 변수를 통해)를 추가하는 데 가장 유용합니다. 필드 값은 전역 플레이스홀더(예: `{env.*}`)일 수 있지만, 로그는 HTTP 요청 컨텍스트 외부에서 작성되므로 요청별 플레이스홀더는 사용할 수 *not* 않습니다.

`wrap` 지정은 선택 사항입니다. 생략하면 현재 출력 모듈이 [`stderr`](#stderr) 또는 [`stdout`](#stdout)인지, 그리고 인터랙티브 터미널인지에 따라 기본값이 선택됩니다. 이 경우 [`console`](#console)이 선택되고, 그렇지 않으면 [`json`](#json)이 선택됩니다.

`fields` 블록을 생략하고 `append` 블록 내에 직접 필드를 지정할 수 있습니다.



## 예제 <a id="examples"></a>

기본 로거에 대한 액세스 로깅을 활성화합니다.

즉, 기본적으로 `stderr`로 로깅되지만, [`log` 전역 옵션](/docs/caddyfile/options#log)으로 `default` 로거를 재구성하여 변경할 수 있습니다:

```caddy
example.com {
	log
}
```


로그를 파일에 기록합니다(기본적으로 활성화되는 로그 롤링 포함):

```caddy
example.com {
	log {
		output file /var/log/access.log
	}
}
```


매일 자정에 롤링하거나 로그 파일이 1GB에 도달할 때(둘 중 먼저 발생하는 시점) 롤링하고, 롤링된 파일 5개 또는 30일분의 로그를 유지하도록 로그 롤링을 커스터마이징합니다:

```caddy
example.com {
	log {
		output file /var/log/access.log {
			roll_at 00:00
			roll_size 1gb
			roll_keep 5
			roll_keep_for 720h
		}
	}
}
```


로그에서 `User-Agent` 요청 헤더를 삭제합니다:

```caddy
example.com {
	log {
		format filter {
			request>headers>User-Agent delete
		}
	}
}
```


여러 민감한 쿠키를 편집합니다. (일부 민감한 헤더는 기본적으로 빈 값으로 로깅됩니다. `Cookie` 헤더 값 로깅을 활성화하려면 [`log_credentials` 전역 옵션](/docs/caddyfile/options#log-credentials)을 참조하세요):

```caddy
example.com {
	log {
		format filter {
			request>headers>Cookie cookie {
				replace session REDACTED
				delete secret
			}
		}
	}
}
```


요청의 원격 주소를 마스킹합니다. IPv4 주소의 경우 처음 16비트(예: 255.255.0.0)를 유지하고, IPv6 주소의 경우 처음 32비트를 유지합니다.

Caddy v2.7부터 `remote_ip`와 `client_ip`가 모두 로깅됩니다. 여기서 `client_ip`는 [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies)가 구성된 경우의 "실제 IP"입니다:

```caddy
example.com {
	log {
		format filter {
			request>remote_ip ip_mask 16 32
			request>client_ip ip_mask 16 32
		}
	}
}
```


환경 변수의 서버 ID를 모든 로그 항목에 추가하고, 헤더를 삭제하기 위해 `filter`와 연결합니다:

```caddy
example.com {
	log {
		format append {
			server_id {env.SERVER_ID}
			wrap filter {
				request>headers>Cookie delete
			}
		}
	}
}
```


<span id="wildcard-logs" /> 각 로거에 대해 `hostnames`를 재정의하여 [와일드카드 사이트 블록](/docs/caddyfile/patterns#wildcard-certificates)에서 각 서브도메인에 대해 별도의 로그 파일을 작성합니다. 반복을 피하기 위해 [스니펫(snippet)](/docs/caddyfile/concepts#snippets)을 사용합니다:

```caddy
(subdomain-log) {
	log {
		hostnames {args[0]}
		output file /var/log/{args[0]}.log
	}
}

*.example.com {
	import subdomain-log foo.example.com
	@foo host foo.example.com
	handle @foo {
		respond "foo"
	}

	import subdomain-log bar.example.com
	@bar host bar.example.com
	handle @bar {
		respond "bar"
	}
}
```

<span id="multiple-outputs" /> 특정 서브도메인에 대한 액세스 로그를 서로 다른 형식([`transform-encoder` 플러그인 <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder) 하나와 [`json`](#json) 하나)으로 두 개의 다른 파일에 기록합니다.

사이트 블록에서 로거 이름을 `foo`로 재정의한 다음, 전역 옵션의 두 로거에서 `include http.log.access.foo`를 사용하여 해당 로거에서 생성된 액세스 로그를 포함함으로써 작동합니다:

```caddy
{
	log access-formatted {
		include http.log.access.foo
		output file /var/log/access-foo.log
		format transform "{common_log}"
	}

	log access-json {
		include http.log.access.foo
		output file /var/log/access-foo.json
		format json
	}
}

foo.example.com {
	log foo
}
```

<span id="sampling-example" /> 샘플링을 통해 로그 볼륨을 줄입니다. 예를 들어 초당 처음 5개의 요청을 유지한 다음, 그 이후에는 요청 10개당 1개만 유지합니다:

```caddy
example.com {
	log {
		sampling {
			interval   1s
			first      5
			thereafter 10
		}
	}
}
```
