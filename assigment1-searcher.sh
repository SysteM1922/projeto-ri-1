#!/bin/bash
source .setup.sh

# -------------------------NOT WORKING-------------------------
# Use test_searcher.py to run interactive mode --> CLI incompatible with interactive mode
# Interactive Mode (BM25)
python main.py searcher interactive "" --top_k 10 ranking.bm25 --ranking.bm25.k1 1.2 --ranking.bm25.b 0.6
# Interactive Mode (TF-IDF) 
python main.py searcher interactive "" --top_k 10 ranking.tfidf --ranking.tfidf.smart "lnc.ltc"



# -------------------------WORKING-------------------------
# Batch Mode (BM25) --> runs with default parameters (k1=1.2, b=0.75) despite the cli arguments // Conflitos de argumentos na cli (cli mal feita)
python main.py searcher batch "" "questions_with_gs/question_E8B1_gs.jsonl" "output_file" --top_k 10 ranking.bm25 --ranking.bm25.k1 1.2 --ranking.bm25.b 0.6

# Batch Mode (TF-IDF) (Using cache depends if there is a file from the indexer)
python main.py searcher batch "" "questions_with_gs/question_E8B1_gs.jsonl" "output" --top_k 10 ranking.tfidf --ranking.tfidf.smart "lnc.ltc"
