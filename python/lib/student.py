import datetime
import config
import hashlib

def _epoch(dt):
    delta = dt - datetime.datetime(1970,1,1)
    return delta.days*60*60*24+delta.seconds

def _digest(name,e):
    return "%s, %s, %s [%s]" % (e.what,e.where,e.who,name)

class Student:
    def __init__(self,year,src):
        self._year = year
        self._src = src
        self._details = []
        
    def add(self,details):
        self._details.append(details)

    def generate(self):
        # root url
        rooturl = config.config('base')
        if rooturl[-1] == '/':
            rooturl = rooturl[:-1]
        # date
        now = datetime.datetime.utcnow()
        now -= datetime.timedelta(microseconds = now.microsecond) # round to nearest second
        now = now.isoformat()+"Z"
        du = datetime.datetime.utcnow()
        # year
        yv = self._year.starts[0].year
        yv = "%4.4d/%2.2d" % (yv,(yv+1)%100)
        # summaries
        name = []
        summary = ""
        for d in self._details:
            summary += "<b>%s</b>: %s %s" % (d.name,d.metadata('head'),d.metadata('foot'))
            name.append(d.name)
        # pageurl and selfurl
        pageurl = rooturl
        pageurl = '#'
        selfurl = "%s/gcal.php?course=%s" % (rooturl,",".join([x.id for x in self._details]))
        # events
        events = []
        for d in self._details:
            for g in d.getGroups():
                for e in g.group:
                    for (start,end) in self._year.atoms_to_isos(e.when.patterns()):
                        id = hashlib.md5("%s:%s:%s" % (e.eid(3),start,end)).hexdigest()
                        text = _digest(d.name,e)
                        events.append(self._src.create_entry(id,now,text,pageurl,selfurl,e.where,start,end,_epoch(du),text))
        #
        return self._src.emit(pageurl,now," ".join(name),pageurl,summary,events)
        
def student(d,y,gc):
    s = Student(y,gc)
    s.add(d)
    return s.generate()
