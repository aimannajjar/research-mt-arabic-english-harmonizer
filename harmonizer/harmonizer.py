'''
Created on Mar 21, 2013

@author: aiman.najjar

This script harmonizes an annotated corpus based on a harmonizer model
The harmonizer model can be trained using train_harmonizer script

USAGE: python harmonizer.py model-file annotated-corpus 

The corpus must be annotated as such:
Each line represents a sentence, words are spearated by spaces and each 
word is represented in the following form:

  surface form|lemma|pos,morphological_features


'''

import sys
import re
import cPickle
import numpy as np
from sklearn import svm
from sklearn.svm import LinearSVC

SKIP_UNSEEN_LEMMAS = True

def main(argv):  


  # Validate and parse arguments
  arglist = sys.argv 
  if len(arglist) < 2:
      print "Usage: harmonizer.py model-file annotated-corpus"
      sys.exit(1) 

  harmonizer_model_filename = arglist[1]
  corpus_filename = arglist[2]

  # Read model from disk
  with open(harmonizer_model_filename, 'rb') as fid:
      model = cPickle.load(fid)

  features_dict = model["features_dict"]
  classifier = model["classifier"]
  no_lemmas = model["no_lemmas"]
  
  # Iterate through sentences
  for line in open(corpus_filename, 'rb'):

    harmonized_sentence = "" 

    # Iterate through words in sentence
    words_in_sentence = line.split(" ")    
    for word in words_in_sentence:

        
        (surface, lemma, features_vector) = word.split("|")
        (pos, features) = features_vector.split(",")
        features_array = re.findall('..', features)

        features_vector = []
        if not no_lemmas:
          if lemma not in features_dict and SKIP_UNSEEN_LEMMAS:
            harmonized_sentence = harmonized_sentence + surface + " "
            continue
          elif lemma not in features_dict and not SKIP_UNSEEN_LEMMAS:
            features_vector.append(int(features_dict["na"]))  
          else:
            features_vector.append(int(features_dict[lemma]))

        if pos.strip() in features_dict:
          features_vector.append(features_dict[pos.strip()])
        else:
          features_vector.append(int(features_dict["na"]))

        for feature in features_array:
          if feature.strip() in features_dict:
            feature_val = int(features_dict[feature.strip()])
          else:
            feature_val = int(features_dict["na"])
          features_vector.append(feature_val)

        features_vector_np = np.array(features_vector)
        
        if classifier.predict(features_vector_np)[0] == 1:
          harmonized_sentence = harmonized_sentence + lemma + "$$ "
        else:
          harmonized_sentence = harmonized_sentence + surface + " "
        
    print harmonized_sentence


if __name__ == '__main__':
  main(sys.argv)


