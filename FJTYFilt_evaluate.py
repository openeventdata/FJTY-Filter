"""
classify_unlabelled.py

Reads pickled files for a vectorized and model that were generated by SVM_filter_estimate.py then classifies case-word
vectors from the file INPUT_FILE_NAME which was generated by make_wordlists_nolabel.py. If the prediction corresponds
to MODE, writes the urls of the case to screen and a file OUTPUT_PREFIX + "." + str(MODE) + ".urls.txt". 

The command option -wp writes the wordlists of these predicted cases to a file WORDLIST_PREFIX + "." + str(MODE) + ".wordlists.txt":
this is used when these cases will be added to a training set.

The command options -sp and -sf writes the stories of these predicted cases to a file STORY_PREFIX + "." + str(MODE) + ".stories.txt":
this is used when manually reviewing the classifications.

TO RUN PROGRAM:

python3 classify_unlabelled.py -m <mode> [optional command pairs]

Command option occur in pairs -<option> <value>. -m mode is required

    -wf INPUT_FILE_NAME : name of the wordlist file of unlabelled vectors to be classified. Default: hard-coded name in program
    -fp OUTPUT_PREFIX   : prefix for the file which lists of the urls that were predicted as being MODE. Default: "Mode"
    -sp STORY_PREFIX    : prefix for file of stories for the cases that were predicted as being MODE. Default: do not write file
    -sf STORY_FILE_NAME : name of .stories.txt file used to generate the unlabelled vectors. Require if -sp is used
    -wp WORDLIST_PREFIX : prefix for file of wordlists for the cases that were predicted as being MODE. Default: do not write file


PROGRAMMING NOTES: None


SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 10.10.5; it is standard Python 3.5
so it should also run in Unix or Windows. 

PROVENANCE:
Programmer: Philip A. Schrodt
            Parus Analytics
            Charlottesville, VA, 22901 U.S.A.
            http://eventdata.parusanalytics.com

Copyright (c) 2017	Philip A. Schrodt.	All rights reserved.

This code is covered under the MIT license: http://opensource.org/licenses/MIT

Report bugs to: schrodt735@gmail.com

REVISION HISTORY:
31-Jan-17: Initial version
23-Feb-17: Integrated functions of get_urls, get_urls_wordlists; added full cmd-opts
04-Mar-20: Modified from classify_unlabelled.py to use the PLOVER formats

=========================================================================================================
"""

import sys
sys.path.insert(1, "../FJ-2/")

import utilFJML
import pickle
import json
import os

CMD_OPTIONS = ["-m", "-wf", "-sf", "-fp", "-sp", "-wp"]

FILE_PATH = "./"
INPUT_FILE_NAME = "demo-REUT-20-02-25-wordlists.jsonl"  
MODE = None
STORY_FILE_NAME = None
STORY_PREFIX = None
WORDLIST_PREFIX = None
OUTPUT_PREFIX = "Mode"

FJFILT_CATEGORIES = [("0", "codeable"), ("1", "sports"), ("2", "culture/entertainment"), ("3", "business/finance"), 
        ("4", "opinion"), ("5", "crime"), ("6", "accidents"), ("7", "natural disaster"), ("8", "[open]"), 
        ("9", "no codeable content")]


for cmdopt in sys.argv:
    if cmdopt.startswith('-') and cmdopt in CMD_OPTIONS:
        theopt = sys.argv[sys.argv.index(cmdopt) + 1]
        if cmdopt == "-m":
            MODE = int(theopt)
        elif cmdopt == "-wf":
            INPUT_FILE_NAME = theopt
        elif cmdopt == "-sf":
            STORY_FILE_NAME = theopt
        elif cmdopt == "-sp":
            STORY_PREFIX = theopt
        elif cmdopt == "-wp":
            WORDLIST_PREFIX = theopt
        elif cmdopt == "-fp":
            OUTPUT_PREFIX = theopt
    elif cmdopt.startswith('-'):
        print("Unrecognized option: " + cmdopt, end=" ")
        try:
            print(sys.argv[sys.argv.index(cmdopt) + 1])
        except:
            print()
            
if STORY_PREFIX and not STORY_FILE_NAME:
    print("STORY_FILE_NAME (-sf) is required if the -sp option is used")
    sys.exit()


if WORDLIST_PREFIX:
    fwdl = open(WORDLIST_PREFIX + "." + str(MODE) + ".wordlists.txt", 'w')
else:
    fwdl = None

#pvector = pickle.load(open("save.vectorizer.p", "rb"))
#pmodel = pickle.load(open("save.lin_clf.p", "rb"))
pvector = pickle.load(open("save-vectorizer-Mk2.p", "rb"))
pmodel = pickle.load(open("save-lin_clf-Mk2.p", "rb"))


testcase = []
caseurl = []
filename = INPUT_FILE_NAME
reader = utilFJML.read_file(os.path.join(FILE_PATH, filename))
print("\nReading", FILE_PATH + filename)
for krec, rec in enumerate(reader):
    testcase.append(rec["textInfo"]["wordlist"])
    caseurl.append((rec["id"], rec["citeInfo"]["title"]))
print(len(testcase),"cases")

XP_test = pvector.transform(testcase).toarray()

urls = []
if MODE:
    fout = open(OUTPUT_PREFIX + "." + str(MODE) + ".urls.txt", 'w')
else:
    fout = open(OUTPUT_PREFIX + ".all.urls.txt", 'w')
for kcase, xv in enumerate(XP_test):
    pred = pmodel.predict([xv])
    if not MODE or pred[0] == MODE:
        urls.append(caseurl[kcase])
        print(urls[-1])
        fout.write(str({"mode": str(pred[0]) + "-" + FJFILT_CATEGORIES[pred[0]][1], 
                        "id": caseurl[kcase][0], 
                        "title": caseurl[kcase][1]})
                         + '\n')
        if fwdl:
            fwdl.write(str(MODE) + line[1:])

fout.close()
if fwdl:
    fwdl.close()

if STORY_PREFIX:
    print("Getting stories from",STORY_FILE_NAME)
    fsty = open(STORY_PREFIX + "." + str(MODE) + ".stories.txt", 'w')
    fin = open(STORY_FILE_NAME,'r')
    read_fin()
    fsty.close()
        
print("Finished")