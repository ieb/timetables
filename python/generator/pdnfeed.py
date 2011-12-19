#!/usr/bin/env python

# Writes pdn-feed.json from scraping PDN site.
import sys
import getopt
import pdninput
import filepaths;

def usage():
    print """
    
Gets the PDN timetable from www.pdn.cam.ac.uk

Usage:
    
./pdnfeed.py   -- Retrieve PDN Feed from within the CUDN
        -u <cookie>  -- Retrieve PDN Feed from outside CUDN using Raven Cookie.
        -p part1,part2,part3  -- Retrieve Parts from the PDN Feed.
        -o <filename>  -- Save the output to the file specified.

"""
    sys.exit(1)



def execute(optlist,args):
    ucam_webauth = ""
    output = filepaths.gentmpdir+'/pdn-feed.json'
    parts = [ 'IA', 'IB', 'II' ]
    sleepTime = 10
    for (opt,val) in optlist:
        if opt == '-u':
            ucam_webauth = val
            print "Will use cookie  %s " % (ucam_webauth)
        elif opt == '-h':
            usage()
        elif opt == '-p':
            parts = val.split(',')
            print "Will get parts %s " % (parts)
        elif opt == '-o':
            output = val
            print "Will output to %s " % output
        elif opt == '-s':
            sleepTime = val
            print "Will sleep between calls %s seconds " % sleepTime

    pdn = pdninput.Pdns()
    pdn.setSleep(sleepTime)
    pdn.setUCamWebAuth(ucam_webauth)
    pdn.getParts()
    for part in (['IA', 'IB', 'II']):
        pdn.getPart(part)

    pdn.dumpFeed(output);


if __name__ == '__main__':
    (optlist,args) = getopt.getopt(sys.argv[1:],"hu:p:o:s:")
    execute(optlist,args)
    sys.exit(1)