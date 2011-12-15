import config
import time
import random

def record(r):
    # ADD OUR OWN DATA
    r['report-time'] = str(int(time.time()))

    # SANITIZE
    out = {}
    for (k,v) in r.iteritems():
        v = v.replace('\t','    ').replace('\n','\t').replace('\r','\t')
        out[k] = v    
    data = ""
    for (k,v) in out.iteritems():
        data += "%s = %s \n" % (k,v)

    # CALCULATE FILENAME
    base = config.config('error-base')
    if not base:
        base = '../../error'
    
    filename = "%s/error_%u_%u.txt" % (base,time.time(),random.getrandbits(32))
    
    # WRITE IT
    f = open(filename,"wb")
    print >>f,data.encode('utf-8')
    f.close()
