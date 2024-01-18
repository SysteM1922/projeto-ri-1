#!/bin/bash
source .setup.sh

# commands to complete the indexer assigment
# fell free to change, if you changed the CLI or if you found a more optimal combination of parameters
# that solves the assigment.

# REQUIRED
# 1) Create a indexer for the tiny collection
python main.py indexer collections/pubmed_tiny.jsonl \
                       pubmed_indexer_tiny_folder \
                       --tokenizer.minL 3 \
                       --tokenizer.stopwords stopw.txt \
                       --tokenizer.stemmer pystemmer \
                       --tokenizer.regular_exp "<complete with regular expression>" \
                       --tokenizer.lowercase \
                       --indexer.algorithm SPIMI 
#   Expected behaviour: 
#        The program indexes the collections/pubmed_tiny.jsonl collection and 
#        stores the inverted index as well as all of the necessary metadata inside the 
#        folder pubmed_indexer_tiny_folder.

# Example 1 
python main.py indexer collections/pubmed_2022_tiny.jsonl "" --tokenizer.minL 3 --tokenizer.stopwords default_stopwords.txt --tokenizer.stemmer pystemmer --tokenizer.regular_exp "[a-zA-Z0-9]{3,}" --tokenizer.lowercase --indexer.algorithm SPIMI

# 2) Create a indexer for the tiny collection that store the position index
python main.py indexer collections/pubmed_tiny.jsonl \
                       pubmed_indexer_tiny_folder_wPositions \
                       --tokenizer.minL 3 \
                       --tokenizer.stopwords stopw.txt \
                       --tokenizer.stemmer pystemmer \
                       --tokenizer.regular_exp "<complete with regular expression>" \
                       --tokenizer.lowercase \
                       --indexer.algorithm SPIMI \
                       --indexer.storing.store_term_position \
#   Expected behaviour: 
#        The program indexes the collections/pubmed_tiny.jsonl collection and 
#        stores the inverted index with term positions as well as all of the necessary 
#        metadata inside the folder pubmed_indexer_tiny_folder.

# Example 2
python main.py indexer collections/pubmed_2022_tiny.jsonl "" --tokenizer.minL 3 --tokenizer.stopwords default_stopwords.txt --tokenizer.stemmer pystemmer --tokenizer.regular_exp "[a-zA-Z0-9]{3,}" --tokenizer.lowercase --indexer.algorithm SPIMI --indexer.storing.store_term_position

# 3) Create a indexer for the tiny collection, with low memory threashold (0.2), which 
# corresponds that we allow the indexer to use 20% of the available memory 

python main.py indexer collections/pubmed_small.jsonl \
                       pubmed_indexer_small_folder_mT \
                       --tokenizer.minL 3 \
                       --tokenizer.stopwords stopw.txt \
                       --tokenizer.stemmer pystemmer \
                       --tokenizer.regular_exp "<complete with regular expression>" \
                       --tokenizer.lowercase \
                       --indexer.algorithm SPIMI \
                       --indexer.storing.store_term_position \
                       --indexer.memory_threshold 0.2
#   Expected behaviour: 
#        The program indexes the collections/pubmed_tiny.jsonl collection and 
#        stores the inverted index as well as all of the necessary metadata inside the 
#        folder pubmed_indexer_tiny_folder. During the indexing the memory usages should
#        not surparss the 0.2 threshold and the index shards should be writed to disk and
#        later merged

# Example 3
python main.py indexer collections/pubmed_2022_tiny.jsonl "" --tokenizer.minL 3 --tokenizer.stopwords default_stopwords.txt --tokenizer.stemmer pystemmer --tokenizer.regular_exp "[a-zA-Z0-9]{3,}" --tokenizer.lowercase --indexer.algorithm SPIMI --indexer.storing.store_term_position --indexer.memory_threshold 0.2



# OPTIONAL
# 4) Create a indexer for the medium collection
python main.py indexer collections/pubmed_medium.jsonl \
                       pubmed_indexer_medium_folder \
                       --tokenizer.minL 3 \
                       --tokenizer.stopwords stopw.txt \
                       --tokenizer.stemmer pystemmer \
                       --tokenizer.regular_exp "<complete with regular expression>" \
                       --tokenizer.lowercase \
                       --indexer.algorithm SPIMI \
                       --indexer.memory_threshold 0.8

# Example 4
python main.py indexer collections/pubmed_2022_medium.jsonl "" --tokenizer.minL 3 --tokenizer.stopwords default_stopwords.txt --tokenizer.stemmer pystemmer --tokenizer.regular_exp "[a-zA-Z0-9]{3,}" --tokenizer.lowercase --indexer.algorithm SPIMI --indexer.memory_threshold 0.8


# 5) Create a indexer for the large collection
python main.py indexer collections/pubmed_large.jsonl \
                       pubmed_indexer_large_folder \
                       --tokenizer.minL 3 \
                       --tokenizer.stopwords stopw.txt \
                       --tokenizer.stemmer pystemmer \
                       --tokenizer.regular_exp "<complete with regular expression>" \
                       --tokenizer.lowercase \
                       --indexer.algorithm SPIMI \
                       --indexer.memory_threshold 0.8

# Example 5
python main.py indexer collections/pubmed_2022_large.jsonl "" --tokenizer.minL 3 --tokenizer.stopwords default_stopwords.txt --tokenizer.stemmer pystemmer --tokenizer.regular_exp "[a-zA-Z0-9]{3,}" --tokenizer.lowercase --indexer.algorithm SPIMI --indexer.memory_threshold 0.8


# 6) Create a indexer for the tiny collection and cache the computation for BM25
python main.py indexer collections/pubmed_tiny_bm25_cached.jsonl \
                       pubmed_indexer_tiny_folder \
                       --tokenizer.minL 3 \
                       --tokenizer.stopwords stopw.txt \
                       --tokenizer.stemmer pystemmer \
                       --tokenizer.regular_exp "<complete with regular expression>" \
                       --tokenizer.lowercase \
                       --indexer.algorithm SPIMI \
                       --indexer.storing.bm25.cache_in_disk \
                       --indexer.storing.bm25.b 0.75 \

# Example 6
python main.py indexer collections/pubmed_2022_tiny.jsonl "" --tokenizer.minL 3 --tokenizer.stopwords default_stopwords.txt --tokenizer.stemmer pystemmer --tokenizer.regular_exp "[a-zA-Z0-9]{3,}" --tokenizer.lowercase --indexer.algorithm SPIMI --indexer.storing.bm25.cache_in_disk --indexer.storing.bm25.b 0.75
