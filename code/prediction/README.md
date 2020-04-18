1. Create the input features. This works on a data directory.

python generate_input_data.py \path\to\ECO_1_2\data\ECO_annotation_1_2\T1 eco_1_2_inputs.txt

python generate_input_data.py \path\to\ECO_3\data\ECO_annotation3\T1 eco_3_inputs.txt

2. Create the answer key. This requires the annotations. The ECO_1_2 key is used for training.

python gen_corpus_answer_key.py \path\to\ECO_3 ECO_annotation_1_2 3 eco_1_2_ans_key.txt T1 S1 A1 M1

python gen_corpus_answer_key.py \path\to\ECO_3 ECO_annotation3 3 eco_3_ans_key.txt T1 D1 A2

3. Do the prediction -- create the model and predict. This step is done in an Anaconda environment.

python test_mlpc_cv_rs.py eco_1_2_inputs.txt eco_1_2_ans_key.txt eco_3_inputs.txt eco_3_ans_key.txt model_output.dump

Note: The script will save the best model it finds and then use that model to do the prediction.


Optional: 4. Just predict. A prediction can be made with a saved model dump. The team's saved file is mlpc_model.dump

python test_mplc_cv_predict.py mlpc_model.dump eco_3_inputs.txt eco_3_ans_key.txt







