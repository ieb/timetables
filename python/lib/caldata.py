import sys

import collections
import rectangle
import datahash

def cid(r):
    try:
        return r[0]['cid']
    except:
        return r['cid']

class CalData(object):
    def __init__(self,id):
        self.id = id
        self.zoos = collections.defaultdict(list)
        self.courses = {}

    def refresh_course(self,c):
        self.courses[c.cid] = { 'name': c.cname, 'id': c.cid }

    def make_course_static(self,c,static):
        self.courses[c.cid]['staticurls'] = static

    def replace_course_rectangles(self,c,zoo):
        self.zoos[c.cid] = zoo

    def all_individual_rectangles(self):
        out = []
        for z in self.zoos.itervalues():
            for c in z.clusters.itervalues():
                out.extend(c.individuals.values())
        return out

    @staticmethod
    def from_json(data):
        new = []
        out = CalData(data['id'])
        zoodata = collections.defaultdict(list)
        for ra in data['rectangles']:
            if not isinstance(ra,list):
                ra = [ra]
            existing = []
            for r in ra:
                if r['cid'].startswith('createdseries_'):
                    new.append(r)
                else:
                    existing.append(r)
            if len(existing):
                zoodata[cid(ra)].append(existing)
        for (c,d) in zoodata.iteritems():
            out.zoos[c] = rectangle.RectangleZoo.from_json(d)
        out.courses = data['courses']
        return (out,new)

    def each_course_individual_rectangles(self):
        for (cid,z) in self.zoos.iteritems():
            out = []
            for c in z.clusters.itervalues():
                out.extend(c.individuals.values())
            yield (cid,out)
 
    def to_json(self):
        rects = []
        for z in self.zoos.itervalues():
            rects.extend(z.to_json())
        out = {
            'id': self.id,
            'rectangles': rects,
            'courses': self.courses
        }
        out['vhash'] = datahash.datahash(out)
        return out
