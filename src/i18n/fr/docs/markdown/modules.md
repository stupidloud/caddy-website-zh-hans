<div id="module-list-container">
	<h1>Tous les modules</h1>
	<p>
		Cette page liste tous les modules Caddy enregistrés. Les modules sont des plugins qui étendent la <a href="/docs/json">structure de configuration JSON</a> de Caddy.
	</p>
	<p>
		Nous vous recommandons d'utiliser la fonction "Rechercher dans la page" de votre navigateur pour des recherches rapides.
	</p>
	<table id="module-list">
		<tr>
			<th></th>
			<th>ID du module</th>
			<th>Description</th>
		</tr>
		<!--Rempli par JS-->
	</table>
</div>

<div id="module-docs-container">
	<div class="pad"><h1 class="module-name"><!--Rempli par JS--></h1></div>
	<div id="module-multiple-repos">
		Il existe plusieurs modules nommés <b class="module-name"><!--Rempli par JS--></b>. Choisissez-en un selon son dépôt.
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