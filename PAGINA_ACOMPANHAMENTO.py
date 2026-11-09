from F_ReadEditDB import ReadEditDB
from F_Conexao import iniciar_conexao
from elements import carregar_imagem_local, html_badge, download_evidencias, gerar_respostas_container
from dotenv import load_dotenv
from datetime import datetime
import streamlit.components.v1 as components
import base64
import time
import streamlit as st
import pandas as pd
import os
import io

load_dotenv(override=True)


# # --- CONFIGURANDO O TUNEL SSH E A CONEXAO COM O BANCO DA VPS ---
engine = iniciar_conexao()
CONFIG_DB = ReadEditDB(engine=engine)


# ## VARIAVEIS GLOBAIS .ENV ##
logo_dc = os.getenv('LOGO_DROGA_CLARA')


# ## VARIAVEIS PARA MANTER O SITE FUNCIONANDO ANTES DE SUBIR AS PLANILHAS
hoje = datetime.now()
buffer = io.BytesIO()

print(st.session_state)
# ## CONFIGURAÇÕES DA PAGINA ##

if 'codigo' not in st.session_state:
    st.session_state.codigo = None
if 'nova_resposta' not in st.session_state:
    st.session_state.nova_resposta = None
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = 2
if 'df_denuncia_existente' not in st.session_state:
    st.session_state.df_denuncia_existente = pd.DataFrame()
    
if st.session_state.get('df_denuncia_existente').empty:    

    df_denuncia = CONFIG_DB.denuncia_read(database='denuncia_anonima',
                                        table='DENUNCIAS_PRIMARIO',
                                        codigo=st.session_state.get("codigo"))
else:
    df_denuncia = st.session_state.get('df_denuncia_existente')


        
        
aut_enviar_denuncia = True


if not st.session_state.get("codigo", False):
    st.error("⛔ Acesso negado. Você precisa consultar uma consulta ja existente.")
    st.stop()



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
        DENUNCIA {st.session_state.get('codigo')}
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




df_status = CONFIG_DB.geral_read(database='denuncia_anonima',
                                 table='STATUS')
df_categoria = CONFIG_DB.geral_read(database='denuncia_anonima',
                                 table='CATEGORIAS')
df_urgencia = CONFIG_DB.geral_read(database='denuncia_anonima',
                                 table='URGENCIAS')
df_respostas = CONFIG_DB.read_respostas(codigo_den=st.session_state.get("codigo"))



df_status = df_status.rename(columns={'DESCRICAO':'DESCRICAO_STATUS'})
df_categoria = df_categoria.rename(columns={'DESCRICAO':'DESCRICAO_CAT'})
df_urgencia = df_urgencia.rename(columns={'DESCRICAO':'DESCRICAO_URG'})
df_mostrar = df_denuncia.merge(df_status, left_on='STATUS', right_on='CODIGO_STATUS', how='left')
df_mostrar = df_mostrar.merge(df_categoria, left_on='CATEGORIA', right_on='CODIGO_CATEGORIA', how='left')
df_mostrar = df_mostrar.merge(df_urgencia, left_on='GRAVIDADE', right_on='CODIGO_URGENCIA', how='left')


_,titulo,_ = st.columns([1,3,1])
titulo.html(html_cabecalho)

container_principal = st.container(border=True,
                                  horizontal = False,
                                  )

with container_principal:
    _, centro, _ = st.columns([1,6,1])
    with centro:
        data_abertura, categoria, categoria_outros, gravidade, status, botao_download = st.columns([1,1,1,1,1,1], vertical_alignment='bottom')
        
        botao_download_evid = download_evidencias(path=df_mostrar['PATH_EVID'].iloc[0],
                                                  position=botao_download,
                                                  codigo=st.session_state.get('codigo'))
        
        
        data_titulo = data_abertura.markdown('**Data Abertura:**')
        data_text = html_badge(valor=df_mostrar['DATA_ABERTURA'].iloc[0],
                               position=data_abertura)
        
        categoria_titulo = categoria.markdown('**Categoria:**')
        categoria_text = html_badge(valor=df_mostrar['DESCRICAO_CAT'].iloc[0],
                               position=categoria)
        
        if df_mostrar['CATEGORIA'].iloc[0] == 8: #AQUI SOMENTE OUTROS
            catoutros_titulo = categoria_outros.markdown('**Categoria Outros:**')
            catoutros_text = html_badge(valor=df_mostrar['CATEGORIA_OUTROS'].iloc[0],
                                position=categoria_outros)
            
            gravidade_titulo = gravidade.markdown('**Urgencia:**')
            gravidade_text = html_badge(valor=f'Prioridade: {df_mostrar['DESCRICAO_URG'].iloc[0]}',
                                        position=gravidade)
            
            
            status_text = html_badge(valor=f'Prioridade: {df_mostrar['DESCRICAO_STATUS'].iloc[0]}',
                                        position=status)
        else:
            
            gravidade_titulo = gravidade.markdown('**Urgencia:**')
            gravidade_text = html_badge(valor=f'Prioridade: {df_mostrar['DESCRICAO_URG'].iloc[0]}',
                                        position=gravidade)
            
            status_titulo = status.markdown('**Status:**')
            status_text = html_badge(valor=f'Prioridade: {df_mostrar['DESCRICAO_STATUS'].iloc[0]}',
                                        position=status)
        st.divider()
        
        st.markdown(f'**Acompanhe as respostas respostas abaixo:**')
        
        container_conteudo = st.container(border=True,
                                              height=600)
        with container_conteudo:
            conteudo_titulo = st.markdown(f'{df_mostrar['DATA_ABERTURA'].iloc[0].strftime('%d/%m/%Y %H:%M:%S')} **Usuário Anonimo:**')  
                      
            with st.container(border=True, key="userden_0"):
                st.text(df_mostrar['CONTEUDO'].iloc[0])
            
            
            gerar_respostas_container(df=df_respostas)
            
        st.divider()
        
        nova_resposta, novas_evidencias, botao_nova_resposta = st.columns([3,1,1], vertical_alignment='center') 
        
        novas_tex = nova_resposta.text_area(label="**Inserir nova esposta:**",
                                            key='nova_resposta')
        novas_evi = novas_evidencias.file_uploader(label="**Novas Evidencias:**",
                                        accept_multiple_files=True,
                                        on_change='ignore',
                                        )
        
        if novas_tex or novas_evi:
            aut_enviar_denuncia = False
            
        botao_reg =  botao_nova_resposta.button('Enviar Denuncia',
                                                width='stretch',
                                                type='primary',
                                                disabled=aut_enviar_denuncia,
                                                help='Você deve preencher todos os campos obrigatórios indicados com * ')
               
        if botao_reg:
            
            df_subir_respostas = pd.DataFrame(
                {
                  "CODIGO":[st.session_state.get("codigo")],
                  "RESPOSTA":[st.session_state.get("nova_resposta")],
                  "USUARIO_RESPOSTA_COD":[st.session_state.get("usuario_logado")],
                  "DATA_RESPOSTA":datetime.now()
                    
                }
            )
         
            CONFIG_DB.upload_msql_df(df=df_subir_respostas,
                                    table='RESPOSTAS_DENUNCIAS',
                                    database='denuncia_anonima')
            
            if novas_evi:
                arquivo_salvo = 0
                arquivo_ignorado = 0
                    
                for arquivo in novas_evi:
                    caminho_completo = os.path.join(df_mostrar['PATH_EVID'].iloc[0], arquivo.name)
                    
                    if os.path.exists(caminho_completo):
                        arquivo_ignorado += 1
                    
                    else:
                        with open(caminho_completo, "wb") as saver:
                            saver.write(arquivo.getbuffer())
                        
                        arquivo_salvo += 1
                    
                    if arquivo_salvo > 0:
                        st.toast(f"{arquivo_salvo} arquivo(s) de evidencias salvos e enviados")    
                
            time.sleep(2)
            denuncia_pront = False 
            if 'codigo' in st.session_state:
                del st.session_state['codigo']
            
            st.switch_page("PAGINA_FINAL.py")
