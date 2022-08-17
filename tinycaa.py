#!/usr/bin/env python3

# tinycaa - generate a CAA RR type 257
#
# example: ./tinycaa.py --domain example.com --flag 1 --tag issue --ca ca.example.net
#
# https://www.rfc-editor.org/rfc/rfc8659
#
# 2022 Lee Maguire

import sys
import getopt

domain = "example.com"
flags = "0"
tags = "issue"
value = "ca.example.net"
ttl = "86400"

def tinyCAARecord( domain, flags, tags, value, ttl ):
    ## output a single line containing a tinydns formatted record
    output = ":" 
    output += tinyBytes( bytes(domain, "ascii") )
    output += ":257:"
    output += tinyBytes( nboInt(1, flags) )
    output += tinyBytes( nboInt(1, len(tags)) )
    output += tinyBytes( bytes(tags, "ascii") )
    output += tinyBytes( bytes(value, "ascii") )
    output += ":" + ttl
    return( output )

def tinyBytes( bytearr, encode_all=False ):
    ## output printable ascii but not space, "/", ":", "\"
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

opts, args = getopt.getopt(sys.argv[1:],"hd:f:t:v:l:",["help","domain=","flags=","tags=","value=","ttl="])
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print('Usage: tinycaa.py --domain example.com --flags 1 --tags issue --value ca.example.net')
        print('  --domain hostname (domain hostname)')
        print('  --flags int (0=non-critical 1=critical)')
        print('  --tags string ("issue","issuewild","iodef")')
        print('  --value strint (CA identifier)')
        print('  --ttl int (dns ttl)')
        sys.exit()
    elif opt in ("-d", "--domain"):
        domain = arg
    elif opt in ("-f", "--flags"):
        flags = arg
    elif opt in ("-t", "--tags"):
        tags = arg
    elif opt in ("-v", "--value"):
        value = arg
    elif opt in ("-l", "--ttl"):
        ttl = arg

line = tinyCAARecord( domain, flags, tags, value, ttl )
sys.stdout.write( line + "\n")

sys.exit(0)
