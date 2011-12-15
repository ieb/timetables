import re
import sys
import string

digits_re = re.compile(r"^([0-9]+)")

class RawLexer(object):
    terms = ['mi','le','ea']
    days = ['m','tu','w','th','f','sa','su'] # also 's' (=='sa') handled separately
    range = [',','-','!']
    misc = ['x',':','.']
    
    debug = False
    
    def __init__(self,input):
        self._input = input.lower()
        self._terms_ok = True
        self._week_no = False
        self._after_x = False
    
    def _prefix(self,options,pos = False):
        i = 0
        for op in options:
            if self._input.startswith(op):
                self._input = self._input[len(op):]
                if pos:
                    return i
                else:
                    return op
            i += 1
        return None
        
    def pop(self):
        p = self._pop()
        if RawLexer.debug:
            print >>sys.stderr,str(p)
        return p
        
    def _pop(self):
        # skip whitespace
        while len(self._input) and self._input[0] in string.whitespace:
            self._input = self._input[1:]
        # eof
        if not len(self._input):
            return ("EOF",None)
        # digits
        d = digits_re.match(self._input)
        if d != None:
            self._input = self._input[len(d.group(1)):]
            if self._after_x:
                return ("MULT",d.group(1))
            elif self._week_no:
                return ("WEEKNO",d.group(1))
            else:
                return ("TIME",d.group(1))
        # terms
        if self._terms_ok:
            tm = self._prefix(self.terms,True)
            if tm != None:
                self._week_no = True # digits are week numbers
                return ("TERM",tm)
        # days
        dy = self._prefix(self.days,True)
        if dy != None:
            self._terms_ok = False          
            self._week_no = False
            return ("DAY",dy)
        if self._input[0] == 's':
            self._terms_ok = False          
            self._week_no = False
            self._input = self._input[1:]
            return ("DAY",5)            
        # range
        rg = self._prefix(self.range)
        if rg != None:
            return ("CHAR",rg)
        # misc
        ms = self._prefix(self.misc)
        if ms != None:
            self._terms_ok = False
            self._week_no = False          
            if ms == 'x':
                self._after_x = True
            return ("CHAR",ms)
        raise Exception("Bad lex: '%s'" % self._input)

# Inserts commas where consecutive lexemes of same type (simplifies range computation)
class CommaInsertedLexer(object):
    comma = set(["TIME","TERM","DAY"])
    
    def __init__(self,input):
        self._raw = RawLexer(input)
        self._saved = None
        self._last = None
    
    def pop(self):
        if self._saved:
            out = self._saved
            self._saved = None
            return out
        (type,value) = self._raw.pop()
        if self._last != None:
            if type == self._last and type in self.comma:
                self._saved = (type,value)
                return ("CHAR",",")
        self._last = type
        return (type,value)

class BufferingLexer(object):
    def __init__(self,input):
        self._lexer = CommaInsertedLexer(input)
        self._saved = None
        
    def peek(self):
        if self._saved != None:
            return self._saved
        else:
            self._saved = self._lexer.pop()
            return self._saved
        
    def pop(self):
        if self._saved != None:
            out = self._saved
            self._saved = None
            return out
        else:
            return self._lexer.pop()

    def popreq(self,t1):
        (t2,value) = self.pop()
        if t1 != t2:
            raise Exception("Expected %s, got %s (%s)" % (t1,t2,value))
        return (t2,value)

    def peek_is(self,type,value = None):
        (t,v) = self.peek()
        return t == type and (value is None or v == value)

    def attempt(self,type,value):
        p = self.peek_is(type,value)
        if p:
            self.pop()
        return p
