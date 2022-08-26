#!/usr/bin/env python3

# tinyloc - generate a RR type 29 LOC record in tinydns format
#
# example: ./tinyuri.py --domain example.com --d1 51 --m1 30 --s1 3.637 --l1 N --d2 0 --m2 8 --s2 29.624 --l2 W
#   :example.com:29:\000\000\000\000\213\015\010\365\177\370\071\110\000\230\226\200:86400
#
# https://www.rfc-editor.org/rfc/rfc1876
#
# 2022 Lee Maguire

import sys
import getopt
from math import log10, floor

domain = "example.com"
d1 = "0"
m1 = "0"
s1 = "0.0"
l1 = "N"
d2 = "0"
m2 = "0"
s2 = "0.0"
l2 = "W"
alt = "0.00"
siz = "0.00"
hp = "0.00"
vp = "0.00"
ttl = "86400"

def tinyLocRecord( domain, d1, m1, s1, l1, d2, m2, s2, l2, alt, siz, hp, vp, ttl ):
    output = ":"
    output += tinyBytes( bytes(domain, "ascii") )
    output += ":29:"
    output += tinyBytes( nboInt(1,0) ) # version = 0
    output += tinyBytes( locSize( siz ), True )
    output += tinyBytes( locSize( hp ), True )
    output += tinyBytes( locSize( vp ), True )
    output += tinyBytes( dmsBytes( d1, m1, s1, l1 ), True )
    output += tinyBytes( dmsBytes( d2, m2, s2, l2 ), True )
    output += tinyBytes( locAlt( alt ), True )
    output += ":" + ttl
    return( output )

def tinyBytes( bytearr, encode_all=False ):
    ## output printable ascii (but not space, "/", ":", "\")
    ## all other characters output as octal \nnn codes
    output = ""
    for b in bytearr:
        if not encode_all and b > 32 and b < 127 and b not in [47,58,92]:
            output += chr(b)
        else:
            output += "\\{0:03o}".format(b)
    return( output )

def nboInt( length, number ):
    ## returns bytes representing an integer in network byte order (big endian)
    ## if input "2, 256", output should be equivalent to "\001\000"
    intbytes = int(number).to_bytes(length, "big")
    return( intbytes )

## https://stackoverflow.com/a/3411435
def round_to_1(x):
    if int(x) == 0:
        return(x)
    else:
        return(round(x, -int(floor(log10(abs(x))))))

def locSize( metres ):
    metres = metres.replace("m", "")
    # How does RFC1876 represent a size from 1cm to 90000km in a single byte?
    # Fistly, it records a value in cm, but only to the most significant number (0-9)
    # Then it jams the significand and ^10 exponent into 4-bits each such that the
    # hex representation is the two numbers  
    #  eg input of "2.9m" should return output of "\x32" (300cm)
    #  eg input of "0.01m" should return output of "\x10" (1cm)
    #  eg input of "90000000m" should return output of "\x99" (90000km)
    #    
    # This efficent scheme has surely saved *megabytes* of bandwidth by now.
    #
    round_cm = str(int(round_to_1(float( metres ) * 100)))
    sig_exp = int(round_cm[0]) << 4 # shift the 4-bit significand to the front of the byte
    sig_exp += (len(round_cm) - 1) # add the 4-bit exponent to the back
    #print(hex(sig_exp))
    return( sig_exp.to_bytes(1, "big") )
    # Thanks, I hate it.

def locAlt( alt ):
    alt = alt.replace("m", "")
    ### a baseline of 10,0000m represents sea-level (ie 0m) in RFC 1876
    di = (int(float(alt)) + 100000) * 100
    return(di.to_bytes(4, "big"))

def dmsBytes( d, m, s, l ):
    ## convert degrees, minutes, seconds notation
    ## 32-bit integer representing thousands of a second
    midpoint = 2 ** 31 ## defined in RFC 1876
    pos = 0.0
    x = 0.0
    x =  int(d) * 3600000
    x += int(m) * 60000
    x += float(s) * 1000
    if l in "N":
        pos = midpoint + x
    elif l in "S":
        pos = midpoint - x
    elif l in "E":
        pos = midpoint + x
    elif l in "W":
        pos = midpoint - x
    dms = int(pos).to_bytes(4, "big")
    return( dms )

opts, args = getopt.getopt(sys.argv[1:],"hd:l:",["help","domain=","d1=","m1=","s1=","l1=","d2=","m2=","s2=","l2=","alt=","siz=","hp=","vp=","ttl="])
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print('Usage: tinyloc.py --domain example.com --d1 51 --m1 30 --s1 3.637 --l1 N --d2 0 --m2 8 --s2 29.624 --l2 W')
        print('  --domain domain-name')
        print('  --d1 0-90 (degrees lat)')
        print('  --m1 0-59 (minutes lat)')
        print('  --s1 0-59.999 (seconds lat)')
        print('  --l1 direction ("N"/"S)')
        print('  --d2 0-90 (degrees lon)')
        print('  --m2 0-59 (minutes lon)')
        print('  --s2 0-59.999 (seconds lon)')
        print('  --l2 direction ("E"/"W")')
        print('  --alt -100000.00 - 42849672.95m (altitude in m)')
        print('  --siz 0 .. 90000000.00m (size)')
        print('  --hp 0 .. 90000000.00m (horizonal precision)')
        print('  --vp 0 .. 90000000.00m (vertical precision)')
        print('  --ttl int (dns ttl)')
        sys.exit()
    elif opt in ("-d", "--domain"):
        domain = arg
    elif opt in ("--d1"):
        d1 = arg
    elif opt in ("--m1"):
        m1 = arg
    elif opt in ("--s1"):
        s1 = arg
    elif opt in ("--l1"):
        l1 = arg
    elif opt in ("--d2"):
        d2 = arg
    elif opt in ("--m2"):
        m2 = arg
    elif opt in ("--s2"):
        s2 = arg
    elif opt in ("--l2"):
        l2 = arg
    elif opt in ("--alt"):
        alt = arg
    elif opt in ("--siz"):
        siz = arg
    elif opt in ("--hp"):
        hp = arg
    elif opt in ("--vp"):
        vp = arg
    elif opt in ("-l", "--ttl"):
        ttl = arg

line = tinyLocRecord( domain, d1, m1, s1, l1, d2, m2, s2, l2, alt, siz, hp, vp, ttl )
sys.stdout.write( line + "\n")

sys.exit(0)
