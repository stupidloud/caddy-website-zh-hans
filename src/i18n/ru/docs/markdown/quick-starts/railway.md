---
title: Быстрый старт с Railway
---

<a id="railway-quick-start"></a>
# Быстрый старт с Railway

Развертывание Caddy на Railway — простой и беспроблемный способ развернуть собственную сборку Caddy с плагинами.

**Предварительные требования:**
- Бесплатная учетная запись [Railway](https://railway.com)

<a id="deploy-caddy-on-railway"></a>
## Развертывание Caddy на Railway

Перейдите на нашу [страницу загрузки](/download), выберите нужные плагины, затем нажмите фиолетовую кнопку "Deploy on Railway" сверху.

<details>
	<summary>Или настройте шаблон вручную</summary>

Если вы хотите настроить шаблон Railway самостоятельно, вот как это сделать.

Перейдите к шаблону на Railway:

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

и добавьте нужные плагины, нажав "Configure":

![Экран развертывания](/resources/images/railway/deploy-screen.png)

Затем вставьте плагины в переменную `CADDY_PLUGINS`, разделяя их пробелами:

![Добавление плагинов](/resources/images/railway/deploy-config.png)

</details>

Нажмите Deploy, а после завершения развертывания проверьте его, нажав ссылку здесь:

![Посетить развертывание](/resources/images/railway/prod-link.png)

Вы должны увидеть страницу приветствия, показывающую, что ваш новый сервер работает!

Далее можно настроить развертывание так, чтобы оно обслуживало ваш собственный сайт или проксировало к другому сервису Railway.

<a id="customize-the-deployment"></a>
## Настройка развертывания

Чтобы обслуживать собственный сайт или изменить конфигурацию, просто "eject" [наш шаблон](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic) в ваш собственный репозиторий:

![Eject template](/resources/images/railway/eject.png)

Из собственного репозитория вы можете:

- Поместить свой сайт в папку `www`.
- Изменить конфигурацию Caddy, то есть [Caddyfile](/docs/caddyfile).

Просто закоммитьте изменения и отправьте их, затем можно снова развернуть на Railway.

Если вы хотите изменить плагины в вашей сборке Caddy, достаточно отредактировать переменную `CADDY_PLUGINS` и повторно развернуть:

![Изменить плагины](/resources/images/railway/plugins-variable.png)

<a id="tips"></a>
## Советы

Railway завершает TLS за вас, поэтому конфигурацию Caddy следует писать так, как будто к нему уже проксируют запросы (так и есть). Поэтому, если вы используете hosts в адресах сайтов Caddyfile, в глобальных параметрах следует использовать `auto_https off`. В нашем шаблоне Caddy не находится на edge.


<a id="variables"></a>
## Переменные

Переменные окружения, которые можно задать в проекте Railway и которые этот шаблон может использовать:

Name | Description | Default | Example(s)
---- | ----------- | ------- | ----------
`CADDY_PLUGINS` | Список плагинов Caddy, разделенный пробелами | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
