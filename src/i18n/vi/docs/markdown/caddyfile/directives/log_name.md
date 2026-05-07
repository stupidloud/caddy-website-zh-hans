---
title: log_name (chỉ thị Caddyfile)
---

# log_name

Ghi đè tên logger được sử dụng cho một yêu cầu khi ghi nhật ký truy cập với [chỉ thị `log`](log).

Chỉ thị này hữu ích khi bạn muốn ghi lại các yêu cầu vào các tệp khác nhau dựa trên một số điều kiện, chẳng hạn như đường dẫn hoặc phương thức yêu cầu.

Có thể chỉ định nhiều hơn một tên logger, để nhật ký của yêu cầu được đẩy tới nhiều hơn một logger phù hợp.

Điều này thường được kết hợp với tùy chọn [`no_hostname`](log#no_hostname) của chỉ thị `log`, tùy chọn này ngăn logger được liên kết với bất kỳ tên miền nào của khối trang web, do đó chỉ những yêu cầu đặt `log_name` mới đẩy nhật ký tới logger đó.


<a id="syntax"></a>
## Cú pháp

```caddy-d
log_name [<matcher>] <names...>
```


<a id="examples"></a>
## Ví dụ

Bạn có thể muốn ghi nhật ký các yêu cầu vào các tệp khác nhau, ví dụ: bạn có thể muốn ghi nhật ký kiểm tra sức khỏe (health checks) vào một tệp riêng biệt so với nhật ký truy cập chính.

Sử dụng `no_hostname` trong một `log` sẽ ngăn logger được liên kết với bất kỳ tên miền nào của khối trang web (ví dụ: `localhost` ở đây), do đó chỉ những yêu cầu có `log_name` được đặt thành tên của logger đó mới nhận được nhật ký.

```caddy
localhost {
	log {
		output file ./caddy.access.log
	}

	log health_check_log {
		output file ./caddy.access.health.log
		no_hostname
	}

	handle /healthz* {
		log_name health_check_log
		respond "Healthy"
	}

	handle {
		respond "Hello World"
	}
}
```
