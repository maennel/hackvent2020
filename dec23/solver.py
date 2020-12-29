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