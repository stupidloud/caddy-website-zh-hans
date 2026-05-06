---
title: Como o Logging Funciona
---

Como o Logging Funciona
=================

O Caddy tem recursos de logging poderosos e flexíveis, mas eles podem ser diferentes do que você está acostumado, especialmente se você vem de hospedagem compartilhada mais arcaica ou de outros servidores web legados.

## Visão geral

Há dois aspectos principais do logging: emissão e consumo.

**Emissão** significa produzir mensagens. Ela consiste em três etapas:

1. Coletar informações relevantes (contexto)
2. Construir uma representação útil (codificação)
3. Enviar essa representação para uma saída (gravação)

Essa funcionalidade faz parte do núcleo do Caddy, permitindo que qualquer parte da base de código do Caddy ou dos módulos (plugins) emita logs.

**Consumo** é a entrada e o processamento das mensagens. Para serem úteis, os logs emitidos precisam ser consumidos. Logs que apenas são gravados, mas nunca lidos, não têm valor. Consumir logs pode ser tão simples quanto um administrador lendo a saída do terminal, ou tão avançado quanto conectar uma ferramenta de agregação de logs ou um serviço de nuvem para filtrar, contar e indexar mensagens.

### O papel do Caddy

_O Caddy é um emissor de logs_. Ele não consome logs, exceto pelo processamento mínimo necessário para codificar e gravar os logs. Isso é importante porque mantém o core do Caddy mais simples, levando a menos bugs e casos-limite, enquanto reduz a carga de manutenção. No fim, processamento de logs está fora do escopo do core do Caddy.

No entanto, sempre há a possibilidade de um módulo de app do Caddy consumir logs. (Só que, até onde sabemos, isso ainda não existe.)

## Logs estruturados

Como a maioria das aplicações modernas, os logs do Caddy são _estruturados_. Isso significa que a informação em uma mensagem não é simplesmente uma string opaca ou um slice de bytes. Em vez disso, os dados permanecem fortemente tipados e indexados por nomes individuais de _campo_ até o momento de codificar a mensagem e escrevê-la.

Compare logs não estruturados tradicionais&mdash;como o arcaico Common Log Format (CLF)&mdash;comumente usado em servidores HTTP tradicionais:

```
127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.1" 200 2326
```

Esse formato "tem estrutura", mas não é "estruturado": ele só pode ser usado para registrar requisições HTTP. Não há maneira (eficiente) de codificá-lo de forma diferente, porque ele é uma string opaca de bytes. Também falta muita informação. Ele nem sequer inclui o cabeçalho Host da requisição! Esse formato de log só é útil quando se hospeda um único site e para obter as informações mais básicas sobre as requisições.

<aside class="tip">
	A falta de informação de host no CLF é o motivo pelo qual esses logs normalmente precisam ser gravados em arquivos separados quando se hospeda mais de um site: não há como saber o cabeçalho Host da requisição de outra forma!
</aside>

Agora compare uma mensagem de log estruturada equivalente do Caddy, codificada como JSON e formatada de forma agradável para exibição:

```json
{
	"level": "info",
	"ts": 1646861401.5241024,
	"logger": "http.log.access",
	"msg": "handled request",
	"request": {
		"remote_ip": "127.0.0.1",
		"remote_port": "41342",
		"client_ip": "127.0.0.1",
		"proto": "HTTP/2.0",
		"method": "GET",
		"host": "localhost",
		"uri": "/",
		"headers": {
			"User-Agent": ["curl/7.82.0"],
			"Accept": ["*/*"],
			"Accept-Encoding": ["gzip, deflate, br"],
		},
		"tls": {
			"resumed": false,
			"version": 772,
			"cipher_suite": 4865,
			"proto": "h2",
			"server_name": "example.com"
		}
	},
	"bytes_read": 0,
	"user_id": "",
	"duration": 0.000929675,
	"size": 10900,
	"status": 200,
	"resp_headers": {
		"Server": ["Caddy"],
		"Content-Encoding": ["gzip"],
		"Content-Type": ["text/html; charset=utf-8"],
		"Vary": ["Accept-Encoding"]
	}
}
```

Você pode ver como o log estruturado é muito mais útil e contém muito mais informação. A abundância de informações nessa mensagem de log não é apenas útil, ela também vem praticamente sem custo de desempenho: os logs do Caddy são zero-allocation. Logs estruturados não têm restrições quanto a tipos de dados ou contexto: eles podem ser usados em qualquer caminho de código e incluir qualquer tipo de informação.

Como os logs são estruturados e fortemente tipados, eles podem ser codificados em qualquer formato. Então, se você não quiser trabalhar com JSON, os logs podem ser codificados em qualquer outra representação. O Caddy suporta outros formatos por meio de [módulos de log encoder](/docs/json/logging/logs/encoder/), e outros ainda podem ser adicionados.

**Mais importante** na distinção entre logs estruturados e formatos legados: com uma penalidade de desempenho, um log estruturado [pode ser transformado no Common Log Format legado <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/transform-encoder), mas não o contrário. É não trivial (ou pelo menos ineficiente) ir de CLF para formatos estruturados, e impossível considerando a falta de informação.

Em essência, logging estruturado eficiente geralmente promove estas filosofias:

- É melhor ter logs demais do que logs de menos
- Filtrar é melhor do que descartar
- Adiar a codificação traz mais flexibilidade e interoperabilidade

## Emissão

No código, uma emissão de log se parece com o seguinte:

```go
logger.Debug("proxy roundtrip",
	zap.String("upstream", di.Upstream.String()),
	zap.Object("request", caddyhttp.LoggableHTTPRequest{Request: req}),
	zap.Object("headers", caddyhttp.LoggableHTTPHeader(res.Header)),
	zap.Duration("duration", duration),
	zap.Int("status", res.StatusCode),
)
```

<aside class="tip">
	Essa é uma linha real de código do reverse proxy do Caddy. Essa linha é o que permite inspecionar requisições aos upstreams configurados quando o debug logging está habilitado. É uma informação inestimável ao depurar!
</aside>

Você pode ver que essa única chamada de função contém o nível do log, uma mensagem e vários campos de dados. Todos eles são fortemente tipados, e o Caddy usa uma biblioteca de logging zero-allocation para que as emissões sejam rápidas e eficientes, com quase nenhum overhead.

A variável `logger` é um `zap.Logger` que pode ter qualquer quantidade de contexto associada, incluindo tanto um nome quanto campos de dados. Isso permite que loggers "herdem" de contextos pai de forma elegante, possibilitando tracing e métricas avançados.

A partir daí, a mensagem é enviada por um pipeline de processamento altamente eficiente, onde é codificada e gravada.

## Pipeline de logging

Como você viu acima, as mensagens são emitidas por **loggers**. Em seguida, as mensagens são enviadas para **logs** para processamento.

O Caddy permite [configurar vários logs](/docs/json/logging/logs/) que podem processar mensagens. Um log consiste em um encoder, um writer, um nível mínimo, uma taxa de amostragem e uma lista de loggers a incluir ou excluir. No Caddy, sempre existe um log padrão chamado `default`. Você pode personalizá-lo especificando um log com a chave `"default"` [neste objeto](/docs/json/logging/logs/) na configuração.

<aside class="tip">

Agora seria um bom momento para [explorar a documentação de logging do Caddy](/docs/json/logging/) e se familiarizar com a estrutura e os parâmetros dos quais estamos falando.

</aside>


- **Encoder:** O formato do log. Transforma a representação em memória em um slice de bytes. Encoders têm acesso a todos os campos de uma mensagem de log.
- **Writer:** A saída do log. Pode ser qualquer módulo writer de log, como um arquivo ou socket de rede. Ele simplesmente grava bytes.
- **Level:** Logs têm vários níveis, de DEBUG a FATAL. Mensagens abaixo do nível especificado serão ignoradas pelo log.
- **Sampling:** Caminhos extremamente quentes podem emitir mais logs do que podem ser processados com eficiência; habilitar sampling é uma forma de reduzir a carga e ainda assim obter uma amostra representativa das mensagens.
- **Include/exclude:** Cada mensagem é emitida por um logger, que tem um nome (geralmente derivado do ID do módulo). Logs podem incluir ou excluir mensagens de determinados loggers.

Quando uma mensagem de log é emitida pelo Caddy:

- O nome do logger de origem é verificado em relação à lista de include/exclude de cada log; se estiver incluído (ou não excluído), ele é admitido naquele log.
- Se o sampling estiver habilitado, um cálculo rápido determina se a mensagem de log será mantida.
- A mensagem é codificada usando o encoder configurado no log.
- Os bytes codificados são então gravados no writer configurado do log.

Por padrão, todas as mensagens vão para todos os logs configurados. Isso segue os valores do logging estruturado descritos acima. Você pode limitar quais mensagens vão para quais logs definindo suas listas de include/exclude, mas isso serve principalmente para filtrar mensagens de diferentes módulos; não foi pensado para ser usado como um serviço de agregação de logs. Para manter o pipeline de logging do Caddy enxuto e eficiente, o processamento avançado de mensagens é deixado para o consumo.

## Consumo

Depois que as mensagens são enviadas para uma saída, um consumidor vai lê-las, fazer o parse e tratá-las adequadamente.

Esse é um domínio de problema muito diferente do de emitir logs, e o core do Caddy não cuida do consumo (embora um módulo de app do Caddy certamente pudesse fazê-lo). Há inúmeras ferramentas que você pode usar para processar fluxos de mensagens JSON (ou outros formatos) e visualizar, filtrar, indexar e consultar logs. Você poderia até escrever ou implementar a sua própria.

Por exemplo, se você executa software legado que exige CLF separado em diferentes arquivos com base em um campo específico (por exemplo, hostname), você poderia usar ou escrever uma ferramenta simples que lê o JSON, chama `sprintf()` para criar uma string CLF e então a grava em um arquivo com base no valor do campo `request.host`.

Os recursos de logging do Caddy também podem ser usados para implementar métricas e tracing: métricas basicamente contam mensagens com certas características, e tracing liga várias mensagens com base em semelhanças entre elas.

Há inúmeras possibilidades para o que você pode fazer consumindo os logs do Caddy!
