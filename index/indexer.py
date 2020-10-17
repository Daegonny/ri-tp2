from nltk.stem.snowball import SnowballStemmer
from bs4 import BeautifulSoup
import string
from nltk.tokenize import word_tokenize
import os


class Cleaner:
    def __init__(self,stop_words_file:str,language:str,
                        perform_stop_words_removal:bool,perform_accents_removal:bool,
                        perform_stemming:bool):
        self.set_stop_words = self.read_stop_words(stop_words_file)

        self.stemmer = SnowballStemmer(language)
        in_table =  "áéíóúâêôçãẽõü"
        out_table = "aeiouaeocaeou"
        #altere a linha abaixo para remoção de acentos (Atividade 11)
        self.accents_translation_table = None
        self.set_punctuation = set(string.punctuation)

        #flags
        self.perform_stop_words_removal = perform_stop_words_removal
        self.perform_accents_removal = perform_accents_removal
        self.perform_stemming = perform_stemming

    def html_to_plain_text(self,html_doc:str) ->str:
        return None

    def read_stop_words(self,str_file):
        set_stop_words = set()
        with open(str_file, "r") as stop_words_file:
            for line in stop_words_file:
                arr_words = line.split(",")
                [set_stop_words.add(word) for word in arr_words]
        return set_stop_words
    def is_stop_word(self,term:str):
        return True

    def word_stem(self,term:str):
        return ""


    def remove_accents(self,term:str) ->str:
        return None


    def preprocess_word(self,term:str) -> str:

        return None



class HTMLIndexer:
    cleaner = Cleaner(stop_words_file="stopwords.txt",
                        language="portuguese",
                        perform_stop_words_removal=True,
                        perform_accents_removal=True,
                        perform_stemming=True)
    def __init__(self,index):
        self.index = index

    def text_word_count(self,plain_text:str):
        dic_word_count = {}

        return dic_word_count
    def index_text(self,doc_id:int, text_html:str):
        pass

    def index_text_dir(self,path:str):

        for str_sub_dir in os.listdir(path):
            path_sub_dir = f"{path}/{str_sub_dir}"
