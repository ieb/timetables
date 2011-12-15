import collections

class TermWeek:
    def __init__(self):
        self._termweeks = collections.defaultdict(set)
        
    def addTermWeek(self,term,week):
        self._termweeks[term].add(week)

    def copyRestrictedToTerm(self,term):
        out = TermWeek()
        out._termweeks[term] = self._termweeks[term]
        return out
        
    def getTerms(self):
        out = set()
        for (k,v) in self._termweeks.iteritems():
            if len(v):
                out.add(k)
        return out
        
    def restrictToTerm(self,t):
        v = self._termweeks[t]
        self._termweeks = collections.defaultdict(set)
        self._termweeks[t] = v            

    def each(self):
        for term in range(0,3):
            for weeks in sorted(self._termweeks[term]):
                yield (term,weeks)

    def merge(self,other):
        for term in self.each_term(True):
            self._termweeks[term] |= other._termweeks[term]

    def set_all_in_term(self,term):
        self._termweeks[term] = set(range(1,9))

    def set_all(self):
        for term in self.each_term(True):
            self.set_all_in_term(term)

    def first(self):
        for (term,week) in self.each():
            return (term,week)
        return None

    def last(self):
        for (term,week) in self.each():
            (out_term,out_week) = (term,week)
        return (out_term,out_week)

    def each_term(self,even_empty = False):
        for term in range(0,3):
            if even_empty or len(self._termweeks[term]):
                yield term

    def weeks_of_term(self,term):
        return self._termweeks[term]

    def first_week_of_term(self,term):
        tw = self._termweeks[term]
        if len(tw) > 0:
            return min(tw)
        return None

    def last_week_of_term(self,term):
        tw = self._termweeks[term]
        if len(tw) > 0:
            return max(tw)
        return None

    def expand_back_to_week(self,term,start):
        cur_min = min(self._termweeks[term])
        for w in range(start,cur_min):
            self._termweeks[term].add(w)

    def expand_forward_to_week(self,term,end):
        cur_max = max(self._termweeks[term])
        for w in range(cur_max+1,end+1):
            self._termweeks[term].add(w)

    def all_weeks_of_term_test(self,term):
        return self._termweeks[term] == range(1,9)
    
    def all_weeks_of_year_test(self):
        for term in self.each_term(True):
            if not self.all_weeks_of_term_test(term):
                return False
        return True

    def successor(self,term,week):
        threshold = week
        for term in range(term,3):
            x = util.successor(self._termweeks[term],threshold)
            if x is not None: return (term,x)
            threshold = 0
        return (None,None)

    def __len__(self):
        return reduce(lambda c, x: c + len(x),self._termweeks.itervalues(),0)
        
    def __eq__(self,other):
        for term in self.each_term(True):
            if self._termweeks != other._termweeks:
                return False
        return True

    def __ne__(self,other): return not self.__eq__(other)
