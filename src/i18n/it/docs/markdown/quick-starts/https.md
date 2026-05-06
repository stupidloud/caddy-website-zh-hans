---
title: Avvio rapido all'HTTPS
---

# Avvio rapido all'HTTPS

Questa guida vi mostrerà come rendere operativo l'[HTTPS completamente gestito](/docs/automatic-https) in pochissimo tempo.

<aside class="tip">
	Caddy usa l'HTTPS per tutti i siti per impostazione predefinita, a condizione che venga fornito un nome host nella configurazione. Questo tutorial assume che desideriate rendere operativo un sito pubblicamente affidabile (ovvero non "localhost") tramite HTTPS, quindi useremo un nome di dominio pubblico e porte esterne.
</aside>

**Prerequisiti:**
- Competenze di base del terminale / riga di comando
- Comprensione di base del DNS
- Un nome di dominio pubblico registrato
- Accesso esterno alle porte 80 e 443
- `caddy` e `curl` nel vostro PATH

---

In questo tutorial, sostituite `example.com` con il vostro effettivo nome di dominio.

Impostate i record A/AAAA del vostro dominio affinché puntino al vostro server. Potete farlo accedendo al vostro provider DNS e gestendo il vostro nome di dominio.

Prima di continuare, verificate che i record siano corretti con una ricerca autoritativa. Sostituite `example.com` con il vostro nome di dominio e, se state usando IPv6, sostituite `type=A` con `type=AAAA`:

<pre><code class="cmd bash">curl "https://cloudflare-dns.com/dns-query?name=example.com&type=A" \
  -H "accept: application/dns-json"</code></pre>

Assicuratevi inoltre che il vostro server sia raggiungibile esternamente sulle porte 80 e 443 da un'interfaccia pubblica.

<aside class="tip">
	Se vi trovate in una rete domestica o in un'altra rete ristretta, potreste dover inoltrare le porte o regolare le impostazioni del firewall.
</aside>

Tutto ciò che dobbiamo fare è avviare Caddy con il vostro nome di dominio nella configurazione. Esistono diversi modi per farlo.

## Caddyfile

Questo è il modo più comune per ottenere l'HTTPS.

Create un file chiamato `Caddyfile` (senza estensione) in cui la prima riga sia il vostro nome di dominio, ad esempio:

```caddy
example.com

respond "Ciao, privacy!"
```

Quindi, dalla stessa directory, eseguite:

<pre><code class="cmd bash">caddy run</code></pre>

Vedrete Caddy predisporre un certificato TLS e servire il vostro sito tramite HTTPS. Ciò è stato possibile perché l'indirizzo del vostro sito nel Caddyfile conteneva un nome di dominio.


## Il comando `file-server`

Se tutto ciò di cui avete bisogno è servire file statici tramite HTTPS, eseguite questo comando (sostituendo il vostro nome di dominio):

<pre><code class="cmd bash">caddy file-server --domain example.com</code></pre>

Vedrete Caddy predisporre un certificato TLS e servire il vostro sito tramite HTTPS.


## Il comando `reverse-proxy`

Se tutto ciò di cui avete bisogno è un semplice reverse proxy tramite HTTPS (come terminatore TLS), eseguite questo comando (sostituendo il vostro nome di dominio e l'effettivo indirizzo del backend):

<pre><code class="cmd bash">caddy reverse-proxy --from example.com --to localhost:9000</code></pre>

Vedrete Caddy predisporre un certificato TLS e servire il vostro sito tramite HTTPS.


## Configurazione JSON

La regola generale è che qualsiasi [host matcher](/docs/json/apps/http/servers/routes/match/host/) attiverà l'HTTPS automatico.

Pertanto, una configurazione JSON come la seguente abiliterà l'[HTTPS automatico](/docs/automatic-https) pronto per la produzione:

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":443"],
					"routes": [
						{
							"match": [{
								"host": ["example.com"]
							}],
							"handle": [{
								"handler": "static_response",
								"body": "Ciao, privacy!"
							}]
						}
					]
				}
			}
		}
	}
}
```
