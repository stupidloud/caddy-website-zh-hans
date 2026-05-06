---
title: "Поддержка Caddyfile"
---

<a id="caddyfile-support"></a>
# Поддержка Caddyfile

Caddy modules автоматически добавляются в [native JSON config](/docs/json/) благодаря своему namespace при [регистрации](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule), что делает их и usable, и documented. Поэтому поддержка Caddyfile полностью optional, но ее часто просят пользователи, предпочитающие Caddyfile.

<a id="unmarshaler"></a>
## Unmarshaler

Чтобы добавить поддержку Caddyfile для своего module, просто реализуйте interface [`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler). Синтаксис Caddyfile для вашего module определяется тем, как вы парсите tokens.

Задача unmarshaler — настроить type вашего module, например заполнить его fields, используя переданный [`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser). Например, type module с именем `Gizmo` может иметь такой method:

```go
// UnmarshalCaddyfile implements caddyfile.Unmarshaler. Syntax:
//
// gizmo <name> [<option>]
//
func (g *Gizmo) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // consume directive name

	if !d.Args(&g.Name) {
		// not enough args
		return d.ArgErr()
	}
	if d.NextArg() {
		// optional arg
		g.Option = d.Val()
	}
	if d.NextArg() {
		// too many args
		return d.ArgErr()
	}

	return nil
}
```

Хорошая идея — документировать syntax в godoc comment для method. Подробнее о parsing Caddyfile см. [godoc для package `caddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc).

Token с именем директивы можно consume/skip простым вызовом `d.Next()`.

Обязательно проверяйте missing и/или excess arguments с помощью `d.NextArg()` или `d.RemainingArgs()`. Используйте `d.ArgErr()` для простого сообщения "invalid case" или `d.Errf("some message")`, чтобы создать полезное error message с объяснением проблемы (и, желательно, предлагаемым solution).

Также нужно добавить [interface guard](/docs/extending-caddy#interface-guards), чтобы убедиться, что interface реализован правильно:

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

<a id="blocks"></a>
### Blocks

Чтобы принять больше configuration, чем помещается в одну строку, можно разрешить block с subdirectives. Это можно сделать с помощью `d.NextBlock()` и итерации до возврата на исходный nesting level:

```go
for nesting := d.Nesting(); d.NextBlock(nesting); {
	switch d.Val() {
		case "sub_directive_1":
		// ...
		case "sub_directive_2":
		// ...
	}
}
```

Если каждая итерация loop consume весь segment (line или block), это elegant way для обработки blocks.

<a id="http-directives"></a>
## HTTP Directives

HTTP Caddyfile — default syntax Caddyfile adapter в Caddy (или "server type"). Он extensible, то есть можно [зарегистрировать](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterDirective) собственные "top-level" directives для module:

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

Если ваша директива возвращает только один HTTP handler (как часто бывает), [`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective) может быть проще:

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

Основная идея в том, что [parsing function](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc), связанная с вашей директивой, возвращает одно или несколько значений [`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue). (Или, при использовании `RegisterHandlerDirective`, она просто напрямую возвращает заполненное значение `caddyhttp.MiddlewareHandler`.) Каждое config value связано с ["class"](#classes), который помогает HTTP Caddyfile adapter понять, в каких part(s) итоговой JSON config его можно использовать. Все config values складываются в общую pile, из которой adapter берет данные при построении итоговой JSON config.

Этот design позволяет вашей директиве возвращать любые config values для любых распознанных classes, то есть она может влиять на любые parts config, для которых HTTP Caddyfile adapter имеет designated class.

Если вы уже реализовали method `UnmarshalCaddyfile()`, parse function может быть такой простой:

```go
// parseCaddyfileHandler unmarshals tokens from h into a new middleware handler value.
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

Подробнее об использовании type `httpcaddyfile.Helper` см. [`httpcaddyfile` package godoc](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc).

<a id="handler-order"></a>
### Handler order

Все directives, которые возвращают HTTP middleware/handler values, должны вычисляться в правильном order. Например, handler, задающий root directory site, должен идти перед handler, который обращается к root directory, чтобы тот знал directory path.

HTTP Caddyfile [имеет hard-coded ordering для standard directives](/docs/caddyfile/directives#directive-order). Это гарантирует, что пользователям не нужно знать implementation details самых распространенных функций web server, и упрощает написание корректных configurations. Единый hard-coded list также предотвращает nondeterminism с учетом extensible nature Caddyfile.

**Когда вы регистрируете новую handler directive, ее нужно добавить в этот list, прежде чем ее можно будет использовать (вне блока `route`).** Это делается одним из трех methods:

- (Рекомендуется) Author plugin может вызвать [`httpcaddyfile.RegisterDirectiveOrder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile#RegisterDirectiveOrder) в `init()` после регистрации директивы, чтобы вставить directive в order относительно другой [standard directive](/docs/caddyfile/directives#directive-order). Тогда пользователи смогут использовать directive напрямую в своих sites без дополнительной настройки. Например, чтобы вставить directive `gizmo` для выполнения после handler `header`:

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- Пользователи могут добавить [глобальную опцию `order`](/docs/caddyfile/options), чтобы изменить standard order для своего Caddyfile. Например: `order gizmo before respond` вставит новую directive `gizmo` для выполнения перед handler `respond`. После этого directive можно использовать обычным образом.

- Пользователи могут поместить directive в [блок `route`](/docs/caddyfile/directives/route). Поскольку directives в блоке route не переупорядочиваются, directives, используемым в route block, не нужно присутствовать в list.

Если вы выбираете один из двух последних вариантов, задокументируйте рекомендацию для пользователей о правильном месте вашей directive в list, чтобы они могли использовать ее корректно.

<a id="classes"></a>
### Classes

Эта таблица описывает каждый class с exported types, распознаваемый HTTP Caddyfile adapter:

Class name | Expected type | Описание
---------- | ------------- | -----------
bind | `[]string` | Server listener bind addresses
route | `caddyhttp.Route` | HTTP handler route
error_route | `*caddyhttp.Subroute` | HTTP error handling route
tls.connection_policy | `*caddytls.ConnectionPolicy` | TLS connection policy
tls.cert_issuer | `certmagic.Issuer` | TLS certificate issuer
tls.cert_loader | `caddytls.CertificateLoader` | TLS certificate loader

<a id="server-types"></a>
## Server Types

Структурно Caddyfile — простой format, поэтому могут существовать разные types форматов Caddyfile (иногда называемые "server types") для разных нужд.

Default Caddyfile format — HTTP Caddyfile, с которым вы, вероятно, знакомы. Этот format в основном настраивает [`http` app](/docs/modules/http), лишь потенциально добавляя немного config в другие parts структуры Caddy config (например, app `tls` для загрузки и автоматизации certificates).

Для настройки apps, отличных от HTTP, можно реализовать собственный config adapter, использующий [ваш собственный server type](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter). Caddyfile adapter фактически сам parse input и отдаст вам list server blocks и options, а ваша adapter logic должна осмыслить эту structure и превратить ее в JSON config.
