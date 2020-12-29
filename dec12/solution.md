# HV20.12 Wiener waltz

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | SmartSmurf |
| **Level**      | medium |
| **Categories** | `crypto` |

## Description
### Introduction
During their yearly season opening party our super-smart elves developed an improved usage of the well known RSA crypto algorithm. Under the "Green IT" initiative they decided to save computing horsepower (or rather reindeer power?) on their side. To achieve this they chose a pretty large private exponent around 1/4 size of modulus - impossible to guess. The reduction of 75% should save a lot of computing effort while still being safe. Shouldn't it?

### Mission
Your SIGINT team captured some communication containing key exchange and encrypted data. Can you recover the original message?

[Download](./b7307460-be03-45be-bd9f-b404b48e62c9.pcap)

### Hints
Don't waste time with the attempt to brute-force the private key

## Approach

- Skim through the pcap and discard traffic on port 443 as it's encrypted and there seems to be no key exchange.
- Find that there's something going on on port 7711
- Read that traffic and find a modulus n and an e in packet 1952:

```
{
    "pubkey": {
        "n": "dbn25TSjDhUge4L68AYooIqwo0HC2mIYxK/ICnc+8/0fZi1CHo/QwiPCcHM94jYdfj3PIQFTri9j/za3oO+3gVK39bj2O9OekGPG2M1GtN0Sp+ltellLl1oV+TBpgGyDt8vcCAR1B6shOJbjPAFqL8iTaW1C4KyGDVQhQrfkXtAdYv3ZaHcV8tC4ztgA4euP9o1q+kZux0fTv31kJSE7K1iJDpGfy1HiJ5gOX5T9fEyzSR0kA3sk3a35qTuUU1OWkH5MqysLVKZXiGcStNErlaggvJb6oKkx1dr9nYbqFxaQHev0EFX4EVfPqQzEzesa9ZAZTtxbwgcV9ZmTp25MZg==",
        "e": "S/0OzzzDRdsps+I85tNi4d1i3d0Eu8pimcP5SBaqTeBzcADturDYHk1QuoqdTtwX9XY1Wii6AnySpEQ9eUEETYQkTRpq9rBggIkmuFnLygujFT+SI3Z+HLDfMWlBxaPW3Exo5Yqqrzdx4Zze1dqFNC5jJRVEJByd7c6+wqiTnS4dR77mnFaPHt/9IuMhigVisptxPLJ+g9QX4ZJX8ucU6GPSVzzTmwlDIjaenh7L0bC1Uq/euTDUJjzNWnMpHLHnSz2vgxLg4Ztwi91dOpO7KjvdZQ7++nlHRE6zlMHTsnPFSwLwG1ZxnGVdFnuMjEbPA3dcTe54LxOSb2cvZKDZqA==",
        "format": [
            "mpz_export",
            -1, //order (least significant word first)
            4, // size (word size)
            1, // endian (most significant byte first)
            0 // nail
        ]
    },
    "sessionId": "RmERqOnbsA/oua67sID4Eg=="
}
```
- Subsequent packets (starting at 1956) apparently contain encrypted data (re-ordered by `blockId`):

```
{"sessionId": "RmERqOnbsA/oua67sID4Eg==", 
"blockId": 0, 
"data": "fJdSIoC9qz27pWVpkXTIdJPuR9Fidfkq1IJPRQdnTM2XmhrcZToycoEoqJy91BxikRXQtioFKbS7Eun7oVS0yw==", "format": "plain"}

{"sessionId": "RmERqOnbsA/oua67sID4Eg==", "blockId": 1, "data": "vzwheJ3akhr1LJTFzmFxdhBgViykRpUldFyU6qTu5cjxd1fOM3xkn49GYEM+2cUVk22Tu5IsYDbzJ4/zSDfzKA==", "format": "plain"}

{"sessionId": "RmERqOnbsA/oua67sID4Eg==", "blockId": 2, "data": "fRYUyYEINA5i/hCsEtKkaCn2HsCp98+ksi/8lw1HNTP+KFyjwh2gZH+nkzLwI+fdJFbCN5iwFFXo+OzgcEMFqw==", "format": "plain"}

{"sessionId": "RmERqOnbsA/oua67sID4Eg==", "blockId": 3, "data": "+y2fMsE0u2F6bp2VP27EaLN68uj2CXm9J1WVFyLgqeQryh5jMyryLwuJNo/pz4tXzRqV4a8gM0JGdjvF84mf+w==", "format": "plain"}
```
- n and e represent the public key. Luckily, there's also a format description. Searching for `mpz_export` leads to https://gmplib.org/manual/Integer-Import-and-Export, which explains also the following parameters:
    
    - order = -1: least significant word first (i.e. we have to reverse the order of words)
    - size = 4: size in bytes of a word
    - endian = 1: most significant byte first
    - nail = 0: no impact (I believe)

- As we want to decrypt the ciphered message, which is encrypted using the RSA public key, we need to find the private key first. But how? I would have searched for this a longer time, if there wasn't the challenge title "Wiener waltz". Searching for "RSA attacks" leads to ["Coppersmith's attack"](https://en.wikipedia.org/wiki/Coppersmith%27s_attack), which references ["Wiener's attack"](https://en.wikipedia.org/wiki/Wiener%27s_attack). Alternatively, one could also search for "Wiener crypto". 
- Apparently, choosing a small private key `d` was not so smart by the elves.
- Searching for a tool, I landed at https://github.com/Ganapati/RsaCtfTool, which seems to implement the wanted attack.
- RsaCtfTool however turned out to have a picky interface, so that the output had to be verified each time.
- Running the following command produced the private key:

```bash
./RsaCtfTool.py -n 0xa76e4c6615f59993dc5bc207f590194ec4cdeb1a57cfa90c1055f811901debf486ea1716d5dafd9dfaa0a931a820bc96b4d12b95578867122b0b54a6907e4cab94535396adf9a93b037b24ddb3491d2494fd7c4c27980e5f9fcb51e258890e9125213b2bd3bf7d64466ec747f68d6afa00e1eb8fd0b8ced8687715f21d62fdd9b7e45ed00d54214242e0ac86c893696d3c016a2f213896e3047507abb7cbdc0869806c835a15f9307a594b9712a7e96dcd46b4dd9063c6d8f63bd39e52b7f5b8a0efb78163ff36b70153ae2f7e3dcf213de2361d23c270731e8fd0c21f662d42773ef3fdc4afc80ac2da62188ab0a341f00628a0207b82fa34a30e1575b9f6e5 -e 0x64a0d9a8926f672fee782f1303775c4d8c8c46cf655d167b1b56719cc54b02f0c1d3b273444eb394fefa79473bdd650e3a93bb2a708bdd5d12e0e19b4b3daf83291cb1e73ccd5a73b930d426b552afde1ecbd1b022369e9ed39b094363d2573cf2e714e817e19257b27e83d4b29b713c218a0562dffd22e39c568f1e1d47bee6a8939d2eedcebec244241c9d2e632515d5da853471e19cde8aaaaf37dc4c68e541c5a3d6b0df316923767e1ca3153f9259cbca0b808926b86af6b06084244d1a7941044d92a4443d28ba027cf576355a9d4edc174d50ba8abab0d81e737000ed16aa4de099c3f94804bbca62dd62dddde6d362e129b3e23c3cc345db4bfd0ecf --attack wiener --private

[*] Testing key /tmp/tmpzuq4981n.
[*] Performing wiener attack on /tmp/tmpzuq4981n.

Results for /tmp/tmpzuq4981n:

Private key :
-----BEGIN RSA PRIVATE KEY-----
MIIEXQIBAAKCAQEAp25MZhX1mZPcW8IH9ZAZTsTN6xpXz6kMEFX4EZAd6/SG6hcW
1dr9nfqgqTGoILyWtNErlVeIZxIrC1SmkH5Mq5RTU5at+ak7A3sk3bNJHSSU/XxM
J5gOX5/LUeJYiQ6RJSE7K9O/fWRGbsdH9o1q+gDh64/QuM7YaHcV8h1i/dm35F7Q
DVQhQkLgrIbIk2ltPAFqLyE4luMEdQert8vcCGmAbINaFfkwellLlxKn6W3NRrTd
kGPG2PY7055St/W4oO+3gWP/NrcBU64vfj3PIT3iNh0jwnBzHo/Qwh9mLUJ3PvP9
xK/ICsLaYhiKsKNB8AYooCB7gvo0ow4Vdbn25QKCAQBkoNmokm9nL+54LxMDd1xN
jIxGz2VdFnsbVnGcxUsC8MHTsnNETrOU/vp5RzvdZQ46k7sqcIvdXRLg4ZtLPa+D
KRyx5zzNWnO5MNQmtVKv3h7L0bAiNp6e05sJQ2PSVzzy5xToF+GSV7J+g9Sym3E8
IYoFYt/9IuOcVo8eHUe+5qiTnS7tzr7CRCQcnS5jJRXV2oU0ceGc3oqqrzfcTGjl
QcWj1rDfMWkjdn4coxU/klnLyguAiSa4avawYIQkTRp5QQRNkqREPSi6Anz1djVa
nU7cF01Quoq6sNgec3AA7RaqTeCZw/lIBLvKYt1i3d3m02LhKbPiPDzDRdtL/Q7P
AkB7dSuT4jDODSTwTjIp+fBefNg8SeSdShdPLILytYNJtwNDeDJb0Ye7QfSWWBMD
bI+NMT9MMq7XeTXO8zgA4aIvAoGBALlCNJVmKy1SZAHzv1yAx78vOH+lpfM6oteo
mR0QQVD/iJLsKBfecK/nSTS1XKbIYBmr3VPv4bcxV3VlSGqFJmRgF2gekzsm6fK4
Z0z3XBbJkvUUHTjM7XsbcmFJBYsYiCumrybzv7wjhu1CrSwYt8A/Imt8HltcrXZz
cfLo2g4dAoGBAOddWxAVpWghi00EAvWoVss9UcbcAYergX0Gv+zYUv9jClIFvGgT
Bmo5WZ3lpQCDRfdb4mMhd7IIALGhMPB2QPyhjoeMAgiq4wnewRgUxB2SZ+wKCc3M
PqL4iy7ZQGsrQO60MU8OxRFk8AAhTW8QYEdcszln5AdZccS5RTOQr1FpAkB7dSuT
4jDODSTwTjIp+fBefNg8SeSdShdPLILytYNJtwNDeDJb0Ye7QfSWWBMDbI+NMT9M
Mq7XeTXO8zgA4aIvAkB7dSuT4jDODSTwTjIp+fBefNg8SeSdShdPLILytYNJtwND
eDJb0Ye7QfSWWBMDbI+NMT9MMq7XeTXO8zgA4aIvAoGAK1AN3Npry6/Ua0BwkQy6
hpcOshnf4viahNoOXswzeD90TV1hU8G4DVnz8r3fp3chBJWcnscYViJkehMwdJo+
LMMwRuYos0iHraTT0BJATxlcN14BreOnvAqI32L2L24ij0er64Ukj647DTJiQ1AD
QguWrpROv9OLIJXfGNf9BEA=
-----END RSA PRIVATE KEY-----
```

- Decoding the data to be decrypted:
```bash
echo "fJdSIoC9qz27pWVpkXTIdJPuR9Fidfkq1IJPRQdnTM2XmhrcZToycoEoqJy91BxikRXQtioFKbS7Eun7oVS0yw==\
vzwheJ3akhr1LJTFzmFxdhBgViykRpUldFyU6qTu5cjxd1fOM3xkn49GYEM+2cUVk22Tu5IsYDbzJ4/zSDfzKA==\
fRYUyYEINA5i/hCsEtKkaCn2HsCp98+ksi/8lw1HNTP+KFyjwh2gZH+nkzLwI+fdJFbCN5iwFFXo+OzgcEMFqw==\
+y2fMsE0u2F6bp2VP27EaLN68uj2CXm9J1WVFyLgqeQryh5jMyryLwuJNo/pz4tXzRqV4a8gM0JGdjvF84mf+w==" | base64 -d > ../data_enc.dat
```
- And decrypting the data:
```bash
$ ./RsaCtfTool.py -n 0xa76e4c6615f59993dc5bc207f590194ec4cdeb1a57cfa90c1055f811901debf486ea1716d5dafd9dfaa0a931a820bc96b4d12b95578867122b0b54a6907e4cab94535396adf9a93b037b24ddb3491d2494fd7c4c27980e5f9fcb51e258890e9125213b2bd3bf7d64466ec747f68d6afa00e1eb8fd0b8ced8687715f21d62fdd9b7e45ed00d54214242e0ac86c893696d3c016a2f213896e3047507abb7cbdc0869806c835a15f9307a594b9712a7e96dcd46b4dd9063c6d8f63bd39e52b7f5b8a0efb78163ff36b70153ae2f7e3dcf213de2361d23c270731e8fd0c21f662d42773ef3fdc4afc80ac2da62188ab0a341f00628a0207b82fa34a30e1575b9f6e5 -e 0x64a0d9a8926f672fee782f1303775c4d8c8c46cf655d167b1b56719cc54b02f0c1d3b273444eb394fefa79473bdd650e3a93bb2a708bdd5d12e0e19b4b3daf83291cb1e73ccd5a73b930d426b552afde1ecbd1b022369e9ed39b094363d2573cf2e714e817e19257b27e83d4b29b713c218a0562dffd22e39c568f1e1d47bee6a8939d2eedcebec244241c9d2e632515d5da853471e19cde8aaaaf37dc4c68e541c5a3d6b0df316923767e1ca3153f9259cbca0b808926b86af6b06084244d1a7941044d92a4443d28ba027cf576355a9d4edc174d50ba8abab0d81e737000ed16aa4de099c3f94804bbca62dd62dddde6d362e129b3e23c3cc345db4bfd0ecf --attack wiener --uncipherfile ../data_enc.dat --output out.txt

[...]

You made it! Here is your flag: HV20{5hor7_Priv3xp_a1n7_n0_5mar7}\r\rGood luck for Hackvent, merry X-mas and all the best for 2021, greetz SmartSmurf
```

- Note it was not possible to feed the `RsaCtfTool` tool with the previously computed private key, as it would simply ignore it for some reason. This took _mcia_ and me quite some time to come to this realisation...

## Tools
- Python
- [RsaCtfTool](https://github.com/Ganapati/RsaCtfTool)
- CyberChef
- SublimeText

## Flag
`HV20{5hor7_Priv3xp_a1n7_n0_5mar7}`

## Credits
Thanks to _mcia_ for precious hints and questions that allowed to move fast during this challenge, which was really well streamlined and built in a logical fashion.
