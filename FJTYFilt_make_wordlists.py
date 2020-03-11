"""
FJTYFilt_wordlists_from_stories.py

Reads a -stories file (labelled or unlabelled) in PLOVER data-exchange (PDE) format, filters to get rid of stop words and other 
likely non-words, then writes a list of the remaining words as a space-delimited string (per requirement of the sklearn SVM routines) 
to a PDE formatted file with "-wordlists" replacing "-stories" in the name. Input file list and file path is currently hard coded

TO RUN PROGRAM:

python3 FJTYFilt_wordlists_from_stories.py <-f filename> <-c filename>

where 

-f: read a simple list of file names, one name per line
-c: read a list of file names from the FJTY.plovigy.filerecs.txt output of FJTY.plovigy.py, so the file name is the fourth item in
    a space-limited string
-o: output file name; otherwise set based on input files

PROGRAMMING NOTES: 

1. There is also a hard-coded default for FILE_NAMES

SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 10.13.5; it is standard Python 3.7
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
31-Jan-17:	Initial version
04-Mar-20:  Modified from make_wordlists_nolabel.py to use PLOVER formats

=========================================================================================================
"""
import sys
sys.path.insert(1, "../FJ-2/")  # this is specific, obviously, to the particular directory structure I was using

import utilFJML
import spacy
import json
import os

FILE_PATH = "./"
FILE_NAMES = ["REUT-20-02-25-stories.jsonl", "REUT-20-02-26-stories.jsonl", "REUT-20-02-27-stories.jsonl", "REUT-20-02-28-stories.jsonl"]
FILE_NAMES = ["CovidEight-stories.jsonl"]  # useful if just processing a single file

def get_words():
    """ filter using spaCy and write remaining list """
#    print(story)
    story = ""
    for lp in rec["textInfo"]["textStory"]:
        story += " " + lp
    parsed_review = nlp(story)
#    print(str(parsed_review))
    wlist = []
    nnum = 0
    for num, token in enumerate(parsed_review):
        if token.like_num:
            nnum += 1
        if (len(token.lemma_) > 3) and \
           (token.lemma_.isalpha()) and \
           (token.ent_iob_ == 'O') and \
           (not token.text[0].isupper()) and \
            not (token.is_stop or token.is_punct or token.is_space or token.like_num):
            wlist.append(token.lemma_)
    pldict = {"textInfo": {"wordlist": " ".join(wlist)}, "citeInfo": {"title": rec["citeInfo"]["title"]}, "id": rec["id"]}
    if "mode" in rec:
        pldict['mode'] = rec['mode']
    fout.write(json.dumps(pldict, indent=2, sort_keys=True ) + "\n")
            
    
outfilename = None
for cmdopt in sys.argv: # yes, I know there is also a massive package that can do this...
    if cmdopt.startswith('-') and cmdopt in ["-o", "-f", "-c"]:
        theopt = sys.argv[sys.argv.index(cmdopt) + 1]
        if cmdopt in ["-f", "-c"]:
            try:
                print("Reading file list from", sys.argv[2])
                if sys.argv[1] == "-f":  
                    FILE_NAMES = [line[:-1] for line in open(sys.argv[2], "r")]
                elif sys.argv[1] == "-c":
                    print([line.split(" ") for line in open(sys.argv[2], "r")])
                    FILE_NAMES = [line.split(" ")[3] for line in open(sys.argv[2], "r")] # FJTY.plovigy.filerecs.txt output of FJTY.plovigy.py
            except:
                print("Could not locate the file", sys.argv[2])
                exit()
        if cmdopt == "-o":
            outfilename = theopt
    elif cmdopt.startswith('-'):
        print("Unrecognized option: " + cmdopt, end=" ")
        try:
            print(sys.argv[sys.argv.index(cmdopt) + 1])
        except:
            print()


if not outfilename:
    if "-stories." in FILE_NAMES[0]:
        outfilename = FILE_NAMES[0].replace("-stories.","-wordlists.") # use for regular name
    else:
        outfilename = "null-wordlists-" + FILE_NAMES[0] # alternative if name is not regular


print("Loading en_core_web_sm")
nlp = spacy.load('en_core_web_sm')

ka = 0
fout = open(outfilename,'w')
for filename in FILE_NAMES[:]:
    reader = utilFJML.read_file(os.path.join(FILE_PATH, filename))
    print("\nReading", FILE_PATH + filename)
    for krec, rec in enumerate(reader):
        if krec % 32 == 0:
            print(krec, rec["id"])
        get_words()
        ka += 1
#        if krec > 3: break

print(ka, "stories processed")
fout.close()

print("Finished")