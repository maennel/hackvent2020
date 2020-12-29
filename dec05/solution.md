# HV20.05 Image DNA

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | blaknyte0 |
| **Level**      | easy |
| **Categories** | `forensics`, `crypto` |

## Description

Santa has thousands of Christmas balls in stock. They all look the same, but he can still tell them apart. Can you see the difference?

![Christmas ball 1](./6bbc452b-6a32-4a72-b74f-07b7ad7b181d.jpg)
![Christmas ball 2](./cf505372-330b-4b34-a95b-59fa33db37f8.jpg)

## Approach

`strings` on the images gave a long string in the end of both files including only chars A, C, G and T. Googling led to https://www.genome.gov/genetics-glossary/acgt. 
Ok, the challenge's title already hinted it, so now it's confirmed: it's got something to do with DNA.

```
$ strings 6bbc452b-6a32-4a72-b74f-07b7ad7b181d.jpg | tail -n1
CTGTCGCGAGCGGATACATTCAAACAATCCTGGGTACAAAGAATAAAACCTGGGCAATAATTCACCCAAACAAGGAAAGTAGCGAAAAAGTTCCAGAGGCCAAA

$ strings cf505372-330b-4b34-a95b-59fa33db37f8.jpg | tail -n1
ATATATAAACCAGTTAATCAATATCTCTATATGCTTATATGTCTCGTCCGTCTACGCACCTAATATAACGTCCATGCGTCACCCCTAGACTAATTACCTCATTC
```

I stumbled on [DNA-Sharp](https://esolangs.org/wiki/DNA-Sharp) was a deeeeep rabbit hole - but I should have reacted earlier, when at least one of the two strings did not parse correctly.

Further rabbit holes were ahead: The following pages both indicated some mapping between ACGT and 0-3 combinations.
- https://ch.mathworks.com/matlabcentral/fileexchange/68817-dna-crytography-with-encoding-and-decoding-text-message
- https://github.com/jokergoo/Crypt-DNASequence ---> unrelated, but the same mapping ACGT=>bin.

More information was needed. Running `binwalk` on the files resulted in a file named `A` on one of the files. It contained `00`.

Also, diffing the two images using ImageMagick (`compare image1 image2 -compose src diff.png`) shows that one of them contains slightly different data:
![Diff](./diff.png)

Steghide to the help! Running `steghide extract -sf 6bbc452b-6a32-4a72-b74f-07b7ad7b181d.jpg` (without any password) produced a file `T.png` showing only `11`.

Finally, since it's an easy challenge I tried mapping each of the 4 characters to two bits as follows: 
```bash
echo <ACGT-string> | sed 's/A/00/g;s/C/01/g;s/G/10/g;s/T/11/g'`
```

XOR the two resulting strings (in binary format) - and tadaa - [the flag](https://gchq.github.io/CyberChef/#recipe=From_Binary%28'None'%29XOR%28%7B'option':'Binary','string':'0111101101100110001001101000110001001111010000000100001101011110101011000100000010000011000000000101111010100100001100001111010001010100000001000010100000001011001001100000000000101111010100100010100101000000'%7D,'Standard',false%29&input=MDAxMTAwMTEwMDExMDAwMDAwMDEwMTAwMTAxMTExMDAwMDExMDEwMDAwMTEwMDExMDExMTAxMTEwMDExMDAxMTEwMDExMTExMDAxMTAwMTExMDExMDExMTAxMTAxMTAxMDExMDExMDExMTAwMDExMDAxMDAwMTAxMTEwMDAwMTEwMDExMDAwMDAxMTAxMTAxMDEwMDExMTAwMTEwMTEwMTAwMDEwMTAxMDExMTAwMTAwMDAxMTEwMDAwMTExMTAwMDEwMTExMDEwMDExMTEwMQ)

## Tools
- CyberChef
- Sed
- strings
- binwalk
- ImageMagick (compare)

## Flag
`HV20{s4m3s4m3bu7diff3r3nt}`
