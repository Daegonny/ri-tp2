from .structure import *
import unittest
from .index_structure_test import StructureTest
from .performance_test import PerformanceTest



class FileIndexTest(unittest.TestCase):

    def check_idx_file(self, obj_index, set_occurrences):
        #verifica a ordem das ocorrencias
        self.assertEqual(len( obj_index.lst_occurrences_tmp),0,"A lista de ocorrencias deve ser zerada após chamar o método save_tmp_occurrences")
        last_occur = TermOccurrence(float('-inf'),float('-inf'),10)
        set_file_occurrences = set()
        with open(obj_index.str_idx_file_name,"rb") as idx_file:
            occur = obj_index.next_from_file(idx_file)
            while occur is not None:
                self.assertTrue(occur>last_occur, msg=f"A ocorrencia {last_occur} foi colocada de forma incorreta antes da ocorrencia {occur}")
                set_file_occurrences.add(occur)
                last_occur = occur
                occur = obj_index.next_from_file(idx_file)

        sobra_arquivo = set_file_occurrences-set_occurrences
        sobra_lista = set_occurrences-set_file_occurrences
        self.assertEqual(len(sobra_arquivo),0, f"Existem ocorrências no arquivo que não estavam na 'lst_occurrences_tmp': {sobra_arquivo} ")
        self.assertEqual(len(sobra_lista),0, f"As seguintes ocorrências não foram inseridas no arquivo de indice: {sobra_lista} ")

    def test_save_tmp_occurrences(self):

        #testa a primeira vez (adicionando tudo na primeira vez)
        self.index = FileIndex()
        set_occurrences = []
        self.index.lst_occurrences_tmp = [TermOccurrence(2,4,5),
                                        TermOccurrence(2,2,1),
                                        TermOccurrence(1,2,1),
                                        TermOccurrence(1,1,3)]
        set_occurrences = set(self.index.lst_occurrences_tmp)
        self.index.save_tmp_occurrences()
        self.check_idx_file(self.index, set_occurrences)
        print("Primeira execução (criação inicial do indice) [ok]")

        #adicina alguns
        self.index.lst_occurrences_tmp = [TermOccurrence(1,3,3),
                                        TermOccurrence(2,3,4)]
        set_occurrences = set_occurrences | set(self.index.lst_occurrences_tmp)
        self.index.save_tmp_occurrences()
        self.check_idx_file(self.index, set_occurrences)
        print("Inserção de alguns itens - teste 1/2 [ok]")




        #adiciona mais alguns
        self.index.lst_occurrences_tmp = [TermOccurrence(2,1,2),
                                        TermOccurrence(3,2,2),
                                        TermOccurrence(3,1,1)]

        #checa ordenação do arquivo e verifica todas as ocorrencias existem
        set_occurrences = set_occurrences|set(self.index.lst_occurrences_tmp)
        self.index.save_tmp_occurrences()
        self.check_idx_file(self.index, set_occurrences)
        print("Inserção de alguns itens - teste 2/2 [ok]")

    def test_finish_indexing(self):
        self.index = FileIndex()
        self.index.lst_occurrences_tmp = [
                                        TermOccurrence(1,1,3),
                                        TermOccurrence(2,1,2),
                                        TermOccurrence(3,1,1),
                                        TermOccurrence(1,2,1),
                                        TermOccurrence(2,2,1),
                                        TermOccurrence(3,2,2),
                                        TermOccurrence(1,3,3),
                                        TermOccurrence(1,4,5),
                                        TermOccurrence(2,4,5),
                                        ]


        print("Lista de ocorrências a serem testadas:")
        for i,occ in enumerate(self.index.lst_occurrences_tmp):
            print(f"{occ}")
        x = 100
        int_size_of_occur = None
        with open("teste_file.idx","wb") as file:
            self.index.append_ocurrence_to_file(file, self.index.lst_occurrences_tmp[0])
            int_size_of_occur = file.tell()

        print(f"Tamanho de cada ocorrência: {int_size_of_occur} bytes")
        self.index.save_tmp_occurrences()
        #verifica, para cada posição
        self.index.dic_index = {"casa":TermFilePosition(1),
                                "verde":TermFilePosition(2),
                                "prédio":TermFilePosition(3),
                                "amarelo":TermFilePosition(4)}
        self.index.finish_indexing()

        arr_termos = ["casa","verde","prédio","amarelo"]
        #testa se o id manteve-se o mesmo
        [self.assertEqual(self.index.dic_index[arr_termos[i]].term_id,i+1,f"O id do termo {i+1} mudou para {self.index.dic_index[arr_termos[i]].term_id}") for i in range(4)]



        #testa se a quantidade de documentos que possuem um determinado termo está correto
        arr_pos_por_termo = [0,int_size_of_occur*3,int_size_of_occur*6,int_size_of_occur*7]
        arr_pos = [1,4,7,8]
        [self.assertEqual(self.index.dic_index[arr_termos[i]].term_file_start_pos,arr_pos_por_termo[i],f"A posição inicial do termo de id {i+1} no arquivo seria {arr_pos_por_termo[i]} (ou seja, antes da {arr_pos[i]}ª ocorrencia) e não {self.index.dic_index[arr_termos[i]].term_file_start_pos}") for i in range(4)]

        #testa se a quantidade de documentos que possuem um determinado termo está correto
        arr_doc_por_termo = [3,3,1,2]
        [self.assertEqual(self.index.dic_index[arr_termos[i]].doc_count_with_term,arr_doc_por_termo[i],f"A quantidade de documentos que possuem o termo de id {self.index.dic_index[arr_termos[i]].term_id} seria {arr_doc_por_termo[i]} e não {self.index.dic_index[arr_termos[i]].doc_count_with_term}") for i in range(4)]

if __name__ == "__main__":
    unittest.main()
