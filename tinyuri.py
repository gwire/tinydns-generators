#!/usr/bin/env python3

# tinyuri - generate a RR type 256 URI record in tinydns format
#
# example: ./tinyuri.py --domain example.com --service ldap --proto tcp --priority 10 --weight 20 --target "ldap://dir.example.com:389"
#
# https://www.rfc-editor.org/rfc/rfc7553
#
# 2022 Lee Maguire

import sys
import getopt

domain = "example.com"
service = "ldap"
proto = "tcp"
priority = 10
weight = 20
target = "ldap://dir.example.com:389"
ttl = "86400"

## https://www.iana.org/assignments/enum-services/enum-services.xhtml
enumtype = ""
enumsubtype = ""
enumscheme = ""

def tinyUriRecord( domain, prefix, priority, weight, target, ttl ):
    output = ":"
    srvdomain = prefix + "." + domain
    output += tinyBytes( bytes(srvdomain, "ascii") )
    output += ":256:"
    output += tinyBytes( nboInt(2, priority), True )
    output += tinyBytes( nboInt(2, weight), True )
    output += tinyBytes( bytes(target, "ascii") )
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

opts, args = getopt.getopt(sys.argv[1:],"hd:s:p:t:l:",["help","domain=","service=","proto=","priority=","weight=","target=","enumtype=","enumsubtype=","enumscheme=","ttl="])
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print('Usage: tinyuri.py --domain example.com --service ldap --proto tcp --priority 10 --weight 20 --target "ldap://dir.example.com:389"')
        print('  --domain domain-name')
        print('  --service service-name (eg "ldap")')
        print('  --proto protocol ("tcp" or "udp")')
        print('  --priority int (eg 1)')
        print('  --weight int (eg 10)')
        print('  --target "uri" (eg "ldap://dir.example.com:389")')
        print('  --ttl int (dns ttl)')
        sys.exit()
    elif opt in ("-d", "--domain"):
        domain = arg
    elif opt in ("--service"):
        service = arg
    elif opt in ("--proto"):
        proto = arg
    elif opt in ("-p", "--priority"):
        priority = arg
    elif opt in ("--weight"):
        weight = arg
    elif opt in ("-t", "--target"):
        target = arg
    elif opt in ("-l", "--ttl"):
        ttl = arg
    elif opt in ("--enumscheme"):
        enumscheme = arg
        proto = ""
    elif opt in ("--enumsubtype"):
        enumsubtype = arg
        proto = ""
    elif opt in ("--enumtype"):
        enumtype = arg
        proto = ""

if proto:
    prefix = "_" + service + "._" + proto
elif enumsubtype:
    prefix = "_" + enumscheme + "._" + enumsubtype + "._" + enumtype
else:
    prefix = "_" + enumscheme + "._" + enumtype

line = tinyUriRecord( domain, prefix, priority, weight, target, ttl )
sys.stdout.write( line + "\n")

sys.exit(0)
