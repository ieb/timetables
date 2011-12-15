import sys
import pytz
import datetime
import icalendar

uk = pytz.timezone('Europe/London') # London will do, at a push, as a Cambridge substitute! :-)

def _s2t(t):
    global uk
    v = datetime.datetime.strptime(t,"%Y-%m-%dT%H:%M:%SZ")
    v = uk.localize(v)
    v = v.astimezone(pytz.utc)
    return v

class ICal:        
    def create_entry(self,id,date,text,pageurl,selfurl,where,dt_from,dt_to,seq,content):
        event = icalendar.Event()
        event.add('summary',unicode(text))
        event.add('dtstart',_s2t(dt_from))
        event.add('dtend',_s2t(dt_to))
        event.add('dtstamp',_s2t(date))
        event['uid'] = "%s@cam.ac.uk" % id
        event.add('priority',5)
        return event
    
    # XXX seems to be nowhere to put summary, that makes me sad.
    def emit(self,id,date,title,url,summary,entries):
        cal = icalendar.Calendar()
        cal.add('version','2.0')
        cal.add('prodid','-//Mercury//cam.ac.uk//')
        cal.add('x-wr-calname',title)
        for e in entries:
            cal.add_component(e)
        # XXX horrible hack for screwy typing.
        # You can tell it's a MS-originated standard with its obsession with confusing, similar types!
        return cal.as_string().decode('utf-8').replace(';VALUE=DATE','').replace('X-WR-CALNAME','X-WR-CALNAME;VALUE=TEXT')
