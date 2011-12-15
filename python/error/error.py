# Error handler, trusted with recording snafus. Hence rather simple to avoid failing itself.
#
# takes aleternating keys and values as arguments, and stores them as foo = bar in the error directory, having substituted tabs with four space and newlines with tabs.
# the filename is error_<timestamp>_<rnd>.txt . where <rnd> is a 32 bit random int, to avoid clashes in same-second reports with a probability of 99.998%
#
# also adds report-time key containing report time and may, in future, add other keys beginning report-*
#
# conventional keys and values are
#
# receiver-user = crsid
# session = jssesison id
# url = originating url
# parent = parent url
# time = time error created according to originator
# origin = identifier of unit reporting error
# message = message displayed to user
# report = full error report (eg stacktrace)
# level = info,warn,error
#
# a trialing key (ie odd number of arguments) implies value will be supplied on stdin

# SETUP ENVIRONMENT OF EXECUTABLE
import os
import sys

heredir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0,heredir+"/../lib")

os.chdir(os.path.dirname(sys.argv[0]))

# ENVIRONMENT IS NOW SET UP!
import time

import error

data = sys.argv[1:]
if not len(data):
    data.append('report-was-blank')
    data.append('')
elif len(data) % 2:
    data.append(sys.stdin.read().decode('utf-8'))
data = dict(zip(data[0::2],data[1::2]))

error.record(data)
