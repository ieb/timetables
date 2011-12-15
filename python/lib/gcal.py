import json
import re
import datetime
import config
import util
import hashlib

template_json = """
{
    "version": "1.0",
    "encoding": "UTF-8",
    "feed": {
        "xmlns": "http://www.w3.org/2005/Atom",
        "xmlns$gCal": "http://schemas.google.com/gCal/2005",
        "xmlns$gd": "http://schemas.google.com/g/2005",
        "id": {
            "$t": "<<feedid>>"
        },
        "updated": {
            "$t": "<<feeddate>>"
        },
        "category": [
            {
                "scheme": "http://schemas.google.com/g/2005#kind",
                "term": "http://schemas.google.com/g/2005#event"
            }
        ],
        "title": {
            "$t": "<<feedtitle>>",
            "type": "text"
        },
        "subtitle": {
            "$t": "<<feedsummary>>",
            "type": "text"
        },
        "link": [
            {
                "rel": "alternate",
                "type": "text/html",
                "href": "<<feedpageurl>>"
            }
        ],
        "author": [
            {
                "name": {
                    "$t": "Mercury"
                },
                "email": {
                    "$t": "letshelp@caret.cam.ac.uk"
                }
            }
        ],
        "gCal$timezone": {
            "value": "UTC"
        },
        "entry": "<<feedentries>>"
    }
}
"""

entry_json = """
{
    "id": {
        "$t": "<<entryid>>"
    },
    "published": {
        "$t": "<<entrydate>>"
    },
    "updated": {
        "$t": "<<entrydate>>"
    },
    "category": [
        {
            "scheme": "http://schemas.google.com/g/2005#kind",
            "term": "http://schemas.google.com/g/2005#event"
        }
    ],
    "title": {
        "$t": "<<entrytext>>",
        "type": "text"
    },
    "content": {
        "$t": "<<entrycontent>>",
        "type": "text"
    },
    "link": [
        {
            "rel": "alternate",
            "type": "text/html",
            "href": "<<entrypageurl>>",
            "title": "alternate"
        }, {
            "rel": "self",
            "type": "application/atom+xml",
            "href": "<<entryselfurl>>"
        }
    ],
    "author": [
        {
            "name": {
                "$t": "Mercury"
            },
            "email": {
                "$t": "letshelp@caret.cam.ac.uk"
            }
        }
    ],
    "gd$eventStatus": {
        "value": "http://schemas.google.com/g/2005#event.confirmed"
    },
    "gd$where": [
        {
            "valueString": "<<entrywhere>>"
        }
    ],
    "gd$who": [
        {
            "email": "letshelp@caret.cam.ac.uk",
            "rel": "http://schemas.google.com/g/2005#event.organizer",
            "valueString": "letshelp@caret.cam.ac.uk"
        }
    ],
    "gd$when": [
        {
            "endTime": "<<entryto>>",
            "startTime": "<<entryfrom>>"
        }
    ],
    "gd$transparency": {
        "value": "http://schemas.google.com/g/2005#event.opaque"
    },
    "gCal$anyoneCanAddSelf": {
        "value": "false"
    },
    "gCal$guestsCanInviteOthers": {
        "value": "false"
    },
    "gCal$guestsCanModify": {
        "value": "false"
    },
    "gCal$guestsCanSeeGuests": {
        "value": "true"
    },
    "gCal$sequence": {
        "value": "<<entryseq>>"
    },
    "gCal$uid": {
        "value": "<<entryuid>>"
    }
}
"""

template = json.loads(template_json)
entry = json.loads(entry_json)

tmpl_re = re.compile(u'<<(.*)>>')
def apply(tmpl,data):
    if isinstance(tmpl,dict):
        out = {}
        for (k,v) in tmpl.iteritems():
            out[k] = apply(v,data)
        return out
    elif isinstance(tmpl,list):
        out = []
        for k in tmpl:
            out.append(apply(k,data))
        return out
    elif isinstance(tmpl,str) or isinstance(tmpl,unicode):
        m = tmpl_re.match(tmpl)
        if m is None:
            return tmpl
        elif m.group(1) not in data:
            return ""
        else:
            return data[m.group(1)]
    else:
        return tmpl

class GCal:
    def create_entry(self,id,date,text,pageurl,selfurl,where,dt_from,dt_to,seq,content):
        return apply(entry,{
            'entryid': id,
            'entrydate': date,
            'entrytext': text,
            'entrypageurl': pageurl,
            'entryselfurl': selfurl,
            'entrywhere': where,
            'entryfrom': dt_from,
            'entryto': dt_to,
            'entryseq': seq,
            'entryuid': "%s@cam.ac.uk" % id,
            'entrycontent': content
        })
    
    def emit(self,id,date,title,url,summary,entries):
        out = apply(template,{
            'feedid': id,
            'feeddate': date,
            'feedtitle': title,
            'feedsummary': summary,
            'feedpageurl': url,
            'feedentries': entries
        })
        return json.dumps(out)
