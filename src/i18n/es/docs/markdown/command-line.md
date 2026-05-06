---
title: "Command Line"
---

# Línea de comandos

Caddy tiene una interfaz de línea de comandos estándar similar a Unix. El uso básico es:

```
caddy <command> [<args...>]
```

Los `<carets>` indican parámetros que debes reemplazar con tu entrada.

Los `[brackets]` indican parámetros opcionales. Los `(brackets)` indican parámetros obligatorios.

Las elipsis `...` indican continuación, es decir, uno o más parámetros.

Los `--flags` pueden tener un atajo de una letra como `-f`.

**Inicio rápido: `caddy`, `caddy help`, o `man caddy` (si está instalado)**

---

- **[caddy adapt](#caddy-adapt)**
  Adapta un documento de configuración al JSON nativo

- **[caddy build-info](#caddy-build-info)**
  Imprime la información de compilación

- **[caddy completion](#caddy-completion)**
  Genera scripts de autocompletado de shell

- **[caddy environ](#caddy-environ)**
  Imprime el entorno

- **[caddy file-server](#caddy-file-server)**
  Un servidor de archivos estático simple, listo para producción

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  Comando auxiliar del servidor de archivos para exportar la plantilla de exploración por defecto

- **[caddy fmt](#caddy-fmt)**
  Da formato a un Caddyfile

- **[caddy hash-password](#caddy-hash-password)**
  Genera el hash de una contraseña y lo imprime en base64

- **[caddy help](#caddy-help)**
  Ver ayuda de los comandos de caddy

- **[caddy list-modules](#caddy-list-modules)**
  Lista los módulos instalados de Caddy

- **[caddy manpage](#caddy-manpage)**
  Genera páginas man

- **[caddy reload](#caddy-reload)**
  Cambia la configuración del proceso Caddy en ejecución

- **[caddy respond](#caddy-respond)**
  Servidor HTTP rápido y predefinido, útil para desarrollo y pruebas

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  Un proxy inverso HTTP(S) simple, listo para producción

- **[caddy run](#caddy-run)**
  Inicia el proceso Caddy en primer plano

- **[caddy start](#caddy-start)**
  Inicia el proceso Caddy en segundo plano

- **[caddy stop](#caddy-stop)**
  Detiene el proceso Caddy en ejecución

- **[caddy storage export](#caddy-storage)**
  Exporta el contenido del almacenamiento configurado a un tarball

- **[caddy storage import](#caddy-storage)**
  Importa un tarball exportado previamente al almacenamiento configurado

- **[caddy trust](#caddy-trust)**
  Instala un certificado en el almacén de confianza local

- **[caddy untrust](#caddy-untrust)**
  Quita un certificado del(s) almacén(es) de confianza local

- **[caddy upgrade](#caddy-upgrade)**
  Actualiza Caddy a la última versión

- **[caddy add-package](#caddy-add-package)**
  Actualiza Caddy a la última versión, añadiendo plugins adicionales

- **[caddy remove-package](#caddy-remove-package)**
  Actualiza Caddy a la última versión, quitando algunos plugins

- **[caddy validate](#caddy-validate)**
  Comprueba si un archivo de configuración es válido

- **[caddy version](#caddy-version)**
  Imprime la versión

- **[Signals](#signals)**
  Cómo maneja Caddy las señales

- **[Exit codes](#exit-codes)**
  Se emiten cuando el proceso Caddy sale

## Subcommands


### `caddy adapt`
<a id="caddy-adapt"></a>

<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

Adapta una configuración a la estructura JSON nativa de Caddy y escribe el resultado en stdout, junto con cualquier advertencia en stderr, y luego sale.

`--config` es la ruta del archivo de configuración. Si se omite, asume `Caddyfile` en el directorio actual si existe; de lo contrario, esta opción es obligatoria. Si quieres usar stdin en lugar de un archivo normal, usa - como ruta.

`--adapter` especifica el adaptador de configuración a usar; el valor predeterminado es `caddyfile`.

`--pretty` formatea la salida con sangrías para facilitar la lectura.

`--validate` carga y aprovisiona la configuración adaptada para comprobar su validez (pero no inicia realmente la configuración).

Ten en cuenta que una configuración adaptada con éxito aún puede fallar al validarla. Como ejemplo, usa este Caddyfile:

```caddy
localhost

tls cert_notexist.pem key_notexist.pem
```

Intenta adaptarlo:

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

Funciona sin errores. Luego intenta:

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_notexist.pem: no such file or directory
</code></pre>

Aunque ese Caddyfile puede adaptarse a JSON sin errores, los archivos de certificado y/o clave reales no existen, por lo que la validación falla porque ese error surge en la fase de aprovisionamiento. Por lo tanto, la validación es una comprobación de errores más estricta que la adaptación.

#### Ejemplo

Para adaptar un Caddyfile a JSON que puedas leer y ajustar fácilmente de forma manual:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile --pretty</code></pre>



### `caddy build-info`
<a id="caddy-build-info"></a>

<pre><code class="cmd bash">caddy build-info</code></pre>

Imprime la información proporcionada por Go sobre la compilación (ruta del módulo principal, versiones de paquetes, reemplazos de módulos).



### `caddy completion`
<a id="caddy-completion"></a>

<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

Genera scripts de autocompletado del shell. Esto te permite usar tab-complete o auto-complete (o similar, según el shell) al escribir comandos `caddy`.

Para obtener instrucciones de instalación de este script en tu shell, ejecuta `caddy help completion` o `caddy completion -h`.



### `caddy environ`
<a id="caddy-environ"></a>

<pre><code class="cmd bash">caddy environ</code></pre>

Imprime el entorno tal como lo ve caddy y sale. Puede ser útil al depurar sistemas init o unidades de gestores de procesos como systemd.



### `caddy file-server`
<a id="caddy-file-server"></a>

<pre><code class="cmd bash">caddy file-server
	[-r, --root &lt;path&gt;]
	[--listen &lt;addr&gt;]
	[-d, --domain &lt;example.com&gt;]
	[-b, --browse]
	[--reveal-symlinks]
	[-t, --templates]
	[--access-log]
	[-v, --debug]
	[-f, --file-limit &lt;number&gt;]
	[--no-compress]
	[-p, --precompressed]</code></pre>

Inicia un servidor de archivos estáticos simple pero listo para producción.

`--root` especifica la ruta de la raíz de archivos. El valor predeterminado es el directorio de trabajo actual.

`--listen` acepta una dirección de escucha. El valor predeterminado es `:80`, salvo que se use `--domain`, en cuyo caso el predeterminado será `:443`.

`--domain` solo servirá archivos a través de ese nombre de host, y Caddy intentará servirlos por HTTPS, así que asegúrate de que cualquier DNS público esté configurado correctamente si es un nombre de dominio público. El puerto predeterminado se cambiará a 443.

`--browse` habilita los listados de directorios si se solicita un directorio sin archivo de índice.

`--reveal-symlinks` muestra el objetivo de los enlaces simbólicos en los listados de directorios, cuando `--browse` está habilitado.

`--templates` habilita el renderizado de plantillas.

`--access-log` habilita el registro de solicitudes/acceso.

`--debug` habilita el registro detallado.

`--file-limit` establece el número máximo de archivos mostrados en listados de directorios. Valor predeterminado: `10000`. Si el número de archivos supera este límite, solo se mostrarán los primeros N archivos, donde N es el límite especificado.

`--no-compress` desactiva la compresión. Por defecto, la compresión Zstandard y Gzip está habilitada.

`--precompressed` especifica los formatos de codificación para buscar archivos sidecar precomprimidos. Puede repetirse para varios formatos. Consulta la [directiva file_server](/docs/caddyfile/directives/file_server#precompressed) para más información.

Este comando desactiva la API de administración, lo que facilita ejecutar varias instancias en una máquina local de desarrollo.


#### `caddy file-server export-template`
<a id="caddy-file-server-export-template"></a>

<pre><code class="cmd bash">caddy file-server export-template</code></pre>

Exporta la plantilla de navegación de archivos predeterminada a stdout

### `caddy fmt`
<a id="caddy-fmt"></a>

<pre><code class="cmd bash">caddy fmt [&lt;path&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

Da formato o embellece un Caddyfile, y luego sale. El resultado se imprime en stdout salvo que se use `--overwrite`, y saldrá con código `1` si hay diferencias.

`<path>` especifica la ruta del Caddyfile. Si es `-`, la entrada se lee de stdin. Si se omite, se asume un archivo llamado Caddyfile en el directorio actual.

`--overwrite` hace que el resultado se escriba en el archivo de entrada en vez de imprimirse en terminal. Si la entrada no es un archivo regular, esta opción no tiene efecto.

`--diff` compara la salida con la entrada y marca las líneas con `-` y `+` cuando difieren. Ten en cuenta que las líneas sin cambios se prefijan con dos espacios para alineación y que esto no es un formato de parche válido; solo sirve como herramienta visual.


### `caddy hash-password`
<a id="caddy-hash-password"></a>

<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;password&gt;]
	[-a, --algorithm &lt;name&gt;]</code></pre>
	[--bcrypt-cost &lt;cost&gt;]</code></pre>

Forma conveniente de hacer hash de una contraseña en texto plano. El hash resultante se escribe en stdout en un formato utilizable directamente en la configuración de Caddy.

`--plaintext`
    Contraseña que se desea hashear. Si se omite, se leerá de stdin.
    Si Caddy está conectado a un TTY controlador, la entrada no se mostrará.

`--algorithm`
    Selecciona el algoritmo de hash. Opciones válidas:
      * `argon2id` (recomendado para seguridad moderna)
      * `bcrypt`  (heredado, más lento, costo configurable, costo predeterminado `14`)

Parámetros específicos de bcrypt:

`--bcrypt-cost`
    Define la dificultad de bcrypt. Valores más altos aumentan la seguridad al
    hacer más lenta y exigente en CPU el cálculo del hash.
    Debe estar dentro del rango válido [bcrypt.MinCost, bcrypt.MaxCost].
    Si se omite o es inválido, se usa el costo predeterminado.

Parámetros específicos de Argon2id:

`--argon2id-time`
    Número de iteraciones. Aumentarlo vuelve
    el hash más lento y más resistente a ataques de fuerza bruta.

`--argon2id-memory`
    Cantidad de memoria usada durante el hash.
    Valores más grandes aumentan la resistencia a ataques GPU/ASIC.

`--argon2id-threads`
    Número de hilos CPU a usar. Útil para acelerar en sistemas multinúcleo.

`--argon2id-keylen`
    Longitud del hash resultante en bytes. Claves más largas aumentan
    la seguridad pero incrementan ligeramente el tamaño de almacenamiento.


### `caddy help`
<a id="caddy-help"></a>

<pre><code class="cmd bash">caddy help [&lt;command&gt;]</code></pre>

Imprime el texto de ayuda de la CLI, opcionalmente para un subcomando específico, y luego sale.



### `caddy list-modules`
<a id="caddy-list-modules"></a>

<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

Imprime los módulos de Caddy instalados, opcionalmente con información de paquete y/o versión de sus módulos Go asociados, y luego sale.

En algunos casos por scripts puede ser redundante imprimir también los módulos estándar, por lo que puedes usar `--skip-standard` para omitirlos.

`--json` emite la información del módulo en formato JSON, útil para procesamiento programático.

NOTA: Debido a [un bug en Go](https://github.com/golang/go/issues/29228), la información de versiones solo está disponible si Caddy se construye como dependencia y no como módulo principal. Usa [xcaddy](/docs/build#xcaddy) para facilitar esto.



### `caddy manpage`
<a id="caddy-manpage"></a>

<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;path&gt;)</code></pre>

Genera páginas de manual/documentación para los comandos de Caddy y las escribe en el directorio especificado. La salida de este comando puede leerse con el comando `man`.

`--directory` (obligatorio) es la ruta del directorio en el que se escribirán las páginas. Se creará si no existe.

Una vez generadas, normalmente se deben instalar las páginas de manual. El procedimiento varía según la plataforma, pero en sistemas Linux típicos suele ser así:

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

Luego puedes ejecutar `man caddy` (o `man caddy-*` para subcomandos) para leer la documentación en tu terminal.

Las páginas de manual son documentación separada de la que hay en nuestro sitio web. Nuestro sitio web tiene documentación más completa y se actualiza con mayor frecuencia.



### `caddy reload`
<a id="caddy-reload"></a>

<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

Asigna una nueva configuración a la instancia de Caddy en ejecución. Esto tiene el mismo efecto que hacer POST de un documento al [/load endpoint](/docs/api#post-load), pero este comando resulta más conveniente para flujos simples basados en archivos de configuración. Comparado con los comandos `stop`, `start` y `run`, este único comando es la forma correcta y semánticamente adecuada de cambiar/recargar la configuración en ejecución.

Como este comando usa la API, el endpoint de administración no debe estar deshabilitado.

`--config` es el archivo de configuración a aplicar. Si es `-`, la configuración se lee de stdin. Si no se especifica, intentará con un archivo llamado `Caddyfile` en el directorio de trabajo actual y, si existe, lo adaptará usando el adaptador `caddyfile`; de lo contrario, si no hay archivo de configuración para cargar, es un error.

`--adapter` especifica un adaptador de configuración, si aplica. Esta opción no es necesaria si el nombre de archivo de `--config` empieza con `Caddyfile` o termina con `.caddyfile`, lo que supone el adaptador `caddyfile`. En caso contrario, esta opción es obligatoria si el archivo de configuración proporcionado no está en formato JSON nativo de Caddy.

`--address` debe usarse si el endpoint de administración no escucha en la dirección predeterminada y esta es distinta de la dirección del archivo de configuración proporcionado.

`--force` hará que se recargue incluso si la configuración especificada es la misma que la que Caddy está ejecutando. Puede ser útil para forzar a Caddy a aprovisionar de nuevo sus módulos, lo cual puede tener efectos secundarios, por ejemplo: recargar certificados TLS cargados manualmente.



### `caddy respond`
<a id="caddy-respond"></a>

<pre><code class="cmd bash">caddy respond
	[-s, --status &lt;code&gt;]
	[-H, --header "&lt;Field&gt;: &lt;value&gt;"]
	[-b, --body &lt;content&gt;]
	[-l, --listen &lt;addr&gt;]
	[-v, --debug]
	[--access-log]
	[&lt;status|body&gt;]</code></pre>


Inicia uno o más servidores HTTP codificados directamente, útiles para desarrollo, staging y algunos casos de producción. Puede servir para verificar o depurar clientes HTTP, scripts o incluso balanceadores de carga.

`--status` es el código de estado HTTP a devolver.

`--header` añade un encabezado HTTP; se espera el formato `Field: value`. Esta opción puede usarse varias veces.

`--body` especifica el cuerpo de respuesta. Alternativamente, el cuerpo puede recibirse por stdin.

`--listen` es la dirección de escucha, que puede ser cualquier [dirección de red](/docs/conventions#network-addresses) reconocida por Caddy y puede incluir un rango de puertos para iniciar varios servidores.

`--debug` habilita registro de depuración detallado.

`--access-log` habilita el registro de acceso/solicitudes.

Sin opciones, este comando escucha en un puerto disponible aleatorio y responde a solicitudes HTTP con una respuesta 200 vacía. La dirección de escucha puede personalizarse con la opción `--listen` y siempre se imprimirá en stdout. Si la dirección incluye un rango de puertos, se iniciarán varios servidores.

Si se da un argumento final sin nombre, se tratará como código de estado (igual que la opción `--status`) si es un número de 3 dígitos. De lo contrario, se usa como cuerpo de respuesta (igual que la opción `--body`). Las opciones `--status` y `--body` siempre tienen prioridad sobre este argumento.

Un cuerpo puede proporcionarse en 3 formas: una opción, un argumento final sin nombre, o mediante stdin (si no se usa ninguna opción ni argumento). Se admite una [evaluación de plantillas](https://pkg.go.dev/text/template) limitada en el cuerpo, con estas variables:

Variable | Descripción
---------|-------------
`.N`       | Número del servidor
`.Port`    | Puerto del listener
`.Address` | Dirección del listener


#### Ejemplos

Respuesta 200 vacía en un puerto aleatorio:
<pre><code class="cmd bash">caddy respond</code></pre>

Respuesta HTTP con cuerpo:
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

Múltiples servidores y plantillas:
<pre><code class="cmd"><b>$ caddy respond --listen :2000-2004 "{{printf "I'm server {{.N}} on port {{.Port}}"}}"</b>

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

<b>$ curl 127.0.0.1:2002</b>
I'm server 2 on port 2002</code></pre>

Canaliza una página de mantenimiento:
<pre><code class="cmd bash">cat maintenance.html | caddy respond \
	--listen :80 \
	--status 503 \
	--header "Content-Type: text/html"</code></pre>



### `caddy reverse-proxy`
<a id="caddy-reverse-proxy"></a>

<pre><code class="cmd bash">caddy reverse-proxy
	[-f, --from &lt;addr&gt;]
	(-t, --to &lt;addr&gt;)
	[-H, --header-up "&lt;Field&gt;: &lt;value&gt;"]
	[-d, --header-down "&lt;Field&gt;: &lt;value&gt;"]
	[-c, --change-host-header]
	[-r, --disable-redirects]
	[-i, --internal-certs]
	[-v, --debug]
	[--access-log]
	[--insecure]</code></pre>

Un proxy inverso simple pero listo para producción. Útil para despliegues rápidos, demos y desarrollo.

Simplemente enruta el tráfico HTTP(S) de la dirección `--from` a la dirección `--to`. Puedes especificar múltiples direcciones `--to` repitiendo la opción. Se requiere al menos una dirección `--to`. La dirección `--to` puede tener rango de puertos como atajo para expandir a múltiples servidores upstream.

Salvo que se indique otra cosa en las direcciones, la dirección `--from` se asumirá como HTTPS si se indica un nombre de host, y `--to` se asumirá como HTTP.

Si la dirección `--from` tiene host o IP, Caddy intentará servir el proxy por HTTPS con un certificado (salvo que se anule con el esquema o puerto HTTP).

Si se sirve por HTTPS: 
  - `--disable-redirects` se puede usar para evitar el enlace al puerto HTTP.

  - `--internal-certs` se puede usar para forzar la emisión de certificados mediante la CA interna en vez de intentar emitir un certificado público.

Para proxy:
  - `--header-up` puede usarse para establecer una cabecera de solicitud que se envía al upstream.
  
  - `--header-down` puede usarse para establecer una cabecera de respuesta que se envía de vuelta al cliente.
  
  - `--change-host-header` establece el encabezado Host de la solicitud con la dirección del upstream, en lugar del Host de entrada por defecto.

    Esto es un atajo para `--header-up "Host: {http.reverse_proxy.upstream.hostport}"`
  
  - `--insecure` desactiva la verificación TLS con el upstream. ADVERTENCIA: *ESTO DESHABILITA LA SEGURIDAD AL NO VERIFICAR EL CERTIFICADO DEL UPSTREAM*.
  
  - `--debug` habilita el registro detallado.

Este comando desactiva la API de administración, por lo que es más fácil ejecutar varias instancias en una máquina local de desarrollo.


### `caddy run`
<a id="caddy-run"></a>

<pre><code class="cmd bash">caddy run
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--pidfile &lt;file&gt;]
	[-e, --environ]
	[--envfile &lt;file&gt;]
	[-r, --resume]
	[-w, --watch]</code></pre>

Ejecuta Caddy y bloquea indefinidamente; es decir, modo "daemon".

`--config` especifica un archivo de configuración inicial para cargar y usar de inmediato. Si es `-`, la configuración se lee de stdin. Si no se especifica configuración, Caddy se ejecutará con una configuración en blanco y usará los ajustes predeterminados para los [puntos finales de la API de administración](/docs/api), que se pueden usar para cargarle nueva configuración. Como caso especial, si el directorio de trabajo actual tiene un archivo llamado "Caddyfile" y el adaptador `caddyfile` está conectado (por defecto), ese archivo se cargará y usará para configurar Caddy, incluso sin opciones de línea de comandos.

`--adapter` es el nombre del adaptador de configuración a usar al cargar la configuración inicial, si aplica. Esta opción no es necesaria si el nombre de archivo de `--config` empieza por `Caddyfile` o termina en `.caddyfile`, lo que supone el adaptador `caddyfile`. De lo contrario, esta opción es obligatoria si el archivo de configuración proporcionado no está en el formato JSON nativo de Caddy. Cualquier advertencia se imprimirá en el log, pero ten en cuenta que cualquier adaptación sin errores se usará inmediatamente, incluso si hay advertencias. Si quieres revisar primero el resultado de la adaptación, usa el subcomando [`caddy adapt`](#caddy-adapt).

`--pidfile` escribe el PID en el archivo especificado.

`--environ` imprime el entorno antes de iniciar. Es lo mismo que el comando `caddy environ`, pero no sale después de imprimir.

`--envfile` carga variables de entorno del archivo indicado, en formato `KEY=VALUE`. Se aceptan comentarios que empiecen por `#`; las claves pueden llevar prefijo `export`; los valores pueden ir entre comillas dobles (las comillas internas pueden escaparse); se admiten valores multilinea.

`--resume` usa la última configuración cargada que se guardó automáticamente, sustituyendo la opción `--config` (si está presente). Esta opción garantiza la persistencia de configuración a través de reinicios de máquina o del proceso. Es más útil en despliegues centrados en [API](/docs/api).

`--watch` observará el archivo de configuración y lo recargará automáticamente al cambiar. ⚠️ ¡Esta función solo está pensada para entornos de desarrollo locales!

<aside class="advice">

No detengas el servidor para cambiar configuración mientras esté en producción; eso causará tiempo de inactividad. (Puede parecer obvio, pero recibimos muchas quejas al respecto.) Usa en su lugar el comando [`caddy reload`](#caddy-reload), o envía la señal `SIGUSR1` al proceso, que tiene el mismo efecto que `caddy reload` con la configuración actualmente cargada.

</aside>



### `caddy start`
<a id="caddy-start"></a>

<pre><code class="cmd bash">caddy start
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]
	[--pidfile &lt;file&gt;]
	[-r, --resume]
	[-w, --watch]</code></code></pre>

Igual que [`caddy run`](#caddy-run), pero en segundo plano. Este comando solo se bloquea hasta que el proceso en segundo plano se ejecuta correctamente (o falla al arrancar), y luego retorna.

Nota: la opción `--config` *no* admite `-` para leer la configuración desde stdin.

Se desaconseja usar este comando con servicios del sistema o en Windows. En Windows, el proceso hijo permanece unido al terminal, por lo que cerrar la ventana detendrá Caddy de forma forzada y no siempre es evidente. Considera ejecutar Caddy [como servicio](/docs/running).

Una vez iniciado, puedes usar [`caddy stop`](#caddy-stop) o el endpoint de API `POST /stop` (`/docs/api#post-stop`) para salir del proceso en segundo plano.



### `caddy stop`
<a id="caddy-stop"></a>

<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

<aside class="tip">

Detener (y reiniciar) el servidor es ortogonal a los cambios de configuración. *No uses el comando stop para cambiar configuración en producción, salvo que aceptes tiempo de inactividad.* Usa en su lugar el comando [`caddy reload`](#caddy-reload).

</aside>


Detiene de forma ordenada el proceso Caddy en ejecución (distinto del proceso del comando stop) y provoca su salida. Usa el endpoint [`POST /stop`](/docs/api#post-stop) de la API de administración para realizar un apagado ordenado.

La dirección de esta petición se puede personalizar con la opción `--address` o desde el `--config`, si la API de administración del módulo en ejecución no usa la dirección de escucha predeterminada.

Si quieres detener la configuración actual pero sin salir del proceso, usa [`caddy reload`](#caddy-reload) con una configuración vacía o el endpoint [`DELETE /config/`](/docs/api#delete-configpath).


### `caddy storage`
<a id="caddy-storage"></a>

<i>⚠️ Experimental</i>

Permite la exportación e importación del contenido del almacenamiento de datos configurado de Caddy.

Esto es útil al necesitar migrar de un [módulo de almacenamiento](/docs/json/storage/) a otro, exportando desde el anterior, actualizando tu configuración y luego importando en el nuevo.

El siguiente comando permite copiar el almacenamiento entre módulos distintos en una sola operación, usando configuraciones antigua y nueva, enviando la salida del comando export al comando import.

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">

Ten en cuenta que al usar [almacenamiento en sistema de archivos](/docs/conventions#data-directory), debes ejecutar el comando export como el mismo usuario con el que normalmente se ejecuta Caddy; de lo contrario se puede usar una ubicación de almacenamiento incorrecta.

Por ejemplo, al ejecutar Caddy como [servicio systemd](/docs/running#linux-service), se ejecutará como el usuario `caddy`, así que debes ejecutar los comandos export o import como ese usuario. Esto suele hacerse con `sudo -u caddy <command>`.

</aside>


#### `caddy storage export`

<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;path&gt;
	[-o, --output &lt;path&gt;]</code></pre>

`--config` es el archivo de configuración a cargar. Es obligatorio para conectar el módulo de almacenamiento correcto.

`--output` es el nombre de archivo donde escribir el tarball. Si es `-`, la salida se escribe en stdout.



#### `caddy storage import`

<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;path&gt;
	-i, --input &lt;path&gt;</code></pre>

`--config` es el archivo de configuración a cargar. Es obligatorio para conectar el módulo de almacenamiento correcto.

`--input` es el nombre del archivo tarball de origen. Si es `-`, la entrada se lee de stdin.


### `caddy trust`
<a id="caddy-trust"></a>

<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Instala un certificado raíz para una CA gestionada por la [app PKI](/docs/json/apps/pki/) de Caddy en los almacenes de confianza locales.

Caddy intenta instalar sus certificados raíz en los almacenes de confianza locales automáticamente cuando se generan por primera vez, pero podría fallar si Caddy no tiene permisos adecuados para escribir en el almacén de confianza. Este comando es necesario para preinstalar los certificados antes de usarlos si el proceso del servidor se ejecuta como usuario sin privilegios (como en systemd). Puede que necesites ejecutarlo con `sudo` en sistemas Unix.

Por defecto, este comando instala el certificado raíz de la CA predeterminada de Caddy (es decir, "local"). Puedes especificar el ID de otra CA con la opción `--ca`.

Este comando intentará conectarse a la [API de administración](/docs/api) de Caddy para obtener el certificado raíz, usando el endpoint [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates). También puedes especificar explícitamente `--address`, o usar `--config` para cargar la dirección administrativa desde tu configuración, si la API de administración del proceso en ejecución no usa la dirección de escucha predeterminada.

También puedes usar el binario `caddy` con este comando para instalar certificados en otras máquinas de tu red, si la API de administración es accesible a otras máquinas; ten cuidado al hacerlo para no exponer la API a clientes no confiables.


### `caddy untrust`
<a id="caddy-untrust"></a>

<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;path&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Quita la confianza de un certificado raíz de los almacenes de confianza locales.

Este comando desinstala la confianza; no elimina necesariamente el certificado raíz de los almacenes por completo. Por eso, confiar y desconfiar repetidamente de certificados nuevos puede llenar las bases de datos de confianza.

Este comando no borra ni modifica los archivos de certificado del almacenamiento configurado de Caddy.

Este comando puede usarse de dos formas:
- Especificando una ruta directa al certificado raíz a quitar con la opción `--cert`.
- Obteniendo el certificado raíz desde la [API de administración](/docs/api) usando el endpoint [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates). Este es el comportamiento por defecto si no se dan opciones.

Si se usa la API de administración, el ID de CA predeterminado es "local". Puedes especificar el ID de otra CA con `--ca`. También puedes especificar explícitamente `--address`, o usar `--config` para cargar la dirección administrativa desde tu configuración si la API de administración del proceso en ejecución no usa la dirección de escucha predeterminada.


### `caddy upgrade`
<a id="caddy-upgrade"></a>

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

Reemplaza el binario actual de Caddy por la última versión desde [nuestra página de descarga](/download) con los mismos módulos instalados, incluyendo todos los plugins de terceros registrados en el sitio web de Caddy.

Las actualizaciones no interrumpen los servidores en ejecución; actualmente, el comando solo reemplaza el binario en disco. Esto puede cambiar en el futuro si encontramos una forma adecuada de hacerlo.

El proceso de actualización es tolerante a fallos: primero se hace respaldo del binario actual (copiado junto al actual) y se restaura automáticamente si algo sale mal. Si deseas conservar la copia de respaldo al terminar, usa la opción `--keep-backup`.

Este comando puede requerir privilegios elevados si tu usuario no tiene permisos de escritura sobre el archivo ejecutable.


### `caddy add-package`
<a id="caddy-add-package"></a>

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy add-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

Al igual que `caddy upgrade`, reemplaza el binario actual de Caddy por la última versión con los mismos módulos instalados, _más_ los paquetes listados como argumentos incluidos en el nuevo binario. Consulta la lista de paquetes que puedes instalar en [nuestra página de descarga](/download). Cada argumento debe ser el nombre completo del paquete.

Por ejemplo:

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>



### `caddy remove-package`
<a id="caddy-remove-package"></a>

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy remove-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

Al igual que `caddy upgrade`, reemplaza el binario actual de Caddy por la última versión con los mismos módulos instalados, pero _sin_ los paquetes listados en los argumentos si estaban presentes en el binario actual. Ejecuta `caddy list-modules --packages` para ver la lista de nombres de paquetes de módulos no estándar incluidos en el binario actual.



### `caddy validate`
<a id="caddy-validate"></a>

<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]</code></pre>

Valida un archivo de configuración y luego sale. Este comando deserializa la configuración, luego carga y aprovisiona todos sus módulos como si fuera a iniciar la configuración, pero la configuración no se inicia realmente. Esto expone errores en una configuración que surgen durante las fases de carga o aprovisionamiento y es una comprobación de errores más estricta que simplemente serializar una configuración como JSON.

`--config` es el archivo de configuración a validar. Si es `-`, la configuración se lee de stdin. Si existe, el predeterminado es el `Caddyfile` del directorio actual.

`--adapter` es el nombre del adaptador de configuración a usar. Esta opción no es necesaria si el nombre del archivo `--config` empieza con `Caddyfile` o termina con `.caddyfile`, lo que supone el adaptador `caddyfile`. De lo contrario, esta opción es obligatoria si el archivo de configuración proporcionado no está en formato JSON nativo.

`--envfile` carga variables de entorno del archivo especificado, en formato `KEY=VALUE`. Se admiten comentarios que empiecen con `#`; las claves pueden llevar prefijo `export`; los valores pueden ir entre comillas dobles (las comillas dobles internas se pueden escapar); se admiten valores multilinea.



### `caddy version`
<a id="caddy-version"></a>
<pre><code class="cmd bash">caddy version</code></pre>

Imprime la versión y sale.



## Signals
<a id="signals"></a>

Caddy intercepta ciertas señales y ignora otras. Las señales pueden iniciar comportamientos específicos del proceso.

Señal | Comportamiento
-------|----------
`SIGINT` | Salida ordenada. Envía la señal otra vez para forzar la salida inmediata.
`SIGQUIT` | Cierra Caddy inmediatamente, pero aún limpia bloqueos en el almacenamiento porque es importante.
`SIGTERM` | Salida ordenada.
`SIGUSR1` | Recarga la configuración, pero solo si se inició con `caddy run` (sin `--resume`) y no se han realizado cambios de configuración vía [la API](/docs/api) (incluido [`caddy reload`]#caddy-reload)).
`SIGUSR2` | Ignorada.
`SIGHUP` | Ignorada.

Una salida ordenada significa que ya no se aceptan conexiones nuevas y las conexiones existentes se vacían antes de cerrar el socket. Puede aplicarse (y ser configurable) un período de gracia. Cuando finaliza el período de gracia, las conexiones se terminan de forma forzada. Los bloqueos en el almacenamiento y otros recursos que módulos individuales necesitan liberar se limpian durante un apagado ordenado.

Cuando se recibe una señal para recargar configuración (`SIGUSR1`), actúa como una recarga forzada de configuración (es decir, recarga de todas formas aunque el texto de configuración no haya cambiado), lo que puede recargar archivos dependientes como certificados TLS desde disco.

Las recargas de configuración basadas en señales solo están habilitadas si Caddy se inicia con `caddy run` con un archivo de configuración. Se deshabilitan (ignorando señales, con una advertencia en el log) si Caddy se inicia con `--resume` (ya que implica un flujo API), o si se recibe cualquier cambio de configuración por la API de administración, o si se ejecuta `caddy reload` con un nombre de archivo o adaptador de configuración _diferente_ al usado originalmente al arrancar. Esto evita conflictos entre métodos de recarga.



## Exit codes
<a id="exit-codes"></a>

Caddy devuelve un código al salir el proceso:

Código | Significado
-----|---------
`0` | Salida normal.
`1` | Error de inicio. *No reinicies el proceso automáticamente; probablemente volverá a fallar a menos que se hagan cambios.*
`2` | Salida forzada. Caddy fue obligado a salir sin limpiar recursos.
`3` | Salida fallida. Caddy salió con errores durante la limpieza.

En bash, puedes obtener el código de salida del último comando con `echo $?.`
