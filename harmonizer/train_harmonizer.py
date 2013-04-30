'''
Created on Mar 21, 2013

@author: aiman.najjar

This script trains a harmoinizer model given CSV training data file

When "train-with-lemmas" is set, lemmas will be used as additional 
features to train the binary classifier. If you do not wish to use 
lemmas do not pass any value to the argument

The CSV training data file should be of this format

   Label,Lemmma,POS,Comma-separated List of Other Features

* Label: Can be either True or False - strictly, where True means collapsible
         and false means non-collapsible
* Comma-separated list of other featurees: Can include any number of features
    such as morphological features, number of features must be consistent
    across samples


'''
import logging
import sys
import gzip
import os
import re
import argparse
import numpy as np
import cPickle
from sklearn import svm

if __name__ == '__main__':

    logging.basicConfig(level=logging.ERROR)

    parser = argparse.ArgumentParser(description='Given a CSV training data, this script trains ' +
                                                 'a binary classifier to label collapsible and ' +
                                                 'non-collapsible tokens',
                                    epilog="Aiman Najjar, Columbia Unviersity <an2434@columbia.edu>")

    parser.add_argument('csv_file', metavar='CSV_FILE', type=argparse.FileType('r'),
                       help='The comma-separated training data file')

    parser.add_argument('--out', '-o', metavar='OUTPUT_MODEL', type=argparse.FileType('wb'),
                        default=sys.stdout, required=True, help='Location to save trained model at')

    parser.add_argument('--train-lemmas', '-l', dest="train_lemmas", choices=['Y', 'N'], default='N',
                        metavar="TRAIN_LEMMAS", help="Specifies whether lemmas should be used as features " +
                                                     "when training the classifier model")

    args = parser.parse_args()

    no_lemmas = (args.train_lemmas == "N")


    # First pass on data:
    # Map string values to numerical values
    # This is needed for the SVM library to work  
    features_keys = dict() # Maps string to number
    key_id = 0    
    for line in args.csv_file:
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


    # Second pass on data:
    # Construct features vectors and corresponding labels array
    features = [] # Features vectors 
    labels = []  # Labels (Collapsible = 1, Non-collapsible = 0)

    csv_file.seek(0)
    for line in args.csv_file:

        # Parse training sample
        fields = line.split(",")
        label = fields[0]        
        if label == "True":
            label = 1
        else:
            label = 0

        # -------------------------------------
        # Build features vector for this sample
        feature_vectors = []

        # If lemmas are used as features, we start from column 1
        # otherwise we start from column 2
        first_feature_idx = 1
        if no_lemmas:
            first_feature_idx = 2

        # Iterate through features and append them to the features vector
        for i in range(first_feature_idx,len(fields)):
            feature_val = fields[i].strip()
            feature_numerical_val = int(features_keys[feature_val])
            feature_vectors.append(feature_numerical_val)
        

    	print "Training %s" % feature_vectors

        features.append(np.array(feature_vectors))
        labels.append(label)


    # Convert to numpy arrays (needed for SVM lib)
    X = np.array(features)
    y = np.array(labels)


    # Begin classifier training
    if not no_lemmas:
        print "Training with Lemmas..."
    else:
        print "Training without Lemmas..."
    clf = svm.SVC()
    clf.fit(X,y)

    # Dump model on disk (pickle)
    model = { "features_dict": features_keys, "classifier":clf, "no_lemmas":no_lemmas}
    with args.out as fid:
        cPickle.dump(model, fid)    

    # Done
    print "Done. Saved model on disk"
        



