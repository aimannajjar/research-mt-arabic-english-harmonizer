'''
Created on Mar 21, 2013

@author: aiman.najjar

This script trains a harmoinizer model given CSV training data file
Model will be saved on disk under this name: harmonizer_model.pkl

USAGE: python train_harmonizer.py training_data.csv


'''
import logging
import sys
import gzip
import os
import re
import numpy as np
import cPickle
from sklearn import svm
from sklearn.svm import LinearSVC

if __name__ == '__main__':

    logging.basicConfig(level=logging.ERROR)

    arglist = sys.argv 
    if len(arglist) < 2:
        print "Usage: train_harmonizer.py data_file_name.csv [dont-use-lemmas]"
        sys.exit(1) #exit interpreter

    no_lemmas = False
    if len(arglist) > 2:
        no_lemmas = True

    features_keys = dict()
    key_id = 0
    data_filename = arglist[1]
    data_size = 0

    for line in open(data_filename, 'rb'):
        data_size = data_size + 1
        fields = line.split(",")
        label = fields[0]        

        first_feature_idx = 1
        if no_lemmas:
            first_feature_idx = 2

        for i in range(first_feature_idx,len(fields)):
            feature_val = fields[i].strip()
            if feature_val not in features_keys:
                features_keys[feature_val.strip()] = key_id
                key_id = key_id + 1

    features = []  ## Features vectors 
    labels = []  ## Labels for each sample

    for line in open(data_filename, 'rb'):
        fields = line.split(",")
        label = fields[0]        

        if label == "True":
            label = 1
        else:
            label = 0

        feature_vectors = []
        feature_vectors_names = []

        first_feature_idx = 1
        if no_lemmas:
            first_feature_idx = 2

        for i in range(first_feature_idx,len(fields)):
            feature_val = fields[i].strip()
            feature_vectors_names.append(feature_val)
            feature_vectors.append(int(features_keys[feature_val]))

        features.append(np.array(feature_vectors))
        labels.append(label)

    X = np.array(features)
    y = np.array(labels)

    if not no_lemmas:
        print "Training with Lemmas..."
    else:
        print "Training without Lemmas..."
    # clf = svm.SVC()
    clf = LinearSVC()
    clf.fit(X,y)

    model = { "features_dict": features_keys, "classifier":clf}

    with open('harmonizer_model.pkl', 'wb') as fid:
        cPickle.dump(model, fid)    

    print "Done. Saved harmonizer_model.pkl"
        
