---
title: fs (direttiva del Caddyfile)
---

# fs

Imposta quale file system debba essere usato per l'esecuzione dell'I/O dei file.

Questa direttiva permette di connettersi a un filesystem remoto nel cloud, a un database con un'interfaccia di tipo file, o persino di leggere file incorporati nel binario di Caddy.

Per prima cosa, è necessario dichiarare un nome per il file system usando l'[opzione globale `filesystem`](/docs/caddyfile/options#filesystem), quindi è possibile usare questa direttiva per specificare quale file system utilizzare.

Questa direttiva è spesso usata in combinazione con la [direttiva `file_server`](file_server) per servire file statici, o con la [direttiva `try_files`](try_files) per eseguire riscritture basate sull'esistenza dei file. Tipicamente viene usata anche con la [direttiva `root`](root) per impostare il percorso radice all'interno del file system.


## Sintassi

```caddy-d
fs [<matcher>] <filesystem>
```

## Esempi

Uso di un file system chiamato `foo`, utilizzando un immaginario modulo chiamato `custom` che potrebbe richiedere autenticazione:

```caddy
{
	filesystem foo custom {
		api_key abc123
	}
}

example.com {
	fs foo
	root * /srv
	file_server
}
```

Per servire solo le immagini dal file system `foo`, e il resto dal file system predefinito:

```caddy
example.com {
	fs /images* foo
	root * /srv
	file_server
}
```
