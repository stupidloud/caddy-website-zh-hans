---
title: acme_server (diretiva do Caddyfile)
---

# acme_server

Um handler de servidor embutido do [protocolo ACME](https://tools.ietf.org/html/rfc8555). Isso permite que uma instância do Caddy emita certificados para qualquer outro software compatível com ACME (incluindo outras instâncias do Caddy).

Quando habilitado, requisições que correspondam ao caminho `/acme/*` serão tratadas pelo servidor ACME.


## Configuração do cliente

Usando os padrões do servidor ACME, os clientes ACME devem ser configurados simplesmente para usar `https://localhost/acme/local/directory` como endpoint ACME. (`local` é o ID da CA padrão do Caddy.)


## Sintaxe

```caddy-d
acme_server [<matcher>] {
	ca         <id>
	lifetime   <duration>
	resolvers  <resolvers...>
	challenges <challenges...>
	allow_wildcard_names
	allow {
		domains <domains...>
		ip_ranges <addresses...>
	}
	deny {
		domains <domains...>
		ip_ranges <addresses...>
	}
}
```

- **ca** especifica o ID da autoridade certificadora com a qual os certificados serão assinados. O padrão é `local`, que é a CA padrão do Caddy, destinada a certificados autoassinados usados localmente, o que é mais comum em ambientes de desenvolvimento. Para uso mais amplo, é recomendável especificar outra CA para evitar confusão. Se a CA com o ID fornecido ainda não existir, ela será criada. Veja as [opções globais da app PKI](/docs/caddyfile/options#pki-options) para configurar CAs alternativas.

- **lifetime** (Padrão: `12h`) é uma [duração](/docs/conventions#durations) que especifica o período de validade dos certificados emitidos. Esse valor deve ser menor que a duração do [certificado intermediário](/docs/caddyfile/options#intermediate-lifetime) usado para assinatura. Não é recomendável alterar isso, a menos que seja absolutamente necessário.

- **resolvers** são os endereços dos resolvedores DNS a usar ao procurar os registros TXT para resolver desafios ACME DNS. Aceita [endereços de rede](/docs/conventions#network-addresses), com padrão de UDP e porta 53, a menos que especificado. Se o host for um endereço IP, a conexão será feita diretamente para resolver o servidor upstream. Se o host não for um endereço IP, os endereços serão resolvidos usando a [convenção de resolução de nomes](https://golang.org/pkg/net/#hdr-Name_Resolution) da biblioteca padrão do Go. Se vários resolvers forem especificados, um deles será escolhido aleatoriamente.

- **challenges** define os tipos de desafio habilitados. Se não for definido ou se a diretiva for usada sem valores, todos os tipos de desafio serão habilitados. Valores aceitos: `http-01`, `tls-alpn-01`, `dns-01`.

- **allow_wildcard_names** habilita a emissão de certificados com SAN curinga (Subject Alternative Name)

- **allow**, **deny** configuram a política operacional do `acme_server`. A avaliação da política segue os critérios descritos pela Step-CA [aqui](https://smallstep.com/docs/step-ca/policies/#policy-evaluation).

	- **domains** define os nomes de domínio de sujeito que devem ser permitidos ou negados conforme os critérios de avaliação da política.

	- **ip_ranges** define os intervalos de IP de sujeito que devem ser permitidos ou negados conforme os critérios de avaliação da política.

## Exemplos

Para servir um servidor ACME com ID `home` no domínio `acme.example.com`, com a CA personalizada pela [opção global `pki`](/docs/caddyfile/options#pki-options), e emitindo seu próprio certificado usando o emissor `internal`:

```caddy
{
	pki {
		ca home {
			name "My Home CA"
		}
	}
}

acme.example.com {
	tls {
		issuer internal {
			ca home
		}
	}
	acme_server {
		ca home
	}
}
```

Se você tiver outro servidor Caddy, ele poderá usar o servidor ACME acima para emitir seus próprios certificados:

```caddy
{
	acme_ca https://acme.example.com/acme/home/directory
	acme_ca_root /path/to/home_ca_root.crt
}

example.com {
	respond "Olá, mundo!"
}
```
