---
title: bind (direttiva del Caddyfile)
---

# bind

Sovrascrive l'interfaccia alla quale deve associarsi (bind) il socket del server.

Normalmente, il listener si associa all'interfaccia vuota (wildcard). Tuttavia, è possibile forzare il listener ad associarsi a un altro hostname o IP. Questa direttiva accetta solo un host, non una porta. La porta è determinata dall'[indirizzo del sito](/docs/caddyfile/concepts#indirizzi) (il valore predefinito è `443`).

Si noti che associare i siti in modo incoerente può portare a conseguenze impreviste. Ad esempio, se due siti sulla stessa porta risolvono verso `127.0.0.1` e solo uno di essi è configurato con `bind 127.0.0.1`, allora solo un sito sarà accessibile poiché l'altro si assocerà alla porta senza un host specifico; il sistema operativo sceglierà il socket con la corrispondenza più specifica. (Gli host virtuali non sono condivisi tra listener diversi.)

`bind` accetta [indirizzi di rete](/docs/conventions#indirizzi-di-rete), ma non può includere una porta.


## Sintassi

```caddy-d
bind <hosts...>
```

- **&lt;hosts...&gt;** è l'elenco delle interfacce host alle quali associare il listener.


## Esempi

Per rendere un socket accessibile solo sulla macchina corrente, associarsi all'interfaccia di loopback (localhost):

```caddy
example.com {
	bind 127.0.0.1
}
```

Per includere l'IPv6:

```caddy
example.com {
	bind 127.0.0.1 [::1]
}
```

Per associarsi a `10.0.0.1:8080`:

```caddy
example.com:8080 {
	bind 10.0.0.1
}
```

Per associarsi a un socket di dominio Unix in `/run/caddy`:

```caddy
example.com {
	bind unix//run/caddy
}
```

Per cambiare i permessi del file affinché sia scrivibile da tutti gli utenti (il [valore predefinito](/docs/conventions#indirizzi-di-rete) è `0200`, ovvero scrivibile solo dal proprietario):

```caddy
example.com {
	bind unix//run/caddy|0222
}
```

Per associare un dominio a due interfacce diverse, con risposte differenti:

```caddy
example.com {
	bind 10.0.0.1
	respond "Uno"
}

example.com {
	bind 10.0.0.2
	respond "Due"
}
```
