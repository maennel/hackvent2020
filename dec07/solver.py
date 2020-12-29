import base64
from hashlib import sha1

for a in range(0, 9):
    for b in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/":
        try:
            flag = base64.b64decode("SFYyMHtyMz{}zcnMzXzNuZzFuMzNyMW5n{}200ZDNfMzRzeX0=".format(a, b))
        except UnicodeDecodeError:
            print("Error with a={} and b={}".format(a, b))
            continue
        key = base64.b64decode("Q1RGX3hsNHoxbmnf")
        arr = bytearray()

        for i in range(0, len(flag)):
            arr.append(flag[i] ^ key[i % len(key)])

        if "6b4077ca9adac8713f014294cf17fec6c54f150a" == sha1(arr).hexdigest():
            print(flag)
            print("Success with a={} and b={}".format(a, b))
