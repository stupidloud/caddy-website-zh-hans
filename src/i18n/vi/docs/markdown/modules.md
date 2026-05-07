<div id="module-list-container">
	<h1>Tất cả mô-đun</h1>
	<p>
		Trang này liệt kê tất cả các mô-đun Caddy đã đăng ký. Các mô-đun là các plugin mở rộng <a href="/docs/json">cấu trúc cấu hình JSON</a> của Caddy.
	</p>
	<p>
		Chúng tôi khuyên bạn nên sử dụng tính năng "Tìm trong trang" của trình duyệt để tra cứu nhanh.
	</p>
	<table id="module-list">
		<tr>
			<th></th>
			<th>ID Mô-đun</th>
			<th>Mô tả</th>
		</tr>
		<!--Được điền bởi JS-->
	</table>
</div>

<div id="module-docs-container">
	<div class="pad"><h1 class="module-name"><!--Được điền bởi JS--></h1></div>
	<div id="module-multiple-repos">
		Có nhiều mô-đun có tên là <b class="module-name"><!--Được điền bởi JS--></b>. Hãy chọn một mô-đun theo kho lưu trữ của nó.
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
