---
title: "명령줄"
---

# 명령줄

Caddy에는 표준 유닉스 계열 명령줄 인터페이스가 있습니다. 기본 사용법은 다음과 같습니다:

```
caddy <명령> [<인수...>]
```

`<캐럿>`은 여러분의 입력으로 교체되는 매개변수를 나타냅니다.

`[대괄호]`는 선택적 매개변수를 나타냅니다. `(괄호)`는 필수 매개변수를 나타냅니다.

줄임표 `...`는 연속(즉, 하나 이상의 매개변수)을 나타냅니다.

`--플래그`에는 `-f`와 같은 단일 문자 단축키가 있을 수 있습니다.

**빠른 시작: `caddy`, `caddy help` 또는 `man caddy`(설치된 경우)**

---

- **[caddy adapt](#caddy-adapt)**
  구성 문서를 기본 JSON으로 조정(adapt)합니다.

- **[caddy build-info](#caddy-build-info)**
  빌드 정보를 출력합니다.

- **[caddy completion](#caddy-completion)**
  셸 자동 완성 스크립트를 생성합니다.

- **[caddy environ](#caddy-environ)**
  환경 변수를 출력합니다.

- **[caddy file-server](#caddy-file-server)**
  간단하지만 프로덕션 준비가 완료된 파일 서버입니다.

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  기본 파일 브라우저 템플릿을 내보내기 위한 파일 서버용 보조 명령입니다.

- **[caddy fmt](#caddy-fmt)**
  Caddyfile의 형식을 지정(format)합니다.

- **[caddy hash-password](#caddy-hash-password)**
  암호를 해시하고 base64로 출력합니다.

- **[caddy help](#caddy-help)**
  caddy 명령에 대한 도움말을 봅니다.

- **[caddy list-modules](#caddy-list-modules)**
  설치된 Caddy 모듈을 나열합니다.

- **[caddy manpage](#caddy-manpage)**
  매뉴얼 페이지(manpages)를 생성합니다.

- **[caddy reload](#caddy-reload)**
  실행 중인 Caddy 프로세스의 구성을 변경합니다.

- **[caddy respond](#caddy-respond)**
  개발 및 테스트를 위한 빠르고 깔끔한 하드 코딩된 HTTP 서버입니다.

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  간단하지만 프로덕션 준비가 완료된 HTTP(S) 역방향 프록시입니다.

- **[caddy run](#caddy-run)**
  포그라운드에서 Caddy 프로세스를 시작합니다.

- **[caddy start](#caddy-start)**
  백그라운드에서 Caddy 프로세스를 시작합니다.

- **[caddy stop](#caddy-stop)**
  실행 중인 Caddy 프로세스를 중지합니다.

- **[caddy storage export](#caddy-storage)**
  구성된 저장소의 내용을 타볼(tarball)로 내보냅니다.

- **[caddy storage import](#caddy-storage)**
  이전에 내보낸 타볼을 구성된 저장소로 가져옵니다.

- **[caddy trust](#caddy-trust)**
  로컬 트러스트 스토어(들)에 인증서를 설치합니다.

- **[caddy untrust](#caddy-untrust)**
  로컬 트러스트 스토어(들)에서 인증서 신뢰를 해제합니다.

- **[caddy upgrade](#caddy-upgrade)**
  Caddy를 최신 릴리스로 업그레이드합니다.

- **[caddy add-package](#caddy-add-package)**
  추가 플러그인이 추가된 상태로 Caddy를 최신 릴리스로 업그레이드합니다.

- **[caddy remove-package](#caddy-remove-package)**
  일부 플러그인이 제거된 상태로 Caddy를 최신 릴리스로 업그레이드합니다.

- **[caddy validate](#caddy-validate)**
  구성 파일이 유효한지 테스트합니다.

- **[caddy version](#caddy-version)**
  버전을 출력합니다.

- **[신호](#signals)**
  Caddy가 신호(signals)를 처리하는 방법입니다.

- **[종료 코드](#exit-codes)**
  Caddy 프로세스가 종료될 때 발생합니다.

## <a id="subcommands"></a>하위 명령


### <a id="caddy-adapt"></a>`caddy adapt`

<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

구성을 Caddy의 기본 JSON 구성 구조로 조정하고 출력을 표준 출력(stdout)에 쓰는 동시에, 경고는 표준 에러(stderr)에 쓴 다음 종료합니다.

`--config`는 구성 파일의 경로입니다. 생략하면 현재 디렉터리에 있는 경우 `Caddyfile`을 가정합니다. 그렇지 않으면 이 플래그가 필수입니다. 일반 파일 대신 표준 입력(stdin)을 사용하려면 경로로 `-`를 사용하세요.

`--adapter`는 사용할 구성 어댑터를 지정합니다. 기본값은 `caddyfile`입니다.

`--pretty`는 사람이 읽을 수 있도록 들여쓰기와 함께 출력 형식을 지정합니다.

`--validate`는 유효성을 검사하기 위해 조정된 구성을 로드하고 프로비저닝합니다(하지만 실제로 구성을 실행하기 시작하지는 않습니다).

성공적으로 조정된 구성도 여전히 유효성 검사에 실패할 수 있다는 점에 유의하세요. 이에 대한 예제로 다음 Caddyfile을 사용합니다:

```caddy
localhost

tls cert_notexist.pem key_notexist.pem
```

조정해 보세요:

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

오류 없이 성공합니다. 그런 다음 시도해 보세요:

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_notexist.pem: no such file or directory
</code></pre>

비록 해당 Caddyfile을 오류 없이 JSON으로 조정할 수 있더라도 실제 인증서 및/또는 키 파일이 존재하지 않으므로, 프로비저닝 단계 중에 오류가 발생하여 유효성 검사에 실패합니다. 따라서 유효성 검사는 조정(adaptation)보다 더 강력한 오류 검사입니다.

#### <a id="example"></a>예제

Caddyfile을 수동으로 쉽게 읽고 수정할 수 있는 JSON으로 조정하려면:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile --pretty</code></pre>



### <a id="caddy-build-info"></a>`caddy build-info`

<pre><code class="cmd bash">caddy build-info</code></pre>

Go에서 제공하는 빌드에 대한 정보(주 모듈 경로, 패키지 버전, 모듈 교체)를 출력합니다.




### <a id="caddy-completion"></a>`caddy completion`

<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

셸 자동 완성 스크립트를 생성합니다. 이를 통해 `caddy` 명령을 입력할 때 탭 완성 또는 자동 완성(또는 셸에 따라 이와 유사한 기능)을 얻을 수 있습니다.

특정 셸에 이 스크립트를 설치하기 위한 지침을 얻으려면 `caddy help completion` 또는 `caddy completion -h`를 실행하세요.



### <a id="caddy-environ"></a>`caddy environ`

<pre><code class="cmd bash">caddy environ</code></pre>

Caddy가 보는 환경 변수를 출력한 다음 종료합니다. systemd와 같은 init 시스템이나 프로세스 관리자 단위를 디버깅할 때 유용할 수 있습니다.




### <a id="caddy-file-server"></a>`caddy file-server`

<pre><code class="cmd bash">caddy file-server
	[-r, --root &lt;path&gt;]
	[--listen &lt;addr&gt;]
	[-d, --domain &lt;example.com&gt;]
	[-b, --browse]
	[--reveal-symlinks]
	[-t, --templates]
	[--access-log]
	[-v, --debug]
	[-f, --file-limit &lt;number&gt;]
	[--no-compress]
	[-p, --precompressed]</code></pre>

간단하지만 프로덕션 준비가 완료된 정적 파일 서버를 가동합니다.

`--root`는 루트 파일 경로를 지정합니다. 기본값은 현재 작업 디렉터리입니다.

`--listen`은 수신 대기 주소를 허용합니다. `--domain`을 사용하지 않는 한 기본값은 `:80`이며, 사용하는 경우 `:443`이 기본값이 됩니다.

`--domain`은 해당 호스트 이름을 통해서만 파일을 제공하며, Caddy는 HTTPS를 통해 제공하려고 시도하므로, 공용 도메인 이름인 경우 공용 DNS가 올바르게 구성되었는지 먼저 확인해야 합니다. 기본 포트는 443으로 변경됩니다.

`--browse`는 인덱스 파일이 없는 디렉터리가 요청될 경우 디렉터리 목록을 활성화합니다.

`--reveal-symlinks`는 `--browse`가 활성화된 경우 디렉터리 목록에 심볼릭 링크의 대상을 표시합니다.

`--templates`는 템플릿 렌더링을 활성화합니다.

`--access-log`는 요청/액세스 로그를 활성화합니다.

`--debug`는 상세 로깅(verbose logging)을 활성화합니다.

`--file-limit`는 디렉터리 목록에 표시할 최대 파일 수를 설정합니다. 기본값: `10000`. 파일 수가 이 제한을 초과하면 처음 N개의 파일만 표시되며, 여기서 N은 지정된 제한입니다.

`--no-compress`는 압축을 비활성화합니다. 기본적으로 Zstandard 및 Gzip 압축이 활성화됩니다.

`--precompressed`는 사전 압축된 사이드카(sidecar) 파일을 검색하기 위한 인코딩 형식을 지정합니다. 여러 형식을 지정하기 위해 반복할 수 있습니다. 자세한 내용은 [file_server 지시문](/docs/caddyfile/directives/file_server#precompressed)을 참조하세요.

이 명령은 관리자 API를 비활성화하므로 로컬 개발 컴퓨터에서 여러 인스턴스를 더 쉽게 실행할 수 있습니다.


#### <a id="caddy-file-server-export-template"></a>`caddy file-server export-template`

<pre><code class="cmd bash">caddy file-server export-template</code></pre>

기본 파일 검색 템플릿을 표준 출력(stdout)으로 내보냅니다.

### <a id="caddy-fmt"></a>`caddy fmt`

<pre><code class="cmd bash">caddy fmt [&lt;path&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

Caddyfile의 형식을 지정하거나 예쁘게 만든 다음 종료합니다. `--overwrite`가 사용되지 않는 한 결과가 표준 출력에 출력되며, 차이가 있는 경우 코드 `1`과 함께 종료됩니다.

`<path>`는 Caddyfile의 경로를 지정합니다. `-`인 경우 입력을 표준 입력(stdin)에서 읽습니다. 생략하면 현재 디렉터리에 `Caddyfile`이라는 이름의 파일이 있다고 가정합니다.

`--overwrite`는 터미널에 출력되는 대신 결과가 입력 파일에 덮어쓰여지게 합니다. 입력이 일반 파일이 아니면 이 플래그는 아무런 영향을 미치지 않습니다.

`--diff`는 출력을 입력과 비교하여 차이가 있는 줄 앞에 `-`와 `+` 접두사를 붙이게 합니다. 변경되지 않은 줄은 정렬을 위해 공백 2개로 접두사가 붙으며, 이것은 유효한 패치(patch) 형식이 아니라 시각적 도구로만 사용된다는 점에 유의하세요.


### <a id="caddy-hash-password"></a>`caddy hash-password`

<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;password&gt;]
	[-a, --algorithm &lt;name&gt;]</code></pre>
	[--bcrypt-cost &lt;cost&gt;]</code></pre>

평문 암호를 해시하는 편리한 방법입니다. 결과 해시는 Caddy 구성에서 직접 사용할 수 있는 형식으로 표준 출력에 기록됩니다.

`--plaintext`
    해시할 암호입니다. 생략하면 표준 입력에서 읽어옵니다.
    Caddy가 제어 TTY에 연결되어 있으면 입력이 에코되지 않습니다.

`--algorithm`
    해시 알고리즘을 선택합니다. 유효한 옵션은 다음과 같습니다:
      * `argon2id` (최신 보안에 권장됨)
      * `bcrypt`  (레거시, 더 느림, 비용 구성 가능, 기본 비용은 `14`)

bcrypt 전용 매개변수:

`--bcrypt-cost`
    bcrypt 해싱 난이도를 설정합니다. 값이 높을수록 해시 계산이 더 느려지고 CPU 집약적이 되어 보안이 강화됩니다.
    유효한 범위 [bcrypt.MinCost, bcrypt.MaxCost] 내에 있어야 합니다.
    생략하거나 유효하지 않은 경우 기본 비용이 사용됩니다.

Argon2id 전용 매개변수:

`--argon2id-time`
    수행할 반복 횟수입니다. 이를 높이면 해싱이 느려지고 무차별 대입 공격(brute-force attacks)에 대한 저항력이 커집니다.

`--argon2id-memory`
    해싱 중 사용할 메모리 양입니다.
    값이 클수록 GPU/ASIC 공격에 대한 저항력이 커집니다.

`--argon2id-threads`
    사용할 CPU 스레드 수입니다. 멀티 코어 시스템에서 더 빠른 해싱을 위해 높입니다.

`--argon2id-keylen`
    바이트 단위의 결과 해시 길이입니다. 키가 길어지면 보안이 강화되지만 스토리지 크기가 약간 커집니다.


### <a id="caddy-help"></a>`caddy help`

<pre><code class="cmd bash">caddy help [&lt;command&gt;]</code></pre>

CLI 도움말 텍스트를 출력합니다. 선택적으로 특정 하위 명령에 대한 도움말을 출력한 다음 종료합니다.



### <a id="caddy-list-modules"></a>`caddy list-modules`

<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

설치된 Caddy 모듈을 출력한 후 종료합니다. 선택적으로 연결된 Go 모듈의 패키지 및/또는 버전 정보를 포함할 수 있습니다.

일부 스크립트 작성 상황에서는 모든 표준 모듈도 함께 출력하는 것이 불필요할 수 있으므로, `--skip-standard`를 사용하여 출력에서 생략할 수 있습니다.

`--json`은 프로그래밍 방식의 처리에 유용할 수 있는 JSON 형식으로 모듈 정보를 출력합니다.

참고: [Go의 버그](https://github.com/golang/go/issues/29228)로 인해 버전 정보는 Caddy가 주 모듈이 아닌 종속성으로 빌드된 경우에만 사용할 수 있습니다. 이를 더 쉽게 하려면 [xcaddy](/docs/build#xcaddy)를 사용하세요.



### <a id="caddy-manpage"></a>`caddy manpage`

<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;path&gt;)</code></pre>

Caddy 명령에 대한 매뉴얼/문서 페이지를 생성하고 지정된 경로의 디렉터리에 씁니다. 이 명령의 출력은 `man` 명령으로 읽을 수 있습니다.

`--directory` (필수)는 매뉴얼 페이지를 쓸 디렉터리 경로입니다. 존재하지 않는 경우 생성됩니다.

생성된 후에는 일반적으로 매뉴얼 페이지를 설치해야 합니다. 이 절차는 플랫폼에 따라 다르지만 일반적인 Linux 시스템에서는 다음과 비슷합니다:

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

그런 다음 터미널에서 `man caddy`(또는 하위 명령의 경우 `man caddy-*`)를 실행하여 문서를 읽을 수 있습니다.

매뉴얼 페이지는 웹사이트에 있는 문서와는 별개의 문서입니다. 저희 웹사이트에는 자주 업데이트되는 보다 포괄적인 문서가 있습니다.




### <a id="caddy-reload"></a>`caddy reload`

<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

실행 중인 Caddy 인스턴스에 새 구성을 제공합니다. 이는 [/load 엔드포인트](/docs/api#post-load)에 문서를 POST하는 것과 동일한 효과를 가지지만, 이 명령은 구성 파일을 중심으로 하는 간단한 워크플로에 편리합니다. `stop`, `start`, `run` 명령과 비교할 때 이 단일 명령은 실행 중인 구성을 변경/새로 고치는 의미적으로 올바른 방법입니다.

이 명령은 API를 사용하기 때문에 관리자 엔드포인트가 비활성화되어서는 안 됩니다.

`--config`는 적용할 구성 파일입니다. `-`인 경우 표준 입력에서 구성을 읽습니다. 지정되지 않으면 현재 작업 디렉터리에서 `Caddyfile`이라는 파일을 찾고, 존재하는 경우 `caddyfile` 구성 어댑터를 사용하여 조정합니다. 그렇지 않고 로드할 구성 파일이 없으면 오류가 발생합니다.

`--adapter`는 사용할 구성 어댑터를 지정합니다. `--config` 파일 이름이 `Caddyfile`로 시작하거나 `.caddyfile`로 끝나는 경우 `caddyfile` 어댑터를 가정하므로 이 플래그가 필요하지 않습니다. 그렇지 않고 제공된 구성 파일이 Caddy의 기본 JSON 형식이 아닌 경우 이 플래그가 필수입니다.

`--address`는 관리자 엔드포인트가 기본 주소에서 수신 대기하지 않고 제공된 구성 파일의 주소와 다른 경우에 사용해야 합니다.

`--force`는 지정된 구성이 Caddy가 이미 실행 중인 것과 같더라도 강제로 다시 로드(reload)가 발생하도록 합니다. 예를 들어 수동으로 로드된 TLS 인증서를 다시 로드하는 것과 같이 부작용(side-effects)이 발생할 수 있는 모듈을 Caddy가 강제로 다시 프로비저닝하도록 하는 데 유용할 수 있습니다.




### <a id="caddy-respond"></a>`caddy respond`

<pre><code class="cmd bash">caddy respond
	[-s, --status &lt;code&gt;]
	[-H, --header "&lt;Field&gt;: &lt;value&gt;"]
	[-b, --body &lt;content&gt;]
	[-l, --listen &lt;addr&gt;]
	[-v, --debug]
	[--access-log]
	[&lt;status|body&gt;]</code></pre>


개발, 스테이징 및 일부 프로덕션 사용 사례에 유용한 하나 이상의 간단하고 하드 코딩된 HTTP 서버를 시작합니다. HTTP 클라이언트, 스크립 또는 로드 밸런서를 확인하거나 디버깅하는 데 유용할 수 있습니다.

`--status`는 반환할 HTTP 상태 코드입니다.

`--header`는 HTTP 헤더를 추가합니다. `Field: value` 형식이 예상됩니다. 이 플래그는 여러 번 사용할 수 있습니다.

`--body`는 응답 본문을 지정합니다. 또는 본문을 표준 입력에서 파이프(pipe)할 수 있습니다.

`--listen`은 수신 대기 주소로, Caddy가 인식하는 모든 [네트워크 주소](/docs/conventions#network-addresses)일 수 있으며 여러 서버를 시작하기 위한 포트 범위가 포함될 수 있습니다.

`--debug`는 상세 디버그 로깅을 활성화합니다.

`--access-log`는 액세스/요청 로깅을 활성화합니다.

옵션이 지정되지 않은 경우 이 명령은 사용 가능한 임의의 포트에서 수신 대기하고 빈 200 응답으로 HTTP 요청에 응답합니다. 수신 대기 주소는 `--listen` 플래그를 사용하여 사용자 정의할 수 있으며 항상 표준 출력에 인쇄됩니다. 수신 대기 주소에 포트 범위가 포함된 경우 여러 서버가 시작됩니다.

명명되지 않은 마지막 인수가 제공되면 3자리 숫자인 경우 상태 코드(`--status` 플래그와 동일)로 처리됩니다. 그렇지 않으면 응답 본문(`--body` 플래그와 동일)으로 사용됩니다. `--status` 및 `--body` 플래그는 항상 이 인수를 재정의합니다.

본문은 플래그, 명령의 (명명되지 않은) 마지막 인수 또는 (플래그와 인수가 설정되지 않은 경우) 표준 입력으로 파이프하는 등 3가지 방법으로 제공될 수 있습니다. 다음 변수를 사용하여 본문에서 제한된 [템플릿 평가(template evaluation)](https://pkg.go.dev/text/template)가 지원됩니다:

변수 | 설명
---------|-------------
`.N`       | 서버 번호
`.Port`    | 수신 대기 포트
`.Address` | 수신 대기 주소


#### <a id="examples"></a>예제

임의의 포트에서 빈 200 응답:
<pre><code class="cmd bash">caddy respond</code></pre>

본문이 포함된 HTTP 응답:
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

여러 서버 및 템플릿:
<pre><code class="cmd"><b>$ caddy respond --listen :2000-2004 "{{printf "I'm server {{.N}} on port {{.Port}}"}}"</b>

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

<b>$ curl 127.0.0.1:2002</b>
I'm server 2 on port 2002</code></pre>

유지 관리(maintenance) 페이지를 파이프(pipe):
<pre><code class="cmd bash">cat maintenance.html | caddy respond \
	--listen :80 \
	--status 503 \
	--header "Content-Type: text/html"</code></pre>




### <a id="caddy-reverse-proxy"></a>`caddy reverse-proxy`

<pre><code class="cmd bash">caddy reverse-proxy
	[-f, --from &lt;addr&gt;]
	(-t, --to &lt;addr&gt;)
	[-H, --header-up "&lt;Field&gt;: &lt;value&gt;"]
	[-d, --header-down "&lt;Field&gt;: &lt;value&gt;"]
	[-c, --change-host-header]
	[-r, --disable-redirects]
	[-i, --internal-certs]
	[-v, --debug]
	[--access-log]
	[--insecure]</code></pre>

간단하지만 프로덕션 준비가 완료된 역방향 프록시입니다. 빠른 배포, 데모 및 개발에 유용합니다.

간단히 HTTP(S) 트래픽을 `--from` 주소에서 `--to` 주소로 전송합니다. 플래그를 반복하여 여러 개의 `--to` 주소를 지정할 수 있습니다. 최소한 하나의 `--to` 주소가 필요합니다. `--to` 주소에는 여러 업스트림으로 확장하기 위한 단축키로 포트 범위를 가질 수 있습니다.

주소에서 달리 지정하지 않는 한, 호스트 이름이 제공되는 경우 `--from` 주소는 HTTPS로 간주되고 `--to` 주소는 HTTP로 간주됩니다.

`--from` 주소에 호스트나 IP가 있는 경우 Caddy는 인증서와 함께 HTTPS를 통해 프록시를 서비스하려고 시도합니다(HTTP 체계나 포트로 재정의되지 않는 한).

HTTPS로 서비스하는 경우:
  - `--disable-redirects`를 사용하여 HTTP 포트에 바인딩하는 것을 피할 수 있습니다.

  - `--internal-certs`를 사용하여 공개 인증서 발급을 시도하는 대신 내부 CA를 사용하여 인증서를 강제로 발급할 수 있습니다.

프록시의 경우:
  - `--header-up`을 사용하여 업스트림으로 보낼 요청 헤더를 설정할 수 있습니다.
  
  - `--header-down`을 사용하여 클라이언트로 다시 보낼 응답 헤더를 설정할 수 있습니다.
  
  - `--change-host-header`는 들어오는 Host 헤더를 기본값으로 사용하는 대신 요청의 Host 헤더를 업스트림의 주소로 설정합니다.

    이것은 `--header-up "Host: {http.reverse_proxy.upstream.hostport}"`의 단축키입니다.
  
  - `--insecure`는 업스트림과의 TLS 유효성 검사를 비활성화합니다. 경고: 이는 업스트림의 인증서를 확인하지 않음으로써 보안을 비활성화합니다.
  
  - `--debug`는 상세 로깅을 활성화합니다.

이 명령은 관리자 API를 비활성화하므로 로컬 개발 컴퓨터에서 여러 인스턴스를 더 쉽게 실행할 수 있습니다.



### <a id="caddy-run"></a>`caddy run`

<pre><code class="cmd bash">caddy run
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--pidfile &lt;file&gt;]
	[-e, --environ]
	[--envfile &lt;file&gt;]
	[-r, --resume]
	[-w, --watch]</code></pre>

Caddy를 실행하고 무기한 차단합니다(즉, "데몬(daemon)" 모드).

`--config`는 즉시 로드하고 사용할 초기 구성 파일을 지정합니다. `-`인 경우 구성을 표준 입력에서 읽습니다. 구성을 지정하지 않으면 Caddy는 빈 구성으로 실행되고 새 구성을 제공하는 데 사용할 수 있는 [관리자 API 엔드포인트](/docs/api)에 대한 기본 설정을 사용합니다. 특별한 경우로, 현재 작업 디렉터리에 "Caddyfile"이라는 파일이 있고 `caddyfile` 구성 어댑터가 연결되어 있는 경우(기본값) 명령줄 플래그 없이도 해당 파일이 로드되어 Caddy를 구성하는 데 사용됩니다.

`--adapter`는 초기 구성을 로드할 때 사용할 구성 어댑터의 이름입니다. `--config` 파일 이름이 `Caddyfile`로 시작하거나 `.caddyfile`로 끝나는 경우 `caddyfile` 어댑터를 가정하므로 이 플래그가 필요하지 않습니다. 그렇지 않고 제공된 구성 파일이 Caddy의 기본 JSON 형식이 아닌 경우 이 플래그가 필수입니다. 모든 경고는 로그에 인쇄되지만, 경고가 있더라도 오류 없이 적용된 구성은 즉시 사용된다는 점에 유의하세요. 적용 결과를 먼저 검토하려면 [`caddy adapt`](#caddy-adapt) 하위 명령을 사용하세요.

`--pidfile`은 PID를 지정된 파일에 씁니다.

`--environ`은 시작하기 전에 환경 변수를 인쇄합니다. 이는 `caddy environ` 명령과 동일하지만 인쇄 후 종료되지 않습니다.

`--envfile`은 `KEY=VALUE` 형식으로 지정된 파일에서 환경 변수를 로드합니다. `#`으로 시작하는 주석이 지원됩니다. 키에 `export` 접두사를 붙일 수 있습니다. 값을 큰따옴표로 묶을 수 있습니다(내부의 큰따옴표는 이스케이프할 수 있음). 다중 줄 값이 지원됩니다.

`--resume`은 자동 저장된 마지막 로드 구성을 사용하여 `--config` 플래그(있는 경우)를 무시합니다. 이 플래그를 사용하면 컴퓨터 재부팅이나 프로세스 재시작 시 구성 내구성이 보장됩니다. [API](/docs/api) 중심 배포에서 가장 유용합니다.

`--watch`는 구성 파일을 감시하고 변경된 후 자동으로 다시 로드합니다. ⚠️ 이 기능은 로컬 개발 환경에서만 사용하도록 고안되었습니다!

<aside class="advice">

프로덕션 환경에서 실행하는 동안 구성을 변경하기 위해 서버를 중지하지 마세요! 그러면 다운타임이 발생합니다(이것은 당연한 것이지만, 이와 관련된 불만이 얼마나 많은지 알면 놀랄 것입니다). 대신 [`caddy reload`](#caddy-reload) 명령을 사용하거나, 현재 로드된 구성으로 `caddy reload`와 동일한 효과를 갖는 프로세스에 `SIGUSR1` 신호를 보내세요.

</aside>



### <a id="caddy-start"></a>`caddy start`

<pre><code class="cmd bash">caddy start
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]
	[--pidfile &lt;file&gt;]
	[-w, --watch]</code></pre>

[`caddy run`](#caddy-run)과 동일하지만 백그라운드에서 실행됩니다. 이 명령은 백그라운드 프로세스가 성공적으로 실행될 때까지(또는 실행에 실패할 때까지) 차단된 다음 반환됩니다.

참고: 플래그 `--config`는 표준 입력에서 구성을 읽기 위한 `-`를 지원하지 **않습니다**.

시스템 서비스나 Windows에서는 이 명령을 사용하지 않는 것이 좋습니다. Windows에서는 하위 프로세스가 터미널에 계속 연결되어 있으므로 창을 닫으면 명확하지 않게 Caddy가 강제로 중지됩니다. 대신 [서비스로서](/docs/running) Caddy를 실행하는 것을 고려하세요.

시작되면 [`caddy stop`](#caddy-stop) 또는 [`POST /stop`](/docs/api#post-stop) API 엔드포인트를 사용하여 백그라운 프로세스를 종료할 수 있습니다.



### <a id="caddy-stop"></a>`caddy stop`

<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

<aside class="tip">

서버를 중지(하고 다시 시작)하는 것은 구성 변경과는 직교(orthogonal)하는 것입니다. **다운타임을 원하는 경우가 아니라면 프로덕션에서 구성을 변경하기 위해 stop 명령을 사용하지 마세요.** 대신 [`caddy reload`](#caddy-reload) 명령을 사용하세요.

</aside>


(stop 명령의 프로세스가 아닌) 실행 중인 Caddy 프로세스를 정상적으로 중지하고 종료되게 합니다. 관리자 API의 [`POST /stop`](/docs/api#post-stop) 엔드포인트를 사용하여 정상 종료(graceful shutdown)를 수행합니다.

이 요청의 주소는 `--address` 플래그를 사용하여, 또는 실행 중인 인스턴스의 관리자 API가 기본 수신 대기 주소를 사용하지 않는 경우 제공된 `--config`에서 사용자 정의할 수 있습니다.

현재 구성을 중지하고 싶지만 프로세스는 종료하고 싶지 않은 경우 빈 구성으로 [`caddy reload`](#caddy-reload)를 사용하거나 [`DELETE /config/`](/docs/api#delete-configpath) 엔드포인트를 사용하세요.


### <a id="caddy-storage"></a>`caddy storage`

<i>⚠️ 실험적</i>

Caddy의 구성된 데이터 저장소 내용을 내보내고 가져올 수 있습니다.

이것은 기존 저장소 모듈에서 내보내고, 구성을 업데이트한 다음, 새 모듈로 가져옴으로써 한 [저장소 모듈](/docs/json/storage/)에서 다른 모듈로 전환해야 할 때 유용합니다.

다음 명령을 사용하여 기존 구성과 새 구성을 사용하여 내보내기 명령의 출력을 가져오기 명령으로 파이프하여 서로 다른 모듈 간에 스토리지를 한 번에 복사할 수 있습니다.

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">

[파일 시스템 저장소](/docs/conventions#data-directory)를 사용할 때 내보내기 명령은 Caddy가 일반적으로 실행되는 것과 동일한 사용자로 실행해야 합니다. 그렇지 않으면 잘못된 저장소 위치가 사용될 수 있습니다.

예를 들어 Caddy를 [systemd 서비스](/docs/running#linux-service)로 실행할 때 `caddy` 사용자로 실행되므로 해당 사용자로 내보내기 또는 가져오기 명령을 실행해야 합니다. 이는 일반적으로 `sudo -u caddy <command>`로 수행할 수 있습니다.

</aside>


#### <a id="caddy-storage-export"></a>`caddy storage export`

<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;path&gt;
	[-o, --output &lt;path&gt;]</code></pre>

`--config`는 로드할 구성 파일입니다. 이는 올바른 저장소 모듈에 연결되도록 하기 위해 필수입니다.

`--output`은 타볼을 기록할 파일 이름입니다. `-`인 경우 출력은 표준 출력에 기록됩니다.



#### <a id="caddy-storage-import"></a>`caddy storage import`

<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;path&gt;
	-i, --input &lt;path&gt;</code></pre>

`--config`는 로드할 구성 파일입니다. 이는 올바른 저장소 모듈에 연결되도록 하기 위해 필수입니다.

`--input`은 읽어올 타볼의 파일 이름입니다. `-`인 경우 입력은 표준 입력에서 읽습니다.


### <a id="caddy-trust"></a>`caddy trust`

<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Caddy의 [PKI 앱](/docs/json/apps/pki/)에서 관리하는 CA에 대한 루트 인증서를 로컬 트러스트 스토어에 설치합니다.

Caddy는 루트 인증서가 처음 생성될 때 로컬 트러스트 스토어에 자동으로 설치하려고 시도하지만, Caddy에 트러스트 스토어에 쓸 수 있는 적절한 권한이 없으면 실패할 수 있습니다. (systemd를 통하는 것과 같이) 권한 없는 사용자로 서버 프로세스가 실행되는 경우, 사용 전에 인증서를 미리 설치하려면 이 명령이 필요합니다. 유닉스 시스템에서는 `sudo`를 사용하여 이 명령을 실행해야 할 수도 있습니다.

기본적으로 이 명령은 Caddy의 기본 CA(즉, "local")에 대한 루트 인증서를 설치합니다. `--ca` 플래그를 사용하여 다른 CA의 ID를 지정할 수 있습니다.

이 명령은 [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates) 엔드포인트를 사용하여 루트 인증서를 가져오기 위해 Caddy의 [관리자 API](/docs/api) 연결을 시도합니다. 실행 중인 인스턴스의 관리자 API가 기본 수신 대기 주소를 사용하지 않는 경우, `--address`를 명시적으로 지정하거나 `--config` 플래그를 사용하여 구성에서 관리자 주소를 로드할 수 있습니다.

관리자 API에 다른 컴퓨터가 접근할 수 있는 경우, 네트워크에 있는 다른 컴퓨터에 인증서를 설치하기 위해 `caddy` 바이너리와 이 명령을 함께 사용할 수도 있습니다. 이 작업을 수행할 때는 신뢰할 수 없는 클라이언트에 관리자 API를 노출하지 않도록 주의하세요.


### <a id="caddy-untrust"></a>`caddy untrust`

<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;path&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

로컬 트러스트 스토어(들)에서 루트 인증서의 신뢰를 해제합니다.

이 명령은 신뢰를 제거합니다. 트러스트 스토어에서 루트 인증서를 완전히 삭제하지는 않습니다. 따라서 새 인증서를 반복적으로 신뢰하고 신뢰 해제하면 트러스트 데이터베이스가 가득 찰 수 있습니다.

이 명령은 Caddy의 구성된 저장소에서 인증서 파일을 삭제하거나 수정하지 않습니다.

이 명령은 다음 두 가지 방법 중 하나로 사용할 수 있습니다:
- `--cert` 플래그로 신뢰 해제할 루트 인증서의 직접 경로를 지정합니다.
- [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates) 엔드포인트를 사용하여 [관리자 API](/docs/api)에서 루트 인증서를 가져옵니다. 이것은 플래그가 지정되지 않은 경우의 기본 동작입니다.

관리자 API가 사용되는 경우 CA ID의 기본값은 "local"입니다. `--ca` 플래그를 사용하여 다른 CA의 ID를 지정할 수 있습니다. 실행 중인 인스턴스의 관리자 API가 기본 수신 대기 주소를 사용하지 않는 경우, `--address`를 명시적으로 지정하거나 `--config` 플래그를 사용하여 구성에서 관리자 주소를 로드할 수 있습니다.


### <a id="caddy-upgrade"></a>`caddy upgrade`

<i>⚠️ 실험적</i>

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

현재 Caddy 바이너리를 Caddy 웹사이트에 등록된 모든 제3자 플러그인을 포함하여 동일한 모듈이 설치된 [저희 다운로드 페이지](/download)의 최신 버전으로 교체합니다.

업그레이드는 실행 중인 서버를 방해하지 않습니다. 현재 명령은 디스크에 있는 바이너리만 교체합니다. 향후 이 작업을 수행할 좋은 방법을 찾으면 변경될 수 있습니다.

업그레이드 프로세스는 내결함성(fault tolerant)을 갖습니다. 현재 바이너리를 먼저 백업(현재 것 옆에 복사)하고 문제가 발생하면 자동으로 복원합니다. 업그레이드 프로세스가 완료된 후 백업을 유지하려면 `--keep-backup` 옵션을 사용할 수 있습니다.

사용자에게 실행 파일에 쓸 권한이 없는 경우 이 명령은 상승된 권한이 필요할 수 있습니다.



### <a id="caddy-add-package"></a>`caddy add-package`

<i>⚠️ 실험적</i>

<pre><code class="cmd bash">caddy add-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

`caddy upgrade`와 유사하게 동일한 모듈이 설치된 최신 버전으로 현재 Caddy 바이너리를 교체합니다. 여기에 인수로 나열된 패키지가 새 바이너리에 추가로 포함됩니다. [다운로드 페이지](/download)에서 설치할 수 있는 패키지 목록을 찾아보세요. 각 인수는 전체 패키지 이름이어야 합니다.

예를 들어:

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>



### <a id="caddy-remove-package"></a>`caddy remove-package`

<i>⚠️ 실험적</i>

<pre><code class="cmd bash">caddy remove-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

`caddy upgrade`와 유사하게 현재 Caddy 바이너리를 동일한 모듈이 설치된 최신 버전으로 교체하지만, 인수로 나열된 패키지가 현재 바이너리에 존재하는 경우 이를 *제외(without)*합니다. `caddy list-modules --packages`를 실행하여 현재 바이너리에 포함된 비표준 모듈의 패키지 이름 목록을 확인하세요.



### <a id="caddy-validate"></a>`caddy validate`

<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]</code></pre>

구성 파일의 유효성을 검사한 다음 종료합니다. 이 명령은 구성을 역직렬화한 다음 구성을 시작하는 것처럼 모든 모듈을 로드하고 프로비저닝하지만 실제로는 구성이 시작되지 않습니다. 이는 로드 또는 프로비저닝 단계에서 발생하는 구성 오류를 노출하며 단순히 구성을 JSON으로 직렬화하는 것보다 더 강력한 오류 검사입니다.

`--config`는 유효성을 검사할 구성 파일입니다. `-`인 경우 구성을 표준 입력에서 읽습니다. 기본값은 현재 디렉터리의 `Caddyfile`입니다(있는 경우).

`--adapter`는 사용할 구성 어댑터의 이름입니다. `--config` 파일 이름이 `Caddyfile`로 시작하거나 `.caddyfile`로 끝나는 경우 `caddyfile` 어댑터를 가정하므로 이 플래그가 필요하지 않습니다. 그렇지 않고 제공된 구성 파일이 Caddy의 기본 JSON 형식이 아닌 경우 이 플래그가 필수입니다.

`--envfile`은 `KEY=VALUE` 형식으로 지정된 파일에서 환경 변수를 로드합니다. `#`으로 시작하는 주석이 지원됩니다. 키에 `export` 접두사를 붙일 수 있습니다. 값을 큰따옴표로 묶을 수 있습니다(내부의 큰따옴표는 이스케이프할 수 있음). 다중 줄 값이 지원됩니다.



### <a id="caddy-version"></a>`caddy version`
<pre><code class="cmd bash">caddy version</code></pre>

버전을 인쇄하고 종료합니다.



## <a id="signals"></a>신호(Signals)

Caddy는 특정 신호를 트랩(trap)하고 나머지는 무시합니다. 신호는 특정 프로세스 동작을 시작할 수 있습니다.

신호 | 동작
-------|----------
`SIGINT` | 정상 종료. 즉시 강제로 종료하려면 신호를 한 번 더 보냅니다.
`SIGQUIT` | Caddy를 즉시 종료하지만 스토리지는 중요하므로 스토리지의 잠금(locks)은 여전히 정리합니다.
`SIGTERM` | 정상 종료.
`SIGUSR1` | `caddy run`(`--resume` 제외)으로 시작했고 [API](/docs/api)([`caddy reload`]#caddy-reload) 포함)를 통해 구성이 변경되지 않은 경우에만 구성 파일을 다시 로드합니다.
`SIGUSR2` | 무시됨.
`SIGHUP` | 무시됨.

정상 종료는 새 연결을 더 이상 수락하지 않고 소켓이 닫히기 전에 기존 연결을 드레인(drain)한다는 의미입니다. 유예 기간(grace period)이 적용될 수 있습니다(구성 가능). 유예 기간이 지나면 연결이 강제로 해제됩니다. 정상 종료 동안 스토리지의 잠금과 개별 모듈이 릴리스해야 하는 기타 리소스가 정리됩니다.

구성 재로드 신호(`SIGUSR1`)를 받으면, (구성 텍스트가 변경되지 않았더라도 어쨌든 재로드하는) 강제 구성 재로드처럼 작동하여 디스크에서 TLS 인증서와 같은 종속 파일을 다시 로드할 수 있습니다.

신호 기반 구성 재로드는 Caddy가 구성 파일과 함께 `caddy run`으로 시작된 경우에만 활성화됩니다. Caddy가 `--resume`으로 시작되거나(API 워크플로를 의미하므로), 관리자 API를 통해 구성 변경 사항이 수신되거나, 처음 시작한 것과 _다른_ 파일 이름 또는 구성 어댑터로 `caddy reload`를 실행한 경우에는 (신호가 무시되고 로그 경고와 함께) 비활성화됩니다. 이는 재로드 방법 간의 충돌을 피하기 위한 것입니다.



## <a id="exit-codes"></a>종료 코드

Caddy는 프로세스가 종료될 때 코드를 반환합니다:

코드 | 의미
-----|---------
`0` | 정상 종료.
`1` | 시작 실패. **프로세스를 자동으로 다시 시작하지 마세요. 변경하지 않는 한 다시 오류가 발생할 가능성이 높습니다.**
`2` | 강제 종료. Caddy가 리소스를 정리하지 않고 강제로 종료되었습니다.
`3` | 종료 실패. 정리 과정에서 일부 오류와 함께 Caddy가 종료되었습니다.

bash에서는 `echo $?`로 마지막 명령의 종료 코드를 얻을 수 있습니다.
