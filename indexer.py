import time
from memory_manager import MemoryManager
from tokenizer import Tokenizer
from reader import JsonReader, Reader
import os
from utils import *
import linecache
import json

class Indexer:
    
    def __init__(self, path_to_collection: str, index_output_path: str,
                 index_algorithm: str = "SPIMI", memory_threshold: int = None, store_term_positions: bool = False, 
                 bm25_cache_in_disk: bool = False, bm25_k1: float = 1.2, bm25_b: float = 0.75,
                 tfidf_cache_in_disk: bool = False, tfidf_smart: str = "lnc.ltc",
                 minL: int = 0, stopwords_path: str = "default_stopwords.txt", stemmer: str = None, regular_exp: str = "", lowercase: bool = False) -> None:
        
        #   check if the index algorithm is valid
        if index_algorithm == "SPIMI":
            if store_term_positions:
                self.__class__ = Positional_Indexer
            else:
                self.__class__ = Non_Positional_Indexer
        else:
            raise NotImplementedError
        
        #   start the memory manager
        self.memory_manager = MemoryManager(memory_threshold)

        #   read the collection
        if path_to_collection.endswith(".jsonl") or path_to_collection.endswith(".json.gz"):
            self.reader = JsonReader(path_to_collection).read()
        else:
            self.reader = Reader(path_to_collection).read()

        #   check if the cache options are valid
        if bm25_cache_in_disk and tfidf_cache_in_disk:
            raise ValueError("Cannot use both bm25_cache_in_disk and tfidf_cache_in_disk")
        elif isinstance(self, Positional_Indexer) and (bm25_cache_in_disk or tfidf_cache_in_disk):
            raise ValueError("Cannot use bm25_cache_in_disk or tfidf_cache_in_disk with positional indexer")
        elif bm25_cache_in_disk:
            self.cache = "bm25"
            self.bm25_k1 = bm25_k1
            self.bm25_b = bm25_b
        elif tfidf_cache_in_disk:
            self.cache = "tfidf"
            self.smart = tfidf_smart.split(".")[0]
        else:
            self.cache = None

        #   '\0' is the lowest unicode character
        self.last_term = '\0'
        self.last_index = 0

        #   start the tokenizer
        self.tokenizer = Tokenizer(regular_exp=regular_exp, stemmer=stemmer, stopwords_path=stopwords_path, minL=minL, lowercase=lowercase)
        self.index_output_path = index_output_path
        self.stats = {"index_size": 0, "index_time": 0, "nr_parcial_indexes": 0, "merge_time": 0}

        #   create the folder to store the parcial indexes
        if not os.path.exists(f"{self.index_output_path}.temp_index"):
            os.mkdir(f"{self.index_output_path}.temp_index")

        #   prepare metadata file
        if os.path.exists(f"{self.index_output_path}metadata.json"):
            os.remove(f"{self.index_output_path}metadata.json")

        #   write metadata file
        with open(f"{self.index_output_path}metadata.json", "w") as f:
            json.dump({"index_algorithm": index_algorithm,
                       "store_term_positions": store_term_positions,
                       "bm25_cache_in_disk": bm25_cache_in_disk,
                       "bm25_k1": bm25_k1,
                       "bm25_b": bm25_b,
                       "tfidf_cache_in_disk": tfidf_cache_in_disk,
                       "tfidf_smart": tfidf_smart,
                       "minL": minL,
                       "stopwords_path": stopwords_path,
                       "stemmer": stemmer,
                       "regular_exp": regular_exp,
                       "lowercase": lowercase}, f)
            

class SPIMI(Indexer):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def index(self):

        index = {}
        index_count = 0
        doc_id = 0
        map_list = []
        line_count = 0

        #   delete all temp_index files if they exist
        self.clean_partial_index()

        #   delete the document mapper file if it exists
        if os.path.exists(f"{self.index_output_path}document_mapping"):
            os.remove(f"{self.index_output_path}document_mapping")
        mapper = open(f"{self.index_output_path}document_mapping", 'a')

        #   clear the cache if it exists
        if self.cache == "tfidf":
            if os.path.exists(f"{self.index_output_path}cache_{self.cache}_{self.smart}"):
                os.remove(f"{self.index_output_path}cache_{self.cache}_{self.smart}")

        elif self.cache == "bm25":
            if os.path.exists(f"{self.index_output_path}cache_{self.cache}_{self.bm25_k1}_{self.bm25_b}"):
                os.remove(f"{self.index_output_path}cache_{self.cache}_{self.bm25_k1}_{self.bm25_b}")

        def write_in_document_mapper():
            mapper.writelines(map_list)
            map_list.clear()

        def save_partial_index():
            write_in_document_mapper()
            self.save_index(index, path=f"{self.index_output_path}.temp_index/index{index_count}")
            index.clear()

        control = True

        start = time.perf_counter()
        doc = next(self.reader)

        max_iter = 10000
        stop = False
        current_memory = self.memory_manager.get_memory_usage()

        def check_max_iter(max_iter: int):
            memory_diff = self.memory_manager.get_memory_usage() - current_memory
            prod_factor = 1.0

            #   based on the memory usage of the first 10000 iterations, we calculate the number of iterations that we can do
            while prod_factor >= 0.05:
                if self.memory_manager.can_afford_memory(memory_diff + memory_diff * prod_factor):
                    memory_diff += memory_diff * prod_factor
                    max_iter += max_iter * prod_factor
                else:
                    prod_factor -= 0.05

            return int(max_iter)

        if isinstance(self, Positional_Indexer):
            while control:
                for _ in range(max_iter):
                    for i, token in enumerate(self.tokenizer.tokenize(doc["title"] + doc["abstract"])):
                        try:
                            index[token][doc_id].append(i)
                        except KeyError:
                            try:
                                index[token][doc_id] = [i]
                            except KeyError:
                                index[token] = {doc_id: [i]}

                    map_list.append(f'{doc["pmid"]}:{i}\n')
                    
                    doc_id += 1
                    try:
                        doc = next(self.reader)
                    except StopIteration:
                        control = False
                        break
                
                if not stop:
                    max_iter = check_max_iter(max_iter)
                    stop = True
                        
                line_count += len(index)
                save_partial_index()
                index_count += 1

        elif isinstance(self, Non_Positional_Indexer):
            while control:
                for _ in range(max_iter):
                    tokens = self.tokenizer.tokenize(doc["title"] + doc["abstract"])
                    for token in set(tokens):
                        try:
                            index[token].append(f"{doc_id}:{tokens.count(token)}")
                        except KeyError:
                            index[token]=[f"{doc_id}:{tokens.count(token)}"]

                    map_list.append(f"{doc['pmid']}:{len(tokens)}\n")

                    doc_id += 1
                    try:
                        doc = next(self.reader)
                    except StopIteration:
                        control = False
                        break

                if not stop:
                    max_iter = check_max_iter(max_iter)
                    stop = True
                    
                line_count += len(index)
                save_partial_index()
                index_count += 1

        end = time.perf_counter() - start
        self.stats["index_time"] = end
        mapper.close()
        
        print(f"Total indexing time:         {round(self.stats['index_time'], 2)} s")
        input("Next?")

        self.index_map = {}

        start = time.perf_counter()
        #   tell the merger to fill the blocks with the same number of lines as the medium number of lines per parcial index 
        self.merge_index(max_iter // index_count, line_count)
        end = time.perf_counter() - start
        self.stats["merge_time"] = end
        
        self.clean_partial_index()
        os.rmdir(f"{self.index_output_path}.temp_index")
        self.stats["index_size"] = os.path.getsize(f"{self.index_output_path}index") / 1024 / 1024

        print(f"Total index size on disk:    {round(self.stats['index_size'],2)} MB")
        if self.cache == "tfidf":
            print(f"Total cache size on disk:    {round(os.path.getsize(f'{self.index_output_path}cache_{self.cache}_{self.smart}') / 1024 / 1024, 2)} MB")
        elif self.cache == "bm25":
            print(f"Total cache size on disk:    {round(os.path.getsize(f'{self.index_output_path}cache_{self.cache}_{self.bm25_k1}_{self.bm25_b}') / 1024 / 1024, 2)} MB")
        
        print(f"Number of parcial indexes:   {self.stats['nr_parcial_indexes']}")
        print(f"Merging time:                {round(self.stats['merge_time'], 2)} s")

        self.create_dictionary()

        self.write_map()

    def merge_index(self, block_size: int, N: int = None):
        final_terms = {}
        new_final_terms = {}
        indexes, queues = self.start_final_index()

        #   if we are using bm25 we need to calculate the average document length
        if self.cache:
            if self.cache == "bm25":
                with open(f"{self.index_output_path}document_mapping", "r") as doc_map:
                    self.avg_dl = sum(int(line.split(":")[1]) for line in doc_map)/N
            block_size = block_size // 2
                    
        #  fill the queues with the first block_size lines of each parcial index
        for idx in list(indexes.keys()):
            for _ in range(block_size - len(queues[idx])):
                try:
                    line = next(indexes[idx])
                    queues[idx].append(line.split(";"))
                except StopIteration:
                    del indexes[idx]
                    break

        #  while there are still blocks to merge
        while True:
            lower_term = '\U0010ffff'
            #   find the lowest term in the blocks
            for idx in list(queues.keys()):
                try:
                    term = queues[idx][0][0]
                    if term < lower_term:
                       lower_term = term
                       lower_idx = idx
                    elif term == lower_term:
                        queues[lower_idx][0].extend(queues[idx][0][1:])
                        del queues[idx][0]
                except IndexError:
                    if idx not in indexes:
                        del queues[idx]
                    continue

            #   add the lowest term to the final terms
            try:
                final_terms[lower_term]=queues[lower_idx][0][1:]
            except KeyError:
                break
            del queues[lower_idx][0]

            #   if the block is empty we need to fill it again
            if not queues[lower_idx]:

                new_final_terms[lower_term] = final_terms.pop(lower_term)
                self.save_index(final_terms, path = f"{self.index_output_path}index" , final = True, N = N)
                final_terms.clear()
                final_terms[lower_term] = new_final_terms.pop(lower_term)

                for idx in list(indexes.keys()):
                    for _ in range(block_size - len(queues[idx])):
                        try:
                            line = next(indexes[idx])
                            queues[idx].append(line.split(";"))
                        except StopIteration:
                            del indexes[idx]
                            break

        self.save_index(final_terms, path = f"{self.index_output_path}index", final = True, N = N)
        final_terms.clear()

    def save_index(self):
        raise NotImplementedError

    def clean_partial_index(self):
        for file in list(os.listdir(f"{self.index_output_path}.temp_index")):
            os.remove(f"{self.index_output_path}.temp_index/{file}")

    def start_final_index(self):
        #   delete the index file if it exists
        if os.path.exists(f"{self.index_output_path}index"):
            os.remove(f"{self.index_output_path}index")

        indexes = {}
        queues = {}
        for doc in list(os.listdir(f"{self.index_output_path}.temp_index")):
            #   open all the parcial indexes
            if doc.startswith("index"):
                indexes[doc] = Reader(f"{self.index_output_path}.temp_index/{doc}").read()
                queues[doc] = []

        self.stats["nr_parcial_indexes"] = len(indexes)

        return indexes, queues
    
    def create_dictionary(self):
        raise NotImplementedError

    def create_index_map(self, index):
        term_comp = self.last_term
        for i, term in enumerate(sorted(index)):
            #   if the first two letters of the term are different from the last term, we need to update the index map
            if term[:2] > term_comp:
                term_comp = term[:2]
                self.index_map[term_comp] = i + self.last_index
        
        #   update the last term and the last index taking into account the number of terms already indexed
        self.last_index += i
        self.last_term = term_comp

    def start_index_map(self):
        if os.path.exists(f"{self.index_output_path}index_map.json"):
            os.remove(f"{self.index_output_path}index_map.json")

    def write_map(self):
        with open(f"{self.index_output_path}index_map.json", 'w') as f:
            json.dump(self.index_map, f)

class Positional_Indexer(SPIMI):

    def __init__(self,**kwargs) -> None:
        super().__init__(**kwargs)

    def save_index(self, index: dict, path: str, final: bool = False, N: int = None):
        #   write to disk the index in the format: term;doc1:pos,pos,pos;doc2:pos,pos,pos;doc3:pos;...
        if final:
            with open(path, 'a') as f:
                for term in index:
                    f.write(f"{term};{';'.join(doc for doc in index[term])}\n")
            
            self.create_index_map(index)
        else:
            with open(path, 'w') as f:
                for term in sorted(index):
                    f.write(f"{term};{';'.join('{0}:{1}'.format(doc,','.join(map(str, index[term][doc]))) for doc in index[term])}\n")

    def create_dictionary(self):
        dictionary = open(f"{self.index_output_path}dictionary", 'w')

        with open(f"{self.index_output_path}index", 'r') as f:
            for line in f:
                term = line.split(";")[0]
                dictionary.write(f"{term}:{line.count(':')}\n")
        
        dictionary.close()


class Non_Positional_Indexer(SPIMI):

    def __init__(self,**kwargs) -> None:
        super().__init__(**kwargs)
    def save_index(self, index: dict, path: str, final: bool = False, N: int = None):
        #   write to disk the index in the format: term;doc1:freq;doc2:freq;doc3:freq;...
        if final:
            if not self.cache:
                with open(path, 'a') as f:
                    for term in index:
                        f.write(f"{term};{';'.join(doc for doc in index[term])}\n")
                        
            elif self.cache == "tfidf":
                with open(path, 'a') as f:
                    with open(f"{self.index_output_path}cache_{self.cache}_{self.smart}", 'a') as tfidf:
                        for term in index:
                            tfidfs = {}
                            #   calculate the tfidf for each document that contains the term
                            idfs = document_frequency_weighting(self.smart[1], {doc: int(doc.split(":")[1]) for doc in index[term]}, N)
                            for doc in index[term]:
                                doc_id, tf = doc.split(":")
                                #   calculate the tf weight for the term in the document
                                tfidfs[doc_id] = single_term_frequency_weighting(self.smart[0], int(tf)) * idfs[doc]
                            #   write the tfidf to the cache file
                            tfidf.write(f"{term};{';'.join('{}:{}'.format(doc, round(tfidf, 4)) for doc, tfidf in normalization_factor(self.smart[2], tfidfs).items())}\n")
                            #   write the index to the index file
                            f.write(f"{term};{';'.join(doc for doc in index[term])}\n")

            elif self.cache == "bm25":
                with open(path, 'a') as f:
                    with open(f"{self.index_output_path}cache_{self.cache}_{self.bm25_k1}_{self.bm25_b}", 'a') as bm25:
                        for term in index:
                            bm25s = {}
                            #   calculate the idf for each document that contains the term
                            idfs = document_frequency_weighting("t", {doc: len(index[term]) for doc in index[term]}, N)
                            for doc in index[term]:
                                doc_id, tf = doc.split(":")
                                #   calculate the bm25 for the term in the document
                                bm25s[doc_id] = rsv(bm25_k1=self.bm25_k1,
                                                    bm25_b=self.bm25_b,
                                                    idf=idfs[doc],
                                                    tf=int(tf),
                                                    dl=int(linecache.getline(f'{self.index_output_path}document_mapping', int(doc_id)+1).split(":")[1]),
                                                    avgdl=self.avg_dl)
                            #   write the bm25 to the cache file
                            bm25.write(f"{term};{';'.join('{}:{:}'.format(doc, round(bm25, 4)) for doc, bm25 in bm25s.items())}\n")
                            #   write the index to the index file
                            f.write(f"{term};{';'.join(doc for doc in index[term])}\n")
            self.create_index_map(index)

        else:
            with open(path, 'w') as f:
                for term in sorted(index):
                    f.write(f"{term};{';'.join(doc for doc in index[term])}\n")

    def create_dictionary(self):
        dictionary = open(f"{self.index_output_path}dictionary", 'w')

        with open(f"{self.index_output_path}index", 'r') as f:
            for line in f:
                block = line.split(";")
                dictionary.write(f"{block[0]}:{sum([int(doc.split(':')[1]) for doc in block[1:]])}\n")
        
        dictionary.close()
