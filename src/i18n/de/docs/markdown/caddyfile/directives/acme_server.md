---
title: acme_server (Caddyfile directive)
---

# acme_server

Ein eingebetteter Handler für einen [ACME protocol](https://tools.ietf.org/html/rfc8555)-Server. Damit kann eine Caddy-Instanz Zertifikate für jede andere ACME-kompatible Software ausstellen, einschließlich anderer Caddy-Instanzen.

Wenn aktiviert, werden Requests, die auf den Pfad `/acme/*` passen, vom ACME-Server verarbeitet.


<a id="client-configuration"></a>
## Client-Konfiguration

Mit den Standardwerten des ACME-Servers sollten ACME-Clients einfach `https://localhost/acme/local/directory` als ACME-Endpunkt verwenden. (`local` ist die ID von Caddys Standard-CA.)


<a id="syntax"></a>
## Syntax

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

- **ca** gibt die ID der Zertifizierungsstelle an, mit der Zertifikate signiert werden. Standard ist `local`, Caddys Standard-CA für lokal verwendete, selbstsignierte Zertifikate, wie sie in Entwicklungsumgebungen am häufigsten sind. Für breitere Nutzung wird empfohlen, eine andere CA anzugeben, um Verwechslungen zu vermeiden. Wenn die CA mit der angegebenen ID noch nicht existiert, wird sie erstellt. Siehe die [globalen Optionen der PKI-App](/docs/caddyfile/options#pki-options), um alternative CAs zu konfigurieren.

- **lifetime** (Standard: `12h`) ist eine [Dauer](/docs/conventions#durations), welche die Gültigkeitsdauer ausgestellter Zertifikate angibt. Dieser Wert muss kleiner sein als die Lebensdauer des zum Signieren verwendeten [Zwischenzertifikats](/docs/caddyfile/options#intermediate-lifetime). Es wird nicht empfohlen, diesen Wert zu ändern, außer es ist unbedingt nötig.

- **resolvers** sind die Adressen der DNS-Resolver, die beim Nachschlagen der TXT-Records zum Lösen von ACME-DNS-Challenges verwendet werden. Akzeptiert [Netzwerkadressen](/docs/conventions#network-addresses), standardmäßig UDP und Port 53, sofern nicht anders angegeben. Wenn der Host eine IP-Adresse ist, wird er direkt angewählt, um den Upstream-Server aufzulösen. Wenn der Host keine IP-Adresse ist, werden die Adressen mit der [Namensauflösungs-Konvention](https://golang.org/pkg/net/#hdr-Name_Resolution) der Go-Standardbibliothek aufgelöst. Wenn mehrere Resolver angegeben sind, wird einer zufällig ausgewählt.

- **challenges** legt die aktivierten Challenge-Typen fest. Wenn nicht gesetzt oder die Direktive ohne Werte verwendet wird, sind alle Challenge-Typen aktiviert. Akzeptierte Werte sind: http-01, tls-alpn-01, dns-01.

- **allow_wildcard_names** erlaubt das Ausstellen von Zertifikaten mit Wildcard-SAN (Subject Alternative Name).

- **allow**, **deny** konfigurieren die Betriebsrichtlinie des `acme_server`. Die Auswertung der Richtlinie folgt den von Step-CA [hier](https://smallstep.com/docs/step-ca/policies/#policy-evaluation) beschriebenen Kriterien.

	- **domains** legt die Subject-Domainnamen fest, die gemäß den Kriterien der Richtlinienauswertung erlaubt oder verweigert werden.

	- **ip_ranges** legt die Subject-IP-Bereiche fest, die gemäß den Kriterien der Richtlinienauswertung erlaubt oder verweigert werden.

<a id="examples"></a>
## Beispiele

Einen ACME-Server mit der ID `home` auf der Domain `acme.example.com` bereitstellen, mit einer über die [globale Option `pki`](/docs/caddyfile/options#pki-options) angepassten CA, und sein eigenes Zertifikat mit dem `internal`-Issuer ausstellen:

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

Wenn Sie einen weiteren Caddy-Server haben, kann er den obigen ACME-Server verwenden, um eigene Zertifikate auszustellen:

```caddy
{
	acme_ca https://acme.example.com/acme/home/directory
	acme_ca_root /path/to/home_ca_root.crt
}

example.com {
	respond "Hello, world!"
}
```
