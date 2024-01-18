import math

def load_index(path_to_index: str) -> dict:

        index = {}
        with open(path_to_index, 'r') as f:
            for line in f:

                # Obtain terms and documents
                block = line.split(";")

                term = block[0]
                if term not in index:
                    index[term] = {}

                for doc in block[1:]:
                    doc_id, counter = doc.split(":")
                    index[term][doc_id] = int(counter)

        return index


def load_terms_freq(path_to_dictionary: str) -> dict:

    terms_freq = {}
    with open(path_to_dictionary, 'r') as f:
        for line in f:
            term, freq = line.split(":")
            terms_freq[term] = int(freq)

    return terms_freq


# Calculates the term frequency with algorithm tf
def term_frequency_weighting(smart, terms_freq) -> dict:
    if smart == 'n':
        # Return natural term frequency
        return terms_freq
    
    if smart == 'l':
        # Return logarithmic term frequency
        return {term: 1 + math.log10(freq) for term, freq in terms_freq.items()}

    if smart == 'b':
        # Return boolean term frequency
        return {term: 1 for term in terms_freq}

    raise NotImplementedError()


# Calculates the document frequency with algorithm df
def document_frequency_weighting(smart, freqs, N) -> dict:

    if smart == 'n':
        # Return no document frequency (always 1)
        return {term: 1 for term in freqs}

    if smart == 't':
        # Return idf
        return {term: math.log10(N / doc_freq) for term, doc_freq in freqs.items()}

    if smart == 'p':
        # Return prob idf
        return {term: max(0, math.log10((N - doc_freq) / doc_freq)) for term, doc_freq in freqs.items()}

    raise NotImplementedError()


# Calculates the normalization factor with algorithm norm
def normalization_factor(smart, weights) -> dict:

    if smart == 'n':
        # Return no normalization
        return weights

    if smart == 'c':
        # Return cosine normalization
        doc_norm = math.sqrt(sum(weight ** 2 for weight in weights.values()))
        return {term: weight / doc_norm for term, weight in weights.items()}
        
    raise NotImplementedError()

def single_term_frequency_weighting(smart, freq) -> int:

    if smart == 'n':
        # Return natural term frequency
        return freq
    
    if smart == 'l':
        # Return logarithmic term frequency
        return 1 + math.log10(freq)

    if smart == 'b':
        # Return boolean term frequency
        return 1

    raise NotImplementedError()

def rsv(bm25_b:float, bm25_k1:float, idf: float, tf: int, dl: int, avgdl: float):

    return idf * ((tf * (bm25_k1 + 1)) / (tf + bm25_k1 * (1-bm25_b) + bm25_b * (dl / avgdl)))