---
title: "Suporte ao Caddyfile"
---

# Suporte ao Caddyfile

Os módulos Caddy são adicionados automaticamente à [configuração JSON nativa](/docs/json/) em virtude do seu namespace quando são [registrados](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule), tornando-os utilizáveis e documentados. Isso torna o suporte ao Caddyfile puramente opcional, mas é frequentemente solicitado por usuários que preferem o Caddyfile.

<a id="unmarshaler"></a>
## Unmarshaler

Para adicionar suporte ao Caddyfile para o seu módulo, basta implementar a interface [`caddyfile.Unmarshaler`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Unmarshaler). Você escolhe a sintaxe do Caddyfile que seu módulo possui pela forma como você analisa (parse) os tokens.

O trabalho de um unmarshaler é simplesmente configurar o tipo do seu módulo, por exemplo, preenchendo seus campos, usando o [`caddyfile.Dispenser`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Dispenser) passado a ele. Por exemplo, um tipo de módulo chamado `Gizmo` pode ter este método:

```go
// UnmarshalCaddyfile implementa caddyfile.Unmarshaler. Sintaxe:
//
// gizmo <name> [<option>]
//
func (g *Gizmo) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // consome o nome da diretiva

	if !d.Args(&g.Name) {
		// argumentos insuficientes
		return d.ArgErr()
	}
	if d.NextArg() {
		// argumento opcional
		g.Option = d.Val()
	}
	if d.NextArg() {
		// argumentos em excesso
		return d.ArgErr()
	}

	return nil
}
```

É uma boa ideia documentar a sintaxe no comentário godoc do método. Veja o [godoc para o pacote `caddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc) para mais informações sobre a análise do Caddyfile.

O token do nome da diretiva pode ser consumido/ignorado com uma simples chamada `d.Next()`.

Certifique-se de verificar se há argumentos ausentes e/ou em excesso com `d.NextArg()` ou `d.RemainingArgs()`. Use `d.ArgErr()` para uma mensagem simples de "caso inválido" ou use `d.Errf("alguma mensagem")` para criar uma mensagem de erro útil com uma explicação do problema (e, idealmente, uma solução sugerida).

Você também deve adicionar um [protetor de interface](/docs/extending-caddy#interface-guards) para garantir que a interface seja satisfeita corretamente:

```go
var _ caddyfile.Unmarshaler = (*Gizmo)(nil)
```

<a id="blocks"></a>
### Blocos

Para aceitar mais configurações do que as que cabem em uma única linha, você pode querer permitir um bloco com subdiretivas. Isso pode ser feito usando `d.NextBlock()` e iterando até retornar ao nível de aninhamento original:

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

Desde que cada iteração do loop consuma todo o segmento (linha ou bloco), essa é uma maneira elegante de lidar com blocos.

<a id="http-directives"></a>
## Diretivas HTTP

O Caddyfile HTTP é a sintaxe do adaptador Caddyfile padrão do Caddy (ou "tipo de servidor"). Ele é extensível, o que significa que você pode [registrar](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterDirective) suas próprias diretivas de "nível superior" para o seu módulo:

```go
func init() {
	httpcaddyfile.RegisterDirective("gizmo", parseCaddyfile)
}
```

Se sua diretiva retornar apenas um único manipulador (handler) HTTP (como é comum), você pode achar o [`RegisterHandlerDirective`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#RegisterHandlerDirective) mais fácil:

```go
func init() {
	httpcaddyfile.RegisterHandlerDirective("gizmo", parseCaddyfileHandler)
}
```

A ideia básica é que [a função de análise](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#UnmarshalFunc) que você associa à sua diretiva retorne um ou mais valores [`ConfigValue`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc#ConfigValue). (Ou, se estiver usando `RegisterHandlerDirective`, ela simplesmente retorna o valor `caddyhttp.MiddlewareHandler` preenchido diretamente.) Cada valor de configuração é associado a uma ["classe"](#classes) que ajuda o adaptador Caddyfile HTTP a saber em qual(is) parte(s) da configuração JSON final ele pode ser usado. Todos os valores de configuração são despejados em uma pilha da qual o adaptador extrai ao construir a configuração JSON final.

Esse design permite que sua diretiva retorne quaisquer valores de configuração para quaisquer classes reconhecidas, o que significa que ela pode influenciar quaisquer partes da configuração para as quais o adaptador Caddyfile HTTP tenha uma classe designada.

Se você já implementou o método `UnmarshalCaddyfile()`, sua função de análise poderia ser tão simples quanto:

```go
// parseCaddyfileHandler descompacta tokens de h em um novo valor de manipulador middleware.
func parseCaddyfileHandler(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var g Gizmo
	err := g.UnmarshalCaddyfile(h.Dispenser)
	return g, err
}
```

Veja o [`godoc do pacote httpcaddyfile`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile?tab=doc) para mais informações sobre como usar o tipo `httpcaddyfile.Helper`.

<a id="handler-order"></a>
### Ordem dos manipuladores

Todas as diretivas que retornam valores de middleware/manipulador HTTP precisam ser avaliadas na ordem correta. Por exemplo, um manipulador que define o diretório raiz do site deve vir antes de um manipulador que acessa o diretório raiz, para que ele saiba qual é o caminho do diretório.

O Caddyfile HTTP [tem uma ordem codificada rigidamente para as diretivas padrão](/docs/caddyfile/directives#directive-order). Isso garante que os usuários não precisem conhecer os detalhes da implementação das funções mais comuns de seu servidor web e torna mais fácil para eles escreverem configurações corretas. Uma única lista codificada rigidamente também evita o não determinismo, dada a natureza extensível do Caddyfile.

**Quando você registra uma nova diretiva de manipulador, ela deve ser adicionada a essa lista antes de poder ser usada (fora de um bloco `route`).** Isso é feito usando um de três métodos:

- (Recomendado) O autor do plugin pode chamar [`httpcaddyfile.RegisterDirectiveOrder`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile#RegisterDirectiveOrder) em `init()` após registrar a diretiva, para inserir a diretiva na ordem relativa a outra [diretiva padrão](/docs/caddyfile/directives#directive-order). Ao fazer isso, os usuários podem usar a diretiva diretamente em seus sites sem configuração extra. Por exemplo, para inserir sua diretiva `gizmo` para ser avaliada após o manipulador `header`:

	```go
	httpcaddyfile.RegisterDirectiveOrder("gizmo", httpcaddyfile.After, "header")
	```

- Os usuários podem adicionar a [`opção global order`](/docs/caddyfile/options) para modificar a ordem padrão em seu Caddyfile. Por exemplo: `order gizmo before respond` inserirá uma nova diretiva `gizmo` para ser avaliada antes do manipulador `respond`. Então a diretiva poderá ser usada normalmente.

- Os usuários podem colocar a diretiva em um [bloco `route`](/docs/caddyfile/directives/route). Como as diretivas em um bloco route não são reordenadas, as diretivas usadas em um bloco route não precisam aparecer na lista.

Se você escolher uma das duas últimas opções, documente uma recomendação para seus usuários sobre qual lugar na lista é o local correto para a sua diretiva ser ordenada, para que eles possam usá-la adequadamente.

<a id="classes"></a>
### Classes

Esta tabela descreve cada classe com tipos exportados que é reconhecida pelo adaptador Caddyfile HTTP:

Nome da Classe | Tipo Esperado | Descrição
---------- | ------------- | -----------
bind | `[]string` | Endereços de escuta do servidor
route | `caddyhttp.Route` | Rota do manipulador HTTP
error_route | `*caddyhttp.Subroute` | Rota de tratamento de erros HTTP
tls.connection_policy | `*caddytls.ConnectionPolicy` | Política de conexão TLS
tls.cert_issuer | `certmagic.Issuer` | Emissor de certificado TLS
tls.cert_loader | `caddytls.CertificateLoader` | Carregador de certificado TLS

<a id="server-types"></a>
## Tipos de Servidor

Estruturalmente, o Caddyfile é um formato simples, portanto, pode haver diferentes tipos de formatos de Caddyfile (às vezes chamados de "tipos de servidor") para atender a diferentes necessidades.

O formato Caddyfile padrão é o Caddyfile HTTP, com o qual você provavelmente está familiarizado. Este formato configura principalmente o [aplicativo `http`](/docs/modules/http), embora possa potencialmente espalhar alguma configuração em outras partes da estrutura de configuração do Caddy (por exemplo, o aplicativo `tls` para carregar e automatizar certificados).

Para configurar aplicativos que não sejam HTTP, você pode querer implementar seu próprio adaptador de configuração que use [seu próprio tipo de servidor](https://pkg.go.dev/github.com/caddyserver/caddy/v2/caddyconfig/caddyfile?tab=doc#Adapter). O adaptador Caddyfile irá realmente analisar a entrada para você e fornecer a lista de blocos de servidor e opções, e cabe ao seu adaptador dar sentido a essa estrutura e transformá-la em uma configuração JSON.
