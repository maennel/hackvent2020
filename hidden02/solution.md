# HV20.H2 Oh, another secret!

Hidden 2 was (not so) hidden in Dec14's challenge.

Looking a bit closer what happens in the MBR using Ghidra shows that there's two arrays of values being XORed:

At 0xf4:
`58 57 97 83 6f 65 76 36 5e 67 5d 64 4d 3c a5 75 f3 7c e0 1f 06 d1 ad 66 24 78 3c a3 e7`
...and staring 0x9e:
`55 5d df d5 5d 55 0d 5e 6f 03 39 57 23 11 94 1b de 0c 8c 2b 37 bf 80 53 15 4e 54 94 9a`

## Flag
`HV20{h1dd3n-1n-pl41n-516h7}`
