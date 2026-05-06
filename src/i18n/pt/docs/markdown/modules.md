---
title: Módulos
---

<div id="module-list-container">
	<h1>Todos os módulos</h1>
	<p>
		Esta página lista todos os módulos registrados do Caddy. Módulos são plugins que estendem a <a href="/docs/json">estrutura de configuração JSON</a> do Caddy.
	</p>
	<p>
		Recomendamos usar a função "Localizar na página" do seu navegador para buscas rápidas.
	</p>
	<table id="module-list">
		<tr>
			<th></th>
			<th>ID do módulo</th>
			<th>Descrição</th>
		</tr>
		<!--Preenchido por JS-->
	</table>
</div>

<div id="module-docs-container">
	<div class="pad"><h1 class="module-name"><!--Preenchido por JS--></h1></div>
	<div id="module-multiple-repos">
		Há mais de um módulo chamado <b class="module-name"><!--Preenchido por JS--></b>. Escolha um pelo seu repositório.
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
