---
title: Profilando o Caddy
---

Profilando o Caddy
================

Um **perfil de programa** é um retrato do uso de recursos de um programa em tempo de execução. Perfis podem ser extremamente úteis para identificar áreas problemáticas, depurar bugs e crashes e otimizar código.

O Caddy usa as ferramentas do Go para capturar perfis, chamadas [pprof](https://github.com/google/pprof), e elas já vêm embutidas no comando `go`.

Perfis mostram consumo de CPU e memória, exibem stack traces de goroutines e ajudam a localizar deadlocks ou primitivas de sincronização com alta contenção.

Ao relatar certos bugs no Caddy, talvez peçamos um perfil. Este artigo pode ajudar. Ele descreve tanto como obter perfis com o Caddy quanto como usar e interpretar os perfis pprof resultantes em geral.

Antes de começar, duas coisas para saber:

1. **Os perfis do Caddy NÃO são sensíveis em termos de segurança.** Eles contêm leituras técnicas inofensivas, não o conteúdo da memória. Não concedem acesso a sistemas. É seguro compartilhá-los.
2. **Perfis são leves e podem ser coletados em produção.** Na verdade, isso é uma prática recomendada para muitos usuários; veja mais adiante neste artigo.

## Obtendo perfis

Os perfis estão disponíveis pela [interface de administração](/docs/api) em `/debug/pprof/`. Em uma máquina rodando Caddy, abra isso no navegador:

```
http://localhost:2019/debug/pprof/
```

<aside class="tip">
	Por padrão, a admin API só é acessível localmente. Se estiver rodando remotamente, em VMs ou em containers, veja a próxima seção para saber como acessar esse endpoint.
</aside>

Você verá uma tabela simples com contagens e links, como:

Count | Profile
----- | --------------------
79    | allocs
0     | block
0     | cmdline
22    | goroutine
79    | heap
0     | mutex
0     | profile
29    | threadcreate
0     | trace
|     | full goroutine stack dump

As contagens são uma forma útil de identificar leaks rapidamente. Se você suspeita de um leak, atualize a página repetidamente e verá uma ou mais dessas contagens aumentando constantemente. Se a contagem de heap crescer, pode ser um leak de memória; se a contagem de goroutines crescer, pode ser um leak de goroutine.

Clique nos perfis e veja como eles são. Alguns podem estar vazios e isso é normal muitas vezes. Os mais usados são **goroutine** (stacks de funções), **heap** (memória) e **profile** (CPU). Outros perfis são úteis para depurar contenção de mutex ou deadlocks.

Na parte de baixo, há uma descrição simples de cada perfil:

- **allocs:** Uma amostragem de todas as alocações de memória passadas
- **block:** Stack traces que levaram ao bloqueio em primitivas de sincronização
- **cmdline:** A invocação de linha de comando do programa atual
- **goroutine:** Stack traces de todas as goroutines atuais. Use `debug=2` como parâmetro de query para exportar no mesmo formato de um panic não recuperado.
- **heap:** Uma amostragem de alocações de memória de objetos vivos. Você pode especificar o parâmetro GET `gc` para executar GC antes de capturar a amostra do heap.
- **mutex:** Stack traces dos detentores de mutexes em contenção
- **profile:** Perfil de CPU. Você pode especificar a duração em segundos pelo parâmetro GET `seconds`. Depois de obter o arquivo do perfil, use o comando `go tool pprof` para investigar o perfil.
- **threadcreate:** Stack traces que levaram à criação de novas threads do sistema operacional
- **trace:** Um trace de execução do programa atual. Você pode especificar a duração em segundos pelo parâmetro GET `seconds`. Depois de obter o arquivo de trace, use o comando `go tool trace` para investigá-lo.

<aside class="tip">

A diferença entre "goroutine" e "full goroutine stack dump" é o parâmetro `?debug=2`: o stack dump completo é como a saída que você veria após um panic; ele é mais verboso e, notavelmente, não colapsa goroutines idênticas.

</aside>

### Baixando perfis

Clicar nos links da página índice do pprof acima vai fornecer perfis em formato texto. Isso é útil para depuração, e é o formato que nós da equipe do Caddy preferimos, porque conseguimos examinar rapidamente em busca de pistas óbvias sem precisar de ferramentas extras.

Mas o binário é, na verdade, o formato padrão. Os links HTML adicionam o parâmetro de query `?debug=` para formatá-los como texto, exceto o link "profile" (CPU), que não tem representação textual.

Estes são os parâmetros de query que você pode definir (da [documentação do Go](https://pkg.go.dev/net/http/pprof#hdr-Parameters)):

- **`debug=N` (todos os perfis exceto cpu):** formato da resposta: N = 0: binário (padrão), N > 0: texto puro
- **`gc=N` (perfil heap):** N > 0: executa um ciclo de garbage collection antes de perfilhar
- **`seconds=N` (perfis allocs, block, goroutine, heap, mutex, threadcreate):** retorna um perfil delta
- **`seconds=N` (perfis cpu, trace):** profile pelo tempo dado

Como esses são endpoints HTTP, você também pode usar qualquer cliente HTTP como curl ou wget para baixar perfis.

Depois que seus perfis forem baixados, você pode enviá-los para um comentário de issue no GitHub ou usar um site como [pprof.me](https://pprof.me/). Especificamente para perfis de CPU, [flamegraph.com](https://flamegraph.com/) é outra opção.

## Acesso remoto

_Se você já consegue acessar a admin API localmente, pule esta seção._

Por padrão, a admin API do Caddy só é acessível pelo socket de loopback. No entanto, há pelo menos 3 formas de acessar o endpoint `/debug/pprof` do Caddy remotamente:

### Reverse proxy pelo seu site

Uma opção fácil é simplesmente fazer reverse proxy para ele a partir do seu site:

```caddy-d
reverse_proxy /debug/pprof/* localhost:2019 {
	header_up Host {upstream_hostport}
}
```

Isso, claro, vai tornar os perfis disponíveis para quem conseguir conectar ao seu site. Se isso não for desejado, você pode adicionar alguma autenticação usando um módulo de autenticação HTTP da sua escolha.

(Não esqueça o matcher `/debug/pprof/*`, senão você vai fazer proxy da admin API inteira!)

### Túnel SSH

Outra forma é usar um túnel SSH. Trata-se de uma conexão criptografada usando o protocolo SSH entre seu computador e o seu servidor. Execute um comando como este no seu computador:

<pre><code class="cmd bash">ssh -N username@example.com -L 8123:localhost:2019</code></pre>

Isso tunela `localhost:8123` (na sua máquina local) para `localhost:2019` em `example.com`. Lembre-se de substituir `username`, `example.com` e as portas conforme necessário.

<aside class="tip">

Esse comando vai rodar em primeiro plano. Tenha em mente que, se você tentar colocá-lo em background com <kbd>Ctrl</kbd>+<kbd>Z</kbd>, isso vai pausar o túnel, e as conexões usando o túnel vão falhar.

</aside>

Então, em outro terminal, você pode usar `curl` assim:

<pre><code class="cmd bash">curl -v http://localhost:8123/debug/pprof/ -H "Host: localhost:2019"</code></pre>

Você pode evitar a necessidade de `-H "Host: ..."` usando a porta `2019` em ambos os lados do túnel (mas isso exige que a porta `2019` não esteja sendo usada na sua própria máquina, ou seja, que você não tenha o Caddy rodando localmente).

Enquanto o túnel estiver ativo, você pode acessar qualquer parte da admin API. Use <kbd>Ctrl</kbd>+<kbd>C</kbd> no comando `ssh` para fechar o túnel.

#### Túnel de longa duração

Rodar um túnel com o comando acima exige que você mantenha o terminal aberto. Se quiser rodar o túnel em segundo plano, você pode iniciá-lo assim:

<pre><code class="cmd bash">ssh -f -N -M -S /tmp/caddy-tunnel.sock username@example.com -L 8123:localhost:2019</code></pre>

Isso vai iniciar em background e criar um socket de controle em `/tmp/caddy-tunnel.sock`. Você pode então usar o socket de controle para encerrar o túnel quando terminar:

<pre><code class="cmd bash">ssh -S /tmp/caddy-tunnel.sock -O exit e</code></pre>

### Admin API remota

Você também pode configurar a admin API para aceitar conexões remotas de clientes autorizados.

(TODO: Escrever um artigo sobre isso.)

## Perfis de goroutine

O dump de goroutines é útil para saber quais goroutines existem e quais são seus call stacks. Em outras palavras, ele nos dá uma ideia de código que está sendo executado atualmente ou que está bloqueado/aguardando.

Se você clicar em "goroutines" ou acessar `/debug/pprof/goroutine?debug=1`, verá uma lista de goroutines e seus call stacks. Por exemplo:

```
goroutine profile: total 88
23 @ 0x43e50e 0x436d37 0x46bda5 0x4e1327 0x4e261a 0x4e2608 0x545a65 0x5590c5 0x6b2e9b 0x50ddb8 0x6b307e 0x6b0650 0x6b6918 0x6b6921 0x4b8570 0xb11a05 0xb119d4 0xb12145 0xb1d087 0x4719c1
#	0x46bda4	internal/poll.runtime_pollWait+0x84			runtime/netpoll.go:343
#	0x4e1326	internal/poll.(*pollDesc).wait+0x26			internal/poll/fd_poll_runtime.go:84
#	0x4e2619	internal/poll.(*pollDesc).waitRead+0x279		internal/poll/fd_poll_runtime.go:89
#	0x4e2607	internal/poll.(*FD).Read+0x267				internal/poll/fd_unix.go:164
#	0x545a64	net.(*netFD).Read+0x24					net/fd_posix.go:55
#	0x5590c4	net.(*conn).Read+0x44					net/net.go:179
#	0x6b2e9a	crypto/tls.(*atLeastReader).Read+0x3a			crypto/tls/conn.go:805
#	0x50ddb7	bytes.(*Buffer).ReadFrom+0x97				bytes/buffer.go:211
#	0x6b307d	crypto/tls.(*Conn).readFromUntil+0xdd			crypto/tls/conn.go:827
#	0x6b064f	crypto/tls.(*Conn).readRecordOrCCS+0x24f		crypto/tls/conn.go:625
#	0x6b6917	crypto/tls.(*Conn).readRecord+0x157			crypto/tls/conn.go:587
#	0x6b6920	crypto/tls.(*Conn).Read+0x160				crypto/tls/conn.go:1369
#	0x4b856f	io.ReadAtLeast+0x8f					io/io.go:335
#	0xb11a04	io.ReadFull+0x64					io/io.go:354
#	0xb119d3	golang.org/x/net/http2.readFrameHeader+0x33		golang.org/x/net@v0.14.0/http2/frame.go:237
#	0xb12144	golang.org/x/net/http2.(*Framer).ReadFrame+0x84		golang.org/x/net@v0.14.0/http2/frame.go:498
#	0xb1d086	golang.org/x/net/http2.(*serverConn).readFrames+0x86	golang.org/x/net@v0.14.0/http2/server.go:818

1 @ 0x43e50e 0x44e286 0xafeeb3 0xb0af86 0x5c29fc 0x5c3225 0xb0365b 0xb03650 0x15cb6af 0x43e09b 0x4719c1
#	0xafeeb2	github.com/caddyserver/caddy/v2/cmd.cmdRun+0xcd2					github.com/caddyserver/caddy/v2@v2.7.4/cmd/commandfuncs.go:277
#	0xb0af85	github.com/caddyserver/caddy/v2/cmd.init.1.func2.WrapCommandFuncForCobra.func1+0x25	github.com/caddyserver/caddy/v2@v2.7.4/cmd/cobra.go:126
#	0x5c29fb	github.com/spf13/cobra.(*Command).execute+0x87b						github.com/spf13/cobra@v1.7.0/command.go:940
#	0x5c3224	github.com/spf13/cobra.(*Command).ExecuteC+0x3a4					github.com/spf13/cobra@v1.7.0/command.go:1068
#	0xb0365a	github.com/spf13/cobra.(*Command).Execute+0x5a						github.com/spf13/cobra@v1.7.0/command.go:992
#	0xb0364f	github.com/caddyserver/caddy/v2/cmd.Main+0x4f						github.com/caddyserver/caddy/v2@v2.7.4/cmd/main.go:65
#	0x15cb6ae	main.main+0xe										caddy/main.go:11
#	0x43e09a	runtime.main+0x2ba									runtime/proc.go:267

1 @ 0x43e50e 0x44e9c5 0x8ec085 0x4719c1
#	0x8ec084	github.com/caddyserver/certmagic.(*Cache).maintainAssets+0x304	github.com/caddyserver/certmagic@v0.19.2/maintain.go:67

...
```

A primeira linha, `goroutine profile: total 88`, nos diz o que estamos vendo e quantas goroutines há.

A lista de goroutines vem em seguida. Elas são agrupadas por seus call stacks em ordem decrescente de frequência.

Uma linha de goroutine tem esta sintaxe: `<count> @ <addresses...>`

A linha começa com a contagem das goroutines que têm o call stack associado. O símbolo `@` indica o início dos endereços de instrução de chamada, isto é, os ponteiros de função, que originaram a goroutine. Cada ponteiro é uma chamada de função, ou frame de chamada.

Você pode notar que muitas de suas goroutines compartilham o mesmo primeiro endereço de chamada. Esse é o `main` do seu programa, ou ponto de entrada. Algumas goroutines não terão origem ali porque programas têm várias funções `init()` e o runtime do Go também pode criar goroutines.

As linhas que seguem começam com `#` e são, na verdade, apenas comentários para o benefício do leitor. Elas contêm o stack trace atual da goroutine. O topo representa o topo da pilha, ou seja, a linha de código atualmente sendo executada. A base representa o fundo da pilha, ou o código que a goroutine inicialmente começou a executar.

O stack trace tem este formato:

```
<address> <package/func>+<offset> <filename>:<line>
```

O endereço é o ponteiro da função, depois você verá o nome do pacote e da função Go (com o nome do tipo associado, se for um método), e o offset de instrução dentro da função. Então talvez a informação mais útil: o arquivo e número da linha, no final.

### Full goroutine stack dump

Se mudarmos o parâmetro de query para `?debug=2`, obtemos um dump completo. Isso inclui um stack trace verboso de cada goroutine, e goroutines idênticas não são colapsadas. Essa saída pode ser muito grande em servidores ocupados, mas traz informações interessantes!

Vamos olhar uma que corresponde ao primeiro call stack acima (truncado):

```
goroutine 61961905 [IO wait, 1 minutes]:
internal/poll.runtime_pollWait(0x7f9a9a059eb0, 0x72)
	runtime/netpoll.go:343 +0x85
...
golang.org/x/net/http2.(*serverConn).readFrames(0xc001756f00)
	golang.org/x/net@v0.14.0/http2/server.go:818 +0x87
created by golang.org/x/net/http2.(*serverConn).serve in goroutine 61961902
	golang.org/x/net@v0.14.0/http2/server.go:930 +0x56a
```

Apesar da verbosidade, as informações mais úteis fornecidas de forma exclusiva por esse dump são a primeira e a última linha de cada goroutine.

A primeira linha contém o número da goroutine (61961905), o estado ("IO wait") e a duração ("1 minutes"):

- **Número da goroutine:** Sim, goroutines têm números! Mas eles não são expostos ao nosso código. Esses números são especialmente úteis em um stack trace, porque podemos ver qual goroutine criou esta (veja no final: "created by ... in goroutine 61961902"). A ferramenta mostrada abaixo ajuda a desenhar gráficos visuais disso.

- **Estado:** Isso mostra o que a goroutine está fazendo no momento. Alguns estados possíveis:
	- `running`: Executando código - ótimo!
	- `IO wait`: Esperando por rede. Não consome uma thread do sistema operacional porque está estacionada em um poller de rede não bloqueante.
	- `sleep`: Todos precisamos de mais disso.
	- `select`: Bloqueada em um select; esperando um case ficar disponível.
	- `select (no cases):` Bloqueada em um `select {}` vazio especificamente. O Caddy usa isso em seu `main` para continuar rodando porque os shutdowns são iniciados por outras goroutines.
	- `chan receive`: Bloqueada em uma recepção de canal (`<-ch`).
	- `semacquire`: Esperando adquirir um semáforo (primitiva de sincronização de baixo nível).
	- `syscall`: Executando uma syscall. Consome uma thread do sistema operacional.

- **Duração:** Quanto tempo a goroutine existe. Útil para encontrar bugs como leaks de goroutine. Por exemplo, se esperamos que todas as conexões de rede sejam fechadas após alguns minutos, o que significa encontrar muitas goroutines netconn vivas por horas?

### Interpretando dumps de goroutine

Sem olhar o código, o que podemos aprender sobre a goroutine acima?

Ela foi criada há apenas cerca de um minuto, está aguardando dados em um socket de rede e seu número de goroutine é bem alto (61961905).

Do primeiro dump (debug=1), sabemos que seu stack é executado com relativa frequência, e o grande número de goroutine combinado com a curta duração sugere que houve dezenas de milhões dessas goroutines de vida curta. Ela está em uma função chamada `pollWait` e seu histórico de chamadas inclui leitura de frames HTTP/2 a partir de uma conexão criptografada em rede que usa TLS.

Então, podemos deduzir que essa goroutine está atendendo uma requisição HTTP/2! Ela está esperando dados do cliente. Mais do que isso, sabemos que a goroutine que a criou não é uma das primeiras goroutines do processo porque ela também tem um número alto; encontrar essa goroutine no dump revela que ela foi criada para lidar com um novo stream HTTP/2 durante uma requisição existente. Em contraste, outras goroutines com números altos podem ter sido criadas por uma goroutine de número baixo (como 32), indicando uma conexão novinha em folha logo após uma chamada `Accept()` do socket.

Cada programa é diferente, mas ao depurar o Caddy, esses padrões tendem a se manter.

## Perfis de memória

Perfis de memória (ou heap) rastreiam alocações de heap, que são os principais consumidores de memória em um sistema. Alocações também são suspeitas comuns de problemas de desempenho porque alocar memória requer syscalls, que podem ser lentas.

Perfis de heap se parecem com perfis de goroutine em quase tudo, exceto pelo começo da linha superior. Aqui está um exemplo:

```
0: 0 [1: 4096] @ 0xb1fc05 0xb1fc4d 0x48d8d1 0xb1fce6 0xb184c7 0xb1bc8e 0xb41653 0xb4105c 0xb4151d 0xb23b14 0x4719c1
#	0xb1fc04	bufio.NewWriterSize+0x24					bufio/bufio.go:599
#	0xb1fc4c	golang.org/x/net/http2.glob..func8+0x6c				golang.org/x/net@v0.17.0/http2/http2.go:263
#	0x48d8d0	sync.(*Pool).Get+0xb0						sync/pool.go:151
#	0xb1fce5	golang.org/x/net/http2.(*bufferedWriter).Write+0x45		golang.org/x/net@v0.17.0/http2/http2.go:276
#	0xb184c6	golang.org/x/net/http2.(*Framer).endWrite+0xc6			golang.org/x/net@v0.17.0/http2/frame.go:371
#	0xb1bc8d	golang.org/x/net/http2.(*Framer).WriteHeaders+0x48d		golang.org/x/net@v0.17.0/http2/frame.go:1131
#	0xb41652	golang.org/x/net/http2.(*writeResHeaders).writeHeaderBlock+0xd2	golang.org/x/net@v0.17.0/http2/write.go:239
#	0xb4105b	golang.org/x/net/http2.splitHeaderBlock+0xbb			golang.org/x/net@v0.17.0/http2/write.go:169
#	0xb4151c	golang.org/x/net/http2.(*writeResHeaders).writeFrame+0x1dc	golang.org/x/net@v0.17.0/http2/write.go:234
#	0xb23b13	golang.org/x/net/http2.(*serverConn).writeFrameAsync+0x73	golang.org/x/net@v0.17.0/http2/server.go:851
```

O formato da primeira linha é o seguinte:

```
<live objects> <live memory> [<allocations>: <allocation memory>] @ <addresses...>
```

No exemplo acima, temos uma única alocação feita por `bufio.NewWriterSize()`, mas atualmente nenhum objeto vivo deste call stack.

Interessantemente, podemos inferir desse call stack que o pacote http2 usou um buffer pool de 4 KB para escrever frame(s) HTTP/2 para o cliente. Você frequentemente verá objetos em pool em perfis de memória Go se caminhos quentes foram otimizados para reutilizar alocações. Isso reduz novas alocações, e o perfil de heap pode ajudar você a saber se o pool está sendo usado corretamente!

## Perfis de CPU

Perfis de CPU ajudam você a entender onde o programa Go está gastando a maior parte do tempo agendado no processador.

No entanto, não há forma em texto puro para esses perfis, então na próxima seção usaremos comandos `go tool pprof` para ajudar a lê-los.

Para baixar um perfil de CPU, faça uma requisição para `/debug/pprof/profile?seconds=N`, onde N é o número de segundos durante os quais você quer coletar o perfil. Durante a coleta do perfil de CPU, o desempenho do programa pode ser levemente afetado. (Outros perfis praticamente não têm impacto de desempenho.)

Quando terminar, ele deve baixar um arquivo binário, apropriadamente chamado `profile`. Então precisamos examiná-lo.

## `go tool pprof`

Usaremos o analisador de perfis embutido do Go para ler o perfil de CPU como exemplo, mas você pode usá-lo com qualquer tipo de perfil.

Execute este comando (substituindo "profile" pelo caminho real do arquivo, se for diferente), que abre um prompt interativo:

<pre><code class="cmd bash">go tool pprof profile
File: caddy_master
Type: cpu
Time: Aug 29, 2022 at 8:47pm (MDT)
Duration: 30.02s, Total samples = 70.11s (233.55%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) </code></pre>

<aside class="tip">

Você pode usar este comando para examinar qualquer tipo de perfil, não apenas perfis de CPU. Os princípios são os mesmos para outros perfis e os conceitos se transferem.

</aside>

Isso é algo que você pode explorar. Digitar `help` mostra uma lista de comandos e `o` exibe as opções atuais. E, se você digitar `help <command>`, poderá obter informações sobre um comando específico.

Há muitos comandos, mas alguns comuns são:

- `top`: Mostra o que consumiu mais CPU. Você pode acrescentar um número como `top 20` para ver mais, ou uma regex para "focar" ou ignorar certos itens.
- `web`: Abre o grafo de chamadas no navegador. É uma ótima forma de ver visualmente o uso de CPU.
- `svg`: Gera uma imagem SVG do grafo de chamadas. É igual ao `web`, exceto que não abre o navegador e o SVG é salvo localmente.
- `tree`: Uma visão tabular do stack de chamadas.

Vamos começar com `top`. Vemos uma saída assim:

```
(pprof) top
Showing nodes accounting for 38.36s, 54.71% of 70.11s total
Dropped 785 nodes (cum <= 0.35s)
Showing top 10 nodes out of 196
      flat  flat%   sum%        cum   cum%
    10.97s 15.65% 15.65%     10.97s 15.65%  runtime/internal/syscall.Syscall6
     6.59s  9.40% 25.05%     36.65s 52.27%  runtime.gcDrain
     5.03s  7.17% 32.22%      5.34s  7.62%  runtime.(*lfstack).pop (inline)
     3.69s  5.26% 37.48%     11.02s 15.72%  runtime.scanobject
     2.42s  3.45% 40.94%      2.42s  3.45%  runtime.(*lfstack).push
     2.26s  3.22% 44.16%      2.30s  3.28%  runtime.pageIndexOf (inline)
     2.11s  3.01% 47.17%      2.56s  3.65%  runtime.findObject
     2.03s  2.90% 50.06%      2.03s  2.90%  runtime.markBits.isMarked (inline)
     1.69s  2.41% 52.47%      1.69s  2.41%  runtime.memclrNoHeapPointers
     1.57s  2.24% 54.71%      1.57s  2.24%  runtime.epollwait
```

Os 10 maiores consumidores de CPU estavam todos no runtime do Go -- em particular, muita garbage collection (lembre-se de que syscalls são usadas para liberar e alocar memória). Isso é um indício de que podemos reduzir alocações para melhorar o desempenho, e um perfil de heap seria útil.

OK, mas e se quisermos ver a utilização de CPU do nosso próprio código? Podemos ignorar padrões contendo "runtime" assim:

```
(pprof) top -runtime  
Active filters:
   ignore=runtime
Showing nodes accounting for 0.92s, 1.31% of 70.11s total
Dropped 160 nodes (cum <= 0.35s)
Showing top 10 nodes out of 243
      flat  flat%   sum%        cum   cum%
     0.17s  0.24%  0.24%      0.28s   0.4%  sync.(*Pool).getSlow
     0.11s  0.16%   0.4%      0.11s  0.16%  github.com/prometheus/client_golang/prometheus.(*histogram).observe (inline)
     0.10s  0.14%  0.54%      0.23s  0.33%  github.com/prometheus/client_golang/prometheus.(*MetricVec).hashLabels
     0.10s  0.14%  0.68%      0.12s  0.17%  net/textproto.CanonicalMIMEHeaderKey
     0.10s  0.14%  0.83%      0.10s  0.14%  sync.(*poolChain).popTail
     0.08s  0.11%  0.94%      0.26s  0.37%  github.com/prometheus/client_golang/prometheus.(*histogram).Observe
     0.07s   0.1%  1.04%      0.07s   0.1%  internal/poll.(*fdMutex).rwlock
     0.07s   0.1%  1.14%      0.10s  0.14%  path/filepath.Clean
     0.06s 0.086%  1.23%      0.06s 0.086%  context.value
     0.06s 0.086%  1.31%      0.06s 0.086%  go.uber.org/zap/buffer.(*Buffer).AppendByte
```

Bem, está claro que as métricas do Prometheus também são um grande consumidor, mas você notará que, no total, elas representam ordens de magnitude menos que a GC acima. A diferença gritante sugere que deveríamos focar em reduzir a GC.

<aside class="tip">

É importante notar que perfis de CPU obtêm suas medições por amostragem intermitente, e as amostras nunca serão capturadas com frequência maior que a taxa de amostragem, que é de 10ms por padrão. É por isso que você não verá durações cumulativas menores que 10ms (elas provavelmente são menores, mas arredondadas para cima). Para tempos mais específicos, você pode fazer um execution trace, que não usa amostragem. (TODO: adicionar seção sobre tracing.)

</aside>

Vamos usar `q` para sair desse perfil e usar o mesmo comando no perfil de heap:

```
(pprof) top
Showing nodes accounting for 22259.07kB, 81.30% of 27380.04kB total
Showing top 10 nodes out of 102
      flat  flat%   sum%        cum   cum%
   12300kB 44.92% 44.92%    12300kB 44.92%  runtime.allocm
 2570.01kB  9.39% 54.31%  2570.01kB  9.39%  bufio.NewReaderSize
 2048.81kB  7.48% 61.79%  2048.81kB  7.48%  runtime.malg
 1542.01kB  5.63% 67.42%  1542.01kB  5.63%  bufio.NewWriterSize
 ...
 ```

Bingo. Quase metade da memória é alocada estritamente para buffers de leitura e escrita por causa do uso do pacote bufio. Portanto, podemos inferir que otimizar nosso código para reduzir buffering seria muito benéfico. (O [patch associado no Caddy](https://github.com/caddyserver/caddy/pull/4978) faz exatamente isso.)

### Visualizações

Se, em vez disso, executarmos os comandos `svg` ou `web`, obteremos uma visualização do perfil:

![Visualização de perfil de CPU](/old/resources/images/profile.png)

Esse é um perfil de CPU, mas gráficos semelhantes estão disponíveis para outros tipos de perfil.

Para aprender a ler esses gráficos, leia a [documentação do pprof](https://github.com/google/pprof/blob/main/doc/README.md#interpreting-the-callgraph).

### Comparando perfis

Depois de fazer uma mudança de código, você pode comparar o antes e o depois usando uma análise de diferença ("diff"). Aqui está um diff do heap:

<pre><code class="cmd bash">go tool pprof -diff_base=before.prof after.prof
File: caddy
Type: inuse_space
Time: Aug 29, 2022 at 1:21am (MDT)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) top
Showing nodes accounting for -26.97MB, 49.32% of 54.68MB total
Dropped 10 nodes (cum <= 0.27MB)
Showing top 10 nodes out of 137
      flat  flat%   sum%        cum   cum%
  -27.04MB 49.45% 49.45%   -27.04MB 49.45%  bufio.NewWriterSize
      -2MB  3.66% 53.11%       -2MB  3.66%  runtime.allocm
    1.06MB  1.93% 51.18%     1.06MB  1.93%  github.com/yuin/goldmark/util.init
    1.03MB  1.89% 49.29%     1.03MB  1.89%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.glob..func2
       1MB  1.84% 47.46%        1MB  1.84%  bufio.NewReaderSize
      -1MB  1.83% 49.29%       -1MB  1.83%  runtime.malg
       1MB  1.83% 47.46%        1MB  1.83%  github.com/caddyserver/caddy/v2/modules/caddyhttp/reverseproxy.cloneRequest
      -1MB  1.83% 49.29%       -1MB  1.83%  net/http.(*Server).newConn
   -0.55MB  1.00% 50.29%    -0.55MB  1.00%  html.populateMaps
    0.53MB  0.97% 49.32%     0.53MB  0.97%  github.com/alecthomas/chroma.TypeRemappingLexer</code></pre>

Como você pode ver, reduzimos as alocações de memória em cerca de metade!

Diffs também podem ser visualizados:

![Visualização de diff de perfil de CPU](/old/resources/images/profile-diff.png)

Isso torna muito óbvio como as mudanças afetaram o desempenho de certas partes do programa.

## Leitura adicional

Há muito a dominar em profiling de programas, e nós apenas arranhamos a superfície.

Para realmente colocar o "pro" em "profiling", considere estes recursos:

- [Documentação do pprof](https://github.com/google/pprof/blob/main/doc/README.md)
- [Uso real de perfis com o Caddy](https://github.com/caddyserver/caddy/pull/4978)
- [Performance no wiki do Go](https://github.com/golang/go/wiki/Performance)
- [O pacote `net/http/pprof`](https://pkg.go.dev/net/http/pprof)
