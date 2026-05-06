---
title: map (Caddyfile 지시어)
---

# map

입력 값에 따라 전환되는 커스텀 플레이스홀더의 값을 설정합니다.

소스 값을 맵의 입력 측과 비교하여, 일치하는 항목에 대해 출력 값을 각 대상에 적용합니다. 대상은 플레이스홀더 이름이 됩니다. 각 대상에 대해 기본 출력 값을 지정할 수도 있습니다.

매핑된 플레이스홀더는 사용될 때까지 평가되지 않으므로, 매우 큰 매핑의 경우에도 이 지시어는 상당히 효율적입니다.

## 구문 <a id="syntax"></a>

```caddy-d
map [<matcher>] <source> <destinations...> {
	[~]<input> <outputs...>
	default    <defaults...>
}
```

- **&lt;source&gt;** 는 전환할 입력 값입니다. 보통 플레이스홀더를 사용합니다.

- **&lt;destinations...&gt;** 는 출력 값을 담기 위해 생성될 플레이스홀더들입니다.

- **&lt;input&gt;** 은 매칭할 입력 값입니다. `~` 접두사가 붙으면 정규 표현식으로 취급됩니다.

- **&lt;outputs...&gt;** 는 연관된 플레이스홀더에 저장할 하나 이상의 출력 값입니다. 첫 번째 출력은 첫 번째 대상에, 두 번째 출력은 두 번째 대상에 기록되는 식입니다.
  
  특수한 경우로, Caddyfile 파서는 하이픈 리터럴(`-`)인 출력을 null/nil 값으로 취급합니다. 이는 특정 입력에 대해 해당 출력만 기본값으로 폴백하고 싶지만, 다른 출력에는 기본값이 아닌 값을 사용하고 싶을 때 유용합니다.

  출력 값은 가능하면 형 변환이 이루어집니다. `true`와 `false`는 불리언 유형으로 변환되고, 숫자 값은 정수 또는 부동 소수점으로 변환됩니다. 이러한 변환을 피하려면 출력을 [따옴표](/docs/caddyfile/concepts#tokens-and-quotes)로 감싸면 문자열로 유지됩니다.

  각 매핑의 출력 개수는 대상 개수를 초과할 수 없습니다. 하지만 편의상 대상보다 출력이 적을 수 있으며, 누락된 출력은 암시적으로 채워집니다.
  
  정규 표현식이 입력으로 사용된 경우, `${group}`을 사용하여 캡처 그룹을 참조할 수 있습니다. 여기서 `group`은 표현식의 캡처 그룹 이름 또는 번호입니다. 캡처 그룹 `0`은 전체 정규식 매치, `1`은 첫 번째 캡처 그룹, `2`는 두 번째 캡처 그룹 등입니다.

- **&lt;default&gt;** 는 일치하는 입력이 없을 경우 저장할 출력 값을 지정합니다.


## 예제 <a id="examples"></a>

다음 예제는 이 지시어의 대부분의 측면을 보여줍니다:

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

이 지시어는 요청의 도메인 이름인 `{host}` 값에 따라 전환됩니다.

- 요청이 `example.com`인 경우, `{my_placeholder}`를 `some value`로, `{magic_number}`를 `3`으로 설정합니다.
- 그렇지 않고, 요청이 `foo.example.com`인 경우, `{my_placeholder}`를 `another value`로 설정하고, `{magic_number}`는 기본값인 `42`가 되도록 합니다.
- 그렇지 않고, 요청이 `example.com`의 서브도메인인 경우, `{my_placeholder}`를 첫 번째 정규식 캡처 그룹(즉, 전체 서브도메인)의 값을 포함하는 문자열로 설정하고, `{magic_number}`를 5로 설정합니다.
- 그렇지 않고, 요청이 `.net` 또는 `.xyz`로 끝나는 호스트인 경우, `{magic_number}`만 각각 `7` 또는 `15`로 설정합니다. `{my_placeholder}`는 설정되지 않은 상태로 둡니다.
- 그렇지 않으면 (다른 모든 호스트의 경우), 기본값이 적용됩니다: `{my_placeholder}`는 `unknown domain`으로 설정되고 `{magic_number}`는 `42`로 설정됩니다.
