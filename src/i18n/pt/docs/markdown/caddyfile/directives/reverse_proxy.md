---
title: reverse_proxy (diretiva do Caddyfile)
---

<script>
ready(function() {
	// Corrige os matchers de resposta para renderizarem com a cor certa,
	// e cria links para a seção de matchers de resposta
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Matcher de resposta">${text}</a>`;
		}
	});

	// Corrige o placeholder de matcher
	const nameMatchers = $$_('pre.chroma .nd');
	for (let item of nameMatchers) {
		if (item.innerText.includes('@name')) {
			item.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Matcher de resposta">@name</a>';
			break;
		}
	}
	
	const replaceStatusElements = $$_('pre.chroma .k');
	for (let item of replaceStatusElements) {
		if (item.innerText.includes('replace_status') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Matcher de resposta">[&lt;matcher&gt;]</a>';
			break;
		}
	}
	
	const handleResponseElements = $$_('pre.chroma .k');
	for (let item of handleResponseElements) {
		if (item.innerText.includes('handle_response') && item.nextElementSibling) {
			const next = item.nextElementSibling;
			const span = document.createElement('span');
			span.className = 'nd';
			next.parentNode.insertBefore(span, next);
			span.appendChild(next);
			span.innerHTML = '<a href="/docs/caddyfile/response-matchers" style="color: inherit;" title="Matcher de resposta">[&lt;matcher&gt;]</a>';
			break;
		}
	}

	// Vamos adicionar links a todas as subdiretivas se um anchor correspondente for encontrado na página.
	addLinksToSubdirectives();
});
</script>

# reverse_proxy

Faz proxy de requisições para um ou mais backends com opções configuráveis de transporte, balanceamento de carga, health checks, manipulação de requisição e buffering.

- [Sintaxe](#syntax)
- [Upstreams](#upstreams)
  - [Endereços de upstream](#upstream-addresses)
  - [Upstreams dinâmicos](#dynamic-upstreams)
    - [SRV](#srv)
    - [A/AAAA](#aaaaa)
	- [Multi](#multi)
- [Balanceamento de carga](#load-balancing)
  - [Active health checks](#active-health-checks)
  - [Passive health checks](#passive-health-checks)
  - [Eventos](#events)
- [Streaming](#streaming)
- [Cabeçalhos](#headers)
- [Rewrites](#rewrites)
- [Transports](#transports)
  - [O transport `http`](#the-http-transport)
  - [O transport `fastcgi`](#the-fastcgi-transport)
- [Interceptando respostas](#intercepting-responses)
- [Exemplos](#examples)



<a id="syntax"></a>
## Sintaxe

```caddy-d
reverse_proxy [<matcher>] [<upstreams...>] {
	# backends
	to      <upstreams...>
	dynamic <module> ...

	# balanceamento de carga
	lb_policy       <name> [<options...>]
	lb_retries      <retries>
	lb_try_duration <duration>
	lb_try_interval <interval>
	lb_retry_match  <request-matcher>

	# active health checking
	health_uri          <uri>
	health_upstream     <ip:port>
	health_port         <port>
	health_interval     <interval>
	health_passes       <num>
	health_fails	    <num>
	health_timeout      <duration>
	health_method       <method>
	health_status       <status>
	health_request_body <body>
	health_body         <regexp>
	health_follow_redirects
	health_headers {
		<field> [<values...>]
	}

	# passive health checking
	fail_duration     <duration>
	max_fails         <num>
	unhealthy_status  <status>
	unhealthy_latency <duration>
	unhealthy_request_count <num>

	# streaming
	flush_interval     <duration>
	request_buffers    <size>
	response_buffers   <size>
	stream_timeout     <duration>
	stream_close_delay <duration>

	# manipulação de requisição/cabeçalhos
	trusted_proxies [private_ranges] <ranges...>
	header_up   [+|-]<field> [<value|regexp> [<replacement>]]
	header_down [+|-]<field> [<value|regexp> [<replacement>]]
	method <method>
	rewrite <to>

	# round trip
	transport <name> {
		...
	}

	# opcionalmente intercepta respostas do upstream
	@name {
		status <code...>
		header <field> [<value>]
	}
	replace_status [<matcher>] <status_code>
	handle_response [<matcher>] {
		<directives...>

		# diretivas especiais disponíveis apenas em handle_response
		copy_response [<matcher>] [<status>] {
			status <status>
		}
		copy_response_headers [<matcher>] {
			include <fields...>
			exclude <fields...>
		}
	}
}
```


<a id="upstreams"></a>
## Upstreams

- **&lt;upstreams...&gt;** é uma lista de upstreams (backends) para os quais fazer proxy.
- **to** <span id="to"/> é uma forma alternativa de especificar a lista de upstreams, um (ou mais) por linha.
- **dynamic** <span id="dynamic"/> configura um módulo de _upstreams dinâmicos_. Isso permite obter a lista de upstreams dinamicamente para cada requisição. Veja [upstreams dinâmicos](#dynamic-upstreams) abaixo para uma descrição dos módulos padrão. Upstreams dinâmicos são obtidos em cada iteração do loop do proxy (isto é, potencialmente várias vezes por requisição se retries de balanceamento de carga estiverem habilitados) e terão precedência sobre upstreams estáticos. Se ocorrer um erro, o proxy cairá para usar qualquer upstream configurado estaticamente.


<a id="upstream-addresses"></a>
### Endereços de upstream

Endereços estáticos de upstream podem ter a forma de uma URL que contenha apenas esquema e host/port, ou um [endereço de rede Caddy](/docs/conventions#network-addresses) convencional. Exemplos válidos:

- `localhost:4000`
- `127.0.0.1:4000`
- `[::1]:4000`
- `http://localhost:4000`
- `https://example.com`
- `h2c://127.0.0.1`
- `example.com`
- `unix//var/php.sock`
- `unix+h2c//var/grpc.sock`
- `localhost:8001-8006`
- `[fe80::ea9f:80ff:fe46:cbfd%eth0]:443`

Por padrão, as conexões são feitas ao upstream via HTTP em texto claro. Ao usar a forma URL, um esquema pode ser usado para definir alguns padrões do [`transport`](#transports) como atalho.
- Usar `https://` como esquema usará o [transport `http`](#the-http-transport) com [`tls`](#tls) habilitado.

  Além disso, talvez seja necessário sobrescrever o cabeçalho `Host` para que ele corresponda ao valor TLS SNI, usado pelos servidores para roteamento e seleção de certificados. Veja a seção [HTTPS](#https) abaixo para mais detalhes.

- Usar `h2c://` como esquema usará o [transport `http`](#the-http-transport) com [versões HTTP](#versions) definidas para permitir conexões HTTP/2 em texto claro.

- Usar `http://` como esquema é idêntico a omitir o esquema, já que HTTP já é o padrão. Essa sintaxe existe por simetria com os outros atalhos de esquema.

Esquemas não podem ser misturados, já que eles modificam a configuração comum de transporte (um transporte com TLS não pode carregar ao mesmo tempo HTTPS e HTTP em texto claro). Qualquer configuração explícita de transporte não será sobrescrita, e omitir esquemas ou usar outras portas não assume um transporte específico.

Ao usar IPv6 com zone (por exemplo, endereços link-local com uma interface de rede específica), um esquema **não** pode ser usado como atalho porque o `%` causará erro de parse de URL; configure o transporte explicitamente em vez disso.

Ao usar a forma [endereço de rede](/docs/conventions#network-addresses), o tipo de rede é especificado como um prefixo do endereço upstream. Isso não pode ser combinado com um esquema URL. Como caso especial, `unix+h2c/` é suportado como atalho para a rede `unix/` com os mesmos efeitos do esquema `h2c://`. Intervalos de porta são suportados como atalho, expandindo para múltiplos upstreams com o mesmo host.

Endereços de upstream **não podem** conter caminhos ou query strings, já que isso implicaria reescrever a requisição enquanto ela é feita proxy, comportamento que não é definido nem suportado. Você pode usar a [`diretiva rewrite`](/docs/caddyfile/directives/rewrite) se precisar disso.

Se o endereço não for uma URL (isto é, não tiver esquema), então [placeholders](/docs/caddyfile/concepts#placeholders) podem ser usados, mas isso torna o upstream _dinamicamente estático_, significando que potencialmente muitos backends diferentes agem como um único upstream estático em termos de health checks e balanceamento de carga. Recomendamos usar um módulo de [upstreams dinâmicos](#dynamic-upstreams), se possível. Ao usar placeholders, uma porta **deve** ser incluída (pela substituição do placeholder ou como sufixo estático do endereço).


<a id="dynamic-upstreams"></a>
### Upstreams dinâmicos

O reverse proxy do Caddy inclui alguns módulos padrão de upstream dinâmico. Observe que usar upstreams dinâmicos tem implicações para balanceamento de carga e health checks, dependendo da configuração da política: health checks ativos não rodam para upstreams dinâmicos; e balanceamento de carga e health checks passivos funcionam melhor se a lista de upstreams for relativamente estável e consistente (especialmente com round-robin). Idealmente, módulos de upstream dinâmico retornam apenas backends saudáveis e utilizáveis.


<a id="srv"></a>
#### SRV

Obtém upstreams de registros DNS SRV.

```caddy-d
	dynamic srv [<full_name>] {
		service   <service>
		proto     <proto>
		name      <name>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
	}
```

- **&lt;full_name&gt;** é o nome de domínio completo do registro a consultar (isto é, `_service._proto.name`).
- **service** é o componente de serviço do nome completo.
- **proto** é o componente de protocolo do nome completo. Pode ser `tcp` ou `udp`.
- **name** é o componente de nome. Ou, se `service` e `proto` estiverem vazios, o nome de domínio completo a consultar.
- **refresh** é com que frequência atualizar os resultados em cache. Padrão: `1m`
- **resolvers** é a lista de resolvedores DNS para sobrescrever os resolvedores do sistema.
- **dial_timeout** é o timeout para discagem da consulta.
- **dial_fallback_delay** é quanto tempo esperar antes de iniciar uma conexão RFC 6555 Fast Fallback. Padrão: `300ms`


<a id="aaaaa"></a>
#### A/AAAA

Obtém upstreams de registros DNS A/AAAA.

```caddy-d
	dynamic a [<name> <port>] {
		name      <name>
		port      <port>
		refresh   <interval>
		resolvers <ip...>
		dial_timeout        <duration>
		dial_fallback_delay <duration>
		versions ipv4|ipv6
	}
```

- **name** é o nome de domínio a consultar.
- **port** é a porta a usar para o backend.
- **refresh** é com que frequência atualizar os resultados em cache. Padrão: `1m`
- **resolvers** é a lista de resolvedores DNS para sobrescrever os resolvedores do sistema.
- **dial_timeout** é o timeout para discagem da consulta.
- **dial_fallback_delay** é quanto tempo esperar antes de iniciar uma conexão RFC 6555 Fast Fallback. Padrão: `300ms`
- **versions** é a lista de versões de IP a resolver. Padrão: `ipv4 ipv6`, correspondendo a ambos os registros A e AAAA respectivamente.


<a id="multi"></a>
#### Multi

Anexa os resultados de vários módulos de upstream dinâmico. Útil se você quiser fontes redundantes de upstreams, por exemplo: um cluster primário de SRVs com backup em um cluster secundário de SRVs.

```caddy-d
	dynamic multi {
		<source> [...]
	}
```

- **&lt;source&gt;** é o nome do módulo para os upstreams dinâmicos, seguido da sua configuração. Mais de um pode ser especificado.




<a id="load-balancing"></a>
## Balanceamento de carga

Balanceamento de carga é normalmente usado para dividir tráfego entre vários upstreams. Ao habilitar retries, ele também pode ser usado com um ou mais upstreams para segurar requisições até que um upstream saudável possa ser selecionado (por exemplo, para esperar e mitigar erros enquanto um upstream reinicia ou é implantado novamente).

Isso já vem habilitado por padrão, com a política `random`. Retries estão desativados por padrão.

- **lb_policy** <span id="lb_policy"/> é o nome da política de balanceamento de carga, junto com quaisquer opções. Padrão: `random`.

  Para políticas que envolvem hash, o algoritmo [highest-random-weight (HRW)](https://en.wikipedia.org/wiki/Rendezvous_hashing) é usado para garantir que um cliente ou requisição com a mesma chave de hash seja mapeado para o mesmo upstream, mesmo que a lista de upstreams mude.

  Algumas políticas suportam fallback como opção, se indicado; nesse caso, elas aceitam um [bloco](/docs/caddyfile/concepts#blocks) com `fallback <policy>` que recebe outra política de balanceamento de carga. Para essas políticas, o fallback padrão é `random`. Configurar um fallback permite usar uma política secundária se a primária não selecionar nenhuma, permitindo combinações poderosas. Fallbacks podem ser aninhados várias vezes, se desejado.
  
  Por exemplo, `header` pode ser usado como primário para permitir que desenvolvedores escolham um upstream específico, com fallback de `first` para todas as outras conexões, implementando failover primário/secundário.
  ```caddy-d
  lb_policy header X-Upstream {
  	fallback first
  }
  ```

	- `random` escolhe um upstream aleatoriamente

	- `random_choose <n>` seleciona aleatoriamente dois ou mais upstreams, depois escolhe um com menor carga (`n` normalmente é 2)

	- `first` escolhe o primeiro upstream disponível, na ordem em que são definidos na configuração, permitindo failover primário/secundário; lembre-se de habilitar health checks junto com isso, caso contrário o failover não ocorrerá

	- `round_robin` percorre cada upstream em turnos

	- `weighted_round_robin <weights...>` percorre cada upstream em turnos, respeitando os pesos fornecidos. A quantidade de argumentos de peso deve corresponder à quantidade de upstreams configurados. Os pesos devem ser inteiros não negativos. Por exemplo, com dois upstreams e pesos `5 1`, o primeiro upstream será selecionado 5 vezes seguidas antes de o segundo ser selecionado uma vez, então o ciclo se repete. Se zero for usado como peso, isso desabilitará a seleção desse upstream para novas requisições.

	- `least_conn` escolhe o upstream com menor número de requisições atuais; se mais de um host tiver o menor número, um deles é escolhido aleatoriamente

	- `ip_hash` mapeia o IP remoto (o peer imediato) para um upstream sticky

	- `client_ip_hash` mapeia o IP do cliente para um upstream sticky; isso funciona melhor em conjunto com a [opção global `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies), que habilita a análise do IP real do cliente; caso contrário, ele se comporta como `ip_hash`

	- `uri_hash` mapeia a URI da requisição (path e query) para um upstream sticky

	- `query [key]` mapeia uma query da requisição para um upstream sticky, fazendo hash do valor da query; se a chave especificada não estiver presente, a política fallback será usada para selecionar um upstream (`random` por padrão)

	- `header [field]` mapeia um cabeçalho da requisição para um upstream sticky, fazendo hash do valor do cabeçalho; se o campo de cabeçalho especificado não estiver presente, a política fallback será usada para selecionar um upstream (`random` por padrão)

	- `cookie [<name> [<secret>]]` na primeira requisição de um cliente (quando não há cookie), a política fallback será usada para selecionar um upstream (`random` por padrão), e um cabeçalho `Set-Cookie` é adicionado à resposta (o nome padrão do cookie é `lb` se não for especificado). O valor do cookie é o endereço de discagem do upstream escolhido, hashado com HMAC-SHA256 (usando `<secret>` como segredo compartilhado, string vazia se não for especificada).
	
	  Em requisições subsequentes em que o cookie estiver presente, o valor do cookie será mapeado para o mesmo upstream se ele estiver disponível; se não estiver disponível ou não for encontrado, um novo upstream é selecionado com a política fallback, e o cookie é adicionado à resposta.

	  Se você quiser usar um upstream específico para depuração, pode fazer hash do endereço do upstream com o segredo e definir o cookie no seu cliente HTTP (navegador ou outro). Por exemplo, com PHP, você pode executar o seguinte para calcular o valor do cookie, em que `10.1.0.10:8080` é o endereço de um dos seus upstreams, e `secret` é o segredo configurado.
	  ```php
	  echo hash_hmac('sha256', '10.1.0.10:8080', 'secret');
	  // cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf
	  ```
	
	  Você pode definir o cookie no console Javascript do navegador, por exemplo para definir o cookie chamado `lb`:
	  ```js
	  document.cookie = "lb=cdd96966817dd14a99f47ee17451464f29998da170814a16b483e4c1ff4c48cf";
	  ```

- **lb_retries** <span id="lb_retries"/> é quantas vezes tentar selecionar backends disponíveis para cada requisição se o próximo host disponível estiver fora do ar. Por padrão, retries estão desativados (zero).

  Se [`lb_try_duration`](#lb_try_duration) também estiver configurado, os retries podem parar mais cedo se a duração for atingida. Em outras palavras, a duração de retry tem precedência sobre a contagem de retries.

- **lb_try_duration** <span id="lb_try_duration"/> é um [valor de duração](/docs/conventions#durations) que define por quanto tempo tentar selecionar backends disponíveis para cada requisição se o próximo host disponível estiver fora do ar. Por padrão, retries estão desativados (duração zero).

  Os clientes esperarão até esse tempo enquanto o balanceador tenta encontrar um upstream disponível. Um ponto de partida razoável pode ser `5s`, já que o timeout padrão de discagem do transport HTTP é `3s`; isso deve permitir pelo menos uma nova tentativa se o upstream selecionado inicialmente não puder ser alcançado. Mas sinta-se à vontade para experimentar e encontrar o equilíbrio certo para o seu caso de uso.

- **lb_try_interval** <span id="lb_try_interval"/> é um [valor de duração](/docs/conventions#durations) que define quanto tempo esperar entre selecionar o próximo host do pool. O padrão é `250ms`. Só é relevante quando uma requisição para um upstream falha. Tenha cuidado: definir isso como `0` com um `lb_try_duration` não zero pode fazer a CPU girar se todos os backends estiverem fora do ar e a latência for muito baixa.

- **lb_retry_match** <span id="lb_retry_match"/> restringe com quais requisições os retries são permitidos. Uma requisição precisa corresponder a essa condição para ser repetida se a conexão com o upstream tiver sido bem-sucedida, mas o round-trip subsequente tiver falhado. Se a conexão com o upstream falhar, um retry sempre é permitido. Por padrão, apenas requisições `GET` são repetidas.

  A sintaxe para essa opção é a mesma dos [matchers nomeados de requisição](/docs/caddyfile/matchers#named-matchers), mas sem o `@name`. Se você só precisar de um matcher, pode configurá-lo na mesma linha. Para vários matchers, um bloco é necessário.


<a id="active-health-checks"></a>
### Active health checks

Os health checks ativos verificam a saúde em segundo plano com base em um timer. Para habilitar isso, `health_uri` ou `health_port` são obrigatórios.

- **health_uri** <span id="health_uri"/> é o caminho da URI (e query opcional) para health checks ativos.

- **health_upstream** <span id="health_upstream"/> é o ip:port a usar para health checks ativos, se for diferente do upstream. Isso deve ser usado em conjunto com `health_header` e `{http.reverse_proxy.active.target_upstream}`.

- **health_port** <span id="health_port"/> é a porta a usar para health checks ativos, se for diferente da porta do upstream. Ignorado se `health_upstream` for usado.

- **health_interval** <span id="health_interval"/> é um [valor de duração](/docs/conventions#durations) que define com que frequência fazer health checks ativos. Padrão: `30s`.

- **health_passes** <span id="health_passes"/> é o número de health checks consecutivos exigidos antes de marcar o backend como saudável novamente. Padrão: `1`.

- **health_fails** <span id="health_fails"/> é o número de health checks consecutivos exigidos antes de marcar o backend como não saudável. Padrão: `1`.

- **health_timeout** <span id="health_timeout"/> é um [valor de duração](/docs/conventions#durations) que define quanto tempo esperar por uma resposta antes de marcar o backend como inativo. Padrão: `5s`.

- **health_method** <span id="health_method"/> é o método HTTP a usar para o health check ativo. Padrão: `GET`.

- **health_status** <span id="health_status"/> é o código de status HTTP esperado de um backend saudável. Pode ser um código de 3 dígitos ou uma classe de status terminada em `xx`. Por exemplo: `200` (que é o padrão) ou `2xx`.

- **health_request_body** <span id="health_request_body"/> é uma string representando o corpo da requisição a enviar com o health check ativo.

- **health_body** <span id="health_body"/> é uma substring ou expressão regular a corresponder no corpo da resposta de um health check ativo. Se o backend não retornar um corpo correspondente, ele será marcado como inativo.

- **health_follow_redirects** <span id="health_follow_redirects"/> fará com que o health check siga redirecionamentos fornecidos pelo upstream. Por padrão, uma resposta de redirecionamento faria o health check contar como falha.

- **health_headers** <span id="health_headers"/> permite especificar cabeçalhos a definir nas requisições de health check ativo. Isso é útil se você precisar mudar os cabeçalhos enviados ao endpoint de health check.

`health_headers { <field> [<values...>] }`


<a id="passive-health-checks"></a>
### Passive health checks

Os health checks passivos observam falhas reais do tráfego e marcam backends como não saudáveis com base nelas.

- **fail_duration** <span id="fail_duration"/> é por quanto tempo um backend permanece marcado como ruim após falhar.
- **max_fails** <span id="max_fails"/> é o número de falhas permitidas antes de marcar o backend como não saudável.
- **unhealthy_status** <span id="unhealthy_status"/> marca um backend como não saudável se ele responder com estes códigos de status.
- **unhealthy_latency** <span id="unhealthy_latency"/> marca um backend como não saudável se a latência exceder essa duração.
- **unhealthy_request_count** <span id="unhealthy_request_count"/> marca um backend como não saudável se houver muitas requisições concorrentes.


<a id="events"></a>
## Eventos

Quando um upstream passa de saudável para não saudável ou vice-versa, [um evento](/docs/caddyfile/options#event-options) é emitido. Esses eventos podem ser usados para disparar outras ações, como enviar uma notificação ou registrar uma mensagem. Os eventos são os seguintes:

- `healthy` é emitido quando um upstream é marcado como saudável depois de ter estado anteriormente não saudável
- `unhealthy` é emitido quando um upstream é marcado como não saudável depois de ter estado anteriormente saudável

Em ambos os casos, `host` é incluído como metadado no evento para identificar o upstream que mudou de estado. Ele pode ser usado como placeholder com `{event.data.host}` no handler de evento `exec`, por exemplo.


<a id="streaming"></a>
## Streaming

Por padrão, o proxy faz buffering parcial da resposta para eficiência na rede.

O proxy também suporta conexões WebSocket, realizando a requisição de upgrade HTTP e depois transformando a conexão em um túnel bidirecional.

<aside class="tip">

Por padrão, conexões WebSocket são encerradas à força (com uma mensagem Close enviada tanto ao cliente quanto ao upstream) quando a configuração é recarregada. Cada requisição mantém uma referência à configuração, então fechar conexões antigas é necessário para controlar o uso de memória. Esse comportamento de fechamento pode ser personalizado com as opções [`stream_timeout`](#stream_timeout) e [`stream_close_delay`](#stream_close_delay).

</aside>

- **flush_interval** <span id="flush_interval"/> ajusta com que frequência o Caddy deve liberar o buffer de resposta para o cliente. Por padrão, nenhuma liberação periódica é feita. Um valor negativo (geralmente `-1`) sugere um modo de baixa latência que desabilita completamente o buffering da resposta e libera imediatamente após cada escrita para o cliente, sem cancelar a requisição ao backend mesmo que o cliente desconecte cedo. Esta opção é ignorada e as respostas são liberadas imediatamente para o cliente se uma das condições abaixo for verdadeira:
    - `Content-Type: text/event-stream`
    - `Content-Length` é desconhecido
    - HTTP/2 em ambos os lados do proxy, `Content-Length` é desconhecido, e `Accept-Encoding` ou não está definido ou é `identity`

- **request_buffers** <span id="request_buffers"/> faz com que o proxy leia até `<size>` bytes do corpo da requisição para um buffer antes de enviá-lo ao upstream. Isso é muito ineficiente e só deve ser feito se o upstream precisar ler corpos de requisição sem atraso (o que é algo que a aplicação upstream deveria corrigir). Aceita todos os formatos de tamanho suportados por [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **response_buffers** <span id="response_buffers"/> faz com que o proxy leia até `<size>` bytes do corpo da resposta para um buffer antes de devolvê-la ao cliente. Isso deve ser evitado sempre que possível por motivos de desempenho, mas pode ser útil se o backend tiver restrições de memória mais rígidas. Aceita todos os formatos de tamanho suportados por [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go).

- **stream_timeout** <span id="stream_timeout"/> é um [valor de duração](/docs/conventions#durations) após o qual requisições em streaming, como WebSockets, serão encerradas à força no fim do tempo limite. Isso basicamente cancela conexões se elas ficarem abertas tempo demais. Um ponto de partida razoável pode ser `24h` para eliminar conexões mais antigas que um dia. Padrão: sem timeout.

- **stream_close_delay** <span id="stream_close_delay"/> é um [valor de duração](/docs/conventions#durations) que atrasa o fechamento forçado de requisições em streaming, como WebSockets, quando a configuração é descarregada; em vez disso, o stream permanecerá aberto até que o atraso termine. Em outras palavras, habilitar isso impede que os streams sejam fechados imediatamente quando a configuração do Caddy é recarregada. Isso pode ser uma boa ideia para evitar uma tempestade de clientes reconectando após o fechamento da configuração anterior. Um ponto de partida razoável pode ser algo como `5m` para dar aos usuários 5 minutos para sair naturalmente da página após um recarregamento de configuração. Padrão: sem atraso.


<a id="headers"></a>
## Cabeçalhos

O proxy pode **manipular cabeçalhos** entre si e o backend:

- **header_up** <span id="header_up"/> define, adiciona (com o prefixo `+`), apaga (com o prefixo `-`) ou substitui (usando dois argumentos, uma busca e uma substituição) um cabeçalho da requisição enviada ao backend.

- **header_down** <span id="header_down"/> define, adiciona (com o prefixo `+`), apaga (com o prefixo `-`) ou substitui (usando dois argumentos, uma busca e uma substituição) um cabeçalho da resposta recebida do backend.

Por exemplo, para definir um cabeçalho de requisição, sobrescrevendo quaisquer valores existentes:

```caddy-d
header_up Some-Header "the value"
```

Para adicionar um cabeçalho de resposta; observe que pode haver vários valores para um campo de cabeçalho:

```caddy-d
header_down +Some-Header "first value"
header_down +Some-Header "second value"
```

Para apagar um cabeçalho de requisição, impedindo que ele chegue ao backend:

```caddy-d
header_up -Some-Header
```

Para apagar todos os cabeçalhos de requisição correspondentes, usando uma correspondência por sufixo:

```caddy-d
header_up -Some-*
```

Para apagar _todos_ os cabeçalhos de requisição, e então adicionar individualmente os que você quiser (não recomendado):

```caddy-d
header_up -*
```

Para fazer uma substituição por expressão regular em um cabeçalho de requisição:

```caddy-d
header_up Some-Header "^prefix-([A-Za-z0-9]*)$" "replaced-$1-suffix"
```

A linguagem de expressão regular usada é RE2, incluída no Go. Veja a [referência de sintaxe RE2](https://github.com/google/re2/wiki/Syntax) e a [visão geral da sintaxe de regexp do Go](https://pkg.go.dev/regexp/syntax). A string de substituição é [expandida](https://pkg.go.dev/regexp#Regexp.Expand), permitindo usar valores capturados, por exemplo `$1` sendo o primeiro grupo de captura.


<a id="defaults"></a>
### Defaults

Por padrão, o Caddy repassa os cabeçalhos de entrada, incluindo `Host`, para o backend sem modificações, com três exceções:

- Ele define ou acrescenta o campo [`X-Forwarded-For`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For).
- Ele define o campo [`X-Forwarded-Proto`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto).
- Ele define o campo [`X-Forwarded-Host`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host).

<span id="trusted_proxies"/> Para esses cabeçalhos `X-Forwarded-*`, por padrão o proxy ignora os valores vindos de requisições de entrada para evitar spoofing.

Se o Caddy não for o primeiro servidor a receber conexões dos seus clientes, você pode configurar `trusted_proxies` com uma lista de intervalos IP (CIDRs) cujas requisições de entrada serão confiáveis para fornecer bons valores para esses cabeçalhos.

É fortemente recomendado configurar isso por meio da [opção global `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) em vez de no proxy, para que isso se aplique a todos os handlers de proxy no seu servidor e também tenha o benefício de habilitar o parsing do IP do cliente.

<aside class="tip">

Se você estiver usando Cloudflare na frente do Caddy, saiba que pode estar vulnerável a spoofing do cabeçalho `X-Forwarded-For`. Nossos amigos da [Authelia](https://www.authelia.com) documentaram uma [solução alternativa](https://www.authelia.com/integration/proxies/forwarded-headers/) para configurar o Cloudflare para ignorar valores de entrada desse cabeçalho.

</aside>

Além disso, ao usar o [transport `http`](#the-http-transport), o cabeçalho `Accept-Encoding: gzip` será definido, se estiver ausente na requisição do cliente. Isso permite que o upstream sirva conteúdo compactado, se puder. Esse comportamento pode ser desativado com [`compression off`](#compression) no transport.


<a id="https"></a>
### HTTPS

Como (a maioria) dos cabeçalhos mantém seus valores originais quando são enviados por proxy, muitas vezes é necessário sobrescrever o cabeçalho `Host` com o endereço do upstream configurado ao fazer proxy para HTTPS, de modo que o cabeçalho `Host` corresponda ao valor TLS ServerName:

```caddy-d
reverse_proxy https://example.com {
	header_up Host {upstream_hostport}
}
```

Desde o Caddy v2.11.0, isso é feito automaticamente, então não é mais necessário sobrescrever explicitamente o cabeçalho `Host` ao fazer proxy para HTTPS. Se você quiser desativar esse comportamento, pode definir o cabeçalho `Host` como seu valor original:

```caddy-d
reverse_proxy https://example.com {
	header_up Host {hostport}
}
```

O cabeçalho `X-Forwarded-Host` continua sendo passado [por padrão](#defaults), então o upstream ainda pode usá-lo se precisar saber o valor original do cabeçalho `Host`.

O mesmo se aplica ao encerrar TLS no Caddy e fazer proxy via HTTP, seja para uma porta ou um unix socket. O próprio Caddy precisa receber o Host correto quando é o alvo de `reverse_proxy`. No caso de unix socket, o `upstream_hostport` será o caminho do socket, e o Host deve ser definido explicitamente.


<a id="rewrites"></a>
## Rewrites

Por padrão, o Caddy faz a requisição ao upstream com o mesmo método HTTP e URI da requisição de entrada, a menos que um rewrite tenha sido realizado na cadeia de middleware antes de chegar ao `reverse_proxy`.

Antes de fazer proxy, a requisição é clonada; isso garante que quaisquer modificações feitas na requisição durante o handler não vazem para outros handlers. Isso é útil em situações em que o processamento precisa continuar depois do proxy.

Além das [manipulações de cabeçalho](#headers), o método e a URI da requisição podem ser alterados antes de ela ser enviada ao upstream:

- **method** <span id="method"/> altera o método HTTP da requisição clonada. Se o método for alterado para `GET` ou `HEAD`, o corpo da requisição de entrada _não_ será enviado upstream por este handler.
- **rewrite** <span id="rewrite"/> altera a URI (path e query) da requisição clonada. Isso é semelhante à [`diretiva rewrite`](/docs/caddyfile/directives/rewrite), exceto que não persiste além do escopo deste handler.

Esses rewrites são frequentemente úteis para um padrão como "pre-check requests". Por exemplo, a requisição pode ser enviada a um gateway de autenticação para decidir se deve continuar ou ser redirecionada para login. Para esse padrão, o Caddy fornece a diretiva [`forward_auth`](/docs/caddyfile/directives/forward_auth).



<a id="transports"></a>
## Transports

O **transport** de proxy do Caddy é plugável:

- **transport** <span id="transport"/> define como se comunicar com o backend. O padrão é `http`.


<a id="the-http-transport"></a>
### O `http` transport

```caddy-d
transport http {
	read_buffer             <size>
	write_buffer            <size>
	max_response_header     <size>
	proxy_protocol          v1|v2
	dial_timeout            <duration>
	dial_fallback_delay     <duration>
	response_header_timeout <duration>
	expect_continue_timeout <duration>
	resolvers <ip...>
	tls
	tls_client_auth <automate_name> | <cert_file> <key_file>
	tls_insecure_skip_verify
	tls_curves <curves...>
	tls_timeout <duration>
	tls_trust_pool <module>
	tls_server_name <server_name>
	tls_renegotiation <level>
	tls_except_ports <ports...>
	keepalive [off|<duration>]
	keepalive_interval <interval>
	keepalive_idle_conns <max_count>
	keepalive_idle_conns_per_host <count>
	versions <versions...>
	compression off
	max_conns_per_host <count>
	network_proxy <module>
}
```

- **read_buffer** <span id="read_buffer"/> é o tamanho do buffer de leitura em bytes. Padrão: `4KiB`.
- **write_buffer** <span id="write_buffer"/> é o tamanho do buffer de escrita em bytes. Padrão: `4KiB`.
- **max_response_header** <span id="max_response_header"/> é a quantidade máxima de bytes a ler dos cabeçalhos de resposta. Padrão: `10MiB`.
- **proxy_protocol** <span id="proxy_protocol"/> habilita [PROXY protocol](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) na conexão com o upstream, prefixando os dados reais do IP do cliente. Isso é melhor combinado com a [opção global `servers > trusted_proxies`](/docs/caddyfile/options#trusted-proxies) se o Caddy estiver atrás de outro proxy. Versões `v1` e `v2` são suportadas. Por padrão, isso está desativado.
- **dial_timeout** <span id="dial_timeout"/> é a duração máxima para esperar ao conectar ao socket upstream. Padrão: `3s`.
- **dial_fallback_delay** <span id="dial_fallback_delay"/> é a duração máxima para esperar antes de iniciar uma conexão RFC 6555 Fast Fallback. Um valor negativo desativa isso. Padrão: `300ms`.
- **response_header_timeout** <span id="response_header_timeout"/> é a duração máxima para esperar a leitura dos cabeçalhos de resposta do upstream. Padrão: sem timeout.
- **expect_continue_timeout** <span id="expect_continue_timeout"/> é a duração máxima para esperar os primeiros cabeçalhos de resposta do upstream depois de escrever completamente os cabeçalhos da requisição, se a requisição tiver `Expect: 100-continue`. Padrão: sem timeout.
- **read_timeout** <span id="read_timeout"/> é a duração máxima para esperar pela próxima leitura do backend. Padrão: sem timeout.
- **write_timeout** <span id="write_timeout"/> é a duração máxima para esperar pelas próximas escritas no backend. Padrão: sem timeout.
- **resolvers** <span id="resolvers"/> é uma lista de resolvedores DNS para substituir os resolvedores do sistema.
- **tls** <span id="tls"/> usa HTTPS com o backend.
- **tls_client_auth** <span id="tls_client_auth"/> habilita autenticação TLS de cliente de duas formas: (1) especificando um nome de domínio para o qual o Caddy deve obter um certificado e mantê-lo renovado, ou (2) especificando um arquivo de certificado e uma chave para apresentar ao backend.
- **tls_insecure_skip_verify** <span id="tls_insecure_skip_verify"/> desativa a verificação do handshake TLS. _Não use em produção._
- **tls_curves** <span id="tls_curves"/> é uma lista de curvas elípticas suportadas para a conexão upstream.
- **tls_timeout** <span id="tls_timeout"/> é a duração máxima para o handshake TLS completar. Padrão: sem timeout.
- **tls_trust_pool** <span id="tls_trust_pool"/> configura a fonte de CAs confiáveis.
- **tls_server_name** <span id="tls_server_name"/> define o nome do servidor usado ao verificar o certificado recebido no handshake TLS.
- **tls_renegotiation** <span id="tls_renegotiation"/> define o nível de renegociação TLS. A renegociação TLS é o ato de realizar handshakes subsequentes após o primeiro. O nível pode ser um destes:
  - `never` (o padrão) desativa a renegociação.
  - `once` permite que um servidor remoto solicite renegociação uma vez por conexão.
  - `freely` permite que um servidor remoto solicite renegociação repetidamente.
- **tls_except_ports** <span id="tls_except_ports"/> quando TLS está habilitado, se o target upstream usar uma das portas dadas, TLS será desativado para essas conexões.
- **keepalive** <span id="keepalive"/> é `off` ou uma duração que especifica por quanto tempo manter conexões abertas. Padrão: `2m`.
- **keepalive_interval** <span id="keepalive_interval"/> é o intervalo entre probes de vivacidade. Padrão: `30s`.
- **keepalive_idle_conns** <span id="keepalive_idle_conns"/> define o número máximo de conexões a manter vivas. Padrão: sem limite.
- **keepalive_idle_conns_per_host** <span id="keepalive_idle_conns_per_host"/> controla o máximo de conexões ociosas por host. Padrão: `32`.
- **versions** <span id="versions"/> permite personalizar quais versões HTTP suportar. Valores válidos: `1.1`, `2`, `h2c`, `3`.
- **compression** <span id="compression"/> pode ser usado para desativar compressão para o backend definindo `off`.
- **max_conns_per_host** <span id="max_conns_per_host"/> limita opcionalmente o número total de conexões por host. Padrão: sem limite.
- **network_proxy** <span id="network_proxy"/> especifica o nome de um módulo de proxy de rede a usar para requisições ao servidor upstream. Se não for explicitamente configurado, o Caddy respeita o proxy configurado via variáveis de ambiente conforme a [stdlib do Go](https://pkg.go.dev/golang.org/x/net/http/httpproxy#FromEnvironment), ou seja, `HTTP_PROXY`, `HTTPS_PROXY` e `NO_PROXY`. Quando um valor é fornecido para este parâmetro, as requisições fluirão pelo reverse proxy na seguinte ordem: Cliente (usuários) → `reverse_proxy` → `network_proxy` → upstream. Os módulos embutidos são:
  - `none`, que é usado para ignorar as configurações de ambiente `HTTP_PROXY`, `HTTPS_PROXY` e `NO_PROXY`.
  - `url <url>`, que é usado para especificar uma única URL sobrescrevendo a configuração do ambiente.

<a id="the-fastcgi-transport"></a>
### O `fastcgi` transport

```caddy-d
transport fastcgi {
	root  <path>
	split <at>
	env   <key> <value>
	resolve_root_symlink
	dial_timeout  <duration>
	read_timeout  <duration>
	write_timeout <duration>
	capture_stderr
}
```

- **root** <span id="root"/> é a raiz do site. Padrão: `{http.vars.root}` ou o diretório de trabalho atual.
- **split** <span id="split"/> define onde dividir o caminho para obter PATH_INFO.
- **env** <span id="env"/> define uma variável de ambiente extra com o valor fornecido.
- **resolve_root_symlink** <span id="resolve_root_symlink"/> resolve o diretório `root` para seu valor real.
- **dial_timeout** <span id="dial_timeout"/> é quanto tempo esperar ao conectar ao socket upstream. Padrão: `3s`.
- **read_timeout** <span id="read_timeout"/> é quanto tempo esperar ao ler do servidor FastCGI. Padrão: sem timeout.
- **write_timeout** <span id="write_timeout"/> é quanto tempo esperar ao enviar para o servidor FastCGI. Padrão: sem timeout.
- **capture_stderr** <span id="capture_stderr"/> habilita capturar e registrar quaisquer mensagens enviadas pelo servidor fastcgi upstream em `stderr`.

<aside class="tip">

Se você estiver tentando servir uma aplicação PHP moderna, talvez esteja procurando a [`diretiva php_fastcgi`](/docs/caddyfile/directives/php_fastcgi), que é um atalho para um proxy usando a diretiva `fastcgi`, com os rewrites necessários para usar `index.php` como ponto de entrada de roteamento.

</aside>


<a id="intercepting-responses"></a>
## Interceptando respostas

O reverse proxy pode ser configurado para interceptar respostas do backend. Para facilitar isso, [matchers de resposta](/docs/caddyfile/response-matchers) podem ser definidos (semelhante à sintaxe dos matchers de requisição) e a primeira rota `handle_response` correspondente será invocada.

Quando um handler de resposta é invocado, a resposta do backend não é escrita para o cliente, e a rota `handle_response` configurada será executada em seu lugar; cabe a essa rota escrever uma resposta. Se a rota _não_ escrever uma resposta, o processamento continuará com qualquer handler [ordenado depois](/docs/caddyfile/directives#directive-order) deste `reverse_proxy`.

- **@name** é o nome de um [matcher de resposta](/docs/caddyfile/response-matchers).
- **replace_status** <span id="replace_status"/> simplesmente altera o código de status da resposta quando ela corresponde ao matcher fornecido.
- **handle_response** <span id="handle_response"/> define a rota a executar quando a resposta corresponde ao matcher fornecido. Se um matcher for omitido, todas as respostas são interceptadas. Quando vários blocos `handle_response` são definidos, o primeiro bloco correspondente será aplicado.

Além disso, dentro de `handle_response`, podem ser usadas duas diretivas especiais de handler:

- **copy_response** <span id="copy_response"/> copia o corpo da resposta recebida do backend de volta para o cliente. Opcionalmente permite mudar o código de status da resposta durante isso.
- **copy_response_headers** <span id="copy_response_headers"/> copia os cabeçalhos de resposta do backend para o cliente, opcionalmente incluindo ou excluindo uma lista de campos.

Três placeholders ficarão disponíveis dentro das rotas `handle_response`:

- `{rp.status_code}` O código de status da resposta do backend.
- `{rp.status_text}` O texto de status da resposta do backend.
- `{rp.header.*}` Os cabeçalhos da resposta do backend.

Cada uso de `reverse_proxy` recebe o corpo da requisição original (ou como modificado por outro módulo); a resposta copiada de um `handle_response` não é passada adiante para um reverse proxy subsequente.



<a id="examples"></a>
## Exemplos

Fazer reverse proxy de todas as requisições para um backend local:

```caddy
example.com {
	reverse_proxy localhost:9005
}
```

Balancear carga de todas as requisições entre 3 backends:

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80
}
```

O mesmo, mas apenas requisições dentro de `/api`, e sticky usando a política `cookie`:

```caddy
example.com {
	reverse_proxy /api/* node1:80 node2:80 node3:80 {
		lb_policy cookie api_sticky
	}
}
```

Usando [active health checks](#active-health-checks) para determinar quais backends estão saudáveis:

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /healthz
		lb_try_duration 5s
	}
}
```

Configurar algumas opções de transport:

```caddy
example.com {
	reverse_proxy localhost:8080 {
		transport http {
			dial_timeout 2s
			response_header_timeout 30s
		}
	}
}
```

Fazer reverse proxy para um upstream HTTPS:

```caddy
example.com {
	reverse_proxy https://example.com
}
```

Fazer reverse proxy para um upstream HTTPS, mas desativando a verificação TLS. Isso NÃO É RECOMENDADO.

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_insecure_skip_verify
		}
	}
}
```

Confiar explicitamente no certificado do upstream:

```caddy
example.com {
	reverse_proxy 10.0.0.1:443 {
		transport http {
			tls_trust_pool file /path/to/cert.pem
			tls_server_name app.example.com
		}
	}
}
```

Remover um prefixo de caminho antes de fazer proxy:

```caddy
example.com {
	handle_path /prefix/* {
		reverse_proxy localhost:9000
	}
}
```

Substituir um prefixo de caminho antes de fazer proxy:

```caddy
example.com {
	handle_path /old-prefix/* {
		rewrite /new-prefix{path}
		reverse_proxy localhost:9000
	}
}
```

Suporte a `X-Accel-Redirect`, ou seja, servir arquivos estáticos conforme solicitado, interceptando a resposta:

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@accel header X-Accel-Redirect *
		handle_response @accel {
			root /path/to/private/files
			rewrite {rp.header.X-Accel-Redirect}
			method GET
			file_server
		}
	}
}
```

Página de erro personalizada para erros do upstream:

```caddy
example.com {
	reverse_proxy localhost:8080 {
		@error status 500 503
		handle_response @error {
			root /path/to/error/pages
			rewrite /{rp.status_code}.html
			file_server
		}
	}
}
```

Obter backends dinamicamente a partir de consultas DNS A/AAAA:

```caddy
example.com {
	reverse_proxy {
		dynamic a example.com 9000
	}
}
```

Obter backends dinamicamente a partir de consultas DNS SRV:

```caddy
example.com {
	reverse_proxy {
		dynamic srv _api._tcp.example.com
	}
}
```

Usar active health checks e `health_upstream` pode ser útil ao criar um serviço intermediário para fazer um health check mais completo:

```caddy
example.com {
	reverse_proxy node1:80 node2:80 node3:80 {
		health_uri /health
		health_upstream 127.0.0.1:53336
		health_headers {
			Full-Upstream {http.reverse_proxy.active.target_upstream}
		}
	}
}
```
