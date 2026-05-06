---
title: Adaptadores de configuración
---

# Adaptadores de configuración

El lenguaje de configuración nativo de Caddy es [JSON](https://www.json.org/json-en.html), pero escribir JSON a mano puede ser tedioso y propenso a errores. Por eso Caddy soporta configurarse con otros lenguajes mediante **adaptadores de configuración**. Son plugins de Caddy que permiten usar tu formato preferido al generar [Caddy JSON](/docs/json/) por ti.

Por ejemplo, un adaptador de configuración puede [convertir tu configuración de NGINX a Caddy JSON](https://github.com/caddyserver/nginx-adapter).

## Adaptadores de configuración conocidos

Los siguientes adaptadores de configuración están disponibles actualmente (algunos son proyectos de terceros):

- [**caddyfile**](/docs/caddyfile) (estándar)
- [**nginx**](https://github.com/caddyserver/nginx-adapter)
- [**jsonc**](https://github.com/caddyserver/jsonc-adapter)
- [**json5**](https://github.com/caddyserver/json5-adapter)
- [**yaml**](https://github.com/abiosoft/caddy-yaml)
- [**cue**](https://github.com/caddyserver/cue-adapter)
- [**toml**](https://github.com/awoodbeck/caddy-toml-adapter)
- [**hcl**](https://github.com/francislavoie/caddy-hcl)
- [**dhall**](https://github.com/mholt/dhall-adapter)
- [**mysql**](https://github.com/zhangjiayin/caddy-mysql-adapter)

## Usar adaptadores de configuración

Puedes usar un adaptador de configuración especificándolo en la línea de comandos con la marca `--adapter` en la mayoría de subcomandos que aceptan una configuración:

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

O a través de la API en el endpoint [`/load`](/docs/api#post-load):

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

Si solo quieres obtener el JSON de salida sin ejecutarlo, puedes usar el comando [`caddy adapt`](/docs/command-line#caddy-adapt):

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

## Precauciones

No todos los lenguajes de configuración son 100% compatibles con Caddy; algunas funciones o comportamientos simplemente no se traducen bien o aún no están implementados en el adaptador o en Caddy.

Algunos adaptadores hacen una traducción 1 a 1, como YAML→JSON o TOML→JSON. Otros están diseñados específicamente para Caddy, como el Caddyfile. En general, estos adaptadores funcionarán siempre.

Sin embargo, no todos los adaptadores funcionan en todo momento. Los adaptadores de configuración hacen su mejor esfuerzo para traducir tu entrada a JSON de Caddy con la mayor fidelidad y corrección posible. Como este proceso de conversión no está garantizado como completo y correcto todo el tiempo, no los llamamos "convertidores" ni "traductores". Son "adaptadores" porque al menos te dan un buen punto de partida para terminar de construir tu configuración JSON final.

Los adaptadores de configuración pueden mostrar JSON resultante, advertencias y errores. Los JSON aparecen cuando no hay errores. Los errores ocurren cuando hay algo incorrecto en la entrada (por ejemplo, errores de sintaxis). Las advertencias se emiten cuando algo está mal en la adaptación pero no necesariamente es fatal (por ejemplo, una función no soportada). Ten precaución si usas configuraciones que se adaptaron con advertencias.
