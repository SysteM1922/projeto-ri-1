from tokenizer import Tokenizer
from reader import JsonReader
import time

start = time.perf_counter()
path = "collections/pubmed_2022_small.jsonl"

tokenizer = Tokenizer(regular_exp="[a-zA-Z0-9]{3,}", stemmer="pystemmer", lowercase=True)
doc = JsonReader(path)

dic = {}

for item in doc.read():
    for token in tokenizer.tokenize(item["title"] + item["abstract"]):
        pass
    

print(time.perf_counter() - start)

