<div id="module-list-container">
	<h1><a id="all-modules"></a>Todos los módulos</h1>
	<p>
		Esta página enumera todos los módulos registrados de Caddy. Los módulos son plugins que amplían la <a href="/docs/json">estructura de configuración JSON</a> de Caddy.
	</p>
	<p>
		Recomendamos usar la función "Buscar en la página" de tu navegador para búsquedas rápidas.
	</p>
	<table id="module-list">
		<tr>
			<th></th>
			<th>ID de módulo</th>
			<th>Descripción</th>
		</tr>
		<!--Populated by JS-->
	</table>
</div>

<div id="module-docs-container">
	<div class="pad"><h1 class="module-name"><!--Populated by JS--></h1></div>
	<div id="module-multiple-repos">
		Hay más de un módulo llamado <b class="module-name"><!--Populated by JS--></b>. Elige uno por su repositorio.
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
