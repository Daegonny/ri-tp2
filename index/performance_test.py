from IPython.display import clear_output
from index.structure import *

from datetime import datetime
import math
import tracemalloc
import unittest
from random import randrange,seed






class PerformanceTest(unittest.TestCase):
    NUM_DOCS = 2000
    NUM_TERM_PER_DOC = 500

    def setUp(self):
        self.index = HashIndex()

    def create_vocabulary(self):
        vocabulary = []
        for i in range(65,91):
            for j in range(65,91):
                for k in range(65,91):
                    vocabulary.append(f"{chr(i)}{chr(j)}{chr(k)}")
        return vocabulary

    def print_status(self,count:int,total:int):

        delta = datetime.now()-self.time
        porc_complete = math.floor(count/total*100)
        current, peak = tracemalloc.get_traced_memory()

        clear_output(wait=True)
        print(f"Memoria usada: {current / 10**6:,} MB; Máximo {peak / 10**6:,} MB",flush=True)
        print(f"Indexando ocorrencia #{count:,}/{total:,} ({porc_complete}%)",flush=True)
        print(f"Tempo gasto: {delta.total_seconds()}s",flush=True)

    def index_words(self):
        count = 0
        seed(10)
        words = []
        for doc_i in range(PerformanceTest.NUM_DOCS):
            for term_j in range(PerformanceTest.NUM_TERM_PER_DOC):
                idx_term = randrange(0,len(self.vocabulary))
                str_term = self.vocabulary[idx_term]
                self.index.index(str_term, doc_i, (count%10)+1)
                #indiceTeste.index(vocabulario[(count+1)%15625], d, (count%10)+1);
                if count%50000==0:
                    self.print_status(count,PerformanceTest.NUM_DOCS*PerformanceTest.NUM_TERM_PER_DOC)

                count+=1
        return count

    def test_performance(self):


        print("Criando vocabulário...")
        self.vocabulary = self.create_vocabulary()

        tracemalloc.start()
        self.time = datetime.now()
        total = self.index_words()
        self.print_status(total,total)
        tracemalloc.stop()

import time
class FilePerformanceTest(PerformanceTest):
    def setUp(self):
        self.index = FileIndex()

def test():
    for i in range(10):
        clear_output(wait=True)
        print(f"oi {i}")
        time.sleep(1)

if __name__ == "__main__":
    unittest.main()
