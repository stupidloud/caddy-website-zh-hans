---
title: bind (directiva de Caddyfile)
---

# bind

Sobrescribe la interfaz a la que debe enlazar el socket del servidor.

Normalmente, el listener se enlaza a la interfaz vacía (wildcard). Sin embargo, puedes forzar el listener a enlazar a otro hostname o IP en su lugar. Esta directiva acepta solo un host, no un puerto. El puerto lo determina la [dirección del sitio](/docs/caddyfile/concepts#addresses) (por defecto `443`).

Ten en cuenta que enlazar sitios de forma inconsistente puede tener consecuencias no deseadas. Por ejemplo, si dos sitios en el mismo puerto resuelven a `127.0.0.1` y solo uno de esos sitios está configurado con `bind 127.0.0.1`, solo un sitio será accesible, ya que el otro se enlazará al puerto sin un host específico; el sistema operativo elegirá el socket con la coincidencia más específica. (Los hosts virtuales no se comparten entre listeners diferentes.)

`bind` acepta [direcciones de red](/docs/conventions#network-addresses), pero no puede incluir un puerto.


## Sintaxis

```caddy-d
bind <hosts...>
```

- **&lt;hosts...&gt;** es la lista de interfaces de host para enlazar con el listener.


## Ejemplos

Para hacer un socket accesible solo en la máquina actual, enlaza a la interfaz loopback (localhost):

```caddy
example.com {
	bind 127.0.0.1
}
```

Para incluir IPv6:

```caddy
example.com {
	bind 127.0.0.1 [::1]
}
```

Para enlazar a `10.0.0.1:8080`:

```caddy
example.com:8080 {
	bind 10.0.0.1
}
```

Para enlazar a un socket de dominio Unix en `/run/caddy`:

```caddy
example.com {
	bind unix//run/caddy
}
```

Para cambiar el permiso del archivo para que sea escribible por todos los usuarios ([por defecto](/docs/conventions#network-addresses) es `0200`, que solo puede ser escrito por el propietario):

```caddy
example.com {
	bind unix//run/caddy|0222
}
```

Para enlazar un dominio a dos interfaces diferentes, con respuestas distintas:

```caddy
example.com {
	bind 10.0.0.1
	respond "One"
}

example.com {
	bind 10.0.0.2
	respond "Two"
}
```
