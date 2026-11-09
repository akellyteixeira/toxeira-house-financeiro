import pyodbc
import pandas as pd
from dotenv import load_dotenv
from funcoes_aux import ler_banco_extrair_dp
import os
import paramiko
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

#from upload_banco import UploadBanco ## esta em beckup
load_dotenv(override=True)

df_etinerarios = None
df_empresas = None
df_pessoas = None

# --- CONFIGURANDO O TUNEL SSH E A CONEXAO COM O BANCO DA VPS ---
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.RSAKey

SSH_HOST = os.getenv('SSH_HOST')
SSH_USER = os.getenv('SSH_USER')
SSH_PASSWORD = os.getenv('SSH_PASSWORD') 

DB_USER = os.getenv('DB_USER') 
DB_PASSWORD = os.getenv('DB_PASSWORD')  

tunnel = SSHTunnelForwarder(
    (SSH_HOST, 22),
    ssh_username=SSH_USER,
    ssh_password=SSH_PASSWORD, 
    remote_bind_address=('127.0.0.1', 3306),
    host_pkey_directories=[]
)

# --- CONFIGURANDO CONEXAO COM O BANCO DO DOMINIO ---
conn_str = (
    "Driver={SQL Anywhere 17};"
    f"UID={os.getenv('LOGIN_DP')};"
    f"PWD={os.getenv('SENHA_DP')};"
    f"Host={os.getenv('SERVIDOR_DP')};"
    f"DBN={os.getenv('BASE_DADOS_DP')};"
)

query_colaboradores = """
    SELECT v1.*,
           v2.nome_cargo,
           v3.DESCRICAO as 'Descricao_afastamento'
    FROM (
        SELECT  codi_emp,
                i_empregados,
                admissao,
                i_filiais,
                i_horaemp,
                nome,
                categoria,
                forma_pagto,
                cpf,
                i_cargos,
                I_AFASTAMENTOS
        FROM bethadba.foempregados f 
        WHERE 1=1
    )v1
    LEFT JOIN (
        SELECT codi_emp,
                i_cargos,
                nome as 'nome_cargo'
        FROM bethadba.FOCARGOS
        WHERE 1=1
    )v2 ON v1.codi_emp=v2.codi_emp AND v1.i_cargos = v2.i_cargos
    LEFT JOIN(
        SELECT I_AFASTAMENTOS, DESCRICAO 
        FROM bethadba.FOAFASTAMENTOS_TIPOS f2  
        WHERE 1=1
    )v3 ON v1.I_AFASTAMENTOS = v3.I_AFASTAMENTOS
"""

query_etinerarios = """
SELECT v1.*,
       v2.COMPETENCIA,
       v2.VALOR
FROM(
    SELECT I_LINHAS,
           I_EMPONI,
           NOME
    FROM bethadba.folinhas f 
    WHERE 1=1
    )v1 
LEFT JOIN(
    WITH FilaOrdenada AS (
        SELECT 
            I_LINHAS ,
            COMPETENCIA ,
            valor,
            ROW_NUMBER() OVER(PARTITION BY I_LINHAS ORDER BY COMPETENCIA DESC) AS posicao
        FROM bethadba.FOLINHAS_VALORES_PASSAGEM  WITH (NOLOCK)
    )
    SELECT 
        I_LINHAS,
        COMPETENCIA,
        valor
    FROM FilaOrdenada
    WHERE posicao = 1
)v2 ON v2.I_LINHAS = v1.I_LINHAS
""" 

query_emp_onibus = """
SELECT I_EMPONI,
       NOME AS NOME_EMP
    FROM bethadba.foemponi
"""

query_funcionarios_onibus = """
select CODI_EMP,
           I_LINHAS,
           I_EMPREGADOS,
           QUANTIDADE,
           UNIDADE_LANCTO,
           COMPETENCIA_INICIO,
           COMPETENCIA_FIM,
           DETERMINAR_FIM 
    FROM bethadba.fovaletrp f 
    WHERE 1=1
"""

# --- CONSULTANDO DADOS DO DOMINIO, SALVANDO NO DATALAKE E SUBINDO MYSQL ---

try:
    conexao_dominio = pyodbc.connect(conn_str)  
    print("Deu certo a conexão") 
    print("Iniciando consulta Etinerarios") 
    df_etinerarios = ler_banco_extrair_dp(conexao=conexao_dominio, sql_query=query_etinerarios)
except Exception as e:
    print(f"Erro na consulta Etinerarios:{e}")

try:
    conexao_dominio = pyodbc.connect(conn_str)  
    print("Deu certo a conexão") 
    print("Iniciando consulta Empresas") 
    df_empresas = ler_banco_extrair_dp(conexao=conexao_dominio, sql_query=query_emp_onibus)
except Exception as e:
    print(f"Erro na consulta Empresas:{e}")

try:
    conexao_dominio = pyodbc.connect(conn_str)  
    print("Deu certo a conexão")
    print("Iniciando consulta Pessoas Passagens") 
    df_pessoas = ler_banco_extrair_dp(conexao=conexao_dominio, sql_query=query_funcionarios_onibus)
except Exception as e:
    print(f"Erro na consulta Pessoas Passagens:{e}")

try:
    conexao_dominio = pyodbc.connect(conn_str)  
    print("Deu certo a conexão")
    print("Iniciando consulta Geral colaboradores") 
    df_geral_colab = ler_banco_extrair_dp(conexao=conexao_dominio, sql_query=query_colaboradores)
except Exception as e:
    print(f"Erro na consulta Geral colaboradores:{e}")

# --- AJUSTANDO O FORMATO DE PIVOT TABLE PARA SUBIR ---
lista_cargos = [
    'ASSISTENTE DE MONITORAMENTO CFTV','FARMACEUTICO ( A ) GERENTE','OPERADOR (A) DE LOJA',
    'FARMACEUTICA ','OPERADOR ( A ) DE LOJA','VENDEDOR (A)','ATENDENTE TELEMARKETING',
    'FARMACEUTICO GERENTE','OPERADOR DE LOJA JUNIOR','FARMACEUTICA(O)','OPERADOR (A)  DE LOJA',
    'VENDEDOR (A) LIDER','BALCONISTA','FISCAL DE LOJA','PROMOTOR DE VENDAS','FARMACEUTICO ( A ) ',
    'OPERADOR (A) DE CAIXA','BALCONISTA ','GERENTE DE LOJA JUNIOR','REPOSITOR','FARMACEUTICO (A)',
    'OPERADOR (A) DE TELEVENDAS','COORDENADOR (A) FARMACEUTICO (A)','GERENTE DE LOJA PLENO',
    'SUBGERENTE','FARMACEUTICO(A) GERENTE','OPERADOR DE CAIXA','COORDENADOR DE FISCAIS',
    'GERENTE DE LOJA SENIOR','SUBGERENTE DE LAYOUT','FARMACEUTICO(A) SUPERVISOR','OPERADOR DE LOJA PLENO', 
    'ENCARREGADO DE LOJA','LIDER DE LOJA JUNIOR','SUBGERENTE DE LOJA','GERENTE ADM DE LOJA',
    'OPERADOR(A) DE LOJA','FARMACEUTICA','LIDER DE LOJA PLENO','SUBGERENTE DE LOJA PLENO',
    'GERENTE DE LOJA','SUB GERENTE DE LOJA','FARMACEUTICO','LIDER DE LOJA SENIOR',
    'SUBGERENTE DE LOJA SENIOR','LIDER DE LOJA','SUBGERENTE DE LOJA II','FARMACEUTICO ( A )',
    'MOTOFRETISTA','SUPERVISOR DE LOJA JUNIOR','LIDER DE LOJA II','SUBGERENTE DE LOJA JUNIOR'
]
afastamentos_cortar = [8, 23, 24]

df_view = df_pessoas.merge(df_etinerarios, how='left', on='I_LINHAS')
df_view = df_view.merge(df_empresas, how='left', on='I_EMPONI')
df_view = df_view.merge(df_geral_colab, how='left', left_on=['CODI_EMP','I_EMPREGADOS'],
                        right_on=['codi_emp','i_empregados'])

df_view = df_view.loc[df_view['DETERMINAR_FIM'] == 0]
df_view = df_view.loc[~df_view['I_AFASTAMENTOS'].isin(afastamentos_cortar)]
df_view = df_view.loc[df_view['I_LINHAS'] >= 20000]
df_view = df_view.loc[df_view['I_LINHAS'] <= 30000]
df_view['ESCALA'] = df_view['i_cargos'].apply(lambda x: "6X1" if x in lista_cargos else "5X2")

pivot_final = df_view.pivot_table(index=['cpf','nome','Descricao_afastamento','ESCALA'],
                                  columns='NOME_EMP',
                                  values=['QUANTIDADE','VALOR'], aggfunc='sum').reset_index()

pivot_final.columns = ['_'.join(col).strip('_') for col in pivot_final.columns]
pivot_final = pivot_final.fillna(0)

pivot_final = pivot_final.rename(columns={
    'cpf':'MATRICULA_CPF',
    'nome':'NOME_COMPLETO',
    'Descricao_afastamento':'STATUS',
    'ESCALA':'SETOR',
    'VALOR_TRANSFACIL':'VLR_VLR_PASSAGENS_BHBUS',
    'QUANTIDADE_TRANSFACIL':'QTD_BHBUS',
    'VALOR_CONSORCIO OTIMO':'VLR_PASSAGENS_OTIMO',
    'QUANTIDADE_CONSORCIO OTIMO':'QTD_OTIMO',
    'VALOR_BETIM CARD':'VLR_PASSAGENS_BETIM',
    'QUANTIDADE_BETIM CARD':'QTD_BETIM',
    'VALOR_VINSCOL':'VLR_PASSAGENS_VISCOL',
    'QUANTIDADE_VINSCOL':'QTD_VISCOL',
    'VALOR_TURI':'VLR_PASSAGENS_TURI',
    'QUANTIDADE_TURI':'QTD_TURI',
    'VALOR_SETE LAGOANO':'VLR_PASSAGENS_SETELAGOANO',
    'QUANTIDADE_SETE LAGOANO':'QTD_SETELAGOANO'
})

# --- UPLOAD DAS INFORMAÇÕES PARA O BANCO VPS MYSQL ---
try:
    print("Iniciando conexão com VPS")
    tunnel.start()
    db_url = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@127.0.0.1:{tunnel.local_bind_port}/"
    engine = create_engine(db_url)
    
    try:
        if not df_geral_colab.empty:
            print("Iniciando importação de GERAL_COLABORADORES")
            with engine.begin() as conexao_segura:          
                try:
                    conexao_segura.execute(text("TRUNCATE TABLE vale_transporte.GERAL_COLABORADORES;"))
                except:
                    print("Tabela GERAL_COLABORADORES ainda não existe, criando ...")
                df_geral_colab.to_sql(
                    name='GERAL_COLABORADORES', 
                    schema='vale_transporte',
                    con=conexao_segura, 
                    if_exists='append', 
                    index=False
                )
                
        if not pivot_final.empty:
            print("Iniciando importação de CADASTRO_ATUAL_SITE")
            with engine.begin() as conexao_segura:          
                try:
                    conexao_segura.execute(text("TRUNCATE TABLE vale_transporte.CADASTRO_ATUAL_SITE;"))
                except:
                    print("Tabela CADASTRO_ATUAL_SITE ainda não existe, criando ...")
                pivot_final.to_sql(
                    name='CADASTRO_ATUAL_SITE', 
                    schema='vale_transporte',
                    con=conexao_segura, 
                    if_exists='append', 
                    index=False
                )
    
        if not df_pessoas.empty:
            print("Iniciando importação de PESSOAS_PASSAGEM")
            with engine.begin() as conexao_segura:          
                try:
                    conexao_segura.execute(text("TRUNCATE TABLE vale_transporte.PESSOAS_PASSAGEM;"))
                except:
                    print("Tabela PESSOAS_PASSAGEM ainda não existe, criando ...")
                df_pessoas.to_sql(
                    name='PESSOAS_PASSAGEM', 
                    schema='vale_transporte',
                    con=conexao_segura, 
                    if_exists='append', 
                    index=False
                )
    
        if not df_empresas.empty:
            print("Iniciando importação de EMP_ONIBUS")
            with engine.begin() as conexao_segura:
                try:
                    conexao_segura.execute(text("TRUNCATE TABLE vale_transporte.EMP_ONIBUS;"))
                except:
                    print("Tabela EMP_ONIBUS ainda não existe, criando ...")
                df_empresas.to_sql(
                    name='EMP_ONIBUS', 
                    schema='vale_transporte',
                    con=conexao_segura, 
                    if_exists='append', 
                    index=False
                )   
                
        if not df_etinerarios.empty:
            print("Iniciando importação de ETINERARIOS")
            with engine.begin() as conexao_segura:
                try:
                    conexao_segura.execute(text("TRUNCATE TABLE vale_transporte.ETINERARIOS;"))
                except:
                    print("Tabela ETINERARIOS ainda não existe, criando ...")
                df_etinerarios.to_sql(
                    name='ETINERARIOS', 
                    schema='vale_transporte',
                    con=conexao_segura, 
                    if_exists='append', 
                    index=False
                )     
    
    except Exception as e:
        print(f"Erro nos uploads ao banco: {e}")
  
except Exception as e:
    print(f"Erro na conexão com tunnel VPS: {e}")
    
finally:
    # Garante que o túnel SSH seja fechado, mesmo que dê erro no meio do caminho
    if 'tunnel' in locals() and tunnel.is_active:
        tunnel.stop()
        print("Túnel SSH fechado com sucesso.")