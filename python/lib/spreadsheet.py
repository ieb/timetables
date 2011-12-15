import altfmt
import re
import cgi

lines_re = re.compile(r"<[Pp].*?>")
del_re = re.compile(r"</[Pp].*?>")

class SpreadsheetWriter:
    def __init__(self,writer,alt,metadata):
        self._alt = alt
        self._writer = writer
        self._metadata = {}
        for k in metadata:
            self._metadata[k] = lines_re.split(del_re.sub('',metadata[k]))
        self._row_count = 0

    def _write_unicode(self,data):
        self._writer.writerow([x.encode('utf-8') for x in data])

    def writehead(self,id,name,who,where):
        if self._alt:
            print >>self._writer,altfmt.write((("id",id),("name",name),("org",who),("location",where)))
            for k in sorted(self._metadata.keys()):
                for v in self._metadata[k]:
                    print >>self._writer,altfmt.write([('metadata',k),('value',v)])
        else:
            self._write_unicode([id,name,who,where])
            self._write_unicode([])
            headings = ['Course','Type','Organiser','Subject','Pattern','Where','Merge','']
            for k in sorted(self._metadata.keys()):
                headings.append(k)
            self._write_unicode(headings)

    def writerow(self,course,type,who,what,when,where,merge):
        if self._alt:
            print >>self._writer,altfmt.write((('course',course),('type',type),('who',who),('what',what),('when',str(when)),('where',where),('merge',"yes" if merge else "no")))
        else:
            row = [course,type,who,what,str(when),where,"yes" if merge else "no",'']
            for k in sorted(self._metadata.keys()):
                if len(self._metadata[k]) > self._row_count:
                    text = self._metadata[k][self._row_count]
                else:
                    text = ''
                row.append(text)
            self._row_count += 1
            self._write_unicode(row)

class SpreadsheetReader:
    def __init__(self,reader,alt):
        self._alt = alt
        self._reader = reader
        self._metadata = {}
        self._mk = []
    
    def _to_key(self,kss):
        return kss.strip().lower().replace(' ','-')
    
    def readhead(self):
        if self._alt:
            out = altfmt.read(("id","name","org","location"),self._reader.next())
        else:
            out = self._reader.next()[0:4]
            self._reader.next()
            for kss in self._reader.next()[8:]:
                k = self._to_key(kss)
                self._mk.append(k)
                self._metadata[k] = []          
        return out

    def readrow(self,row):
        if self._alt:
            md = altfmt.read(('metadata','value'),row,False)
            if md is not None:
                if md[0] not in self._metadata:
                    self._metadata[md[0]] = []
                self._metadata[md[0]].append(md[1])
                return None
            row = altfmt.read(('course','type','who','what','when','where','merge'),row)
        out = row[0:7]
        if len(row) > 8:
            for (i,md) in enumerate(row[8:]):
                self._metadata[self._mk[i]].append(md)        
        self._first = False
        return out

    # only works once whole spreadsheet has been read
    def get_metadata_after(self):
        out = {}
        for (k,v) in self._metadata.iteritems():
            out[k] = "<p>"+"</p><p>".join(v)+"</p>"
        return out
