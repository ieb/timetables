import logging
import codecs
datadir = "../../data"
srcdatadir = "../../source-data"
gentmpdir = "../../generate-tmp"

import os,sys

heredir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,heredir+"/../lib")

import csv
import re
import json
import collections

import element
import fullpattern
import details

space_re = re.compile(r'\s+')
hourtail_re = re.compile(r':00')
and_re = re.compile(r'and')
weeksep_re = re.compile(r'[Ww]eeks?\s+([\d,\s]+(?:\s*(?:-|and)\s*\d+)?)(?:\s+only)?[\:\)]')
lecturer_re = re.compile(r'(Dr|Mr|Mrs|Ms|Miss|Prof(essor)?)\.?\s+(\w[\.?\s-]+)*(\w\.?\s+)[\w-]*\w',re.U)
interlectjunk_re = re.compile(r'(Group \w\W?\s+)?\a(\s*(and|[,/])\s*\a)?')
isolatedpunc_re = re.compile(r'(^|\s+)[^\w\s-](\s+|$)',re.U)
trailpunc_re = re.compile(r'\s+[^,]\s*$')
recomma_re = re.compile(r'(\d)\s+(\d)')
decomma_re = re.compile(r',\s+,')

# True means cross-course lecture
subjname_map = {
    'faculty': True,
    'mml': True,
    'all languages': True,
    'all langs': True,
    'comparative': 'Comparative Studies'
}

# Once you have generated a new data/idmap.csv for the year, look in that file to find the top level
# MML lecture IDS and add them here. All IDS in Part IA start with the IA value and so forth.
# This changes every year and if any records are added to the master mapping.
mml = {
    'IA': 'T0002000112012',
    'IB': 'T0002000022012',
    'II': 'T0002000032012',
    'LingI': 'T0002000862012',
    'LingII': 'T0002001062012'
}


days = {
    'Monday': 'M',
    'Tuesday': 'Tu',
    'Wednesday': 'W',
    'Thursday': 'Th',
    'Friday': 'F'
}

# skip these as they're special (extrenal courses, etc)
# "Modern & Medieval Languages (including Linguistics)","MML Part II","Linguistics",
# "Modern & Medieval Languages (including Linguistics)","MML Part IB","Linguistics",
skips = set(['T0002000022012005','T0002000032012010'])

# Load MML subject data
subjects = json.load(open(gentmpdir+'/subjects.json'))

mml_subjs = dict([(k,subjects[mml[k]]) for k,v in mml.iteritems()])

rev_mml_subjs = {}
for (a,b) in mml_subjs.iteritems():
    rev_mml_subjs[a] =  dict([(v, k) for k, v in b.iteritems()])

# output data built in these XXX should be a class or something
detail_objs = {}

def get_details(part,code):
    if not code in detail_objs:
        print "Making details for %s" % (code)
        detail_objs[code] = details.Details(code,mml_subjs[part][code],"Yseult Jay","Various",{ 'head': '', 'foot': ''})
    return detail_objs[code]

def add_event(part,when,code,what,who):
    dt = get_details(part,code)
    dt.addRow(element.Element(who,what,"See faculty notices",fullpattern.FullPattern(when),True,'Lecture',mml_subjs[part][code]))

def process_lecturer(lecturers,new):
    lecturers.append("%s [none]" % new.group(0))
    return '\a'

def process_event_internal(part,tw,when,subject,det1,det2):
    # extract lecturers
    lecturers = []
    det2 = lecturer_re.sub(lambda x: process_lecturer(lecturers,x),unicode(det2,'utf-8','replace'))    
    det2 = interlectjunk_re.sub('',det2)
    det2 = isolatedpunc_re.sub(' ',det2)
    det2 = trailpunc_re.sub('.',det2)
    det2 = space_re.sub(' ',det2)
    lecturers = ", ".join(lecturers)
    add_event(part,"%s %s" % (tw,when),subject,"%s %s" % (det1,det2),lecturers)

def fix_week_list(data):
    data = recomma_re.sub(r'\1,\2',data)
    data = decomma_re.sub(',',data)
    return data

def process_event(part,term,day,time,subject,det1,det2):
    if not det1.strip() and not det2.strip():
        return
    term = ['Mi','Le','Ea'][term]
    day = days[day.strip()]
    time = hourtail_re.sub('',time)
    try:
        t = int(time)
        if t>12:
            t -= 12
        time = str(t)
    except:
        pass
    det1 = space_re.sub(' ',det1)
    det2 = space_re.sub(' ',det2)
    #
    subject = subject.strip()
    if subject.lower() in subjname_map:
        subject = subjname_map[subject.lower()]
    if subject == True:
        subjects = set(mml_subjs[part].keys())  
    elif subject in rev_mml_subjs[part]:
        subjects = set([rev_mml_subjs[part][subject]])
    else:
        raise Exception("Unknown course '%s'" % subject)
    # extract week patterns from details strings
    pw_dets = weeksep_re.split(det2)
    det2s = []
    if len(pw_dets) > 1:
        # Was split
        for i in range(0,(len(pw_dets)-1)/2):
            det2s.append((fix_week_list(pw_dets[i*2+1]),pw_dets[i*2+2]))
    else:
        # check in det1 for restrictor
        m = weeksep_re.search(det1)
        if m:
            det2s.append((fix_week_list(m.group(1)),det2))
        else:
            det2s.append(('1-8',det2))
    for (week,d2) in det2s:
        w = and_re.sub(',',week)
        for s in subjects:
            process_event_internal(part,term+w,day+time,s,det1,d2)

path = "%s/yseult" % (srcdatadir,)

for part in mml.iterkeys():
    for csvfile in filter(lambda x: x.startswith(part+'-'),os.listdir(path)):
        print "Using file %s" % csvfile
        reader = csv.reader(open("%s/yseult/%s" % (srcdatadir,csvfile)))
        reader.next()
        for row in reader:
            process_event(part,0,row[0],row[1],row[2],row[3],row[4])
            process_event(part,1,row[0],row[1],row[2],row[5],row[6])
            process_event(part,2,row[0],row[1],row[2],row[7],row[8])
    for (key,dt) in detail_objs.iteritems():
        if key in skips:
            continue
        out = open("%s/yseult_%s.json" % (gentmpdir,key),"w")
        print "Writing %s" % key
        print >>out,json.dumps(dt.to_json())
        out.close()
