---
title: map (direttiva del Caddyfile)
---

# map

Imposta i valori di placeholder personalizzati commutandoli in base a un valore di input.

Confronta il valore sorgente con il lato di input della mappa e, per quello che corrisponde, applica il valore (o i valori) di output a ciascuna destinazione. Le destinazioni diventano nomi di placeholder. È possibile specificare anche valori di output predefiniti per ciascuna destinazione.

I placeholder mappati non vengono valutati finché non vengono utilizzati, quindi anche per mappature molto grandi, questa direttiva è piuttosto efficiente.

## Sintassi

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<input> <outputs...>
	default    <defaults...>
}
```

- **&lt;source&gt;** è il valore di input su cui commutare. Solitamente un placeholder.

- **&lt;destinations...&gt;** sono i placeholder da creare che conterranno i valori di output.

- **&lt;input&gt;** è il valore di input da far corrispondere. Se preceduto da `~`, viene trattato come un'espressione regolare.

- **&lt;outputs...&gt;** è uno o più valori di output da memorizzare nel placeholder associato. Il primo output viene scritto nella prima destinazione, il secondo output nella seconda destinazione, ecc.
  
  Come caso speciale, il parser del Caddyfile tratta gli output che sono un trattino letterale (`-`) come valori null/nil. Questo è utile se volete ripiegare su un valore predefinito per quel particolare output nel caso dell'input fornito, ma volete usare valori non predefiniti per altri output.

  I valori di output verranno convertiti nel tipo appropriato se possibile; `true` e `false` verranno convertiti in tipi booleani, e i valori numerici verranno convertiti rispettivamente in interi o virgola mobile. Per evitare questa conversione, potete racchiudere l'output tra [virgolette](/docs/caddyfile/concepts#token-e-virgolette) e rimarranno stringhe.

  Il numero di output per ogni mappatura non deve superare il numero di destinazioni; tuttavia, per comodità, possono esserci meno output rispetto alle destinazioni, e gli eventuali output mancanti verranno compilati implicitamente.
  
  Se come input è stata utilizzata un'espressione regolare, i gruppi di cattura possono essere referenziati con la sintassi `${group}` dove `group` è il nome o il numero del gruppo di cattura nell'espressione. Il gruppo di cattura `0` è l'intera corrispondenza regexp, `1` è il primo gruppo di cattura, `2` il secondo, e così via.

- **&lt;default&gt;** specifica i valori di output da memorizzare se nessun input corrisponde.


## Esempi

Il seguente esempio mostra la maggior parte degli aspetti di questa direttiva:

```caddy-d
map {host}                {my_placeholder}  {magic_number} {
	example.com           "qualche valore"  3
	foo.example.com       "un altro valore"
	~(.*)\.example\.com$  "${1} sottodominio" 5

	~.*\.net$             -                 7
	~.*\.xyz$             -                 15

	default               "dominio sconosciuto" 42
}
```

Questa direttiva commuta sul valore di `{host}`, ovvero il nome di dominio della richiesta.

- Se la richiesta è per `example.com`, imposta `{my_placeholder}` su `qualche valore`, e `{magic_number}` su `3`.
- Altrimenti, se la richiesta è per `foo.example.com`, imposta `{my_placeholder}` su `un altro valore`, e lascia che `{magic_number}` vada al valore predefinito `42`.
- Altrimenti, se la richiesta è per qualsiasi sottodominio di `example.com`, imposta `{my_placeholder}` su una stringa contenente il valore del primo gruppo di cattura regexp, ovvero l'intero sottodominio, e imposta `{magic_number}` su 5.
- Altrimenti, se la richiesta è per qualsiasi host che termina in `.net` o `.xyz`, imposta solo `{magic_number}` rispettivamente su `7` o `15`. Lascia `{my_placeholder}` non impostato.
- Altrimenti (per tutti gli altri host), verranno applicati i valori predefiniti: `{my_placeholder}` verrà impostato su `dominio sconosciuto` e `{magic_number}` verrà impostato su `42`.
