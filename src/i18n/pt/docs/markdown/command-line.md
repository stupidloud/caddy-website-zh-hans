---
title: "Linha de comando"
---

# Linha de comando

O Caddy tem uma interface de linha de comando padrão, no estilo Unix. O uso básico é:

```
caddy <command> [<args...>]
```

Os `<carets>` indicam parâmetros que serão substituídos pela sua entrada.

Os `[brackets]` indicam parâmetros opcionais. Os `(brackets)` indicam parâmetros obrigatórios.

As reticências `...` indicam continuação, isto é, um ou mais parâmetros.

As `--flags` podem ter um atalho de uma letra, como `-f`.

**Início rápido: `caddy`, `caddy help` ou `man caddy` (se instalado)**

---

- **[caddy adapt](#caddy-adapt)**
  Adapta um documento de configuração para o JSON nativo

- **[caddy build-info](#caddy-build-info)**
  Mostra informações de build

- **[caddy completion](#caddy-completion)**
  Gera script de auto-completar do shell

- **[caddy environ](#caddy-environ)**
  Mostra o ambiente

- **[caddy file-server](#caddy-file-server)**
  Um servidor de arquivos simples, mas pronto para produção

- **[caddy file-server export-template](#caddy-file-server-export-template)**
  Comando auxiliar do file server para exportar o template padrão do navegador de arquivos

- **[caddy fmt](#caddy-fmt)**
  Formata um Caddyfile

- **[caddy hash-password](#caddy-hash-password)**
  Faz hash de uma senha e imprime em base64

- **[caddy help](#caddy-help)**
  Mostra ajuda para comandos do caddy

- **[caddy list-modules](#caddy-list-modules)**
  Lista os módulos Caddy instalados

- **[caddy manpage](#caddy-manpage)**
  Gera páginas de manual

- **[caddy reload](#caddy-reload)**
  Altera a configuração do processo Caddy em execução

- **[caddy respond](#caddy-respond)**
  Um servidor HTTP fixo, simples e direto, para desenvolvimento e testes

- **[caddy reverse-proxy](#caddy-reverse-proxy)**
  Um reverse proxy HTTP(S) simples, mas pronto para produção

- **[caddy run](#caddy-run)**
  Inicia o processo Caddy em primeiro plano

- **[caddy start](#caddy-start)**
  Inicia o processo Caddy em segundo plano

- **[caddy stop](#caddy-stop)**
  Para o processo Caddy em execução

- **[caddy storage export](#caddy-storage)**
  Exporta o conteúdo do storage configurado para um tarball

- **[caddy storage import](#caddy-storage)**
  Importa um tarball exportado anteriormente para o storage configurado

- **[caddy trust](#caddy-trust)**
  Instala um certificado em trust store(s) locais

- **[caddy untrust](#caddy-untrust)**
  Remove a confiança de um certificado da trust store local

- **[caddy upgrade](#caddy-upgrade)**
  Atualiza o Caddy para a versão mais recente

- **[caddy add-package](#caddy-add-package)**
  Atualiza o Caddy para a versão mais recente, com plugins adicionais

- **[caddy remove-package](#caddy-remove-package)**
  Atualiza o Caddy para a versão mais recente, com alguns plugins removidos

- **[caddy validate](#caddy-validate)**
  Testa se um arquivo de configuração é válido

- **[caddy version](#caddy-version)**
  Mostra a versão

- **[Signals](#signals)**
  Como o Caddy lida com sinais

- **[Exit codes](#exit-codes)**
  Códigos emitidos quando o processo Caddy encerra

<a id="subcommands"></a>
## Subcomandos

<a id="caddy-adapt"></a>
### `caddy adapt`

<pre><code class="cmd bash">caddy adapt
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[-p, --pretty]
	[--validate]</code></pre>

Adapta uma configuração para a estrutura JSON nativa do Caddy e escreve a saída em stdout, junto com quaisquer avisos em stderr, e então encerra.

`--config` é o caminho do arquivo de configuração. Se omitido, assume `Caddyfile` no diretório atual, se existir; caso contrário, essa flag é obrigatória. Se você quiser usar stdin em vez de um arquivo regular, use `-` como caminho.

`--adapter` especifica o config adapter a ser usado; o padrão é `caddyfile`.

`--pretty` formata a saída com indentação para leitura humana.

`--validate` carrega e provisiona a configuração adaptada para verificar se é válida (mas não inicia de fato a configuração).

Observe que uma configuração que foi adaptada com sucesso ainda pode falhar na validação. Por exemplo, use este Caddyfile:

```caddy
localhost

tls cert_notexist.pem key_notexist.pem
```

Tente adaptá-lo:

<pre><code class="cmd bash">caddy adapt --config Caddyfile</code></pre>

Ele terá sucesso sem erro. Agora tente:

<pre><code class="cmd"><span class="bash">caddy adapt --config Caddyfile --validate</span>
adapt: validation: loading app modules: module name 'tls': provision tls: loading certificates: open cert_notexist.pem: no such file or directory
</code></pre>

Mesmo que esse Caddyfile possa ser adaptado para JSON sem erros, os arquivos reais de certificado e/ou chave não existem, então a validação falha porque esse erro surge durante a fase de provisionamento. Portanto, a validação é um teste de erro mais forte do que simplesmente serializar uma configuração como JSON.

#### Exemplo

Para adaptar um Caddyfile para JSON que você possa ler e ajustar manualmente com facilidade:

<pre><code class="cmd bash">caddy adapt --config /path/to/Caddyfile --pretty</code></pre>

<a id="caddy-build-info"></a>
### `caddy build-info`

<pre><code class="cmd bash">caddy build-info</code></pre>

Mostra informações fornecidas pelo Go sobre a build (caminho do módulo principal, versões de pacotes, substituições de módulos).

<a id="caddy-completion"></a>
### `caddy completion`

<pre><code class="cmd bash">caddy completion [bash|zsh|fish|powershell]</code></pre>

Gera scripts de auto-completar do shell. Isso permite usar tab-complete ou auto-complete (ou algo similar, dependendo do shell) ao digitar comandos `caddy`.

Para obter instruções de instalação do script no seu shell específico, execute `caddy help completion` ou `caddy completion -h`.

<a id="caddy-environ"></a>
### `caddy environ`

<pre><code class="cmd bash">caddy environ</code></pre>

Mostra o ambiente como visto pelo caddy, e então encerra. Pode ser útil ao depurar init systems ou units de gerenciadores de processo como systemd.

<a id="caddy-file-server"></a>
### `caddy file-server`

<pre><code class="cmd bash">caddy file-server
	[-r, --root &lt;path&gt;]
	[--listen &lt;addr&gt;]
	[-d, --domain &lt;example.com&gt;]
	[-b, --browse]
	[--reveal-symlinks]
	[-t, --templates]
	[--access-log]
	[-v, --debug]
	[-f, --file-limit &lt;number&gt;]
	[--no-compress]
	[-p, --precompressed]</code></pre>

Sobe um servidor simples, mas pronto para produção, de arquivos estáticos.

`--root` especifica o caminho da raiz dos arquivos. O padrão é o diretório de trabalho atual.

`--listen` aceita um endereço de escuta. O padrão é `:80`, a menos que `--domain` seja usado; nesse caso, o padrão passa a ser `:443`.

`--domain` serve arquivos apenas por aquele hostname, e o Caddy tentará servi-lo sobre HTTPS, então certifique-se de que o DNS público esteja configurado corretamente se for um domínio público. A porta padrão será alterada para 443.

`--browse` habilita listagem de diretório quando uma pasta sem arquivo index é solicitada.

`--reveal-symlinks` mostra o destino dos links simbólicos em listagens de diretório quando `--browse` está habilitado.

`--templates` habilita renderização de templates.

`--access-log` habilita o log de requisições/acesso.

`--debug` habilita logging verboso.

`--file-limit` define um número máximo de arquivos exibidos em listagens de diretório. Padrão: `10000`. Se o número de arquivos exceder esse limite, apenas os primeiros N arquivos serão mostrados, onde N é o limite especificado.

`--no-compress` desabilita compressão. Por padrão, Zstandard e Gzip ficam habilitados.

`--precompressed` especifica formatos de codificação para procurar arquivos sidecar pré-comprimidos. Pode ser repetido para múltiplos formatos. Veja a [diretiva file_server](/docs/caddyfile/directives/file_server#precompressed) para mais informações.

Esse comando desabilita a admin API, o que facilita rodar várias instâncias em uma máquina de desenvolvimento local.

<a id="caddy-file-server-export-template"></a>
#### `caddy file-server export-template`

<pre><code class="cmd bash">caddy file-server export-template</code></pre>

Exporta o template padrão de navegação de arquivos para stdout.

<a id="caddy-fmt"></a>
### `caddy fmt`

<pre><code class="cmd bash">caddy fmt [&lt;path&gt;]
	[-w, --overwrite]
	[-d, --diff]</code></pre>

Formata ou "embelez"a um Caddyfile e então encerra. O resultado é impresso em stdout, a menos que `--overwrite` seja usado, e o processo sai com código `1` se houver diferenças.

`<path>` especifica o caminho do Caddyfile. Se for `-`, a entrada é lida de stdin. Se omitido, assume-se um arquivo chamado Caddyfile no diretório atual.

`--overwrite` faz o resultado ser gravado no arquivo de entrada em vez de ser impresso no terminal. Se a entrada não for um arquivo regular, essa flag não tem efeito.

`--diff` faz a saída ser comparada com a entrada, e as linhas serão prefixadas com `-` e `+` onde diferirem. Observe que linhas inalteradas são prefixadas com dois espaços para alinhamento, e que isso não é um formato de patch válido; é apenas uma ferramenta visual.

<a id="caddy-hash-password"></a>
### `caddy hash-password`

<pre><code class="cmd bash">caddy hash-password
	[-p, --plaintext &lt;password&gt;]
	[-a, --algorithm &lt;name&gt;]
	[--bcrypt-cost &lt;cost&gt;]</code></pre>

Uma forma prática de gerar hash de uma senha em texto puro. O hash resultante é escrito em stdout em um formato que pode ser usado diretamente na sua configuração do Caddy.

`--plaintext`
    A senha a ser hasheada. Se omitida, será lida de stdin.
    Se o Caddy estiver conectado a um TTY de controle, a entrada não será exibida.

`--algorithm`
    Seleciona o algoritmo de hash. Opções válidas:
      * `argon2id` (recomendado para segurança moderna)
      * `bcrypt`  (legado, mais lento, custo configurável, custo padrão `14`)

Parâmetros específicos do bcrypt:

`--bcrypt-cost`
    Define a dificuldade de hash do bcrypt. Valores maiores aumentam a segurança
    tornando o cálculo do hash mais lento e mais intensivo em CPU.
    Deve estar no intervalo válido [bcrypt.MinCost, bcrypt.MaxCost].
    Se omitido ou inválido, o custo padrão é usado.

Parâmetros específicos do Argon2id:

`--argon2id-time`
    Número de iterações a executar. Aumentar isso torna
    o hashing mais lento e mais resistente a ataques de força bruta.

`--argon2id-memory`
    Quantidade de memória a ser usada durante o hashing.
    Valores maiores aumentam a resistência a ataques de GPU/ASIC.

`--argon2id-threads`
    Número de threads de CPU a usar. Aumente para hashes mais rápidos
    em sistemas com vários núcleos.

`--argon2id-keylen`
    Tamanho do hash resultante em bytes. Chaves maiores aumentam a segurança,
    mas aumentam um pouco o tamanho de armazenamento.

<a id="caddy-help"></a>
### `caddy help`

<pre><code class="cmd bash">caddy help [&lt;command&gt;]</code></pre>

Mostra o texto de ajuda da CLI, opcionalmente para um subcomando específico, e então encerra.

<a id="caddy-list-modules"></a>
### `caddy list-modules`

<pre><code class="cmd bash">caddy list-modules
	[--packages]
	[--versions]
	[-s, --skip-standard]
	[--json]</code></pre>

Mostra os módulos Caddy instalados, opcionalmente com informações de pacote e/ou versão dos módulos Go associados, e então encerra.

Em alguns cenários automatizados, pode ser redundante mostrar também todos os módulos padrão, então você pode usar `--skip-standard` para omiti-los da saída.

`--json` gera as informações dos módulos em formato JSON, o que pode ser útil para processamento programático.

OBS: Devido a [um bug no Go](https://github.com/golang/go/issues/29228), informações de versão só ficam disponíveis se o Caddy for compilado como dependência e não como módulo principal. Use [xcaddy](/docs/build#xcaddy) para facilitar isso.

<a id="caddy-manpage"></a>
### `caddy manpage`

<pre><code class="cmd bash">caddy manpage
	(-o, --directory &lt;path&gt;)</code></pre>

Gera páginas de manual/documentação para os comandos do Caddy e escreve no diretório indicado. A saída desse comando pode ser lida pelo comando `man`.

`--directory` (obrigatório) é o caminho do diretório no qual as páginas de manual serão gravadas. Ele será criado se não existir.

Depois de geradas, as páginas de manual normalmente precisam ser instaladas. Esse procedimento varia por plataforma, mas em sistemas Linux típicos é algo assim:

<pre><code class="cmd"><b>$ caddy manpage --directory man
$ gzip -r man/
$ sudo cp man/* /usr/share/man/man8/
$ sudo mandb
</b></code></pre>

Então você pode executar `man caddy` (ou `man caddy-*` para subcomandos) para ler a documentação no terminal.

As páginas de manual são uma documentação separada da que existe no nosso site. Nosso site tem documentação mais completa e atualizada com frequência.

<a id="caddy-reload"></a>
### `caddy reload`

<pre><code class="cmd bash">caddy reload
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--address &lt;interface&gt;]
	[-f, --force]</code></pre>

Entrega ao Caddy em execução uma nova configuração. Isso tem o mesmo efeito de fazer POST de um documento no [endpoint /load](/docs/api#post-load), mas esse comando é conveniente para fluxos simples centrados em arquivos de configuração. Em comparação com os comandos `stop`, `start` e `run`, esse comando único é a forma correta e semântica de alterar/recarregar a configuração em execução.

Como esse comando usa a API, o endpoint de administração não deve estar desabilitado.

`--config` é o arquivo de configuração a ser aplicado. Se for `-`, a configuração é lida de stdin. Se não for especificado, o comando tentará um arquivo chamado `Caddyfile` no diretório de trabalho atual e, se ele existir, o adaptará usando o config adapter `caddyfile`; caso contrário, é erro se não houver arquivo de configuração para carregar.

`--adapter` especifica o config adapter a ser usado, se houver. Essa flag não é necessária se o nome fornecido em `--config` começar com `Caddyfile` ou terminar com `.caddyfile`, o que assume o adapter `caddyfile`. Caso contrário, essa flag é obrigatória se o arquivo de configuração fornecido não estiver no formato JSON nativo do Caddy.

`--address` precisa ser usado se o endpoint de administração não estiver ouvindo no endereço padrão e se ele for diferente do endereço no arquivo de configuração fornecido.

`--force` fará o reload acontecer mesmo se a configuração especificada for igual à que o Caddy já estiver executando. Pode ser útil para forçar o Caddy a reprovisionar seus módulos, o que pode ter efeitos colaterais; por exemplo: recarregar certificados TLS carregados manualmente.

<a id="caddy-respond"></a>
### `caddy respond`

<pre><code class="cmd bash">caddy respond
	[-s, --status &lt;code&gt;]
	[-H, --header "&lt;Field&gt;: &lt;value&gt;"]
	[-b, --body &lt;content&gt;]
	[-l, --listen &lt;addr&gt;]
	[-v, --debug]
	[--access-log]
	[&lt;status|body&gt;]</code></pre>

Inicia um ou mais servidores HTTP simples e fixos, úteis para desenvolvimento, staging e alguns casos de produção. Pode ser útil para verificar ou depurar clientes HTTP, scripts ou até balanceadores de carga.

`--status` é o código HTTP a retornar.

`--header` adiciona um cabeçalho HTTP; espera-se o formato `Field: value`. Essa flag pode ser usada várias vezes.

`--body` especifica o corpo da resposta. Alternativamente, o corpo pode ser enviado via stdin.

`--listen` é o endereço de escuta, que pode ser qualquer [endereço de rede](/docs/conventions#network-addresses) reconhecido pelo Caddy, e pode incluir um intervalo de portas para iniciar vários servidores.

`--debug` habilita logging verboso de debug.

`--access-log` habilita o logging de acesso/requisição.

Sem opções, esse comando escuta em uma porta aleatória disponível e responde às requisições HTTP com uma resposta 200 vazia. O endereço de escuta pode ser customizado com `--listen` e sempre será impresso em stdout. Se o endereço de escuta incluir um intervalo de portas, vários servidores serão iniciados.

Se um argumento final sem nome for fornecido, ele será tratado como código de status (igual à flag `--status`) se for um número de 3 dígitos. Caso contrário, ele será usado como corpo da resposta (igual à flag `--body`). As flags `--status` e `--body` sempre sobrescrevem esse argumento.

O corpo pode ser fornecido de 3 formas: por uma flag, por um argumento final sem nome ao comando, ou via stdin (se a flag e o argumento não estiverem definidos). Há suporte a avaliação limitada de [template](https://pkg.go.dev/text/template) no corpo, com as seguintes variáveis:

Variable | Description
---------|-------------
`.N`       | Número do servidor
`.Port`    | Porta de escuta
`.Address` | Endereço de escuta

#### Exemplos

Resposta 200 vazia em uma porta aleatória:
<pre><code class="cmd bash">caddy respond</code></pre>

Resposta HTTP com corpo:
<pre><code class="cmd bash">caddy respond "Hello, world!"</code></pre>

Vários servidores e templates:
<pre><code class="cmd"><b>$ caddy respond --listen :2000-2004 "{{printf "I'm server {{.N}} on port {{.Port}}"}}"</b>

Server address: [::]:2000
Server address: [::]:2001
Server address: [::]:2002
Server address: [::]:2003
Server address: [::]:2004

<b>$ curl 127.0.0.1:2002</b>
I'm server 2 on port 2002</code></pre>

Enviando uma página de manutenção por pipe:
<pre><code class="cmd bash">cat maintenance.html | caddy respond \
	--listen :80 \
	--status 503 \
	--header "Content-Type: text/html"</code></pre>

<a id="caddy-reverse-proxy"></a>
### `caddy reverse-proxy`

<pre><code class="cmd bash">caddy reverse-proxy
	[-f, --from &lt;addr&gt;]
	(-t, --to &lt;addr&gt;)
	[-H, --header-up "&lt;Field&gt;: &lt;value&gt;"]
	[-d, --header-down "&lt;Field&gt;: &lt;value&gt;"]
	[-c, --change-host-header]
	[-r, --disable-redirects]
	[-i, --internal-certs]
	[-v, --debug]
	[--access-log]
	[--insecure]</code></pre>

Um reverse proxy simples, mas pronto para produção. Útil para implantações rápidas, demos e desenvolvimento.

Ele apenas encaminha tráfego HTTP(S) do endereço `--from` para o endereço `--to`. Vários endereços `--to` podem ser especificados repetindo a flag. Pelo menos um endereço `--to` é obrigatório. O endereço `--to` pode ter um intervalo de portas como atalho para expandir em vários upstreams.

A menos que especificado de outra forma nos endereços, o endereço `--from` será assumido como HTTPS se um hostname for fornecido, e o endereço `--to` será assumido como HTTP.

Se o endereço `--from` tiver host ou IP, o Caddy tentará servir o proxy sobre HTTPS com um certificado (a menos que isso seja sobrescrito pelo esquema HTTP ou pela porta).

Se estiver servindo HTTPS:
  - `--disable-redirects` pode ser usado para evitar o bind na porta HTTP.
  - `--internal-certs` pode ser usado para forçar a emissão de certificados usando a CA interna em vez de tentar emitir um certificado público.

Para proxy:
  - `--header-up` pode ser usado para definir um cabeçalho de requisição a ser enviado ao upstream.
  - `--header-down` pode ser usado para definir um cabeçalho de resposta a ser enviado de volta ao cliente.
  - `--change-host-header` define o cabeçalho Host da requisição para o endereço do upstream, em vez de usar por padrão o Host recebido.
  
    Isso é um atalho para `--header-up "Host: {http.reverse_proxy.upstream.hostport}"`
  
  - `--insecure` desabilita a verificação TLS com o upstream. AVISO: ISSO DESABILITA A SEGURANÇA AO NÃO VERIFICAR O CERTIFICADO DO UPSTREAM.
  
  - `--debug` habilita logging verboso.

Esse comando desabilita a admin API para facilitar a execução de várias instâncias em uma máquina de desenvolvimento local.

<a id="caddy-run"></a>
### `caddy run`

<pre><code class="cmd bash">caddy run
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--pidfile &lt;file&gt;]
	[-e, --environ]
	[--envfile &lt;file&gt;]
	[-r, --resume]
	[-w, --watch]</code></pre>

Executa o Caddy e bloqueia indefinidamente; isto é, modo "daemon".

`--config` especifica um arquivo de configuração inicial a ser carregado e usado imediatamente. Se for `-`, a configuração é lida de stdin. Se nenhuma configuração for especificada, o Caddy será executado com uma configuração em branco e usará as configurações padrão dos [endpoints da admin API](/docs/api), que podem ser usados para fornecer nova configuração. Como caso especial, se o diretório de trabalho atual tiver um arquivo chamado "Caddyfile" e o config adapter `caddyfile` estiver disponível (padrão), esse arquivo será carregado e usado para configurar o Caddy, mesmo sem flags de linha de comando.

`--adapter` é o nome do config adapter a ser usado ao carregar a configuração inicial, se houver. Essa flag não é necessária se o nome fornecido em `--config` começar com `Caddyfile` ou terminar com `.caddyfile`, o que assume o adapter `caddyfile`. Caso contrário, essa flag é obrigatória se o arquivo de configuração fornecido não estiver no formato JSON nativo do Caddy. Quaisquer avisos serão impressos no log, mas tenha em mente que qualquer adaptação sem erros será usada imediatamente, mesmo que haja avisos. Se você quiser revisar o resultado da adaptação antes, use o subcomando [`caddy adapt`](#caddy-adapt).

`--pidfile` grava o PID no arquivo especificado.

`--environ` imprime o ambiente antes de iniciar. É o mesmo que o comando `caddy environ`, mas não encerra depois de imprimir.

`--envfile` carrega variáveis de ambiente de um arquivo especificado, no formato `KEY=VALUE`. Comentários iniciados com `#` são suportados; chaves podem vir prefixadas com `export`; valores podem ser colocados entre aspas duplas (aspas duplas internas podem ser escapadas); valores multilinha também são suportados.

`--resume` usa a última configuração carregada que foi autosaved, sobrescrevendo `--config` (se presente). Usar essa flag garante durabilidade da configuração em reinícios de máquina ou do processo. Ela é mais útil em implantações centradas na [API](/docs/api).

`--watch` monitora o arquivo de configuração e o recarrega automaticamente após mudanças. ⚠️ Esse recurso é destinado apenas a ambientes de desenvolvimento local!

<aside class="advice">

Não pare o servidor para mudar a configuração enquanto estiver em produção! Isso causará downtime. (Deveria ser óbvio, mas você ficaria surpreso com a quantidade de reclamações que recebemos sobre isso.) Use o comando [`caddy reload`](#caddy-reload) em vez disso, ou envie um sinal `SIGUSR1` para o processo, que tem o mesmo efeito de `caddy reload` com a configuração atualmente carregada.

</aside>

<a id="caddy-start"></a>
### `caddy start`

<pre><code class="cmd bash">caddy start
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]
	[--pidfile &lt;file&gt;
	[-w, --watch]</code></pre>

Mesma coisa que [`caddy run`](#caddy-run), mas em segundo plano. Esse comando só bloqueia até que o processo em segundo plano esteja rodando com sucesso (ou falhe ao iniciar) e então retorna.

Observação: a flag `--config` não suporta `-` para ler a configuração de stdin.

O uso desse comando é desencorajado com serviços do sistema ou no Windows. No Windows, o processo filho permanecerá ligado ao terminal, então fechar a janela forçará a parada do Caddy, o que não é óbvio. Considere rodar o Caddy [como serviço](/docs/running) em vez disso.

Depois de iniciar, você pode usar [`caddy stop`](#caddy-stop) ou o endpoint da API [`POST /stop`](/docs/api#post-stop) para encerrar o processo em segundo plano.

<a id="caddy-stop"></a>
### `caddy stop`

<pre><code class="cmd bash">caddy stop
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

<aside class="tip">

Parar (e reiniciar) o servidor é algo separado de mudanças na configuração. **Não use o comando stop para mudar a configuração em produção, a menos que você queira downtime.** Use o comando [`caddy reload`](#caddy-reload) em vez disso.

</aside>


Para de forma graciosa o processo Caddy em execução (exceto o próprio processo do comando stop) e faz com que ele saia. Ele usa o endpoint [`POST /stop`](/docs/api#post-stop) da admin API para realizar um shutdown gracioso.

O endereço dessa requisição pode ser customizado com a flag `--address`, ou a partir do `--config` fornecido, se a admin API da instância em execução não estiver usando o endereço de escuta padrão.

Se você quiser parar a configuração atual, mas não quer encerrar o processo, use [`caddy reload`](#caddy-reload) com uma configuração vazia, ou o endpoint [`DELETE /config/`](/docs/api#delete-configpath).

<a id="caddy-storage"></a>
### `caddy storage`

<i>⚠️ Experimental</i>

Permite exportar e importar o conteúdo do storage de dados configurado do Caddy.

Isso é útil quando você precisa migrar de um [módulo de storage](/docs/json/storage/) para outro, exportando do antigo, atualizando sua configuração e importando para o novo.

O comando abaixo pode ser usado para copiar o storage entre diferentes módulos em uma única etapa, usando configs antiga e nova, fazendo o pipe da saída do export para o import.

```
$ caddy storage export -c Caddyfile.old -o- |
  caddy storage import -c Caddyfile.new -i-
```

<aside class="advice">

Observe que, ao usar [filesystem storage](/docs/conventions#data-directory), você precisa executar o comando export como o mesmo usuário que normalmente executa o Caddy; caso contrário, o local errado de storage poderá ser usado.

Por exemplo, ao executar o Caddy como um serviço [systemd](/docs/running#linux-service), ele rodará como o usuário `caddy`, então você deve executar os comandos export ou import como esse usuário. Isso normalmente pode ser feito com `sudo -u caddy <command>`.

</aside>

<a id="caddy-storage-export"></a>
#### `caddy storage export`

<pre><code class="cmd bash">caddy storage export
	-c, --config &lt;path&gt;
	[-o, --output &lt;path&gt;]</code></pre>

`--config` é o arquivo de configuração a carregar. Isso é obrigatório para que o módulo de storage correto seja conectado.

`--output` é o nome do arquivo para gravar o tarball. Se for `-`, a saída é gravada em stdout.

<a id="caddy-storage-import"></a>
#### `caddy storage import`

<pre><code class="cmd bash">caddy storage import
	-c, --config &lt;path&gt;
	-i, --input &lt;path&gt;</code></pre>

`--config` é o arquivo de configuração a carregar. Isso é obrigatório para que o módulo de storage correto seja conectado.

`--input` é o nome do arquivo tarball a ser lido. Se for `-`, a entrada é lida de stdin.

<a id="caddy-trust"></a>
### `caddy trust`

<pre><code class="cmd bash">caddy trust
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Instala um certificado raiz de uma CA gerenciada pelo [app PKI](/docs/json/apps/pki/) do Caddy em trust stores locais.

O Caddy tentará instalar automaticamente seus certificados raiz nos trust stores locais quando eles forem gerados pela primeira vez, mas isso pode falhar se o Caddy não tiver permissões adequadas para gravar no trust store. Esse comando é necessário para pré-instalar os certificados antes de usá-los, se o processo do servidor rodar como usuário sem privilégios (como via systemd). Talvez seja necessário usar `sudo` em sistemas Unix.

Por padrão, esse comando instala o certificado raiz da CA padrão do Caddy (isto é, "local"). Você pode especificar o ID de outra CA com a flag `--ca`.

Esse comando tentará conectar-se à [admin API](/docs/api) do Caddy para buscar o certificado raiz, usando o endpoint [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaltidgtcertificates). Você pode especificar explicitamente `--address`, ou usar `--config` para carregar o endereço da admin a partir da sua configuração, se a instância em execução não estiver usando o endereço padrão.

Você também pode usar o binário `caddy` com esse comando para instalar certificados em outras máquinas da sua rede, se a admin API for tornada acessível a outras máquinas -- tenha cuidado para não expor a admin API a clientes não confiáveis.

<a id="caddy-untrust"></a>
### `caddy untrust`

<pre><code class="cmd bash">caddy untrust
	[-p, --cert &lt;path&gt;]
	[--ca &lt;id&gt;]
	[--address &lt;interface&gt;]
	[-c, --config &lt;path&gt; [-a, --adapter &lt;name&gt;]]</code></pre>

Remove a confiança de um certificado raiz do(s) trust store(s) local(is).

Esse comando remove a confiança; ele não necessariamente apaga o certificado raiz completamente dos trust stores. Assim, confiar e remover a confiança repetidamente de novos certificados pode encher bancos de confiança.

Esse comando não apaga nem modifica arquivos de certificado do storage configurado do Caddy.

Esse comando pode ser usado de duas formas:
- Especificando um caminho direto para o certificado raiz a remover, com a flag `--cert`.
- Buscando o certificado raiz na [admin API](/docs/api) usando o endpoint [`GET /pki/ca/<id>/certificates`](/docs/api#get-pkicaidcertificates). Esse é o comportamento padrão se nenhuma flag for fornecida.

Se a admin API for usada, o ID da CA assume o padrão "local". Você pode especificar o ID de outra CA com a flag `--ca`. Você pode especificar `--address`, ou usar `--config` para carregar o endereço da admin da sua configuração, se a instância em execução não estiver usando o endereço padrão.

<a id="caddy-upgrade"></a>
### `caddy upgrade`

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy upgrade
	[-k, --keep-backup]</code></pre>

Substitui o binário atual do Caddy pela versão mais recente da [nossa página de download](/download) com os mesmos módulos instalados, incluindo todos os plugins de terceiros registrados no site do Caddy.

As atualizações não interrompem servidores em execução; atualmente, o comando apenas substitui o binário no disco. Isso pode mudar no futuro se encontrarmos uma boa forma de fazer isso.

O processo de atualização é tolerante a falhas; o binário atual é primeiro salvo como backup (copiado ao lado do atual) e restaurado automaticamente se algo der errado. Se você quiser manter o backup após a conclusão do processo de atualização, pode usar a opção `--keep-backup`.

Esse comando pode exigir privilégios elevados se o seu usuário não tiver permissão para gravar no arquivo executável.

<a id="caddy-add-package"></a>
### `caddy add-package`

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy add-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

Da mesma forma que `caddy upgrade`, substitui o binário atual do Caddy pela versão mais recente com os mesmos módulos instalados, _mais_ os pacotes listados como argumentos incluídos no novo binário. Encontre a lista de pacotes que você pode instalar na [nossa página de download](/download). Cada argumento deve ser o nome completo do pacote.

Por exemplo:

<pre><code class="cmd bash">caddy add-package github.com/caddy-dns/cloudflare</code></pre>

<a id="caddy-remove-package"></a>
### `caddy remove-package`

<i>⚠️ Experimental</i>

<pre><code class="cmd bash">caddy remove-package &lt;packages...&gt;
	[-k, --keep-backup]</code></pre>

Da mesma forma que `caddy upgrade`, substitui o binário atual do Caddy pela versão mais recente com os mesmos módulos instalados, mas _sem_ os pacotes listados como argumentos, se eles existirem no binário atual. Execute `caddy list-modules --packages` para ver a lista de nomes de pacotes de módulos não padrão incluídos no binário atual.

<a id="caddy-validate"></a>
### `caddy validate`

<pre><code class="cmd bash">caddy validate
	[-c, --config &lt;path&gt;]
	[-a, --adapter &lt;name&gt;]
	[--envfile &lt;file&gt;]</code></pre>

Valida um arquivo de configuração e então encerra. Esse comando desserializa a configuração, depois carrega e provisiona todos os módulos como se fosse iniciar a configuração, mas a configuração não chega a ser iniciada de fato. Isso expõe erros em uma configuração que surgem durante as fases de carregamento ou provisionamento e é uma verificação de erro mais forte do que simplesmente serializar uma configuração como JSON.

`--config` é o arquivo de configuração a validar. Se for `-`, a configuração é lida de stdin. O padrão é o `Caddyfile` no diretório atual, se houver.

`--adapter` é o nome do config adapter a ser usado. Essa flag não é necessária se o nome fornecido em `--config` começar com `Caddyfile` ou terminar com `.caddyfile`, o que assume o adapter `caddyfile`. Caso contrário, essa flag é obrigatória se o arquivo de configuração fornecido não estiver no formato JSON nativo do Caddy.

`--envfile` carrega variáveis de ambiente de um arquivo especificado, no formato `KEY=VALUE`. Comentários iniciados com `#` são suportados; chaves podem ser prefixadas com `export`; valores podem ser colocados entre aspas duplas (aspas duplas internas podem ser escapadas); valores multilinha também são suportados.

<a id="caddy-version"></a>
### `caddy version`
<pre><code class="cmd bash">caddy version</code></pre>

Mostra a versão e encerra.

## Signals

O Caddy captura certos sinais e ignora outros. Sinais podem iniciar comportamentos específicos do processo.

Signal | Comportamento
-------|----------
`SIGINT` | Saída graciosa. Envie o sinal novamente para forçar a saída imediata.
`SIGQUIT` | Encerra o Caddy imediatamente, mas ainda limpa locks no storage porque isso é importante.
`SIGTERM` | Saída graciosa.
`SIGUSR1` | Recarrega o arquivo de configuração, mas apenas se iniciado com `caddy run` (sem `--resume`) e se nenhuma mudança na configuração tiver sido feita pela [API](/docs/api) (incluindo [`caddy reload`]#caddy-reload)).
`SIGUSR2` | Ignorado.
`SIGHUP` | Ignorado.

Uma saída graciosa significa que novas conexões deixam de ser aceitas e as conexões existentes são drenadas antes que o socket seja fechado. Pode haver um período de graça (e ele é configurável). Quando o período termina, as conexões são encerradas à força. Locks no storage e outros recursos que módulos individuais precisam liberar são limpos durante um shutdown gracioso.

Quando um sinal para recarregar a configuração (`SIGUSR1`) é recebido, ele age como um reload forçado da configuração (isto é, recarrega mesmo que o texto da configuração não tenha mudado), o que pode recarregar arquivos dependentes como certificados TLS do disco.

Reloads de configuração baseados em sinal só ficam habilitados se o Caddy for iniciado com `caddy run` com um arquivo de configuração. Eles ficam desabilitados (sinais ignorados, com aviso no log) se o Caddy for iniciado com `--resume` (já que isso implica um fluxo baseado em API), ou se qualquer alteração de configuração for recebida pela admin API, ou se `caddy reload` for executado com um nome de arquivo ou config adapter _diferente_ daquele com que foi iniciado originalmente. Isso evita conflitos entre métodos de recarregamento.

## Exit codes

O Caddy retorna um código quando o processo termina:

Code | Meaning
-----|---------
`0` | Saída normal.
`1` | Falha na inicialização. **Não reinicie automaticamente o processo; ele provavelmente falhará novamente, a menos que mudanças sejam feitas.**
`2` | Saída forçada. O Caddy foi forçado a encerrar sem limpar recursos.
`3` | Falha ao encerrar. O Caddy saiu com alguns erros durante a limpeza.

No bash, você pode obter o código de saída do último comando com `echo $?`.
