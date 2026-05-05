---
title: tls (Caddyfile directive)
---

<script>
ready(function() {
	// Wir fügen Links zu allen Unterdirektiven hinzu, wenn ein passender Anker auf der Seite gefunden wird.
	addLinksToSubdirectives();
});
</script>

# tls

Konfiguriert TLS für die Site.

**Caddys standardmäßige TLS-Einstellungen sind sicher. Ändern Sie diese Einstellungen nur, wenn Sie einen guten Grund haben und die Auswirkungen verstehen.** Die häufigste Verwendung dieser Direktive ist die Angabe einer E-Mail-Adresse für das ACME-Konto, das Ändern des ACME-CA-Endpunkts oder das Bereitstellen eigener Zertifikate.

Kompatibilitätshinweis: Wegen der sensiblen Natur von TLS als Sicherheitsprotokoll können bewusste Anpassungen der TLS-Standardwerte in neuen Minor- oder Patch-Releases vorgenommen werden. Alte oder fehlerhafte TLS-Versionen, Cipher, Funktionen usw. können jederzeit entfernt werden. Wenn Ihr Deployment extrem empfindlich auf Änderungen reagiert, sollten Sie die Werte, die konstant bleiben müssen, ausdrücklich angeben und Upgrades aufmerksam verfolgen. In fast allen Fällen empfehlen wir die Standardeinstellungen.


<a id="syntax"></a>
## Syntax

```caddy-d
tls [internal|force_automate|<email>] | [<cert_file> <key_file>] {
	protocols <min> [<max>]
	ciphers   <cipher_suites...>
	curves    <groups...>
	alpn      <values...>
	load      <paths...>
	ca        <ca_dir_url>
	ca_root   <pem_file>
	key_type  ed25519|p256|p384|rsa2048|rsa4096
	dns       <provider_name> [<params...>]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	eab       <key_id> <mac_key>
	on_demand
	reuse_private_keys
	client_auth {
		mode                   [request|require|verify_if_given|require_and_verify]
		trust_pool             <module>
		verifier 			   <module>
	}
	issuer          <issuer_name>  [<params...>]
	get_certificate <manager_name> [<params...>]
	insecure_secrets_log <log_file>
	renewal_window_ratio <ratio>
	force_automate
}
```

- **internal** bedeutet, Caddys interne, lokal vertrauenswürdige CA zu verwenden, um Zertifikate für diese Site auszustellen. Zur weiteren Konfiguration des [`internal`](#internal)-Issuers verwenden Sie die Unterdirektive [`issuer`](#issuer).

- **force_automate** zwingt Caddy, Zertifikate für die Site zu automatisieren, selbst wenn andere verwaltete Zertifikate zutreffen.

- **&lt;email&gt;** ist die E-Mail-Adresse für das ACME-Konto, das die Zertifikate der Site verwaltet. Möglicherweise bevorzugen Sie stattdessen die globale Option [`email`](/docs/caddyfile/options#email), um dies für alle Sites auf einmal zu konfigurieren.

<aside class="tip">

Beachten Sie, dass Let's Encrypt Ihnen E-Mails zu bald ablaufenden Zertifikaten senden kann. Das kann irreführend sein, weil Caddy bei der Erneuerung möglicherweise einen anderen Issuer gewählt hat (z. B. ZeroSSL). Prüfen Sie Ihre Logs und/oder das Zertifikat selbst (zum Beispiel im Browser), um zu sehen, welcher Issuer verwendet wurde und ob dessen Ablaufdatum noch gültig ist; falls ja, können Sie die E-Mail von Let's Encrypt ignorieren.

</aside>

- **&lt;cert_file&gt;** und **&lt;key_file&gt;** sind die Pfade zu Zertifikat und privatem Schlüssel als PEM-Dateien. Nur eines von beiden anzugeben ist ungültig.

- **protocols** <span id="protocols"/> gibt die minimale und maximale Protokollversion an. ÄNDERN SIE DIES NICHT, außer Sie wissen genau, was Sie tun. Diese Konfiguration ist selten nötig, weil Caddy immer moderne Standardwerte verwendet.

  Standard min: `tls1.2`, Standard max: `tls1.3`

- **ciphers** <span id="ciphers"/> gibt die Liste der Cipher-Suite-Namen in absteigender Präferenzreihenfolge an. ÄNDERN SIE DIES NICHT, außer Sie wissen genau, was Sie tun. Beachten Sie, dass Cipher Suites für TLS 1.3 nicht anpassbar sind und nicht alle TLS-1.2-Cipher standardmäßig aktiviert sind. Die unterstützten Namen sind (in Präferenzreihenfolge der Go stdlib):
	- `TLS_AES_128_GCM_SHA256`
	- `TLS_CHACHA20_POLY1305_SHA256`
	- `TLS_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA`

- **curves** <span id="curves"/> gibt die Liste der zu unterstützenden EC-Gruppen an. Es wird empfohlen, die Standardwerte nicht zu ändern. Unterstützte Werte sind:
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> ist die Liste der Werte, die in der [ALPN-Erweiterung <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Glossary/ALPN) des TLS-Handshakes angekündigt werden.

- **load** <span id="load"/> gibt eine Liste von Ordnern an, aus denen PEM-Dateien geladen werden, die Zertifikat+Schlüssel-Bundles enthalten.

- **ca** <span id="ca"/> ändert den ACME-CA-Endpunkt. Dies wird meist verwendet, um beim Testen [Let's Encrypts Staging-Endpunkt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) oder einen internen ACME-Server zu setzen. (Um diesen Wert für das gesamte Caddyfile zu ändern, verwenden Sie stattdessen die globale Option [`acme_ca`](/docs/caddyfile/options).)

- **ca_root** <span id="ca_root"/> gibt eine PEM-Datei an, die ein vertrauenswürdiges Root-Zertifikat für den ACME-CA-Endpunkt enthält, wenn es nicht im System-Trust-Store liegt.

- **key_type** <span id="key_type"/> ist der Schlüsseltyp, der beim Erzeugen von CSRs verwendet wird. Setzen Sie dies nur bei konkreter Anforderung.

- **dns** <span id="dns"/> aktiviert die [DNS-Challenge](/docs/automatic-https#dns-challenge) mit dem angegebenen Provider-Plugin, das aus einem der [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns)-Repositories eingebunden sein muss. Jedes Provider-Plugin kann nach seinem Namen eine eigene Syntax haben; Details finden Sie in dessen Dokumentation. Die Unterstützung der einzelnen DNS-Provider ist Community-Arbeit. [Erfahren Sie in unserem Wiki, wie Sie die DNS-Challenge für Ihren Provider aktivieren.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> ist ein [duration-Wert](/docs/conventions#durations), der die maximale Wartezeit festlegt, bis die DNS-TXT-Records bei Verwendung der DNS-Challenge erscheinen. Setzen Sie ihn auf `-1`, um Propagation Checks zu deaktivieren. Standard: 2 Minuten.

- **propagation_delay** <span id="propagation_delay"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie lange vor Beginn der Propagation Checks für DNS-TXT-Records bei Verwendung der DNS-Challenge gewartet wird. Standard: `0` (keine Wartezeit).

- **dns_ttl** <span id="dns_ttl"/> ist ein [duration-Wert](/docs/conventions#durations), der die TTL des für die DNS-Challenge verwendeten `TXT`-Records setzt. Selten nötig.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> überschreibt die Domain, die für die DNS-Challenge verwendet wird. Dies dient dazu, die Challenge an eine andere Domain zu delegieren.

  Das kann nützlich sein, wenn der DNS-Provider Ihrer primären Domain kein [DNS-Plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) hat. Sie können stattdessen einen `CNAME`-Record mit der Subdomain `_acme-challenge` zu Ihrer primären Domain hinzufügen, der auf eine sekundäre Domain zeigt, für die Sie ein Plugin haben. Diese Option erfordert *keine* besondere Unterstützung durch das Plugin.

  Wenn ACME-Issuer versuchen, die DNS-Challenge für Ihre primäre Domain zu lösen, folgen sie dann dem `CNAME` zu Ihrer sekundären Domain, um den `TXT`-Record zu finden.

  **Hinweis:** Verwenden Sie hier den vollständigen kanonischen Namen aus dem CNAME-Record als Wert - die Subdomain `_acme-challenge` wird nicht automatisch vorangestellt.

- **resolvers** <span id="resolvers"/> passt die DNS-Resolver an, die bei der DNS-Challenge verwendet werden; diese haben Vorrang vor Systemresolvern oder Standardresolvern. Wenn hier gesetzt, werden die Resolver an alle konfigurierten Zertifikats-Issuer weitergegeben.

  Dies ist typischerweise eine Liste von IP-Adressen. Zum Beispiel, um [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns) zu verwenden:

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> konfiguriert ACME External Account Binding (EAB) für diese Site mit der von Ihrer CA bereitgestellten Key-ID und dem MAC-Key.

- **on_demand** <span id="on_demand"/> aktiviert [On-Demand TLS](/docs/automatic-https#on-demand-tls) für die Hostnamen in den Adressen des Site-Blocks. **Sicherheitswarnung:** In Produktion ist dies unsicher, sofern Sie nicht auch die globale Option [`on_demand_tls`](/docs/caddyfile/options#on-demand-tls) konfigurieren, um Missbrauch zu begrenzen.

- **reuse_private_keys** <span id="reuse_private_keys"/> aktiviert die Wiederverwendung privater Schlüssel bei der Zertifikatserneuerung. Standardmäßig wird für jedes neue Zertifikat ein neuer Schlüssel erstellt, um Pinning abzufedern und den Umfang einer Schlüsselkompromittierung zu reduzieren. Key Pinning widerspricht Best Practices der Branche. Diese Option wird nicht empfohlen, außer Sie haben einen konkreten Grund; sie kann in einer zukünftigen Version entfernt werden.

- **client_auth** <span id="client_auth"/> aktiviert und konfiguriert TLS-Clientauthentifizierung:
  - **mode** <span id="mode"/> ist der Modus zur Authentifizierung des Clients. Erlaubte Werte sind:

    | Mode | Beschreibung |
    | --- | --- |
    | request | Clients nach einem Zertifikat fragen, aber auch ohne eines erlauben; nicht verifizieren |
    | require | Clients müssen ein Zertifikat präsentieren, aber es wird nicht verifiziert |
    | verify_if_given | Clients nach einem Zertifikat fragen; auch ohne eines erlauben, aber verifizieren, falls eines vorhanden ist |
    | require_and_verify | Clients müssen ein gültiges, verifiziertes Zertifikat präsentieren |

    Standard: `require_and_verify`, wenn ein `trust_pool`-Modul bereitgestellt wird; andernfalls `require`.

  - **trust_pool** <span id="trust_pool"/> konfiguriert die Quelle der Certificate Authorities (CA), deren Zertifikate zur Validierung von Client-Zertifikaten verwendet werden.

	Welche Certificate Authority den Pool vertrauenswürdiger Zertifikate bereitstellt und wie die Konfiguration in diesem Abschnitt aussieht, hängt vom konfigurierten Trust-Pool-Quellmodul ab. Die in Caddy verfügbaren Standardmodule sind [unten aufgelistet](#trust-pool-providers). Die vollständige Liste der Module, einschließlich Drittanbieter, steht in der [`trust_pool`-JSON-Dokumentation](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool).

    Mehrere `trusted_*`-Direktiven können verwendet werden, um mehrere CA- oder Leaf-Zertifikate anzugeben. Client-Zertifikate, die nicht als eines der Leaf-Zertifikate aufgelistet oder von einer der angegebenen CAs signiert sind, werden gemäß **mode** abgelehnt.

  - **verifier** <span id="verifier"/> aktiviert die Verwendung eines benutzerdefinierten Moduls zur Verifikation von Client-Zertifikaten. Solche Module können eigene Client-Authentifizierungsprüfungen durchführen, etwa sicherstellen, dass das Zertifikat nicht widerrufen wurde.

- **issuer** <span id="issuer"/> konfiguriert einen benutzerdefinierten Zertifikats-Issuer oder eine Quelle, von der Zertifikate bezogen werden.

  Welcher Issuer verwendet wird und welche Optionen in diesem Abschnitt folgen, hängt von den verfügbaren [Issuer-Modulen](#issuers) ab. Einige der anderen Unterdirektiven wie `ca` und `dns` sind eigentlich Abkürzungen zur Konfiguration des `acme`-Issuers (und diese Unterdirektive wurde später hinzugefügt). Daher ist es verwirrend und verboten, diese Direktive zusammen mit einigen der anderen anzugeben.

  Diese Unterdirektive kann mehrfach angegeben werden, um mehrere redundante Issuer zu konfigurieren; wenn einer kein Zertifikat ausstellen kann, wird der nächste versucht.

- **get_certificate** <span id="get_certificate"/> aktiviert das Abrufen von Zertifikaten von einem [Manager-Modul](#certificate-managers) zur Handshake-Zeit.

- **insecure_secrets_log** <span id="insecure_secrets_log"/> aktiviert das Loggen von TLS-Secrets in eine Datei. Dies ist auch als `SSLKEYLOGFILE` bekannt. Es verwendet das NSS-Key-Log-Format, das dann von Wireshark oder anderen Tools geparst werden kann. ⚠️ **Sicherheitswarnung:** Dies ist unsicher, weil es anderen Programmen oder Tools ermöglicht, TLS-Verbindungen zu entschlüsseln, und damit die Sicherheit vollständig kompromittiert. Für Debugging und Fehlersuche kann diese Fähigkeit jedoch nützlich sein.

- **renewal_window_ratio** <span id="renewal_window_ratio"/> ist ein Verhältnis zwischen 0 und 1, das bestimmt, wie viel Zertifikatslaufzeit verbleiben muss, bevor Caddy versucht, das Zertifikat zu erneuern. Wenn ein Zertifikat zum Beispiel 90 Tage gültig ist und dieses Verhältnis `0.3333` beträgt (der Standardwert), versucht Caddy fortlaufend, das Zertifikat zu erneuern, sobald 30 Tage oder weniger bis zum Ablauf verbleiben. Kann auch global mit der globalen Option [`renewal_window_ratio`](/docs/caddyfile/options#renewal_window_ratio) gesetzt werden.

  Sie müssen dies selten ändern, aber es kann nützlich sein, später in der Laufzeit des Zertifikats zu erneuern, wenn Ihre CA sehr lange für die Ausstellung braucht.

  Beachten Sie, dass dies nur ein Vorschlag ist, da ACME-Issuer die [ARI-Erweiterung](https://datatracker.ietf.org/doc/rfc9773/) implementieren können. ARI gibt ein Zeitfenster vor, in dem der ACME-Client (hier Caddy) die Erneuerung versuchen soll, und dieses Fenster muss nicht mit diesem Verhältnis übereinstimmen.

- **force_automate** ist dasselbe wie die Inline-Angabe (siehe oben).

<a id="trust-pool-providers"></a>
### Trust-Pool-Provider

Dies sind die Standard-Trust-Pool-Provider, die in der Unterdirektive `trust_pool` verwendet werden können:

<a id="inline"></a>
#### inline

Das Modul `inline` parst die vertrauenswürdigen Root-Zertifikate, die direkt im Caddyfile im base64-DER-codierten Format aufgelistet sind. Die Direktive `trust_der` kann mehrfach wiederholt werden.

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> ist ein base64-DER-codiertes CA-Zertifikat, gegen das Client-Zertifikate validiert werden.

<a id="file"></a>
#### file

Das Modul `file` liest die vertrauenswürdigen Root-Zertifikate aus PEM-Dateien von der Festplatte. Die Direktive `pem_file` kann mehrere Dateipfade in derselben Zeile akzeptieren und mehrfach wiederholt werden.

```caddy-d
... file [<pem_file>...] {
	pem_file <pem_file>...
}
```

- **pem_file** <span id="pem_file"/> ist ein Pfad zu einer PEM-CA-Zertifikatsdatei, gegen die Client-Zertifikate validiert werden.

<a id="pki_root"></a>
#### pki_root

Das Modul `pki_root` bezieht das *Root* und vertraut Zertifikaten der Certificate Authority, die in der [PKI-App](/docs/caddyfile/options#pki-options) definiert ist. Die Direktive `authority` kann mehrere Authorities gleichzeitig akzeptieren und mehrfach wiederholt werden.

```caddy-d
... pki_root [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> ist der Name der Certificate Authority, die in der PKI-App konfiguriert ist.

<a id="pki_intermediate"></a>
#### pki_intermediate

Das Modul `pki_intermediate` bezieht das *Intermediate* und vertraut Zertifikaten der Certificate Authority, die in der [PKI-App](/docs/caddyfile/options#pki-options) definiert ist. Die Direktive `authority` kann mehrere Authorities gleichzeitig akzeptieren und mehrfach wiederholt werden.

```caddy-d
... pki_intermediate [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> ist der Name der Certificate Authority, die in der PKI-App konfiguriert ist.

<a id="storage"></a>
#### storage

Das Modul `storage` extrahiert das Root der vertrauenswürdigen Zertifikate aus Caddy-[Storage](/docs/caddyfile/options#storage). Die Direktive `authority` kann mehrere Authorities gleichzeitig akzeptieren und mehrfach wiederholt werden.

```caddy-d
... storage [<storage_keys>...] {
	storage <storage_module>
	keys    <storage_keys>...
}
```

- **storage** <span id="storage"/> ist ein optional zu verwendendes Storage-Modul. Wenn nicht angegeben, wird das Standard-Storage-Modul verwendet. Wenn angegeben, darf es nur einmal angegeben werden.

- **keys** <span id="keys"/> ist die Liste der Storage-Keys, unter denen die PEM-Dateien der Zertifikate gespeichert sind. Die Direktive akzeptiert mehrere Werte in derselben Zeile und kann mehrfach angegeben werden.

<a id="http"></a>
#### http

Das Modul `http` bezieht die vertrauenswürdigen Zertifikate von HTTP-Endpunkten. Die Direktive `endpoints` kann mehrere Endpunkte gleichzeitig akzeptieren und mehrfach wiederholt werden.

```caddy-d
... http [<endpoints...>] {
	endpoints   <endpoints...>
	tls         <tls_config>
}
```

- **endpoints** <span id="endpoints"/> ist die Liste der HTTP-Endpunkte, von denen Zertifikate bezogen werden. Die Direktive akzeptiert mehrere Werte in derselben Zeile und kann mehrfach angegeben werden.

- **tls** <span id="tls"/> ist eine optionale TLS-Konfiguration, die beim Verbinden mit dem HTTP-Endpunkt verwendet wird. Das Parsen des Abschnitts ist im [folgenden Abschnitt](#tls-1) definiert.

<a id="tls-1"></a>
##### TLS

```caddy-d
... {
	ca                    <ca_module>
	insecure_skip_verify
	handshake_timeout     <duration>
	server_name           <name>
	renegotiation         <never|once|freely>
}
```

- **ca** <span id="ca"/> ist eine optionale Direktive zur Definition des Trust-Pool-Providers. Die Konfiguration folgt demselben Verhalten wie [`trust_pool`](#trust_pool). Wenn angegeben, darf sie nur einmal angegeben werden.

- **insecure_skip_verify** <span id="insecure_skip_verify"/> schaltet die TLS-Handshake-Verifikation ab, wodurch die Verbindung unsicher und anfällig für Man-in-the-Middle-Angriffe wird. *Nicht in Produktion verwenden.* Die Verifikation erfolgt entweder gegen die vom System vertrauten Certificate Authorities oder gemäß der Direktive [`ca`](#ca).

- **handshake_timeout** <span id="handshake_timeout"/> ist die maximale [Dauer](/docs/conventions#durations), die auf Abschluss des TLS-Handshakes gewartet wird. Standard: kein Timeout.

- **server_name** <span id="server_name"/> setzt den Servernamen, der beim Verifizieren des im TLS-Handshake empfangenen Zertifikats verwendet wird. Standardmäßig wird der Host-Teil der Upstream-Adresse verwendet.

- **renegotiation** <span id="renegotiation"/> setzt das TLS-Renegotiation-Level. TLS-Renegotiation bedeutet, nach dem ersten weitere Handshakes auszuführen. Das Level kann eines der folgenden sein:
  - `never` (Standard) deaktiviert Renegotiation.
  - `once` erlaubt einem Remote-Server, einmal pro Verbindung Renegotiation anzufordern.
  - `freely` erlaubt einem Remote-Server, wiederholt Renegotiation anzufordern.

<a id="verifiers"></a>
### Verifier

Client-Zertifikats-Verifier-Module werden ausgeführt, nachdem validiert wurde, dass die Zertifikate von einer vertrauenswürdigen Certificate Authority ausgestellt wurden, sofern `trust_pool` konfiguriert ist. Der aktuell in Standard-Caddy ausgelieferte Verifier ist `leaf`.

<a id="leaf"></a>
#### Leaf

Der `leaf`-Verifier prüft, ob das Client-Zertifikat zu einer definierten Menge erlaubter Zertifikate gehört. Die Zertifikatsmenge wird mit [Loader](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders)-Modulen geladen.

<a id="loaders"></a>
##### Loader

Die Standard-Caddy-Distribution bündelt 4 Loader, 3 davon sind im Caddyfile verfügbar.

<a id="file-1"></a>
###### File

Der `file`-Loader lädt die Zertifikatsmenge aus angegebenen PEM-Dateien.

```caddy-d
... file <pem_files...>
```

<a id="folder"></a>
###### Folder

Der `folder`-Loader durchläuft die benannten Verzeichnisse rekursiv und sucht nach PEM-Dateien, die als akzeptierte Client-Zertifikate geladen werden.

```caddy-d
... folder <folders...>
```

<a id="pem"></a>
###### PEM

Der `pem`-Loader akzeptiert Zertifikate, die im Caddyfile im PEM-Format inline angegeben sind.

```caddy-d
... pem <pem_strings...>
```

<a id="issuers"></a>
### Issuer

Diese Issuer sind standardmäßig in der `tls`-Direktive enthalten:

<a id="acme"></a>
#### acme

Bezieht Zertifikate mit dem ACME-Protokoll. Beachten Sie, dass `acme` ein Standard-Issuer ist (mit Let's Encrypt), daher ist eine explizite Konfiguration normalerweise unnötig.

```caddy-d
... acme [<directory_url>] {
	dir      <directory_url>
	test_dir <test_directory_url>
	email    <email>
	timeout  <duration>
	disable_http_challenge
	disable_tlsalpn_challenge
	alt_http_port    <port>
	alt_tlsalpn_port <port>
	eab <key_id> <mac_key>
	trusted_roots <pem_files...>
	dns [<provider_name> [<options>]]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}
	profile <name>
}
```

- **dir** <span id="dir"/> ist die URL zum Directory der ACME-CA.

  Standard: `https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> ist ein optionales Fallback-Directory, das bei erneuten Challenge-Versuchen verwendet wird; wenn alle Challenges fehlschlagen, wird dieser Endpunkt während der Retries verwendet. Nützlich, wenn eine CA einen Staging-Endpunkt hat und Sie Rate Limits des Produktionsendpunkts vermeiden möchten.

  Standard: `https://acme-staging-v02.api.letsencrypt.org/directory`

- **email** <span id="email"/> ist die Kontakt-E-Mail-Adresse des ACME-Kontos.

- **timeout** <span id="timeout"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie lange auf eine ACME-Operation gewartet wird, bevor sie timed out.

- **disable_http_challenge** <span id="disable_http_challenge"/> deaktiviert die HTTP-Challenge.

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> deaktiviert die TLS-ALPN-Challenge.

- **alt_http_port** <span id="alt_http_port"/> ist ein alternativer Port, auf dem die HTTP-Challenge bedient wird; sie muss auf Port 80 stattfinden, daher müssen Sie Pakete an diesen alternativen Port weiterleiten.

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> ist ein alternativer Port, auf dem die TLS-ALPN-Challenge bedient wird; sie muss auf Port 443 stattfinden, daher müssen Sie Pakete an diesen alternativen Port weiterleiten.

- **eab** <span id="eab"/> gibt ein External Account Binding an, das bei manchen ACME-CAs erforderlich sein kann.

- **trusted_roots** <span id="trusted_roots"/> sind ein oder mehrere Root-Zertifikate (als PEM-Dateinamen), denen beim Verbinden mit dem ACME-CA-Server vertraut wird.

- **dns** <span id="dns"/> konfiguriert die DNS-Challenge. Ein Provider muss hier konfiguriert werden, außer die globale Option [`dns`](/docs/caddyfile/options#dns) gibt ein global anwendbares DNS-Provider-Modul an.

- **propagation_timeout** <span id="propagation_timeout"/> ist ein [duration-Wert](/docs/conventions#durations), der die maximale Wartezeit festlegt, bis die DNS-TXT-Records bei Verwendung der DNS-Challenge erscheinen. Setzen Sie ihn auf `-1`, um Propagation Checks zu deaktivieren. Standard: 2 Minuten.

- **propagation_delay** <span id="propagation_delay"/> ist ein [duration-Wert](/docs/conventions#durations), der festlegt, wie lange vor Beginn der Propagation Checks für DNS-TXT-Records bei Verwendung der DNS-Challenge gewartet wird. Standard: 0 (keine Wartezeit).

- **dns_ttl** <span id="dns_ttl"/> ist ein [duration-Wert](/docs/conventions#durations), der die TTL des für die DNS-Challenge verwendeten `TXT`-Records setzt. Selten nötig.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> überschreibt die Domain, die für die DNS-Challenge verwendet wird. Dies dient dazu, die Challenge an eine andere Domain zu delegieren.

  Das kann nützlich sein, wenn der DNS-Provider Ihrer primären Domain kein [DNS-Plugin <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) hat. Sie können stattdessen einen `CNAME`-Record mit der Subdomain `_acme-challenge` zu Ihrer primären Domain hinzufügen, der auf eine sekundäre Domain zeigt, für die Sie ein Plugin haben. Diese Option erfordert *keine* besondere Unterstützung durch das Plugin.

  Wenn ACME-Issuer versuchen, die DNS-Challenge für Ihre primäre Domain zu lösen, folgen sie dann dem `CNAME` zu Ihrer sekundären Domain, um den `TXT`-Record zu finden.

  **Hinweis:** Verwenden Sie hier den vollständigen kanonischen Namen aus dem CNAME-Record als Wert - die Subdomain `_acme-challenge` wird nicht automatisch vorangestellt.

- **resolvers** <span id="resolvers"/> passt die DNS-Resolver an, die bei der DNS-Challenge verwendet werden; diese haben Vorrang vor Systemresolvern oder Standardresolvern. Wenn hier gesetzt, werden die Resolver an alle konfigurierten Zertifikats-Issuer weitergegeben.

  Dies ist typischerweise eine Liste von IP-Adressen. Zum Beispiel, um [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns) zu verwenden:

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> gibt an, welche Zertifikatsketten Caddy bevorzugen soll; nützlich, wenn Ihre CA mehrere Ketten bereitstellt. Verwenden Sie eine der folgenden Optionen:
	- **smallest** <span id="smallest"/> weist Caddy an, Ketten mit der geringsten Byte-Anzahl zu bevorzugen.

	- **root_common_name** <span id="root_common_name"/> ist eine Liste eines oder mehrerer Common Names; Caddy wählt die erste Kette, deren Root auf mindestens einen der angegebenen Common Names passt.

	- **any_common_name** <span id="any_common_name"/> ist eine Liste eines oder mehrerer Common Names; Caddy wählt die erste Kette, deren Issuer auf mindestens einen der angegebenen Common Names passt.

- **profile** ist der Name des [ACME-Profils](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/), das beim Bestellen von Zertifikaten angewendet wird. Wenn Sie eines angeben, müssen alle konfigurierten (implizit oder anderweitig) CAs dieses Profil unterstützen. Verfügbare Profile finden Sie in der Dokumentation Ihrer CA; manche CAs unterstützen möglicherweise keine Profile. EXPERIMENTELL: Die ACME-Profil-Spezifikation ist noch im Draft-Status, daher kann diese Funktion sich ändern oder entfernt werden.


<a id="zerossl"></a>
#### zerossl

Bezieht Zertifikate über [ZeroSSLs proprietäre Zertifikatsausstellungs-API](https://zerossl.com/documentation/api/). Ein API-Key ist erforderlich, und je nach Plan kann auch eine Zahlung nötig sein. Beachten Sie, dass dieser Issuer sich vom [ACME-Endpunkt von ZeroSSL](https://zerossl.com/documentation/acme/) unterscheidet. Um ZeroSSLs ACME-Endpunkt zu verwenden, nutzen Sie den oben beschriebenen `acme`-Issuer, konfiguriert mit ZeroSSLs ACME-Directory-Endpunkt.

```caddy-d
... zerossl <api_key> {
	validity_days <days>
	alt_http_port <port>
	dns <provider_name> ...
	propagation_delay <duration>
	propagation_timeout <duration>
	resolvers <list...>
	dns_ttl <duration>
}
```

- **validity_days** <span id="validity_days"/> definiert die Zertifikatslaufzeit. Nur bestimmte Werte werden akzeptiert; Details finden Sie in [ZeroSSLs Dokumentation](https://zerossl.com/documentation/api/create-certificate/).
<!--
  Default: `https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> ist der Port, der zum Abschließen der HTTP-Validierung von ZeroSSL verwendet wird, wenn nicht Port 80.
- **dns** <span id="zerossl_dns"/> aktiviert die CNAME-Validierungsmethode mit dem benannten DNS-Provider und der angegebenen Konfiguration zur automatischen Record-Bereitstellung. Das DNS-Provider-Plugin muss aus den [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns)-Repositories installiert sein. Jedes Provider-Plugin kann nach seinem Namen eine eigene Syntax haben; Details finden Sie in dessen Dokumentation. Die Unterstützung der einzelnen DNS-Provider ist Community-Arbeit.
- **propagation_delay** <span id="zerossl_propagation_delay"/> gibt an, wie lange vor der Prüfung der CNAME-Record-Propagation gewartet wird.
- **propagation_timeout** <span id="zerossl_propagation_timeout"/> gibt an, wie lange auf CNAME-Record-Propagation gewartet wird, bevor aufgegeben wird.
- **resolvers** <span id="zerossl_resolvers"/> definiert benutzerdefinierte DNS-Resolver zur Prüfung der CNAME-Record-Propagation.
- **dns_ttl** <span id="zerossl_dns_ttl"/> konfiguriert die TTL für CNAME-Records, die als Teil des Validierungsprozesses erstellt werden.



<a id="internal"></a>
#### internal

Bezieht Zertifikate von einer internen Certificate Authority.

```caddy-d
... internal {
	ca       <name>
	lifetime <duration>
	sign_with_root
}
```

- **ca** <span id="ca"/> ist der Name der zu verwendenden internen CA. Standard: `local`. Siehe die [globalen Optionen der PKI-App](/docs/caddyfile/options#pki-options), um die CA `local` zu konfigurieren oder alternative CAs zu erstellen.

  Standardmäßig hat das Root-CA-Zertifikat eine Laufzeit von `3600d` (10 Jahre) und das Intermediate eine Laufzeit von `7d` (7 Tage).

  Caddy versucht, das Root-CA-Zertifikat im System-Trust-Store zu installieren. Das kann jedoch fehlschlagen, wenn Caddy als unprivilegierter Benutzer oder in einem Docker-Container läuft. In diesem Fall muss das Root-CA-Zertifikat manuell installiert werden, entweder mit dem Befehl [`caddy trust`](/docs/command-line#caddy-trust) oder durch [Herauskopieren aus dem Container](/docs/running#usage).

- **lifetime** <span id="lifetime"/> ist ein [duration-Wert](/docs/conventions#durations), der die Gültigkeitsdauer intern ausgestellter Leaf-Zertifikate setzt. Standard: `12h`. Es wird NICHT empfohlen, dies zu ändern, außer es ist absolut nötig. Sie muss kürzer sein als die Laufzeit des Intermediates.

- **sign_with_root** <span id="sign_with_root"/> erzwingt, dass das Root statt des Intermediates der Issuer ist. Dies wird NICHT empfohlen und sollte nur verwendet werden, wenn Geräte/Clients Zertifikatsketten nicht korrekt validieren (sehr selten).



<a id="certificate-managers"></a>
### Certificate Managers

Certificate-Manager-Module unterscheiden sich von Issuer-Modulen dadurch, dass ihre Verwendung impliziert, dass ein externes Tool oder ein externer Dienst das Zertifikat erneuert, während ein Issuer-Modul impliziert, dass Caddy das Zertifikat selbst verwaltet. (Issuer-Module nehmen eine Certificate Signing Request (CSR) als Eingabe, Certificate-Manager-Module dagegen ein TLS ClientHello.)

Diese Manager-Module sind standardmäßig in der `tls`-Direktive enthalten:

<a id="tailscale"></a>
#### tailscale

Bezieht Zertifikate von einer lokal laufenden [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com)-Instanz. [HTTPS muss in Ihrem Tailscale-Konto aktiviert sein](https://tailscale.com/kb/1153/enabling-https/) (oder auf Ihrem Open-Source-[Headscale-Server <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/juanfont/headscale)); außerdem muss der Caddy-Prozess entweder als root laufen, oder Sie müssen `tailscaled` so konfigurieren, dass Ihr Caddy-Benutzer [Zertifikate abrufen darf](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).

***HINWEIS: Dies ist normalerweise unnötig!*** Caddy verwendet Tailscale automatisch für alle `*.ts.net`-Domains ohne zusätzliche Konfiguration.

```caddy-d
get_certificate tailscale  # oft unnötig!
```


<a id="http-1"></a>
#### http

Zertifikate durch eine HTTP(S)-Anfrage beziehen. Die Antwort muss den Statuscode `200` haben, und der Body muss eine PEM-Kette mit dem vollständigen Zertifikat (einschließlich Intermediates) sowie dem privaten Schlüssel enthalten.

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> ist die vollständig qualifizierte URL, an die die Anfrage gesendet wird. Aus Performance-Gründen wird dringend empfohlen, hierfür einen lokalen Endpunkt zu verwenden. Die URL wird um die folgenden Query-String-Parameter ergänzt:

  - `server_name`: SNI-Wert
  - `signature_schemes`: kommagetrennte Liste von Hex-IDs der Signaturalgorithmen
  - `cipher_suites`: kommagetrennte Liste von Hex-IDs der Cipher Suites
  - `local_ip`: IP-Adresse, an die der Client die Anfrage gesendet hat



<a id="examples"></a>
## Beispiele

Ein benutzerdefiniertes Zertifikat und einen Schlüssel verwenden. Das Zertifikat sollte [SANs](https://en.wikipedia.org/wiki/Subject_Alternative_Name) haben, die zur Site-Adresse passen:

```caddy
example.com {
	tls cert.pem key.pem
}
```

[Lokal vertrauenswürdige](/docs/automatic-https#local-https) Zertifikate für alle Hosts im aktuellen Site-Block verwenden, statt öffentlicher Zertifikate via ACME / Let's Encrypt (nützlich in Entwicklungsumgebungen):

```caddy
example.com {
	tls internal
}
```

Lokal vertrauenswürdige Zertifikate verwenden, aber [On-Demand](/docs/automatic-https#on-demand-tls) statt im Hintergrund verwaltet. Dadurch können Sie jede Domain auf Ihre Caddy-Instanz zeigen lassen und automatisch ein Zertifikat bereitstellen. Dies SOLLTE NICHT verwendet werden, wenn Ihre Caddy-Instanz öffentlich erreichbar ist, da ein Angreifer damit die Ressourcen Ihres Servers erschöpfen könnte:

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

Benutzerdefinierte Optionen für die interne CA verwenden (die Abkürzung `tls internal` kann nicht verwendet werden):

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

Eine E-Mail-Adresse für Ihr ACME-Konto angeben (wenn jedoch nur eine E-Mail für alle Sites verwendet wird, empfehlen wir stattdessen die globale Option [`email`](/docs/caddyfile/options)):

```caddy
example.com {
	tls your@email.com
}
```

Die DNS-Challenge für eine bei Cloudflare verwaltete Domain mit Zugangsdaten aus einer Umgebungsvariable aktivieren. Dies schaltet Unterstützung für Wildcard-Zertifikate frei, die DNS-Validierung erfordern:

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

Die Zertifikatskette per HTTP beziehen, statt sie von Caddy verwalten zu lassen. Beachten Sie, dass [`get_certificate`](#certificate-managers) impliziert, dass [`on_demand`](#on_demand) aktiviert ist und Zertifikate mit einem Modul abgerufen werden, statt ACME-Ausstellung auszulösen:

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

TLS-Clientauthentifizierung aktivieren und verlangen, dass Clients ein gültiges Zertifikat präsentieren, das gegen alle bereitgestellten CAs über den [`trust_pool`](#trust_pool)-Provider `file` verifiziert wird:

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
