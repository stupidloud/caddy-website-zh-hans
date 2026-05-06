---
title: log_name (diretiva do Caddyfile)
---

# log_name

Sobrescreve o nome do logger a usar para uma requisição ao escrever access logs com a [`diretiva log`](log).

Esta diretiva é útil quando você quer registrar requisições em arquivos diferentes com base em alguma condição, como o caminho ou método da requisição.

Mais de um nome de logger pode ser especificado, de modo que o log da requisição seja enviado para mais de um logger correspondente.

Isso é frequentemente combinado com a opção [`no_hostname`](log#no_hostname) da diretiva `log`, que impede que o logger seja associado a qualquer hostname do bloco de site, de modo que apenas requisições que definirem `log_name` enviarão logs para esse logger.


## Sintaxe

```caddy-d
log_name [<matcher>] <names...>
```


## Exemplos

Talvez você queira registrar requisições em arquivos diferentes, por exemplo, registrar health checks em um arquivo separado dos access logs principais.

Usar `no_hostname` em um `log` impede que o logger seja associado a qualquer hostname do bloco de site (isto é, `localhost` aqui), de modo que apenas requisições que tenham `log_name` definido para o nome desse logger receberão logs.

```caddy
localhost {
	log {
		output file ./caddy.access.log
	}

	log health_check_log {
		output file ./caddy.access.health.log
		no_hostname
	}

	handle /healthz* {
		log_name health_check_log
		respond "Healthy"
	}

	handle {
		respond "Hello World"
	}
}
```
