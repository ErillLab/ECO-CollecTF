# Run the scripts in the IAA directory first before running this script.
# Alpha (density) will be at the end of corpus_params_from_data_log.txt
# FNR and FPR at the end of corpus_FNR_FPR.txt
import time
import os

sys_cmd = "python get_alpha_from_data.py params_from_data_config.txt > corpus_alpha_from_data_log.txt"
print sys_cmd
os.system(sys_cmd)
time.sleep(2)
sys_cmd = "python run_annot_pairs_as_gs_v2.py params_from_data_config.txt v2 corpus_FNR_FPR.txt"
print sys_cmd
os.system(sys_cmd)
