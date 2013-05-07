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
import argparse
import cPickle
import numpy as np
from sklearn import svm
from sklearn.svm import LinearSVC
from util import *

SKIP_UNSEEN_LEMMAS = False

def main(argv):  


  parser = argparse.ArgumentParser(description='Given a harmonizer model and a source-language file, ' +
                                               'this scripts generates a target-language that is more harmonized ' +
                                               'with target language',
                                  epilog="Aiman Najjar, Columbia Unviersity <an2434@columbia.edu>")

  parser.add_argument('model_file', metavar='MODEL', type=argparse.FileType('r'),
                     help='The trained harmonizer model file')

  parser.add_argument('corpus_file', metavar='CORPUS', type=argparse.FileType('r'),
                     help='Annotated corpus from which to generate harmonized corpus')

  parser.add_argument('--out', '-o', metavar='OUTPUT_CORPUS', type=argparse.FileType('wb'),
                      default=sys.stdout, help='Location to save harmonized corpus', required=True)


  parser.add_argument('--preprocess', '-p', dest="preprocess", nargs="+",
                      choices=['NORM_ALIFS', 'NORM_YAA', 'REMOVE_DIACRITICS', 'REMOVE_WORD_SENSE'],
                      metavar="SCHEME", help="Pre-processing schemes to applied to tokens before classification, " +
                           "must be consisted with schemes used when model was trained: " +
                           "'NORM_ALIFS', 'NORM_YAA', REMOVE_DIACRITICS', 'REMOVE_WORD_SENSE'")


  parser.add_argument('--verbose', '-v', action='store_true',
                      help='Verbose output, helpful to debug')


  args = parser.parse_args()

  # Read model from disk
  with args.model_file as fid:
      model = cPickle.load(fid)

  features_dict = model["features_dict"]
  classifier = model["classifier"]

  no_lemmas = True
  if "no_lemmas" in model:
    no_lemmas = bool(model["no_lemmas"])
  
  if no_lemmas == True:
    print "Harmonizer loaded. Lemmas were not used to train this model"
  else:
    print "Harmonizer loaded. Lemmas were used to train this model"

  line_no = 0
  # Iterate through sentences
  for line in args.corpus_file:

    harmonized_sentence = "" 

    # Iterate through words in sentence
    words_in_sentence = line.split(" ")    
    for word in words_in_sentence:

        
        (surface, lemma, features_vector) = word.split("|")
        (pos, features) = features_vector.split(",")
        features_array = re.findall('..', features)

        lemma = normalize_word(lemma, args.preprocess)

        features_vector = []
        features_vector_strings = []
        if not no_lemmas:
          if lemma not in features_dict and SKIP_UNSEEN_LEMMAS:
            harmonized_sentence = harmonized_sentence + surface + " "
            continue
          elif lemma not in features_dict and not SKIP_UNSEEN_LEMMAS:
            features_vector.append(int(features_dict["na"]))
            features_vector_strings.append("na")
          else:
            features_vector.append(int(features_dict[lemma]))
            features_vector_strings.append(lemma)

        if pos.strip() in features_dict:
          features_vector.append(int(features_dict[pos.strip()]))
          features_vector_strings.append(pos.strip())
        else:
          features_vector.append(int(features_dict["na"]))
          features_vector_strings.append("na")

        for feature in features_array:
          if feature.strip() in features_dict:
            feature_val = int(features_dict[feature.strip()])
            features_vector_strings.append(feature.strip())
          else:
            feature_val = int(features_dict["na"])
            features_vector_strings.append("na")

          features_vector.append(feature_val)

        features_vector_np = np.array(features_vector)

        if args.verbose:
          print "Classifying %s" % lemma
          print "Features: %s" % features_vector_strings
        
        if classifier.predict(features_vector_np)[0] == 1:
          harmonized_sentence = harmonized_sentence + lemma + "$$ "
          if args.verbose:
            print "Label: Collapisble"
        else:
          harmonized_sentence = harmonized_sentence + surface + " "
          if args.verbose:
            print "Label: Non-Collapisble"

        if args.verbose:
          print ""
    
    line_no = line_no + 1

    if (line_no % 1000) == 0:
      print "Harmonized %d sentences" % line_no

    args.out.write(harmonized_sentence.strip() + "\n")
  
  print "Done"    


if __name__ == '__main__':
  main(sys.argv)


