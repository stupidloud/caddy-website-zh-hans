---
title: tls (Caddyfile directive)
---

<script>
ready(function() {
	// Vamos adicionar links a todas as subdiretivas se houver uma tag de âncora correspondente na página.
	addLinksToSubdirectives();
});
</script>

# tls

Configura o TLS para o site.

**As configurações padrão de TLS do Caddy são seguras. Só altere essas definições se você tiver um bom motivo e entender as implicações.** O uso mais comum desta diretiva é especificar um endereço de e-mail da conta ACME, alterar o endpoint da ACME CA ou fornecer seus próprios certificados.

Observação de compatibilidade: devido à sua natureza sensível como protocolo de segurança, ajustes deliberados nos padrões de TLS podem ser feitos em novas versões menores ou de correção. Versões antigas ou quebradas de TLS, cifras, recursos etc. podem ser removidas a qualquer momento. Se sua implantação for extremamente sensível a mudanças, especifique explicitamente os valores que precisam permanecer constantes e fique atento às atualizações. Em quase todos os casos, recomendamos usar as configurações padrão.


<a id="syntax"></a>
## Sintaxe

```caddy-d
tls [internal|force_automate|<email>] | [<cert_file> <key_file>] {
	protocols <min> [<max>]
	ciphers   <cipher_suites...>
	curves    <groups...>
	alpn      <values...>
	load      <paths...>
	ca        <ca_dir_url>
	ca_root   <pem_file>
	key_type  ed25519|p256|p384|rsa2048|rsa4096
	dns       <provider_name> [<params...>]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	eab       <key_id> <mac_key>
	on_demand
	reuse_private_keys
	client_auth {
		mode                   [request|require|verify_if_given|require_and_verify]
		trust_pool             <module>
		verifier  			   <module>
	}
	issuer          <issuer_name>  [<params...>]
	get_certificate <manager_name> [<params...>]
	insecure_secrets_log <log_file>
	renewal_window_ratio <ratio>
	force_automate
}
```

- **internal** significa usar a CA interna e localmente confiável do Caddy para produzir certificados para este site. Para configurar ainda mais o emissor [`internal`](#internal), use a subdiretiva [`issuer`](#issuer).

- **force_automate** força o Caddy a automatizar certificados para o site, mesmo que outros certificados gerenciados se apliquem.

- **&lt;email&gt;** é o endereço de e-mail usado na conta ACME que gerencia os certificados do site. Você pode preferir usar a [opção global `email`](/docs/caddyfile/options#email) em vez disso, para configurar isso para todos os seus sites de uma vez.

<aside class="tip">

Lembre-se de que o Let's Encrypt pode enviar e-mails avisando que seu certificado está perto de expirar, mas isso pode ser enganoso porque o Caddy pode ter escolhido usar um emissor diferente (por exemplo, ZeroSSL) ao renovar. Verifique seus logs e/ou o certificado em si (por exemplo, no seu navegador) para ver qual emissor foi usado e se a validade ainda está correta; se estiver, você pode ignorar com segurança o e-mail do Let's Encrypt.

</aside>

- **&lt;cert_file&gt;** e **&lt;key_file&gt;** são os caminhos para os arquivos PEM do certificado e da chave privada. Especificar apenas um deles é inválido.

- **protocols** <span id="protocols"/> especifica as versões mínima e máxima do protocolo. NÃO altere isso a menos que saiba o que está fazendo. Configurar isso raramente é necessário, porque o Caddy sempre usará padrões modernos.
  
  Mínimo padrão: `tls1.2`, Máximo padrão: `tls1.3`

- **ciphers** <span id="ciphers"/> especifica a lista de nomes de suites de cifra em ordem decrescente de preferência. NÃO altere isso a menos que saiba o que está fazendo. Observe que suites de cifra não são personalizáveis para TLS 1.3; e nem todas as cifras TLS 1.2 estão habilitadas por padrão. Os nomes suportados são (em ordem de preferência da stdlib do Go):
	- `TLS_AES_128_GCM_SHA256`
	- `TLS_CHACHA20_POLY1305_SHA256`
	- `TLS_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`
	- `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256`
	- `TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA`
	- `TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA`
	- `TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA`

- **curves** <span id="curves"/> especifica a lista de grupos EC a suportar. Recomenda-se não alterar os padrões. Os valores suportados são:
	- `x25519mlkem768` (PQC)
	- `x25519`
	- `secp256r1`
	- `secp384r1`
	- `secp521r1`

- **alpn** <span id="alpn"/> é a lista de valores a anunciar na [extensão ALPN <img src="/old/resources/images/external-link.svg" class="external-link">](https://developer.mozilla.org/en-US/docs/Glossary/ALPN) do handshake TLS.

- **load** <span id="load"/> especifica uma lista de pastas das quais carregar arquivos PEM que sejam pacotes de certificado + chave.

- **ca** <span id="ca"/> altera o endpoint da CA ACME. Isso é mais usado para definir o [endpoint de staging do Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) durante testes, ou um servidor ACME interno. (Para alterar esse valor para todo o Caddyfile, use a opção global `acme_ca` [global option](/docs/caddyfile/options) em vez disso.)

- **ca_root** <span id="ca_root"/> especifica um arquivo PEM que contém um certificado raiz confiável para o endpoint da CA ACME, caso ele não esteja na trust store do sistema.

- **key_type** <span id="key_type"/> é o tipo de chave a usar ao gerar CSRs. Só defina isso se houver uma necessidade específica.

- **dns** <span id="dns"/> habilita o [desafio DNS](/docs/automatic-https#dns-challenge) usando o plugin de provedor especificado, que precisa ser incluído a partir de um dos repositórios [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Cada plugin de provedor pode ter sua própria sintaxe após o nome; consulte a documentação dele para detalhes. Manter suporte para cada provedor DNS é um esforço da comunidade. [Saiba como habilitar o desafio DNS para seu provedor em nossa wiki.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)

- **propagation_timeout** <span id="propagation_timeout"/> é um [valor de duração](/docs/conventions#durations) que define o tempo máximo de espera para que os registros TXT de DNS apareçam ao usar o desafio DNS. Defina como `-1` para desabilitar as verificações de propagação. Padrão: 2 minutos.

- **propagation_delay** <span id="propagation_delay"/> é um [valor de duração](/docs/conventions#durations) que define quanto tempo esperar antes de iniciar as verificações de propagação dos registros TXT de DNS ao usar o desafio DNS. Padrão `0` (sem espera).

- **dns_ttl** <span id="dns_ttl"/> é um [valor de duração](/docs/conventions#durations) que define o TTL do registro `TXT` usado para o desafio DNS. Raramente necessário.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> substitui o domínio usado para o desafio DNS. Isso serve para delegar o desafio a outro domínio.

  Você pode querer usar isso se o provedor DNS do seu domínio principal não tiver um [plugin DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) disponível. Em vez disso, você pode adicionar um registro `CNAME` com o subdomínio `_acme-challenge` ao seu domínio principal, apontando para um domínio secundário para o qual você _tenha_ um plugin. Esta opção _não_ requer suporte especial do plugin.
  
  Quando os emissores ACME tentarem resolver o desafio DNS para o seu domínio principal, eles seguirão então o `CNAME` até o domínio secundário para encontrar o registro `TXT`.

  **Observação:** use aqui o nome canônico completo do registro CNAME como valor - o subdomínio `_acme-challenge` não será prefixado automaticamente.

- **resolvers** <span id="resolvers"/> personaliza os resolvedores DNS usados ao executar o desafio DNS; eles têm precedência sobre resolvedores do sistema ou quaisquer padrões. Se definidos aqui, os resolvedores serão propagados para todos os emissores de certificados configurados.

  Normalmente, isso é uma lista de endereços IP. Por exemplo, para usar o [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns):

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **eab** <span id="eab"/> configura o binding de conta externa (EAB) do ACME para este site, usando o ID de chave e a chave MAC fornecidos pela sua CA.

- **on_demand** <span id="on_demand"/> habilita [TLS sob demanda](/docs/automatic-https#on-demand-tls) para os nomes de host fornecidos nos endereços do bloco de site. **Aviso de segurança:** fazer isso em produção é inseguro a menos que você também configure a [opção global `on_demand_tls`](/docs/caddyfile/options#on-demand-tls) para mitigar abuso.

- **reuse_private_keys** <span id="reuse_private_keys"/> habilita reutilização de chaves privadas ao renovar certificados. Por padrão, uma nova chave é criada para cada novo certificado para mitigar pinning e reduzir o impacto de uma eventual comprometimento da chave. Key pinning contraria as melhores práticas da indústria. Esta opção não é recomendada, a menos que você tenha um motivo específico para usá-la; isso pode ser removido em uma versão futura.

- **client_auth** <span id="client_auth"/> habilita e configura autenticação de cliente TLS:
  - **mode** <span id="mode"/> é o modo para autenticar o cliente. Os valores permitidos são:

    | Modo | Descrição |
    | --- | --- |
    | request | Solicita um certificado dos clientes, mas permite a conexão mesmo sem um; não o verifica |
    | require | Exige que os clientes apresentem um certificado, mas não o verifica |
    | verify_if_given | Solicita um certificado dos clientes; permite a conexão mesmo sem um, mas o verifica se houver |
    | require_and_verify | Exige que os clientes apresentem um certificado válido e verificado |

    Padrão: `require_and_verify` se o módulo `trust_pool` for fornecido; caso contrário, `require`.
	
  - **trust_pool** <span id="trust_pool"/> configura a origem das autoridades certificadoras (CA) que fornecem certificados contra os quais os certificados de cliente serão validados.
	
	A autoridade certificadora usada para fornecer o conjunto de certificados confiáveis e a configuração dentro do segmento dependem da origem configurada pelo módulo trust pool. Os módulos padrão disponíveis no Caddy estão [listados abaixo](#trust-pool-providers). A lista completa de módulos, incluindo os de terceiros, está na [documentação JSON de `trust_pool`](/docs/json/apps/http/servers/tls_connection_policies/client_authentication/#trust_pool).

    Várias diretivas `trusted_*` podem ser usadas para especificar múltiplos certificados de CA ou leaf. Certificados de cliente que não estejam listados como um dos certificados leaf ou assinados por qualquer uma das CAs especificadas serão rejeitados de acordo com o **mode**.

  - **verifier** <span id="verifier"/> habilita o uso de um módulo verificador personalizado de certificado de cliente. Esses verificadores podem executar checagens personalizadas de autenticação, como garantir que o certificado não foi revogado.

- **issuer** <span id="issuer"/> configura um emissor de certificados personalizado, ou uma fonte da qual obter certificados.

  Qual emissor é usado e as opções que se seguem neste segmento dependem dos [módulos de emissor](#issuers) disponíveis. Algumas das outras subdiretivas, como `ca` e `dns`, são na verdade atalhos para configurar o emissor `acme` (e esta subdiretiva foi adicionada depois), então especificar esta diretiva junto de algumas outras é confuso e, portanto, proibido.
  
  Esta subdiretiva pode ser especificada várias vezes para configurar vários emissores redundantes; se um falhar ao emitir um certificado, o próximo será tentado.

- **get_certificate** <span id="get_certificate"/> habilita a obtenção de certificados a partir de um [módulo gerenciador](#certificate-managers) no momento do handshake.

- **insecure_secrets_log** <span id="insecure_secrets_log"/> habilita o registro dos segredos TLS em um arquivo. Isso também é conhecido como `SSLKEYLOGFILE`. Usa o formato NSS key log, que pode então ser analisado pelo Wireshark ou outras ferramentas. ⚠️ **Aviso de segurança:** isso é inseguro porque permite que outros programas ou ferramentas decifrem conexões TLS e, portanto, compromete completamente a segurança. Porém, essa capacidade pode ser útil para depuração e troubleshooting.

- **renewal_window_ratio** <span id="renewal_window_ratio"/> é uma proporção entre 0 e 1 que determina quanto da vida útil do certificado ainda deve restar antes de o Caddy tentar renová-lo. Por exemplo, se um certificado tiver vida útil de 90 dias e essa proporção for `0.3333` (o valor padrão), então o Caddy continuará tentando renovar o certificado quando restarem 30 dias ou menos até a expiração. Também pode ser definido globalmente com a [opção global `renewal_window_ratio`](/docs/caddyfile/options#renewal_window_ratio).

  Você raramente precisará alterar isso, mas pode ser útil renovar mais tarde na vida útil do certificado se sua CA tiver um tempo de emissão muito longo.

  Tenha em mente que isso é uma sugestão, já que emissores ACME podem implementar a [extensão ARI](https://datatracker.ietf.org/doc/rfc9773/). A ARI dita uma janela dentro da qual o cliente ACME (o Caddy, neste caso) deve tentar a renovação, e essa janela pode não se alinhar com essa proporção.

- **force_automate** é o mesmo que especificar inline (veja acima).

<a id="trust-pool-providers"></a>
### Provedores de trust pool

Estes são os provedores padrão de trust pool que podem ser usados na subdiretiva `trust_pool`:

<a id="inline"></a>
#### inline

O módulo `inline` interpreta os certificados raiz confiáveis diretamente listados no Caddyfile em formato base64 DER. A diretiva `trust_der` pode ser repetida várias vezes.

```caddy-d
trust_pool inline {
	trust_der      <base64_der>
}
```

- **trust_der** <span id="trust_der"/> é um certificado CA codificado em base64 DER, contra o qual os certificados de cliente serão validados.

<a id="file"></a>
#### file

O módulo `file` lê os certificados raiz confiáveis a partir de arquivos PEM no disco. A diretiva `pem_file` pode aceitar vários caminhos de arquivo na mesma linha e pode ser repetida várias vezes.

```caddy-d
... file [<pem_file>...] {
	pem_file <pem_file>...
}
```

- **pem_file** <span id="pem_file"/> é o caminho de um arquivo PEM de certificado CA, contra o qual os certificados de cliente serão validados.

<a id="pki_root"></a>
#### pki_root

O módulo `pki_root` obtém a _raiz_ e confia nos certificados da autoridade certificadora definida no [app PKI](/docs/caddyfile/options#pki-options). A diretiva `authority` pode aceitar várias autoridades ao mesmo tempo e pode ser repetida várias vezes.

```caddy-d
... pki_root [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> é o nome da autoridade certificadora configurada no app PKI.

<a id="pki_intermediate"></a>
#### pki_intermediate

O módulo `pki_intermediate` obtém o _intermediário_ e confia nos certificados da autoridade certificadora definida no [app PKI](/docs/caddyfile/options#pki-options). A diretiva `authority` pode aceitar várias autoridades ao mesmo tempo e pode ser repetida várias vezes.

```caddy-d
... pki_intermediate [<ca_name>...] {
	authority <ca_name>...
}
```

- **authority** <span id="authority"/> é o nome da autoridade certificadora configurada no app PKI.

<a id="storage"></a>
#### storage

O módulo `storage` extrai a raiz dos certificados confiáveis do [storage](/docs/caddyfile/options#storage) do Caddy. A diretiva `authority` pode aceitar várias autoridades ao mesmo tempo e pode ser repetida várias vezes.

```caddy-d
... storage [<storage_keys>...] {
	storage <storage_module>
	keys    <storage_keys>...
}
```

- **storage** <span id="storage"/> é um módulo de armazenamento opcional a ser usado. Se não for especificado, será usado o módulo de armazenamento padrão. Se for especificado, só poderá ser usado uma vez.

- **keys** <span id="keys"/> é a lista de chaves de armazenamento nas quais os arquivos PEM dos certificados estão guardados. A diretiva aceita vários valores na mesma linha e pode ser especificada várias vezes.

<a id="http"></a>
#### http

O módulo `http` obtém os certificados confiáveis a partir de endpoints HTTP. A diretiva `endpoints` pode aceitar vários endpoints ao mesmo tempo e pode ser repetida várias vezes.

```caddy-d
... http [<endpoints...>] {
	endpoints   <endpoints...>
	tls         <tls_config>
}
```

- **endpoints** <span id="endpoints"/> é a lista de endpoints HTTP dos quais obter certificados. A diretiva aceita vários valores na mesma linha e pode ser especificada várias vezes.

- **tls** <span id="tls"/> é uma configuração TLS opcional a ser usada ao conectar ao endpoint HTTP. A análise do segmento é definida na [seção a seguir](#tls-1).

<a id="tls-1"></a>
##### TLS

```caddy-d
... {
	ca                    <ca_module>
	enable_system_roots
	insecure_skip_verify
	handshake_timeout     <duration>
	server_name           <name>
	renegotiation         <never|once|freely>
}
```

- **ca** <span id="ca"/> é uma diretiva opcional para definir o provedor do trust pool. A configuração segue o mesmo comportamento de [`trust_pool`](#trust_pool). Se for especificado, só poderá ser usado uma vez.

- **insecure_skip_verify** <span id="insecure_skip_verify"/> desativa a verificação do handshake TLS, tornando a conexão insegura e vulnerável a ataques man-in-the-middle. _Não use em produção._ A verificação é feita contra as autoridades certificadoras confiadas pelo sistema ou conforme determinado pela diretiva [`ca`](#ca).

- **handshake_timeout** <span id="handshake_timeout"/> é a duração máxima de espera para a conclusão do handshake TLS. Padrão: sem timeout.

- **server_name** <span id="server_name"/> define o nome do servidor usado ao verificar o certificado recebido no handshake TLS. Por padrão, isso usará a parte de host do endereço upstream.

- **renegotiation** <span id="renegotiation"/> define o nível de renegociação TLS. A renegociação TLS é a realização de handshakes subsequentes após o primeiro. O nível pode ser um destes:
  - `never` (o padrão) desativa a renegociação.
  - `once` permite que um servidor remoto solicite renegociação uma vez por conexão.
  - `freely` permite que um servidor remoto solicite renegociação repetidamente.

<a id="verifiers"></a>
### Verificadores

Os módulos verificadores de certificado de cliente são executados depois de validar que eles foram emitidos por uma autoridade certificadora confiável, se `trust_pool` estiver configurado. O único verificador atualmente incluído no Caddy padrão é `leaf`.

<a id="leaf"></a>
#### Leaf

O verificador `leaf` verifica se o certificado de cliente está entre um conjunto definido de certificados permitidos. O conjunto de certificados é carregado usando módulos [loader](https://caddyserver.com/docs/modules/tls.client_auth.verifier.leaf#leaf_certs_loaders).

<a id="loaders"></a>
##### Carregadores

A distribuição padrão do Caddy inclui 4 carregadores, sendo 3 deles disponíveis no Caddyfile.

<a id="file-loader"></a>
###### File

O carregador `file` carrega o conjunto de certificados a partir de arquivos PEM especificados.

```caddy-d
... file <pem_files...>
```

<a id="folder"></a>
###### Folder

O carregador `folder` percorre recursivamente os diretórios nomeados, procurando arquivos PEM a serem carregados como certificados de cliente aceitos.

```caddy-d
... folder <folders...>
```

<a id="pem"></a>
###### PEM

O carregador `pem` aceita certificados embutidos no Caddyfile em formato PEM.

```caddy-d
... pem <pem_strings...>
```

<a id="issuers"></a>
### Emissores

Estes emissores vêm incluídos por padrão com a diretiva `tls`:

<a id="acme"></a>
#### acme

Obtém certificados usando o protocolo ACME. Observe que `acme` é um emissor padrão (usando o Let's Encrypt), então configurá-lo explicitamente normalmente é desnecessário.

```caddy-d
... acme [<directory_url>] {
	dir      <directory_url>
	test_dir <test_directory_url>
	email    <email>
	timeout  <duration>
	disable_http_challenge
	disable_tlsalpn_challenge
	alt_http_port    <port>
	alt_tlsalpn_port <port>
	eab <key_id> <mac_key>
	trusted_roots <pem_files...>
	dns [<provider_name> [<options>]]
	propagation_timeout <duration>
	propagation_delay   <duration>
	dns_ttl             <duration>
	dns_challenge_override_domain <domain>
	resolvers <dns_servers...>
	preferred_chains [smallest] {
		root_common_name <common_names...>
		any_common_name  <common_names...>
	}
	profile <name>
}
```

- **dir** <span id="dir"/> é a URL do diretório da ACME CA.
  
  Padrão: `https://acme-v02.api.letsencrypt.org/directory`

- **test_dir** <span id="test_dir"/> é um diretório de fallback opcional a ser usado ao repetir tentativas de desafios; se todos os desafios falharem, este endpoint será usado durante as tentativas; útil se uma CA tiver um endpoint de staging no qual você queira evitar limites de taxa no endpoint de produção.

  Padrão: `https://acme-staging-v02.api.letsencrypt.org/directory`

- **email** <span id="email"/> é o endereço de e-mail de contato da conta ACME.

- **timeout** <span id="timeout"/> é um [valor de duração](/docs/conventions#durations) que define por quanto tempo esperar antes de expirar uma operação ACME.

- **disable_http_challenge** <span id="disable_http_challenge"/> desabilita o desafio HTTP.

- **disable_tlsalpn_challenge** <span id="disable_tlsalpn_challenge"/> desabilita o desafio TLS-ALPN.

- **alt_http_port** <span id="alt_http_port"/> é uma porta alternativa na qual servir o desafio HTTP; ele precisa acontecer na porta 80, então você deve encaminhar pacotes para essa porta alternativa.

- **alt_tlsalpn_port** <span id="alt_tlsalpn_port"/> é uma porta alternativa na qual servir o desafio TLS-ALPN; ele precisa acontecer na porta 443, então você deve encaminhar pacotes para essa porta alternativa.

- **eab** <span id="eab"/> especifica um External Account Binding que pode ser exigido por algumas CAs ACME.

- **trusted_roots** <span id="trusted_roots"/> é um ou mais certificados raiz (como arquivos PEM) em que confiar ao conectar ao servidor ACME da CA.

- **dns** <span id="dns"/> configura o desafio DNS. Um provedor precisa ser configurado aqui, a menos que a [opção global `dns`](/docs/caddyfile/options#dns) especifique um módulo de provedor DNS aplicável globalmente.

- **propagation_timeout** <span id="propagation_timeout"/> é um [valor de duração](/docs/conventions#durations) que define o tempo máximo de espera para que os registros TXT de DNS apareçam ao usar o desafio DNS. Defina como `-1` para desabilitar as verificações de propagação. Padrão: 2 minutos.

- **propagation_delay** <span id="propagation_delay"/> é um [valor de duração](/docs/conventions#durations) que define quanto tempo esperar antes de iniciar as verificações de propagação dos registros TXT de DNS ao usar o desafio DNS. Padrão 0 (sem espera).

- **dns_ttl** <span id="dns_ttl"/> é um [valor de duração](/docs/conventions#durations) que define o TTL do registro `TXT` usado para o desafio DNS. Raramente necessário.

- **dns_challenge_override_domain** <span id="dns_challenge_override_domain"/> substitui o domínio usado para o desafio DNS. Isso serve para delegar o desafio a outro domínio.

  Você pode querer usar isso se o provedor DNS do seu domínio principal não tiver um [plugin DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns) disponível. Em vez disso, você pode adicionar um registro `CNAME` com o subdomínio `_acme-challenge` ao seu domínio principal, apontando para um domínio secundário para o qual você _tenha_ um plugin. Esta opção _não_ requer suporte especial do plugin.
  
  Quando emissores ACME tentarem resolver o desafio DNS para o seu domínio principal, eles seguirão então o `CNAME` até o domínio secundário para encontrar o registro `TXT`.

  **Observação:** use aqui o nome canônico completo do registro CNAME como valor - o subdomínio `_acme-challenge` não será prefixado automaticamente.

- **resolvers** <span id="resolvers"/> personaliza os resolvedores DNS usados ao executar o desafio DNS; eles têm precedência sobre resolvedores do sistema ou quaisquer padrões. Se definidos aqui, os resolvedores serão propagados para todos os emissores de certificados configurados.

  Normalmente, isso é uma lista de endereços IP. Por exemplo, para usar o [Google Public DNS <img src="/old/resources/images/external-link.svg" class="external-link">](https://developers.google.com/speed/public-dns):

  ```caddy-d
  resolvers 8.8.8.8 8.8.4.4
  ```

- **preferred_chains** <span id="preferred_chains"/> especifica quais cadeias de certificados o Caddy deve preferir; útil se sua CA fornecer várias cadeias. Use uma das opções a seguir:
	- **smallest** <span id="smallest"/> fará o Caddy preferir cadeias com a menor quantidade de bytes.

	- **root_common_name** <span id="root_common_name"/> é uma lista de um ou mais nomes comuns; o Caddy escolherá a primeira cadeia que tiver uma raiz que corresponda a pelo menos um dos nomes comuns especificados.

	- **any_common_name** <span id="any_common_name"/> é uma lista de um ou mais nomes comuns; o Caddy escolherá a primeira cadeia que tiver um emissor que corresponda a pelo menos um dos nomes comuns especificados.

- **profile** é o nome do [perfil ACME](https://datatracker.ietf.org/doc/draft-aaron-acme-profiles/) a ser aplicado ao solicitar certificados. Se você especificar um, todas as CAs configuradas (implícita ou explicitamente) precisam suportar esse perfil. Consulte a documentação da sua CA para perfis disponíveis; algumas CAs talvez não deem suporte a perfis. EXPERIMENTAL: a especificação de perfil ACME ainda está em rascunho, então este recurso/função está sujeito a mudanças ou remoção.


<a id="zerossl"></a>
#### zerossl

Obtém certificados usando a [API proprietária de emissão de certificados da ZeroSSL](https://zerossl.com/documentation/api/). Uma chave de API é necessária e o pagamento também pode ser exigido dependendo do seu plano. Observe que isso é diferente do [endpoint ACME da ZeroSSL](https://zerossl.com/documentation/acme/). Para usar o endpoint ACME da ZeroSSL, use o emissor `acme` descrito acima, configurado com o endpoint de diretório ACME da ZeroSSL.

```caddy-d
... zerossl <api_key> {
	validity_days <days>
	alt_http_port <port>
	dns <provider_name> ...
	propagation_delay <duration>
	propagation_timeout <duration>
	resolvers <list...>
	dns_ttl <duration>
}
```

- **validity_days** <span id="validity_days"/> define a vida útil do certificado. Apenas certos valores são aceitos; consulte a [documentação da ZeroSSL](https://zerossl.com/documentation/api/create-certificate/) para detalhes.
<!--   
  Default: `https://acme-v02.api.letsencrypt.org/directory`
 -->
- **alt_http_port** <span id="zerossl_alt_http_port"/> é a porta a ser usada para concluir a validação HTTP da ZeroSSL, se não for a porta 80.
- **dns** <span id="zerossl_dns"/> habilita o método de validação CNAME usando o provedor DNS nomeado com a configuração dada para provisionamento automático de registros. O plugin do provedor DNS deve ser instalado a partir dos repositórios [`caddy-dns` <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/caddy-dns). Cada plugin de provedor pode ter sua própria sintaxe após o nome; consulte a documentação dele para detalhes. Manter suporte para cada provedor DNS é um esforço da comunidade.
- **propagation_delay** <span id="zerossl_propagation_delay"/> é quanto tempo esperar antes de verificar a propagação do registro CNAME.
- **propagation_timeout** <span id="zerossl_propagation_timeout"/> é quanto tempo esperar pela propagação do registro CNAME antes de desistir.
- **resolvers** <span id="zerossl_resolvers"/> define resolvedores DNS personalizados a usar ao verificar a propagação do registro CNAME.
- **dns_ttl** <span id="zerossl_dns_ttl"/> configura o TTL para registros CNAME criados como parte do processo de validação.



<a id="internal"></a>
#### internal

Obtém certificados de uma autoridade certificadora interna.

```caddy-d
... internal {
	ca       <name>
	lifetime <duration>
	sign_with_root
}
```

- **ca** <span id="ca"/> é o nome da CA interna a usar. Padrão: `local`. Veja as [opções globais do app PKI](/docs/caddyfile/options#pki-options) para configurar a CA `local`, ou para criar CAs alternativas.

  Por padrão, o certificado raiz da CA tem validade de `3600d` (10 anos) e o intermediário tem validade de `7d` (7 dias).

  O Caddy tentará instalar o certificado raiz da CA na trust store do sistema, mas isso pode falhar quando o Caddy estiver sendo executado como um usuário sem privilégios, ou dentro de um container Docker. Nesse caso, o certificado raiz precisará ser instalado manualmente, seja usando o comando [`caddy trust`](/docs/command-line#caddy-trust), seja [copiando-o para fora do container](/docs/running#usage).

- **lifetime** <span id="lifetime"/> é um [valor de duração](/docs/conventions#durations) que define o período de validade para certificados leaf emitidos internamente. Padrão: `12h`. NÃO é recomendado alterar isso, a menos que seja absolutamente necessário. Ele deve ser menor que a vida útil do intermediário.

- **sign_with_root** <span id="sign_with_root"/> força a raiz a ser o emissor em vez do intermediário. Isso NÃO é recomendado e só deve ser usado quando dispositivos/clients não validam corretamente cadeias de certificados (muito incomum).


<a id="certificate-managers"></a>
### Gerenciadores de certificados

Os módulos de gerenciador de certificados diferem dos módulos de emissor porque o uso dos módulos de gerenciador implica que uma ferramenta ou serviço externo está mantendo o certificado renovado, enquanto um módulo de emissor implica que o próprio Caddy está gerenciando o certificado. (Os módulos de emissor recebem uma Certificate Signing Request (CSR) como entrada, mas os módulos de gerenciador recebem um TLS ClientHello como entrada.)

Estes módulos de gerenciador vêm incluídos por padrão com a diretiva `tls`:

<a id="tailscale"></a>
#### tailscale

Obtém certificados de uma instância [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com) em execução local. [HTTPS deve estar habilitado na sua conta Tailscale](https://tailscale.com/kb/1153/enabling-https/) (ou no seu servidor de código aberto [Headscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://github.com/juanfont/headscale)); e o processo do Caddy deve estar sendo executado como root, ou você deve configurar o `tailscaled` para dar ao usuário do Caddy [permissão para buscar certificados](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348).

_**OBSERVAÇÃO: isso normalmente é desnecessário!** O Caddy usa automaticamente o Tailscale para todos os domínios `*.ts.net` sem nenhuma configuração extra._

```caddy-d
get_certificate tailscale  # geralmente desnecessário!
```


<a id="http-1"></a>
#### http

Obtém certificados fazendo uma requisição HTTP(S). A resposta deve ter um status `200` e o corpo deve conter uma cadeia PEM incluindo o certificado completo (com intermediários) e a chave privada.

```caddy-d
get_certificate http <url>
```

- **url** <span id="url"/> é a URL totalmente qualificada para a qual a requisição será feita. Recomenda-se fortemente que isso seja um endpoint local por motivos de desempenho. A URL será augmentada com os seguintes parâmetros de query string:

  - `server_name`: valor SNI
  - `signature_schemes`: lista separada por vírgulas de IDs hexadecimais de algoritmos de assinatura
  - `cipher_suites`: lista separada por vírgulas de IDs hexadecimais de suites de cifra
  - `local_ip`: endereço IP para o qual o cliente fez a requisição


<a id="examples"></a>
## Exemplos

Use um certificado e uma chave personalizados. O certificado deve ter [SANs](https://en.wikipedia.org/wiki/Subject_Alternative_Name) que correspondam ao endereço do site:

```caddy
example.com {
	tls cert.pem key.pem
}
```

Use certificados [confiáveis localmente](/docs/automatic-https#local-https) para todos os hosts no bloco de site atual, em vez de certificados públicos via ACME / Let's Encrypt (útil em ambientes de desenvolvimento):

```caddy
example.com {
	tls internal
}
```

Use certificados confiáveis localmente, mas gerenciados [sob demanda](/docs/automatic-https#on-demand-tls) em vez de em segundo plano. Isso permite apontar qualquer domínio para sua instância do Caddy e ter um certificado provisionado automaticamente. Isso NÃO DEVE ser usado se sua instância do Caddy estiver acessível publicamente, pois um atacante poderia usá-la para esgotar os recursos do seu servidor:

```caddy
https:// {
	tls internal {
		on_demand
	}
}
```

Use opções personalizadas para a CA interna (não pode usar o atalho `tls internal`):

```caddy
example.com {
	tls {
		issuer internal {
			ca foo
		}
	}
}
```

Especifique um endereço de e-mail para sua conta ACME (mas, se apenas um e-mail for usado para todos os sites, recomendamos usar a [opção global `email`](/docs/caddyfile/options) em vez disso):

```caddy
example.com {
	tls your@email.com
}
```

Habilite o desafio DNS para um domínio gerenciado no Cloudflare com credenciais de conta em uma variável de ambiente. Isso desbloqueia suporte a certificados curinga, que exige validação DNS:

```caddy
*.example.com {
	tls {
		dns cloudflare {env.CLOUDFLARE_API_TOKEN}
	}
}
```

Obtenha a cadeia do certificado via HTTP, em vez de o Caddy gerenciá-la. Observe que [`get_certificate`](#certificate-managers) implica que [`on_demand`](#on_demand) esteja habilitado, buscando certificados com um módulo em vez de disparar a emissão ACME:

```caddy
https:// {
	tls {
		get_certificate http http://localhost:9007/certs
	}
}
```

Habilite a autenticação de cliente TLS e exija que os clientes apresentem um certificado válido verificado contra todas as CAs fornecidas via o provedor `file` da [`trust_pool`](#trust_pool):

```caddy
example.com {
	tls {
		client_auth {
			trust_pool file ../caddy.ca.cer ../root.ca.cer
		}
	}
}
```
