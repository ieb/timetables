import hashlib,random,itertools
from datetime import tzinfo, timedelta, datetime

def _nrt_str(seq,i):
    if seq != None:
        return str(seq[i])
    else:
        return str(i)

def number_range_text(data,seq = None):
    out = ""
    vals = [int(i) for i in sorted(list(data))]
    vals.append(None)
    range_start = -1
    range_last = -1
    for i in vals:
        if range_start == -1 or i == None or range_last != i-1:
            if range_start != -1 and range_last != range_start:
                out += "-" + _nrt_str(seq,range_last)
            if i != None:
                out += ","+_nrt_str(seq,i)
                range_start = i
                range_last = i
        else:
            range_last = i                
    if len(out):
        out = out[1:]
    return out

def hide_commas(data):
    ranges = data.split(",")
    out = ""
    was_range = False
    first = True
    for r in ranges:
        is_range = ('-' in r)
        if (is_range or was_range) and not first:
            out += ","
        out += r
        was_range = is_range
        first = False
    return out

def all_or_else(what,fn,fallback):
    v = None
    for w in what:
        if v == None:
            v = fn(w)
        elif v != fn(w):
            return fallback
    return v

base = 1

def rndid(seed,prefix):
    global base
    return prefix + hashlib.md5("%s%s%d%d" % (prefix,seed,random.randrange(1000000000),base)).hexdigest()
    base += 1

def hashid(prefix,*data):
    data = [unicode(x) for x in data]
    return prefix + hashlib.md5("%s%s" % (prefix,str(data))).hexdigest()

def min_non_empty_value_key(data):
    min = None
    mink = None
    for (k,v) in data.iteritems():
        if len(v) > 0 and (min == None or min > len(v)):
            min = len(v)
            mink = k
    return mink

def ranges(data):
    rstart = None
    rlast = None
    data = sorted(list(data))
    i = 0
    out = []
    while i < len(data):
        # What's the longest range from here?
        for j in range(i,len(data)+1):
            if j == len(data) or data[j] != data[i]+(j-i):
                break
        out.append((data[i],j-i))
        i = j        
    return out

def powerset(data):
    s = list(data)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def successor(data,threshold):
    c = filter(lambda x: x > threshold,data)
    if not len(c): return None
    return min(c)

def plural(singular):
    if len(singular) and singular[-1] == 's':
        return singular
    return "%ss" % singular # XXX do it better

ZERO = timedelta(0)
HOUR = timedelta(hours=1)

# A UTC class.

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = UTC()

