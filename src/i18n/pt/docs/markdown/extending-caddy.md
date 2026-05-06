---
title: "Estendendo o Caddy"
---

# Estendendo o Caddy

O Caddy é fácil de estender devido à sua arquitetura modular. A maioria dos tipos de extensões (ou plugins) do Caddy são conhecidos como _módulos_ se estenderem ou se conectarem à estrutura de configuração do Caddy. Para ser claro, os módulos do Caddy são distintos dos [módulos Go](https://github.com/golang/go/wiki/Modules) (mas também são módulos Go).

**Pré-requisitos:**
- Compreensão básica da [arquitetura do Caddy](/docs/architecture)
- Proficiência na linguagem Go
- [`go` <img src="/old/resources/images/external-link.svg" class="external-link">](https://golang.org/doc/install)
- [`xcaddy` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/xcaddy)


<a id="quick-start"></a>
## Início Rápido

Um módulo Caddy é qualquer tipo nomeado que se registra como um módulo Caddy quando seu pacote é importado. Crucialmente, um módulo sempre implementa a interface [`caddy.Module`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Module), que fornece seu nome e uma função construtora.

Em um novo módulo Go, cole o seguinte modelo em um arquivo Go e personalize o nome do seu pacote, o nome do tipo e o ID do módulo Caddy:

```go
package mymodule

import "github.com/caddyserver/caddy/v2"

func init() {
	caddy.RegisterModule(Gizmo{})
}

// Gizmo é um exemplo; coloque seu próprio tipo aqui.
type Gizmo struct {
}

// CaddyModule retorna as informações do módulo Caddy.
func (Gizmo) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "foo.gizmo",
		New: func() caddy.Module { return new(Gizmo) },
	}
}
```

Em seguida, execute este comando no diretório do seu projeto e você verá seu módulo na lista:

<pre><code class="cmd bash">xcaddy list-modules
...
foo.gizmo
...</code></pre>

<aside class="tip">

O [comando `xcaddy`](https://github.com/caddyserver/xcaddy) é uma parte importante do fluxo de trabalho de todo desenvolvedor de módulos. Ele compila o Caddy com seu plugin e o executa com os argumentos fornecidos. Ele descarta o binário temporário a cada vez (semelhante ao `go run`).

</aside>


Parabéns, seu módulo se registra no Caddy e pode ser usado no [documento de configuração do Caddy](/docs/json/) em quaisquer lugares que usem módulos no mesmo namespace.

Nos bastidores, o `xcaddy` está simplesmente criando um novo módulo Go que requer tanto o Caddy quanto o seu plugin (com um `replace` apropriado para usar sua versão de desenvolvimento local) e, em seguida, adiciona uma importação para garantir que ele seja compilado:

```go
import _ "github.com/example/mymodule"
```


<a id="module-basics"></a>
## Fundamentos de Módulos

Os módulos Caddy:

1. Implementam a interface `caddy.Module` para fornecer um ID e um construtor
2. Têm um nome exclusivo no namespace adequado
3. Geralmente satisfazem alguma(s) interface(s) que sejam significativas para o módulo host desse namespace

**Módulos host** (ou _módulos pai_) são módulos que carregam/inicializam outros módulos. Eles normalmente definem namespaces para módulos convidados.

**Módulos convidados** (ou _módulos filhos_) são módulos que são carregados ou inicializados. Todos os módulos são módulos convidados.


<a id="module-ids"></a>
## IDs de Módulo

Cada módulo Caddy possui um ID exclusivo, consistindo em um namespace e um nome:

- Um ID completo se parece com `foo.bar.nome_do_modulo`
- O namespace seria `foo.bar`
- O nome seria `nome_do_modulo`, que deve ser exclusivo em seu namespace

IDs de módulo devem usar a convenção `snake_case`.

<a id="namespaces"></a>
### Namespaces

Namespaces são como classes, ou seja, um namespace define alguma funcionalidade que é comum entre todos os módulos dentro dele. Por exemplo, podemos esperar que todos os módulos dentro do namespace `http.handlers` sejam manipuladores (handlers) HTTP. Segue-se que um módulo host pode realizar uma asserção de tipo (type-assertion) dos módulos convidados nesse namespace de tipos `interface{}` para um tipo mais específico e útil, como `caddyhttp.MiddlewareHandler`.

Um módulo convidado deve estar corretamente no namespace para ser reconhecido por um módulo host, pois os módulos host solicitarão ao Caddy módulos dentro de um determinado namespace para fornecer a funcionalidade desejada pelo módulo host. Por exemplo, se você fosse escrever um módulo manipulador HTTP chamado `gizmo`, o nome do seu módulo seria `http.handlers.gizmo`, porque o aplicativo `http` procurará manipuladores no namespace `http.handlers`.

Dito de outra forma, espera-se que os módulos Caddy implementem [certas interfaces](/docs/extending-caddy/namespaces) dependendo do seu namespace de módulo. Com essa convenção, os desenvolvedores de módulos podem dizer coisas intuitivas como: "Todos os módulos no namespace `http.handlers` são manipuladores HTTP". Tecnicamente falando, isso geralmente significa: "Todos os módulos no namespace `http.handlers` implementam a interface `caddyhttp.MiddlewareHandler`". Como esse conjunto de métodos é conhecido, o tipo mais específico pode ser asseverado e usado.

**[Veja uma tabela mapeando todos os namespaces padrão do Caddy para seus tipos Go.](/docs/extending-caddy/namespaces)**

Os namespaces `caddy` e `admin` são reservados e não podem ser nomes de aplicativos.

Para escrever módulos que se conectam a módulos host de terceiros, consulte esses módulos para obter a documentação de seus namespaces.

<a id="names"></a>
### Nomes

O nome dentro de um namespace é significativo e altamente visível para os usuários, mas não é particularmente importante, desde que seja exclusivo, conciso e faça sentido para o que faz.


<a id="app-modules"></a>
## Módulos de Aplicativo (App)

Aplicativos (Apps) são módulos com um namespace vazio e que convencionalmente se tornam seu próprio namespace de nível superior. Os módulos de aplicativo implementam a interface [`caddy.App`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#App).

Esses módulos aparecem na propriedade [`"apps"`](/docs/json/#apps) do nível superior da configuração do Caddy:

```json
{
	"apps": {}
}
```

Exemplos de [aplicativos](/docs/json/apps/) são `http` e `tls`. O deles é o namespace vazio.

Os módulos convidados escritos para esses aplicativos devem estar em um namespace derivado do nome do aplicativo. Por exemplo, manipuladores HTTP usam o namespace `http.handlers` e carregadores de certificados TLS usam o namespace `tls.certificates`.

<a id="module-implementation"></a>
## Implementação de Módulo

Um módulo pode ser virtualmente qualquer tipo, mas structs são os mais comuns porque podem conter a configuração do usuário.


<a id="configuration"></a>
### Configuração

A maioria dos módulos requer alguma configuração. O Caddy cuida disso automaticamente, desde que seu tipo seja compatível com JSON. Assim, se um módulo for um tipo struct, ele precisará de tags de struct em seus campos, que devem usar `snake_case` de acordo com a convenção do Caddy:

```go
type Gizmo struct {
	MyField string `json:"my_field,omitempty"`
	Number  int    `json:"number,omitempty"`
}
```

Usar a opção `omitempty` na tag de struct omitirá o campo da saída JSON se for o valor zero para seu tipo. Isso é útil para manter a configuração JSON limpa e concisa quando convertida (marshaled) (por exemplo, ao adaptar do Caddyfile para JSON).

Quando um módulo é inicializado, ele já terá sua configuração preenchida. Também é possível realizar etapas adicionais de [provisionamento](#provisioning) e [validação](#validating) após a inicialização de um módulo.


<a id="module-lifecycle"></a>
### Ciclo de Vida do Módulo

A vida de um módulo começa quando ele é carregado por um módulo host. Ocorre o seguinte:

1. [`New()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleInfo.New) é chamado para obter uma instância do valor do módulo.
2. A configuração do módulo é desconvertida (unmarshaled) nessa instância.
3. Se o módulo for um [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner), o método `Provision()` é chamado.
4. If o módulo for um [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator), o método `Validate()` é chamado.
5. Neste ponto, o módulo host recebe o módulo convidado carregado como um valor `interface{}`, portanto, o módulo host geralmente fará a asserção de tipo do módulo convidado em um tipo mais útil. Verifique a documentação do módulo host para saber o que é exigido de um módulo convidado em seu namespace, por exemplo, quais métodos precisam ser implementados.
6. Quando um módulo não é mais necessário e se ele for um [`caddy.CleanerUpper`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#CleanerUpper), o método `Cleanup()` é chamado.

Observe que várias instâncias carregadas do seu módulo podem se sobrepor em um determinado momento! Durante as alterações de configuração, novos módulos são iniciados antes que os antigos sejam interrompidos. Certifique-se de usar o estado global com cuidado. Use o tipo [`caddy.UsagePool`](https://pkg.go.dev/github.com/caddyserver/caddy/v2#UsagePool) para ajudar a gerenciar o estado global entre carregamentos de módulos. Se o seu módulo escuta em um soquete, use `caddy.Listen*()` para obter um soquete que suporte uso sobreposto.

<a id="provisioning"></a>
### Provisionamento

A configuração de um módulo será desconvertida (unmarshaled) em seu valor automaticamente (ao carregar a configuração JSON). Isso significa, por exemplo, que os campos da struct serão preenchidos para você.

No entanto, se o seu módulo exigir etapas de provisionamento adicionais, você poderá implementar a interface (opcional) [`caddy.Provisioner`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Provisioner):

```go
// Provision configura o módulo.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	// TODO: configurar o módulo
	return nil
}
```

É aqui que você deve definir valores padrão para campos que não foram fornecidos pelo usuário (campos que não são seu valor zero). Se um campo for obrigatório, você poderá retornar um erro se não estiver definido. Para campos numéricos onde o valor zero tem significado (por exemplo, alguma duração de tempo limite), você pode querer suportar `-1` para significar "desligado" em vez de `0`, para que possa definir um valor padrão se o usuário não o configurou.

Também é onde os módulos host normalmente carregam seus módulos convidados/filhos.

Um módulo pode acessar outros aplicativos chamando `ctx.App()`, mas os módulos não devem ter dependências circulares. Em outras palavras, um módulo carregado pelo aplicativo `http` não pode depender do aplicativo `tls` se um módulo carregado pelo aplicativo `tls` depender do aplicativo `http`. (Muito semelhante às regras que proíbem ciclos de importação em Go.)

Além disso, você deve evitar realizar operações caras em `Provision`, pois o provisionamento é realizado mesmo se uma configuração estiver apenas sendo validada. Quando estiver na fase de provisionamento, não espere que o módulo seja realmente usado.

<a id="logs"></a>
#### Logs

Veja [como o registro (logging) funciona](/docs/logging) no Caddy. Se o seu módulo precisar de registro, não use `log.Print*()` da biblioteca padrão Go. Em outras palavras, **não use o logger global do Go**. O Caddy usa registro estruturado de alto desempenho e altamente flexível com o [zap](https://github.com/uber-go/zap).

Para emitir logs, obtenha um logger no método Provision do seu módulo:

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	g.logger = ctx.Logger() // g.logger é um *zap.Logger
}
```

Então você pode emitir logs estruturados e com níveis usando `g.logger`. Veja o [godoc do zap](https://pkg.go.dev/go.uber.org/zap?tab=doc#Logger) para detalhes.


<a id="validating"></a>
### Validação

Os módulos que gostariam de validar sua configuração podem fazê-lo satisfazendo a interface (opcional) [`caddy.Validator`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Validator):

```go
// Validate valida que o módulo tem uma configuração utilizável.
func (g Gizmo) Validate() error {
	// TODO: validar a configuração do módulo
	return nil
}
```

`Validate` deve ser uma função de apenas leitura. Ela é executada após o método `Provision()`.


<a id="interface-guards"></a>
### Protetores de Interface (Interface guards)

O comportamento do módulo Caddy é implícito porque as interfaces Go são satisfeitas implicitamente. Simplesmente adicionar os métodos certos ao tipo do seu módulo é tudo o que basta para garantir a correção do seu módulo. Assim, cometer um erro de digitação ou errar a assinatura do método pode levar a um comportamento inesperado (ou falta dele).

Felizmente, existe uma verificação de tempo de compilação fácil e sem sobrecarga que você pode adicionar ao seu código para garantir que adicionou os métodos corretos. Eles são chamados de protetores de interface:

```go
var _ InterfaceName = (*YourType)(nil)
```

Substitua `InterfaceName` pela interface que você pretende satisfazer e `YourType` pelo nome do tipo do seu módulo.

Por exemplo, um manipulador HTTP como o servidor de arquivos estáticos pode satisfazer várias interfaces:

```go
// Protetores de interface
var (
	_ caddy.Provisioner           = (*FileServer)(nil)
	_ caddyhttp.MiddlewareHandler = (*FileServer)(nil)
)
```

Isso evita que o programa seja compilado se `*FileServer` não satisfizer essas interfaces.

Sem protetores de interface, bugs confusos podem aparecer. Por exemplo, se o seu módulo deve se provisionar antes de ser usado, mas seu método `Provision()` tiver um erro (por exemplo, erro de digitação ou assinatura errada), o provisionamento nunca acontecerá, causando frustração. Os protetores de interface são super fáceis e podem evitar isso. Eles geralmente ficam no final do arquivo.


<a id="host-modules"></a>
## Módulos Host

Um módulo se torna um módulo host quando carrega seus próprios módulos convidados. Isso é útil se uma parte da funcionalidade do módulo puder ser implementada de diferentes maneiras.

Um módulo host é quase sempre uma struct. Normalmente, o suporte a um módulo convidado requer dois campos de struct: um para conter seu JSON bruto e outro para conter seu valor decodificado:

```go
type Gizmo struct {
	GadgetRaw json.RawMessage `json:"gadget,omitempty" caddy:"namespace=foo.gizmo.gadgets inline_key=gadgeter"`

	Gadget Gadgeter `json:"-"`
}
```

O primeiro campo (`GadgetRaw` neste exemplo) é onde a forma JSON bruta e não provisionada do módulo convidado pode ser encontrada.

O segundo campo (`Gadget`) é onde o valor final provisionado será eventualmente armazenado. Como o segundo campo não é voltado para o usuário, nós o excluímos do JSON com uma tag de struct. (Você também pode não exportá-lo se não for necessário para outros pacotes e, então, nenhuma tag de struct será necessária.)

<a id="caddy-struct-tags"></a>
### Tags de struct do Caddy

A tag de struct `caddy` no campo de módulo bruto ajuda o Caddy a saber o namespace e o nome (compreendendo o ID completo) do módulo a ser carregado. Também é usada para gerar documentação.

A tag de struct tem um formato muito simples: `chave1=val1 chave2=val2 ...`

Para campos de módulo, a tag de struct se parecerá com:

```go
`caddy:"namespace=foo.bar inline_key=baz"`
```

A parte `namespace=` é obrigatória. Ela define o namespace no qual procurar o módulo.

A parte `inline_key=` só é usada se o nome do módulo for encontrado _em linha_ com o próprio módulo; isso implica que o valor é um objeto onde uma das chaves é a _chave em linha_ e seu valor é o nome do módulo. Se omitido, o tipo do campo deve ser um [`caddy.ModuleMap`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#ModuleMap) ou `[]caddy.ModuleMap`, onde a chave do mapa é o nome do módulo.


<a id="loading-guest-modules"></a>
### Carregando módulos convidados

Para carregar um módulo convidado, chame [`ctx.LoadModule()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context.LoadModule) durante a fase de provisionamento:

```go
// Provision configura g e carrega seu gadget.
func (g *Gizmo) Provision(ctx caddy.Context) error {
	if g.GadgetRaw != nil {
		val, err := ctx.LoadModule(g, "GadgetRaw")
		if err != nil {
			return fmt.Errorf("loading gadget module: %v", err)
		}
		g.Gadget = val.(Gadgeter)
	}
	return nil
}
```

Observe que a chamada `LoadModule()` recebe um ponteiro para a struct e o nome do campo como uma string. Estranho, certo? Por que não apenas passar o campo da struct diretamente? É porque existem algumas maneiras diferentes de carregar módulos dependendo do layout da configuração. Essa assinatura de método permite que o Caddy use reflexão para descobrir a melhor maneira de carregar o módulo e, o mais importante, ler suas tags de struct.

Se um módulo convidado deve ser definido explicitamente pelo usuário, você deve retornar um erro se o campo Raw for nulo ou vazio antes de tentar carregá-lo.

Observe como o módulo carregado recebe uma asserção de tipo: `g.Gadget = val.(Gadgeter)` - isso ocorre porque o `val` retornado é um tipo `interface{}`, o que não é muito útil. No entanto, esperamos que todos os módulos no namespace declarado (`foo.gizmo.gadgets` da tag struct em nosso exemplo) implementem a interface `Gadgeter`, portanto, essa asserção de tipo é segura e podemos usá-la!

Se o seu módulo host definir um novo namespace, certifique-se de documentar esse namespace e seu(s) tipo(s) Go para desenvolvedores [como fizemos aqui](/docs/extending-caddy/namespaces).

<a id="module-documentation"></a>
## Documentação de Módulo

Registre o módulo para que um novo módulo Caddy apareça na documentação do módulo e esteja disponível em http://caddyserver.com/download. O registro está disponível em http://caddyserver.com/account. Crie uma nova conta se ainda não tiver uma e clique em "Register package".

<a id="complete-example"></a>
## Exemplo Completo

Suponhamos que queiramos escrever um módulo manipulador (handler) HTTP. Este será um middleware fictício para fins de demonstração que imprime o endereço IP do visitante em um fluxo em cada solicitação HTTP.

Também queremos que ele seja configurável via Caddyfile, porque a maioria das pessoas prefere usar o Caddyfile em situações não automatizadas. Fazemos isso registrando uma diretiva de manipulador Caddyfile, que é um tipo de diretiva que pode adicionar um manipulador à rota HTTP. Também implementamos a interface `caddyfile.Unmarshaler`. Ao adicionar essas poucas linhas de código, este módulo pode ser configurado com o Caddyfile! Por exemplo: `visitor_ip stdout`.

Aqui está o código para tal módulo, com comentários explicativos:

```go
package visitorip

import (
	"fmt"
	"io"
	"net/http"
	"os"

	"github.com/caddyserver/caddy/v2"
	"github.com/caddyserver/caddy/v2/caddyconfig/caddyfile"
	"github.com/caddyserver/caddy/v2/caddyconfig/httpcaddyfile"
	"github.com/caddyserver/caddy/v2/modules/caddyhttp"
)

func init() {
	caddy.RegisterModule(Middleware{})
	httpcaddyfile.RegisterHandlerDirective("visitor_ip", parseCaddyfile)
}

// Middleware implementa um manipulador HTTP que grava o
// endereço IP do visitante em um arquivo ou fluxo.
type Middleware struct {
	// O arquivo ou fluxo no qual gravar. Pode ser "stdout"
	// ou "stderr".
	Output string `json:"output,omitempty"`

	w io.Writer
}

// CaddyModule retorna as informações do módulo Caddy.
func (Middleware) CaddyModule() caddy.ModuleInfo {
	return caddy.ModuleInfo{
		ID:  "http.handlers.visitor_ip",
		New: func() caddy.Module { return new(Middleware) },
	}
}

// Provision implementa caddy.Provisioner.
func (m *Middleware) Provision(ctx caddy.Context) error {
	switch m.Output {
	case "stdout":
		m.w = os.Stdout
	case "stderr":
		m.w = os.Stderr
	default:
		return fmt.Errorf("an output stream is required")
	}
	return nil
}

// Validate implementa caddy.Validator.
func (m *Middleware) Validate() error {
	if m.w == nil {
		return fmt.Errorf("no writer")
	}
	return nil
}

// ServeHTTP implementa caddyhttp.MiddlewareHandler.
func (m Middleware) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	m.w.Write([]byte(r.RemoteAddr))
	return next.ServeHTTP(w, r)
}

// UnmarshalCaddyfile implementa caddyfile.Unmarshaler.
func (m *Middleware) UnmarshalCaddyfile(d *caddyfile.Dispenser) error {
	d.Next() // consome o nome da diretiva

	// requer um argumento
	if !d.NextArg() {
		return d.ArgErr()
	}

	// armazena o argumento
	m.Output = d.Val()
	return nil
}

// parseCaddyfile desconverte os tokens de h em um novo Middleware.
func parseCaddyfile(h httpcaddyfile.Helper) (caddyhttp.MiddlewareHandler, error) {
	var m Middleware
	err := m.UnmarshalCaddyfile(h.Dispenser)
	return m, err
}

// Protetores de interface
var (
	_ caddy.Provisioner           = (*Middleware)(nil)
	_ caddy.Validator             = (*Middleware)(nil)
	_ caddyhttp.MiddlewareHandler = (*Middleware)(nil)
	_ caddyfile.Unmarshaler       = (*Middleware)(nil)
)
```
