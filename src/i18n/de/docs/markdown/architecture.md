---
title: Architektur
---

Architektur
============

Caddy ist eine einzelne, eigenständige, statische Binärdatei ohne externe Abhängigkeiten, da sie in Go geschrieben ist. Diese Werte sind wichtige Bestandteile der Projektvision, da sie die Bereitstellung vereinfachen und die langwierige Fehlerbehebung in Produktionsumgebungen reduzieren.

Wenn es keine dynamische Verknüpfung gibt, wie kann sie dann erweitert werden? Caddy verfügt über eine neuartige Plugin-Architektur, die ihre Fähigkeiten weit über die aller anderen Webserver hinaus erweitert, selbst wenn diese über externe (dynamisch verknüpfte) Abhängigkeiten verfügen.

Unsere Philosophie „weniger bewegliche Teile“ führt letztendlich zu zuverlässigeren, besser verwaltbaren und kostengünstigeren Standorten, insbesondere im großen Maßstab. Dieses halbtechnische Dokument beschreibt, wie wir dieses Ziel durch Software-Engineering erreichen.


<a id="overview"></a>
## Überblick

Caddy besteht aus einem Befehl, einer Kernbibliothek und Modulen.

Der **Befehl** stellt die [Befehlszeilenschnittstelle](/docs/command-line) bereit, mit der Sie hoffentlich vertraut sind. Auf diese Weise starten Sie den Prozess von Ihrem Betriebssystem aus. Der Umfang an Code und Logik ist hier relativ gering und enthält nur das, was zum Bootstrapping des Kerns auf die vom Benutzer gewünschte Weise erforderlich ist. Wir vermeiden absichtlich die Verwendung von Flags und Umgebungsvariablen für die Konfiguration, es sei denn, sie beziehen sich auf die Bootstrapping-Konfiguration.


<aside class="tip">

Module können der Befehlszeilenschnittstelle Unterbefehle hinzufügen! Daher kommt beispielsweise der Befehl [`caddy file-server`](/docs/command-line#caddy-file-server). Diese hinzugefügten Befehle können beliebige Flags haben oder beliebige Umgebungsvariablen verwenden, auch wenn die Kernbefehle Caddy deren Verwendung minimieren.

</aside>


Die **[Kernbibliothek](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc)** oder „Kern“ von Caddy verwaltet hauptsächlich die Konfiguration. Es kann [`Run()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Run) eine neue Konfiguration oder [`Stop()`](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Stop) eine laufende Konfiguration sein. Es stellt außerdem verschiedene Dienstprogramme, Typen und Werte für die Verwendung von Modulen bereit.

**Module** erledigen alles andere. In Caddy sind viele Module integriert, die als *Standardmodule* bezeichnet werden. Es wird festgestellt, dass diese für die meisten Benutzer am nützlichsten sind.


<aside class="tip">

Manchmal werden die Begriffe *Modul*, *Plugin* und *Erweiterung* synonym verwendet, und normalerweise ist das in Ordnung. Technisch gesehen sind alle Module Plugins, aber nicht alle Plugins sind Module. Module sind speziell eine Art Plugin, das die [Konfigurationsstruktur](/docs/json/) von Caddy erweitert.

</aside>




## Caddy-Kern

Im Kern lädt Caddy lediglich eine Anfangskonfiguration („config“) oder öffnet, falls noch keine vorhanden ist, einen Socket, um später eine neue Konfiguration zu akzeptieren.

Eine [Caddy-Konfiguration](/docs/json/) ist ein JSON-Dokument mit einigen Feldern auf der obersten Ebene:

```json
{
	"admin": {},
	"logging": {},
	"apps": {•••},
	...
}
```

Der Kern von Caddy weiß, wie man mit einigen dieser Felder nativ arbeitet:

- [`admin`](/docs/json/admin/), damit der [Administrator API](/docs/api) eingerichtet und der Prozess verwaltet werden kann
- [`logging`](/docs/json/logging/), damit es [Protokolle ausgeben kann](/docs/logging)

Aber andere Felder der obersten Ebene (wie [`apps`](/docs/json/apps/)) sind für den Kern von Caddy undurchsichtig. Tatsächlich weiß Caddy nur, dass es mit den Bytes in `apps` zu tun hat, sie in einen Schnittstellentyp zu deserialisieren, auf dem zwei Methoden aufgerufen werden können:

1. `Start()`
2. `Stop()`

... und das war's. Es ruft `Start()` für jede App auf, wenn eine Konfiguration geladen wird, und `Stop()` für jede App, wenn eine Konfiguration entladen wird.

Wenn ein App-Modul gestartet wird, wird der Modullebenszyklus der App initiiert.


<aside class="tip">

Wenn Sie ein Programmierer sind, der Caddy-Module erstellt, finden Sie analoge Informationen in unserem Leitfaden [Extending Caddy](/docs/extending-caddy), jedoch mit mehr Fokus auf Code.

</aside>


## Modullebenszyklus

Es gibt zwei Arten von Modulen: *Host-Module* und *Gast-Module*.

**Hostmodule** (oder „übergeordnete“ Module) sind solche, die andere Module laden.

**Gastmodule** (oder „untergeordnete“ Module) werden geladen. Alle Module sind Gastmodule – auch App-Module.

Module werden geladen, bereitgestellt und validiert, verwendet und dann bereinigt, und zwar in dieser Reihenfolge:

1. Geladen
2. Bereitgestellt und validiert
3. Gebraucht
4. Aufgeräumt

Caddy startet den Modullebenszyklus, wenn eine Konfiguration zuerst geladen wird, indem alle konfigurierten App-Module initialisiert werden. Von da an geht es rasant weiter, während jedes App-Modul den Rest des Weges zurücklegt.

### Ladephase

Das Laden eines Moduls beinhaltet die Deserialisierung seiner JSON-Bytes in einen typisierten Wert im Speicher. Das ist es... im Grunde. Es geht lediglich darum, JSON in einen Wert zu dekodieren.

### Bereitstellungsphase

In dieser Phase findet der Großteil der Einrichtungsarbeit statt. Alle Module erhalten die Möglichkeit, sich nach dem Laden selbst bereitzustellen.

Da alle Eigenschaften aus der JSON-Kodierung bereits dekodiert wurden, müssen hier nur noch zusätzliche Einstellungen vorgenommen werden. Die häufigste Aufgabe während der Bereitstellung ist das Einrichten von Gastmodulen. Mit anderen Worten: Die Bereitstellung eines Host-Moduls führt auch zur Bereitstellung seiner Gastmodule, und zwar bis ganz nach unten.

Sie können sich ein Bild davon machen, indem Sie [die JSON-Struktur von Caddy in unseren Dokumenten durchlaufen](/docs/json/). Überall dort, wo Sie `{•••}` sehen, können Gastmodule verwendet werden; und wenn Sie auf eines klicken, können Sie die Erkundung ganz nach unten fortsetzen, bis keine Gastmodule mehr vorhanden sind.

Weitere häufige Bereitstellungsaufgaben sind das Einrichten interner Werte, die während der Lebensdauer des Moduls verwendet werden, oder das Standardisieren von Eingaben. Beispielsweise verwendet das Modul [`http.matchers.remote_ip`](/docs/modules/http.matchers.remote_ip) die Bereitstellungsphase, um CIDR-Werte aus den Zeichenfolgeneingaben zu analysieren, die es vom JSON erhalten hat. Auf diese Weise muss es dies nicht bei jeder HTTP-Anfrage tun und ist dadurch effizienter.

Die Validierung kann auch in der Bereitstellungsphase erfolgen. Wenn die resultierende Konfiguration eines Moduls ungültig ist, kann hier ein error zurückgegeben werden, der den gesamten Konfigurationsladevorgang abbricht.

### Nutzungsphase

Sobald ein Gastmodul bereitgestellt und validiert wurde, kann es von seinem Hostmodul verwendet werden. Was genau das bedeutet, ist jedem Hostmodul selbst überlassen.

Jedes Modul verfügt über eine ID, die aus einem Namespace und einem Namen in diesem Namespace besteht. Beispielsweise ist [`http.handlers.reverse_proxy`](/docs/modules/http.handlers.reverse_proxy) ein HTTP handler, da es sich im Namespace `http.handlers` befindet und der Name `reverse_proxy` ist. Alle Module im `http.handlers`-Namespace erfüllen dieselbe Schnittstelle, die dem Hostmodul bekannt ist. Somit weiß die `http`-App, wie man solche Module lädt und verwendet.

<a id="cleanup-phase"></a>
### Aufräumphase

Wenn es Zeit ist, eine Konfiguration zu stoppen, werden alle Module entladen. Wenn ein Modul Ressourcen zugewiesen hat, die freigegeben werden sollten, hat es in der Bereinigungsphase die Möglichkeit, dies zu tun.


## Einstecken

Ein Modul – oder ein beliebiges Caddy-Plugin – wird an Caddy „angeschlossen“, indem ein `import` für das Modulpaket hinzugefügt wird. Durch den Import des Pakets registriert sich [das Modul] (https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#RegisterModule) beim Caddy-Kern, sodass es beim Start des Caddy-Prozesses jedes Modul mit Namen kennt. Es kann sogar Modulwerte und -namen verknüpfen und umgekehrt.


<aside class="tip">

Plugins können hinzugefügt werden, ohne die Caddy-Codebasis überhaupt zu ändern. Anweisungen dazu gibt es [in der Readme-Datei](https://github.com/caddyserver/caddy/#with-version-information-andor-plugins)!

</aside>


## Konfiguration verwalten

Das Ändern der aktiven Konfiguration eines laufenden Servers (oft als „Neuladen“ bezeichnet) kann aufgrund des hohen Parallelitätsgrads und der Tausenden von Parametern, die Server benötigen, schwierig sein. Caddy löst dieses Problem elegant durch ein Design, das viele Vorteile bietet:

- Keine Unterbrechung der laufenden Dienste
- Granulare Konfigurationsänderungen sind möglich
- Nur eine Sperre erforderlich (im Hintergrund)
- Alle Nachladungen sind atomar, konsistent, isoliert und größtenteils dauerhaft („ACID“)
- Minimaler globaler Zustand

Sie können [hier ein Video über das Design von Caddy 2 ansehen](https://www.youtube.com/watch?v=EhJO8giOqQs).

Bei einem Neuladen der Konfiguration werden die neuen Module bereitgestellt. Wenn alle erfolgreich sind, werden die alten bereinigt. Für kurze Zeit sind zwei Konfigurationen gleichzeitig betriebsbereit.

Jeder Konfiguration ist ein [Kontext](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#Context) zugeordnet, der den gesamten Modulstatus enthält, sodass die meisten Status niemals den Gültigkeitsbereich einer Konfiguration verlassen. Das sind gute Nachrichten für Korrektheit, Leistung und Einfachheit!

Manchmal ist jedoch ein wirklich globaler Staat notwendig. Beispielsweise kann der Reverse-Proxy den Zustand seiner Upstreams verfolgen; Da es global nur einen upstream gibt, wäre es schlecht, wenn er sie bei jeder geringfügigen Konfigurationsänderung vergessen würde. Glücklicherweise bietet Caddy [Funktionen](https://pkg.go.dev/github.com/caddyserver/caddy/v2?tab=doc#UsagePool), die dem Garbage Collector einer Sprachlaufzeit ähneln, um den globalen Zustand aufgeräumt zu halten.

Ein offensichtlicher Ansatz für Online-Konfigurationsaktualisierungen besteht darin, den Zugriff auf jeden einzelnen Konfigurationsparameter zu synchronisieren, auch in Hot Paths. Das ist unglaublich schlecht in Bezug auf Leistung und Komplexität&mdash;insbesondere im Maßstab&mdash;also verwendet Caddy diesen Ansatz nicht.

Stattdessen werden Konfigurationen als unveränderliche, atomare Einheiten behandelt: Entweder wird das Ganze ersetzt, oder es wird nichts geändert. Die [Admin-API-Endpunkte](/docs/api)&mdash;die granulare Änderungen durch Durchquerung in die Struktur ermöglichen&mdash;mutieren nur eine In-Memory-Darstellung der Konfiguration, aus der ein völlig neues Konfigurationsdokument generiert und geladen wird. Dieser Ansatz bietet enorme Vorteile in Bezug auf Einfachheit, Leistung und Konsistenz. Da es nur eine Sperre gibt, ist es für Caddy einfach, schnelle Nachladevorgänge zu verarbeiten.

