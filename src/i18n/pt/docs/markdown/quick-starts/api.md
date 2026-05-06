---
title: "Início rápido da API"
---

# Início rápido da API

**Pré-requisitos:**
- Noções básicas de terminal / linha de comando
- `caddy` e `curl` no seu `PATH`

---

Primeiro inicie o Caddy:

<pre><code class="cmd bash">caddy start</code></pre>

O Caddy está rodando ocioso neste momento (com uma configuração vazia). Dê a ele uma configuração simples com `curl`:

<pre><code class="cmd bash">curl localhost:2019/load \
    -H "Content-Type: application/json" \
    -d @- << EOF
    {
        "apps": {
            "http": {
                "servers": {
                    "hello": {
                        "listen": [":2015"],
                        "routes": [
                            {
                                "handle": [{
                                    "handler": "static_response",
                                    "body": "Hello, world!"
                                }]
                            }
                        ]
                    }
                }
            }
        }
    }
EOF</code></pre>

Enviar um corpo POST com [Heredoc](https://en.wikipedia.org/wiki/Here_document#Unix_shells) pode ser trabalhoso, então, se preferir usar arquivos, salve o JSON em um arquivo chamado `caddy.json` e use este comando:

<pre><code class="cmd bash">curl localhost:2019/load \
  -H "Content-Type: application/json" \
  -d @caddy.json
</code></pre>

Agora carregue [localhost:2015](http://localhost:2015) no navegador ou use `curl`:

<pre><code class="cmd"><span class="bash">curl localhost:2015</span>
Hello, world!</code></pre>

Também podemos definir vários sites em interfaces diferentes com este JSON:

```json
{
	"apps": {
		"http": {
			"servers": {
				"hello": {
					"listen": [":2015"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Hello, world!"
							}]
						}
					]
				},
				"bye": {
					"listen": [":2016"],
					"routes": [
						{
							"handle": [{
								"handler": "static_response",
								"body": "Goodbye, world!"
							}]
						}
					]
				}
			}
		}
	}
}
```

Atualize seu JSON e faça a requisição da API novamente.

Teste seu novo endpoint de "goodbye" [no navegador](http://localhost:2016) ou com `curl` para garantir que funciona:

<pre><code class="cmd"><span class="bash">curl localhost:2016</span>
Goodbye, world!</code></pre>

Quando terminar com o Caddy, lembre-se de pará-lo:

<pre><code class="cmd bash">caddy stop</code></pre>

Há muito mais que você pode fazer com a API, incluindo exportar a configuração e fazer alterações granulares na configuração (em vez de atualizar tudo de uma vez). Não deixe de ler o [tutorial completo da API](/docs/api-tutorial) para aprender como!

## Leitura adicional

- [Tutorial completo da API](/docs/api-tutorial)
- [Documentação da API](/docs/api)
