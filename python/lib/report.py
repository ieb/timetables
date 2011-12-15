# Generates report view text

import re
import cgi

import group
import util

header_tmpl = """
<h2>%s</h2>
<dl class="report_summary">
  <dt>Course organiser:</dt>
  <dd>%s</dd>
</dl>
<div id="report_head_meta">
  %s
</div>
"""

full_tmpl = """
<div class="report">
  <div class="report_header">
    %s
  </div>
  <div class="report_groups">
    %s
  </div>
  <div class="report_footer">
    %s
  </div>
</div>
"""

group_tmpl = """
  <h3>%s: %s</h3>
  <dl class="report_entries">
    %s
  </dl>
"""

element_tmpl = """
<dt>
  %s
</dt>
<dd>
  %s <small>[%s]</small>
</dd>
"""

time_row_tmpl = """
<tr>
  <td>%s</td>
  <td>%s</td>
  <td>%s</td>
  <td>%s</td>
  <td>%s</td>
  <td>%s</td>
  <td>%s</td>
</tr>
"""

time_tmpl = """
<div class="report_header">
  <div id="report_head_meta">
    %s
  </div>
</div>
<table id="time_table">
<tr>
  <th>Date</th>
  <th>Start</th>
  <th>End</th>
  <th>Type</th>
  <th>What</th>
  <th>Where</th>
  <th>Who</th>
</tr>
%s
</table>
<div class="report_footer">
%s
</div>
"""

def header(d):
    return header_tmpl % (cgi.escape(d.name),cgi.escape(d.who),d.metadata('head'))

def r_element(g,e,year):
    when = year.to_templated_secular_display(e.when,g,type = e.type)
    body = "%s (%s) <i>%s</i>" % (e.what,when,e.where)
    return element_tmpl % (cgi.escape(e.who),body,e.when)

def r_group(g,els):
    return group_tmpl % (group.Group.longnames[g.term],util.plural(g.type),els)

dd_re = re.compile(r'<dd>(.*)</dd>',re.S)

def sort_key((index,text)):
    global dd_re
    # re-extract text!
    m = dd_re.search(text)
    if m:
        text = m.group(1)
    return (text,index)

def report(d,year,sort_text = False):
    groups = []
    for g in d.getGroups():
        row = []
        for e in g.elements:
            row.append(r_element(g,e,year))
        if sort_text:
            row = [x for x in enumerate(row)]
            row.sort(key = sort_key)
            row = [x[1] for x in row]
        groups.append(r_group(g,"".join(row)))
    return full_tmpl % (header(d),"".join(groups),d.metadata('foot'))

def rt_entry(start,end,g,e):
    day = start.date().strftime("%d %B %Y").lstrip('0')  
    st = start.time().strftime("%H:%M")
    et = end.time().strftime("%H:%M")
    return time_row_tmpl % (day,st,et,g.type,e.what,e.where,e.who)

def rt_element(g,e,year):
    out = []
    for dt in year.atoms_to_isos(e.when.patterns(),as_datetime = True):
        out.append((dt[0],rt_entry(dt[0],dt[1],g,e)))
    return out

def report_time(d,year):
    events = {}
    for g in d.getGroups():
        for e in g.elements:
            for (key,value) in rt_element(g,e,year):
                events[key] = value
    events = [events[x] for x in sorted(events.keys())]
    return time_tmpl % (header(d),"".join(events),d.metadata("foot"))
