
import sys
import re
import cPickle
import numpy as np
from sklearn import svm
from sklearn.svm import LinearSVC

SKIP_UNSEEN_LEMMAS = True

def main(argv):  

  arglist = sys.argv 
  if len(arglist) < 3:
      print "Usage: harmonizer.py harmonizer-model corpus [no-lemmas]"
      sys.exit(1) #exit interpreter

  no_lemmas = False
  if len(arglist) > 3:
    no_lemmas = True

  harmonizer_model_filename = arglist[1]
  corpus_filename = arglist[2]


  with open(harmonizer_model_filename, 'rb') as fid:
      model = cPickle.load(fid)

  features_dict = model["features_dict"]
  classifier = model["classifier"]

  
  for line in open(corpus_filename, 'rb'):

    harmonized_sentence = ""
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


