import datetime
import copy
import util
import re
import logging

from fullpattern import FullPattern
from patternatom import PatternAtom
from grouptemplate import GroupTemplate

term_names = ['Michaelmas','Lent','Easter']

multispace_re = re.compile(r" +")

# XXX within term
class Year:
    def __init__(self,starts):
        self.starts = starts

    def _date(self,term,week,day):
        # day 0 = mon, .... 6 = sun
        days_after_thursday = (day+4) % 7
        # 2 is because we store Tuesday term starts
        return self.starts[term] + datetime.timedelta(days=(week-1)*7) + datetime.timedelta(days = days_after_thursday+2)

    def atoms_to_secular(self,atoms,show_time = True):
        full = []
        short = []
        common = True
        terms = set()
        for atom in atoms:
            for term in atom.getTerms():
                terms.add(term)
        for term in terms:
            for atom in atoms:
                when = []
                weeks = atom.getTermWeeks().weeks_of_term(term)
                for week in weeks:
                    for dt in atom.getDayTimesRaw():
                        (day,time) = dt.rep2()
                        date = self._date(term,week,day)
                        when.append((date,time))
                for (date,time) in sorted(when,key = lambda x: x[0]):
                    daystr = date.strftime("%e %b")
                    full.append("%s at %s" % (daystr,time))
                    short.append(daystr)
                    if common is True:
                        common = time
                    elif common is not False and common != time:
                            common = False
        if show_time:
            if common is not False and common is not True:
                # oclock, etc
                out = "at %s on %s" % (common,", ".join(short))
            else:
                out = ", ".join(full)
        else:
            out = ", ".join(short)
        out = multispace_re.sub(' ',out)
        return out

    def _to_iso(self,date,time,as_datetime):
        dt = datetime.datetime.combine(date,time)
        dt -= datetime.timedelta(microseconds = dt.microsecond) # round to nearest second
        if as_datetime:
            return dt
        return dt.isoformat()+"Z"

    def atoms_to_isos(self,atoms,as_datetime = False):
        out = []
        for atom in atoms:
            for frag in atom.blast():
                for (term,week) in frag.getTermWeeks().each():
                    for dt in frag.getDayTimesRaw():
                        date = self._date(term,week,dt.day)
                        start = datetime.time(dt.start[0],dt.start[1])
                        end = datetime.time(dt.end[0],dt.end[1])
                        out.append((self._to_iso(date,start,as_datetime),self._to_iso(date,end,as_datetime)))
        return out

    def to_templated_secular_display(self,fp,group,type= 'lecture'):
        gt = GroupTemplate(None)
        gt.add_patterns(fp)
        gt.calculate_reduction(True)
        out = []
        for (_,_,(pattern,mult)) in gt.get_patterns_raw(False):
            if pattern is None:
                # just multiplier, should be just "x lectures"
                row = "%d %s, %s" % (mult,util.plural(type),gt.template) # XXX proper plurals
            elif mult is None:
                # traditional pattern, expand codes sensibly
                row = "%s %s" % (util.plural(type),self.atoms_to_secular(fp.patterns(),True))
            else:
                # start date and multiplier
                pp = copy.deepcopy(gt.template)
                pp.setAllYear()
                row = "%s %s, starting on %s, %s" % (mult,util.plural(type),self.atoms_to_secular([pattern],False),pp)
            out.append(row)
        prefix = ''
        if group is not None:
            prefix = "%s term, " % term_names[group.term]
        return prefix+", ".join(out)
