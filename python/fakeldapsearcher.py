import sys
import os,os.path
import getopt
import simplejson as json

folk="""
Agatha
Dorothy
Freya
Fuchsia
Gwen
Louise
Magdalene
Mildred
Muriel
Pauline
Ramona
Roxanne
Ruth
Sally
Wilhelmina
Zelda
Albert
Alfred
Bernard
Boaz
Chester
Claude
Clement
Conrad
Cyrus
Earl
Edgar
Hector
Ira
Leon
Leroy
Linus
Luther
Oswald
Otto
Ralph
Roscoe
Roy
Stanley
Vance
Vaughan
Victor
Waldo
Wilfred
Bernice
Beulah
Beverly
Claudine
Doris
Elva
Ernestine
Fern
Garnet
Gladys
Gloria
Hilda
Hildegarde
Irma
Leona
Luella
Lucille
Maxine
Maybelle
Opal
Peggy
Thomasina
Yolanda
Clarence
Egbert
Enoch
Floyd
Godfrey
Herman
Irving
Leonard
Lester
Lloyd
Murray
Roger
Calliope
Columba
Cressida
Flavia
Inez
Junia
Ludovica
Suzette
Andre
Anton
Baptiste
Dmitri
Ferdinand
Hans
Ilario
Manuel
Nico
Olaf
Severin
Baldwin
Billie
Byron
Dewey
Etta
Farrah
Gatsby
Guthrie
Hale
Hawthorne
Hero
Icarus
Ichabod
Lana
Laszlo
Lazarus
Lolita
Ludwig
Lyle
Maynard
Merlin
Narcissa
Odetta
Rhett
Thor
Ulysses
Whistler
Zora
"""

people = []
for (i,v) in enumerate(folk.split()):
    people.append("%s [abc%d]" % (v,i))

def usage():
    print """
Usage:
    
python ldapsearcher.py -m <term>   -- find matches to term.

"""
    sys.exit(1)

# for some reason or queries are very slow. Doing them separately gives us more control anyway.

def autocomplete(q):
    q = q.lower()
    out = []
    if len(q)<2:
        return []
    for v in filter(lambda x: x.lower().find(q) != -1,people):
        outbits = {
        "id" : v,
        "value": v,
        "label": v
        }
        out.append(outbits)
    return out

(optlist,args) = getopt.getopt(sys.argv[1:],"m:")

for (opt,val) in optlist:
    if opt == '-m':
        mode = '-m'
        term = val

script = sys.argv[0]

if term == None:
    usage()

if mode == '-m':
   print json.dumps(autocomplete(term))
else:
    usage()
sys.exit(0)
