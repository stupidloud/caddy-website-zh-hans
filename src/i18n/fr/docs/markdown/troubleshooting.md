Stratégies de dépannage
========================

Cette page présente un cadre méthodologique général pour résoudre par vous-même la plupart des problèmes que vous pourriez rencontrer en utilisant Caddy *sans avoir recours à l'IA*. Nous recommandons des étapes similaires lorsque vous demandez de l'aide sur nos forums. Dans bien des cas, vous pouvez répondre à votre propre question ou résoudre vos propres problèmes en appliquant une réflexion critique.


Que savez-vous ?
----------------

Il se peut que vous ne sachiez pas quel est le problème, ce qui le cause ou comment le résoudre. Commençons donc par des éléments fondamentaux que vous connaissez certainement :

### Ce que vous attendez

Dites-le à voix haute, ou dans votre tête, ou écrivez-le. Soyez clair et précis afin qu'il n'y ait aucun doute ou place pour l'ambiguïté. Vous pourriez même vous expliquer à vous-même *pourquoi* c'est ce que vous attendez.

"Ça devrait marcher" n'est pas une bonne attente.

"Je m'attends à une redirection 301 lorsque je fais une requête vers cette URI" est bien meilleur.


### Comportement actuel

Observez ce qui se passe. Que se passe-t-il *exactement*, et en quoi cela contraste-t-il avec votre attente ? Synthétisez ce que vous savez.

"Ça ne marche pas" est inutile et paresseux ; évitez cette phrase partout, sauf peut-être comme raccourci pour décrire un comportement spécifique déjà documenté en détail.

"Au lieu d'une réponse 301, j'obtiens une réponse 200, bien que je voie l'en-tête `Server: Caddy`", est bien meilleur car cela compare et contraste ce que vous savez avec ce que vous attendez, et synthétise d'autres informations connues, ce qui nous indique que la requête atteint au moins une instance de Caddy.


### Journaux (Logs)

Que contiennent les journaux de Caddy ? Par défaut, ils sont écrits dans le terminal qui a lancé le processus. S'il est exécuté en mode "détaché", par exemple comme un service système, vous devrez peut-être récupérer les journaux ailleurs.

Notez que les journaux de requêtes HTTP ("journaux d'accès") sont différents des journaux de processus et doivent être explicitement activés dans votre configuration.

Vous pourriez également vouloir activer la journalisation au niveau DEBUG si ce n'est pas déjà fait.

Mais dans tous les cas, l'une des premières choses à faire est de regarder les journaux. *Tous les journaux.* Le contexte du message compte, donc une seule ligne de journal isolée est rarement utile. Collectez-en plus que ce dont vous pensez avoir besoin et conservez-les tout au long du processus de dépannage.

Y a-t-il des indices dans les journaux ?


Reconnaître et douter des suppositions
--------------------------------------

Avant d'aller plus loin, nous devons souligner à quel point il est crucial de critiquer ce que vous supposez. Nous faisons tous des suppositions basées sur nos habitudes et nos attentes. "Garde à l'esprit tes suppositions, et grand sera ton pouvoir." (— Yoda, ou quelqu'un comme ça.)

Par exemple, une supposition courante est qu'après avoir recompilé Caddy, lancer `caddy` exécutera le nouveau code. Ce n'est vrai que si votre binaire compilé a remplacé celui présent dans votre `$PATH`. Sinon, `./caddy` est généralement l'invocation appropriée.

Les suppositions s'accumulent à mesure que votre déploiement ou votre configuration gagne en complexité. Par exemple, un déploiement dans Docker implique de reconstruire une image et de la lancer, ce qui multiplie les suppositions que vous pourriez faire.

Beaucoup de questions et de rapports de bugs s'avèrent être des problèmes de configuration externe du système et du réseau, et non de Caddy lui-même. Par exemple, si vous ne pouvez pas vous connecter à votre instance Caddy, mais que Caddy tourne clairement, vous supposez probablement que ce n'est pas le DNS. Indice : c'est presque toujours le DNS.

Même le simple fait de supposer que vous avez rechargé une configuration, alors que ce n'est pas le cas, est une erreur courante. Efforcez-vous d'être rigoureux dans votre processus. Vérifiez à chaque niveau.


Reproduire le comportement
--------------------------

C'est une étape clé qui permet souvent aux problèmes de se résoudre d'eux-mêmes : faites en sorte que le problème se reproduise.

Plus précisément, reproduisez-le *de la manière la plus minimale possible*. Éliminez les configurations inutiles, les étapes de déploiement, les facteurs environnementaux, etc., jusqu'à ce que le problème disparaisse.

Une stratégie courante consiste à éliminer une seule chose à la fois, et de réessayer, jusqu'à ce que le problème disparaisse. Alors, cette chose que vous avez retirée est probablement la cause, ou — et c'est un bon moment pour douter des suppositions — une combinaison de la dernière chose et de ce que vous avez retiré juste avant. Vérifiez en rajoutant les premières choses retirées. Cernez le problème.

Une autre idée est d'éliminer environ la moitié de tout à chaque itération, et une fois que le problème disparaît, d'éliminer juste la moitié de cette moitié, et ainsi de suite. C'est comme une recherche binaire et cela peut être plus rapide.

Alternativement, au lieu de l'élimination, vous pourriez inverser ces stratégies et construire progressivement votre configuration ou votre scénario à partir de zéro, en réessayant à chaque fois, jusqu'à ce que le problème apparaisse.

Souvent, ce processus identifiera à lui seul le problème et la solution pourrait devenir évidente. Si ce n'est pas le cas, vous pourrez au moins noter les étapes minimales pour reproduire le problème.


Explorer les comportements
--------------------------

Une fois les étapes pour reproduire le problème connues, vous êtes bien placé pour diagnostiquer une cause. Cela implique de bricoler et, si vous êtes calé, de lire le code.

Si vous ne pouvez pas expliquer pourquoi le problème survient, variez le comportement. Faites un petit changement et réessayez. Par exemple, si votre configuration implique une expression régulière, changez/simplifiez l'expression — ou supprimez-la entièrement — et voyez si vous obtenez *quelque chose* qui se rapproche du comportement recherché. Même si ce n'est pas ce que vous voulez, au moins vous saurez s'il s'agit d'un problème avec l'expression régulière ou la configuration.

Au fur et à mesure de votre exploration, remarquez les schémas de ce qui fonctionne et de ce qui ne fonctionne pas. Cela devrait vous mener vers une solution.

Si vous trouvez une solution, vous pouvez alors décider s'il s'agit d'un bug ou non. Parfois, ce n'est pas évident ; il n'y a pas de mal à poster un ticket avec vos expérimentations et à obtenir l'avis des mainteneurs dans les deux cas.

Et si ce n'est pas un bug, félicitations ! Vous avez résolu un problème et appris au moins quelque chose au passage.

Pensez à partager votre expérience [sur le forum](https://caddy.community) pour aider d'autres personnes qui pourraient rencontrer le même problème.
