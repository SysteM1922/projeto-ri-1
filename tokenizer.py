import re
import Stemmer

class Tokenizer:

    __instance = None

    @staticmethod
    def getInstance():
        if Tokenizer.__instance == None:
            Tokenizer()
        return Tokenizer.__instance

    def __init__(self, minL: int = 3, stopwords_path: str = "default_stopwords.txt", stemmer: str = None, regular_exp: str = "[a-zA-Z0-9]{3,}", lowercase: bool = True):
        if Tokenizer.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.minL = minL
            self.stopwords_path = stopwords_path
            self.stemmer = None
            if stemmer == "pystemmer":
                self.stemmer = Stemmer.Stemmer('english')
            self.regular_exp = re.compile(regular_exp)
            self.lowercase = lowercase
            self.stopwords = set()
            self._load_stopwords()
            Tokenizer.__instance = self

    def _load_stopwords(self):
        with open(self.stopwords_path, 'r') as f:
            self.stopwords = set(f.read().splitlines())

    def tokenize(self, text: str):
        #   remove punctuation
        tokens = self.regular_exp.findall(text)

        if self.lowercase:
            #   lowercase and remove stopwords
            if self.stemmer == None:
                tokens = [token.lower() for token in tokens if token.lower() not in self.stopwords]
            else:
                tokens = [self.stemmer.stemWord(token.lower()) for token in tokens if token.lower() not in self.stopwords]
            
        else:
            #   remove stopwords
            if self.stemmer == None:
                tokens = [token for token in tokens if token not in self.stopwords]
            else:
                tokens = [self.stemmer.stemWord(token) for token in tokens if token not in self.stopwords]

        #   remove tokens with less than minL characters
        tokens = [token for token in tokens if len(token) > self.minL-1]

        return tokens
        

        

    