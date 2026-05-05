<div id="module-list-container">
	<h1>すべてのモジュール</h1>
	<p>
		このページでは、登録済みのすべての Caddy モジュールを一覧表示します。モジュールは、Caddy の <a href="/docs/json">JSON 設定構造</a>を拡張するプラグインです。
	</p>
	<p>
		素早く探すには、ブラウザーの「ページ内検索」機能を使うことをおすすめします。
	</p>
	<table id="module-list">
		<tr>
			<th></th>
			<th>Module ID</th>
			<th>説明</th>
		</tr>
		<!--Populated by JS-->
	</table>
</div>

<div id="module-docs-container">
	<div class="pad"><h1 class="module-name"><!--Populated by JS--></h1></div>
	<div id="module-multiple-repos">
		<b class="module-name"><!--Populated by JS--></b> という名前のモジュールが複数あります。リポジトリを選んでください。
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
