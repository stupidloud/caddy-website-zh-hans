---
title: fs (directive Caddyfile)
---

# fs

Définit quel système de fichiers doit être utilisé pour effectuer les E/S fichiers.

Cela peut vous permettre de vous connecter à un système de fichiers distant tournant dans le cloud, ou à une base de données avec une interface de type fichier, ou même de lire des fichiers intégrés dans le binaire Caddy.

Tout d'abord, vous devez déclarer un nom de système de fichiers en utilisant l' [option globale `filesystem`](/docs/caddyfile/options#filesystem), puis vous pouvez utiliser cette directive pour spécifier quel système de fichiers utiliser.

Cette directive est souvent utilisée conjointement avec la [directive `file_server`](file_server) pour servir des fichiers statiques, ou la [directive `try_files`](try_files) pour effectuer des réécritures basées sur l'existence de fichiers. Elle est également typiquement utilisée avec la [directive `root`](root) pour définir le chemin racine au sein du système de fichiers.


## Syntaxe

```caddy-d
fs [<matcher>] <système_fichiers>
```

## Exemples

Utilisation d'un système de fichiers nommé `foo`, utilisant un module imaginaire nommé `custom` qui pourrait nécessiter une authentification :

```caddy
{
	filesystem foo custom {
		api_key abc123
	}
}

example.com {
	fs foo
	root /srv
	file_server
}
```

Pour servir uniquement les images depuis le système de fichiers `foo`, et le reste depuis le système de fichiers par défaut :

```caddy
example.com {
	fs /images* foo
	root /srv
	file_server
}
```
