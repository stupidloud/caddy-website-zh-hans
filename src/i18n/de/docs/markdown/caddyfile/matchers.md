---
title: Request-Matcher (Caddyfile)
---

<script>
ready(function() {
	// Wir fügen Links auf die Matcher in den Codeblöcken hinzu,
	// die auf die zugehörigen Anker verweisen.
	let headers = Array.from($$_('article h3')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Matcher-Tokens anhand ihres Inhalts mit dem Syntaxabschnitt verlinken
	$$_('pre.chroma .nd').forEach(item => {
		let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
		let anchor = "named-matchers";
		if (text == "*") anchor = "wildcard-matchers";
		if (text.startsWith('/')) anchor = "path-matchers";
		item.innerHTML = `<a href="#${anchor}" style="color: inherit;" title="Matcher token">${text}</a>`;
	});
});
</script>

# Request-Matcher

**Request-Matcher** können verwendet werden, um Anfragen nach verschiedenen Kriterien zu filtern oder einzuordnen.

- [Syntax](#syntax)
	- [Beispiele](#examples)
	- [Wildcard-Matcher](#wildcard-matchers)
	- [Pfad-Matcher](#path-matchers)
	- [Benannte Matcher](#named-matchers)
- [Standard-Matcher](#standard-matchers)
	- [client_ip](#client-ip)
	- [expression](#expression)
	- [file](#file)
	- [header](#header)
	- [header_regexp](#header-regexp)
	- [host](#host)
	- [method](#method)
	- [not](#not)
	- [path](#path)
	- [path_regexp](#path-regexp)
	- [protocol](#protocol)
	- [query](#query)
	- [remote_ip](#remote-ip)
	- [vars](#vars)
	- [vars_regexp](#vars-regexp)


## Syntax

Im Caddyfile kann ein **Matcher-Token**, das direkt auf die Direktive folgt, den Gültigkeitsbereich dieser Direktive einschränken. Das Matcher-Token kann eine dieser Formen haben:

1. [**`*`**](#wildcard-matchers), um alle Anfragen zu matchen (Wildcard; Standard).
2. [**`/path`**](#path-matchers), beginnend mit einem Schrägstrich, um einen Anfragepfad zu matchen.
3. [**`@name`**](#named-matchers), um einen *benannten Matcher* anzugeben.

Wenn eine Direktive Matcher unterstützt, erscheint dies in ihrer Syntaxdokumentation als `[<matcher>]`. Matcher-Tokens sind [normalerweise optional](/docs/caddyfile/directives#syntax), gekennzeichnet durch `[ ]`. Wenn das Matcher-Token weggelassen wird, entspricht das einem Wildcard-Matcher (`*`).


<a id="examples"></a>
#### Beispiele

Diese Direktive gilt für [alle](#wildcard-matchers) HTTP-Anfragen:

```caddy-d
reverse_proxy localhost:9000
```

Und dies ist dasselbe (`*` ist hier nicht nötig):

```caddy-d
reverse_proxy * localhost:9000
```

Diese Direktive gilt aber nur für Anfragen mit einem [Pfad](#path-matchers), der mit `/api/` beginnt:

```caddy-d
reverse_proxy /api/* localhost:9000
```

Um auf etwas anderes als einen Pfad zu matchen, definiere einen [benannten Matcher](#named-matchers) und verweise mit `@name` darauf:

```caddy-d
@postfoo {
	method POST
	path /foo/*
}
reverse_proxy @postfoo localhost:9000
```




<a id="wildcard-matchers"></a>
### Wildcard-Matcher

Der Wildcard- (oder "Catch-all"-) Matcher `*` matcht alle Anfragen und wird nur benötigt, wenn ein Matcher-Token erforderlich ist. Wenn zum Beispiel das erste Argument, das du einer Direktive geben möchtest, zufällig ebenfalls ein Pfad ist, sähe es genauso aus wie ein Pfad-Matcher. In diesem Fall kannst du einen Wildcard-Matcher verwenden, um die Bedeutung eindeutig zu machen, zum Beispiel:

```caddy-d
root * /home/www/mysite
```

Ansonsten wird dieser Matcher nicht häufig verwendet. Im Allgemeinen empfehlen wir, ihn wegzulassen, wenn die Syntax ihn nicht verlangt.


<a id="path-matchers"></a>
### Pfad-Matcher

Das Matchen anhand des URI-Pfads ist die häufigste Art, Anfragen zu matchen, deshalb kann der Matcher inline angegeben werden:

```caddy-d
redir /old.html /new.html
```

Pfad-Matcher-Tokens müssen mit einem Schrägstrich `/` beginnen.

**[Pfad-Matching](#path) ist standardmäßig ein exakter Match, kein Prefix-Match.** Für einen schnellen Prefix-Match musst du ein `*` anhängen. Beachte, dass `/foo*` sowohl auf `/foo` und `/foo/` als auch auf `/foobar` passt; möglicherweise möchtest du stattdessen `/foo/*`.


<a id="named-matchers"></a>
### Benannte Matcher

Alle Matcher, die keine Pfad- oder Wildcard-Matcher sind, müssen benannte Matcher sein. Das ist ein Matcher, der außerhalb einer bestimmten Direktive definiert wird und wiederverwendet werden kann.

Einen Matcher mit eindeutigem Namen zu definieren gibt dir mehr Flexibilität, weil du [beliebige verfügbare Matcher](#standard-matchers) zu einem Set kombinieren kannst:

```caddy-d
@name {
	...
}
```

oder, wenn das Set nur einen Matcher enthält, kannst du ihn in dieselbe Zeile schreiben:

```caddy-d
@name ...
```

Dann kannst du den Matcher verwenden, indem du ihn als erstes Argument einer Direktive angibst:

```caddy-d
directive @name
```

Zum Beispiel proxyt dies HTTP/1.1-WebSocket-Anfragen an `localhost:6001` und andere Anfragen an `localhost:8080`. Es matcht Anfragen, die ein Header-Feld namens `Connection` haben, das `Upgrade` *enthält*, **und** ein weiteres Feld namens `Upgrade` mit exakt `websocket`:

```caddy
example.com {
	@websockets {
		header Connection *Upgrade*
		header Upgrade    websocket
	}
	reverse_proxy @websockets localhost:6001

	reverse_proxy localhost:8080
}
```

Wenn das Matcher-Set nur aus einem Matcher besteht, funktioniert auch eine einzeilige Syntax:

```caddy-d
@post method POST
reverse_proxy @post localhost:6001
```

Als Sonderfall kann der [`expression`-Matcher](#expression) ohne Angabe seines Namens verwendet werden, solange ein [quoted](/docs/caddyfile/concepts#tokens-and-quotes) Argument (die CEL-Expression selbst) auf den Matcher-Namen folgt:

```caddy-d
@not-found `{err.status_code} == 404`
```

Wie Direktiven müssen Definitionen benannter Matcher in den [Site-Blöcken](/docs/caddyfile/concepts#structure) stehen, die sie verwenden.

Eine Definition eines benannten Matchers bildet ein *Matcher-Set*. Matcher in einem Set werden per AND verknüpft, d. h. alle müssen matchen. Wenn du zum Beispiel sowohl einen [`header`](#header)- als auch einen [`path`](#path)-Matcher im Set hast, müssen beide matchen.

Mehrere Matcher desselben Typs können mithilfe boolescher Algebra (AND/OR) zusammengeführt werden (z. B. mehrere [`path`](#path)-Matcher im selben Set), wie in den jeweiligen Abschnitten unten beschrieben.

Für komplexere boolesche Matching-Logik wird empfohlen, den [`expression`-Matcher](#expression) zu verwenden und eine CEL-Expression zu schreiben. Sie unterstützt **and** `&&`, **or** `||` und **Klammern** `( )`.





<a id="standard-matchers"></a>
## Standard-Matcher

Die vollständige Matcher-Dokumentation findest du [in der Dokumentation des jeweiligen Matcher-Moduls](/docs/json/apps/http/servers/routes/match/).

Anfragen können auf folgende Arten gematcht werden:



<a id="client-ip"></a>
### client_ip

```caddy-d
client_ip <ranges...>

expression client_ip('<ranges...>')
```

Anhand der Client-IP-Adresse. Akzeptiert genaue IPs oder CIDR-Bereiche. IPv6-Zonen werden unterstützt.

Dieser Matcher wird am besten verwendet, wenn die globale Option [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) konfiguriert ist; andernfalls verhält er sich identisch zum Matcher [`remote_ip`](#remote-ip). Nur bei Anfragen von vertrauenswürdigen Proxies wird die Client-IP zu Beginn der Anfrage geparst. Nicht vertrauenswürdige Anfragen verwenden die Remote-IP-Adresse des direkten Peers oder die per [PROXY-Protokoll](/docs/caddyfile/options#proxy-protocol) gesetzte Adresse.

Als Kurzform kann `private_ranges` verwendet werden, um alle privaten IPv4- und IPv6-Bereiche zu matchen. Das entspricht der Angabe all dieser Bereiche: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Pro benanntem Matcher kann es mehrere `client_ip`-Matcher geben; ihre Bereiche werden zusammengeführt und per OR verknüpft.

#### Beispiel:

Anfragen von privaten IPv4-Adressen matchen:

```caddy-d
@private-ipv4 client_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Dieser Matcher wird häufig mit dem [`not`](#not)-Matcher kombiniert, um den Match umzukehren. Zum Beispiel, um alle Verbindungen von *öffentlichen* IPv4- und IPv6-Adressen abzubrechen (also dem Gegenteil aller privaten Bereiche):

```caddy
example.com {
	@denied not client_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

In einer [CEL-Expression](#expression) sähe das so aus:

```caddy-d
@my-friends `client_ip('12.23.34.45', '23.34.45.56')`
```



### expression

```caddy-d
expression <cel...>
```

Anhand einer beliebigen [CEL (Common Expression Language)](https://github.com/google/cel-spec)-Expression, die `true` oder `false` zurückgibt.

Die meisten anderen Request-Matcher können in Expressions auch als Funktionen verwendet werden. Das erlaubt flexiblere boolesche Logik als außerhalb von Expressions. Die unterstützte Syntax innerhalb von CEL-Expressions findest du in der Dokumentation des jeweiligen Matchers.

Caddy-[Platzhalter](/docs/conventions#placeholders) (oder [Caddyfile-Kurzformen](/docs/caddyfile/concepts#placeholders)) können in diesen CEL-Expressions verwendet werden, da sie vorverarbeitet und in reguläre CEL-Funktionsaufrufe umgewandelt werden, bevor die CEL-Umgebung sie interpretiert. Wenn ein Platzhalter als String-Argument an eine Matcher-Funktion übergeben werden soll, muss die führende `{` mit einem Backslash `\` escaped werden, damit sie nicht vorverarbeitet wird, zum Beispiel `file('\{path}.md')`.

Der Einfachheit halber kann der Matcher-Name weggelassen werden, wenn ein benannter Matcher definiert wird, der ausschließlich aus einer CEL-Expression besteht. Die CEL-Expression muss [quoted](/docs/caddyfile/concepts#tokens-and-quotes) sein (Backticks oder Heredocs empfohlen). Das liest sich recht angenehm:

```caddy-d
@mutable `{method}.startsWith("P")`
```

In diesem Fall wird der CEL-Matcher angenommen.

#### Beispiele:

Anfragen matchen, deren Methoden mit `P` beginnen, z. B. `PUT` oder `POST`:

```caddy-d
@methods expression {method}.startsWith("P")
```

Anfragen matchen, bei denen der Handler den Fehlerstatuscode `404` zurückgegeben hat; dies würde zusammen mit der [`handle_errors`-Direktive](/docs/caddyfile/directives/handle_errors) verwendet:

```caddy-d
@404 expression {err.status_code} == 404
```

Anfragen matchen, bei denen der Pfad auf eine von zwei verschiedenen regulären Expressions passt. Das lässt sich nur mit einer Expression schreiben, weil der [`path_regexp`](#path-regexp)-Matcher normalerweise nur einmal pro benanntem Matcher existieren kann:

```caddy-d
@user expression path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')
```

Oder dasselbe ohne Matcher-Namen, in [Backticks](/docs/caddyfile/concepts#tokens-and-quotes) eingeschlossen, damit es als einzelnes Token geparst wird:

```caddy-d
@user `path_regexp('^/user/(\w*)') || path_regexp('^/(\w*)')`
```

Du kannst die [Heredoc-Syntax](/docs/caddyfile/concepts#heredocs) verwenden, um mehrzeilige CEL-Expressions zu schreiben:

```caddy-d
@api <<CEL
	{method} == "GET"
	&& {path}.startsWith("/api/")
	CEL
respond @api "Hello, API!"
```


---
### file

```caddy-d
file {
	root       <path>
	try_files  <files...>
	try_policy first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified
	split_path <delims...>
}
file <files...>

expression `file({
	'root': '<path>',
	'try_files': ['<files...>'],
	'try_policy': 'first_exist|first_exist_fallback|smallest_size|largest_size|most_recently_modified',
	'split_path': ['<delims...>']
})`
expression file('<files...>')
```

Anhand von Dateien.

- `root` definiert das Verzeichnis, in dem nach Dateien gesucht wird. Standard ist das aktuelle Arbeitsverzeichnis oder die [`root`-Variable](/docs/modules/http.handlers.vars) (`{http.vars.root}`), falls sie gesetzt ist (kann über die [`root`-Direktive](/docs/caddyfile/directives/root) gesetzt werden).

- `try_files` prüft Dateien in seiner Liste, die zur try_policy passen.

  Um Verzeichnisse zu matchen, hänge einen abschließenden Schrägstrich `/` an den Pfad an. Alle Dateipfade sind relativ zur [root](/docs/caddyfile/directives/root) der Site, und [Glob-Patterns](https://pkg.go.dev/path/filepath#Match) werden expandiert.

  Wenn die `try_policy` `first_exist` ist (der Standard), darf das letzte Element in der Liste eine mit `=` vorangestellte Zahl sein (z. B. `=404`). Als Fallback wird dann ein Fehler mit diesem Code ausgegeben; der Fehler kann mit [`handle_errors`](/docs/caddyfile/directives/handle_errors) abgefangen und behandelt werden.



- `try_policy` legt fest, wie eine Datei ausgewählt wird. Standard ist `first_exist`.

	- `first_exist` prüft, ob Dateien existieren. Die erste vorhandene Datei wird ausgewählt.

	- `first_exist_fallback` ähnelt `first_exist`, nimmt aber an, dass das letzte Element der Liste immer existiert, um einen Festplattenzugriff zu vermeiden.

	- `smallest_size` wählt die Datei mit der kleinsten Größe.

	- `largest_size` wählt die Datei mit der größten Größe.

	- `most_recently_modified` wählt die Datei, die zuletzt geändert wurde.

- `split_path` bewirkt, dass der Pfad am ersten Trennzeichen aus der Liste geteilt wird, das in jedem zu prüfenden Dateipfad gefunden wird. Für jeden Split-Wert ist die linke Seite des Splits einschließlich des Trennzeichens selbst der Dateipfad, der versucht wird. Zum Beispiel würde `/remote.php/dav/` mit dem Trennzeichen `.php` die Datei `/remote.php` versuchen. Jedes Trennzeichen muss am Ende einer URI-Pfadkomponente stehen, damit es als Split-Trennzeichen verwendet werden kann. Das ist eine Nischeneinstellung und wird hauptsächlich beim Ausliefern von PHP-Sites verwendet.

Da `try_files` mit der Policy `first_exist` so häufig ist, gibt es dafür eine einzeilige Kurzform:

```caddy-d
file <files...>
```

Ein leerer `file`-Matcher (einer, nach dem keine Dateien aufgelistet sind) prüft, ob die angeforderte Datei&mdash;wörtlich aus der URI, relativ zur [Site-root](/docs/caddyfile/directives/root)&mdash;existiert. Das ist praktisch dasselbe wie `file {path}`.


<aside class="tip">

Da Rewriting basierend auf der Existenz einer Datei auf der Festplatte so häufig ist, gibt es außerdem eine [`try_files`-Direktive](/docs/caddyfile/directives/try_files), die eine Kurzform des `file`-Matchers und eines [`rewrite`-Handlers](/docs/caddyfile/directives/rewrite) ist.

</aside>


Bei einem Match werden vier neue Platzhalter verfügbar:

- `{file_match.relative}` Der root-relative Pfad der Datei. Das ist beim Rewriting von Anfragen oft nützlich.
- `{file_match.absolute}` Der absolute Pfad der gematchten Datei, einschließlich root.
- `{file_match.type}` Der Dateityp, `file` oder `directory`.
- `{file_match.remainder}` Der nach dem Teilen des Dateipfads verbleibende Teil (wenn `split_path` konfiguriert ist)


#### Beispiele:

Anfragen matchen, bei denen der Pfad eine vorhandene Datei ist:

```caddy-d
@file file
```

Anfragen matchen, bei denen der Pfad mit angehängtem `.html` eine vorhandene Datei ist, oder andernfalls der Pfad selbst eine vorhandene Datei ist:

```caddy-d
@html file {
	try_files {path}.html {path} 
}
```

Dasselbe wie oben, aber mit der einzeiligen Kurzform und mit Fallback auf einen 404-Fehler, wenn keine Datei gefunden wird:

```caddy-d
@html-or-error file {path}.html {path} =404
```

Einige weitere Beispiele mit [CEL-Expressions](#expression). Beachte, dass Platzhalter vorverarbeitet und in reguläre CEL-Funktionsaufrufe umgewandelt werden, bevor die CEL-Umgebung sie interpretiert; deshalb wird hier Konkatenation verwendet. Außerdem muss wegen aktueller Parsing-Einschränkungen die Langform verwendet werden, wenn mit Platzhaltern konkateniert wird:

```caddy-d
@file `file()`
@first `file({'try_files': [{path}, {path} + '/', 'index.html']})`
@smallest `file({'try_policy': 'smallest_size', 'try_files': ['a.txt', 'b.txt']})`
```


---
### header

```caddy-d
header <field> [<value> ...]

expression header({'<field>': '<value>'})
```

Anhand von Anfrage-Header-Feldern.

- `<field>` ist der Name des zu prüfenden HTTP-Header-Felds.
	- Wenn `!` vorangestellt ist, darf das Feld für einen Match nicht existieren (Wertargument weglassen).
- `<value>` ist der Wert, den das Feld haben muss, damit es matcht. Einer oder mehrere können angegeben werden.
	- Wenn `*` vorangestellt ist, wird ein schneller Suffix-Match ausgeführt (erscheint am Ende).
	- Wenn `*` angehängt ist, wird ein schneller Prefix-Match ausgeführt (erscheint am Anfang).
	- Wenn es von `*` umschlossen ist, wird ein schneller Substring-Match ausgeführt (erscheint irgendwo).
	- Andernfalls ist es ein schneller exakter Match.

Unterschiedliche Header-Felder innerhalb desselben Sets werden per AND verknüpft. Mehrere Werte pro Feld werden per OR verknüpft.

Beachte, dass Header-Felder wiederholt werden und unterschiedliche Werte haben können. Backend-Anwendungen MÜSSEN berücksichtigen, dass Header-Feldwerte Arrays und keine Einzelwerte sind; Caddy interpretiert in solchen Zweifelsfällen keine Bedeutung.

#### Beispiel:

Anfragen matchen, deren `Connection`-Header `Upgrade` enthält:

```caddy-d
@upgrade header Connection *Upgrade*
```

Anfragen matchen, deren `Foo`-Header `bar` ODER `baz` enthält:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Anfragen matchen, die überhaupt kein `Foo`-Header-Feld haben:

```caddy-d
@not_foo header !Foo
```

Mit einer [CEL-Expression](#expression) WebSocket-Anfragen matchen, indem geprüft wird, ob der `Connection`-Header `Upgrade` enthält und der `Upgrade`-Header `websocket` entspricht (HTTP/2 hat dafür den `:protocol`-Header):

```caddy-d
@websockets `header({'Connection':'*Upgrade*','Upgrade':'websocket'}) || header({':protocol': 'websocket'})`
```


---
<a id="header-regexp"></a>
### header_regexp

```caddy-d
header_regexp [<name>] <field> <regexp>

expression header_regexp('<name>', '<field>', '<regexp>')
expression header_regexp('<field>', '<regexp>')
```

Wie [`header`](#header), unterstützt aber reguläre Expressions.

Die verwendete Sprache für reguläre Expressions ist RE2, das in Go enthalten ist. Siehe die [RE2-Syntaxreferenz](https://github.com/google/re2/wiki/Syntax) und die [Übersicht zur Go-regexp-Syntax](https://pkg.go.dev/regexp/syntax).

Ab v2.8.0 wird, wenn `name` *nicht* angegeben ist, der Name vom Namen des benannten Matchers übernommen. Zum Beispiel führt ein benannter Matcher `@foo` dazu, dass dieser Matcher `foo` heißt. Der Hauptvorteil eines ausdrücklich angegebenen Namens besteht darin, dass mehr als ein regexp-Matcher (z. B. `header_regexp` und [`path_regexp`](#path-regexp), oder mehrere unterschiedliche Header-Felder) im selben benannten Matcher verwendet werden kann.

Capture-Groups können nach dem Matching in Direktiven über [Platzhalter](/docs/caddyfile/concepts#placeholders) angesprochen werden:
- `{re.<name>.<capture_group>}`, wobei:
  - `<name>` der Name der regulären Expression ist,
  - `<capture_group>` entweder der Name oder die Nummer der Capture-Group in der Expression ist.

- `{re.<capture_group>}` ohne Namen wird der Einfachheit halber ebenfalls befüllt. Der Haken ist, dass bei mehreren nacheinander verwendeten regexp-Matchern die Platzhalterwerte vom nächsten Matcher überschrieben werden.

Capture-Group `0` ist der vollständige regexp-Match, `1` ist die erste Capture-Group, `2` die zweite usw. `{re.foo.1}` oder `{re.1}` enthalten also beide den Wert der ersten Capture-Group.

Pro Header-Feld wird nur eine reguläre Expression unterstützt, da regexp-Patterns nicht zusammengeführt werden können. Wenn du mehr brauchst, solltest du einen [`expression`-Matcher](#expression) verwenden. Matches gegen mehrere unterschiedliche Header-Felder werden per AND verknüpft.

#### Beispiel:

Anfragen matchen, deren Cookie-Header `login_` gefolgt von einem Hex-String enthält, mit einer Capture-Group, auf die über `{re.login.1}` oder `{re.1}` zugegriffen werden kann.

```caddy-d
@login header_regexp login Cookie login_([a-f0-9]+)
```

Dies kann vereinfacht werden, indem der Name weggelassen wird; er wird dann aus dem benannten Matcher abgeleitet:

```caddy-d
@login header_regexp Cookie login_([a-f0-9]+)
```

Oder dasselbe mit einer [CEL-Expression](#expression):

```caddy-d
@login `header_regexp('login', 'Cookie', 'login_([a-f0-9]+)')`
```



---
### host

```caddy-d
host <hosts...>

expression host('<hosts...>')
```

Matcht die Anfrage anhand ihres `Host`-Header-Felds.

Da die meisten Site-Blöcke Hosts bereits in der Adresse der Site angeben, wird dieser Matcher häufiger in Site-Blöcken verwendet, die einen Wildcard-Hostnamen nutzen (siehe das [Wildcard-Zertifikate-Pattern](/docs/caddyfile/patterns#wildcard-certificates)), bei denen aber hostnamenspezifische Logik erforderlich ist.

Mehrere `host`-Matcher werden per OR verknüpft.

#### Beispiel:

Eine Subdomain matchen:

```caddy-d
@sub host sub.example.com
```

Die Apex-Domain und eine Subdomain matchen:

```caddy-d
@site host example.com www.example.com
```

Mehrere Subdomains mit einer [CEL-Expression](#expression):

```caddy-d
@app `host('app1.example.com', 'app2.example.com')`
```



---
### method

```caddy-d
method <verbs...>

expression method('<verbs...>')
```

Anhand der Methode (Verb) der HTTP-Anfrage. Verben sollten großgeschrieben sein, wie `POST`. Kann eine oder mehrere Methoden matchen.

Mehrere `method`-Matcher werden per OR verknüpft.

#### Beispiele:

Anfragen mit der Methode `GET` matchen:

```caddy-d
@get method GET
```

Anfragen mit den Methoden `PUT` oder `DELETE` matchen:

```caddy-d
@put-delete method PUT DELETE
```

Read-only-Methoden mit einer [CEL-Expression](#expression) matchen:

```caddy-d
@read `method('GET', 'HEAD', 'OPTIONS')`
```



---
### not

```caddy-d
not <matcher>
```

oder, um mehrere per AND verknüpfte Matcher zu negieren, einen Block öffnen:

```caddy-d
not {
	<matchers...>
}
```

Die Ergebnisse der eingeschlossenen Matcher werden negiert.

#### Beispiele:

Anfragen mit Pfaden matchen, die NICHT mit `/css/` ODER `/js/` beginnen.

```caddy-d
@not-assets {
	not path /css/* /js/*
}
```

Anfragen matchen mit WEDER:
- einem `/api/`-Pfadpräfix, NOCH
- der Anfrage-Methode `POST`

d. h. sie dürfen keines davon haben, um zu matchen:

```caddy-d
@with-neither {
	not path /api/*
	not method POST
}
```

Anfragen OHNE BEIDES matchen:
- ein `/api/`-Pfadpräfix, UND
- die Anfrage-Methode `POST`

d. h. sie müssen entweder keines davon oder nur eines davon haben, um zu matchen:

```caddy-d
@without-both {
	not {
		path /api/*
		method POST
	}
}
```

Für diesen Matcher gibt es keine [CEL-Expression](#expression), weil du stattdessen den Operator `!` zur Negation verwenden kannst. Zum Beispiel:

```caddy-d
@without-both `!path('/api*') && !method('POST')`
```

Das ist mit Klammern dasselbe wie:

```caddy-d
@without-both `!(path('/api*') || method('POST'))`
```




---
### path

```caddy-d
path <paths...>

expression path('<paths...>')
```

Anhand des Anfragepfads (der Pfadkomponente der Anfrage-URI). Pfad-Matches sind exakt, aber nicht case-sensitive. Wildcards `*` können verwendet werden:

- Nur am Ende, für einen Prefix-Match (`/prefix/*`)
- Nur am Anfang, für einen Suffix-Match (`*.suffix`)
- Nur auf beiden Seiten, für einen Substring-Match (`*/contains/*`)
- Nur in der Mitte, für einen globartigen Match (`/accounts/*/info`)

Schrägstriche sind bedeutsam. Zum Beispiel passt `/foo*` auf `/foo`, `/foobar`, `/foo/` und `/foo/bar`, aber `/foo/*` passt *nicht* auf `/foo` oder `/foobar`.

Anfragepfade werden vor dem Matching bereinigt, um Directory-Traversal-Punkte aufzulösen. Außerdem werden mehrere Schrägstriche zusammengeführt, sofern das Match-Pattern nicht selbst mehrere Schrägstriche enthält. Anders gesagt: `/foo` passt auf `/foo` und `//foo`, aber `//foo` passt nur auf `//foo`.

Da es für jede gegebene URI mehrere escaped Formen gibt, wird der Anfragepfad normalisiert (URL-dekodiert, unescaped), außer bei Escape-Sequenzen an Positionen, an denen auch im Match-Pattern Escape-Sequenzen vorhanden sind. Zum Beispiel passt `/foo/bar` sowohl auf `/foo/bar` als auch auf `/foo%2Fbar`, aber `/foo%2Fbar` passt nur auf `/foo%2Fbar`, weil die Escape-Sequenz in der Konfiguration ausdrücklich angegeben ist.

Das spezielle Wildcard-Escape `%*` kann statt `*` verwendet werden, damit der gematchte Abschnitt escaped bleibt. Zum Beispiel passt `/bands/*/*` nicht auf `/bands/AC%2FDC/T.N.T`, weil der Pfad im normalisierten Raum verglichen wird, wo er wie `/bands/AC/DC/T.N.T` aussieht und nicht zum Pattern passt. `/bands/%*/*` passt jedoch auf `/bands/AC%2FDC/T.N.T`, weil der durch `%*` dargestellte Abschnitt ohne Dekodieren der Escape-Sequenzen verglichen wird.

Mehrere Pfade werden per OR verknüpft.

#### Beispiele:

Mehrere Verzeichnisse und deren Inhalte matchen:

```caddy-d
@assets path /js/* /css/* /images/*
```

Eine bestimmte Datei matchen:

```caddy-d
@favicon path /favicon.ico
```

Dateierweiterungen matchen:

```caddy-d
@extensions path *.js *.css
```

Mit einer [CEL-Expression](#expression):

```caddy-d
@assets `path('/js/*', '/css/*', '/images/*')`
```



---
<a id="path-regexp"></a>
### path_regexp

```caddy-d
path_regexp [<name>] <regexp>

expression path_regexp('<name>', '<regexp>')
expression path_regexp('<regexp>')
```

Wie [`path`](#path), unterstützt aber reguläre Expressions. Läuft gegen den URI-dekodierten/unescaped Pfad.

Die verwendete Sprache für reguläre Expressions ist RE2, das in Go enthalten ist. Siehe die [RE2-Syntaxreferenz](https://github.com/google/re2/wiki/Syntax) und die [Übersicht zur Go-regexp-Syntax](https://pkg.go.dev/regexp/syntax).

Ab v2.8.0 wird, wenn `name` *nicht* angegeben ist, der Name vom Namen des benannten Matchers übernommen. Zum Beispiel führt ein benannter Matcher `@foo` dazu, dass dieser Matcher `foo` heißt. Der Hauptvorteil eines ausdrücklich angegebenen Namens besteht darin, dass mehr als ein regexp-Matcher (z. B. `path_regexp` und [`header_regexp`](#header-regexp)) im selben benannten Matcher verwendet werden kann.

Capture-Groups können nach dem Matching in Direktiven über [Platzhalter](/docs/caddyfile/concepts#placeholders) angesprochen werden:
- `{re.<name>.<capture_group>}`, wobei:
  - `<name>` der Name der regulären Expression ist,
  - `<capture_group>` entweder der Name oder die Nummer der Capture-Group in der Expression ist.

- `{re.<capture_group>}` ohne Namen wird der Einfachheit halber ebenfalls befüllt. Der Haken ist, dass bei mehreren nacheinander verwendeten regexp-Matchern die Platzhalterwerte vom nächsten Matcher überschrieben werden.

Capture-Group `0` ist der vollständige regexp-Match, `1` ist die erste Capture-Group, `2` die zweite usw. `{re.foo.1}` oder `{re.1}` enthalten also beide den Wert der ersten Capture-Group.

Pro benanntem Matcher kann es nur ein `path_regexp`-Pattern geben, da dieser Matcher nicht mit sich selbst zusammengeführt werden kann. Wenn du mehr brauchst, solltest du einen [`expression`-Matcher](#expression) verwenden.

#### Beispiel:

Anfragen matchen, deren Pfad mit einem 6 Zeichen langen Hex-String endet, gefolgt von `.css` oder `.js` als Dateierweiterung, mit Capture-Groups (in `( )` eingeschlossene Teile), auf die entsprechend mit `{re.static.1}` und `{re.static.2}` (oder `{re.1}` und `{re.2}`) zugegriffen werden kann:

```caddy-d
@static path_regexp static \.([a-f0-9]{6})\.(css|js)$
```

Dies kann vereinfacht werden, indem der Name weggelassen wird; er wird dann aus dem benannten Matcher abgeleitet:

```caddy-d
@static path_regexp \.([a-f0-9]{6})\.(css|js)$
```

Oder dasselbe mit einer [CEL-Expression](#expression), wobei zusätzlich geprüft wird, dass die [`file`](#file) auf der Festplatte existiert:

```caddy-d
@static `path_regexp('\.([a-f0-9]{6})\.(css|js)$') && file()`
```



---
### protocol

```caddy-d
protocol http|https|grpc|http/<version>[+]

expression protocol('http|https|grpc|http/<version>[+]')
```

Anhand des Anfrageprotokolls. Ein breiter Protokollname wie `http`, `https` oder `grpc` kann verwendet werden; oder spezifische bzw. minimale HTTP-Versionen wie `http/1.1` oder `http/2+`.

Pro benanntem Matcher kann es nur einen `protocol`-Matcher geben.

#### Beispiel:

Anfragen matchen, die HTTP/2 verwenden:

```caddy-d
@http2 protocol http/2+
```

Mit einer [CEL-Expression](#expression):

```caddy-d
@http2 `protocol('http/2+')`
```



---
### query

```caddy-d
query <key>=<val>...
query ""

expression query({'<key>': '<val>'})
expression query({'<key>': ['<vals...>']})
```

Anhand von Query-String-Parametern. Sollte eine Folge von `key=value`-Paaren oder ein leerer String "" sein. Schlüssel werden exakt (case-sensitive) gematcht, unterstützen aber auch `*`, um jeden Wert zu matchen. Werte können Platzhalter verwenden. Ein leerer String matcht HTTP-Anfragen ohne Query-Parameter.

Pro benanntem Matcher kann es mehrere `query`-Matcher geben, und Paare mit denselben Schlüsseln werden per OR verknüpft. Unterschiedliche Schlüssel werden per AND verknüpft. Daher müssen alle Schlüssel im Matcher mindestens einen passenden Wert haben.

Ungültige Query-Strings (fehlerhafte Syntax, nicht escapte Semikolons usw.) schlagen beim Parsen fehl und matchen daher nicht.

**HINWEIS:** Query-String-Parameter sind Arrays, keine Einzelwerte. Das liegt daran, dass wiederholte Schlüssel in Query-Strings gültig sind und jeder davon einen anderen Wert haben kann. Dieser Matcher matcht für einen Schlüssel, wenn irgendeiner seiner konfigurierten Werte im Query-String zugewiesen ist. Backend-Anwendungen, die Query-Strings verwenden, MÜSSEN berücksichtigen, dass Query-String-Werte Arrays sind und mehrere Werte haben können.

#### Beispiel:

Einen `q`-Query-Parameter mit beliebigem Wert matchen:

```caddy-d
@search query q=*
```

Einen `sort`-Query-Parameter mit dem Wert `asc` oder `desc` matchen:

```caddy-d
@sorted query sort=asc sort=desc
```

Sowohl `q` als auch `sort` mit einer [CEL-Expression](#expression) matchen:

```caddy-d
@search-sort `query({'sort': ['asc', 'desc'], 'q': '*'})`
```



---
<a id="remote-ip"></a>
### remote_ip

```caddy-d
remote_ip <ranges...>

expression remote_ip('<ranges...>')
```

Anhand der Remote-IP-Adresse (d. h. der IP-Adresse des direkten Peers oder der per [PROXY-Protokoll](/docs/caddyfile/options#proxy-protocol) gesetzten Adresse). Akzeptiert genaue IPs oder CIDR-Bereiche. IPv6-Zonen werden unterstützt.

Als Kurzform kann `private_ranges` verwendet werden, um alle privaten IPv4- und IPv6-Bereiche zu matchen. Das entspricht der Angabe all dieser Bereiche: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`

Wenn du die aus HTTP-Headern geparste "echte IP" des Clients matchen möchtest, verwende stattdessen den [`client_ip`](#client-ip)-Matcher.

Pro benanntem Matcher kann es mehrere `remote_ip`-Matcher geben; ihre Bereiche werden zusammengeführt und per OR verknüpft.

#### Beispiel:

Anfragen von privaten IPv4-Adressen matchen:

```caddy-d
@private-ipv4 remote_ip 192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8
```

Dieser Matcher wird häufig mit dem [`not`](#not)-Matcher kombiniert, um den Match umzukehren. Zum Beispiel, um alle Verbindungen von *öffentlichen* IPv4- und IPv6-Adressen abzubrechen (also dem Gegenteil aller privaten Bereiche):

```caddy
example.com {
	@denied not remote_ip private_ranges
	abort @denied

	respond "Hello, you must be from a private network!"
}
```

In einer [CEL-Expression](#expression) sähe das so aus:

```caddy-d
@my-friends `remote_ip('12.23.34.45', '23.34.45.56')`
```



---
### vars

```caddy-d
vars <variable> <values...>

expression vars({'<variable>': '<value>'})
expression vars({'<variable>': ['<values...>']})
```

Anhand des Werts einer Variable im Anfragekontext oder des Werts eines Platzhalters. Es können mehrere Werte angegeben werden, um jeden dieser möglichen Werte zu matchen (per OR verknüpft).

Das Argument **&lt;variable&gt;** kann entweder ein Variablenname oder ein Platzhalter in geschweiften Klammern `{ }` sein. (Platzhalter werden im ersten Parameter nicht expandiert.)

Dieser Matcher ist am nützlichsten in Kombination mit der [`map`-Direktive](/docs/caddyfile/directives/map), die Ausgaben setzt, mit der [`vars`-Direktive](/docs/caddyfile/directives/vars) innerhalb deiner Routen oder mit Plugins, die Informationen im Anfragekontext setzen.

#### Beispiel:

Eine Ausgabe der [`map`-Direktive](/docs/caddyfile/directives/map) namens `magic_number` für die Werte `3` oder `5` matchen:

```caddy-d
vars {magic_number} 3 5
```

Den Wert eines beliebigen Platzhalters matchen, d. h. die ID des authentifizierten Benutzers, entweder `Bob` oder `Alice`:

```caddy-d
vars {http.auth.user.id} Bob Alice
```

Ein vollständiges Beispiel, das mit der [`vars`-Direktive](/docs/caddyfile/directives/vars) eine Variable setzt und dann mit dem [`vars`-Matcher](#vars) darauf matcht. Hier kombinieren wir zwei Anfrage-Header zu einer Variable und matchen auf diese Variable:

```caddy
example.com {
	vars combined_header "{header.Foo}_{header.Bar}"
	@special vars {vars.combined_header} "123_456"
	handle @special {
		respond "You sent Foo=123 and Bar=456!"
	}
	handle {
		respond "Foo and Bar were not special."
	}
}
```

In einer [CEL-Expression](#expression) sähe das so aus:

```caddy-d
@magic `vars({'magic_number': ['3', '5']})`
```


---
<a id="vars-regexp"></a>
### vars_regexp

```caddy-d
vars_regexp [<name>] <variable> <regexp>

expression vars_regexp('<name>', '<variable>', '<regexp>')
expression vars_regexp('<variable>', '<regexp>')
```

Wie [`vars`](#vars), unterstützt aber reguläre Expressions.

Die verwendete Sprache für reguläre Expressions ist RE2, das in Go enthalten ist. Siehe die [RE2-Syntaxreferenz](https://github.com/google/re2/wiki/Syntax) und die [Übersicht zur Go-regexp-Syntax](https://pkg.go.dev/regexp/syntax).

Ab v2.8.0 wird, wenn `name` *nicht* angegeben ist, der Name vom Namen des benannten Matchers übernommen. Zum Beispiel führt ein benannter Matcher `@foo` dazu, dass dieser Matcher `foo` heißt. Der Hauptvorteil eines ausdrücklich angegebenen Namens besteht darin, dass mehr als ein regexp-Matcher (z. B. `vars_regexp` und [`header_regexp`](#header-regexp)) im selben benannten Matcher verwendet werden kann.

Capture-Groups können nach dem Matching in Direktiven über [Platzhalter](/docs/caddyfile/concepts#placeholders) angesprochen werden:
- `{re.<name>.<capture_group>}`, wobei:
  - `<name>` der Name der regulären Expression ist,
  - `<capture_group>` entweder der Name oder die Nummer der Capture-Group in der Expression ist.

- `{re.<capture_group>}` ohne Namen wird der Einfachheit halber ebenfalls befüllt. Der Haken ist, dass bei mehreren nacheinander verwendeten regexp-Matchern die Platzhalterwerte vom nächsten Matcher überschrieben werden.

Capture-Group `0` ist der vollständige regexp-Match, `1` ist die erste Capture-Group, `2` die zweite usw. `{re.foo.1}` oder `{re.1}` enthalten also beide den Wert der ersten Capture-Group.

Pro Variablenname wird nur eine reguläre Expression unterstützt, da regexp-Patterns nicht zusammengeführt werden können. Wenn du mehr brauchst, solltest du einen [`expression`-Matcher](#expression) verwenden. Matches gegen mehrere unterschiedliche Variablen werden per AND verknüpft.

#### Beispiel:

Eine Ausgabe der [`map`-Direktive](/docs/caddyfile/directives/map) namens `magic_number` für einen Wert matchen, der mit `4` beginnt, und den Wert in einer Capture-Group erfassen, auf die mit `{re.magic.1}` oder `{re.1}` zugegriffen werden kann:

```caddy-d
@magic vars_regexp magic {magic_number} ^(4.*)
```

Dies kann vereinfacht werden, indem der Name weggelassen wird; er wird dann aus dem benannten Matcher abgeleitet:

```caddy-d
@magic vars_regexp {magic_number} ^(4.*)
```

In einer [CEL-Expression](#expression) sähe das so aus:

```caddy-d
@magic `vars_regexp('magic_number', '^(4.*)')`
```
