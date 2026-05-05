---
title: "Automatic HTTPS"
---

<a id="automatic-https"></a>
# Automatic HTTPS

**Caddy war der erste Webserver, der HTTPS automatisch *und standardmäßig* verwendet hat.**

Automatic HTTPS provisioniert TLS-Zertifikate für alle deine Sites und hält sie erneuert. Es leitet HTTP außerdem automatisch zu HTTPS um. Caddy verwendet sichere und moderne Standardwerte; keine Downtime, zusätzliche Konfiguration oder separate Werkzeuge sind erforderlich.

<aside class="tip">
	Caddy hat automatic HTTPS-Technologie eingeführt; wir machen das seit dem ersten Tag, an dem es 2015 praktikabel war. Caddys HTTPS-Automatisierungslogik ist die ausgereifteste und robusteste der Welt.
</aside>

Hier ist ein 28-sekündiges Video, das zeigt, wie es funktioniert:

<iframe width="100%" height="480" src="https://www.youtube-nocookie.com/embed/nk4EWHvvZtI?rel=0" frameborder="0" allowfullscreen=""></iframe>


**Menü:**

- [Überblick](#overview)
- [Aktivierung](#activation)
- [Auswirkungen](#effects)
- [Hostname-Anforderungen](#hostname-requirements)
- [Local HTTPS](#local-https)
- [Testen](#testing)
- [ACME-Challenges](#acme-challenges)
- [On-Demand TLS](#on-demand-tls)
- [Fehler](#errors)
- [Storage](#storage)
- [Wildcard-Zertifikate](#wildcard-certificates)
- [Encrypted ClientHello (ECH)](#encrypted-clienthello-ech)



<a id="overview"></a>
## Überblick

**Standardmäßig liefert Caddy alle Sites über HTTPS aus.**

- Caddy liefert IP-Adressen und lokale/interne Hostnamen über HTTPS mit selbstsignierten Zertifikaten aus, denen lokal automatisch vertraut wird (wenn erlaubt).
	- Beispiele: `localhost`, `127.0.0.1`
- Caddy liefert öffentliche DNS-Namen über HTTPS mit Zertifikaten einer öffentlichen ACME CA wie [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) oder [ZeroSSL <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com) aus.
	- Beispiele: `example.com`, `sub.example.com`, `*.example.com`

Caddy hält alle verwalteten Zertifikate erneuert und leitet HTTP (Standardport `80`) automatisch zu HTTPS (Standardport `443`) um.

**Für Local HTTPS:**

- Caddy kann nach einem Passwort fragen, um sein eindeutiges Root-Zertifikat in deinem Trust Store zu installieren. Das passiert nur einmal pro Root; du kannst es jederzeit entfernen.
- Jeder Client, der auf die Site zugreift, ohne Caddys Root-CA-Zertifikat zu vertrauen, zeigt Sicherheitsfehler an.

**Für öffentliche Domainnamen:**

<aside class="tip">

Dies sind übliche Anforderungen für jede einfache Produktionswebsite, nicht nur für Caddy. Der Hauptunterschied ist, dass du deine DNS-Records **vor** dem Start von Caddy korrekt setzen solltest, damit Caddy Zertifikate provisionieren kann.

</aside>


- Wenn die A/AAAA-Records deiner Domain auf deinen Server zeigen,
- die Ports `80` und `443` extern offen sind,
- Caddy an diese Ports binden kann (*oder* diese Ports an Caddy weitergeleitet werden),
- dein [Datenverzeichnis](/docs/conventions#data-directory) beschreibbar und persistent ist,
- und dein Domainname irgendwo relevant in der config erscheint,

werden Sites automatisch über HTTPS ausgeliefert. Du musst nichts weiter dafür tun. Es funktioniert einfach.

Da HTTPS eine gemeinsame, öffentliche Infrastruktur nutzt, solltest du als Server-Admin die restlichen Informationen auf dieser Seite verstehen, damit du unnötige Probleme vermeidest, sie bei Auftreten beheben kannst und fortgeschrittene Deployments korrekt konfigurierst.



<a id="activation"></a>
## Aktivierung

Caddy aktiviert automatic HTTPS implizit, wenn es einen Domainnamen (d. h. Hostnamen) oder eine IP-Adresse kennt, die es bedient. Es gibt verschiedene Wege, Caddy deine Domain/IP mitzuteilen, je nachdem, wie du Caddy ausführst oder konfigurierst:

- Eine [Site-Adresse](/docs/caddyfile/concepts#addresses) im [Caddyfile](/docs/caddyfile)
- Ein [host matcher](/docs/json/apps/http/servers/routes/match/host/) auf oberster Ebene in den [JSON routes](/docs/modules/http#servers/routes)
- Kommandozeilenflags wie [`--domain`](/docs/command-line#caddy-file-server) oder [`--from`](/docs/command-line#caddy-reverse-proxy)
- Der Certificate Loader [automate](/docs/json/apps/tls/certificates/automate/)

Jedes der folgenden Dinge verhindert, dass automatic HTTPS ganz oder teilweise aktiviert wird:

- Explizites Deaktivieren [per JSON](/docs/json/apps/http/servers/automatic_https/) oder [per Caddyfile](/docs/caddyfile/options#auto-https)
- Keine Hostnamen oder IP-Adressen in der config angeben
- Ausschließlich auf dem HTTP-Port lauschen
- Der [Site-Adresse](/docs/caddyfile/concepts#addresses) im Caddyfile `http://` voranstellen
- Zertifikate manuell laden (außer [`ignore_loaded_certificates`](/docs/json/apps/http/servers/automatic_https/ignore_loaded_certificates/) ist gesetzt)

**Sonderfälle:**

- Domains, die auf `.ts.net` enden, werden nicht von Caddy verwaltet. Stattdessen versucht Caddy automatisch, diese Zertifikate zur Handshake-Zeit von der lokal laufenden [Tailscale <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com)-Instanz zu beziehen. Dafür muss [HTTPS in deinem Tailscale-Konto aktiviert sein <img src="/old/resources/images/external-link.svg" class="external-link">](https://tailscale.com/kb/1153/enabling-https/), und der Caddy-Prozess muss entweder als root laufen oder du musst `tailscaled` so konfigurieren, dass dein Caddy-Benutzer [Berechtigung zum Abrufen von Zertifikaten](https://github.com/caddyserver/caddy/pull/4541#issuecomment-1021568348) hat.


<a id="effects"></a>
## Auswirkungen

Wenn automatic HTTPS aktiviert wird, passiert Folgendes:

- Zertifikate werden für [alle qualifizierenden Domainnamen](#hostname-requirements) bezogen und erneuert
- HTTP wird zu HTTPS umgeleitet (dies verwendet [HTTP port](/docs/modules/http#http_port) `80`)

Automatic HTTPS überschreibt niemals explizite Konfiguration; es ergänzt sie nur.

Wenn du bereits einen [server](/docs/json/apps/http/servers/) hast, der auf dem HTTP-Port lauscht, werden die HTTP->HTTPS-Redirect-Routen nach deinen Routen mit host matcher eingefügt, aber vor einer benutzerdefinierten Catch-all-Route.

Du kannst [automatic HTTPS anpassen oder deaktivieren](/docs/json/apps/http/servers/automatic_https/), falls nötig; zum Beispiel kannst du bestimmte Domainnamen überspringen oder Redirects deaktivieren (im Caddyfile über [globale Optionen](/docs/caddyfile/options)).


<a id="hostname-requirements"></a>
## Hostname-Anforderungen

Alle Hostnamen (Domainnamen) qualifizieren sich für vollständig verwaltete Zertifikate, wenn sie:

- nicht leer sind
- nur aus alphanumerischen Zeichen, Bindestrichen, Punkten und Wildcard (`*`) bestehen
- nicht mit einem Punkt beginnen oder enden ([RFC 1034](https://tools.ietf.org/html/rfc1034#section-3.5))

Zusätzlich qualifizieren sich Hostnamen für öffentlich vertrauenswürdige Zertifikate, wenn sie:

- nicht localhost sind (einschließlich `.localhost`, `.local`, `.internal` und `.home.arpa` TLDs)
- keine IP-Adresse sind
- nur ein einzelnes Wildcard `*` als linkestes Label haben


<a id="local-https"></a>
## Local HTTPS

Caddy verwendet HTTPS automatisch für alle Sites mit angegebenem Host (Domain, IP oder Hostname), einschließlich interner und lokaler Hosts. Manche Hosts sind entweder nicht öffentlich (z. B. `127.0.0.1`, `localhost`) oder qualifizieren sich allgemein nicht für öffentlich vertrauenswürdige Zertifikate (z. B. IP-Adressen; man kann Zertifikate dafür bekommen, aber nur von manchen CAs). Sie werden trotzdem über HTTPS ausgeliefert, sofern dies nicht deaktiviert wird.

Um nicht-öffentliche Sites über HTTPS auszuliefern, erzeugt Caddy seine eigene Certificate Authority (CA) und verwendet sie zum Signieren von Zertifikaten. Die Vertrauenskette besteht aus einem Root- und einem Zwischenzertifikat. Leaf-Zertifikate werden vom Zwischenzertifikat signiert. Sie werden in [Caddys Datenverzeichnis](/docs/conventions#data-directory) unter `pki/authorities/local` gespeichert.

Caddys lokale CA wird von [Smallstep-Bibliotheken <img src="/old/resources/images/external-link.svg" class="external-link">](https://smallstep.com/certificates/) betrieben.

Local HTTPS verwendet kein ACME und führt keine DNS-Validierung durch. Es funktioniert nur auf der lokalen Maschine und wird nur dort vertraut, wo das Root-Zertifikat der CA installiert ist.

<a id="ca-root"></a>
### CA Root

Der private Schlüssel des Root wird eindeutig mit einer kryptographisch sicheren Pseudozufallsquelle erzeugt und mit eingeschränkten Berechtigungen im Storage persistiert. Er wird nur für Signieraufgaben in den Speicher geladen und verlässt danach den Scope, sodass er vom Garbage Collector erfasst werden kann.

Obwohl Caddy so konfiguriert werden kann, dass direkt mit dem Root signiert wird (zur Unterstützung nicht-konformer Clients), ist dies standardmäßig deaktiviert; der Root-Schlüssel wird nur zum Signieren von Zwischenzertifikaten verwendet.

Wenn ein Root-Schlüssel zum ersten Mal verwendet wird, versucht Caddy, ihn in den lokalen Trust Store bzw. die lokalen Trust Stores des Systems zu installieren. Wenn Caddy dafür keine Berechtigung hat, fragt es nach einem Passwort. Dieses Verhalten kann mit [`skip_install_trust` in einem Caddyfile](/docs/caddyfile/options#skip-install-trust) oder [`"install_trust": false` in einer JSON-config](/docs/json/apps/pki/certificate_authorities/install_trust/) deaktiviert werden. Wenn dies fehlschlägt, weil Caddy als unprivilegierter Benutzer läuft, kannst du [`caddy trust`](/docs/command-line#caddy-trust) ausführen, um die Installation als privilegierter Benutzer erneut zu versuchen.

<aside class="tip">
	Es ist sicher, Caddys Root-Zertifikat auf deiner eigenen Maschine zu vertrauen, solange dein Computer nicht kompromittiert ist und dein eindeutiger Root-Schlüssel nicht geleakt wurde.
</aside>

Nachdem Caddys Root-CA installiert ist, siehst du sie in deinem lokalen Trust Store als "Caddy Local Authority" (sofern du keinen anderen Namen konfiguriert hast). Du kannst sie jederzeit deinstallieren, wenn du möchtest (der Befehl [`caddy untrust`](/docs/command-line#caddy-untrust) macht das einfach).

Beachte, dass die automatische Installation des Zertifikats in lokale Trust Stores nur der Bequemlichkeit dient und nicht garantiert funktioniert, besonders wenn Container verwendet werden oder Caddy als unprivilegierter Systemdienst läuft. Wenn du dich auf interne PKI verlässt, liegt es letztlich in der Verantwortung des Systemadministrators sicherzustellen, dass Caddys Root-CA korrekt zu den nötigen Trust Stores hinzugefügt wird (das liegt außerhalb des Umfangs des Webservers).


<a id="ca-intermediates"></a>
### CA Intermediates

Ein Zwischenzertifikat und ein Schlüssel werden ebenfalls erzeugt; diese werden zum Signieren von Leaf-Zertifikaten (einzelnen Site-Zertifikaten) verwendet.

Anders als das Root-Zertifikat haben Zwischenzertifikate eine viel kürzere Lebensdauer und werden bei Bedarf automatisch erneuert.


<a id="testing"></a>
## Testen

Wenn du deine Caddy-Konfiguration testest oder damit experimentierst, stelle sicher, dass du [den ACME-Endpunkt](/docs/modules/tls.issuance.acme#ca) auf eine Staging- oder Development-URL änderst; andernfalls triffst du wahrscheinlich Rate Limits, die deinen HTTPS-Zugriff je nach betroffenem Limit bis zu einer Woche blockieren können.

Eine der Standard-CAs von Caddy ist [Let's Encrypt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/), das einen [Staging-Endpunkt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/) hat, der nicht denselben [Rate Limits <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/rate-limits/) unterliegt:

```
https://acme-staging-v02.api.letsencrypt.org/directory
```

<a id="acme-challenges"></a>
## ACME-Challenges

Das Beziehen eines öffentlich vertrauenswürdigen TLS-Zertifikats erfordert Validierung durch eine öffentlich vertrauenswürdige Drittpartei. Heutzutage wird dieser Validierungsprozess mit dem [ACME-Protokoll <img src="/old/resources/images/external-link.svg" class="external-link">](https://tools.ietf.org/html/rfc8555) automatisiert und kann auf eine von drei Arten ("challenge types") erfolgen, die unten beschrieben sind.

Die ersten beiden Challenge-Typen sind standardmäßig aktiviert. Wenn mehrere Challenges aktiviert sind, wählt Caddy zufällig eine aus, um versehentliche Abhängigkeit von einer bestimmten Challenge zu vermeiden. Mit der Zeit lernt es, welcher Challenge-Typ am erfolgreichsten ist, und bevorzugt diesen zuerst, fällt aber bei Bedarf auf andere verfügbare Challenge-Typen zurück.


<a id="http-challenge"></a>
### HTTP challenge

Die HTTP challenge führt einen autoritativen DNS-Lookup für den A/AAAA-Record des Kandidaten-Hostnamens aus und fordert dann über Port `80` per HTTP eine temporäre kryptographische Ressource an. Wenn die CA die erwartete Ressource sieht, wird ein Zertifikat ausgestellt.

Diese Challenge erfordert, dass Port `80` extern erreichbar ist. Wenn Caddy nicht auf Port 80 lauschen kann, müssen Pakete von Port `80` an Caddys [HTTP port](/docs/json/apps/http/http_port/) weitergeleitet werden.

Diese Challenge ist standardmäßig aktiviert und benötigt keine explizite Konfiguration.


<a id="tls-alpn-challenge"></a>
### TLS-ALPN challenge

Die TLS-ALPN challenge führt einen autoritativen DNS-Lookup für den A/AAAA-Record des Kandidaten-Hostnamens aus und fordert dann über Port `443` eine temporäre kryptographische Ressource mit einem TLS-Handshake an, der spezielle ServerName- und ALPN-Werte enthält. Wenn die CA die erwartete Ressource sieht, wird ein Zertifikat ausgestellt.

Diese Challenge erfordert, dass Port `443` extern erreichbar ist. Wenn Caddy nicht auf Port 443 lauschen kann, müssen Pakete von Port `443` an Caddys [HTTPS port](/docs/json/apps/http/https_port/) weitergeleitet werden.

Diese Challenge ist standardmäßig aktiviert und benötigt keine explizite Konfiguration.


<a id="dns-challenge"></a>
### DNS challenge

Die DNS challenge führt einen autoritativen DNS-Lookup für die `TXT`-Records des Kandidaten-Hostnamens aus und sucht nach einem speziellen `TXT`-Record mit einem bestimmten Wert. Wenn die CA den erwarteten Wert sieht, wird ein Zertifikat ausgestellt.

Diese Challenge benötigt keine offenen Ports, und der Server, der ein Zertifikat anfordert, muss nicht extern erreichbar sein. Die DNS challenge erfordert jedoch Konfiguration. Caddy muss die Zugangsdaten kennen, um auf den DNS-Provider deiner Domain zuzugreifen, damit es die speziellen `TXT`-Records setzen (und löschen) kann. Wenn die DNS challenge aktiviert ist, sind andere Challenges standardmäßig deaktiviert.

Da ACME CAs bei der Challenge-Verifikation DNS-Standards für `TXT`-Lookups befolgen, kannst du CNAME-Records verwenden, um die Beantwortung der Challenge an andere DNS-Zonen zu delegieren. Damit lässt sich die Subdomain `_acme-challenge` an [eine andere Zone](/docs/caddyfile/directives/tls#dns_challenge_override_domain) delegieren. Das ist besonders nützlich, wenn dein DNS-Provider keine API bereitstellt oder von keinem der DNS-Plugins für Caddy unterstützt wird.

DNS-Provider-Unterstützung ist Community-Arbeit. [Lerne in unserem Wiki, wie du die DNS challenge für deinen Provider aktivierst.](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148)


<a id="on-demand-tls"></a>
## On-Demand TLS

Caddy hat eine neue Technologie eingeführt, die wir **On-Demand TLS** nennen. Sie bezieht dynamisch ein neues Zertifikat während des ersten TLS-Handshakes, der es benötigt, statt bereits beim Laden der config. Entscheidend ist: Dafür müssen die Domainnamen **nicht** vorab fest in deiner Konfiguration eingetragen sein.

Viele Unternehmen verlassen sich auf dieses einzigartige Feature, um ihre TLS-Deployments kostengünstiger und ohne operative Kopfschmerzen zu skalieren, wenn sie zehntausende Sites bedienen.

On-demand TLS ist nützlich, wenn:

- du beim Starten oder Neuladen deines Servers nicht alle Domainnamen kennst,
- Domainnamen möglicherweise nicht sofort korrekt konfiguriert sind (DNS-Records noch nicht gesetzt),
- du die Domainnamen nicht kontrollierst (z. B. Kundendomains).

Wenn on-demand TLS aktiviert ist, musst du die Domainnamen nicht in deiner config angeben, um Zertifikate für sie zu erhalten. Stattdessen wird der Handshake angehalten, wenn ein TLS-Handshake für einen Servernamen (SNI) eingeht, für den Caddy noch kein Zertifikat hat, während Caddy ein Zertifikat bezieht, um den Handshake abzuschließen. Die Verzögerung beträgt normalerweise nur wenige Sekunden, und nur dieser erste Handshake ist langsam. Alle zukünftigen Handshakes sind schnell, weil Zertifikate gecacht und wiederverwendet werden und Erneuerungen im Hintergrund stattfinden. Zukünftige Handshakes können Wartung für das Zertifikat auslösen, um es erneuert zu halten, aber diese Wartung läuft im Hintergrund, wenn das Zertifikat noch nicht abgelaufen ist.

<a id="using-on-demand-tls"></a>
### On-Demand TLS verwenden

**On-demand TLS muss aktiviert und eingeschränkt werden, um Missbrauch zu verhindern.**

On-demand TLS wird in [TLS automation policies](/docs/json/apps/tls/automation/policies/) aktiviert, wenn du JSON-config verwendest, oder [in Site-Blöcken mit der Direktive `tls`](/docs/caddyfile/directives/tls), wenn du das Caddyfile verwendest.

Um Missbrauch dieses Features zu verhindern, musst du Einschränkungen konfigurieren. Das geschieht im [`automation`-Objekt der JSON-config](/docs/json/apps/tls/automation/on_demand/) oder in der globalen Caddyfile-Option [`on_demand_tls`](/docs/caddyfile/options#on-demand-tls). Einschränkungen sind "global" und können nicht pro Site oder pro Domain konfiguriert werden. Die wichtigste Einschränkung ist ein "ask"-Endpunkt, an den Caddy einen HTTP-Request sendet, um zu fragen, ob es ein Zertifikat für die Domain im Handshake beziehen und verwalten darf. Das bedeutet, du brauchst ein internes Backend, das zum Beispiel die Account-Tabelle deiner Datenbank abfragen und prüfen kann, ob ein Kunde sich mit diesem Domainnamen registriert hat.

Achte darauf, wie schnell deine CA Zertifikate ausstellen kann. Wenn das länger als wenige Sekunden dauert, beeinträchtigt es die Benutzererfahrung (nur für den ersten Client).

Wegen seiner verzögerten Natur und der zusätzlichen Konfiguration, die zur Missbrauchsverhinderung nötig ist, empfehlen wir, on-demand TLS nur zu aktivieren, wenn dein tatsächlicher Anwendungsfall oben beschrieben ist.

[Siehe unseren Wiki-Artikel für weitere Informationen zur effektiven Nutzung von on-demand TLS.](https://caddy.community/t/serving-tens-of-thousands-of-domains-over-https-with-caddy/11179)

<a id="errors"></a>
## Fehler

Caddy tut sein Bestes, um bei Fehlern im Zertifikatsmanagement weiterzumachen.

Standardmäßig läuft Zertifikatsmanagement im Hintergrund. Das bedeutet, es blockiert den Start nicht und verlangsamt deine Sites nicht. Es bedeutet aber auch, dass der Server schon läuft, bevor alle Zertifikate verfügbar sind. Im Hintergrund zu laufen erlaubt Caddy, über einen langen Zeitraum mit exponentiellem Backoff erneut zu versuchen.

Das passiert, wenn beim Beziehen oder Erneuern eines Zertifikats ein Fehler auftritt:

1. Caddy versucht es nach einer kurzen Pause einmal erneut, falls es nur ein Ausreißer war
2. Caddy pausiert kurz und wechselt dann zum nächsten aktivierten Challenge-Typ
3. Nachdem alle aktivierten Challenge-Typen versucht wurden, [versucht es den nächsten konfigurierten issuer](#issuer-fallback)
	- Let's Encrypt
	- ZeroSSL
4. Nachdem alle issuer versucht wurden, verwendet es exponentiellen Backoff
	- Maximal 1 Tag zwischen Versuchen
	- Bis zu 30 Tage lang

Während Retries mit Let's Encrypt wechselt Caddy zu deren [Staging-Umgebung <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/staging-environment/), um Rate-Limit-Probleme zu vermeiden. Das ist keine perfekte Strategie, aber im Allgemeinen hilfreich.

ACME-Challenges dauern mindestens einige Sekunden, und internes Rate Limiting hilft, versehentlichen Missbrauch zu reduzieren. Caddy verwendet internes Rate Limiting zusätzlich zu dem, was du oder die CA konfigurieren, sodass du Caddy eine Liste mit einer Million Domainnamen geben kannst und es nach und nach, aber so schnell wie möglich, Zertifikate für alle bezieht. Caddys internes Rate Limit beträgt derzeit 10 Versuche pro ACME-Account pro 10 Sekunden.

Um Ressourcenlecks zu vermeiden, bricht Caddy laufende Tasks (einschließlich ACME-Transaktionen) ab, wenn die config geändert wird. Obwohl Caddy häufige config-Reloads verarbeiten kann, solltest du solche betrieblichen Aspekte berücksichtigen und config-Änderungen bündeln, um Reloads zu reduzieren und Caddy die Chance zu geben, Zertifikate im Hintergrund tatsächlich fertig zu beziehen.

<a id="issuer-fallback"></a>
### Issuer fallback

Caddy ist der erste (und bisher einzige) Server, der vollständig redundantes, automatisches Failover zu anderen CAs unterstützt, falls ein Zertifikat nicht erfolgreich bezogen werden kann.

Standardmäßig aktiviert Caddy zwei ACME-kompatible CAs: [**Let's Encrypt** <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org) und [**ZeroSSL** <img src="/old/resources/images/external-link.svg" class="external-link">](https://zerossl.com). Wenn Caddy von Let's Encrypt kein Zertifikat bekommen kann, versucht es ZeroSSL; wenn beide fehlschlagen, verwendet es Backoff und versucht später erneut. In deiner config kannst du anpassen, welche issuer Caddy zum Beziehen von Zertifikaten verwendet, entweder allgemein oder für bestimmte Namen.


<a id="storage"></a>
## Storage

Caddy speichert öffentliche Zertifikate, private Schlüssel und andere Assets in seiner [konfigurierten Storage-Einrichtung](/docs/json/storage/) (oder im Standard, wenn keine konfiguriert ist; Details siehe Link).

**Das Wichtigste bei der Standard-config ist: Der Ordner `$HOME` muss beschreibbar und persistent sein.** Zur Fehlersuche gibt Caddy beim Start seine Umgebungsvariablen aus, wenn das Flag `--environ` angegeben ist.

Alle Caddy-Instanzen, die denselben Storage verwenden, teilen diese Ressourcen automatisch und koordinieren Zertifikatsmanagement als Cluster.

Vor ACME-Transaktionen testet Caddy den konfigurierten Storage, um sicherzustellen, dass er beschreibbar ist und genügend Kapazität hat. Das reduziert unnötige Lock Contention.


<a id="wildcard-certificates"></a>
## Wildcard-Zertifikate

Caddy kann Wildcard-Zertifikate beziehen und verwalten, wenn es so konfiguriert ist, dass es eine Site mit einem qualifizierenden Wildcard-Namen bedient. Ein Site-Name qualifiziert sich für eine Wildcard, wenn nur sein linkestes Domain-Label eine Wildcard ist. Zum Beispiel qualifiziert sich `*.example.com`, aber diese nicht: `sub.*.example.com`, `foo*.example.com`, `*bar.example.com` und `*.*.example.com`. (Das ist eine Einschränkung der WebPKI.)

Wenn du das Caddyfile verwendest, nimmt Caddy Site-Namen in Bezug auf Zertifikats-Subject-Namen wörtlich. Anders gesagt: Eine Site `sub.example.com` veranlasst Caddy, ein Zertifikat für `sub.example.com` zu verwalten, und eine Site `*.example.com` veranlasst Caddy, ein Wildcard-Zertifikat für `*.example.com` zu verwalten. Das wird auf unserer Seite [Common Caddyfile Patterns](/docs/caddyfile/patterns#wildcard-certificates) demonstriert. Wenn du anderes Verhalten brauchst, gibt dir die [JSON-config](/docs/json/) präzisere Kontrolle über Zertifikats-Subjects und Site-Namen ("host matchers").

Seit Caddy 2.10 verwendet Caddy beim Automatisieren eines Wildcard-Zertifikats das Wildcard-Zertifikat für einzelne Subdomains in der Konfiguration. Es bezieht keine Zertifikate für einzelne Subdomains, außer dies ist explizit so konfiguriert (z. B. mit `force_automate`).

Wildcard-Zertifikate repräsentieren einen hohen Grad an Autorität und sollten nur verwendet werden, wenn du so viele Subdomains hast, dass die Verwaltung einzelner Zertifikate die PKI belasten oder CA-erzwungene Rate Limits auslösen würde, oder wenn der Privacy-Tradeoff das Risiko wert ist, bei einem Schlüsselkompromiss so viel der DNS-Zone offenzulegen. Beachte, dass Wildcard-Zertifikate allein keine Privacy bieten, die spezifische Subdomains verbirgt: Sie werden weiterhin in TLS ClientHello-Paketen offengelegt, sofern Encrypted ClientHello (ECH) nicht aktiviert ist. (Siehe unten.)

**Hinweis:** [Let's Encrypt verlangt <img src="/old/resources/images/external-link.svg" class="external-link">](https://letsencrypt.org/docs/challenge-types/) die [DNS challenge](#dns-challenge), um Wildcard-Zertifikate zu beziehen.


<a id="encrypted-clienthello-ech"></a>
## Encrypted ClientHello (ECH)

Normalerweise senden TLS-Handshakes den ClientHello, einschließlich Server Name Indicator (SNI; die Domain, zu der verbunden wird), im Klartext. Das liegt daran, dass er die Parameter enthält, die für die Verschlüsselung der Verbindung nach dem Handshake nötig sind. Dadurch wird natürlich der Domainname, der sensibelste Teil des ClientHello, für jeden sichtbar, der Verbindungen belauschen kann, selbst wenn er nicht in deiner unmittelbaren physischen Nähe ist. Er verrät, mit welchem Dienst du dich verbindest, wenn die Ziel-IP viele verschiedene Sites bedienen kann, und so zensieren manche Regierungen das Internet.

Mit Encrypted ClientHello kann der Client den Domainnamen schützen, indem er den echten ClientHello in einen "äußeren" ClientHello einwickelt, der Parameter zum Entschlüsseln des "inneren" ClientHello herstellt. Viele bewegliche Teile müssen jedoch perfekt zusammenspielen, damit das funktioniert und echte Privacy-Vorteile bringt.

Zuerst muss der Client wissen, welche Parameter oder Konfiguration er zum Verschlüsseln des ClientHello verwenden soll. Diese Informationen enthalten unter anderem einen öffentlichen Schlüssel und eine "äußere" Domain (den "public name"). Diese Konfiguration muss irgendwie zuverlässig veröffentlicht oder verteilt werden.

Theoretisch könntest du sie auf ein Blatt Papier schreiben und an alle verteilen, aber die meisten großen Browser unterstützen das Nachschlagen von DNS-Records des Typs HTTPS, die ECH-Parameter enthalten, wenn sie sich mit einer Site verbinden. Daher musst du: (1) eine ECH-Konfiguration erzeugen (öffentliches/privates Schlüsselpaar und weitere Parameter) und dann (2) einen DNS-Record des Typs HTTPS erstellen, der die base64-kodierte ECH-Konfiguration enthält.

Oder ... du lässt Caddy all das für dich erledigen. Caddy ist der erste und einzige Webserver, der ECH-Konfigurationen automatisch erzeugen, veröffentlichen und bedienen kann.

Sobald der HTTPS-Record veröffentlicht ist, müssen Clients beim Verbinden mit deiner Site einen DNS-Lookup für den HTTPS-Record ausführen. Normalerweise sind DNS-Lookups Klartext, was die Sicherheit der resultierenden ECH-Handshakes beeinträchtigt; Browser müssen daher ein sicheres DNS-Protokoll wie DNS-over-HTTPS (DoH) oder DNS-over-TLS (DoT) verwenden. Je nach Browser muss dies manuell aktiviert werden.

Sobald der Client die ECH-config sicher heruntergeladen hat, verwendet er den eingebetteten öffentlichen Schlüssel, um den ClientHello zu verschlüsseln, und verbindet sich mit deiner Site. Caddy entschlüsselt dann den inneren ClientHello und bedient deine Site, ohne dass der Domainname jemals im Klartext über die Leitung erscheint.

<a id="deployment-considerations"></a>
### Deployment-Überlegungen

ECH ist eine nuancierte Technologie. Obwohl Caddy ECH vollständig automatisiert, müssen viele Dinge berücksichtigt werden, um maximale Privacy-Vorteile zu erreichen. Du solltest dir auch verschiedener Tradeoffs bewusst sein.

<a id="publication"></a>
#### Veröffentlichung

Caddy erstellt nur dann einen HTTPS-Record für eine Domain, wenn für diese Domain bereits ein Record existiert. Das verhindert, dass DNS-Lookups für eine Subdomain kaputtgehen, die möglicherweise von einer Wildcard abgedeckt wird. Stelle sicher, dass deine Sites mindestens einen A/AAAA-Record haben, der auf deinen Server zeigt. Wenn du nur eine Wildcard für DNS-Records verwendest, muss die Wildcard-Domain ebenfalls in deiner Caddy-config erscheinen.

Caddy veröffentlicht keinen HTTPS-Record für eine Domain, die einen CNAME-Record hat.

<a id="ech-grease"></a>
#### ECH GREASE

Wenn du Wireshark öffnest und dich dann in einer modernen Version eines großen Browsers wie Firefox oder Chrome mit irgendeiner Site verbindest (selbst mit einer, die ECH nicht unterstützt, und selbst mit deaktiviertem ECH), bemerkst du möglicherweise, dass der Handshake die Erweiterung `encrypted_client_hello` enthält:

![ECH GREASE](/resources/images/ech-grease.png)

Der Zweck ist, echte ECH-Handshakes von Klartext-Handshakes ununterscheidbar zu machen. Wenn ECH-Handshakes anders aussähen als normale, könnten Zensoren ECH-Handshakes mit minimalem Kollateralschaden blockieren. Wenn sie aber jeden Handshake mit einer plausiblen ECH-Erweiterung blockieren würden, würden sie im Wesentlichen den Großteil des Internets abschalten. (Ziel ist, die Kosten breit angelegter Zensur zu erhöhen.)

Das ist vor allem bei der Fehlersuche an Verbindungen wichtig.

<a id="key-rotation"></a>
#### Schlüsselrotation

Wie bei Zertifikatsschlüsseln ist es keine gute Praxis (und kann direkt unsicher sein), denselben Schlüssel lange zu verwenden. ECH-Schlüssel sollten daher regelmäßig rotiert werden. Anders als Zertifikate laufen ECH-configs nicht strikt ab. Server sollten sie trotzdem rotieren.

Schlüsselrotation ist jedoch schwierig, weil Clients von den aktualisierten Schlüsseln wissen müssen. Wenn der Server alte Schlüssel einfach durch neue ersetzt, würden alle ECH-Handshakes fehlschlagen, sofern Clients nicht sofort über die neuen Schlüssel informiert werden. Aber die aktualisierten Schlüssel einfach zu veröffentlichen reicht nicht. DNS-Records haben TTLs, Resolver cachen Antworten usw. Es kann Minuten, Stunden oder sogar Tage dauern, bis Clients die aktualisierten HTTPS-Records abfragen und die neue ECH-config verwenden.

Aus diesem Grund sollten Server alte ECH-configs für eine gewisse Zeit weiter unterstützen. Andernfalls besteht das Risiko, Servernamen *in großem Maßstab* im Klartext offenzulegen. Caddy rotiert Schlüssel gelegentlich und unterstützt rotierte Schlüssel eine Zeit lang, bis sie schließlich verworfen werden.

Das reicht jedoch möglicherweise nicht. Manche Clients erhalten aus verschiedenen Gründen die aktualisierten Schlüssel trotzdem nicht, und jedes Mal besteht das Risiko, den Servernamen offenzulegen. Daher braucht es einen anderen Weg, Clients die aktualisierte config *in band* mit der Verbindung zu geben. Dafür ist der *outer name* (oder *public name*) da.

<a id="public-name"></a>
#### Public name

Der "äußere" ClientHello ist ein normaler ClientHello mit zwei subtilen Unterschieden, die nur dem Origin-Server bekannt sind:

1. Die SNI-Erweiterung ist gefälscht
2. Die ECH-Erweiterung ist echt

Diese "äußere" SNI-Erweiterung enthält den public name, der deine echten Domains schützt. Dieser Name kann alles sein, aber **dein Server muss für den public name autoritativ sein**, weil Caddy *ein Zertifikat dafür beziehen wird*.

Wenn ein Client versucht, eine ECH-Verbindung herzustellen, der Server den inneren ClientHello aber nicht entschlüsseln kann, kann er den Handshake tatsächlich mit dem *äußeren* ClientHello und einem Zertifikat für den outer name abschließen. Diese sichere Verbindung wird strikt *nur* verwendet, um dem Client die aktuelle ECH-config zu senden; sie ist also eine temporäre TLS-Verbindung allein zum Zweck, die initiale TLS-Verbindung abzuschließen. Es werden keine Anwendungsdaten übertragen: nur der ECH-Schlüssel. Sobald der Client den aktualisierten Schlüssel hat, kann er die TLS-Verbindung wie vorgesehen herstellen.

Auf diese Weise bleibt der echte Servername geschützt, und Clients mit veralteten Daten können weiterhin verbinden; beides sind wichtige Elemente der Sicherheit.

Der outer name kann eine Domain deiner Site, eine Subdomain oder irgendein anderer Domainname sein, der auf deinen Server zeigt. Wir empfehlen, genau einen generischen Namen zu wählen. Cloudflare bedient zum Beispiel Millionen von Sites hinter `cloudflare-ech.com`. Das ist wichtig, um die Größe deines Anonymity Set zu erhöhen.

Public names sollten nicht leer sein; d. h. ein public name muss konfiguriert sein, damit die Dinge funktionieren. Caddy erzwingt das derzeit nicht (möglicherweise später), aber die ECH-Spezifikation verlangt, dass der public name mindestens 1 Byte lang ist. Manche Software akzeptiert leere Namen, andere nicht. Das kann zu verwirrendem Verhalten führen, etwa dass Browser ECH verwenden, Server es aber als ungültig ablehnen; oder Browser ECH nicht verwenden (weil es ungültig ist), obwohl die config korrekt im DNS-Record steht. Es liegt in der Verantwortung des Site-Betreibers, korrekte ECH-Konfiguration und Veröffentlichung sicherzustellen, um Privacy zu gewährleisten.


<a id="anonymity-set"></a>
#### Anonymity set

Um die Privacy-Vorteile von ECH zu maximieren, solltest du die Größe deines *Anonymity Set* maximieren. Im Kern besteht dieses Set aus clientseitig sichtbaren Servern, die für Beobachter identisches Verhalten haben. Die Idee ist, dass ein Beobachter die möglichen Sites oder Dienste, mit denen Clients sich verbinden, nicht leicht reduzieren oder ableiten kann.

In der Praxis empfehlen wir, nur einen public name für alle deine Sites zu haben. (Es gibt nur 1 public name pro ECH-config, was impliziert, dass zu jedem Zeitpunkt nur 1 aktive ECH-config existiert.) Wenn du Caddy in einem Cluster betreibst, teilt und koordiniert Caddy ECH-configs automatisch mit anderen Instanzen, was dies für dich erledigt.

Extrem gedacht impliziert das, dass jede Site im Internet hinter einer einzigen IP-Adresse und einem public name stehen könnte oder sollte ...


<a id="centralization"></a>
#### Zentralisierung

... was uns zum nächsten Thema bringt: Zentralisierung. Eine Kritik an ECH ist, dass es tendenziell Zentralisierung motiviert. Das geschieht auf mindestens zwei Arten: (1) indem Clients DoH/DoT für DNS-Lookups bevorzugen, wodurch alle DNS-Lookups durch eine kleine Handvoll Anbieter laufen, und (2) indem die Größe des Anonymity Set im großen Maßstab maximiert wird.

Wenn DoH oder DoT verwendet wird, laufen DNS-Lookups alle über den DoH/DoT-Provider. Zwischen Client und Provider sind die DNS-Daten verschlüsselt, aber zwischen Provider und DNS-Server nicht. Globales DoH/DoT kanalisiert effektiv all den wertvollen Klartext-DNS-Traffic in wenige große Leitungen, die reif für Beobachtung ... oder Ausfall sind.

Ähnlich gilt: Wenn wir das Anonymity Set wirklich im großen Maßstab maximieren, wären alle Sites hinter einem einzigen public name wie `cloudflare-ech.com` geschützt. Das ist gut für Privacy, aber dann ist das gesamte Internet Cloudflare und diesem einen Domainnamen ausgeliefert. Eine Maximierung in diesem Ausmaß ist nicht notwendig oder praktisch, aber die theoretischen Implikationen bleiben gültig.

Wir empfehlen jeder Organisation oder Einzelperson, einen einzigen Namen für alle ihre Sites zu wählen und diesen zu verwenden; in den meisten Fällen sollte das ausreichende Privacy bieten. Bitte konsultiere jedoch Experten zu deinen individuellen Threat Models für deinen konkreten Fall.


<a id="subdomain-privacy"></a>
#### Subdomain-Privacy

Mit ECH ist es theoretisch möglich, Subdomains vor Side Channels geheim/privat zu halten, wenn es korrekt deployed wird.

Die meisten Sites brauchen das nicht, da Subdomains allgemein öffentliche Informationen sind. Wir raten davon ab, sensible Informationen in Domainnamen zu platzieren. Trotzdem ...

Um sensible Subdomains nicht in Certificate Transparency (CT)-Logs zu leaken, verwende stattdessen ein Wildcard-Zertifikat. Anders gesagt: Statt `sub.example.com` in deine config zu schreiben, schreibe `*.example.com`. (Siehe [Wildcard-Zertifikate](#wildcard-certificates) für wichtige Informationen.)

Eine weitere Leak-Quelle ist DNSSEC, das die meisten autoritativen DNS-Server standardmäßig verwenden. Durch eine Praxis namens "zone walking" ist Subdomain-Enumeration möglich, indem man NSEC-Records betrachtet, die zur authentifizierten Bestätigung der Nichtexistenz verwendet werden. Dafür zeigen sie auf die nächste verfügbare Subdomain in alphabetischer Reihenfolge und bilden eine verkettete Liste aller Records. Stelle sicher, dass deine Domain mindestens NSEC3 oder idealerweise einen Wildcard-CNAME-Record verwendet, um dies abzumildern.

Aktiviere dann ECH in Caddy. Ein Wildcard-Zertifikat kombiniert mit ECH und einem Wildcard-CNAME-Record sollte Subdomains korrekt verbergen, solange jeder Client, der sich verbinden will, ECH verwendet und eine starke Implementierung hat. (Du bist weiterhin darauf angewiesen, dass Clients Privacy bewahren.)


<a id="enabling-ech"></a>
### ECH aktivieren

Da funktionierendes ECH das Veröffentlichen von configs in DNS-Records erfordert, brauchst du einen Caddy-Build mit einem eingebundenen [caddy-dns module](https://github.com/caddy-dns) für deinen DNS-Provider.

Gib dann mit einem Caddyfile deine DNS-Provider-config in den globalen Optionen an, ebenso den ECH public name, den du verwenden möchtest:

```caddy
{
	dns <provider config...>
	ech example.com
}
```

Beachte:

- Das DNS-Provider-Modul muss eingebunden sein, und du musst die richtige Konfiguration für deinen Provider/Account haben.
- Der ECH public name sollte auf deinen Server zeigen. Caddy wird ein Zertifikat dafür beziehen. Er muss keine der Domains deiner Site sein.

Wenn du JSON verwendest, füge diese Eigenschaften zur `tls`-App hinzu:

```json
"encrypted_client_hello": {
	"configs": [
		{
			"public_name": "example.com"
		}
	]
},
"dns": {
	"name": "<provider name>",
	// provider configuration
}
```

Diese Konfigurationen aktivieren ECH und veröffentlichen ECH-configs für alle deine Sites. Die JSON-config bietet mehr Flexibilität, wenn du das Verhalten anpassen musst oder ein fortgeschrittenes Setup hast.

<a id="verifying-ech"></a>
### ECH verifizieren

Es gibt noch nicht viel Tooling rund um ECH; zum Zeitpunkt des Schreibens ist die beste und universellste Methode zur Prüfung, ob es funktioniert, Wireshark zu verwenden und im ServerName-Feld nach deinem public name zu suchen.

Starte zuerst deinen Server und prüfe, dass die Logs etwas wie "published ECH configuration list" für deine Domains erwähnen. (Wenn du Fehler bei der Veröffentlichung bekommst, stelle sicher, dass dein DNS-Provider-Modul [libdns 1.0](https://github.com/libdns/libdns) unterstützt, und öffne ein Issue im Repository deines Providers, falls Probleme auftreten.) Caddy sollte auch ein Zertifikat für den public name beziehen.

Stelle als Nächstes sicher, dass dein Browser ECH aktiviert hat; das kann erfordern, DoH/DoT zu aktivieren. Es ist außerdem sinnvoll, den DNS-Cache deines Browsers (oder Systems) zu leeren, damit er die neu veröffentlichten HTTPS-Records übernimmt. Wir empfehlen außerdem, den Browser zu schließen oder zumindest einen neuen privaten Tab zu öffnen, um sicherzustellen, dass keine bestehenden Verbindungen wiederverwendet werden.

Öffne dann Wireshark und lausche auf dem passenden Netzwerkinterface. Während Wireshark Pakete sammelt, lade deine Site im Browser. Danach kannst du Wireshark pausieren. Finde deinen TLS ClientHello; du solltest im ServerName-Feld den *public name* sehen statt des tatsächlichen Domainnamens, mit dem du dich verbunden hast.

Denke daran: Du kannst weiterhin eine `encrypted_client_hello`-Erweiterung sehen, selbst wenn ECH nicht verwendet wird. Der entscheidende Indikator ist der SNI-Wert. Wenn ECH korrekt funktioniert, solltest du den echten Site-Namen nie im Klartext in Wireshark sehen.

Wenn du Deployment-Probleme mit ECH hast, frage zuerst in unserem [Forum](https://caddy.community). Wenn es ein Bug ist, kannst du auf GitHub [ein Issue öffnen](https://github.com/caddyserver/caddy/issues).


<a id="ech-in-storage"></a>
### ECH im Storage

ECH-Konfigurationen werden im [Datenverzeichnis](/docs/conventions#data-directory) im konfigurierten Storage-Modul (Standard ist das Dateisystem) unter dem Ordner `ech/configs` gespeichert.

Der nächste Ordner ist eine ECH-config-ID, die zufällig erzeugt wird und relativ unwichtig ist. Die Zufälligkeit wird von der Spezifikation empfohlen, um Fingerprinting/Tracking abzumildern.

Eine Metadaten-Sidecar-Datei hilft Caddy nachzuverfolgen, wann Veröffentlichungen zuletzt stattgefunden haben. Das verhindert, dass dein DNS-Provider bei jedem config-Reload gehämmert wird. Wenn du diesen Zustand zurücksetzen musst, kannst du die Metadaten-Datei sicher löschen. Dies kann jedoch auch den Zeitpunkt zurücksetzen, zu dem der Schlüssel rotiert wird. Du kannst auch in die Datei gehen und nur die Informationen zur Veröffentlichung löschen.
