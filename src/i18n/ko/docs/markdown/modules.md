<div id="module-list-container">
	<h1>모든 모듈</h1>
	<p>
		이 페이지는 등록된 모든 Caddy 모듈을 나열합니다. 모듈은 Caddy의 <a href="/docs/json">JSON 구성 구조</a>를 확장하는 플러그인입니다.
	</p>
	<p>
		빠른 검색을 위해 브라우저의 "페이지에서 찾기(Find in page)" 기능을 사용하는 것을 권장합니다.
	</p>
	<table id="module-list">
		<tr>
			<th></th>
			<th>모듈 ID</th>
			<th>설명</th>
		</tr>
		<!--JS로 채워짐-->
	</table>
</div>

<div id="module-docs-container">
	<div class="pad"><h1 class="module-name"><!--JS로 채워짐--></h1></div>
	<div id="module-multiple-repos">
		이름이 <b class="module-name"><!--JS로 채워짐--></b>인 모듈이 둘 이상 있습니다. 저장소로 하나를 선택하세요.
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
