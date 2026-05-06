---
title: "Сборка из исходного кода"
---

<a id="build-from-source"></a>
# Сборка из исходного кода

Есть несколько вариантов сборки Caddy, если вам нужна customized build (например, с plugins):
- [Git](#git): сборка из Git repo
- [`xcaddy`](#xcaddy): сборка с помощью `xcaddy`
- [Docker](#docker): сборка собственного Docker image

Требования:

- [Go](https://golang.org/doc/install) 1.20 или новее

Раздел [Package Support Files](#package-support-files-for-custom-builds-for-debianubunturaspbian) содержит инструкции для пользователей, которые установили Caddy командой APT на Debian-derived system, но для своих задач нуждаются в executable из custom build.



## Git

Требования:

- Установленный Go (см. выше)

Клонируйте repository:

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

Если у вас нет git, можно скачать source code как file archive [с GitHub](https://github.com/caddyserver/caddy). У каждого [release](https://github.com/caddyserver/caddy/releases) также есть source snapshots.

Сборка:

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>


<aside class="tip">

Из-за [ошибки в Go](https://github.com/golang/go/issues/29228) эти базовые шаги не встраивают информацию о версии. Если вам нужна версия (`caddy version`), нужно компилировать Caddy как dependency, а не как main module. Инструкции для этого находятся в файле [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) Caddy. Либо можно использовать [`xcaddy`](#xcaddy), который автоматизирует это.

</aside>

Программы на Go легко компилировать для других платформ. Просто задайте отличающиеся environment variables `GOOS`, `GOARCH` и/или `GOARM`. ([Подробности смотрите в документации Go.](https://golang.org/doc/install/source#environment))

Например, чтобы скомпилировать Caddy для Windows, находясь не в Windows:

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

Или аналогично для Linux ARMv6, если вы не на Linux или не на ARMv6:

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



## xcaddy

Команда [`xcaddy`](https://github.com/caddyserver/xcaddy) — самый простой способ собрать Caddy с информацией о версии и/или plugins.

Требования:

- Установленный Go (см. выше)
- Убедитесь, что [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) находится в вашем `PATH`

Вам **не** нужно скачивать source code Caddy (он сделает это за вас).

После этого собрать Caddy (с информацией о версии) так же просто, как:

<pre><code class="cmd bash">xcaddy build</code></pre>

Чтобы собрать с plugins, используйте `--with`:

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter
	--with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

Как видите, версии plugins можно настраивать синтаксисом `@`. Версиями могут быть tag name, commit SHA или branch.

Cross-platform compilation с `xcaddy` работает так же, как с командой `go`. Например, чтобы cross-compile для macOS:

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



## Docker

Можно использовать image `:builder` как shortcut для сборки нового binary Caddy с custom modules:

```Dockerfile
FROM caddy:<version>-builder AS builder

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    xcaddy build \
    --with github.com/caddyserver/nginx-adapter \
    --with github.com/hairyhenderson/caddy-teapot-module@v0.0.3-0

FROM caddy:<version>

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

Для начала обязательно замените `<version>` на последнюю версию Caddy.

Обратите внимание на вторую инструкцию `FROM`: она создает намного меньший image, просто накладывая newly-built binary поверх обычного image `caddy`.

Builder использует `xcaddy`, чтобы собрать Caddy с указанными modules, аналогично процессу, [описанному выше](#xcaddy). Options `--mount=type=cache,target=/go/pkg/mod` и `--mount=type=cache,target=/root/.cache/go-build` используются для cache зависимостей Go modules и build artifacts соответственно, что ускоряет последующие builds. Этот флаг является [функцией Docker](https://docs.docker.com/build/cache/optimize/#use-cache-mounts), а не `xcaddy`.

Для использования Docker Compose смотрите наш рекомендуемый [`compose.yml`](/docs/running#docker-compose) и инструкции по использованию.



<a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>
## Package support files for custom builds for Debian/Ubuntu/Raspbian

Эта процедура предназначена для упрощения запуска custom binaries `caddy` при сохранении support files из пакета `caddy`.

Она позволяет пользователям использовать default configuration, systemd service files и bash-completion из официального пакета.

Требования:
- Установите пакет `caddy` согласно [этим инструкциям](/docs/install#debian-ubuntu-raspbian)
- Соберите свой custom binary `caddy` (см. разделы выше) или [скачайте](/download) custom build
- Ваш custom binary `caddy` должен находиться в текущем каталоге

Процедура:
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

Объяснение:

- `dpkg-divert` переместит binary `/usr/bin/caddy` в `/usr/bin/caddy.default` и установит diversion на случай, если какой-либо package захочет установить файл в это location.

- `update-alternatives` создаст symlink от нужного binary caddy к `/usr/bin/caddy`

- `systemctl restart caddy` остановит default version сервера Caddy и запустит custom one.

Переключаться между custom и default binaries `caddy` можно, выполнив команду ниже и следуя информации на экране. Затем перезапустите service Caddy.

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

Чтобы обновить Caddy после этого, можно выполнить [`caddy upgrade`](/docs/command-line#caddy-upgrade). Она попытается [скачать](/download) build с теми же plugins, что и текущая build, но с последней версией Caddy, затем заменить текущий binary новым.
