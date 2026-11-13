from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import streamlit as st
import pandas as pd
import bcrypt
import time


class ReadEditDB:
    def __init__(_self, engine):
        _self.engine = engine

    @st.dialog("Alterar senha")
    def mudar_senha(_self):
        cod_usu = st.text_input("Codigo Usuario: ", type='default')
        nova_senha = st.text_input("Nova Senha: ", type="password")

        if cod_usu and nova_senha:
            nova_senha_bytes = nova_senha.encode("utf-8")
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(nova_senha_bytes, salt)

            if st.button("MUDAR SENHA"):
                query = text("""
                UPDATE financeiro.USERS
                SET SENHA = :nova_senha
                WHERE COD_USUARIO = :cod_usu
                """)
                try:
                    with _self.engine.begin() as conn:
                        conn.execute(query, {
                            "nova_senha": senha_hash,
                            "cod_usu": cod_usu})
                    st.toast("Senha ajustada com Sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao trocar a senha: {e}")
 
    def mudar_status(_self, status, codigo):
        query= text("""
        UPDATE denuncia_anonima.DENUNCIAS_PRIMARIO
        SET STATUS = :novo_status
        WHERE CODIGO = :codigo
        """)
        try:
            with _self.engine.begin() as conn:
                conn.execute(query,{
                    "novo_status":status,
                    "codigo":codigo})
                conn.commit()
                st.toast("Status Ajustado com Sucesso")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao ajutar status: {e}")

    def excluir_registro(_self, table,database, cod_transacao):
        query= text(f"""
        DELETE FROM {database}.{table}
        WHERE ID_TRANSACAO = :cod_transacao
        """)
        try:
            with _self.engine.begin() as conn:
                conn.execute(query,{
                    "cod_transacao":cod_transacao})
                conn.commit()
                st.toast(f"✅ Registro {cod_transacao} excluido com sucesso!")
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao excluir registro: {e}")

            
    def usuarios_read(_self, database, table):
        query = f"""
        SELECT *
        FROM {database}.{table}
        WHERE 1=1
        """
        try:
            with _self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
            
            if not df.empty:
                return df
            else:                
                st.error("Usuarios não encontrados")
                time.sleep(1)
                return pd.DataFrame()
        except Exception as e:
            print(f"Erro na consulta de usuarios: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)
    def usuarios_read_login(_self, database, table, usuario):
        query = f"""
        SELECT *
        FROM {database}.{table}
        WHERE 1=1
        AND COD_USUARIO = {usuario}
        """
        try:
            with _self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
            
            if not df.empty:
                return df
            else:                
                st.error("Usuarios não encontrados")
                time.sleep(1)
                return pd.DataFrame()
        except Exception as e:
            print(f"Erro na consulta de usuarios: {e}")
            return pd.DataFrame()
 

            
    def orc_read(_self, database, table, mesano_filtro):
        query = f"""
        SELECT *
        FROM {database}.{table}
        WHERE 1=1
        AND MESANO_VIGENCIA = {mesano_filtro}
        """
        try:
            with _self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
            
            if not df.empty:
                return df
            else:                
                # st.error(f"Tabela {table} não encontrada")
                time.sleep(1)
                return pd.DataFrame()
        except Exception as e:
            print(f"Erro na consulta da tabela {table}: {e}")
            return pd.DataFrame()
        
    @st.cache_data(ttl=300)
    def geral_read(_self, database, table):
        query = f"""
        SELECT *
        FROM {database}.{table}
        WHERE 1=1
        """
        try:
            with _self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
            
            if not df.empty:
                return df
            else:                
                # st.error(f"Tabela {table} não encontrada")
                time.sleep(1)
                return pd.DataFrame()
        except Exception as e:
            print(f"Erro na consulta da tabela {table}: {e}")
            return pd.DataFrame()


    def mov_read(_self, database, table, mes_filtro, ano_filtro):
        query = f"""
        SELECT *
        FROM {database}.{table}
        WHERE 1=1
        AND DATA_PAGAMENTO >= '{ano_filtro}-{mes_filtro}-1'
        AND DATA_PAGAMENTO <=  LAST_DAY('{ano_filtro}-{mes_filtro}-1')
        """
        try:
            with _self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
            
            if not df.empty:
                return df
            else:                
                # st.error(f"Tabela {table} não encontrada")
                time.sleep(1)
                return pd.DataFrame()
        except Exception as e:
            print(f"Erro na consulta da tabela {table}: {e}")
            return pd.DataFrame()

    def upload_msql_df(_self, 
                       df, 
                       table, 
                       database):
        try:
            if not df.empty:
                st.toast(f"Iniciando importação de {table}")
                with _self.engine.begin() as conn:
                    df.to_sql(
                        name=f'{table}',
                        schema=f'{database}',
                        con=conn,
                        if_exists='append',
                        index=False
                    )
                st.toast("✅ Movimentação registrada com sucesso")
        except IntegrityError as e:
            st.error(f"Erro na gravação da denuncia: {e.orig}")
            print(f"Erro na gravação da denuncia: {e.orig}")
        except Exception as e:
            st.error(f"Erro inesperado na importação para o banco de dados: {e}")
            print(f"Erro inesperado na importação para o banco de dados: {e}")
    
    def upload_user_df(_self, 
                       df, 
                       table, 
                       database):
        try:
            if not df.empty:
                st.toast(f"Iniciando importação de {table}")
                with _self.engine.begin() as conn:
                    df.to_sql(
                        name=f'{table}',
                        schema=f'{database}',
                        con=conn,
                        if_exists='append',
                        index=False
                    )
                st.toast("✅ Usuario registrado com sucesso")
        except IntegrityError as e:
            st.error(f"Erro ao registrar Usuario: {e.orig}")
            print(f"Erro ao registrar Usuario:  {e.orig}")
        except Exception as e:
            st.error(f"Erro inesperado na importação para o banco de dados: {e}")
            print(f"Erro inesperado na importação para o banco de dados: {e}") 
