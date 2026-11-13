import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from F_Conexao import iniciar_conexao
from F_ReadEditDB import ReadEditDB
from F_UserAutent import Authentication
from elements import carregar_imagem_local


load_dotenv(override=True)

if not st.session_state.get("autenticado", False):
    st.error("⛔ Acesso negado. Você precisa estar autenticado.")
    st.stop()


# --- CONFIGURANDO O TUNEL SSH E A CONEXAO COM O BANCO DA VPS ---
st.session_state.usuario_logado = 1
hoje = datetime.now()
logo_completo = r'C:\Users\Higor Rodrigues\Desktop\PROJETOS\FINANCEIRO_PAINEL\toxeira-house-financeiro\assets\logo\Sem título.png'
logo_b64 = carregar_imagem_local(logo_completo)

html_cabecalho_2 = f"""
<div style="text-align: center; margin-top: 35px; margin-bottom: 30px; font-family: sans-serif;">    
    <img src="data:image/png;base64,{logo_b64}" width="400" stylie="margin-bottom: 10px;">
</div>
"""

st.markdown("""
    <style>
        /* CSS Mágico para Containers Específicos */
        div[class*="key-principal"] {
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


engine = iniciar_conexao()
try:
    CONFIG_DB = ReadEditDB(engine=engine)
except Exception as e:
    st.error(f"Erro ao conectar ao servidor:{e}")


st.sidebar.markdown(f'''Usuario Logado:
                    **{CONFIG_DB.usuarios_read_login(database='financeiro',
                                                         table='USERS',
                                                         usuario=st.session_state.get("usuario_logado")
                                                         )['NOME'].iloc[0]}**''')



_,titulo,_ = st.columns([1,4,1])
titulo.html(html_cabecalho_2)

container_config = titulo.container(border = True,
                                    horizontal = True,
                                    key='principal')

aba_cadastros_atuais , aba_cadastro  = container_config.tabs(['📄 Cadastros Atuais','🔑 Novo Cadastro'])


with aba_cadastros_atuais:    
    try:                    
        df_cadastros_atuais = CONFIG_DB.usuarios_read(database='financeiro',
                                                      table='USERS',
                                                      )
        
        colunas = st.columns([2.3,2.3,1,1,1,1.25], vertical_alignment="bottom")

        with colunas[0]:
                email_filtro = st.selectbox(
                label = "**Codigo Usuario:**",
                # label_visibility="collapsed",
                index = None,
                placeholder = "Sel. o codigo",
                options = df_cadastros_atuais['COD_USUARIO']
                )
        
        with colunas[1]:
                usuario_filtro = st.selectbox(
                label = "Usuario",
                # label_visibility="collapsed",
                index = None,
                placeholder = "Sel. o usuario",
                options = df_cadastros_atuais['NOME']
                )
        
        with colunas[-1]:
            botao_cadastrar = st.button(label = "ALTERAR SENHA",
                                    type='primary',
                                    key='botao_novasenha')
            if botao_cadastrar:
                CONFIG_DB.mudar_senha()
        
        if email_filtro:
            df_cadastros_atuais = df_cadastros_atuais[df_cadastros_atuais['COD_USUARIO']==email_filtro]
        
        if usuario_filtro:
            df_cadastros_atuais = df_cadastros_atuais[df_cadastros_atuais['NOME']==usuario_filtro]
                
        
        df_exibir = st.dataframe(df_cadastros_atuais[['COD_USUARIO','NOME',
                                                      'TIPO']],
                                                     hide_index = True)        
    except Exception as e:        
        st.error(f"Erro ao procurar os usuários atuais:{e}")
    
with aba_cadastro:
    colunas = st.columns([1,1], vertical_alignment="top")
    
    with colunas[0]:
        usuario = st.text_input(label="Usuario:",
                                type="default",
                                placeholder = "Sera usado para logar",
                                key= 'usuario_cadastrar' )
        
        
    with colunas[1]:
        senha = st.text_input(label="Senha:",
                              type="password",
                              placeholder = "Digite a Senha",
                              key= "senha_cadastrar")
        
        confirma_senha = st.text_input(label="Confirmação de senha:",
                                       type="password",
                                       placeholder = "Digite a Senha",
                                       key='confirma_senha')  
    divisoes = aba_cadastro.columns([4.1,1,1,2], 
                                    vertical_alignment="bottom")
    with divisoes[0]:
        if senha and confirma_senha:
            if senha != confirma_senha:
                st.error("Senhas não conferem")
                
    with divisoes[1]:
        tipo = st.selectbox(
            label = "Tipo: ",
            index = None,
            placeholder = "Tipo Usuario",
            options = ['admin','geral'])   
    

    with divisoes[3]:
        status_botao = True
        df_cadastrar = pd.DataFrame()
        if senha and tipo and usuario:
            if senha == confirma_senha:  
                status_botao = False
                try:
                    df_cadastrar = Authentication.create_account(user_name=usuario,
                                                                 password =senha,
                                                                 type=tipo,
                                                                 )
                except Exception:
                    st.error("Erro ao gerar o DF cadastro")
        if df_cadastrar.empty:
            status_botao = True
        botao_cadastrar = st.button(label = "CADASTRAR",
                                    type='primary',
                                    key='botao_farma',
                                    disabled=status_botao,
                                    on_click=CONFIG_DB.upload_user_df,
                                    kwargs={"df": df_cadastrar, 
                                            "table": "USERS",
                                            "database": "financeiro"})
        time.sleep(1)
        del st.session_state['senha_cadastrar']
        del st.session_state['confirma_senha']
        del st.session_state['usuario_cadastrar']
