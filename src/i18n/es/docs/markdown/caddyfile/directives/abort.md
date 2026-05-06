---
title: abort (directiva de Caddyfile)
---

# abort

Detiene cualquier respuesta al cliente al abortar inmediatamente la cadena de handlers HTTP y cerrar la conexión. Cualquier flujo HTTP concurrente activo en la misma conexión se interrumpe.


## Sintaxis

```caddy-d
abort [<matcher>]
```

## Ejemplos

Cierra forzosamente una conexión recibida para dominios desconocidos al usar un certificado wildcard:

```caddy
*.example.com {
    @foo host foo.example.com
    handle @foo {
        respond "This is foo!" 200
    }

    handle {
		# Los dominios no gestionados llegan aquí,
		# pero no queremos aceptar sus solicitudes
        abort
    }
}
```
