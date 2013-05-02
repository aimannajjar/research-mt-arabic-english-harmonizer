'''
Created on Mar 21, 2013

@author: aiman.najjar

This script creates an annotated training corpus out out of a MADA analysis file.


The output format will be as follows:
    * Each line represents a sentence

    * Each word will be represented with the following factors:
        surface form|lemma|POS,MORPH_FEATURES

    * FEATURE_VECTOR is simply a 18-char string representing the following features
        (in this order):
          Person: [1,2,3,na] # 1 = First, 2 = Second, 3 = Third, na = N/A
          Aspect: [c,i,p,na] # c = Command, i = Imperfective, p = Perfective, na = N/A
          Voice : [a,p,na,u] # a = Active, p = Passive, na = N/A, u = Undefined
          Mood  : [i,j,s,na,u] # i = Indicative, j = Jussive, s = Subjunctive, na = N/A 
          Gender: [f,m,na] # f = Feminine, m = Masculine, na = N/A
          Number: [s,p,d,na,u] # s = Singular, p = Plural, d = Dual, na = N/A, u = Undefined 
          State : [i,d,c,na,u] # i = Indefinite, d = Definite, c = Construct/Poss/Idafa, na = N/A, u = Undefined 
          Case  : [n,a,g,na,u] # n = Nominative, a = Accusative, g = Genitive, na = N/A, u = Undefined
          Rat** : [y,na] # y = yes, n = N/A
     - Each feature will have 2 characters in the string (single-char values will be padded with x)
          
Example output of the word "yrfD":
    yrfD|rafaD|verb,x3xixaxuxmxsnanana




'''
import logging
import sys
import argparse
from util import *


if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Given a MADA analysis file, this scripts ' +
                                                 'crates a corpus annotated with Lemmas and ' +
                                                 'Morpohological features',
                                    epilog="Aiman Najjar, Columbia Unviersity <an2434@columbia.edu>")

    parser.add_argument('mada_file', metavar='MADA_FILE', type=argparse.FileType('r'),
                       help='MADA analysis file (.mada file)')

    parser.add_argument('--out', '-o', metavar='OUTPUT_FILE', type=argparse.FileType('w'),
                        default=sys.stdout, help='Specify to save output on disk', required=True)

    parser.add_argument('--preprocess', '-p', dest="preprocess", nargs="+",
                        choices=['NORM_ALIFS', 'NORM_YAA', 'REMOVE_DIACRITICS', 'REMOVE_WORD_SENSE'],
                        metavar="SCHEME", help="Pre-processing schemes to applied to tokens during annotation: " + 
                             "'NORM_ALIFS', 'NORM_YAA', REMOVE_DIACRITICS', 'REMOVE_WORD_SENSE'")

    args = parser.parse_args()

    logging.basicConfig(level=logging.ERROR)


    factored_sentence = ""
    sentence = ""
    sentence_id = -1
    print "Pre-processing schemes: %s" % args.preprocess
    print "Annotating sentences"
    for line in args.mada_file:


        # Extract analysis for each sentence
        if line.startswith(";;;"):
            if sentence_id >= 0:
                if factored_sentence.strip() != "":
                    if len(factored_sentence.split(" ")) != len(sentence.strip().split(" ")):
                        print "WARNING: Mismatch in number of tokens of annotated sentence (%d != %d)" % \
                                (len(factored_sentence.split(" ")), len(sentence.strip().split(" ")))
                        print "Source sentence: %s" %  sentence.strip()
                        print "Annotated sentence: %s" %  factored_sentence.strip()

                    args.out.write(factored_sentence.strip() + "\n") # print previous sentence analysis
                else:
                    sentence_no_analysis = ""
                    for word in sentence.strip().split(" "):
                        sentence_no_analysis += "%s|%s|%s,%s " % (word, word, "na", "nanananananananana")

                    args.out.write(sentence_no_analysis.strip()+"\n")

                if ( (sentence_id + 1) % 1000) == 0:
                    print "Annotated %d sentences" % (sentence_id+1)



            # New sentence, reset analysis
            sentence_id = sentence_id + 1
            parts = line.partition(";;; SENTENCE ")
            sentence = parts[2].strip()
            factored_sentence = ""

        elif line.startswith(";;WORD"):
            parts = line.partition(";;WORD ")
            word = normalize_word(parts[2], args.preprocess)
        elif line.startswith(";;NO-ANALYSIS"):
            factored_sentence += "%s|%s|%s,%s " % (word, word, "na", "nanananananananana")

        elif line.startswith("*"):
            analysis = line[1:]
            parts = analysis.split(" ")
            parts = parts[1:] # discard first part (probability)

            lemma = ""
            pos = ""
            feature_vector = ""
            clitics = ""
            
            i = 0
            for part in parts:                
                var = part[0:part.index(":")]
                val = part[part.index(":")+1:] .replace("|", "P")

                if var == "lex":
                    lemma = normalize_word(val, args.preprocess)
                elif var.startswith("prc") or var == "enc0":
                    clitics += val + ","
                elif var.startswith("pos"):
                    pos = val
                elif (i >= 9 and i <= 16) or i == 18:
                    if len(val) == 1:
                        val = "x%s" % val
                    feature_vector += val

                i += 1

            clitics = clitics[:len(clitics)-1] # strip trailing comma (,)

            # add this factored word to sentence
            factored_word = "%s|%s|%s,%s " % (word, lemma, pos, feature_vector)
            if factored_word.count("|") != 2:
                sys.stderr.write("ERROR: Found %d |'s in  word, expected 2: %s (lemma: %s)\n"  % (factored_word.count("|"), factored_word, lemma))
                sys.exit()


            factored_sentence += "%s|%s|%s,%s " % (word, lemma, pos, feature_vector)
        
        
    # print last sentence analysis
    args.out.write(factored_sentence.strip()+"\n")
    print "Done"






