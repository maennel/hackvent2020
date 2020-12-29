#!/usr/bin/env python

import struct
# from des import DesKey

bmp_header = open("c9_comment.tar.bmp", "rb").read()

print("Header length: \t\t" + str(len(bmp_header)))
file_size = struct.unpack("<L", bmp_header[0x2:0x6])[0]
data_size = struct.unpack("<L", bmp_header[0x22:0x26])[0]
print("Image file size: \t"+ str(file_size))
print("Image data size: \t" +str(data_size))


with open("part9.tar", "rb") as fd:
    data = fd.read()

print("Part 9 size: \t\t" + str(len(data)))

with open("out.bmp", "w+b") as fd:
    fd.write(bmp_header + (data[len(bmp_header)+16:]))

# initial=data[8:16]
# key=DesKey(b'\x00'*8)
# key=DesKey(data[16:24])
# key=DesKey(initial)
# assert(key.is_single())
# # decrypted=key.decrypt(data[64:], initial=initial)
# decrypted=key.decrypt(data[16:], initial=b'\x00'*8)
# print("Decrypted siez: \t" + str(len(decrypted)))

# # print(bmp_header+decrypted)

# with open("out_decrypted.bmp", "w+b") as fd:
#     fd.write(bmp_header + decrypted)
