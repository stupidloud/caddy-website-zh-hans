<div id="module-list-container">
	<h1>所有模块</h1>
	<p>
		本页面列出了所有已注册的 Caddy 模块。模块是用于扩展 Caddy 的 [JSON 配置结构](/docs/json)的插件。
	</p>
	<p>
		我们建议您使用浏览器的“在页面中查找”功能进行快速查找。
	</p>
	<table id="module-list">
		<tr>
			<th></th>
			<th>模块 ID</th>
			<th>描述</th>
		</tr>
		<!--Populated by JS-->
	</table>
</div>

<div id="module-docs-container">
	<div class="pad"><h1 class="module-name"><!--Populated by JS--></h1></div>
	<div id="module-multiple-repos">
		有多个名为 <b class="module-name"><!--由 JS 填充--></b> 的模块。请根据其仓库选择其中一个。
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