---
title: Convenções
---

# Convenções

O ecossistema do Caddy segue algumas convenções para manter tudo consistente e intuitivo em toda a plataforma.

- [Endereços de rede](#network-addresses)
- [Placeholders](#placeholders)
- [Locais de arquivos](#file-locations)
  - [Diretório de dados](#data-directory)
  - [Diretório de configuração](#configuration-directory)
- [Durações](#durations)

<a id="network-addresses"></a>
## Endereços de rede

Ao especificar um endereço de rede para conectar ou vincular, o Caddy aceita uma string no seguinte formato:

```
network/address
```

A parte de network é opcional (padrão `tcp`) e pode ser qualquer coisa que a função [`net.Dial` do Go](https://pkg.go.dev/net#Dial) reconheça. Se uma network for especificada, uma única barra `/` deve separar as partes network e address.

A network pode ser qualquer uma das seguintes; as com sufixo `4` ou `6` são apenas IPv4 ou IPv6, respectivamente:

- TCP: `tcp`, `tcp4`, `tcp6`
- UDP: `udp`, `udp4`, `udp6`
- IP: `ip`, `ip4`, `ip6`
- Unix: `unix`, `unixgram`, `unixpacket`

A parte address pode assumir qualquer uma destas formas:

- `host`
- `host:port`
- `:port`
- `[ipv6%zone]:port`
- `/path/to/unix/socket`
- `/path/to/unix/socket|0200`

O host pode ser qualquer hostname, nome de domínio resolvível ou endereço IP.

No caso de endereços IPv6, o endereço deve estar entre colchetes `[]`. O identificador de zona (começando com `%`) é opcional e frequentemente usado para endereços link-local.

A porta pode ser um único valor (`:8080`) ou um intervalo inclusivo (`:8080-8085`). Um intervalo de portas será expandido em endereços individuais. Nem todos os campos de configuração aceitam intervalos de portas. A porta especial `:0` significa qualquer porta disponível.

Um caminho de socket Unix só é aceitável quando se usa um tipo de rede `unix*`. A barra que separa a rede e o endereço não faz parte do caminho.

Quando um socket Unix é usado como endereço de bind, você pode opcionalmente especificar um modo de permissão de arquivo após o caminho, separado por uma barra vertical `|`. O padrão é `0200` (octal), isto é, `u=w,g=,o=` (simbólico). O zero à esquerda é opcional.

Exemplos válidos:

```
:8080
127.0.0.1:8080
localhost:8080
localhost:8080-8085
tcp/localhost:8080
tcp/localhost:8080-8085
udp/localhost:9005
[::1]:8080
tcp6/[fe80::1%eth0]:8080
unix//path/to/socket
unix//path/to/socket|0200
```

<aside class="tip">

Endereços de rede do Caddy não são URLs. URLs acoplam as camadas inferiores e superiores do [modelo OSI <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OSI_model#Layer_architecture), mas o Caddy frequentemente usa endereços de rede independentemente de uma aplicação específica, então combinar os dois seria problemático. No Caddy, endereços de rede se referem precisamente a recursos que podem ser conectados ou vinculados nas camadas L3-L5, enquanto URLs combinam L3-L7, o que é demais. Um endereço de rede exige que host+porta e path sejam mutuamente exclusivos, mas URLs não. Endereços de rede às vezes suportam intervalos de portas, mas URLs não.

</aside>

## Placeholders

A configuração do Caddy suporta o uso de _placeholders_. Usar placeholders é uma forma simples de injetar valores dinâmicos em uma configuração estática.

<aside class="tip">

Placeholders são uma ideia parecida com variáveis em outros softwares. Por exemplo, [nginx tem variáveis <img src="/old/resources/images/external-link.svg" class="external-link">](https://nginx.org/en/docs/varindex.html) como `$uri` e `$document_root`, enquanto o equivalente do Caddy seria [`{http.request.uri}`](/docs/json/apps/http/#docs) e [`{http.vars.root}`](/docs/caddyfile/directives/root).

</aside>

Placeholders são delimitados em ambos os lados por chaves `{ }` e contêm o identificador dentro, por exemplo: `{foo.bar}`. A chave de abertura pode ser escapada com `\{like.this}` para evitar a substituição. Os identificadores de placeholder normalmente são namespaced com pontos para evitar colisões entre módulos.

Quais placeholders estão disponíveis depende do contexto. Nem todos os placeholders estão disponíveis em todas as partes da configuração. Por exemplo, o [app HTTP define placeholders](/docs/json/apps/http/#docs) que só estão disponíveis em áreas da configuração relacionadas ao tratamento de requisições HTTP. Quando uma requisição passa pelo handler [`reverse_proxy`](/docs/json/apps/http/servers/routes/handle/reverse_proxy/#docs), o handler define vários placeholders específicos de proxy. Esses placeholders podem ser referenciados durante o proxy e depois dele, em `handle_response`, por exemplo ao definir cabeçalhos de resposta ou enriquecer logs de acesso.

Os placeholders a seguir estão sempre disponíveis (globais):

Placeholder | Descrição
------------|-------------
`{env.*}` | Variável de ambiente; exemplo: `{env.HOME}`
`{file.*}` | Conteúdo de um arquivo; exemplo: `{file./path/to/secret.txt}`
`{system.hostname}` | O hostname local do sistema
`{system.slash}` | O separador de caminho do sistema
`{system.os}` | O sistema operacional
`{system.arch}` | A arquitetura do sistema
`{system.wd}` | O diretório de trabalho atual
`{time.now}` | A hora atual como uma struct Go Time
`{time.now.http}` | A hora atual no formato usado em [cabeçalhos HTTP <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Last-Modified)
`{time.now.unix}` | A hora atual como timestamp Unix em segundos
`{time.now.unix_ms}` | A hora atual como timestamp Unix em milissegundos
`{time.now.common_log}` | A hora atual no formato Common Log
`{time.now.year}` | O ano atual no formato YYYY

Nem todos os campos de configuração suportam placeholders, mas a maioria suporta onde você esperaria. O suporte a placeholders precisa ter sido adicionado explicitamente nesses campos. Autores de plugins podem [ler este artigo](/docs/extending-caddy/placeholders) para aprender como adicionar suporte a placeholders em seus próprios módulos.

<a id="file-locations"></a>
## Locais de arquivos

Esta seção contém informações sobre onde encontrar vários arquivos. Os caminhos de arquivo e diretório descritos aqui são, no máximo, padrões; alguns podem ser substituídos.

### Seus arquivos de configuração

Não existe um lugar único e convencional para você colocar seus arquivos de configuração. Coloque-os onde fizer mais sentido para você.

<aside class="tip">

A única exceção a isso pode ser um arquivo chamado `Caddyfile` no diretório de trabalho atual, que o comando caddy tenta usar por conveniência se nenhum outro arquivo de configuração for especificado.

</aside>


Distribuições que incluem um arquivo de configuração padrão devem documentar onde esse arquivo está, mesmo que isso pareça óbvio para os mantenedores do pacote/distro. Na maioria das instalações Linux, o Caddyfile será encontrado em `/etc/caddy/Caddyfile`.

<a id="data-directory"></a>
### Diretório de dados

O Caddy armazena certificados TLS e outros ativos importantes em um diretório de dados, que é respaldado pelo [módulo de armazenamento configurado](/docs/json/storage/) (padrão: sistema de arquivos local).

Se a variável de ambiente `XDG_DATA_HOME` estiver definida, o caminho será `$XDG_DATA_HOME/caddy`.

Caso contrário, o caminho varia por plataforma, seguindo as convenções do sistema operacional:

OS | Caminho do diretório de dados
---|---------------------
**Linux, BSD** | `$HOME/.local/share/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`
**Android** | `$HOME/caddy` (ou `/sdcard/caddy`)

Todos os outros sistemas operacionais usam o caminho do diretório Linux/BSD.

**O diretório de dados não deve ser tratado como cache.** Seu conteúdo **não** é efêmero nem existe apenas para desempenho. O Caddy armazena certificados TLS, chaves privadas, OCSP staples e outras informações necessárias nesse diretório de dados. Ele não deve ser apagado sem entender as implicações.

É crucial que esse diretório seja persistente e gravável pelo Caddy.

<a id="configuration-directory"></a>
### Diretório de configuração

É aqui que o Caddy pode armazenar certas configurações em disco. Mais notavelmente, ele persiste a última configuração ativa (por padrão) nesse diretório para permitir retomada fácil depois com [`caddy run --resume`](/docs/command-line#caddy-run).

<aside class="tip">

O diretório de configuração *não* é onde você precisa guardar [seus arquivos de configuração](#your-config-files). Embora você possa fazer isso.

</aside>


Se a variável de ambiente `XDG_CONFIG_HOME` estiver definida, o caminho será `$XDG_CONFIG_HOME/caddy`.

Caso contrário, o caminho varia por plataforma, seguindo as convenções do sistema operacional:

OS | Caminho do diretório de configuração
---|---------------------
**Linux, BSD** | `$HOME/.config/caddy`
**Windows** | `%AppData%\Caddy`
**macOS** | `$HOME/Library/Application Support/Caddy`
**Plan 9** | `$HOME/lib/caddy`

Todos os outros sistemas operacionais usam o caminho do diretório Linux/BSD.

É crucial que esse diretório seja persistente e gravável pelo Caddy.

<a id="durations"></a>
## Durações

Strings de duração são usadas com frequência na configuração do Caddy. Elas seguem o mesmo formato da sintaxe [`time.ParseDuration` do Go](https://golang.org/pkg/time/#ParseDuration), exceto que você também pode usar `d` para dia (assumimos 1 dia = 24 horas por simplicidade). As unidades válidas são:

- `ns` (nanosegundo)
- `us`/`µs` (microssegundo)
- `ms` (milissegundo)
- `s` (segundo)
- `m` (minuto)
- `h` (hora)
- `d` (dia)

Exemplos:

- `250ms`
- `5s`
- `1.5h`
- `2h45m`
- `90d`

Na [configuração JSON](/docs/json/), valores de duração também podem ser inteiros que representam nanossegundos.
