---
title: "Compilar desde el código fuente"
---

# Compilar desde el código fuente

Hay varias opciones para compilar Caddy si necesitas una versión personalizada (por ejemplo, con plugins):
- [Git](#git): Compilar desde el repositorio de Git
- [`xcaddy`](#xcaddy): Compilar con `xcaddy`
- [Docker](#docker): Compilar una imagen personalizada de Docker

Requisitos:

- [Go](https://golang.org/doc/install) 1.20 o posterior

La sección [Archivos de soporte de paquetes](#package-support-files-for-custom-builds-for-debianubunturaspbian) contiene instrucciones para usuarios que instalaron Caddy con el comando APT en sistemas derivados de Debian y aún necesitan el ejecutable de una compilación personalizada para su operación.



## Git

Requisitos:

- Go instalado (ver arriba)

Clona el repositorio:

<pre><code class="cmd bash">git clone "https://github.com/caddyserver/caddy.git"</code></pre>

Si no tienes git, puedes descargar el código fuente como un archivo desde [GitHub](https://github.com/caddyserver/caddy). Cada [versión](https://github.com/caddyserver/caddy/releases) también tiene instantáneas del código fuente.

Compila:

<pre><code class="cmd"><span class="bash">cd caddy/cmd/caddy/</span>
<span class="bash">go build</span></code></pre>


<aside class="tip">

Por [un error en Go](https://github.com/golang/go/issues/29228), estos pasos básicos no incrustan la información de versión. Si quieres la versión (`caddy version`), necesitas compilar Caddy como dependencia en lugar de como módulo principal. Las instrucciones están en el archivo `main.go` de Caddy en su [repositorio](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go). O puedes usar [`xcaddy`](#xcaddy), que automatiza este proceso.

</aside>

Los programas de Go son fáciles de compilar para otras plataformas. Solo establece las variables de entorno `GOOS`, `GOARCH` y/o `GOARM` con valores diferentes. ([Consulta la documentación de Go para más detalles.](https://golang.org/doc/install/source#environment))

Por ejemplo, para compilar Caddy para Windows cuando no estás en Windows:

<pre><code class="cmd bash">GOOS=windows go build</code></pre>

O de forma similar para Linux ARMv6 cuando no estás en Linux o estás en ARMv6:

<pre><code class="cmd bash">GOOS=linux GOARCH=arm GOARM=6 go build</code></pre>



## xcaddy

El comando [`xcaddy`](https://github.com/caddyserver/xcaddy) es la forma más fácil de compilar Caddy con información de versión y/o plugins.

Requisitos:

- Tener Go instalado (ver arriba)
- Asegúrate de que [`xcaddy`](https://github.com/caddyserver/xcaddy/releases) esté en tu `PATH`

**No** necesitas descargar el código fuente de Caddy (lo hará por ti).

Entonces compilar Caddy (con información de versión) es tan sencillo como:

<pre><code class="cmd bash">xcaddy build</code></pre>

Para compilar con plugins, usa `--with`:

<pre><code class="cmd bash">xcaddy build \
    --with github.com/caddyserver/nginx-adapter
	--with github.com/caddyserver/ntlm-transport@v0.1.1</code></pre>

Como puedes ver, puedes personalizar las versiones de los plugins con la sintaxis `@`. Las versiones pueden ser un nombre de etiqueta, un commit SHA o una rama.

La compilación multiplataforma con `xcaddy` funciona igual que con el comando `go`. Por ejemplo, para compilar para macOS:

<pre><code class="cmd bash">GOOS=darwin xcaddy build</code></pre>



## Docker

Puedes usar la imagen `:builder` como atajo para construir un nuevo binario de Caddy con módulos personalizados:

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

Reemplaza `<version>` con la versión más reciente de Caddy para empezar.

Observa la segunda instrucción `FROM`: esto produce una imagen mucho más pequeña al superponer el binario recién compilado sobre la imagen `caddy` normal.

El constructor usa `xcaddy` para compilar Caddy con los módulos proporcionados, similar al proceso [descrito arriba](#xcaddy). Las opciones `--mount=type=cache,target=/go/pkg/mod` y `--mount=type=cache,target=/root/.cache/go-build` se usan para almacenar en caché las dependencias de módulos de Go y los artefactos de compilación respectivamente, lo que acelera compilaciones posteriores. La opción es [una característica de Docker](https://docs.docker.com/build/cache/optimize/#use-cache-mounts), no de `xcaddy`.

Para usar Docker Compose, consulta nuestro archivo [`compose.yml`](/docs/running#docker-compose) recomendado y las instrucciones de uso.



<a id="package-support-files-for-custom-builds-for-debianubunturaspbian"></a>
## Archivos de soporte de paquetes para compilaciones personalizadas de Debian/Ubuntu/Raspbian

Este procedimiento busca simplificar la ejecución de binarios personalizados de `caddy` manteniendo los archivos de soporte del paquete `caddy`.

Este procedimiento permite a los usuarios aprovechar la configuración predeterminada, los archivos de servicio systemd y el autocompletado de bash del paquete oficial.

Requisitos:
- Instala el paquete `caddy` según [estas instrucciones](/docs/install#debian-ubuntu-raspbian)
- Construye tu binario personalizado de `caddy` (ve las secciones anteriores) o [descarga](/download) una compilación personalizada
- Tu binario personalizado de `caddy` debe estar ubicado en el directorio actual

Procedimiento:
<pre><code class="cmd"><span class="bash">sudo dpkg-divert --divert /usr/bin/caddy.default --rename /usr/bin/caddy</span>
<span class="bash">sudo mv ./caddy /usr/bin/caddy.custom</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.default 10</span>
<span class="bash">sudo update-alternatives --install /usr/bin/caddy caddy /usr/bin/caddy.custom 50</span>
<span class="bash">sudo systemctl restart caddy</span>
</code></pre>

Explicación:

- `dpkg-divert` moverá el binario `/usr/bin/caddy` a `/usr/bin/caddy.default` y colocará una redirección en caso de que algún paquete intente instalar un archivo en esa ubicación.

- `update-alternatives` creará un enlace simbólico desde el binario de `caddy` deseado a `/usr/bin/caddy`

- `systemctl restart caddy` apagará la versión predeterminada del servidor Caddy y pondrá en marcha la personalizada.

Puedes cambiar entre los binarios `caddy` personalizados y predeterminados ejecutando el siguiente comando y siguiendo la información en pantalla. Luego reinicia el servicio de Caddy.

<pre><code class="cmd bash">update-alternatives --config caddy</code></pre>

Para actualizar Caddy después de esto, puedes ejecutar [`caddy upgrade`](/docs/command-line#caddy-upgrade). Esto intenta [descargar](/download) una compilación con los mismos plugins que tu compilación actual, con la versión más reciente de Caddy, y luego reemplaza el binario actual por el nuevo.
