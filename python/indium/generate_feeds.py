import os
import json

import ical
import gcal
import details
import year
import student

# XXX hardwired
import datetime
year = year.Year([datetime.date(2011,10,4),datetime.date(2012,1,17),datetime.date(2012,4,24)])

def generate_feeds(path,args,alt = False):
    if alt:
        src = gcal.GCal()
    else:
        src = ical.ICal()
    s = student.Student(year,src)
    all = ",".join(args)
    for section in all.split(","):
        id = section.strip()
        det_fn = os.path.join(path,"details_%s.json" % id)
        det_str = json.load(file(det_fn))
        if not 'staticurls' in det_str:
            dt = details.Details.from_json(det_str)
            s.add(dt)
    print s.generate().encode('utf-8')