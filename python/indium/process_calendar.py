import os,json,collections,copy

import patternatom,details,rectangle,process_details

from fullpattern import FullPattern
import element
import caldata
import course
import logging

def load_or_new_details(path,cid):
    det_fn = os.path.join(path,"details_%s.json" % cid)
    if os.path.exists(det_fn):
        return  details.Details.from_json(json.load(file(det_fn)))
    else:
        return rectangle.Rectangle.generate_new_details()

def update_details(path,cid,rs):
    logger = logging.getLogger('indium')
    changed = False
    for rv in rs:
        if rv.changedp():
            changed = True
            break
    if not changed:
        return
    logger.info("updating %s" % cid)
    old_det = load_or_new_details(path,cid)
    new_det = old_det.new_same_header()
    # Index values by eid and take copy as orig
    els = {}
    orig_els = {}
    for g in old_det.getGroups():
        for e in g.elements:
            id = e.eid(g.term) 
            els[id] = copy.deepcopy(e)
            orig_els[id] = e
    # Change values
    for rv in rs:
        # We need the orgi as only changes to rectangles should be propagated to the element to avoid the
        # risk of reversion if multiple rectangles map to an element and only early rectangles change.
        orig = orig_els[rv.key]
        new = els[rv.key]
        # what, where, who
        rv.update_to_element(new,orig)
        # did it move?
        if rv.saved_dt != rv.dt:
            # Remove the corresponding old daytimes for all patterns for this rectangle
            tws = []
            wout = FullPattern()
            for p in new.when.each():
                hit = p.removeDayTimeRangeDirect(rv.saved_dt)
                wout.addOne(p)
                if hit: # derive term/weeks from deleted patterns
                    tws.append(p)
            # Add in new daytime
            newp = patternatom.PatternAtom(False)
            newp.addDayTimeRangeDirect(rv.dt)
            for p in tws:
                newp.addTermWeeksFrom(p)
            wout.addOne(newp)
            new.when = wout
    # Populate based on changed values
    for (eid,e) in els.iteritems():
        new_det.addRow(element.Element(e.who,e.what,e.where,FullPattern(e.when),e.merge,e.type,new_det.name))
    if old_det.to_json(True) != new_det.to_json(True):
        print "  saving"
        det_fn = os.path.join(path,"details_%s.json" % cid)
        j = new_det.to_json() # outside open to allow exceptions
        c = open(det_fn,"wb")
        json.dump(j,c)
        c.close()
        return True
    else:
        logger.debug(" didn't seem to change")
        return False

def process_new_rectangle(path,caldata,r):
    print "New rectangle!"    
    # identify cid
    cid = None
    for c in caldata.courses.itervalues():
        if c['name'] == r['cname']:
            cid = c['id']
    if cid is None:
        raise Exception("Unknown course")
    c = course.Course(cid,r['cname'])
    # load relevant details file
    det = load_or_new_details(path,cid)
    # build element
    el = element.Element(r['organiser'],r['what'],r['where'],FullPattern(r['when']),False,r['type'],c)
    # add to groups
    for term in range(0,3):
        e = copy.deepcopy(el)
        if e.restrictToTerm(term):
            g = det.getGroup(r['type'],term)
            g.group.append(e)
    # save details
    det_fn = os.path.join(path,"details_%s.json" % cid)
    j = det.to_json()  # outside open to allow exceptions
    c = open(det_fn,"wb")
    json.dump(j,c)
    c.close()
    return cid

def process_calendar(path,id):
    logger = logging.getLogger('indium')    
    # Detect changs and news and farm off to relevant method
    cal_fn = os.path.join(path,"cal_%s.json" % id)
    cal = json.load(file(cal_fn))
    (cd,new) = caldata.CalData.from_json(cal)
    changed = set()
    for r in new:
        changed.add(process_new_rectangle(path,cd,r))    
    rs = cd.all_individual_rectangles()
    for (cid,rs) in cd.each_course_individual_rectangles():
        if len(rs):
            if update_details(path,cid,rs):
                changed.add(cid)
    # run corresponding details process to update calendar
    for cid in changed:
        logger.info("  regenerating %s" % cid)
        process_details.process_details(path,cid)
