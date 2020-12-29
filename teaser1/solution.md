# HV20.(-1) Twelve steps of christmas

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | Bread |
| **Level**      | easy |
| **Categories** | `fun` |

## Description
On the third day of christmas my true love sent to me...

three caesar salads,
two to (the) six arguments,
one quick response.

[Message](./db47d0fc-3dde-4f97-9362-df01946699d9.txt)

## Approach
Upon first reading the challenge the three lines rang a bell, there was some Caesar code involved, something something six arguments and a quick response (so a QR code). Only the middle verse was not instantly clear to me, so I tried the obvious: compute 2^6, which is 64 - which must be related to base64.

Applying Caesar code with a rotation of 3, followed by a base64 decode and saving the outcome in a file ending in "png" (you could see the format from the file's magic bytes), one could see a QR code shine through, which did - however - not have a high enough contrast. Correcting this with an image manipulation program, I was able to scan the code and get the flag.

ROT 3 on initial message:
`Verse 3 done! Off with you! Get back to work! You're not done here...`

## Tools involved
- Cyberchef
- Binary eye
- GIMP

## Flag
`HV20{34t-sl33p-haxx-rep34t}`
