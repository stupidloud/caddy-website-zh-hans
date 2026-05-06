---
title: Быстрый старт с Caddyfile
---

<a id="caddyfile-quick-start"></a>
# Быстрый старт с Caddyfile

Создайте новый текстовый файл с именем `Caddyfile` (без расширения).

Первое, что нужно указать в Caddyfile, — адрес вашего сайта:

```caddy
localhost
```

<aside class="tip">

Если порты HTTP и HTTPS (80 и 443 соответственно) являются привилегированными портами в вашей ОС, вам нужно либо запускать с повышенными правами, либо использовать более высокие порты. Чтобы получить разрешение, запустите от root через `sudo -E` или используйте `sudo setcap cap_net_bind_service=+ep $(which caddy)`. Либо, чтобы использовать более высокие порты, просто измените адрес на что-то вроде `localhost:2080` и измените HTTP-порт с помощью параметра Caddyfile [`http_port`](/docs/caddyfile/options).

</aside>

Затем нажмите Enter и укажите, что он должен делать, чтобы получилось так:

```caddy
localhost

respond "Hello, world!"
```

Сохраните это и запустите Caddy из той же папки, где находится ваш Caddyfile:

<pre><code class="cmd bash">caddy start</code></pre>

Вероятно, у вас попросят пароль, потому что Caddy по умолчанию обслуживает все сайты — даже локальные — через HTTPS. (Запрос пароля должен появиться только в первый раз!)

<aside class="tip">

Для локального HTTPS Caddy автоматически создает сертификаты и уникальные приватные ключи. Корневой сертификат добавляется в хранилище доверенных сертификатов вашей системы, поэтому и нужен запрос пароля. Это позволяет локально разрабатывать через HTTPS без ошибок сертификатов.

</aside>

(Если вы получаете ошибки прав доступа, возможно, нужно запустить с повышенными правами или выбрать порт выше 1023.)

Откройте [localhost](http://localhost) в браузере или запросите его через `curl`:

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Hello, world!</code></pre>

В Caddyfile можно определить несколько сайтов, обернув их в фигурные скобки `{ }`. Измените ваш Caddyfile так:

```caddy
localhost {
	respond "Hello, world!"
}

localhost:2016 {
	respond "Goodbye, world!"
}
```

Обновленную конфигурацию можно передать Caddy двумя способами: напрямую через API:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

или командой reload, которая выполняет тот же API-запрос за вас:

<pre><code class="cmd bash">caddy reload</code></pre>

Проверьте новую конечную точку "goodbye" [в браузере](https://localhost:2016) или с помощью `curl`, чтобы убедиться, что она работает:

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Goodbye, world!</code></pre>

Когда закончите работу с Caddy, обязательно остановите его:

<pre><code class="cmd bash">caddy stop</code></pre>

<a id="further-reading"></a>
## Дополнительное чтение

- [Основные понятия Caddyfile](/docs/caddyfile/concepts)
- [Директивы](/docs/caddyfile/directives)
- [Распространенные шаблоны](/docs/caddyfile/patterns)
