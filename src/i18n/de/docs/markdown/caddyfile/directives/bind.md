---
title: bind (Caddyfile directive)
---

# bind

Überschreibt das Interface, an das der Socket des Servers gebunden werden soll.

Normalerweise bindet der Listener an das leere (Wildcard-)Interface. Sie können den Listener jedoch zwingen, stattdessen an einen anderen Hostnamen oder eine andere IP zu binden. Diese Direktive akzeptiert nur einen Host, keinen Port. Der Port wird durch die [Site-Adresse](/docs/caddyfile/concepts#addresses) bestimmt (standardmäßig `443`).

Beachten Sie, dass inkonsistentes Binden von Sites unbeabsichtigte Folgen haben kann. Wenn zum Beispiel zwei Sites auf demselben Port zu `127.0.0.1` auflösen und nur eine dieser Sites mit `bind 127.0.0.1` konfiguriert ist, ist nur eine Site erreichbar, weil die andere ohne spezifischen Host an den Port bindet; das Betriebssystem wählt den spezifischer passenden Socket. (Virtuelle Hosts werden nicht über verschiedene Listener hinweg geteilt.)

`bind` akzeptiert [Netzwerkadressen](/docs/conventions#network-addresses), darf aber keinen Port enthalten.


<a id="syntax"></a>
## Syntax

```caddy-d
bind <hosts...>
```

- **&lt;hosts...&gt;** ist die Liste der Host-Interfaces, an die der Listener gebunden werden soll.


<a id="examples"></a>
## Beispiele

Um einen Socket nur auf der aktuellen Maschine erreichbar zu machen, binden Sie ihn an das Loopback-Interface (localhost):

```caddy
example.com {
	bind 127.0.0.1
}
```

IPv6 einbeziehen:

```caddy
example.com {
	bind 127.0.0.1 [::1]
}
```

An `10.0.0.1:8080` binden:

```caddy
example.com:8080 {
	bind 10.0.0.1
}
```

An einen Unix-Domain-Socket unter `/run/caddy` binden:

```caddy
example.com {
	bind unix//run/caddy
}
```

Die Dateiberechtigung so ändern, dass alle Benutzer schreiben können ([Standard](/docs/conventions#network-addresses) ist `0200`, also nur für den Besitzer schreibbar):

```caddy
example.com {
	bind unix//run/caddy|0222
}
```

Eine Domain an zwei verschiedene Interfaces binden, mit unterschiedlichen Responses:

```caddy
example.com {
	bind 10.0.0.1
	respond "One"
}

example.com {
	bind 10.0.0.2
	respond "Two"
}
```
