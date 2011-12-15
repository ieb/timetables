# Use top.csv and idmap.csv to build a complete id map, appending new ids if necessary

datadir = "../../data"
srcdatadir = "../../source-data"
gentmpdir = "../../generate-tmp"

year = 2011

import csv
import re
import collections
import json

spaces_re = re.compile(r'\s+')
punc_re = re.compile(r'[^A-Za-z0-9 ]')

def clean(data):
    return punc_re.sub('',spaces_re.sub(' ',data.strip().upper()))

# read in existing id map
tripos_prefixes = {}
part_prefixes = {}
max_tripos = 0
max_part = 0
max_subj = collections.defaultdict(lambda: 0)
ids = {}
idmapfile = open(srcdatadir+'/idmap.csv','r')
idmap = csv.reader(idmapfile)
for row in idmap:
    (tripos,part,subject,id) = map(lambda x: clean(x),row)
    tripos_prefixes[tripos] = id[1:5]
    max_tripos = max(max_tripos,int(id[1:5]))
    part_prefixes[(tripos,part)] = id[5:10]
    max_part = max(max_part,int(id[5:10]))
    max_subj[(tripos,part)] = max(max_subj[(tripos,part)],int(id[14:]))
    ids[(tripos,part,subject)] = id
idmapfile.close()

# read in top for anything new
topfile =  csv.reader(open(srcdatadir+'/top.csv','r'))
subjects = set()
nosubj = {}
cleanrun = ['','','','']
running = ['','','','']
cleaned = []
statics = {}

for (idx,row) in enumerate(topfile):
    for (i,data) in enumerate(row[0:4]):
        if clean(data):
            running[i] = clean(data)
            cleanrun[i] = data
            for j in range(i+1,len(running)):
                running[j] = ''        
                cleanrun[j] = ''
    cleaned.append(cleanrun[:])
    if row[2]:
        nosubj[(running[0],running[2])] = idx
    if row[3]:
        if (running[0],running[2]) in nosubj:
            del nosubj[(running[0],running[2])]
        subjects.add((running[0],running[2],running[3],idx))
    if len(row) > 4 and row[4].strip():
        statics[(running[0],running[2],running[3])] = row[4]

for ((tripos,part),idx) in nosubj.iteritems():
    subjects.add((tripos,part,'',idx))

adds = []
rowidx = {}
# create ids for new subjects and, for all subjects, remember row for clean data later
for (tripos,part,subject,row) in subjects:
    rowidx[(tripos,part,subject)] = row
    if (tripos,part,subject) in ids:
        continue
    print "New subject %s" % cleaned[row]
    # Find a tripos match, if possible
    if not tripos in tripos_prefixes:
        max_tripos += 1
        tripos_prefixes[tripos] = str(max_tripos)
    tid = int(tripos_prefixes[tripos])
    # ditto part
    if not (tripos,part) in part_prefixes:
        max_part += 1
        part_prefixes[(tripos,part)] = str(max_part)
    pid = int(part_prefixes[(tripos,part)])
    if not (tripos,part) in max_subj:
        max_subj[(tripos,part)] = 0
    max_subj[(tripos,part)] += 1
    sid = max_subj[(tripos,part)]
    newid = "T%04.4d%05.5d%4.4d%3.3d" % (tid,pid,year,sid)
    print "  assigning %s" % newid
    ids[(tripos,part,subject)] = newid
    adds.append([cleaned[row][0],cleaned[row][2],cleaned[row][3],newid])

# read in pdfs (and set to placeholder)
pdfsfile = open(srcdatadir+"/pdfs.csv","r")
allpdfs = set()
for row in csv.reader(pdfsfile):
    allpdfs.add(row[0])
pdfsfile.close()

pdfsfile = open(srcdatadir+"/pdfs.csv","w")
pdfs = csv.writer(pdfsfile)
for ((tripos,part,subject),pdf) in statics.iteritems():
    id = ids[(tripos,part,subject)]
    pdfs.writerow([id,'Entire Course','All Year',pdf," ".join([tripos,part,subject])])
    #print "Static URL for '%s' '%s' '%s' (%s) is %s" % (tripos,part,subject,id,pdf)
    if id in allpdfs:
        allpdfs.remove(id)
for pdf in allpdfs:
    pdfs.writerow([pdf,'Entire Course','All Year','http://timetables.caret.cam.ac.uk/none-yet.pdf','Not specified'])
        
pdfsfile.close()

# write updated idmap file (in a sensible order)
idmapfile = open(srcdatadir+'/idmap.csv','a')
idmap = csv.writer(idmapfile)
for row in adds:
    idmap.writerow(row)
idmapfile.close()

# build tiered structure
data = collections.defaultdict(lambda: collections.defaultdict(dict))

for (tripos,part,subject,row) in subjects:
    data[tripos][part][subject] = ids[(tripos,part,subject)]

subjects = collections.defaultdict(dict)
top = {}
# create json-candidate for top.json and subjects.json
triposes_data = []
for tripos in sorted(data.keys()):
    print "%s -> %s" % (tripos,data[tripos])
    parts_data = []
    for part in sorted(data[tripos].keys()):
        for subject in sorted(data[tripos][part].keys()):
            id = ids[(tripos,part,subject)]
            if not (tripos,part,subject) in rowidx:
                continue
            row = rowidx[(tripos,part,subject)]
            subjects[id[0:14]][id] = cleaned[row][3]
            part_data = { 'name': cleaned[row][2], 'id': id[0:14]}
        parts_data.append(part_data)
    triposes_data.append({ 'parts': parts_data, 'name': cleaned[row][0] })
top = { 'years': [{ "name": "2011/12", 'triposes': triposes_data }] }

# save top.json and subjects.json
out = open(datadir+'/top.json','wb')
print >>out, json.dumps(top)
out.close()
out = open(gentmpdir+'/subjects.json','wb')
print >>out, json.dumps(subjects)
out.close()
