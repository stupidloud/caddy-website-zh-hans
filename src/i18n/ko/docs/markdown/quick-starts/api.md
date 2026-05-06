---
title: API Quick-start
---

# API 빠른 시작

**사전 준비사항:**
- 기본적인 터미널 / 명령줄 기술
- PATH에 `caddy`와 `curl` 포함

---

먼저 Caddy를 시작합니다:

<pre><code class="cmd bash">caddy start</code></pre>

Caddy는 현재 아무 설정 없이 유휴 상태(빈 구성)로 실행 중입니다. `curl`을 사용하여 간단한 설정을 부여해 보겠습니다:

<pre><code class="cmd bash">curl localhost:2019/load \
    -H "Content-Type: application/json" \
    -d @- << EOF
    {
        "apps": {
            "http": {
                "servers": {
                    "hello": {
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
EOF</code></pre>

[Heredoc](https://en.wikipedia.org/wiki/Here_document#Unix_shells)을 사용하여 POST 본문을 제공하는 것은 번거로울 수 있으므로, 파일 사용을 선호하신다면 JSON을 `caddy.json`이라는 파일에 저장한 후 다음 명령어를 대신 사용하세요:

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

이제 브라우저에서 [localhost:2015](http://localhost:2015)를 불러오거나 `curl`을 사용합니다:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

다음 JSON을 사용해 서로 다른 인터페이스에 여러 사이트를 정의할 수도 있습니다:

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				},
				"bye": {
					"listen": [":2016"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Goodbye, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

JSON을 업데이트한 후 API 요청을 다시 수행합니다.

새로운 "goodbye" 엔드포인트를 [브라우저](http://localhost:2016)나 `curl`에서 테스트하여 제대로 작동하는지 확인해 보세요:

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Goodbye, world!</code></pre>

Caddy 사용을 완료했다면 중지하는 것을 잊지 마세요:

<pre><code class="cmd bash">caddy stop</code></pre>

설정 내보내기, 전체 설정 업데이트가 아닌 세분화된 설정 변경 등 API를 사용하여 훨씬 더 많은 작업을 할 수 있습니다. 사용 방법을 알아보려면 [전체 API 튜토리얼](/docs/api-tutorial)을 반드시 읽어보세요!

## 더 읽어보기

- [전체 API 튜토리얼](/docs/api-tutorial)
- [API 문서](/docs/api)
