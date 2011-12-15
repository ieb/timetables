import util
from grouptemplate import GroupTemplate
import fullpattern
import altfmt
import copy

class Element(object):
    def __init__(self,who = None,what = None,where = None,when = None,merge = None,type = None,course = None):
        (self._who,self._what,self._where,self._when,self._merge,self._type,self._cname) = (who,what,where,when,1 if merge else 0,type,course)
        if isinstance(self._when,str):
            raise Exception("string! '%s'" % self._when)


    attrs = set(['who','what','where','when'])
    sattrs = set(['type','merge','cname'])

    attrs = {
        'who': { 'mode': 'various', 'code': ['who'] },
        'what': { 'mode': 'various', 'code': ['what'] },
        'where': { 'mode': 'various', 'code': ['where'] },
        'when': { 'mode': 'various', 'code': ['when','code'] },
        'type': { 'mode': 'plain', 'code': [] },
        'merge': { 'mode': 'plain', 'code': ['merge'] },
        'cname': { 'mode': 'plain', 'code': [] },
    }

    def to_rect_json(self):
        out = {}
        for (attr,vals) in Element.attrs.iteritems():
            for code in vals['code']:
                out[code] = self.__getattr__(attr)
        return out

    def __repr__(self):
        return str((self._who,self._what,self._where,self._when,self._merge))

    def key(self):
        if isinstance(self._when,str):
            print self
            raise Exception("string! '%s'" % self._when)
        return self._when.key()

    def __getattr__(self,name):
        if not name in Element.attrs:
            return object.__getattribute__(self,name)           
        key = '_'+name
        v = self.__dict__[key]
        if Element.attrs[name]['mode'] == 'various':
            return v if v else "Unspecified"
        elif Element.attrs[name]['mode'] == 'plain':
            return v

    def __setattr__(self,name,value):
        if name in Element.attrs or name in Element.sattrs:
            self.__dict__['_'+name] = value
        else:
            self.__dict__[name] = value

    def specified(self,name):
        key = '_'+name
        return key in self.__dict__ and self.__dict__[key] is not None

    def _clash(self,a,b,clash):
        if a is None:
            return b
        elif a != b:
            return apply(clash,[a,b])
        else:
            return a

    def _clash_when(self,a,b):
        a.addAll(b)
        return a

    def _clash_what(self,a,b):
        out = "Various"
        if self._type is not None:
            out += " " + self._type + "s" # XXX proper plurals
            out += " of " + self._cname
        return out

    def additional(self,other):
        self._who = self._clash(self._who,other._who,lambda a,b: "Various")
        self._where = self._clash(self._where,other._where,lambda a,b: "Various")
        self._when = self._clash(self._when,other._when,self._clash_when)
        self._what = self._clash(self._what,other._what,self._clash_what)        
        if other._type is None:
            self._type = None
        else:
            if self._type is not None and self._type != other._type:
                self._type = None

    def update_with(self,other,orig = None):
        if orig is not None:
            if other._who != orig._who:
                self._who = other._who
            if other._where != orig._where:                                
                self._where = other._where
            if str(other._when) != str(orig._when):                
                self._when = other._when
            if other._what != orig._what:                
                self._what = other._what
            if other._type != orig._type:                
                self._type = other._type
        else:
            self._who = other._who
            self._where = other._where
            self._when = other._when
            self._what = other._what
            self._type = other._type

    def restrictToTerm(self,term):
        self._when.restrictToTerm(term)
        return not self._when.empty()

    def copyRestrictedToTerm(self,term):
        out = copy.copy(self)
        out._when = self._when.copyRestrictedToTerm(term)
        any = not out._when.empty()
        return out if any else None

    def getTerms(self):
        return self._when.getTerms()

    def eid(self,term):
        self.when.tidy() # XXX shouldn't depend on tidyness of when, should have stable hash into when
        return util.hashid('E',self.type,term,self.what,self.who,self.where,str(self.when),self.merge)

    def el_to_json(self,term,pattern):
        out = self.to_rect_json()
        p = pattern if pattern is not None else self._when
        out['code'] = str(p)
        out['when'] = str(p)
        out['eid'] = self.eid(term)
        return out

    @staticmethod
    def from_json(e,template,type,name):
        out = Element(e['who'],e['what'],e['where'],fullpattern.FullPattern(e['code'],template),e['merge'],type,name)
        if isinstance(out._when,str):
            raise Exception("string! '%s'" % out._when)
        return out

    def to_csv(self,ss):
        ss.writerow(self._cname,self._type,self._who,self._what,self._when,self._where,self._merge)

    @staticmethod
    def from_csv(ss,reader,verifier = None):
        for row in reader:            
            data = ss.readrow(row)
            if data is None:
                continue
            (name,type,who,what,when,where,merge) = data
            if verifier is not None:
                verifier.verify_row(name,type,who,what,when,where,merge)
            merge = merge.lower() == 'yes' or merge.lower() == 'true'
            yield Element(who,what,where,fullpattern.FullPattern(when),merge,type,name)

def entitle_elements_of(data):
    titles = [(x,e.what) for (x,e) in data.items()]
    twhere = [(x,"%s (%s)" % (e.what,e.where)) for (x,e) in data.items()]
    twho = [(x,"%s (%s)" % (e.what,e.who)) for (x,e) in data.items()]
    twherewho = [(x,"%s (%s, %s)" % (e.what,e.who,e.where)) for (x,e) in data.items()]
    return dict(min([titles,twhere,twho,twherewho],key = lambda t: len(set(dict(t).values()))))
