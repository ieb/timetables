'''
This file contains input methods classes, each input method should have a merge method to allow its data to be merged
into a details file. It should also change the mergestate for each course that it updates.
'''

import os,sys
import json,csv,random,subprocess,collections,copy
import util,details
from fullpattern import FullPattern
import element
import csvverifier
import filepaths
import inputmethods

'''
    Returns a list of input objects, in the order they should be processed.
'''
def inputObjects():
    return [
            StaticPdf(),
            Yseult(),
            Pdns(),
            Spreadsheet(),
            Fake()
            ]

class DetailsMergeState(object):
    courseIds = set()
    triposIds = set()
    names = {}
    
    def __init__(self, top, subjects):
        triposes = top['years'][0]['triposes']
        coursemap = collections.defaultdict(dict)
        for tripos in triposes:
            for part in tripos['parts']:
                out = { 'id': part['id'],'courses': {} }
                modules = {}
                if part['id'] in subjects:
                    for (id,module) in subjects[part['id']].iteritems(): 
                        coursemap[part['id']][id] = module if module else "Entire course"
                else:
                    cid = "%s000" % part['id']
                    coursemap[part['id']][cid] = "Entire course"
        #
        
        ids = collections.defaultdict(dict)
        for year in top['years']:
            for tripos in year['triposes']:
                for part in tripos['parts']:
                    self.triposIds.add(part['id'])
                    self.names[part['id']] = part['name']
                    self.courseIds |= set(coursemap[part['id']].iterkeys())
                    for (k,v) in coursemap[part['id']].iteritems():
                        self.names[k] = v
                        ids[part['id']][v] = k
    
    
    
class StaticPdf(object):
    def merge(self, mergeState):
        # Merge in explicit PDF data
        pdfs = collections.defaultdict(list)
        for row in csv.reader(file(filepaths.pdfsDataFilePath)):
            if len(row) < 4:
                continue
            (id,_,name,pdf) = row[0:4]
            pdfs[id].append({'pdf': pdf, 'name': name})
            print >>sys.stderr,"Using PDF for %s (%s)" % (id,name)
            if id in mergeState.courseIds:
                mergeState.courseIds.remove(id)
        for (cid,datas) in pdfs.iteritems():
            if not cid in mergeState.names:
                continue
            out = {
                'id': cid,
                'name': mergeState.names[cid],
                'staticurls': []
            }        
            for data in datas:
                out['staticurls'].append(data['pdf'])
            filepaths.saveDetailFile(out, cid)


class Yseult(object):
    def merge(self, mergeState):
        # Merge in yseult data
        for json_file in [x for x in os.listdir(filepaths.gentmpdir) if x.endswith('.json') and x.startswith('yseult_')]:
            print "  file %s" % json_file
            data = json.load(file("%s/%s" % (filepaths.gentmpdir,json_file)))
            id = json_file[len('yseult_'):-len('.json')]
            print >>sys.stderr,"Yseult file for %s" % id
            filepaths.saveDetailFile(data, id)
            mergeState.courseIds.remove(id)


class Pdns(object):
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


class Spreadsheet(object):
    def merge(self, mergeState):
        # Go through the spreadsheets one by one
        if os.path.isdir(filepaths.newCourseSheetDir):
            for csv_file in [x for x in os.listdir(filepaths.newCourseSheetDir) if x.endswith('.csv')]:
                print >>sys.stderr,"Reading %s" % csv_file
                ds = details.Details.from_csv(open("%s/%s" % (filepaths.newCourseSheetDir,csv_file)),verifier = csvverifier.Verifier())
                if not ds.id in courseIds:
                    print >>sys.stderr,"    already handled, skipping"
                    continue
                filepaths.saveDetailFile(ds.to_json(),ds.id)
                mergeState.courseIds.remove(ds.id)
        else:
            print "No manual new course sheet files in %s skipping" % (filepaths.newCourseSheetDir)

class Fake(object):
    days = ['M','Tu','W','Th','F','Sa']

    def fake_time(self):
        return random.choice(self.days)+str(random.randint(1,12))
    
    def merge(self, mergeState):
        # Fakes
        for cid in mergeState.courseIds:
            print >>sys.stderr,"MISSING %s" % cid
            ds = details.Details(cid,mergeState.names[cid],"Example organiser","Example location",{"notes": "", "course-description": ""})    
            for term in ['Michaelmas','Lent','Easter']:
                for type in ['Lecture','Practical']:
                    ds.addRow(element.Element("Example person",mergeState.names[cid],"Example location",FullPattern(term[:2]+' '+self.fake_time()),False,type,mergeState.names[cid]))
            filepaths.saveDetailFile(ds.to_json(),cid)
