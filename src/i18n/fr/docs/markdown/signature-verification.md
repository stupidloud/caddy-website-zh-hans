---
title: Vérifier les signatures des fichiers (assets)
---

# Vérification des signatures

La signature des artefacts vous permet de valider que l'artefact que vous possédez est bien celui créé par le workflow du projet et n'a pas été modifié par un tiers non autorisé (ex : attaque de l'homme du milieu). La validation fournit une base commune et l'assurance que toutes les parties se réfèrent au même artefact, qu'il s'agisse d'un exécutable, d'un SBOM ou d'un fichier texte.

Depuis Caddy v2.6.0, les artefacts de release CI/CD sont signés à l'aide de la technologie du projet [Sigstore](https://www.sigstore.dev/), qui émet des certificats contenant des détails sur le sujet auquel le certificat est délivré. Vous pouvez commencer par inspecter le certificat utilisé pour signer l'artefact de votre choix. Les certificats sont encodés en base64, vous devez donc d'abord les décoder pour obtenir le fichier PEM. Dans cet exemple, nous travaillerons avec l'artefact `caddy_2.6.0_checksums.txt` et supposerons un environnement de type Linux.

Commencez par télécharger les 3 fichiers relatifs à votre artefact (c'est-à-dire `<l'artefact>` lui-même, `<l'artefact>.sig` qui est la signature, et `<l'artefact>.pem` qui est le certificat émanant de la racine de Fulcio par Sigstore). Ensuite, décodez le fichier `.pem` téléchargé vers sa version non "blindée" :

<pre><code class="cmd bash">base64 -d < caddy_2.6.0_checksums.txt.pem > cert.pem</code></pre>

Vous pouvez maintenant inspecter le certificat à l'aide de la commande `openssl`. Lancer `openssl x509 -in cert.pem -text` sur le certificat que nous venons de décoder affiche cet extrait :


<pre><code class="cmd"><span class="bash">openssl x509 -in cert.pem -text</span>
Certificate:
    Data:
        Version: 3 (0x2)
...
    Signature Algorithm: ecdsa-with-SHA384
        Issuer: O=sigstore.dev, CN=sigstore-intermediate
        Validity
            Not Before: Sep 20 17:17:06 2022 GMT
            Not After : Sep 20 17:27:06 2022 GMT
        Subject:
        Subject Public Key Info:
            Public Key Algorithm: id-ecPublicKey
...
        X509v3 extensions:
            X509v3 Key Usage: critical
                Digital Signature
            X509v3 Extended Key Usage:
                Code Signing
...
            X509v3 Subject Alternative Name: critical
                URI:https://github.com/caddyserver/caddy/.github/workflows/release.yml@refs/tags/v2.6.0
...
</code></pre>

<aside class="tip" id="x509-extensions">

Notez l'usage prévu du certificat : `Code Signing`. Le certificat contient également l'URI du workflow GitHub Actions déclencheur dans l'extension `X509v3 Subject Alternative Name`, le nom du workflow GHA dans `1.3.6.1.4.1.57264.1.4`, le commit à signer dans `1.3.6.1.4.1.57264.1.3`, le nom du dépôt dans `1.3.6.1.4.1.57264.1.5`, et la référence (ref) déclencheuse dans `1.3.6.1.4.1.57264.1.6`. Ces détails combinés identifient l'événement unique dans l'univers pour lequel le certificat doit être utilisé.

</aside>

Maintenant que nous avons le certificat, nous pouvons utiliser la CLI `cosign` pour valider la signature. Nous lançons la commande suivante (notez qu'elle utilise le certificat non décodé) :

<pre><code class="cmd"><span class="bash">COSIGN_EXPERIMENTAL=1 cosign verify-blob --certificate ./caddy_2.6.0_checksums.txt.pem --signature ./caddy_2.6.0_checksums.txt.sig ./caddy_2.6.0_checksums.txt</span>
tlog entry verified with uuid: 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 index: 3618623
Verified OK
</code></pre>

Passons maintenant à l'outil `rekor-cli`, qui interagit avec le serveur public Rekor stockant les journaux de transparence. Lançons :

<pre><code class="cmd bash">rekor-cli get --uuid 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 --format json | jq -r '.'
</code></pre>

L'utilisation de `jq` permet d'embellir la sortie. Vous devriez voir un résultat comme celui-ci :

```json
{
  "Attestation": "",
  "AttestationType": "",
  "Body": {
    "HashedRekordObj": {
      "data": {
        "hash": {
          "algorithm": "sha256",
          "value": "508f1044ecd9f14c43c6c8986b45b90fc79f25736e2bc85c0911433ce82533f2"
        }
      },
      "signature": {
        "content": "MEUCIHGL2HP5XzcUESTxIk72FS1aNK54LesTfyo+dVhRMeduAiEAnWZDZ5Ur44Y9056vr4to2Fb9FteG53eAFotv3fUZ4h4=",
        "publicKey": {
          "content": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t..."
        }
      }
    }
  },
  "LogIndex": 3618623,
  "IntegratedTime": 1663694226,
  "UUID": "04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09",
  "LogID": "c0d23d6ad406973f9559f3ba2d1ca01f84147d8ffc5b8445c224f98b9591801d"
}
```

Remarquez comment la valeur de `.Body.HashedRekordObj.signature.content` correspond au contenu de la signature générée dans notre CI et disponible dans le fichier `caddy_2.6.0_checksums.txt.sig`. De plus, le certificat utilisé et téléchargé est également stocké sur le serveur Rekor et disponible dans la réponse sous `.Body.HashedRekordObj.signature.publicKey.content` ; il correspond à la chaîne que nous avons dans le fichier `caddy_2.6.0_checksums.txt.pem`. Nous pouvons aller plus loin et vérifier comment `.Body.HashedRekordObj.data.hash.value` correspond à la sortie de la commande `sha256sum ./caddy_2.6.0_checksums.txt`. À ce stade, nous avons des certificats correspondants, des signatures correspondantes et des sommes de contrôle (checksums) correspondantes. Tout cela est enregistré publiquement dans les journaux de transparence pour que tout un chacun puisse le valider.

## Vérifier l'authenticité d'un artefact

Et si on vous remettait un artefact prétendu être un produit du projet Caddy mais sans vous donner le fichier de signature ou le certificat ? Vous pouvez utiliser `rekor-cli` pour interroger le serveur Rekor pour cet artefact :

<pre><code class="cmd"><span class="bash">rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]'</span>
Found matching entries (listed by UUID):
362f8ecba72f432604deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09</code></pre>

Notez que l'UUID correspond à celui rencontré précédemment pour le même fichier. Comme nous l'avons fait auparavant, nous pouvons interroger Rekor pour obtenir les détails de cet UUID :

<pre><code class="cmd bash">rekor-cli get --uuid 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 --format json | jq -r '.'</code></pre>

Cependant, nous pouvons raccourcir la recherche en exécutant cette ligne qui fusionne les deux commandes :

<pre><code class="cmd"><span class="bash">rekor-cli get --uuid $(rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]') --format json | jq -r '.'</span>
</code></pre>

Nous savons maintenant que l'artefact est signé et que sa signature est consignée sur le serveur de journaux de transparence Rekor. L'étape suivante consiste à valider que la signature et l'artefact sont bien le produit du workflow CI/CD du projet Caddy. Nous faisons cela en extrayant la clé publique du JSON reçu de Rekor, en la décodant en fichier PEM, puis en inspectant le certificat avec `openssl`.

<pre>
<code class="cmd"><span class="bash">rekor-cli get --uuid $(rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]') --format json | jq -r '.Body.HashedRekordObj.signature.publicKey.content' | base64 -d > cert.pem</span></code>
</pre>

Inspectez maintenant le certificat avec `openssl` et portez une attention particulière à la section `X509v3 extensions`.

<pre><code class="cmd"><span class="bash">openssl x509 -in cert.pem -text</span>
...
            X509v3 Subject Alternative Name: critical
                URI:https://github.com/caddyserver/caddy/.github/workflows/release.yml@refs/tags/v2.6.0
...
</code></pre>

Les [valeurs des extensions](#x509-extensions) indiquent l'authenticité de l'artefact. Reportez-vous aux [informations OID de Sigstore](https://github.com/sigstore/fulcio/blob/a25fb09c3f0561ac43e50357fdfc427e3f0aca4a/docs/oid-info.md) pour la définition de chaque extension.

## Que faire si la signature n'est pas vérifiée ?

Un échec de vérification de signature indique que l'artefact en main n'a pas été produit par le workflow CI/CD du projet Caddy sur GitHub. Si vous possédez la signature, le certificat et l'artefact, vous recherchez une vérification réussie rapportée par `cosign`. Alternativement, vous pouvez utiliser `rekor-cli` pour inspecter le serveur Rekor, valider que les extensions du certificat ont les valeurs attendues, et faire correspondre les sommes de contrôle et les signatures. Un écart ou l'absence d'entrée dans Rekor signifie soit que l'artefact n'a pas été produit par le CI/CD du projet Caddy, soit que l'artefact a été altéré quelque part entre le flux de build du CI/CD, la page des releases GitHub et sa livraison chez vous.
