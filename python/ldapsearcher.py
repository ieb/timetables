import sys
import os,os.path
import getopt
import ldap
import simplejson as json

def usage():
    print """
Usage:
    
python ldapsearcher.py -m <term> [-h <head>] [-t <tail>]   -- find matches to term prfix with string head, suffix with tail

"""
    sys.exit(1)



base = "ou=people, o=University of Cambridge,dc=cam,dc=ac,dc=uk"
def get_connection():
    global base
    # XXX cache dap keep around for one minute
    return ldap.initialize('ldap://ldap.lookup.cam.ac.uk/')

# for some reason or queries are very slow. Doing them separately gives us more control anyway.

def autocompleteCN(dap,q,head,tail):
    out = []
    if len(q)<4:
        return []
    for (_k,v) in dap.search_s(base,ldap.SCOPE_SUBTREE,'(cn=*'+q.lower()+'*)',['uid','cn']):
        v = "%s %s [%s] %s" % (head,v['cn'][0],v['uid'][0],tail)
        outbits = {
        "id" : v,
        "value": v,
        "label": v
        }
        out.append(outbits)
    return out

def autocompleteUID(dap,q,head,tail):
    out = []
    if len(q)<2:
        return []
    for (_k,v) in dap.search_s(base,ldap.SCOPE_SUBTREE,'(uid='+q.lower()+'*)',['uid','cn']):
        v = "%s %s [%s] %s" % (head,v['cn'][0],v['uid'][0],tail)        
        outbits = {
        "id" : v,
        "value": v,
        "label": v
        }
        out.append(outbits)
    return out

def autocomplete(q,head,tail):
    out = []
    if len(q)<2:
        return []
    dap = get_connection()
    out.extend(autocompleteCN(dap,q,head,tail))
    out.extend(autocompleteUID(dap,q,head,tail))
    return out



(optlist,args) = getopt.getopt(sys.argv[1:],"m:gh:t:")

head = ''
tail = ''
for (opt,val) in optlist:
    if opt == '-m':
        mode = '-m'
        term = val
    elif opt == '-h':
        head = val
    elif opt == '-t':
        tail = val

script = sys.argv[0]

if term == None:
    usage()


if mode == '-m':
   print json.dumps(autocomplete(term,head,tail))
else:
    usage()
sys.exit(0)