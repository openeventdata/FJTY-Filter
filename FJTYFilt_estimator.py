"""
FJTYFilt_estimator.py

Creates a vectorizer and estimated an SVM model from the files in FILE_NAMES; run a TRAIN_PROP train/test on these  
then saves these  

TO RUN PROGRAM:

python3 SVM_filter_estimate.py 


PROGRAMMING NOTES:

1. There are no summary statistics across the experiments, as these are currently just eyeballed to make sure nothing is 
   badly out of line.
   

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
16-Jan-17:	Initial version
31-Jan-17:	modified to save vectorizer and model, clean up output
02-Jan-17:	cmd-line for file list; save estimates
05-Mar-19:  modified from SVM_filter_estimate.py for FJ project

=========================================================================================================
"""

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from time import time
import datetime
import utilFJML
import pickle
import random
import os

N_EXPERIMENTS = 5
TRAIN_PROP = 0.33   # proportion of cases in the training file.

INPUT_FILELIST = "filt-estimator-filelist.txt"
FILE_PATH = "../FJML-Filter/FJTY_training_wordlists"
FILE_NAMES = [line[:-1] for line in open(INPUT_FILELIST, "r")]

LABELS = ["codeable", "sports", "culture/entertainment", "business/finance", "opinion", "crime", "accidents", 
        "natural disaster", "open", "no codeable content"]

TEST_RESULT_FILE_NAME = "SVM_test_results-"
VECTORZ_PFILE_NAME = "save-vectorizer-Mk2.p"
MODEL_PFILE_NAME = "save-lin_clf-Mk2.p"

N_MODE = 10  # maximum number of unique modes

random.seed()
# Evaluate the model 

suffix = utilFJML.get_timed_suffix()
fout = open(TEST_RESULT_FILE_NAME + suffix + ".txt", 'w')
fout.write("SVM_FILTER_ESTIMATE.PY TRAIN/TEST RESULTS\nRun datetime: {:s}\n".format(datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')))
fout.write("Training cases proportion: {:0.3f}\nTraining files\n".format(TRAIN_PROP))
fout.write("FILE_PATH: " + FILE_PATH + "\n")
for stnm in FILE_NAMES:
    fout.write("  " + stnm + '\n')

for kex in range(N_EXPERIMENTS):
    fout.write("\n       ============ Experiment {:d} ============\n".format(kex + 1))    
    Y = []
    corpus = []
    Ytest = []
    testcase = []

    for filename in FILE_NAMES:
        reader = utilFJML.read_file(os.path.join(FILE_PATH, filename))
        print("Reading", FILE_PATH + filename)
        for krec, rec in enumerate(reader):
            if random.random() < TRAIN_PROP:
                Y.append(int(rec['mode'][0]))
                corpus.append(rec['textInfo']['wordlist'])
            else:
                Ytest.append(int(rec['mode'][0]))
                testcase.append(rec['textInfo']['wordlist'])

    vectorizer = TfidfVectorizer(min_df=1)
    tfidf2 = vectorizer.fit_transform(corpus)
    X = tfidf2.toarray()

    t0 = time()
    lin_clf = svm.LinearSVC()
    lin_clf.fit(X, Y) 
    print("Time to estimate: {:0.3f} sec".format(time() - t0))
    fout.write("Time to estimate: {:0.3f} sec\n".format(time() - t0))
    """LinearSVC(C=1.0, class_weight=None, dual=True, fit_intercept=True,
         intercept_scaling=1, loss='squared_hinge', max_iter=1000,
         multi_class='ovr', penalty='l2', random_state=None, tol=0.0001,
         verbose=0)"""
    #dec = lin_clf.decision_function([[1,1]])
    kcorr = 0
    classmat = []
    for ka in range(N_MODE):
        classmat.append(N_MODE*[0])
    for ka, xv in enumerate(X):
        pred = lin_clf.predict([xv])
        classmat[Y[ka]][pred[0]] +=1
        if Y[ka] == pred[0]:
            kcorr +=1
    print('Training set')
    fout.write('Training set\n')
    for ka, kv in enumerate(classmat):
        print(ka,end=' | ')
        fout.write(str(ka) + ' | ')
        tot = 0
        for kb, num in enumerate(kv):
            print("{:4d}  ".format(num),end='')
            fout.write("{:4d}  ".format(num))
            tot += num
            if ka == kb:
                main = num
        if tot > 0:
            print('  {:.2f}'.format(float(main*100)/tot))
            fout.write('  {:.2f}\n'.format(float(main*100)/tot))
        else:
            print('  {:.2f}'.format(0.0))
            fout.write('  {:.2f}\n'.format(0.0))

    X_test = vectorizer.transform(testcase).toarray()

    kt = 0
    kcorr = 0
    classmat = []
    for ka in range(N_MODE):
        classmat.append(N_MODE*[0])
    t0 = time()
    for ka, xv in enumerate(X_test):
        kt += 1
        pred = lin_clf.predict([xv])
        classmat[Ytest[ka]][pred[0]] +=1
        if Ytest[ka] == pred[0]:
            kcorr +=1
    print("Time to fit {:d} cases {:0.3f} sec".format(kt, time() - t0))
    fout.write("\nTime to fit {:d} cases {:0.3f} sec\n".format(kt, time() - t0))

    print('Test set')
    fout.write('Test set\n')
    for ka, kv in enumerate(classmat):
        tot = 0
        print("{:>22s} | ".format(LABELS[ka]),end='')
        fout.write("{:>22s} | ".format(LABELS[ka]))
        nnc = 0
        for kb, num in enumerate(kv):
            print("{:4d}  ".format(num),end='')
            fout.write("{:4d}  ".format(num))
            tot += num
            if ka == kb:
                main = num
            if kb != 0:
                nnc += num
                
        if tot > 0:
            print(' {:4d} ({:6.2f}%)  {:6.2f}%'.format(tot,float(tot*100)/kt, float(main*100)/tot), end="")
            fout.write(' {:4d} ({:6.2f}%)  {:6.2f}%'.format(tot,float(tot*100)/kt, float(main*100)/tot))
            if ka == 0:
                print('  {:6.2f}%'.format(float(main*100)/tot))
                fout.write('  {:6.2f}%\n'.format(float(main*100)/tot))
            else:
                print('  {:6.2f}%'.format(float(nnc*100)/tot))
                fout.write('  {:6.2f}%\n'.format(float(nnc*100)/tot))
            
        else:
            print(' ---')
            fout.write(' ---\n')
            
fout.close()

print('Saving model using all cases')

Y = []
corpus = []
for filename in FILE_NAMES:
    reader = utilFJML.read_file(os.path.join(FILE_PATH, filename))
    print("Reading", FILE_PATH + filename)
    for krec, rec in enumerate(reader):
        Y.append(int(rec['mode'][0]))
        corpus.append(rec['textInfo']['wordlist'])

vectorizer = TfidfVectorizer(min_df=1)
tfidf2 = vectorizer.fit_transform(corpus)
pickle.dump(vectorizer, open(VECTORZ_PFILE_NAME, "wb"))
X = tfidf2.toarray()

lin_clf = svm.LinearSVC()
lin_clf.fit(X, Y) 
pickle.dump(lin_clf, open(MODEL_PFILE_NAME, "wb"))

print("Finished")
