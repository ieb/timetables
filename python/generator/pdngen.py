# From the data feed generate some details. Separated from pdn-feed.py to allow iteration in this code without refetch.
# Reads in lect-lab.csv and pdn-feed.json and generates lots of pdnout-*.json

import os,sys

heredir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,heredir+"/../lib")

import json,datetime,collections,util,csv,re

from fullpattern import FullPattern
import details
import element

srcdatadir = "../../source-data"
gentmpdir = "../../generate-tmp"

os.chdir(os.path.dirname(sys.argv[0]))

# XXX hardwired term dates
# These are the Tuesdays!

#term_start = [
#              datetime.date(2010,10,5),
#              datetime.date(2011,1,18),
#              datetime.date(2011,4,26),
#              datetime.date(2011,9,30) # end of year
#]
term_start = [
              datetime.date(2011,10,4),
              datetime.date(2012,1,17),
              datetime.date(2012,4,24),
              datetime.date(2012,9,30) # end of year
]

# Read in types to help disambiguate lectures from labs
type_file = []
for row in csv.reader(file(srcdatadir+'/lect-lab.csv')):
    if len(row) < 4 or row[3] == 'Type':
        continue
    type_file.append([x.strip() for x in row[0:4]])

def what_type(where,duration):
    for (regexp,min,max,type) in type_file:
        if regexp != '' and not re.search(regexp,where):
            continue
        if min != '' and float(duration) < float(min):
            continue
        if max != '' and float(duration) > float(max):
            continue
        return type

# Biggest task is reaggregation.

def convert_times(start_s,end_s):
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

term_names = ["Mi","Le","Ea"]
day_names = ["M","Tu","W","Th","F","Sa","Su"]

def build_days(days,timestr):
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

name_prune_re = re.compile(r";(.*)$")

# 8 is am, 7 is pm
def build_time(when):
    if when.hour > 12 and when.hour < 20:
        out = str(when.hour-12)
    elif when.hour < 13 and when.hour > 7:
        out = str(when.hour)
    else:
        out = "%s!" % str(when.hour)
    if when.minute != 0:
        out += ":%2.2d" % when.minute
    return out

def build_duration(time,duration):
    out = build_time(time)
    if duration != 60:
        # arithmetic not supported on time objects, :(.
        d = ( time.hour * 60 + time.minute ) + duration
        end = datetime.time(d/60,d%60)
        end = build_time(end)
        out = "%s-%s" % (out,end)
    return out

punc_re = re.compile(r"[^A-Za-z0-9\s]")
multispaces_re = re.compile(r"\s+")

def collapse_name(data):
    data = punc_re.sub(' ',data)
    data = multispaces_re.sub(' ',data).lower()
    return data

def build_details(part,subject,lectures):
    # convert dates to term/week/day format and store merged based on who, where, time, duration
    data = collections.defaultdict(list)
    names = collections.defaultdict(list)
    for (what,who,where,start,end) in lectures:
        name = collapse_name(what)
        if what.strip() == '':
            continue
        (term,week,day,time,duration) = convert_times(start,end)
        names[name] = what
        data[(term,name,who,where,time,duration)].append((term,week,day))
    out = []
    for ((term,name,who,where,time,duration),days) in data.iteritems():
        timestr = build_duration(time,duration)
        dayp = build_days(days,timestr)
        type = what_type(where,duration)
        who = name_prune_re.sub(' et al.',who)
        out.append((term,names[name],who,where,dayp,type))
    return out

terms_full = ['Michaelmas','Lent','Easter']

def build_json(part,subject,dets):
    # What groups do we have?
    ds = details.Details([part,subject],subject,"Various","Various",{"notes": "", "course-description": ""})
    # Add elements
    for (_term,what,who,where,pattern,type) in dets:        
        ds.addRow(element.Element(who,what,where,pattern,True,type,subject))
    # Outer wrapper
    return ds.to_json()

xofy_re = re.compile(r"\(\d\s+of\s+\d\)")
spaces_re = re.compile(r"\s")

pdn = json.load(open(gentmpdir+'/pdn-feed.json'))
i = 0

# Remove old PDN files
pdnfile_re = re.compile(r"^pdnout-[0-9]+.json$")
for old in filter(lambda x: pdnfile_re.match(x) != None,os.listdir(gentmpdir)):
    os.unlink("%s/%s" % (gentmpdir,old))

# Separate into subjects
for (part,subjects) in pdn['subjects'].iteritems():
    for subject in subjects:
        print "Part '%s' Subject '%s'" % (part,subject)
        lectures = []
        for (part_c,subj_c,what,who,where,start,end) in pdn['events']:
            what = spaces_re.sub(' ',xofy_re.sub('',what)).strip()
            if part == part_c and subject == subj_c:
                lectures.append((what,who,where,start,end))
        ds = build_details(part,subject,lectures)
        json_str = build_json(part,subject,ds)
        c = open("%s/pdnout-%4.4d.json" % (gentmpdir,i),"wb")
        json.dump(json_str,c)
        c.close()
        i += 1
