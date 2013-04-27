'''
Created on Mar 21, 2013

@author: aiman.najjar

This script scans a factored phrase table and generate CSV training data 
that can be used to train a "harmoinizer" classifier 

USAGE: python extract-data.py phrase-table


'''
import logging
import sys
import gzip
import os
import re

if __name__ == '__main__':

    logging.basicConfig(level=logging.ERROR)

    # Validate arguments
    arglist = sys.argv 
    if len(arglist) < 2:
        print "Usage: extract-data.py phrase-table"
        sys.exit(1) #exit interpreter

    phrase_table_filename = arglist[1]

    # Load phrase table in memory
    # We will load only interesting entries, entries that has
    # multi-token phrases in the source side will be skipped
    phrase_table = dict()
    for line in gzip.open(phrase_table_filename, 'rb'):
        
        (source,target, score1, score2, score3) = line.split("|||")
        source = source.strip()
        target = target.strip()
        score1 = score1.strip()
        score2 = score2.strip()
        score3 = score3.strip()

        if source.strip().count(" ") > 0:
            continue

        if target not in phrase_table:
            phrase_table[target] = []

        (lemma, features_vector) = source.split("|")
        (pos, features) = features_vector.split(",")

        phrase_table[target].append( (lemma,pos,features) )


    # We will build this data using the factored phrase table
    # key is a lemma
    # value is a list of entries where each entry is this tuple
    #   (pos, feature_vector, classification)
    # classification is a binary class (true or false)
    training_data = dict()

    for phrase in phrase_table:
        
        lemmas = dict()

        for entry in phrase_table[phrase]:
            (lemma, pos, features) = entry
            # print "%s:\t%s" % (phrase, lemma)

            if lemma not in lemmas:
                lemmas[lemma] = []

            # Third element in tuple marks whether the lemma with these features and pos should be collapsed
            # It is set to False initially, then we check to see whether the lemma was repated for the same phrase
            lemmas[lemma].append( [pos,features,False, phrase] ) 

            # Identify repeated lemmas (ones that can be collapsed)
            for lemma_entry in lemmas[lemma]:
                should_collapse = False

                if len(lemmas[lemma]) > 1:
                    should_collapse = True

                lemma_entry[2] = should_collapse

        # Add new data to overall training data
        for lemma in lemmas:
            if not lemma in training_data:
                training_data[lemma] = dict()

            # In some cases: multiple entries with same lemma, pos,features            
            # are found but with both True and False should_collapse values.
            # In such case, we insert this entry only once in training_data and
            # we set should_collapse to True.
            for lemma_entry in lemmas[lemma]:
                pos = lemma_entry[0]
                features = lemma_entry[1]
                collapse = lemma_entry[2]
                phrase = lemma_entry[3]

                if pos not in training_data[lemma]:
                    training_data[lemma][pos] = dict()

                if features not in training_data[lemma][pos]:
                    training_data[lemma][pos][features] = (collapse, phrase)                    
                elif not training_data[lemma][pos][features] and collapse: 
                    training_data[lemma][pos][features] = (collapse, phrase)

                


    ## Export training data
    for lemma in training_data:
        for pos in training_data[lemma]:
            for features in training_data[lemma][pos]:
                (collapse,phrase) = training_data[lemma][pos][features]
                print '%s,%s,%s,%s' % (collapse,lemma.replace(",", "_"),pos,','.join(re.findall('..',features)))



