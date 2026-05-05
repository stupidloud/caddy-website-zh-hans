---
title: abort (Caddyfile directive)
---

# abort

Verhindert jede Response an den Client, indem die HTTP-Handler-Kette sofort abgebrochen und die Verbindung geschlossen wird. Alle gleichzeitig aktiven HTTP-Streams auf derselben Verbindung werden unterbrochen.


<a id="syntax"></a>
## Syntax

```caddy-d
abort [<matcher>]
```

<a id="examples"></a>
## Beispiele

Eine Verbindung für unbekannte Domains zwangsweise schließen, wenn ein Wildcard-Zertifikat verwendet wird:

```caddy
*.example.com {
    @foo host foo.example.com
    handle @foo {
        respond "This is foo!" 200
    }

    handle {
		# Nicht behandelte Domains landen hier,
		# aber wir wollen ihre Requests nicht annehmen
        abort
    }
}
```
