---
title: Mantener Caddy en ejecución
---

# Mantener Caddy en ejecución

Aunque Caddy se puede ejecutar directamente con su [interfaz de línea de comandos](/docs/command-line), hay varias ventajas en usar un gestor de servicios para mantenerlo en ejecución, como asegurar que se inicie automáticamente cuando el sistema se reinicia y capturar los registros stdout/stderr.


- [Servicio en Linux](#linux-service)
  - [Archivos de unidad](#unit-files)
  - [Instalación manual](#manual-installation)
  - [Uso del servicio](#using-the-service)
  - [HTTPS local](#local-https-with-systemd)
  - [Sobrescrituras](#overrides)
	- [Variables de entorno](#environment-variables)
	- [`run` y `reload` override](#run-and-reload-override)
	- [Reinicio tras caída](#restart-on-crash)
  - [Consideraciones de SELinux](#selinux-considerations)
- [Servicio de Windows](#windows-service)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [Instalación](#setup)
  - [Uso](#usage)
  - [HTTPS local](#local-https-with-docker)


<a id="linux-service"></a>
## Servicio en Linux

La forma recomendada de ejecutar Caddy en distribuciones Linux con systemd es con nuestros archivos de unidad oficiales de systemd.


### Archivos de unidad
<a id="unit-files"></a>

Proporcionamos dos archivos de unidad de systemd diferentes para que elijas según tu caso de uso:

- [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service) si configuras Caddy con un [Caddyfile](/docs/caddyfile). Si prefieres usar un adaptador de configuración diferente o un archivo JSON, puedes [sobrescribir](#overrides) las directivas `ExecStart` y `ExecReload`.

- [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service) si configuras Caddy únicamente a través de su [API](/docs/api). Este servicio usa la opción [`--resume`](/docs/command-line#caddy-run) para iniciar Caddy usando `autosave.json`, que se [persiste](/docs/json/admin/config/) por defecto.

Son muy similares, pero difieren en las directivas `ExecStart` y `ExecReload` para adaptarse a los flujos de trabajo.

Si necesitas cambiar entre servicios, debes deshabilitar y detener el anterior antes de habilitar e iniciar el otro. Por ejemplo, para cambiar del servicio `caddy` al `caddy-api`:
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>


### Instalación manual
<a id="manual-installation"></a>

Algunos [métodos de instalación](/docs/install) configuran automáticamente Caddy para que se ejecute como servicio. Si elegiste un método que no lo hizo, puedes seguir estas instrucciones:

**Requisitos:**

- Binario `caddy` que hayas [descargado](/download) o [compilado desde fuente](/docs/build)
- `systemctl --version` 232 o superior
- privilegios `sudo`

Mueve el binario de caddy a tu `$PATH`, por ejemplo:
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

Comprueba que funcionó:
<pre><code class="cmd bash">caddy version</code></pre>

Crea un grupo llamado `caddy`:
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

Crea un usuario llamado `caddy` con un directorio home escribible:
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

Si usas un archivo de configuración, asegúrate de que sea legible por el usuario `caddy` que acabas de crear.

A continuación, [elige un archivo de unidad de systemd](#unit-files) según tu caso de uso.

**Revisa cuidadosamente las directivas `ExecStart` y `ExecReload`.** Asegúrate de que la ruta del binario y los argumentos de la línea de comandos sean correctos para tu instalación. Por ejemplo: si usas un archivo de configuración, cambia tu ruta `--config` si difiere de los valores predeterminados.

El lugar habitual para guardar el archivo de servicio es: `/etc/systemd/system/caddy.service`

Después de guardar tu archivo de servicio, puedes iniciar el servicio por primera vez con el flujo habitual de systemctl:

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

Verifica que esté en ejecución:
<pre><code class="cmd bash">systemctl status caddy</code></pre>

Ahora estás listo para [usar el servicio](#using-the-service)!



### Uso del servicio
<a id="using-the-service"></a>

Si usas un Caddyfile, puedes editar tu configuración con `nano`, `vi` o tu editor preferido:
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

Puedes colocar los archivos de tu sitio estático en `/var/www/html` o `/srv`. Asegúrate de que el usuario `caddy` tenga permiso para leer los archivos.

Para verificar que el servicio se está ejecutando:
<pre><code class="cmd bash">systemctl status caddy</code></pre>
El comando de estado también mostrará la ubicación del archivo de servicio actualmente en ejecución.

Cuando se ejecuta con nuestro archivo de servicio oficial, la salida de Caddy se redirige a `journalctl`. Para leer todos tus logs y evitar truncados:
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

Si usas un archivo de configuración, puedes recargar Caddy de forma ordenada tras realizar cambios:
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

Puedes detener el servicio con:
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

No detengas el servicio para cambiar la configuración de Caddy. Parar el servidor genera tiempo de inactividad. Usa el comando de recarga en su lugar.

</aside>

El proceso de Caddy se ejecutará como usuario `caddy`, cuyo `$HOME` es `/var/lib/caddy`. Esto significa que:
- La ubicación de [almacenamiento de datos](/docs/conventions#data-directory) predeterminada (para certificados y otra información de estado) estará en `/var/lib/caddy/.local/share/caddy`.
- La ubicación de [almacenamiento de configuración](/docs/conventions#configuration-directory) predeterminada (para la configuración JSON autoguardada, útil principalmente para el servicio `caddy-api`) estará en `/var/lib/caddy/.config/caddy`.


### HTTPS local con systemd
<a id="local-https-with-systemd"></a>

Cuando usas Caddy para desarrollo local con HTTPS, podrías usar un [hostname](/docs/caddyfile/concepts#addresses) como `localhost` o `app.localhost`. Esto habilita [Local HTTPS](/docs/automatic-https#local-https) usando la CA local de Caddy para emitir certificados.

Como Caddy se ejecuta como usuario `caddy` al correr como servicio, no tendrá permisos para instalar su certificado CA raíz en el almacén de confianza del sistema. Para hacerlo, ejecuta [`sudo caddy trust`](/docs/command-line#caddy-trust) para realizar la instalación.

Si quieres que otros dispositivos se conecten a tu servidor al usar el emisor [`internal`](/docs/caddyfile/directives/tls#internal), también necesitarás instalar el certificado CA raíz en esos dispositivos. Puedes encontrar el certificado raíz en `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt`. Muchos navegadores web usan hoy su propio almacén de confianza (ignorando el sistema), así que quizá también debas instalar el certificado manualmente allí.


### Sobrescrituras
<a id="overrides"></a>

La mejor forma de sobrescribir aspectos de los archivos de servicio es con este comando:
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

Esto abre un archivo en blanco con el editor de texto de tu terminal por defecto, donde puedes sobrescribir o añadir directivas a la definición de la unidad. A esto se le llama archivo "drop-in".

#### Variables de entorno
<a id="environment-variables"></a>

Si necesitas definir variables de entorno para tu configuración, puedes hacerlo así:
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

Del mismo modo, si prefieres mantener un archivo separado para las variables de entorno (*envfile*), puedes usar la directiva [`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) así:
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

Entonces tu archivo `/etc/caddy/.env` podría verse así (no uses comillas `"` alrededor de los valores):

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

#### `run` y `reload` override

<a id="run-and-reload-override"></a>
Si necesitas cambiar el archivo de configuración del valor predeterminado de Caddyfile a un archivo JSON (ten en cuenta que las directivas `Exec*` [deben reiniciarse con cadenas vacías](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=) antes de definir un nuevo valor):
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

#### Reinicio tras caída
<a id="restart-on-crash"></a>

Si quieres que caddy se reinicie solo tras 5s si alguna vez cae inesperadamente:
```systemd
[Service]
# Reinicia caddy automáticamente si se cae, excepto si el código de salida es 1
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

Luego guarda el archivo y sale del editor, y reinicia el servicio para que surta efecto:
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>



### Consideraciones de SELinux
<a id="selinux-considerations"></a>

En sistemas con SELinux habilitado tienes dos opciones:
1. Instalar Caddy usando el [repositorio COPR](/docs/install#fedora-redhat-centos). Tu archivo systemd y el binario de Caddy ya estarán creados y etiquetados correctamente (de modo que puedes ignorar esta sección). Si quieres usar una compilación personalizada de Caddy, necesitarás etiquetar el ejecutable como se describe abajo.

2. [Descargar Caddy desde este sitio](/download) o compilarlo con [`xcaddy`](https://github.com/caddyserver/xcaddy). En ambos casos tendrás que etiquetar los archivos tú mismo.

Los archivos de unidad systemd y sus ejecutables no se ejecutarán a menos que estén etiquetados con `systemd_unit_file_t` y `bin_t`, respectivamente.

La etiqueta `systemd_unit_file_t` se aplica automáticamente a los archivos creados en `/etc/systemd/...`, así que asegúrate de crear tu archivo `caddy.service` ahí, tal como indican las instrucciones de [instalación manual](#manual-installation).

Para etiquetar el binario `caddy`, puedes usar:
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

<a id="windows-service"></a>
## Servicio de Windows

Hay dos formas de ejecutar Caddy como servicio en Windows: [sc.exe](#scexe) o [WinSW](#winsw).

### sc.exe
<a id="scexe"></a>

Para crear el servicio, ejecuta:

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "YOURPATH\caddy.exe run"</code></pre>

(reemplaza `YOURPATH` con la ruta real de tu `caddy.exe`)

Para iniciar:

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

Para detener:

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>


### WinSW
<a id="winsw"></a>

Instala Caddy como servicio en Windows con estas instrucciones.

**Requisitos:**

- Binario `caddy.exe` que hayas [descargado](/download) o [compilado desde fuente](/docs/build)
- Cualquier `.exe` de la última versión de
  [WinSW](https://github.com/winsw/winsw/releases/latest) servicio wrapper (la configuración abajo está escrita para lanzamientos v2.x)

Pon todos los archivos en un directorio de servicio. En los siguientes ejemplos usamos `C:\caddy`.

Renombra el archivo `WinSW-x64.exe` como `caddy-service.exe`.

Añade un `caddy-service.xml` en el mismo directorio:

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

Ahora puedes instalar el servicio usando:
<pre><code class="cmd bash">caddy-service install</code></pre>

Tal vez quieras iniciar la consola de Servicios de Windows para ver si el servicio se ejecuta correctamente:
<pre><code class="cmd bash">services.msc</code></pre>

Ten en cuenta que los servicios de Windows no se pueden recargar, así que debes indicarle a caddy recargar directamente:
<pre><code class="cmd bash">caddy reload</code></pre>

Se puede reiniciar con los comandos normales de servicios de Windows, por ejemplo desde la pestaña "Services" del Administrador de tareas.

Para personalizar el wrapper del servicio, consulta la [documentación de WinSW](https://github.com/winsw/winsw/tree/master#usage)


<a id="docker-compose"></a>
## Docker Compose

La forma más sencilla de iniciar con Docker es usar Docker Compose. Consulta la documentación de [Docker Hub](https://hub.docker.com/_/caddy) para más detalles sobre la imagen oficial de Caddy.

<aside class="tip">

Esto asume que estás usando [Docker Compose V2](https://docs.docker.com/compose/reference/), donde el comando ahora es `docker compose` (con espacio), en lugar de `docker-compose` (con guion) de la V1.

</aside>

### Configuración
<a id="setup"></a>

Primero, crea un archivo `compose.yml` (o añade este servicio a tu archivo existente):

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

Asegúrate de completar `<version>` con el número de versión más reciente, que puedes ver en [Docker Hub](https://hub.docker.com/_/caddy) en la sección "Tags".

Qué hace esto:

- Usa la política de reinicio `unless-stopped` para asegurarse de que el contenedor de Caddy se reinicie automáticamente cuando la máquina se reinicie.
- Enlaza los puertos `80` y `443` para HTTP y HTTPS respectivamente, además de `443/udp` para HTTP/3.
- Monta el directorio `conf` que contiene la configuración de tu Caddyfile.
- Monta el directorio `site` para servir archivos estáticos de tu sitio desde `/srv`.
- Volúmenes con nombre para `/data` y `/config` para [persistir información importante](/docs/conventions#file-locations).

Luego, crea un archivo `Caddyfile` como único archivo en el directorio `conf`, y escribe tu configuración de [Caddyfile](/docs/caddyfile/concepts).

Si tienes archivos estáticos para servir, puedes colocarlos en un directorio `site/` junto a las configuraciones, y luego configurar [`root`](/docs/caddyfile/directives/root) usando `root /srv`. Si no tienes, puedes quitar el volumen montado de `/srv`.

<aside class="tip">

Si usas Caddy para hacer [reverse proxy](/docs/caddyfile/directives/reverse_proxy) a otro contenedor, recuerda que en la red de Docker, `localhost` significa "este contenedor", no "esta máquina". Por ejemplo, no uses `reverse_proxy localhost:8080`; usa `reverse_proxy other-container:8080`

</aside>

Si necesitas una compilación personalizada de Caddy con plugins, sigue las [instrucciones de compilación de Docker](/docs/build#docker) para crear una imagen personalizada. Crea el `Dockerfile` junto a tu `compose.yml`, y luego reemplaza la línea `image:` en tu `compose.yml` por `build: .`.



### Uso
<a id="usage"></a>

Luego, puedes iniciar el contenedor:
<pre><code class="cmd bash">docker compose up -d</code></pre>

Para recargar Caddy tras cambios en tu Caddyfile:
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

Desde v2.11.0, puedes recargar usando `SIGUSR1`, siempre que Caddy se haya iniciado con `caddy run` y un archivo de configuración:
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

Para ver los 1000 registros más recientes de Caddy, y usar `f` para seguir viendo los nuevos en tiempo real:
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

### HTTPS local con Docker
<a id="local-https-with-docker"></a>

Cuando usas Docker para desarrollo local con HTTPS, podrías usar un [hostname](/docs/caddyfile/concepts#addresses) como `localhost` o `app.localhost`. Esto habilita [Local HTTPS](/docs/automatic-https#local-https) usando la CA local de Caddy para emitir certificados. Esto significa que clientes HTTP fuera del contenedor no confiarán en el certificado TLS servido por Caddy. Para solucionarlo, puedes instalar el certificado raíz de Caddy en el almacén de confianza de tu máquina host:

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

Muchos navegadores web usan hoy su propio almacén de confianza (ignorando el almacén del sistema), así que también puede que necesites instalar el certificado manualmente allí, usando el archivo `root.crt` copiado del contenedor en el comando anterior.

- Para Firefox, ve a Preferencias > Privacidad y seguridad > Certificados > Ver certificados > Authorities > Importar, y selecciona el archivo `root.crt`.

- Para Chrome, ve a Configuración > Privacidad y seguridad > Seguridad > Administrar certificados > Authorities > Importar, y selecciona el archivo `root.crt`.
