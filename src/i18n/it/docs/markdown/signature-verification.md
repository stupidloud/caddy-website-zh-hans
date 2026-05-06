---
title: Verifica delle firme degli asset
---

# Verifica delle firme

La firma degli artefatti consente di convalidare che l'artefatto in vostro possesso sia lo stesso creato dal workflow del progetto e non sia stato modificato da una parte non autorizzata (es. attacco man-in-the-middle). La convalida fornisce una base comune, sicurezza e la certezza che tutte le parti si riferiscano allo stesso artefatto, alla stessa collezione di byte, che si tratti di un eseguibile, di una SBOM o di un file di testo.

A partire da Caddy v2.6.0, gli artefatti delle release CI/CD sono firmati utilizzando la tecnologia del progetto [Sigstore](https://www.sigstore.dev/), che emette certificati contenenti dettagli sul soggetto a cui il certificato è rilasciato. Potete iniziare ispezionando il certificato utilizzato per firmare l'artefatto di vostra scelta. I certificati sono codificati in base64, quindi dovete prima decodificarli per ricevere il file PEM. In questo esempio, lavoreremo con l'artefatto `caddy_2.6.0_checksums.txt` e assumeremo un ambiente di tipo Linux.

Iniziate scaricando i 3 file relativi all'artefatto scelto (ovvero `<l'artefatto>` che è l'artefatto effettivo la cui firma e certificati devono essere verificati, `<l'artefatto>.sig` che è la firma dell'artefatto, e `<l'artefatto>.pem` che è il certificato discendente dal certificato root di Fulcio di Sigstore). Quindi decodificate il file `.pem` scaricato dalla codifica base64 alla versione "armored":

<pre><code class="cmd bash">base64 -d < caddy_2.6.0_checksums.txt.pem > cert.pem</code></pre>

Potete ora ispezionare il certificato usando il comando `openssl`. Eseguendo `openssl x509 -in cert.pem -text` sul certificato appena decodificato, otterrete questo output (estratto):


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
</pre>

<aside class="tip" id="x509-extensions">
<a id="x509-extensions"></a>
	Notate l'uso previsto dichiarato del certificato, che è `Code Signing`. Il certificato contiene anche l'URI del workflow GitHub Actions che lo ha attivato nell'estensione `X509v3 Subject Alternative Name`, il nome del workflow GHA in `1.3.6.1.4.1.57264.1.4`, il commit da firmare in `1.3.6.1.4.1.57264.1.3`, il nome del repository in `1.3.6.1.4.1.57264.1.5` e il riferimento (ref) attivante in `1.3.6.1.4.1.57264.1.6`. Questi dettagli insieme identificano il singolo evento nell'universo per il quale il certificato deve essere utilizzato.
</aside>

Ora che abbiamo il certificato, possiamo usare la CLI `cosign` per convalidare la firma. Eseguiamo il comando seguente (notate che usa il certificato non decodificato):

<pre><code class="cmd"><span class="bash">COSIGN_EXPERIMENTAL=1 cosign verify-blob --certificate ./caddy_2.6.0_checksums.txt.pem --signature ./caddy_2.6.0_checksums.txt.sig ./caddy_2.6.0_checksums.txt</span>
tlog entry verified with uuid: 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 index: 3618623
Verified OK
</code></pre>

Passiamo ora a un altro strumento e usiamo `rekor-cli`, che interagisce con il server pubblico Rekor dove sono memorizzati i log di trasparenza. Eseguiamo:

<pre><code class="cmd bash">rekor-cli get --uuid 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 --format json | jq -r '.'
</code></pre>

L'uso di `jq` serve per abbellire l'output. Dovreste vedere un output simile a questo:

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
          "content": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURsRENDQXhtZ0F3SUJBZ0lVSXJCRm5hM1hWSmhuWnJmZU1RSHZTZ0tyKzJBd0CegYIKoZIzj0EAwMwNzEVMBMGA1UEChMMc2lnc3RvcmUuZGV2MR4wHAYDVQQDExVzaWdzdG9yZS1pbnRlcm1lZGlhdGUwHhcNMjIwOTIwMTcxNzA2WhcNMjIwOTIwMTcyNzA2WjAAMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEIu72sYUc3s+QHZF1NsSCnVRe86ZbPxiJigve2JN8AkA5ANROGQswk8yk0N8197EIJInPOjgG/5J1BoS1niWMmqOCAjgwggI0MA4GA1UdDwEB/wQEAwIHgDATBgNVHSUEDDAKBggrBgEFBQcDAzAdBgNVHQ4EFgQUO8DR0si6LVWVH2h43MYs2bUXDuowHwYDVR0jBBgwFoAU39Ppz1YkEZb5qNjpKFWixi4YZD8wYQYDVR0RAQH/BFcwVYZTaHR0cHM6Ly9naXRodWIuY29tL2NhZGR5c2VydmVyL2NhZGR5Ly5naXRodWIvd29ya2Zsb3dzL3JlbGVhc2UueW1sQHJlZnMvdGFncy92Mi42LjAwOQYKKwYBBAGDvzABAQQraHR0cHM6Ly90b2tlbi5hY3Rpb25zLmdpdGh1YnVzZXJjb250ZW50LmNvbTASBgorBgEEAYO/MAECBARwdXNoMDYGCisGAQQBg78wAQMEKDgyMWEwOGE2ZTM5ZWQwZTdjNDNiMDI3MWNjZjEyNmMxOTRlYjYzMzkwFQYKKwYBBAGDvzABBAQHUmVsZWFzZTAfBgorBgEEAYO/MAEFBBFjYWRkeXNlcnZlci9jYWRkeTAeBgorBgEEAYO/MAEGBBByZWZzL3RhZ3MvdjIuNi4wMIGKBgorBgEEAdZ5AgQCBHwEegB4AHYACGCS8ChS/2hF0dFrJ4ScRWcYrBY9wzjSbea8IgY2b3IAAAGDW+dEUwAABAMARzBFAiEAnD5NRKZhFLhCHHDIzV6bwVAqlYP6dW0CwKWDo1jzmEYCIE5ZeeK14oi6I+7z2VRXSVq4/r15GAFxYaCMFrI0UOjjMAoGCCqGSM49BAMDA2kAMGYCMQC+szwVVnhkxg+8SGmpCifNTZI5AFBCqCqtEU1k8mE17AjptWoUG/bBDkbuoFQIJuECMQCnbZfbTMjdRxM9KHqm82RQLFqdnRDQz2/Q6Td2/cyOncNrungHQGpA1tv2l9VqNp0=-----END CERTIFICATE-----"
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

Notate come il valore di `.Body.HashedRekordObj.signature.content` corrisponda al contenuto della firma generata nella nostra CI e disponibile nel file `caddy_2.6.0_checksums.txt.sig`. Inoltre, anche il certificato usato e scaricato è memorizzato nel server Rekor e disponibile nella risposta in `.Body.HashedRekordObj.signature.publicKey.content`, e corrisponde alla stringa che abbiamo nel file `caddy_2.6.0_checksums.txt.pem`. Possiamo fare un ulteriore passo avanti e verificare come `.Body.HashedRekordObj.data.hash.value` corrisponda all'output del comando `sha256sum ./caddy_2.6.0_checksums.txt`. Quindi, a questo punto abbiamo certificati corrispondenti, firme corrispondenti e checksum corrispondenti (del file contenente i checksum degli archivi ma non di se stesso; questo checksum è fornito e registrato esternamente tramite l'ecosistema Sigstore). Tutto questo è registrato pubblicamente nei log di trasparenza affinché il grande pubblico possa convalidarlo.

## Verificare l'autenticità di un artefatto

<a id="verificare-lautenticità-di-un-artefatto"></a>
E se vi venisse consegnato un artefatto che si dichiara prodotto del progetto Caddy ma non vi venissero forniti il file della firma o il certificato? Potete usare `rekor-cli` per interrogare il server Rekor riguardo all'artefatto in questione:

<pre><code class="cmd"><span class="bash">rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]'</span>
Found matching entries (listed by UUID):
362f8ecba72f432604deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09</code></pre>

Notate come l'UUID corrisponda a quello riscontrato nella sezione precedente per lo stesso file. Come fatto in precedenza, possiamo interrogare Rekor per i dettagli della voce relativa a questo UUID:

<pre><code class="cmd bash">rekor-cli get --uuid 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 --format json | jq -r '.'</code></pre>

Tuttavia, possiamo abbreviare la ricerca eseguendo questa riga per unire i due comandi separati in uno solo:

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
          "content": "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURsRENDQXhtZ0F3SUJBZ0lVSXJCRm5hM1hWSmhuWnJmZU1RSHZTZ0tyKzJBd0CegYIKoZIzj0EAwMwNzEVMBMGA1UEChMMc2lnc3RvcmUuZGV2MR4wHAYDVQQDExVzaWdzdG9yZS1pbnRlcm1lZGlhdGUwHhcNMjIwOTIwMTcxNzA2WhcNMjIwOTIwMTcyNzA2WjAAMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEIu72sYUc3s+QHZF1NsSCnVRe86ZbPxiJigve2JN8AkA5ANROGQswk8yk0N8197EIJInPOjgG/5J1BoS1niWMmqOCAjgwggI0MA4GA1UdDwEB/wQEAwIHgDATBgNVHSUEDDAKBggrBgEFBQcDAzAdBgNVHQ4EFgQUO8DR0si6LVWVH2h43MYs2bUXDuowHwYDVR0jBBgwFoAU39Ppz1YkEZb5qNjpKFWixi4YZD8wYQYDVR0RAQH/BFcwVYZTaHR0cHM6Ly9naXRodWIuY29tL2NhZGR5c2VydmVyL2NhZGR5Ly5naXRodWIvd29ya2Zsb3dzL3JlbGVhc2UueW1sQHJlZnMvdGFncy92Mi42LjAwOQYKKwYBBAGDvzABAQQraHR0cHM6Ly90b2tlbi5hY3Rpb25zLmdpdGh1YnVzZXJjb250ZW50LmNvbTASBgorBgEEAYO/MAECBARwdXNoMDYGCisGAQQBg78wAQMEKDgyMWEwOGE2ZTM5ZWQwZTdjNDNiMDI3MWNjZjEyNmMxOTRlYjYzMzkwFQYKKwYBBAGDvzABBAQHUmVsZWFzZTAfBgorBgEEAYO/MAEFBBFjYWRkeXNlcnZlci9jYWRkeTAeBgorBgEEAYO/MAEGBBByZWZzL3RhZ3MvdjIuNi4wMIGKBgorBgEEAdZ5AgQCBHwEegB4AHYACGCS8ChS/2hF0dFrJ4ScRWcYrBY9wzjSbea8IgY2b3IAAAGDW+dEUwAABAMARzBFAiEAnD5NRKZhFLhCHHDIzV6bwVAqlYP6dW0CwKWDo1jzmEYCIE5ZeeK14oi6I+7z2VRXSVq4/r15GAFxYaCMFrI0UOjjMAoGCCqGSM49BAMDA2kAMGYCMQC+szwVVnhkxg+8SGmpCifNTZI5AFBCqCqtEU1k8mE17AjptWoUG/bBDkbuoFQIJuECMQCnbZfbTMjdRxM9KHqm82RQLFqdnRDQz2/Q6Td2/cyOncNrungHQGpA1tv2l9VqNp0=-----END CERTIFICATE-----"
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

Ora sappiamo che l'artefatto è firmato e che la sua firma è registrata nel server dei log di trasparenza Rekor. Il passo successivo è convalidare che la firma e l'artefatto siano stati prodotti dal workflow CI/CD del progetto Caddy. Lo facciamo estraendo la chiave pubblica dal JSON ricevuto interrogando Rekor, decodificandola in base64 nel file PEM e ispezionando il certificato con `openssl`. Eseguite il comando seguente per estrarre il certificato dalla risposta di Rekor ricevuta in precedenza, decodificarlo e memorizzare il risultato in un file.

<pre>
<code class="cmd"><span class="bash">rekor-cli get --uuid $(rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]') --format json | jq -r '.Body.HashedRekordObj.signature.publicKey.content' | base64 -d > cert.pem</span></code>
</pre>

Ora ispezionate il certificato usando `openssl` e prestate attenzione alla sezione `X509v3 extensions`.

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

I [valori delle estensioni](#x509-extensions) indicano l'autenticità dell'artefatto. Consultate le [informazioni OID di Sigstore](https://github.com/sigstore/fulcio/blob/a25fb09c3f0561ac43e50357fdfc427e3f0aca4a/docs/oid-info.md) per la definizione di ciascuna estensione.

## E se la firma non fosse verificata?

<a id="e-se-la-firma-non-fosse-verificata"></a>
Il fallimento della verifica della firma indica che l'artefatto in questione non è stato prodotto dal workflow CI/CD del progetto Caddy su GitHub. Se disponete della firma, del certificato e dell'artefatto, dovete cercare di ottenere una verifica positiva riportata da `cosign`. In alternativa, potete usare `rekor-cli` per ispezionare la voce nel server Rekor, convalidare le estensioni del certificato per i valori corretti e attesi, e far corrispondere checksum e firme. Discrepanze o l'assenza di una voce in Rekor significano che l'artefatto non è stato prodotto dalla CI/CD del progetto Caddy, oppure che l'artefatto è stato manomesso in qualche punto tra il flusso di build della CI/CD, la pagina delle release di GitHub e la consegna a voi.
