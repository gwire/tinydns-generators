#!/usr/bin/env python3
#
# tinyipv6 - generate an IPv6 type 28 AAAA record in the tinydns format
#
# example: ./tinyipv6.py -l 60 -d host.example.com -i 2001:db8:85a3:8d3:1319:8a2e:370:7348
# :host.example.com:28:\040\001\015\270\205\243\010\323\023\031\212.\003psH:86400
#
# -3 and -6 options will generate "3:" and "6:" type records, if your server supports them 
#
# 2022 Lee Maguire

import ipaddress
import sys
import getopt

ttl = "86400"
domain= "host.example.com"
ip = "2001:db8:85a3:8d3:1319:8a2e:370:7348"
opt_r = 0
opt_3 = 0
opt_6 = 0

def tinyBytes( bytearr, encode_all=False ):
    ## output printable ascii but not space, "/", ":", "\"
    ## all other characters output as octal \nnn codes
    output = ""
    for b in bytearr:
        if not encode_all and int(b) > 32 and int(b) < 127 and int(b) not in [47,58,92]:
            output += chr(b)
        else:
            output += "\\{0:03o}".format(b)
    return( output )

def tinyAAAARecord( rtype, fqdn, ipv6addr, ttl ):
    output = ""
    if rtype in "3":
        output += "3"
    elif rtype in "6":
        output += "6"
    else:
        output += ":"
    output += tinyBytes( bytes(fqdn, "ascii") ) 
    if rtype in ("3","6"):
        ip6_out = str(ipaddress.IPv6Address(ipv6addr).exploded).replace(":","")
        output += ":" + tinyBytes( bytes(ip6_out, "ascii") )
    else:
        output += ":28:" + tinyBytes( ipaddress.IPv6Address(ipv6addr).packed, True ) 
    output +=  ":" + ttl
    return( output )

opts, args = getopt.getopt(sys.argv[1:],"hd:i:l:36r",["domain=","ip=","ttl=","raw"])
for opt, arg in opts:
  if opt == '-h':
    print('Usage: tinyipv6.py -d host.example.com -i 2001:db8:85a3:8d3:1319:8a2e:370:7348 -l 60 [-r][-3][-6]')
    sys.exit()
  elif opt in ("-d", "--domain"):
    domain = arg
  elif opt in ("-i", "--ip"):
    ip = arg
  elif opt in ("-l", "--ttl"):
    ttl = arg
  elif opt in ("-r", "--raw"):
    opt_r = 1
  elif opt in ("-3"):
    opt_3 = 1
  elif opt in ("-6"):
    opt_6 = 1

## default to the raw format if not specified
if not opt_3 and not opt_6:
    opt_r = 1

if opt_r:
  line = tinyAAAARecord( "r", domain, ip, ttl)
  sys.stdout.write( line + "\n")
if opt_3:
  line = tinyAAAARecord( "3", domain, ip, ttl)
  sys.stdout.write( line + "\n")
if opt_6:
  line = tinyAAAARecord( "6", domain, ip, ttl)
  sys.stdout.write( line + "\n")

sys.exit(0)
