---
title: Guía rápida de Railway
---

# Guía rápida de Railway

Implementar Caddy en Railway es una forma sencilla y directa de desplegar una build personalizada de Caddy con plugins.

**Requisitos previos:**
- Una cuenta gratuita de [Railway](https://railway.com)

## Desplegar Caddy en Railway

Ve a nuestra [página de descarga](/download) y selecciona los plugins que necesites, luego haz clic en el botón morado "Deploy on Railway" en la parte superior.

<details>
	<summary>O, configura la plantilla manualmente</summary>

De forma alternativa, si quieres configurar tú mismo la plantilla de Railway, así es como hacerlo.

Ve a la plantilla en Railway:

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

y añade los plugins que necesites haciendo clic en "Configure":

![Deploy screen](/resources/images/railway/deploy-screen.png)

Luego pega los plugins en la variable `CADDY_PLUGINS`, separados por espacios:

![Adding plugins](/resources/images/railway/deploy-config.png)

</details>

Haz clic en Deploy y, cuando termine el despliegue, puedes probarlo haciendo clic en el enlace que aparece aquí:

![Visit your deployment](/resources/images/railway/prod-link.png)

Deberías ver una página de bienvenida que muestra que tu nuevo servidor está funcionando.

Luego puedes personalizar tu despliegue para servir tu propio sitio o hacer proxy a otro servicio en Railway.

## Personalizar el despliegue

Para servir tu propio sitio web o cambiar la configuración, simplemente "eject” [nuestra plantilla](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic) a tu propio repositorio:

![Eject template](/resources/images/railway/eject.png)

Desde tu propio repositorio, puedes:

- Poner tu propio sitio en la carpeta `www`.
- Modificar la configuración de Caddy, que es el [Caddyfile](/docs/caddyfile).

Simplemente haz commit y push de los cambios, luego puedes volver a desplegar en Railway.

Si quieres cambiar los plugins en tu build de Caddy, solo tienes que editar la variable `CADDY_PLUGINS` y volver a desplegar:

![Change plugins](/resources/images/railway/plugins-variable.png)

## Consejos

Railway termina TLS por ti, por lo que debes escribir tu configuración de Caddy como si fuera un proxy inverso (porque lo es). Por eso, si usas hosts en las direcciones de sitio de tu Caddyfile, debes usar `auto_https off` en las opciones globales. Caddy no actúa como edge-facing en nuestra plantilla.


## Variables

Variables de entorno que puedes definir en tu proyecto de Railway y que esta plantilla puede usar:

Nombre | Descripción | Predeterminado | Ejemplo(s)
---- | ----------- | ------- | ----------
`CADDY_PLUGINS` | Lista de plugins de Caddy separados por espacios | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
