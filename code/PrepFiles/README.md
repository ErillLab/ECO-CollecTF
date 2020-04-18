August 2018. We followed this process because we already had the PMIDs of the documents we wanted to get and we had most of this code from a prior effort.

nltk toolkit must be installed with the english.pickle file.


1. Create a text file with the PMIDs of the documents to obtain. One PMID per line.


2. Get the PMIDs' PMC IDs

python fetch_pmid_pmcs.py input_file output_file

ex: python fetch_pmid_pmcs.py input_file_of_pmids.txt pmid_pmc_info.txt


3. Process the downloaded file to obtain just the pmid-pmc id pairs

python get_pmid_pmc_pairs.py input_file > output_file

ex: python get_pmid_pmc_pairs.py pmid_pmc_info.txt pmid_pmc_id_pairs.txt


4. Get the PMC XMLs

python fetch_pmc_xmls.py input_file output_dir

ex: python fetch_pmc_xmls.py pmid_pmc_id_pairs.txt pmc_xmls


5. Triage -- documents downloaded from PMC can be in different formats. Also, not all PMC documents have a license that permits downloaded.
Triage the output dir to extract the results and results/discussion sections that we recognize.

python triage_pmc_xmls_results.py input_dir output_dir

ex: python triage_pmc_xmls_results.py pmc_xmls triage_pmc_xmls

Note: the files that were successfully parsed go into the directory triage_pmc_xmls\format_1R. 
The rest go into the directory triage_pmc_xmls\unknownR


6. Preprocess to remove special characters

python replace_dir_html_chars.py html_entity_transformations.txt input_dir output_dir

ex: python replace_dir_html_chars.py html_entity_transformations.txt triage_pmc_xmls\format_1R triage_pmc_xmls\preproc_xmls


7. OPTIONAL: parse the XMLs into HTMLs for easy review in a browser

python parse_dir_results_xmls.py -m m input_dir output_dir

ex: python parse_dir_results_xmls.py -m m triage_pmc_xmls\preproc_xmls triage_pmc_xmls\htmls


8. Extract the XML text into text files

python parse_dir_results_xmls.py input_dir output_dir

ex: python parse_dir_results_xmls.py triage_pmc_xmls\preproc_xmls triage_pmc_xmls\texts


9. Parse the texts into files with one sentence per line

Note: This uses nltk toolkit. Must have the english.pickle file. Review the files to be sure the sentence breaking is occurring correctly.

python split_s_dir.py input_dir output_dir

ex: python split_s_dir.py triage_pmc_xmls\texts results_dir\data


10. brat requires files to be in Unix format -- that is, they need the Unix end-of-line character \n, not the Microsoft carriage return - line feed.
Unix systems have a utility called dos2unix that will convert the files. Mingw's utility was used for ECO-CollecTF.

cd results_dir\data
dos2unix *.txt

NOTE: the above operation is done in place (files are overwritten).


11. Follow brat installation instructions for preparing the data directory for brat at http://brat.nlplab.org/installation.html under the section "Placing data".
(After the brat server has been installed and set up, of course.)


12. To extract the attribution and copyright information:
python parse_dir_copyright_xmls.py input_dir article_output_dir

Make the article_output_dir be a different directory where the results text files are placed.

