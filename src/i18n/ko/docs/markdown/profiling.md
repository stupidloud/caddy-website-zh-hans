---
title: Caddy 프로파일링
---

Caddy 프로파일링
================

**프로그램 프로필(program profile)** 은 런타임에 프로그램의 리소스 사용에 대한 스냅샷입니다. 프로필은 문제 영역을 식별하고, 버그 및 충돌을 해결하며, 코드를 최적화하는 데 매우 유용할 수 있습니다.

Caddy는 프로필을 캡처하기 위해 [pprof](https://github.com/google/pprof)라는 Go의 도구를 사용하며, 이는 `go` 명령에 내장되어 있습니다.

프로필은 CPU 및 메모리 소비자에 대해 보고하고, 고루틴(goroutine)의 스택 추적을 표시하며, 교착 상태(deadlock) 또는 경합이 심한(high-contention) 동기화 기본 요소를 추적하는 데 도움을 줍니다.

Caddy에서 특정 버그를 보고할 때 프로필을 요청할 수 있습니다. 이 문서가 도움이 될 수 있습니다. Caddy를 사용하여 프로필을 얻는 방법과 일반적으로 결과 pprof 프로필을 사용하고 해석하는 방법 모두를 설명합니다.


시작하기 전에 알아야 할 두 가지:

1. **Caddy 프로필은 보안에 민감하지 않습니다.** 메모리 내용이 아니라 무해한 기술적 판독값이 포함되어 있습니다. 시스템에 대한 액세스 권한을 부여하지 않습니다. 안심하고 공유할 수 있습니다.
2. **프로필은 가벼우며 프로덕션 환경에서 수집할 수 있습니다.** 사실 이것은 많은 사용자에게 권장되는 모범 사례입니다. 이 문서의 뒷부분을 참조하세요.

## 프로필 얻기

프로필은 [관리자 인터페이스](/docs/api)의 `/debug/pprof/`를 통해 사용할 수 있습니다. Caddy가 실행 중인 머신의 브라우저에서 다음을 엽니다.

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	기본적으로 관리자 API는 로컬에서만 액세스할 수 있습니다. 원격, VM 또는 컨테이너에서 실행하는 경우 이 엔드포인트에 액세스하는 방법은 다음 섹션을 참조하세요.
</aside>

다음과 같은 간단한 카운트 및 링크 테이블을 볼 수 있습니다.

카운트 | 프로필
----- | --------------------
79    | allocs
0     | block
0     | cmdline
22    | goroutine
79    | heap
0     | mutex
0     | profile
29    | threadcreate
0     | trace
|     | full goroutine stack dump

카운트는 누수(leak)를 빠르게 식별하는 편리한 방법입니다. 누수가 의심되는 경우 페이지를 반복해서 새로 고치면 하나 이상의 카운트가 지속적으로 증가하는 것을 볼 수 있습니다. heap 카운트가 증가하면 메모리 누수일 수 있고, goroutine 카운트가 증가하면 고루틴 누수일 수 있습니다.

프로필을 클릭하여 어떻게 보이는지 확인해 보세요. 일부는 비어 있을 수 있으며 이는 대부분의 경우 정상입니다. 가장 일반적으로 사용되는 것은 <b>goroutine</b>(함수 스택), <b>heap</b>(메모리) 및 <b>profile</b>(CPU)입니다. 다른 프로필은 뮤텍스(mutex) 경합이나 교착 상태를 해결하는 데 유용합니다.

하단에는 각 프로필에 대한 간단한 설명이 있습니다.

- **allocs:** 과거의 모든 메모리 할당 샘플링
- **block:** 동기화 기본 요소에서 블로킹을 초래한 스택 추적
- **cmdline:** 현재 프로그램의 명령줄 호출
- **goroutine:** 현재 모든 고루틴의 스택 추적. 복구되지 않은 패닉과 동일한 형식으로 내보내려면 쿼리 매개변수로 debug=2를 사용하세요.
- **heap:** 라이브 객체의 메모리 할당 샘플링. 힙 샘플을 가져오기 전에 GC를 실행하도록 gc GET 매개변수를 지정할 수 있습니다.
- **mutex:** 경합 중인 뮤텍스 보유자의 스택 추적
- **profile:** CPU 프로필. seconds GET 매개변수에 기간을 지정할 수 있습니다. 프로필 파일을 가져온 후 go tool pprof 명령을 사용하여 프로필을 조사하세요.
- **threadcreate:** 새로운 OS 스레드 생성을 초래한 스택 추적
- **trace:** 현재 프로그램의 실행 추적. seconds GET 매개변수에 기간을 지정할 수 있습니다. 추적 파일을 가져온 후 go tool trace 명령을 사용하여 추적을 조사하세요.

<aside class="tip">

"goroutine"과 "full goroutine stack dump"의 차이점은 `?debug=2` 매개변수입니다. 전체 스택 덤프는 패닉 후에 표시되는 출력과 같습니다. 더 장황하며 동일한 고루틴을 접지(collapse) 않는다는 것이 특징입니다.

</aside>


### 프로필 다운로드

위의 pprof 인덱스 페이지에서 링크를 클릭하면 텍스트 형식의 프로필이 제공됩니다. 이것은 디버깅에 유용하며, 추가 도구 없이도 명백한 단서를 찾기 위해 훑어볼 수 있기 때문에 Caddy 팀에서 선호하는 방식입니다.

그러나 실제 기본 형식은 바이너리입니다. HTML 링크는 텍스트 표현이 없는 (CPU) "profile" 링크를 제외하고 텍스트로 형식화하기 위해 `?debug=` 쿼리 문자열 매개변수를 추가합니다.

설정할 수 있는 쿼리 문자열 매개변수는 다음과 같습니다([Go 문서](https://pkg.go.dev/net/http/pprof#hdr-Parameters) 참조).

- **`debug=N` (cpu를 제외한 모든 프로필):** 응답 형식: N = 0: 바이너리(기본값), N > 0: 일반 텍스트
- **`gc=N` (heap 프로필):** N > 0: 프로파일링 전에 가비지 수집 주기 실행
- **`seconds=N` (allocs, block, goroutine, heap, mutex, threadcreate 프로필):** 델타 프로필 반환
- **`seconds=N` (cpu, trace 프로필):** 주어진 기간 동안의 프로필

이는 HTTP 엔드포인트이므로 curl이나 wget과 같은 모든 HTTP 클라이언트를 사용하여 프로필을 다운로드할 수도 있습니다.

프로필이 다운로드되면 GitHub 이슈 댓글에 업로드하거나 [pprof.me](https://pprof.me/)와 같은 사이트를 사용할 수 있습니다. 특히 CPU 프로필의 경우 [flamegraph.com](https://flamegraph.com/)이 또 다른 옵션입니다.


## 원격 액세스

*이미 로컬에서 관리자 API에 액세스할 수 있는 경우 이 섹션을 건너뛰세요.*

기본적으로 Caddy의 관리자 API는 루프백 소켓을 통해서만 액세스할 수 있습니다. 그러나 Caddy의 `/debug/pprof` 엔드포인트에 원격으로 액세스할 수 있는 방법은 최소 3가지가 있습니다.

### 사이트를 통한 리버스 프록시

한 가지 쉬운 옵션은 사이트에서 간단히 리버스 프록시를 설정하는 것입니다.

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

물론 이렇게 하면 사이트에 연결할 수 있는 사람이 프로필을 사용할 수 있게 됩니다. 이를 원하지 않는 경우 선택한 HTTP 인증 모듈을 사용하여 인증을 추가할 수 있습니다.

(`/debug/pprof/*` 매처를 잊지 마세요. 그렇지 않으면 전체 관리자 API를 프록시하게 됩니다!)


### SSH 터널

다른 방법은 SSH 터널을 사용하는 것입니다. 이것은 컴퓨터와 서버 간의 SSH 프로토콜을 사용하는 암호화된 연결입니다. 컴퓨터에서 다음과 같은 명령을 실행합니다.

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

이렇게 하면 `example.com`의 `localhost:2019`를 (로컬 컴퓨터의) `localhost:8123`으로 터널링합니다. `username`, `example.com` 및 포트를 필요에 따라 교체해야 합니다.

<aside class="tip">

이 명령은 포그라운드에서 실행됩니다. <kbd>Ctrl</kbd>+<kbd>Z</kbd>를 사용하여 프로세스를 백그라운드로 전환하려고 하면 터널이 일시 중지되고 터널을 사용하는 연결이 실패한다는 점에 유의하세요.

</aside>

그런 다음 다른 터널에서 다음과 같이 `curl`을 실행할 수 있습니다.

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

터널의 양쪽에서 포트 `2019`를 사용하면 `-H "Host: ..."`가 필요하지 않습니다(단, 자체 컴퓨터에서 포트 `2019`가 이미 사용 중이 아니어야 합니다. 즉, 로컬에서 Caddy가 실행 중이 아니어야 함).

터널이 활성화되어 있는 동안 모든 관리자 API에 액세스할 수 있습니다. `ssh` 명령에서 <kbd>Ctrl</kbd>+<kbd>C</kbd>를 입력하여 터널을 닫습니다.

#### 장기 실행 터널

위의 명령으로 터널을 실행하려면 터미널을 열어 두어야 합니다. 백그라운드에서 터널을 실행하려면 다음과 같이 터널을 시작할 수 있습니다.

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

그러면 백그라운드에서 시작되고 `/tmp/caddy-tunnel.sock`에 제어 소켓이 만들어집니다. 터널 사용을 완료한 후 제어 소켓을 사용하여 터널을 닫을 수 있습니다.

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>


### 원격 관리자 API

승인된 클라이언트에 대한 원격 연결을 허용하도록 관리자 API를 구성할 수도 있습니다.

(TODO: 이에 대한 글 작성.)



## Goroutine 프로필

goroutine 덤프는 어떤 고루틴이 존재하고 호출 스택(call stack)이 무엇인지 아는 데 유용합니다. 즉, 현재 실행 중이거나 블로킹/대기 중인 코드에 대한 아이디어를 제공합니다.

"goroutines"를 클릭하거나 `/debug/pprof/goroutine?debug=1`로 이동하면 고루틴 목록과 그 호출 스택이 표시됩니다. 예를 들면 다음과 같습니다.

```
goroutine profile: total 88
23 @ 0x43e50e 0x436d37 0x46bda5 0x4e1327 0x4e261a 0x4e2608 0x545a65 0x5590c5 0x6b2e9b 0x50ddb8 0x6b307e 0x6b0650 0x6b6918 0x6b6921 0x4b8570 0xb11a05 0xb119d4 0xb12145 0xb1d087 0x4719c1
#	0x46bda4	internal/poll.runtime_pollWait+0x84			runtime/netpoll.go:343
#	0x4e1326	internal/poll.(*pollDesc).wait+0x26			internal/poll/fd_poll_runtime.go:84
#	0x4e2619	internal/poll.(*pollDesc).waitRead+0x279		internal/poll/fd_poll_runtime.go:89
#	0x4e2607	internal/poll.(*FD).Read+0x267				internal/poll/fd_unix.go:164
#	0x545a64	net.(*netFD).Read+0x24					net/fd_posix.go:55
#	0x5590c4	net.(*conn).Read+0x44					net/net.go:179
#	0x6b2e9a	crypto/tls.(*atLeastReader).Read+0x3a			crypto/tls/conn.go:805
#	0x50ddb7	bytes.(*Buffer).ReadFrom+0x97				bytes/buffer.go:211
#	0x6b307d	crypto/tls.(*Conn).readFromUntil+0xdd			crypto/tls/conn.go:827
#	0x6b064f	crypto/tls.(*Conn).readRecordOrCCS+0x24f		crypto/tls/conn.go:625
#	0x6b6917	crypto/tls.(*Conn).readRecord+0x157			crypto/tls/conn.go:587
#	0x6b6920	crypto/tls.(*Conn).Read+0x160				crypto/tls/conn.go:1369
#	0x4b856f	io.ReadAtLeast+0x8f					io/io.go:335
#	0xb11a04	io.ReadFull+0x64					io/io.go:354
#	0xb119d3	golang.org/x/net/http2.readFrameHeader+0x33		golang.org/x/net@v0.14.0/http2/frame.go:237
#	0xb12144	golang.org/x/net/http2.(*Framer).ReadFrame+0x84		golang.org/x/net@v0.14.0/http2/frame.go:498
#	0xb1d086	golang.org/x/net/http2.(*serverConn).readFrames+0x86	golang.org/x/net@v0.14.0/http2/server.go:818

1 @ 0x43e50e 0x44e286 0xafeeb3 0xb0af86 0x5c29fc 0x5c3225 0xb0365b 0xb03650 0x15cb6af 0x43e09b 0x4719c1
#	0xafeeb2	github.com/caddyserver/caddy/v2/cmd.cmdRun+0xcd2					github.com/caddyserver/caddy/v2@v2.7.4/cmd/commandfuncs.go:277
#	0xb0af85	github.com/caddyserver/caddy/v2/cmd.init.1.func2.WrapCommandFuncForCobra.func1+0x25	github.com/caddyserver/caddy/v2@v2.7.4/cmd/cobra.go:126
#	0x5c29fb	github.com/spf13/cobra.(*Command).execute+0x87b						github.com/spf13/cobra@v1.7.0/command.go:940
#	0x5c3224	github.com/spf13/cobra.(*Command).ExecuteC+0x3a4					github.com/spf13/cobra@v1.7.0/command.go:1068
#	0xb0365a	github.com/spf13/cobra.(*Command).Execute+0x5a						github.com/spf13/cobra@v1.7.0/command.go:992
#	0xb0364f	github.com/caddyserver/caddy/v2/cmd.Main+0x4f						github.com/caddyserver/caddy/v2@v2.7.4/cmd/main.go:65
#	0x15cb6ae	main.main+0xe										caddy/main.go:11
#	0x43e09a	runtime.main+0x2ba									runtime/proc.go:267

1 @ 0x43e50e 0x44e9c5 0x8ec085 0x4719c1
#	0x8ec084	github.com/caddyserver/certmagic.(*Cache).maintainAssets+0x304	github.com/caddyserver/certmagic@v0.19.2/maintain.go:67

...
```

첫 번째 줄인 `goroutine profile: total 88`은 우리가 무엇을 보고 있는지, 그리고 고루틴이 몇 개인지 알려줍니다.

고루틴 목록이 이어집니다. 이들은 빈도의 내림차순으로 호출 스택별로 그룹화됩니다.

고루틴 라인의 구문은 `<count> @ <addresses...>`입니다.

줄은 관련된 호출 스택이 있는 고루틴의 개수(count)로 시작합니다. `@` 기호는 고루틴을 시작한 호출 명령 주소(즉, 함수 포인터)의 시작을 나타냅니다. 각 포인터는 함수 호출 또는 호출 프레임(call frame)입니다.

많은 고루틴이 동일한 첫 번째 호출 주소를 공유한다는 것을 알 수 있습니다. 이것은 프로그램의 main 또는 진입점(entry point)입니다. 일부 고루틴은 프로그램에 다양한 `init()` 함수가 있고 Go 런타임도 고루틴을 생성할 수 있기 때문에 그곳에서 시작되지 않습니다.

`#`로 시작하는 다음 줄들은 사실 독자를 위한 주석일 뿐입니다. 이 줄에는 고루틴의 현재 스택 추적이 포함되어 있습니다. 맨 위는 스택의 맨 위, 즉 현재 실행 중인 코드 줄을 나타냅니다. 맨 아래는 스택의 맨 아래, 즉 고루틴이 초기에 실행되기 시작한 코드를 나타냅니다.

스택 추적의 형식은 다음과 같습니다.

```
<address> <package/func>+<offset> <filename>:<line>
```

주소는 함수 포인터이고, 그런 다음 Go 패키지와 함수 이름(메서드인 경우 관련된 유형 이름 포함) 및 함수 내의 명령 오프셋이 표시됩니다. 그리고 아마도 가장 유용한 정보인 파일과 줄 번호가 끝에 있습니다.

### 전체 고루틴 스택 덤프

쿼리 문자열 매개변수를 `?debug=2`로 변경하면 전체 덤프를 얻을 수 있습니다. 여기에는 모든 고루틴의 장황한 스택 추적이 포함되며, 동일한 고루틴이 접히지 않습니다. 이 출력은 바쁜 서버에서는 매우 클 수 있지만 흥미로운 정보입니다!

위의 첫 번째 호출 스택에 해당하는 하나를 살펴보겠습니다(잘림).

```
goroutine 61961905 [IO wait, 1 minutes]:
internal/poll.runtime_pollWait(0x7f9a9a059eb0, 0x72)
	runtime/netpoll.go:343 +0x85
...
golang.org/x/net/http2.(*serverConn).readFrames(0xc001756f00)
	golang.org/x/net@v0.14.0/http2/server.go:818 +0x87
created by golang.org/x/net/http2.(*serverConn).serve in goroutine 61961902
	golang.org/x/net@v0.14.0/http2/server.go:930 +0x56a
```

장황함에도 불구하고 이 덤프에서만 고유하게 제공되는 가장 유용한 정보는 모든 고루틴의 첫 번째와 마지막 줄입니다.

첫 번째 줄에는 고루틴의 번호(61961905), 상태("IO wait") 및 기간("1 minutes")이 포함되어 있습니다.

- **고루틴 번호:** 네, 고루틴에는 번호가 있습니다! 하지만 코드에는 노출되지 않습니다. 하지만 이 번호들은 스택 추적에서 특히 도움이 되는데, 어떤 고루틴이 이것을 생성했는지 볼 수 있기 때문입니다(끝 부분 참조: "created by ... in goroutine 61961902"). 아래에 표시된 도구는 이를 시각적 그래프로 그리는 데 도움이 됩니다.

- **상태:** 이것은 고루틴이 현재 무엇을 하고 있는지 알려줍니다. 볼 수 있는 몇 가지 가능한 상태는 다음과 같습니다.
	- `running`: 코드 실행 중 - 좋습니다!
	- `IO wait`: 네트워크 대기 중. 비차단(non-blocking) 네트워크 폴러(poller)에 주차되어 있기 때문에 OS 스레드를 소비하지 않습니다.
	- `sleep`: 우리 모두에게 필요한 것입니다.
	- `select`: select에서 블로킹됨; case를 사용할 수 있을 때까지 기다립니다.
	- `select (no cases):` 특히 빈 select `select {}`에서 블로킹됨. Caddy는 다른 고루틴에서 종료가 시작되기 때문에 계속 실행하기 위해 main에서 이것을 하나 사용합니다.
	- `chan receive`: 채널 수신(`<-ch`)에서 블로킹됨.
	- `semacquire`: 세마포어(저수준 동기화 기본 요소) 획득을 기다림.
	- `syscall`: 시스템 호출(system call) 실행 중. OS 스레드를 소비합니다.

- **기간:** 고루틴이 존재한 기간. 고루틴 누수와 같은 버그를 찾는 데 유용합니다. 예를 들어 몇 분 후에 모든 네트워크 연결이 닫힐 것으로 예상하는데 수많은 netconn 고루틴이 몇 시간 동안 살아 있다면 무엇을 의미할까요?

### 고루틴 덤프 해석하기

코드를 보지 않고도 위의 고루틴에 대해 무엇을 알 수 있을까요?

이 고루틴은 불과 약 1분 전에 생성되었고, 네트워크 소켓을 통해 데이터를 기다리고 있으며, 고루틴 번호가 꽤 큽니다(61961905).

첫 번째 덤프(debug=1)에서 우리는 이 호출 스택이 비교적 자주 실행된다는 것을 알고 있으며, 짧은 기간과 결합된 큰 고루틴 번호는 비교적 수명이 짧은 고루틴이 수천만 개나 생성되었음을 시사합니다. 이 고루틴은 `pollWait`라는 함수에 있으며 그 호출 기록에는 TLS를 사용하는 암호화된 네트워크 연결에서 HTTP/2 프레임을 읽는 것이 포함되어 있습니다.

따라서 우리는 이 고루틴이 HTTP/2 요청을 처리하고 있다고 추론할 수 있습니다! 클라이언트로부터 데이터를 기다리고 있습니다. 더구나 우리는 이를 생성한 고루틴이 역시 번호가 높기 때문에 프로세스의 첫 번째 고루틴 중 하나가 아니라는 것을 알고 있습니다. 덤프에서 해당 고루틴을 찾으면 기존 요청 중에 새로운 HTTP/2 스트림을 처리하기 위해 생성되었음을 알 수 있습니다. 대조적으로, 번호가 높은 다른 고루틴은 번호가 낮은 고루틴(예: 32)에 의해 생성될 수 있으며, 이는 소켓의 `Accept()` 호출에서 갓 생성된 새로운 연결을 나타냅니다.

프로그램마다 다르지만, Caddy를 디버깅할 때 이러한 패턴은 대체로 들어맞는 경향이 있습니다.

## 메모리 프로필

메모리(또는 힙) 프로필은 시스템 메모리의 주요 소비자인 힙 할당을 추적합니다. 할당(allocation)은 또한 성능 문제의 일반적인 용의자인데, 메모리를 할당하려면 시스템 호출이 필요하고 이는 느릴 수 있기 때문입니다.

힙 프로필은 맨 윗줄의 시작 부분을 제외하고 거의 모든 면에서 고루틴 프로필과 비슷해 보입니다. 다음은 그 예입니다.

```
0: 0 [1: 4096] @ 0xb1fc05 0xb1fc4d 0x48d8d1 0xb1fce6 0xb184c7 0xb1bc8e 0xb41653 0xb4105c 0xb4151d 0xb23b14 0x4719c1
#	0xb1fc04	bufio.NewWriterSize+0x24					bufio/bufio.go:599
#	0xb1fc4c	golang.org/x/net/http2.glob..func8+0x6c				golang.org/x/net@v0.17.0/http2/http2.go:263
#	0x48d8d0	sync.(*Pool).Get+0xb0						sync/pool.go:151
#	0xb1fce5	golang.org/x/net/http2.(*bufferedWriter).Write+0x45		golang.org/x/net@v0.17.0/http2/http2.go:276
#	0xb184c6	golang.org/x/net/http2.(*Framer).endWrite+0xc6			golang.org/x/net@v0.17.0/http2/frame.go:371
#	0xb1bc8d	golang.org/x/net/http2.(*Framer).WriteHeaders+0x48d		golang.org/x/net@v0.17.0/http2/frame.go:1131
#	0xb41652	golang.org/x/net/http2.(*writeResHeaders).writeHeaderBlock+0xd2	golang.org/x/net@v0.17.0/http2/write.go:239
#	0xb4105b	golang.org/x/net/http2.splitHeaderBlock+0xbb			golang.org/x/net@v0.17.0/http2/write.go:169
#	0xb4151c	golang.org/x/net/http2.(*writeResHeaders).writeFrame+0x1dc	golang.org/x/net@v0.17.0/http2/write.go:234
#	0xb23b13	golang.org/x/net/http2.(*serverConn).writeFrameAsync+0x73	golang.org/x/net@v0.17.0/http2/server.go:851
```

첫 번째 줄의 형식은 다음과 같습니다.

```
<live objects> <live memory> [<allocations>: <allocation memory>] @ <addresses...>
```

위의 예에서 `bufio.NewWriterSize()`에 의해 단일 할당이 수행되었지만 현재 이 호출 스택의 라이브 객체는 없습니다.

흥미롭게도 해당 호출 스택에서 http2 패키지가 클라이언트에 HTTP/2 프레임을 쓰기 위해 풀링된(pooled) 4KB를 사용했음을 추론할 수 있습니다. 핫 패스(hot paths)가 할당을 재사용하도록 최적화된 경우 Go 메모리 프로필에서 풀링된 개체를 자주 볼 수 있습니다. 이렇게 하면 새로운 할당이 줄어들고 힙 프로필을 통해 풀이 제대로 사용되고 있는지 알 수 있습니다!

## CPU 프로필

CPU 프로필은 Go 프로그램이 프로세서에 예약된 시간의 대부분을 어디에서 보내는지 이해하는 데 도움이 됩니다.

그러나 이에 대한 일반 텍스트 형식은 없으므로 다음 섹션에서는 `go tool pprof` 명령을 사용하여 읽어보겠습니다.

CPU 프로필을 다운로드하려면 `/debug/pprof/profile?seconds=N`으로 요청을 보냅니다. 여기서 N은 프로필을 수집할 기간(초)입니다. CPU 프로필 수집 중에는 프로그램 성능에 약간의 영향을 미칠 수 있습니다. (다른 프로필은 성능에 거의 영향을 미치지 않습니다.)

완료되면 `profile`이라는 적절한 이름의 바이너리 파일을 다운로드해야 합니다. 그런 다음 이를 검사해야 합니다.

## `go tool pprof`

예제로 Go에 내장된 프로필 분석기를 사용하여 CPU 프로필을 읽겠지만 어떤 종류의 프로필이든 사용할 수 있습니다.

대화형 프롬프트를 여는 다음 명령(실제 파일 경로가 다를 경우 "profile"을 대체)을 실행합니다.

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">

이 명령을 사용하여 CPU 프로필뿐만 아니라 모든 유형의 프로필을 검사할 수 있습니다. 원리는 다른 프로필과 동일하며 개념은 이어집니다.

</aside>

이것은 여러분이 탐색할 수 있는 것입니다. `help`를 입력하면 명령 목록이 표시되고 `o`를 입력하면 현재 옵션이 표시됩니다. 그리고 `help <command>`를 입력하면 특정 명령에 대한 정보를 얻을 수 있습니다.

명령이 많지만 일반적인 명령은 다음과 같습니다.

- `top`: 가장 많은 CPU를 사용한 것을 표시합니다. 더 많이 보려면 `top 20`과 같은 숫자를 추가하거나, 특정 항목에 "초점(focus)"을 맞추거나 무시하려면 정규식을 추가할 수 있습니다.
- `web`: 웹 브라우저에서 호출 그래프(call graph)를 엽니다. CPU 사용량을 시각적으로 확인하기에 아주 좋은 방법입니다.
- `svg`: 호출 그래프의 SVG 이미지를 생성합니다. 웹 브라우저를 열지 않고 SVG가 로컬에 저장된다는 점을 제외하면 `web`과 동일합니다.
- `tree`: 호출 스택의 표 형식 보기입니다.

`top`부터 시작해 봅시다. 다음과 같은 출력이 표시됩니다.

```
(pprof) top
Showing nodes accounting for 38.36s, 54.71% of 70.11s total
Dropped 785 nodes (cum <= 0.35s)
Showing top 10 nodes out of 196
      flat  flat%   sum%        cum   cum%
    10.97s 15.65% 15.65%     10.97s 15.65%  runtime/internal/syscall.Syscall6
     6.59s  9.40% 25.05%     36.65s 52.27%  runtime.gcDrain
     5.03s  7.17% 32.22%      5.34s  7.62%  runtime.(*lfstack).pop (inline)
     3.69s  5.26% 37.48%     11.02s 15.72%  runtime.scanobject
     2.42s  3.45% 40.94%      2.42s  3.45%  runtime.(*lfstack).push
     2.26s  3.22% 44.16%      2.30s  3.28%  runtime.pageIndexOf (inline)
     2.11s  3.01% 47.17%      2.56s  3.65%  runtime.findObject
     2.03s  2.90% 50.06%      2.03s  2.90%  runtime.markBits.isMarked (inline)
     1.69s  2.41% 52.47%      1.69s  2.41%  runtime.memclrNoHeapPointers
     1.57s  2.24% 54.71%      1.57s  2.24%  runtime.epollwait
```

CPU의 상위 10개 소비자는 모두 Go 런타임에 속해 있었습니다. 특히 가비지 수집이 많았습니다(syscall은 메모리를 확보하고 할당하는 데 사용된다는 것을 기억하세요). 이것은 성능을 향상시키기 위해 할당을 줄일 수 있다는 힌트이며, 힙 프로필은 가치가 있을 것입니다.

알겠습니다. 하지만 우리 코드의 CPU 사용률을 보고 싶다면 어떻게 해야 할까요? 다음과 같이 "runtime"이 포함된 패턴을 무시할 수 있습니다.

```
(pprof) top -runtime  
Active filters:
   ignore=runtime
Showing nodes accounting for 0.92s, 1.31% of 70.11s total
Dropped 160 nodes (cum <= 0.35s)
Showing top 10 nodes out of 243
      flat  flat%   sum%        cum   cum%
     0.17s  0.24%  0.24%      0.28s   0.4%  sync.(*Pool).getSlow
     0.11s  0.16%   0.4%      0.11s  0.16%  github.com/prometheus/client_golang/prometheus.(*histogram).observe (inline)
     0.10s  0.14%  0.54%      0.23s  0.33%  github.com/prometheus/client_golang/prometheus.(*MetricVec).hashLabels
     0.10s  0.14%  0.68%      0.12s  0.17%  net/textproto.CanonicalMIMEHeaderKey
     0.10s  0.14%  0.83%      0.10s  0.14%  sync.(*poolChain).popTail
     0.08s  0.11%  0.94%      0.26s  0.37%  github.com/prometheus/client_golang/prometheus.(*histogram).Observe
     0.07s   0.1%  1.04%      0.07s   0.1%  internal/poll.(*fdMutex).rwlock
     0.07s   0.1%  1.14%      0.10s  0.14%  path/filepath.Clean
     0.06s 0.086%  1.23%      0.06s 0.086%  context.value
     0.06s 0.086%  1.31%      0.06s 0.086%  go.uber.org/zap/buffer.(*Buffer).AppendByte
```

음, Prometheus 메트릭이 또 다른 주요 소비자라는 것은 분명하지만 누적(cum)으로 보면 위의 GC보다 몇 배나 낮다는 것을 알 수 있습니다. 이 엄청난 차이는 GC를 줄이는 데 집중해야 함을 시사합니다.

<aside class="tip">

CPU 프로필은 간헐적 샘플링에서 측정값을 얻으며, 샘플은 샘플링 속도(기본값은 10ms)보다 더 자주 수집되지 않는다는 점에 유의하는 것이 중요합니다. 그렇기 때문에 10ms 미만의 누적 시간(cum)을 볼 수 없는 것입니다(아마도 그보다 작을 텐데, 반올림된 것임). 보다 구체적인 타이밍의 경우 샘플링을 사용하지 않는 실행 추적(execution trace)을 수행할 수 있습니다. (TODO: 추적에 대한 섹션 추가.)

</aside>

`q`를 사용하여 이 프로필을 종료하고 힙 프로필에 대해 동일한 명령을 사용해 보겠습니다.

```
(pprof) top
Showing nodes accounting for 22259.07kB, 81.30% of 27380.04kB total
Showing top 10 nodes out of 102
      flat  flat%   sum%        cum   cum%
   12300kB 44.92% 44.92%    12300kB 44.92%  runtime.allocm
 2570.01kB  9.39% 54.31%  2570.01kB  9.39%  bufio.NewReaderSize
 2048.81kB  7.48% 61.79%  2048.81kB  7.48%  runtime.malg
 1542.01kB  5.63% 67.42%  1542.01kB  5.63%  bufio.NewWriterSize
 ...
 ```

빙고. 버퍼링을 위한 bufio 패키지 사용에서 읽기 및 쓰기 버퍼에 메모리의 거의 절반이 할당됩니다. 따라서 코드를 최적화하여 버퍼링을 줄이면 매우 유리할 것이라고 추론할 수 있습니다. (Caddy의 [관련 패치](https://github.com/caddyserver/caddy/pull/4978)가 바로 그 작업을 수행합니다).

### 시각화

대신 `svg` 또는 `web` 명령을 실행하면 프로필의 시각화가 나타납니다.

![CPU profile visualization](/old/resources/images/profile.png)

이것은 CPU 프로필이지만 다른 프로필 유형에 대해서도 유사한 그래프를 사용할 수 있습니다.

이러한 그래프를 읽는 방법을 알아보려면 [pprof 문서](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph)를 읽어보세요.


### 프로필 차이 분석 (Diffing profiles)

코드를 변경한 후 차이 분석("diff")을 사용하여 전후를 비교할 수 있습니다. 다음은 힙의 diff입니다.

<pre><code class="cmd bash">go tool pprof -diff_base=before.prof after.prof
File: caddy
Type: inuse_space
Time: Aug 29, 2022 at 1:21am (MDT)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) top
Showing nodes accounting for -26.97MB, 49.32% of 54.68MB total
Dropped 10 nodes (cum <= 0.27MB)
Showing top 10 nodes out of 137
      flat  flat%   sum%        cum   cum%
  -27.04MB 49.45% 49.45%   -27.04MB 49.45%  bufio.NewWriterSize
      -2MB  3.66% 53.11%       -2MB  3.66%  runtime.allocm
    1.06MB  1.93% 51.18%     1.06MB  1.93%  github.com/yuin/goldmark/util.init
    1.03MB  1.89% 49.29%     1.03MB  1.89%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.glob..func2
       1MB  1.84% 47.46%        1MB  1.84%  bufio.NewReaderSize
      -1MB  1.83% 49.29%       -1MB  1.83%  runtime.malg
       1MB  1.83% 47.46%        1MB  1.83%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.cloneRequest
      -1MB  1.83% 49.29%       -1MB  1.83%  net/http.(*Server).newConn
   -0.55MB  1.00% 50.29%    -0.55MB  1.00%  html.populateMaps
    0.53MB  0.97% 49.32%     0.53MB  0.97%  github.com/alecthomas/chroma.TypeRemappingLexer</code></pre>

보시다시피 메모리 할당을 약 절반으로 줄였습니다!

Diff도 시각화할 수 있습니다.

![CPU profile visualization](/old/resources/images/profile-diff.png)

이렇게 하면 변경 사항이 프로그램의 특정 부분 성능에 어떤 영향을 미쳤는지 매우 명확하게 알 수 있습니다.

## 추가 읽을거리

프로그램 프로파일링에는 마스터해야 할 것이 많고 우리는 그저 겉핥기만 했을 뿐입니다.

"프로파일링(profiling)"의 진정한 "프로(pro)"가 되려면 다음 리소스를 고려하세요.

- [pprof 문서](https://github.com/google/pprof/blob/main/doc/README.md)
- [Caddy 프로필의 실제 사용 사례](https://github.com/caddyserver/caddy/pull/4978)
- [Go wiki의 성능(Performance)](https://github.com/golang/go/wiki/Performance)
- [`net/http/pprof` 패키지](https://pkg.go.dev/net/http/pprof)
