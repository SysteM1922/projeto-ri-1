from indexer import Indexer

indexer = Indexer(memory_threshold=0.2,
                  path_to_collection="collections/pubmed_2022_small.jsonl",
                  index_output_path="", regular_exp="[a-zA-Z0-9]{3,}",
                  stemmer="pystemmer",
                  lowercase=True, minL=3,
                  index_algorithm="SPIMI",
                  store_term_positions=False,
                  bm25_cache_in_disk=False,
                  tfidf_cache_in_disk=False,
                  tfidf_smart="lnc.ltc",
                  stopwords_path="default_stopwords.txt")

indexer.index()