---
title: acme_server (директива Caddyfile)
---

# acme_server

Встроенный handler сервера [протокола ACME](https://tools.ietf.org/html/rfc8555). Он позволяет экземпляру Caddy выпускать сертификаты для любого другого ACME-совместимого ПО (включая другие экземпляры Caddy).

Когда он включен, запросы, соответствующие пути `/acme/*`, будут обрабатываться ACME server.


<a id="client-configuration"></a>
## Конфигурация клиента

При использовании значений ACME server по умолчанию ACME clients достаточно настроить на использование `https://localhost/acme/local/directory` как ACME endpoint. (`local` — это ID стандартного CA Caddy.)


<a id="syntax"></a>
## Синтаксис

```caddy-d
acme_server [<matcher>] {
	ca         <id>
	lifetime   <duration>
	resolvers  <resolvers...>
	challenges <challenges...>
	allow_wildcard_names
	allow {
		domains <domains...>
		ip_ranges <addresses...>
	}
	deny {
		domains <domains...>
		ip_ranges <addresses...>
	}
}
```

- **ca** задает ID certificate authority, которым будут подписываться сертификаты. По умолчанию используется `local` — стандартный CA Caddy, предназначенный для локально используемых самоподписанных сертификатов, что чаще всего встречается в dev-средах. Для более широкого применения рекомендуется указать другой CA, чтобы избежать путаницы. Если CA с указанным ID еще не существует, он будет создан. См. [глобальные опции приложения PKI](/docs/caddyfile/options#pki-options), чтобы настроить альтернативные CA.

- **lifetime** (по умолчанию: `12h`) — это [duration](/docs/conventions#durations), задающая срок действия выпущенных сертификатов. Это значение должно быть меньше срока действия [intermediate certificate](/docs/caddyfile/options#intermediate-lifetime), используемого для подписи. Изменять его не рекомендуется, если в этом нет строгой необходимости.

- **resolvers** — адреса DNS resolvers, которые используются при поиске TXT records для решения ACME DNS challenges. Принимает [сетевые адреса](/docs/conventions#network-addresses), по умолчанию с UDP и портом 53, если не указано иное. Если host является IP-адресом, подключение будет выполнено напрямую для разрешения upstream server. Если host не является IP-адресом, адреса разрешаются по [соглашению о разрешении имен](https://golang.org/pkg/net/#hdr-Name_Resolution) стандартной библиотеки Go. Если указано несколько resolvers, один выбирается случайно.

- **challenges** задает включенные типы challenge. Если не задано или директива используется без значений, включаются все типы challenge. Допустимые значения: http-01, tls-alpn-01, dns-01.

- **allow_wildcard_names** включает выпуск сертификатов с wildcard SAN (Subject Alternative Name).

- **allow**, **deny** настраивают operational policy для `acme_server`. Оценка policy следует критериям, описанным Step-CA [здесь](https://smallstep.com/docs/step-ca/policies/#policy-evaluation).

	- **domains** задает subject domain names, которые разрешаются или запрещаются согласно критериям оценки policy.

	- **ip_ranges** задает subject IP ranges, которые разрешаются или запрещаются согласно критериям оценки policy.

<a id="examples"></a>
## Примеры

Чтобы обслуживать ACME server с ID `home` на домене `acme.example.com`, с CA, настроенным через [глобальную опцию `pki`](/docs/caddyfile/options#pki-options), и выпуском собственного сертификата с помощью issuer `internal`:

```caddy
{
	pki {
		ca home {
			name "My Home CA"
		}
	}
}

acme.example.com {
	tls {
		issuer internal {
			ca home
		}
	}
	acme_server {
		ca home
	}
}
```

Если у вас есть другой Caddy server, он может использовать приведенный выше ACME server для выпуска собственных сертификатов:

```caddy
{
	acme_ca https://acme.example.com/acme/home/directory
	acme_ca_root /path/to/home_ca_root.crt
}

example.com {
	respond "Hello, world!"
}
```
