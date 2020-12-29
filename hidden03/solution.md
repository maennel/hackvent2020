# HV20.H3 Hidden in Plain Sight

## Approach

The flag came with the challenge on Dec23. We start at the point where we have the backup contents decrypted and available. $PWD is at the root of the backup folder.

Various searches have lead to nowhere:
```bash
for f in $(find -type f | grep sqlite); do TABLES=$(sqlite3 -list  $f '.tables'); for t in $TABLES; do echo "### $f - $t ###"; sqlite3 $f "select * from $t;"; done ; done > db.dump
```
```bash
for f in $(find -type f | grep storedata); do TABLES=$(sqlite3 -list  $f '.tables'); for t in $TABLES; do echo "### $f - $t ###"; sqlite3 $f "select * from $t;"; done ; done > db.dump
```
```bash
find -type f -iname *.png
# ./AppDomain-com.apple.mobilesafari/Library/Safari/Thumbnails/C6467A5D-4E96-45DB-9806-21931105D87C.png
```
```bash
find -type f -iname *.jpg
for f in $(find -type f -iname *.mp4); do exiftool $f; binwalk $f; strings $f |grep 'HV20'; done
```
```bash
# Find all different file types in the folder
for f in $(find -type f); do file -b $f; done | sort | uniq | less
```
```bash
# Convert all Apple binary property list files to XML
for f in $(find -type f); do $(file -b $f | grep -qi 'Apple binary') || continue; echo "#### $f ####"; plistutil -i $f; done | less
```

And finally...:
```bash
for f in $(find -type f); do $(file -b $f | grep -qi 'sqlite') || continue; echo "#### $f ####"; strings $f; done | less
```

A base64-looking string jumped to my eye in this output...
```bash
strings ./HomeDomain/Library/AddressBook/AddressBook.sqlitedb
# includes: "http://SFYyMHtpVHVuM3NfYmFja3VwX2YwcmVuc2l4X0ZUV30=C66731B8-44AE-469B-9086-18A3A1F796B0"
echo "SFYyMHtpVHVuM3NfYmFja3VwX2YwcmVuc2l4X0ZUV30=" | base64 -d  # Produces the flag.
```

Sometimes it's worth the effort grepping for a ROT13 or, like in this case, a base64 encoded flag (or its prefix).

## Tools
- plistutil - a tool to convert Apple property list files from binary to XML and vice-versa (Ubuntu package `libplist-utils`)
- strings
- binwalk
- exiftool
- pngchunks

## Flag
`HV20{iTun3s_backup_f0rensix_FTW}`
