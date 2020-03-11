"""
FJTYFilt-plovigy.py

A subset of plovigy-mark.py which uses the PLOVIGY data exchange jsonl format and is a low-footprint terminal-based system for 
classifying discard modes. The program adds a "mode" field of the form 

FJFILT_CATEGORIES[int(keych)][0] + "-" + FJFILT_CATEGORIES[int(keych)][1]

(for example "0-codeable", "1-sports",  "2-culture/entertainment") and overwrites the 'parser', 'coder', 'codedDate' and 'codedTime' fields. 

TO RUN PROGRAM:

python3 FJTYFilt-plovigy.py <options>

where the options are pairs as follows:

-f <filename>    file to read (required)
-c <coder>       optional coder identification (defaults to Parus Analytics)
-a <filename>    optional name for autocoding lists

KEYS

0-9       add mode to the record and write     
+/space   skip: typically used when duplicates are recognized
q         quit 

AUTOCODING 

An autocoding file consists of a set of lines in the format

  <mode#>-<mode_text>: <comma delimited list of phrases>
  
Example:
0-codeable-auto: Trump, Xi, WHO
8-covid-19: coronavirus, covid-19, COVID-19
3-gold-prices: Gold prices

Autocoding checks the first AUTO_WINDOW characters in the text and if a phrase is found, the "mode" is set to <mode#>-<mode_text> 
and the record is written without pausing. The lists are checked in order, so for example a text "Xi said China had the coronavirus
under control" would have a mode of 0-codeable-auto, not 8-covid-19.

PROGRAMMING NOTES:

1. The file FILEREC_NAME keeps track of the location in the file.

2. Output file names replaces "-stories" with "-labelled" and adds a time-stamp

3. Key input is not case-sensitive

4. Currently the program is using integers for the mode, which obviously restricts these to 10 in number. It is easy to 
   modify this to use other one-key alternatives, e.g. A, B, C,..., or if you are using a keypad, +, -, *, ... and then
   change the FJTYFilt_wordlists.py program to adjust for this.
   
5. AUTO_WINDOW is currently a constant but it would be easy to modify the program so this could be set in the autofile lists,
   e.g. something like
            0-codeable-auto: 128: Trump, Xi, WHO
            8-covid-19: 256: coronavirus, covid-19, COVID-19
            3-gold-prices: 32: Gold prices
 

SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 10.13.6 and Ubuntu 16.04; it is standard Python 3.7 so it should also run in Windows. 

PROVENANCE:
Programmer: Philip A. Schrodt
            Parus Analytics
            Charlottesville, VA, 22901 U.S.A.
            http://eventdata.parusanalytics.com

Copyright (c) 2020	Philip A. Schrodt.	All rights reserved.

plovigy-mark.py was initially developed as part of research funded by a U.S. National Science Foundation "Resource 
Implementations for Data Intensive Research in the Social Behavioral and Economic Sciences (RIDIR)" 
project: Modernizing Political Event Data for Big Data Social Science Research (Award 1539302; 
PI: Patrick Brandt, University of Texas at Dallas)

This code is covered under the MIT license: http://opensource.org/licenses/MIT

Report bugs to: schrodt735@gmail.com

REVISION HISTORY:
15-Dec-17:	Initial version
04-Jan-18:	Default switching option
23-Jan-18:	Buffered output; comment option
14-May-19:  Modified for PITF-PROT
24-Jul-19:  Modified to use curses
09-Mar-20:  Modified from plovigy-mark.py for FJTY system

=========================================================================================================
"""
import sys
sys.path.insert(1, "../FJ-2/")

import utilFJML
import textwrap
import curses
import json
import os


CMD_OPTIONS = ["-f", "-c", "-a"]

FJFILT_CATEGORIES = [("0", "codeable"), ("1", "sports"), ("2", "culture/entertainment"), ("3", "business/finance"), 
        ("4", "opinion"), ("5", "crime"), ("6", "accidents"), ("7", "natural disaster"), ("8", "[open]"), 
        ("9", "no codeable content")]

FILEREC_NAME = "FJTY.plovigy.filerecs.txt"  # used to pick up after the last record already coded

FIELDOPTIONS = "0123456789"
KEYOPTIONS = FIELDOPTIONS + " XQ+"

CATEGORY_OFFSET = 7   # Y-axis negative offset for category list

AUTO_WINDOW = 256  # number of characters to search for autoList phrases


# process command line options
coder = "Parus Analytics"  # set defaults
filename, autoFilename = None, None

for cmdopt in sys.argv: # yes, I know there is also a massive package that can do this...
    if cmdopt.startswith('-') and cmdopt in CMD_OPTIONS:
        theopt = sys.argv[sys.argv.index(cmdopt) + 1]
        if cmdopt == "-f":
            filename = theopt
        elif cmdopt == "-c":
            coder = theopt
        elif cmdopt == "-a":
            autoFilename = theopt
        """elif cmdopt == "-sp":
            STORY_PREFIX = theopt
        elif cmdopt == "-wp":
            WORDLIST_PREFIX = theopt
        elif cmdopt == "-fp":
            OUTPUT_PREFIX = theopt"""
    elif cmdopt.startswith('-'):
        print("Unrecognized option: " + cmdopt, end=" ")
        try:
            print(sys.argv[sys.argv.index(cmdopt) + 1])
        except:
            print()
            
if not filename: 
    print("File name (-f) is required")
    exit()
    
if autoFilename:
    if not os.path.exists(autoFilename):
        print("The autocoding file", autoFilename, "could not be found\nExiting program")
        exit()  
    autoLists = []
    for line in open(autoFilename,"r"):
        part = line[:-1].partition(":")
        autoLists.append((part[0],[li.strip() for li in part[2].split(",")]))

#print(autoLists)
#exit()
    
nskip = 0
if os.path.exists(FILEREC_NAME):  
    with open(FILEREC_NAME,'r') as frec:
        line = frec.readline() 
        while line:  # go through the entire file to get the last entry
            if filename in line:
                nskip = int(line.split()[1])
            line = frec.readline()

if nskip < 0:
    print("All records in", filename, "have been coded")
    answ = input("Do you want to restart at the beginning of the file? (Y/N) -->")
    if answ in ['Y','y']:
        nskip = 0
    else:
        print("Please select another file: exiting program")
        exit()    

if nskip == 0:
    print("Restarting at the beginning of", filename)
else:
    print("Skipping first", nskip - 1,"records in",filename)            

answ = input("Press return to start...")

def main(stdscr):

    global nskip
    
    SUBW_HGT = 48   # dimensions of coding window in characters
    SUBW_WID = 148
    INIT_Y = 2 
    INIT_X = 4

    def next_key(win):    
        key = 31
        while chr(key).upper() not in KEYOPTIONS: 
            win.addstr(SUBW_HGT-2, 2, "Enter option: ")  # maybe give an error here for invalid entry?
            key = win.getch()
            win.clrtobot()
            win.border()
        win.refresh()
        return key, chr(key).upper()

    def show_categories(win):
        """ warning: assorted magic numbers here in terms of offsets """
        Y_ORG = SUBW_HGT - CATEGORY_OFFSET
        X_ORG = 24
    
        xc = X_ORG
        yc = Y_ORG
        win.addstr(yc, xc, "Categories")
        for val in FJFILT_CATEGORIES:
            if val[0] == "4":
                xc = 54
                yc = Y_ORG
            elif val[0] == "7":
                xc = 72
                yc = Y_ORG
            win.addstr(yc, xc, val[0]  + ": " + val[1])
            yc += 1
            
    def write_record(autocode = False):
        if autocode:
            record["citeInfo"]['parser'] = "Mode autocoded in FJTYFilt-plovigy.py using " + autoFilename
        else:
            record["citeInfo"]['parser'] = "Mode set using in FJTYFilt-plovigy.py"
        record['codedDate'], record['codedTime'] = utilFJML.get_date_time()
        record['coder'] = coder
        fout.write(json.dumps(record, indent=2, sort_keys=True ) + "\n")


    nacc, nrej, nauto = 0, 0, 0  # counters for annotations
    for ka, record in enumerate(reader):
        if ka < nskip:
            continue
            
        thestory = " ".join(record["textInfo"]["textStory"]) 
        if autoFilename:
            gotone = False
            for li in autoLists:
                for target in li[1]:
                    if target in thestory[:AUTO_WINDOW]: 
                       record["mode"] = li[0]
                       write_record(autocode = True)
                       nauto += 1
                       gotone = True
                       break
                if gotone: 
                    break
            if gotone:
                continue                        

        modwin = curses.newwin(SUBW_HGT ,SUBW_WID, 2, 2)
        modwin.border()         
        
        modwin.addstr(INIT_Y, INIT_X, str(ka) + ": " + record['date'] )
        modwin.addstr(INIT_Y+2, INIT_X,record['citeInfo']['title'])
        y_curs = INIT_Y + 4
        x_curs = INIT_X
        for ln in textwrap.wrap(thestory,128):
            if y_curs >= SUBW_HGT - CATEGORY_OFFSET - 2:
                modwin.addstr(y_curs, x_curs, ln[:-20] + " ...---TRUNCATED---")
                break
            modwin.addstr(y_curs, x_curs, ln)
            y_curs += 1
        show_categories(modwin)
        modwin.addstr(SUBW_HGT-2, x_curs+96, "accept:{:3d}   skip:{:3d}   auto:{:3d}   total:{:3d}".format(nacc, nrej, nauto, nauto + nacc + nrej))
        modwin.addstr(SUBW_HGT-2, INIT_X + 16, "Options: [0-9] write mode     +/space skip     Q quit") 
        
        modwin.refresh()
        key, keych = next_key(modwin)

        if keych in FIELDOPTIONS:
            nacc += 1
            record["mode"] = FJFILT_CATEGORIES[int(keych)][0] + "-" + FJFILT_CATEGORIES[int(keych)][1]
            write_record()
        elif " " == keych or " "  == keych:
            nrej += 1
        elif keych == "Q":
            nskip = ka
            return nacc, nrej, nauto

    else:
        print("All records have been coded")
        nskip = -1
        return nacc, nrej, nauto

savedrecs = []
timestr = suffix = utilFJML.get_timed_suffix()
if "-stories." in filename:
    outfilename = filename.replace("-stories.","-labelled-" + timestr + ".") # use for regular name
else:
    outfilename = "null-labelled-" + timestr + "-" + filename # alternative if name is not regular
fout = open(outfilename, "w")

reader = utilFJML.read_file(filename)
nacc, nrej, nauto = curses.wrapper(main)

fout.close()

with open(FILEREC_NAME,'a') as frec:  # record cases coded and current position in file
    frec.write("{:s} {:d} {:s} {:s}".format(filename, nskip, timestr,outfilename)) 
    frec.write( "  accept:{:3d}  reject:{:3d}  auto:{:3d}  total:{:3d}".format(nacc, nrej, nauto, nauto + nacc + nrej))
    if autoFilename:
        frec.write("  autoFilename:" + autoFilename)
    frec.write("\n")

print("Finished")
