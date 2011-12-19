
import os
import json
import csv
import filepaths
import httplib,re,time,urllib,sys,collections


class Pdns(object):
    events = []
    pdn_host = "www.pdn.cam.ac.uk"
    pdn_base = "/teaching/resources/timetabledb/htdocs/"
    pdn_query = "/teaching/resources/timetabledb/htdocs/index.php"
    main_re = re.compile(r'<table.*?id=Main.*?>(.*?)</table>',re.S)
    row_re = re.compile(r'</tr>')
    cell_re = re.compile(r'</t[dh]>')
    detag_re = re.compile(r'<.*?>')
    parts = {}
    names = collections.defaultdict(list)
    conn = None
    ucam_webauth = None
    sleepTime = 10

    def setSleep(self, sleepTime):
        self.sleepTime = float(sleepTime)

    def setUCamWebAuth(self, ucam_webauth):
        self.ucam_webauth = ucam_webauth

    def getParts(self):
        if not self.conn:
            self.conn = httplib.HTTPConnection(self.pdn_host)
        headers = {}
        if self.ucam_webauth:
            headers['Cookie'] = "Ucam-WebAuth-Session=%s" % self.ucam_webauth
        self.conn.request("GET",self.pdn_base,headers=headers)
        r1 = self.conn.getresponse()
        if r1.status == 302:
            raise Exception("Please go to http:/%s%s and login to capture webauth token" % (self.pdn_host,self.pdn_base))
        if r1.status != 200:
            raise Exception("Didn't get 200 getting http:/%s%s  %d" % (self.pdn_host,self.pdn_base, r1.status))
        base = unicode(r1.read(),"ISO-8859-1")

        # Find Module selector
        module_re = re.compile(r"<select.*?name='Module'.*?>(.*)</select>")
        m = module_re.search(base)
        if not m:
            raise Exception("Couldn't find dropdown")
        modules = m.group(1)

        # Split on optgroups
        parts = {}
        groups_re = re.compile('<optgroup.*?label=[\'"](.*?)[\'"](.*?)</optgroup>')
        def og(m):
            parts[m.group(1)] = m.group(2)
            return ''
        groups_re.sub(og,modules)
        self.parts = parts


    def getPart(self, part):
        # Get our optgroup and extract subjects XXX
        group = self.parts[part]
        subjects = {}
        if not group:
            raise Exception("Cannot find %s" % part)
        options_re = re.compile('<option.*?value=[\'"](.*?)[\'"].*?title=[\'"](.*?)[\'"].*?>')
        def os(m):
            subjects[m.group(1)] = m.group(2)
            return ''
        options_re.sub(os,group)

        # Iterate through subjects
        for (key,name) in subjects.iteritems():
            self.names[part].append(name)
            print "Retrieving '%s'" % name
            params = urllib.urlencode({'Location': 'All', 'Module': key, 'action': 'Whole Year', 'AcadYear': '11/12'})
            headers = {}
            headers = {"Content-type": "application/x-www-form-urlencoded" }
            if self.ucam_webauth:
                headers['Cookie'] = "Ucam-WebAuth-Session=%s" % self.ucam_webauth
            self.conn.request("POST",self.pdn_query,params,headers)
            r1 = self.conn.getresponse()
            if r1.status != 200:
                raise Exception("Didn't get 200 getting http:/%s/%s" % (self.pdn_host,self.pdn_base))
            data = unicode(r1.read(),"ISO-8859-1")
            self.process_subject(part,name,data)
            time.sleep(self.sleepTime)

    def dump(self, outputFile):
        # Output data in sensible format
        out = {
            'subjects': self.names,
            'events': self.events
        }
        json.dump(out,open(outputFile,'wb'))


    def add_lecture(self, part,what,subj,who,where,when_d,when_s,when_e):
        date_s = time.strftime("%Y-%m-%d %H:%M:%S",time.strptime("%s %s" % (when_d,when_s),"%d %b %y %H:%M"))
        date_e = time.strftime("%Y-%m-%d %H:%M:%S",time.strptime("%s %s" % (when_d,when_e),"%d %b %y %H:%M"))
        print "what=%s subj=%s who=%s where=%s date_s=%s date_e=%s" % (what,subj,who,where,date_s,date_e)
        self.events.append((part,what,subj,who,where,date_s,date_e))

    def process_subject(self,part,name,data):
        # Extract table
        m = self.main_re.search(data)
        if m == None:
            raise Exception("Cannot find main table in '%s'" % name)
        # split into rows
        rows = self.row_re.split(m.group(1))
        if len(rows) < 3:
            raise Exception("Bad table, too short for '%s'" % name)
        if len(rows) == 3:
            print >>sys.stderr,"WARN: Table contained no data for '%s'" % name
        rows = rows[2:-1]
        for row in rows:
            cells = self.cell_re.split(row)
            cells = [ self.detag_re.sub('',x) for x in cells ]
            self.add_lecture(part,cells[15],cells[20],cells[5],cells[14],cells[11],cells[12],cells[13])

    def merge(self, mergeState):
        # Merge in pdn-originated data
        if os.path.isfile(filepaths.pdnSrcFilePath):
            pdn_idx = {}
            for json_file in [x for x in os.listdir(filepaths.gentmpdir) if x.endswith('.json') and x.startswith('pdnout-')]:
                data = json.load(file("%s/%s" % (filepaths.gentmpdir,json_file)))
                (part,course) = data['id']
                pdn_idx[(part,course)] = data
            for row in csv.reader(file(filepaths.pdnSrcFilePath)):
                if row[0] == 'ID' or len(row) < 4:
                    continue
                (id,part,course,organiser) = row[0:4]
                if not id in mergeState.courseIds:
                    continue
                if (part,course) in pdn_idx:
                    data = pdn_idx[(part,course)]
                    print >>sys.stderr,"Using PDN source for %s %s" % (part,course)
                    data['organiser'] = organiser
                    data['id'] = id
                    filepaths.saveDetailFile(data,id)
                    mergeState.courseIds.remove(id)
        else:
            print "No PDN source files present (%s), skipping" % (filepaths.pdnSrcFilePath)
