import json
import gzip

class Reader:
    def __init__(self, path_to_file: str):
        self.type = path_to_file.split(".")[-1]
        self.file = self._open_file(path_to_file)

    def read(self):
        for line in self.file:
            yield line.strip()
        self.file.close()

    def _open_file(self, path_to_collection: str):
        #   read gzipped file
        if self.type == "gz":
            return gzip.open(path_to_collection, 'rt')
        #   read json file
        else:
            return open(path_to_collection, 'r')

class JsonReader(Reader):

    def __init__(self, path_to_collection: str):
        super().__init__(path_to_collection)
        
    def read(self):
        for line in self.file:
            yield json.loads(line.strip())
        self.file.close()