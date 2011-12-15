import os,sys

heredir = os.path.dirname(os.path.abspath(__file__))

# heredir = "/home/caret/aptana/thallium/python/indium" # needed when profiling

sys.path.insert(0,heredir+"/../lib")

import warnings

warnings.filterwarnings('ignore', '.*the sets module is deprecated.*',DeprecationWarning)

import process_details,process_calendar,generate_feeds
import os.path
import getopt
import logging

def usage():
    print """
Usage:
    
python indium.py -c <cid>   -- calendar file has changed, update others.
python indium.py -d <did>   -- details file has changed, update others.
python indium.py -s [-a] <did> -- csv [spreadsheet] file has changed, update details. (-a -- use alternative format)
python indium.py -g <cid>   -- generate calendar file from details files.
python indium.py -r -- regenerate all calendars, etc, from details files.
python indium.py -F [-a] <did>,<did>,...    -- generate feed on stdout, (-a -- use gcal format)

  All can also optionally take [-l <path to log file>] [-p <path to data dir>]

"""
    sys.exit(1)

def setup_logging(logpath):
    logger = logging.getLogger('indium')
    hdlr = logging.FileHandler(logpath)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.DEBUG)
    logger.debug("staring logging")

def execute(optlist,args):
    path = '../../data'
    logpath = '/tmp/indium.log'
    alt = False
    arg = False
    mode = None
    
    for (opt,val) in optlist:
        if opt in ('-c','-d','-g','-s','-r','-F'):
            mode = opt
            arg = True
        elif opt == '-p':
            path = val
        elif opt == '-a':
            alt = True
        elif opt == '-l':
            logpath = val
            
        if opt == '-r':
            arg = False
    
    script = sys.argv[0]
    if arg:
        file = args[0]
    
    os.chdir(os.path.dirname(script))
    setup_logging(logpath)
    
    if mode == None:
        usage()
    
    logging.getLogger('indium').info("optlist=%s args='%s'" % (optlist,args))
    
    if mode == '-c':
        process_calendar.process_calendar(path,file)
    elif mode == '-d':
        process_details.process_details(path,file)
    elif mode == '-g':
        process_details.generate_calendar(path,file)
    elif mode == '-s':
        process_details.process_spreadsheet(path,file,alt)
    elif mode == '-r':
        process_details.process_all(path)
    elif mode == '-F':
        generate_feeds.generate_feeds(path,args,alt)
    else:
        usage()

if __name__ == '__main__':
    (optlist,args) = getopt.getopt(sys.argv[1:],"cdp:gsarl:FG")
    execute(optlist,args)

    sys.exit(0)
