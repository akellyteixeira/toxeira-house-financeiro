from pandas import options

from F_ReadEditDB import ReadEditDB
from F_Conexao import iniciar_conexao
from elements import metricas_gerar,carregar_imagem_local   
from dotenv import load_dotenv
from datetime import datetime
import streamlit.components.v1 as components
import streamlit as st
import os
import io

load_dotenv(override=True)


# # --- CONFIGURANDO O TUNEL SSH E A CONEXAO COM O BANCO DA VPS ---
engine = iniciar_conexao()

# ## VARIAVEIS GLOBAIS .ENV ##
logo_dc = os.getenv('LOGO_DROGA_CLARA')
st.set_page_config(layout="wide")

# ## VARIAVEIS PARA MANTER O SITE FUNCIONANDO ANTES DE SUBIR AS PLANILHAS
hoje = datetime.now()
buffer = io.BytesIO()

# ## CONFIGURAÇÕES DA PAGINA ##

if 'codigo' not in st.session_state:
    st.session_state.codigo = None
if 'nova_resposta' not in st.session_state:
    st.session_state.nova_resposta = None

if 'filtro_codigo' not in st.session_state:
    st.session_state.filtro_codigo = []
if 'filtro_data' not in st.session_state:
    st.session_state.filtro_data = []
if 'filtro_status' not in st.session_state:
    st.session_state.filtro_status = []
if 'filtro_categoria' not in st.session_state:
    st.session_state.filtro_categoria= []
if 'filtro_urgencia' not in st.session_state:
    st.session_state.filtro_urgencia = []



aut_enviar_denuncia = True

if not st.session_state.get("autenticado", False):
    st.error("⛔ Acesso negado. Você precisa estar autenticado.")
    st.stop()

print(st.session_state)



logo_completo = r'C:\Users\Higor Rodrigues\Desktop\PROJETOS\PROJETO_DENUNCIAS_INTERNAS\DENUNCIAS_INTERNAS\ASSETS\logo_completo.png'
logo_b64 = carregar_imagem_local(logo_completo)



## EDIÇÃO PARA OS CONTAINERS DAS RESPOSTAS
st.markdown("""
<style>
/* Seleciona qualquer div cuja classe contenha 'st-key-' E também a palavra 'userden' */
div[class*="st-key-"][class*="userden"] {
    border: 3px solid #b1d0e6 !important;    /* Borda azul */
    background-color: #f0f9ff !important;   /* Fundo verde */
    padding: 1.5rem;                      /* Espaçamento interno (opcional) */
    border-radius: 8px;                   /* Arredondamento das bordas (opcional) */
}

/* Força a cor do texto para vermelho em TODOS os elementos dentro desses containers */
div[class*="st-key-"][class*="userden"] * {
    color: #06203b !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* Seleciona qualquer div cuja classe contenha 'st-key-' E também a palavra 'userresp' */
div[class*="st-key-"][class*="userresp"] {
    border: 3px solid #8c8c8c !important; 
    background-color: #f0f2f6 !important; 
    padding: 1.5rem;                      
    border-radius: 8px;                   
}

/* Força a cor do texto para vermelho em TODOS os elementos dentro desses containers */
div[class*="st-key-"][class*="userresp"] * {
    color: #8c8c8c !important;
}
</style>
""", unsafe_allow_html=True)

html_cabecalho = f"""
<div style="text-align: center; margin-top: 20px; margin-bottom: 30px; font-family: sans-serif;">    
    <img src="data:image/png;base64,{logo_b64}" width="250" style="margin-bottom: 15px;">
    <h4 style="color: #2c3e50; 
        margin: 0; 
        letter-spacing: 1px;
        font-size: 150%;">
        ACOMPANHAMENTO DENUNCIAS
    </h4>
</div>
"""


## CONFIGURANDO READ DB ##
CONFIG_DB = ReadEditDB(engine=engine)

df_status = CONFIG_DB.geral_read(database='denuncia_anonima',
                                 table='STATUS')
df_categoria = CONFIG_DB.geral_read(database='denuncia_anonima',
                                 table='CATEGORIAS')
df_urgencia = CONFIG_DB.geral_read(database='denuncia_anonima',
                                 table='URGENCIAS')
df_denuncias = CONFIG_DB.geral_read(database='denuncia_anonima',
                                 table='DENUNCIAS_PRIMARIO')

df_status = df_status.rename(columns={'DESCRICAO':'DESCRICAO_STATUS'})
df_categoria = df_categoria.rename(columns={'DESCRICAO':'DESCRICAO_CAT'})
df_urgencia = df_urgencia.rename(columns={'DESCRICAO':'DESCRICAO_URG'})
df_mostrar = df_denuncias.merge(df_status, left_on='STATUS', right_on='CODIGO_STATUS', how='left')
df_mostrar = df_mostrar.merge(df_categoria, left_on='CATEGORIA', right_on='CODIGO_CATEGORIA', how='left')
df_mostrar = df_mostrar.merge(df_urgencia, left_on='GRAVIDADE', right_on='CODIGO_URGENCIA', how='left')

st.sidebar.markdown(f'''# **{CONFIG_DB.usuarios_read_login(database='denuncia_anonima',
                                                         table='USUARIOS',
                                                         usuario=st.session_state.get("usuario_logado")
                                                         )['NOME'].iloc[0]}**''')



_,titulo,_ = st.columns([1,3,1])
titulo.html(html_cabecalho)

container_principal = st.container(border=True,
                                   )


with container_principal:
    

    linha_metricas = container_principal.columns([1,1,1,1,1,1,1,1])
    
    
 
    try:
        df_mostrar['DATA'] = df_mostrar['DATA_ABERTURA'].dt.strftime('%d/%m/%Y')
        total_denuncias       = df_mostrar['CODIGO'].nunique()
        denuncias_finalizadas = df_mostrar['CODIGO'].loc[df_mostrar['STATUS']==3].nunique()
        denuncias_emanalize   = df_mostrar['CODIGO'].loc[df_mostrar['STATUS']==2].nunique()
        delta_emanalise       = (denuncias_emanalize/total_denuncias)*100 
        delta_fializados      = (denuncias_finalizadas/total_denuncias)*100 
    except:
        total_denuncias       = None
        denuncias_finalizadas = None
        denuncias_emanalize   = None
        delta_emanalise       = None
        delta_fializados      = None 



    metricas_gerar(position=linha_metricas[5],
                   label='**Total Denuncias:**',
                   value=f'{total_denuncias} Denuncias',
                   delta='Denuncias filtradas')

    metricas_gerar(position=linha_metricas[6],
                   label='**Denuncias Em Analise:**',
                   value=denuncias_emanalize,
                   delta=f"{delta_emanalise}%")

    metricas_gerar(position=linha_metricas[7],
                   label='**Denuncias Finalizadas:**',
                   value=denuncias_finalizadas,
                   delta=f"{delta_fializados}%"
                   )


    filtros_ativos = {
        'CODIGO': st.session_state.filtro_codigo,
        'DATA': st.session_state.filtro_data,
        'DESCRICAO_STATUS': st.session_state.filtro_status,
        'DESCRICAO_CAT': st.session_state.filtro_categoria,
        'DESCRICAO_URG': st.session_state.filtro_urgencia,
    }
 
    def gerar_opcoes(coluna_alvo):
        df_temp = df_mostrar.copy()
        for coluna, escolhas in filtros_ativos.items():
            if coluna != coluna_alvo and escolhas:
                df_temp = df_temp[df_temp[coluna].isin(escolhas)]
        return df_temp[coluna_alvo].unique()

    linha_metricas[0].multiselect("Codigo:", options=gerar_opcoes('CODIGO'), key='filtro_codigo')
    linha_metricas[1].multiselect("Data Abertura:", options=gerar_opcoes('DATA'), key='filtro_data')
    linha_metricas[2].multiselect("Status:", options=gerar_opcoes('DESCRICAO_STATUS'), key='filtro_status')
    linha_metricas[3].multiselect("Categoria:", options=gerar_opcoes('DESCRICAO_CAT'), key='filtro_categoria')
    linha_metricas[4].multiselect("Urgencia:", options=gerar_opcoes('DESCRICAO_URG'), key='filtro_urgencia')
    
    for coluna, escolhas in filtros_ativos.items():                          
        if escolhas:                                                         
            df_mostrar = df_mostrar[df_mostrar[coluna].isin(escolhas)] 
    
    
    def codigo_get ():
        st.session_state.codigo = df_mostrar['CODIGO'].iloc[st.session_state.get("botao_detalhar").get("row")]
        return st.session_state.codigo 

    def status_get ():
        st.session_state.status = df_show['STATUS_AJUSTAR'].iloc[st.session_state.get("botao_status").get("row")]
        st.session_state.codigo = df_mostrar['CODIGO'].iloc[st.session_state.get("botao_status").get("row")]

        if st.session_state.codigo != None and st.session_state.status != None:
            status_subir = df_status[df_status['DESCRICAO_STATUS']==st.session_state.status]['CODIGO_STATUS'].iloc[0]
            print(status_subir)
            CONFIG_DB.mudar_status(status=status_subir,
                                   codigo=st.session_state.codigo)
        else:
            st.error("Não foi possivel ajustar o status")
            
        return st.session_state.codigo 
     
    df_mostrar['DETALHAR'] = "Ver Detalhes"
    df_mostrar['STATUS_AJUSTAR'] = 'Mudar Status'
    df_mostrar['MUDAR_STATUS'] = 'Alterar Status'
    df_data_editor = df_mostrar.copy()
    df_data_editor['DATA_ABERTURA'] = df_data_editor['DATA_ABERTURA'].dt.strftime( '%d/%m/%Y - %H:%mh')
    df_data_editor = df_data_editor[['CODIGO','DATA_ABERTURA','DESCRICAO_CAT',
                                     'CATEGORIA_OUTROS','DESCRICAO_URG','DESCRICAO_STATUS',
                                     'STATUS_AJUSTAR','MUDAR_STATUS','DETALHAR']]
    df_show = st.data_editor(df_data_editor,
                             key="df_data_editor",
                              column_config={
                                 "DETALHAR": st.column_config.ButtonColumn("DETALHES",
                                                                          type='primary',
                                                                          on_click=codigo_get,
                                                                          key="botao_detalhar"),
                                 
                                 "MUDAR_STATUS": st.column_config.ButtonColumn("MUDAR STATUS",
                                                                          type='primary',
                                                                          on_click=status_get,
                                                                          key="botao_status"),
 

                                  "STATUS_AJUSTAR": st.column_config.SelectboxColumn("STATUS_NOVO",
                                                                                    options=df_status['DESCRICAO_STATUS'].unique())



                             },

                              hide_index=True)

    if st.session_state.get('botao_detalhar'):
        print(st.session_state)
        # time.sleep(2)
        st.switch_page("PAGINA_ACOMPANHAMENTO.py")
