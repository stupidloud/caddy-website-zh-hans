---
title: "验证资产签名"
---

<a id="signature-verification"></a>
# 签名验证

资产签名可用于验证你手中的工件是否就是项目工作流创建的版本，且未被未授权方（例如中间人）篡改。该验证为所有相关方提供了共同依据、保障和确认：无论是可执行文件、SBOM，还是文本文件，大家都在引用同一份字节集合。

自 Caddy v2.6.0 起，CI/CD 发布产物使用项目的 [Sigstore](https://www.sigstore.dev/) 技术进行签名。该技术会签发包含证书授予主体详情的证书。你可以先查看用于签名目标工件的证书。证书是 base64 编码的，因此需要先解码成 PEM 文件。本文示例使用 `caddy_2.6.0_checksums.txt`，并默认 Linux 类环境。

先下载该工件对应的 3 个文件（即实际工件 `<the artifact>`、该工件签名 `<the artifact>.sig` 以及由 Sigstore 的 Fulcio root cert 派生的证书 `<the artifact>.pem`）。

然后把下载到的 `.pem` 文件 base64 解码为 armored 版本：

<pre><code class="cmd bash">base64 -d < caddy_2.6.0_checksums.txt.pem > cert.pem</code></pre>

接着可用 `openssl` 检查证书。对刚刚解码出的证书执行 `openssl x509 -in cert.pem -text` 会看到如下摘录：


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

注意该证书声明的用途是 `Code Signing`。证书还包含在 `X509v3 Subject Alternative Name` 扩展里的触发 GitHub Actions 工作流 URI、在 `1.3.6.1.4.1.57264.1.4` 里的 GHA workflow 名称、在 `1.3.6.1.4.1.57264.1.3` 里的待签 commit、在 `1.3.6.1.4.1.57264.1.5` 里的仓库名，以及在 `1.3.6.1.4.1.57264.1.6` 里的触发 ref。以上信息共同定位了该证书只对应的单一事件。

</aside>

有了证书之后，我们可以使用 `cosign` CLI 验证签名。执行以下命令（注意它使用的是未解码证书）：

<pre><code class="cmd"><span class="bash">COSIGN_EXPERIMENTAL=1 cosign verify-blob --certificate ./caddy_2.6.0_checksums.txt.pem --signature ./caddy_2.6.0_checksums.txt.sig ./caddy_2.6.0_checksums.txt</span>
tlog entry verified with uuid: 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 index: 3618623
Verified OK
</code></pre>

现在切换到 `rekor-cli`，它与存储透明日志的公共 Rekor server 交互。运行：

<pre><code class="cmd bash">rekor-cli get --uuid 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 --format json | jq -r '.'</code></pre>

使用 `jq` 是为了美化输出。你应看到类似以下内容：

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

可以看到 `.Body.HashedRekordObj.signature.content` 与 CI 生成并保存在 `caddy_2.6.0_checksums.txt.sig` 中的签名内容一致。此外，下载并使用的证书也会在 Rekor server 中存储，在响应中的 `.Body.HashedRekordObj.signature.publicKey.content` 可以找到，并且与 `caddy_2.6.0_checksums.txt.pem` 文件中的字符串一致。我们还可以进一步检查 `.Body.HashedRekordObj.data.hash.value` 与 `sha256sum ./caddy_2.6.0_checksums.txt` 命令输出是否一致。到这一步，就形成了证书、签名与校验和的匹配：该校验和是归档文件校验和清单的校验和，而非归档本身的；该校验和由 Sigstore 生态系统对外提供并记录。全部信息都公开存档在透明日志中，任何人都可验证。

<a id="verifying-authenticity-of-an-artifact"></a>
## 验证工件的真实性

如果你拿到的所谓 Caddy 项目产物未附带签名文件和证书，怎么办？你可以用 `rekor-cli` 查询 Rekor server 中对应工件的记录：

<pre><code class="cmd"><span class="bash">rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]'</span>
Found matching entries (listed by UUID):
362f8ecba72f432604deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09</code></pre>

可以看到这个 UUID 与上一段落里同一文件记录到的 UUID 相同。和前文一样，我们可以再查询这个 UUID 的 entry 详情：

<pre><code class="cmd bash">rekor-cli get --uuid 04deb84e5a73ba75ea69092c6d700eaeb869c29cae3e0cf98dbfef871361ed09 --format json | jq -r '.'</code></pre>

也可以用一行命令将两步合并，直接查询并输出详情：

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

现在我们知道该工件已签名，且签名已记录到 Rekor 透明日志服务器。下一步是验证签名和工件是否确实来自 Caddy 项目的 CI/CD workflow。操作方式是从 Rekor 返回的 JSON 中提取公钥，base64 解码到 PEM 文件，再用 `openssl` 检查证书。运行下列命令可直接从前文返回的 Rekor 响应提取证书并解码保存：

<pre>
<code class="cmd"><span class="bash">rekor-cli get --uuid $(rekor-cli search --artifact ./caddy_2.6.0_checksums.txt --format json | jq -r '.UUIDs[0]') --format json | jq -r '.Body.HashedRekordObj.signature.publicKey.content' | base64 -d > cert.pem</span></code>
</pre>

然后再用 `openssl` 检查证书，重点关注 `X509v3 extensions` 段：

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

[X.509 扩展值](#x509-extensions)可反映工件真实性。扩展定义见 [Sigstore OID 信息](https://github.com/sigstore/fulcio/blob/a25fb09c3f0561ac43e50357fdfc427e3f0aca4a/docs/oid-info.md)。

<a id="what-if-the-signature-is-not-verified"></a>
## 签名未通过时怎么办

签名验证失败通常意味着当前文件并非 GitHub 上 Caddy 项目 CI/CD workflow 产出的工件。如果你已经拿到签名、证书和工件本体，应优先看 `cosign` 报告是否显示验证成功。备选路径是使用 `rekor-cli` 查询 Rekor server 的记录，校验证书扩展是否具备正确期望值，并对比校验和和签名。若存在不匹配，或未查询到 Rekor entry，说明该工件要么不是由 Caddy 项目 CI/CD 产出，要么在 CI/CD 构建、GitHub Releases 页面到交付给你的过程中被篡改。
