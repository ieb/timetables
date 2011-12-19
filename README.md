# Timetables

This repository contains the Timetables software developed at Caret, University of Cambridge and licensed open source under the AGPL license. 

Before using please read the LICENSE file contained in this repository.

Before contributing please read the LICENSE and NOTICE file contained within this repository.

We have chosen to make this software open source to allow others to use it and we have chosen the AGPL license to encourage others to contribute modifications and extensions back to the wider community in some form. Obviously we would not expect or ask anyone to contribute modifications and extensions containing to private or security related information back to the wider community.

# Introduction

Timetables primary use case to to provide a timetable based on official sources of information for a student. The student is able to select the courses, lectures, activities that they attend and interact with to produce a customised calendar of information that they can then use either via the timetables user interface, or as a feed into other applications. Specially authorized users are given the ability to create and edit timetables, since in some cases the official source of information may be incomplete.

The web application comes in two parts. A web front end, written largely in PHP serving up HTML pages, many of which make heavy use of client side programming (JQuery etc) to build the user interface from feeds of information. The feeds of information are represented as JSON feeds, containing details of events and the relationships between events and the structure into which those events fit. Those events are largely stored on disk as JSON files. The JSON files are maintained by Python scripts that process source information from the institution to publish the JSON files. These scripts are written for the University of Cambridge and rely on source of information specific to Cambridge, many of which are only available on the internal network (CUDN) at Cambridge. If this code was to be used at another institution the Python code would need to be customised to work with the sources of information at that institution.


# Documentation

You will find working documentation in the Wiki and issue tracker associated with this repository. In addition there is documentation under the doc folder that was imported from the original project.

# Layout of code base

* /config - base configuration for the system.
* /doc - documentation
* /python - python code for generating and managing the json feeds.
* /python/error - error handler
* /python/generator - python generator scripts for generating json feeds from sources
* /python/indium - final processing script to build JSON feeds to support the webapp, see indium.py for details.
* /python/lib - supporting Python library code.
* /spec - orriginal specification for web application
* /web - php web application with html pages


# Installation

## Requirements

* Apache HTTPD 2.2 or later
* PHP 5.3 or later
* Python 2.6
    * python-ldap 2.4.3 install using  ''sudo easy_install python-ldap''
    * pytz install using ''sudo easy_install pytz''
    * simplejson 2.2.1 ''sudo easy_install simplejson''
    * icalendar ''sudo easy_install icalendar''

## Map the web application into Apache.

Edit config/config.txt to represent your installation. The value of base must be changed to match the path where you want the application to be hosted. It is used by both the Python code at generation stage and the Php code at application runtime.

Include config/apache.config in an appropriate place, replacing __SOURCE__ with the appropriate path to your source code. It maps the /web into the HTTPD url space. You may want to add other configuration statements to suite your environment.

Look in web/php/config.php and check that the paths are ok, in particular the path of the python executable.

## Authentication

Authentication is performed by Apache, which should protect web/php/login.php. The default configuration uses Basic Auth and an password file. For a simple deployment you can use this approach. Follow the instructions in config/apache.config to set this up. (ie create a password file in config/passwords using htpasswd)

## Authorization

Authorization is controlled with a user json file in /data. eg user_ieb.json. To grant ieb full editing access create /data/user_ieb.json containing

    {"triposes":[],"all":true}

Do the same for any users that you want to give full access.


## Generating initial data

Data is generated under /data. This is done using python scripts.
First create some directories

    mkdir data
    mkdir generator-tmp
    touch data/log.txt
    chgrp www-data data/log.txt
    chmod g+w data/log.txt
    cd python/generator

Starting from source-data/top.csv, generate (or update) data/idmap.csv data/pdfs.csv, data/top.json, data/subjects.json

    python topgen.py


## Generate some subject data

Acquiring subject data will be specific to the institution. The aim is to create subject json files that can be used to create calendar files in the correct format. These are some examples from Cambridge. Unless you have access to the data feeds from Cambridge you will need to create your own.

### Generate Data from Department of Physiology, Development and Neuroscience online timetable. (Optional)

This is an example of generating json subject files from an external source. If you have access to the CUDN or a Raven account then you can generate data from Department of Physiology, Development and Neuroscience online timetable.

Create generator-tmp/pdn-feed.json from http://www.pdn.cam.ac.uk/teaching/resources/timetabledb/htdocs/ (Raven Login required)

    python pdnfeed.py

Using source-data/lect-lab.csv to discriminate between lectures and labs, generate one json file per subject in generator-tmp/pdn-feed.json

    python pdngen.py

### Generate Data from Department of Medieval and Modern Languages (Optional)

This is an example of generating json subject files from an local source. In this case /generator-tmp/subjects.json contains subject data. ygen.py converts this into subject json files, one per subject.

    python ygen.py


## Generate Calendar files

The final step is to convert the subject.json files from multiple sources into calendar files. This generates 100s of json files, one per Calendar. Each filename is based on the ID of the course.

    python detgen.py


## Refresh Calendar files

If you have a set of source data and just want to re-generate the Calendar json files you can use indium.py directly. This script takes data/details_*.json files and generates a collection of files associated with each detail file.

    python indium.py -r





# Credits

* The work was funded by : ?
* Original code largely written by Dan Shepard whilst at Caret
* For other contributions, please consult the commit history.

(c) 2011 University of Cambridge


