#!/usr/bin/env python3.7
# coding: UTF-8

from __future__ import print_function
from __future__ import division

import argparse
import getpass
import os.path
import pprint
import random
import shutil
import sqlite3
import string
import struct
import tempfile
from binascii import hexlify

import Crypto.Cipher.AES # https://www.dlitz.net/software/pycrypto/
import biplist
import fastpbkdf2
from biplist import InvalidPlistException


def main():
    ## Parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('--backup-directory', dest='backup_directory',
                    default='testdata/encrypted')
    parser.add_argument('--password-pipe', dest='password_pipe',
                        help="""\
Keeps password from being visible in system process list.
Typical use: --password-pipe=<(echo -n foo)
""")
    parser.add_argument('--no-anonymize-output', dest='anonymize',
                        action='store_false')
    args = parser.parse_args()
    global ANONYMIZE_OUTPUT
    ANONYMIZE_OUTPUT = args.anonymize
    if ANONYMIZE_OUTPUT:
        print('Warning: All output keys are FAKE to protect your privacy')

    manifest_file = os.path.join(args.backup_directory, 'Manifest.plist')
    with open(manifest_file, 'rb') as infile:
        manifest_plist = biplist.readPlist(infile)
    keybag = Keybag(manifest_plist['BackupKeyBag'])
    # the actual keys are unknown, but the wrapped keys are known
    keybag.printClassKeys()

    if args.password_pipe:
        password = readpipe(args.password_pipe)
        if password.endswith(b'\n'):
            password = password[:-1]
    else:
        password = getpass.getpass('Backup password: ').encode('utf-8')

    ## Unlock keybag with password
    if not keybag.unlockWithPasscode(password):
        raise Exception('Could not unlock keybag; bad password?')
    # now the keys are known too
    keybag.printClassKeys()

    ## Decrypt metadata DB
    print(manifest_plist.keys())
    manifest_key = manifest_plist['ManifestKey'][4:]
    with open(os.path.join(args.backup_directory, 'Manifest.db'), 'rb') as db:
        encrypted_db = db.read()

    manifest_class = struct.unpack('<l', manifest_plist['ManifestKey'][:4])[0]
    key = keybag.unwrapKeyForClass(manifest_class, manifest_key)
    decrypted_data = AESdecryptCBC(encrypted_db, key)

    temp_dir = tempfile.mkdtemp()
    try:
        # Does anyone know how to get Python’s SQLite module to open some
        # bytes in memory as a database?
        db_filename = os.path.join(temp_dir, 'db.sqlite3')
        with open(db_filename, 'wb') as db_file:
            db_file.write(decrypted_data)
        conn = sqlite3.connect(db_filename)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # c.execute("select * from Files limit 1");
        # r = c.fetchone()
        c.execute("""
            SELECT fileID, domain, relativePath, file
            FROM Files
            WHERE relativePath LIKE 'Media/PhotoData/MISC/DCIM_APPLE.plist'
            ORDER BY domain, relativePath""")
        results = c.fetchall()
    finally:
        shutil.rmtree(temp_dir)

    for item in results:
        fileID, domain, relativePath, file_bplist = item

        plist = biplist.readPlistFromString(file_bplist)
        file_data = plist['$objects'][plist['$top']['root'].integer]
        size = file_data['Size']

        protection_class = file_data['ProtectionClass']
        encryption_key = plist['$objects'][
            file_data['EncryptionKey'].integer]['NS.data'][4:]

        backup_filename = os.path.join(args.backup_directory,
                                    fileID[:2], fileID)
        with open(backup_filename, 'rb') as infile:
            data = infile.read()
            key = keybag.unwrapKeyForClass(protection_class, encryption_key)
            # truncate to actual length, as encryption may introduce padding
            decrypted_data = AESdecryptCBC(data, key)[:size]

        print('== decrypted data:')
        print(wrap(decrypted_data))
        print()

        print('== pretty-printed plist')
        pprint.pprint(biplist.readPlistFromString(decrypted_data))

##
# this section is mostly copied from parts of iphone-dataprotection
# http://code.google.com/p/iphone-dataprotection/

CLASSKEY_TAGS = [b"CLAS",b"WRAP",b"WPKY", b"KTYP", b"PBKY"]  #UUID
KEYBAG_TYPES = ["System", "Backup", "Escrow", "OTA (icloud)"]
KEY_TYPES = ["AES", "Curve25519"]
PROTECTION_CLASSES={
    1:"NSFileProtectionComplete",
    2:"NSFileProtectionCompleteUnlessOpen",
    3:"NSFileProtectionCompleteUntilFirstUserAuthentication",
    4:"NSFileProtectionNone",
    5:"NSFileProtectionRecovery?",

    6: "kSecAttrAccessibleWhenUnlocked",
    7: "kSecAttrAccessibleAfterFirstUnlock",
    8: "kSecAttrAccessibleAlways",
    9: "kSecAttrAccessibleWhenUnlockedThisDeviceOnly",
    10: "kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly",
    11: "kSecAttrAccessibleAlwaysThisDeviceOnly"
}
WRAP_DEVICE = 1
WRAP_PASSCODE = 2

class Keybag(object):
    def __init__(self, data):
        self.type = None
        self.uuid = None
        self.wrap = None
        self.deviceKey = None
        self.attrs = {}
        self.classKeys = {}
        self.KeyBagKeys = None #DATASIGN blob
        self.parseBinaryBlob(data)
        print(self.attrs)

    def parseBinaryBlob(self, data):
        currentClassKey = None

        for tag, data in loopTLVBlocks(data):
            if len(data) == 4:
                data = struct.unpack(">L", data)[0]
            if tag == b"TYPE":
                self.type = data
                if self.type > 3:
                    print("FAIL: keybag type > 3 : %d" % self.type)
            elif tag == b"UUID" and self.uuid is None:
                self.uuid = data
            elif tag == b"WRAP" and self.wrap is None:
                self.wrap = data
            elif tag == b"UUID":
                if currentClassKey:
                    self.classKeys[currentClassKey[b"CLAS"]] = currentClassKey
                currentClassKey = {b"UUID": data}
            elif tag in CLASSKEY_TAGS:
                currentClassKey[tag] = data
            else:
                self.attrs[tag] = data
        if currentClassKey:
            self.classKeys[currentClassKey[b"CLAS"]] = currentClassKey

    def unlockWithPasscode(self, passcode):
        # passcode1 = fastpbkdf2.pbkdf2_hmac('sha256', passcode,
        #                                 self.attrs[b"DPSL"],
        #                                 self.attrs[b"DPIC"], 32)
        passcode_key = fastpbkdf2.pbkdf2_hmac('sha1', passcode1,
                                            self.attrs[b"SALT"],
                                            self.attrs[b"ITER"], 32)
        print('== Passcode key')
        print(anonymize(hexlify(passcode_key)))
        for classkey in self.classKeys.values():
            if b"WPKY" not in classkey:
                continue
            k = classkey[b"WPKY"]
            if classkey[b"WRAP"] & WRAP_PASSCODE:
                k = AESUnwrap(passcode_key, classkey[b"WPKY"])
                if not k:
                    return False
                classkey[b"KEY"] = k
        return True

    def unwrapKeyForClass(self, protection_class, persistent_key):
        ck = self.classKeys[protection_class][b"KEY"]
        if len(persistent_key) != 0x28:
            raise Exception("Invalid key length")
        return AESUnwrap(ck, persistent_key)

    def printClassKeys(self):
        print("== Keybag")
        print("Keybag type: %s keybag (%d)" % (KEYBAG_TYPES[self.type], self.type))
        print("Keybag version: %d" % self.attrs[b"VERS"])
        print("Keybag UUID: %s" % anonymize(hexlify(self.uuid)))
        print("-"*209)
        print("".join(["Class".ljust(53),
                    "WRAP".ljust(5),
                    "Type".ljust(11),
                    "Key".ljust(65),
                    "WPKY".ljust(65),
                    "Public key"]))
        print("-"*208)
        for k, ck in self.classKeys.items():
            if k == 6:print("")

            print("".join(
                [PROTECTION_CLASSES.get(k).ljust(53),
                str(ck.get(b"WRAP","")).ljust(5),
                KEY_TYPES[ck.get(b"KTYP",0)].ljust(11),
                anonymize(hexlify(ck.get(b"KEY", b""))).ljust(65),
                anonymize(hexlify(ck.get(b"WPKY", b""))).ljust(65),
            ]))
        print()

def loopTLVBlocks(blob):
    i = 0
    while i + 8 <= len(blob):
        tag = blob[i:i+4]
        length = struct.unpack(">L",blob[i+4:i+8])[0]
        data = blob[i+8:i+8+length]
        yield (tag,data)
        i += 8 + length

def unpack64bit(s):
    return struct.unpack(">Q",s)[0]
def pack64bit(s):
    return struct.pack(">Q",s)

def AESUnwrap(kek, wrapped):
    C = []
    for i in range(len(wrapped)//8):
        C.append(unpack64bit(wrapped[i*8:i*8+8]))
    n = len(C) - 1
    R = [0] * (n+1)
    A = C[0]

    for i in range(1,n+1):
        R[i] = C[i]

    for j in reversed(range(0,6)):
        for i in reversed(range(1,n+1)):
            todec = pack64bit(A ^ (n*j+i))
            todec += pack64bit(R[i])
            B = Crypto.Cipher.AES.new(kek).decrypt(todec)
            A = unpack64bit(B[:8])
            R[i] = unpack64bit(B[8:])

    if A != 0xa6a6a6a6a6a6a6a6:
        return None
    res = b"".join(map(pack64bit, R[1:]))
    return res

ZEROIV = "\x00"*16
def AESdecryptCBC(data, key, iv=ZEROIV, padding=False):
    if len(data) % 16:
        print("AESdecryptCBC: data length not /16, truncating")
        data = data[0:(len(data)/16) * 16]
    data = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv).decrypt(data)
    if padding:
        return removePadding(16, data)
    return data

##
# here are some utility functions, one making sure I don’t leak my
# secret keys when posting the output on Stack Exchange

anon_random = random.Random(0)
memo = {}
def anonymize(s):
    if type(s) == str:
        s = s.encode('utf-8')
    global anon_random, memo
    if ANONYMIZE_OUTPUT:
        if s in memo:
            return memo[s]
        possible_alphabets = [
            string.digits,
            string.digits + 'abcdef',
            string.ascii_letters,
            "".join(chr(x) for x in range(0, 256)),
        ]
        for a in possible_alphabets:
            if all((chr(c) if type(c) == int else c) in a for c in s):
                alphabet = a
                break
        ret = "".join([anon_random.choice(alphabet) for i in range(len(s))])
        memo[s] = ret
        return ret
    else:
        return s

def wrap(s, width=78):
    "Return a width-wrapped repr(s)-like string without breaking on \’s"
    s = repr(s)
    quote = s[0]
    s = s[1:-1]
    ret = []
    while len(s):
        i = s.rfind('\\', 0, width)
        if i <= width - 4: # "\x??" is four characters
            i = width
        ret.append(s[:i])
        s = s[i:]
    return '\n'.join("%s%s%s" % (quote, line ,quote) for line in ret)

def readpipe(path):
    if stat.S_ISFIFO(os.stat(path).st_mode):
        with open(path, 'rb') as pipe:
            return pipe.read()
    else:
        raise Exception("Not a pipe: {!r}".format(path))

if __name__ == '__main__':
    main()
