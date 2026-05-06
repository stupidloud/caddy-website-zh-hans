---
title: acme_server (Caddyfile 指令)
---

<a id="acme-server"></a>
# acme_server

一個嵌入式的 [ACME 協定](https://tools.ietf.org/html/rfc8555) 伺服器處理器。這允許 Caddy 實例為任何其他相容 ACME 的軟體（包括其他 Caddy 實例）簽發憑證。

啟用後，匹配路徑 `/acme/*` 的請求將由 ACME 伺服器處理。


<a id="client-configuration"></a>
## 客戶端配置

使用 ACME 伺服器預設值時，ACME 客戶端只需配置為使用 `https://localhost/acme/local/directory` 作為其 ACME 端點。（`local` 是 Caddy 預設 CA 的 ID。）


<a id="syntax"></a>
## 語法

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

- **ca** 指定用於簽署憑證的憑證授權單位 (CA) 的 ID。預設為 `local`，這是 Caddy 的預設 CA，旨在用於本地使用的自簽名憑證，這在開發環境中最為常見。對於更廣泛的使用，建議指定不同的 CA 以避免混淆。如果具有給定 ID 的 CA 尚不存在，則會建立它。請參閱 [PKI 應用全域選項](/docs/caddyfile/options#pki-options) 以配置替代 CA。

- **lifetime** (預設：`12h`) 是一個 [時長](/docs/conventions#durations)，指定簽發憑證的有效期。此值必須小於用於簽署的 [中間憑證](/docs/caddyfile/options#intermediate-lifetime) 的壽命。除非絕對必要，否則不建議更改此值。

- **resolvers** 是在查找用於解決 ACME DNS 挑戰的 TXT 紀錄時要使用的 DNS 解析器位址。接受 [網路位址](/docs/conventions#network-addresses)，除非另有指定，否則預設為 UDP 和連接埠 53。如果主機是 IP 位址，它將直接撥號以解析上游伺服器。如果主機不是 IP 位址，則使用 Go 標準函式庫的 [名稱解析慣例](https://golang.org/pkg/net/#hdr-Name_Resolution) 來解析位址。如果指定了多個解析器，則隨機選擇一個。

- **challenges** 設定啟用的挑戰類型。如果未設定或指令在不含值的情況下使用，則啟用所有挑戰類型。接受的值為：http-01、tls-alpn-01、dns-01。

- **allow_wildcard_names** 允許簽發帶有萬用字元 SAN (主體別名) 的憑證。

- **allow**、**deny** 配置 `acme_server` 的運行策略。策略評估遵循 Step-CA 在 [此處](https://smallstep.com/docs/step-ca/policies/#policy-evaluation) 描述的準則。

	- **domains** 根據策略評估準則設定要允許或拒絕的主體網域名稱。

	- **ip_ranges** 根據策略評估準則設定要允許或拒絕的主體 IP 範圍。

<a id="examples"></a>
## 範例

要在網域 `acme.example.com` 上提供 ID 為 `home` 的 ACME 伺服器，並透過 [`pki` 全域選項](/docs/caddyfile/options#pki-options) 自訂 CA，並使用 `internal` 發行者簽發其自身的憑證：

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

如果你有另一個 Caddy 伺服器，它可以使用上述 ACME 伺服器來簽發其自身的憑證：

```caddy
{
	acme_ca https://acme.example.com/acme/home/directory
	acme_ca_root /path/to/home_ca_root.crt
}

example.com {
	respond "Hello, world!"
}
```
