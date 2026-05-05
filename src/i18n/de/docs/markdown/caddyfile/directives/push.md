---
title: push (Caddyfile directive)
---

# push

Konfiguriert den Server so, dass er Ressourcen per HTTP/2 Server Push vorab an den Client sendet.

Ressourcen können für Server Push verknüpft werden, indem die Link-Header der Antwort angegeben werden. Diese Direktive pusht automatisch Ressourcen, die von Upstream-Link-Headern in diesen Formaten beschrieben werden:

- `<resource>; as=script`
- `<resource>; as=script,<resource>; as=style`
- `<resource>; nopush`
- `<resource>;<resource2>;...`

wobei `<resource>` mit einem Slash `/` beginnt (also ein URI-Pfad mit demselben Host ist). Nur Ressourcen vom selben Host können gepusht werden. Wenn eine verknüpfte Ressource extern ist oder das Attribut `nopush` hat, wird sie nicht gepusht.

Standardmäßig enthalten Push-Anfragen einige Header, die als sicher zum Kopieren aus der ursprünglichen Anfrage gelten:

- Accept-Encoding
- Accept-Language
- Accept
- Cache-Control
- User-Agent

da angenommen wird, dass viele Anfragen ohne diese Header fehlschlagen würden; sie müssen nicht manuell konfiguriert werden.

Push-Anfragen werden intern virtualisiert und sind daher sehr leichtgewichtig.


<a id="syntax"></a>
## Syntax

```caddy-d
push [<matcher>] [<resource>] {
	[GET|HEAD] <resource>
	headers {
		[+]<field> [<value|regexp> [<replacement>]]
		-<field>
	}
}
```

- **&lt;resource&gt;** ist der Ziel-URI-Pfad, der gepusht werden soll. Wird er innerhalb des Blocks verwendet, kann optional die Methode davor stehen (GET oder POST; GET ist Standard).
- **&lt;headers&gt;** manipuliert die Header der Push-Anfrage mit derselben Syntax wie die [`header`-Direktive](/docs/caddyfile/directives/header). Einige Header werden standardmäßig übernommen und müssen nicht ausdrücklich konfiguriert werden (siehe oben).



<a id="examples"></a>
## Beispiele

Alle Ressourcen pushen, die von `Link`-Headern in der Antwort beschrieben werden:

```caddy-d
push
```

Dasselbe, aber zusätzlich `/resources/style.css` für alle Anfragen pushen:

```caddy-d
push * /resources/style.css
```

`/foo.jpg` nur pushen, wenn der Client `/foo.html` anfordert:

```caddy-d
push /foo.html /foo.jpg
```
