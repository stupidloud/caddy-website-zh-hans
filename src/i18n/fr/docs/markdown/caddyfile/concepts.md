---
title: Concepts du Caddyfile
---

# Concepts du Caddyfile

Ce document vous aidera à découvrir en détail le Caddyfile HTTP.

1. [Structure](#structure)
	- [Blocs](#blocks)
	- [Directives](#directives)
	- [Jetons et guillemets](#tokens-and-quotes)
2. [Options globales](#global-options)
3. [Adresses](#addresses)
4. [Sélecteurs (Matchers)](#matchers)
5. [Espaces réservés (Placeholders)](#placeholders)
6. [Extraits (Snippets)](#snippets)
7. [Routes nommées](#named-routes)
8. [Commentaires](#comments)
9. [Variables d'environnement](#environment-variables)


<a id="structure"></a>
## Structure

La structure du Caddyfile peut être décrite visuellement :

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
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">email</span> <span class="struct-opt-value">you@yours.com</span></div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-opt-name">servers</span> {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-indent-spacer"></span><span class="struct-subdir">trusted_proxies</span> <span class="struct-arg">static</span> <span class="struct-arg">private_ranges</span></div>
						<div class="struct-line"><span class="struct-indent-spacer"></span>}</div>
						<div class="struct-line">}</div>
					</div>
					<div class="struct-block snippet">
						<div class="struct-line">(snippet) {</div>
						<div class="struct-line struct-indent"><span class="struct-indent-spacer"></span><span class="struct-comment"># ceci est un extrait réutilisable</span></div>
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
				<div class="struct-legend-title">Légende</div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-global)"></div><div class="struct-label">Bloc d'options globales</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-snippet)"></div><div class="struct-label">Extrait (Snippet)</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-site)"></div><div class="struct-label">Bloc de site</div></div>
				<div class="struct-item"><div class="struct-swatch-border" style="border-color:var(--struct-border-matcher)"></div><div class="struct-label">Définition de sélecteur</div></div>
				<div class="struct-item-spacer"></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-name-bg)"></div><div class="struct-label">Nom de l'option</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-opt-value-bg)"></div><div class="struct-label">Valeur de l'option</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-comment-bg)"></div><div class="struct-label">Commentaire</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-site-addr-bg)"></div><div class="struct-label">Adresse du site</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-directive-bg)"></div><div class="struct-label">Directive</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-matcher-token-bg)"></div><div class="struct-label">Jeton de sélecteur</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-arg-bg)"></div><div class="struct-label">Argument</div></div>
				<div class="struct-item"><div class="struct-swatch-fill" style="background:var(--struct-subdir-bg)"></div><div class="struct-label">Sous-directive</div></div>
			</div>
		</div>
	</div>
</div>

Points clés :

- Un [**bloc d'options globales**](#global-options) optionnel peut être la toute première chose dans le fichier.

- Des [extraits (snippets)](#snippets) ou des [routes nommées](#named-routes) peuvent optionnellement apparaître ensuite.

- Sinon, la première ligne du Caddyfile est **toujours** la ou les [adresses](#addresses) du site à servir.

- Toutes les [directives](#directives) et [sélecteurs](#matchers) **doivent** se trouver dans un bloc de site. Il n'y a pas de portée globale ou d'héritage entre les blocs de site.

- S'il n'y a qu'un seul bloc de site, ses accolades `{ }` sont optionnelles.

Un Caddyfile se compose d'au moins un ou plusieurs blocs de site, qui commencent toujours par une ou plusieurs [adresses](#addresses) pour le site. Toute directive apparaissant avant l'adresse sèmera la confusion chez l'analyseur.


<a id="blocks"></a>
### Blocs

L'ouverture et la fermeture d'un **bloc** se font avec des accolades :

```
... {
	...
}
```

- L'accolade ouvrante `{` doit être à la fin de sa ligne et précédée d'un espace.

- L'accolade fermante `}` doit être sur sa propre ligne.

Lorsqu'il n'y a qu'un seul bloc de site, les accolades (et l'indentation) sont optionnelles. C'est pratique pour définir rapidement un site unique, par exemple ceci :

```caddy
localhost

reverse_proxy /api/* localhost:9001
file_server
```

est équivalent à :

```caddy
localhost {
	reverse_proxy /api/* localhost:9001
	file_server
}
```

lorsque vous n'avez qu'un seul bloc de site ; c'est une question de préférence.

Pour configurer plusieurs sites avec le même Caddyfile, vous **devez** utiliser des accolades autour de chacun d'eux pour séparer leurs configurations :

```caddy
example1.com {
	root /www/example.com
	file_server
}

example2.com {
	reverse_proxy localhost:9000
}
```

Si une requête correspond à plusieurs blocs de site, le bloc de site ayant l'adresse de correspondance la plus précise est choisi. Les requêtes ne cascaderont pas vers d'autres blocs de site.


<a id="directives"></a>
### Directives

Les [**directives**](/docs/caddyfile/directives) sont des mots-clés fonctionnels qui personnalisent la manière dont le site est servi. Elles **doivent** apparaître à l'intérieur des blocs de site. Par exemple, une configuration complète de serveur de fichiers pourrait ressembler à ceci :

```caddy
localhost {
	file_server
}
```

Ou un proxy inverse :

```caddy
localhost {
	reverse_proxy localhost:9000
}
```

Dans ces exemples, [`file_server`](/docs/caddyfile/directives/file_server) et [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) sont des directives. Les directives sont le premier mot d'une ligne dans un bloc de site.

Dans le second exemple, `localhost:9000` est un **argument** car il apparaît sur la même ligne après la directive.

Parfois, les directives peuvent ouvrir leurs propres blocs. Les **sous-directives** apparaissent au début de chaque ligne à l'intérieur des blocs de directives :

```caddy
localhost {
	reverse_proxy localhost:9000 localhost:9001 {
		lb_policy first
	}
}
```

Ici, `lb_policy` est une sous-directive de [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) (elle définit la politique d'équilibrage de charge à utiliser entre les backends).

**Sauf indication contraire, les directives ne peuvent pas être utilisées à l'intérieur d'autres blocs de directives.** Par exemple, [`basic_auth`](/docs/caddyfile/directives/basic_auth) ne peut pas être utilisé à l'intérieur de [`file_server`](/docs/caddyfile/directives/file_server) car le serveur de fichiers ne sait pas comment effectuer l'authentification ; mais vous pouvez utiliser des directives à l'intérieur des blocs [`route`](/docs/caddyfile/directives/route), [`handle`](/docs/caddyfile/directives/handle), et [`handle_path`](/docs/caddyfile/directives/handle_path) car ils sont spécifiquement conçus pour regrouper les directives entre elles.

Notez que lorsque le Caddyfile HTTP est adapté, les directives de gestionnaire HTTP sont triées selon un [ordre de directives](/docs/caddyfile/directives#directive-order) par défaut spécifique, sauf si elles se trouvent dans un bloc [`route`](/docs/caddyfile/directives/route). Ainsi, l'ordre d'apparition des directives n'a pas d'importance, sauf dans les blocs `route`.


<a id="tokens-and-quotes"></a>
### Jetons et guillemets

Le Caddyfile est découpé en jetons (tokens) avant d'être analysé. Les espaces blancs sont significatifs dans le Caddyfile, car les jetons sont séparés par des espaces blancs.

Souvent, les directives attendent un certain nombre d'arguments ; si un seul argument possède une valeur contenant des espaces blancs, il serait découpé en deux jetons distincts :

```caddy-d
directive abc def
```

Cela pourrait s'avérer problématique et retourner des erreurs ou un comportement inattendu.

Si `abc def` est censé être la valeur d'un seul argument, il doit être entouré de guillemets :

```caddy-d
directive "abc def"
```

Les guillemets peuvent être échappés si vous devez utiliser des guillemets à l'intérieur de jetons eux-mêmes entre guillemets :

```caddy-d
directive "\"abc def\""
```

Pour éviter d'échapper les guillemets, vous pouvez utiliser des accents graves <code>\` \`</code> pour entourer les jetons ; par exemple :

```caddy-d
directive `{"foo": "bar"}`
```

À l'intérieur des jetons entre guillemets, tous les autres caractères sont traités littéralement, y compris les espaces, les tabulations et les sauts de ligne. Les jetons multi-lignes sont donc possibles :

```caddy-d
directive "première ligne
	seconde ligne"
```

Les Heredocs <span id="heredocs"/> sont également supportés :

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

Le marqueur d'ouverture heredoc doit commencer par `<<`, suivi de n'importe quel texte (les lettres majuscules sont recommandées). Le marqueur de fermeture heredoc doit être le même texte (dans l'exemple ci-dessus, `HTML`). Le marqueur d'ouverture peut être échappé par `\<<` pour empêcher l'analyse heredoc, si nécessaire.

Le marqueur de fermeture peut être indenté, ce qui entraîne la suppression d'autant d'indentation sur chaque ligne de texte (inspiré par [PHP](https://www.php.net/manual/fr/language.types.string.php#language.types.string.syntax.heredoc)), ce qui est agréable pour la lisibilité à l'intérieur des [blocs](#blocks) tout en offrant un grand contrôle des espaces blancs dans le texte du jeton. Le saut de ligne final est également supprimé, mais peut être conservé en ajoutant une ligne vide supplémentaire avant le marqueur de fermeture.

Des jetons supplémentaires peuvent suivre le marqueur de fermeture en tant qu'arguments de la directive (comme dans l'exemple ci-dessus, le code d'état `200`).


<a id="global-options"></a>
## Options globales

Un Caddyfile peut optionnellement commencer par un bloc spécial n'ayant aucune clé, appelé [bloc d'options globales](/docs/caddyfile/options) :

```caddy
{
	...
}
```

S'il est présent, il doit être le tout premier bloc de la configuration.

Il sert à définir des options qui s'appliquent globalement, ou qui ne s'appliquent à aucun site en particulier. À l'intérieur, seules les options globales peuvent être définies ; vous ne pouvez pas y utiliser les directives habituelles de site.

Par exemple, pour activer l'option globale `debug`, couramment utilisée pour produire des journaux verbeux lors d'un dépannage :

```caddy
{
	debug
}
```

**[Lisez la page des Options Globales](/docs/caddyfile/options) pour en savoir plus.**



<a id="addresses"></a>
## Adresses

Une adresse apparaît toujours en haut du bloc de site, et constitue généralement la première chose dans le Caddyfile.

Voici des exemples d'adresses valides :

| Adresse              | Effet                            |
|----------------------|-----------------------------------|
| `example.com`        | HTTPS avec [certificat de confiance publique](/docs/automatic-https#hostname-requirements) géré |
| `*.example.com`      | HTTPS avec [certificat wildcard de confiance publique](/docs/caddyfile/patterns#wildcard-certificates) géré |
| `localhost`          | HTTPS avec [certificat de confiance locale](/docs/automatic-https#local-https) géré |
| `http://`            | HTTP générique (catch-all), affecté par [`http_port`](/docs/caddyfile/options#http-port) |
| `https://`           | HTTPS générique (catch-all), affecté par [`https_port`](/docs/caddyfile/options#http-port) |
| `http://example.com` | HTTP explicitement, avec un sélecteur `Host` |
| `example.com:443`    | HTTPS car correspond au port par défaut de [`https_port`](/docs/caddyfile/options#http-port) |
| `:443`               | HTTPS générique car correspond au port par défaut de [`https_port`](/docs/caddyfile/options#http-port) |
| `:8080`              | HTTP sur port non standard, pas de sélecteur `Host` |
| `localhost:8080`     | HTTPS sur port non standard, en raison de la présence d'un domaine valide |
| `https://example.com:443` | HTTPS, mais avoir à la fois `https://` et `:443` est redondant |
| `127.0.0.1` | HTTPS, avec un certificat IP de confiance locale |
| `http://127.0.0.1` | HTTP, avec un sélecteur `Host` par adresse IP (rejette `localhost`) |


<aside class="tip">

Le [HTTPS automatique](/docs/automatic-https) est activé si l'adresse de votre site contient un nom d'hôte ou une adresse IP. Ce comportement est purement implicite, cependant, il n'écrase donc jamais une configuration explicite.

Par exemple, si l'adresse du site est `http://example.com`, le HTTPS automatique ne s'activera pas car le schéma est explicitement `http://`.

</aside>


À partir de l'adresse, Caddy peut potentiellement déduire le schéma, l'hôte et le port de votre site. Si l'adresse n'a pas de port, le Caddyfile choisira le port correspondant au schéma s'il est spécifié, sinon le port par défaut 443 sera supposé.

Si vous spécifiez un nom d'hôte, seules les requêtes possédant un en-tête `Host` correspondant seront acceptées. En d'autres termes, si l'adresse du site est `localhost`, alors Caddy ne fera pas correspondre les requêtes vers `127.0.0.1`.

Des caractères génériques (`*`) peuvent être utilisés, mais uniquement pour représenter précisément un segment du nom d'hôte. Par exemple, `*.example.com` correspond à `foo.example.com` mais pas à `foo.bar.example.com`, et `*` correspond à `localhost` mais pas à `example.com`. Voir le [modèle des certificats wildcard](/docs/caddyfile/patterns#wildcard-certificates) pour un exemple pratique.

Pour intercepter tous les hôtes, omettez la portion hôte de l'adresse, par exemple, simplement `https://`. C'est utile lors de l'utilisation du [TLS à la demande (On-Demand TLS)](/docs/automatic-https#on-demand-tls), lorsque vous ne connaissez pas les domaines à l'avance.

Si plusieurs sites partagent la même définition, vous pouvez les lister tous ensemble, séparés par des espaces et des virgules (au moins un espace est nécessaire). Les trois exemples suivants sont équivalents :

```caddy
# Adresses de site séparées par des virgules
localhost:8080, example.com, www.example.com {
	...
}
```

ou

```caddy
# Adresses de site séparées par des espaces
localhost:8080 example.com www.example.com {
	...
}
```

ou

```caddy
# Adresses de site séparées par des virgules et des sauts de ligne
localhost:8080,
example.com,
www.example.com {
	...
}
```

Une adresse doit être unique ; vous ne pouvez pas spécifier la même adresse plus d'une fois.

Les [espaces réservés (placeholders)](#placeholders) **ne peuvent pas** être utilisés dans les adresses, mais vous pouvez y utiliser des [variables d'environnement](#environment-variables) de style Caddyfile :

```caddy
{$DOMAIN:localhost} {
	...
}
```

Par défaut, les sites se lient sur toutes les interfaces réseau. Si vous souhaitez surcharger cela, utilisez la [directive `bind`](/docs/caddyfile/directives/bind) ou l'[option globale `default_bind`](/docs/caddyfile/options#default-bind).



<a id="matchers"></a>
## Sélecteurs (Matchers)

Les [directives](#directives) de gestionnaire HTTP s'appliquent à toutes les requêtes par défaut (sauf indication contraire).

Les [sélecteurs de requête (request matchers)](/docs/caddyfile/matchers) peuvent être utilisés pour classer les requêtes selon des critères donnés. Avec les sélecteurs, vous pouvez spécifier exactement à quelles requêtes une certaine directive s'applique.

Pour les directives supportant les sélecteurs, le premier argument après la directive est le **jeton de sélecteur**. Voici quelques exemples :

```caddy-d
root *           /var/www  # jeton de sélecteur : *
root /index.html /var/www  # jeton de sélecteur : /index.html
root @post       /var/www  # jeton de sélecteur : @post
```

Les jetons de sélecteur peuvent être entièrement omis pour correspondre à toutes les requêtes ; par exemple, `*` n'a pas besoin d'être fourni si l'argument suivant ne ressemble pas à un sélecteur de chemin.

**[Lisez la page des Sélecteurs de Requête](/docs/caddyfile/matchers) pour en savoir plus.**




<a id="placeholders"></a>
## Espaces réservés (Placeholders)

Les [espaces réservés (placeholders)](/docs/conventions#placeholders) sont un moyen simple d'injecter des valeurs dynamiques dans votre configuration statique. Ils peuvent être utilisés comme arguments pour les directives et sous-directives.

Les espaces réservés sont entourés de chaque côté par des accolades `{ }` et contiennent l'identifiant à l'intérieur, par exemple : `{foo.bar}`. L'accolade d'ouverture de l'espace réservé peut être échappée `\{comme.ceci}` pour empêcher le remplacement. Les identifiants d'espaces réservés possèdent généralement des espaces de noms séparés par des points pour éviter les collisions entre modules.

Les espaces réservés disponibles dépendent du contexte. Ils ne sont pas tous disponibles dans toutes les parties de la configuration. Par exemple, [l'application HTTP définit des espaces réservés](/docs/json/apps/http/#docs) qui ne sont accessibles que dans les zones de configuration liées au traitement des requêtes HTTP (c'est-à-dire dans les [directives](#directives) et [sélecteurs](#matchers) de gestionnaire HTTP, mais *pas* dans la [configuration `tls`](/docs/caddyfile/directives/tls)). Certaines directives ou sélecteurs peuvent également définir leurs propres espaces réservés qui peuvent être utilisés par tout ce qui les suit. Certains espaces réservés [sont disponibles globalement](/docs/conventions#placeholders).

Vous pouvez utiliser n'importe quel espace réservé dans le Caddyfile, mais par commodité, vous pouvez également utiliser certains de ces raccourcis équivalents qui sont développés lors de l'analyse du Caddyfile :

| Caddyfile        | Remplace                            |
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

Tous les champs de configuration ne supportent pas les espaces réservés, mais la plupart le font là où on s'y attendrait. Le support des espaces réservés doit avoir été explicitement ajouté à ces champs. Les auteurs de plugins peuvent [lire cet article](/docs/extending-caddy/placeholders) pour apprendre comment ajouter le support des espaces réservés dans leurs propres modules.




<a id="snippets"></a>
## Extraits (Snippets)

Vous pouvez définir des blocs spéciaux appelés extraits (snippets) en leur donnant un nom entouré de parenthèses :

```caddy
(logging) {
	log {
		output file /var/log/caddy.log
		format json
	}
}
```

Et vous pouvez ensuite les réutiliser partout où vous en avez besoin, en utilisant la directive spéciale [`import`](/docs/caddyfile/directives/import) :

```caddy
example.com {
	import logging
}

www.example.com {
	import logging
}
```

La directive [`import`](/docs/caddyfile/directives/import) peut également être utilisée pour inclure d'autres fichiers à sa place. Si l'argument ne correspond pas à un extrait défini, il sera tenté comme un fichier. Elle supporte également les globs pour importer plusieurs fichiers. Cas particulier : elle peut apparaître n'importe où dans le Caddyfile (sauf comme argument d'une autre directive), y compris en dehors des blocs de site :

```caddy
{
	email admin@example.com
}

import sites/*
```

Vous pouvez passer des arguments à une configuration importée (extraits ou fichiers) et les utiliser ainsi :

```caddy
(snippet) {
	respond "Yahaha! Vous avez trouvé {args[0]} !"
}

a.example.com {
	import snippet "Exemple A"
}

b.example.com {
	import snippet "Exemple B"
}
```

⚠️ <i>Expérimental</i> <span style='white-space: pre;'> | </span> <span>v2.9.x+</span>

Vous pouvez également passer un bloc optionnel à un extrait importé, et l'utiliser comme suit.

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

**[Lisez la page de la directive `import`](/docs/caddyfile/directives/import) pour en savoir plus.**


<a id="named-routes"></a>
## Routes nommées

⚠️ <i>Expérimental</i>

Les routes nommées utilisent une syntaxe similaire aux [extraits (snippets)](#snippets) ; c'est un bloc spécial défini en dehors des blocs de site, préfixé par `&(` et se terminant par `)` avec le nom entre les deux.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080
}
```

Et vous pouvez ensuite réutiliser cette route nommée dans n'importe quel site :

```caddy
example.com {
	invoke app-proxy
}

www.example.com {
	invoke app-proxy
}
```

Ceci est particulièrement utile pour réduire l'utilisation de la mémoire si la même route est nécessaire dans de nombreux sites différents, ou si plusieurs conditions de sélecteur différentes sont nécessaires pour invoquer la même route.

**[Lisez la page de la directive `invoke`](/docs/caddyfile/directives/invoke) pour en savoir plus.**



<a id="comments"></a>
## Commentaires

Les commentaires commencent par `#` et se poursuivent jusqu'à la fin de la ligne :

```caddy-d
# Les commentaires peuvent commencer une ligne
directive  # ou aller à la fin
```

Le caractère dièse `#` pour un commentaire ne peut pas apparaître au milieu d'un jeton (c'est-à-dire qu'il doit être précédé d'un espace ou apparaître au début d'une ligne). Cela permet l'utilisation de dièses à l'intérieur des URIs ou d'autres valeurs sans nécessiter de guillemets.



<a id="environment-variables"></a>
## Variables d'environnement

Si votre configuration repose sur des variables d'environnement, vous pouvez les utiliser dans le Caddyfile :

```caddy
{$ENV}
```

Les variables d'environnement sous cette forme sont substituées **avant que l'analyse du Caddyfile ne commence**, elles peuvent donc se développer en valeurs vides (c'est-à-dire `""`), jetons partiels, jetons complets, ou même jetons et lignes multiples.

Par exemple, une variable d'environnement `UPSTREAMS="app1:8080 app2:8080 app3:8080"` se développerait en plusieurs [jetons](#tokens-and-quotes) :

```caddy
example.com {
	reverse_proxy {$UPSTREAMS}
}
```

Une valeur par défaut peut être spécifiée pour les cas où la variable d'environnement n'est pas trouvée, en utilisant `:` comme délimiteur entre le nom de la variable et la valeur par défaut :

```caddy
{$DOMAIN:localhost} {

}
```

Si vous souhaitez **différer la substitution** d'une variable d'environnement jusqu'à l'exécution, vous pouvez utiliser les [espaces réservés `{env.*}` standards](/docs/conventions#placeholders). Notez que tous les paramètres de configuration ne supportent pas ces espaces réservés cependant, car les développeurs de modules doivent ajouter une ligne de code pour effectuer le remplacement. Si cela ne semble pas fonctionner, veuillez ouvrir un ticket pour demander le support de cette fonctionnalité.

Par exemple, si vous avez le [plugin `caddy-dns/cloudflare` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns/cloudflare) installé et souhaitez configurer le [défi DNS](/docs/automatic-https#dns-challenge), vous pouvez passer votre variable d'environnement `CLOUDFLARE_API_TOKEN` au plugin comme ceci :

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

Si vous faites tourner Caddy en tant que service systemd, consultez [ces instructions](/docs/running#overrides) pour définir des surcharges de service afin de définir vos variables d'environnement.
