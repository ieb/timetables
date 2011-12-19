#!/usr/bin/env python
# Use top.csv and idmap.csv to build a complete id map, appending new ids if necessary
#   Starting from source-data/top.csv in the form
#  <tripos>,<part>,<subject>,<url>
# generate or update
#   idmap.csv   <tripos>,<part>,<subject>,<id>
#   pdfs.csv <id>,'Entire Course','All Year',<pdf>,<tripos part subject>
#   top.json
#   subjects.json
# If idmap already exists, it is updated. Other files are re-generated.
#

import csv
import re
import os
import sys
import collections
import json
import filepaths

# read in top for anything new
if not os.path.isfile(filepaths.topFilePath):
    print "File %s is missing, this is needed to generate the top level ids and associated files, please create." % (filepaths.topFilePath)
    print "The file should be a csv file containing rows of the form  <tripos>,<part>,<subject>,<url> "
    print "Where tripos is not specified, the record takes the last tripos specified."
    sys.exit(-1)


year = 2011


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
if os.path.isfile(filepaths.idmapFilePath):
    idmapfile = open(filepaths.idmapFilePath,'r')
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


topfile =  csv.reader(open(filepaths.topFilePath,'r'))
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
    print "Assigning %s to new subject %s" % (newid, cleaned[row])
    ids[(tripos,part,subject)] = newid
    adds.append([cleaned[row][0],cleaned[row][2],cleaned[row][3],newid])

# read in source pdfs (and set to placeholder)
allpdfs = set()
if os.path.isfile(filepaths.pdfsFilePath):
    pdfsfile = open(filepaths.pdfsFilePath,"r")
    for row in csv.reader(pdfsfile):
        allpdfs.add(row[0])
    pdfsfile.close()

# read in data pdfs (and set to placeholder)
if os.path.isfile(filepaths.pdfsDataFilePath):
    pdfsfile = open(filepaths.pdfsDataFilePath,"r")
    for row in csv.reader(pdfsfile):
        allpdfs.add(row[0])
    pdfsfile.close()

pdfsfile = open(filepaths.pdfsDataFilePath,"w")
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
idmapfile = open(filepaths.idmapFilePath,'a')
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
    print "Updating key for Tripos %s" % (tripos)
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
out = open(filepaths.topJsonFilePath,'wb')
print >>out, json.dumps(top)
out.close()
out = open(filepaths.subjectsJsonFilePath,'wb')
print >>out, json.dumps(subjects)
out.close()

print "Script Complete ==============================="
print "Source data was %s " % (filepaths.topFilePath)
print "Updated %s" % (filepaths.idmapFilePath)
print "Updated %s" % (filepaths.pdfsDataFilePath)
print "Updated %s" % (filepaths.subjectsJsonFilePath)
print "Updated %s" % (filepaths.topFilePath)
print "Next generate some details json files using pdnfeed/pdngen, ygen, fakegen"
