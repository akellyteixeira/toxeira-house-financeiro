import pandas as pd
import numpy as np

from F_ReadEditDB import ReadEditDB
from F_Conexao import iniciar_conexao
from elements import carregar_imagem_local
from dotenv import load_dotenv
from datetime import datetime, date
import streamlit as st
import time
import io

load_dotenv(override=True)



# if not st.session_state.get("codigo", False):
#     st.error("⛔ Acesso negado. Você precisa criar uma nova denunciar ou utilizar o código anotado para consultar o status da denuncia aberta.")
#     st.stop()
#


logo_completo = r'C:\Users\Higor Rodrigues\Desktop\PROJETOS\FINANCEIRO_PAINEL\toxeira-house-financeiro\assets\logo\Sem título.png'
logo_b64 = carregar_imagem_local(logo_completo)


html_cabecalho = f"""
<div style="text-align: center; margin-top: 20px; margin-bottom: 30px; font-family: sans-serif;">    
    <img src="data:image/png;base64,{logo_b64}" width="300" stylie="margin-bottom: 15px;">
    <h4 style="color: #2c3e50; 
        margin: 0; 
        letter-spacing: 1px;
        font-size: 150%;">
        DASHBOARD FINANCEIRO
    </h4>
</div>
"""

html_cabecalho_2 = f"""
<div style="text-align: center; margin-top: 20px; margin-bottom: 30px; font-family: sans-serif;">    
    <img src="data:image/png;base64,{logo_b64}" width="250" stylie="margin-bottom: 10px;">
</div>
"""



# --- CONFIGURANDO O TUNEL SSH E A CONEXAO COM O BANCO DA VPS ---
database = 'financeiro'
ano_atual = datetime.now().year
mes_atual = datetime.now().month
mes_ano = (ano_atual*100)+mes_atual



engine = iniciar_conexao()
CONFIG_DB = ReadEditDB(engine=engine)

## CONFIGURAÇÕES DA PAGINA ##
st.set_page_config(
    page_title='DASHBOARD',
    # page_icon =logo_dc,
    layout='wide',
    initial_sidebar_state = 'auto')


if 'filtro_mes' not in st.session_state: 
    st.session_state.filtro_mes = [mes_ano]




### ------------------ ###
### DATAFRAMES PADROES ###
### ------------------ ###

try:
    df_geral_movimentacoes = CONFIG_DB.geral_read(database=database,
                                                  table='FATO_MOV')
    df_geral_movimentacoes['MES_ANO'] = ((df_geral_movimentacoes['DATA_PAGAMENTO'].dt.year)*100) + (df_geral_movimentacoes['DATA_PAGAMENTO'].dt.month)
    
except:
    df_geral_movimentacoes = pd.DataFrame()


try:
    df_geral_credito = CONFIG_DB.geral_read(database=database,
                                            table='FATO_CREDITO')
    df_geral_credito['MES_ANO'] = ((df_geral_credito['DATA_PAGAMENTO'].dt.year)*100) + (df_geral_credito['DATA_PAGAMENTO'].dt.month)

except:
    df_geral_credito = pd.DataFrame()


try:
    df_geral_orcamento = CONFIG_DB.geral_read(database=database,
                                              table='FATO_ORCAMENTO')
    df_geral_orcamento['MES_ANO'] = df_geral_orcamento['MESANO_VIGENCIA']

except:
    df_geral_orcamento = pd.DataFrame()





# _,titulo,_ = st.columns([1,1,1])
# titulo.html(html_cabecalho)
#

container_principal = st.container(border = True)


aba_dashboard, aba_geral = container_principal.tabs(['📊 Dashboard','📊 Geral'])

with aba_dashboard:
    linha_filtros = st.columns([1,1,1,1,1,1])
    linha_1 = st.columns([1,1,1,1,1,3])
    linha_2 = st.columns([5,3],vertical_alignment='top')


    filtros_ativos = {
            # 'FILIAL': st.session_state.filtro_filial,
            # 'Linha': st.session_state.filtro_linha,
            # 'NomeFabricante': st.session_state.filtro_fabricante,
            # 'CODIGO_LISTA': st.session_state.filtro_lista,
            # 'DATA': st.session_state.filtro_data,
            'MES_ANO': st.session_state.filtro_mes
            }

    def gerar_opcoes(coluna_alvo):
        df_temp = df_geral_movimentacoes.copy()
        for coluna, escolhas in filtros_ativos.items():
            if coluna != coluna_alvo and escolhas:
                df_temp = df_temp[df_temp[coluna].isin(escolhas)]
        return df_temp[coluna_alvo].unique()

    # linha_filtros[5].multiselect("Filial:", options=gerar_opcoes('FILIAL'), key='filtro_filial')
    # linha_filtros[1].multiselect("Linha:", options=gerar_opcoes('Linha'), key='filtro_linha')
    # linha_filtros[2].multiselect("Fabricante:", options=gerar_opcoes('NomeFabricante'), key='filtro_fabricante')
    # linha_filtros[3].multiselect("Lista:", options=gerar_opcoes('CODIGO_LISTA'), key='filtro_lista')
    # linha_filtros[4].multiselect("Data:", options=gerar_opcoes('DATA'), key='filtro_data')
    linha_filtros[1].multiselect("Mes Ano:", options=gerar_opcoes('MES_ANO'), key='filtro_mes')
    linha_filtros[0].html(html_cabecalho_2)
 
    for coluna, escolhas in filtros_ativos.items():
        if escolhas:
            df_geral_movimentacoes = df_geral_movimentacoes[df_geral_movimentacoes[coluna].isin(escolhas)]
    

    ## --- METRICAS --- ##

    total_entrada_dinheiro = df_geral_movimentacoes[df_geral_movimentacoes['COD_TIPO_MOV'] == 1]['VALOR_PAGO'].sum()
    total_orcado           = df_geral_orcamento['VALOR_ORCAMENTO'].sum()
    categorias_orcamento   = df_geral_orcamento['COD_CATEGORIA'].unique()
    total_gasto_orcamento  = df_geral_movimentacoes[df_geral_movimentacoes['COD_TIPO_MOV'] == 2][df_geral_movimentacoes['COD_CATEGORIA'].isin(categorias_orcamento)]['VALOR_PAGO'].sum() 
    total_pago_credito     = df_geral_credito['VALOR_PAGO'].sum()
    total_gasto_dinheiro   = df_geral_movimentacoes[df_geral_movimentacoes['COD_TIPO_MOV'] == 2][df_geral_movimentacoes['COD_TIPO'] == 1]['VALOR_PAGO'].sum()
    total_gasto_credito    = df_geral_movimentacoes[df_geral_movimentacoes['COD_TIPO_MOV'] == 2][df_geral_movimentacoes['COD_TIPO'] == 2]['VALOR_PAGO'].sum()
    transacoes_dinheiro    = df_geral_movimentacoes[df_geral_movimentacoes['COD_TIPO_MOV'] == 2][df_geral_movimentacoes['COD_TIPO'] == 1]['ID_TRANSACAO'].nunique()
    transacoes_credito     = df_geral_movimentacoes[df_geral_movimentacoes['COD_TIPO_MOV'] == 2][df_geral_movimentacoes['COD_TIPO'] == 2]['ID_TRANSACAO'].nunique()
    total_limite_credito   = df_geral_credito['VALOR_LIBERADO'].sum()
    transacoes_credito_pag = df_geral_credito['ID_TRANSACAO'].nunique()    
    saldo_dinheiro         = total_entrada_dinheiro - total_pago_credito - total_gasto_dinheiro
    saldo_credito          = total_limite_credito - total_gasto_credito
    saldo_orcamento        = total_orcado - total_gasto_orcamento
    


    linha_1[0].metric(label = "**TOTAL DINHEIRO x SALDO**",
                      value = f"R${saldo_dinheiro:_.2f}".replace(".",",").replace("_","."),
                      delta = f"**{round((1-(saldo_dinheiro/total_entrada_dinheiro))*100,2)}% -- R${total_entrada_dinheiro:_.2f}**".replace(".",",").replace("_","."),
                      border = True,
                      delta_arrow ='off',
                      icon=":material/paid:"
                      )

    linha_1[1].metric(label = "**TOTAL CREDITO x SALDO**",
                      value = f"R${saldo_credito:_.2f}".replace(".",",").replace("_","."),
                      delta = f"**{round((1-(saldo_credito/total_limite_credito))*100,2)}% -- R${total_limite_credito:_.2f}**".replace(".",",").replace("_","."),
                      border = True,
                      delta_arrow ='off',
                      icon=":material/credit_card:"
                      )

    linha_1[2].metric(label = "**TOTAL GASTO DINHEIRO**",
                      value = f"R${(total_gasto_dinheiro+total_pago_credito):_.2f}".replace(".",",").replace("_","."),
                      delta = f"**{transacoes_dinheiro + transacoes_credito_pag} Transações**",
                      border = True,
                      delta_arrow ='off',
                      icon=":material/paid:"
                      )

    linha_1[3].metric(label = "**TOTAL GASTO CREDITO**",
                      value = f"R${total_gasto_credito:_.2f}".replace(".",",").replace("_","."),
                      delta = f"**{transacoes_credito} Transações**",
                      border = True,
                      delta_arrow ='off',
                      icon=":material/credit_card:"
                      )

    linha_1[4].metric(label = "**TOTAL ORÇADO x GASTO**",
                      value = f"R${saldo_orcamento:_.2f}".replace(".",",").replace("_","."),
                      delta = f"**{round((1-(total_gasto_orcamento/total_orcado))*100,2)}% -- R${total_orcado:_.2f}**".replace(".",",").replace("_","."),
                      border = True,
                      delta_arrow ='off',
                      icon=":material/credit_card:"
                      )




    # linha_2[0].
