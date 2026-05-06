---
title: Adattatori di configurazione
---

# Adattatori di configurazione

Il linguaggio di configurazione nativo di Caddy è il [JSON](https://www.json.org/json-en.html), ma scrivere il JSON a mano può essere noioso e soggetto a errori. Ecco perché Caddy supporta la configurazione con altri linguaggi tramite gli **adattatori di configurazione** (config adapters). Si tratta di plugin di Caddy che rendono possibile l'uso della configurazione nel vostro formato preferito, generando al posto vostro il [JSON di Caddy](/docs/json/).

Ad esempio, un adattatore di configurazione potrebbe [trasformare la vostra configurazione NGINX nel JSON di Caddy](https://github.com/caddyserver/nginx-adapter).

## Adattatori di configurazione noti

I seguenti adattatori di configurazione sono attualmente disponibili (alcuni sono progetti di terze parti):

- [**caddyfile**](/docs/caddyfile) (standard)
- [**nginx**](https://github.com/caddyserver/nginx-adapter)
- [**jsonc**](https://github.com/caddyserver/jsonc-adapter)
- [**json5**](https://github.com/caddyserver/json5-adapter)
- [**yaml**](https://github.com/abiosoft/caddy-yaml)
- [**cue**](https://github.com/caddyserver/cue-adapter)
- [**toml**](https://github.com/awoodbeck/caddy-toml-adapter)
- [**hcl**](https://github.com/francislavoie/caddy-hcl)
- [**dhall**](https://github.com/mholt/dhall-adapter)
- [**mysql**](https://github.com/zhangjiayin/caddy-mysql-adapter)

## Usare gli adattatori di configurazione

Potete usare un adattatore di configurazione specificandolo sulla riga di comando tramite il flag `--adapter` nella maggior parte dei sottocomandi che accettano una configurazione:

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

Oppure tramite l'API all'[endpoint `/load`](/docs/api#post-load):

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

Se volete solo ottenere il JSON risultante senza eseguirlo, potete usare il comando [`caddy adapt`](/docs/command-line#caddy-adapt):

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

## Avvertenze

Non tutti i linguaggi di configurazione sono compatibili al 100% con Caddy; alcune funzionalità o comportamenti semplicemente non si traducono bene o non sono ancora stati programmati nell'adattatore o in Caddy stesso.

Alcuni adattatori eseguono una traduzione 1-a-1, come YAML->JSON o TOML->JSON. Altri sono progettati specificamente per Caddy, come il Caddyfile. In genere, questi adattatori funzioneranno sempre.

Tuttavia, non tutti gli adattatori funzionano sempre correttamente. Gli adattatori di configurazione fanno del loro meglio per tradurre il vostro input nel JSON di Caddy con la massima fedeltà e correttezza. Poiché non è garantito che questo processo di conversione sia completo e corretto in ogni momento, non li chiamiamo "convertitori" o "traduttori". Sono "adattatori" poiché vi forniranno almeno un buon punto di partenza per finire di elaborare la vostra configurazione JSON finale.

Gli adattatori di configurazione possono restituire il JSON risultante, avvisi (warning) ed errori. Il JSON viene restituito se non si verificano errori. Gli errori si verificano quando c'è qualcosa che non va nell'input (ad esempio, errori di sintassi). Gli avvisi vengono emessi quando c'è qualcosa che non va nell'adattamento ma che non è necessariamente fatale (ad esempio, una funzionalità non supportata). Si consiglia cautela se si utilizzano configurazioni che sono state adattate con degli avvisi.
