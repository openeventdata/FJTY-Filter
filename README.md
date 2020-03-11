# FJTYFilter system

The FJTYFilter system is a series of Python programs for pre-filtering news articles using an SVM classifier trained by example
(sample files are included).
The system uses the [PLOVER data-exchange format](https://github.com/openeventdata/PLOVER): [http://ploverdata.org], [the spaCy
natural language processing system](https://spacy.io/), and Python [scikit-learn](https://scikit-learn.org/stable/) machine learning package for the SVM.

`spaCy` is used to tokenize the text, then the words are filtered on the following criteria

* character length > 3
* all alphabetic
* not part of a named entity: `spaCy` doesn't always get these correctly
* not in the `spaCy` English-language stop list

The remaining word list is transformed into a tf/idf vector by the [sklearn](https://scikit-learn.org/stable/modules/svm.html) function `TfidfVectorizer` and then a multiclass SVM is estimated using `LinearSVC` with the default values (these are included as comments in the documentation: I have made no efforts to optimize these hyperparameters as the defaults seem to be working adequately).

The training cases were developed incrementally using an older corpus using a combination of initially seeding the cases into codeable/not codeable based on whether they had generated events, then, using an earlier variant of the program `FJTYFilt-plovigy.py`, manually classifying about 1000 cases into the various uncodeable categories (again, developed through a couple iterations), and finally "bootstrapping" additional training cases based on classifying unknown cases and then manually reviewing these (which is gets to be quite quick since most of the classifications are correct). In March-2020, the new *coivd-19* category was implemented using a couple days of Reuters downloads as proof-of-concept

The current programs are about half-way between research and operational, as the original codebase was from a pipeline for a project that was destined for, but never quite made it to, operational status (happens a lot, eh?). File names and directories are, for the most part, 
hard-coded in the program, but it would be relatively straightforward to replace these with command-line options (see, for 
example, those implemented in `FJTYFilt_make_wordlists.py` and `FJTYFilt_evaluate.py`) so they could be used in a scripted pipeline. Error-checking, for example for missing files and input producing out-of-range list indices, has been only partially implemented.


Filter modes
============

The system is configured to use the following scheme:

0. codeable
1. sports
2. culture and entertainment
3. business and finance
4. opinion
5. crime
6. accidents
7. natural disaster
8. [open: current sample uses COVID-19]
9. no codeable content: typically links and other non-language records; the corpus from which the initial training cases were derived had quite a bit of this sort of content.

A number of training cases have been provided in the file `FJTY_training_wordlists.zip`. These produce the following performance

```
SVM_FILTER_ESTIMATE.PY TRAIN/TEST RESULTS
Run datetime: 20-03-11 10:10:04
Training cases proportion: 0.330
Training files
FILE_PATH: ../FJML-Filter/FJTY_training_wordlists
  SportOne-wordlists.jsonl
  CultTwo-wordlists.jsonl
  BusFinThree-wordlists.jsonl
  OpinFour-wordlists.jsonl
  CrimeFive-wordlists.jsonl
  AcciSix-wordlists.jsonl
  WeathrSeven-wordlists.jsonl
  CovidEight-wordlists.jsonl
  JunkNine-wordlists.jsonl
  list0215-wordlists.jsonl
  list0218-wordlists.jsonl

       ============ Experiment 1 ============
Time to estimate: 0.062 sec
Training set
0 |  136     0     0     1     0     0     0     0     0     0    99.27
1 |    0   152     0     0     0     0     0     0     0     0    100.00
2 |    0     0    64     0     0     0     0     0     0     0    100.00
3 |    0     0     0    89     0     0     0     0     2     0    97.80
4 |    1     0     0     0     7     0     0     0     0     0    87.50
5 |    1     0     0     0     0     5     0     0     0     0    83.33
6 |    0     0     0     0     0     0     6     0     0     0    100.00
7 |    0     0     0     0     0     0     0    12     0     0    100.00
8 |    0     0     0     0     0     0     0     0    37     0    100.00
9 |    2     0     0     0     0     0     0     0     0    34    94.44

Time to fit 1070 cases 0.145 sec
Test set
              codeable |  252     1     3    12     0     0     0     1     4     0    273 ( 25.51%)   92.31%   92.31%
                sports |    4   265     2     1     0     0     0     0     0     0    272 ( 25.42%)   97.43%   98.53%
 culture/entertainment |   20     4   117     4     0     0     0     0     0     0    145 ( 13.55%)   80.69%   86.21%
      business/finance |   19     1     8   149     0     0     0     0    14     1    192 ( 17.94%)   77.60%   90.10%
               opinion |    7     0     2     2     1     0     0     0     0     0     12 (  1.12%)    8.33%   41.67%
                 crime |   10     1     2     1     0     3     0     0     0     0     17 (  1.59%)   17.65%   41.18%
             accidents |    9     0     1     1     0     0     3     0     0     0     14 (  1.31%)   21.43%   35.71%
      natural disaster |    1     0     0     0     0     0     0    17     0     0     18 (  1.68%)   94.44%   94.44%
       open [covid-19] |    0     0     0    11     0     0     0     0    48     0     59 (  5.51%)   81.36%  100.00%
   no codeable content |   15     0     1     1     0     0     0     0     0    51     68 (  6.36%)   75.00%   77.94%

```
So, obviously, quite a few additional cases are needed in the `opinion` and `crime` categories, and `business/finance` and `accidents` could use some work as well. These additional cases can be generated from labelled cases using the `FJTYFilt_make_wordlists.py` program.


Prerequisites
=============

1. `spaCy` and the relevant routines from `sklearn` need to be installed.

2. `FJTYFilt_make_wordlists.py` and `FJTYFilt-plovigy.py` both use stories (not sentences) in the PLOVER data exchange (PDE) format: as usual, the easiest way to grok this is just look
at the sample cases in *demo-REUT-20-02-25-wordlists.jsonl*

Programs
========

All programs are Python 3.7 and open source under the MIT License. The programs have been run in both Mac OS-X 10.13 and on the AWS cloud
ca. 2018 and should run without difficulty in any Unix-like environment. 

utilFJML.py
------------
Utility routines for the FJOLTYNG-ML system: the primary routine used from this is `utilFJML.read_file`, which is a generic
routine for reading expanded *.jsonl* files; a couple date-time routines are also used.


FJTYFilt_make_wordlists.py
----------------------------------
Reads a stories file in PDE format, filters to get rid of stop words and other likely non-words, then writes a
list of the remaining words as a space-delimited string (per requirements of the sklearn SVM routines) to a PDE filename with "-wordlists" 
replacing "-stories". 

#### TO RUN PROGRAM: 

`python3 FJTYFilt_wordlists_from_stories.py <-f filename> <-c filename> <-o filename>`

where 

* `-f`: read a simple list of file names, one name per line
* `-c`: read a list of file names from the *FJTY.plovigy.filerecs.txt* output of `FJTY.plovigy.py`, so the file name is the fourth item in
    a space-limited string
* `-o`: output file name; otherwise this is based on name of first input file


FJTYFilt_estimator.py
---------------------
Estimate and save models using the `sklearn` modules: input and output formats are hard coded.

* TEST_RESULT_FILE_NAME = "SVM_test_results.txt"  (saves a copy of the train/test results)
* VECTORZ_PFILE_NAME = "save.vectorizer-Mk2.p"  (pickled vectorizer)
* MODEL_PFILE_NAME = "save.lin_clf-Mk2.p" (pickled SVM)

The program first does N_EXPERIMENTS (currently set at 5) train/test experiments at a [possibly excessively conservative] 1:2 ratio (that is, model is estimated on one-third of the cases and tested on the remaining two-thirds): these results are shown on the screen and saved in the file *TEST_RESULT_FILE_NAME*. The model which is saved is estimated using all of the cases, so the experimental accuracy is likely lower than the operational accuracy.

A classification matrix is displayed, followed by these percentages:

* category as a percent of all cases
* accuracy in classifying the category (main diagonal entry/total)
* accuracy in classifying the category as codeable or not (1 - (category-0/total))


FJTYFilt_evaluate.py
--------------------
This program classifies new cases: it reads pickled files for a vectorized and model that were generated by `FJTYFilt_estimator.py` then classifies case-word vectors from the file `INPUT_FILE_NAME` which was generated by `FJTYFilt_make_wordlists.py`. Predicted values and the case `id` and `title` is written to screen and a file `OUTPUT_PREFIX + "." + str(MODE)/all + ".urls.txt"`. A later program presumably specific to the formats used in your own project can then be used to merge these based on the `id` field.

Output file has the form
```
{'mode': '0-codeable', 'id': 'REUT-2020-02-25-idUSKCN20J0HS', 'title': 'Malaysian king to meet all lawmakers to decide the next PM'}
{'mode': '8-[open]', 'id': 'REUT-2020-02-25-idUSKCN20J0HH', 'title': 'China aviation regulator says flights outside of Hubei to resume gradually'}
{'mode': '3-business/finance', 'id': 'REUT-2020-02-25-idUSKCN20J03L', 'title': 'Asian currencies arrest slide as easing expectations stall dollar'}
```

#### TO RUN PROGRAM: 

`python3 FJTYFilt_evaluate.py [optional command pairs]`

Example for filtering sport stories:
```
FJTYFilt_evaluate.py m -1
```
Command options occur in pairs `-option value`. 

* `-m MODE`: select a single mode; otherwise all modes will be included
* `-wf INPUT_FILE_NAME` : name of the wordlist file of unlabelled vectors to be classified. Default: hard-coded name in program
* `-fp OUTPUT_PREFIX`   : prefix for the file which lists of the urls that were predicted as being MODE. Default: "Mode"
* `-sp STORY_PREFIX`    : prefix for file of stories for the cases that were predicted as being MODE: this is used when manually reviewing the classifications. Default: do not write file
* `-sf STORY_FILE_NAME` : name of .stories.txt file used to generate the unlabelled vectors. Required if `-sp` is used
* `-wp WORDLIST_PREFIX` : prefix for file of wordlists for the cases that were predicted as being MODE:  this is used when these cases will be added to a training set. Default: do not write file

The options beyond `-m` were used in an earlier pipeline and I've not tested them for the revised version.

Supporting files
================

FJTY_training_wordlists.zip
---------------------------
Set of training cases: most of these are mode-specific; the remaining two are a mixed set.


FJTY_SVM_Models.zip
--------------------
Estimated SVM models: `FJTYFilt_evaluate.py` is currently set to use these


demo-REUT-20-02-25-wordlists.jsonl
----------------------------------
Sample input for `FJTYFilt_evaluate.py`



*prodigy* and other classification utilities
============================================

An article on machine learning in [*The Economist*](https://www.economist.com/technology-quarterly/2020/01/02/chinas-success-at-ai-has-relied-on-good-data) in late 2019 made the interesting observation that China's success in this area rests
not on new algorithms&mdash;Chinese machine learning enterprises use the same tools and techniques everyone else uses&mdash;but on China's ability to quickly and inexpensively 
generate very large numbers of labelled training cases: an entire industry has arisen in China to do this.

This is also the insight behind the [explosion.ai](https://explosion.ai/) program [`prodigy`](https://prodi.gy/): enable a user or small team to rapidly 
label/classify training cases. And without the inconveniences of market authoritarianism.  `prodigy` is proprietary software but explosion.ai has certainly made far more than their share of contributions 
to open source&mdash;`spaCy` for godsakes!&mdash;and this is a place where the investment might be well worthwhile. The key contribution of
`prodigy` is the integration of a machine-learning algorithm which, well, "learns" the correct classification of your cases, so pretty
soon you are simply approving its decisions rather than having to think: this allows classification to go *very* fast.

The `FJTYFilt-plovigy.py` program below is an alternative way of doing this&mdash;it has a very small footprint, is keyboard based, and works well on 
airplanes&mdash;but does not have the machine learning component. If you are going to be doing a lot of labelling, notably in the development
of new categories, I'd recommend `prodigy`. You will need to write a couple programs (and if so, *please, please* post them to this repo!) 
to go between the PDE and `prodigy` formats&mdash;and also note that `prodigy` uses the term "jsonl" to refer to a file with one JSON 
record per line, not the more expansive and human-readable format used in this project&mdash;but hey, 80% to 90% of data-science is
getting the files correctly formatted, right?

FJTYFilt-plovigy.py
-------------------

This program is a subset of [`plovigy-mark.py`](https://github.com/openeventdata/plovigy-mark) which uses the PDE jsonl format and is a low-footprint terminal-based system for classifying discard modes. The program adds a "mode" field of the form `mode_number - mode_text`
(for example "0-codeable", "1-sports",  "2-culture/entertainment") and overwrites the 'parser', 'coder', 'codedDate' and 'codedTime' fields.

#### TO RUN PROGRAM:

`python3 FJTYFilt-plovigy.py filename coder`

where the options are pairs as follows:

* `-f <filename>`:    file to read (required)
* `-c <coder>`:       optional coder identification (defaults to a hard-coded value, e.g. "Parus Analytics"")
* `-a <filename>`:    optional filename for autocoding lists


#### KEYS

* 0-9:        add mode to the record and write     
* +/space:   skip&mdash;typically used when duplicates are recognized
* q:          quit 

#### AUTOCODING 

An autocoding file consists of a set of lines in the format

  `<mode#>-<mode_text>: <comma delimited list of phrases>`
  
#### Example:
```
0-codeable-auto: Trump, Xi, WHO
8-covid-19: coronavirus, covid-19, COVID-19
3-gold-prices: Gold prices
````

Autocoding checks the first `AUTO_WINDOW` characters in the text and if a phrase (these are case-sensitive) is found, the `mode` is set to `<mode_number>-<mode_text>` 
and the record is written without pausing. The lists are checked in order, so for example a text "Xi said China had the coronavirus
under control" would have a mode of `0-codeable-auto`, not `8-covid-19`.

#### PROGRAMMING NOTES:

1. The file FILEREC_NAME keeps track of the location in the file, output file name (which has a date-time suffix) and other information.

2. Output file names replaces "-stories" with "-labelled" and adds a date-time-stamp

3. Key input is not case-sensitive

4. With the current settings, the program uses a window 148W x 48H, measured in *characters* (not pixels)

4. Currently the program is using integers for the mode, which obviously restricts these to 10 in number. It is easy to 
   modify this to use other one-key alternatives, e.g. A, B, C,..., or if you are using a keypad, +, -, *, ... and then
   change the `FJTYFilt_estimator.py` program to adjust for this.
   
5. AUTO_WINDOW is currently a constant but it would be easy to modify the program so this could be set in the autofile lists,
   e.g. something like
   
```
0-codeable-auto: 128: Trump, Xi, WHO
8-covid-19: 256: coronavirus, covid-19, COVID-19
3-gold-prices: 32: Gold prices
```

prodigy2plover.py
-----------------
Your file here!

plover2prodigy.py
-----------------
Your file here!



