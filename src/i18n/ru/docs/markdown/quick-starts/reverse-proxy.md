---
title: Быстрый старт с обратным прокси
---

<a id="reverse-proxy-quick-start"></a>
# Быстрый старт с обратным прокси

Это руководство покажет, как быстро запустить production-ready обратный прокси с HTTPS или без него.

**Предварительные требования:**
- Базовые навыки работы с терминалом / командной строкой
- `caddy` в вашем PATH
- Запущенный backend-процесс, к которому нужно проксировать

---

В этом руководстве предполагается, что у вас есть backend HTTP service, работающий на `127.0.0.1:9000`. Эти команды предназначены для Linux, но те же принципы применимы и к другим операционным системам.

Можно быстро запустить простой обратный прокси без конфигурационного файла или использовать конфигурационный файл для большей гибкости и контроля.


<a id="command-line"></a>
## Командная строка

Чтобы запустить plaintext HTTP proxy с порта 2080 на порт 9000 на вашей машине:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to :9000</code></pre>

Затем проверьте:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Команда [`reverse-proxy`](/docs/command-line#reverse-proxy) предназначена для быстрых и простых обратных прокси. (Ее можно использовать в production, если ваши требования простые.)

<a id="caddyfile"></a>
## Caddyfile

В текущем рабочем каталоге создайте файл `Caddyfile` с таким содержимым:

```caddy
:2080

reverse_proxy :9000
```

Этот конфигурационный файл примерно эквивалентен команде `caddy reverse-proxy` выше.

Затем из того же каталога выполните:

<pre><code class="cmd bash">caddy run</code></pre>

Затем проверьте ваш прокси:

<pre><code class="cmd bash">curl -v 127.0.0.1:2080</code></pre>

Если вы измените Caddyfile, обязательно [перезагрузите](/docs/command-line#caddy-reload) Caddy.

Это был простой пример. С [директивой `reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) можно сделать гораздо больше.

<a id="https-from-client-to-proxy"></a>
## HTTPS от клиента к прокси

Caddy будет обслуживать ваш прокси через [HTTPS автоматически и по умолчанию](/docs/automatic-https), если знает hostname (доменное имя). Команда `caddy reverse-proxy` по умолчанию использует `localhost`, если опустить флаг `--from`; либо можно заменить первую строку Caddyfile доменным именем прокси.

- Если вы используете `localhost` или любой домен, заканчивающийся на `.localhost`, Caddy будет использовать автоматически обновляемый self-signed certificate. В первый раз может понадобиться ввести пароль, пока Caddy пытается установить корневой сертификат своего CA в ваше хранилище доверия.
- Если вы используете любое другое доменное имя, Caddy попытается получить публично доверенный сертификат; убедитесь, что ваши DNS-записи указывают на вашу машину, а порты 80 и 443 открыты для публичного доступа и направлены на Caddy.

Если порт не указан, Caddy по умолчанию использует 443 для HTTPS. В этом случае вам также потребуется разрешение на привязку к низким портам. Пара способов сделать это в Linux:

- Запустить от root (например, `sudo -E`).
- Или выполнить `sudo setcap cap_net_bind_service=+ep $(which caddy)`, чтобы дать Caddy именно эту capability.

Вот самая базовая команда `caddy reverse-proxy`, которая дает HTTPS:

<pre><code class="cmd bash">caddy reverse-proxy --to :9000</code></pre>

Затем проверьте:

<pre><code class="cmd bash">curl -v https://localhost</code></pre>

Hostname можно настроить флагом `--from`:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to :9000</code></pre>

Если у вас нет разрешения на привязку к низким портам, можно проксировать с более высокого порта:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com:8443 --to :9000</code></pre>

Если вы используете Caddyfile, просто измените первую строку на ваше доменное имя, например:

```caddy
example.com

reverse_proxy :9000
```

<a id="https-from-proxy-to-backend"></a>
## HTTPS от прокси к backend

Caddy также может проксировать по HTTPS между собой и backend, если backend поддерживает TLS. Просто используйте `https://` в адресе backend:

<pre><code class="cmd bash">caddy reverse-proxy --from :2080 --to https://localhost:9000</code></pre>

Для этого сертификат backend должен быть доверенным в системе, где запущен Caddy. (Caddy не доверяет self-signed certificates, если это явно не настроено.)

Разумеется, HTTPS можно использовать и на обоих концах:

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to https://example.com:9000</code></pre>

Это обслуживает HTTPS от клиента к прокси и от прокси к backend.

Если hostname, к которому вы проксируете, отличается от того, с которого вы проксируете, нужно использовать флаг `--change-host-header`:

<pre><code class="cmd bash">caddy reverse-proxy \
	--from example.com \
	--to https://localhost:9000 \
	--change-host-header</code></pre>

По умолчанию Caddy пропускает все HTTP headers без изменений, включая `Host`, и Caddy выводит TLS ServerName из header `Host`. Флаг `--change-host-header` сбрасывает header Host на значение backend, чтобы TLS handshake мог успешно завершиться. В примере выше он изменится с `example.com` на `localhost:9000` (а `localhost` будет использован в TLS handshake).
