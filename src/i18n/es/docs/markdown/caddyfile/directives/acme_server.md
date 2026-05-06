---
title: acme_server (directiva de Caddyfile)
---

# acme_server

Un manejador de servidor [protocolo ACME](https://tools.ietf.org/html/rfc8555) integrado. Esto permite que una instancia de Caddy emita certificados para cualquier software compatible con ACME (incluyendo otras instancias de Caddy).

Cuando está habilitado, las solicitudes que coincidan con la ruta `/acme/*` serán gestionadas por el servidor ACME.


## Configuración del cliente

Usando los valores por defecto de ACME, los clientes ACME deben configurarse para usar `https://localhost/acme/local/directory` como su endpoint ACME. (`local` es el ID de la CA por defecto de Caddy.)


## Sintaxis

```caddy-d
acme_server [<matcher>] {
	ca         <id>
	lifetime   <duration>
	resolvers  <resolvers...>
	challenges <challenges...>
	allow_wildcard_names
	allow {
		domains <domains...>
		ip_ranges <addresses...>
	}
	deny {
		domains <domains...>
		ip_ranges <addresses...>
	}
}
```

- **ca** especifica el ID de la autoridad certificadora con la que firmar certificados. El valor por defecto es `local`, que es la CA por defecto de Caddy, pensada para certificados autofirmados de uso local, lo más común en entornos de desarrollo. Para un uso más amplio, se recomienda especificar una CA distinta para evitar confusión. Si la CA con el ID dado aún no existe, se creará. Consulta las [opciones globales de la app PKI](/docs/caddyfile/options#pki-options) para configurar CA alternativas.

- **lifetime** (por defecto: `12h`) es una [duración](/docs/conventions#durations) que especifica el período de validez de los certificados emitidos. Este valor debe ser menor que la vida del [certificado intermedio](/docs/caddyfile/options#intermediate-lifetime) usado para firmar. No se recomienda cambiarlo salvo que sea absolutamente necesario.

- **resolvers** son las direcciones de los resolvers DNS usados para buscar los registros TXT al resolver retos ACME DNS. Acepta [direcciones de red](/docs/conventions#network-addresses) y usa por defecto UDP y puerto 53 salvo que se indique lo contrario. Si el host es una dirección IP, se conectará directamente para resolver el servidor upstream. Si el host no es una IP, las direcciones se resuelven usando la [convención de resolución de nombres](https://golang.org/pkg/net/#hdr-Name_Resolution) de la biblioteca estándar de Go. Si se especifican múltiples resolvers, se elige uno al azar.

- **challenges** establece los tipos de desafío habilitados. Si no se establece o la directiva se usa sin valores, se habilitan todos los tipos de desafío. Los valores aceptados son: http-01, tls-alpn-01, dns-01.

- **allow_wildcard_names** habilita la emisión de certificados con wildcard SAN (Subject Alternative Name).

- **allow**, **deny** configuran la política operativa de `acme_server`. La evaluación de política sigue los criterios descritos por Step-CA [aquí](https://smallstep.com/docs/step-ca/policies/#policy-evaluation).

	- **domains** establece los nombres de dominio de sujeto permitidos o denegados según los criterios de evaluación de política.

	- **ip_ranges** establece los rangos IP de sujeto permitidos o denegados según los criterios de evaluación de política.

## Ejemplos

Para servir un servidor ACME con ID `home` en el dominio `acme.example.com`, con la CA personalizada mediante la [opción global `pki`](/docs/caddyfile/options#pki-options) y emitiendo su propio certificado usando el issuer `internal`:

```caddy
{
	pki {
		ca home {
			name "My Home CA"
		}
	}
}

acme.example.com {
	tls {
		issuer internal {
			ca home
		}
	}
	acme_server {
		ca home
	}
}
```

Si tienes otro servidor Caddy, puede usar el servidor ACME anterior para emitir sus propios certificados:

```caddy
{
	acme_ca https://acme.example.com/acme/home/directory
	acme_ca_root /path/to/home_ca_root.crt
}

example.com {
	respond "Hello, world!"
}
```
