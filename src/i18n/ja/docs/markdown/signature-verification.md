---
title: アセット署名を検証する
---

<a id="signature-verification"></a>
# 署名検証

Artifact signing により、手元にある artifact がプロジェクトの workflow によって作成されたものと同一であり、権限のない第三者（例: man-in-the-middle）によって変更されていないことを検証できます。この検証は、すべての当事者が同じ artifact、つまり実行ファイル、SBOM、テキストファイルなどの同じバイト列を参照しているという共通基盤、保証、知識を提供します。

Caddy v2.6.0 以降、CI/CD release artifact はプロジェクトの [Sigstore](https://www.sigstore.dev/) 技術を使って署名されています。Sigstore は、証明書の発行対象に関する詳細を含む証明書を発行します。まず、選択した artifact の署名に使われた証明書を調べることから始められます。証明書は base64 エンコードされているため、PEM ファイルを得るには最初に base64 デコードする必要があります。この例では `caddy_2.6.0_checksums.txt` artifact を使い、Linux 風の環境を想定します。

まず、選択した artifact に関係する 3 つのファイルをダウンロードします（つまり `<the artifact>` は実際の artifact、`<the artifact>.sig` は artifact の署名、`<the artifact>.pem` は Sigstore の Fulcio による root cert から派生した証明書です）。次に、ダウンロードした `.pem` ファイルを base64 デコードして armored version にします。

<pre><code class="cmd bash">base64 -d < caddy_2.6.0_checksums.txt.pem > cert.pem</code></pre>

これで `openssl` コマンドを使って証明書を調べられます。先ほどデコードした証明書に対して `openssl x509 -in cert.pem -text` を実行すると、次のような抜粋が表示されます。


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

証明書に記載された intended usage が `Code Signing` であることに注目してください。証明書には、`X509v3 Subject Alternative Name` extension 内のトリガー元 Github Actions workflow の URI、`1.3.6.1.4.1.57264.1.4` 内の GHA workflow 名、`1.3.6.1.4.1.57264.1.3` 内の署名対象 commit、`1.3.6.1.4.1.57264.1.5` 内の repo 名、`1.3.6.1.4.1.57264.1.6` 内のトリガー元 ref も含まれます。これらの詳細を合わせると、その証明書が使われるべき唯一のイベントを正確に特定できます。

</aside>

証明書を得たので、`cosign` cli を使って署名を検証できます。次のコマンドを実行します（デコードしていない証明書を使っている点に注意してください）。

<pre><code class="cmd"><span class="bash">COSIGN_EXPERIMENTAL=1 cosign verify-blob --certificate ./caddy_2.6.0_checksums.txt.pem --signature ./caddy_2.6.0_checksums.txt.sig ./caddy_2.6.0_checksums.txt</span>
tlog entry verified with uuid: 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 index: 3618623
Verified OK
</code></pre>

次に cli ツールを切り替え、透明性ログを保存している公開 Rekor server とやり取りする `rekor-cli` を使います。次を実行します。

<pre><code class="cmd bash">rekor-cli get --uuid 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 --format json | jq -r '.'
</code></pre>

`jq` は出力を見やすく整形するために使っています。次のような出力が表示されます。

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

`.Body.HashedRekordObj.signature.content` の値が、CI で生成され `caddy_2.6.0_checksums.txt.sig` ファイルとして利用できる署名の内容と一致していることに注目してください。さらに、使用されダウンロードされた証明書も Rekor server に保存されており、レスポンスの `.Body.HashedRekordObj.signature.publicKey.content` で利用できます。これは `caddy_2.6.0_checksums.txt.pem` ファイル内の文字列と一致します。さらに一歩進めて、`.Body.HashedRekordObj.data.hash.value` が `sha256sum ./caddy_2.6.0_checksums.txt` コマンドの出力と一致することも確認できます。ここまでで、証明書、署名、チェックサムが一致していることが分かりました（これは archive のチェックサムを含むファイル自体のチェックサムであり、archive 自体のチェックサムではありません。このチェックサムは Sigstore ecosystem を通じて外部から提供され記録されています）。これらはすべて、一般の人々が検証できるよう透明性ログに公開記録されています。

<a id="verifying-authenticity-of-an-artifact"></a>
## Artifact の真正性を検証する

Caddy プロジェクトの成果物だと主張される artifact を渡されたものの、署名ファイルや証明書を渡されていない場合はどうすればよいでしょうか。`rekor-cli` を使って、対象 artifact について Rekor server を問い合わせることができます。

<pre><code class="cmd"><span class="bash">rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]'</span>
Found matching entries (listed by UUID):
362f8ecba72f432604deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09</code></pre>

UUID が、同じファイルについて前のセクションで見たものと一致していることに注目してください。前のセクションと同じように、この UUID の entry details を Rekor に問い合わせられます。

<pre><code class="cmd bash">rekor-cli get --uuid 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 --format json | jq -r '.'</code></pre>

ただし、次の 1 行を実行すれば、2 つの別々のコマンドを 1 つの one-liner にまとめて lookup を短縮できます。

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

これで artifact が署名されており、その署名が Rekor transparency log server に記録されていることが分かりました。次の手順は、署名と artifact が Caddy プロジェクトの CI/CD workflow による成果物であることを検証することです。Rekor への問い合わせで受け取った JSON から公開鍵を抽出し、base64 デコードして PEM ファイルにし、`openssl` で証明書を調べます。先ほど受け取った Rekor レスポンスから証明書を抽出し、base64 デコードして、結果をファイルに保存するには、次のコマンドを実行します。

<pre>
<code class="cmd"><span class="bash">rekor-cli get --uuid $(rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]') --format json | jq -r '.Body.HashedRekordObj.signature.publicKey.content' | base64 -d > cert.pem</span></code>
</pre>

次に `openssl` で証明書を調べ、`X509v3 extensions` セクションに注目します。

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

[extension values](#x509-extensions) は artifact の真正性を示します。各 extension の定義については [Sigstore OID information](https://github.com/sigstore/fulcio/blob/a25fb09c3f0561ac43e50357fdfc427e3f0aca4a/docs/oid-info.md) を参照してください。

<a id="what-if-the-signature-is-not-verified"></a>
## 署名が検証されない場合は？

署名検証の失敗は、手元の artifact が GitHub 上の Caddy プロジェクトの CI/CD workflow によって生成されたものではないことを示します。署名、証明書、artifact を持っている場合は、`cosign` による検証成功の報告を探します。別の方法として、`rekor-cli` を使って Rekor server の entry を調べ、証明書 extension が正しく期待通りの値であることを検証し、チェックサムと署名を照合できます。不一致や Rekor entry の欠如は、その artifact が Caddy プロジェクトの CI/CD によって生成されたものではないか、CI/CD の build flow、GitHub releases page、そしてあなたへの配送経路のどこかで artifact が改ざんされたことを意味します。
