---
title: "Hỗ trợ Placeholder"
---

<a id="placeholders"></a>
# Placeholder

Trong Caddy, các placeholder được xử lý bởi từng plugin riêng lẻ khi cần thiết; chúng không tự động hoạt động ở mọi nơi.

Điều này có nghĩa là nếu bạn muốn plugin của mình hỗ trợ placeholder, bạn phải thêm hỗ trợ cho chúng một cách rõ ràng.

Nếu bạn chưa quen với placeholder, hãy bắt đầu bằng cách [đọc tại đây](/docs/conventions#placeholders)!

<a id="placeholders-overview"></a>
## Tổng quan về Placeholder

[Placeholder](/docs/conventions#placeholders) là một chuỗi có định dạng `{foo.bar}` được sử dụng làm các giá trị cấu hình động, được đánh giá sau đó tại thời điểm thực thi (runtime).

Việc [thay thế biến môi trường](/docs/caddyfile/concepts#environment-variables) trong Caddyfile bắt đầu bằng dấu đô la như `{$FOO}` được đánh giá tại thời điểm phân tích cú pháp Caddyfile, và không cần plugin của bạn xử lý. Đây _không phải_ là các placeholder, mặc dù chia sẻ cùng cú pháp `{ }`.

Do đó, điều quan trọng là phải hiểu rằng `{env.HOST}` (một [placeholder toàn cục](/docs/conventions#placeholders)) về bản chất khác với `{$HOST}` (một phép thay thế biến môi trường Caddyfile).

Ví dụ, hãy xem Caddyfile sau:
```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

Khi bạn chuyển đổi Caddyfile này sang JSON bằng `HOST=example caddy adapt`, bạn sẽ nhận được:

```json
{
  "apps": {
    "http": {
      "servers": {
        "srv0": {
          "listen": [":8080"],
          "routes": [
            {
              "handle": [
                {
                  "body": "example",
                  "handler": "static_response",
                  "status_code": 200
                }
              ]
            }
          ]
        },
        "srv1": {
          "listen": [":8081"],
          "routes": [
            {
              "handle": [
                {
                  "body": "{env.HOST}",
                  "handler": "static_response",
                  "status_code": 200
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```

Đặc biệt, hãy nhìn vào trường `"body"` trong cả `srv0` và `srv1`.

Vì `srv0` đã sử dụng `{$HOST}` (thay thế biến môi trường Caddyfile), giá trị đã trở thành `example`, vì nó được xử lý trong thời gian phân tích cú pháp Caddyfile khi tạo cấu hình JSON.

Vì `srv1` đã sử dụng `{env.HOST}` (một placeholder toàn cục), nó vẫn không thay đổi khi chuyển đổi sang JSON.

Điều này có nghĩa là người dùng viết cấu hình JSON (không sử dụng Caddyfile) không thể sử dụng cú pháp `{$ENV}`. Vì lý do đó, điều quan trọng là các tác giả plugin phải triển khai hỗ trợ thay thế placeholder khi cấu hình được cung cấp (provisioned). Điều này được giải thích bên dưới.


<a id="implementing-placeholder-support"></a>
## Triển khai hỗ trợ placeholder

Bạn không nên xử lý placeholder trong [`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile). Thay vào đó, các placeholder nên được thay thế sau đó, hoặc trong bước [`Provision()`](/docs/extending-caddy#provisioning), hoặc trong quá trình thực thi module của bạn (ví dụ: `ServeHTTP()` cho các trình xử lý HTTP, `Match()` cho các trình so khớp, v.v.), bằng cách sử dụng một `caddy.Replacer`.


<a id="examples"></a>
### Ví dụ

Ở đây, chúng ta đang sử dụng một replacer mới được khởi tạo để xử lý các placeholder. Nó có quyền truy cập vào các [placeholder toàn cục](/docs/conventions#placeholders) như `{env.HOST}`, nhưng _không_ truy cập được vào các placeholder HTTP như `{http.request.uri}` vì việc cung cấp (provisioning) diễn ra khi cấu hình được tải, chứ không phải trong một yêu cầu.

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

Ở đây, chúng ta lấy replacer từ ngữ cảnh yêu cầu `r.Context()` trong `ServeHTTP`. Replacer này có quyền truy cập vào cả các placeholder toàn cục _và_ các placeholder HTTP theo từng yêu cầu như `{http.request.uri}`.

```go
func (g *Gizmo) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	repl := r.Context().Value(caddy.ReplacerCtxKey).(*caddy.Replacer)
	_, err := w.Write([]byte(repl.ReplaceAll(g.Name,"")))
	if err != nil {
		return err
	}
	return next.ServeHTTP(w, r)
}
```
