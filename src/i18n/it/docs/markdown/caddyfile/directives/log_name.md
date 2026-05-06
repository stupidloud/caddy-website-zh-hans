---
title: log_name (direttiva del Caddyfile)
---

# log_name

Sovrascrive il nome del logger da usare per una richiesta durante la scrittura dei log degli accessi con la [direttiva `log`](log).

Questa direttiva è utile quando si desidera loggare le richieste in file diversi in base a qualche condizione, come il percorso della richiesta o il metodo.

È possibile specificare più di un nome di logger, in modo che il log della richiesta venga inviato a più di un logger corrispondente.

Questa opzione è spesso abbinata all'opzione [`no_hostname`](log#no_hostname) della direttiva `log`, che impedisce al logger di essere associato a uno qualsiasi degli hostname del blocco sito, in modo che solo le richieste che impostano `log_name` inviino log a quel logger.


## Sintassi

```caddy-d
log_name [<matcher>] <names...>
```


## Esempi

Potreste voler loggare le richieste in file diversi, ad esempio potreste voler loggare i controlli sanitari (health checks) in un file separato rispetto ai log degli accessi principali.

L'uso di `no_hostname` in un blocco `log` impedisce al logger di essere associato a uno qualsiasi degli hostname del blocco sito (ovvero `localhost` in questo esempio), in modo che solo le richieste che hanno `log_name` impostato sul nome di quel logger ricevano i log.

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
		respond "Sano"
	}

	handle {
		respond "Ciao mondo"
	}
}
```
