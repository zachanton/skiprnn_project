import codecs
import logging
import numpy as np

logger = logging.getLogger(__name__)

class W2VEmbReader:
    """
    Word2Vec Embedding Reader class

    Used to read word embedding from word2vec output
    and then pre-initialize the embedding matrix of the Neural Network
    """
    
    def __init__(self, emb_path, emb_dim=None):
        """
        Initialize the class with the word2vec word embedding output
        Able to handle format with header and without header
        """
        logger.info('Loading embeddings from: ' + emb_path)
        has_header=False
        with codecs.open(emb_path, 'r', encoding='utf8') as emb_file:
            tokens = emb_file.readline().strip().split()
            if len(tokens) == 2:
                try:
                    int(tokens[0])
                    int(tokens[1])
                    has_header = True
                except ValueError:
                    pass
        if has_header:
            with codecs.open(emb_path, 'r', encoding='utf8') as emb_file:
                tokens = emb_file.readline().strip().split()
                assert len(tokens) == 2, 'The first line in W2V embeddings must be the pair (vocab_size, emb_dim)'
                self.vocab_size = int(tokens[0])
                self.emb_dim = int(tokens[1])
                assert self.emb_dim == emb_dim, 'The embeddings dimension does not match with the requested dimension'
                self.embeddings = {}
                counter = 0
                for line in emb_file:
                    tokens = line.strip().split()
                    assert len(tokens) == self.emb_dim + 1, 'The number of dimensions does not match the header info'
                    word = tokens[0]
                    vec = tokens[1:]
                    self.embeddings[word] = vec
                    counter += 1
                assert counter == self.vocab_size, 'Vocab size does not match the header info'
        else:
            with codecs.open(emb_path, 'r', encoding='utf8') as emb_file:
                self.vocab_size = 0
                self.emb_dim = -1
                self.embeddings = {}
                for line in emb_file:
                    tokens = line.strip().split()
                    if self.emb_dim == -1:
                        self.emb_dim = len(tokens) - 1
                        assert self.emb_dim == emb_dim, 'The embeddings dimension does not match with the requested dimension'
                    else:
                        assert len(tokens) == self.emb_dim + 1, 'The number of dimensions does not match the header info'
                    word = tokens[0]
                    vec = tokens[1:]
                    self.embeddings[word] = vec
                    self.vocab_size += 1
        
        logger.info('  #vectors: %i, #dimensions: %i' % (self.vocab_size, self.emb_dim))
    
    def get_emb_given_word(self, word):
        try:
            return self.embeddings[word]
        except KeyError:
            return None
    
    def get_emb_matrix_given_vocab(self, vocab, emb_matrix):
        """
        Given a vocabulary list and the word embedding matrix,
        pre-initialize the word embedding matrix of known words with
        the word embeddings that has already been stored earlier in the constructor.
        """
        counter = 0.
        for word, index in vocab.items():
            try:
                emb_matrix[index] = [float(i) for i in self.embeddings[word]]
                counter += 1
            except KeyError:
                pass
        logger.info('%i/%i word vectors initialized (hit rate: %.2f%%)' % (counter, len(vocab), 100*counter/len(vocab)))
        return emb_matrix
    
    def get_emb_dim(self):
        return self.emb_dim
    
