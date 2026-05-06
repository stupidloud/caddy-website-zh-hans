---
title: Railway Quick-start
---

# Railway 빠른 시작

Railway에 Caddy를 배포하는 것은 플러그인이 포함된 커스텀 Caddy 빌드를 쉽고 번거로움 없이 배포하는 방법입니다.

**사전 준비사항:**
- 무료 [Railway](https://railway.com) 계정

## Railway에 Caddy 배포하기

[다운로드 페이지](/download)로 이동하여 필요한 플러그인을 선택한 다음, 상단에 있는 보라색 "Deploy on Railway" 버튼을 클릭합니다.

<details>
	<summary>또는, 템플릿 수동 설정하기</summary>

Railway 템플릿을 직접 설정하고 싶은 경우, 다음 방법으로 진행할 수 있습니다.

Railway의 템플릿으로 이동합니다:

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

그리고 "Configure"를 클릭하여 필요한 플러그인을 추가합니다:

![Deploy screen](/resources/images/railway/deploy-screen.png)

그런 다음 공백으로 구분하여 `CADDY_PLUGINS` 변수에 플러그인들을 붙여넣습니다:

![Adding plugins](/resources/images/railway/deploy-config.png)

</details>

Deploy를 클릭하고 배포가 완료된 후, 여기의 링크를 클릭하여 테스트해 볼 수 있습니다:

![Visit your deployment](/resources/images/railway/prod-link.png)

새 서버가 정상적으로 작동하고 있음을 보여주는 시작 페이지를 볼 수 있을 것입니다!

다음으로, 자신의 사이트를 제공하거나 다른 Railway 서비스로 프록시하도록 배포를 커스텀할 수 있습니다.

## 배포 커스텀하기

자신의 웹사이트를 제공하거나 설정을 변경하려면, 단순히 [우리의 템플릿](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic)을 자신의 리포지토리로 "추출(eject)"하면 됩니다:

![Eject template](/resources/images/railway/eject.png)

자신의 리포지토리에서 다음을 수행할 수 있습니다:

- `www` 폴더에 자신의 사이트를 넣습니다.
- Caddy의 설정인 [Caddyfile](/docs/caddyfile)을 수정합니다.

간단히 변경 사항을 커밋하고 푸시한 다음, Railway에 재배포할 수 있습니다.

Caddy 빌드의 플러그인을 변경하려면 `CADDY_PLUGINS` 변수를 편집하고 재배포하기만 하면 됩니다:

![Change plugins](/resources/images/railway/plugins-variable.png)

## 팁

Railway가 TLS를 대신 종료해 주므로, 프록시 되는 것처럼 Caddy 설정을 작성해야 합니다 (실제로 프록시 되기 때문입니다). 따라서 Caddyfile 사이트 주소에 호스트를 사용하는 경우, 전역 옵션(global options)에서 `auto_https off`를 사용해야 합니다. 템플릿을 사용할 때 Caddy는 엣지를 마주하는(edge-facing) 것이 아닙니다.

## 변수

이 템플릿이 사용할 수 있는, Railway 프로젝트에 설정할 수 있는 환경 변수입니다:

Name | Description | Default | Example(s)
---- | ----------- | ------- | ----------
`CADDY_PLUGINS` | 공백으로 구분된 Caddy 플러그인 목록 | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
