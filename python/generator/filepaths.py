import os

datadir = "../../data"
srcdatadir = "../../source-data"
gentmpdir = "../../generate-tmp"
idmapFilePath = datadir+"/idmap.csv"
topFilePath = srcdatadir+"/top.csv"
pdfsFilePath = srcdatadir+"/pdfs.csv"
pdfsDataFilePath = datadir+"/pdfs.csv"
topJsonFilePath = datadir+"/top.json"
subjectsJsonFilePath = gentmpdir+"/subjects.json"

# create missing directories if missing
if not os.path.isdir(datadir):
    os.mkdir(datadir)

if not os.path.isdir(gentmpdir):
    os.mkdir(gentmpdir)
