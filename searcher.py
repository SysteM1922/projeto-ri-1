import json
import math
from reader import JsonReader
from tokenizer import Tokenizer
import time
import os
import linecache
from utils import *

class Searcher:

    def __init__(self, searcher_mode: str, index_folder: str, path_to_questions: str, output_file: str, ranking_mode: str, 
                 top_k: int = 10, ranking_bm25_k1: float = 1.2, ranking_bm25_b: float=0.75, ranking_tfidf_smart: str="lnc.ltc" ) -> None:

        #   load metadata
        metadata = json.load(open(f"{index_folder}metadata.json"))

        #   initialize tokenizer with metadata
        self.tokenizer = Tokenizer(minL=metadata["minL"], stemmer=metadata["stemmer"], lowercase=metadata["lowercase"], regular_exp=metadata["regular_exp"], stopwords_path=metadata["stopwords_path"])

        self.cache = False
        self.cache_file = None
        
        if ranking_mode == "ranking.bm25":
            self.__class__ = BM25Searcher
            self.bm25_k1 = ranking_bm25_k1
            self.bm25_b = ranking_bm25_b
            if os.path.exists(f"{index_folder}cache_bm25_{self.bm25_k1}_{self.bm25_b}"):
                self.cache = True
                self.cache_file = f"{index_folder}cache_bm25_{self.bm25_k1}_{self.bm25_b}"

        elif ranking_mode == "ranking.tfidf":
            self.__class__ = TFIDFSearcher
            self.smart = ranking_tfidf_smart.split(".")
            if os.path.exists(f"{index_folder}cache_tfidf_{self.smart[0]}"):  
                self.cache = True
                self.cache_file = f"{index_folder}cache_tfidf_{self.smart[0]}"
        
        else:
            raise Exception("Invalid ranking mode: {}".format(ranking_mode))
        
        self.index_folder = index_folder
        self.path_to_questions = path_to_questions
        self.output_file = output_file+".json"
        self.top_k = top_k
        self.searcher_mode = searcher_mode
        self.path_to_questions = path_to_questions

        self.index_map = json.load(open(f"{index_folder}index_map.json"))
        self.combinations = list(self.index_map.keys())

    def start(self):
        if self.searcher_mode == "batch":
            queries = JsonReader(self.path_to_questions).read()
            self.batch_search(queries)

        elif self.searcher_mode == "interactive":
            self.interative_search()

        else:
            raise Exception("Invalid searcher mode: {}".format(self.searcher_mode))
        
    def process_query(self, query: str):
        return self.tokenizer.tokenize(query)

    def batch_search(self, queries: list[str]):

        final_results = {}

        for query in queries:

            # Example:
            # {"query_id": "5e48e0e0f8b2df0d49000001", 
            # "query_text": "Are gut microbiota profiles altered by irradiation?", 
            # "documents_pmid": ["30430918", "30343431", "30459840"]}

            query_id = query["query_id"]
            query_text = query["query_text"]

            query_tokens = self.process_query(query_text)

            results, query_processing_time, total_results_count = self.search(query_tokens)
            print(f"{query_id}: {total_results_count} results found in {round(query_processing_time, 3)} seconds")
            final_results[query_id] = results
            #print(results)
            # print(query_id, query_text, query_tokens)

            # save results

        self.save_results(final_results, self.output_file)

    def interative_search(self):
        
        query = input("\nEnter query: ")
        while query:
            query_tokens = self.process_query(query)
            results, query_processing_time, total_results_count = self.search(query_tokens)

            print(f"{total_results_count} results found in {round(query_processing_time, 3)} seconds")

            for document_pmid, score in results.items():
                print("PMID: {0} - Score: {1}".format(document_pmid, round(score,3)))

            query = input("\nEnter query: ")

    @staticmethod
    def save_results(final_results:dict, output_file: str):
        with open(output_file, "w") as f:  
            for query_id in final_results:
                result_json = {"query_id": query_id, "documents_pmid": [], "scores": []}
                for document_pmid, score in final_results[query_id].items():
                    result_json["documents_pmid"].append(document_pmid)
                    result_json["scores"].append(score)
                f.write(json.dumps(result_json) + "\n")


    def print_results():
        pass

    def search(self):
        raise NotImplementedError


class TFIDFSearcher(Searcher):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        print("initializing TFIDFSearcher with SMART: {0}".format(self.smart))


    def search(self, query_tokens: list[str]):

        #   Initialize results
        results = {}

        #   If query has no tokens, skip it
        if len(query_tokens) == 0:
            return results, 0, 0

        start_time = time.perf_counter()

        #   Calculate N
        N = sum(1 for _ in open('document_mapping'))

        doc_smart, query_smart = self.smart

        query_terms_freq = {}
        docs_freq = {}
        coll_results = {}

        if self.cache:
            print("Using cache")
            for term in set(query_tokens):
                #   Calculate query term frequency of terms in query
                query_terms_freq[term] = query_tokens.count(term)
                try:
                    #   Check where term is in index
                    start_idx = self.index_map[term[:2]]
                    end_idx = self.index_map[self.combinations[self.combinations.index(term[:2])+1]]
                except:
                    continue
                #   Iterate over the cache file to find the term
                for idx in range(start_idx, end_idx):
                    line = linecache.getline(self.cache_file, idx + 1)
                    if line.startswith(term):
                        line = line.split(";")[1:]
                        #   Calculate document frequency of terms in query
                        docs_freq[term] = len(line)
                        for doc in line:
                            #   Get the tf-idf score of the term in the document
                            doc_id, score = doc.split(":")
                            if doc_id not in coll_results:
                                coll_results[doc_id] = {}	
                            coll_results[doc_id][term] = float(score)
                        break

            query_terms_weights = term_frequency_weighting(query_smart[0], query_terms_freq)
            doc_weights = document_frequency_weighting(query_smart[1], docs_freq, N)
            query_tfidf = normalization_factor(query_smart[2], {term: query_terms_weights[term] * doc_weights[term] for term in query_terms_weights if term in doc_weights})

            results = {}
            for doc_id in coll_results:
                new_doc = linecache.getline('document_mapping', int(doc_id)+1).split(":")[0]
                #   Calculate similarity between query and document
                if new_doc not in results:
                    results[new_doc] = 0
                results[new_doc] = sum(query_tfidf[term] * coll_results[doc_id].get(term, 0)  for term in query_tfidf)


        else:
            coll_terms_freq = {}
            coll_terms_weights = {}
            for term in set(query_tokens):
                #   Calculate query term frequency of terms in query
                query_terms_freq[term] = query_tokens.count(term)
                try:
                    #   Check where term is in index
                    start_idx = self.index_map[term[:2]]
                    end_idx = self.index_map[self.combinations[self.combinations.index(term[:2])+1]]
                except:
                    continue
                #   Iterate over the index file to find the term
                for idx in range(start_idx, end_idx):
                    line = linecache.getline(f'{self.index_folder}index', idx + 1)
                    if line.startswith(term):
                        line = line.split(";")[1:]
                        #   Calculate document frequency of terms in query
                        docs_freq[term] = len(line)
                        for doc in line:
                            #   Get the tf-idf score of the term in the document
                            doc_id, tf = doc.split(":")
                            if term not in coll_terms_freq:
                                coll_terms_freq[term] = {}	
                            coll_terms_freq[term][doc_id] = int(tf)
                        break
            
            query_terms_weights = term_frequency_weighting(query_smart[0], query_terms_freq)
            doc_weights = document_frequency_weighting(query_smart[1], docs_freq, N)
            query_tfidf = normalization_factor(query_smart[2], {term: query_terms_weights[term] * doc_weights[term] for term in query_terms_weights if term in doc_weights})
            doc_weights = document_frequency_weighting(doc_smart[1], docs_freq, N)

            for term in coll_terms_freq:
                #   Calculate tf-idf score of terms in collection
                coll_terms_weights = term_frequency_weighting(doc_smart[0], coll_terms_freq[term])
                for doc_id in coll_terms_weights:
                    if doc_id not in coll_results:
                        coll_results[doc_id] = {}
                    coll_results[doc_id][term] = coll_terms_weights[doc_id] * doc_weights[term]
            
            coll_results = {doc_id: normalization_factor(doc_smart[2], coll_results[doc_id]) for doc_id in coll_results}
            
            results = {}
            for doc_id in coll_results:
                new_doc = linecache.getline('document_mapping', int(doc_id) + 1).split(":")[0]
                #   Calculate similarity between query and document
                if new_doc not in results:
                    results[new_doc] = 0
                results[new_doc] = sum(query_tfidf[term] * coll_results[doc_id].get(term, 0)  for term in query_tfidf)

        query_processing_time = time.perf_counter() - start_time
        # Sort results by cosine similarity (score)
        results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
        # Return top-k documents
        results2 = {k: results[k] for k in list(results)[:self.top_k]}

        return results2, query_processing_time, len(results)
    
    
class BM25Searcher(Searcher):        

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
        print("initializing BM25Searcher with k1: {0} and b: {1}".format(self.k1, self.b))

    def search(self, query_tokens: str):
        
        start_time = time.perf_counter()

        # Initialize results
        results = {}

        # If query has no tokens, skip it
        if len(query_tokens) == 0:
            return results, 0, 0

        if self.cache:
            print("Using cache")
            for term in set(query_tokens):
                try:
                    #   Check where term is in index
                    start_idx= self.index_map[term[:2]]
                    end_idx = self.index_map[self.combinations[self.combinations.index(term[:2])+1]]
                except:
                    continue
                for idx in range(start_idx, end_idx):
                    #   Iterate over the cache file to find the term
                    line = linecache.getline(self.cache_file, idx + 1)
                    if line.startswith(term):
                        line = line.split(";")[1:]
                        for doc in line:
                            doc_id, score = doc.split(":")
                            document_pmid=linecache.getline('document_mapping', int(doc_id)+1).split(":")[0]
                            #   Add the score of the term in the document to the total score of the document
                            if document_pmid not in results:
                                results[document_pmid] = 0
                            results[document_pmid] += float(score)
                        break

        else:
            # Average document length
            # document length = number of terms in document document mapping doc:dl
            dl = [int(line.split(":")[1]) for line in open('document_mapping')]
            N = len(dl)
            avgdl = sum(dl) / N
            # Compute BM25 score for each document
            for term in query_tokens:
                # Obtain inverted list for term
                try:
                    start_idx = self.index_map[term[:2]]
                    end_idx = self.index_map[self.combinations[self.combinations.index(term[:2])+1]]
                except:
                    continue
                for idx in range(start_idx, end_idx):
                    #   Iterate over the index file to find the term
                    line = linecache.getline('index', idx + 1)
                    if line.startswith(term):
                        line = line.split(";")[1:]
                        for doc in line:
                            doc_id, tf = doc.split(":")
                            #   Calculate idf
                            idf = math.log10(N / len(line))
                            #   Calculate BM25 score
                            score = rsv(bm25_b=self.bm25_b, bm25_k1=self.bm25_k1, idf=idf, tf=int(tf), dl=dl[int(doc_id)], avgdl = avgdl)
                            document_pmid=linecache.getline('document_mapping', int(doc_id)+1).split(":")[0]
                            #   Add the score of the term in the document to the total score of the document
                            if document_pmid not in results:
                                results[document_pmid] = 0
                            results[document_pmid] += score
                        break

        query_processing_time = time.perf_counter() - start_time

        # ----------- Return results
        # Sort results by BM25 score
        results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
        # Return top-k documents
        results2 = {k: results[k] for k in list(results)[:self.top_k]}

        return results2, query_processing_time, len(results)
        