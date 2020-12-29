# HV20.23 Those who make backups are cowards!

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | hardlock |
| **Level**      | hard |
| **Categories** | `crypto`, `ios` |

## Description

Santa tried to get an important file back from his old mobile phone backup. Thankfully he left a post-it note on his phone with the PIN. Sadly Rudolph thought the Apple was real and started eating it (there we go again...). Now only the first of eight digits, a **2**, is still visible...

But maybe you can do something to help him get his important stuff back?

[Download](./65195ba5-2dac-49a4-9606-c9d8733bebcf.rar)

### Hints
- If you get stuck, call Shamir

## Approach

It seems, we're given an encrypted iPhone backup. Unpacking the archive produces a bunch of encrypted files and some with a more telling filename:
```
$ ls -al
total 16768
drwxr-xr-x 2 hacker hacker   28672 Dec 16 21:47 .
drwxr-xr-x 7 hacker hacker    4096 Dec 23 02:05 ..
-rw-r--r-- 1 hacker hacker     240 Dec 16 21:47 000cae3437db21095a85771716e6874f92ce7593
-rw-r--r-- 1 hacker hacker     144 Dec 16 21:47 012707a2ae34d77a28b16a9e443b780ea4e6b0aa
-rw-r--r-- 1 hacker hacker   14224 Dec 16 21:47 01a14737bf725839e60201704f5e0447e23800a6
-rw-r--r-- 1 hacker hacker      48 Dec 16 21:47 02080c751f0cd98738a2e9ccf7c133f0197865fa
-rw-r--r-- 1 hacker hacker     576 Dec 16 21:47 02dcc29d169dda989f3402fe07d8b6526d6fb1ac
-rw-r--r-- 1 hacker hacker      48 Dec 16 21:47 0354ef572fa6f5f20370be41aa816bd69cb2a642
-rw-r--r-- 1 hacker hacker     272 Dec 16 21:47 0468d26ad5dc28df372736abb757ed6457c7eed1
[...]
-rw-r--r-- 1 hacker hacker   1399 Dec 16 21:47 DDNABackup.plist
-rw-r--r-- 1 hacker hacker   8579 Dec 16 21:47 Info.plist
-rw-r--r-- 1 hacker hacker 101463 Dec 16 21:47 Manifest.mbdb
-rw-r--r-- 1 hacker hacker   9221 Dec 16 21:47 Manifest.plist
-rw-r--r-- 1 hacker hacker    189 Dec 16 21:47 Status.plist
```

Some web searching brought me to the following article https://medium.com/taptuit/breaking-into-encrypted-iphone-backups-4dacc39403f0, which in turn leads to https://github.com/philsmd/itunes_backup2hashcat to retrieve the hash of the backup encryption.
```bash
./itunes_backup2hashcat.pl ../5e8dfbc7f9f29a7645d66ef70b6f2d3f5dad8583/Manifest.plist
$itunes_backup$*9*892dba473d7ad9486741346d009b0deeccd32eea6937ce67070a0500b723c871a454a81e569f95d9*10000*0834c7493b056222d7a7e382a69c0c6a06649d9a**
```

Using that hash combined with the information given in the challenge description, we can craft a `hashcat` command:

The password/PIN to crack:
- has 8 positions
- all digits
- the first digit is "2"
- has known format, hence we can run a mask attack (sub-type of brute-force attack, hence `-a 3`)

```bash
hashcat -m 14700 -o recovered.hash -a 3 hash.pwd 2?d?d?d?d?d?d?d
```

The resulting string is:
```
$itunes_backup$*9*892dba473d7ad9486741346d009b0deeccd32eea6937ce67070a0500b723c871a454a81e569f95d9*10000*0834c7493b056222d7a7e382a69c0c6a06649d9a**:20201225
```
The PIN is `20201225` (who would have thought someone would shoot beyond the limits of this HackVent...?).

Some other resources, I stumbled over for this first phase of this challenge (which could be useful for other CTFs) are:
- Mapping SHA1 hashes to file names: https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup/
- Read out Manifest.mbdb: https://stackoverflow.com/questions/3085153/how-to-parse-the-manifest-mbdb-file-in-an-ios-4-0-itunes-backup
- Decrypt files: https://stackoverflow.com/questions/1498342/how-to-decrypt-an-encrypted-apple-itunes-iphone-backup

Using `backup_tool.py` from https://github.com/dinosec/iphone-dataprotection we can then decrypt the files from the backup. the library, however, requires a small patch first:
```diff
$ git diff crypto/aeswrap.py
diff --git a/python_scripts/crypto/aeswrap.py b/python_scripts/crypto/aeswrap.py
index 75dbb84..4ef2ca6 100644
--- a/python_scripts/crypto/aeswrap.py
+++ b/python_scripts/crypto/aeswrap.py
@@ -26,7 +26,7 @@ def AESUnwrap(kek, wrapped):
         for i in reversed(xrange(1,n+1)):
             todec = pack64bit(A ^ (n*j+i))
             todec += pack64bit(R[i])
-            B = AES.new(kek).decrypt(todec)
+            B = AES.new(kek, AES.MODE_ECB).decrypt(todec)
             A = unpack64bit(B[:8])
             R[i] = unpack64bit(B[8:])
```

Let's move on to decrypt the backup folder:
```
python backup_tool.py ../../5e8dfbc7f9f29a7645d66ef70b6f2d3f5dad8583/
```

In the reconstructed backup, we find plenty of jpg files and sqlite files

```bash
# Find all image files (jpg, png, tiff, etc.) and print out their filename
for f in $(find -type f); do $(file -b $f | grep -qi 'image') || continue; echo $f; done
# Find all SQLite files and dump them into a single file
for f in $(find -type f); do $(file -b $f | grep -qi 'sqlite') || continue; TABLES=$(sqlite3 -list  $f '.tables'); for t in $TABLES; do echo "### $f - $t ###"; sqlite3 $f "select * from $t;"; done ; done > db.dump
```

Looking at the images, a promising one jumped to my eyes: `./5e8dfbc7f9f29a7645d66ef70b6f2d3f5dad8583_extract/CameraRollDomain/Media/DCIM/100APPLE/IMG_0003.JPG` - which was unfortunately only Rick Astley singing his song... -\_-



SQLite3 file `./5e8dfbc7f9f29a7645d66ef70b6f2d3f5dad8583_extract/HomeDomain/Library/AddressBook/AddressBook.sqlitedb` looks promising, too:
```sql
sqlite> select * from ABPerson;
2|M||||||||6344440980251505214334711510534398387022222632429506422215055328147354699502|0||||||AÜ|AÜ|629844018|629844018|||||0|||A|A|0|0|-1||1|50808F95-A166-4290-97D3-3B9FA17073EB:ABPerson|||||||||
3|N||||||||77534090655128210476812812639070684519317429042401383232913500313570136429769|0||||||CÜ|CÜ|629844041|629844090|||||0|||C|C|0|0|-1||1|315422BB-B907-425D-9D68-7A4D94906B1B:ABPerson|||||||||
```

`M` and `N` - remembering our hint to call Shamir, this could be an RSA message and a corresponding modulus (see https://en.wikipedia.org/wiki/RSA_(cryptosystem)#Operation).

In order to reverse the message to its original, the modulus must be factorizable so that we can derive the private key.

Note that a similar challenge appeared HackVent 2018 already and is nicely documented on *mcia's* blog: https://sigterm.ch/2018/12/25/hackvent-2018-write-up/#Hidden_Flag_3

Using factorDB, we're able to quickly factorize the modulus: http://factordb.com/index.php?query=77534090655128210476812812639070684519317429042401383232913500313570136429769, giving us `p` and `q`:
```
p: 250036537280588548265467573745565999443
q: 310091043086715822123974886007224132083
```

We also assume `e` to be 65537, as this is a common value for the parameter.

With that, we can now write a solver in python doing the math for us:
- compute `phi`
- compute the inverse of `e` given `phi`, being `d`
- decrypt `m` given `d` and `n`

...which results in the flag.

The solver script looks as follows:
```python
import gmpy2
import binascii

m = 6344440980251505214334711510534398387022222632429506422215055328147354699502
n = 77534090655128210476812812639070684519317429042401383232913500313570136429769
p = 250036537280588548265467573745565999443
q = 310091043086715822123974886007224132083
e = 65537

'''
Credits: https://sigterm.ch/2018/12/25/hackvent-2018-write-up/#Hidden_Flag_3
m^d % n
x^e % n = m

'''

def encrypt(e, n, message):
    return pow(int(message.encode("hex"), 16), e, n)
 
 
def decrypt(d, n, message):
    res = pow(message, d, n)
    return binascii.unhexlify('{0:02x}'.format(res))

phi = (p-1) * (q-1)
d = gmpy2.invert(e, phi)
plain = decrypt(d, n, m)

print(plain)
```

## Flag
`HV20{s0rry_n0_gam3_to_play}`
