---
title: log (Caddyfile directive)
---

<script>
ready(function() {
	// Fix > in code blocks
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Skip if ends with >
			if (item.textContent.trim().endsWith('>')) return;
			// Replace > with <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# log

Aktiviert und konfiguriert HTTP-Request-Logging (auch als Access Logs bekannt).

<aside class="tip">

Um Caddys Runtime-Logs zu konfigurieren, verwenden Sie stattdessen die [globale Option `log`](/docs/caddyfile/options#log).

</aside>


Die Direktive `log` gilt für die Hostnamen des Site-Blocks, in dem sie erscheint, sofern dies nicht mit der Subdirektive `hostnames` überschrieben wird.

Wenn konfiguriert, werden standardmäßig alle Requests an die Site geloggt. Um einige Requests bedingt vom Logging auszunehmen, verwenden Sie die Direktive [`log_skip`](log_skip).

Um eigene Felder zu Log-Einträgen hinzuzufügen, verwenden Sie die Direktive [`log_append`](log_append).


- [Syntax](#syntax)
- [Output-Module](#output-modules)
  - [stderr](#stderr)
  - [stdout](#stdout)
  - [discard](#discard)
  - [file](#file)
  - [net](#net)
- [Format-Module](#format-modules)
  - [console](#console)
  - [json](#json)
  - [filter](#filter)
    - [delete](#delete)
	- [rename](#rename)
	- [replace](#replace)
	- [ip_mask](#ip-mask)
	- [query](#query)
	- [cookie](#cookie)
	- [regexp](#regexp)
	- [hash](#hash)
  - [append](#append)
- [Beispiele](#examples)

Standardmäßig werden Header mit potenziell sensiblen Informationen (`Cookie`, `Set-Cookie`, `Authorization` und `Proxy-Authorization`) in Access Logs als `REDACTED` geloggt. Dieses Verhalten kann mit der globalen Server-Option [`log_credentials`](/docs/caddyfile/options#log-credentials) deaktiviert werden.


<a id="syntax"></a>
## Syntax

```caddy-d
log [<logger_name>] {
	hostnames <hostnames...>
	no_hostname
	output <writer_module> ...
	format <encoder_module> ...
	level  <level>
	sampling {
		interval   <duration>
		first      <number>
		thereafter <number>
	}
}
```

- **logger_name** <span id="logger_name"/> ist ein optionaler Override des Logger-Namens für diese Site.

  Standardmäßig wird automatisch ein Logger-Name generiert, z. B. `log0`, `log1` usw., abhängig von der Reihenfolge der Sites im Caddyfile. Das ist nur nützlich, wenn Sie zuverlässig aus einem anderen Logger, der in globalen Optionen definiert ist, auf die Ausgabe dieses Loggers verweisen möchten. Siehe [ein Beispiel](#multiple-outputs) unten.

- **hostnames** <span id="hostnames"/> ist ein optionaler Override der Hostnamen, für die dieser Logger gilt.

  Standardmäßig gilt der Logger für die Hostnamen des Site-Blocks, in dem er erscheint, also die Site-Adressen. Das ist nützlich, wenn Sie in einem [Wildcard-Site-Block](/docs/caddyfile/patterns#wildcard-certificates) unterschiedliche Logger pro Subdomain definieren möchten. Siehe [ein Beispiel](#wildcard-logs) unten.

- **no_hostname** <span id="no_hostname"/> verhindert, dass der Logger mit einem der Hostnamen des Site-Blocks verknüpft wird. Standardmäßig wird der Logger mit der [Site-Adresse](/docs/caddyfile/concepts#addresses) verknüpft, in der die Direktive `log` erscheint.

  Das ist nützlich, wenn Sie Requests abhängig von einer Bedingung, etwa Request-Pfad oder Methode, mit der Direktive [`log_name`](/docs/caddyfile/directives/log_name) in verschiedene Dateien loggen möchten.

- **output** <span id="output"/> konfiguriert, wohin Logs geschrieben werden. Siehe [`output`-Module](#output-modules) unten.

  Standard: `stderr`.

- **format** <span id="format"/> beschreibt, wie Logs kodiert oder formatiert werden. Siehe [`format`-Module](#format-modules) unten.

  Standard: `console`, wenn `stderr` als Terminal erkannt wird, sonst `json`.

- **level** <span id="level"/> ist das minimale Entry-Level, das geloggt wird. Standard: `INFO`.

  Beachten Sie, dass Access Logs derzeit nur Logs der Level `INFO` und `ERROR` ausgeben.

- **sampling** <span id="sampling"/> konfiguriert Log-Sampling, um das Log-Volumen zu reduzieren. Wenn Sampling angegeben ist, wird es aktiviert, wobei die untenstehenden Standards gelten. Weglassen deaktiviert Sampling.

  - **interval** ist das [Dauerfenster](/docs/conventions#durations), über das Sampling durchgeführt wird. Standard: `1s` (deaktiviert).

  - **first** gibt an, wie viele Logs innerhalb eines bestimmten Levels und einer bestimmten Message pro Intervall behalten werden. Standard: `100`.

  - **thereafter** gibt an, wie viele Logs in jedem Intervall nach den zuerst behaltenen Logs übersprungen werden. Standard: `100`.

  Zum Beispiel werden mit `interval 1s`, `first 5` und `thereafter 10` in jedem 10-Sekunden-Intervall die ersten 5 Log-Einträge behalten, danach wird innerhalb dieser Sekunde jeder 10. Log-Eintrag mit demselben Level und derselben Message durchgelassen.


<a id="output-modules"></a>
### Output-Module

Die Subdirektive **output** erlaubt es, anzupassen, wohin Logs geschrieben werden.

#### stderr

Standardfehler (Konsole, ist der Standard).

```caddy-d
output stderr
```

#### stdout

Standardausgabe (Konsole).

```caddy-d
output stdout
```

#### discard

Keine Ausgabe.

```caddy-d
output discard
```

#### file

Eine Datei. Standardmäßig werden Log-Dateien anhand ihrer Größe rotiert ("rolled"), um zu verhindern, dass Speicherplatz erschöpft wird.

Log-Rolling wird von [timberjack <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/DeRuina/timberjack) bereitgestellt.

<aside class="tip">

**Hinweis zum Neuladen von Log-Datei-Optionen:** Ein Server-Neustart ist erforderlich, um Konfigurationsänderungen auf eine bestimmte Output-Datei anzuwenden.
Die Änderungen werden beim Server-Reload nicht angewendet, außer Sie fügen einen neuen Log-Dateinamen hinzu.

</aside>

```caddy-d
output file <filename> {
	mode          <mode>
	roll_disabled
	roll_size     <size>
	roll_interval <duration>
	roll_minutes  <minutes...>
	roll_at	      <times...>
	roll_uncompressed
	roll_local_time
	roll_keep     <num>
	roll_keep_for <days>
	backup_time_format <format>
}
```

- **&lt;filename&gt;** ist der Pfad zur Log-Datei.

  Beim Rolling werden Dateien mit dem Template `<name>-<timestamp>-<reason>.log` umbenannt. Der Timestamp wird gemäß der Option [`backup_time_format`](#backup_time_format) formatiert. Der Grund ist entweder `size` oder `time`, je nachdem, was die Rotation ausgelöst hat. Wenn die Datei komprimiert wird, wird `.gz` an den Dateinamen angehängt.

   Wenn der Dateiname zum Beispiel `access.log` ist, könnte eine gerollte Datei `access-2026-01-30T22-15-42.123-size.log` heißen, wenn sie wegen der Größe rotiert wurde, oder `access-2025-01-30T00-00-00.000-time.log`, wenn sie wegen der Zeit rotiert wurde.

- **mode** <span id="mode"/> ist der Unix-Dateimodus bzw. die Berechtigungen für die Log-Datei. Der Modus besteht aus 1 bis 4 Oktalziffern (gleich dem numerischen Format, das der Unix-Befehl [chmod <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Chmod) akzeptiert, außer dass ein Modus nur aus Nullen als Standardmodus `600` interpretiert wird).

  Zum Beispiel würde `0600` den Modus auf `rw-,---,---` setzen (Lese-/Schreibzugriff für den Besitzer der Log-Datei und kein Zugriff für andere); `0640` würde den Modus auf `rw-,r--,---` setzen (Lese-/Schreibzugriff für den Besitzer, nur Lesezugriff für die Gruppe); `644` setzt den Modus auf `rw-,r--,r--` und gewährt Lese-/Schreibzugriff für den Besitzer der Log-Datei, aber nur Lesezugriff für Gruppenbesitzer und andere Benutzer.

- **roll_disabled** <span id="roll_disabled"/> deaktiviert Log-Rolling. Dies kann dazu führen, dass der Speicherplatz ausgeht; verwenden Sie es daher nur, wenn Ihre Log-Dateien auf andere Weise verwaltet werden.

- **roll_size** <span id="roll_size"/> ist die Größe, bei der die Log-Datei rotiert wird. Die aktuelle Implementierung unterstützt Megabyte-Auflösung; Bruchteile werden auf das nächste ganze Megabyte aufgerundet. Zum Beispiel wird `1.1MiB` auf `2MiB` aufgerundet.

  Dies ist immer aktiviert. Wenn ein Schreibvorgang in die Logs dazu führt, dass die Datei die angegebene Größe überschreitet, wird das Log sofort rotiert. Der Backup-Dateiname enthält `size` als Grund.

  Standard: `100MiB`

- **roll_interval** <span id="roll_interval"/> ist die maximale Dauer zwischen Log-Rotationen. Der Wert ist ein [Dauer-String](/docs/conventions#durations), nach dem die Log-Datei rotiert wird.

  Wenn aktiviert, wird die Datei beim nächsten Schreibvorgang in die Logs rotiert, nachdem diese Dauer seit der letzten Rotation vergangen ist. Der Backup-Dateiname enthält `time` als Grund.

  Beachten Sie: Wenn dies auf `24h` gesetzt ist, rotiert es nicht notwendigerweise um Mitternacht, sondern nach 24 Stunden seit der letzten Rotation. Wenn Rolling wegen der Größe erfolgt, ist die Zeit der nächsten Rotation gegenüber der vorherigen Rotation verschoben. Sie können stattdessen die Optionen `roll_at` oder `roll_minutes` verwenden, um zu bestimmten Zeiten zu rotieren.

  Standard: deaktiviert

- **roll_minutes** <span id="roll_minutes"/> ist eine Liste von Minutenwerten (0-59), zu denen die Log-Datei rotiert wird. Zum Beispiel würde `10 40` die Log-Datei jede Stunde alle 30 Minuten bei `xx:10` und `xx:40` rotieren. Rotationen sind auf die Uhrminute ausgerichtet (Sekunde 0).

  Das Aktivieren startet einen goroutine-Timer, der eine Log-Rotation zu den angegebenen Minutenwerten auslöst (führt also eine kleine Menge Hintergrundverarbeitung ein). Dies arbeitet zusätzlich zu `roll_interval` und `roll_size`. Der Backup-Dateiname enthält `time` als Grund.

  Standard: deaktiviert

- **roll_at** <span id="roll_at"/> ist eine Liste von Zeitwerten (im 24-Stunden-Format), zu denen die Log-Datei rotiert wird. Zum Beispiel würde `00:00 12:00` die Log-Datei zweimal täglich um Mitternacht und um zwölf Uhr rotieren. Rotationen sind auf die Uhrminute ausgerichtet (Sekunde 0).

  Das Aktivieren startet einen goroutine-Timer, der eine Log-Rotation zu den angegebenen Zeiten auslöst (führt also eine kleine Menge Hintergrundverarbeitung ein). Dies arbeitet zusätzlich zu `roll_interval` und `roll_size`. Der Backup-Dateiname enthält `time` als Grund.

  Standard: deaktiviert

- **roll_uncompressed** <span id="roll_uncompressed"/> schaltet gzip-Log-Kompression aus.

  Standard: `gzip`-Kompression ist aktiviert.

- **roll_local_time** <span id="roll_local_time"/> legt fest, dass Rolling lokale Zeitstempel in Dateinamen verwendet.
  Standard: verwendet UTC-Zeit.

- **roll_keep** <span id="roll_keep"/> gibt an, wie viele Log-Dateien behalten werden, bevor die ältesten gelöscht werden. Wird ausgelöst, wenn eine neue Log-Datei erstellt wird.

  Standard: `10`

- **roll_keep_for** <span id="roll_keep_for"/> gibt an, wie lange gerollte Dateien als [Dauer-String](/docs/conventions#durations) behalten werden. Wird ausgelöst, wenn eine neue Log-Datei erstellt wird.
  Die aktuelle Implementierung unterstützt Tagesauflösung; Bruchteile werden auf den nächsten ganzen Tag aufgerundet. Zum Beispiel wird `36h` (1,5 Tage) auf `48h` (2 Tage) aufgerundet.
  
  Standard: `2160h` (90 Tage)

- **backup_time_format** <span id="backup_time_format"/> ist das Zeitformat für Backup-Dateinamen. Es muss ein gültiger Time-Layout-String sein; vollständige Details finden Sie in der [Go-Dokumentation](https://pkg.go.dev/time#pkg-constants).

  Standard: `2006-01-02T15-04-05`


#### net

Ein Netzwerk-Socket. Wenn der Socket ausfällt, schreibt er Logs nach stderr, während er versucht, die Verbindung wiederherzustellen.

```caddy-d
output net <address> {
	dial_timeout <duration>
	soft_start
}
```

- **&lt;address&gt;** ist die [Adresse](/docs/conventions#network-addresses), an die Logs geschrieben werden.

- **dial_timeout** <span id="dial_timeout"/> gibt an, wie lange auf eine erfolgreiche Verbindung zum Log-Socket gewartet wird. Log-Ausgaben können bis zu dieser Dauer blockiert werden, wenn der Socket ausfällt.

- **soft_start** <span id="soft_start"/> ignoriert Fehler beim Verbinden mit dem Socket, sodass Sie Ihre Konfiguration laden können, auch wenn der entfernte Log-Dienst ausgefallen ist. Logs werden stattdessen nach stderr ausgegeben.


<a id="format-modules"></a>
### Format-Module

Die Subdirektive **format** erlaubt es, anzupassen, wie Logs kodiert (formatiert) werden. Sie erscheint innerhalb eines `log`-Blocks.

<aside class="tip">

**Hinweis zum Common Log Format (CLF):** CLF kollidiert mit modernen strukturierten Logs. Um Ihre Access Logs in das deprecated Common Log Format umzuwandeln, verwenden Sie bitte das Plugin [`transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder).

</aside>


Zusätzlich zur Syntax jedes einzelnen Encoders können diese gemeinsamen Eigenschaften bei den meisten Encodern gesetzt werden:

```caddy-d
format <encoder_module> {
	message_key     <key>
	level_key       <key>
	time_key        <key>
	name_key        <key>
	caller_key      <key>
	stacktrace_key  <key>
	line_ending     <char>
	time_format     <format>
	time_local
	duration_format <format>
	level_format    <format>
}
```

- **message_key** <span id="message_key"/> Der Schlüssel für das Message-Feld des Log-Eintrags. Standard: `msg`

- **level_key** <span id="level_key"/> Der Schlüssel für das Level-Feld des Log-Eintrags. Standard: `level`

- **time_key** <span id="time_key"/> Der Schlüssel für das Zeitfeld des Log-Eintrags. Standard: `ts`
- **name_key** <span id="name_key"/> Der Schlüssel für das Namensfeld des Log-Eintrags. Standard: `name`

- **caller_key** <span id="caller_key"/> Der Schlüssel für das Caller-Feld des Log-Eintrags.

- **stacktrace_key** <span id="stacktrace_key"/> Der Schlüssel für das Stacktrace-Feld des Log-Eintrags.

- **line_ending** <span id="line_ending"/> Die zu verwendenden Zeilenenden.

- **time_format** <span id="time_format"/> Das Format für Zeitstempel.
  Standard: `wall_milli`, wenn das Format standardmäßig `console` ist, sonst `unix_seconds_float`.
  
  Kann einer der folgenden Werte sein:
  - `unix_seconds_float` Gleitkommazahl der Sekunden seit der Unix-Epoche.
  - `unix_milli_float` Gleitkommazahl der Millisekunden seit der Unix-Epoche.
  - `unix_nano` Ganze Zahl der Nanosekunden seit der Unix-Epoche.
  - `iso8601` Beispiel: `2006-01-02T15:04:05.000Z0700`
  - `rfc3339` Beispiel: `2006-01-02T15:04:05Z07:00`
  - `rfc3339_nano` Beispiel: `2006-01-02T15:04:05.999999999Z07:00`
  - `wall` Beispiel: `2006/01/02 15:04:05`
  - `wall_milli` Beispiel: `2006/01/02 15:04:05.000`
  - `wall_nano` Beispiel: `2006/01/02 15:04:05.000000000`
  - `common_log` Beispiel: `02/Jan/2006:15:04:05 -0700`
  - Oder jeder kompatible Time-Layout-String; vollständige Details finden Sie in der [Go-Dokumentation](https://pkg.go.dev/time#pkg-constants).
  
  Beachten Sie, dass die Teile des Format-Strings spezielle Konstanten für das Layout sind; `2006` ist also das Jahr, `01` der Monat, `Jan` der Monat als String, `02` der Tag. Verwenden Sie im Format-String nicht die tatsächlichen aktuellen Datumszahlen.

- **time_local** <span id="time_local"/> Loggt mit der lokalen Systemzeit statt mit der Standardzeit UTC.

- **duration_format** <span id="duration_format"/> Das Format für Dauern.

  Standard: `seconds`.
  
  Kann einer der folgenden Werte sein:
  - `s`, `second` oder `seconds` Gleitkommazahl der verstrichenen Sekunden.
  - `ms`, `milli` oder `millis` Gleitkommazahl der verstrichenen Millisekunden.
  - `ns`, `nano` oder `nanos` Ganze Zahl der verstrichenen Nanosekunden.
  - `string` Verwendet Gos eingebautes String-Format, zum Beispiel `1m32.05s` oder `6.31ms`.

- **level_format** <span id="level_format"/> Das Format für Level.

  Standard: `color`, wenn das Format standardmäßig `console` ist, sonst `lower`.
  
  Kann einer der folgenden Werte sein:
  - `lower` Kleinschreibung.
  - `upper` Großschreibung.
  - `color` Großschreibung mit ANSI-Farben.
  

#### console

Der console-Encoder formatiert den Log-Eintrag menschenlesbar und erhält dabei etwas Struktur.

```caddy-d
format console
```

#### json

Formatiert jeden Log-Eintrag als JSON-Objekt.

```caddy-d
format json
```


#### filter

Erlaubt feldweises Filtern.

```caddy-d
format filter {
	fields {
		<field> <filter> ...
	}
	<field> <filter> ...
	wrap <encode_module> ...
}
```

Verschachtelte Felder können mit `>` als Darstellung einer Verschachtelungsebene referenziert werden. Mit anderen Worten: Bei einem Objekt wie `{"a":{"b":0}}` kann das innere Feld als `a>b` referenziert werden.

Die folgenden Felder sind grundlegend für das Log und können nicht gefiltert werden, weil sie von der zugrunde liegenden Logging-Bibliothek als Spezialfälle hinzugefügt werden: `ts`, `level`, `logger` und `msg`.

`wrap` ist optional; wenn es weggelassen wird, wird ein Standard gewählt, abhängig davon, ob das aktuelle Output-Modul [`stderr`](#stderr) oder [`stdout`](#stdout) ist und ein interaktives Terminal ist. In diesem Fall wird [`console`](#console) gewählt, andernfalls [`json`](#json).

Als Kurzform kann der `fields`-Block weggelassen werden und die Filter können direkt innerhalb des `filter`-Blocks angegeben werden.


Dies sind die verfügbaren Filter:

##### delete

Markiert ein Feld, sodass es beim Kodieren übersprungen wird.

```caddy-d
<field> delete
```


##### rename

Benennt den Schlüssel eines Log-Felds um.

```caddy-d
<field> rename <key>
```


##### replace

Markiert ein Feld, sodass es zur Encoding-Zeit durch den bereitgestellten String ersetzt wird.

```caddy-d
<field> replace <replacement>
```


<a id="ip-mask"></a>
##### ip_mask

Maskiert IP-Adressen im Feld mit einer CIDR-Maske, d. h. mit der Anzahl von Bits der IP, die von links beginnend behalten werden. Wenn das Feld ein Array von Strings ist (z. B. HTTP-Header), wird jeder Wert im Array maskiert. Der Wert kann ein kommagetrennter String von IP-Adressen sein.

Für IPv4- und IPv6-Adressen gibt es getrennte Konfiguration, weil sie eine unterschiedliche Gesamtzahl von Bits haben.

Am häufigsten werden diese Felder gefiltert:
- `request>remote_ip` für den direkt verbindenden Client
- `request>client_ip` für den geparsten "real client", wenn [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) konfiguriert ist
- `request>headers>X-Forwarded-For`, wenn hinter einem Reverse Proxy

```caddy-d
<field> ip_mask [<ipv4> [<ipv6>]] {
	ipv4 <cidr>
	ipv6 <cidr>
}
```


##### query

Markiert ein Feld, sodass eine oder mehrere Aktionen ausgeführt werden, um den Query-Teil eines URL-Felds zu manipulieren. Am häufigsten ist das zu filternde Feld `request>uri`.

```caddy-d
<field> query {
	delete  <key>
	replace <key> <replacement>
	hash    <key>
}
```

Die verfügbaren Aktionen sind:

- **delete** entfernt den angegebenen Schlüssel aus der Query.

- **replace** ersetzt den Wert des angegebenen Query-Schlüssels durch **replacement**. Nützlich, um einen Redaction-Platzhalter einzufügen; Sie sehen, dass der Query-Schlüssel in der URL war, aber der Wert ist verborgen.

- **hash** ersetzt den Wert des angegebenen Query-Schlüssels durch die ersten 4 Bytes des SHA-256-Hashs des Werts, klein hexadezimal. Nützlich, um den Wert zu verschleiern, falls er sensibel ist, während weiterhin erkennbar bleibt, ob jeder Request einen anderen Wert hatte.


##### cookie

Markiert ein Feld, sodass eine oder mehrere Aktionen ausgeführt werden, um den Wert eines `Cookie`-HTTP-Headers zu manipulieren. Am häufigsten ist das zu filternde Feld `request>headers>Cookie`.

```caddy-d
<field> cookie {
	delete  <name>
	replace <name> <replacement>
	hash    <name>
}
```

Die verfügbaren Aktionen sind:

- **delete** entfernt das angegebene Cookie anhand des Namens aus dem Header.

- **replace** ersetzt den Wert des angegebenen Cookies durch **replacement**. Nützlich, um einen Redaction-Platzhalter einzufügen; Sie sehen, dass das Cookie im Header war, aber der Wert ist verborgen.

- **hash** ersetzt den Wert des angegebenen Cookies durch die ersten 4 Bytes des SHA-256-Hashs des Werts, klein hexadezimal. Nützlich, um den Wert zu verschleiern, falls er sensibel ist, während weiterhin erkennbar bleibt, ob jeder Request einen anderen Wert hatte.

Wenn viele Aktionen für denselben Cookie-Namen definiert sind, wird nur die erste Aktion angewendet.


##### regexp

Markiert ein Feld, sodass zur Encoding-Zeit eine Ersetzung per regulärem Ausdruck angewendet wird. Wenn das Feld ein Array von Strings ist (z. B. HTTP-Header), werden Ersetzungen auf jeden Wert im Array angewendet.

```caddy-d
<field> regexp <pattern> <replacement>
```

Die verwendete Sprache für reguläre Ausdrücke ist RE2, enthalten in Go. Siehe die [RE2-Syntaxreferenz](https://github.com/google/re2/wiki/Syntax) und die [Übersicht zur Go-regexp-Syntax](https://pkg.go.dev/regexp/syntax).

Im Ersatzstring können Capture Groups mit `${group}` referenziert werden, wobei `group` entweder der Name oder die Nummer der Capture Group im Ausdruck ist. Capture Group `0` ist der vollständige regexp-Match, `1` ist die erste Capture Group, `2` die zweite usw.


##### hash

Markiert ein Feld, sodass es zur Encoding-Zeit durch die ersten 4 Bytes (8 Hex-Zeichen) des SHA-256-Hashs des Werts ersetzt wird. Wenn das Feld ein String-Array ist (z. B. HTTP-Header), wird jeder Wert im Array gehasht.

Nützlich, um den Wert zu verschleiern, falls er sensibel ist, während weiterhin erkennbar bleibt, ob jeder Request einen anderen Wert hatte.

```caddy-d
<field> hash
```

#### append

Hängt Feld(er) an alle Log-Einträge an.

```caddy-d
format append {
	fields {
		<field> <value>
	}
	<field> <value>
	wrap <encode_module> ...
}
```

Am nützlichsten ist dies zum Hinzufügen von Informationen über die Caddy-Instanz, die die Log-Einträge erzeugt, möglicherweise über eine Umgebungsvariable. Die Feldwerte dürfen globale Platzhalter sein (z. B. `{env.*}`), aber wegen des Schreibens von Logs außerhalb des HTTP-Request-Kontexts *keine* per-request-Platzhalter.

`wrap` ist optional; wenn es weggelassen wird, wird ein Standard gewählt, abhängig davon, ob das aktuelle Output-Modul [`stderr`](#stderr) oder [`stdout`](#stdout) ist und ein interaktives Terminal ist. In diesem Fall wird [`console`](#console) gewählt, andernfalls [`json`](#json).

Der `fields`-Block kann weggelassen werden, und die Felder können direkt innerhalb des `append`-Blocks angegeben werden.



<a id="examples"></a>
## Beispiele

Access Logging zum Standard-Logger aktivieren.

Mit anderen Worten: Standardmäßig wird nach `stderr` geloggt, aber dies kann geändert werden, indem der Logger `default` mit der [globalen Option `log`](/docs/caddyfile/options#log) neu konfiguriert wird:

```caddy
example.com {
	log
}
```


Logs in eine Datei schreiben (mit Log-Rolling, das standardmäßig aktiviert ist):

```caddy
example.com {
	log {
		output file /var/log/access.log
	}
}
```


Log-Rolling anpassen: täglich um Mitternacht oder wenn die Log-Datei 1 GB erreicht (was zuerst eintritt) rotieren und 5 gerollte Dateien oder 30 Tage Logs behalten:

```caddy
example.com {
	log {
		output file /var/log/access.log {
			roll_at 00:00
			roll_size 1gb
			roll_keep 5
			roll_keep_for 720h
		}
	}
}
```


Den Request-Header `User-Agent` aus den Logs löschen:

```caddy
example.com {
	log {
		format filter {
			request>headers>User-Agent delete
		}
	}
}
```


Mehrere sensible Cookies redigieren. (Beachten Sie, dass einige sensible Header standardmäßig mit leeren Werten geloggt werden; siehe die globale Option [`log_credentials`](/docs/caddyfile/options#log-credentials), um das Logging von `Cookie`-Header-Werten zu aktivieren):

```caddy
example.com {
	log {
		format filter {
			request>headers>Cookie cookie {
				replace session REDACTED
				delete secret
			}
		}
	}
}
```


Die Remote-Adresse aus dem Request maskieren und die ersten 16 Bits (d. h. 255.255.0.0) für IPv4-Adressen sowie die ersten 32 Bits von IPv6-Adressen behalten.

Beachten Sie, dass seit Caddy v2.7 sowohl `remote_ip` als auch `client_ip` geloggt werden, wobei `client_ip` die "real IP" ist, wenn [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) konfiguriert ist:

```caddy
example.com {
	log {
		format filter {
			request>remote_ip ip_mask 16 32
			request>client_ip ip_mask 16 32
		}
	}
}
```


Eine Server-ID aus einer Umgebungsvariable an alle Log-Einträge anhängen und dies mit einem `filter` verketten, der einen Header löscht:

```caddy
example.com {
	log {
		format append {
			server_id {env.SERVER_ID}
			wrap filter {
				request>headers>Cookie delete
			}
		}
	}
}
```


<span id="wildcard-logs" /> Um getrennte Log-Dateien für jede Subdomain in einem [Wildcard-Site-Block](/docs/caddyfile/patterns#wildcard-certificates) zu schreiben, indem `hostnames` für jeden Logger überschrieben wird. Dies verwendet ein [Snippet](/docs/caddyfile/concepts#snippets), um Wiederholung zu vermeiden:

```caddy
(subdomain-log) {
	log {
		hostnames {args[0]}
		output file /var/log/{args[0]}.log
	}
}

*.example.com {
	import subdomain-log foo.example.com
	@foo host foo.example.com
	handle @foo {
		respond "foo"
	}

	import subdomain-log bar.example.com
	@bar host bar.example.com
	handle @bar {
		respond "bar"
	}
}
```

<span id="multiple-outputs" /> Um die Access Logs für eine bestimmte Subdomain in zwei verschiedene Dateien mit unterschiedlichen Formaten zu schreiben (eine mit dem Plugin [`transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder), die andere mit [`json`](#json)).

Dies funktioniert, indem der Logger-Name im Site-Block als `foo` überschrieben wird und die von diesem Logger erzeugten Access Logs anschließend in den zwei Loggern in den globalen Optionen mit `include http.log.access.foo` eingebunden werden:

```caddy
{
	log access-formatted {
		include http.log.access.foo
		output file /var/log/access-foo.log
		format transform "{common_log}"
	}

	log access-json {
		include http.log.access.foo
		output file /var/log/access-foo.json
		format json
	}
}

foo.example.com {
	log foo
}
```

<span id="sampling-example" /> Um das Log-Volumen mit Sampling zu reduzieren, zum Beispiel um die ersten 5 Requests pro Sekunde zu behalten und danach 1 von jeweils 10 Requests:

```caddy
example.com {
	log {
		sampling {
			interval   1s
			first      5
			thereafter 10
		}
	}
}
```
