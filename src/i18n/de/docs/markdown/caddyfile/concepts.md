---
title: Caddyfile-Konzepte
---

# Caddyfile-Konzepte

Dieses Dokument hilft dir, das HTTP-Caddyfile im Detail zu verstehen.

1. [Struktur](#structure)
	- [Blöcke](#blocks)
	- [Direktiven](#directives)
	- [Tokens und Anführungszeichen](#tokens-and-quotes)
2. [Globale Optionen](#global-options)
3. [Adressen](#addresses)
4. [Matcher](#matchers)
5. [Platzhalter](#placeholders)
6. [Snippets](#snippets)
7. [Benannte Routen](#named-routes)
8. [Kommentare](#comments)
9. [Umgebungsvariablen](#environment-variables)


<a id="structure"></a>
## Struktur

Die Struktur des Caddyfile lässt sich visuell so beschreiben:

<style>
	:root {
		--struct-border-global: #e74c3c;
		--struct-border-snippet: #2ecc71;
		--struct-border-site: #3498db;
		--struct-border-matcher: #d453d4;
		--struct-bg-1: #edf5fd;
		--struct-bg-2: #f8fbfd;
		--struct-bg-end: 100%;
		--struct-fg: #254048;
		--struct-opt-name-bg: #ffd9dd;
		--struct-opt-name-fg: #7a2a39;
		--struct-opt-value-bg: #f4dec6;
		--struct-opt-value-fg: #5a3723;
		--struct-comment-bg: #d2d7d8;
		--struct-comment-fg: #495456;
		--struct-site-addr-bg: #cbe4f2;
		--struct-site-addr-fg: #1f6f9a;
		--struct-directive-bg: #c8f7d6;
		--struct-directive-fg: #14663a;
		--struct-matcher-token-bg: #ffd6ff;
		--struct-matcher-token-fg: #6f2070;
		--struct-arg-bg: #ded0ff;
		--struct-arg-fg: #4b2f7a;
		--struct-subdir-bg: #dbbca2;
		--struct-subdir-fg: #5b3a25;
	}
	html.dark {
		--struct-border-global: #e74c3c;
		--struct-border-snippet: #2ecc71;
		--struct-border-site: #3498db;
		--struct-border-matcher: #d453d4;
		--struct-bg-1: #0d313c;
		--struct-bg-2: transparent;
		--struct-bg-end: 120%;
		--struct-fg: #cbd6da;
		--struct-opt-name-bg: #6b2630;
		--struct-opt-name-fg: #ffd9dd;
		--struct-opt-value-bg: #68412b;
		--struct-opt-value-fg: #f4dec6;
		--struct-comment-bg: #2f424d;
		--struct-comment-fg: #e8eef0;
		--struct-site-addr-bg: #204d59;
		--struct-site-addr-fg: #d6f0ff;
		--struct-directive-bg: #1f4e36;
		--struct-directive-fg: #c8f7d6;
		--struct-matcher-token-bg: #65305a;
		--struct-matcher-token-fg: #ffd6ff;
		--struct-arg-bg: #3b2e46;
		--struct-arg-fg: #ded0ff;
		--struct-subdir-bg: #6a4a2e;
		--struct-subdir-fg: #ebc095;
	}
	/* Farbvariablen - leicht anzupassen */
	.struct-caddyfile-visual-repl {
		display: block;
		margin: 0;
		padding: 0;
	}
	/* Standardhintergrund (hell) der Visualisierung */
	.struct-caddyfile-visual-repl .struct-visual {
		box-sizing: border-box;
		margin: 0 0 1.25rem;
		padding: 14px;
		border-radius: 14px;
		background: linear-gradient(to bottom, var(--struct-bg-1) 0%, var(--struct-bg-2) var(--struct-bg-end));
		color: var(--struct-fg);
		font-family: Inter, 'Source Sans Pro', Arial, system-ui, sans-serif;
		line-height: 1.2;
	}
	/* Layout */
	.struct-caddyfile-visual-repl .struct-panel {
		display: flex;
		gap: 18px;
		align-items: flex-start;
		flex-wrap: wrap;
	}
	.struct-caddyfile-visual-repl .struct-diagram {
		flex: 1;
		padding: 8px 8px;
	}
	.struct-caddyfile-visual-repl .struct-legend {
		width: 310px;
		padding: 12px 4px;
	}
	/* Codeähnlicher Kasten: normalen Leerraum verwenden, damit HTML-Pretty-Printing keine Quell-Einrückung sichtbar macht */
	.struct-caddyfile-visual-repl .struct-code-box {
		background: transparent;
		border-radius: 8px;
		padding: 6px 6px !important;
		font-family: var(--monospace-fonts);
		font-size: 90%;
		white-space: normal;
	}
	.struct-block {
		border-radius: 8px;
		padding: 10px;
		margin: 0 0 10px 0;
	}
	.struct-block.global {
		border: 4px solid var(--struct-border-global);
	}
	.struct-block.snippet {
		border: 4px solid var(--struct-border-snippet);
	}
	.struct-block.site {
		border: 4px solid var(--struct-border-site);
	}
	.struct-block.matcher {
		border: 4px solid var(--struct-border-matcher);
		margin: 8px 8px 10px 10px;
		padding: 8px;
		border-radius: 6px;
	}
	.struct-token, .struct-opt-name, .struct-opt-value, .struct-comment, .struct-site-addr, .struct-directive, .struct-matcher-token, .struct-arg, .struct-subdir {
		display: inline !important;
		padding: .03rem .18rem !important;
		border-radius: 6px;
		font-family: var(--monospace-fonts);
		font-size: 95%;
		vertical-align: middle;
	}
	.struct-opt-name {
		background: var(--struct-opt-name-bg);
		color: var(--struct-opt-name-fg);
	}
	.struct-opt-value {
		background: var(--struct-opt-value-bg);
		color: var(--struct-opt-value-fg);
	}
	.struct-comment {
		background: var(--struct-comment-bg);
		color: var(--struct-comment-fg);
	}
	.struct-site-addr {
		background: var(--struct-site-addr-bg);
		color: var(--struct-site-addr-fg);
	}
	.struct-directive {
		background: var(--struct-directive-bg);
		color: var(--struct-directive-fg);
	}
	.struct-matcher-token {
		background: var(--struct-matcher-token-bg);
		color: var(--struct-matcher-token-fg);
	}
	.struct-arg {
		background: var(--struct-arg-bg);
		color: var(--struct-arg-fg);
	}
	.struct-subdir {
		background: var(--struct-subdir-bg);
		color: var(--struct-subdir-fg);
	}
	.struct-legend .struct-legend-title {
		font-weight: 700;
		font-size: 1.6rem;
	}
	.struct-legend .struct-item {
		display: flex;
		align-items: center;
		gap: 10px;
		margin: 16px 0;
	}
	.struct-legend .struct-item-spacer {
		height: 8px;
	}
	/* Farbfeld für rahmenbasierte Legendeneinträge (Blöcke) */
	.struct-legend .struct-swatch-border {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		border: 4px solid transparent;
		background: transparent;
	}
	/* Farbfeld für gefüllte Legendeneinträge (Texthintergründe) */
	.struct-legend .struct-swatch-fill {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		background: transparent;
	}
	.struct-legend .struct-label {
		font-size: 90%;
		color: inherit;
	}
	.struct-caddyfile-visual-repl .struct-visual, .struct-caddyfile-visual-repl .struct-panel, .struct-caddyfile-visual-repl .struct-diagram, .struct-caddyfile-visual-repl .struct-legend, .struct-caddyfile-visual-repl .struct-code-box {
		margin: 0;
	}
	/* Kompakten vertikalen Rhythmus und explizite Einrückung erzwingen, damit globales CSS nicht hineinwirkt
		HINWEIS: normalen Leerraum verwenden, damit serverseitige HTML-Formatierung keine sichtbaren Lücken erzeugt */
	.struct-line {
		display: block !important;
		margin: 0 !important;
		padding: 2px 0 !important;
		line-height: 1.2 !important;
		white-space: normal !important;
	}
	/* Hilfsmittel zur visuellen Einrückung von Zeilen (nicht auf Leerraum in der Quelldatei verlassen)
		ein explizites Abstandselement verwenden, damit HTML-Formatierung die Ausrichtung nicht beeinflusst */
	.struct-line.struct-indent {
		padding-left: 0 !important;
	}
	.struct-indent-spacer {
		display: inline-block;
		width: 1.2rem;
		height: 1px;
		margin-right: 0.18rem;
	}
	/* Kleinerer Abstand für Subdirektiven / verschachtelte Zeilen */
	.struct-subindent-spacer {
		display: inline-block;
		width: 0.9rem;
		height: 1px;
		margin-right: 0.12rem;
	}
</style>

<div class="struct-caddyfile-visual-repl fullwidth">
	<div class="struct-visual">
		<div class="struct-panel">
			<div class="struct-diagram">
				<div class="struct-code-box">
					<div class="struct-block global">
						<div class="struct-line">{</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">email</span> <span class="struct-opt-value">you@yours.com</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">servers</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">trusted_proxies</span> <span class="struct-arg">static</span> <span class="struct-arg">private_ranges</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block snippet">
						<div class="struct-line">(snippet) {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-comment"># dies ist ein wiederverwendbares Snippet</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">log</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">output</span> <span class="struct-arg">file</span> <span class="struct-arg">/var/log/access.log</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line"><span class="struct-site-addr">example.com</span> {</div>
						<div class="struct-block matcher">
							<div class="struct-line"><span class="struct-matcher-token">@post</span> {</div>
							<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-matcher-token">method</span> <span class="struct-arg">POST</span></div>
							<div class="struct-line">}</div>
						</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">reverse_proxy</span> <span class="struct-matcher-token">@post</span> <span class="struct-arg">localhost:9001</span> <span class="struct-arg">localhost:9002</span> {</div>
						<div class="struct-line"><span class="struct-subindent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">lb_policy</span> <span class="struct-arg">first</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">file_server</span> <span class="struct-matcher-token">/static</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">import</span> <span class="struct-arg">snippet</span></div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block site">
						<div class="struct-line struct-indent"><span class="struct-site-addr">www.example.com</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">redir</span> <span class="struct-arg">https://example.com{uri}</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-directive">import</span> <span class="struct-arg">snippet</span></div>
						<div class="struct-line">}</div>
					</div>
				</div>
			</div>
			<div class="struct-legend" aria-hidden="false">
				<div class="struct-legend-title">Legende</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">Globaler Optionsblock</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">Snippet</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">Site-Block</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-matcher)"></div><div class="struct-label">Matcher-Definition</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">Optionsname</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">Optionswert</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">Kommentar</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">Site-Adresse</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">Direktive</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">Matcher-Token</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">Argument</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">Subdirektive</div></div>
			</div>
		</div>
	</div>
</div>

Wichtige Punkte:

- Ein optionaler [**globaler Optionsblock**](#global-options) kann ganz am Anfang der Datei stehen.

- Danach können optional [Snippets](#snippets) oder [benannte Routen](#named-routes) folgen.

- Andernfalls ist die erste Zeile des Caddyfile **immer** die [Adresse bzw. die Adressen](#addresses) der bereitzustellenden Site.

- Alle [Direktiven](#directives) und [Matcher](#matchers) **müssen** in einem Site-Block stehen. Es gibt keinen globalen Gültigkeitsbereich und keine Vererbung zwischen Site-Blöcken.

- Wenn es nur einen Site-Block gibt, sind dessen geschweifte Klammern `{ }` optional.

Ein Caddyfile besteht aus mindestens einem oder mehreren Site-Blöcken, die immer mit einer oder mehreren [Adressen](#addresses) für die Site beginnen. Direktiven vor der Adresse verwirren den Parser.


<a id="blocks"></a>
### Blöcke

Ein **Block** wird mit geschweiften Klammern geöffnet und geschlossen:

```
... {
	...
}
```

- Die öffnende geschweifte Klammer `{` muss am Ende ihrer Zeile stehen und ihr muss ein Leerzeichen vorausgehen.

- Die schließende geschweifte Klammer `}` muss in einer eigenen Zeile stehen.

Wenn es nur einen Site-Block gibt, sind die geschweiften Klammern (und die Einrückung) optional. Das ist praktisch, um schnell eine einzelne Site zu definieren. Zum Beispiel ist dies:

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

gleichbedeutend mit:

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

wenn du nur einen einzelnen Site-Block hast; es ist Geschmackssache.

Um mehrere Sites mit demselben Caddyfile zu konfigurieren, **musst** du jede einzelne mit geschweiften Klammern umschließen, damit ihre Konfigurationen getrennt bleiben:

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

Wenn eine Anfrage auf mehrere Site-Blöcke passt, wird der Site-Block mit der spezifischsten passenden Adresse gewählt. Anfragen fallen nicht in andere Site-Blöcke weiter.


<a id="directives"></a>
### Direktiven

[**Direktiven**](/docs/caddyfile/directives) sind funktionale Schlüsselwörter, mit denen angepasst wird, wie die Site ausgeliefert wird. Sie **müssen** innerhalb von Site-Blöcken stehen. Eine vollständige file_server-Konfiguration könnte zum Beispiel so aussehen:

```caddy
localhost {
	file_server
}
```

Oder ein reverse_proxy:

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

In diesen Beispielen sind [`file_server`](/docs/caddyfile/directives/file_server) und [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) Direktiven. Direktiven sind das erste Wort einer Zeile in einem Site-Block.

Im zweiten Beispiel ist `localhost:9000` ein **Argument**, weil es in derselben Zeile nach der Direktive steht.

Manchmal können Direktiven eigene Blöcke öffnen. **Subdirektiven** stehen am Anfang jeder Zeile innerhalb von Direktivenblöcken:

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

Hier ist `lb_policy` eine Subdirektive von [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) (sie legt die Load-Balancing-Policy fest, die zwischen Backends verwendet wird).

**Sofern nicht anders dokumentiert, können Direktiven nicht innerhalb anderer Direktivenblöcke verwendet werden.** Zum Beispiel kann [`basic_auth`](/docs/caddyfile/directives/basic_auth) nicht innerhalb von [`file_server`](/docs/caddyfile/directives/file_server) verwendet werden, weil der file_server nicht weiß, wie Authentifizierung durchzuführen ist. Du kannst Direktiven aber innerhalb von [`route`](/docs/caddyfile/directives/route)-, [`handle`](/docs/caddyfile/directives/handle)- und [`handle_path`](/docs/caddyfile/directives/handle_path)-Blöcken verwenden, weil diese speziell dafür gedacht sind, Direktiven zu gruppieren.

Beachte, dass HTTP-handler-Direktiven beim Adaptieren des HTTP-Caddyfile nach einer bestimmten standardmäßigen [Direktivenreihenfolge](/docs/caddyfile/directives#directive-order) sortiert werden, außer sie stehen in einem [`route`](/docs/caddyfile/directives/route)-Block. Die Reihenfolge, in der Direktiven erscheinen, spielt also außer in `route`-Blöcken keine Rolle.


<a id="tokens-and-quotes"></a>
### Tokens und Anführungszeichen

Das Caddyfile wird vor dem Parsen in Tokens lexikalisch zerlegt. Leerraum ist im Caddyfile bedeutsam, weil Tokens durch Leerraum getrennt werden.

Direktiven erwarten oft eine bestimmte Anzahl von Argumenten. Wenn ein einzelnes Argument einen Wert mit Leerraum enthält, würde es als zwei getrennte Tokens gelesen:

```caddy-d
directive abc def
```

Das kann problematisch sein und zu Fehlern oder unerwartetem Verhalten führen.

Wenn `abc def` der Wert eines einzelnen Arguments sein soll, muss es in Anführungszeichen gesetzt werden:

```caddy-d
directive "abc def"
```

Anführungszeichen können auch escaped werden, wenn du sie innerhalb von quoted Tokens verwenden musst:

```caddy-d
directive "\"abc def\""
```

Um das Escapen von Anführungszeichen zu vermeiden, kannst du stattdessen Backticks <code>\` \`</code> verwenden, um Tokens einzuschließen, zum Beispiel:

```caddy-d
directive `{"foo": "bar"}`
```

Innerhalb von quoted Tokens werden alle anderen Zeichen wörtlich behandelt, einschließlich Leerzeichen, Tabs und Zeilenumbrüchen. Mehrzeilige Tokens sind daher möglich:

```caddy-d
directive "first line
	second line"
```

Heredocs <span id="heredocs"/> werden ebenfalls unterstützt:

```caddy
example.com {
	respond <<HTML
		<html>
		  <head><title>Foo</title></head>
		  <body>Foo</body>
		</html>
		HTML 200
}
```

Die öffnende Heredoc-Markierung muss mit `<<` beginnen, gefolgt von beliebigem Text (Großbuchstaben empfohlen). Die schließende Heredoc-Markierung muss derselbe Text sein (im obigen Beispiel `HTML`). Die öffnende Markierung kann bei Bedarf mit `\<<` escaped werden, um Heredoc-Parsing zu verhindern.

Die schließende Markierung darf eingerückt sein; dadurch wird jeder Textzeile genau diese Einrückung entfernt (inspiriert von [PHP](https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc)). Das verbessert die Lesbarkeit innerhalb von [Blöcken](#blocks) und gibt trotzdem genaue Kontrolle über den Leerraum im Token-Text. Der abschließende Zeilenumbruch wird ebenfalls entfernt, kann aber beibehalten werden, indem vor der schließenden Markierung eine zusätzliche Leerzeile eingefügt wird.

Weitere Tokens können nach der schließenden Markierung als Argumente der Direktive folgen (wie im obigen Beispiel der Statuscode `200`).


<a id="global-options"></a>
## Globale Optionen

Ein Caddyfile kann optional mit einem besonderen Block ohne Schlüssel beginnen, dem sogenannten [globalen Optionsblock](/docs/caddyfile/options):

```caddy
{
	...
}
```

Wenn er vorhanden ist, muss er der allererste Block der Konfiguration sein.

Er dient dazu, Optionen zu setzen, die global gelten oder keiner einzelnen Site speziell zugeordnet sind. Darin können nur globale Optionen gesetzt werden; reguläre Site-Direktiven kannst du dort nicht verwenden.

Um zum Beispiel die globale Option `debug` zu aktivieren, die häufig für ausführliche Logs bei der Fehlersuche verwendet wird:

```caddy
{
	debug
}
```

**[Lies die Seite zu globalen Optionen](/docs/caddyfile/options), um mehr zu erfahren.**



<a id="addresses"></a>
## Adressen

Eine Adresse steht immer oben im Site-Block und ist normalerweise das Erste im Caddyfile.

Dies sind Beispiele für gültige Adressen:

| Adresse              | Wirkung                           |
|----------------------|-----------------------------------|
| `example.com`        | HTTPS mit verwaltetem [öffentlich vertrauenswürdigem Zertifikat](/docs/automatic-https#hostname-requirements) |
| `*.example.com`      | HTTPS mit verwaltetem [öffentlich vertrauenswürdigem Wildcard-Zertifikat](/docs/caddyfile/patterns#wildcard-certificates) |
| `localhost`          | HTTPS mit verwaltetem [lokal vertrauenswürdigem Zertifikat](/docs/automatic-https#local-https) |
| `http://`            | HTTP-Catch-all, beeinflusst durch [`http_port`](/docs/caddyfile/options#http-port) |
| `https://`           | HTTPS-Catch-all, beeinflusst durch [`https_port`](/docs/caddyfile/options#http-port) |
| `http://example.com` | Explizit HTTP, mit einem `Host`-Matcher |
| `example.com:443`    | HTTPS, weil dies dem Standardwert von [`https_port`](/docs/caddyfile/options#http-port) entspricht |
| `:443`               | HTTPS-Catch-all, weil dies dem Standardwert von [`https_port`](/docs/caddyfile/options#http-port) entspricht |
| `:8080`              | HTTP auf einem nicht standardmäßigen Port, ohne `Host`-Matcher |
| `localhost:8080`     | HTTPS auf einem nicht standardmäßigen Port, weil eine gültige Domain vorhanden ist |
| `https://example.com:443` | HTTPS, aber `https://` und `:443` zusammen sind redundant |
| `127.0.0.1` | HTTPS, mit einem lokal vertrauenswürdigen IP-Zertifikat |
| `http://127.0.0.1` | HTTP, mit einem IP-Adress-`Host`-Matcher (weist `localhost` zurück) |


<aside class="tip">

[Automatic HTTPS](/docs/automatic-https) wird aktiviert, wenn die Adresse deiner Site einen Hostnamen oder eine IP-Adresse enthält. Dieses Verhalten ist jedoch rein implizit und überschreibt daher niemals eine explizite Konfiguration.

Wenn die Adresse der Site zum Beispiel `http://example.com` ist, wird auto-HTTPS nicht aktiviert, weil das Schema ausdrücklich `http://` ist.

</aside>


Aus der Adresse kann Caddy potenziell Schema, Host und Port deiner Site ableiten. Wenn die Adresse keinen Port enthält, wählt das Caddyfile den zum Schema passenden Port, sofern eines angegeben ist; andernfalls wird der Standardport 443 angenommen.

Wenn du einen Hostnamen angibst, werden nur Anfragen mit passendem `Host`-Header berücksichtigt. Anders gesagt: Wenn die Site-Adresse `localhost` lautet, passt Caddy nicht auf Anfragen an `127.0.0.1`.

Wildcards (`*`) können verwendet werden, aber nur, um genau ein Label des Hostnamens darzustellen. Zum Beispiel passt `*.example.com` auf `foo.example.com`, aber nicht auf `foo.bar.example.com`; und `*` passt auf `localhost`, aber nicht auf `example.com`. Ein praktisches Beispiel findest du im [Wildcard-Zertifikate-Pattern](/docs/caddyfile/patterns#wildcard-certificates).

Um alle Hosts abzufangen, lass den Host-Teil der Adresse weg, zum Beispiel einfach `https://`. Das ist nützlich bei [On-Demand TLS](/docs/automatic-https#on-demand-tls), wenn du die Domains vorher nicht kennst.

Wenn mehrere Sites dieselbe Definition teilen, kannst du sie gemeinsam auflisten, getrennt durch Leerzeichen und Kommas (mindestens ein Leerzeichen ist erforderlich). Die folgenden drei Beispiele sind gleichwertig:

```caddy
# Durch Kommas getrennte Site-Adressen
localhost:8080, example.com, www.example.com {
	...
}
```

oder

```caddy
# Durch Leerzeichen getrennte Site-Adressen
localhost:8080 example.com www.example.com {
	...
}
```

oder

```caddy
# Durch Kommas und Zeilenumbrüche getrennte Site-Adressen
localhost:8080,
example.com,
www.example.com {
	...
}
```

Eine Adresse muss eindeutig sein; du kannst dieselbe Adresse nicht mehr als einmal angeben.

[Platzhalter](#placeholders) können in Adressen **nicht** verwendet werden, aber du kannst darin [Umgebungsvariablen](#environment-variables) im Caddyfile-Stil verwenden:

```caddy
{$DOMAIN:localhost} {
	...
}
```

Standardmäßig binden Sites an alle Netzwerkschnittstellen. Wenn du das überschreiben möchtest, verwende dafür die [`bind`-Direktive](/docs/caddyfile/directives/bind) oder die globale Option [`default_bind`](/docs/caddyfile/options#default-bind).



<a id="matchers"></a>
## Matcher

HTTP-handler-[Direktiven](#directives) gelten standardmäßig für alle Anfragen (sofern nicht anders dokumentiert).

[Request-Matcher](/docs/caddyfile/matchers) können verwendet werden, um Anfragen nach bestimmten Kriterien einzuordnen. Mit Matchern kannst du genau festlegen, für welche Anfragen eine bestimmte Direktive gilt.

Bei Direktiven, die Matcher unterstützen, ist das erste Argument nach der Direktive das **Matcher-Token**. Hier sind einige Beispiele:

```caddy-d
root *           /var/www  # Matcher-Token: *
root /index.html /var/www  # Matcher-Token: /index.html
root @post       /var/www  # Matcher-Token: @post
```

Matcher-Tokens können vollständig weggelassen werden, um alle Anfragen zu matchen; zum Beispiel muss `*` nicht angegeben werden, wenn das nächste Argument nicht wie ein Pfad-Matcher aussieht.

**[Lies die Seite zu Request-Matchern](/docs/caddyfile/matchers), um mehr zu erfahren.**




<a id="placeholders"></a>
## Platzhalter

[Platzhalter](/docs/conventions#placeholders) sind eine einfache Möglichkeit, dynamische Werte in deine statische Konfiguration einzufügen. Sie können als Argumente für Direktiven und Subdirektiven verwendet werden.

Platzhalter werden auf beiden Seiten durch geschweifte Klammern `{ }` begrenzt und enthalten innen den Bezeichner, zum Beispiel `{foo.bar}`. Die öffnende Platzhalterklammer kann als `\{like.this}` escaped werden, um eine Ersetzung zu verhindern. Platzhalterbezeichner sind typischerweise mit Punkten namespaced, um Kollisionen zwischen Modulen zu vermeiden.

Welche Platzhalter verfügbar sind, hängt vom Kontext ab. Nicht alle Platzhalter sind in allen Teilen der Konfiguration verfügbar. Beispielsweise [setzt die HTTP-App Platzhalter](/docs/json/apps/http/#docs), die nur in Bereichen der Konfiguration verfügbar sind, die HTTP-Anfragen verarbeiten, also in HTTP-handler-[Direktiven](#directives) und [Matchern](#matchers), aber *nicht* in der [`tls`-Konfiguration](/docs/caddyfile/directives/tls). Manche Direktiven oder Matcher können außerdem eigene Platzhalter setzen, die von nachfolgenden Teilen verwendet werden können. Einige Platzhalter sind [global verfügbar](/docs/conventions#placeholders).

Du kannst beliebige Platzhalter im Caddyfile verwenden, der Einfachheit halber aber auch einige dieser gleichwertigen Kurzformen, die beim Parsen des Caddyfile expandiert werden:

| Caddyfile        | Ersetzt                             |
|------------------|-------------------------------------|
| `{cookie.*}`     | `{http.request.cookie.*}`           |
| `{client_ip}`    | `{http.vars.client_ip}`             |
| `{dir}`          | `{http.request.uri.path.dir}`       |
| `{err.*}`        | `{http.error.*}`                    |
| `{file_match.*}` | `{http.matchers.file.*}`            |
| `{file.base}`    | `{http.request.uri.path.file.base}` |
| `{file.ext}`     | `{http.request.uri.path.file.ext}`  |
| `{file}`         | `{http.request.uri.path.file}`      |
| `{header.*}`     | `{http.request.header.*}`           |
| `{host}`         | `{http.request.host}`               |
| `{hostport}`     | `{http.request.hostport}`           |
| `{labels.*}`     | `{http.request.host.labels.*}`      |
| `{method}`       | `{http.request.method}`             |
| `{orig_method}`  | `{http.request.orig_method}`        |
| `{orig_uri}`     | `{http.request.orig_uri}`           |
| `{orig_path}`    | `{http.request.orig_uri.path}`      |
| `{orig_dir}`     | `{http.request.orig_uri.path.dir}`  |
| `{orig_file}`    | `{http.request.orig_uri.path.file}` |
| `{orig_query}`   | `{http.request.orig_uri.query}`     |
| `{orig_?query}`  | `{http.request.orig_uri.prefixed_query}` |
| `{path.*}`       | `{http.request.uri.path.*}`         |
| `{path}`         | `{http.request.uri.path}`           |
| `{%path}`        | `{http.request.uri.path_escaped}`   |
| `{port}`         | `{http.request.port}`               |
| `{query.*}`      | `{http.request.uri.query.*}`        |
| `{query}`        | `{http.request.uri.query}`          |
| `{%query}`       | `{http.request.uri.query_escaped}`  |
| `{?query}`       | `{http.request.uri.prefixed_query}` |
| `{re.*}`         | `{http.regexp.*}`                   |
| `{remote_host}`  | `{http.request.remote.host}`        |
| `{remote_port}`  | `{http.request.remote.port}`        |
| `{remote}`       | `{http.request.remote}`             |
| `{rp.*}`         | `{http.reverse_proxy.*}`            |
| `{resp.*}`       | `{http.intercept.*}`                |
| `{scheme}`       | `{http.request.scheme}`             |
| `{tls_cipher}`   | `{http.request.tls.cipher_suite}`   |
| `{tls_client_certificate_der_base64}` | `{http.request.tls.client.certificate_der_base64}` |
| `{tls_client_certificate_pem}`        | `{http.request.tls.client.certificate_pem}` |
| `{tls_client_fingerprint}`            | `{http.request.tls.client.fingerprint}`     |
| `{tls_client_issuer}`                 | `{http.request.tls.client.issuer}`          |
| `{tls_client_serial}`                 | `{http.request.tls.client.serial}`          |
| `{tls_client_subject}`                | `{http.request.tls.client.subject}`         |
| `{tls_version}`       | `{http.request.tls.version}`             |
| `{upstream_hostport}` | `{http.reverse_proxy.upstream.hostport}` |
| `{uri}`               | `{http.request.uri}`                     |
| `{%uri}`              | `{http.request.uri_escaped}`             |
| `{vars.*}`            | `{http.vars.*}`                          |

Nicht alle Konfigurationsfelder unterstützen Platzhalter, aber die meisten tun es dort, wo du es erwarten würdest. Unterstützung für Platzhalter muss diesen Feldern ausdrücklich hinzugefügt worden sein. Plugin-Autoren können [diesen Artikel lesen](/docs/extending-caddy/placeholders), um zu erfahren, wie sie Unterstützung für Platzhalter in ihren eigenen Modulen hinzufügen.




<a id="snippets"></a>
## Snippets

Du kannst besondere Blöcke definieren, die Snippets heißen, indem du ihnen einen von Klammern umschlossenen Namen gibst:

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

Danach kannst du sie überall dort wiederverwenden, wo du sie brauchst, indem du die besondere Direktive [`import`](/docs/caddyfile/directives/import) verwendest:

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

Die Direktive [`import`](/docs/caddyfile/directives/import) kann auch verwendet werden, um an ihrer Stelle andere Dateien einzubinden. Wenn das Argument keinem definierten Snippet entspricht, wird es als Datei versucht. Sie unterstützt außerdem Globs, um mehrere Dateien zu importieren. Als Sonderfall kann sie überall im Caddyfile erscheinen (außer als Argument einer anderen Direktive), auch außerhalb von Site-Blöcken:

```caddy
{
	email admin@example.com
}

import sites/*
```

Du kannst einer importierten Konfiguration (Snippets oder Dateien) Argumente übergeben und sie so verwenden:

```caddy
(snippet) {
	respond "Yahaha! You found {args[0]}!"
}

a.example.com {
	import snippet "Example A"
}

b.example.com {
	import snippet "Example B"
}
```

⚠️ <i>Experimentell</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Du kannst einem importierten Snippet auch einen optionalen Block übergeben und ihn wie folgt verwenden.

```caddy
(snippet) {
	{block}
	respond "OK"
}

a.example.com {
	import snippet {
		header +foo bar
	}
}

b.example.com {
	import snippet {
		header +bar foo
	}
}
```

**[Lies die Seite zur `import`-Direktive](/docs/caddyfile/directives/import), um mehr zu erfahren.**


<a id="named-routes"></a>
## Benannte Routen

⚠️ <i>Experimentell</i>

Benannte Routen verwenden eine ähnliche Syntax wie [Snippets](#snippets). Sie sind besondere Blöcke, die außerhalb von Site-Blöcken definiert werden, mit `&(` beginnen und mit `)` enden; dazwischen steht der Name.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

Danach kannst du diese benannte Route innerhalb jeder Site wiederverwenden:

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

Das ist besonders nützlich, um Speicherverbrauch zu reduzieren, wenn dieselbe Route in vielen verschiedenen Sites benötigt wird oder wenn mehrere unterschiedliche Matcher-Bedingungen dieselbe Route aufrufen sollen.

**[Lies die Seite zur `invoke`-Direktive](/docs/caddyfile/directives/invoke), um mehr zu erfahren.**



<a id="comments"></a>
## Kommentare

Kommentare beginnen mit `#` und reichen bis zum Ende der Zeile:

```caddy-d
# Kommentare können eine Zeile beginnen
directive  # oder am Ende stehen
```

Das Hash-Zeichen `#` für einen Kommentar darf nicht mitten in einem Token stehen (d. h. ihm muss ein Leerzeichen vorausgehen oder es muss am Zeilenanfang stehen). Dadurch können Hash-Zeichen in URIs oder anderen Werten verwendet werden, ohne dass Anführungszeichen nötig sind.



<a id="environment-variables"></a>
## Umgebungsvariablen

Wenn deine Konfiguration von Umgebungsvariablen abhängt, kannst du sie im Caddyfile verwenden:

```caddy
{$ENV}
```

Umgebungsvariablen in dieser Form werden **ersetzt, bevor das Parsen des Caddyfile beginnt**. Sie können daher zu leeren Werten (d. h. `""`), Teil-Tokens, vollständigen Tokens oder sogar zu mehreren Tokens und Zeilen expandieren.

Zum Beispiel würde eine Umgebungsvariable `UPSTREAMS="app1:8080 app2:8080 app3:8080"` zu mehreren [Tokens](#tokens-and-quotes) expandieren:

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

Ein Standardwert für den Fall, dass die Umgebungsvariable nicht gefunden wird, kann angegeben werden, indem `:` als Trennzeichen zwischen Variablenname und Standardwert verwendet wird:

```caddy
{$DOMAIN:localhost} {

}
```

Wenn du die **Ersetzung einer Umgebungsvariable bis zur Laufzeit aufschieben** möchtest, kannst du die [standardmäßigen `{env.*}`-Platzhalter](/docs/conventions#placeholders) verwenden. Beachte jedoch, dass nicht alle Konfigurationsparameter diese Platzhalter unterstützen, weil Modulentwickler eine Codezeile hinzufügen müssen, um die Ersetzung auszuführen. Wenn es nicht zu funktionieren scheint, öffne bitte ein Issue, um Unterstützung dafür anzufordern.

Wenn du zum Beispiel das Plugin [`caddy-dns/cloudflare` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns/cloudflare) installiert hast und die [DNS-Challenge](/docs/automatic-https#dns-challenge) konfigurieren möchtest, kannst du deine Umgebungsvariable `CLOUDFLARE_API_TOKEN` so an das Plugin übergeben:

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Wenn du Caddy als systemd-Dienst betreibst, findest du in [diesen Anweisungen](/docs/running#overrides), wie du Service-Overrides einrichtest, um deine Umgebungsvariablen zu definieren.
