import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import calendar
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

def grafico_2_runrate(total_orcado,
                      df_filt_gasto,
                      lista_cat_orcamentos):
    try:
        df_filt_gasto = df_filt_gasto[df_filt_gasto['COD_CATEGORIA'].isin(lista_cat_orcamentos)]
        df_area = df_filt_gasto.groupby('DATA_PAGAMENTO', as_index=False)['VALOR_PAGO'].sum()
        df_area = df_area.sort_values('DATA_PAGAMENTO')
        df_area['VALOR_ACUMULADO'] = df_area['VALOR_PAGO'].cumsum()
        df_area['DATA_STR'] = df_area['DATA_PAGAMENTO'].dt.strftime('%d/%m/%Y')

        fig_area = px.area(
            df_area,
            x='DATA_STR',
            y='VALOR_ACUMULADO',
            title="Evolução do Gasto Acumulado no Mês"
        )

        fig_area.update_traces(
            line_color='#115975', # Azul escuro semelhante ao teu gráfico de barras
            fillcolor='rgba(17, 89, 117, 0.15)', # Mesmo azul, mas quase transparente
            mode='lines+markers', # Adiciona pequenos pontos em cada dia
            marker=dict(size=6, color='#115975', line=dict(width=1, color='white')),
            hovertemplate="<b>%{x}</b><br>Gasto Acumulado: R$ %{y:,.2f}<extra></extra>"
        )

        fig_area.add_hline(
            y=total_orcado,
            line_dash="dash",
            line_color="#e74c3c", # Vermelho de alerta
            annotation_text=f"Limite do Orçamento: R$ {total_orcado:,.2f}",
            annotation_position="top left",
            annotation_font=dict(color="#e74c3c", size=12)
        )

        fig_area.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title=None,
            yaxis_title="Valor Acumulado (R$)",
            margin=dict(t=60, b=40, l=40, r=40),
            xaxis=dict(
                showgrid=False,
                type='category',
                categoryorder='array',
                categoryarray=df_area['DATA_STR'].tolist()
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#f0f2f6',
                zeroline=False
            )
        )
        return fig_area
    except:
        return None




def grafico_3_categoria_gasto(df_gasto_categoria,
                              ):
    
    try:
        figura_grafico_categoria = px.pie(
            df_gasto_categoria,
            values='VALOR_PAGO',
            names='DESCRICAO_SAIDAS',
            hole=0.55, # Aumentei um pouco o furo para um visual mais elegante
            title="Gasto por Categoria", # Título alinhado ao estilo do outro gráfico
            color_discrete_sequence=px.colors.sequential.Peach[2:]
        )

        figura_grafico_categoria.update_traces(
            textposition='inside',
            textinfo='percent',
            insidetextorientation='horizontal',
            textfont=dict(size=12, color='white'),
            marker=dict(line=dict(color='#FFFFFF', width=0.8)),
            hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Representação: %{percent}<extra></extra>"
        )

        figura_grafico_categoria.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=60, b=20, l=20, r=20),
            legend_title=None,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                font=dict(size=12)
            )
            )
        return figura_grafico_categoria
    except:
        return None


def grafico_4_orcamento_gasto(df_orcamento_gasto_categoria):
    
    try:
        figura_barras_orcamento = px.bar(
            df_orcamento_gasto_categoria,
                y='DESCRICAO_SAIDAS',
                x=['VALOR_ORCAMENTO', 'VALOR_PAGO'], # Orçamento primeiro para ficar no fundo!
                orientation='h',
                title='Orçamento vs Gasto',
                barmode='overlay', # <-- O SEGREDO: Coloca uma barra sobre a outra (sobreposição)
                text_auto=True,
                color_discrete_sequence=['#eb5c40', '#F20505']
        )

        figura_barras_orcamento.update_traces(
            texttemplate='R$ %{x:,.2f}', 
            textfont=dict(size=12, color='white'),
            marker_line_width=0
        )

        figura_barras_orcamento.data[0].update(
            textposition='inside',
            insidetextanchor='end',
            name='Orçamento'
        )

        figura_barras_orcamento.data[1].update(
            textposition='inside',
            insidetextanchor='start',
            name='Valor Gasto'
        )

        figura_barras_orcamento.update_layout(
            yaxis=dict(
                title=None,
                type='category',
            ),
            xaxis_title="Valor (R$)",
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridcolor='#e5e5e5',
                zeroline=True,
                zerolinecolor='#cccccc'
            ),
            legend_title=None,
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.05, 
                xanchor="right", 
                x=1
            ), 
            margin=dict(t=80, b=40, l=40, r=20)
        )
        return figura_barras_orcamento
    except:
        return None


def grafico_1_gastodia(df_gasto_dia,
                       paleta_de_cores):

    try:
        ### GRAFICO BARRAS GASTO/DIA ###
        fig_barras_dia_pag = px.bar(
            df_gasto_dia,
            x='DATA_PAGAMENTO',
            y='VALOR_PAGO',
            color='DESCRICAO_TIPO', 
            barmode='group', 
            title="Gasto por dia (Por Tipo)",
            text='VALOR_PAGO',
            color_discrete_sequence=paleta_de_cores
        )

        fig_barras_dia_pag.update_traces(
            textposition='outside',
            texttemplate='R$ %{text:,.2f}', 
            textfont=dict(size=12, color='black'),
            marker_line_width=0
        )

        fig_barras_dia_pag.update_layout(
            xaxis=dict(
                title=None,
                type='category', # Força a ser categoria
                categoryorder='array', # Avisa que a ordem virá de uma lista específica
                categoryarray=df_gasto_dia['DATA_PAGAMENTO'].unique() # Passa as datas na ordem do seu DF ordenado
            ),
            yaxis_title="Valor Gasto (R$)",
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(
                showgrid=True,
                gridcolor='#e5e5e5',
                zeroline=True,
                zerolinecolor='#cccccc'
            ),
            legend_title=None,
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.05, 
                xanchor="right", 
                x=1
            ), 
            margin=dict(t=80, b=40, l=40, r=20)
        )
        
        return fig_barras_dia_pag
    except:
        return None




@st.cache_data(ttl=300)
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
