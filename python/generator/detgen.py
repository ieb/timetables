# Reads top.json and alice.json to generate a list of subjects. Reads pdfs.csv to find subjects with static links. Reads from pdn-src.csv and all
# the pdn-out*.json files. Reads in and processes all the direct source .csv files. Writes out details_*.csv. Runs -g on all triposes to generate
# calendar files.

datadir = "../../data"
srcdatadir = "../../source-data"
gentmpdir = "../../generate-tmp"

pdffile = 'pdfs.csv'

import os,sys

heredir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,heredir+"/../lib")
sys.path.insert(0,heredir+"/../indium")

import json,csv,random,subprocess,collections,copy
import indium,util,details
from fullpattern import FullPattern
import element
import csvverifier

os.chdir(os.path.dirname(sys.argv[0]))

top = json.load(file(datadir+'/top.json'))

# Find every single course so that we can at least put dummy data in for it.

alice = json.load(file(gentmpdir+'/subjects.json'))
triposes = top['years'][0]['triposes']
coursemap = collections.defaultdict(dict)
for tripos in triposes:
    for part in tripos['parts']:
        out = { 'id': part['id'],'courses': {} }
        modules = {}
        if part['id'] in alice:
            for (id,module) in alice[part['id']].iteritems(): 
                coursemap[part['id']][id] = module if module else "Entire course"
        else:
            cid = "%s000" % part['id']
            coursemap[part['id']][cid] = "Entire course"
#

tids = set()
cids = set()
names = {}
ids = collections.defaultdict(dict)
for year in top['years']:
    for tripos in year['triposes']:
        for part in tripos['parts']:
            tids.add(part['id'])
            names[part['id']] = part['name']
            cids |= set(coursemap[part['id']].iterkeys())
            for (k,v) in coursemap[part['id']].iteritems():
                names[k] = v
                ids[part['id']][v] = k

# Merge in explicit PDF data
pdfs = collections.defaultdict(list)
for row in csv.reader(file("%s/%s" % (datadir,"pdfs.csv"))):
    if len(row) < 4:
        continue
    (id,_,name,pdf) = row[0:4]
    pdfs[id].append({'pdf': pdf, 'name': name})
    print >>sys.stderr,"Using PDF for %s (%s)" % (id,name)
    if id in cids:
        cids.remove(id)
for (cid,datas) in pdfs.iteritems():
    if not cid in names:
        continue
    out = {
        'id': cid,
        'name': names[cid],
        'staticurls': []
    }        
    for data in datas:
        out['staticurls'].append(data['pdf'])
    c = open(datadir+"/details_%s.json" % cid,'wb')
    json.dump(out,c)
    c.close()        

# Merge in yseult data
for json_file in [x for x in os.listdir(gentmpdir) if x.endswith('.json') and x.startswith('yseult_')]:
    print "  file %s" % json_file
    data = json.load(file("%s/%s" % (gentmpdir,json_file)))
    id = json_file[len('yseult_'):-len('.json')]
    print >>sys.stderr,"Yseult file for %s" % id
    c = open("%s/details_%s.json" % (datadir,id),'wb')
    json.dump(data,c)
    c.close()
    cids.remove(id)
    
# Merge in pdn-originated data
pdn_idx = {}
for json_file in [x for x in os.listdir(gentmpdir) if x.endswith('.json') and x.startswith('pdnout-')]:
    data = json.load(file("%s/%s" % (gentmpdir,json_file)))
    (part,course) = data['id']
    pdn_idx[(part,course)] = data

for row in csv.reader(file(srcdatadir+'/pdn-src.csv')):
    if row[0] == 'ID' or len(row) < 4:
        continue
    (id,part,course,organiser) = row[0:4]
    if not id in cids:
        continue
    if (part,course) in pdn_idx:
        data = pdn_idx[(part,course)]
        print >>sys.stderr,"Using PDN source for %s %s" % (part,course)
        data['organiser'] = organiser
        data['id'] = id
        cids.remove(id)
        c = open("%s/details_%s.json" % (datadir,id),'wb')
        json.dump(data,c)
        c.close()

# XXX no mixed terms within pattern
termnames = ["Mi","Le","Ea"]
termfullnames=["Michaelmas","Lent","Easter"]

# Go through the spreadsheets one by one
newdir = srcdatadir+'/new-course-sheets'
for csv_file in [x for x in os.listdir(newdir) if x.endswith('.csv')]:
    print >>sys.stderr,"Reading %s" % csv_file
    ds = details.Details.from_csv(open("%s/%s" % (newdir,csv_file)),verifier = csvverifier.Verifier())
    if not ds.id in cids:
        print >>sys.stderr,"    already handled, skipping"
        continue
    cids.remove(ds.id)    
    c = open(datadir+"/details_%s.json" % ds.id,'wb')
    json.dump(ds.to_json(),c)
    c.close()

days = ['M','Tu','W','Th','F','Sa']

def fake_time():
    return random.choice(days)+str(random.randint(1,12))

# Fakes
for cid in cids:
    print >>sys.stderr,"MISSING %s" % cid
    ds = details.Details(cid,names[cid],"Example organiser","Example location",{"notes": "", "course-description": ""})    
    for term in ['Michaelmas','Lent','Easter']:
        for type in ['Lecture','Practical']:
            ds.addRow(element.Element("Example person",names[cid],"Example location",FullPattern(term[:2]+' '+fake_time()),False,type,names[cid]))
    c = open(datadir+"/details_%s.json" % cid,'wb')
    json.dump(ds.to_json(),c)
    c.close()

# Regnerate calendar entries
print >>sys.stderr,"Regenerating calendars"
for tid in tids:
    indium.execute([('-p',datadir),('-g',None)],[tid])
print >>sys.stderr,"done"
