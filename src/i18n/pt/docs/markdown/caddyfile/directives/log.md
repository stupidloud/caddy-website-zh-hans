---
title: log (diretiva do Caddyfile)
---

<script>
ready(function() {
	// Corrige > em blocos de código
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('>')) {
			// Pula se terminar com >
			if (item.textContent.trim().endsWith('>')) return;
			// Substitui > por <span class="p">&gt;</span>
			item.innerHTML = item.innerHTML.replace(/&gt;/g, '<span class="p">&gt;</span>');
		}
	});

	// Vamos adicionar links a todas as subdiretivas se um anchor correspondente for encontrado na página.
	addLinksToSubdirectives();
});
</script>

# log

Habilita e configura o logging de requisições HTTP (também conhecido como access logs).

<aside class="tip">

Para configurar os logs de runtime do Caddy, veja a [opção global `log`](/docs/caddyfile/options#log) em vez disso.

</aside>


A diretiva `log` se aplica aos hostnames do bloco de site em que aparece, a menos que seja sobrescrita pela subdiretiva `hostnames`.

Quando configurada, por padrão todas as requisições ao site serão logadas. Para pular condicionalmente algumas requisições do logging, use a [`diretiva log_skip`](log_skip).

Para adicionar campos personalizados às entradas de log, use a [`diretiva log_append`](log_append).


- [Sintaxe](#syntax)
- [Módulos de saída](#output-modules)
  - [stderr](#stderr)
  - [stdout](#stdout)
  - [discard](#discard)
  - [file](#file)
  - [net](#net)
- [Módulos de formato](#format-modules)
  - [console](#console)
  - [json](#json)
  - [filter](#filter)
    - [delete](#delete)
	- [rename](#rename)
	- [replace](#replace)
	- [ip_mask](#ip-mask)
	- [query](#query)
	- [cookie](#cookie)
	- [regexp](#regexp)
	- [hash](#hash)
  - [append](#append)
- [Exemplos](#examples)

Por padrão, cabeçalhos com informações potencialmente sensíveis (`Cookie`, `Set-Cookie`, `Authorization` e `Proxy-Authorization`) serão registrados como `REDACTED` nos access logs. Esse comportamento pode ser desativado com a [opção global de servidor `log_credentials`](/docs/caddyfile/options#log-credentials).


<a id="syntax"></a>
## Sintaxe

```caddy-d
log [<logger_name>] {
	hostnames <hostnames...>
	no_hostname
	output <writer_module> ...
	format <encoder_module> ...
	level  <level>
	sampling {
		interval   <duration>
		first      <number>
		thereafter <number>
	}
}
```

- **logger_name** <span id="logger_name"/> é uma substituição opcional do nome do logger para este site.

  Por padrão, um nome de logger é gerado automaticamente, por exemplo `log0`, `log1` e assim por diante, dependendo da ordem dos sites no Caddyfile. Isso só é útil se você quiser referenciar de forma confiável a saída desse logger a partir de outro logger definido nas opções globais. Veja [um exemplo](#multiple-outputs) abaixo.

- **hostnames** <span id="hostnames"/> é uma substituição opcional dos hostnames aos quais esse logger se aplica.

  Por padrão, o logger se aplica aos hostnames do bloco de site em que aparece, isto é, os endereços do site. Isso é útil se você quiser definir loggers diferentes por subdomínio em um [bloco de site curinga](/docs/caddyfile/patterns#wildcard-certificates). Veja [um exemplo](#wildcard-logs) abaixo.

- **no_hostname** <span id="no_hostname"/> impede que o logger seja associado a qualquer hostname do bloco de site. Por padrão, o logger é associado ao [endereço do site](/docs/caddyfile/concepts#addresses) em que a diretiva `log` aparece.

  Isso é útil quando você quer logar requisições em arquivos diferentes com base em alguma condição, como o caminho ou método da requisição, usando a [`diretiva log_name`](log_name).

- **output** <span id="output"/> configura onde escrever os logs. Veja os [módulos de `output`](#output-modules) abaixo.

  Padrão: `stderr`.

- **format** <span id="format"/> descreve como codificar, ou formatar, os logs. Veja os [módulos de `format`](#format-modules) abaixo.

  Padrão: `console` se `stderr` for detectado como terminal, `json` caso contrário.

- **level** <span id="level"/> é o nível mínimo de entrada a ser logado. Padrão: `INFO`.

  Observe que access logs atualmente emitem apenas logs de nível `INFO` e `ERROR`.

- **sampling** <span id="sampling"/> configura amostragem de logs para reduzir o volume. Se `sampling` for especificado, ele é habilitado, com os padrões abaixo entrando em vigor. Omiti-lo desativa a amostragem.

  - **interval** é a [janela de duração](/docs/conventions#durations) ao longo da qual a amostragem será feita. Padrão: `1s` (desabilitado).

  - **first** é quantos logs manter em um dado nível e mensagem para cada intervalo. Padrão: `100`.

  - **thereafter** é quantos logs pular em cada intervalo depois dos primeiros logs mantidos. Padrão: `100`.

  Por exemplo, com `interval 1s`, `first 5` e `thereafter 10`, em cada intervalo de 10 segundos os primeiros 5 registros de log serão mantidos, e depois será permitido um a cada 10 logs com o mesmo nível e mensagem dentro desse segundo.


<a id="output-modules"></a>
### Módulos de saída

A subdiretiva **output** permite personalizar onde os logs são escritos.

#### stderr

Saída de erro padrão (console, é o padrão).

```caddy-d
output stderr
```

#### stdout

Saída padrão (console).

```caddy-d
output stdout
```

#### discard

Sem saída.

```caddy-d
output discard
```

#### file

Um arquivo. Por padrão, os arquivos de log são rotacionados ("rolled") com base no tamanho para evitar exaustão de espaço em disco.

O log rolling é fornecido por [timberjack <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/DeRuina/timberjack)

<aside class="tip">

**Uma observação sobre recarregar opções de arquivos de log:** é necessário reiniciar o servidor para aplicar mudanças de configuração a um dado arquivo de saída.
As mudanças não serão aplicadas no momento do reload do servidor, a menos que você adicione um novo nome de arquivo de log.

</aside>

```caddy-d
output file <filename> {
	mode          <mode>
	roll_disabled
	roll_size     <size>
	roll_interval <duration>
	roll_minutes  <minutes...>
	roll_at	      <times...>
	roll_uncompressed
	roll_local_time
	roll_keep     <num>
	roll_keep_for <days>
	backup_time_format <format>
}
```

- **&lt;filename&gt;** é o caminho do arquivo de log.

  Quando rotacionados, os arquivos são renomeados usando o template `<name>-<timestamp>-<reason>.log`. O timestamp é formatado de acordo com a opção [`backup_time_format`](#backup_time_format). O motivo é `size` ou `time`, dependendo do que acionou a rotação. Se o arquivo for compactado, `.gz` será anexado ao nome do arquivo.

   Por exemplo, se o nome do arquivo for `access.log`, um arquivo rotacionado pode se chamar `access-2026-01-30T22-15-42.123-size.log` se tiver sido rotacionado por tamanho, ou `access-2025-01-30T00-00-00.000-time.log` se tiver sido rotacionado por tempo.

- **mode** <span id="mode"/> é o modo/permissões Unix do arquivo de log. O modo consiste em 1 a 4 dígitos octais (mesmo formato numérico aceito pelo comando Unix [chmod <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/Chmod), exceto que um modo todo zero é interpretado como o modo padrão `600`).

  Por exemplo: `0600` define o modo como `rw-,---,---` (acesso de leitura/escrita para o proprietário do arquivo de log, e nenhum acesso para mais ninguém); `0640` define o modo como `rw-,r--,---` (acesso de leitura/escrita para o proprietário, apenas leitura para o grupo); `644` define o modo como `rw-,r--,r--`, fornecendo acesso de leitura/escrita ao proprietário do arquivo de log, mas apenas leitura para o grupo e outros usuários.

- **roll_disabled** <span id="roll_disabled"/> desativa o log rolling. Isso pode levar à exaustão de espaço em disco, então use isso apenas se seus arquivos de log forem mantidos de outra forma.

- **roll_size** <span id="roll_size"/> é o tamanho no qual o arquivo de log deve ser rotacionado. A implementação atual suporta resolução em megabytes; valores fracionários são arredondados para cima para o próximo megabyte inteiro. Por exemplo, `1.1MiB` é arredondado para `2MiB`.

  Isso está sempre habilitado. Se uma escrita nos logs fizer o arquivo exceder o tamanho especificado, o log será imediatamente rotacionado. O nome do arquivo de backup incluirá `size` como motivo.

  Padrão: `100MiB`

- **roll_interval** <span id="roll_interval"/> é a duração máxima entre rotações de log. O valor é uma [string de duração](/docs/conventions#durations) após a qual o arquivo de log será rotacionado.

  Quando habilitado, o arquivo é rotacionado na próxima escrita para os logs depois que essa duração tiver passado desde a última rotação. O nome do arquivo de backup incluirá `time` como motivo.

  Observe que, se definido como `24h`, isso não significa necessariamente rotação à meia-noite, mas sim no marco de 24 horas desde a última rotação. Se a rotação ocorrer por tamanho, então o horário da próxima rotação será deslocado em relação à rotação anterior. Você pode usar as opções `roll_at` ou `roll_minutes` para rotacionar em horários específicos.

  Padrão: desabilitado

- **roll_minutes** <span id="roll_minutes"/> é uma lista de valores de minuto (0-59) nos quais o arquivo de log deve ser rotacionado. Por exemplo, `10 40` rotacionaria o arquivo de log a cada 30 minutos em `xx:10` e `xx:40` de cada hora. As rotações são alinhadas ao minuto do relógio (segundo 0).

  Habilitar isso cria um timer goroutine que dispara uma rotação de log nos valores de minuto especificados (isto é, introduz uma pequena quantidade de processamento em segundo plano). Isso opera além de `roll_interval` e `roll_size`. O nome do arquivo de backup incluirá `time` como motivo.

  Padrão: desabilitado

- **roll_at** <span id="roll_at"/> é uma lista de valores de horário (no formato 24 horas) nos quais o arquivo de log deve ser rotacionado. Por exemplo, `00:00 12:00` rotacionaria o arquivo de log duas vezes por dia, à meia-noite e ao meio-dia. As rotações são alinhadas ao minuto do relógio (segundo 0).

  Habilitar isso cria um timer goroutine que dispara uma rotação de log nos horários especificados (isto é, introduz uma pequena quantidade de processamento em segundo plano). Isso opera além de `roll_interval` e `roll_size`. O nome do arquivo de backup incluirá `time` como motivo.

  Padrão: desabilitado

- **roll_uncompressed** <span id="roll_uncompressed"/> desativa a compressão gzip dos logs.

  Padrão: a compressão `gzip` está habilitada.

- **roll_local_time** <span id="roll_local_time"/> faz a rotação usar timestamps locais nos nomes dos arquivos.
  Padrão: usa tempo UTC.

- **roll_keep** <span id="roll_keep"/> é quantos arquivos de log devem ser mantidos antes de apagar os mais antigos. Dispara quando um novo arquivo de log é criado.

  Padrão: `10`

- **roll_keep_for** <span id="roll_keep_for"/> é por quanto tempo manter arquivos rotacionados, como uma [string de duração](/docs/conventions#durations). Dispara quando um novo arquivo de log é criado.
  A implementação atual suporta resolução em dias; valores fracionários são arredondados para cima para o próximo dia inteiro. Por exemplo, `36h` (1,5 dia) é arredondado para `48h` (2 dias).
  
  Padrão: `2160h` (90 dias)

- **backup_time_format** <span id="backup_time_format"/> é o formato de tempo a usar nos nomes dos arquivos de backup. Deve ser uma string de layout de tempo válida; veja a [documentação do Go](https://pkg.go.dev/time#pkg-constants) para detalhes completos.

  Padrão: `2006-01-02T15-04-05`


#### net

Um socket de rede. Se o socket cair, os logs serão enviados para stderr enquanto tenta se reconectar.

```caddy-d
output net <address> {
	dial_timeout <duration>
	soft_start
}
```

- **&lt;address&gt;** é o [endereço](/docs/conventions#network-addresses) para onde escrever os logs.

- **dial_timeout** <span id="dial_timeout"/> é quanto tempo esperar por uma conexão bem-sucedida com o socket de log. As emissões de log podem ficar bloqueadas por até esse tempo se o socket cair.

- **soft_start** <span id="soft_start"/> ignora erros ao conectar ao socket, permitindo carregar sua configuração mesmo se o serviço remoto de logs estiver indisponível. Os logs serão emitidos para stderr em vez disso.


<a id="format-modules"></a>
### Módulos de formato

A subdiretiva **format** permite personalizar como os logs são codificados (formatados). Ela aparece dentro de um bloco `log`.

<aside class="tip">

**Uma observação sobre Common Log Format (CLF):** CLF conflita com logs estruturados modernos. Para transformar seus access logs no Common Log Format depreciado, use o [plugin `transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder).

</aside>

Além da sintaxe de cada encoder individual, estas propriedades comuns podem ser definidas na maioria dos encoders:

```caddy-d
format <encoder_module> {
	message_key     <key>
	level_key       <key>
	time_key        <key>
	name_key        <key>
	caller_key      <key>
	stacktrace_key  <key>
	line_ending     <char>
	time_format     <format>
	time_local
	duration_format <format>
	level_format    <format>
}
```

- **message_key** <span id="message_key"/> A chave do campo de mensagem da entrada de log. Padrão: `msg`

- **level_key** <span id="level_key"/> A chave do campo de nível da entrada de log. Padrão: `level`

- **time_key** <span id="time_key"/> A chave do campo de tempo da entrada de log. Padrão: `ts`
- **name_key** <span id="name_key"/> A chave do campo de nome da entrada de log. Padrão: `name`

- **caller_key** <span id="caller_key"/> A chave do campo de caller da entrada de log.

- **stacktrace_key** <span id="stacktrace_key"/> A chave do campo de stacktrace da entrada de log.

- **line_ending** <span id="line_ending"/> As quebras de linha a usar.

- **time_format** <span id="time_format"/> O formato dos timestamps.
  Padrão: `wall_milli` se o formato padrão for `console`, `unix_seconds_float` caso contrário.
  
  Pode ser um dos seguintes:
  - `unix_seconds_float` Número decimal de segundos desde a época Unix.
  - `unix_milli_float` Número decimal de milissegundos desde a época Unix.
  - `unix_nano` Número inteiro de nanossegundos desde a época Unix.
  - `iso8601` Exemplo: `2006-01-02T15:04:05.000Z0700`
  - `rfc3339` Exemplo: `2006-01-02T15:04:05Z07:00`
  - `rfc3339_nano` Exemplo: `2006-01-02T15:04:05.999999999Z07:00`
  - `wall` Exemplo: `2006/01/02 15:04:05`
  - `wall_milli` Exemplo: `2006/01/02 15:04:05.000`
  - `wall_nano` Exemplo: `2006/01/02 15:04:05.000000000`
  - `common_log` Exemplo: `02/Jan/2006:15:04:05 -0700`
  - Ou qualquer string de layout de tempo compatível; veja a [documentação do Go](https://pkg.go.dev/time#pkg-constants) para detalhes completos.
  
  Observe que as partes da string de formato são constantes especiais do layout; então `2006` é o ano, `01` é o mês, `Jan` é o mês como string, `02` é o dia. Não use os números reais da data atual na string de formato.

- **time_local** <span id="time_local"/> Registra com a hora local do sistema em vez do padrão UTC.

- **duration_format** <span id="duration_format"/> O formato das durações.

  Padrão: `seconds`.
  
  Pode ser um dos seguintes:
  - `s`, `second` ou `seconds` Número decimal de segundos decorridos.
  - `ms`, `milli` ou `millis` Número decimal de milissegundos decorridos.
  - `ns`, `nano` ou `nanos` Número inteiro de nanossegundos decorridos.
  - `string` Usa o formato de string embutido do Go, por exemplo `1m32.05s` ou `6.31ms`.

- **level_format** <span id="level_format"/> O formato dos níveis.

  Padrão: `color` se o formato padrão for `console`, `lower` caso contrário.
  
  Pode ser um dos seguintes:
  - `lower` Minúsculas.
  - `upper` Maiúsculas.
  - `color` Maiúsculas, com cores ANSI.
  

#### console

O encoder console formata a entrada de log para legibilidade humana, preservando alguma estrutura.

```caddy-d
format console
```

#### json

Formata cada entrada de log como um objeto JSON.

```caddy-d
format json
```


#### filter

Permite filtragem por campo.

```caddy-d
format filter {
	fields {
		<field> <filter> ...
	}
	<field> <filter> ...
	wrap <encode_module> ...
}
```

Campos aninhados podem ser referenciados representando um nível de aninhamento com `>`. Em outras palavras, para um objeto como `{"a":{"b":0}}`, o campo interno pode ser referenciado como `a>b`.

Os seguintes campos são fundamentais para o log e não podem ser filtrados porque são adicionados pela biblioteca de logging subjacente como casos especiais: `ts`, `level`, `logger` e `msg`.

Especificar `wrap` é opcional; se omitido, um padrão é escolhido dependendo de o módulo de saída atual ser [`stderr`](#stderr) ou [`stdout`](#stdout), e se for um terminal interativo, caso em que [`console`](#console) é escolhido, caso contrário [`json`](#json) é escolhido.

Como atalho, o bloco `fields` pode ser omitido e os filtros podem ser especificados diretamente dentro do bloco `filter`.


Estes são os filtros disponíveis:

##### delete

Marca um campo para ser ignorado na codificação.

```caddy-d
<field> delete
```


##### rename

Renomeia a chave de um campo de log.

```caddy-d
<field> rename <key>
```


##### replace

Marca um campo para ser substituído pela string fornecida no momento da codificação.

```caddy-d
<field> replace <replacement>
```


<a id="ip-mask"></a>
##### ip_mask

Mascarar endereços IP no campo usando uma máscara CIDR, isto é, o número de bits do IP a manter, começando pela esquerda. Se o campo for um array de strings (por exemplo, cabeçalhos HTTP), cada valor no array é mascarado. O valor pode ser uma string com endereços IP separados por vírgulas.

Há configuração separada para endereços IPv4 e IPv6, já que eles têm números totais de bits diferentes.

Os campos mais comuns a filtrar seriam:
- `request>remote_ip` para o cliente que se conecta diretamente
- `request>client_ip` para o "cliente real" analisado quando [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) está configurado
- `request>headers>X-Forwarded-For` se estiver atrás de um reverse proxy

```caddy-d
<field> ip_mask [<ipv4> [<ipv6>]] {
	ipv4 <cidr>
	ipv6 <cidr>
}
```


##### query

Marca um campo para que uma ou mais ações sejam executadas, manipulando a parte de query de um campo URL. O campo mais comum a filtrar seria `request>uri`.

```caddy-d
<field> query {
	delete  <key>
	replace <key> <replacement>
	hash    <key>
}
```

As ações disponíveis são:

- **delete** remove a chave fornecida da query.

- **replace** substitui o valor da chave de query por **replacement**. Útil para inserir um placeholder de redaction; você verá que a chave estava na URL, mas o valor ficará oculto.

- **hash** substitui o valor da chave de query pelos primeiros 4 bytes do hash SHA-256 do valor, em hexadecimal minúsculo. Útil para obscurecer o valor se ele for sensível, mas ainda permitir notar se cada requisição tinha um valor diferente.


##### cookie

Marca um campo para que uma ou mais ações sejam executadas, manipulando o valor de um cabeçalho HTTP `Cookie`. O campo mais comum a filtrar seria `request>headers>Cookie`.

```caddy-d
<field> cookie {
	delete  <name>
	replace <name> <replacement>
	hash    <name>
}
```

As ações disponíveis são:

- **delete** remove do cabeçalho o cookie fornecido pelo nome.

- **replace** substitui o valor do cookie fornecido por **replacement**. Útil para inserir um placeholder de redaction; você verá que o cookie estava no cabeçalho, mas o valor ficará oculto.

- **hash** substitui o valor do cookie pelos primeiros 4 bytes do hash SHA-256 do valor, em hexadecimal minúsculo. Útil para obscurecer o valor se ele for sensível, mas ainda permitir notar se cada requisição tinha um valor diferente.

Se muitas ações forem definidas para o mesmo nome de cookie, apenas a primeira ação será aplicada.


##### regexp

Marca um campo para que uma substituição por expressão regular seja aplicada no momento da codificação. Se o campo for um array de strings (por exemplo, cabeçalhos HTTP), cada valor no array recebe as substituições.

```caddy-d
<field> regexp <pattern> <replacement>
```

A linguagem de expressão regular usada é RE2, incluída no Go. Veja a [referência de sintaxe do RE2](https://github.com/google/re2/wiki/Syntax) e a [visão geral da sintaxe de regexp do Go](https://pkg.go.dev/regexp/syntax).

Na string de substituição, grupos de captura podem ser referenciados com `${group}`, onde `group` é o nome ou o número do grupo de captura na expressão. O grupo de captura `0` é a correspondência completa da regexp, `1` é o primeiro grupo de captura, `2` é o segundo grupo de captura, e assim por diante.


##### hash

Marca um campo para ser substituído pelos primeiros 4 bytes (8 caracteres hex) do hash SHA-256 do valor no momento da codificação. Se o campo for um array de strings (por exemplo, cabeçalhos HTTP), cada valor no array é hashado.

Útil para obscurecer o valor se ele for sensível, mas ainda permitir notar se cada requisição tinha um valor diferente.

```caddy-d
<field> hash
```

#### append

Acrescenta campo(s) a todas as entradas de log.

```caddy-d
format append {
	fields {
		<field> <value>
	}
	<field> <value>
	wrap <encode_module> ...
}
```

É mais útil para adicionar informações sobre a instância do Caddy que está produzindo as entradas de log, possivelmente via uma variável de ambiente. Os valores dos campos podem ser placeholders globais (por exemplo, `{env.*}`), mas _não_ placeholders por requisição, porque os logs são escritos fora do contexto da requisição HTTP.

Especificar `wrap` é opcional; se omitido, um padrão é escolhido dependendo de o módulo de saída atual ser [`stderr`](#stderr) ou [`stdout`](#stdout), e se for um terminal interativo, caso em que [`console`](#console) é escolhido, caso contrário [`json`](#json) é escolhido.

O bloco `fields` pode ser omitido e os campos podem ser especificados diretamente dentro do bloco `append`.


<a id="examples"></a>
## Exemplos

Habilitar logging de acesso para o logger padrão.

Em outras palavras, por padrão isso registra em `stderr`, mas isso pode ser alterado reconfigurando o logger `default` com a [opção global `log`](/docs/caddyfile/options#log):

```caddy
example.com {
	log
}
```


Escrever logs em um arquivo (com log rolling, que é habilitado por padrão):

```caddy
example.com {
	log {
		output file /var/log/access.log
	}
}
```


Personalizar o log rolling, rotacionando diariamente à meia-noite ou quando o arquivo de log atingir 1 GB (o que acontecer primeiro), e mantendo 5 arquivos rotacionados ou 30 dias de logs:

```caddy
example.com {
	log {
		output file /var/log/access.log {
			roll_at 00:00
			roll_size 1gb
			roll_keep 5
			roll_keep_for 720h
		}
	}
}
```


Remover o cabeçalho de requisição `User-Agent` dos logs:

```caddy
example.com {
	log {
		format filter {
			request>headers>User-Agent delete
		}
	}
}
```


Redigir vários cookies sensíveis. (Observe que alguns cabeçalhos sensíveis são registrados com valores vazios por padrão; veja a [opção global `log_credentials`](/docs/caddyfile/options#log-credentials) para habilitar o logging de valores do cabeçalho `Cookie`):

```caddy
example.com {
	log {
		format filter {
			request>headers>Cookie cookie {
				replace session REDACTED
				delete secret
			}
		}
	}
}
```


Mascarar o endereço remoto da requisição, mantendo os primeiros 16 bits (isto é, 255.255.0.0) para endereços IPv4 e os primeiros 32 bits para endereços IPv6.

Observe que, desde o Caddy v2.7, tanto `remote_ip` quanto `client_ip` são registrados, onde `client_ip` é o IP "real" quando [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies) está configurado:

```caddy
example.com {
	log {
		format filter {
			request>remote_ip ip_mask 16 32
			request>client_ip ip_mask 16 32
		}
	}
}
```


Para acrescentar um ID de servidor de uma variável de ambiente a todas as entradas de log, e encadear isso com um `filter` para excluir um cabeçalho:

```caddy
example.com {
	log {
		format append {
			server_id {env.SERVER_ID}
			wrap filter {
				request>headers>Cookie delete
			}
		}
	}
}
```


<span id="wildcard-logs" /> Para escrever arquivos de log separados para cada subdomínio em um [bloco de site curinga](/docs/caddyfile/patterns#wildcard-certificates), sobrescrevendo `hostnames` para cada logger. Isso usa um [snippet](/docs/caddyfile/concepts#snippets) para evitar repetição:

```caddy
(subdomain-log) {
	log {
		hostnames {args[0]}
		output file /var/log/{args[0]}.log
	}
}

*.example.com {
	import subdomain-log foo.example.com
	@foo host foo.example.com
	handle @foo {
		respond "foo"
	}

	import subdomain-log bar.example.com
	@bar host bar.example.com
	handle @bar {
		respond "bar"
	}
}
```

<span id="multiple-outputs" /> Para escrever os access logs de um subdomínio específico em dois arquivos diferentes, com formatos diferentes (um com o [plugin `transform-encoder` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder) e o outro com [`json`](#json)).

Isso funciona sobrescrevendo o nome do logger como `foo` no bloco de site, e então incluindo os access logs produzidos por esse logger nos dois loggers nas opções globais com `include http.log.access.foo`:

```caddy
{
	log access-formatted {
		include http.log.access.foo
		output file /var/log/access-foo.log
		format transform "{common_log}"
	}

	log access-json {
		include http.log.access.foo
		output file /var/log/access-foo.json
		format json
	}
}

foo.example.com {
	log foo
}
```

<span id="sampling-example" /> Para reduzir o volume de logs com amostragem, por exemplo para manter as primeiras 5 requisições por segundo e depois 1 a cada 10 requisições:

```caddy
example.com {
	log {
		sampling {
			interval   1s
			first      5
			thereafter 10
		}
	}
}
```
