---
title: Concetti del Caddyfile
---

# Concetti del Caddyfile

Questo documento vi aiuterà a conoscere in dettaglio l'HTTP Caddyfile.

1. [Struttura](#struttura)
	- [Blocchi](#blocchi)
	- [Direttive](#direttive)
	- [Token e virgolette](#token-e-virgolette)
2. [Opzioni globali](#opzioni-globali)
3. [Indirizzi](#indirizzi)
4. [Matcher](#matcher)
5. [Placeholder](#placeholder)
6. [Snippet](#snippet)
7. [Rotte nominate](#rotte-nominate)
8. [Commenti](#commenti)
9. [Variabili d'ambiente](#variabili-dambiente)



## Struttura

La struttura del Caddyfile può essere descritta visivamente:

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
	/* color variables - easy to tweak */
	.struct-caddyfile-visual-repl {
		display: block;
		margin: 0;
		padding: 0;
	}
	/* default (light) visual background */
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
	/* layout */
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
	/* code-like box: use normal whitespace so HTML pretty-printing won't leak source indentation */
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
	/* swatch for border-based legend items (blocks) */
	.struct-legend .struct-swatch-border {
		width: 42px;
		height: 24px;
		border-radius: 6px;
		box-sizing: border-box;
		border: 4px solid transparent;
		background: transparent;
	}
	/* swatch for filled legend items (text backgrounds) */
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
	/* force compact vertical rhythm and explicit indenting so global CSS can't leak in
		NOTE: use normal whitespace so server-side HTML formatting doesn't create visible gaps */
	.struct-line {
		display: block !important;
		margin: 0 !important;
		padding: 2px 0 !important;
		line-height: 1.2 !important;
		white-space: normal !important;
	}
	/* helper to visually indent lines (do not rely on source file whitespace)
		use an explicit spacer element so HTML formatting won't affect alignment */
	.struct-line.struct-indent {
		padding-left: 0 !important;
	}
	.struct-indent-spacer {
		display: inline-block;
		width: 1.2rem;
		height: 1px;
		margin-right: 0.18rem;
	}
	/* smaller spacer for sub-directive / nested lines */
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
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">email</span> <span class="struct-opt-value">voi@vostro.com</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">servers</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">trusted_proxies</span> <span class="struct-arg">static</span> <span class="struct-arg">private_ranges</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block snippet">
						<div class="struct-line">(snippet) {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-comment"># questo è uno snippet riutilizzabile</span></div>
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
				<div class="struct-legend-title">Legenda</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">Blocco opzioni globali</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">Snippet</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">Blocco sito</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-matcher)"></div><div class="struct-label">Definizione matcher</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">Nome opzione</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">Valore opzione</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">Commento</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">Indirizzo del sito</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">Direttiva</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">Token matcher</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">Argomento</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">Sottodirettiva</div></div>
			</div>
		</div>
	</div>
</div>

Punti chiave:

- Un [**blocco opzioni globali**](#opzioni-globali) opzionale può essere la primissima cosa nel file.

- Gli [snippet](#snippet) o le [rotte nominate](#rotte-nominate) possono apparire opzionalmente subito dopo.

- Altrimenti, la prima riga del Caddyfile è **sempre** l'[indirizzo (o gli indirizzi)](#indirizzi) del sito da servire.

- Tutte le [direttive](#direttive) e i [matcher](#matcher) **devono** essere inseriti in un blocco sito. Non esiste un ambito globale o ereditarietà tra i blocchi sito.

- If esiste un solo blocco sito, le sue parentesi graffe `{ }` sono opzionali.

Un Caddyfile consiste in almeno uno o più blocchi sito, ciascuno dei quali inizia sempre con uno o più [indirizzi](#indirizzi) per il sito. Qualsiasi direttiva che appaia prima dell'indirizzo confonderà il parser.


### Blocchi

L'apertura e la chiusura di un **blocco** si effettuano con le parentesi graffe:

```
... {
	...
}
```

- La parentesi graffa di apertura `{` deve trovarsi alla fine della sua riga ed essere preceduta da uno spazio.

- La parentesi graffa di chiusura `}` deve trovarsi su una riga a sé stante.

Quando c'è un solo blocco sito, le parentesi graffe (e l'indentazione) sono opzionali. Questo serve per comodità per definire velocemente un singolo sito, ad esempio questo:

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

è equivalente a:

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

quando si ha un solo blocco sito; è una questione di preferenza.

Per configurare più siti con lo stesso Caddyfile, **dovete** usare le parentesi graffe attorno a ciascuno di essi per separarne le configurazioni:

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

Se una richiesta corrisponde a più blocchi sito, viene scelto il blocco sito con l'indirizzo corrispondente più specifico. Le richieste non "cascano" in altri blocchi sito.


### Direttive

Le [**direttive**](/docs/caddyfile/directives) sono parole chiave funzionali che personalizzano il modo in cui il sito viene servito. **Devono** apparire all'interno dei blocchi sito. Ad esempio, una configurazione completa del server di file potrebbe apparire così:

```caddy
localhost {
	file_server
}
```

Or a reverse proxy:

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

In questi esempi, [`file_server`](/docs/caddyfile/directives/file_server) e [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) sono direttive. Le direttive sono la prima parola di una riga in un blocco sito.

Nel secondo esempio, `localhost:9000` è un **argomento** perché appare sulla stessa riga dopo la direttiva.

A volte le direttive possono aprire i propri blocchi. Le **sottodirettive** appaiono all'inizio di ogni riga all'interno dei blocchi delle direttive:

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

Qui, `lb_policy` è una sottodirettiva di [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) (imposta la policy di bilanciamento del carico da usare tra i backend).

**Salvo diversa documentazione, le direttive non possono essere usate all'interno di altri blocchi direttiva.** Ad esempio, [`basic_auth`](/docs/caddyfile/directives/basic_auth) non può essere usata all'interno di [`file_server`](/docs/caddyfile/directives/file_server) perché il file server non sa come gestire l'autenticazione; ma potete usare le direttive all'interno dei blocchi [`route`](/docs/caddyfile/directives/route), [`handle`](/docs/caddyfile/directives/handle) e [`handle_path`](/docs/caddyfile/directives/handle_path) perché sono specificamente progettati per raggruppare le direttive.

Si noti che quando l'HTTP Caddyfile viene adattato, le direttive degli handler HTTP vengono ordinate secondo uno specifico [ordine delle direttive](/docs/caddyfile/directives#directive-order) predefinito, a meno che non si trovino in un blocco [`route`](/docs/caddyfile/directives/route); pertanto, l'ordine di apparizione delle direttive non ha importanza, tranne che nei blocchi `route`.


### Token e virgolette

Il Caddyfile viene analizzato lessicalmente in token prima di essere processato. Lo spazio bianco è significativo nel Caddyfile, perché i token sono separati proprio dagli spazi bianchi.

Spesso le direttive si aspettano un certo numero di argomenti; se un singolo argomento ha un valore contenente spazi bianchi, verrebbe interpretato come due token separati:

```caddy-d
directive abc def
```

Ciò potrebbe essere problematico e restituire errori o comportamenti imprevisti.

Se `abc def` deve essere il valore di un singolo argomento, deve essere racchiuso tra virgolette:

```caddy-d
directive "abc def"
```

Le virgolette possono essere precedute da un carattere di escape se avete bisogno di usare virgolette all'interno di token già virgolettati:

```caddy-d
directive "\"abc def\""
```

Per evitare l'escape delle virgolette, potete invece usare gli accenti gravi <code>` `</code> per racchiudere i token; per esempio:

```caddy-d
directive `{"foo": "bar"}`
```

All'interno dei token virgolettati, tutti gli altri caratteri sono trattati letteralmente, inclusi spazi, tabulazioni e ritorni a capo. Sono quindi possibili token su più righe:

```caddy-d
directive "prima riga
	seconda riga"
```

Sono supportati anche gli <span id="heredocs"/>heredoc:

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

Il marcatore di apertura dell'heredoc deve iniziare con `<<`, seguito da qualsiasi testo (consigliate le lettere maiuscole). Il marcatore di chiusura dell'heredoc deve essere lo stesso testo (nell'esempio sopra, `HTML`). Il marcatore di apertura può essere preceduto da un escape `\<<` per impedire l'interpretazione dell'heredoc, se necessario.

Il marcatore di chiusura può essere indentato, il che fa sì che ogni riga di testo venga privata di quella quantità di indentazione (ispirato da [PHP](https://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.heredoc)), il che è ottimo per la leggibilità all'interno dei [blocchi](#blocchi) garantendo al contempo un ottimo controllo degli spazi bianchi nel testo del token. Anche il ritorno a capo finale viene rimosso, ma può essere mantenuto aggiungendo una riga vuota extra prima del marcatore di chiusura.

Ulteriori token possono seguire il marcatore di chiusura come argomenti della direttiva (come nell'esempio sopra, il codice di stato `200`).


## Opzioni globali

Un Caddyfile può opzionalmente iniziare con uno speciale blocco senza chiavi, chiamato [blocco opzioni globali](/docs/caddyfile/options):

```caddy
{
	...
}
```

Se presente, deve essere il primissimo blocco nella configurazione.

Viene usato per impostare opzioni che si applicano globalmente, o non a un particolare sito. Al suo interno possono essere impostate solo le opzioni globali; non è possibile usare le normali direttive dei siti.

Ad esempio, per abilitare l'opzione globale `debug`, che viene comunemente usata per produrre log dettagliati per la risoluzione dei problemi:

```caddy
{
	debug
}
```

**[Leggete la pagina delle Opzioni Globali](/docs/caddyfile/options) per saperne di più.**



## Indirizzi

Un indirizzo appare sempre all'inizio del blocco sito, ed è solitamente la prima cosa nel Caddyfile.

Questi sono esempi di indirizzi validi:

| Indirizzo            | Effetto                            |
|----------------------|-----------------------------------|
| `example.com`        | HTTPS con [certificato pubblicamente affidabile](/docs/automatic-https#hostname-requirements) gestito |
| `*.example.com`      | HTTPS con [certificato wildcard pubblicamente affidabile](/docs/caddyfile/patterns#wildcard-certificates) gestito |
| `localhost`          | HTTPS con [certificato affidabile localmente](/docs/automatic-https#local-https) gestito |
| `http://`            | HTTP catch-all, influenzato da [`http_port`](/docs/caddyfile/options#http-port) |
| `https://`           | HTTPS catch-all, influenzato da [`https_port`](/docs/caddyfile/options#http-port) |
| `http://example.com` | HTTP esplicitamente, con un matcher `Host` |
| `example.com:443`    | HTTPS dovuto alla corrispondenza con il valore predefinito di [`https_port`](/docs/caddyfile/options#http-port) |
| `:443`               | HTTPS catch-all dovuto alla corrispondenza con il valore predefinito di [`https_port`](/docs/caddyfile/options#http-port) |
| `:8080`              | HTTP su porta non standard, nessun matcher `Host` |
| `localhost:8080`     | HTTPS su porta non standard, dovuto alla presenza di un dominio valido |
| `https://example.com:443` | HTTPS, ma avere sia `https://` che `:443` è ridondante |
| `127.0.0.1` | HTTPS, con un certificato IP affidabile localmente |
| `http://127.0.0.1` | HTTP, con un matcher `Host` dell'indirizzo IP (rifiuta `localhost`) |


<aside class="tip">
	L'[HTTPS automatico](/docs/automatic-https) è abilitato se l'indirizzo del vostro sito contiene un nome host o un indirizzo IP. Questo comportamento è puramente implicito, tuttavia, quindi non sovrascrive mai alcuna configurazione esplicita.

	Ad esempio, se l'indirizzo del sito è `http://example.com`, l'auto-HTTPS non si attiverà perché lo schema è esplicitamente `http://`.
</aside>


Dall'indirizzo, Caddy può potenzialmente dedurre lo schema, l'host e la porta del vostro sito. Se l'indirizzo è senza porta, il Caddyfile sceglierà la porta corrispondente allo schema se specificato, oppure verrà assunta la porta predefinita 443.

Se specificate un hostname, verranno accettate solo le richieste con un header `Host` corrispondente. In altre parole, se l'indirizzo del sito è `localhost`, Caddy non accetterà le richieste verso `127.0.0.1`.

Le wildcard (`*`) possono essere utilizzate, ma solo per rappresentare precisamente una etichetta dell'hostname. Ad esempio, `*.example.com` corrisponde a `foo.example.com` ma non a `foo.bar.example.com`, e `*` corrisponde a `localhost` ma non a `example.com`. Consultate il [pattern dei certificati wildcard](/docs/caddyfile/patterns#wildcard-certificates) per un esempio pratico.

Per intercettare tutti gli host, omettete la porzione dell'host nell'indirizzo, ad esempio semplicemente `https://`. Questo è utile quando si usa il [TLS on-demand](/docs/automatic-https#on-demand-tls), ovvero quando non conoscete i domini in anticipo.

Se più siti condividono la stessa definizione, potete elencarli tutti insieme, separati da spazi e virgole (è necessario almeno uno spazio). I seguenti tre esempi sono equivalenti:

```caddy
# Indirizzi sito separati da virgola
localhost:8080, example.com, www.example.com {
	...
}
```

oppure

```caddy
# Indirizzi sito separati da spazio
localhost:8080 example.com www.example.com {
	...
}
```

oppure

```caddy
# Indirizzi sito separati da virgola e nuova riga
localhost:8080,
example.com,
www.example.com {
	...
}
```

Un indirizzo deve essere unico; non potete specificare lo stesso indirizzo più di una volta.

I [placeholder](#placeholder) **non possono** essere usati negli indirizzi, ma potete usare al loro interno le [variabili d'ambiente](#variabili-dambiente) in stile Caddyfile:

```caddy
{$DOMAIN:localhost} {
	...
}
```

Per impostazione predefinita, i siti si associano (bind) a tutte le interfacce di rete. Se desiderate sovrascrivere questo comportamento, usate la [direttiva `bind`](/docs/caddyfile/directives/bind) o l'[opzione globale `default_bind`](/docs/caddyfile/options#default-bind).



## Matcher

Le [direttive](#direttive) degli handler HTTP si applicano a tutte le richieste per impostazione predefinita (salvo diversa documentazione).

I [matcher di richiesta](/docs/caddyfile/matchers) possono essere usati per classificare le richieste in base a determinati criteri. Con i matcher, potete specificare esattamente a quali richieste si applica una determinata direttiva.

Per le direttive che supportano i matcher, il primo argomento dopo la direttiva è il **token matcher**. Ecco alcuni esempi:

```caddy-d
root *           /var/www  # token matcher: *
root /index.html /var/www  # token matcher: /index.html
root @post       /var/www  # token matcher: @post
```

I token matcher possono essere omessi del tutto per far corrispondere tutte le richieste; ad esempio, `*` non deve essere fornito se l'argomento successivo non assomiglia a un matcher di percorso.

**[Leggete la pagina dei Matcher di richiesta](/docs/caddyfile/matchers) per saperne di più.**




## Placeholder

I [placeholder](/docs/conventions#placeholders) sono un modo semplice per iniettare valori dinamici nella vostra configurazione statica. Possono essere usati come argomenti di direttive e sottodirettive.

I placeholder sono delimitati su entrambi i lati da parentesi graffe `{ }` e contengono l'identificatore all'interno, ad esempio: `{foo.bar}`. La parentesi graffa di apertura del placeholder può essere preceduta da un escape `\{come.questo}` per evitarne la sostituzione. Gli identificatori dei placeholder sono tipicamente organizzati in namespace con punti per evitare collisioni tra i moduli.

Quali placeholder siano disponibili dipende dal contesto. Non tutti i placeholder sono disponibili in tutte le parti della configurazione. Ad esempio, [l'app HTTP imposta dei placeholder](/docs/json/apps/http/#docs) che sono disponibili solo nelle aree della configurazione relative alla gestione delle richieste HTTP (ovvero nelle [direttive](#direttive) e nei [matcher](#matcher) degli handler HTTP, ma *non* nella [configurazione `tls`](/docs/caddyfile/directives/tls)). Alcune direttive o matcher possono impostare i propri placeholder che possono essere usati da tutto ciò che li segue. Alcuni placeholder [sono disponibili globalmente](/docs/conventions#placeholders).

Potete usare qualsiasi placeholder nel Caddyfile, ma per comodità potete anche usare alcune di queste scorciatoie equivalenti che vengono espanse quando il Caddyfile viene analizzato:

| Caddyfile        | Sostituisce                            |
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

Non tutti i campi della configurazione supportano i placeholder, ma la maggior parte lo fa dove ci si aspetterebbe. Il supporto per i placeholder deve essere stato aggiunto esplicitamente a quei campi. Gli autori di plugin possono [leggere questo articolo](/docs/extending-caddy/placeholders) per imparare come aggiungere il supporto per i placeholder nei propri moduli.




## Snippet

Potete definire dei blocchi speciali chiamati snippet dando loro un nome racchiuso tra parentesi:

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

Potete poi riutilizzarli ovunque ne abbiate bisogno, usando la speciale direttiva [`import`](/docs/caddyfile/directives/import):

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

La direttiva [`import`](/docs/caddyfile/directives/import) può essere usata anche per includere altri file al suo posto. Se l'argomento non corrisponde a uno snippet definito, verrà provato come file. Supporta anche i glob per importare più file. Come caso speciale, può apparire in qualsiasi punto del Caddyfile (tranne che come argomento di un'altra direttiva), inclusi i punti all'esterno dei blocchi sito:

```caddy
{
	email admin@example.com
}

import sites/*
```

Potete passare argomenti a una configurazione importata (snippet o file) e usarli in questo modo:

```caddy
(snippet) {
	respond "Yahaha! Hai trovato {args[0]}!"
}

a.example.com {
	import snippet "Esempio A"
}

b.example.com {
	import snippet "Esempio B"
}
```

⚠️ <i>Sperimentale</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Potete anche passare un blocco opzionale a uno snippet importato, e usarli come segue:

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

**[Leggete la pagina della direttiva `import`](/docs/caddyfile/directives/import) per saperne di più.**


## Rotte nominate

⚠️ <i>Sperimentale</i>

Le rotte nominate usano una sintassi simile agli [snippet](#snippet); sono dei blocchi speciali definiti all'esterno dei blocchi sito, preceduti da `&(` e terminanti con `)`, con il nome nel mezzo.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

Potete poi riutilizzare questa rotta nominata all'interno di qualsiasi sito:

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

Questo è particolarmente utile per ridurre l'uso della memoria se la stessa rotta è necessaria in molti siti diversi, o se sono necessarie più condizioni di matcher diverse per invocare la stessa rotta.

**[Leggete la pagina della direttiva `invoke`](/docs/caddyfile/directives/invoke) per saperne di più.**



## Commenti

I commenti iniziano con `#` e proseguono fino alla fine della riga:

```caddy-d
# I commenti possono iniziare una riga
directive  # oppure andare alla fine
```

Il carattere cancelletto `#` per un commento non può apparire nel mezzo di un token (ovvero deve essere preceduto da uno spazio o apparire all'inizio di una riga). Ciò consente l'uso dei cancelletti all'interno degli URI o di altri valori senza richiedere la virgolettatura.



## Variabili d'ambiente

Se la vostra configurazione si affida alle variabili d'ambiente, potete usarle nel Caddyfile:

```caddy
{$ENV}
```

Le variabili d'ambiente in questa forma vengono sostituite **prima che inizi l'analisi del Caddyfile**, quindi possono espandersi in valori vuoti (ovvero `""`), token parziali, token completi o persino più token e righe.

Ad esempio, una variabile d'ambiente `UPSTREAMS="app1:8080 app2:8080 app3:8080"` si espanderebbe in più [token](#token-e-virgolette):

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

È possibile specificare un valore predefinito per quando la variabile d'ambiente non viene trovata, usando `:` come delimitatore tra il nome della variabile e il valore predefinito:

```caddy
{$DOMAIN:localhost} {

}
```

Se volete **posticipare la sostituzione** di una variabile d'ambiente fino al runtime, potete usare i [placeholder standard `{env.*}`](/docs/conventions#placeholders). Si noti che non tutti i parametri della configurazione supportano questi placeholder, poiché gli sviluppatori di moduli devono aggiungere una riga di codice per eseguire la sostituzione. Se sembra non funzionare, aprite una issue per richiederne il supporto.

Ad esempio, se avete installato il [plugin `caddy-dns/cloudflare` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns/cloudflare) e desiderate configurare la [sfida DNS](/docs/automatic-https#dns-challenge), potete passare la variabile d'ambiente `CLOUDFLARE_API_TOKEN` al plugin in questo modo:

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Se state eseguendo Caddy come servizio systemd, consultate [queste istruzioni](/docs/running#override) per impostare gli override del servizio al fine di definire le vostre variabili d'ambiente.
