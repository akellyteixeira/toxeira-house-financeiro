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
        CADASTRAR NOVO MOVIMENTO
    </h4>
</div>
"""

texto_explicativo = f"""
<div style="text-align: left; margin-top: 20px; margin-bottom: 30px; font-family: sans-serif;">    
    <h4 style="color: #2c3e50; 
        margin: 0; 
        letter-spacing: 1px;
        font-size: 100%;">
        Preencha os campos abaixo com <b>atenção</b>. Os dados serão encaminhados para o setor responsável pela investigação e resolução.  
    </h4> 
    <h4 style="color: #2c3e50; 
        margin: 0; 
        letter-spacing: 1px;
        font-size: 100%;">
        Anote o codigo: <b>{st.session_state.get("codigo")}</b>, você pode utiliza-lo para consultar as futuras atualizações do caso. 
    </h4> 
</div>
"""


# --- CONFIGURANDO O TUNEL SSH E A CONEXAO COM O BANCO DA VPS ---
database = 'financeiro'

engine = iniciar_conexao()
CONFIG_DB = ReadEditDB(engine=engine)


## VARIAVEIS GLOBAIS .ENV ##
aut_enviar_denuncia = True
df_upload = pd.DataFrame()

df_status = CONFIG_DB.geral_read(database=database,
                                 table='STATUS')

df_categoria_entrada =  CONFIG_DB.geral_read(database=database,
                                             table='CATEGORIA_ENTRADAS')

df_categoria_saidas =   CONFIG_DB.geral_read(database=database,
                                             table='CATEGORIA_SAIDAS')


df_cadastro_credito =   CONFIG_DB.geral_read(database=database,
                                             table='CADASTRO_CREDITO')

df_tipo_pagamento =     CONFIG_DB.geral_read(database=database,
                                             table='TIPO_PAGAMENTO')

df_tipo_movimento =     CONFIG_DB.geral_read(database=database,
                                             table='TIPO_MOVIMENTACAO')
try:
    df_movimentacoes_mes_atual = CONFIG_DB.mov_read(database=database,
                                                table='FATO_MOV',
                                                mes_filtro=datetime.now().month,
                                                ano_filtro=datetime.now().year,
                                                )
    df_movimentacoes_mes_atual = df_movimentacoes_mes_atual.merge(df_status, on='COD_STATUS', how='left')
    df_movimentacoes_mes_atual = df_movimentacoes_mes_atual.merge(df_categoria_entrada, on='COD_CATEGORIA', how='left')
    df_movimentacoes_mes_atual = df_movimentacoes_mes_atual.merge(df_categoria_saidas, on='COD_CATEGORIA', how='left')
    df_movimentacoes_mes_atual = df_movimentacoes_mes_atual.merge(df_tipo_pagamento, on='COD_TIPO', how='left')
    df_movimentacoes_mes_atual = df_movimentacoes_mes_atual.merge(df_tipo_movimento, on='COD_TIPO_MOV', how='left')
    df_movimentacoes_mes_atual = df_movimentacoes_mes_atual.merge(df_cadastro_credito,on='COD_CREDITO',how='left')
    
    df_movimentacoes_mes_atual = df_movimentacoes_mes_atual.fillna(" ")
    df_movimentacoes_mes_atual['CATEGORIA'] = np.where(df_movimentacoes_mes_atual['COD_TIPO_MOV'] == 1,   # Condição
                                                       df_movimentacoes_mes_atual['DESCRICAO_ENTRADAS'],  # Valor se for Verdadeiro
                                                       df_movimentacoes_mes_atual['DESCRICAO_SAIDAS'])    # Valor se for Falso
 
    df_movimentacoes_mes_atual['ORIGEM_MOV'] = np.where(df_movimentacoes_mes_atual['COD_TIPO_MOV'] == 2,   # Condição
                                                        df_movimentacoes_mes_atual['DESCRICAO_TIPO']+' - '+df_movimentacoes_mes_atual['DESCRICAO_CREDITO'],  # Valor se for Verdadeiro
                                                        df_movimentacoes_mes_atual['DESCRICAO_TIPO'])    # Valor se for Falso

    df_movimentacoes_mes_atual = df_movimentacoes_mes_atual[['ID_TRANSACAO','DATA_PAGAMENTO','DESCRICAO_TIPO_MOV',
                                                             'ORIGEM_MOV','DESCRICAO_STATUS','CATEGORIA','OBS','VALOR_PAGO']]

except Exception as e:
    df_movimentacoes_mes_atual = pd.DataFrame()


try:
    df_creditos_mes_atual = CONFIG_DB.mov_read(database=database,
                                           table='FATO_CREDITO',
                                           mes_filtro=datetime.now().month,
                                          ano_filtro=datetime.now().year,
                                          )
    df_creditos_mes_atual = df_creditos_mes_atual.merge(df_status, on='COD_STATUS', how='left')
    df_creditos_mes_atual = df_creditos_mes_atual.merge(df_cadastro_credito, on='COD_CREDITO',how='left')
    df_creditos_mes_atual = df_creditos_mes_atual[['ID_TRANSACAO','DATA_PAGAMENTO','DESCRICAO_CREDITO',
                                                   'VALOR_PAGO','VALOR_LIBERADO','OBS']]
except Exception as e:
    df_creditos_mes_atual = pd.DataFrame()


try:
    df_orcamento_mes_atual = CONFIG_DB.orc_read(database=database,
                                                table='FATO_ORCAMENTO',
                                                mesano_filtro=((datetime.now().year)*100)+(datetime.now().month)
                                                )

    df_orcamento_mes_atual = df_orcamento_mes_atual.merge(df_categoria_saidas, on='COD_CATEGORIA',how='left')
    df_orcamento_mes_atual = df_orcamento_mes_atual[['ID_TRANSACAO','DESCRICAO_SAIDAS','VALOR_ORCAMENTO','OBS']]
    df_orcamento_mes_atual = df_orcamento_mes_atual.rename(columns={'DESCRICAO_SAIDAS':'CATEGORIA'})
    
except Exception as e:
    df_orcamento_mes_atual = pd.DataFrame()


## VARIAVEIS PARA MANTER O SITE FUNCIONANDO ANTES DE SUBIR AS PLANILHAS
hoje = datetime.now()
buffer = io.BytesIO()


menus_superiores = {
    'Get help':'https://wa.me/5543996408905',
    'About':'''
    '''}


## CONFIGURAÇÕES DA PAGINA ##
st.set_page_config(
    page_title='NOVA MOVIMENTACAO',
    menu_items=menus_superiores,
    layout='wide',
    # initial_sidebar_state = 'auto',
)



_,titulo,_ = st.columns([1,1,1])
titulo.html(html_cabecalho)

container_principal = st.container(border=True,
                                horizontal = False,
                                )

with container_principal:

    _,texto,_ = st.columns([1,5,1])
 
    tipo_mov,data_do_pagamento,categoria_mov,tipo_mov_pag, status, botao_registrar_col = texto.columns([1,1,1,1,1,1], vertical_alignment="bottom")
    valor,credito,obs_colum = texto.columns([1,1,4], vertical_alignment="bottom") 

    tipo = tipo_mov.selectbox(label = "**Tipo:***",
                              placeholder = "Sel. o tipo",
                              options = df_tipo_movimento['DESCRICAO_TIPO_MOV'],
                              index = None)

    data_pagamento = data_do_pagamento.date_input(label = "**Data do Pagamento:**",
                                                  value = 'today',
                                                  min_value = date(2026,1,1),
                                                  format = "DD/MM/YYYY"
                                                  )
    df_upload.loc[0, 'DATA_PAGAMENTO'] = pd.to_datetime(data_pagamento)
    df_upload.loc[0, 'ID_TRANSACAO'] = f'T_{int(time.time()*1000)}' 

    status_mov = status.selectbox(label = "**Status:**",
                                  placeholder = "Selecione o status",
                                  options = df_status['DESCRICAO_STATUS'],
                                  index = None
                                  )
    valor_mov = valor.number_input(label = "**Valor:**",
                                  placeholder = "Digite o valor",
                                  min_value = 0.0,
                                  value = None,
                                  format = "%.2f"
                                  )
 
    observacao = obs_colum.text_input(label="**Observações:**",
                                      key='observacao_input')
 
    if status_mov:
        df_upload.loc[0, 'COD_STATUS'] = df_status[df_status['DESCRICAO_STATUS'] == status_mov]['COD_STATUS'].iloc[0]
    if valor_mov:
        df_upload.loc[0, 'VALOR_PAGO'] = valor_mov
    if observacao:
        df_upload.loc[0, 'OBS'] = observacao
    if tipo == 'Saida' :
        categoria = categoria_mov.selectbox(label = "**Categoria:**",
                                            placeholder = "Sel. a categoria",
                                            options = df_categoria_saidas['DESCRICAO_SAIDAS'],
                                            index = None)

        tipo_mov_pagamento = tipo_mov_pag.selectbox(label = "**Tipo Pagamento:**",
                                                    placeholder = "Credito ou Conta",
                                                    options = df_tipo_pagamento['DESCRICAO_TIPO'],
                                                    index = None)
        df_upload.loc[0, 'COD_TIPO_MOV'] = df_tipo_movimento[df_tipo_movimento['DESCRICAO_TIPO_MOV']==tipo]['COD_TIPO_MOV'].iloc[0]

        if categoria:
            df_upload.loc[0, 'COD_CATEGORIA']  = df_categoria_saidas[df_categoria_saidas['DESCRICAO_SAIDAS'] == categoria]['COD_CATEGORIA'].iloc[0]
        if tipo_mov_pagamento:
            df_upload.loc[0, 'COD_TIPO'] = df_tipo_pagamento[df_tipo_pagamento['DESCRICAO_TIPO'] == tipo_mov_pagamento]['COD_TIPO'].iloc[0]
 
        if tipo_mov_pagamento == "Credito":
            tipo_credito = credito.selectbox(label = "**Origem Credito:**",
                                             placeholder = "Sel. o credito",
                                             options = df_cadastro_credito['DESCRICAO_CREDITO'],
                                             )
            df_upload.loc[0, 'COD_CREDITO'] = df_cadastro_credito[df_cadastro_credito['DESCRICAO_CREDITO'] == tipo_credito]['COD_CREDITO'].iloc[0]


    elif tipo == 'Credito':
        origem_credito = tipo_mov_pag.selectbox(label = "**Origem Credito:**",
                                                placeholder = "Sel. a Origem",
                                                options = df_cadastro_credito['DESCRICAO_CREDITO'],
                                                index = None)
        valor_credito = credito.number_input(label = "**Credito Liberado:**",
                                             placeholder = "Digite o valor",
                                             min_value = 0.0,
                                             value = None,
                                             format = "%.2f"
                                             )
        if origem_credito:
            df_upload.loc[0, 'COD_CREDITO'] = df_cadastro_credito[df_cadastro_credito['DESCRICAO_CREDITO'] == origem_credito]['COD_CREDITO'].iloc[0]
        if valor_credito:
            df_upload.loc[0, 'VALOR_LIBERADO'] = valor_credito

    elif tipo == 'Entrada':
        categoria = categoria_mov.selectbox(label = "**Categoria:**",
                                             placeholder = "Sel. a categoria",
                                             options = df_categoria_entrada['DESCRICAO_ENTRADAS'],
                                             index = None
                                             )
        df_upload.loc[0, 'COD_TIPO'] = None 
        df_upload.loc[0, 'COD_TIPO_MOV'] = df_tipo_movimento[df_tipo_movimento['DESCRICAO_TIPO_MOV']==tipo]['COD_TIPO_MOV'].iloc[0]
        if categoria:
            df_upload.loc[0, 'COD_CATEGORIA'] = df_categoria_entrada[df_categoria_entrada['DESCRICAO_ENTRADAS'] == categoria]['COD_CATEGORIA'].iloc[0]

    elif tipo == 'Orçamento':
        categoria = categoria_mov.selectbox(label = "**Categoria:**",
                                            placeholder = "Sel. a categoria",
                                            options = df_categoria_saidas['DESCRICAO_SAIDAS'],
                                            index = None)
        if categoria:
            df_upload.loc[0, 'COD_CATEGORIA']  = df_categoria_saidas[df_categoria_saidas['DESCRICAO_SAIDAS'] == categoria]['COD_CATEGORIA'].iloc[0]



    with botao_registrar_col:
        botao_registrar = st.button('Cadastrar',
                                    width='stretch',
                                    type='primary',
                                    disabled=False,
                                    help='Você deve preencher todos os campos obrigatórios indicados com * ')
        if botao_registrar:
            if tipo == 'Credito':
 
                CONFIG_DB.upload_msql_df(df=df_upload,
                                        table='FATO_CREDITO',
                                        database=database)
            elif tipo == 'Orçamento':
                df_upload = df_upload.rename(columns={'VALOR_PAGO':'VALOR_ORCAMENTO'})
                df_upload['MESANO_VIGENCIA'] = ((df_upload['DATA_PAGAMENTO'].dt.year)*100)+(df_upload['DATA_PAGAMENTO'].dt.month)
                df_upload = df_upload.drop(columns=['DATA_PAGAMENTO'])
                CONFIG_DB.upload_msql_df(df=df_upload,
                                        table='FATO_ORCAMENTO',
                                        database=database)

            else:
                CONFIG_DB.upload_msql_df(df=df_upload,
                                        table='FATO_MOV',
                                        database=database)
 

 
            time.sleep(1)
            st.rerun()
    


    with texto:
        st.divider()
        container_df_principal  = st.container(border = True)
        st.divider()
        container_df_secundario = st.container(border = True)
        st.divider()
        container_df_orcamento  = st.container(border = True)
        
        with container_df_principal:
            _,titulo,_ = st.columns([1,5,1])

           
            def codigo_get ():
                    st.session_state.codigo = df_movimentacoes_mes_atual['ID_TRANSACAO'].iloc[st.session_state.get("botao_excluir").get("row")]
                    CONFIG_DB.excluir_registro(table='FATO_MOV',
                                           database=database,
                                           cod_transacao=st.session_state.codigo)
                    return st.session_state.codigo 


            titulo.markdown(f"### **MOVIMENTAÇÕES MÊS ATUAL ({datetime.now().month}/{datetime.now().year}):**",text_alignment='center')
            df_modificar_mes = df_movimentacoes_mes_atual.copy()
            df_modificar_mes['EXCLUIR'] = "⚙  Excluir"

            condicoes = [
                df_modificar_mes['DESCRICAO_TIPO_MOV'] == 'Saida',
                df_modificar_mes['DESCRICAO_TIPO_MOV'] == 'Entrada'
                ]

            opcoes_tipo = ['🔴 Saida', '🟢 Entrada']

            df_modificar_mes['DESCRICAO_TIPO_MOV'] = np.select(
                condicoes,
                opcoes_tipo,
                default=df_modificar_mes['DESCRICAO_TIPO_MOV']
            )

            df = st.data_editor(df_modificar_mes,
                                hide_index = True,
                                column_config={
                                 "EXCLUIR": st.column_config.ButtonColumn("EXCLUIR",
                                                                          type='primary',
                                                                          on_click=codigo_get,
                                                                          key="botao_excluir")})
        
        with container_df_secundario:
            _,titulo,_ = st.columns([1,5,1])
            def codigo_get ():
                    st.session_state.codigo = df_creditos_mes_atual['ID_TRANSACAO'].iloc[st.session_state.get("botao_excluir_2").get("row")]
                    CONFIG_DB.excluir_registro(table='FATO_CREDITO',
                                           database=database,
                                           cod_transacao=st.session_state.codigo)
                    return st.session_state.codigo 


            titulo.markdown(f"### **MOVIMENTAÇÕES CREDITO MÊS ATUAL ({datetime.now().month}/{datetime.now().year}):**",text_alignment='center')
            df_modificar_mes = df_creditos_mes_atual.copy()
            df_modificar_mes['EXCLUIR'] = "⚙  Excluir"

            df = st.data_editor(df_modificar_mes,
                                hide_index = True,
                                key='data_credito',
                                column_config={
                                 "EXCLUIR": st.column_config.ButtonColumn("EXCLUIR",
                                                                          type='primary',
                                                                          on_click=codigo_get,
                                                                          key="botao_excluir_2")})

        with container_df_orcamento:
            print(df_orcamento_mes_atual)
            _,titulo,_ = st.columns([1,5,1])
            def codigo_get ():
                    st.session_state.codigo = df_orcamento_mes_atual['ID_TRANSACAO'].iloc[st.session_state.get("botao_excluir_3").get("row")]
                    CONFIG_DB.excluir_registro(table='FATO_ORCAMENTO',
                                           database=database,
                                           cod_transacao=st.session_state.codigo)
                    return st.session_state.codigo 


            titulo.markdown(f"### **ORÇAMENTOS MÊS ATUAL ({datetime.now().month}/{datetime.now().year}):**",text_alignment='center')
            df_modificar_mes = df_orcamento_mes_atual.copy()
            df_modificar_mes['EXCLUIR'] = "⚙  Excluir"

            df = st.data_editor(df_modificar_mes,
                                key='data_orcamento',
                                hide_index = True,
                                column_config={
                                 "EXCLUIR": st.column_config.ButtonColumn("EXCLUIR",
                                                                          type='primary',
                                                                          on_click=codigo_get,
                                                                          key="botao_excluir_3")})

    # st.dataframe(df_upload)
