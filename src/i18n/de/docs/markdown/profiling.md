---
title: Caddy profilieren
---

<a id="profiling-caddy"></a>
Caddy profilieren
================

Ein **Programmprofil** ist eine Momentaufnahme der Ressourcennutzung eines Programms zur Laufzeit. Profile können äußerst hilfreich sein, um Problembereiche zu identifizieren, Fehler und Abstürze zu untersuchen und Code zu optimieren.

Caddy verwendet zum Erfassen von Profilen die Go-Werkzeuge, genannt [pprof](https://github.com/google/pprof), die in den Befehl `go` integriert sind.

Profile zeigen Verbraucher von CPU und Speicher, Stack Traces von Goroutinen und helfen dabei, Deadlocks oder Synchronisationsprimitive mit hoher Contention aufzuspüren.

Wenn bestimmte Fehler in Caddy gemeldet werden, bitten wir möglicherweise um ein Profil. Dieser Artikel hilft dabei. Er beschreibt sowohl, wie du Profile mit Caddy erhältst, als auch allgemein, wie du die resultierenden pprof-Profile verwendest und interpretierst.


Zwei Dinge vor dem Einstieg:

1. **Caddy-Profile sind NICHT sicherheitssensibel.** Sie enthalten harmlose technische Ausgaben, nicht den Inhalt des Speichers. Sie gewähren keinen Zugriff auf Systeme. Sie können sicher geteilt werden.
2. **Profile sind leichtgewichtig und können in Produktion gesammelt werden.** Tatsächlich ist das für viele Benutzer eine empfohlene Best Practice; mehr dazu später in diesem Artikel.

<a id="obtaining-profiles"></a>
## Profile abrufen

Profile sind über die [Admin-Schnittstelle](/docs/api) unter `/debug/pprof/` verfügbar. Öffne auf einer Maschine, auf der Caddy läuft, diese Adresse im Browser:

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	Standardmäßig ist die admin API nur lokal erreichbar. Wenn Caddy remote, in VMs oder in Containern läuft, lies im nächsten Abschnitt, wie du auf diesen Endpoint zugreifst.
</aside>

Du wirst eine einfache Tabelle mit Zählwerten und Links sehen, zum Beispiel:

Anzahl | Profil
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

Die Zählwerte sind ein praktischer Weg, Leaks schnell zu erkennen. Wenn du ein Leak vermutest, aktualisiere die Seite wiederholt; dann siehst du, ob einer oder mehrere dieser Werte ständig steigen. Wenn der Heap-Wert wächst, ist es ein mögliches Speicherleck; wenn der Goroutine-Wert wächst, ist es ein mögliches Goroutine-Leck.

Klicke dich durch die Profile und schau dir an, wie sie aussehen. Manche sind leer, und das ist oft normal. Die am häufigsten verwendeten sind <b>goroutine</b> (Funktions-Stacks), <b>heap</b> (Speicher) und <b>profile</b> (CPU). Andere Profile sind nützlich, um Mutex-Contention oder Deadlocks zu untersuchen.

Unten gibt es eine einfache Beschreibung jedes Profils:

- **allocs:** Eine Stichprobe aller bisherigen Speicherallokationen
- **block:** Stack Traces, die zum Blockieren an Synchronisationsprimitiven geführt haben
- **cmdline:** Der Befehlszeilenaufruf des aktuellen Programms
- **goroutine:** Stack Traces aller aktuellen Goroutinen. Verwende debug=2 als Query-Parameter, um im selben Format wie bei einer nicht abgefangenen Panic zu exportieren.
- **heap:** Eine Stichprobe der Speicherallokationen lebender Objekte. Du kannst den GET-Parameter gc angeben, um vor der Heap-Stichprobe GC auszuführen.
- **mutex:** Stack Traces von Haltern umkämpfter Mutexe
- **profile:** CPU-Profil. Du kannst die Dauer im GET-Parameter seconds angeben. Nachdem du die Profildatei erhalten hast, verwende den Befehl go tool pprof, um das Profil zu untersuchen.
- **threadcreate:** Stack Traces, die zur Erstellung neuer OS-Threads geführt haben
- **trace:** Ein Trace der Ausführung des aktuellen Programms. Du kannst die Dauer im GET-Parameter seconds angeben. Nachdem du die Trace-Datei erhalten hast, verwende den Befehl go tool trace, um den Trace zu untersuchen.

<aside class="tip">

Der Unterschied zwischen "goroutine" und "full goroutine stack dump" ist der Parameter `?debug=2`: Der vollständige Stack Dump ähnelt der Ausgabe, die du nach einer Panic sehen würdest; er ist ausführlicher und fasst insbesondere identische Goroutinen nicht zusammen.

</aside>


<a id="downloading-profiles"></a>
### Profile herunterladen

Wenn du auf die Links der obigen pprof-Indexseite klickst, bekommst du Profile im Textformat. Das ist zum Debuggen nützlich, und genau das bevorzugen wir im Caddy-Team, weil wir es schnell auf offensichtliche Hinweise durchsehen können, ohne zusätzliche Werkzeuge zu brauchen.

Binär ist aber tatsächlich das Standardformat. Die HTML-Links hängen den Query-String-Parameter `?debug=` an, um sie als Text zu formatieren, außer beim (CPU-)Link "profile", für den es keine Textdarstellung gibt.

Diese Query-String-Parameter kannst du setzen (aus [der Go-Dokumentation](https://pkg.go.dev/net/http/pprof#hdr-Parameters)):

- **`debug=N` (alle Profile außer cpu):** Response-Format: N = 0: binär (Standard), N > 0: Klartext
- **`gc=N` (heap profile):** N > 0: vor dem Profiling einen Garbage-Collection-Zyklus ausführen
- **`seconds=N` (allocs, block, goroutine, heap, mutex, threadcreate profiles):** ein Delta-Profil zurückgeben
- **`seconds=N` (cpu, trace profiles):** für die angegebene Dauer profilieren

Da es sich um HTTP-Endpoints handelt, kannst du Profile auch mit jedem HTTP-Client wie curl oder wget herunterladen.

Nachdem deine Profile heruntergeladen sind, kannst du sie in einen GitHub-Issue-Kommentar hochladen oder eine Website wie [pprof.me](https://pprof.me/) verwenden. Speziell für CPU-Profile ist [flamegraph.com](https://flamegraph.com/) eine weitere Option.


<a id="accessing-remotely"></a>
## Remote zugreifen

*Wenn du bereits lokal auf die admin API zugreifen kannst, überspringe diesen Abschnitt.*

Standardmäßig ist Caddys admin API nur über den Loopback-Socket erreichbar. Es gibt jedoch mindestens 3 Wege, wie du remote auf Caddys `/debug/pprof`-Endpoint zugreifen kannst:

<a id="reverse-proxy-through-your-site"></a>
### Reverse Proxy über deine Site

Eine einfache Möglichkeit ist, ihn von deiner Site aus schlicht per Reverse Proxy weiterzuleiten:

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

Dadurch werden Profile natürlich für alle verfügbar, die sich mit deiner Site verbinden können. Wenn das nicht gewünscht ist, kannst du mit einem HTTP-Auth-Modul deiner Wahl Authentifizierung hinzufügen.

(Vergiss den Matcher `/debug/pprof/*` nicht, sonst leitest du die gesamte admin API per Proxy weiter!)


### SSH-Tunnel

Ein anderer Weg ist ein SSH-Tunnel. Das ist eine verschlüsselte Verbindung mit dem SSH-Protokoll zwischen deinem Computer und deinem Server. Führe auf deinem Computer einen Befehl wie diesen aus:

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

Das tunnelt `localhost:8123` (auf deiner lokalen Maschine) zu `localhost:2019` auf `example.com`. Ersetze `username`, `example.com` und Ports nach Bedarf.

<aside class="tip">

Dieser Befehl läuft im Vordergrund. Beachte: Wenn du versuchst, den Prozess mit <kbd>Ctrl</kbd>+<kbd>Z</kbd> in den Hintergrund zu schicken, pausiert das den Tunnel, und Verbindungen über den Tunnel können nicht hergestellt werden.

</aside>

Dann kannst du in einem anderen Terminal `curl` so ausführen:

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

Du kannst die Notwendigkeit von `-H "Host: ..."` vermeiden, indem du Port `2019` auf beiden Seiten des Tunnels verwendest (das setzt aber voraus, dass Port `2019` auf deinem eigenen Computer nicht bereits belegt ist, also dort kein Caddy lokal läuft).

Während der Tunnel aktiv ist, kannst du auf sämtliche Teile der admin API zugreifen. Drücke <kbd>Ctrl</kbd>+<kbd>C</kbd> beim `ssh`-Befehl, um den Tunnel zu schließen.

<a id="long-running-tunnel"></a>
#### Länger laufender Tunnel

Bei einem Tunnel mit dem obigen Befehl musst du das Terminal offen halten. Wenn du den Tunnel im Hintergrund ausführen möchtest, kannst du ihn so starten:

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

Das startet im Hintergrund und erstellt einen Control Socket unter `/tmp/caddy-tunnel.sock`. Anschließend kannst du den Control Socket verwenden, um den Tunnel zu schließen, wenn du fertig bist:

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>


<a id="remote-admin-api"></a>
### Remote admin API

Du kannst die admin API auch so konfigurieren, dass sie Remote-Verbindungen von autorisierten Clients akzeptiert.

(TODO: Artikel darüber schreiben.)



<a id="goroutine-profiles"></a>
## Goroutine-Profile

Der Goroutine Dump ist nützlich, um zu wissen, welche Goroutinen existieren und wie ihre Call Stacks aussehen. Mit anderen Worten: Er gibt uns eine Vorstellung davon, welcher Code gerade ausgeführt wird oder blockiert/wartet.

Wenn du auf "goroutines" klickst oder `/debug/pprof/goroutine?debug=1` aufrufst, siehst du eine Liste von Goroutinen und ihren Call Stacks. Zum Beispiel:

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

Die erste Zeile, `goroutine profile: total 88`, sagt uns, was wir betrachten und wie viele Goroutinen es gibt.

Danach folgt die Liste der Goroutinen. Sie sind nach ihren Call Stacks gruppiert, in absteigender Häufigkeit.

Eine Goroutine-Zeile hat diese Syntax: `<count> @ <addresses...>`

Die Zeile beginnt mit der Anzahl der Goroutinen, die den zugehörigen Call Stack haben. Das Symbol `@` markiert den Beginn der Call-Instruction-Adressen, also der Function Pointer, aus denen die Goroutine entstanden ist. Jeder Pointer ist ein Funktionsaufruf bzw. ein Call Frame.

Du wirst möglicherweise bemerken, dass viele deiner Goroutinen dieselbe erste Call-Adresse teilen. Das ist die main-Funktion deines Programms bzw. sein Einstiegspunkt. Manche Goroutinen entstehen dort nicht, weil Programme verschiedene `init()`-Funktionen haben und auch die Go-Laufzeit Goroutinen starten kann.

Die folgenden Zeilen beginnen mit `#` und sind tatsächlich nur Kommentare zugunsten des Lesers. Sie enthalten den aktuellen Stack Trace der Goroutine. Oben steht die Spitze des Stacks, also die aktuell ausgeführte Codezeile. Unten steht der Boden des Stacks, also der Code, mit dem die Goroutine ursprünglich zu laufen begann.

Der Stack Trace hat dieses Format:

```
<address> <package/func>+<offset> <filename>:<line>
```

Die Adresse ist der Function Pointer; danach siehst du den Go-Paket- und Funktionsnamen (mit zugehörigem Typnamen, wenn es eine Methode ist) sowie den Instruction Offset innerhalb der Funktion. Am Ende steht die vielleicht nützlichste Information: Datei und Zeilennummer.

<a id="full-goroutine-stack-dump"></a>
### Vollständiger Goroutine Stack Dump

Wenn wir den Query-String-Parameter zu `?debug=2` ändern, erhalten wir einen vollständigen Dump. Er enthält einen ausführlichen Stack Trace jeder Goroutine, und identische Goroutinen werden nicht zusammengefasst. Diese Ausgabe kann auf ausgelasteten Servern sehr groß sein, ist aber interessante Information!

Schauen wir uns eine an, die dem ersten Call Stack oben entspricht (gekürzt):

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

Trotz der Ausführlichkeit sind die nützlichsten Informationen, die dieser Dump eindeutig liefert, die erste und letzte Zeile jeder Goroutine.

Die erste Zeile enthält die Nummer der Goroutine (61961905), ihren Zustand ("IO wait") und die Dauer ("1 minutes"):

- **Goroutine-Nummer:** Ja, Goroutinen haben Nummern! Sie werden unserem Code aber nicht zugänglich gemacht. Diese Nummern sind in einem Stack Trace dennoch besonders hilfreich, weil wir sehen können, welche Goroutine diese hier gestartet hat (siehe am Ende: "created by ... in goroutine 61961902"). Weiter unten gezeigte Werkzeuge helfen uns, daraus visuelle Graphen zu zeichnen.

- **Zustand:** Das sagt uns, was die Goroutine gerade tut. Hier sind einige mögliche Zustände, die du sehen kannst:
	- `running`: Führt Code aus - großartig!
	- `IO wait`: Wartet auf Netzwerk. Verbraucht keinen OS-Thread, weil sie auf einem nicht blockierenden Netzwerk-Poller geparkt ist.
	- `sleep`: Davon brauchen wir alle mehr.
	- `select`: Blockiert in einem select; wartet darauf, dass ein case verfügbar wird.
	- `select (no cases):` Blockiert konkret in einem leeren select `select {}`. Caddy verwendet eines in seiner main-Funktion, um weiterzulaufen, weil Shutdowns von anderen Goroutinen initiiert werden.
	- `chan receive`: Blockiert beim Empfang aus einem Channel (`<-ch`).
	- `semacquire`: Wartet darauf, ein Semaphore zu erwerben (niedrigstufiges Synchronisationsprimitiv).
	- `syscall`: Führt einen Systemaufruf aus. Verbraucht einen OS-Thread.

- **Dauer:** Wie lange die Goroutine existiert. Nützlich, um Fehler wie Goroutine-Lecks zu finden. Wenn wir zum Beispiel erwarten, dass alle Netzwerkverbindungen nach wenigen Minuten geschlossen sind, was bedeutet es dann, wenn wir viele netconn-Goroutinen finden, die seit Stunden leben?

<a id="interpreting-goroutine-dumps"></a>
### Goroutine Dumps interpretieren

Was können wir ohne Blick in den Code über die obige Goroutine lernen?

Sie wurde erst vor etwa einer Minute erstellt, wartet auf Daten über einen Netzwerk-Socket, und ihre Goroutine-Nummer ist ziemlich groß (61961905).

Aus dem ersten Dump (debug=1) wissen wir, dass ihr Call Stack relativ häufig ausgeführt wird; die große Goroutine-Nummer kombiniert mit der kurzen Dauer deutet darauf hin, dass es zig Millionen dieser relativ kurzlebigen Goroutinen gegeben hat. Sie befindet sich in einer Funktion namens `pollWait`, und ihre Aufrufhistorie enthält das Lesen von HTTP/2-Frames aus einer verschlüsselten Netzwerkverbindung, die TLS verwendet.

Daraus können wir ableiten, dass diese Goroutine eine HTTP/2-Anfrage bedient! Sie wartet auf Daten vom Client. Mehr noch: Wir wissen, dass die Goroutine, die sie gestartet hat, keine der ersten Goroutinen des Prozesses ist, weil auch sie eine hohe Nummer hat; wenn man diese Goroutine im Dump findet, sieht man, dass sie gestartet wurde, um während einer bestehenden Anfrage einen neuen HTTP/2-Stream zu bearbeiten. Im Gegensatz dazu können andere Goroutinen mit hohen Nummern von einer Goroutine mit niedriger Nummer (etwa 32) gestartet worden sein, was auf eine ganz neue Verbindung direkt aus einem `Accept()`-Aufruf am Socket hinweist.

Jedes Programm ist anders, aber beim Debuggen von Caddy treffen diese Muster tendenziell zu.

<a id="memory-profiles"></a>
## Speicherprofile

Speicher- bzw. Heap-Profile verfolgen Heap-Allokationen, die die größten Speicherverbraucher auf einem System sind. Allokationen sind außerdem ein üblicher Verdächtiger bei Performance-Problemen, weil das Allozieren von Speicher Systemaufrufe benötigt, die langsam sein können.

Heap-Profile sehen Goroutine-Profilen in fast jeder Hinsicht ähnlich, außer am Anfang der obersten Zeile. Hier ist ein Beispiel:

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

Das Format der ersten Zeile ist:

```
<live objects> <live memory> [<allocations>: <allocation memory>] @ <addresses...>
```

Im obigen Beispiel wurde eine einzelne Allokation von `bufio.NewWriterSize()` vorgenommen, aber aus diesem Call Stack gibt es aktuell keine lebenden Objekte.

Interessanterweise können wir aus diesem Call Stack schließen, dass das http2-Paket gepoolte 4 KB verwendet hat, um HTTP/2-Frame(s) an den Client zu schreiben. In Go-Speicherprofilen sieht man oft gepoolte Objekte, wenn Hot Paths so optimiert wurden, dass Allokationen wiederverwendet werden. Das reduziert neue Allokationen, und das Heap-Profil kann dir helfen zu erkennen, ob der Pool richtig genutzt wird!

<a id="cpu-profiles"></a>
## CPU-Profile

CPU-Profile helfen dir zu verstehen, wo das Go-Programm den größten Teil seiner eingeplanten Zeit auf dem Prozessor verbringt.

Für diese Profile gibt es jedoch keine Klartextform. Im nächsten Abschnitt verwenden wir daher Befehle von `go tool pprof`, um sie lesbar zu machen.

Um ein CPU-Profil herunterzuladen, stelle eine Anfrage an `/debug/pprof/profile?seconds=N`, wobei N die Anzahl der Sekunden ist, über die du das Profil sammeln möchtest. Während der Erfassung eines CPU-Profils kann die Programmleistung leicht beeinträchtigt werden. (Andere Profile haben praktisch keinen Performance-Einfluss.)

Wenn der Vorgang abgeschlossen ist, sollte eine Binärdatei heruntergeladen werden, passend `profile` genannt. Dann müssen wir sie untersuchen.

## `go tool pprof`

Wir verwenden Go's eingebauten Profil-Analyzer, um als Beispiel das CPU-Profil zu lesen; du kannst ihn aber mit jeder Art von Profil verwenden.

Führe diesen Befehl aus (ersetze "profile" durch den tatsächlichen Dateipfad, falls er anders ist), der eine interaktive Eingabeaufforderung öffnet:

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">

Du kannst diesen Befehl verwenden, um jede Art von Profil zu untersuchen, nicht nur CPU-Profile. Die Prinzipien sind für andere Profile dieselben, und die Konzepte lassen sich übertragen.

</aside>

Das kannst du selbst erkunden. Wenn du `help` eingibst, bekommst du eine Liste der Befehle, und `o` zeigt dir aktuelle Optionen. Wenn du `help <command>` eingibst, bekommst du Informationen zu einem bestimmten Befehl.

Es gibt viele Befehle, aber einige häufige sind:

- `top`: Zeigt, was am meisten CPU verbraucht hat. Du kannst eine Zahl wie `top 20` anhängen, um mehr zu sehen, oder einen Regex, um auf bestimmte Einträge zu "fokussieren" oder sie zu ignorieren.
- `web`: Öffnet den Call Graph in deinem Webbrowser. Das ist eine gute Möglichkeit, CPU-Nutzung visuell zu sehen.
- `svg`: Erzeugt ein SVG-Bild des Call Graph. Es ist dasselbe wie `web`, öffnet aber nicht deinen Webbrowser; das SVG wird lokal gespeichert.
- `tree`: Eine tabellarische Ansicht des Call Stacks.

Beginnen wir mit `top`. Wir sehen eine Ausgabe wie:

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

Die Top-10-CPU-Verbraucher lagen alle in der Go-Laufzeit -- insbesondere viel Garbage Collection (denk daran, dass Syscalls verwendet werden, um Speicher freizugeben und zu allozieren). Das ist ein Hinweis darauf, dass wir Allokationen reduzieren könnten, um die Performance zu verbessern, und dass ein Heap-Profil sinnvoll wäre.

OK, aber was, wenn wir CPU-Auslastung aus unserem eigenen Code sehen möchten? Wir können Muster ignorieren, die "runtime" enthalten:

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

Nun ist klar, dass Prometheus-Metriken ein weiterer Top-Verbraucher sind, aber du wirst bemerken, dass sie kumuliert um Größenordnungen weniger ausmachen als die GC oben. Der deutliche Unterschied legt nahe, dass wir uns auf die Reduzierung von GC konzentrieren sollten.

<aside class="tip">

Wichtig ist: CPU-Profile beziehen ihre Messwerte aus periodischem Sampling, und Samples werden nie häufiger erfasst als die Sampling-Rate, die standardmäßig 10 ms beträgt. Deshalb siehst du keine kumulierten Zeitdauern unter 10 ms (sie sind wahrscheinlich kürzer, werden aber aufgerundet). Für genauere Timings kannst du einen Execution Trace verwenden, der kein Sampling nutzt. (TODO: Abschnitt über Tracing hinzufügen.)

</aside>

Verlassen wir dieses Profil mit `q` und verwenden denselben Befehl für das Heap-Profil:

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

Bingo. Fast die Hälfte des Speichers wird ausschließlich für Lese- und Schreibpuffer aus unserer Nutzung des bufio-Pakets alloziert. Daraus können wir schließen, dass eine Optimierung unseres Codes zur Reduzierung von Buffering sehr vorteilhaft wäre. (Der [zugehörige Patch in Caddy](https://github.com/caddyserver/caddy/pull/4978) tut genau das.)

<a id="visualizations"></a>
### Visualisierungen

Wenn wir stattdessen die Befehle `svg` oder `web` ausführen, bekommen wir eine Visualisierung des Profils:

![CPU profile visualization](/old/resources/images/profile.png)

Dies ist ein CPU-Profil, aber ähnliche Graphen sind für andere Profiltypen verfügbar.

Wie man diese Graphen liest, erfährst du in [der pprof-Dokumentation](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph).


<a id="diffing-profiles"></a>
### Profile vergleichen

Nachdem du eine Codeänderung vorgenommen hast, kannst du Vorher und Nachher mit einer Differenzanalyse ("diff") vergleichen. Hier ist ein Diff des Heaps:

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

Wie du siehst, haben wir Speicherallokationen ungefähr halbiert!

Diffs können ebenfalls visualisiert werden:

![CPU profile visualization](/old/resources/images/profile-diff.png)

Das macht sehr deutlich, wie sich die Änderungen auf die Performance bestimmter Programmteile ausgewirkt haben.

<a id="further-reading"></a>
## Weiterführende Lektüre

Beim Programm-Profiling gibt es viel zu meistern, und wir haben nur an der Oberfläche gekratzt.

Um wirklich zum Profi im "Profiling" zu werden, ziehe diese Ressourcen in Betracht:

- [pprof-Dokumentation](https://github.com/google/pprof/blob/main/doc/README.md)
- [Ein Praxisbeispiel für Profile mit Caddy](https://github.com/caddyserver/caddy/pull/4978)
- [Performance im Go-Wiki](https://github.com/golang/go/wiki/Performance)
- [Das Paket `net/http/pprof`](https://pkg.go.dev/net/http/pprof)
