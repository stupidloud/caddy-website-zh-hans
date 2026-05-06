---
title: invoke (direttiva del Caddyfile)
---

# invoke

<i>⚠️ Sperimentale</i>

Invoca una [rotta nominata](/docs/caddyfile/concepts#rotte-nominate).

Questo è utile quando abbinato a direttive degli handler HTTP che hanno un proprio stato in memoria, o se sono costose da predisporre al caricamento. Se avete centinaia di siti o più, invocare una rotta nominata può aiutare a ridurre l'uso della memoria.

<aside class="tip">
	
A differenza di [`import`](/docs/caddyfile/directives/import), `invoke` non supporta argomenti, ma potete usare [`vars`](/docs/caddyfile/directives/vars) per definire variabili che possono essere utilizzate all'interno della rotta nominata.

</aside>

## Sintassi

```caddy-d
invoke [<matcher>] <route-name>
```

- **&lt;route-name&gt;** è il nome della rotta precedentemente definita che dovrebbe essere invocata. Se la rotta non viene trovata, verrà generato un errore.


## Esempi

Definisce una [rotta nominata](/docs/caddyfile/concepts#rotte-nominate) con un [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy) che può essere riutilizzata in più siti, con lo stesso stato di bilanciamento del carico in memoria riutilizzato per ogni sito.

```caddy
&(app-proxy) {
	reverse_proxy app-01:8080 app-02:8080 app-03:8080 {
		lb_policy least_conn
		health_uri /healthz
		health_interval 5s
	}
}

# Il dominio apex permette l'accesso all'app tramite un sottopercorso /app
# e al sito principale negli altri casi.
example.com {
	handle_path /app* {
		invoke app-proxy
	}

	handle {
		root * /srv
		file_server
	}
}

# L'app è accessibile anche tramite un sottodominio.
app.example.com {
	invoke app-proxy
}
```
