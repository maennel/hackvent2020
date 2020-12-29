# HV20.04 Br❤️celet

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | brp64 (with the help of his daugther) |
| **Level**      | easy |
| **Categories** | `fun` |

## Description

Santa was given a nice bracelet by one of his elves. Little does he know that the secret admirer has hidden a message in the pattern of the bracelet...

![br❤️celet](./7a95aa57-0faf-4eab-bbc3-b9d350795966.jpg)

### Hints
- No internet is required - only the bracelet
- The message is encoded in binary
- Violet color is the delimiter
- Colors have a fixed order
- Missing colors matter

## Approach
Rabbit hole alert

Transcribing the 5 bracelet colors (**g**reen, **m**agenta, **p**ink, **y**ellow, **b**lue) gives the following string:
```
gmpymgbmpgmgbmpgbymgbymgbmbymbymgbympymbymmgbymgymgymbymbymgmgbmpgbmbymgbymbymgm
```

<Insert many unsuccessful attempts here>

At some point the hint with violet/magenta being the separator was published, which gave the following:

```
"m" as separator
g|py|gb|pg|gb|pgby|gby|gb|by|by|gby|py|by| |gby|gy|gy|by|by|g|gb|pgb|by|gby|by|g|
```

If `m` was the separator, 4 more colors remain. Looking at the split string, one notices that `y`, if present, is always located on the very right. `b` was always on the right, unless there is `y`, etc. So here's the fixed order from the hints.

With that, I assigned values being a power of 2 to each color (a bit randomly and in a desparate move):

| Color | Value |
| --- | --- |
| y | 1 |
| b | 2 |
| g | 4 |
| p | 8 |

Summing these up, produces the following string of hex values:
```
g|py|gb|pg|gb|pgby|gby|gb|by|by|gby|py|by| |gby|gy|gy|by|by|g|gb|pgb|by|gby|by|g|
4 9  6  C  6  F    7   6  3  3  7   9  3  0 7   5  5  3  3  4 6  E   3  7   3  4
```
which decodes to `Ilov3y0uS4n74`.

I only realised when re-working my write-up that the colors represent bits. Each color/bit can either be present/1 or absent/0. However, one first had still to discover/guess that magenta was the separator.

## Flag
`HV20{Ilov3y0uS4n74}`
