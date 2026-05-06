---
title: Perfilado de Caddy
---

Perfilado de Caddy
================

Un **profile** de un programa es una instantánea del uso de recursos en tiempo de ejecución. Los perfiles ayudan mucho a identificar áreas problemáticas, depurar bugs y crashes, y optimizar código.

Caddy usa la herramienta de Go para perfiles, llamada [pprof](https://github.com/google/pprof), que está integrada en el comando `go`.

Los perfiles informan consumo de CPU y memoria, muestran trazas de stack de goroutines y ayudan a localizar bloqueos o primitivas de sincronización con alta contención.

Cuando reportamos ciertos bugs de Caddy, a veces pedimos un profile. Este documento sirve de guía: explica cómo obtener perfiles con Caddy y cómo usar/interpretar los perfiles `pprof`.

Dos cosas para empezar:

1. **Los profiles de Caddy NO son sensibles de seguridad.** Contienen lecturas técnicas benignas, no contenido de memoria. No dan acceso a sistemas. Son seguros de compartir.
2. **Los profiles son ligeros y pueden tomarse en producción.** De hecho, para muchos usuarios es una buena práctica recomendada; consulta más abajo.

## Obtener profiles

Los perfiles están disponibles en la [admin interface](/docs/api) en `/debug/pprof/`. En una máquina con Caddy, abre esa URL en tu navegador:

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	Por defecto, la admin API solo es accesible localmente. Si estás en remoto, VMs o contenedores, consulta la sección siguiente para acceder al endpoint.
</aside>

Verás una tabla simple con contadores y enlaces, por ejemplo:

Count | Profile
----- | --------------------
79    | allocs
0     | block
0     | cmdline
22    | goroutine
79    | heap
0     | mutex
0     | profile
29    | threadcreate
0     | trace
|     | full goroutine stack dump

Los contadores ayudan a detectar fugas. Si sospechas una fuga, refresca la página y observa cuáles crecen de forma constante. Si sube `heap`, podría haber leak de memoria; si sube `goroutine`, leak de goroutines.

Haz clic en cada profile y mira su contenido. Algunos pueden estar vacíos y eso es normal. Los más usados son <b>goroutine</b> (stacks de funciones), <b>heap</b> (memoria) y <b>profile</b> (CPU). Otros ayudan a depurar contención de mutex o deadlocks.

Abajo de la tabla hay descripciones:

- **allocs:** muestra una muestra de todas las asignaciones de memoria pasadas
- **block:** trazas de stack por bloqueos en primitivas de sincronización
- **cmdline:** comando de ejecución actual
- **goroutine:** trazas de todas las goroutines actuales. Usa `debug=2` para exportarlo en el formato de panic.
- **heap:** muestra asignaciones de memoria de objetos vivos. Puedes pasar el parámetro `gc` para hacer GC antes de tomar la muestra.
- **mutex:** trazas de primitivas mutex disputadas
- **profile:** perfil CPU. Puedes pasar duración en segundos como parámetro GET.
- **threadcreate:** trazas de creación de threads del SO
- **trace:** traza de ejecución del programa actual. Duración en segundos con parámetro GET.

<aside class="tip">

La diferencia entre “goroutine” y “full goroutine stack dump” es el parámetro `?debug=2`. El dump completo se parece a un panic, incluye más detalle y no colapsa goroutines idénticas.

</aside>


### Descargar perfiles

Los enlaces del índice pprof dan perfiles en formato texto; eso facilita encontrar pistas rápidamente sin herramientas extra, y es lo que suele usar el equipo de Caddy.

El formato binario es el predeterminado. Enlace de HTML añade `?debug=` para obtener texto, excepto “profile” (CPU) que no tiene representación textual directa.

Parámetros de query que puedes usar (de la [documentación de Go](https://pkg.go.dev/net/http/pprof#hdr-Parameters)):

- **`debug=N` (all profiles except cpu):** formato de respuesta: N = 0 binario (default), N > 0 texto plano
- **`gc=N` (heap profile):** N > 0 ejecuta GC antes de perfilar
- **`seconds=N` (allocs, block, goroutine, heap, mutex, threadcreate):** devuelve un perfil delta
- **`seconds=N` (cpu, trace):** perfil durante N segundos

Al ser endpoints HTTP, puedes usar `curl` o `wget` para descargar.

Una vez descargados, puedes adjuntarlos a un issue en GitHub o usar un sitio como [pprof.me](https://pprof.me/). Para perfiles de CPU, [flamegraph.com](https://flamegraph.com/) es otra opción.

## Acceso remoto

_Si ya puedes acceder localmente a la admin API, salta esta sección._

Por defecto, la admin API de Caddy solo se expone por socket de loopback. Hay al menos 3 formas de acceder a `/debug/pprof` desde remoto.

### Reverse proxy a través del sitio

Una opción simple es hacer reverse proxy desde tu sitio:

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

Obviamente esto deja los profiles disponibles para quien pueda acceder al sitio. Si no quieres, añade autenticación con un módulo HTTP.

(No olvides el matcher `/debug/pprof/*`, si no, harías proxy de toda la admin API.)


### Túnel SSH

Otra opción es un túnel SSH (conexión cifrada con el protocolo SSH entre tu equipo y el servidor). Ejecuta algo como:

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

Esto conecta `localhost:8123` (tu máquina) a `localhost:2019` en `example.com`. Sustituye `username`, `example.com` y puertos.

<aside class="tip">

Este comando corre en foreground. Si lo pones en background con <kbd>Ctrl</kbd>+<kbd>Z</kbd>, se detiene el túnel y las conexiones fallan.

</aside>

Entonces en otra terminal:

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

Puedes evitar `-H "Host: ..."` usando puerto `2019` en ambos lados del túnel (si ese puerto no está usado localmente, p.ej. sin Caddy local).

Con el túnel activo puedes acceder a toda la admin API. Pulsa <kbd>Ctrl</kbd>+<kbd>C</kbd> sobre `ssh` para cerrarlo.

#### Túnel de larga duración

El comando anterior exige mantener terminal abierta. Para correrlo en background:

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

Se ejecuta en background y crea un socket de control en `/tmp/caddy-tunnel.sock`. Puedes usarlo para cerrar:

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>

### Admin remoto

También puedes configurar la admin API para aceptar conexiones remotas desde clientes autorizados.

(TODO: Write article about this.)


## Profiles de goroutines

El dump de goroutines es útil para saber qué goroutines existen y sus stacks, es decir, qué código ejecuta y qué está bloqueado.

Al hacer clic en “goroutines” o abrir `/debug/pprof/goroutine?debug=1`, verás una lista con stacks. Por ejemplo:

```
goroutine profile: total 88
23 @ 0x43e50e 0x436d37 ...
...
```

La primera línea indica lo que ves: `goroutine profile: total 88` y cuántas goroutines hay.

Las goroutines se agrupan por stack traces en orden decreciente de frecuencia.

La sintaxis de una línea es `<count> @ <addresses...>`.

La parte inicial con `@` muestra direcciones de llamada (punteros a función). Los campos siguientes son el trace de esa goroutine. Las líneas con `#` son comentarios para el lector y contienen el stack actual. La parte superior es la parte superior del stack (línea en ejecución actual), y la inferior es donde arrancó la goroutine.

Formato del stack:

```
<address> <package/func>+<offset> <filename>:<line>
```

### Full goroutine stack dump

Con `?debug=2` obtienes un dump completo. Incluye stacks completos de cada goroutine y no colapsa las repetidas. En servidores con carga, esto puede ser muy grande.

Ejemplo abreviado:

```
goroutine 61961905 [IO wait, 1 minutes]:
internal/poll.runtime_pollWait(0x7f9a9a059eb0, 0x72)
	runtime/netpoll.go:343 +0x85
...
golang.org/x/net/http2.(*serverConn).readFrames(0xc001756f00)
	golang.org/x/net/http2@v0.14.0/http2/server.go:818 +0x87
created by golang.org/x/net/http2.(*serverConn).serve in goroutine 61961902
	golang.org/x/net/http2@v0.14.0/server.go:930 +0x56a
```

Pese al volumen, las líneas más útiles suelen ser las primeras y últimas de cada goroutine.

La primera línea tiene número de goroutine (`61961905`), estado (“IO wait”) y duración (“1 minutes”).

- **Número de goroutine:** es el identificador, útil para rastrear qué goroutine la generó.
- **Estado:** lo que la goroutine está haciendo:
	- `running`: ejecutando código
	- `IO wait`: espera de red; no consume thread del SO por estar en poller no bloqueante
	- `sleep`: dormida
	- `select`: bloqueada esperando un caso
	- `select (no cases):` bloqueada en `select {}` vacío (Caddy usa uno para mantener activo el proceso)
	- `chan receive`: bloqueada esperando recibir por canal (`<-ch`)
	- `semacquire`: esperando un semáforo
	- `syscall`: ejecutando llamada al sistema y consumiendo thread
- **Duración:** tiempo de vida de la goroutine. Útil para detectar leaks. Si esperas que conexiones de red cierren en minutos y ves goroutines netconn vivas por horas, hay problema.

### Interpretar dumps de goroutines

Sin tocar código, de este ejemplo inferimos: creada hace ~1 min, esperando por socket de red y con un id alto (61961905).

Desde el dump en `debug=1` sabemos que este stack se ejecuta con frecuencia; la combinación de id alto + duración corta sugiere muchas goroutines cortas. Está en `pollWait` y lee HTTP/2 frames desde una conexión TLS, así que probablemente atiende una petición HTTP/2.

También sabemos que la goroutine que la creó no es de id muy bajo, por lo que se parece a una conexión nueva creada durante una petición existente, no a la raíz del proceso.

Cada programa es distinto, pero este patrón es habitual al depurar Caddy.

## Memory profiles

Las memory (heap) profiles registran asignaciones en el heap, que suelen ser grandes consumidoras de memoria. También suelen explicar problemas de rendimiento, porque las asignaciones implican syscalls.

Los heap profiles se ven casi igual que los goroutine profiles excepto por la primera línea. Ejemplo:

```
0: 0 [1: 4096] @ 0xb1fc05 ...
#	0xb1fc04	bufio.NewWriterSize+0x24					bufio/bufio.go:599
...
```

Formato:

```
<live objects> <live memory> [<allocations>: <allocation memory>] @ <addresses...>
```

En el ejemplo, hay una asignación de `bufio.NewWriterSize()` sin objetos vivos para ese stack.

Podemos inferir que `http2` está usando objetos de 4 KiB reutilizados para escribir frames HTTP/2. En código optimizado por pool, esto se ve con frecuencia y ayuda a validar si el pool funciona.

## CPU profiles

Los CPU profiles muestran dónde se usa más tiempo de procesador.

No hay forma de texto para estos, así que en la siguiente sección usamos `go tool pprof`.

Para descargar un CPU profile, consulta `/debug/pprof/profile?seconds=N`, donde `N` es segundos de colección. Durante esta recolección el rendimiento puede verse ligeramente afectado (otros perfiles casi no impactan). Al acabar, se descarga un binario `profile`.

## `go tool pprof`

Usaremos el analizador de Go para leer perfiles (también funciona con cualquier tipo). Comando:

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">

Puedes usar este comando para cualquier tipo de profile, no solo CPU.

</aside>

Hay muchos comandos; algunos comunes:

- `top`: muestra lo que más CPU usa. Puedes añadir número `top 20` o filtros regex.
- `web`: abre el call graph en navegador.
- `svg`: genera un SVG del call graph local.
- `tree`: vista tabular de la pila.

Ejemplo:

```
(pprof) top
Showing nodes accounting for 38.36s, 54.71% of 70.11s total
...
```

En ese ejemplo, mucho tiempo estaba en runtime de Go, señal de que un cambio en código debería ir con optimización del GC y luego revisar.

Puedes filtrar runtime:

```
(pprof) top -runtime
```

<aside class="tip">

Estas mediciones de CPU son por muestreo intermitente, y una muestra no se captura más seguido que la tasa de muestreo (10ms por defecto). Por eso no verás duraciones acumuladas por debajo de 10ms (aunque probablemente sí existan, se redondean arriba). Si necesitas tiempos más precisos, puedes hacer un execution trace, que no usa muestreo.

</aside>

Puedes usar `q` para salir de esta sesión y repetirla con otro tipo de profile:

```
(pprof) q
```

### Visualizaciones

También `svg` o `web` generan visualizaciones:

![CPU profile visualization](/old/resources/images/profile.png)

Hay gráficos similares para otros tipos de perfiles.

Si quieres aprender, mira [la documentación de pprof](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph).


### Comparar perfiles

Después de cambios de código puedes comparar perfiles base y post-cambio:

<pre><code class="cmd bash">go tool pprof -diff_base=before.prof after.prof
...
</code></pre>

Así verás en `top` qué cambió positivamente o empeoró.

Por ejemplo, Caddy mostró que bajó mucho memoria al cambiar una implementación:

![CPU profile visualization](/old/resources/images/profile-diff.png)

Esto ayuda a visualizar el impacto real de la optimización.

## Más lectura

El perfilado es amplio; aquí solo cubrimos lo básico.

Para ir más lejos:

- [Documentación de pprof](https://github.com/google/pprof/blob/main/doc/README.md)
- [Uso real de perfiles en Caddy](https://github.com/caddyserver/caddy/pull/4978)
- [Performance on the Go wiki](https://github.com/golang/go/wiki/Performance)
- [The `net/http/pprof` package](https://pkg.go.dev/net/http/pprof)
