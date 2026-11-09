import streamlit as st
import pandas as pd
import plotly.express as px
from F_ReadEditDB import ReadEditDB
from F_Conexao import iniciar_conexao
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv(override=True)

# if not st.session_state.get("autenticado", False):
#     st.error("⛔ Acesso negado. Você precisa estar autenticado.")
#     st.stop()

# if st.session_state.get("tipo_usuario", "") != "admin":
#     st.error("⛔ Acesso negado. Esta página é restrita a administradores.")
#     st.stop()


## VARIAVEIS GLOBAIS .ENV ##
logo_dc = os.getenv('LOGO_DROGA_CLARA')
ARV_MERCADOLOGICA = os.getenv('ARV_MERCADOLOGICA')


mostrar_dash_farma = True
mostrar_dash_loja = True


if 'filtro_filial' not in st.session_state: 
    st.session_state.filtro_filial = []
if 'filtro_linha' not in st.session_state: 
    st.session_state.filtro_linha = []
if 'filtro_fabricante' not in st.session_state: 
    st.session_state.filtro_fabricante = []
if 'filtro_lista' not in st.session_state: 
    st.session_state.filtro_lista = []
if 'filtro_data' not in st.session_state: 
    st.session_state.filtro_data = []
if 'filtro_mes' not in st.session_state: 
    st.session_state.filtro_mes = []
if 'filtro_farma_filial' not in st.session_state: 
    st.session_state.filtro_farma_filial = []
if 'filtro_farma_linha' not in st.session_state: 
    st.session_state.filtro_farma_linha = []
if 'filtro_farma_fabricante' not in st.session_state: 
    st.session_state.filtro_farma_fabricante = []
if 'filtro_farma_lista' not in st.session_state: 
    st.session_state.filtro_farma_lista = []
if 'filtro_farma_data' not in st.session_state: 
    st.session_state.filtro_farma_data = []
if 'filtro_farma_mes' not in st.session_state: 
    st.session_state.filtro_farma_mes = []   
if 'filtro_resumo_filial' not in st.session_state: 
    st.session_state.filtro_resumo_filial = []
if 'filtro_resumo_linha' not in st.session_state: 
    st.session_state.filtro_resumo_linha = []
if 'filtro_resumo_fabricante' not in st.session_state: 
    st.session_state.filtro_resumo_fabricante = []
if 'filtro_resumo_lista' not in st.session_state: 
    st.session_state.filtro_resumo_lista = []
if 'filtro_resumo_data' not in st.session_state: 
    st.session_state.filtro_resumo_data = []
if 'filtro_resumo_mes' not in st.session_state: 
    st.session_state.filtro_resumo_mes = []   


## CONFIGURAÇÕES DA PAGINA ##
st.set_page_config(
    page_title='DASHBOARD',
    page_icon =logo_dc,
    layout='wide',
    initial_sidebar_state = 'auto')

engine = iniciar_conexao()
CONFIG_DB = ReadEditDB(engine=engine)


listas_cadastradas  = CONFIG_DB.listas_read_geral_dash(database="contagem_loja", table="LISTAS_CADASTRADAS")
df_cont_enviada_loja = CONFIG_DB.listas_read_geral_dash(database="contagem_loja", table="CONTAGEM_LOJA_ENVIADA")
df_cont_enviada_farma = CONFIG_DB.listas_read_geral_dash(database="contagem_loja", table="CONTAGEM_FARMA_ENVIADA")

if not df_cont_enviada_loja.empty and not listas_cadastradas.empty and not df_cont_enviada_farma.empty:
    df_loja_dash = df_cont_enviada_loja.merge(listas_cadastradas, on='CODIGO_LISTA', how='left')  
    try: 
        df_loja_dash['DATA'] = df_loja_dash['DATA_CONTAGEM_FIN'].dt.date
        df_loja_dash['MES_ANO'] = (df_loja_dash['DATA_CONTAGEM_FIN'].dt.year*100)+(df_loja_dash['DATA_CONTAGEM_FIN'].dt.month)
        df_loja_dash['DIFERENCA'] = df_loja_dash['FISICO']-df_loja_dash['SISTEMA']       
    except Exception as e:
        df_loja_dash['DATA'] = None
        df_loja_dash['MES_ANO'] = None
        df_loja_dash['DIFERENCA'] = None
        mostrar_dash_loja = False
        pass
    df_farma_dash = df_cont_enviada_farma.merge(listas_cadastradas, on='CODIGO_LISTA', how='left')
    try: 
        df_farma_dash['DATA'] = df_farma_dash['DATA_CONTAGEM_FIN'].dt.date
        df_farma_dash['MES_ANO'] = (df_farma_dash['DATA_CONTAGEM_FIN'].dt.year*100)+(df_farma_dash['DATA_CONTAGEM_FIN'].dt.month)
        df_farma_dash['DIFERENCA'] = df_farma_dash['FISICO']-df_farma_dash['SISTEMA']
    except Exception as e:
        df_farma_dash['DATA'] = None
        df_farma_dash['MES_ANO'] = None
        df_farma_dash['DIFERENCA'] = None
        mostrar_dash_farma = False
        pass
    
container_dash = st.container(border = True,
                                horizontal = True,
                                width=2000)

aba_macro_loja , aba_macro_farma, aba_resumo = container_dash.tabs(['📊 Macro Lojas','📊 Macro Farmas','✅ CheckList'])

with aba_macro_loja:
    if mostrar_dash_loja:
        linha_filtros = st.columns([1,1,1,1,1,1])
        linha_1 = st.columns([0.7,0.7,0.7,0.7,0.7,3])
        linha_2 = st.columns([1.75,1.75,3],vertical_alignment='top')
        filtros_ativos = {
                'FILIAL': st.session_state.filtro_filial,
                'Linha': st.session_state.filtro_linha,
                'NomeFabricante': st.session_state.filtro_fabricante,
                'CODIGO_LISTA': st.session_state.filtro_lista,
                'DATA': st.session_state.filtro_data,
                'MES_ANO': st.session_state.filtro_mes
            }

        def gerar_opcoes(coluna_alvo):
            df_temp = df_loja_dash.copy()
            for coluna, escolhas in filtros_ativos.items():
                if coluna != coluna_alvo and escolhas:
                    df_temp = df_temp[df_temp[coluna].isin(escolhas)]
            return df_temp[coluna_alvo].unique()

        linha_filtros[0].multiselect("Filial:", options=gerar_opcoes('FILIAL'), key='filtro_filial')
        linha_filtros[1].multiselect("Linha:", options=gerar_opcoes('Linha'), key='filtro_linha')
        linha_filtros[2].multiselect("Fabricante:", options=gerar_opcoes('NomeFabricante'), key='filtro_fabricante')
        linha_filtros[3].multiselect("Lista:", options=gerar_opcoes('CODIGO_LISTA'), key='filtro_lista')
        linha_filtros[4].multiselect("Data:", options=gerar_opcoes('DATA'), key='filtro_data')
        linha_filtros[5].multiselect("Mes Ano:", options=gerar_opcoes('MES_ANO'), key='filtro_mes')

        for coluna, escolhas in filtros_ativos.items():
            if escolhas:
                df_loja_dash = df_loja_dash[df_loja_dash[coluna].isin(escolhas)]
                
        df_loja_dash = df_loja_dash.fillna(0)
        df_loja_dash['DIF_ABS'] = df_loja_dash['DIFERENCA'].abs()
        pivot_filial_acur = df_loja_dash.pivot_table(index='FILIAL',
                                                        values=['SISTEMA','DIF_ABS'],
                                                        aggfunc='sum').reset_index()
        
        pivot_filial_acur['ACURACIDADE_%'] = (1-(pivot_filial_acur['DIF_ABS']/pivot_filial_acur['SISTEMA']))*100 
        df_loja_dash['TIPO_DIVERGENCIA'] = df_loja_dash['DIFERENCA'].apply(lambda x: 'Sobra' if x > 0 else 'Falta')
        df_barras = df_loja_dash.groupby(['Linha', 'TIPO_DIVERGENCIA'], as_index=False)['DIFERENCA'].sum()
        

        sistema_total = None
        sku_contagem = None
        falta_total = None
        sku_falta = None
        sobra_total = None
        sku_sobra = None
        sku_diferentes = None
        acuracidade_qtd = None
        
        try:
            acuracidade_qtd = (1-(pivot_filial_acur['DIF_ABS'].sum()/pivot_filial_acur['SISTEMA'].sum()))*100 
            sistema_total = df_loja_dash['SISTEMA'].sum()
            sku_diferentes = df_loja_dash[df_loja_dash['DIFERENCA'] != 0]['SKU'].nunique() 
            sku_contagem = df_loja_dash['SKU'].nunique()
            df_negativos = df_loja_dash[df_loja_dash['DIFERENCA']<0]
            falta_total = df_negativos['DIFERENCA'].sum()
            sku_falta = df_negativos['SKU'].nunique()
            df_positivos = df_loja_dash[df_loja_dash['DIFERENCA']>0]
            sobra_total = df_positivos['DIFERENCA'].sum()
            sku_sobra = df_positivos['SKU'].nunique()
            df_negativos = df_negativos.pivot_table(index=['SKU','Descricao',
                                                            'NomeFabricante','Linha'],
                                                    values=['SISTEMA','FISICO','DIFERENCA'],
                                                    aggfunc='sum').reset_index()
            
            df_positivos = df_positivos.pivot_table(index=['SKU','Descricao',
                                                            'NomeFabricante','Linha'],
                                                    values=['SISTEMA','FISICO','DIFERENCA'],
                                                    aggfunc='sum').reset_index()
        except:
            pass  
        
        linha_1[0].metric(label="Sku Contados: ",
                        value=f"{sku_contagem} SKU",
                        delta = f"{acuracidade_qtd:.2f}%",
                        delta_description='Acur. Qtd',
                        delta_color = "off",
                        delta_arrow = "off",                      
                        border=True)
        linha_1[1].metric(label="Sku Divergentes: ",
                        value=f"{sku_diferentes} SKU",
                        delta=f"{100-((sku_diferentes/sku_contagem)*100):.2f}%",
                        delta_color = "off",
                        delta_arrow = "off",
                        delta_description='Acur. itens',
                        border=True)
        linha_1[2].metric(label="Sobra QTD: ",
                        value=f"{int(sobra_total):.0f} UND",
                        delta=f"{((sobra_total/sistema_total)*100):.2f}%",
                        delta_description='do estoque',
                        delta_color = "off",
                        delta_arrow = "off",
                        border=True)
        linha_1[3].metric(label="Falta QTD: ",
                        value=f"{int(falta_total)} UND",
                        delta=f"{((falta_total/sistema_total)*100):.2f}%",
                        delta_description='do estoque',
                        delta_color = "off",
                        delta_arrow = "off",
                        border=True)
        linha_1[4].metric(label="Estoque Sistema: ",
                        value=f"{int(sistema_total)} UND",
                        delta=f"Estoque que deveria ter",
                        delta_color = "off",
                        delta_arrow = "off",
                        border=True)    
        linha_1[5].dataframe(df_negativos,
                            hide_index=True,
                            height=300
                            )     
        
        
        linha_2[2].dataframe(df_positivos,
                            hide_index=True,
                            height=300
                            )   
        ## GRAFICO TREEMAP
        fig_treemap = px.treemap(
            pivot_filial_acur,
            path=[px.Constant("Todas as Filiais"), 'FILIAL'],
            values='ACURACIDADE_%',
            color='FILIAL')
        fig_treemap.update_traces(
            textinfo="label+value",
            hovertemplate='<b>Filial: %{label}</b><br>Acuracidade: %{value:.2f}<extra></extra>',
            textfont_size=16
        )
        
        fig_treemap.update_layout(margin=dict(t=50, l=25, r=25, b=25))
            
        linha_2[0].plotly_chart(fig_treemap, 
                                use_container_width=True,
                                on_select='rerun')
        ## GRAFICO BARRAS
        fig_barras = px.bar(
            df_barras,
            x='Linha',
            y='DIFERENCA',
            color='TIPO_DIVERGENCIA',
            barmode='group', 
            title="Divergências (Sobras e Faltas) por Linha",
            text='DIFERENCA', 
            color_discrete_map={'Sobra': '#122335', 'Falta': '#2a8b75'} 
        )
        fig_barras.update_traces(
            textposition='outside',
            texttemplate='%{text:,.0f}' 
        )
        
        fig_barras.update_layout(
            xaxis_title=None, 
            yaxis_title="Quantidade (Unidades)",
            legend_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5), 
            margin=dict(b=80)
        )
        
        linha_2[1].plotly_chart(fig_barras, use_container_width=True)
    else:
        st.info("Sem dados atuais para mostrar na DASHBOARD")

with aba_macro_farma:
    if mostrar_dash_farma:
        linha_filtros = st.columns([1,1,1,1,1,1])
        linha_1 = st.columns([0.7,0.7,0.7,0.7,0.7,3])
        linha_2 = st.columns([1.75,1.75,3],vertical_alignment='top')
        filtros_ativos = {
                'FILIAL': st.session_state.filtro_farma_filial,
                'Linha': st.session_state.filtro_farma_linha,
                'NomeFabricante': st.session_state.filtro_farma_fabricante,
                'CODIGO_LISTA': st.session_state.filtro_farma_lista,
                'DATA': st.session_state.filtro_farma_data,
                'MES_ANO': st.session_state.filtro_farma_mes
            }

        def gerar_opcoes_farma(coluna_alvo):
            df_temp = df_farma_dash.copy()
            for coluna, escolhas in filtros_ativos.items():
                if coluna != coluna_alvo and escolhas:
                    df_temp = df_temp[df_temp[coluna].isin(escolhas)]
            return df_temp[coluna_alvo].unique()

        linha_filtros[0].multiselect("Filial:", options=gerar_opcoes_farma('FILIAL'), key='filtro_farma_filial')
        linha_filtros[1].multiselect("Linha:", options=gerar_opcoes_farma('Linha'), key='filtro_farma_linha')
        linha_filtros[2].multiselect("Fabricante:", options=gerar_opcoes_farma('NomeFabricante'), key='filtro_farma_fabricante')
        linha_filtros[3].multiselect("Lista:", options=gerar_opcoes_farma('CODIGO_LISTA'), key='filtro_farma_lista')
        linha_filtros[4].multiselect("Data:", options=gerar_opcoes_farma('DATA'), key='filtro_farma_data')
        linha_filtros[5].multiselect("Mes Ano:", options=gerar_opcoes_farma('MES_ANO'), key='filtro_farma_mes')

        for coluna, escolhas in filtros_ativos.items():
            if escolhas:
                df_farma_dash = df_farma_dash[df_farma_dash[coluna].isin(escolhas)]
                
        df_farma_dash = df_farma_dash.fillna(0)
        df_farma_dash['DIF_ABS'] = df_farma_dash['DIFERENCA'].abs()
        pivot_filial_acur = df_farma_dash.pivot_table(index='FILIAL',
                                                        values=['SISTEMA','DIF_ABS'],
                                                        aggfunc='sum').reset_index()
        
        pivot_filial_acur['ACURACIDADE_%'] = (1-(pivot_filial_acur['DIF_ABS']/pivot_filial_acur['SISTEMA']))*100 
        df_farma_dash['TIPO_DIVERGENCIA'] = df_farma_dash['DIFERENCA'].apply(lambda x: 'Sobra' if x > 0 else 'Falta')
        df_barras = df_farma_dash.groupby(['Linha', 'TIPO_DIVERGENCIA'], as_index=False)['DIFERENCA'].sum()
        # df_farma_dash.to_excel("testecont.xlsx")

        sistema_total = None
        sku_contagem = None
        falta_total = None
        sku_falta = None
        sobra_total = None
        sku_sobra = None
        sku_diferentes = None
        acuracidade_qtd = None
        
        try:
            acuracidade_qtd = (1-(pivot_filial_acur['DIF_ABS'].sum()/pivot_filial_acur['SISTEMA'].sum()))*100 
            sistema_total = df_farma_dash['SISTEMA'].sum()
            sku_diferentes = df_farma_dash[df_farma_dash['DIFERENCA'] != 0]['SKU'].nunique() 
            sku_contagem = df_farma_dash['SKU'].nunique()
            df_negativos = df_farma_dash[df_farma_dash['DIFERENCA']<0]
            falta_total = df_negativos['DIFERENCA'].sum()
            sku_falta = df_negativos['SKU'].nunique()
            df_positivos = df_farma_dash[df_farma_dash['DIFERENCA']>0]
            sobra_total = df_positivos['DIFERENCA'].sum()
            sku_sobra = df_positivos['SKU'].nunique()
            df_negativos = df_negativos.pivot_table(index=['SKU','Descricao',
                                                            'NomeFabricante','Linha'],
                                                    values=['SISTEMA','FISICO','DIFERENCA'],
                                                    aggfunc='sum').reset_index()
            
            df_positivos = df_positivos.pivot_table(index=['SKU','Descricao',
                                                            'NomeFabricante','Linha'],
                                                    values=['SISTEMA','FISICO','DIFERENCA'],
                                                    aggfunc='sum').reset_index()
        except:
            pass  
        
        linha_1[0].metric(label="Sku Contados: ",
                        value=f"{int(sku_contagem)} SKU",
                        delta = f"{acuracidade_qtd:.2f}%",
                        delta_description='Acur. Qtd',
                        delta_color = "off",
                        delta_arrow = "off",                      
                        border=True)
        linha_1[1].metric(label="Sku Divergentes: ",
                        value=f"{int(sku_diferentes)} SKU",
                        delta=f"{100-((sku_diferentes/sku_contagem)*100):.2f}%",
                        delta_color = "off",
                        delta_arrow = "off",
                        delta_description='Acur. itens',
                        border=True)
        linha_1[2].metric(label="Sobra QTD: ",
                        value=f"{int(sobra_total)} UND",
                        delta=f"{((sobra_total/sistema_total)*100):.2f}%",
                        delta_description='do estoque',
                        delta_color = "off",
                        delta_arrow = "off",
                        border=True)
        linha_1[3].metric(label="Falta QTD: ",
                        value=f"{int(falta_total)} UND",
                        delta=f"{((falta_total/sistema_total)*100):.2f}%",
                        delta_description='do estoque',
                        delta_color = "off",
                        delta_arrow = "off",
                        border=True)
        linha_1[4].metric(label="Estoque Sistema: ",
                        value=f"{int(sistema_total)} UND",
                        delta=f"Estoque que deveria ter",
                        delta_color = "off",
                        delta_arrow = "off",
                        border=True)    
        linha_1[5].dataframe(df_negativos,
                            hide_index=True,
                            height=300
                            )     
        
        
        linha_2[2].dataframe(df_positivos,
                            hide_index=True,
                            height=300
                            )   
        ## GRAFICO TREEMAP
        fig_treemap = px.treemap(
            pivot_filial_acur,
            path=[px.Constant("Todas as Filiais"), 'FILIAL'],
            values='ACURACIDADE_%',
            color='FILIAL')
        fig_treemap.update_traces(
            textinfo="label+value",
            hovertemplate='<b>Filial: %{label}</b><br>Acuracidade: %{value:.2f}<extra></extra>',
            textfont_size=16
        )
        
        fig_treemap.update_layout(margin=dict(t=50, l=25, r=25, b=25))
            
        linha_2[0].plotly_chart(fig_treemap, 
                                use_container_width=True,
                                on_select='rerun')
        ## GRAFICO BARRAS
        fig_barras = px.bar(
            df_barras,
            x='Linha',
            y='DIFERENCA',
            color='TIPO_DIVERGENCIA',
            barmode='group', 
            title="Divergências (Sobras e Faltas) por Linha",
            text='DIFERENCA', 
            color_discrete_map={'Sobra': '#122335', 'Falta': '#2a8b75'} 
        )
        fig_barras.update_traces(
            textposition='outside',
            texttemplate='%{text:,.0f}' 
        )
        
        fig_barras.update_layout(
            xaxis_title=None, 
            yaxis_title="Quantidade (Unidades)",
            legend_title=None,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5), 
            margin=dict(b=80)
        )
        
        linha_2[1].plotly_chart(fig_barras, use_container_width=True)
    else:
        st.info("Sem dados atuais para mostrar na DASHBOARD")
        
with aba_resumo:
    linha_filtros = st.columns([1,1,1,1,1,1])
    linhas_nomes = st.columns([1,1])
    linha_tabelas = st.columns([1,1])    
    data_minima = datetime.today().date()
    
    try:
        usuarios_base = CONFIG_DB.listas_read_geral_dash(database="contagem_loja", table="USERS")

        usuarios_base = usuarios_base[usuarios_base['TIPO']=='geral']
        usuarios_base = usuarios_base[usuarios_base['STATUS']==1]
        
    except Exception as e:
        usuarios_base = pd.DataFrame()
        st.info("SEM DADOS PARA MOSTRAR NO MOMENTO")

    
    df_cont_enviada_loja = CONFIG_DB.listas_read_geral_dash(database="contagem_loja", table="CONTAGEM_LOJA_ENVIADA")
    df_cont_enviada_farma = CONFIG_DB.listas_read_geral_dash(database="contagem_loja", table="CONTAGEM_FARMA_ENVIADA")
    
    data_minima_loja = df_cont_enviada_loja['DATA_CONTAGEM_FIN'].min()
    data_minima_farma = df_cont_enviada_farma['DATA_CONTAGEM_FIN'].min()

    data_minima = min(data_minima_farma, data_minima_loja)
    
    filtro_data_resumo = linha_filtros[0].date_input("Data da contagem:",
                                                min_value=data_minima,
                                                max_value=datetime.today().date(),
                                                value=datetime.today().date())

    df_cont_enviada_loja = df_cont_enviada_loja[df_cont_enviada_loja['DATA_CONTAGEM_FIN'].dt.date == filtro_data_resumo]
    df_cont_enviada_farma = df_cont_enviada_farma[df_cont_enviada_farma['DATA_CONTAGEM_FIN'].dt.date == filtro_data_resumo]
    df_cont_enviada_loja['DIFERENCA'] = df_cont_enviada_loja['FISICO']-df_cont_enviada_loja['SISTEMA']  
    df_cont_enviada_farma['DIFERENCA'] = df_cont_enviada_farma['FISICO']-df_cont_enviada_farma['SISTEMA']
            
    df_cont_enviada_loja['DIF_ABS'] = df_cont_enviada_loja['DIFERENCA'].abs()
    df_cont_enviada_farma['DIF_ABS'] = df_cont_enviada_farma['DIFERENCA'].abs()
    
    try:
        pivot_cont_loja = df_cont_enviada_loja.pivot_table(index=['FILIAL'],
                                                            values=['DATA_CONTAGEM_FIN','DIF_ABS','SISTEMA'],
                                                            aggfunc={'DATA_CONTAGEM_FIN':'max',
                                                                    'DIF_ABS':'sum',
                                                                    'SISTEMA':'sum'}).reset_index()
        pivot_cont_loja['ACURACIDADE_%'] = round((1-(pivot_cont_loja['DIF_ABS']/pivot_cont_loja['SISTEMA']))*100,2)  
        
        
        df_mostrar_loja = usuarios_base.merge(pivot_cont_loja, left_on="EMAIL",right_on='FILIAL', how="left")
        df_mostrar_loja = df_mostrar_loja[['USUARIO','DATA_CONTAGEM_FIN','DIF_ABS','ACURACIDADE_%']]        
    except:
        df_mostrar_loja = pd.DataFrame()    
    
    try:
        pivot_cont_farma = df_cont_enviada_farma.pivot_table(index=['FILIAL'],
                                                            values=['DATA_CONTAGEM_FIN','DIF_ABS','SISTEMA'],
                                                            aggfunc={'DATA_CONTAGEM_FIN':'max',
                                                                    'DIF_ABS':'sum',
                                                                    'SISTEMA':'sum'}).reset_index()
        pivot_cont_farma['ACURACIDADE_%'] = round((1-(pivot_cont_farma['DIF_ABS']/pivot_cont_farma['SISTEMA']))*100,2)
        
        df_mostrar_farma = usuarios_base.merge(pivot_cont_farma, left_on="EMAIL",right_on='FILIAL', how="left")
        df_mostrar_farma = df_mostrar_farma[['USUARIO','DATA_CONTAGEM_FIN','DIF_ABS','ACURACIDADE_%']]
    except:
        df_mostrar_farma = pd.DataFrame()  
    
    try:
        lojas_enviaram = df_mostrar_loja[~df_mostrar_loja['DIF_ABS'].isna()]['USUARIO'].nunique() 
        farma_enviaram = df_mostrar_farma[~df_mostrar_farma['DIF_ABS'].isna()]['USUARIO'].nunique() 
        linhas_nomes[0].markdown(f"## Contagens loja enviadas ({lojas_enviaram} enviaram)")
        linhas_nomes[1].markdown(f"## Contagens Farma enviadas ({farma_enviaram} enviaram)")
    except:
        st.info("SEM DADOS PARA A DATA SELECIONADA")
    
    linha_tabelas[0].dataframe(df_mostrar_loja,
                               height='content',
                               hide_index = True)
    linha_tabelas[1].dataframe(df_mostrar_farma,
                               height='content',
                               hide_index = True)