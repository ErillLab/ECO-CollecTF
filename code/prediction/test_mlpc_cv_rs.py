from __future__ import print_function
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import GridSearchCV
from sklearn import metrics
from sklearn.externals import joblib

import sys
import os
import math
import numpy as np
import pandas as pd

input_fname = sys.argv[1]
ans_fname = sys.argv[2]
test_fname = sys.argv[3]
true_fname = sys.argv[4]
out_fname = sys.argv[5] # for the saved model

input_df = pd.read_csv(input_fname, sep="\t", index_col=0)
ans_df = pd.read_csv(ans_fname, sep="\t", index_col=0)
one_df = input_df.join(ans_df, how='inner')

#PMID_S	SimpleAssert	MoreAssert	ToPhrase	WrapUp	BI  PG	SF	SP	TaxI    TaxE    ECOScore	ECOID	ECOWords	ECOTextWords	SOScore	SOID	SOWords	SOTextWords	GOBPScore	GOBPID	GOBPWords	GOBPTextWords	GOMFScore	GOMFID	GOMFWords	GOMFTextWords	Sentence
# PMID_S	AnyS	AnyP	MajS	MajP	AnySfS	AnySfP	MajSfS	MajSfP	AnyBPS	AnyBPP	MajBPS	MajBPP	AnyMFS	AnyMFP	MajMFS	MajMFP  AnyTxS	AnyTxP	MajTxS	MajTxP

featuresS1 = ['SimpleAssert', 'ToPhrase', 'WrapUp', 'PG', 'SP', 'ECOScore', 'SOScore', 'GOBPScore', 'GOMFScore']
pred_col = 'AnyS'
#pred_col = 'MajS'
x = one_df[featuresS1]
y = one_df[pred_col]

print(x.shape)
print(y.shape)

# Separate test data
input_dft = pd.read_csv(test_fname, sep="\t", index_col=0)
ans_dft = pd.read_csv(true_fname, sep="\t", index_col=0)
one_dft = input_dft.join(ans_dft, how='inner')
xt = one_dft[featuresS1]
yt = one_dft[pred_col]

print(xt.shape)
print(yt.shape)
a=True
rs_range = [r for r in range(7,101,3)]
rs_range.extend([301, 501, 703, 811, 1017, 11713, 79843])
print (rs_range)

if a:
  #print("\nrandom_state = "+str(rs))
  parameters = {'hidden_layer_sizes':[(5,), (10,), (50,), (100,), (200,)], 'activation':['relu'], 'max_iter':[1000], 'random_state':rs_range}
  clf = GridSearchCV(MLPClassifier(), parameters, cv=10, scoring='precision')
  clf = clf.fit(x, y)
  
  
  print (clf.best_score_, clf.best_params_)

  the_model = clf.best_estimator_
  
  joblib.dump(the_model, out_fname)
  
  #for i in range(len(featuresS1)):
  #  print("Feature importance:", featuresS1[i], the_model.feature_importances_[i])


  y_predt = the_model.predict(xt)
  print("Num pos in y_predt:", y_predt.sum())
  #print("Accuracy:",metrics.accuracy_score(yt, y_predt))
  prec = metrics.precision_score(yt, y_predt)
  print("Precision:",prec)
  print("Recall:",metrics.recall_score(yt, y_predt))

  cm = pd.DataFrame(
    metrics.confusion_matrix(yt, y_predt),
    columns=['Predicted F', 'Predicted T'],
    index=['True F', 'True T']
  )
  print(cm.head)
  
