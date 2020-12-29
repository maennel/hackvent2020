#!/usr/bin/env python
import binascii

t = b'\xde\xad\xbe\xef\xc0\x12\x34\x56\x78\x9a'

def keystream_get_char(count, pwd_hash):
    c = pwd_hash[count & 0xf]
    b = t[c % 10]
    return b ^ c ^ count

def decrypt(encrypted_data, pwd_hash):
    decrypted_data = ''
    for i in range(len(encrypted_data)):
        val = keystream_get_char(i,pwd_hash)
        decrypted_data += chr(encrypted_data[i] ^ val)
    return decrypted_data

BYTEORDER = 'little'

def calc_hash(pwd):
    # local_58 = binascii.unhexlify('68736168')
    # local_50 = binascii.unhexlify('deadbeef')
    # local_48 = binascii.unhexlify('65726f6d')
    # local_40 = binascii.unhexlify('c00ffeee')
    # local_10 = binascii.unhexlify('68736168')
    # local_18 = binascii.unhexlify('deadbeef')
    # local_20 = binascii.unhexlify('65726f6d')
    # local_28 = binascii.unhexlify('c00ffeee')
    local_58 = binascii.unhexlify('68617368')
    local_50 = binascii.unhexlify('efbeadde')
    local_48 = binascii.unhexlify('6d6f7265')
    local_40 = binascii.unhexlify('eefe0fc0')
    local_10 = binascii.unhexlify('68617368')
    local_18 = binascii.unhexlify('efbeadde')
    local_20 = binascii.unhexlify('6d6f7265')
    local_28 = binascii.unhexlify('eefe0fc0')

    for i in range(len(pwd)):
        c = int(pwd[i])

        local_50 = int.to_bytes(int.from_bytes(local_10, BYTEORDER) ^ (c * i & 0xff ^ c |
                               (c * (i + 0x31) & 0xff ^ c) << 0x18 |
                                (c * (i + 0x42) & 0xff ^ c) << 0x10 |
                                (c * (i + 0xef) & 0xff ^ c) << 0x8), 4, BYTEORDER)
        local_48 = int.to_bytes(int.from_bytes(local_18, BYTEORDER) ^ (c * i & 0x5a ^ c |
                               (c * (i + 0xc0) & 0xff ^ c) << 0x18 |
                               (c * (i + 0x11) & 0xff ^ c) << 0x10 |
                               (c * (i + 0xde) & 0xff ^ c) << 0x8), 4, BYTEORDER)
        local_40 = int.to_bytes(int.from_bytes(local_20, BYTEORDER) ^ (c * i & 0x22 ^ c |
                               (c * (i + 0xe3) & 0xff ^ c) << 0x18 |
                               (c * (i + 0xde) & 0xff ^ c) << 0x10 |
                               (c * (i + 0xd) & 0xff ^ c) << 0x8), 4, BYTEORDER)
        local_58 = int.to_bytes(int.from_bytes(local_28, BYTEORDER) ^ (c * i & 0xef ^ c |
                               (c * (i + 0x52) & 0xff ^ c) << 0x18 |
                               (c * (i + 0x24) & 0xff ^ c) << 0x10 |
                               (c * (i + 0x33) & 0xff ^ c) << 0x8), 4, BYTEORDER)
        local_28 = local_58
        local_20 = local_40
        local_18 = local_48
        local_10 = local_50

    return local_58 + local_50 + local_48 + local_40

def test_calc_hash():
    h = calc_hash(b'lovebug1')
    print(h == binascii.unhexlify('ffe4b28b699f2840ee21e51f3c23ed0f'))

def test_decrypt():
    pwd_hash = b'\xff\xe4\xb2\x8b\x69\x9f\x28\x40\xee\x21\xe5\x1f\x3c\x23\xed\x0f'
    encrypted_data = b'\x99\xf8\xbb\x66\x7f'
    encrypted_data = binascii.unhexlify(
        'a5cbfa22047498eeedea1ccac35d98619ce0a86e0a3d86fbefb03acf915ed131f8c9d95b3147ada7')
    decrypted_data = decrypt(encrypted_data, pwd_hash)
    expected = 'HV20{this-is-a-sample-flag_fort35t1ing}' + chr(0)
    print(decrypted_data == expected)


def main():
    flag_enc_enc = binascii.unhexlify('e5afe59d31aca3ca211ec379a673235edab6a08d2ed3b7b66b55857ec834227a')
    flag_enc = b''
    for i in range(0, len(flag_enc_enc), 4):
        data = flag_enc_enc[i:i+4]
        flag_enc += int.to_bytes(int.from_bytes(data, 'big') ^ int.from_bytes(b'\xde\xad\xbe\xef', 'little'), 4, 'big')

    # print(decrypt(flag_enc, calc_hash(b'xmasrocks')))
    # return

    with open('rockyou.txt', 'r', errors='ignore') as fd:
        i = 0
        p = "start"
        while p != "" or i < 2000000:
            i += 1
            p = fd.readline()[:-1]
            h = calc_hash(bytes(p, 'utf-8'))
            flag = decrypt(flag_enc, h)
            if flag.startswith('HV20'):
                # print("#######")
                print("%%%%%% Success?!")
                print("Password: %s" % p)
                print("Flag: %s" % flag)
                break
            if (i % 10000) == 0:
                print("Computed entry %s (%s)." % (str(i), p))

    print("THE END")


if __name__ == '__main__':
    test_decrypt()
    test_calc_hash()
    main()
