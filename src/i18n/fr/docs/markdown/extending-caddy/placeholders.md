---
title: "Support des espaces réservés (Placeholders)"
---

# Espaces réservés (Placeholders)

Dans Caddy, les espaces réservés sont traités individuellement par chaque plugin selon les besoins ; ils ne fonctionnent pas automatiquement partout.

Cela signifie que si vous souhaitez que votre plugin supporte les espaces réservés, vous devez explicitement y ajouter le support.

Si vous n'êtes pas encore familier avec les espaces réservés, commencez par [lire ceci](/docs/conventions#placeholders) !

## Vue d'ensemble des espaces réservés

Les [espaces réservés (placeholders)](/docs/conventions#placeholders) sont des chaînes de caractères au format `{foo.bar}` utilisées comme valeurs de configuration dynamiques, qui sont évaluées plus tard lors de l'exécution.

Les [substitutions de variables d'environnement](/docs/caddyfile/concepts#environment-variables) du Caddyfile commençant par un signe dollar comme `{$FOO}` sont évaluées au moment de l'analyse du Caddyfile, et n'ont pas besoin d'être gérées par votre plugin. Ce ne sont *pas* des espaces réservés, bien qu'elles partagent la même syntaxe `{ }`.

Il est donc important de comprendre que `{env.HOST}` (un [espace réservé global](/docs/conventions#placeholders)) est intrinsèquement différent de `{$HOST}` (une substitution de variable d'env du Caddyfile).

À titre d'exemple, voyez le Caddyfile suivant :
```caddy
:8080 {
	respond {$HOST} 200
}

:8081 {
	respond {env.HOST} 200
}
```

Lorsque vous adaptez ce Caddyfile en JSON avec `HOST=exemple caddy adapt`, vous obtiendrez :

```json
{
  "apps": {
    "http": {
      "servers": {
        "srv0": {
          "listen": [":8080"],
          "routes": [
            {
              "handle": [
                {
                  "body": "exemple",
                  "handler": "static_response",
                  "status_code": 200
                }
              ]
            }
          ]
        },
        "srv1": {
          "listen": [":8081"],
          "routes": [
            {
              "handle": [
                {
                  "body": "{env.HOST}",
                  "handler": "static_response",
                  "status_code": 200
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```

En particulier, regardez le champ `"body"` dans `srv0` et `srv1`.

Puisque `srv0` utilisait `{$HOST}` (substitution de variable d'env du Caddyfile), la valeur est devenue `exemple`, car elle a été traitée lors de l'analyse du Caddyfile au moment de produire la configuration JSON.

Puisque `srv1` utilisait `{env.HOST}` (un espace réservé global), elle reste intacte lors de l'adaptation en JSON.

Cela signifie que les utilisateurs écrivant une configuration JSON (n'utilisant pas le Caddyfile) ne peuvent pas utiliser la syntaxe `{$ENV}`. Pour cette raison, il est important que les auteurs de plugins implémentent le support du remplacement des espaces réservés lorsque la configuration est initialisée (provisionnée). Ceci est expliqué ci-dessous.


## Implémenter le support des espaces réservés

Vous ne devez pas traiter les espaces réservés dans [`UnmarshalCaddyfile()`](/docs/extending-caddy/caddyfile). Au lieu de cela, les espaces réservés doivent être remplacés plus tard, soit lors de l'étape [`Provision()`](/docs/extending-caddy#provisioning), soit pendant l'exécution de votre module (ex: `ServeHTTP()` pour les gestionnaires HTTP, `Match()` pour les sélecteurs, etc.), en utilisant un `caddy.Replacer`.


### Exemples

Ici, nous utilisons un replacer nouvellement construit pour traiter les espaces réservés. Il a accès aux [espaces réservés globaux](/docs/conventions#placeholders) tels que `{env.HOST}`, mais *pas* aux espaces réservés HTTP tels que `{http.request.uri}` car le provisionnement se produit lors du chargement de la configuration, et non pendant une requête.

```go
func (g *Gizmo) Provision(ctx caddy.Context) error {
	repl := caddy.NewReplacer()
	g.Name = repl.ReplaceAll(g.Name,"")
	return nil
}
```

Ici, nous récupérons le replacer depuis le contexte de la requête `r.Context()` pendant `ServeHTTP`. Ce replacer a accès à la fois aux espaces réservés globaux *et* aux espaces réservés HTTP par requête tels que `{http.request.uri}`.

```go
func (g *Gizmo) ServeHTTP(w http.ResponseWriter, r *http.Request, next caddyhttp.Handler) error {
	repl := r.Context().Value(caddy.ReplacerCtxKey).(*caddy.Replacer)
	_, err := w.Write([]byte(repl.ReplaceAll(g.Name,"")))
	if err != nil {
		return err
	}
	return next.ServeHTTP(w, r)
}
```
