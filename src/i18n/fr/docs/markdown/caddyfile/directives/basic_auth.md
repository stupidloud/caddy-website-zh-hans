---
title: basic_auth (directive Caddyfile)
---

# basic_auth

Active l'authentification HTTP Basic, qui peut être utilisée pour protéger des répertoires et des fichiers avec un nom d'utilisateur et un mot de passe haché.

**Notez que l'authentification Basic n'est pas sécurisée via le HTTP en texte clair.** Faites preuve de discernement lorsque vous décidez quoi protéger avec l'authentification HTTP Basic.

Lorsqu'un utilisateur demande une ressource protégée, le navigateur lui demandera un nom d'utilisateur et un mot de passe s'il n'en a pas déjà fourni. Si les identifiants appropriés sont présents dans l'en-tête `Authorization`, le serveur accordera l'accès à la ressource. Si l'en-tête est manquant ou si les identifiants sont incorrects, le serveur répondra par une erreur HTTP 401 Unauthorized.

La configuration de Caddy n'accepte pas les mots de passe en texte clair ; vous DEVEZ les hacher avant de les mettre dans la configuration. La commande [`caddy hash-password`](/docs/command-line#caddy-hash-password) peut vous y aider.

Après une authentification réussie, l'espace réservé `{http.auth.user.id}` sera disponible, contenant le nom d'utilisateur authentifié.

Avant la v2.8.0, cette directive s'appelait `basicauth`, mais a été renommée pour plus de cohérence avec les autres directives.


## Syntaxe

```caddy-d
basic_auth [<matcher>] [<hash_algorithm> [<realm>]] {
	<nom_utilisateur> <mot_de_passe_haché>
	...
}
```

- **&lt;hash_algorithm&gt;** spécifie l'algorithme de hachage de mot de passe (ou fonction de dérivation de clé) utilisé pour les hachages dans cette configuration. Les options disponibles incluent `argon2id`, le défaut étant `bcrypt`.

- **&lt;realm&gt;** est un nom de domaine d'authentification (realm) personnalisé.

- **&lt;nom_utilisateur&gt;** est un nom d'utilisateur ou un ID utilisateur.

- **&lt;mot_de_passe_haché&gt;** est le hachage du mot de passe.


## Exemples

Exiger une authentification pour toutes les requêtes vers `example.com` :

```caddy
example.com {
	basic_auth {
		# Utilisateur "Bob", mot de passe "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}
	respond "Bienvenue, {http.auth.user.id}" 200
}
```

Protéger les fichiers dans `/secret/` afin que seul `Bob` puisse y accéder (tout le monde pouvant voir les autres chemins) :

```caddy
example.com {
	root /srv

	basic_auth /secret/* {
		# Utilisateur "Bob", mot de passe "hiccup"
		Bob $2a$14$Zkx19XLiW6VYouLHR5NmfOFU0z2GTNmpkT/5qqR7hx4IjWJPDhjvG
	}

	file_server
}
```

Exemple avec `argon2id` :

```caddy
example.com {
	root /srv

	basic_auth /secret/* argon2id {
		# Utilisateur "Bob", mot de passe "hiccup"
		Bob $argon2id$v=19$m=47104,t=1,p=1$zJPvVe48N64JUa9MFlVhiw$b5Tznu0PxnA4TciY6qYe2BFPxncF1ePQaeNukHhH1cU
	}

	file_server
}
```
