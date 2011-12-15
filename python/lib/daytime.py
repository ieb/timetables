class DayTimeRange(object):
    dayname = ['M','Tu','W','Th','F','Sa','Su']
    
    def __init__(self,dy,fh,fm,th = None,tm = None):
        if th is None:
            (fh,fm,th,tm) = (fh[0],fh[1],fm[0],fm[1])
        self._dy = dy
        self._fh = fh
        self._fm = fm
        self._th = th
        self._tm = tm

    def format_single_time(self,h,m):
        # hour format
        if h >= 13 and h <= 19:
            hr = str(h-12)
        elif h <= 7:
            hr = str(h)+"!"
        else:
            hr = str(h)
        # minute format
        if m != 0:
            return "%s:%2.2d" % (hr,m)
        else:
            return hr

    def intersect_test(self,other):
        if self._dy != other._dy:
            return False
        if self._fh < other._fh or (self._fh == other._fh and self._fm < other._fm):
            (self._fh,self._fm) = (other._fh,other._fm)
        if self._th < other._th or (self._th == other._th and self._tm < other._tm):
            (self._th,self._tm) = (other._th,other._tm)
        if self._th < self._fh or (self._fh == self._th and self._fm >= self._tm):
            return False
        return True

    def rep2(self):
        if self._fm == self._tm and self._th == self._fh + 1:
            time = self.format_single_time(self._fh,self._fm)
        else:
            time = "%s-%s" % (self.format_single_time(self._fh,self._fm),self.format_single_time(self._th,self._tm))
        return (self._dy,time)

    def __repr__(self):
        return self.format_day_time()
        
    def format_day_time(self):
        (day,time) = self.rep2()
        return "%s %s" % (self.dayname[day],time)

    def data(self):
        return (self._dy,(self._fh,self._fm),(self._th,self._tm))
    
    def startval(self):
        return self._fh * 60 + self._fm

    @property    
    def day(self):
        return self._dy

    @property
    def start(self):
        return (self._fh,self._fm)

    @property
    def end(self):
        return (self._th,self._tm)
    
    def key(self):
        return "%1.1d%4.4d" % ((self._dy+4)%7,self.startval())

    # these three needed for set ops and ordering
    def __eq__(self,other): return self.data().__eq__(other.data())
    def __ne__(self,other): return self.data().__ne__(other.data())
    def __lt__(self,other): return self.key().__lt__(other.key())
    def __le__(self,other): return self.key().__le__(other.key())
    def __gt__(self,other): return self.key().__gt__(other.key())
    def __ge__(self,other): return self.key().__ge__(other.key())

    def __hash__(self):
        return self.data().__hash__()    
    