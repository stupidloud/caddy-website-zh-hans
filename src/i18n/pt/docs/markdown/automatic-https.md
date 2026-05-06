---
title: "HTTPS Automático"
---

# HTTPS Automático

**Caddy foi o primeiro servidor web a usar HTTPS automaticamente _e por padrão_.**

O HTTPS automático provisiona certificados TLS para todos os seus sites e os mantém renovados. Ele também redireciona HTTP para HTTPS para você! O Caddy usa padrões seguros e modernos -- sem tempo de inatividade, configuração extra ou ferramentas separadas.

<aside class="tip">
	Caddy inovou na tecnologia de HTTPS automático; fazemos isso desde o primeiro dia em que foi viável, em 2015. A lógica de automação HTTPS do Caddy é a mais madura e robusta do mundo.
</aside>

Aqui está um vídeo de 28 segundos mostrando como funciona:

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**Menu:**

- [Visão Geral](#overview)
- [Ativação](#activation)
- [Efeitos](#effects)
- [Requisitos de Nome de Host](#hostname-requirements)
- [HTTPS Local](#local-https)
- [Testes](#testing)
- [Desafios ACME](#acme-challenges)
- [TLS Sob Demanda (On-Demand)](#on-demand-tls)
- [Erros](#errors)
- [Armazenamento](#storage)
- [Certificados Wildcard](#wildcard-certificates)
- [Encrypted ClientHello (ECH)](#encrypted-clienthello-ech)



<a id="overview"></a>
## Visão Geral

**Por padrão, o Caddy serve todos os sites através de HTTPS.**

- O Caddy serve endereços IP e nomes de host locais/internos via HTTPS usando certificados autoassinados que são automaticamente confiados localmente (se permitido).
	- Exemplos: `localhost`, `127.0.0.1`
- O Caddy serve nomes DNS públicos via HTTPS usando certificados de uma CA ACME pública, como [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) ou [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com).
	- Exemplos: `example.com`, `sub.example.com`, `*.example.com`

O Caddy mantém todos os certificados gerenciados renovados e redireciona HTTP (porta padrão `80`) para HTTPS (porta padrão `443`) automaticamente.

**Para HTTPS local:**

- O Caddy pode solicitar uma senha para instalar seu certificado raiz exclusivo em seu armazenamento de confiança. Isso acontece apenas uma vez por raiz; e você pode removê-lo a qualquer momento.
- Qualquer cliente que acesse o site sem confiar no certificado CA raiz do Caddy verá erros de segurança.

**Para nomes de domínio públicos:**

<aside class="tip">

Estes são requisitos comuns para qualquer site de produção básico, não apenas para o Caddy. A principal diferença é configurar seus registros DNS corretamente **antes** de executar o Caddy para que ele possa provisionar os certificados.

</aside>


- Se os registros A/AAAA do seu domínio apontarem para o seu servidor,
- as portas `80` e `443` estiverem abertas externamente,
- o Caddy puder se vincular a essas portas (_ou_ se essas portas forem encaminhadas para o Caddy),
- seu [diretório de dados](/docs/conventions#data-directory) for gravável e persistente,
- e seu nome de domínio aparecer em algum lugar relevante na configuração,

então os sites serão servidos por HTTPS automaticamente. Você não terá que fazer mais nada. Simplesmente funciona!

Como o HTTPS utiliza uma infraestrutura pública compartilhada, você, como administrador do servidor, deve entender o restante das informações nesta página para evitar problemas desnecessários, resolvê-los quando ocorrerem e configurar corretamente implantações avançadas.



<a id="activation"></a>
## Ativação

O Caddy ativa implicitamente o HTTPS automático quando conhece um nome de domínio (ou seja, nome de host) ou endereço IP que está servindo. Existem várias maneiras de informar ao Caddy seu domínio/IP, dependendo de como você executa ou configura o Caddy:

- Um [endereço de site](/docs/caddyfile/concepts#addresses) no [Caddyfile](/docs/caddyfile)
- Um [correspondente de host (host matcher)](/docs/json/apps/http/servers/routes/match/host/) no nível superior nas [rotas JSON](/docs/modules/http#servers/routes)
- Sinalizadores de linha de comando como [`--domain`](/docs/command-line#caddy-file-server) ou [`--from`](/docs/command-line#caddy-reverse-proxy)
- O carregador de certificados [automate](/docs/json/apps/tls/certificates/automate/)

Qualquer um dos seguintes impedirá que o HTTPS automático seja ativado, total ou parcialmente:

- Desativá-lo explicitamente [via JSON](/docs/json/apps/http/servers/automatic_https/) ou [via Caddyfile](/docs/caddyfile/options#auto-https)
- Não fornecer nomes de host ou endereços IP na configuração
- Escutar exclusivamente na porta HTTP
- Prefixar o [endereço do site](/docs/caddyfile/concepts#addresses) com `http://` no Caddyfile
- Carregar certificados manualmente (a menos que [`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/) esteja definido)

**Casos especiais:**

- Domínios terminados em `.ts.net` não serão gerenciados pelo Caddy. Em vez disso, o Caddy tentará obter esses certificados automaticamente no momento do handshake a partir da instância do [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) em execução local. Isso requer que o [HTTPS esteja habilitado em sua conta Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/) e o processo Caddy deve estar sendo executado como root, ou você deve configurar o `tailscaled` para dar ao seu usuário Caddy [permissão para buscar certificados](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).


<a id="effects"></a>
## Efeitos

Quando o HTTPS automático é ativado, ocorre o seguinte:

- Certificados são obtidos e renovados para [todos os nomes de domínio qualificados](#hostname-requirements)
- O HTTP é redirecionado para o HTTPS (isso usa a [porta HTTP](/docs/modules/http#http_port) `80`)

O HTTPS automático nunca substitui a configuração explícita, apenas a complementa.

Se você já tiver um [servidor](/docs/json/apps/http/servers/) escutando na porta HTTP, as rotas de redirecionamento HTTP->HTTPS serão inseridas após suas rotas com um correspondente de host, mas antes de uma rota genérica definida pelo usuário.

Você pode [personalizar ou desativar o HTTPS automático](/docs/json/apps/http/servers/automatic_https/) se necessário; por exemplo, você pode ignorar certos nomes de domínio ou desativar redirecionamentos (para o Caddyfile, faça isso com [opções globais](/docs/caddyfile/options)).


<a id="hostname-requirements"></a>
## Requisitos de Nome de Host

Todos os nomes de host (nomes de domínio) se qualificam para certificados totalmente gerenciados se:

- não forem vazios
- consistirem apenas em caracteres alfanuméricos, hifens, pontos e o caractere curinga (`*`)
- não começarem ou terminarem com um ponto ([RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5))

Além disso, os nomes de host se qualificam para certificados de confiança pública se:

- não forem localhost (incluindo os TLDs `.localhost`, `.local`, `.internal` e `.home.arpa`)
- não forem um endereço IP
- tiverem apenas um único caractere curinga `*` como o rótulo mais à esquerda


<a id="local-https"></a>
## HTTPS Local

O Caddy usa HTTPS automaticamente para todos os sites com um host (domínio, IP ou nome de host) especificado, incluindo hosts internos e locais. Alguns hosts não são públicos (por exemplo, `127.0.0.1`, `localhost`) ou geralmente não se qualificam para certificados de confiança pública (por exemplo, endereços IP -- você pode obter certificados para eles, mas apenas de algumas CAs). Estes ainda são servidos através de HTTPS, a menos que desativado.

Para servir sites não públicos via HTTPS, o Caddy gera sua própria autoridade certificadora (CA) e a utiliza para assinar certificados. A cadeia de confiança consiste em um certificado raiz e um intermediário. Os certificados de folha (leaf) são assinados pelo intermediário. Eles são armazenados no [diretório de dados do Caddy](/docs/conventions#data-directory) em `pki/authorities/local`.

A CA local do Caddy é alimentada pelas [bibliotecas Smallstep <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/).

O HTTPS local não usa ACME nem realiza nenhuma validação de DNS. Funciona apenas na máquina local e é confiável apenas onde o certificado raiz da CA está instalado.

<a id="ca-root"></a>
### CA Raiz

A chave privada da raiz é gerada exclusivamente usando uma fonte pseudialeatória criptograficamente segura e persistida no armazenamento com permissões limitadas. Ela é carregada na memória apenas para realizar tarefas de assinatura, após as quais sai do escopo para ser coletada pelo coletor de lixo.

Embora o Caddy possa ser configurado para assinar com a raiz diretamente (para suportar clientes não conformes), isso é desativado por padrão, e a chave raiz é usada apenas para assinar intermediários.

A primeira vez que uma chave raiz é usada, o Caddy tentará instalá-la no(s) armazenamento(s) de confiança local do sistema. Se não tiver permissão para isso, solicitará uma senha. Esse comportamento pode ser desativado com [`skip_install_trust` em um caddyfile](/docs/caddyfile/options#skip-install-trust) ou [`"install_trust": false` em uma configuração json](/docs/json/apps/pki/certificate_authorities/install_trust/). Se isso falhar por estar sendo executado como um usuário não privilegiado, você pode executar [`caddy trust`](/docs/command-line#caddy-trust) para tentar a instalação como um usuário privilegiado Novamente.

<aside class="tip">
	É seguro confiar no certificado raiz do Caddy em sua própria máquina, desde que seu computador não esteja comprometido e sua chave raiz exclusiva não seja vazada.
</aside>

Após a CA raiz do Caddy ser instalada, você a verá em seu armazenamento de confiança local como "Caddy Local Authority" (a menos que você tenha configurado um nome diferente). Você pode desinstalá-la a qualquer momento se desejar (o comando [`caddy untrust`](/docs/command-line#caddy-untrust) facilita isso).

Observe que a instalação automática do certificado nos armazenamentos de confiança locais é apenas por conveniência e não é garantida, especialmente se contêineres estiverem sendo usados ou se o Caddy estiver sendo executado como um serviço de sistema não privilegiado. No final das contas, se você estiver confiando em uma PKI interna, é responsabilidade do administrador do sistema garantir que a CA raiz do Caddy seja adicionada corretamente aos armazenamentos de confiança necessários (isso está fora do escopo do servidor web).


<a id="ca-intermediates"></a>
### CA Intermediários

Um certificado intermediário e uma chave também serão gerados, que serão usados para assinar certificados de folha (sites individuais).

Ao contrário do certificado raiz, os certificados intermediários têm uma vida útil muito mais curta e serão renovados automaticamente conforme necessário.


<a id="testing"></a>
## Testes

Para testar ou experimentar sua configuração do Caddy, certifique-se de [alterar o endpoint ACME](/docs/modules/tls.issuance.acme#ca) para um URL de teste ou desenvolvimento; caso contrário, é provável que você atinja limites de taxa que podem bloquear seu acesso ao HTTPS por até uma semana, dependendo de qual limite você atingiu.

Uma das CAs padrão do Caddy é a [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/), que possui um [endpoint de teste <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) que não está sujeito aos mesmos [limites de taxa <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/):

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

<a id="acme-challenges"></a>
## Desafios ACME

A obtenção de um certificado TLS de confiança pública requer a validação de uma autoridade terceirizada de confiança pública. Hoje em dia, esse processo de validação é automatizado com o [protocolo ACME <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555) e pode ser realizado de três maneiras ("tipos de desafio"), descritas abaixo.

Os dois primeiros tipos de desafio são habilitados por padrão. Se vários desafios estiverem habilitados, o Caddy escolhe um aleatoriamente para evitar a dependência acidental de um desafio específico. Com o tempo, ele aprende qual tipo de desafio é mais bem-sucedido e começará a preferi-lo primeiro, mas recorrerá a outros tipos de desafio disponíveis, se necessário.


<a id="http-challenge"></a>
### Desafio HTTP

O desafio HTTP realiza uma consulta DNS autoritativa para o registro A/AAAA do nome de host candidato e, em seguida, solicita um recurso criptográfico temporário pela porta `80` usando HTTP. Se a CA vir o recurso esperado, um certificado é emitido.

Este desafio requer que a porta `80` esteja acessível externamente. Se o Caddy não puder escutar na porta 80, os pacotes da porta `80` devem ser encaminhados para a [porta HTTP](/docs/json/apps/http/http_port/) do Caddy.

Este desafio é habilitado por padrão e não requer configuração explícita.


<a id="tls-alpn-challenge"></a>
### Desafio TLS-ALPN

O desafio TLS-ALPN realiza uma consulta DNS autoritativa para o registro A/AAAA do nome de host candidato e, em seguida, solicita um recurso criptográfico temporário pela porta `443` usando um handshake TLS contendo valores especiais de ServerName e ALPN. Se a CA vir o recurso esperado, um certificado é emitido.

Este desafio requer que a porta `443` esteja acessível externamente. Se o Caddy não puder escutar na porta 443, os pacotes da porta `443` devem ser encaminhados para a [porta HTTPS](/docs/json/apps/http/https_port/) do Caddy.

Este desafio é habilitado por padrão e não requer configuração explícita.


<a id="dns-challenge"></a>
### Desafio DNS

O desafio DNS realiza uma consulta DNS autoritativa para os registros `TXT` do nome de host candidato e procura por um registro `TXT` especial com um determinado valor. Se a CA vir o valor esperado, um certificado é emitido.

Este desafio não requer nenhuma porta aberta e o servidor que solicita um certificado não precisa estar acessível externamente. No entanto, o desafio DNS requer configuração. O Caddy precisa conhecer as credenciais para acessar o provedor de DNS do seu domínio para que possa definir (e limpar) os registros `TXT` especiais. Se o desafio DNS estiver habilitado, outros desafios serão desativados por padrão.

Como as CAs ACME seguem os padrões DNS ao procurar registros `TXT` para verificação de desafio, você pode usar registros CNAME para delegar a resposta ao desafio para outras zonas DNS. Isso pode ser usado para delegar o subdomínio `_acme-challenge` para [outra zona](/docs/caddyfile/directives/tls#dns_challenge_override_domain). Isso é particularmente útil se o seu provedor de DNS não fornecer uma API ou não for suportado por um dos plugins de DNS para o Caddy.

O suporte ao provedor de DNS é um esforço da comunidade. [Saiba como habilitar o desafio DNS para o seu provedor em nossa wiki.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


<a id="on-demand-tls"></a>
## TLS Sob Demanda (On-Demand)

O Caddy foi pioneiro em uma nova tecnologia que chamamos de **TLS Sob Demanda**, que obtém dinamicamente um novo certificado durante o primeiro handshake TLS que o exige, em vez de no carregamento da configuração. Crucialmente, isso **não** requer a codificação rígida (hard-coding) dos nomes de domínio em sua configuração antecipadamente.

Muitas empresas contam com esse recurso exclusivo para dimensionar suas implantações TLS a um custo menor e sem dores de cabeça operacionais ao servir dezenas de milhares de sites.

O TLS sob demanda é útil se:

- você não conhece todos os nomes de domínio quando inicia ou recarrega seu servidor,
- os nomes de domínio podem não estar configurados corretamente imediatamente (registros DNS ainda não definidos),
- você não tem controle sobre os nomes de domínio (por exemplo, são domínios de clientes).

Quando o TLS sob demanda está habilitado, você não precisa especificar os nomes de domínio em sua configuração para obter certificados para eles. Em vez disso, quando um handshake TLS é recebido para um nome de servidor (SNI) para o qual o Caddy ainda não possui um certificado, o handshake é retido enquanto o Caddy obtém um certificado para usar para completar o handshake. O atraso é geralmente de apenas alguns segundos, e apenas o handshake inicial é lento. Todos os handshakes futuros são rápidos porque os certificados são armazenados em cache e reutilizados, e as renovações acontecem em segundo plano. Handshakes futuros podem acionar a manutenção do certificado para mantê-lo renovado, mas essa manutenção acontece em segundo plano se o certificado ainda não tiver expirado.

<a id="using-on-demand-tls"></a>
### Usando TLS Sob Demanda

**O TLS sob demanda deve ser habilitado e restrito para evitar abusos.**

A habilitação do TLS sob demanda ocorre nas [políticas de automação TLS](/docs/json/apps/tls/automation/policies/) se estiver usando a configuração JSON, ou [em blocos de site com a diretiva `tls`](/docs/caddyfile/directives/tls) se estiver usando o Caddyfile.

Para evitar o abuso desse recurso, você deve configurar restrições. Isso é feito no [objeto `automation` da configuração JSON](/docs/json/apps/tls/automation/on_demand/), ou na [opção global `on_demand_tls`](/docs/caddyfile/options#on-demand-tls) do Caddyfile. As restrições são "globais" e não podem ser configuradas por site ou por domínio. A restrição primária é um endpoint de consulta ("ask") para o qual o Caddy enviará uma solicitação HTTP para perguntar se tem permissão para obter e gerenciar um certificado para o domínio no handshake. Isso significa que você precisará de algum backend interno que possa, por exemplo, consultar a tabela de contas do seu banco de dados e ver se um cliente se inscreveu com esse nome de domínio.

Esteja ciente da rapidez com que sua CA é capaz de emitir certificados. Se levar mais do que alguns segundos, isso afetará negativamente a experiência do usuário (apenas para o primeiro cliente).

Devido à sua natureza diferida e à configuração extra necessária para evitar abusos, recomendamos habilitar o TLS sob demanda apenas quando seu caso de uso real for descrito acima.

[Consulte nosso artigo na wiki para obter mais informações sobre como usar o TLS sob demanda de forma eficaz.](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)


<a id="errors"></a>
## Erros

O Caddy faz o seu melhor para continuar se ocorrerem erros com o gerenciamento de certificados.

Por padrão, o gerenciamento de certificados é realizado em segundo plano. Isso significa que não bloqueará a inicialização nem deixará seus sites lentos. No entanto, também significa que o servidor estará em execução antes mesmo de todos os certificados estarem disponíveis. A execução em segundo plano permite que o Caddy tente novamente com backoff exponencial durante um longo período de tempo.

Aqui está o que acontece se houver um erro ao obter ou renovar um certificado:

1. O Caddy tenta novamente uma vez após uma breve pausa, caso tenha sido um acaso
2. O Caddy pausa brevemente e, em seguida, muda para o próximo tipo de desafio habilitado
3. Depois que todos os tipos de desafio habilitados foram tentados, [ele tenta o próximo emissor configurado](#issuer-fallback)
	- Let's Encrypt
	- ZeroSSL
4. Depois que todos os emissores foram tentados, ele recua exponencialmente
	- Máximo de 1 dia entre as tentativas
	- Por até 30 dias

Durante as tentativas com o Let's Encrypt, o Caddy muda para seu [ambiente de teste <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) para evitar preocupações com o limite de taxa. Esta não é uma estratégia perfeita, mas no geral é útil.

Os desafios ACME levam pelo menos alguns segundos, e a limitação de taxa interna ajuda a mitigar abusos acidentais. O Caddy usa limitação de taxa interna, além do que você ou a CA configuram, para que você possa entregar ao Caddy uma lista com um milhão de nomes de domínio e ele irá gradualmente -- mas o mais rápido possível -- obter certificados para todos eles. O limite de taxa interno do Caddy é atualmente de 10 tentativas por conta ACME a cada 10 segundos.

Para evitar vazamento de recursos, o Caddy interrompe as tarefas em andamento (incluindo transações ACME) quando a configuração é alterada. Embora o Caddy seja capaz de lidar com recargas de configuração frequentes, esteja atento a considerações operacionais como essa e considere o agrupamento de alterações de configuração para reduzir recargas e dar ao Caddy a chance de realmente terminar de obter certificados em segundo plano.

<a id="issuer-fallback"></a>
### Fallback de Emissor

O Caddy é o primeiro (e até agora o único) servidor a suportar failover automático e totalmente redundante para outras CAs caso não consiga obter um certificado com sucesso.

Por padrão, o Caddy habilita duas CAs compatíveis com ACME: [**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) e [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com). Se o Caddy não conseguir obter um certificado do Let's Encrypt, ele tentará com o ZeroSSL; se ambos falharem, ele recuará e tentará novamente mais tarde. Em sua configuração, você pode personalizar quais emissores o Caddy usa para obter certificados, seja universalmente ou para nomes específicos.


<a id="storage"></a>
## Armazenamento

O Caddy armazenará certificados públicos, chaves privadas e outros ativos em sua [instalação de armazenamento configurada](/docs/json/storage/) (ou na padrão, se não configurada -- consulte o link para obter detalhes).

**O principal que você precisa saber usando a configuração padrão é que a pasta `$HOME` deve ser gravável e persistente.** Para ajudá-lo a solucionar problemas, o Caddy imprime suas variáveis de ambiente na inicialização se o sinalizador `--environ` for especificado.

Quaisquer instâncias do Caddy configuradas para usar o mesmo armazenamento compartilharão automaticamente esses recursos e coordenarão o gerenciamento de certificados como um cluster.

Antes de tentar qualquer transação ACME, o Caddy testará o armazenamento configurado para garantir que ele seja gravável e tenha capacidade suficiente. Isso ajuda a reduzir a contenção desnecessária de bloqueio.


<a id="wildcard-certificates"></a>
## Certificados Wildcard

O Caddy pode obter e gerenciar certificados curinga (wildcard) quando configurado para servir um site com um nome curinga qualificado. Um nome de site se qualifica para um curinga se apenas o rótulo de domínio mais à esquerda for um curinga. Por exemplo, `*.example.com` se qualifica, mas estes não: `sub.*.example.com`, `foo*.example.com`, `*bar.example.com` e `*.*.example.com`. (Esta é uma restrição da WebPKI.)

Se estiver usando o Caddyfile, o Caddy interpreta os nomes dos sites literalmente em relação aos nomes dos sujeitos dos certificados. Em outras palavras, um site definido como `sub.example.com` fará com que o Caddy gerencie um certificado para `sub.example.com`, e um site definido como `*.example.com` fará com que o Caddy gerencie um certificado curinga para `*.example.com`. Você pode ver isso demonstrado em nossa página de [Padrões Comuns do Caddyfile](/docs/caddyfile/patterns#wildcard-certificates). Se você precisar de um comportamento diferente, a [configuração JSON](/docs/json/) oferece um controle mais preciso sobre os sujeitos dos certificados e os nomes dos sites ("correspondentes de host").

A partir do Caddy 2.10, ao automatizar um certificado curinga, o Caddy usará o certificado curinga para subdomínios individuais na configuração. Ele não obterá certificados para subdomínios individuais, a menos que seja explicitamente configurado para isso (por exemplo, com `force_automate`).

Certificados curinga representam um amplo grau de autoridade e só devem ser usados quando você tiver tantos subdomínios que o gerenciamento de certificados individuais para eles sobrecarregaria a PKI ou faria com que você atingisse os limites de taxa impostos pela CA, ou se a compensação de privacidade valer o risco de expor grande parte da zona DNS em caso de comprometimento da chave. Observe que os certificados curinga por si só não oferecem privacidade ao ocultar subdomínios específicos: eles ainda são expostos em pacotes TLS ClientHello, a menos que o Encrypted ClientHello (ECH) esteja habilitado. (Veja abaixo.)

**Nota:** [A Let's Encrypt exige <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) o [desafio DNS](#dns-challenge) para obter certificados curinga.


<a id="encrypted-clienthello-ech"></a>
## Encrypted ClientHello (ECH)

Normalmente, os handshakes TLS envolvem o envio do ClientHello, incluindo o Server Name Indicator (SNI; o domínio ao qual você está se conectando), em texto simples. Isso ocorre porque ele contém os parâmetros necessários para criptografar a conexão que vem após o handshake. Isso, é claro, expõe o nome do domínio, que é a parte mais sensível do ClientHello, a qualquer pessoa que possa interceptar as conexões, mesmo que não estejam em sua vizinhança física imediata. Ele revela a qual serviço você está se conectando quando o IP de destino pode servir a muitos sites diferentes, e é assim que alguns governos censuram a Internet.

Com o Encrypted ClientHello, o cliente pode proteger o nome do domínio envolvendo o verdadeiro ClientHello em um ClientHello "externo" que estabelece parâmetros para descriptografar o ClientHello "interno". No entanto, muitas partes móveis precisam se unir perfeitamente para que isso funcione e ofereça benefícios reais de privacidade.

Primeiro, o cliente precisa saber quais parâmetros, ou configuração, usar para criptografar o ClientHello. Essas informações incluem uma chave pública e um domínio "externo" (o "nome público"), entre outras coisas. Essa configuração precisa ser publicada ou distribuída de alguma forma confiável.

Teoricamente, você poderia anotá-la em um pedaço de papel e distribuí-la para todos, mas a maioria dos principais navegadores suporta a consulta de registros DNS do tipo HTTPS contendo parâmetros ECH ao se conectar a um site. Portanto, você precisará: (1) gerar uma configuração ECH (par de chaves pública/privada, entre outros parâmetros) e, em seguida, (2) criar um registro DNS do tipo HTTPS contendo a configuração ECH codificada em base64.

Ou... você pode deixar o Caddy fazer tudo isso por você. O Caddy é o primeiro e único servidor web que pode gerar, publicar e servir configurações ECH automaticamente.

Assim que o registro HTTPS for publicado, os clientes precisarão realizar uma consulta DNS para o registro HTTPS ao se conectarem ao seu site. Normalmente, as consultas DNS são em texto simples, o que compromete a segurança dos handshakes ECH resultantes, portanto os navegadores precisarão usar um protocolo DNS seguro, como DNS-sobre-HTTPS (DoH) ou DNS-sobre-TLS (DoT). Dependendo do navegador, isso pode precisar ser habilitado manualmente.

Depois que o cliente baixa com segurança a configuração ECH, ele usa a chave pública incorporada para criptografar o ClientHello e prossegue para se conectar ao seu site. O Caddy descriptografa o ClientHello interno e prossegue para servir seu site, sem que o nome do domínio apareça em texto simples pela rede.

<a id="deployment-considerations"></a>
### Considerações de implantação

ECH é uma tecnologia cheia de nuances. Embora o Caddy automatize completamente o ECH, muitas coisas precisam ser consideradas para obter os benefícios máximos de privacidade. Você também deve estar ciente de várias compensações.

<a id="publication"></a>
#### Publicação

O Caddy criará apenas um registro HTTPS para um domínio se já houver um registro para esse domínio. Isso evita a quebra de consultas DNS para um subdomínio que pode ser coberto por um curinga. Certifique-se de que seus sites tenham pelo menos um registro A/AAAA apontando para seu servidor. Se você usar apenas um caractere curinga para registros DNS, o domínio curinga também precisará aparecer em sua configuração do Caddy.

O Caddy não publicará um registro HTTPS para um domínio que possua um registro CNAME.

<a id="ech-grease"></a>
#### ECH GREASE

Se você abrir o Wireshark e se conectar a qualquer site (mesmo um que não suporte ECH) em uma versão moderna de um navegador principal como Firefox ou Chrome (mesmo com ECH desativado), poderá notar que o handshake inclui a extensão `encrypted_client_hello`:

![ECH GREASE](/resources/images/ech-grease.png)

O objetivo disso é tornar os handshakes ECH verdadeiros indistinguíveis dos de texto simples. Se os handshakes ECH parecessem diferentes dos normais, os censores poderiam simplesmente bloquear os handshakes ECH com danos colaterais mínimos. Mas se bloqueassem qualquer handshake com uma extensão ECH plausível, desligariam essencialmente a maior parte da Internet. (O objetivo é aumentar o custo da censura generalizada.)

Isso é importante saber principalmente ao solucionar problemas de conexão.

<a id="key-rotation"></a>
#### Rotação de chaves

Assim como as chaves de certificado, não é uma boa prática (e pode ser francamente inseguro) usar a mesma chave por muito tempo. Como tal, as chaves ECH devem ser rotacionadas regularmente. Ao contrário dos certificados, as configurações ECH não expiram estritamente. Mas os servidores devem rotacioná-las de qualquer maneira.

A rotação de chaves é complicada, porém, porque os clientes precisam saber sobre as chaves atualizadas. Se o servidor simplesmente substituísse as chaves antigas por novas, todos os handshakes ECH falhariam, a menos que os clientes fossem imediatamente notificados sobre as novas chaves. Mas simplesmente publicar as chaves atualizadas não é suficiente. A realidade é que os registros DNS possuem TTLs, e os resolvedores armazenam respostas em cache, etc. Pode levar minutos, horas ou até dias para os clientes consultarem os registros HTTPS atualizados e começarem a usar a nova configuração ECH.

Por esse motivo, os servidores devem continuar suportando configurações ECH antigas por um período de tempo. Não fazer isso corre o risco de expor nomes de servidores em texto simples _em escala_. O Caddy rotaciona as chaves de vez em quando e suporta chaves rotacionadas por algum tempo, até que sejam finalmente descartadas.

No entanto, isso pode não ser suficiente. Alguns clientes ainda não receberão as chaves atualizadas por vários motivos e, sempre que isso acontece, há um risco de expor o nome do servidor. Portanto, deve haver outra maneira de fornecer aos clientes a configuração atualizada _em banda_ (in-band) com a conexão. É para isso que serve o _nome externo_ (ou _nome público_).

<a id="public-name"></a>
#### Nome público

O ClientHello "externo" é um ClientHello normal com duas diferenças sutis que só são conhecidas pelo servidor de origem:

1. A extensão SNI é falsa
2. A extensão ECH é real

Essa extensão SNI "externa" contém o nome público que protege seus domínios reais. Esse nome pode ser qualquer coisa, mas **seu servidor deve ser autoritativo para o nome público** porque o Caddy _irá_ obter um certificado para ele.

Se um cliente tentar fazer uma conexão ECH, mas o servidor não conseguir descriptografar o ClientHello interno, ele poderá completar o handshake usando o ClientHello _externo_ com um certificado para o nome externo. Esta conexão segura é estritamente usada _apenas_ para enviar ao cliente a configuração ECH atual; ou seja, é uma conexão TLS temporária com o único propósito de completar a conexão TLS inicial. Nenhum dado de aplicativo é transmitido: apenas a chave ECH. Assim que o cliente tiver a chave atualizada, ele poderá estabelecer a conexão TLS conforme pretendido.

Desta forma, o nome verdadeiro do servidor permanece protegido e os clientes fora de sincronia continuam sendo capazes de se conectar, que são elementos vitais de segurança.

O nome público pode ser um dos domínios do seu site, um subdomínio ou qualquer outro nome de domínio que aponte para o seu servidor. Recomendamos escolher exatamente um nome genérico. Por exemplo, a Cloudflare serve milhões de sites por trás de `cloudflare-ech.com`. Isso é importante para aumentar o tamanho do seu conjunto de anonimato (anonymity set).

Os nomes públicos não devem ser vazios; ou seja, um nome público deve ser configurado para que as coisas funcionem. O Caddy atualmente não impõe isso (e pode fazê-lo mais tarde), mas a especificação ECH exige que o nome público tenha pelo menos 1 byte de comprimento. Alguns softwares aceitarão nomes vazios, outros não. Isso pode levar a comportamentos confusos, como navegadores usando ECH, mas servidores rejeitando-o como inválido; ou navegadores não usando ECH (porque é inválido), mesmo que a configuração esteja no registro DNS corretamente. É responsabilidade do proprietário do site garantir a configuração e publicação adequadas do ECH para garantir a privacidade.


<a id="anonymity-set"></a>
#### Conjunto de anonimato (Anonymity set)

Para maximizar os benefícios de privacidade do ECH, esforce-se para maximizar o tamanho do seu _conjunto de anonimato_. Em essência, este conjunto é composto por servidores voltados para o cliente que possuem comportamento idêntico para observadores. A ideia é que um observador não consiga reduzir/deduzir facilmente os possíveis sites ou serviços aos quais os clientes estão se conectando.

Na prática, recomendamos ter apenas um nome público para todos os seus sites. (Existe apenas 1 nome público por configuração ECH, portanto, isso implica ter apenas 1 configuração ECH ativa a qualquer momento.) Se você opera o Caddy em um cluster, o Caddy compartilha e coordena automaticamente as configurações ECH com outras instâncias, o que cuida disso para você.

Levado ao extremo, isso implica que todos os sites na Internet poderiam ou deveriam estar atrás de um único endereço IP e um nome público...


<a id="centralization"></a>
#### Centralização

... o que nos leva ao próximo tópico: centralização. Uma das críticas ao ECH é que ele tende a motivar a centralização. Ele faz isso de pelo menos duas maneiras: (1) por clientes que preferem DoH/DoT para consultas DNS, o que envia todas as consultas DNS através de um pequeno punhado de provedores, e (2) por maximizar o tamanho do conjunto de anonimato em escala.

Quando DoH ou DoT é usado, as consultas DNS passam todas pelo provedor DoH/DoT. Entre o cliente e o provedor, os dados DNS são criptografados, mas entre o provedor e o servidor DNS, eles não são criptografados. O DoH/DoT global efetivamente afunila todo o suculento tráfego DNS em texto simples em alguns grandes tubos que estão prontos para observação... ou falha.

Da mesma forma, se realmente maximizarmos o conjunto de anonimato em escala, todos os sites seriam protegidos sob um único nome público, como `cloudflare-ech.com`. Isso é bom para a privacidade, mas então toda a Internet estaria à mercê da Cloudflare e desse único nome de domínio. Agora, maximizar a esse ponto não é necessário nem prático, mas as implicações teóricas permanecem válidas.

Recomendamos que cada organização ou indivíduo escolha um único nome para todos os seus sites e o utilize, e na maioria dos casos isso deve oferecer privacidade suficiente. No entanto, consulte especialistas com seus modelos de ameaças individuais para seu caso específico.


<a id="subdomain-privacy"></a>
#### Privacidade de subdomínio

Com o ECH, agora é teoricamente possível manter os subdomínios em segredo/privados de canais laterais se implantados corretamente.

A maioria dos sites não precisa disso, pois, de modo geral, os subdomínios são informações públicas. Desaconselhamos colocar informações confidenciais em nomes de domínio. Dito isso...

Para evitar o vazamento de subdomínios confidenciais para os logs de Transparência de Certificado (CT), use um certificado curinga em seu lugar. Em outras palavras, em vez de colocar `sub.example.com` em sua configuração, coloque `*.example.com`. (Consulte [Certificados Wildcard](#wildcard-certificates) para obter informações importantes.)

Outra fonte de vazamentos é o DNSSEC, que a maioria dos servidores DNS autoritativos usa por padrão. Através de uma prática chamada "zone walking", a enumeração de subdomínios é possível observando os registros NSEC, que são usados para fornecer a negação de existência autenticada. Para isso, eles apontam para o próximo subdomínio disponível em ordem alfabética, formando uma lista vinculada de todos os registros. Certifique-se de que seu domínio esteja usando, no mínimo, NSEC3 ou, idealmente, um registro CNAME curinga para mitigar isso.

Em seguida, habilite o ECH no Caddy. Um certificado curinga combinado com ECH e um registro CNAME curinga deve ocultar adequadamente os subdomínios, desde que cada cliente que tente se conectar a ele use ECH e tenha uma implementação forte. (Você ainda está à mercê dos clientes para preservar a privacidade.)


<a id="enabling-ech"></a>
### Habilitando ECH

Como o ECH funcional requer a publicação de configurações em registros DNS, você precisará de uma compilação do Caddy com um [módulo caddy-dns](https://github.com/caddy-dns) conectado para o seu provedor de DNS.

Em seguida, com um Caddyfile, especifique a configuração do seu provedor de DNS nas opções globais, bem como o nome público ECH que você deseja usar:

```caddy
{
	dns <configuração do provedor...>
	ech example.com
}
```

Lembre-se:

- O módulo provedor de DNS deve estar conectado e você deve ter a configuração correta para o seu provedor/conta.
- O nome público ECH deve apontar para o seu servidor. O Caddy obterá um certificado para ele. Ele não precisa ser um dos domínios do seu site.

Se estiver usando JSON, adicione estas propriedades ao aplicativo `tls`:

```json
"encrypted_client_hello": {
	"configs": [
		{
			"public_name": "example.com"
		}
	]
},
"dns": {
	"name": "<nome do provedor>",
	// configuração do provedor
}
```

Essas configurações habilitarão o ECH e publicarão as configurações ECH para todos os seus sites. A configuração JSON oferece mais flexibilidade se você precisar personalizar o comportamento ou tiver uma configuração avançada.

<a id="verifying-ech"></a>
### Verificando ECH

Ainda não há muitas ferramentas em torno do ECH, então, no momento em que este artigo foi escrito, a melhor e mais universal maneira de verificar se ele está funcionando é usar o Wireshark e procurar seu nome público no campo ServerName.

Primeiro, inicie seu servidor e veja se os registros mencionam algo como "published ECH configuration list" para seus domínios. (Se você receber algum erro na publicação, certifique-se de que o módulo do provedor de DNS suporte o [libdns 1.0](https://github.com/libdns/libdns) e registre um problema no repositório do seu provedor se encontrar problemas.) O Caddy também deve obter um certificado para o nome público.

Em seguida, certifique-se de que seu navegador tenha o ECH habilitado; isso pode exigir a habilitação de DoH/DoT. Também é uma boa ideia limpar o cache DNS do seu navegador (ou do sistema) para garantir que ele selecionará os registros HTTPS recém-publicados. Também recomendamos fechar o navegador ou, pelo menos, abrir uma nova guia privada para garantir que ele não reutilize conexões existentes.

Em seguida, abra o Wireshark e comece a escutar na interface de rede apropriada. Enquanto o Wireshark está coletando pacotes, carregue seu site em seu navegador. Você pode então pausar o Wireshark. Encontre o ClientHello do seu TLS e você verá o _nome público_ no campo ServerName, em vez do nome de domínio real ao qual você se conectou.

Lembre-se: você ainda pode ver uma extensão `encrypted_client_hello`, mesmo que o ECH não seja usado. O indicador principal é o valor SNI. Você nunca deve ver o nome verdadeiro do site em texto simples com o Wireshark se o ECH estiver funcionando corretamente.

Se você encontrar problemas de implantação com o ECH, primeiro pergunte em nosso [fórum](https://caddy.community). Se for um bug, você pode [registrar um problema](https://github.com/caddyserver/caddy/issues) no GitHub.


<a id="ech-in-storage"></a>
### ECH no armazenamento

As configurações ECH são armazenadas no [diretório de dados](/docs/conventions#data-directory) no módulo de armazenamento configurado (sendo o padrão o sistema de arquivos) sob a pasta `ech/configs`.

A próxima pasta é um ID de configuração ECH, que são gerados aleatoriamente e relativamente sem importância. A aleatoriedade é recomendada pela especificação para ajudar a mitigar o rastreamento/impressão digital (fingerprinting).

Um arquivo metadata sidecar ajuda o Caddy a acompanhar quando as publicações ocorreram pela última vez. Isso evita sobrecarregar seu provedor de DNS em cada recarga de configuração. Se você tiver que redefinir esse estado, poderá excluir com segurança o arquivo de metadados. No entanto, isso também pode redefinir o momento em que a chave será rotacionada. Você também pode entrar no arquivo e limpar apenas as informações sobre a publicação.
