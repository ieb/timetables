import collections
import hashlib

def _hash_dataobject(data):
    out = '\001'
    keys = sorted(data.keys())
    for key in keys:
        out += '\002'
        out += _hash_string(key)
        out += '\003'
        out += _hash_any(data[key])
    out += '\004'
    return out

def _hash_dataarray(data):
    out = '\005'
    for entry in data:
        out += '\006'
        out += _hash_any(entry)
    out += '\007'
    return out

def _hash_string(data):
    if isinstance(data,unicode):
        data = data.encode('utf-8')
    if not isinstance(data,str):
        data = str(data)
    out = '\010'
    out += str(len(data))
    out += '\011'
    out += data
    out += '\012'
    return out

def _hash_any(data):
    if isinstance(data,dict) or isinstance(data,collections.defaultdict):
        return _hash_dataobject(data)
    elif isinstance(data,list) or isinstance(data,set):
        return _hash_dataarray(data)
    else:
        return _hash_string(data)
    
def datahash(data):
    return hashlib.md5(_hash_any(data)).hexdigest()
