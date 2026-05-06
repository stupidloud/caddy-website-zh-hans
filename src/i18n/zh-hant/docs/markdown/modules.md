<div id="module-list-container">
	<a id="all-modules"></a>
	<h1>所有模組</h1>
	<p>
		本頁面列出了所有已註冊的 Caddy 模組。模組是用於擴展 Caddy <a href="/docs/json">JSON 配置結構</a> 的插件。
	</p>
	<p>
		我們建議使用瀏覽器的「在頁面中尋找」功能來快速查找。
	</p>
	<table id="module-list">
		<tr>
			<th></th>
			<th>模組 ID</th>
			<th>描述</th>
		</tr>
		<!--Populated by JS-->
	</table>
</div>

<div id="module-docs-container">
	<div class="pad"><h1 class="module-name"><!--Populated by JS--></h1></div>
	<div id="module-multiple-repos">
		有多個名為 <b class="module-name"><!--Populated by JS--></b> 的模組。請根據其儲存庫選擇一個。
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