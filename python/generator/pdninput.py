
import os
import json
import csv
import filepaths
import details
import element
import httplib,re,time,urllib,sys,collections,datetime,util
from fullpattern import FullPattern
import codecs

term_names = ["Mi","Le","Ea"]
day_names = ["M","Tu","W","Th","F","Sa","Su"]
terms_full = ['Michaelmas','Lent','Easter']

# see http://www.cam.ac.uk/univ/termdates.html
# term_start = [datetime.date(2011,10,4), datetime.date(2012,1,17), datetime.date(2012,4,24), datetime.date(2012,9,30) ] # last element is end of year 
term_start = [datetime.date(2012,10,2),datetime.date(2013,1,15),datetime.date(2013,4,23), datetime.date(2012,9,30) ]
#term_start = [datetime.date(2013,10,8),datetime.date(2014,1,14),datetime.date(2014,4,22), datetime.date(2012,9,30) ]
#term_start = [datetime.date(2014,10,7),datetime.date(2015,1,13),datetime.date(2015,4,21), datetime.date(2012,9,30) ]
#term_start = [datetime.date(2015,10,6),datetime.date(2016,1,12),datetime.date(2016,4,19), datetime.date(2012,9,30) ]


PDN_HOST = "www.pdn.cam.ac.uk"
PDN_BASE = "/teaching/resources/timetabledb/htdocs/"
PDN_QUERY = "/teaching/resources/timetabledb/htdocs/index.php"


class Pdns(object):
    events = []
    main_re = re.compile(r'<table.*?id=Main.*?>(.*?)</table>',re.S)
    row_re = re.compile(r'</tr>')
    cell_re = re.compile(r'</t[dh]>')
    detag_re = re.compile(r'<.*?>')
    name_prune_re = re.compile(r";(.*)$")
    punc_re = re.compile(r"[^A-Za-z0-9\s]")
    multispaces_re = re.compile(r"\s+")
    xofy_re = re.compile(r"\(\d\s+of\s+\d\)")
    spaces_re = re.compile(r"\s")
    pdnfile_re = re.compile(r"^pdnout-[0-9]+.json$")
    pdnFeed = {}
    parts = {}
    names = collections.defaultdict(list)
    conn = None
    ucam_webauth = None
    sleepTime = 10
    type_file = []


    def setSleep(self, sleepTime):
        self.sleepTime = float(sleepTime)

    def setUCamWebAuth(self, ucam_webauth):
        self.ucam_webauth = ucam_webauth

    def getParts(self):
        if not self.conn:
            self.conn = httplib.HTTPConnection(PDN_HOST)
        headers = {}
        if self.ucam_webauth:
            headers['Cookie'] = "Ucam-WebAuth-Session=%s" % self.ucam_webauth
        self.conn.request("GET",PDN_BASE,headers=headers)
        r1 = self.conn.getresponse()
        if r1.status == 302:
            raise Exception("Please go to http:/%s%s and login to capture webauth token" % (PDN_HOST,PDN_BASE))
        if r1.status != 200:
            raise Exception("Didn't get 200 getting http:/%s%s  %d" % (PDN_HOST,PDN_BASE, r1.status))
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
            self.conn.request("POST",PDN_QUERY,params,headers)
            r1 = self.conn.getresponse()
            if r1.status != 200:
                raise Exception("Didn't get 200 getting http:/%s/%s" % (PDN_HOST,PDN_BASE))
            data = unicode(r1.read(),"ISO-8859-1")
            self.process_subject(part,name,data)
            time.sleep(self.sleepTime)

    def dumpFeed(self, outputFile):
        # Output data in sensible format
        self.pdnFeed = {
            'subjects': self.names,
            'events': self.events
        }
        json.dump(self.pdnFeed,open(outputFile,'wb'))

    def saveFeed(self, outputFile):
        # Output data in sensible format
        self.pdnFeed = {
            'subjects': self.names,
            'events': self.events
        }

    def loadFeed(self, inputFile):
        self.pdnFeed = json.load(open(inputFile))

    def deleteSubjects(self, location):
        for old in filter(lambda x: self.pdnfile_re.match(x) != None,os.listdir(location)):
            os.unlink("%s/%s" % (location,old))

    def extractSubjects(self, location):
        # Separate into subjects
        i = 0
        for (part,subjects) in self.pdnFeed['subjects'].iteritems():
            for subject in subjects:
                print "Part '%s' Subject '%s'" % (part,subject)
                lectures = []
                for (part_c,subj_c,what,who,where,start,end) in self.pdnFeed['events']:
                    what = self.spaces_re.sub(' ',self.xofy_re.sub('',what)).strip()
                    if part == part_c and subject == subj_c:
                        lectures.append((what,who,where,start,end))
                ds = self.build_details(part,subject,lectures)
                json_str = self.build_json(part,subject,ds)
                c = open("%s/pdnout-%4.4d.json" % (location,i),"wb")
                json.dump(json_str,c)
                c.close()
                i += 1
        return i

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


    ''' Generating '''
    def loadLectLab(self):
        for row in csv.reader(file(filepaths.srcdatadir+'/lect-lab.csv')):
            if len(row) < 4 or row[3] == 'Type':
                continue
            self.type_file.append([x.strip() for x in row[0:4]])

    ''' What is the type based on where and duration '''
    def what_type(self, where,duration):
        if len(self.type_file) == 0:
            self.loadLectLab()
        for (regexp,min,max,type) in self.type_file:
            if regexp != '' and not re.search(regexp,where):
                continue
            if min != '' and float(duration) < float(min):
                continue
            if max != '' and float(duration) > float(max):
                continue
            return type

    def convert_times(self, start_s,end_s):
        start = datetime.datetime.strptime(start_s,"%Y-%m-%d %H:%M:%S")
        end = datetime.datetime.strptime(end_s,"%Y-%m-%d %H:%M:%S")
        # convert start/end to a duration
        delta = end - start
        if delta.days > 0:
            raise Exception("Start and end on different days!")
        duration = int(delta.seconds / 60)
        # separate day from time
        date = start.date()
        time = start.time()
        # calculate term
        term = None
        for ti in range(0,3):
            if date >= term_start[ti] and date < term_start[ti+1]:
                term = ti
        if term == None:
            raise Exception("Event outside any term at %s" % date)
        # calculate week within term
        term_start_thu = term_start[term] + datetime.timedelta(2)
        days_after = (date - term_start_thu).days
        return (term,days_after/7+1,(days_after+3)%7,time,duration)



    def build_days(self,days,timestr):
        # merge days by term/week
        inweek = collections.defaultdict(set)
        for (term,week,day) in days:
            inweek[(term,week)].add(day_names[day])
        # flip the map around so index is by day set
        outweek = collections.defaultdict(set)
        for ((term,week),days) in inweek.iteritems():
            daystr = "".join(sorted(list(days),reverse=True))
            outweek[daystr].add((term,week))
        # For each day combination build term/week specs
        twout = collections.defaultdict(str)
        for (daystr,termweeks) in outweek.iteritems():
            for term in range(0,3):
                weeks = set()
                for (term2,week) in termweeks:
                    if term == term2:
                        weeks.add(week)
                if len(weeks):
                    week_str = util.number_range_text(weeks)
                    twout[int(term)*100+int(min(weeks))] += "%s%s %s" % (term_names[term],week_str,daystr)
        out = FullPattern()
        for k in sorted(twout.keys()):
            out.addOne("%s%s" % (twout[k],timestr))
        return out

    # 8 is am, 7 is pm
    def build_time(self, when):
        if when.hour > 12 and when.hour < 20:
            out = str(when.hour-12)
        elif when.hour < 13 and when.hour > 7:
            out = str(when.hour)
        else:
            out = "%s!" % str(when.hour)
        if when.minute != 0:
            out += ":%2.2d" % when.minute
        return out

    def build_duration(self, time,duration):
        out = self.build_time(time)
        if duration != 60:
            # arithmetic not supported on time objects, :(.
            d = ( time.hour * 60 + time.minute ) + duration
            end = datetime.time(d/60,d%60)
            end = self.build_time(end)
            out = "%s-%s" % (out,end)
        return out

    def collapse_name(self,data):
        data = self.punc_re.sub(' ',data)
        data = self.multispaces_re.sub(' ',data).lower()
        return data

    def build_details(self,part,subject,lectures):
        # convert dates to term/week/day format and store merged based on who, where, time, duration
        data = collections.defaultdict(list)
        names = collections.defaultdict(list)
        for (what,who,where,start,end) in lectures:
            name = self.collapse_name(what)
            if what.strip() == '':
                continue
            (term,week,day,time,duration) = self.convert_times(start,end)
            names[name] = what
            data[(term,name,who,where,time,duration)].append((term,week,day))
        out = []
        for ((term,name,who,where,time,duration),days) in data.iteritems():
            timestr = self.build_duration(time,duration)
            dayp = self.build_days(days,timestr)
            type = self.what_type(where,duration)
            who = self.name_prune_re.sub(' et al.',who)
            out.append((term,names[name],who,where,dayp,type))
        return out



    def build_json(self, part,subject,dets):
        # What groups do we have?
        ds = details.Details([part,subject],subject,"Various","Various",{"notes": "", "course-description": ""})
        # Add elements
        for (_term,what,who,where,pattern,type) in dets:
            ds.addRow(element.Element(who,what,where,pattern,True,type,subject))
        # Outer wrapper
        return ds.to_json()


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
