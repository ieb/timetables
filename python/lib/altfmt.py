# alternative format foo=bar|baz=baaz, etc

# XXX escape
def write(data):
    out = []
    for (k,v) in data:
        out.append("%s=%s" % (k,v))
    return ("|".join(out)).encode('utf-8')

def read(fmt,row,exc = True):
    row = row.strip()
    out = []
    for (i,part) in enumerate(row.split("|")):
        (k,v) = part.split('=')
        if fmt[i] != k:
            if exc:
                raise Exception("Bad line '%s', key '%s' unknown or in wrong order" % (row,k))
            else:
                return None
        out.append(v)
    return out
