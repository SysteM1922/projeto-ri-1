#!/bin/bash
source .setup.sh
# General example
python main.py evaluator 'gold_standard_file' 'run_file' --metrics 'precision' 'recall' 'F1' 'DCG' 'AP'

# Example 1
# Run Evaluator with default metrics [F1, DCG, MAP/AP]
python main.py evaluator "questions_with_gs/question_E8B1_gs.jsonl" "output.json" 

# Example 2
# Run Evaluator with custom metrics [precision, recall, F1]
python main.py evaluator "questions_with_gs/question_E8B1_gs.jsonl" "output.json" --metrics precision recall F1

# Example 3
# Run Evaluator with all metrics
python main.py evaluator "questions_with_gs/question_E8B1_gs.jsonl" "output.json" --metrics precision recall F1 DCG AP