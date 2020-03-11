"""
utilFJML.py

Programmer: Philip A. Schrodt <schrodt735@gmail.com>
This code is covered under the MIT license: http://opensource.org/licenses/MIT

REVISION HISTORY:
02-Mar-2020:	Initial version
=========================================================================================================
"""
import datetime
import json
import os

VERSION = "0.5b1"
CODEBOOK = "PLOVER 0.7b1"


PLOVER_CAT = ["CONSULT", "ASSAULT", "AGREE", "COERCE", "DISAPPROVE", "SUPPORT", "PROTEST", 
               "REJECT", "DEMAND", "THREATEN", "SANCTION", "INVESTIGATE", "RETREAT", "AID", 
               "CONCEDE", "COOPERATION", "MOBILIZE"] 

               
PLOVER_MODE = {"CONSULT":["host", "visit", "phone", "third-party"], 
                "ASSAULT":["firearms", "heavy-weapons", "suicide-attack", "abduct"], #  "violence", "beat"] #, "sexual"], 
                "COERCE":["arrest", "confiscate", "restrict", "deport"], 
                "PROTEST":["demonstrate", "riot"], # "boycott", "obstruct", "hunger-strike"], 
                "MOBILIZE":["troops", "police"]
            }


PLOVER_CONTEXT = ["diplomatic", "legal", "military", "government", "economic", "humanitarian", "political",
                "refugee", "terrorism", "resource", "culture", "disease", "disaster",  "election", "legislative",
                "cyber", "future", "historical", "hypothetical"]


MAX_SIZE = 3000


def get_timed_suffix():
    return datetime.datetime.now().strftime('%y%m%d%H%M%S')

    
def get_date_time():
    datestr = datetime.datetime.now().strftime('%Y-%m-%d*%H:%M:%S').partition("*")
    return datestr[0], datestr[2]
    

def read_file(filename):
    """ returns next record in a line-delimited JSON file """
    jstr = ""
    for line in open(filename, "r"):
        if line.startswith("}"):
#            print(jstr)   # debug: uncomment to find badly formed cases, or put this into a try/except
            adict = json.loads(jstr + "}")
            yield adict
            jstr = ""
        else:
            if "\t" in line:
                line = line.replace("\t", "\\t")
            jstr += line[:-1].strip()


def read_dictionary(thedict, filename):
    print("Initializing from", filename)
    reader = read_file(filename)
    for rec in reader:
        for name in rec['names']:   
            stlist = name.lower().split()
            curdict = thedict["Root"][0]
            for wd in stlist[:-1]:
                if wd not in curdict:
                    curdict[wd] = [{}, None]
                curdict = curdict[wd][0]
            if stlist[-1] not in curdict:
                curdict[stlist[-1]] = [{}, rec['code'], 0]
            else:
                curdict[stlist[-1]] = [curdict[stlist[-1]][0], rec['code'], 0]

                
def read_newphrase(actordict, filename):
    newdict = {}
    print("Adding new phrases from", filename)
    for ka, line in enumerate(open(filename,"r")): 
        if ":" not in line:
            continue
        part = line[:-1].partition(":")
        name = part[0][3:].partition("  ")[2].strip()
        if part[2] in newdict:
            if name not in newdict[part[2]]:
                newdict[part[2]].append(name)
        else:
            newdict[part[2]] = [name]

    with open("newphrase.scr.jsonl", "w") as fout:
        for key, val in newdict.items():
            outrecord = {"code": key, "names": val}
            fout.write(json.dumps(outrecord, indent=2, sort_keys=True ) + "\n")

    read_dictionary(actordict, "newphrase.scr.jsonl")
    os.remove("newphrase.scr.jsonl")


