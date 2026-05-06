---
title: El Caddyfile
---

# El Caddyfile

El **Caddyfile** es un formato de configuración de Caddy cómodo para personas. Es la forma favorita de la mayoría de la gente para usar Caddy porque es fácil de escribir, fácil de entender y lo bastante expresivo para la mayoría de casos de uso.

Se ve así:

```caddy
example.com {
	root /var/www/wordpress
	encode
	php_fastcgi unix//run/php/php-version-fpm.sock
	file_server
}
```

(Ese es un Caddyfile real listo para producción que sirve WordPress con HTTPS totalmente gestionado.)

La idea básica es que primero escribes la dirección de tu sitio y luego las funciones o características que quieres que tenga tu sitio. [Ver más patrones comunes.](/docs/caddyfile/patterns)

## Menú

- #### [Guía de inicio rápido](/docs/quick-starts/caddyfile)
  Un buen punto de partida para familiarizarte con el Caddyfile.
- #### [Tutorial completo de Caddyfile](/docs/caddyfile-tutorial)
  Aprende a hacer una variedad de cosas comunes con el Caddyfile.
- #### [Conceptos de Caddyfile](/docs/caddyfile/concepts)
  Lectura obligatoria. Estructura, direcciones de sitio, matchers, placeholders y más.
- #### [Directivas](/docs/caddyfile/directives)
  Palabras clave al inicio de las líneas que habilitan funciones para tus sitios.
- #### [Matchers de solicitudes](/docs/caddyfile/matchers)
  Filtra las solicitudes usando matchers con tus directivas.
- #### [Opciones globales](/docs/caddyfile/options)
  Configuraciones que se aplican a todo el servidor en lugar de a sitios individuales.
- #### [Patrones comunes](/docs/caddyfile/patterns)
  Formas simples de hacer tareas comunes.
<!-- - #### [Caddyfile specification](/docs/caddyfile/spec) TODO: Finish this -->


## Nota

El Caddyfile es solo un [adaptador de configuración](/docs/config-adapters) para Caddy. Generalmente se prefiere cuando se construyen configuraciones manualmente, pero no es tan expresivo, flexible o programable como la [estructura JSON nativa](/docs/json/) de Caddy. Si estás automatizando tus configuraciones/despliegues de Caddy, puede que quieras usar JSON con la [API de Caddy](/docs/api). (También puedes usar el Caddyfile con la API, solo que con un alcance limitado.)
