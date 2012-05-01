#!/usr/bin/env python
# Reads top.json and alice.json to generate a list of subjects. Reads pdfs.csv to find subjects with static links. Reads from pdn-src.csv and all
# the pdn-out*.json files. Reads in and processes all the direct source .csv files. Writes out details_*.csv. Runs -g on all triposes to generate
# calendar files.



import os,sys

heredir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,heredir+"/../lib")
sys.path.insert(0,heredir+"/../indium")

import indium
import inputmethods
import json
import filepaths
import getopt


days = ['M','Tu','W','Th','F','Sa']


def execute(optlist, args):


    #load merge state from teh top and the subjects files.

    mergeState = inputmethods.DetailsMergeState(json.load(file(filepaths.topJsonFilePath)),json.load(file(filepaths.subjectsJsonFilePath)))

    #perform a merge operation with each type according to the order configured inthe input methods.
    for mergeMethod in inputmethods.inputObjects():
        mergeMethod.merge(mergeState)

    # Regnerate calendar entries
    print >>sys.stderr,"Regenerating calendars"
    for tid in mergeState.triposIds:
        indium.execute([('-p',filepaths.datadir),('-g',None)],[tid])
    print >>sys.stderr,"done"

if __name__ == '__main__':
    (optlist,args) = getopt.getopt(sys.argv[1:],"h")
    execute(optlist,args)
    sys.exit(1)
