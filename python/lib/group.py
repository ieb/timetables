import util
from grouptemplate import GroupTemplate
import element
import logging

class Group(object):
    longnames = ['Michaelmas','Lent','Easter']
    
    def __init__(self,type,term):
        self.type = type
        self.term = term
        self.group = []

    def key(self):
        return "%1.1d%s" % (self.term,self.type)

    @property
    def elements(self):
        return sorted(self.group,key = lambda x: x.key())

    def best_template(self):
        gt = GroupTemplate(None,self.term)
        for e in self.elements:
            gt.add_patterns(e.when,e)
        gt.calculate_reduction()
        gt.restrict_to_term(self.term)
        return gt

    def to_json(self, quick = False):
        if quick:
            out = {
                'name': self.type,
                'term': Group.longnames[self.term],
                'code': '',
                'elements': []
            }
            els = out['elements']
            for e in self.group:
                els.append(e.el_to_json(self.term,None))            
        else:        
            group = self.best_template()
            out = {
                'name': self.type,
                'term': Group.longnames[self.term],
                'code': str(group.template),
                'elements': []
            }
            els = out['elements']
            for (_,e,p) in group.get_patterns():
                els.append(e.el_to_json(self.term,p))
        return out

    def to_csv(self,ss):
        for el in self.elements:
            el.to_csv(ss)
