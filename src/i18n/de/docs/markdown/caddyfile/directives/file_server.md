---
title: file_server (Caddyfile directive)
---

<script>
ready(function() {
	// Inline-browse-Argument korrigieren
	for (let item of $$_('pre.chroma .s')) {
		if (item.innerText.includes('browse')) {
			const span = document.createElement('span');
			span.className = 'k';
			item.parentNode.insertBefore(span, item);
			span.appendChild(item);
			span.innerHTML = '<a href="#browse" style="color: inherit;" title="browse">browse</a>';
			break;
		}
	}

	// Wir fügen Links zu allen Subdirektiven hinzu, wenn ein passender Anker auf der Seite gefunden wird.
	addLinksToSubdirectives();
});
</script>

# file_server

Ein statischer Dateiserver, der echte und virtuelle Dateisysteme unterstützt. Er bildet Dateipfade, indem er den URI-Pfad des Requests an den [Root-Pfad der Site](root) anhängt.

Standardmäßig erzwingt er kanonische URIs; das bedeutet, dass HTTP-Weiterleitungen für Requests auf Verzeichnisse ausgegeben werden, die nicht mit einem abschließenden Slash enden (um ihn hinzuzufügen), oder für Requests auf Dateien, die einen abschließenden Slash haben (um ihn zu entfernen). Weiterleitungen werden jedoch nicht ausgegeben, wenn ein internes Rewrite das letzte Element des Pfads (den Dateinamen) verändert.

Am häufigsten wird die Direktive `file_server` zusammen mit der Direktive [`root`](root) verwendet, um den Datei-Root für die ganze Site zu setzen. Diese Direktive hat auch eine Subdirektive `root` (siehe unten), um den Root nur für diesen Handler zu setzen (nicht empfohlen). Beachten Sie, dass ein Site-Root keine Sandbox-Garantien bietet: Der Dateiserver verhindert zwar Directory Traversal über Pfadkomponenten, aber symbolische Links innerhalb des Roots können weiterhin Zugriffe außerhalb des Roots erlauben.

Wenn Fehler auftreten (z. B. Datei nicht gefunden `404`, Zugriff verweigert `403`), werden die Fehler-Routen aufgerufen. Verwenden Sie die Direktive [`handle_errors`](handle_errors), um Fehler-Routen zu definieren und eigene Fehlerseiten anzuzeigen.

Bei Verwendung von `browse` wird die Standardausgabe durch das HTML-Template erzeugt. Clients können die Verzeichnisauflistung auch als JSON oder Klartext anfordern, indem sie die Header `Accept: application/json` beziehungsweise `Accept: text/plain` verwenden. Die JSON-Ausgabe kann für Skripting nützlich sein, die Klartextausgabe für die Nutzung im Terminal.


<a id="syntax"></a>
## Syntax

```caddy-d
file_server [<matcher>] [browse] {
	fs            <backend...>
	root          <path>
	hide          <files...>
	index         <filenames...>
	browse        [<template_file>] {
		reveal_symlinks
		sort <sort_field> [<direction>]
		file_limit <number>
	}
	precompressed [<formats...>]
	status        <status>
	disable_canonical_uris
	pass_thru
}
```

- **fs** <span id="fs"/> gibt ein alternatives (möglicherweise virtuelles) Dateisystem an. Hier kann jedes Caddy-Modul im Namespace `caddy.fs` verwendet werden. Jeder Root-Pfad oder jedes Präfix wird weiterhin auf alternative Dateisystemmodule angewendet. Standardmäßig wird die lokale Festplatte verwendet.

	[`xcaddy`](/docs/build#xcaddy) v0.4.0 führt das [`--embed`-Flag](https://github.com/caddyserver/xcaddy#custom-builds) ein, um einen Dateisystembaum in den benutzerdefinierten Caddy-Build einzubetten, und registriert ein `fs`-Modul namens `embedded`, mit dem Ihre statische Site als Caddy-Executable verteilt werden kann.

- **root** <span id="root"/> setzt den Pfad zum Site-Root. Es ähnelt der Direktive [`root`](root), gilt aber nur für diese Dateiserver-Instanz und überschreibt jeden anderen Site-Root, der möglicherweise definiert wurde. Standard: `{http.vars.root}` oder das aktuelle Arbeitsverzeichnis. Hinweis: Diese Subdirektive ändert den Root nur für diesen Handler. Damit andere Direktiven (wie [`try_files`](try_files) oder [`templates`](templates)) denselben Site-Root kennen, verwenden Sie stattdessen die Direktive [`root`](root).

- **hide** <span id="hide"/> ist eine Liste von Dateien oder Ordnern, die verborgen werden sollen; wenn sie angefordert werden, tut der Dateiserver so, als existierten sie nicht. Akzeptiert Platzhalter und Glob-Muster. Beachten Sie, dass dies *Dateisystem*-Pfade sind, NICHT Request-Pfade. Anders gesagt: Relative Pfade verwenden das aktuelle Arbeitsverzeichnis als Basis, NICHT den Site-Root; und alle Pfade werden vor Vergleichen (wenn möglich) in ihre absolute Form umgewandelt. Wenn ein Dateiname oder Muster ohne Pfadtrenner angegeben wird, werden alle Dateien mit passendem Namen unabhängig von ihrem Speicherort verborgen; andernfalls wird erst ein Pfadpräfix-Match versucht und danach ein Glob-Match. Da dies eine Caddyfile-Konfiguration ist, werden die aktiven Konfigurationsdateien standardmäßig hinzugefügt. Hide-Vergleiche sind case-sensitive; auf case-insensitive Dateisystemen kann ein Request-Pfad mit anderer Groß-/Kleinschreibung trotzdem auf denselben Pfad auf der Festplatte auflösen, daher sollte `hide` nicht als Sicherheitsgrenze für sensible Pfade betrachtet werden.

- **index** <span id="index"/> ist eine Liste von Dateinamen, nach denen als Indexdateien gesucht wird. Standard: `index.html index.txt`

- **browse** <span id="browse"/> aktiviert Dateiauflistungen für Requests auf Verzeichnisse, die keine Indexdatei haben.

  - **<template_file>** <span id="template_file"/> ist eine optionale eigene Template-Datei für Verzeichnisauflistungen. Standard ist das Template, das mit dem Befehl `caddy file-server export-template` extrahiert werden kann; dieser gibt das Standardtemplate auf stdout aus. Das eingebettete Template ist außerdem [hier im Quellcode ![external link](/old/resources/images/external-link.svg)](https://github.com/caddyserver/caddy/blob/master/modules/caddyhttp/fileserver/browse.html) verfügbar. Browse-Templates können auch Aktionen aus [dem standardmäßigen `templates`-Modul](/docs/modules/http.handlers.templates#docs) verwenden.

  - **reveal_symlinks** <span id="reveal_symlinks"/> aktiviert das Anzeigen der Ziele symbolischer Links in Verzeichnisauflistungen. Standardmäßig werden die Symlink-Ziele verborgen, und nur die Linkdatei selbst wird angezeigt.

  - **sort** <span id="sort"/> ändert die Standardsortierung für Verzeichnisauflistungen. Der erste Parameter ist das Feld bzw. die Spalte, nach der sortiert wird: `name`, `namedirfirst`, `size` oder `time`. Das zweite Argument ist eine optionale Richtung: `asc` oder `desc`. Beispiel: `sort name desc` sortiert nach Name in absteigender Reihenfolge.

  - **file_limit** <span id="file_limit"/> setzt die maximale Anzahl an Dateien, die in Verzeichnisauflistungen angezeigt werden. Standard: `10000`. Wenn die Anzahl der Dateien diese Grenze überschreitet, werden nur die ersten N Dateien angezeigt, wobei N die angegebene Grenze ist.

- **precompressed** <span id="precompressed"/> ist die Liste der Encoding-Formate, nach denen bei vorkomprimierten Sidecar-Dateien gesucht wird. Die Argumente sind eine geordnete Liste von Encoding-Formaten, nach denen bei vorkomprimierten [Sidecar-Dateien](https://en.wikipedia.org/wiki/Sidecar_file) gesucht wird. Unterstützte Formate sind `gzip` (`.gz`), `zstd` (`.zst`) und `br` (`.br`). Wenn die Formate weggelassen werden, ist der Standard `br zstd gzip` (in dieser Reihenfolge).

  Alle Dateisuchen prüfen zuerst, ob die unkomprimierte Datei existiert. Sobald sie gefunden wurde, sucht Caddy nach Sidecar-Dateien mit der Dateiendung jedes aktivierten Formats. Wenn eine vorkomprimierte Sidecar-Datei gefunden wird, antwortet Caddy mit der vorkomprimierten Datei und setzt den `Content-Encoding`-Response-Header entsprechend. Andernfalls antwortet Caddy wie üblich mit der unkomprimierten Datei. Wenn die Direktive [`encode`](encode) aktiviert ist, kann sie die Response on-the-fly komprimieren, falls keine vorkomprimierte Datei vorhanden ist.

- **status** <span id="status"/> ist eine optionale Statuscode-Überschreibung, die beim Schreiben der Response verwendet wird. Besonders nützlich, wenn auf einen Request mit einer [eigenen Fehlerseite](handle_errors) geantwortet wird. Kann ein dreistelliger Statuscode sein, zum Beispiel: `404`. Platzhalter werden unterstützt. Standardmäßig ist der geschriebene Statuscode typischerweise `200` oder `206` für Partial Content.

- **disable_canonical_uris** <span id="disable_canonical_uris"/> deaktiviert das Standardverhalten der Weiterleitung (einen abschließenden Slash hinzufügen, wenn der Request-Pfad ein Verzeichnis ist, oder den abschließenden Slash entfernen, wenn der Request-Pfad eine Datei ist). Beachten Sie, dass die Kanonisierung standardmäßig nicht stattfindet, wenn das letzte Element des Request-Pfads (der Dateiname) durch ein internes Rewrite verändert wurde, damit ein explizites Rewrite nicht durch implizites Verhalten überschrieben wird.

- **pass_thru** <span id="pass_thru"/> aktiviert den Pass-thru-Modus, der zum nächsten HTTP-Handler in der Route weiterläuft, wenn die angeforderte Datei nicht gefunden wird, statt einen `404`-Fehler auszulösen (und [`handle_errors`](handle_errors)-Routen aufzurufen). Praktisch ist das nur innerhalb eines [`route`](route)-Blocks mit weiteren Handler-Direktiven nach `file_server` nützlich, weil diese Direktive effektiv [als letzte geordnet ist](/docs/caddyfile/directives#directive-order).


<a id="examples"></a>
## Beispiele

Ein statischer Dateiserver aus dem aktuellen Verzeichnis:

```caddy-d
file_server
```

Mit aktivierten Dateiauflistungen:

```caddy-d
file_server browse
```

Nur statische Dateien innerhalb des Ordners `/static` ausliefern:

```caddy-d
file_server /static/*
```

Die Direktive `file_server` wird normalerweise mit der [`root`-Direktive](root) kombiniert, um den Root-Pfad festzulegen, aus dem Dateien ausgeliefert werden:

```caddy
example.com {
	root /srv
	file_server
}
```

<aside class="tip">

Wenn Sie Caddy als systemd-Service ausführen, funktioniert das Lesen von Dateien aus `/home` nicht, weil der Benutzer `caddy` keine "ausführbare" Berechtigung für das Verzeichnis `/home` hat (notwendig zum Durchlaufen). Es wird empfohlen, Ihre Dateien stattdessen in `/srv` oder `/var/www/html` abzulegen.

</aside>


Alle `.git`-Ordner und ihre Inhalte verbergen:

```caddy-d
file_server {
	hide .git
}
```

Wenn vom Client unterstützt (`Accept-Encoding`-Header), wird neben der angeforderten Datei geprüft, ob vorkomprimierte Dateien existieren. Wenn also `/path/to/file` angefordert wird, wird in dieser Reihenfolge nach `/path/to/file.br`, `/path/to/file.zst` und `/path/to/file.gz` gesucht und die erste verfügbare Datei mit entsprechendem `Content-Encoding` ausgeliefert:

```caddy-d
file_server {
	precompressed
}
```
