---
title: Arquitectura
---

Arquitectura
============

Caddy es un binario estático, auto-contenido y sin dependencias externas porque está escrito en Go. Estos principios son partes importantes de la visión del proyecto, ya que simplifican el despliegue y reducen la resolución de problemas tediosa en entornos de produccion.

Si no hay enlace dinámico, ¿como puede extenderse? Caddy tiene una arquitectura de plugins novedosa que amplía su capacidad mucho más allá de cualquier otro servidor web, incluso de los que tienen dependencias externas (enlazadas dinámicamente).

Nuestra filosofía de "menos piezas moviles" termina logrando sitios mas fiables, faciles de administrar y con menor costo — especialmente en escala. Este documento semitecnico describe como logramos ese objetivo mediante ingeniería de software.


## Descripcion general

Caddy se compone de un comando, la biblioteca central y los módulos.

El **comando** proporciona la [interfaz de línea de comandos](/docs/command-line) con la que seguramente estás familiarizado. Es la forma de iniciar el proceso desde tu sistema operativo. La cantidad de código y lógica aquí es bastante mínima, y solo incluye lo necesario para iniciar la base con el modo que el usuario desea. Evitamos intencionalmente usar flags y variables de entorno para configuracion excepto cuando se relacionan con la inicialización.


<aside class="tip">

Los módulos pueden agregar subcomandos a la interfaz de linea de comandos. Por ejemplo, de ahi proviene el comando [`caddy file-server`](/docs/command-line#caddy-file-server). Estos comandos adicionales pueden tener cualquier flag o usar cualquier variable de entorno que deseen, aunque los comandos principales de Caddy minimizan su uso.

</aside>


La **[biblioteca central](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc)**, o "núcleo" de Caddy, gestiona principalmente la configuración. Puede ejecutar [`Run()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Run) sobre una configuración nueva o [`Stop()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Stop) una configuración en ejecucion. También provee varias utilidades, tipos y valores para que los módulos los usen.

Los **módulos** hacen todo lo demas. Muchos módulos vienen incorporados en Caddy, y se llaman *módulos estándar*. Se determinan como los más utiles para más usuarios.


<aside class="tip">

Algunas veces los terminos *modulo*, *plugin* y *extension* se usan de forma intercambiable, y a menudo eso esta bien. Tecnicamente, todos los módulos son plugins, pero no todos los plugins son módulos. Los módulos son especificamente un tipo de plugin que extiende la [estructura de configuración](/docs/json/) de Caddy.

</aside>



## Nucleo de Caddy

En su centro, Caddy simplemente carga una configuración inicial ("config") o, si no hay ninguna, abre un socket para aceptar configuración nueva mas adelante.

Una [configuracion de Caddy](/docs/json/) es un documento JSON, con algunos campos en su nivel superior:

```json
{
	"admin": {},
	"logging": {},
	"apps": {•••},
	...
}
```

El núcleo de Caddy conoce cómo trabajar con algunos de estos campos de forma nativa:

- [`admin`](/docs/json/admin/) para poder configurar la [admin API](/docs/api) y manejar el proceso
- [`logging`](/docs/json/logging/) para que pueda [emitir logs](/docs/logging)

Pero otros campos de nivel superior (como [`apps`](/docs/json/apps/)) son opacos para el núcleo de Caddy. De hecho, todo lo que Caddy sabe hacer con los bytes de `apps` es deserializarlos en un tipo de interfaz en el que puede invocar dos métodos:

1. `Start()`
2. `Stop()`

... y eso es todo. Ejecuta `Start()` en cada app cuando se carga una config, y `Stop()` en cada app cuando se descarga una config.

Cuando se inicia un modulo app, inicia el ciclo de vida del módulo de esa app.


<aside class="tip">

Si eres un programador que está construyendo módulos de Caddy, puedes encontrar información equivalente en nuestra guía de [Extending Caddy](/docs/extending-caddy), pero con mayor enfoque en código.

</aside>


## Ciclo de vida del modulo

Hay dos tipos de módulos: *modulos host* y *modulos guest*.

**Los modulos host** (o "módulos padre") son aquellos que cargan otros módulos.

**Los modulos guest** (o "módulos hijo") son aquellos que se cargan. Todos los módulos son módulos guest, incluso los módulos de app.

Los módulos se cargan, provisionan y validan, se usan y luego se limpian, en esta secuencia:

1. Cargados
2. Provisionados y validados
3. Usados
4. Liberados

Caddy inicia el ciclo de vida de los módulos cuando una config se carga primero inicializando todos los módulos de app configurados. De ahi en adelante, es una cadena de recursividad como "tortugas hasta el fondo" a medida que cada modulo app se encarga del resto.

### Fase de carga

La carga de un módulo implica deserializar sus bytes JSON en un valor tipado en memoria. Eso... es básicamente. Es sólo decodificar JSON en un valor.

### Fase de provisión

Esta fase es donde va la mayor parte del trabajo de configuración. Todos los módulos tienen la oportunidad de provisión tras ser cargados.

Como cualquier propiedad de la codificación JSON ya se habrá decodificado, solo se necesita configuración adicional aquí. La tarea más común durante la provisión es configurar módulos guest. En otras palabras, proveer un módulo host también resulta en la provision de sus módulos guest, hasta el nivel mas profundo.

Puedes tener una idea de esto al [recorrer la estructura JSON de Caddy en nuestra documentación](/docs/json/). En cualquier lugar donde veas `{•••}` se pueden usar módulos guest; y al hacer clic dentro de uno, puedes seguir explorando hasta que no queden más módulos guest.

Otras tareas comunes de provisión son definir valores internos que se usarán durante la vida del módulo o normalizar entradas. Por ejemplo, el módulo [`http.matchers.remote_ip`](/docs/modules/http.matchers.remote_ip) usa la fase de provisioning para analizar valores CIDR a partir de las entradas de texto que recibió del JSON. De esa forma no tiene que hacerlo en cada solicitud HTTP, y resulta más eficiente.

La validación también puede ocurrir en la fase de provisión. Si la configuración resultante de un módulo es inválida, puede devolverse un error que aborta todo el proceso de carga de configuración.

### Fase de uso

Una vez que un módulo guest está provisionado y validado, puede ser usado por su modulo host. Lo que eso significa exactamente depende de cada modulo host.

Cada módulo tiene un ID, que consiste en un namespace y un nombre dentro de ese namespace. Por ejemplo, [`http.handlers.reverse_proxy`](/docs/modules/http.handlers.reverse_proxy) es un handler HTTP porque está en el namespace `http.handlers`, y su nombre es `reverse_proxy`. Todos los módulos en el namespace `http.handlers` satisfacen la misma interfaz, conocida por el modulo host. Así, la app `http` sabe cómo cargar y usar este tipo de módulos.

### Fase de limpieza

Cuando es hora de detener una configuración, todos los módulos se descargan. Si un módulo asigno recursos que deben liberarse, tiene la oportunidad de hacerlo en la fase de limpieza.


## Integracion de modulos

Un módulo — o cualquier plugin de Caddy — se "enchufa" en Caddy agregando un `import` del paquete del módulo. Al importar el paquete, [el módulo se registra a si mismo](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule) con el núcleo de Caddy, para que cuando arranque el proceso de Caddy sepa cada módulo por nombre. Incluso puede asociar valores de módulo con nombres, y viceversa.


<aside class="tip">

Los plugins se pueden agregar sin modificar para nada la base de codigo de Caddy. Hay instrucciones [en el readme](https://github.com/caddyserver/caddy/#with-version-information-andor-plugins) para hacerlo.

</aside>


## Gestion de configuracion

Cambiar la configuración activa de un servidor en ejecución (a menudo llamado "recarga") puede ser complejo con altos niveles de concurrencia y miles de parámetros que requieren los servidores. Caddy resuelve este problema elegantemente con un diseño que tiene muchos beneficios:

- Sin interrupcion del servicio en ejecución
- Posibles cambios de configuración granulares
- Solo un lock requerido (en segundo plano)
- Todas las recargas son atomicas, consistentes, aisladas y mayormente duraderas ("ACID")
- Estado global mínimo

Puedes [ver un video sobre el diseño de Caddy 2 aqui](https://www.youtube.com/watch?v=EhJO8giOqQs).

Una recarga de configuracion funciona provisionando los módulos nuevos y, si todos tienen exito, se limpia los antiguos. Por un breve periodo, dos configuraciones estan operativas al mismo tiempo.

Cada configuración se asocia con un [contexto](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context) que contiene todo el estado de módulos, por lo que la mayoría del estado nunca sale del alcance de una configuración. Esto es una buena noticia para la corrección, el rendimiento y la simplicidad.

Sin embargo, a veces es necesario tener estado verdaderamente global. Por ejemplo, el reverse proxy puede llevar registro de salud de sus upstreams; como solo hay un upstream global de cada uno, seria malo olvidarlos cada vez que se hace un cambio menor de configuración. Afortunadamente, Caddy [proporciona herramientas](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#UsagePool) similares al recolector de basura de un lenguaje para mantener ordenado el estado global.

Un enfoque obvio para actualizar configuraciones en línea es sincronizar acceso a cada único parametro de configuración, incluso en rutas calientes. Esto es terriblemente malo en rendimiento y complejidad —especialmente a escala— por eso Caddy no usa ese enfoque.

En su lugar, las configuraciones se tratan como unidades atómicas e inmutables: o se reemplaza todo, o no cambia nada. Los [endpoint de la API de admin](/docs/api)—que permiten cambios granulares al recorrer la estructura—modifican solo una representación en memoria de la configuración, desde la cual se genera un documento de configuración nuevo y se carga. Este enfoque tiene enormes beneficios en simplicidad, rendimiento y consistencia. Dado que solo hay un lock, es fácil para Caddy procesar recargas rapidas.
