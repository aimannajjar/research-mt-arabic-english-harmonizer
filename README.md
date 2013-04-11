The purpose of this document is to illustrate how to replicate the experiment that I have made and which I was able to improve the BLEU score of a Arabic-English baseline SMT

Environment & Data
-------------------
The experiments described here were done on the following environment:
* Ubuntu 12.04 (64-bit) - We used EC2 instance of type m3.xlarge 
* GIZA 1.0.7
* SRILM 1.5.12
* Moses Decoder - Pulled latest from Github on 4/9/2013
* MADA 3.2 (with SVMTools 1.3.1, aramorph-1.2.1, SRLIM 1.5.12 not patched)
* Python 2.7
* Additional Python Modules: numpy, scikits-learn


**Data**
_____
* Training Data:34k Sentence Pairs (Cleaned)
  > https://dl.dropbox.com/s/agv9khd6mvfa8as/TrainData.zip

* LM Model: 106930 Sentences 
  > https://dl.dropbox.com/s/4wyaebj0dln2xgt/LM_data%2BTrain_data.en.zip


Baseline SMT Training & Evaluation
-----------------------------------

**Training**
______________
Starting from project root directory, run the following:
```
cd SMT/Baseline
mkdir -p work/LM
cp ../../LM_data+Train_data.en.lm work/LM/
$SCRIPTS_ROOTDIR/training/train-model.perl  -external-bin-dir /home/ubuntu/tools/bin \
                                            -root-dir work \
                                            -corpus data/Train/Train_data.clean \
                                            -f ar -e en -alignment grow-diag-final-and \
                                            -reordering msd-bidirectional-fe \
                                            -lm 0:3:/home/ubuntu/workspace/mt-arabic-english-harmonizer/SMT/Baseline/work/LM/LM_data+Train_data.en.lm

mkdir -p work/tuning
$SCRIPTS_ROOTDIR/training/mert-moses.pl data/Tune/Tune_data.mt04.50.ar data/Tune/Tune_data.mt04.50.en /home/ubuntu/tools/moses/bin/moses work/model/moses.ini --working-dir /home/ubuntu/workspace/mt-arabic-english-harmonizer/SMT/Baseline/work/tuning/mert --rootdir $SCRIPTS_ROOTDIR --decoder-flags "-v 0" --mertdir=/home/ubuntu/tools/moses/mert --predictable-seed
$SCRIPTS_ROOTDIR/scripts/reuse-weights.perl work/tuning/mert/moses.ini < work/model/moses.ini > work/tuning/moses-tuned.ini
```
**Notes:**

1. /home/ubuntu/tools/bin points to GIZA++ binaries directory
2. LM model must be absolute path


**Evaluation:**
________________
```
$SCRIPTS_ROOTDIR/training/filter-model-given-input.pl work/evaluation/filtered work/tuning/moses-tuned.ini data/Test/Test_data.mt05.src.ar
/home/ubuntu/tools/moses/bin/moses -config work/evaluation/filtered/moses.ini -input-file data/Test/Test_data.mt05.src.ar 1> work/evaluation/Eval.filtered.output 2> work/evaluation/filtered.decode.out &

```

perl $MADAHOME/MADA+TOKAN.pl config=conf/template.madaconfig file=data/Train/Train_data.clean.ar TOKAN_SCHEME="SCHEME=ATP MARKNOANALYSIS" 

ngram-count -order 3 -interpolate -kndiscount -unk -text data/LM/LM_data+Train_data.en -lm work/LM/LM_data+Train_data.en.lm

python harmonizer/factorize-corpus.py data/Train/Train_data.clean.ar.bw.mada  > data/Train/Train_data.clean.factored.ar

cp data/Train/Train_data.clean.en data/Train/Train_data.clean.factored.en

# Cleans up residue from a previous training (if any)
rm -rfv work && mkdir -p work/LM && cp LM_data+Train_data.en.lm work/LM/ && rm -f data/Train/Train_data_factored.0-0.ar && rm -f data/Train/Train_data_factored.1-0.ar && rm -f data/Train/Train_data_factored.0-0.en && rm -f data/Train/Train_data_factored.1-0.en


head -n 34000 data/Train/Train_data.clean.factored.ar > data/Train/Train_data.clean.factored.small.ar
head -n 34000 data/Train/Train_data.clean.factored.en > data/Train/Train_data.clean.factored.small.en


$SCRIPTS_ROOTDIR/training/train-model.perl  -external-bin-dir /Users/aiman/tools/bin \
                                            -root-dir /Users/aiman/Development/mt-project/work \
                                            -corpus data/Train/Train_data.clean.factored.small \
                                            -f ar -e en -alignment grow-diag-final-and \
                                            -reordering msd-bidirectional-fe \
                                            -lm 0:3:/Users/aiman/Development/mt-project/work/LM/LM_data+Train_data.en.lm \
                                            -alignment-factors 1-0 \
                                            -translation-factors 1,2-0

python harmonizer/cluster-annotated-table.py work/model/phrase-table.1,2-0.gz > harmonizer_training_data.csv

python harmonizer/train_harmonizer.py harmonizer_training_data.csv #### Saves the model as harmonizer_mode.pkl

########### TRAINING & EVALUATING THE BASELINE SYSTEM ############
Trained with 34000 Sentences (cleaned)

cd SMT/Baseline
mkdir -p work/LM
cp ../../LM_data+Train_data.en.lm work/LM/

$SCRIPTS_ROOTDIR/training/train-model.perl  -external-bin-dir /Users/aiman/tools/bin \
                                            -root-dir work \
                                            -corpus data/Train/Train_data.clean \
                                            -f ar -e en -alignment grow-diag-final-and \
                                            -reordering msd-bidirectional-fe \
                                            -lm 0:3:/Users/aiman/Development/mt-project/work/LM/LM_data+Train_data.en.lm


$SCRIPTS_ROOTDIR/training/filter-model-given-input.pl work/evaluation/filtered work/model/moses.ini data/Test/Test_data.mt05.src.ar


nohup nice /Users/aiman/tools/mosesdecoder/bin/moses -config work/evaluation/filtered/moses.ini -input-file data/Test/Test_data.mt05.src.ar 1> work/evaluation/Eval.filtered.output 2> work/evaluation/filtered.decode.out &

$SCRIPTS_ROOTDIR/wrap-xml.perl data/Test/Test_data.mt05.ref.ar.xml en my-system-name < work/evaluation/Eval.filtered.output > work/evaluation/Eval.filtered.output.sgm

$SCRIPTS_ROOTDIR/generic/mteval-v11b.pl -s data/Test/Test_data.mt05.src.ar.xml -r data/Test/Test_data.mt05.ref.en.xml -t work/evaluation/Eval.filtered.output.sgm –c



MT evaluation scorer began on 2013 Apr 7 at 22:00:24
command line:  /Users/aiman/tools/mosesdecoder/scripts/generic/mteval-v11b.pl -s data/Test/Test_data.mt05.src.ar.xml -r data/Test/Test_data.mt05.ref.en.xml -t work/evaluation/Eval.filtered.output.sgm –c
  Evaluation of Arabic-to-English translation using:
    src set "mt05_arabic_evlset_v0" (4 docs, 48 segs)
    ref set "mt05_arabic_evlset_v0-ref" (4 refs)
    tst set "mt05_arabic_evlset_v0" (1 systems)

NIST score = 6.3133  BLEU score = 0.3124 for system "ahd"

# ------------------------------------------------------------------------

Individual N-gram scoring
        1-gram   2-gram   3-gram   4-gram   5-gram   6-gram   7-gram   8-gram   9-gram
        ------   ------   ------   ------   ------   ------   ------   ------   ------
 NIST:  5.0049   1.0157   0.2046   0.0570   0.0311   0.0108   0.0058   0.0022   0.0000  "ahd"

 BLEU:  0.7170   0.3981   0.2510   0.1582   0.0933   0.0519   0.0323   0.0169   0.0052  "ahd"

# ------------------------------------------------------------------------
Cumulative N-gram scoring
        1-gram   2-gram   3-gram   4-gram   5-gram   6-gram   7-gram   8-gram   9-gram
        ------   ------   ------   ------   ------   ------   ------   ------   ------
 NIST:  5.0049   6.0206   6.2252   6.2822   6.3133   6.3241   6.3299   6.3321   6.3321  "ahd"

 BLEU:  0.6866   0.5116   0.3977   0.3124   0.2432   0.1866   0.1444   0.1098   0.0779  "ahd"
MT evaluation scorer ended on 2013 Apr 7 at 22:00:25



########### TRAINING & EVALUATING THE IMPROVED SYSTEM ############

mkdir -p SMT/Improved/data/Train

* Improvment: Harmonize training data with English Language
python harmonizer/harmonizer.py harmonizer_model.pkl data/Train/Train_data.clean.factored.ar > SMT/Improved/data/Train/Train_data.clean.harmonized.ar

cp data/Train/Train_data.clean.factored.en SMT/Improved/data/Train/Train_data.clean.harmonized.en 

cd SMT/Improved

$SCRIPTS_ROOTDIR/training/train-model.perl  -external-bin-dir /Users/aiman/tools/bin \
                                            -root-dir work \
                                            -corpus data/Train/Train_data.clean.harmonized \
                                            -f ar -e en -alignment grow-diag-final-and \
                                            -reordering msd-bidirectional-fe \
                                            -lm 0:3:/Users/aiman/Development/mt-project/work/LM/LM_data+Train_data.en.lm


# Harmonize test data
cd ../../
perl $MADAHOME/MADA+TOKAN.pl config=conf/template.madaconfig file=SMT/Improved/data/Test/Test_data.mt05.src.ar TOKAN_SCHEME="SCHEME=ATP MARKNOANALYSIS" 

python harmonizer/factorize-corpus.py SMT/Improved/data/Test/Test_data.mt05.src.ar.bw.mada  > SMT/Improved/data/Test/Test_data.mt05.src.factored.ar
python harmonizer/harmonizer.py harmonizer_model.pkl SMT/Improved/data/Test/Test_data.mt05.src.factored.ar > SMT/Improved/data/Test/Test_data.mt05.src.harmonized.ar

# Evaluate
cd SMT/Improved

$SCRIPTS_ROOTDIR/training/filter-model-given-input.pl work/evaluation/filtered work/model/moses.ini data/Test/Test_data.mt05.src.harmonized.ar

nohup nice /Users/aiman/tools/mosesdecoder/bin/moses -config work/evaluation/filtered/moses.ini -input-file data/Test/Test_data.mt05.src.harmonized.ar 1> work/evaluation/Eval.filtered.output 2> work/evaluation/filtered.decode.out &

$SCRIPTS_ROOTDIR/wrap-xml.perl data/Test/Test_data.mt05.ref.ar.xml en my-system-name < work/evaluation/Eval.filtered.output > work/evaluation/Eval.filtered.output.sgm

$SCRIPTS_ROOTDIR/generic/mteval-v11b.pl -s data/Test/Test_data.mt05.src.ar.xml -r data/Test/Test_data.mt05.ref.en.xml -t work/evaluation/Eval.filtered.output.sgm –c

## Attempt 1: SVM Harmonizer Trained with 7000 Sentences ##
    - Yields dataset size: 15402 entry
    - 1972 of which belongs to class 1
    - 7000 sentences from Train_data.ar/en  (not cleaned)
    - Trained using SVM
    - Harmonized Corpus containd  2599 collapsed token
    - Harmonized Corpus size 35644 (not cleaned)
    - Test data yielded only 3 collapsed tokens

        MT evaluation scorer began on 2013 Apr 4 at 01:10:05
        command line:  /Users/aiman/tools/mosesdecoder/scripts/generic/mteval-v11b.pl -s data/Test/Test_data.mt05.src.ar.xml -r data/Test/Test_data.mt05.ref.en.xml -t work/evaluation/Eval.filtered.output.sgm –c
          Evaluation of Arabic-to-English translation using:
            src set "mt05_arabic_evlset_v0" (4 docs, 48 segs)
            ref set "mt05_arabic_evlset_v0-ref" (4 refs)
            tst set "mt05_arabic_evlset_v0" (1 systems)

        NIST score = 6.4259  BLEU score = 0.3153 for system "ahd"

        # ------------------------------------------------------------------------

        Individual N-gram scoring
                1-gram   2-gram   3-gram   4-gram   5-gram   6-gram   7-gram   8-gram   9-gram
                ------   ------   ------   ------   ------   ------   ------   ------   ------
         NIST:  5.0323   1.0981   0.2164   0.0523   0.0267   0.0118   0.0058   0.0046   0.0025  "ahd"

         BLEU:  0.7269   0.4117   0.2571   0.1556   0.0938   0.0548   0.0315   0.0190   0.0115  "ahd"

        # ------------------------------------------------------------------------
        Cumulative N-gram scoring
                1-gram   2-gram   3-gram   4-gram   5-gram   6-gram   7-gram   8-gram   9-gram
                ------   ------   ------   ------   ------   ------   ------   ------   ------
         NIST:  5.0323   6.1304   6.3468   6.3992   6.4259   6.4377   6.4435   6.4482   6.4507  "ahd"

         BLEU:  0.6929   0.5214   0.4054   0.3153   0.2450   0.1894   0.1456   0.1122   0.0867  "ahd"
        MT evaluation scorer ended on 2013 Apr 4 at 01:10:06


## Attempt 2: SVM Harmonizer Trained with 34000 Sentences without Lemmas ##

    - Yields dataset size: 11407 entry
    - 1662 of which belongs to class 1
    - 34000 sentences from Train_data.clean.ar/en  
    - Trained using SVM
    - Harmonized Corpus containd 4003 collapsed token
    - Test data yielded only 7 collapsed tokens

        MT evaluation scorer began on 2013 Apr 7 at 20:45:56
        command line:  /Users/aiman/tools/mosesdecoder/scripts/generic/mteval-v11b.pl -s data/Test/Test_data.mt05.src.ar.xml -r data/Test/Test_data.mt05.ref.en.xml -t work/evaluation/Eval.filtered.output.sgm –c
          Evaluation of Arabic-to-English translation using:
            src set "mt05_arabic_evlset_v0" (4 docs, 48 segs)
            ref set "mt05_arabic_evlset_v0-ref" (4 refs)
            tst set "mt05_arabic_evlset_v0" (1 systems)

        NIST score = 6.3497  BLEU score = 0.3246 for system "ahd"

        # ------------------------------------------------------------------------

        Individual N-gram scoring
                1-gram   2-gram   3-gram   4-gram   5-gram   6-gram   7-gram   8-gram   9-gram
                ------   ------   ------   ------   ------   ------   ------   ------   ------
         NIST:  5.0066   1.0479   0.2163   0.0537   0.0253   0.0106   0.0066   0.0031   0.0015  "ahd"

         BLEU:  0.7353   0.4146   0.2733   0.1754   0.1085   0.0647   0.0402   0.0226   0.0129  "ahd"

        # ------------------------------------------------------------------------
        Cumulative N-gram scoring
                1-gram   2-gram   3-gram   4-gram   5-gram   6-gram   7-gram   8-gram   9-gram
                ------   ------   ------   ------   ------   ------   ------   ------   ------
         NIST:  5.0066   6.0545   6.2708   6.3245   6.3497   6.3603   6.3669   6.3700   6.3716  "ahd"

         BLEU:  0.6863   0.5154   0.4077   0.3246   0.2571   0.2020   0.1588   0.1234   0.0953  "ahd"
        MT evaluation scorer ended on 2013 Apr 7 at 20:45:57


## Attempt 2: SVM Harmonizer Trained with Lemmas ##

    - Yields dataset size: 11407 entry
    - 1662 of which belongs to class 1
    - 34000 sentences from Train_data.clean.ar/en  
    - Trained using SVM
    - Harmonized Corpus containd 987347 non-collapsed token and 716463 collapsed token
    - Test data yielded only 7 collapsed tokens

        MT evaluation scorer began on 2013 Apr 8 at 11:41:03
        command line:  /Users/aiman/tools/mosesdecoder/scripts/generic/mteval-v11b.pl -s data/Test/Test_data.mt05.src.ar.xml -r data/Test/Test_data.mt05.ref.en.xml -t work/evaluation/Eval.filtered.output.sgm –c
          Evaluation of Arabic-to-English translation using:
            src set "mt05_arabic_evlset_v0" (4 docs, 48 segs)
            ref set "mt05_arabic_evlset_v0-ref" (4 refs)
            tst set "mt05_arabic_evlset_v0" (1 systems)

        NIST score = 6.5082  BLEU score = 0.3100 for system "ahd"

        # ------------------------------------------------------------------------

        Individual N-gram scoring
                1-gram   2-gram   3-gram   4-gram   5-gram   6-gram   7-gram   8-gram   9-gram
                ------   ------   ------   ------   ------   ------   ------   ------   ------
         NIST:  5.2053   1.0090   0.2110   0.0581   0.0247   0.0068   0.0027   0.0013   0.0000  "ahd"

         BLEU:  0.7427   0.4022   0.2418   0.1512   0.0870   0.0454   0.0237   0.0109   0.0042  "ahd"

        # ------------------------------------------------------------------------
        Cumulative N-gram scoring
                1-gram   2-gram   3-gram   4-gram   5-gram   6-gram   7-gram   8-gram   9-gram
                ------   ------   ------   ------   ------   ------   ------   ------   ------
         NIST:  5.2053   6.2144   6.4254   6.4835   6.5082   6.5150   6.5176   6.5189   6.5189  "ahd"

         BLEU:  0.7124   0.5242   0.3994   0.3100   0.2385   0.1796   0.1337   0.0973   0.0682  "ahd"
        MT evaluation scorer ended on 2013 Apr 8 at 11:41:04




        
