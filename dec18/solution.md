# HV20.18 Santa's lost home

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | darkstar |
| **Level**      | hard |
| **Categories** | `linux`, `forensic`, `crypto` |


## Description
Santa has forgotten his password and can no longer access his data. While trying to read the hard disk from another computer he also destroyed an important file. To avoid further damage he made a backup of his home partition. Can you help him recover the data.

When asked he said the only thing he remembers is that he used his name in the password... I thought this was something only a real human would do...

[Backup](./9154cb91-e72e-498f-95de-ac8335f71584.img.bz2)

### Hints
- It's not rock-science, it's station-science!
- Use default options

## Approach
Unwrap the bz2 file: 
```bash
bzip --decompress --keep 9154cb91-e72e-498f-95de-ac8335f71584.img.bz2
```

Mount the filesystem:
```bash
mkdir santa
mount 9154cb91-e72e-498f-95de-ac8335f71584.img ./santa
```

Explore and discover that the important file that's missing is the `wrapped-passphrase` (see https://wiki.archlinux.org/index.php/ECryptfs#Mounting)
```bash
ls -al ./santa/.ecryptfs/santa/.ecryptfs/
```
The wrapped passphrase can be unwrapped using a user defined password and then used to decrypt the ecryptfs data.

With the passphrase missing, we were also blocked at the following stage:
```bash
root@hlkali:/home/hacker/Documents/hackvent20/dec18/santa# ecryptfs-recover-private 
INFO: Searching for encrypted private directories (this might take a while)...
INFO: Found [/home/hacker/Documents/hackvent20/dec18/santa/.ecryptfs/santa/.Private].
Try to recover this directory? [Y/n]: Y
INFO: Could not find your wrapped passphrase file.
INFO: To recover this directory, you MUST have your original MOUNT passphrase.
INFO: When you first setup your encrypted private directory, you were told to record
INFO: your MOUNT passphrase.
INFO: It should be 32 characters long, consisting of [0-9] and [a-f].

Enter your MOUNT passphrase: 
```

The high-level flow for generating the wrapped passphrase, as explained in the following nice article: https://research.kudelskisecurity.com/2015/08/25/how-to-crack-ubuntu-disk-encryption-and-passwords/ looks as follows:
- Wrapping key = first16bytes(hash(salt + password))
- Wrapping key signature = hash(Wrapping Key)
- Wrapped passphrase = AES-128(wrapping key, passphrase)

From the wrapped passphrase, one can derive a hash with the following format, which can then be used to brute-force the wrapping password using something like JohnTheRipper or HashCat: `$ecryptfs$0$1$0011223344556677$21ff10301b5457e1`

I was lucky and, by accident, found the following at the very end of the `.img` file something that looked as if it was a `wrapped-passphrase`:
```hexdump
05c00000  3a 02 a7 23 b1 2f 66 bc  fe aa 30 35 31 31 31 39  |:..#./f...051119|
05c00010  62 30 62 61 63 65 30 61  62 36 db b8 dd 00 47 8f  |b0bace0ab6....G.|
05c00020  a1 89 ae c3 cb e5 22 94  f4 ca d1 57 fe 2d 78 65  |......"....W.-xe|
05c00030  67 74 61 1f 32 1b 99 30  6f c7 
```

![wrapped-passphrase file format](https://cybermashup.files.wordpress.com/2015/08/wrappedpassphrasev2.png)

Gives the hash: `$ecryptfs$0$1$a723b12f66bcfeaa$051119b0bace0ab6`

From the challenge description it became obvious, that the password was **not** in the famous rockyou wordlist, but in a different one. Searching for `hashcat wordlist station` brought me to the right page. Now, download the wordlist from CrackStation (human passwords only, as indicated in the challenge description): https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm
Filter the wordlist accoring to the hint given in the challenge description to consider only passwords with some derivation of `santa` in it: `grep -i -e '[s5][a4@]n[t7][4a@]' crackstation-human-only.txt > crackstation-human-santa-only.txt`

Confirm the hash format with: https://hashcat.net/wiki/doku.php?id=frequently_asked_questions#how_can_i_identify_the_hash_type

Run hashcat: `hashcat --hash-type 12200 ./ecryptfs_hash.txt ./crackstation-human-santa-only.txt`

Get the password 🎉:
```
$ecryptfs$0$1$a723b12f66bcfeaa$051119b0bace0ab6:think-santa-lives-at-north-pole
```

Re-create the `wrapped-passphrase` file:
```bash
echo -n "3a02a723b12f66bcfeaa30353131313962306261636530616236dbb8dd00478fa189aec3cbe52294f4cad157fe2d78656774611f321b99306fc7"| xxd -r -p > santa/.ecryptfs/santa/.ecryptfs/wrapped-passphrase
```
And recover the `.Private` directory:
```bash
$ ecryptfs-recover-private 
INFO: Searching for encrypted private directories (this might take a while)...
INFO: Found [/home/hacker/Documents/hackvent20/dec18/santa/.ecryptfs/santa/.Private].
Try to recover this directory? [Y/n]: Y
INFO: Found your wrapped-passphrase
Do you know your LOGIN passphrase? [Y/n] Y
INFO: Enter your LOGIN passphrase...
Passphrase: 
Inserted auth tok with sig [7b4f67408a83013e] into the user session keyring
INFO: Success!  Private data mounted at [/tmp/ecryptfs.Racizvrv].
INFO: Found [/home/hacker/.Private].
Try to recover this directory? [Y/n]: 
```

Retrieve the flag at the temporarily mounted folder:
```bash
$ cat /tmp/ecryptfs.Racizvrv/flag.txt 
HV20{a_b4ckup_of_1mp0rt4nt_f1l35_15_3553nt14l}
```

## Tools
- hexdump
- hashcat
- ecryptfs-utils

## Flag
`HV20{a_b4ckup_of_1mp0rt4nt_f1l35_15_3553nt14l}`
