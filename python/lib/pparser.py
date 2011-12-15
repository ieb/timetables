import re
import sys
import string
import patternatom

import plexer

import fullpattern

class AtomParser(object):
    def __init__(self,input,group = None):
        self._lexer = plexer.BufferingLexer(input)
        self._group = group
        self._mult = None
        self._implicit = False

    def parse_template(self):
        self._pattern = patternatom.PatternAtom(True)
        self._parse_top(True)
        return self._pattern

    def parse_full(self):
        self._pattern = patternatom.PatternAtom(False)
        self._parse_top(False)
        return (self._pattern,self._mult,self._implicit)

    def _parse_top(self,template):
        if self._lexer.attempt('CHAR','x'):
            q = self._lexer.popreq('MULT')
            self._mult = int(q[1])
            if not template:
                self._pattern.setAllYear()
                self._implicit = True
        elif self._lexer.peek_is('TERM'):
            self._parse_term_weeks()
        elif self._group is not None:
            self._group.inherit_termweek(self._pattern)
        else:
            self._pattern.setAllYear()
        self._parse_day_times()
        if not template:
            self._parse_mults()

    def _add_days_times(self,days,times):
        for day in days:
            for time in times:
                self._pattern.addDayTimeRange(day,time[0],time[1],time[2],time[3])

    def _add_days(self,days):
        raise Exception("Whole days not supported yet")

    def _parse_day_times(self):
        self._parse_day_time()
        if self._lexer.peek_is('DAY'):
            self._parse_day_times()

    def _parse_day_time(self):
        days = self._parse_days()
        if days is None and self._group is not None:
            self._group.inherit_daytime(self._pattern)
        if self._lexer.peek_is('TIME'):
            times = self._parse_times()
            self._add_days_times(days,times)
        elif days is not None:
            self._add_days(days)
    
    def _parse_term_weeks(self):
        p = self._lexer.popreq('TERM')
        if self._lexer.peek_is('WEEKNO'):
            for week in self._parse_weeks():
                self._pattern.addTermWeek(p[1],week)
        else:
            self._pattern.setAllInTerm(p[1])
        if self._lexer.attempt('CHAR',','):
            self._parse_term_weeks()
        if self._lexer.peek_is('TERM'):
            self._parse_term_weeks()
            
    def _parse_weeks(self):
        out = self._parse_week_range()
        if self._lexer.attempt('CHAR',','):
            if self._lexer.peek_is('WEEKNO'):
                out |= self._parse_weeks()
        return out
    
    def _parse_week_range(self):
        p = self._lexer.popreq('WEEKNO')
        if self._lexer.attempt('CHAR','-'):
            r = self._lexer.popreq('WEEKNO')
        else:
            r = p
        out = set()
        for i in range(int(p[1]),int(r[1])+1):
            out.add(i)
        return out

    def _parse_days(self):
        days = self._parse_day_range()
        if self._lexer.attempt('CHAR',','):
            days |= self._parse_days()
        return days
        
    def _parse_day_range(self):
        if self._lexer.peek()[0] == 'EOF' or self._lexer.peek_is('CHAR','x'):
            return None
        p = self._lexer.pop()
        if self._lexer.attempt('CHAR','-'):
            r = self._lexer.popreq('DAY')
        else:
            r = p
        (a,b) = (int(p[1]),int(r[1]))
        if b < a:
            b += 7
        out = set()
        for i in range(a,b+1):
            out.add(i%7)
        return out

    def _parse_times(self):
        out = set()
        out.add(self._parse_time_range())
        if self._lexer.attempt('CHAR',','):
            if self._lexer.peek_is('TIME'):
                out |= self._parse_times()
        return out
    
    def _parse_time_range(self):
        p = self._parse_time()
        if self._lexer.attempt('CHAR','-'):
            r = self._parse_time()
        else:
            r = (p[0]+1,p[1])
        return (p[0],p[1],r[0],r[1])
        
    def _parse_time(self):
        p = self._lexer.popreq('TIME')
        hr = int(p[1])
        if not self._lexer.attempt('CHAR','!') and hr < 8:
            hr += 12
        if self._lexer.attempt('CHAR',':'):
            r = self._lexer.popreq('TIME')
        else:
            r = (None,0)
        return (hr,int(r[1]))

    def _parse_mults(self):
        if self._lexer.attempt('CHAR','x'):
            q = self._lexer.popreq("MULT")
            self._mult = int(q[1])

class FullParser(object):
    def __init__(self,text,group = None):
        self._p = AtomParser(text,group)
        self._group = group

    def _apply(self,base,mult):
        out = fullpattern.FullPattern()
        for p in self._group.get_next_n(base,mult,trial = False):
            out.addAll(p)
        return out
        
    def parse(self):
        (base,mult,implicit) = self._p.parse_full()
        if mult is not None and self._group is not None:
            if implicit:
                base = self._group.last()
            return self._apply(base,mult)        
        else:
            out = fullpattern.FullPattern(base)
            if self._group is not None:
                self._group.track_pattern(out)
            return out

def fullparse(text,template = None):    
    return FullParser(text,group = template).parse()
        
def parseone(text):
    return AtomParser(text).parse_template()
  
# XXX compact patterns generation from pattern list    
if __name__ == '__main__' and False:
    from grouptemplate import GroupTemplate
    
    g = GroupTemplate("TuThSa12")
    p = fullparse("Mi1 Tu12 x4",g)
    g.add_patterns(p)
    print p.format(group = g)
    print g.get_patterns()
