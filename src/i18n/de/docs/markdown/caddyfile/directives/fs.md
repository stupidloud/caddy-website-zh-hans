---
title: fs (Caddyfile directive)
---

# fs

Legt fest, welches Dateisystem für Datei-I/O verwendet werden soll.

Damit können Sie zum Beispiel ein entferntes Dateisystem in der Cloud anbinden, eine Datenbank mit dateiähnlicher Schnittstelle verwenden oder sogar aus Dateien lesen, die in die Caddy-Binärdatei eingebettet sind.

Zuerst müssen Sie mit der [globalen Option `filesystem`](/docs/caddyfile/options#filesystem) einen Dateisystemnamen deklarieren; danach können Sie mit dieser Direktive angeben, welches Dateisystem verwendet werden soll.

Diese Direktive wird häufig zusammen mit der Direktive [`file_server`](file_server) verwendet, um statische Dateien auszuliefern, oder mit der Direktive [`try_files`](try_files), um Rewrites anhand der Existenz von Dateien auszuführen. Typischerweise wird sie außerdem mit der Direktive [`root`](root) genutzt, um den Root-Pfad innerhalb des Dateisystems festzulegen.


<a id="syntax"></a>
## Syntax

```caddy-d
fs [<matcher>] <filesystem>
```

<a id="examples"></a>
## Beispiele

Ein Dateisystem namens `foo` verwenden, mit einem imaginären Modul namens `custom`, das möglicherweise Authentifizierung benötigt:

```caddy
{
	filesystem foo custom {
		api_key abc123
	}
}

example.com {
	fs foo
	root /srv
	file_server
}
```

Nur Bilder aus dem Dateisystem `foo` ausliefern und den Rest aus dem Standard-Dateisystem:

```caddy
example.com {
	fs /images* foo
	root /srv
	file_server
}
```
