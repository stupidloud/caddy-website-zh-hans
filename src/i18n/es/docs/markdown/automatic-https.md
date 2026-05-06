---
title: "HTTPS automático"
---

# HTTPS automático

**Caddy fue el primer servidor web en usar HTTPS de forma automática _y de forma predeterminada_.**

HTTPS automático emite certificados TLS para todos tus sitios y los mantiene renovados. También redirige HTTP a HTTPS por ti. Caddy usa valores predeterminados modernos y seguros; no requiere tiempo de inactividad, configuración adicional ni herramientas separadas.

<aside class="tip">
	Caddy fue pionero en la tecnología de HTTPS automático; esto es así desde 2015, cuando se volvió viable. La lógica de automatización de HTTPS de Caddy es la más madura y robusta del mundo.
</aside>

Este es un vídeo de 28 segundos que muestra cómo funciona:

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**Menú:**

- [Overview](#overview)
- [Activation](#activation)
- [Effects](#effects)
- [Hostname requirements](#hostname-requirements)
- [Local HTTPS](#local-https)
- [Testing](#testing)
- [ACME Challenges](#acme-challenges)
- [On-Demand TLS](#on-demand-tls)
- [Errors](#errors)
- [Storage](#storage)
- [Wildcard certificates](#wildcard-certificates)
- [Encrypted ClientHello (ECH)](#encrypted-clienthello-ech)



## Overview

**Por defecto, Caddy sirve todos los sitios por HTTPS.**

- Caddy sirve direcciones IP y nombres de host internos/locales con HTTPS usando certificados autofirmados que se confían automáticamente de forma local (si está permitido).
	- Ejemplos: `localhost`, `127.0.0.1`
- Caddy sirve nombres DNS públicos con HTTPS usando certificados de una CA ACME pública como [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) o [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com).
	- Ejemplos: `example.com`, `sub.example.com`, `*.example.com`

Caddy mantiene todos los certificados gestionados renovados y redirige HTTP (puerto `80` predeterminado) a HTTPS (puerto `443`) automáticamente.

**Para HTTPS local:**

- Caddy puede solicitar una contraseña para instalar su certificado raíz único en el almacén de confianza local. Esto sucede solo una vez por raíz y puedes quitarlo en cualquier momento.
- Cualquier cliente que acceda al sitio sin confiar en el certificado de la CA raíz de Caddy mostrará errores de seguridad.

**Para nombres de dominio públicos:**

<aside class="tip">

Estos son requisitos comunes para cualquier sitio de producción básico, no solo para Caddy. La diferencia principal es definir correctamente tus registros DNS **antes** de ejecutar Caddy para que pueda emitir certificados.

</aside>


- Si los registros A/AAAA de tu dominio apuntan a tu servidor,
- los puertos `80` y `443` están abiertos externamente,
- Caddy puede enlazar (`bind`) esos puertos (o esos puertos se reenvían a Caddy),
- tu [directorio de datos](/docs/conventions#data-directory) es escribible y persistente,
- y el nombre de dominio aparece en algún lugar relevante de la configuración,

entonces los sitios se servirán por HTTPS automáticamente. No tendrás que hacer nada más. ¡Funciona.

Debido a que HTTPS usa una infraestructura pública compartida, como administrador del servidor debes entender el resto de esta página para evitar problemas innecesarios, depurarlos cuando ocurran y configurar correctamente implementaciones avanzadas.



## Activation

Caddy activa HTTPS automático de forma implícita cuando conoce un nombre de dominio (por ejemplo, un hostname) o una dirección IP que sirve. Hay varias formas de informar el dominio/IP a Caddy según cómo ejecutes o configures Caddy:

- Una [dirección de sitio](/docs/caddyfile/concepts#addresses) en el [Caddyfile](/docs/caddyfile)
- Un [host matcher](/docs/json/apps/http/servers/routes/match/host/) al nivel superior en las [rutas JSON](/docs/modules/http#servers/routes)
- Banderas de la CLI como [`--domain`](/docs/command-line#caddy-file-server) o [`--from`](/docs/command-line#caddy-reverse-proxy)
- El cargador de certificados [automate](/docs/json/apps/tls/certificates/automate/)

Cualquiera de los siguientes casos impedirá activar HTTPS automático, total o parcialmente:

- Deshabilitarlo explícitamente [mediante JSON](/docs/json/apps/http/servers/automatic_https/) o [mediante Caddyfile](/docs/caddyfile/options#auto-https)
- No proporcionar nombres de host o direcciones IP en la configuración
- Escuchar exclusivamente en el puerto HTTP
- Anteponer `http://` a la [dirección de sitio](/docs/caddyfile/concepts#addresses) en el Caddyfile
- Cargar certificados manualmente (salvo que se defina [`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/))

**Casos especiales:**

- Los dominios que terminan en `.ts.net` no los gestiona Caddy. En su lugar, Caddy intenta obtener automáticamente esos certificados en tiempo de handshake desde la instancia local de [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com). Esto requiere que [HTTPS esté habilitado en tu cuenta de Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/) y que el proceso de Caddy se ejecute como root, o que configures `tailscaled` para dar a tu usuario de Caddy [permiso para obtener certificados](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).


## Effects

Cuando HTTPS automático se activa, sucede lo siguiente:

- Se obtienen y renuevan certificados para [todos los nombres de dominio válidos](#hostname-requirements)
- HTTP se redirige a HTTPS (usa el [puerto HTTP](/docs/modules/http#http_port) `80`)

HTTPS automático nunca sobrescribe la configuración explícita; solo la complementa.

Si ya tienes un [server](/docs/json/apps/http/servers/) escuchando en el puerto HTTP, las rutas de redirección HTTP->HTTPS se insertarán después de tus rutas con un matcher de host, pero antes de una ruta catch-all definida por el usuario.

Puedes [personalizar o desactivar HTTPS automático](/docs/json/apps/http/servers/automatic_https/) si lo necesitas; por ejemplo, puedes omitir ciertos dominios o desactivar redirecciones (para Caddyfile hazlo con las [opciones globales](/docs/caddyfile/options)).


## Hostname requirements

Todos los nombres de host (nombres de dominio) califican para certificados totalmente gestionados si:

- no están vacíos
- consisten solo en alfanuméricos, guiones, puntos y wildcard (`*`)
- no comienzan ni terminan con un punto ([RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5))

Además, los nombres de host califican para certificados de confianza pública si:

- no son localhost (incluyendo TLDs `.localhost`, `.local`, `.internal` y `.home.arpa`)
- no son direcciones IP
- tienen un único comodín `*` como etiqueta más a la izquierda


## Local HTTPS

Caddy usa HTTPS automáticamente para todos los sitios con host especificado (dominio, IP o hostname), incluidos hosts internos y locales. Algunos hosts no son públicos (por ejemplo, `127.0.0.1`, `localhost`) o generalmente no califican para certificados de confianza pública (por ejemplo, IPs; puedes obtener certificados para ellas, pero solo de algunas CAs). Aun así siguen sirviéndose con HTTPS a menos que lo desactives.

Para servir sitios no públicos con HTTPS, Caddy genera su propia autoridad certificadora (CA) y la usa para firmar certificados. La cadena de confianza consta de un certificado raíz y uno intermedio. Los certificados leaf están firmados por el intermedio. Se guardan en [el directorio de datos de Caddy](/docs/conventions#data-directory), en `pki/authorities/local`.

Caddy local HTTPS está impulsado por las [librerías de Smallstep <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/).

HTTPS local no usa ACME ni realiza validación DNS. Funciona solo en la máquina local y es confiable solo donde el certificado raíz de la CA esté instalado.

### CA Root

La clave privada de la raíz se genera de forma única usando una fuente criptográficamente segura pseudoaleatoria y se guarda en almacenamiento con permisos limitados. Solo se carga en memoria para tareas de firma y luego sale de alcance para ser recolectada.

Aunque Caddy puede configurarse para firmar directamente con la raíz (para compatibilidad con clientes no conformes), esto está deshabilitado por defecto y la clave raíz solo se usa para firmar intermedios.

La primera vez que se usa una clave raíz, Caddy intentará instalarla en el/los almacenes de confianza local del sistema. Si no tiene permisos para hacerlo, solicitará contraseña. Este comportamiento puede desactivarse con [`skip_install_trust` en un caddyfile](/docs/caddyfile/options#skip-install-trust) o [`"install_trust": false` en configuración json](/docs/json/apps/pki/certificate_authorities/install_trust/). Si falla por ejecutarse como usuario sin privilegios, puedes ejecutar [`caddy trust`](/docs/command-line#caddy-trust) para reintentar la instalación como usuario privilegiado.

<aside class="tip">
	Es seguro confiar en el certificado raíz de Caddy en tu máquina siempre que tu equipo no esté comprometido y tu clave raíz única no se filtre.
</aside>

Tras instalar la CA raíz de Caddy, la verás en tu almacén local con el nombre "Caddy Local Authority" (salvo que hayas configurado otro nombre). Puedes desinstalarla en cualquier momento; el comando [`caddy untrust`](/docs/command-line#caddy-untrust) lo facilita.

Nota: la instalación automática del certificado en los almacenes de confianza locales es solo por conveniencia y no está garantizada, especialmente si se usan contenedores o si Caddy se ejecuta como servicio del sistema sin privilegios. En última instancia, si usas una PKI interna, es responsabilidad del administrador del sistema asegurar que la CA raíz de Caddy esté bien añadida en los almacenes de confianza necesarios (esto está fuera del alcance del servidor web).


### CA Intermediates

También se generará un certificado y clave intermedios, que se usarán para firmar certificados leaf (de sitio individual).

A diferencia del certificado raíz, los certificados intermedios tienen una vida útil mucho menor y se renuevan automáticamente cuando sea necesario.


## Testing

Para probar o experimentar con tu configuración de Caddy, asegúrate de [cambiar el endpoint ACME](/docs/modules/tls.issuance.acme#ca) a una URL de staging o desarrollo; de lo contrario, probablemente alcanzarás límites de tasa que pueden bloquear HTTPS durante hasta una semana, según el límite que superes.

Uno de los endpoints por defecto de Caddy es [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/), que tiene un [entorno de staging <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) que no está sujeto a los mismos [límites de tasa <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/):

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

## ACME challenges

Obtener un certificado TLS de confianza pública requiere validación de una autoridad de terceros de confianza pública. Actualmente, este proceso está automatizado con el [protocolo ACME <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555), y se puede ejecutar de tres formas (“tipos de challenge”), descritas abajo.

Los dos primeros challenge están habilitados por defecto. Si hay varios habilitados, Caddy elige uno al azar para evitar dependencia accidental de un tipo. Con el tiempo aprende cuál funciona mejor y lo prefiera primero, y cae a otros tipos disponibles si es necesario.


### HTTP challenge

El HTTP challenge realiza una consulta DNS autorizada para el registro A/AAAA del hostname candidato y luego pide un recurso criptográfico temporal por el puerto `80` mediante HTTP. Si la CA ve el recurso esperado, se emite un certificado.

Este challenge requiere que el puerto `80` sea accesible externamente. Si Caddy no puede escuchar en el puerto 80, los paquetes de ese puerto deben reenviarse al [puerto HTTP](/docs/json/apps/http/http_port/) de Caddy.

Este challenge está habilitado por defecto y no requiere configuración explícita.


### TLS-ALPN challenge

El TLS-ALPN challenge hace una consulta DNS autorizada del registro A/AAAA del hostname candidato y luego solicita un recurso criptográfico temporal por el puerto `443` mediante un handshake TLS que incluye valores especiales de ServerName y ALPN. Si la CA ve el recurso esperado, se emite un certificado.

Este challenge requiere que el puerto `443` sea accesible externamente. Si Caddy no puede escuchar en el puerto 443, los paquetes de ese puerto deben reenviarse al [puerto HTTPS](/docs/json/apps/http/https_port/) de Caddy.

Este challenge está habilitado por defecto y no requiere configuración explícita.


### DNS challenge

El DNS challenge realiza una consulta DNS autorizada de los registros `TXT` del hostname candidato y busca un registro `TXT` especial con un valor específico. Si la CA ve el valor esperado, se emite un certificado.

Este challenge no requiere puertos abiertos, y el servidor que solicita un certificado no necesita ser accesible externamente. Sin embargo, exige configuración. Caddy debe conocer las credenciales para acceder al proveedor DNS de tu dominio para que pueda establecer (y limpiar) los registros `TXT` especiales. Si se habilita el DNS challenge, los otros challenges se desactivan por defecto.

Dado que las CAs ACME siguen las normas DNS al consultar registros `TXT` para la verificación de challenge, puedes usar registros CNAME para delegar la respuesta del challenge a otras zonas DNS. Esto se puede usar para delegar la subzona `_acme-challenge` en [otra zona](/docs/caddyfile/directives/tls#dns_challenge_override_domain). Es útil si tu proveedor DNS no ofrece API o no es compatible con alguno de los plugins DNS de Caddy.

El soporte de proveedores DNS es un esfuerzo comunitario. [Lee cómo habilitar el DNS challenge para tu proveedor en nuestra wiki.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


## On-Demand TLS

Caddy introdujo una nueva tecnología llamada **On-Demand TLS**, que obtiene dinámicamente un certificado durante el primer handshake TLS que lo requiere, en lugar de hacerlo al cargar la configuración. Lo importante es que esto **no** requiere definir de antemano los nombres de dominio en la configuración.

Muchas empresas usan esta característica para escalar despliegues TLS con menos costo y sin dolores operativos al servir decenas de miles de sitios.

TLS bajo demanda es útil si:

- no conoces todos los nombres de dominio al iniciar o recargar el servidor
- los nombres no están correctamente configurados inicialmente (registros DNS aún no definidos)
- no controlas los dominios (por ejemplo, son dominios de clientes)

Cuando se habilita, no es necesario definir esos dominios en la configuración para obtener certificados. Cuando llega un handshake TLS para un nombre de servidor (SNI) sin certificado en Caddy, el handshake se mantiene mientras Caddy obtiene uno para completarlo. La demora suele ser de unos segundos, y solo afecta al primer handshake. Los siguientes handshakes son rápidos porque los certificados se reutilizan desde caché; las renovaciones ocurren en segundo plano. Handshakes posteriores pueden disparar mantenimiento de certificados para conservarlos actualizados, pero ese mantenimiento ocurre en segundo plano si el certificado aún no expiró.

### Using On-Demand TLS

**On-Demand TLS debe activarse y restringirse para evitar abuso.**

La activación de TLS bajo demanda se configura en las [políticas de automatización TLS](/docs/json/apps/tls/automation/policies/) en configuración JSON, o en bloques de sitio con la directiva `tls` en Caddyfile.

Para prevenir abuso de esta función, debes configurar restricciones. Esto se hace en el objeto [`automation` de JSON](/docs/json/apps/tls/automation/on_demand/) o en la opción global [`on_demand_tls` del Caddyfile](/docs/caddyfile/options#on-demand-tls). Las restricciones son “globales” y no se pueden ajustar por sitio o por dominio. La restricción principal es un endpoint “ask” al que Caddy enviará una petición HTTP para pedir permiso para obtener y gestionar un certificado del dominio en el handshake. Necesitas un backend interno que pueda consultar, por ejemplo, la tabla de cuentas en tu base de datos para verificar si el cliente registró ese dominio.

Ten en cuenta qué tan rápido puede emitir tu CA. Si tarda más de unos segundos, afecta negativamente a la experiencia (solo al primer cliente).

Por su ejecución diferida y la configuración extra para prevenir abuso, recomendamos habilitar TLS bajo demanda solo cuando el caso de uso lo justifique como se describió antes.

[Consulta este artículo de la wiki para más información sobre cómo usar TLS bajo demanda eficazmente.](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)

## Errors

Caddy intenta seguir funcionando si ocurren errores en la gestión de certificados.

Por defecto, la gestión de certificados se ejecuta en segundo plano. Esto significa que no bloquea el arranque ni ralentiza tus sitios. Sin embargo, también significa que el servidor puede estar en ejecución antes de que todos los certificados estén disponibles. Al ejecutarse en segundo plano, Caddy reintenta con backoff exponencial durante un largo periodo.

Así es lo que ocurre cuando hay un error al obtener o renovar un certificado:

1. Caddy reintenta una vez tras una pausa breve, por si fue un fallo esporádico
2. Caddy pausa brevemente y cambia al siguiente tipo de challenge habilitado
3. Tras probar todos los tipos habilitados, [prueba el siguiente emisor configurado](#issuer-fallback)
	- Let's Encrypt
	- ZeroSSL
4. Tras probar todos los emisores, hace backoff exponencial
	- máximo de 1 día entre intentos
	- hasta por 30 días

Durante reintentos con Let's Encrypt, Caddy usa su [entorno de staging <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) para evitar problemas de límite de tasa. No es perfecto, pero normalmente funciona bien.

Los challenges ACME tardan al menos unos segundos, y la limitación interna ayuda a evitar abuso accidental. Caddy usa limitación interna además de la que configures tú o la CA, para que puedas pasarle un millón de dominios y obtendrá certificados para todos de manera gradual, tan rápido como sea posible. El límite interno actual es de 10 intentos por cuenta ACME cada 10 segundos.

Para evitar consumir recursos innecesariamente, Caddy aborta tareas en curso (incluidas transacciones ACME) cuando cambia la configuración. Aunque Caddy puede gestionar recargas frecuentes, considera agrupar cambios para reducir recargas y permitir que termine la emisión de certificados en segundo plano.

### Issuer fallback

Caddy fue el primer servidor (y hasta ahora el único) que soporta failover totalmente redundante y automático a otras CAs cuando no puede emitir un certificado con éxito.

Por defecto, Caddy habilita dos CAs compatibles con ACME: [**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) y [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com). Si Caddy no puede emitir con Let's Encrypt, probará con ZeroSSL; si ambos fallan, esperará con backoff y reintentará después. En tu configuración puedes personalizar qué emisores usar para obtener certificados, de forma global o por nombres concretos.


## Storage

Caddy guarda certificados públicos, claves privadas y otros recursos en su [almacenamiento configurado](/docs/json/storage/) (o en el predeterminado si no está configurado; consulta el enlace para detalles).

**Usando la configuración predeterminada, la carpeta `$HOME` debe ser escribible y persistente.** Para ayudarte a depurar, Caddy imprime sus variables de entorno al iniciar si se indica la bandera `--environ`.

Todas las instancias de Caddy que compartan el mismo almacenamiento compartirán automáticamente estos recursos y coordinarán la gestión de certificados como un clúster.

Antes de intentar transacciones ACME, Caddy probará el almacenamiento configurado para verificar que sea escribible y tenga capacidad suficiente. Esto ayuda a reducir contención de bloqueos innecesarios.


## Wildcard certificates

Caddy puede obtener y gestionar certificados comodín cuando configura un sitio con un nombre wildcard válido. Un nombre de sitio valida para comodín si solo su etiqueta de dominio más a la izquierda es comodín. Por ejemplo, `*.example.com` valida, pero estos no: `sub.*.example.com`, `foo*.example.com`, `*bar.example.com` y `*.*.example.com`. (Es una restricción de WebPKI.)

Si usas Caddyfile, Caddy toma los nombres de sitio literalmente respecto a los sujetos del certificado. Es decir, un sitio definido como `sub.example.com` hará que Caddy gestione un certificado para `sub.example.com`, y uno definido como `*.example.com` hará que gestione un comodín para `*.example.com`. Esto se muestra en [Common Caddyfile Patterns](/docs/caddyfile/patterns#wildcard-certificates). Si necesitas comportamiento distinto, la [configuración JSON](/docs/json/) te da control más preciso de sujetos y nombres de sitio (“host matchers”).

Desde Caddy 2.10, al automatizar un certificado comodín, Caddy usa ese comodín para subdominios individuales en la configuración. No obtendrá certificados individuales salvo que se configure explícitamente (por ejemplo con `force_automate`).

Los certificados comodín otorgan bastante autoridad y deben usarse solo cuando tienes tantos subdominios que gestionar certificados individuales pondría en tensión la PKI o provocaría límites de tasa, o si la compensación de privacidad justifica el riesgo de exponer tanta zona DNS ante un compromiso de clave. Nota que un comodín por sí solo no oculta subdominios: siguen expuestos en paquetes TLS ClientHello si no está habilitado Encrypted ClientHello (ECH). (Ver abajo.)

**Nota:** [Let's Encrypt exige <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) el [DNS challenge](#dns-challenge) para emitir certificados comodín.


## Encrypted ClientHello (ECH)

Normalmente, los handshakes TLS envían el ClientHello, incluido el Server Name Indicator (SNI; el dominio de destino), en texto plano. Esto incluye parámetros necesarios para cifrar la conexión posterior al handshake. Así, el nombre de dominio queda expuesto a cualquiera que intercepte conexiones, incluso fuera de tu entorno físico. Esto revela qué servicio se está alcanzando cuando una IP destino sirve muchos sitios, y es una vía de censura.

Con Encrypted ClientHello, el cliente puede proteger el nombre de dominio envolviendo el ClientHello real en un ClientHello “externo” que establece parámetros para descifrar el “interno”. Sin embargo, muchas piezas deben coordinarse para que esto funcione y aporte privacidad real.

Primero, el cliente debe conocer qué parámetros o configuración usar para cifrar el ClientHello. Esa información incluye una clave pública y un dominio “externo” (“public name”), entre otros datos. Esa configuración debe publicarse o distribuirse de forma fiable.

En teoría podrías escribirlo y compartirlo manualmente, pero la mayoría de navegadores modernos consulta registros DNS tipo HTTPS con parámetros ECH al conectarse. Por eso, necesitas (1) generar una configuración ECH (par de claves pública/privada y otros parámetros), y luego (2) crear un registro DNS HTTPS con la configuración ECH en base64.

O puedes dejar que Caddy haga todo. Caddy es el primer y único servidor web que puede generar, publicar y servir configuraciones ECH automáticamente.

Cuando el registro HTTPS se publica, los clientes realizan una consulta DNS HTTPS al conectarse. Las consultas DNS normalmente son texto plano, lo que puede comprometer la seguridad de los handshakes ECH; por eso los navegadores deben usar DNS seguro como DNS-over-HTTPS (DoH) o DNS-over-TLS (DoT). Según el navegador, puede requerir activación manual.

Cuando el cliente descarga de forma segura la configuración ECH, usa la clave pública embebida para cifrar el ClientHello y se conecta al sitio. Luego Caddy descifra el ClientHello interno y atiende el sitio sin que el nombre de dominio aparezca en texto plano.

### Deployment considerations

ECH es una tecnología compleja. Aunque Caddy automatiza ECH, hay muchos puntos a considerar para obtener beneficios de privacidad máximos. También debes conocer los distintos trade-offs.

#### Publication

Caddy solo crea un registro HTTPS para un dominio si ya existe uno para ese dominio. Esto evita romper consultas DNS para un subdominio que pueda estar cubierto por comodín. Asegúrate de que tus sitios tengan al menos un registro A/AAAA apuntando a tu servidor. Si solo usas comodines en DNS, ese dominio comodín también debe estar en la configuración de Caddy.

Caddy no publicará un registro HTTPS para un dominio con registro CNAME.

#### ECH GREASE

Si abres Wireshark y conectas a cualquier sitio (incluso uno sin ECH) con un navegador moderno como Firefox o Chrome (aunque ECH esté desactivado), puedes ver que el handshake incluye la extensión `encrypted_client_hello`:

![ECH GREASE](/resources/images/ech-grease.png)

Esto hace que los handshakes ECH reales sean indistinguibles de los de texto plano. Si los handshakes ECH se viesen diferentes, los censores podrían bloquearlos con poco daño colateral. Si bloquean cualquier handshake con esa extensión, apagarían la mayor parte de Internet. (El objetivo es elevar el costo de una censura masiva.)

Esto importa sobre todo al depurar conexiones.

#### Key rotation

Como con las claves de certificados, no es recomendable (y puede ser inseguro) usar la misma clave por mucho tiempo. Por ello, las claves ECH deben rotarse periódicamente. A diferencia de certificados, las configuraciones ECH no caducan estrictamente; aun así, deberían rotarse.

La rotación es delicada porque los clientes deben conocer las claves actualizadas. Si el servidor reemplaza inmediatamente claves antiguas por nuevas, todos los handshakes ECH fallarían salvo notificación inmediata al cliente. Pero publicar claves actualizadas no es suficiente: los registros DNS tienen TTL y los resolutores cachean respuestas. Puede llevar minutos, horas o días que los clientes consulten los registros HTTPS actualizados y empiecen a usar la configuración nueva.

Por ello, los servidores deben mantener soporte de configuraciones ECH antiguas durante un tiempo. Si no, se filtra el nombre del servidor en texto plano *a gran escala*. Caddy rota claves periódicamente y conserva claves rotadas un tiempo hasta descartarlas.

Puede no bastar. Algunos clientes no obtienen claves actualizadas y, cuando ocurre, existe riesgo de exponer el nombre del servidor. Por eso hace falta otro mecanismo para enviar la configuración actualizada *in-band* con la conexión: el *_outer name_* (o *_public name_*).

#### Public name

El ClientHello “externo” es un ClientHello normal con dos diferencias sutiles que solo conoce el servidor de origen:

1. La extensión SNI es falsa
2. La extensión ECH es real

Ese SNI externo contiene el public name que protege tus dominios reales. Puede ser cualquier nombre, pero **tu servidor debe ser autoritativo** para ese nombre porque Caddy **obtendrá** un certificado para él.

Si un cliente intenta ECH y el servidor no puede descifrar el ClientHello interno, puede completar el handshake con el ClientHello externo usando un certificado del nombre externo. Esta conexión segura se usa solo para enviar la configuración ECH actual; es una conexión TLS temporal para completar el handshake inicial. No se envían datos de aplicación, solo la clave ECH. Cuando el cliente tiene la clave actual, establece la TLS como debe ser.

Así, el nombre real del servidor permanece protegido y los clientes fuera de sincronía siguen pudiendo conectar, ambos elementos clave para la seguridad.

El nombre externo puede ser uno de tus dominios, un subdominio, o cualquier dominio que apunte a tu servidor. Recomendamos usar exactamente un nombre genérico; por ejemplo, Cloudflare protege millones de sitios tras `cloudflare-ech.com`. Esto aumenta el tamaño de tu anonymity set.

El public name no debe estar vacío; debe existir para que esto funcione. Caddy aún no lo obliga de forma estricta (puede hacerlo más adelante), pero la especificación ECH requiere al menos 1 byte. Algunos clientes aceptan nombres vacíos y otros no. Puede generar comportamientos confusos como clientes que usan ECH y servidores lo rechazan como inválido, o clientes que no usan ECH al verlo inválido aunque el config esté correctamente en DNS. El propietario del sitio debe asegurar configuración y publicación correctas para proteger privacidad.

#### Anonymity set

Para maximizar los beneficios de privacidad de ECH, busca maximizar el tamaño de tu *anonymity set*. En esencia es el conjunto de servidores accesibles al cliente con comportamiento idéntico frente a observadores. La idea es que un observador no pueda deducir fácilmente los posibles sitios o servicios conectados.

En la práctica recomendamos un único public name para todos tus sitios. (Hay solo 1 public name por configuración ECH, lo que implica una configuración activa a la vez.) Si ejecutas Caddy en un clúster, Caddy comparte y coordina ECH con otras instancias.

Extremadamente, esto implica que todos los sitios de Internet podrían estar detrás de una sola IP y un solo public name...

#### Centralization

... lo que nos lleva a la centralización. Una crítica de ECH es que puede incentivar la centralización. Esto ocurre al menos en dos formas: (1) clientes prefieren DoH/DoT para resolver DNS, enviando todas las consultas DNS a pocos proveedores, y (2) maximizar anonymity set a escala.

Con DoH/DoT, todas las búsquedas DNS pasan por el proveedor DoH/DoT. Entre cliente y proveedor los datos DNS van cifrados, pero entre proveedor y servidor DNS no. DoH/DoT global concentra prácticamente todo el tráfico DNS en texto plano en pocas “tuberías”, lo que facilita observación o fallos.

De forma similar, si se maximiza al extremo el anonymity set, todos los sitios quedarían protegidos detrás de un único public name, como `cloudflare-ech.com`. Esto mejora privacidad, pero toda Internet quedaría dependiente de Cloudflare y ese dominio. No es necesario ni práctico al máximo, pero las implicaciones teóricas siguen siendo válidas.

Recomendamos que cada organización o persona use un único nombre para todos sus sitios; en muchos casos basta para privacidad suficiente. Consulta un análisis de amenazas para tu caso.

#### Subdomain privacy

Con ECH, teóricamente ya es posible mantener subdominios privados frente a canales laterales si se despliega correctamente.

La mayoría de sitios no lo requieren; en general, los subdominios son información pública. Evita poner datos sensibles en nombres de dominio.

Para evitar filtrar subdominios sensibles en logs de Certificate Transparency (CT), usa un certificado comodín. Es decir, en vez de `sub.example.com`, usa `*.example.com`. (Consulta [Wildcard certificates](#wildcard-certificates) para detalles importantes.)

Otra fuente de fuga es DNSSEC. La mayoría de servidores DNS autoritativos usan “zone walking”: se puede enumerar subdominios por registros NSEC que señalan el siguiente subdominio disponible en orden alfabético. Asegura que tu dominio use al menos NSEC3 o, idealmente, CNAME comodín para mitigarlo.

Luego habilita ECH en Caddy. Un certificado comodín junto con ECH y un CNAME comodín ocultan subdominios correctamente, siempre que cada cliente que conecte use ECH y lo implemente bien. (Aún dependes de los clientes para mantener la privacidad.)

### Habilitar ECH

Como ECH funcional requiere publicar configuraciones en DNS, necesitas una compilación de Caddy con un [módulo caddy-dns](https://github.com/caddy-dns) para tu proveedor DNS.

Luego, en Caddyfile, especifica en opciones globales el proveedor DNS y el nombre público ECH:

```caddy
{
	dns <provider config...>
	ech example.com
}
```

Recuerda:

- El módulo DNS del proveedor debe estar habilitado y debes tener la configuración correcta para ese proveedor/cuenta.
- El public name de ECH debe apuntar a tu servidor. Caddy obtiene un certificado para él. No tiene por qué ser uno de los dominios del sitio.

Si usas JSON, añade estas propiedades al módulo `tls`:

```json
"encrypted_client_hello": {
	"configs": [
		{
			"public_name": "example.com"
		}
	]
},
"dns": {
	"name": "<provider name>",
	// provider configuration
}
```

Estas configuraciones habilitan ECH y publican las configuraciones ECH para todos tus sitios. JSON ofrece más flexibilidad si necesitas personalizar comportamiento o usar configuración avanzada.

### Verificando ECH

Actualmente no hay muchas herramientas para ECH, así que la mejor verificación universal es usar Wireshark y buscar tu public name en el campo ServerName.

Primero inicia el servidor y comprueba que los logs muestren algo como “published ECH configuration list” para tus dominios. Si hay errores de publicación, asegúrate de que el módulo DNS soporte [libdns 1.0](https://github.com/libdns/libdns) y crea un issue en el repositorio del proveedor si hay problemas. Caddy también debería obtener un certificado para el public name.

Después, verifica que tu navegador tenga ECH habilitado; puede requerir DoH/DoT. También conviene vaciar la caché DNS del navegador o sistema para tomar los registros HTTPS recién publicados. Recomendamos cerrar el navegador o abrir una pestaña privada nueva para evitar reutilizar conexiones.

Luego abre Wireshark y escucha en la interfaz correcta. Mientras recolecta paquetes, carga el sitio en tu navegador. Pausa Wireshark y busca el TLS ClientHello: deberías ver el *_public name_* en el campo ServerName, en lugar del dominio real.

Recuerda: puede verse la extensión `encrypted_client_hello` aunque no se esté usando ECH. El indicador clave es el valor SNI. Si ECH funciona, nunca deberías ver el nombre real del sitio en texto plano en Wireshark.

Si surgen problemas de despliegue con ECH, consulta primero en nuestro [forum](https://caddy.community). Si es un bug, puedes [abrir un issue](https://github.com/caddyserver/caddy/issues) en GitHub.

### ECH in storage

Las configuraciones ECH se guardan en el [directorio de datos](/docs/conventions#data-directory), en el módulo de almacenamiento configurado (por defecto, sistema de archivos), dentro de `ech/configs`.

La siguiente carpeta es un ID de configuración ECH, generado aleatoriamente y relativamente irrelevante. La aleatoriedad se recomienda para mitigar huellas o rastreo.

Un archivo sidecar de metadatos permite a Caddy registrar cuándo fueron las últimas publicaciones; esto evita consultar excesivamente al proveedor DNS en cada recarga. Si necesitas reiniciar este estado, puedes borrar ese archivo de metadatos. Sin embargo, también puedes restablecer el momento en que se rotará la clave. También puedes editar el archivo y limpiar solo la información de publicación.
