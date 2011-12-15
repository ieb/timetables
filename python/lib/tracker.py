"""
tracker / OffsetTracker is a class which keeps track of which of the slots 
defined in a template have already been seen and uses this information to
answer questions about offsets for advanced x expressions.
"""

import copy
import logging

class OffsetTracker(object):
    def __init__(self,reduction,term):
        # iterate through slots
        self._all = {}
        blasted = []
        for v in reduction.blast():
            if term is not None and v.firstTermWeek()[0] != term:
                continue
            blasted.append(v)
        for (i,v) in enumerate(blasted):
            self._all[i] = v
        self._unused = set(range(0,len(self._all.keys())))
        self._last = None
        self.reduction = reduction
        
    def addPattern(self,p):
        for pp in p.blast():
            for (idx,member) in self._all.iteritems():
                if pp == member:
                    if idx in self._unused:
                        self._unused.remove(idx)
            if self._last is None or self._last.key() < pp.key():
                self._last = pp

    def _calc_init_offset(self,ordered,starting):
        offset = -1
        if starting is not None:
            for i in range(0,len(ordered)):
                if i in self._unused and str(starting) == str(self._all[ordered[i]]): # XXX should be able to compare directly
                    offset = i
                    break
            if offset == -1:
                for i in range(0,len(ordered)):
                    if int(starting.key()) <= int(self._all[ordered[i]].key()):
                        offset = i
                        break
        if offset == -1:
            offset = 0
        return offset

    def addNextN(self,n,trial = False,starting = None):
        # XXX add in out-of-range dates
        ordered = sorted(self._unused)
        offset = self._calc_init_offset(ordered,starting)
        out = set()
        for i in range(offset,min(offset+n,len(ordered))):
            out.add(ordered[i])
            if not trial:
                self._unused.remove(ordered[i])
        return [self._all[i] for i in out]

    def last(self):
        return self._last

    def first_unused(self):
        unused = []
        for i in self._unused:
            unused.append(self._all[i])
        if not len(unused):
            return None
        return min(unused,key = lambda x : x.key())
