#!/usr/bin/env python3

# tinydkim - takes an RSA public key on stdin and outputs a tinydns / djbdns DKIM record
#
# example: openssl rsa -in test.pem -pubout | ./tinydkim.py -s test -d foo.com 
#
# TODO: add support for notes field?
#
# https://www.rfc-editor.org/rfc/rfc6376.html
#
# 2016,2022 Lee Maguire

import getopt
import sys
import re

bind = ''
opt_h = ''
opt_t = ''
ttl = "86400"
selector = "selector"
domain = "example.com"

def extractPubKey( key ):
    output = ""
    key = key.replace('-----BEGIN PUBLIC KEY-----','')
    key = key.replace('-----END PUBLIC KEY-----','')
    key = key.replace('-----BEGIN RSA PUBLIC KEY-----','')
    key = key.replace('-----END RSA PUBLIC KEY-----','')
    for c in key:
        if not c in ["\r","\n","\t"," "]:
            output = output + c
    return( output );

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

def tinyDkimRecord( domain, record, ttl ):
    output = ":"
    output += tinyBytes( bytes(domain, "ascii") )
    output += ":16:"
    output += tinyBytes ( nboInt(1, len(record)) )
    output += tinyBytes( bytes(record, "ascii"))
    output += ":" + ttl
    return( output )

def dnsQuotedText( text ):
    output = ""
    for c in text:
        if c in [";"]:
            output = output + "\\;"
        else:
            output = output + c
    output = "\"" + output + "\""
    return( output );

def dnsTxtRecord( domain, record, ttl ):
    output = domain + ". " + ttl + " IN TXT " +  dnsQuotedText( record );
    return( output )

opts, args = getopt.getopt(sys.argv[1:],"hs:d:t:l:b",["selector=","domain=","hash=","testing=","ttl=","bind"])
for opt, arg in opts:
    if opt == '-h':
        print('Usage: tinydkim.py -s selector -d example.com -t y < pubkey.pem')
        sys.exit()
    elif opt in ("-s", "--selector"):
        selector = arg
    elif opt in ("-d", "--domain"):
        domain = arg
    elif opt in ("-h", "--hash"):
        opt_h = arg
    elif opt in ("-t", "--testing"):
        opt_t = arg
    elif opt in ("-l", "--ttl"):
        ttl = arg
    elif opt in ("-b", "--bind"):
        bind = 1

input_text = "".join(sys.stdin)

rdata = "v=DKIM1"
if opt_h:
    rdata = rdata + "; h=" + opt_h 
rdata = rdata + "; p=" + extractPubKey( input_text )
if opt_t:
    rdata = rdata + "; t=" + opt_t

fqdn = selector + "._domainkey." +  domain

line = tinyDkimRecord( fqdn, rdata, ttl )
sys.stdout.write( line + "\n")

## optionally output the format used by lookup tools for comparison
if bind:
    line = dnsTxtRecord( fqdn, rdata, ttl )
    sys.stdout.write( "\n# " + line + "\n" )

sys.exit(0)
