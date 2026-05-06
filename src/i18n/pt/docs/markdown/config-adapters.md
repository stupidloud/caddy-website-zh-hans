---
title: Adaptadores de Configuração
---

# Adaptadores de Configuração

A linguagem nativa de configuração do Caddy é [JSON](https://www.json.org/json-en.html), mas escrever JSON à mão pode ser trabalhoso e propenso a erros. Por isso o Caddy suporta configuração em outras linguagens por meio de **config adapters**. Eles são plugins do Caddy que tornam possível usar a configuração no formato de sua preferência, gerando [Caddy JSON](/docs/json/) para você.

Por exemplo, um config adapter pode [converter sua configuração do NGINX em Caddy JSON](https://github.com/caddyserver/nginx-adapter).

## Config adapters conhecidos

Os seguintes config adapters estão disponíveis atualmente (alguns são projetos de terceiros):

- [**caddyfile**](/docs/caddyfile) (padrão)
- [**nginx**](https://github.com/caddyserver/nginx-adapter)
- [**jsonc**](https://github.com/caddyserver/jsonc-adapter)
- [**json5**](https://github.com/caddyserver/json5-adapter)
- [**yaml**](https://github.com/abiosoft/caddy-yaml)
- [**cue**](https://github.com/caddyserver/cue-adapter)
- [**toml**](https://github.com/awoodbeck/caddy-toml-adapter)
- [**hcl**](https://github.com/francislavoie/caddy-hcl)
- [**dhall**](https://github.com/mholt/dhall-adapter)
- [**mysql**](https://github.com/zhangjiayin/caddy-mysql-adapter)

## Usando config adapters

Você pode usar um config adapter especificando-o na linha de comando com a flag `--adapter` na maioria dos subcomandos que aceitam uma configuração:

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

Ou pela API, no [endpoint `/load`](/docs/api#post-load):

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

Se quiser apenas obter o JSON de saída sem executá-lo, você pode usar o comando [`caddy adapt`](/docs/command-line#caddy-adapt):

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

## Observações

Nem todas as linguagens de configuração são 100% compatíveis com o Caddy; alguns recursos ou comportamentos simplesmente não são traduzidos bem ou ainda não foram programados no adapter ou no próprio Caddy.

Alguns adapters fazem uma tradução 1 para 1, como YAML->JSON ou TOML->JSON. Outros são criados especificamente para o Caddy, como o Caddyfile. Em geral, esses adapters sempre funcionam.

No entanto, nem todos os adapters funcionam o tempo todo. Os config adapters fazem o possível para converter sua entrada para Caddy JSON com a maior fidelidade e correção. Como esse processo de conversão não é garantido como completo e correto o tempo todo, não os chamamos de "converters" ou "translators". Eles são "adapters" porque, no mínimo, fornecem um bom ponto de partida para você terminar de montar sua configuração JSON final.

Os config adapters podem produzir o JSON resultante, avisos e erros. O JSON é produzido se não houver erros. Erros acontecem quando há algo errado com a entrada (por exemplo, erros de sintaxe). Avisos são emitidos quando há algo errado com a adaptação, mas que não é necessariamente fatal (por exemplo, recurso não suportado). Se você usar configurações adaptadas com avisos, é preciso cautela.
