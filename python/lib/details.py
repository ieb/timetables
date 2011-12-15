import copy,collections,sys

import util
import logging

from grouptemplate import GroupTemplate
from fullpattern import FullPattern
from group import Group
import element
import datahash
import csv
import altfmt
import report
import spreadsheet
import student
import gcal
import ical

class Details(object):
    termindex = {}
    for (i,v) in enumerate(Group.longnames): termindex[v] = i
    
    def __init__(self,id,name,who,where,metadata):
        self._groups = collections.defaultdict(dict)
        self.id = id
        self.name = name
        self.who = who
        self._where = where
        self._metadata = metadata
    
    def new_same_header(self):
        return Details(self.id,self.name,self.who,self._where,self._metadata)
    
    def getGroups(self): 
        out = self._groups.values()
        return sorted(out,key = lambda x : x.key())
    
    def getGroup(self,type,term):
        if not (type,term) in self._groups:
            self._groups[(type,term)] = Group(type,term)
        return self._groups[(type,term)]
        
    def addRow(self,el):
        terms = el.getTerms()
        # for efficiency (copy is slow) if only one term we shortcut the loop
        if len(terms) == 1:
            self.getGroup(el.type,list(terms)[0]).group.append(el)
        else:
            for term in terms:
                new_el = el.copyRestrictedToTerm(term)
                if new_el is not None:
                    self.getGroup(el.type,term).group.append(new_el)
                
    def to_json(self,quick = False):
        out =  {
            'id': self.id,
            'name': self.name,
            'organiser': self.who,
            'where': self._where,
            "metadata": self._metadata,
            'groups': []
        }
        groups = sorted(self._groups.values(),key = lambda x: x.key())
        for g in groups:
            out['groups'].append(g.to_json(quick))
        out['vhash'] = datahash.datahash(out)
        return out

    def to_csv(self,f,alt = False):
        if alt:
            ss = spreadsheet.SpreadsheetWriter(f,True,self._metadata)
        else:
            ss = spreadsheet.SpreadsheetWriter(csv.writer(f,quotechar='"'),False,self._metadata)
        ss.writehead(self.id,self.name,self.who,self._where)
        groups = sorted(self._groups.values(),key = lambda x: x.key())
        for g in groups:
            g.to_csv(ss)

    def to_report(self,year,sort_text = False):
        return report.report(self,year,sort_text)

    def to_report_time(self,year):
        return report.report_time(self,year)

    def to_gcal(self,year):
        gc = gcal.GCal()
        return student.student(self,year,gc)

    def to_ical(self,year):
        gc = ical.ICal()
        return student.student(self,year,gc)

    @staticmethod
    def _add_rows_from_group_json(out,g,template,name):
        type = g['name']
        for e in g['elements']:
            out.addRow(element.Element.from_json(e,template,type,name))

    @staticmethod
    def from_json(data):
        out = Details(data['id'],data['name'],data['organiser'],data['where'],data['metadata'])
        for g in data['groups']:
            term = Details.termindex[g['term']]
            group = GroupTemplate(g['code'],term)
            Details._add_rows_from_group_json(out,g,group,data['name'])
        return out

    # XXX some of this stuff should go in spreadsheet        
    @staticmethod
    def from_csv(f,idin = None,alt = False,verifier = None):
        if alt:
            ss = spreadsheet.SpreadsheetReader(f,True)
            reader = f
        else:
            reader = csv.reader(f,quotechar='"')
            ss = spreadsheet.SpreadsheetReader(reader,False)
        (id,what,who,where) = ss.readhead()
        if verifier is not None:
            verifier.verify_head(id,what,who,where)
        if idin is not None and id != idin:
            raise Exception("ID was missing: is this the right spreadsheet?")
        dt = Details(id,what,who,where,{})
        for el in element.Element.from_csv(ss,reader,verifier):
            dt.addRow(el)
        dt._metadata = ss.get_metadata_after()
        return dt

    def metadata(self,key):
        return self._metadata[key] if key in self._metadata else ''
