---
title: method (chỉ thị Caddyfile)
---

# method

Thay đổi phương thức HTTP của yêu cầu.


<a id="syntax"></a>
## Cú pháp

```caddy-d
method [<matcher>] <method>
```

- **&lt;method&gt;** là phương thức HTTP muốn thay đổi yêu cầu thành.


<a id="examples"></a>
## Ví dụ

Thay đổi phương thức cho tất cả các yêu cầu trong `/api` thành `POST`:

```caddy-d
method /api* POST
```
