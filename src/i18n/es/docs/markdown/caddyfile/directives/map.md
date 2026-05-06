---
title: map (directiva de Caddyfile)
---

# map

Configura valores de placeholders personalizados según un valor de entrada.

Compara el valor de origen con el lado de entrada del map y, para la coincidencia encontrada, aplica el/los valor(es) de salida a cada destino. Los destinos se convierten en nombres de placeholder. También se pueden especificar valores de salida predeterminados para cada destino.

Los placeholders mapeados no se evalúan hasta que se usan, por lo que incluso con mapeos muy grandes, esta directiva es bastante eficiente.

## Sintaxis

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<input> <outputs...>
	default    <defaults...>
}
```

- **&lt;source&gt;** es el valor de entrada sobre el que conmutar. Suele ser un placeholder.

- **&lt;destinations...&gt;** son los placeholders a crear que contendrán los valores de salida.

- **&lt;input&gt;** es el valor de entrada a comparar. Si tiene prefijo `~`, se trata como expresión regular.

- **&lt;outputs...&gt;** es uno o más valores de salida que se almacenan en el placeholder asociado. La primera salida se escribe en el primer destino, la segunda salida en el segundo destino, etc.
  
  Como caso especial, el parser de Caddyfile trata las salidas que son un guion literal (`-`) como valores nulos (`null`/`nil`). Esto es útil si quieres volver al valor por defecto para esa salida concreta en el caso de esa entrada, pero usar valores no predeterminados para otras salidas.

  Las salidas se convierten de tipo si es posible; `true` y `false` se convertirán a booleanos, y los valores numéricos a entero o flotante según corresponda. Para evitar esta conversión, puedes envolver la salida entre [comillas](/docs/caddyfile/concepts#tokens-and-quotes) y permanecerá como cadena.

  El número de salidas para cada mapeo no debe exceder el número de destinos; sin embargo, por conveniencia, puede haber menos salidas que destinos, y cualquier salida faltante se rellenará implícitamente.
  
  Si se usó una expresión regular como entrada, los grupos de captura pueden referenciarse con `${group}`, donde `group` es el nombre o el número del grupo de captura en la expresión. El grupo de captura `0` es la coincidencia completa de la regexp, `1` el primer grupo, `2` el segundo, y así sucesivamente.

- **&lt;default&gt;** especifica los valores de salida a almacenar si no coinciden entradas.


## Ejemplos

El siguiente ejemplo demuestra la mayoría de aspectos de esta directiva:

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

Esta directiva conmutará según el valor de `{host}`, es decir, el nombre de dominio de la solicitud.

- Si la solicitud es para `example.com`, establece `{my_placeholder}` en `some value` y `{magic_number}` en `3`.
- Si la solicitud es para `foo.example.com`, establece `{my_placeholder}` en `another value` y deja que `{magic_number}` use el valor por defecto `42`.
- Si la solicitud es para cualquier subdominio de `example.com`, establece `{my_placeholder}` con una cadena que contiene el valor del primer grupo de captura de la expresión regular, es decir, el subdominio completo, y establece `{magic_number}` en `5`.
- Si la solicitud es para cualquier host que termine en `.net` o `.xyz`, establece solo `{magic_number}` en `7` o `15`, respectivamente. Deja `{my_placeholder}` sin establecer.
- En caso contrario (para todos los demás hosts), se aplicarán los valores predeterminados: `{my_placeholder}` se establecerá en `unknown domain` y `{magic_number}` en `42`.
