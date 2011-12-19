#!/usr/bin/env python

import os,sys

heredir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,heredir+"/../lib")
sys.path.insert(0,heredir+"/../indium")

import json
import collections
import csv
import filepaths

if not os.path.isfile(filepaths.topJsonFilePath):
    print "No index of subjects please run topgen.py to generate before running this script "
    sys.exit(-1)

fakeGenFilePath = filepaths.gentmpdir+"/fake-src.csv"


top = json.load(file(filepaths.topJsonFilePath))

subjects = collections.defaultdict(set)
triposnames = {}



triposes = top['years'][0]['triposes']
ntripos = 0
nparts = 0
for tripos in triposes:
    ntripos = ntripos + 1
    for part in tripos['parts']:
        nparts = nparts + 1
        (tripos_name,part_name,part_id) = (tripos['name'],part['name'],part['id'])
        triposnames[part_id] = "%s %s" % (tripos_name,part_name)
        n = 0
        for f in filter(lambda x: x.startswith(filepaths.detailsPrefix+part_id),os.listdir(filepaths.datadir)):
            n = n + 1
            details = json.load(file(filepaths.datadir+"/"+f))
            subject = details['name']            
            subjects[part_id].add(subject)
if len(subjects) == 0:
    print "Found %s tripos, containing %s parts, but no details files found, have you generated any details file in %s/%s*.json  " % ( ntripos, nparts, filepaths.datadir,filepaths.detailsPrefix)
    sys.exit(-1)

print "Found %s tripos, containing %s parts, generating for %d subjects in %s  " % ( ntripos, nparts, len(subjects), fakeGenFilePath)

out = csv.writer(open(fakeGenFilePath,"wb"))
for (tripos_id,subjects) in subjects.iteritems():
    for subject in subjects:
        for term in ('Michaelmas','Lent','Easter'):
            out.writerow([tripos_id,subject,term,'',triposnames[tripos_id]])
            