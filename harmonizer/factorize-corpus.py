'''
Created on Mar 21, 2013

@author: aiman.najjar

This script creates a factored training corpus out out of a MADA analysis file.

USAGE: factorize-corpus.py mada_analysis_file.bw.mada


This will outout will be printed on stdout, you can use direction to store it in a file

The output format will be as follows:
    * Each line represents a sentence

    * Each word will be represented with the following factors:
        surface form|lemma|POS,FEATURE_VECTOR

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
    yrfD|rafaD-u_1|verb,x3xixaxuxmxsnanana


Alif forms  => A
Yaa' and Alif maqsoora => y



'''
import logging
import sys
from util import *



if __name__ == '__main__':

    logging.basicConfig(level=logging.ERROR)

    arglist = sys.argv 
    if len(arglist) < 2:
        print "Usage: python factorize-corpus.py mada_analysis_file"
        sys.exit(1) #exit interpreter

    mada_filename = arglist[1]

    factored_sentence = ""
    sentence = ""
    sentence_id = -1
    for line in open("%s" % mada_filename):


        # Extract analysis for each sentence
        if line.startswith(";;;"):
            if sentence_id >= 0:
                if factored_sentence.strip() != "":
                    print factored_sentence.strip() # print previous sentence analysis
                else:
                    sentence_no_analysis = ""
                    for word in sentence.strip().split(" "):
                        sentence_no_analysis += "%s|%s|%s,%s " % (word, word, "na", "nanananananananana")
                    print sentence_no_analysis.strip()


            # New sentence, reset analysis
            sentence_id = sentence_id + 1
            parts = line.partition(";;; SENTENCE ")
            sentence = parts[2].strip()
            factored_sentence = ""

        elif line.startswith(";;WORD"):
            parts = line.partition(";;WORD ")
            word = normalize_word(parts[2])

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
                    lemma = normalize_word(val)
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
    print factored_sentence.strip() 






