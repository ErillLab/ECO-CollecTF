0. Run the main script in the IAA dir first: ECO-CollecTF_run_iaa_scripts.py.

1. After a preliminary step, get the counts of the number of curators that annotated and output the majority list and the unanimous list.
python count_eco_matches.py \path\to\ECO-CollecTF\ECO_1_2 ECO_annotation_1_2 ..\eco_v2018-09-14.obo output-dir T1 S1 A1 M1 > count_log.txt

2. If desired, concatenate the two output files eco_agreements_unanimous.txt and eco_agreements_majority.txt. Or these files can be processed individually.

3. Format the information in a more user-friendly form, sorted by ECO and by confidence, and output as a CSV.
python format_eco_agrees.py eco_agreements_unanimous.txt ..\eco_v2018-09-14.obo unanimous_list.csv

Note: Step #3 can be run with inputing a concatenated file. Or run separately with the majority input file and the two csvs concatenated.

Note: The same process can be followed for ECO_annotation_3 and combined with the files with ECO_annotation_1_2.

For selecting ECO examples of use, ECO_annotation_1_2 and ECO_annotation_3 files were combined before step 3.

The resulting CSV was manually reviewed to remove excess examples so that no ECO term had more than 3 or 4.

The ECO group reviewed this list and selected those examples that they felt best demonstrated the usage of ECO terms.

4. Manually review the CSV to select the desired examples of use.
