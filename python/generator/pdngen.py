#!/usr/bin/env python

# From the data feed generate some details. Separated from pdn-feed.py to allow iteration in this code without refetch.
# Reads in lect-lab.csv and pdn-feed.json and generates lots of pdnout-*.json

import os,sys

heredir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,heredir+"/../lib")


import pdninput
import filepaths
import getopt


def usage():
    print """

Converts the PDN timetable into details files

Usage:

./pdngen.py   -- Retrieve PDN Feed from within the CUDN
        -i <filename>  -- Load from the input file
        -o <outputDir>  -- The output location

"""
    sys.exit(1)


def execute(optlist, args):
    inputFeed = filepaths.gentmpdir+'/pdn-feed.json'
    output = filepaths.gentmpdir
    for (opt,val) in optlist:
        if opt == '-i':
            inputFeed = val
            print "Will input from %s " % output
        elif opt == '-h':
            usage()
        elif opt == '-o':
            output = val
            print "Will output to %s " % output

    pdn = pdninput.Pdns()
    pdn.loadFeed(inputFeed)
    pdn.deleteSubjects(output)
    pdn.extractSubjects(output)


if __name__ == '__main__':
    (optlist,args) = getopt.getopt(sys.argv[1:],"hi:o:")
    execute(optlist,args)
    sys.exit(1)

