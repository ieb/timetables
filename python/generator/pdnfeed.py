# Writes pdn-feed.json from scraping PDN site.

pdn_host = "www.pdn.cam.ac.uk"
pdn_base = "/teaching/resources/timetabledb/htdocs/"
pdn_query = "/teaching/resources/timetabledb/htdocs/index.php"

gentmpdir = "../../generate-tmp"

# XXX robust feed error reporting

# Steal raven cookies for access outside Cambridge
ucam_webauth = ""

#

import httplib,re,time,urllib,sys,collections,json,os

os.chdir(os.path.dirname(sys.argv[0]))

events = []
def add_lecture(part,what,subj,who,where,when_d,when_s,when_e):
    date_s = time.strftime("%Y-%m-%d %H:%M:%S",time.strptime("%s %s" % (when_d,when_s),"%d %b %y %H:%M"))
    date_e = time.strftime("%Y-%m-%d %H:%M:%S",time.strptime("%s %s" % (when_d,when_e),"%d %b %y %H:%M"))
    print "what=%s subj=%s who=%s where=%s date_s=%s date_e=%s" % (what,subj,who,where,date_s,date_e)
    events.append((part,what,subj,who,where,date_s,date_e))

main_re = re.compile(r'<table.*?id=Main.*?>(.*?)</table>',re.S)
row_re = re.compile(r'</tr>')
cell_re = re.compile(r'</t[dh]>')
detag_re = re.compile(r'<.*?>')
def process_subject(part,name,data):
    # Extract table
    m = main_re.search(data)
    if m == None:
        raise Exception("Cannot find main table in '%s'" % name)
    # split into rows
    rows = row_re.split(m.group(1))
    if len(rows) < 3:
        raise Exception("Bad table, too short for '%s'" % name)
    if len(rows) == 3:
        print >>sys.stderr,"WARN: Table contained no data for '%s'" % name
    rows = rows[2:-1]
    for row in rows:
        cells = cell_re.split(row)
        cells = [ detag_re.sub('',x) for x in cells ]
        add_lecture(part,cells[15],cells[20],cells[5],cells[14],cells[11],cells[12],cells[13])
    
headers = {}
if ucam_webauth:
    headers['Cookie'] = "Ucam-WebAuth-Session=%s" % ucam_webauth

conn = httplib.HTTPConnection(pdn_host)
conn.request("GET",pdn_base,headers=headers)
r1 = conn.getresponse()
if r1.status != 200:
    raise Exception("Didn't get 200 getting http:/%s/%s" % (pdn_host,pdn_base))
base = unicode(r1.read(),"ISO-8859-1")

# Find Module selector
module_re = re.compile(r"<select.*?name='Module'.*?>(.*)</select>")
m = module_re.search(base)
if not m:
    raise Exception("Couldn't find dropdown")
modules = m.group(1)

# Split on optgroups
groups = {}
groups_re = re.compile('<optgroup.*?label=[\'"](.*?)[\'"](.*?)</optgroup>')
def og(m):
    groups[m.group(1)] = m.group(2)
    return ''
groups_re.sub(og,modules)

names = collections.defaultdict(list)
for part in ('IA','IB','II'):
    # Get our optgroup and extract subjects XXX
    group = groups[part]
    subjects = {}
    if not group:
        raise Exception("Cannot find %s" % part)
    options_re = re.compile('<option.*?value=[\'"](.*?)[\'"].*?title=[\'"](.*?)[\'"].*?>')
    def os(m):
        subjects[m.group(1)] = m.group(2)
        return ''
    options_re.sub(os,group)
    
    # Iterate through subjects
    for (key,name) in subjects.iteritems():
        names[part].append(name)
        print "Retrieving '%s'" % name
        params = urllib.urlencode({'Location': 'All', 'Module': key, 'action': 'Whole Year', 'AcadYear': '11/12'})
        headers = {"Content-type": "application/x-www-form-urlencoded" }
        if ucam_webauth:
            headers['Cookie'] = "Ucam-WebAuth-Session=%s" % ucam_webauth        
        conn.request("POST",pdn_query,params,headers)
        r1 = conn.getresponse()
        if r1.status != 200:
            raise Exception("Didn't get 200 getting http:/%s/%s" % (pdn_host,pdn_base))
        data = unicode(r1.read(),"ISO-8859-1")    
        process_subject(part,name,data)
        time.sleep(10)
        
# Output data in sensible format
out = {
    'subjects': names,
    'events': events
}
json.dump(out,open(gentmpdir+'/pdn-feed.json','wb'))
