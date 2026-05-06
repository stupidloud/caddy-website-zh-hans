---
title: Профилирование Caddy
---

Профилирование Caddy
================

**Program profile** — это snapshot использования resources программой во время runtime. Profiles могут быть крайне полезны для поиска problem areas, troubleshooting bugs и crashes, а также optimization code.

Caddy использует tooling Go для capturing profiles; он называется [pprof](https://github.com/google/pprof) и встроен в command `go`.

Profiles сообщают о consumers CPU и memory, показывают stack traces goroutines и помогают находить deadlocks или synchronization primitives с высоким contention.

При сообщении о некоторых bugs в Caddy мы можем попросить profile. Эта статья поможет. Она описывает и то, как получить profiles с Caddy, и то, как в целом использовать и интерпретировать полученные pprof profiles.


Две вещи, которые нужно знать перед началом:

1. **Caddy profiles НЕ являются security-sensitive.** Они содержат безвредные technical readouts, а не contents of memory. Они не дают access к systems. Ими безопасно делиться.
2. **Profiles легковесны и могут собираться в production.** На самом деле для многих users это recommended best practice; см. далее в статье.

<a id="obtaining-profiles"></a>
## Получение profiles

Profiles доступны через [admin interface](/docs/api) по адресу `/debug/pprof/`. На машине, где запущен Caddy, откройте его в browser:

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	По умолчанию admin API доступен только локально. Если Caddy запущен удаленно, в VMs или containers, см. следующий section о доступе к этому endpoint.
</aside>

Вы увидите простую table counts и links, например:

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

Counts — удобный способ быстро выявлять leaks. Если вы подозреваете leak, обновляйте страницу несколько раз, и увидите, как один или несколько counts постоянно растут. Если растет heap count, это possible memory leak; если растет goroutine count, это possible goroutine leak.

Откройте profiles по ссылкам и посмотрите, как они выглядят. Некоторые могут быть empty, и это часто нормально. Самые используемые: <b>goroutine</b> (function stacks), <b>heap</b> (memory) и <b>profile</b> (CPU). Другие profiles полезны для troubleshooting mutex contention или deadlocks.

Внизу есть простое описание каждого profile:

- **allocs:** Sampling всех прошлых memory allocations
- **block:** Stack traces, приведшие к blocking на synchronization primitives
- **cmdline:** Command line invocation текущей program
- **goroutine:** Stack traces всех текущих goroutines. Используйте debug=2 как query parameter, чтобы export в том же format, что и unrecovered panic.
- **heap:** Sampling memory allocations live objects. Можно указать GET parameter gc, чтобы run GC перед взятием heap sample.
- **mutex:** Stack traces holders contended mutexes
- **profile:** CPU profile. Можно указать duration в GET parameter seconds. После получения profile file используйте command go tool pprof для исследования profile.
- **threadcreate:** Stack traces, приведшие к creation новых OS threads
- **trace:** Trace execution текущей program. Можно указать duration в GET parameter seconds. После получения trace file используйте command go tool trace для исследования trace.

<aside class="tip">

Разница между "goroutine" и "full goroutine stack dump" — parameter `?debug=2`: full stack dump похож на output, который вы увидели бы после panic; он более verbose и, что важно, не collapses identical goroutines.

</aside>


<a id="downloading-profiles"></a>
### Скачивание profiles

Клик по links на pprof index page выше даст profiles в text format. Это полезно для debugging, и именно это команда Caddy предпочитает, потому что мы можем быстро просмотреть их в поиске obvious clues без дополнительного tooling.

Но binary фактически является default format. HTML links добавляют query string parameter `?debug=`, чтобы format их как text, кроме link "profile" (CPU), у которого нет textual representation.

Вот query string parameters, которые можно задавать (из [Go docs](https://pkg.go.dev/net/http/pprof#hdr-Parameters)):

- **`debug=N` (all profiles except cpu):** response format: N = 0: binary (default), N > 0: plaintext
- **`gc=N` (heap profile):** N > 0: run a garbage collection cycle before profiling
- **`seconds=N` (allocs, block, goroutine, heap, mutex, threadcreate profiles):** return a delta profile
- **`seconds=N` (cpu, trace profiles):** profile for the given duration

Поскольку это HTTP endpoints, можно также использовать любой HTTP client вроде curl или wget для скачивания profiles.

После скачивания profiles их можно upload в comment GitHub issue или использовать site вроде [pprof.me](https://pprof.me/). Конкретно для CPU profiles [flamegraph.com](https://flamegraph.com/) — еще один вариант.


<a id="accessing-remotely"></a>
## Удаленный доступ

*Если у вас уже есть локальный доступ к admin API, пропустите этот section.*

По умолчанию admin API Caddy доступен только через loopback socket. Однако есть как минимум 3 способа получить удаленный доступ к endpoint `/debug/pprof` Caddy:

<a id="reverse-proxy-through-your-site"></a>
### Reverse proxy через ваш site

Один простой вариант — просто reverse proxy к нему из вашего site:

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

Разумеется, это сделает profiles доступными тем, кто может подключиться к вашему site. Если это нежелательно, можно добавить authentication с помощью HTTP auth module по вашему выбору.

(Не забудьте matcher `/debug/pprof/*`, иначе вы проксируете весь admin API!)


<a id="ssh-tunnel"></a>
### SSH tunnel

Еще один способ — SSH tunnel. Это encrypted connection через SSH protocol между вашим computer и server. Выполните такую command на своем computer:

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

Это tunnels `localhost:8123` (на вашей local machine) к `localhost:2019` на `example.com`. Обязательно замените `username`, `example.com` и ports при необходимости.

<aside class="tip">

Эта command будет работать в foreground. Имейте в виду: если попытаться отправить process в background через <kbd>Ctrl</kbd>+<kbd>Z</kbd>, tunnel приостановится, и connections через tunnel не смогут connect.

</aside>

Затем в другом terminal можно выполнить `curl` так:

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

Можно избежать необходимости `-H "Host: ..."` используя port `2019` на обеих сторонах tunnel (но это требует, чтобы port `2019` не был уже занят на вашем computer, т. е. чтобы Caddy не был запущен локально).

Пока tunnel active, можно получить доступ к любому и всему admin API. Нажмите <kbd>Ctrl</kbd>+<kbd>C</kbd> на command `ssh`, чтобы закрыть tunnel.

<a id="long-running-tunnel"></a>
#### Long-running tunnel

Запуск tunnel command выше требует держать terminal open. Если нужно запустить tunnel в background, можно начать tunnel так:

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

Он запустится в background и создаст control socket в `/tmp/caddy-tunnel.sock`. Затем можно использовать control socket, чтобы закрыть tunnel, когда он больше не нужен:

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>


<a id="remote-admin-api"></a>
### Remote admin API

Также можно настроить admin API на прием remote connections от authorized clients.

(TODO: Write article about this.)



<a id="goroutine-profiles"></a>
## Goroutine profiles

Goroutine dump полезен, чтобы знать, какие goroutines существуют и какие у них call stacks. Иными словами, он дает представление о code, который сейчас executing или blocking/waiting.

Если кликнуть "goroutines" или перейти на `/debug/pprof/goroutine?debug=1`, вы увидите list goroutines и их call stacks. Например:

```
goroutine profile: total 88
23 @ 0x43e50e 0x436d37 0x46bda5 0x4e1327 0x4e261a 0x4e2608 0x545a65 0x5590c5 0x6b2e9b 0x50ddb8 0x6b307e 0x6b0650 0x6b6918 0x6b6921 0x4b8570 0xb11a05 0xb119d4 0xb12145 0xb1d087 0x4719c1
#	0x46bda4	internal/poll.runtime_pollWait+0x84			runtime/netpoll.go:343
#	0x4e1326	internal/poll.(*pollDesc).wait+0x26			internal/poll/fd_poll_runtime.go:84
#	0x4e2619	internal/poll.(*pollDesc).waitRead+0x279		internal/poll/fd_poll_runtime.go:89
#	0x4e2607	internal/poll.(*FD).Read+0x267				internal/poll/fd_unix.go:164
#	0x545a64	net.(*netFD).Read+0x24					net/fd_posix.go:55
#	0x5590c4	net.(*conn).Read+0x44					net/net.go:179
#	0x6b2e9a	crypto/tls.(*atLeastReader).Read+0x3a			crypto/tls/conn.go:805
#	0x50ddb7	bytes.(*Buffer).ReadFrom+0x97				bytes/buffer.go:211
#	0x6b307d	crypto/tls.(*Conn).readFromUntil+0xdd			crypto/tls/conn.go:827
#	0x6b064f	crypto/tls.(*Conn).readRecordOrCCS+0x24f		crypto/tls/conn.go:625
#	0x6b6917	crypto/tls.(*Conn).readRecord+0x157			crypto/tls/conn.go:587
#	0x6b6920	crypto/tls.(*Conn).Read+0x160				crypto/tls/conn.go:1369
#	0x4b856f	io.ReadAtLeast+0x8f					io/io.go:335
#	0xb11a04	io.ReadFull+0x64					io/io.go:354
#	0xb119d3	golang.org/x/net/http2.readFrameHeader+0x33		golang.org/x/net@v0.14.0/http2/frame.go:237
#	0xb12144	golang.org/x/net/http2.(*Framer).ReadFrame+0x84		golang.org/x/net@v0.14.0/http2/frame.go:498
#	0xb1d086	golang.org/x/net/http2.(*serverConn).readFrames+0x86	golang.org/x/net@v0.14.0/http2/server.go:818

1 @ 0x43e50e 0x44e286 0xafeeb3 0xb0af86 0x5c29fc 0x5c3225 0xb0365b 0xb03650 0x15cb6af 0x43e09b 0x4719c1
#	0xafeeb2	github.com/caddyserver/caddy/v2/cmd.cmdRun+0xcd2					github.com/caddyserver/caddy/v2@v2.7.4/cmd/commandfuncs.go:277
#	0xb0af85	github.com/caddyserver/caddy/v2/cmd.init.1.func2.WrapCommandFuncForCobra.func1+0x25	github.com/caddyserver/caddy/v2@v2.7.4/cmd/cobra.go:126
#	0x5c29fb	github.com/spf13/cobra.(*Command).execute+0x87b						github.com/spf13/cobra@v1.7.0/command.go:940
#	0x5c3224	github.com/spf13/cobra.(*Command).ExecuteC+0x3a4					github.com/spf13/cobra@v1.7.0/command.go:1068
#	0xb0365a	github.com/spf13/cobra.(*Command).Execute+0x5a						github.com/spf13/cobra@v1.7.0/command.go:992
#	0xb0364f	github.com/caddyserver/caddy/v2/cmd.Main+0x4f						github.com/caddyserver/caddy/v2@v2.7.4/cmd/main.go:65
#	0x15cb6ae	main.main+0xe										caddy/main.go:11
#	0x43e09a	runtime.main+0x2ba									runtime/proc.go:267

1 @ 0x43e50e 0x44e9c5 0x8ec085 0x4719c1
#	0x8ec084	github.com/caddyserver/certmagic.(*Cache).maintainAssets+0x304	github.com/caddyserver/certmagic@v0.19.2/maintain.go:67

...
```

Первая строка, `goroutine profile: total 88`, говорит, на что мы смотрим и сколько goroutines существует.

Далее идет list goroutines. Они grouped по call stacks в descending order frequency.

Строка goroutine имеет syntax: `<count> @ <addresses...>`

Строка начинается с count goroutines, у которых associated call stack. Symbol `@` указывает начало call instruction addresses, т. е. function pointers, которые originated goroutine. Каждый pointer — function call или call frame.

Можно заметить, что многие goroutines имеют один и тот же первый call address. Это main или entry point вашей program. Некоторые goroutines не будут originated там, потому что programs имеют разные functions `init()`, а Go runtime также может spawn goroutines.

Следующие lines начинаются с `#` и фактически являются comments для удобства reader. Они содержат current stack trace goroutine. Top представляет top of stack, т. е. текущую line of code being executed. Bottom представляет bottom of stack, или code, который goroutine initially started running.

Stack trace имеет такой format:

```
<address> <package/func>+<offset> <filename>:<line>
```

Address — function pointer; затем вы увидите Go package и function name (с associated type name, если это method), а также instruction offset внутри function. Затем в конце, возможно самая полезная info, file и line number.

<a id="full-goroutine-stack-dump"></a>
### Full goroutine stack dump

Если изменить query string parameter на `?debug=2`, мы получим full dump. Он включает verbose stack trace каждой goroutine, и identical goroutines не collapsed. Этот output может быть очень большим на busy servers, но это интересная information!

Посмотрим на один, соответствующий первому call stack выше (truncated):

```
goroutine 61961905 [IO wait, 1 minutes]:
internal/poll.runtime_pollWait(0x7f9a9a059eb0, 0x72)
	runtime/netpoll.go:343 +0x85
...
golang.org/x/net/http2.(*serverConn).readFrames(0xc001756f00)
	golang.org/x/net@v0.14.0/http2/server.go:818 +0x87
created by golang.org/x/net/http2.(*serverConn).serve in goroutine 61961902
	golang.org/x/net@v0.14.0/http2/server.go:930 +0x56a
```

Несмотря на verbosity, самая полезная information, uniquely provided этим dump, — первая и последняя lines каждой goroutine.

Первая строка содержит number goroutine (61961905), state ("IO wait") и duration ("1 minutes"):

- **Goroutine number:** Да, у goroutines есть numbers! Но они не exposed нашему code. Однако эти numbers особенно helpful в stack trace, потому что можно увидеть, какая goroutine spawned эту (см. в конце: "created by ... in goroutine 61961902"). Tooling ниже помогает рисовать visual graphs этого.

- **State:** Показывает, что goroutine сейчас делает. Возможные states:
	- `running`: Executing code - отлично!
	- `IO wait`: Waiting for network. Не consumes OS thread, потому что parked на non-blocking network poller.
	- `sleep`: Нам всем нужно больше этого.
	- `select`: Blocked on select; ждет, пока case станет available.
	- `select (no cases):` Blocked on empty select `select {}` specifically. Caddy использует один в main, чтобы продолжать running, потому что shutdowns инициируются из других goroutines.
	- `chan receive`: Blocked on channel receive (`<-ch`).
	- `semacquire`: Waiting to acquire semaphore (low-level synchronization primitive).
	- `syscall`: Executing system call. Consumes OS thread.

- **Duration:** Как долго goroutine существует. Полезно для поиска bugs вроде goroutine leaks. Например, если мы ожидаем, что все network connections будут closed через несколько minutes, что означает большое число netconn goroutines, живых hours?

<a id="interpreting-goroutine-dumps"></a>
### Интерпретация goroutine dumps

Не глядя в code, что можно узнать о goroutine выше?

Она создана всего около minute назад, ждет data over network socket, и ее goroutine number довольно large (61961905).

Из первого dump (debug=1) мы знаем, что ее call stack executed relatively frequently, а large goroutine number вместе с short duration suggests, что были десятки миллионов таких relatively short-lived goroutines. Она находится в function `pollWait`, а ее call history включает reading HTTP/2 frames из encrypted network connection, использующего TLS.

Значит, можно deduce, что эта goroutine обслуживает HTTP/2 request! Она ждет data от client. Более того, мы знаем, что goroutine, которая spawned ее, не одна из первых goroutines process, потому что у нее тоже high number; finding that goroutine in dump reveals, что она spawned для обработки нового HTTP/2 stream во время existing request. Напротив, другие goroutines с high numbers могут быть spawned goroutine с low number (например, 32), что indicates brand new connection сразу после call `Accept()` из socket.

Каждая program отличается, но при debugging Caddy эти patterns обычно true.

<a id="memory-profiles"></a>
## Memory profiles

Memory (или heap) profiles track heap allocations, которые являются major consumers memory в system. Allocations также обычно подозреваются в performance problems, потому что allocating memory требует system calls, которые могут быть slow.

Heap profiles похожи на goroutine profiles почти во всем, кроме начала top line. Пример:

```
0: 0 [1: 4096] @ 0xb1fc05 0xb1fc4d 0x48d8d1 0xb1fce6 0xb184c7 0xb1bc8e 0xb41653 0xb4105c 0xb4151d 0xb23b14 0x4719c1
#	0xb1fc04	bufio.NewWriterSize+0x24					bufio/bufio.go:599
#	0xb1fc4c	golang.org/x/net/http2.glob..func8+0x6c				golang.org/x/net@v0.17.0/http2/http2.go:263
#	0x48d8d0	sync.(*Pool).Get+0xb0						sync/pool.go:151
#	0xb1fce5	golang.org/x/net/http2.(*bufferedWriter).Write+0x45		golang.org/x/net@v0.17.0/http2/http2.go:276
#	0xb184c6	golang.org/x/net/http2.(*Framer).endWrite+0xc6			golang.org/x/net@v0.17.0/http2/frame.go:371
#	0xb1bc8d	golang.org/x/net/http2.(*Framer).WriteHeaders+0x48d		golang.org/x/net@v0.17.0/http2/frame.go:1131
#	0xb41652	golang.org/x/net/http2.(*writeResHeaders).writeHeaderBlock+0xd2	golang.org/x/net@v0.17.0/http2/write.go:239
#	0xb4105b	golang.org/x/net/http2.splitHeaderBlock+0xbb			golang.org/x/net@v0.17.0/http2/write.go:169
#	0xb4151c	golang.org/x/net/http2.(*writeResHeaders).writeFrame+0x1dc	golang.org/x/net@v0.17.0/http2/write.go:234
#	0xb23b13	golang.org/x/net/http2.(*serverConn).writeFrameAsync+0x73	golang.org/x/net@v0.17.0/http2/server.go:851
```

Format первой строки:

```
<live objects> <live memory> [<allocations>: <allocation memory>] @ <addresses...>
```

В примере выше есть single allocation, сделанная `bufio.NewWriterSize()`, но сейчас нет live objects из этого call stack.

Интересно, что из этого call stack можно infer: package http2 использовал pooled 4 KB для writing HTTP/2 frame(s) клиенту. В Go memory profiles часто видны pooled objects, если hot paths optimized to reuse allocations. Это reduces new allocations, а heap profile помогает понять, правильно ли используется pool!

<a id="cpu-profiles"></a>
## CPU profiles

CPU profiles помогают понять, где Go program spends большую часть scheduled time на processor.

Однако plaintext form для них нет, поэтому в следующем section мы используем commands `go tool pprof`, чтобы помочь их читать.

Чтобы скачать CPU profile, выполните request к `/debug/pprof/profile?seconds=N`, где N — число seconds, за которые нужно собрать profile. Во время CPU profile collection performance program может слегка impacted. (Другие profiles практически не имеют performance impact.)

После completion должен скачаться binary file с подходящим name `profile`. Затем его нужно исследовать.

<a id="go-tool-pprof"></a>
## `go tool pprof`

Мы используем встроенный profile analyzer Go для чтения CPU profile как пример, но его можно использовать с любым type profile.

Выполните эту command (заменив "profile" на actual filepath, если он отличается), которая открывает interactive prompt:

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">

Этой command можно исследовать любой type profile, не только CPU profiles. Principles те же для других profiles, и concepts переносятся.

</aside>

Это можно исследовать. Ввод `help` дает list commands, а `o` показывает current options. Если набрать `help <command>`, можно получить information about a specific command.

Commands много, но common ones:

- `top`: Показать, что used the most CPU. Можно добавить number вроде `top 20`, чтобы увидеть больше, или regex, чтобы "focus" on или ignore certain items.
- `web`: Открыть call graph в web browser. Отличный способ visually увидеть CPU usage.
- `svg`: Generate SVG image call graph. То же, что `web`, но не открывает browser, а SVG сохраняется locally.
- `tree`: Tabular view call stack.

Начнем с `top`. Видим output вроде:

```
(pprof) top
Showing nodes accounting for 38.36s, 54.71% of 70.11s total
Dropped 785 nodes (cum <= 0.35s)
Showing top 10 nodes out of 196
      flat  flat%   sum%        cum   cum%
    10.97s 15.65% 15.65%     10.97s 15.65%  runtime/internal/syscall.Syscall6
     6.59s  9.40% 25.05%     36.65s 52.27%  runtime.gcDrain
     5.03s  7.17% 32.22%      5.34s  7.62%  runtime.(*lfstack).pop (inline)
     3.69s  5.26% 37.48%     11.02s 15.72%  runtime.scanobject
     2.42s  3.45% 40.94%      2.42s  3.45%  runtime.(*lfstack).push
     2.26s  3.22% 44.16%      2.30s  3.28%  runtime.pageIndexOf (inline)
     2.11s  3.01% 47.17%      2.56s  3.65%  runtime.findObject
     2.03s  2.90% 50.06%      2.03s  2.90%  runtime.markBits.isMarked (inline)
     1.69s  2.41% 52.47%      1.69s  2.41%  runtime.memclrNoHeapPointers
     1.57s  2.24% 54.71%      1.57s  2.24%  runtime.epollwait
```

Top 10 consumers CPU все были в Go runtime -- в частности, много garbage collection (помните, syscalls используются для free и allocate memory). Это hint, что можно reduce allocations для улучшения performance, и heap profile будет worthwhile.

Хорошо, но что если нужно увидеть CPU utilization из нашего code? Можно ignore patterns, содержащие "runtime":

```
(pprof) top -runtime  
Active filters:
   ignore=runtime
Showing nodes accounting for 0.92s, 1.31% of 70.11s total
Dropped 160 nodes (cum <= 0.35s)
Showing top 10 nodes out of 243
      flat  flat%   sum%        cum   cum%
     0.17s  0.24%  0.24%      0.28s   0.4%  sync.(*Pool).getSlow
     0.11s  0.16%   0.4%      0.11s  0.16%  github.com/prometheus/client_golang/prometheus.(*histogram).observe (inline)
     0.10s  0.14%  0.54%      0.23s  0.33%  github.com/prometheus/client_golang/prometheus.(*MetricVec).hashLabels
     0.10s  0.14%  0.68%      0.12s  0.17%  net/textproto.CanonicalMIMEHeaderKey
     0.10s  0.14%  0.83%      0.10s  0.14%  sync.(*poolChain).popTail
     0.08s  0.11%  0.94%      0.26s  0.37%  github.com/prometheus/client_golang/prometheus.(*histogram).Observe
     0.07s   0.1%  1.04%      0.07s   0.1%  internal/poll.(*fdMutex).rwlock
     0.07s   0.1%  1.14%      0.10s  0.14%  path/filepath.Clean
     0.06s 0.086%  1.23%      0.06s 0.086%  context.value
     0.06s 0.086%  1.31%      0.06s 0.086%  go.uber.org/zap/buffer.(*Buffer).AppendByte
```

Что ж, ясно, что Prometheus metrics — еще один top consumer, но cumulatively они на orders of magnitude меньше, чем GC выше. Резкая difference suggests, что нужно focus on reducing GC.

<aside class="tip">

Важно отметить, что CPU profiles получают measurements через intermittent sampling, и samples никогда не будут captured чаще sampling rate, который по умолчанию 10ms. Поэтому вы не увидите cumulative time durations меньше 10ms (они, вероятно, меньше, но rounded up). Для более specific timings можно сделать execution trace, который не использует sampling. (TODO: Add section about tracing.)

</aside>

Используем `q`, чтобы quit этот profile, и применим ту же command к heap profile:

```
(pprof) top
Showing nodes accounting for 22259.07kB, 81.30% of 27380.04kB total
Showing top 10 nodes out of 102
      flat  flat%   sum%        cum   cum%
   12300kB 44.92% 44.92%    12300kB 44.92%  runtime.allocm
 2570.01kB  9.39% 54.31%  2570.01kB  9.39%  bufio.NewReaderSize
 2048.81kB  7.48% 61.79%  2048.81kB  7.48%  runtime.malg
 1542.01kB  5.63% 67.42%  1542.01kB  5.63%  bufio.NewWriterSize
 ...
 ```

Bingo. Почти половина memory allocated строго для read и write buffers из-за использования package bufio. Поэтому можно infer, что optimizing code для reducing buffering будет very beneficial. ([Связанный patch в Caddy](https://github.com/caddyserver/caddy/pull/4978) именно это и делает).

<a id="visualizations"></a>
### Visualizations

Если вместо этого выполнить commands `svg` или `web`, мы получим visualization profile:

![CPU profile visualization](/old/resources/images/profile.png)

Это CPU profile, но similar graphs доступны и для других profile types.

Чтобы узнать, как читать эти graphs, прочитайте [pprof documentation](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph).


<a id="diffing-profiles"></a>
### Diffing profiles

После code change можно compare before и after через difference analysis ("diff"). Вот diff heap:

<pre><code class="cmd bash">go tool pprof -diff_base=before.prof after.prof
File: caddy
Type: inuse_space
Time: Aug 29, 2022 at 1:21am (MDT)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) top
Showing nodes accounting for -26.97MB, 49.32% of 54.68MB total
Dropped 10 nodes (cum <= 0.27MB)
Showing top 10 nodes out of 137
      flat  flat%   sum%        cum   cum%
  -27.04MB 49.45% 49.45%   -27.04MB 49.45%  bufio.NewWriterSize
      -2MB  3.66% 53.11%       -2MB  3.66%  runtime.allocm
    1.06MB  1.93% 51.18%     1.06MB  1.93%  github.com/yuin/goldmark/util.init
    1.03MB  1.89% 49.29%     1.03MB  1.89%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.glob..func2
       1MB  1.84% 47.46%        1MB  1.84%  bufio.NewReaderSize
      -1MB  1.83% 49.29%       -1MB  1.83%  runtime.malg
       1MB  1.83% 47.46%        1MB  1.83%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.cloneRequest
      -1MB  1.83% 49.29%       -1MB  1.83%  net/http.(*Server).newConn
   -0.55MB  1.00% 50.29%    -0.55MB  1.00%  html.populateMaps
    0.53MB  0.97% 49.32%     0.53MB  0.97%  github.com/alecthomas/chroma.TypeRemappingLexer</code></pre>

Как видно, мы reduced memory allocations примерно наполовину!

Diffs тоже можно visualize:

![CPU profile visualization](/old/resources/images/profile-diff.png)

Это делает очень obvious, как changes повлияли на performance отдельных parts program.

<a id="further-reading"></a>
## Дальнейшее чтение

В program profiling нужно освоить многое, и мы только scratched the surface.

Чтобы действительно добавить "pro" в "profiling", рассмотрите эти resources:

- [pprof Documentation](https://github.com/google/pprof/blob/main/doc/README.md)
- [Real-world use profiles with Caddy](https://github.com/caddyserver/caddy/pull/4978)
- [Performance on the Go wiki](https://github.com/golang/go/wiki/Performance)
- [Package `net/http/pprof`](https://pkg.go.dev/net/http/pprof)
