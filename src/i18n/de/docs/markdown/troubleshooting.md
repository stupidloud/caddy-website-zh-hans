Fehlerbehebungsstrategien
=========================

Diese Seite stellt einen allgemeinen, methodischen Rahmen vor, mit dem du die meisten Probleme, die dir bei der Verwendung von Caddy begegnen können, selbst beheben kannst, *ohne KI zu verwenden*. Wir empfehlen ähnliche Schritte, wenn du in unseren Foren um Hilfe bittest. In vielen Fällen kannst du deine eigene Frage beantworten oder dein Problem lösen, indem du kritisch denkst.


Was weißt du?
-------------

Vielleicht weißt du nicht, was das Problem ist, wodurch es verursacht wird oder wie du es behebst. Beginnen wir also mit einigen grundlegenden Dingen, die du sicher weißt:

### Was du erwartest

Sprich es laut aus, denke es klar durch oder schreibe es auf. Sei eindeutig und konkret, damit kein Zweifel und kein Interpretationsspielraum bleibt. Du kannst dir sogar selbst erklären, *warum* du genau das erwartest.

„Es sollte funktionieren“ ist keine gute Erwartung.

„Ich erwarte eine 301-Weiterleitung, wenn ich eine Anfrage an diese URI stelle“ ist deutlich besser.


### Aktuelles Verhalten

Beobachte, was passiert. Was passiert *genau*, und wie unterscheidet es sich von deiner Erwartung? Fasse zusammen, was du weißt.

„Es funktioniert nicht“ ist wenig hilfreich und nachlässig; vermeide diese Formulierung überall, außer vielleicht als Kurzbeschreibung für ein konkretes Verhalten, das bereits im Detail dokumentiert wurde.

„Statt einer 301-Antwort bekomme ich eine 200-Antwort, obwohl ich den Header `Server: Caddy` sehe“ ist viel besser, weil es vergleicht, was du weißt und was du erwartest, und andere bekannte Informationen einbezieht. Das sagt uns, dass die Anfrage zumindest eine Caddy-Instanz erreicht.


### Logs

Was steht in Caddys Logs? Standardmäßig werden sie in das Terminal geschrieben, das den Prozess gestartet hat. Wenn Caddy „detached“, etwa als Systemdienst, läuft, musst du die Logs möglicherweise an anderer Stelle abrufen.

Beachte, dass HTTP-Request-Logs („access logs“) sich von Prozess-Logs unterscheiden und in deiner Konfiguration ausdrücklich aktiviert werden müssen.

Vielleicht möchtest du auch Logging auf DEBUG-Ebene aktivieren, falls du das noch nicht getan hast.

In jedem Fall ist eines der ersten Dinge, die du tun solltest: Schau in die Logs. *In alle.* Kontext ist bei Logmeldungen wichtig, deshalb ist eine einzelne Logzeile isoliert selten nützlich. Sammle mehr, als du glaubst zu brauchen, und bewahre es während der Fehlerbehebung auf.

Gibt es Hinweise in den Logs?


Annahmen erkennen und anzweifeln
--------------------------------

Bevor wir weitergehen, müssen wir betonen, wie entscheidend es ist, die eigenen Annahmen zu hinterfragen. Wir alle treffen Annahmen auf Basis dessen, was wir gewohnt sind und was wir erwarten. „Achte auf deine Annahmen, und groß wird deine Macht sein.“ (&mdash;Yoda, oder so ähnlich.)

Eine häufige Annahme ist zum Beispiel, dass nach dem Neukompilieren von Caddy das Ausführen von `caddy` den neuen Code startet. Das stimmt nur, wenn dein kompiliertes Binary dasjenige in deinem `$PATH` ersetzt hat. Meist ist stattdessen `./caddy` der richtige Aufruf.

Annahmen stapeln sich, wenn Deployment oder Konfiguration komplexer werden. Ein Deployment in Docker beinhaltet zum Beispiel, ein Image neu zu bauen und auszuführen, wodurch sich die möglichen Annahmen vervielfachen.

Viele Fragen und Bug Reports erweisen sich am Ende als Probleme mit externen System- und Netzwerkkonfigurationen, nicht mit Caddy selbst. Wenn du dich zum Beispiel nicht mit deiner Caddy-Instanz verbinden kannst, Caddy aber eindeutig läuft, nimmst du wahrscheinlich an, dass es nicht DNS ist. Hinweis: Es ist fast immer DNS.

Schon die Annahme, dass du eine Konfiguration neu geladen hast, obwohl du es tatsächlich nicht getan hast, ist ein häufiger Fehler. Sei streng mit deinem Prozess. Prüfe auf jeder Ebene.


Verhalten reproduzieren
-----------------------

Das ist ein wichtiger Schritt, bei dem sich Probleme oft von selbst lösen: Sorge dafür, dass das Problem erneut auftritt.

Genauer: Sorge dafür, dass es *auf die minimal mögliche Weise* erneut auftritt. Entferne unnötige Konfiguration, Deployment-Schritte, Umgebungsfaktoren usw., bis das Problem verschwindet.

Eine gängige Strategie ist, jeweils nur eine Sache zu entfernen und erneut zu testen, bis das Problem verschwindet. Dann ist diese entfernte Sache wahrscheinlich die Ursache, oder&mdash;und hier lohnt es sich, Annahmen anzuzweifeln&mdash;eine Kombination aus dieser letzten Sache und etwas, das du zuvor entfernt hast, ist die Ursache. Verifiziere das, indem du die zuerst entfernten Dinge wieder hinzufügst. Grenze es ein.

Eine andere Idee ist, in jeder Iteration ungefähr die Hälfte von allem zu entfernen. Sobald das Problem verschwindet, entfernst du wiederum nur die Hälfte dieser Hälfte und so weiter. Das ähnelt einer binären Suche und kann schneller sein.

Alternativ kannst du diese Strategien statt durch Eliminierung auch umkehren und deine Konfiguration oder dein Szenario schrittweise von Grund auf aufbauen, jedes Mal erneut testen, bis das Problem erscheint.

Oft identifiziert dieser Prozess allein das Problem, und die Lösung wird offensichtlich. Falls nicht, kannst du zumindest die minimalen Schritte zum Reproduzieren des Problems aufschreiben.


Verhalten untersuchen
---------------------

Wenn die Schritte zur Reproduktion bekannt sind, bist du gut positioniert, um eine Ursache zu diagnostizieren. Dazu gehört Ausprobieren und, wenn du dich auskennst, Code lesen.

Wenn du nicht erklären kannst, warum das Problem auftritt, variiere das Verhalten. Nimm eine kleine Änderung vor und versuche es erneut. Wenn deine relevante Konfiguration zum Beispiel einen regulären Ausdruck enthält, ändere oder vereinfache den Ausdruck&mdash;oder entferne ihn ganz&mdash;und sieh, ob du *irgendeinen* Schritt in Richtung des gewünschten Verhaltens erreichst. Selbst wenn es nicht genau das ist, was du willst, weißt du immerhin, dass das Problem beim regulären Ausdruck oder bei der Konfiguration liegt.

Achte beim Untersuchen auf Muster darin, was funktioniert und was nicht. Das sollte dich auf den Weg zu einer Lösung führen.

Wenn du eine Lösung findest, kannst du entscheiden, ob es ein Bug sein sollte oder nicht. Manchmal ist nicht offensichtlich, ob es ein Bug ist; es ist in Ordnung, ein Issue mit deinen Experimenten zu posten und so oder so Feedback von Maintainern zu bekommen.

Und wenn es kein Bug ist: Glückwunsch. Du hast ein Problem gelöst und dabei zumindest etwas gelernt.

Erwäge, [im Forum](https://caddy.community) über deine Erfahrung zu schreiben, um anderen zu helfen, die auf dasselbe Problem stoßen könnten.
