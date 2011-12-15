import pparser
import patternatom
from copy import deepcopy,copy
import traceback

class FullPattern(object):    
    def __init__(self, patterns=None, group=None):
        self._patterns = []
        self._pg = group
        if patterns is not None:
            self.addAll(patterns)
        self._tidied = False
    
    def copyRestrictedToTerm(self,term):
        out = copy(self)
        out._patterns = []
        for p in self._patterns:
            q = p.copyRestrictedToTerm(term)
            if not q.empty():
                out._patterns.append(q)
        out._tidied = False
        return out
    
    def patterns(self):
        return self._patterns
    
    def addOne(self, p, copy=False):
        if not isinstance(p, patternatom.PatternAtom):
            x = None
            try:
                x = pparser.fullparse(p, self._pg)
            except Exception as e:
                print "Cannot parse '%s', probably unimplemented" % p
                #traceback.print_exc(e)
                raise e
            if x is not None:
                self.addAll(x)
            return
        if p.empty():
            return
        if copy:
            p = deepcopy(p)
        self._patterns.append(p)
        self._tidied = False

    def addAll(self, ps, copy=False):
        if isinstance(ps, FullPattern):
            for p in ps._patterns:
                self.addOne(p, copy)
        elif isinstance(ps, patternatom.PatternAtom):
            self.addOne(ps, copy)
        else:
            try:
                for p in ps.split(";"):
                    self.addOne(p.strip(), copy)
            except Exception, e:
                raise e
                raise Exception("addAll doesn't understand %s" % ps.__class__)
            
    def empty(self):
        if len(self._patterns) == 0:
            return True
        for p in self._patterns:
            if not p.empty():
                return False
        return True

    def key(self):
        if not self._patterns:
            return ""
        return min([x.key() for x in self._patterns])

    def _merge_one(self, ps, one):
        for (i, p) in enumerate(ps):
            q = one.merge(p)
            if q is not None:
                ps[i] = q
                return
        ps.append(one)
        
    def _merge(self, ps):
        out = []
        for p in ps:
            if p.empty():
                continue
            self._merge_one(out, p)
        return out

    def tidy(self):
        if self._tidied:
            return
        while True:
            a = len(self._patterns)        
            self._patterns = self._merge(self._patterns)
            b = len(self._patterns)
            if b >= a:
                break        
        self._patterns = sorted(self._patterns, key=lambda x: x.key())
        self._tidied = True

    def each(self, fn=None, destructive=True):
        self.tidy()
        if fn == None:
            return filter(lambda x: not x.empty(), self._patterns)
        for p in self._patterns:
            if not p.empty():
                fn(p)
        if destructive:
            self._tidied = False

    def restrictToTerm(self,t):
        new = []
        for p in self._patterns:
            p.restrictToTerm(t)
            if not p.empty():
                new.append(p)
        self._patterns = new

    def getTerms(self):
        out = set()
        for p in self._patterns:
            out |= p.getTerms()
        return out

    def blast(self):
        out = []
        for p in self._patterns:
            out.extend(p.blast())
        return out

    def count(self):
        count = 0
        for p in self.each(destructive=False):
            count += p.count()
        return count

    def first(self):
        firsts = []
        for p in self.each(destructive=False):
            firsts.append(p.first())
        firsts = sorted(firsts, key=lambda x : x.key())
        if len(firsts):
            return firsts[0]
        return None

    def format(self, group=None):
        self.tidy()
        out = []
        reduction = group.template if group is not None else None
        for p in self._patterns:
            out.append(p.format_atom(reduction = reduction))
        return " ; ".join(out)

    def __repr__(self):
        return self.format()
