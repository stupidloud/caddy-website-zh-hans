---
title: Adaptateurs de configuration
---

# Adaptateurs de configuration

Le langage de configuration natif de Caddy est le [JSON](https://www.json.org/json-en.html), mais écrire du JSON à la main peut être fastidieux et source d'erreurs. C'est pourquoi Caddy permet d'être configuré avec d'autres langages via des **adaptateurs de configuration**. Ce sont des plugins Caddy qui permettent d'utiliser une configuration dans votre format préféré en générant du [JSON Caddy](/docs/json/) pour vous.

Par exemple, un adaptateur de configuration pourrait [transformer votre configuration NGINX en JSON Caddy](https://github.com/caddyserver/nginx-adapter).

## Adaptateurs connus

Les adaptateurs de configuration suivants sont actuellement disponibles (certains sont des projets tiers) :

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

## Utilisation des adaptateurs

Vous pouvez utiliser un adaptateur en le spécifiant en ligne de commande avec le drapeau `--adapter` sur la plupart des sous-commandes acceptant une configuration :

<pre><code class="cmd bash">caddy run --config caddy.yaml --adapter yaml</code></pre>

Ou via l'API sur le [point d'accès `/load`](/docs/api#post-load) :

<pre><code class="cmd bash">curl localhost:2019/load \
	-H "Content-Type: application/yaml" \
	--data-binary @caddy.yaml</code></pre>

Si vous souhaitez seulement obtenir le JSON résultant sans l'exécuter, vous pouvez utiliser la commande [`caddy adapt`](/docs/command-line#caddy-adapt) :

<pre><code class="cmd bash">caddy adapt --config caddy.yaml --adapter yaml</code></pre>

## Mises en garde

Tous les langages de configuration ne sont pas compatibles à 100 % avec Caddy ; certaines fonctionnalités ou comportements ne se traduisent tout simplement pas bien ou ne sont pas encore programmés dans l'adaptateur ou dans Caddy lui-même.

Certains adaptateurs effectuent une traduction directe (1 pour 1), comme YAML->JSON ou TOML->JSON. D'autres sont conçus spécifiquement pour Caddy, comme le Caddyfile. Généralement, ces adaptateurs fonctionneront toujours.

Cependant, tous les adaptateurs ne fonctionnent pas tout le temps. Les adaptateurs de configuration font de leur mieux pour traduire votre saisie en JSON Caddy avec la plus grande fidélité et justesse possible. Comme ce processus de conversion n'est pas garanti d'être complet et correct à tout moment, nous ne les appelons pas des "convertisseurs" ou des "traducteurs". Ce sont des "adaptateurs" car ils vous donneront au moins un bon point de départ pour finir de peaufiner votre configuration JSON finale.

Les adaptateurs de configuration peuvent produire le JSON résultant, des avertissements et des erreurs. Le JSON est produit si aucune erreur ne survient. Les erreurs surviennent quand quelque chose ne va pas avec l'entrée (par exemple, des erreurs de syntaxe). Des avertissements sont émis quand quelque chose ne va pas lors de l'adaptation mais n'est pas nécessairement fatal (par exemple, une fonctionnalité non supportée). La prudence est de mise si vous utilisez des configurations adaptées avec des avertissements.
