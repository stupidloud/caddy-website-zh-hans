---
title: tls (directiva Caddyfile)
---

<script>
ready(function() {
	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

# tls

Configura TLS para el sitio.

**La configuracion TLS por defecto de Caddy es segura. Cambia esta seccion solo si tienes una razon clara y entiendes las implicaciones.** El uso mas comun de esta directiva es definir el correo de la cuenta ACME, cambiar el endpoint ACME CA o proveer tus propios certificados.

Nota de compatibilidad: debido al contenido sensible de un protocolo de seguridad, en versiones menores o parches se pueden ajustar los valores por defecto de TLS. Versiones antiguas o cifrados, funcionalidades, etc. pueden eliminarse en cualquier momento. Si tu despliegue es muy sensible a cambios, especifica explicitamente los valores que deben permanecer estables y mantente atento a las actualizaciones. En casi todos los casos recomendamos usar la configuracion por defecto.


## Syntax

```caddy-d
tls [internal|force_automate|<email>] | [<cert_file> <key_file>] {
	protocols <min> [<max>]
	ciphers   <cipher_suites...>
	curves    <groups...>
	alpn      <values...>
	load      <paths...>
	ca        <ca_dir_url>
	ca_root   <pem_file>
	key_type  ed25519|p256|p384|rsa2048|rsa4096
	dns       <provider_name> [<params...>]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	eab       <key_id> <mac_key>
	on_demand
	reuse_private_keys
	client_auth {
		mode                   [request|require|verify_if_given|require_and_verify]
		trust_pool             <module>
		verifier 			   <module>
	}
	issuer          <issuer_name>  [<params...>]
	get_certificate <manager_name> [<params...>]
	insecure_secrets_log <log_file>
	renewal_window_ratio <ratio>
	force_automate
}
```

- **internal** significa usar la CA interna de confianza local de Caddy para generar certificados para este sitio. Para configurar mas al detalle el emisor `internal` usa la subdirectiva [`issuer`](#issuer).

- **force_automate** obliga a Caddy a automatizar certificados para el sitio, aunque existan otros certificados administrados.

- **&lt;email&gt;** es la direccion de correo para la cuenta ACME que maneja los certificados del sitio. Es posible que prefieras usar la [`opcion global email`](/docs/caddyfile/options#email) en su lugar para configurarlo en todos tus sitios a la vez.

<aside class="tip">

Ten en cuenta que Let's Encrypt puede enviarte correos sobre vencimiento proximo del certificado, pero eso puede inducir error si Caddy eligio usar otro emisor (por ejemplo ZeroSSL) al renovar. Revisa tus logs y/o el propio certificado (por ejemplo en el navegador) para ver que emisor se usó y si su fecha de vencimiento sigue siendo valida; si es asi, puedes ignorar con seguridad ese correo de Let's Encrypt.

</aside>

- **&lt;cert_file&gt;** y **&lt;key_file&gt;** son las rutas a los archivos PEM de certificado y clave privada. Es invalido especificar solo uno.

- **protocols** <span id="protocols"/> define los valores minimo y maximo de protocolo. NO CAMBIES esto si no sabes exactamente lo que haces. Esta configuracion casi nunca es necesaria porque Caddy siempre usa valores modernos por defecto.
  
  Minimo por defecto: `tls1.2`, maximo por defecto: `tls1.3`

- **ciphers** <span id="ciphers"/> especifica la lista de suites de cifrado en orden de preferencia descendente. NO CAMBIES esto si no sabes lo que haces. Ten en cuenta que las suites de cifrado de TLS 1.3 no son personalizables; y no todos los cifrados TLS 1.2 vienen habilitados por defecto. Los nombres admitidos son (en orden de preferencia de la stdlib de Go):
	- `TLS_AES_128_GCM_SHA256`
	- `TLS_CHACHA20_POLY1305_SHA256`
	- `TLS_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA`

- **curves** <span id="curves"/> indica la lista de grupos EC que se aceptan. Se recomienda no cambiar valores por defecto. Valores admitidos:
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> es la lista de valores para anunciar en la [extension ALPN <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Glossary/ALPN) durante el handshake TLS.

- **load** <span id="load"/> especifica carpetas desde las cuales cargar archivos PEM con pares certificado+clave.

- **ca** <span id="ca"/> cambia el endpoint ACME CA. Usualmente se usa para establecer el [endpoint de pruebas de Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) o un servidor ACME interno. Para cambiar este valor globalmente en todo el Caddyfile usa la [opcion global `acme_ca`](/docs/caddyfile/options) en su lugar.

- **ca_root** <span id="ca_root"/> indica un archivo PEM que contiene un certificado raiz de confianza del endpoint ACME CA si no esta en el store de confianza del sistema.

- **key_type** <span id="key_type"/> es el tipo de clave al generar CSR. Solo cambia esto si tienes una necesidad especifica.

- **dns** <span id="dns"/> habilita el [reto DNS](/docs/automatic-https#dns-challenge) con el plugin indicado, que debe estar incorporado desde uno de los repositorios [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Cada plugin puede tener su propia sintaxis despues del nombre; consulta su documentacion. El soporte para cada proveedor DNS lo mantiene la comunidad. [Aprende a habilitar el reto DNS para tu proveedor en nuestro wiki.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> es un [valor de duracion](/docs/conventions#durations) que define el maximo tiempo de espera para que aparezcan los registros DNS TXT al usar el reto DNS. Usa `-1` para desactivar las comprobaciones de propagacion. Por defecto 2 minutos.

- **propagation_delay** <span id="propagation_delay"/> es un [valor de duracion](/docs/conventions#durations) que define cuanto esperar antes de empezar a comprobar propagacion de registros DNS TXT al usar el reto DNS. Por defecto `0` (sin espera).

- **dns_ttl** <span id="dns_ttl"/> es un [valor de duracion](/docs/conventions#durations) para el TTL del registro `TXT` usado en el reto DNS. Raramente necesario.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> reemplaza el dominio usado para el reto DNS. Sirve para delegar el reto a otro dominio.

  Puedes usarlo si el proveedor DNS de tu dominio principal no tiene un [plugin DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Puedes agregar un registro `CNAME` con subdominio `_acme-challenge` al dominio principal, apuntando a un dominio secundario para el cual SI tienes plugin. Esta opcion _no_ requiere soporte especial del plugin.
  
  Cuando los emisores ACME intenten resolver el reto DNS del dominio principal, seguiran ese `CNAME` hacia el dominio secundario para encontrar el registro `TXT`.

  **Nota:** Usa el nombre canónico completo del registro CNAME como valor -- el subdominio `_acme-challenge` no se antepone automaticamente.

- **resolvers** <span id="resolvers"/> personaliza los resolvers DNS usados al realizar el reto DNS; tienen precedencia sobre resolvers del sistema y cualquier valor por defecto. Si se define aqui, propagaran a todos los emisores de certificados configurados.

  Tipeicamente se usa una lista de direcciones IP. Por ejemplo, para usar [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns):

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> configura ACME external account binding (EAB) para este sitio, usando `key_id` y `mac_key` del CA.

- **on_demand** <span id="on_demand"/> habilita [TLS bajo demanda](/docs/automatic-https#on-demand-tls) para los hostnames indicados en la direccion del bloque site. **Advertencia de seguridad:** usarlo en produccion es inseguro salvo que tambien configures la [opcion global `on_demand_tls`](/docs/caddyfile/options#on-demand-tls) para mitigar abuso.

- **reuse_private_keys** <span id="reuse_private_keys"/> permite reutilizar la clave privada al renovar certificados. Por defecto se crea una clave nueva por cada certificado para reducir pinning y limitar impacto si hay compromiso de clave. El pinning es contra buenas practicas. No se recomienda esta opcion salvo necesidad; puede desaparecer en una version futura.

- **client_auth** <span id="client_auth"/> habilita y configura la autenticacion de cliente TLS:
  - **mode** <span id="mode"/> es el modo de autenticacion del cliente. Valores permitidos:

    | Modo | Descripcion |
    | --- | --- |
    | request | Solicita al cliente un certificado, pero permite ausencia y no lo verifica |
    | require | Requiere certificado de cliente, pero no lo verifica |
    | verify_if_given | Solicita certificado; permite ausencia, pero lo verifica si existe |
    | require_and_verify | Exige un certificado valido que sea verificado |

    Default: `require_and_verify` si se provee modulo `trust_pool`; de lo contrario, `require`.
	
  - **trust_pool** <span id="trust_pool"/> configura la fuente de CAs que emitieron los certificados contra los que validar client certificates.
	
	La autoridad de certificacion usada, el pool de certificados confiables y la configuracion del segmento dependen de la fuente de modulo trust pool configurada. Los modulos estandar incluidos se listan abajo en [Trust Pool Providers](#trust-pool-providers). La lista completa de modulos, incluyendo de terceros, aparece en la documentacion JSON [`trust_pool`](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool).

    Puedes usar varios `trusted_*` para definir multiples CA o certificados hoja. Los certificados de cliente que no esten en la lista de leaf o firmados por ninguna de las CA especificadas seran rechazados segun **mode**.

  - **verifier** <span id="verifier"/> habilita un modulo verificador personalizado de certificados cliente. Puede implementar chequeos personalizados, por ejemplo validar que el certificado no este revocado.

- **issuer** <span id="issuer"/> configura un emisor de certificados personalizado, o una fuente de la que obtenerlos.

  El emisor usado y sus opciones dependen de los [issuer modules](#issuers) disponibles. Algunos subcomandos como `ca` o `dns` son atajos para configurar `acme` (y esta subdirectiva se agrego despues), por lo que combinarlos con `issuer` produce confusiones y esta prohibido.
  
  Esta subdirectiva puede repetirse para definir emisores redundantes; si uno falla en emitir, se intenta el siguiente.

- **get_certificate** <span id="get_certificate"/> habilita obtener certificados desde un [manager module](#certificate-managers) en el momento del handshake.

- **insecure_secrets_log** <span id="insecure_secrets_log"/> habilita log de secretos TLS a archivo, tambien llamado `SSLKEYLOGFILE`. Usa formato NSS key log, que puede ser analizado por Wireshark u otras herramientas. ⚠️ **Advertencia de seguridad:** esto es inseguro porque permite que otros programas o herramientas descifren conexiones TLS, por lo que compromete completamente la seguridad. Aun asi puede ser util para depuracion.

- **renewal_window_ratio** <span id="renewal_window_ratio"/> es una ratio entre 0 y 1 que indica el tiempo de vida del certificado que debe quedar para que Caddy intente renovarlo. Por ejemplo, si el certificado dura 90 dias y esta ratio `0.3333` (valor por defecto), Caddy intentara renovar continuamente cuando queden 30 dias o menos. Tambien puede configurarse globalmente con la [opcion global `renewal_window_ratio`](/docs/caddyfile/options#renewal_window_ratio).

  Rara vez debes cambiar esto, pero puede ayudar a renovar mas tarde en el ciclo de vida si tu CA tarda mucho en emitir.

  Recuerda que es solo una sugerencia, porque emisores ACME pueden implementar la [extension ARI](https://datatracker.ietf.org/doc/rfc9773/), donde el cliente ACME (Caddy en este caso) debe intentar renovar dentro de una ventana indicada por el emisor que puede no coincidir con esta ratio.

- **force_automate** equivale a escribir inline (ver arriba).

### Trust Pool Providers

Estos son los proveedores de trust pool estandar que se pueden usar en la subdirectiva `trust_pool`:

#### inline

El modulo `inline` analiza certificados raices confiables listados en el Caddyfile directamente en formato base64 DER. La directiva `trust_der` puede repetirse.

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> es un certificado CA en base64 DER contra el que validar certificados cliente.

#### file

El modulo `file` lee certificados raices confiables desde archivos PEM en disco. La directiva `pem_file` acepta varias rutas en la misma linea y puede repetirse.

```caddy-d
... file [<pem_file>...] {
	pem_file <pem_file>...
}
```

- **pem_file** <span id="pem_file"/> es una ruta a un certificado CA PEM contra el que validar certificados cliente.

#### pki_root

El modulo `pki_root` obtiene y confia en certificados de la [app PKI](/docs/caddyfile/options#pki-options). La directiva `authority` acepta multiples autoridades y puede repetirse.

```caddy-d
... pki_root [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> es el nombre de la autoridad de certificacion configurada en la app PKI.

#### pki_intermediate

El modulo `pki_intermediate` obtiene y confia en certificados _intermedios_ de la [app PKI](/docs/caddyfile/options#pki-options). La directiva `authority` acepta varias autoridades y puede repetirse.

```caddy-d
... pki_intermediate [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> es el nombre de la autoridad de certificacion configurada en la app PKI.

#### storage

El modulo `storage` obtiene certificados confiables raiz desde el [storage de Caddy](/docs/caddyfile/options#storage). `authority` acepta multiples llaves y puede repetirse.

```caddy-d
... storage [<storage_keys>...] {
	storage <storage_module>
	keys    <storage_keys>...
}
```

- **storage** <span id="storage"/> es un modulo de storage opcional. Si no se define, se usa el por defecto. Si se define, solo puede aparecer una vez.

- **keys** <span id="keys"/> es la lista de claves de storage donde se guardan los archivos PEM de certificados. Puede tener multiples valores en la misma linea y repetirse.

#### http

El modulo `http` obtiene certificados confiables desde endpoints HTTP. La directiva `endpoints` acepta multiples endpoints y puede repetirse.

```caddy-d
... http [<endpoints...>] {
	endpoints   <endpoints...>
	tls         <tls_config>
}
```

- **endpoints** <span id="endpoints"/> es la lista de endpoints HTTP para obtener certificados. Acepta multiples valores y puede repetirse.

- **tls** <span id="tls"/> es una configuracion TLS opcional para conectarse al endpoint HTTP. El analisis del segmento se define en [seccion siguiente](#tls-1).

##### TLS

```caddy-d
... {
	ca                    <ca_module>
	insecure_skip_verify
	handshake_timeout     <duration>
	server_name           <name>
	renegotiation         <never|once|freely>
}
```

- **ca** <span id="ca"/> es una directiva opcional para definir la fuente de confianza del trust pool. La configuracion sigue el comportamiento de [`trust_pool`](#trust_pool). Si se indica, solo puede definirse una vez.

- **insecure_skip_verify** <span id="insecure_skip_verify"/> desactiva la verificacion del handshake TLS, haciendo la conexion vulnerable a ataques man-in-the-middle. _No uses en produccion._ La verificacion se hace sobre CAs confiables del sistema o las definidas por [`ca`](#ca).

- **handshake_timeout** <span id="handshake_timeout"/> es la maxima [duracion](/docs/conventions#durations) para completar el handshake TLS. Default: Sin limite.

- **server_name** <span id="server_name"/> define el SNI usado al verificar el certificado recibido en el handshake TLS. Por defecto usa el host de la direccion upstream.

- **renegotiation** <span id="renegotiation"/> ajusta el nivel de renegociacion TLS. Puede ser:
  - `never` (valor por defecto) desactiva renegociacion.
  - `once` permite una peticion de renegociacion por conexion.
  - `freely` permite peticiones repetidas de renegociacion.

### Verifiers

Los modulos verificador de certificado cliente se ejecutan despues de validar que la CA emisora pertenece a un trust pool configurado. En el Caddy estandar, actualmente solo esta disponible `leaf`.

#### Leaf

El verificador `leaf` valida que el certificado cliente pertenezca a un conjunto de certificados permitidos. El conjunto se carga desde modulos [loader](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders).

##### Loaders

La distribucion estandar de Caddy incluye 4 loaders, 3 disponibles en Caddyfile.

###### File

El loader `file` carga las listas desde archivos PEM especificados.

```caddy-d
... file <pem_files...>
```

###### Folder

El loader `folder` recorre recursivamente directorios para buscar PEM a cargar como certificados cliente aceptados.

```caddy-d
... folder <folders...>
```

###### PEM

El loader `pem` acepta certificados inline en Caddyfile en formato PEM.

```caddy-d
... pem <pem_strings...>
```

### Issuers

Estos emisores vienen incluidos en la directiva `tls`:

#### acme

Obtiene certificados con protocolo ACME. Nota que `acme` es emisor por defecto (Let's Encrypt), por lo que normalmente no hace falta configurar explicitamente.

```caddy-d
... acme [<directory_url>] {
	dir      <directory_url>
	test_dir <test_directory_url>
	email    <email>
	timeout  <duration>
	disable_http_challenge
	disable_tlsalpn_challenge
	alt_http_port    <port>
	alt_tlsalpn_port <port>
	eab <key_id> <mac_key>
	trusted_roots <pem_files...>
	dns [<provider_name> [<options>]]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}
	profile <name>
}
```

- **dir** <span id="dir"/> es la URL del directorio de la CA ACME.
  
  Default: `https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> es un directorio opcional alternativo cuando hay reintentos de desafios; si fallan todos, se usa este endpoint. Es util si tu CA tiene endpoint de staging y quieres evitar limites en produccion.

  Default: `https://acme-staging-v02.api.letsencrypt.org/directory`

- **email** <span id="email"/> es el correo de contacto ACME.

- **timeout** <span id="timeout"/> es una [duracion](/docs/conventions#durations) de espera maxima para operaciones ACME.

- **disable_http_challenge** <span id="disable_http_challenge"/> desactiva el reto HTTP.

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> desactiva el reto TLS-ALPN.

- **alt_http_port** <span id="alt_http_port"/> es un puerto alternativo para servir desafio HTTP; debe ser 80 y reenviar paquetes al puerto elegido.

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> puerto alternativo para servir TLS-ALPN challenge; debe ser 443.

- **eab** <span id="eab"/> configura External Account Binding, requerido por algunos ACME CAs.

- **trusted_roots** <span id="trusted_roots"/> una o mas rutas PEM de certificados raiz para confiar al conectar al servidor ACME CA.

- **dns** <span id="dns"/> configura el reto DNS. Debes configurar un proveedor aqui a menos que la [opcion global `dns`](/docs/caddyfile/options#dns) defina uno globalmente.

- **propagation_timeout** <span id="propagation_timeout"/> es un [valor de duracion](/docs/conventions#durations) maximo de espera para que aparezcan registros DNS TXT al usar reto DNS. Usa `-1` para desactivar comprobaciones de propagacion. Por defecto 2 minutos.

- **propagation_delay** <span id="propagation_delay"/> es un [valor de duracion](/docs/conventions#durations) que indica cuanto esperar antes de empezar a verificar propagacion de registros DNS TXT al usar reto DNS. Valor por defecto 0 (sin espera).

- **dns_ttl** <span id="dns_ttl"/> es un [valor de duracion](/docs/conventions#durations) para TTL de registro `TXT` usado en reto DNS. Raramente necesario.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> reemplaza dominio a usar para reto DNS, para delegar al dominio alternativo.

  Puedes usarlo cuando el proveedor DNS del dominio principal no tenga un [plugin DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Puedes crear un registro `CNAME` con subdominio `_acme-challenge` apuntando a un dominio secundario que si soporte el plugin. Esta opcion _no_ requiere soporte especial.
  
  Cuando ACME intente resolver el reto DNS del dominio principal, seguira el `CNAME` al secundario para encontrar `TXT`.

  **Nota:** Usa el nombre canónico completo como valor; el subdominio `_acme-challenge` no se agrega automaticamente.

- **resolvers** <span id="resolvers"/> personaliza resolvers DNS para el reto DNS; tienen precedencia sobre resolvers del sistema y por defecto. Si se define aca, propagaran a todos los emisores configurados.

  Normalmente es una lista de IPs. Por ejemplo, para [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns):

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> define que cadenas debe preferir Caddy. Opciones:
	- **smallest** <span id="smallest"/> prefiere cadenas con menos bytes.
	- **root_common_name** <span id="root_common_name"/> lista de CN; Caddy elige la primera cadena cuyo root coincida al menos con uno.
	- **any_common_name** <span id="any_common_name"/> lista de CN; Caddy elige primer emisor con alguna coincidencia.

- **profile** nombre del [perfil ACME](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/) usado al solicitar certificados. Si especificas uno, todas las CAs implicitas deben soportarlo. Consulta docs de tu CA; puede no haber soporte. EXPERIMENTAL: La especificacion ACME profile esta en draft, por lo que puede cambiar o eliminarse.


#### zerossl

Obtiene certificados usando la [API propietaria de ZeroSSL](https://zerossl.com/documentation/api/). Se requiere API key y puede requerir pago segun plan. Nota que esto es distinto a usar endpoint ACME de ZeroSSL. Para usar ACME de ZeroSSL, usa emisor `acme` con su directorio ACME.

```caddy-d
... zerossl <api_key> {
	validity_days <days>
	alt_http_port <port>
	dns <provider_name> ...
	propagation_delay <duration>
	propagation_timeout <duration>
	resolvers <list...>
	dns_ttl <duration>
}
```

- **validity_days** <span id="validity_days"/> define la duracion del certificado. Solo acepta ciertos valores; revisa docs de ZeroSSL.
<!--   
  Default: `https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> puerto para validacion HTTP de ZeroSSL si no es 80.
- **dns** <span id="zerossl_dns"/> activa validacion CNAME usando proveedor DNS con configuracion dada para aprovisionar registros automaticos.
- **propagation_delay** <span id="zerossl_propagation_delay"/> tiempo de espera antes de revisar propagacion de registro CNAME.
- **propagation_timeout** <span id="zerossl_propagation_timeout"/> tiempo maximo de espera de propagacion CNAME.
- **resolvers** <span id="zerossl_resolvers"/> resolvers DNS personalizados para validar propagacion CNAME.
- **dns_ttl** <span id="zerossl_dns_ttl"/> TTL de registros CNAME creados durante validacion.



#### internal

Obtiene certificados de una autoridad de certificacion interna.

```caddy-d
... internal {
	ca       <name>
	lifetime <duration>
	sign_with_root
}
```

- **ca** <span id="ca"/> nombre de la CA interna a usar. Default: `local`. Mira [opciones globales de PKI](/docs/caddyfile/options#pki-options) para configurar `local` o crear CAs alternas.

  Por defecto la certificacion raiz dura `3600d` (10 años) y el intermedio `7d` (7 dias).

  Caddy intenta instalar el certificado raiz en el sistema de confianza, pero puede fallar si se ejecuta sin privilegios o en Docker. En ese caso debes instalarlo manualmente con [`caddy trust`](/docs/command-line#caddy-trust) o [sacandolo del contenedor](/docs/running#usage).

- **lifetime** <span id="lifetime"/> es una [duracion](/docs/conventions#durations) de validez para certificados leaf emitidos internamente. Default: `12h`. No se recomienda cambiarlo salvo necesidad. Debe ser menor que la duracion del cert intermediate.

- **sign_with_root** <span id="sign_with_root"/> fuerza al root como emisor en lugar del intermediate. No se recomienda y solo deberia usarse cuando dispositivos/clientes no validan cadenas correctamente (situacion poco comun).



### Certificate Managers

Los modulos manager de certificados se distinguen de los issuers: usar manager significa que una herramienta o servicio externo mantiene la renovacion, mientras que un issuer significa que Caddy gestiona el certificado. (Los issuers usan CSR como entrada, los manager reciben TLS ClientHello.)

Estos managers vienen con la directiva `tls`:

#### tailscale

Obtiene certificados desde una instancia de [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) ejecutandose localmente. [HTTPS debe estar activo en tu cuenta Tailscale](https://tailscale.com/kb/1153/enabling-https/) (o en tu [Headscale open source <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/juanfont/headscale)); y el proceso Caddy debe ejecutarse como root, o configurar `tailscaled` para dar permiso a tu usuario para obtener certificados (ver [PR 4541](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348)).

_**NOTA: Esto suele no ser necesario!** Caddy usa Tailscale automaticamente para todos dominios `*.ts.net` sin configuracion adicional._

```caddy-d
get_certificate tailscale  # muchas veces innecesario!
```


#### http

Obtiene certificados haciendo una peticion HTTP(S). La respuesta debe tener codigo `200` y el cuerpo debe contener cadena PEM con certificacion completa (incluyendo intermediados) y clave privada.

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> URL completa a la que consultar. Se recomienda que sea local por rendimiento. La URL se agrega con query string:

  - `server_name`: valor de SNI
  - `signature_schemes`: lista separada por comas de ids hex de algoritmos de firma
  - `cipher_suites`: lista separada por comas de ids hex de cipher suites
  - `local_ip`: IP de destino de la peticion



## Examples

Usa certificado y clave personalizada. El certificado debe tener [SANs](https://en.wikipedia.org/wiki/Subject_Alternative_Name) que coincidan con la direccion del sitio:

```caddy
example.com {
	tls cert.pem key.pem
}
```

Usa certificados [de confianza local](/docs/automatic-https#local-https) para todos los host del bloque de sitio actual, en vez de certificados publicos ACME / Let's Encrypt (util para entornos de desarrollo):

```caddy
example.com {
	tls internal
}
```

Usa certificados locales con [On-Demand](/docs/automatic-https#on-demand-tls) en vez de en segundo plano. Esto permite apuntar cualquier dominio a tu instancia de Caddy y que emita automaticamente un certificado. Esto NO DEBE usarse si la instancia de Caddy es publica, porque un atacante podria agotar recursos:

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

Usa opciones personalizadas para la CA interna (no se puede usar el shortcut `tls internal`):

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

Especifica email de cuenta ACME (pero si usas un solo email para todos sitios, recomendamos la [opcion global `email`](/docs/caddyfile/options) mejor):

```caddy
example.com {
	tls your@email.com
}
```

Habilita reto DNS para dominio gestionado en Cloudflare con token de entorno. Esto habilita wildcard y requiere validacion DNS:

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

Obtiene la cadena de certificados por HTTP en lugar de que Caddy la gestione. Nota que [`get_certificate`](#certificate-managers) implica [`on_demand`](#on_demand), obteniendo certificados via modulo en lugar de emitir ACME:

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

Habilita TLS Client Authentication y exige certificados validos verificados contra todas las CA definidas via proveedor [`trust_pool`](#trust_pool) `file`:

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
