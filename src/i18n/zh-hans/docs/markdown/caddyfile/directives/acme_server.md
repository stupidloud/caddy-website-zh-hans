---
title: "acme_server（Caddyfile 指令）"
---

# acme_server

一个嵌入式的 [ACME 协议](https://tools.ietf.org/html/rfc8555)服务器处理程序。这使得 Caddy 实例能够为任何其他兼容 ACME 的软件（包括其他 Caddy 实例）签发证书。

启用后，匹配该路径的请求 `/acme/*` 的请求将由 ACME 服务器处理。


<span id="client-configuration"/>
## 客户端配置

使用 ACME 服务器的默认设置时，ACME 客户端只需配置为使用 `https://localhost/acme/local/directory` 作为其 ACME 端点。（`local` 是 Caddy 默认 CA 的 ID。）


<span id="syntax"/>
## 语法

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

- **ca** 指定用于签署证书的证书颁发机构 (CA) 的标识。默认值为 `local`，即 Caddy 的默认 CA，专用于本地使用的自签名证书，这在开发环境中最为常见。若需更广泛的应用，建议指定其他 CA 以避免混淆。若指定 ID 的 CA 尚未存在，系统将自动创建。请参阅 [PKI 应用的全局选项](/docs/caddyfile/options#pki-options)以配置其他 CA。

- **有效期**（默认值： `12h`) 是一个[时长](/docs/conventions#durations)参数，用于指定签发证书的有效期。该值必须小于用于签名[的中间证书](/docs/caddyfile/options#intermediate-lifetime)的有效期。除非绝对必要，否则不建议更改此值。

- **解析器**是指在查询 TXT 记录以解决 ACME DNS 验证时所使用的 DNS 解析器地址。 接受[网络地址](/docs/conventions#network-addresses)，默认使用 UDP 协议和 53 端口，除非另有指定。如果主机是 IP 地址，将直接拨号连接以解析上游服务器。如果主机不是 IP 地址，则使用 Go 标准库的[名称解析约定](https://golang.org/pkg/net/#hdr-Name_Resolution)进行解析。如果指定了多个解析器，则随机选择其中一个。

- **challenges** 用于设置启用的验证类型。如果未设置该选项，或者该指令未带参数，则所有验证类型均被启用。支持的值包括：http-01、tls-alpn-01、dns-01。

- **allow_wildcard_names** 启用签发包含通配符 SAN（主体替代名称）的证书

- **允许**、**拒绝**，用于配置 `acme_server`。策略评估遵循 Step-CA [在此处](https://smallstep.com/docs/step-ca/policies/#policy-evaluation)描述的标准。

	- **域名** 用于根据策略评估标准，设置允许或拒绝的主题域名。

	- **ip_ranges** 用于根据策略评估标准，设置允许或拒绝的主体 IP 地址范围。

<span id="examples"/>
## 示例

要托管一个 ACME 服务器，其 ID 为 `home` 位于 `acme.example.com`上托管，并通过[全局选项`pki`](/docs/caddyfile/options#pki-options)自定义CA，同时使用 `internal` 签发者：

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

如果您还有另一台 Caddy 服务器，它可以利用上述 ACME 服务器签发自己的证书：

```caddy
{
	acme_ca https://acme.example.com/acme/home/directory
	acme_ca_root /path/to/home_ca_root.crt
}

example.com {
	respond "Hello, world!"
}
```
