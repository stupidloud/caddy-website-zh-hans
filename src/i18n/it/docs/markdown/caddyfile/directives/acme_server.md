---
title: acme_server (direttiva del Caddyfile)
---

# acme_server

Un handler server integrato per il [protocollo ACME](https://tools.ietf.org/html/rfc8555). Questo permette a un'istanza di Caddy di emettere certificati per qualsiasi altro software compatibile con ACME (incluse altre istanze di Caddy).

Quando abilitato, le richieste che corrispondono al percorso `/acme/*` verranno gestite dal server ACME.


## Configurazione del client

Usando i valori predefiniti del server ACME, i client ACME dovrebbero semplicemente essere configurati per usare `https://localhost/acme/local/directory` come loro endpoint ACME. (`local` è l'ID della CA predefinita di Caddy.)


## Sintassi

```caddy-d
acme_server [<matcher>] {
	ca         <id>
	lifetime   <durata>
	resolvers  <risolutori...>
	challenges <sfide...>
	allow_wildcard_names
	allow {
		domains <domini...>
		ip_ranges <indirizzi...>
	}
	deny {
		domains <domini...>
		ip_ranges <indirizzi...>
	}
}
```

- **ca** specifica l'ID dell'autorità di certificazione con cui firmare i certificati. Il valore predefinito è `local`, che è la CA predefinita di Caddy, destinata a certificati auto-firmati usati localmente, cosa molto comune negli ambienti di sviluppo. Per un uso più ampio, si raccomanda di specificare una CA diversa per evitare confusione. Se la CA con l'ID fornito non esiste già, verrà creata. Consultate le [opzioni globali dell'app PKI](/docs/caddyfile/options#opzioni-pki) per configurare CA alternative.

- **lifetime** (Predefinito: `12h`) è una [durata](/docs/conventions#durate) che specifica il periodo di validità per i certificati emessi. Questo valore deve essere inferiore alla durata del [certificato intermedio](/docs/caddyfile/options#intermediate-lifetime) usato per la firma. Si sconsiglia di cambiare questo valore a meno che non sia assolutamente necessario.

- **resolvers** sono gli indirizzi dei risolutori DNS da usare durante la ricerca dei record TXT per la risoluzione delle sfide ACME DNS. Accetta [indirizzi di rete](/docs/conventions#indirizzi-di-rete) con valore predefinito UDP e porta 53 se non specificato. Se l'host è un indirizzo IP, verrà contattato direttamente per risolvere il server upstream. Se l'host non è un indirizzo IP, gli indirizzi vengono risolti usando la [convenzione di risoluzione dei nomi](https://golang.org/pkg/net/#hdr-Name_Resolution) della libreria standard di Go. Se vengono specificati più risolutori, ne viene scelto uno a caso.

- **challenges** imposta i tipi di sfida abilitati. Se non impostato o se la direttiva viene usata senza valori, tutti i tipi di sfida sono abilitati. I valori accettati sono: http-01, tls-alpn-01, dns-01.

- **allow_wildcard_names** abilita l'emissione di certificati con SAN (Subject Alternative Name) wildcard.

- **allow**, **deny** configurano la policy operativa di `acme_server`. La valutazione della policy segue i criteri descritti da Step-CA [qui](https://smallstep.com/docs/step-ca/policies/#policy-evaluation).

	- **domains** imposta i nomi di dominio dei soggetti da consentire o negare secondo i criteri di valutazione della policy.

	- **ip_ranges** imposta gli intervalli IP dei soggetti da consentire o negare secondo i criteri di valutazione della policy.

## Esempi

Per servire un server ACME con ID `casa` sul dominio `acme.example.com`, con la CA personalizzata tramite l'[opzione globale `pki`](/docs/caddyfile/options#opzioni-pki), ed emettendo il proprio certificato usando l'emittente `internal`:

```caddy
{
	pki {
		ca casa {
			name "La mia CA di casa"
		}
	}
}

acme.example.com {
	tls {
		issuer internal {
			ca casa
		}
	}
	acme_server {
		ca casa
	}
}
```

Se avete un altro server Caddy, questo può usare il server ACME sopra indicato per emettere i propri certificati:

```caddy
{
	acme_ca https://acme.example.com/acme/casa/directory
	acme_ca_root /percorso/della/root_ca_casa.crt
}

example.com {
	respond "Ciao, mondo!"
}
```
