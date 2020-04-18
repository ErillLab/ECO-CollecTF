This script runs a series of other scripts to create some intermediate data that is easier to work with than the original format. This additional information will be created in new directories in the corpus tree.

python ECO-CollecTF_run_iaa_scripts.py \path\to\ECO_1_2 ECO_annotation_1_2 3 team_1_pairs.txt ..\eco_v2018-09-14.obo T1 S1 A1 M1

python ECO-CollecTF_run_iaa_scripts.py \path\to\ECO_3 ECO_annotation3 3 team_2_pairs.txt ..\eco_v2018-09-14.obo T1 D1 A2

The IAA scores will be in the IAA subdirs under the corpus (one per corpus), IAA_sent_iaa_k_avg.txt and IAA_multi_label_iaa_kwic_avg.txt.

