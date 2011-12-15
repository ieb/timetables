path = "../../config/config.txt"

cfg = None

def load():
    global cfg
    f = open(path,"r")
    cfg = {}
    for line in f:
        r = line.split('=',2)
        if len(r) == 2:
            cfg[r[0].strip()] = r[1].strip()
    f.close()

def config(key):
    if cfg is None:
        load()
    if key in cfg:
        return cfg[key]
    else:
        return None
