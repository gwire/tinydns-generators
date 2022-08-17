#!/usr/bin/env python3

# tinysvcb - generate a RR type 64 SVCB or 65 HTTPS records in tinydns wire format
#
# example: ./tinysvcb.py --https --domain example.com --priority 0 --target host.example.com
#
# Based on https://datatracker.ietf.org/doc/draft-ietf-dnsop-svcb-https/10/
#
# 2022 Lee Maguire

import sys
import getopt
import ipaddress
import base64

rrtype = "65"
domain = "example.com"
priority = "0"
target = "host.example.com"
parameters = ""
ttl = "86400"

def tinySVCBRecord( rrtype, domain, priority, target, parameters, ttl ):
    output = ":"
    output += tinyBytes( bytes(domain, "ascii") )
    output += ":" + rrtype + ":"
    output += tinyBytes( nboInt(2, priority) )
    output += tinyBytes( lengthPrefixedLabels(target) )
    if int(priority) > 0 and len(parameters) > 0:
        output += tinyBytes( encodeParameters( parameters ) )
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

def charString( text ):
    ## Appendix A in the spec
    output = text  ## TODO: actually implement
    return( output )

def getParamId( key ):
    if key in "mandatory":
        return( 0 )
    elif key in "alpn":
        return( 1 )
    elif key in "no-default-alpn":
        return( 2 )
    elif key in "port":
        return( 3 )
    elif key in "ipv4hint":
        return( 4 )
    elif key in "ech":
        return( 5 )
    elif key in "ipv6hint":
        return( 6 )
    elif key.startswith('key'):
        return( int(key[3:]) )

def encodeParameters( parameters ):
    outbytes = bytearray(b'')
    paramdict = {}

    ## put parameter ids and raw values into a dictonary
    for param in parameters.split(" "):
        if param in "no-default-alpn":
            svcint = getParamId( param )
            paramdict[svcint] = "empty" ## value is ignored
        else:
            key,value = param.split("=")
            value = value.strip('\"')
            value = value.strip('\'')
            svcint = getParamId( key )
            paramdict[svcint] = value

    ## go through the dictionary in id order
    for svcid in sorted(paramdict):
        outbytes += nboInt(2, svcid)

        if svcid == 0: # mandatory
            mandatory_ids = []
            mandatory = paramdict[svcid].split(",")
            for mandsvc in mandatory:
                mandatory_ids.append( getParamId(mandsvc) )
            outbytes += nboInt(2, len(mandatory_ids) * 2) # length is fixed 2 bytes per item
            ## go through array in id order
            for i in sorted(mandatory_ids):
                outbytes += nboInt(2, i)

        elif svcid == 1: # alpn
            alpn_outbytes = bytearray(b'')
            alpn_length = 0 
            alpns = paramdict[svcid].split(",")
            for alpn in alpns:
                alpn_length += 1
                alpn_bytes = bytes(alpn, "ascii") ## TODO: account for pre-escaped text
                alpn_length += len(alpn_bytes)
                alpn_outbytes += nboInt(1, len(alpn_bytes))
                alpn_outbytes += alpn_bytes
            outbytes += nboInt(2, alpn_length)
            outbytes += alpn_outbytes

        elif svcid == 3: # port
            outbytes += nboInt(2, 2)
            outbytes += nboInt(2, paramdict[svcid] ) # port value is just an int

        elif svcid == 4: # ipv4hint
            addresses = paramdict[svcid].split(",")
            outbytes += nboInt(2, len(addresses) * 4) # length is fixed 4 bytes per item
            for ipv4addr in addresses:
                outbytes += ipaddress.IPv4Address(ipv4addr).packed

        elif svcid == 5: # ech
            ech = base64.b64decode(paramdict[svcid])
            outbytes += nboInt(2, len(ech))
            outbytes += ech

        elif svcid == 6: # ipv6hint
            addresses = paramdict[svcid].split(",")
            outbytes += nboInt(2, len(addresses) * 16) # length is fixed 16 bytes per item
            for ipv6addr in addresses:
                outbytes += ipaddress.IPv6Address(ipv6addr).packed

        elif svcid > 6:
                key_val = charString(paramdict[svcid])
                outbytes += nboInt(2, len(key_val))
                outbytes += bytes(key_val, "ascii")

    return( outbytes )

opts, args = getopt.getopt(sys.argv[1:],"hd:p:t:a:l:",["help","https","svcb","priority=","target=","domain=","ttl=","parameters="])
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print('Usage: tinysvcb.py --https --domain example.com --priority 0 --target host.example.com')
        print('  --svcb  (Use RR 64)')
        print('  --https (Use RR 65)')
        print('  --priority int (0 for alias)')
        print('  --domain hostname (domain hostname)')
        print('  --target hostname (service hostname)')
        print('  --parameters "key=value key=value" (parameter list)')
        print('  --ttl int (dns ttl)')
        sys.exit()
    elif opt in ("--svcb"):
        rrtype = "64"
    elif opt in ("--https"):
        rrtype = "65"
    elif opt in ("-d", "--domain"):
        domain = arg
    elif opt in ("-p", "--priority"):
        priority = arg
    elif opt in ("-t", "--target"):
        target = arg
    elif opt in ("-a", "--parameters"):
        parameters = arg
    elif opt in ("-l", "--ttl"):
        ttl = arg

line = tinySVCBRecord( rrtype, domain, priority, target, parameters, ttl)
sys.stdout.write( line + "\n")

sys.exit(0)
