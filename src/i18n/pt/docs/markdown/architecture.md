---
title: Arquitetura
---

Arquitetura
===========

O Caddy é um binário único, autocontido, estático, sem dependências externas, porque é escrito em Go. Esses valores são parte importante da visão do projeto porque simplificam a implantação e reduzem o trabalho tedioso de depuração em ambientes de produção.

Se não há linkagem dinâmica, então como ele pode ser estendido? O Caddy tem uma arquitetura de plugins inovadora que amplia suas capacidades muito além das de qualquer outro servidor web, mesmo daqueles com dependências externas (dinamicamente vinculadas).

Nossa filosofia de "menos peças móveis" resulta, no fim, em sites mais confiáveis, mais fáceis de administrar e menos caros - especialmente em escala. Este documento semi-técnico descreve como alcançamos esse objetivo por meio de engenharia de software.

## Visão geral

O Caddy consiste em um comando, uma biblioteca central e módulos.

O **comando** fornece a [interface de linha de comando](/docs/command-line) com a qual você provavelmente já está familiarizado. É assim que você inicia o processo a partir do seu sistema operacional. A quantidade de código e lógica aqui é relativamente pequena, e contém apenas o necessário para inicializar o núcleo da forma desejada pelo usuário. Evitamos intencionalmente usar flags e variáveis de ambiente para configuração, exceto quando dizem respeito à inicialização da configuração.

<aside class="tip">

Os módulos podem adicionar subcomandos à interface de linha de comando! Por exemplo, é daí que vem o comando [`caddy file-server`](/docs/command-line#caddy-file-server). Esses comandos adicionados podem usar quaisquer flags ou variáveis de ambiente que quiserem, embora os comandos centrais do Caddy minimizem esse uso.

</aside>

A **[biblioteca central](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc)**, ou "core" do Caddy, gerencia principalmente a configuração. Ela pode [`Run()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Run) uma nova configuração ou [`Stop()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Stop) uma configuração em execução. Ela também fornece várias utilidades, tipos e valores para os módulos usarem.

Os **módulos** fazem todo o resto. Muitos módulos já vêm incorporados ao Caddy, e são chamados de _módulos padrão_. Eles são considerados os mais úteis para a maioria dos usuários.

<aside class="tip">

Às vezes os termos *module*, *plugin* e *extension* são usados de forma intercambiável, e normalmente isso não é problema. Tecnicamente, todos os módulos são plugins, mas nem todo plugin é um módulo. Módulos são especificamente um tipo de plugin que estende a [estrutura de configuração](/docs/json/) do Caddy.

</aside>

## Núcleo do Caddy

Em sua essência, o Caddy apenas carrega uma configuração inicial ("config") ou, se não houver uma, abre um socket para aceitar uma nova configuração depois.

Uma [configuração do Caddy](/docs/json/) é um documento JSON, com alguns campos no nível superior:

```json
{
	"admin": {},
	"logging": {},
	"apps": {•••},
	...
}
```

O núcleo do Caddy sabe trabalhar nativamente com alguns desses campos:

- [`admin`](/docs/json/admin/) para que ele possa configurar a [admin API](/docs/api) e gerenciar o processo
- [`logging`](/docs/json/logging/) para que ele possa [emitir logs](/docs/logging)

Mas outros campos de nível superior, como [`apps`](/docs/json/apps/), são opacos para o core do Caddy. Na verdade, tudo o que o Caddy sabe fazer com os bytes em `apps` é desserializá-los em um tipo de interface sobre o qual ele pode chamar dois métodos:

1. `Start()`
2. `Stop()`

... e só isso. Ele chama `Start()` em cada app quando uma configuração é carregada, e `Stop()` em cada app quando uma configuração é descarregada.

Quando um módulo de app é iniciado, ele dá início ao ciclo de vida do módulo dessa app.

<aside class="tip">

Se você é um programador criando módulos para o Caddy, pode encontrar informações análogas em nosso guia [Extending Caddy](/docs/extending-caddy), mas com mais foco em código.

</aside>

## Ciclo de vida do módulo

Há dois tipos de módulos: _host modules_ e _guest modules_.

**Host modules** (ou módulos "pai") são os que carregam outros módulos.

**Guest modules** (ou módulos "filho") são os que são carregados. Todos os módulos são guest modules - até mesmo módulos de app.

Os módulos são carregados, provisionados e validados, utilizados e depois limpos, nesta sequência:

1. Carregado
2. Provisionado e validado
3. Utilizado
4. Limpo

O Caddy inicia o ciclo de vida do módulo quando uma configuração é carregada, começando pela inicialização de todos os módulos de app configurados. A partir daí, é como "tartarugas até o fundo", porque cada módulo de app leva o restante do processo adiante.

### Fase de carregamento

Carregar um módulo envolve desserializar seus bytes JSON em um valor tipado na memória. É basicamente isso. É apenas decodificar JSON em um valor.

### Fase de provisionamento

Essa fase é onde fica a maior parte do trabalho de preparação. Todos os módulos têm a chance de se provisionar depois de carregados.

Como quaisquer propriedades da codificação JSON já terão sido decodificadas, aqui só é necessário fazer preparação adicional. A tarefa mais comum durante o provisionamento é configurar módulos guest. Em outras palavras, provisionar um módulo host também resulta no provisionamento de seus módulos guest, e assim por diante.

Você pode ter uma noção disso ao [navegar pela estrutura JSON do Caddy em nossa documentação](/docs/json/). Em qualquer lugar em que você veja `{•••}` é onde módulos guest podem ser usados; e, ao entrar em um deles, você pode continuar explorando até não haver mais módulos guest.

Outras tarefas comuns de provisionamento são configurar valores internos que serão usados durante a vida útil do módulo ou padronizar entradas. Por exemplo, o módulo [`http.matchers.remote_ip`](/docs/modules/http.matchers.remote_ip) usa a fase de provisionamento para fazer o parse de valores CIDR a partir das entradas de string recebidas do JSON. Dessa forma, ele não precisa fazer isso a cada requisição HTTP e, como resultado, é mais eficiente.

A validação também pode acontecer na fase de provisionamento. Se a configuração resultante de um módulo for inválida, um erro pode ser retornado aqui e abortar todo o processo de carregamento da configuração.

### Fase de uso

Depois que um módulo guest é provisionado e validado, ele pode ser usado pelo seu módulo host. O que isso significa exatamente fica a cargo de cada módulo host.

Cada módulo tem um ID, composto por um namespace e um nome dentro desse namespace. Por exemplo, [`http.handlers.reverse_proxy`](/docs/modules/http.handlers.reverse_proxy) é um handler HTTP porque está no namespace `http.handlers`, e seu nome é `reverse_proxy`. Todos os módulos no namespace `http.handlers` satisfazem a mesma interface, conhecida pelo módulo host. Assim, a app `http` sabe como carregar e usar esse tipo de módulo.

### Fase de limpeza

Quando chega a hora de parar uma configuração, todos os módulos são descarregados. Se um módulo alocou recursos que devem ser liberados, ele tem a oportunidade de fazê-lo na fase de limpeza.

## Plugando

Um módulo - ou qualquer plugin do Caddy - é "plugado" no Caddy adicionando um `import` do pacote do módulo. Ao importar o pacote, [o módulo se registra sozinho](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule) no core do Caddy, de modo que, quando o processo do Caddy inicia, ele conhece cada módulo pelo nome. Ele pode até associar valores de módulo e nomes, e vice-versa.

<aside class="tip">

Plugins podem ser adicionados sem modificar a base de código do Caddy. Há instruções [no readme](https://github.com/caddyserver/caddy/#with-version-information-andor-plugins) para fazer isso!

</aside>

## Gerenciamento de configuração

Alterar a configuração ativa de um servidor em execução (frequentemente chamado de "reload") pode ser complicado com os altos níveis de concorrência e os milhares de parâmetros que servidores exigem. O Caddy resolve esse problema de forma elegante usando um design que traz muitos benefícios:

- Sem interrupção para serviços em execução
- Mudanças granulares de configuração são possíveis
- Apenas um lock é necessário (em segundo plano)
- Todos os reloads são atômicos, consistentes, isolados e em sua maioria duráveis ("ACID")
- Estado global mínimo

Você pode [assistir a um vídeo sobre o design do Caddy 2 aqui](https://www.youtube.com/watch?v=EhJO8giOqQs).

O reload de uma configuração funciona provisionando os novos módulos e, se tudo der certo, os antigos são limpos. Por um breve período, duas configurações ficam operacionais ao mesmo tempo.

Cada configuração está associada a um [contexto](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context) que mantém todo o estado dos módulos, então a maior parte do estado nunca sai do escopo de uma configuração. Isso é ótimo para correção, desempenho e simplicidade!

No entanto, às vezes um estado verdadeiramente global é necessário. Por exemplo, o reverse proxy pode manter o controle da saúde de seus upstreams; como existe apenas um de cada upstream globalmente, seria ruim se ele esquecesse deles sempre que uma pequena alteração de configuração fosse feita. Felizmente, o Caddy [fornece mecanismos](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#UsagePool) semelhantes ao garbage collector de um runtime de linguagem para manter o estado global organizado.

Uma abordagem óbvia para atualizações de configuração on-line é sincronizar o acesso a cada parâmetro de configuração, até mesmo nos caminhos quentes. Isso é absurdamente ruim em termos de desempenho e complexidade - especialmente em escala - então o Caddy não usa essa abordagem.

Em vez disso, as configurações são tratadas como unidades imutáveis e atômicas: ou tudo é substituído, ou nada muda. Os [endpoints da admin API](/docs/api) - que permitem alterações granulares ao navegar pela estrutura - mutam apenas uma representação em memória da configuração, a partir da qual um documento de configuração totalmente novo é gerado e carregado. Essa abordagem traz enormes benefícios em simplicidade, desempenho e consistência. Como há apenas um lock, o Caddy consegue processar reloads frequentes com facilidade.
