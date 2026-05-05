---
title: Asset-Signaturen verifizieren
---

<a id="signature-verification"></a>
# Signaturverifikation

Durch das Signieren von Artefakten kannst du prüfen, ob das Artefakt, das du hast, genau dasselbe ist, das vom Workflow des Projekts erzeugt wurde, und ob es nicht von einer unautorisierten Partei verändert wurde (z. B. durch einen Man-in-the-Middle). Die Validierung schafft eine gemeinsame Grundlage, Sicherheit und Gewissheit, dass alle Parteien sich auf dasselbe Artefakt beziehen, dieselbe Byte-Sammlung, egal ob es sich um eine ausführbare Datei, eine SBOM oder eine Textdatei handelt.

Seit Caddy v2.6.0 werden CI/CD-Release-Artefakte mit Technologie des Projekts [Sigstore](https://www.sigstore.dev/) signiert. Sigstore stellt Zertifikate aus, die Details über das Subjekt enthalten, dem das Zertifikat ausgestellt wurde. Du kannst damit beginnen, das Zertifikat zu untersuchen, das zum Signieren des gewünschten Artefakts verwendet wurde. Die Zertifikate sind base64-codiert; du musst sie also zuerst base64-decodieren, um die PEM-Datei zu erhalten. In diesem Beispiel arbeiten wir mit dem Artefakt `caddy_2.6.0_checksums.txt` und nehmen eine Linux-ähnliche Umgebung an.

Lade zunächst die 3 Dateien herunter, die zu deinem gewünschten Artefakt gehören (d. h. `<the artifact>`, das eigentliche Artefakt, dessen zugehörige Signatur und Zertifikate verifiziert werden sollen, `<the artifact>.sig`, die Signatur des Artefakts, und `<the artifact>.pem`, das Zertifikat, das vom Root-Zertifikat von Fulcio by Sigstore abstammt). Decodiere dann die heruntergeladene `.pem`-Datei aus base64 in die armored-Version:

<pre><code class="cmd bash">base64 -d < caddy_2.6.0_checksums.txt.pem > cert.pem</code></pre>

Du kannst das Zertifikat nun mit dem Befehl `openssl` untersuchen. Wenn du `openssl x509 -in cert.pem -text` gegen das gerade decodierte Zertifikat ausführst, zeigt es diesen gekürzten Auszug:


<pre><code class="cmd"><span class="bash">openssl x509 -in cert.pem -text</span>
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            22:b0:45:9d:ad:d7:54:98:67:66:b7:de:31:01:ef:4a:02:ab:fb:60
    Signature Algorithm: ecdsa-with-SHA384
        Issuer: O=sigstore.dev, CN=sigstore-intermediate
        Validity
            Not Before: Sep 20 17:17:06 2022 GMT
            Not After : Sep 20 17:27:06 2022 GMT
        Subject:
        Subject Public Key Info:
            Public Key Algorithm: id-ecPublicKey
                Public-Key: (256 bit)
                pub:
                    04:22:ee:f6:b1:85:1c:de:cf:90:1d:91:75:36:c4:
                    82:9d:54:5e:f3:a6:5b:3f:18:89:8a:0b:de:d8:93:
                    7c:02:40:39:00:d4:4e:19:0b:30:93:cc:a4:d0:df:
                    35:f7:b1:08:24:89:cf:3a:38:06:ff:92:75:06:84:
                    b5:9e:25:8c:9a
                ASN1 OID: prime256v1
                NIST CURVE: P-256
        X509v3 extensions:
            X509v3 Key Usage: critical
                Digital Signature
            X509v3 Extended Key Usage:
                Code Signing
            X509v3 Subject Key Identifier:
                3B:C0:D1:D2:C8:BA:2D:55:95:1F:68:78:DC:C6:2C:D9:B5:17:0E:EA
            X509v3 Authority Key Identifier:
                keyid:DF:D3:E9:CF:56:24:11:96:F9:A8:D8:E9:28:55:A2:C6:2E:18:64:3F

            X509v3 Subject Alternative Name: critical
                URI:https://github.com/caddyserver/caddy/.github/workflows/release.yml@refs/tags/v2.6.0
            1.3.6.1.4.1.57264.1.1:
                https://token.actions.githubusercontent.com
            1.3.6.1.4.1.57264.1.2:
                push
            1.3.6.1.4.1.57264.1.3:
                821a08a6e39ed0e7c43b0271ccf126c194eb6339
            1.3.6.1.4.1.57264.1.4:
                Release
            1.3.6.1.4.1.57264.1.5:
                caddyserver/caddy
            1.3.6.1.4.1.57264.1.6:
                refs/tags/v2.6.0
            1.3.6.1.4.1.11129.2.4.2:
                .z.x.v..`..(R.hE..k'..Eg...=.8.m..".6or....[.DS.....G0E.!..>MD.a..B.p..^..P*...um.....X..F. NYy.....#...TWIZ...y..qa....4P..
    Signature Algorithm: ecdsa-with-SHA384
         30:66:02:31:00:be:b3:3c:15:56:78:64:c6:0f:bc:48:69:a9:
         0a:27:cd:4d:92:39:00:50:42:a8:2a:ad:11:4d:64:f2:61:35:
         ec:08:e9:b5:6a:14:1b:f6:c1:0e:46:ee:a0:54:08:26:e1:02:
         31:00:a7:6d:97:db:4c:c8:dd:47:13:3d:28:7a:a6:f3:64:50:
         2c:5a:9d:9d:10:d0:cf:6f:d0:e9:37:76:fd:cc:8e:9d:c3:6b:
         ba:78:07:40:6a:40:d6:db:f6:97:d5:6a:36:9d
-----BEGIN CERTIFICATE-----
MIIDlDCCAxmgAwIBAgIUIrBFna3XVJhnZrfeMQHvSgKr+2AwCgYIKoZIzj0EAwMw
NzEVMBMGA1UEChMMc2lnc3RvcmUuZGV2MR4wHAYDVQQDExVzaWdzdG9yZS1pbnRl
cm1lZGlhdGUwHhcNMjIwOTIwMTcxNzA2WhcNMjIwOTIwMTcyNzA2WjAAMFkwEwYH
KoZIzj0CAQYIKoZIzj0DAQcDQgAEIu72sYUc3s+QHZF1NsSCnVRe86ZbPxiJigve
2JN8AkA5ANROGQswk8yk0N8197EIJInPOjgG/5J1BoS1niWMmqOCAjgwggI0MA4G
A1UdDwEB/wQEAwIHgDATBgNVHSUEDDAKBggrBgEFBQcDAzAdBgNVHQ4EFgQUO8DR
0si6LVWVH2h43MYs2bUXDuowHwYDVR0jBBgwFoAU39Ppz1YkEZb5qNjpKFWixi4Y
ZD8wYQYDVR0RAQH/BFcwVYZTaHR0cHM6Ly9naXRodWIuY29tL2NhZGR5c2VydmVy
L2NhZGR5Ly5naXRodWIvd29ya2Zsb3dzL3JlbGVhc2UueW1sQHJlZnMvdGFncy92
Mi42LjAwOQYKKwYBBAGDvzABAQQraHR0cHM6Ly90b2tlbi5hY3Rpb25zLmdpdGh1
YnVzZXJjb250ZW50LmNvbTASBgorBgEEAYO/MAECBARwdXNoMDYGCisGAQQBg78w
AQMEKDgyMWEwOGE2ZTM5ZWQwZTdjNDNiMDI3MWNjZjEyNmMxOTRlYjYzMzkwFQYK
KwYBBAGDvzABBAQHUmVsZWFzZTAfBgorBgEEAYO/MAEFBBFjYWRkeXNlcnZlci9j
YWRkeTAeBgorBgEEAYO/MAEGBBByZWZzL3RhZ3MvdjIuNi4wMIGKBgorBgEEAdZ5
AgQCBHwEegB4AHYACGCS8ChS/2hF0dFrJ4ScRWcYrBY9wzjSbea8IgY2b3IAAAGD
W+dEUwAABAMARzBFAiEAnD5NRKZhFLhCHHDIzV6bwVAqlYP6dW0CwKWDo1jzmEYC
IE5ZeeK14oi6I+7z2VRXSVq4/r15GAFxYaCMFrI0UOjjMAoGCCqGSM49BAMDA2kA
MGYCMQC+szwVVnhkxg+8SGmpCifNTZI5AFBCqCqtEU1k8mE17AjptWoUG/bBDkbu
oFQIJuECMQCnbZfbTMjdRxM9KHqm82RQLFqdnRDQz2/Q6Td2/cyOncNrungHQGpA
1tv2l9VqNp0=
-----END CERTIFICATE-----
</code></pre>

<aside class="tip" id="x509-extensions">

Beachte die angegebene beabsichtigte Verwendung des Zertifikats: `Code Signing`. Das Zertifikat enthält außerdem die URI des auslösenden Github Actions Workflows in der Extension `X509v3 Subject Alternative Name`, den Namen des GHA-Workflows in `1.3.6.1.4.1.57264.1.4`, den zu signierenden Commit in `1.3.6.1.4.1.57264.1.3`, den Repo-Namen in `1.3.6.1.4.1.57264.1.5` und die auslösende Ref `1.3.6.1.4.1.57264.1.6`. Zusammen zeigen diese Details genau auf das eine Ereignis im Universum, für das das Zertifikat verwendet werden soll.

</aside>

Nachdem wir das Zertifikat haben, können wir die Signatur mit der `cosign`-CLI validieren. Wir führen den folgenden Befehl aus (beachte, dass er das nicht decodierte Zertifikat verwendet):

<pre><code class="cmd"><span class="bash">COSIGN_EXPERIMENTAL=1 cosign verify-blob --certificate ./caddy_2.6.0_checksums.txt.pem --signature ./caddy_2.6.0_checksums.txt.sig ./caddy_2.6.0_checksums.txt</span>
tlog entry verified with uuid: 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 index: 3618623
Verified OK
</code></pre>

Wechseln wir nun das CLI-Werkzeug und verwenden `rekor-cli`, das mit dem öffentlichen Rekor-Server interagiert, auf dem die Transparenzlogs gespeichert sind. Führen wir aus:

<pre><code class="cmd bash">rekor-cli get --uuid 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 --format json | jq -r '.'
</code></pre>

`jq` wird verwendet, um die Ausgabe hübscher zu formatieren. Du solltest eine Ausgabe wie diese sehen:

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
          "content": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURsRENDQXhtZ0F3SUJBZ0lVSXJCRm5hM1hWSmhuWnJmZU1RSHZTZ0tyKzJBd0NnWUlLb1pJemowRUF3TXcKTnpFVk1CTUdBMVVFQ2hNTWMybG5jM1J2Y21VdVpHVjJNUjR3SEFZRFZRUURFeFZ6YVdkemRHOXlaUzFwYm5SbApjbTFsWkdsaGRHVXdIaGNOTWpJd09USXdNVGN4TnpBMldoY05Nakl3T1RJd01UY3lOekEyV2pBQU1Ga3dFd1lICktvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVJdTcyc1lVYzNzK1FIWkYxTnNTQ25WUmU4NlpiUHhpSmlndmUKMkpOOEFrQTVBTlJPR1Fzd2s4eWswTjgxOTdFSUpJblBPamdHLzVKMUJvUzFuaVdNbXFPQ0FqZ3dnZ0kwTUE0RwpBMVVkRHdFQi93UUVBd0lIZ0RBVEJnTlZIU1VFRERBS0JnZ3JCZ0VGQlFjREF6QWRCZ05WSFE0RUZnUVVPOERSCjBzaTZMVldWSDJoNDNNWXMyYlVYRHVvd0h3WURWUjBqQkJnd0ZvQVUzOVBwejFZa0VaYjVxTmpwS0ZXaXhpNFkKWkQ4d1lRWURWUjBSQVFIL0JGY3dWWVpUYUhSMGNITTZMeTluYVhSb2RXSXVZMjl0TDJOaFpHUjVjMlZ5ZG1WeQpMMk5oWkdSNUx5NW5hWFJvZFdJdmQyOXlhMlpzYjNkekwzSmxiR1ZoYzJVdWVXMXNRSEpsWm5NdmRHRm5jeTkyCk1pNDJMakF3T1FZS0t3WUJCQUdEdnpBQkFRUXJhSFIwY0hNNkx5OTBiMnRsYmk1aFkzUnBiMjV6TG1kcGRHaDEKWW5WelpYSmpiMjUwWlc1MExtTnZiVEFTQmdvckJnRUVBWU8vTUFFQ0JBUndkWE5vTURZR0Npc0dBUVFCZzc4dwpBUU1FS0RneU1XRXdPR0UyWlRNNVpXUXdaVGRqTkROaU1ESTNNV05qWmpFeU5tTXhPVFJsWWpZek16a3dGUVlLCkt3WUJCQUdEdnpBQkJBUUhVbVZzWldGelpUQWZCZ29yQmdFRUFZTy9NQUVGQkJGallXUmtlWE5sY25abGNpOWoKWVdSa2VUQWVCZ29yQmdFRUFZTy9NQUVHQkJCeVpXWnpMM1JoWjNNdmRqSXVOaTR3TUlHS0Jnb3JCZ0VFQWRaNQpBZ1FDQkh3RWVnQjRBSFlBQ0dDUzhDaFMvMmhGMGRGcko0U2NSV2NZckJZOXd6alNiZWE4SWdZMmIzSUFBQUdEClcrZEVVd0FBQkFNQVJ6QkZBaUVBbkQ1TlJLWmhGTGhDSEhESXpWNmJ3VkFxbFlQNmRXMEN3S1dEbzFqem1FWUMKSUU1WmVlSzE0b2k2SSs3ejJWUlhTVnE0L3IxNUdBRnhZYUNNRnJJMFVPampNQW9HQ0NxR1NNNDlCQU1EQTJrQQpNR1lDTVFDK3N6d1ZWbmhreGcrOFNHbXBDaWZOVFpJNUFGQkNxQ3F0RVUxazhtRTE3QWpwdFdvVUcvYkJEa2J1Cm9GUUlKdUVDTVFDbmJaZmJUTWpkUnhNOUtIcW04MlJRTEZxZG5SRFF6Mi9RNlRkMi9jeU9uY05ydW5nSFFHcEEKMXR2Mmw5VnFOcDA9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K"
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

Beachte, dass der Wert von `.Body.HashedRekordObj.signature.content` mit dem Inhalt der Signatur übereinstimmt, die in unserem CI erzeugt wurde und in der Datei `caddy_2.6.0_checksums.txt.sig` verfügbar ist. Außerdem ist das verwendete und heruntergeladene Zertifikat ebenfalls auf dem Rekor-Server gespeichert, in der Antwort unter `.Body.HashedRekordObj.signature.publicKey.content` verfügbar und stimmt mit dem String überein, den wir in der Datei `caddy_2.6.0_checksums.txt.pem` haben. Wir können noch einen Schritt weitergehen und prüfen, dass `.Body.HashedRekordObj.data.hash.value` mit der Ausgabe des Befehls `sha256sum ./caddy_2.6.0_checksums.txt` übereinstimmt. Bis hierhin haben wir also übereinstimmende Zertifikate, übereinstimmende Signaturen und übereinstimmende Checksummen (der Datei, die die Checksummen der Archive enthält, aber nicht ihrer selbst; diese Checksumme wird extern über das Sigstore-Ökosystem bereitgestellt und aufgezeichnet). All das ist öffentlich in Transparenzlogs erfasst, damit die Allgemeinheit es validieren kann.

<a id="verifying-authenticity-of-an-artifact"></a>
## Authentizität eines Artefakts verifizieren

Was ist, wenn dir ein Artefakt übergeben wird, das angeblich vom Caddy-Projekt stammt, du aber weder die Signaturdatei noch das Zertifikat erhalten hast? Du kannst `rekor-cli` verwenden, um den Rekor-Server nach dem betreffenden Artefakt abzufragen:

<pre><code class="cmd"><span class="bash">rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]'</span>
Found matching entries (listed by UUID):
362f8ecba72f432604deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09</code></pre>

Beachte, dass die UUID mit derjenigen übereinstimmt, die im früheren Abschnitt für dieselbe Datei aufgetaucht ist. Wie im früheren Abschnitt können wir Rekor nach den Entry-Details dieser UUID fragen:

<pre><code class="cmd bash">rekor-cli get --uuid 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 --format json | jq -r '.'</code></pre>

Wir können die Abfrage jedoch abkürzen, indem wir mit dieser Zeile die zwei getrennten Befehle zu einem Einzeiler zusammenführen:

<pre><code class="cmd"><span class="bash">rekor-cli get --uuid $(rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]') --format json | jq -r '.'</span>
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
          "content": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURsRENDQXhtZ0F3SUJBZ0lVSXJCRm5hM1hWSmhuWnJmZU1RSHZTZ0tyKzJBd0NnWUlLb1pJemowRUF3TXcKTnpFVk1CTUdBMVVFQ2hNTWMybG5jM1J2Y21VdVpHVjJNUjR3SEFZRFZRUURFeFZ6YVdkemRHOXlaUzFwYm5SbApjbTFsWkdsaGRHVXdIaGNOTWpJd09USXdNVGN4TnpBMldoY05Nakl3T1RJd01UY3lOekEyV2pBQU1Ga3dFd1lICktvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVJdTcyc1lVYzNzK1FIWkYxTnNTQ25WUmU4NlpiUHhpSmlndmUKMkpOOEFrQTVBTlJPR1Fzd2s4eWswTjgxOTdFSUpJblBPamdHLzVKMUJvUzFuaVdNbXFPQ0FqZ3dnZ0kwTUE0RwpBMVVkRHdFQi93UUVBd0lIZ0RBVEJnTlZIU1VFRERBS0JnZ3JCZ0VGQlFjREF6QWRCZ05WSFE0RUZnUVVPOERSCjBzaTZMVldWSDJoNDNNWXMyYlVYRHVvd0h3WURWUjBqQkJnd0ZvQVUzOVBwejFZa0VaYjVxTmpwS0ZXaXhpNFkKWkQ4d1lRWURWUjBSQVFIL0JGY3dWWVpUYUhSMGNITTZMeTluYVhSb2RXSXVZMjl0TDJOaFpHUjVjMlZ5ZG1WeQpMMk5oWkdSNUx5NW5hWFJvZFdJdmQyOXlhMlpzYjNkekwzSmxiR1ZoYzJVdWVXMXNRSEpsWm5NdmRHRm5jeTkyCk1pNDJMakF3T1FZS0t3WUJCQUdEdnpBQkFRUXJhSFIwY0hNNkx5OTBiMnRsYmk1aFkzUnBiMjV6TG1kcGRHaDEKWW5WelpYSmpiMjUwWlc1MExtTnZiVEFTQmdvckJnRUVBWU8vTUFFQ0JBUndkWE5vTURZR0Npc0dBUVFCZzc4dwpBUU1FS0RneU1XRXdPR0UyWlRNNVpXUXdaVGRqTkROaU1ESTNNV05qWmpFeU5tTXhPVFJsWWpZek16a3dGUVlLCkt3WUJCQUdEdnpBQkJBUUhVbVZzWldGelpUQWZCZ29yQmdFRUFZTy9NQUVGQkJGallXUmtlWE5sY25abGNpOWoKWVdSa2VUQWVCZ29yQmdFRUFZTy9NQUVHQkJCeVpXWnpMM1JoWjNNdmRqSXVOaTR3TUlHS0Jnb3JCZ0VFQWRaNQpBZ1FDQkh3RWVnQjRBSFlBQ0dDUzhDaFMvMmhGMGRGcko0U2NSV2NZckJZOXd6alNiZWE4SWdZMmIzSUFBQUdEClcrZEVVd0FBQkFNQVJ6QkZBaUVBbkQ1TlJLWmhGTGhDSEhESXpWNmJ3VkFxbFlQNmRXMEN3S1dEbzFqem1FWUMKSUU1WmVlSzE0b2k2SSs3ejJWUlhTVnE0L3IxNUdBRnhZYUNNRnJJMFVPampNQW9HQ0NxR1NNNDlCQU1EQTJrQQpNR1lDTVFDK3N6d1ZWbmhreGcrOFNHbXBDaWZOVFpJNUFGQkNxQ3F0RVUxazhtRTE3QWpwdFdvVUcvYkJEa2J1Cm9GUUlKdUVDTVFDbmJaZmJUTWpkUnhNOUtIcW04MlJRTEZxZG5SRFF6Mi9RNlRkMi9jeU9uY05ydW5nSFFHcEEKMXR2Mmw5VnFOcDA9Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K"
        }
      }
    }
  },
  "LogIndex": 3618623,
  "IntegratedTime": 1663694226,
  "UUID": "04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09",
  "LogID": "c0d23d6ad406973f9559f3ba2d1ca01f84147d8ffc5b8445c224f98b9591801d"
}
</code></pre>

Wir wissen nun, dass das Artefakt signiert ist und seine Signatur im Rekor-Transparenzlog-Server protokolliert wurde. Der nächste Schritt ist zu validieren, dass Signatur und Artefakt vom CI/CD-Workflow des Caddy-Projekts erzeugt wurden. Das tun wir, indem wir den öffentlichen Schlüssel aus dem JSON extrahieren, das wir von der Rekor-Abfrage erhalten haben, ihn per base64 in eine PEM-Datei decodieren und anschließend das Zertifikat mit `openssl` untersuchen. Führe den folgenden Befehl aus, um das Zertifikat aus der zuvor erhaltenen Rekor-Antwort zu extrahieren, base64 zu decodieren und das Ergebnis in einer Datei zu speichern.

<pre>
<code class="cmd"><span class="bash">rekor-cli get --uuid $(rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]') --format json | jq -r '.Body.HashedRekordObj.signature.publicKey.content' | base64 -d > cert.pem</span></code>
</pre>

Untersuche nun das Zertifikat mit `openssl` und achte auf den Abschnitt `X509v3 extensions`.

<pre><code class="cmd"><span class="bash">openssl x509 -in cert.pem -text</span>
Certificate:
...
        Issuer: O=sigstore.dev, CN=sigstore-intermediate
...
        X509v3 extensions:
            X509v3 Key Usage: critical
                Digital Signature
            X509v3 Extended Key Usage:
                Code Signing
            X509v3 Subject Key Identifier:
                3B:C0:D1:D2:C8:BA:2D:55:95:1F:68:78:DC:C6:2C:D9:B5:17:0E:EA
            X509v3 Authority Key Identifier:
                keyid:DF:D3:E9:CF:56:24:11:96:F9:A8:D8:E9:28:55:A2:C6:2E:18:64:3F

            X509v3 Subject Alternative Name: critical
                URI:https://github.com/caddyserver/caddy/.github/workflows/release.yml@refs/tags/v2.6.0
            1.3.6.1.4.1.57264.1.1:
                https://token.actions.githubusercontent.com
            1.3.6.1.4.1.57264.1.2:
                push
            1.3.6.1.4.1.57264.1.3:
                821a08a6e39ed0e7c43b0271ccf126c194eb6339
            1.3.6.1.4.1.57264.1.4:
                Release
            1.3.6.1.4.1.57264.1.5:
                caddyserver/caddy
            1.3.6.1.4.1.57264.1.6:
                refs/tags/v2.6.0
            1.3.6.1.4.1.11129.2.4.2:
                .z.x.v..`..(R.hE..k'..Eg...=.8.m..".6or....[.DS.....G0E.!..>MD.a..B.p..^..P*...um.....X..F. NYy.....#...TWIZ...y..qa....4P..
   ...
</code></pre>

Die [Extension-Werte](#x509-extensions) weisen auf die Authentizität des Artefakts hin. Die Definition der einzelnen Extensions findest du in den [Sigstore OID-Informationen](https://github.com/sigstore/fulcio/blob/a25fb09c3f0561ac43e50357fdfc427e3f0aca4a/docs/oid-info.md).

<a id="what-if-the-signature-is-not-verified"></a>
## Was, wenn die Signatur nicht verifiziert wird?

Ein Fehlschlag der Signaturverifikation zeigt an, dass das vorliegende Artefakt nicht vom CI/CD-Workflow des Caddy-Projekts auf GitHub erzeugt wurde. Wenn du die Signatur, das Zertifikat und das Artefakt hast, suchst du nach einer erfolgreichen Verifikation, die von `cosign` gemeldet wird. Alternativ kannst du mit `rekor-cli` den Rekor-Server nach dem Eintrag durchsuchen, die Zertifikats-Extensions auf die richtigen und erwarteten Werte validieren und Checksummen sowie Signaturen abgleichen. Abweichungen oder das Fehlen eines Rekor-Eintrags bedeuten entweder, dass das Artefakt nicht vom CI/CD des Caddy-Projekts erzeugt wurde, oder dass das Artefakt irgendwo zwischen dem Build-Ablauf des CI/CD, der GitHub-Releases-Seite und der Auslieferung an dich manipuliert wurde.
