---
title: "Início rápido do Caddyfile"
---

# Início rápido do Caddyfile

Crie um novo arquivo de texto chamado `Caddyfile` (sem extensão).

A primeira coisa a digitar em um Caddyfile é o endereço do seu site:

```caddy
localhost
```

<aside class="tip">

Se as portas HTTP e HTTPS (80 e 443, respectivamente) forem portas privilegiadas no seu sistema operacional, você precisará executar com privilégios elevados ou usar portas mais altas. Para obter permissão, execute como root com `sudo -E` ou use `sudo setcap cap_net_bind_service=+ep $(which caddy)`. Alternativamente, para usar portas mais altas, basta alterar o endereço para algo como `localhost:2080` e mudar a porta HTTP usando a opção [`http_port`](/docs/caddyfile/options) do Caddyfile.

</aside>

Então pressione Enter e digite o que quer que ele faça, de modo que fique assim:

```caddy
localhost

respond "Hello, world!"
```

Salve isso e execute o Caddy a partir da mesma pasta que contém seu Caddyfile:

<pre><code class="cmd bash">caddy start</code></pre>

Provavelmente será solicitada a sua senha, porque o Caddy serve todos os sites -- até os locais -- via HTTPS por padrão. (O prompt de senha deve aparecer apenas na primeira vez!)

<aside class="tip">

Para HTTPS local, o Caddy gera certificados automaticamente e chaves privadas exclusivas para você. O certificado raiz é adicionado ao trust store do seu sistema, por isso o prompt de senha é necessário. Isso permite desenvolver localmente com HTTPS sem erros de certificado.

</aside>

(Se você receber erros de permissão, talvez precise executar com privilégios elevados ou escolher uma porta acima de 1023.)

Abra o navegador em [localhost](http://localhost) ou use `curl`:

<pre><code class="cmd"><span class="bash">curl https://localhost</span>
Hello, world!</code></pre>

Você pode definir vários sites em um Caddyfile envolvendo-os em chaves `{ }`. Mude seu Caddyfile para ficar assim:

```caddy
localhost {
	respond "Hello, world!"
}

localhost:2016 {
	respond "Goodbye, world!"
}
```

Você pode dar ao Caddy a configuração atualizada de duas formas, ou diretamente com a API:

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: text/caddyfile" \
	--data-binary @Caddyfile
</code></pre>

ou com o comando reload, que faz a mesma requisição à API por você:

<pre><code class="cmd bash">caddy reload</code></pre>

Teste seu novo endpoint de "goodbye" [no navegador](https://localhost:2016) ou com `curl` para garantir que funciona:

<pre><code class="cmd"><span class="bash">curl https://localhost:2016</span>
Goodbye, world!</code></pre>

Quando terminar com o Caddy, lembre-se de pará-lo:

<pre><code class="cmd bash">caddy stop</code></pre>

## Leitura adicional

- [Conceitos do Caddyfile](/docs/caddyfile/concepts)
- [Diretivas](/docs/caddyfile/directives)
- [Padrões comuns](/docs/caddyfile/patterns)
