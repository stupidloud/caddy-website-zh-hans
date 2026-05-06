<div id="module-list-container">
	<h1>Все модули</h1>
	<p>
		На этой странице перечислены все зарегистрированные Caddy modules. Modules — это plugins, расширяющие <a href="/docs/json">структуру JSON-конфигурации</a> Caddy.
	</p>
	<p>
		Для быстрого поиска рекомендуем использовать функцию браузера "Найти на странице".
	</p>
	<table id="module-list">
		<tr>
			<th></th>
			<th>Module ID</th>
			<th>Описание</th>
		</tr>
		<!--Populated by JS-->
	</table>
</div>

<div id="module-docs-container">
	<div class="pad"><h1 class="module-name"><!--Populated by JS--></h1></div>
	<div id="module-multiple-repos">
		Есть больше одного module с именем <b class="module-name"><!--Populated by JS--></b>. Выберите нужный по его repository.
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
