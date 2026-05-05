---
title: Railway Quick-start
---

<a id="railway-quick-start"></a>
# Railway Quick-start

Caddy auf Railway bereitzustellen ist ein einfacher, unkomplizierter Weg, einen eigenen Caddy-Build mit Plugins zu deployen.

**Voraussetzungen:**
- Ein kostenloses [Railway](https://railway.com)-Konto

<a id="deploy-caddy-on-railway"></a>
## Caddy auf Railway deployen

Gehe zu unserer [Download-Seite](/download), wähle die benötigten Plugins aus und klicke oben auf den violetten Button „Deploy on Railway“.

<details>
	<summary>Oder die Vorlage manuell konfigurieren</summary>

Alternativ kannst du die Railway-Vorlage selbst konfigurieren. So geht es.

Öffne die Vorlage auf Railway:

<a href="https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

und füge alle benötigten Plugins hinzu, indem du auf „Configure“ klickst:

![Deploy-Bildschirm](/resources/images/railway/deploy-screen.png)

Füge die Plugins dann durch Leerzeichen getrennt in die Variable `CADDY_PLUGINS` ein:

![Plugins hinzufügen](/resources/images/railway/deploy-config.png)

</details>

Klicke auf Deploy. Nachdem das Deployment abgeschlossen ist, kannst du es über den Link hier ausprobieren:

![Deployment besuchen](/resources/images/railway/prod-link.png)

Du solltest eine Willkommensseite sehen, die zeigt, dass dein neuer Server funktioniert.

Als Nächstes kannst du dein Deployment anpassen, um deine eigene Website bereitzustellen oder zu einem anderen Railway-Dienst zu proxien.

<a id="customize-the-deployment"></a>
## Deployment anpassen

Um deine eigene Website bereitzustellen oder die Konfiguration zu ändern, „ejecte“ einfach [unsere Vorlage](https://railway.com/deploy/caddy?referralCode=YOPtw9&amp;utm_medium=integration&amp;utm_source=template&amp;utm_campaign=generic) in dein eigenes Repository:

![Vorlage ejecten](/resources/images/railway/eject.png)

Aus deinem eigenen Repository heraus kannst du:

- Deine eigene Website in den Ordner `www` legen.
- Caddys Konfiguration ändern, also das [Caddyfile](/docs/caddyfile).

Committe die Änderungen einfach und pushe sie, dann kannst du auf Railway erneut deployen.

Wenn du die Plugins in deinem Caddy-Build ändern möchtest, musst du nur die Variable `CADDY_PLUGINS` bearbeiten und erneut deployen:

![Plugins ändern](/resources/images/railway/plugins-variable.png)

## Tipps

Railway terminiert TLS für dich, deshalb solltest du deine Caddy-Konfiguration so schreiben, als würde zu ihr geproxied, denn genau das passiert. Wenn du also Hosts in den Site-Adressen deines Caddyfile verwendest, solltest du in den globalen Optionen `auto_https off` setzen. Mit unserer Vorlage steht Caddy nicht direkt am Edge.


<a id="variables"></a>
## Variablen

Umgebungsvariablen, die du in deinem Railway-Projekt setzen kannst und die diese Vorlage verwenden kann:

Name | Beschreibung | Standard | Beispiel(e)
---- | ------------ | -------- | -----------
`CADDY_PLUGINS` | Durch Leerzeichen getrennte Liste von Caddy-Plugins | ` ` | `github.com/caddy-dns/cloudflare github.com/mholt/caddy-ratelimit`
