import streamlit as st
from F_Conexao import iniciar_conexao
from F_ReadEditDB import ReadEditDB
from F_UserAutent import Authentication
from dotenv import load_dotenv
from elements import carregar_imagem_local


# --- CONFIGURANDO O TUNEL SSH E A CONEXAO COM O BANCO DA VPS ---
engine = iniciar_conexao()
CONFIG_DB = ReadEditDB(engine=engine)

load_dotenv(override=True)


st.set_page_config(
layout = 'wide'

)

logo_completo = r'C:\Users\Higor Rodrigues\Desktop\PROJETOS\FINANCEIRO_PAINEL\toxeira-house-financeiro\assets\logo\Sem título.png'
logo_b64 = carregar_imagem_local(logo_completo)
paleta_de_cores = ['#054159', '#45A9BF', '#F2790F', '#F20505', '#eb5c40']

html_cabecalho_2 = f"""
<div style="text-align: left; margin-top: 35px; margin-bottom: 30px; font-family: sans-serif;">    
    <img src="data:image/png;base64,{logo_b64}" width="400" stylie="margin-bottom: 10px;">
</div>
"""

st.markdown("""
    <style>
        /* CSS Mágico para Containers Específicos */
        div[class*="stForm "] {
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





if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario_logado' not in st.session_state:
    st.session_state.usuario_logado = ""
if 'tipo_usuario' not in st.session_state: 
    st.session_state.tipo_usuario = ""

container_principal = st.container(
                                   gap='xxsmall',
                                   wrap=True,
                                   )


with container_principal:
    linha_1 = st.columns([1,1])
    _,_,logo,col_login,_,_ = st.columns([1,1,3,3,1,1], vertical_alignment='center')

    if not st.session_state.autenticado:    
        with logo:
            st.html(html_cabecalho_2)
        with col_login:
            with st.form(key = "login_form"):
                st.title(":material/login: Login")
                usuario_input = st.text_input("Codigo Usuário: ",
                                            type="default")
                senha_input = st.text_input("Senha: ", type="password")
                botao_entrar = st.form_submit_button("Entrar", type="primary", width="stretch", key='botao_login')

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
                            print(st.session_state.tipo_usuario)
                            st.rerun()
                            
                        else:
                            st.error("Usuário ou senha inválidos.")

                    except Exception as e:
                        st.error(f"Erro ao autenticar: {e}")
                    

    else:
        main_page = st.Page("PAGINA_NOVADENUNCIA.py", title="Lançamentos")
        pagina_contas = st.Page("PAGINA_CONTAS.py")
        pagina_login = st.Page("PAGINA_LOGIN.py")
        pagina_dashboard = st.Page("PAGINA_DASHBOARD.py")
 
        if st.session_state.get("tipo_usuario") == 'admin':
           
            pg = st.navigation([main_page, pagina_contas, pagina_dashboard],
                            position="hidden"
                            )
            with st.sidebar:
                st.page_link(main_page, label=':material/paid: Novos Lançamentos')
                st.page_link(pagina_dashboard, label=':material/dashboard: Dashboard')
                st.page_link(pagina_contas, label=':material/person: Contas')
                
                if st.button("Sair", use_container_width=True):
                    st.session_state.autenticado = False
                    st.session_state.usuario_logado = ""
                    st.session_state.tipo_usuario = ""
                    st.rerun()
            
        pg.run()

