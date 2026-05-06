---
title: Convenciones
---

# Convenciones

El ecosistema de Caddy sigue algunas convenciones para mantener la consistencia y la intuición en toda la plataforma.


- [Direcciones de red](#direcciones-de-red)
- [Placeholders](#placeholders)
- [Ubicaciones de archivos](#ubicaciones-de-archivos)
  - [Directorio de datos](#directorio-de-datos)
  - [Directorio de configuración](#directorio-de-configuración)
- [Duraciones](#duraciones)



## Direcciones de red

Al especificar una dirección de red para marcar (`dial`) o enlazar (`bind`), Caddy acepta una cadena con el siguiente formato:

```
network/address
```

La parte de red es opcional (por defecto `tcp`) y puede ser cualquier valor que reconozca la función [`net.Dial`](https://pkg.go.dev/net#Dial) de Go. Si se especifica una red, debe separarse de la dirección con una sola barra `/`.

La red puede ser una de las siguientes; las que terminan en `4` o `6` son solo IPv4 o IPv6 respectivamente:

- TCP: `tcp`, `tcp4`, `tcp6`
- UDP: `udp`, `udp4`, `udp6`
- IP: `ip`, `ip4`, `ip6`
- Unix: `unix`, `unixgram`, `unixpacket`

La parte de dirección puede tener cualquiera de estas formas:

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/path/to/unix/socket`
- `/path/to/unix/socket|0200`

`host` puede ser cualquier hostname, nombre de dominio resoluble o dirección IP.

En el caso de direcciones IPv6, la dirección debe ir entre corchetes `[]`. El identificador de zona (que empieza con `%`) es opcional (suele usarse para direcciones link-local).

El puerto puede ser un único valor (`:8080`) o un rango inclusivo (`:8080-8085`). Un rango de puertos se descompone en direcciones individuales. No todos los campos de configuración aceptan rangos de puerto. El puerto especial `:0` significa cualquier puerto disponible.

Una ruta de socket unix solo se acepta cuando se usa un tipo de red `unix*`. La barra que separa la red y la dirección no se considera parte de la ruta.

Cuando se usa un socket unix como dirección de bind, puedes especificar opcionalmente un modo de permisos tras la ruta, separado por una barra vertical `|`. El valor predeterminado es `0200` (octal), es decir `u=w,g=,o=` (simbólico). El `0` inicial es opcional.

Ejemplos válidos:

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//path/to/socket
unix//path/to/socket|0200
```

<aside class="tip">

Las direcciones de red de Caddy no son URLs. Las URLs combinan capas alta y baja del [modelo OSI <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OSI_model#Layer_architecture), pero Caddy suele usar direcciones de red independientemente de una aplicación específica, por lo que combinarlas sería problemático. En Caddy, las direcciones de red se refieren precisamente a recursos que se pueden dialear o enlazar en L3-L5, mientras que las URLs combinan L3-L7, que son demasiadas. Una dirección de red requiere que host+puerto y ruta sean mutuamente excluyentes, pero en URLs no siempre ocurre. Las direcciones de red a veces admiten rangos de puertos, pero las URLs no.

</aside>




## Placeholders

La configuración de Caddy admite el uso de _placeholders_. Usar placeholders es una forma simple de inyectar valores dinámicos en una configuración estática.

<aside class="tip">

Los placeholders son una idea similar a las variables en otros software. Por ejemplo, [nginx tiene variables <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html) como `$uri` y `$document_root`, mientras que el equivalente de Caddy sería [`{http.request.uri}`](/docs/json/apps/http/#docs) y [`{http.vars.root}`](/docs/caddyfile/directives/root).

</aside>


Los placeholders se delimitan por llaves `{ }` y contienen el identificador dentro, por ejemplo: `{foo.bar}`. La llave de apertura del placeholder puede escaparse como `\{como.esto}` para evitar la sustitución. Los identificadores de placeholders suelen usar namespaces con puntos para evitar colisiones entre módulos.

Qué placeholders están disponibles depende del contexto. No todos están disponibles en todas las partes de la configuración. Por ejemplo, [la app HTTP establece placeholders](/docs/json/apps/http/#docs) que solo están disponibles en áreas de configuración relacionadas con el manejo de solicitudes HTTP. Cuando una solicitud pasa por el handler [`reverse_proxy`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs), el handler establece varios placeholders específicos de proxy. Esos placeholders se pueden referenciar durante el proxy y también después (en `handle_response`), por ejemplo al configurar encabezados de respuesta o enriquecer access logs.

Los siguientes placeholders están siempre disponibles (globales):

Placeholder | Descripción
------------|-------------
`{env.*}` | Variable de entorno; ejemplo: `{env.HOME}`
`{file.*}` | Contenidos desde un archivo; ejemplo: `{file./path/to/secret.txt}`
`{system.hostname}` | El hostname local del sistema
`{system.slash}` | El separador de ruta del sistema de archivos
`{system.os}` | El sistema operativo del sistema
`{system.arch}` | La arquitectura del sistema
`{system.wd}` | El directorio de trabajo actual
`{time.now}` | El tiempo actual como struct `time` de Go
`{time.now.http}` | El tiempo actual en el formato usado en [HTTP headers <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified)
`{time.now.unix}` | El tiempo actual como timestamp Unix en segundos
`{time.now.unix_ms}` | El tiempo actual como timestamp Unix en milisegundos
`{time.now.common_log}` | El tiempo actual en Common Log Format
`{time.now.year}` | El año actual en formato YYYY

No todos los campos de configuración admiten placeholders, pero la mayoría sí donde se esperaría. El soporte para placeholders debe haberse agregado explícitamente a esos campos. Los autores de plugins pueden [leer este artículo](/docs/extending-caddy/placeholders) para aprender cómo agregar soporte de placeholders en sus módulos.



## Ubicaciones de archivos

Esta sección contiene información sobre dónde encontrar varios archivos. Las rutas de archivo y directorio descritas aquí son como máximo valores predeterminados; algunas pueden anularse.

### Tus archivos de configuración
<a id="your-config-files"></a>

No existe un lugar único y convencional para poner tus archivos de configuración. Ponlos donde tenga más sentido para ti.

<aside class="tip">

La única excepción podría ser un archivo llamado `Caddyfile` en el directorio de trabajo actual, que el comando caddy busca por conveniencia si no se especifica ningún otro archivo de configuración.

</aside>


Las distribuciones que se envían con un archivo de configuración predeterminado deberían documentar dónde está ese archivo, incluso si puede resultar obvio para los mantenedores del paquete o distro. Para la mayoría de instalaciones Linux, el Caddyfile se encuentra en `/etc/caddy/Caddyfile`.


### Directorio de datos

Caddy guarda certificados TLS y otros activos importantes en un directorio de datos, respaldado por [el módulo de almacenamiento configurado](/docs/json/storage/) (por defecto: sistema de archivos local).

Si la variable de entorno `XDG_DATA_HOME` está configurada, es `$XDG_DATA_HOME/caddy`.

En caso contrario, su ruta varía por plataforma y sigue convenciones del SO:

SO | Ruta del directorio de datos
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (o `/sdcard/caddy`)

Todas las demás OS usan la ruta de Linux/BSD.

**El directorio de datos no debe tratarse como caché.** Su contenido **no** es efímero ni solo para rendimiento. Caddy almacena certificados TLS, claves privadas, OCSP staples y otra información necesaria en el directorio de datos. No debe limpiarse sin entender las implicaciones.

Es crucial que este directorio sea persistente y escribible por Caddy.


### Directorio de configuración
<a id="directorio-de-configuración"></a>

Aquí es donde Caddy puede guardar cierta configuración en disco. Principalmente, persiste la última configuración activa (de forma predeterminada) en esta carpeta para poder reanudar fácilmente más tarde usando [`caddy run --resume`](/docs/command-line#caddy-run).

<aside class="tip">

El directorio de configuración *no* es donde debes guardar [tus archivos de configuración](#your-config-files). (Aunque puedes hacerlo.)

</aside>


Si la variable de entorno `XDG_CONFIG_HOME` está configurada, es `$XDG_CONFIG_HOME/caddy`.

De lo contrario, su ruta varía por plataforma y sigue convenciones del OS:


SO | Ruta del directorio de configuración
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

Todas las demás OS usan la ruta de Linux/BSD.

Es crucial que este directorio sea persistente y escribible por Caddy.


## Duraciones

Las cadenas de duración se usan comúnmente en la configuración de Caddy. Tienen el mismo formato que la sintaxis de [`time.ParseDuration` de Go](https://golang.org/pkg/time/#ParseDuration), salvo que también puedes usar `d` para días (asumimos que 1 día = 24 horas por simplicidad). Las unidades válidas son:

- `ns` (nanosegundo)
- `us`/`µs` (microsegundo)
- `ms` (milisegundo)
- `s` (segundo)
- `m` (minuto)
- `h` (hora)
- `d` (día)

Ejemplos:

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

En la [configuración JSON](/docs/json/), los valores de duración también pueden ser enteros, que representan nanosegundos.
