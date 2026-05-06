---
title: Быстрый старт с API
---

<a id="api-quick-start"></a>
# Быстрый старт с API

**Предварительные требования:**
- Базовые навыки работы с терминалом / командной строкой
- `caddy` и `curl` в вашем PATH

---

Сначала запустите Caddy:

<pre><code class="cmd bash">caddy start</code></pre>

Caddy сейчас работает в простое (с пустой конфигурацией). Передайте ему простую конфигурацию через `curl`:

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

Передавать POST body через [Heredoc](https://en.wikipedia.org/wiki/Here_document#Unix_shells) может быть утомительно, поэтому если вам удобнее работать с файлами, сохраните JSON в файл `caddy.json`, а затем используйте вместо этого такую команду:

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

Теперь откройте [localhost:2015](http://localhost:2015) в браузере или используйте `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Мы также можем определить несколько сайтов на разных интерфейсах с таким JSON:

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

Обновите JSON, затем снова выполните API-запрос.

Проверьте новую конечную точку "goodbye" [в браузере](http://localhost:2016) или с помощью `curl`, чтобы убедиться, что она работает:

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Goodbye, world!</code></pre>

Когда закончите работу с Caddy, обязательно остановите его:

<pre><code class="cmd bash">caddy stop</code></pre>

С API можно сделать гораздо больше, включая экспорт конфигурации и точечные изменения config (в отличие от обновления всей конфигурации целиком). Обязательно прочитайте [полное руководство по API](/docs/api-tutorial), чтобы узнать как!

<a id="further-reading"></a>
## Дополнительное чтение

- [Полное руководство по API](/docs/api-tutorial)
- [Документация API](/docs/api)
