---
title: method (Caddyfile 지시어)
---

# method

요청의 HTTP 메서드를 변경합니다.


## 구문 <a id="syntax"></a>

```caddy-d
method [<matcher>] <method>
```

- **&lt;method&gt;** 는 요청을 변경할 HTTP 메서드입니다.


## 예제 <a id="examples"></a>

`/api` 아래의 모든 요청에 대해 메서드를 `POST`로 변경합니다:

```caddy-d
method /api* POST
```
