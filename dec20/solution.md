# HV20.20 Twelve steps of Christmas

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | Bread :bread: |
| **Level**      | leet |
| **Categories** | `programming`, `forensic`, `linux` |

## Description

On the twelfth day of Christmas my true love sent to me...
twelve rabbits a-rebeling,
eleven ships a-sailing,
ten (twentyfourpointone) pieces a-puzzling,
and the rest is history.

![Bunnies](./bfd96926-dd11-4e07-a05a-f6b807570b5a.png)

### Hints
You should definitely give [Bread's famous easy perfect fresh rosemary yeast black pepper bread](./7da737b4-29ba-4f4d-b882-b4ec133bc6c9.txt) a try this Christmas!

## Approach

Rabbit holes ahead! The given png file was also interpretable as a html file thanks to an early png `tEXt` chunk containing an html tag. To provoke this effect, I renamed `image.png` to `image.png.html` and opened it in a browser.

```
00000000  89 50 4e 47 0d 0a 1a 0a  00 00 00 0d 49 48 44 52  |.PNG........IHDR|
00000010  00 00 06 60 00 00 03 f3  08 06 00 00 00 a0 37 c3  |...`..........7.|
00000020  0b 00 00 00 0c 74 45 58  74 3c 68 74 6d 6c 3e 00  |.....tEXt<html>.|
00000030  3c 21 2d 2d 20 f1 a3 a4  de 00 00 1b 20 74 45 58  |<!-- ....... tEX|
00000040  74 5f 00 72 a4 de 43 87  7d b8 c4 45 72 a5 38 4b  |t_.r..C.}..Er.8K|
00000050  b0 33 b0 56 af bb 6a a2  23 a7 50 45 84 e9 58 c3  |.3.V..j.#.PE..X.|
00000060  e5 33 9f 58 7d 7c ef 38  ee f8 4c eb a2 db 98 9c  |.3.X}|.8..L.....|
00000070  e9 ed ad ba b2 7e 47 61  ed 4a 57 5b df 8f ba ad  |.....~Ga.JW[....|
00000080  a0 fb fd 33 e7 e7 35 e4  7a 5a a4 f2 88 ad 85 7b  |...3..5.zZ.....{|
00000090  35 f8 4e 6e 28 94 cd 96  85 97 25 34 c6 82 48 f9  |5.Nn(.....%4..H.|
```

In parallel, I analysed the html and most importantly the script that was executed when one clicks on the image. It checks for a query parameter `p` holding a value that SHA1 hashes to `60DB15C4E452C71C5670119E7889351242A83505`.

According to [CrackStation](https://crackstation.net/) that value is `bunnyrabbitsrule4real`.

With that parameter in the URL: `file:///home/manu/Documents/private/hackvent20/dec20/bfd96926-dd11-4e07-a05a-f6b807570b5a.png.html?p=bunnyrabbitsrule4real`, I clicked on the image to trigger the JS code, which generated a file named `11.py`. There was also another rabbit image displayed with strange dots on top, but the dots decoded to `11.py` as well.

`11.py` contains the following code:
```python
import sys
print(sys.argv[1])
print(sys.argv[2])
i = bytearray(open(sys.argv[1], 'rb').read().split(sys.argv[2].encode('utf-8') + b"\n")[-1])
j = bytearray(b"Rabbits are small mammals in the family Leporidae of the order Lagomorpha (along with the hare and the pika). Oryctolagus cuniculus includes the European rabbit species and its descendants, the world's 305 breeds[1] of domestic rabbit. Sylvilagus includes 13 wild rabbit species, among them the seven types of cottontail. The European rabbit, which has been introduced on every continent except Antarctica, is familiar throughout the world as a wild prey animal and as a domesticated form of livestock and pet. With its widespread effect on ecologies and cultures, the rabbit (or bunny) is, in many areas of the world, a part of daily life-as food, clothing, a companion, and a source of artistic inspiration.")
open('11.7z', 'wb').write(bytearray([i[_] ^ j[_%len(j)] for _ in range(len(i))]))
```
`11.py` hints towards a 7z file. 7z files have a magic file identifier being `37 7A BC AF 27 1C`. If we XOR that with "Rabbit" (which is what `11.py` does), we know what bytes to look for: `65 1b de cd 4e 68`. According to the code, this sequence is preceded by `0a`, a newline character.

I looked for this sequence in a very simple manner leveraging `hexdump` (or alternatively `xxd`):
```bash
for f in ./*; do hexdump -C $f | grep -n '0a 65 1b de cd' && echo $f; done
231074:00386a10  82 62 72 65 61 64 62 72  65 61 64 0a 65 1b de cd  |.breadbread.e...|
./bfd96926-dd11-4e07-a05a-f6b807570b5a.png
```
`0x0a` is preceded by "breadbread", which is our separator. So let's run the python script, which then produces `11.7z`:
```bash
python3 ./11.py bfd96926-dd11-4e07-a05a-f6b807570b5a.png breadbread
```

To look a bit closer into `11.7z`, let's walk through it (recursively):

```bash
binwalk -eM 11.7z
```

This extracts a ton of files... which look like a Docker image.

The file `1d66b052bd26bb9725d5c15a5915bed7300e690facb51465f2d0e62c7d644649.json` looks interesting and contains the following:
```
[...]
"RUN /bin/sh -c cp /tmp/t/bunnies12.jpg bunnies12.jpg && steghide embed -e loki97 ofb -z 9 -p \"bunnies12.jpg\\\\\\\" -ef /tmp/t/hidden.png -p \\\\\\\"SecretPassword\" -N -cf \"bunnies12.jpg\" -ef \"/tmp/t/hidden.png\" && mkdir /home/bread/flimflam && xxd -p bunnies12.jpg > flimflam/snoot.hex && rm -rf bunnies12.jpg && split -l 400 /home/bread/flimflam/snoot.hex /home/bread/flimflam/flom && rm -rf /home/bread/flimflam/snoot.hex && chmod 0000 /home/bread/flimflam && apk del steghide xxd # buildkit"
[...]
```
It seems like there was some secret embedded into a `bunnies12.jpg` image using steghide and then split up into multiple hex files. Let's undo that. 

To do so, we first need to find the right layer/directory which seems to be `ab2b751e14409f169383b5802e61764fb4114839874ff342586ffa4f968de0c1`, since it contains many files named `flom` followed by a numeric index.

I proceeded as follows to find the hidden immage:
```bash
chmod 755 ab2b751e14409f169383b5802e61764fb4114839874ff342586ffa4f968de0c1/_layer.tar.extracted/home/bread/flimflam
ls -al ab2b751e14409f169383b5802e61764fb4114839874ff342586ffa4f968de0c1/_layer.tar.extracted/home/bread/flimflam/*
# many many files here
cat flom* >snoot.hex
cat snoot.hex | xxd -r -p > ../bunnies12.jpg

steghide --extract -sf bunnies12.jpg -p "bunnies12.jpg\\\" -ef /tmp/t/hidden.png -p \\\"SecretPassword" -xf hidden.png
```

`hidden.png` contains an unreadable QR code (because the white border is missing). making it readable gives the flag(.png)!

![Flag](./flag.png)

## Flag
`HV20{My_pr3c10u5_my_r363x!!!,_7hr0w_17_1n70_7h3_X1._-_64l4dr13l}`
