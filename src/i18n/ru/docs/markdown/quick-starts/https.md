---
title: Быстрый старт с HTTPS
---

<a id="https-quick-start"></a>
# Быстрый старт с HTTPS

Это руководство покажет, как очень быстро начать работу с [полностью управляемым HTTPS](/docs/automatic-https).

<aside class="tip">
	Caddy по умолчанию использует HTTPS для всех сайтов, если в конфигурации указан host name. В этом руководстве предполагается, что вы хотите поднять публично доверенный сайт (то есть не "localhost") по HTTPS, поэтому мы будем использовать публичное доменное имя и внешние порты.
</aside>

**Предварительные требования:**
- Базовые навыки работы с терминалом / командной строкой
- Базовое понимание DNS
- Зарегистрированное публичное доменное имя
- Внешний доступ к портам 80 и 443
- `caddy` и `curl` в вашем PATH

---

В этом руководстве заменяйте `example.com` на ваше настоящее доменное имя.

Настройте A/AAAA records вашего домена так, чтобы они указывали на ваш сервер. Это можно сделать, войдя к вашему DNS provider и управляя доменным именем.

Перед продолжением проверьте корректность записей авторитетным lookup. Замените `example.com` на ваше доменное имя, а если используете IPv6, замените `type=A` на `type=AAAA`:

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=example.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

Также убедитесь, что ваш сервер доступен извне на портах 80 и 443 через публичный интерфейс.

<aside class="tip">
	Если вы находитесь в домашней или другой ограниченной сети, может понадобиться пробросить порты или изменить настройки firewall.
</aside>

Все, что нужно сделать, — запустить Caddy с вашим доменным именем в конфигурации. Есть несколько способов сделать это.

<a id="caddyfile"></a>
## Caddyfile

Это самый распространенный способ получить HTTPS.

Создайте файл `Caddyfile` (без расширения), в первой строке которого указано ваше доменное имя, например:

```caddy
example.com

respond "Hello, privacy!"
```

Затем из того же каталога выполните:

<pre><code class="cmd bash">caddy run</code></pre>

Вы увидите, как Caddy provision TLS certificate и начнет обслуживать ваш сайт по HTTPS. Это стало возможно, потому что адрес сайта в Caddyfile содержал доменное имя.


<a id="the-file-server-command"></a>
## Команда `file-server`

Если вам нужно только обслуживать статические файлы по HTTPS, выполните эту команду (заменив доменное имя):

<pre><code class="cmd bash">caddy file-server --domain example.com</code></pre>

Вы увидите, как Caddy provision TLS certificate и начнет обслуживать ваш сайт по HTTPS.


<a id="the-reverse-proxy-command"></a>
## Команда `reverse-proxy`

Если вам нужен только простой обратный прокси по HTTPS (как TLS terminator), выполните эту команду (заменив доменное имя и реальный адрес backend):

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to localhost:9000</code></pre>

Вы увидите, как Caddy provision TLS certificate и начнет обслуживать ваш сайт по HTTPS.


<a id="json-config"></a>
## Конфигурация JSON

Общее практическое правило: любой [host matcher](/docs/json/apps/http/servers/routes/match/host/) запустит автоматический HTTPS.

Таким образом, такая JSON-конфигурация включит production-ready [автоматический HTTPS](/docs/automatic-https):

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["example.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Hello, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
