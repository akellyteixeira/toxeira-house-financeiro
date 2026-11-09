import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime
from elements import carregar_imagem_local
from F_CreatNewDen import DenunciaClass
from F_Conexao import iniciar_conexao
from F_ReadEditDB import ReadEditDB

data = datetime.now()
path_evid = r'C:\Users\Higor Rodrigues\Desktop\PROJETOS\PROJETO_DENUNCIAS_INTERNAS\DENUNCIAS_INTERNAS\EVIDENCIAS'
logo_dc = r'C:\Users\Higor Rodrigues\Desktop\PROJETOS\PROJETO_DENUNCIAS_INTERNAS\DENUNCIAS_INTERNAS\ASSETS\logo-Droga-Claraa.png'
logo_completo = r'C:\Users\Higor Rodrigues\Desktop\PROJETOS\PROJETO_DENUNCIAS_INTERNAS\DENUNCIAS_INTERNAS\ASSETS\logo_completo.png'
logo_b64 = carregar_imagem_local(logo_completo)

config = DenunciaClass(path_pai_evidencias=path_evid)

html_cabecalho = f"""
<div style="text-align: center; margin-top: 20px; margin-bottom: 30px; font-family: sans-serif;">
    
    <img src="data:image/png;base64,{logo_b64}" width="300" style="margin-bottom: 15px;">
    
    <!-- TITULO -->
    <h4 style="color: #2c3e50; 
        margin: 0; 
        letter-spacing: 1px;
        font-size: 200%;">
        PORTAL DE DENÚNCIAS ANÔNIMAS
    </h4>
    
    <!-- LINHA SEPARADORA -->
    <hr style="width: 80%; margin: 20px auto; border-top: 1px solid #ddd;">
    
    <!-- TEXTO EXPLICATIVO -->
    <div style="text-align: left; max-width: 80%; margin: 0 auto; color: #444; line-height: 1.6; font-size: 16px;">
        
        <p style="margin-bottom: 20px;">
            Este portal é um ambiente seguro e exclusivo para que nossos colaboradores possam relatar, 
            de forma totalmente anônima, qualquer comportamento ou prática que viole os princípios, 
            valores e políticas internas da nossa rede. Nosso compromisso é manter um ambiente de trabalho íntegro, 
            transparente e de respeito mútuo.
        </p>

        <h5 style="color: #2c3e50; font-size: 18px; margin-top: 25px; margin-bottom: 10px;">
            O que pode ser relatado neste portal?
        </h5>
        
        <ul style="margin-bottom: 25px; padding-left: 20px;">
            <li style="margin-bottom: 8px;">Casos de assédio moral, sexual ou discriminação de qualquer natureza.</li>
            <li style="margin-bottom: 8px;">Suspeitas de fraudes, furtos, ou desvios de estoque e medicamentos.</li>
            <li style="margin-bottom: 8px;">Descumprimento de normas de saúde, segurança ou procedimentos operacionais padrão.</li>
            <li style="margin-bottom: 8px;">Qualquer outra conduta antiética, ilegal ou inadequada no ambiente de trabalho.</li>
        </ul>

        <h5 style="color: #2c3e50; font-size: 18px; margin-top: 25px; margin-bottom: 10px;">
            Garantia de Anonimato e Não Retaliação
        </h5>
        
        <p style="margin-bottom: 20px;">
            A sua segurança é a nossa prioridade. Este sistema foi estruturado para garantir <strong>100% de 
            confidencialidade</strong> e você não precisa se identificar em nenhum momento. A Droga Clara repudia 
            e proíbe estritamente qualquer tipo de retaliação contra colaboradores que registrarem denúncias de boa-fé.
        </p>
        
    </div>
</div>
"""

# --- CONFIGURANDO O TUNEL SSH E A CONEXAO COM O BANCO DA VPS ---
engine = iniciar_conexao()
CONFIG_DB = ReadEditDB(engine=engine)

## CONFIGURAÇÕES DA PAGINA ##
st.set_page_config(
    page_title='DENUNCIAS',
    page_icon =logo_dc,
    layout='wide',
    # initial_sidebar_state = 'auto',
    )


if 'codigo_in' not in st.session_state:
    st.session_state.codigo_in = False
if 'codigo' not in st.session_state:
    st.session_state.codigo = None
if 'codigo_existent' not in st.session_state:
    st.session_state.codigo_existent = ""
if 'path_evid' not in st.session_state:
    st.session_state.path_evid = ""
if 'df_denuncia' not in st.session_state:
    st.session_state.df_denuncia = pd.DataFrame()
if 'df_denuncia_existente' not in st.session_state:
    st.session_state.df_denuncia_existente = pd.DataFrame()
if 'tipo_acesso' not in st.session_state:
    st.session_state.tipo_acesso = None
    
if not st.session_state.tipo_acesso:
    janela_central = st.container(border = True,
                                 horizontal = True,
                                 )    
    with janela_central:        
        canto,titulo,__ = st.columns([1,3,1])
        
        ### BOTAO LOGIN ###
        botao_login = canto.button('login adm',
                                   type='secondary')
        if botao_login:
            st.session_state.tipo_acesso = "admin"        
        ### BOTAO LOGIN ###
        
        titulo.html(html_cabecalho)
        titulo.markdown("<p style='text-align: center; font-weight: bold; margin-bottom: 5px; margin-top: 30px;'>CASO JÁ TENHA UMA DENÚNCIA E QUEIRA ACOMPANHAR:</p>",
                        unsafe_allow_html=True)

        
        _, col_input, col_botao = titulo.columns([1, 1.5, 1]) 
        with col_input:
            codigo_existente = st.text_input(
                label="Código da Denúncia", 
                label_visibility="collapsed", 
                key="codigo_existent",
                placeholder=" Formato esperado (exemplo): 20260901-A12B34C5",
                max_chars=17,
            )
            
        with col_botao:
            padrao_valido = r"^[A-Z0-9]{8}-[A-Z0-9]{8}$"
            if st.session_state.codigo_existent:           
                if re.match(padrao_valido, st.session_state.codigo_existent):
                    botao_pesquisar = st.button("Buscar Denúncia")
                    
                    if botao_pesquisar:
                        codigo = codigo_existente
                        
                        df_denuncia_exist = CONFIG_DB.denuncia_read(database='denuncia_anonima',
                                                                  table='DENUNCIAS_PRIMARIO',
                                                                  codigo=codigo) 
                        
                        st.session_state.df_denuncia_existente = df_denuncia_exist
                        
                        
                        if not st.session_state.get('df_denuncia_existente').empty:
                            st.session_state.path_evid = config.criar_path_evidencias(codigo=st.session_state.codigo)    
                            st.session_state.tipo_acesso = 'existente' 
                            st.session_state.codigo = codigo
                            
                        st.rerun()
                else:
                    st.error("Formato ou codigo inválido!")
                    
        _, col_texto, col_botao_2 = col_input.columns([1, 1.5, 1],
                                                   vertical_alignment  ="bottom")        
        with col_texto:
            st.markdown("<p style='text-align: center; font-weight: bold; margin-bottom: 5px; margin-top: 30px;'>CASO QUEIRA FAZER UMA NOVA DENUNCIA:</p>",
                        unsafe_allow_html=True)
            
        with col_botao_2:
            botao_novo = col_botao_2.button("Nova Denuncia",
                                            type='primary')   
            if botao_novo:
                df_denuncia, denuncia, path_evid = config.nova_denuncia(categoria=None,
                                                                        conteudo=None,
                                                                        datetime=data,
                                                                        gravidade=None)
                st.session_state.codigo = denuncia
                st.session_state.df_denuncia = df_denuncia
                st.session_state.path_evid = path_evid
                st.session_state.codigo_in = True
                st.session_state.tipo_acesso = 'nova'
                st.rerun()
                         
                
else:
    main_page = st.Page("PAGINA_NOVADENUNCIA.py", title="Configurações", icon=":material/settings:")
    pagina_final = st.Page("PAGINA_FINAL.py")
    pagina_acompanhamento = st.Page("PAGINA_ACOMPANHAMENTO.py")
    pagina_acompanhamento_usu = st.Page("PAGINA_ACOMPANHAMENTO_USU.py")
    pagina_contas = st.Page("PAGINA_CONTAS.py")
    pagina_login = st.Page("PAGINA_LOGIN.py")

    if st.session_state.get("tipo_acesso") == 'nova':
        pg = st.navigation([main_page, pagina_final],
                        position="hidden")
    
    elif st.session_state.get("tipo_acesso") == 'existente':
        pg = st.navigation([pagina_acompanhamento,pagina_final],
                        position="hidden")
        
    elif st.session_state.get("tipo_acesso") == 'admin':
        pg = st.navigation([pagina_login,pagina_acompanhamento_usu,pagina_acompanhamento,pagina_contas,pagina_final],
                        position="hidden"
                           )
        with st.sidebar:
            st.page_link(pagina_acompanhamento_usu, label='Acompanhamento Denuncias')
            st.page_link(pagina_contas, label='Contas')
    pg.run() 
