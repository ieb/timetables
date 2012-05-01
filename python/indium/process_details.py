import sys,os,json

import course,rectangle,details
import caldata
import csvverifier
import year

# XXX hardwired
import datetime
# see http://www.cam.ac.uk/univ/termdates.html
#year = year.Year([datetime.date(2011,10,4),datetime.date(2012,1,17),datetime.date(2012,4,24)])
year = year.Year([datetime.date(2012,10,2),datetime.date(2013,1,15),datetime.date(2013,4,23)])
#year = year.Year([datetime.date(2013,10,8),datetime.date(2014,1,14),datetime.date(2014,4,22)])
#year = year.Year([datetime.date(2014,10,7),datetime.date(2015,1,13),datetime.date(2015,4,21)])
#year = year.Year([datetime.date(2015,10,6),datetime.date(2016,1,12),datetime.date(2016,4,19)])

def update_calendar(det_str,cal):
    c = course.Course(det_str['id'],det_str['name'])
    cal.refresh_course(c)
    if 'staticurls' in det_str:
        # static calendar
        cal.make_course_static(c,det_str['staticurls'])
    else:
        # generate new rectangles
        zoo = rectangle.RectangleZoo.zoo_from_details(c,details.Details.from_json(det_str))
        cal.replace_course_rectangles(c,zoo)
    
def process_details(path,id):
    # update calendar
    det_fn = os.path.join(path,"details_%s.json" % id)
    cal_fn = os.path.join(path,"cal_%s.json" % id[0:14])
    det_str = json.load(file(det_fn))
    if os.path.exists(cal_fn):
        (cal,_) = caldata.CalData.from_json(json.load(file(cal_fn)))
    else:
        cal = caldata.CalData(id[0:14])
    update_calendar(det_str,cal)
    j = cal.to_json()
    c = open(cal_fn,"wb")
    json.dump(j,c)
    c.close()
    # update details to include new hash and generate csv and alt files
    if not 'staticurls' in det_str:
        dt = details.Details.from_json(det_str)
        j = dt.to_json()
        c = open(det_fn,"wb")
        json.dump(j,c)
        c.close()
        dt.to_csv(open("%s/csv_%s.csv" % (path,id),"w"),False)
        dt.to_csv(open("%s/alt_%s.alt" % (path,id),"w"),True)
        c = open("%s/report_%s.html" % (path,id),"wb")
        print >>c,dt.to_report(year).encode('utf-8')
        c.close()
        c = open("%s/report_time_%s.html" % (path,id),"wb")
        print >>c,dt.to_report_time(year).encode('utf-8')
        c.close()
        c = open("%s/report_paper_%s.html" % (path,id),"wb")
        print >>c,dt.to_report(year,True).encode('utf-8')
        c.close()
        c = open("%s/student_%s.json" % (path,id),"wb")
        print >>c,dt.to_gcal(year).encode('utf-8')
        c.close()
        c = open("%s/student_%s.ical" % (path,id),"wb")
        print >>c,dt.to_ical(year).encode('utf-8')
        c.close()

def generate_calendar(path,id):
    # delete calendar
    cal_fn = os.path.join(path,"cal_%s.json" % id)
    try:
        os.unlink(cal_fn)
    except:
        pass
    # iterate through details files
    for file in filter(lambda x: x.startswith("details_"+id),os.listdir(path)):
        print "  processing %s" % file
        file = file[len("details_"):-len('.json')]
        process_details(path,file)

def process_all(path):
    # Build list of calendars based on details files
    cals = set()
    for file in filter(lambda x: x.startswith("details_"),os.listdir(path)):
        det = file[len("details_"):-len('.json')]
        cals.add(det[0:-3])
    for cal in cals:        
        print "Regenerating %s" % cal
        generate_calendar(path,cal)
    print "done"

def process_spreadsheet(path,id,alt = False):
    if alt:
        csv_fn = os.path.join(path,"alt_%s.alt" % id)
    else:
        csv_fn = os.path.join(path,"csv_%s.csv" % id)
    dt = details.Details.from_csv(open(csv_fn),id,alt,csvverifier.Verifier())
    det_fn = os.path.join(path,"details_%s.json" % id)
    j = dt.to_json()
    c = open(det_fn,"wb")
    json.dump(j,c)
    c.close()
    process_details(path,id) # Update calendar, etc, too!
