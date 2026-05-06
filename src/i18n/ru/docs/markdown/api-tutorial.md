---
title: "Руководство по API"
---

<a id="api-tutorial"></a>
# Руководство по API

Это руководство покажет, как использовать [admin API](/docs/api) Caddy, который позволяет автоматизировать работу программируемым способом.

**Цели:**
- 🔲 Запустить daemon
- 🔲 Передать Caddy конфигурацию
- 🔲 Проверить конфигурацию
- 🔲 Заменить активную конфигурацию
- 🔲 Обходить конфигурацию
- 🔲 Использовать теги `@id`

**Предварительные требования:**
- Базовые навыки работы с терминалом / командной строкой
- Базовый опыт с JSON
- `caddy` и `curl` в вашем PATH

---

Чтобы запустить daemon Caddy, используйте подкоманду `run`:

<pre><code class="cmd bash">caddy run</code></pre>

<aside class="complete">Запустить daemon</aside>

Эта команда блокируется навсегда, но что она делает? Сейчас... ничего. По умолчанию конфигурация Caddy ("config") пустая. Это можно проверить через [admin API](/docs/api) в другом терминале:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Чтобы Caddy начал приносить пользу, ему нужно передать config. Один способ сделать это — выполнить POST-запрос к endpoint [/load](/docs/api#post-load). Как и любой HTTP request, это можно сделать многими способами, но в этом руководстве мы используем `curl`.

<a id="your-first-config"></a>
## Ваша первая конфигурация

Чтобы подготовить request, нам нужно создать config. Конфигурация Caddy — это просто [документ JSON](/docs/json/) (или [что угодно, что преобразуется в JSON](/docs/config-adapters)).

<aside class="tip">
	Конфигурационные файлы не обязательны. Configuration API всегда можно использовать без файлов, что удобно при автоматизации. Это руководство использует файл, потому что так удобнее редактировать вручную.
</aside>

Сохраните это в JSON-файл:

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

Затем загрузите его:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="tip">
	Убедитесь, что не забыли @ перед именем файла; это сообщает curl, что вы отправляете файл.
</aside>

<aside class="complete">Передать Caddy конфигурацию</aside>

Можно проверить, что Caddy применил новую config, еще одним GET request:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Проверьте, что она работает: откройте [localhost:2015](http://localhost:2015) в браузере или используйте `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

<aside class="complete">Проверить конфигурацию</aside>

Если вы видите *Hello, world!*, поздравляем — все работает! Всегда полезно убедиться, что config работает так, как вы ожидаете, особенно перед развертыванием в production.

Изменим приветственное сообщение с "Hello world!" на что-то чуть более мотивирующее: "I can do hard things." Внесите это изменение в конфигурационный файл, чтобы объект handler теперь выглядел так:

```json
{
	"handler": "static_response",
	"body": "I can do hard things."
}
```

Сохраните конфигурационный файл, затем обновите активную конфигурацию Caddy, снова выполнив тот же POST request:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/json" \
	-d @caddy.json
</code></pre>

<aside class="complete">Заменить активную конфигурацию</aside>

Для уверенности проверьте, что config обновилась:

<pre><code class="cmd bash">curl localhost:2019/config/</code></pre>

Проверьте это, обновив страницу в браузере (или снова выполнив `curl`), и вы увидите вдохновляющее сообщение!


<a id="config-traversal"></a>
## Обход конфигурации

Вместо загрузки всего config file ради небольшого изменения используем мощную возможность API Caddy, чтобы внести изменение, вообще не трогая config file.

<aside class="tip">
	Вносить небольшие изменения на production servers, заменяя весь config, как мы сделали выше, может быть опасно; это похоже на root-доступ к файловой системе. API Caddy позволяет ограничить scope ваших изменений и гарантировать, что другие части config не будут случайно изменены.
</aside>

Используя path из request URI, можно пройти внутрь структуры config и обновить только строку сообщения (прокрутите вправо, если строка обрезана):

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/body \
	-H "Content-Type: application/json" \
	-d '"Work smarter, not harder."'
</code></pre>


<aside class="tip">

Каждый раз, когда вы изменяете config через API, Caddy сохраняет копию новой config, чтобы позже ее можно было [**--resume**](/docs/command-line#caddy-run)!

</aside>


Можно проверить, что это сработало, похожим GET request, например:

<pre><code class="cmd bash">curl localhost:2019/config/apps/http/servers/example/routes</code></pre>

Вы должны увидеть:

```json
[{"handle":[{"body":"Work smarter, not harder.","handler":"static_response"}]}]
```


<aside class="tip">

Можно использовать [`jq` command <img src="/old/resources/images/external-link.svg" class="external-link">](https://stedolan.github.io/jq/), чтобы prettify JSON output: **`curl ... | jq`**

</aside>


<aside class="complete">Обходить конфигурацию</aside>

**Важное примечание:** Это должно быть очевидно, но после того как вы используете API для изменения, которого нет в исходном config file, ваш config file устаревает. Есть несколько способов с этим работать:

- Используйте `--resume` команды [caddy run](/docs/command-line#caddy-run), чтобы использовать последнюю активную config.
- Не смешивайте использование config files с изменениями через API; имейте один источник истины.
- [Экспортируйте новую конфигурацию Caddy](/docs/api#get-configpath) последующим GET request (менее рекомендуется, чем первые два варианта).



<a id="using-id-in-json"></a>
## Использование `@id` в JSON

Config traversal, конечно, полезен, но paths немного длинные, не так ли?

Можно добавить нашему объекту handler [тег `@id`](/docs/api#using-id-in-json), чтобы обращаться к нему проще:

<pre><code class="cmd bash">curl \
	localhost:2019/config/apps/http/servers/example/routes/0/handle/0/@id \
	-H "Content-Type: application/json" \
	-d '"msg"'
</code></pre>

Это добавляет свойство к нашему объекту handler: `"@id": "msg"`, поэтому теперь он выглядит так:

```json
{
	"@id": "msg",
	"body": "Work smarter, not harder.",
	"handler": "static_response"
}
```


<aside class="tip">

Теги **@id** могут находиться в любом object и иметь любое primitive value (обычно string). [Подробнее](/docs/api#using-id-in-json)

</aside>


Теперь можно обратиться к нему напрямую:

<pre><code class="cmd bash">curl localhost:2019/id/msg</code></pre>

И теперь можно изменить сообщение более коротким path:

<pre><code class="cmd bash">curl \
	localhost:2019/id/msg/body \
	-H "Content-Type: application/json" \
	-d '"Some shortcuts are good."'
</code></pre>

И проверить его снова:

<pre><code class="cmd bash">curl localhost:2019/id/msg/body</code></pre>

<aside class="complete">Использовать теги <code>@id</code></aside>
