---
title: Быстрый старт со статическими файлами
---

<a id="static-files-quick-start"></a>
# Быстрый старт со статическими файлами

Это руководство покажет, как быстро запустить production-ready сервер статических файлов.

**Предварительные требования:**
- Базовые навыки работы с терминалом / командной строкой
- `caddy` в вашем PATH
- Папка с вашим сайтом

---

Есть два простых способа быстро запустить файловый сервер.

<a id="command-line"></a>
## Командная строка

В терминале перейдите в корневой каталог вашего сайта и выполните:

<pre><code class="cmd bash">caddy file-server</code></pre>

Если вы получаете ошибку прав доступа, скорее всего, ваша ОС не разрешает привязку к низким портам, поэтому используйте более высокий порт:

<pre><code class="cmd bash">caddy file-server --listen :2015</code></pre>

Затем откройте [localhost](http://localhost) (или [localhost:2015](http://localhost:2015)) в браузере, чтобы увидеть сайт!

Если у вас нет index-файла, но вы хотите показывать список файлов, используйте параметр `--browse`:

<pre><code class="cmd bash">caddy file-server --browse</code></pre>

Можно использовать другую папку как корень сайта:

<pre><code class="cmd bash">caddy file-server --root ~/mysite</code></pre>



<a id="caddyfile"></a>
## Caddyfile

В корне вашего сайта создайте файл `Caddyfile` с таким содержимым:

```caddy
localhost

file_server
```

Если у вас нет разрешения на привязку к низким портам, замените `localhost` на `localhost:2015` (или другой высокий порт).

Затем из того же каталога выполните:

<pre><code class="cmd bash">caddy run</code></pre>

После этого можно открыть [localhost](https://localhost) (или любой адрес из вашей конфигурации), чтобы увидеть сайт!

У [директивы `file_server`](/docs/caddyfile/directives/file_server) есть дополнительные параметры для настройки сайта. Не забудьте [перезагрузить](/docs/command-line#caddy-reload) Caddy (или остановить и снова запустить его), когда измените Caddyfile!

Если у вас нет index-файла, но вы хотите показывать список файлов, используйте аргумент `browse`:

```caddy
localhost

file_server browse
```

Можно также использовать другую папку как корень сайта:

```caddy
localhost

root /var/www/mysite
file_server
```
