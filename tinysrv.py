#!/usr/bin/env python3

# tinysrv - generate a RR type 33 SRV record in tinydns format
#
# example: ./tinysrv.py --domain example.com --service ldap --proto tcp --priority 10 --weight 20 --port 389 --target dir.example.com
#
# https://www.rfc-editor.org/rfc/rfc2782
#
# 2022 Lee Maguire

import sys
import getopt

domain = "example.com"
service = "ldap"
proto = "tcp"
priority = 10
weight = 20
port = 389
target = "dir.example.com"
ttl = "86400"

def tinySrvRecord( domain, service, proto, priority, weight, port, target, ttl ):
    output = ":"
    srvdomain = "_" + service + "._" + proto + "." + domain
    output += tinyBytes( bytes(srvdomain, "ascii") )
    output += ":33:"
    output += tinyBytes( nboInt(2, priority), True )
    output += tinyBytes( nboInt(2, weight), True )
    output += tinyBytes( nboInt(2, port), True )
    ## it's not clear from the RFC that the target should be length prefixed labels
    output += tinyBytes( lengthPrefixedLabels(target) )
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

def lengthPrefixedLabels( domain ):
    ## if input "example.com", output should be "\007example\003com\000"
    ## if input ".", output should be "\000"
    ## TODO: account for pre-escaped text
    outbytes = bytearray(b'')
    if len(domain) > 1:
        for label in domain.split("."):
            outbytes += nboInt(1, len(label))
            outbytes += bytes(label, "ascii")
    outbytes += nboInt(1, 0)
    return( outbytes )

opts, args = getopt.getopt(sys.argv[1:],"hd:s:p:t:l:",["help","domain=","service=","proto=","priority=","weight=","port=","target=","ttl="])
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print('Usage: tinysrv.py --domain example.com --service ldap --proto tcp --priority 10 --weight 20 --port 389 --target dir.example.com')
        print('  --domain domain-name')
        print('  --service service-name (eg "ldap")')
        print('  --proto protocol ("tcp" or "udp")')
        print('  --priority int (eg 1)')
        print('  --weight int (eg 10)')
        print('  --port int (eg 389)')
        print('  --target hostname (service hostname)')
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
    elif opt in ("--port"):
        port = arg
    elif opt in ("-t", "--target"):
        target = arg
    elif opt in ("-l", "--ttl"):
        ttl = arg

line = tinySrvRecord( domain, service, proto, priority, weight, port, target, ttl )
sys.stdout.write( line + "\n")

sys.exit(0)
