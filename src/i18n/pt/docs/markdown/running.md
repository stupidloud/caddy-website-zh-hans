---
title: "Manter o Caddy em execução"
---

# Manter o Caddy em execução

Embora o Caddy possa ser executado diretamente com sua [interface de linha de comando](/docs/command-line), há várias vantagens em usar um gerenciador de serviços para mantê-lo em execução, como garantir que ele inicie automaticamente quando o sistema reiniciar e capturar logs de stdout/stderr.

- [Serviço Linux](#linux-service)
  - [Arquivos de unidade](#unit-files)
  - [Instalação manual](#manual-installation)
  - [Usando o serviço](#using-the-service)
  - [HTTPS local](#local-https-with-systemd)
  - [Overrides](#overrides)
	- [Variáveis de ambiente](#environment-variables)
	- [Override de `run` e `reload`](#run-and-reload-override)
	- [Reiniciar em caso de falha](#restart-on-crash)
  - [Considerações sobre SELinux](#selinux-considerations)
- [Serviço Windows](#windows-service)
  - [sc.exe](#scexe)
  - [WinSW](#winsw)
- [Docker Compose](#docker-compose)
  - [Configuração](#setup)
  - [Uso](#usage)
  - [HTTPS local](#local-https-with-docker)

<a id="linux-service"></a>
## Serviço Linux

A forma recomendada de executar o Caddy em distribuições Linux com systemd é usar nossos arquivos oficiais de unidade systemd.

<a id="unit-files"></a>
### Arquivos de unidade

Fornecemos dois arquivos de unidade systemd diferentes para você escolher, dependendo do seu caso de uso:

- [**`caddy.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy.service) se você configurar o Caddy com um [Caddyfile](/docs/caddyfile). Se preferir usar outro config adapter ou um arquivo de configuração JSON, você pode [sobrescrever](#overrides) os comandos `ExecStart` e `ExecReload`.

- [**`caddy-api.service`**](https://github.com/caddyserver/dist/blob/master/init/caddy-api.service) se você configurar o Caddy exclusivamente pela [API](/docs/api). Esse serviço usa a opção [`--resume`](/docs/command-line#caddy-run), que iniciará o Caddy usando o `autosave.json` que é [persistido](/docs/json/admin/config/) por padrão.

Eles são muito parecidos, mas diferem nos comandos `ExecStart` e `ExecReload` para acomodar os fluxos de trabalho.

Se você precisar alternar entre os serviços, deve desabilitar e parar o anterior antes de habilitar e iniciar o outro. Por exemplo, para mudar do serviço `caddy` para o serviço `caddy-api`:
<pre><code class="cmd"><span class="bash">sudo systemctl disable --now caddy</span>
<span class="bash">sudo systemctl enable --now caddy-api</span></code></pre>

<a id="manual-installation"></a>
### Instalação manual

Alguns [métodos de instalação](/docs/install) configuram automaticamente o Caddy para rodar como serviço. Se você escolheu um método que não faz isso, pode seguir estas instruções:

**Requisitos:**

- binário `caddy` que você [baixou](/download) ou [compilou a partir do código-fonte](/docs/build)
- `systemctl --version` 232 ou mais recente
- privilégios `sudo`

Mova o binário do caddy para o seu `$PATH`, por exemplo:
<pre><code class="cmd bash">sudo mv caddy /usr/bin/</code></pre>

Teste se funcionou:
<pre><code class="cmd bash">caddy version</code></pre>

Crie um grupo chamado `caddy`:
<pre><code class="cmd bash">sudo groupadd --system caddy</code></pre>

Crie um usuário chamado `caddy` com um diretório home gravável:
<pre><code class="cmd bash">sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy</code></pre>

Se estiver usando um arquivo de configuração, certifique-se de que ele seja legível pelo usuário `caddy` que você acabou de criar.

Em seguida, [escolha um arquivo de unidade systemd](#unit-files) com base no seu caso de uso.

**Confira duas vezes as diretivas `ExecStart` e `ExecReload`.** Verifique se a localização do binário e os argumentos da linha de comando estão corretos para a sua instalação! Por exemplo: se estiver usando um arquivo de configuração, altere o caminho em `--config` se ele for diferente do padrão.

O local usual para salvar o arquivo de serviço é: `/etc/systemd/system/caddy.service`

Depois de salvar o arquivo de serviço, você pode iniciar o serviço pela primeira vez com a sequência usual do systemctl:

<pre><code class="cmd"><span class="bash">sudo systemctl daemon-reload</span>
<span class="bash">sudo systemctl enable --now caddy</span></code></pre>

Verifique se ele está em execução:
<pre><code class="cmd bash">systemctl status caddy</code></pre>

Agora você está pronto para [usar o serviço](#using-the-service)!

<a id="using-the-service"></a>
### Usando o serviço

Se estiver usando um Caddyfile, você pode editar sua configuração com `nano`, `vi` ou seu editor preferido:
<pre><code class="cmd bash">sudo nano /etc/caddy/Caddyfile</code></pre>

Você pode colocar os arquivos do seu site estático em `/var/www/html` ou `/srv`. Certifique-se de que o usuário `caddy` tenha permissão para ler os arquivos.

Para verificar se o serviço está em execução:
<pre><code class="cmd bash">systemctl status caddy</code></pre>
O comando de status também mostrará a localização do arquivo de serviço atualmente em execução.

Ao rodar com nosso arquivo de serviço oficial, a saída do Caddy será redirecionada para o `journalctl`. Para ler seus logs completos e evitar que as linhas sejam truncadas:
<pre><code class="cmd bash">journalctl -u caddy --no-pager | less +G</code></pre>

Se estiver usando um arquivo de configuração, você pode recarregar o Caddy de forma graciosa após fazer qualquer alteração:
<pre><code class="cmd bash">sudo systemctl reload caddy</code></pre>

Você pode parar o serviço com:
<pre><code class="cmd bash">sudo systemctl stop caddy</code></pre>

<aside class="advice">

Não pare o serviço para mudar a configuração do Caddy. Parar o servidor causará downtime. Use o comando reload em vez disso.

</aside>

O processo Caddy será executado como o usuário `caddy`, cujo `$HOME` é definido como `/var/lib/caddy`. Isso significa que:
- O local padrão do [storage de dados](/docs/conventions#data-directory) (para certificados e outras informações de estado) ficará em `/var/lib/caddy/.local/share/caddy`.
- O local padrão do [storage de configuração](/docs/conventions#configuration-directory) (para o JSON auto-salvo, principalmente útil para o serviço `caddy-api`) ficará em `/var/lib/caddy/.config/caddy`.

<a id="local-https-with-systemd"></a>
### HTTPS local com systemd

Ao usar o Caddy para desenvolvimento local com HTTPS, você pode usar um [hostname](/docs/caddyfile/concepts#addresses) como `localhost` ou `app.localhost`. Isso habilita o [HTTPS local](/docs/automatic-https#local-https) usando a CA local do Caddy para emitir certificados.

Como o Caddy roda como usuário `caddy` quando executado como serviço, ele não terá permissão para instalar o certificado raiz da CA no trust store do sistema. Para fazer isso, execute [`sudo caddy trust`](/docs/command-line#caddy-trust) para realizar a instalação.

Se você quiser que outros dispositivos se conectem ao seu servidor ao usar o issuer [`internal`](/docs/caddyfile/directives/tls#internal), será necessário instalar o certificado raiz da CA nesses dispositivos também. Você pode encontrar o certificado raiz da CA em `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt`. Muitos navegadores agora usam seu próprio trust store (ignorando o trust store do sistema), então talvez você também precise instalar o certificado manualmente lá.

### Overrides

A melhor forma de sobrescrever aspectos dos arquivos de serviço é com este comando:
<pre><code class="cmd bash">sudo systemctl edit caddy</code></pre>

Isso abrirá um arquivo em branco com seu editor de texto padrão do terminal, no qual você pode sobrescrever ou adicionar diretivas à definição da unidade. Isso é chamado de arquivo "drop-in".

<a id="environment-variables"></a>
#### Variáveis de ambiente

Se você precisar definir variáveis de ambiente para uso na sua configuração, pode fazê-lo assim:
```systemd
[Service]
Environment="CF_API_TOKEN=super-secret-cloudflare-tokenvalue"
```

Da mesma forma, se preferir manter um arquivo separado para variáveis de ambiente (envfile), você pode usar a diretiva [`EnvironmentFile`](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) assim:
```systemd
[Service]
EnvironmentFile=/etc/caddy/.env
```

Então o seu arquivo `/etc/caddy/.env` pode ser assim (não use aspas `"` em torno dos valores):

```env
CF_API_TOKEN=super-secret-cloudflare-tokenvalue
```

<a id="run-and-reload-override"></a>
#### Override de `run` e `reload`

Se você precisar mudar o arquivo de configuração do padrão Caddyfile para usar um arquivo JSON (observe que diretivas `Exec*` [devem ser reiniciadas com strings vazias](https://www.freedesktop.org/software/systemd/man/systemd.service.html#ExecStart=) antes de definir um novo valor):
```systemd
[Service]
ExecStart=
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/caddy.json
ExecReload=
ExecReload=/usr/bin/caddy reload --config /etc/caddy/caddy.json
```

<a id="restart-on-crash"></a>
#### Reiniciar em caso de falha

Se você quiser que o caddy reinicie sozinho após 5s se ele travar inesperadamente:
```systemd
[Service]
# Reinicia automaticamente o caddy se ele travar, exceto se o código de saída for 1
RestartPreventExitStatus=1
Restart=on-failure
RestartSec=5s
```

Então salve o arquivo, saia do editor de texto e reinicie o serviço para que a mudança tenha efeito:
<pre><code class="cmd bash">sudo systemctl restart caddy</code></pre>

<a id="selinux-considerations"></a>
### Considerações sobre SELinux

Em sistemas com SELinux habilitado, você tem duas opções:
1. Instalar o Caddy usando o [repositório COPR](/docs/install#fedora-redhat-centos). Seu arquivo systemd e o binário do caddy já serão criados e rotulados corretamente (então você pode ignorar esta seção). Se quiser usar uma build personalizada do Caddy, será necessário rotular o executável como descrito abaixo.

2. [Baixar o Caddy deste site](/download) ou compilá-lo com [`xcaddy`](https://github.com/caddyserver/xcaddy). Em qualquer dos casos, você precisará rotular os arquivos manualmente.

Arquivos de unidade systemd e seus executáveis não serão executados a menos que sejam rotulados com `systemd_unit_file_t` e `bin_t`, respectivamente.

O rótulo `systemd_unit_file_t` é aplicado automaticamente a arquivos criados em `/etc/systemd/...`, então certifique-se de criar seu arquivo `caddy.service` lá, conforme as instruções de [instalação manual](#manual-installation).

Para marcar o binário `caddy`, você pode usar o seguinte comando:
<pre><code class="cmd bash">semanage fcontext -a -t bin_t /usr/bin/caddy && restorecon -Rv /usr/bin/caddy
</code></pre>

<a id="windows-service"></a>
## Serviço Windows

Há duas formas de executar o Caddy como serviço no Windows: [sc.exe](#scexe) ou [WinSW](#winsw).

### sc.exe

Para criar o serviço, execute:

<pre><code class="cmd bash">sc.exe create caddy start= auto binPath= "YOURPATH\caddy.exe run"</code></pre>

(substitua `YOURPATH` pelo caminho real do seu `caddy.exe`)

Para iniciar:

<pre><code class="cmd bash">sc.exe start caddy</code></pre>

Para parar:

<pre><code class="cmd bash">sc.exe stop caddy</code></pre>

### WinSW

Instale o Caddy como serviço no Windows com estas instruções.

**Requisitos:**

- binário `caddy.exe` que você [baixou](/download) ou [compilou a partir do código-fonte](/docs/build)
- qualquer `.exe` da release mais recente do wrapper de serviço [WinSW](https://github.com/winsw/winsw/releases/latest) (a configuração de serviço abaixo foi escrita para releases v2.x)

Coloque todos os arquivos em um diretório de serviço. Nos exemplos a seguir, usaremos `C:\caddy`.

Renomeie o arquivo `WinSW-x64.exe` para `caddy-service.exe`.

Adicione um `caddy-service.xml` no mesmo diretório:

```xml
<service>
  <id>caddy</id>
  <!-- Display name of the service -->
  <name>Caddy Web Server (powered by WinSW)</name>
  <!-- Service description -->
  <description>Caddy Web Server (https://caddyserver.com/)</description>
  <executable>%BASE%\caddy.exe</executable>
  <arguments>run</arguments>
  <log mode="roll-by-time">
    <pattern>yyyy-MM-dd</pattern>
  </log>
</service>
```

Agora você pode instalar o serviço usando:
<pre><code class="cmd bash">caddy-service install</code></pre>

Talvez você queira abrir o Console de Serviços do Windows para ver se o serviço está rodando corretamente:
<pre><code class="cmd bash">services.msc</code></pre>

Observe que serviços do Windows não podem ser recarregados, então você precisa dizer ao caddy diretamente para recarregar:
<pre><code class="cmd bash">caddy reload</code></pre>

Reiniciar é possível pelos comandos normais de serviços do Windows, por exemplo pela aba "Services" do Task Manager.

Para personalizar o wrapper de serviço, veja a [documentação do WinSW](https://github.com/winsw/winsw/tree/master#usage)

## Docker Compose

A forma mais simples de colocar tudo em funcionamento com Docker é usar Docker Compose. Veja a documentação no [Docker Hub](https://hub.docker.com/_/caddy) para mais detalhes sobre a imagem oficial Docker do Caddy.

<aside class="tip">

Isso assume que você está usando o [Docker Compose V2](https://docs.docker.com/compose/reference/), em que o comando agora é `docker compose` (com espaço), em vez do `docker-compose` (com hífen) do V1.

</aside>

<a id="setup"></a>
### Configuração

Primeiro, crie um arquivo `compose.yml` (ou adicione esse serviço ao arquivo existente):

```yaml
services:
  caddy:
    image: caddy:<version>
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./conf:/etc/caddy
      - ./site:/srv
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

Certifique-se de preencher o `<version>` da imagem com o número da versão mais recente, que você pode encontrar listado no [Docker Hub](https://hub.docker.com/_/caddy) na seção "Tags".

O que isso faz:

- Usa a política de reinício `unless-stopped` para garantir que o container do Caddy seja reiniciado automaticamente quando sua máquina reiniciar.
- Faz bind nas portas `80` e `443` para HTTP e HTTPS respectivamente, além de `443/udp` para HTTP/3.
- Faz bind mount do diretório `conf`, que contém a configuração do Caddyfile.
- Faz bind mount do diretório `site` para servir os arquivos estáticos do seu site a partir de `/srv`.
- Volumes nomeados para `/data` e `/config` para [persistir informações importantes](/docs/conventions#file-locations).

Depois, crie um arquivo chamado `Caddyfile` como o único arquivo no diretório `conf`, e escreva sua configuração [Caddyfile](/docs/caddyfile/concepts).

Se você tiver arquivos estáticos para servir, pode colocá-los em um diretório `site/` ao lado das configs e então definir a [`root`](/docs/caddyfile/directives/root) usando `root /srv`. Se não tiver, pode remover o volume mount `/srv`.

<aside class="tip">

Se você estiver usando o Caddy para [reverse proxy](/docs/caddyfile/directives/reverse_proxy) para outro container, lembre-se de que, na rede Docker, `localhost` significa "este container", não "esta máquina". Portanto, por exemplo, não use `reverse_proxy localhost:8080`; use `reverse_proxy other-container:8080` em vez disso.

</aside>

Se você precisar de uma build personalizada do Caddy com plugins, siga as [instruções de build para Docker](/docs/build#docker) para criar uma imagem Docker personalizada. Crie o `Dockerfile` ao lado do `compose.yml`, e então substitua a linha `image:` no seu `compose.yml` por `build: .`.

<a id="usage"></a>
### Uso

Então, você pode iniciar o container:
<pre><code class="cmd bash">docker compose up -d</code></pre>

Para recarregar o Caddy após fazer alterações no Caddyfile:
<pre><code class="cmd bash">docker compose exec -w /etc/caddy caddy caddy reload</code></pre>

Desde a v2.11.0, você pode recarregar usando `SIGUSR1`, desde que o Caddy tenha sido iniciado com `caddy run` e um arquivo de configuração:
<pre><code class="cmd bash">docker compose kill -sUSR1 caddy</code></pre>

Para ver os 1000 logs mais recentes do Caddy, e acompanhar novos logs em streaming com `f`:
<pre><code class="cmd bash">docker compose logs caddy -n=1000 -f</code></pre>

<a id="local-https-with-docker"></a>
### HTTPS local com Docker

Ao usar Docker para desenvolvimento local com HTTPS, você pode usar um [hostname](/docs/caddyfile/concepts#addresses) como `localhost` ou `app.localhost`. Isso habilita o [HTTPS local](/docs/automatic-https#local-https) usando a CA local do Caddy para emitir certificados. Isso significa que clientes HTTP fora do container não confiarão no certificado TLS servido pelo Caddy. Para resolver isso, você pode instalar o certificado raiz da CA do Caddy na trust store da sua máquina host:

<div x-data="{ os: $persist(defaultOS(['linux', 'mac', 'windows'], 'linux')) }" class="tabs">
<div class="tab-buttons">
	<button x-on:click="os = 'linux'" x-bind:class="{ active: os === 'linux' }">Linux</button>
	<button x-on:click="os = 'mac'" x-bind:class="{ active: os === 'mac' }">Mac</button>
	<button x-on:click="os = 'windows'" x-bind:class="{ active: os === 'windows' }">Windows</button>
</div>

<div x-show="os === 'linux'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /usr/local/share/ca-certificates/root.crt \
  && sudo update-ca-certificates</code></pre>

</div>

<div x-show="os === 'mac'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    /tmp/root.crt \
  && sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain /tmp/root.crt</code></pre>

</div>

<div x-show="os === 'windows'" class="tab bordered">

<pre><code class="cmd bash">docker compose cp \
    caddy:/data/caddy/pki/authorities/local/root.crt \
    %TEMP%/root.crt \
  && certutil -addstore -f "ROOT" %TEMP%/root.crt</code></pre>

</div>
</div>

Muitos navegadores agora usam sua própria trust store (ignorando a trust store do sistema), então talvez você também precise instalar o certificado manualmente lá, usando o arquivo `root.crt` copiado do container no comando acima.

- Para Firefox, vá em Preferences > Privacy & Security > Certificates > View Certificates > Authorities > Import, e selecione o arquivo `root.crt`.

- Para Chrome, vá em Settings > Privacy and security > Security > Manage certificates > Authorities > Import, e selecione o arquivo `root.crt`.
