from IPython.display import clear_output
from typing import List, Set, Union
from abc import abstractmethod
from functools import total_ordering
from os import path
import os
import pickle
import gc

class Index:
    def __init__(self):
        self.dic_index = {}
        self.set_documents = set()
        self.int_last_id = 1

    def index(self, term:str, doc_id:int, term_freq:int):
        if term not in self.dic_index:
            int_term_id = self.get_last_id()
            self.dic_index[term] = self.create_index_entry(int_term_id)
        else:
            int_term_id = self.get_term_id(term)

        self.add_index_occur(self.dic_index[term], doc_id, int_term_id, term_freq)


    def get_last_id(self) -> int:
        int_last_id = self.int_last_id
        self.int_last_id = self.int_last_id + 1
        return int_last_id

    @property
    def vocabulary(self) -> List:
        return [*self.dic_index]

    @property
    def document_count(self) -> int:
        return len(self.set_documents)

    @abstractmethod
    def get_term_id(self, term:str):
        raise NotImplementedError("Voce deve criar uma subclasse e essa deve sobrepor este método")


    @abstractmethod
    def create_index_entry(self, termo_id:int):
        raise NotImplementedError("Voce deve criar uma subclasse e essa deve sobrepor este método")

    @abstractmethod
    def add_index_occur(self, entry_dic_index, doc_id:int, term_id:int, freq_termo:int):
        raise NotImplementedError("Voce deve criar uma subclasse e essa deve sobrepor este método")

    @abstractmethod
    def get_occurrence_list(self, term:str) -> List:
        raise NotImplementedError("Voce deve criar uma subclasse e essa deve sobrepor este método")

    @abstractmethod
    def document_count_with_term(self,term:str) -> int:
         raise NotImplementedError("Voce deve criar uma subclasse e essa deve sobrepor este método")

    def finish_indexing(self):
        pass

    def __str__(self):
        arr_index = []
        for str_term in self.vocabulary:
            arr_index.append(f"{str_term} -> {self.get_occurrence_list(str_term)}")

        return "\n".join(arr_index)

    def __repr__(self):
        return str(self)

@total_ordering
class TermOccurrence:
    def __init__(self,doc_id:int,term_id:int, term_freq:int):
        self.doc_id = doc_id
        self.term_id = term_id
        self.term_freq = term_freq

    def write(self, idx_file):
        pass

    def __hash__(self):
    	return hash((self.doc_id,self.term_id))
    def __eq__(self,other_occurrence:"TermOccurrence"):
        if(not other_occurrence):
            return False
        return (other_occurrence and self.term_id == other_occurrence.term_id) \
        and self.doc_id == other_occurrence.doc_id

    def __lt__(self,other_occurrence:"TermOccurrence"):
        if(not other_occurrence):
            return True
        return other_occurrence and ((self.term_id < other_occurrence.term_id) \
        or (self.term_id == other_occurrence.term_id and self.doc_id < other_occurrence.doc_id))

    def __str__(self):
        return f"(term_id:{self.term_id} doc: {self.doc_id} freq: {self.term_freq})"

    def __repr__(self):
        return str(self)


#HashIndex é subclasse de Index
class HashIndex(Index):
    def get_term_id(self, term:str):
        return self.dic_index[term][0].term_id

    def create_index_entry(self, term_id:int) -> List:
        return []

    def add_index_occur(self, entry_dic_index:List[TermOccurrence], doc_id:int, term_id:int, term_freq:int):
        entry_dic_index.append(TermOccurrence(doc_id, term_id, term_freq))
        if(doc_id not in self.set_documents):
            self.set_documents.add(doc_id)

    def get_occurrence_list(self,term: str)->List:
        return self.dic_index.get(term, [])

    def document_count_with_term(self,term:str) -> int:
        return len(self.get_occurrence_list(term))





class TermFilePosition:
    def __init__(self,term_id:int,  term_file_start_pos:int=None, doc_count_with_term:int = None):
        self.term_id = term_id

        #a serem definidos após a indexação
        self.term_file_start_pos = term_file_start_pos
        self.doc_count_with_term = doc_count_with_term

    def __str__(self):
        return f"term_id: {self.term_id}, doc_count_with_term: {self.doc_count_with_term}, term_file_start_pos: {self.term_file_start_pos}"
    def __repr__(self):
        return str(self)

class FileIndex(Index):

    TMP_OCCURRENCES_LIMIT = 1000000
    INT_BYTE_SIZE = 4
    INT_OCCURRENCE_BYTE_SIZE = 3*INT_BYTE_SIZE

    def __init__(self):
        super().__init__()

        self.lst_occurrences_tmp = []
        self.idx_file_counter = 0
        self.str_idx_file_name_base = "occur_idx_file"
        self.str_idx_file_name = f"{self.str_idx_file_name_base}_{self.idx_file_counter}"

    def update_str_idx_file_name(self):
        self.str_idx_file_name = f"{self.str_idx_file_name_base}_{self.idx_file_counter}"

    def get_old_file_name(self):
        return f"{self.str_idx_file_name_base}_{self.idx_file_counter-1}"

    def get_term_id(self, term:str):
        return self.dic_index[term].term_id

    def create_index_entry(self, term_id:int) -> TermFilePosition:
        return  TermFilePosition(term_id)

    def add_index_occur(self, entry_dic_index:TermFilePosition,  doc_id:int, term_id:int, term_freq:int):
        self.lst_occurrences_tmp.append(TermOccurrence(doc_id,term_id,term_freq))

        if len(self.lst_occurrences_tmp) >= FileIndex.TMP_OCCURRENCES_LIMIT:
            self.save_tmp_occurrences()

    def next_from_list(self) -> TermOccurrence:
        if len(self.lst_occurrences_tmp) > 0:
            next_occurrence = self.lst_occurrences_tmp.pop(0)
            return next_occurrence
        else:
            return None

    def read_int_byte_size(self, file) -> int:
        bytes_from_file = file.read(self.INT_BYTE_SIZE)
        if not bytes_from_file:
            return None
        else:
            return  int.from_bytes(bytes_from_file,byteorder='big')

    def next_from_file(self,file) -> TermOccurrence:
        #TODO: Descobrir como usar pickle
        doc_id = self.read_int_byte_size(file)
        if not doc_id:
            return None
        term_id = self.read_int_byte_size(file)
        term_freq = self.read_int_byte_size(file)

        return TermOccurrence(doc_id, term_id, term_freq)

    def append_ocurrence_to_file(self, file, obj_occurrence:TermOccurrence):
        if(obj_occurrence):
            file.write(obj_occurrence.doc_id.to_bytes(self.INT_BYTE_SIZE, byteorder="big"))
            file.write(obj_occurrence.term_id.to_bytes(self.INT_BYTE_SIZE, byteorder="big"))
            file.write(obj_occurrence.term_freq.to_bytes(self.INT_BYTE_SIZE,byteorder="big"))

    def increment_idx_file_counter(self):
        self.idx_file_counter = self.idx_file_counter + 1

    def save_ocurrences_on_file(self, str_file_name:str, lst_occurrences):
        with open(str_file_name, "wb") as file:
            for obj_occurrence in lst_occurrences:
                self.append_ocurrence_to_file(file, obj_occurrence)

    def write_sorted(self, current_file, next_file):
        next_from_file = self.next_from_file(current_file)
        next_from_list = self.next_from_list()
        print(next_from_file, next_from_list)
        while (next_from_file or next_from_list):
            if (next_from_file and next_from_file < next_from_list):
                self.append_ocurrence_to_file(next_file, next_from_file)
                next_from_file = self.next_from_file(current_file)
            else:
                self.append_ocurrence_to_file(next_file, next_from_list)
                next_from_list = self.next_from_list()

    def save_tmp_occurrences(self):
        gc.disable()
        self.lst_occurrences_tmp.sort()
        idx_file_counter = self.idx_file_counter
        if(idx_file_counter == 0):
            self.save_ocurrences_on_file(self.str_idx_file_name, self.lst_occurrences_tmp)
        else:
            str_current_file_name = self.str_idx_file_name
            self.update_str_idx_file_name()
            str_next_file_name = self.str_idx_file_name

            with open(str_next_file_name, "wb") as next_file:
                with open(str_current_file_name, "rb") as current_file:
                    self.write_sorted(current_file, next_file)

        self.remove_file(self.get_old_file_name())
        self.lst_occurrences_tmp = []
        self.increment_idx_file_counter()
        gc.enable()

    def finish_indexing(self):
        if len(self.lst_occurrences_tmp) > 0:
            self.save_tmp_occurrences()

        dic_term_by_id = self.get_dic_term_by_id()
    
        int_file_position = 0
        int_document_count = 0
        int_current_id = 0

        with open(self.str_idx_file_name,'rb') as idx_file:
           
            termOcurrence = self.next_from_file(idx_file)
           
            while (termOcurrence != None):
                
                if (termOcurrence.term_id != int_current_id):
                    dic_term_by_id[termOcurrence.term_id].term_file_start_pos = int_file_position
                    
                    if(int_current_id > 0):
                        dic_term_by_id[int_current_id].doc_count_with_term = int_document_count
                    
                    int_document_count = 1
                    int_current_id = int_current_id + 1
                else:
                    int_document_count = int_document_count + 1 
                    
                termOcurrence = self.next_from_file(idx_file)
                int_file_position = int_file_position + self.INT_OCCURRENCE_BYTE_SIZE

            dic_term_by_id[int_current_id].doc_count_with_term = int_document_count

    def get_dic_term_by_id(self):
        dic_term_by_id = {}
        for str_term, obj_term in self.dic_index.items():
            dic_term_by_id[obj_term.term_id] = obj_term
        return dic_term_by_id

    def get_occurrence_list(self,term: str)->List:
        if term in self.dic_index.keys():
            termFilePosition = self.dic_index[term]
            list_ocurrences = []
            with open(self.str_idx_file_name, 'rb') as file:
                file.seek(termFilePosition.term_file_start_pos)
                for i in range(termFilePosition.doc_count_with_term):
                    list_ocurrences.append(self.next_from_file(file))
            return list_ocurrences
        return []

    def document_count_with_term(self,term:str) -> int:
        if term in self.dic_index.keys():
            termFilePosition = self.dic_index[term]
            return termFilePosition.doc_count_with_term
        return 0

    def remove_file(self, file):
        if os.path.exists(file):
            os.remove(file)
