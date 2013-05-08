'''
Created on Mar 21, 2013

@author: aiman.najjar

This script scans a factored phrase table and generate CSV training data 
that can be used to train a "harmoinizer" classifier 


'''
import logging
import sys
import gzip
import os
import re
import argparse
from util import *

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Given a phrase table, this scripts ' +
                                                 'training data that can be used to train a ' +
                                                 'harmonizer',
                                    epilog="Aiman Najjar, Columbia Unviersity <an2434@columbia.edu>")

    parser.add_argument('phrase_table', metavar='PHRASE_TABLE',
                       help='Phrase table file in compressed format')

    parser.add_argument('--out', '-o', metavar='OUTPUT_FILE', type=argparse.FileType('w'),
                        default=sys.stdout, help='Where to save the generated CSV file', required=True)

    parser.add_argument('--score-threshold', '-t', metavar='SCORE_THRESHOLD', type=float,
                        default=0.0, help='Minimum average score threshold for entries to be considered')


    parser.add_argument('--preprocess', '-p', dest="preprocess", nargs="+",
                        choices=['NORM_ALIFS', 'NORM_YAA', 'REMOVE_DIACRITICS', 'REMOVE_WORD_SENSE'],
                        metavar="SCHEME", help="Pre-processing schemes to applied to tokens during data extraction: " + 
                             "'NORM_ALIFS', 'NORM_YAA', REMOVE_DIACRITICS', 'REMOVE_WORD_SENSE'")


    args = parser.parse_args()

    logging.basicConfig(level=logging.ERROR)

    # Load phrase table in memory
    # We will load only interesting entries, entries that has
    # multi-token phrases in the source side will be skipped
    print "Loading phrase table in memory"
    print "Pre-processing schemes: %s" % args.preprocess
    line_no = 0
    phrase_table = dict()
    total_skipped = 0 
    total_considered = 0
    for line in gzip.open(args.phrase_table, 'rb'):
        
        (source,target, scores, alignments, scores2) = line.split("|||")
        source = source.strip()
        target = target.strip()
        scores = scores.strip()
        alignments = alignments.strip()
        scores2 = scores2.strip()

        if source.strip().count(" ") > 0:
            continue

        # Compute score average
        (inv_phrase_prob, inv_lex_prob, phrase_prob, lex_prob, penalty) = scores.split(" ")
        inv_phrase_prob = float(inv_phrase_prob.strip())
        inv_lex_prob = float(inv_lex_prob.strip())
        phrase_prob = float(phrase_prob.strip())
        lex_prob = float(lex_prob.strip())
        avg_score = (inv_phrase_prob + inv_lex_prob + phrase_prob + lex_prob) / 4.0
        total_considered = total_considered + 1
        if avg_score < args.score_threshold:
            total_skipped = total_skipped + 1
            continue

        key = lemma + "|||" + target
        if  key not in phrase_table:
            phrase_table[key] = []

        (lemma, features_vector) = source.split("|")
        (pos, features) = features_vector.split(",")

        phrase_table[key].append( (normalize_word(lemma, args.preprocess),pos,features) )
        
        line_no = line_no + 1
        if (line_no % 10000) == 0:
            print "Loaded %d entries" % line_no

    print "Phrase table loaded"
    print "%d/%d entries were skipped for having too low scores" % (total_skipped, total_considered)



    # We will build this data using the factored phrase table
    # key is a lemma
    # value is a list of entries where each entry is this tuple
    #   (pos, feature_vector, classification)
    # classification is a binary class (true or false)
    print "Extracting harmonization data"
    training_data = dict()

    for key in phrase_table:

        (source_lemma, target_phrase) = key.split("|||")

        should_collapse = False

        if len(phrase_table[key]) > 1:
            should_collapse = True

        for entry in phrase_table[key]:
            (lemma, pos, features) = entry

            if lemma not in training_data:
                training_data[lemma] = dict()

            if pos not in training_data[lemma]:
                training_data[lemma][pos] = dict()

            if features not in training_data[lemma][pos]:
                training_data[lemma][pos][features] = (should_collapse, target_phrase)                    


    print "Data extracted. Generating CSV file"
    ## Export training data
    for lemma in training_data:
        for pos in training_data[lemma]:
            for features in training_data[lemma][pos]:
                (collapse,phrase) = training_data[lemma][pos][features]
                args.out.write('%s,%s,%s,%s\n' % (collapse,lemma.replace(",", "_"),pos,','.join(re.findall('..',features))))

    print "Done"


