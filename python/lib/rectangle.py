import hashlib,random,json,copy,collections
import sys

import util
from fullpattern import FullPattern
import group
import patternatom
import element
import daytime
import course
import datahash

class Rectangle(object):
    default_metadata = ['notes','course-description','special-instructions']
    
    def __init__(self,dt,course,type,key,order,merged,rcodehash = None):
        self.dt = dt
        self.type = type
        self._termweeks = [[],[],[]]
        self._course = course
        self.meta = element.Element(type = type,course = course.cname)
        self.key = key
        self._patterns = FullPattern()
        self.order = order
        self._merged = merged
        self.text = None
        self.saved_dt = None
        self.rcodehash = rcodehash
    
    def addEvent(self,termweeks,elements,pattern):
        for (term,week) in termweeks.each():
            self._termweeks[term].append(week)
        self.meta.additional(elements)
        self._patterns.addOne(pattern)

    def __repr__(self):
        return "<dt=%s type=%s course=%s termweeks=%s>" % (self.dt.data(),self.type,self._course.cid,self._termweeks)

    def to_json(self):
        when = FullPattern(self.meta.when) if self.meta.specified('when') else ''
        rcode = "%s%d%2.2d%2.2d%2.2d%2.2d" % \
            ('Y' if self._merged else 'X',self.dt.day,self.dt.start[0],self.dt.start[1],self.dt.end[0],self.dt.end[1])
        out = {
            "day": self.dt.day,
            "starttime": self.dt.start,
            "endtime": self.dt.end,
            "cid": self._course.cid,
            "rid": rcode,
            "text": self.text if self.text is not None else self.meta.what,
            "cname": self._course.cname,
            "what": self.meta.what,
            "organiser": self.meta.who,
            "where": self.meta.where,
            "type": self.type,
            "termweeks": self._termweeks,
            "code": self.key,
            "when": str(when)
        }
        rcodehash = datahash.datahash(out)
        out['rid'] = "%s:%s:%s" % (rcodehash,out['rid'],util.rndid(rcode,"R"))
        return out

    def changedp(self):
        if self.rcodehash is None:
            return False
        cmp = copy.deepcopy(self.to_json())
        cmp['rid'] = cmp['rid'].split(":")[1]
        calced = datahash.datahash(cmp)
        return self.rcodehash != calced

    def update_to_element(self,el,orig):
        el.update_with(self.meta,orig)

    def add_rectangles_from_all(self,rs):
        for t in range(0,3):
            v = set(self._termweeks[t])
            for r in rs:
                v |= set(r._termweeks[t])
            self._termweeks[t] = sorted(list(v))

    @staticmethod        
    def from_json(data,order):
        dt = daytime.DayTimeRange(data['day'],data['starttime'],data['endtime'])
        c = course.Course(data['cid'],data['cname'])
        (rcodehash,rid,_) = data['rid'].split(':')
        merge = rid[0] == 'Y' if 'rid' in data else False # Is this correct?
        out = Rectangle(dt,c,data['type'],data['code'],order,merge,rcodehash)
        out._termweeks = data['termweeks']
        el = element.Element(what = data['what'], where = data['where'], who = data['organiser'], when = FullPattern(data['when']), 
                            type = data['type'],course = data['cname'],merge = merge)
        out.meta.additional(el)        
        out._patterns = FullPattern(data['when'])
        # Extract saved daytime
        out.saved_dt = daytime.DayTimeRange(int(rid[1]),int(rid[2:4]),int(rid[4:6]),int(rid[6:8]),int(rid[8:10]))
        return out

    def generate_new_details(self):
        metadata = {}
        for key in Rectangle.default_metadata:
            metadata[key] = ""
        return details.Details(self.course.cid,self.meta.what,self.meta.who,self.meta.where,metadata)

    def generate_direct_pattern(self,term):
        p = patternatom.PatternAtom(False)
        for w in self._termweeks[term]:
            p.addTermWeek(term,w)
        p.addDayTimeRangeDirect(self.dt)
        return p

class RectangleCluster(object):
    def __init__(self,key):
        self.key = key
        self.individuals = {}

    def sorted(self):
        return sorted(self.individuals.itervalues(),key = lambda x : x.order)

    def add_rectangle(self,g,e,dt,course):
        code = e.eid(g.term)
        self.individuals[code] = Rectangle(dt,course,g.type,code,len(self.individuals),e.merge)
        return self.individuals[code]

    def _compound_json(self,rs):
        out = copy.deepcopy(rs[0])
        for r in rs:
            out.meta.additional(r.meta)
        out.add_rectangles_from_all(rs)
        return out.to_json()
    
    def to_json(self):
        r = self.sorted()
        if len(r) > 1:
            m = [self._compound_json(r)]
            for (rv,t) in element.entitle_elements_of(dict([(x,x.meta) for x in r])).iteritems():
                rv.text = t
            m.extend([y.to_json() for y in r])
            return m
        else:
            return r[0].to_json()
    
    @staticmethod
    def _real_rects(data):
        if isinstance(data,list):
            if len(data) > 1:
                return data[1:]
            else:
                return data
        else:
            return [data]
    
    @staticmethod
    def from_json(key,data):
        out = RectangleCluster(key)
        rs = RectangleCluster._real_rects(data)
        for rd in rs:
            r = Rectangle.from_json(rd,len(out.individuals))
            out.individuals[r.key] = r
        return out
        
class RectangleZoo(object):
    def __init__(self):
        self.clusters = {}

    def _make_cluster(self,key):
        if not key in self.clusters:
            self.clusters[key] = RectangleCluster(key)
        return self.clusters[key]
    
    @staticmethod
    def _calc_key(type,what,dt,course,merge):
        if merge:
            return (dt.data(),course.cid,type,True)
        else:
            return (dt.data(),course.cid,type,False,what)
    
    def _getRectangle(self,g,e,dt,course):
        cluster = self._make_cluster(RectangleZoo._calc_key(g.type,e.what,dt,course,e.merge))
        return cluster.add_rectangle(g,e,dt,course)
    
    def addPattern(self,course,group,elements):
        for atom in elements.when.each():
            termweeks = atom.getTermWeeks()
            for dt in atom.getDayTimesRaw():
                rect = self._getRectangle(group,elements,dt,course)
                rect.addEvent(termweeks,elements,atom)

    def getRectangles(self):
        return [c.sorted() for c in self.clusters.itervalues()]

    def to_json(self):
        return [c.to_json() for c in self.clusters.itervalues()]

    @staticmethod
    def zoo_from_details(course,details):
        zoo = RectangleZoo()
        for group in details.getGroups():
            for e in group.elements:
                zoo.addPattern(course,group,e)
        return zoo

    @staticmethod
    def from_json(data):
        out = RectangleZoo()
        for cdata in data:
            tmpl = cdata[0] if isinstance(cdata,list) else cdata
            dt = daytime.DayTimeRange(tmpl['day'],tmpl['starttime'],tmpl['endtime'])
            c = course.Course(tmpl['cid'],tmpl['cname']) # XXX is this correct behaviour?
            rid = tmpl['rid'].split(':')[1]
            merge = rid[0] == 'Y' if 'rid' in tmpl else True
            key = RectangleZoo._calc_key(tmpl['type'],tmpl['what'],dt,c,merge)
            out.clusters[key] = RectangleCluster.from_json(key,cdata)
        return out
