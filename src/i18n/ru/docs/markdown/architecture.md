---
title: Архитектура
---

Архитектура
============

Caddy — единый, самодостаточный, статический binary без внешних зависимостей, потому что он написан на Go. Эти свойства являются важной частью vision проекта: они упрощают deployment и уменьшают утомительное troubleshooting в production environments.

Если dynamic linking нет, как его расширять? У Caddy новая plugin architecture, которая расширяет его возможности далеко за пределы любого другого web server, даже серверов с внешними (dynamically-linked) зависимостями.

Наша философия "меньше движущихся частей" в итоге дает более надежные, более управляемые и менее дорогие sites&mdash;особенно в масштабе. Этот полутехнический документ описывает, как мы достигаем этой цели через software engineering.


<a id="overview"></a>
## Обзор

Caddy состоит из command, core library и modules.

**Command** предоставляет [command line interface](/docs/command-line), с которым вы, надеемся, знакомы. Так вы запускаете process из operating system. Объем code и logic здесь довольно мал: только то, что нужно для bootstrap core тем способом, который нужен пользователю. Мы намеренно избегаем flags и environment variables для конфигурации, кроме случаев, где они относятся к bootstrapping config.


<aside class="tip">

Modules могут добавлять subcommands в command line interface! Например, именно оттуда появляется команда [`caddy file-server`](/docs/command-line#caddy-file-server). Эти добавленные commands могут иметь любые flags или использовать любые environment variables, даже если core-команды Caddy минимизируют их применение.

</aside>


**[Core library](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc)**, или "core" Caddy, в основном управляет конфигурацией. Она может [`Run()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Run) новую конфигурацию или [`Stop()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Stop) работающую config. Она также предоставляет различные utilities, types и values для modules.

**Modules** делают все остальное. Многие modules встроены в Caddy; они называются *standard modules*. Они выбраны как наиболее полезные для большинства пользователей.


<aside class="tip">

Иногда термины *module*, *plugin* и *extension* используются взаимозаменяемо, и обычно это нормально. Технически все modules являются plugins, но не все plugins являются modules. Modules — это конкретный вид plugin, который расширяет [структуру config](/docs/json/) Caddy.

</aside>




<a id="caddy-core"></a>
## Core Caddy

В своей основе Caddy лишь загружает initial configuration ("config") или, если ее нет, открывает socket, чтобы позже принять новую configuration.

[Конфигурация Caddy](/docs/json/) — это JSON document с несколькими fields на верхнем уровне:

```json
{
	"admin": {},
	"logging": {},
	"apps": {•••},
	...
}
```

Core Caddy умеет нативно работать с некоторыми из этих fields: 

- [`admin`](/docs/json/admin/), чтобы настроить [admin API](/docs/api) и управлять process
- [`logging`](/docs/json/logging/), чтобы [emit logs](/docs/logging)

Но другие top-level fields (например, [`apps`](/docs/json/apps/)) непрозрачны для core Caddy. Фактически все, что Caddy умеет делать с bytes в `apps`, — deserialize их в interface type, у которого можно вызвать два methods:

1. `Start()`
2. `Stop()`

... и это все. Он вызывает `Start()` для каждого app при загрузке config и `Stop()` для каждого app при выгрузке config.

Когда app module запускается, он инициирует module lifecycle этого app.


<aside class="tip">

Если вы programmer, который создает Caddy modules, аналогичную информацию можно найти в нашем guide [Extending Caddy](/docs/extending-caddy), но с большим фокусом на code.

</aside>


<a id="module-lifecycle"></a>
## Lifecycle module

Есть два вида modules: *host modules* и *guest modules*.

**Host modules** (или "parent" modules) — это modules, которые загружают другие modules.

**Guest modules** (или "child" modules) — это modules, которые загружаются. Все modules являются guest modules -- даже app modules.

Modules загружаются, provision и validate, используются, затем очищаются в такой последовательности:

1. Loaded
2. Provisioned and validated
3. Used
4. Cleaned up

Caddy запускает module lifecycle при загрузке config, сначала инициализируя все настроенные app modules. Оттуда все идет "turtles all the way down": каждый app module продолжает процесс дальше.

<a id="load-phase"></a>
### Фаза load

Загрузка module включает deserializing его JSON bytes в typed value в памяти. Это... в общем-то все. Это просто decoding JSON в value.

<a id="provision-phase"></a>
### Фаза provision

В этой фазе выполняется большая часть setup work. Все modules получают возможность provision themselves после загрузки.

Поскольку все properties из JSON encoding уже decoded, здесь требуется только дополнительный setup. Самая распространенная задача во время provisioning — настройка guest modules. Иными словами, provisioning host module также приводит к provisioning его guest modules, на всю глубину.

Это можно почувствовать, [проходя по JSON structure Caddy в нашей документации](/docs/json/). Везде, где вы видите `{•••}`, могут использоваться guest modules; переходя внутрь, можно продолжать исследовать ниже, пока guest modules больше не останется.

Другие распространенные provisioning tasks — настройка внутренних values, которые будут использоваться в течение lifetime module, или стандартизация inputs. Например, module [`http.matchers.remote_ip`](/docs/modules/http.matchers.remote_ip) использует provision phase, чтобы разобрать CIDR values из string inputs, полученных из JSON. Благодаря этому ему не нужно делать это при каждом HTTP request, и он работает эффективнее.

Validation также может выполняться в provision phase. Если итоговая config module невалидна, здесь можно вернуть error, который прервет весь процесс загрузки config.

<a id="use-phase"></a>
### Фаза use

После provisioning и validation guest module может использоваться своим host module. Что именно это означает, зависит от каждого host module.

У каждого module есть ID, состоящий из namespace и name в этом namespace. Например, [`http.handlers.reverse_proxy`](/docs/modules/http.handlers.reverse_proxy) — это HTTP handler, потому что он находится в namespace `http.handlers`, а его name — `reverse_proxy`. Все modules в namespace `http.handlers` реализуют один и тот же interface, известный host module. Поэтому app `http` знает, как загружать и использовать такие modules.

<a id="cleanup-phase"></a>
### Фаза cleanup

Когда пора остановить config, все modules выгружаются. Если module выделял какие-либо resources, которые нужно освободить, он получает возможность сделать это в cleanup phase.


<a id="plugging-in"></a>
## Подключение

Module -- или любой Caddy plugin -- "подключается" к Caddy добавлением `import` для package module. При import package [module регистрирует себя](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule) в core Caddy, поэтому при запуске process Caddy знает каждый module по имени. Он даже может связывать values module с names и наоборот.


<aside class="tip">

Plugins можно добавить вообще без изменения code base Caddy. Инструкции для этого есть [в readme](https://github.com/caddyserver/caddy/#with-version-information-andor-plugins)!

</aside>


<a id="managing-configuration"></a>
## Управление конфигурацией

Изменение active configuration работающего server (часто называемое "reload") может быть сложным из-за высокого уровня concurrency и тысяч параметров, которые нужны servers. Caddy решает эту проблему элегантно, используя design с множеством преимуществ:

- Нет прерывания работающих services
- Возможны granular config changes
- Требуется только один lock (в фоне)
- Все reloads atomic, consistent, isolated и mostly durable ("ACID")
- Минимальное global state

Можно [посмотреть видео о design Caddy 2 здесь](https://www.youtube.com/watch?v=EhJO8giOqQs).

Config reload работает так: новые modules проходят provisioning, и если все успешно, старые очищаются. Короткое время две configs работают одновременно.

Каждая configuration связана с [context](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context), который хранит все module state, поэтому большая часть state никогда не выходит за область config. Это хорошо для correctness, performance и simplicity!

Однако иногда truly global state необходимо. Например, reverse proxy может отслеживать health своих upstreams; поскольку каждый upstream глобально существует в одном экземпляре, было бы плохо, если бы он забывал о них при каждом небольшом config change. К счастью, Caddy [предоставляет facilities](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#UsagePool), похожие на garbage collector language runtime, чтобы держать global state в порядке.

Один очевидный подход к online config updates — синхронизировать доступ к каждому отдельному config parameter, даже в hot paths. Это крайне плохо с точки зрения performance и complexity&mdash;особенно в масштабе&mdash;поэтому Caddy не использует такой подход.

Вместо этого configs рассматриваются как immutable, atomic units: либо заменяется все целиком, либо ничего не меняется. [Admin API endpoints](/docs/api)&mdash;которые позволяют granular changes через обход structure&mdash;изменяют только in-memory representation config, из которого генерируется и загружается целый новый config document. Этот подход дает большие преимущества в simplicity, performance и consistency. Поскольку есть только один lock, Caddy легко обрабатывает быстрые reloads.
