import pandas as pd
from F_ReadEditDB import ReadEditDB
from F_Conexao import iniciar_conexao
from elements import carregar_imagem_local, grafico_1_gastodia, grafico_3_categoria_gasto
from elements import grafico_4_orcamento_gasto, grafico_2_runrate

from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

load_dotenv(override=True)

if not st.session_state.get("autenticado", False):
    st.error("⛔ Acesso negado. Você precisa criar uma nova denunciar ou utilizar o código anotado para consultar o status da denuncia aberta.")
    st.stop()



logo_completo = r'C:\Users\Higor Rodrigues\Desktop\PROJETOS\FINANCEIRO_PAINEL\toxeira-house-financeiro\assets\logo\Sem título.png'
logo_b64 = carregar_imagem_local(logo_completo)
paleta_de_cores = ['#054159', '#45A9BF', '#F2790F', '#F20505', '#eb5c40']

st.markdown("""
    <style>
        /* CSS para as Métricas */
        [data-testid="stMetric"] {
            background-color: #ffffff !important;
            border-radius: 15px 45px!important;
            box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.08) !important;
            padding: 15px 20px !important;
            border: 1px solid #f0f2f6 !important;
            color: #053f5c !important;
            border-top: 4px solid #eb5c40 !important;
        }
        div[class*="st-key-saldo"] [data-testid="stMetric"] {
            border-top: 4px solid #45A9BF !important; /* Cor topo específica (Verde) */
        }
        /* CSS Mágico para Containers Específicos */
        div[class*="st-key-grafico"] {
            background-color: #ffffff !important;
            border-radius: 15px !important;
            box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.08) !important;
            border: 1px solid #f0f2f6 !important;
            padding: 20px !important;
            color: #053f5c !important;

            
            /* Garante que o padding não faça o container vazar da tela */
            box-sizing: border-box !important; 
        }
    </style>
""", unsafe_allow_html=True)

html_cabecalho_2 = f"""
<div style="text-align: center; margin-top: 35px; margin-bottom: 30px; font-family: sans-serif;">    
    <img src="data:image/png;base64,{logo_b64}" width="280" stylie="margin-bottom: 10px;">
</div>
"""



# --- CONFIGURANDO O TUNEL SSH E A CONEXAO COM O BANCO DA VPS ---
database = 'financeiro'
ano_atual = datetime.now().year
mes_atual = datetime.now().month
mes_ano = (ano_atual*100)+mes_atual



engine = iniciar_conexao()
CONFIG_DB = ReadEditDB(engine=engine)


## ----------------------- ##
## CONFIGURAÇÕES DA PAGINA ##
## ----------------------- ##
st.set_page_config(
    page_title='DASHBOARD',
    # page_icon =logo_dc,
    layout='wide',
    initial_sidebar_state = 'auto')


if 'filtro_mes' not in st.session_state: 
    st.session_state.filtro_mes = [mes_ano]
st.sidebar.markdown(f'''Usuario Logado:
                    **{CONFIG_DB.usuarios_read_login(database='financeiro',
                                                         table='USERS',
                                                         usuario=st.session_state.get("usuario_logado")
                                                         )['NOME'].iloc[0]}**''')
### ------------------ ###
### DATAFRAMES PADROES ###
### ------------------ ###
df_tipo_pagamento  = CONFIG_DB.geral_read(database=database,
                                          table='TIPO_PAGAMENTO')
df_categoria_saida = CONFIG_DB.geral_read(database=database,
                                          table='CATEGORIA_SAIDAS')


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

total_entrada_dinheiro = 0
total_orcado           = 0 
categorias_orcamento   = []
total_gasto_orcamento  = 0
total_pago_credito     = 0
total_gasto_dinheiro   = 0
total_gasto_credito    = 0
transacoes_dinheiro    = []
transacoes_credito     = []
total_limite_credito   = 0
transacoes_credito_pag = []
saldo_dinheiro         = 0
saldo_credito          = 0
saldo_orcamento        = 0
saldo_total            = 0


container_principal = st.container(border = True)
aba_dashboard, aba_geral = container_principal.tabs(['📊 Dashboard','📊 Geral'])

with aba_dashboard:
    # linha_filtros = st.columns([1,1,1,1,1,1])
    linha_1 = st.columns([2,1,1,1,1,1,1])
    espaco_filtro_logo = linha_1[0].columns([2,1],vertical_alignment='center')
    linha_2 = st.columns([5,2],vertical_alignment='top')
    linha_3 = st.columns([5,2],vertical_alignment='top')


    filtros_ativos = {
            'MES_ANO': st.session_state.filtro_mes
            }

    def gerar_opcoes(coluna_alvo):
        df_temp   = df_geral_movimentacoes.copy()
        df_temp_2 = df_geral_orcamento.copy()
        df_temp_3 = df_geral_credito.copy()
        lista_dfs = [df_temp, df_temp_2, df_temp_3]
        series_combinadas = []

        for df in lista_dfs:
            df_temp = df.copy()
            for coluna, escolhas in filtros_ativos.items():
                if coluna != coluna_alvo and escolhas and coluna in df_temp.columns:
                    df_temp = df_temp[df_temp[coluna].isin(escolhas)]
            if coluna_alvo in df_temp.columns:
                series_combinadas.append(df_temp[coluna_alvo].dropna())
        if series_combinadas:
            return pd.concat(series_combinadas).unique()
        return []


    espaco_filtro_logo[1].multiselect(":material/date_range: Mes Ano:", options=gerar_opcoes('MES_ANO'), key='filtro_mes')
    espaco_filtro_logo[0].html(html_cabecalho_2)
 
    for coluna, escolhas in filtros_ativos.items():
        if escolhas:
            df_geral_movimentacoes = df_geral_movimentacoes[df_geral_movimentacoes[coluna].isin(escolhas)]
            df_geral_orcamento = df_geral_orcamento[df_geral_orcamento[coluna].isin(escolhas)]
            df_geral_credito = df_geral_credito[df_geral_credito[coluna].isin(escolhas)]



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
    saldo_total            = saldo_dinheiro+saldo_credito-saldo_orcamento
    ## -- DF GRAFICOS -- ##
    try:
        df_filt_gasto   = df_geral_movimentacoes[df_geral_movimentacoes['COD_TIPO_MOV'] == 2]

        df_gasto_dia    = df_filt_gasto.pivot_table(index=['DATA_PAGAMENTO','COD_TIPO'],
                                                    values='VALOR_PAGO',
                                                    aggfunc='sum',
                                                    ).reset_index().sort_values(by='DATA_PAGAMENTO', ascending=True)

        df_gasto_dia['DATA_PAGAMENTO'] = df_gasto_dia['DATA_PAGAMENTO'].dt.strftime('%d/%m/%Y')
        df_gasto_dia = df_gasto_dia.merge(df_tipo_pagamento, on='COD_TIPO', how='left')
    except:
        df_gasto_dia = pd.Dataframe()
        df_filt_gasto = pd.Dataframe()

    ## ---------------- ##
    try:
        df_gasto_categoria = df_filt_gasto.pivot_table(index='COD_CATEGORIA',
                                                    values='VALOR_PAGO',
                                                    aggfunc='sum').reset_index().sort_values(by='VALOR_PAGO', ascending=True)
        df_gasto_categoria = df_gasto_categoria.merge(df_categoria_saida, on='COD_CATEGORIA', how='left')
    except:
        df_gasto_categoria = pd.Dataframe()

    ## ---------------- ##
    try:
        df_orcamento_gasto_categoria = df_geral_orcamento.merge(df_gasto_categoria.drop(columns='DESCRICAO_SAIDAS'), on='COD_CATEGORIA', how='left')
        df_orcamento_gasto_categoria = df_orcamento_gasto_categoria.merge(df_categoria_saida, on='COD_CATEGORIA', how='left')
        df_orcamento_gasto_categoria = df_orcamento_gasto_categoria[['DESCRICAO_SAIDAS','VALOR_PAGO','VALOR_ORCAMENTO']]
    except:
        df_orcamento_gasto_categoria = pd.Dataframe()

    linha_1[1].metric(label = "**TOTAL DINHEIRO x SALDO**",
                      value = f"R${saldo_dinheiro:_.2f}".replace(".",",").replace("_","."),
                      delta = f"**{round((1-(saldo_dinheiro/total_entrada_dinheiro))*100,2)}% -- R${total_entrada_dinheiro:_.2f}**".replace(".",",").replace("_","."),
                      border = True,
                      delta_arrow ='off',
                      icon=":material/paid:"
                      )

    linha_1[2].metric(label = "**TOTAL CREDITO x SALDO**",
                      value = f"R${saldo_credito:_.2f}".replace(".",",").replace("_","."),
                      delta = f"**{round((1-(saldo_credito/total_limite_credito))*100,2)}% -- R${total_limite_credito:_.2f}**".replace(".",",").replace("_","."),
                      border = True,
                      delta_arrow ='off',
                      icon=":material/credit_card:"
                      )

    linha_1[3].metric(label = "**TOTAL GASTO DINHEIRO**",
                      value = f"R${(total_gasto_dinheiro+total_pago_credito):_.2f}".replace(".",",").replace("_","."),
                      delta = f"**{transacoes_dinheiro + transacoes_credito_pag} Transações**",
                      border = True,
                      delta_arrow ='off',
                      icon=":material/paid:"
                      )

    linha_1[4].metric(label = "**TOTAL GASTO CREDITO**",
                      value = f"R${total_gasto_credito:_.2f}".replace(".",",").replace("_","."),
                      delta = f"**{transacoes_credito} Transações**",
                      border = True,
                      delta_arrow ='off',
                      icon=":material/credit_card:"
                      )

    linha_1[5].metric(label = "**TOTAL ORÇADO x GASTO**",
                      value = f"R${saldo_orcamento:_.2f}".replace(".",",").replace("_","."),
                      delta = f"**{round((1-(total_gasto_orcamento/total_orcado))*100,2)}% -- R${total_orcado:_.2f}**".replace(".",",").replace("_","."),
                      border = True,
                      delta_arrow ='off',
                      icon=":material/credit_card:"
                      )
    with linha_1[6].container(key="saldo"):
        st.metric(label = "**SALDO**",
                value = f"R${saldo_total:_.2f}".replace(".",",").replace("_","."),
                border = True,
                delta  = f"**{round(saldo_total/(saldo_dinheiro+saldo_credito),2)*100}%**",
                delta_arrow ='off',
                icon=":material/account_balance_wallet:",
                )

 

    with linha_2[0].container(key="grafico_barras_dia"):
        fig_barras_dia_pag = grafico_1_gastodia(df_gasto_dia=df_gasto_dia,
                                                paleta_de_cores=paleta_de_cores)
        st.plotly_chart(fig_barras_dia_pag, width='stretch')

    with linha_3[0].container(key="grafico_barras_dia_2"):
        fig_grafico_previsao = grafico_2_runrate(df_filt_gasto=df_filt_gasto,
                                                 total_orcado=total_orcado,
                                                 lista_cat_orcamentos=categorias_orcamento) 
        st.plotly_chart(fig_grafico_previsao, width='stretch', key='barras_2')
 
    with linha_2[1].container(key="grafico_lateral_1"):
        figura_grafico_categoria = grafico_3_categoria_gasto(df_gasto_categoria=df_gasto_categoria)
        st.plotly_chart(figura_grafico_categoria, width='stretch', key='rosca_2')

    # Preenche o quadrado vermelho inferior (ao lado do gráfico 2)
    with linha_3[1].container(key="grafico_lateral_2",):
        figura_barras_orcamento = grafico_4_orcamento_gasto(df_orcamento_gasto_categoria=df_orcamento_gasto_categoria)
        if figura_barras_orcamento is not None:
            st.plotly_chart(figura_barras_orcamento, width='stretch')
        else:
            st.info("Não há dados de orçamento/gasto para o período selecionado.",  width='stretch')

