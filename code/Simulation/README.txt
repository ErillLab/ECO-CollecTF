Run the simulations used for analyzing KwIC.

Parameters for the run are:
alpha = density of annotated sentences
gamma1 = FNR
gamma2 = FPR
beta = probability of success for geometric distribution

See gen_doc_params_from_data_glommed_loosest_*.txt

Note: "0hops" parameter file is equivalent to p=1. That is no hopping is done.

Note: corpus_all_occurrences_ecos_used_list.txt is a dump of all the ECOs in the corpus, by annotator, with repeats.

1. Generate the simulated documents and annotations for a given parameter set.

python generate_set_of_docs.py \path\to\output-dir gen_doc_params_from_data_beta_0hops.txt corpus_all_occurrences_ecos_used_list.txt

    Note: The script will create the new output-directory to put the results (example: \path\to\beta_1) provided the upper-level directories exist already.
    Note: generate_set_of_docs.py is set to generate 100 document sets. Each doc set consists of 10 text files with 150 sentences each (for 1500 sentences total).
    Note: The brat directory structure for data is modeled here, as is the intermediate format created for the actual data. The "data" directory for the "annotations" is not really used so it is just a copy of the gold standard data. The data_as_tags intermediate format subdirectory is what contains the "annotations".


2. Calculate the KwIC for the simulated set. 
IMPORTANT Note: script calls operating system grep, such as you get on Windows with mingw.

python generate_set_of_stats.py \full\path\to\output-dir

    Note: This step uses the scripts in the IAA directory for outputing the intermediate format files and calculating KwIC.
    Note: It will take a while to run.
    Note: Both the Cohen's K and the KwIC are calculated. Over 100 doc sets, the K should average to around 0.69. (The simulated K should closely match the actual K is the data parameters alpha, gamma1, and gamma2 are good estimates.

At the end of this step, the data of all the runs is summarized in the \path\to\output-dir files
    The first 4 values are the parameters (remember 0=#hops, all other values are p).
    The last 3 values are min, max and average.
    The values in the middle are the values for each doc set.


3. Repeat for other parameter files. For step 1, use a new subdirectory for each.

4. If you want to generate a CSV with the KwICs and Ks for all the runs in one file (requires pandas):

4A. Create a text file with the names of the directories for each run. Since we use subdirs, it looks like
beta_1
beta_0.5

4B. python generate_csv_from_indiv.py text-file-with-subdir-names.txt p-pos output_csv

    Note: p-pos = which position the p or hops is in the subdir-name. In the sample it is 1
    Note: Will get 2 csvs: output_csv_k.csv and output_csv_kwic.csv
