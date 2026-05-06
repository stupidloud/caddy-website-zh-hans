---
title: map (директива Caddyfile)
---

# map

Задает значения пользовательских placeholders, переключаемые по входному значению.

Она сравнивает source value с входной стороной map и для совпавшего значения применяет output value(s) к каждому destination. Destinations становятся именами placeholders. Для каждого destination также можно указать default output values.

Mapped placeholders не вычисляются до тех пор, пока не будут использованы, поэтому даже для очень больших mappings эта директива достаточно эффективна.

<a id="syntax"></a>
## Синтаксис

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<input> <outputs...>
	default    <defaults...>
}
```

- **&lt;source&gt;** — входное значение, по которому выполняется переключение. Обычно placeholder.

- **&lt;destinations...&gt;** — создаваемые placeholders, которые будут хранить output values.

- **&lt;input&gt;** — входное значение для сопоставления. Если начинается с `~`, оно трактуется как regular expression.

- **&lt;outputs...&gt;** — одно или несколько output values для сохранения в связанном placeholder. Первый output записывается в первый destination, второй output — во второй destination и т. д.
  
  В качестве особого случая parser Caddyfile трактует outputs, являющиеся literal hyphen (`-`), как null/nil values. Это полезно, если для данного input нужно откатиться к default value для конкретного output, но использовать non-default values для других outputs.

  Outputs будут преобразованы по типу, если это возможно; `true` и `false` будут преобразованы в boolean types, а числовые значения — в integer или float соответственно. Чтобы избежать этого преобразования, можно обернуть output [кавычками](/docs/caddyfile/concepts#tokens-and-quotes), и он останется string.

  Количество outputs для каждого mapping не должно превышать количество destinations; однако для удобства outputs может быть меньше, чем destinations, и любые отсутствующие outputs будут заполнены неявно.
  
  Если в качестве input использовался regular expression, capture groups можно ссылаться через `${group}`, где `group` — имя или номер capture group в expression. Capture group `0` — полное regexp match, `1` — первая capture group, `2` — вторая capture group и т. д.

- **&lt;default&gt;** задает output values, которые нужно сохранить, если ни один input не совпал.


<a id="examples"></a>
## Примеры

Следующий пример демонстрирует большинство аспектов этой директивы:

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

Эта директива переключается по значению `{host}`, то есть по domain name запроса.

- Если запрос к `example.com`, установить `{my_placeholder}` в `some value`, а `{magic_number}` в `3`.
- Иначе, если запрос к `foo.example.com`, установить `{my_placeholder}` в `another value`, а `{magic_number}` оставить со значением по умолчанию `42`.
- Иначе, если запрос к любому subdomain `example.com`, установить `{my_placeholder}` в string, содержащую значение первой regexp capture group, то есть весь subdomain, и установить `{magic_number}` в 5.
- Иначе, если запрос к любому host, заканчивающемуся на `.net` или `.xyz`, установить только `{magic_number}` в `7` или `15` соответственно. Оставить `{my_placeholder}` неустановленным.
- Иначе (для всех остальных hosts) будут применены значения по умолчанию: `{my_placeholder}` будет установлен в `unknown domain`, а `{magic_number}` — в `42`.
