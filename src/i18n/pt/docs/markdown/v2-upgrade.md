---
title: Atualizando para o Caddy 2
---

Guia de atualização
=================

O Caddy 2 é uma base de código totalmente nova, escrita do zero, para melhorar o Caddy 1. O Caddy 2 não é compatível com versões anteriores do Caddy 1. Mas não se preocupe: para a maioria das configurações básicas, não há muita diferença. Este guia vai ajudar você a fazer a transição da forma mais fácil possível.

Este guia não vai explorar em detalhe os novos recursos disponíveis -- que, aliás, são realmente muito bons; você deve [aprendê-los](/docs/getting-started) -- o objetivo aqui é apenas colocar você rapidamente em funcionamento no Caddy 2.

- [Pontos principais](#high-order-bits)
- [Passos](#steps)
- [HTTPS e portas](#https-and-ports)
- [Linha de comando](#command-line)
- [Caddyfile](#caddyfile)
	- [Mudanças principais](#primary-changes)
	- [basicauth](#basicauth)
	- [browse](#browse)
	- [errors](#errors)
	- [ext](#ext)
	- [fastcgi](#fastcgi)
	- [gzip](#gzip)
	- [header](#header)
	- [log](#log)
	- [proxy](#proxy)
	- [redir](#redir)
	- [rewrite](#rewrite)
	- [root](#root)
	- [status](#status)
	- [templates](#templates)
	- [tls](#tls)
- [Arquivos de serviço](#service-files)
- [Plugins](#plugins)
- [Obter ajuda](#getting-help)

<a id="high-order-bits"></a>
## Pontos principais

- "Caddy 2" ainda é chamado apenas de `caddy`. Podemos usar "Caddy 2" para esclarecer qual versão está sendo mencionada e tornar a transição menos confusa.
- A maioria dos usuários só precisará substituir o binário `caddy` e a configuração atualizada do `Caddyfile` (depois de testar que tudo funciona).
- Talvez seja melhor entrar no Caddy 2 sem carregar suposições do Caddy 1.
- Talvez você não consiga replicar perfeitamente sua configuração de nicho do v1 no v2. Geralmente, há uma boa razão para isso.
- A linha de comando não é mais usada para configurar o servidor.
- Variáveis de ambiente não são mais necessárias para configuração.
- A forma principal de fornecer configuração ao Caddy 2 é por meio da [API](/docs/api), mas o comando [`caddy`](/docs/command-line) também pode ser usado.
- Você deve saber que a linguagem nativa de configuração do Caddy 2 é [JSON](/docs/json/), e que o Caddyfile é apenas outro [config adapter](/docs/config-adapters) que converte para JSON para você. Casos extremamente customizados/avançados podem exigir JSON, já que nem toda configuração possível pode ser expressa pelo Caddyfile.
- O Caddyfile é em grande parte o mesmo, mas também muito mais poderoso; as diretivas mudaram.

<a id="steps"></a>
## Passos

1. Familiarize-se com o Caddy 2 fazendo nosso tutorial [Primeiros passos](/docs/getting-started).
2. Faça o passo 1 se ainda não o fez. Sério -- não dá para enfatizar o quanto é importante pelo menos saber usar o Caddy 2. (E é mais divertido!)
3. Use o guia abaixo para adaptar seus comandos `caddy`.
4. Use o guia abaixo para adaptar seu Caddyfile.
5. Teste sua nova configuração localmente ou em staging.
6. Teste, teste, teste de novo
7. Implante e divirta-se!

<a id="https-and-ports"></a>
## HTTPS e portas

A porta padrão do Caddy não é mais `:2015`. A porta padrão do Caddy 2 é `:443` ou, se nenhum hostname/IP for conhecido, a porta `:80`. Você sempre pode customizar as portas na sua configuração.

O protocolo padrão do Caddy 2 é [_sempre_ HTTPS se um hostname ou IP for conhecido](/docs/automatic-https#overview). Isso é diferente do Caddy 1, em que apenas domínios com aparência pública usavam HTTPS por padrão. Agora, _todo_ site usa HTTPS (a menos que você desative isso especificando explicitamente a porta `:80` ou `http://`).

Endereços IP e domínios localhost receberão certificados de uma [CA local incorporada e confiável localmente](/docs/automatic-https#local-https). Todos os outros domínios usarão ZeroSSL ou Let's Encrypt. (Tudo isso é configurável.)

A estrutura de storage dos certificados e dos recursos ACME mudou. O Caddy 2 provavelmente obterá novos certificados para seus sites; mas, se você tiver muitos certificados, poderá migrá-los manualmente caso isso não aconteça automaticamente. Veja os issues [#2955](https://github.com/caddyserver/caddy/issues/2955) e [#3124](https://github.com/caddyserver/caddy/issues/3124) para detalhes.

<a id="command-line"></a>
## Linha de comando

O comando `caddy` agora é `caddy run`.

Todas as flags de linha de comando são diferentes. Remova-as; toda a configuração do servidor agora existe dentro do documento de configuração real (normalmente Caddyfile ou JSON). Você provavelmente encontrará o que precisa na [estrutura JSON](/docs/json/) ou nas [opções globais do Caddyfile](/docs/caddyfile/options) para substituir a maioria das flags da linha de comando do v1.

Um comando como `caddy -conf ../Caddyfile` se tornaria `caddy run --config ../Caddyfile`.

Como antes, se o seu Caddyfile estiver na pasta atual, o Caddy o encontrará e usará automaticamente; você não precisa usar a flag `--config` nesse caso.

Os sinais são em grande parte os mesmos, exceto que USR1 e USR2 não são mais suportados. Use o comando [`caddy reload`](/docs/command-line#caddy-reload) ou a [API](/docs/api) para carregar nova configuração.

Executar `caddy` sem nenhuma configuração costumava iniciar um servidor simples de arquivos. O equivalente no Caddy 2 é [`caddy file-server`](/docs/command-line#caddy-file-server).

Variáveis de ambiente não são mais relevantes, exceto `HOME` (e, opcionalmente, quaisquer variáveis `XDG_*` que você definir). O `CADDYPATH` é [substituído pelas convenções do sistema operacional](/docs/conventions#file-locations).

## Caddyfile

O [Caddyfile v2](/docs/caddyfile/concepts) é muito parecido com o que você já conhece. A principal coisa que você precisará fazer é mudar suas diretivas.

⚠️ **Não deixe de ler as novas diretivas!** Especialmente se sua configuração for mais avançada, há muitos detalhes a considerar. Essas dicas vão deixar você majoritariamente adaptado bem rápido, mas leia a documentação completa de cada diretiva para entender as implicações da atualização. E, claro, sempre teste suas configurações minuciosamente antes de colocá-las em produção.

#<a id="primary-changes"></a>
<a id="primary-changes"></a>
### Mudanças principais

- Se você estiver servindo arquivos estáticos, precisará adicionar uma [`diretiva file_server`](/docs/caddyfile/directives/file_server), já que o Caddy 2 não assume isso por padrão. O Caddy 2 também não faz sniff de MIME por padrão, por motivos de segurança; se um Content-Type estiver faltando, talvez você precise definir o cabeçalho manualmente usando a diretiva [header](/docs/caddyfile/directives/header).

- No v1, você só podia filtrar (ou "combinar") diretivas pelo path da requisição. No v2, o [request matching](/docs/caddyfile/matchers) é muito mais poderoso. Quaisquer diretivas do v2 que adicionem middleware à cadeia do handler HTTP ou que manipulem a requisição/resposta HTTP de qualquer forma aproveitam essa nova funcionalidade de matching. [Leia mais sobre os request matchers do v2.](/docs/caddyfile/matchers) Você vai precisar entendê-los para dar sentido ao Caddyfile v2.

- Embora muitos [placeholders](/docs/conventions#placeholders) sejam os mesmos, muitos mudaram, e agora existem [muitos novos](/docs/modules/http#docs), incluindo [atalhos para o Caddyfile](/docs/caddyfile/concepts#placeholders).

- Os logs do Caddy 2 são todos estruturados, e o formato padrão é JSON. Todos os níveis de log podem simplesmente ir para o mesmo log para processamento (mas você pode personalizar isso se precisar).

- Onde no Caddy 1 você combinava requisições por prefixo de path, no Caddy 2 o matching de path é exato por padrão. Se quiser combinar um prefixo como `/foo/`, você precisará de `/foo/*` no Caddy 2.

Listaremos aqui algumas das diretivas v1 mais comuns e descreveremos como convertê-las para uso no Caddyfile v2.

⚠️ **O fato de uma diretiva v1 não aparecer nesta página não significa que o v2 não consiga fazer aquilo!** Algumas diretivas v1 não são necessárias, não traduzem bem ou são atendidas de outras formas no v2. Para algumas customizações avançadas, talvez você precise descer para o JSON para obter o que quer. Explore [nossa documentação](/docs/caddyfile) para encontrar o que precisa!

### basicauth

A autenticação HTTP Basic ainda é configurada com a diretiva [`basic_auth`](/docs/caddyfile/directives/basic_auth). No entanto, a configuração do Caddy 2 não aceita senhas em texto puro. Você precisa gerar hash delas, e o comando [`caddy hash-password`](/docs/command-line#caddy-hash-password) pode ajudar.

- **v1:**
```
basicauth /secret/ Bob hiccup
```

- **v2:**
```caddy-d
basic_auth /secret/* {
	Bob JDJhJDEwJEVCNmdaNEg2Ti5iejRMYkF3MFZhZ3VtV3E1SzBWZEZ5Q3VWc0tzOEJwZE9TaFlZdEVkZDhX
}
```

### browse

Navegação de arquivos agora é habilitada pela diretiva [`file_server`](/docs/caddyfile/directives/file_server).

- **v1:**
```
browse /subfolder/
```
- **v2:**
```caddy-d
file_server /subfolder/* browse
```

### errors

Páginas de erro personalizadas podem ser feitas com [`handle_errors`](/docs/caddyfile/directives/handle_errors).

- **v1:**

```
errors {
	404 404.html
	500 500.html
}
```

- **v2:**

```
handle_errors {
	rewrite /{err.status_code}.html
	file_server
}
```

### ext

Extensões implícitas de arquivo podem ser feitas com [`try_files`](/docs/caddyfile/directives/try_files).

- **v1:** `ext .html`
- **v2:** `try_files {path}.html {path}`

### fastcgi

Supondo que você esteja servindo PHP, o equivalente no v2 é [`php_fastcgi`](/docs/caddyfile/directives/php_fastcgi).

- **v1:**
```
fastcgi / localhost:9005 php
```
- **v2:**
```caddy-d
php_fastcgi localhost:9005
```

Observe que a diretiva `fastcgi` do v1 fazia muita coisa por baixo dos panos, incluindo tentar arquivos no disco, reescrever requisições e até redirecionar. A diretiva `php_fastcgi` do v2 também faz essas coisas para você, mas a documentação mostra sua [forma expandida](/docs/caddyfile/directives/php_fastcgi#expanded-form), que você pode modificar se suas necessidades forem diferentes.

Não há necessidade de preset `php` no v2, já que a diretiva `php_fastcgi` assume PHP por padrão. Uma linha como `php_fastcgi 127.0.0.1:9000 php` fará o reverse proxy pensar que existe um segundo backend chamado `php`, levando a erros de conexão.

As subdiretivas são diferentes no v2 -- você provavelmente não precisará de nenhuma para PHP.

### gzip

Uma única diretiva [`encode`](/docs/caddyfile/directives/encode) agora é usada para todas as codificações de resposta, incluindo múltiplos formatos de compressão.

- **v1:**
```
gzip
```
- **v2:**
```caddy-d
encode gzip
```

Curiosidade: o Caddy 2 também suporta `zstd` (mas nenhum navegador suporta ainda).

### header

[Em grande parte inalterada](/docs/caddyfile/directives/header), mas agora muito mais poderosa, já que pode fazer substituições de substring no v2.

- **v1:**
```
header / Strict-Transport-Security max-age=31536000;
```
- **v2:**
```caddy-d
header Strict-Transport-Security max-age=31536000;
```

### log

Habilita logging de acesso; a diretiva [`log`](/docs/caddyfile/directives/log) ainda pode ser usada no v2, mas todos os logs são estruturados, codificados como JSON, por padrão.

A forma recomendada de habilitar logging de acesso é simplesmente:

```caddy-d
log
```

que emite logs estruturados para stderr. (Você também pode emitir para um arquivo ou socket de rede; veja a documentação da diretiva [`log`](/docs/caddyfile/directives/log).)

Por padrão, os logs serão no formato JSON [estruturado](/docs/logging). Se você ainda precisar de logs no Common Log Format (CLF) por motivos legados, pode usar o plugin [`transform-encoder`](https://github.com/caddyserver/transform-encoder).

### proxy

O equivalente no v2 é [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy).

Mudanças notáveis nas subdiretivas: `header_upstream` e `header_downstream` passaram a ser `header_up` e `header_down`, respectivamente; e as subdiretivas relacionadas a balanceamento de carga são prefixadas com `lb_`.

Outra diferença significativa é que o proxy do v2 passa todos os cabeçalhos de entrada por padrão (incluindo o cabeçalho `Host`) e define o cabeçalho `X-Forwarded-For`. Em outras palavras, o modo "transparent" do v1 é basicamente o padrão no v2 (mas, se você precisar de outros cabeçalhos como X-Real-IP, terá que defini-los manualmente). Você ainda pode sobrescrever/customizar o cabeçalho `Host` usando a subdiretiva `header_up`.

Proxy de websocket "simplesmente funciona" no v2; não há necessidade de "habilitar" websockets como no v1.

A subdiretiva `without` foi removida porque [gambiarras de rewrite](#rewrite) não são mais necessárias no v2 graças ao suporte melhorado a matchers.

- **v1:**
```
proxy / localhost:9005
```
- **v2:**
```caddy-d
reverse_proxy localhost:9005
```

### redir

[Inalterada](/docs/caddyfile/directives/redir), exceto por alguns detalhes sobre o argumento opcional de código de status. A maioria das configurações não precisará de alterações.

- **v1:** `redir https://example.com{uri}`
- **v2:** `redir https://example.com{uri}`

### rewrite

A semântica da reescrita de requisições ("internal redirecting") mudou um pouco. Se você usava uma chamada "rewrite hack" no v1 como forma de combinar requisições com algo além de um prefixo simples de path, isso é completamente desnecessário no v2.

A [nova diretiva `rewrite`](/docs/caddyfile/directives/rewrite) é muito simples, mas muito poderosa, porque a maior parte de sua complexidade é tratada por [matchers](/docs/caddyfile/matchers) no v2:

- **v1:**
```
rewrite {
	if {>User-Agent} has mobile
	to /mobile{uri}
}
```
- **v2:**
```caddy-d
@mobile {
	header User-Agent *mobile*
}
rewrite @mobile /mobile{uri}
```

Observe como simplesmente usamos os [matcher tokens](/docs/caddyfile/matchers) normais do Caddy 2; isso não é mais um caso especial para esta diretiva.

Comece removendo todas as rewrite hacks; transforme-as em [matchers nomeados](/docs/caddyfile/concepts#named-matchers) em vez disso. Avalie cada `rewrite` do v1 para ver se ele realmente é necessário no v2. Dica: um Caddyfile v1 que usa `rewrite` para adicionar um prefixo de path e depois usa `proxy` com `without` para remover esse mesmo prefixo é uma rewrite hack e pode ser eliminado.

Você pode achar as novas diretivas [`route`](/docs/caddyfile/directives/route) e [`handle`](/docs/caddyfile/directives/handle) úteis para ter mais controle sobre lógica avançada de roteamento.

### root

[Inalterada](/docs/caddyfile/directives/root).

Lembre-se de adicionar uma [`diretiva file_server`](/docs/caddyfile/directives/file_server) se estiver servindo arquivos estáticos, já que o Caddy 2 não assume isso por padrão, enquanto no v1 isso sempre ficava habilitado.

### status

O equivalente no v2 é [`respond`](/docs/caddyfile/directives/respond), que também pode escrever um corpo de resposta.

- **v1:**
```
status 404 /secrets/
```
- **v2:**
```caddy-d
respond /secrets/* 404
```

### templates

A sintaxe geral da diretiva [`templates`](/docs/caddyfile/directives/templates) não mudou, mas as ações/funções reais de template são diferentes e muito melhores. Por exemplo, templates podem incluir arquivos, renderizar markdown, fazer sub-requisições internas, fazer parse de front matter e mais!

[Veja a documentação](/docs/modules/http.handlers.templates) para detalhes sobre as novas funções.

- **v1:** `templates`
- **v2:** `templates`

### tls

Os fundamentos da diretiva [`tls`](/docs/caddyfile/directives/tls) não mudaram, por exemplo ao especificar seu próprio certificado e chave:

- **v1:** `tls cert.pem key.pem`
- **v2:** `tls cert.pem key.pem`

Mas a [lógica de auto-HTTPS](/docs/automatic-https) do Caddy _mudou_, então fique atento a isso!

Os nomes dos conjuntos de cifras também mudaram.

Uma configuração comum no Caddy 2 é usar `tls internal` para ele servir um certificado confiável localmente para um hostname de desenvolvimento que não seja `localhost` ou um IP.

A maioria dos sites não vai precisar dessa diretiva de forma alguma.

<a id="service-files"></a>
## Arquivos de serviço

Recomendamos usar [um de nossos arquivos oficiais de serviço systemd](/docs/running#linux-service) para implantações do Caddy.

Se você precisar de um arquivo de serviço customizado, baseie-o no nosso. Eles foram cuidadosamente ajustados ao que é necessário por boas razões! Certifique-se de customizar o seu, se necessário.

## Plugins

Plugins escritos para o v1 não são automaticamente compatíveis com o v2. Muitos plugins do v1 nem sequer são necessários no v2. Por outro lado, o v2 é muito mais extensível e flexível que o v1!

Se quiser escrever um plugin para o Caddy 2, [aprenda a escrever um módulo Caddy](/docs/extending-caddy).

### Compilando o Caddy 2 com plugins

O Caddy 2 pode ser baixado com plugins na [página interativa de download](/download). Alternativamente, você pode [compilar o Caddy você mesmo](/docs/build) usando `xcaddy` e escolher quais plugins incluir. O `xcaddy` automatiza as instruções do arquivo [main.go](https://github.com/caddyserver/caddy/blob/master/cmd/caddy/main.go) do Caddy.

<a id="getting-help"></a>
## Obter ajuda

Se você estiver com dificuldade para fazer o Caddy funcionar, dê uma olhada primeiro na documentação do nosso site. Reserve um tempo para tentar coisas novas e entender o que está acontecendo - o v2 é bem diferente do v1 em muitos aspectos (mas também é bem familiar)!

Se ainda precisar de ajuda, participe de [nossa comunidade](https://caddy.community)! Você pode descobrir que ajudar outras pessoas é a melhor forma de ajudar a si mesmo também.
