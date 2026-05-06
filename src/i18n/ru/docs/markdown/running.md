---
title: Поддержание работы Caddy
---

<a id="keep-caddy-running"></a>
# Поддержание работы Caddy

Хотя Caddy можно запускать напрямую через его [интерфейс командной строки](/docs/command-line), использование service manager дает множество преимуществ: например, он обеспечивает автоматический запуск при перезагрузке системы и сбор stdout/stderr logs.


- [Linux Service](#linux-service)
  - [Unit Files](#unit-files)
  - [Manual Installation](#manual-installation)
  - [Using the Service](#using-the-service)
  - [Local HTTPS](#local-https-with-systemd)
  - [Overrides](#overrides)
	- [Environment variables](#environment-variables)
	- [`run` and `reload` override](#run-and-reload-override)
	- [Restart on crash](#restart-on-crash)
  - [SELinux Considerations](#selinux-considerations)
- [Windows service](#windows-service)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [Setup](#setup)
  - [Usage](#usage)
  - [Local HTTPS](#local-https-with-docker)


<a id="linux-service"></a>
## Linux Service

Рекомендуемый способ запускать Caddy в Linux distributions с systemd — использовать наши официальные systemd unit files.


<a id="unit-files"></a>
### Unit Files

Мы предоставляем два разных systemd unit files, между которыми можно выбрать в зависимости от вашего use case:

- [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service), если вы настраиваете Caddy с помощью [Caddyfile](/docs/caddyfile). Если вы предпочитаете другой config adapter или JSON config file, можно [override](#overrides) команды `ExecStart` и `ExecReload`.

- [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service), если вы настраиваете Caddy только через его [API](/docs/api). Этот service использует option [`--resume`](/docs/command-line#caddy-run), который запустит Caddy с использованием `autosave.json`, который по умолчанию [persisted](/docs/json/admin/config/).

Они очень похожи, но отличаются командами `ExecStart` и `ExecReload`, чтобы поддерживать разные workflows.

Если нужно переключиться между services, сначала следует disable и stop предыдущий, а затем enable и start другой. Например, чтобы переключиться с service `caddy` на service `caddy-api`:
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>


<a id="manual-installation"></a>
### Manual Installation

Некоторые [способы установки](/docs/install) автоматически настраивают Caddy для запуска как service. Если вы выбрали способ, который этого не сделал, следуйте этим инструкциям:

**Требования:**

- Binary `caddy`, который вы [скачали](/download) или [собрали из исходного кода](/docs/build)
- `systemctl --version` 232 или новее
- Права `sudo`

Переместите binary caddy в ваш `$PATH`, например:
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

Проверьте, что это сработало:
<pre><code class="cmd bash">caddy version</code></pre>

Создайте group с именем `caddy`:
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

Создайте user с именем `caddy` и writeable home directory:
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

Если используется config file, убедитесь, что он readable для только что созданного user `caddy`.

Затем [выберите systemd unit file](#unit-files) на основе вашего use case.

**Дважды проверьте directives `ExecStart` и `ExecReload`.** Убедитесь, что location binary и arguments командной строки правильные для вашей installation! Например: если используется config file, измените path `--config`, если он отличается от defaults.

Обычное место для сохранения service file: `/etc/systemd/system/caddy.service`

После сохранения service file можно впервые запустить service обычной последовательностью systemctl:

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

Проверьте, что он работает:
<pre><code class="cmd bash">systemctl status caddy</code></pre>

Теперь вы готовы [использовать service](#using-the-service)!



<a id="using-the-service"></a>
### Using the Service

Если используется Caddyfile, можно редактировать конфигурацию через `nano`, `vi` или предпочитаемый editor:
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

Статические файлы сайта можно разместить в `/var/www/html` или `/srv`. Убедитесь, что user `caddy` имеет permission читать эти files.

Чтобы проверить, что service работает:
<pre><code class="cmd bash">systemctl status caddy</code></pre>
Команда status также покажет location текущего running service file.

При запуске с нашим официальным service file вывод Caddy будет redirected в `journalctl`. Чтобы прочитать полные logs и избежать обрезания строк:
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

Если используется config file, после изменений можно gracefully reload Caddy:
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

Остановить service можно так:
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

Не останавливайте service для изменения конфигурации Caddy. Остановка server приведет к downtime. Вместо этого используйте команду reload.

</aside>

Процесс Caddy будет работать как user `caddy`, у которого `$HOME` установлен в `/var/lib/caddy`. Это означает:
- Default [data storage location](/docs/conventions#data-directory) (для certificates и другой state information) будет в `/var/lib/caddy/.local/share/caddy`.
- Default [config storage location](/docs/conventions#configuration-directory) (для auto-saved JSON config, в основном полезно для service `caddy-api`) будет в `/var/lib/caddy/.config/caddy`.


<a id="local-https-with-systemd"></a>
### Local HTTPS with systemd

При использовании Caddy для локальной разработки с HTTPS вы можете использовать [hostname](/docs/caddyfile/concepts#addresses) вроде `localhost` или `app.localhost`. Это включает [Local HTTPS](/docs/automatic-https#local-https), используя local CA Caddy для выдачи certificates. 

Поскольку при запуске как service Caddy работает как user `caddy`, у него не будет permission установить root CA certificate в system trust store. Для этого выполните [`sudo caddy trust`](/docs/command-line#caddy-trust), чтобы выполнить installation.

Если вы хотите, чтобы другие devices подключались к вашему server при использовании issuer [`internal`](/docs/caddyfile/directives/tls#internal), нужно установить root CA certificate и на эти devices. Root CA certificate находится по пути `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt`. Многие web browsers теперь используют собственный trust store (игнорируя system trust store), поэтому может понадобиться вручную установить certificate и туда.


<a id="overrides"></a>
### Overrides

Лучший способ override aspects service files — эта команда:
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

Она откроет пустой файл в вашем default terminal text editor, где можно override или add directives в unit definition. Это называется "drop-in" file.

<a id="environment-variables"></a>
#### Environment variables

Если нужно определить environment variables для использования в config, это можно сделать так:
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

Аналогично, если вы предпочитаете поддерживать отдельный file для environment variables (envfile), можно использовать directive [`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) так:
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

Тогда ваш файл `/etc/caddy/.env` может выглядеть так (не используйте quotes `"` вокруг values):

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

<a id="run-and-reload-override"></a>
#### `run` and `reload` override

Если нужно изменить config file с default Caddyfile на JSON file (обратите внимание, что directives `Exec*` [нужно сбрасывать empty strings](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=) перед установкой нового value):
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

<a id="restart-on-crash"></a>
#### Restart on crash

Если вы хотите, чтобы caddy перезапускался через 5s при unexpected crash:
```systemd
[Service]
# Automatically restart caddy if it crashes except if the exit code was 1
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

Затем сохраните file, выйдите из text editor и перезапустите service, чтобы изменения вступили в силу:
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>



<a id="selinux-considerations"></a>
### SELinux Considerations

На системах с включенным SELinux есть два варианта:
1. Установить Caddy через [COPR repo](/docs/install#fedora-redhat-centos). Ваш systemd file и binary caddy уже будут созданы и правильно labelled (поэтому этот раздел можно пропустить). Если вы хотите использовать custom build Caddy, нужно label executable, как описано ниже.

2. [Скачать Caddy с этого сайта](/download) или скомпилировать его с [`xcaddy`](https://github.com/caddyserver/xcaddy). В любом случае вам нужно label files самостоятельно.

Systemd unit files и их executables не будут запускаться, если они не labelled соответственно `systemd_unit_file_t` и `bin_t`.

Label `systemd_unit_file_t` автоматически применяется к файлам, созданным в `/etc/systemd/...`, поэтому обязательно создайте `caddy.service` file там, как указано в инструкциях [manual installation](#manual-installation).

Чтобы tag binary `caddy`, можно использовать такую команду:
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

<a id="windows-service"></a>
## Windows service

Есть два способа запускать Caddy как service в Windows: [sc.exe](#scexe) или [WinSW](#winsw).

<a id="scexe"></a>
### sc.exe

Чтобы создать service, выполните:

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "YOURPATH\caddy.exe run"</code></pre>

(замените `YOURPATH` на реальный path к вашему `caddy.exe`)

Чтобы запустить:

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

Чтобы остановить:

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>


<a id="winsw"></a>
### WinSW

Установите Caddy как service в Windows по этим инструкциям.

**Требования:**

- Binary `caddy.exe`, который вы [скачали](/download) или [собрали из исходного кода](/docs/build)
- Любой `.exe` из последнего release
  [WinSW](https://github.com/winsw/winsw/releases/latest) service wrapper (service config ниже написан для releases v2.x)

Поместите все files в service directory. В следующих примерах мы используем `C:\caddy`.

Переименуйте файл `WinSW-x64.exe` в `caddy-service.exe`.

Добавьте `caddy-service.xml` в тот же directory:

```xml
<service>
  <id>caddy</id>
  <!-- Display name of the service -->
  <name>Caddy Web Server (powered by WinSW)</name>
  <!-- Service description -->
  <description>Caddy Web Server (https://caddyserver.com/)</description>
  <executable>%BASE%\caddy.exe</executable>
  <arguments>run</arguments>
  <log mode="roll-by-time">
    <pattern>yyyy-MM-dd</pattern>
  </log>
</service>
```

Теперь можно установить service:
<pre><code class="cmd bash">caddy-service install</code></pre>

Возможно, стоит открыть Windows Services Console, чтобы увидеть, правильно ли работает service:
<pre><code class="cmd bash">services.msc</code></pre>

Учтите, что Windows services нельзя reload, поэтому нужно сказать caddy напрямую выполнить reload:
<pre><code class="cmd bash">caddy reload</code></pre>

Restart возможен через обычные команды Windows services, например через вкладку "Services" в Task Manager.

Для настройки service wrapper смотрите [документацию WinSW](https://github.com/winsw/winsw/tree/master#usage)


<a id="docker-compose"></a>
## Docker Compose

Самый простой способ быстро начать работу с Docker — использовать Docker Compose. Дополнительные сведения об official Caddy Docker image смотрите в документации на [Docker Hub](https://hub.docker.com/_/caddy).

<aside class="tip">

Здесь предполагается, что вы используете [Docker Compose V2](https://docs.docker.com/compose/reference/), где команда теперь `docker compose` (с пробелом), а не `docker-compose` из V1 (с hyphen).

</aside>

<a id="setup"></a>
### Setup

Сначала создайте файл `compose.yml` (или добавьте этот service в существующий file):

```yaml
services:
  caddy:
    image: caddy:<version>
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./conf:/etc/caddy
      - ./site:/srv
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

Обязательно заполните image `<version>` последним номером версии, который можно найти на [Docker Hub](https://hub.docker.com/_/caddy) в разделе "Tags".

Что это делает:

- Использует restart policy `unless-stopped`, чтобы контейнер Caddy автоматически перезапускался при reboot вашей machine.
- Bind к портам `80` и `443` для HTTP и HTTPS соответственно, плюс `443/udp` для HTTP/3.
- Bind mounts directory `conf`, содержащий вашу конфигурацию Caddyfile.
- Bind mounts directory `site`, чтобы обслуживать статические файлы вашего site из `/srv`.
- Named volumes для `/data` и `/config`, чтобы [persist important information](/docs/conventions#file-locations).

Затем создайте файл с именем `Caddyfile` как единственный file в directory `conf` и напишите вашу config [Caddyfile](/docs/caddyfile/concepts).

Если нужно обслуживать static files, можно разместить их в directory `site/` рядом с configs, а затем задать [`root`](/docs/caddyfile/directives/root) через `root /srv`. Если нет, можно удалить volume mount `/srv`.

<aside class="tip">

Если вы используете Caddy для [reverse proxy](/docs/caddyfile/directives/reverse_proxy) к другому container, помните: в Docker networking `localhost` означает "этот container", а не "эта machine". Поэтому, например, не используйте `reverse_proxy localhost:8080`; вместо этого используйте `reverse_proxy other-container:8080` 

</aside>

Если вам нужна custom build Caddy с plugins, следуйте [инструкциям по Docker build](/docs/build#docker), чтобы создать custom Docker image. Создайте `Dockerfile` рядом с `compose.yml`, затем замените строку `image:` в `compose.yml` на `build: .`.



<a id="usage"></a>
### Usage

Затем можно запустить container:
<pre><code class="cmd bash">docker compose up -d</code></pre>

Чтобы reload Caddy после изменений в Caddyfile:
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

Начиная с v2.11.0, можно выполнить reload с помощью `SIGUSR1`, при условии что Caddy был запущен через `caddy run` и с config file:
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

Чтобы увидеть 1000 последних logs Caddy и `f`ollow новые:
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

<a id="local-https-with-docker"></a>
### Local HTTPS with Docker

При использовании Docker для локальной разработки с HTTPS вы можете использовать [hostname](/docs/caddyfile/concepts#addresses) вроде `localhost` или `app.localhost`. Это включает [Local HTTPS](/docs/automatic-https#local-https), используя local CA Caddy для выдачи certificates. Это означает, что HTTP clients за пределами container не будут доверять TLS certificate, который обслуживает Caddy. Чтобы решить это, можно установить root CA cert Caddy в trust store вашей host machine:

<div x-data="{ os: $persist(defaultOS(['linux', 'mac', 'windows'], 'linux')) }" class="tabs">
<div class="tab-buttons">
	<button x-on:click="os = 'linux'" x-bind:class="{ active: os === 'linux' }">Linux</button>
	<button x-on:click="os = 'mac'" x-bind:class="{ active: os === 'mac' }">Mac</button>
	<button x-on:click="os = 'windows'" x-bind:class="{ active: os === 'windows' }">Windows</button>
</div>

<div x-show="os === 'linux'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /usr/local/share/ca-certificates/root.crt \
  && sudo update-ca-certificates</code></pre>

</div>

<div x-show="os === 'mac'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /tmp/root.crt \
  && sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain /tmp/root.crt</code></pre>

</div>

<div x-show="os === 'windows'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    %TEMP%/root.crt \
  && certutil -addstore -f "ROOT" %TEMP%/root.crt</code></pre>

</div>
</div>

Многие web browsers теперь используют собственный trust store (игнорируя system trust store), поэтому может понадобиться вручную установить certificate и туда, используя файл `root.crt`, скопированный из container командой выше.

- Для Firefox перейдите в Preferences > Privacy & Security > Certificates > View Certificates > Authorities > Import и выберите файл `root.crt`.

- Для Chrome перейдите в Settings > Privacy and security > Security > Manage certificates > Authorities > Import и выберите файл `root.crt`.
