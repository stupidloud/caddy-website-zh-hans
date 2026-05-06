---
title: Opções globais (Caddyfile)
---

<script>
ready(function() {
	// Vamos adicionar links nas opções no bloco de código no topo
	// para seus respectivos anchors.
	let headers = Array.from($$_('article h5')).map(el => el.id.replace(/-/g, "_"));

	$$_('pre.chroma .k').forEach(item => {
		if (headers.includes(item.innerText)) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.innerHTML = `<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Adiciona links nos comentários para suas respectivas seções
	$$_('pre.chroma .c1').forEach(item => {
		if (item.innerText.includes('#')) {
			let text = item.innerText;
			let before = text.slice(0, text.indexOf('#')); // whitespace inicial
			text = text.slice(text.indexOf('#')); // apenas a parte do comentário
			let url = '#' + text.replace(/#/g, '').trim().toLowerCase().replace(/ /g, "-");
			item.innerHTML = `${before}<a href="${url}" style="color: inherit;" title="${text}">${text}</a>`;
		}
	});

	// Corrige cirurgicamente um link duplicado; 'name' aparece duas vezes
	// como link para duas seções diferentes, então trocamos o segundo para #name-1
	const caLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('ca [<id>]'));
	if (caLine && caLine.nextElementSibling) {
		const nameLink = caLine.nextElementSibling.querySelector('a');
		if (nameLink && nameLink.innerText.includes('name')) {
			nameLink.href = '#name-1';
		}
	}

	// Corrige cirurgicamente `renewal_window_ratio`, que aparece duas vezes como link
	// para duas seções diferentes, então trocamos o segundo para #renewal_window_ratio-1
	const renewalLine = Array.from($$_('pre.chroma .line'))
		.find(line => line.innerText.includes('renewal_window_ratio'));
	if (renewalLine && renewalLine.nextElementSibling) {
		const renewalLink = renewalLine.nextElementSibling.querySelector('a');
		if (renewalLink && renewalLink.innerText.includes('renewal_window_ratio')) {
			renewalLink.href = '#renewal_window_ratio-1';
		}
	}
});
</script>


<a id="global-options"></a>
# Opções globais

O Caddyfile oferece uma forma de especificar opções que se aplicam globalmente. Algumas opções funcionam como valores padrão; outras personalizam servidores HTTP e não se aplicam apenas a um site em particular; e outras ainda personalizam o comportamento do [adaptador](/docs/config-adapters) do Caddyfile.

O topo do seu Caddyfile pode ser um **bloco de opções globais**. Esse é um bloco que não tem chaves:

```caddy
{
	...
}
```

Pode haver no máximo um, e ele deve ser o primeiro bloco do Caddyfile.

As opções possíveis são (clique em cada opção para ir direto à documentação dela):

```caddy
{
	# Opções gerais
	debug
	http_port    <port>
	https_port   <port>
	default_bind <hosts...>
	order <dir1> first|last|[before|after <dir2>]
	storage <module_name> {
		<options...>
	}
	storage_clean_interval <duration>
	admin   off|<addr> {
		origins <origins...>
		enforce_origin
	}
	persist_config off
	log [name] {
		output  <writer_module> ...
		format  <encoder_module> ...
		level   <level>
		include <namespaces...>
		exclude <namespaces...>
	}
	grace_period   <duration>
	shutdown_delay <duration>
	metrics {
		per_host
		observe_catchall_hosts
		otlp
	}

	# Opções de TLS
	auto_https off|disable_redirects|ignore_loaded_certs|disable_certs
	email <yours>
	default_sni <name>
	fallback_sni <name>
	local_certs
	skip_install_trust
	acme_ca <directory_url>
	acme_ca_root <pem_file>
	acme_eab {
		key_id <key_id>
		mac_key <mac_key>
	}
	acme_dns <provider> ...
	dns <provider> ...
	ech <public_names...> {
		dns <provider> ...
	}
	on_demand_tls {
		ask        <endpoint>
		permission <module>
	}
	key_type ed25519|p256|p384|rsa2048|rsa4096
	cert_issuer <name> ...
	renew_interval <duration>
	cert_lifetime  <duration>
	ocsp_interval  <duration>
	ocsp_stapling off
	renewal_window_ratio <ratio>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}

	# Opções do servidor
	servers [<listener_address>] {
		name <name>
		listener_wrappers {
			<listener_wrappers...>
		}
		timeouts {
			read_body   <duration>
			read_header <duration>
			write       <duration>
			idle        <duration>
		}
		keepalive_interval <duration>
		keepalive_idle     <duration>
		keepalive_count	   <number>
		0rtt off

		trusted_proxies <module> ...
		trusted_proxies_strict
		trusted_proxies_unix
		client_ip_headers <headers...>

		trace
		max_header_size <size>
		enable_full_duplex
		log_credentials
		protocols [h1|h2|h2c|h3]
		strict_sni_host [on|insecure_off]
	}

	# Sistemas de arquivos
	filesystem <name> <module> {
		<options...>
	}

	# Opções de PKI
	pki {
		ca [<id>] {
			name                  <name>
			root_cn               <name>
			intermediate_cn       <name>
			intermediate_lifetime <duration>
			maintenance_interval  <duration>
			renewal_window_ratio  <ratio>
			root {
				format <format>
				cert   <path>
				key    <path>
			}
			intermediate {
				format <format>
				cert   <path>
				key    <path>
			}
		}
	}

	# Opções de eventos
	events {
		on <event> <handler...>
	}
}
```


<a id="general-options"></a>
## Opções gerais

##### `debug`
Ativa o modo de depuração, que define o nível de log como `DEBUG` para o [logger padrão](#log). Isso revela mais detalhes que podem ser úteis na depuração (e é muito verboso em produção). Pedimos que você o habilite antes de pedir ajuda nos [fóruns da comunidade](https://caddy.community). Por exemplo, no topo do seu Caddyfile, se você não tiver outras opções globais:

```caddy
{
	debug
}
```


##### `http_port`
A porta que o servidor deve usar para HTTP.

**Apenas para uso interno**; não altera a porta HTTP para clientes. Isso normalmente é usado se, dentro da sua rede interna, você precisou encaminhar a porta `80` para outra porta (por exemplo `8080`) antes de chegar ao Caddy, por motivos de roteamento.

Padrão: `80`


##### `https_port`
A porta que o servidor deve usar para HTTPS.

**Apenas para uso interno**; não altera a porta HTTPS para clientes. Isso normalmente é usado se, dentro da sua rede interna, você precisou encaminhar a porta `443` para outra porta (por exemplo `8443`) antes de chegar ao Caddy, por motivos de roteamento.

Padrão: `443`


##### `default_bind`
Os endereços padrão de bind a serem usados para todos os sites, se a [`diretiva bind`](/docs/caddyfile/directives/bind) não for usada no site. Padrão: vazio, o que faz bind em todas as interfaces.

<aside class="tip">

Tenha em mente que isso só se aplicará aos servidores gerados pelo Caddyfile; isso significa que o servidor HTTP criado pelo [Automatic HTTPS](/docs/automatic-https) para redirecionamentos HTTP->HTTPS não herdará esses endereços de bind. Para contornar isso, certifique-se de declarar um site `http://` (ele pode ser vazio, sem diretivas) para que ele exista quando o Caddyfile for adaptado e receba os endereços de bind.

</aside>

```caddy
{
	default_bind 10.0.0.1
}
```



##### `order`
Atribui uma ordem a diretivas de HTTP handler. Como os handlers HTTP executam em uma cadeia sequencial, é necessário que eles sejam executados na ordem correta. Diretivas padrão têm uma [ordem pré-definida](/docs/caddyfile/directives#directive-order), mas, se você estiver usando módulos de HTTP handler de terceiros, será preciso definir a ordem explicitamente usando esta opção ou colocando a diretiva em um [`bloco route`](/docs/caddyfile/directives/route). A ordenação pode ser descrita de forma absoluta (`first` ou `last`) ou relativa (`before` ou `after`) a outra diretiva.

Por exemplo, para usar o [plugin `replace-response`](https://github.com/caddyserver/replace-response), você deve garantir que a diretiva dele fique ordenada depois de `encode`, para que ele possa fazer substituições antes de a resposta ser codificada (porque as respostas sobem pela cadeia de handlers, e não descem):

```caddy
{
	order replace after encode
}
```


##### `storage`
Configura o mecanismo de storage do Caddy. O padrão é [`file_system`](/docs/json/storage/file_system/). Há muitos outros [módulos de storage](/docs/json/storage/) disponíveis, fornecidos por plugins.

Por exemplo, para mudar a localização do storage no sistema de arquivos:

```caddy
{
	storage file_system /path/to/custom/location
}
```

Personalizar o módulo de storage normalmente é necessário quando você sincroniza o storage do Caddy entre várias instâncias do Caddy para garantir que todas usem os mesmos certificados e chaves. Veja a seção [Automatic HTTPS sobre storage](/docs/automatic-https#storage) para mais detalhes.


##### `storage_clean_interval`
Com que frequência verificar unidades de storage em busca de ativos antigos ou expirados e removê-los. Essas varreduras fazem muitas leituras (e operações de listagem) no módulo de storage, então escolha um intervalo maior para implantações grandes. Aceita [valores de duração](/docs/conventions#durations).

O storage sempre será limpo quando o processo iniciar pela primeira vez. Depois disso, uma nova limpeza será iniciada esta duração após o início da limpeza anterior, se a limpeza anterior tiver sido concluída em menos da metade do tempo desse intervalo (caso contrário, o próximo início será pulado).

Padrão: `24h`

```caddy
{
	storage_clean_interval 7d
}
```




##### `admin`
Personaliza o [endpoint da API de administração](/docs/api). Aceita placeholders. Usa [endereços de rede](/docs/conventions#network-addresses).

Padrão: `localhost:2019`, a menos que a variável de ambiente `CADDY_ADMIN` esteja definida.

Se definido como `off`, o endpoint de administração será desativado. Quando desativado, **mudanças de configuração ficarão impossíveis** sem parar e iniciar o servidor, já que o comando [`caddy reload`](/docs/command-line#caddy-reload) usa a API de administração para enviar a nova configuração ao servidor em execução.

Lembre-se de usar a flag de CLI `--address` com [comandos](/docs/command-line) compatíveis para especificar o endpoint de administração atual, caso o endereço do servidor em execução tenha sido alterado do padrão.

Também suporta estas subopções:

- **origins** configura a lista de [origens](https://developer.mozilla.org/en-US/docs/Glossary/Origin) que podem se conectar ao endpoint.

  Um padrão é escolhido de forma inteligente:
  - se o endereço de listen for loopback (por exemplo `localhost`, um IP de loopback ou um unix socket), então as origens permitidas serão `localhost`, `::1` e `127.0.0.1`, combinadas com a porta do endereço de listen (então `localhost:2019` é uma origem válida).
  - se o endereço de listen não for loopback, a origem permitida será o próprio endereço de listen.

  Se o host do endereço de listen não for uma interface curinga (coringas incluem: string vazia, ou `0.0.0.0`, ou `[::]`), então a verificação do cabeçalho `Host` é aplicada. Na prática, isso significa que, por padrão, o cabeçalho `Host` é validado para estar em `origins`, já que a interface é `localhost`. Mas, para um endereço como `:2020`, que tem uma interface curinga, a validação do cabeçalho `Host` não é feita.

- **enforce_origin** força a validação do cabeçalho de requisição `Origin`. Isso é feito implicitamente sempre que cabeçalhos CORS são enviados pelo cliente ou se o cliente desabilita explicitamente CORS com `Sec-Fetch-Mode: no-cors`. Caso contrário, essa opção é mais útil quando o endereço de listen é uma interface curinga (já que `Host` não é validado) e a API de administração está exposta à internet pública. Ela habilita checagens de preflight CORS e garante que o cabeçalho `Origin` seja validado contra a lista `origins`. Use isso apenas se você estiver executando o Caddy na sua máquina de desenvolvimento e precisar acessar a API de administração a partir de um navegador.

Por exemplo, para expor a API de administração em outra porta, em todas as interfaces — ⚠️ essa porta **não deve ser exposta publicamente**, caso contrário qualquer pessoa poderá controlar seu servidor; considere habilitar a validação de origem se precisar que ela seja pública:

```caddy
{
	admin :2020
}
```

Para desligar a API de administração — ⚠️ isso torna **recarregamentos de configuração impossíveis** sem parar e iniciar o servidor:

```caddy
{
	admin off
}
```

Para usar um [unix socket](/docs/conventions#network-addresses) para a API de administração, permitindo controle de acesso via permissões de arquivo:

```caddy
{
	admin unix//run/caddy-admin.sock
}
```

Para permitir apenas requisições com um cabeçalho `Origin` correspondente:

```caddy
{
	admin :2019 {
		origins http://localhost:2019 http://example.com:8080
		enforce_origin
	}
}
```


##### `persist_config`

Controla se a configuração JSON atual deve ser persistida no [diretório de configuração](/docs/conventions#configuration-directory), para evitar perder mudanças feitas via API de administração. Atualmente, apenas a opção `off` é suportada. Por padrão, a configuração é persistida.

```caddy
{
	persist_config off
}
```



##### `log`
Configura loggers nomeados.

O nome pode ser informado para indicar um logger específico cujo comportamento será personalizado. Se nenhum nome for especificado, o comportamento do logger `default` é modificado. Você pode ler mais sobre o logger `default` e sobre [como o logging funciona no Caddy](/docs/logging).

Vários loggers com nomes diferentes podem ser configurados usando `log` várias vezes.

Isso difere da [`diretiva log`](/docs/caddyfile/directives/log), que configura apenas o logging de requisições HTTP (também conhecido como access logs). A opção global `log` compartilha sua estrutura de configuração com a diretiva (exceto por `include` e `exclude`), e a documentação completa pode ser encontrada na página da diretiva.

- **output** configura onde escrever os logs.

  Veja a [`diretiva log`](/docs/caddyfile/directives/log#output-modules) para a documentação completa.

- **format** descreve como codificar, ou formatar, os logs.

  Veja a [`diretiva log`](/docs/caddyfile/directives/log#format-modules) para a documentação completa.

- **level** é o nível mínimo de entrada a ser logado.

  Padrão: `INFO`.

  Valores possíveis: `DEBUG`, `INFO`, `WARN`, `ERROR` e, muito raramente, `PANIC`, `FATAL`.

- **include** especifica os nomes de log a incluir neste logger.

  Por padrão, esta lista está vazia (isto é, todos os logs são incluídos).

  Por exemplo, para incluir apenas logs emitidos pela API de administração, você incluiria `admin.api`.

- **exclude** especifica os nomes de log a excluir deste logger.

  Por padrão, esta lista está vazia (isto é, nenhum log é excluído).

  Por exemplo, para excluir apenas os HTTP access logs, você excluiria `http.log.access`.

Os nomes de logger que `include` e `exclude` aceitam dependem dos módulos usados, e a forma mais fácil de descobri-los é pelos logs anteriores.

Aqui está um exemplo que registra em json todos os HTTP access logs e logs da administração no stdout:

```caddy
{
	log default {
		output stdout
		format json
		include http.log.access admin.api
	}
}
```

##### `grace_period`
Define o período de graça para desligar servidores HTTP (isto é, durante mudanças de configuração ou quando o Caddy está parando).

Durante o período de graça, nenhuma nova conexão é aceita, conexões ociosas são fechadas e conexões ativas aguardam impacientemente a conclusão das requisições. Se os clientes não concluírem suas requisições dentro do período de graça, o servidor será encerrado à força para permitir que o reload termine e liberar recursos. Aceita [valores de duração](/docs/conventions#durations).

Por padrão, o período de graça é infinito, o que significa que conexões nunca são fechadas à força.

```caddy
{
	grace_period 10s
}
```


##### `shutdown_delay`
Define uma [duração](/docs/conventions#durations) _antes_ do [período de graça](#grace_period), durante a qual um servidor que será desligado continua operando normalmente, exceto que o placeholder `{http.shutting_down}` avalia para `true` e `{http.time_until_shutdown}` informa o tempo até o início do período de graça.

Isso causa um atraso se algum servidor estiver sendo desligado como parte de uma mudança de configuração, e efetivamente agenda a mudança para mais tarde. Isso é útil para avisar health checkers da morte iminente do servidor e dar tempo para um load balancer tirá-lo da rotação; por exemplo:

```caddy
{
	shutdown_delay 30s
}

example.com {
	handle /health-check {
		@goingDown vars {http.shutting_down} true
		respond @goingDown "Tchau em {http.time_until_shutdown}" 503
		respond 200
	}
	handle {
		respond "Olá, mundo!"
	}
}
```


<a id="tls-options"></a>
## Opções de TLS

##### `auto_https`
Configura o [Automatic HTTPS](/docs/automatic-https), o recurso que permite ao Caddy automatizar o gerenciamento de certificados e redirecionamentos HTTP-to-HTTPS para seus sites.

Há alguns modos para escolher:

- `off`: desativa tanto a automação de certificados quanto os redirecionamentos HTTP-to-HTTPS.

- `disable_redirects`: desativa apenas os redirecionamentos HTTP-to-HTTPS.

- `disable_certs`: desativa apenas a automação de certificados.

- `ignore_loaded_certs`: automatiza certificados mesmo para nomes que apareçam em certificados carregados manualmente. Útil se você especificou um certificado usando a [`diretiva tls`](/docs/caddyfile/directives/tls) que contém nomes (ou wildcards) que você quer que sejam gerenciados automaticamente.

<aside class="tip">

Essa opção não afeta o protocolo padrão do Caddy, que é sempre HTTPS, quando um endereço de site tem um nome de domínio válido. Isso significa que `auto_https off` não fará seu site ser servido por HTTP; ele apenas desativará o gerenciamento automático de certificados e os redirecionamentos.

Ou seja, se você quiser servir seu site por HTTP, deve mudar o [endereço do site](/docs/caddyfile/concepts#addresses) para começar com `http://` ou terminar com `:80` (ou com a [`opção http_port`](#http_port)).

</aside>

```caddy
{
	auto_https disable_redirects
}
```


##### `email`
Seu endereço de e-mail. Usado principalmente ao criar uma conta ACME com sua CA, e é altamente recomendado caso haja problemas com seus certificados.

<aside class="tip">

Tenha em mente que a Let's Encrypt pode enviar e-mails sobre o certificado se aproximando da expiração, mas isso pode ser enganoso porque o Caddy pode ter escolhido usar outro emissor (por exemplo ZeroSSL) na renovação. Verifique seus logs e/ou o próprio certificado (no navegador, por exemplo) para ver qual emissor foi usado e se a expiração ainda é válida; se estiver, você pode ignorar o e-mail da Let's Encrypt com segurança.

</aside>

```caddy
{
	email admin@example.com
}
```


##### `default_sni`
Define um ServerName TLS padrão quando os clientes não usam SNI no ClientHello.

```caddy
{
	default_sni example.com
}
```


##### `fallback_sni`
⚠️ <i>Experimental</i>

Se configurado, o fallback se torna o ServerName TLS no ClientHello caso o ServerName original não corresponda a nenhum certificado no cache.

Os usos disso são bastante específicos; normalmente, se um cliente for uma CDN e repassar o ServerName do handshake downstream, mas puder aceitar um certificado com o hostname da origem em vez disso, então você definiria isso como o hostname da sua origem. Observe que o Caddy precisa estar gerenciando um certificado para esse nome.

```caddy
{
	fallback_sni example.com
}
```


##### `local_certs`
Faz com que **todos** os certificados sejam emitidos internamente por padrão, em vez de por uma ACME CA pública como Let's Encrypt. Isso é útil como um atalho rápido em ambientes de desenvolvimento.

```caddy
{
	local_certs
}
```


##### `skip_install_trust`
Pula as tentativas de instalar a raiz da CA local no trust store do sistema, bem como nos trust stores do Java e do Mozilla Firefox.

```caddy
{
	skip_install_trust
}
```


##### `acme_ca`
Especifica a URL do diretório da ACME CA. É fortemente recomendado definir isso para o [endpoint de staging do Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) para testes ou desenvolvimento. Padrão: endpoints de produção do ZeroSSL e do Let's Encrypt.

Observe que uma ACME CA configurada globalmente pode não se aplicar a todos os sites; veja os [requisitos de hostname](/docs/automatic-https#hostname-requirements) para usar o(s) emissor(es) ACME padrão.

```caddy
{
	acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}
```

##### `acme_ca_root`
Especifica um arquivo PEM que contém um certificado raiz confiável para endpoints da ACME CA, caso ele não esteja no trust store do sistema.

```caddy
{
	acme_ca_root /path/to/ca/root.pem
}
```


##### `acme_eab`
Especifica um External Account Binding a ser usado para todas as transações ACME.

Por exemplo, com credenciais falsas do ZeroSSL:

```caddy
{
	acme_eab {
		key_id GD-VvWydSVFuss_GhBwYQQ
		mac_key MjXU3MH-Z0WQ7piMAnVsCpD1shgMiWx6ggPWiTmydgUaj7dWWWfQfA
	}
}
```


##### `acme_dns`
Configura o provedor de [desafio ACME DNS](/docs/automatic-https#dns-challenge) a ser usado para todas as transações ACME.

Requer uma build personalizada do Caddy com um plugin para o seu provedor de DNS.

Os tokens que seguem o nome do provedor configuram o provedor do mesmo modo que se fossem especificados no [`issuer acme` da `diretiva tls`](/docs/caddyfile/directives/tls#acme).

```caddy
{
	acme_dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```


##### `dns`
Configura um provedor DNS padrão a ser usado quando nenhum outro for especificado localmente em um contexto relevante. Por exemplo, se o desafio ACME DNS estiver habilitado mas não tiver um provedor DNS configurado, esse padrão global será usado. Ele também é aplicado ao publicar configurações de Encrypted ClientHello (ECH).

Seu binário do Caddy deve ser compilado com o módulo do provedor DNS especificado para isso funcionar.

Exemplo, usando credenciais de uma variável de ambiente:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
}
```

(Requer Caddy 2.10 beta 1 ou mais recente.)


##### `ech`
Habilita Encrypted ClientHello (ECH) usando os nomes de domínio públicos especificados como o nome do servidor em texto claro (SNI) nos handshakes TLS. Nas condições corretas, ECH pode ajudar a proteger os nomes de domínio dos seus sites no tráfego. O Caddy gerará e publicará uma configuração ECH para cada nome público especificado. A publicação é como clientes compatíveis (como navegadores modernos configurados corretamente) sabem que devem usar ECH para acessar seus sites.

Para funcionar corretamente, a(s) configuração(ões) ECH precisa(m) ser publicada(s) de um modo que os clientes esperam. A maioria dos navegadores (com DNS-over-HTTPS ou DNS-over-TLS habilitado) espera que as configurações ECH sejam publicadas em registros DNS do tipo HTTPS. O Caddy faz esse tipo de publicação automaticamente, mas você precisa especificar um provedor DNS, seja com a subopção `dns` ou globalmente com a [opção global `dns`](#dns), e o binário do Caddy deve ser compilado com o módulo do provedor DNS especificado. (Builds personalizadas estão disponíveis na nossa [página de download](/download).)

**Avisos de privacidade:**

- Em geral, é aconselhável **maximizar o tamanho do seu [_conjunto de anonimato_](https://www.ietf.org/archive/id/draft-ietf-tls-esni-23.html#name-introduction)**. Por isso, normalmente recomendamos que a maioria dos usuários configure _apenas um_ nome de domínio público para proteger todos os sites.
- **Seu servidor deve ser autoritativo para o(s) nome(s) de domínio público que você especificar** (isto é, eles devem apontar para o seu servidor), porque o Caddy obterá um certificado para eles. Esses certificados são vitais para ajudar clientes compatíveis com a especificação a se conectarem de forma confiável e segura com ECH em alguns casos. Eles são usados apenas para facilitar um handshake ECH adequado, e não para dados da aplicação (seus sites -- a menos que você defina um site com o mesmo nome do seu domínio público).
- Cada circunstância pode ser diferente. Recomendamos consultar especialistas para **revisar seu modelo de ameaça** se o risco for alto, já que ECH não é uma solução única para todos os casos.

Exemplo usando credenciais de uma variável de ambiente para publicação em nameservers hospedados na Cloudflare:

```caddy
{
	dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	ech ech.example.net
}
```

Isso deve fazer com que clientes compatíveis carreguem todos os seus sites com `ech.example.net`, em vez dos nomes individuais dos sites expostos em texto claro.

Uma publicação bem-sucedida exige que os domínios do seu site estejam hospedados no provedor DNS configurado e que os registros possam ser modificados com as credenciais / configuração de provedor fornecidas.

(Requer Caddy 2.10 beta 1 ou mais recente.)


##### `on_demand_tls`
Configura [On-Demand TLS](/docs/automatic-https#on-demand-tls) onde ele estiver habilitado, mas não o habilita (para habilitá-lo, use a [`subdiretiva on_demand` da diretiva `tls`](/docs/caddyfile/directives/tls#syntax)). Obrigatório para uso em ambientes de produção, para evitar abuso.

- **ask** faz o Caddy enviar uma requisição HTTP para a URL fornecida, perguntando se um domínio pode ter um certificado emitido.

  A requisição tem uma query string `?domain=` contendo o valor do nome de domínio.

  Se o endpoint retornar um código de status `2xx`, o Caddy estará autorizado a obter um certificado para esse nome. Qualquer outro código de status resultará no cancelamento da emissão do certificado e em erro no handshake TLS.

<aside class="tip">

O endpoint `ask` deve responder _o mais rápido possível_, em poucos milissegundos, idealmente. Normalmente, o endpoint deve fazer uma consulta em tempo constante em um banco de dados indexado por nome de domínio; evite loops. Evite fazer consultas DNS ou outras requisições de rede.

</aside>

- **permission** permite usar módulos personalizados para determinar se um certificado deve ser emitido para um nome específico. O módulo deve implementar a [`interface caddytls.OnDemandPermission`](https://pkg.go.dev/github.com/caddyserver/caddy/v2/modules/caddytls#OnDemandPermission). Um módulo `http` de permissão está incluído, que é o que a opção `ask` usa, e permanece como atalho por compatibilidade com versões anteriores.

- ⚠️ Opções de limitação por taxa **interval** e **burst** estavam disponíveis, mas NÃO são recomendadas. Remova-as da configuração se ainda as tiver.

```caddy
{
	on_demand_tls {
		ask http://localhost:9123/ask
	}
}

https:// {
	tls {
		on_demand
	}
}
```


##### `key_type`
Especifica o tipo de chave a gerar para certificados TLS; só altere isso se tiver uma necessidade específica de personalização.

Os valores possíveis são: `ed25519`, `p256`, `p384`, `rsa2048`, `rsa4096`.

```caddy
{
	key_type ed25519
}
```


##### `cert_issuer`
Define o emissor (ou fonte) dos certificados TLS.

Isso permite configurar emissores globalmente, em vez de por site como você faria com a [`subdiretiva issuer` da diretiva `tls`](/docs/caddyfile/directives/tls#issuer).

Pode ser repetida se você quiser configurar mais de um emissor a ser tentado. Eles serão tentados na ordem em que forem definidos.

```caddy
{
	cert_issuer acme {
		...
	}
	cert_issuer zerossl {
		...
	}
}
```


##### `renew_interval`
Com que frequência verificar todos os certificados carregados e gerenciados em busca de expiração, e acionar a renovação se estiverem expirados.

Padrão: `10m`

```caddy
{
	renew_interval 30m
}
```


##### `cert_lifetime`
O período de validade que será solicitado à CA para emitir um certificado.

Esse valor é usado para calcular o campo `notAfter` da ordem ACME; portanto, o sistema precisa ter um relógio razoavelmente sincronizado. OBSERVAÇÃO: Nem todas as CAs suportam isso. Consulte a documentação ACME da sua CA para ver se isso é permitido e quais valores podem ser usados.

Padrão: `0` (a CA escolhe a duração, normalmente 90 dias)

⚠️ Este é um recurso experimental. Sujeito a mudanças ou remoção.

```caddy
{
	cert_lifetime 30d
}
```


##### `ocsp_interval`
Com que frequência verificar se os [staples OCSP <img src="/old/resources/images/external-link.svg" class="external-link">](https://en.wikipedia.org/wiki/OCSP_stapling) precisam ser atualizados.

Padrão: `1h`

```caddy
{
	ocsp_interval 2h
}
```


##### `ocsp_stapling`
Pode ser definido como `off` para desativar OCSP stapling. Útil em ambientes nos quais os responders não podem ser alcançados por causa de firewalls.

```caddy
{
	ocsp_stapling off
}
```

##### `renewal_window_ratio`
A proporção (entre 0 e 1) da duração do certificado que ainda deve restar antes de o Caddy tentar renová-lo. Por exemplo, se um certificado tiver duração de 90 dias e essa proporção for `0.3333` (o valor padrão), então o Caddy tentará renovar o certificado continuamente quando ele tiver 30 dias ou menos restantes antes da expiração. Também pode ser definido por site com a [`subdiretiva renewal_window_ratio` da diretiva `tls`](/docs/caddyfile/directives/tls#renewal_window_ratio).

Você raramente precisará alterar isso, mas pode ser útil renovar mais tarde na vida útil do certificado se sua CA tiver um tempo de emissão muito longo.

Tenha em mente que isso é apenas uma sugestão, já que emissores ACME podem implementar a [extensão ARI](https://datatracker.ietf.org/doc/rfc9773/), na qual o emissor dita uma janela em que o cliente ACME (o Caddy, neste caso) deve tentar renovar, e essa janela pode não coincidir com essa proporção.

```caddy
{
	renewal_window_ratio 0.1
}
```


##### `preferred_chains`
Se sua CA fornecer várias cadeias de certificados, você pode usar esta opção para especificar qual cadeia o Caddy deve preferir. Defina uma das opções a seguir:

- **smallest** fará o Caddy preferir cadeias com o menor número de bytes.

- **root_common_name** é uma lista de um ou mais common names; o Caddy escolherá a primeira cadeia cujo root corresponda a pelo menos um dos common names especificados.

- **any_common_name** é uma lista de um ou mais common names; o Caddy escolherá a primeira cadeia cujo emissor corresponda a pelo menos um dos common names especificados.

Observe que especificar `preferred_chains` como uma opção global afetará todos os emissores se não houver nenhuma [configuração de emissor em nível superior que a sobrescreva](/docs/caddyfile/directives/tls#acme).

```caddy
{
	preferred_chains smallest
}
```

```caddy
{
	preferred_chains {
		root_common_name "ISRG Root X2"
	}
}
```


<a id="server-options"></a>
## Opções do servidor

Personaliza [servidores HTTP](/docs/json/apps/http/servers/) com configurações que podem abranger vários sites e, portanto, não podem ser configuradas corretamente em blocos de site. Essas opções afetam o listener/socket ou outras facilidades abaixo da camada HTTP.

Podem ser especificadas mais de uma vez com diferentes valores de `listener_address` para configurar opções diferentes por servidor. Por exemplo, `servers :443` se aplicará apenas ao servidor vinculado ao endereço de listener `:443`. Omitir o endereço de listener aplicará as opções a qualquer servidor restante.

<aside class="tip">

Use o comando [`caddy adapt`](/docs/command-line#caddy-adapt) para descobrir o endereço de listen dos servidores no seu Caddyfile.

</aside>


Por exemplo, para configurar opções diferentes para os servidores nas portas `:80` e `:443`, você especificaria dois blocos `servers`:

```caddy
{
	servers :443 {
		listener_wrappers {
			http_redirect
			tls
		}
	}

	servers :80 {
		protocols h1 h2c
	}
}
```

Ao usar `servers`, ele **só** se aplica a servidores que **realmente aparecem** no seu Caddyfile (isto é, produzidos por um bloco de site). Lembre-se de que [Automatic HTTPS](/docs/automatic-https) criará um servidor ouvindo na porta `80` (ou na [`opção http_port`](#http_port)) para servir redirecionamentos HTTP->HTTPS e resolver o desafio ACME HTTP; isso acontece em runtime, isto é, _depois_ que o adaptador do Caddyfile aplica `servers`. Em outras palavras, isso significa que `servers` **não** se aplicará a `:80` a menos que você declare explicitamente um bloco de site como `http://` ou `:80`.


<aside class="tip">

Se você estiver usando a [`diretiva bind`](/docs/caddyfile/directives/bind) ou a [`opção global default_bind`](/docs/caddyfile/options#default_bind), o `listener_address` *DEVE* corresponder ao endereço de bind combinado com a porta do bloco de site; caso contrário, as configurações não serão aplicadas. Por exemplo:

```caddy
{
	# Isto NÃO vai corresponder ao servidor, endereço de bind ausente
	servers :8080 {
		name private
	}

	# Isto vai funcionar porque é uma correspondência exata
	servers 192.168.1.2:8080 {
		name public
	}
}

:8080 {
	bind 127.0.0.1
}

:8080 {
	bind 192.168.1.2
}
```

</aside>



##### `name`

Um nome personalizado para atribuir a este servidor. Normalmente é útil para identificar um servidor pelo nome nos logs e métricas. Se não for definido, o Caddy o nomeará dinamicamente usando um padrão `srvX`, em que `X` começa em `0` e incrementa com base no número de servidores na configuração.

Tenha em mente que apenas servidores produzidos por blocos de site na sua configuração terão essas configurações aplicadas. [Automatic HTTPS](/docs/automatic-https) cria um servidor `:80` (ou [`http_port`](#http_port)) em runtime, então, se você quiser renomeá-lo, precisará de pelo menos um bloco de site `http://` vazio.

Por exemplo:

```caddy
{
	servers :443 {
		name https
	}

	servers :80 {
		name http
	}
}

example.com {
}

http:// {
}
```

</aside>



##### `listener_wrappers`

Permite configurar [listener wrappers](/docs/json/apps/http/servers/listener_wrappers/), que podem modificar o comportamento do socket listener. Eles são aplicados na ordem fornecida.

###### `tls`

O listener wrapper `tls` é um wrapper sem efeito que marca onde o listener TLS deve ficar em uma cadeia de listener wrappers. Ele só deve ser usado se outro listener wrapper precisar ficar na frente do handshake TLS.

###### `http_redirect`

O [`http_redirect`](/docs/json/apps/http/servers/listener_wrappers/http_redirect/) fornece redirecionamentos HTTP->HTTPS para conexões que chegam na porta TLS como uma requisição HTTP, detectando pelos primeiros bytes que não se trata de um handshake TLS, mas sim de uma requisição HTTP. Isso é mais útil ao servir HTTPS em uma porta não padrão (outra que não `443`), já que os navegadores tentarão HTTP a menos que o esquema seja especificado. Ele deve ser colocado _antes_ do listener wrapper `tls`. Aqui está um exemplo:

```caddy
{
	servers {
		listener_wrappers {
			http_redirect
			tls
		}
	}
}
```

###### `proxy_protocol`

O listener wrapper [`proxy_protocol`](/docs/json/apps/http/servers/listener_wrappers/proxy_protocol/) (antes da v2.7.0 ele só estava disponível por plugin) habilita o parsing do [PROXY protocol](https://github.com/haproxy/haproxy/blob/master/doc/proxy-protocol.txt) (popularizado pelo HAProxy). Ele deve ser usado _antes_ do listener wrapper `tls`, já que analisa dados em texto claro no início da conexão:

Tenha cuidado, porque metadados do PROXY protocol podem ser aplicados à conexão antes da avaliação dos matchers ou de [`trusted_proxies`](/docs/caddyfile/options#trusted-proxies). O endereço IP do peer imediato será perdido para avaliações posteriores.

```caddy-d
proxy_protocol {
	timeout <duration>
	allow <cidrs...>
	deny <cidrs...>
	fallback_policy <policy>
}
```

- **timeout** especifica a duração máxima para aguardar o cabeçalho PROXY. O padrão é `5s`.

- **allow** é uma lista de intervalos CIDR de origens confiáveis que podem enviar cabeçalhos PROXY. Unix sockets são confiáveis por padrão e não fazem parte desta opção.

- **deny** é uma lista de intervalos CIDR de origens confiáveis para os quais cabeçalhos PROXY devem ser rejeitados.

- **fallback_policy** é a ação a tomar se o cabeçalho PROXY vier de um endereço que não esteja em nenhuma das listas allow/deny. A política de fallback padrão é `ignore`. Os valores aceitos para `fallback_policy` são:
	- `ignore`: usa o endereço do cabeçalho PROXY, mas aceita a conexão
	- `use`: usa o endereço do cabeçalho PROXY
	- `reject`: rejeita a conexão quando o cabeçalho PROXY é enviado
	- `require`: exige que a conexão envie o cabeçalho PROXY, rejeita se ele não estiver presente
	- `skip`: aceita a conexão sem exigir o cabeçalho PROXY.


Por exemplo, para um servidor HTTPS (que precisa do listener wrapper `tls`) que aceita cabeçalhos PROXY de um intervalo específico de endereços IP e rejeita cabeçalhos PROXY de um intervalo diferente, com timeout de 2 segundos:

```caddy
{
	servers {
		listener_wrappers {
			proxy_protocol {
				timeout 2s
				allow 192.168.86.1/24 192.168.86.1/24
				deny 10.0.0.0/8
				fallback_policy reject
			}
			tls
		}
	}
}
```


##### `timeouts`

- **read_body** é um [valor de duração](/docs/conventions#durations) que define por quanto tempo será permitido ler o upload de um cliente. Definir isso para um valor curto e não zero pode mitigar ataques slowloris, mas também pode afetar clientes genuinamente lentos. Padrão: sem timeout.

- **read_header** é um [valor de duração](/docs/conventions#durations) que define por quanto tempo será permitido ler os cabeçalhos da requisição de um cliente. Padrão: sem timeout.

- **write** é um [valor de duração](/docs/conventions#durations) que define por quanto tempo será permitido escrever para um cliente. Observe que definir isso para um valor pequeno ao servir arquivos grandes pode afetar negativamente clientes genuinamente lentos. Padrão: sem timeout.

- **idle** é um [valor de duração](/docs/conventions#durations) que define o tempo máximo de espera pela próxima requisição quando keep-alives estão habilitados. Padrão: 5 minutos para ajudar a evitar exaustão de recursos.

```caddy
{
	servers {
		timeouts {
			read_body   10s
			read_header 5s
			write       30s
			idle        10m
		}
	}
}
```


##### `keepalive_interval`

O intervalo no qual pacotes TCP keepalive são enviados para manter a conexão viva na camada TCP quando nenhum outro dado está sendo transmitido. Padrão: `15s`.

```caddy
{
	servers {
		keepalive_interval 30s
	}
}
```


##### `keepalive_idle`

A duração pela qual uma conexão deve ficar ociosa antes que pacotes TCP keepalive sejam enviados quando nenhum outro dado está sendo transmitido. Padrão: `15s`.

```caddy
{
	servers {
		keepalive_idle 1m
	}
}
```


##### `keepalive_count`

O número máximo de pacotes TCP keepalive a enviar antes de considerar a conexão morta. Padrão: `9`.

```caddy
{
	servers {
		keepalive_count 5
	}
}
```


##### `0rtt`

Por padrão, 0-RTT (early data) está habilitado para listeners QUIC (isto é, HTTP/3) para permitir que clientes enviem dados no primeiro round trip do handshake TLS, o que pode melhorar o desempenho em conexões repetidas.

Você pode definir isso como `off` para desabilitar 0-RTT para listeners QUIC. Um motivo para desabilitar 0-RTT é se um matcher [`remote_ip`](/docs/caddyfile/matchers#remote-ip) for usado, o que introduz uma dependência de o endereço remoto ser verificado se o roteamento acontecer antes de o handshake TLS ser concluído. Um response HTTP 425 é escrito nesse caso, mas alguns clientes (navegadores) podem se comportar mal e não fazer retry, então desabilitar 0-RTT pode garantir que responses 425 não sejam vistos pelos usuários, ao custo de perder os benefícios de desempenho do 0-RTT.

```caddy
{
	servers {
		0rtt off
	}
}
```


##### `trusted_proxies`

Permite configurar intervalos IP (CIDRs) de servidores proxy a partir dos quais as requisições devem ser confiáveis. Por padrão, nenhum proxy é confiável.

Habilitar isso faz com que requisições confiáveis tenham o IP _real_ do cliente analisado a partir dos cabeçalhos HTTP (por padrão, `X-Forwarded-For`; veja [`client_ip_headers`](#client-ip-headers) para configurar outros cabeçalhos). Se confiável, o IP do cliente é adicionado aos [access logs](/docs/caddyfile/directives/log), fica disponível como um [placeholder](/docs/caddyfile/concepts#placeholders) `{client_ip}`, e permite o uso do [`matcher client_ip`](/docs/caddyfile/matchers#client-ip). Se a requisição não vier de um proxy confiável, o IP do cliente é definido como o endereço IP remoto da conexão de entrada direta ou como o endereço definido pelo [PROXY protocol](/docs/caddyfile/options#proxy-protocol), se usado. Por padrão, os IPs nos cabeçalhos são analisados da esquerda para a direita. Veja [`trusted_proxies_strict`](#trusted-proxies-strict) para alterar esse comportamento.

Alguns matchers ou handlers podem usar o status de confiança da requisição para tomar decisões. Por exemplo, se confiável, o handler [`reverse_proxy`](/docs/caddyfile/directives/reverse_proxy#defaults) fará proxy e acrescentará os cabeçalhos de requisição sensíveis `X-Forwarded-*`.

Atualmente, apenas o módulo de origem de IP `static` está incluído com a distribuição padrão do Caddy, mas isso pode ser [estendido](/docs/extending-caddy) com plugins para manter uma lista dinâmica de intervalos IP.


###### `static`

Recebe uma lista estática (imutável) de intervalos IP (CIDRs) para confiar.

Como atalho, `private_ranges` pode ser usado para corresponder a todos os intervalos privados IPv4 e IPv6. É o mesmo que especificar todos estes intervalos: `192.168.0.0/16 172.16.0.0/12 10.0.0.0/8 127.0.0.1/8 fd00::/8 ::1`.

A sintaxe é a seguinte:

```caddy-d
trusted_proxies static [private_ranges] <ranges...>
```

Aqui está um exemplo completo, confiando em um intervalo IPv4 de exemplo e um intervalo IPv6:

```caddy
{
	servers {
		trusted_proxies static 12.34.56.0/24 1200:ab00::/32
	}
}
```

##### `trusted_proxies_strict`

Quando [`trusted_proxies`](#trusted-proxies) está habilitado, os IPs nos cabeçalhos (configurados por [`client_ip_headers`](#client-ip-headers)) são analisados da esquerda para a direita por padrão. O primeiro endereço IP não confiável encontrado se torna o endereço real do cliente. Desde a v2.8, você pode optar por analisar esses cabeçalhos da direita para a esquerda com `trusted_proxies_strict`. Por padrão, essa opção está desativada por compatibilidade com versões anteriores.

Proxies upstream como HAProxy, CloudFlare, AWS ALB, CloudFront etc. acrescentam cada novo endereço remoto de conexão à direita de `X-Forwarded-For`. É recomendável habilitar `trusted_proxies_strict` ao trabalhar com eles, pois o IP mais à esquerda pode ser falsificado pelo cliente.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		trusted_proxies_strict
	}
}
```

<aside class="tip">

Especificamente no caso do AWS ALB, você certamente vai querer habilitar essa opção. [Pela documentação deles](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/x-forwarded-headers.html#w227aac13c27b9c15), você só pode identificar o IP real do cliente definindo o modo XFF como `append`. Esse IP será acrescentado à direita de `X-Forwarded-For` e só pode ser extraído com segurança via `trusted_proxies_strict`.

</aside>

##### `trusted_proxies_unix`

A opção `trusted_proxies_unix` permite confiar em todas as conexões vindas de Unix sockets, o que é útil quando o Caddy está atrás de um reverse proxy (possivelmente outra instância do Caddy) que se conecta a ele via um Unix socket (isto é, a [`diretiva bind`](/docs/caddyfile/directives/bind) aponta para um unix socket). Isso está desativado por padrão.

```caddy
{
	servers {
		trusted_proxies_unix
	}
}
```

##### `client_ip_headers`

Em conjunto com [`trusted_proxies`](#trusted-proxies), permite configurar quais cabeçalhos usar para determinar o endereço IP do cliente. Por padrão, apenas `X-Forwarded-For` é considerado. Vários campos de cabeçalho podem ser especificados; nesse caso, o primeiro valor de cabeçalho não vazio é usado.

```caddy
{
	servers {
		trusted_proxies static private_ranges
		client_ip_headers X-Forwarded-For X-Real-IP
	}
}
```


##### `metrics`

Habilita a coleta de métricas; necessário antes de fazer scrape das métricas ou enviá-las com OTLP. Observe que métricas reduzem o desempenho em servidores muito movimentados. (Nossa comunidade está trabalhando para melhorar isso. Participe!)

```caddy
{
	metrics
}
```

Você pode adicionar a opção `per_host` para rotular as métricas com o nome do host da métrica.

```caddy
{
	metrics {
		per_host
	}
}
```

Devido ao potencial de cardinalidade infinita ao observar todos os possíveis hosts que podem ser enviados por clientes, o Caddy só registrará métricas para hosts configurados, enquanto todos os outros hosts (por exemplo, `attacker.com`) serão agregados sob o rótulo `"_other"`. Para forçar a observação de todos os hosts, quando um potencial de cardinalidade infinita é um risco aceitável, adicione `observe_catchall_hosts`. Observe que adicionar `observe_catchall_hosts` não habilitará `per_host`. No entanto, isso é habilitado automaticamente para servidores HTTPS (já que certificados fornecem alguma proteção contra cardinalidade ilimitada), mas está desativado por padrão para servidores HTTP para evitar ataques de cardinalidade por meio de cabeçalhos Host arbitrários.

```caddy
{
	metrics {
		per_host
		observe_catchall_hosts
	}
}
```

Você pode adicionar a opção `otlp` para enviar as mesmas métricas a um endpoint OpenTelemetry Protocol (OTLP). O exporter é configurado por variáveis de ambiente padrão `OTEL_*`, como `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_METRIC_EXPORT_INTERVAL` e `OTEL_METRICS_EXPORTER`.

```caddy
{
	metrics {
		otlp
	}
}
```

Por exemplo:

```console
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318 \
	OTEL_METRICS_EXPORTER=otlp \
	caddy run
```

Veja [Monitorando o Caddy com métricas](/docs/metrics) para mais detalhes.

##### `trace`
Registra cada handler individual que é invocado. Requer que o logger emita em nível `DEBUG` (você pode fazer isso com a [opção global `debug`](#debug)).

OBSERVAÇÃO: Isso pode registrar a configuração dos seus módulos de HTTP handler; não habilite isso em contextos inseguros quando houver dados sensíveis na configuração.

⚠️ Este é um recurso experimental. Sujeito a mudanças ou remoção.

```caddy
{
	servers {
		trace
	}
}
```


##### `max_header_size`

O tamanho máximo a ser lido dos cabeçalhos de requisição HTTP de um cliente. Se o limite for excedido, o servidor responderá com o status HTTP `431 Request Header Fields Too Large`. Aceita todos os formatos suportados por [go-humanize](https://github.com/dustin/go-humanize/blob/master/bytes.go). Por padrão, o limite é `1MB`.

```caddy
{
	servers {
		max_header_size 5MB
	}
}
```


##### `enable_full_duplex`

Habilita comunicação full-duplex para requisições HTTP/1.

Para requisições HTTP/1, o servidor HTTP do Go, por padrão, consome qualquer parte não lida do corpo da requisição antes de começar a escrever a resposta, impedindo que handlers leiam da requisição e escrevam a resposta simultaneamente. Habilitar essa opção desativa esse comportamento e permite que handlers continuem lendo da requisição enquanto escrevem a resposta ao mesmo tempo.

Para requisições HTTP/2+, o servidor HTTP do Go sempre permite leituras e respostas concorrentes, então essa opção não tem efeito.

Teste cuidadosamente com seus clientes HTTP, pois alguns clientes antigos podem não suportar full-duplex HTTP/1, o que pode causar deadlock. Veja [golang/go#57786](https://github.com/golang/go/issues/57786) para mais informações.

⚠️ Este é um recurso experimental. Sujeito a mudanças ou remoção.

```caddy
{
	servers {
		enable_full_duplex
	}
}
```


##### `log_credentials`

Por padrão, access logs (habilitados com a [`diretiva log`](/docs/caddyfile/directives/log)) com cabeçalhos que contêm informações potencialmente sensíveis (`Cookie`, `Set-Cookie`, `Authorization` e `Proxy-Authorization`) serão registrados como `REDACTED`.

Se você não quiser que esses cabeçalhos sejam ocultados, pode habilitar a opção `log_credentials`.

```caddy
{
	servers {
		log_credentials
	}
}
```



##### `protocols`

A lista separada por espaços de protocolos HTTP suportados.

Padrão: `h1 h2 h3`

Valores aceitos:
- `h1` para HTTP/1.1
- `h2` para HTTP/2
- `h2c` para HTTP/2 sobre texto claro
- `h3` para HTTP/3

Atualmente, habilitar HTTP/2 (incluindo H2C) implica necessariamente habilitar HTTP/1.1, porque a biblioteca padrão do Go não nos permite desabilitar HTTP/1.1 quando usamos seu servidor HTTP. No entanto, HTTP/1.1 ou HTTP/3 podem ser habilitados independentemente.

Observe que H2C ("Cleartext HTTP/2" ou "H2 over TCP") e HTTP/3 não são implementados pela biblioteca padrão do Go, então alguma funcionalidade ou recursos podem ser limitados. Não recomendamos habilitar H2C a menos que seja absolutamente necessário para sua aplicação.

```caddy
{
	servers :80 {
		protocols h1 h2c
	}
}
```



##### `strict_sni_host`

Habilitar isso exige que o cabeçalho `Host` de uma requisição corresponda ao valor de `ServerName` enviado pelo ClientHello TLS do cliente, uma proteção necessária ao usar autenticação TLS de cliente. Se houver divergência, um response HTTP `421 Misdirected Request` será escrito para o cliente.

Essa opção será ativada automaticamente se [autenticação de cliente](/docs/caddyfile/directives/tls#client_auth) estiver configurada. Isso impede bypass de autenticação TLS de cliente (domain fronting), que poderia ser explorado ao enviar um valor de SNI desprotegido durante um handshake TLS e depois colocar um domínio protegido no cabeçalho Host após estabelecer a conexão. Esse comportamento é um padrão seguro, mas você pode desativá-lo explicitamente com `insecure_off`; por exemplo, no caso de executar um proxy em que domain fronting é desejado e o acesso não é restrito com base no hostname.

```caddy
{
	servers {
		strict_sni_host on
	}
}
```


<a id="file-systems"></a>
## Sistemas de arquivos

A opção global `filesystem` permite declarar um ou mais sistemas de arquivos que podem ser usados para E/S de arquivos.

Isso pode permitir conectar-se a um filesystem remoto executando na nuvem, ou a um banco de dados com interface de arquivo, ou até mesmo ler arquivos embutidos dentro do binário do Caddy.

Sistemas de arquivos são declarados com um nome para identificá-los. Isso significa que você pode conectar mais de um sistema de arquivos do mesmo tipo, se precisar.

Por padrão, o Caddy não tem nenhum módulo de sistema de arquivos, então você precisará compilar o Caddy com um plugin para o sistema de arquivos que quiser usar.

#### Exemplo

Usando um módulo de sistema de arquivos `custom` imaginário, você poderia declarar dois sistemas de arquivos:

```caddy
{
	filesystem foo custom {
		...
	}

	filesystem bar custom {
		...
	}
}

foo.example.com {
	fs foo
	file_server
}

foo.example.com {
	fs bar
	file_server
}
```


<a id="pki-options"></a>
## Opções de PKI

O app PKI (Public Key Infrastructure) é a base dos recursos [Local HTTPS](/docs/automatic-https#local-https) e [acme_server](/docs/caddyfile/directives/acme_server) do Caddy. O app define autoridades certificadoras (CAs) capazes de assinar certificados.

O ID padrão da CA é `local`. Se o ID for omitido ao configurar o `ca`, então `local` será assumido.

##### `name`
O nome visível ao usuário da autoridade certificadora.

Padrão: `Caddy Local Authority`

```caddy
{
	pki {
		ca local {
			name "My Local CA"
		}
	}
}
```

##### `root_cn`
O nome a colocar no campo CommonName do certificado raiz.

Padrão: `{pki.ca.name} - {time.now.year} ECC Root`

```caddy
{
	pki {
		ca local {
			root_cn "My Local CA - 2024 ECC Root"
		}
	}
}
```

##### `intermediate_cn`
O nome a colocar no campo CommonName dos certificados intermediários.

Padrão: `{pki.ca.name} - ECC Intermediate`

```caddy
{
	pki {
		ca local {
			intermediate_cn "My Local CA - ECC Intermediate"
		}
	}
}
```

##### `intermediate_lifetime`
A [duração](/docs/conventions#durations) pela qual certificados intermediários são válidos. Esse valor **deve** ser menor que a duração do certificado raiz (`3600d` ou 10 anos).

Padrão: `7d`. Não é _recomendado_ alterar isso, a menos que seja absolutamente necessário.

```caddy
{
	pki {
		ca local {
			intermediate_lifetime 30d
		}
	}
}
```

##### `maintenance_interval`
A [duração](/docs/conventions#durations) com que frequência verificar se certificados intermediários (e raiz, quando aplicável) precisam de renovação.

Padrão: `10m`. Não é _recomendado_ alterar isso, a menos que seja absolutamente necessário.

```caddy
{
	pki {
		ca local {
			maintenance_interval 30m
		}
	}
}
```

##### `renewal_window_ratio`
A proporção (entre 0 e 1) da duração do certificado que ainda deve restar antes de o Caddy tentar renovar certificados. Por exemplo, se um certificado tiver duração de 1 ano e essa proporção for `0.2` (o valor padrão), então o Caddy tentará renovar continuamente o certificado quando faltarem 73 dias ou menos para a expiração.

```caddy
{
	pki {
		ca local {
			renewal_window_ratio 0.1
		}
	}
}
```


##### `root`
Um par de chaves (certificado e chave privada) a ser usado como raiz da CA. Se não for especificado, um será gerado e gerenciado automaticamente.

- **format** é o formato no qual o certificado e a chave privada são fornecidos. Atualmente, apenas `pem_file` é suportado, que é o padrão, então esse campo é opcional.
- **cert** é o certificado. Deve ser o caminho para um arquivo PEM, quando usar o formato `pem_file`.
- **key** é a chave privada. Deve ser o caminho para um arquivo PEM, quando usar o formato `pem_file`.

##### `intermediate`
Um par de chaves (certificado e chave privada) a ser usado como intermediário da CA. Se não for especificado, um será gerado e gerenciado automaticamente.

- **format** é o formato no qual o certificado e a chave privada são fornecidos. Atualmente, apenas `pem_file` é suportado, que é o padrão, então esse campo é opcional.
- **cert** é o certificado. Deve ser o caminho para um arquivo PEM, quando usar o formato `pem_file`.
- **key** é a chave privada. Deve ser o caminho para um arquivo PEM, quando usar o formato `pem_file`.

```caddy
{
	pki {
		ca local {
			root {
				format pem_file
				cert /path/to/root.pem
				key /path/to/root.key
			}
			intermediate {
				format pem_file
				cert /path/to/intermediate.pem
				key /path/to/intermediate.key
			}
		}
	}
}
```


<a id="event-options"></a>
## Opções de eventos

Os módulos do Caddy emitem eventos quando coisas interessantes acontecem (ou estão prestes a acontecer).

Eventos normalmente incluem um payload de metadados. A melhor forma de aprender sobre eventos e seus payloads é pela documentação de cada módulo, mas você também pode ver os eventos e seus payloads de dados habilitando a [opção global `debug`](#debug) e lendo os logs.

##### `on`

Vincula um handler de evento ao evento nomeado. Especifique o nome do módulo do handler de evento, seguido da sua configuração.

Por exemplo, para executar um comando depois que um certificado for obtido (requer um [plugin de terceiros <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/mholt/caddy-events-exec)), com uma parte do payload do evento sendo passada para o script usando um placeholder:

```caddy
{
	events {
		on cert_obtained exec ./my-script.sh {event.data.certificate_path}
	}
}
```

### Events

Estes eventos padrão são emitidos pelo Caddy:

- [`tls` events <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddyserver/certmagic#events)
- [`reverse_proxy` events](/docs/caddyfile/directives/reverse_proxy#events)

Plugins também podem emitir eventos, então consulte a documentação deles para detalhes.
