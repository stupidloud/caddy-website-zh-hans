---
title: "시작하기"
---

# 시작하기

Caddy에 오신 것을 환영합니다! 이 자습서에서는 Caddy 사용의 기본 사항을 살펴보고 Caddy에 익숙해지는 데 도움을 줄 것입니다.

**목표:**
- 🔲 데몬 실행
- 🔲 API 사용해 보기
- 🔲 Caddy에 구성 제공
- 🔲 구성 테스트
- 🔲 Caddyfile 만들기
- 🔲 구성 어댑터 사용
- 🔲 초기 구성으로 시작
- 🔲 JSON과 Caddyfile 비교
- 🔲 API와 구성 파일 비교
- 🔲 백그라운드에서 실행
- 🔲 중단 시간 없는 구성 다시 로드

**전제 조건:**
- 기본 터미널 / 명령줄 기술
- 기본 텍스트 편집기 기술
- PATH에 `caddy`와 `curl` 존재

---

**패키지 관리자를 통해 [Caddy를 설치](/docs/install)한 경우, Caddy가 이미 서비스로 실행 중일 수 있습니다. 만약 그렇다면 이 자습서를 진행하기 전에 서비스를 중지해 주세요.**

먼저 실행해 보겠습니다:

<pre><code class="cmd bash">caddy</code></pre>

이런! 하위 명령이 없으면 `caddy` 명령은 도움말 텍스트만 표시합니다. 무엇을 해야 할지 잊어버렸을 때 언제든지 이것을 사용할 수 있습니다.

Caddy를 데몬으로 시작하려면 `run` 하위 명령을 사용하세요:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">데몬 실행</aside>

이것은 영원히 차단되지만, 무엇을 하고 있을까요? 현재로서는... 아무것도 하지 않습니다. 기본적으로 Caddy의 구성("config")은 비어 있습니다. 다른 터미널에서 [관리자 API](/docs/api)를 사용하여 이를 확인할 수 있습니다:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

<aside class="tip">

이것은 여러분의 웹사이트가 **아닙니다**: localhost:2019의 관리 엔드포인트는 Caddy를 제어하는 데 사용되며 기본적으로 localhost로 제한됩니다.

</aside>


<aside class="complete">API 사용해 보기</aside>

구성을 제공하여 Caddy를 유용하게 만들 수 있습니다. 여러 가지 방법으로 수행할 수 있지만, 다음 섹션에서는 `curl`을 사용하여 [/load](/docs/api#post-load) 엔드포인트에 POST 요청을 하는 것부터 시작합니다.



## 첫 번째 구성

요청을 준비하려면 구성을 만들어야 합니다. 기본적으로 Caddy의 구성은 단순한 [JSON 문서](/docs/json/)입니다.

이것을 JSON 파일(예: `caddy.json`)에 저장합니다:

```json
{
	"apps": {
		"http": {
			"servers": {
				"example": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

<aside class="tip">

반드시 구성 파일을 사용해야 하는 것은 아니지만, 이 자습서에서는 사용할 것입니다. Caddy의 [관리자 API](/docs/api)는 다른 프로그램이나 스크립트에서 사용하도록 설계되었습니다.

</aside>


그런 다음 업로드합니다:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Caddy에 구성 제공</aside>

다른 GET 요청으로 Caddy가 새 구성을 적용했는지 확인할 수 있습니다:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

브라우저에서 [localhost:2015](http://localhost:2015)로 이동하거나 `curl`을 사용하여 작동하는지 테스트해 봅니다:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

*Hello, world!*가 보인다면, 축하합니다 -- 작동하는 것입니다! 특히 프로덕션에 배포하기 전에 구성이 예상대로 작동하는지 확인하는 것은 항상 좋은 생각입니다.

<aside class="complete">구성 테스트</aside>


## 첫 번째 Caddyfile

Hello World를 위한 것치고는 *꽤 많은 작업*이었습니다.

Caddy를 구성하는 다른 방법은 [**Caddyfile**](/docs/caddyfile)을 사용하는 것입니다. 위에서 JSON으로 작성한 것과 동일한 구성을 다음과 같이 간단하게 표현할 수 있습니다:

```caddy
:2015

respond "Hello, world!"
```


이것을 현재 디렉터리에 `Caddyfile`(확장자 없음)이라는 이름의 파일로 저장합니다.

<aside class="complete">Caddyfile 만들기</aside>

Caddy가 이미 실행 중이라면 중지(<kbd>Ctrl</kbd>+<kbd>C</kbd>)한 후 다음을 실행합니다:

<pre><code class="cmd bash">caddy adapt</code></pre>

또는 Caddyfile을 다른 곳에 저장했거나 이름을 `Caddyfile`이 아닌 다른 이름으로 지정한 경우:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile</code></pre>

JSON 출력이 보일 것입니다! 여기서 무슨 일이 일어난 걸까요?

방금 [*구성 어댑터*](/docs/config-adapters)를 사용하여 Caddyfile을 Caddy의 기본 JSON 구조로 변환했습니다.

<aside class="complete">구성 어댑터 사용</aside>

해당 출력을 사용하여 다른 API 요청을 할 수도 있지만, `caddy` 명령이 알아서 처리해 주기 때문에 이 모든 단계를 건너뛸 수 있습니다. 현재 디렉터리에 Caddyfile이라는 파일이 있고 다른 구성이 지정되지 않은 경우, Caddy는 Caddyfile을 로드하고, 우리를 위해 변환(adapt)한 다음 바로 실행합니다.

이제 현재 폴더에 Caddyfile이 있으므로 `caddy run`을 다시 실행해 보겠습니다:

<pre><code class="cmd bash">caddy run</code></pre>

또는 Caddyfile이 다른 곳에 있는 경우:

<pre><code class="cmd bash">caddy run --config /path/to/Caddyfile</code></pre>

(이름이 "Caddyfile"로 시작하지 않는 다른 이름인 경우 `--adapter caddyfile`을 지정해야 합니다.)

이제 사이트를 다시 로드해 보면 작동하는 것을 볼 수 있습니다!

<aside class="complete">초기 구성으로 시작</aside>

보시다시피, 초기 구성으로 Caddy를 시작하는 방법은 여러 가지가 있습니다:

- 현재 디렉터리의 Caddyfile이라는 이름의 파일
- `--config` 플래그 (선택적으로 `--adapter` 플래그와 함께 사용)
- `--resume` 플래그 (구성이 이전에 로드된 경우)


## JSON vs. Caddyfile

이제 Caddyfile이 자동으로 JSON으로 변환된다는 것을 알았습니다.

Caddyfile이 JSON보다 쉬워 보이지만 항상 Caddyfile을 사용해야 할까요? 각 접근 방식에는 장단점이 있습니다. 대답은 여러분의 요구 사항과 사용 사례에 따라 다릅니다.

JSON | Caddyfile
-----|----------
생성하기 쉬움 | 손으로 직접 작성하기 쉬움
프로그래밍하기 쉬움 | 자동화하기 까다로움
표현력이 매우 뛰어남 | 적당히 표현력이 있음
Caddy의 모든 기능 지원 | Caddy 기능의 대부분 지원
구성 탐색 허용 | Caddyfile 내에서 탐색 불가
부분적인 구성 변경 | 전체 구성 변경만 가능
내보낼 수 있음 | 내보낼 수 없음
모든 API 엔드포인트와 호환 | 일부 API 엔드포인트와 호환
문서 자동 생성 | 문서를 직접 작성해야 함
어디에나 존재함 | 틈새 시장을 위함
더 효율적임 | 컴퓨팅 자원을 더 사용함
조금 지루함 | 조금 재밌음
**자세히 알아보기: [JSON 구조](/docs/json/)** | **자세히 알아보기: [Caddyfile 문서](/docs/caddyfile)**

사용 사례에 어떤 것이 가장 적합한지 결정해야 합니다.

JSON과 Caddyfile([및 기타 지원되는 구성 어댑터](/docs/config-adapters)) 모두 [Caddy의 API](/docs/api)와 함께 사용할 수 있다는 점에 유의해야 합니다. 그러나 Caddy의 전체 기능과 API 기능을 이용하려면 JSON을 사용해야 합니다. 구성 어댑터를 사용하는 경우 API로 구성을 로드하거나 변경하는 유일한 방법은 [/load 엔드포인트](/docs/api#post-load)뿐입니다.

<aside class="complete">JSON과 Caddyfile 비교</aside>


## API vs. 구성 파일

<aside class="tip">

내부적으로 구성 파일조차도 Caddy의 API 엔드포인트를 거칩니다. `caddy` 명령은 이러한 API 호출을 감싸줄(wrap) 뿐입니다.

</aside>


또한 워크플로를 API 기반으로 할지 CLI 기반으로 할지 결정해야 합니다. (동일한 서버에서 API와 구성 파일을 *모두* 사용할 수는 있지만 권장하지 않습니다. 단일 진실 공급원(single source of truth)을 두는 것이 가장 좋습니다.)

API | 구성 파일
----|-------------
HTTP 요청으로 구성 변경 | 셸 명령으로 구성 변경
확장하기 쉬움 | 확장하기 어려움
손으로 직접 관리하기 어려움 | 손으로 직접 관리하기 쉬움
정말 재밌음 | 역시 재밌음
**자세히 알아보기: [API 자습서](/docs/api-tutorial)** | **자세히 알아보기: [Caddyfile 자습서](/docs/caddyfile-tutorial)**

<aside class="tip">
	API를 사용하여 서버의 구성을 수동으로 관리하는 것은 REST 클라이언트 애플리케이션과 같은 적절한 도구를 사용하면 충분히 할 수 있습니다.
</aside>

API 또는 구성 파일 워크플로의 선택은 구성 어댑터의 사용과 독립적(orthogonal)입니다. JSON을 사용하되 파일에 저장하고 명령줄 인터페이스를 사용할 수 있으며, 반대로 API와 함께 Caddyfile을 사용할 수도 있습니다.

하지만 대부분의 사람들은 JSON+API 또는 Caddyfile+CLI 조합을 사용합니다.

보시다시피, Caddy는 다양한 사용 사례와 배포 환경에 매우 적합합니다!

<aside class="complete">API와 구성 파일 비교</aside>



## 시작, 중지, 실행

Caddy는 서버이므로 무기한 실행됩니다. 즉, `caddy run`을 실행하면 프로세스가 종료될 때까지(보통 <kbd>Ctrl</kbd>+<kbd>C</kbd>로) 터미널이 차단(block) 해제되지 않습니다.

`caddy run`이 가장 일반적이며 보통 권장되지만(특히 시스템 서비스를 만들 때!), 대안으로 `caddy start`를 사용하여 Caddy를 시작하고 백그라운드에서 실행되도록 할 수 있습니다:

<pre><code class="cmd bash">caddy start</code></pre>

이렇게 하면 터미널을 다시 사용할 수 있으므로 일부 대화형 헤드리스(headless) 환경에서 편리합니다.

그러면 <kbd>Ctrl</kbd>+<kbd>C</kbd>가 대신 중지해 주지 않으므로 직접 프로세스를 중지해야 합니다:

<pre><code class="cmd bash">caddy stop</code></pre>

또는 API의 [/stop 엔드포인트](/docs/api#post-stop)를 사용하세요.

<aside class="complete">백그라운드에서 실행</aside>


## 구성 다시 로드

서버는 중단 시간(downtime) 없이 구성 다시 로드/변경을 수행할 수 있습니다.

구성을 로드하거나 변경하는 모든 [API 엔드포인트](/docs/api)는 중단 시간 없이 우아하게(graceful) 작동합니다.

그러나 명령줄을 사용할 때, 새로운 구성을 적용하기 위해 <kbd>Ctrl</kbd>+<kbd>C</kbd>를 사용하여 서버를 중지했다가 다시 시작하고 싶어질 수 있습니다. 이렇게 하지 마세요: 서버를 중지하고 시작하는 것은 구성 변경과 독립적(orthogonal)이며 중단 시간이 발생합니다.

<aside class="tip">
	서버를 중지하면 서버가 다운됩니다.
</aside>

대신, 우아한 구성 변경을 위해 [`caddy reload`](/docs/command-line#caddy-reload) 명령을 사용하세요:

<pre><code class="cmd bash">caddy reload</code></pre>

이것은 실제로는 내부적으로 API를 사용하는 것일 뿐입니다. 로드를 수행하고, 필요한 경우 구성 파일을 JSON으로 변환한 다음, 중단 시간 없이 활성 구성을 우아하게 교체합니다.

새 구성을 로드하는 데 오류가 발생하면, Caddy는 작동하던 마지막 구성으로 롤백합니다.

<aside class="tip">
	기술적으로는 이전 구성이 중지되기 전에 새 구성이 시작되므로 아주 짧은 시간 동안 두 구성이 동시에 실행됩니다! 새 구성이 실패하면 오류와 함께 중단되고 이전 구성은 중지되지 않습니다.
</aside>

<aside class="complete">중단 시간 없는 구성 다시 로드</aside>
