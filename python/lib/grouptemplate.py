import collections

import pparser
import tracker
import util
import besttmplcalc
import logging

class GroupTemplate(object):
    def __init__(self,template,term = None):
        self.term = term
        if template is not None:
            self.template = pparser.parseone(str(template))
            self._tracker = tracker.OffsetTracker(self.template,term)
        self._patterns = []

    def restrict_to_term(self,term):
        self.template.restrictToTerm(term)

    def add_patterns(self,ps,payload = None):
        self._patterns.append([ps,payload,None])        

    def inherit_daytime(self,pattern):
        pattern.addDayTimesFrom(self.template)

    def inherit_termweek(self,pattern):
        pattern.addTermWeeksFrom(self.template)

    def track_pattern(self,p):
        self._tracker.addPattern(p)

    def get_next_n(self,start,mult = 1,trial = False):
        return sorted(self._tracker.addNextN(mult,trial = trial,starting = start),key = lambda x: x.key())        

    def _does_xn_match_starting_at(self,starting,count,got):
        want = self.get_next_n(starting,count,trial = True)
        out = map(lambda x: str(x),want) == map(lambda x: str(x),got)
        if out:
            self.get_next_n(starting,count,trial = False)
        return out

    def get_patterns_raw(self,allow_unbased = True):
        hits = 0
        misses = 0
        for m in self._patterns:
            ps = m[0]
            first_here = ps.first()
            us = sorted(ps.blast(),key = lambda x: x.key())
            first_unused = self._tracker.first_unused()
            count = ps.count()
            rendered = None
            if allow_unbased and first_unused is not None and self._does_xn_match_starting_at(first_unused,count,us):
                m[2] = (None,count)
                hits += count
            elif self._does_xn_match_starting_at(first_here,count,us):
                m[2] = (first_here,count)
                hits += count
            else:
                m[2] = (m[0].format(group = self),None)
                misses += count
            for p in ps.each():
                self._tracker.addPattern(p)
        if hits*3 < (hits+misses)*2:
            # Patterns don't help: revert
            for m in self._patterns:
                m[2] = (m[0].format(group = self),None)
        return self._patterns

    def get_patterns(self,allow_unbased = True):
        out = []
        for m in self.get_patterns_raw(allow_unbased):
            (main,mult) = m[2]
            if main is None: main = ''
            mult = 'x'+str(mult) if mult is not None else ''
            m[2] = "%s %s" % (main,mult)
            out.append(m)
        return out

    def last(self):
        return self._tracker.last()

    def calculate_reduction(self,extended = False):
        self.template = besttmplcalc.best(self._patterns,extended)
        self._tracker = tracker.OffsetTracker(self.template,self.term)
