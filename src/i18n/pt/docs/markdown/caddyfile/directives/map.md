---
title: map (diretiva do Caddyfile)
---

# map

Define valores de placeholders personalizados com base em um valor de entrada.

Ela compara o valor de origem com a parte de entrada do mapa e, para a correspondência encontrada, aplica o(s) valor(es) de saída a cada destino. Os destinos se tornam nomes de placeholder. Também podem ser especificados valores de saída padrão para cada destino.

Os placeholders mapeados não são avaliados até que sejam usados, então, mesmo para mapeamentos muito grandes, esta diretiva é bastante eficiente.

## Sintaxe

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<input> <outputs...>
	default    <defaults...>
}
```

- **&lt;source&gt;** é o valor de entrada sobre o qual fazer o switch. Normalmente, um placeholder.

- **&lt;destinations...&gt;** são os placeholders a criar que conterão os valores de saída.

- **&lt;input&gt;** é o valor de entrada a corresponder. Se for prefixado com `~`, ele será tratado como expressão regular.

- **&lt;outputs...&gt;** é um ou mais valores de saída a armazenar no placeholder associado. A primeira saída é escrita no primeiro destino, a segunda no segundo destino, e assim por diante.
  
  Como caso especial, o parser do Caddyfile trata saídas que sejam um hífen literal (`-`) como valores nulos/nil. Isso é útil se você quiser cair para um valor padrão para aquela saída específica no caso da entrada dada, mas quiser usar valores não padrão para outras saídas.

  As saídas serão convertidas de tipo, se possível; `true` e `false` serão convertidos para booleanos, e valores numéricos serão convertidos para inteiro ou float conforme apropriado. Para evitar essa conversão, você pode envolver a saída com [aspas](/docs/caddyfile/concepts#tokens-and-quotes) e elas permanecerão como strings.

  O número de saídas para cada mapeamento não deve exceder o número de destinos; porém, por conveniência, pode haver menos saídas do que destinos, e qualquer saída faltante será preenchida implicitamente.
  
  Se uma expressão regular foi usada como entrada, então os grupos de captura podem ser referenciados com `${group}`, onde `group` é o nome ou o número do grupo de captura na expressão. O grupo de captura `0` é a correspondência completa da regexp, `1` é o primeiro grupo de captura, `2` é o segundo, e assim por diante.

- **&lt;default&gt;** especifica os valores de saída a armazenar se nenhuma entrada corresponder.


## Exemplos

O exemplo a seguir demonstra a maioria dos aspectos desta diretiva:

```caddy-d
map {host}                {my_placeholder}  {magic_number} {
	example.com           "some value"      3
	foo.example.com       "another value"
	~(.*)\.example\.com$  "${1} subdomain"  5

	~.*\.net$             -                 7
	~.*\.xyz$             -                 15

	default               "unknown domain"  42
}
```

Esta diretiva faz switch com base no valor de `{host}`, isto é, o nome de domínio da requisição.

- Se a requisição for para `example.com`, define `{my_placeholder}` como `some value` e `{magic_number}` como `3`.
- Caso contrário, se a requisição for para `foo.example.com`, define `{my_placeholder}` como `another value` e deixa `{magic_number}` com o padrão `42`.
- Caso contrário, se a requisição for para qualquer subdomínio de `example.com`, define `{my_placeholder}` como uma string contendo o valor do primeiro grupo de captura da regexp, isto é, todo o subdomínio, e define `{magic_number}` como 5.
- Caso contrário, se a requisição for para qualquer host que termine em `.net` ou `.xyz`, define apenas `{magic_number}` como `7` ou `15`, respectivamente. Deixa `{my_placeholder}` sem definição.
- Caso contrário (para todos os outros hosts), os valores padrão serão aplicados: `{my_placeholder}` será definido como `unknown domain` e `{magic_number}` como `42`.
