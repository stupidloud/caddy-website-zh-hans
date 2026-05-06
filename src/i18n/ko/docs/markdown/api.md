---
title: "API"
---

# API

Caddy는 [REST <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Representational_state_transfer) API를 사용하여 HTTP를 통해 접근할 수 있는 관리 엔드포인트를 통해 구성됩니다. Caddy 구성에서 [이 엔드포인트를 구성](/docs/json/admin/)할 수 있습니다.

**기본 주소: `localhost:2019`**

기본 주소는 `CADDY_ADMIN` 환경 변수를 설정하여 변경할 수 있습니다. 일부 설치 방법은 이를 다른 것으로 설정할 수 있습니다. Caddy 구성의 주소가 항상 기본값보다 우선합니다.

<aside class="tip">
	서버에서 신뢰할 수 없는 코드를 실행 중인 경우(이런 😬), 프로세스를 격리하고, 취약한 프로그램을 패치하고, 권한이 있는 유닉스 소켓에 바인딩하도록 엔드포인트를 구성하여 관리 엔드포인트를 보호해야 합니다.
</aside>

최신 구성은 변경 후 디스크에 저장됩니다([비활성화](/docs/json/admin/config/)되지 않은 경우). 재시작 후 [`caddy run --resume`](/docs/command-line#caddy-run)을 사용하여 마지막으로 작동한 구성을 재개할 수 있으며, 이는 전원 주기 또는 이와 유사한 상황에서 구성의 내구성을 보장합니다.

API를 시작하려면 [API 튜토리얼](/docs/api-tutorial)을 시도해 보거나, 시간이 없다면 [API 빠른 시작 가이드](/docs/quick-starts/api)를 확인해 보세요.

---

- **[POST /load](#post-load)**
  활성 구성을 설정하거나 교체합니다.

- **[POST /stop](#post-stop)**
  활성 구성을 중지하고 프로세스를 종료합니다.

- **[GET /config/[path]](#get-configpath)**
  명명된 경로의 구성을 내보냅니다.

- **[POST /config/[path]](#post-configpath)**
  객체를 설정하거나 교체합니다. 배열에 추가합니다.
  
- **[PUT /config/[path]](#put-configpath)**
  새 객체를 생성합니다. 배열에 삽입합니다.

- **[PATCH /config/[path]](#patch-configpath)**
  기존 객체 또는 배열 요소를 교체합니다.

- **[DELETE /config/[path]](#delete-configpath)**
  명명된 경로의 값을 삭제합니다.

- **[JSON에서 `@id` 사용](#using-id-in-json)**
  구성 구조를 쉽게 순회합니다.

- **[동시 구성 변경](#concurrent-config-changes)**
  동기화되지 않은 구성 변경 시 충돌을 방지합니다.

- **[POST /adapt](#post-adapt)**
  구성을 실행하지 않고 JSON으로 조정(adapt)합니다.

- **[GET /pki/ca/&lt;id&gt;](#get-pkicaltidgt)**
  특정 [PKI 앱](/docs/json/apps/pki/) CA에 대한 정보를 반환합니다.

- **[GET /pki/ca/&lt;id&gt;/certificates](#get-pkicaltidgtcertificates)**
  특정 [PKI 앱](/docs/json/apps/pki/) CA의 인증서 체인을 반환합니다.

- **[GET /reverse_proxy/upstreams](#get-reverse-proxyupstreams)**
  구성된 프록시 업스트림의 현재 상태를 반환합니다.


## POST /load

Caddy의 구성을 설정하여 이전 구성을 모두 재정의합니다. 다시 로드가 완료되거나 실패할 때까지 차단(block)됩니다. 구성 변경은 가볍고 효율적이며 다운타임이 발생하지 않습니다. 새 구성이 어떤 이유로든 실패하면 다운타임 없이 이전 구성으로 롤백됩니다.

이 엔드포인트는 구성 어댑터를 사용하여 다양한 구성 형식을 지원합니다. 요청의 Content-Type 헤더는 요청 본문에 사용된 구성 형식을 나타냅니다. 일반적으로 이것은 Caddy의 기본 구성 형식을 나타내는 `application/json`이어야 합니다. 다른 구성 형식의 경우 슬래시 / 뒤의 값이 사용할 구성 어댑터의 이름이 되도록 적절한 Content-Type을 지정하세요. 예를 들어 Caddyfile을 제출할 때는 `text/caddyfile`과 같은 값을 사용하고, JSON 5의 경우 `application/json5`와 같은 값을 사용합니다.

새 구성이 현재 구성과 동일한 경우 다시 로드되지 않습니다. 강제로 다시 로드하려면 요청 헤더에 `Cache-Control: must-revalidate`를 설정하세요.

### 예제

새 활성 구성 설정:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: application/json" \
	-d @caddy.json</code></pre>

참고: curl의 `-d` 플래그는 줄바꿈을 제거하므로 구성 형식이 줄바꿈에 민감한 경우(예: Caddyfile) 대신 `--data-binary`를 사용하세요:

<pre><code class="cmd bash">curl "http://localhost:2019/load" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## POST /stop

서버를 우아하게 종료하고 프로세스를 종료합니다. 프로세스를 종료하지 않고 실행 중인 구성만 중지하려면 [DELETE /config/](#delete-configpath)를 사용하세요.

### 예제

프로세스 중지:

<pre><code class="cmd bash">curl -X POST "http://localhost:2019/stop"</code></pre>


## GET /config/[path]

명명된 경로에서 Caddy의 현재 구성을 내보냅니다. JSON 본문을 반환합니다.

### 예제

전체 구성을 내보내고 예쁘게 출력:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/" | jq</span>
{
	"apps": {
		"http": {
			"servers": {
				"myserver": {
					"listen": [
						":443"
					],
					"routes": [
						{
							"match": [
								{
									"host": [
										"example.com"
									]
								}
							],
							"handle": [
								{
									"handler": "file_server"
								}
							]
						}
					]
				}
			}
		}
	}
}</code></pre>

리스너 주소만 내보내기:

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/config/apps/http/servers/myserver/listen"</span>
[":443"]</code></pre>



## POST /config/[path]

명명된 경로의 Caddy 구성을 요청의 JSON 본문으로 변경합니다. 대상 값이 배열이면 POST는 추가(append)하고, 객체이면 생성하거나 교체합니다.

특별한 경우로, 다음과 같은 경우 배열에 많은 항목을 추가할 수 있습니다:

1. 경로가 `/...`로 끝나는 경우
2. `/...` 앞의 경로 요소가 배열을 참조하는 경우
3. 페이로드가 배열인 경우

이 경우 페이로드 배열의 요소가 확장되어 각각 대상 배열에 추가됩니다. Go 용어로 이것은 다음과 같은 효과를 가집니다:

```go
baseSlice = append(baseSlice, newElems...)
```

### 예제

리스너 주소 추가:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>

여러 리스너 주소 추가:

<pre><code class="cmd bash">curl \
	-H "Content-Type: application/json" \
	-d '[":8080", ":5133"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/..."</code></pre>

## PUT /config/[path]

명명된 경로의 Caddy 구성을 요청의 JSON 본문으로 변경합니다. 대상 값이 배열의 위치(인덱스)이면 PUT은 삽입하고, 객체이면 엄격하게 새 값을 생성합니다.

### 예제

첫 번째 슬롯에 리스너 주소 추가:

<pre><code class="cmd bash">curl -X PUT \
	-H "Content-Type: application/json" \
	-d '":8080"' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen/0"</code></pre>


## PATCH /config/[path]

명명된 경로의 Caddy 구성을 요청의 JSON 본문으로 변경합니다. PATCH는 기존 값이나 배열 요소를 엄격하게 교체합니다.

### 예제

리스너 주소 교체:

<pre><code class="cmd bash">curl -X PATCH \
	-H "Content-Type: application/json" \
	-d '[":8081", ":8082"]' \
	"http://localhost:2019/config/apps/http/servers/myserver/listen"</code></pre>



## DELETE /config/[path]

명명된 경로의 Caddy 구성을 제거합니다. DELETE는 대상 값을 삭제합니다.

### 예제

전체 현재 구성을 언로드하지만 프로세스는 계속 실행 상태로 두기:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/"</code></pre>

HTTP 서버 중 하나만 중지:

<pre><code class="cmd bash">curl -X DELETE "http://localhost:2019/config/apps/http/servers/myserver"</code></pre>


## JSON에서 `@id` 사용 <a id="using-id-in-json"></a>

해당 JSON 부분에 더 쉽게 직접 액세스하기 위해 JSON 문서에 ID를 포함할 수 있습니다.

객체에 `"@id"`라는 필드를 추가하고 고유한 이름을 지정하기만 하면 됩니다. 예를 들어, 자주 액세스하려는 역방향 프록시 핸들러가 있는 경우:

```json
{
	"@id": "my_proxy",
	"handler": "reverse_proxy"
}
```

이를 사용하려면 전체 경로 없이 해당하는 `/config/` 엔드포인트에 하는 것과 동일한 방식으로 `/id/` API 엔드포인트에 요청하면 됩니다. ID는 해당 구성 범위로 바로 이동하게 해줍니다.

예를 들어 ID 없이 역방향 프록시의 업스트림에 액세스하려면 경로가 다음과 같이 됩니다:

```
/config/apps/http/servers/myserver/routes/1/handle/0/upstreams
```

하지만 ID를 사용하면 경로가 다음과 같이 됩니다:

```
/id/my_proxy/upstreams
```

이는 기억하기 쉽고 손으로 쓰기도 훨씬 쉽습니다.

## 동시 구성 변경 <a id="concurrent-config-changes"></a>

<aside class="tip">

이 섹션은 모든 `/config/` 엔드포인트에 해당합니다. 이는 실험적이며 변경될 수 있습니다.

</aside>


Caddy의 구성 API는 개별 요청에 대해 [ACID 보장 <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/ACID)을 제공하지만, 단일 요청 이상의 변경은 적절하게 동기화되지 않으면 충돌이나 데이터 손실이 발생할 수 있습니다.

예를 들어, 두 클라이언트가 동시에 `GET /config/foo`를 수행하고 해당 범위(구성 경로) 내에서 편집을 한 다음, 동시에 `POST|PUT|PATCH|DELETE /config/foo/...`를 호출하여 변경 사항을 적용할 수 있습니다. 이로 인해 충돌이 발생합니다: 둘 중 하나가 다른 하나를 덮어쓰거나, 두 번째 변경이 준비되었던 것과 다른 버전의 구성에 적용되어 구성이 의도하지 않은 상태로 남을 수 있습니다. 이는 변경 사항이 서로를 인식하지 못하기 때문입니다.

Caddy의 API는 여러 요청에 걸친 트랜잭션을 지원하지 않으며 HTTP는 상태 비저장(stateless) 프로토콜입니다. 하지만 `Etag` 및 `If-Match` 헤더를 사용하여 일종의 낙관적 동시성 제어로서 모든 변경에 대한 충돌을 감지하고 방지할 수 있습니다. 이는 동기화 없이 Caddy의 `/config/...` 엔드포인트를 동시에 사용할 가능성이 있는 경우 유용합니다. `GET /config/...` 요청에 대한 모든 응답에는 경로와 해당 범위 내 내용의 해시(예: `Etag: "/config/apps/http/servers 65760b8e"`)가 포함된 `Etag`라는 HTTP 헤더가 있습니다. 변경 요청에서 `If-Match` 헤더를 이전 `GET` 요청의 Etag 헤더로 설정하기만 하면 됩니다.

이에 대한 기본 알고리즘은 다음과 같습니다:

1. 구성 내의 임의의 범위 `S`에 대해 `GET` 요청을 수행합니다. 응답의 `Etag` 헤더를 유지합니다.
2. 반환된 구성에서 원하는 변경을 수행합니다.
3. 요청 헤더 `If-Match`를 저장된 `Etag` 값으로 설정하여 범위 `S` 내에서 `POST|PUT|PATCH|DELETE` 요청을 수행합니다.
4. 응답이 HTTP 412(사전 조건 실패)이면 1단계부터 반복하거나 시도 횟수가 너무 많으면 포기합니다.

이 알고리즘은 명시적인 동기화 없이도 Caddy 구성에 대해 겹치는 여러 변경을 안전하게 허용합니다. 구성의 서로 다른 부분에 대한 동시 변경은 재시도를 요구하지 않도록 설계되었습니다: 구성의 동일한 범위를 겹치는 변경만이 충돌을 일으킬 가능성이 있으며 재시도가 필요합니다.


## POST /adapt

구성을 로드하거나 실행하지 않고 Caddy JSON으로 조정(adapt)합니다. 성공하면 결과 JSON 문서가 응답 본문으로 반환됩니다.

Content-Type 헤더는 [/load](#post-load)가 작동하는 것과 동일한 방식으로 구성 형식을 지정하는 데 사용됩니다. 예를 들어 Caddyfile을 조정하려면 `Content-Type: text/caddyfile`을 설정합니다.

이 엔드포인트는 관련 [구성 어댑터](/docs/config-adapters)가 Caddy 빌드에 연결되어 있는 한 모든 구성 형식을 조정합니다.

### 예제

Caddyfile을 JSON으로 조정:

<pre><code class="cmd bash">curl "http://localhost:2019/adapt" \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile</code></pre>


## GET /pki/ca/&lt;id&gt;

ID를 통해 특정 [PKI 앱](/docs/json/apps/pki/) CA에 대한 정보를 반환합니다. 요청된 CA ID가 기본값(`local`)인 경우 이전에 프로비저닝되지 않았다면 CA가 프로비저닝됩니다. 다른 CA ID는 이전에 프로비저닝되지 않은 경우 오류를 반환합니다.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local" | jq</span>
{
	"id": "local",
	"name": "Caddy Local Authority",
	"root_common_name": "Caddy Local Authority - 2022 ECC Root",
	"intermediate_common_name": "Caddy Local Authority - ECC Intermediate",
	"root_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... gRw==\n-----END CERTIFICATE-----\n",
	"intermediate_certificate": "-----BEGIN CERTIFICATE-----\nMIIB ... FzQ==\n-----END CERTIFICATE-----\n"
}</code></pre>


## GET /pki/ca/&lt;id&gt;/certificates

ID를 통해 특정 [PKI 앱](/docs/json/apps/pki/) CA의 인증서 체인을 반환합니다. 요청된 CA ID가 기본값(`local`)인 경우 이전에 프로비저닝되지 않았다면 CA가 프로비저닝됩니다. 다른 CA ID는 이전에 프로비저닝되지 않은 경우 오류를 반환합니다.

이 엔드포인트는 시스템의 신뢰 저장소에 CA의 루트 인증서를 설치할 수 있도록 [`caddy trust`](/docs/command-line#caddy-trust) 명령에 의해 내부적으로 사용됩니다.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/pki/ca/local/certificates"</span>
-----BEGIN CERTIFICATE-----
MIIByDCCAW2gAwIBAgIQViS12trTXBS/nyxy7Zg9JDAKBggqhkjOPQQDAjAwMS4w
...
By75JkP6C14OfU733oElfDUMa5ctbMY53rWFzQ==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBpDCCAUmgAwIBAgIQTS5a+3LUKNxC6qN3ZDR8bDAKBggqhkjOPQQDAjAwMS4w
...
9M9t0FwCIQCAlUr4ZlFzHE/3K6dARYKusR1ck4A3MtucSSyar6lgRw==
-----END CERTIFICATE-----</code></pre>


## <a id="get-reverse-proxyupstreams"></a>GET /reverse_proxy/upstreams

구성된 역방향 프록시 업스트림(백엔드)의 현재 상태를 JSON 문서로 반환합니다.

<pre><code class="cmd"><span class="bash">curl "http://localhost:2019/reverse_proxy/upstreams" | jq</span>
[
	{"address": "10.0.1.1:80", "num_requests": 4, "fails": 2},
	{"address": "10.0.1.2:80", "num_requests": 5, "fails": 4},
	{"address": "10.0.1.3:80", "num_requests": 3, "fails": 3}
]</code></pre>

JSON 배열의 각 항목은 전역 업스트림 풀에 저장된 구성된 [업스트림](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/)입니다.

- **address**는 업스트림의 다이얼 주소입니다.
- **num_requests**는 현재 업스트림에서 처리 중인 활성 요청 수입니다.
- **fails**는 수동 상태 확인에 의해 구성된 대로 기억된 현재 실패한 요청 수입니다.

백엔드의 가용성을 결정하는 것이 목표인 경우, 사용 중인 핸들러 구성과 업스트림의 관련 속성을 교차 확인해야 합니다. 예를 들어 프록시에 대해 [수동 상태 확인(passive health checks)](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/)을 활성화한 경우, 업스트림이 사용 가능한지 확인하려면 `fails` 및 `num_requests` 값도 고려해야 합니다: `fails` 양이 프록시에 대해 구성된 최대 실패 횟수(즉, [`max_fails`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/max_fails/))보다 적은지, 그리고 `num_requests`가 구성된 업스트림당 최대 요청 수(즉, 전체 프록시의 경우 [`unhealthy_request_count`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/health_checks/passive/unhealthy_request_count/), 또는 개별 업스트림의 경우 [`max_requests`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/upstreams/max_requests/)) 이하인지 확인하세요.
