import streamlit as st
import pandas as pd
import bcrypt


class Authentication:    
    @staticmethod
    def create_account(user_name,
                       password,
                       type,
                      ):
        try:
            senha_bytes = password.encode("utf-8")
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(senha_bytes, salt)
            dict_user = {"NOME": user_name,
                         "SENHA": senha_hash,
                         "TIPO":type}
            
            df = pd.DataFrame(dict_user, index=[0])

            return df
                
        except Exception as e:
            st.error(f"Erro ao criar o usuário: {e}")        
            return None
    
    @staticmethod
    def compara_senha(df_banco,
                       senha):
        if df_banco.empty:
            return {"valido": False, "tipo": "geral"}
        
        try:
            comparar_bytes = senha.encode("utf-8")            
            password_banco = df_banco['SENHA'].iloc[0]   
            if isinstance(password_banco, str):
                password_banco = password_banco.encode("utf-8")
            tipo = df_banco['TIPO'].iloc[0]         
            if bcrypt.checkpw(comparar_bytes, password_banco):
                return {"valido": True, "tipo": tipo}
                
            else:
                return {"valido": False, "tipo": "geral"}
                            
        except Exception as e:
            st.error(f"Erro na comparação de senha: {e}")
            return {"valido": False, "tipo": "geral"}
