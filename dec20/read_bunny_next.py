from PIL import Image

im = Image.open("rabbits_next.png")

x=0
y=0

out = bytearray()

while y < 20:
    if y % 2 == 0:
        while x < im.width:
            if x % 2 == 0:
                out.append(0x31 if im.getpixel((x,y))[0] == 255 else 0x30)
            x+=1
    x = 0
    y+=1

with open("rabbits_next.png.bin", "wb") as fd:
    fd.write(out)
