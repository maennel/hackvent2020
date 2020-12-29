# HV20.03 Packed gifts

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | darkstar |
| **Level**      | easy |
| **Categories** | `crypto` |

## Description
One of the elves has unfortunately added a password to the last presents delivery and we cannot open it. The elf has taken a few days off after all the stress of the last weeks and is not available. Can you open the package for us?

We found the following packages:

[Package 1](./790ccd6f-cd84-452c-8bee-7aae5dfe2610.zip)
[Package 2](./941fdd96-3585-4fca-a2dd-e8add81f24a1.zip)

## Approach

In an attempt to unzip the two files we realise that Package 2 (`941fdd96-3585-4fca-a2dd-e8add81f24a1.zip`) is password protected in contrast to Package 1.

Runnin `unzip -vl 790ccd6f-cd84-452c-8bee-7aae5dfe2610.zip` and `unzip -vl 941fdd96-3585-4fca-a2dd-e8add81f24a1.zip`, we also see that the password protected zip file contains a file called `flag.bin`, which is not present in the other package. All other files seem to be named the same and have the same timestamp. However, CRCs are different - with one exception.

Given that we have to deal with legacy zip file encryption (and not AES encryption, we can find that out if `7z l -slt <zip file>` prints something like `"ZipCrypto Deflate"`) and if there is indeed a same file in both archives, we can run a "known-plaintext" attack to find the encrypting key and use it to extract the flag from the encrypted zip file.

Comparing CRCs, we find that both files `0053.bin` have the matching CRC `fcd6b08a`.

Let's start a Plaintext attack on file 0053.bin using `bkcrack` (the result of some Google Fu): 
```
bkcrack -C 941fdd96-3585-4fca-a2dd-e8add81f24a1.zip -c 0053.bin -P 790ccd6f-cd84-452c-8bee-7aae5dfe2610.zip -p 0053.bin
```

`bkcrack` finds encrypting keys `2445b967 cfb14967 dceb769b`. To extract the file we run 
```
bkcrack -C 941fdd96-3585-4fca-a2dd-e8add81f24a1.zip -c flag.bin -k 2445b967 cfb14967 dceb769b -d flag_deflated.txt
```
Inflate the resulting file (see flag.b64.txt): `python3 inflate.py < flag_deflated.txt > flag.b64.txt`

The inflating script was taken from https://github.com/kimci86/bkcrack/blob/master/tools/inflate.py:
```python
import sys
import zlib

def inflate(data):
    """Returns uncompressed data."""
    return zlib.decompress(data, -zlib.MAX_WBITS)

def main():
    """Read deflate compressed data from stdin and write uncompressed data to stdout."""
    sys.stdout.buffer.write(inflate(sys.stdin.buffer.read()))

if __name__ == "__main__":
    main()
```

Base64 decode the resulting string (see flag.txt): `base64 -d flag.b64.txt > flag.txt`

## Tools
- [bkcrack](https://github.com/kimci86/bkcrack)


## Flag
`HV20{ZipCrypt0_w1th_kn0wn_pla1ntext_1s_easy_t0_decrypt}`
