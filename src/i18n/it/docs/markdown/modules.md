<div id="module-list-container">
	<h1>Tutti i moduli</h1>
	<p>
		Questa pagina elenca tutti i moduli registrati di Caddy. I moduli sono plugin che estendono la <a href="/docs/json">struttura di configurazione JSON</a> di Caddy.
	</p>
	<p>
		Raccomandiamo di usare la funzione "Trova nella pagina" del vostro browser per ricerche rapide.
	</p>
	<table id="module-list">
		<tr>
			<th></th>
			<th>ID Modulo</th>
			<th>Descrizione</th>
		</tr>
		<!--Popolato da JS-->
	</table>
</div>

<div id="module-docs-container">
	<div class="pad"><h1 class="module-name"><!--Popolato da JS--></h1></div>
	<div id="module-multiple-repos">
		Esiste più di un modulo chiamato <b class="module-name"><!--Popolato da JS--></b>. Scegline uno tramite il suo repository.
	</div>
	<div id="module-template" class="module-repo-container">
		<div class="module-repo-selector"></div>
		<article>
			{{include "/includes/docs/renderbox.html"}}
			{{include "/includes/docs/details.html"}}
		</article>
	</div>
</div>

{{include "/includes/docs/hovercard.html"}}
