import streamlit as st
import pandas as pd
import base64
import zipfile
import io
import os


def metricas_gerar(position,
                   value,
                   label,
                   delta):

    
    try:
        metric = position.metric(
                value=value,
                label=label,
                border=True,
                delta=delta,
                delta_color ='off',

    )
        return metric
    except Exception as e:
        st.info(f'Erro para gerar metrica: {e}')
        return None


@st.cache_data
def gerar_respostas_container (df,
                               ):
    if not df.empty:
        df = df.sort_values(by=['INDICE'], ascending=True)
    else:
        return None 
    
    try:
        for index, linha in df.iterrows():
            data = linha['DATA_RESPOSTA'].strftime('%d/%m/%Y %H:%M:%S')
            usuario = linha['NOME']
            cod_usu = linha['COD_USU']
            resposta = linha['RESPOSTA']
            indice = index+1
            
            if cod_usu == 2:
                st.markdown(f'{data} **{usuario}:**')
                container_texto = st.container(border=True,
                                               key=f'userden_{indice}')
                container_texto.text(resposta)
            
            else:
                st.markdown(f'{data} **{usuario}:**')
                container_texto = st.container(border=True,
                                               key=f'userresp_{indice}')
                container_texto.text(resposta)
                
    except Exception as e:
        print(f'Erro no tratamento; {e}')    


def download_evidencias (path,
                         position,
                         codigo
                         ):
    if os.path.exists(path):
        arquivos = os.listdir(path)
        if arquivos:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as ziper:
                for arquivo in arquivos:
                    caminho_completo = os.path.join(path, arquivo)
                    ziper.write(caminho_completo, arcname=arquivo)
            
            zip_buffer.seek(0)
            position.download_button(
                            label="Download evidencias",
                            data=zip_buffer,
                            file_name=f"EVD_{codigo}.zip",
                            mime="application/zip",
                            key=f'download_evidencias',
                            type="primary",
                        )   
        else:
            st.error("Não existem evidencias para baixar")
    
    else:
        st.error("Não existem evidencias para baixar")


def html_badge(valor, position):
    try:
        html_badge_data = f"""
            <div style="
                background-color: #f0f2f6; 
                border-radius: 5px; 
                padding: 8px 12px; 
                color: #8c8c8c; 
                font-size: 14px;
                text-align: center;
            ">
            {valor}
            </div>
            """   
        badge = position.markdown(html_badge_data, unsafe_allow_html=True)
        
        return badge
    except Exception as e:
        return position.error(e, unsafe_allow_html=True)

def carregar_imagem_local(caminho):
    with open(caminho, "rb") as arquivo:
        return base64.b64encode(arquivo.read()).decode('utf-8')
    
def gerar_html_impressao(df, titulo="Contagem"):
    df_print = df.copy()
    df_print = df_print.astype(str).replace('<NA>', '')
    # Converte o DataFrame do Pandas para tabelas HTML
    tabela_html = df_print.to_html(index=False, border=0, classes="tabela-a4", na_rep=" ")
    
    
    # Monta a estrutura da página com CSS focado em impressão
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
        <style>
            /* Configuração do tamanho A4 para a impressora */
            @page {{
                size: A4;
                margin: 15mm;
            }}
            body {{
                font-family: Arial, sans-serif;
                color: #333;
            }}
            h2 {{
                text-align: center;
                color: #122335;
            }}
            /* Estilizando a tabela para ficar com visual corporativo */
            .tabela-a4 {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
            }}
            .tabela-a4 th, .tabela-a4 td {{
                border: 1px solid #ddd;
                padding: 6px;
                text-align: left;
            }}
            .tabela-a4 th {{
                background-color: #2a8b75;
                color: white;
            }}
            /* Faz com que o cabeçalho da tabela repita se tiver mais de uma página */
            thead {{ display: table-header-group; }}
            tfoot {{ display: table-row-group; }}
            tr {{ page-break-inside: avoid; }}
        </style>
    </head>
    <!-- O onload="window.print()" abre a tela de impressão automaticamente! -->
    <body onload="window.print()">
        <h2>{titulo}</h2>
        <p><strong>Data de Emissão:</strong> {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}</p>
        <hr>
        {tabela_html}
    </body>
    </html>
    """
    return html_template

def limpar_conteudo_config (key_nome,
                            key_uploader):
    if key_nome in st.session_state:
        st.session_state[key_nome] = ""
        
    # Usa colchetes para acessar a chave "uploader_config"
    if key_uploader in st.session_state:
        del st.session_state[key_uploader]

    

def formato_moeda (valor:float):
    valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor_formatado

def card_informativo (linha:list,
                      posicao_lista:int):
    card = linha[posicao_lista].container(height=100,
                                          border=True,
                                          horizontal_alignment='center')
    return card


def config_card (titulo_card:str,
                 card,
                 valor_card:str,
                 altura:int):

    card.markdown(titulo_card, unsafe_allow_html=True)
    if valor_card!=None:
        card.markdown(valor_card,
                      text_alignment='center',
                      width=altura,
                      unsafe_allow_html=True)
