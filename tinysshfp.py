#!/usr/bin/env python3

# tinysshfp - takes the output of "ssh-keygen -r" and converts into tinydns
#
# example: ssh-keygen -r example.com | ./tinysshfp.py 
#
# https://www.rfc-editor.org/rfc/rfc4255
# 2017,2022 Lee Maguire

import getopt
import sys
import re

ttl = "86400"

def tinyBytes( bytearr, escape_all=False ):
    ## output printable ascii but not space, "/", ":", "\"
    ## all other characters output as octal \nnn codes
    output = ""
    for b in bytearr:
        if not escape_all and int(b) > 32 and int(b) < 127 and int(b) not in [47,58,92]:
            output += chr(b)
        else:
            output += "\\{0:03o}".format(b)
    return( output )

def nboInt( length, number ):
    ## returns bytes representing an integer in network byte order (big endian)
    ## if input "2, 256", output should be equivalent to "\001\000"
    intbytes = int(number).to_bytes(length, "big")
    return( intbytes )

def tinySshfpRecord( hostname, algid, fptype, fp, ttl ):
    output = ""
    output += ":"
    output += tinyBytes(bytes(hostname, "ascii"))
    output += ":44:"
    output += tinyBytes( nboInt(1,algid) )
    output += tinyBytes( nboInt(1,fptype) )
    output += tinyBytes( bytes.fromhex(fp), True )
    output += ":" + ttl
    return( output );

opts, args = getopt.getopt(sys.argv[1:],"ht:",["ttl="])
for opt, arg in opts:
    if opt == '-h':
        print('Usage: tinysshfp.py -t 60')
        sys.exit()
    elif opt in ("-t", "--ttl"):
        ttl = arg

for input_text in sys.stdin:
    hostname,xin,xsshfp,algid,fptype,fp = input_text.rstrip().split(" ")
    line = tinySshfpRecord( hostname, algid, fptype, fp, ttl )
    sys.stdout.write( line + "\n")

sys.exit(0)
