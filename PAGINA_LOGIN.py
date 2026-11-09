import streamlit as st
from F_Conexao import iniciar_conexao
from F_ReadEditDB import ReadEditDB
from F_UserAutent import Authentication

# --- CONFIGURANDO O TUNEL SSH E A CONEXAO COM O BANCO DA VPS ---
engine = iniciar_conexao()
CONFIG_DB = ReadEditDB(engine=engine)


if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = ""
if 'tipo_usuario' not in st.session_state: 
    st.session_state.tipo_usuario = ""

if not st.session_state.autenticado:
    _, col_login, _ = st.columns([1, 1, 1])
    
    with col_login:
        st.title("🔐 Login")
        with st.form("form_login"):
            usuario_input = st.text_input("Codigo Usuário: ",
                                          type="default")
            senha_input = st.text_input("Senha: ", type="password")
            botao_entrar = st.form_submit_button("Entrar", type="primary", width="stretch")

        if botao_entrar:
            if not usuario_input or not senha_input:
                st.error("Preencha o email e a senha para continuar.")
            else:
                try:
                    df = CONFIG_DB.usuarios_read_login(database='financeiro',
                                                table='USERS',
                                                 usuario = usuario_input
                                                 )
                    resultado = Authentication.compara_senha(df_banco=df,
                                                          senha=senha_input)
                    if resultado["valido"]:
                        st.session_state.autenticado = True
                        st.session_state.usuario_logado = usuario_input
                        st.session_state.tipo_usuario = resultado["tipo"]
                        st.rerun()
                    else:
                        st.error("Usuário ou senha inválidos.")

                except Exception as e:
                    st.error(f"Erro ao autenticar: {e}")

else:
    st.switch_page("PAGINA_ACOMPANHAMENTO_USU.py")
