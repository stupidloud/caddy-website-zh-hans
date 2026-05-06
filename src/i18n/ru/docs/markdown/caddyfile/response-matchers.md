---
title: Matchers ответов (Caddyfile)
---

<script>
ready(function() {
	// Response matchers
	$$_('pre.chroma .nd').forEach(item => {
		if (item.innerText.includes('@')) {
			let text = item.innerText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
			let url = '#' + item.innerText.replace(/_/g, "-");
			item.classList.add('nd');
			item.classList.remove('k');
			item.innerHTML = `<a href="#syntax" style="color: inherit;">${text}</a>`;
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('status')) {
			item.innerHTML = '<a href="#status" style="color: inherit;">status</a>';
		}
	});
	
	$$_('pre.chroma .k').forEach(item => {
		if (item.innerText.includes('header')) {
			item.innerHTML = '<a href="#header" style="color: inherit;">header</a>';
		}
	});

	// We'll add links to all the subdirectives if a matching anchor tag is found on the page.
	addLinksToSubdirectives();
});
</script>

<a id="response-matchers"></a>
# Matchers ответов

**Matchers ответов** можно использовать для фильтрации (или классификации) ответов по конкретным критериям.

Обычно они появляются только как конфигурация внутри некоторых других директив, чтобы принимать решения об ответе в момент его записи клиенту.

- [Синтаксис](#syntax)
- [Matchers](#matchers)
	- [status](#status)
	- [header](#header)

<a id="syntax"></a>
## Синтаксис

Если директива принимает matchers ответов, в документации по синтаксису использование обозначается как `[<response_matcher>]` или `[<inline_response_matcher>]`.

- Токен **<response_matcher>** может быть именем ранее объявленного именованного matcher ответа. Например: `@name`.
- Токен **<inline_response_matcher>** может быть самим критерием ответа без предварительного объявления. Например: `status 200`.

<a id="named"></a>
### Именованный

```caddy-d
@name {
	status <code...>
	header <field> [<value>]
}
```
Если для директивы важен только один аспект ответа, можно указать имя и критерий в одной строке:

```caddy-d
@name status <code...>
```

<a id="inline"></a>
### Inline

```caddy-d
... {
	status <code...>
	header <field> [<value>]
}
```
```caddy-d
... status <code...>
```
```caddy-d
... header <field> [<value>]
```

<a id="matchers"></a>
## Matchers

### status

```caddy-d
status <code...>
```

По HTTP status code.

- **&lt;code...&gt;** — список HTTP status codes. Особые случаи — строки вроде `2xx` и `3xx`, которые соответствуют всем status codes в диапазонах `200`-`299` и `300`-`399` соответственно.

<a id="example"></a>
#### Пример:

```caddy-d
@success status 2xx
```



### header

```caddy-d
header <field> [<value>]
```

По полям header ответа.

- `<field>` — имя проверяемого поля HTTP header.
	- Если оно начинается с `!`, для совпадения поле не должно существовать (аргумент value опускается).
- `<value>` — значение, которое должно быть у поля для совпадения.
	- Если оно начинается с `*`, выполняется быстрое совпадение по суффиксу (значение появляется в конце).
	- Если оно заканчивается на `*`, выполняется быстрое совпадение по префиксу (значение появляется в начале).
	- Если оно заключено в `*`, выполняется быстрое совпадение по подстроке (значение появляется где угодно).
	- В остальных случаях это быстрое точное совпадение.

Разные поля header в одном наборе объединяются через AND. Несколько значений для одного поля объединяются через OR.

Обратите внимание, что поля header могут повторяться и иметь разные значения. Backend-приложения ДОЛЖНЫ учитывать, что значения полей header являются массивами, а не одиночными значениями, и Caddy не интерпретирует смысл в таких неоднозначных ситуациях.

<a id="example-1"></a>
#### Пример:

Сопоставить ответы, в которых header `Foo` содержит значение `bar`:

```caddy-d
@upgrade header Foo *bar*
```

Сопоставить ответы, в которых header `Foo` имеет значение `bar` ИЛИ `baz`:

```caddy-d
@foo {
	header Foo bar
	header Foo baz
}
```

Сопоставить ответы, у которых вообще нет поля header `Foo`:

```caddy-d
@not_foo header !Foo
```
