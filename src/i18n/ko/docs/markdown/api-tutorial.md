---
title: "API 튜토리얼"
---

# API 튜토리얼

이 튜토리얼에서는 프로그래밍 방식으로 자동화할 수 있게 해주는 Caddy의 [관리자 API](/docs/api) 사용 방법을 보여줍니다.

**목표:**
- 🔲 데몬 실행
- 🔲 Caddy에 구성(config) 제공
- 🔲 구성 테스트
- 🔲 활성 구성 교체
- 🔲 구성 순회(traverse)
- 🔲 `@id` 태그 사용

**사전 준비 사항:**
- 기본적인 터미널 / 명령줄 기술
- 기본적인 JSON 사용 경험
- PATH에 `caddy` 및 `curl` 포함

---

Caddy 데몬을 시작하려면 `run` 하위 명령을 사용하세요:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">데몬 실행</aside>

이 명령은 영원히 블록되지만, 무엇을 하고 있을까요? 현재로서는... 아무것도 하지 않습니다. 기본적으로 Caddy의 구성("config")은 비어 있습니다. 다른 터미널에서 [관리자 API](/docs/api)를 사용하여 이를 확인할 수 있습니다:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

구성을 제공하여 Caddy를 유용하게 만들 수 있습니다. 이를 수행하는 한 가지 방법은 [/load](/docs/api#post-load) 엔드포인트에 POST 요청을 하는 것입니다. 다른 HTTP 요청과 마찬가지로 이 작업을 수행하는 방법은 많지만, 이 튜토리얼에서는 `curl`을 사용합니다.

## 첫 번째 구성

요청을 준비하려면 구성을 만들어야 합니다. Caddy의 구성은 단순히 [JSON 문서](/docs/json/)(또는 [JSON으로 변환되는 모든 것](/docs/config-adapters))입니다.

<aside class="tip">
	구성 파일은 필수가 아닙니다. 구성 API는 파일 없이도 항상 사용할 수 있으며, 이는 작업을 자동화할 때 편리합니다. 이 튜토리얼에서는 손으로 편집하기가 더 편리하기 때문에 파일을 사용합니다.
</aside>

이것을 JSON 파일로 저장하세요:

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

그런 다음 업로드하세요:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	파일명 앞에 @를 잊지 않도록 하세요. 이것은 curl에게 파일을 보내고 있음을 알려줍니다.
</aside>

<aside class="complete">Caddy에 구성 제공</aside>

다른 GET 요청으로 Caddy가 새 구성을 적용했는지 확인할 수 있습니다:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

브라우저에서 [localhost:2015](http://localhost:2015)로 이동하거나 `curl`을 사용하여 작동하는지 테스트하세요:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">구성 테스트</aside>

*Hello, world!*가 표시된다면 축하합니다. 작동하는 것입니다! 특히 프로덕션에 배포하기 전에 구성이 예상대로 작동하는지 확인하는 것은 항상 좋은 생각입니다.

환영 메시지를 "Hello world!"에서 조금 더 동기 부여가 되는 "I can do hard things."로 변경해 보겠습니다. 구성 파일에서 이 변경을 수행하여 핸들러 객체가 다음과 같이 보이게 하세요:

```json
{
	"handler": "static_response",
	"body": "I can do hard things."
}
```

구성 파일을 저장한 다음, 동일한 POST 요청을 다시 실행하여 Caddy의 활성 구성을 업데이트하세요:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">활성 구성 교체</aside>

확실히 하기 위해 구성이 업데이트되었는지 확인하세요:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

브라우저에서 페이지를 새로고침하거나(`curl`을 다시 실행하여) 테스트하면 영감을 주는 메시지가 표시됩니다!


## 구성 순회

작은 변경을 위해 전체 구성 파일을 업로드하는 대신, 구성 파일을 건드리지 않고 변경할 수 있는 Caddy API의 강력한 기능을 사용해 보겠습니다.

<aside class="tip">
	위에서 했던 것처럼 전체 구성을 교체하여 프로덕션 서버를 조금씩 변경하는 것은 위험할 수 있습니다. 이는 파일 시스템에 대한 루트 권한을 갖는 것과 같습니다. Caddy의 API를 사용하면 구성의 다른 부분이 실수로 변경되지 않도록 변경 범위를 제한할 수 있습니다.
</aside>

요청 URI의 경로를 사용하여 구성 구조를 순회하고 메시지 문자열만 업데이트할 수 있습니다(잘린 경우 오른쪽으로 스크롤하세요):

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Work smarter, not harder."'
</code></pre>


<aside class="tip">

API를 사용하여 구성을 변경할 때마다 Caddy는 나중에 [**--resume** 할 수 있도록](/docs/command-line#caddy-run) 새 구성의 복사본을 지속적으로 저장합니다!

</aside>


예를 들어 비슷한 GET 요청으로 작동했는지 확인할 수 있습니다:

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

다음과 같이 표시되어야 합니다:

```json
[{"handle":[{"body":"Work smarter, not harder.","handler":"static_response"}]}]
```


<aside class="tip">

[`jq` 명령 <img src="/old/resources/images/external-link.svg" class="external-link">](https://stedolan.github.io/jq/)을 사용하여 JSON 출력을 예쁘게 만들 수 있습니다: **`curl ... | jq`**

</aside>


<aside class="complete">구성 순회</aside>

**중요 참고:** 당연한 말이지만, API를 사용하여 원본 구성 파일에 없는 변경을 수행하면 구성 파일은 더 이상 사용되지 않게 됩니다. 이를 처리하는 방법에는 몇 가지가 있습니다:

- [caddy run](/docs/command-line#caddy-run) 명령의 `--resume`을 사용하여 마지막 활성 구성을 사용합니다.
- 구성 파일 사용과 API를 통한 변경을 혼합하지 말고 하나의 진실의 원천(source of truth)을 가지세요.
- 후속 GET 요청으로 [Caddy의 새 구성을 내보냅니다](/docs/api#get-configpath)(처음 두 옵션보다 권장되지 않음).



## JSON에서 `@id` 사용

구성 순회는 확실히 유용하지만, 경로가 조금 길다고 생각하지 않으시나요?

핸들러 객체에 [`@id` 태그](/docs/api#using-id-in-json)를 지정하여 더 쉽게 접근할 수 있습니다:

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

이렇게 하면 핸들러 객체에 `"@id": "msg"` 속성이 추가되므로 이제 다음과 같이 보입니다:

```json
{
	"@id": "msg",
	"body": "Work smarter, not harder.",
	"handler": "static_response"
}
```


<aside class="tip">

**@id** 태그는 모든 객체에 들어갈 수 있으며 기본값(일반적으로 문자열)을 가질 수 있습니다. [자세히 알아보기](/docs/api#using-id-in-json)

</aside>


그런 다음 직접 접근할 수 있습니다:

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

그리고 이제 더 짧은 경로로 메시지를 변경할 수 있습니다:

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Some shortcuts are good."'
</code></pre>

다시 확인해 보세요:

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete"><code>@id</code> 태그 사용</aside>