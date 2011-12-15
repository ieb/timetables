import util,collections,sys
import traceback

from copy import deepcopy,copy

from daytime import DayTimeRange
from termweek import TermWeek
import pparser
import tracker

# hours 1-7 -> 13-19

class PatternAtom(object):
    dayname = ['M','Tu','W','Th','F','Sa','Su']
    terms = ['Mi','Le','Ea']
    
    def __init__(self,template):
        self._daytimes = []
        self._termweeks = TermWeek()
        self._template = template # currently unused, but should be useful in reducing confusion in this class re omissions
    
    def addTermWeek(self,term,week):
        self._termweeks.addTermWeek(term,week)
    
    def addDayTimeRange(self,dy,fh,fm,th,tm):
        self._daytimes.append(DayTimeRange(dy,fh,fm,th,tm))

    def addDayTimeRangeDirect(self,c):
        self._daytimes.append(c)

    def getDayTimesRaw(self):
        return self._daytimes
    
    def getTermWeeks(self):
        return self._termweeks  
    
    def getTerms(self):
        return self._termweeks.getTerms()
    
    def restrictToTerm(self,t):
        self._termweeks.restrictToTerm(t)

    def copyRestrictedToTerm(self,term):
        out = copy(self)
        out._termweeks = self._termweeks.copyRestrictedToTerm(term)
        return out
    
    def restrictToDayTimeRange(self,dy,fh,fm,th,tm):
        r = DayTimeRange(dy,fh,fm,th,tm)
        out = []
        for dt in self._daytimes:
            if dt.intersect_test(r):
                out.append(dt)
        self._daytimes = out
    
    def removeDayTimeRangeDirect(self,target):        
        hit = target in self._daytimes
        self._daytimes = filter(lambda x: x != target,self._daytimes)
        return hit
    
    def addTermWeeksFrom(self,src):
        self._termweeks.merge(src._termweeks)
    
    def addDayTimesFrom(self,src):
        self._daytimes.extend(deepcopy(src._daytimes))            
    
    def setAllYear(self):
        self._termweeks.set_all()

    def setAllInTerm(self,term):
        self._termweeks.set_all_in_term(term)
    
    def empty(self):
        if len(self._daytimes) == 0:
            return True
        return not len(self._termweeks)
    
    def firstDayTime(self):
        return min(self._daytimes)
    
    def firstTermWeek(self):
        return self._termweeks.first()

    def lastDayTime(self):
        return max(self._daytimes)
    
    def key(self):
        (first_term,first_week) = self._termweeks.first()
        day = set([x.day for x in self._daytimes])
        first_day = min([(x+4)%7 for x in day])
        m_day = (first_day+3)%7
        min_time = set()        
        for d in [x for x in self._daytimes if x.day == m_day]:
            min_time.add(d.startval())
        if len(min_time):
            min_time = min(min_time)
        else:
            min_time = 0
        return "%1.1d%2.2d%1.1d%4.4d" % (first_term,first_week,first_day,min_time)
    
    def merge(self,other):
        # If dts are equivalent, can merge tws
        if set(self._daytimes) == set(other._daytimes):
            # Merge tws
            out = deepcopy(self)
            out._termweeks.merge(other._termweeks)
            return out
        # If tws are equivalent, can merge dts
        if self._termweeks == other._termweeks:
            out = deepcopy(self)
            out._daytimes.extend(deepcopy(other._daytimes))
            return out
        return None
    
    def _after(self,(term,week),cur):
        x = util.successor(self._daytimes,cur)
        if x is None:
            (term,week) = self._termweeks.successor(term,week)
            if term is None and week is None:
                return None
            return ((term,week),self.firstDayTime())
        else:
            return ((term,week),x)
    
    def plus(self,parent,offset):
        (term,week) = self._termweeks.last()
        pos = ((term,week),self.lastDayTime())
        for i in range(0,offset):
            pos = apply(parent._after,pos)
            if pos is None:
                return None
        ((term,week),next_dt) = pos
        out = PatternAtom(False)
        out.addTermWeek(term,week)
        out.addDayTimeRangeDirect(next_dt)
        return out
    
    def first(self):
        (term,week) = self.firstTermWeek()
        out = PatternAtom(False)
        out.addTermWeek(term,week)
        out.addDayTimeRangeDirect(self.firstDayTime())
        return out
    
    def __repr__(self):
        return self.format_atom()

    def _format_termweeks(self,reduction):
        if reduction is not None and  self._termweeks == reduction._termweeks:
            return ""
        out = []
        if not self._termweeks.all_weeks_of_year_test():
            for term in self._termweeks.each_term():
                weeks = self._termweeks.weeks_of_term(term)
                if self._termweeks.all_weeks_of_term_test(term):
                    s = ''
                else:
                    s = util.number_range_text(weeks)
                out.append("%s%s" % (self.terms[term],s))
        return " ".join(out)

    def _format_daytimes(self,reduction):
        if reduction is not None and set(reduction._daytimes) == set(self._daytimes):
            return ""
        # collate by time
        daysbytime = collections.defaultdict(set)
        for dt in self._daytimes:
            (day,time) = dt.rep2()
            daysbytime[time].add(day)
        # sort by time. For now we only care about stability, should also care about sensibleness XXX
        keys = sorted(daysbytime.keys())
        # emit    
        out = []
        for time in keys:
            days = daysbytime[time]
            out.append(util.hide_commas(util.number_range_text(days,self.dayname)))
            out.append(time)
        return " ".join(out)
    
    # XXX force verbosity on overriding
    def format_atom(self,reduction = None):
        if not reduction:
            reduction = pparser.parseone("MiLeEa")
        out = []
        ts = self._format_termweeks(reduction)
        if ts:
            out.append(ts)
        # days and times
        dts = self._format_daytimes(reduction)
        if dts:
            out.append(dts)
        return " ".join(out)
    
    def count(self):
        return len(self._termweeks) * len(self._daytimes)
            
    def blast(self):
        out = []
        for (term,week) in self._termweeks.each():
            for dt in self._daytimes:
                p = PatternAtom(False)
                p.addTermWeek(term,week)
                p.addDayTimeRangeDirect(dt)
                out.append(p)
        return sorted(out,key = lambda x: x.key())

    def expand_back_to(self,datetime):
        for term in range(0,3):
            first_week = datetime._termweeks.first_week_of_term(term)
            if first_week is None:
                continue
            self._termweeks.expand_back_to_week(term,first_week)

    def expand_forward_to(self,datetime):
        for term in range(0,3):
            last_week = datetime._termweeks.last_week_of_term(term)
            if last_week is None:
                continue
            self._termweeks.expand_forward_to_week(term,last_week)

    def __eq__(self,other):
        if self._template != other._template:
            return False
        if self._termweeks != other._termweeks:
            return False
        if set(self._daytimes) != set(other._daytimes):
            return False
        return True

    def __ne__(self,other):
        return not self.__eq__(other)
