from __future__ import print_function
from sklearn.neural_network import MLPClassifier
from sklearn import metrics
from sklearn.externals import joblib

import sys
import os
import math
import numpy as np
import pandas as pd

input_fname = sys.argv[1] # the model
test_fname = sys.argv[2]  # test inputs file
print("Num args:", len(sys.argv))
if len(sys.argv) > 3:
  true_fname = sys.argv[3] # test ans key
else:
  true_fname = None

out_fname = os.path.splitext(os.path.basename(input_fname))[0] + "_outS.txt"
print("Output S to", out_fname)

featuresS1 = ['SimpleAssert', 'ToPhrase', 'WrapUp', 'PG', 'SP', 'ECOScore', 'SOScore', 'GOBPScore', 'GOMFScore']
pred_col = 'AnyS'

input_dft = pd.read_csv(test_fname, sep="\t", index_col=0)
if true_fname is None:
  xt = input_dft[featuresS1]
  print(xt.shape)
  print("Do prediction but no scoring of prediction")
else:
  ans_dft = pd.read_csv(true_fname, sep="\t", index_col=0)
  one_dft = input_dft.join(ans_dft, how='inner')
  xt = one_dft[featuresS1]
  yt = one_dft[pred_col]
  print("Do prediction WITH scoring")
  
clf = joblib.load(input_fname)

y_predt = clf.predict(xt)
print("Num pos in y_predt:", y_predt.sum())
#print(y_predt)
i=0
p=0
with open(out_fname, "w") as fpo:
  for idx in xt.index:
    #print(idx, i, y_predt[i])
    if y_predt[i] > 0:
      out_str = idx+"\t"+one_dft.loc[idx, 'Sentence']
      for col in one_dft.columns:
        if not col == 'Sentence':
          out_str+="\t"+str(one_dft.loc[idx, col])
      fpo.write("%s\n" % out_str)

    else:
      s=""
    #print (idx, y_predt[i], s)
    i += 1  

if true_fname is not None:
  #print("Accuracy:",metrics.accuracy_score(yt, y_predt))
  print("Precision:",metrics.precision_score(yt, y_predt))
  print("Recall:",metrics.recall_score(yt, y_predt))
