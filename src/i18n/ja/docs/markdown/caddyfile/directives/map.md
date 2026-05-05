---
title: map (Caddyfile directive)
---

# map

入力値に応じて、カスタム placeholder の値を設定します。

source 値を map の入力側と比較し、マッチしたものについて、各 destination に output 値を適用します。destination は placeholder 名になります。各 destination にはデフォルトの output 値も指定できます。

map された placeholder は使われるまで評価されないため、非常に大きな mapping でもこのディレクティブはかなり効率的です。

<a id="syntax"></a>
## 構文

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<input> <outputs...>
	default    <defaults...>
}
```

- **&lt;source&gt;** は切り替えに使う入力値です。通常は placeholder です。

- **&lt;destinations...&gt;** は、output 値を保持するために作成する placeholder です。

- **&lt;input&gt;** はマッチ対象の入力値です。`~` を prefix として付けると、正規表現として扱われます。

- **&lt;outputs...&gt;** は、関連する placeholder に保存する 1 つ以上の output 値です。最初の output は最初の destination に、2 番目の output は 2 番目の destination に、という順に書き込まれます。
  
  特別なケースとして、Caddyfile パーサーはリテラルのハイフン（`-`）である output を null/nil 値として扱います。これは、指定された input の場合に特定の output だけはデフォルト値へフォールバックし、他の output には非デフォルト値を使いたい場合に便利です。

  output は可能であれば型変換されます。`true` と `false` は boolean 型に変換され、数値は integer または float に変換されます。この変換を避けるには、output を [quotes](/docs/caddyfile/concepts#tokens-and-quotes) で囲むと文字列のままになります。

  各 mapping の output 数は destination 数を超えてはいけません。ただし利便性のため、destination より少ない output は許可され、不足分は暗黙的に補完されます。
  
  input に正規表現を使った場合、capture group は `${group}` で参照できます。`group` には、式内の capture group の名前または番号を指定します。capture group `0` は正規表現全体のマッチ、`1` は最初の capture group、`2` は 2 番目の capture group、という形です。

- **&lt;default&gt;** は、どの input にもマッチしない場合に保存する output 値を指定します。


<a id="examples"></a>
## 例

次の例は、このディレクティブの主な使い方を示しています。

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

このディレクティブは `{host}`、つまりリクエストの domain name の値で切り替えます。

- リクエストが `example.com` 宛ての場合、`{my_placeholder}` を `some value` に、`{magic_number}` を `3` に設定します。
- そうでなく、リクエストが `foo.example.com` 宛ての場合、`{my_placeholder}` を `another value` に設定し、`{magic_number}` はデフォルトの `42` にします。
- そうでなく、リクエストが `example.com` の任意の subdomain 宛ての場合、`{my_placeholder}` を最初の regexp capture group の値、つまり subdomain 全体を含む文字列に設定し、`{magic_number}` を 5 に設定します。
- そうでなく、リクエストが `.net` または `.xyz` で終わる任意の host 宛ての場合、それぞれ `{magic_number}` だけを `7` または `15` に設定します。`{my_placeholder}` は未設定のままにします。
- それ以外（すべての他の host）では、デフォルト値が適用されます。`{my_placeholder}` は `unknown domain` に、`{magic_number}` は `42` に設定されます。
