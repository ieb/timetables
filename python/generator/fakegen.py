import os,sys

heredir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,heredir+"/../lib")
sys.path.insert(0,heredir+"/../indium")

import json
import collections
import csv

datadir = "../../data"
gentmpdir = "../../generate-tmp"

top = json.load(file(datadir+'/top.json'))

subjects = collections.defaultdict(set)
triposnames = {}

triposes = top['years'][0]['triposes']
for tripos in triposes:
    for part in tripos['parts']:
        (tripos_name,part_name,part_id) = (tripos['name'],part['name'],part['id'])
        triposnames[part_id] = "%s %s" % (tripos_name,part_name)
        for f in filter(lambda x: x.startswith("details_"+part_id),os.listdir(datadir)):
            details = json.load(file(datadir+"/"+f))
            subject = details['name']            
            subjects[part_id].add(subject)
            
out = csv.writer(open(gentmpdir+"/fake-src.csv","wb"))
for (tripos_id,subjects) in subjects.iteritems():
    for subject in subjects:
        for term in ('Michaelmas','Lent','Easter'):
            out.writerow([tripos_id,subject,term,'',triposnames[tripos_id]])
            