import uuid
import os
from datetime import datetime
import pandas as pd


class DenunciaClass:
        
    def __init__(self,
                 path_pai_evidencias:str):
        
        self.codigo = self.cod_unq()
        self.path_pai_evidencias = path_pai_evidencias
    
    def cod_unq (self) -> str:
        try:
            primeira_parte = datetime.now().strftime("%Y%m%d")
            segunda_parte = str(uuid.uuid4())[:8].upper()
            codigo = str(primeira_parte)+"-"+str(segunda_parte)
            return codigo
        except Exception as e:
            print(f"Erro ao gerar código:{e}")
            return None
        
    def criar_path_evidencias(self,
                              codigo:str)->str:
        try:
            path = os.path.join(self.path_pai_evidencias,
                                codigo)
            os.makedirs(path, exist_ok=True)
            return path
        except Exception as e:
            print(f'Erro ao criar a pasta de evidencias:{e}')
            return None
        
    def nova_denuncia(self,
                      categoria:str,
                      conteudo:str,
                      gravidade:str,
                      datetime:datetime                     
                      ) -> dict:
        
        codigo = self.codigo
        path_evidencias = self.criar_path_evidencias(codigo=codigo)
        
        try:
            dict_denuncia = {"CODIGO":[codigo],
                            "DATA_ABERTURA":[datetime],
                            "CATEGORIA":[categoria],
                            "CONTEUDO":[conteudo],
                            "STATUS":1,
                            "GRAVIDADE":gravidade,
                            "PATH_EVID":[path_evidencias]          
            }
            dataframe_denuncia = pd.DataFrame(dict_denuncia)
            return dataframe_denuncia, codigo, path_evidencias
        except Exception as e:
            print(f"Erro na criação do DFdf : {e}")        
            return None, None, None
        
    def resposta_new (codigo:str,
                      last_resp:int,
                      conteudo:str,
                      user:None):
        try:
            dict_resposta = {"CODIGO":[codigo],
                             "USER":[user],
                             "CONTEUDO":[conteudo],
                             "SEQ_RESP":last_resp+1}
            dataframe_resposta = pd.DataFrame(dict_resposta)
            return dataframe_resposta
        except Exception as e:
            print(f"Erro ao gerar a resposta: {e}")
            return None

# path_evid = r'C:\Users\Higor Rodrigues\Desktop\PROJETOS\PROJETO_DENUNCIAS_INTERNAS\DENUNCIAS_INTERNAS\EVIDENCIAS'
# data = datetime.now()
# categoria = "teste_categoria"
# conteudo = "Conteudo teste para ver se está funcionando perfeitamente a minha classe"




# config = DenunciaClass(path_pai_evidencias=path_evid)
# denuncia = config.nova_denuncia(categoria=categoria,
#                                 conteudo=conteudo,
#                                 datetime=data)

# df = denuncia[0]
# codigo = denuncia[-1]